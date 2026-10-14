"""Local FLUX.2 klein 4B/9B inference with one active model at a time."""
import gc
import os
import threading
import time

os.environ.setdefault("HF_DEACTIVATE_ASYNC_LOAD", "1")
os.environ.setdefault("PYTORCH_ALLOC_CONF", "expandable_segments:True")

from model_config import MODELS


class Cancelled(Exception):
    pass


class Engine:
    def __init__(self):
        self.pipe = None
        self.active_model = None
        self.device = os.getenv("KLEIN_DEVICE", "cuda:0")
        self.memory_budget_gib = float(os.getenv("KLEIN_MEMORY_BUDGET_GIB", "7.0"))
        self.lock = threading.Lock()

    def load(self, model_key, progress):
        if model_key not in MODELS:
            raise ValueError(f"未対応のモデルです: {model_key}")
        if self.pipe is not None and self.active_model == model_key:
            return
        if self.pipe is not None:
            progress("switching", 0, "モデルを切り替えるため、現在のモデルを解放しています")
            self.unload()

        import torch
        from diffusers import Flux2KleinPipeline, Flux2Transformer2DModel, GGUFQuantizationConfig
        from transformers import BitsAndBytesConfig, Qwen3ForCausalLM

        config = MODELS[model_key]
        gguf_path = config["gguf_dir"] / config["gguf_file"]
        if not torch.cuda.is_available():
            raise RuntimeError("CUDA対応GPUが見つかりません。NVIDIA GPUとドライバーを確認してください。")
        if not gguf_path.is_file():
            raise RuntimeError(f"{config['name']}が未準備です。download_models.py を実行してください。")
        torch.cuda.set_device(self.device)
        total = torch.cuda.get_device_properties(self.device).total_memory
        torch.cuda.set_per_process_memory_fraction(min(self.memory_budget_gib * 2**30 / total, 0.95), self.device)
        dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
        progress("loading", 0, f"{config['name']}を読み込んでいます")
        try:
            text_encoder = Qwen3ForCausalLM.from_pretrained(
                config["model_dir"] / "text_encoder", local_files_only=True,
                dtype=dtype,
                quantization_config=BitsAndBytesConfig(
                    load_in_4bit=True, bnb_4bit_quant_type="nf4",
                    bnb_4bit_compute_dtype=dtype, bnb_4bit_use_double_quant=True,
                ),
                device_map={"": self.device},
            )
            text_encoder.to("cpu")
            gc.collect()
            torch.cuda.empty_cache()
            transformer = Flux2Transformer2DModel.from_single_file(
                str(gguf_path), config=str(config["model_dir"]), subfolder="transformer",
                local_files_only=True, torch_dtype=dtype,
                quantization_config=GGUFQuantizationConfig(compute_dtype=dtype),
            )
            pipe = Flux2KleinPipeline.from_pretrained(
                config["model_dir"], transformer=transformer, text_encoder=text_encoder,
                torch_dtype=dtype, local_files_only=True,
            )
            pipe.vae.enable_tiling()
            pipe.enable_model_cpu_offload(device=self.device)
        except Exception:
            self.pipe = None
            self.active_model = None
            gc.collect()
            torch.cuda.empty_cache()
            raise
        self.pipe = pipe
        self.active_model = model_key

    def generate(self, model_key, prompt, reference, width, height, seed, progress, cancel):
        import torch
        started = time.monotonic()
        if torch.cuda.is_available():
            torch.cuda.set_device(self.device)
            torch.cuda.reset_peak_memory_stats(self.device)
        self.load(model_key, progress)
        if cancel.is_set():
            raise Cancelled()
        progress("encoding", 0, "プロンプトと参照画像を読み取っています")

        def on_step(pipe, step, timestep, kwargs):
            if cancel.is_set():
                raise Cancelled()
            progress("generating", step + 1, f"生成中 {step + 1} / 4")
            return kwargs

        generation_start = time.monotonic()
        with torch.inference_mode():
            result = self.pipe(
                image=reference, prompt=prompt, width=width, height=height,
                num_inference_steps=4, guidance_scale=1.0,
                generator=torch.Generator("cpu").manual_seed(seed),
                max_sequence_length=512, callback_on_step_end=on_step,
            ).images[0]
        torch.cuda.synchronize(self.device)
        return result, {
            "model": model_key,
            "model_name": MODELS[model_key]["name"],
            "seconds": round(time.monotonic() - generation_start, 2),
            "total_seconds": round(time.monotonic() - started, 2),
            "peak_allocated_gib": round(torch.cuda.max_memory_allocated(self.device) / 2**30, 3),
            "peak_reserved_gib": round(torch.cuda.max_memory_reserved(self.device) / 2**30, 3),
            "allocator_budget_gib": self.memory_budget_gib,
            "gpu": torch.cuda.get_device_name(self.device),
            "steps": 4,
        }

    def unload(self):
        if self.pipe is not None:
            self.pipe.remove_all_hooks()
            self.pipe = None
        self.active_model = None
        gc.collect()
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

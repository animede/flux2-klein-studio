from pathlib import Path

ROOT = Path(__file__).resolve().parent

MODELS = {
    "4b": {
        "name": "FLUX.2 klein 4B",
        "description": "軽量・商用利用向け",
        "license": "Apache-2.0",
        "model_dir": ROOT / "models" / "klein-4b",
        "gguf_dir": ROOT / "models" / "gguf",
        "base_repo": "black-forest-labs/FLUX.2-klein-4B",
        "base_revision": "e7b7dc27f91deacad38e78976d1f2b499d76a294",
        "gguf_repo": "unsloth/FLUX.2-klein-4B-GGUF",
        "gguf_revision": "0084d1df98e2e2137fe776d55170bc4792ec1d66",
        "gguf_file": "flux-2-klein-4b-Q4_K_M.gguf",
        "quantization": "GGUF Q4_K_M",
        "reference_pixel_budget": 4 * 768**2,
    },
    "9b": {
        "name": "FLUX.2 klein 9B",
        "description": "高品質・非商用・非本番",
        "license": "FLUX Non-Commercial License v2.1",
        "model_dir": ROOT / "models" / "klein-9b",
        "gguf_dir": ROOT / "models" / "gguf",
        "base_repo": "black-forest-labs/FLUX.2-klein-9B",
        "base_revision": "92196c8e11f7b6cf2b7493e037d8c5345c559216",
        "gguf_repo": "unsloth/FLUX.2-klein-9B-GGUF",
        "gguf_revision": "fde8634245fe6b749a221c25b34672b5b8fbd079",
        "gguf_file": "flux-2-klein-9b-Q3_K_M.gguf",
        "quantization": "GGUF Q3_K_M",
        "reference_pixel_budget": 2 * 768**2,
    },
}

DEFAULT_MODEL = "4b"

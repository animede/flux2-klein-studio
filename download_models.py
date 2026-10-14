"""Download one or both selectable models with pinned revisions."""
import argparse
from concurrent.futures import ThreadPoolExecutor

from huggingface_hub import hf_hub_download, snapshot_download

from model_config import MODELS


def download_model(config):
    snapshot_download(
        config["base_repo"], revision=config["base_revision"], local_dir=config["model_dir"],
        allow_patterns=["model_index.json", "scheduler/*", "tokenizer/*", "text_encoder/*",
                        "vae/*", "transformer/config.json", "LICENSE*"],
        max_workers=3,
    )
    return hf_hub_download(
        config["gguf_repo"], config["gguf_file"], revision=config["gguf_revision"],
        local_dir=config["gguf_dir"],
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("model", nargs="?", default="all", choices=["all", *MODELS])
    args = parser.parse_args()
    selected = list(MODELS.values()) if args.model == "all" else [MODELS[args.model]]
    with ThreadPoolExecutor(max_workers=len(selected)) as pool:
        for result in pool.map(download_model, selected):
            print(result, flush=True)
    print(f"Model download complete: {args.model}", flush=True)

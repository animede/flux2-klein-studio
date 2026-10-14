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
    parser = argparse.ArgumentParser(
        description="Download pinned FLUX.2 klein support files and GGUF weights."
    )
    parser.add_argument("model", nargs="?", default="all", choices=["all", *MODELS])
    parser.add_argument(
        "--acknowledge-9b-license",
        action="store_true",
        help=(
            "Confirm that you reviewed and accepted the FLUX Non-Commercial "
            "License v2.1 and Usage Policy. Required for 9B downloads."
        ),
    )
    args = parser.parse_args()
    if args.model in {"all", "9b"} and not args.acknowledge_9b_license:
        parser.error(
            "9B is licensed for non-commercial, non-production use and has "
            "additional conditions. Review https://huggingface.co/black-forest-labs/"
            "FLUX.2-klein-9B and THIRD_PARTY_NOTICES.md, accept the official "
            "Hugging Face access terms, then rerun with --acknowledge-9b-license."
        )
    selected = list(MODELS.values()) if args.model == "all" else [MODELS[args.model]]
    with ThreadPoolExecutor(max_workers=len(selected)) as pool:
        for result in pool.map(download_model, selected):
            print(result, flush=True)
    print(f"Model download complete: {args.model}", flush=True)

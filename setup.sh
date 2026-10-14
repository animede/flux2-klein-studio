#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
model_choice="${1:-4b}"
if [[ "$model_choice" != "all" && "$model_choice" != "4b" && "$model_choice" != "9b" && "$model_choice" != "none" ]]; then
  echo "Usage: ./setup.sh [all|4b|9b|none] [--acknowledge-9b-license]" >&2
  exit 2
fi
# Remove development-machine links if this folder was copied to another PC.
for path in .venv models/klein-4b models/gguf/flux-2-klein-4b-Q4_K_M.gguf; do
  if [[ -L "$path" && ! -e "$path" ]]; then
    rm "$path"
  fi
done
if [[ ! -x .venv/bin/python ]]; then
  python3.12 -m venv .venv
fi
.venv/bin/python -m pip install -r requirements.txt
if [[ "$model_choice" != "none" ]]; then
  .venv/bin/python download_models.py "$model_choice" "${@:2}"
fi

#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export TOKENIZERS_PARALLELISM=false
export HF_HUB_DISABLE_TELEMETRY=1
exec .venv/bin/python -m uvicorn app:app --host "${KLEIN_HOST:-127.0.0.1}" --port "${KLEIN_PORT:-7864}" --workers 1

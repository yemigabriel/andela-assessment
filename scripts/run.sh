#!/usr/bin/env bash
set -euo pipefail

UV_CACHE_DIR=.uv-cache uv run uvicorn backend.main:app --host 0.0.0.0 --port 8000

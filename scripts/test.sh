#!/usr/bin/env bash
set -euo pipefail

PYTHONPATH=. UV_PROJECT_ENVIRONMENT=.venv-backend UV_CACHE_DIR=.uv-cache uv run --group dev pytest tests

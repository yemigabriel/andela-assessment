#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST_DIR="$ROOT_DIR/dist"
BUILD_DIR="$DIST_DIR/lambda"
ZIP_PATH="$DIST_DIR/backend.zip"

rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"
mkdir -p "$DIST_DIR"

UV_CACHE_DIR="$ROOT_DIR/.uv-cache" uv pip install \
  --python "$(command -v python3)" \
  --python-version 3.12 \
  --python-platform x86_64-manylinux2014 \
  --only-binary :all: \
  --target "$BUILD_DIR" \
  -r "$ROOT_DIR/requirements.txt"
cp -R "$ROOT_DIR/backend" "$BUILD_DIR/backend"

cd "$BUILD_DIR"
zip -rq "$ZIP_PATH" .

cd "$ROOT_DIR/infra"
terraform init
terraform apply

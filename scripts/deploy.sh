#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST_DIR="$ROOT_DIR/dist"
BUILD_DIR="$DIST_DIR/lambda"
ZIP_PATH="$DIST_DIR/backend.zip"
TF_STATE_KEY="${TF_STATE_KEY:-meridian-support/terraform.tfstate}"

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
if [[ -n "${TF_STATE_BUCKET:-}" && -n "${TF_STATE_LOCK_TABLE:-}" ]]; then
  terraform init -reconfigure \
    -backend-config="bucket=${TF_STATE_BUCKET}" \
    -backend-config="key=${TF_STATE_KEY}" \
    -backend-config="region=${AWS_REGION:-eu-west-1}" \
    -backend-config="dynamodb_table=${TF_STATE_LOCK_TABLE}"
else
  terraform init
fi

if [[ "${CI:-}" == "true" ]]; then
  terraform apply -auto-approve
else
  terraform apply
fi

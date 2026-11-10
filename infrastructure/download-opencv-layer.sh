#!/usr/bin/env bash
set -euo pipefail

# Script to download OpenCV layer from GitHub releases
# Expects GH_TOKEN and GH_REPO environment variables to be set
# Expects RUNNER_TEMP to be available (GitHub Actions)

if [[ -z "${GH_TOKEN:-}" ]]; then
  echo "::error::GH_TOKEN environment variable is required"
  exit 1
fi

if [[ -z "${GH_REPO:-}" ]]; then
  echo "::error::GH_REPO environment variable is required"
  exit 1
fi

if [[ -z "${RUNNER_TEMP:-}" ]]; then
  echo "::error::RUNNER_TEMP environment variable is required"
  exit 1
fi

tag=$(bash infrastructure/layer-release-tag.sh opencv)
bash infrastructure/wait-for-opencv-release.sh "$tag"
echo "Downloading OpenCV layer from $tag"

download_dir="$RUNNER_TEMP/native-layers/opencv"
if ! gh release download "$tag" --dir "$download_dir" \
  --pattern opencv-layer.zip --pattern SHA256SUMS; then
  echo "::error::Unable to download OpenCV layer. Run publish-opencv-layer.yml for this commit and wait for it to succeed before deploying."
  exit 1
fi

(cd "$download_dir" && sha256sum --check SHA256SUMS)
mkdir -p infrastructure/opencv/build
mv "$download_dir/opencv-layer.zip" infrastructure/opencv/build/

#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IMAGE="crossword-solver-opencv-layer"
OUTPUT_DIR="${SCRIPT_DIR}/build"
OUTPUT_ZIP="${OUTPUT_DIR}/opencv-layer.zip"

rm -rf "${OUTPUT_DIR}"
mkdir -p "${OUTPUT_DIR}"

CONTAINER_ID=$(docker create \
  --platform linux/amd64 \
  "${IMAGE}")

docker cp "${CONTAINER_ID}:/opt/." "${OUTPUT_DIR}/opt"

docker rm "${CONTAINER_ID}" >/dev/null

cd "${OUTPUT_DIR}/opt"

# -y keeps symlinks as links; Lambda extracts layers to /opt so paths must not start with opt/.
zip -ry "${OUTPUT_ZIP}" . >/dev/null

cd "${OUTPUT_DIR}"
rm -rf opt

echo "Created ${OUTPUT_ZIP}"
ls -lh "${OUTPUT_ZIP}"
#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

IMAGE="crossword-solver-tesseract-layer"
OUTPUT_DIR="${SCRIPT_DIR}/build"
OUTPUT_ZIP="${OUTPUT_DIR}/tesseract-layer.zip"

rm -rf "${OUTPUT_DIR}"
mkdir -p "${OUTPUT_DIR}/layer/bin"
mkdir -p "${OUTPUT_DIR}/layer/lib"
mkdir -p "${OUTPUT_DIR}/layer/share/tessdata"

docker build \
  --platform linux/amd64 \
  -t "${IMAGE}" \
  "${SCRIPT_DIR}"

CONTAINER_ID=$(docker create --platform linux/amd64 "${IMAGE}")

trap 'docker rm "${CONTAINER_ID}" >/dev/null' EXIT

docker cp \
  "${CONTAINER_ID}:/opt/bin/tesseract" \
  "${OUTPUT_DIR}/layer/bin/tesseract"

docker cp \
  "${CONTAINER_ID}:/opt/lib/libtesseract.so.5.0.5" \
  "${OUTPUT_DIR}/layer/lib/"

docker cp \
  "${CONTAINER_ID}:/opt/lib/libleptonica.so.6.0.0" \
  "${OUTPUT_DIR}/layer/lib/"

for lib in libjpeg.so.62 libpng16.so.16 libtiff.so.5 libjbig.so.2.1 libwebp.so.7 libgomp.so.1; do
  docker cp "${CONTAINER_ID}:/opt/lib/${lib}" "${OUTPUT_DIR}/layer/lib/"
done

ln -s libtesseract.so.5.0.5 \
  "${OUTPUT_DIR}/layer/lib/libtesseract.so.5"

ln -s libleptonica.so.6.0.0 \
  "${OUTPUT_DIR}/layer/lib/libleptonica.so.6"

docker cp \
  "${CONTAINER_ID}:/opt/share/tessdata/eng.traineddata" \
  "${OUTPUT_DIR}/layer/share/tessdata/eng.traineddata"

cd "${OUTPUT_DIR}/layer"

zip -ry "${OUTPUT_ZIP}" .
rm -rf "${OUTPUT_DIR}/layer"

echo "Created ${OUTPUT_ZIP}"
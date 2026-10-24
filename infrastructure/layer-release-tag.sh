#!/usr/bin/env bash

set -euo pipefail

if [[ $# -ne 1 || ( "$1" != "opencv" && "$1" != "tesseract" ) ]]; then
  echo "Usage: $0 <opencv|tesseract>" >&2
  exit 2
fi

LAYER="$1"
REPO_ROOT="$(git -C "$(dirname "${BASH_SOURCE[0]}")" rev-parse --show-toplevel)"

# Use committed inputs so application-only commits reuse the same layer release.
INPUT_HASH="$(git -C "${REPO_ROOT}" ls-tree -r HEAD -- \
  "infrastructure/${LAYER}" \
  infrastructure/layer-release-tag.sh \
  ".github/workflows/publish-${LAYER}-layer.yml" | git hash-object --stdin)"

printf '%s-layer-%s\n' "${LAYER}" "${INPUT_HASH}"

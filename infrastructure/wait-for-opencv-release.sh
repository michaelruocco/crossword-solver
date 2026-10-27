#!/usr/bin/env bash

set -euo pipefail

if [[ $# -ne 1 || ! "$1" =~ ^opencv-layer-[0-9a-f]{40}$ ]]; then
  echo "Usage: $0 opencv-layer-<hash>" >&2
  exit 2
fi

: "${GH_REPO:?GH_REPO must identify the repository}"
TAG="$1"
DEADLINE=$((SECONDS + 7200))
RESPONSE="$(mktemp)"
ERROR="$(mktemp)"
trap 'rm -f "$RESPONSE" "$ERROR"' EXIT

while true; do
  if gh api --include "repos/$GH_REPO/releases/tags/$TAG" \
    --jq '(.draft == false) and ([.assets[] | select(.state == "uploaded") | .name] | (index("opencv-layer.zip") != null and index("SHA256SUMS") != null))' \
    > "$RESPONSE" 2> "$ERROR"; then
    if [[ "$(tail -n 1 "$RESPONSE")" == "true" ]]; then
      echo "OpenCV release $TAG is ready."
      exit 0
    fi
  elif ! grep -Eq '^HTTP/[^ ]+ 404([[:space:]]|$)' "$RESPONSE"; then
    cat "$ERROR" >&2
    echo "::error::Failed to query OpenCV release $TAG." >&2
    exit 1
  fi

  if (( SECONDS >= DEADLINE )); then
    echo "::error::Timed out waiting for $TAG and its assets. Check publish-opencv-layer.yml, publish this commit's layer, then retry deployment." >&2
    exit 1
  fi
  echo "Waiting for OpenCV release $TAG and both uploaded assets..."
  sleep 30
done

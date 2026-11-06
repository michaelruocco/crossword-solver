#!/usr/bin/env bash

set -euo pipefail

: "${TF_VAR_environment:?TF_VAR_environment must identify the environment to destroy}"
: "${TF_STATE_BUCKET:?TF_STATE_BUCKET must identify the protected state bucket}"

if [[ ! "$TF_VAR_environment" =~ ^[a-z][a-z0-9-]*$ ]]; then
  echo "Invalid environment name: $TF_VAR_environment" >&2
  exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK_DIR="$(mktemp -d)"
trap 'rm -rf "$WORK_DIR"' EXIT

terraform -chdir="$SCRIPT_DIR/terraform" show -json destroy.tfplan > "$WORK_DIR/plan.json"
account_id=$(aws sts get-caller-identity --query Account --output text)
jq -r '.resource_changes[]? | select(.type == "aws_s3_bucket" and (.change.actions | index("delete"))) | .change.before.bucket' \
  "$WORK_DIR/plan.json" > "$WORK_DIR/buckets.txt"

while IFS= read -r bucket; do
  case "$bucket" in
    "crossword-solver-$TF_VAR_environment-puzzle-images"|"crossword-solver-$TF_VAR_environment-lambda-layers"|"crossword-solver-$TF_VAR_environment-ui-$account_id") ;;
    *) echo "::error::Refusing to empty unexpected bucket $bucket" >&2; exit 1 ;;
  esac
  if [[ "$bucket" == "$TF_STATE_BUCKET" ]]; then
    echo "::error::Refusing to empty the Terraform state bucket." >&2
    exit 1
  fi
done < "$WORK_DIR/buckets.txt"

while IFS= read -r bucket; do
  echo "Emptying application bucket $bucket"
  aws s3 rm "s3://$bucket" --recursive --only-show-errors
  while true; do
    aws s3api list-object-versions --bucket "$bucket" --max-keys 1000 --no-paginate \
      > "$WORK_DIR/versions.json"
    jq '{Objects: ([.Versions[]?, .DeleteMarkers[]?] | map({Key, VersionId})), Quiet: true}' \
      "$WORK_DIR/versions.json" > "$WORK_DIR/deletions.json"
    count=$(jq '.Objects | length' "$WORK_DIR/deletions.json")
    if [[ "$count" == 0 ]]; then break; fi
    aws s3api delete-objects --bucket "$bucket" \
      --delete "file://$WORK_DIR/deletions.json" > "$WORK_DIR/delete-result.json"
    if ! jq -e '(.Errors // []) | length == 0' "$WORK_DIR/delete-result.json" > /dev/null; then
      echo "::error::S3 could not delete all versions from $bucket. Per-object failures:" >&2
      jq '.Errors[]? | {Key, VersionId, Code, Message}' "$WORK_DIR/delete-result.json" >&2
      exit 1
    fi
  done
done < "$WORK_DIR/buckets.txt"
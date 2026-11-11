#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$SCRIPT_DIR/terraform"

if [[ ! "${TF_VAR_environment:-}" =~ ^[a-z][a-z0-9-]*$ ]]; then
  echo "::error::Set TF_VAR_environment to a valid environment name before emptying buckets." >&2
  exit 1
fi

if [[ -z "${TF_STATE_BUCKET:-}" ]]; then
  echo "::error::Set TF_STATE_BUCKET before emptying application buckets." >&2
  exit 1
fi

plan_json="$(terraform -chdir="$TERRAFORM_DIR" show -json destroy.tfplan)"
planned_buckets_json="$(
  jq -c '
    [
      .resource_changes[]?
      | select(.type == "aws_s3_bucket" and (.change.actions | index("delete")))
      | .change.before.bucket
    ]
    | unique
  ' <<< "$plan_json"
)"

planned_buckets=()
has_planned_buckets=false
while IFS= read -r bucket; do
  planned_buckets+=("$bucket")
  has_planned_buckets=true
done < <(jq -r '.[]' <<< "$planned_buckets_json")
allowed_buckets=(
  "crossword-solver-${TF_VAR_environment}-puzzle-images"
  "crossword-solver-${TF_VAR_environment}-lambda-layers"
  "crossword-solver-${TF_VAR_environment}-ui"
)

if [[ "$has_planned_buckets" == true ]]; then
  for bucket in "${planned_buckets[@]}"; do
    if [[ "$bucket" == "$TF_STATE_BUCKET" ]]; then
      echo "::error::Refusing to empty the Terraform state bucket $bucket." >&2
      exit 1
    fi

    allowed=false
    for allowed_bucket in "${allowed_buckets[@]}"; do
      if [[ "$bucket" == "$allowed_bucket" ]]; then
        allowed=true
        break
      fi
    done
    if [[ "$allowed" != true ]]; then
      echo "::error::Refusing to empty unexpected bucket $bucket from the destroy plan." >&2
      exit 1
    fi
  done

  for bucket in "${planned_buckets[@]}"; do
    echo "Emptying s3://$bucket"
    aws s3 rm "s3://$bucket" --recursive

    while true; do
      versions_json="$(aws s3api list-object-versions --bucket "$bucket" --no-paginate --output json)"
      delete_json="$(
        jq -c '
          {
            Objects: ((.Versions // []) + (.DeleteMarkers // []) | map({Key, VersionId})),
            Quiet: true
          }
        ' <<< "$versions_json"
      )"

      if [[ "$(jq '.Objects | length' <<< "$delete_json")" == 0 ]]; then
        break
      fi

      delete_file="$(mktemp)"
      trap 'rm -f "$delete_file"' EXIT
      printf '%s\n' "$delete_json" > "$delete_file"
      delete_result="$(aws s3api delete-objects --bucket "$bucket" --delete "file://$delete_file" --output json)"
      rm -f "$delete_file"
      trap - EXIT

      if jq -e '(.Errors // []) | length > 0' <<< "$delete_result" > /dev/null; then
        jq -c '.Errors[]' <<< "$delete_result" >&2
        exit 1
      fi
    done
  done
fi

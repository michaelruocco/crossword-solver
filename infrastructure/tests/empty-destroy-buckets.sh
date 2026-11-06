#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEST_DIR="$(mktemp -d)"
trap 'rm -rf "$TEST_DIR"' EXIT
export TEST_DIR

terraform() {
  if [[ "${TEST_TERRAFORM_FAILURE:-false}" == true ]]; then
    echo "Mock Terraform failure" >&2
    return 1
  fi
  printf '%s\n' "$TEST_PLAN_JSON"
}

aws() {
  printf '%s\n' "$*" >> "$TEST_DIR/aws-calls"
  case "$1 $2" in
    "sts get-caller-identity") printf '123456789012\n' ;;
    "s3 rm") return 0 ;;
    "s3api list-object-versions")
      if [[ "${TEST_AWS_FAILURE:-false}" == true ]]; then
        echo "Mock AWS failure" >&2
        return 1
      fi
      local count=0
      if [[ -f "$TEST_DIR/list-count" ]]; then read -r count < "$TEST_DIR/list-count"; fi
      printf '%s\n' "$((count + 1))" > "$TEST_DIR/list-count"
      if (( count < 2 )); then
        printf '%s\n' '{"Versions":[{"Key":"layer.zip","VersionId":"version-1"}],"DeleteMarkers":[{"Key":"layer.zip","VersionId":"marker-1"}]}'
      else
        printf '{}\n'
      fi
      ;;
    "s3api delete-objects")
      local payload="${6#file://}"
      jq -e '.Objects | length == 2 and .[0].VersionId == "version-1" and .[1].VersionId == "marker-1"' "$payload" > /dev/null || return 1
      printf '%s\n' "$TEST_DELETE_RESULT"
      ;;
    *) echo "Unexpected mock AWS command: $*" >&2; return 1 ;;
  esac
}

export -f terraform aws
export TF_VAR_environment=dev
export TF_STATE_BUCKET=crossword-solver-state
export TEST_DELETE_RESULT='{}'
export TEST_PLAN_JSON

run_case() {
  local expected="$1"
  local actual=0
  rm -f "$TEST_DIR/aws-calls" "$TEST_DIR/list-count"
  bash "$SCRIPT_DIR/../empty-destroy-buckets.sh" > "$TEST_DIR/stdout" 2> "$TEST_DIR/stderr" || actual=$?
  if [[ "$actual" != "$expected" ]]; then
    cat "$TEST_DIR/stderr" >&2
    echo "Expected exit $expected, got $actual" >&2
    exit 1
  fi
}

TEST_PLAN_JSON='{"resource_changes":[{"type":"aws_s3_bucket","change":{"actions":["delete"],"before":{"bucket":"crossword-solver-dev-lambda-layers"}}}]}'
run_case 0
[[ "$(grep -c 's3api delete-objects' "$TEST_DIR/aws-calls")" == 2 ]]
[[ "$(cat "$TEST_DIR/list-count")" == 3 ]]
echo "PASS: removes versions and delete markers across multiple batches"

export TEST_DELETE_RESULT='{"Errors":[{"Key":"layer.zip","VersionId":"version-1","Code":"AccessDenied","Message":"Access Denied"}]}'
run_case 1
grep -q '"Key": "layer.zip"' "$TEST_DIR/stderr"
grep -q '"VersionId": "version-1"' "$TEST_DIR/stderr"
grep -q '"Code": "AccessDenied"' "$TEST_DIR/stderr"
grep -q '"Message": "Access Denied"' "$TEST_DIR/stderr"
[[ "$(grep -c 's3api delete-objects' "$TEST_DIR/aws-calls")" == 1 ]]
echo "PASS: reports all per-object failure details and stops immediately"
export TEST_DELETE_RESULT='{}'

TEST_PLAN_JSON=$(jq '.resource_changes += [{"type":"aws_s3_bucket","change":{"actions":["delete"],"before":{"bucket":"unexpected-bucket"}}}]' <<< "$TEST_PLAN_JSON")
run_case 1
! grep -q '^s3 ' "$TEST_DIR/aws-calls"
grep -q 'unexpected bucket unexpected-bucket' "$TEST_DIR/stderr"
echo "PASS: validates every bucket before deleting any objects"

TEST_PLAN_JSON='{"resource_changes":[{"type":"aws_s3_bucket","change":{"actions":["delete"],"before":{"bucket":"crossword-solver-dev-lambda-layers"}}}]}'
export TF_STATE_BUCKET=crossword-solver-dev-lambda-layers
run_case 1
! grep -q '^s3 ' "$TEST_DIR/aws-calls"
grep -q 'Terraform state bucket' "$TEST_DIR/stderr"
echo "PASS: refuses the state bucket even if its name matches the allowlist"
export TF_STATE_BUCKET=crossword-solver-state

export TEST_AWS_FAILURE=true
run_case 1
grep -q 'Mock AWS failure' "$TEST_DIR/stderr"
! grep -q 's3api delete-objects' "$TEST_DIR/aws-calls"
echo "PASS: preserves AWS command failures"
export TEST_AWS_FAILURE=false

export TEST_TERRAFORM_FAILURE=true
run_case 1
[[ ! -f "$TEST_DIR/aws-calls" ]]
grep -q 'Mock Terraform failure' "$TEST_DIR/stderr"
echo "PASS: does not call AWS when reading the plan fails"
export TEST_TERRAFORM_FAILURE=false

TEST_PLAN_JSON='{"resource_changes":[{"type":"aws_s3_bucket","change":{"actions":["no-op"],"before":{"bucket":"unexpected-bucket"}}}]}'
run_case 0
! grep -q '^s3 ' "$TEST_DIR/aws-calls"
echo "PASS: ignores buckets not scheduled for deletion"
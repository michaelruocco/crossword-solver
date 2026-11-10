#!/usr/bin/env bash
set -euo pipefail

# Script to validate deployment configuration
# Expects AWS_ROLE_ARN and TF_STATE_BUCKET environment variables to be set

if [[ -z "${AWS_ROLE_ARN:-}" || -z "${TF_STATE_BUCKET:-}" ]]; then
  echo "::error::Configure AWS_ROLE_ARN and TF_STATE_BUCKET as GitHub Actions variables."
  exit 1
fi

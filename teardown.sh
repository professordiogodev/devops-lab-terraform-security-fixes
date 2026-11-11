#!/usr/bin/env bash
# Removes Terraform and scanner caches. Nothing was ever created in AWS. Run with: ./teardown.sh
cd "$(dirname "$0")" || exit 1
rm -rf terraform/.terraform terraform/.terraform.lock.hcl .checkov_baseline
find . -name __pycache__ -type d -prune -exec rm -rf {} + 2>/dev/null
echo "Now run ./verify-teardown.sh"

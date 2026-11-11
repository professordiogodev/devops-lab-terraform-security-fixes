#!/usr/bin/env bash
# Proves the lab left nothing behind. Run with: ./verify-teardown.sh
cd "$(dirname "$0")" || exit 1
pass=0; failn=0
check() { local d="$1"; shift; if "$@" >/dev/null 2>&1; then echo "PASS  $d"; pass=$((pass+1)); else echo "FAIL  $d"; failn=$((failn+1)); fi; }
check "no .terraform directory or lock file" bash -c '[ ! -d terraform/.terraform ] && [ ! -f terraform/.terraform.lock.hcl ]'
check "no Terraform state file (nothing was applied)" bash -c '[ -z "$(find terraform -name "*.tfstate*")" ]'
echo
if [ "$failn" -eq 0 ]; then echo "TEARDOWN VERIFIED ($pass/$pass) on this machine"; else echo "NOT CLEAN: $failn leftover(s)."; fi
exit "$failn"

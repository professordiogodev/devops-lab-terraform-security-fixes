#!/usr/bin/env bash
rc=0
grep -q 'TODO' FIXES.md && { echo "- ❌ FIXES.md still has TODO"; rc=1; } || echo "- ✅ FIXES.md is filled in"
grep -q '0.0.0.0/0' terraform/main.tf && grep -qE 'port.*(22|3306)' terraform/main.tf && grep -B3 -A3 '0.0.0.0/0' terraform/main.tf | grep -qE '(22|3306)' && { echo "- ❌ SSH or MySQL may still be open to the world"; rc=1; } || echo "- ✅ no SSH/MySQL open to the world"
grep -q 'pollie123' terraform/main.tf && { echo "- ❌ the password is still in main.tf"; rc=1; } || echo "- ✅ no hardcoded password"
git ls-files | grep -qE '[.]tfstate|[.]terraform/' && { echo "- ❌ state or .terraform is committed"; rc=1; } || echo "- ✅ no state committed"
grep -qE '^ALL CHECKS PASSED \(' SUBMISSION.md && echo "- ✅ SUBMISSION.md shows ALL CHECKS PASSED" || { echo "- ❌ paste the verify.sh output ('ALL CHECKS PASSED') into SUBMISSION.md"; rc=1; }
exit $rc

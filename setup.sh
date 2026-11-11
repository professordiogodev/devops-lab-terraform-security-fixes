#!/usr/bin/env bash
# Checks the tools. Creates nothing anywhere. Run: ./setup.sh
cd "$(dirname "$0")" || exit 1
for c in terraform checkov python3; do command -v "$c" >/dev/null && echo "ok: $c" || echo "MISSING: $c  (checkov: python3 -m pip install checkov)"; done
echo "Your first scan:  checkov -d terraform --framework terraform --compact --quiet"

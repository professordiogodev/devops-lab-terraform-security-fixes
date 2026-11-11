#!/usr/bin/env bash
# Scans your Terraform with Checkov and checks your fixes. Run with: ./verify.sh
cd "$(dirname "$0")" || exit 1
command -v checkov >/dev/null || { echo "checkov is not installed:  python3 -m pip install checkov" >&2; exit 1; }
exec python3 .lab/tfseccheck.py

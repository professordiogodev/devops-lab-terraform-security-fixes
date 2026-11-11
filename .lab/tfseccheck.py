#!/usr/bin/env python3
import json, os, re, shutil, subprocess, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.chdir(ROOT)
passed = failed = 0

# The rules this lab enforces. Checkov has hundreds more and adds new ones every month; this list is stable on purpose.
REQUIRED = {
    "CKV_AWS_20": "S3: no public READ ACL", "CKV2_AWS_6": "S3: public access block", "CKV_AWS_21": "S3: versioning", "CKV_AWS_18": "S3: access logging",
    "CKV_AWS_24": "SG: SSH not open to the world", "CKV_AWS_23": "SG: every rule has a description",
    "CKV_AWS_16": "RDS: encrypted at rest", "CKV_AWS_17": "RDS: not publicly accessible", "CKV_AWS_133": "RDS: backups", "CKV_AWS_293": "RDS: deletion protection",
    "CKV_AWS_79": "EC2: IMDSv1 disabled", "CKV_AWS_8": "EC2: EBS encrypted", "CKV_AWS_88": "EC2: no public IP", "CKV_AWS_126": "EC2: detailed monitoring",
    "CKV_AWS_62": "IAM: no full admin", "CKV_AWS_63": "IAM: no wildcard action", "CKV_AWS_355": "IAM: no wildcard resource", "CKV2_AWS_40": "IAM: no full IAM privileges",
    "CKV_AWS_286": "IAM: no privilege escalation", "CKV_AWS_287": "IAM: no credentials exposure", "CKV_AWS_288": "IAM: no data exfiltration",
    "CKV_AWS_289": "IAM: no permissions management", "CKV_AWS_290": "IAM: no unconstrained write",
}


def check(desc, ok, hint=""):
    global passed, failed
    if ok:
        passed += 1; print("PASS  " + desc, flush=True)
    else:
        failed += 1; print("FAIL  " + desc + (("   -> " + hint) if hint else ""), flush=True)


def sh(*a, timeout=900):
    r = subprocess.run(a, capture_output=True, text=True, timeout=timeout)
    return r.returncode, r.stdout, r.stderr


tf = open("terraform/main.tf").read()
code = "\n".join(l for l in tf.split("\n") if not l.lstrip().startswith("#") or "checkov:skip" in l)
print("== The code ==")
if shutil.which("terraform"):
    check("terraform fmt -check is clean", sh("terraform", "-chdir=terraform", "fmt", "-check")[0] == 0, "terraform -chdir=terraform fmt")
    sh("terraform", "-chdir=terraform", "init", "-backend=false", "-input=false", "-no-color")
    rc, o, e = sh("terraform", "-chdir=terraform", "validate", "-no-color")
    check("terraform validate passes (your fixes did not break the code)", rc == 0, (o + e)[-250:])
else:
    print("      (terraform is not installed: fmt and validate skipped)")
check("the AWS provider has a version constraint", re.search(r'required_providers\s*\{[^}]*aws\s*=\s*\{[^}]*version\s*=', code, re.S) is not None)
check("the database password is not a default value: a sensitive variable with no default, or managed by RDS", re.search(r'variable\s+"db_password"\s*\{(?![^}]*default)[^}]*sensitive\s*=\s*true', code, re.S) is not None or "manage_master_user_password" in code)
check("no password or secret is written in a .tf file", not re.search(r'(?i)(password|secret)\s*=\s*"[^"$]{4,}"', code) and "pollie123" not in code)
check("no security group rule opens MySQL (3306) or SSH (22) to 0.0.0.0/0", not re.search(r'(from_port|to_port)\s*=\s*(22|3306)[^}]*0\.0\.0\.0/0', code, re.S))
check("resources are tagged (a tags argument, or default_tags on the provider)", "default_tags" in code or code.count("tags") >= 3)

print("== The scanner ==")
if not shutil.which("checkov"):
    print("      checkov is not installed:  python3 -m pip install checkov"); sys.exit(1)
rc, out, err = sh("checkov", "-d", "terraform", "--framework", "terraform", "--quiet", "--compact", "-o", "json")
try:
    d = json.loads(out)
    r = d if isinstance(d, dict) else d[0]
    res = r["results"]
except Exception:
    check("checkov ran", False, (out + err)[-250:]); sys.exit(1)
failed_ids = {}
for c in res.get("failed_checks", []):
    failed_ids.setdefault(c["check_id"], set()).add(c["resource"])
skipped = [c for c in res.get("skipped_checks", [])]
for cid, desc in REQUIRED.items():
    check("%s %s" % (cid, desc), cid not in failed_ids, "fails on: %s" % ", ".join(sorted(failed_ids.get(cid, []))))
check("at most 3 skipped checks, each with a reason of at least 20 characters", len(skipped) <= 3 and all(len((c.get("check_result") or {}).get("suppress_comment", "") or "") >= 20 for c in skipped), "#checkov:skip=CKV_AWS_xxx: reason ...")
n = open("FIXES.md").read()
check("FIXES.md is filled in (no TODO left)", "TODO" not in n and len(n.split()) > 80)
print()
print(("ALL CHECKS PASSED (%d/%d)" % (passed, passed)) if failed == 0 else ("%d check(s) failed, %d passed" % (failed, passed)))
sys.exit(1 if failed else 0)

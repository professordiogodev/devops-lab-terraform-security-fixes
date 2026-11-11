# LAB | Terraform: The Plan That Would Have Leaked Everything

## The situation

A colleague opened a pull request for Pollie's cloud resources: a bucket for uploads, a web server, a MySQL database and an IAM policy for the app. It is tidy, it passes `terraform validate`, `terraform plan` shows nine resources to add, and two reviewers have written "LGTM". If it were applied this afternoon:

- every upload would be readable by anyone on the internet,
- the database would accept connections from the whole world, with a password committed to the repository,
- the server would hand its credentials to anyone who can make it fetch a URL,
- and the app would hold an IAM policy that allows **every action on every resource** of the account.

Nobody looked for these because, in infrastructure code, what is *missing* is invisible: no line says "don't encrypt". A scanner reads every resource and knows what a safe one looks like. Today you use one. Nothing is deployed and nothing costs money: this is about reading and fixing code before it becomes a bill or a breach.

> **Your mission**
> - Run Checkov on the pull request and read the report as a list of attacks
> - Fix the code resource by resource: S3, network, database, server, IAM, secrets
> - Keep `terraform validate` green: a secure file that does not work is not a fix
> - Justify any check you skip, in writing, on the line itself
> - Pass the checker, then write down what you changed

**Time:** 90-105 min | **Cost:** free (nothing is created in AWS) | **You need:** Terraform 1.10 or newer, Checkov (`python3 -m pip install checkov`), Python 3, git and a terminal.

---

## Part 0 - The pull request

Fork this repository, clone your fork and run `./setup.sh` (it only checks that the tools exist). Read `terraform/main.tf` from top to bottom, as a reviewer would, before you run anything. Write down the problems you see yourself. Then:

```bash
cd terraform
terraform init -backend=false
terraform validate
cd ..
checkov -d terraform --framework terraform --compact --quiet
```

Validate says "Success". Checkov says 36 checks failed. Both are right: the code is **valid** and **unsafe**.

> **Think** `terraform plan` would also have looked fine. What does a plan show you, and what can it never show you? (A plan describes what will be *created*, not whether the thing is a good idea.)

---

## Part 1 - S3: an attacker's reading list

`acl = "public-read"` means what it says. Fix the bucket with the **separate resources** of the current AWS provider:

- a public access block with **all four** settings on (`block_public_acls`, `block_public_policy`, `ignore_public_acls`, `restrict_public_buckets`): even a later mistake in a policy cannot make the bucket public;
- versioning (a delete or overwrite can be undone);
- default encryption;
- access logging into a **second** bucket. That log bucket needs its own public access block and versioning, and it cannot log into itself without a loop: for that one check use a `#checkov:skip=CKV_AWS_18:<reason>` comment above the resource. A skip is a decision, so it carries its reason.

---

## Part 2 - Network and database

- SSH must not be open to `0.0.0.0/0`. Take the allowed range from a **variable with no default** (the office or VPN range).
- MySQL (3306) must not be open to the world either. Give the database **its own security group** that accepts port 3306 only **from the web servers' security group** (`security_groups = [...]`, not a CIDR).
- Every rule has a `description`.
- The database: encrypted at rest, **not** publicly accessible, backups on (`backup_retention_period`), deletion protection on, a final snapshot, and attached to the database security group.
- **The password.** It is `default = "pollie123"` in a variable. Remove it. The best option is `manage_master_user_password = true`: RDS creates the password in Secrets Manager and rotates it, and Terraform never sees it. The alternative is a variable with **no default** and `sensitive = true`.

> **Think** `sensitive = true` hides the value in the plan output. Does it keep it out of the state file? (Open a state file in your head: Terraform stores every attribute it manages, in clear text, in the state. Who can read your state bucket?)

---

## Part 3 - The server

- Instance metadata: `metadata_options { http_tokens = "required" }` disables the old IMDSv1, which a server-side request forgery bug can use to steal the instance's credentials (you may have seen this in the IMDS lab).
- Encrypted root volume, no public IP, detailed monitoring.

---

## Part 4 - IAM: least privilege

`Action = "*"` and `Resource = "*"` is administrator. The app needs to read and write objects in the uploads bucket. Write exactly that, with an `aws_iam_policy_document` data source: the actions `s3:GetObject` and `s3:PutObject`, on `"${aws_s3_bucket.uploads.arn}/*"`. Notice how many Checkov rules about privilege escalation, credential exposure and data exfiltration pass at once when a policy names what it needs.

---

## Part 5 - Hygiene, and what to skip

- The AWS provider needs a **version constraint** (`version = "~> 6.0"`). Without one, the next `terraform init` may download a different major version.
- Tags: either a `tags` argument or `default_tags` on the provider, so every resource has an owner.
- Checkov has hundreds of checks and adds new ones every month. Some will keep failing on your fixed code (for example "S3 cross-region replication" or "RDS multi-AZ"): they are good ideas that cost money, and a team may decide not to follow them yet. The checker enforces a stable list; it lets you skip at most three, each with a reason of at least twenty characters. In real life, a skip needs a name next to it and a review date.

---

## Part 6 - Prove it

Write `FIXES.md` (for each group: what was wrong as an attack, what you changed), then:

```bash
./verify.sh
```

It runs `terraform fmt` and `validate`, enforces the list of Checkov rules, checks that there is no password in any `.tf` file and no port 22 or 3306 open to the world, and reads your notes. Fix what is red and run it again until it ends with **ALL CHECKS PASSED**.

> **Stuck?** `validate` fails after your edit: a reference to a resource you renamed or removed. `CKV2_AWS_6` still fails: the public access block must be a separate resource with `bucket = aws_s3_bucket.X.id`. `CKV_AWS_18` fails on the log bucket: the skip comment must be directly above that resource. `CKV_AWS_290` still fails: the policy still has `Action = "*"` or a resource of `*`. `terraform fmt -check` fails: run `terraform -chdir=terraform fmt`.

---

## Level up (optional)

- Run the scan against the **plan** instead of the files: `terraform plan -out tf.plan && terraform show -json tf.plan > plan.json && checkov -f plan.json`. What does the plan know that the source does not (resolved variables, module outputs)?
- Add the scan to a GitHub Actions workflow with a pinned action and make it a required check on pull requests. How would a developer see the failing rule?
- Add `tflint` with the AWS ruleset. Which problems does it find that Checkov does not (invalid instance types, deprecated arguments)?
- Replace the AES256 default encryption by a KMS key you manage (`CKV_AWS_145`). What does it cost, and what does it let you do (key policies, audit, revocation)?

<!-- teardown:start (generated by labs.py, do not edit) -->
## Tear down (mandatory)

Resources left behind cost money, keep doors open and pollute the next lab. Removing what you created is part of the job, so it is part of the submission: **you must prove it is gone**.

Do this **last**, after you have pasted your `verify` output into `SUBMISSION.md` (once you tear down, the lab can no longer be verified).

1. Nothing is created in AWS. Run `./teardown.sh` to remove the Terraform and scanner caches, then `./verify-teardown.sh`.

Then run the proof:

```bash
./verify-teardown.sh
```

It prints a list of checks and must end with **TEARDOWN VERIFIED**. If it reports leftovers, remove them and run it again. Paste the full output in your submission.
<!-- teardown:end -->

<!-- submission:start (generated by labs.py, do not edit) -->
## Submission

Answer the questions in `SUBMISSION.md` in **your fork** (paste output in code blocks where asked), push, then submit the **URL of your fork**.

**Files to commit**

- `terraform/main.tf`: the fixed code
- `FIXES.md`: what you changed and why

**Questions to answer**

1. Paste the summary of the first Checkov run (passed, failed, skipped). Choose three failed checks and explain each as an attack: who could do what to whom if this were applied?
2. Show your S3 fix. What are the four settings of a public access block and what does each stop? Why is `acl = "public-read"` deprecated, and what replaced ACLs for access control?
3. The database password was `default = "pollie123"` in a `.tf` file. Where does the value live now, why is `sensitive = true` not enough on its own, and what does Terraform still write into the state file? Name two better options (a secrets store, `manage_master_user_password`).
4. Rewrite the IAM policy to least privilege and paste it. What are the actions and the resources? What do the checks about privilege escalation and data exfiltration look for in a policy?
5. You used `#checkov:skip` (or chose not to). When is a skip acceptable, what must it contain, and who should approve it? Why is a skip with no reason worse than a failing check?
6. Where would you run this scan so that the code above could never be merged? (hint: pre-commit, pull request, both.) Why scan the code AND the plan (`terraform show -json`)?
7. Paste the output of `./verify.sh`. It must end with **ALL CHECKS PASSED**.
8. **Tear down.** Paste the output of `./verify-teardown.sh`. It must end with **TEARDOWN VERIFIED**.
<!-- submission:end -->

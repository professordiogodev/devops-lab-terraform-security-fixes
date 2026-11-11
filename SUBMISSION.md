# Submission

Fork URL: <!-- paste the URL of your fork here -->

## Files to commit

- [ ] `terraform/main.tf`: the fixed code
- [ ] `FIXES.md`: what you changed and why

## Questions

Answer in your own words. Where a question asks for output, paste it in a code block.

### Q1. Paste the summary of the first Checkov run (passed, failed, skipped). Choose three failed checks and explain each as an attack: who could do what to whom if this were applied?

**Your answer:**

<!-- replace this line with your answer -->

### Q2. Show your S3 fix. What are the four settings of a public access block and what does each stop? Why is `acl = "public-read"` deprecated, and what replaced ACLs for access control?

**Your answer:**

<!-- replace this line with your answer -->

### Q3. The database password was `default = "pollie123"` in a `.tf` file. Where does the value live now, why is `sensitive = true` not enough on its own, and what does Terraform still write into the state file? Name two better options (a secrets store, `manage_master_user_password`).

**Your answer:**

<!-- replace this line with your answer -->

### Q4. Rewrite the IAM policy to least privilege and paste it. What are the actions and the resources? What do the checks about privilege escalation and data exfiltration look for in a policy?

**Your answer:**

<!-- replace this line with your answer -->

### Q5. You used `#checkov:skip` (or chose not to). When is a skip acceptable, what must it contain, and who should approve it? Why is a skip with no reason worse than a failing check?

**Your answer:**

<!-- replace this line with your answer -->

### Q6. Where would you run this scan so that the code above could never be merged? (hint: pre-commit, pull request, both.) Why scan the code AND the plan (`terraform show -json`)?

**Your answer:**

<!-- replace this line with your answer -->

### Q7. Paste the output of `./verify.sh`. It must end with **ALL CHECKS PASSED**.

**Your answer:**

<!-- replace this line with your answer -->

### Q8. **Tear down.** Paste the output of `./verify-teardown.sh`. It must end with **TEARDOWN VERIFIED**.

**Your answer:**

<!-- replace this line with your answer -->

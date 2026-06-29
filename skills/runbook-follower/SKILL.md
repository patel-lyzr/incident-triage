---
name: runbook-follower
description: Walk an incident runbook as a decision tree, correlating New Relic symptoms with the GitHub change that caused them.
---

# Runbook Follower

Use this skill whenever an alert arrives. It turns the runbook into an executable
decision tree and keeps you correlating **symptom (New Relic) → change (GitHub)**.

The runbook lives as a markdown file in the repo (`knowledge/`) or in the
service's GitHub repo (fetch it with the GitHub MCP `get_file_contents`).

## Instructions
Parse the runbook into ordered **steps**, each one of:
- **measure** — run a New Relic query with the `nrql-query` tool; record the number.
- **branch** — choose the next step from a condition over prior results.
- **correlate** — use the **GitHub MCP** (`list_commits`, `list_pull_requests`,
  `get_pull_request`) to find the change near the spike; name the suspect PR.
- **search** — use the **GitHub MCP** (`search_issues`) for existing reports.
- **report** — use the **GitHub MCP** (`create_issue_comment` / `create_issue`)
  to post findings on the incident issue.
- **escalate** — request to page a human (requires human review).

Execute in order, never skip. At each branch, state the condition + which path
you took + the evidence (the NRQL number or the commit/PR).

## Output — decision log
```
- measure(error_rate): 4.2% (NRQL) → above 1% threshold
- branch: error_rate>1% → correlate
- correlate: PR #482 "switch payments to new pool" merged 6m before spike → SUSPECT
- search: issue #131 "checkout 5xx" open → linked
- report: commented findings on #131 with PR link + evidence
## Recommendation
Roll back PR #482 — requires human approval.
```

Load only the runbook section relevant to the current branch (progressive disclosure).

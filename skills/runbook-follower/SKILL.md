---
name: runbook-follower
description: Ingest a Confluence runbook and walk it as a step-by-step decision tree.
---

# Runbook Follower

Use this skill whenever an alert maps to a runbook. It turns a prose runbook into
an executable decision tree and keeps you on-track.

## Instructions
1. Fetch the runbook page (via the `confluence` MCP server) by the title the
   alert references, or search by service + symptom.
2. Parse it into ordered **steps**. Each step is one of:
   - **check** — run a diagnostic (use `nrql-query`) and record the result.
   - **branch** — choose the next step based on a condition over prior results.
   - **action** — a remediation (requires human approval; never auto-run in prod).
   - **escalate** — hand off (to a sub-agent, or request to page a human).
3. Execute steps **in order**. Never skip. At each branch, state the condition and
   which path you took and why (cite the diagnostic result).
4. Keep a running **decision log**: `step id → action taken → evidence`.
5. Stop at the first `action`/`escalate` step that needs human review and surface
   the decision log so far.

## Output format
```
## Decision log
- step 1 (check error_rate): error_rate=4.2% (NRQL) → above 1% threshold
- step 2 (branch): error_rate>1% → go to step 4 (DB path)
- step 4 (check db_latency): p95=812ms → elevated
...
## Recommendation
<the runbook's prescribed next action> — requires human approval before execution.
```

## Progressive disclosure
Load only the runbook section relevant to the current branch; do not dump the
whole corpus into context.

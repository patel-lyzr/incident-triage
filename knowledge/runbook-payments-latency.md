# Runbook — Payments Latency / Errors

Symptom: elevated checkout/payment latency or error rate.

1. measure: `SELECT percentage(count(*), WHERE error) FROM PaymentTxn WHERE appName='payments' SINCE 15 minutes ago`
   - branch: error_rate > 1% → step 2 (correlate); else → step 4 (latency path).
2. correlate (GitHub MCP): list merged PRs + commits on the payments repo in the
   last 2h. A change merged shortly before the spike is the prime suspect.
3. search (GitHub MCP): search open issues for "payments" / "checkout 5xx" — link if found.
4. measure latency: `SELECT percentile(duration,95) FROM PaymentTxn WHERE appName='payments' SINCE 15 minutes ago`
   - branch: p95 > 800ms → escalate to diagnoser "latency regression".
5. report (GitHub MCP): comment findings (impact, suspect PR + link, evidence) on the incident issue.
6. escalate: request to page payments on-call (HUMAN REVIEW REQUIRED).

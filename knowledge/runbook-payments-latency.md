# Runbook — Payments Latency

Symptom: elevated checkout/payment latency or error rate.

1. check: `SELECT percentage(count(*), WHERE error) FROM Transaction WHERE appName='payments' SINCE 10 minutes ago`
   - branch: error_rate > 1% → step 3 (DB path); else → step 2 (upstream path).
2. check upstream: `SELECT average(duration) FROM Span WHERE service='payment-gateway' SINCE 10 minutes ago` → escalate to diagnoser with hypothesis "upstream gateway slow".
3. check DB: `SELECT percentile(db.duration,95) FROM Span WHERE service='payments' SINCE 10 minutes ago`
   - branch: p95 > 500ms → escalate to diagnoser "db contention"; else → escalate "unknown".
4. action: failover read replica — REQUIRES HUMAN APPROVAL.
5. escalate: post findings, then request page of payments on-call.

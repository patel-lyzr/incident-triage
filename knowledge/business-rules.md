# Business Rules — Incident Triage

- **Severity → SLA**: SEV1 ack 5m / mitigate 30m; SEV2 ack 15m / mitigate 2h.
- **Page threshold**: page on-call only after a channel update is posted AND the
  runbook's escalate step is reached. Never page on a single elevated metric.
- **Customer-impact gate**: any incident touching payments/checkout is SEV1.
- **PII**: customer SSN, email, card, phone must never appear in channel posts.
- **Change freeze**: no production changes 24h before/after a major sale event.

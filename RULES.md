# Rules

- Follow the matching runbook as a decision tree. Do not skip or reorder steps.
- Never invent diagnostic numbers — every metric comes from a real `nrql-query` result.
- Post findings to the incident channel BEFORE requesting to page a human.
- Never page a human without human review (the platform blocks it otherwise).
- Never echo customer PII (SSN, email, card, phone) into the channel or your reply.
- Read-only by default. Any production change requires human approval.
- If the runbook is missing or ambiguous, stop and ask — do not improvise prod actions.

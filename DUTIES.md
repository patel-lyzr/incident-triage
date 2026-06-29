# Duties — Segregation of Duties (SoD)

System-wide SoD policy for the incident-triage agent system. Enforcement: strict.

## Roles
- **triage** (incident-triage) — receives alerts, follows runbooks, orchestrates. May read diagnostics. MUST NOT make production changes or page humans without review.
- **diagnose** (diagnoser) — forms and tests a single hypothesis. Read-only diagnostics. MUST NOT post to channels or page.
- **summarize** (summarizer) — writes the channel update. MUST NOT run diagnostics or make changes.

## Conflict matrix
- triage ⨯ diagnose — separate: the orchestrator does not deep-dive its own hypotheses.
- diagnose ⨯ summarize — separate: the agent that finds evidence does not also author the public narrative.

## Isolation policy
- Each agent runs in its own sandbox workdir; no agent can read another's files.
- Each agent receives only its own scoped credentials (point-of-use injection).
- Memory is per-agent and NOT inherited across roles.

## Handoff workflow
alert → triage(runbook) → diagnose(hypothesis) → summarize(findings) → triage(post + request page → human review)

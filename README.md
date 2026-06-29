# incident-triage

Nordstrom reference **incident triage agent** (OpenGAP spec v0.1.0). Core idea:
most incidents are caused by a recent deploy, so the agent **correlates the
symptom (New Relic) with the change that caused it (GitHub)** and reports it.

Flow: alert → confirm the spike with NRQL → find the suspect commit/PR via the
**GitHub MCP** → search open issues for dupes → delegate the deep-dive to
sub-agents → comment findings on the incident issue → (human review) page on-call.

## Capabilities demonstrated
| Capability | Where it lives |
|---|---|
| **MCP** | GitHub MCP — `.mcp.json` (works today) + `agent.yaml → mcp_servers` (spec decl). Lists commits/PRs, searches & comments on issues. |
| **Tool** (code) | `tools/nrql-query.yaml` + `tools/scripts/nrql-query.py` — real New Relic NerdGraph NRQL. |
| **Skill** | `skills/runbook-follower/` — walks the runbook as a decision tree (symptom→change). |
| **Sub-agents** | `agents/diagnoser/`, `agents/summarizer.md` + `delegation`. |
| Knowledge | `knowledge/` — runbook + business rules + service ownership. |
| A2A / compliance / SoD | `agent.yaml → a2a`, `compliance` (HITL before paging), `DUTIES.md`. |

## Simulation data (so it runs end-to-end)
`scripts/seed_newrelic.py` seeds `PaymentTxn` events into New Relic (healthy
baseline → ~11% error + ~1s p95 regression in the last ~8 min). The matching
GitHub story lives on this repo: a merged **suspect PR** (payments pool 16→4),
an open **incident issue**, and a **related** known issue for the dupe-search.

The agent's path, end to end:
1. NRQL → `err_pct ≈ 11%, p95 ≈ 1000ms` (spike confirmed)
2. GitHub MCP `list_pull_requests` → the merged "lean connection pool" PR right before the spike = suspect
3. GitHub MCP `search_issues` → finds the open "pool exhaustion" issue (not a dupe of a fix, links context)
4. GitHub MCP `create_issue_comment` → posts findings + roll-back recommendation on the incident issue

## Run it
Register in AgentOS with `source = github.com/patel-lyzr/incident-triage`, engine
`claude-agent-sdk`. Required env injected by the platform:
`ANTHROPIC_API_KEY`, `GITHUB_PAT` (GitHub MCP), `NEW_RELIC_USER_API_KEY` +
`NEW_RELIC_ACCOUNT_ID` (the `nrql-query` tool).

## PII
PII is **not** in this repo — it's applied at the **proxy level (SRS)** from
Studio (incoming SSN=block / Email=redact on the execution path), independent of
the agent definition.

## Engine
Runs on **`claude-agent-sdk`** (the only engine that speaks MCP). `workflows/`
and `extends` were dropped (gitclaw-native, not needed here). The `mcp_servers:`
block in `agent.yaml` is the OpenGAP-spec declaration; `.mcp.json` is the
working copy the loader auto-discovers (`settingSources:["project"]`).

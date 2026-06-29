# incident-triage

Nordstrom reference **incident triage agent**, authored to the OpenGAP spec
(v0.1.0). It anchors the "complex agent" requirements: receive an alert → follow
the runbook → run diagnostics → delegate to sub-agents → post findings → (with
human review) page on-call.

## How this repo maps to the 11 requirements
| # | Requirement | Where it lives here |
|---|---|---|
| 1 | Multiple MCP servers, own creds | `agent.yaml → mcp_servers` (pagerduty, servicenow, confluence, newrelic; each `${TOKEN}`) |
| 2 | Tools + skills as code | `tools/nrql-query.yaml` (+ `scripts/`), `skills/runbook-follower/` |
| 3 | Ground in knowledge | `knowledge/index.yaml` + runbook & business-rules docs |
| 4 | Sub-agents | `agents/diagnoser/` (dir), `agents/summarizer.md` (file) + `delegation` |
| 5 | Call agents via platform | `agent.yaml → a2a` (by identity, not hardcoded endpoints) |
| 6 | Inherit base agent | `agent.yaml → extends: …/nordstrom-base-agent` |
| 7 | Real-time PII | SRS policy bound to the agent (see below) — incoming + outgoing |
| 8 | Runtime policy | SRS policy enforced per tool call (OPA/Cedar) |
| 9 | Tenant/run isolation | `DUTIES.md` (SoD) + per-agent sandbox/memory; `compliance.segregation_of_duties` |
| 10 | Cost attribution | platform observability (per agent/team), nothing repo-side |
| 11 | Creds out of reach | `${VAR}` refs only; broker injects at point of use (see scripts) |

## Run it
Register in AgentOS with `source = github.com/<org>/incident-triage`, or via SDK:
```ts
const agent = new ComputerAgent({
  source: "github.com/<org>/incident-triage",
  harness: "claude-agent-sdk",
  runtime: new LocalSubstrate(),
  envs: { ANTHROPIC_API_KEY, /* + MCP creds injected by the broker */ },
});
for await (const ev of agent.chat("Alert: payments latency SEV2")) { /* … */ }
```

## PII
PII is **not** configured in this repo. It's applied at the **proxy level (SRS)**,
configured from Studio — incoming/outgoing redaction runs on the execution path
independent of the agent definition. Nothing to wire here.

## Engine + what runs today
Run on **`claude-agent-sdk`** (the only engine that speaks MCP). To keep this
build runnable, `workflows/` and `extends` were dropped (those are gitclaw-native
and not needed here).

**Works on claude-agent-sdk today:**
- **MCP** — GitHub MCP via `.mcp.json` (auto-discovered with `settingSources:["project"]`)
- `tools/` — written in the claude-agent-sdk loader shape (`implementation.script`)
- `skills/` (the runbook-follower), `agents/` (sub-agents), `hooks/`, `compliance` (HITL), `model`
- `knowledge/` — files on disk; the agent reads them via the Read tool / the runbook skill

**Still platform-side gaps:** outgoing PII (`redactOutput`) and a Vault-backed
per-tenant credential broker (req #11). The `mcp_servers:` block in `agent.yaml`
is kept as the OpenGAP-spec declaration (inert; `.mcp.json` is the working copy).

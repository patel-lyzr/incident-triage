# Policies (SRS-enforced)

PII + runtime policy are **not** in the agent prompt — they're enforced on the
execution path by **SRS** (a policy is authored in Studio/SRS and bound to this
agent by `policy_id`; the harness evaluates every tool call + scrubs text).
This file documents the policy bound to `incident-triage` so it's reviewable.

Bound policy: RAI `6a441b16…79b` → wraps OPA `6a441b16…79a`.

## 1. PII — `pii_detection` (RAI / `/v1/rai/inference`)
Runs on `llm_input` (incoming) and `llm_output` (the GitHub comment the agent
writes — where PCI leakage would happen). Entity → action:

| Entity | Action | Why |
|---|---|---|
| `CREDIT_CARD` | **block** | PCI — a PAN must never flow through triage or into a comment |
| `US_SSN` | **block** | regulated PII |
| `EMAIL_ADDRESS` | redact → `[EMAIL]` | don't leak customer contact into an issue |
| `PHONE_NUMBER` | redact | same |
| `PERSON` | redact | scrub customer names |

`block` rejects the turn with a block reason; `redact` swaps placeholders and lets
the agent keep working.

## 2. Runtime — OPA (Rego), per tool call
SRS sends the call as `input.request.{tool_name, arguments}` and reads `allow`.

```rego
package computeragent.tools

default allow = true

# Segregation of duties: the triage agent diagnoses + reports. It must NOT
# mutate source control (merge / open PRs / push / delete / edit issues).
mutating = {"merge_pull_request", "create_pull_request", "update_pull_request",
            "push_files", "create_or_update_file", "delete_file", "delete_ref",
            "update_issue"}
allow = false {
    mutating[t]
    endswith(input.request.tool_name, t)
}

# GitHub writes (comment / open issue) only on the owned org.
allow = false {
    input.request.tool_name == "mcp__github__add_issue_comment"
    input.request.arguments.owner != "patel-lyzr"
}
allow = false {
    input.request.tool_name == "mcp__github__create_issue"
    input.request.arguments.owner != "patel-lyzr"
}

# SSRF / cloud-metadata endpoint in any argument.
allow = false {
    contains(lower(json.marshal(input.request.arguments)), "169.254.169.254")
}
```

Verified via SRS `evaluate-tool-call`: `merge_pull_request` → deny, comment on
`patel-lyzr/*` → allow, comment elsewhere → deny, `nrql-query` → allow, IMDS → deny.

## 3. Runtime — Cedar (alternative engine, same SoD)
SRS also accepts a `cedar_guardrail`. Equivalent SoD rule:

```cedar
forbid(principal, action, resource)
when {
  action.tool_name like "mcp__github__merge_pull_request*" ||
  action.tool_name like "mcp__github__*create_pull_request*" ||
  action.tool_name like "mcp__github__push_files*"
};
```

## How it lines up with the agent
The agent *recommends* rolling back the suspect PR but is **policy-blocked** from
merging/reverting it — diagnose-and-report, never make the production change.
That pairs with `compliance.supervision.human_in_the_loop: always` (it can't page
a human without review either).

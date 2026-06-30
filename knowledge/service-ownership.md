# Service Ownership

Maps an alerting service to its GitHub repo (for correlation) and on-call.

| service | repo (GitHub MCP target) | team | on-call | channel |
|---|---|---|---|---|
| payments | patel-lyzr/payments-service | team-payments | payments-oncall | #inc-payments |
| checkout | patel-lyzr/payments-service | team-checkout | checkout-oncall | #inc-checkout |

When an alert names a service, look up its **repo** here and point **every**
GitHub MCP call at that repo — listing commits/PRs (correlation),
`search_issues` for existing reports, and `add_issue_comment`/`create_issue`
for the incident. Never use the agent's own definition repo for any of these.

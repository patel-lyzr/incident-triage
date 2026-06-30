# Service Ownership

Maps an alerting service to its GitHub repo (for correlation) and on-call.

| service | repo (GitHub MCP target) | team | on-call | channel |
|---|---|---|---|---|
| payments | patel-lyzr/payments-service | team-payments | payments-oncall | #inc-payments |
| checkout | patel-lyzr/payments-service | team-checkout | checkout-oncall | #inc-checkout |

When an alert names a service, look up its **repo** here and run the GitHub MCP
correlation against that repo — never against the agent's own definition repo.

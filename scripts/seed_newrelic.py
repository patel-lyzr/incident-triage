#!/usr/bin/env python3
"""Seed simulated `PaymentTxn` events into New Relic so the agent's NRQL finds a
real spike. Baseline-good for the first ~15 min, then a deploy-regression spike
(high error rate + latency) in the last ~8 min.

    NR_INGEST_KEY=<NRAL license key> NR_ACCOUNT_ID=8123390 python3 scripts/seed_newrelic.py

Query it back:  SELECT percentage(count(*), WHERE error) FROM PaymentTxn
                WHERE appName='payments' SINCE 20 minutes ago
"""
import json, os, sys, time, urllib.request

ACCT = os.environ.get("NR_ACCOUNT_ID", "8123390")
KEY = os.environ.get("NR_INGEST_KEY")
if not KEY:
    sys.exit("set NR_INGEST_KEY (the NRAL ingest/license key)")

now = int(time.time())
events = []
# 15 min of healthy baseline: ~0.5% errors, ~120ms p95
for i in range(160):
    ts = now - (20 * 60) + i * 5          # spread across the first 13-14 min
    err = (i % 200 == 0)                   # ~0.5%
    events.append({"eventType": "PaymentTxn", "appName": "payments",
                   "timestamp": ts, "error": err, "duration": 0.11 + (i % 3) * 0.01,
                   "route": "/checkout"})
# last ~8 min: regression — ~22% errors, ~900ms p95 (the deploy broke the pool)
for i in range(120):
    ts = now - (8 * 60) + i * 4
    err = (i % 9 < 2)                      # ~22%
    dur = 0.9 + (i % 5) * 0.05 if err else 0.4
    events.append({"eventType": "PaymentTxn", "appName": "payments",
                   "timestamp": ts, "error": err, "duration": dur,
                   "route": "/checkout"})

req = urllib.request.Request(
    f"https://insights-collector.newrelic.com/v1/accounts/{ACCT}/events",
    data=json.dumps(events).encode(),
    headers={"Content-Type": "application/json", "Api-Key": KEY},
)
with urllib.request.urlopen(req, timeout=30) as r:
    print(r.status, r.read().decode())
print(f"seeded {len(events)} PaymentTxn events (acct {ACCT})")
# ponytail: synchronous one-shot; NR ingest is async so allow ~30s before querying.

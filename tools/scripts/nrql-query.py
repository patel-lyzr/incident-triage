#!/usr/bin/env python3
"""nrql-query tool — runs a NRQL query via New Relic NerdGraph.

Reads the tool input as JSON on stdin (and args as UPPERCASE env vars), uses the
NEW_RELIC_USER_API_KEY supplied AT POINT OF USE by the platform broker (never stored
in the repo), and prints the rows as JSON on stdout. Non-zero exit on failure.
"""
import json, os, sys, urllib.request

def main() -> int:
    raw = sys.stdin.read() or "{}"
    args = json.loads(raw)
    nrql = args.get("nrql") or os.environ.get("NRQL")
    if not nrql:
        print("missing 'nrql'", file=sys.stderr); return 2
    key = os.environ.get("NEW_RELIC_USER_API_KEY")
    acct = os.environ.get("NEW_RELIC_ACCOUNT_ID")
    if not key or not acct:
        print("NEW_RELIC_USER_API_KEY / NEW_RELIC_ACCOUNT_ID not provided", file=sys.stderr); return 3
    query = (
        '{ actor { account(id: %s) { nrql(query: %s) { results } } } }'
        % (acct, json.dumps(nrql))
    )
    req = urllib.request.Request(
        "https://api.newrelic.com/graphql",
        data=json.dumps({"query": query}).encode(),
        headers={"Content-Type": "application/json", "API-Key": key},
    )
    try:
        with urllib.request.urlopen(req, timeout=int(args.get("timeout_seconds", 20))) as r:
            body = json.loads(r.read())
    except Exception as e:  # ponytail: surface the error as tool failure
        print(f"NRQL request failed: {e}", file=sys.stderr); return 1
    rows = (((body.get("data") or {}).get("actor") or {}).get("account") or {}).get("nrql", {}).get("results", [])
    print(json.dumps({"rows": rows, "total": len(rows)}))
    return 0

if __name__ == "__main__":
    sys.exit(main())

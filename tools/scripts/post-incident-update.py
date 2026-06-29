#!/usr/bin/env python3
"""Posts an incident-channel update. SLACK_BOT_TOKEN is supplied at point of use."""
import json, os, sys, urllib.request
a = json.loads(sys.stdin.read() or "{}")
tok = os.environ.get("SLACK_BOT_TOKEN")
if not tok: print("SLACK_BOT_TOKEN not provided", file=sys.stderr); sys.exit(3)
req = urllib.request.Request("https://slack.com/api/chat.postMessage",
    data=json.dumps({"channel": a["channel"], "text": a["text"]}).encode(),
    headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json"})
try:
    body = json.loads(urllib.request.urlopen(req, timeout=10).read())
except Exception as e:
    print(f"post failed: {e}", file=sys.stderr); sys.exit(1)
print(json.dumps({"ok": body.get("ok", False), "ts": body.get("ts")}))

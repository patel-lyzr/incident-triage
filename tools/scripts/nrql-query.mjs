#!/usr/bin/env node
// nrql-query tool — runs a NRQL query via New Relic NerdGraph.
// Reads tool input as JSON on stdin, uses NEW_RELIC_USER_API_KEY /
// NEW_RELIC_ACCOUNT_ID from env (injected by the platform), prints rows as JSON.
import https from "node:https";

const raw = await new Promise((r) => {
  let s = "";
  process.stdin.on("data", (c) => (s += c));
  process.stdin.on("end", () => r(s || "{}"));
});
const args = JSON.parse(raw);
const nrql = args.nrql || process.env.NRQL;
if (!nrql) { console.error("missing 'nrql'"); process.exit(2); }
const key = process.env.NEW_RELIC_USER_API_KEY, acct = process.env.NEW_RELIC_ACCOUNT_ID;
if (!key || !acct) { console.error("NEW_RELIC_USER_API_KEY / NEW_RELIC_ACCOUNT_ID not provided"); process.exit(3); }

const query = `{ actor { account(id: ${acct}) { nrql(query: ${JSON.stringify(nrql)}) { results } } } }`;
const body = JSON.stringify({ query });
const req = https.request("https://api.newrelic.com/graphql", {
  method: "POST",
  headers: { "Content-Type": "application/json", "API-Key": key, "Content-Length": Buffer.byteLength(body) },
  timeout: (args.timeout_seconds || 20) * 1000,
}, (res) => {
  let d = "";
  res.on("data", (c) => (d += c));
  res.on("end", () => {
    try {
      const rows = JSON.parse(d)?.data?.actor?.account?.nrql?.results ?? [];
      console.log(JSON.stringify({ rows, total: rows.length }));
    } catch (e) { console.error("NRQL parse failed: " + e.message); process.exit(1); }
  });
});
req.on("error", (e) => { console.error("NRQL request failed: " + e.message); process.exit(1); });
req.on("timeout", () => { req.destroy(); console.error("NRQL request timed out"); process.exit(1); });
req.end(body);

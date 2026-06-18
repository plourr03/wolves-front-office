# Data integrity (read this first, it is not optional)

## The rule
Every number, label, ranking, percentage, and factual claim that appears on screen must come from a query against the data warehouse. Nothing is estimated, rounded from memory, inferred from general NBA knowledge, or filled in to make a beat land. If a value is not validated, it does not go on screen.

## Why it matters
The whole brand rests on the analysis being trustworthy. One invented number that someone catches burns credibility that is slow to rebuild, and for a portfolio meant to be seen by front offices, credibility is the only currency that counts. Treat a fabricated stat as the one unforgivable bug.

## The workflow
1. Write the claims first. Before building anything, list every factual statement the post will make, which is every on-screen number and every assertion, as a claims manifest.
2. Back each claim with a query. For every claim, write the SQL that produces it against the warehouse. One claim, one query.
3. Run them and capture the exact values. Use the actual returned numbers, formatted for display. No approximations.
4. Log provenance. Record the query, the returned value, and the date pulled, so any number on screen can be traced back. The scripts/validate_claims.py helper does this for you.
5. Build only with validated values. Plug the captured numbers into the visual and nothing else.

## The story bends to the data, never the reverse
If a narrative beat you wanted is not supported by a query, either find data that supports it or cut the beat. Do not paper over a gap with "roughly" or "about." Decide the angle as a hypothesis, then let the validated numbers decide what the post actually says.

## Reusing an existing visual
Re-validate it. Re-run the queries behind every number already in the visual and confirm they still match the warehouse. If anything disagrees, stop, surface the discrepancy, and do not publish until it is resolved.

## Connecting to the warehouse
Use the existing connection (the Postgres warehouse over Tailscale). Read the connection string from an environment variable such as DATABASE_URL. Never hardcode credentials into the skill, the template, the manifest, or the post.

## When you cannot validate
If the warehouse is unreachable, or a needed table or field is missing, do not guess. Tell the user exactly which claim could not be backed, and stop. A post that ships a day late is fine. A post with a made-up number is not.

## The claims manifest
A small JSON file the validator reads. Each entry ties one on-screen value to the query that proves it:

```json
[
  {
    "id": "rs_rim_rate",
    "claim": "Share of regular-season FGA at the rim",
    "display": "42%",
    "query": "SELECT ROUND(100.0 * SUM(CASE WHEN shot_zone='rim' THEN 1 ELSE 0 END)/COUNT(*),0) FROM shots WHERE player='Anthony Edwards' AND season='2025-26' AND season_type='regular'"
  }
]
```

Run it with:

```
DATABASE_URL=... python scripts/validate_claims.py claims.json
```

The script runs every query, prints the warehouse value next to what you plan to show, writes provenance.json, and exits with an error if any claim fails to return a value. Confirm by eye that each on-screen display matches its warehouse value before you build.

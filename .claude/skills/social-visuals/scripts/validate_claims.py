#!/usr/bin/env python3
"""Validate every on-screen claim against the data warehouse before a post is built.

Reads a claims manifest (JSON), runs each claim's SQL against the warehouse
(connection from the DATABASE_URL environment variable), prints a results table,
and writes a provenance log. If any claim fails to return a value, it exits
non-zero so the build stops.

This is a pattern to adapt to your schema, not a finished query set. The rule it
enforces does not change: no number reaches the screen without a query behind it.

Manifest format (claims.json):
[
  {
    "id": "rs_rim_rate",
    "claim": "Share of regular-season FGA at the rim",
    "display": "42%",
    "query": "SELECT ... FROM ... WHERE ..."
  }
]
"""
import json
import os
import sys
import datetime

try:
    import psycopg  # psycopg 3

    def connect(dsn):
        return psycopg.connect(dsn)
except ImportError:
    try:
        import psycopg2

        def connect(dsn):
            return psycopg2.connect(dsn)
    except ImportError:
        sys.exit("Install psycopg first: pip install 'psycopg[binary]'")


def main(manifest_path, log_path="provenance.json"):
    dsn = os.environ.get("DATABASE_URL")
    if not dsn:
        sys.exit("Set DATABASE_URL to your warehouse connection string. Never hardcode it.")

    with open(manifest_path) as f:
        claims = json.load(f)

    rows = []
    provenance = []
    all_ok = True

    with connect(dsn) as conn:
        for c in claims:
            try:
                with conn.cursor() as cur:
                    cur.execute(c["query"])
                    result = cur.fetchone()
                value = None if result is None else result[0]
            except Exception as e:
                value = f"ERROR: {e}"

            passed = value is not None and not str(value).startswith("ERROR")
            all_ok = all_ok and passed
            rows.append((c["id"], str(c.get("display", "")), str(value), "ok" if passed else "FAIL"))
            provenance.append({
                "id": c["id"],
                "claim": c.get("claim", ""),
                "display": c.get("display", ""),
                "value": str(value),
                "query": c["query"],
                "pulled_at": datetime.datetime.now().isoformat(timespec="seconds"),
            })

    id_w = max((len(r[0]) for r in rows), default=8)
    print(f"{'claim id':<{id_w}}  {'on screen':<10}  {'warehouse':<16}  status")
    for rid, disp, val, status in rows:
        print(f"{rid:<{id_w}}  {disp:<10}  {val:<16}  {status}")

    with open(log_path, "w") as f:
        json.dump(provenance, f, indent=2)
    print(f"\nProvenance written to {log_path}")

    if not all_ok:
        sys.exit("\nValidation failed. Do not build the post until every claim returns a value.")
    print("\nAll claims returned a value. Confirm each display matches its warehouse value, then build.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage: python validate_claims.py claims.json [provenance.json]")
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "provenance.json")

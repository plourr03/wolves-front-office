"""Verify the Q0C cohort playoff outcomes against the warehouse.

The cohort ladder visualization (Article 1) draws each cohort team's playoff
finish. Before rendering, confirm every row against nba_games: regular-season
record and playoff wins/losses for the cohort season.

Fails loudly if .env is missing or the password is the placeholder.
"""
import os
from pathlib import Path

import pandas as pd
import psycopg2
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

if not os.environ.get("POSTGRES_PASSWORD") or "your" in os.environ.get("POSTGRES_PASSWORD", "").lower():
    raise SystemExit("POSTGRES_PASSWORD missing or placeholder. Fill in .env.")

# (season_start_year, team) -> the cohort season window
COHORT = [
    (2016, "PHX"), (2018, "NYK"), (2018, "SAC"), (2021, "PHI"),
    (2022, "CHI"), (2023, "PHX"), (2024, "SAC"), (2025, "MIN"),
]

canon = pd.read_csv(ROOT / "outputs/tables/q0c_historical_cohort/cohort_with_outcomes.csv")

conn = psycopg2.connect(
    host=os.environ["POSTGRES_HOST"], port=os.environ["POSTGRES_PORT"],
    dbname=os.environ["POSTGRES_DB"], user=os.environ["POSTGRES_USER"],
    password=os.environ["POSTGRES_PASSWORD"],
)
cur = conn.cursor()
cur.execute("SET search_path TO nba")

print(f"{'Season':<9}{'Team':<6}{'RS (wh)':<10}{'RS (canon)':<12}"
      f"{'PO W-L (wh)':<14}{'PO W-L (canon)':<16}{'Match'}")
print("-" * 78)

for syear, team in COHORT:
    # Season runs Sept of syear through Aug of syear+1.
    d0, d1 = f"{syear}-09-01", f"{syear + 1}-08-31"
    cur.execute(
        """
        SELECT season_type,
               COUNT(*) FILTER (WHERE (team_abbreviation = %(t)s AND wl = 'W')) AS wins,
               COUNT(*) FILTER (WHERE (team_abbreviation = %(t)s AND wl = 'L')) AS losses
        FROM nba_games
        WHERE team_abbreviation = %(t)s
          AND game_date BETWEEN %(d0)s AND %(d1)s
        GROUP BY season_type
        """,
        {"t": team, "d0": d0, "d1": d1},
    )
    rows = {st: (w, l) for st, w, l in cur.fetchall()}
    rs = rows.get("Regular Season", (0, 0))
    po = rows.get("Playoffs", (0, 0))

    c = canon[(canon.season_start_year == syear) & (canon.team_abbreviation == team)].iloc[0]
    rs_canon = c.rs_record
    po_canon = (int(c.playoff_wins), int(c.playoff_losses))

    rs_ok = f"{rs[0]}-{rs[1]}" == rs_canon
    po_ok = po == po_canon
    flag = "OK" if (rs_ok and po_ok) else "*** MISMATCH ***"

    print(f"{c.season_year:<9}{team:<6}{rs[0]}-{rs[1]:<8}{rs_canon:<12}"
          f"{po[0]}-{po[1]:<12}{po_canon[0]}-{po_canon[1]:<14}{flag}")

cur.close()
conn.close()

"""rosters_current: MIN + CHA rosters pulled at build time (spec 6.5), joined
to verified contracts and impact metrics, with the LaMelo-trade overlay.

Sources:
  Postgres nba.nba_team_rosters (latest snapshot)   roster membership, age
  offseason/data/nba_contracts_2026_27.csv          salary years (HoopsHype, verified)
  offseason/data/player_value.csv                   RAPM + B-Ref BPM triangulation
  lamelo/data/trade_definition.json                 the trade overlay

The trade is not league-official until the July moratorium lifts (~Jul 6),
so the warehouse snapshot is pre-trade. Rows carry roster_state:
  'pre_trade'  as pulled from the warehouse
  'post_trade' overlay applied (Randle+Reid out / LaMelo+Green+Gueye in for
               MIN; LaMelo+Green out / Reid in for CHA; Dosunmu added to MIN)
Engine D consumes post_trade rows. Re-pull at S5 to catch the official swap
plus any further offseason movement.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import duckdb
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = PROJECT_ROOT.parent
sys.path.insert(0, str(REPO_ROOT / "postmortem"))
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv

load_dotenv(REPO_ROOT / ".env")
from lib.db import query  # noqa: E402  (postmortem/lib/db.py)

TEAM_IDS = {"MIN": 1610612750, "CHA": 1610612766}
CONTRACTS = REPO_ROOT / "offseason" / "data" / "nba_contracts_2026_27.csv"
PLAYER_VALUE = REPO_ROOT / "offseason" / "data" / "player_value.csv"
TRADE_DEF = REPO_ROOT / "lamelo" / "data" / "trade_definition.json"
DB_PATH = PROJECT_ROOT / "data" / "warehouse.duckdb"

# name -> (new_team or None=departs). Applied on top of the warehouse snapshot.
def trade_moves() -> dict:
    td = json.loads(TRADE_DEF.read_text())
    return {
        "out_MIN": [p for p in td["min_net"]["players_out"]],
        "in_MIN": [p for p in td["min_net"]["players_in"]],
        "resigned_MIN": ["Ayo Dosunmu"],
        "out_CHA": ["LaMelo Ball", "Josh Green"],
        "in_CHA": ["Naz Reid"],
    }


def pull_rosters() -> pd.DataFrame:
    ids = tuple(TEAM_IDS.values())
    df = query(f"""
        SELECT team_abbreviation AS team, player, player_id AS nba_player_id,
               position, birth_date, age, experience, roster_date
        FROM nba_team_rosters
        WHERE team_id IN {ids}
          AND roster_date = (SELECT max(roster_date) FROM nba_team_rosters)
        ORDER BY team, player
    """)
    return df


def league_pool() -> pd.DataFrame:
    """Full latest-snapshot league pool, for sourcing incoming players'
    rows (LaMelo/Green/Gueye/Dosunmu arrive from other teams)."""
    return query("""
        SELECT team_abbreviation AS team, player, player_id AS nba_player_id,
               position, birth_date, age, experience, roster_date
        FROM nba_team_rosters
        WHERE roster_date = (SELECT max(roster_date) FROM nba_team_rosters)
    """)


def apply_trade(pre: pd.DataFrame, pool: pd.DataFrame) -> pd.DataFrame:
    mv = trade_moves()
    post = pre.copy()
    post = post[~((post.team == "MIN") & post.player.isin(mv["out_MIN"]))]
    post = post[~((post.team == "CHA") & post.player.isin(mv["out_CHA"]))]
    incoming = []
    for name, team in ([(n, "MIN") for n in mv["in_MIN"] + mv["resigned_MIN"]]
                       + [(n, "CHA") for n in mv["in_CHA"]]):
        src = pool[pool.player == name]
        if src.empty:
            print(f"WARNING: incoming player {name!r} not found in league pool")
            continue
        row = src.iloc[[0]].copy()
        row["team"] = team
        incoming.append(row)
    merged = pd.concat([post] + incoming, ignore_index=True)
    # idempotent vs snapshots that already reflect parts of the trade
    # (the 2026-07-01 snapshot already had Dosunmu on MIN -> duplicate row)
    return merged.drop_duplicates(["team", "player"], keep="first")


def enrich(df: pd.DataFrame) -> pd.DataFrame:
    contracts = pd.read_csv(CONTRACTS)
    ccols = ["nba_player_id", "salary_2026_27", "salary_2027_28", "salary_2028_29",
             "salary_2029_30", "years_remaining", "player_option_flag",
             "team_option_flag", "fa_status_2026"]
    value = pd.read_csv(PLAYER_VALUE)
    vcols = ["player_id", "net_rapm", "net_sd", "off_rapm", "def_rapm",
             "bbr_bpm", "bbr_mp", "consensus_net", "reliable"]
    out = (df.merge(contracts[ccols].drop_duplicates("nba_player_id"),
                    on="nba_player_id", how="left")
             .merge(value[vcols].rename(columns={"player_id": "nba_player_id"})
                    .drop_duplicates("nba_player_id"),
                    on="nba_player_id", how="left"))
    return out


def main():
    pre = pull_rosters()
    pool = league_pool()
    post = apply_trade(pre, pool)
    pre["roster_state"], post["roster_state"] = "pre_trade", "post_trade"
    roster_df = enrich(pd.concat([pre, post], ignore_index=True))
    con = duckdb.connect(str(DB_PATH))
    con.execute("CREATE OR REPLACE TABLE rosters_current AS SELECT * FROM roster_df")
    # full league snapshot persisted for the star-spells boundary rule:
    # roster membership is the "under contract with" evidence (dead money
    # from a waive-and-stretch has a cap charge but no roster row)
    con.execute("CREATE OR REPLACE TABLE league_rosters_snapshot AS SELECT * FROM pool")
    con.close()
    for state in ("pre_trade", "post_trade"):
        sub = roster_df[roster_df.roster_state == state]
        for team in ("MIN", "CHA"):
            t = sub[sub.team == team]
            n_val = t.net_rapm.notna().sum()
            print(f"{state} {team}: {len(t)} players, {n_val} with RAPM, "
                  f"{t.salary_2026_27.notna().sum()} with contracts")
    print("rosters_current loaded")


if __name__ == "__main__":
    main()

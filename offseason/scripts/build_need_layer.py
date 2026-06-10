#!/usr/bin/env python3
"""
build_need_layer.py

Component 3 inputs: a league-wide per-player profile across the six need
dimensions, and the Wolves returning-roster profile + need vector under each exit
scenario. The need vector is the gap between a playoff-calibrated contender
benchmark and the returning-roster profile, recomputed per scenario. The same
per-player dimension table is the target's profile in the acquisition metric, so
need-fit is a dot product in one shared space.

Dimensions (percentiles, league-wide over rotation players):
  hc_creation          half-court creation production (Synergy: poss x PPP)
  secondary_playmaking assist rate (advanced AST%)
  off_ball_shooting    made-3 volume per 36 (spacing)
  def_versatility_poa  ball pressure + overall D (STL/36 + inverted def RAPM)
  rim_protect_reb      rim protection + defensive boards (BLK/36 + DREB%)
  transition           transition production (Synergy: poss x PPP)

Scenarios: status_quo, randle_out, gobert_out, both_out. DiVincenzo's torn-Achilles
absence is baked into every returning roster. A departed (or absent) player's
minutes become a replacement-level hole (25th percentile), so losing a player
creates need exactly where he was strong.

Outputs:
  offseason/data/player_dimensions.csv   per-player six-dimension percentiles
  offseason/data/need_vectors.csv        scenario x dimension: profile, benchmark, need

    python build_need_layer.py
"""

import os
import sys
import csv
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
POSTMORTEM = os.path.abspath(os.path.join(HERE, "..", "..", "postmortem"))
DATA = os.path.join(HERE, "..", "data")

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(POSTMORTEM, ".env"))
except ImportError:
    pass
sys.path.insert(0, POSTMORTEM)
from lib import db  # noqa: E402

DIMS = ["hc_creation", "secondary_playmaking", "off_ball_shooting",
        "def_versatility_poa", "rim_protect_reb", "transition"]

# Playoff-calibrated contender benchmark (percentile space). Half-court creation,
# shooting, defensive versatility, and rim protection weighted higher because
# playoff series are decided in the half court against set, switching defenses.
BENCHMARK = {"hc_creation": 0.62, "secondary_playmaking": 0.55, "off_ball_shooting": 0.60,
             "def_versatility_poa": 0.60, "rim_protect_reb": 0.58, "transition": 0.52}
REPLACEMENT_PCTILE = 0.25     # a departed player's minutes are filled at replacement level
MIN_MINUTES = 1000            # universe for league percentiles (rotation players)

# Wolves 2026-27 returning rotation (DiVincenzo OUT: torn Achilles). Dosunmu re-signed.
WOLVES_ROTATION = {
    1630162: "Anthony Edwards", 203497: "Rudy Gobert", 203944: "Julius Randle",
    1630183: "Jaden McDaniels", 1629675: "Naz Reid", 1630245: "Ayo Dosunmu",
    201144: "Mike Conley", 1642866: "Joan Beringer", 1630545: "Terrence Shannon Jr.",
    1641740: "Jaylen Clark",
}
SCENARIO_REMOVE = {
    "status_quo": set(),
    "randle_out": {203944},
    "gobert_out": {203497},
    "both_out": {203944, 203497},
}


def pull_player_metrics():
    box = db.query("""
        SELECT player_id, SUM(minutes_played) min, SUM(fg3m) fg3m, SUM(stl) stl,
               SUM(blk) blk FROM nba_player_stats
        WHERE season_year IN ('2023-24','2024-25','2025-26')
        GROUP BY player_id HAVING SUM(minutes_played) >= %s""", (MIN_MINUTES,))
    adv = db.query("""
        SELECT person_id AS player_id,
               SUM(assist_percentage*minutes_float)/NULLIF(SUM(minutes_float),0) ast_pct,
               SUM(defensive_rebound_percentage*minutes_float)/NULLIF(SUM(minutes_float),0) dreb_pct
        FROM nba_player_advanced_stats
        WHERE game_id IN (SELECT DISTINCT game_id FROM nba_player_stats
                          WHERE season_year IN ('2023-24','2024-25','2025-26'))
        GROUP BY person_id""")
    trans = db.query("""
        SELECT player_id, SUM(poss) tr_poss, SUM(pts) tr_pts
        FROM nba_synergy_player_play_types
        WHERE play_type='Transition' AND season_type='Regular Season'
          AND season_year IN ('2023-24','2024-25','2025-26')
        GROUP BY player_id""")
    df = box.merge(adv, on="player_id", how="left").merge(trans, on="player_id", how="left")

    pt = pd.read_csv(os.path.join(DATA, "playoff_translation.csv"))[
        ["player_id", "hc_ppp_rs", "hc_poss_rs", "spotup_ppp_rs"]]
    pv = pd.read_csv(os.path.join(DATA, "player_value.csv"))[["player_id", "def_rapm"]]
    df = df.merge(pt, on="player_id", how="left").merge(pv, on="player_id", how="left")

    m = df["min"].clip(lower=1)
    df["fg3m36"] = df["fg3m"] / m * 36
    df["stl36"] = df["stl"] / m * 36
    df["blk36"] = df["blk"] / m * 36
    df["hc_prod"] = (df["hc_ppp_rs"].fillna(0) * df["hc_poss_rs"].fillna(0))
    df["tr_prod"] = (df["tr_pts"].fillna(0))           # transition points produced
    df["def_value"] = -df["def_rapm"].fillna(df["def_rapm"].median())   # higher = better D
    return df


def pct(s):
    return s.rank(pct=True)


def build_dimensions(df):
    out = pd.DataFrame({"player_id": df["player_id"]})
    out["hc_creation"] = pct(df["hc_prod"])
    out["secondary_playmaking"] = pct(df["ast_pct"].fillna(0))
    out["off_ball_shooting"] = pct(df["fg3m36"])
    out["def_versatility_poa"] = 0.5 * pct(df["stl36"]) + 0.5 * pct(df["def_value"])
    out["rim_protect_reb"] = 0.5 * pct(df["blk36"]) + 0.5 * pct(df["dreb_pct"].fillna(0))
    out["transition"] = pct(df["tr_prod"])
    # re-percentile the two composites so all dims live on a 0-1 percentile scale
    out["def_versatility_poa"] = pct(out["def_versatility_poa"])
    out["rim_protect_reb"] = pct(out["rim_protect_reb"])
    return out


def wolves_minutes():
    mins = db.query("""SELECT player_id, SUM(minutes_played) min FROM nba_player_stats
                       WHERE season_year='2025-26' AND player_id = ANY(%s)
                       GROUP BY player_id""", (list(WOLVES_ROTATION),))
    return dict(zip(mins["player_id"], mins["min"]))


def scenario_profiles(dims):
    dim_map = {int(r["player_id"]): r for _, r in dims.iterrows()}
    base_min = wolves_minutes()
    # DiVincenzo already excluded from WOLVES_ROTATION; everyone here is a returner
    rows = []
    for scen, removed in SCENARIO_REMOVE.items():
        present = {pid: m for pid, m in base_min.items() if pid in WOLVES_ROTATION}
        total = sum(present.values())
        gap = sum(m for pid, m in present.items() if pid in removed)
        kept = {pid: m for pid, m in present.items() if pid not in removed}
        profile = {}
        for d in DIMS:
            val = sum((m / total) * dim_map[pid][d] for pid, m in kept.items() if pid in dim_map)
            val += (gap / total) * REPLACEMENT_PCTILE          # the hole, at replacement
            profile[d] = val
        for d in DIMS:
            need = BENCHMARK[d] - profile[d]
            rows.append({"scenario": scen, "dimension": d,
                         "team_profile": round(profile[d], 3),
                         "benchmark": BENCHMARK[d],
                         "need": round(need, 3),
                         "is_need": "TRUE" if need > 0.05 else "FALSE"})
    return rows


def main():
    df = pull_player_metrics()
    dims = build_dimensions(df)
    dims.round(3).to_csv(os.path.join(DATA, "player_dimensions.csv"), index=False)
    print(f"player_dimensions.csv: {len(dims)} players x {len(DIMS)} dims")

    needs = scenario_profiles(dims)
    fields = ["scenario", "dimension", "team_profile", "benchmark", "need", "is_need"]
    with open(os.path.join(DATA, "need_vectors.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader(); w.writerows(needs)
    print(f"need_vectors.csv: {len(SCENARIO_REMOVE)} scenarios x {len(DIMS)} dims\n")

    nd = pd.DataFrame(needs)
    for scen in SCENARIO_REMOVE:
        sub = nd[nd["scenario"] == scen].sort_values("need", ascending=False)
        top = sub.iloc[0]
        gaps = ", ".join(f"{r['dimension']}({r['need']:+.2f})" for _, r in sub.iterrows() if r["need"] > 0.05)
        print(f"  {scen:11}: top need = {top['dimension']} ({top['need']:+.2f}) | needs: {gaps or 'none > 0.05'}")


if __name__ == "__main__":
    main()

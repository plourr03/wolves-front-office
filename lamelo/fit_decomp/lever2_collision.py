"""
Lever 2: the Ant-LaMelo usage collision. For each high-usage two-initiator duo, measure the
two-man on-court OFFENSIVE synergy from the possession cache: offensive rating when BOTH are on
vs when only the better individual is on. Synergy = both_on - max(A_only, B_only). Positive =
the pairing elevates beyond either alone; negative = a collision (two ball-dominant players who
cannot both have it). Then place Edwards-LaMelo by PROFILE (their two-man does not exist yet),
honestly, against the successes and the failures.

Clean possession-level data (2023-26 cache) is weighted heavily per the plan; older duos would
need a coarser proxy and are out of scope here (most of the core set is in-window).
"""
from __future__ import annotations
import glob, os, sys
from pathlib import Path
import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
CACHE = REPO / "offseason" / "data" / "cache" / "possessions_league"
sys.path.insert(0, str(REPO / "postmortem" / "lib"))
import db  # noqa: E402

# duo: (label, idA, idB) ; classification hint is NOT used in the math, only for display
DUOS = [
    ("Doncic-Irving (DAL)", 1629029, 202681),
    ("Mitchell-Garland (CLE)", 1628378, 1629636),
    ("Morant-Bane (MEM)", 1629630, 1630217),
    ("Fox-DeRozan (SAC)", 1628368, 201942),
    ("Young-Murray (ATL)", 1629027, 1627749),
    ("Booker-Beal (PHX)", 1626164, 203078),
]
ANT, LAMELO = 1630162, 1630163


def load_cache():
    files = sorted(glob.glob(str(CACHE / "*.parquet")))
    df = pd.concat([pd.read_parquet(f, columns=["off_players_str", "points_scored"]) for f in files],
                   ignore_index=True)
    df["_s"] = "," + df["off_players_str"].astype(str) + ","
    return df


def ortg(df, mask):
    n = int(mask.sum())
    return (df.loc[mask, "points_scored"].sum() / n * 100.0 if n else float("nan")), n


def main():
    print("loading possession cache ...", flush=True)
    df = load_cache()
    print(f"  {len(df):,} possessions", flush=True)
    rows = []
    for label, a, b in DUOS:
        ma = df["_s"].str.contains(f",{a},", regex=False)
        mb = df["_s"].str.contains(f",{b},", regex=False)
        both, n_both = ortg(df, ma & mb)
        aonly, n_a = ortg(df, ma & ~mb)
        bonly, n_b = ortg(df, mb & ~ma)
        syn = both - max(aonly, bonly)
        rows.append((label, both, n_both, aonly, n_a, bonly, n_b, syn))
    print(f"\n{'duo':24}{'both_on':>9}{'(poss)':>9}{'A_only':>8}{'B_only':>8}{'synergy':>9}")
    for label, both, nb, ao, na, bo, n_b, syn in rows:
        print(f"{label:24}{both:>9.1f}{nb:>9,}{ao:>8.1f}{bo:>8.1f}{syn:>+9.1f}")

    # usage context (are they duplicative on-ball, or is one complementary?)
    ids = [x for _, a, b in DUOS for x in (a, b)] + [ANT, LAMELO]
    usg = db.query("""SELECT a.person_id pid,
                      ROUND((SUM(a.usage_percentage*a.minutes_float)/NULLIF(SUM(a.minutes_float),0))::numeric,3) usg
                      FROM nba_player_advanced_stats a
                      JOIN nba_player_stats ps ON ps.game_id=a.game_id AND ps.player_id=a.person_id
                      WHERE a.person_id = ANY(%s) AND ps.season_year IN ('2024-25','2025-26')
                      GROUP BY a.person_id""", (ids,))
    u = dict(zip(usg.pid, usg.usg.astype(float)))
    print("\n=== usage (2024-25/25-26), duplication check ===")
    for label, a, b in DUOS:
        print(f"  {label:24} {u.get(a,0):.2f} / {u.get(b,0):.2f}  (both high = duplicative)")
    print(f"  {'Edwards-LaMelo (target)':24} {u.get(ANT,0):.2f} / {u.get(LAMELO,0):.2f}")


if __name__ == "__main__":
    main()

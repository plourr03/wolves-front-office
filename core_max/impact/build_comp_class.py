#!/usr/bin/env python3
"""Phase 2 (FROZEN spec v1.1): Joan's comp-class membership + the within-class input profile.

Membership is STRUCTURAL only (no production-stat filter), so this computes WHO is in the
class and reports N plus the pre-committed input-profile transparency check (where Joan's
314 rookie minutes sit in the class, plus draft and age spreads), making reference-class
dilution visible BEFORE any outcome is computed. See core_max/docs/phase2_plan.md.

    python core_max/impact/build_comp_class.py
"""
import os
import sys
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "postmortem"))
from lib import db  # noqa: E402

SMB = os.path.join(REPO, "offseason", "data", "cache", "season_min_blk_2001_2026.csv")
OUTDIR = os.path.join(REPO, "core_max", "outputs", "phase2")
FROZEN = os.path.join(REPO, "core_max", "data_frozen", "phase2_draft_bio.parquet")
JOAN_PID = 1642866

# FROZEN membership bands (phase2_plan.md v1.1)
DRAFT_LO, DRAFT_HI = 9, 25
AGE_LO, AGE_HI = 18, 21
MIN_LO, MIN_HI = 100, 1200
ROOKIE_LO, ROOKIE_HI = 2001, 2020            # rookie-season start year (>= 5 forward seasons)
BIG_POS = {"C", "C-F", "F-C", "Center", "Center-Forward", "Forward-Center"}


def season_start(s):
    return int(str(s)[:4])


def pull_draft_bio(player_ids):
    """Static, immutable per-player draft slot + listed position. Cached (frozen) on first pull."""
    if os.path.exists(FROZEN):
        return pd.read_parquet(FROZEN)
    ids = [int(p) for p in player_ids]
    draft = db.query("SELECT player_id, draft_number FROM nba_player_season_bio "
                     "WHERE player_id = ANY(%s) AND draft_number IS NOT NULL", (ids,))
    draft = draft.groupby("player_id")["draft_number"].max().reset_index()
    pos = db.query("SELECT player_id, position FROM nba_player_bio WHERE player_id = ANY(%s)", (ids,))
    df = draft.merge(pos, on="player_id", how="outer")
    os.makedirs(os.path.dirname(FROZEN), exist_ok=True)
    df.to_parquet(FROZEN, index=False)
    return df


def is_big(p):
    return str(p).strip() in BIG_POS


def main():
    smb = pd.read_csv(SMB)
    smb["season_start"] = smb["season"].map(season_start)
    rookie = smb.loc[smb.groupby("PLAYER_ID")["season_start"].idxmin()].copy()   # earliest season per player
    bio = pull_draft_bio(smb["PLAYER_ID"].unique())
    print("distinct positions in bio:", sorted(set(str(x) for x in bio["position"].dropna().unique()))[:20])

    m = rookie.merge(bio, left_on="PLAYER_ID", right_on="player_id", how="left")
    m["draft_number"] = pd.to_numeric(m["draft_number"], errors="coerce")

    cls = m[
        m["position"].apply(is_big)
        & m["draft_number"].between(DRAFT_LO, DRAFT_HI)
        & m["AGE"].between(AGE_LO, AGE_HI)
        & m["MIN"].between(MIN_LO, MIN_HI)
        & m["season_start"].between(ROOKIE_LO, ROOKIE_HI)
    ].copy()
    cls = cls[cls["PLAYER_ID"] != JOAN_PID]

    print("=" * 70)
    print(f"COMP CLASS N = {len(cls)}   (Joan's frozen reference class)")
    print("=" * 70)
    joan = smb[smb["PLAYER_ID"] == JOAN_PID].sort_values("season_start").iloc[0]
    jmin = float(joan["MIN"])
    print(f"Joan rookie (2025-26): age {joan['AGE']:.0f}, MIN {jmin:.0f} (7.9 mpg), draft #17")

    print("\nWITHIN-CLASS INPUT PROFILE (dilution transparency check):")
    for col, lab, jv in [("MIN", "rookie minutes", jmin),
                         ("draft_number", "draft slot", 17.0),
                         ("AGE", "rookie age", float(joan["AGE"]))]:
        q = cls[col].quantile([0, .25, .5, .75, 1.0])
        print(f"  {lab:14s}: min {q[0]:.0f} | p25 {q[.25]:.0f} | median {q[.5]:.0f} | "
              f"p75 {q[.75]:.0f} | max {q[1.0]:.0f}   (Joan {jv:.0f})")
    pct = float((cls["MIN"] < jmin).mean()) * 100
    hi = float((cls["MIN"] >= 800).mean()) * 100
    print(f"  Joan's {jmin:.0f} rookie minutes sit at the {pct:.0f}th percentile of the class")
    print(f"  share of class with rookie MIN >= 800 (rotation-role rookies): {hi:.0f}% "
          f"(if high, the ceiling diluted Joan's reference class -> re-registration, not a silent edit)")

    os.makedirs(OUTDIR, exist_ok=True)
    out = cls[["PLAYER_ID", "PLAYER_NAME", "season", "AGE", "MIN", "draft_number", "position"]]
    out = out.sort_values("MIN")
    out.to_csv(os.path.join(OUTDIR, "comp_class.csv"), index=False)
    print(f"\nwrote {os.path.join(OUTDIR, 'comp_class.csv')} ({len(out)} comps)")
    print("\nthe lowest-minute (most Joan-like) comps:")
    for _, r in out.head(8).iterrows():
        nm = str(r["PLAYER_NAME"]).encode("ascii", "replace").decode()
        print(f"  {nm[:24]:24s} {r['season']} age {r['AGE']:.0f} MIN {r['MIN']:.0f} pick {r['draft_number']:.0f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

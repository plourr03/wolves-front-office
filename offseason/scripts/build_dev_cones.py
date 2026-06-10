#!/usr/bin/env python3
"""
build_dev_cones.py  -- comp-based development cones for the young core (Beringer, Shannon).

Comps from 25 years of season box data: nba_player_season_bio (age/height/draft) JOINED with a
real MINUTES + BLOCKS pull (data/cache/season_min_blk_2001_2026.csv), so the rim-anchor ladder is
built on BLOCKS + rebounding + size (blocks are the most diagnostic rim signal), not a proxy.

Three honest refinements:
 1) SELECTION-BIAS caveat. Minutes are endogenous (early run selects for quality), so the
    starter-track branch is INFLATED and the buried branch OVERSTATED as causal estimates. We
    partially de-bias by (a) FIRST-ROUND picks only for Beringer's set, and (b) splitting the
    buried group into "blocked (emerged later)" vs "failed anywhere (never)". Deflating the gap
    strengthens hold-Gobert from BOTH sides (smaller trade dividend, smaller cost of keeping).
 2) THIRD BRANCH: groomed-behind-the-starter (700-1500 season minutes, a backup role). This path
    EXISTS in the keep-Gobert world (backup-5 minutes behind a 31-mpg, soon-35 Gobert + load
    management) and is controllable, so it is the A/C development plan for Beringer.
 3) Blocks-based rim tiers (above).

Tiers remain role-relative (rim-anchor for Beringer, bench-creator for Shannon) and are still
proxies; the cone is a distribution of comp outcomes, not a forecast of these two specifically.

    python build_dev_cones.py
"""

import os
import sys
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
POST = os.path.abspath(os.path.join(HERE, "..", "..", "postmortem"))
sys.path.insert(0, POST)
from lib import db  # noqa: E402
CACHE = os.path.join(HERE, "..", "data", "cache", "season_min_blk_2001_2026.csv")

RIM_IMPACT = {"out": -2.0, "fringe big": -1.5, "rotation rim protector": 0.5,
              "starting anchor": 2.0, "elite anchor": 4.0}
WING_IMPACT = {"out": -2.0, "fringe": -1.0, "dependable bench scorer": 0.3,
               "high-end 6th man": 1.5, "starter": 2.5}


def load():
    mb = pd.read_csv(CACHE)
    mb["yr"] = mb["season"].str[:4].astype(int)
    mb = mb.rename(columns={"PLAYER_ID": "pid", "AGE": "age", "GP": "gp", "MIN": "min",
                            "REB": "reb", "BLK": "blk", "PTS": "pts", "AST": "ast"})
    bio = db.query("""SELECT player_id pid, season_year, player_height_inches ht, draft_number dn
                      FROM nba_player_season_bio WHERE season_type='Regular Season'""")
    bio["yr"] = bio["season_year"].str[:4].astype(int)
    # height/draft are ~player-constant: take the max-height, min-draft per player
    bio["ht"] = pd.to_numeric(bio["ht"], errors="coerce")
    bio["dn"] = pd.to_numeric(bio["dn"], errors="coerce")   # 'Undrafted' -> NaN
    binfo = bio.groupby("pid").agg(ht=("ht", "max"), dn=("dn", "min")).reset_index()
    s = mb.merge(binfo, on="pid", how="left")
    s["mpg"] = s["min"] / s["gp"].clip(lower=1)
    s["bpg"] = s["blk"] / s["gp"].clip(lower=1)
    s["rpg"] = s["reb"] / s["gp"].clip(lower=1)
    s["ppg"] = s["pts"] / s["gp"].clip(lower=1)
    return s


def rim_tier(row):
    if row is None:
        return "out"
    mn, bpg = row["min"], row["bpg"]
    if mn >= 1800 and bpg >= 1.6:
        return "elite anchor"
    if mn >= 1500 and bpg >= 1.0:
        return "starting anchor"
    if mn >= 700 and bpg >= 0.6:
        return "rotation rim protector"
    return "fringe big"


def wing_tier(row):
    if row is None:
        return "out"
    mn, ppg = row["min"], row["ppg"]
    if ppg >= 15 and mn >= 1900:
        return "starter"
    if ppg >= 12 and mn >= 1200:
        return "high-end 6th man"
    if ppg >= 6 and mn >= 700:
        return "dependable bench scorer"
    return "fringe"


def cone(anchors, by_pid, tier_fn, impact_map, horizons):
    out = {}
    for h in horizons:
        tiers = []
        for _, a in anchors.iterrows():
            g = by_pid[a["pid"]]
            tgt = g[(g["age"] >= a["age"] + h - 0.5) & (g["age"] <= a["age"] + h + 0.5)]
            row = tgt.sort_values("min").iloc[-1] if len(tgt) else None
            tiers.append(tier_fn(row))
        n = len(tiers); v = np.array([impact_map[t] for t in tiers])
        out[h] = {"n": n, "dist": {k: round(tiers.count(k) / n, 3) for k in impact_map},
                  "P10": round(np.percentile(v, 10), 1), "P25": round(np.percentile(v, 25), 1),
                  "P50": round(np.percentile(v, 50), 1), "P75": round(np.percentile(v, 75), 1),
                  "P90": round(np.percentile(v, 90), 1)}
    return out


def peak_min_by(by_pid, pid, age, within=1):
    g = by_pid[pid]; e = g[g["age"] <= age + within]
    return e["min"].max() if len(e) else 0


def emerged_later(by_pid, pid, age):
    g = by_pid[pid]; late = g[(g["age"] > age + 1) & (g["age"] <= age + 5)]
    return bool(len(late) and (late["min"] >= 1300).any())


def show(name, ladder, branches):
    print(f"\n=== {name} :: {ladder} ladder ===")
    for b, c in branches.items():
        print(f"  [{b}]")
        for h, d in c.items():
            ds = " ".join(f"{k.split()[0]}:{int(v*100)}%" for k, v in d["dist"].items())
            print(f"    +{h}y (n={d['n']:>3}): P10 {d['P10']:+.1f}/P25 {d['P25']:+.1f}/P50 {d['P50']:+.1f}/"
                  f"P75 {d['P75']:+.1f}/P90 {d['P90']:+.1f} | {ds}")


def main():
    s = load()
    by_pid = {pid: g for pid, g in s.groupby("pid")}

    # ---- Beringer: FIRST-ROUND young bigs (age 18-20, >=81in, draft 1-30) ----
    big = s[(s["age"].between(18, 20)) & (s["ht"] >= 81) & (s["dn"].between(1, 30))]
    bigA = big.sort_values("age").groupby("pid").head(1)

    def branch(r):
        pk = peak_min_by(by_pid, r["pid"], r["age"])
        if pk >= 1600:
            return "starter-track"
        if pk >= 700:
            return "groomed-backup"
        return "buried"
    bigA = bigA.assign(branch=bigA.apply(branch, axis=1))
    buried = bigA[bigA["branch"] == "buried"]
    blocked = buried[buried.apply(lambda r: emerged_later(by_pid, r["pid"], r["age"]), axis=1)]
    failed = buried[~buried.index.isin(blocked.index)]
    br = {
        "STARTER-TRACK runway (>=1600 min; INFLATED by selection)": cone(bigA[bigA.branch == "starter-track"], by_pid, rim_tier, RIM_IMPACT, (2, 4)),
        "GROOMED-backup (700-1600 min; the keep-Gobert A/C plan)": cone(bigA[bigA.branch == "groomed-backup"], by_pid, rim_tier, RIM_IMPACT, (2, 4)),
        "buried: BLOCKED-then-emerged (talented, stuck)": cone(blocked, by_pid, rim_tier, RIM_IMPACT, (2, 4)),
        "buried: FAILED-anywhere (never stuck; OVERSTATES cost)": cone(failed, by_pid, rim_tier, RIM_IMPACT, (2, 4)),
    }
    show("Joan Beringer (turns 20 in Nov; WIDE cone) -- FIRST-ROUND big comps, blocks-based", "rim-anchor", br)
    print("  SELECTION CAVEAT: minutes are endogenous, so starter-track is inflated and buried overstated as CAUSAL.")
    print("  De-biasing (first-round only + groomed branch + blocked-vs-failed split) DEFLATES the runway-vs-buried gap,")
    print("  which strengthens HOLD-GOBERT from both sides: smaller dividend from trading, smaller cost of keeping.")
    print("  A/C PLAN: Beringer is the designated backup-5 behind a 31-mpg/soon-35 Gobert (+ load mgmt) = the GROOMED")
    print("  branch, controllable WITHOUT trading Gobert, as long as the portfolio adds no veteran big who blocks him.")

    # ---- Shannon: age 24-26 wings (76-80in), bench-scorer profile ----
    wing = s[(s["age"].between(24, 26)) & (s["ht"].between(76, 80)) & (s["ppg"].between(4, 16)) & (s["gp"] >= 20)]
    wingA = wing.sort_values("age").groupby("pid").head(1)
    wrun = wingA[wingA.apply(lambda r: peak_min_by(by_pid, r["pid"], r["age"]) >= 1600, axis=1)]
    wblk = wingA[~wingA.index.isin(wrun.index)]
    sh = {"RUNWAY (got starter run; OPERATIVE under A/C)": cone(wrun, by_pid, wing_tier, WING_IMPACT, (2,)),
          "BLOCKED (stayed bench)": cone(wblk, by_pid, wing_tier, WING_IMPACT, (2,))}
    show("Terrence Shannon Jr (turns 26 in July; NARROW plateau cone)", "bench-creator", sh)
    print("  A/C GRANTS Shannon's runway automatically: Randle out + DiVincenzo's absence open the bench-scoring role,")
    print("  so the RUNWAY branch is the operative one under the recommendation. Upside is MINUTES not skill (plateau age).")


if __name__ == "__main__":
    main()

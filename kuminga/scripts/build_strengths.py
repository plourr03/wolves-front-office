#!/usr/bin/env python3
"""Item 8b: turn the mechanical rotations into 2026-27 team strengths, all 30 teams,
all four views.

    net_2026_27 = regress_to_expectation(measured 2025-26 net)
                + beta * (rollup_current - rollup_baseline)

The anchor is measured reality. The move is the modelled roster change. Because both
rollups come from the SAME minutes heuristic, the heuristic's level bias cancels in
the difference and only the roster change survives. `deflate` is affine
(alpha + beta*x), so the alpha cancels too and the delta is beta * (hot difference).

Baseline (R6) is the 2025-26 end-of-season roster with no injuries, which by
construction gives rollup_current == rollup_baseline and therefore
net = regress_to_expectation(measured). That is the "nobody did anything" field the
offseason is measured against.

FOUR VIEWS (R1), carried separately end to end, never averaged:
  consensus  the in-house triangulated spine
  rapm       the possession-based view that can see defense
  box        the box-score prior, which mostly cannot
  darko      the external anchor (darko.app, retrieved 2026-06-10)

    python kuminga/scripts/build_strengths.py
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "offseason", "scripts"))

from kuminga.lib import kfreeze, runlog  # noqa: E402
import build_team_ratings as A           # noqa: E402
import bracket_sim as E                  # noqa: E402

ROT = os.path.join(REPO, "kuminga", "outputs", "rotations_2026_27.csv")
VALUE = os.path.join(REPO, "offseason", "data", "player_value.csv")
DARKO = os.path.join(REPO, "offseason", "data", "darko-dpm-leaderboard.csv")
OUT = os.path.join(REPO, "kuminga", "outputs", "team_strengths_2026_27.csv")

FORKS = ["consensus", "rapm", "box", "darko"]


def nkey(name) -> str:
    import re
    import unicodedata
    s = str(name)
    try:
        s = s.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        pass
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    drop = {"jr", "jr.", "sr", "sr.", "ii", "iii", "iv"}
    s = " ".join(t for t in s.split() if t not in drop)
    return re.sub(r"[^a-z0-9]+", "", s)


def build_impacts(value: pd.DataFrame, darko: pd.DataFrame, bio: pd.DataFrame) -> dict:
    """One {player_id_str: {off, def, off_sd, def_sd, def_div, read}} per fork.

    Sign convention, verified against the value file itself: net = off - def, so a
    NEGATIVE def is good defense (points prevented). DARKO publishes DDPM with
    positive = better defense, so it is negated to match.
    """
    imps = {f: {} for f in FORKS}
    for _, r in value.iterrows():
        pid = str(int(r.player_id))
        common = dict(off_sd=float(r.off_sd), def_sd=float(r.def_sd),
                      def_div=float(r.def_divergence) if pd.notna(r.def_divergence) else 0.0,
                      read=r.translation_read if isinstance(r.translation_read, str) else "")
        imps["consensus"][pid] = dict(off=float(r.consensus_off), def_=float(r.consensus_def), **common)
        imps["rapm"][pid] = dict(off=float(r.off_rapm), def_=float(r.def_rapm), **common)
        imps["box"][pid] = dict(off=float(r.box_off_prior), def_=float(r.box_def_prior), **common)

    # DARKO: map by normalised name against the bio dimension.
    bio_k = bio.copy()
    bio_k["k"] = bio_k.player_name.map(nkey)
    k2id = bio_k.drop_duplicates("k").set_index("k").player_id.to_dict()
    matched = 0
    for _, r in darko.iterrows():
        pid = k2id.get(nkey(r["Player"]))
        if pid is None:
            continue
        pid = str(int(pid))
        base = imps["consensus"].get(pid, {})
        imps["darko"][pid] = dict(
            off=float(r["ODPM"]), def_=-float(r["DDPM"]),
            off_sd=base.get("off_sd", 1.2), def_sd=base.get("def_sd", 1.2),
            def_div=base.get("def_div", 0.0), read=base.get("read", ""))
        matched += 1

    # rollup() expects the key "def"; build with def_ then rename to avoid the keyword.
    for f in FORKS:
        for pid, d in imps[f].items():
            d["def"] = d.pop("def_")
    return imps, matched


def add_rookie_impacts(imps: dict, pool: pd.DataFrame) -> int:
    """Give the 2026 rookies (synthetic negative ids) an impact in every fork.

    They have no measured value in any of the four views, so all four get the SAME
    draft-slot prior that build_rotations fitted on the 2025 class. The prior is split
    evenly between offence and defence (off = net/2, def = -net/2, so off - def = net)
    because nothing in the data says which side it belongs on. Their uncertainty is set
    wide deliberately: a slot prior is a guess.
    """
    n = 0
    for _, x in pool[pool.player_id < 0].drop_duplicates("player_id").iterrows():
        pid = str(int(x.player_id))
        net = float(x.consensus_net)
        for f in FORKS:
            if pid in imps[f]:
                continue
            imps[f][pid] = dict(off=net / 2.0, **{"def": -net / 2.0},
                                off_sd=2.0, def_sd=2.0, def_div=0.0, read="")
            n += 1
    return n


def main():
    with runlog.run("build_strengths", inputs={"rotations": ROT,
                                               "snapshot": kfreeze.current_snapshot_id()}) as r:
        rot = pd.read_csv(ROT)
        value = pd.read_csv(VALUE)
        darko = pd.read_csv(DARKO)
        darko.columns = [c.strip().lstrip("﻿") for c in darko.columns]
        bio, sid = kfreeze.load("player_bio")
        tn, _ = kfreeze.load("team_net", sid)
        for c in ("net_rating", "off_rating", "def_rating", "pace"):
            tn[c] = pd.to_numeric(tn[c], errors="coerce")

        imps, n_darko = build_impacts(value, darko, bio)
        n_rook = add_rookie_impacts(imps, rot)
        r.note(f"2026 rookies given a slot-prior impact in every fork: {n_rook // len(FORKS)}")
        for f in FORKS:
            r.note(f"impact fork '{f}': {len(imps[f])} players")
        r.note(f"DARKO name-matched: {n_darko} of {len(darko)}")

        # season_start_year: the 2025-26 season is 2025. Using 2026 silently returns
        # an empty frame, which is how this was first written.
        measured = (tn[(tn.season_start_year == 2025) & (tn.season_type == "Regular Season")]
                    .set_index("team_abbr").net_rating.to_dict())
        r.note(f"measured 2025-26 RS net available for {len(measured)} teams")

        p = E.load_e_params()
        beta = float(p["beta"])
        r.note(f"deflate beta = {beta}; persist slope = {p['persist_slope']}, "
               f"int = {p['persist_int']}")

        rows = []
        for fork in FORKS:
            imp = imps[fork]
            for team in sorted(rot.team_abbr.unique()):
                roll = {}
                for scen in ("baseline", "current"):
                    g = rot[(rot.scenario == scen) & (rot.team_abbr == team)]
                    mpg = {str(int(x.player_id)): float(x.mpg)
                           for _, x in g.iterrows() if pd.notna(x.player_id)}
                    roll[scen] = A.rollup(mpg, imp, "rs")
                    # coverage: how much of the rotation the fork can actually value
                    covered = sum(m for pid, m in mpg.items() if pid in imp)
                    roll[scen]["coverage"] = covered / 240.0

                m25 = measured.get(team)
                exp = E.regress_to_expectation(m25) if m25 is not None else 0.0
                delta = beta * (roll["current"]["net"] - roll["baseline"]["net"])

                rows.append(dict(
                    fork=fork, team_abbr=team,
                    measured_net_2025_26=m25,
                    exp_2026_27=exp,
                    hot_baseline=roll["baseline"]["net"],
                    hot_current=roll["current"]["net"],
                    delta_net=delta,
                    net_baseline=exp,
                    net_current=exp + delta,
                    net_sd=roll["current"]["net_sd"],
                    munc=roll["current"]["method_uncertainty"],
                    coverage_baseline=roll["baseline"]["coverage"],
                    coverage_current=roll["current"]["coverage"],
                    conf=E.TEAM_CONF.get(team, "W"),
                ))

        df = pd.DataFrame(rows)
        df.to_csv(OUT, index=False)
        r.note(f"strengths: {len(df)} rows ({df.fork.nunique()} forks x {df.team_abbr.nunique()} teams)")
        for f in FORKS:
            s = df[df.fork == f]
            r.note(f"  {f}: mean coverage {s.coverage_current.mean():.3f}, "
                   f"delta range [{s.delta_net.min():+.2f}, {s.delta_net.max():+.2f}]")
        r.output(OUT, rows=len(df))

    print()
    piv = df.pivot_table(index="team_abbr", columns="fork", values="delta_net").round(2)
    piv["mean"] = piv.mean(axis=1).round(2)
    print("2026-27 net-rating delta from the offseason, by fork (positive = improved):")
    print(piv.sort_values("mean", ascending=False).to_string())


if __name__ == "__main__":
    main()

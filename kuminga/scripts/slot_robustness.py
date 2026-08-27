#!/usr/bin/env python3
"""S2: how much of the C3 finding depends on WHO fills the 4.

THE RULE THAT PUT SHANNON IN THE POOL. C3 defines eligible-at-the-4 as

    ("Forward" in listed_position) and not listed_position.startswith("Center")

Terrence Shannon Jr. is listed **Guard-Forward**. That contains "Forward" and is not
centre-first, so he qualified. Note this is a DIFFERENT rule from the position-pool
rule added for S1, which keys on the PRIMARY listing and therefore makes Shannon a
guard. The two rules disagree about exactly the one player C3's answer turned on,
which is why this robustness pass exists.

WHY LYLES WAS NOT THE FILL. Trey Lyles is listed Forward and is eligible under both
rules. He was not the fill because he had no headroom: his prior load is 6.0 minutes,
so his ceiling is 6.0 + 3 = 9.0, and the ceilinged rotation already had him at exactly
9.0. Room = 0.0. The same is true of Joan Beringer (prior 7.85, ceiling 10.85, already
at 10.85). Jaden McDaniels had 2.7 minutes of room and took them. Everything left had
to go to the next eligible body with headroom, and under the C3 rule that was Shannon.

WHAT THIS SCRIPT DOES. Re-prices Kuminga's marginal contribution under five different
answers to "who fills the 4", including two that force a named player past his ceiling,
because "if Lyles were the fill" is a question about a hypothetical role, not about
last season's minutes.

    python kuminga/scripts/slot_robustness.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "offseason", "scripts"))
sys.path.insert(0, HERE)

from kuminga.lib import kfreeze, rotation, runlog  # noqa: E402
import build_team_ratings as A                     # noqa: E402
import bracket_sim as E                            # noqa: E402
from build_strengths import build_impacts, add_rookie_impacts  # noqa: E402

POOL = os.path.join(REPO, "kuminga", "outputs", "player_pool_2026_27.csv")
ROT = os.path.join(REPO, "kuminga", "outputs", "rotations_2026_27.csv")
FCURVE = os.path.join(REPO, "kuminga", "outputs", "fcurve_min.csv")
STR = os.path.join(REPO, "kuminga", "outputs", "team_strengths_2026_27.csv")
VALUE = os.path.join(REPO, "offseason", "data", "player_value.csv")
DARKO = os.path.join(REPO, "offseason", "data", "darko-dpm-leaderboard.csv")
OUT = os.path.join(REPO, "kuminga", "outputs", "slot_robustness.csv")

FORKS = ["consensus", "rapm", "box", "darko"]
KUMINGA_ID = "1630228"
FORCED_CEILING = 36.0     # a named filler may be pushed to a full starter's load


def c3_eligible(p):
    p = str(p or "")
    return ("Forward" in p) and (not p.startswith("Center"))


def tight_eligible(p):
    """S2's tighter rule: only Forward or Forward-Centre listings."""
    return str(p or "") in ("Forward", "Forward-Center")


def main():
    with runlog.run("slot_robustness", inputs={"variants": 5}) as r:
        pool = pd.read_csv(POOL)
        rot = pd.read_csv(ROT)
        fc = pd.read_csv(FCURVE)
        st = pd.read_csv(STR)
        value = pd.read_csv(VALUE)
        darko = pd.read_csv(DARKO)
        darko.columns = [c.strip().lstrip("﻿") for c in darko.columns]
        bio, _ = kfreeze.load("player_bio")
        imps, _ = build_impacts(value, darko, bio)
        add_rookie_impacts(imps, pool)

        mn = pool[(pool.scenario == "current") & (pool.team_abbr == "MIN")].copy()
        mr = rot[(rot.scenario == "current") & (rot.team_abbr == "MIN")]
        rot_min = {str(int(x.player_id)): float(x.mpg) for _, x in mr.iterrows()}
        name = {str(int(x.player_id)): x.player_name for _, x in mn.iterrows()
                if pd.notna(x.player_id)}
        ceil = {str(int(x.player_id)): float(rotation.ceiling_for(x.prior_mpg))
                for _, x in mn.iterrows() if pd.notna(x.player_id)}
        rank = {str(int(x.player_id)): float(x.rank_score) for _, x in mn.iterrows()
                if pd.notna(x.player_id)}
        posn = {str(int(x.player_id)): x.position for _, x in mn.iterrows()
                if pd.notna(x.player_id)}
        kmin = rot_min.get(KUMINGA_ID, 0.0)

        # ---- the fill order under the C3 rule, shown explicitly ---------------
        elig = [p for p in name if c3_eligible(posn.get(p)) and p != KUMINGA_ID]
        elig = sorted(elig, key=lambda p: -rank.get(p, 0))
        r.note(f"Kuminga's minutes to redistribute: {kmin:.2f}")
        r.note("C3 fill order (eligible at the 4, by rank score):")
        for p in elig:
            r.note(f"  {name[p]:22s} {str(posn.get(p)):15s} in_rot="
                   f"{rot_min.get(p,0):5.2f} ceiling={ceil.get(p,0):5.2f} "
                   f"room={max(ceil.get(p,0)-rot_min.get(p,0),0):5.2f}")

        def price(minutes: dict):
            out = {}
            for fork in FORKS:
                exp = float(st[(st.fork == fork) & (st.team_abbr == "MIN")].exp_2026_27.iloc[0])
                hb = float(st[(st.fork == fork) & (st.team_abbr == "MIN")].hot_baseline.iloc[0])
                g = fc[fc.fork == fork]
                roll = A.rollup(minutes, imps[fork], "rs")
                net = exp + beta * (roll["net"] - hb)
                out[fork] = float(np.interp(net, g.min_net, g.title)) * 100
            return out

        beta = float(E.load_e_params()["beta"])
        with_k = price(rot_min)

        def fill(order, forced=None):
            """Remove Kuminga; hand his minutes down `order`, allowing a forced filler
            to exceed his ceiling up to FORCED_CEILING."""
            out = dict(rot_min)
            freed = out.pop(KUMINGA_ID, 0.0)
            placed = {}
            for pid in order:
                if freed <= 1e-9:
                    break
                cap = FORCED_CEILING if pid == forced else ceil.get(pid, 0.0)
                room = cap - out.get(pid, 0.0)
                if room <= 1e-9:
                    continue
                take = min(room, freed)
                out[pid] = out.get(pid, 0.0) + take
                placed[name.get(pid, pid)] = take
                freed -= take
            return out, placed, freed

        by_name = {v: k for k, v in name.items()}
        variants = {}

        # 1. the C3 default
        variants["A_c3_default_shannon"] = (elig, None)
        # 2. Lyles forced to fill
        ly = by_name.get("Trey Lyles")
        variants["B_lyles_fills"] = ([ly] + [p for p in elig if p != ly], ly)
        # 3. McDaniels slides to the 4; the next wing takes his 3 minutes
        mcd = by_name.get("Jaden McDaniels")
        wing = next((p for p in sorted(name, key=lambda q: -rank.get(q, 0))
                     if p not in (KUMINGA_ID, mcd) and "Forward" in str(posn.get(p, ""))), None)
        variants["C_mcdaniels_slides"] = ([mcd] + ([wing] if wing else [])
                                          + [p for p in elig if p not in (mcd, wing)], mcd)
        # 4. Beringer forced to fill
        ber = by_name.get("Joan Beringer")
        variants["D_beringer_fills"] = ([ber] + [p for p in elig if p != ber], ber)
        # 5. tighter eligibility: Forward or Forward-Centre only
        tight = sorted([p for p in name if tight_eligible(posn.get(p)) and p != KUMINGA_ID],
                       key=lambda p: -rank.get(p, 0))
        variants["E_tight_rule_F_or_FC"] = (tight, None)

        rows = []
        for label, (order, forced) in variants.items():
            without, placed, unplaced = fill(order, forced)
            wo = price(without)
            marg = {f: with_k[f] - wo[f] for f in FORKS}
            vals = list(marg.values())
            sign = ("ALL POSITIVE" if all(v > 0 for v in vals) else
                    "ALL NEGATIVE" if all(v < 0 for v in vals) else "MIXED")
            rows.append(dict(variant=label,
                             filled_by="; ".join(f"{k} +{v:.1f}" for k, v in placed.items()),
                             unplaced_minutes=unplaced,
                             **{f"pp_{f}": marg[f] for f in FORKS},
                             mean_pp=float(np.mean(vals)),
                             lo_pp=min(vals), hi_pp=max(vals),
                             sign_agreement=sign))
            r.note(f"[{label:24s}] {sign:13s} [{min(vals):+.3f}, {max(vals):+.3f}]pp "
                   f"| filled by {'; '.join(f'{k} +{v:.1f}' for k, v in placed.items())}"
                   + (f" | {unplaced:.1f} min UNPLACED" if unplaced > 0.01 else ""))

        df = pd.DataFrame(rows)
        df.to_csv(OUT, index=False)

        all_pos = (df.sign_agreement == "ALL POSITIVE").all()
        fails = df[df.sign_agreement != "ALL POSITIVE"].variant.tolist()
        if all_pos:
            r.note("RULING: all-positive survives EVERY fill. The section claim may read "
                   "'against any internal alternative'.")
        else:
            r.note("RULING: all-positive does NOT survive every fill. The section claim "
                   "must read 'against the MOST LIKELY internal alternative', and these "
                   f"fills are where it fails: {fails}")
        r.output(OUT, rows=len(df))

    print()
    print(df[["variant", "filled_by", "unplaced_minutes"] +
             [f"pp_{f}" for f in FORKS] + ["mean_pp", "sign_agreement"]]
          .round(3).to_string(index=False))


if __name__ == "__main__":
    main()

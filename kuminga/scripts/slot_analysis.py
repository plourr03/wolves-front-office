#!/usr/bin/env python3
"""C3: Kuminga's value when his minutes can only come from the power-forward slot.

THE PROBLEM THIS FIXES. The unconstrained heuristic reallocates a departed player's
minutes across the whole rotation in proportion to desired load. Take Kuminga out and
his 26 minutes are shared by Gobert, Ball, Edwards and everyone else, all of whom the
model rates highly. That makes ANY forward look replaceable, because the counterfactual
is implicitly "his minutes go to the best players on the roster", which no coach can do:
the other four positions are already occupied by the people occupying them.

THE RULE. A slot pool is defined per roster from listed positions in nba_player_bio:
a player is eligible at the 4 if his listed position contains "Forward" AND is not
centre-first. That keeps Forward, Forward-Centre, Guard-Forward and Forward-Guard, and
drops Centre and Centre-Forward. Kuminga's minutes are then taken from, and returned
to, that pool only. Everyone else's minutes are untouched.

WHAT IT CHANGES. The counterfactual stops being "the stars absorb it" and becomes "the
next forward on the roster plays". For Minnesota that is a real and much less flattering
alternative, and it is the honest one.

    python kuminga/scripts/slot_analysis.py
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
sys.path.insert(0, HERE)

from kuminga.lib import kfreeze, market, rotation, runlog  # noqa: E402
import build_team_ratings as A                             # noqa: E402
import bracket_sim as E                                    # noqa: E402
from build_strengths import build_impacts, add_rookie_impacts, nkey  # noqa: E402

POOL = os.path.join(REPO, "kuminga", "outputs", "player_pool_2026_27.csv")
ROT = os.path.join(REPO, "kuminga", "outputs", "rotations_2026_27.csv")
CURVE = os.path.join(REPO, "kuminga", "outputs", "minutes_rank_curve.csv")
FCURVE = os.path.join(REPO, "kuminga", "outputs", "fcurve_min.csv")
STR = os.path.join(REPO, "kuminga", "outputs", "team_strengths_2026_27.csv")
VALUE = os.path.join(REPO, "offseason", "data", "player_value.csv")
DARKO = os.path.join(REPO, "offseason", "data", "darko-dpm-leaderboard.csv")
CONTRACTS = os.path.join(REPO, "offseason", "data", "nba_contracts_2026_27_verified.csv")
OUT = os.path.join(REPO, "kuminga", "outputs", "slot_constrained.csv")
OUT_ALT = os.path.join(REPO, "kuminga", "outputs", "slot_alternatives.csv")

FORKS = ["consensus", "rapm", "box", "darko"]
KUMINGA = "Jonathan Kuminga"
KUMINGA_ID = 1630228
TPMLE = 6_064_000
SD_NOT_QUOTABLE = 1.5


def pf_eligible(position) -> bool:
    """Eligible at the 4 from the listed position. Centre-first listings are excluded."""
    p = str(position or "")
    return ("Forward" in p) and (not p.startswith("Center"))


def reallocate_within_slot(rot_min: dict, removed_id: str, slot_ids: set,
                           ceilings: dict, bench_slot_ids: list) -> dict:
    """Take one player out and give his minutes to the slot pool only.

    Fills in order: players already in the rotation who are eligible and have headroom,
    then eligible players not currently in the rotation, down the rank order. Everyone
    outside the slot pool keeps exactly the minutes he had.
    """
    out = dict(rot_min)
    freed = out.pop(removed_id, 0.0)
    if freed <= 0:
        return out, 0.0
    # The removed player must be excluded from the fill order. Without this he is
    # simply the next eligible body with headroom, so the loop hands his own minutes
    # straight back to him: he came out at 26.0 and went back in at 23.3, the
    # "counterfactual" was 97% himself, and every marginal contribution came out at
    # roughly zero. That is the failure mode this whole slot exercise exists to avoid.
    order = ([p for p in out if p in slot_ids and p != removed_id]
             + [p for p in bench_slot_ids if p not in out and p != removed_id])
    for pid in order:
        if freed <= 1e-9:
            break
        room = ceilings.get(pid, 0.0) - out.get(pid, 0.0)
        if room <= 1e-9:
            continue
        take = min(room, freed)
        out[pid] = out.get(pid, 0.0) + take
        freed -= take
    return out, freed


def main():
    with runlog.run("slot_analysis", inputs={"rule": "listed position contains Forward, "
                                                     "not centre-first"}) as r:
        pool = pd.read_csv(POOL)
        rot = pd.read_csv(ROT)
        curve = pd.read_csv(CURVE, index_col=0).iloc[:, 0]
        fc = pd.read_csv(FCURVE)
        st = pd.read_csv(STR)
        value = pd.read_csv(VALUE)
        darko = pd.read_csv(DARKO)
        darko.columns = [c.strip().lstrip("﻿") for c in darko.columns]
        ct = pd.read_csv(CONTRACTS)
        bio, _ = kfreeze.load("player_bio")

        imps, _ = build_impacts(value, darko, bio)
        add_rookie_impacts(imps, pool)
        pos = bio.set_index("player_id").position.to_dict()

        mn_pool = pool[(pool.scenario == "current") & (pool.team_abbr == "MIN")].copy()
        mn_pool["position"] = mn_pool.player_id.map(pos)
        mn_pool["pf_ok"] = mn_pool.position.map(pf_eligible)
        r.note("MIN slot pool (eligible at the 4): " +
               ", ".join(mn_pool[mn_pool.pf_ok].player_name))
        r.note("NOT eligible: " + ", ".join(mn_pool[~mn_pool.pf_ok].player_name))

        mn_rot = rot[(rot.scenario == "current") & (rot.team_abbr == "MIN")]
        rot_min = {str(int(x.player_id)): float(x.mpg) for _, x in mn_rot.iterrows()}
        ceilings = {str(int(x.player_id)): float(rotation.ceiling_for(x.prior_mpg))
                    for _, x in mn_pool.iterrows() if pd.notna(x.player_id)}
        slot_ids = {str(int(x.player_id)) for _, x in mn_pool.iterrows()
                    if x.pf_ok and pd.notna(x.player_id)}
        bench_slot = [str(int(x.player_id)) for _, x in
                      mn_pool[mn_pool.pf_ok & (mn_pool.rs_avail > 0)]
                      .sort_values("rank_score", ascending=False).iterrows()
                      if pd.notna(x.player_id)]

        without, unplaced = reallocate_within_slot(rot_min, str(KUMINGA_ID), slot_ids,
                                                   ceilings, bench_slot)
        name_by_id = {str(int(x.player_id)): x.player_name
                      for _, x in mn_pool.iterrows() if pd.notna(x.player_id)}
        gains = {name_by_id.get(p, p): without.get(p, 0.0) - rot_min.get(p, 0.0)
                 for p in set(without) | set(rot_min)}
        gains = {k: v for k, v in gains.items() if abs(v) > 0.01 and k != KUMINGA}
        r.note(f"Kuminga's {rot_min.get(str(KUMINGA_ID), 0):.1f} minutes redistribute "
               f"within the slot to: " +
               ", ".join(f"{k} +{v:.1f}" for k, v in
                         sorted(gains.items(), key=lambda kv: -kv[1])))
        if unplaced > 0.01:
            r.note(f"  {unplaced:.1f} minutes could not be placed inside the slot pool "
                   "(everyone eligible is at his ceiling)")

        filler = max(gains, key=gains.get) if gains else None
        r.note(f"THE PLAYER WHO OTHERWISE FILLS THE 4: {filler}")

        # ---- per-fork marginal contribution ----------------------------------
        p = E.load_e_params()
        beta = float(p["beta"])
        rows = []
        for fork in FORKS:
            exp = float(st[(st.fork == fork) & (st.team_abbr == "MIN")].exp_2026_27.iloc[0])
            hb = float(st[(st.fork == fork) & (st.team_abbr == "MIN")].hot_baseline.iloc[0])
            g = fc[fc.fork == fork]

            def price(mp):
                roll = A.rollup(mp, imps[fork], "rs")
                net = exp + beta * (roll["net"] - hb)
                return net, float(np.interp(net, g.min_net, g.title))

            net_w, t_w = price(rot_min)
            net_o, t_o = price(without)
            fid = [i for i, n in name_by_id.items() if n == filler]
            fill_net = None
            if fid and fid[0] in imps[fork]:
                d = imps[fork][fid[0]]
                fill_net = d["off"] - d["def"]
            kd = imps[fork][str(KUMINGA_ID)]
            kum_net = kd["off"] - kd["def"]
            rows.append(dict(fork=fork, min_net_with=net_w, min_net_without=net_o,
                             title_with=t_w, title_without=t_o,
                             marginal_pp=(t_w - t_o) * 100,
                             kuminga_net=kum_net, filler=filler, filler_net=fill_net,
                             surplus_vs_filler=(kum_net - fill_net)
                             if fill_net is not None else np.nan))
            r.note(f"[{fork:9s}] with {t_w*100:.2f}% | without {t_o*100:.2f}% | "
                   f"MARGINAL {(t_w-t_o)*100:+.3f}pp | Kuminga {kum_net:+.2f} vs "
                   f"{filler} {fill_net:+.2f}" if fill_net is not None else "")
        sc = pd.DataFrame(rows)
        sc.to_csv(OUT, index=False)
        signs = ("ALL POSITIVE" if (sc.marginal_pp > 0).all() else
                 "ALL NEGATIVE" if (sc.marginal_pp < 0).all() else "MIXED")
        r.note(f"SLOT-CONSTRAINED VERDICT for kuminga_in: {signs} "
               f"[{sc.marginal_pp.min():+.3f}, {sc.marginal_pp.max():+.3f}]pp")

        # ---- alternatives, same slot rule, PF-eligible only -------------------
        value["k"] = value.player_name.map(nkey)
        bio2 = bio.copy(); bio2["k"] = bio2.player_name.map(nkey)
        pos_by_k = bio2.drop_duplicates("k").set_index("k").position.to_dict()
        sal = (ct[ct.nba_player_id.astype(str).str.isdigit()]
               .assign(pid=lambda d: d.nba_player_id.astype(float).astype(int))
               .drop_duplicates("pid").set_index("pid").salary_2026_27)

        CANDIDATES = [("Josh Minott", 4_500_000), ("Jaxson Hayes", 6_000_000),
                      ("Kenrich Williams", 5_000_000), ("Al Horford", 6_822_000),
                      ("Dean Wade", 9_000_000)]
        alt_rows = []
        for name, price_paid in CANDIDATES:
            k = nkey(name)
            position = pos_by_k.get(k, "")
            eligible = pf_eligible(position)
            row = value[value.k == k]
            if row.empty:
                continue
            rw = row.iloc[0]
            sd = float(np.sqrt(rw.off_sd ** 2 + rw.def_sd ** 2))
            # Price the swap under the SAME slot rule: the alternative takes exactly
            # Kuminga's minutes, nobody else moves. That is the like-for-like question.
            per_fork = {}
            for fork in FORKS:
                exp = float(st[(st.fork == fork) & (st.team_abbr == "MIN")].exp_2026_27.iloc[0])
                hb = float(st[(st.fork == fork) & (st.team_abbr == "MIN")].hot_baseline.iloc[0])
                g = fc[fc.fork == fork]
                imp = dict(imps[fork])
                pid_alt = str(int(rw.player_id))
                if pid_alt not in imp:
                    per_fork[fork] = np.nan
                    continue
                swapped = dict(rot_min)
                kmin = swapped.pop(str(KUMINGA_ID), 0.0)
                swapped[pid_alt] = swapped.get(pid_alt, 0.0) + kmin
                roll = A.rollup(swapped, imp, "rs")
                net = exp + beta * (roll["net"] - hb)
                t_alt = float(np.interp(net, g.min_net, g.title))
                base_t = float(sc[sc.fork == fork].title_with.iloc[0])
                per_fork[fork] = (t_alt - base_t) * 100
            vals = [v for v in per_fork.values() if not np.isnan(v)]
            sign = ("ALL POSITIVE" if vals and all(v > 0 for v in vals) else
                    "ALL NEGATIVE" if vals and all(v < 0 for v in vals) else "MIXED")
            alt_rows.append(dict(
                player=name, listed_position=position, pf_eligible=eligible,
                salary=price_paid, affordable_on_tpmle=price_paid <= TPMLE,
                consensus_net=float(rw.consensus_net), net_sd=float(rw.net_sd),
                posterior_sd=sd,
                **{f"pp_{f}": per_fork.get(f, np.nan) for f in FORKS},
                mean_pp=float(np.mean(vals)) if vals else np.nan,
                sign_agreement=sign,
                quotable=(sd <= SD_NOT_QUOTABLE) and eligible,
                exclusion_reason=("centre-first listing, not a 4" if not eligible else
                                  f"posterior sd {sd:.2f} exceeds {SD_NOT_QUOTABLE}"
                                  if sd > SD_NOT_QUOTABLE else ""),
            ))
        alt = pd.DataFrame(alt_rows)
        alt.to_csv(OUT_ALT, index=False)
        r.note("ALTERNATIVES under the slot rule:")
        for _, x in alt.iterrows():
            r.note(f"  {x.player:18s} {x.listed_position:15s} pf={str(x.pf_eligible):5s} "
                   f"afford={str(x.affordable_on_tpmle):5s} sd={x.posterior_sd:.2f} "
                   f"mean {x.mean_pp:+.2f}pp {x.sign_agreement:13s} "
                   f"quotable={x.quotable} {x.exclusion_reason}")
        r.output(OUT, rows=len(sc))
        r.output(OUT_ALT, rows=len(alt))

    print()
    print(sc.round(3).to_string(index=False))
    print()
    print(alt.round(2).to_string(index=False))


if __name__ == "__main__":
    main()

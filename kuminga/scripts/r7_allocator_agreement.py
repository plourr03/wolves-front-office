#!/usr/bin/env python3
"""R7: do the shipping verdicts hold under BOTH minutes allocators?

D85 left this open. There are two allocators, and they answer different questions:

  TEAM-RANK  `rotation.allocate`, what `build_rotations` calls. Ranks a roster team-wide,
             cuts at ten, and is the basis of every headline number.
  POOLED     `rotation.allocate_pooled`, what the attribution layer calls. Splits the 240
             minutes into guard/forward/big budgets and water-fills inside each, so a
             departing player's minutes stay in his own position group.

The shipping rule now has four cells per verdict: two aging bases x two allocators. A
verdict ships only if its sign is the same in all four, is not MIXED in any, and all four
views clear their floor in every cell.

  MOVES (Shapley) come from `r5_shapley_williams.py`, which prices the eight-move game
  under both allocators on both bases and is gated against the published tables.

  SLOT VARIANTS are recomputed here, because `slot_robustness.py` only ever ran on the
  team-rank rotation. The pooled version starts from the pooled allocation of the same
  roster and hands Kuminga's minutes down the same eligibility and ceiling rules.

  G1  the team-rank slot variants reproduce `slot_robustness.csv` (un-aged) and
      `aged/slot_robustness.csv` to 1e-9 points.
  G2  the floors reproduce the published clearing counts for the slot variants.
  G3  the pooled allocation of the current roster sums to 240 minutes and contains
      Kuminga; his minutes to redistribute are reported for both allocators.

    python kuminga/scripts/r7_allocator_agreement.py
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
from slot_robustness import c3_eligible, tight_eligible, FORCED_CEILING, KUMINGA_ID  # noqa: E402

OUT_DIR = os.path.join(REPO, "kuminga", "outputs")
POOL = os.path.join(OUT_DIR, "player_pool_2026_27.csv")
CURVE = os.path.join(OUT_DIR, "minutes_rank_curve.csv")
SHARES = os.path.join(OUT_DIR, "team_pool_shares.csv")
VALUE = os.path.join(REPO, "offseason", "data", "player_value.csv")
DARKO = os.path.join(REPO, "offseason", "data", "darko-dpm-leaderboard.csv")
OUT = os.path.join(OUT_DIR, "r7_allocator_slots.csv")
OUT_V = os.path.join(OUT_DIR, "r7_allocator_verdicts.csv")
FORKS = ["consensus", "rapm", "box", "darko"]
BASES = {
    "unaged": dict(dir=OUT_DIR, aging="0"),
    "aged": dict(dir=os.path.join(OUT_DIR, "aged"), aging="1"),
}
# every candidate verdict, so the sheet has one source for the four-cell rule. The seven
# that shipped after D85 are ball_in, reid_out, ddv_injury and slot variants A, C, D, E.
MOVES = ["ball_in", "reid_out", "other_departures", "randle_out", "dosunmu_retained",
         "depth", "kuminga_in", "ddv_injury"]
SLOTS = ["A_c3_default_shannon", "B_lyles_fills", "C_mcdaniels_slides", "D_beringer_fills",
         "E_tight_rule_F_or_FC"]


def floors_for(fc, st):
    """noise_floor.py, line for line."""
    out = {}
    for f in FORKS:
        g = fc[fc.fork == f].sort_values("min_net").reset_index(drop=True)
        net = float(st[(st.fork == f) & (st.team_abbr == "MIN")].net_current.iloc[0])
        mc = float(np.interp(net, g.min_net, g.title_sd)) * 100
        h = float(g.min_net.diff().median())
        d2 = np.abs(np.diff(g.title.to_numpy(), 2)) / (h ** 2)
        idx = int(np.clip(np.searchsorted(g.min_net.to_numpy(), net) - 1, 0, len(d2) - 1))
        lo, hi = max(0, idx - 2), min(len(d2), idx + 3)
        f2 = float(np.max(d2[lo:hi])) if hi > lo else float(np.max(d2))
        out[f] = 2.0 * float(np.hypot(mc, (h ** 2) / 8.0 * f2 * 100)) * np.sqrt(2)
    return out


def sign_of(vals):
    return ("ALL POSITIVE" if all(v > 0 for v in vals) else
            "ALL NEGATIVE" if all(v < 0 for v in vals) else "MIXED")


def main():
    with runlog.run("r7_allocator_agreement",
                    inputs={"bases": list(BASES), "allocators": ["pooled", "teamrank"],
                            "moves": MOVES, "slots": SLOTS}) as r:
        pool = pd.read_csv(POOL)
        curve = pd.read_csv(CURVE, index_col=0).iloc[:, 0]
        value = pd.read_csv(VALUE)
        darko = pd.read_csv(DARKO)
        darko.columns = [c.strip().lstrip("﻿") for c in darko.columns]
        bio, _ = kfreeze.load("player_bio")
        budget = pd.read_csv(SHARES, index_col=0).loc["MIN"].to_dict()
        beta = float(E.load_e_params()["beta"])

        mn = pool[(pool.scenario == "current") & (pool.team_abbr == "MIN")].copy()
        pid = lambda x: str(int(x))  # noqa: E731
        name = {pid(x.player_id): x.player_name for _, x in mn.iterrows() if pd.notna(x.player_id)}
        ceil = {pid(x.player_id): float(rotation.ceiling_for(x.prior_mpg))
                for _, x in mn.iterrows() if pd.notna(x.player_id)}
        rank = {pid(x.player_id): float(x.rank_score) for _, x in mn.iterrows()
                if pd.notna(x.player_id)}
        posn = {pid(x.player_id): x.position for _, x in mn.iterrows() if pd.notna(x.player_id)}
        by_name = {v: k for k, v in name.items()}

        # the two allocations of the same roster
        pooled_min = {k: float(v) for k, v in
                      rotation.allocate_pooled(mn, curve, budget_share=budget).items()}
        allocations = {"pooled": pooled_min}
        r.note("G3: pooled allocation %.1f minutes over %d players; Kuminga %.2f"
               % (sum(pooled_min.values()), len(pooled_min), pooled_min.get(KUMINGA_ID, 0.0)))
        if abs(sum(pooled_min.values()) - 240.0) > 1e-6 or KUMINGA_ID not in pooled_min:
            raise RuntimeError("G3 failed: the pooled allocation is not 240 minutes with Kuminga")

        def fills(rot_min):
            """The five variants of who takes Kuminga's minutes, on a given allocation."""
            elig = sorted([p for p in name if c3_eligible(posn.get(p)) and p != KUMINGA_ID],
                          key=lambda p: -rank.get(p, 0))
            ly, mcd, ber = (by_name.get(n) for n in ("Trey Lyles", "Jaden McDaniels", "Joan Beringer"))
            wing = next((p for p in sorted(name, key=lambda q: -rank.get(q, 0))
                         if p not in (KUMINGA_ID, mcd) and "Forward" in str(posn.get(p, ""))), None)
            tight = sorted([p for p in name if tight_eligible(posn.get(p)) and p != KUMINGA_ID],
                           key=lambda p: -rank.get(p, 0))
            return {
                "A_c3_default_shannon": (elig, None),
                "B_lyles_fills": ([ly] + [p for p in elig if p != ly], ly),
                "C_mcdaniels_slides": ([mcd] + ([wing] if wing else [])
                                       + [p for p in elig if p not in (mcd, wing)], mcd),
                "D_beringer_fills": ([ber] + [p for p in elig if p != ber], ber),
                "E_tight_rule_F_or_FC": (tight, None),
            }

        def without_kuminga(rot_min, order, forced):
            out = dict(rot_min)
            freed = out.pop(KUMINGA_ID, 0.0)
            placed = {}
            for p in order:
                if freed <= 1e-9:
                    break
                cap = FORCED_CEILING if p == forced else ceil.get(p, 0.0)
                room = cap - out.get(p, 0.0)
                if room <= 1e-9:
                    continue
                take = min(room, freed)
                out[p] = out.get(p, 0.0) + take
                placed[name.get(p, p)] = take
                freed -= take
            return out, placed, freed

        rows = []
        floors = {}
        for basis, cfg in BASES.items():
            os.environ["KUMINGA_AGING"] = cfg["aging"]
            imps, _ = build_impacts(value, darko, bio)
            add_rookie_impacts(imps, pool)
            fc = pd.read_csv(os.path.join(cfg["dir"], "fcurve_min.csv"))
            st = pd.read_csv(os.path.join(cfg["dir"], "team_strengths_2026_27.csv"))
            rot = pd.read_csv(os.path.join(cfg["dir"], "rotations_2026_27.csv"))
            mr = rot[(rot.scenario == "current") & (rot.team_abbr == "MIN")]
            allocations["teamrank"] = {pid(x.player_id): float(x.mpg) for _, x in mr.iterrows()}
            floors[basis] = floors_for(fc, st)
            pub = pd.read_csv(os.path.join(cfg["dir"], "slot_robustness.csv")).set_index("variant")
            pubf = pd.read_csv(os.path.join(
                cfg["dir"] if basis == "aged" else OUT_DIR,
                "noise_floor_slot%s.csv" % ("_AGED" if basis == "aged" else ""))).set_index("variant")

            def price(minutes):
                out = {}
                for f in FORKS:
                    exp = float(st[(st.fork == f) & (st.team_abbr == "MIN")].exp_2026_27.iloc[0])
                    hb = float(st[(st.fork == f) & (st.team_abbr == "MIN")].hot_baseline.iloc[0])
                    g = fc[fc.fork == f]
                    net = exp + beta * (A.rollup(minutes, imps[f], "rs")["net"] - hb)
                    out[f] = float(np.interp(net, g.min_net, g.title)) * 100
                return out

            for alloc, rot_min in allocations.items():
                with_k = price(rot_min)
                for variant, (order, forced) in fills(rot_min).items():
                    wo, placed, unplaced = without_kuminga(rot_min, order, forced)
                    marg = {f: with_k[f] - price(wo)[f] for f in FORKS}
                    vals = list(marg.values())
                    n_clear = sum(abs(marg[f]) >= floors[basis][f] for f in FORKS)
                    rows.append(dict(basis=basis, allocator=alloc, variant=variant,
                                     kuminga_minutes=rot_min.get(KUMINGA_ID, 0.0),
                                     filled_by="; ".join("%s +%.1f" % (k, v) for k, v in placed.items()),
                                     unplaced_minutes=unplaced,
                                     **{"pp_" + f: marg[f] for f in FORKS},
                                     mean_pp=float(np.mean(vals)), lo_pp=min(vals), hi_pp=max(vals),
                                     sign_agreement=sign_of(vals), n_clear=n_clear,
                                     clears_all=bool(sign_of(vals) != "MIXED" and n_clear == 4)))
                    if alloc == "teamrank":
                        gap = max(abs(float(pub.loc[variant, "pp_" + f]) - marg[f]) for f in FORKS)
                        if gap > 1e-9:
                            raise RuntimeError("G1 failed on %s %s: %.2e" % (basis, variant, gap))
                        if n_clear != int(pubf.loc[variant, "n_forks_clearing"]):
                            raise RuntimeError("G2 failed on %s %s" % (basis, variant))
            r.note("G1/G2 %s: team-rank slot variants reproduce slot_robustness and its clearing "
                   "counts" % basis)
            r.note("%s: Kuminga has %.2f minutes team-rank, %.2f pooled"
                   % (basis, allocations["teamrank"].get(KUMINGA_ID, 0.0),
                      pooled_min.get(KUMINGA_ID, 0.0)))

        S = pd.DataFrame(rows)
        S.to_csv(OUT, index=False)
        for _, x in S[S.basis == "unaged"].iterrows():
            r.note("  %-9s %-22s %+.3f  %-13s %d/4  %s%s"
                   % (x.allocator, x.variant, x.mean_pp, x.sign_agreement, x.n_clear,
                      x.filled_by, " | %.1f UNPLACED" % x.unplaced_minutes
                      if x.unplaced_minutes > 0.01 else ""))

        # ---- the four-cell rule ------------------------------------------------------
        mv = pd.read_csv(os.path.join(OUT_DIR, "r5_shapley_williams_verdicts.csv"))
        mv = mv[(mv.game == "eight moves") & mv.version.isin(["after_d85", "after_d85_teamrank"])]
        mv["allocator"] = np.where(mv.version == "after_d85", "pooled", "teamrank")
        out = []
        for item in MOVES + SLOTS:
            cells = {}
            for alloc in ("pooled", "teamrank"):
                for basis in BASES:
                    if item in MOVES:
                        x = mv[(mv.allocator == alloc) & (mv.move == item)].iloc[0]
                        cells[(alloc, basis)] = dict(
                            mean=float(x["mean_pp_" + basis]), sign=x["sign_" + basis],
                            n_clear=int(x["n_clear_" + basis]),
                            clears=bool(x["clears_all_" + basis]))
                    else:
                        x = S[(S.allocator == alloc) & (S.basis == basis) & (S.variant == item)].iloc[0]
                        cells[(alloc, basis)] = dict(mean=float(x.mean_pp), sign=x.sign_agreement,
                                                     n_clear=int(x.n_clear), clears=bool(x.clears_all))
            signs = {c["sign"] for c in cells.values()}
            ships = bool(len(signs) == 1 and "MIXED" not in signs
                         and all(c["clears"] for c in cells.values()))
            row = dict(item=item, family="move" if item in MOVES else "slot", ships_all_four=ships,
                       signs="; ".join(sorted(signs)))
            for (alloc, basis), c in cells.items():
                row["%s_%s_mean" % (alloc, basis)] = c["mean"]
                row["%s_%s_sign" % (alloc, basis)] = c["sign"]
                row["%s_%s_clear" % (alloc, basis)] = c["n_clear"]
            out.append(row)
        V = pd.DataFrame(out)
        V.to_csv(OUT_V, index=False)
        r.note("")
        r.note("THE FOUR-CELL RULE (pooled and team-rank, un-aged and aged):")
        for _, x in V.iterrows():
            r.note("  %-22s pooled %+.3f / %+.3f | team-rank %+.3f / %+.3f | clearing %d,%d,%d,%d "
                   "| %s -> %s"
                   % (x["item"], x.pooled_unaged_mean, x.pooled_aged_mean, x.teamrank_unaged_mean,
                      x.teamrank_aged_mean, x.pooled_unaged_clear, x.pooled_aged_clear,
                      x.teamrank_unaged_clear, x.teamrank_aged_clear, x.signs,
                      "SHIPS" if x.ships_all_four else "DROPS"))
        r.note("ships under all four cells: %d of %d" % (int(V.ships_all_four.sum()), len(V)))
        r.output(OUT, rows=len(S))
        r.output(OUT_V, rows=len(V))


if __name__ == "__main__":
    main()

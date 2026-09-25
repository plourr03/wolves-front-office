#!/usr/bin/env python3
"""The Williams ordering check: is the 16.1 a finding about the roster or an artefact of how
the rotation is ordered?

1. Minnesota's projected ten under both allocators, with each player's impact in every
   view, prior minutes per appearance, rank score and projected minutes; whether Shannon
   is in the ten.
2. Three orderings of the same roster, each allocated and priced the same way:
     default            rank score = 0.5 * pct(prior minutes) + 0.5 * pct(impact), everyone
     mover-discounted   movers ordered on 0.2 / 0.8 (the W1 minutes blend applied to the
                        ORDER as well), incumbents on 0.5 / 0.5
     impact only        rank score = pct(impact), everyone
   For each: Williams's rank on the roster and his minutes, and the offseason verdict
   (title odds at the current roster's net minus at the baseline's, per view, off the
   f-curve, the field held fixed) exactly as the sensitivity script prices it.
3. The calibrated default: Williams's prior load times the median retention of the
   mover cohort (`mover_minutes_base_rate.py`), priced the same way with the rest of his
   minutes handed down the rank order under each player's ceiling.

OUTPUT. `outputs/williams_ordering_check.csv` (one row per ordering or level, with the
four views), `outputs/williams_projected_ten.csv` (item 1) and
`docs/williams_ordering_check.md`.

    python kuminga/scripts/williams_ordering_check.py
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

from kuminga.lib import kfreeze, rotation, runlog     # noqa: E402
import build_team_ratings as A                        # noqa: E402
import bracket_sim as E                               # noqa: E402
from build_strengths import build_impacts, add_rookie_impacts  # noqa: E402

OUT_DIR = os.path.join(REPO, "kuminga", "outputs")
POOL = os.path.join(OUT_DIR, "player_pool_2026_27.csv")
ROT = os.path.join(OUT_DIR, "rotations_2026_27.csv")
FCURVE = os.path.join(OUT_DIR, "fcurve_min.csv")
STR = os.path.join(OUT_DIR, "team_strengths_2026_27.csv")
CURVE = os.path.join(OUT_DIR, "minutes_rank_curve.csv")
SHARES = os.path.join(OUT_DIR, "team_pool_shares.csv")
BASE = os.path.join(OUT_DIR, "mover_minutes_base_rate.csv")
VALUE = os.path.join(REPO, "offseason", "data", "player_value.csv")
DARKO = os.path.join(REPO, "offseason", "data", "darko-dpm-leaderboard.csv")
OUT = os.path.join(OUT_DIR, "williams_ordering_check.csv")
OUT_TEN = os.path.join(OUT_DIR, "williams_projected_ten.csv")
OUT_MD = os.path.join(REPO, "kuminga", "docs", "williams_ordering_check.md")

FORKS = ["consensus", "rapm", "box", "darko"]
WILLIAMS_ID = "1642262"
SHANNON = "Terrence Shannon Jr."
MOVER_ORDER_MPG_WEIGHT = 0.2      # the W1 blend, applied to the order


def sign_of(vals):
    if all(v > 0 for v in vals):
        return "ALL POSITIVE"
    if all(v < 0 for v in vals):
        return "ALL NEGATIVE"
    return "MIXED"


def main():
    with runlog.run("williams_ordering_check", inputs={"mover_order_mpg_weight": MOVER_ORDER_MPG_WEIGHT}) as r:
        pool = pd.read_csv(POOL)
        rot = pd.read_csv(ROT)
        fc = pd.read_csv(FCURVE)
        st = pd.read_csv(STR)
        curve = pd.read_csv(CURVE, index_col=0).iloc[:, 0]
        budget = pd.read_csv(SHARES, index_col=0).loc["MIN"].to_dict()
        value = pd.read_csv(VALUE)
        darko = pd.read_csv(DARKO)
        darko.columns = [c.strip().lstrip("﻿") for c in darko.columns]
        bio, _ = kfreeze.load("player_bio")
        imps, _ = build_impacts(value, darko, bio)
        add_rookie_impacts(imps, pool)
        beta = float(E.load_e_params()["beta"])

        mn = pool[(pool.scenario == "current") & (pool.team_abbr == "MIN")].copy()
        mn = mn[mn.player_id.notna()].copy()
        mn["pid"] = mn.player_id.map(lambda x: str(int(x)))
        name = dict(zip(mn.pid, mn.player_name))
        ceil = dict(zip(mn.pid, rotation.ceiling_for(mn.prior_mpg.to_numpy())))

        def imp(fork, pid):
            d = imps[fork].get(pid)
            return float(d["off"] - d["def"]) if d else np.nan     # net = off - def, the value file's convention

        def net_for(minutes, fork):
            row = st[(st.fork == fork) & (st.team_abbr == "MIN")]
            exp = float(row.exp_2026_27.iloc[0])
            hb = float(row.hot_baseline.iloc[0])
            roll = A.rollup(minutes, imps[fork], "rs")
            return exp + beta * (roll["net"] - hb)

        def title_at(net, fork):
            g = fc[fc.fork == fork]
            return float(np.interp(net, g.min_net, g.title)) * 100

        base_t = {f: title_at(float(st[(st.fork == f) & (st.team_abbr == "MIN")].net_baseline.iloc[0]), f) for f in FORKS}

        def price(minutes):
            net_k = {f: net_for(minutes, f) for f in FORKS}
            title_k = {f: title_at(net_k[f], f) for f in FORKS}
            delta = {f: title_k[f] - base_t[f] for f in FORKS}
            return net_k, title_k, delta

        # ---- 1. the projected ten under both allocators --------------------------------
        team_rank = rot[(rot.scenario == "current") & (rot.team_abbr == "MIN")].copy()
        team_rank["pid"] = team_rank.player_id.map(lambda x: str(int(x)))
        tr_min = dict(zip(team_rank.pid, team_rank.mpg))
        pooled_min = {k: float(v) for k, v in rotation.allocate_pooled(mn, curve, budget_share=budget).items()}
        avail = mn[mn.rs_avail > 0].sort_values("rank_score", ascending=False).reset_index(drop=True)
        avail["order_rank"] = avail.index + 1
        ten = []
        for _, x in avail.iterrows():
            ten.append(dict(player=x.player_name, position=x.position, order_rank=int(x.order_rank), rank_score=float(x.rank_score),
                            pct_mpg=float(x.pct_mpg), pct_net=float(x.pct_net), prior_mpg=float(x.prior_mpg), moved=bool(x.moved_teams),
                            consensus=imp("consensus", x.pid), rapm=imp("rapm", x.pid), box=imp("box", x.pid), darko=imp("darko", x.pid),
                            mpg_team_rank=float(tr_min.get(x.pid, 0.0)), mpg_pooled=float(pooled_min.get(x.pid, 0.0))))
        TEN = pd.DataFrame(ten)
        TEN.to_csv(OUT_TEN, index=False)
        in_ten_tr = set(TEN[TEN.mpg_team_rank > 0].player)
        pooled_top10 = set(TEN.sort_values("mpg_pooled", ascending=False).head(10).player)
        r.note("1. Minnesota's available pool by rank score (team-rank minutes / pooled minutes):")
        for _, x in TEN.iterrows():
            r.note("   %2d  %-22s score %.3f (mpg pct %.2f, net pct %.2f) prior %5.1f%s | consensus %+.2f rapm %+.2f box %+.2f darko %+.2f | team-rank %5.1f  pooled %5.1f"
                   % (x.order_rank, x.player, x.rank_score, x.pct_mpg, x.pct_net, x.prior_mpg, " mover" if x.moved else "      ",
                      x.consensus, x.rapm, x.box, x.darko, x.mpg_team_rank, x.mpg_pooled))
        r.note("   Shannon in the team-rank ten: %s; in the pooled top ten by minutes: %s"
               % (SHANNON in in_ten_tr, SHANNON in pooled_top10))
        r.note("   team-rank ten: %s" % ", ".join(TEN[TEN.mpg_team_rank > 0].sort_values("mpg_team_rank", ascending=False).player))
        r.note("   pooled top ten: %s" % ", ".join(TEN.sort_values("mpg_pooled", ascending=False).head(10).player))

        # ---- 2. the three orderings -----------------------------------------------------
        rows = []

        def run_ordering(label, score_fn):
            m2 = mn.copy()
            m2["rank_score"] = score_fn(m2)
            frame = rotation.allocation_frame(m2, curve, use_ceiling=True)
            frame["pid"] = frame.player_id.map(lambda x: str(int(x)))
            minutes = dict(zip(frame.pid, frame.mpg))
            order = m2[m2.rs_avail > 0].sort_values("rank_score", ascending=False).reset_index(drop=True)
            wrank = int(order.index[order.pid == WILLIAMS_ID][0]) + 1
            wmin = float(minutes.get(WILLIAMS_ID, 0.0))
            net_k, title_k, delta = price(minutes)
            rec = dict(ordering=label, williams_rank=wrank, williams_mpg=wmin, in_ten=wmin > 0,
                       tenth_man=frame.sort_values("mpg").iloc[0].player_name if len(frame) else "",
                       delta_mean=float(np.mean(list(delta.values()))), delta_sign=sign_of(list(delta.values())),
                       title_mean=float(np.mean(list(title_k.values()))))
            for f in FORKS:
                rec["delta_" + f] = delta[f]
                rec["title_" + f] = title_k[f]
                rec["net_" + f] = net_k[f]
            rec["rotation"] = "; ".join("%s %.1f" % (x.player_name, x.mpg) for _, x in frame.sort_values("mpg", ascending=False).iterrows())
            rows.append(rec)
            r.note("   %-34s Williams rank %2d, %5.1f mpg | delta %+.2f (%s): consensus %+.2f rapm %+.2f box %+.2f darko %+.2f"
                   % (label, wrank, wmin, rec["delta_mean"], rec["delta_sign"], delta["consensus"], delta["rapm"], delta["box"], delta["darko"]))
            return rec

        r.note("2. Three orderings, team-rank allocator, priced off the f-curve with the field fixed:")
        run_ordering("default (0.5 minutes / 0.5 impact, all)", lambda d: d.rank_score)
        run_ordering("mover-discounted order (movers 0.2 / 0.8)",
                     lambda d: np.where(d.moved_teams, MOVER_ORDER_MPG_WEIGHT * d.pct_mpg + (1 - MOVER_ORDER_MPG_WEIGHT) * d.pct_net, d.rank_score))
        run_ordering("impact only (pct impact, all)", lambda d: d.pct_net)

        # ---- 3. the calibrated default from the mover base rate ---------------------------
        base = pd.read_csv(BASE).set_index("group")
        med = float(base.loc["all movers", "median"])
        q25, q75, n = float(base.loc["all movers", "q25"]), float(base.loc["all movers", "q75"]), int(base.loc["all movers", "n"])
        wprior = float(mn[mn.pid == WILLIAMS_ID].prior_mpg.iloc[0])
        rank = dict(zip(mn.pid, mn.rank_score))

        def set_williams(minutes, target):
            m = dict(minutes)
            freed = m.get(WILLIAMS_ID, 0.0) - target
            m[WILLIAMS_ID] = target
            for pid in sorted([x for x in m if x != WILLIAMS_ID], key=lambda x: -rank.get(x, 0)):
                if freed <= 1e-9:
                    break
                take = min(max(ceil.get(pid, 0.0) - m.get(pid, 0.0), 0.0), freed)
                m[pid] = m.get(pid, 0.0) + take
                freed -= take
            return m, freed

        r.note("3. The calibrated default: cohort n=%d, retention median %.2f (IQR %.2f to %.2f); Williams's prior %.1f a night"
               % (n, med, q25, q75, wprior))
        levels = [("calibrated: median retention, all movers", med), ("calibrated: lower quartile, all movers", q25), ("calibrated: upper quartile, all movers", q75)]
        for grp, lab in (("new team top ten by wins", "calibrated: median, new team top ten by wins"),
                         ("new team at or above .600", "calibrated: median, new team at or above .600"),
                         ("new team under .500", "calibrated: median, new team under .500")):
            if grp in base.index:
                levels.append((lab + " (n=%d)" % int(base.loc[grp, "n"]), float(base.loc[grp, "median"])))
        for label, ret in levels:
            raw_target = ret * wprior
            target = min(raw_target, float(tr_min.get(WILLIAMS_ID, 0.0)))   # the check hands minutes DOWN only; above the default the default stands
            m, unplaced = set_williams(tr_min, target)
            net_k, title_k, delta = price(m)
            rec = dict(ordering=label, williams_rank=int(avail.index[avail.pid == WILLIAMS_ID][0]) + 1, williams_mpg=target, in_ten=target > 0,
                       tenth_man="", delta_mean=float(np.mean(list(delta.values()))), delta_sign=sign_of(list(delta.values())),
                       title_mean=float(np.mean(list(title_k.values()))), retention=ret, retention_x_prior=raw_target, unplaced=unplaced)
            for f in FORKS:
                rec["delta_" + f] = delta[f]
                rec["title_" + f] = title_k[f]
                rec["net_" + f] = net_k[f]
            rec["rotation"] = "; ".join("%s %.1f" % (name[p], v) for p, v in sorted(m.items(), key=lambda kv: -kv[1]) if v > 0)
            rows.append(rec)
            r.note("   %-52s %5.1f mpg (%.2f x %.1f%s) | delta %+.2f (%s): consensus %+.2f rapm %+.2f box %+.2f darko %+.2f%s"
                   % (label, target, ret, wprior, (" = %.1f, above the default so the default stands" % raw_target) if raw_target > target + 1e-9 else "",
                      rec["delta_mean"], rec["delta_sign"], delta["consensus"], delta["rapm"], delta["box"], delta["darko"],
                      (" | %.1f minutes unplaced" % unplaced) if unplaced > 1e-6 else ""))
        R = pd.DataFrame(rows)
        R.to_csv(OUT, index=False)
        r.output(OUT_TEN, rows=len(TEN))
        r.output(OUT, rows=len(R))

        # ---- the doc ------------------------------------------------------------------------
        L = ["# The Williams ordering check\n",
             "*Run `%s`. Item 1 is the projected ten under both allocators; item 2 re-orders the same roster three ways; item 3 sets his "
             "minutes from the mover base rate (`mover_minutes_base_rate.py`). Every verdict is priced the way the sensitivity script "
             "prices it: title odds at the roster's net minus at the baseline's, per view, off the f-curve, the field fixed.*\n" % r.run_id,
             "## 1. Minnesota's pool by rank score\n",
             "| # | player | rank score | minutes pct | impact pct | prior mpg | mover | consensus | RAPM | box | DARKO | team-rank mpg | pooled mpg |",
             "|---:|---|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|"]
        for _, x in TEN.iterrows():
            L.append("| %d | %s | %.3f | %.2f | %.2f | %.1f | %s | %+.2f | %+.2f | %+.2f | %+.2f | %.1f | %.1f |"
                     % (x.order_rank, x.player, x.rank_score, x.pct_mpg, x.pct_net, x.prior_mpg, "yes" if x.moved else "", x.consensus, x.rapm, x.box, x.darko,
                        x.mpg_team_rank, x.mpg_pooled))
        L.append("")
        L.append("Shannon in the team-rank ten: **%s**. In the pooled top ten by minutes: **%s**.\n" % ("yes" if SHANNON in in_ten_tr else "no", "yes" if SHANNON in pooled_top10 else "no"))
        L.append("## 2. Three orderings, and 3. the calibrated default\n")
        L.append("| ordering or level | Williams rank | Williams mpg | offseason delta, mean | sign | consensus | RAPM | box | DARKO |")
        L.append("|---|---:|---:|---:|---|---:|---:|---:|---:|")
        for _, x in R.iterrows():
            L.append("| %s | %d | %.1f | %+.2f | %s | %+.2f | %+.2f | %+.2f | %+.2f |"
                     % (x.ordering, x.williams_rank, x.williams_mpg, x.delta_mean, x.delta_sign, x.delta_consensus, x.delta_rapm, x.delta_box, x.delta_darko))
        L.append("")
        L.append("Mover base rate: n = %d, retention median %.2f, quartiles %.2f and %.2f; Williams's prior load %.1f a night.\n" % (n, med, q25, q75, wprior))
        with open(OUT_MD, "w", encoding="utf-8") as fh:
            fh.write("\n".join(L))
        r.output(OUT_MD)


if __name__ == "__main__":
    main()

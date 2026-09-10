#!/usr/bin/env python3
"""F4a/b/c: the model-market disagreement opened up per view, per player, and tested.

F1 ruled out five explanations and found no single defect. This does not try to fix
anything. It discloses the disagreement in the three forms that let a reader judge it.

F4a  PER VIEW. The four impact views are carried separately end to end and never
     averaged, so a team where all four disagree with the market in the same direction
     is a different object from one where the mean happens to differ. ALL-VIEWS means
     every fork sits on the same side of the market; MIXED means the forks straddle it.
     A MIXED disagreement is not really the model disagreeing with the market, it is the
     model disagreeing with itself.

F4b  PER PLAYER. Every player whose minutes-weighted contribution to his team's rollup
     exceeds 1.0 net points, on a top-10 disagreement team, with all four views and his
     RAPM possessions. **No caps and no edits.** This is a disclosure table for the
     methods appendix, so a reader can see exactly which individual estimates the tails
     rest on and form their own view.

F4c  THE DEPTH-VERSUS-STARS HYPOTHESIS, AS A NUMBER. The suspicion from F1 is that where
     the two disagree, the model likes depth and the market likes star concentration.
     That is testable: measure each team's TOP-HEAVINESS as the share of its
     minutes-weighted impact sitting in its best two and best three players, and
     correlate it against model-minus-market across all 30. A negative correlation is
     the hypothesis confirmed (top-heavy teams priced below the market by us).

    python kuminga/scripts/f4_per_view_disagreement.py
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

from kuminga.lib import kfreeze, runlog                        # noqa: E402
from build_strengths import build_impacts, add_rookie_impacts  # noqa: E402

MKT = os.path.join(REPO, "kuminga", "outputs", "market_devig_2026_27.csv")
SIM = os.path.join(REPO, "kuminga", "outputs", "preaging", "sim_all30_2026_27.csv")
ROT = os.path.join(REPO, "kuminga", "outputs", "rotations_2026_27.csv")
POOL = os.path.join(REPO, "kuminga", "outputs", "player_pool_2026_27.csv")
VALUE = os.path.join(REPO, "offseason", "data", "player_value.csv")
DARKO = os.path.join(REPO, "offseason", "data", "darko-dpm-leaderboard.csv")
OUT_A = os.path.join(REPO, "kuminga", "outputs", "f4a_per_view_disagreement.csv")
OUT_B = os.path.join(REPO, "kuminga", "outputs", "f4b_tail_players.csv")
OUT_C = os.path.join(REPO, "kuminga", "outputs", "f4c_top_heaviness.csv")
FORKS = ["consensus", "rapm", "box", "darko"]
NAMED = ["BOS", "CHA", "DET", "HOU", "SAS", "PHI", "OKC", "NYK"]
CONTRIB_MIN = 1.0


def main():
    with runlog.run("f4_per_view_disagreement",
                    inputs={"contrib_threshold": CONTRIB_MIN}) as r:
        mk = pd.read_csv(MKT).set_index("team_abbr")
        sim = pd.read_csv(SIM)
        rot = pd.read_csv(ROT)
        rot = rot[rot.scenario == "current"]
        pool = pd.read_csv(POOL)
        value = pd.read_csv(VALUE)
        darko = pd.read_csv(DARKO)
        darko.columns = [c.strip().lstrip("﻿") for c in darko.columns]
        bio, _ = kfreeze.load("player_bio")
        imps, _ = build_impacts(value, darko, bio)
        add_rookie_impacts(imps, pool)

        # ---- F4a: per view ----------------------------------------------------
        t = sim.pivot_table(index="team_abbr", columns="fork", values="title_current")
        t = t.reindex(columns=FORKS) * 100
        ranks = t.rank(ascending=False).astype(int)
        rows = []
        for tm in t.index:
            mkt = float(mk.loc[tm, "market_pct"])
            diffs = {f: float(t.loc[tm, f]) - mkt for f in FORKS}
            same = (all(v > 0 for v in diffs.values()) or
                    all(v < 0 for v in diffs.values()))
            rows.append(dict(
                team=tm, market_pct=mkt, market_rank=int(mk.loc[tm, "market_rank"]),
                mean_pct=float(t.loc[tm].mean()),
                label="ALL-VIEWS" if same else "MIXED",
                direction=("model high" if diffs["consensus"] > 0 else "model low"),
                **{"pct_" + f: float(t.loc[tm, f]) for f in FORKS},
                **{"rank_" + f: int(ranks.loc[tm, f]) for f in FORKS},
                **{"diff_" + f: diffs[f] for f in FORKS},
                abs_mean_gap=abs(float(t.loc[tm].mean()) - mkt)))
        a = pd.DataFrame(rows).set_index("team")
        a = a.sort_values("abs_mean_gap", ascending=False)
        a.reset_index().to_csv(OUT_A, index=False)

        big = a[a.abs_mean_gap > 0.5]
        r.note("F4a. THE %d DISAGREEMENTS, PER VIEW. ALL-VIEWS means all four forks sit "
               "on the same side of the market." % len(big))
        r.note("  %-4s %7s %6s | %-33s | %-19s | %s"
               % ("team", "market", "mean", "title % by view (con/rapm/box/darko)",
                  "rank by view", "label"))
        for tm, x in big.iterrows():
            r.note("  %-4s %6.2f%% %5.2f%% | %6.2f %6.2f %6.2f %6.2f | "
                   "%3d %3d %3d %3d | %s"
                   % (tm, x.market_pct, x.mean_pct, x.pct_consensus, x.pct_rapm,
                      x.pct_box, x.pct_darko, x.rank_consensus, x.rank_rapm,
                      x.rank_box, x.rank_darko, x.label))
        n_all = int((big.label == "ALL-VIEWS").sum())
        r.note("  %d of %d are ALL-VIEWS; %d are MIXED, where the model disagrees with "
               "itself as much as with the market." % (n_all, len(big), len(big) - n_all))
        r.note("")
        r.note("  THE EIGHT NAMED TEAMS:")
        for tm in NAMED:
            x = a.loc[tm]
            r.note("    %-4s %-9s %-11s market %5.2f%% (rk %2d) | model %5.2f%% "
                   "| views %5.2f %5.2f %5.2f %5.2f | ranks %2d %2d %2d %2d"
                   % (tm, x.label, x.direction, x.market_pct, x.market_rank,
                      x.mean_pct, x.pct_consensus, x.pct_rapm, x.pct_box, x.pct_darko,
                      x.rank_consensus, x.rank_rapm, x.rank_box, x.rank_darko))

        # ---- F4b: tail players ------------------------------------------------
        top10 = big.head(10).index.tolist()
        prow = []
        for tm in top10:
            g = rot[rot.team_abbr == tm]
            for _, x in g.iterrows():
                pid = x.player_id
                if pd.isna(pid):
                    continue
                key = str(int(pid))
                vals = {}
                for f in FORKS:
                    v = imps[f].get(key)
                    vals[f] = (float(v.get("off", 0)) - float(v.get("def", 0))
                               if isinstance(v, dict) else np.nan)
                contrib = float(x.mpg) / 48.0 * vals["consensus"]
                if abs(contrib) <= CONTRIB_MIN:
                    continue
                pv = value[value.player_id == pid]
                prow.append(dict(
                    team=tm, player=x.player_name, mpg=round(float(x.mpg), 1),
                    contribution=round(contrib, 2),
                    possessions=(int(pv.possessions.iloc[0])
                                 if len(pv) and pd.notna(pv.possessions.iloc[0])
                                 else None),
                    net_sd=(round(float(pv.net_sd.iloc[0]), 2)
                            if len(pv) and pd.notna(pv.net_sd.iloc[0]) else None),
                    **{f: round(vals[f], 2) for f in FORKS}))
        b = pd.DataFrame(prow).sort_values(["team", "contribution"],
                                           ascending=[True, False])
        b.to_csv(OUT_B, index=False)
        r.note("")
        r.note("F4b. TAIL PLAYERS: contribution above %.1f net points, top-10 "
               "disagreement teams. NO CAPS, NO EDITS, disclosure only." % CONTRIB_MIN)
        r.note("    %-4s %-22s %5s %6s %7s | %6s %6s %6s %6s"
               % ("team", "player", "mpg", "contr", "poss", "cons", "rapm", "box",
                  "darko"))
        for _, x in b.iterrows():
            r.note("    %-4s %-22s %5.1f %+6.2f %7s | %6.2f %6.2f %6.2f %6.2f"
                   % (x["team"], x["player"], x["mpg"], x["contribution"],
                      x["possessions"] if x["possessions"] else "-",
                      x["consensus"], x["rapm"], x["box"], x["darko"]))
        r.note("    %d players clear the threshold across %d teams"
               % (len(b), b.team.nunique()))

        # ---- F4c: top-heaviness ------------------------------------------------
        crow = []
        for tm, g in rot.groupby("team_abbr"):
            g = g.copy()
            g["c"] = g.mpg / 48.0 * g.consensus_net
            pos = g.c.clip(lower=0).sort_values(ascending=False)
            tot = float(pos.sum()) or 1.0
            crow.append(dict(team=tm,
                             top2_share=float(pos.head(2).sum()) / tot,
                             top3_share=float(pos.head(3).sum()) / tot,
                             total_pos_contrib=tot))
        c = pd.DataFrame(crow).set_index("team")
        c = c.join(a[["market_pct", "mean_pct", "label"]])
        c["model_minus_market"] = c.mean_pct - c.market_pct
        c.reset_index().to_csv(OUT_C, index=False)

        r2 = c.top2_share.corr(c.model_minus_market)
        r3 = c.top3_share.corr(c.model_minus_market)
        r.note("")
        r.note("F4c. THE DEPTH-VERSUS-STARS HYPOTHESIS, AS A NUMBER, n = 30 teams.")
        r.note("  corr(top-2 share of positive impact, model minus market) = %+.3f" % r2)
        r.note("  corr(top-3 share of positive impact, model minus market) = %+.3f" % r3)
        if r3 < -0.3:
            r.note("  NEGATIVE and material: top-heavy teams are priced BELOW the market "
                   "by this model, which is the depth-versus-stars hypothesis CONFIRMED.")
        elif r3 > 0.3:
            r.note("  POSITIVE: top-heavy teams are priced ABOVE the market, which is "
                   "the OPPOSITE of the hypothesis.")
        else:
            r.note("  NEAR ZERO. The depth-versus-stars story is NOT supported. "
                   "Whatever separates the model from the market, it is not how "
                   "concentrated a roster's impact is.")
        r.note("  most top-heavy: " + ", ".join(
            "%s %.2f" % (i, x.top3_share) for i, x in c.nlargest(4, "top3_share").iterrows()))
        r.note("  flattest:       " + ", ".join(
            "%s %.2f" % (i, x.top3_share) for i, x in c.nsmallest(4, "top3_share").iterrows()))
        mn = c.loc["MIN"]
        r.note("  MIN top-3 share %.2f, model minus market %+.2fpp"
               % (mn.top3_share, mn.model_minus_market))
        r.output(OUT_A, rows=len(a))
        r.output(OUT_B, rows=len(b))
        r.output(OUT_C, rows=len(c))

    print()
    print(big[["market_pct", "mean_pct", "label", "direction"]].round(2).to_string())


if __name__ == "__main__":
    main()

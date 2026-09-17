#!/usr/bin/env python3
"""R5: the honesty rail on both aging bases.

Section 1 of the piece says the model and the market agree on the shape of the league
(rank correlation), disagree about specific teams, and that most of those disagreements
are ALL-VIEWS. Those three figures were only ever computed on the un-aged basis
(`market_devig.py`, `f4_per_view_disagreement.py`). The shipping rule asks a claim to
hold on both bases, so this script recomputes them on the aged basis with the same
definitions and reports Minnesota's and Boston's position on each.

Definitions, unchanged from the two source scripts:
  rank correlation   Spearman, each view's title odds against the proportional de-vig
  disagreement       |mean of four views - market| > 0.5 points
  ALL-VIEWS          all four views sit on the same side of the market

  G1  on the un-aged basis this script reproduces the sheet's rank correlation band, the
      disagreement count and the ALL-VIEWS count exactly, or it fails.

    python kuminga/scripts/r5_honesty_rail_bases.py
"""
from __future__ import annotations

import hashlib
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO)

from kuminga.lib import runlog  # noqa: E402

OUTDIR = os.path.join(REPO, "kuminga", "outputs")
MKT = os.path.join(OUTDIR, "market_devig_2026_27.csv")
F4A = os.path.join(OUTDIR, "f4a_per_view_disagreement.csv")
SIMS = {"unaged": os.path.join(OUTDIR, "preaging", "sim_all30_2026_27.csv"),
        "aged": os.path.join(OUTDIR, "aged", "sim_all30_2026_27.csv")}
OUT = os.path.join(OUTDIR, "r5_honesty_rail_bases.csv")
OUT_T = os.path.join(OUTDIR, "r5_disagreements_bases.csv")
FORKS = ["consensus", "rapm", "box", "darko"]
FLOOR = 0.5


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    inputs = {k: {"path": v, "sha256": sha(v)} for k, v in SIMS.items()}
    inputs["market"] = {"path": MKT, "sha256": sha(MKT)}
    with runlog.run("r5_honesty_rail_bases", inputs=inputs) as r:
        mk = pd.read_csv(MKT).set_index("team_abbr")
        mkt_pct = mk.market_prop * 100
        rail, teams = [], []
        for basis, path in SIMS.items():
            sim = pd.read_csv(path)
            t = (sim.pivot_table(index="team_abbr", columns="fork", values="title_current")
                 .reindex(columns=FORKS) * 100)
            t = t.reindex(mk.index)
            ranks = t.rank(ascending=False, method="min").astype(int)
            cors = {f: float(t[f].rank().corr(mk.market_prop.rank())) for f in FORKS}
            diff = t.sub(mkt_pct, axis=0)
            mean_gap = t.mean(axis=1) - mkt_pct
            same = (diff > 0).all(axis=1) | (diff < 0).all(axis=1)
            dis = mean_gap.abs() > FLOOR
            for tm in t.index:
                teams.append(dict(basis=basis, team=tm, market_pct=float(mkt_pct[tm]),
                                  market_rank=int(mk.loc[tm, "market_rank"]),
                                  mean_pct=float(t.loc[tm].mean()), mean_gap=float(mean_gap[tm]),
                                  disagreement=bool(dis[tm]),
                                  label="ALL-VIEWS" if same[tm] else "MIXED",
                                  views_above_market=int((diff.loc[tm] > 0).sum()),
                                  **{"pct_" + f: float(t.loc[tm, f]) for f in FORKS},
                                  **{"rank_" + f: int(ranks.loc[tm, f]) for f in FORKS}))
            rail.append(dict(basis=basis, rankcorr_lo=min(cors.values()),
                             rankcorr_hi=max(cors.values()),
                             **{"rankcorr_" + f: cors[f] for f in FORKS},
                             n_disagree=int(dis.sum()), n_allviews=int((dis & same).sum())))
            r.note("%s: rank correlation %.2f to %.2f; %d disagreements, %d ALL-VIEWS"
                   % (basis, min(cors.values()), max(cors.values()), dis.sum(), (dis & same).sum()))
            for tm in ("MIN", "BOS", "SAS"):
                r.note("  %s market %.2f%% (rank %d) | views %s | ranks %s | %s, %d of 4 above market"
                       % (tm, mkt_pct[tm], mk.loc[tm, "market_rank"],
                          " ".join("%.2f" % t.loc[tm, f] for f in FORKS),
                          " ".join(str(ranks.loc[tm, f]) for f in FORKS),
                          "ALL-VIEWS" if same[tm] else "MIXED", (diff.loc[tm] > 0).sum()))
        rail = pd.DataFrame(rail).set_index("basis")
        teams = pd.DataFrame(teams)

        # G1: reproduce the un-aged sheet figures from their source scripts
        cors_src = [float(mk[f].rank().corr(mk.market_prop.rank())) for f in FORKS]
        f4a = pd.read_csv(F4A).set_index("team")
        dis_src = mk[mk.diff_pp.abs() > FLOOR].index
        want = dict(lo=round(min(cors_src), 6), hi=round(max(cors_src), 6), n=len(dis_src),
                    allv=int((f4a.loc[dis_src, "label"] == "ALL-VIEWS").sum()))
        got = dict(lo=round(rail.loc["unaged", "rankcorr_lo"], 6),
                   hi=round(rail.loc["unaged", "rankcorr_hi"], 6),
                   n=int(rail.loc["unaged", "n_disagree"]), allv=int(rail.loc["unaged", "n_allviews"]))
        r.note("G1 un-aged reproduction: source %s, this script %s" % (want, got))
        if want != got:
            raise RuntimeError("G1 failed: the un-aged rail does not reproduce the source scripts")

        # which disagreements change label between bases
        u = teams[teams.basis == "unaged"].set_index("team")
        a = teams[teams.basis == "aged"].set_index("team")
        for tm in u.index:
            if (u.loc[tm, "disagreement"] or a.loc[tm, "disagreement"]) and (
                    u.loc[tm, "label"] != a.loc[tm, "label"] or
                    u.loc[tm, "disagreement"] != a.loc[tm, "disagreement"]):
                r.note("  changes between bases: %s un-aged %s%s, aged %s%s"
                       % (tm, u.loc[tm, "label"], "" if u.loc[tm, "disagreement"] else " (not a disagreement)",
                          a.loc[tm, "label"], "" if a.loc[tm, "disagreement"] else " (not a disagreement)"))

        rail.reset_index().to_csv(OUT, index=False)
        teams.to_csv(OUT_T, index=False)
        r.output(OUT, rows=len(rail))
        r.output(OUT_T, rows=len(teams))


if __name__ == "__main__":
    main()

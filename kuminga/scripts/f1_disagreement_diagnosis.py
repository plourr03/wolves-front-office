#!/usr/bin/env python3
"""F1: where the model and the market disagree, and what is driving it.

The market study found 20 of 30 teams differing by more than the materiality floor, with
the model making Boston the title favourite and Charlotte a top-five team. Neither is a
defensible reading of those rosters, so the disagreement is diagnostic of us. This opens
the ten biggest gaps and looks at what the rollup is actually made of.

FOR EACH TEAM, the top eight by projected minutes with:

  IMPACT PER VIEW      the four forks side by side, because a team can be carried by one
  SAMPLE SIZE          RAPM possessions behind the estimate, and the `reliable` flag.
                       A high impact on 400 possessions is a prior, not a measurement.
  INJURY STATUS        regular-season availability from the R7 table
  RETURN STATUS        whether the player is coming back from a season-long absence.
                       Detected as: on a 2026-27 roster, carrying an impact estimate,
                       but with no 2025-26 baseline row. Those players are being priced
                       on their last healthy season with no discount at all, which is
                       the single most likely source of an inflated rollup.

WHAT THIS SCRIPT DOES NOT DO. It does not fix anything. It is the diagnosis that F2 and
F3 act on, and it is kept separate so the corrections can be argued with the evidence in
front of them rather than asserted.

    python kuminga/scripts/f1_disagreement_diagnosis.py
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
ROT = os.path.join(REPO, "kuminga", "outputs", "rotations_2026_27.csv")
POOL = os.path.join(REPO, "kuminga", "outputs", "player_pool_2026_27.csv")
VALUE = os.path.join(REPO, "offseason", "data", "player_value.csv")
DARKO = os.path.join(REPO, "offseason", "data", "darko-dpm-leaderboard.csv")
INJ = os.path.join(REPO, "kuminga", "data", "injuries_2026_27.csv")
OUT = os.path.join(REPO, "kuminga", "outputs", "f1_disagreement_ranking.csv")
OUT_D = os.path.join(REPO, "kuminga", "outputs", "f1_rollup_decomposition.csv")
FORKS = ["consensus", "rapm", "box", "darko"]
TOPN = 10


def main():
    with runlog.run("f1_disagreement_diagnosis", inputs={"top_n": TOPN}) as r:
        mk = pd.read_csv(MKT)
        rot = pd.read_csv(ROT)
        pool = pd.read_csv(POOL)
        value = pd.read_csv(VALUE)
        darko = pd.read_csv(DARKO)
        darko.columns = [c.strip().lstrip("﻿") for c in darko.columns]
        bio, _ = kfreeze.load("player_bio")
        imps, _ = build_impacts(value, darko, bio)
        add_rookie_impacts(imps, pool)
        inj = pd.read_csv(INJ)

        # ---- rank the disagreements ------------------------------------------
        mk["abs_gap"] = mk.diff_pp.abs()
        mk = mk.sort_values("abs_gap", ascending=False)
        big = mk[mk.abs_gap > 0.5].copy()
        big["rank_gap"] = np.arange(1, len(big) + 1)
        big[["team_abbr", "rank_gap", "market_pct", "market_rank", "model_pct",
             "model_rank", "diff_pp", "abs_gap"]].to_csv(OUT, index=False)

        r.note("THE %d DISAGREEMENTS ABOVE THE FLOOR, ranked by size:" % len(big))
        for _, x in big.iterrows():
            r.note("  %2d. %-4s market %5.2f%% (rk %2d) | model %5.2f%% (rk %2d) | "
                   "%+6.2fpp %s" % (x.rank_gap, x.team_abbr, x.market_pct,
                                    int(x.market_rank), x.model_pct, int(x.model_rank),
                                    x.diff_pp,
                                    "MODEL HIGH" if x.diff_pp > 0 else "model low"))

        # ---- who is a return-from-absence ------------------------------------
        base_ids = set(pool[pool.scenario == "baseline"].player_id.dropna())
        cur = pool[pool.scenario == "current"].copy()
        cur["returning"] = (~cur.player_id.isin(base_ids)) & cur.player_id.notna() \
            & (cur.impact_source == "player_value")
        n_ret = int(cur.returning.sum())
        r.note("")
        r.note("RETURN-FROM-ABSENCE candidates league-wide: %d players carry a "
               "measured impact but have no 2025-26 row, so they are priced on their "
               "last healthy season with no discount." % n_ret)

        vs = value.set_index("player_id")
        inj_by = {str(x.player).lower(): x for _, x in inj.iterrows()}

        rows = []
        top = big.head(TOPN).team_abbr.tolist()
        for tm in top:
            g = rot[(rot.scenario == "current") & (rot.team_abbr == tm)]
            g = g.sort_values("mpg", ascending=False).head(8)
            for _, x in g.iterrows():
                pid = x.player_id
                pv = vs.loc[pid] if pid in vs.index else None
                key = str(x.player_name).lower()
                ij = inj_by.get(key)
                rec = dict(team=tm, player=x.player_name, mpg=round(float(x.mpg), 1),
                           poss=(float(pv.possessions) if pv is not None
                                 and pd.notna(pv.possessions) else np.nan),
                           reliable=(bool(pv.reliable) if pv is not None
                                     and pd.notna(pv.reliable) else None),
                           net_sd=(float(pv.net_sd) if pv is not None
                                   and pd.notna(pv.net_sd) else np.nan),
                           rs_avail=float(x.rs_avail),
                           returning=bool(cur[cur.player_id == pid].returning.any()),
                           injury=(str(ij.injury)[:40] if ij is not None else ""))
                for f in FORKS:
                    v = imps[f].get(str(int(pid))) if pd.notna(pid) else None
                    # SIGN CONVENTION: net = off - def. A NEGATIVE def is GOOD
                    # defence (points prevented), which build_strengths documents and
                    # the value file confirms (max |net - (off-def)| = 0.01 across the
                    # league, against 14.15 for off+def). An earlier version of this
                    # diagnostic summed them and produced Wembanyama at -5.26 and Luka
                    # Garza at +5.17, which is what a flipped defensive sign looks like.
                    rec[f] = (round(float(v.get("off", 0)) - float(v.get("def", 0)), 2)
                              if isinstance(v, dict) else np.nan)
                rows.append(rec)
        dec = pd.DataFrame(rows)
        dec.to_csv(OUT_D, index=False)

        r.note("")
        r.note("ROLLUP DECOMPOSITION, top %d disagreements, top 8 by minutes:" % TOPN)
        for tm in top:
            sub = dec[dec.team == tm]
            gap = float(big[big.team_abbr == tm].diff_pp.iloc[0])
            thin = sub[(sub.poss < 2000) | (sub.reliable == False)]  # noqa: E712
            ret = sub[sub.returning]
            r.note("")
            r.note("  %s  (%+.2fpp, model %s)" % (tm, gap,
                                                  "HIGH" if gap > 0 else "low"))
            r.note("    %-22s %5s %6s %5s %6s %6s %6s %6s  %s"
                   % ("player", "mpg", "poss", "rel", "cons", "rapm", "box", "darko",
                      "flags"))
            for _, x in sub.iterrows():
                flags = []
                if x.returning:
                    flags.append("RETURNING")
                if pd.notna(x.poss) and x.poss < 2000:
                    flags.append("thin(%d)" % int(x.poss))
                if x.rs_avail < 1:
                    flags.append("avail %.2f" % x.rs_avail)
                r.note("    %-22s %5.1f %6s %5s %6s %6s %6s %6s  %s"
                       % (x.player, x.mpg,
                          "%d" % x.poss if pd.notna(x.poss) else "-",
                          "Y" if x.reliable else ("N" if x.reliable is False else "-"),
                          x.consensus, x.rapm, x.box, x.darko, ", ".join(flags)))
            r.note("    -> %d of 8 thin or unreliable; %d returning from absence"
                   % (len(thin), len(ret)))

        # ---- the two named teams ---------------------------------------------
        r.note("")
        r.note("WHAT DRIVES THE TWO NAMED TEAMS")
        for tm in ("BOS", "CHA"):
            sub = dec[dec.team == tm]
            if not len(sub):
                r.note("  %s is not in the top %d gaps" % (tm, TOPN))
                continue
            gap = float(big[big.team_abbr == tm].diff_pp.iloc[0])
            wsum = {f: float((sub.mpg * sub[f]).sum() / sub.mpg.sum()) for f in FORKS}
            r.note("  %s, %+.2fpp. Minutes-weighted impact of the top 8 by view: %s"
                   % (tm, gap, ", ".join("%s %.2f" % (f, wsum[f]) for f in FORKS)))
            lead = sub.assign(contrib=sub.mpg * sub.consensus).nlargest(3, "contrib")
            for _, x in lead.iterrows():
                r.note("    carried by %-20s %.1f mpg at consensus %+.2f "
                       "(%s poss, %s)"
                       % (x.player, x.mpg, x.consensus,
                          "%d" % x.poss if pd.notna(x.poss) else "n/a",
                          "RETURNING" if x.returning else
                          ("thin" if pd.notna(x.poss) and x.poss < 2000 else "ok")))
        r.output(OUT, rows=len(big))
        r.output(OUT_D, rows=len(dec))

    print()
    print(big[["team_abbr", "rank_gap", "market_pct", "model_pct", "diff_pp"]]
          .round(2).to_string(index=False))


if __name__ == "__main__":
    main()

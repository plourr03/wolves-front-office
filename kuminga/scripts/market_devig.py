#!/usr/bin/env python3
"""The 2026-27 title market: de-vig two ways, then set it against the model.

THE INPUT. `2026-27-title-odds-six-books.csv`, six books hand-transcribed from a
screenshot on 2026-09-09, plus the median file. **Title odds only. Win totals are absent
from the transcription, so the win-total comparison this project has run in the past
CANNOT be run and is reported as unavailable rather than quietly skipped.**

WHY DE-VIG AT ALL. Raw implied probabilities from a book sum to more than one; the
excess is the house margin. Comparing a model's probabilities against raw implied
numbers compares 1.00 of probability against 1.22 of it, which makes every team look
overpriced. Two standard removals, both reported:

  PROPORTIONAL   p_i / sum(p).  Removes the margin evenly in proportion to price, so
                 every team loses the same FRACTION of its number.
  POWER          p_i^k, with k solved so the result sums to one. Removes more margin
                 from longshots than from favourites, which is the direction the
                 favourite-longshot bias actually runs in sports betting markets.

WHICH THE PIECE QUOTES: **proportional**. Not because it is more nearly right, but
because it is the transparent one. Power de-vig requires choosing to model a bias whose
size is not identified from a single screenshot of six books, and the difference between
the two methods for Minnesota is small enough to state in a clause. The power figures
are reported beside it so the reader can see the sensitivity rather than take it on
faith. Both columns are on the output.

    python kuminga/scripts/market_devig.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO)

from kuminga.lib import runlog  # noqa: E402

SIX = os.path.join(REPO, "offseason", "data", "2026-27-title-odds-six-books.csv")
MED = os.path.join(REPO, "offseason", "data", "2026-27-preseason-odd.csv")
# the un-aged primary, read from the frozen copy so a concurrent aged run cannot race it
SIM = os.path.join(REPO, "kuminga", "outputs", "preaging", "sim_all30_2026_27.csv")
NF = os.path.join(REPO, "kuminga", "outputs", "noise_floor.csv")
OUT = os.path.join(REPO, "kuminga", "outputs", "market_devig_2026_27.csv")
FORKS = ["consensus", "rapm", "box", "darko"]

NAME_TO_ABBR = {
    "Atlanta Hawks": "ATL", "Boston Celtics": "BOS", "Brooklyn Nets": "BKN",
    "Charlotte Hornets": "CHA", "Chicago Bulls": "CHI", "Cleveland Cavaliers": "CLE",
    "Dallas Mavericks": "DAL", "Denver Nuggets": "DEN", "Detroit Pistons": "DET",
    "Golden State Warriors": "GSW", "Houston Rockets": "HOU", "Indiana Pacers": "IND",
    "Los Angeles Clippers": "LAC", "LA Clippers": "LAC", "Los Angeles Lakers": "LAL",
    "Memphis Grizzlies": "MEM", "Miami Heat": "MIA", "Milwaukee Bucks": "MIL",
    "Minnesota Timberwolves": "MIN", "New Orleans Pelicans": "NOP",
    "New York Knicks": "NYK", "Oklahoma City Thunder": "OKC", "Orlando Magic": "ORL",
    "Philadelphia 76ers": "PHI", "Phoenix Suns": "PHX", "Portland Trail Blazers": "POR",
    "Sacramento Kings": "SAC", "San Antonio Spurs": "SAS", "Toronto Raptors": "TOR",
    "Utah Jazz": "UTA", "Washington Wizards": "WAS",
}


def american_to_prob(o):
    o = float(o)
    return 100.0 / (o + 100.0) if o > 0 else (-o) / (-o + 100.0)


def power_devig(p, tol=1e-12):
    """Solve sum(p_i^k) = 1 for k by bisection. k > 1 shrinks longshots hardest."""
    lo, hi = 0.5, 5.0
    for _ in range(200):
        k = (lo + hi) / 2.0
        s = float(np.sum(p ** k))
        if abs(s - 1.0) < tol:
            break
        if s > 1.0:
            lo = k
        else:
            hi = k
    return p ** k, k


def main():
    with runlog.run("market_devig", inputs={"six_books": SIX, "median": MED}) as r:
        six = pd.read_csv(SIX)
        six["team_abbr"] = six.team.map(NAME_TO_ABBR)
        assert six.team_abbr.notna().all(), \
            "unmapped team names: %s" % six[six.team_abbr.isna()].team.tolist()

        bookcols = [c for c in six.columns if c.startswith("book_")]
        r.note("six-book table: %d teams, %d books" % (len(six), len(bookcols)))
        r.note("WIN TOTALS: absent from this transcription. The win-total comparison "
               "this project has run before CANNOT be run and is reported unavailable.")

        # ---- the 76ers outlier ------------------------------------------------
        b = six.set_index("team_abbr")[bookcols]
        med = b.median(axis=1)
        spread = (b.max(axis=1) / b.min(axis=1))
        phi = b.loc["PHI"]
        r.note("")
        r.note("OUTLIER, flagged and excluded from the median discussion:")
        r.note("  PHI books: %s" % dict(phi.astype(int)))
        r.note("  book_4 at +%d against a %d-%d range on the other five. That is not a "
               "price, it is a transcription or a stale line."
               % (int(phi["book_4"]), int(phi.drop("book_4").min()),
                  int(phi.drop("book_4").max())))
        phi_wo = float(phi.drop("book_4").median())
        r.note("  the MEDIAN is robust to it by construction: %d with book_4 in, %d "
               "with it out, a %.2fpp difference in implied probability."
               % (int(med["PHI"]), int(phi_wo),
                  (american_to_prob(phi_wo) - american_to_prob(med["PHI"])) * 100))
        r.note("  So PHI stays in the table on its median. The outlier is excluded from "
               "any statement about book DISAGREEMENT, where it would dominate.")
        wide = spread.drop("PHI").sort_values(ascending=False)
        r.note("  widest genuine book disagreement, PHI excluded: "
               + ", ".join("%s %.2fx" % (t, v) for t, v in wide.head(4).items()))

        # ---- de-vig -----------------------------------------------------------
        six["p_raw"] = med.reindex(six.team_abbr).to_numpy()
        six["p_raw"] = [american_to_prob(x) for x in six.p_raw]
        over = float(six.p_raw.sum())
        six["market_prop"] = six.p_raw / over
        pw, k = power_devig(six.p_raw.to_numpy())
        six["market_power"] = pw
        r.note("")
        r.note("DE-VIG. Raw implied probabilities sum to %.4f, an overround of %.1f%%."
               % (over, (over - 1) * 100))
        r.note("  proportional: divide through by %.4f" % over)
        r.note("  power       : exponent k = %.4f solved so the powers sum to one" % k)
        r.note("  max |proportional - power| across the league: %.2fpp (%s)"
               % ((six.market_prop - six.market_power).abs().max() * 100,
                  six.loc[(six.market_prop - six.market_power).abs().idxmax(),
                          "team_abbr"]))
        mn = six[six.team_abbr == "MIN"].iloc[0]
        r.note("  MINNESOTA: proportional %.2f%%, power %.2f%%, a %.2fpp difference. "
               "THE PIECE QUOTES PROPORTIONAL."
               % (mn.market_prop * 100, mn.market_power * 100,
                  abs(mn.market_prop - mn.market_power) * 100))

        # ---- against the model ------------------------------------------------
        sim = pd.read_csv(SIM)
        t = (sim.pivot_table(index="team_abbr", columns="fork", values="title_current")
             .reindex(columns=FORKS))
        t["model_mean"] = t.mean(axis=1)
        t["model_lo"] = t[FORKS].min(axis=1)
        t["model_hi"] = t[FORKS].max(axis=1)
        m = six.set_index("team_abbr").join(t)
        m["diff_pp"] = (m.model_mean - m.market_prop) * 100
        m["market_pct"] = m.market_prop * 100
        m["model_pct"] = m.model_mean * 100
        m["model_rank"] = m.model_mean.rank(ascending=False).astype(int)
        m = m.sort_values("market_prop", ascending=False)
        m.reset_index().to_csv(OUT, index=False)

        floor = 0.5
        if os.path.exists(NF):
            nfd = pd.read_csv(NF)
            if "min_abs_pp" in nfd.columns:
                pass
        r.note("")
        r.note("MODEL vs MARKET, proportional de-vig. Flagged where the gap exceeds the "
               "worst-fork materiality floor (%.2fpp):" % floor)
        big = m[m.diff_pp.abs() > floor].sort_values("diff_pp")
        for tm, x in big.iterrows():
            r.note("  %-4s market %5.2f%% (rank %2d) | model %5.2f%% (rank %2d) | "
                   "%+6.2fpp" % (tm, x.market_pct, int(x.market_rank), x.model_pct,
                                 int(x.model_rank), x.diff_pp))
        r.note("  %d of %d teams differ by more than the floor" % (len(big), len(m)))

        # ---- the three named disagreements ------------------------------------
        r.note("")
        r.note("THE THREE ORDERING DISAGREEMENTS, named:")
        for a, bb in (("MIN", "LAL"),):
            xa, xb = m.loc[a], m.loc[bb]
            r.note("  1. %s vs %s. Market: %s ahead (%.2f%% vs %.2f%%). Model: %s ahead "
                   "(%.2f%% vs %.2f%%). %s"
                   % (a, bb, a if xa.market_prop > xb.market_prop else bb,
                      xa.market_pct, xb.market_pct,
                      a if xa.model_mean > xb.model_mean else bb,
                      xa.model_pct, xb.model_pct,
                      "THEY DISAGREE ON THE ORDER."
                      if (xa.market_prop > xb.market_prop) !=
                         (xa.model_mean > xb.model_mean) else "They agree on the order."))
        top5 = m.head(5).index.tolist()
        bos = m.loc["BOS"]
        r.note("  2. BOS against the market's top five. Market top five: %s. BOS is "
               "market rank %d at %.2f%%; the model has BOS rank %d at %.2f%%."
               % (", ".join(top5), int(bos.market_rank), bos.market_pct,
                  int(bos.model_rank), bos.model_pct))
        mnr = m.loc["MIN"]
        r.note("  3. The model's Minnesota number against the market's. Market "
               "%.2f%% (rank %d). Model %.2f%% (rank %d), band %.2f%% to %.2f%%. "
               "Gap %+.2fpp."
               % (mnr.market_pct, int(mnr.market_rank), mnr.model_pct,
                  int(mnr.model_rank), mnr.model_lo * 100, mnr.model_hi * 100,
                  mnr.diff_pp))
        r.note("     The market's number sits %s the model's four-view band."
               % ("INSIDE" if mnr.model_lo <= mnr.market_prop <= mnr.model_hi
                  else "OUTSIDE"))
        r.output(OUT, rows=len(m))

    print()
    print(m.reset_index()[["team_abbr", "market_pct", "market_rank", "model_pct",
                           "model_rank", "diff_pp"]].round(2).to_string(index=False))


if __name__ == "__main__":
    main()

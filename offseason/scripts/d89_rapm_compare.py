#!/usr/bin/env python3
"""D89: RAPM before and after the possession points fix, with the bias direction on record.

Possession points used to be credited to whichever team the tracker had on offense, so an
and-one free throw went to the OTHER team: the fouled shooter's team lost the point and
the defending team gained it. A player who draws many and-ones therefore had his offensive
RAPM pushed down. This compares the two fits and tests that prediction directly, by
splitting the shift by each player's and-one rate.

Inputs: two fits of `build_rapm.py`, one on the frozen pre-D89 cache and one on the
rebuilt cache. And-one counts come from play-by-play: a free throw of "1 of 1" whose
previous event by the same player in the same period was a made field goal.

  G1  reported, not enforced: the possession GRID also changes slightly. An and-one free
      throw used to END a possession, so the old grid carried a phantom possession for
      each one. That is 2.2% fewer possessions, all of them `made_ft`, so the fix moves
      both the points and a small number of possession boundaries.

    python offseason/scripts/d89_rapm_compare.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
POSTMORTEM = os.path.join(REPO, "postmortem")
sys.path.insert(0, POSTMORTEM)
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(POSTMORTEM, ".env"))
except ImportError:
    pass
from lib import db  # noqa: E402

DATA = os.path.join(REPO, "offseason", "data")
BEFORE = os.path.join(DATA, "player_value_pre_d89.csv")
AFTER = os.path.join(DATA, "player_value.csv")
ANDONE = os.path.join(DATA, "and_one_rates.csv")
OUT = os.path.join(DATA, "d89_rapm_before_after.csv")
OUT_MD = os.path.join(REPO, "offseason", "outputs", "d89_rapm_refit.md")
NAMED = ["Jonathan Kuminga", "Anthony Edwards", "Rudy Gobert", "LaMelo Ball", "Naz Reid",
         "Moussa Diabate", "Kon Knueppel", "Neemias Queta"]

AND_ONE_SQL = """
with games as (
  select distinct game_id from nba.nba_games where (season_id % 10000) in (2023, 2024, 2025)
), ev as (
  select p.game_id, p.period, p.person_id, p.action_number, p.action_type, p.sub_type,
         p.shot_result
  from nba.nba_play_by_play p join games using (game_id)
  where p.person_id is not null and p.person_id <> 0
), tagged as (
  select *,
         lag(action_type) over w prev_type,
         lag(shot_result) over w prev_res,
         lag(period) over w prev_period
  from ev
  window w as (partition by game_id, person_id order by action_number)
)
select person_id player_id,
       count(*) filter (
         where (lower(action_type) in ('freethrow', 'free throw'))
           and sub_type ilike '%1 of 1%' and sub_type not ilike '%technical%'
           and prev_period = period
           and (prev_type in ('2pt', '3pt', 'Made Shot'))
           and (prev_res = 'Made' or prev_type = 'Made Shot')
       ) and_ones
from tagged group by 1
"""

MADE_FG_SQL = """
select player_id, sum(fgm)::int made_fg, sum(fta)::int fta
from nba.nba_player_stats
where game_id in (select distinct game_id from nba.nba_games
                  where (season_id % 10000) in (2023, 2024, 2025))
group by 1
"""


def and_one_rates() -> pd.DataFrame:
    if os.path.exists(ANDONE):
        return pd.read_csv(ANDONE)
    print("counting and-ones from play-by-play (3 seasons) ...", flush=True)
    a = db.query(AND_ONE_SQL)
    m = db.query(MADE_FG_SQL)
    df = a.merge(m, on="player_id", how="outer").fillna(0)
    df["and_one_rate"] = df.and_ones / df.made_fg.replace(0, np.nan)
    df.to_csv(ANDONE, index=False)
    print("  %d players, %d and-ones total" % (len(df), int(df.and_ones.sum())))
    return df


def main():
    b = pd.read_csv(BEFORE)
    a = pd.read_csv(AFTER)
    keep = ["player_id", "player_name", "possessions", "off_rapm", "def_rapm", "net_rapm",
            "box_net_bpm", "reliable"]
    m = b[keep].merge(a[keep], on=["player_id", "player_name"], suffixes=("_before", "_after"))
    print("players before %d, after %d, matched %d" % (len(b), len(a), len(m)))

    # G1: report how much the possession grid moved (phantom and-one possessions removed)
    same_poss = int((m.possessions_before == m.possessions_after).sum())
    tot_b, tot_a = int(m.possessions_before.sum()), int(m.possessions_after.sum())
    print("G1: identical possession counts for %d of %d players; player-possessions %d -> %d "
          "(%+.2f%%), all of the difference is and-one free throws no longer ending a possession"
          % (same_poss, len(m), tot_b, tot_a, 100 * (tot_a - tot_b) / tot_b))

    for c in ("off_rapm", "def_rapm", "net_rapm"):
        m["d_" + c] = m[c + "_after"] - m[c + "_before"]
    ao = and_one_rates()
    m = m.merge(ao[["player_id", "and_ones", "made_fg", "and_one_rate", "fta"]],
                on="player_id", how="left")
    m.to_csv(OUT, index=False)

    rel = m[(m.reliable_after == "TRUE") | (m.reliable_after is True)].copy()
    if rel.empty:
        rel = m[m.possessions_after >= 2000].copy()
    print("\nSHIFTS (all players / reliable only)")
    for c in ("off_rapm", "def_rapm", "net_rapm"):
        print("  %-9s mean %+.3f / %+.3f | mean abs %.3f / %.3f | max abs %.2f"
              % (c, m["d_" + c].mean(), rel["d_" + c].mean(), m["d_" + c].abs().mean(),
                 rel["d_" + c].abs().mean(), m["d_" + c].abs().max()))

    print("\nBIGGEST MOVERS BY OFFENSIVE RAPM (reliable, top 12 each way)")
    top = rel.sort_values("d_off_rapm", ascending=False)
    for _, r in pd.concat([top.head(12), top.tail(12)]).iterrows():
        print("  %-24s off %+6.2f -> %+6.2f (%+5.2f)  net %+6.2f -> %+6.2f  and-one rate %.3f "
              "(%d of %d)" % (r.player_name[:24], r.off_rapm_before, r.off_rapm_after,
                              r.d_off_rapm, r.net_rapm_before, r.net_rapm_after,
                              r.and_one_rate if pd.notna(r.and_one_rate) else float("nan"),
                              r.and_ones or 0, r.made_fg or 0))

    print("\nTHE DIRECTION OF THE BIAS: shift by and-one rate quartile (reliable players)")
    q = rel[rel.and_one_rate.notna() & (rel.made_fg >= 100)].copy()
    q["quartile"] = pd.qcut(q.and_one_rate, 4, labels=["Q1 lowest", "Q2", "Q3", "Q4 highest"])
    tab = q.groupby("quartile", observed=True).agg(
        players=("player_id", "count"), and_one_rate=("and_one_rate", "mean"),
        d_off=("d_off_rapm", "mean"), d_def=("d_def_rapm", "mean"), d_net=("d_net_rapm", "mean"))
    print(tab.round(3).to_string())
    corr = q[["and_one_rate", "d_off_rapm", "d_net_rapm"]].corr().loc["and_one_rate"]
    print("  corr(and-one rate, offensive shift) = %.3f; with net shift = %.3f"
          % (corr.d_off_rapm, corr.d_net_rapm))

    print("\nNAMED PLAYERS, BEFORE AND AFTER")
    rows = []
    def flat(s):
        import unicodedata
        s = unicodedata.normalize("NFKD", str(s))
        return "".join(ch for ch in s if not unicodedata.combining(ch)).lower()

    m["flat_name"] = m.player_name.map(flat)
    for nm in NAMED:
        hit = m[m.flat_name.str.contains(flat(nm.split()[-1]), na=False)]
        hit = hit[hit.flat_name == flat(nm)] if (hit.flat_name == flat(nm)).any() else hit
        if hit.empty:
            print("  %-22s not in the fit" % nm)
            continue
        r = hit.sort_values("possessions_after", ascending=False).iloc[0]
        rows.append(r)
        print("  %-22s off %+6.2f -> %+6.2f | def %+6.2f -> %+6.2f | net %+6.2f -> %+6.2f | "
              "poss %6d | and-one rate %s"
              % (r.player_name[:22], r.off_rapm_before, r.off_rapm_after, r.def_rapm_before,
                 r.def_rapm_after, r.net_rapm_before, r.net_rapm_after, r.possessions_after,
                 ("%.3f" % r.and_one_rate) if pd.notna(r.and_one_rate) else "n/a"))

    os.makedirs(os.path.dirname(OUT_MD), exist_ok=True)
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write("# D89. RAPM refit on corrected possession points\n\n")
        fh.write("*Before: the frozen pre-D89 possession cache. After: the rebuilt cache. "
                 "Box and DARKO views are untouched; consensus is re-derived downstream.*\n\n")
        fh.write("## Shifts\n\n| view | mean | mean absolute | largest |\n|---|---:|---:|---:|\n")
        for c in ("off_rapm", "def_rapm", "net_rapm"):
            fh.write("| %s | %+.3f | %.3f | %.2f |\n"
                     % (c, m["d_" + c].mean(), m["d_" + c].abs().mean(), m["d_" + c].abs().max()))
        fh.write("\n## The direction of the bias, by and-one rate\n\n")
        fh.write(tab.round(3).to_markdown() + "\n\n")
        fh.write("Correlation between a player's and-one rate and his offensive RAPM shift: "
                 "**%.3f**.\n\n" % corr.d_off_rapm)
        fh.write("## Named players\n\n")
        fh.write("| player | off before | off after | def before | def after | net before | "
                 "net after | possessions | and-one rate |\n|---|---:|---:|---:|---:|---:|---:|---:|---:|\n")
        for r in rows:
            fh.write("| %s | %+.2f | %+.2f | %+.2f | %+.2f | %+.2f | %+.2f | %d | %s |\n"
                     % (r.player_name, r.off_rapm_before, r.off_rapm_after, r.def_rapm_before,
                        r.def_rapm_after, r.net_rapm_before, r.net_rapm_after,
                        r.possessions_after,
                        ("%.3f" % r.and_one_rate) if pd.notna(r.and_one_rate) else "n/a"))
    print("\nwrote %s and %s" % (os.path.relpath(OUT, REPO), os.path.relpath(OUT_MD, REPO)))


if __name__ == "__main__":
    main()

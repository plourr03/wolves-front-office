#!/usr/bin/env python3
"""U5: the spacing table. Descriptive only, no model.

Three-point ATTEMPT RATE (3PA / FGA) and accuracy for Minnesota's projected 2026-27
five, against last season's five, against all 30 teams.

WHAT "MOST-USED FIVE" MEANS HERE, because the warehouse cannot give the literal one.
There is no lineup table in `nba`, so a team's five is defined as its **five
highest-minute players in the 2025-26 regular season**. That is a proxy for a starting
five, not the most-used five-man unit, and it is applied identically to all 30 teams so
the distribution is at least internally consistent. Labelled as such wherever it appears.

TWO WEIGHTINGS, because they answer different questions:
  minutes-weighted  each player's own rate weighted by his minutes. This is what was
                    asked for and it describes "the average shot selection of these
                    five men".
  pooled            sum(3PA) / sum(FGA) across the five. This is the rate the unit
                    would actually post, because it weights by who shoots.
The two differ whenever the high-volume shooters are not the high-minute ones.

Kuminga and Ball are pooled across both of their 2025-26 teams.

    python kuminga/scripts/spacing_table.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "postmortem"))

from kuminga.lib import runlog   # noqa: E402
from lib import db               # noqa: E402

OUT = os.path.join(REPO, "kuminga", "outputs", "spacing_table.csv")
OUT_T = os.path.join(REPO, "kuminga", "outputs", "spacing_teams.csv")
SEASON = "2025-26"
MIN_FGA = 100      # a rate on fewer attempts than this is not a rate

PROJECTED = ["LaMelo Ball", "Anthony Edwards", "Jaden McDaniels",
             "Jonathan Kuminga", "Rudy Gobert"]


# A MINUTES-WEIGHTED 3P% IS NOT A STATISTIC AND IS NOT REPORTED.
# Rudy Gobert shot 0-for-7 from three in 2,710 minutes last season. Weighting accuracy
# by MINUTES gives that 0.000 the largest weight of anyone in Minnesota's projected
# five, ahead of Edwards at 225-for-577, and drags the group to .280 against a real
# .372. Accuracy is therefore reported POOLED, which is the same as weighting by
# attempts, and that is the only accuracy figure in this table.
# The minutes-weighted 3PA RATE is kept, because a centre attempting no threes is a
# real fact about spacing and belongs weighted by how long he is on the floor.
MIN_3PA_FOR_ACC = 50


def rates(df):
    """minutes-weighted 3PA rate, plus POOLED rate and accuracy."""
    m = df.minutes_played.to_numpy(dtype=float)
    r3 = np.where(df.fga > 0, df.fg3a / df.fga, np.nan)
    ok = ~np.isnan(r3)
    mw_rate = float(np.average(r3[ok], weights=m[ok])) if ok.any() else np.nan
    pooled_rate = float(df.fg3a.sum() / df.fga.sum()) if df.fga.sum() else np.nan
    pooled_acc = float(df.fg3m.sum() / df.fg3a.sum()) if df.fg3a.sum() else np.nan
    return mw_rate, pooled_acc, pooled_rate, pooled_acc


def main():
    with runlog.run("spacing_table", inputs={"season": SEASON,
                                             "five": "top-5 by minutes (PROXY)"}) as r:
        q = f"""
            select player_id, player_name,
                   sum(minutes_played) as minutes_played,
                   sum(fga) as fga, sum(fg3a) as fg3a, sum(fg3m) as fg3m,
                   max(team_abbreviation) as any_team
            from nba.nba_player_stats
            where season_year = '{SEASON}' and minutes_played is not null
            group by player_id, player_name
        """
        pl = db.query(q)
        # team assignment for the "five" is by where the player logged the most minutes
        qt = f"""
            select player_id, team_abbreviation, sum(minutes_played) as mp
            from nba.nba_player_stats
            where season_year = '{SEASON}' and minutes_played is not null
            group by player_id, team_abbreviation
        """
        tm = db.query(qt).sort_values("mp", ascending=False).drop_duplicates("player_id")
        pl = pl.merge(tm[["player_id", "team_abbreviation"]], on="player_id", how="left")
        r.note(f"{SEASON}: {len(pl)} players, {pl.team_abbreviation.nunique()} teams")

        # ---- all 30 teams' proxy fives -------------------------------------
        rows = []
        for team, g in pl.groupby("team_abbreviation"):
            five = g.sort_values("minutes_played", ascending=False).head(5)
            mw_r, _, p_r, p_a = rates(five)
            # no mw_acc column: a minutes-weighted 3P% is not a statistic, see above
            rows.append(dict(team_abbr=team, mw_rate=mw_r,
                             pooled_rate=p_r, pooled_acc=p_a,
                             five="; ".join(five.player_name)))
        teams = pd.DataFrame(rows).sort_values("mw_rate", ascending=False)
        teams.to_csv(OUT_T, index=False)

        def pct_of(val, col):
            return float((teams[col] < val).mean() * 100)

        out = []

        def add(label, df, note=""):
            mw_r, _, p_r, p_a = rates(df)
            thin = df[df.fg3a < MIN_3PA_FOR_ACC].player_name.tolist()
            out.append(dict(lineup=label, mw_3pa_rate=mw_r,
                            pooled_3pa_rate=p_r, pooled_3p_pct=p_a,
                            league_pctile_mw_rate=pct_of(mw_r, "mw_rate"),
                            league_pctile_pooled_rate=pct_of(p_r, "pooled_rate"),
                            league_pctile_acc=pct_of(p_a, "pooled_acc"),
                            players="; ".join(df.player_name),
                            barely_shoots_threes=("; ".join(thin) if thin else ""),
                            note=note))
            r.note(f"[{label}] 3PA rate: minutes-weighted {mw_r:.3f} "
                   f"(pctile {pct_of(mw_r, 'mw_rate'):.0f}), pooled {p_r:.3f} "
                   f"(pctile {pct_of(p_r, 'pooled_rate'):.0f}) | pooled 3P% {p_a:.3f} "
                   f"(pctile {pct_of(p_a, 'pooled_acc'):.0f})")
            if thin:
                r.note(f"    under {MIN_3PA_FOR_ACC} 3PA, excluded from no figure but "
                       f"worth naming: {thin}")

        proj = pl[pl.player_name.isin(PROJECTED)]
        missing = set(PROJECTED) - set(proj.player_name)
        assert not missing, f"projected five not found in {SEASON}: {missing}"
        add("MIN projected 2026-27 five", proj,
            "Ball and Kuminga pooled across both 2025-26 teams")

        last = pl[pl.team_abbreviation == "MIN"].sort_values(
            "minutes_played", ascending=False).head(5)
        add("MIN 2025-26 five (top-5 by minutes)", last)

        df = pd.DataFrame(out)
        df.to_csv(OUT, index=False)

        r.note("")
        r.note(f"LEAGUE DISTRIBUTION of the minutes-weighted 3PA rate across 30 proxy "
               f"fives: min {teams.mw_rate.min():.3f} ({teams.iloc[-1].team_abbr}), "
               f"median {teams.mw_rate.median():.3f}, "
               f"max {teams.mw_rate.max():.3f} ({teams.iloc[0].team_abbr})")
        r.note(f"  MIN projected: {df.iloc[0].league_pctile_mw_rate:.0f}th percentile "
               f"minutes-weighted, {df.iloc[0].league_pctile_pooled_rate:.0f}th pooled, "
               f"{df.iloc[0].league_pctile_acc:.0f}th on accuracy.")
        d_mw = df.iloc[0].mw_3pa_rate - df.iloc[1].mw_3pa_rate
        d_p = df.iloc[0].pooled_3pa_rate - df.iloc[1].pooled_3pa_rate
        r.note(f"  vs last season's five: {d_mw:+.3f} minutes-weighted but {d_p:+.3f} "
               f"pooled, and {df.iloc[0].pooled_3p_pct - df.iloc[1].pooled_3p_pct:+.3f} "
               f"on accuracy.")
        if d_mw * d_p < 0:
            r.note("  THE TWO WEIGHTINGS DISAGREE ON DIRECTION. By average shot selection "
                   "the five shoots fewer threes; by actual shot volume it shoots more. "
                   "That gap is one player: LaMelo Ball attempted 740 threes at a .595 "
                   "rate of his own attempts in only 1,982 minutes, so he is a far larger "
                   "share of the shots than of the minutes. Report both or neither.")
        r.output(OUT, rows=len(df))
        r.output(OUT_T, rows=len(teams))

    print()
    print(df[["lineup", "mw_3pa_rate", "pooled_3pa_rate", "pooled_3p_pct",
              "league_pctile_mw_rate", "league_pctile_pooled_rate",
              "league_pctile_acc"]].round(3).to_string(index=False))
    print()
    print("top 5 / bottom 5 by minutes-weighted 3PA rate:")
    print(pd.concat([teams.head(5), teams.tail(5)])[
        ["team_abbr", "mw_rate", "pooled_rate", "pooled_acc"]].round(3).to_string(index=False))


if __name__ == "__main__":
    main()

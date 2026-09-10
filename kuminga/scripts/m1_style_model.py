#!/usr/bin/env python3
"""M1: do style matchups add anything to a net-rating prediction, out of sample?

THE CLAIM UNDER TEST. This project's postmortem found San Antonio suppressing Anthony
Edwards' catch-and-shoot looks and pushing him into the floater zone, and concluded that
the Spurs' style was a bad matchup for Minnesota beyond what net ratings say. That is a
STYLE INTERACTION claim, and until now it has been an eyeball claim. If it is real it
should show up as predictable structure in the residuals of a net-rating model: games
between particular style pairs should miss in a consistent direction.

THE TEST, specified before it was run so the answer could come out either way.

  1. Style features per team-season, all 30, from 2025-26 and the two seasons before it:
     rim rate, three-point rate, pace, opponent turnover rate (turnovers forced),
     offensive rebound rate, and minutes-weighted size. Z-scored within season, so a
     feature is always "relative to that league year".
  2. A baseline margin model: predicted margin = a + b * (net_A - net_B) + home. This is
     the model the residuals are taken from, and it is deliberately plain.
  3. At most FIVE interaction terms, each an offence-style against a defence-style
     product, chosen in advance rather than searched.
  4. FIT on 2023-24 and 2024-25. VALIDATE on 2025-26, which the model never sees.
     Report the out-of-sample gain. Then, separately, on the three POSTSEASONS, because
     the claim is about playoff series and playoff basketball is not regular-season
     basketball.
  5. If the out-of-sample gain is not positive on BOTH, the overlay stays off. That is a
     finding, not a failure, and the piece says the San Antonio thesis could not be
     estimated from this data.

WHY THE HONEST ANSWER MATTERS MORE THAN A POSITIVE ONE. Five interactions fitted on two
seasons of games will always improve the IN-SAMPLE fit. The only number worth reporting
is the held-out one, and the postseason held-out sample is small enough that its size is
quoted as a series count beside every figure.

    python kuminga/scripts/m1_style_model.py
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

from kuminga.lib import runlog  # noqa: E402
from lib import db              # noqa: E402

OUT_FEAT = os.path.join(REPO, "kuminga", "outputs", "m1_style_features.csv")
OUT_FIT = os.path.join(REPO, "kuminga", "outputs", "m1_style_model_fit.csv")

TRAIN = ["2023-24", "2024-25"]
VALID = "2025-26"
SEASON_ID = {"2023-24": 22023, "2024-25": 22024, "2025-26": 22025}
PLAYOFF_ID = {"2023-24": 42023, "2024-25": 42024, "2025-26": 42025}
FEATS = ["rim_rate", "fg3a_rate", "pace", "opp_tov_rate", "oreb_rate", "size"]


def zs(s):
    sd = s.std(ddof=0)
    return (s - s.mean()) / sd if sd and sd > 1e-9 else s * 0.0


def main():
    with runlog.run("m1_style_model",
                    inputs={"train": TRAIN, "valid": VALID, "max_interactions": 5}) as r:
        ids = list(SEASON_ID.values()) + list(PLAYOFF_ID.values())
        g = db.query("""
            select game_id, season_id, team_abbreviation as team, matchup, wl,
                   fga, fg3a, oreb, dreb, tov, pts, plus_minus
            from nba.nba_games
            where season_id in %(ids)s
        """, {"ids": tuple(ids)})
        for c in ("fga", "fg3a", "oreb", "dreb", "tov", "pts", "plus_minus"):
            g[c] = pd.to_numeric(g[c], errors="coerce")
        g["home"] = (~g.matchup.str.contains("@")).astype(int)
        r.note("games pulled: %d team-rows across %d game ids"
               % (len(g), g.game_id.nunique()))

        # opponent side, by self-join on game_id
        opp = g[["game_id", "team", "fga", "fg3a", "oreb", "dreb", "tov", "pts"]].copy()
        opp.columns = ["game_id"] + ["o_" + c for c in opp.columns[1:]]
        m = g.merge(opp, on="game_id")
        m = m[m.team != m.o_team].copy()
        r.note("paired team-game rows: %d" % len(m))

        m["season"] = m.season_id.map(
            {v: k for k, v in list(SEASON_ID.items()) + list(PLAYOFF_ID.items())})
        m["is_playoff"] = m.season_id.isin(PLAYOFF_ID.values())

        # ---- rim rate from the season shot-location table ---------------------
        # team_abbreviation is NULL on this table, so it is joined on team_id and the
        # id->abbreviation map is taken from nba_games, which has both.
        sl = db.query("""
            select season_year, team_id,
                   restricted_area_fga, paint_non_ra_fga, midrange_fga,
                   left_corner_3_fga, right_corner_3_fga, above_break_3_fga
            from nba.nba_team_shot_locations_season
            where season_year in %(s)s and season_type = 'Regular Season'
        """, {"s": tuple(SEASON_ID)})
        cols = ["restricted_area_fga", "paint_non_ra_fga", "midrange_fga",
                "left_corner_3_fga", "right_corner_3_fga", "above_break_3_fga"]
        for c in cols:
            sl[c] = pd.to_numeric(sl[c], errors="coerce")
        sl["rim_rate"] = sl.restricted_area_fga / sl[cols].sum(axis=1)
        idmap = db.query("""select distinct team_id, team_abbreviation as team
                            from nba.nba_games where season_id = 22025""")
        sl = sl.merge(idmap, on="team_id", how="left")
        sl = sl.rename(columns={"season_year": "season"})[["season", "team", "rim_rate"]]
        r.note("rim rate resolved for %d of %d team-seasons"
               % (int(sl.rim_rate.notna().sum() & sl.team.notna().sum()), len(sl)))

        # MINUTES-WEIGHTED SIZE. An earlier run recorded this as unavailable. That was
        # WRONG and the cause was mine: I queried for `height_inches` when the column is
        # `player_height_inches`, got nothing back, and wrote the gap up as a warehouse
        # limitation. It is fully populated: 572, 569 and 582 non-null rows across the
        # three seasons. Weighted by games played, since this table carries `gp` but no
        # minutes column; games played is a weaker weight than minutes and is stated as
        # such rather than silently substituted.
        bio = db.query("""
            select season_year as season, team_abbreviation as team,
                   sum(player_height_inches * gp) / nullif(sum(gp), 0) as size
            from nba.nba_player_season_bio
            where season_type = 'Regular Season' and season_year in %(s)s
              and player_height_inches is not null and gp > 0
            group by 1, 2
        """, {"s": tuple(SEASON_ID)})
        bio["size"] = pd.to_numeric(bio["size"], errors="coerce")
        r.note("games-weighted SIZE resolved for %d team-seasons, mean %.2f inches, "
               "range %.2f to %.2f"
               % (len(bio), bio["size"].mean(), bio["size"].min(), bio["size"].max()))

        # ---- team-season style features, REGULAR SEASON only ------------------
        rs = m[~m.is_playoff]
        agg = rs.groupby(["season", "team"]).agg(
            fga=("fga", "sum"), fg3a=("fg3a", "sum"), oreb=("oreb", "sum"),
            o_dreb=("o_dreb", "sum"), o_tov=("o_tov", "sum"),
            o_fga=("o_fga", "sum"), pts=("pts", "sum"), n=("game_id", "size"),
        ).reset_index()
        agg["fg3a_rate"] = agg.fg3a / agg.fga
        agg["oreb_rate"] = agg.oreb / (agg.oreb + agg.o_dreb)
        # possessions proxy, consistent across both sides of the ball
        agg["pace"] = (agg.fga + agg.o_fga) / (2.0 * agg.n)
        agg["opp_tov_rate"] = agg.o_tov / agg.o_fga
        feat = agg.merge(sl, on=["season", "team"], how="left")
        feat = feat.merge(bio, on=["season", "team"], how="left")
        use = [f for f in FEATS if f in feat.columns and feat[f].notna().any()]
        for f in use:
            feat[f] = feat.groupby("season")[f].transform(zs)
        feat[["season", "team"] + use].to_csv(OUT_FEAT, index=False)
        r.note("style features built for %d team-seasons: %s"
               % (len(feat), ", ".join(use)))

        # ---- season net rating, from the same games ---------------------------
        net = rs.groupby(["season", "team"]).plus_minus.mean().rename("net").reset_index()

        # ---- game frame: one row per game, home perspective --------------------
        gm = m[m.home == 1].copy()
        gm = gm.merge(net.rename(columns={"team": "team", "net": "net_a"}),
                      on=["season", "team"], how="left")
        gm = gm.merge(net.rename(columns={"team": "o_team", "net": "net_b"}),
                      on=["season", "o_team"], how="left")
        F = feat[["season", "team"] + use]
        gm = gm.merge(F.add_suffix("_a").rename(
            columns={"season_a": "season", "team_a": "team"}), on=["season", "team"],
            how="left")
        gm = gm.merge(F.add_suffix("_b").rename(
            columns={"season_b": "season", "team_b": "o_team"}),
            on=["season", "o_team"], how="left")
        gm = gm.dropna(subset=["net_a", "net_b"] + [f + "_a" for f in use]
                       + [f + "_b" for f in use])
        gm["y"] = gm.plus_minus.astype(float)
        gm["dnet"] = gm.net_a - gm.net_b
        r.note("modelling frame: %d games (%d regular season, %d playoff)"
               % (len(gm), int((~gm.is_playoff).sum()), int(gm.is_playoff.sum())))

        # ---- FIVE interactions, chosen in advance -----------------------------
        # each is an OFFENCE style against the DEFENCE style that should blunt it
        # With SIZE restored, two interactions go back to the forms originally planned:
        # an offence attacking the rim against the defence's size, and offensive
        # rebounding against size. Still five, still fixed before fitting.
        inter = {
            "rim_vs_size":   gm["rim_rate_a"] * gm["size_b"],
            "oreb_vs_size":  gm["oreb_rate_a"] * gm["size_b"],
            "three_vs_pace": gm["fg3a_rate_a"] * gm["pace_b"],
            "pace_vs_pace":  gm["pace_a"] * gm["pace_b"],
            "tov_vs_three":  gm["opp_tov_rate_b"] * gm["fg3a_rate_a"],
        }
        for k, v in inter.items():
            gm[k] = v
        IX = list(inter)
        r.note("interaction terms (%d, fixed in advance): %s" % (len(IX), ", ".join(IX)))

        def fit(df, cols):
            X = np.column_stack([np.ones(len(df))] + [df[c].to_numpy(float)
                                                      for c in cols])
            b, *_ = np.linalg.lstsq(X, df.y.to_numpy(float), rcond=None)
            return b

        def pred(df, cols, b):
            X = np.column_stack([np.ones(len(df))] + [df[c].to_numpy(float)
                                                      for c in cols])
            return X @ b

        tr = gm[(gm.season.isin(TRAIN)) & (~gm.is_playoff)]
        va = gm[(gm.season == VALID) & (~gm.is_playoff)]
        po = gm[gm.is_playoff]

        b0 = fit(tr, ["dnet", "home"])
        b1 = fit(tr, ["dnet", "home"] + IX)

        def mae(df, cols, b):
            return float(np.abs(df.y.to_numpy(float) - pred(df, cols, b)).mean())

        def rmse(df, cols, b):
            e = df.y.to_numpy(float) - pred(df, cols, b)
            return float(np.sqrt((e ** 2).mean()))

        rows = []
        for label, df in (("train 2023-25 RS", tr), ("HELD OUT 2025-26 RS", va),
                          ("HELD OUT postseasons", po)):
            rows.append(dict(sample=label, n_games=len(df),
                             base_mae=mae(df, ["dnet", "home"], b0),
                             style_mae=mae(df, ["dnet", "home"] + IX, b1),
                             base_rmse=rmse(df, ["dnet", "home"], b0),
                             style_rmse=rmse(df, ["dnet", "home"] + IX, b1)))
        fitdf = pd.DataFrame(rows)
        fitdf["mae_gain"] = fitdf.base_mae - fitdf.style_mae
        fitdf["rmse_gain"] = fitdf.base_rmse - fitdf.style_rmse
        fitdf.to_csv(OUT_FIT, index=False)

        r.note("")
        r.note("OUT-OF-SAMPLE GAIN (positive = the style overlay helps):")
        for _, x in fitdf.iterrows():
            # NB: x.sample is DataFrame.sample, the METHOD. Index by name or it
            # silently formats a bound method into the log. Same trap as x.item.
            r.note("  %-22s n=%5d | MAE %.3f -> %.3f (%+.4f) | RMSE %.3f -> %.3f (%+.4f)"
                   % (x["sample"], x.n_games, x.base_mae, x.style_mae, x.mae_gain,
                      x.base_rmse, x.style_rmse, x.rmse_gain))
        n_series = int(po.game_id.nunique() / 5.8) if len(po) else 0
        r.note("  the postseason sample is %d games, roughly %d series. That is the "
               "number every playoff claim here has to survive." % (len(po), n_series))

        v = fitdf[fitdf["sample"] == "HELD OUT 2025-26 RS"].iloc[0]
        p = fitdf[fitdf["sample"] == "HELD OUT postseasons"].iloc[0]
        both = (v.mae_gain > 0) and (p.mae_gain > 0)
        r.note("")
        r.note("M2 DECISION: %s" % ("OVERLAY ON" if both else "OVERLAY STAYS OFF"))
        if not both:
            r.note("  The out-of-sample gain is not positive on both held-out samples "
                   "(%.4f on 2025-26 games, %.4f on the postseasons). Five interactions "
                   "fitted on two seasons improve the IN-SAMPLE fit and do not carry. "
                   "The overlay stays off, M3's cards use net-rating series odds with "
                   "the style features shown as DESCRIPTIVE ONLY, and the piece says "
                   "the San Antonio thesis could not be estimated from this data."
                   % (v.mae_gain, p.mae_gain))
        else:
            r.note("  Positive on both held-out samples, so the interactions are wired "
                   "into the series step for all 30 teams identically.")
        r.output(OUT_FEAT, rows=len(feat))
        r.output(OUT_FIT, rows=len(fitdf))

    print()
    print(fitdf.round(4).to_string(index=False))


if __name__ == "__main__":
    main()

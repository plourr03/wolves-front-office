#!/usr/bin/env python3
"""F4d: does top-heaviness carry out-of-sample signal for playoff series outcomes?

F4c killed the depth-versus-stars story as an explanation for the model-market gap: the
correlation between a team's impact concentration and model-minus-market is -0.065.
That is a different question from whether concentration predicts PLAYOFF results, which
is what F4d asks, so it is tested separately rather than assumed dead.

THE PROXY, and its limitation stated up front. Top-heaviness here is **minutes
concentration**: the share of a team's regular-season minutes taken by its top two and
top three players, from `nba_player_tracking_season`. It is NOT impact concentration.
Impact concentration cannot be computed historically in this project, because the RAPM
spine is a multi-season pooled estimate rather than a per-season one, so there is no
2023-24 impact number to concentrate. Minutes concentration is what a coach actually
controls when a rotation shortens, which is the mechanism the hypothesis names, so it is
a defensible proxy and a weak one, and both halves of that belong in the report.

THE TEST. Baseline playoff margin = a + b(net_A - net_B) + home. Add the top-three
minutes-share difference. Fit on the 2024 and 2025 postseasons, validate on 2026.
**If the held-out gain is not positive, no series adjustment is proposed.** The
regular-season rollup is not touched either way, per the brief.

    python kuminga/scripts/f4d_topheaviness_series.py
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

OUT = os.path.join(REPO, "kuminga", "outputs", "f4d_topheaviness_series.csv")
SEASONS = {"2023-24": 22023, "2024-25": 22024, "2025-26": 22025}
PLAYOFFS = {"2023-24": 42023, "2024-25": 42024, "2025-26": 42025}
TRAIN = ["2023-24", "2024-25"]
VALID = "2025-26"


def main():
    with runlog.run("f4d_topheaviness_series",
                    inputs={"proxy": "minutes concentration", "train": TRAIN,
                            "valid": VALID}) as r:
        tr = db.query("""
            select season_year as season, team_abbreviation as team,
                   player_id, gp, min
            from nba.nba_player_tracking_season
            where season_type = 'Regular Season' and season_year in %(s)s
        """, {"s": tuple(SEASONS)})
        for c in ("gp", "min"):
            tr[c] = pd.to_numeric(tr[c], errors="coerce")
        # TWO TRAPS IN THIS TABLE, both caught by the top-3 share coming out at 0.042
        # when a real one is 0.35 to 0.40. First, it carries one row per TRACKING
        # CATEGORY, so each player appears about eleven times and a naive group-by
        # counts him eleven times. Second, `min` is already TOTAL minutes for the
        # season, so multiplying by gp double-counts. Dedupe, and use min as it stands.
        tr = tr.drop_duplicates(subset=["season", "team", "player_id"])
        tr["tot_min"] = tr["min"]
        tr = tr.dropna(subset=["tot_min", "team"])
        rows = []
        for (s, tm), g in tr.groupby(["season", "team"]):
            v = g.tot_min.sort_values(ascending=False)
            t = float(v.sum()) or 1.0
            rows.append(dict(season=s, team=tm, top2=float(v.head(2).sum()) / t,
                             top3=float(v.head(3).sum()) / t))
        th = pd.DataFrame(rows)
        r.note("top-heaviness built for %d team-seasons; top-3 share mean %.3f, "
               "range %.3f to %.3f"
               % (len(th), th.top3.mean(), th.top3.min(), th.top3.max()))

        ids = list(SEASONS.values()) + list(PLAYOFFS.values())
        g = db.query("""
            select game_id, season_id, team_abbreviation as team, matchup,
                   plus_minus, pts
            from nba.nba_games where season_id in %(i)s
        """, {"i": tuple(ids)})
        g["plus_minus"] = pd.to_numeric(g.plus_minus, errors="coerce")
        g["home"] = (~g.matchup.str.contains("@")).astype(int)
        s_map = {v: k for k, v in list(SEASONS.items()) + list(PLAYOFFS.items())}
        g["season"] = g.season_id.map(s_map)
        g["is_po"] = g.season_id.isin(PLAYOFFS.values())

        opp = g[["game_id", "team"]].rename(columns={"team": "o_team"})
        m = g.merge(opp, on="game_id")
        m = m[m.team != m.o_team]
        rs = m[~m.is_po]
        net = rs.groupby(["season", "team"]).plus_minus.mean().rename("net").reset_index()

        po = m[m.is_po & (m.home == 1)].copy()
        po = po.merge(net, on=["season", "team"], how="left")
        po = po.merge(net.rename(columns={"team": "o_team", "net": "o_net"}),
                      on=["season", "o_team"], how="left")
        po = po.merge(th, on=["season", "team"], how="left")
        po = po.merge(th.rename(columns={"team": "o_team", "top2": "o_top2",
                                         "top3": "o_top3"}),
                      on=["season", "o_team"], how="left")
        po = po.dropna(subset=["net", "o_net", "top3", "o_top3"])
        po["dnet"] = po.net - po.o_net
        po["dtop3"] = po.top3 - po.o_top3
        po["y"] = po.plus_minus.astype(float)
        r.note("playoff games with both sides resolved: %d across %d postseasons "
               "(roughly %d series)" % (len(po), po.season.nunique(), len(po) // 5.8))

        def fit(d, cols):
            X = np.column_stack([np.ones(len(d))] + [d[c].to_numpy(float) for c in cols])
            b, *_ = np.linalg.lstsq(X, d.y.to_numpy(float), rcond=None)
            return b

        def mae(d, cols, b):
            X = np.column_stack([np.ones(len(d))] + [d[c].to_numpy(float) for c in cols])
            return float(np.abs(d.y.to_numpy(float) - X @ b).mean())

        a = po[po.season.isin(TRAIN)]
        v = po[po.season == VALID]
        b0 = fit(a, ["dnet"])
        b1 = fit(a, ["dnet", "dtop3"])
        res = []
        for lab, d in (("train postseasons", a), ("HELD OUT 2026 postseason", v)):
            res.append(dict(sample=lab, n=len(d), base_mae=mae(d, ["dnet"], b0),
                            with_top3=mae(d, ["dnet", "dtop3"], b1)))
        f = pd.DataFrame(res)
        f["gain"] = f.base_mae - f.with_top3
        f.to_csv(OUT, index=False)

        r.note("")
        r.note("coefficient on the top-3 minutes-share difference: %+.2f points of "
               "margin per unit share (train)" % b1[2])
        for _, x in f.iterrows():
            r.note("  %-26s n=%3d | MAE %.3f -> %.3f (%+.4f)"
                   % (x["sample"], x["n"], x["base_mae"], x["with_top3"], x["gain"]))
        held = f[f["sample"].str.startswith("HELD OUT")].iloc[0]
        r.note("")
        if held["gain"] > 0:
            r.note("HELD-OUT GAIN IS POSITIVE (%+.4f). A series-step adjustment is "
                   "worth proposing, applied identically to all 30." % held["gain"])
        else:
            r.note("HELD-OUT GAIN IS NOT POSITIVE (%+.4f). **No series adjustment is "
                   "proposed.** Top-heaviness does not predict playoff margin beyond "
                   "net rating out of sample, on this proxy and this sample. The "
                   "regular-season rollup is untouched either way."
                   % held["gain"])
        r.note("  Sample is the binding limit: %d held-out games, roughly %d series. "
               "A null here is weak evidence of absence, and the piece should say so "
               "rather than treating it as settled."
               % (len(v), len(v) // 5.8))
        r.output(OUT, rows=len(f))

    print()
    print(f.round(4).to_string(index=False))


if __name__ == "__main__":
    main()

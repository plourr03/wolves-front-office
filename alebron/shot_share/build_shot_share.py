"""
Shot-share model: how much could Edwards's catch-and-shoot (open) SHARE of his threes
shift next to a lead creator? Comp-based, criteria locked in PREREGISTRATION.md, take
every qualifier. Frequency only; efficiency held fixed.

Builds one player-season table from nba_player_tracking_season (RS), screens for the
locked subject + treatment criteria, measures cs_share before/after, nets out league
drift, and writes the comp set + the projected range for Edwards (27% baseline).

    python build_shot_share.py
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "postmortem"))
from lib import db  # noqa: E402

OUT = Path(__file__).resolve().parent
EDWARDS_ID = 1630162
EDWARDS_BASE = 0.277          # 2025-26 cs_share, 139/(139+363)

# locked thresholds (PREREGISTRATION.md)
PPG_MIN, APG_SUBJ_MAX, CSSHARE_MAX = 20.0, 6.0, 0.50
GP_MIN, THREE_MIN, APG_CREATOR = 40, 80, 6.0


def load_player_seasons() -> pd.DataFrame:
    """One row per (player, season): team, gp, ppg, apg, cs3a, pu3a, cs_share, cs_fg3_pct."""
    raw = db.query("""
        select player_id, player_name, season_year, measure_type, team_abbreviation,
               gp, points, ast, catch_shoot_fg3a, catch_shoot_fg3_pct, catch_shoot_efg_pct,
               pull_up_fg3a, pull_up_fg3_pct
        from nba_player_tracking_season
        where season_type='Regular Season'
          and measure_type in ('CatchShoot','PullUpShot','Possessions','Passing')
    """)
    for c in ["gp", "points", "ast", "catch_shoot_fg3a", "catch_shoot_fg3_pct",
              "catch_shoot_efg_pct", "pull_up_fg3a", "pull_up_fg3_pct"]:
        raw[c] = pd.to_numeric(raw[c], errors="coerce")
    g = raw.groupby(["player_id", "season_year"])
    df = pd.DataFrame({
        "player_name": g["player_name"].first(),
        "team": g["team_abbreviation"].first(),
        "gp": g["gp"].max(),
        "pts": g["points"].max(),
        "ast": g["ast"].max(),
        "cs3a": g["catch_shoot_fg3a"].max(),
        "cs3pct": g["catch_shoot_fg3_pct"].max(),
        "cs_efg": g["catch_shoot_efg_pct"].max(),
        "pu3a": g["pull_up_fg3a"].max(),
        "pu3pct": g["pull_up_fg3_pct"].max(),
    }).reset_index()
    df["ppg"] = df["pts"] / df["gp"]
    df["apg"] = df["ast"] / df["gp"]
    df["tot3a"] = df["cs3a"].fillna(0) + df["pu3a"].fillna(0)
    df["cs_share"] = df["cs3a"] / df["tot3a"]
    return df


def prev_season(s: str) -> str:
    y = int(s[:4])
    return f"{y-1}-{str(y)[2:]}"


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    df = load_player_seasons()
    by = {(r.player_id, r.season_year): r for r in df.itertuples(index=False)}
    seasons = sorted(df["season_year"].unique())
    print(f"player-seasons: {len(df)} across {seasons[0]}..{seasons[-1]}")

    # creators per season: APG >= 6 on gp>=40
    creators = {s: set(df[(df.season_year == s) & (df.apg >= APG_CREATOR) & (df.gp >= GP_MIN)].player_id)
                for s in seasons}
    # team lookup
    team = {(r.player_id, r.season_year): r.team for r in df.itertuples(index=False)}

    # league cs_share drift over the reference volume pool (PPG>=20, gp>=40, tot3a>=80)
    pool = df[(df.ppg >= PPG_MIN) & (df.gp >= GP_MIN) & (df.tot3a >= THREE_MIN)]
    pool_mean = pool.groupby("season_year")["cs_share"].mean()

    comps = []
    for r in df.itertuples(index=False):
        Y = r.season_year
        Y0 = prev_season(Y)
        if Y0 not in seasons:
            continue
        if r.player_id == EDWARDS_ID:
            continue
        pre = by.get((r.player_id, Y0))
        if pre is None:
            continue
        # subject qualifies in Y-1
        if not (pre.ppg >= PPG_MIN and pre.apg < APG_SUBJ_MAX and pre.cs_share < CSSHARE_MAX
                and pre.gp >= GP_MIN and pre.tot3a >= THREE_MIN):
            continue
        # plays Y on real volume
        if not (r.gp >= GP_MIN and r.tot3a >= THREE_MIN and pd.notna(r.cs_share)):
            continue
        # gained a NEW lead creator in Y (teammate in Y, not in Y-1)
        new_creators = []
        for cid in creators.get(Y, set()):
            if cid == r.player_id:
                continue
            if team.get((cid, Y)) == r.team and team.get((cid, Y0)) != team.get((r.player_id, Y0)):
                cr = by.get((cid, Y))
                cr0 = by.get((cid, Y0))
                # require the creator's lead-distributor status in Y-1 (pre-join)
                if cr0 is not None and cr0.apg >= APG_CREATOR:
                    new_creators.append((cr0.apg, cid))
        if not new_creators:
            continue
        new_creators.sort(reverse=True)
        cid = new_creators[0][1]
        cinfo = by[(cid, Y)]
        cinfo0 = by[(cid, Y0)]
        drift = float(pool_mean.get(Y, np.nan) - pool_mean.get(Y0, np.nan))
        comps.append({
            "subject": r.player_name, "subject_id": int(r.player_id),
            "pre_season": Y0, "post_season": Y,
            "creator": cinfo.player_name, "creator_apg_preY": round(float(cinfo0.apg), 1),
            "team_pre": team.get((r.player_id, Y0)), "team_post": r.team,
            "team_change": team.get((r.player_id, Y0)) != r.team,
            "pre_ppg": round(float(pre.ppg), 1), "pre_apg": round(float(pre.apg), 1),
            "pre_cs_share": round(float(pre.cs_share), 4), "post_cs_share": round(float(r.cs_share), 4),
            "pre_cs3a": int(pre.cs3a), "pre_pu3a": int(pre.pu3a),
            "post_cs3a": int(r.cs3a), "post_pu3a": int(r.pu3a),
            "pre_cs3pct": round(float(pre.cs3pct), 3), "post_cs3pct": round(float(r.cs3pct), 3),
            "delta": round(float(r.cs_share - pre.cs_share), 4),
            "league_drift": round(drift, 4),
            "delta_adj": round(float(r.cs_share - pre.cs_share - drift), 4),
        })

    cdf = pd.DataFrame(comps).sort_values("delta", ascending=False)
    cdf.to_csv(OUT / "comp_set.csv", index=False)
    pd.set_option("display.width", 200); pd.set_option("display.max_columns", 40)
    print(f"\n=== COMP SET (N={len(cdf)}) ===")
    print(cdf[["subject", "pre_season", "post_season", "creator", "creator_apg_preY",
               "team_change", "pre_ppg", "pre_apg", "pre_cs_share", "post_cs_share",
               "delta", "league_drift", "delta_adj"]].to_string(index=False))

    if len(cdf):
        for col in ["delta", "delta_adj"]:
            v = cdf[col].values
            print(f"\n{col}: N={len(v)} median={np.median(v):+.3f} mean={np.mean(v):+.3f} "
                  f"p25={np.percentile(v,25):+.3f} p75={np.percentile(v,75):+.3f} "
                  f"min={v.min():+.3f} max={v.max():+.3f}")
        # projection onto Edwards 27%
        adj = cdf["delta_adj"].values
        proj = EDWARDS_BASE + adj
        summ = {
            "n": int(len(cdf)),
            "edwards_base": EDWARDS_BASE,
            "delta_raw": {k: round(float(f(cdf["delta"].values)), 4) for k, f in
                          [("median", np.median), ("p25", lambda x: np.percentile(x, 25)),
                           ("p75", lambda x: np.percentile(x, 75)), ("min", np.min), ("max", np.max)]},
            "delta_adj": {k: round(float(f(adj)), 4) for k, f in
                          [("median", np.median), ("p25", lambda x: np.percentile(x, 25)),
                           ("p75", lambda x: np.percentile(x, 75)), ("min", np.min), ("max", np.max)]},
            "edwards_projected_share_adj": {
                "median": round(float(np.median(proj)), 4),
                "p25": round(float(np.percentile(proj, 25)), 4),
                "p75": round(float(np.percentile(proj, 75)), 4),
            },
        }
        (OUT / "results.json").write_text(json.dumps(summ, indent=2))
        print(f"\nEdwards 27% -> drift-adj projected (p25..p75): "
              f"{summ['edwards_projected_share_adj']['p25']*100:.0f}% to "
              f"{summ['edwards_projected_share_adj']['p75']*100:.0f}% "
              f"(median {summ['edwards_projected_share_adj']['median']*100:.0f}%)")

    # Lens B: movement-shooter ceiling (high cs_share on volume, 2024-25/2025-26)
    mv = df[(df.season_year.isin(["2024-25", "2025-26"])) & (df.tot3a >= 200)
            ].sort_values("cs_share", ascending=False).head(8)
    print("\n=== Lens B ceiling reference (highest cs_share, vol>=200 3PA) ===")
    print(mv[["player_name", "season_year", "cs_share", "tot3a"]].round(3).to_string(index=False))


if __name__ == "__main__":
    main()

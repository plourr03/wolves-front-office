"""FC-DRB wire threshold from the Phase 3 scorecard + CIs + symmetry inputs.

The wire: team defensive-rebound proxy in anchor-off (Gobert-off) minutes,
as a league percentile, read at R1 (first 20 games) and R2 (first 37).
Derives the ARM-B trigger percentile from the early->rest mapping across all
330 team-seasons, and reports Fisher CIs for the FC-DRB and AVAIL-PACE
statistics (reported, not gates), per Bobby's ruling.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr, pearsonr, norm

REPO = Path(r"C:\Users\bobby\playground\wolves-front-office")
DATA = REPO / "all-for-one" / "tripwire-backtest" / "data"
PANEL = DATA / "stints_panel"
sys.path.insert(0, str(REPO / "postmortem"))
from lib.db import query  # noqa: E402

pd.set_option("display.width", 200)


def drb(half):
    miss = (half.fga_def - half.fgm_def).sum()
    return (1 - half.oreb_def.sum() / miss) if miss > 0 else np.nan


def fisher_ci(r, n, alpha=0.05):
    if n < 4 or abs(r) >= 1:
        return (np.nan, np.nan)
    z = np.arctanh(r); se = 1 / np.sqrt(n - 3)
    zc = norm.ppf(1 - alpha / 2)
    return (np.tanh(z - zc * se), np.tanh(z + zc * se))


def prop_ci(p, n, alpha=0.05):
    # Wilson interval for a proportion (sign consistency)
    z = norm.ppf(1 - alpha / 2)
    d = 1 + z**2 / n
    c = (p + z**2 / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / d
    return (c - h, c + h)


def main() -> None:
    files = sorted(PANEL.glob("*.parquet"))
    print(f"loading {len(files)} panel games...", flush=True)
    df = pd.concat((pd.read_parquet(f) for f in files), ignore_index=True)
    df = df[~df.in_garbage_time]
    g = query("""SELECT game_id, team_id, RIGHT(season_id::text,4)::int ss, game_date
                 FROM nba.nba_games WHERE LEFT(season_id::text,1)='2'""")
    df = df.merge(g, on=["game_id", "team_id"], how="inner")
    df = df[(df.ss >= 2014) & (df.ss <= 2024)]
    gn = (df[["team_id", "ss", "game_id", "game_date"]].drop_duplicates()
          .sort_values(["team_id", "ss", "game_date", "game_id"]))
    gn["game_no"] = gn.groupby(["team_id", "ss"]).cumcount() + 1
    df = df.merge(gn[["team_id", "ss", "game_id", "game_no"]], on=["team_id", "ss", "game_id"])

    anchor = {}
    tm = query("""SELECT RIGHT(gm.season_id::text,4)::int ss, ps.team_id, ps.player_id,
                    SUM(a.minutes_float) mn
                  FROM nba.nba_player_advanced_stats a
                  JOIN nba.nba_games gm ON gm.game_id=a.game_id
                  JOIN nba.nba_player_stats ps ON ps.game_id=a.game_id AND ps.player_id=a.person_id
                  WHERE LEFT(gm.season_id::text,1)='2' AND a.minutes_float IS NOT NULL GROUP BY 1,2,3""")
    pos = dict(zip(query("SELECT player_id, position FROM nba.nba_player_bio").player_id,
                   query("SELECT player_id, position FROM nba.nba_player_bio").position.fillna("")))
    CEN = {"Center", "Center-Forward", "Forward-Center"}
    tm["c"] = tm.player_id.map(pos).isin(CEN)
    for (ss, tid), gg in tm[tm.c].groupby(["ss", "team_id"]):
        anchor[(ss, tid)] = int(gg.sort_values("mn", ascending=False).iloc[0].player_id)

    rows = []
    for (tid, ss), sub in df.groupby(["team_id", "ss"]):
        a = anchor.get((ss, tid))
        if a is None:
            continue
        off = sub[~sub.lineup_id.map(lambda L: str(a) in L.split(","))]
        r20 = drb(off[off.game_no <= 20]); r37 = drb(off[off.game_no <= 37])
        rest = drb(off[off.game_no > 37])
        full = drb(off)
        rows.append({"team_id": tid, "ss": ss, "drb20": r20, "drb37": r37,
                     "drb_rest": rest, "drb_full": full})
    d = pd.DataFrame(rows).dropna(subset=["drb20", "drb37", "drb_rest"])
    # league percentiles within each season
    for c in ["drb20", "drb37", "drb_rest", "drb_full"]:
        d[c + "_pct"] = d.groupby("ss")[c].rank(pct=True)
    d.to_parquet(DATA / "fcdrb_wire_cases.parquet", index=False)
    print(f"team-seasons: {len(d)}\n")

    # persistence: early percentile -> rest percentile
    for early in ["drb20", "drb37"]:
        rho, _ = spearmanr(d[early], d.drb_rest)
        print(f"{early} -> drb_rest: Spearman={rho:.3f} (n={len(d)})")
    print()

    # SCORECARD: bucket by R2 (drb37) league percentile, show rest percentile
    print("SCORECARD: rest-of-season anchor-off DRB by R2 (game-37) percentile bucket")
    d["r2_bucket"] = pd.cut(d.drb37_pct, [0, 0.2, 0.33, 0.5, 1.0],
                            labels=["bot20", "20-33", "33-50", "top50"])
    print(d.groupby("r2_bucket", observed=True).agg(
        n=("drb37_pct", "size"),
        mean_rest_pct=("drb_rest_pct", "mean"),
        p_rest_bot33=("drb_rest_pct", lambda s: (s <= 0.33).mean()),
        p_rest_bot20=("drb_rest_pct", lambda s: (s <= 0.20).mean())).to_string())

    # threshold pick: where does a low early read reliably predict a low rest?
    print("\nP(rest in bottom third | R2 percentile below cut):")
    for cut in [0.20, 0.25, 0.33, 0.40]:
        below = d[d.drb37_pct <= cut]
        print(f"  R2 pct <= {cut:.2f}: n={len(below)}, "
              f"P(rest bottom-third)={((below.drb_rest_pct<=0.33).mean()):.3f}, "
              f"mean rest pct={below.drb_rest_pct.mean():.3f}")

    # ---- CIs for the ruling ----
    print("\n" + "=" * 70)
    print("CONFIDENCE INTERVALS (Fisher for r, Wilson for sign), reported not gated")
    print("=" * 70)
    # FC-DRB (Scenario C persistence, n=82) from the committed cases
    c = pd.read_parquet(DATA / "scenarioC_cases.parquet")
    rho_fc, _ = spearmanr(c.early_drb, c.yc1_rest_drb)
    em, om = c.early_drb.median(), c.yc1_rest_drb.median()
    sign_fc = ((c.early_drb >= em) == (c.yc1_rest_drb >= om)).mean()
    print(f"FC-DRB  Spearman={rho_fc:.3f}, 95% CI {fisher_ci(rho_fc, len(c))}, n={len(c)}")
    print(f"FC-DRB  sign={sign_fc:.3f}, 95% CI {prop_ci(sign_fc, len(c))}")
    # AVAIL-PACE (n=377 at N=20)
    ap = pd.read_parquet(DATA / "avail_pace_cases.parquet")
    sub = ap.dropna(subset=["avail_20"])
    rho_ap, _ = spearmanr(sub.avail_20, sub.full_gp)
    em2, om2 = sub.avail_20.median(), sub.full_gp.median()
    sign_ap = ((sub.avail_20 >= em2) == (sub.full_gp >= om2)).mean()
    print(f"AVAIL   Spearman={rho_ap:.3f}, 95% CI {fisher_ci(rho_ap, len(sub))}, n={len(sub)}")
    print(f"AVAIL   sign={sign_ap:.3f}, 95% CI {prop_ci(sign_ap, len(sub))}")

    # arcsine translation check
    print("\narcsine translation: concordance = 1/2 + arcsin(rho)/pi")
    for gate in [0.70]:
        rho_equiv = np.sin((gate - 0.5) * np.pi)
        print(f"  sign gate {gate} <-> Spearman {rho_equiv:.3f}")


if __name__ == "__main__":
    main()

"""FC-DRB subgroup split + whole-team wire validation (Bobby's redesign ruling).

Partition frontcourt-succession team-seasons into:
  retained-primary : the team kept its #1 rim-minutes big and lost its #2
                     (the Wolves case: keep Gobert, lose Reid).
  lost-primary     : the #1 rim-minutes big departed.

For the RETAINED-PRIMARY subgroup, measure early->rest DRB persistence BOTH
ways: whole-team DRB, and primary-off (anchor-off) DRB. For lost-primary,
whole-team DRB (the 0.617-validated construct). Also compute whole-team DRB
reliability r(25) across all team-seasons (the redesigned binding metric),
and the whole-team scorecard for threshold derivation.

Gates: n>=30 translated rule (Spearman>=0.59); 8<=n<30 original sign gate
(0.70); n<8 descriptive only.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

REPO = Path(r"C:\Users\bobby\playground\wolves-front-office")
DATA = REPO / "all-for-one" / "tripwire-backtest" / "data"
PANEL = DATA / "stints_panel"
sys.path.insert(0, str(REPO / "postmortem"))
from lib.db import query  # noqa: E402

pd.set_option("display.width", 200)
BIG = {"Center", "Center-Forward", "Forward-Center"}
STAY_MIN, DEPART_MIN, REPLACE_MIN = 1500, 500, 1500


def drb(h):
    miss = (h.fga_def - h.fgm_def).sum()
    return (1 - h.oreb_def.sum() / miss) if miss > 0 else np.nan


def sign_consistency(x, y):
    xm, ym = np.median(x), np.median(y)
    return float(((np.array(x) >= xm) == (np.array(y) >= ym)).mean())


def verdict(rho, sign, n):
    if n < 8:
        return "descriptive only (n<8)"
    if n >= 30:
        return f"translated gate (>=0.59): {'PASS' if rho >= 0.59 else 'FAIL'}"
    return f"original sign gate (>=0.70): {'PASS' if sign >= 0.70 else 'FAIL'}"


def main() -> None:
    # ---- big-minutes per team-season (all seasons, warehouse) ----
    tm = query("""SELECT RIGHT(gm.season_id::text,4)::int ss, ps.team_id, ps.player_id,
                    SUM(a.minutes_float) mn
                  FROM nba.nba_player_advanced_stats a
                  JOIN nba.nba_games gm ON gm.game_id=a.game_id
                  JOIN nba.nba_player_stats ps ON ps.game_id=a.game_id AND ps.player_id=a.person_id
                  WHERE LEFT(gm.season_id::text,1)='2' AND a.minutes_float IS NOT NULL GROUP BY 1,2,3""")
    pos = dict(zip(query("SELECT player_id, position FROM nba.nba_player_bio").player_id,
                   query("SELECT player_id, position FROM nba.nba_player_bio").position.fillna("")))
    tm["big"] = tm.player_id.map(pos).isin(BIG)
    minmap = {(r.ss, r.team_id, r.player_id): r.mn for r in tm.itertuples()}

    # classify each team-season transition S -> S+1
    classes = []  # (hole_ss=S+1, team_id, subgroup, primary_pid)
    for (ss, tid), g in tm[tm.big].groupby(["ss", "team_id"]):
        bigs = g.sort_values("mn", ascending=False)
        if len(bigs) < 1:
            continue
        big1 = bigs.iloc[0]
        big2 = bigs.iloc[1] if len(bigs) > 1 else None
        nxt_ss = ss + 1
        big1_next = minmap.get((nxt_ss, tid, big1.player_id), 0)
        big2_next = minmap.get((nxt_ss, tid, big2.player_id), 0) if big2 is not None else 0
        # any team next season at all?
        team_next = tm[(tm.ss == nxt_ss) & (tm.team_id == tid)]
        if not len(team_next):
            continue
        if big1_next < DEPART_MIN:
            classes.append({"hole_ss": nxt_ss, "team_id": tid, "subgroup": "lost_primary",
                            "primary_pid": None})
        elif (big1_next >= STAY_MIN and big2 is not None and big2_next < DEPART_MIN):
            # retained primary, lost second; require no NEW big replacement >=1500 not on prior roster
            prev_roster = set(g.player_id)
            new_bigs = team_next[team_next.player_id.map(pos).isin(BIG) & (team_next.mn >= REPLACE_MIN)
                                 & (~team_next.player_id.isin(prev_roster))]
            classes.append({"hole_ss": nxt_ss, "team_id": tid,
                            "subgroup": "retained_primary" if len(new_bigs) == 0 else "retained_primary_replaced",
                            "primary_pid": int(big1.player_id)})
    C = pd.DataFrame(classes)
    C = C[(C.hole_ss >= 2014) & (C.hole_ss <= 2024)]
    print("subgroup counts (hole seasons 2014-24):")
    print(C.subgroup.value_counts().to_string())

    # ---- panel: DRB per team-season, whole-team + primary-off ----
    files = sorted(PANEL.glob("*.parquet"))
    print(f"\nloading {len(files)} panel games...", flush=True)
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

    def persistence(cases, metric, split=25):
        rows = []
        for r in cases.itertuples():
            sub = df[(df.team_id == r.team_id) & (df.ss == r.hole_ss)]
            if not len(sub):
                continue
            if metric == "whole":
                e, rest = sub[sub.game_no <= split], sub[sub.game_no > split]
            else:  # primary_off
                if r.primary_pid is None or pd.isna(r.primary_pid):
                    continue
                ppid = str(int(r.primary_pid))  # column is float (None-mixed); cast cleanly
                off = sub[~sub.lineup_id.map(lambda L: ppid in L.split(","))]
                e, rest = off[off.game_no <= split], off[off.game_no > split]
            de, dr = drb(e), drb(rest)
            if pd.notna(de) and pd.notna(dr):
                rows.append((de, dr))
        return np.array(rows)

    print("\n" + "=" * 78)
    print("SUBGROUP VALIDITY (early first-25 -> rest DRB persistence)")
    print("=" * 78)
    for sg in ["lost_primary", "retained_primary", "retained_primary_replaced"]:
        cases = C[C.subgroup == sg]
        print(f"\n[{sg}]  n_cases={len(cases)}")
        for metric in ["whole", "primary_off"]:
            if metric == "primary_off" and sg == "lost_primary":
                continue  # no retained primary to hold off
            arr = persistence(cases, metric)
            if len(arr) >= 2:
                rho, _ = spearmanr(arr[:, 0], arr[:, 1])
                sign = sign_consistency(arr[:, 0], arr[:, 1])
                print(f"   {metric:12s}: n={len(arr):3d} Spearman={rho:+.3f} sign={sign:.3f} "
                      f"-> {verdict(rho, sign, len(arr))}")
            else:
                print(f"   {metric:12s}: n={len(arr)} (too few)")

    # ---- whole-team DRB reliability r(25) across ALL team-seasons (redesigned binding metric) ----
    print("\n" + "=" * 78)
    print("WHOLE-TEAM DRB reliability r(25) across ALL 330 team-seasons (binding metric)")
    print("=" * 78)
    from scipy.stats import pearsonr
    for N in [10, 15, 20, 25, 30]:
        rows = []
        for (tid, ss), sub in df.groupby(["team_id", "ss"]):
            e, rest = sub[sub.game_no <= N], sub[sub.game_no > N]
            de, dr = drb(e), drb(rest)
            if pd.notna(de) and pd.notna(dr):
                rows.append((de, dr))
        arr = np.array(rows)
        r, _ = pearsonr(arr[:, 0], arr[:, 1])
        print(f"   N={N}: r={r:.3f} (n={len(arr)})")

    # ---- whole-team scorecard for threshold (like AVAIL-PACE) ----
    print("\n" + "=" * 78)
    print("WHOLE-TEAM DRB scorecard: rest percentile by R2 (game-37) percentile bucket")
    print("=" * 78)
    rows = []
    for (tid, ss), sub in df.groupby(["team_id", "ss"]):
        d20 = drb(sub[sub.game_no <= 20]); d37 = drb(sub[sub.game_no <= 37])
        drest = drb(sub[sub.game_no > 37])
        if pd.notna(d20) and pd.notna(d37) and pd.notna(drest):
            rows.append({"tid": tid, "ss": ss, "d20": d20, "d37": d37, "drest": drest})
    s = pd.DataFrame(rows)
    for c in ["d20", "d37", "drest"]:
        s[c + "_pct"] = s.groupby("ss")[c].rank(pct=True)
    s.to_parquet(DATA / "fcdrb_wholeteam_cases.parquet", index=False)
    s["b"] = pd.cut(s.d37_pct, [0, 0.2, 0.33, 0.5, 1.0], labels=["bot20", "20-33", "33-50", "top50"])
    print(s.groupby("b", observed=True).agg(
        n=("d37_pct", "size"), mean_rest_pct=("drest_pct", "mean"),
        p_rest_bot33=("drest_pct", lambda z: (z <= 0.33).mean()),
        p_rest_bot25=("drest_pct", lambda z: (z <= 0.25).mean())).to_string())
    print("\ntwo-read joint (bottom-third at BOTH game-20 and game-37):")
    for cut in [0.25, 0.33]:
        fire = s[(s.d20_pct <= cut) & (s.d37_pct <= cut)]
        print(f"  cut={cut}: n_fire={len(fire)}, P(rest bottom-third)={(fire.drest_pct<=0.33).mean():.3f}, "
              f"mean rest pct={fire.drest_pct.mean():.3f}")


if __name__ == "__main__":
    main()

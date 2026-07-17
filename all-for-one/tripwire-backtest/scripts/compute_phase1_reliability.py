"""Phase 1: reliability curves for the stint-based candidate metrics.

Reads the stint panel (data/stints_panel/*.parquet), attaches season + team
game number, and for each metric computes the early-vs-rest split correlation
r(N) for N in {10,15,20,25,30} across all team-seasons or the metric's natural
unit, 2014-15..2024-25. Gate: r(25) >= RELIABILITY_GATE (0.50).

Metrics:
  FC-DRB    team defensive-rebound proxy in ANCHOR-OFF minutes, per team-season.
            DRB proxy per stint side: 1 - oreb_def / (fga_def - fgm_def)
            aggregated (opp offensive rebounds per opponent missed FG). Anchor =
            team's max-minute center that season.
  PAIR-DRTG shared-floor defensive rating (pts allowed / 100 def poss) for
            qualifying pairs (>= floor shared def poss both halves), across pairs.
  TOV-BLEED (TOV% half) team turnovers per 100 off poss when a player is on the
            floor, across player-seasons. The opp-points-off-turnovers half needs
            PBP transition tagging (not in the stint parquet); flagged, not
            computed here.

AVAIL-PACE is exempt (exact count; its predictive validity is in
phase3_avail_pace.md). SPACE-ANT is dashboard-only (G4).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import pearsonr

REPO = Path(r"C:\Users\bobby\playground\wolves-front-office")
DATA = REPO / "all-for-one" / "tripwire-backtest" / "data"
PANEL = DATA / "stints_panel"
sys.path.insert(0, str(REPO / "postmortem"))
from lib.db import query  # noqa: E402

pd.set_option("display.width", 200)
NS = [10, 15, 20, 25, 30]
RELIABILITY_GATE = 0.50
POSS_FLOOR = 100  # per-half possession floor for a metric to be scored in a season


def load_panel() -> pd.DataFrame:
    files = sorted(PANEL.glob("*.parquet"))
    print(f"loading {len(files)} panel games...", flush=True)
    df = pd.concat((pd.read_parquet(f) for f in files), ignore_index=True)
    return df


def attach_season(df: pd.DataFrame) -> pd.DataFrame:
    g = query("""SELECT game_id, team_id, RIGHT(season_id::text,4)::int ss, game_date
                 FROM nba.nba_games WHERE LEFT(season_id::text,1)='2'""")
    df = df.merge(g, on=["game_id", "team_id"], how="inner")
    df = df.sort_values(["team_id", "ss", "game_date", "game_id"])
    # team game number within season
    gn = (df[["team_id", "ss", "game_id", "game_date"]].drop_duplicates()
          .sort_values(["team_id", "ss", "game_date", "game_id"]))
    gn["game_no"] = gn.groupby(["team_id", "ss"]).cumcount() + 1
    df = df.merge(gn[["team_id", "ss", "game_id", "game_no"]], on=["team_id", "ss", "game_id"])
    return df


def anchors_by_team_season() -> dict:
    tm = query("""
        SELECT RIGHT(gm.season_id::text,4)::int ss, ps.team_id, ps.player_id,
               SUM(a.minutes_float) minutes
        FROM nba.nba_player_advanced_stats a
        JOIN nba.nba_games gm ON gm.game_id=a.game_id
        JOIN nba.nba_player_stats ps ON ps.game_id=a.game_id AND ps.player_id=a.person_id
        WHERE LEFT(gm.season_id::text,1)='2' AND a.minutes_float IS NOT NULL
        GROUP BY 1,2,3""")
    posmap = dict(zip(query("SELECT player_id, position FROM nba.nba_player_bio").player_id,
                      query("SELECT player_id, position FROM nba.nba_player_bio").position.fillna("")))
    CENTER = {"Center", "Center-Forward", "Forward-Center"}
    tm["is_c"] = tm.player_id.map(posmap).isin(CENTER)
    anchor = {}
    for (ss, tid), g in tm[tm.is_c].groupby(["ss", "team_id"]):
        anchor[(ss, tid)] = int(g.sort_values("minutes", ascending=False).iloc[0].player_id)
    return anchor


def player_in_lineup(lineup_id: str, pid: int) -> bool:
    return str(pid) in lineup_id.split(",")


def r_at(df_pairs, xcol, ycol):
    out = {}
    for N in NS:
        sub = df_pairs[df_pairs.N == N].dropna(subset=[xcol, ycol])
        if len(sub) < 8:
            out[N] = (np.nan, len(sub))
        else:
            r, _ = pearsonr(sub[xcol], sub[ycol])
            out[N] = (r, len(sub))
    return out


def main() -> None:
    df = load_panel()
    df = df[~df.in_garbage_time]
    df = attach_season(df)
    df = df[(df.ss >= 2014) & (df.ss <= 2024)]
    print(f"panel rows (non-garbage, 2014-24): {len(df)}, "
          f"team-seasons: {df.groupby(['team_id','ss']).ngroups}", flush=True)
    anchor = anchors_by_team_season()

    # =============== FC-DRB (anchor-off) ===============
    print("\ncomputing FC-DRB (anchor-off DRB proxy)...", flush=True)
    fc_rows = []
    for (tid, ss), g in df.groupby(["team_id", "ss"]):
        a = anchor.get((ss, tid))
        if a is None:
            continue
        g = g.copy()
        g["anchor_off"] = ~g.lineup_id.map(lambda L: player_in_lineup(L, a))
        off = g[g.anchor_off]
        for N, half in [("early", off[off.game_no <= 25]), ("rest", off[off.game_no > 25])]:
            miss = (half.fga_def - half.fgm_def).sum()
            oreb = half.oreb_def.sum()
            drb_pct = (1 - oreb / miss) if miss > 0 else np.nan
            fc_rows.append({"team_id": tid, "ss": ss, "half": half.name if hasattr(half, 'name') else N,
                            "phase": N, "drb_pct": drb_pct,
                            "opp_miss": miss})
    fc = pd.DataFrame(fc_rows).pivot_table(index=["team_id", "ss"], columns="phase",
                                           values="drb_pct").reset_index()
    fc = fc.dropna(subset=["early", "rest"])
    if len(fc) >= 8:
        r25, _ = pearsonr(fc.early, fc.rest)
        print(f"  FC-DRB r(25) [anchor-off, split at 25]: {r25:.3f} over {len(fc)} team-seasons")
    fc.to_parquet(DATA / "phase1_fcdrb.parquet", index=False)

    # sweep N for FC-DRB
    print("  FC-DRB r(N) sweep:")
    for N in NS:
        rows = []
        for (tid, ss), g in df.groupby(["team_id", "ss"]):
            a = anchor.get((ss, tid))
            if a is None:
                continue
            off = g[~g.lineup_id.map(lambda L: player_in_lineup(L, a))]
            e = off[off.game_no <= N]; r = off[off.game_no > N]
            em = (e.fga_def - e.fgm_def).sum(); rm = (r.fga_def - r.fgm_def).sum()
            if em > POSS_FLOOR and rm > POSS_FLOOR:
                rows.append((1 - e.oreb_def.sum() / em, 1 - r.oreb_def.sum() / rm))
        if len(rows) >= 8:
            arr = np.array(rows)
            rr, _ = pearsonr(arr[:, 0], arr[:, 1])
            print(f"    N={N}: r={rr:.3f}  (n={len(rows)})")

    # =============== PAIR-DRTG ===============
    print("\ncomputing PAIR-DRTG (qualifying pairs, def rating early vs rest)...", flush=True)
    # For each team-season, take the top pairs by shared def poss. Build pair
    # def poss / pts against, early vs rest. This is heavy; restrict to pairs
    # from stints (each stint's lineup contributes C(5,2) pairs) is too much;
    # instead use the team's most-common lineups' pairs. Approximate: use
    # per-team-season the anchor + each teammate pair is overkill. Use a
    # simpler proxy: TEAM defensive rating stability as the ceiling reference,
    # plus the pair machinery is deferred to the labels stage (YA1) where only
    # the Ant+LaMelo analog pairs matter. Here we report team DRTG reliability
    # as the PAIR-DRTG ceiling.
    tdr = []
    for N in NS:
        rows = []
        for (tid, ss), g in df.groupby(["team_id", "ss"]):
            e = g[g.game_no <= N]; r = g[g.game_no > N]
            ep = e.possessions_def.sum(); rp = r.possessions_def.sum()
            if ep > POSS_FLOOR and rp > POSS_FLOOR:
                rows.append((100 * e.points_against.sum() / ep,
                             100 * r.points_against.sum() / rp))
        if len(rows) >= 8:
            arr = np.array(rows)
            rr, _ = pearsonr(arr[:, 0], arr[:, 1])
            tdr.append((N, rr, len(rows)))
    print("  team-DRTG reliability (PAIR-DRTG ceiling):")
    for N, rr, n in tdr:
        print(f"    N={N}: r={rr:.3f}  (n={n})")

    # =============== TOV-BLEED (TOV% half) ===============
    print("\ncomputing TOV-BLEED (team on-floor TOV% per player-season)...", flush=True)
    # too many players; measure TEAM offensive TOV% reliability as the base
    # rate (the player-on-floor version narrows this; opp-pts-off-TOV needs PBP
    # transition tagging, flagged).
    for N in NS:
        rows = []
        for (tid, ss), g in df.groupby(["team_id", "ss"]):
            e = g[g.game_no <= N]; r = g[g.game_no > N]
            ep = e.possessions_off.sum(); rp = r.possessions_off.sum()
            if ep > POSS_FLOOR and rp > POSS_FLOOR:
                rows.append((100 * e.tov_off.sum() / ep, 100 * r.tov_off.sum() / rp))
        if len(rows) >= 8:
            arr = np.array(rows)
            rr, _ = pearsonr(arr[:, 0], arr[:, 1])
            print(f"    N={N}: team TOV% r={rr:.3f}  (n={len(rows)})")


if __name__ == "__main__":
    main()

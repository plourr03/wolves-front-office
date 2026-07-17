"""Compute the Jaden markers BEFORE -> AFTER for every marker-usable class member.

Warehouse-computable markers (this script):
  JO-EFF   ts_pct (nba_player_season_bio) vs league mean AND vs own trailing-3.
  JO-FLOOR scoring attempts / 75 poss = (FGA + 0.44*FTA)/poss*75.
           FGA/FTA from nba_player_stats, poss from nba_player_advanced_stats.
  JO-GROWTH (a) self-created eff: tracking PullUpShot (pull_up_efg_pct, pull_up_fga)
              + Drives (drive_fg_pct, drive_pts, drive_fga).
            (b) FT rate = FTA/FGA.
            (c) 3P volume (fg3a/g) AND accuracy (fg3_pct), both rising.
  JD-LOAD  share of the wing's defensive partial_possessions spent on high-usage
           perimeter creators (nba_boxscore_matchups). before vs after.
  JD-HOLD  possession-weighted mean of (pts allowed per poss by the wing minus the
           opponent's own season baseline excluding the wing), over primary-option
           opponents guarded >= floor possessions. before vs after (a diff-in-diff).

JD-COVER is stint/lineup-dependent -> computed in compute_jd_cover.py (stint panel).

BEFORE / AFTER seasons come from calibration_class.parquet. Season scoping:
  BEFORE = full before_ss season (all teams); AFTER = new-team games in after_ss.
Grain notes: season_bio / tracking are per primary team-stint; we take the
max-gp row. Join on nba_player_id / person_id only.

Writes data/marker_movements.parquet and prints seed sanity + class distributions.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(r"C:\Users\bobby\playground\wolves-front-office")
OUTDIR = REPO / "all-for-one" / "board" / "jaden_calibration" / "data"
sys.path.insert(0, str(REPO / "postmortem"))
from lib.db import query  # noqa: E402

pd.set_option("display.width", 240)
pd.set_option("display.max_rows", 200)
pd.set_option("display.max_columns", 80)

# --- tunables (all reported, none frozen) ---
OPP_CREATOR_USG = 0.25      # "primary perimeter creator" opponent bar (season usg)
HOLD_POSS_FLOOR = 20        # min partial-possessions vs an opponent to count for JD-HOLD
LEAGUE_TS_GP_FLOOR = 30     # league-mean ts baseline: players with gp>=30
SEEDS = {203932: "Aaron Gordon", 1628969: "Mikal Bridges", 1628384: "OG Anunoby"}


def ss_to_str(ss):
    return f"{int(ss)}-{str(int(ss)+1)[-2:]}"


def main() -> None:
    c = pd.read_parquet(OUTDIR / "calibration_class.parquet")
    mu = c[c.marker_usable].copy().reset_index(drop=True)
    print(f"marker-usable members: {len(mu)}")

    pids = sorted(mu.player_id.unique().tolist())
    # season set we need (before and after)
    need = set()
    for r in mu.itertuples():
        for s in (int(r.before_ss), int(r.after_ss)):
            need.add(s)
        # trailing-3 needs before_ss-1, before_ss-2 too
        need.add(int(r.before_ss) - 1)
        need.add(int(r.before_ss) - 2)
    ss_min, ss_max = min(need), max(need)

    # ---------------- season_bio (ts, usg) : whole table for league baselines --------
    bio = query(
        """
        SELECT player_id, LEFT(season_year,4)::int AS ss, team_id, team_abbreviation,
               gp, usg_pct, ts_pct
        FROM nba.nba_player_season_bio WHERE season_type='Regular Season'
        """
    )
    bio["usg_pct"] = pd.to_numeric(bio.usg_pct, errors="coerce")
    bio["ts_pct"] = pd.to_numeric(bio.ts_pct, errors="coerce")
    # one row per player-season (max gp stint)
    bio_ps = (bio.sort_values("gp").groupby(["player_id", "ss"], as_index=False).last())
    ts_map = {(int(r.player_id), int(r.ss)): r.ts_pct for r in bio_ps.itertuples() if pd.notna(r.ts_pct)}
    usg_map = {(int(r.player_id), int(r.ss)): r.usg_pct for r in bio_ps.itertuples() if pd.notna(r.usg_pct)}
    # league mean ts by season (gp floor)
    lg = bio_ps[bio_ps.gp >= LEAGUE_TS_GP_FLOOR].groupby("ss").ts_pct.mean()
    lg_ts = {int(s): float(v) for s, v in lg.items()}

    # ---------------- player_stats box aggregates per (player, ss, team) -------------
    ps = query(
        f"""
        SELECT ps.player_id, LEFT(ps.season_year,4)::int AS ss, ps.team_id,
               COUNT(*) AS gp, SUM(ps.minutes_played) AS mins,
               SUM(ps.fga) AS fga, SUM(ps.fta) AS fta, SUM(ps.ftm) AS ftm,
               SUM(ps.fg3a) AS fg3a, SUM(ps.fg3m) AS fg3m, SUM(ps.pts) AS pts
        FROM nba.nba_player_stats ps
        JOIN nba.nba_games gm ON gm.game_id = ps.game_id AND gm.team_id = ps.team_id
        WHERE LEFT(gm.season_id::text,1) = '2' AND ps.player_id = ANY(%s)
          AND LEFT(ps.season_year,4)::int BETWEEN %s AND %s
        GROUP BY 1,2,3
        """,
        (pids, ss_min, ss_max),
    )
    # ---------------- advanced possessions per (person, ss, team) --------------------
    adv = query(
        f"""
        SELECT a.person_id AS player_id, RIGHT(gm.season_id::text,4)::int AS ss,
               a.team_id, SUM(a.possessions) AS poss
        FROM nba.nba_player_advanced_stats a
        JOIN nba.nba_games gm ON gm.game_id = a.game_id AND gm.team_id = a.team_id
        WHERE LEFT(gm.season_id::text,1) = '2' AND a.person_id = ANY(%s)
          AND RIGHT(gm.season_id::text,4)::int BETWEEN %s AND %s
        GROUP BY 1,2,3
        """,
        (pids, ss_min, ss_max),
    )
    poss_tt = {(int(r.player_id), int(r.ss), int(r.team_id)): float(r.poss) for r in adv.itertuples()}

    # ---------------- tracking PullUpShot + Drives -----------------------------------
    trk = query(
        f"""
        SELECT player_id, LEFT(season_year,4)::int AS ss, measure_type, team_id, gp,
               pull_up_fga, pull_up_pts, pull_up_efg_pct,
               drives, drive_fga, drive_pts, drive_fg_pct
        FROM nba.nba_player_tracking_season
        WHERE season_type='Regular Season' AND player_id = ANY(%s)
          AND measure_type IN ('PullUpShot','Drives')
          AND LEFT(season_year,4)::int BETWEEN %s AND %s
        """,
        (pids, ss_min, ss_max),
    )
    for col in ["pull_up_fga", "pull_up_pts", "pull_up_efg_pct", "drives",
                "drive_fga", "drive_pts", "drive_fg_pct"]:
        trk[col] = pd.to_numeric(trk[col], errors="coerce")
    pu = trk[trk.measure_type == "PullUpShot"].sort_values("gp").groupby(["player_id", "ss"], as_index=False).last()
    dr = trk[trk.measure_type == "Drives"].sort_values("gp").groupby(["player_id", "ss"], as_index=False).last()
    pu_map = {(int(r.player_id), int(r.ss)): r for r in pu.itertuples()}
    dr_map = {(int(r.player_id), int(r.ss)): r for r in dr.itertuples()}

    # ---------------- matchups (JD-LOAD, JD-HOLD) ------------------------------------
    # opponent usg/position lookups
    posbio = query("SELECT player_id, position FROM nba.nba_player_bio")
    pos_map = {int(r.player_id): (r.position or "") for r in posbio.itertuples()}

    # wing-as-defender matchup rows for the needed seasons
    mch = query(
        f"""
        SELECT m.person_id_def, m.person_id_off, RIGHT(gm.season_id::text,4)::int AS ss,
               SUM(COALESCE(m.partial_possessions,0)) AS poss,
               SUM(COALESCE(m.player_points,0)) AS pts
        FROM nba.nba_boxscore_matchups m
        JOIN nba.nba_games gm ON gm.game_id = m.game_id
        WHERE LEFT(gm.season_id::text,1) = '2' AND m.person_id_def = ANY(%s)
          AND RIGHT(gm.season_id::text,4)::int BETWEEN %s AND %s
        GROUP BY 1,2,3
        """,
        (pids, ss_min, ss_max),
    )
    # opponent season totals across ALL defenders (baseline, excl-wing computed per cell)
    opp_tot = query(
        f"""
        SELECT m.person_id_off, RIGHT(gm.season_id::text,4)::int AS ss,
               SUM(COALESCE(m.partial_possessions,0)) AS poss,
               SUM(COALESCE(m.player_points,0)) AS pts
        FROM nba.nba_boxscore_matchups m
        JOIN nba.nba_games gm ON gm.game_id = m.game_id
        WHERE LEFT(gm.season_id::text,1) = '2'
          AND RIGHT(gm.season_id::text,4)::int BETWEEN %s AND %s
        GROUP BY 1,2
        """,
        (ss_min, ss_max),
    )
    opp_tot_map = {(int(r.person_id_off), int(r.ss)): (float(r.poss), float(r.pts)) for r in opp_tot.itertuples()}

    def jd_markers(wing_id, ss):
        sub = mch[(mch.person_id_def == wing_id) & (mch.ss == ss)].copy()
        if not len(sub):
            return {}
        sub["poss"] = sub.poss.astype(float)
        sub["pts"] = sub.pts.astype(float)
        sub = sub[sub.poss > 0]
        total_poss = sub.poss.sum()
        # opponent flags: primary perimeter creator = usg>=bar AND perimeter position
        def is_prim(opp):
            u = usg_map.get((int(opp), ss))
            p = pos_map.get(int(opp), "")
            perimeter = p in ("Guard", "Guard-Forward", "Forward-Guard", "Forward")
            return (u is not None and u >= OPP_CREATOR_USG and perimeter)
        sub["prim"] = sub.person_id_off.map(is_prim)
        load = (sub.loc[sub.prim, "poss"].sum() / total_poss) if total_poss > 0 else np.nan
        # JD-HOLD over primary opponents guarded >= floor poss
        hold_rows = sub[sub.prim & (sub.poss >= HOLD_POSS_FLOOR)]
        diffs, wts = [], []
        for r in hold_rows.itertuples():
            tot = opp_tot_map.get((int(r.person_id_off), ss))
            if not tot:
                continue
            tp, tpts = tot
            base_poss = tp - r.poss
            base_pts = tpts - r.pts
            if base_poss <= 0:
                continue
            wing_rate = r.pts / r.poss
            base_rate = base_pts / base_poss
            diffs.append(wing_rate - base_rate)
            wts.append(r.poss)
        hold = (np.average(diffs, weights=wts) if diffs else np.nan)
        return {"jd_load": load, "jd_hold": hold, "jd_load_totposs": total_poss,
                "jd_hold_nopp": len(hold_rows)}

    # ---------------- assemble per-member marker rows --------------------------------
    def scoring_attempts_per75(pid, ss, team_scope):
        """team_scope: 'all' (before) or a team_id (after)."""
        if team_scope == "all":
            s = ps[(ps.player_id == pid) & (ps.ss == ss)]
            poss = sum(poss_tt.get((pid, ss, int(t)), 0.0) for t in s.team_id.unique())
        else:
            s = ps[(ps.player_id == pid) & (ps.ss == ss) & (ps.team_id == team_scope)]
            poss = poss_tt.get((pid, ss, int(team_scope)), 0.0)
        if not len(s) or poss <= 0:
            return None
        fga = float(s.fga.sum()); fta = float(s.fta.sum())
        gp = int(s.gp.sum())
        fg3a = float(s.fg3a.sum()); fg3m = float(s.fg3m.sum())
        att = fga + 0.44 * fta
        return {
            "sa75": att / poss * 75.0, "fga": fga, "fta": fta, "poss": poss, "gp": gp,
            "ftr": (fta / fga) if fga > 0 else np.nan,
            "fg3a_pg": fg3a / gp if gp else np.nan,
            "fg3_pct": (fg3m / fg3a) if fg3a > 0 else np.nan,
        }

    def self_created(pid, ss):
        pur = pu_map.get((pid, ss)); drr = dr_map.get((pid, ss))
        out = {}
        if pur is not None:
            g = pur.gp or np.nan
            out["pull_up_efg"] = pur.pull_up_efg_pct
            out["pull_up_fga_pg"] = (pur.pull_up_fga / g) if g else np.nan
            out["pull_up_pts"] = pur.pull_up_pts
            out["pull_up_fga"] = pur.pull_up_fga
        if drr is not None:
            g = drr.gp or np.nan
            out["drive_fg_pct"] = drr.drive_fg_pct
            out["drives_pg"] = (drr.drives / g) if g else np.nan
            out["drive_pts"] = drr.drive_pts
            out["drive_fga"] = drr.drive_fga
        # blended self-created points per FGA (pull-ups + drive FGA)
        pu_fga = out.get("pull_up_fga"); pu_pts = out.get("pull_up_pts")
        d_fga = out.get("drive_fga"); d_pts = out.get("drive_pts")
        if all(v is not None and not pd.isna(v) for v in (pu_fga, pu_pts, d_fga, d_pts)) and (pu_fga + d_fga) > 0:
            out["selfcreate_ppfga"] = (pu_pts + d_pts) / (pu_fga + d_fga)
        return out

    rows = []
    for r in mu.itertuples():
        pid = int(r.player_id); b = int(r.before_ss); a = int(r.after_ss)
        # JO-EFF
        b_ts = ts_map.get((pid, b)); a_ts = ts_map.get((pid, a))
        trail = [ts_map.get((pid, b - k)) for k in (0, 1, 2)]
        trail = [t for t in trail if t is not None]
        trail3 = float(np.mean(trail)) if trail else np.nan
        # JO-FLOOR + FTr + 3P
        bf = scoring_attempts_per75(pid, b, "all")
        af = scoring_attempts_per75(pid, a, int(r.new_team_id))
        # JO-GROWTH self-created
        bsc = self_created(pid, b); asc = self_created(pid, a)
        # JD
        bjd = jd_markers(pid, b); ajd = jd_markers(pid, a)

        row = {
            "player_id": pid, "wing": r.wing, "arr_ss": int(r.arr_ss), "kind": r.kind,
            "new_team": r.new_team, "creator": r.creator,
            "before_ss": b, "after_ss": a,
            # JO-EFF
            "ts_before": b_ts, "ts_after": a_ts,
            "ts_delta": (a_ts - b_ts) if (a_ts is not None and b_ts is not None) else np.nan,
            "ts_lg_before": lg_ts.get(b), "ts_lg_after": lg_ts.get(a),
            "ts_vs_lg_before": (b_ts - lg_ts.get(b)) if (b_ts is not None and b in lg_ts) else np.nan,
            "ts_vs_lg_after": (a_ts - lg_ts.get(a)) if (a_ts is not None and a in lg_ts) else np.nan,
            "ts_trail3": trail3,
            "ts_after_vs_trail3": (a_ts - trail3) if (a_ts is not None and not pd.isna(trail3)) else np.nan,
            # JO-FLOOR
            "sa75_before": bf["sa75"] if bf else np.nan,
            "sa75_after": af["sa75"] if af else np.nan,
            # JO-GROWTH (b) FT rate
            "ftr_before": bf["ftr"] if bf else np.nan,
            "ftr_after": af["ftr"] if af else np.nan,
            # JO-GROWTH (c) 3P
            "fg3a_pg_before": bf["fg3a_pg"] if bf else np.nan,
            "fg3a_pg_after": af["fg3a_pg"] if af else np.nan,
            "fg3_pct_before": bf["fg3_pct"] if bf else np.nan,
            "fg3_pct_after": af["fg3_pct"] if af else np.nan,
            # JO-GROWTH (a) self-created
            "pull_up_efg_before": bsc.get("pull_up_efg"), "pull_up_efg_after": asc.get("pull_up_efg"),
            "drive_fg_pct_before": bsc.get("drive_fg_pct"), "drive_fg_pct_after": asc.get("drive_fg_pct"),
            "selfcreate_ppfga_before": bsc.get("selfcreate_ppfga"),
            "selfcreate_ppfga_after": asc.get("selfcreate_ppfga"),
            "pull_up_fga_pg_before": bsc.get("pull_up_fga_pg"), "pull_up_fga_pg_after": asc.get("pull_up_fga_pg"),
            # JD
            "jd_load_before": bjd.get("jd_load"), "jd_load_after": ajd.get("jd_load"),
            "jd_hold_before": bjd.get("jd_hold"), "jd_hold_after": ajd.get("jd_hold"),
            "jd_load_totposs_before": bjd.get("jd_load_totposs"), "jd_load_totposs_after": ajd.get("jd_load_totposs"),
            "jd_hold_nopp_before": bjd.get("jd_hold_nopp"), "jd_hold_nopp_after": ajd.get("jd_hold_nopp"),
        }
        # derived movements
        if bf and af:
            row["sa75_pctchg"] = (af["sa75"] - bf["sa75"]) / bf["sa75"] * 100.0
        row["ftr_delta"] = (row["ftr_after"] - row["ftr_before"]) if pd.notna(row["ftr_after"]) and pd.notna(row["ftr_before"]) else np.nan
        row["fg3a_pg_delta"] = (row["fg3a_pg_after"] - row["fg3a_pg_before"]) if pd.notna(row["fg3a_pg_after"]) and pd.notna(row["fg3a_pg_before"]) else np.nan
        row["fg3_pct_delta"] = (row["fg3_pct_after"] - row["fg3_pct_before"]) if pd.notna(row["fg3_pct_after"]) and pd.notna(row["fg3_pct_before"]) else np.nan
        for k in ("pull_up_efg", "drive_fg_pct", "selfcreate_ppfga"):
            bb = row.get(f"{k}_before"); aa = row.get(f"{k}_after")
            row[f"{k}_delta"] = (aa - bb) if (bb is not None and aa is not None and pd.notna(bb) and pd.notna(aa)) else np.nan
        row["jd_load_delta"] = (row["jd_load_after"] - row["jd_load_before"]) if pd.notna(row.get("jd_load_after")) and pd.notna(row.get("jd_load_before")) else np.nan
        row["jd_hold_delta"] = (row["jd_hold_after"] - row["jd_hold_before"]) if pd.notna(row.get("jd_hold_after")) and pd.notna(row.get("jd_hold_before")) else np.nan
        rows.append(row)

    out = pd.DataFrame(rows).sort_values("wing").reset_index(drop=True)
    out.to_parquet(OUTDIR / "marker_movements.parquet", index=False)
    print(f"wrote {OUTDIR/'marker_movements.parquet'} ({len(out)} members)")

    # seed sanity
    print("\n" + "=" * 100)
    print("SEED SANITY (before -> after)")
    print("=" * 100)
    scols = ["wing", "before_ss", "after_ss", "ts_before", "ts_after", "ts_delta",
             "sa75_before", "sa75_after", "sa75_pctchg", "ftr_before", "ftr_after",
             "fg3a_pg_before", "fg3a_pg_after", "fg3_pct_before", "fg3_pct_after",
             "pull_up_efg_before", "pull_up_efg_after", "drive_fg_pct_before", "drive_fg_pct_after",
             "jd_load_before", "jd_load_after", "jd_hold_before", "jd_hold_after"]
    seed = out[out.player_id.isin(SEEDS)]
    with pd.option_context("display.float_format", lambda v: f"{v:.3f}"):
        print(seed[scols].to_string(index=False))

    # quick NA audit per marker
    print("\nNON-NULL counts per marker (of", len(out), "members):")
    for col in ["ts_delta", "sa75_pctchg", "ftr_delta", "fg3a_pg_delta", "fg3_pct_delta",
                "pull_up_efg_delta", "drive_fg_pct_delta", "selfcreate_ppfga_delta",
                "jd_load_delta", "jd_hold_delta"]:
        print(f"  {col:26s}: {out[col].notna().sum()}")


if __name__ == "__main__":
    main()

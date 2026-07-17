"""Jaden-markers CALIBRATION CLASS extraction.

board_spec v2.0 / jaden_markers.md section 5. Same extraction discipline as the
tripwire Scenario A work (build_reference_class.py): arrivals foundation from
game-level data, diacritic-safe, join on nba_player_id only, seed validation,
curated log for hand-added cases.

THE CLASS: a two-way WING (Forward / Guard-Forward / Forward-Guard) who ARRIVED
at a team that already had (or that season fielded) an established HIGH-USAGE
CREATOR (a teammate with prior- or current-season usg_pct >= 0.28, fraction).
This is the historical analog to Jaden McDaniels sharing a floor with the added
high-usage creator LaMelo Ball. We measure how the wing's OWN per-opportunity
markers moved from a BEFORE baseline (last full season without the creator) to
an AFTER state (first full season with the creator).

Seeds (must appear or get a logged reason):
  Aaron Gordon   ORL -> DEN Mar 2021   creator Nikola Jokic   arr_ss 2020 midseason
  Mikal Bridges  BKN -> NYK 2024-25    creator Jalen Brunson  arr_ss 2024 offseason
  OG Anunoby     TOR -> NYK Dec 2023   creator Jalen Brunson  arr_ss 2023 midseason

Window: arr_ss in [2018, 2025]. Matchup data (the defensive gate markers) covers
2017-18+, so BEFORE = arr_ss-1 must be >= 2017; that bounds arr_ss >= 2018,
exactly the coverage caveat the feasibility doc carries.

BEFORE / AFTER season rule:
  offseason arrival: BEFORE = arr_ss-1 (prior team, no creator); AFTER = arr_ss.
  midseason arrival: BEFORE = arr_ss-1 (prior team, no creator, last full year);
                     AFTER = arr_ss+1 (first FULL season with creator; the
                     arrival season itself is partial and is skipped).
An AFTER season is only usable if it has warehouse data (<= 2025-26) and the
wing played a real season there (>= AFTER_G_FLOOR games at the new team) with the
creator still on the roster.

Writes: data/calibration_class.parquet, data/calibration_class_curation_log.md
Freezes NOTHING; thresholds are proposed downstream and labelled TUNE.
"""
from __future__ import annotations

import sys
import unicodedata as ud
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(r"C:\Users\bobby\playground\wolves-front-office")
TRIP = REPO / "all-for-one" / "tripwire-backtest" / "data"
OUTDIR = REPO / "all-for-one" / "board" / "jaden_calibration" / "data"
sys.path.insert(0, str(REPO / "postmortem"))
from lib.db import query  # noqa: E402

pd.set_option("display.width", 240)
pd.set_option("display.max_rows", 200)
pd.set_option("display.max_columns", 60)

USG_CREATOR = 0.28          # creator bar (fraction), prior OR current season
CREATOR_GP_FLOOR = 40       # creator must have a real season (kills small-sample usg)
WING_POS = {"Forward", "Guard-Forward", "Forward-Guard"}
MPG_FLOOR = 24.0            # starter-level role, both BEFORE and AFTER (era-robust vs raw minutes)
G_FLOOR = 40               # games floor so mpg is meaningful (both seasons; shortened seasons OK)
WING_AFTER_USG_CAP = 0.27   # wing is a SECONDARY option in the pairing, not a primary creator
ARR_MIN, ARR_MAX = 2018, 2025

SEEDS = [
    ("Aaron Gordon", 203932, 2020, "midseason", 203999, "Nikola Jokic"),
    ("Mikal Bridges", 1628969, 2024, "offseason", 1628973, "Jalen Brunson"),
    ("OG Anunoby", 1628384, 2023, "midseason", 1628973, "Jalen Brunson"),
]


def fold(s: str) -> str:
    return "".join(c for c in ud.normalize("NFKD", str(s)) if not ud.combining(c)).lower()


def season_str(start: int) -> str:
    return f"{start}-{str(start + 1)[-2:]}"


def load_game_teams() -> pd.DataFrame:
    """One row per (player, season_start, team): games, first/last date. RS only."""
    df = query(
        """
        SELECT ps.player_id, LEFT(ps.season_year,4)::int AS ss, ps.team_id,
               ps.team_abbreviation AS team, MIN(ps.game_date) AS first_date,
               MAX(ps.game_date) AS last_date, COUNT(*) AS g,
               SUM(ps.minutes_played) AS mins
        FROM nba.nba_player_stats ps
        JOIN nba.nba_games gm ON gm.game_id = ps.game_id AND gm.team_id = ps.team_id
        WHERE LEFT(gm.season_id::text,1) = '2'
          AND ps.minutes_played > 0
          AND LEFT(ps.season_year,4)::int >= 2014
        GROUP BY 1,2,3,4
        """
    )
    return df


def load_usg() -> pd.DataFrame:
    return query(
        """
        SELECT player_id, LEFT(season_year,4)::int AS ss, usg_pct, gp
        FROM nba.nba_player_season_bio
        WHERE season_type='Regular Season'
        """
    )


def main() -> None:
    print("loading arrivals foundation + warehouse maps ...", flush=True)
    foundation = pd.read_parquet(TRIP / "arrivals_foundation.parquet")
    foundation["prior_usg"] = pd.to_numeric(foundation.prior_usg, errors="coerce")
    foundation["prior_min"] = pd.to_numeric(foundation.prior_min, errors="coerce")

    gt = load_game_teams()
    usg = load_usg()
    usg_map = {(int(r.player_id), int(r.ss)): (float(r.usg_pct) if pd.notna(r.usg_pct) else None)
               for r in usg.itertuples()}
    gp_map = {(int(r.player_id), int(r.ss)): (int(r.gp) if pd.notna(r.gp) else 0)
              for r in usg.itertuples()}
    # star set: (player_id, season_start) with an All-Star or All-NBA selection
    hon = pd.read_parquet(TRIP / "honors.parquet")
    hon = hon[hon.resolved & hon.award.isin(["ALL_STAR", "ALL_NBA"])]
    star_set = set(zip(hon.nba_player_id.astype(int), hon.season_start.astype(int)))
    # roster: (ss, team_id) -> list of (player_id, games)
    roster = {}
    for (ss, tid), grp in gt.groupby(["ss", "team_id"]):
        roster[(int(ss), int(tid))] = list(zip(grp.player_id.astype(int), grp.g.astype(int)))
    # games / minutes at (player, ss, team)
    g_map = {(int(r.player_id), int(r.ss), int(r.team_id)): int(r.g) for r in gt.itertuples()}
    tmin_map = {(int(r.player_id), int(r.ss), int(r.team_id)): float(r.mins) for r in gt.itertuples()}
    # season TOTAL games / minutes across teams (player, ss)
    seas = gt.groupby(["player_id", "ss"]).agg(g=("g", "sum"), mins=("mins", "sum")).reset_index()
    seas_g = {(int(r.player_id), int(r.ss)): int(r.g) for r in seas.itertuples()}
    seas_min = {(int(r.player_id), int(r.ss)): float(r.mins) for r in seas.itertuples()}

    names = query("SELECT player_id, first_name, last_name FROM nba.nba_player_bio")
    nm = {int(r.player_id): f"{r.first_name} {r.last_name}" for r in names.itertuples()}

    # ----- restrict foundation to wing arrivals in the window -----
    a = foundation.copy()
    a = a[(a.arr_ss >= ARR_MIN) & (a.arr_ss <= ARR_MAX)]
    a = a[a.position.isin(WING_POS)]
    print(f"wing arrivals (pos in {sorted(WING_POS)}) in [{ARR_MIN},{ARR_MAX}]: {len(a)}")

    # ----- creator detection: a STAR teammate (honors) with a real high-usage season -----
    def qualifies_creator(tm_pid, ss):
        """usg>=0.28 in season ss with a real season (gp>=40) AND a star in ss."""
        u = usg_map.get((tm_pid, ss))
        if u is None or u < USG_CREATOR:
            return None
        if gp_map.get((tm_pid, ss), 0) < CREATOR_GP_FLOOR:
            return None
        if (tm_pid, ss) not in star_set:
            return None
        return u

    def find_creator(pid, arr_ss, new_team_id):
        team = roster.get((arr_ss, int(new_team_id)), [])
        best = None
        for tm_pid, _g in team:
            if tm_pid == pid:
                continue
            # qualify on prior OR current season (each checked for star+gp+usg)
            u_prev = qualifies_creator(tm_pid, arr_ss - 1)
            u_cur = qualifies_creator(tm_pid, arr_ss)
            u_best = max([u for u in (u_prev, u_cur) if u is not None], default=None)
            if u_best is not None:
                if best is None or u_best > best[1]:
                    best = (tm_pid, u_best, usg_map.get((tm_pid, arr_ss - 1)),
                            usg_map.get((tm_pid, arr_ss)))
        return best

    rows = []
    for r in a.itertuples():
        cr = find_creator(int(r.player_id), int(r.arr_ss), int(r.new_team_id))
        if cr is None:
            continue
        cr_pid, cr_usg, cr_prev, cr_cur = cr
        rows.append({
            "player_id": int(r.player_id), "wing": nm.get(int(r.player_id)),
            "arr_ss": int(r.arr_ss), "kind": r.kind,
            "new_team_id": int(r.new_team_id), "new_team": r.new_team,
            "prior_team": r.prior_team, "arr_date": r.arr_date,
            "position": r.position, "wing_prior_usg": r.prior_usg,
            "wing_prior_min": r.prior_min,
            "creator_id": int(cr_pid), "creator": nm.get(int(cr_pid)),
            "creator_usg_max": round(cr_usg, 3),
        })
    c = pd.DataFrame(rows)
    print(f"wing arrivals WITH a high-usage creator (usg>={USG_CREATOR}): {len(c)}")

    # ----- BEFORE / AFTER season resolution -----
    def resolve(row):
        pid, arr_ss, kind = row.player_id, row.arr_ss, row.kind
        before_ss = arr_ss - 1
        after_ss = arr_ss if kind == "offseason" else arr_ss + 1
        # BEFORE: starter role in the wing's last full season (season total across teams)
        b_g = seas_g.get((pid, before_ss), 0)
        b_min = seas_min.get((pid, before_ss), 0.0)
        before_mpg = (b_min / b_g) if b_g else 0.0
        before_ok = b_g >= G_FLOOR and before_mpg >= MPG_FLOOR
        # AFTER: starter role at the NEW team with the creator
        after_ok = after_ss <= 2025
        after_g = g_map.get((pid, after_ss, row.new_team_id), 0)
        after_min = tmin_map.get((pid, after_ss, row.new_team_id), 0.0)
        after_mpg = (after_min / after_g) if after_g else 0.0
        creator_after = after_ok and g_map.get((row.creator_id, after_ss, row.new_team_id), 0) > 0
        wing_after_usg = usg_map.get((pid, after_ss))
        creator_after_usg = usg_map.get((row.creator_id, after_ss))
        secondary = (wing_after_usg is not None and creator_after_usg is not None
                     and wing_after_usg < creator_after_usg
                     and wing_after_usg < WING_AFTER_USG_CAP)
        after_role_ok = bool(after_ok and after_g >= G_FLOOR and after_mpg >= MPG_FLOOR
                             and creator_after)
        return pd.Series({
            "before_ss": before_ss, "after_ss": after_ss,
            "before_games": b_g, "before_mpg": round(before_mpg, 1),
            "after_games_newteam": after_g, "after_mpg": round(after_mpg, 1),
            "creator_on_after_team": bool(creator_after),
            "wing_after_usg": wing_after_usg, "creator_after_usg": creator_after_usg,
            "wing_secondary_after": bool(secondary),
            "before_ok": before_ok, "after_role_ok": after_role_ok,
        })

    c = pd.concat([c, c.apply(resolve, axis=1)], axis=1)

    c = c.sort_values(["arr_ss", "wing"]).reset_index(drop=True)

    # membership.
    # in_class (structural): starter-level two-way wing (BEFORE starter role) who
    #   arrived at a team with a STAR high-usage creator, in a SECONDARY role.
    #   Provisional members whose AFTER season has no data yet keep the secondary
    #   test waived (cannot check the future).
    c["in_class"] = c.before_ok & (c.wing_secondary_after | (c.after_ss > 2025))
    # marker-usable: BEFORE and AFTER both real starter seasons + secondary + data.
    c["marker_usable"] = (c.before_ok & c.after_role_ok & c.wing_secondary_after)

    OUTDIR.mkdir(parents=True, exist_ok=True)
    c.to_parquet(OUTDIR / "calibration_class.parquet", index=False)

    show = ["wing", "arr_ss", "kind", "new_team", "prior_team", "creator",
            "creator_usg_max", "wing_prior_usg", "wing_after_usg", "creator_after_usg",
            "before_ss", "before_mpg", "after_ss", "after_mpg", "after_games_newteam"]
    print("\n" + "=" * 150)
    print("CALIBRATION CLASS -- MARKER-USABLE MEMBERS (BEFORE + AFTER both real starter seasons)")
    print("=" * 150)
    print(c[c.marker_usable][show].to_string(index=False))

    print("\n--- structural members with AFTER not yet computable (future season / no data) ---")
    prov = c[c.in_class & ~c.marker_usable]
    print(prov[["wing", "arr_ss", "kind", "new_team", "creator", "after_ss",
                "after_games_newteam", "after_role_ok", "wing_secondary_after"]].to_string(index=False))

    print(f"\nstructural class size (in_class): {int(c.in_class.sum())}")
    print(f"marker-usable (BEFORE+AFTER both computable): {int(c.marker_usable.sum())}")

    # ----- SEED VALIDATION -----
    print("\n" + "=" * 78)
    print("SEED VALIDATION")
    print("=" * 78)
    seed_log = []
    for label, pid, ss, kind, cr_pid, cr_name in SEEDS:
        m = c[(c.player_id == pid) & (c.arr_ss == ss)]
        if len(m):
            r = m.iloc[0]
            ok_creator = (r.creator_id == cr_pid)
            status = (f"IN CLASS. creator={r.creator} (usg {r.creator_usg_max}), "
                      f"before={season_str(int(r.before_ss))} ({r.before_mpg}mpg), "
                      f"after={season_str(int(r.after_ss))} ({r.after_mpg}mpg), "
                      f"marker_usable={r.marker_usable}")
            if not ok_creator:
                status += f"  [WARN creator mismatch: expected {cr_name} got {r.creator}]"
            print(f"  {label:16s} {season_str(ss)} {kind}: {status}")
            seed_log.append((label, "IN", status))
        else:
            # diagnose why absent
            fm = foundation[(foundation.player_id == pid) & (foundation.arr_ss == ss)]
            if not len(fm):
                reason = "NOT in arrivals foundation (investigate)"
            else:
                fr = fm.iloc[0]
                cr = find_creator(pid, ss, int(fr.new_team_id))
                reason = (f"in foundation pos={fr.position} prior_min={fr.prior_min} "
                          f"creator={'yes' if cr else 'NONE'}")
            print(f"  {label:16s} {season_str(ss)} {kind}: *** ABSENT *** {reason}")
            seed_log.append((label, "ABSENT", reason))

    # ----- curation log -----
    log = OUTDIR / "calibration_class_curation_log.md"
    with open(log, "w", encoding="utf-8") as f:
        f.write("# Calibration class curation log\n\n")
        f.write("Auto-generated by build_calibration_class.py. Freezes nothing.\n\n")
        f.write(f"- Window: arr_ss in [{ARR_MIN},{ARR_MAX}] (matchup coverage 2017-18+ bounds BEFORE>=2017-18).\n")
        f.write(f"- Wing = position in {sorted(WING_POS)} (nba_player_bio). 'Known for defense' is NOT separately enforced (no defense DB filter); descriptive limitation noted in the report.\n")
        f.write(f"- Creator = a STAR teammate (All-Star or All-NBA in {{arr_ss-1, arr_ss}}, honors.parquet) on the new team with usg_pct >= {USG_CREATOR} (prior OR current, fraction) and gp >= {CREATOR_GP_FLOOR}.\n")
        f.write(f"- Starter bar: BEFORE and AFTER both >= {MPG_FLOOR} mpg over >= {G_FLOOR} games (era-robust vs raw minutes; keeps the shortened 2019-20/2020-21 seasons in play).\n")
        f.write(f"- Secondary-role screen: wing AFTER usg < creator AFTER usg AND < {WING_AFTER_USG_CAP} (the wing is not the primary creator in the pairing). No cap on the wing's PRIOR usage (Mikal Bridges was a #1 option at BKN and stays in-class).\n\n")
        f.write(f"Structural class size (in_class): {int(c.in_class.sum())}. Marker-usable: {int(c.marker_usable.sum())}.\n\n")
        f.write("## Seed validation\n\n")
        for label, st, reason in seed_log:
            f.write(f"- **{label}**: {st}. {reason}\n")
        f.write("\n## Members excluded from marker distributions (AFTER not usable)\n\n")
        ex = c[c.in_class & ~c.marker_usable]
        if len(ex):
            for r in ex.itertuples():
                f.write(f"- {r.wing} (arr {season_str(int(r.arr_ss))}, {r.kind}): "
                        f"after_ss={season_str(int(r.after_ss))} games={int(r.after_games_newteam)} "
                        f"creator_on_after={r.creator_on_after_team} -> AFTER not usable "
                        f"({'future/no data' if r.after_ss > 2025 else 'games or creator floor'})\n")
        else:
            f.write("(none)\n")
        f.write("\n## Hand-added cases\n\n(none; class is fully query-derived)\n")

    print(f"\nwrote {OUTDIR/'calibration_class.parquet'} and {log}")


if __name__ == "__main__":
    main()

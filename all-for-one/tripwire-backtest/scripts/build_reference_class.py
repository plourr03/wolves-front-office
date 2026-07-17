"""Phase 2: reference-class extraction (Scenarios A, B, C).

Builds the arrivals foundation from game-level data (nba_player_stats), then
layers the three scenario filters. Joins on nba_player_id only. Applies the
corrected usg bar (0.28) and derives prior-season minutes from minutes_float.

Mandated sensitivities (carry-forwards #2, and the honors finding):
  - usage filter: strict (>=0.28) AND loosened, both reported.
  - incumbent filter: strict (All-NBA in prior 2, or All-Star game-starter)
    AND widened (current-season All-Star, i.e. same season as arrival).

Every seed case (spec section 3) must appear or get a logged exclusion.

Writes case tables to data/refclass_{A,B,C}.parquet. Stint-dependent LABELS
(YA1 pair net rating, YC1 anchor-off rebounding) are computed later, after
the stint panel finishes; this script produces the CLASS and the box-score
features/labels.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(r"C:\Users\bobby\playground\wolves-front-office")
DATA = REPO / "all-for-one" / "tripwire-backtest" / "data"
sys.path.insert(0, str(REPO / "postmortem"))
from lib.db import query  # noqa: E402

pd.set_option("display.width", 220)
pd.set_option("display.max_rows", 200)

USG_STRICT = 0.28
MIN_PRIOR = 1200
ERA_START = 2010  # arrival season_start >= 2010 (2010-11)


def season_str(start: int) -> str:
    return f"{start}-{str(start + 1)[-2:]}"


def start_of(season_year: str) -> int:
    return int(season_year[:4])


# ---------------------------------------------------------------- foundation
def load_game_teams() -> pd.DataFrame:
    """One row per (player, season, team): first date, games. RS only."""
    return query(
        """
        SELECT ps.player_id, ps.season_year, ps.team_id, ps.team_abbreviation,
               MIN(ps.game_date) AS first_date, MAX(ps.game_date) AS last_date,
               COUNT(*) AS g
        FROM nba.nba_player_stats ps
        JOIN nba.nba_games gm ON gm.game_id = ps.game_id AND gm.team_id = ps.team_id
        WHERE LEFT(gm.season_id::text,1) = '2'
          AND ps.minutes_played > 0
          AND LEFT(ps.season_year,4)::int >= 2008
        GROUP BY 1,2,3,4
        """
    )


def build_arrivals(gt: pd.DataFrame) -> pd.DataFrame:
    """Arrival events: (player, arrival_season_start, new_team, prior_team,
    arrival_date, kind in {offseason, midseason})."""
    gt = gt.copy()
    gt["ss"] = gt.season_year.map(start_of)
    rows = []
    for pid, pg in gt.groupby("player_id"):
        by_season = {ss: s.sort_values("first_date") for ss, s in pg.groupby("ss")}
        seasons_with_games = sorted(by_season)
        for ss, s in by_season.items():
            teams = list(s.itertuples())
            # midseason arrivals: every team after the first this season
            for i, t in enumerate(teams):
                if i == 0:
                    # offseason arrival? compare first team of ss to last team of
                    # the most recent PRIOR season with games (handles gap years:
                    # a player who missed a full season, e.g. Simmons 2021-22,
                    # Wall 2019-20, still gets an arrival at his next team).
                    prior_seasons = [x for x in seasons_with_games if x < ss]
                    if not prior_seasons:
                        continue  # truly new to the league (rookie)
                    prev = by_season[prior_seasons[-1]]
                    prev_last = prev.sort_values("last_date").iloc[-1]
                    if prev_last.team_id != t.team_id:
                        rows.append({"player_id": pid, "arr_ss": ss,
                                     "new_team_id": t.team_id, "new_team": t.team_abbreviation,
                                     "prior_team_id": prev_last.team_id, "prior_team": prev_last.team_abbreviation,
                                     "arr_date": t.first_date, "kind": "offseason"})
                else:
                    prev_t = teams[i - 1]
                    rows.append({"player_id": pid, "arr_ss": ss,
                                 "new_team_id": t.team_id, "new_team": t.team_abbreviation,
                                 "prior_team_id": prev_t.team_id, "prior_team": prev_t.team_abbreviation,
                                 "arr_date": t.first_date, "kind": "midseason"})
    return pd.DataFrame(rows)


def prior_season_usage() -> pd.DataFrame:
    """usg_pct and gp per player-season (rate stats, from bio)."""
    return query(
        """
        SELECT player_id, LEFT(season_year,4)::int AS ss, usg_pct, gp
        FROM nba.nba_player_season_bio
        WHERE season_type='Regular Season'
        """
    )


def prior_season_minutes() -> pd.DataFrame:
    """Total minutes per player-season from minutes_float (RS)."""
    return query(
        """
        SELECT ps.player_id, LEFT(gm.season_id::text,4) || '' AS ss_txt,
               RIGHT(gm.season_id::text,4)::int AS ss,
               SUM(a.minutes_float) AS minutes
        FROM nba.nba_player_advanced_stats a
        JOIN nba.nba_games gm ON gm.game_id = a.game_id
        JOIN nba.nba_player_stats ps ON ps.game_id = a.game_id AND ps.player_id = a.person_id
        WHERE LEFT(gm.season_id::text,1)='2' AND a.minutes_float IS NOT NULL
        GROUP BY 1,2,3
        """
    )


def position_map() -> dict:
    bio = query("SELECT player_id, position FROM nba.nba_player_bio")
    return dict(zip(bio.player_id, bio.position.fillna("")))


def honors() -> pd.DataFrame:
    return pd.read_parquet(DATA / "honors.parquet")


GUARD_POS = {"Guard", "Guard-Forward", "Forward-Guard"}


def incumbent_qualifies(honors_df, team_players_by_season, arr_ss, new_team_id, arriving_pid):
    """Return (strict_ok, widened_ok, who_strict, who_widened).
    strict: some OTHER player on new_team in arr_ss with All-NBA in {arr_ss-1,
    arr_ss-2} OR All-Star game-starter in that window.
    widened: additionally counts a current-season (arr_ss) All-Star selection.
    """
    roster = team_players_by_season.get((arr_ss, new_team_id), set()) - {arriving_pid}
    if not roster:
        return (False, False, None, None)
    win = {arr_ss - 1, arr_ss - 2}
    strict_who, wide_who = None, None
    for pid in roster:
        h = honors_df[honors_df.nba_player_id == pid]
        if not len(h):
            continue
        hw = h[h.season_start.isin(win)]
        anba = (hw.award == "ALL_NBA").any()
        as_start = ((hw.award == "ALL_STAR") & (hw.is_starter == True)).any()
        if anba or as_start:
            strict_who = pid
        # widened: current-season All-Star (any) or prior-window All-Star (any)
        cur = h[(h.season_start == arr_ss) & (h.award == "ALL_STAR")]
        as_any_win = ((hw.award == "ALL_STAR")).any()
        if anba or as_start or len(cur) or as_any_win:
            wide_who = pid
    return (strict_who is not None, wide_who is not None, strict_who, wide_who)


def main() -> None:
    print("loading foundation...", flush=True)
    gt = load_game_teams()
    arrivals = build_arrivals(gt)
    arrivals = arrivals[arrivals.arr_ss >= ERA_START]
    usage = prior_season_usage()
    minutes = prior_season_minutes()
    posmap = position_map()
    hon = honors()

    # roster membership: (season_start, team_id) -> set(player_id)
    gt2 = gt.copy(); gt2["ss"] = gt2.season_year.map(start_of)
    roster = gt2.groupby(["ss", "team_id"]).player_id.apply(set).to_dict()

    # attach prior-season usage/minutes to each arrival (prior = arr_ss - 1)
    usg_map = {(r.player_id, r.ss): r.usg_pct for r in usage.itertuples()}
    gp_map = {(r.player_id, r.ss): r.gp for r in usage.itertuples()}
    min_map = {(r.player_id, r.ss): r.minutes for r in minutes.itertuples()}

    a = arrivals.copy()
    a["prior_ss"] = a.arr_ss - 1
    a["prior_usg"] = [usg_map.get((p, s)) for p, s in zip(a.player_id, a.prior_ss)]
    a["prior_min"] = [min_map.get((p, s)) for p, s in zip(a.player_id, a.prior_ss)]
    a["position"] = a.player_id.map(posmap)
    a["is_guard"] = a.position.isin(GUARD_POS)

    # ---- Scenario A ----
    print("building Scenario A...", flush=True)
    incs, incw, whs, whw = [], [], [], []
    for r in a.itertuples():
        so, sw, ws, ww = incumbent_qualifies(hon, roster, r.arr_ss, r.new_team_id, r.player_id)
        incs.append(so); incw.append(sw); whs.append(ws); whw.append(ww)
    a["inc_strict"] = incs; a["inc_widened"] = incw
    a["inc_who_strict"] = whs; a["inc_who_widened"] = whw

    base = a[(a.prior_usg.notna()) & (a.prior_min.notna())].copy()
    # name lookup for readability
    names = query("SELECT player_id, first_name||' '||last_name nm FROM nba.nba_player_bio")
    nm = dict(zip(names.player_id, names.nm))
    base["arriving"] = base.player_id.map(nm)
    base["inc_strict_name"] = base.inc_who_strict.map(lambda x: nm.get(x) if pd.notna(x) else None)

    scenA = base[base.is_guard & (base.prior_min >= MIN_PRIOR)].copy()
    scenA_strict = scenA[(scenA.prior_usg >= USG_STRICT) & scenA.inc_strict]
    scenA_loose_usg = scenA[(scenA.prior_usg >= 0.25) & scenA.inc_strict]
    scenA_wide_inc = scenA[(scenA.prior_usg >= USG_STRICT) & scenA.inc_widened]

    print(f"\nScenario A class sizes:")
    print(f"  strict (usg>=0.28, incumbent strict):       {len(scenA_strict)}")
    print(f"  loosened usage (usg>=0.25, incumbent strict): {len(scenA_loose_usg)}")
    print(f"  widened incumbent (usg>=0.28, inc widened):   {len(scenA_wide_inc)}")

    cols = ["arriving", "arr_ss", "new_team", "prior_team", "kind", "arr_date",
            "prior_usg", "prior_min", "inc_strict", "inc_widened", "inc_strict_name"]
    scenA_out = scenA[cols].sort_values(["arr_ss", "arriving"]).reset_index(drop=True)
    scenA_out.to_parquet(DATA / "refclass_A.parquet", index=False)

    # save the arrivals foundation too (B/C build on it)
    a.to_parquet(DATA / "arrivals_foundation.parquet", index=False)
    print(f"\nwrote refclass_A.parquet ({len(scenA_out)} guard-arrivals with prior data), "
          f"arrivals_foundation.parquet ({len(a)} arrivals)")

    # ---- seed reconciliation (Scenario A core) ----
    print("\n" + "=" * 78)
    print("SEED RECONCILIATION (Scenario A core class)")
    print("=" * 78)
    seeds = [
        ("Damian Lillard", 2023), ("Kyrie Irving", 2022), ("James Harden", 2020),
        ("James Harden", 2021), ("James Harden", 2023), ("Russell Westbrook", 2021),
        ("Chris Paul", 2020), ("Donovan Mitchell", 2022), ("Bradley Beal", 2023),
        ("De'Aaron Fox", 2024), ("Luka Doncic", 2024), ("Dejounte Murray", 2024),
    ]
    import unicodedata as _ud

    def _fold(s):
        return "".join(c for c in _ud.normalize("NFKD", str(s))
                       if not _ud.combining(c)).lower()
    scenA_fold = scenA.assign(_f=scenA.arriving.map(_fold))
    for nmz, ss in seeds:
        m = scenA_fold[(scenA_fold._f == _fold(nmz)) & (scenA_fold.arr_ss == ss)]
        if len(m):
            r = m.iloc[0]
            in_strict = (r.prior_usg >= USG_STRICT) and r.inc_strict
            tags = []
            if not (r.prior_usg >= USG_STRICT):
                tags.append(f"usg {r.prior_usg:.3f}<0.28")
            if not r.inc_strict:
                tags.append("inc not strict" + (" (widened OK)" if r.inc_widened else " (NONE)"))
            status = "IN strict" if in_strict else "OUT strict: " + ", ".join(tags)
            print(f"  {nmz:20s} {season_str(ss)}: {status}")
        else:
            print(f"  {nmz:20s} {season_str(ss)}: *** NOT IN ARRIVALS *** (investigate)")


if __name__ == "__main__":
    main()

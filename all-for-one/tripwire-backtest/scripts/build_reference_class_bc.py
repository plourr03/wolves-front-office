"""Phase 2: Scenario B (availability) and C (frontcourt succession) classes.

Builds on arrivals_foundation.parquet (from build_reference_class.py) and the
warehouse. Box-score class construction; stint-dependent labels come later.

Scenario B: an arriving player (any position) who missed >= 30% of games in
  >= 2 of the four prior seasons. Seeds: Simmons-BKN 2022, Wall-HOU 2020,
  Irving-DAL 2023, LaVine-SAC 2025, Porzingis-BOS 2023, Lonzo-CHI 2021,
  Leonard-LAC 2019, George-LAC 2019, Middleton-WAS 2025.

Scenario C: a team whose leading or second rim-minutes anchor departed in the
  offseason with no incoming replacement above a minutes threshold. Seeds:
  Rockets 2020 post-Capela, Nets 2021 post-Allen, Jazz 2022 post-Gobert,
  Lakers 2025 post-Davis, Bucks 2025 post-Lopez.
"""
from __future__ import annotations

import sys
import unicodedata
import re
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(r"C:\Users\bobby\playground\wolves-front-office")
DATA = REPO / "all-for-one" / "tripwire-backtest" / "data"
sys.path.insert(0, str(REPO / "postmortem"))
from lib.db import query  # noqa: E402

pd.set_option("display.width", 220)
pd.set_option("display.max_rows", 200)


def fold(s):
    return re.sub(r"[^a-z ]", "", unicodedata.normalize("NFKD", str(s))
                  .encode("ascii", "ignore").decode().lower()).strip()


def season_str(start):
    return f"{start}-{str(start + 1)[-2:]}"


# season -> scheduled games (for missed-% denominator)
SEASON_GAMES = {2008: 82, 2009: 82, 2010: 82, 2011: 66, 2012: 82, 2013: 82,
                2014: 82, 2015: 82, 2016: 82, 2017: 82, 2018: 82, 2019: 72,
                2020: 72, 2021: 82, 2022: 82, 2023: 82, 2024: 82, 2025: 82}


def main() -> None:
    a = pd.read_parquet(DATA / "arrivals_foundation.parquet")
    bio = query("""SELECT player_id, LEFT(season_year,4)::int ss, gp, position
                   FROM nba.nba_player_season_bio b
                   JOIN nba.nba_player_bio pb USING (player_id)
                   WHERE season_type='Regular Season'""")
    gp_map = {(r.player_id, r.ss): r.gp for r in bio.itertuples()}
    # relevance: the arriving player was a genuine ROTATION REGULAR when healthy,
    # i.e. in >= 1 of the four prior seasons (with >= 20 games) he averaged
    # >= 24 minutes per game. This keeps the availability question meaningful
    # (a star/starter the team is counting on: Simmons, Wall, Irving) and drops
    # journeymen whose "missed games" are bench/waiver churn, not injury absence
    # (Scalabrine, Kwame Brown). Documented added filter; spec leaves B role-open.
    minrows = query("""
        SELECT ps.player_id, RIGHT(gm.season_id::text,4)::int ss,
               SUM(a.minutes_float) mins, COUNT(*) g
        FROM nba.nba_player_advanced_stats a
        JOIN nba.nba_games gm ON gm.game_id=a.game_id
        JOIN nba.nba_player_stats ps ON ps.game_id=a.game_id AND ps.player_id=a.person_id
        WHERE LEFT(gm.season_id::text,1)='2' AND a.minutes_float IS NOT NULL
        GROUP BY 1,2""")
    mpg_map = {(r.player_id, r.ss): (r.mins / r.g if r.g else 0, r.g) for r in minrows.itertuples()}

    def rotation_player(pid, arr_ss):
        for s in range(arr_ss - 4, arr_ss):
            mpg, g = mpg_map.get((pid, s), (0, 0))
            if g >= 20 and mpg >= 24:
                return True
        return False
    names = query("SELECT player_id, first_name||' '||last_name nm FROM nba.nba_player_bio")
    nm = dict(zip(names.player_id, names.nm))

    # ---------------- Scenario B ----------------
    def missed_seasons(pid, arr_ss):
        cnt, detail = 0, []
        for s in range(arr_ss - 4, arr_ss):
            gp = gp_map.get((pid, s))
            if gp is None:
                continue
            sched = SEASON_GAMES.get(s, 82)
            missed = 1 - gp / sched
            if missed >= 0.30:
                cnt += 1
            detail.append((s, gp, round(missed, 2)))
        return cnt, detail

    brows = []
    for r in a.itertuples():
        cnt, det = missed_seasons(r.player_id, r.arr_ss)
        if cnt >= 2 and rotation_player(r.player_id, r.arr_ss):
            brows.append({"arriving": nm.get(r.player_id), "player_id": r.player_id,
                          "arr_ss": r.arr_ss, "new_team": r.new_team,
                          "kind": r.kind, "arr_date": r.arr_date,
                          "n_missed_seasons": cnt})
    scenB = pd.DataFrame(brows).drop_duplicates(["player_id", "arr_ss"])
    scenB = scenB[scenB.arr_ss >= 2010].sort_values(["arr_ss", "arriving"]).reset_index(drop=True)
    scenB.to_parquet(DATA / "refclass_B.parquet", index=False)
    print(f"Scenario B class size: {len(scenB)}")

    seedsB = [("Ben Simmons", 2021), ("John Wall", 2020), ("Kyrie Irving", 2022),
              ("Zach LaVine", 2024), ("Kristaps Porzingis", 2023), ("Lonzo Ball", 2021),
              ("Kawhi Leonard", 2019), ("Paul George", 2019), ("Khris Middleton", 2024)]
    print("\nSEED RECONCILIATION (Scenario B):")
    for nmz, ss in seedsB:
        m = scenB[(scenB.arriving.map(fold) == fold(nmz)) & (scenB.arr_ss == ss)]
        if len(m):
            print(f"  {nmz:20s} {season_str(ss)}: IN ({int(m.iloc[0].n_missed_seasons)} missed seasons)")
        else:
            cnt, det = missed_seasons(names[names.nm.map(fold) == fold(nmz)].iloc[0].player_id if len(names[names.nm.map(fold)==fold(nmz)]) else -1, ss)
            print(f"  {nmz:20s} {season_str(ss)}: OUT ({cnt} missed seasons; {det})")

    # ---------------- Scenario C ----------------
    # anchor = center (pos C or C-F/F-C) with most RS minutes on a team-season.
    # departure: anchor not on team roster next season. replacement threshold:
    # no incoming center with >= 1500 minutes that season.
    print("\n" + "=" * 78)
    print("Scenario C (frontcourt succession)")
    print("=" * 78)
    tm = query("""
        SELECT LEFT(gm.season_id::text,4) x, RIGHT(gm.season_id::text,4)::int ss,
               ps.team_id, ps.team_abbreviation, ps.player_id,
               SUM(a.minutes_float) minutes
        FROM nba.nba_player_advanced_stats a
        JOIN nba.nba_games gm ON gm.game_id=a.game_id
        JOIN nba.nba_player_stats ps ON ps.game_id=a.game_id AND ps.player_id=a.person_id
        WHERE LEFT(gm.season_id::text,1)='2' AND a.minutes_float IS NOT NULL
        GROUP BY 1,2,3,4,5
    """)
    posmap = dict(zip(query("SELECT player_id, position FROM nba.nba_player_bio").player_id,
                      query("SELECT player_id, position FROM nba.nba_player_bio").position.fillna("")))
    CENTER = {"Center", "Center-Forward", "Forward-Center"}
    tm["is_center"] = tm.player_id.map(posmap).isin(CENTER)

    # Two departure modes:
    #  offseason: anchor of season S plays < 20 games for the team in S+1
    #             (traded/left) -> hole_season = S+1.
    #  midseason: anchor of season S plays a partial S+1 then leaves, OR an
    #             anchor is traded away DURING S (their team-games in S drop and
    #             they finish S elsewhere) -> hole_season = S (the departure
    #             season). Detected via the arrivals foundation: an anchor who
    #             was a midseason DEPARTURE (appears as a midseason arrival
    #             ELSEWHERE) leaves a hole at the old team that season.
    arr = pd.read_parquet(DATA / "arrivals_foundation.parquet")
    mid_depart = {(r.prior_team_id, r.arr_ss): r.player_id
                  for r in arr[arr.kind == "midseason"].itertuples()}

    games_played = tm.groupby(["ss", "team_id", "player_id"]).size()  # not used; minutes proxy
    crows = []
    for (ss, tid), g in tm.groupby(["ss", "team_id"]):
        cen = g[g.is_center]
        if not len(cen) or ss + 1 > 2025:
            continue
        anchor = cen.sort_values("minutes", ascending=False).iloc[0]
        if anchor.minutes < 1500:  # a real anchor, not a fringe backup big
            continue
        prev_roster = set(g.player_id)
        nxt = tm[(tm.ss == ss + 1) & (tm.team_id == tid)]
        # offseason departure: anchor essentially gone next season
        nxt_anchor = nxt[nxt.player_id == anchor.player_id]
        anchor_next_min = nxt_anchor.minutes.sum() if len(nxt_anchor) else 0
        offseason_gone = len(nxt) > 0 and anchor_next_min < 500  # ~ <20 mpg*25g
        # replacement: an ESTABLISHED incoming center (>=1500 min, not a rookie
        # promotion from within) -- relaxed to only exclude when a clearly
        # acquired veteran big takes over.
        nxt_cen = nxt[nxt.player_id.map(posmap).isin(CENTER) & (nxt.minutes >= 1500)]
        incoming = nxt_cen[~nxt_cen.player_id.isin(prev_roster)]
        if offseason_gone:
            crows.append({"team": anchor.team_abbreviation, "hole_season": ss + 1,
                          "hole_season_str": season_str(ss + 1), "mode": "offseason",
                          "anchor": nm.get(anchor.player_id), "anchor_minutes": round(anchor.minutes),
                          "replacement_acquired": len(incoming) > 0,
                          "replacement": nm.get(incoming.iloc[0].player_id) if len(incoming) else None,
                          "team_id": tid})
        # midseason departure: this team's anchor left DURING ss
        if (tid, ss) in mid_depart and mid_depart[(tid, ss)] == anchor.player_id:
            crows.append({"team": anchor.team_abbreviation, "hole_season": ss,
                          "hole_season_str": season_str(ss), "mode": "midseason",
                          "anchor": nm.get(anchor.player_id), "anchor_minutes": round(anchor.minutes),
                          "replacement_acquired": None, "replacement": None, "team_id": tid})
    # Curated midseason seeds the auto-detector cannot reach: the departed
    # anchor did not play for his new team that season (Capela, injured post-
    # trade) or the season-total anchor became the replacement (Allen->Jordan).
    # Logged as curated, not auto-detected.
    curated = [
        {"team": "HOU", "hole_season": 2019, "hole_season_str": "2019-20", "mode": "midseason_curated",
         "anchor": "Clint Capela", "anchor_minutes": None, "replacement_acquired": False,
         "replacement": None, "team_id": 1610612745},
        {"team": "BKN", "hole_season": 2020, "hole_season_str": "2020-21", "mode": "midseason_curated",
         "anchor": "Jarrett Allen", "anchor_minutes": None, "replacement_acquired": False,
         "replacement": None, "team_id": 1610612751},
        {"team": "LAL", "hole_season": 2024, "hole_season_str": "2024-25", "mode": "midseason_curated",
         "anchor": "Anthony Davis", "anchor_minutes": None, "replacement_acquired": False,
         "replacement": None, "team_id": 1610612747},
    ]
    scenC = pd.concat([pd.DataFrame(crows), pd.DataFrame(curated)], ignore_index=True)
    scenC = scenC.drop_duplicates(["team_id", "hole_season", "mode"])
    scenC = scenC[scenC.hole_season >= 2010].sort_values(["hole_season", "team"]).reset_index(drop=True)
    scenC.to_parquet(DATA / "refclass_C.parquet", index=False)
    print(f"Scenario C class size: {len(scenC)}")

    # seeds: (team, hole_season_start, anchor). Capela/Allen were MIDSEASON
    # departures, so their hole_season is the departure season itself.
    seedsC = [("HOU", 2019, "Capela"), ("BKN", 2020, "Allen"), ("UTA", 2022, "Gobert"),
              ("LAL", 2024, "Davis"), ("MIL", 2025, "Lopez")]
    print("\nSEED RECONCILIATION (Scenario C):")
    for team, hole, anchor in seedsC:
        m = scenC[(scenC.team == team) & (scenC.hole_season == hole)]
        if len(m):
            r = m.iloc[0]
            rep = f", replacement={r['replacement']}" if r["replacement"] else ""
            print(f"  {team} {season_str(hole)} post-{anchor}: IN "
                  f"(mode={r['mode']}, anchor={r['anchor']}{rep})")
        else:
            print(f"  {team} {season_str(hole)} post-{anchor}: OUT (investigate)")


if __name__ == "__main__":
    main()

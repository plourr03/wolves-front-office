"""Phase 0 Step 5: rename-map parse test + lookup-level seed resolution."""
import sys
from pathlib import Path

REPO = Path(r"C:\Users\bobby\playground\wolves-front-office")
sys.path.insert(0, str(REPO / "postmortem"))
from lib.db import query  # noqa: E402
import pandas as pd  # noqa: E402
pd.set_option("display.width", 220)
pd.set_option("display.max_rows", 200)


def hdr(s):
    print("\n" + "=" * 78)
    print(s)
    print("=" * 78)


def explain(label, sql):
    try:
        query("EXPLAIN " + sql)
        print(f"  PARSE OK   {label}")
    except Exception as e:
        print(f"  PARSE FAIL {label}: {type(e).__name__}: {str(e).splitlines()[0]}")


hdr("nba_games rebounding columns (for reliability-curve query mapping)")
print(query("""
    SELECT column_name FROM information_schema.columns
    WHERE table_schema='nba' AND table_name='nba_games'
      AND (column_name ILIKE '%%reb%%' OR column_name ILIKE '%%drb%%'
           OR column_name ILIKE '%%orb%%')
    ORDER BY column_name
""").to_string(index=False))

hdr("PARSE TESTS on section 7 queries, real schema")

# Q1: reliability curve, team DRB. team_game -> nba_games.
# nba_games has dreb (own def reb) but NOT opponent oreb on the same row.
# Opp ORB requires the opponent's row. So the placeholder query's `opp_orb`
# has no direct column; it needs a self-join on game_id to the other team.
explain("Q1 team-DRB reliability (naive, opp_orb as column)", """
    SELECT team_id, season_id, game_id, dreb, opp_orb
    FROM nba.nba_games
""")
explain("Q1 team-DRB reliability (mapped: opp reb via self-join)", """
    WITH ordered AS (
      SELECT g.team_id, g.season_id, g.game_id, g.dreb AS drb, o.oreb AS opp_orb,
             ROW_NUMBER() OVER (PARTITION BY g.team_id, g.season_id
                                ORDER BY g.game_date) AS rn
      FROM nba.nba_games g
      JOIN nba.nba_games o
        ON o.game_id = g.game_id AND o.team_id <> g.team_id
      WHERE RIGHT(g.season_id::text,4)::int BETWEEN 2014 AND 2025
    )
    SELECT team_id, season_id, COUNT(*) FROM ordered
    WHERE rn <= 25 GROUP BY 1,2
""")

# Q3: Scenario A extraction. player_season -> nba_player_season_bio, usg scale
# fixed, minutes derived, position via nba_player_bio, honors BLOCKED.
explain("Q3 Scenario A WITHOUT honors (player_season + position + usg fixed)", """
    SELECT s1.player_id AS arriving, s1.season_year, s1.team_id AS new_team,
           s0.team_id AS old_team, s0.usg_pct AS prior_usg
    FROM nba.nba_player_season_bio s1
    JOIN nba.nba_player_season_bio s0
      ON s0.player_id = s1.player_id
     AND s0.season_year = (LEFT(s1.season_year,4)::int - 1)::text
                          || '-' || RIGHT(LPAD(((RIGHT(s1.season_year,2)::int - 1 + 100) %% 100)::text,2,'0'),2)
    JOIN nba.nba_player_bio pb ON pb.player_id = s1.player_id
    WHERE s1.team_id <> s0.team_id
      AND s0.usg_pct >= 0.28
      AND s1.season_type = 'Regular Season' AND s0.season_type = 'Regular Season'
      AND pb.position IN ('Guard','Guard-Forward','Forward-Guard')
""")
explain("Q3 Scenario A WITH honors (references nonexistent nba.honors)", """
    SELECT s1.player_id FROM nba.nba_player_season_bio s1
    WHERE EXISTS (SELECT 1 FROM nba.honors h WHERE h.player_id = s1.player_id)
""")

# Q4: AVAIL-PACE. Redefined in 4b; the posterior-table version is retired.
explain("Q4 AVAIL-PACE original (availability_posterior tables)", """
    SELECT p.gp FROM nba.availability_posterior p
""")
# The redefined warehouse-only version:
explain("Q4 AVAIL-PACE redefined (games-through-N, warehouse only)", """
    SELECT COUNT(*) AS gp
    FROM nba.nba_player_stats ps
    JOIN nba.nba_games g ON g.game_id = ps.game_id AND g.team_id = ps.team_id
    WHERE ps.player_id = 1630163 AND ps.minutes_played > 0
""")

hdr("LOOKUP-LEVEL SEED RESOLUTION (Scenario A core class)")
print("Each seed must resolve: arriving player changed teams INTO new_team in season S.")
seeds = [
    ("Damian Lillard", "2023-24", "Milwaukee"),
    ("Kyrie Irving", "2022-23", "Dallas"),
    ("James Harden", "2020-21", "Brooklyn"),
    ("James Harden", "2021-22", "Philadelphia"),
    ("James Harden", "2023-24", "LA Clippers"),
    ("Russell Westbrook", "2021-22", "LA Lakers"),
    ("Chris Paul", "2020-21", "Phoenix"),
    ("Donovan Mitchell", "2022-23", "Cleveland"),
    ("Bradley Beal", "2023-24", "Phoenix"),
    ("De'Aaron Fox", "2024-25", "San Antonio"),
    ("Luka Doncic", "2024-25", "LA Lakers"),
    ("Dejounte Murray", "2024-25", "New Orleans"),
]
rows = []
for name, seas, team in seeds:
    r = query("""
        SELECT player_name, season_year, team_abbreviation, gp, usg_pct
        FROM nba.nba_player_season_bio
        WHERE player_name = %s AND season_year = %s AND season_type='Regular Season'
        ORDER BY gp DESC
    """, (name, seas))
    if len(r):
        rr = r.iloc[0]
        rows.append((name, seas, team, rr.team_abbreviation, int(rr.gp), float(rr.usg_pct), "RESOLVED"))
    else:
        rows.append((name, seas, team, "-", 0, 0.0, "*** NOT FOUND ***"))
print(pd.DataFrame(rows, columns=["arriving","season","exp_team","got_team","gp","usg","status"]).to_string(index=False))

hdr("LOOKUP-LEVEL SEED RESOLUTION (Scenario B availability class)")
seedsB = ["Ben Simmons","John Wall","Kyrie Irving","Zach LaVine","Kristaps Porzingis",
          "Lonzo Ball","Kawhi Leonard","Paul George","Khris Middleton"]
rowsB = []
for name in seedsB:
    r = query("""
        SELECT MIN(season_year) AS first_s, MAX(season_year) AS last_s, COUNT(*) AS seasons
        FROM nba.nba_player_season_bio
        WHERE player_name = %s AND season_type='Regular Season'
    """, (name,))
    rr = r.iloc[0]
    rowsB.append((name, rr.first_s, rr.last_s, int(rr.seasons),
                  "RESOLVED" if rr.seasons else "*** NOT FOUND ***"))
print(pd.DataFrame(rowsB, columns=["player","first_season","last_season","n_seasons","status"]).to_string(index=False))

"""Spurs vs Wolves 2025-26 LAFI comparison.

Question: the 2D quadrant chart places SAS and MIN both in Q4. Are they actually
architecturally similar, or does the 2D view (C1, C2 only) mislead?
"""
import os
from pathlib import Path

import pandas as pd
import psycopg2
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")


def section(t):
    print(f"\n{'='*72}\n{t}\n{'='*72}")


# ---------------------------------------------------------------------------
# 1. Full LAFI profiles from the canonical composite output
# ---------------------------------------------------------------------------
comp = pd.read_csv(ROOT / "outputs/tables/q0a_lafi/lafi_composite_5component.csv")
comp = comp[comp.season_type == "Regular Season"]

def profile(team, year):
    r = comp[(comp.team_abbreviation == team) & (comp.season_start_year == year)]
    if r.empty:
        return None
    r = r.iloc[0]
    return {
        "C1_ball_stickiness": round(r.C1_ball_stickiness_pct, 1),
        "C2_movement_death": round(r.C2_movement_death_pct, 1),
        "C3_isolation_reliance": round(r.C3_isolation_reliance_pct, 1),
        "C4_action_poverty": round(r.C4_action_poverty_pct, 1),
        "C5_shot_quality_decay": round(r.C5_shot_quality_decay_pct, 1),
        "Full_LAFI": round(r.lafi_pct, 1),
        "Sharp_LAFI": round(r.sharp_lafi_pct, 1),
    }

sas = profile("SAS", 2025)
mins = profile("MIN", 2025)

section("1. Full LAFI profile: Spurs vs Wolves, 2025-26 regular season")
metrics = ["C1_ball_stickiness", "C2_movement_death", "C3_isolation_reliance",
           "C4_action_poverty", "C5_shot_quality_decay", "Full_LAFI", "Sharp_LAFI"]
print(f"{'Metric':<24}{'Wolves':>10}{'Spurs':>10}{'Gap (W-S)':>12}")
print("-" * 56)
for m in metrics:
    w, s = mins[m], sas[m]
    print(f"{m:<24}{w:>10}{s:>10}{w - s:>12.1f}")

# ---------------------------------------------------------------------------
# 2. Cohort filter check (Q0C definition)
# ---------------------------------------------------------------------------
section("2. Q0C cohort filter: Sharp LAFI >= 80 AND C1 < 50 AND C2 > 50")
def cohort_check(name, p):
    in_cohort = p["Sharp_LAFI"] >= 80 and p["C1_ball_stickiness"] < 50 and p["C2_movement_death"] > 50
    in_q4 = p["C1_ball_stickiness"] < 50 and p["C2_movement_death"] > 50
    print(f"{name}: Sharp LAFI {p['Sharp_LAFI']} | C1 {p['C1_ball_stickiness']} | C2 {p['C2_movement_death']}")
    print(f"   In Q4 quadrant (2D cut)? {in_q4}")
    print(f"   In Q0C cohort (adds Sharp>=80)? {in_cohort}")
cohort_check("Wolves 25-26", mins)
cohort_check("Spurs 25-26", sas)

# ---------------------------------------------------------------------------
# 3. Which quadrant does each chart anchor actually plot in?
# ---------------------------------------------------------------------------
section("3. Chart anchors: actual quadrant placement on the 2D (C1, C2) view")
anchors = [("SAS", 2025), ("OKC", 2024), ("GSW", 2015),
           ("DEN", 2022), ("HOU", 2017), ("DAL", 2022)]
for team, year in anchors:
    p = profile(team, year)
    if p is None:
        print(f"  {team} {year}: NOT FOUND")
        continue
    c1, c2 = p["C1_ball_stickiness"], p["C2_movement_death"]
    if c1 < 50 and c2 < 50:
        q = "Q1 Designed"
    elif c1 >= 50 and c2 < 50:
        q = "Q2 Star-anchored"
    elif c1 >= 50 and c2 >= 50:
        q = "Q3 Single-star pickup"
    else:
        q = "Q4 Distributed pickup"
    print(f"  {team} '{year%100:02d}-{(year+1)%100:02d}: C1={c1}, C2={c2}  ->  {q}"
          f"  (Sharp LAFI {p['Sharp_LAFI']}, Full LAFI {p['Full_LAFI']})")

# ---------------------------------------------------------------------------
# 4. Any cohort-profile team that reached the conference finals? (verify Q0C)
# ---------------------------------------------------------------------------
section("4. Cohort-profile teams (Sharp>=80, C1<50, C2>50) across the LAFI universe")
cohort = comp[(comp.sharp_lafi_pct >= 80) &
              (comp.C1_ball_stickiness_pct < 50) &
              (comp.C2_movement_death_pct > 50)]
print(f"Total teams matching the cohort profile: {len(cohort)}")
for r in cohort.itertuples():
    print(f"  {r.team_abbreviation} {r.season_start_year}-{(r.season_start_year+1)%100:02d}"
          f"  Sharp LAFI {r.sharp_lafi_pct:.1f}")

# ---------------------------------------------------------------------------
# 5. Offensive context from the warehouse
# ---------------------------------------------------------------------------
section("5. Offensive context: Spurs vs Wolves, 2025-26 regular season")
conn = psycopg2.connect(
    host=os.environ["POSTGRES_HOST"], port=os.environ["POSTGRES_PORT"],
    dbname=os.environ["POSTGRES_DB"], user=os.environ["POSTGRES_USER"],
    password=os.environ["POSTGRES_PASSWORD"],
)
cur = conn.cursor()
cur.execute("SET search_path TO nba")
cur.execute(
    """
    WITH team_adv AS (
      SELECT g.team_abbreviation,
             AVG(a.offensive_rating) AS ortg,
             AVG(a.true_shooting_percentage) AS ts,
             AVG(a.effective_field_goal_percentage) AS efg,
             AVG(a.assist_percentage) AS ast_pct,
             AVG(a.pace) AS pace
      FROM nba_games g
      JOIN nba_team_advanced_stats a USING (game_id, team_id)
      WHERE g.season_type = 'Regular Season'
        AND g.game_date BETWEEN '2025-09-01' AND '2026-06-30'
      GROUP BY g.team_abbreviation
    ),
    team_box AS (
      SELECT team_abbreviation,
             SUM(fg3a)::numeric / NULLIF(SUM(fga), 0) AS fg3a_rate,
             SUM(ast)::numeric / NULLIF(SUM(fgm), 0) AS ast_per_fgm
      FROM nba_games
      WHERE season_type = 'Regular Season'
        AND game_date BETWEEN '2025-09-01' AND '2026-06-30'
      GROUP BY team_abbreviation
    )
    SELECT t.team_abbreviation,
           ROUND(t.ortg::numeric,1) AS ortg,
           RANK() OVER (ORDER BY t.ortg DESC) AS ortg_rank,
           ROUND((t.ts*100)::numeric,1) AS ts_pct,
           ROUND((t.efg*100)::numeric,1) AS efg_pct,
           ROUND((b.fg3a_rate*100)::numeric,1) AS fg3a_rate,
           ROUND((b.ast_per_fgm*100)::numeric,1) AS ast_per_100_fgm,
           ROUND(t.ast_pct::numeric,1) AS ast_pct
    FROM team_adv t JOIN team_box b USING (team_abbreviation)
    WHERE t.team_abbreviation IN ('SAS','MIN')
    ORDER BY t.team_abbreviation
    """
)
cols = [d[0] for d in cur.description]
for row in cur.fetchall():
    print(dict(zip(cols, row)))

cur.close()
conn.close()

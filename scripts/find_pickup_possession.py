"""Reconstruct candidate pickup-ball possessions for the article."""
import os
import re
from pathlib import Path
import psycopg2
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")
conn = psycopg2.connect(
    host=os.environ["POSTGRES_HOST"],
    port=os.environ["POSTGRES_PORT"],
    dbname=os.environ["POSTGRES_DB"],
    user=os.environ["POSTGRES_USER"],
    password=os.environ["POSTGRES_PASSWORD"],
)
cur = conn.cursor()
cur.execute("SET search_path TO nba")

CLOCK_PATTERN = re.compile(r"PT(\d+)M([\d\.]+)S")


def clock_to_seconds(clock_str):
    if not clock_str:
        return None
    m = CLOCK_PATTERN.match(clock_str)
    if not m:
        return None
    return int(m.group(1)) * 60 + float(m.group(2))


def fmt(s):
    if s is None:
        return "?"
    return f"{int(s // 60)}:{s % 60:05.2f}"


# All MIN missed FGs in the 4 SAS series losses, with description text and
# game clock. Filter to shots that are mid-range pullups or contested 3s.
LOSSES = ['0042500232', '0042500233', '0042500235', '0042500236']

def show_possession_around(game_id, period, target_clock_seconds, window=24):
    """Print all events in this period whose clock_seconds_remaining is within
    [target - window, target + window]."""
    cur.execute(
        """
        SELECT action_number, period, clock, team_tricode, player_name,
               description, action_type, sub_type
        FROM nba_play_by_play
        WHERE game_id = %s AND period = %s
        ORDER BY action_number ASC
        """,
        (game_id, period),
    )
    events = cur.fetchall()
    in_range = []
    for ev in events:
        cs = clock_to_seconds(ev[2])
        if cs is None:
            continue
        if abs(cs - target_clock_seconds) <= window:
            in_range.append((cs, ev))
    in_range.sort(key=lambda x: -x[0])  # chronological: high clock first
    for cs, ev in in_range:
        an, period, clock, team, player, desc, atype, stype = ev
        print(f"  [{fmt(cs)}] {team or '-'} {player or '-'}: {atype}/{stype} -- {desc}")


# Find the worst-looking iso-style misses in losses. Use description text
# to identify pullups, fadeaways, stepbacks, turnarounds, running pullups.
ISO_KEYWORDS = ["pullup", "fadeaway", "stepback", "step back", "turnaround", "running"]

cur.execute(
    """
    SELECT game_id, action_number, period, clock, team_tricode, player_name,
           description, shot_distance, shot_value
    FROM nba_play_by_play
    WHERE game_id = ANY(%s)
      AND team_tricode = 'MIN'
      AND is_field_goal = 1
      AND shot_result = 'Missed'
      AND (description ILIKE '%%pullup%%' OR description ILIKE '%%fadeaway%%' OR
           description ILIKE '%%stepback%%' OR description ILIKE '%%step back%%' OR
           description ILIKE '%%turnaround%%' OR description ILIKE '%%running%%')
    ORDER BY game_id, period, action_number
    """,
    (LOSSES,),
)
iso_misses = cur.fetchall()
print(f"\n{len(iso_misses)} iso-style missed FGs in 4 SAS series losses:\n")
for row in iso_misses:
    game_id, an, period, clock, team, player, desc, dist, sval = row
    cs = clock_to_seconds(clock)
    print(f"  G{game_id[-1]} P{period} {fmt(cs)} | {player} {dist}ft ({sval}pt): {desc}")

# Look at the lead-in (16 seconds prior) for the top candidates.
print("\n" + "="*70)
print("LEAD-IN CONTEXT (16s window) for star-player iso misses")
print("="*70)

star_misses = [r for r in iso_misses if r[5] in ("Anthony Edwards", "Julius Randle", "Naz Reid", "Jaden McDaniels")]
for r in star_misses[:12]:
    game_id, an, period, clock, team, player, desc, dist, sval = r
    cs = clock_to_seconds(clock)
    print(f"\n>>> G{game_id[-1]} P{period} {fmt(cs)} | {player}: {desc}")
    show_possession_around(game_id, period, cs, window=18)

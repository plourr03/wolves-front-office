"""Curate voted All-Star starters lost to the DNP limitation (Bobby's directive
2026-07-17). My roster-based scrape captures who STARTED the game, so fan/media
-voted starters who were injured and replaced are absent or mis-flagged. This
upserts them as is_starter=True, marked source='curated_voted_starter_dnp',
per house convention (logged curation).

Voted-starter-DNP cases, each verified against the season's Wikipedia All-Star
page (voted starters who did not play due to injury; COVID/health-and-safety
absences excluded). Years with injured voted starters were checked; all other
window years had every voted starter play, so the roster scrape equals the
voted-starter set there.
"""
import sys
from pathlib import Path
import unicodedata as ud
import pandas as pd

REPO = Path(r"C:\Users\bobby\playground\wolves-front-office")
DATA = REPO / "all-for-one" / "tripwire-backtest" / "data"
sys.path.insert(0, str(REPO / "postmortem"))
from lib.db import query  # noqa: E402


def fold(s):
    return "".join(c for c in ud.normalize("NFKD", str(s)) if not ud.combining(c)).lower()


# (player, season_start) verified voted-starter-DNP. season_start = game year - 1.
CASES = [
    ("Yao Ming", 2010),
    ("Kobe Bryant", 2013),
    ("Kobe Bryant", 2014), ("Anthony Davis", 2014), ("Blake Griffin", 2014),
    ("Anthony Davis", 2020), ("Kevin Durant", 2020),
    ("Stephen Curry", 2022), ("Kevin Durant", 2022), ("Zion Williamson", 2022),
    ("Joel Embiid", 2023),
    ("Giannis Antetokounmpo", 2024), ("LeBron James", 2024),
    ("Giannis Antetokounmpo", 2025), ("Stephen Curry", 2025), ("Shai Gilgeous-Alexander", 2025),
]

h = pd.read_parquet(DATA / "honors.parquet")
if "source" not in h.columns:
    h["source"] = "bref_scrape"
bio = query("SELECT player_id, first_name||' '||last_name nm FROM nba.nba_player_bio")
bio["f"] = bio.nm.map(fold)

added, flipped, already = 0, 0, 0
new_rows = []
for nm, ss in CASES:
    m = bio[bio.f == fold(nm)]
    if not len(m):
        print(f"  WARN no bio for {nm}")
        continue
    pid = int(m.iloc[0].player_id)
    mask = (h.nba_player_id == pid) & (h.season_start == ss) & (h.award == "ALL_STAR")
    if mask.any():
        if not h.loc[mask, "is_starter"].any():
            h.loc[mask, "is_starter"] = True
            h.loc[mask, "source"] = "curated_voted_starter_dnp"
            flipped += 1
        else:
            already += 1
    else:
        new_rows.append({"season_start": ss, "season": f"{ss}-{str(ss+1)[-2:]}",
                         "award": "ALL_STAR", "tier": None, "is_starter": True,
                         "bref_name": nm, "nba_player_id": pid, "resolved": True,
                         "source": "curated_voted_starter_dnp"})
        added += 1

h2 = pd.concat([h, pd.DataFrame(new_rows)], ignore_index=True) if new_rows else h
h2.to_parquet(DATA / "honors.parquet", index=False)
print(f"curated voted-starter-DNP: {added} added, {flipped} flipped reserve->starter, "
      f"{already} already correct  (total {added + flipped} corrected)")
print(f"honors.parquet now {len(h2)} rows, "
      f"{int((h2.source=='curated_voted_starter_dnp').sum())} curated")

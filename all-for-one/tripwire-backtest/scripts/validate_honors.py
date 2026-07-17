"""Validate the honors ingest against the Scenario A seed incumbents.

For each seed case, the incumbent must qualify under the spec's rule:
"made All-NBA in either of the two prior seasons OR was an All-Star starter"
in that window. Reports the qualifying award per incumbent. Cases that
qualify ONLY under a loosened rule (All-Star reserve) are the documented
incumbent-filter sensitivity, reported not forced.
"""
import sys
import re
import unicodedata
from pathlib import Path
import pandas as pd

REPO = Path(r"C:\Users\bobby\playground\wolves-front-office")
sys.path.insert(0, str(REPO / "postmortem"))
from lib.db import query  # noqa: E402


def _fold(s: str) -> str:
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z ]", "", s.lower()).strip()

honors = pd.read_parquet(REPO / "all-for-one" / "tripwire-backtest" / "data" / "honors.parquet")

# seed case -> (arrival season_start, [incumbent names])
SEEDS = [
    ("Lillard to MIL 2023-24", 2023, ["Giannis Antetokounmpo"]),
    ("Irving to DAL 2022-23", 2022, ["Luka Doncic"]),
    ("Harden to BKN 2020-21", 2020, ["Kevin Durant"]),
    ("Harden to PHI 2021-22", 2021, ["Joel Embiid"]),
    ("Harden to LAC 2023-24", 2023, ["Kawhi Leonard", "Paul George"]),
    ("Westbrook to LAL 2021-22", 2021, ["LeBron James", "Anthony Davis"]),
    ("Paul to PHX 2020-21", 2020, ["Devin Booker"]),
    ("Mitchell to CLE 2022-23", 2022, ["Darius Garland"]),
    ("Beal to PHX 2023-24", 2023, ["Devin Booker", "Kevin Durant"]),
    ("Fox to SAS 2024-25", 2024, ["Victor Wembanyama"]),
    ("Doncic to LAL 2024-25", 2024, ["LeBron James"]),
    ("Murray to NOP 2024-25", 2024, ["Dejounte Murray"]),  # NOTE: incumbent is Williamson
]
# fix: Murray->NOP incumbent is Williamson (Murray is the ARRIVING player)
SEEDS[-1] = ("Murray to NOP 2024-25 (inc Williamson)", 2024, ["Zion Williamson"])

# resolve incumbent names to player_id (player_id-only join thereafter)
bio = query("""
    SELECT player_id, first_name || ' ' || last_name AS nm FROM nba.nba_player_bio
""")
bio["fold"] = bio.nm.map(_fold)
name2id = {}
for nm in set(n for _, _, ns in SEEDS for n in ns):
    m = bio[bio.fold == _fold(nm)]
    name2id[nm] = int(m.iloc[0].player_id) if len(m) else None

hon_by_pid = honors.groupby("nba_player_id")

print(f"{'CASE':40s} {'INCUMBENT':22s} {'WINDOW':11s} QUALIFIES")
print("-" * 100)
rows = []
for case, arr, incs in SEEDS:
    w = {arr - 1, arr - 2}
    for inc in incs:
        pid = name2id.get(inc)
        quals = []
        if pid is not None and pid in hon_by_pid.groups:
            h = hon_by_pid.get_group(pid)
            hw = h[h.season_start.isin(w)]
            if (hw.award == "ALL_NBA").any():
                tiers = sorted(hw[hw.award == "ALL_NBA"].tier.dropna().astype(int).unique())
                quals.append(f"All-NBA{tiers}")
            starters = hw[(hw.award == "ALL_STAR") & (hw.is_starter == True)]
            if len(starters):
                quals.append("AS-starter")
            reserves = hw[(hw.award == "ALL_STAR") & (hw.is_starter == False)]
            if len(reserves) and not quals:
                quals.append("(AS-reserve ONLY)")
        status = ", ".join(quals) if quals else "*** NONE ***"
        wtxt = f"{min(w)}&{max(w)}"
        print(f"{case:40s} {inc:22s} {wtxt:11s} {status}")
        rows.append({"case": case, "incumbent": inc, "pid": pid, "quals": status})

df = pd.DataFrame(rows)
strict_ok = df[~df.quals.str.contains("NONE|reserve ONLY")]
sens = df[df.quals.str.contains("reserve ONLY")]
none = df[df.quals.str.contains("NONE")]
print("\nSUMMARY")
print(f"  incumbents qualifying under STRICT rule (All-NBA or AS-starter): {len(strict_ok)}/{len(df)}")
print(f"  qualify only under LOOSENED rule (AS-reserve): {len(sens)}  <- documented sensitivity")
if len(sens):
    print("   ", ", ".join(f"{r.incumbent} ({r.case.split(' 20')[0]})" for _, r in sens.iterrows()))
print(f"  qualify under NEITHER: {len(none)}")
if len(none):
    print("   ", ", ".join(f"{r.incumbent} ({r.case})" for _, r in none.iterrows()))
# a seed CASE resolves if AT LEAST ONE incumbent qualifies (strict or loosened)
case_ok = df.groupby("case").apply(
    lambda g: (~g.quals.str.contains("NONE")).any(), include_groups=False)
print(f"\n  seed CASES with >=1 qualifying incumbent (any rule): {case_ok.sum()}/{len(case_ok)}")
if (~case_ok).any():
    print("    cases with NO qualifying incumbent:", list(case_ok[~case_ok].index))

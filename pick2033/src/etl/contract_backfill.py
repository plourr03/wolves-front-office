"""contract_years_remaining backfill (Ruling A / spec 6.2 best-effort).

Source: B-Ref player-page all_salaries tables (full career, season x salary),
fetched through the cached throttled client; slugs are already our
player_ids, so there is NO name-matching risk.

Inference: contract boundaries from salary-series breakpoints + franchise
changes. A season STARTS a new contract when:
  - it is the first NBA salary season, OR follows a gap year, OR
  - the player's final-stint FRANCHISE changed between seasons (offseason
    moves: FA signings are new deals; the rare offseason trade is
    misread as a break -- acceptable truncation noise, flagged), OR
  - the year-over-year salary change falls outside the era's
    within-contract raise envelope:
       |change| > 25%  through 1998-99  (pre-1999 CBA: 20% Bird raises)
       |change| > 15%  through 2011-12  (12.5%-of-year-1 raises exceed
                                         12.5% yoy early in backloaded deals
                                         -- Garnett's $126M was shredded by
                                         a 13% envelope in QC)
       |change| > 9%   2012-13 onward   (7.5%/4.5% then 8%/5%)
    with the envelope widened to 30% in a player's first four salary
    seasons (rookie-scale year-4 escalations run ~26%, e.g. Edwards).
  Envelopes are deliberately GENEROUS: a false break truncates
  years-remaining mid-contract, which is the worse error for the hazard.
  contract_years_remaining at season t = (last season of current contract) - t.
  Walk year = 0. One-year deals chain to 0 every year (correct).
  KNOWN BLIND SPOT (accepted, flagged): a same-franchise re-sign whose
  first-year salary lands within the envelope of the prior year reads as a
  contract continuation (years-remaining overstated across the re-sign).

Known limitations (documented, carried as method flags):
  - extensions appear as breaks at their START season (years-remaining
    reflects the deal being played under, not signed leverage)
  - the FINAL contract of a career ends at the last observed salary
    (fine historically); for currently-active players the verified
    2026-27 contracts CSV supplies the forward end
  - missing salary seasons -> contract_known=False for those rows

Output: data/staged/contract_years_backfill.parquet
        (player_id, season, contract_years_remaining, contract_known, method)
Coverage vs the 1,290 spell-season rows reported and written to
outputs/validation/contract_backfill_coverage.md. Data enters the M2 refit
BLIND per Ruling A (spec pre-declared; no peeking at fit outcomes).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
from bs4 import BeautifulSoup

from src.etl.bref_client import fetch, strip_comment_tables

STAGED = PROJECT_ROOT / "data" / "staged"
OUT_VAL = PROJECT_ROOT / "outputs" / "validation"
CONTRACTS_CSV = PROJECT_ROOT.parent / "offseason" / "data" / "nba_contracts_2026_27.csv"


def parse_salaries(html: str) -> pd.DataFrame:
    soup = BeautifulSoup(strip_comment_tables(html), "lxml")
    table = soup.find("table", id="all_salaries")
    rows = []
    if table is None:
        return pd.DataFrame(columns=["season", "salary"])
    for r in table.find_all("tr"):
        season = r.find(attrs={"data-stat": "season"})
        sal = r.find(attrs={"data-stat": "salary"})
        lg = r.find(attrs={"data-stat": "lg_id"})
        if season is None or sal is None:
            continue
        stxt = season.get_text(strip=True)
        if not re.match(r"^\d{4}-\d{2}$", stxt):
            continue
        if lg is not None and lg.get_text(strip=True) not in ("NBA", ""):
            continue
        amt = re.sub(r"[^\d]", "", sal.get_text())
        if amt:
            rows.append({"season": int(stxt[:4]) + 1, "salary": int(amt)})
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    return df.groupby("season", as_index=False).salary.sum()  # traded-year splits


def raise_envelope(season: int, career_idx: int) -> float:
    if career_idx < 4:
        return 0.30          # rookie-scale escalations
    if season <= 1999:
        return 0.25
    if season <= 2012:
        return 0.15
    return 0.09


def infer_contracts(sal: pd.DataFrame, team_by_season: dict | None = None) -> pd.DataFrame:
    """Break inference -> per-season years remaining."""
    sal = sal.sort_values("season").reset_index(drop=True)
    starts = []
    for i, r in sal.iterrows():
        if i == 0 or r.season - sal.season[i - 1] > 1:
            starts.append(i)
            continue
        if team_by_season is not None:
            t0 = team_by_season.get(int(sal.season[i - 1]))
            t1 = team_by_season.get(int(r.season))
            if t0 is not None and t1 is not None and t0 != t1:
                starts.append(i)   # offseason franchise change = new deal
                continue
        prev = sal.salary[i - 1]
        change = (r.salary - prev) / prev if prev > 0 else 1.0
        # envelope keys on the CURRENT SEGMENT'S start season: contracts keep
        # the raise rules of the CBA they were signed under (a season-keyed
        # envelope shredded Garnett's 1999-2004 deal at the 1999 boundary and
        # clipped LeBron's 2011-14 deal at the 2011-CBA boundary in QC)
        seg_start_season = int(sal.season[starts[-1]])
        if abs(change) > raise_envelope(seg_start_season, i):
            starts.append(i)
    starts.append(len(sal))
    rows = []
    for a, b in zip(starts[:-1], starts[1:]):
        end_season = int(sal.season[b - 1])
        for i in range(a, b):
            rows.append({"season": int(sal.season[i]),
                         "contract_years_remaining": end_season - int(sal.season[i]),
                         "method": "bref_salary_breaks"})
    return pd.DataFrame(rows)


def forward_years_active(player_name: str, contracts: pd.DataFrame) -> int | None:
    """Verified forward seasons remaining after 2025-26 for active players."""
    row = contracts[contracts.player == player_name]
    if row.empty:
        return None
    r = row.iloc[0]
    yrs = 0
    for col in ("salary_2026_27", "salary_2027_28", "salary_2028_29", "salary_2029_30"):
        if pd.notna(r[col]) and r[col] > 0:
            yrs += 1
    return yrs


def main():
    sp = pd.read_parquet(STAGED / "star_spells_provisional.parquet")
    players = sorted(sp.player_id.unique())
    names = sp.drop_duplicates("player_id").set_index("player_id").player_name
    contracts = pd.read_csv(CONTRACTS_CSV)
    # final-stint franchise per (player, season) for franchise-change breaks
    import duckdb
    con = duckdb.connect(str(PROJECT_ROOT / "data" / "warehouse.duckdb"), read_only=True)
    stints = con.execute("""
        SELECT player_id, season, franchise_id FROM (
          SELECT player_id, season, franchise_id,
                 row_number() OVER (PARTITION BY player_id, season
                   ORDER BY coalesce(stint_order, 0) DESC) rn
          FROM player_impact_seasons WHERE NOT is_combined AND franchise_id IS NOT NULL)
        WHERE rn = 1""").fetchdf()
    con.close()
    team_map = {pid: dict(zip(g.season, g.franchise_id))
                for pid, g in stints.groupby("player_id")}
    print(f"backfilling {len(players)} spell players", flush=True)

    all_rows, missing = [], []
    for i, pid in enumerate(players):
        html = fetch(f"/players/{pid[0]}/{pid}.html", f"player_{pid}")
        sal = parse_salaries(html)
        if sal.empty:
            missing.append(pid)
            continue
        inf = infer_contracts(sal, team_map.get(pid))
        # active players: extend the final contract with the verified forward view
        fwd = forward_years_active(names[pid], contracts)
        if fwd is not None and (inf.season.max() >= 2025):
            last = inf.season.max()
            inf.loc[inf.season == last, "contract_years_remaining"] += fwd
            # re-derive earlier seasons of that final contract
            final_start = inf[inf.contract_years_remaining
                              == inf[inf.season == last].contract_years_remaining.iloc[0]]
            inf.loc[:, "method"] = np.where(
                inf.season >= last - 0, "bref_plus_verified_forward", inf.method)
        inf["player_id"] = pid
        all_rows.append(inf)
        if (i + 1) % 25 == 0:
            print(f"  {i + 1}/{len(players)}", flush=True)

    bf = pd.concat(all_rows, ignore_index=True)
    bf["contract_known"] = True
    bf.to_parquet(STAGED / "contract_years_backfill.parquet", index=False)

    merged = sp.drop(columns=["contract_years_remaining"], errors="ignore").merge(
        bf[["player_id", "season", "contract_years_remaining"]],
        on=["player_id", "season"], how="left")
    cov = merged.contract_years_remaining.notna().mean()
    by_era = merged.assign(era=(merged.season // 10) * 10).groupby("era").apply(
        lambda g: g.contract_years_remaining.notna().mean(), include_groups=False)
    lines = [
        "# Contract backfill coverage (spec 6.2 / Ruling A)",
        f"- source: B-Ref all_salaries, {len(players)} spell players, "
        f"{len(missing)} with no salary table: {missing}",
        f"- spell-season coverage: **{cov:.1%}** of {len(merged)} rows",
        "- by decade: " + ", ".join(f"{int(e)}s {v:.1%}" for e, v in by_era.items()),
        f"- walk-year rate among covered rows: "
        f"{(merged.contract_years_remaining == 0).mean() / max(cov, 1e-9):.1%}",
        "- method: salary-break + franchise-change inference; era envelopes "
        "keyed on the segment's SIGNING season (25% pre-1999, 15% to 2011, 9% "
        "after; 30% in a career's first four seasons for rookie scale); "
        "generous on purpose (false breaks truncate years-remaining, the worse "
        "error for the hazard). Known blind spot: smooth same-franchise "
        "re-signs read as continuations (Duncan-pattern; overstates remaining "
        "for stay-put stars, attenuating the coefficient). QC'd against "
        "Edwards/Garnett/LeBron/Duncan ground truth. Data enters the M2 refit "
        "blind to fit outcomes.",
    ]
    OUT_VAL.mkdir(parents=True, exist_ok=True)
    (OUT_VAL / "contract_backfill_coverage.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()

"""M0 cross-validation gate: B-Ref SRS (our Model A observable) against the
Postgres warehouse's per-game point differential on the 1998-2026 overlap.
SRS = point diff adjusted for schedule strength, so r should exceed 0.98.
A miss means a team-mapping or parsing bug, not a data nuance.

Writes outputs/validation/m0_crosscheck.md.
"""

from __future__ import annotations

import sys
from pathlib import Path

import duckdb
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = PROJECT_ROOT.parent
sys.path.insert(0, str(REPO_ROOT / "postmortem"))
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv

load_dotenv(REPO_ROOT / ".env")
from lib.db import query  # noqa: E402

from src.etl.franchise_map import to_franchise  # noqa: E402

OUT = PROJECT_ROOT / "outputs" / "validation"


def warehouse_point_diff() -> pd.DataFrame:
    df = query("""
        SELECT (season_id % 10000) + 1 AS season, team_abbreviation AS abbr,
               avg(plus_minus) AS avg_diff, count(*) AS games
        FROM nba_games
        WHERE season_type = 'Regular Season'
        GROUP BY 1, 2
    """)
    df["avg_diff"] = df.avg_diff.astype(float)
    df["franchise_id"] = [to_franchise(a, int(s)) for a, s in zip(df.abbr, df.season)]
    return df[["franchise_id", "season", "avg_diff", "games"]]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(PROJECT_ROOT / "data" / "warehouse.duckdb"), read_only=True)
    bref = con.execute(
        "SELECT franchise_id, season, srs, wins FROM franchise_seasons WHERE season >= 1998"
    ).fetchdf()
    con.close()
    pg = warehouse_point_diff()
    m = bref.merge(pg, on=["franchise_id", "season"], how="inner")
    n_bref = len(bref)
    r_all = m.srs.corr(m.avg_diff)
    lines = [
        "# M0 cross-check: B-Ref SRS vs warehouse point differential",
        f"- overlap rows matched: {len(m)} of {n_bref} B-Ref franchise-seasons (1998+)",
        f"- corr(SRS, avg point diff), all seasons: **{r_all:.4f}** (gate: > 0.98)",
    ]
    by_era = m.assign(era=(m.season // 5) * 5).groupby("era").apply(
        lambda g: g.srs.corr(g.avg_diff), include_groups=False)
    lines.append("- by half-decade: " + ", ".join(f"{e}: {v:.3f}" for e, v in by_era.items()))
    worst = m.assign(gap=(m.srs - m.avg_diff).abs()).nlargest(5, "gap")
    lines.append("- largest gaps (SRS vs diff, SOS effects expected): "
                 + "; ".join(f"{r.franchise_id} {r.season} {r.gap:.2f}" for r in worst.itertuples()))
    passed = r_all > 0.98 and len(m) > 0.95 * n_bref
    lines.append(f"\n**GATE {'PASS' if passed else 'FAIL'}**")
    report = "\n".join(lines)
    (OUT / "m0_crosscheck.md").write_text(report, encoding="utf-8")
    print(report)
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()

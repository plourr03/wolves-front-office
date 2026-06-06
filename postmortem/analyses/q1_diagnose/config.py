"""Q1 configuration: seasons, output paths, constants.

Sample window: 2014-15 through 2025-26 for the historical playoff-dropoff
norms. Headline comparisons are Wolves 2025-26 RS vs Wolves 2025-26 PO,
with 2024-25 (Randle year 1, conference finals) and 2023-24 (WCF year, the
best-recent-version reference) included as Wolves-specific year-over-year
context.
"""
from __future__ import annotations
from pathlib import Path

# Seasons.
WOLVES_TEAM_ID = 1610612750
CURRENT_SEASON_YEAR = 2025  # 2025-26
WOLVES_REFERENCE_YEARS = [2023, 2024, 2025]  # WCF year, Randle Y1, current

# Historical playoff-dropoff norm: ten complete seasons before the current.
# We exclude the current season (incomplete) and the COVID seasons (per
# project convention from LAFI v1 validation).
HISTORICAL_DROPOFF_YEARS = [2014, 2015, 2016, 2017, 2018, 2021, 2022, 2023, 2024]
# (2019-20 bubble and 2020-21 COVID excluded by default.)

# Garbage-time filter conventions (per project standard).
GARBAGE_MARGIN = 15
GARBAGE_LAST_MIN = 3

# Bootstrap.
BOOTSTRAP_N = 1000
BOOTSTRAP_SEED = 42
CI_LEVEL = 0.95

# Paths.
REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_ROOT = REPO_ROOT / "outputs"
TABLE_DIR = OUTPUT_ROOT / "tables" / "q1_diagnose"
CHART_DIR = OUTPUT_ROOT / "charts" / "q1_diagnose"
FINDINGS_DIR = OUTPUT_ROOT / "findings" / "q1_diagnose"
for d in (TABLE_DIR, CHART_DIR, FINDINGS_DIR):
    d.mkdir(parents=True, exist_ok=True)


def season_label(start_year: int) -> str:
    return f"{start_year}-{str(start_year + 1)[-2:]}"

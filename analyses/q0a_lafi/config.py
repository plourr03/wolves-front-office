"""LAFI configuration: weights, season universe, paths.

Kept separate so values can be tweaked without touching the computation code.
The 25/20/20/20/15 weights are the priors from the spec. Empirical re-tuning
happens in the validation phase as a robustness check, not as the default.
"""
from __future__ import annotations

from pathlib import Path

# Component weights (sum to 1.0). Per spec section 2.1.
COMPONENT_WEIGHTS = {
    "ball_stickiness":     0.25,
    "movement_death":      0.20,
    "isolation_reliance":  0.20,
    "action_poverty":      0.20,
    "shot_quality_decay":  0.15,
}

# Season universe.
# Tracking starts 2013-14 with partial data; Synergy goes back further but
# only the modern Synergy (2014-15+) is fully populated. Default window is
# 12 seasons through the current season.
DEFAULT_SEASON_START_YEARS = list(range(2014, 2026))   # 2014-15 .. 2025-26
SEASON_TYPES = ("Regular Season", "Playoffs")

# Predictive validation exclusion policy.
# 2019-20 ended in the Orlando bubble with no fans, condensed schedule, and
# bubble-specific personnel rest patterns. 2020-21 was a 72-game season with
# lingering COVID protocols, no fans for most of it, and bubble hangover for
# the Lakers and Heat. Including them forces ad hoc adjustments or treats
# structurally weird seasons as normal. Default validation excludes both.
# Robustness checks include them with an explicit flag in the chart/table.
VALIDATION_EXCLUDED_YEARS = (2019, 2020)


def validation_seasons(include_covid: bool = False) -> list[int]:
    """Seasons used in the predictive validation regressions.

    Default excludes 2019-20 and 2020-21. Pass include_covid=True to run the
    robustness version that keeps them.
    """
    years = list(DEFAULT_SEASON_START_YEARS)
    if not include_covid:
        years = [y for y in years if y not in VALIDATION_EXCLUDED_YEARS]
    return years

# Wolves diagnosis window per spec section 5.1
WOLVES_TRAJECTORY_YEARS = [2021, 2022, 2023, 2024, 2025]  # 2021-22 .. 2025-26

# Repo paths.
REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_ROOT = REPO_ROOT / "outputs"
CACHE_DIR = OUTPUT_ROOT / "cache" / "q0a_lafi"
TABLE_DIR = OUTPUT_ROOT / "tables" / "q0a_lafi"
CHART_DIR = OUTPUT_ROOT / "charts" / "q0a_lafi"
REPORT_DIR = OUTPUT_ROOT / "reports" / "q0a_lafi"

for d in (CACHE_DIR, TABLE_DIR, CHART_DIR, REPORT_DIR):
    d.mkdir(parents=True, exist_ok=True)


def season_label(start_year: int) -> str:
    """2014 -> '2014-15'."""
    return f"{start_year}-{str(start_year + 1)[-2:]}"


def season_start_year_from_label(label: str) -> int:
    """'2014-15' -> 2014."""
    return int(label.split("-")[0])


# Wolves team_id used across queries.
WOLVES_TEAM_ID = 1610612750

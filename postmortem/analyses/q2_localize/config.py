"""Q2 configuration."""
from __future__ import annotations
from pathlib import Path

WOLVES_TEAM_ID = 1610612750
CURRENT_SEASON_YEAR = 2025  # 2025-26
PREV_SEASON_YEAR = 2024     # 2024-25

# Stint and possession thresholds for lineup analysis.
MIN_LINEUP_POSSESSIONS_HEATMAP = 20   # for headline lineup tables
MIN_LINEUP_POSSESSIONS_CHARTS = 30    # tighter for visualizations
MIN_TWO_MAN_POSSESSIONS = 100
MIN_THREE_MAN_POSSESSIONS = 100

# Bootstrap.
BOOTSTRAP_N = 1000
BOOTSTRAP_SEED = 42
CI_LEVEL = 0.95

# Paths.
REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_ROOT = REPO_ROOT / "outputs"
TABLE_DIR = OUTPUT_ROOT / "tables" / "q2_localize"
CHART_DIR = OUTPUT_ROOT / "charts" / "q2_localize"
FINDINGS_DIR = OUTPUT_ROOT / "findings" / "q2_localize"
CACHE_DIR = REPO_ROOT / "outputs" / "cache" / "q2_localize"
for d in (TABLE_DIR, CHART_DIR, FINDINGS_DIR, CACHE_DIR):
    d.mkdir(parents=True, exist_ok=True)


def season_label(start_year: int) -> str:
    return f"{start_year}-{str(start_year + 1)[-2:]}"


# Wolves player IDs (2025-26 rotation; some also relevant for 2024-25).
ANT_ID = 1630162           # Anthony Edwards
CONLEY_ID = 201144          # Mike Conley
GOBERT_ID = 203497          # Rudy Gobert
NAZ_ID = 1629675            # Naz Reid
MCDANIELS_ID = 1630183      # Jaden McDaniels
RANDLE_ID = 203944          # Julius Randle
DIVINCENZO_ID = 1628978     # Donte DiVincenzo
DOSUNMU_ID = 1630245        # Ayo Dosunmu
INGLES_ID = 204060          # Joe Ingles
KYLE_ANDERSON_ID = 203937   # Kyle Anderson
CLARK_ID = 1641740          # Jaylen Clark
HYLAND_ID = 1630538         # Bones Hyland
DILLINGHAM_ID = 1642265     # Rob Dillingham
SHANNON_ID = 1630545        # Terrence Shannon Jr.
BERINGER_ID = 1642866       # Joan Beringer

CORE_ROTATION = [ANT_ID, CONLEY_ID, GOBERT_ID, NAZ_ID, MCDANIELS_ID,
                 RANDLE_ID, DIVINCENZO_ID, DOSUNMU_ID]
WING_OR_GUARD_DEPTH = [INGLES_ID, KYLE_ANDERSON_ID, CLARK_ID, HYLAND_ID,
                       DILLINGHAM_ID, SHANNON_ID]
BIGS = [GOBERT_ID, NAZ_ID, RANDLE_ID, BERINGER_ID]

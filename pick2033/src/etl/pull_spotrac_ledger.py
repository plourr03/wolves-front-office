"""Fresh post-trade pull of the Spotrac future-pick ledger into pick2033.

Reuses offseason/scripts/pull_nba_draft_picks.py wholesale (its parsing is
battle-tested); only the output location changes, so the offseason project's
canonical pre-trade pull (2026-06-06) stays untouched for provenance.
Output: data/raw/spotrac/nba_draft_picks_future.{csv,json}
"""

import importlib.util
import sys
from datetime import date
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = PROJECT_ROOT.parent
SCRIPT = REPO_ROOT / "offseason" / "scripts" / "pull_nba_draft_picks.py"
OUT_DIR = PROJECT_ROOT / "data" / "raw" / "spotrac"


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    spec = importlib.util.spec_from_file_location("pull_nba_draft_picks", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["pull_nba_draft_picks"] = mod
    spec.loader.exec_module(mod)
    mod.OUTPUT_DIR = str(OUT_DIR)
    mod.CSV_PATH = str(OUT_DIR / "nba_draft_picks_future.csv")
    mod.JSON_PATH = str(OUT_DIR / "nba_draft_picks_future.json")
    mod.main()
    (OUT_DIR / "PULL_DATE.txt").write_text(date.today().isoformat())
    print(f"ledger refreshed -> {mod.CSV_PATH}")


if __name__ == "__main__":
    main()

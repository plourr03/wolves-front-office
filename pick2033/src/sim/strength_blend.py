"""Strength-space calibrations. At M1 this holds the SRS -> wins mapping
(fit fresh on the 1980+ panel; e_calibration_params.json is NOT reused because
its wins_a/wins_b were fit on a deflated rotation-rollup net over 3 seasons --
a different input variable; the fresh slope is cross-checked against it in the
validation report). The roster-BPM -> SRS mapping and the blend schedule land
at S5 (M4).

    win_pct = 0.5 + c * srs + eps      (fit on win_pct handles shortened
                                        seasons for free; wins = 82 * win_pct)
"""

from __future__ import annotations

import json
from pathlib import Path

import duckdb
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "data" / "warehouse.duckdb"
PARAMS_PATH = PROJECT_ROOT / "outputs" / "posteriors" / "srs_wins_params.json"


def fit_srs_to_wins() -> dict:
    con = duckdb.connect(str(DB_PATH), read_only=True)
    df = con.execute("SELECT srs, win_pct FROM franchise_seasons").fetchdf()
    con.close()
    x, y = df.srs.values, df.win_pct.values - 0.5
    c = float(np.sum(x * y) / np.sum(x * x))  # through-origin by construction
    resid = y - c * x
    params = {
        "c": c,
        "resid_sd_win_pct": float(resid.std(ddof=1)),
        "n": len(df),
        "note": "win_pct = 0.5 + c*srs; cross-check vs e_calibration wins_b in validation report",
    }
    PARAMS_PATH.parent.mkdir(parents=True, exist_ok=True)
    PARAMS_PATH.write_text(json.dumps(params, indent=1))
    return params


def load_srs_to_wins() -> dict:
    if not PARAMS_PATH.exists():
        return fit_srs_to_wins()
    return json.loads(PARAMS_PATH.read_text())


def wins_from_srs(srs: np.ndarray, rng: np.random.Generator | None = None,
                  season_noise: bool = True, games: int = 82) -> np.ndarray:
    """Expected (or noisy) wins from SRS. Renormalization to the league total
    happens in the season loop (Engine D), not here."""
    p = load_srs_to_wins()
    wp = 0.5 + p["c"] * srs
    if season_noise:
        if rng is None:
            raise ValueError("season_noise=True requires rng")
        wp = wp + rng.normal(0, p["resid_sd_win_pct"], size=np.shape(srs))
    return np.clip(wp, 0.02, 0.98) * games

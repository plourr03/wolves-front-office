"""Gate 8.4 tail-realism logic, pre-committed per the ratified 2026-07-01
operationalization (docs/decisions.md) BEFORE the M4 gate run. Amendments
encoded exactly:

  A1. Both tails gated at the TERMINAL horizon (2033) within +/-25% of the
      historical unconditional base rate.
  A2. Transient check: per-year tail-rate excess non-increasing across
      2027-2033 with tolerance 2x Monte Carlo SE per year.
  A3. Historical base rates on WIN-PERCENTAGE thresholds (>= .732 top,
      <= .244 bottom) so shortened seasons enter at pace.
  A4. Pooled-over-horizons rates reported, un-gated.

Disclosure carried on every report emission: this operationalization was
chosen after a correlated preview (justified a priori: phi^7 ~ 0.07 makes
2033 effectively stationary); weaker than true pre-registration.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

TOP_TAIL_WPCT = 0.732      # >= 60 wins at 82-game pace
BOTTOM_TAIL_WPCT = 0.244   # <= 20 wins at 82-game pace
BAND = 0.25

DISCLOSURE = ("Operationalization chosen after a correlated preview "
              "(2026-07-01), justified a priori (phi^7 ~ 0.07 makes the "
              "terminal horizon effectively stationary); weaker than true "
              "pre-registration and disclosed as such.")


def historical_tail_rates(win_pct: np.ndarray) -> tuple[float, float]:
    """Base rates on win-percentage thresholds (amendment 3)."""
    return float((win_pct >= TOP_TAIL_WPCT).mean()), float((win_pct <= BOTTOM_TAIL_WPCT).mean())


@dataclass
class TailGateResult:
    terminal_top: float
    terminal_bottom: float
    hist_top: float
    hist_bottom: float
    terminal_pass: bool
    transient_pass: bool
    yearly_top: list
    yearly_bottom: list
    pooled_top: float
    pooled_bottom: float

    @property
    def gate_pass(self) -> bool:
        return self.terminal_pass and self.transient_pass


def _non_increasing_within_noise(excess: np.ndarray, se: np.ndarray) -> bool:
    """Amendment 2: inversions within 2x per-year MC SE pass."""
    for i in range(1, len(excess)):
        tol = 2.0 * float(np.hypot(se[i], se[i - 1]))
        if excess[i] > excess[i - 1] + tol:
            return False
    return True


def evaluate_tail_gate(sim_win_pct: np.ndarray, hist_win_pct: np.ndarray) -> TailGateResult:
    """sim_win_pct: (n_paths, n_years, n_teams) simulated win percentages,
    year axis ordered 2027..2033. hist_win_pct: 1-D historical panel."""
    hist_top, hist_bottom = historical_tail_rates(hist_win_pct)
    n_paths, n_years, n_teams = sim_win_pct.shape
    n_cells = n_paths * n_teams

    yearly_top, yearly_bottom, se_top, se_bottom = [], [], [], []
    for y in range(n_years):
        t = float((sim_win_pct[:, y, :] >= TOP_TAIL_WPCT).mean())
        b = float((sim_win_pct[:, y, :] <= BOTTOM_TAIL_WPCT).mean())
        yearly_top.append(t)
        yearly_bottom.append(b)
        se_top.append(np.sqrt(max(t * (1 - t), 1e-12) / n_cells))
        se_bottom.append(np.sqrt(max(b * (1 - b), 1e-12) / n_cells))

    term_top, term_bottom = yearly_top[-1], yearly_bottom[-1]
    terminal_pass = (abs(term_top - hist_top) / hist_top <= BAND
                     and abs(term_bottom - hist_bottom) / hist_bottom <= BAND)
    transient_pass = (
        _non_increasing_within_noise(np.array(yearly_top) - hist_top, np.array(se_top))
        and _non_increasing_within_noise(np.array(yearly_bottom) - hist_bottom, np.array(se_bottom)))

    return TailGateResult(
        terminal_top=term_top, terminal_bottom=term_bottom,
        hist_top=hist_top, hist_bottom=hist_bottom,
        terminal_pass=terminal_pass, transient_pass=transient_pass,
        yearly_top=yearly_top, yearly_bottom=yearly_bottom,
        pooled_top=float((sim_win_pct >= TOP_TAIL_WPCT).mean()),
        pooled_bottom=float((sim_win_pct <= BOTTOM_TAIL_WPCT).mean()),
    )

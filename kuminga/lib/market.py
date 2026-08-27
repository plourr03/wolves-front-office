"""Impact -> market salary, by empirical percentile mapping.

WHY NOT THE LINEAR PAR CURVE. `build_value_layer.fit_par_curves` fits
salary = a + b*net over players earning at least $8,000,000, because those are the
deals the open market actually set. That is the right sample for its purpose, but the
fitted line has an intercept near $19.6M, so using it to price a player whose market
might land BELOW $8M is an out-of-sample extrapolation: it prices a league-average
player at roughly $19.6M and hands Kuminga at the taxpayer MLE a $17.7M "bargain" that
is mostly the intercept. That number is an artefact of the selection, not a finding.

The project's own value layer already anticipates this and says the primary surplus
should be in NET units, because those are bounded. This module supplies the dollar
view without the extrapolation, by mapping percentile to percentile:

    net -> its percentile in the impact distribution
        -> the same percentile of the salary distribution
        -> dollars

Monotone by construction, bounded by the observed salary range, and it needs no
functional form. The sample is rotation players on non-minimum deals: reliable
estimates, salary above $2,000,000, so a minimum contract (which carries no market
information about the player) does not drag the low end down.

Calibration check, 2026-27 book: net 0.0 maps to about $5.4M, Kuminga's +1.33 to about
$11.5M, Edwards's +1.88 to about $16.0M, Gobert's +5.28 to about $57.1M. Those are
recognisable prices, which the linear curve's outputs were not.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

MIN_MARKET_SALARY = 2_000_000


class MarketCurve:
    """Percentile map from an impact estimate to a market salary."""

    def __init__(self, nets: np.ndarray, salaries: np.ndarray, label: str = ""):
        self.nets = np.sort(np.asarray(nets, dtype=float))
        self.salaries = np.sort(np.asarray(salaries, dtype=float))
        self.label = label
        self.n = len(self.nets)

    def percentile(self, net: float) -> float:
        return float((self.nets < net).mean())

    def salary(self, net):
        p = np.searchsorted(self.nets, np.asarray(net, dtype=float), side="left") / self.n
        return np.quantile(self.salaries, np.clip(p, 0.0, 1.0))

    def __repr__(self):
        return (f"MarketCurve({self.label}, n={self.n}, "
                f"${self.salaries.min()/1e6:.1f}M-${self.salaries.max()/1e6:.1f}M)")


def build(value: pd.DataFrame, salary_by_pid: pd.Series, net_col: str,
          label: str = "", min_salary: float = MIN_MARKET_SALARY) -> MarketCurve:
    """Fit the curve for one impact view over market-priced rotation players."""
    df = value.copy()
    df["salary"] = df.player_id.map(salary_by_pid)
    m = df[df.salary.notna() & (df.salary > min_salary)
           & df[net_col].notna()
           & (df.reliable.astype(str).str.lower() == "true")]
    return MarketCurve(m[net_col].to_numpy(), m.salary.to_numpy(), label or net_col)

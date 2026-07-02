"""Backfill directive 1 (2026-07-02): synthetic test of the Duncan-pattern
bias direction.

Dispute on record: the coverage memo claimed smooth same-franchise re-sign
mislabeling ATTENUATES the contract coefficient; Bobby's hypothesis is the
opposite -- the mislabeling deletes true walk-year person-time from
NON-events (stayers re-sign and their years=0 rows get relabeled as
mid-contract), leaving the years=0 pool leaver-enriched, inflating hazard
at years=0 and EXAGGERATING the slope.

Design: simulate spells under a known discrete-time hazard
    P(depart) = logistic(b0 + b_c * years_remaining),  b_c < 0
with 3-5 year contracts; walk-year survivors re-sign with the same team.
Inject mislabeling: a fraction f of re-sign junctions are "smooth"
(undetected), merging adjacent contracts so years_remaining counts down to
the MERGED end. Fit logistic MLE on clean vs corrupted labels; compare b_c.
"""

from __future__ import annotations

import sys

import numpy as np
from scipy.optimize import minimize

TRUE_B0, TRUE_BC = -1.2, -0.45
N_SPELLS, MAX_SEASONS, RESIGN_P, SEED = 6000, 15, 0.85, 20330702


def simulate_clean_and_corrupt(rng):
    """Cleaner implementation: generate per-spell, produce both label sets."""
    clean_rows, corrupt_rows = [], []
    for s in range(N_SPELLS):
        smooth = rng.random() < 0.6
        season, alive = 0, True
        spell_true, spell_seasons = [], []
        while alive and season < MAX_SEASONS:
            length = int(rng.integers(3, 6))
            for k in range(length):
                yrs_rem = length - 1 - k
                p = 1 / (1 + np.exp(-(TRUE_B0 + TRUE_BC * yrs_rem)))
                event = bool(rng.random() < p)
                spell_true.append([yrs_rem, event])
                spell_seasons.append(season)
                season += 1
                if event:
                    alive = False
                    break
                if season >= MAX_SEASONS:
                    alive = False
                    break
            else:
                # completed the contract without departing: walk-year survived
                if rng.random() < RESIGN_P:
                    continue
                spell_true[-1][1] = True     # FA walk = departure at walk year
                alive = False
        clean_rows.extend(spell_true)
        if smooth:
            # merged contract: years count down to the spell's final season
            last = len(spell_true) - 1
            corrupt_rows.extend([[last - i, ev] for i, (_, ev) in enumerate(spell_true)])
        else:
            corrupt_rows.extend(spell_true)
    return np.array(clean_rows, float), np.array(corrupt_rows, float)


def fit_logistic(yrs, y):
    yrs_z = (yrs - yrs.mean()) / yrs.std()

    def nll(theta):
        z = np.clip(theta[0] + theta[1] * yrs_z, -30, 30)
        return float(np.sum(np.logaddexp(0, z) - y * z))

    res = minimize(nll, x0=np.array([-1.0, -0.3]), method="Nelder-Mead")
    return res.x[1] / yrs.std()   # back to per-year scale


def main():
    rng = np.random.default_rng(SEED)
    clean, corrupt = simulate_clean_and_corrupt(rng)
    b_clean = fit_logistic(clean[:, 0], clean[:, 1])
    b_corrupt = fit_logistic(corrupt[:, 0], corrupt[:, 1])
    print(f"true b_c per year: {TRUE_BC}")
    print(f"clean-label fit:   {b_clean:+.4f}")
    print(f"corrupt-label fit: {b_corrupt:+.4f}")
    verdict = ("EXAGGERATES (Bobby right, memo wrong)"
               if abs(b_corrupt) > abs(b_clean)
               else "ATTENUATES (memo right)")
    print(f"verdict: mislabeling {verdict}")
    # hazard at walk year, both label sets (the mechanism check)
    for name, d in (("clean", clean), ("corrupt", corrupt)):
        m0 = d[:, 0] == 0
        print(f"  {name}: hazard at years=0: {d[m0, 1].mean():.3f} "
              f"(n={int(m0.sum())}); at years>=2: {d[d[:, 0] >= 2, 1].mean():.3f}")
    sys.exit(0)


if __name__ == "__main__":
    main()

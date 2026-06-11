#!/usr/bin/env python3
"""
gobert_depreciation.py -- the Gobert depreciation curve (feeds Piece 8, "The Price of Rudy").

Computes the spine the article rests on:
  1. DARKO value-vs-DPM curve, fit empirically from the full leaderboard (high-minute players),
     so a projected DPM converts to a projected $ value the same way DARKO prices everyone.
  2. Gobert's net-DPM projected forward by the standard age curve (age 34 -> 35 -> 36).
  3. The contract-surplus curve ($ value minus salary) across 2026-27 / 2027-28 / 2028-29,
     with the point it crosses negative (he is +$4.7M today).
  4. P(healthy AND productive) per window, from the availability model (aged) x the age curve.

The comp-anchored trade-return bands and the time-dependent reservation price live in the
findings doc (they are scouting/market judgments grounded in nba_trade_comps.json + the public
record, not a single regression). This script produces the quantitative spine for them.

    python gobert_depreciation.py
"""
import os
import sys
import csv
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
POST = os.path.abspath(os.path.join(HERE, "..", "..", "postmortem"))
sys.path.insert(0, POST)
import age_curve as AC       # noqa: E402
from lib import db           # noqa: E402

GOBERT = 203497
DARKO_CSV = os.path.join(HERE, "..", "data", "darko-dpm-leaderboard.csv")
# Gobert contract (HoopsHype, verified 2026-06-06): salary by season
SALARY = {"2026-27": 36.5e6, "2027-28": 38.0e6}   # 2027-28 is a PLAYER OPTION (near-certain opt-in)
CUR_DPM = 2.0            # DARKO net (o-2, d+4), rank 32
CUR_VALUE = 39.7e6       # DARKO $ value today
CUR_SALARY_DARKO = 35.0e6


def money(s):
    return float(str(s).replace("$", "").replace("M", "").replace("+", "").replace(",", "")) * 1e6


def load_darko():
    rows = []
    with open(DARKO_CSV, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            try:
                dpm = float(str(r["DPM"]).replace("+", ""))
                mpg = float(r["MPG"])
                val = money(r["$ Value"])
                rows.append((dpm, mpg, val, r["Player"]))
            except (ValueError, KeyError):
                continue
    return rows


def fit_value_curve(rows, min_mpg=26):
    """Fit $ value ~ a + b*DPM for rotation-level minutes (Gobert is 32.8 mpg).
    Value flattens near the max, so fit only the relevant DPM band [-2, +5]."""
    sub = [(d, v) for d, m, v, n in rows if m >= min_mpg and -2 <= d <= 5]
    d = np.array([x[0] for x in sub]); v = np.array([x[1] for x in sub])
    b, a = np.polyfit(d, v, 1)
    pred = a + b * d
    ss = 1 - np.sum((v - pred) ** 2) / np.sum((v - v.mean()) ** 2)
    return a, b, ss, len(sub)


def age_at(season_start_year):
    """Gobert age at the Oct 1 start of the given season-start year, from birthdate."""
    from datetime import date
    r = db.query("SELECT birthdate FROM nba_player_bio WHERE player_id=%s", (GOBERT,))
    bd = r.iloc[0]["birthdate"]
    return (date(season_start_year, 10, 1) - bd).days / 365.25


def cum_age_delta(age_from, age_to):
    """Integrate the standard annual aging rate from age_from to age_to (forward decline)."""
    d, a, step = 0.0, age_from, 0.25
    while a < age_to - 1e-9:
        d += AC._rate(a) * step
        a += step
    return d


def availability_aged():
    """Recency-weighted RS suit-up rate (the model's base), then an age haircut forward.
    Gobert is durable; the haircut reflects that games-played erodes past 34 for centers."""
    r = db.query("""SELECT (g.season_id %% 10000) yr, COUNT(DISTINCT g.game_id) gp
                    FROM nba_games g JOIN nba_player_stats p
                      ON p.game_id=g.game_id AND p.player_id=%s
                    WHERE g.season_type='Regular Season' AND (g.season_id %% 10000) IN (2023,2024,2025)
                    GROUP BY yr""", (GOBERT,))
    gp = {int(x["yr"]): int(x["gp"]) for _, x in r.iterrows()}
    w = {2023: 0.2, 2024: 0.3, 2025: 0.5}
    base = sum(w[y] * min(82, gp.get(y, 0)) / 82 for y in w)
    return base, gp


def main():
    rows = load_darko()
    a, b, r2, n = fit_value_curve(rows)
    print(f"=== DARKO value-vs-DPM fit (MPG>=26, DPM in [-2,5], n={n}) ===")
    print(f"  $value ~= {a/1e6:.1f}M + {b/1e6:.2f}M * DPM   (R^2={r2:.2f})")
    print(f"  check: at Gobert's +2.0 DPM -> ${(a+b*2.0)/1e6:.1f}M (DARKO actual $39.7M)")

    age2627 = age_at(2026)
    print(f"\n  Gobert age at 2026-27 start: {age2627:.2f}")

    # project DPM forward from the current (2025-26, age ~33.3) measurement
    age_cur = age_at(2025)
    windows = [
        ("2026-27 (age 34)", 2026, "Now / age-34 season"),
        ("2027-28 (age 35)", 2027, "the $38M player-option year"),
        ("2028-29 (age 36)", 2028, "hypothetical extension year"),
    ]
    base_avail, gp = availability_aged()
    print(f"\n  Availability (recency-wtd RS suit-up, model base): {base_avail*100:.0f}%  (GP {gp})")

    print(f"\n=== DEPRECIATION CURVE (from current net DPM {CUR_DPM:+.1f}, value ${CUR_VALUE/1e6:.1f}M) ===")
    print(f"{'season':22}{'age':>6}{'net DPM':>9}{'$ value':>10}{'salary':>9}{'surplus':>10}"
          f"{'P(avail)':>10}{'P(prod)':>9}{'window wt':>11}")
    prev = None
    curve = []
    print(f"\n  ANCHORING: DARKO prices Gobert ${(CUR_VALUE-(a+b*CUR_DPM))/1e6:+.1f}M ABOVE the DPM-only fit")
    print(f"  (a defensive-anchor/minutes premium), so the surplus curve uses his ACTUAL ${CUR_VALUE/1e6:.1f}M")
    print(f"  value and applies the empirical marginal slope ${b/1e6:.2f}M per lost DPM point.")
    for label, yr, note in windows:
        ag = age_at(yr)
        dpm = CUR_DPM + cum_age_delta(age_cur, ag)
        val = CUR_VALUE + b * (dpm - CUR_DPM)   # actual-anchored + empirical marginal slope
        sal = SALARY.get(f"{yr}-{str(yr+1)[2:]}")
        # 2028-29 has no contract salary; show value only (would be a new deal)
        surplus = (val - sal) if sal else None
        # P(healthy): base availability with an age haircut (~4 pp per year past 34)
        years_past = max(0, ag - 34.27)
        p_avail = max(0.55, base_avail - 0.045 * years_past)
        # P(productive): prob net DPM stays clearly positive (>=+0.5), normal band SD~0.9
        from math import erf, sqrt
        sd = 0.9
        p_prod = 0.5 * (1 + erf((dpm - 0.5) / (sd * sqrt(2))))
        wt = p_avail * p_prod
        salstr = f"${sal/1e6:.1f}M" if sal else "  (FA)"
        surstr = f"{surplus/1e6:+.1f}M" if surplus is not None else "   n/a"
        print(f"{label:22}{ag:>6.1f}{dpm:>+9.2f}{val/1e6:>9.1f}M{salstr:>9}{surstr:>10}"
              f"{p_avail*100:>9.0f}%{p_prod*100:>8.0f}%{wt*100:>10.0f}%")
        curve.append((label, ag, dpm, val, sal, surplus, p_avail, p_prod, wt))
        prev = surplus

    # find the surplus crossing (interpolate between 2026-27 and 2027-28)
    s1 = curve[0][5]; s2 = curve[1][5]
    if s1 is not None and s2 is not None and s1 > 0 and s2 < 0:
        frac = s1 / (s1 - s2)
        print(f"\n  SURPLUS CROSSES NEGATIVE during 2026-27->2027-28: about {frac*100:.0f}% of the way,")
        print(f"  i.e. around the {'2027 trade deadline / summer 2027' if frac>0.4 else 'early 2026-27 season'}.")
        print(f"  (2026-27 surplus {s1/1e6:+.1f}M; 2027-28 surplus {s2/1e6:+.1f}M on the $38M option.)")
    elif s1 is not None and s1 < 0:
        print(f"\n  SURPLUS already negative in 2026-27 ({s1/1e6:+.1f}M).")

    # ---- time-dependent reservation price by view ----
    # The EV sacrificed by trading him scales with his on-court impact, which the age curve
    # erodes equally (absolute) across views. Static "now-EV sacrificed" from the both-out table.
    VIEWS = {  # view: (current impact, static now-EV-sacrificed pp, static return-must-clear pp)
        "box":       (1.48, 0.97, 1.5),
        "DARKO":     (2.00, 2.18, 2.7),
        "consensus": (5.28, 3.87, 4.4),
        "rapm":      (5.76, 5.40, 5.9),
    }
    d_2627 = cum_age_delta(age_cur, age_at(2026))   # to age 34
    d_2728 = cum_age_delta(age_cur, age_at(2027))   # to age 35 (the option year / summer-2027 asset)
    print("\n=== TIME-DEPENDENT EV SACRIFICED BY TRADING (scales with his eroding impact) ===")
    print(f"{'view':12}{'impact now':>11}{'EV-sac now':>12}{'EV-sac deadline':>17}{'EV-sac sum2027':>16}")
    for v, (imp0, ev0, _clear) in VIEWS.items():
        imp_dl = imp0 + d_2627 * 0.5      # deadline ~ mid 2026-27, half a year of decline
        imp_27 = imp0 + d_2728            # summer 2027 = age-35 level
        ev_dl = ev0 * max(0.0, imp_dl) / imp0
        ev_27 = ev0 * max(0.0, imp_27) / imp0
        print(f"{v:12}{imp0:>+11.2f}{ev0:>+11.2f}{ev_dl:>+16.2f}{ev_27:>+15.2f}")
    print("  Reading: the price of KEEPING him (EV you'd sacrifice to trade) falls as he declines,")
    print("  so the reservation bar drops over time. But the realistic RETURN falls faster and goes")
    print("  NEGATIVE by summer 2027 (a $38M age-35 expiring at -$8M surplus = you attach a sweetener).")

    print("\n  NOTE: holds minutes ~constant; a minutes decline would steepen the value drop.")
    print("  NOTE: defense ages more gracefully than offense for a rim anchor; the standard 50/50")
    print("        split is used here, with a slower-defense sensitivity flagged in the doc.")


if __name__ == "__main__":
    main()

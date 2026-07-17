"""Defense-screened recompute (fixes the verification's headline finding).

The analyst's class dropped the 'two-way wing KNOWN FOR DEFENSE' criterion
(position-only filter), so ~half of the 38 marker-usable members are
offense-first scorers who gained efficiency mechanically by cutting usage next
to a star -- the wrong archetype for calibrating a 3-and-D wing like Jaden.

This applies a NON-CIRCULAR defensive screen: the wing was already a primary
perimeter defender BEFORE the pairing (jd_load_before >= class median), which
uses BEFORE deployment, not the AFTER markers being calibrated. It recomputes
the marker distributions and the proposed thresholds on the screened subset
(the headline) and prints the full-38 numbers beside them (robustness).
Confirms all three seeds survive the screen. Freezes nothing.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd

REPO = Path(r"C:\Users\bobby\playground\wolves-front-office")
DATA = REPO / "all-for-one" / "board" / "jaden_calibration" / "data"
SEEDS = {203932: "Aaron Gordon", 1628969: "Mikal Bridges", 1628384: "OG Anunoby"}


def q(s, p):
    return float(pd.Series(s).dropna().quantile(p))


def med(s):
    return float(pd.Series(s).dropna().median())


def main():
    m = pd.read_parquet(DATA / "marker_movements.parquet")
    cov = pd.read_parquet(DATA / "jd_cover.parquet") if (DATA / "jd_cover.parquet").exists() else None

    thr = med(m.jd_load_before)                       # non-circular BEFORE-deployment screen
    scr = m[m.jd_load_before >= thr].copy()
    print(f"defensive screen: jd_load_before >= class median {thr:.3f}")
    print(f"  full class n={len(m)}  ->  defense-screened n={len(scr)}")
    seeds_in = [nm for pid, nm in SEEDS.items() if pid in set(scr.player_id)]
    print(f"  seeds surviving the screen: {seeds_in}")
    for pid, nm in SEEDS.items():
        r = m[m.player_id == pid]
        if len(r):
            print(f"    {nm:14s} jd_load_before={r.iloc[0].jd_load_before:.3f} "
                  f"({'IN' if r.iloc[0].jd_load_before >= thr else 'OUT'})")

    def compare(label, col, transform=None):
        fa = m[col] if transform is None else transform(m)
        sa = scr[col] if transform is None else transform(scr)
        print(f"\n{label}")
        print(f"  full-38  : median {med(fa):+.4f}  q25 {q(fa,.25):+.4f}  q75 {q(fa,.75):+.4f}")
        print(f"  screened : median {med(sa):+.4f}  q25 {q(sa,.25):+.4f}  q75 {q(sa,.75):+.4f}  (n={pd.Series(sa).notna().sum()})")
        return sa

    print("\n" + "=" * 70)
    print("OFFENSIVE LADDER (screened headline vs full-38 robustness)")
    print("=" * 70)
    tr3 = compare("JO-EFF ts_after_vs_trail3", "ts_after_vs_trail3")
    lgmv = compare("JO-EFF d(ts_vs_league)", None, lambda d: d.ts_vs_lg_after - d.ts_vs_lg_before)
    sa75 = compare("JO-FLOOR scoring-attempts/75 %chg", "sa75_pctchg")

    # proposed bands on the SCREENED subset (same quantile logic as the analyst)
    leap_tr3 = round(q(tr3, .75), 3); leap_lg = round(q(lgmv, .75), 3); decl = round(q(tr3, .25), 3)
    print(f"\nPROPOSED JO-EFF bands, DEFENSE-SCREENED (headline):")
    print(f"  LEAP    : ts_after_vs_trail3 >= {leap_tr3:+.3f} AND d(ts_vs_league) >= {leap_lg:+.3f}")
    print(f"  FLAT    : ts_after_vs_trail3 in ({decl:+.3f}, {leap_tr3:+.3f})")
    print(f"  DECLINE : ts_after_vs_trail3 <= {decl:+.3f}")
    n_leap = int(((scr.ts_after_vs_trail3 >= leap_tr3) & ((scr.ts_vs_lg_after - scr.ts_vs_lg_before) >= leap_lg)).sum())
    print(f"  screened members in LEAP band: {n_leap}/{len(scr)}")
    # who is in the leap band (archetype check)
    lb = scr[(scr.ts_after_vs_trail3 >= leap_tr3) & ((scr.ts_vs_lg_after - scr.ts_vs_lg_before) >= leap_lg)]
    print(f"  LEAP-band members: {list(lb.wing)}")

    print("\nJO-FLOOR floor at -15% (anti-vanishing):")
    print(f"  full-38  trips: {int((m.sa75_pctchg <= -15).sum())}/{len(m)}")
    print(f"  screened trips: {int((scr.sa75_pctchg <= -15).sum())}/{len(scr)}")

    print("\nJO-GROWTH (at least one rung):")
    def growth_any(d):
        a = d.selfcreate_ppfga_after > d.selfcreate_ppfga_before
        b = d.ftr_after > d.ftr_before
        c = (d.fg3a_pg_after > d.fg3a_pg_before) & (d.fg3_pct_after > d.fg3_pct_before)
        return (a | b | c)
    print(f"  full-38  : {int(growth_any(m).sum())}/{len(m)}")
    print(f"  screened : {int(growth_any(scr).sum())}/{len(scr)}")

    print("\n" + "=" * 70)
    print("DEFENSIVE GATE (screened headline vs full-38)")
    print("=" * 70)
    compare("JD-LOAD after share", "jd_load_after")
    hold = compare("JD-HOLD after (pts allowed vs baseline)", "jd_hold_after")
    print(f"\nPROPOSED JD-HOLD strong-pass (screened): <= {round(q(hold,.25),3):+.3f} (class q25)")
    print(f"  JD-LOAD pass at after-share >= screened median {med(scr.jd_load_after):.3f}")
    print(f"  JD-HOLD hold-below-baseline: full {int((m.jd_hold_after<0).sum())}/{len(m)}, "
          f"screened {int((scr.jd_hold_after<0).sum())}/{len(scr)}")

    # persist the screened proposals
    out = {
        "screen": {"rule": "jd_load_before >= class median", "threshold": thr,
                   "n_full": len(m), "n_screened": len(scr), "seeds_in": seeds_in},
        "JO-EFF": {"leap_ts_after_vs_trail3_ge": leap_tr3, "leap_d_ts_vs_league_ge": leap_lg,
                   "decline_le": decl, "n_leap_screened": n_leap, "leap_members": list(lb.wing)},
        "JO-FLOOR": {"floor_pctchg": -15, "trips_screened": int((scr.sa75_pctchg <= -15).sum())},
        "JO-GROWTH": {"rule": "at least one rung", "screened": int(growth_any(scr).sum()), "of": len(scr)},
        "JD-HOLD": {"strong_pass_le": round(q(hold, .25), 3), "hold_below_screened": int((scr.jd_hold_after < 0).sum())},
        "JD-LOAD": {"pass_after_share_ge": round(med(scr.jd_load_after), 3)},
    }
    (DATA / "threshold_proposals_screened.json").write_text(json.dumps(out, indent=1))
    print(f"\nwrote {DATA/'threshold_proposals_screened.json'}")


if __name__ == "__main__":
    main()

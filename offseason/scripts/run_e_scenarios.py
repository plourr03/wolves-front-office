#!/usr/bin/env python3
"""
run_e_scenarios.py  -- Component E baseline + league variants + overlay eyeball.

Runs the calibrated 2026-27 baseline, then the two league-assumption variants the
review requires (no Wolves trade is simulated; these are alternative BASELINES):

  - Tatum THREE-WAY: healthy / plays-but-diminished (the DEFAULT for a Year-1 Achilles
    return) / out. Boston's baseline net assumes a healthy Tatum (its full roster-change
    delta); diminished scales that delta to 0.5, out to 0.0 (= Boston's measured
    2025-26 net, which was largely Tatum-less anyway).
  - Giannis landing: baseline puts Giannis on Miami; the variant keeps him in Milwaukee
    (Miami reverts to its measured net, Milwaukee keeps him). Tests how much the field
    depends on the single most consequential assumed move.

Then the matchup-overlay eyeball: MIN vs each contender, base resolver vs overlay,
since the overlay cannot be backtested and basketball sanity is its only check.

    python run_e_scenarios.py
"""

import os
import sys
import copy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_team_ratings as A          # noqa: E402
import bracket_sim as E                 # noqa: E402

OUTDIR = os.path.join(HERE, "..", "outputs")
NS_BASE, NS_VAR = 20000, 12000


def safe(s): return str(s).encode("ascii", "replace").decode()


def title_table(res, teams):
    return {t: res["teams"][t]["title"] for t in teams}


def topk(res, k=6):
    return sorted(res["teams"], key=lambda t: -res["teams"][t]["title"])[:k]


# Title odds reported as a band over the shape (sigma) uncertainty. The realistic de-vig
# range is ~3.5-7.0 (sigma<3.5 produces a 19.8% favorite-gap that violates the actual
# boards; the standard proportional de-vig gives the central 5.5). {4.5,5.5,6.5} captures
# ~70% of that realistic range and the board reproduction holds across all three.
SIGMA_BAND = [4.5, 5.5, 6.5]


def sim_at_sigma(strengths, sigma, n_sims, seed=7):
    base_ep = E.load_e_params()
    E._EP = {**base_ep, "sigma_unobs": sigma}
    res = E.simulate_league(strengths, n_sims=n_sims, use_overlay=True, seed=seed)
    E._EP = base_ep
    return res


def main():
    imp = A.load_impacts()
    base = E.build_2026_27_league(imp)
    # title-odds BAND over the shape (sigma) uncertainty: the de-vig method is not pinned
    # down (gate finding), so we carry sigma as a range and never print a false point.
    band = {sg: sim_at_sigma(base, sg, NS_BASE, seed=7) for sg in SIGMA_BAND}
    res = band[5.5]
    lines = []

    def emit(s=""):
        print(safe(s)); lines.append(s)

    emit("=== Component E: 2026-27 BASELINE (calibrated, no trade) ===")
    p = E.load_e_params()
    emit(f"params: deflation {p['alpha']}+{p['beta']}*hot, wins={p['wins_a']}+{p['wins_b']}*net; "
         f"title odds as a BAND over sigma_unobs in {SIGMA_BAND} (central 5.5)  [{p['source']}]")
    emit(f"\n{'team':5}{'act25':>7}{'exp':>7}{'delta':>7}{'net26':>8}{'munc':>6}{'title band (lo-mid-hi)':>24}{'conf':>7}{'src':>16}")
    def title_band(t):
        vals = sorted(band[sg]["teams"][t]["title"] for sg in SIGMA_BAND)
        return vals[0], res["teams"][t]["title"], vals[-1]
    for t in topk(res, 14):
        s = base[t]; d = res["teams"][t]
        lo, mid, hi = title_band(t)
        tb = f"{lo*100:.1f}-{mid*100:.1f}-{hi*100:.1f}%"
        emit(f"{t:5}{s['actual25']:>7.2f}{s.get('exp',s['actual25']):>7.2f}{s['delta']:>+7.2f}{d['net']:>8.2f}"
             f"{d['munc']:>6.2f}{tb:>24}{d['conf']*100:>6.1f}%{s['src']:>16}")
    m = res["teams"]["MIN"]; mlo, mmid, mhi = title_band("MIN")
    emit(f"MIN: net {m['net']:.2f} title {mlo*100:.1f}-{mmid*100:.1f}-{mhi*100:.1f}% (band over sigma) "
         f"conf {m['conf']*100:.1f}% reach-CF {m['cf']*100:.1f}% reach-R2 {m['r2']*100:.1f}%")

    # ---- Tatum three-way ----
    emit("\n=== Variant A: Tatum three-way (BOS) ===")
    full = base["BOS"]["full_delta"]; exp = base["BOS"]["exp"]
    emit(f"  Boston healthy-Tatum delta = {full:+.2f} over its regressed (Tatum-less) core {exp:+.2f}; "
         f"baseline uses diminished (0.5x).")
    emit(f"  {'branch':16}{'BOS net':>9}{'BOS title':>11}{'OKC title':>11}{'champ is East':>15}")
    for label, f in [("healthy", 1.0), ("diminished*", 0.5), ("out", 0.0)]:
        v = copy.deepcopy(base)
        v["BOS"]["net"] = round(exp + f * full, 2)               # regressed core + scaled Tatum
        rv = E.simulate_league(v, n_sims=NS_VAR, use_overlay=True, seed=99)
        east_title = sum(rv["teams"][t]["title"] for t in v if v[t]["conf"] == "E")
        emit(f"  {label:16}{v['BOS']['net']:>9.2f}{rv['teams']['BOS']['title']*100:>10.1f}%"
             f"{rv['teams']['OKC']['title']*100:>10.1f}%{east_title*100:>14.1f}%")
    emit("  * diminished is the DEFAULT (baseline) expectation for a Year-1 Achilles return.")

    # ---- Giannis landing ----
    emit("\n=== Variant B: Giannis landing ===")
    emit(f"  {'scenario':22}{'MIA net':>9}{'MIA title':>11}{'MIA conf':>10}")
    for label, mia_net in [("Giannis -> MIA (base)", base["MIA"]["net"]),
                           ("Giannis stays MIL", base["MIA"]["exp"])]:   # MIA reverts to its regressed core
        v = copy.deepcopy(base)
        v["MIA"]["net"] = mia_net
        if "stays MIL" in label:
            v["MIL"]["net"] = base["MIL"]["exp"]         # Giannis restored to Milwaukee (regressed core, no removal)
        rv = E.simulate_league(v, n_sims=NS_VAR, use_overlay=True, seed=55)
        emit(f"  {label:22}{v['MIA']['net']:>9.2f}{rv['teams']['MIA']['title']*100:>10.1f}%"
             f"{rv['teams']['MIA']['conf']*100:>9.1f}%")
    emit("  (MIN is West; these East moves change MIN's Finals opponent, not its path there.)")

    # ---- overlay eyeball ----
    emit("\n=== Matchup-overlay eyeball: MIN vs each contender (cannot be backtested) ===")
    on = E.conditional_series("MIN", base, use_overlay=True)
    off = E.conditional_series("MIN", base, use_overlay=False)
    emit(f"  {'opp':5}{'net':>8}{'base%':>9}{'overlay%':>10}{'overlay tilt':>14}")
    for o in sorted(on, key=lambda x: -base[x]["net"])[:11]:
        tilt = (on[o] - off[o]) * 100
        emit(f"  {o:5}{base[o]['net']:>+8.2f}{off[o]*100:>8.1f}%{on[o]*100:>9.1f}%{tilt:>+13.1f}")
    emit("  (tilt > 0 = the overlay helps MIN vs that style; capped at a few series points)")

    os.makedirs(OUTDIR, exist_ok=True)
    open(os.path.join(OUTDIR, "e_baseline.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print(f"\nwrote {os.path.relpath(os.path.join(OUTDIR, 'e_baseline.md'), HERE)}")


if __name__ == "__main__":
    main()

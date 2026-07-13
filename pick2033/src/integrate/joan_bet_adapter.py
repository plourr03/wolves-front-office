"""F: Joan Bet integration adapter (spec 7.8) -- the equity final pass.

Restates the FINAL priced bill in championship-equity terms via the ON-5
CRN-paired marginal-equity curve (outputs/posteriors/equity_curve.json).
Per the gate ruling: DELTAS ONLY -- absolute P(title) levels never leave
this layer. This file is the only coupling point to the Joan Bet
machinery (here, its cached curve; the curve build imported bracket_sim).

Conversion chain, per path and instrument:
  4yr-VORP payoff V  ->  per-season net-rating delta d = V / 4
  (a season of VORP is already a net-rating-equivalent contribution:
  BPM points per 100 possessions above replacement, prorated by the
  player's share of team minutes; no wins conversion is needed)
  ->  for each of the four delivery seasons (draft year +1 .. +4, clamped
  to the 2033 sim horizon), read the receiving team's simulated strength
  net = (win_pct - 0.5) / c  (srs_wins_params.json) and interpolate the
  equity curve (tier axis x delta axis, anchored at delta 0 -> 0 pp)
  ->  cumulative title-equity pp = sum over the four delivery seasons;
  per-season = cumulative / 4 (flat spread, documented).

Two co-equal perspectives (plan D3, Bobby amendment 1): value delivered
to Charlotte read on CHA's simulated tier path, value forgone by
Minnesota read on MIN's. The SAME per-path VORP draws feed both (the
swap exchanges the same two picks, so CHA's slot-value gain is MIN's
slot-value loss path by path); only the tier path differs. The VORP
arrays are re-generated with the pricing pass's exact rng sequence and
ASSERTED bit-close against swap_pricing_FINAL.json before any equity
number is written.

Totals are per-path sums, never sums of marginal means. Negative payoff
draws (a realized late pick below replacement value) map through odd
symmetry; deltas beyond the 4.0 grid edge extrapolate on the 3.0-4.0
slope (rare). Per-instrument conversion prices each instrument's delta
separately; at the observed magnitudes (d mostly < 1.0) the curve is
near-linear, so the convexity cross-term between overlapping delivery
windows is second-order (documented, not modeled).

Equity is defined for the VORP currency only (WS is not a net-rating
unit); the WS robustness track lives in the VORP bill, not here.
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
from src.models.slot_value import band_residuals, curve_draws, fit as fit_e1, load_data  # noqa: E402
from src.sim.pick_ledger import require_verified_terms, resolve_all  # noqa: E402
from src.sim.swap_pricing import SWAP_YEARS, payoff_draws, scenario_masks  # noqa: E402

SIMS = PROJECT_ROOT / "outputs" / "sims"
OUT = PROJECT_ROOT / "outputs" / "json"
VARIANT = "two_tier"
SECONDS_YEARS = (2029, 2032, 2033)
RESOLVED_2026 = {"out_slot": 28, "in_slot": 33, "draft_year": 2026}
DELIVERY_SEASONS = 4


def _load_curve() -> dict:
    payload = json.loads((PROJECT_ROOT / "outputs" / "posteriors" / "equity_curve.json").read_text())
    return payload


def _pp_for_tier(points: list, d: np.ndarray) -> np.ndarray:
    """Delta-axis interpolation for one tier, anchored at (0, 0), odd
    symmetry for negative deltas, end-slope extrapolation past the grid."""
    xs = np.concatenate([[0.0], [p["net_delta"] for p in points]])
    ys = np.concatenate([[0.0], [p["dtitle_pp_mean"] for p in points]])
    dd = np.abs(d)
    pp = np.interp(dd, xs, ys)
    over = dd > xs[-1]
    if over.any():
        slope = (ys[-1] - ys[-2]) / (xs[-1] - xs[-2])
        pp[over] = ys[-1] + slope * (dd[over] - xs[-1])
    return np.sign(d) * pp


def equity_from_value_draws(value_draws: np.ndarray, context: dict) -> np.ndarray:
    """Interface contract per spec 7.8. context needs: curve (tier dict),
    net (per-path receiving-team net rating for ONE delivery season).
    Returns title-equity pp for that season's share (d = V/4)."""
    curve = context["curve"]
    net = context["net"]
    d = value_draws / DELIVERY_SEASONS
    tiers = sorted(curve.values(), key=lambda c: c["base_net"])
    base_nets = np.array([t["base_net"] for t in tiers])
    vals = np.stack([_pp_for_tier(t["points"], d) for t in tiers])  # (n_tiers, n)
    netc = np.clip(net, base_nets[0], base_nets[-1])
    idx = np.clip(np.searchsorted(base_nets, netc, side="right") - 1, 0, len(tiers) - 2)
    x0, x1 = base_nets[idx], base_nets[idx + 1]
    w = (netc - x0) / (x1 - x0)
    cols = np.arange(len(netc))
    return (1.0 - w) * vals[idx, cols] + w * vals[idx + 1, cols]


def instrument_equity(V: np.ndarray, draft_year: int, team: str, winpct: np.ndarray,
                      fr_ids: list, seasons: list, curve: dict, c: float) -> np.ndarray:
    """Cumulative 4-yr title-equity pp for one instrument, one perspective."""
    ti = fr_ids.index(team)
    cum = np.zeros_like(V)
    for k in range(1, DELIVERY_SEASONS + 1):
        s = min(draft_year + k, seasons[-1])          # horizon clamp
        wp = winpct[:, seasons.index(s), ti]
        net = (wp - 0.5) / c
        cum += equity_from_value_draws(V, {"curve": curve, "net": net})
    return cum


def _summ(vals: np.ndarray, masks: dict) -> dict:
    out = {"mean": float(vals.mean()), "q10": float(np.percentile(vals, 10)),
           "q50": float(np.percentile(vals, 50)), "q90": float(np.percentile(vals, 90))}
    out["per_season"] = {k: out[k] / DELIVERY_SEASONS for k in ("mean", "q10", "q50", "q90")}
    out["scenarios"] = {k: {"p": float(m.mean()),
                            "conditional_mean": float(vals[m].mean()) if m.any() else None}
                        for k, m in masks.items()}
    return out


def _assert_matches_final(name: str, vals: np.ndarray, published: dict):
    """The equity pass must run on the exact CRN draws the published bill
    used. Mean and median must reproduce swap_pricing_FINAL.json."""
    for key, mine in (("mean", vals.mean()), ("q50", np.percentile(vals, 50))):
        ref = published[key]
        if not np.isclose(mine, ref, rtol=1e-6, atol=1e-9):
            raise AssertionError(
                f"CRN reproduction failed for {name}.{key}: {mine} vs published {ref}")


def main():
    require_verified_terms()
    params = yaml.safe_load((PROJECT_ROOT / "config" / "model_params.yaml").read_text())
    pricing_seed = params["seed"] + 7
    published = json.loads((OUT / "swap_pricing_FINAL.json").read_text())
    curve_payload = _load_curve()
    curve = curve_payload["curve"]
    srs = json.loads((PROJECT_ROOT / "outputs" / "posteriors" / "srs_wins_params.json").read_text())
    c = srs["c"]

    z = np.load(SIMS / f"slots_{VARIANT}_FINAL.npz")
    w = np.load(SIMS / f"winpct_{VARIANT}_FINAL.npz")
    slots = z["slots"]
    fr_ids = [str(t) for t in z["fr_ids"]]
    seasons = [int(s) for s in z["seasons"]]
    winpct = w["winpct"]
    departures = {"Anthony Edwards": z["dep_Anthony_Edwards"].astype(bool)}
    cha_win_2033 = winpct[:, seasons.index(2033), fr_ids.index("CHA")]
    masks = scenario_masks(departures, cha_win_2033)
    n = slots.shape[0]

    # E1 posterior from cache (never refits on a warm cache) + line items.
    df = load_data()
    post, health = fit_e1(df["value_4yr"].values.astype(float),
                          df.slot.values.astype(int), "vorp", params["seed"] + 6)
    residuals = band_residuals(df, post, "value_4yr")
    e1_means = np.array([post[f"m_{k}"].mean() for k in range(1, 61)])
    seconds_flat = float(e1_means[30:45].mean())
    e1_export = json.loads((PROJECT_ROOT / "outputs" / "validation" / "model_e1_slot_value.json").read_text())
    assert np.isclose(seconds_flat, e1_export["vorp"]["seconds_flat_31_45"], rtol=1e-6), \
        "seconds flat value drifted from the E1 export"
    li_2026 = float(e1_means[RESOLVED_2026["out_slot"] - 1] - e1_means[RESOLVED_2026["in_slot"] - 1])

    line_items = {
        "resolved_2026": {
            "out_slot": RESOLVED_2026["out_slot"], "in_slot": RESOLVED_2026["in_slot"],
            "ev_out_vorp": float(e1_means[RESOLVED_2026["out_slot"] - 1]),
            "ev_in_vorp": float(e1_means[RESOLVED_2026["in_slot"] - 1]),
            "net_out_vorp": li_2026,
            "note": "deterministic slot-EV by design; slots known at signing"},
        "seconds": {
            "years": list(SECONDS_YEARS), "flat_value_each_vorp": seconds_flat,
            "total_vorp": seconds_flat * len(SECONDS_YEARS),
            "sensitivity_band_vorp": [float(e1_means[44]), float(e1_means[30])],
            "note": "flat E1 slot-31-45 posterior-mean value per second; band is slot-45 to slot-31 EV"},
    }

    payload = {
        "meta": {
            "tag": "FINAL", "variant": VARIANT, "n_paths": n,
            "pricing_seed": pricing_seed,
            "equity_curve_hash": curve_payload["version_hash"],
            "srs_wins_c": c,
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "code_commit": _commit(),
            "gate_note": curve_payload["gate_note"],
            "conversion_note": (
                "per-season net delta = 4yr VORP / 4 (season VORP is a "
                "net-rating-equivalent unit); tier read per delivery season on the "
                "receiving team's simulated win path, net = (win_pct - 0.5) / c; "
                "delivery = draft year +1..+4 clamped to the 2033 horizon; flat "
                "4-season spread; per-instrument conversion (near-linear curve at "
                "observed deltas, convexity cross-term second-order)"),
            "per_path_sum_note": "totals are per-path sums, not sums of means",
            "currency_note": "equity defined for VORP only; WS is not a net-rating unit",
        },
        "line_items_vorp": line_items,
        "runs": {},
    }

    for top1 in (True, False):
        rng = np.random.default_rng(pricing_seed)
        outcomes = resolve_all(slots, fr_ids, seasons, top1)
        pub = published["runs"][f"top1_{str(top1).lower()}_vorp"]
        V = {}
        total_ps = np.zeros(n)
        for y in SWAP_YEARS:
            pay, _ = payoff_draws(outcomes[y], post, residuals, rng)
            _assert_matches_final(f"swap_{y}", pay, pub["swaps"][str(y)])
            V[f"swap_{y}"] = (pay, y)
            total_ps += pay
        v2033 = curve_draws(post, outcomes[2033].min_slot_resolved, rng, residuals)
        _assert_matches_final("outright_2033", v2033, pub["outright_2033"])
        _assert_matches_final("total_per_path", total_ps + v2033, pub["total_per_path"])
        V["outright_2033"] = (v2033, 2033)
        for y in SECONDS_YEARS:
            V[f"second_{y}"] = (np.full(n, seconds_flat), y)
        V["resolved_2026"] = (np.full(n, li_2026), RESOLVED_2026["draft_year"])

        run = {}
        for persp, team in (("delivered_to_CHA", "CHA"), ("forgone_by_MIN", "MIN")):
            eq = {k: instrument_equity(v, dy, team, winpct, fr_ids, seasons, curve, c)
                  for k, (v, dy) in V.items()}
            picks_swaps = sum(eq[k] for k in
                              [f"swap_{y}" for y in SWAP_YEARS] + ["outright_2033"])
            package = picks_swaps + sum(eq[f"second_{y}"] for y in SECONDS_YEARS) + eq["resolved_2026"]
            run[persp] = {
                "decomposition": {k: _summ(v, masks) for k, v in eq.items()},
                "picks_swaps_total": _summ(picks_swaps, masks),
                "package_total": _summ(package, masks),
            }
        payload["runs"][f"top1_{str(top1).lower()}"] = run

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "total_asset_cost.json").write_text(json.dumps(payload, indent=1))
    base = payload["runs"]["top1_true"]
    for persp in ("delivered_to_CHA", "forgone_by_MIN"):
        t = base[persp]["picks_swaps_total"]
        print(f"{persp}: picks+swaps cumulative {t['mean']:+.2f}pp "
              f"[q10 {t['q10']:+.2f}, q90 {t['q90']:+.2f}] "
              f"(per-season {t['per_season']['mean']:+.3f}pp)")
        p = base[persp]["package_total"]
        print(f"  package (with seconds + 2026): {p['mean']:+.2f}pp "
              f"[q10 {p['q10']:+.2f}, q90 {p['q90']:+.2f}]")
    print(f"line items (VORP): 2026 net {li_2026:.3f}, seconds {seconds_flat:.3f} x 3")
    print(f"total_asset_cost.json written ({payload['meta']['equity_curve_hash']})")


def _commit() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                              capture_output=True, text=True,
                              cwd=PROJECT_ROOT).stdout.strip()
    except OSError:
        return "unknown"


if __name__ == "__main__":
    main()

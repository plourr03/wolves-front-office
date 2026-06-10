#!/usr/bin/env python3
"""
build_rotation_model.py  -- Championship layer, Component B.

The bridge from "a sum of players" to "a team." Component A's naive minutes-weighted
rollup overstates stacked rosters (OKC rolled +13 vs +11 actual) because player RAPM
is measured in mostly-average-teammate contexts and does not add linearly when good
players pile up: one ball, five floor slots, skill overlap. B corrects that with a
redundancy term grounded in STRUCTURAL SATURATION, not a free parameter:

  - skill_surplus  : sum over the six need dimensions of profile above the contender
                     benchmark (stacking a skill past what a team can use is wasted).
  - depth_surplus  : positive impact carried by the rotation BEYOND the top five
                     (good players who cannot all be on the floor).
  - usage_overlap  : stacked on-ball creation (hc-creation + secondary playmaking
                     above median), since one ball saturates.

The penalty is CALIBRATED against the whole league: we regress A's residual
(rolled minus actual 2025-26 net) on each saturation measure and use the one with
real signal, at the fitted slope. So stacked teams come down while the teams A
already nailed (SAS, NYK, the bottom four), which have little surplus, stay put. It
is centered, so it does not shift the league mean or penalize talent that fills gaps
(consistent with the need-fit layer: a duplicate skill is worth less than a
complementary one).

    python build_rotation_model.py        # calibrates B, then re-validates A+B
"""

import os
import sys
import csv
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
POSTMORTEM = os.path.abspath(os.path.join(HERE, "..", "..", "postmortem"))
DATA = os.path.join(HERE, "..", "data")
sys.path.insert(0, HERE)
sys.path.insert(0, POSTMORTEM)
import build_team_ratings as A   # reuse the rollup + impacts
from lib import db  # noqa

DIMS = ["hc_creation", "secondary_playmaking", "off_ball_shooting",
        "def_versatility_poa", "rim_protect_reb", "transition"]
BENCHMARK = {"hc_creation": 0.62, "secondary_playmaking": 0.55, "off_ball_shooting": 0.60,
             "def_versatility_poa": 0.60, "rim_protect_reb": 0.58, "transition": 0.52}
PLAYOFF_ROTATION = 9


def load_dims():
    out = {}
    for r in csv.DictReader(open(os.path.join(DATA, "player_dimensions.csv"), encoding="utf-8")):
        out[r["player_id"]] = {d: float(r[d]) for d in DIMS}
    return out


def rosters_2025_26():
    rows = db.query("""SELECT team_abbreviation t, player_id, SUM(minutes_played) m
                       FROM nba_player_stats WHERE season_year='2025-26'
                       GROUP BY team_abbreviation, player_id""")
    by = {}
    for _, r in rows.iterrows():
        by.setdefault(r["t"], {})[str(r["player_id"])] = r["m"] / 82.0
    return by


def team_profile(roster_mpg, dims):
    num = {d: 0.0 for d in DIMS}
    wsum = 0.0
    for pid, mpg in roster_mpg.items():
        d = dims.get(pid)
        if not d:
            continue
        num = {k: num[k] + mpg * d[k] for k in DIMS}
        wsum += mpg
    return {k: (num[k] / wsum if wsum else 0.5) for k in DIMS}


def saturation_measures(roster_mpg, imp, dims):
    prof = team_profile(roster_mpg, dims)
    skill_surplus = sum(max(0.0, prof[d] - BENCHMARK[d]) for d in DIMS)
    # depth surplus: positive net impact beyond the top-5 by impact
    contrib = []
    for pid, mpg in roster_mpg.items():
        d = imp.get(pid)
        if d:
            contrib.append(((mpg / 48.0), d["off"] - d["def"]))
    contrib.sort(key=lambda c: -c[1])
    depth_surplus = sum(w * max(0.0, net) for (w, net) in contrib[5:])
    # usage overlap: stacked on-ball creation above median
    usage_overlap = 0.0
    for pid, mpg in roster_mpg.items():
        d = dims.get(pid)
        if d:
            onball = 0.5 * (d["hc_creation"] + d["secondary_playmaking"])
            usage_overlap += (mpg / 48.0) * max(0.0, onball - 0.5)
    return {"skill_surplus": skill_surplus, "depth_surplus": depth_surplus,
            "usage_overlap": usage_overlap}


def actual_2025_26():
    rs = db.query("""SELECT DISTINCT game_id FROM nba_games
                     WHERE season_type='Regular Season' AND (season_id % 10000)=2025""")
    ids = list(rs["game_id"])
    net = db.query("""SELECT team_tricode t, AVG(net_rating) net FROM nba_team_advanced_stats
                      WHERE game_id = ANY(%s) GROUP BY team_tricode""", (ids,))
    w = db.query("""SELECT team_abbreviation t, SUM(CASE WHEN wl='W' THEN 1 ELSE 0 END) w
                    FROM nba_games WHERE season_type='Regular Season' AND (season_id % 10000)=2025
                    GROUP BY team_abbreviation""")
    return dict(zip(net["t"], net["net"].astype(float))), dict(zip(w["t"], w["w"].astype(float)))


def calibrate_and_validate():
    imp = A.load_impacts()
    dims = load_dims()
    rost = rosters_2025_26()
    actual_net, actual_w = actual_2025_26()

    teams = [t for t in rost if t in actual_net]
    rolled = {t: A.rollup(rost[t], imp, "rs") for t in teams}
    mean_net = np.mean([rolled[t]["net"] for t in teams])
    sat = {t: saturation_measures(rost[t], imp, dims) for t in teams}

    # A's residual = rolled (centered) minus actual; positive = overshoot
    resid = {t: (rolled[t]["net"] - mean_net) - actual_net[t] for t in teams}
    r = np.array([resid[t] for t in teams])

    print("=== Component B calibration: which structural saturation explains A's overshoot? ===")
    best = None
    for meas in ("skill_surplus", "depth_surplus", "usage_overlap"):
        s = np.array([sat[t][meas] for t in teams])
        sc = (s - s.mean())
        corr = np.corrcoef(sc, r)[0, 1]
        slope = np.polyfit(sc, r, 1)[0]
        print(f"  {meas:14}: corr(saturation, overshoot) = {corr:+.3f}  slope = {slope:+.3f}")
        if best is None or abs(corr) > abs(best[1]):
            best = (meas, corr, slope, s.mean())
    meas, corr, slope, smean = best
    SIGNAL_GATE = 0.40        # only impose a team penalty if a measure really explains the overshoot
    use_penalty = abs(corr) >= SIGNAL_GATE
    if use_penalty:
        print(f"  -> using {meas} (corr {corr:+.3f} clears the {SIGNAL_GATE} gate), penalty slope {slope:+.3f}")
    else:
        print(f"  -> NO measure clears the {SIGNAL_GATE} gate (best |corr|={abs(corr):.2f}). "
              f"After the defensive reweighting, A shows NO systematic team-level overshoot, so B imposes "
              f"NO baseline team penalty (forcing one overcorrects SAS/NYK). Redundancy/fit is applied at "
              f"the MARGIN for roster changes instead (marginal_fit, below), which is where it is grounded.")

    def adjusted(t):
        pen = (slope * (sat[t][meas] - smean)) if use_penalty else 0.0
        return (rolled[t]["net"] - mean_net) - pen

    teams_sorted = sorted(teams, key=lambda t: -adjusted(t))
    xa = np.array([adjusted(t) for t in teams])
    ya = np.array([actual_net[t] for t in teams])
    yw = np.array([actual_w[t] for t in teams])
    b1, b0 = np.polyfit(xa, ya, 1)
    r_net = np.corrcoef(xa, ya)[0, 1]
    r_win = np.corrcoef(xa, yw)[0, 1]
    pred_w = 41 + (b0 + b1 * xa) * 2.7
    mae_w = np.mean(np.abs(pred_w - yw))

    # before/after on the previously-overshooting teams
    def safe(x): return str(x).encode("ascii", "replace").decode()
    print(f"\n=== A+B re-validation (2025-26) ===")
    print(f"corr(adjusted net, actual) = {r_net:.3f} (A alone was 0.964) | corr wins {r_win:.3f} | wins MAE {mae_w:.1f}")
    print(f"\n{'team':5}{'A_roll':>8}{'B_adj':>8}{'actual':>8}{'method_unc':>11}")
    for t in ["OKC", "SAS", "NYK", "BOS", "DET", "MIN", "WAS", "BKN"]:
        if t in teams:
            print(f"{safe(t):5}{rolled[t]['net']-mean_net:>8.2f}{adjusted(t):>8.2f}"
                  f"{actual_net[t]:>8.2f}{rolled[t]['method_uncertainty']:>11.2f}")
    return meas, slope, smean


def project_rotation(roster_mpg, mode="playoff"):
    """Playoff rotations tighten to ~9; bench minutes redistribute to the top group."""
    if mode != "playoff":
        return dict(roster_mpg)
    top = sorted(roster_mpg.items(), key=lambda kv: -kv[1])[:PLAYOFF_ROTATION]
    tot = sum(m for _, m in top) or 1
    return {p: m / tot * 240.0 for p, m in top}


def marginal_fit(team_profile, player_dims, cap=1.5):
    """Bounded net adjustment for ADDING a player to a team: complementary (fills a
    dimension where the team is below the contender benchmark) earns a bonus,
    redundant (stacks a dimension where the team is already in surplus) a penalty.
    Same dimensions and benchmark as the need-fit layer, so a duplicate skill is
    worth less than a complementary one in both places. Bounded, structural, not a
    free parameter. This is where B's redundancy lives, since the league shows no
    systematic redundancy to subtract at the baseline team level."""
    adj = 0.0
    for d in DIMS:
        gap = BENCHMARK[d] - team_profile[d]      # + = team needs this dimension
        provision = player_dims[d] - 0.5          # + = player provides it
        adj += gap * provision
    return max(-cap, min(cap, round(adj * 3.0, 2)))


if __name__ == "__main__":
    calibrate_and_validate()
    # demo: marginal fit of a rim protector vs a redundant wing into the both-out Wolves
    dims = load_dims()
    rost = rosters_2025_26()
    both_out = {p: m for p, m in rost["MIN"].items() if p not in ("203944", "203497")}
    prof = team_profile(both_out, dims)
    name_to_id = {r["player_name"]: r["player_id"]
                  for r in csv.DictReader(open(os.path.join(DATA, "player_value.csv"), encoding="utf-8"))}
    print("\n=== marginal_fit demo: candidate added to the both-out Wolves ===")
    for name in ["Walker Kessler", "Clint Capela", "Kawhi Leonard", "Lauri Markkanen"]:
        vid = next((v for k, v in name_to_id.items() if name.lower() in k.lower()), None)
        if vid and vid in dims:
            print(f"  add {name:16}: marginal_fit = {marginal_fit(prof, dims[vid]):+.2f} net")

#!/usr/bin/env python3
"""
build_team_ratings.py  -- Championship layer, Component A.

Turn a roster into a team strength. Rolls the per-player CONSENSUS impact (the
externally triangulated RAPM+BBR spine) into team offensive, defensive, and net
ratings, in two modes:
  - regular-season mode: actual rotation minutes. Used for seeding.
  - playoff mode: rotation tightened to the top 9 (bench minutes redistributed the
    way playoff rotations shrink) and offense reweighted by each player's
    playoff-translation read. A defined, documented transform, not a knob.

Team net (per 100, vs an average team) = sum over the rotation of
(minutes/48) x player net impact, then centered to the league mean so it is
expressed relative to an average team. Intervals carry through from the player
posterior SDs. Nothing collapses to a bare point.

Validation (the gate before anything downstream): roll up the actual 2025-26
rosters and check the result reproduces the real 2025-26 net ratings and win
totals within reason (ordering + calibrated scale). A and B must pass this before
C/D/E are built.

    python build_team_ratings.py            # runs the 2025-26 validation
"""

import os
import sys
import csv
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
POSTMORTEM = os.path.abspath(os.path.join(HERE, "..", "..", "postmortem"))
DATA = os.path.join(HERE, "..", "data")
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(POSTMORTEM, ".env"))
except ImportError:
    pass
sys.path.insert(0, POSTMORTEM)
from lib import db  # noqa: E402

PLAYOFF_OFF_MULT = {"holds_up": 1.05, "neutral": 1.0, "slips": 0.92,
                    "insufficient_po_sample": 0.98, "": 1.0}
PLAYOFF_ROTATION = 9            # playoff rotations tighten to ~9


def load_impacts():
    """player_id -> dict(off, def, off_sd, def_sd, playoff_read). Consensus spine."""
    imp = {}
    for r in csv.DictReader(open(os.path.join(DATA, "player_value.csv"), encoding="utf-8")):
        def f(k, d=0.0):
            v = (r.get(k) or "").strip()
            try:
                return float(v)
            except ValueError:
                return d
        imp[r["player_id"]] = {
            "off": f("consensus_off", f("off_rapm")), "def": f("consensus_def", f("def_rapm")),
            "off_sd": f("off_sd", 1.2), "def_sd": f("def_sd", 1.2),
            "def_div": f("def_divergence", 0.0),   # RAPM-vs-box disagreement on defense
            "read": r.get("translation_read", ""),
        }
    return imp


def rollup(roster_mpg, imp, mode="rs"):
    """roster_mpg: {player_id: minutes_per_game}. Returns off/def/net + net_sd
    (uncentered; the caller centers net to the league mean)."""
    players = sorted(roster_mpg.items(), key=lambda kv: -kv[1])
    if mode == "playoff":
        players = players[:PLAYOFF_ROTATION]
        tot = sum(m for _, m in players) or 1
        players = [(p, m / tot * 240.0) for p, m in players]   # rescale to a full game
    off = dff = var = mdiv = dcontrib = 0.0
    for pid, mpg in players:
        d = imp.get(pid)
        if not d:
            continue
        w = mpg / 48.0
        omult = PLAYOFF_OFF_MULT.get(d["read"], 1.0) if mode == "playoff" else 1.0
        off += w * d["off"] * omult
        dff += w * d["def"]
        var += (w ** 2) * (d["off_sd"] ** 2 + d["def_sd"] ** 2)
        # method_uncertainty is weighted by each player's share of the team DEFENSIVE
        # RATING (|w * def|), not by raw minutes. The team's defensive read is only as
        # uncertain as the players who actually make up its defense: a rim-anchored team
        # (MIN/Gobert, SAS/Wembanyama) whose whole defensive rating rests on one
        # method-divergent player should carry that player's uncertainty, not have it
        # averaged down by nine box-legible role players. Minutes-weighting did the
        # latter and put SAS at the bottom of the field, which was wrong.
        cw = abs(w * d["def"])
        mdiv += cw * d["def_div"]
        dcontrib += cw
    # Note the divergence is player-specific, not a "rim protector" flag: Wembanyama's
    # def_divergence (1.56) is half Gobert's (3.17) because the box SEES Wemby's defense
    # (blocks/steals/rebounds -> DBPM +3.56) so RAPM and the box corroborate him, while
    # Gobert's deterrence is mostly invisible to the box (DBPM +1.26). Both keep their
    # elite point estimate; Wemby's just carries less uncertainty, correctly.
    method_unc = (mdiv / dcontrib) if dcontrib else 0.0
    return {"off": off, "def": dff, "net": off - dff, "net_sd": var ** 0.5,
            "method_uncertainty": round(method_unc, 2)}


def team_ratings_for_season(season_year, imp, mode="rs"):
    """Build each team's rollup from a season's actual rosters + minutes."""
    rows = db.query("""SELECT team_abbreviation t, player_id, SUM(minutes_played) m,
                              COUNT(DISTINCT game_id) g
                       FROM nba_player_stats WHERE season_year=%s
                       GROUP BY team_abbreviation, player_id""", (season_year,))
    by_team = {}
    for _, r in rows.iterrows():
        by_team.setdefault(r["t"], {})[str(r["player_id"])] = r["m"] / 82.0
    out = {t: rollup(mpg, imp, mode) for t, mpg in by_team.items()}
    mean_net = np.mean([v["net"] for v in out.values()])
    for v in out.values():
        v["net_centered"] = v["net"] - mean_net          # relative to league-average team
    return out


def validate_2025_26(imp):
    roll = team_ratings_for_season("2025-26", imp, mode="rs")
    rs_ids = db.query("""SELECT DISTINCT game_id FROM nba_games
                         WHERE season_type='Regular Season' AND (season_id % 10000)=2025""")
    ids = list(rs_ids["game_id"])
    act_net = db.query("""SELECT team_tricode t, AVG(net_rating) net FROM nba_team_advanced_stats
                          WHERE game_id = ANY(%s) GROUP BY team_tricode""", (ids,))
    act_w = db.query("""SELECT team_abbreviation t, SUM(CASE WHEN wl='W' THEN 1 ELSE 0 END) w
                        FROM nba_games WHERE season_type='Regular Season' AND (season_id % 10000)=2025
                        GROUP BY team_abbreviation""")
    A = dict(zip(act_net["t"], act_net["net"].astype(float)))
    W = dict(zip(act_w["t"], act_w["w"].astype(float)))
    teams = [t for t in roll if t in A]
    x = np.array([roll[t]["net_centered"] for t in teams])
    ya = np.array([A[t] for t in teams])
    yw = np.array([W[t] for t in teams])

    # calibrate rolled -> actual net (ridge shrinks the spread; fit the scale)
    b1, b0 = np.polyfit(x, ya, 1)
    pred_net = b0 + b1 * x
    r_net = np.corrcoef(x, ya)[0, 1]
    r_win = np.corrcoef(x, yw)[0, 1]
    # net -> wins via the standard ~2.7 wins per net point around .500
    pred_w = 41 + pred_net * 2.7
    mae_w = np.mean(np.abs(pred_w - yw))

    def safe(s): return str(s).encode("ascii", "replace").decode()
    print(f"=== Component A validation, 2025-26 (RS mode), {len(teams)} teams ===")
    print(f"corr(rolled net, actual net) = {r_net:.3f}   corr(rolled net, actual wins) = {r_win:.3f}")
    print(f"calibration: actual_net ~ {b0:+.2f} + {b1:.2f} * rolled_net   (ridge compresses spread, b1>1 expected)")
    print(f"predicted-wins MAE = {mae_w:.1f} games")
    order = sorted(teams, key=lambda t: -roll[t]["net_centered"])
    print(f"\n{'team':5}{'rolled':>8}{'pred_net':>9}{'act_net':>8}{'pred_W':>7}{'act_W':>6}")
    for t in order[:6] + order[-4:]:
        pn = b0 + b1 * roll[t]["net_centered"]
        print(f"{safe(t):5}{roll[t]['net_centered']:>8.2f}{pn:>9.1f}{A[t]:>8.1f}{41+pn*2.7:>7.0f}{W[t]:>6.0f}")
    return r_net, r_win


if __name__ == "__main__":
    imp = load_impacts()
    validate_2025_26(imp)

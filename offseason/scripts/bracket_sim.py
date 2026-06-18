#!/usr/bin/env python3
"""
bracket_sim.py  -- Championship layer, Component E.

The bracket Monte Carlo. Turns a league of team strengths into title odds, round
advancement, and the deep-round matchup distribution, by simulating the regular
season for seeds and resolving every playoff series through Component D.

THE SURVIVORSHIP MODEL (the principled fix for the late-round bias D flagged).
Each simulation draws each team's TRUE playoff strength once: playoff_net = RS_net +
eps, eps ~ N(0, sigma_t). Series are then resolved on the drawn strengths. Teams that
advance tend to have drawn favorable eps, so deep-round opponents are positively
selected and late-round favorites compress on their own, with no round dummy. sigma_t
combines a league-wide unobserved-playoff-quality term (sigma_unobs, the knob the
de-vigged boards calibrate) with each team's own method_uncertainty (the RAPM-vs-box
defensive disagreement), so a rim-anchored, method-divergent team (MIN 1.84) swings
wider than a box-legible one (DET 0.48). sigma_unobs governs how concentrated title
odds are: more noise, more upsets, a wider title distribution.

TWO CALIBRATED MAPPINGS (build_e_calibration.py fits them, writes e_calibration_params.json):
  - SCALE: hot rotation-rollup net -> RS-scale net (deflation alpha/beta), and RS net
    -> wins (wins_a/wins_b, with residual sigma_record). Anchored on actual win totals.
  - SHAPE: sigma_unobs. Anchored on the de-vigged preseason title boards.

SCALE CONTRACT (inherited from D): everything the resolver sees is on the actual RS
per-100 net scale. The deflation puts the hot top-10 rollups onto that scale first.

    python bracket_sim.py        # builds + simulates the 2026-27 baseline league
"""

import os
import sys
import csv
import json
import math
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
POSTMORTEM = os.path.abspath(os.path.join(HERE, "..", "..", "postmortem"))
DATA = os.path.join(HERE, "..", "data")
OUTDIR = os.path.join(HERE, "..", "outputs")
sys.path.insert(0, POSTMORTEM)
sys.path.insert(0, HERE)
import series_resolver as D                 # noqa: E402
import build_team_ratings as A              # noqa: E402
import build_rotation_model as B            # noqa: E402
from build_series_calibration import TEAM_CONF  # noqa: E402

E_PARAMS_PATH = os.path.join(DATA, "e_calibration_params.json")
ROLE_MPG = {"starter": 34, "sixth": 26, "rotation": 18, "deep": 9}

# How much each team's method_uncertainty widens its playoff-strength draw, in
# quadrature with the league-wide sigma_unobs. Structural (not a fitted knob): a team
# whose defensive rating the box and RAPM disagree on is genuinely less predictable.
MUNC_W = 0.35

# Full 30-team name -> tricode (current franchises), for parsing the preseason boards.
NAME_TO_ABBR = {
    "Atlanta Hawks": "ATL", "Boston Celtics": "BOS", "Brooklyn Nets": "BKN",
    "Charlotte Hornets": "CHA", "Chicago Bulls": "CHI", "Cleveland Cavaliers": "CLE",
    "Dallas Mavericks": "DAL", "Denver Nuggets": "DEN", "Detroit Pistons": "DET",
    "Golden State Warriors": "GSW", "Houston Rockets": "HOU", "Indiana Pacers": "IND",
    "Los Angeles Clippers": "LAC", "Los Angeles Lakers": "LAL", "Memphis Grizzlies": "MEM",
    "Miami Heat": "MIA", "Milwaukee Bucks": "MIL", "Minnesota Timberwolves": "MIN",
    "New Orleans Pelicans": "NOP", "New York Knicks": "NYK", "Oklahoma City Thunder": "OKC",
    "Orlando Magic": "ORL", "Philadelphia 76ers": "PHI", "Phoenix Suns": "PHX",
    "Portland Trail Blazers": "POR", "Sacramento Kings": "SAC", "San Antonio Spurs": "SAS",
    "Toronto Raptors": "TOR", "Utah Jazz": "UTA", "Washington Wizards": "WAS",
}

_EP = None


def load_e_params():
    global _EP
    if _EP is None:
        if os.path.exists(E_PARAMS_PATH):
            _EP = json.load(open(E_PARAMS_PATH, encoding="utf-8"))
        else:
            _EP = {"alpha": 0.0, "beta": 1.0, "wins_a": 41.0, "wins_b": 2.7,
                   "sigma_record": 5.0, "sigma_unobs": 3.0, "source": "fallback"}
    return _EP


# ---------------------------------------------------------------------------
# Rollups: rotation -> hot net -> RS-scale net (with uncertainty carried).
# ---------------------------------------------------------------------------
def roster_to_mpg(rotation):
    raw = {p["nba_player_id"]: ROLE_MPG.get(p["role"], 12) for p in rotation}
    tot = sum(raw.values()) or 1
    return {pid: m / tot * 240.0 for pid, m in raw.items()}


def deflate(hot_net):
    p = load_e_params()
    return p["alpha"] + p["beta"] * hot_net


def strength_from_rotation(rotation, imp, mode="rs"):
    """Rotation (role-tagged) -> RS-scale net rating, carrying net_sd + method_unc."""
    mpg = roster_to_mpg(rotation)
    roll = A.rollup(mpg, imp, mode)
    return {"net_hot": roll["net"], "net": deflate(roll["net"]),
            "net_sd": roll["net_sd"], "munc": roll["method_uncertainty"]}


# ---------------------------------------------------------------------------
# De-vig and board parsing.
# ---------------------------------------------------------------------------
def american_to_prob(odds):
    o = float(str(odds).replace("+", ""))
    return (100.0 / (o + 100.0)) if o > 0 else (-o / (-o + 100.0))


def parse_board(path):
    """Returns list of {team, abbr, title_odds_american, implied, ou_wins, result_w}."""
    rows = []
    for r in csv.reader(open(path, encoding="utf-8")):
        if not r or r[0] == "Team" or r[0].strip() == "":
            continue
        name, odds = r[0].strip(), r[1].strip()
        ou = float(r[3]) if len(r) > 3 and r[3].strip() else None
        abbr = NAME_TO_ABBR.get(name)
        rows.append({"team": name, "abbr": abbr, "odds": odds,
                     "implied_raw": american_to_prob(odds), "ou": ou})
    s = sum(x["implied_raw"] for x in rows)
    for x in rows:
        x["devig"] = x["implied_raw"] / s          # remove the vig
    return rows


# ---------------------------------------------------------------------------
# The simulation.
# ---------------------------------------------------------------------------
def _seed_bracket(seeds_by_conf):
    """Fixed 1-8 bracket per conference. Returns the R1 pairings (hi, lo) per conf."""
    out = {}
    for conf, order in seeds_by_conf.items():
        # order[0]=1 seed ... order[7]=8 seed
        s = {i + 1: order[i] for i in range(min(8, len(order)))}
        out[conf] = [(s[1], s[8]), (s[4], s[5]), (s[3], s[6]), (s[2], s[7])]
    return out


def simulate_league(strengths, n_sims=10000, seed=12345, use_overlay=False):
    """strengths: {abbr: {net, net_sd, munc, conf, profile(optional)}}.
    Returns aggregated title / conf / round-advance probs and the matchup table."""
    p = load_e_params()
    rng = np.random.default_rng(seed)
    teams = list(strengths)
    base_net = np.array([strengths[t]["net"] for t in teams])
    munc = np.array([strengths[t].get("munc", 0.0) for t in teams])
    sd = np.array([strengths[t].get("net_sd", 0.0) for t in teams])
    conf = {t: strengths[t]["conf"] for t in teams}
    prof = {t: strengths[t].get("profile") for t in teams}
    # per-team playoff-strength sigma: league noise + method uncertainty (+ tiny posterior sd)
    sigma_t = np.sqrt(p["sigma_unobs"] ** 2 + (MUNC_W * munc) ** 2 + (0.15 * sd) ** 2)
    sig_rec = p["sigma_record"]
    wa, wb = p["wins_a"], p["wins_b"]

    idx = {t: i for i, t in enumerate(teams)}
    title = {t: 0 for t in teams}
    confwin = {t: 0 for t in teams}
    reach = {t: {2: 0, 3: 0, 4: 0, "champ": 0} for t in teams}   # reach R2/CF/Finals/title
    # matchup table: (a,b,round) -> [meetings, a_wins] with a<b alphabetical
    mt = {}

    def resolve(hi, lo, dnet, sim_wins):
        """hi has home court (higher seed within conf; better record in Finals)."""
        pf = prof[hi] if use_overlay else None
        po = prof[lo] if use_overlay else None
        pr = D.series_win_prob(dnet[hi], dnet[lo], True, pf, po)
        win_hi = rng.random() < pr
        a, b = sorted((hi, lo))
        rec = mt.setdefault((a, b), [0, 0])
        rec[0] += 1
        winner = hi if win_hi else lo
        if winner == a:
            rec[1] += 1
        return winner

    for _ in range(n_sims):
        eps = rng.normal(0.0, sigma_t)
        dnet = {t: base_net[idx[t]] + eps[idx[t]] for t in teams}
        sim_wins = {t: wa + wb * base_net[idx[t]] + rng.normal(0.0, sig_rec) for t in teams}
        # seeds: top 8 by simulated wins within conference
        seeds_by_conf = {}
        for c in ("E", "W"):
            ct = sorted([t for t in teams if conf[t] == c], key=lambda t: -sim_wins[t])
            seeds_by_conf[c] = ct[:8]
        r1 = _seed_bracket(seeds_by_conf)
        conf_champs = {}
        for c in ("E", "W"):
            (a1, a8), (a4, a5), (a3, a6), (a2, a7) = r1[c]
            w18 = resolve(a1, a8, dnet, sim_wins); w45 = resolve(a4, a5, dnet, sim_wins)
            w36 = resolve(a3, a6, dnet, sim_wins); w27 = resolve(a2, a7, dnet, sim_wins)
            # mark R2 reach
            for t in (w18, w45, w36, w27):
                reach[t][2] += 1
            # semis: 1/8 side vs 4/5 side ; 2/7 side vs 3/6 side. higher seed (lower
            # record-rank within conf) hosts.
            def host(x, y):
                return (x, y) if sim_wins[x] >= sim_wins[y] else (y, x)
            sf1 = resolve(*host(w18, w45), dnet, sim_wins)
            sf2 = resolve(*host(w27, w36), dnet, sim_wins)
            for t in (sf1, sf2):
                reach[t][3] += 1
            cf = resolve(*host(sf1, sf2), dnet, sim_wins)
            reach[cf][4] += 1
            conf_champs[c] = cf
            confwin[cf] += 1
        ce, cw = conf_champs["E"], conf_champs["W"]
        champ = resolve(*( (ce, cw) if sim_wins[ce] >= sim_wins[cw] else (cw, ce) ),
                        dnet, sim_wins)
        title[champ] += 1
        reach[champ]["champ"] += 1

    out = {"n_sims": n_sims, "teams": {}}
    for t in teams:
        out["teams"][t] = {
            "net": round(strengths[t]["net"], 2), "munc": round(strengths[t].get("munc", 0), 2),
            "title": title[t] / n_sims, "conf": confwin[t] / n_sims,
            "r2": reach[t][2] / n_sims, "cf": reach[t][3] / n_sims, "finals": reach[t][4] / n_sims,
        }
    out["matchups"] = {f"{a}|{b}": {"meet": v[0] / n_sims, "a_wins_given_meet": (v[1] / v[0] if v[0] else None),
                                    "a": a, "b": b} for (a, b), v in mt.items()}
    return out


def conditional_series(team, strengths, use_overlay=True):
    """Direct (not sim-frequency) P(team wins a series) vs every other team, home court
    to the higher net. The clean 'if these two met' read for the deep-round eyeball.

    CAVEAT (gate v2): the resolver is ~5.7pp too favorite-confident in the smallest
    (0-2) net-gap bucket vs 1997-2025 history, and CF/Finals matchups have the smallest
    gaps, so simulated deep-round survival runs ~3pp hot. Treat a Wolves CF/Finals series
    probability here as a slight UPPER bound, and lean on the board-anchored title band
    rather than the round-by-round curve. Deliberately un-fixed (a round dummy overfits 50
    series); the variance overlay partly absorbs it."""
    res = {}
    tn = strengths[team]["net"]; tp = strengths[team].get("profile")
    for o in strengths:
        if o == team:
            continue
        on = strengths[o]["net"]; op = strengths[o].get("profile")
        hc = tn >= on
        if hc:
            p = D.series_win_prob(tn, on, True, tp if use_overlay else None, op if use_overlay else None)
        else:
            p = 1.0 - D.series_win_prob(on, tn, True, op if use_overlay else None, tp if use_overlay else None)
        res[o] = p
    return res


# ---------------------------------------------------------------------------
# Build the 2026-27 baseline league (all 30 teams).
# ---------------------------------------------------------------------------
# Teams with a GENUINE 2026-27 roster change (per opponent_rosters assumed_moves); they
# get a realigned move delta. Everyone else stands pat (per their own assumed_moves) and
# is anchored to measured 2025-26 net with delta=0, which is un-gameable and keeps the
# 60+ win teams (DET, SAS) at the top instead of riding role-tag-drift rollup noise.
MOVED = {"MIA", "MIN", "BOS"}
TATUM_DIMINISH = 0.5   # baseline Boston uses a diminished Year-1 Achilles-return Tatum (the
#                        default expectation); the variant explores healthy (1.0) and out (0.0).
# ORL's 2025-26 net (+0.49) is injury-suppressed (Banchero/Wagner missed time), so its
# realized net underrates a healthy roster. Anchor it to the healthy projected-roster
# rollup instead of the injured realized net, then regress like any expectation.
HEALTH_REBOUND = {"ORL"}

# Fix 2: returning-star health correction (see docs/trade_model_spec_untouchables_and_health.md).
# A star who missed all/most of 2025-26 and is expected back, on a team NOT in the projected
# (opponent_rosters) contender set. The gap-year net is the WRONG anchor: losing a franchise engine
# collapses the whole season (IND fell to -7.85, a tank, not the roster's true level), so anchoring
# on it understates a healthy roster ACROSS THE BOARD, not just at one position. Instead anchor on
# the team's PRE-INJURY net (the season before the lost one, when the star was healthy: IND made a
# Finals at +2.19), then apply the SAME post-Achilles diminish the BOS/Tatum baseline uses, removing
# (1 - TATUM_DIMINISH) of the returning star's marginal value. Visible via src="returning-star-health".
# BOS/Tatum itself is handled by MOVED + TATUM_DIMINISH and so is intentionally NOT listed here.
RETURNING_STARS = {
    "IND": {"player_id": "1630169", "pre_injury_year": 2024, "role": "starter"},   # Haliburton (Achilles)
}


def regress_to_expectation(net):
    """Realized net -> forward-looking expectation, the scale the title sim was calibrated
    on (persistence regression in build_e_calibration). Pulls overperformers (DET, SAS)
    back toward what the market would set their 2026-27 number at; a no-op (slope 1) only
    if the calibration is missing."""
    p = load_e_params()
    return p.get("persist_int", 0.0) + p.get("persist_slope", 1.0) * net


def _realigned_delta(proj_rot, act_rot, imp):
    """deflate(rollup(projected)) - deflate(rollup(actual realigned)), where the actual
    rotation's STAYERS (players also in the projected rotation) are re-tagged to their
    PROJECTED role so they carry identical minutes in both rollups and cancel exactly.
    This isolates the genuine roster change instead of conflating it with role-tag drift
    between the scout's rotation and the minutes-rank proxy. Stand-pat -> ~0 by design."""
    proj_roles = {p["nba_player_id"]: p["role"] for p in proj_rot}
    realigned = [{"nba_player_id": p["nba_player_id"], "role": proj_roles.get(p["nba_player_id"], p["role"])}
                 for p in act_rot]
    return (deflate(A.rollup(roster_to_mpg(proj_rot), imp, "rs")["net"])
            - deflate(A.rollup(roster_to_mpg(realigned), imp, "rs")["net"]))


def build_2026_27_league(imp):
    """All 30 teams on the RS net scale. Stand-pat teams (their own assumed_moves say so)
    sit at MEASURED 2025-26 net (delta 0). The three teams with a real roster change (MIA
    +Giannis, MIN -DiVincenzo, BOS Tatum-returns) get a realigned move delta; Boston's
    baseline applies a DIMINISHED Tatum (half the healthy delta). Proxy teams that lost a
    player to a contender (MIL -> Giannis) get that removal. Component C profiles supply the
    dimension vectors for the overlay only; the net comes from measured reality + the move."""
    import bracket_helpers as BH
    dims = B.load_dims()
    actual_net = BH.actual_team_net(2025)
    actual_rot = BH.actual_top_rotations("2025-26")
    op_profiles = {p["team"]: p["dimensions"] for p in
                   json.load(open(os.path.join(DATA, "opponent_profiles.json"), encoding="utf-8"))}
    opp = json.load(open(os.path.join(DATA, "opponent_rosters.json"), encoding="utf-8"))
    projected = {tm["team_abbr"]: tm["rotation"] for tm in opp}
    moved_players = {p["nba_player_id"] for rot in projected.values() for p in rot}

    strengths = {}
    for ab in actual_net:
        a25 = round(actual_net[ab], 2)
        rot = actual_rot.get(ab)
        if ab in MOVED:                                             # real roster change
            full = _realigned_delta(projected[ab], rot or [], imp)
            delta = TATUM_DIMINISH * full if ab == "BOS" else full
            proj_roll = A.rollup(roster_to_mpg(projected[ab]), imp, "rs")
            exp = regress_to_expectation(a25)
            strengths[ab] = {"net": round(exp + delta, 2), "net_sd": proj_roll["net_sd"],
                             "munc": proj_roll["method_uncertainty"], "conf": TEAM_CONF.get(ab, "W"),
                             "profile": op_profiles.get(ab), "src": "exp+move",
                             "delta": round(delta, 2), "full_delta": round(full, 2),
                             "exp": round(exp, 2), "actual25": a25}
        elif ab in HEALTH_REBOUND and ab in projected:              # injury-distorted last year
            healthy = deflate(A.rollup(roster_to_mpg(projected[ab]), imp, "rs")["net"])
            exp = regress_to_expectation(healthy)
            proj_roll = A.rollup(roster_to_mpg(projected[ab]), imp, "rs")
            strengths[ab] = {"net": round(exp, 2), "net_sd": proj_roll["net_sd"],
                             "munc": proj_roll["method_uncertainty"], "conf": TEAM_CONF.get(ab, "W"),
                             "profile": op_profiles.get(ab), "src": "health-rebound",
                             "delta": round(exp - regress_to_expectation(a25), 2),
                             "exp": round(exp, 2), "actual25": a25}
        elif ab in RETURNING_STARS and ab not in MOVED:             # star returning from a lost season
            rs = RETURNING_STARS[ab]
            base_rot = rot or []
            present = {p["nba_player_id"] for p in base_rot}
            inj_rot = base_rot + ([{"nba_player_id": rs["player_id"], "role": rs["role"]}]
                                  if rs["player_id"] not in present else [])
            # the returning star's full marginal value (talent rollup with vs without him)
            base_net = deflate(A.rollup(roster_to_mpg(base_rot), imp, "rs")["net"]) if base_rot else 0.0
            star_lift = deflate(A.rollup(roster_to_mpg(inj_rot), imp, "rs")["net"]) - base_net
            # anchor on the PRE-INJURY net (healthy season), then dock the post-Achilles diminish, the
            # same fraction the BOS/Tatum baseline applies: remove (1 - TATUM_DIMINISH) of his value.
            pre_net = BH.actual_team_net(rs["pre_injury_year"]).get(ab, a25)
            exp = regress_to_expectation(pre_net)
            net = exp - (1.0 - TATUM_DIMINISH) * star_lift
            proj_roll = A.rollup(roster_to_mpg(inj_rot), imp, "rs")
            strengths[ab] = {"net": round(net, 2), "net_sd": proj_roll["net_sd"],
                             "munc": proj_roll["method_uncertainty"], "conf": TEAM_CONF.get(ab, "W"),
                             "profile": BH.team_dim_profile(inj_rot, dims),
                             "src": "returning-star-health",
                             "delta": round(net - regress_to_expectation(a25), 2),
                             "star_lift": round(star_lift, 2), "pre_injury_net": round(pre_net, 2),
                             "exp": round(exp, 2), "actual25": a25}
        elif ab in projected:                                       # stand-pat contender
            roll = A.rollup(roster_to_mpg(rot), imp, "rs") if rot else None
            exp = regress_to_expectation(a25)
            strengths[ab] = {"net": round(exp, 2), "net_sd": 0.0,
                             "munc": roll["method_uncertainty"] if roll else 0.0,
                             "conf": TEAM_CONF.get(ab, "W"), "profile": op_profiles.get(ab),
                             "src": "exp standpat", "delta": 0.0, "exp": round(exp, 2), "actual25": a25}
        else:                                                       # proxy (non-contender)
            kept = [p for p in rot if p["nba_player_id"] not in moved_players] if rot else []
            removal = 0.0
            if rot and kept and len(kept) < len(rot):               # lost a player to a contender
                removal = (deflate(A.rollup(roster_to_mpg(kept), imp, "rs")["net"])
                           - deflate(A.rollup(roster_to_mpg(rot), imp, "rs")["net"]))
            roll = A.rollup(roster_to_mpg(rot), imp, "rs") if rot else None
            exp = regress_to_expectation(a25)
            strengths[ab] = {"net": round(exp + removal, 2), "net_sd": 0.0,
                             "munc": roll["method_uncertainty"] if roll else 0.0,
                             "conf": TEAM_CONF.get(ab, "W"),
                             "profile": BH.team_dim_profile(rot, dims) if rot else None,
                             "src": "exp standpat" + (" (-moved)" if removal else ""),
                             "delta": round(removal, 2), "exp": round(exp, 2), "actual25": a25}
    return strengths


def _fmt_pct(x):
    return f"{x*100:5.1f}%"


def main():
    p = load_e_params()
    imp = A.load_impacts()
    print(f"=== Component E baseline, 2026-27 (sigma_unobs={p.get('sigma_unobs')}, "
          f"deflation {p.get('alpha')}+{p.get('beta')}*hot, wins={p.get('wins_a')}+{p.get('wins_b')}*net) "
          f"[{p.get('source')}] ===")
    strengths = build_2026_27_league(imp)
    res = simulate_league(strengths, n_sims=20000, use_overlay=True)
    order = sorted(res["teams"], key=lambda t: -res["teams"][t]["title"])

    def safe(s): return str(s).encode("ascii", "replace").decode()
    print(f"\n{'team':5}{'act25':>7}{'delta':>7}{'net26':>8}{'munc':>6}{'title':>8}{'conf':>8}{'CF':>8}")
    for t in order[:16]:
        d = res["teams"][t]; s = strengths[t]
        print(f"{safe(t):5}{s.get('actual25',0):>7.2f}{s.get('delta',0):>+7.2f}{d['net']:>8.2f}"
              f"{d['munc']:>6.2f}{_fmt_pct(d['title']):>8}{_fmt_pct(d['conf']):>8}{_fmt_pct(d['cf']):>8}")
    print(f"  (title sums to {sum(res['teams'][t]['title'] for t in res['teams'])*100:.0f}%)")

    # MIN deep-round read
    print("\n=== MIN deep-round read ===")
    m = res["teams"]["MIN"]
    print(f"MIN net {m['net']:.2f} (munc {m['munc']:.2f}) | title {_fmt_pct(m['title'])} "
          f"conf {_fmt_pct(m['conf'])} reach-CF {_fmt_pct(m['cf'])} reach-R2 {_fmt_pct(m['r2'])}")
    cond = conditional_series("MIN", strengths, use_overlay=True)
    print("\n  P(MIN wins a series) vs each contender: POINT (no survivorship) vs SIM-given-they-meet")
    print(f"  {'opp':5}{'net':>8}{'point%':>9}{'sim-meet%':>11}{'meet freq':>11}")
    for o in sorted(cond, key=lambda x: -res["teams"][x]["net"])[:11]:
        key = "|".join(sorted(("MIN", o)))
        mm = res["matchups"].get(key)
        if mm:
            sim_min = mm["a_wins_given_meet"] if mm["a"] == "MIN" else (1 - mm["a_wins_given_meet"])
            print(f"  {safe(o):5}{strengths[o]['net']:>+8.2f}{_fmt_pct(cond[o]):>9}"
                  f"{_fmt_pct(sim_min):>11}{_fmt_pct(mm['meet']):>11}")


if __name__ == "__main__":
    main()

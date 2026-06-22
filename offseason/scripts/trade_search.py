#!/usr/bin/env python3
"""
trade_search.py  -- THE OPTIMAL-TRADE BOARD (Pass 1: two-team, every partner).

For each of the 29 partners, search legal two-team trades and return the one that maximizes
MIN's risk-adjusted championship dP on the aged spine, SUBJECT TO the partner accepting it
(partner_acceptance.py: surplus / need / cap-relief, from data). The board is ranked across
all 29, with explicit "no realistic deal" verdicts where nothing clears both sides.

Acceptance scope: partner_acceptance is Minnesota-acquisition-specific with HAND-SET Phase 2-C
coefficients, not calibrated against realized trades (a realized-trade backtest proved it does not
generalize, 16% recall). See docs/acceptance_model_scope_and_limitation.md. The board's strong deals
clear regardless; read the MARGINAL rankings with that un-calibrated caveat.

Cost discipline (each Monte Carlo _sim is seconds, no caching) -> three tiers:
  Tier 0 (free): enumerate MIN outbound packages x partner give-back combos; two-sided
                 feasibility gate + partner acceptance + a cheap MIN net-delta proxy (the
                 apply_trade rollup, no sim) + the 2027 flex-state classifier. Keep top-K/team.
  Tier 1 (1 sim/survivor): central consensus dP at sigma 5.5, reduced NS. Best legal,
                 accepted, positive deal per partner.
  Tier 2 (full): four views (consensus/box/rapm + DARKO where available) + risk-adjusted EV
                 with availability band + gauntlet, NS high, for each team winner + near-misses.

  python trade_search.py [--partners ATL,UTA,...] [--ns 2500] [--tier2-ns 6000] [--topk 4]
"""

import os
import sys
import csv
import copy
import re
import argparse
import itertools
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
sys.path.insert(0, HERE)
import build_team_ratings as A          # noqa: E402
import build_rotation_model as B        # noqa: E402
import bracket_helpers as BH            # noqa: E402
import bracket_sim as E                 # noqa: E402
import apply_trade as F                 # noqa: E402
import risk_overlay as G                # noqa: E402
import age_curve as AC                  # noqa: E402
import evaluate_move as EM              # noqa: E402
import partner_acceptance as PA         # noqa: E402

# -------- MIN config: off-limits, tradable pieces, base rotation, sweetener inventory -------- #
OFF_LIMITS = {"1630162", "1630183", "1642866"}      # Edwards, McDaniels, Beringer
MIN = {"Edwards": "1630162", "Dosunmu": "1630245", "McDaniels": "1630183", "Randle": "203944",
       "Gobert": "203497", "Naz": "1629675", "Conley": "201144", "Shannon": "1630545",
       "Beringer": "1642866", "Phillips": "1641763", "Clark": "1641740"}

# tradable salary-matchers and filler (name -> (pid, salary, kicker, role_in_base))
MIN_PIECES = {
    "Randle":  (MIN["Randle"],  33_333_334, 0.0,   "starter"),
    "Gobert":  (MIN["Gobert"],  36_500_000, 0.075, "starter"),
    "Naz":     (MIN["Naz"],     23_333_333, 0.0,   "sixth"),
    "Shannon": (MIN["Shannon"],  2_800_000, 0.0,   "rotation"),
    "Phillips":(MIN["Phillips"], 2_400_000, 0.0,   "deep"),
    "Clark":   (MIN["Clark"],    2_300_000, 0.0,   "deep"),
}
# canonical 2026-27 MIN rotation (Dosunmu re-signed, DiVincenzo torn-Achilles out): role-tagged
MIN_BASE_ROT = [("Edwards", "starter"), ("Dosunmu", "starter"), ("McDaniels", "starter"),
                ("Randle", "starter"), ("Gobert", "starter"), ("Naz", "sixth"),
                ("Conley", "rotation"), ("Shannon", "rotation"), ("Beringer", "deep"),
                ("Phillips", "deep")]

# MIN sweetener inventory: asset-points (same currency as partner_acceptance). Greedy cheapest-first.
# The incoming UTA firsts (2027/2029) are HELD OUT of the live search: they carry protection +
# Stepien conditions that must be read per deal, so they cannot be spent by default. The sweetener
# bills are computed on MIN's OWN, unconditioned chips only (2026 slot, 2028 + 2033 own firsts,
# seconds). A deal that can only be financed with a UTA first triggers the per-deal conditional read.
MIN_PICKS = [("a 2nd-round pick", 0.7), ("a 2nd-round pick", 0.7),
             ("the 2026 first (slot locked draft night)", 3.5),
             ("the 2033 own first", 3.5), ("the 2028 own first", 5.0)]
# held pending a per-deal Stepien + protection-window read (NOT used by default):
HELD_UTA_PICKS = [("the re-routed UTA 2027 first (conditional)", 3.0),
                  ("the re-routed UTA 2029 first (conditional)", 3.0)]
MIN_CHEST_PTS = sum(p for _, p in MIN_PICKS)         # MIN's OWN, spendable chest (for reference)
# The most MIN will rationally attach to ONE deal: ~two premium firsts + a second. A deal that
# needs more than this to win acceptance is NOT a realistic deal (it is a no-deal / near-miss).
MAX_SWEETENER_PTS = 8.5

# MIN's own scenario need (which exit-state need vector to read when MIN sheds a big)
MIN_NEED_BY_OUT = {frozenset(): "status_quo", frozenset({"Randle"}): "randle_out",
                   frozenset({"Gobert"}): "gobert_out", frozenset({"Randle", "Gobert"}): "both_out"}

# ------------------------------- Fix 1: partner-side untouchables ---------------------------- #
# The partner-side mirror of MIN's OFF_LIMITS, for the other 29 teams (see
# docs/trade_model_spec_untouchables_and_health.md). The data gate untouchable() below is
# superstar-calibrated, so reported-core role players on mid salaries clear it and the search
# surfaces fantasy deals (e.g. Nembhard + Toppin for Randle). This list closes that hole.
#   "hard"        = never offered (unioned with the data gate; only ever ADDS exclusions).
#   "speculative" = not dropped, but force-tagged Speculative (the AD/Kyrie conditional-on-pivot
#                   path), so it is never reported as available.
# Conf in trailing comments: R = reported/consensus, J = analyst read.
PARTNER_UNTOUCHABLES = {
    # East
    "ATL": {"hard": ["Jalen Johnson"]},                                   # R; Trae Young = gray
    "BOS": {"hard": ["Jayson Tatum"]},                                    # R only; rest movable in the gap year
    "BKN": {"hard": []},                                                  # no centerpiece
    "CHA": {"hard": ["LaMelo Ball", "Brandon Miller", "Kon Knueppel"]},   # R
    "CHI": {"hard": ["Matas Buzelis"]},                                   # J
    "CLE": {"hard": ["Donovan Mitchell", "Evan Mobley"]},                 # R
    "DET": {"hard": ["Cade Cunningham", "Ausar Thompson"]},               # Cunningham R, Thompson J; Duren is RFA
    "IND": {"hard": ["Tyrese Haliburton", "Pascal Siakam",
                     "Andrew Nembhard", "Obi Toppin"]},                   # R, core-seven group
    "MIA": {"hard": ["Bam Adebayo"]},                                     # R; Herro openly available
    "MIL": {"hard": []},                                                  # Giannis = extend-or-trade
    "NYK": {"hard": ["Jalen Brunson", "Karl-Anthony Towns"]},             # R
    "ORL": {"hard": ["Paolo Banchero", "Franz Wagner"]},                  # R; Suggs core (J)
    "PHI": {"hard": ["Tyrese Maxey", "Joel Embiid", "VJ Edgecombe"]},     # Maxey R, others J
    "TOR": {"hard": ["Scottie Barnes"]},                                  # R
    "WAS": {"hard": ["Tre Johnson"]},                                     # R; Anthony Davis is available
    # West
    "DAL": {"hard": ["Cooper Flagg"], "speculative": ["Kyrie Irving"]},   # Flagg R; Kyrie soft keep
    "DEN": {"hard": ["Nikola Jokic"]},                                    # R only
    "GSW": {"hard": ["Stephen Curry"]},                                   # R
    "HOU": {"hard": ["Amen Thompson", "Alperen Sengun"]},                 # Thompson R, Sengun J
    "LAC": {"hard": []},                                                  # retooling
    "LAL": {"hard": ["Luka Doncic"]},                                     # R; LeBron/Reaves are FAs
    "MEM": {"hard": []},                                                  # selling; Morant available
    "MIN": {"hard": ["Anthony Edwards", "Jaden McDaniels", "Joan Beringer"]},  # matches OFF_LIMITS
    "NOP": {"hard": ["Trey Murphy III", "Derik Queen"]},                  # J
    "OKC": {"hard": ["Shai Gilgeous-Alexander", "Chet Holmgren", "Jalen Williams"]},  # R
    "PHX": {"hard": ["Devin Booker"]},                                    # J; verify rest of roster
    "POR": {"hard": ["Shaedon Sharpe", "Donovan Clingan"]},               # J, low conf
    "SAC": {"hard": []},                                                  # no franchise piece
    "SAS": {"hard": ["Victor Wembanyama", "Stephon Castle", "Dylan Harper", "De'Aaron Fox"]},  # R
    "UTA": {"hard": []},                                                  # rebuilding; Kessler is RFA
}

PV = {r["player_id"]: r for r in csv.DictReader(open(os.path.join(DATA, "player_value.csv"), encoding="utf-8"))}
SURP = {r["player_id"]: r for r in csv.DictReader(open(os.path.join(DATA, "player_surplus.csv"), encoding="utf-8"))}


def _norm_name(s):
    """case/accent/punct/suffix-insensitive name key, so 'De'Aaron Fox' and 'Trey Murphy III'
    resolve cleanly and 'Obi Toppin' never collides with 'Jacob Toppin'."""
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    s = re.sub(r"[.\-']", "", s)
    s = re.sub(r"\b(jr|sr|ii|iii|iv|v)\b", "", s)
    return re.sub(r"\s+", " ", s).strip()


def resolve_partner_untouchables():
    """Resolve the display-name override to stable player_ids, scoped PER TEAM (so a name only
    matches a player actually on that team). Returns (hard, spec, unresolved) where hard/spec map
    team -> set(pid). Matching uses player_surplus ids, the same ids partner_players yields."""
    by_team = {}
    for pid, r in SURP.items():
        by_team.setdefault(r["team_abbr"], {})[_norm_name(r["player_name"])] = str(pid)
    hard, spec, unresolved = {}, {}, []
    for team, cfg in PARTNER_UNTOUCHABLES.items():
        idx = by_team.get(team, {})
        for key, dest in (("hard", hard), ("speculative", spec)):
            for nm in cfg.get(key, []):
                pid = idx.get(_norm_name(nm))
                if pid:
                    dest.setdefault(team, set()).add(pid)
                else:
                    # not on the 2026-27 priced book for that team -> cannot be surfaced anyway,
                    # but record it so coverage stays auditable.
                    unresolved.append((team, key, nm))
    return hard, spec, unresolved


HARD_UNTOUCH, SPEC_UNTOUCH, _UNRESOLVED_UNTOUCH = resolve_partner_untouchables()
OVERRIDE_REMOVED = {}        # partner -> [player_name, ...] dropped by the hard override (for the board reason)


# ----------------------------- shared engine state (built once) ----------------------------- #
class Engine:
    def __init__(self, ns):
        F.NS = ns
        self.base_imp = A.load_impacts()
        self.dims = B.load_dims()
        G.inject_replacement(self.base_imp, self.dims)
        self.aged = AC.aged_impacts(self.base_imp)
        self.ar = BH.actual_top_rotations("2025-26")
        self.an = BH.actual_team_net(2025)
        self.base_league = E.build_2026_27_league(self.aged)
        self.pre = F._sim(self.base_league, 5.5)["teams"]["MIN"]["title"]
        self.const = EM.load_constants("2026-27")
        self.min_ts = EM.load_team_state("MIN", "2026-27", "base")


def _r(name_or_pid, role):
    pid = MIN.get(name_or_pid, name_or_pid)
    return {"nba_player_id": pid, "role": role}


BIG_POS = ("C", "C-F", "F-C")
STRETCH_SHOOT = 0.40        # off_ball_shooting pctile above which a big spaces next to Gobert


def _redundant_rim_big(pid, keeps_gobert):
    """A non-shooting center acquired while MIN KEEPS Gobert is redundant: he cannot share heavy
    minutes with Gobert (two non-spacers), so he plays BACKUP-five minutes, not the starter slot.
    A true stretch-five (Turner-type, off_ball_shooting >= 0.40) is NOT redundant: he spaces."""
    if not keeps_gobert:
        return False
    if PA.player_position(pid) not in BIG_POS:
        return False
    return PA.player_dims(pid).get("off_ball_shooting", 0.5) < STRETCH_SHOOT


def build_min_rotation(out_names, in_players):
    """Realistic-lineup default: removed MIN pieces free their roles; incoming players inherit them
    best-impact-to-best-role, EXCEPT a redundant rim big (keeping Gobert) is forced to a backup role
    so the model never plays two non-spacing centers heavy minutes together. Leftover freed slots
    drop to REPLACEMENT. in_players: list of (pid, salary)."""
    rank = {"starter": 0, "sixth": 1, "rotation": 2, "deep": 3}
    freed = sorted([role for (nm, role) in MIN_BASE_ROT if nm in out_names], key=lambda x: rank[x])
    kept = [_r(nm, role) for (nm, role) in MIN_BASE_ROT if nm not in out_names]
    keeps_gobert = "Gobert" not in out_names
    incoming = sorted(in_players, key=lambda p: -float(PV.get(p[0], {}).get("consensus_net", 0) or 0))
    non_redundant = [p for p in incoming if not _redundant_rim_big(p[0], keeps_gobert)]
    redundant = [p for p in incoming if _redundant_rim_big(p[0], keeps_gobert)]
    added, fi = [], 0
    # non-redundant incoming inherit freed roles best-first
    for (pid, _sal) in non_redundant:
        role = freed[fi] if fi < len(freed) else "rotation"
        added.append({"nba_player_id": pid, "role": role}); fi += 1
    # redundant rim bigs take a NON-starter freed slot if one remains, else a backup-five rotation role
    for (pid, _sal) in redundant:
        if fi < len(freed) and freed[fi] != "starter":
            role = freed[fi]; fi += 1
        else:
            role = "rotation"
        added.append({"nba_player_id": pid, "role": role})
    # any starter slot a non-redundant incoming did not fill -> replacement-level body (a committee 4,
    # NOT a second center): this is what keeps a redundant-big acquisition from inflating the lineup
    while fi < len(freed):
        added.append({"nba_player_id": G.REPL_ID, "role": freed[fi]}); fi += 1
    return kept + added


def min_scenario(out_pkg, in_players):
    """out_pkg: list of (name, salary, kicker). in_players: list of (pid, salary)."""
    out_names = [nm for (nm, _s, _k) in out_pkg]
    rot = build_min_rotation(set(out_names), in_players)
    override = [p[0] for p in in_players] + [MIN[nm] for nm in out_names if nm in MIN]
    return {"name": "search", "slug": "search", "team_state_scenario": "base",
            "outgoing": [{"label": nm, "salary": s, "trade_kicker_pct": k} for (nm, s, k) in out_pkg],
            "incoming": [{"label": pid, "salary": s} for (pid, s) in in_players],
            "override_ids": override, "post_rotations": {"MIN": rot}}


# ----------------------------------- feasibility (two-sided) -------------------------------- #
def min_legal(eng, out_pkg, in_players):
    out = [{"label": nm, "salary": s, "trade_kicker_pct": k} for (nm, s, k) in out_pkg]
    inc = [{"label": pid, "salary": s} for (pid, s) in in_players]
    r = EM.evaluate_move(eng.min_ts, eng.const, out, inc)
    return r


def partner_legal(eng, partner, give_back, min_in_salaries):
    """Partner SENDS give_back to MIN, RECEIVES MIN's outbound salaries (picks are not salary)."""
    pts = EM.load_team_state(partner, "2026-27", "base")
    out = [{"label": p[0], "salary": p[1]} for p in give_back]
    inc = [{"label": "from MIN", "salary": s} for s in min_in_salaries]
    return EM.evaluate_move(pts, eng.const, out, inc)


# ---------------------------------- cheap MIN impact proxy ---------------------------------- #
def proxy_net_delta(eng, scenario):
    """MIN post-trade team net minus baseline net, from the rollup -- NO Monte Carlo."""
    post = F.apply_trade(scenario, eng.base_league, eng.aged, eng.dims, eng.ar, eng.an)
    return post["MIN"]["net"] - eng.base_league["MIN"]["net"]


# --------------------------------------- sweetener bill ------------------------------------- #
def pick_bill(required_pts):
    """Minimal-overshoot selection of MIN's OWN picks (UTA firsts held out) covering required_pts:
    the subset whose total is >= required with the least total spend (tie: fewest picks). Returns
    (picks, pts, needs_uta) where needs_uta is True if even MIN's whole own chest cannot cover it."""
    if required_pts <= 0:
        return [], 0.0, False
    n = len(MIN_PICKS)
    best = None
    for mask in range(1, 1 << n):
        subset = [MIN_PICKS[i] for i in range(n) if mask & (1 << i)]
        tot = sum(p for _, p in subset)
        if tot + 1e-9 >= required_pts:
            key = (tot, len(subset))
            if best is None or key < best[0]:
                best = (key, [l for l, _ in subset], tot)
    if best is None:                       # whole own chest still short -> a UTA first is needed
        return [l for l, _ in MIN_PICKS], MIN_CHEST_PTS, True
    return best[1], round(best[2], 2), False


# ----------------------------- MIN outbound package enumeration ----------------------------- #
def min_outbound_packages():
    """The salary-matching base packages MIN can send (off-limits already excluded)."""
    R = ("Randle", 33_333_334, 0.0); GO = ("Gobert", 36_500_000, 0.075); NZ = ("Naz", 23_333_333, 0.0)
    SH = ("Shannon", 2_800_000, 0.0); PH = ("Phillips", 2_400_000, 0.0); CL = ("Clark", 2_300_000, 0.0)
    return [
        ("Randle", [R]), ("Randle+filler", [R, SH]),
        ("Gobert", [GO]), ("Gobert+filler", [GO, PH]),
        ("Naz", [NZ]), ("Naz+filler", [NZ, SH]),
        ("Randle+Naz", [R, NZ]),
        ("both (Randle+Gobert)", [R, GO]),
        ("both+filler", [R, GO, CL]),
    ]


# ----------------------------- adverse-selection availability screen ------------------------- #
def untouchable(pid, partner_posture):
    """A player a team will NOT trade at any realistic price (the adverse-selection screen made
    a hard gate). Elite value is never sold; a good young player is a cornerstone unless his team
    is a teardown and he is a vet they would cash out. Mirrors the run_pairs KEEP discipline."""
    r = SURP.get(str(pid))
    if not r or r["surplus_net"] == "":
        return False
    s = float(r["surplus_net"])
    try:
        age = float(r["age"]) if r.get("age") else 30.0
    except (ValueError, TypeError):
        age = 30.0
    try:
        sal = float(r["salary_2026_27"] or 0)
    except (ValueError, TypeError):
        sal = 0.0
    net = float(r["consensus_net"]) if r["consensus_net"] != "" else 0.0
    if s >= 3.0:
        return True                                  # elite value: nobody sells (Wemby, SGA, Caruso..)
    if s >= 2.0:
        # a +2-to-3 player only moves if his team is tearing down AND he is a vet they cash out
        return not (partner_posture in ("rebuilder", "retooler") and age >= 28)
    # a YOUNG franchise cornerstone (a $30M+ player who is 29 or younger) is the pillar a team builds
    # around -- never moved for a non-star return, on ANY team (Luka, Haliburton, Sengun, Morant).
    if sal >= 30_000_000 and age <= 29.0:
        return True
    # an older $35M+ star is untouchable UNLESS his team is actively tearing down / pivoting -- exactly
    # how the series treats AD/Kyrie (gettable only if WAS/DAL pivot) while Brunson/Booker/Bam/Curry
    # (contenders / comfortable mids) stay off-limits.
    if sal >= 35_000_000 and partner_posture not in ("rebuilder", "retooler"):
        return True
    # ascending young assets are held by EVERYONE. A rookie-age player (<=22.5) is held regardless of a
    # rough rookie net (a #1 pick is upside, not a bust); a slightly older cheap player must not be a bust.
    if age <= 22.5 and sal < 16_000_000:
        return True
    if age <= 23.5 and sal < 16_000_000 and net >= -1.0:
        return True
    if age <= 26.5 and s >= 0.8 and sal < 22_000_000:
        return True
    return False


# Targeted data-hygiene corrections (Pass-1 HoopsHype scrape errors). The Zubac-on-IND mislabel is
# the canonical case; the full exclusion set is now DATA-DRIVEN from validate_contracts.py
# (data/contract_validation_flags.csv), so the engine refuses to surface any deal touching a
# contract row that failed validation (Phase 2-D, the automated Spotrac verify the findings doc asks
# for). Falls back to the canonical Zubac row if the flags file has not been generated yet.
def _load_bad_rows():
    bad = set()      # Zubac-on-IND is now CORRECT (real 2026 trade); flags come from the validator
    path = os.path.join(DATA, "contract_validation_flags.csv")
    if os.path.exists(path):
        for r in csv.DictReader(open(path, encoding="utf-8")):
            pid = (r.get("nba_player_id") or "").strip()
            if pid:
                bad.add((pid, (r.get("team_abbr") or "").strip()))
    return bad


KNOWN_BAD_ROWS = _load_bad_rows()      # {(nba_player_id, team_abbr)} excluded from partner_players


def partner_players(partner):
    """Rostered partner players MIN might want and that the partner would actually move: has
    impact, salary > $4M, and not an untouchable cornerstone. Caps to top ~12 by net."""
    pp = PA.posture(partner).get("posture", "mid")
    hard = HARD_UNTOUCH.get(partner, set())
    removed = []
    rows = []
    for pid, r in SURP.items():
        if r["team_abbr"] != partner:
            continue
        if (str(pid), partner) in KNOWN_BAD_ROWS:
            continue
        sal = float(r["salary_2026_27"] or 0)
        net = r["consensus_net"]
        if sal < 4_000_000 or net == "":
            continue
        if untouchable(pid, pp):
            continue
        # Fix 1: partner-side override is UNIONED with the data gate (only adds exclusions, never
        # makes a data-gated player available). reason = manual_untouchable_reported_core.
        if str(pid) in hard:
            removed.append(r["player_name"])
            continue
        rows.append((pid, sal, float(net), r["player_name"], r["position"]))
    OVERRIDE_REMOVED[partner] = removed
    rows.sort(key=lambda x: -x[2])
    return rows[:12]


def giveback_combos(players, out_salary, tier, const, min_want_net=0.5):
    """1- and 2-player give-back combos whose salary roughly fits MIN's take-back band for the
    outbound, and where at least one piece is a player MIN wants (net >= min_want_net)."""
    limit = EM.matching_limit(out_salary, tier, const)
    singles = [(p,) for p in players]
    pairs = list(itertools.combinations(players, 2))
    combos = []
    for combo in singles + pairs:
        sal = sum(p[1] for p in combo)
        if sal > limit + 250_000:                 # MIN can't legally take this much back
            continue
        if not any(p[2] >= min_want_net for p in combo):
            continue
        combos.append(combo)
    return combos


# ------------------------------------- 2027 flex classifier --------------------------------- #
def flex_state(eng, out_pkg, in_players, sweetener_pts, min_gate):
    """HIGH / MODERATE / LOW 2027 war-chest state, from the data of the deal."""
    in_years = max([PA.years_left(p[0]) for p in in_players], default=1)
    in_salary = sum(p[1] for p in in_players)
    out_base = sum(s for (_n, s, _k) in out_pkg)
    sheds = out_base - in_salary                          # +: MIN sheds salary
    hard = bool(min_gate.get("hard_cap_tripped")) or bool(min_gate.get("take_back_more"))
    spends_firsts = sweetener_pts >= 5.0                  # a real first or more out of the chest
    if in_years >= 3 and (hard or in_salary >= 30_000_000):
        return "LOW"
    if sheds >= 8_000_000 and in_years <= 2 and not spends_firsts:
        return "HIGH"
    if spends_firsts and in_years >= 3:
        return "LOW"
    if in_years <= 2 and not hard:
        return "HIGH" if not spends_firsts else "MODERATE"
    return "MODERATE"


# --------------------------------- Tier 0: free per-partner screen -------------------------- #
def screen_partner(eng, partner, topk):
    """Return (survivors, near_misses). survivor = dict with scenario + acceptance + proxy + flex."""
    players = partner_players(partner)
    survivors, near = [], []
    for pkg_name, out_pkg in min_outbound_packages():
        out_salary = sum(s * (1 + k) for (_n, s, k) in out_pkg)   # kicker-inflated for matching
        out_base = sum(s for (_n, s, _k) in out_pkg)
        combos = giveback_combos(players, out_salary, eng.min_ts["tier"], eng.const)
        for combo in combos:
            in_players = [(p[0], p[1]) for p in combo]
            mg = min_legal(eng, out_pkg, in_players)
            if not mg["legal"]:
                continue
            pg = partner_legal(eng, partner, [(p[0], p[1]) for p in combo], [s for (_n, s, _k) in out_pkg])
            partner_can_absorb = pg["legal"]
            # partner acceptance: sends combo, receives MIN outbound (+ sweetener picks)
            sends = [{"pid": p[0], "salary": p[1], "label": p[3]} for p in combo]
            receives = [{"pid": (MIN.get(n)), "salary": s, "label": n} for (n, s, _k) in out_pkg]
            # find the minimum sweetener (pts) that wins acceptance, up to MIN's chest
            best_accept = None
            for swp in (0.0, 0.7, 1.4, 3.5, 5.0, 7.0, MAX_SWEETENER_PTS):
                a = PA.decide(partner, sends, receives, sweetener_pts=swp)
                if a["accepted"]:
                    best_accept = (swp, a); break
            scen = min_scenario(out_pkg, in_players)
            proxy = proxy_net_delta(eng, scen)
            rec = {"partner": partner, "pkg": pkg_name, "out_pkg": out_pkg, "in_players": in_players,
                   "combo": combo, "proxy": proxy, "min_gate": mg, "partner_can_absorb": partner_can_absorb}
            if best_accept and partner_can_absorb and proxy > 0:
                swp, a = best_accept
                picks, pts, needs_uta = pick_bill(a["required_sweetener_pts"] if a["channel"] == "cap_relief" else swp)
                rec.update({"accept": a, "sweetener_pts": pts, "sweetener_picks": picks,
                            "needs_uta": needs_uta,
                            "flex": flex_state(eng, out_pkg, in_players, pts, mg)})
                survivors.append(rec)
            elif proxy > 0.4:        # MIN really wants it but it failed acceptance or partner matching
                why = ("partner can't match/absorb the salary" if not partner_can_absorb
                       else "no acceptance channel fires even at MIN's full chest")
                rec.update({"near_reason": why, "best_accept": best_accept})
                near.append(rec)
    # rank survivors by a RISK-HAIRCUT proxy (avail x playoff-read x Edwards-overlap on the key
    # incoming player), not raw net delta, so a steadier role-player deal survives the top-k cut
    # rather than being crowded out by high-variance stars. tier1 then refines with the real sim.
    for r in survivors:
        key = max([p[0] for p in r["in_players"]],
                  key=lambda p: float(PV.get(p, {}).get("consensus_net", 0) or 0))
        rd = PV.get(key, {}).get("translation_read", "")
        r["screen_risk"] = r["proxy"] * _avail(key) * G.PO_MULT.get(rd, 0.98) * G.usage_mult(key, eng.dims)
    survivors.sort(key=lambda r: -r["screen_risk"])
    near.sort(key=lambda r: -r["proxy"])
    # also surface the best Gobert-out survivor (even if a keep-Gobert deal beats it for this team),
    # so the cross-validation can compare the channel's Gobert harvest to the hand-built both-out.
    gob = [r for r in survivors if "Gobert" in [n for (n, _s, _k) in r["out_pkg"]]]
    return survivors[:topk], near[:3], (gob[0] if gob else None)


# ----------------------------------- Tier 1: one sim/survivor ------------------------------- #
def consensus_dp(eng, scenario):
    base = eng.base_league
    post = F.apply_trade(scenario, base, eng.aged, eng.dims, eng.ar, eng.an)
    return (F._sim(post, 5.5)["teams"]["MIN"]["title"] - eng.pre) * 100


_AVAIL_CACHE = {}


def _avail(pid):
    if pid not in _AVAIL_CACHE:
        try:
            _AVAIL_CACHE[pid] = G.availability(pid)[0]
        except Exception:
            _AVAIL_CACHE[pid] = 0.85
    return _AVAIL_CACHE[pid]


def tier1_best(eng, survivors):
    """Score each survivor's consensus dP, then pick the partner's winner on a CHEAP risk proxy:
    dP haircut by the key incoming player's availability, playoff-translation multiplier, and
    Edwards-overlap usage multiplier (the same factors the full overlay uses, minus the two-branch
    sim). This keeps a high-variance star (Kyrie, post-ACL) from beating a steadier role-player deal
    that is better once risk is priced. Tier 2 then does the full risk-adjusted treatment."""
    scored = []
    for rec in survivors:
        scen = min_scenario(rec["out_pkg"], rec["in_players"])
        rec["dp_consensus"] = consensus_dp(eng, scen)
        key = max([p[0] for p in rec["in_players"]],
                  key=lambda p: float(PV.get(p, {}).get("consensus_net", 0) or 0))
        read = PV.get(key, {}).get("translation_read", "")
        haircut = _avail(key) * G.PO_MULT.get(read, 0.98) * G.usage_mult(key, eng.dims)
        rec["risk_proxy"] = rec["dp_consensus"] * haircut
        scored.append(rec)
    scored.sort(key=lambda r: -r["risk_proxy"])
    return scored


# ----------------------------------- Tier 2: full treatment --------------------------------- #
def _dp_view(eng, scen, imp, replace=None):
    base = E.build_2026_27_league(imp)
    pre = F._sim(base, 5.5)["teams"]["MIN"]["title"]
    s = scen
    if replace:
        s = copy.deepcopy(scen)
        for p in s["post_rotations"]["MIN"]:
            if p["nba_player_id"] in (replace if isinstance(replace, (set, list)) else {replace}):
                p["nba_player_id"] = G.REPL_ID
    post = F.apply_trade(s, base, imp, eng.dims, eng.ar, eng.an)
    return (F._sim(post, 5.5)["teams"]["MIN"]["title"] - pre) * 100


def tier2_full(eng, rec):
    """Four views (consensus/box/rapm + DARKO where available), risk-adjusted EV with the
    availability band on the KEY incoming player, gauntlet vs OKC/SAS, conservative anchor."""
    scen = min_scenario(rec["out_pkg"], rec["in_players"])
    override = scen["override_ids"]
    in_pids = [p[0] for p in rec["in_players"]]
    # four views
    views = {"consensus": _dp_view(eng, scen, eng.aged)}
    for v in ("box", "rapm", "darko"):
        if v == "darko" and not any(p in F._DARKO for p in in_pids if F._DARKO):
            views[v] = None
            continue
        iv = F.build_impacts_view(v, override, eng.aged)
        views[v] = _dp_view(eng, scen, iv)
    # risk overlay on the TOP-TWO highest-net incoming players (extended from single-key per the Phase 2
    # spec): a low-availability second star (a post-ACL guard who outranks nobody on net but carries real
    # medical risk) is now priced, where before only the single highest-net piece was haircut. Independent-
    # availability 4-state EV (both play / each one out / both out); the playoff-translation x usage haircut
    # is applied to the both-play branch.
    base = eng.base_league
    ranked = sorted(in_pids, key=lambda p: float(PV.get(p, {}).get("consensus_net", 0) or 0), reverse=True)
    keys = ranked[:2]

    def _poum(p):
        return G.PO_MULT.get(PV.get(p, {}).get("translation_read", ""), 0.98) * G.usage_mult(p, eng.dims)

    full = _dp_view(eng, scen, eng.aged)
    key = keys[0]
    avail = _avail(key)                       # cached + DB-drop-tolerant (falls back to 0.85), not a raw query
    if len(keys) == 1:
        with_dp = full * _poum(key)
        without_dp = _dp_view(eng, scen, eng.aged, replace=key)
        risk_adj = avail * with_dp + (1 - avail) * without_dp
    else:
        k1, k2 = keys
        a1, a2 = avail, _avail(k2)
        with_dp = full * ((_poum(k1) + _poum(k2)) / 2.0)        # both play, playoff/usage haircut
        dp_k1out = _dp_view(eng, scen, eng.aged, replace=k1)    # top piece hurt, second plays
        dp_k2out = _dp_view(eng, scen, eng.aged, replace=k2)    # second piece hurt, top plays
        dp_bothout = _dp_view(eng, scen, eng.aged, replace=set(keys))
        without_dp = dp_bothout                                 # report the both-out floor as "without"
        risk_adj = (a1 * a2 * with_dp + a1 * (1 - a2) * dp_k2out
                    + (1 - a1) * a2 * dp_k1out + (1 - a1) * (1 - a2) * dp_bothout)
        rec["key2"] = k2
        rec["avail2"] = a2
    # conservative anchor = lowest available view (winner's-curse discipline)
    avail_views = [x for x in views.values() if x is not None]
    anchor = min(avail_views)
    # gauntlet vs OKC/SAS
    post = F.apply_trade(scen, base, eng.aged, eng.dims, eng.ar, eng.an)
    cond = E.conditional_series("MIN", post, use_overlay=True)
    cpre = E.conditional_series("MIN", base, use_overlay=True)
    rec.update({"views": views, "risk_adj": risk_adj, "anchor": anchor, "with_dp": with_dp,
                "without_dp": without_dp, "avail": avail, "key": key,
                "gauntlet_okc": (cond["OKC"] - cpre["OKC"]) * 100,
                "gauntlet_sas": (cond["SAS"] - cpre["SAS"]) * 100,
                "darko_avail": views.get("darko") is not None})
    return rec


# ----------------------------- Pass 2: targeted three-team resolver ------------------------- #
def dump_absorbers():
    rows = [r for r in csv.DictReader(open(os.path.join(DATA, "team_posture.csv"), encoding="utf-8"))
            if r["absorbs_dumps"] == "TRUE"]
    rows.sort(key=lambda r: -float(r["rebuild_score"]))
    return [r["team_abbr"] for r in rows]


def pass2_resolve(eng, near, third_teams):
    """For a near-miss where the partner could NOT match/absorb MIN's big outbound, route that
    big contract to a third team T (a data-defined dump-absorber) and send the partner a smaller
    MIN package (Naz + picks) it can absorb and accept. Surface only if T is STRUCTURALLY needed
    (the two-team version is illegal/rejected) and all three sides clear. Reports why T is needed."""
    partner = near["partner"]
    out_pkg = near["out_pkg"]
    combo = near["combo"]
    gb = [(p[0], p[1]) for p in combo]
    gb_names = ", ".join(p[3] for p in combo)
    gb_salary = sum(p[1] for p in gb)
    # the big contract the partner couldn't absorb (largest MIN outbound piece)
    big = max(out_pkg, key=lambda x: x[1])
    if big[0] not in ("Randle", "Gobert"):
        return None
    rest_pieces = [p for p in out_pkg if p is not big]
    # MIN substitutes Naz as the salary it sends the partner (if Naz not already the big / in rest)
    NZ = ("Naz", 23_333_333, 0.0)
    min_to_partner = [NZ] + [p for p in rest_pieces if p[0] not in ("Naz", big[0])]
    mtp_salary = sum(s for (_n, s, _k) in min_to_partner)

    for T in third_teams:
        if T == partner:
            continue
        # T absorbs `big` (cap_relief): T sends back a min filler, receives big, with a sweetener
        t_sends = [{"pid": None, "salary": 2_300_000, "label": "min filler"}]
        t_receives = [{"pid": MIN.get(big[0]), "salary": big[1], "label": big[0]}]
        accept_T = None
        for swp in (0.7, 1.4, 3.5, 5.0, 7.0, MAX_SWEETENER_PTS):
            a = PA.decide(T, t_sends, t_receives, sweetener_pts=swp)
            if a["accepted"] and a["channel"] == "cap_relief":
                accept_T = (swp, a); break
        if not accept_T:
            continue
        t_ts = EM.load_team_state(T, "2026-27", "base")
        tg = EM.evaluate_move(t_ts, eng.const, [{"label": "filler", "salary": 2_300_000}],
                              [{"label": big[0], "salary": big[1], "trade_kicker_pct": big[2]}])
        if not tg["legal"]:
            continue
        # partner: sends gb, receives MIN's smaller package (Naz + small), + sweetener
        p_sends = [{"pid": p[0], "salary": p[1], "label": p[3]} for p in combo]
        p_receives = [{"pid": MIN.get(n), "salary": s, "label": n} for (n, s, _k) in min_to_partner]
        accept_P = None
        for swp in (0.0, 1.4, 3.5, 5.0, 7.0, MAX_SWEETENER_PTS):
            a = PA.decide(partner, p_sends, p_receives, sweetener_pts=swp)
            if a["accepted"]:
                accept_P = (swp, a); break
        if not accept_P:
            continue
        p_ts = EM.load_team_state(partner, "2026-27", "base")
        pg = EM.evaluate_move(p_ts, eng.const, [{"label": p[3], "salary": p[1]} for p in combo],
                              [{"label": n, "salary": s} for (n, s, _k) in min_to_partner])
        if not pg["legal"]:
            continue
        # MIN: sends big (to T) + min_to_partner (to partner), receives gb (from partner)
        min_out = [{"label": n, "salary": s, "trade_kicker_pct": k} for (n, s, k) in [big] + min_to_partner]
        min_in = [{"label": p[0], "salary": p[1]} for p in gb]
        mg = EM.evaluate_move(eng.min_ts, eng.const, min_out, min_in)
        if not mg["legal"]:
            continue
        # score MIN's resulting roster (it acquires gb, sheds big + Naz): build the scenario
        scen = min_scenario([big] + min_to_partner, gb)
        dp = consensus_dp(eng, scen)
        if dp <= 0:
            continue
        return {"partner": partner, "third": T, "gb_names": gb_names, "big": big[0],
                "min_to_partner": min_to_partner, "dp": dp,
                "why": (f"{partner} could not absorb {big[0]}'s ${big[1]/1e6:.0f}M; {T} "
                        f"(a {PA.posture(T).get('posture')}/dump-absorber) takes {big[0]} via cap-relief, "
                        f"freeing {partner} to send {gb_names} for MIN's smaller (Naz-led) package."),
                "sweetener_T": pick_bill(accept_T[1]["required_sweetener_pts"])[0],
                "accept_P_channel": accept_P[1]["channel"]}
    return None


def _gb_str(combo):
    return ", ".join(f"{p[3]} (${p[1]/1e6:.0f}M)" for p in combo)


def emit_board(board, three):
    """Write the machine-readable board (data/trade_board.csv) and the ranked board markdown."""
    rows = []
    for b in board:
        if b["deal"]:
            d = b["deal"]; v = d.get("views", {})
            rows.append({
                "partner": b["partner"], "verdict": "DEAL",
                "min_sends": d["pkg"], "min_gets": _gb_str(d["combo"]),
                "sweetener": "; ".join(d.get("sweetener_picks") or []) or "none",
                "accept_channel": d["accept"]["channel"], "partner_posture": d["accept"]["posture"],
                "dp_consensus": round(d.get("views", {}).get("consensus", d["dp_consensus"]), 2),
                "dp_box": round(v["box"], 2) if v.get("box") is not None else "",
                "dp_rapm": round(v["rapm"], 2) if v.get("rapm") is not None else "",
                "dp_darko": round(v["darko"], 2) if v.get("darko") is not None else "",
                "anchor": round(d["anchor"], 2) if "anchor" in d else "",
                "risk_adj": round(d["risk_adj"], 2) if "risk_adj" in d else "",
                "gauntlet_okc": round(d["gauntlet_okc"], 1) if "gauntlet_okc" in d else "",
                "gauntlet_sas": round(d["gauntlet_sas"], 1) if "gauntlet_sas" in d else "",
                "flex_2027": d["flex"], "sourcing": d.get("sourcing", "model-surfaced"),
                "needs_uta_first": "TRUE" if d.get("needs_uta") else "FALSE"})
        else:
            nm = (b.get("near") or [{}])[0]
            rows.append({"partner": b["partner"], "verdict": "NO DEAL",
                         "min_sends": "", "min_gets": "", "sweetener": "",
                         "accept_channel": "", "partner_posture": PA.posture(b["partner"]).get("posture", ""),
                         "dp_consensus": "", "dp_box": "", "dp_rapm": "", "dp_darko": "",
                         "anchor": "", "risk_adj": "", "gauntlet_okc": "", "gauntlet_sas": "",
                         "flex_2027": "", })
            reason = nm.get("near_reason", "no positive-dP deal clears both sides")
            held = OVERRIDE_REMOVED.get(b["partner"]) or []
            held_note = f"; core held (manual_untouchable_reported_core): {', '.join(held)}" if held else ""
            rows[-1]["min_gets"] = f"(near: {reason}{held_note})"
            rows[-1]["sourcing"] = ""; rows[-1]["needs_uta_first"] = ""
    fields = ["partner", "verdict", "min_sends", "min_gets", "sweetener", "accept_channel",
              "partner_posture", "dp_consensus", "dp_box", "dp_rapm", "dp_darko", "anchor",
              "risk_adj", "gauntlet_okc", "gauntlet_sas", "flex_2027", "sourcing", "needs_uta_first"]
    with open(os.path.join(DATA, "trade_board.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields); w.writeheader(); w.writerows(rows)
    # three-team rows appended to a sibling file
    if three:
        tf = ["partner", "third_team", "min_gets", "routed", "dp_consensus", "why"]
        with open(os.path.join(DATA, "trade_board_threeteam.csv"), "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=tf); w.writeheader()
            for r in three:
                w.writerow({"partner": r["partner"], "third_team": r["third"], "min_gets": r["gb_names"],
                            "routed": r["big"], "dp_consensus": round(r["dp"], 2), "why": r["why"]})
    print(f"\nemit -> data/trade_board.csv ({len(rows)} partners)"
          + (f" + data/trade_board_threeteam.csv ({len(three)})" if three else ""))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--partners", default="")
    ap.add_argument("--ns", type=int, default=2500)
    ap.add_argument("--tier2-ns", type=int, default=6000)
    ap.add_argument("--topk", type=int, default=6)
    ap.add_argument("--tier2", action="store_true", help="run the full four-view + risk-adjusted pass")
    ap.add_argument("--pass2", action="store_true", help="run the targeted three-team resolver")
    ap.add_argument("--emit", action="store_true", help="write data/trade_board.csv + outputs md")
    args = ap.parse_args()

    eng = Engine(args.ns)
    PA.load_layers()

    def safe(s): return str(s).encode("ascii", "replace").decode()

    n_hard = sum(len(v) for v in HARD_UNTOUCH.values())
    n_spec = sum(len(v) for v in SPEC_UNTOUCH.values())
    print(f"partner-untouchables override: {n_hard} hard / {n_spec} speculative resolved across "
          f"{len(HARD_UNTOUCH)} teams"
          + (f"; {len(_UNRESOLVED_UNTOUCH)} unresolved (not on the priced book): "
             + ", ".join(f"{t}/{nm}" for (t, _k, nm) in _UNRESOLVED_UNTOUCH) if _UNRESOLVED_UNTOUCH else ""))
    all_teams = sorted({r["team_abbr"] for r in SURP.values()} - {"MIN"})
    partners = [t.strip() for t in args.partners.split(",") if t.strip()] or all_teams

    print(f"=== Pass 1 screen: MIN baseline title {eng.pre*100:.2f}% | NS={args.ns} | {len(partners)} partners ===\n")
    board = []
    gob_candidates = []
    TOP_N = 3
    for partner in partners:
        survivors, near, gob = screen_partner(eng, partner, args.topk)
        if gob:
            gob_candidates.append((partner, gob))
        if not survivors:
            reason = (f"near-miss: {near[0]['near_reason']}" if near else "no positive-dP deal clears both sides")
            print(f"  {partner}: NO DEAL ({reason})")
            board.append({"partner": partner, "deal": None, "near": near})
            continue
        scored = tier1_best(eng, survivors)          # sets dp_consensus + risk_proxy, sorted by risk_proxy
        cands = scored[:TOP_N]
        if args.tier2:
            F.NS = args.tier2_ns
            for rec in cands:
                tier2_full(eng, rec)                 # full four-view + risk-adjusted on each candidate
            F.NS = args.ns
            best = max(cands, key=lambda r: r["risk_adj"])   # the partner's winner on the HONEST axis
        else:
            best = scored[0]
        # sourcing tag: a $35M+ incoming star is Speculative-by-construction (the posture math lets it
        # through only if the partner pivots; it is NOT reported available).
        spec_ids = SPEC_UNTOUCH.get(partner, set())
        is_spec = (any(p[1] >= 35_000_000 for p in best["combo"])
                   or any(str(p[0]) in spec_ids for p in best["combo"])
                   or best["accept"].get("soft_speculative"))   # sourced 'not available' (news layer)
        best["sourcing"] = ("Speculative (conditional on partner pivot)" if is_spec else "model-surfaced")
        a = best["accept"]
        gb = ", ".join(f"{p[3]} ${p[1]/1e6:.0f}M" for p in best["combo"])
        sweet = (" + " + " + ".join(best["sweetener_picks"])) if best["sweetener_picks"] else " (no sweetener)"
        ra = f" risk-adj {best['risk_adj']:+.2f}" if "risk_adj" in best else ""
        print(f"  {partner}: dP {best['dp_consensus']:+.2f}{ra} | MIN sends {best['pkg']}{sweet} | "
              f"MIN gets {safe(gb)}")
        print(f"        accept via {a['channel']} ({a['posture']}) | flex {best['flex']} | "
              f"{best['sourcing']}{' | NEEDS A UTA FIRST' if best.get('needs_uta') else ''}")
        board.append({"partner": partner, "deal": best, "near": near, "scored": scored})

    def rank_key(b):
        d = b["deal"]
        return d["risk_adj"] if "risk_adj" in d else d.get("risk_proxy", d["dp_consensus"])
    ranked = sorted([b for b in board if b["deal"]], key=lambda b: -rank_key(b))
    print(f"\n=== RANKED (risk-adjusted dP) -- {len(ranked)} partners with a deal, "
          f"{len(board)-len(ranked)} no-deal ===")
    for b in ranked:
        d = b["deal"]
        ra = f"{d['risk_adj']:+.2f}" if "risk_adj" in d else f"~{d.get('risk_proxy',0):+.2f}"
        anc = f" anchor {d['anchor']:+.2f}" if "anchor" in d else ""
        gb = ", ".join(p[3] for p in d["combo"])
        print(f"  risk-adj {ra}{anc}  {b['partner']:4} {d['pkg']:14} flex {d['flex']:8} "
              f"{d['sourcing'][:11]:11} | {safe(gb)}")

    # ---- Pass 2: targeted three-team on the salary-blocked near-misses ----
    three = []
    if args.pass2:
        absorbers = dump_absorbers()
        print(f"\n=== Pass 2: targeted three-team (dump-absorbers: {', '.join(absorbers)}) ===")
        seen = set()
        for b in board:
            for nm in (b.get("near") or []):
                if nm.get("near_reason", "").startswith("partner can't") and nm["partner"] not in seen:
                    res = pass2_resolve(eng, nm, absorbers)
                    if res:
                        three.append(res); seen.add(nm["partner"])
                        print(f"  +{res['dp']:.2f}pp  {res['partner']}+{res['third']}: MIN gets {safe(res['gb_names'])}")
                        print(f"        WHY 3rd team: {res['why']}")
        if not three:
            print("  (no near-miss resolved into a legal, accepted three-team deal)")

    # ---- cross-validation: does the (cap-relief/value) channel rediscover the both-out Gobert harvest? ----
    # Score the best Gobert-out candidate each partner produced (even where a keep-Gobert deal beat it),
    # and compare to the hand-built both-out playbook. The user's check: flag anything that beats it.
    BOTH_OUT_BENCH = 2.2   # championship_profiles both-out present-title harvest (DARKO-anchored, ~+2.2)
    print("\n=== cross-validation: the Gobert-out harvest the search finds vs the hand-built both-out ===")
    won_gobert = [b for b in ranked if "Gobert" in b["deal"]["pkg"] or "both" in b["deal"]["pkg"]]
    if won_gobert:
        print("  Gobert-out deals that WON their partner (beat the keep-Gobert alternative):")
        for b in won_gobert:
            d = b["deal"]
            print(f"    {b['partner']:4} {d['pkg']:16} dP {d['dp_consensus']:+.2f} flex {d['flex']}")
    else:
        print("  NO Gobert-out deal won its partner -- keep-Gobert (Randle conversion) dominates everywhere.")
    if gob_candidates:
        scored_gob = []
        for partner, rec in gob_candidates:
            scen = min_scenario(rec["out_pkg"], rec["in_players"])
            rec["dp_consensus"] = consensus_dp(eng, scen)
            scored_gob.append((partner, rec))
        scored_gob.sort(key=lambda x: -x[1]["dp_consensus"])
        print("  best Gobert-out candidates found (consensus dP), top 5:")
        for partner, rec in scored_gob[:5]:
            gb = ", ".join(p[3] for p in rec["combo"])
            beat = " <<< BEATS both-out bench" if rec["dp_consensus"] > BOTH_OUT_BENCH else ""
            print(f"    {partner:4} {rec['pkg']:18} dP {rec['dp_consensus']:+.2f} | MIN gets {safe(gb)}{beat}")
        best = scored_gob[0][1]["dp_consensus"]
        print(f"  -> best Gobert-out harvest dP {best:+.2f} vs both-out bench ~{BOTH_OUT_BENCH:+.2f}: "
              + ("a Gobert-out deal BEATS the hand-built harvest (investigate)" if best > BOTH_OUT_BENCH
                 else "keep-Gobert dominates; confirms A/C-win-now over both-out (matches the playbook)"))

    if args.emit:
        emit_board(board, three)


if __name__ == "__main__":
    main()

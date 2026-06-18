#!/usr/bin/env python3
"""
partner_acceptance.py

Does the PARTNER say yes? Acceptance defined from data, computed the same way we compute
MIN's own side, never from vibes. A deal clears the partner iff ANY of three channels fires:

  (A) SURPLUS-IMPROVEMENT. The partner's inbound surplus_net beats its outbound by a margin
      (it receives more value-over-par than it gives). Gated against pure positional
      redundancy: a clear value gain only counts if the incoming basket fills a real need OR
      the partner is a rebuilder/retooler collecting value. This is where adverse selection
      lives: a high-surplus player only leaves if the partner is paid back in value or assets.

  (B) NEED-FILL. The partner's need-fit improves -- the incoming players address its measured
      needs (team_needs.csv) better than the players it sends, in the SAME role-adjusted
      dot-product space acquisition_metric.need_fit uses for MIN. A contender pays surplus to
      fill a need; this channel catches that.

  (C) CAP-RELIEF (dump). Fires ONLY when (a) the partner is a genuine rebuilder / floor-seeker
      / non-contender by the data-derived posture (team_posture.absorbs_dumps), AND it is NET
      ABSORBING salary, AND (b) MIN attaches a sufficient PRICED sweetener. The required
      sweetener scales with how far below par the absorbed contract is and how many years it
      runs, anchored to the comp ladder (Randle's mild expiring -> a second; a toxic multi-year
      -> an unprotected first). This is the only channel that exercises the shed-for-2027-
      flexibility axis, so it must exist for the board to agree with the portfolio capstone.

A deal that fires no channel is DISCARDED (reported only as the team-level no-deal verdict).

    python partner_acceptance.py        # self-tests on a few hand deals
"""

import os
import csv

try:
    import motivation_overrides as MO      # Phase 2-B: the sourced news layer (optional)
except Exception:                          # absent table -> neutral on the news axis
    MO = None

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")

DIMS = ["hc_creation", "secondary_playmaking", "off_ball_shooting",
        "def_versatility_poa", "rim_protect_reb", "transition"]
BIG_POSITIONS = ("C", "C-F", "F-C")

# Base acceptance margins (impact units / need-fit units). Phase 2-C turns these into FUNCTIONS of
# the team's computed urgency (team_urgency.csv) and sourced motivation (motivation_overrides). The
# base values are the pre-Phase-2 constants; every urgency/motivation term defaults to ZERO effect
# when its data file is absent, so the board is unchanged without the new layers.
SURPLUS_MARGIN = 0.6      # base clear value/asset gain for the partner
NEED_MARGIN = 0.12        # base clear need-fit gain for the partner
ROTATION_SALARY = 5_000_000   # below this, a piece is filler and doesn't "fill a need"
PT_TO_SURPLUS = 0.45      # one sweetener asset-point ~ this much surplus-equivalent value
BALANCE_TOL = 10_000_000  # a value/need deal must be a roughly balanced swap, not a salary dump
VET_AGE = 27.0            # at/over this, a rebuilder treats an outgoing player as a sellable vet
NEED_VALUE_FLOOR = -0.75  # need-fill cannot justify more than a small on-court value loss for the partner

# Phase 2-C coefficients. HAND-SET, validated against the self-tests below and the Phase 2 sanity
# checks, NOT against realized league trades. We tried that calibration and it is deliberately CLOSED:
# the realized-trade backtest (backtest_harness.py / backtest_tune.py) proved this acceptance model is
# scoped to Minnesota ACQUIRING a player and does not generalize to scoring arbitrary two-team trades
# (16% recall on real deals, because a general trade is zero-sum in surplus and these gates are tuned
# for MIN filling a need). See docs/acceptance_model_scope_and_limitation.md. So these stay hand-set
# and are directionally reasonable but un-calibrated at the margin: read the board's MARGINAL deals
# with that grain of salt; the strong deals clear regardless. Every one multiplies a [0,1] signal.
K_WINNOW_VALUE = 0.30     # a max win-now acquirer accepts this much less surplus margin
K_SELLER_DISCOUNT = 0.40  # a fully news-motivated seller drops the required margin this much
K_HEAT_PREMIUM = 0.50     # a max market-heat (coveted) player raises the required margin this much
K_SOFT_PREMIUM = 0.30     # a sourced soft "not available" raises the required margin this much
HEAT_STAR_FLOOR = 3.5     # consensus_net below which the heat PREMIUM does NOT apply: market_heat
HEAT_STAR_SPAN = 3.5      #   = surplus x demand inflates the cheap-productive-big value tier, so the
#                             bidding-war premium is gated to genuine scarce talent (net >= ~3.5),
#                             never a value play (a rim-protector at net ~3 is cheap, not coveted-scarce)
SURPLUS_MARGIN_FLOOR = 0.10   # never accept near-pure value destruction on the value channel
K_WINNOW_NEED = 0.50      # a max win-now team lowers its need bar by half
NEED_MARGIN_FLOOR = 0.04
K_ABSORB_DISCOUNT = 0.50  # a max-appetite absorber needs this fraction less sweetener to eat a dump

_SURPLUS = _DIMS = _NEEDS = _POSTURE = _URGENCY = _HEAT = None


def load_layers():
    global _SURPLUS, _DIMS, _NEEDS, _POSTURE, _URGENCY, _HEAT
    if _SURPLUS is not None:
        return
    _SURPLUS = {}
    for r in csv.DictReader(open(os.path.join(DATA, "player_surplus.csv"), encoding="utf-8")):
        _SURPLUS[r["player_id"]] = r
    _DIMS = {}
    for r in csv.DictReader(open(os.path.join(DATA, "player_dimensions.csv"), encoding="utf-8")):
        _DIMS[str(int(float(r["player_id"])))] = {d: float(r[d]) for d in DIMS}
    _NEEDS = {}
    for r in csv.DictReader(open(os.path.join(DATA, "team_needs.csv"), encoding="utf-8")):
        _NEEDS.setdefault(r["team_abbr"], {})[r["dimension"]] = float(r["need"])
    _POSTURE = {}
    for r in csv.DictReader(open(os.path.join(DATA, "team_posture.csv"), encoding="utf-8")):
        _POSTURE[r["team_abbr"]] = r
    # Phase 2-A/2-B layers, both optional: absent file -> neutral (every signal defaults to 0).
    _URGENCY = {}
    path = os.path.join(DATA, "team_urgency.csv")
    if os.path.exists(path):
        for r in csv.DictReader(open(path, encoding="utf-8")):
            _URGENCY[r["team_abbr"]] = r
    _HEAT = {}
    path = os.path.join(DATA, "player_market_heat.csv")
    if os.path.exists(path):
        for r in csv.DictReader(open(path, encoding="utf-8")):
            _HEAT[str(r["player_id"]).strip()] = r


# --------------------------------------------------------------------------- #
# Phase 2 urgency + motivation accessors (all default to 0.0 when data absent)
# --------------------------------------------------------------------------- #
def _urg(team, field):
    load_layers()
    r = _URGENCY.get(team)
    if not r:
        return 0.0
    try:
        return float(r.get(field) or 0.0)
    except (ValueError, TypeError):
        return 0.0


def win_now_pressure(team):
    """Computed win-now (urgency layer) plus any sourced owner mandate (news layer), capped at 1."""
    base = _urg(team, "win_now_pressure")
    boost = MO.win_now_boost(team) if MO else 0.0
    return min(1.0, base + boost)


def asset_hunger(team):
    return _urg(team, "asset_hunger")


def shed_pressure(team):
    return _urg(team, "shed_pressure")


def expiring_risk(team):
    return _urg(team, "expiring_risk")


def market_heat(pid):
    load_layers()
    r = _HEAT.get(str(pid))
    try:
        return float(r["market_heat"]) if r else 0.0
    except (ValueError, TypeError, KeyError):
        return 0.0


def seller_motivation(pid):
    """News-sourced motivation of the OWNER to move this player (0 if no override / no news layer)."""
    return MO.seller_motivation(pid) if MO else 0.0


def soft_unavailable(pid):
    return MO.soft_unavailable(pid) if MO else 0.0


def pick_value_weight(team):
    """Continuous replacement for the binary 'rebuilders count picks': how much a team values draft
    capital / youth in a deal, from asset_hunger. Mapped so rebuilders/retoolers weight picks heavily
    (~1.0 once asset_hunger reaches ~0.5) and contenders sit near zero, which is the whole point: a
    correctly-labeled contender never rubber-stamps a picks-heavy lowball. Falls back to the old
    binary gate when the urgency layer is absent."""
    if _URGENCY:
        return max(0.0, min(1.0, asset_hunger(team) / 0.5))
    return 1.0 if posture(team).get("posture") in ("rebuilder", "retooler") else 0.0


def absorb_appetite(team):
    """How willingly a team takes salary ON (for the cap-relief sweetener discount). A floor-seeker
    (below the salary floor) needs salary; a rebuilder collecting assets will eat money for picks."""
    pos = posture(team)
    floor = 0.6 if pos.get("floor_seeking") == "TRUE" else 0.0
    return max(0.0, min(1.0, floor + 0.6 * asset_hunger(team)))


def surplus_net(pid):
    load_layers()
    r = _SURPLUS.get(str(pid))
    if not r or r["surplus_net"] == "":
        return 0.0
    return float(r["surplus_net"])


def player_dims(pid):
    load_layers()
    return _DIMS.get(str(pid), {d: 0.5 for d in DIMS})


def player_position(pid):
    load_layers()
    r = _SURPLUS.get(str(pid))
    return (r["position"] if r else "") or ""


def years_left(pid):
    load_layers()
    r = _SURPLUS.get(str(pid))
    try:
        return int(r["years_left"]) if r else 1
    except (ValueError, TypeError):
        return 1


def player_age(pid):
    load_layers()
    r = _SURPLUS.get(str(pid))
    try:
        return float(r["age"]) if (r and r.get("age")) else None
    except (ValueError, TypeError):
        return None


def player_net(pid):
    load_layers()
    r = _SURPLUS.get(str(pid))
    try:
        return float(r["consensus_net"]) if (r and r["consensus_net"] != "") else 0.0
    except (ValueError, TypeError):
        return 0.0


def team_need(team):
    load_layers()
    return _NEEDS.get(team, {d: 0.0 for d in DIMS})


def posture(team):
    load_layers()
    return _POSTURE.get(team, {})


# --------------------------------------------------------------------------- #
# need-fit in the partner's space (role-adjusted, mirrors acquisition_metric)
# --------------------------------------------------------------------------- #
def need_addressed(pid, salary, need_vec):
    """How well this player fills the team's positive needs: need-weighted average of his
    role-adjusted dims over dims with need > 0.05. Scaled by a rotation-weight so a minimum
    filler cannot 'fill a need'. Returns a scalar ~[0, 1]."""
    dims = player_dims(pid)
    is_big = player_position(pid) in BIG_POSITIONS
    num = den = 0.0
    for d in DIMS:
        need = max(0.0, need_vec.get(d, 0.0))
        if need <= 0.05:
            continue
        contrib = dims.get(d, 0.5)
        if d == "rim_protect_reb" and not is_big and contrib < 0.85:
            contrib = min(contrib, 0.40)        # a wing can't fill a center-sized rim hole
        num += need * contrib
        den += need
    base = (num / den) if den else 0.0
    role_w = 1.0 if salary >= ROTATION_SALARY else 0.3
    return base * role_w


# --------------------------------------------------------------------------- #
# cap-relief sweetener pricing
# --------------------------------------------------------------------------- #
def required_sweetener(absorbed, partner=None):
    """Points MIN must attach for a team to eat the below-par contracts it absorbs. `absorbed` =
    list of (pid, salary) MIN sends that are below par. Price scales with the impact deficit (how
    far below par) amplified by guaranteed years. Calibrated so a mild expiring (Randle, -1.14, 2yr)
    prices to ~a second. Phase 2-C: an eager absorber (floor-seeker / asset-hungry, given `partner`)
    pays less, scaled by absorb_appetite."""
    pts = 0.0
    for pid, _sal in absorbed:
        drag = max(0.0, -surplus_net(pid))
        yrs = max(1, years_left(pid))
        pts += drag * (1.0 + 0.4 * (yrs - 1))
    if partner is not None:
        pts *= (1.0 - K_ABSORB_DISCOUNT * absorb_appetite(partner))
    return round(max(0.0, pts), 2)


def sweetener_label(pts):
    if pts <= 0.6:
        return "a 2nd-round pick"
    if pts <= 1.8:
        return "1-2 2nd-round picks"
    if pts <= 3.5:
        return "a protected 1st (or a 2nd + a young filler)"
    if pts <= 6.0:
        return "an unprotected 1st"
    return "two 1sts (or a 1st + a young rotation player)"


# --------------------------------------------------------------------------- #
# the acceptance decision
# --------------------------------------------------------------------------- #
def _sent_value(pid, partner_posture):
    """Surplus of an outgoing player AS VALUED BY THE PARTNER. A rebuilder/retooler discounts
    a win-now VET (age >= 27) it sends out -- his value doesn't fit their timeline, so they
    will cash him out for assets. A young player is NOT discounted (adverse selection: a
    rebuilder keeps its cornerstones), so prying one loose still takes full value."""
    s = surplus_net(pid)
    if partner_posture in ("rebuilder", "retooler"):
        age = player_age(pid)
        if age is not None and age >= VET_AGE and s > 0:
            return 0.5 * s
    return s


def decide(partner, sends, receives, sweetener_pts=0.0):
    """partner accepts a deal where it SENDS `sends` to MIN and RECEIVES `receives` from MIN.
    Each item: {"pid": str|None, "salary": int, "label": str}. Items with pid=None (filler,
    MLE, picks) carry no surplus and no dims. `sweetener_pts` = asset points MIN attaches
    (picks/young players). Returns the verdict dict."""
    load_layers()
    nv = team_need(partner)
    pos = posture(partner)
    ppost = pos.get("posture", "?")

    # Phase 2-C urgency/motivation, all over the player(s) MIN is acquiring (the partner's SENDS):
    sends_pids = [i["pid"] for i in sends if i.get("pid")]
    win_now = win_now_pressure(partner)                       # acquirer pressure (computed + news)
    seller_mot = max([seller_motivation(p) for p in sends_pids], default=0.0)   # news: motivated seller
    soft = max([soft_unavailable(p) for p in sends_pids], default=0.0)          # sourced "not available"
    pvw = pick_value_weight(partner)                          # how much picks count for this team
    # heat PREMIUM: a bidding war for SCARCE TALENT, NOT a reward for a good contract. market_heat is
    # surplus x demand, which inflates cheap productive role players (the rim-protector value tier),
    # so gate the premium by the coveted player's TALENT (consensus_net): a value play (net ~3) gets
    # no star premium, a real star (net 7+) gets the full one.
    heat_pid = max(sends_pids, key=market_heat) if sends_pids else None
    heat = market_heat(heat_pid) if heat_pid else 0.0
    coveted_net = player_net(heat_pid) if heat_pid else 0.0
    star_gate = max(0.0, min(1.0, (coveted_net - HEAT_STAR_FLOOR) / HEAT_STAR_SPAN))
    heat_premium = K_HEAT_PREMIUM * heat * star_gate

    # margins become functions (defaults reduce to the base constants when signals are 0):
    surplus_margin = max(SURPLUS_MARGIN_FLOOR,
                         SURPLUS_MARGIN - K_WINNOW_VALUE * win_now - K_SELLER_DISCOUNT * seller_mot
                         + heat_premium + K_SOFT_PREMIUM * soft)
    need_margin = max(NEED_MARGIN_FLOOR, NEED_MARGIN * (1.0 - K_WINNOW_NEED * win_now))

    # value axis: outgoing valued at the partner's timeline; incoming = player surplus + WEIGHTED picks.
    sent_value = sum(_sent_value(i["pid"], ppost) for i in sends if i.get("pid"))
    recv_player_value = sum(surplus_net(i["pid"]) for i in receives if i.get("pid"))
    pick_value = sweetener_pts * PT_TO_SURPLUS * pvw          # picks count in proportion to appetite
    recv_value = recv_player_value + pick_value
    delta_value = recv_value - sent_value
    player_delta = recv_player_value - sent_value             # players only (no sweetener)

    sent_need = sum(need_addressed(i["pid"], i["salary"], nv) for i in sends if i.get("pid"))
    recv_need = sum(need_addressed(i["pid"], i["salary"], nv) for i in receives if i.get("pid"))
    need_gain = recv_need - sent_need

    recv_salary = sum(i["salary"] for i in receives)
    sent_salary = sum(i["salary"] for i in sends)
    net_absorb = recv_salary - sent_salary            # >0: partner is net-absorbing MIN salary
    balanced = net_absorb <= BALANCE_TOL              # a real swap, not a salary dump onto them

    best_recv_fit = max([need_addressed(i["pid"], i["salary"], nv)
                         for i in receives if i.get("pid")], default=0.0)

    channels = []
    # (A) value/asset gain. The sweetener counts in proportion to pick_value_weight, so a contender
    # (pvw ~ 0) cannot be moved by picks alone and an asset-hungry team (pvw ~ 1) can. The fit gate
    # is waived for a true asset collector (high pvw).
    if balanced and delta_value >= surplus_margin and (best_recv_fit >= 0.30 or pvw >= 0.5):
        channels.append("value")
    # (B) need-fill -- balanced swap, real need gain, not at a big on-court talent loss.
    if balanced and need_gain >= need_margin and player_delta >= NEED_VALUE_FLOOR:
        channels.append("need")
    # (C) cap-relief DUMP -- the partner net-absorbs MIN salary for a priced sweetener (discounted by
    # its appetite to take salary on), AND MIN is NOT acquiring a real player back.
    absorbed = [(i["pid"], i["salary"]) for i in receives
                if i.get("pid") and surplus_net(i["pid"]) < 0]
    req_pts = required_sweetener(absorbed, partner)
    absorbs = pos.get("absorbs_dumps") == "TRUE"
    min_gets_real_player = any(player_net(i["pid"]) >= 1.2 for i in sends if i.get("pid"))
    if (absorbs and net_absorb > 3_000_000 and sweetener_pts >= req_pts and absorbed
            and not min_gets_real_player):
        channels.append("cap_relief")

    # audit: which sourced news entries touched this decision
    motivation_sources = []
    if MO:
        for p in sends_pids:
            sig = MO.player_signal(p)
            if sig:
                motivation_sources.append({"pid": p, "type": sig["type"], "source": sig["source"],
                                           "date": sig["date"]})
        tsig = MO.team_signal(partner, "win_now_mandate")
        if tsig:
            motivation_sources.append({"team": partner, "type": "win_now_mandate",
                                       "source": tsig["source"], "date": tsig["date"]})

    return {"accepted": bool(channels), "channels": channels,
            "channel": (channels[0] if channels else None),
            "delta_value": round(delta_value, 2), "need_gain": round(need_gain, 3),
            "net_absorb": round(net_absorb), "best_recv_fit": round(best_recv_fit, 3),
            "balanced": balanced,
            "required_sweetener_pts": req_pts, "required_sweetener": sweetener_label(req_pts),
            "posture": ppost, "absorbs_dumps": absorbs,
            # Phase 2-C audit: the urgency/motivation values used and the margins they produced
            "win_now_used": round(win_now, 3), "seller_motivation_used": round(seller_mot, 3),
            "market_heat_used": round(heat, 3), "heat_star_gate": round(star_gate, 3),
            "heat_premium": round(heat_premium, 3), "soft_unavailable_used": round(soft, 3),
            "pick_value_weight": round(pvw, 3), "surplus_margin_used": round(surplus_margin, 3),
            "need_margin_used": round(need_margin, 3), "soft_speculative": soft > 0.0,
            "motivation_sources": motivation_sources}


# --------------------------------------------------------------------------- #
# self-tests
# --------------------------------------------------------------------------- #
def _item(name, salary):
    """Build an item by player name (looks up pid) for the tests."""
    load_layers()
    pid = next((p for p, r in _SURPLUS.items() if r["player_name"] == name), None)
    return {"pid": pid, "salary": salary, "label": name}


def main():
    load_layers()
    MIN_RANDLE = _item("Julius Randle", 33_333_334)
    MIN_GOBERT = _item("Rudy Gobert", 36_500_000)
    filler_min = {"pid": None, "salary": 2_300_000, "label": "min filler"}

    print("=== partner acceptance self-tests ===\n")

    # 1. UTA (rebuilder) sends Markkanen, receives Randle + filler + a first (MIN pays to upgrade).
    mk = _item("Lauri Markkanen", 46_113_154)
    v = decide("UTA", sends=[mk], receives=[MIN_RANDLE, {"pid": None, "salary": 12_780_000, "label": "filler"}],
               sweetener_pts=5.0)
    print(f"1. UTA sends Markkanen for Randle+filler+a 1st (5pts): accepted={v['accepted']} channels={v['channels']}")
    print(f"   d_value={v['delta_value']} need_gain={v['need_gain']} posture={v['posture']} "
          f"(rebuilder cashes out a 28yo vet for an expiring + a pick)\n")

    # 2. CHA (mid, NOT a dump-absorber) asked to eat a Randle dump for a second. Should REJECT.
    v = decide("CHA", sends=[filler_min], receives=[MIN_RANDLE], sweetener_pts=1.0)
    print(f"2. CHA eats Randle dump for a 2nd: accepted={v['accepted']} channels={v['channels']} "
          f"absorbs_dumps={v['absorbs_dumps']} (CHA is a mid team, should NOT absorb)\n")

    # 3. BKN (rebuilder, absorbs) eats a Randle dump. Required sweetener vs attached.
    v_low = decide("BKN", sends=[filler_min], receives=[MIN_RANDLE], sweetener_pts=0.0)
    v_ok = decide("BKN", sends=[filler_min], receives=[MIN_RANDLE], sweetener_pts=2.0)
    print(f"3. BKN eats Randle dump: required={v_low['required_sweetener']} ({v_low['required_sweetener_pts']}pts)")
    print(f"   with NO sweetener: accepted={v_low['accepted']} | with 2 pts: accepted={v_ok['accepted']} "
          f"channels={v_ok['channels']}\n")

    # 4. A contender taking Gobert's value (surplus channel) -- e.g. a rim-needy team.
    v = decide("MIA", sends=[_item("Kel'el Ware", 5_000_000) or filler_min, {"pid": None, "salary": 30_000_000, "label": "filler"}],
               receives=[MIN_GOBERT])
    print(f"4. MIA sends pieces for Gobert (value+rim): accepted={v['accepted']} channels={v['channels']} "
          f"d_value={v['delta_value']} need_gain={v['need_gain']} (Gobert is +3.08 surplus)\n")

    # 5. Kuzma (toxic multi... 1yr but -4.57) dump pricing sanity
    kuzma = _item("Kyle Kuzma", 20_500_000)
    print(f"5. Kuzma dump sweetener: required={sweetener_label(required_sweetener([(kuzma['pid'], kuzma['salary'])]))} "
          f"({required_sweetener([(kuzma['pid'], kuzma['salary'])])}pts) vs Randle "
          f"{required_sweetener([(MIN_RANDLE['pid'], MIN_RANDLE['salary'])])}pts "
          f"(toxic deal should cost more than Randle)")


if __name__ == "__main__":
    main()

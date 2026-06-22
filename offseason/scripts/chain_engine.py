#!/usr/bin/env python3
"""
chain_engine.py -- Path B core: evaluate a SEQUENCE of trades (a chain) where each leg changes
Minnesota's cap and roster, the NEXT leg is judged against that new state, and the chain is scored
on where it ENDS, not leg by leg.

This is the capability the model did not have. The old evaluate_chain just looped legs against
caller-supplied static rows, stopped at the first illegal leg, and carried no state. This carries
state.

Built ADDITIVELY on the existing engine (nothing here edits evaluate_move or build_team_state):
  - evaluate_move.evaluate_move        : the CBA gate (matching, the take-back-more first-apron trip,
                                         exception paths, the post-move apron/tier/distances).
  - build_team_state.derive_tier/toolbox/cap_holds_for : re-derive tier + the permission kit and the
                                         cap basis for the next leg, using the canonical functions.
  - trade_search.tier2_full (in score_end_state) : the four-view + conservative-anchor + risk-adjusted
                                         end-state dP. Reused unchanged.

What is NEW (the gap the spec names):
  1. A mutable carried team-state (apron basis, cap basis, tier, distances, roster, TPE inventory)
     that updates after EVERY leg, so leg i+1 is judged against the post-leg-i state.
  2. The first-apron HARD-CAP LATCH: once any leg takes back more salary (or uses a hard-capping
     exception), MIN is hard-capped at the first apron for the rest of the chain, and every later
     leg is refused if it lands above that line. Enforced HERE in the runner, so evaluate_move is
     untouched (no board re-baselining). This is the single highest correctness risk; self-test B
     exists specifically to catch a chain that forgets to carry the ceiling.

Numbers come from the engine's own constants (league_year_constants.json via evaluate_move.load_*),
never hard-coded: first apron 209.1M, second apron 222.0M, MIN base ~14.64M under the first apron.

DEFERRED per the build decision: three-way salary routing (spec section 4, the automatic search for
a Randle home). Hand-built three-team structures still evaluate leg by leg here; only the AUTOMATIC
search is deferred.

    python chain_engine.py        # self-tests A (shed-then-spend opens room) and B (hard-cap latch)
"""
import os
import sys
import copy

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
sys.path.insert(0, HERE)
import evaluate_move as EM          # noqa: E402
import build_team_state as BTS      # noqa: E402  (import only; main() does not run on import)


# --------------------------------------------------------------------------- #
# The carried state
# --------------------------------------------------------------------------- #
class ChainState:
    """A mutable Minnesota cap+roster state threaded leg to leg. Seeded from a team_state row; updated
    by apply_leg after each LEGAL leg. evaluate_move reads from self.ts, so every field it consults
    (apron_team_salary, tier, the can_* permissions, tpe_max_single_available, season) is kept fresh.

    Cap basis: carried as a running number and updated by the base salary delta each leg, then under_cap
    is recomputed so derive_tier's under/over-cap branch stays correct. This matches evaluate_move's own
    treatment (it nets actual salary and ignores rookie-min roster-charge drift on player-count change),
    so the chain inherits that documented approximation rather than introducing a new one. MIN never
    approaches the cap in these chains, so the approximation is immaterial to its tier."""

    def __init__(self, ts_row, const, label="MIN"):
        self.label = label
        self.ts = copy.deepcopy(ts_row)        # evaluate_move reads this dict
        self.const = const
        self.cap = const["salary_cap"]
        self.cap_team_salary = ts_row.get("cap_team_salary", ts_row["apron_team_salary"])
        self.rookie_min = const["min_salary_by_yos"]["0"]
        self.count = ts_row.get("num_under_contract", 0)   # salaried contracts; drives the charge to 12
        # hard-cap latch (sticky once set, monotonic)
        self.hard_capped = bool(ts_row.get("hard_capped"))
        self.hard_cap_line = ts_row.get("hard_cap_line")
        self.under_cap_warned = False
        # roster ledger (pid deltas; the seed roster ids are not enumerated, we track in/out)
        self.roster_out = set()
        self.roster_in = set()
        # TPE inventory: single-use, non-combinable. Seeded with the known largest single TPE from the
        # team_state (the smaller-TPE breakdown is not stored); created TPEs append; a TPE is CONSUMED
        # (dropped) when a leg absorbs through it, so a later leg cannot reuse it.
        self.tpes = [v for v in [ts_row.get("tpe_max_single_available")] if v]
        self.history = []                      # human-readable per-leg trail

    def snapshot(self):
        return {
            "apron_team_salary": self.ts["apron_team_salary"],
            "tier": self.ts["tier"],
            "under_first_apron": self.const["first_apron"] - self.ts["apron_team_salary"],
            "under_tax": self.const["luxury_tax"] - self.ts["apron_team_salary"],
            "hard_capped": self.hard_capped,
            "hard_cap_line": self.hard_cap_line,
            "tpe_max_single_available": self.ts.get("tpe_max_single_available"),
        }


# --------------------------------------------------------------------------- #
# Apply one leg against the carried state
# --------------------------------------------------------------------------- #
def apply_leg(state, leg):
    """Evaluate ONE leg against the CURRENT carried state, enforce the carried first-apron hard cap,
    and if legal update the carried state for the next leg. Returns evaluate_move's result dict
    augmented with chain fields (legal_against_carried_state, chain_hard_cap_blocked, created_tpe).

    leg = {label, outgoing:[{label,salary,pid?,trade_kicker_pct?}], incoming:[...],
           exception_used?: 'none'|'tpe'|'full_mle'|'taxpayer_mle'|'bae'|'bird'|'sign_and_trade'}"""
    const = state.const
    out = leg.get("outgoing", [])
    inc = leg.get("incoming", [])
    exc = leg.get("exception_used", "none")
    r = EM.evaluate_move(state.ts, const, out, inc, exception_used=exc)

    out_base = sum(p["salary"] for p in out)
    inc_base = sum(p["salary"] for p in inc)
    inc_inflated = sum(p["salary"] * (1 + float(p.get("trade_kicker_pct") or 0)) for p in inc)
    n_out = sum(1 for p in out if p["salary"] > 0)
    n_in = sum(1 for p in inc if p["salary"] > 0)

    # --- roster-charge drift: evaluate_move nets salary only and never re-charges empty slots when the
    #     headcount changes (a 2-for-1 leaves a slot the CBA fills to 12 at the rookie min). Recompute
    #     the (12 - count) charge on the corrected count and adjust the apron, so a headcount-changing
    #     leg cannot silently understate the apron near a line. The chain would otherwise COMPOUND the
    #     drift leg over leg. ---
    new_count = state.count - n_out + n_in
    charge_delta = (max(0, BTS.ROSTER_TARGET - new_count) - max(0, BTS.ROSTER_TARGET - state.count)) * state.rookie_min
    corrected_apron = None
    if r.get("new_apron_team_salary") is not None:
        corrected_apron = r["new_apron_team_salary"] + charge_delta
    r["corrected_apron_team_salary"] = corrected_apron

    # --- cross-leg HARD-CAP LATCH (the runner's job; evaluate_move sees only one leg and does NOT read
    #     an incoming hard_capped flag, so a Bird re-sign or any non-hard-capping move would sail past a
    #     ceiling a PRIOR leg set unless we enforce it here). Checked against the corrected apron. ---
    r["chain_hard_cap_blocked"] = False
    if state.hard_capped and state.hard_cap_line is not None and corrected_apron is not None and r["legal"]:
        if corrected_apron > state.hard_cap_line:
            over = corrected_apron - state.hard_cap_line
            tier_word = "second-apron" if state.hard_cap_line == const["second_apron"] else "first-apron"
            r["legal"] = False
            r["chain_hard_cap_blocked"] = True
            r["failing_constraint"] = (
                f"chain hard cap: MIN was {tier_word} hard-capped at ${state.hard_cap_line:,.0f} by an "
                f"earlier leg; this leg lands at ${corrected_apron:,.0f}, ${over:,.0f} over")

    # --- re-check THIS leg's OWN hard cap against the corrected apron (catches a headcount-changing
    #     take-back-more / exception leg that evaluate_move waved through on the un-recharged apron). ---
    if r["legal"] and corrected_apron is not None:
        own_line = r.get("hard_cap_line") if (r.get("hard_cap_set", "none") != "none" or r.get("hard_cap_tripped")) else None
        if own_line is not None and corrected_apron > own_line:
            over = corrected_apron - own_line
            r["legal"] = False
            r["chain_hard_cap_blocked"] = True
            r["failing_constraint"] = (f"hard cap (roster-charge corrected): this leg trips a cap at "
                                       f"${own_line:,.0f} and lands at ${corrected_apron:,.0f}, ${over:,.0f} over")

    r["legal_against_carried_state"] = r["legal"]
    if not r["legal"]:
        state.history.append((leg.get("label", ""), "ILLEGAL: " + r["failing_constraint"]))
        return r

    # --- legal: roll the carried state forward (use the corrected apron) ---
    state.count = new_count
    state.ts["num_under_contract"] = new_count
    state.ts["apron_team_salary"] = corrected_apron
    # cap basis: net actual salary INCLUDING the incoming trade kicker (parity with the apron basis),
    # plus the same charge drift. MIN sits ~$42M over the cap line so under_cap never flips in content,
    # but keeping the bases consistent matters for a deep-shed chain that nears the cap.
    state.cap_team_salary = state.cap_team_salary - out_base + inc_inflated + charge_delta
    state.ts["cap_team_salary"] = state.cap_team_salary
    under_cap = state.cap_team_salary < state.cap
    tier = BTS.derive_tier(corrected_apron, under_cap, const)
    state.ts["tier"] = tier
    state.ts.update(BTS.toolbox(tier))         # refresh the whole permission kit for the next leg
    state.ts["distance_to_tax"] = const["luxury_tax"] - corrected_apron
    state.ts["distance_to_first_apron"] = const["first_apron"] - corrected_apron
    state.ts["distance_to_second_apron"] = const["second_apron"] - corrected_apron
    state.ts["cap_room"] = max(0, state.cap - state.cap_team_salary)

    # under_cap is the DEFERRED section-4 cap-space-absorption gap: evaluate_move routes an under-cap
    # team through 125% matching instead of absorbing into room, so the NEXT straight-trade leg's
    # legality is approximate. Surface it rather than silently mis-judge.
    if under_cap and not state.under_cap_warned:
        state.under_cap_warned = True
        state.history.append(("WARNING", "chain drove MIN UNDER the cap; under-cap straight-trade matching "
                              "is the deferred section-4 cap-space gap, read the next straight-trade leg with caution"))

    for p in out:
        if p.get("pid"):
            state.roster_out.add(p["pid"]); state.roster_in.discard(p["pid"])
    for p in inc:
        if p.get("pid"):
            state.roster_in.add(p["pid"]); state.roster_out.discard(p["pid"])

    # --- TPE CONSUMPTION: a TPE is single-use and non-combinable. If this leg absorbed via a TPE,
    #     consume (drop) the smallest available TPE that legally covered it, so a later leg cannot
    #     reuse it. (Remainders cannot be re-sliced, so the whole TPE is spent.) ---
    if exc == "tpe" and state.tpes:
        usable = sorted(t for t in state.tpes if t + 250_000 >= inc_inflated)
        if usable:
            state.tpes.remove(usable[0])
            r["tpe_consumed"] = usable[0]

    # --- HARD-CAP LATCH: sticky once any leg sets a cap (take-back-more or a hard-capping exception).
    #     Monotonic: never raise or clear an existing tighter ceiling. (At the second apron, evaluate_move
    #     skips the take-back-more block entirely and its own matching already forbids taking back more,
    #     so the latch correctly relies on that and never needs to set a second-apron line itself.) ---
    if r.get("take_back_more") or r.get("hard_cap_set", "none") != "none" or r.get("hard_cap_tripped"):
        line = r.get("hard_cap_line") or const["first_apron"]
        state.hard_cap_line = line if state.hard_cap_line is None else min(state.hard_cap_line, line)
        state.hard_capped = True
        state.ts["hard_capped"] = True
        state.ts["hard_cap_line"] = state.hard_cap_line

    # --- created TPE: a PURE send-out (a player leaves with NO incoming salary, exception_used=none)
    #     cleanly creates a single-use, non-combinable TPE = the outgoing base. An under-match SWAP does
    #     NOT (per simultaneous-trade rules); this CONSERVATIVELY under-counts available TPE. ---
    if exc == "none" and out_base > 0 and inc_base == 0:
        state.tpes.append(out_base)
        r["created_tpe"] = out_base

    # refresh the TPE summary fields evaluate_move reads
    state.ts["tpe_max_single_available"] = max(state.tpes) if state.tpes else 0
    state.ts["tpe_total_available"] = sum(state.tpes)

    tail = f" | HARD-CAPPED @ ${state.hard_cap_line:,.0f}" if state.hard_capped else ""
    state.history.append((leg.get("label", ""),
                          f"legal -> apron ${corrected_apron:,.0f} ({tier}){tail}"))
    return r


def run_chain(initial_ts_row, const, legs, label="MIN"):
    """Thread `legs` through a fresh carried state. Does NOT hard-stop at the first illegal leg (so the
    end state is still inspectable); records per-leg legality. Returns (state, leg_results)."""
    state = ChainState(initial_ts_row, const, label=label)
    results = []
    for leg in legs:
        results.append(apply_leg(state, leg))
    return state, results


# --------------------------------------------------------------------------- #
# Future-capital terms + honesty flags (spec sections 5 and 7). Pure, additive.
# --------------------------------------------------------------------------- #
# Pick asset-points on the SAME scale trade_search.MIN_PICKS uses (a first ~3.5, a second ~0.7), so
# the future axis is commensurate with the sweetener ladder. Net = acquired minus spent.
PICK_PTS = {"first": 3.5, "first_unprotected": 3.5, "first_protected": 3.0, "first_late": 3.0,
            "swap": 1.5, "second": 0.7, "2nd": 0.7}
YOUNG_AGE = 24.0          # at/under this an incoming player is treated as youth (value as a FLOOR)


def pick_points(label):
    key = str(label).strip().lower().replace(" ", "_")
    for k, v in PICK_PTS.items():
        if k in key:
            return v
    return 3.0            # an unlabeled "first" defaults to a protected-first value


def _young_incoming(in_pids):
    """Incoming pids that are young/cost-controlled (age <= YOUNG_AGE), PLUS those whose age is missing.
    The model undervalues youth, so the spec wants them carried as a FLOOR with a warning. A MISSING age
    is treated as potentially-young (rookies are the most likely to have incomplete age data AND the
    population the flag most needs to protect), so the warning never silently under-fires. Returns
    (young:[(pid,age)], unknown_age:[pid])."""
    import partner_acceptance as PA
    PA.load_layers()
    young, unknown = [], []
    for pid in in_pids:
        if str(pid) not in PA._SURPLUS:        # not a resolvable real player (placeholder/filler) -> skip
            continue
        age = PA.player_age(pid)
        if age is None:
            unknown.append(pid)
        elif age <= YOUNG_AGE:
            young.append((pid, age))
    return young, unknown


def future_capital(state, base_row, const, picks_in=None, picks_out=None, in_pids=None):
    """The section-5 future axis: net first-round picks (asset-points), young talent (flagged as a
    floor), and apron room gained. apron_room_gained = salary shed = base apron minus final apron."""
    picks_in = picks_in or []
    picks_out = picks_out or []
    apron_room_gained = base_row["apron_team_salary"] - state.ts["apron_team_salary"]
    net_pick_pts = sum(pick_points(p) for p in picks_in) - sum(pick_points(p) for p in picks_out)
    young, unknown = _young_incoming(in_pids or [])
    return {
        "net_pick_pts": round(net_pick_pts, 2),
        "picks_in": picks_in, "picks_out": picks_out,
        "apron_room_gained": apron_room_gained,
        "final_under_first_apron": const["first_apron"] - state.ts["apron_team_salary"],
        "young_incoming": young, "unknown_age_incoming": unknown,
        "young_floor_warning": (
            "FLOOR: young/cost-controlled (or unknown-age) returns valued on the pick/asset-point scale, "
            "not the model's raw rating (the model undervalues youth). Read their on-court dP as a floor."
            if (young or unknown) else ""),
    }


def lane_flag(leg):
    """Per-leg in-lane / out-of-lane tag (spec section 7). In lane = MIN ACQUIRES a real on-court
    player (the validated acquisition lane). Out of lane = MIN is the SELLER (sheds a real player for
    picks/cap/expirings), where partner_acceptance carries the un-calibrated caveat (16% recall)."""
    import partner_acceptance as PA
    PA.load_layers()
    # Tag by transaction STRUCTURE, not a net threshold: MIN acquiring ANY real player (a pid that
    # resolves to a surplus row) is in lane regardless of that player's net (a +0.36 starter is still an
    # acquisition). Out of lane only when MIN ships a real player and gets back no real player (picks/
    # cap/expirings) -- the seller case the scope doc flags as un-calibrated (16% recall).
    in_real = [p["pid"] for p in leg.get("incoming", []) if p.get("pid") and str(p["pid"]) in PA._SURPLUS]
    out_real = [p["pid"] for p in leg.get("outgoing", []) if p.get("pid") and str(p["pid"]) in PA._SURPLUS]
    if in_real:
        return ("in_lane", "MIN acquires a real player (validated acquisition lane)")
    if any(PA.player_net(p) >= 0.5 for p in out_real):
        return ("out_of_lane", "MIN is the SELLER (sheds a real player for picks/cap/expirings); acceptance "
                               "is un-calibrated here (scope doc, 16% recall), read the verdict with caution")
    return ("neutral", "filler/cap-only leg")


# --------------------------------------------------------------------------- #
# End-state title scoring (spec section 5). Reuses trade_search.tier2_full unchanged.
# --------------------------------------------------------------------------- #
def score_end_state(eng, out_pkg, in_players, label="chain end state"):
    """Score the chain's FINAL roster with the existing four-view + conservative-anchor + risk-adjusted
    machinery. out_pkg: [(MIN_name, salary, kicker)] net removed from MIN; in_players: [(pid, salary)]
    net acquired. Returns the tier2_full rec (views, anchor, risk_adj, with_dp, without_dp, avail)."""
    import trade_search as TS
    # de-dupe: drop any incoming pid that is already a MIN baseline player, so build_min_rotation cannot
    # double-list (and double-weight) a kept player passed in as an acquisition.
    min_pids = set(TS.MIN.values())
    in_players = [p for p in in_players if p[0] not in min_pids]
    if not in_players:
        # pure shed (MIN acquires nobody): no key incoming player to risk-haircut. Score the consensus
        # dP of the resulting roster (the shed player drops to replacement) and report anchor==risk_adj.
        scen = TS.min_scenario(out_pkg, [])
        dp = TS.consensus_dp(eng, scen)
        return {"views": {"consensus": dp, "box": None, "rapm": None, "darko": None}, "anchor": dp,
                "risk_adj": dp, "with_dp": dp, "without_dp": dp, "avail": 1.0, "key": None,
                "gauntlet_okc": 0.0, "gauntlet_sas": 0.0, "darko_avail": False, "pure_shed": True}
    rec = {"out_pkg": out_pkg, "in_players": in_players, "partner": label, "pkg": label,
           "combo": [(p[0], p[1], 0.0, p[0], "") for p in in_players]}
    TS.tier2_full(eng, rec)
    return rec


# --------------------------------------------------------------------------- #
# Self-tests (hand-checkable). A: shed-then-spend opens room. B: hard-cap latch.
# --------------------------------------------------------------------------- #
def _ok(name, cond, detail=""):
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f" -> {detail}" if detail else ""))
    return bool(cond)


def selftests():
    const = EM.load_constants("2026-27")
    base = EM.load_team_state("MIN", "2026-27", "base")
    FA = const["first_apron"]
    print(f"Seed MIN 2026-27 base: apron ${base['apron_team_salary']:,} tier={base['tier']} "
          f"under-first-apron ${FA - base['apron_team_salary']:,} tpe_max ${base.get('tpe_max_single_available') or 0:,}")
    print(f"Constants read from engine: tax ${const['luxury_tax']:,} first_apron ${FA:,} "
          f"second_apron ${const['second_apron']:,}\n")
    passed = []

    # ---- Self-test A: shed Randle for a DOWNGRADE (opens real room), then spend via the Conley TPE,
    #      keep Gobert. Confirms room opens as expected and leg 2 is legal AGAINST the post-leg-1 state.
    print("Self-test A: shed-then-spend opens room (Randle downgrade -> ~10M room -> Conley TPE absorb)")
    legsA = [
        {"label": "L1 shed Randle for a $22M downgrade",
         "outgoing": [{"label": "Randle", "salary": 33_333_334, "pid": "203944"}],
         "incoming": [{"label": "downgrade wing ($22M)", "salary": 22_000_000, "pid": "DOWNGRADE"}]},
        {"label": "L2 absorb a $10M wing via the Conley TPE",
         "outgoing": [],
         "incoming": [{"label": "absorbed wing ($10M)", "salary": 10_000_000, "pid": "ABSORB"}],
         "exception_used": "tpe"},
    ]
    stA, rA = run_chain(base, const, legsA)
    room_before = FA - base["apron_team_salary"]
    room_after_l1 = FA - rA[0]["new_apron_team_salary"]
    passed.append(_ok("A1 leg1 legal (take back less)", rA[0]["legal"],
                      f"apron ${rA[0]['new_apron_team_salary']:,} ({rA[0]['new_tier']})"))
    passed.append(_ok("A1 opens ~$11.3M of first-apron room", abs((room_after_l1 - room_before) - 11_333_334) < 1,
                      f"room {room_before/1e6:.2f}M -> {room_after_l1/1e6:.2f}M (+{(room_after_l1-room_before)/1e6:.2f}M)"))
    passed.append(_ok("A1 is a clean under-match swap (leg 1 sets no hard cap)",
                      (not rA[0]["take_back_more"]) and rA[0].get("hard_cap_set", "none") == "none"))
    passed.append(_ok("A2 leg2 legal vs the POST-leg-1 carried state", rA[1]["legal_against_carried_state"],
                      f"apron ${rA[1].get('new_apron_team_salary',0):,} via Conley TPE"))
    passed.append(_ok("A2 TPE absorb hard-caps at the first apron but lands UNDER it (legal)",
                      stA.hard_capped and stA.ts["apron_team_salary"] < FA,
                      f"final apron ${stA.ts['apron_team_salary']:,} < first apron ${FA:,}"))
    passed.append(_ok("A2 end state still over_cap_under_tax, Gobert untouched", stA.ts["tier"] == "over_cap_under_tax",
                      f"final apron ${stA.ts['apron_team_salary']:,}"))

    # ---- Self-test B: the hard-cap LATCH. Leg 1 takes back more (sets the first-apron cap), then a
    #      Bird re-sign that evaluate_move ALONE would wave through must be BLOCKED by the carried cap.
    print("\nSelf-test B: hard-cap latch (take-back-more on L1 must block an over-apron Bird re-sign on L2)")
    legsB = [
        {"label": "L1 Randle ($33.33M) for a $39.49M guard (takes back $6.16M more)",
         "outgoing": [{"label": "Randle", "salary": 33_333_334, "pid": "203944"}],
         "incoming": [{"label": "lead guard ($39.49M)", "salary": 39_491_282, "pid": "GUARD"}]},
        {"label": "L2 re-sign Dosunmu ($16.5M) via Bird",
         "outgoing": [],
         "incoming": [{"label": "Dosunmu (Bird re-sign)", "salary": 16_500_000, "pid": "1630245"}],
         "exception_used": "bird"},
    ]
    stB, rB = run_chain(base, const, legsB)
    passed.append(_ok("B1 take-back-more leg legal and SETS the first-apron cap",
                      rB[0]["legal"] and rB[0]["take_back_more"] and stB.hard_cap_line == FA,
                      f"apron ${rB[0]['new_apron_team_salary']:,}, latched @ ${stB.hard_cap_line:,}"))
    passed.append(_ok("B2 Bird re-sign BLOCKED by the carried hard cap (the latch fires)",
                      (not rB[1]["legal_against_carried_state"]) and rB[1]["chain_hard_cap_blocked"],
                      rB[1]["failing_constraint"]))
    # control: the SAME Bird re-sign on a state WITHOUT the latch is legal -> proves the latch did the work
    post_l1_no_latch = copy.deepcopy(base)
    post_l1_no_latch["apron_team_salary"] = rB[0]["new_apron_team_salary"]   # same apron, but hard_capped stays False
    ctrl = EM.evaluate_move(post_l1_no_latch, const, [],
                            [{"label": "Dosunmu (Bird)", "salary": 16_500_000}], exception_used="bird")
    passed.append(_ok("B2 control: WITHOUT the latch evaluate_move would WRONGLY allow it", ctrl["legal"],
                      "proves the block comes from the carried ceiling, not from evaluate_move itself"))

    # ---- Self-test C: relaxed-untouchable hand path (section 6). The board search would NEVER propose
    #      sending Edwards (OFF_LIMITS and absent from MIN_PIECES); a hand-specified scenario can.
    print("\nSelf-test C: relaxed-untouchable hand path (Edwards is sendable in a hand-built scenario)")
    import trade_search as TS
    scenC = TS.min_scenario([("Edwards", 48_924_624, 0.0)], [("1629630", 42_166_510)])
    rotC = [p["nba_player_id"] for p in scenC["post_rotations"]["MIN"]]
    passed.append(_ok("C Edwards (untouchable) enters override_ids via the hand path",
                      TS.MIN["Edwards"] in scenC["override_ids"]))
    passed.append(_ok("C Edwards removed from the post-trade rotation (evaluated, not pre-blocked)",
                      TS.MIN["Edwards"] not in rotC))

    # ---- Self-test D: honesty lane flags (section 7) ----
    print("\nSelf-test D: honesty flags (in-lane acquisition vs out-of-lane seller leg)")
    acq_leg = {"incoming": [{"pid": "1629630", "salary": 42_166_510, "label": "Morant"}],
               "outgoing": [{"pid": None, "salary": 25_000_000, "label": "filler"}]}
    sell_leg = {"incoming": [{"pid": None, "salary": 2_300_000, "label": "min filler"}],
                "outgoing": [{"pid": "203944", "salary": 33_333_334, "label": "Randle"}]}
    passed.append(_ok("D acquisition leg tagged in_lane", lane_flag(acq_leg)[0] == "in_lane"))
    passed.append(_ok("D MIN-sheds-Randle-for-cap leg tagged out_of_lane", lane_flag(sell_leg)[0] == "out_of_lane"))

    # ---- future-capital terms on chain A ----
    fc = future_capital(stA, base, const, picks_in=["a protected 1st"], picks_out=["a 2nd"])
    passed.append(_ok("future-capital: apron room gained == net salary shed; net picks computed",
                      fc["apron_room_gained"] == base["apron_team_salary"] - stA.ts["apron_team_salary"],
                      f"room gained ${fc['apron_room_gained']:,}, net picks {fc['net_pick_pts']:+.1f} pts"))

    # ---- Self-test E: latch PERSISTENCE + MONOTONICITY (the 3-leg chain the review recommended).
    #      L1 take-back-more sets the first-apron cap; L2 a clean swap must NOT clear it; L3 a Bird re-sign
    #      that pushes over the carried ceiling must be blocked, and the line must never have loosened.
    print("\nSelf-test E: latch persists across a clean intermediate leg and never loosens (monotonic)")
    legsE = [
        {"label": "L1 Randle for a $39.49M guard (take-back-more)",
         "outgoing": [{"label": "Randle", "salary": 33_333_334, "pid": "203944"}],
         "incoming": [{"label": "guard ($39.49M)", "salary": 39_491_282, "pid": "GUARD"}]},
        {"label": "L2 clean $5M-for-$4M swap (stays under; must NOT clear the latch)",
         "outgoing": [{"label": "out $5M", "salary": 5_000_000}],
         "incoming": [{"label": "in $4M", "salary": 4_000_000}]},
        {"label": "L3 Bird re-sign $12M (pushes over the carried first-apron cap)",
         "outgoing": [], "incoming": [{"label": "Bird $12M", "salary": 12_000_000}], "exception_used": "bird"},
    ]
    stE, rE = run_chain(base, const, legsE)
    passed.append(_ok("E1 take-back-more sets the first-apron latch", rE[0]["legal"] and stE.hard_cap_line == FA))
    passed.append(_ok("E2 clean intermediate leg legal AND latch persists at the first apron (monotonic)",
                      rE[1]["legal_against_carried_state"] and stE.hard_capped and stE.hard_cap_line == FA))
    passed.append(_ok("E3 later Bird re-sign blocked by the still-active carried cap",
                      (not rE[2]["legal_against_carried_state"]) and rE[2]["chain_hard_cap_blocked"]))

    # ---- Self-test F: TPE single-use (the HIGH bug). A second TPE absorb must FAIL once the only TPE
    #      is consumed by the first. (Two $10M absorbs cannot both clear one $10.77M Conley TPE.) ----
    print("\nSelf-test F: a TPE is consumed on use and cannot absorb twice")
    legsF = [
        {"label": "L1 absorb $10M via the Conley TPE", "outgoing": [],
         "incoming": [{"label": "wing A ($10M)", "salary": 10_000_000}], "exception_used": "tpe"},
        {"label": "L2 absorb ANOTHER $10M via 'the' TPE (should fail; it is spent)", "outgoing": [],
         "incoming": [{"label": "wing B ($10M)", "salary": 10_000_000}], "exception_used": "tpe"},
    ]
    stF, rF = run_chain(base, const, legsF)
    passed.append(_ok("F1 first TPE absorb legal and consumes the Conley TPE",
                      rF[0]["legal"] and rF[0].get("tpe_consumed") and stF.ts["tpe_max_single_available"] == 0))
    passed.append(_ok("F2 second TPE absorb FAILS (single-use: the TPE is gone)",
                      not rF[1]["legal_against_carried_state"], rF[1]["failing_constraint"]))

    # ---- youth-floor flag (section 7): fires for a young incoming AND on missing age (no under-fire) ----
    print("\nYouth-floor honesty flag (fires for young AND unknown-age incoming)")
    import partner_acceptance as PA
    PA.load_layers()
    young_pid = next((pid for pid in sorted(PA._SURPLUS) if (PA.player_age(pid) or 99) <= 22), None)
    passed.append(_ok("youth-floor flag fires for a young incoming",
                      bool(young_pid) and bool(future_capital(stA, base, const, in_pids=[young_pid])["young_floor_warning"])))
    PA._SURPLUS["_TESTBLANK"] = {"player_name": "Test Rookie", "age": "", "consensus_net": "", "team_abbr": "XXX",
                                 "salary_2026_27": "5000000", "years_left": "4", "position": "G", "surplus_net": ""}
    passed.append(_ok("youth-floor flag fires on MISSING age (no silent under-fire)",
                      bool(future_capital(stA, base, const, in_pids=["_TESTBLANK"])["young_floor_warning"])))
    del PA._SURPLUS["_TESTBLANK"]

    print(f"\n{sum(passed)}/{len(passed)} checks passed")
    for st, tag in [(stA, "A"), (stB, "B")]:
        print(f"\nchain {tag} trail:")
        for label, note in st.history:
            print(f"   {label}: {note}")
    return all(passed)


# --------------------------------------------------------------------------- #
# Worked example (spec section 9): a real in-lane two-leg reshape, scored end to end.
#   Leg 1: shed Randle for a real DOWNGRADE (opens room, keeps Gobert).
#   Leg 2: spend the room by absorbing a real wing through the Conley TPE.
# Heavy (builds the sim Engine), so it is gated behind --worked.
# --------------------------------------------------------------------------- #
def _pick_real(sal_lo, sal_hi, exclude=()):
    """Pick a real, deterministic demo target in a salary band. Excludes bigs (C/C-F/F-C): MIN keeps
    Gobert, so a sensible reshape adds a guard/wing into the need, not a redundant center."""
    import partner_acceptance as PA
    PA.load_layers()
    BIG = ("C", "C-F", "F-C")
    cands = []
    for pid, r in PA._SURPLUS.items():
        if pid in exclude or r["team_abbr"] == "MIN":
            continue
        if PA.player_position(pid) in BIG:
            continue
        try:
            sal = float(r["salary_2026_27"] or 0)
        except (ValueError, TypeError):
            continue
        net = PA.player_net(pid)
        if sal_lo <= sal <= sal_hi and r["consensus_net"] not in ("", None) and net >= 0.4:
            cands.append((pid, int(sal), net, r["player_name"], r["team_abbr"]))
    cands.sort(key=lambda x: (-x[2], x[0]))
    return cands[0] if cands else None


def worked_example():
    import trade_search as TS
    import partner_acceptance as PA
    PA.load_layers()
    const = EM.load_constants("2026-27")
    base = EM.load_team_state("MIN", "2026-27", "base")
    FA = const["first_apron"]

    dgrade = _pick_real(20_000_000, 24_000_000)
    absorb = _pick_real(8_000_000, 10_500_000, exclude={dgrade[0]} if dgrade else set())
    print("=" * 78)
    print("WORKED EXAMPLE (in-lane 2-leg reshape): shed Randle for a downgrade, spend via Conley TPE, keep Gobert")
    print("=" * 78)
    print(f"  Leg 1 target (downgrade, ~$22M): {dgrade[3]} ({dgrade[4]}, ${dgrade[1]:,}, net {dgrade[2]:+.2f})")
    print(f"  Leg 2 target (absorb via Conley TPE): {absorb[3]} ({absorb[4]}, ${absorb[1]:,}, net {absorb[2]:+.2f})")

    legs = [
        {"label": f"L1 Randle -> {dgrade[3]} (downgrade, opens room)",
         "partner": dgrade[4],
         "outgoing": [{"label": "Randle", "salary": 33_333_334, "pid": "203944"}],
         "incoming": [{"label": dgrade[3], "salary": dgrade[1], "pid": dgrade[0]}],
         "picks_out": [], "picks_in": []},
        {"label": f"L2 absorb {absorb[3]} via the Conley TPE",
         "outgoing": [],
         "incoming": [{"label": absorb[3], "salary": absorb[1], "pid": absorb[0]}],
         "exception_used": "tpe", "picks_out": [], "picks_in": []},
    ]

    # 1) cap chain (legality + latch + state carry)
    state, results = run_chain(base, const, legs)
    print("\n-- CAP CHAIN (state carried leg to leg) --")
    for leg, r in zip(legs, results):
        lane, why = lane_flag(leg)
        apron = r.get("corrected_apron_team_salary") or r.get("new_apron_team_salary") or 0
        print(f"  [{ 'LEGAL' if r['legal'] else 'ILLEGAL'}] {leg['label']}")
        print(f"        apron -> ${apron:,} (roster-charge corrected) | lane: {lane} ({why})")
        if not r["legal"]:
            print(f"        WHY: {r['failing_constraint']}")

    # 2) acceptance on the in-lane acquisition leg (partner gets Randle, sends the downgrade)
    print("\n-- ACCEPTANCE (leg 1 partner) --")
    accepted = None
    for swp in (0.0, 0.7, 1.4, 3.5, 5.0):
        a = PA.decide(dgrade[4],
                      sends=[{"pid": dgrade[0], "salary": dgrade[1], "label": dgrade[3]}],
                      receives=[{"pid": "203944", "salary": 33_333_334, "label": "Randle"}],
                      sweetener_pts=swp)
        if a["accepted"]:
            accepted = (swp, a)
            break
    if accepted:
        swp, a = accepted
        print(f"  {dgrade[4]} accepts via {a['channel']} at sweetener {swp} pts (posture {a['posture']})")
    else:
        print(f"  {dgrade[4]} does NOT accept Randle for {dgrade[3]} even at MIN's chest "
              f"(a downgrade swap onto a non-absorber; would need a different partner or a real sweetener)")

    # 3) end-state title scoring (four views + conservative anchor + risk-adjusted)
    print("\n-- END-STATE TITLE SCORING (the chain's final roster vs baseline) --")
    rec = score_end_state(TS.Engine(2500), [("Randle", 33_333_334, 0.0)],
                          [(dgrade[0], dgrade[1]), (absorb[0], absorb[1])])
    v = rec["views"]
    print(f"  views: consensus {v['consensus']:+.2f} | box {v.get('box',0):+.2f} | rapm {v.get('rapm',0):+.2f}"
          + (f" | darko {v['darko']:+.2f}" if v.get('darko') is not None else ""))
    print(f"  conservative ANCHOR (min of views): {rec['anchor']:+.2f}pp")
    print(f"  risk-adjusted dP (availability-weighted): {rec['risk_adj']:+.2f}pp")

    # 4) future-capital + honesty flags
    fc = future_capital(state, base, const, picks_in=[], picks_out=[], in_pids=[dgrade[0], absorb[0]])
    print("\n-- FUTURE-CAPITAL READ + HONESTY FLAGS --")
    print(f"  final cap: apron ${state.ts['apron_team_salary']:,} ({state.ts['tier']}), "
          f"${fc['final_under_first_apron']:,} under the first apron, ${const['luxury_tax']-state.ts['apron_team_salary']:,} under the tax")
    print(f"  apron room gained (net salary shed): ${fc['apron_room_gained']:,}")
    print(f"  net first-round picks: {fc['net_pick_pts']:+.1f} asset-pts")
    if fc["young_floor_warning"]:
        names = ", ".join([PA._SURPLUS[p]["player_name"] for p, _ in fc["young_incoming"]]
                          + [PA._SURPLUS[p]["player_name"] for p in fc["unknown_age_incoming"]])
        print(f"  YOUNG-FLOOR FLAG ({names}): {fc['young_floor_warning']}")
    for leg in legs:
        lane, why = lane_flag(leg)
        if lane == "out_of_lane":
            print(f"  OUT-OF-LANE: {leg['label']} -> {why}")
    print("\n  TWO-AXIS READ -> title: anchor {:+.2f}pp / risk-adj {:+.2f}pp | future: {:+.1f} net pick-pts, "
          "${:,} room gained".format(rec["anchor"], rec["risk_adj"], fc["net_pick_pts"], fc["apron_room_gained"]))


if __name__ == "__main__":
    if "--worked" in sys.argv:
        worked_example()
    else:
        ok = selftests()
        sys.exit(0 if ok else 1)

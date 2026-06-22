#!/usr/bin/env python3
"""
chain_content.py -- the thin content-driver on top of chain_engine.py (Path B).

Hand-specify a "door" (a named multi-leg reshape with REALISTIC, hand-picked targets and sweeteners)
and get the full two-axis report back:
  - the cap chain (legality + the hard-cap latch, leg by leg, against the carried state),
  - partner acceptance per leg (which channel fires, the required sweetener, the in/out-of-lane tag),
  - the end-state title impact (four views + conservative anchor + risk-adjusted) WITH a risk
    DECOMPOSITION so the anchor-vs-risk-adjusted gap is legible (availability, playoff translation,
    Edwards usage overlap, the with/without branches),
  - the final cap position, and
  - the future-capital breakdown (net picks, apron room) + honesty flags.

Hand-picked targets are the whole point: the auto-picker finds steals the other team will not actually
trade (it grabbed Denver's Braun for Randle, which Denver never does). The content doors specify real
targets and the sweetener the partner needs. Section 4 (automatic routing) stays deferred.

    python chain_content.py        # demo: the in-lane shed-and-spend door, end to end
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import chain_engine as CE          # noqa: E402
import evaluate_move as EM         # noqa: E402
import partner_acceptance as PA    # noqa: E402
import risk_overlay as G           # noqa: E402
import trade_search as TS          # noqa: E402


def pid_by_name(name):
    """Resolve a display name to the player_surplus pid (the id score_end_state/decide key on)."""
    PA.load_layers()
    target = CE._young_incoming and name  # touch import; no-op
    for pid, r in PA._SURPLUS.items():
        if r.get("player_name") == name:
            return pid
    # fall back to a normalized match
    nrm = name.lower().replace(".", "").replace("'", "").strip()
    for pid, r in PA._SURPLUS.items():
        if (r.get("player_name", "").lower().replace(".", "").replace("'", "").strip()) == nrm:
            return pid
    return None


def _derive_score(legs):
    """Derive the net roster change for end-state scoring from the cap legs: MIN-name players that leave
    (out_pkg for min_scenario) and real acquired pids that STAY (not flipped in a later leg)."""
    PA.load_layers()
    min_names = set(TS.MIN)
    out_names, in_players, sent = [], [], set()
    for leg in legs:
        for o in leg.get("outgoing", []):
            if o.get("label") in min_names:
                out_names.append((o["label"], o["salary"], float(o.get("trade_kicker_pct") or 0)))
            if o.get("pid") and str(o["pid"]) in PA._SURPLUS:
                sent.add(str(o["pid"]))
        for i in leg.get("incoming", []):
            if i.get("pid") and str(i["pid"]) in PA._SURPLUS:
                in_players.append((str(i["pid"]), i["salary"]))
    in_players = [(p, s) for (p, s) in in_players if p not in sent]   # drop acquired-then-flipped
    return out_names, in_players


def door_report(eng, door, base=None, const=None):
    """Run one door end to end and print the two-axis report. Returns the computed pieces for reuse."""
    PA.load_layers()
    const = const or EM.load_constants("2026-27")
    base = base or EM.load_team_state("MIN", "2026-27", "base")

    print("=" * 78)
    print(f"DOOR: {door['name']}")
    print(f"  thesis: {door['thesis']}")
    print("=" * 78)

    # 1) cap chain
    state, results = CE.run_chain(base, const, door["legs"])
    all_legal = True
    print("\n-- CAP CHAIN (state carried leg to leg) --")
    for leg, r in zip(door["legs"], results):
        lane, _why = CE.lane_flag(leg)
        ok = r["legal_against_carried_state"]
        all_legal = all_legal and ok
        apron = r.get("corrected_apron_team_salary") or r.get("new_apron_team_salary") or 0
        print(f"  [{'LEGAL' if ok else 'ILLEGAL'}] {leg['label']}   (lane: {lane})")
        print(f"        -> apron ${apron:,.0f}")
        if not ok:
            print(f"        WHY: {r['failing_constraint']}")
    fa, tax = const["first_apron"], const["luxury_tax"]
    print(f"  FINAL: apron ${state.ts['apron_team_salary']:,.0f} ({state.ts['tier']}), "
          f"${fa - state.ts['apron_team_salary']:,.0f} under first apron, ${tax - state.ts['apron_team_salary']:,.0f} under tax"
          + (f", HARD-CAPPED @ ${state.hard_cap_line:,.0f}" if state.hard_capped else ""))

    # 2) acceptance per leg (legs that name a partner)
    print("\n-- PARTNER ACCEPTANCE (per leg) --")
    for leg in door["legs"]:
        if not leg.get("partner"):
            print(f"  {leg['label']}: signing/exception leg (no partner to accept)")
            continue
        lane, _ = CE.lane_flag(leg)
        acc = None
        for swp in sorted({leg.get("sweetener_pts", 0.0), 0.0, 0.7, 1.4, 3.5, 5.0, 7.0, 8.5}):
            a = PA.decide(leg["partner"], leg.get("partner_sends", []), leg.get("partner_receives", []), sweetener_pts=swp)
            if a["accepted"]:
                acc = (swp, a)
                break
        if acc:
            swp, a = acc
            print(f"  {leg['partner']} ({leg['label']}): ACCEPT via {a['channel']} at {swp} sweetener-pts "
                  f"(posture {a['posture']})  [lane: {lane}]")
        else:
            print(f"  {leg['partner']} ({leg['label']}): NO DEAL even at MIN's full chest  [lane: {lane}]")
        if lane == "out_of_lane":
            print("        ^ out-of-lane (MIN selling): acceptance is un-calibrated (scope doc, 16% recall)")

    # 3) end-state scoring + the RISK DECOMPOSITION (why anchor != risk-adj)
    out_names, in_players = _derive_score(door["legs"])
    # SQUEEZE COST: if a re-sign leg (Bird) was BLOCKED by the carried hard cap, that baseline player
    # WALKS, so the honest end-state must drop him (not silently keep a guy the cap says you cannot keep).
    inv_min = {str(v): k for k, v in TS.MIN.items()}
    for leg, r in zip(door["legs"], results):
        if (not r["legal_against_carried_state"]) and leg.get("exception_used") == "bird":
            for inc in leg.get("incoming", []):
                nm = inv_min.get(str(inc.get("pid")))
                if nm and nm not in [o[0] for o in out_names]:
                    out_names.append((nm, inc["salary"], 0.0))
                    print(f"  [SQUEEZE COST] {nm}'s re-sign is blocked by the hard cap -> modeled as WALKING "
                          f"in the end-state (the star's number is net of the guard you lose to fit him)")
    rec = CE.score_end_state(eng, out_names, in_players, label=door["name"])
    v = rec["views"]
    print("\n-- END-STATE TITLE IMPACT (final roster vs baseline) --")
    box = f"{v['box']:+.2f}" if v.get("box") is not None else "n/a"
    rapm = f"{v['rapm']:+.2f}" if v.get("rapm") is not None else "n/a"
    print(f"  views: consensus {v['consensus']:+.2f} | box {box} | rapm {rapm}"
          + (f" | darko {v['darko']:+.2f}" if v.get('darko') is not None else "") + " (pp)")
    print(f"  conservative ANCHOR (lowest view): {rec['anchor']:+.2f}pp    risk-adjusted: {rec['risk_adj']:+.2f}pp")
    if rec.get("pure_shed") or not rec.get("key"):
        print("  (pure shed: MIN acquires no one, so there is no key incoming player to risk-haircut; "
              "anchor == risk-adj == the consensus dP of losing the shed player to replacement.)")
    else:
        key = rec["key"]
        kr = TS.PV.get(key, {})
        read = kr.get("translation_read", "")
        po = G.PO_MULT.get(read, 0.98)
        um = G.usage_mult(key, eng.dims)
        print("  WHY the risk haircut bites (decomposition on the top-two incoming players):")
        print(f"     key 1 = {kr.get('player_name', key)} (net {kr.get('consensus_net', '?')}), "
              f"availability {rec['avail']:.2f}, playoff x{po:.2f} ({read or 'n/a'}), Edwards-overlap x{um:.2f}")
        if rec.get("key2"):
            k2r = TS.PV.get(rec["key2"], {})
            print(f"     key 2 = {k2r.get('player_name', rec['key2'])} (net {k2r.get('consensus_net', '?')}), "
                  f"availability {rec['avail2']:.2f}  <-- now priced (was ignored under single-key)")
        print(f"     with (both play, haircut applied) {rec['with_dp']:+.2f}pp   vs   "
              f"without (both hurt -> replacement) {rec['without_dp']:+.2f}pp")
        print(f"     risk_adj (4-state availability EV) = {rec['risk_adj']:+.2f}pp")
    print(f"  gauntlet vs OKC {rec.get('gauntlet_okc', 0):+.1f}pp | vs SAS {rec.get('gauntlet_sas', 0):+.1f}pp")

    # 4) future capital + honesty
    in_pids = [p for p, _ in in_players]
    fc = CE.future_capital(state, base, const, picks_in=door.get("picks_in", []),
                           picks_out=door.get("picks_out", []), in_pids=in_pids)
    print("\n-- FUTURE CAPITAL + HONESTY FLAGS --")
    print(f"  net first-round picks: {fc['net_pick_pts']:+.1f} asset-pts "
          f"(in: {fc['picks_in'] or 'none'} / out: {fc['picks_out'] or 'none'})")
    print(f"  apron room gained (net salary shed): ${fc['apron_room_gained']:,.0f}")
    if fc["young_floor_warning"]:
        nm = ", ".join([PA._SURPLUS[p]["player_name"] for p, _ in fc["young_incoming"]]
                       + [PA._SURPLUS[p]["player_name"] for p in fc["unknown_age_incoming"]])
        print(f"  YOUNG-FLOOR ({nm}): {fc['young_floor_warning']}")
    if not all_legal:
        print("  NOTE: a leg is ILLEGAL as specified; the end-state score assumes the chain completes. Fix the leg.")
    print(f"\n  TWO-AXIS  ->  title: anchor {rec['anchor']:+.2f}pp / risk-adj {rec['risk_adj']:+.2f}pp   |   "
          f"future: {fc['net_pick_pts']:+.1f} pick-pts, ${fc['apron_room_gained']:,.0f} room, "
          f"${fa - state.ts['apron_team_salary']:,.0f} under the apron")
    return {"state": state, "rec": rec, "fc": fc, "all_legal": all_legal}


# --------------------------------------------------------------------------- #
# Demo door (validates the driver + shows the format and the risk decomposition)
# --------------------------------------------------------------------------- #
def demo_door():
    PA.load_layers()
    braun = pid_by_name("Christian Braun")
    jerome = pid_by_name("Ty Jerome")
    return {
        "name": "Demo: shed-and-spend reshape (keep Gobert)",
        "thesis": "shed Randle for a wing, add a guard through the Conley TPE, keep Gobert",
        "legs": [
            {"label": "L1 Randle -> Christian Braun", "partner": "DEN",
             "outgoing": [{"label": "Randle", "salary": 33_333_334, "pid": "203944"}],
             "incoming": [{"label": "Christian Braun", "salary": 21_551_726, "pid": braun}],
             "partner_sends": [{"pid": braun, "salary": 21_551_726, "label": "Christian Braun"}],
             "partner_receives": [{"pid": "203944", "salary": 33_333_334, "label": "Randle"}],
             "sweetener_pts": 0.0},
            {"label": "L2 absorb Ty Jerome via the Conley TPE",
             "outgoing": [], "incoming": [{"label": "Ty Jerome", "salary": 9_220_050, "pid": jerome}],
             "exception_used": "tpe"},
        ],
        "picks_in": [], "picks_out": [],
    }


def _ps(name):
    """(pid, 2026-27 salary) for a display name, from player_surplus."""
    PA.load_layers()
    pid = pid_by_name(name)
    sal = int(float(PA._SURPLUS[pid]["salary_2026_27"])) if (pid and PA._SURPLUS[pid].get("salary_2026_27")) else 0
    return pid, sal


# --------------------------------------------------------------------------- #
# The three draft-night doors (hand-picked targets, per Bobby's calls). Leg 2 is the realistic MIN
# follow-on (re-sign Dosunmu via Bird), which also reveals whether leg 1 hard-caps the chain.
# --------------------------------------------------------------------------- #
def content_doors():
    PA.load_layers()
    RANDLE, NAZ, SHANNON, DOSUNMU = "203944", "1629675", "1630545", "1630245"
    kyrie, kyrie_s = _ps("Kyrie Irving")
    gafford, gafford_s = _ps("Daniel Gafford")
    murray, murray_s = _ps("Keegan Murray")
    monk, monk_s = _ps("Malik Monk")
    dosunmu_resign = 16_500_000     # projected Bird re-sign

    swing = {
        "name": "DOOR 1 - THE SWING (win-now): cash flexibility for Kyrie",
        "thesis": "Randle + Naz for Kyrie + Gafford (DAL, speculative), then re-sign Dosunmu. A star-guard bet.",
        "legs": [
            {"label": "L1 Randle + Naz -> Kyrie Irving + Daniel Gafford (DAL)", "partner": "DAL",
             "outgoing": [{"label": "Randle", "salary": 33_333_334, "pid": RANDLE},
                          {"label": "Naz", "salary": 23_333_333, "pid": NAZ}],
             "incoming": [{"label": "Kyrie Irving", "salary": kyrie_s, "pid": kyrie},
                          {"label": "Daniel Gafford", "salary": gafford_s, "pid": gafford}],
             "partner_sends": [{"pid": kyrie, "salary": kyrie_s, "label": "Kyrie Irving"},
                               {"pid": gafford, "salary": gafford_s, "label": "Daniel Gafford"}],
             "partner_receives": [{"pid": RANDLE, "salary": 33_333_334, "label": "Randle"},
                                  {"pid": NAZ, "salary": 23_333_333, "label": "Naz"}],
             "sweetener_pts": 5.0},
            {"label": "L2 re-sign Dosunmu via Bird (the follow-on; watch the squeeze)",
             "outgoing": [], "incoming": [{"label": "Dosunmu (Bird re-sign)", "salary": dosunmu_resign, "pid": DOSUNMU}],
             "exception_used": "bird"},
        ],
        "picks_out": ["the 2026 first", "the 2033 own first"], "picks_in": [],
    }
    flip = {
        "name": "DOOR 2 - THE FLIP (middleman): turn Randle into Murray + Monk, keep powder dry",
        "thesis": "Randle + filler for Keegan Murray (young wing) + Malik Monk (scoring guard) from SAC, "
                  "then re-sign Dosunmu. Value + youth at a lighter pick cost than the MIL/Turner haul.",
        "legs": [
            {"label": "L1 Randle + Shannon -> Keegan Murray + Malik Monk (SAC)", "partner": "SAC",
             "outgoing": [{"label": "Randle", "salary": 33_333_334, "pid": RANDLE},
                          {"label": "Shannon", "salary": 2_800_000, "pid": SHANNON}],
             "incoming": [{"label": "Keegan Murray", "salary": murray_s, "pid": murray},
                          {"label": "Malik Monk", "salary": monk_s, "pid": monk}],
             "partner_sends": [{"pid": murray, "salary": murray_s, "label": "Keegan Murray"},
                               {"pid": monk, "salary": monk_s, "label": "Malik Monk"}],
             "partner_receives": [{"pid": RANDLE, "salary": 33_333_334, "label": "Randle"},
                                  {"pid": SHANNON, "salary": 2_800_000, "label": "Shannon"}],
             "sweetener_pts": 5.0},
            {"label": "L2 re-sign Dosunmu via Bird (the follow-on; watch the squeeze)",
             "outgoing": [], "incoming": [{"label": "Dosunmu (Bird re-sign)", "salary": dosunmu_resign, "pid": DOSUNMU}],
             "exception_used": "bird"},
        ],
        "picks_out": ["the 2026 first", "the 2033 own first"], "picks_in": [],
    }
    stockpile = {
        "name": "DOOR 3 - THE STOCKPILE (patient): the true sell, FLAGGED out-of-lane",
        "thesis": "Dump Randle for cap room (attach a 2nd); bank flexibility. Note: Gobert has no clean home (the deferred 4-team-routing wall), so a full teardown is blocked.",
        "legs": [
            {"label": "L1 Randle -> a rebuilder (salary dump, attach a 2nd)", "partner": "BKN",
             "outgoing": [{"label": "Randle", "salary": 33_333_334, "pid": RANDLE}],
             "incoming": [{"label": "min filler", "salary": 2_300_000, "pid": None}],
             "partner_sends": [{"pid": None, "salary": 2_300_000, "label": "min filler"}],
             "partner_receives": [{"pid": RANDLE, "salary": 33_333_334, "label": "Randle"}],
             "sweetener_pts": 0.7},
        ],
        "picks_out": ["a 2nd"], "picks_in": [],
    }
    return [swing, flip, stockpile]


if __name__ == "__main__":
    eng = TS.Engine(2500)
    if "--doors" in sys.argv:
        for d in content_doors():
            door_report(eng, d)
            print("\n")
    else:
        door_report(eng, demo_door())

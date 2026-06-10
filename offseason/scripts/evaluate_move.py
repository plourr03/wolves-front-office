#!/usr/bin/env python3
"""
evaluate_move.py

The transaction evaluator (team-state schema section 7). Answers one question
fast: is a proposed move legal, and where does it leave the acquiring team. Every
team_state field maps to a check here; that is the test that the schema is complete.

    evaluate_move(team_state, constants, outgoing, incoming, pick_and_cash, exception_used)

Inputs:
  team_state    a team_state row dict (the acquiring team, season, scenario)
  constants     the league_year_constants row for that season
  outgoing      list of player dicts the team SENDS. Each: {label, salary,
                optional team_option_year, optional team_option_exercised (bool)}
  incoming      list of player dicts the team RECEIVES. Each: {label, salary,
                optional trade_kicker_pct (e.g. 0.15)}
  pick_and_cash optional {picks: [...], cash: <number>} (cash gated at 2nd apron)
  exception_used  none | full_mle | taxpayer_mle | tpe | sign_and_trade

Returns the section-7 contract: legal, failing_constraint (plain language),
matching_ok, aggregation_ok, takeback_ok, st_ok, prior_tpe_ok, cash_ok,
option_ok, hard_cap_tripped, hard_cap_level, new_apron_team_salary, new_tier,
new_distances, and the minimum context (matching limit, salaries).

Baked in per the build spec:
  - tiered matching brackets read from constants (not a flat percentage),
  - single-TPE absorb via tpe_max_single_available, since TPEs cannot be combined,
  - aggregation only when can_aggregate, no take-back-more at the second apron,
  - incoming inflated by any trade kicker BEFORE matching,
  - sign-and-trade and prior-year-TPE use gated on their booleans,
  - team-option-year outgoing players count only if the option is exercised,
  - hard cap re-checked against the apron line AFTER the move lands.

A two-stage star chain is supported by evaluate_chain([...]) which runs legs in
order and reports where a chain breaks.

Run the self-tests:
    python evaluate_move.py
"""

import os
import csv
import json

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")


# ----------------------------------------------------------------------------- #
# loaders (so tests and callers can pull real rows)
# ----------------------------------------------------------------------------- #
def load_constants(season):
    with open(os.path.join(DATA, "league_year_constants.json"), encoding="utf-8") as fh:
        return json.load(fh)["seasons"][season]


def load_team_state(team, season, scenario="base"):
    with open(os.path.join(DATA, "team_state.json"), encoding="utf-8") as fh:
        for r in json.load(fh)["rows"]:
            if r["team_abbr"] == team and r["season"] == season and r["scenario_id"] == scenario:
                return r
    raise KeyError(f"no team_state row for {team} {season} {scenario}")


# ----------------------------------------------------------------------------- #
# matching
# ----------------------------------------------------------------------------- #
def matching_limit(outgoing_salary, tier, const):
    """Max incoming salary allowed for the given outgoing, by tier, using the
    bracket thresholds encoded in the constants (do not flatten to 1.25)."""
    t1, t2 = const["match_t1"], const["match_t2"]
    tm = const["trade_matching"]
    if tier in ("under_cap", "over_cap_under_tax", "taxpayer"):   # below first apron
        if outgoing_salary <= t1:
            return 2.00 * outgoing_salary + 250_000
        if outgoing_salary <= t2:
            return outgoing_salary + t1
        return 1.25 * outgoing_salary + 250_000
    if tier == "first_apron":
        return tm["first_apron_pct"] * outgoing_salary          # ~1.10x (confirm flag in constants)
    return tm["second_apron_pct"] * outgoing_salary             # 1.00x dollar-for-dollar


def _inflated(incoming):
    """Incoming cap hit including any trade kicker (the kicker inflates matching)."""
    out = []
    for p in incoming:
        kick = float(p.get("trade_kicker_pct") or 0)
        out.append({"label": p.get("label", "?"), "salary": p["salary"] * (1 + kick),
                    "kicker": kick, "base": p["salary"]})
    return out


# ----------------------------------------------------------------------------- #
# the evaluator
# ----------------------------------------------------------------------------- #
def evaluate_move(team_state, const, outgoing, incoming, pick_and_cash=None, exception_used="none"):
    ts = team_state
    tier = ts["tier"]
    pick_and_cash = pick_and_cash or {}
    inc = _inflated(incoming)
    inc_total = sum(p["salary"] for p in inc)

    res = {
        "legal": True, "failing_constraint": "",
        "matching_ok": True, "aggregation_ok": True, "takeback_ok": True,
        "st_ok": True, "prior_tpe_ok": True, "cash_ok": True, "option_ok": True,
        "hard_cap_tripped": False, "hard_cap_level": "none",
        "hard_cap_set": "none", "hard_cap_room": None, "take_back_more": False,
        "exception_used": exception_used,
    }

    def fail(field, msg):
        res[field] = False
        res["legal"] = False
        if not res["failing_constraint"]:
            res["failing_constraint"] = msg

    # --- conditional team-option outgoing: a team-option-year player counts as
    # outgoing salary only if that option is (or would be) exercised. Also collect
    # no-trade-clause holders (their consent is required: a contingency, not illegal). ---
    usable_out, ntc_needed = [], []
    for p in outgoing:
        if p.get("team_option_year") == ts["season"] and p.get("team_option_exercised") is False:
            fail("option_ok", f"cannot trade {p.get('label','?')}: {ts['season']} team "
                              f"option not exercised, he is not under contract to send")
        else:
            usable_out.append(p)
            if p.get("no_trade_clause"):
                ntc_needed.append(p.get("label", "?"))
    res["ntc_waivers_needed"] = ntc_needed

    # An outbound trade kicker inflates the player's salary for MATCHING (raising the
    # sending team's take-back room); apron relief is the base salary, since the bonus
    # conveys to the acquiring team. (Gobert's 7.5% kicker is the canonical case.)
    def match_sal(p):
        return p["salary"] * (1 + float(p.get("trade_kicker_pct") or 0))
    out_salary = sum(match_sal(p) for p in usable_out)     # kicker-inflated, for matching
    out_base = sum(p["salary"] for p in usable_out)         # base, for apron relief
    n_out = sum(1 for p in usable_out if p["salary"] > 0)

    # --- sign-and-trade gate ---
    if exception_used == "sign_and_trade" and not ts["can_acquire_sign_and_trade"]:
        fail("st_ok", f"sign-and-trade acquisition barred at tier {tier}")

    # --- cash gate ---
    if pick_and_cash.get("cash", 0) and not ts["can_send_cash"]:
        fail("cash_ok", f"cannot send cash at tier {tier}")

    # --- the salary path. Exceptions (TPE/MLE/BAE/room) absorb or sign without
    # salary matching, bounded by the exception amount. A straight trade or a
    # sign-and-trade goes through tiered matching. A plain signing with no
    # exception is legal only for minimums. ---
    EXC_AMT = {"full_mle": const["full_mle"], "taxpayer_mle": const["taxpayer_mle"],
               "bae": const["bae"], "room_exception": const["room_exception"]}
    EXC_AVAIL = {"full_mle": ts["full_mle_available"], "taxpayer_mle": ts["taxpayer_mle_available"],
                 "bae": ts["bae_available"], "room_exception": ts["room_exception_available"]}
    vet_min = const["min_salary_by_yos"]["10+"]

    if exception_used == "tpe":
        tpe_max = ts.get("tpe_max_single_available") or 0
        if not ts["can_use_prior_year_tpe"]:        # prior-year TPEs barred at 2nd apron
            fail("prior_tpe_ok", f"cannot use a prior-year trade exception at tier {tier}")
        if inc_total > tpe_max + 250_000:
            fail("matching_ok", f"incoming ${inc_total:,.0f} exceeds the largest single "
                                f"TPE ${tpe_max:,.0f} (TPEs cannot be combined)")
    elif exception_used in EXC_AMT:
        if not EXC_AVAIL[exception_used]:
            fail("matching_ok", f"{exception_used} not available at tier {tier}")
        if inc_total > EXC_AMT[exception_used] + 250_000:
            fail("matching_ok", f"incoming ${inc_total:,.0f} exceeds the {exception_used} "
                                f"amount ${EXC_AMT[exception_used]:,.0f}")
    elif exception_used == "bird":
        # re-signing your OWN free agent via Bird (or Early-Bird) rights is legal OVER the
        # cap up to the max, with NO minimum restriction and NO hard cap by itself. (A team
        # already at the second apron is separately constrained, but a Bird re-sign does not
        # trip the first-apron hard cap the way the MLE/TPE/S&T do.) The apron is still tracked.
        pass
    elif not usable_out and inc_total > 0:
        # plain signing with no exception: only minimums are allowed over the cap
        if any(p["salary"] > vet_min + 250_000 for p in inc):
            fail("matching_ok", f"over-cap signing needs an exception; only minimums "
                                f"(<= ${vet_min:,.0f}) allowed with exception_used=none")
    else:
        # straight trade or sign-and-trade: tiered salary matching
        if n_out > 1 and not ts["can_aggregate"]:
            fail("aggregation_ok", f"cannot aggregate {n_out} outgoing salaries at tier {tier} "
                                   f"(second apron: each outgoing must match on its own)")
        if tier == "second_apron":
            inc_sorted = sorted((p["salary"] for p in inc), reverse=True)
            out_sorted = sorted((match_sal(p) for p in usable_out if p["salary"] > 0), reverse=True)
            if inc_total > out_salary:
                fail("takeback_ok", f"second apron: incoming ${inc_total:,.0f} exceeds "
                                    f"outgoing ${out_salary:,.0f} (cannot take back more)")
            if len(inc_sorted) > len(out_sorted):
                fail("matching_ok", "second apron: more incoming contracts than outgoing "
                                    "(no aggregation, each must be matched individually)")
            else:
                for i, isal in enumerate(inc_sorted):
                    if isal > out_sorted[i] + 250_000:
                        fail("matching_ok", f"second apron: incoming ${isal:,.0f} not matched "
                                            f"1-for-1 by an outgoing contract")
                        break
        else:
            limit = matching_limit(out_salary, tier, const)
            res["matching_limit"] = round(limit)
            if inc_total > limit:
                fail("matching_ok", f"incoming ${inc_total:,.0f} exceeds the {tier} matching "
                                    f"limit ${limit:,.0f} on ${out_salary:,.0f} outgoing")

    # --- where the move lands, and the hard-cap recheck AFTER it lands ---
    # apron relief uses the BASE outgoing (kicker conveys to the acquirer, not relief)
    new_apron = ts["apron_team_salary"] - out_base + inc_total
    res["new_apron_team_salary"] = round(new_apron)
    res["new_distances"] = {
        "to_tax": round(const["luxury_tax"] - new_apron),
        "to_first_apron": round(const["first_apron"] - new_apron),
        "to_second_apron": round(const["second_apron"] - new_apron),
    }
    res["new_tier"] = ("over_cap_under_tax" if new_apron < const["luxury_tax"]
                       else "taxpayer" if new_apron < const["first_apron"]
                       else "first_apron" if new_apron < const["second_apron"]
                       else "second_apron")

    # hard cap: which line does this move trip, and does the team land under it?
    HARD_FIRST = {"full_mle", "bae", "sign_and_trade", "tpe"}   # tpe is MIN-specific per the rules ref
    if exception_used in HARD_FIRST:
        res["hard_cap_tripped"] = True
        res["hard_cap_level"] = "first_apron"
        line = const["first_apron"]
    elif exception_used == "taxpayer_mle":
        res["hard_cap_tripped"] = True
        res["hard_cap_level"] = "second_apron"
        line = const["second_apron"]
    else:
        line = None
    if line is not None:
        res["hard_cap_line"] = line
        res["hard_cap_room"] = round(line - new_apron)
        if new_apron > line:
            fail("matching_ok", f"hard cap: using {exception_used} caps the team at "
                                f"${line:,.0f}; the move lands at ${new_apron:,.0f}, "
                                f"${new_apron - line:,.0f} over")

    # --- take-back-more (expanded 125% matching) hard cap ---
    # In a straight trade (or S&T), taking back MORE salary than you send out triggers a
    # FIRST-APRON hard cap for the rest of the season. This is the trigger that sits under
    # the whole keep-Gobert lane: most realistic additions take back extra salary, which
    # caps MIN at the first apron and is what squeezes a subsequent Dosunmu re-sign. A team
    # already at/over the line cannot take back more without landing over the cap (illegal).
    straight = exception_used in ("none", "sign_and_trade") and usable_out and inc_total > 0
    if straight and inc_total > out_base and tier != "second_apron":
        res["take_back_more"] = True
        fa = const["first_apron"]
        if line is None:                      # do not loosen a tighter exception-set cap
            res["hard_cap_set"] = "first_apron"
            res["hard_cap_line"] = fa
            res["hard_cap_room"] = round(fa - new_apron)   # room left for SUBSEQUENT moves this season
        if new_apron > fa:
            fail("takeback_ok", f"taking back more (${inc_total:,.0f} in vs ${out_base:,.0f} out) "
                                f"hard-caps at the first apron ${fa:,.0f}; the move lands at "
                                f"${new_apron:,.0f}, ${new_apron - fa:,.0f} over")

    return res


def evaluate_chain(legs):
    """Run a two-stage (or longer) chain in order. Each leg is a dict of evaluate_move
    kwargs. Returns per-leg results and where the chain breaks, for the star-case
    'setup trade returns assets, then repackage' path."""
    out = []
    for i, leg in enumerate(legs):
        leg = dict(leg)
        label = leg.pop("label", f"leg {i+1}")
        r = evaluate_move(**leg)
        out.append({"leg": i + 1, "label": label, "result": r})
        if not r["legal"]:
            return {"chain_legal": False, "broke_at": i + 1, "legs": out}
    return {"chain_legal": True, "broke_at": None, "legs": out}


# ----------------------------------------------------------------------------- #
# self-tests: obviously legal and obviously illegal deals
# ----------------------------------------------------------------------------- #
def _check(name, got_legal, want_legal, res):
    ok = "PASS" if got_legal == want_legal else "FAIL"
    note = res["failing_constraint"] if not got_legal else f"lands ${res['new_apron_team_salary']:,} ({res['new_tier']})"
    print(f"  [{ok}] {name}: legal={got_legal} -> {note}")
    return ok == "PASS"


def main():
    c = load_constants("2026-27")
    min_base = load_team_state("MIN", "2026-27", "base")        # over_cap_under_tax, tiered_125
    okc = load_team_state("OKC", "2026-27", "base")             # second_apron
    print(f"MIN base tier={min_base['tier']} tpe_max=${min_base['tpe_max_single_available']:,} "
          f"can_aggregate={min_base['can_aggregate']}")
    print(f"OKC base tier={okc['tier']} can_aggregate={okc['can_aggregate']}\n")

    passed = []
    # 1. LEGAL: MIN sends Randle ($33.33M), takes back $35M. Outgoing>29M -> 125%+250K = $41.9M limit.
    r = evaluate_move(min_base, c, [{"label": "Randle", "salary": 33_333_334}],
                      [{"label": "incoming wing", "salary": 35_000_000}])
    passed.append(_check("MIN Randle for $35M (within 125% band)", r["legal"], True, r))

    # 2. ILLEGAL matching: MIN sends $10M, takes back $30M (10M is mid-bracket: limit = 10M + t1 ~= $18M).
    r = evaluate_move(min_base, c, [{"label": "filler", "salary": 10_000_000}],
                      [{"label": "star", "salary": 30_000_000}])
    passed.append(_check("MIN $10M out for $30M in (over band)", r["legal"], False, r))

    # 3. LEGAL but barely: MIN full-MLE signing ($15.048M) lands just under the
    #    first-apron hard cap ($209.1M). Shows how little first-apron room MIN has.
    r = evaluate_move(min_base, c, [], [{"label": "full MLE signing", "salary": 15_048_000}],
                      exception_used="full_mle")
    passed.append(_check("MIN full-MLE signing lands just under first-apron hard cap", r["legal"], True, r))

    # 3b. ILLEGAL hard cap: with Dosunmu re-signed (apron bumped to ~$200M), the same
    #     MLE signing pushes MIN over the first-apron hard cap. Exercises the
    #     post-move recheck against hard_cap_line.
    min_post_dosunmu = dict(min_base)
    min_post_dosunmu["apron_team_salary"] = 200_000_000
    r = evaluate_move(min_post_dosunmu, c, [], [{"label": "full MLE signing", "salary": 15_048_000}],
                      exception_used="full_mle")
    passed.append(_check("MIN full-MLE signing post-Dosunmu trips first-apron hard cap", r["legal"], False, r))

    # 3c. LEGAL take-back-more SETS a first-apron hard cap with limited room (the keep-Gobert
    #     lane): Kyrie $39.49M in for Randle $33.33M out -> +$6.16M back -> hard cap $209.1M.
    r = evaluate_move(min_base, c, [{"label": "Randle", "salary": 33_333_334}],
                      [{"label": "Kyrie", "salary": 39_491_282}])
    ok3c = (r["legal"] and r["take_back_more"] and r["hard_cap_set"] == "first_apron"
            and r["hard_cap_room"] < 16_500_000)
    print(f"  [{'PASS' if ok3c else 'FAIL'}] MIN take-back-more (Kyrie for Randle): legal={r['legal']} "
          f"take_back_more={r['take_back_more']} hard_cap_set={r['hard_cap_set']} room=${r['hard_cap_room']:,} "
          f"-> Dosunmu ~$16.5M does NOT fit under the season cap")
    passed.append(ok3c)

    # 3c2. LEGAL Bird re-sign over the cap (Dosunmu $16.5M): blessed natively, no hard cap.
    r = evaluate_move(min_base, c, [], [{"label": "Dosunmu (Bird re-sign)", "salary": 16_500_000}],
                      exception_used="bird")
    passed.append(_check("MIN re-signs Dosunmu $16.5M via Bird (legal over cap, no hard cap)",
                         r["legal"] and r["hard_cap_set"] == "none", True, r))

    # 3d. ILLEGAL: a take-back-more that LANDS over the first apron is not allowed.
    mpd = dict(min_base); mpd["apron_team_salary"] = 200_000_000
    r = evaluate_move(mpd, c, [{"label": "a", "salary": 30_000_000}, {"label": "b", "salary": 20_000_000}],
                      [{"label": "big star", "salary": 62_000_000}])
    passed.append(_check("take-back-more landing over first apron (illegal)", r["legal"], False, r))

    # 4. LEGAL TPE absorb: MIN absorbs a $10M player via the $10.77M Conley TPE, no outgoing.
    r = evaluate_move(min_base, c, [], [{"label": "absorbed contract", "salary": 10_000_000}],
                      exception_used="tpe")
    passed.append(_check("MIN absorbs $10M via single TPE (under first-apron hard cap)", r["legal"], True, r))

    # 5. ILLEGAL TPE: MIN tries to absorb $12M via TPE (> $10.77M largest single; can't combine).
    r = evaluate_move(min_base, c, [], [{"label": "too big", "salary": 12_000_000}],
                      exception_used="tpe")
    passed.append(_check("MIN absorbs $12M via TPE (exceeds largest single)", r["legal"], False, r))

    # 6. ILLEGAL second apron aggregation: OKC aggregates two players for a bigger incoming.
    r = evaluate_move(okc, c, [{"label": "p1", "salary": 15_000_000}, {"label": "p2", "salary": 12_000_000}],
                      [{"label": "big incoming", "salary": 26_000_000}])
    passed.append(_check("OKC aggregates 2 outgoing (second apron forbids)", r["legal"], False, r))

    # 7. ILLEGAL second apron take-back-more: OKC sends $20M, takes back $21M.
    r = evaluate_move(okc, c, [{"label": "p1", "salary": 20_000_000}],
                      [{"label": "incoming", "salary": 21_000_000}])
    passed.append(_check("OKC takes back more than sent (second apron)", r["legal"], False, r))

    # 8. LEGAL second apron 1-for-1: OKC sends $20M, takes back $19.5M.
    r = evaluate_move(okc, c, [{"label": "p1", "salary": 20_000_000}],
                      [{"label": "incoming", "salary": 19_500_000}])
    passed.append(_check("OKC 1-for-1 dollar-for-dollar (legal)", r["legal"], True, r))

    # 9. ILLEGAL trade kicker pushes over the band: MIN sends $33.33M, takes back $40M base + 15% kicker = $46M.
    r = evaluate_move(min_base, c, [{"label": "Randle", "salary": 33_333_334}],
                      [{"label": "kicker guy", "salary": 40_000_000, "trade_kicker_pct": 0.15}])
    passed.append(_check("MIN $40M+15% kicker breaks the match", r["legal"], False, r))

    # 10. ILLEGAL conditional team option: send a declined team-option player.
    r = evaluate_move(min_base, c,
                      [{"label": "TO guy", "salary": 24_000_000, "team_option_year": "2026-27",
                        "team_option_exercised": False}],
                      [{"label": "incoming", "salary": 20_000_000}])
    passed.append(_check("send a declined team-option player (not under contract)", r["legal"], False, r))

    # 11. CHAIN: setup trade (legal) then repackage (legal).
    chain = evaluate_chain([
        {"label": "setup: shed Randle for expirings", "team_state": min_base, "const": c,
         "outgoing": [{"label": "Randle", "salary": 33_333_334}],
         "incoming": [{"label": "expirings", "salary": 30_000_000}]},
        {"label": "repackage for star", "team_state": load_team_state("MIN", "2026-27", "s2_gobert_out"),
         "const": c, "outgoing": [{"label": "Gobert", "salary": 36_500_000}],
         "incoming": [{"label": "star", "salary": 40_000_000}]},
    ])
    ok = "PASS" if chain["chain_legal"] else "FAIL"
    print(f"  [{ok}] two-stage chain legal={chain['chain_legal']} (broke_at={chain['broke_at']})")
    passed.append(chain["chain_legal"])

    print(f"\n{sum(passed)}/{len(passed)} checks passed")


if __name__ == "__main__":
    main()

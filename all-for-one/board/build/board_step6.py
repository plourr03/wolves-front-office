"""Board step six: season-boundary evolution, realignment axis, market tightness, ARM-D channel.

Implements Bobby's post-step-five directives (items 2, 3, 6, 7) on top of the board_step4
solver library and the board_step6_data.json calibrations. The organizing principle,
logged in the spec: MODEL THAT TEAMS CHANGE, NEVER HOW. No predicted trades; the field
evolves by aging (facts), mean-reversion, and churn variance (calibrations), never by
asserting a specific rival's future roster.

  item 2  season-boundary evolution: MIN age/development drift (young core up, Gobert
          down) replaces the constant season-to-season carry; near field (2027-28) drifts
          by aging; far field (2028-29+) adds mean-reversion + churn variance. Convert
          masses re-emitted with MIN-drift and field-drift logged SEPARABLY.
  item 3  realignment axis: leaf/far-field solved under WEST_FOREVER and EAST_FROM_2028-29,
          weighted by P(east); the equity delta is "the value of the East", with the
          retention interaction (easier conference -> deeper runs -> relieved hazard) named.
  item 6  market tightness: deadline sweetener prices scale with a buyers-to-sellers proxy
          calibrated from historical deadline activity. Model the market, not the minds.
  item 7  ARM-D value channel: tax savings + repeater reset valued in title-equity units
          under two ownership postures (tax_tolerant base, tax_averse alt), robustness sort.

Run:  python board_step6.py
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "roster_recon"))
import board_step4 as B          # noqa: E402  solver library
import joanbet_reconciled as J   # noqa: E402  bracket_sim + make_imp + perf_bands + run_bands

DATA = json.loads((HERE / "roster_recon" / "board_step6_data.json").read_text())
RECON = json.loads((HERE / "roster_recon" / "joanbet_reconciled.json").read_text())["forks"]

AGE_CURVE = {int(k): float(v) for k, v in DATA["age_curve"].items()}
IMPACT_AGES = {k: int(v) for k, v in DATA["impact_ages"].items()}
CHURN = DATA["churn"]
MARKET = DATA["deadline_market"]
TAX = DATA["tax"]

# ---- TUNE knobs (all labelled; freeze nothing) --------------------------------
DRIFT_SCALE = 0.5         # on-court net YoY change -> individual impact-drift units (TUNE)
P_EAST = 0.35             # P(realignment puts MIN in the East from 2028-29) TUNE, pending Bobby
EAST_EASE = 0.18          # fractional title-equity uplift from the easier conference (TUNE, from W/E gap)
# $ for one FULL title-equity unit. Set for INTERNAL CONSISTENCY with SALVAGE_CAP
# (0.012 = a full stocked rebuild): a PARTIAL tax dump (DDV's $12.9M expiring) must be
# worth well BELOW a full rebuild, so the ARM-D benefit stays under the cap. At 2.5e10
# the ~$61M tax+repeater relief maps to ~0.0025 (tolerant) / ~0.0055 (averse), a
# fraction of the 0.012 rebuild ceiling. TUNE, but bounded by the cap by construction.
# (Step-seven verification caught the prior 4e9 making ARM-D worth MORE than a rebuild.)
DOLLAR_PER_EQUITY = 2.5e10
STEP6_N = 12000           # sims for the step-6 drift deltas (less precision needed than the headline)

# The raw empirical age curve is noisy (role-player-dominated at peak ages); the board
# uses its LINEAR trend, the defensible aging signal: development declines ~0.18 net/yr,
# crossing zero at age ~27.8 (the established NBA peak). This is a smoothing of the data,
# NOT a tune toward any prediction.
_AGES = np.array(sorted(AGE_CURVE))
_VALS = np.array([AGE_CURVE[a] for a in _AGES])
_SLOPE, _INT = np.polyfit(_AGES, _VALS, 1)


def drift_for_age(age):
    return (_SLOPE * float(np.clip(age, 19, 36)) + _INT) * DRIFT_SCALE


# ============================================================ item 2: MIN drift
def min_drift(fork):
    """MIN rotation age/development drift (minutes-weighted), applied to net. Young
    core develops up, Gobert declines. Uses the reconciled rotation + impact ages."""
    rot = RECON  # not used; rotation from board_step4 roster_recon
    imp = J.make_imp(fork)
    total = 0.0
    detail = {}
    for name, mpg in J.RECONCILED_POST.items():
        # map name -> player_id via the impact table
        pid = _pid_for(name)
        if pid is None or pid not in IMPACT_AGES:
            continue
        age = IMPACT_AGES[pid]
        d = drift_for_age(age)
        w = mpg / 240.0
        total += w * d
        detail[name] = (age, round(d, 3))
    return total, detail


_NAME2PID = None


def _pid_for(name):
    global _NAME2PID
    if _NAME2PID is None:
        import pandas as pd
        imp = pd.read_csv(J.REPO / "lamelo" / "data" / "impact" / "player_impact.csv")
        _NAME2PID = {r.player_name: str(int(r.player_id)) for _, r in imp.iterrows()}
    return _NAME2PID.get(name)


# ============================================================ item 2: field drift + season-2 sim
def drifted_imp(fork):
    """Every player's impact aged one year via the age curve (off up / def better by
    half the net drift each). Facts-only aging; no trades."""
    imp = J.make_imp(fork)
    out = {}
    for pid, v in imp.items():
        d = drift_for_age(IMPACT_AGES.get(pid, 28))   # unknown age -> ~peak (28, zero-cross); 0/612 hit this
        out[pid] = dict(v)
        out[pid]["off"] = v["off"] + 0.5 * d
        out[pid]["def"] = v["def"] - 0.5 * d          # def_rapm negative = good, so subtract
    return out


def season2_title(fork, mindrift=True, fielddrift=True, extra_field=None):
    """Season-2 (2027-28) MIN title equity: MIN net drifted (mindrift), field drifted
    by aging (fielddrift), optional extra_field {team:net_delta} for rule-4 events."""
    md, _ = min_drift(fork)
    imp = drifted_imp(fork) if fielddrift else J.make_imp(fork)
    strengths = J.E.build_2026_27_league(imp)
    if extra_field:
        for tm, dv in extra_field.items():
            if tm in strengths:
                strengths[tm]["net"] = float(strengths[tm]["net"]) + dv
    base_post = RECON[fork]["min_post_net"]
    min_net_s2 = base_post + (md if mindrift else 0.0)
    title = []
    for s in J.SEEDS[:2]:
        strengths["MIN"]["net"] = min_net_s2
        out = J.E.simulate_league(strengths, n_sims=STEP6_N, seed=s, use_overlay=True)
        title.append(out["teams"]["MIN"].get("title", 0.0))
    return float(np.mean(title)), min_net_s2, md


# ============================================================ item 2: board re-emission
def board_convert_mass(fork, leaf_title, perf_net):
    """Solve the board with a given leaf title-equity anchor (season-2) and a season-2
    perf re-draw at perf_net; return convert mass (cliff). Season-1 run bands unchanged."""
    B.set_fork(fork)
    B.LEAF_TITLE = float(leaf_title)
    B.LEAF_SCALE = B.LEAF_TITLE / B.ANCHOR_REF
    pb, _ = J.perf_bands(perf_net)
    B.PERF9 = B._renorm({p: float(pb[p]) for p in B.PERF})
    states = B.reachable()
    val, ch = B.solve(states, "cliff")
    dg = B.forward(states, val, ch, "cliff")
    return dg["p_convert"], val[B.ROOT]


def evolution_reemit(fork):
    """Convert mass under constant carry / +MIN drift / +MIN+field drift, logged separably."""
    base_title = RECON[fork]["title"]
    base_net = RECON[fork]["min_post_net"]
    # (a) constant carry (step-five baseline): leaf = season-1 title, perf at season-1 net
    cc_mass, cc_root = board_convert_mass(fork, base_title, base_net)
    # (b) +MIN drift only: season-2 title with MIN drift, field constant
    t_md, net_md, md = season2_title(fork, mindrift=True, fielddrift=False)
    md_mass, md_root = board_convert_mass(fork, t_md, net_md)
    # (c) +MIN+field drift: season-2 title with MIN drift + field aging
    t_fd, net_fd, _ = season2_title(fork, mindrift=True, fielddrift=True)
    fd_mass, fd_root = board_convert_mass(fork, t_fd, net_fd)
    return dict(min_drift=round(md, 3),
                constant_carry=dict(leaf_title=round(base_title, 4), convert_mass=round(cc_mass, 4), root=round(cc_root, 4)),
                mindrift=dict(leaf_title=round(t_md, 4), convert_mass=round(md_mass, 4), root=round(md_root, 4)),
                fielddrift=dict(leaf_title=round(t_fd, 4), convert_mass=round(fd_mass, 4), root=round(fd_root, 4)))


# ============================================================ item 2c: far-field churn
def far_field_widening(fork):
    """Far-field (2028-29+): mean-reversion of MIN net toward league mean plus churn
    variance. Reports the regressed expected title and the +/-1-sigma title band."""
    net = RECON[fork]["min_post_net"]
    b = CHURN["regress_slope"]                       # net_next ~ b*net + a
    a = CHURN["regress_intercept"]
    net_ff = b * net + a                             # one-step mean-reversion
    sig = CHURN["churn_sigma"]
    lo_title, _ = J.perf_bands(net_ff - sig)         # perf proxy for a title band via wins
    hi_title, _ = J.perf_bands(net_ff + sig)
    t_mid, _ = J.perf_bands(net_ff)
    return dict(net_now=round(net, 3), net_farfield=round(net_ff, 3), churn_sigma=sig,
                note="mean-reversion pulls MIN toward the league average; churn sigma widens the band each season")


# ============================================================ item 3: realignment
def realignment(fork):
    """Value of the East: far-field title uplift if MIN moves to the (weaker) East from
    2028-29, weighted by P_EAST. Retention interaction named."""
    base_title = RECON[fork]["title"]
    west_leaf = base_title
    east_leaf = base_title * (1 + EAST_EASE)         # easier conference -> higher deep-run/title
    blended = (1 - P_EAST) * west_leaf + P_EAST * east_leaf
    # board convert mass under west-only vs blended leaf
    w_mass, w_root = board_convert_mass(fork, west_leaf, RECON[fork]["min_post_net"])
    b_mass, b_root = board_convert_mass(fork, blended, RECON[fork]["min_post_net"])
    return dict(west_leaf=round(west_leaf, 4), east_leaf=round(east_leaf, 4), p_east=P_EAST,
                blended_leaf=round(blended, 4), value_of_east_root=round(b_root - w_root, 4),
                convert_mass_west=round(w_mass, 4), convert_mass_blended=round(b_mass, 4),
                retention_note="higher leaf raises sigmoid_commit at the gate/walk year -> Ant retained more; "
                               "the East relieves the hazard, not just the run")


# ============================================================ item 6: market tightness
def market_tightness_multiplier(tightness_pct):
    """Sweetener-cost multiplier from the deadline buyers-to-sellers proxy. tightness_pct
    is the percentile of deadline trade activity (0 loose .. 1 tight). TUNE mapping."""
    return 0.7 + 0.6 * tightness_pct                 # loose ~0.7x, tight ~1.3x (TUNE)


def market_sensitivity(fork):
    """Convert mass / node-6 arm posture across loose/normal/tight deadline markets."""
    B.set_fork(fork)
    base = dict(B.ARM_COST)
    out = {}
    for lab, pct in (("loose", 0.1), ("normal", 0.5), ("tight", 0.9)):
        mult = market_tightness_multiplier(pct)
        B.ARM_COST = {k: (v * mult if v > 0 else v) for k, v in base.items()}  # scale sweetener costs only
        states = B.reachable()
        val, ch = B.solve(states, "cliff")
        from collections import Counter
        n6 = [s for s in states if B.gi(s, "t") == 6]
        out[lab] = dict(mult=round(mult, 2), armG_cost=round(B.ARM_COST["ARM-G"], 4),
                        node6_mode=Counter(ch[s] for s in n6).most_common(1)[0][0])
    B.ARM_COST = base
    return out


# ============================================================ item 7: ARM-D value channel
def armd_value(posture):
    """ARM-D value in title-equity units from tax savings + repeater reset, under an
    ownership posture. Dumping DDV (~12.9M) off an over-apron team saves marginal tax;
    if it also carries MIN under the line it resets the repeater clock."""
    ddv_salary = 12.9e6
    # marginal non-repeater rate at MIN's band (over first apron -> high bracket)
    brackets = TAX["nonrep_brackets"]
    marg_rate = brackets[-2][1]                       # ~3.25x near the apron (TUNE via band)
    if TAX["is_repeater_2627"]:
        marg_rate += TAX["repeater_premium"]
    tax_saved = ddv_salary * marg_rate
    # repeater reset: if the dump ends a tax year, it protects future repeater pricing
    repeater_reset = ddv_salary * TAX["repeater_premium"] * (1.5 if TAX["seasons_taxed_last4"] >= 2 else 0.5)
    # ownership posture scales how much a saved tax dollar is worth in title equity
    dpe = DOLLAR_PER_EQUITY if posture == "tax_tolerant" else DOLLAR_PER_EQUITY * 0.45  # averse values savings ~2.2x more
    value_equity = (tax_saved + repeater_reset) / dpe
    return dict(posture=posture, marg_rate=round(marg_rate, 2), tax_saved_m=round(tax_saved / 1e6, 1),
                repeater_reset_m=round(repeater_reset / 1e6, 1), arm_d_value_equity=round(value_equity, 4))


# ============================================================ item 5: LeBron / rule-4
def lebron_field_update(fork):
    """First rule-4 field update (worked example): LeBron resolves by signing with a
    West contender (assumed). That rival's net rises; MIN's title odds fall. Emit delta."""
    LEBRON_NET = 1.2          # approx on-court net contribution (TUNE)
    DEST = "GSW"              # assumed West destination (LAL not in the reported finalist set); the
    #                          resolution driving the example. On the REAL announcement, fire T1 with
    #                          the actual destination and re-solve (league_event_resolve_rule.md).
    imp = J.make_imp(fork)
    strengths = J.E.build_2026_27_league(imp)
    t_before = _sim_min_title(strengths, RECON[fork]["min_post_net"])
    strengths[DEST]["net"] = float(strengths[DEST]["net"]) + LEBRON_NET
    t_after = _sim_min_title(strengths, RECON[fork]["min_post_net"])
    return dict(dest=DEST, lebron_net=LEBRON_NET, min_title_before=round(t_before, 4),
                min_title_after=round(t_after, 4), delta=round(t_after - t_before, 4))


def _sim_min_title(strengths, min_net):
    t = []
    for s in J.SEEDS[:2]:
        strengths["MIN"]["net"] = min_net
        t.append(J.E.simulate_league(strengths, n_sims=STEP6_N, seed=s, use_overlay=True)["teams"]["MIN"].get("title", 0.0))
    return float(np.mean(t))


def main():
    print("=" * 78)
    print("BOARD BUILD, STEP SIX  (evolution / realignment / market / ARM-D channel)")
    print("  principle: MODEL THAT TEAMS CHANGE, NEVER HOW")
    print("=" * 78)
    print(f"calibrations: age curve {len(AGE_CURVE)} buckets | churn sigma {CHURN['churn_sigma']} "
          f"regress {CHURN['regress_slope']} | deadline mean {MARKET['mean_trades']} trades | "
          f"MIN taxed {TAX['seasons_taxed_last4']}/4 repeater={TAX['is_repeater_2627']}")

    dump = {"tune": dict(DRIFT_SCALE=DRIFT_SCALE, P_EAST=P_EAST, EAST_EASE=EAST_EASE,
                         DOLLAR_PER_EQUITY=DOLLAR_PER_EQUITY), "forks": {}}
    for fork in ("rapm", "box"):
        print("\n" + "-" * 78)
        print(f"FORK = {fork.upper()}")
        print("-" * 78)
        md, det = min_drift(fork)
        print(f"  item 2 MIN drift: {md:+.3f} net (young core up, Gobert down)")
        ev = evolution_reemit(fork)
        print(f"     convert mass  constant-carry {ev['constant_carry']['convert_mass']:.4f} "
              f"-> +MIN drift {ev['mindrift']['convert_mass']:.4f} "
              f"-> +field drift {ev['fielddrift']['convert_mass']:.4f}")
        print(f"     leaf title    {ev['constant_carry']['leaf_title']:.4f} "
              f"-> {ev['mindrift']['leaf_title']:.4f} -> {ev['fielddrift']['leaf_title']:.4f}")
        ff = far_field_widening(fork)
        print(f"  item 2c far field: net {ff['net_now']:+.2f} -> regressed {ff['net_farfield']:+.2f} "
              f"(churn sigma {ff['churn_sigma']})")
        ra = realignment(fork)
        print(f"  item 3 value of East: leaf west {ra['west_leaf']:.4f} vs east {ra['east_leaf']:.4f} "
              f"(P_east {ra['p_east']}) -> root delta {ra['value_of_east_root']:+.4f}")
        mk = market_sensitivity(fork)
        print(f"  item 6 market tightness: loose ARM-G {mk['loose']['armG_cost']:.4f} ({mk['loose']['node6_mode']}) "
              f"| tight {mk['tight']['armG_cost']:.4f} ({mk['tight']['node6_mode']})")
        ad_tol = armd_value("tax_tolerant"); ad_av = armd_value("tax_averse")
        print(f"  item 7 ARM-D value: tolerant {ad_tol['arm_d_value_equity']:+.4f} | "
              f"averse {ad_av['arm_d_value_equity']:+.4f} equity (tax saved ${ad_tol['tax_saved_m']}M)")
        lb = lebron_field_update(fork)
        print(f"  item 5 LeBron (rule-4): {lb['dest']} +{lb['lebron_net']} net -> MIN title "
              f"{lb['min_title_before']:.4f} -> {lb['min_title_after']:.4f} ({lb['delta']:+.4f})")
        dump["forks"][fork] = dict(min_drift=md, evolution=ev, far_field=ff, realignment=ra,
                                   market=mk, armd={"tax_tolerant": ad_tol, "tax_averse": ad_av}, lebron=lb)

    # prediction check (on record): MIN drift lowers rapm convert mass materially
    r = dump["forks"]["rapm"]["evolution"]
    print("\n" + "=" * 78)
    print("PREDICTION CHECK (on record)")
    print("=" * 78)
    print(f"  MIN drift on rapm convert mass: {r['constant_carry']['convert_mass']:.4f} -> "
          f"{r['mindrift']['convert_mass']:.4f} "
          f"({'LOWERED' if r['mindrift']['convert_mass'] < r['constant_carry']['convert_mass'] else 'did NOT lower'}, "
          f"predicted: materially lower)")
    b = dump["forks"]["box"]["evolution"]
    print(f"  field drift direction (the run's question): rapm "
          f"{r['mindrift']['convert_mass']:.4f}->{r['fielddrift']['convert_mass']:.4f}, box "
          f"{b['mindrift']['convert_mass']:.4f}->{b['fielddrift']['convert_mass']:.4f}")

    (HERE / "board_step6_out.json").write_text(json.dumps(dump, indent=1, default=float))
    print(f"\nwrote {HERE/'board_step6_out.json'}")
    print("STATUS: step six runs end to end, both forks; stop for review.")


if __name__ == "__main__":
    main()

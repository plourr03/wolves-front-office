"""Per-game reconciliation error localizer (F1 tail census instrument).

Given a game_id, reconstruct the stint floor and localize where the
per-player minutes error lives, so a residual can be classified:

  per-player      reconstructed seconds vs official seconds-precise
                  minutes_float; who fails the 0.5-min bar, starter or bench.
  per-period      team on-floor seconds per period vs 5 * period_length --
                  a period that does not sum flags a floor-COUNT error
                  localized to that period (the sharp structural signal;
                  minutes_float is a game total so per-period official
                  minutes do not exist, but the team-seconds identity is
                  exact per period by construction when the floor is right).
  starters        derived period-1 floor vs the official starters
                  (nba_player_advanced_stats.position five).
  sub discriminator   |error| vs sub count and a flat-vs-scaling read.

Emits a human summary and, with --json, a compact machine record for the
tail-census workflow. Read-only; never writes cache.

Usage: python -m src.stints.diagnose <game_id> [--json]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

FITENGINE_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(FITENGINE_ROOT))
from src.adapters.postmortem_lib import query  # noqa: E402
from src.stints import floor_state, stint_builder  # noqa: E402
from src.stints.reconcile import (  # noqa: E402
    REG_SECONDS, OT_SECONDS, official_minutes, player_seconds_from_stints)


def _lineup_pids(lineup_id: str) -> list[int]:
    import re
    return [int(p) for p in re.split(r"[,\-]", str(lineup_id)) if p]


def _period_len(per: int) -> float:
    return 720.0 if per <= 4 else 300.0


def _period_contributions(row) -> list[tuple[int, float]]:
    """Split one stint's WALL-CLOCK seconds across the periods it spans.
    Clock counts down from the period length; a stint from (p0, c0) to
    (p1, c1) spends c0 in p0, the full length of each intermediate period,
    and (len(p1) - c1) in p1. Non-spanning stints return one entry."""
    p0, p1 = int(row.period_start), int(row.period_end)
    c0, c1 = float(row.clock_start_sec), float(row.clock_end_sec)
    if p0 == p1:
        return [(p0, c0 - c1)]
    out = [(p0, c0)]
    for p in range(p0 + 1, p1):
        out.append((p, _period_len(p)))
    out.append((p1, _period_len(p1) - c1))
    return out


def diagnose(game_id: str) -> dict:
    try:
        res = floor_state.process_game(game_id)
    except Exception as e:
        return {"game_id": game_id, "quarantined": True,
                "error": f"{type(e).__name__}: {e}"}
    stints = stint_builder.derive_stints(res["annotated"], res["possessions"])
    ps = player_seconds_from_stints(stints)
    off = official_minutes(game_id)
    n_periods = int(res["pbp"].period.max())
    exp_team = 5 * (REG_SECONDS + OT_SECONDS * max(0, n_periods - 4))

    m = off.merge(ps, on=["player_id", "team_id"], how="outer")
    m["secs"] = m.secs.fillna(0.0)
    m["official_true"] = m.minutes_float.astype(float).fillna(
        m.minutes_played.fillna(0.0).astype(float) + 0.5)
    m["recon_min"] = m.secs / 60.0
    m["delta"] = (m.recon_min - m.official_true).abs()
    names = query("""SELECT DISTINCT ON (player_id) player_id, player_name
                     FROM nba_player_stats WHERE game_id = %s
                     ORDER BY player_id, game_date DESC""", (game_id,))
    nm = dict(zip(names.player_id, names.player_name))

    # per-period team PLAYER-seconds (each stint carries 5 players, so a
    # team's player-seconds in a period = sum over its stints of
    # duration_sec * lineup_size). One regulation period is 720s of wall
    # clock, one OT 300s; 5 on the floor -> 5*720 / 5*300 player-seconds.
    # A period whose player-seconds are ~0 is a PHANTOM period (a stray
    # period marker with no real playing time -- a PBP data quirk, seen on
    # 0021500916); flagged separately from a floor-COUNT error.
    # accumulate player-seconds per (period, team), splitting cross-period
    # stints at the boundary (each stint carries lineup_size players)
    acc: dict[tuple[int, int], float] = {}
    for row in stints.itertuples():
        size = len(_lineup_pids(row.lineup_id))
        for per, secs in _period_contributions(row):
            acc[(per, int(row.team_id))] = (
                acc.get((per, int(row.team_id)), 0.0) + secs * size)
    per_period = {}
    phantom_periods = []
    for per in sorted({p for p, _ in acc}):
        exp = _period_len(per)
        rec = {}
        for (pp, t), v in acc.items():
            if pp != per:
                continue
            exact = bool(abs(v - 5 * exp) < 1.0)
            phantom = bool(v < 1.0)
            rec[int(t)] = {"player_secs": round(float(v), 1),
                           "expected": 5 * exp,
                           "exact": exact or phantom, "phantom": phantom}
            if phantom:
                phantom_periods.append((int(per), int(t)))
        per_period[int(per)] = rec

    # reference-completeness: does official minutes SUM to a full game per
    # team? A whole-team shortfall (recon uniformly exceeds official, team
    # seconds still exact) means the reference is incomplete -- a warehouse
    # ingest gap (seen on in-progress 2025-26 games), NOT a reconstruction
    # error. exp_team is in seconds; official minutes are in minutes.
    exp_team_min = exp_team / 60.0
    off_sum = m.groupby("team_id").official_true.sum()
    recon_sum = m.groupby("team_id").recon_min.sum()
    ref_complete = {int(t): {
        "official_total_min": round(float(off_sum.get(t, 0.0)), 1),
        "recon_total_min": round(float(recon_sum.get(t, 0.0)), 1),
        "expected_min": round(exp_team_min, 1),
        "official_shortfall_min": round(exp_team_min - float(off_sum.get(t, 0.0)), 1),
    } for t in off_sum.index}
    ref_incomplete = any(
        v["official_shortfall_min"] > 3.0 for v in ref_complete.values())

    starters = res["starters"]
    off_start = query("""SELECT team_id, person_id FROM nba_player_advanced_stats
                         WHERE game_id = %s AND position IS NOT NULL
                           AND position <> ''""", (game_id,))
    official_starters = {int(t): set(int(p) for p in g.person_id)
                         for t, g in off_start.groupby("team_id")}
    starter_mismatch = {}
    for tid, derived in starters.items():
        offs = official_starters.get(int(tid), set())
        if offs and set(derived) != offs:
            starter_mismatch[int(tid)] = {
                "derived_not_official": sorted(set(derived) - offs),
                "official_not_derived": sorted(offs - set(derived))}

    n_subs = int((res["annotated"].action_type == "substitution").sum()) // 2
    failing = m[m.delta > 0.5].copy()
    failing["name"] = failing.player_id.map(nm)
    fail_recs = [
        {"player_id": int(r.player_id), "name": r["name"],
         "team_id": int(r.team_id) if pd.notna(r.team_id) else None,
         "recon_min": round(float(r.recon_min), 2),
         "official_min": round(float(r.official_true), 2),
         "delta_min": round(float(r.delta), 2),
         "is_official_starter": bool(int(r.player_id) in
                                     official_starters.get(int(r.team_id), set())
                                     if pd.notna(r.team_id) else False)}
        for _, r in failing.sort_values("delta", ascending=False).iterrows()]

    team_exact = all(pp[t]["exact"] for pp in per_period.values() for t in pp)
    bad_periods = [(p, t) for p, pp in per_period.items()
                   for t in pp if not pp[t]["exact"] and not pp[t]["phantom"]]
    # error direction: uniformly-over (reference incomplete) vs mixed
    # (attribution error, sum roughly conserved)
    signed = (m.recon_min - m.official_true)
    n_over = int((signed > 0.5).sum())
    n_under = int((signed < -0.5).sum())
    direction = ("uniform_over" if n_under == 0 and n_over > 2
                 else "uniform_under" if n_over == 0 and n_under > 2
                 else "mixed")
    return {
        "game_id": game_id, "quarantined": False, "n_periods": n_periods,
        "n_subs": n_subs, "n_player_games": int(len(m)),
        "n_failing": int(len(failing)),
        "worst_delta": round(float(m.delta.max()), 2),
        "team_seconds_all_exact": team_exact,
        "bad_periods": [{"period": p, "team_id": t} for p, t in bad_periods],
        "phantom_periods": [{"period": p, "team_id": t}
                            for p, t in phantom_periods],
        "starter_mismatch": starter_mismatch,
        "reference_incomplete": ref_incomplete,
        "reference_by_team": ref_complete,
        "error_direction": direction, "n_over": n_over, "n_under": n_under,
        "failing_players": fail_recs,
        "expected_team_secs_per_side": exp_team,
    }


def trace(game_id: str, top: int = 4) -> dict:
    """For the worst-failing players (the swap pair and neighbours), dump
    their reconstructed on-floor stint intervals next to their PBP
    substitution events, so a membership swap is directly visible: a player
    credited to a stint the PBP says they were subbed out of, or vice
    versa. Read-only diagnostic for the tail-census workflow."""
    res = floor_state.process_game(game_id)
    stints = stint_builder.derive_stints(res["annotated"], res["possessions"])
    d = diagnose(game_id)
    fails = d["failing_players"][:top]
    names = query("""SELECT DISTINCT ON (player_id) player_id, player_name
                     FROM nba_player_stats WHERE game_id = %s
                     ORDER BY player_id, game_date DESC""", (game_id,))
    nm = dict(zip(names.player_id, names.player_name))
    subs = query("""
        SELECT period, clock, description, person_id
        FROM nba_play_by_play
        WHERE game_id = %s AND action_type IN ('Substitution','substitution')
        ORDER BY period, action_number""", (game_id,))
    out = {"game_id": game_id, "players": []}
    for f in fails:
        pid = f["player_id"]
        pid_stints = [
            {"period": int(s.period_start),
             "clock_start": float(s.clock_start_sec),
             "clock_end": float(s.clock_end_sec),
             "mins": round(float(s.duration_sec) / 60.0, 2)}
            for s in stints.itertuples()
            if pid in _lineup_pids(s.lineup_id)]
        pid_subs = [
            {"period": int(r.period), "clock": r.clock, "desc": r.description}
            for r in subs.itertuples()
            if (r.person_id == pid) or (nm.get(pid, "") and
                nm[pid].split()[-1].lower() in str(r.description).lower())]
        out["players"].append({
            "player_id": pid, "name": f["name"],
            "recon_min": f["recon_min"], "official_min": f["official_min"],
            "delta": f["delta_min"], "is_starter": f["is_official_starter"],
            "n_stint_intervals": len(pid_stints),
            "stint_intervals": pid_stints,
            "pbp_sub_events": pid_subs})
    return out


def _print_human(d: dict) -> None:
    if d.get("quarantined"):
        print(f"{d['game_id']}: QUARANTINED -- {d['error']}")
        return
    print(f"{d['game_id']}: {d['n_periods']} periods, {d['n_subs']} subs, "
          f"{d['n_failing']}/{d['n_player_games']} player-games fail, "
          f"worst {d['worst_delta']} min")
    print(f"  team-seconds all periods exact: {d['team_seconds_all_exact']}"
          f" | error direction: {d['error_direction']} "
          f"({d['n_over']} over, {d['n_under']} under)")
    if d["reference_incomplete"]:
        print(f"  REFERENCE INCOMPLETE (official minutes undercount, not our "
              f"error): {d['reference_by_team']}")
    if d["bad_periods"]:
        print(f"  BAD PERIODS (floor-count error): {d['bad_periods']}")
    if d.get("phantom_periods"):
        print(f"  PHANTOM PERIODS (stray marker, no real time): "
              f"{d['phantom_periods']}")
    if d["starter_mismatch"]:
        print(f"  STARTER MISMATCH vs official: {d['starter_mismatch']}")
    for f in d["failing_players"]:
        tag = "STARTER" if f["is_official_starter"] else "bench"
        print(f"    {f['name']:24} {tag:7} recon {f['recon_min']:6.2f} "
              f"off {f['official_min']:6.2f} delta {f['delta_min']:6.2f}")


def main() -> None:
    game_id = sys.argv[1]
    flags = sys.argv[2:]
    if "--trace" in flags:
        print(json.dumps(trace(game_id), default=str, indent=1))
        return
    d = diagnose(game_id)
    if "--json" in flags:
        print(json.dumps(d))
    else:
        _print_human(d)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""D88: recompute every reported figure that rode on the stint points defect.

`lib/lineup_aggregation.py` credited a possession's points to the stint containing the
possession's timestamp, which put and-1 free throws and possessions spanning a
substitution on the wrong side. Measured against the box score: 4.25 points per team-game
on average, up to 11, 3.89% of all points, and the error is exactly mirrored between the
two teams of a game (`validate_stint_points.py`).

The cached stints carry per-stint made-shot columns, so nothing has to be re-derived from
play-by-play: points are rebuilt in place and Q2's own functions are re-run on both bases.
BEFORE is the cache as it stands, AFTER is points = 2*fgm + fg3m + ftm.

Uncertainty: the AFTER figure is bootstrapped over stints with Q2's own settings (1000
resamples, seed 42, 95%). A figure is FLAGGED when the shift is larger than the
half-width of that interval, or when it changes sign, because that is the case where a
sentence in a findings document or an article draft may no longer hold.

    python postmortem/scripts/recompute_stint_figures.py [--quick]
"""
from __future__ import annotations

import argparse
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, ROOT)

from analyses.q2_localize import analysis, batch, config, confound_checks  # noqa: E402

OUT = os.path.join(ROOT, "outputs", "tables", "validation", "d88_recomputed_figures.csv")
CACHES = {2023: config.CACHE_DIR / "wolves_2023_stints",
          2024: config.CACHE_DIR / "wolves_2024_stints",
          2025: config.CACHE_DIR / "wolves_2025_stints"}
W = config.WOLVES_TEAM_ID
ROWS: list[dict] = []


def rebuild(stints: pd.DataFrame) -> pd.DataFrame:
    """Points from made shots. The columns are per-stint event counts, already
    attributed to the stint that contains each shot."""
    s = stints.copy()
    s["points_for"] = 2 * s.fgm_off + s.fg3m_off + s.ftm_off
    s["points_against"] = 2 * s.fgm_def + s.fg3m_def + s.ftm_def
    return s


def record(figure: str, doc: str, reported, before: float, after: float,
           ci: tuple[float, float] | None, extra: str = "") -> None:
    half = (ci[1] - ci[0]) / 2 if ci and not any(np.isnan(c) for c in ci) else np.nan
    shift = after - before
    flag = ""
    if not np.isnan(half) and abs(shift) > half:
        flag = "MOVED BEYOND ITS INTERVAL"
    if not np.isnan(before) and not np.isnan(after) and np.sign(before) != np.sign(after):
        flag = ("SIGN CHANGED" if not flag else "SIGN CHANGED, " + flag)
    ROWS.append(dict(figure=figure, document=doc, reported=reported, before=round(before, 2),
                     after=round(after, 2), shift=round(shift, 2),
                     ci_lo=None if ci is None else round(ci[0], 2),
                     ci_hi=None if ci is None else round(ci[1], 2),
                     ci_half_width=None if np.isnan(half) else round(half, 2),
                     flag=flag, note=extra))
    print("  %-52s before %+8.2f  after %+8.2f  shift %+7.2f  %s"
          % (figure[:52], before, after, shift, flag or ""))


def both(sub_before: pd.DataFrame, metric):
    """(before, after, ci_on_after) for one stint subset and one metric."""
    sub_after = rebuild(sub_before)
    b = metric(sub_before) if len(sub_before) else np.nan
    boot = analysis.bootstrap_lineup_metric(sub_after, metric)
    return b, boot["point"], (boot["ci_lo"], boot["ci_hi"])


def wolves(stints: pd.DataFrame, gt: bool = True) -> pd.DataFrame:
    s = stints[stints.team_id == W]
    return s[~s.in_garbage_time] if gt else s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true", help="skip the per-lineup leaderboard")
    args = ap.parse_args()

    cache = {y: batch.load_cached_stints(p) for y, p in CACHES.items()}
    splits = {y: analysis.split_stints_by_season_type(df, y) for y, df in cache.items()}
    for y, sp in splits.items():
        print("%s: %s" % (config.season_label(y), {k: len(v) for k, v in sp.items()}))

    po25 = splits[2025].get("Playoffs", pd.DataFrame())
    rs25 = splits[2025].get("Regular Season", pd.DataFrame())
    rs24 = splits[2024].get("Regular Season", pd.DataFrame())
    po24 = splits[2024].get("Playoffs", pd.DataFrame())

    # ---- 1. team lineup-grain net rating, four season/type combos --------------
    print("\n1. TEAM NET RATING, LINEUP GRAIN (03_yoy_lineup_comparison.md lines 27-30)")
    # the source table orders its rows RS, RS, PO, PO
    for label, sub, rep in (("2024-25 RS", rs24, "+4.17"), ("2025-26 RS", rs25, "+3.00"),
                            ("2024-25 PO", po24, "-3.68"), ("2025-26 PO", po25, "-0.92")):
        if sub.empty:
            continue
        b, a, ci = both(wolves(sub), analysis.m_net_rating)
        record("team net rating, %s" % label, "03_yoy_lineup_comparison.md", rep, b, a, ci)

    # ---- 2. the two headline playoff lineups -----------------------------------
    print("\n2. THE TWO HEADLINE 2025-26 PLAYOFF LINEUPS (01_q2_findings.md lines 13-17)")
    w_po = wolves(po25)
    five = {"Dosunmu five (Edwards, McDaniels, Dosunmu, Randle, Gobert)":
            [config.ANT_ID, config.MCDANIELS_ID, config.DOSUNMU_ID, config.RANDLE_ID, config.GOBERT_ID],
            "DiVincenzo five (Edwards, McDaniels, DiVincenzo, Randle, Gobert)":
            [config.ANT_ID, config.MCDANIELS_ID, config.DIVINCENZO_ID, config.RANDLE_ID, config.GOBERT_ID]}
    for label, ids in five.items():
        lid = ",".join(str(i) for i in sorted(ids))
        sub = w_po[w_po.lineup_id == lid]
        if sub.empty:
            print("  %s: not found in the cache" % label)
            continue
        b, a, ci = both(sub, analysis.m_net_rating)
        record("net rating, %s" % label, "01_q2_findings.md",
               "-27.2" if "Dosunmu" in label else "+3.0", b, a, ci,
               "%.1f minutes" % (sub.duration_sec.sum() / 60))

    # ---- 3. individual on/off, 2025-26 playoffs --------------------------------
    print("\n3. INDIVIDUAL ON/OFF, 2025-26 PLAYOFFS (01_q2_findings.md lines 221-230)")
    reported_onoff = {config.DIVINCENZO_ID: "+18.4", config.CONLEY_ID: "+15.8",
                      config.NAZ_ID: "+8.6", config.CLARK_ID: "+4.7", config.GOBERT_ID: "+1.6",
                      config.HYLAND_ID: "-1.9", config.MCDANIELS_ID: "-8.8",
                      config.DOSUNMU_ID: "-9.7", config.ANT_ID: "-12.1", config.RANDLE_ID: "-16.3"}
    names = analysis.load_player_names(list(reported_onoff))
    for pid, rep in reported_onoff.items():
        on = w_po[w_po.lineup_id.apply(lambda lid: analysis.player_in_lineup(lid, pid))]
        off = w_po[w_po.lineup_id.apply(lambda lid: not analysis.player_in_lineup(lid, pid))]
        if on.empty or off.empty:
            continue
        diff = lambda s: analysis.m_net_rating(s)  # noqa: E731
        b_on, a_on, _ = both(on, diff)
        b_off, a_off, _ = both(off, diff)
        # bootstrap the difference itself, resampling both sides
        rng = np.random.default_rng(config.BOOTSTRAP_SEED)
        on_a, off_a = rebuild(on), rebuild(off)
        samples = []
        for _ in range(config.BOOTSTRAP_N):
            s1 = on_a.iloc[rng.integers(0, len(on_a), len(on_a))]
            s2 = off_a.iloc[rng.integers(0, len(off_a), len(off_a))]
            v = analysis.m_net_rating(s1) - analysis.m_net_rating(s2)
            if not np.isnan(v):
                samples.append(v)
        ci = tuple(np.quantile(samples, [0.025, 0.975])) if len(samples) > 5 else (np.nan, np.nan)
        record("on/off, %s, 2025-26 PO" % names.get(pid, pid), "01_q2_findings.md", rep,
               b_on - b_off, a_on - a_off, ci)

    # ---- 4. the pairing cohorts, 2025-26 playoffs ------------------------------
    print("\n4. PAIRING COHORTS, 2025-26 PLAYOFFS (02_q2_corrections... lines 22-29)")
    for label, fn, rep in (("Gobert + Reid, no Randle", confound_checks.filter_gobert_naz_no_randle, "+9.82"),
                           ("Gobert + Randle, no Reid", confound_checks.filter_gobert_randle_no_naz, "-12.22"),
                           ("triple big", confound_checks.filter_triple_big, "+10.88")):
        sub = fn(w_po)
        if sub.empty:
            continue
        b, a, ci = both(sub, analysis.m_net_rating)
        record("net rating, %s, 2025-26 PO" % label, "02_q2_corrections_and_edwards_context.md",
               rep, b, a, ci, "%.1f minutes" % (sub.duration_sec.sum() / 60))

    # ---- 5. the year-over-year pairings and DiVincenzo -------------------------
    print("\n5. YEAR OVER YEAR (03_yoy_lineup_comparison.md lines 11-19, 72-90, 113-120)")
    yoy = (("Gobert + Randle, 2024-25 RS", rs24, confound_checks.filter_gobert_randle_no_naz, "+5.71"),
           ("Gobert + Randle, 2025-26 RS", rs25, confound_checks.filter_gobert_randle_no_naz, "+4.57"),
           ("Gobert + Reid, 2024-25 RS", rs24, confound_checks.filter_gobert_naz_no_randle, "+10.76"),
           ("Gobert + Reid, 2025-26 RS", rs25, confound_checks.filter_gobert_naz_no_randle, "+5.78"))
    for label, sub, fn, rep in yoy:
        if sub.empty:
            continue
        c = fn(wolves(sub))
        if c.empty:
            continue
        b, a, ci = both(c, analysis.m_net_rating)
        record("net rating, %s" % label, "03_yoy_lineup_comparison.md", rep, b, a, ci,
               "%.0f minutes" % (c.duration_sec.sum() / 60))
    for label, sub, rep_on, rep_off in (("2025-26 RS", rs25, "+7.57", "-4.57"),
                                        ("2024-25 RS", rs24, "+4.08", "+4.22")):
        if sub.empty:
            continue
        s = wolves(sub)
        on = s[s.lineup_id.apply(lambda lid: analysis.player_in_lineup(lid, config.DIVINCENZO_ID))]
        off = s[s.lineup_id.apply(lambda lid: not analysis.player_in_lineup(lid, config.DIVINCENZO_ID))]
        for nm, part, rep in (("on", on, rep_on), ("off", off, rep_off)):
            if part.empty:
                continue
            b, a, ci = both(part, analysis.m_net_rating)
            record("DiVincenzo %s, net rating, %s" % (nm, label), "03_yoy_lineup_comparison.md",
                   rep, b, a, ci)

    # ---- 6. Q8's Edwards x Randle 2x2 -----------------------------------------
    print("\n6. EDWARDS x RANDLE 2x2 (01_q8_v1_findings.md lines 197-224)")
    for label, sub in (("2025-26 PO", po25), ("2025-26 RS", rs25), ("2024-25 RS", rs24)):
        if sub.empty:
            continue
        s = wolves(sub)
        for ant in (True, False):
            for ran in (True, False):
                cell = s[s.lineup_id.apply(
                    lambda lid: (analysis.player_in_lineup(lid, config.ANT_ID) == ant)
                    and (analysis.player_in_lineup(lid, config.RANDLE_ID) == ran))]
                if cell.empty or cell.possessions_off.sum() < 50:
                    continue
                b, a, ci = both(cell, analysis.m_net_rating)
                record("Edwards %s, Randle %s, %s" % ("on" if ant else "off",
                                                      "on" if ran else "off", label),
                       "01_q8_v1_findings.md", "", b, a, ci)

    # ---- 7. a control that must not move --------------------------------------
    print("\n7. CONTROL: a metric with no points in it (01_q2_findings.md line 15)")
    for label, pid, rep in (("Reid at the 5 (no Gobert), 3PA per 100", config.NAZ_ID, "37.4"),
                            ("Gobert at the 5, 3PA per 100", config.GOBERT_ID, "29.2")):
        sub = w_po[w_po.lineup_id.apply(lambda lid: analysis.player_in_lineup(lid, pid))]
        if pid == config.NAZ_ID:
            sub = sub[sub.lineup_id.apply(lambda lid: not analysis.player_in_lineup(lid, config.GOBERT_ID))]
        if sub.empty:
            continue
        b, a, ci = both(sub, analysis.m_fg3a_per_100)
        record(label, "01_q2_findings.md", rep, b, a, ci)

    df = pd.DataFrame(ROWS)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    df.to_csv(OUT, index=False)
    print("\n%d figures recomputed; %d flagged" % (len(df), int((df.flag != "").sum())))
    print("mean absolute shift %.2f, largest %.2f (%s)"
          % (df["shift"].abs().mean(), df["shift"].abs().max(),
             df.loc[df["shift"].abs().idxmax(), "figure"]))  # df.shift is a method
    if (df.flag != "").any():
        print("\nFLAGGED:")
        print(df[df.flag != ""][["figure", "reported", "before", "after", "shift",
                                 "ci_half_width", "flag"]].to_string(index=False))
    print("\nwrote %s" % os.path.relpath(OUT, ROOT))


if __name__ == "__main__":
    main()

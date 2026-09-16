#!/usr/bin/env python3
"""M4: every legal five Minnesota can put on the floor, scored and labelled.

WHAT THIS IS AND IS NOT. It is a scored enumeration, not a rotation forecast. Most of
these fives have never played a second together, and the ones that have played are the
only ones carrying evidence rather than arithmetic. Every row is labelled OBSERVED with
its possession count or COMPOSED, and the composed ones are ranked only where the spread
across the four views is small enough to mean anything.

SCORING, and each is stated as what it is:

  impact_off / impact_def   minutes-neutral sum of the five players' offensive and
                            defensive components. Sign convention: net = off - def, so a
                            NEGATIVE def is good defence.
  fg3a_rate                 share of the five's shots taken from three, 2025-26.
  fg3_pct                   **weighted by three-point ATTEMPTS, never by minutes.** An
                            earlier version of this project weighted a lineup's shooting
                            by minutes and handed Rudy Gobert, 0-for-7 from three on
                            2,710 minutes, the largest weight in the average, producing
                            .280 for a group that actually shot .372. Attempts is the
                            only correct weight.
  rim_protect               the defensive component of the biggest defender in the five.
                            A MODEL proxy, not a measurement of rim deterrence.
  creation                  assists per game summed across the five, 2025-26.
  size                      games-weighted mean height in inches.

REFERENCE ROWS. Last season's Reid+Gobert and Randle+Gobert pairings are carried so the
composed fives can be read against something that actually happened.

    python kuminga/scripts/m4_lineup_study.py
"""
from __future__ import annotations

import itertools
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "offseason", "scripts"))
sys.path.insert(0, os.path.join(REPO, "postmortem"))
sys.path.insert(0, HERE)

from kuminga.lib import kfreeze, runlog                        # noqa: E402
from build_strengths import build_impacts, add_rookie_impacts  # noqa: E402
from lib import db                                             # noqa: E402

POOL = os.path.join(REPO, "kuminga", "outputs", "player_pool_2026_27.csv")
VALUE = os.path.join(REPO, "offseason", "data", "player_value.csv")
DARKO = os.path.join(REPO, "offseason", "data", "darko-dpm-leaderboard.csv")
OUT = os.path.join(REPO, "kuminga", "outputs", "m4_lineups.csv")
FORKS = ["consensus", "rapm", "box", "darko"]
SD_MAX = 1.5          # a composed five with a wider four-view spread is not ranked


def main():
    with runlog.run("m4_lineup_study", inputs={"sd_max": SD_MAX}) as r:
        pool = pd.read_csv(POOL)
        value = pd.read_csv(VALUE)
        darko = pd.read_csv(DARKO)
        darko.columns = [c.strip().lstrip("﻿") for c in darko.columns]
        bio_f, _ = kfreeze.load("player_bio")
        imps, _ = build_impacts(value, darko, bio_f)
        add_rookie_impacts(imps, pool)

        mn = pool[(pool.scenario == "current") & (pool.team_abbr == "MIN")].copy()
        mn = mn[mn.player_id.notna()].copy()
        # AVAILABILITY. A player the pipeline has out for the season (rs_avail 0) cannot
        # be in a five. The first versions enumerated him anyway, and Donte DiVincenzo
        # (Achilles, out for 2026-27) led the closing candidates.
        out_ = mn[mn.rs_avail <= 0].player_name.tolist()
        mn = mn[mn.rs_avail > 0].copy()
        r.note("excluded as unavailable for 2026-27 (rs_avail 0): %s"
               % (", ".join(out_) if out_ else "none"))
        mn["pid"] = mn.player_id.astype(int).astype(str)
        r.note("Minnesota roster available to enumerate: %d players" % len(mn))

        # ---- per-player descriptive stats from the warehouse -------------------
        b = db.query("""
            select player_id, player_name, player_height_inches as height,
                   gp, ast, pts
            from nba.nba_player_season_bio
            where season_type = 'Regular Season' and season_year = '2025-26'
        """)
        for c in ("height", "gp", "ast", "pts"):
            b[c] = pd.to_numeric(b[c], errors="coerce")
        sl = db.query("""
            select player_id,
                   coalesce(left_corner_3_fga,0)+coalesce(right_corner_3_fga,0)
                     +coalesce(above_break_3_fga,0) as fg3a,
                   coalesce(left_corner_3_fgm,0)+coalesce(right_corner_3_fgm,0)
                     +coalesce(above_break_3_fgm,0) as fg3m,
                   coalesce(restricted_area_fga,0)+coalesce(paint_non_ra_fga,0)
                     +coalesce(midrange_fga,0)+coalesce(left_corner_3_fga,0)
                     +coalesce(right_corner_3_fga,0)+coalesce(above_break_3_fga,0) as fga
            from nba.nba_player_shot_locations_season
            where season_type = 'Regular Season' and season_year = '2025-26'
        """)
        for c in ("fg3a", "fg3m", "fga"):
            sl[c] = pd.to_numeric(sl[c], errors="coerce")
        mn = mn.merge(b[["player_id", "height", "gp", "ast"]], on="player_id", how="left")
        mn = mn.merge(sl, on="player_id", how="left")
        miss = mn[mn.fga.isna()].player_name.tolist()
        if miss:
            r.note("  no 2025-26 shooting row (rookies / no NBA season): %s"
                   % ", ".join(miss))

        # ---- enumerate legal fives ---------------------------------------------
        # A five needs at least one big and at least one guard, and no more than three
        # of any pool. That is the loosest constraint that still rules out a five with
        # no centre or five guards, and it is stated rather than tuned.
        recs = mn.set_index("pid").to_dict("index")
        pids = list(recs)
        fives = []
        for c in itertools.combinations(pids, 5):
            pools = [recs[p]["pool"] for p in c]
            if pools.count("big") < 1 or pools.count("guard") < 1:
                continue
            if max(pools.count(x) for x in ("guard", "forward", "big")) > 3:
                continue
            fives.append(c)
        r.note("legal fives enumerated: %d (at least one big, at least one guard, "
               "no more than three of any pool)" % len(fives))

        # ---- observed possessions from last season's stints --------------------
        obs = {}
        try:
            st = pd.read_parquet(os.path.join(REPO, "kuminga", "data",
                                              "stints_2025_26.parquet"))
            st = st[st.team_id == 1610612750]
            for _, x in st.iterrows():
                key = frozenset(str(v) for v in str(x.lineup_id).split(","))
                obs[key] = obs.get(key, 0.0) + float(x.possessions_off or 0)
            r.note("observed Minnesota lineups in 2025-26 stints: %d distinct" % len(obs))
        except Exception as e:                                    # noqa: BLE001
            r.note("stint file unavailable (%s); every row will be COMPOSED"
                   % type(e).__name__)

        rows = []
        for c in fives:
            names = [recs[p]["player_name"] for p in c]
            off = {f: sum(imps[f].get(p, {}).get("off", 0.0) for p in c) for f in FORKS}
            dff = {f: sum(imps[f].get(p, {}).get("def", 0.0) for p in c) for f in FORKS}
            net = {f: off[f] - dff[f] for f in FORKS}
            vals = list(net.values())
            fg3a = sum(recs[p].get("fg3a") or 0 for p in c)
            fg3m = sum(recs[p].get("fg3m") or 0 for p in c)
            fga = sum(recs[p].get("fga") or 0 for p in c)
            # a missing height is NaN, and NaN is truthy, so `if h` let it through and
            # made the mean NaN; and max() over NaN picked an arbitrary "biggest"
            heights = [recs[p]["height"] for p in c if pd.notna(recs[p].get("height"))]
            biggest = max(c, key=lambda p: recs[p]["height"]
                          if pd.notna(recs[p].get("height")) else 0.0)
            rows.append(dict(
                lineup=" / ".join(sorted(names)),
                observed_poss=obs.get(frozenset(c), 0.0),
                label="OBSERVED" if obs.get(frozenset(c), 0) > 0 else "COMPOSED",
                net_mean=float(np.mean(vals)), net_sd=float(np.std(vals)),
                net_lo=float(min(vals)), net_hi=float(max(vals)),
                impact_off=float(np.mean(list(off.values()))),
                impact_def=float(np.mean(list(dff.values()))),
                fg3a_rate=(fg3a / fga if fga else np.nan),
                fg3_pct=(fg3m / fg3a if fg3a else np.nan),
                rim_protect=float(imps["consensus"].get(biggest, {}).get("def", 0.0)),
                # PER GAME. `nba_player_season_bio.ast` is a season TOTAL; summing totals
                # (as a first version did, 1,150 for a five) charged a player for games
                # he missed. Kuminga's 36 games halved his share.
                creation=sum((recs[p].get("ast") or 0) / recs[p]["gp"]
                             for p in c if (recs[p].get("gp") or 0) > 0),
                size=(float(np.mean(heights)) if heights else np.nan),
                has_gobert=any(recs[p]["player_name"] == "Rudy Gobert" for p in c),
                n_bigs=sum(1 for p in c if recs[p]["pool"] == "big")))
        d = pd.DataFrame(rows)
        d["rankable"] = (d.label == "OBSERVED") | (d.net_sd <= SD_MAX)
        d.to_csv(OUT, index=False)

        n_obs = int((d.label == "OBSERVED").sum())
        r.note("  %d of %d fives have actually played together; %d composed fives have "
               "a four-view spread wide enough that the model refuses to rank them "
               "(sd > %.1f)" % (n_obs, len(d), int((~d.rankable).sum()), SD_MAX))

        def show(title, sub, by, asc=False, n=4):
            r.note("")
            r.note("  %s" % title)
            if not len(sub):
                r.note("    none qualify")
                return
            for _, x in sub.sort_values(by, ascending=asc).head(n).iterrows():
                r.note("    %-58s net %+5.2f [%+.2f,%+.2f] | 3PA%% %s 3P%% %s | "
                       "size %s | %s"
                       % (x.lineup[:58], x.net_mean, x.net_lo, x.net_hi,
                          "%.3f" % x.fg3a_rate if pd.notna(x.fg3a_rate) else " n/a ",
                          "%.3f" % x.fg3_pct if pd.notna(x.fg3_pct) else " n/a ",
                          "%.1f" % x["size"] if pd.notna(x["size"]) else "n/a",
                          ("OBSERVED %d poss" % x.observed_poss)
                          if x.label == "OBSERVED" else "composed"))

        # ---- a classification finding that has to be surfaced, not printed away --
        bigs = mn[mn.pool == "big"].player_name.tolist()
        r.note("")
        r.note("  POSITION POOLS: Minnesota has %d player(s) pooled as a BIG: %s"
               % (len(bigs), ", ".join(bigs)))
        if len(bigs) < 2:
            r.note("    **Joan Beringer, listed C by Spotrac and a seven-foot rookie "
                   "centre, is carried as `Forward` by the position source and pooled "
                   "as a forward.** Two consequences, and neither is a fact about the "
                   "roster:")
            r.note("      1. Every legal five must contain Gobert, so 'best five "
                   "without Gobert' and 'double big' are EMPTY BY CONSTRUCTION rather "
                   "than because no such lineup is good.")
            r.note("      2. Minnesota's own big-minutes budget is 53.7 a game, from "
                   "last season's Gobert-plus-Reid shape. One pooled big with a "
                   "ceiling near 34 cannot absorb it, so roughly 19 minutes of big "
                   "budget spills to the other pools every night.")
            r.note("    This is the single highest-priority correction for the next "
                   "session, because the double-big question is the structural "
                   "question about this roster and the model currently cannot ask it.")

        ok = d[d.rankable]
        show("BEST OFFENCE (highest offensive impact):", ok, "impact_off")
        show("BEST DEFENCE (most negative defensive component):", ok, "impact_def",
             asc=True)
        show("CLOSING CANDIDATES (best net, rankable only):", ok, "net_mean")
        show("BEST WITHOUT GOBERT:", ok[~ok.has_gobert], "net_mean")
        show("DOUBLE BIG:", ok[ok.n_bigs >= 2], "net_mean")

        r.note("")
        r.note("  THE MODEL REFUSES TO RANK these composed fives (widest four-view "
               "spread), and they are listed because refusing quietly is worse:")
        for _, x in d[~d.rankable].nlargest(4, "net_sd").iterrows():
            r.note("    %-58s net %+5.2f but spread %+.2f to %+.2f (sd %.2f)"
                   % (x.lineup[:58], x.net_mean, x.net_lo, x.net_hi, x.net_sd))

        r.note("")
        r.note("  REFERENCE, last season's Minnesota pairings, from the stint file:")
        try:
            st2 = pd.read_parquet(os.path.join(REPO, "kuminga", "data",
                                               "stints_2025_26.parquet"))
            st2 = st2[st2.team_id == 1610612750].copy()
            ids = db.query("""select player_id, player_name
                              from nba.nba_player_season_bio
                              where season_year='2025-26'
                                and season_type='Regular Season'""")
            nm = dict(zip(ids.player_id.astype(str), ids.player_name))
            for a, b_ in (("Naz Reid", "Rudy Gobert"), ("Julius Randle", "Rudy Gobert")):
                ia = [k for k, v in nm.items() if v == a]
                ib = [k for k, v in nm.items() if v == b_]
                if not ia or not ib:
                    r.note("    %s + %s: ids not resolved" % (a, b_))
                    continue
                sel = st2[st2.lineup_id.astype(str).str.contains(ia[0])
                          & st2.lineup_id.astype(str).str.contains(ib[0])]
                poss = float(sel.possessions_off.sum())
                pf, pa = float(sel.points_for.sum()), float(sel.points_against.sum())
                dpos = float(sel.possessions_def.sum()) or 1.0
                r.note("    %-14s + %-12s %7.0f off poss | %.1f per 100 for, %.1f "
                       "against, net %+.1f"
                       % (a, b_, poss, 100 * pf / (poss or 1), 100 * pa / dpos,
                          100 * pf / (poss or 1) - 100 * pa / dpos))
        except Exception as e:                                    # noqa: BLE001
            r.note("    stint reference unavailable (%s)" % type(e).__name__)
        r.output(OUT, rows=len(d))

    print()
    print(d.nlargest(6, "net_mean")[["lineup", "label", "net_mean", "net_sd"]]
          .round(2).to_string(index=False))


if __name__ == "__main__":
    main()

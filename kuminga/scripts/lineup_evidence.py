#!/usr/bin/env python3
"""Item 15: descriptive lineup evidence from 2025-26 play-by-play.

DESCRIPTIVE ONLY. These are on-court splits, not causal estimates and not a fit model.
Lineup net ratings over a single season are small-sample and heavily confounded by who
else is on the floor, opponent quality, and score state. The project has burned itself
on exactly this before (the DiVincenzo lineup finding turned out to be a round-of-
opponent effect, not a personnel effect), so every number here ships with its
possession count and nothing here is offered as an effect.

WHAT IT ANSWERS
  1. Randle + Gobert vs Reid + Gobert: net rating and 3-point attempt rate. The
     frontcourt pairing question the Kuminga signing inherits.
  2. Kuminga on/off at Golden State and at Atlanta, separately, because his role
     changed at the February trade.
  3. Kuminga's shot profile: rim rate, three-point rate, three-point accuracy, and
     transition share.

    python kuminga/scripts/lineup_evidence.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "postmortem"))

from lib import db                # noqa: E402
from kuminga.lib import runlog    # noqa: E402

STINTS = os.path.join(REPO, "kuminga", "data", "stints_2025_26.parquet")
OUT = os.path.join(REPO, "kuminga", "outputs", "lineup_evidence.csv")
OUT_SHOT = os.path.join(REPO, "kuminga", "outputs", "kuminga_shot_profile.csv")

PID = {"Randle": 203944, "Gobert": 203497, "Reid": 1629675, "Kuminga": 1630228,
       "Edwards": 1630162, "McDaniels": 1630183, "DiVincenzo": 1628978}
TEAM_ID = {"MIN": 1610612750, "GSW": 1610612744, "ATL": 1610612737}
MIN_POSS = 100          # below this, report but flag as too thin to read


def has(lineup_id: str, pid: int) -> bool:
    """lineup_id is a COMMA-separated, sorted list of player ids.

    Splitting on the wrong delimiter here does not raise: it silently returns False for
    every player, which reads as "this player was never on the floor" and produces a
    clean-looking table of zeroes. Guarded by the assertion in main().
    """
    return str(pid) in str(lineup_id).split(",")


def agg(df: pd.DataFrame) -> dict:
    po, pd_ = df.possessions_off.sum(), df.possessions_def.sum()
    pf, pa = df.points_for.sum(), df.points_against.sum()
    fga, fg3a = df.fga_off.sum(), df.fg3a_off.sum()
    fg3m = df.fg3m_off.sum()
    return dict(
        n_stints=len(df), minutes=df.duration_sec.sum() / 60.0,
        poss_off=po, poss_def=pd_,
        off_rating=(pf / po * 100) if po else np.nan,
        def_rating=(pa / pd_ * 100) if pd_ else np.nan,
        net_rating=((pf / po * 100) - (pa / pd_ * 100)) if po and pd_ else np.nan,
        fg3a_rate=(fg3a / fga) if fga else np.nan,
        fg3_pct=(fg3m / fg3a) if fg3a else np.nan,
    )


def main():
    with runlog.run("lineup_evidence", inputs={"stints": STINTS}) as r:
        st = pd.read_parquet(STINTS)
        st = st[~st.in_garbage_time]
        r.note(f"{len(st):,} non-garbage stints loaded")

        # Guard: every lineup must parse to exactly five ids, and the players we are
        # about to split on must actually appear. A wrong delimiter or an id typo
        # produces zeroes rather than an error, so it is asserted rather than assumed.
        sizes = st.lineup_id.map(lambda l: len(str(l).split(",")))
        assert (sizes == 5).all(), f"lineup_id does not parse to 5 ids: {sizes.value_counts().to_dict()}"
        for nm, pid in PID.items():
            n = int(st.lineup_id.map(lambda l: has(l, pid)).sum())
            assert n > 0, f"{nm} ({pid}) appears in ZERO stints: id or delimiter is wrong"
            r.note(f"  guard: {nm} appears in {n:,} stints")

        rows = []

        # ---- 1. the frontcourt pairings ------------------------------------
        mn = st[st.team_id == TEAM_ID["MIN"]]
        r.note(f"MIN stints: {len(mn):,}")
        pairs = {
            "Randle+Gobert": (PID["Randle"], PID["Gobert"]),
            "Reid+Gobert": (PID["Reid"], PID["Gobert"]),
            "Randle+Reid": (PID["Randle"], PID["Reid"]),
            "Gobert_only_of_the_three": None,
        }
        for label, pair in pairs.items():
            if pair is None:
                sub = mn[mn.lineup_id.map(lambda l: has(l, PID["Gobert"])
                                          and not has(l, PID["Randle"])
                                          and not has(l, PID["Reid"]))]
            else:
                a, b = pair
                sub = mn[mn.lineup_id.map(lambda l: has(l, a) and has(l, b))]
            d = agg(sub)
            d.update(group="MIN frontcourt", label=label, team="MIN")
            rows.append(d)
            r.note(f"  {label:26s} {d['poss_off']:>6.0f} poss off | net "
                   f"{d['net_rating']:+6.2f} | 3PA rate {d['fg3a_rate']:.3f}")

        # ---- 2. Kuminga on/off, by team ------------------------------------
        for team in ("GSW", "ATL"):
            t = st[st.team_id == TEAM_ID[team]]
            on = t[t.lineup_id.map(lambda l: has(l, PID["Kuminga"]))]
            off = t[t.lineup_id.map(lambda l: not has(l, PID["Kuminga"]))]
            for label, sub in (("Kuminga ON", on), ("Kuminga OFF", off)):
                d = agg(sub)
                d.update(group=f"Kuminga on/off {team}", label=label, team=team)
                rows.append(d)
            don, doff = agg(on), agg(off)
            if don["poss_off"] and doff["poss_off"]:
                r.note(f"  {team}: ON net {don['net_rating']:+6.2f} "
                       f"({don['poss_off']:.0f} poss) | OFF net {doff['net_rating']:+6.2f} "
                       f"({doff['poss_off']:.0f} poss) | diff "
                       f"{don['net_rating'] - doff['net_rating']:+6.2f}")
                rows.append(dict(group=f"Kuminga on/off {team}", label="ON minus OFF",
                                 team=team, net_rating=don["net_rating"] - doff["net_rating"],
                                 poss_off=min(don["poss_off"], doff["poss_off"]),
                                 fg3a_rate=don["fg3a_rate"] - doff["fg3a_rate"]))

        ev = pd.DataFrame(rows)
        ev["too_thin"] = ev.poss_off < MIN_POSS
        ev.to_csv(OUT, index=False)
        r.note(f"wrote {len(ev)} evidence rows; {int(ev.too_thin.sum())} flagged too thin")

        # ---- 3. Kuminga shot profile ---------------------------------------
        shots = db.query("""
            SELECT season_type, shot_zone_basic, shot_zone_range, shot_type,
                   shot_distance, shot_made_flag, team_id
            FROM nba_shot_chart_detail
            WHERE player_id = %s AND season_year = %s""", (PID["Kuminga"], "2025-26"))
        prof = []
        for team_label, tid in (("GSW", TEAM_ID["GSW"]), ("ATL", TEAM_ID["ATL"]),
                                ("both", None)):
            s = shots if tid is None else shots[shots.team_id == tid]
            for stype in ("Regular Season", "Playoffs", "all"):
                ss = s if stype == "all" else s[s.season_type == stype]
                if not len(ss):
                    continue
                is3 = ss.shot_type.str.contains("3PT", na=False)
                rim = ss.shot_distance <= 4
                prof.append(dict(
                    team=team_label, season_type=stype, fga=len(ss),
                    rim_rate=float(rim.mean()),
                    rim_fg_pct=float(ss[rim].shot_made_flag.mean()) if rim.any() else np.nan,
                    fg3a_rate=float(is3.mean()),
                    fg3_pct=float(ss[is3].shot_made_flag.mean()) if is3.any() else np.nan,
                    mid_rate=float(((~is3) & (~rim)).mean()),
                ))
        pr = pd.DataFrame(prof)

        syn = db.query("""
            SELECT season_year, season_type, team_abbreviation, play_type,
                   poss, poss_pct, ppp, percentile
            FROM nba_synergy_player_play_types
            WHERE player_id = %s AND season_year IN ('2024-25','2025-26')
              AND type_grouping = 'Offensive'   -- capitalised in the table
            ORDER BY season_year, season_type, poss DESC""", (PID["Kuminga"],))
        pr.to_csv(OUT_SHOT, index=False)
        r.note("Kuminga shot profile (both teams, regular season): " +
               str(pr[(pr.team == 'both') & (pr.season_type == 'Regular Season')]
                   [["rim_rate", "fg3a_rate", "fg3_pct", "mid_rate"]].round(3).to_dict("records")))
        syn.to_csv(os.path.join(REPO, "kuminga", "outputs", "kuminga_play_types.csv"), index=False)
        tr = syn[(syn.play_type == "Transition") & (syn.season_year == "2025-26")]
        assert len(tr), "no Transition rows: check type_grouping capitalisation"
        for _, x in tr.iterrows():
            r.note(f"  transition {x.season_type} {x.team_abbreviation}: "
                   f"{float(x.poss_pct)*100:.1f}% of possessions, {float(x.ppp):.3f} PPP, "
                   f"pctile {float(x.percentile)*100:.0f}")
        r.output(OUT, rows=len(ev))
        r.output(OUT_SHOT, rows=len(pr))

    print()
    print(ev[["group", "label", "poss_off", "net_rating", "fg3a_rate", "too_thin"]]
          .round(3).to_string(index=False))
    print()
    print(pr.round(3).to_string(index=False))


if __name__ == "__main__":
    main()

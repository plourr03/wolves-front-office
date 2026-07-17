"""JD-COVER (the anchor claim) from the fitengine stint panel.

Spec: team defensive rating in the CREATOR's minutes, wing ON vs OFF. Negative
on-off (DRTG_on - DRTG_off) = the wing improves team defense in the star's
minutes, which is what the draft 3.0-per-100 threshold wants to see.

This is STINT/lineup-dependent, so it is NOT in compute_markers.py. The panel
(all-for-one/tripwire-backtest/data/stints_panel/) is readily usable and covers
RS 2014-15..2024-25, so we compute JD-COVER for every marker-usable member whose
AFTER season is <= 2024-25 (four members with a 2025-26 AFTER fall outside the
built panel and are reported as panel-pending, not faked).

Per member, over the wing's NEW-team stints in the AFTER season (garbage time
dropped): among stints with the creator on the floor (creator_id in lineup_id),
split by whether the wing is also on. Aggregate points_against / possessions_def.
Report possession counts so the possession-floor TUNE is visible.

Writes data/jd_cover.parquet.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(r"C:\Users\bobby\playground\wolves-front-office")
OUTDIR = REPO / "all-for-one" / "board" / "jaden_calibration" / "data"
PANEL = REPO / "all-for-one" / "tripwire-backtest" / "data" / "stints_panel"
sys.path.insert(0, str(REPO / "postmortem"))
from lib.db import query  # noqa: E402

pd.set_option("display.width", 220)
pd.set_option("display.max_rows", 200)

PANEL_MAX_SS = 2024   # panel built through 2024-25
SEEDS = {203932: "Aaron Gordon", 1628969: "Mikal Bridges", 1628384: "OG Anunoby"}


def game_ids(team_id: int, ss: int) -> list[str]:
    sid = f"2{ss}"  # RS season_id, e.g. 22021 for 2021-22
    r = query(
        """
        SELECT DISTINCT game_id FROM nba.nba_games
        WHERE team_id = %s AND season_id::text = %s
        """,
        (team_id, sid),
    )
    return r.game_id.astype(str).tolist()


def main() -> None:
    c = pd.read_parquet(OUTDIR / "calibration_class.parquet")
    mu = c[c.marker_usable].copy()
    comp = mu[mu.after_ss <= PANEL_MAX_SS].copy()
    pend = mu[mu.after_ss > PANEL_MAX_SS].copy()
    print(f"marker-usable: {len(mu)}; JD-COVER computable (after<=2024-25): {len(comp)}; "
          f"panel-pending (2025-26 AFTER): {len(pend)}")

    rows = []
    for r in comp.itertuples():
        wing = str(int(r.player_id)); creator = str(int(r.creator_id))
        team_id = int(r.new_team_id); ss = int(r.after_ss)
        gids = game_ids(team_id, ss)
        frames = []
        for g in gids:
            fp = PANEL / f"{g}.parquet"
            if not fp.exists():
                continue
            df = pd.read_parquet(fp, columns=["team_id", "lineup_id", "possessions_def",
                                              "points_against", "in_garbage_time"])
            df = df[(df.team_id == team_id) & (~df.in_garbage_time)]
            if len(df):
                frames.append(df)
        if not frames:
            continue
        st = pd.concat(frames, ignore_index=True)
        lu = st.lineup_id.str.split(",")
        creator_on = lu.apply(lambda xs: creator in xs)
        wing_on = lu.apply(lambda xs: wing in xs)
        cst = st[creator_on]
        on = cst[wing_on[creator_on.index][creator_on]]
        off = cst[~wing_on[creator_on.index][creator_on]]

        def agg(d):
            pa = d.points_against.sum(); pos = d.possessions_def.sum()
            return pa, pos, (pa / pos * 100.0 if pos > 0 else np.nan)

        pa_on, pos_on, drtg_on = agg(on)
        pa_off, pos_off, drtg_off = agg(off)
        onoff = (drtg_on - drtg_off) if (pd.notna(drtg_on) and pd.notna(drtg_off)) else np.nan
        rows.append({
            "player_id": int(r.player_id), "wing": r.wing, "new_team": r.new_team,
            "creator": r.creator, "after_ss": ss,
            "poss_creator_on_wing_on": float(pos_on), "poss_creator_on_wing_off": float(pos_off),
            "drtg_wing_on": drtg_on, "drtg_wing_off": drtg_off, "jd_cover_onoff": onoff,
        })

    out = pd.DataFrame(rows).sort_values("wing").reset_index(drop=True)
    for r in pend.itertuples():
        # record panel-pending members explicitly
        out = pd.concat([out, pd.DataFrame([{
            "player_id": int(r.player_id), "wing": r.wing, "new_team": r.new_team,
            "creator": r.creator, "after_ss": int(r.after_ss),
            "poss_creator_on_wing_on": np.nan, "poss_creator_on_wing_off": np.nan,
            "drtg_wing_on": np.nan, "drtg_wing_off": np.nan, "jd_cover_onoff": np.nan,
        }])], ignore_index=True)
    out.to_parquet(OUTDIR / "jd_cover.parquet", index=False)
    print(f"wrote {OUTDIR/'jd_cover.parquet'} ({len(out)} rows)")

    print("\nSEED JD-COVER:")
    with pd.option_context("display.float_format", lambda v: f"{v:.2f}"):
        print(out[out.player_id.isin(SEEDS)].to_string(index=False))

    valid = out[out.jd_cover_onoff.notna()]
    print(f"\nJD-COVER computed for {len(valid)} members.")
    print("possession floor visibility: min OFF possessions =",
          f"{valid.poss_creator_on_wing_off.min():.0f}, median OFF =",
          f"{valid.poss_creator_on_wing_off.median():.0f}")


if __name__ == "__main__":
    main()

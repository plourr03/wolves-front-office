#!/usr/bin/env python3
"""Item 4 audit: what changed in team_state between the June 17 build and the rebuild.

The June file was built before free agency. Everything downstream that read it was
answering on a pre-offseason league. This quantifies the drift so the change is on the
record rather than silently absorbed.

    python kuminga/scripts/diff_team_state.py
"""
from __future__ import annotations

import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO)

from kuminga.lib import runlog  # noqa: E402

OLD = os.path.join(REPO, "kuminga", "data", "team_state.PRE_ITEM4.csv")
NEW = os.path.join(REPO, "offseason", "data", "team_state.csv")
OUT = os.path.join(REPO, "kuminga", "outputs", "team_state_diff_2026_27.csv")

COLS = ["apron_team_salary", "cap_team_salary", "tier", "distance_to_second_apron",
        "distance_to_first_apron", "taxpayer_mle_available", "full_mle_available",
        "hard_capped", "is_taxpayer"]


def main():
    with runlog.run("diff_team_state", inputs={"old": OLD, "new": NEW}) as r:
        old = pd.read_csv(OLD)
        new = pd.read_csv(NEW)
        o = old[(old.scenario_id == "base") & (old.season == "2026-27")].set_index("team_abbr")
        n = new[(new.scenario_id == "base") & (new.season == "2026-27")].set_index("team_abbr")
        j = o[COLS].join(n[COLS], lsuffix="_jun17", rsuffix="_now")
        j["salary_change"] = j.apron_team_salary_now - j.apron_team_salary_jun17
        j["tier_changed"] = j.tier_jun17 != j.tier_now
        j["mle_status_changed"] = j.taxpayer_mle_available_jun17 != j.taxpayer_mle_available_now
        j = j.sort_values("salary_change", ascending=False)
        j.to_csv(OUT)

        r.note(f"teams whose apron tier changed: {int(j.tier_changed.sum())} of {len(j)}")
        r.note(f"median absolute salary change: ${j.salary_change.abs().median():,.0f}")
        r.note(f"largest increase: {j.salary_change.idxmax()} +${j.salary_change.max():,.0f}")
        r.note(f"largest decrease: {j.salary_change.idxmin()} ${j.salary_change.min():,.0f}")
        for t in j[j.tier_changed].index:
            r.note(f"  {t}: {j.loc[t,'tier_jun17']} -> {j.loc[t,'tier_now']} "
                   f"({j.loc[t,'salary_change']/1e6:+.1f}M)")
        r.output(OUT, rows=len(j))


if __name__ == "__main__":
    main()

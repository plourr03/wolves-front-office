"""F5 prep contracts (no DB): team-change detection classifies midseason
vs offseason correctly, and the sealed window can never leak into a dev
artifact even if a change list contains sealed-era rows."""

import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.etl.transaction_universe import (  # noqa: E402
    DEV_END_YEARS, detect_team_changes)


def synth_appearances():
    rows = []

    def add(pid, team, dates, season):
        for d in dates:
            rows.append({"player_id": pid, "player_name": f"P{pid}",
                         "team_id": team, "game_id": f"g{len(rows)}",
                         "season_year": season, "game_date": pd.Timestamp(d),
                         "end_year": int(season[:4]) + 1})

    # player 1: midseason trade in 2018-19 (team 10 -> 20 in February)
    add(1, 10, ["2018-11-01", "2019-01-15"], "2018-19")
    add(1, 20, ["2019-02-08", "2019-03-01"], "2018-19")
    # player 2: offseason move (team 10 in 2018-19, team 30 in 2019-20)
    add(2, 10, ["2018-11-02", "2019-04-01"], "2018-19")
    add(2, 30, ["2019-10-25", "2020-01-05"], "2019-20")
    # player 3: no change
    add(3, 40, ["2018-11-03", "2019-03-03"], "2018-19")
    # player 4: SEALED-era change (2022-23), must never reach a dev artifact
    add(4, 10, ["2022-01-05"], "2021-22")
    add(4, 50, ["2022-11-01"], "2022-23")
    return pd.DataFrame(rows)


def test_detects_and_classifies_changes():
    cases = detect_team_changes(synth_appearances())
    assert set(cases.player_id) == {1, 2, 4}

    c1 = cases[cases.player_id == 1].iloc[0]
    assert bool(c1.midseason) and c1.new_team_id == 20
    assert c1.transaction_date == pd.Timestamp("2019-02-08")
    assert c1.window_end_year == 2019 and c1.preceding_end_year == 2018

    c2 = cases[cases.player_id == 2].iloc[0]
    assert not bool(c2.midseason) and c2.new_team_id == 30
    assert c2.window_end_year == 2020 and c2.preceding_end_year == 2019


def test_dev_filter_never_carries_sealed_years():
    cases = detect_team_changes(synth_appearances())
    dev = cases[cases.end_year.isin(DEV_END_YEARS)]
    assert 4 not in set(dev.player_id)          # 2022-23 case filtered
    assert set(dev.end_year).issubset(DEV_END_YEARS)
    assert max(DEV_END_YEARS) == 2021           # the seal starts at 2021-22

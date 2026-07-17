"""Phase 2 labels + Phase 3 for Scenario C (frontcourt succession).

Tests FC-DRB's predictive validity: does EARLY anchor-off defensive
rebounding predict the SEASON-LONG hole?

Per Scenario C case (team, hole_season, departed anchor), from the panel:
  early feature (first 25 games): team DRB proxy in anchor-off minutes.
    Since the anchor DEPARTED, "anchor-off" = the whole season for the new
    roster; the metric is the team's DRB proxy, and the question is whether
    its early value predicts its rest-of-season value AND whether the hole
    (low DRB) persisted.
  YC1 outcome (games 26-82): team DRB proxy, rest of season.

Because the anchor is gone, this is really: does the team's early DRB
predict its full-season DRB (a persistence/predictive check on the FC-DRB
metric within the succession class). Cases in the panel window (2014-24)
only; curated midseason cases (Capela/Allen/Davis) use the departure season.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr, pearsonr

REPO = Path(r"C:\Users\bobby\playground\wolves-front-office")
DATA = REPO / "all-for-one" / "tripwire-backtest" / "data"
PANEL = DATA / "stints_panel"
sys.path.insert(0, str(REPO / "postmortem"))
from lib.db import query  # noqa: E402


def drb_proxy(half):
    miss = (half.fga_def - half.fgm_def).sum()
    return (1 - half.oreb_def.sum() / miss) if miss > 0 else np.nan


def main() -> None:
    C = pd.read_parquet(DATA / "refclass_C.parquet")
    C = C[(C.hole_season >= 2014) & (C.hole_season <= 2024)].copy()
    a2i = query("SELECT DISTINCT team_abbreviation, team_id FROM nba.nba_games")
    # panel load for the needed team-seasons
    g = query("""SELECT game_id, team_id, RIGHT(season_id::text,4)::int ss, game_date
                 FROM nba.nba_games WHERE LEFT(season_id::text,1)='2'""")
    need = set((int(r.hole_season), int(r.team_id)) for r in C.itertuples())
    g2 = g[g[["ss", "team_id"]].apply(tuple, axis=1).isin(need)]
    files = [PANEL / f"{gid}.parquet" for gid in set(g2.game_id) if (PANEL / f"{gid}.parquet").exists()]
    print(f"loading {len(files)} panel games for {len(need)} Scenario C team-seasons...", flush=True)
    panel = pd.concat((pd.read_parquet(f) for f in files), ignore_index=True) if files else pd.DataFrame()
    panel = panel[~panel.in_garbage_time].merge(g, on=["game_id", "team_id"], how="inner")
    gn = (panel[["team_id", "ss", "game_id", "game_date"]].drop_duplicates()
          .sort_values(["team_id", "ss", "game_date", "game_id"]))
    gn["game_no"] = gn.groupby(["team_id", "ss"]).cumcount() + 1
    panel = panel.merge(gn[["team_id", "ss", "game_id", "game_no"]], on=["team_id", "ss", "game_id"])

    rows = []
    for r in C.itertuples():
        sub = panel[(panel.team_id == r.team_id) & (panel.ss == r.hole_season)]
        if not len(sub):
            continue
        early = sub[sub.game_no <= 25]
        rest = sub[(sub.game_no >= 26)]
        de, dr = drb_proxy(early), drb_proxy(rest)
        if pd.notna(de) and pd.notna(dr):
            rows.append({"team": r.team, "hole_season": r.hole_season, "anchor": r.anchor,
                         "mode": getattr(r, "mode"), "early_drb": de, "yc1_rest_drb": dr})
    cases = pd.DataFrame(rows)
    cases.to_parquet(DATA / "scenarioC_cases.parquet", index=False)
    print(f"\nScenario C labeled cases (in panel): {len(cases)}")
    if len(cases) >= 8:
        rho, _ = spearmanr(cases.early_drb, cases.yc1_rest_drb)
        r, _ = pearsonr(cases.early_drb, cases.yc1_rest_drb)
        print(f"  FC-DRB persistence within succession class: "
              f"Spearman={rho:.3f}, Pearson={r:.3f} (n={len(cases)})")
        print(f"  (does early anchor-off DRB predict rest-of-season DRB in the hole?)")
    print(cases.sort_values("hole_season").to_string(index=False))


if __name__ == "__main__":
    main()

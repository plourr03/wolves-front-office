"""Phase 2 labels + Phase 3 for Scenario A (co-star integration).

Tests the spec's central hypothesis (section 5): early OFFENSE is the false
signal in Scenario A; the separators are availability pace, shared-floor
DEFENSE, and the turnover/spacing interaction.

Per Scenario A case (arriving guard + qualifying incumbent), from the stint
panel:
  early features (first N games from arrival, N=20):
    pair_off_early   pair shared-floor offensive rating (pts/100 off poss)
    pair_drtg_early  pair shared-floor defensive rating (pts allowed/100)
    pair_net_early   off - def
  outcome labels:
    YA1_cont  pair shared-floor net rating over team games 41-82
              (>= 800 shared possessions else null)
    YA1_bin   YA1_cont >= 0
    YA3       breakup within 18 months (star traded / trade request); the
              hand-curated flag column is loaded from ya3_breakup.csv

Phase 3: for each early feature vs YA1_cont, Spearman + sign consistency
across cases. The hypothesis predicts pair_drtg_early separates and
pair_off_early does not.

Cases outside the panel window (pre-2014, 2025-26) are box-grain-only:
they keep box features/labels and drop the pair (stint) features.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

REPO = Path(r"C:\Users\bobby\playground\wolves-front-office")
DATA = REPO / "all-for-one" / "tripwire-backtest" / "data"
PANEL = DATA / "stints_panel"
sys.path.insert(0, str(REPO / "postmortem"))
from lib.db import query  # noqa: E402

pd.set_option("display.width", 220)
N_EARLY = 20
SHARED_POSS_LABEL_FLOOR = 800


def load_panel_for_teams(team_seasons: set) -> pd.DataFrame:
    g = query("""SELECT game_id, team_id, RIGHT(season_id::text,4)::int ss, game_date
                 FROM nba.nba_games WHERE LEFT(season_id::text,1)='2'""")
    g = g[g[["ss", "team_id"]].apply(tuple, axis=1).isin(team_seasons)]
    gid_set = set(g.game_id)
    files = [PANEL / f"{gid}.parquet" for gid in gid_set if (PANEL / f"{gid}.parquet").exists()]
    if not files:
        return pd.DataFrame()
    df = pd.concat((pd.read_parquet(f) for f in files), ignore_index=True)
    df = df.merge(g, on=["game_id", "team_id"], how="inner")
    df = df.sort_values(["team_id", "ss", "game_date", "game_id"])
    gn = (df[["team_id", "ss", "game_id", "game_date"]].drop_duplicates()
          .sort_values(["team_id", "ss", "game_date", "game_id"]))
    gn["game_no"] = gn.groupby(["team_id", "ss"]).cumcount() + 1
    return df.merge(gn[["team_id", "ss", "game_id", "game_no"]], on=["team_id", "ss", "game_id"])


def pair_stats(g: pd.DataFrame, p1: int, p2: int):
    """shared-floor off/def rating over stints where BOTH on floor."""
    def both(L):
        s = L.split(",")
        return str(p1) in s and str(p2) in s
    sh = g[g.lineup_id.map(both) & (~g.in_garbage_time)]
    op = sh.possessions_off.sum(); dp = sh.possessions_def.sum()
    if op < 1 or dp < 1:
        return None
    ortg = 100 * sh.points_for.sum() / op
    drtg = 100 * sh.points_against.sum() / dp
    return {"off": ortg, "drtg": drtg, "net": ortg - drtg,
            "shared_off_poss": int(op), "shared_def_poss": int(dp)}


def main() -> None:
    A = pd.read_parquet(DATA / "refclass_A.parquet")
    A = A[(A.prior_usg >= 0.28) & A.inc_strict].copy()  # strict class for labels
    # need incumbent pid -- rebuild from the who column via arrivals foundation
    af = pd.read_parquet(DATA / "arrivals_foundation.parquet")
    # map arriving name->pid
    names = query("SELECT player_id, first_name||' '||last_name nm FROM nba.nba_player_bio")
    id2nm = dict(zip(names.player_id, names.nm))
    nm2id = {}
    for pid, n in id2nm.items():
        nm2id.setdefault(n, pid)
    # incumbent pid: recompute strict incumbent per case from honors
    hon = pd.read_parquet(DATA / "honors.parquet")
    # attach arriving pid + incumbent pid
    # (refclass_A has inc_strict_name; map to pid)
    A["arr_pid"] = A.arriving.map(lambda n: nm2id.get(n))
    A["inc_pid"] = A.inc_strict_name.map(lambda n: nm2id.get(n) if pd.notna(n) else None)

    team_seasons = set((int(r.arr_ss), _abbr2id(r.new_team)) for r in A.itertuples())
    team_seasons = {ts for ts in team_seasons if ts[1] is not None and 2014 <= ts[0] <= 2024}
    print(f"loading panel for {len(team_seasons)} Scenario A team-seasons in window...", flush=True)
    panel = load_panel_for_teams(team_seasons)
    print(f"  panel rows: {len(panel)}", flush=True)

    rows = []
    for r in A.itertuples():
        tid = _abbr2id(r.new_team)
        rec = {"arriving": r.arriving, "arr_ss": r.arr_ss, "team": r.new_team,
               "incumbent": r.inc_strict_name, "kind": r.kind,
               "in_panel": (2014 <= r.arr_ss <= 2024)}
        if panel is not None and len(panel) and r.arr_pid and r.inc_pid and (2014 <= r.arr_ss <= 2024):
            g = panel[(panel.team_id == tid) & (panel.ss == r.arr_ss)]
            if r.kind == "midseason":
                g = g[g.game_date >= r.arr_date]
                g = g.assign(game_no=g.groupby(["team_id", "ss"]).cumcount() + 1) if len(g) else g
            early = g[g.game_no <= N_EARLY]
            latewin = g[(g.game_no >= 41) & (g.game_no <= 82)]
            pe = pair_stats(early, int(r.arr_pid), int(r.inc_pid))
            pl = pair_stats(latewin, int(r.arr_pid), int(r.inc_pid))
            if pe:
                rec.update(pair_off_early=pe["off"], pair_drtg_early=pe["drtg"],
                           pair_net_early=pe["net"], shared_early_poss=pe["shared_def_poss"])
            if pl and pl["shared_def_poss"] >= SHARED_POSS_LABEL_FLOOR:
                rec["ya1_cont"] = pl["net"]
                rec["ya1_bin"] = int(pl["net"] >= 0)
        rows.append(rec)

    cases = pd.DataFrame(rows)
    cases.to_parquet(DATA / "scenarioA_cases.parquet", index=False)
    print(f"\nScenario A labeled cases: {len(cases)}, "
          f"with ya1_cont: {cases.ya1_cont.notna().sum() if 'ya1_cont' in cases else 0}")
    if "ya1_cont" in cases:
        print(cases[["arriving", "arr_ss", "team", "incumbent", "pair_off_early",
                     "pair_drtg_early", "pair_net_early", "ya1_cont"]].to_string(index=False))

    # Phase 3: early feature vs YA1_cont
    print("\n" + "=" * 78)
    print("PHASE 3: which early feature predicts YA1 (pair net rating games 41-82)?")
    print("=" * 78)
    if "ya1_cont" in cases:
        lab = cases.dropna(subset=["ya1_cont"])
        print(f"labeled cases: {len(lab)} (N_GATE=8)")
        for feat in ["pair_off_early", "pair_drtg_early", "pair_net_early"]:
            sub = lab.dropna(subset=[feat])
            if len(sub) >= 3:
                rho, _ = spearmanr(sub[feat], sub.ya1_cont)
                # sign consistency vs class median
                fm, om = sub[feat].median(), sub.ya1_cont.median()
                # note: for drtg, LOWER is better, so flip expected direction
                sign = ((sub[feat] >= fm) == (sub.ya1_cont >= om)).mean()
                print(f"  {feat:18s}: Spearman={rho:+.3f}  sign_consistency={sign:.3f}  (n={len(sub)})")
        print("\nHypothesis check: pair_drtg_early should separate (negative Spearman,")
        print("lower early DRTG -> higher YA1 net); pair_off_early should NOT.")


def _abbr2id(abbr):
    global _A2I
    try:
        return _A2I.get(abbr)
    except NameError:
        m = query("SELECT DISTINCT team_abbreviation, team_id FROM nba.nba_games")
        _A2I = dict(zip(m.team_abbreviation, m.team_id))
        return _A2I.get(abbr)


_A2I = None
if __name__ == "__main__":
    m = query("SELECT DISTINCT team_abbreviation, team_id FROM nba.nba_games")
    _A2I = dict(zip(m.team_abbreviation, m.team_id))
    main()

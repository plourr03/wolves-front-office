"""Build the stint trust spike sample (tripwire backtest, Phase 0 Step 2).

Three strata, per Bobby's direction 2026-07-17:

  frontier  random games/season for 2010-11..2013-14, to locate the trust
            frontier. yy10-yy12 have never been attempted by fitengine
            (game_universe.parquet starts at yy13).
  targeted  every game of the candidate bonus cases living in the unproven
            zone. These are the cases the spike exists to price.
  spot      seed-case team-seasons from 2017-18..2020-21. Nominally proven,
            but format weirdness is a PER-GAME property, so season-level
            proof does not cover it.

SEAL GUARDRAIL: fitengine's backtest_protocol.yaml seals 2021-22..2025-26
(yy21..yy25) until F5. yy20 is 2020-21 and safe; yy21 is 2021-22 and sealed.
This script hard-asserts that no sampled game exceeds yy20.

Read-only against the warehouse. Writes a game list to scratchpad.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

FITENGINE = Path(r"C:\Users\bobby\playground\wolves-front-office\counterfactual-fit-engine")
sys.path.insert(0, str(FITENGINE))
from src.adapters.postmortem_lib import query  # noqa: E402

RNG_SEED = 20260717
N_FRONTIER_PER_SEASON = 150
N_SPOT_PER_TEAM_SEASON = 20

# yy -> season label, for the frontier
FRONTIER_SEASONS = {10: "2010-11", 11: "2011-12", 12: "2012-13", 13: "2013-14"}

# (yy, team_abbr, case label, date_from or None for whole season)
TARGETED = [
    (10, "NYK", "Anthony to NYK (Feb 2011)", "2011-02-23"),
    (11, "LAC", "Paul to LAC (Dec 2011)", None),
    (12, "LAL", "Howard to LAL (2012-13)", None),
]

SPOT = [
    (17, "OKC", "Anthony to OKC 2017"),
    (17, "MIN", "Butler to MIN 2017"),
    (17, "BOS", "Irving to BOS 2017"),
    (19, "LAC", "Leonard + George to LAC 2019"),
    (19, "HOU", "Westbrook to HOU 2019 / post-Capela"),
    (19, "BOS", "Walker to BOS 2019"),
    (20, "HOU", "Wall to HOU 2020"),
    (20, "PHX", "Paul to PHX 2020"),
    (20, "BKN", "Harden to BKN (Jan 2021)"),
]

SEAL_FIRST_YY = 21  # yy21 = 2021-22 = SEALED until F5. Never sample at or above.


def season_games(yy: int) -> pd.DataFrame:
    """All regular-season games of a season. season_id = '2' || yy+2000."""
    sid = f"2{2000 + yy}"
    return query(
        """
        SELECT DISTINCT game_id, game_date
        FROM nba.nba_games
        WHERE season_id::text = %s
        ORDER BY game_date, game_id
        """,
        (sid,),
    )


def team_season_games(yy: int, abbr: str, date_from: str | None) -> pd.DataFrame:
    sid = f"2{2000 + yy}"
    sql = """
        SELECT DISTINCT game_id, game_date
        FROM nba.nba_games
        WHERE season_id::text = %s AND team_abbreviation = %s
    """
    params: tuple = (sid, abbr)
    if date_from:
        sql += " AND game_date >= %s"
        params = (sid, abbr, date_from)
    sql += " ORDER BY game_date, game_id"
    return query(sql, params)


def main() -> None:
    rng = np.random.default_rng(RNG_SEED)
    rows = []

    print("=" * 72)
    print("FRONTIER stratum (yy10-yy13, random)")
    print("=" * 72)
    for yy, label in FRONTIER_SEASONS.items():
        pool = season_games(yy)
        n = min(N_FRONTIER_PER_SEASON, len(pool))
        pick = pool.iloc[rng.choice(len(pool), size=n, replace=False)]
        print(f"  {label} (yy{yy}): pool={len(pool):4d} sampled={n}")
        for gid in pick.game_id:
            rows.append({"game_id": gid, "yy": yy, "season": label,
                         "spike_stratum": "frontier", "case": ""})

    print("\n" + "=" * 72)
    print("TARGETED stratum (bonus cases in the unproven zone)")
    print("=" * 72)
    for yy, abbr, case, date_from in TARGETED:
        g = team_season_games(yy, abbr, date_from)
        print(f"  {case:32s} {abbr} yy{yy}: {len(g)} games")
        for gid in g.game_id:
            rows.append({"game_id": gid, "yy": yy, "season": FRONTIER_SEASONS.get(yy, f"yy{yy}"),
                         "spike_stratum": "targeted", "case": case})

    print("\n" + "=" * 72)
    print("SPOT stratum (seed-case team-seasons, 2017-18..2020-21)")
    print("=" * 72)
    for yy, abbr, case in SPOT:
        pool = team_season_games(yy, abbr, None)
        n = min(N_SPOT_PER_TEAM_SEASON, len(pool))
        pick = pool.iloc[rng.choice(len(pool), size=n, replace=False)]
        print(f"  {case:36s} {abbr} yy{yy}: pool={len(pool):3d} sampled={n}")
        for gid in pick.game_id:
            rows.append({"game_id": gid, "yy": yy, "season": f"20{yy}-{yy + 1}",
                         "spike_stratum": "spot", "case": case})

    df = pd.DataFrame(rows)

    # SEAL ASSERTION -- fail loud, never sample into fitengine's F5 window.
    breach = df[df.yy >= SEAL_FIRST_YY]
    assert len(breach) == 0, f"SEAL BREACH: {len(breach)} games at yy>={SEAL_FIRST_YY}"
    print(f"\nseal check: max yy sampled = {df.yy.max()} (yy{SEAL_FIRST_YY}+ is sealed). OK")

    # dedupe: a targeted game can also land in the frontier random draw.
    # keep the most specific stratum (targeted > spot > frontier).
    order = {"targeted": 0, "spot": 1, "frontier": 2}
    df["_o"] = df.spike_stratum.map(order)
    df = df.sort_values("_o").drop_duplicates("game_id", keep="first").drop(columns="_o")

    print("\n" + "=" * 72)
    print("SAMPLE")
    print("=" * 72)
    print(df.groupby("spike_stratum").size().to_string())
    print(f"\n  TOTAL unique games: {len(df)}")
    print(f"  est. runtime @ 2.61 s/game single-process: {len(df) * 2.61 / 60:.0f} min")

    # ---- sizing arithmetic, reported per the plan --------------------------
    print("\n" + "=" * 72)
    print("SIZING ARITHMETIC")
    print("=" * 72)
    print("recon_rate_TRUE_0p5 is scored over PLAYER-GAMES (~21 played/game).")
    print("95% CI half-width at p=0.998, h = 1.96*sqrt(p(1-p)/N):\n")
    for ngames in (20, 150, 480, 600, len(df)):
        N = ngames * 21
        h = 1.96 * np.sqrt(0.998 * 0.002 / N)
        print(f"  {ngames:4d} games = {N:6d} player-games -> +/- {h:.5f}")
    print("\n  => 150 games/season resolves 0.995 vs 0.998 comfortably.")

    print("\nquarantine_rate is scored over GAMES, and is the BINDING constraint")
    print("on sample size. With zero observed quarantines, the 95% upper bound")
    print("is the rule of three, 3/n:\n")
    for ngames in (150, 300, 600, len(df)):
        print(f"  {ngames:4d} games, 0 quarantines -> 95% upper bound {3 / ngames:.4f}")
    print("\n  => a 150-game season CANNOT resolve a 0.005 quarantine bar; its")
    print("     best bound is 0.02. Pooled across the 4 frontier seasons (600")
    print("     games) it CAN bound 0.005. This asymmetry is load-bearing for")
    print("     the open threshold question and is reported, not smoothed over.")

    out = Path(
        r"C:\Users\bobby\AppData\Local\Temp\claude"
        r"\C--Users-bobby-playground-wolves-front-office"
        r"\ab0e38ad-9447-4c97-ab02-9edacecd90a8\scratchpad\spike_sample.json"
    )
    out.write_text(json.dumps({
        "rng_seed": RNG_SEED,
        "n_games": len(df),
        "games": df.to_dict(orient="records"),
    }, indent=1))
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()

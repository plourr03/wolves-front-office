#!/usr/bin/env python3
"""Item 5: injuries_2026_27.csv, hand-curated league-wide, per R7.

R7: a player is "long-term out" if a sourced report puts expected absence at 20 or
more games. Regular-season availability 0; playoff availability per the sourced
return date. DiVincenzo is out for the 2026-27 regular season in the primary
scenario, with a playoff return at 80% of prior value as the sensitivity.

TWO AVAILABILITY COLUMNS, deliberately:
  rs_avail / po_avail          -- R7 as written. Binary for the regular season.
  rs_avail_frac / po_avail_frac -- the researcher's derivation from the sourced
                                   return language, e.g. a February return is ~0.35
                                   of the regular season.
The R7 columns are primary and drive the sim. The fractional columns exist because
R7's binary rule is conservative for a player who is sourced to return mid-season
(Jimmy Butler at a projected 0.5 becomes 0.0 under R7), and the difference should be
measurable rather than buried. See decisions.md D8.

NOTE ON PROVENANCE: no source publishes an availability fraction. The injury, the
date and the return language are sourced; the fractions are derived. Every row keeps
its URL.

    python kuminga/scripts/build_injuries.py
"""
from __future__ import annotations

import json
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO)

from kuminga.lib import runlog  # noqa: E402

RAW = os.path.join(REPO, "kuminga", "data", "_research_raw.json")
OUT = os.path.join(REPO, "kuminga", "data", "injuries_2026_27.csv")

# R7's threshold is 20 or more games missed out of an 82-game regular season, so the
# long-term cut is availability at or below 62/82. Setting it looser than this wrongly
# sweeps in players sourced to return in November (Gueye at 0.80 is ~16 games missed,
# which is NOT long-term) and zeroes a player who will be available for four fifths of
# the season.
REGULAR_SEASON_GAMES = 82
LONG_TERM_GAMES_MISSED = 20
LONG_TERM_FRAC_CEILING = (REGULAR_SEASON_GAMES - LONG_TERM_GAMES_MISSED) / REGULAR_SEASON_GAMES

# R7 explicitly overrides the researcher's derivation for DiVincenzo.
R7_OVERRIDES = {
    "Donte DiVincenzo": {
        "rs_avail": 0.0, "po_avail": 0.0,
        "sens_po_avail": 0.8,
        "note": "R7 primary: out for the 2026-27 regular season. Sensitivity: playoff "
                "return at 80% of prior value. The 'after the 2027 All-Star break' "
                "timeline is a media projection, not a team statement.",
    },
}


def main():
    with runlog.run("build_injuries", inputs={"raw": RAW, "ruling": "R7"}) as r:
        raw = json.load(open(RAW, encoding="utf-8"))["injuries"]
        rows = []
        for i in raw["injuries"]:
            name = i["player"]
            frac_rs = float(i.get("rs_availability", 0.0))
            frac_po = float(i.get("po_availability", 0.0))
            long_term = frac_rs <= LONG_TERM_FRAC_CEILING

            ov = R7_OVERRIDES.get(name)
            if ov:
                rs, po, sens = ov["rs_avail"], ov["po_avail"], ov["sens_po_avail"]
                note = ov["note"]
            elif long_term:
                # R7 as written: long-term out -> regular season 0, playoffs per the
                # sourced return date (the researcher's po derivation is that read).
                rs, po, sens = 0.0, frac_po, None
                note = "R7: classified long-term out (20+ games)."
            else:
                rs, po, sens = frac_rs, frac_po, None
                note = "below the R7 long-term threshold; carried at derived availability."

            rows.append(dict(
                player=name, team=i["team"], injury=i["injury"],
                injury_date=i.get("injury_date", ""),
                expected_return=i.get("expected_return", ""),
                expected_games_missed=i.get("expected_games_missed", ""),
                long_term_out=long_term,
                rs_avail=rs, po_avail=po,
                sens_po_avail=sens if sens is not None else po,
                rs_avail_frac=frac_rs, po_avail_frac=frac_po,
                source_tier=i.get("tier", ""),
                source_url=i.get("source_url", ""),
                source_url_2=i.get("source_url_2", ""),
                conflict=i.get("conflict", ""),
                note=note,
            ))

        df = pd.DataFrame(rows).sort_values(["rs_avail", "player"])
        df.to_csv(OUT, index=False)

        r.note(f"{len(df)} injury rows, {int(df.long_term_out.sum())} classified long-term out")
        r.note(f"teams affected: {df.team.nunique()}")
        for _, x in df.iterrows():
            r.note(f"  {x.player} ({x.team}): R7 rs={x.rs_avail} po={x.po_avail} "
                   f"| derived rs={x.rs_avail_frac} po={x.po_avail_frac}")
        r.note("R7-vs-derived regular-season availability gap, summed across players: "
               f"{df.rs_avail_frac.sum() - df.rs_avail.sum():.2f} player-seasons")
        r.output(OUT, rows=len(df))

    print()
    print(df[["player", "team", "long_term_out", "rs_avail", "po_avail",
              "rs_avail_frac", "expected_return"]].to_string(index=False))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Item 6: enumerate the 2026-offseason draft-asset movement.

The league transaction feed records the entire seven-asset package as ONE leg reading
"Charlotte Hornets received draft consideration from Minnesota Timberwolves", with a
NULL player_id. No pick detail exists anywhere in the warehouse. This writes the
enumerated ledger from externally verified reporting and applies the delta to
offseason/data/nba_draft_picks_future.csv, which was last verified 2026-06-06 and
therefore predates the trade entirely.

A full league-wide re-scrape of the pick ledger was NOT possible: Spotrac and RealGM
both returned HTTP 403 to automated retrieval. So this is a targeted delta for the
Minnesota assets, not a refresh of all 609 rows. Logged in gaps_remaining.md.

    python kuminga/scripts/build_pick_ledger.py
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
OUT = os.path.join(REPO, "kuminga", "data", "traded_picks_2026_offseason.csv")
LEDGER = os.path.join(REPO, "offseason", "data", "nba_draft_picks_future.csv")
LEDGER_OUT = os.path.join(REPO, "kuminga", "data", "nba_draft_picks_future_2026_08_26.csv")

HR = "https://www.hoopsrumors.com/2026/07/wolves-hornets-nets-bulls-finalize-four-team-trade.html"
SI = ("https://www.si.com/nba/hornets/onsi/full-details-of-the-hornets-four-team-trade-"
      "every-pick-and-player-charlotte-received")


def main():
    with runlog.run("build_pick_ledger", inputs={"raw": RAW, "ledger": LEDGER}) as r:
        raw = json.load(open(RAW, encoding="utf-8"))["picks"]

        rows = []
        for p in raw["picks"]:
            rows.append(dict(
                trade="2026-07-10 four-team (MIN/CHA/BRK/CHI)",
                year=p.get("year"), rnd=p.get("round"),
                from_team=p.get("from_team"), to_team=p.get("to_team"),
                origin_team=p.get("origin_team", ""),
                asset_type=p.get("asset_type"),
                protection=p.get("protection", ""),
                condition=p.get("condition", ""),
                verified=p.get("verified", False),
                source_url=p.get("source_url", HR),
                source_url_2=SI,
            ))
        df = pd.DataFrame(rows).sort_values(["year", "rnd", "to_team"])
        df.to_csv(OUT, index=False)
        r.note(f"{len(df)} draft assets enumerated, {int(df.verified.sum())} verified")
        for _, x in df.iterrows():
            r.note(f"  {x.year} R{x.rnd} {x.from_team}->{x.to_team} [{x.asset_type}] {x.protection}")

        # --- apply the delta to the league-wide ledger ---------------------------
        led = pd.read_csv(LEDGER)
        r.note(f"existing ledger: {len(led)} rows, last_verified "
               f"{led.last_verified.mode().iloc[0] if 'last_verified' in led else 'n/a'}")

        # Mark every MIN-involved row as superseded: the June 6 ledger predates the
        # trade, so any MIN first or second in 2028-2033 may now be encumbered.
        if "controlling_team" in led.columns:
            touched = led[(led.controlling_team == "MIN") | (led.pick_origin == "MIN")
                          | led.condition.fillna("").str.contains("MIN", na=False)]
            led["stale_post_2026_trade"] = led.index.isin(touched.index)
            r.note(f"flagged {len(touched)} ledger rows as stale (MIN-involved, pre-trade)")

        new_rows = []
        for _, x in df.iterrows():
            if x.to_team in ("CHA", "BRK", "BKN") and x.asset_type in ("pick", "swap_right"):
                new_rows.append(dict(
                    controlling_team=x.to_team, round=x.rnd, year=x.year,
                    pick_origin=x.from_team,
                    slot_span=30,
                    is_unprotected_or_unknown=(str(x.protection).lower().startswith("unprot")
                                               or str(x.protection).strip() in ("", "none")),
                    condition=f"{x.asset_type}: {x.protection}".strip(": "),
                    source="2026-07-10 four-team trade (Hoops Rumors + SI)",
                    last_verified="2026-08-26",
                    stale_post_2026_trade=False,
                ))
        if new_rows:
            led = pd.concat([led, pd.DataFrame(new_rows)], ignore_index=True)
        led.to_csv(LEDGER_OUT, index=False)
        r.note(f"wrote updated ledger: {len(led)} rows -> {LEDGER_OUT}")
        r.note("NOT a full refresh: Spotrac and RealGM both 403 automated retrieval. "
               "This is a targeted MIN delta only.")
        r.output(OUT, rows=len(df))
        r.output(LEDGER_OUT, rows=len(led))

    print()
    print(df[["year", "rnd", "from_team", "to_team", "asset_type", "protection"]].to_string(index=False))


if __name__ == "__main__":
    main()

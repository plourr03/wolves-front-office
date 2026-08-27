#!/usr/bin/env python3
"""Item 2 + item 6: the transaction supplement.

The warehouse's nba_transactions feed is live and league-wide but it under-specifies
in three ways that matter here:
  1. no dollars on any of its 9,849 rows,
  2. draft picks appear only as the literal string "draft consideration" with a NULL
     player_id, so a seven-pick package is one undifferentiated leg,
  3. no exception_used tag, so you cannot tell an MLE signing from a minimum.

Rather than fork a parallel ledger that would immediately drift from the live feed,
this writes a CHILD table keyed on the feed's own `group_sort`. Rows whose event is
not in the feed at all (because it is newer than the feed's 2026-08-23 cutoff) get a
synthetic group_sort prefixed "SUPP_" and are tagged status="reported_pending_official".

The production warehouse is read-only for this project. This lands in kuminga/data/.

    python kuminga/scripts/build_transaction_supplement.py
"""
from __future__ import annotations

import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO)

from kuminga.lib import runlog  # noqa: E402

OUT = os.path.join(REPO, "kuminga", "data", "transaction_supplement.csv")

# Source precedence per R8: official NBA/team release > Spotrac/B-Ref/RealGM > reporters.
# Every row carries at least two independent URLs where two exist.

RECORDS = [
    # ---------------------------------------------------------------- item 2
    # The Kuminga signing. Reported 2026-08-26 (today) by Anthony Slater, ESPN,
    # with terms from agent Aaron Turner via Shams Charania. It postdates the
    # nba_transactions feed cutoff (2026-08-23), which is exactly why Phase 0 found
    # it in no store. NOT yet official: tagged reported_pending_official per R4.
    dict(
        group_sort="SUPP_KUMINGA_SIGN_2026", leg=1, transaction_date="2026-08-26",
        transaction_type="Signing", team_abbr="MIN", direction="in",
        player_name="Jonathan Kuminga", nba_player_id=1630228, asset_type="player",
        season="2026-27", salary=6064000, option_type="guaranteed", season_order=1,
        total_value=12431200, years=2, exception_used="taxpayer_mle",
        status="reported_pending_official",
        source_url_1="https://www.espn.com/nba/story/_/id/49736014/jonathan-kuminga-reaches-2-year-deal-minnesota-timberwolves",
        source_url_2="https://www.si.com/nba/timberwolves/onsi/the-curious-case-jonathan-kuminga-landing-timberwolves-01kz3yn6k4rt",
        source_tier="reporter",
        note="2yr/$12.4M reported. Y1 set to the verified 2026-27 TPMLE exactly ($6,064,000); "
             "Y2 = 5% raise. $12,431,200 total is within $31k of the reported $12.4M. The TPMLE "
             "is capped at two years, consistent with the reported length. Chose MIN over a "
             "richer 3yr Lakers sign-and-trade offer (~$12M+/yr).",
    ),
    dict(
        group_sort="SUPP_KUMINGA_SIGN_2026", leg=2, transaction_date="2026-08-26",
        transaction_type="Signing", team_abbr="MIN", direction="in",
        player_name="Jonathan Kuminga", nba_player_id=1630228, asset_type="player",
        season="2027-28", salary=6367200, option_type="player_option", season_order=2,
        total_value=12431200, years=2, exception_used="taxpayer_mle",
        status="reported_pending_official",
        source_url_1="https://www.espn.com/nba/story/_/id/49736014/jonathan-kuminga-reaches-2-year-deal-minnesota-timberwolves",
        source_url_2="https://www.si.com/nba/timberwolves/onsi/the-curious-case-jonathan-kuminga-landing-timberwolves-01kz3yn6k4rt",
        source_tier="reporter",
        note="Year 2 player option. If declined, MIN holds Non-Bird only (one season of "
             "service), capping a re-sign start at 120% of $6,367,200 = $7,640,640. See item 13.",
    ),
    # The Hawks' option decision. This is why he was a free agent at all.
    dict(
        group_sort="SUPP_KUMINGA_OPTION_2026", leg=1, transaction_date="2026-06-29",
        transaction_type="OptionDeclined", team_abbr="ATL", direction="out",
        player_name="Jonathan Kuminga", nba_player_id=1630228, asset_type="player",
        season="2026-27", salary=24300000, option_type="team_option", season_order=1,
        total_value=24300000, years=1, exception_used="",
        status="reported",
        source_url_1="https://www.espn.com/nba/story/_/id/49219048/sources-jonathan-kuminga-free-agent-hawks-decline-option",
        source_url_2="https://www.thescore.com/nba/news/3554780/report-hawks-declining-kumingas-24-3-m-team-option",
        source_tier="reporter",
        note="Declined at the 5pm ET deadline 2026-06-29, making him an unrestricted free agent. "
             "Reported as strategic: declining preserved his Bird rights while freeing the full "
             "non-taxpayer MLE. RECONCILIATION FLAG: nba_player_contracts, scraped 2026-08-26, "
             "still carries this option as live on ATL. The contracts source has not caught the "
             "decline. Treat the ATL $24.3M row as stale, not as evidence he is on Atlanta.",
    ),
    # How he got to Atlanta, for the role-conditional projection in item 12.
    dict(
        group_sort="SUPP_KUMINGA_TO_ATL_2026", leg=1, transaction_date="2026-02-24",
        transaction_type="Trade", team_abbr="ATL", direction="in",
        player_name="Jonathan Kuminga", nba_player_id=1630228, asset_type="player",
        season="2025-26", salary=0, option_type="", season_order=0,
        total_value=0, years=0, exception_used="",
        status="official",
        source_url_1="https://www.espn.com/nba/story/_/id/49219048/sources-jonathan-kuminga-free-agent-hawks-decline-option",
        source_url_2="",
        source_tier="reporter",
        note="Kuminga and Buddy Hield to ATL for Kristaps Porzingis, February 2026. Warehouse "
             "corroborates: his first ATL box score is 2026-02-24, last GSW 2026-01-22. "
             "The GSW/ATL split is the basis of the role-conditional read.",
    ),
    # ----------------------------------------------- rejected offers (A1)
    # The real market for Kuminga this summer. These are the competing bids he turned
    # down, which are the only observed prices for him other than the one he took, and
    # therefore the sharpest available check on the model's four-view market estimate.
    dict(
        group_sort="SUPP_KUMINGA_REJECTED_LAL", leg=1, transaction_date="2026-08-26",
        transaction_type="RejectedOffer", team_abbr="LAL", direction="offered",
        player_name="Jonathan Kuminga", nba_player_id=1630228, asset_type="player",
        season="2026-27", salary=12000000, option_type="", season_order=1,
        total_value=36000000, years=3, exception_used="sign_and_trade",
        status="reported_rejected",
        source_url_1="https://www.espn.com/nba/story/_/id/49736014/jonathan-kuminga-reaches-2-year-deal-minnesota-timberwolves",
        source_url_2="https://heavy.com/sports/nba/los-angeles-lakers/lakers-jonathan-kuminga-picked-minnesota/",
        source_tier="reporter",
        note="Anthony Slater (ESPN): a similar starting role and '$12 million-plus "
             "annually over three years' via sign-and-trade, roughly $36M total. "
             "REJECTED. This is the highest observed bid and it is roughly DOUBLE the "
             "annual value of the deal he took.",
    ),
    dict(
        group_sort="SUPP_KUMINGA_REJECTED_CHI", leg=1, transaction_date="2026-08-26",
        transaction_type="RejectedOffer", team_abbr="CHI", direction="offered",
        player_name="Jonathan Kuminga", nba_player_id=1630228, asset_type="player",
        season="2026-27", salary=0, option_type="", season_order=1,
        total_value=0, years=0, exception_used="",
        status="reported_rejected_terms_undisclosed",
        source_url_1="https://www.si.com/nba/bulls/onsi/bulls-reportedly-made-offer-to-jonathan-kuminga-but-struck-out-26",
        source_url_2="",
        source_tier="reporter",
        note="Chicago made an offer; NO TERMS were reported. Recorded with zero dollars "
             "so it is never summed, and flagged so nobody infers a number from silence.",
    ),
    dict(
        group_sort="SUPP_KUMINGA_REJECTED_POR", leg=1, transaction_date="2026-08-26",
        transaction_type="RejectedOffer", team_abbr="POR", direction="offered",
        player_name="Jonathan Kuminga", nba_player_id=1630228, asset_type="player",
        season="2026-27", salary=0, option_type="", season_order=1,
        total_value=0, years=0, exception_used="",
        status="reported_pursued_terms_undisclosed",
        source_url_1="https://heavy.com/sports/nba/minnesota-timberwolves/timberwolves-land-jonathan-kuminga/",
        source_url_2="",
        source_tier="reporter",
        note="Portland pursued him; no terms reported.",
    ),
    # The stated reason for the shorter deal, which is the qualitative counterpart to
    # the option model in item 14.
    dict(
        group_sort="SUPP_KUMINGA_STATED_INTENT", leg=1, transaction_date="2026-08-26",
        transaction_type="StatedIntent", team_abbr="MIN", direction="context",
        player_name="Jonathan Kuminga", nba_player_id=1630228, asset_type="note",
        season="2026-27", salary=0, option_type="player_option", season_order=0,
        total_value=0, years=2, exception_used="taxpayer_mle",
        status="reported",
        source_url_1="https://www.espn.com/nba/story/_/id/49736014/jonathan-kuminga-reaches-2-year-deal-minnesota-timberwolves",
        source_url_2="https://heavy.com/sports/nba/los-angeles-lakers/lakers-jonathan-kuminga-picked-minnesota/",
        source_tier="reporter",
        note="Anthony Slater (ESPN): he chose Minnesota on a 'shorter-term, prove-it "
             "deal to give him the ability to have more control of his future and "
             "possibly jump back in free agency next summer.' He turned down roughly "
             "twice the annual money from the Lakers to do it. The stated intent is to "
             "reach free agency again in 2027, which is the same event the option model "
             "prices at a 0.50 to 0.80 probability.",
    ),
    # ---------------------------------------------------------------- item 4/16
    # The 14th-man placeholder per R4. MIN sits at 13 standard contracts after Green
    # leaves; the league minimum is 14. This is a modeling placeholder, not a signing.
    dict(
        group_sort="SUPP_MIN_14TH_MAN", leg=1, transaction_date="2026-08-26",
        transaction_type="PlaceholderSigning", team_abbr="MIN", direction="in",
        player_name="[14th man placeholder]", nba_player_id=-1, asset_type="roster_charge",
        season="2026-27", salary=1358000, option_type="guaranteed", season_order=1,
        total_value=1358000, years=1, exception_used="minimum",
        status="placeholder",
        source_url_1="", source_url_2="", source_tier="model_assumption",
        note="R4 placeholder at the 2026-27 rookie minimum ($1,358,000 from the verified "
             "min-salary scale, 0 years of service). Valued at replacement level. MIN has 13 "
             "standard contracts plus one two-way (Enrique Freeman); the league floor is 14 "
             "standard, so a 14th body is mandatory, not optional.",
    ),
]


def main():
    with runlog.run("build_transaction_supplement",
                    inputs={"source": "web-verified, R8 precedence", "records": len(RECORDS)}) as r:
        df = pd.DataFrame(RECORDS)
        cols = ["group_sort", "leg", "transaction_date", "transaction_type", "team_abbr",
                "direction", "player_name", "nba_player_id", "asset_type", "season",
                "season_order", "salary", "option_type", "total_value", "years",
                "exception_used", "status", "source_tier", "source_url_1", "source_url_2", "note"]
        df = df[cols].sort_values(["transaction_date", "group_sort", "leg"])
        df.to_csv(OUT, index=False)
        r.note(f"{len(df)} supplement rows, {df.group_sort.nunique()} events")
        for st, n in df.status.value_counts().items():
            r.note(f"  status={st}: {n}")
        r.output(OUT, rows=len(df))
    print(df[["transaction_date", "group_sort", "team_abbr", "player_name",
              "season", "salary", "option_type", "status"]].to_string(index=False))


if __name__ == "__main__":
    main()

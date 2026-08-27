#!/usr/bin/env python3
"""Item 3: roster_snapshot_2026_27, all 30 teams.

Built from the frozen contract book plus the transaction feed. The warehouse's own
roster table is unusable for this: it is current-DATED (roster_date 2026-08-26) but
2025-26 in CONTENT, so it still has Randle and Reid on Minnesota and Ball on Charlotte.

Four things this has to get right:

1. THE DUPLICATE PROBLEM. Four players appear under TWO teams for 2026-27 at the SAME
   salary: Beal (LAC + PHO), Lillard (MIL + POR), Caldwell-Pope (MEM + PHI), Prosper
   (DAL + MEM). Each was waived by the first team and signed by the second. The
   `salary` column is copied to both rows and is wrong for at least one of them; the
   `remaining_guaranteed_total` column is per-team and IS correct, which is the tell.
   Resolution: the team of the player's most recent Signing/Trade transaction is the
   ACTIVE team; the other carries dead money. Amounts come from DUP_RESOLUTION below,
   which is verified externally and falls back to stretch math.

2. KUMINGA AND THE 14TH MAN. Both come from the transaction supplement (item 2), not
   from the contract book, because the signing postdates the feed.

3. THE STALE ATL ROW. Kuminga's $24.3M Atlanta team option was declined 2026-06-29 but
   the contract scrape still carries it. It is dropped.

4. TWO-WAYS. Not in the contract book at all. Recovered from transaction descriptions.

    python kuminga/scripts/build_roster_snapshot.py
"""
from __future__ import annotations

import json
import os
import sys
from datetime import date

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO)

from kuminga.lib import kfreeze, runlog  # noqa: E402

AS_OF = "2026-08-26"
SEASON = "2026-27"
AGE_ON = date(2026, 10, 1)          # ages stated as of opening night
OUT = os.path.join(REPO, "kuminga", "data", "roster_snapshot_2026_27.csv")
DISCREP = os.path.join(REPO, "kuminga", "data", "roster_snapshot_discrepancies.csv")
CONST = os.path.join(REPO, "offseason", "data", "league_year_constants.json")
SUPP = os.path.join(REPO, "kuminga", "data", "transaction_supplement.csv")
OVERRIDE = os.path.join(REPO, "kuminga", "data", "dup_resolution_verified.json")

# Tricode normalisation: the contract source uses B-Ref codes, the warehouse uses NBA's.
TRICODE_FIX = {"PHO": "PHX", "BRK": "BKN", "CHO": "CHA"}

# Duplicate resolution. active_team = where he actually plays; dead_team carries the
# waived salary. Amounts are overridden by dup_resolution_verified.json when that file
# exists (written from the Spotrac spot-check); otherwise the fallback below applies
# stretch math to the dead team's remaining guarantee and treats the active team's
# remaining guarantee as the real deal.
DUP_RESOLUTION = {
    "Bradley Beal":             {"active": "LAC", "dead": "PHX", "waived_on": "2025-07-16", "stretch_years": 5},
    "Damian Lillard":           {"active": "POR", "dead": "MIL", "waived_on": "2025-07-06", "stretch_years": 5},
    "Kentavious Caldwell-Pope": {"active": "PHI", "dead": "MEM", "waived_on": "2026-07-25", "stretch_years": 3},
    "Olivier-Maxence Prosper":  {"active": "MEM", "dead": "DAL", "waived_on": "2025-08-29", "stretch_years": 3},
}


def norm(tc):
    return TRICODE_FIX.get(tc, tc)


def load_constants():
    with open(CONST, encoding="utf-8") as fh:
        return json.load(fh)["seasons"][SEASON]


def age_on(birthdate):
    if pd.isna(birthdate):
        return None
    b = pd.to_datetime(birthdate).date()
    return round((AGE_ON - b).days / 365.25, 1)


def two_way_players(tx: pd.DataFrame) -> pd.DataFrame:
    """Two-way contracts are absent from the contract book. Recover them from the feed:
    the most recent two-way signing/conversion per player since the season ended."""
    tw = tx[
        (tx.transaction_date >= pd.Timestamp("2026-06-01"))
        & (tx.transaction_description.str.contains("Two-Way", case=False, na=False))
    ].copy()
    tw = tw.sort_values("transaction_date").groupby("player_slug", as_index=False).last()
    # A later standard signing or a waiver supersedes a two-way.
    later = tx[(tx.transaction_date >= pd.Timestamp("2026-06-01"))].copy()
    out = []
    for _, r in tw.iterrows():
        after = later[(later.player_slug == r.player_slug)
                      & (later.transaction_date > r.transaction_date)]
        superseded = after.transaction_description.str.contains(
            "waived|to a Contract", case=False, na=False).any()
        if not superseded:
            out.append(r)
    return pd.DataFrame(out)


def triggering_events(tx: pd.DataFrame) -> dict:
    """Most recent 2026-offseason transaction per player slug -> (date, type, description)."""
    off = tx[tx.transaction_date >= pd.Timestamp("2026-06-01")].copy()
    off = off.sort_values(["transaction_date", "additional_sort"])
    ev = {}
    for _, r in off.iterrows():
        if pd.isna(r.player_slug):
            continue
        ev[r.player_slug] = (str(r.transaction_date.date()), r.transaction_type,
                             r.transaction_description)
    return ev


def slugify(name: str) -> str:
    import re
    s = name.lower().replace(".", "").replace("'", "")
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s


def main():
    with runlog.run("build_roster_snapshot",
                    inputs={"snapshot": kfreeze.current_snapshot_id(), "as_of": AS_OF}) as r:
        const = load_constants()
        contracts, sid = kfreeze.load("contracts")
        tx, _ = kfreeze.load("transactions", sid)
        bio, _ = kfreeze.load("player_bio", sid)
        tx["transaction_date"] = pd.to_datetime(tx.transaction_date)

        discrepancies = []

        cur = contracts[contracts.season == SEASON].copy()
        cur["team_abbr"] = cur.team_abbr.map(norm)
        r.note(f"contract book: {len(cur)} rows for {SEASON}, {cur.team_abbr.nunique()} teams")

        # --- 3. drop the stale Kuminga ATL option row -----------------------------
        stale = cur[(cur.player_name == "Jonathan Kuminga") & (cur.team_abbr == "ATL")]
        if len(stale):
            cur = cur.drop(stale.index)
            discrepancies.append(dict(
                kind="stale_contract_row", team="ATL", player="Jonathan Kuminga",
                detail=f"${int(stale.salary.iloc[0]):,} team option dropped: declined 2026-06-29 "
                       "(ESPN), but the contract scrape still carries it as live.",
                resolution="dropped"))
            r.note("dropped stale Kuminga ATL option row")

        # --- 1. duplicate / dead-money resolution ---------------------------------
        verified = {}
        if os.path.exists(OVERRIDE):
            with open(OVERRIDE, encoding="utf-8") as fh:
                verified = json.load(fh)
            r.note(f"loaded verified duplicate resolution for {len(verified)} players")

        dup_names = cur.player_name.value_counts()
        dup_names = dup_names[dup_names > 1].index.tolist()
        r.note(f"duplicated players in {SEASON}: {dup_names}")

        dead_rows = []
        for name in dup_names:
            rows = cur[cur.player_name == name]
            spec = DUP_RESOLUTION.get(name)
            if spec is None:
                discrepancies.append(dict(kind="unresolved_duplicate", team="", player=name,
                                          detail=f"appears on {list(rows.team_abbr)} with no resolution rule",
                                          resolution="LEFT AS IS - REVIEW"))
                continue
            active, dead = spec["active"], spec["dead"]
            v = verified.get(name, {})

            # Active team keeps one row, at the verified salary if we have it, else at
            # its own remaining-guarantee spread over the seasons it appears in.
            arow = rows[rows.team_abbr == active]
            drow = rows[rows.team_abbr == dead]
            if arow.empty or drow.empty:
                discrepancies.append(dict(kind="duplicate_shape", team="", player=name,
                                          detail=f"expected {active}+{dead}, saw {list(rows.team_abbr)}",
                                          resolution="LEFT AS IS - REVIEW"))
                continue

            if "active_salary_2026_27" in v:
                act_sal = float(v["active_salary_2026_27"])
                act_src = "verified"
            else:
                n_seasons = int((contracts[(contracts.player_name == name)
                                           & (contracts.team_abbr.map(norm) == active)]).shape[0])
                act_sal = float(arow.remaining_guaranteed_total.iloc[0]) / max(n_seasons, 1)
                act_src = "fallback: remaining_guarantee / n_seasons"

            if "dead_money_2026_27" in v:
                dead_sal = float(v["dead_money_2026_27"])
                dead_src = "verified"
            else:
                dead_sal = float(drow.remaining_guaranteed_total.iloc[0]) / spec["stretch_years"]
                dead_src = f"fallback: stretch over {spec['stretch_years']}y"

            cur.loc[arow.index, "salary"] = act_sal
            cur.loc[arow.index, "_salary_source"] = act_src
            cur = cur.drop(drow.index)
            dead_rows.append(dict(team_abbr=dead, player_name=name,
                                  salary=dead_sal, source=dead_src,
                                  waived_on=spec["waived_on"]))
            discrepancies.append(dict(
                kind="dead_money_split", team=f"{active}/{dead}", player=name,
                detail=f"contract book listed ${int(rows.salary.iloc[0]):,} on BOTH. "
                       f"Resolved: {active} active at ${act_sal:,.0f} ({act_src}); "
                       f"{dead} dead money ${dead_sal:,.0f} ({dead_src}).",
                resolution="split"))
            r.note(f"  {name}: {active} ${act_sal:,.0f} active | {dead} ${dead_sal:,.0f} dead")

        # --- assemble standard contracts -----------------------------------------
        cur["slot_type"] = "standard"
        roster = cur.rename(columns={"salary": "salary_2026_27"})[
            ["team_abbr", "player_name", "br_player_id", "salary_2026_27", "option_type",
             "remaining_guaranteed_total", "slot_type"]].copy()
        roster["salary_2026_27"] = roster.salary_2026_27.astype(float)
        roster["status"] = "official"
        roster["source"] = "nba_player_contracts (B-Ref), scraped 2026-08-26"
        # The contract book's index is non-contiguous; appended rows MUST NOT be
        # addressed by .loc[len(df)] or they overwrite real players.
        roster = roster.reset_index(drop=True)
        extra: list[dict] = []

        # dead money rows
        for d in dead_rows:
            extra.append(dict(
                team_abbr=d["team_abbr"], player_name=f"[dead] {d['player_name']}",
                br_player_id=None, salary_2026_27=float(d["salary"]), option_type="dead_money",
                remaining_guaranteed_total=None, slot_type="dead_money",
                status="derived", source=f"waived {d['waived_on']}; {d['source']}"))

        # --- 2. supplement rows (Kuminga, 14th man) -------------------------------
        if os.path.exists(SUPP):
            sup = pd.read_csv(SUPP)
            sup = sup[(sup.season == SEASON) & (sup.direction == "in")
                      & (sup.asset_type.isin(["player", "roster_charge"]))]
            for _, s in sup.iterrows():
                extra.append(dict(
                    team_abbr=norm(s.team_abbr), player_name=s.player_name,
                    br_player_id=None, salary_2026_27=float(s.salary),
                    option_type=s.option_type, remaining_guaranteed_total=None,
                    slot_type="standard" if s.asset_type == "player" else "placeholder",
                    status=s.status, source=f"transaction_supplement: {s.group_sort}"))
                r.note(f"  supplement: {s.player_name} -> {s.team_abbr} ${float(s.salary):,.0f} ({s.status})")

        # --- 4. two-ways ----------------------------------------------------------
        tw = two_way_players(tx)
        slug2team = {}
        for _, t in tw.iterrows():
            # team_slug -> tricode via the transactions table's team_id
            slug2team[t.player_slug] = t.team_id
        team_ids = tx[["team_id", "team_slug"]].drop_duplicates()
        # map team_id to tricode using the contract book's nba_team_id
        id2tri = (contracts[["nba_team_id", "nba_team_tricode"]].drop_duplicates()
                  .set_index("nba_team_id").nba_team_tricode.to_dict())
        n_tw = 0
        already = set(zip(roster.team_abbr, roster.player_name.map(slugify)))
        for _, t in tw.iterrows():
            tri = id2tri.get(t.team_id)
            if tri is None:
                continue
            tri = norm(tri)
            if (tri, t.player_slug) in already:
                continue          # already carries a standard contract
            extra.append(dict(
                team_abbr=tri, player_name=t.player_slug.replace("-", " ").title(),
                br_player_id=None, salary_2026_27=0.0, option_type="two_way",
                remaining_guaranteed_total=None, slot_type="two_way",
                status="official", source=f"nba_transactions {t.transaction_date.date()}"))
            n_tw += 1
        r.note(f"two-way contracts recovered: {n_tw}")

        if extra:
            roster = pd.concat([roster, pd.DataFrame(extra)], ignore_index=True)

        # --- enrich: age, position, triggering event ------------------------------
        bio2 = bio.copy()
        bio2["slug"] = bio2.player_name.map(slugify)
        bio_by_slug = bio2.drop_duplicates("slug").set_index("slug")
        roster["slug"] = roster.player_name.str.replace(r"^\[dead\] ", "", regex=True).map(slugify)
        roster["nba_player_id"] = roster.slug.map(bio_by_slug.player_id)
        roster["birthdate"] = roster.slug.map(bio_by_slug.birthdate)
        roster["age"] = roster.birthdate.map(age_on)
        roster["position"] = roster.slug.map(bio_by_slug.position)
        # Two-way names were reconstructed from a URL slug; prefer the canonical
        # bio spelling where the slug resolves to a real player.
        canon = roster.slug.map(bio_by_slug.player_name)
        fix = (roster.slot_type == "two_way") & canon.notna()
        roster.loc[fix, "player_name"] = canon[fix]

        ev = triggering_events(tx)
        roster["trigger_date"] = roster.slug.map(lambda s: ev.get(s, (None, None, None))[0])
        roster["trigger_type"] = roster.slug.map(lambda s: ev.get(s, (None, None, None))[1])
        roster["trigger_event"] = roster.slug.map(lambda s: ev.get(s, (None, None, None))[2])
        roster.loc[roster.slot_type == "placeholder", "trigger_event"] = "R4 modeling placeholder"
        roster.loc[roster.player_name == "Jonathan Kuminga", "trigger_event"] = \
            "Signed with MIN 2026-08-26 (taxpayer MLE, reported)"

        roster["as_of_date"] = AS_OF
        roster["season"] = SEASON

        # --- sanity: roster counts ------------------------------------------------
        counts = (roster[roster.slot_type.isin(["standard", "placeholder"])]
                  .groupby("team_abbr").size().rename("n_standard"))
        # In late August a team may legitimately carry up to 21 players and may sit
        # below 14; both limits (14 floor, 15 ceiling) bind at the regular-season start.
        # So these are informational, not errors. Only the extremes are worth a row.
        for team, n in counts.items():
            if n < 14:
                discrepancies.append(dict(kind="roster_below_season_floor", team=team, player="",
                                          detail=f"{n} standard contracts in August; must reach 14 "
                                                 "by opening night. Normal for the date.",
                                          resolution="informational"))
            if n > 21:
                discrepancies.append(dict(kind="roster_above_offseason_max", team=team, player="",
                                          detail=f"{n} standard contracts; offseason max is 21",
                                          resolution="flagged"))

        cols = ["as_of_date", "season", "team_abbr", "player_name", "nba_player_id",
                "br_player_id", "slot_type", "salary_2026_27", "option_type",
                "remaining_guaranteed_total", "age", "position",
                "trigger_date", "trigger_type", "trigger_event", "status", "source"]
        roster = roster[cols].sort_values(["team_abbr", "slot_type", "salary_2026_27"],
                                          ascending=[True, True, False])
        roster.to_csv(OUT, index=False)
        pd.DataFrame(discrepancies).to_csv(DISCREP, index=False)

        std = roster[roster.slot_type.isin(["standard", "placeholder"])]
        r.note(f"TOTAL: {len(roster)} rows | {std.team_abbr.nunique()} teams | "
               f"{len(std)} standard+placeholder | "
               f"{(roster.slot_type=='two_way').sum()} two-way | "
               f"{(roster.slot_type=='dead_money').sum()} dead-money")
        r.note(f"discrepancies logged: {len(discrepancies)}")
        r.output(OUT, rows=len(roster))
        r.output(DISCREP, rows=len(discrepancies))

    print()
    print(std.groupby("team_abbr").agg(n=("player_name", "size"),
                                       committed=("salary_2026_27", "sum")).to_string())


if __name__ == "__main__":
    main()

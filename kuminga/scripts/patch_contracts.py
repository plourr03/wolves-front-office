#!/usr/bin/env python3
"""Apply the transaction supplement to the verified contracts file (item 4 prerequisite).

`verified_contracts.py` rebuilds offseason/data/nba_contracts_2026_27_verified.csv from
the warehouse, which does not know about the Kuminga signing (reported 2026-08-26, after
the feed cutoff). `build_team_state.py` reads that file, so without this patch every
downstream apron number would be computed on a roster missing its newest player.

This adds the supplement's MIN rows and drops the stale Kuminga ATL option row, and it
is idempotent: re-running after another verified_contracts rebuild reapplies cleanly.

    python kuminga/scripts/patch_contracts.py
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

VERIFIED = os.path.join(REPO, "offseason", "data", "nba_contracts_2026_27_verified.csv")
SUPP = os.path.join(REPO, "kuminga", "data", "transaction_supplement.csv")
ROSTER_SNAP = os.path.join(REPO, "kuminga", "data", "roster_snapshot_2026_27.csv")
DUPV = os.path.join(REPO, "kuminga", "data", "dup_resolution_verified.json")

KUMINGA_ID = "1630228"
TF = {"PHO": "PHX", "BRK": "BKN", "CHO": "CHA"}


def nkey(name) -> str:
    """Fold a player name to a comparison key.

    The contract scrape is double-encoded for accented names (Jokic, Doncic, Lopez),
    so a raw lowercase compare misses them and would duplicate the player. Strip
    accents, punctuation and generational suffixes; keep the rest.
    """
    import unicodedata, re
    s = str(name)
    # Repair latin-1/utf-8 double encoding. A STRICT encode is the discriminator and
    # no marker list is needed: a genuinely mojibaked name is entirely code points
    # below U+0100 so it re-encodes cleanly, while a correctly-encoded name (Jokic
    # with the accent, U+0107) raises and is left alone. Using errors="ignore" here
    # instead silently TRUNCATES correct names, which is how Jokic and Doncic ended
    # up double-counted on Denver and the Lakers.
    try:
        s = s.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        pass
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower()
    # Drop generational suffixes as whole tokens. Done by splitting rather than by
    # regex so an "ii" inside a name is never eaten.
    drop = {"jr", "jr.", "sr", "sr.", "ii", "iii", "iv"}
    s = " ".join(tok for tok in s.split() if tok not in drop)
    s = re.sub(r"[^a-z0-9]+", "", s)
    return s


def out_team(series):
    """Contracts-file tricodes -> warehouse tricodes, for comparing against the snapshot."""
    return series.map(lambda t: TF.get(t, t))


def main():
    with runlog.run("patch_contracts", inputs={"verified": VERIFIED, "supplement": SUPP}) as r:
        df = pd.read_csv(VERIFIED, dtype=str).fillna("")
        r.note(f"read {len(df)} rows")

        # --- drop the stale ATL Kuminga option row --------------------------------
        before = len(df)
        stale = df[(df.nba_player_id == KUMINGA_ID) & (df.team_abbr == "ATL")]
        df = df.drop(stale.index)
        if len(stale):
            r.note(f"dropped stale Kuminga ATL row (option declined 2026-06-29)")

        # also drop any prior patch of the same rows so this is idempotent
        df = df[~((df.nba_player_id == KUMINGA_ID) & (df.team_abbr == "MIN"))]
        df = df[df.player != "[14th man placeholder]"]

        sup = pd.read_csv(SUPP)
        kum = sup[(sup.nba_player_id == 1630228) & (sup.group_sort == "SUPP_KUMINGA_SIGN_2026")]
        y1 = kum[kum.season == "2026-27"].iloc[0]
        y2 = kum[kum.season == "2027-28"].iloc[0]

        row = {c: "" for c in df.columns}
        row.update({
            "team_abbr": "MIN", "player": "Jonathan Kuminga", "nba_player_id": KUMINGA_ID,
            "position": "F",
            "salary_2026_27": str(int(y1.salary)), "salary_2027_28": str(int(y2.salary)),
            "salary_2028_29": "0", "salary_2029_30": "0",
            "years_left": "2",
            "option_2026_27": "guaranteed", "option_2027_28": "player_option",
            "option_2028_29": "", "option_2029_30": "",
            "trade_kicker_pct": "0", "no_trade_clause_flag": "0",
            "dead_money_teams": "", "dead_money_2026_27": "0",
        })
        add = [row]
        r.note(f"added Kuminga MIN 2026-27 ${int(y1.salary):,} / 2027-28 ${int(y2.salary):,} (PO)")

        # --- R4 14th-man placeholder ---------------------------------------------
        ph = sup[sup.group_sort == "SUPP_MIN_14TH_MAN"].iloc[0]
        prow = {c: "" for c in df.columns}
        prow.update({
            "team_abbr": "MIN", "player": "[14th man placeholder]", "nba_player_id": "",
            "position": "F", "salary_2026_27": str(int(ph.salary)),
            "salary_2027_28": "0", "salary_2028_29": "0", "salary_2029_30": "0",
            "years_left": "1", "option_2026_27": "guaranteed",
            "trade_kicker_pct": "0", "no_trade_clause_flag": "0",
            "dead_money_teams": "", "dead_money_2026_27": "0",
        })
        add.append(prow)
        r.note(f"added 14th-man placeholder ${int(ph.salary):,}")

        # --- restore the 2026 rookie class ---------------------------------------
        # verified_contracts.py resolves names against nba_player_bio, which has no
        # 2026 draft class, so all ~44 rookies fall out as "unresolved" and are
        # dropped. That silently removes ~$196M of real salary league-wide (CHI
        # -$15.6M, OKC -$15.4M) and would understate every team's apron position.
        # They are restored here with synthetic ids; the real nba_player_ids do not
        # exist yet anywhere, and team_state only needs the money.
        snap = pd.read_csv(ROSTER_SNAP)
        snap = snap[snap.slot_type.isin(["standard", "placeholder"])]
        # The verified file already emits WAREHOUSE tricodes (BKN/CHA/PHX), not the
        # contract table's B-Ref codes, so restored rows use the snapshot's codes
        # unchanged. Mapping them back would split a team into two groups.
        have = set(zip(out_team(df.team_abbr), df.player.map(nkey)))
        have |= {("MIN", nkey("Jonathan Kuminga")), ("MIN", nkey("[14th man placeholder]"))}
        n_restored, restored_salary = 0, 0.0
        for _, s in snap.iterrows():
            tb = s.team_abbr
            if (s.team_abbr, nkey(s.player_name)) in have:
                continue
            n_restored += 1
            restored_salary += float(s.salary_2026_27)
            rr = {c: "" for c in df.columns}
            rr.update({
                "team_abbr": tb, "player": s.player_name,
                "nba_player_id": f"R2026_{n_restored:03d}",
                "position": s.position if isinstance(s.position, str) else "",
                "salary_2026_27": str(int(s.salary_2026_27)),
                "salary_2027_28": "0", "salary_2028_29": "0", "salary_2029_30": "0",
                "years_left": "1",
                "option_2026_27": s.option_type if isinstance(s.option_type, str) else "guaranteed",
                "trade_kicker_pct": "0", "no_trade_clause_flag": "0",
                "dead_money_teams": "", "dead_money_2026_27": "0",
            })
            add.append(rr)
        r.note(f"restored {n_restored} unresolved players (mostly the 2026 draft class), "
               f"${restored_salary:,.0f} of 2026-27 salary")

        # --- verified dead-money correction ---------------------------------------
        # verified_contracts.py identifies the active/dead split correctly but fills
        # both the active salary and the dead-money amount with the CONTRACT TABLE's
        # copied figure, which is neither. The active player gets a flat $3,877,000
        # vet-min guess and the dead team gets the active player's salary. Externally
        # verified figures replace both. See kuminga/data/dup_resolution_verified.json.
        if os.path.exists(DUPV):
            with open(DUPV, encoding="utf-8") as fh:
                dv = json.load(fh)
            n_fix = 0
            for name, spec in dv.items():
                if name.startswith("_"):
                    continue
                m = df.player.map(nkey) == nkey(name)
                if not m.any():
                    r.note(f"  WARNING: {name} not found in verified contracts")
                    continue
                old_sal = df.loc[m, "salary_2026_27"].iloc[0]
                old_dead = df.loc[m, "dead_money_2026_27"].iloc[0]
                df.loc[m, "salary_2026_27"] = str(int(spec["active_salary_2026_27"]))
                df.loc[m, "dead_money_2026_27"] = str(int(spec["dead_money_2026_27"]))
                df.loc[m, "dead_money_teams"] = spec["dead_team"]
                n_fix += 1
                r.note(f"  {name}: active {spec['active_team']} ${old_sal} -> "
                       f"${spec['active_salary_2026_27']:,} | dead {spec['dead_team']} "
                       f"${old_dead} -> ${spec['dead_money_2026_27']:,}")
            r.note(f"applied {n_fix} verified dead-money corrections")

        out = pd.concat([df, pd.DataFrame(add)], ignore_index=True)
        out.to_csv(VERIFIED, index=False)
        r.note(f"wrote {len(out)} rows (was {before})")
        r.output(VERIFIED, rows=len(out))

        min_rows = out[out.team_abbr == "MIN"]
        tot = min_rows.salary_2026_27.replace("", "0").astype(float).sum()
        r.note(f"MIN: {len(min_rows)} contracts, 2026-27 total ${tot:,.0f}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Adapt roster v3 (gate-passing, Spotrac-sourced) into the schema the sim layer reads.

WHY AN ADAPTER RATHER THAN A REWRITE. `build_rotations.py` reads
`roster_snapshot_2026_27.csv`, the v1 table, which failed both G4 gates. v3 passes them
but carries a different schema and, critically, NO player ids: Spotrac's pages give
names and Spotrac's own player urls, and joining NBA data on names is the documented way
to lose players to diacritics. So v3 is mapped into v1's shape here, ids are resolved
against v1 and then the warehouse, and anything still unresolved is reported by name
rather than silently dropped.

THE ONE PLACE THE TWO LAYERS LEGITIMATELY DISAGREE: PENDING TRANSACTIONS.

  The CAP layer must EXCLUDE them. Under the CBA a reported-but-unofficial move is not
  team salary, Spotrac excludes them from team totals, and the gates therefore exclude
  them. That is settled and correct.

  The SIM layer must INCLUDE them. The question the sim asks is who plays for whom in
  2026-27, and a reported trade means the player plays for the new team. Excluding them
  would leave James Harden unrostered and Jonathan Kuminga, the entire subject of this
  project, off Minnesota.

  This is not a contradiction, it is two different questions, and conflating them is
  what made the earlier "cap layer vs sim layer" confusion look like a bug. It is
  recorded here so nobody re-derives it a third time.

DOUBLE-COUNTING, which pending rows cause and v1 got wrong. Spotrac lists a pending
player on the ACQUIRING team while his current team still lists him as active, so he
appears twice. The Clippers-Raptors deal (Ingram and Dick to LAC, Leonard to TOR) puts
three players on two rosters each. Rule applied: the pending row wins and the origin row
is dropped, because the pending row is where he will actually play.

    python kuminga/scripts/adapt_roster_v3.py
"""
from __future__ import annotations

import hashlib
import os
import re
import sys
import unicodedata

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "postmortem"))

from kuminga.lib import runlog  # noqa: E402

V3 = os.path.join(REPO, "kuminga", "data", "roster_snapshot_2026_27_v3.csv")
V1 = os.path.join(REPO, "kuminga", "data", "roster_snapshot_2026_27.csv")
OUT = os.path.join(REPO, "kuminga", "data", "roster_snapshot_2026_27_SIM.csv")
OUT_DIFF = os.path.join(REPO, "kuminga", "outputs", "sim_roster_diff_v1_v3.csv")

ACTIVE = ("standard", "non_guaranteed")


SUFFIXES = {"jr", "sr", "ii", "iii", "iv", "v"}


def _tokens(s):
    """Lowercase ascii name tokens with suffixes removed. Tokenising rather than
    running a regex over the whole string is deliberate. An earlier version stripped
    the suffix with a word-boundary regex, the escape did not survive being written to
    disk, and it silently became a bare alternation that would delete the letter v out
    of the middle of ordinary names. Splitting on non-letters cannot fail that way."""
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode()
    parts = [p for p in re.split(r"[^a-z]+", s.lower()) if p]
    keep = [p for p in parts if p not in SUFFIXES]
    return keep or parts


def nkey(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z]", "", s.lower())


def nkey2(s):
    """Suffix-stripped key. 'Jimmy Butler III' and 'Jimmy Butler' are one player, and
    treating them as two dropped a starter to replacement level."""
    return "".join(_tokens(s))


def nkey3(s):
    """First initial plus surname. Catches 'Nicolas Claxton' vs 'Nic Claxton' and the
    whole Cam/Cameron, Nic/Nicolas, Herb/Herbert family of short forms."""
    parts = _tokens(s)
    if len(parts) < 2:
        return None
    return parts[0][0] + parts[-1]


def main():
    with runlog.run("adapt_roster_v3",
                    inputs={"v3": os.path.relpath(V3, REPO),
                            "pending_policy": "included for the sim, dropped at origin"}
                    ) as r:
        v3 = pd.read_csv(V3)
        v1 = pd.read_csv(V1)

        keep = v3[v3.status.isin(ACTIVE + ("pending",))].copy()
        keep["k"] = keep.player_name.map(nkey)

        # ---- pending wins, origin row drops ---------------------------------
        pend = keep[keep.status == "pending"]
        moving = set(pend.k)
        before = len(keep)
        keep = keep[~((keep.k.isin(moving)) & (keep.status != "pending"))]
        dropped = before - len(keep)
        r.note("pending transactions: %d players, %d duplicate origin rows dropped"
               % (len(pend), dropped))
        for _, x in pend.iterrows():
            dup = "" if x.k not in set(v3[v3.status.isin(ACTIVE)].player_name.map(nkey)) \
                  else "  (origin row dropped)"
            r.note("    %s -> %s%s" % (x.player_name, x.team_abbr, dup))
        assert not keep.k.duplicated().any(), \
            "a player is still on two teams: %s" % list(
                keep[keep.k.duplicated(keep=False)].player_name.unique())

        # ---- id resolution --------------------------------------------------
        def first_name(s):
            parts = _tokens(s)
            return parts[0] if parts else ""

        def id_map(df, name_col, id_col):
            """Three keys, tried strictest first. Ambiguous keys are DROPPED rather
            than guessed: two different players sharing a first initial and surname
            must not silently collapse into one. For the third key the source's first
            name travels with the id, so resolve() can check it."""
            d = df.dropna(subset=[id_col]).copy()
            out = []
            for fn in (nkey, nkey2, nkey3):
                d["_k"] = d[name_col].map(fn)
                g = d.dropna(subset=["_k"]).groupby("_k")[id_col].nunique()
                ok = set(g[g == 1].index)
                sub = d[d._k.isin(ok)].drop_duplicates("_k").set_index("_k")
                out.append((sub[id_col], sub[name_col].map(first_name)))
            return out

        def resolve(keydf, maps):
            """THE FIRST-INITIAL KEY NEEDS CORROBORATION, because the uniqueness guard
            above only proves a key is unambiguous INSIDE THE SOURCE. It says nothing
            about whether the roster name is the same person. Two 2026 rookies absent
            from the source proved it: Baba Miller resolved to Brandon Miller ("bmiller")
            and Mikel Brown Jr. to Moses Brown ("mbrown"), so the Clippers were carrying
            Brandon Miller's impact and 30 minutes, and Brooklyn a 7-foot-2 centre in
            place of a guard. A third-key match is now accepted only when one first name
            is a prefix of the other: Nic/Nicolas, Cam/Cameron and Herb/Herbert pass;
            Baba/Brandon and Mikel/Moses do not."""
            got = pd.Series(index=keydf.index, dtype="float64")
            names = keydf["player_name"]
            for i, (fn, (m, src_first)) in enumerate(zip((nkey, nkey2, nkey3), maps)):
                miss = got.isna()
                if not miss.any():
                    break
                keys = names[miss].map(fn)
                cand = keys.map(m)
                if i == 2:
                    ours = names[miss].map(first_name)
                    theirs = keys.map(src_first)
                    ok = [(isinstance(a, str) and isinstance(b, str) and a and b
                           and (a.startswith(b) or b.startswith(a)))
                          for a, b in zip(ours, theirs)]
                    cand = cand.where(pd.Series(ok, index=cand.index))
                got.loc[miss] = cand
            return got

        v1 = v1.assign(k=v1.player_name.map(nkey))
        keep["nba_player_id"] = resolve(keep, id_map(v1, "player_name",
                                                     "nba_player_id"))

        # FOURTH KEY: exact 2026-27 salary. Names alone miss NICKNAMES, which no
        # normalisation catches. Spotrac lists "Nah'Shon Hyland" and v1 lists "Bones
        # Hyland"; all three name keys failed, he fell to replacement level, dropped out
        # of Minnesota's rotation entirely, and Cody Williams absorbed his 18 minutes at
        # -3.86. That single miss moved Minnesota's minutes-weighted net by roughly 0.4
        # points and roughly halved the modelled title probability. A cap hit to the
        # dollar is a strong identifier, so it is used where it is UNIQUE in both books.
        miss = keep.nba_player_id.isna()
        if miss.any():
            sal_v1 = v1.dropna(subset=["nba_player_id"])
            g = sal_v1.groupby("salary_2026_27").nba_player_id.nunique()
            uniq = set(g[g == 1].index)
            smap = (sal_v1[sal_v1.salary_2026_27.isin(uniq)]
                    .drop_duplicates("salary_2026_27")
                    .set_index("salary_2026_27").nba_player_id)
            # and the salary must be unique on OUR side too, or it identifies nothing
            own = keep.groupby("cap_hit_2026_27").size()
            ok_own = set(own[own == 1].index)
            cand = keep.loc[miss & keep.cap_hit_2026_27.isin(ok_own), "cap_hit_2026_27"]
            got = cand.map(smap)
            keep.loc[got.dropna().index, "nba_player_id"] = got.dropna()
            for i in got.dropna().index:
                r.note("    salary key resolved %s (%s) -> id %d"
                       % (keep.at[i, "player_name"], keep.at[i, "team_abbr"],
                          int(keep.at[i, "nba_player_id"])))
        n_v1 = int(keep.nba_player_id.notna().sum())

        try:
            from lib import db
            bio = db.query("""
                select distinct player_id, player_name
                from nba.nba_player_season_bio
                where season_year in ('2025-26','2024-25')""")
            bmaps = id_map(bio, "player_name", "player_id")
            fill = keep.nba_player_id.isna()
            keep.loc[fill, "nba_player_id"] = resolve(keep[fill], bmaps)
            r.note("ids: %d from v1, %d more from the warehouse bio table"
                   % (n_v1, int(keep.nba_player_id.notna().sum()) - n_v1))
        except Exception as e:                                   # noqa: BLE001
            # D111: this fallback used to be silent. A chain launched while the warehouse
            # was offline (2026-09-25 09:23) blanked 27 ids in the frozen snapshot and sent
            # two players to replacement level downstream. Without the warehouse the step
            # now fails, unless the run says explicitly that it accepts v1 ids only.
            if os.environ.get("KUMINGA_ALLOW_NO_WAREHOUSE") != "1":
                raise RuntimeError("warehouse id fill unavailable (%s): the roster snapshot "
                                   "would lose ids; set KUMINGA_ALLOW_NO_WAREHOUSE=1 to accept "
                                   "v1 ids only" % type(e).__name__) from e
            r.note("warehouse id fill unavailable (%s); v1 ids only (KUMINGA_ALLOW_NO_WAREHOUSE=1)"
                   % type(e).__name__)

        unresolved = keep[keep.nba_player_id.isna()]
        r.note("UNRESOLVED ids: %d of %d rows. These are handled downstream by "
               "`build_rotations` (2026 draftees get synthetic negative ids from the "
               "draft table; anyone else falls to replacement level), and they are "
               "listed so that is a decision and not an accident."
               % (len(unresolved), len(keep)))
        for t, g in unresolved.groupby("team_abbr"):
            r.note("    %s: %s" % (t, ", ".join(sorted(g.player_name))))

        # ---- emit v1's schema ------------------------------------------------
        out = pd.DataFrame({
            "as_of_date": keep.as_of,
            "season": keep.season,
            "team_abbr": keep.team_abbr,
            "player_name": keep.player_name,
            "nba_player_id": keep.nba_player_id,
            "br_player_id": None,
            "slot_type": "standard",
            "salary_2026_27": keep.cap_hit_2026_27,
            "option_type": keep.contract_type,
            "remaining_guaranteed_total": keep.guaranteed,
            "age": keep.age,
            "position": keep.position,
            "trigger_date": None, "trigger_type": None, "trigger_event": None,
            "status": keep.status.map(lambda s: "reported_pending_official"
                                      if s == "pending" else s),
            "source": "spotrac_v3",
        })
        out.to_csv(OUT, index=False)
        h = hashlib.sha256(open(OUT, "rb").read()).hexdigest()
        open(OUT.replace(".csv", ".sha256"), "w").write(h + "\n")
        r.note("wrote %d rows across %d teams, sha256 %s"
               % (len(out), out.team_abbr.nunique(), h[:16]))

        # ---- what changes for the sim, team by team --------------------------
        old = v1[v1.slot_type.isin(["standard", "placeholder"])].copy()
        rows = []
        for t in sorted(set(out.team_abbr) | set(old.team_abbr)):
            a = set(old[old.team_abbr == t].player_name.map(nkey))
            b = set(out[out.team_abbr == t].player_name.map(nkey))
            nm = dict(zip(out.player_name.map(nkey), out.player_name))
            nm.update(dict(zip(old.player_name.map(nkey), old.player_name)))
            for k in sorted(b - a):
                rows.append(dict(team=t, change="added", player=nm.get(k, k)))
            for k in sorted(a - b):
                rows.append(dict(team=t, change="removed", player=nm.get(k, k)))
        diff = pd.DataFrame(rows)
        diff.to_csv(OUT_DIFF, index=False)
        r.note("")
        r.note("SIM ROSTER CHANGES vs v1: %d across %d teams"
               % (len(diff), diff.team.nunique() if len(diff) else 0))
        big = diff.groupby("team").size().sort_values(ascending=False)
        r.note("  most changed: " + ", ".join("%s %d" % (t, n)
                                              for t, n in big.head(6).items()))
        mn = diff[diff.team == "MIN"]
        r.note("  MINNESOTA: " + (", ".join("%s %s" % (x.change, x.player)
                                            for _, x in mn.iterrows())
                                  if len(mn) else "no change"))
        r.output(OUT, rows=len(out))
        r.output(OUT_DIFF, rows=len(diff))

    print()
    print(out.groupby("team_abbr").size().to_string())


if __name__ == "__main__":
    main()

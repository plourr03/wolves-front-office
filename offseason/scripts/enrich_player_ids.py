#!/usr/bin/env python3
"""
enrich_player_ids.py

Resolves the THREE id namespaces in the offseason data to one canonical key so
money can be joined to performance.

  - nba_contracts_2026_27.csv : player_id is a HoopsHype id (6-7 digits)
  - nba_free_agents_2026.csv   : player_id is a Spotrac id (4-6 digits)
  - the warehouse              : player_id is the nba_stats id (the join key for
                                 every performance table: stats, RAPM, tracking)

The two scraped id systems do NOT reconcile to each other (zero overlap), and
neither reconciles to the warehouse. So the bridge is the player NAME, matched
against the warehouse player dimension. This script:

  1. Builds a canonical dimension from the warehouse: nba_stats player_id, name,
     and POSITION (from nba_team_rosters season 2025 = 2025-26), with id coverage
     broadened by anyone who logged minutes in 2024-25 or 2025-26.
  2. Matches every contract and free-agent name to it (exact on a normalized name,
     then a 92+ fuzzy pass, then a last-name-anchored pass for nicknames/short
     forms like Nic/Nicolas Claxton, Herb/Herbert Jones, Svi Mykhailiuk). A small
     explicit alias map covers pure nicknames (Bones Hyland, Bub Carrington).
  3. Writes player_id_crosswalk.csv (the durable, auditable mapping).
  4. Enriches the two source files IN PLACE: fills nba_player_id on both, fills
     the blank position column on contracts, flags rounded placeholder salaries
     on contracts, and flags the option-decision boundary on free agents.

Players left UNMATCHED are deep-bench / two-way / out-of-league names with no NBA
minutes in the window. They are intentionally left blank rather than force-matched
(a wrong id is worse than a missing one), and there is no performance data to join
to them anyway.

This is a POST-SCRAPE step. Pipeline order: run the scrapers, then run this.

    python enrich_player_ids.py
"""

import os
import re
import csv
import sys
import time
import unicodedata
import collections

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
POSTMORTEM = os.path.join(REPO, "postmortem")
DATA = os.path.join(HERE, "..", "data")

# Reuse the warehouse connection helper + .env from the postmortem repo.
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(POSTMORTEM, ".env"))
except ImportError:
    pass
sys.path.insert(0, os.path.join(POSTMORTEM, "lib"))
import db  # noqa: E402

CONTRACTS = os.path.join(DATA, "nba_contracts_2026_27.csv")
FREE_AGENTS = os.path.join(DATA, "nba_free_agents_2026.csv")
CROSSWALK = os.path.join(DATA, "player_id_crosswalk.csv")

# Source legal name (normalized) -> canonical nba.com name (normalized). Only for
# pure nicknames that share neither first name nor initial with the legal name.
ALIAS = {
    "nahshon hyland": "bones hyland",
    "carlton carrington": "bub carrington",
}

UNMATCHED_NOTE = "no NBA minutes 2024-25/2025-26 (deep bench / two-way / out-of-league)"


def norm(name):
    """Lowercase, strip diacritics, drop punctuation and generational suffixes."""
    n = unicodedata.normalize("NFKD", name or "")
    n = "".join(c for c in n if not unicodedata.combining(c))
    n = n.lower().replace(".", "").replace("'", "").replace("-", " ")
    n = re.sub(r"\b(jr|sr|ii|iii|iv|v)\b", "", n)
    return re.sub(r"\s+", " ", n).strip()


def build_canonical():
    """player_id -> (name, position). Position from the current roster; id coverage
    extended to anyone who logged minutes in the last two seasons."""
    rost = db.query(
        """SELECT DISTINCT ON (player_id) player_id, player, position
           FROM nba_team_rosters WHERE season = 2025
           ORDER BY player_id, roster_date DESC NULLS LAST"""
    )
    stats = db.query(
        """SELECT DISTINCT player_id, player_name AS player
           FROM nba_player_stats WHERE season_year IN ('2024-25', '2025-26')"""
    )
    canon = {}
    for _, r in rost.iterrows():
        canon[int(r.player_id)] = (r.player, (r.position or "").strip())
    for _, r in stats.iterrows():
        canon.setdefault(int(r.player_id), (r.player, ""))
    return canon


class Matcher:
    def __init__(self, canon):
        self.canon = canon
        self.by_norm = collections.defaultdict(list)   # norm full name -> [pid]
        self.by_last = collections.defaultdict(list)    # last token -> [(norm, pid)]
        for pid, (nm, _) in canon.items():
            nn = norm(nm)
            self.by_norm[nn].append(pid)
            self.by_last[nn.split()[-1]].append((nn, pid))
        self.names = list(self.by_norm.keys())
        from rapidfuzz import process, fuzz
        self._process, self._fuzz = process, fuzz

    def match(self, raw):
        """Return (nba_player_id, method, score, ambiguous_count)."""
        nn = ALIAS.get(norm(raw), norm(raw))
        if not nn:
            return ("", "UNMATCHED", 0, 0)
        if nn in self.by_norm:
            ids = self.by_norm[nn]
            method = "exact" if len(ids) == 1 else "exact-ambiguous"
            return (ids[0], method, 100, len(ids))
        hit = self._process.extractOne(nn, self.names, scorer=self._fuzz.token_sort_ratio)
        if hit and hit[1] >= 92:
            ids = self.by_norm[hit[0]]
            return (ids[0], "fuzzy", round(hit[1]), len(ids))
        toks = nn.split()
        first = toks[0]
        cands = self.by_last.get(toks[-1], [])
        good = [
            (cn, pid) for cn, pid in cands
            if cn.split()[0] == first
            or cn.split()[0].startswith(first[:3]) or first.startswith(cn.split()[0][:3])
            or self._fuzz.ratio(first, cn.split()[0]) >= 70
        ]
        if len(good) == 1:
            cn, pid = good[0]
            return (pid, "lastname", round(self._fuzz.token_sort_ratio(nn, cn)), 1)
        return ("", "UNMATCHED", hit[1] if hit else 0, 0)


def _read(path):
    with open(path, encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
        return rows, (list(rows[0].keys()) if rows else [])


def _write(path, rows, fieldnames):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def _is_estimate(row):
    """Flat-and-round multiyear salary => almost certainly a HoopsHype placeholder.
    Real deals escalate. Advisory flag: verify the exact cap hit vs Spotrac before
    any trade-legality check on this player."""
    vals = []
    for k in ("salary_2026_27", "salary_2027_28", "salary_2028_29", "salary_2029_30"):
        v = (row.get(k) or "").strip()
        if v.isdigit():
            vals.append(int(v))
    return len(vals) >= 2 and len(set(vals)) == 1 and vals[0] % 1_000_000 == 0 and vals[0] >= 2_000_000


def main():
    print("Building canonical dimension from warehouse ...")
    canon = build_canonical()
    matcher = Matcher(canon)
    print(f"  {len(canon)} canonical players")

    crosswalk_rows = []
    today = time.strftime("%Y-%m-%d")
    summary = {}

    for system, path, namecol in (
        ("hoopshype", CONTRACTS, "player"),
        ("spotrac", FREE_AGENTS, "player"),
    ):
        rows, fieldnames = _read(path)
        counts = collections.Counter()
        for r in rows:
            pid, method, score, ambig = matcher.match(r[namecol])
            counts[method] += 1
            r["nba_player_id"] = pid
            nba_name, position = (canon[pid] if pid else ("", ""))
            # contracts: backfill position + flag estimate salaries
            if system == "hoopshype":
                if position and not (r.get("position") or "").strip():
                    r["position"] = position
                r["salary_is_estimate"] = "TRUE" if _is_estimate(r) else "FALSE"
            # free agents: option-decision boundary flag (see data README)
            if system == "spotrac":
                r["counts_on_books_until_declined"] = (
                    "TRUE" if r.get("fa_type") in ("PLYR", "CLUB") else "FALSE"
                )
            crosswalk_rows.append({
                "source_system": system,
                "source_id": r.get(f"{namecol}_id") or r.get("player_id", ""),
                "source_name": r[namecol],
                "nba_player_id": pid,
                "nba_name": nba_name,
                "position": position,
                "match_method": method,
                "match_score": score,
                "ambiguous_count": ambig,
                "note": UNMATCHED_NOTE if method == "UNMATCHED" else "",
            })

        # Ensure new columns are in the header even if no row triggered them.
        for col in ("nba_player_id", "salary_is_estimate", "counts_on_books_until_declined"):
            if any(col in r for r in rows) and col not in fieldnames:
                fieldnames.append(col)
        _write(path, rows, fieldnames)
        matched = len(rows) - counts["UNMATCHED"]
        summary[os.path.basename(path)] = (len(rows), matched, dict(counts))
        print(f"  {os.path.basename(path)}: {matched}/{len(rows)} matched ({dict(counts)})")

    _write(
        CROSSWALK, crosswalk_rows,
        ["source_system", "source_id", "source_name", "nba_player_id", "nba_name",
         "position", "match_method", "match_score", "ambiguous_count", "note"],
    )
    # Surface any exact-name collisions (two real players, one normalized name) for review.
    collisions = [r for r in crosswalk_rows if r["match_method"] == "exact-ambiguous"]
    if collisions:
        print("\n  REVIEW exact-ambiguous (same normalized name -> multiple ids):")
        for c in collisions:
            print(f"    {c['source_name']} -> id {c['nba_player_id']} ({c['ambiguous_count']} candidates)")

    print(f"\nWrote crosswalk -> {CROSSWALK} ({len(crosswalk_rows)} rows)")
    print("Enriched source files in place.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
motivation_overrides.py  -- Phase 2, Component B: the sourced news layer.

The ONLY channel for news-driven motivation. The computed urgency layer (build_urgency_layer.py)
handles apron pressure, win-now pressure, asset hunger, and expiring risk from data. This module
handles only what data cannot know: trade demands, extend-or-trade ultimatums, who is openly
shopping whom, owner win-now mandates, and soft "not available" statements. It NEVER synthesizes a
signal from stats. Absent an entry, a team or player is neutral on the news axis.

Non-negotiable rules enforced here:
  - every entry needs a source and a date, or it is dropped.
  - every entry has an expiry (default 6 weeks from date). Past expiry it is ignored with a warning,
    so a stale "available" cannot linger after a player signs.
  - low confidence (J) applies a smaller effective magnitude than reported (R).

Effects (applied by partner_acceptance.py, Component C; this module only exposes the signal):
  - seller-side types (forced_seller, trade_demand, extend_or_trade, shopping): the player is more
    movable and the required return softens.
  - win_now_mandate (team): adds to that team's win-now pressure.
  - not_available_soft (player): raises his price and keeps him speculative (consistent with the
    untouchables speculative tier; do not double-count there).

    python motivation_overrides.py            # print active/expired/unresolved as of today
"""

import os
import csv
import re
import sys
import unicodedata
from datetime import date, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")

CONF_SCALE = {"R": 1.0, "J": 0.6}            # low confidence -> smaller effective magnitude
SELLER_TYPES = {"forced_seller", "trade_demand", "extend_or_trade", "shopping"}
WIN_NOW_TYPES = {"win_now_mandate"}
SOFT_UNAVAIL_TYPES = {"not_available_soft"}
VALID_TYPES = SELLER_TYPES | WIN_NOW_TYPES | SOFT_UNAVAIL_TYPES
DEFAULT_EXPIRY_WEEKS = 6

_PLAYER = None       # pid(str) -> entry dict
_TEAM = None         # team_abbr -> {type -> entry dict}
_DIAG = None         # {"expired": [...], "unresolved": [...], "dropped": [...]}


def _norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    s = re.sub(r"[.\-']", "", s)
    s = re.sub(r"\b(jr|sr|ii|iii|iv|v)\b", "", s)
    return re.sub(r"\s+", " ", s).strip()


def _name_indexes():
    """Return ((team, norm_name)->pid, norm_name->(pid, team)) from player_surplus.csv."""
    by_team_name, by_name = {}, {}
    with open(os.path.join(DATA, "player_surplus.csv"), encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            pid = str(r["player_id"]).strip()
            key = _norm(r["player_name"])
            by_team_name[(r["team_abbr"], key)] = pid
            by_name[key] = (pid, r["team_abbr"])
    return by_team_name, by_name


def _parse_date(s):
    try:
        return date.fromisoformat((s or "").strip())
    except ValueError:
        return None


def load(as_of=None, force=False):
    """Idempotent load. as_of defaults to today, so expired rows drop on a real-time re-run."""
    global _PLAYER, _TEAM, _DIAG
    if _PLAYER is not None and not force and as_of is None:
        return _PLAYER, _TEAM
    as_of = as_of or date.today()
    by_team_name, by_name = _name_indexes()
    player, team = {}, {}
    diag = {"expired": [], "unresolved": [], "dropped": []}
    path = os.path.join(DATA, "motivation_overrides.csv")
    with open(path, encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            typ = (r.get("type") or "").strip()
            src = (r.get("source") or "").strip()
            d = _parse_date(r.get("date", ""))
            label = (r.get("key") or r.get("team") or "?").strip()
            if not src or d is None:                 # rule: source + date mandatory
                diag["dropped"].append((label, typ, "missing source or date"))
                continue
            if typ not in VALID_TYPES:
                diag["dropped"].append((label, typ, f"unknown type"))
                continue
            exp = _parse_date(r.get("expiry", "")) or (d + timedelta(weeks=DEFAULT_EXPIRY_WEEKS))
            if exp < as_of:                          # rule: ignore + warn past expiry
                diag["expired"].append((label, typ, exp.isoformat()))
                continue
            try:
                mag = max(0.0, min(1.0, float(r.get("magnitude") or 0)))
            except ValueError:
                mag = 0.0
            conf = (r.get("confidence") or "R").strip().upper()
            entry = {"type": typ, "magnitude": mag, "mag_eff": round(mag * CONF_SCALE.get(conf, 0.6), 3),
                     "source": src, "date": d.isoformat(), "expiry": exp.isoformat(),
                     "confidence": conf, "note": (r.get("note") or "").strip(),
                     "team": (r.get("team") or "").strip()}
            scope = (r.get("scope") or "").strip()
            if scope == "team":
                tm = entry["team"] or label
                team.setdefault(tm, {})[typ] = entry
            else:                                    # player scope
                nm = (r.get("key") or "").strip()
                pid = by_team_name.get((entry["team"], _norm(nm)))
                if not pid and _norm(nm) in by_name:
                    pid, actual = by_name[_norm(nm)]
                    if actual != entry["team"]:
                        entry["note"] += f" [team mismatch: news={entry['team']}, book={actual}]"
                        entry["team"] = actual
                if not pid:
                    diag["unresolved"].append((entry["team"], nm))
                    continue
                player[pid] = entry
    _PLAYER, _TEAM, _DIAG = player, team, diag
    return _PLAYER, _TEAM


# -------------------------------- accessors for Component C --------------------------------- #
def seller_motivation(pid):
    """0..1 effective: how motivated the owner of pid is to move him (seller-side news). Softens
    the required return in acceptance."""
    load()
    e = _PLAYER.get(str(pid))
    return e["mag_eff"] if e and e["type"] in SELLER_TYPES else 0.0


def soft_unavailable(pid):
    """0..1 effective: a sourced 'not available' that is not a hard untouchable. Raises price,
    keeps the player speculative."""
    load()
    e = _PLAYER.get(str(pid))
    return e["mag_eff"] if e and e["type"] in SOFT_UNAVAIL_TYPES else 0.0


def win_now_boost(team):
    """0..1 effective add to a team's win-now pressure from a sourced owner mandate."""
    load()
    e = _TEAM.get(team, {}).get("win_now_mandate")
    return e["mag_eff"] if e else 0.0


def player_signal(pid):
    load()
    return _PLAYER.get(str(pid))


def team_signal(team, typ=None):
    load()
    d = _TEAM.get(team, {})
    return d.get(typ) if typ else d


def diagnostics():
    load()
    return _DIAG


def main():
    p, t = load(force=True)
    diag = _DIAG
    as_of = date.today().isoformat()
    print(f"=== motivation_overrides (as_of {as_of}): "
          f"{len(p)} player + {sum(len(v) for v in t.values())} team active ===")
    for pid, e in p.items():
        print(f"  player {pid:8} {e['team']:4} {e['type']:18} mag {e['magnitude']:.2f} -> "
              f"eff {e['mag_eff']:.2f} [{e['confidence']}] exp {e['expiry']}  {e['source']}")
    for tm, d in t.items():
        for typ, e in d.items():
            print(f"  team   {tm:8} {typ:18} mag {e['magnitude']:.2f} -> "
                  f"eff {e['mag_eff']:.2f} [{e['confidence']}] exp {e['expiry']}  {e['source']}")
    for (label, typ, exp) in diag["expired"]:
        print(f"  WARNING expired (ignored): {label} {typ} expiry {exp} < {as_of}")
    for (tm, nm) in diag["unresolved"]:
        print(f"  WARNING unresolved player: {tm} '{nm}' (not on the priced book)")
    for (label, typ, why) in diag["dropped"]:
        print(f"  WARNING dropped: {label} {typ} ({why})")


if __name__ == "__main__":
    main()

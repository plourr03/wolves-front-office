#!/usr/bin/env python3
"""
build_playoff_translation.py

The playoff-translation read for the value layer: does a player's HALF-COURT
shot creation hold up against set, switching, physical playoff defenses, the
exact place the Wolves' kind of failure shows up.

Built from Synergy player play types (warehouse, RS + PO back to 2013-14):
  - Half-court CREATION types (vs set defenses): Isolation, PRBallHandler,
    Postup, Handoff, OffScreen. Possession-weighted PPP and percentile.
  - Regular-season baseline pooled over 2023-24..2025-26 RS.
  - Playoff read pooled over 2023-24..2025-26 PO (where the sample is adequate).
  - rs_to_po_delta = PO half-court PPP minus RS half-court PPP.
  - A directional read: holds_up / neutral / slips / insufficient_po_sample,
    with the sample size carried so small playoff samples are never hidden.

Spotup PPP is also reported separately as the off-ball spacing signal the need
layer consumes (it is not part of the on-ball creation composite).

Joins to the value layer on player_id (nba_stats id). Output:
  offseason/data/playoff_translation.csv

    python build_playoff_translation.py
"""

import os
import sys
import csv

HERE = os.path.dirname(os.path.abspath(__file__))
POSTMORTEM = os.path.abspath(os.path.join(HERE, "..", "..", "postmortem"))
OUT = os.path.join(HERE, "..", "data", "playoff_translation.csv")

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(POSTMORTEM, ".env"))
except ImportError:
    pass
sys.path.insert(0, POSTMORTEM)
from lib import db  # noqa: E402

SEASONS = ("2023-24", "2024-25", "2025-26")
CREATION = ("Isolation", "PRBallHandler", "Postup", "Handoff", "OffScreen")
PO_MIN_POSS = 50           # below this the playoff read is not trustworthy
RISE, SLIP = 0.03, -0.05   # PPP delta thresholds for the directional read


def pull(season_type):
    rows = db.query(
        """SELECT player_id, player_name, play_type, season_year,
                  poss, pts, percentile
           FROM nba_synergy_player_play_types
           WHERE season_type = %s AND season_year = ANY(%s)""",
        (season_type, list(SEASONS)))
    return rows


def aggregate(rows, types):
    """player_id -> {poss, pts, ppp, pctile (poss-weighted), name}. Pooled across seasons."""
    acc = {}
    for _, r in rows.iterrows():
        if r["play_type"] not in types:
            continue
        pid = int(r["player_id"])
        a = acc.setdefault(pid, {"poss": 0.0, "pts": 0.0, "pctile_num": 0.0, "name": r["player_name"]})
        poss = float(r["poss"] or 0)
        a["poss"] += poss
        a["pts"] += float(r["pts"] or 0)
        if r["percentile"] is not None:
            a["pctile_num"] += float(r["percentile"]) * poss
    for a in acc.values():
        a["ppp"] = a["pts"] / a["poss"] if a["poss"] else None
        a["pctile"] = a["pctile_num"] / a["poss"] if a["poss"] else None
    return acc


def total_offense_poss(rows):
    """player_id -> total Synergy possessions (all types), for reliance share."""
    acc = {}
    for _, r in rows.iterrows():
        acc[int(r["player_id"])] = acc.get(int(r["player_id"]), 0.0) + float(r["poss"] or 0)
    return acc


def main():
    rs, po = pull("Regular Season"), pull("Playoffs")
    rs_hc, po_hc = aggregate(rs, CREATION), aggregate(po, CREATION)
    rs_total = total_offense_poss(rs)
    rs_spot = aggregate(rs, ("Spotup",))

    rows = []
    for pid, a in rs_hc.items():
        po_a = po_hc.get(pid)
        po_poss = po_a["poss"] if po_a else 0
        delta = (po_a["ppp"] - a["ppp"]) if (po_a and po_a["ppp"] is not None and a["ppp"] is not None) else None
        if po_poss < PO_MIN_POSS or delta is None:
            read, caveat = "insufficient_po_sample", f"PO half-court poss={po_poss:.0f} (< {PO_MIN_POSS})"
        elif delta >= RISE:
            read, caveat = "holds_up", ""
        elif delta <= SLIP:
            read, caveat = "slips", ""
        else:
            read, caveat = "neutral", ""
        rows.append({
            "player_id": pid, "player_name": a["name"],
            "hc_ppp_rs": round(a["ppp"], 3) if a["ppp"] is not None else "",
            "hc_pctile_rs": round(a["pctile"], 3) if a["pctile"] is not None else "",
            "hc_poss_rs": round(a["poss"]),
            "hc_reliance_rs": round(a["poss"] / rs_total[pid], 3) if rs_total.get(pid) else "",
            "hc_ppp_po": round(po_a["ppp"], 3) if (po_a and po_a["ppp"] is not None) else "",
            "hc_poss_po": round(po_poss),
            "rs_to_po_delta": round(delta, 3) if delta is not None else "",
            "spotup_ppp_rs": round(rs_spot[pid]["ppp"], 3) if pid in rs_spot and rs_spot[pid]["ppp"] is not None else "",
            "spotup_pctile_rs": round(rs_spot[pid]["pctile"], 3) if pid in rs_spot and rs_spot[pid]["pctile"] is not None else "",
            "translation_read": read,
            "caveat": caveat,
            "source": "Synergy player play types (RS+PO 2023-24..2025-26, pooled)",
        })
    rows.sort(key=lambda r: -(r["hc_poss_rs"] or 0))

    fields = ["player_id", "player_name", "hc_ppp_rs", "hc_pctile_rs", "hc_poss_rs",
              "hc_reliance_rs", "hc_ppp_po", "hc_poss_po", "rs_to_po_delta",
              "spotup_ppp_rs", "spotup_pctile_rs", "translation_read", "caveat", "source"]
    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    import collections
    print(f"Wrote {len(rows)} players -> {OUT}")
    print("reads:", dict(collections.Counter(r["translation_read"] for r in rows)))
    def ascii_safe(s):
        return str(s).encode("ascii", "replace").decode()   # Windows cp1252 console guard

    print("\nHigh-volume half-court creators (RS), with playoff read:")
    for r in rows[:14]:
        print(f"  {ascii_safe(r['player_name']):24} hc_ppp_rs={r['hc_ppp_rs']} pctile={r['hc_pctile_rs']} "
              f"reliance={r['hc_reliance_rs']} | PO {r['hc_ppp_po']} (n={r['hc_poss_po']}) "
              f"delta={r['rs_to_po_delta']} -> {r['translation_read']}")


if __name__ == "__main__":
    main()

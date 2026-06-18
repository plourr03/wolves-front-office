#!/usr/bin/env python3
"""Confirm baseline MIN title odds + the CHI deal four-view dP range, for the carousel slide 4.
Reuses the trade_search engine + scenario machinery so the numbers match the committed board."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import trade_search as TS
import apply_trade as F

NS = int(sys.argv[1]) if len(sys.argv) > 1 else 4000

eng = TS.Engine(NS)
print(f"NS={NS}")
print(f"BASELINE MIN title = {eng.pre*100:.3f}%")

# CHI deal: MIN sends Randle (+ Shannon filler), gets Giddey + Okoro
RANDLE = ("Randle", 33_333_334, 0.0)
SHANNON = ("Shannon", 2_800_000, 0.0)
GIDDEY_PID = TS.MIN.get("Giddey") or None
import csv
SURP = {r["player_name"]: r["player_id"] for r in csv.DictReader(open(os.path.join(TS.DATA, "player_surplus.csv"), encoding="utf-8"))}
giddey = SURP["Josh Giddey"]; okoro = SURP["Isaac Okoro"]
in_players = [(giddey, 25_000_000), (okoro, 11_800_000)]

# Randle alone version (headline)
scen_alone = TS.min_scenario([RANDLE], in_players)
# four views
views = {"consensus": TS._dp_view(eng, scen_alone, eng.aged)}
override = scen_alone["override_ids"]
for v in ("box", "rapm", "darko"):
    if v == "darko" and not any(p in F._DARKO for p in [giddey, okoro] if F._DARKO):
        views[v] = None; continue
    iv = F.build_impacts_view(v, override, eng.aged)
    views[v] = TS._dp_view(eng, scen_alone, iv)

print("\n=== CHI deal (Randle -> Giddey+Okoro), four-view dP (percentage points of title) ===")
for k, val in views.items():
    if val is None:
        print(f"  {k:10} (no darko coverage)")
    else:
        print(f"  {k:10} dP {val:+.2f}pp   -> after {eng.pre*100+val:.2f}%")
avail_views = [x for x in views.values() if x is not None]
print(f"\n  anchor (lowest view) dP = {min(avail_views):+.2f}pp -> after {eng.pre*100+min(avail_views):.2f}%")
print(f"  consensus dP            = {views['consensus']:+.2f}pp -> after {eng.pre*100+views['consensus']:.2f}%")
print(f"  baseline                = {eng.pre*100:.2f}%")
print("\n(committed board CHI: cons +2.93 / box +1.35 / rapm +2.40 / DARKO +0.03 ; risk_adj +1.60)")

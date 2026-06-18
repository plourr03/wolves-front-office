#!/usr/bin/env python3
"""Exact four-view title dP for the clean IND deal: MIN sends Randle (alone) for
Nembhard + Toppin. Seeded/deterministic. dP = post - pre (correct sign)."""
import os, sys, csv
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import trade_search as TS
import apply_trade as F

NS = int(sys.argv[1]) if len(sys.argv) > 1 else 9000
eng = TS.Engine(NS)
S = {r["player_name"]: r["player_id"] for r in csv.DictReader(open(os.path.join(TS.DATA, "player_surplus.csv"), encoding="utf-8"))}
nem, top = S["Andrew Nembhard"], S["Obi Toppin"]
RANDLE = ("Randle", 33_333_334, 0.0)
in_players = [(nem, 19_600_000), (top, 15_000_000)]
scen = TS.min_scenario([RANDLE], in_players)
override = scen["override_ids"]

print(f"NS={NS}  baseline MIN title = {eng.pre*100:.2f}%")
views = {"consensus": TS._dp_view(eng, scen, eng.aged)}
for v in ("box", "rapm", "darko"):
    if v == "darko" and not (F._DARKO and any(p in F._DARKO for p in [nem, top])):
        views[v] = None; continue
    views[v] = TS._dp_view(eng, scen, F.build_impacts_view(v, override, eng.aged))
base = eng.pre * 100
print("IND deal (Randle -> Nembhard + Toppin), four-view dP (pts of title):")
for k, val in views.items():
    print(f"  {k:10} {'(n/a)' if val is None else f'{val:+.2f}pp -> after {base+val:.2f}%'}")
avail = [x for x in views.values() if x is not None]
print(f"  anchor(min) {min(avail):+.2f} -> {base+min(avail):.2f}%   consensus {views['consensus']:+.2f} -> {base+views['consensus']:.2f}%")
print(f"(board IND filler-version: cons +1.58 / box +0.93 / rapm +1.33 / darko +0.97 / risk-adj +0.56)")

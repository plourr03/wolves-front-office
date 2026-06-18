#!/usr/bin/env python3
"""Characterize MC noise of the CHI-deal title dP. Build pre/post leagues ONCE per view,
run _sim K times, report mean +/- sd for baseline title, post title, and dP."""
import os, sys, csv, statistics as st
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import trade_search as TS
import apply_trade as F
import bracket_sim as E

NS = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
K = int(sys.argv[2]) if len(sys.argv) > 2 else 6

eng = TS.Engine(NS)
SURP = {r["player_name"]: r["player_id"] for r in csv.DictReader(open(os.path.join(TS.DATA, "player_surplus.csv"), encoding="utf-8"))}
giddey = SURP["Josh Giddey"]; okoro = SURP["Isaac Okoro"]
RANDLE = ("Randle", 33_333_334, 0.0); SHANNON = ("Shannon", 2_800_000, 0.0)
in_players = [(giddey, 25_000_000), (okoro, 11_800_000)]
scen = TS.min_scenario([RANDLE, SHANNON], in_players)     # board's "Randle+filler" version
override = scen["override_ids"]

def title(league):
    return F._sim(league, 5.5)["teams"]["MIN"]["title"] * 100

def view_dp(view_name):
    if view_name == "consensus":
        imp = eng.aged
    else:
        imp = F.build_impacts_view(view_name, override, eng.aged)
    base = E.build_2026_27_league(imp)
    post = F.apply_trade(scen, base, imp, eng.dims, eng.ar, eng.an)
    pres = [title(base) for _ in range(K)]
    posts = [title(post) for _ in range(K)]
    dps = [po - pr for pr, po in zip(pres, posts)]   # dP = post - pre
    return pres, posts, dps

print(f"NS={NS} K={K} replications  (CHI: Randle+filler -> Giddey+Okoro)\n")
print(f"{'view':10}{'base%':>18}{'post%':>18}{'dP(pp)':>20}")
for v in ("consensus", "box", "rapm", "darko"):
    if v == "darko" and not (F._DARKO and any(p in F._DARKO for p in [giddey, okoro])):
        print(f"{v:10}  (no darko coverage for incoming)"); continue
    pres, posts, dps = view_dp(v)
    print(f"{v:10}{st.mean(pres):8.2f} +/-{(st.pstdev(pres)):4.2f}   "
          f"{st.mean(posts):8.2f} +/-{(st.pstdev(posts)):4.2f}   "
          f"{st.mean(dps):+7.2f} +/-{st.pstdev(dps):4.2f}  [{min(dps):+.2f},{max(dps):+.2f}]")
print(f"\n(committed board CHI: cons +2.93 / box +1.35 / rapm +2.40 / DARKO +0.03)")

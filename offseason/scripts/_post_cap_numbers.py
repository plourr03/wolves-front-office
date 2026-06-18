#!/usr/bin/env python3
"""Exact cap/apron numbers for the CHI carousel deal, both teams. Deterministic (evaluate_move)."""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import evaluate_move as EM

c = EM.load_constants("2026-27")
print("=== 2026-27 league thresholds ===")
for k in ("salary_cap", "luxury_tax", "first_apron", "second_apron", "full_mle", "taxpayer_mle"):
    print(f"  {k:14} ${c[k]:,.0f}")

RANDLE = {"label": "Julius Randle", "salary": 33_333_334}
SHANNON = {"label": "Terrence Shannon Jr (filler)", "salary": 2_800_000}
GIDDEY = {"label": "Josh Giddey", "salary": 25_000_000}        # salary_is_estimate -> verify Spotrac
OKORO = {"label": "Isaac Okoro", "salary": 11_800_000}

def show(team, scen, ts, out, inc):
    print(f"\n=== {team}: {scen} ===")
    print(f"  pre  tier={ts['tier']}  apron_team_salary=${ts['apron_team_salary']:,.0f}")
    r = EM.evaluate_move(ts, c, out, inc)
    print(f"  OUT: {', '.join(f'{p['label']} ${p['salary']:,.0f}' for p in out)}")
    print(f"  IN : {', '.join(f'{p['label']} ${p['salary']:,.0f}' for p in inc)}")
    print(f"  legal={r['legal']}  {r.get('failing_constraint','')}")
    if 'matching_limit' in r:
        print(f"  matching_limit on ${sum(p['salary'] for p in out):,.0f} out = ${r['matching_limit']:,.0f}")
    print(f"  take_back_more={r['take_back_more']}  hard_cap_set={r['hard_cap_set']}", end="")
    if r.get('hard_cap_room') is not None:
        print(f"  hard_cap_line=${r.get('hard_cap_line',0):,.0f}  room=${r['hard_cap_room']:,.0f}")
    else:
        print()
    print(f"  POST apron_team_salary = ${r['new_apron_team_salary']:,.0f}  tier={r['new_tier']}")
    d = r['new_distances']
    print(f"  distance to TAX        = ${d['to_tax']:,.0f}   ({'UNDER' if d['to_tax']>0 else 'OVER'})")
    print(f"  distance to 1st APRON  = ${d['to_first_apron']:,.0f}   ({'UNDER' if d['to_first_apron']>0 else 'OVER'})")
    print(f"  distance to 2nd APRON  = ${d['to_second_apron']:,.0f}   ({'UNDER' if d['to_second_apron']>0 else 'OVER'})")
    return r

min_ts = EM.load_team_state("MIN", "2026-27", "base")
chi_ts = EM.load_team_state("CHI", "2026-27", "base")

# Variant 1: MIN sends Randle alone for Giddey+Okoro (does it match without filler?)
show("MIN", "Randle (alone) -> Giddey + Okoro", min_ts, [RANDLE], [GIDDEY, OKORO])
# Variant 2: MIN sends Randle + Shannon filler
show("MIN", "Randle + filler -> Giddey + Okoro", min_ts, [RANDLE, SHANNON], [GIDDEY, OKORO])
# CHI side: sends Giddey+Okoro, receives Randle (+ filler)
show("CHI", "Giddey + Okoro -> Randle", chi_ts, [GIDDEY, OKORO], [RANDLE])
show("CHI", "Giddey + Okoro -> Randle + filler", chi_ts, [GIDDEY, OKORO], [RANDLE, SHANNON])

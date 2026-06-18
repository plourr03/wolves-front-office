#!/usr/bin/env python3
"""
_post_deal_pick.py  (scratch, for the trade-posts carousel)

Rank the REALISTIC (model-surfaced, not Speculative) board deals by how confidently BOTH sides
say yes:
  - partner side: the acceptance margin over the firing threshold, and the MINIMUM sweetener (pts)
    needed to clear (smaller = more motivated yes = "higher probability").
  - MIN side: the conservative DARKO/anchor floor and risk_adj from the board (robust benefit).

Numbers come from the same data the board used (player_surplus / dimensions / needs / posture).
"""
import os, sys, csv
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import partner_acceptance as PA
PA.load_layers()

DATA = os.path.join(HERE, "..", "data")
SURP = {r["player_id"]: r for r in csv.DictReader(open(os.path.join(DATA, "player_surplus.csv"), encoding="utf-8"))}

def pid_by_name(name):
    for pid, r in SURP.items():
        if r["player_name"] == name:
            return pid
    raise KeyError(name)

def item(name, salary):
    return {"pid": pid_by_name(name), "salary": salary, "label": name}

FILLER = {"pid": None, "salary": 2_800_000, "label": "Shannon (filler)"}  # MIN matching filler

# Realistic, MIN-positive board deals (from trade_board.csv). MIN sends -> partner; partner sends -> MIN.
# board floor = dp_darko (conservative anchor); risk_adj from board.
DEALS = [
    {"partner": "MIL", "min_sends": [item("Julius Randle", 33_333_334), FILLER],
     "min_gets": [item("Myles Turner", 27_000_000), item("AJ Green", 10_000_000)],
     "anchor": -0.63, "risk_adj": 1.98},
    {"partner": "CHI", "min_sends": [item("Julius Randle", 33_333_334), FILLER],
     "min_gets": [item("Josh Giddey", 25_000_000), item("Isaac Okoro", 12_000_000)],
     "anchor": 0.03, "risk_adj": 1.60},
    {"partner": "SAC", "min_sends": [item("Julius Randle", 33_333_334), FILLER],
     "min_gets": [item("Keegan Murray", 24_000_000), item("Malik Monk", 20_000_000)],
     "anchor": 0.52, "risk_adj": 1.15},
    {"partner": "MEM", "min_sends": [item("Julius Randle", 33_333_334), FILLER],
     "min_gets": [item("Kentavious Caldwell-Pope", 22_000_000), item("Santiago Aldama", 17_000_000)],
     "anchor": -0.5, "risk_adj": 0.77},
    {"partner": "ORL", "min_sends": [item("Naz Reid", 23_333_333), FILLER],
     "min_gets": [item("Jonathan Isaac", 14_000_000), item("Wendell Carter", 18_000_000)],
     "anchor": 1.28, "risk_adj": 0.65},
    {"partner": "IND", "min_sends": [item("Julius Randle", 33_333_334), FILLER],
     "min_gets": [item("Obi Toppin", 15_000_000), item("Andrew Nembhard", 20_000_000)],
     "anchor": 0.97, "risk_adj": 0.56},
    {"partner": "NYK", "min_sends": [item("Julius Randle", 33_333_334)],
     "min_gets": [item("Mikal Bridges", 33_000_000)],
     "anchor": -0.3, "risk_adj": 0.54},
]

SWEET_LADDER = [0.0, 0.7, 1.4, 3.5, 5.0, 7.0, 8.5]

def min_sweetener_to_clear(partner, sends, receives):
    """sends/receives are from the PARTNER's POV: partner SENDS min_gets, RECEIVES min_sends."""
    for swp in SWEET_LADDER:
        a = PA.decide(partner, sends=sends, receives=receives, sweetener_pts=swp)
        if a["accepted"]:
            return swp, a
    return None, PA.decide(partner, sends=sends, receives=receives, sweetener_pts=8.5)

print(f"{'PARTNER':7} {'CH':10} {'min_sweet':9} {'d_value':8} {'need_gain':9} {'net_absorb':11} {'floor':6} {'risk_adj':8}")
print("-" * 78)
rows = []
for d in DEALS:
    partner = d["partner"]
    # partner sends what MIN gets; receives what MIN sends
    p_sends = [{"pid": x["pid"], "salary": x["salary"], "label": x["label"]} for x in d["min_gets"]]
    p_recv = [{"pid": x["pid"], "salary": x["salary"], "label": x["label"]} for x in d["min_sends"]]
    swp, a = min_sweetener_to_clear(partner, p_sends, p_recv)
    rows.append((d, swp, a))
    swp_s = f"{swp:.1f}pts" if swp is not None else "FAILS"
    print(f"{partner:7} {str(a['channel']):10} {swp_s:9} {a['delta_value']:+8.2f} {a['need_gain']:+9.3f} "
          f"{a['net_absorb']:+11,.0f} {d['anchor']:+6.2f} {d['risk_adj']:+8.2f}")

print("\n--- ranking by (accepts with small sweetener) + (MIN floor not underwater) + (risk_adj) ---")
def score(t):
    d, swp, a = t
    if swp is None:
        return -99
    sweet_pen = -swp * 0.15          # cheaper acceptance = higher prob of getting done
    floor_term = d["anchor"]          # MIN's conservative benefit must be real
    return sweet_pen + floor_term + 0.5 * d["risk_adj"]
for d, swp, a in sorted(rows, key=score, reverse=True):
    swp_s = f"{swp:.1f}pts" if swp is not None else "FAILS"
    print(f"  {d['partner']:5} score={score((d,swp,a)):+.2f}  sweet={swp_s:7} floor={d['anchor']:+.2f} "
          f"risk_adj={d['risk_adj']:+.2f} ch={a['channel']}")

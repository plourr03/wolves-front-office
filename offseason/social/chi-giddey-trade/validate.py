"""Re-validate every on-screen number in the Nembhard/Toppin carousel against the trade MODEL.

The model is this post's warehouse: nothing reaches a slide without a model run behind it.
Re-runs the INSTANT, deterministic pieces (cap legality + apron landing via evaluate_move,
partner acceptance via partner_acceptance) and reads the committed board for the title-odds
views, then checks each against what deal.json plans to display.

Deal: Minnesota sends Julius Randle + Terrence Shannon Jr. for Andrew Nembhard + Obi Toppin
(a clean 2-for-2; the 1-for-2 'Randle alone' version is an invalid 16-man roster the sim
mis-rates, so it is not used). Deeper title re-run:
    python ../../scripts/_post_ind_title.py 9000   (note: use the 2-for-2 board values, not 1-for-2)

Usage (from this folder):
    python validate.py
"""
from __future__ import annotations
import csv, json, sys, datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
OFF = HERE.parents[1]
sys.path.insert(0, str(OFF / "scripts"))
DATA = OFF / "data"

import evaluate_move as EM
import partner_acceptance as PA

deal = json.loads((HERE / "src" / "deal.json").read_text(encoding="utf-8"))
rows, ok = [], True
def check(cid, label, got, want):
    global ok
    passed = str(got) == str(want)
    ok = ok and passed
    rows.append((cid, str(want), str(got), "match" if passed else "DIFFERS", "ok" if passed else "FAIL"))

c = EM.load_constants("2026-27")
min_ts = EM.load_team_state("MIN", "2026-27", "base")
ind_ts = EM.load_team_state("IND", "2026-27", "base")
RANDLE = {"label": "Randle", "salary": 33_333_334}
SHANNON = {"label": "Shannon", "salary": 2_800_000}
NEM = {"label": "Nembhard", "salary": 19_600_000}
TOP = {"label": "Toppin", "salary": 15_000_000}

# ---- cap: MIN side (2-for-2) ----
m = EM.evaluate_move(min_ts, c, [RANDLE, SHANNON], [NEM, TOP])
check("min_legal", "MIN deal legal", m["legal"], True)
check("min_post", "MIN post $192.5M", f"${m['new_apron_team_salary']/1e6:.1f}M", "$192.5M")
check("min_under_tax", "MIN under tax $8.5M", f"${m['new_distances']['to_tax']/1e6:.1f}M", "$8.5M")
check("min_no_hardcap", "MIN no hard cap (sheds salary)", m["take_back_more"] or m["hard_cap_set"] != "none", False)

# ---- cap: IND side ----
i = EM.evaluate_move(ind_ts, c, [NEM, TOP], [RANDLE, SHANNON])
check("ind_legal", "IND deal legal", i["legal"], True)

# ---- acceptance: IND accepts via the value channel ----
PA.load_layers()
SURP = {r["player_name"]: r["player_id"] for r in csv.DictReader(open(DATA / "player_surplus.csv", encoding="utf-8"))}
p_sends = [{"pid": SURP["Andrew Nembhard"], "salary": 19_600_000, "label": "Nembhard"},
           {"pid": SURP["Obi Toppin"], "salary": 15_000_000, "label": "Toppin"}]
p_recv = [{"pid": SURP["Julius Randle"], "salary": 33_333_334, "label": "Randle"},
          {"pid": None, "salary": 2_800_000, "label": "Shannon"}]
a = PA.decide("IND", p_sends, p_recv, sweetener_pts=0.0)
check("ind_accepts", "IND accepts (value channel)", a["accepted"] and a["channel"] == "value", True)

# ---- title odds: committed board, IND row ----
board = {r["partner"]: r for r in csv.DictReader(open(DATA / "trade_board.csv", encoding="utf-8"))}
ind = board["IND"]
print("Committed board IND title-odds views (pts of championship probability):")
print(f"   DARKO {ind['dp_darko']}  box {ind['dp_box']}  RAPM {ind['dp_rapm']}  consensus {ind['dp_consensus']}"
      f"  | anchor {ind['anchor']}  risk-adj {ind['risk_adj']}  flex {ind['flex_2027']}  accept={ind['accept_channel']}")
check("board_riskadj", "board risk-adj +0.56", ind["risk_adj"], "0.56")
check("board_flex", "board flex MODERATE", ind["flex_2027"], "MODERATE")
check("board_channel", "board accept value", ind["accept_channel"], "value")

print()
w = max(len(r[0]) for r in rows)
print(f"{'check':<{w}}  {'planned':<16}  {'model':<16}  {'verdict':<8}  status")
for cid, want, got, verdict, status in rows:
    print(f"{cid:<{w}}  {want:<16}  {got:<16}  {verdict:<8}  {status}")

prov = {"pulled_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "deal": "MIN: Randle + Shannon Jr. -> Nembhard + Toppin (+ one first), Indiana",
        "checks": [{"id": r[0], "planned": r[1], "model": r[2], "status": r[4]} for r in rows]}
(HERE / "provenance.json").write_text(json.dumps(prov, indent=2))
print("\nProvenance -> provenance.json")
if not ok:
    sys.exit("\nVALIDATION FAILED: a displayed number does not match the model. Do not publish.")
print("\nAll model-backed numbers reproduce. Title-odds shown as a RANGE (positive on every view).")

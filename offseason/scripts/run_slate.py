#!/usr/bin/env python3
"""
run_slate.py

Runs the acquisition metric across the 2026 target slate and prints a first-read
board, anchored on Anthony Davis (the cleanest both-out star test). Carries the
guardrails from review: impact intervals travel, impact-decided borderline verdicts
are marked provisional, and clear feasibility calls (clearly feasible / clearly
infeasible) are treated as robust now since they do not lean on impact precision.

Also surfaces, from the value layer itself, rim protectors who fit the both-out
companion-move need (the hole a wing acquisition leaves), independent of the
reported names.

Availability is an assumption for every target and is flagged, not asserted.

    python run_slate.py
"""

import os
import sys
import csv

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
OUTDIR = os.path.join(HERE, "..", "outputs", "acquisition_profiles")
sys.path.insert(0, HERE)
import acquisition_metric as am

# (name, age, group, availability note). Ages are stable facts; salaries/teams come
# from the verified June-6 contract pull. Davis first as the priority model.
SLATE = [
    ("Anthony Davis", 33, "star anchor", "WAS rebuild; plausibly available, not confirmed"),
    ("Giannis Antetokounmpo", 32, "star (long shot)", "MIL has not made him available; long shot"),
    ("Ja Morant", 27, "reported star", "MEM trade chatter; not confirmed"),
    ("Kyrie Irving", 34, "reported star", "DAL; age and ACL history are the swing factors"),
    ("Zion Williamson", 26, "reported star", "NOP; availability and health dominate"),
    ("Trae Young", 28, "reported star", "WAS; plausibly available"),
    ("Lauri Markkanen", 29, "gettable vet", "UTA; gettable"),
    ("Michael Porter", 28, "gettable vet", "BKN; expiring, gettable"),
    ("Josh Giddey", 24, "gettable vet (Bulls guard)", "CHI; gettable (run in place of Coby White, who is a FA in our data)"),
    ("Immanuel Quickley", 27, "gettable vet", "TOR; gettable"),
    ("DeMar DeRozan", 37, "gettable vet", "SAC; expiring vet, gettable"),
]


def robustness(matrix):
    """Clear feasibility calls are robust now; impact-borderline verdicts are provisional."""
    feas_cats = {m["feasibility"]["category"] for m in matrix}
    best = max(matrix, key=lambda m: m["score"])
    if best["feasibility"]["category"] == "infeasible" and feas_cats == {"infeasible"}:
        return "ROBUST (clearly infeasible across all scenarios)"
    if best["impact"].get("wide_band"):
        return "PROVISIONAL (impact-driven, wide band)"
    return "robust-ish (feasibility-led)"


def value_layer_rim_protectors():
    """Independent surfacing: reliable rim protectors who fit the both-out companion
    need and are plausibly absorbable in a Wolves deal (mid salary, not on MIN)."""
    val = {r["player_id"]: r for r in csv.DictReader(open(os.path.join(DATA, "player_value.csv"), encoding="utf-8"))}
    dim = {r["player_id"]: r for r in csv.DictReader(open(os.path.join(DATA, "player_dimensions.csv"), encoding="utf-8"))}
    con = {}
    for r in csv.DictReader(open(os.path.join(DATA, "nba_contracts_2026_27.csv"), encoding="utf-8")):
        if r["nba_player_id"]:
            con[r["nba_player_id"]] = r
    out = []
    for pid, v in val.items():
        d, c = dim.get(pid), con.get(pid)
        if not d or not c or c["team_abbr"] == "MIN":
            continue
        sal = int(c["salary_2026_27"]) if (c["salary_2026_27"] or "").isdigit() else 0
        rim = float(d["rim_protect_reb"])
        net = float(v["net_rapm"])
        if (v["reliable"] == "TRUE" and rim >= 0.80 and net >= 2.0
                and 5_000_000 <= sal <= 30_000_000 and c["position"] in am.BIG_POSITIONS):
            out.append((v["player_name"], c["team_abbr"], sal, round(net, 1), round(rim, 2)))
    out.sort(key=lambda x: -x[4])
    return out[:8]


def safe(s):
    return str(s).encode("ascii", "replace").decode()


def main():
    rows = []
    for name, age, group, avail in SLATE:
        try:
            tgt, matrix, overall, scen = am.run(name, age=age, availability_note=avail)
        except ValueError as e:
            print("  SKIP", safe(name), e)
            continue
        best = max(matrix, key=lambda m: m["score"])
        feas_by = {m["scenario"]: m["feasibility"]["category"] for m in matrix}
        rows.append({
            "name": tgt["name"], "group": group, "age": age, "team": tgt["team"],
            "salary": tgt["salary"], "expiring": tgt["expiring"],
            "net": tgt["net_rapm"], "band": matrix[0]["impact"]["band"],
            "read": tgt["playoff_read"], "best_scen": scen, "best_score": best["score"],
            "best_score_dn": best["score_downside"], "overall": overall,
            "robust": robustness(matrix), "feas": feas_by,
            "contingent": best["contingent_on"],
        })

    # board order: feasible-and-scoring first, then stretch, then infeasible
    order = {"feasible": 0, "stretch": 1, "infeasible": 2}
    rows.sort(key=lambda r: (min(order[c] for c in r["feas"].values()), -r["best_score"]))

    lines = ["# 2026 Wolves acquisition board (first read)\n",
             "_Generated by run_slate.py across the exit scenarios. Availability is an "
             "assumption for every name. Clear feasibility calls are robust now; impact-"
             "driven borderline verdicts are marked PROVISIONAL pending external "
             "triangulation (EPM/DARKO/LEBRON). Trade cost is comp-anchored, not a price._\n",
             "| Target | Grp | Age | $26-27 | Net RAPM (band) | PO read | Best scen | Score (mean/dn) | Robustness | Verdict |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        exp = " (exp)" if r["expiring"] else ""
        lines.append(f"| {r['name']} | {r['group']} | {r['age']} | ${r['salary']/1e6:.1f}M{exp} | "
                     f"{r['net']:+.1f} ({r['band'][0]:+.1f},{r['band'][1]:+.1f}) | {r['read']} | "
                     f"{r['best_scen'] or '-'} | {r['best_score']:.2f}/{r['best_score_dn']:.2f} | "
                     f"{r['robust']} | {r['overall']} |")

    rim = value_layer_rim_protectors()
    lines.append("\n## Value-layer surfaced: rim protectors for the both-out companion move\n")
    lines.append("_The both-out scenario's top need is rim protection, which a wing target cannot "
                 "fill. These reliable rim-protecting bigs (mid-salary, absorbable) are surfaced by "
                 "the value layer as companion candidates; availability is unverified._\n")
    lines.append("| Big | Team | $26-27 | Net RAPM | rim_protect pctile |")
    lines.append("|---|---|---|---|---|")
    for n, t, s, net, r in rim:
        lines.append(f"| {n} | {t} | ${s/1e6:.1f}M | {net:+.1f} | {r:.2f} |")

    board = os.path.join(OUTDIR, "_BOARD.md")
    with open(board, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")

    print(f"\nboard -> {board}\n")
    print(f"{'target':24}{'grp':16}{'best scen':12}{'score':>6} {'robust':>14}  verdict")
    for r in rows:
        print(f"{safe(r['name']):24}{r['group'][:15]:16}{(r['best_scen'] or '-'):12}"
              f"{r['best_score']:>6.2f} {r['robust'][:13]:>14}  {safe(r['overall'])[:60]}")
    print("\nValue-layer rim protectors (both-out companion candidates):")
    for n, t, s, net, rp in rim:
        print(f"  {safe(n):22} {t}  ${s/1e6:>5.1f}M  net {net:+.1f}  rim {rp:.2f}")


if __name__ == "__main__":
    main()

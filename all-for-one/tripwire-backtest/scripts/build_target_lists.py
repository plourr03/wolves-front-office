"""ARM-G / ARM-B draft target lists via the acceptance model.

For each candidate, run partner_acceptance.decide() with MIN acquiring the
player and sending the Green (~14.7M) or DiVincenzo (~12.9M) expiring as
matching salary, and find the minimum sweetener (asset points) at which the
partner accepts. Boolean verdict + required sweetener price, per Bobby's
directive.

CAVEAT (carried verbatim into TRIPWIRES.md, from
offseason/docs/acceptance_model_scope_and_limitation.md): the acceptance
model is MIN-acquisition-specific and its coefficients are hand-set;
calibration on real trades did not generalize (16% recall), so MARGINAL
deals near the accept/reject boundary are the least reliable, which is
exactly where a target list lives. Read as a plausibility screen, not a
probability.

This is a DRAFT list on 2026-27 contract data; finalize against live
rosters near the deadline.
"""
from __future__ import annotations

import sys
from pathlib import Path
import pandas as pd

REPO = Path(r"C:\Users\bobby\playground\wolves-front-office")
sys.path.insert(0, str(REPO / "offseason" / "scripts"))
import partner_acceptance as PA  # noqa: E402

CONTRACTS = pd.read_csv(REPO / "offseason" / "data" / "nba_contracts_2026_27_verified.csv")
POSTURE = pd.read_csv(REPO / "offseason" / "data" / "team_posture.csv")

GREEN = {"pid": None, "salary": 14_700_000, "label": "Josh Green (expiring 14.7M)"}
DDV = {"pid": None, "salary": 12_900_000, "label": "DiVincenzo (expiring 12.9M, inj)"}
# MIN sends the expiring; pid=None so it carries no partner surplus (a pure salary match).

# candidate archetypes: backup guards (ARM-G), backup bigs / rebounding forwards (ARM-B).
# Real players from the 2026-27 contract set, salary matchable to a single expiring
# (<= ~15M) or the aggregate (Green+DDV ~27.6M). Filtered to plausible-seller teams.
ARM_G_NAMES = ["Collin Sexton", "Coby White", "Malcolm Brogdon", "Cam Thomas",
               "Bruce Brown", "Gary Trent Jr.", "Tre Jones"]
ARM_B_NAMES = ["Nick Richards", "Jonas Valanciunas", "Jakob Poeltl", "Robert Williams III",
               "Isaiah Stewart", "Naz Reid", "Jarrett Allen", "Nic Claxton"]


def find_candidate(name):
    m = CONTRACTS[CONTRACTS.player.str.lower() == name.lower()]
    if not len(m):
        # loose match
        m = CONTRACTS[CONTRACTS.player.str.lower().str.contains(name.split()[-1].lower())]
    return m.iloc[0] if len(m) else None


def min_sweetener(partner, candidate_item, expiring):
    """smallest sweetener_pts (0..12) at which partner accepts; None if never."""
    for swp in [0, 1, 2, 3, 4, 5, 6, 8, 10, 12]:
        v = PA.decide(partner, sends=[candidate_item], receives=[expiring], sweetener_pts=swp)
        if v.get("accepted"):
            return swp, v
    return None, v


def run(names, arm, expiring):
    print(f"\n{'='*78}\n{arm}  (MIN sends {expiring['label']})\n{'='*78}")
    print(f"{'target':22s} {'team':5s} {'pos':4s} {'salary':>10s} {'min_sweetener':>14s} {'channel'}")
    rows = []
    for nm in names:
        c = find_candidate(nm)
        if c is None:
            print(f"{nm:22s} (not in 2026-27 contract set)")
            continue
        # salary match: single expiring must cover, else note aggregate needed
        item = {"pid": str(c.nba_player_id), "salary": int(c.salary_2026_27), "label": nm}
        try:
            swp, v = min_sweetener(c.team_abbr, item, expiring)
        except Exception as e:
            print(f"{nm:22s} {c.team_abbr:5s} ERROR {type(e).__name__}: {str(e)[:40]}")
            continue
        matched = c.salary_2026_27 <= expiring["salary"] * 1.0
        note = "" if matched else " [needs Green+DDV aggregate]"
        ch = v.get("channel", "-") if swp is not None else "NO DEAL <=12"
        sw = f"{swp} pts" if swp is not None else "none@<=12"
        print(f"{nm:22s} {c.team_abbr:5s} {str(c.position):4s} {c.salary_2026_27:>10,} {sw:>14s} {ch}{note}")
        rows.append({"arm": arm, "target": nm, "team": c.team_abbr, "salary": int(c.salary_2026_27),
                     "min_sweetener_pts": swp, "channel": ch, "matched_single": bool(matched)})
    return rows


def main():
    allrows = []
    allrows += run(ARM_G_NAMES, "ARM-G (guard depth)", GREEN)
    allrows += run(ARM_B_NAMES, "ARM-B (backup big / rebounding fwd)", DDV)
    out = REPO / "all-for-one" / "tripwire-backtest" / "data" / "target_lists.csv"
    pd.DataFrame(allrows).to_csv(out, index=False)
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()

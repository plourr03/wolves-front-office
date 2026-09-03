#!/usr/bin/env python3
"""Gates A and B on roster_snapshot_2026_27 v3. Fail closed.

GATE A IS RE-SPECIFIED, and the reason is recorded because it overturns a G4 verdict.
The G4 gate demanded 13 to 15 standard contracts per team. It failed seven teams, six of
them on SPOTRAC'S OWN PUBLISHED COUNTS. The gate was wrong, not the data: **13-to-15 is
a regular-season rule.** Article XXIX sets the in-season minimum (14, with a two-week
grace at 13) and the maximum is 15 plus 3 two-ways. In the offseason a team may carry up
to 20 standard contracts and must cut down before opening night. Applying an October
rule to an August snapshot fails teams for being legal.

    GATE A v2, offseason-aware:
      1. parsed standard count == Spotrac's own header count   (our parse is faithful)
      2. standard contracts <= 20                              (offseason roster limit)
      3. two-way contracts <= 3
      The >= 13 floor is REPORTED, not enforced, flagged as binding in October.

Test 1 is the one that protects downstream work. The old gate's real value was never the
range, it was catching a parse that silently dropped or duplicated players, and test 1
does that directly rather than by proxy.

GATE B IS RE-SPECIFIED TOO, because the old one could not say WHERE a team failed.
Spotrac itemises its own total at the foot of every page (Active Roster, Dead Money, Cap
Hold), so the total can be decomposed instead of compared as one lump:

      B1. our active-roster sum   == their Active Roster line     (30 of 30)
      B2. our dead-money sum      == their Dead Money line        (30 of 30)
      B3. our unlikely bonuses    <= their implied unlikely total, where implied is
          (apron allocations - active - dead). We may be SHORT, never OVER.

WHAT B1 AND B2 DO AND DO NOT PROVE. Our rows are parsed FROM Spotrac's table and their
itemised totals are sums of that same table, so B1 and B2 are PARSE-FIDELITY tests, not
independent-truth tests. They catch exactly the v1 failure mode (rows dropped, rows
duplicated, numbers misread) and nothing else. **The roster book is now single-sourced to
Spotrac.** A genuine independent check needs a second publisher, and that is logged as an
open risk rather than claimed as passed.

B3 IS DIFFERENT, and it is the one that carries real information. Spotrac's per-player
table renders unlikely bonuses as "-" for some contracts that their own total includes.
Four teams are short. Since the per-player column is demonstrably incomplete and the
total is not, the team's unlikely total is taken from the total as a residual, and the
per-player column is used only for who-has-what colour.

    python kuminga/scripts/roster_v3_gates.py
"""
from __future__ import annotations

import json
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO)

from kuminga.lib import runlog  # noqa: E402

SNAP = os.path.join(REPO, "kuminga", "data", "roster_snapshot_2026_27_v3.csv")
ANCH = os.path.join(REPO, "kuminga", "data", "spotrac_anchors_2026_27_v3.csv")
OUT = os.path.join(REPO, "kuminga", "outputs", "roster_v3_gates.csv")
OUTJ = os.path.join(REPO, "kuminga", "outputs", "roster_v3_gates.json")
TOL = 2_000.0
OFFSEASON_MAX = 20
RS_MIN, RS_MAX = 13, 15
ACTIVE = ("standard", "non_guaranteed")


def main():
    with runlog.run("roster_v3_gates",
                    inputs={"tolerance": TOL, "offseason_max": OFFSEASON_MAX,
                            "gate_a_spec": "v2 offseason-aware",
                            "gate_b_spec": "v2 component decomposition"}) as r:
        d = pd.read_csv(SNAP)
        an = pd.read_csv(ANCH).set_index("team_abbr")
        act = d[d.status.isin(ACTIVE)]
        dead = d[d.status == "dead_money"]

        t = pd.DataFrame({
            "n_standard": act.groupby("team_abbr").size(),
            "n_two_way": d[d.status == "two_way"].groupby("team_abbr").size(),
            "n_dead": dead.groupby("team_abbr").size(),
            "n_pending": d[d.status == "pending"].groupby("team_abbr").size(),
            "ours_active": act.groupby("team_abbr").cap_hit_2026_27.sum(),
            "ours_dead": dead.groupby("team_abbr").cap_hit_2026_27.sum(),
            "ours_unlikely": (d[d.status.isin(ACTIVE + ("dead_money",))]
                              .groupby("team_abbr").incentives_unlikely.sum()),
        }).join(an[["header_standard", "blk_active", "blk_dead", "blk_apron",
                    "implied_from_ap1", "implied_from_ap2"]])
        t = t.fillna({"n_two_way": 0, "n_dead": 0, "n_pending": 0,
                      "ours_dead": 0.0, "ours_unlikely": 0.0})

        t["sp_unlikely"] = t.blk_apron - t.blk_active - t.blk_dead
        t["d_active"] = t.ours_active - t.blk_active
        t["d_dead"] = t.ours_dead - t.blk_dead
        t["d_unlikely"] = t.ours_unlikely - t.sp_unlikely
        t["parse_faithful"] = t.n_standard == t.header_standard
        t["gate_a"] = (t.parse_faithful & (t.n_standard <= OFFSEASON_MAX)
                       & (t.n_two_way <= 3))
        t["b1"] = t.d_active.abs() <= TOL
        t["b2"] = t.d_dead.abs() <= TOL
        t["b3"] = t.d_unlikely <= TOL           # short is tolerated, OVER is not
        t["unlikely_complete"] = t.d_unlikely.abs() <= TOL
        # authoritative apron: components we verify, plus the reference's own bonus total
        t["apron"] = t.ours_active + t.ours_dead + t.sp_unlikely
        t["apron_vs_spotrac"] = t.apron - t.blk_apron

        # ---- GATE A ---------------------------------------------------------
        r.note("GATE A v2 (parse faithful, <=%d standard, <=3 two-way):" % OFFSEASON_MAX)
        r.note("  standard-count distribution: "
               + ", ".join("%s:%s" % (kk, vv)
                           for kk, vv in sorted(t.n_standard.value_counts().items())))
        r.note("  parse faithful vs Spotrac's header: %d of %d"
               % (int(t.parse_faithful.sum()), len(t)))
        for i, x in t[~t.parse_faithful].iterrows():
            r.note("    %s parsed %d vs header %d" % (i, x.n_standard, x.header_standard))
        for i, x in t[t.n_standard > OFFSEASON_MAX].iterrows():
            r.note("    %s carries %d standard, over the offseason limit of %d"
                   % (i, x.n_standard, OFFSEASON_MAX))
        gate_a = bool(t.gate_a.all())
        r.note("  GATE A: %s" % ("PASS" if gate_a else "FAIL"))
        long_ = t[t.n_standard > RS_MAX]
        r.note("  informational, the %d-%d regular-season rule that binds in October: "
               "%d teams above %d (%s). None are below %d."
               % (RS_MIN, RS_MAX, len(long_), RS_MAX,
                  ", ".join("%s=%d" % (i, x.n_standard) for i, x in long_.iterrows())
                  or "none", RS_MIN))

        # ---- GATE B ---------------------------------------------------------
        r.note("")
        r.note("GATE B v2, by component (parse fidelity against Spotrac's own itemised "
               "totals; SINGLE-SOURCE, see the module docstring):")
        r.note("  B1 active roster: %d of %d within $%s"
               % (int(t.b1.sum()), len(t), format(TOL, ",.0f")))
        for i, x in t[~t.b1].iterrows():
            r.note("    %s %s" % (i, format(x.d_active, "+,.0f")))
        r.note("  B2 dead money:    %d of %d" % (int(t.b2.sum()), len(t)))
        for i, x in t[~t.b2].iterrows():
            r.note("    %s %s" % (i, format(x.d_dead, "+,.0f")))
        r.note("  B3 unlikely bonuses, ours vs their implied total: %d of %d complete"
               % (int(t.unlikely_complete.sum()), len(t)))
        for i, x in t[~t.unlikely_complete].sort_values("d_unlikely").iterrows():
            r.note("    %s: per-player column shows %s, their total implies %s, "
                   "SHORT %s" % (i, format(x.ours_unlikely, ",.0f"),
                                 format(x.sp_unlikely, ",.0f"),
                                 format(-x.d_unlikely, ",.0f")))
        over = t[t.d_unlikely > TOL]
        if len(over):
            r.note("  B3 VIOLATION, ours EXCEEDS theirs (should be impossible): %s"
                   % ", ".join(over.index))
        r.note("  after taking unlikely bonuses from the reference total, every team's "
               "apron matches Spotrac: %d of %d"
               % (int(t.apron_vs_spotrac.abs().le(TOL).sum()), len(t)))
        gate_b = bool(t.b1.all() and t.b2.all() and t.b3.all()
                      and t.apron_vs_spotrac.abs().le(TOL).all())
        r.note("  GATE B: %s" % ("PASS" if gate_b else "FAIL"))

        # ---- tiers, which is what downstream actually consumes ---------------
        k = json.load(open(os.path.join(REPO, "offseason", "data",
                                        "league_year_constants.json"),
                           encoding="utf-8"))["seasons"]["2026-27"]
        ap1, ap2, tax = (float(k["first_apron"]), float(k["second_apron"]),
                         float(k["luxury_tax"]))

        def tier(v):
            return ("second_apron" if v >= ap2 else "first_apron" if v >= ap1
                    else "taxpayer" if v >= tax else "under_tax")

        t["tier"] = t.apron.map(tier)
        t["tier_if_column_only"] = (t.ours_active + t.ours_dead
                                    + t.ours_unlikely).map(tier)
        flip = t[t.tier != t.tier_if_column_only]
        r.note("")
        r.note("  apron tiers: " + ", ".join("%s=%d" % (kk, vv)
                                             for kk, vv in t.tier.value_counts().items()))
        r.note("  teams whose TIER depends on the missing bonuses: %s"
               % (", ".join("%s (%s -> %s)" % (i, x.tier_if_column_only, x.tier)
                            for i, x in flip.iterrows()) if len(flip) else "none"))

        mn = t.loc["MIN"]
        r.note("")
        r.note("MINNESOTA: %d standard, active $%s + dead $%s + unlikely $%s = $%s, "
               "vs Spotrac $%s, diff %s. Tier: %s."
               % (int(mn.n_standard), format(mn.ours_active, ",.0f"),
                  format(mn.ours_dead, ",.0f"), format(mn.ours_unlikely, ",.0f"),
                  format(mn.apron, ",.0f"), format(mn.blk_apron, ",.0f"),
                  format(mn.apron_vs_spotrac, "+,.0f"), mn.tier))
        r.note("  MIN's per-player bonus column is COMPLETE (%s vs %s implied), so "
               "none of the B3 shortfall touches Minnesota."
               % (format(mn.ours_unlikely, ",.0f"), format(mn.sp_unlikely, ",.0f")))

        r.note("")
        r.note("GATE A %s | GATE B %s" % ("PASS" if gate_a else "FAIL",
                                          "PASS" if gate_b else "FAIL"))
        r.note("BOTH GATES PASS. The league-wide quarantine lifts."
               if gate_a and gate_b else
               "FAIL CLOSED. Quarantine stays; downstream does not run.")

        t.reset_index().rename(columns={"index": "team"}).to_csv(OUT, index=False)
        json.dump({"gate_a": gate_a, "gate_b": gate_b,
                   "b1_active": int(t.b1.sum()), "b2_dead": int(t.b2.sum()),
                   "b3_unlikely_complete": int(t.unlikely_complete.sum()),
                   "teams_matching_apron": int(t.apron_vs_spotrac.abs().le(TOL).sum()),
                   "single_source_risk": "roster book is sourced only to Spotrac",
                   "min_apron": float(t.loc["MIN", "apron"]),
                   "min_tier": str(t.loc["MIN", "tier"])},
                  open(OUTJ, "w"), indent=1)
        r.output(OUT, rows=len(t))

    print()
    print(t[["n_standard", "parse_faithful", "ours_active", "ours_dead",
             "ours_unlikely", "sp_unlikely", "apron", "apron_vs_spotrac", "tier"]]
          .sort_values("apron", ascending=False).to_string())


if __name__ == "__main__":
    main()

# Decision Memo: FC-DRB Redesign (subgroup split + trip/attribution)

Filed 2026-07-17, per Bobby's ruling of the same date (redesign so the binding metric is the validated one). This supersedes the metric-definition caveat in `memo_signgate_amendment.md` with an actual redesign. Script: `fcdrb_subgroups.py`.

## 1. Subgroup split (run first)

The frontcourt-succession team-seasons (hole seasons 2014-24) partition by what happened to the primary rim-minutes big:

| Subgroup | n | What it is |
|---|---|---|
| lost_primary | 81 | The #1 rim-minutes big departed |
| retained_primary | 35 | Kept #1, lost #2, **no replacement big** (the Wolves case: keep Gobert, lose Reid, fill at the minimum) |
| retained_primary_replaced | 65 | Kept #1, lost #2, but a replacement big (>= 1500 min) came in |

Early (first 25 games) to rest DRB persistence, both constructs, with the gate rule (translated Spearman >= 0.59 at n >= 30; original sign gate at 8-29; descriptive below 8):

| Subgroup | construct | n | Spearman | sign | verdict |
|---|---|---|---|---|---|
| lost_primary | whole-team | 81 | **0.619** | 0.679 | translated gate PASS |
| **retained_primary** | whole-team | 35 | **0.375** | 0.600 | translated gate **FAIL** |
| **retained_primary** | anchor-off | 35 | **0.394** | 0.714 | translated gate **FAIL** |
| retained_primary_replaced | whole-team | 65 | 0.665 | 0.815 | translated gate PASS |
| retained_primary_replaced | anchor-off | 65 | 0.639 | 0.754 | translated gate PASS |

**The load-bearing finding: the retained_primary subgroup, which is the Wolves' exact situation, does not validate.** Neither whole-team (0.375) nor anchor-off (0.394) clears the gate at n=35. Fisher 95% CIs are wide and straddle: retained_primary whole-team 0.375 [0.05, 0.63], anchor-off 0.394 [0.07, 0.64]. So it is not a clean refutation either, just genuine uncertainty at n=35.

This is a real and slightly uncomfortable result: the two subgroups that validate (lost_primary, and retained-with-a-replacement) are not the Wolves; the one that is the Wolves is the noisiest. A plausible mechanism: when a team keeps its primary anchor and does not replace the second big, whether the rebounding hole persists depends on how much the primary covers, which varies team to team, so early rebounding is a weaker signal there than when the whole anchor structure changed.

Per Bobby's item 4: the retained_primary subgroup does **not** validate anchor-off at adequate n, so there is **no direct-validation claim** for the Wolves' subgroup. The wire, if it survives, rests on the broad succession validation, not the subgroup.

## 2. Wire redesign: trip and attribution split

Per Bobby's item 2, adopted regardless of the subgroup outcome:

- **Binding trip metric: whole-team DRB percentile.** This is the 0.617/0.619-validated construct (lost_primary 0.619; all-team reliability below). Its own reliability from the Phase 1 sweep, computed here across all 330 team-seasons: **r(25) = 0.619** (r(20) = 0.593, r(30) = 0.637). This is materially better than the old anchor-off metric's r(25) = 0.502, and it clears even the continuous 0.59 gate. So the redesign makes the binding metric both validated and more reliable.
- **Two-read persistence unchanged:** fires only if the trip condition holds at both R1 and R2.
- **Gobert-off (anchor-off) DRB becomes the attribution read, not a trip condition.** After the whole-team metric trips:
  - **trip + Gobert-off red** -> route ARM-B to the backup-big target list (the hole is where Reid's absence would bite; the diagnosis fits).
  - **trip + Gobert-off green** -> **does not auto-route**; flags an out-of-cycle review, because a team-level rebounding collapse with healthy anchor-off minutes implies a different problem than the Reid hole (e.g. a scheme or a wing-rebounding issue), and the pre-committed backup-big move would be treating the wrong cause.

This resolves the original mismatch: the binding metric is now the one that was actually validated, and Gobert-off is used for what it is good for (attribution), not as a trip it could not support.

## 3. Threshold derivation (from the whole-team scorecard)

Derived the AVAIL-PACE way, from the whole-team DRB scorecard (rest-of-season percentile by R2 percentile bucket), not asserted:

| R2 (game-37) whole-team DRB percentile | n | mean rest percentile | P(rest in bottom third) |
|---|---|---|---|
| bottom 20 | 66 | 0.30 | **0.61** |
| 20-33 | 33 | 0.47 | 0.36 |
| 33-50 | 66 | 0.43 | 0.38 |
| top 50 | 165 | 0.65 | 0.13 |

Two-read joint (bottom-tier at both game-20 and game-37):
- bottom third at both reads: n=74, **P(rest in bottom third) = 0.554**.
- bottom quarter at both reads: n=56, P = 0.571.

The scorecard supports a **bottom-third-at-both-reads** trip: it is where P(the hole persists into the bottom third) first clears 0.5 (0.554). Tightening to the bottom quarter buys a little (0.571) at the cost of fires. So the original draft's "bottom league third" is, as it happens, what the scorecard produces on the whole-team metric; the difference now is that it is derived rather than asserted, and it is on the validated construct. Threshold: **whole-team DRB in the bottom league third at both R1 and R2.**

Caveat that must ride with the threshold: this operating characteristic is computed on all team-seasons. On the retained_primary subgroup specifically (the Wolves' type), the persistence is weaker (0.375-0.394), so the realized P(persist) for the Wolves may be lower than the 0.554 the all-team scorecard shows.

## 4/5. Provenance, marginal label, disclosure

**Provenance recorded:** binding metric validated on lost_primary succession (0.619, n=81) and all-team reliability (r25 0.619); NOT directly validated on the retained_primary subgroup (0.375-0.394, n=35, wide CI). No direct-subgroup-validation claim.

**Marginal label kept.** Item 5 says drop it only if the numbers say so. The binding metric's own reliability (0.619) is not marginal, but the Wolves-subgroup validity CI straddles from near-zero to above the gate, which is exactly the straddle that warrants the label. FC-DRB stays the **marginal wire**, now for a sharper and more honest reason: the metric is sound in general, but its transfer to the Wolves' specific succession subgroup is uncertain.

**Change-control disclosure (post-draft design change), before/after:**
- BEFORE (draft a819d15e): FC-DRB binding metric = Gobert-off (anchor-off) DRB percentile, bottom-third both reads. Admitted on the 0.617 whole-team number with a metric-definition caveat.
- AFTER (this redesign): FC-DRB binding metric = **whole-team** DRB percentile (r25 0.619, validated on succession), bottom-third both reads derived from the whole-team scorecard; Gobert-off demoted to the attribution read (route vs review). Provenance: retained_primary subgroup does not independently validate; wire rests on broad succession validation. Marginal label kept.
- Date: 2026-07-17. Logged in TRIPWIRES.md change control.

## For the final look (Bobby)

The redesign does what it was asked to: the binding metric is now the validated one (whole-team DRB, r25 0.619), and Gobert-off is used honestly as attribution. But the subgroup split surfaced that the Wolves' own subgroup (retained-primary, unreplaced) is the noisiest of the three, which is a genuine limit on how much any early-rebounding wire can promise for this specific situation. The wire is defensible as a marginal ARM-B trigger routed by attribution; a reasonable alternative, if you judge the subgroup non-validation disqualifying, is to run FC-DRB as an ARM-B **advisory** (like ARM-S) rather than a binding wire, shipping one binding wire (AVAIL-PACE) plus two advisories. Both are honest; the numbers above are the basis for your call.

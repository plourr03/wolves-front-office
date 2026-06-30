# Transport findings, 2026-06-25 (HALT before the sim)

Computed per `01_transport_framework.md`. Both guards held. The headline: the entire
LaMelo valuation hinges on the metric fork, and the fork divergence concentrates on
defense, exactly as the reviewer predicted.

## LaMelo transported net (the decision-relevant number)

| fork | raw net | A (0.75 on net) | B (0.75 on off, carry def) | B implied net-survival |
|---|---|---|---|---|
| RAPM | +1.95 | +1.46 [0.97, 1.75] | **+0.90 [-0.14, 1.53]** | 0.46 |
| box | +1.89 | +1.42 [0.94, 1.70] | **+1.41 [0.92, 1.70]** | 0.75 |

Under the recommended operationalization B (no double-count), LaMelo transports to
**+0.90 net under RAPM** (downside band reaching -0.14, i.e. replacement-ish) versus
**+1.41 under box**. The 0.5-point gap in his transported net is entirely the defensive
treatment. The box fork reproduces a net survival of 0.75, exactly Bobby's committed
prior; the RAPM fork is much harsher (0.46) BECAUSE it prices his defense. So the
committed 0.75 implicitly took a box-like, defense-neutral view of LaMelo.

## What MIN loses (Reid + Randle out)

| fork | Reid-out net lost | Randle-out net lost |
|---|---|---|
| RAPM | +3.27 | +0.44 |
| box | +0.87 | -0.02 |

Randle was near replacement either way (his marginal on-court value was always low,
even at a starter salary). Reid is the divergence: losing him costs +3.27 under RAPM
(a valuable two-way big) but only +0.87 under box. Most of that is his defense, which
RAPM values and box does not. So the "what we lose" side is far larger under RAPM.

## Gobert fragility (the term Bobby's prior is built around)

Defensive cliff = team defense lost per 100 when Gobert sits and the best available
backup-5 plays:

| fork | Gobert def | best backup-5 def | cliff |
|---|---|---|---|
| RAPM | +6.52 | +2.52 (Gueye) | **+4.00** |
| box | +1.02 | +1.87 (Beringer) | **-0.85** |

This is the starkest divergence and the most important. Under RAPM the team is
catastrophically Gobert-dependent on defense (a 4-point-per-100 cliff when he sits),
and losing Reid (a good backup-5 defender) makes the non-Gobert minutes worse, which is
precisely the amplified fragility prior. Under box there is NO fragility at all (the
backups defend fine). The two metrics tell OPPOSITE stories about whether the Reid +
Randle exits matter for depth.

Audit Fix 1 caveat: the +4.00 RAPM cliff is itself FLATTERED by the contested Gueye value.
The "best backup-5" in the RAPM column IS Gueye (+2.52 def), the same near-minimum throw-in
whose unreliable low-sample defensive RAPM also produces the team-strength "wash." Strip
Gueye out and the next-best backup is Beringer (+0.63 def), so the cliff WIDENS to +5.89.
So Gueye simultaneously makes the trade look like a wash AND makes the Gobert-fragility look
smaller; one unreliable number flatters both. The fragility is worse, not better, if Gueye
is valued reliably.

## Implications

1. The verdict will very likely DIFFER between the two forks. Under RAPM this is a
   modest-value, defensively fragile trade; under box it is a cleaner positive with no
   depth problem. Per the plan, if the verdict flips across defensible forks, that
   instability is the honest headline, not a number to cherry-pick.
2. The metric choice is load-bearing and concentrated on defense, LaMelo's exact risk
   and the fragility weakness. Carrying both forks (not anointing RAPM) was the correct
   call, and the YoY test could not distinguish them, so neither can be dismissed.
3. Bobby's committed 0.75 survival aligns with the box view. If RAPM is the better
   defensive measure, LaMelo's transported value is meaningfully lower than the prior
   implies (+0.90 vs +1.46), and the downside reaches replacement level.

## Guard verification

- Double-count guard held: under B the survival fraction hit OFFENSE only; defense was
  carried at the measured (metric-specific) level with NO additional playoff-defense
  multiplier. The center landing below +1.46 (RAPM +0.90) comes from carrying the full
  RAPM-priced defensive liability, not from penalizing defense twice.
- Defensive-divergence guard held: the fork divergence is reported on defense
  explicitly (LaMelo, Reid, the Gobert cliff), not averaged away.

## Open decision for the reviewer (HALT)

1. Operationalization A vs B. Recommend B (captures the off/def asymmetry in LaMelo's
   own net, lands below +1.46 honestly, makes the fork load-bearing where it should be).
2. Accept that the fork instability is a likely honest headline: the trade's on-court
   merit and the fragility depend on whether you trust RAPM or box on defense, and the
   data cannot adjudicate that at this sample.

Stops here, before the team-strength and sim layers, per the gate.

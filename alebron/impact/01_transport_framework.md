# Transport framework (pre-registered before computing transported values), 2026-06-25

Registered BEFORE the transport numbers are produced, per the discipline. Two guards
the reviewer required are baked in.

## Guard 1: watch defensive fork divergence (CONFIRMED on the raw, reported)

The box-prior RAPM and box-only BPM diverge on LaMelo almost entirely on DEFENSE
(net agrees at ~+1.9, but defense diverges by 2.2: RAPM -2.23 contribution vs box
-0.04). The same metric divergence makes the Gobert-fragility term metric-dependent
(RAPM rates Gobert +5.5 better on defense than box, the guards as negative defenders,
Reid as a valuable defender). So the fork is load-bearing on exactly LaMelo's risk and
the fragility weakness. This is reported as a finding, not averaged away.

## Guard 2: no double-counting of the defensive risk

The committed 0.75 survival fraction and any explicit playoff-defense adjustment must
not both price the same defensive risk. Resolution, pre-registered:

- The survival fraction is applied to LaMelo's OFFENSE (transport compresses offense:
  usage compression next to Edwards, leverage jump, role change). It is NOT applied a
  second time to defense.
- LaMelo's DEFENSE is carried at its MEASURED level under each metric. NO separate
  multiplicative playoff-defense haircut is stacked on. The playoff-defense risk is
  represented by (a) the metric itself (RAPM prices his defensive liability at -2.23;
  box hides it at -0.04), and (b) the survival fraction being below 1.0. It is priced
  ONCE. This is the double-count guard.

## Two operationalizations of the committed 0.75 (surfaced for the reviewer to pick)

Because Bobby committed "0.75 of measured impact survives" and the reviewer expects the
center to land below +1.46 without double-counting, there are two clean readings:

- **A (literal): 0.75 on NET.** transported net = 0.75 x raw net. The off/def split is
  an allocation; the defensive divergence shows up in the TEAM-defense aggregate, not in
  LaMelo's own net. Center stays at +1.46 (RAPM) / +1.42 (box). No double-count.
- **B (recommended): 0.75 on OFFENSE, carry measured defense.** transported net =
  0.75 x off + measured def-contribution. The defensive divergence shows up in LaMelo's
  OWN net (the forks diverge), and the center lands below +1.46 under RAPM honestly (the
  full, RAPM-priced defensive liability is carried, not haircut). No double-count.

Under B, the box fork reproduces a net survival of ~0.75 (consistent with Bobby's
prior), while the RAPM fork is harsher (~0.47 net survival) BECAUSE RAPM prices his
defense. That divergence is itself the finding: the committed 0.75 implicitly took a
box-like view of his defense.

## Departing and other imports

- Reid OUT and Randle OUT: no survival haircut (they were measured in MIN's context;
  MIN loses their measured impact). The fork divergence on Reid (RAPM +3.27 vs box +0.87,
  mostly defense) means losing him hurts far more under RAPM.
- Green IN and Gueye IN: carried near face value (role close to prior context), small
  transport. Reported under both forks.

The transported distributions feed the team-strength layer next; the reviewer halts
review here first.

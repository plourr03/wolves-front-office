# LeBron James to the Wolves: the locked evaluation (2026-07-03)

Status: LOCKED. This is the alebron project, a clean clone of the LaMelo evaluation
(`lamelo/`) applied to a NEW, verified-hypothetical question: LeBron James is a confirmed
2026 unrestricted free agent chasing "meaningful, competitive basketball," and the Wolves'
LaMelo trade is already done. What happens if he signs in Minnesota? Same engine, same
discipline, same identifiability gates. A precise title percentage is again DELIBERATELY NOT
published (the engine's star-acquisition retrodiction gate fails, and the point estimate
assumes an availability a 41-turning-42 body cannot guarantee). But the qualitative verdict
is the near-mirror-image of LaMelo's, and that contrast is the finding.

## The one-line finding

Adding LeBron is a **near-free, positive-leaning, ASYMMETRIC bet, the opposite risk profile
of the LaMelo trade.** The second-apron hard cap the LaMelo deal created permits him ONLY as
a veteran-minimum swap for an existing minimum body (the taxpayer MLE is literally illegal by
$1.9-4.0M). On the floor his marginal impact is reliably positive in BOTH defensive metrics
(a ~+1 net-rating add) because at zero asset cost he replaces a replacement-level body. And here
is the load-bearing result: the title delta stays **positive across the entire fit fork and the
whole age-and-availability sweep.** Unlike LaMelo (whose worst case was a real negative bought
with a mountain of picks), LeBron is very unlikely to HURT: the downside is truncated near zero
(he is benchable and cost nothing), while the upside tail (healthy + fit clicks) is a real +2
to +4pp deep-round bump. We still decline a single title number. But where LaMelo was
**wash-to-negative at enormous cost**, LeBron is **small-positive-to-good at almost none.**

## 1. Q0, the binding constraint: can they even sign him? (`data/cap_state.json`)

The LaMelo trade aggregated salary and HARD-CAPPED Minnesota at the second apron ($221.686M,
verified 2026-27 figure). After the completed trade plus the confirmed Ayo ($112M/5), Clark
(3/$10M) and Bones (1/$2.9M) re-signings, a legal 14-man roster already sits at **$219.62M, 
just $2.06M under the hard cap.** So:

| LeBron path | team salary | vs $221.686M hard cap |
|---|---|---|
| Veteran minimum, ADDED as a 15th body | $222.07M | **ILLEGAL, +$0.39M over** |
| Veteran minimum, SWAPPED for a minimum body | $219.97M | **LEGAL** (only ~$1.7M to spare) |
| Taxpayer MLE, added | $225.69M | ILLEGAL, +$4.0M |
| Taxpayer MLE, swapped for a minimum body | $223.59M | ILLEGAL, +$1.9M |

**LeBron fits only at the veteran minimum, and only as a minimum-for-minimum SWAP** (his
10+-year-vet cap hit on a one-year minimum is $2,449,421; the league reimburses the rest of
his $3,876,529). He is not additive, he is a substitution. The four-time MVP can join the
Wolves, if at all, only by taking the minimum AND bumping the 14th/15th man off the roster.
That is the whole Q0 story, and it is a striking one.

## 2. Q2, value decomposition (`impact/*`, `data/impact/*`)

- LeBron raw clean-room impact: net RAPM **+1.27** (off -0.18, def +1.45), box **+1.53** (off
 +1.32, def +0.21), reliable (28,286 poss). His RAPM offense is ~zero and his value is diffuse
 (defense + connective play), the opposite of LaMelo's offense-concentrated profile.
- Transport: because his value is diffuse and his source context (competitive, high-leverage
 playoff LA) already transfers, the LaMelo-style survival-on-OFFENSE is REJECTED (it would
 perversely raise a near-zero offense). Instead an **age-and-role retention factor on NET,
 center 0.80, band [0.55, 1.00]**, is applied, context transfer ~neutral, age-42 decline the
 dominant term. Transported net: **+1.02 [0.70, 1.27] RAPM, +1.22 [0.84, 1.53] box.**
- Marginal team-strength add (he displaces a replacement-level body, per Q0): **+0.88 raw / +0.94
 deflated (RAPM), +1.19 / +1.27 (box).** Reliably positive in BOTH forks, the first sharp
 contrast with LaMelo, whose RAPM add was ~0.
- Gobert fragility is UNCHANGED: LeBron is not a rim protector, so the defensive cliff when
 Gobert sits (still +4.00 RAPM) is neither opened nor closed by him.

## 3. The load-bearing fork: age × availability (`impact/sweep_lebron_availability.py`)

The contested number here, the analogue of the Gueye fork in the LaMelo audit, is LeBron's
age-42 per-minute retention TIMES his availability. Swept jointly, the raw team delta:

| retention (per-minute) | full (30 mpg) | reduced (20 mpg, misses games) |
|---|---|---|
| optimistic 1.00 (defies age) | +1.04 / +1.39 | +0.46 / +0.76 |
| central 0.80 | +0.88 / +1.20 | +0.36 / +0.63 |
| pessimistic 0.55 (cliff) | +0.68 / +0.96 | +0.23 / +0.47 |

(RAPM / box.) The delta is **positive in every cell**, even a declining, injury-shortened
LeBron beats the -1.5 replacement body he replaces. But the range is wide, and it is entirely
in the "small positive" band. Availability is the whole game: a 41-turning-42 body (sciatica
cost him the first 14 games of 2025-26; ~60 GP) sits where a healthier minimum player would
give 65-75. The point estimate below assumes he is roughly available; weight in the games he
will miss and the honest central bump is smaller.

## 4. Q2 sim, title and deep-round picture (CRN-paired, `data/sim/sim_results.json`)

| quantity | RAPM | box |
|---|---|---|
| post-LaMelo baseline P(title) | 2.66% | 3.92% |
| +LeBron P(title) | 3.90% | 6.11% |
| +LeBron reach-CF | 19.6% | 26.3% |
| +LeBron reach-Finals | 8.8% | 12.2% |
| CRN-paired title delta | **+1.24pp** | **+2.19pp** |
| CRN-paired reach-CF delta | +4.43pp | +7.02pp |

Structural band on the title delta (fork spread): **[+1.24, +2.19]pp**, positive in both
forks, does not cross zero. FIELD-ROBUST: re-running against a field updated for the biggest
verified 2026 moves (Jaylen Brown → PHI for an aging Paul George, Kawhi → TOR, Morant → POR,
etc.) moves the delta only to +1.21 / +2.15pp. The field changes the absolute odds, not the
delta, exactly as designed (the CRN pairing cancels field error).

## 5. The scenario shape (fit-clicks / neutral / fit-fails), the decisive result (`data/sim/scenario_table.json`)

The registered fit hypothesis is the THREE-INITIATOR problem: Edwards + Ball + James colliding
for on-ball reps with NO spacing added (LeBron ~31% from three, Reid/Randle already gone) and
LeBron hunted on defense, versus the upside of LeBron as the connective orchestrator/closer who
lets Edwards play off-ball and feeds Gobert. Title delta vs the post-LaMelo baseline:

| scenario | RAPM | box |
|---|---|---|
| fit_fails (-0.75 net) | **+0.28pp** | **+0.73pp** |
| neutral | +1.22pp | +2.15pp |
| fit_clicks (+0.75 net) | +2.49pp | +3.79pp |

**This is the finding.** The title delta stays POSITIVE across the entire fit fork, in both
metric forks. Compare LaMelo, whose RAPM fit-fails went NEGATIVE (-0.78pp title, -3.35pp
reach-CF). LeBron's downside is truncated at ~zero because he is a free, benchable minimum
swap: even a badly-fitting LeBron is marginally better than the replacement body he replaced,
and if it truly is not working, you play him 12 minutes instead of 30. The bet's left tail is
"a wash," not "a real negative." Its right tail (healthy + fit clicks) is a genuine +2.5 to
+3.8pp title bump and an +8 to +12pp swing in reaching the conference finals.

## 6. Q1, the decision grade: the mirror image of LaMelo

- **LaMelo (for context):** a near-zero on-court change bought with a 2033 unprotected first,
 three first swaps, three seconds, and a second-apron hard cap. A bad opportunity-cost bet even
 before the fit risk, the classic "spent the future for a wash."
- **LeBron:** ZERO assets surrendered. The entire cost is one roster spot and a $2.4M cap hit,
 and the downside is truncated (benchable, free). The expected on-court effect is a real small
 positive; the upside is a fun title-relevant tail; the only genuine risk is that a 42-year-old
 breaks down and the roster spot is wasted (a near-costless failure). **As a process decision,
 a minimum LeBron is defensible-to-smart**, cheap, asymmetric, optional. The one real
 opportunity cost is roster-mechanical: the swapped-out minimum body was likely to give 70
 reliable games, and LeBron might give 50 great-but-fewer ones, on an already thin,
 hard-capped, Gobert-fragile roster. That is a depth-vs-ceiling trade, not an asset disaster.

## 7. Why there is STILL no title percentage

Same discipline as LaMelo, honored even though the answer is more favorable:
1. **The engine's star-acquisition retrodiction gate FAILED again** (`sim/run_gates.py`,
 `run_case3.py`): 16 qualifying sealed-era star acquisitions, engine got 5/8 signs and 2/8
 within 4 wins on the power-8 subset. An additive engine cannot see fit or availability, the
 two things a 42-year-old LeBron's value hinges on most. Under the pre-registered kill criteria,
 a failed retrodiction means no published probability. (Calibration re-validation Gate 1a/1b
 PASS, series-frequency Case 2 PASS, the net-to-outcome machinery works; the star gate does not.)
2. **The point estimate assumes availability the model cannot guarantee.** The healthy +1.24 /
 +2.19pp shrinks materially once you weight the games a 41-turning-42 body misses (section 3).
 The availability tail is unmodeled at the point-estimate level; publishing +2pp would be false
 precision about a man who might play 45 games or 70.

So the honest band is **roughly [~0, +3.8pp], positive-leaning, downside-truncated**, reported
as a shape, not a point. What we CAN say cleanly: it almost certainly does not hurt, and it
plausibly helps a little, for free.

## 8. What we cannot resolve

- **WHETHER LeBron stays available** at 41-turning-42. The whole bet. A future fact.
- **WHETHER three alphas fit** with no added spacing. The fit-fails/clicks fork is real and
 reality-graded (prediction 4 below).
- **A PRECISE title percentage**, declined on the failed engine gate and the unmodeled
 availability tail, per the house discipline.
- **A field discrepancy carried forward:** the inherited baseline assumes Donte DiVincenzo is
 OUT for 2026-27 (Achilles), but 2026 reporting lists him in the projected core. Flagged, not
 silently resolved; it moves MIN's absolute level, not the CRN-paired LeBron delta.

## 9. Public-translation rule (the caption inherits the error bars)

The honest public frame: "We ran the same championship model on a fun what-if, LeBron, a real
free agent, signing with the Wolves. First surprise: the LaMelo trade hard-capped them so tight
that the GOAT fits ONLY at the minimum, and only by cutting the 15th man. Second: unlike the
LaMelo swing, this one basically can't backfire, he cost nothing and you can bench him, so the
model has it as a small, one-sided plus, a real couple-point bump if he's healthy and it clicks,
and a wash if it doesn't. We won't hand you a title number: the model's own track record on star
additions is shaky, and nobody can promise a 42-year-old plays 70 games. But as a near-free dice
roll with the downside capped, it's the opposite of the LaMelo bet, that one spent the future
for a wash; this one risks almost nothing for a taste of a ceiling."

## 10. Forward predictions (the immutable log; reality grades these)

| # | prediction | point | band | grade date |
|---|---|---|---|---|
| 1 | LeBron signs somewhere on a minimum or MLE-tier deal (not a max) | true |, | 2026-10-01 |
| 2 | IF he signs with MIN: LeBron games played | 55 | [38, 68] | 2027-04-15 |
| 3 | IF he signs with MIN: Wolves 2026-27 win total | 51 | [44, 56] | 2027-04-15 |
| 4 | IF he signs with MIN: Edwards+Ball+James three-on-court net | +2.0 | [-4, +8] | 2027-04-15 |
| 5 | IF he signs with MIN: reach the conference finals | ~22% (model) | one-shot | 2027-06-30 |

Prediction 4 settles the fit fork the model cannot: near +8 is the fit-clicks world, near -4 is
the three-alpha collision. Predictions 3 and 5 are above-model analyst priors where noted; the
model's own net-to-wins puts the +LeBron team around 48-50 wins.

## Decisions locked

- Publish the qualitative finding, the cap-feasibility headline, and the scenario shape. Do NOT
 print a title percentage (failed star-acquisition gate + unmodeled availability tail).
- The deliverable is the CONTRAST: LaMelo was wash-to-negative at a mountain-of-assets cost;
 LeBron is small-positive-to-good at almost none, with a truncated downside and an availability
 gamble as the only real risk. The hard cap the LaMelo deal created is what makes a minimum the
 only door.

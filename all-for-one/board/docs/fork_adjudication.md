# Fork Adjudication: Pre-Registered Update Rule (rapm vs box)

Pre-registered 2026-07-17, for the ONE FOR ALL board. **Freezes with the October 20, 2026 freeze; the functional form, the evidence read, and the permitted fire dates below are fixed now, before the season provides any evidence.** This is the mechanism that decides, as real games arrive, which of the two metric forks the board should weight, so the fork disagreement is resolved by the season rather than by preference.

## The two forks, on the record

The board carries two first-class projections of MIN's post-trade team net (2026-27), from the reconciled Joan Bet run:

| Fork | projected MIN net | ~wins | title equity |
|---|---|---|---|
| rapm | **+1.50** | ~44 | 1.94% |
| box | **+2.94** | ~48 | 3.81% |

These are the pre-registered projections. Everything below reads realized results against them.

## Evidence read

The evidence is MIN's **realized team net rating**, opponent-adjusted, measured at two pre-committed reads that coincide with the tripwire read dates:

- **R1**: through approximately game 17-20 (late November 2026).
- **R2**: through approximately game 36-39 (mid January 2027).

The realized net is the team's point differential per 100 possessions from `nba_team_advanced_stats`, adjusted for strength of schedule (opponent net) so an easy or hard early slate does not masquerade as fork evidence. It is a descriptive team-strength read, not a causal claim.

## Functional form

A pre-registered Bayesian update on a two-hypothesis space {rapm, box}, with a prior and a Normal likelihood whose width is the early-season sampling noise of team net.

Let `n_R` be the opponent-adjusted realized net at read R, and `proj_f` the fork's projected net (1.50 rapm, 2.94 box). The likelihood of the observation under each fork is

```
L(n_R | f) = Normal(n_R ; proj_f , sigma_R)
```

where `sigma_R` is the standard error of a team's net over R games, pre-committed by sample size (it shrinks from R1 to R2 as the sample grows):

```
sigma_R1 = 3.0   (through ~18 games)
sigma_R2 = 2.2   (through ~37 games)
```

(These SEs are pre-registered TUNE values, sized from the historical spread of team net over the first N games; they may be refined before the freeze but not after, and never in response to a realized read.) The posterior fork weight is the normalized prior-times-likelihood:

```
w_box(R) = [ prior_box * L(n_R | box) ] / [ prior_box * L(n_R | box) + prior_rapm * L(n_R | rapm) ]
w_rapm(R) = 1 - w_box(R)
```

**Prior**: `prior_box = prior_rapm = 0.5` (the run enters agnostic between the two metrics). Bobby may set a different prior before the freeze; it is logged if so.

**Recommendation on the prior (logged 2026-07-17).** The recommendation is that **0.5/0.5 stands at the freeze**, for credibility. An agnostic prior is the strongest public position: it lets the season's realized reads do the adjudicating, and it forecloses the objection that the shop tilted the metric toward the answer it wanted before a single game was played. A 50/50 prior is the one nobody can accuse of curation. Bobby may override before October with a logged justification, per this rule's own anti-tuning terms; absent that override, the freeze carries 0.5/0.5.

**RULING (Bobby, 2026-07-17): 0.5/0.5 confirmed for the freeze.** Bobby confirmed the agnostic recommendation. The freeze carries `prior_box = prior_rapm = 0.5`, closed.

The board then reports every downstream number as the fork-weighted blend `w_rapm * X_rapm + w_box * X_box` at the current read, in addition to the standing full range. Between reads the weights hold.

## Permitted fire dates

The weights may be updated **only at R1 and R2** (and at the October freeze, to set the prior). No intra-window updates: a two-game losing streak in December does not move the fork weight, because the read dates are pre-committed exactly to prevent that. This mirrors the tripwire discipline (a wire fires only at its read date) and the SIGN_GATE / SALVAGE_CAP anti-tuning rule (a parameter is not revised to change an output).

## What a fire does, and does not, do

A fire re-weights the forks and re-reports the blended board. It does **not** discard the losing fork: both stay first-class and the full range is always shown, because a single season's ~37 games cannot certify one metric over the other, only tilt the weight. A read that lands between the two projections (e.g. realized net +2.2) leaves the weight near the prior and is reported as inconclusive, not forced.

## Falsifiable, on the record

The projections (1.50, 2.94), the SEs (3.0, 2.2), the prior (0.5/0.5), the evidence (opponent-adjusted realized net), and the fire dates (R1 ~game 18, R2 ~game 37) are all fixed here. In February 2027 the piece can show the realized reads against the pre-registered projections and the weight they produced, with no retrofitting. The commit history is the proof.

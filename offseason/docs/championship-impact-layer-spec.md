# Championship Impact Layer: Specification

_A layer on top of the existing acquisition metric. The acquisition metric answers "is this player a good fit we can afford." This layer answers "how much does this move raise our chance of winning a championship, and our chance of beating the specific teams in our way." It does not replace the metric. It extends the one-page profile with a championship read._

---

## What it answers

For a given trade scenario, three things:

1. **Title equity.** How much the move changes the Wolves' simulated probability of winning the championship, reported as a range, before and after.
2. **The gauntlet.** How much the move changes the Wolves' series-win odds against each real contender (Spurs, OKC, Knicks, and the rest of the title-path field), reported per opponent. This is the substance, and it is more tractable and more communicable than the single title number.
3. **The honest verdict.** A holistic championship tier that sits next to the existing fit verdict, with the soft factors handled in the open rather than buried.

---

## Design principles (these are load-bearing, build them in from the start)

- **No false point estimate.** Title equity is a tiny, noisy target with one champion a year. Every headline number is a range with an interval, never "plus 4.2 percent." If the code is ever tempted to print a single title-odds figure with no band, that is a bug.
- **Playoff-weighted, not regular-season.** Titles are won in May. The team ratings and the sim up-weight playoff-translating skills (half-court shot creation, rim protection, switchability, half-court defense) and tighten the rotation the way real playoff rotations tighten. Regular-season point differential is not the target.
- **Trades are two-sided.** The player you send out lands on a real team. The sim re-rates both rosters, not just the Wolves', because if the outgoing player lands on a contender you would face, you got worse and they got better at the same time.
- **The league is an explicit, stress-testable snapshot.** You cannot predict 29 offseasons. Hold the league at a documented best-estimate post-offseason state, get the contenders right, and stress-test the few rival moves that would actually swing the number rather than pretending to know them all.
- **Quantify what is quantifiable, flag the rest in the open.** Availability, playoff track record, and usage overlap are partly measurable and modify the expected value and the band. Locker room, ego, and coachability are judgment, so they live as visible flags with written reasons, never as a fabricated number.
- **The championship lens is not the fit lens.** The cleanest-fit move may add little title equity, and the move that raises the ceiling most may be a high-variance swing that hurts the floor. Always show both the floor (regular-season fit) and the ceiling (title equity) so the divergence is visible. The divergence is the point.
- **The feasibility gate stays the gate.** A move that raises title odds but cannot be legally made is still a no. The gate runs first; infeasible scenarios are not simulated.

---

## Relationship to the existing pipeline

This layer consumes, it does not rebuild:

- **From the value layer:** per-player offense and defense RAPM with posterior intervals, and the playoff read.
- **From the need layer:** the six-dimension structural profiles (used both for the Wolves' resulting roster and for opponent scouting).
- **From the feasibility gate (`evaluate_move.py`):** the legal-match check and the exit-scenario context. The gate runs first. Only feasible (or stretch) scenarios proceed to simulation.

The new modules below are the only genuinely new builds.

---

## Components

Suggested module names mirror the existing pipeline (`build_rapm.py`, `build_need_layer.py`, `acquisition_metric.py`).

### A. Team-rating rollup (`build_team_ratings.py`)

**Purpose:** turn a roster of players into a team strength.

**Inputs:** per-player offense and defense RAPM with intervals, projected minutes (from B), the playoff-weighting toggle.

**Method:** aggregate player ratings weighted by projected minutes into team offensive and defensive ratings, then a net team strength. Produce two modes: a regular-season rating (used for seeding in the sim) and a playoff rating (rotation tightened, playoff-translating skills up-weighted, weak-link minutes reduced the way they get hunted in a series). Carry the RAPM intervals through into a team-strength distribution, do not collapse to a point.

**Output:** a team-strength estimate with an interval, in both modes, for any roster configuration.

**Honesty note:** the playoff reweighting is a defined, documented transform, not a knob to be tuned until the Wolves look good.

### B. Rotation and redundancy model (`build_rotation_model.py`)

**Purpose:** the bridge from "a player" to "a team." A player's value depends on who he replaces and how he fits.

**Inputs:** roster, positions, the dimensional profiles, baseline minutes.

**Method:** construct the projected rotation (starters plus key reserves), assign minutes, identify who the new player displaces, and apply fit and redundancy adjustments. Redundancy is a modest penalty for stacking similar skills (two non-shooters, two ball-dominant guards). Complementary fit is a modest bonus (spacing around a slasher, a rim protector behind a gambling perimeter defender). Lineup-level, not strictly additive.

**Output:** the post-trade minutes distribution and a fit and redundancy adjustment that modifies the naive minutes-weighted rating from A.

**Honesty note:** fit and redundancy effects are bounded and grounded in structural factors. They are not free parameters.

### C. Opponent and contender scouting profiles (`build_opponent_profiles.py`)

**Purpose:** characterize the teams you have to beat so series can be resolved on more than overall rating.

**Inputs:** value layer and dimensional profiles applied to each contender's projected post-offseason roster.

**Method:** build a structural profile for each real contender. How they generate offense, what their defense takes away, their rim protection, their switchability, where they crack. Plus their overall team strength from A. Build detailed profiles for the roughly eight to twelve real title-path contenders. Treat the rest of the league coarsely with overall ratings only.

**Output:** a per-contender profile plus team strength, used by D.

### D. Matchup-adjusted series resolution (`series_resolver.py`)

**Purpose:** the probability one team beats another in a series, accounting for style.

**Inputs:** two teams' strengths and structural profiles, home-court.

**Method:** a base series win-probability from the strength differential (logistic on the net-rating gap, with home-court), then a bounded matchup adjustment built from the structural interaction. Examples: your half-court-offense weakness times their half-court-defense strength pushes the number down, your rim protection against their rim pressure adjusts it, a three-point-variance term widens the series even when the mean favors you. The matchup term is capped (a few percentage points on series win-probability, the exact cap is an open decision) so it informs the number without overwhelming the strength signal.

**Output:** P(win series) for any pairing.

**Honesty note:** the matchup term is built only from repeatable structural factors, not from small-sample "Team X always beats Team Y" lore, which is where matchup modeling usually goes to die. Keep it modest and documented.

### E. Playoff and bracket Monte Carlo (`bracket_sim.py`)

**Purpose:** the headline title equity and the opponent distribution.

**Inputs:** all team strengths for the snapshot league, the series resolver D.

**Method:** simulate the regular season from the ratings, derive seeds, build the bracket, resolve and advance each series through D, crown a champion. Run N times (start at 10k, runtime permitting). Run the whole thing twice: the pre-trade league and the post-trade league, where post-trade means the Wolves updated and the counterparty updated (from F).

**Output:**
- Title probability for the Wolves, pre and post, with intervals. This is the headline ΔP(title), reported as a range.
- Round-advancement probabilities.
- The opponent distribution (who you faced at each round, emergent, not pre-assigned) and the per-contender series-win deltas pre to post. This is the substance.

### F. Two-sided trade application (`apply_trade.py`)

**Purpose:** apply a trade to the league correctly, both halves.

**Inputs:** a trade scenario: outgoing players including filler, incoming player, the counterparty's identity, and the counterparty's return.

**Method:** update the Wolves roster (remove outgoing, add incoming) and the counterparty roster (remove what they send, add what they get). Re-rate both teams via A and B. Hand both updated rosters to E.

**Modes:** "full" models the counterparty, "one-sided" models only the Wolves and flags the omission. Default to full whenever the outgoing player would plausibly land on a contender, since that is exactly when the counterparty effect is first-order. One-sided is acceptable for a quick pass or when the counterparty is a lottery team you will never meet in a series.

**Note:** this needs a richer input than the acquisition metric's "send out salary, get player Y." It needs who and what-back. See open decisions on how to source the counterparty return.

**Benefit worth calling out:** because E simulates the actual resulting roster, this layer naturally handles the companion-move problem the acquisition metric could only flag with an asterisk. Feed it "wing plus rim protector" as the resulting both-out roster and it values the pair as one team, instead of a target plus a contingency note. That subsumes the target-pair question into the sim.

### G. Risk and intangibles overlay (`risk_overlay.py`)

**Purpose:** the soft factors, handled honestly.

**Quantifiable (modify the expected value and widen the band):**
- Availability and durability, from games-missed rates and an age curve.
- Playoff track record, from playoff-versus-regular-season splits and series experience.
- Usage overlap with Edwards, from usage rates, on-ball share, and on-off.

**Judgment flags (green, yellow, red, each with a written reason):**
- Locker room and culture, ego and role acceptance, coachability, contract-year and motivation dynamics.

These are visible flags, not numbers. A flag can cap the championship tier or drop it, but it never silently subtracts a fabricated percentage. A red flag caps the tier regardless of the simulated number.

**Output:** an adjusted impact band plus a flag panel, with the measured factors and the judged factors clearly separated so the reader always knows which is which.

---

## The output: the Championship Impact Profile

The layer extends the existing one-page profile. For each trade scenario it adds:

- **Feasibility** (from the gate): exit scenario, legal match including filler, apron and Dosunmu status. Unchanged, runs first.
- **ΔP(title):** range, pre to post, with interval. The headline.
- **Per-contender series-win deltas:** versus each real contender, pre to post. The substance, and the part that answers "who helps us beat the Spurs."
- **Floor versus ceiling:** the regular-season fit read (from the acquisition metric) next to the title-equity read, so the divergence is visible. This is the best-case view.
- **Two-sided note:** counterparty modeled or not, and the size of the counterparty effect if modeled.
- **Risk and intangibles panel:** the quantified adjustments and the judgment flags, kept separate.
- **League snapshot and stress test:** the assumed league state, and how ΔP(title) moves under the one or two rival-move variants that would actually swing it.
- **Championship tier:** a holistic, hedged verdict, not a single number. Something along the lines of raises the ceiling materially, marginal, or lifts the ceiling but lowers the floor, with the reasoning attached.

---

## Validation and sanity checks (do these, they are how we stay honest)

- **Baseline title odds must be believable.** The pre-trade title odds for known teams should roughly track betting markets and public models. If the sim says the defending champs are at 3 percent or the Wolves are at 25, something is broken in A, D, or E.
- **The series resolver should reproduce history.** Series win-rates by seed and by rating gap should roughly match the historical record. Calibrate before trusting D.
- **Marginal additions should move the needle marginally.** Adding a backup guard should not add 5 percent to title odds. If it does, the rollup is too sensitive.
- **Intervals are expected and reported.** A tight title-odds number is a red flag, not a triumph.

---

## Build order

1. Team-rating rollup (A) and rotation model (B). Validate by reproducing current team ratings and standings.
2. Opponent profiles (C) for the contenders.
3. Series resolver (D). Validate against historical series outcomes and market series odds.
4. Bracket Monte Carlo (E). Validate the baseline title odds against public models.
5. Two-sided application (F).
6. Risk and intangibles overlay (G).
7. Profile assembly and tier.

The dependency that matters: nothing downstream is trustworthy until A, D, and E pass their sanity checks. Resist the urge to run trade scenarios before the baseline is calibrated, because a miscalibrated baseline makes every delta meaningless.

---

## Open decisions for you

1. **Matchup-term cap.** How much can style move a series, at most? I would start conservative (a few points of series win-probability) and loosen only if the resolver underfits known matchups.
2. **Sourcing the contenders' projected rosters.** Use the block board plus reported and likely moves, documented as the snapshot. The question is who signs off on the assumed moves. I would default to a documented best estimate plus stress-test variants for the consequential ones.
3. **Counterparty returns for the two-sided model.** For hypotheticals, do we hand-specify the return, or auto-generate a fair-value return from the comp and asset model? I would hand-specify for now and let the asset model suggest returns later.
4. **Who sets the judgment flags.** This is your scouting call, documented. The rule to lock in: a red flag caps the tier no matter how good the number looks.
5. **Compute.** N sims and runtime, since running the full bracket twice per scenario across a slate adds up.

---

## What this is not

It is not an oracle and it does not print a precise title-probability truth. It is a structured, honest decision aid that quantifies what can be quantified, is transparent about what cannot, and shows the ceiling next to the floor. It informs the call. It does not make it for you.

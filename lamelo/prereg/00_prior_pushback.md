# Prior pushback, data-grounded (before lock)

Date: 2026-06-25. Author: build agent. Status: feeds the pre-registration. Bobby
committed his priors cold; this memo pushes back where the data says a prior reads
too kind or too harsh to the team, and proposes the one number (Ant-LaMelo on/off)
he delegated. Nothing here is a verdict on the trade. All figures are from the
2026-06-25 warehouse freeze (see `freeze_manifest.md`).

## The evidence

### LaMelo availability (the anchor for the games-played prior)

Regular-season games played, from `nba_player_stats` joined to `nba_games`:

| Season | GP | MPG | PPG | APG | on-court net |
|---|---|---|---|---|---|
| 2020-21 | 51 | 28.3 | 15.7 | 6.1 | -3.2 |
| 2021-22 | 75 | 31.8 | 20.1 | 7.6 | +1.5 |
| 2022-23 | 36 | 34.7 | 23.3 | 8.4 | -4.7 |
| 2023-24 | 22 | 31.8 | 23.9 | 8.0 | -8.5 |
| 2024-25 | 47 | 31.5 | 25.2 | 7.4 | -3.9 |
| 2025-26 | 72 | 27.5 | 20.1 | 7.1 | +9.1 |

Career GP mean 50.5. Last four seasons mean 44.25. Recency-weighted (the plan's
risk_overlay 0.2/0.3/0.5 on the last three seasons) is about 54.5 games. Two of
the last four seasons were under 40 games (ankle, including multiple surgeries in
2023-24). The most recent season is a real rebound: 72 games, but at his lowest
non-rookie minutes (27.5), so it was a managed 72.

### On-court impact and the comp class (the anchor for survival fraction and on/off)

LaMelo's 2025-26 on-court net was +9.1 with a 123.2 offensive rating on the floor,
his strongest impact season. Edwards' on-court net the last three seasons: +7.3,
+4.8, +3.5 (mean about +5.2). Reference class of analogous high-usage two-guard or
guard-plus-wing duos, recent healthy seasons, individual on-court net as a proxy
(team-quality confounded, directional only):

| Duo | Season | on-court nets | read |
|---|---|---|---|
| Mitchell + Garland (CLE) | 2024-25 | +10.4, +9.8 | elite-team success |
| Doncic + Irving (DAL) | 2023-24 | +5.7, +6.9 | Finals-team success |
| Morant + Bane (MEM) | 2022-23 | +7.3, +8.9 | success when healthy |
| Young + Murray (ATL) | 2023-24 | -2.6, -2.8 | two-guard fit FAILED |
| Booker + Beal (PHX) | 2024-25 | -3.2, -8.0 | two-guard fit FAILED |
| Fox + DeRozan (SAC) | 2024-25 | -1.2, +1.5 | underwhelmed, ~neutral |

The class splits hard: elite-team duos land +5 to +10, the cautionary
two-ball-dominant-guard fits land -3 to +2. The decisive differentiator is that the
failed fits (ATL, PHX, SAC) had no rim anchor behind the guards, while the Wolves
have Gobert. That backstop is why Edwards-LaMelo should sit above the failed comps,
and LaMelo's defense plus the usage collision is why it should sit below the elite
comps.

## Pushback on the committed priors

**Prior 1, Jrue-type alternative: no pushback on substance, one definitional
tightening.** The asset-matching logic (same lead-creator need, plausibly available
then for a similar or smaller package, past-tense decision-point framing) is sound.
Tighten only this: register it as an ARCHETYPE (a veteran lead ball-handler
acquirable for a mid-tier package at the decision point), not literally Jrue
Holiday, so the counterfactual is not hostage to one player's 2026 status.

**Prior 2, survival fraction 0.75 [0.60, 0.90]: center is data-supported, NOT too
kind.** I will not manufacture a pushback here. His most recent and healthiest
season shows a strongly positive on-court impact (+9.1), so 0.75 of his transported
impact is defensible and arguably even conservative if you weight 2025-26 heavily.
Two refinements, not a center change: (a) the downside band could extend modestly
below 0.60 (toward ~0.50) because his pre-2025-26 seasons posted negative on-court
net and playoff defenses will hunt a lead guard, and his efficiency at COMPRESSED
usage next to Edwards is the genuine unknown; (b) per Bobby's own instruction, the
Gobert-ceiling-raise (rim pressure, lob gravity) is an UPSIDE fit scenario only, so
register the SYMMETRIC downside too (LaMelo's point-of-attack defense hunted in the
playoffs, dragging Gobert into space or forcing switches) as the fit-fails scenario,
keeping the fit term symmetric as the plan requires.

**Prior 3, Reid-out cost (impact plus fragility): well-specified, one modeling
note.** Registering both parts is correct and the easy thing to undercount. Model
the fragility part as a VARIANCE widening on the Gobert-availability shared factor
in the dependence structure (section 8), not as a mean haircut, so it shows up in
the tail where it actually bites (the stretches Gobert misses), which is where the
regret term lives.

**Prior 4, forward predictions: the games-played FLOOR and the coupled win FLOOR
are too kind.**

- LaMelo games played, committed 63 [52, 72]. The center of 63 is acceptable: the
  72-game 2025-26 rebound and the upward trend (22, 47, 72) support it, and it sits
  above the recency-weighted 54.5 for a forward-looking reason (the ankle looks more
  stable). But the FLOOR of 52 is too kind. His own last four years include 22 and
  36 game seasons; a band that bottoms at 52 prices out the ankle-recurrence tail
  entirely, and that tail is exactly what the catastrophic-regret term in the
  objective exists to capture. Recommend widening the band down to roughly [44, 73],
  keeping the center near 60 to 63. The reviewer's warning was specifically about
  this number, and the data agrees.
- Win total, committed 54 [50, 58]. The center of 54 is at the optimistic-but-
  defensible edge: it is conditional on the survival fraction and games played both
  landing near their (optimistic-edge) centers, so it should be labeled a
  health-and-fit-clicks central case. The FLOOR of 50 is too kind because it is
  coupled to the games-played floor: if LaMelo plays into the low 40s (the
  recurrence tail), the team almost certainly wins fewer than 50. Recommend widening
  the band down to roughly [46, 58] so the win floor and the GP floor move together.
- Final seed 4 [3, 5]: internally consistent with a 54-win central case. No
  pushback, though it inherits the same upside-conditionality as the win total.

## Proposed: Ant-LaMelo on-court net (the number Bobby delegated)

This forward prediction is graded on the 2026-27 net rating of lineups with both
Edwards and LaMelo on the floor. Anchors: Edwards' own three-year on-court net about
+5.2; the Wolves' recent team net about +4 to +5; the comp class above splitting
between elite-duo success (+5 to +10) and two-guard fit-failure (-3 to +2); the
Wolves placed above the failed comps by Gobert's backstop and below the elite comps
by LaMelo's defense and the usage collision.

- **Proposed center: +3.0. Proposed 80% band: [-2.0, +8.0].**
- The band is deliberately wide and spans the two halves of the comp class: the low
  end (-2) is the fit-fails, defensively-hunted outcome near the cautionary comps;
  the high end (+8) is the fit-clicks, offensive-ceiling outcome near the elite
  comps. A two-man on-court net is a noisy quantity, so the wide band is honest.
- This is a reference-class-anchored PROPOSAL for Bobby to accept or adjust before
  lock. The precise two-man net and the usage-collision interaction get computed in
  the interaction layer (plan section 5), and this prediction is what that
  computation will be graded against.

## Items requiring Bobby's decision before the pre-registration locks

1. LaMelo games-played band: widen the floor (recommend [44, 73], center ~60 to 63).
2. Win-total band: widen the floor to move with GP (recommend [46, 58]).
3. Ant-LaMelo on/off: accept or adjust the proposed +3.0 [-2, +8].
4. Survival fraction: keep [0.60, 0.90] or widen the downside toward 0.50 (optional).

Everything else (Jrue archetype framing, survival-fraction center, Reid-out two-part
cost) is registered as committed.

## Resolution (2026-06-25)

Bobby resolved all four: games played widened to [44, 73] (center 63 held); win total
widened to [46, 58] (center 54 held); on/off accepted at +3.0 [-2, +8]; survival floor
extended to 0.50 (center 0.75 held). He also registered the secondary-creator unlock as
a named hypothesis with its symmetric hedge. The pre-registration is LOCKED.

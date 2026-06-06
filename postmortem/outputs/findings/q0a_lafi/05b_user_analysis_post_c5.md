# User analysis: Phase 2 synthesis and four-act Edwards-era narrative

**Date:** 2026-05-16
**Author:** Bobby
**Context:** All five LAFI components complete. Reading the trajectory and the cross-component pattern.

## The headline artifact of Phase 2 is the trajectory table

```
                  2022-23  2023-24  2024-25  2025-26
C1 Stickiness        14      34       68       30
C2 Motion Death      63      43       55       71
C3 Iso Reliance      43      49       70       89
C4 Action Poverty    30      27       35       45
C5 Shot Quality      46      39       71       82
```

This is the most important thing we have produced. It tells a four-act story.

## The four-act narrative

**Act 1: 2022-23, the Gobert integration year.** Moderate stickiness (low, 14), high motion death (63), moderate iso (43), low action poverty, moderate shot quality. The defining feature: motion died early in the Gobert era because the offense hadn't figured out how to play with him. They were already a "bodies don't move" team but not yet an iso team.

**Act 2: 2023-24, the WCF breakthrough.** Every metric improved or held. Stickiness rose slightly (34, Ant became more central) but motion came back (43), iso stayed contained, shot quality was the best of the era (39). This was the most designed version of the offense and it produced the deepest playoff run of the Edwards era. **The data validates that 2023-24 was the high-water mark not just in record but in offensive structure.**

**Act 3: 2024-25, the Randle integration.** The most diagnostic year. Stickiness jumped to 68 (Randle dominated possessions early as the team figured out how to use him). Motion died slightly (43 to 55). Iso jumped (49 to 70). Shot quality cratered (39 to 71). They reached the conference finals but the offense was already structurally different. The story Scott and I both told (offense feels off, team got there anyway) is exactly what the data shows: a Q3-leaning team that still had enough talent to win two rounds.

**Act 4: 2025-26, the Q4 collapse.** Stickiness fell back (Randle no longer dominating, possessions decentralized to 30). Motion died worse (71). Iso reached extreme (89). Action allocation got worse (45). Shot quality continued its decline (82). They became the distributed-iso, dead-off-ball team we have been diagnosing.

**The four-act story is what the writeup should anchor on.** Not "the Wolves are bad now." Rather: "the Wolves had a designed offense in 2023-24 that worked, then lost it in two stages, and the second stage was worse than the first." That is a story a front office will actually read.

## The C2, C3, C5 lockstep is the real LAFI

Three components, three identical-shaped curves, all rising sharply across the last three years:

- C2 motion death: 43 to 55 to 71
- C3 iso reliance: 49 to 70 to 89
- C5 shot quality decay: 39 to 71 to 82

That is not three independent measurements of three different things. That is three different surfaces of the same underlying pathology.

The underlying pathology in plain language: **when the offense doesn't move bodies, it falls back on iso, and the iso produces bad shots.** The three components are the cause, the symptom, and the consequence of the same disease.

- Motion death is the cause (no advantage creation).
- Iso reliance is the symptom (someone has to do something, so they iso).
- Shot quality decay is the consequence (the iso produces bad shots because the defense was set).

This is also a methodological observation. The spec was worried about component redundancy (Section 3.4: "no two components should correlate above 0.80"). For these three components on the Wolves specifically, the correlation is going to be very high. Phase 3's correlation matrix will tell us whether this is Wolves-specific or league-wide.

**If C2, C3, C5 correlate above 0.80 league-wide, do not drop or merge components.** A high correlation does not mean redundancy; it means motion-death, iso, and bad shots travel together in NBA offenses. That is a real basketball finding, not a measurement artifact.

## The Wembanyama hypothesis got a structural confirmation

The Spurs landed at 11th percentile on shot quality decay. They have one of the best, cleanest, highest-quality shot diets in the league. Pair that with their elite rim protection (Wembanyama) and switchable perimeter defenders.

So when the Wolves play the Spurs, the matchup is:

- Wolves: 82nd percentile shot quality decay (bad shot diet)
- Spurs: 11th percentile shot quality decay (good shot diet)

A 71-percentile-point gap. The Spurs are not just defending the Wolves better; they are winning on both ends structurally. **The Spurs are the team most structurally opposite to the Wolves in the entire league on the dimensions we have been measuring.**

The deeper observation: SAS at 14 on action poverty (broad playbook), Wolves at 45. SAS at 11 on shot quality, Wolves at 82. We'd need C1-C3 to confirm but the pattern looks consistent.

This means the second-round loss is not bad luck or a hot opponent. It is the Wolves running into the team architecturally best-equipped to beat them. If they had drawn a different second-round opponent (say, the Lakers, with similar pickup-ball tendencies), the series might have gone very differently.

## Calibration scorecard at 50%

50% accuracy across 22 priors. Exactly random.

What this means:

- I was good at qualitative direction (Wolves will be elevated on these dimensions).
- I was bad at quantitative magnitude (how elevated, which dimension specifically).
- I was good at structural archetype calls (GSW will be designed, LAC will be sticky).
- I was bad at Wolves-specific magnitudes (over-predicted action poverty, over-predicted stickiness).

Going forward I should:

1. Trust my qualitative pattern recognition.
2. Discount my specific-magnitude predictions.
3. Listen harder when the data surprises me, because I am not better than a coin flip on quantitative calls.

My 50% prior accuracy is actually a good record for advisors; analytics history is littered with strategists who were confident and wrong.

## Thesis revision: composite of 61 is not what the original thesis predicted, and that matters

- Original thesis: Wolves are extreme LA Fitness team, top 5 in the league.
- Data: Wolves land around 61st percentile on the composite, probably 8th-12th in the league.

This is a thesis revision, not a thesis failure. Here is why it is better, not worse, for the final deliverable.

A "Wolves are top 5 on LAFI" finding would be punchy but it would invite the response: "OK, but Brunson Knicks are top 5 too and they're contenders. So what?"

The data refutes the simple thesis and replaces it with something more diagnostic.

**The new thesis: The Wolves are not extreme on LAFI overall, but they are extreme on the three components of LAFI that specifically predict playoff offensive collapse: motion death, iso reliance, and shot quality decay.**

- A team can be high on stickiness (Knicks) and still win because they have an elite primary creator who can carry an offense in the playoffs.
- A team can be high on action poverty (Lakers) and still win because they have two transcendent stars.
- But a team that is high on motion death AND iso reliance AND shot quality decay simultaneously is structurally cooked in the playoffs, because they have no advantage-creation mechanism and the shots they generate are the kind that crater under playoff defensive intensity.

That is a sharper, more defensible thesis. It also points more directly to fixes: "reduce iso, restore motion, improve shot quality" maps to specific roster and system changes.

**Phase 4 implication:** if predictive validation shows the C2+C3+C5 subset is more predictive of playoff failure than the full composite, we may want to weight those three more heavily, or report a "sharp LAFI" subset alongside the full composite.

## Two things to flag before Phase 3

**One. The GSW false positive on Component 5 needs prominent disclosure.** Steph's high pull-up three rate hurts the Warriors on this metric even though his pull-up threes are good shots. This is a known limitation of any shot-diet metric that does not model individual shotmaking. The writeup should acknowledge this and note that v2 (with expected eFG modeling that accounts for the shooter) would handle it.

The good news: the Wolves are not a high-pull-up-three team in the way the Warriors are. The Wolves' pull-up threes are mostly Ant late-clock pressure shots, which are exactly the bad shots the metric is trying to capture. So the Wolves' 82nd percentile is honest. The Warriors' 19th percentile is partly an artifact.

**Two. The four-act trajectory needs to become a canonical visualization in the final deliverable.** The line chart showing five components across four seasons, with 2023-24 as the trough and 2025-26 as the peak, is going to be one of the most striking visuals in the entire project.

## What I'm watching for in Phase 3

Three specific things, in priority order:

1. **Correlation matrix.** Specifically C2/C3, C2/C5, C3/C5 correlations. If all three above 0.70 league-wide, that confirms the "three surfaces of the same disease" interpretation. If lower than expected, the components are more independent than I think and the lockstep is Wolves-specific (which is also interesting but a different story).

2. **PCA PC1 variance explained.** The spec wanted 50-65%. If PC1 explains 70%+, the five components are too redundant and one underlying construct (probably "pickup-ness") dominates. If under 40%, the components do not capture a coherent construct. Both extremes are red flags. The middle is healthy.

3. **The Wolves' rank on the canonical composite.** Will they land where the manual math suggests (60-65 percentile, roughly 8th-12th in the league)? Small differences fine. Big differences would tell me my back-of-envelope math missed something.

4. **Wolves-specific cross-component correlations vs league-wide.** This is the methodological subtlety. The Wolves show high correlation between C2, C3, C5 across their own Edwards-era seasons. But league-wide, those components might be more independent. If true, that is a finding about the Wolves specifically: their pathology connects motion, iso, and shots more tightly than is normal for an NBA team. That would be diagnostic.

## Where the project is right now

Phase 2 has done what I hoped. We have a defensible metric, a refined diagnosis, and a clean year-over-year story. The agent has been disciplined about not over-claiming and the findings folder makes the analytical journey traceable.

Three things looking strong:

1. The Q4 pathology framing is robust across all five components, even where individual components surprised us.
2. The 2023-24 to 2025-26 trajectory is clean and interpretable.
3. The Wembanyama-as-architectural-counterargument finding is shaping up to be one of the most striking insights.

Two things to watch:

1. Phase 4 predictive validation will determine whether LAFI earns its keep or remains a descriptive metric.
2. The composite landing at 61 (not 85+) changes the deliverable's framing. We need to be ready to revise the LAFI spec's success criteria if the predictive relationship is real but the metric is less extreme than originally hypothesized.

Ready for Phase 3.

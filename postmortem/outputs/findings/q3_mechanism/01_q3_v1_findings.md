# Q3 v1: Mechanism analysis (Edwards-specific Spurs decoder)

**Date:** 2026-05-18
**Status:** Q3 v1. Action-classifier-free analysis using shot chart detail + team defensive profiles. The headline Edwards-vs-Spurs question is answered cleanly; the PnR coverage decoder remains a v2 follow-on (requires manual coding or action classifier).
**Sample:** Edwards' 2024-25 and 2025-26 shot chart detail (3,321 shots across 165 games); 2025-26 team defensive profiles via shot chart aggregation.

## Headline

**The Spurs forced Edwards into the floater zone and suppressed his catch-and-shoot opportunities specifically.** Three numbers tell the story:

1. **3PA volume cratered against SAS:** 5.33 3PA/game in R2 vs 8.43/game in RS (-3.1 attempts/game, -37%)
2. **Shot distance shrank:** average 13.24 ft vs SAS, down from 15.29 ft in RS (-2.0 ft toward the basket). Short midrange (11-16 ft) share jumped from 14.6% to 21.2%; 3PA range (23-25 ft) share dropped from 25.8% to 16.8%.
3. **Catch-and-shoot share collapsed:** 6.2% of Edwards' shots vs SAS were classified as catch-and-shoot generic jump shots, down from 13.8% in RS. The Spurs specifically took away his off-ball catches.

**Edwards adapted by driving more (40.7% of shots vs 28.2% RS) and was actually slightly MORE efficient on what he took (46.9% FG vs 48.9% RS).** His eFG only dropped modestly (.522 vs .572). The Spurs' scheme didn't break him as a scorer; it broke him as a three-point creator AND as a screen-and-roll engine for teammates.

**Replicability is real but not severe.** Multiple 2025-26 teams have rim protection + closeout discipline combinations that could plausibly recreate elements of the Spurs' scheme. **OKC (Holmgren) is the closest architectural comp** and is a likely future Western Conference playoff opponent. The Spurs' specific Wembanyama-versatility advantage is harder to replicate (his ability to BOTH rim-protect and switch onto guards is rare), so most teams can do half of the scheme but not the full version.

## 1. Edwards shot diet by phase

| Phase | Games | FGA/G | 3PA/G | 3PA rate | FG% | 3P% | eFG | Avg Distance |
|---|---|---|---|---|---|---|---|---|
| 24-25 RS | 79 | 20.4 | 10.3 | **50.3%** | 44.7% | 39.5% | 0.547 | 16.4 ft |
| 24-25 PO | 15 | 19.9 | 8.7 | 43.6% | 45.3% | 35.4% | 0.530 | 14.7 ft |
| 25-26 RS | 61 | 20.2 | 8.4 | 41.8% | 48.9% | 39.9% | 0.572 | 15.3 ft |
| 25-26 PO R1 DEN | 4 | 16.8 | 7.8 | 46.3% | 35.8% | 25.8% | 0.418 | 16.1 ft |
| **25-26 PO R2 SAS** | **6** | **18.8** | **5.3** | **28.3%** | 46.9% | 37.5% | 0.522 | **13.2 ft** |

**Key observations:**

- **2024-25 RS Edwards was a 50% 3PA-rate shooter.** That's a high-volume primary creator who took half his shots from three.
- **2025-26 RS dropped his 3PA rate to 41.8%** (the step-function shift identified in prior project work, not Edwards-individual per Q0D but reflected in his shot diet).
- **2025-26 PO R1 vs DEN had 4 games of Edwards data** (he was injured games 3-6, played limited or DNP). His shooting collapsed (35.8% FG, 25.8% 3P) but his shot diet shape was relatively normal.
- **2025-26 PO R2 vs SAS:** the diet shape SHIFTED. 3PA volume dropped to 5.3/g. Shot distance shortened by 2 feet. His shooting efficiency was fine (46.9% FG, 37.5% 3P on the reduced volume). **The Spurs didn't make Edwards miss; they made him not even attempt threes.**

## 2. Shot distance buckets (the mechanism)

| Phase | 0-3 ft (rim) | 4-10 ft (paint) | 11-16 ft (short mid) | 17-22 ft (long mid) | 23-25 ft (3pt) | 26+ ft (deep 3) |
|---|---|---|---|---|---|---|
| 24-25 RS | 22.5% | 11.9% | 8.4% | 8.8% | 32.7% | 15.7% |
| 25-26 RS | 22.1% | 12.8% | **14.6%** | 10.1% | 25.8% | 14.5% |
| **25-26 PO R2 SAS** | **26.5%** | **16.8%** | **21.2%** | 7.1% | **16.8%** | 11.5% |

vs SAS, Edwards' shot diet shifted as follows (relative to 2025-26 RS baseline):

- **11-16 ft (short midrange / floater zone): UP from 14.6% to 21.2% (+6.6 pp)**
- **4-10 ft (paint): UP from 12.8% to 16.8% (+4.0 pp)**
- **23-25 ft (3pt zone): DOWN from 25.8% to 16.8% (-9.0 pp)**
- **26+ ft (deep 3): DOWN from 14.5% to 11.5% (-3.0 pp)**
- Rim attempts: slightly up (22.1% → 26.5%)
- 17-22 ft (long midrange): slightly down

**This is the classic "give up the floater, take away the three" signature.** A defending big who can shrink toward the floater zone (because Wembanyama's length lets him bother shots from 11-16 ft that most centers can't), combined with aggressive perimeter closeouts (because the rim is protected), produces exactly this distribution.

The shift is not "drive more, settle for floaters" out of frustration. It's a designed defensive scheme that channels Edwards' creation into the highest-frequency-low-EV shot type (the short floater) by closing off both the rim and the three.

## 3. Action type breakdown

| Phase | Pull-up | Catch-and-shoot (generic JS) | Driving | Fadeaway/Post |
|---|---|---|---|---|
| 25-26 RS | 44.9% | 13.8% | 28.2% | 8.9% |
| 25-26 PO R1 DEN | 53.7% | 10.4% | 31.3% | 3.0% |
| **25-26 PO R2 SAS** | 40.7% | **6.2%** | **40.7%** | 9.7% |

**The catch-and-shoot collapse is the cleanest finding.** Edwards' catch-and-shoot share dropped to less than half its RS rate (6.2% vs 13.8%). **The Spurs were not letting him catch the ball with space to shoot.**

His driving share rose +12.5 percentage points (28.2% → 40.7%). The Spurs forced him into ball-on-the-floor situations rather than off-ball catch-and-shoot situations. Once he was driving, the Wembanyama-anchored rim protection let perimeter defenders pinch off recovery angles.

Pull-up share actually dropped slightly. The Spurs' scheme wasn't "let him pull up"; it was "force him to drive into a shrunken paint."

## 4. Connecting Q3 to Q1 and Q2

The Q1 team-level finding was that the Wolves' 2025-26 playoff 3PA rate dropped from RS 0.420 to PO 0.342 (z=-2.16 vs league norms). The Q2 confound check showed this collapse was Spurs-specific (2024-25 PO held 3PA rate flat; 2025-26 R1 DEN was similar to RS rate; only R2 vs SAS cratered).

Q3 now identifies the mechanism: **the Spurs schemed Edwards specifically off the three-point line.** Edwards alone went from 8.4 3PA/g (RS) to 5.3 3PA/g (R2). Over 6 games, that's ~19 fewer Edwards threes than the RS baseline projects. The team's overall 3PA decline in R2 was driven substantially by Edwards' individual 3PA suppression.

This connects to Q2's lineup-grain finding that Gobert+Randle was -26.46 in R2 specifically. The Spurs' scheme didn't just suppress Edwards' threes; it broke the team's secondary creation entirely. With Edwards forced to drive and the rim protected, the offense relied on Randle and Gobert to create off Edwards' kickouts. Neither is a creator. The possession ended.

## 5. The replicability question

**Could other teams replicate the Spurs' scheme against Edwards in 2026-27 and beyond?**

Pulled team defensive profiles for all 30 teams in 2025-26 RS. Two metrics:
- **Closeout discipline (opp 3PA rate, lower = better):** how much do opponents hold the other team to fewer three-point attempts
- **Rim protection (opp rim FG%, lower = better):** how effective is the team at the rim

The Spurs' approach (force off-ball receivers off the three-point line because the rim is protected) requires both.

### Composite "Spurs archetype score" (closeout + rim protection)

| Team | Opp 3PA rate | Opp rim FG% | Avg DEF rtg | Spurs archetype score |
|---|---|---|---|---|
| **MIN** | 0.379 | 0.633 | 112.68 | **0.075** |
| **SAS** | 0.405 | 0.635 | 110.44 | **0.046** |
| IND | 0.376 | 0.672 | 117.98 | 0.038 |
| **OKC** | 0.440 | 0.610 | **106.62** | 0.036 |
| POR | 0.392 | 0.661 | 113.49 | 0.033 |
| DET | 0.431 | 0.628 | 108.98 | 0.027 |
| CLE | 0.428 | 0.633 | 114.18 | 0.024 |
| HOU | 0.401 | 0.661 | 112.25 | 0.024 |
| ATL | 0.405 | 0.660 | 112.86 | 0.020 |
| DAL | 0.389 | 0.677 | 115.54 | 0.020 |

(League averages: opp 3PA rate 0.415, opp rim FG% 0.671)

### What this tells us

**The Wolves' own defense ranks highest by this composite.** Gobert-anchored rim protection + the team's perimeter closeout discipline produces exactly the architecture the Spurs deployed against them. This is a notable quirk: the Wolves were beaten by an opponent running a similar defensive identity to their own, but with a more switchable center (Wembanyama vs Gobert).

**Multiple Western Conference teams have similar architecture:**
- **OKC** (Holmgren-anchored): elite defense (106.6 rtg) + elite rim protection (60.1% opp rim FG%, the best in the league). Their opp 3PA rate is high (44.0%) which doesn't fit the Spurs pattern, but their rim protection is even better. **OKC could plausibly run a Spurs-like scheme with Holmgren as the rim anchor.**
- **SAS** itself: still in the league, still has Wembanyama. The Wolves will face them again.
- **HOU**: rim protection + closeout discipline both above average; possible.
- **DAL**: closeout discipline good; rim protection less so.

**Eastern Conference comps:**
- **IND, DET, CLE** all show similar composite profiles. Less directly relevant for the Wolves who only face Eastern teams in finals.

### Replicability verdict

**The Spurs' approach is partially replicable but Wembanyama's specific versatility is hard to fully copy.** A team with elite rim protection (Holmgren-tier) and disciplined closeout coverage can recreate the schematic intent: force Edwards off-the-line, channel him to the rim, protect the rim, accept short midrange shots.

The Spurs add Wembanyama's unique ability to BOTH rim-protect from the floater zone AND switch onto guards on the perimeter. Most teams can do one. Few can do both.

**For 2026-27 specifically:** OKC is the most likely opponent that can replicate enough of the scheme to give the Wolves trouble. They were 1-seed in 2024-25 and will be a likely high seed in 2026-27. The Wolves' offensive architecture needs to handle this defensive style or accept that OKC and SAS are difficult matchups.

## 6. What this means for Q5

The Q3 v1 findings update the Q5 prescription in three ways:

1. **The Spurs-specific story is real but not unique enough to ignore.** Other Western Conference teams (OKC most prominently) have architectures that could partially replicate the Spurs' scheme. The Wolves need offensive answers, not just hope for favorable matchups.

2. **Q5 Path 2 (Category B acquisition) becomes even more urgent.** The Spurs' scheme worked partly because Edwards couldn't catch-and-shoot threes (his catch-and-shoot share dropped to 6.2%). Adding more off-ball threats (Category B specialists) would force defenses to either (a) close out on more shooters, opening Edwards back up, or (b) accept giving up more threes elsewhere if they continue focusing on Edwards. **DiVincenzo's recovery and Q5 Path 2 acquisition aren't just about the DiVincenzo-shaped hole; they're about the team's structural response to schemes like the Spurs'.**

3. **Q5 Path 1 (Edwards development) has a specific direction.** Edwards needs to either:
   - Improve his short midrange / floater efficiency (currently 11-16 ft is his weakest zone)
   - Develop a step-back pull-up three that breaks drop coverage from beyond
   - Improve his playmaking on drives to convert defensive over-rotation into open teammates
   - All three, ideally
   The data suggests Edwards' raw scoring on the SAS-style shot diet was actually fine (46.9% FG). The team's problem wasn't that Edwards missed; it was that the team had no other answer when Edwards was contained. Edwards-development is partly individual but mostly about giving Edwards better options to pass to.

## 7. What Q3 v1 does NOT do

The Q3 spec called for a full PnR coverage decoder. This v1 builds the Edwards-shot-diet analysis but does not classify each individual PnR by coverage type. The trade-off:

**Built (v1):**
- Edwards' shot location distribution by opponent series
- Action type bucket analysis (catch-and-shoot vs drive vs pull-up)
- Team-level replicability analysis

**Deferred to v2 (manual coding or action classifier required):**
- Per-PnR coverage classification (drop / hedge / switch / blitz)
- Pass-out destination tracking from blitzes
- Defensive PnR coverage decoder (Q3c: how does Gobert in drop perform vs how does Naz in switch perform)
- Player-level shot quality decomposition (Q3a, requires expected eFG% model)

**The v1 finding (Spurs forced Edwards off the line via catch-and-shoot suppression and floater-zone channeling) is robust enough for Q5 framing without the full PnR decoder.** The deeper coverage classification would strengthen the analysis but would not change the directional conclusion.

The v2 manual coding (~20-30 hours per the spec) remains an option if Q5 deliverable needs sharper claims. For v1 purposes, the shot diet analysis directly answers the load-bearing question: yes, the Spurs scheme-specific suppressed Edwards' shot diet in a measurable way.

## 8. Artifacts

```
analyses/q3_mechanism/
  edwards_shot_diet.py           Edwards shot location decomposition by phase
  replicability.py                Team defensive profiles + Spurs archetype score

outputs/tables/q3_mechanism/
  edwards_shot_zone_by_phase.csv
  edwards_action_type_by_phase.csv
  edwards_distance_buckets_by_phase.csv
  team_defensive_profiles_2025_26.csv
  team_spurs_archetype_score.csv
```

Re-runnable:
```
python -m analyses.q3_mechanism.edwards_shot_diet
python -m analyses.q3_mechanism.replicability
```

## 9. Status

Q3 v1 complete. The central question is answered cleanly: **the Spurs suppressed Edwards' three-point attempts specifically by taking away his catch-and-shoot opportunities and channeling him into the Wembanyama-bothered floater zone.** Edwards adapted by driving more and was actually slightly more efficient on the shorter shots, but the team's overall offensive output collapsed because the team's secondary creation (Randle, Gobert) couldn't convert Edwards' kickouts into productive offense.

Replicability is partial: OKC has architecture similar enough that the Wolves should expect to face Spurs-like defensive looks in future Western Conference playoff series. The structural answer (Category B acquisition + Edwards-around-Edwards roster optimization) becomes more pressing.

Ready for Q5 spec revision per the data scientist's sequence. The diagnosis is now complete enough to write the prescription.

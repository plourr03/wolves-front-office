# Case file: the 2025-26 New York Knicks

**Champion.** Beat San Antonio 4-1 in the Finals. Jalen Brunson, Finals MVP. First title since 1973.

**How to read this file.** The preseason market is a prior, not a prediction to be graded right or wrong. The Knicks matter to a Minnesota preview because **the market priced them well and they still outran the price**, and the useful question is what moved them inside it. Every figure below is from run `h4_knicks_case_file_20260916T190540Z`.

**Sources.** Series results from the warehouse (`nba_games`, season 42025) and independently from [Wikipedia's 2026 NBA playoffs page](https://en.wikipedia.org/wiki/2026_NBA_playoffs); game counts agree exactly. Preseason price from the project's hand-transcribed odds file. Preseason model number from this project's own calibration backtest.

---

## 1. What the odds used

**The market had them as a contender, and it was right to.**

| | Knicks | note |
|---|---:|---|
| preseason title price | +900 | |
| implied probability, de-vigged | **8.27%** | rank **4** of 30 |
| preseason favourite | Oklahoma City Thunder | 24.32% |
| win total | 53.5 | they won **53** |

**The market missed their regular season by 0.5 wins.** That is close to perfect, and it is the first thing a reader should take from this file: the odds were not surprised by who the Knicks were in the regular season.

**Our own model was.** This project's preseason model had them at **4.63%** and **47.5 wins**, a miss of **5.5 wins**, against the market's 0.5. The model sat below the market on the eventual champion by roughly 3.6 points. **That is the same direction it sits on Minnesota now**, and it belongs in the piece as a reason to hold the model's Minnesota number loosely, not as a reason to trust the market's blindly.

**What was observable in September.** Continuity of **0.821**, rank **4** of 30 against a league median of 0.611: all five starters returned. A returning core is exactly the kind of information a market can see and price, and it did.

---

## 2. What changed

**The regular season was steady, not a late surge.** 53-29, a margin of **+6.33**, rank **5** of 30. **+6.16 before the All-Star break and +6.67 after.** Nothing in March told you April was coming.

**Then the playoffs were a different team.**

| | regular season | playoffs |
|---|---:|---:|
| record | 53-29 | **16-3** |
| margin per game | +6.33 | **+14.89** |
| rank | 5 of 30 | **1 of 16** |

**The playoff margin was 2.35 times the regular-season margin.** Playoff opponents are better, so almost every team's margin FALLS in April: the average change across the 16 playoff teams was **-7.39**. The Knicks' change was **+8.57**. **They were the only one of 16 playoff teams whose margin improved at all**; the next best was SAS -0.78.

**The series:** ATL 4-2 (+17.5); PHI 4-0 (+22.2); CLE 4-0 (+19.2); SAS 4-1 (+2.4). They swept Philadelphia and Cleveland by roughly twenty points a game, then won a close Finals.

**Three things moved, and none of them was visible in September.**

**Health reversed.** The starting five (Bridges, Brunson, Towns, Anunoby, Hart) missed **46 regular-season games** between them. In the playoffs they missed **2**. The top eight missed 4 playoff games in total across 19. A team that spent the winter shorthanded arrived in April whole.

**The rotation shortened onto the starters.**

| minutes share | regular season | playoffs | change |
|---|---:|---:|---:|
| top 3 | 0.372 | 0.420 | +0.047 |
| top 5 | 0.579 | 0.673 | **+0.095** |
| top 8 | 0.761 | 0.869 | +0.108 |

**The bracket broke their way.** San Antonio beat Oklahoma City, the preseason favourite, in seven games in the West final, so the Knicks never had to beat the team the market liked most.

---

## 3. Which H1 features would have flagged it

| feature | Knicks | flag? |
|---|---|---|
| preseason market rank | 4 | **yes**: every champion in this project's three-season sample started top 4 |
| preseason implied probability | 8.27% | **circular, so not counted**: the Knicks are one of the three champions that DEFINE the 8.27% to 14.69% band, and they set its floor. Being inside it is true by construction. |
| continuity | 0.821, rank 4 | **weakly**: see the Minnesota line below |
| regular-season margin | +6.33, rank 5 | no: good, not elite |
| style profile | rim_rate 15, fg3a_rate 12, pace 24, opp_tov_rate 13, oreb_rate 5, size 23 | **no**, and this project's held-out test found style carries no playoff signal |
| regular-season health | 46 games missed by the starters | **the wrong way**: a health feature would have marked them DOWN |
| minutes concentration | not a preseason quantity | no: F4d found regular-season concentration does not predict playoff margin |

**The honest reading.** The one non-circular feature that flagged the Knicks is the one the market already priced: they were a top-four team. **Everything that separated them from the other contenders happened after the price was set**, and the one regular-season signal that bore on it, health, pointed the wrong way. This is not a missed signal. It is a one-in-twelve prior landing, driven by variance the preseason could not observe.

---

## What this file means for Minnesota

**The Knicks are the template, and Minnesota does not yet fit it on the first flag.**

- **Market position.** The Knicks started **inside** the champion band at rank 4. Minnesota starts at **3.16% and rank 6**, outside it.
- **Continuity is not the story.** Minnesota's continuity in 2025-26 was **0.829, rank 3**, slightly higher than the Knicks', and Minnesota went out in the second round (beat Denver 4-2, lost to San Antonio 2-4).
- **The playoff lift is the story, and it ran the other way for Minnesota.** In 2025-26 Minnesota's margin changed by **-9.19** from regular season to playoffs, rank **11** of 16. The Knicks' changed by **+8.57**, rank 1.

**The sentence the piece can support:** the last champion was a team the market already had as a contender, which then got healthy, shortened its rotation onto its starters, and played nine points better in the playoffs than in the regular season. None of that was visible in September. Minnesota's case for a similar run has to start from a lower price and a team that went the other way last April.

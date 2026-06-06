# The 2023-24 Wolves offense in context: normal, not elite

**Date:** 2026-05-22
**Trigger:** Drafting Article 2 ("How They Got Here"). Bobby flagged that the opening called the 2023-24 offense "some of the most organized offense in the league," which contradicted the article's own baseline section ("it was a normal one"). He asked for the claim to be checked against data.

## The question

Where did the 2023-24 Wolves offense actually rank, by output and by architecture, among the 30 teams that season?

## Method

`analyses/q0a_lafi/wolves_2023_24_context.py`. 2023-24 Regular Season, all 30 teams. Possession-weighted offensive, defensive, and net rating from `nba_team_advanced_stats`. LAFI within-season rank from `lafi_composite_5component.csv`.

## The data

| Measure | 2023-24 Wolves | Rank of 30 |
|---|---|---|
| Offensive rating | 114.6 | 17th |
| Defensive rating | 108.4 | 1st |
| Net rating | +6.2 | 3rd |
| Full LAFI (architecture) | 35th pct | 13th most-designed |
| Sharp LAFI (architecture) | 45th pct | 14th most-designed |

## The finding

The 2023-24 Wolves were an elite **team**, but not because of their offense. They had the best defense in the league and the third-best net rating. The offense ranked 17th of 30 in points per possession, a touch below the league median, and 13th-14th of 30 in architecture (how designed it was). Middle of the pack on both axes.

"Some of the most organized offense in the league" is false on both output and architecture. The accurate description is the one the article's baseline section already used: a normal, middle-of-the-pack offense. The conference finals run was carried by the league's best defense and by Anthony Edwards.

This matters for the drift narrative. The story is not "an elite offense collapsed." It is "a normal offense drifted into one of the most pickup-style architectures of the modern era." The target the front office should want back is league average, not a juggernaut, and this core cleared that bar two years ago.

Side note, consistent with Article 1's framing: the most-designed offenses in 2023-24 (TOR, SAS, CLE, MEM, UTA) were mostly bad, tanking teams. Designed architecture is not the same as good offense. LAFI measures how a team scores, not how well.

## Implications

Article 2 corrected: the opening, the baseline section, and the closing are reframed around the data. The 2023-24 team is now described as defense-and-Edwards with a normal offense, not as an offensive standard-bearer.

## Artifacts

`analyses/q0a_lafi/wolves_2023_24_context.py`. Re-runnable: `python -m analyses.q0a_lafi.wolves_2023_24_context`.

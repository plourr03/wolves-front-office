# Basketball Concepts Reference

Definitions and context for key analytical concepts used in serious basketball analysis. Use as a reference when working with any of these terms.

## Efficiency metrics

### Points per possession (PPP)

The fundamental unit of basketball efficiency. Total points scored divided by possessions used.

A possession ends in a shot attempt (made or missed), a turnover, or a non-shooting foul that results in free throws. Offensive rebounds that lead to additional shots are part of the same possession.

League average PPP varies by season but is typically around 1.10 to 1.15 in the modern era.

### Offensive rating (ORtg) and defensive rating (DRtg)

PPP scaled to per-100-possessions for readability. ORtg of 115 means 1.15 PPP.

### Net rating

Offensive rating minus defensive rating. A team's overall efficiency margin per 100 possessions.

### Effective field goal percentage (eFG%)

Adjusts FG% to account for the higher value of three-pointers.

$$eFG\% = \frac{FGM + 0.5 \cdot 3PM}{FGA}$$

The cleanest single shooting metric for shot value.

### True shooting percentage (TS%)

Like eFG% but also accounts for free throws.

$$TS\% = \frac{Points}{2 \cdot (FGA + 0.44 \cdot FTA)}$$

Standard for evaluating overall scoring efficiency.

## The four factors

Decomposes offensive and defensive performance into four independent components. Old (Dean Oliver's framework from the early 2000s) but durable.

Offensive four factors:
1. Effective field goal percentage (eFG%)
2. Turnover rate (TOV / possessions)
3. Offensive rebound rate (OREB / available offensive rebounds)
4. Free throw rate (FT / FGA, or sometimes FTA / FGA)

Defensive four factors are the same metrics applied to opponent.

Used as the first cut on any team-level analysis. Most performance differences trace back to one or two factors.

## Pace and possessions

### Pace

Possessions per 48 minutes. Modern league average is around 99-101.

Pace matters because high-pace teams accumulate counting stats faster but their efficiency stats are the same. Always normalize to per-possession when comparing across teams.

### Possessions estimation

The standard formula:
$$\text{Possessions} = FGA + 0.44 \cdot FTA - OREB + TOV$$

Used because exact possessions are not always logged consistently.

## Lineup analysis

### Lineup combination

A specific 5-man combination on the floor. The same 5 players in different orderings or roles count as one lineup.

### Two-man lineup

Any 2-player combination, summing across all minutes those two players share. Easier to analyze than 5-man lineups because of larger samples.

### With-or-without-you (WOWY)

Comparing team performance when player A is on with player B vs without player B. Used to evaluate fit.

### On/off

Team performance differential when a specific player is on the floor vs off the floor.

## Pick-and-roll coverages

The defensive structures used against ball-screen actions. Each has tradeoffs.

### Drop

Big drops below the level of the screen, ball-handler defender chases over the screen. Protects the rim, concedes middle and three.

Best against: pull-up shooters who do not have elite range; non-shooting roll men.
Worst against: skilled shooting bigs who pop, elite mid-range or three-point pullup shooters.

### Soft hedge / show

Big briefly steps up at the level of the screen, then recovers to the roll man. Slows the ball-handler without fully committing.

Best against: middling pick-and-roll teams; bigs who can recover quickly.
Worst against: elite quick decision makers who exploit any momentary advantage.

### Hard hedge

Big aggressively steps out and walls off the ball-handler, often with full body contact. Recovers to the roll man with help.

Best against: ball-handlers who cannot pass out of pressure; teams with limited shooting around the action.
Worst against: elite passers; teams with shooters who punish rotations.

### Blitz / trap

Two defenders converge on the ball-handler at the screen. Forces a pass-out.

Best against: ball-handlers who turn the ball over; teams whose secondary creation is weak.
Worst against: elite passers; teams with multiple creators.

### Switch

The defender on the screener picks up the ball-handler post-screen. Simple and effective if the matchup is acceptable.

Best against: teams without mismatch hunters; teams with limited iso.
Worst against: teams that hunt mismatches; teams with elite iso scorers who can punish smaller defenders.

### Ice / weak

For side pick-and-rolls. The defender on the ball-handler positions to force the ball-handler away from the screen, toward the sideline.

Best against: ball-handlers who heavily rely on the screen direction.
Worst against: ball-handlers comfortable going both directions.

## Play types

Standard categorizations of offensive actions.

### Pick-and-roll ball-handler

The handler in a ball-screen action.

### Pick-and-roll roll man

The screener who rolls toward the basket after setting the screen.

### Post-up

A player receiving the ball with their back to the basket in scoring position.

### Isolation

A player receiving the ball with no screen and attacking off the dribble against a primary defender.

### Spot-up

A player catching the ball as a stationary shooter.

### Handoff (DHO)

A player receiving the ball via a dribble handoff. Functionally similar to a pick-and-roll for the receiver.

### Off-screen

A player coming off an off-ball screen to receive the ball.

### Cut

A player moving toward the basket without the ball, receiving the ball as a finisher.

### Transition

A possession that begins in the open court after a defensive rebound, made basket, or turnover.

## Modern advanced metrics

### Box plus-minus (BPM)

A regression-based estimate of a player's per-100-possession impact. Uses box score stats. Strengths: widely available, easy to compute. Weaknesses: misses defensive value that does not show in the box score.

### Value over replacement player (VORP)

BPM scaled to total contribution, with a "replacement level" baseline. Used for career value comparisons.

### Win shares (WS)

A different approach to per-game value estimation. Older, less favored than BPM/EPM by current analysts but still widely cited.

### Regularized adjusted plus-minus (RAPM)

Regression on player-presence matrices to estimate marginal impact. The cleanest theoretical approach to impact estimation but noisy in small samples.

### Estimated plus-minus (EPM)

Blends RAPM with box-score priors. Currently the most commonly cited "single number" impact metric.

### LEBRON

Similar concept to EPM, slightly different priors. Triangulate with EPM.

### Defensive estimated plus-minus

The defensive component of impact metrics. Less reliable than offensive components but improving.

## Scheme and roster concepts

### Switchable

A defender who can credibly guard multiple positions, particularly across position groups (e.g. guards and forwards). The opposite of a "rim protector who cannot move" or a "small guard who cannot guard wings."

### Stretch big

A center or power forward who can shoot threes at reasonable volume. Modifies pick-and-roll dynamics by pulling defenders away from the rim.

### Defensive anchor

A center whose presence defines the team's defensive identity. Typically a strong rim protector. Examples: Gobert, Adebayo (in different ways), Embiid.

### Primary creator

A player who can generate scoring opportunities for himself and others, especially as the lead pick-and-roll handler. The hardest archetype to acquire.

### Secondary creator

A player who can run pick-and-roll, drive and kick, or create off the dribble at a meaningful but not primary level. Often the difference between a contender and a pretender.

### Three-and-D

A wing whose primary contributions are spot-up three-point shooting and on-ball defense. The most plentiful and acquirable archetype.

## Game state concepts

### Garbage time

Late-game minutes in lopsided contests where the result is decided. Stats during garbage time are not representative of "real basketball." Filter out.

### Clutch

Standard definition: last 5 minutes of the game, score margin within 5 points. Clutch stats are heavily noise-driven but occasionally informative.

### Half-court vs transition

A possession is "transition" if it begins quickly after a change of possession (e.g. defensive rebound, made basket pushed out, live-ball turnover) and the offense pushes the ball before the defense can set. Otherwise "half-court."

Half-court offense is the cleanest measure of structural offensive quality. Transition is partly about athletic talent and partly about defensive vulnerability of the opponent.

## Cap and contract concepts

### Salary cap

The league-wide team salary limit. Soft cap with various exceptions.

### Luxury tax

Teams over a higher threshold pay penalties on excess salary. Penalty scales with overage.

### First apron / second apron

Stricter spending thresholds with severe roster construction restrictions. Major recent additions to the CBA.

### Mid-level exception (MLE)

A salary exception that allows teams over the cap to sign a player at a defined amount. Several variants depending on team status.

### Player option / team option

The right of the player (or team) to extend or end the contract at a defined point. Critical for free agency planning.

### Trade exception

A salary "credit" generated when a team trades a player without taking back equal salary. Can be used to absorb salary later.

### Bird rights

A team's right to re-sign its own free agent without using cap space. Different tiers (full Bird, early Bird, non-Bird) based on years with the team.

## Notation conventions

When writing analyses, the following conventions are common:

- "ORtg" or "offensive rating" or "OR" interchangeably
- "DRtg" or "defensive rating" or "DR" interchangeably
- "Net" or "NR" or "NRtg" for net rating
- "Eff" for efficiency metrics
- "PPG" / "RPG" / "APG" for per-game counting stats
- "/36" for per-36-minute rates
- "/100" for per-100-possessions rates

Stick to one convention within a project. Document it.

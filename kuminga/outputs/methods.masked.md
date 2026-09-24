# Methods for the series

*Rendered from `methods.template.md`. Every number here comes from `outputs/final_numbers.csv` by key and carries a run ID; the reconcile gate fails if a digit appears that is not on the sheet. The articles are written prose-first and link here instead of carrying their own appendix; the prose gate (`gate_prose.py`) checks a finished draft's figures against the same sheet.*

## The four views

Every player gets four impact scores, each in points per hundred possessions. RAPM is a regression that credits each player for how the score moved while he was on the floor, adjusted for everyone else on it. Box is a box-score model. DARKO is a public projection built from box-score trends. Consensus blends RAPM with a public box-score metric. Consensus tracks RAPM at a correlation of ⟦⟧ across players, which means four-way agreement is weaker than it sounds: two of the four are largely the same opinion. Every title probability in the series is the mean of the four views, and the band across the views is printed beside it.

## The two aging bases

The primary basis takes every player at last season's measured level. The aged basis shifts each player by the expected one-year change for his age, estimated league-wide. Aging helps Minnesota because Minnesota is young, so quoting only one basis would be a choice with a thumb on the scale, and the series quotes both everywhere. Table headers say "un-aged" for the primary basis; prose says "primary basis".

## The two minutes allocators, the four cells and the quotability rule

Two rules hand out minutes. The team-rank allocator, which the headline simulation uses, ranks a roster team-wide and plays ten men. The pooled allocator, which the attribution uses, hands minutes out inside position groups. A verdict ships only if its sign holds under both aging bases and under both allocators, and only if every one of the four views clears its noise floor in all four of those cells. The noise floor is twice the size of change the simulation and its interpolation could produce on their own. The shipping verdicts, in all four cells, mean points of title odds and the views clearing in each:

| verdict | pooled, un-aged | pooled, aged | team-rank, un-aged | team-rank, aged | views clearing in each cell |
|---|---:|---:|---:|---:|---|
| ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |

## The bands and the labels

Every figure on the sheet carries two labels. The first says where it came from: MODELED (a simulation or a fitted model), OBSERVED (counted from box scores, contracts, schedules or documents) or DESCRIPTIVE (a parameter or a diagnostic, not a finding). The second says how it may be quoted: QUOTABLE (the figure stands on its own), QUOTABLE AS BAND (it must be printed with its band or interval, because the views or the seeds disagree by more than the figure's own size would suggest) or DESCRIPTIVE. A modeled title probability is always QUOTABLE AS BAND; the band is the four views, low to high.

## The simulation

⟦⟧ seasons per view, on both bases. Attribution prices every combination of Minnesota's offseason moves on a curve built from those simulations, and the curve is checked against the direct simulation every run. Seeding is simulated wins from net rating; the playoff draw is a series model on net rating with a noise term for what net rating cannot see.

## The market

Six books' title odds, de-vigged proportionally: the raw prices add to ⟦⟧ over a hundred, and each team's price is scaled back so the league sums to one.

## What was withheld

The late-clock split. The reconstructed shot clock read within two seconds of zero at recorded violations ⟦⟧ of the time against a bar of ⟦⟧ fixed before the build, so no late-clock figure appears in the series.

## Corrections made during the work

Two bugs in my own data changed figures before publication. The lineup pipeline was crediting some baskets to the wrong team, ⟦⟧ of all points on the ⟦⟧ team-games I checked, which retracted two sentences (that Reid next to Gobert was clearly better than Randle next to Gobert, and that Kuminga's on-off flipped sign between his two teams) and moved several playoff lineup figures in the postmortem project. The same bug lived one level down, in the possession data that RAPM is fitted on, where it misplaced ⟦⟧ of points across ⟦⟧ team-games, so RAPM was refit on corrected points. Kuminga's net RAPM went from ⟦⟧ to ⟦⟧ (consensus ⟦⟧ to ⟦⟧) and Ball's from ⟦⟧ to ⟦⟧ (consensus ⟦⟧ to ⟦⟧); Edwards rose as well. The headline went from ⟦⟧ to ⟦⟧, and from ⟦⟧ to ⟦⟧ on the aged basis, because the whole league was refit with them and it's position in the league that the simulation prices. The attribution model had also been pricing every combination of moves on a roster without Cody Williams; fixing that is what retired three of the verdicts that used to ship.

## The champions table

Every champion from ⟦⟧ to ⟦⟧, ⟦⟧ of them, used only after the winner of the last playoff game in the warehouse matched the team Basketball-Reference names as League Champion. The top eight are the eight largest playoff minute totals. How each was acquired is read from his Basketball-Reference transaction log: drafted (draft night, including draft rights traded in that night), traded for, or signed (free agency, waivers, two-way or ten-day), taking the event that opened his current stint with the franchise; a re-signing or a rookie contract inside an unbroken stint does not restart the clock. Age is on the first of February, the Basketball-Reference convention. Continuity is carried two ways. By appearance: how many of the eight appeared for the franchise in the previous regular season, and the share of all playoff minutes that went to such players. By contract: how many of the eight were with the franchise at any point of the previous season whether or not they played, read from the Basketball-Reference transaction log (Jamal Murray in 2022-23 counts by contract and not by appearance), and the share of all playoff minutes that went to such players. The preseason title price for each champion season is Basketball-Reference's preseason odds page for that season (courtesy sportsoddshistory.com), all thirty teams, de-vigged proportionally and ranked with tied prices sharing a rank; each page is cached with its content hash in the manifest, and the three hand-transcribed seasons were checked against the pages team by team. Net rating is the possession-weighted mean of NBA.com per-game team net rating, ranked among the thirty teams; the post-All-Star split starts after the longest gap in the league schedule between the first of February and the middle of March, derived from the schedule itself. The seed is the conference finish on the Basketball-Reference team page, checked against the warehouse standings. Games missed are the team's games after the player's acquisition date minus his appearances. The top-five share is the five largest minute totals over the team's total minutes. Preseason odds columns are open for a pasted source. The paragraphs are written by the script from those fields; no number in them is typed.

## The Edwards clock

The departure probabilities are the Part 1 model of "Pricing the LaMelo Trade" (Model B, M2 FINAL): a league-wide discrete-time hazard on ⟦⟧ star spells, ⟦⟧ player-seasons and ⟦⟧ departures since the ⟦⟧ season, with contract years remaining as a covariate, applied to Edwards's profile under two team paths, a team winning at ⟦⟧ and one sagging to ⟦⟧. It scored a C-index of ⟦⟧ on the sealed holdout and a calibration slope of ⟦⟧ against a window of ⟦⟧, a red cell printed as such; nothing was refit for this series. The walk-year multiple, ⟦⟧ times the odds with two seasons left, is recomputed from the fitted coefficient. The raw rates beside the model are read forward from every star-season at the same contract stage, split by the team's two-year win percentage, with the counts. The contract is from the Basketball-Reference contract book and HoopsHype, the extension date from NBA.com transactions and the Basketball-Reference player page, the rules from the ⟦⟧ CBA text (NBPA copy, quoted by page), and the ⟦⟧-game consequence from two reports.

## Ball's games

Appearances are warehouse box scores against Charlotte's schedule, a game counted when he logged minutes. Missed stretches are runs of consecutive team games without him; every stretch carries a cause with two source URLs and a quote, and any stretch without a sourced cause would print as unsourced. The base rate takes every player-season from ⟦⟧ in which the player was ⟦⟧ years old, played at least ⟦⟧ minutes per appearance the season before, and had at least ⟦⟧ of the five prior seasons at ⟦⟧ or less of his team's games, with a season lost entirely counting as zero; the strict variant adds a healthy prior season at ⟦⟧ or more of the team's games, which is Ball's case, and two looser variants are printed as sensitivity because the strict cohorts are small. The simulation sets Ball's regular-season availability to games over eighty-two, lets the pipeline's own allocator redistribute his minutes, re-prices the regular-season net by the pipeline's formula, keeps the playoffs at full strength, and runs the four states on common random numbers; at the full eighty-two the title odds reproduce the headline within the f-curve tolerance and P(top six) reproduces the seed distribution.

## The ledger

Every player and pick in and out since the season ended, read from each player's Basketball-Reference transaction log on the player's own leg of each event and from the NBA.com feed, with dollars from the contract book and Spotrac and reported terms with two URLs per move. Grades are listed exactly as written, with what each piece graded, and pieces found but not read are listed with the reason.

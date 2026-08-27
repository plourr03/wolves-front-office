# Morning report: Kuminga, Phases 1 through 3

**Run:** overnight 2026-08-26 into 2026-08-27. **Frozen snapshot:** `wh_cf31d54027f4e098`.
**Scope:** work order items 1 through 19. Sixteen completed, one blocked on terms of use, two partially limited. Details at the end.

---

## The plain-language version

**The single most important thing:** Kuminga has not signed. He has agreed. NBA.com's own tracker separates "multiple reports" from "officially announced" and puts him in the first bucket; the league transaction log has no row for him. Every outlet traces back to one report, from his agent to Shams Charania, on the day you gave me this. Everything below carries that tag.

**And the deal cannot be executed until Josh Green is gone.** This is not a preference, it is arithmetic. Minnesota's contracted 2026-27 salary is **$215,871,829** across 13 players. Adding Kuminga at $6,064,000 takes them to **$221,935,829**, which is **$249,829 over** the second apron of $221,686,000, and using the taxpayer mid-level exception hard-caps them at exactly that line. With Green's $14,679,012 removed the same signing sits $14.4M under it and is legal. Saturday, August 29, is the last day to waive a player and stretch his 2026-27 salary. That is the whole reason the deadline exists.

They miss by less than a rookie-minimum contract. **[Corrected 2026-08-27.** The first version of this report said $223,293,829 and "$7.7M over". That figure included a modelling placeholder for a 14th man, which is not a CBA charge, and the cap gate then added the exception on top of a total that already contained Kuminga, counting the signing twice. See `outputs/cap_reconciliation.md` and decision D20.**]**

**Is the signing good?** In price terms, yes, and the honest range is narrower than I expected. Kuminga's market value on his own impact estimate comes out at $11.5M under the in-house consensus, $11.7M on RAPM, $6.0M on box score, and $2.7M on the external DARKO anchor. He is being paid $6.06M. So two of four views say Minnesota is getting him for about half his price, one says they are paying exactly what he is worth, and one says they are overpaying slightly. Nobody says they are overpaying badly.

**Is the offseason good?** That, the model will not tell you, and I think that is the finding rather than a failure. Minnesota's title probability goes from 2.95% on the R6 baseline (the 2025-26 roster run back healthy, consensus fork) to somewhere between 1.67% and 3.83% depending on which impact view you use. **The four views disagree about the sign.** Under R1 that means there is no publishable claim about the offseason as a whole. What is publishable is that the offseason was close to a wash: projected wins move +0.29, from 45.8 to 46.1, and Minnesota slips from fifth to sixth in the West.

**The clearest number the run produced is not a title probability, it is a play-in probability.** Minnesota's chance of finishing top six in the West and skipping the play-in falls from **73% on the baseline to 39%** under the in-house consensus. The other views are kinder (57% RAPM, 69% box, 84% DARKO), but the direction is the same in three of four and the magnitude is legible in a way that 1.7% against 3.8% is not.

**What moved the number was not the signing.** The Shapley decomposition gives an agreed sign to five of eight moves. Adding LaMelo Ball is clearly positive (+1.17pp mean, all four views). Losing Naz Reid (-0.88pp), re-signing Ayo Dosunmu at $19.3M a year (-0.71pp) and DiVincenzo's Achilles (-0.57pp) are all clearly negative. **Kuminga's own contribution is the one with no agreed sign at all**, running from -0.89pp to +0.24pp. And if you hold the injury out, the transactions taken together were mildly *positive*: the Achilles is what actually cost them.

**One result I would want to argue about before publishing.** Every alternative power forward I tested lands at or above the actual signing, and two that Minnesota could genuinely have afforded on the same exception beat it under all four views: Josh Minott at $4.5M and Jaxson Hayes at $6.0M. That is a talent rollup with no positional awareness and no knowledge of who would have taken the call, so it does not support "they signed the wrong player." It supports something narrower and still awkward: the market at this price point was not thin.

**The risk you are buying is not the player, it is the structure.** Because Kuminga would have spent one season in Minnesota, and because a declined option year is never "covered by a player contract" under the CBA, the Wolves would hold **Non-Bird rights only** if he opts out in 2027. That caps a re-signing start at 120% of his year-two salary, or **$7,640,640**. My first-pass option model puts P(he opts out) between 0.50 and 0.80 across views, and **P(Minnesota can actually keep him) at only 0.28 to 0.54**. The most likely single outcome of this deal is one good year and then losing him for nothing.

**The thing I did not expect to find.** The frontcourt pairing that worked best last season is the one they traded away. Over 2,253 possessions, Naz Reid next to Rudy Gobert was +6.83. Julius Randle next to Gobert, over 3,443 possessions, was +3.10. Minnesota kept Gobert and moved both. Kuminga now inherits that slot.

**And the thing that should make you cautious about Kuminga specifically.** His on/off flips sign between his two 2025-26 teams: **-6.53 at Golden State over 971 possessions, +2.90 at Atlanta over 1,077.** Both samples are small enough that neither is an effect. But the shot profile moves with it in a way that is at least coherent: his three-point rate went from 27.3% at Golden State to 35.9% at Atlanta and his accuracy went up, not down, 32.1% to 34.6%. Then in the playoffs his three-point rate rose again to 40.0% and his accuracy collapsed to 20.8%. That is exactly the "slips" playoff translation his value record already carried.


### What the Shapley says, which is the most useful thing in the run

Exact decomposition over 256 coalitions, so the contributions sum to the whole offseason effect with no residual. Under R1 the publishable claim is the sign agreement, not the number.

| Move | box | consensus | DARKO | RAPM | mean (pp) | verdict |
|---|---|---|---|---|---|---|
| LaMelo Ball in | +1.00 | +0.75 | +2.28 | +0.64 | **+1.17** | **ALL POSITIVE** |
| Randle out | +0.45 | +0.19 | +0.26 | +0.51 | **+0.35** | **ALL POSITIVE** |
| other departures | -0.03 | -0.41 | +1.41 | +0.23 | +0.30 | mixed |
| depth bundle | +0.41 | +0.11 | +0.19 | -0.11 | +0.15 | mixed |
| **Kuminga in** | -0.31 | +0.18 | -0.89 | +0.24 | **-0.20** | **mixed** |
| DiVincenzo injury | -0.39 | -0.33 | -1.50 | -0.06 | **-0.57** | **ALL NEGATIVE** |
| Dosunmu retained | -0.20 | -0.63 | -1.03 | -0.97 | **-0.71** | **ALL NEGATIVE** |
| Reid out | -0.23 | -1.22 | -0.59 | -1.51 | **-0.88** | **ALL NEGATIVE** |

Five of the eight moves have an agreed sign. **Kuminga is not one of them.** His marginal contribution runs from -0.89pp (DARKO) to +0.24pp (RAPM), and the two possession-based views say positive while the two others say negative. On this evidence the signing is a coin flip in title terms, which is a different claim from saying it is bad.

The moves that do have an agreed sign are, in order of size: losing Naz Reid (-0.88pp), re-signing Ayo Dosunmu at $19.3M a year (-0.71pp), DiVincenzo's Achilles (-0.57pp), against adding LaMelo Ball (+1.17pp) and moving Randle (+0.35pp).

**Order dependence is large and it is reported.** Across 2,000 random orderings, individual marginal contributions swing by 1.5 to 3.2pp depending on when a move is evaluated. Kuminga's own swings from -0.43pp to +1.17pp. That is the honest reason the Shapley average exists, and it is also a reason to read every one of these as a range.

### The scenarios that were not taken

All priced on the same pipeline and the same baseline, so they are directly comparable.

| Scenario | mean title % | band across forks |
|---|---|---|
| Kept Reid **and** added Ball | **3.64** | 2.89 to 4.25 |
| What happened, but DiVincenzo healthy | 3.36 | 2.02 to 5.31 |
| Let the free agents walk, sign nobody | 3.15 | 2.56 to 3.64 |
| What happened, minus Kuminga | 2.95 | 1.40 to 4.92 |
| **What actually happened** | **2.77** | 1.71 to 3.77 |
| The Joan Bet's shape (retool the Randle slot only) | 2.53 | 2.17 to 3.19 |

(The third row was labelled "did nothing at all" in the first version. It is not the R6 baseline: it lets Dosunmu, Hyland and Clark walk and signs nobody, which is a different roster. The R6 baseline is 2.94% as a four-fork mean. See `outputs/canonical_figures.md` and decision D25.)

Two things fall out. First, the single best available shape was **keeping Naz Reid and still adding LaMelo Ball**, which is not a criticism the model can fully make, because the Reid salary was part of what made the Ball trade work. Second, **the shape core_max recommended in June scores below what Minnesota actually did**, which is worth saying out loud given that project's standing.

And the decomposition that matters for judging the front office rather than their luck: holding the injury out, the transactions were worth **+0.21pp** (3.36 against 3.15). The injury cost -0.59pp. The net is -0.38pp. **The moves helped slightly; the Achilles is what actually moved the number.**

### The counterfactual fives (item 17, and read the caveat first)

These are talent rollups. The machinery cannot see position and would field five centres without complaint. With that stated:

| Instead of Kuminga | mean pp vs actual | verdict | affordable on the TPMLE? |
|---|---|---|---|
| Dean Wade ($9.0M, PHI) | +1.40 | ALL POSITIVE | **no**, above the exception |
| Josh Minott ($4.5M, BKN) | +1.06 | ALL POSITIVE | **yes** |
| Al Horford ($6.8M, GSW) | +0.55 | mixed | no, just above |
| Beringer absorbs the minutes | +0.53 | mixed | n/a |
| Jaxson Hayes ($6.0M, UTA) | +0.39 | ALL POSITIVE | **yes** |
| Kenrich Williams ($5.0M, OKC) | +0.10 | mixed | yes |
| **The actual signing** | 0.00 |, | yes |
| McDaniels at the 4, next wing up | -0.13 | mixed | n/a |

Every alternative tested lands at or above the actual signing on the mean, and **two affordable ones beat it under all four views**: Josh Minott and Jaxson Hayes. That is the most uncomfortable result in the run and it deserves its caveats: Minott has only 4,535 possessions and a posterior sd of 2.10, which is the widest in the group; Hayes is a centre, which this machinery cannot know matters; and neither was necessarily gettable, since the model has no idea who would have taken Minnesota's call. What the table supports is narrower than "they signed the wrong player": it is that **the taxpayer MLE market this summer contained players who grade at least as well as Kuminga for the same money or less.**

### Kuminga's own uncertainty (item 12)

Sweeping his impact across his own posterior, holding the rest of the league fixed:

| | box | consensus | DARKO | RAPM |
|---|---|---|---|---|
| low (10th pct) | 2.07 | 0.79 | 2.51 | 1.32 |
| median | 3.26 | 1.71 | 3.77 | 2.36 |
| high (90th pct) | 4.99 | 2.64 | 5.61 | 3.51 |
| playoff translation | 3.25 | 1.70 | 3.71 | 2.31 |

Minnesota's Western Conference rank moves between 4th and 8th across the whole grid. **The spread between views is wider than the spread within any one of them**, which is the same identifiability problem that made this project decline to publish a title percentage for LaMelo and for LeBron.

The playoff-translation row barely moves the number, and that is worth a word: his measured "slips" read is an 8% haircut on his offensive term, and his offensive term is already negative under two of the four views. Applying the engine's multiplier directly would have *improved* him, which is the inversion `alebron` documented. I applied it as a strictly non-positive penalty instead.

**A robustness check that came out against intuition.** The heuristic gives Kuminga about 25 minutes; the brief describes him as a starter. Forcing him to 28, 32 or 36 minutes changes Minnesota's title probability by less than half a percentage point in every fork, and the effect is not monotone in the direction you would guess, because his impact estimate sits below the minutes-weighted average of the players whose minutes he would take. **The headline does not hinge on his role.**

---

## The three judgment calls that most affect the numbers

**1. I replaced a linear pricing curve that was producing a fake headline.** The project's par-value curve fits `salary = a + b*net` on players earning $8M or more. Its intercept is about $19.6M, so applied to a taxpayer-MLE player it priced Kuminga's market at $23.8M and reported a **+$17.7M bargain under all four views**. That is a beautiful, unanimous, wrong number: it is mostly the intercept, and it comes from asking a curve about a region it has never seen. What gave it away was the option model, which used the same curve and concluded Kuminga opts out with probability 1.00 under every fork and every aging scenario.

I replaced it with an empirical percentile map: a player's impact percentile reads across to the same percentile of the salary distribution. Calibration is now recognisable (a league-average player prices at $5.4M, Gobert at $57.1M), and the finding changed from unanimous to split, which is the honest version. This is D15 in the decision log and it is the single most consequential thing I changed.

**2. I added an eighth move to the Shapley set.** The seven you named do not span the difference between last season's roster and this one. Conley, Anderson, Ingles, Phillips, Zikarsky, Pullin and Freeman also left. Without an `other_departures` bucket the contributions would not sum to the total and the gap would sit there unexplained. With it, all 256 coalitions enumerate exactly and the decomposition closes.

**3. I turned the matchup overlay off.** The engine can adjust series outcomes for archetype matchups, but the profiles it needs exist for only 12 teams. Running it for 12 of 30 would break R2's requirement that the pipeline be identical across teams. The cost is real and I want it on the record: archetype matchup effects are exactly where the postmortem's Q4 work found this roster is most exposed, particularly against San Antonio, who eliminated them and then made the Finals.

---

## Technical detail

### What the pipeline now is

Every team's 2026-27 strength is

    net = regress_to_expectation(measured 2025-26 net) + beta * (rollup_current - rollup_baseline)

anchored on measured reality and moved by the modelled roster change. Both rollups run through the same minutes heuristic, so its level bias cancels in the difference. Minnesota's measured 2025-26 net of **+2.88** matches the engine's own June figure exactly, which is the check that the new pipeline is anchored where the old one was.

The minutes heuristic, applied identically to all 30 teams: rank by `0.5 * pct(prior minutes per appearance) + 0.5 * pct(consensus net)`, take the top ten available, allocate a 50/50 blend of an empirical team-rank curve (fitted on 2025-26 itself) and the player's own prior load, rescale to 240, apply R7 availability. Rookies get draft-slot priors fitted on the 2025 class. Rotation coverage is 97.8%.

This replaces the previous treatment in which **25 of 30 teams were assumed to have stood pat**. The transaction feed shows 309 legs and 16 trade groups across all 30 teams since June 1, so that assumption was false for essentially everyone.

### What changed league-wide

Rebuilding `team_state` on verified thresholds and the current contract book moved **17 of 30 teams across an apron tier**, median absolute change $25.8M. The Lakers gained $97.7M of committed salary, Chicago $64.5M; Oklahoma City shed $30.9M and dropped from the second apron to the first.

On the floor, projected wins: Miami +5.19, Philadelphia +5.05, Boston +4.13, Brooklyn +3.34, the Lakers +3.10 are the largest gains; Utah -7.37, Indiana -5.00, Toronto -4.37, Golden State -3.93 the largest losses. Boston passes Oklahoma City for the league's best projection. Minnesota is +0.29.

**A result about the method, not the teams:** only 11 of 30 teams have all four impact views agreeing on the sign of their offseason. Nineteen are mixed. That is this machinery's honest resolution, and it is why R1's sign-agreement test is the right publication rule.

### The cap, both branches

| | Trade Green | Stretch Green |
|---|---|---|
| 2026-27 team salary | $208,614,817 | $213,507,821 |
| vs first apron ($209,015,000) | **$400,183 under** | **$4,492,821 over** |
| vs second apron ($221,686,000) | $13,071,183 under | $8,178,179 under |
| Estimated tax bill (non-repeater) | ~$13.1M | ~$23.9M |
| Dead money 2027-28 and 2028-29 | none | $4,893,004 each |

Trading Green keeps Minnesota under the first apron by $400,183. Stretching him costs roughly **$10.9M more in tax in 2026-27 alone**, pushes them over the first apron (losing the bi-annual exception, sign-and-trade acquisition, and prior-year trade exceptions), and puts $4.89M of dead money in each of the next two seasons. The third stretch year lands in Edwards's walk year.

Both branches make Minnesota a taxpayer in 2026-27, which is their third tax year in four and therefore **triggers repeater rates for 2027-28**. The bills above use non-repeater rates and are a floor.

Edwards was not supermax-eligible this summer: six years of service, one short, and he played 61 regular-season games against a 65-game threshold, so no All-NBA and no trigger. The warehouse confirms 61 games, 60 of them with 20-plus minutes. He is first eligible in the 2027 offseason.


---

## What the external verification pass contradicted (R9)

Four things, none fatal, two of which changed a number.

**1. The signing is "agreed", not "signed".** NBA.com distinguishes reported from officially announced and puts Kuminga in the former. The league transaction log has no row. This did not change a number but it changes how every number is labelled: every Kuminga row in every output carries `reported_pending_official`.

**2. The Hawks' declined option leaves a stale row that had to be dropped.** Atlanta declined the $24,300,000 team option on 2026-06-29, but `nba_player_contracts`, scraped the morning of this run, still carries it as live. Left in, Atlanta's apron position is overstated by $24.3M and Kuminga is on two teams at once. Dropped, and logged as an R8 conflict resolved against the contract source, because the contract source is stale rather than contradictory and two independent reporters agree.

**3. The 2029 swap protection is disputed.** Hoops Rumors' transaction breakdown says the 2029 first-round swap Minnesota sent Charlotte is 6-30 protected. ESPN, CBS Minnesota, Sky Sports and the team's own release summary all say "first-round pick swaps in 2028, 2029 and 2030" with no protection stated. Both values are recorded in `kuminga/data/traded_picks_2026_offseason.csv`. It does not affect anything in this run, but it will matter if the pick assets are ever priced.

**4. DiVincenzo's timeline is a media projection, not a team statement.** The injury is fully confirmed: a torn right Achilles, non-contact, less than two minutes into Game 4 of the first round. Our own data corroborates it independently, since he played 1.32 minutes on 2026-04-25 and then vanishes from the box scores entirely. What is NOT sourced is "returns after the All-Star break". Chris Finch said in mid-July that no timeline had been set; the consensus at the time of injury was most or all of the season; CBS Sports' live board currently lists him out until at least April 1, 2027. R7's primary scenario (out for the regular season) is the well-supported one. The 80% playoff-return sensitivity is the optimistic media read and is labelled as such.

One correction the verification pass made to the *brief* rather than to the data: the Randle and Ball moves are not two deals, they are one four-team transaction executed 2026-07-10, and it also included Nic Claxton to Chicago, Mouhamadou Gueye to Charlotte, the draft rights to Matteo Spagnolo to Charlotte, and the No. 33 pick (Isaiah Evans) coming back to Minnesota from Brooklyn. The "2026 first to Brooklyn" is the No. 28 pick, which became Joshua Jefferson.

---

## What did not get done, and why

**Item 7, the 2026-27 futures and win totals: BLOCKED, not attempted.** Six candidate sources were checked before any odds table was fetched (VegasInsider, Covers, Action Network, DraftKings, CBS Sports, NBA.com) and every one explicitly forbids automated retrieval in its terms of use. Nothing was retrieved. Worth noting for the record: robots.txt on four of those permits crawling the odds paths while the human-readable terms forbid it, and where the two disagree the terms govern.

The consequence is that item 10's market-comparison column does not exist, so I cannot tell you which teams the model disagrees with the market about. The three historical seasons of preseason odds already on disk are unaffected and remain usable for backtesting.

**The five-minute fix, if you want it:** https://www.vegasinsider.com/nba/odds/futures/ has both championship futures and season win totals for all 30 teams on one page. Paste it into `offseason/data/2026-27-preseason-odd.csv` in the same three-column shape as the existing files and the comparison runs.

**Item 6, the league-wide pick ledger: PARTIAL.** Minnesota's ten traded assets are enumerated and verified against two sources. A full refresh of all 609 rows was not possible because Spotrac and RealGM both return HTTP 403 to automated retrieval. What exists instead is the June ledger with the verified Minnesota delta appended and **37 MIN-involved rows flagged stale**. Any pick-value work touching another team's 2028-2033 obligations should treat the unflagged rows as June vintage.

**Item 17, the counterfactual fives: RUN, but weaker than the brief hoped.** Per R5 these are talent rollups, not fit models. The machinery minutes-weights impact estimates and cannot see position: it will field five centres without complaint. "Beringer at the 4" therefore means "Beringer's minutes-weighted impact instead of Kuminga's," not a claim about a two-centre frontcourt. Everything about actual fit is in the descriptive lineup evidence instead.

**Three things I checked that turned out to be fine, recorded so you do not re-check them.** Jamir Watkins is absent from the rotation pool because he is on a two-way, which the heuristic excludes by design. Richie Saunders is absent because he has no 2026-27 contract on the books at all. Both are out for the season anyway. And the two-way recovery found 53 contracts league-wide from the transaction feed, since the contract book does not carry them.


---

## Item-by-item status

| # | Item | Status | Where it landed |
|---|---|---|---|
| 1 | Cap thresholds verified | **Done** | `offseason/data/league_year_constants.json`, now `is_projection: false` |
| 2 | Kuminga entry, two sources | **Done** | `kuminga/data/transaction_supplement.csv` |
| 3 | `roster_snapshot_2026_27`, 30 teams | **Done** | 516 rows: 459 standard, 53 two-way, 4 dead-money |
| 4 | `team_state` rebuilt | **Done** | 17 of 30 teams changed apron tier; diff in `outputs/team_state_diff_2026_27.csv` |
| 5 | League-wide injuries (R7) | **Done** | 10 sourced cases, 9 long-term-out |
| 6 | Pick detail | **Partial** | MIN's 10 assets enumerated and verified; league-wide refresh blocked (Spotrac/RealGM 403) |
| 7 | 2026-27 futures | **Blocked** | Terms of use at all six candidate sources |
| 8 | Mechanical all-30 roster projection | **Done** | One heuristic, 97.8% rotation coverage |
| 9 | Signing evaluator | **Done** | Cap gate + surplus under four views |
| 10 | All-30 CRN simulation | **Done** | 20k sims x 5 seeds x 2 fields x 4 forks; all 30 persisted |
| 11 | Shapley attribution | **Done** | Exact, 256 coalitions, plus order-dependence spread |
| 12 | Kuminga scenario fan | **Done** | Low/median/high plus playoff translation, per fork |
| 13 | Bird rights | **Done** | Encoded in `league_year_constants.json`; Non-Bird confirmed from CBA text |
| 14 | Player option, first pass | **Done** | Labelled first pass; uses the new percentile market curve |
| 15 | Descriptive lineup evidence | **Done** | Stint layer rebuilt for MIN/GSW/ATL, 12,608 stints |
| 16 | Cap consequences, both branches | **Done** | 2026-27 through 2028-29, with repeater and supermax timing |
| 17 | Counterfactual fives | **Done, weak by design** | Talent rollups per R5, not fit models |
| 18 | Tables, figures, provenance | **Done** | T1-T9, three figures, `outputs/PROVENANCE.md` |
| 19 | Joan Bet comparison | **Done** | Priced as a named coalition, so it is free and on the same baseline |

**Not done and not in the work order, but worth flagging:** item 10 asked for a seed distribution per team. `simulate_league` computes seeds internally but does not return them, and adding that means editing a shared engine file that four other subsystems import. I have reach-R2 / reach-CF / reach-Finals per team instead, which covers the same ground for a playoff-depth read, and I did not modify the shared engine overnight without you.

---

## How to check any of it

Every script logs a run to `kuminga/logs/runs.jsonl` with its inputs, outputs, git sha and the frozen snapshot id. `kuminga/outputs/PROVENANCE.md` maps each artifact to the run that made it and lists the snapshot's per-table sha256. The warehouse was read-only throughout; every model input is pinned to snapshot `wh_cf31d54027f4e098`.

To re-run end to end:

```bash
python kuminga/scripts/freeze_inputs.py
python kuminga/scripts/build_transaction_supplement.py
python kuminga/scripts/build_roster_snapshot.py
(cd offseason/scripts && python verified_contracts.py --write)
python kuminga/scripts/patch_contracts.py
(cd offseason/scripts && python build_team_state.py)
python kuminga/scripts/build_injuries.py
python kuminga/scripts/build_pick_ledger.py
python kuminga/scripts/build_rotations.py
python kuminga/scripts/build_strengths.py
python kuminga/scripts/run_sim.py --nsims 20000
python kuminga/scripts/build_fcurve.py
python kuminga/scripts/shapley.py
python kuminga/scripts/counterfactuals.py
python kuminga/scripts/eval_signing.py
python kuminga/scripts/player_option.py
python kuminga/scripts/cap_branches.py
python kuminga/scripts/build_stints_2026.py && python kuminga/scripts/lineup_evidence.py
python kuminga/scripts/build_outputs.py && python kuminga/scripts/build_figures.py
```

The two slow steps are the stint rebuild (about 20 minutes, 256 games) and the f-curve (about 30 minutes). Everything else is seconds.

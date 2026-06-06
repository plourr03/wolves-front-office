# NBA Roster-Construction Rules: A Wolves-Centric Reference

**Purpose:** the rules layer for the offseason series and the feasibility module. Everything that constrains the Wolves when they build the roster, organized so it can be encoded.

**As of:** June 5, 2026. The 2025-26 figures are final. The 2026-27 figures are league projections (cap roughly $165M) and get locked when the NBA sets the cap in early July. Treat 2026-27 dollars as projections, not gospel.

**A note on what is solid versus what to confirm.** The thresholds and exception amounts below are well sourced. Three things came back inconsistent across sources and are flagged inline with CONFIRM: the exact salary-matching percentage at the first apron, the exact luxury-tax bracket rates under the new CBA, and the exact counting window for the frozen second-apron pick. For those, check Larry Coon's CBA FAQ or the CBA text before relying on a specific number. The structure is right; the precise figures on those three need a primary-source check.

---

## 1. The thresholds

| Line | 2025-26 (final) | 2026-27 (projected) | What crossing it means |
|---|---|---|---|
| Salary cap | $154.647M | ~$165M | Above it you are an "over-the-cap" team, you sign outside players via exceptions, not cap room |
| Luxury tax | ~$187.9M | ~$200.5M | Above it you pay the tax on every dollar over |
| First apron | $195.945M | ~$209.1M | Above it you lose the full MLE, the BAE, and sign-and-trade acquisitions, and trade matching tightens |
| Second apron | $207.824M | ~$222M | Above it you lose almost every team-building tool and risk a frozen first-round pick |

The aprons rise at the same rate as the cap each year, so the absolute room grows annually. The catch is that the Wolves' salary rises too (Edwards' max escalates, the young extensions kick in), so the relative position does not improve on its own.

The Wolves enter this offseason below all of these: per ESPN's Bobby Marks, roughly $8M under the tax, $14M under the first apron, and $27M under the second. One clarification on the framing, since it matters for planning: they are not currently in the first apron, they are just below it. They operated above the first apron for most of 2025-26 before ducking under it at the trade deadline, and re-signing Dosunmu is likely to push them back into the tax and toward or above the first apron. So "first-apron team" is the realistic 2026-27 working assumption once Dosunmu is paid, not the current status.

---

## 2. The spending tiers, top to bottom

Think of it as a staircase. Each step down costs more and removes tools.

1. **Under the cap.** Full cap room to sign anyone, plus the room exception. Almost no contender lives here; the Wolves do not.
2. **Over the cap, under the tax.** Full non-taxpayer MLE, the BAE, Bird rights to re-sign your own, generous trade matching. The most flexible place a good team can realistically be.
3. **Over the tax, under the first apron.** Same tools as above, but you now pay the luxury tax on every dollar over the tax line. Still have the full MLE and BAE.
4. **First-apron team (over first apron, under second).** You lose the full MLE (down to the taxpayer MLE), lose the BAE, cannot acquire via sign-and-trade, and trade matching tightens. Section 8.
5. **Second-apron team.** You lose essentially everything except minimum signings and re-signing your own via Bird rights, and you put a future first-round pick at risk. Section 9.

The key mental model: **Bird rights let you re-sign your own players at any tier, but adding outside players gets harder the higher you climb.**

---

## 3. Bird rights (the re-signing tool)

Bird rights are what let an over-the-cap team exceed the cap to keep its own free agents. They come in three grades based on how long the player has been with the team without leaving as a free agent:

- **Full (Larry) Bird:** 3 seasons with the team. Re-sign up to the max, up to 5 years, with 8 percent annual raises. The team can exceed the cap, tax, and both aprons to do this.
- **Early Bird:** 2 seasons. Re-sign for up to roughly 175 percent of the prior salary or 105 percent of the league average, whichever is greater, up to 4 years.
- **Non-Bird:** 1 season. Re-sign for up to 120 percent of the prior salary, up to 4 years.

**Why this matters for the Wolves immediately:** Dosunmu was acquired by trade with his Bird rights intact, so the Wolves can re-sign him even while over the tax and into the apron. That is the whole reason a Dosunmu deal does not require cap space. It does, however, raise their team salary, which is what pushes them up the staircase.

---

## 4. The exceptions (adding outside players over the cap)

Amounts scale with the cap. 2025-26 figures are final; 2026-27 are projections off a ~$165M cap.

| Exception | 2025-26 | 2026-27 (proj.) | Years | Who can use it | Hard-cap effect |
|---|---|---|---|---|---|
| Non-taxpayer (full) MLE | $14.104M | ~$15.0M (9.12% of cap) | up to 4 | Over-cap teams below the first apron | Using it hard-caps you at the first apron |
| Taxpayer MLE | $5.685M | ~$6.1M | up to 2 | Teams between the first and second apron | Using it hard-caps you at the second apron |
| Room exception | $8.781M | ~$9.4M (5.678% of cap) | up to 3 | Teams that used cap room | n/a |
| Bi-annual exception (BAE) | ~$5.13M | ~$5.5M (3.32% of cap) | up to 2 | Over-cap teams below the first apron, once every two years | Using it hard-caps you at the first apron |
| Traded Player Exception (TPE) | varies | varies | n/a | Created when you trade away salary; absorb an incoming contract within the TPE size | Using one can hard-cap you (see Wolves note) |
| Minimum salary exception | n/a | n/a | up to 2 | Any team, any tier | n/a |

Notes that bite:

- The **full MLE and the room exception can be used to absorb a player via trade or waiver claim**, not just to sign a free agent. The **taxpayer MLE can only sign new free agents**, not absorb a trade.
- A team can use the full MLE **or** the room exception, never both, and using the room exception forfeits the MLE and BAE for that year.
- The **Wolves hold three trade exceptions** (about $10.8M, $7.6M, and $6.6M, from prior trades). Per Marks, **using any of them hard-caps Minnesota at the first apron** for the season. That is a real tradeoff: those TPEs are useful for taking on a contract without sending salary back, but the moment they use one, they cannot cross the first apron the rest of the year.

---

## 5. Salary matching in trades (by tier)

How much incoming salary you can take back depends on where you sit:

- **Below the first apron:** the generous tiered formula, commonly summarized as **up to 125 percent of outgoing salary plus $250K** on mid-sized deals (small deals can take back up to 200 percent, the largest deals are limited to 100 percent plus a fixed amount). CONFIRM the exact bracket cutoffs against Larry Coon.
- **First-apron team:** matching tightens to **roughly 110 percent** of outgoing salary. CONFIRM, since sources split between 110 percent and 100 percent for this tier specifically.
- **Second-apron team:** **100 percent**, dollar for dollar, and critically **you cannot aggregate two or more players' salaries into one outgoing package.** Each outgoing contract has to match on its own.

For planning the Wolves' star scenarios, treat any move that keeps Dosunmu and adds a large salary as an apron-bound, roughly-100-percent transaction, because the salary involved pushes them up regardless. That is why a star acquisition essentially requires sending out a near-equal or larger salary (Gobert, or Gobert plus Randle), not just a matching filler.

---

## 6. The luxury tax and the repeater tax

**Standard tax:** you pay a rate per dollar over the tax line, and the rate escalates by bracket. The 2023 CBA softened the bottom brackets and steepened the top ones.

Representative non-repeater rates (CONFIRM exact figures against the CBA, sources vary, especially in the middle brackets):

| Amount over the tax line | Approx. rate per $1 |
|---|---|
| $0 to $5M | $1.50 |
| $5M to $10M | $1.75 |
| $10M to $15M | ~$2.50 to $3.50 |
| $15M to $20M | ~$4.75 |
| $20M+ | climbs from there, roughly $0.50 more per additional $5M |

The planning-relevant point is the shape, not the exact cents: the marginal cost per dollar climbs steeply, so going deep into the tax is punishingly expensive on the last dollars.

**Repeater tax:** a team that has paid the tax in **3 of the previous 4 seasons** is a repeater and pays a premium on top of the standard rates (historically about $1.00 more per bracket; the new CBA made it harsher, CONFIRM exact). At the top, a repeater second-apron team can effectively pay something in the neighborhood of $5 to $7 in tax for every $1 of salary.

**Why this is a multi-year trap, not a single-year cost:** repeater status accumulates. Paying the tax this year is a step toward repeater status in future years, and once you are a repeater the same roster costs far more. This is the mechanism that breaks up expensive cores after a few seasons, and it is the heart of the cascade in Section 11.

---

## 7. Hard caps (when your spending gets locked)

A hard cap is a ceiling you cannot exceed for the rest of the league year under any circumstance, even with Bird rights. It is triggered by specific moves:

- **Hard-capped at the first apron** if you: use the non-taxpayer (full) MLE, use the BAE, acquire a player via sign-and-trade, or (Wolves-specific, per Marks) use any of your trade exceptions.
- **Hard-capped at the second apron** if you use the taxpayer MLE.

For the Wolves, the live version of this is the $58.5M figure: per Marks, **to re-sign Dosunmu and still avoid the second-apron hard cap, Minnesota must send out at least $58.5M in salary.** That is the number forcing a Gobert or Randle move. Without shedding that much, keeping Dosunmu pushes them past where they can operate.

---

## 8. First-apron restrictions (the full list)

A first-apron team cannot:

- Use the non-taxpayer (full) MLE (limited to the smaller taxpayer MLE).
- Use the bi-annual exception.
- Acquire a player via sign-and-trade (a sign-and-trade that would keep them above the apron is barred, and being the receiving team in one hard-caps them at the first apron).
- Match salary in trades beyond roughly 110 percent of outgoing (vs 125 percent below the apron). CONFIRM.
- Sign a player waived during the season whose pre-waiver salary was above the MLE.

A first-apron team **can** still re-sign its own free agents via Bird rights, use the taxpayer MLE and minimums, and use trade exceptions from the current year (with the hard-cap caveat).

---

## 9. Second-apron restrictions (the full list, and the frozen pick)

A second-apron team cannot:

- Use any MLE at all, not even the taxpayer version. Outside free agents can only be signed to minimums.
- Aggregate two or more players' salaries into one trade package.
- Take back more salary than it sends out (100 percent matching).
- Use a trade exception created in a prior season.
- Send cash in a trade.
- Acquire a player via sign-and-trade.
- Sign a player from the buyout market whose pre-waiver salary was above the MLE.

It **can** still re-sign its own free agents via whatever Bird rights it holds, and sign minimums.

**The frozen first-round pick (the delayed, devastating penalty):**

- Being above the second apron in a given season **freezes your first-round pick seven years out**, meaning that pick cannot be traded that year.
- If a team stays above the second apron across a multi-year window, that frozen pick is **moved to the end of the first round (pick 30)**, regardless of record.
- CONFIRM the exact counting window. Sources I found split between "above the second apron in 3 of 5 seasons" and "in 2 of 4 seasons after the freeze." The mechanism is certain; the precise count is not, and it is worth a primary-source check before any article states it.

**For the Wolves, this is a future risk, not a current constraint.** They are $27M under the second apron and are actively trying to stay under it. The frozen-pick rules matter only as a "do not let this happen if we ever go all the way in on a star without enough subtraction" warning, not as something binding them today.

---

## 10. Other contract features that affect the math

Encode these as fields, because they change matching and feasibility:

- **Player option:** the player decides whether to stay for that year. Creates walk-year and salary uncertainty. Gobert and Randle both carry 2027-28 player options (Section 11).
- **Team option:** the team decides. Common on rookie-scale deals (Beringer, Shannon) and cheap end-of-bench contracts (Phillips).
- **Trade kicker:** a bonus paid on trade, which **inflates the incoming salary for matching purposes**, so it can break an otherwise-legal match. Always check before constructing a deal.
- **No-trade clause:** the player can veto a trade. Rare, but it removes the team's control entirely.
- **Partial or non-guaranteed salary and guarantee dates:** affect how much salary actually counts and when.
- **Bird rights status of any incoming or outgoing player:** affects what the other team can do and what the Wolves inherit.

---

## 11. The Wolves, year by year (the cascade)

This is the part that matters most: being a tax or first-apron team in 2026-27 is not a one-year cost, it sets up compounding pressure.

**2026-27 (the decision year).**
- Start below all the lines, but re-signing Dosunmu via Bird rights pushes them into the tax and likely to or above the first apron.
- To keep Dosunmu and stay under the second-apron hard cap, send out at least $58.5M, which realistically means moving Gobert, Randle, or both.
- If they shed enough to stay **below the first apron**, they keep the full toolbox: full MLE (~$15M), BAE, 125 percent matching, the ability to absorb via TPE or sign-and-trade. Staying there requires real salary-dumping (for example, moving Randle's ~$33M for little back).
- If they land as a **first-apron team**, they have only the taxpayer MLE (~$6M), no BAE, 110 percent matching, and no sign-and-trade acquisitions.
- If a big swing pushes them **over the second apron**, they are down to minimums and Bird re-signings, with no aggregation, and the frozen-pick clock starts.

**2027-28 (the reset fork).**
- **Gobert and Randle both hold player options.** This is the natural pivot. If they opt in (and have not been traded), that is roughly $70M still on the books, keeping Minnesota expensive and likely in the tax. If they opt out, the Wolves shed that money but lose the players. Either way, 2027-28 is where the current cost structure either resets or entrenches.
- Edwards' max keeps escalating (toward the supermax tier if he makes All-NBA). The McDaniels and Reid extensions are in force. So the **core salary rises even if nothing else changes.**
- If they paid the tax in 2026-27, they are one year closer to **repeater status.**

**2028-29 and beyond (the compounding).**
- If they have been a taxpayer in 3 of the prior 4 seasons, they become a **repeater**, and the same roster costs materially more per dollar of tax.
- Sustained apron membership compounds the roster-building restrictions and, if they ever cross the second apron in enough years, puts the frozen pick at risk.
- This is the window in which the front office's stated Minneapolis-timeline and the sub-26 core's development have to deliver, because the financial flexibility narrows each year they stay expensive without a reset.

**The one-sentence version for the articles:** the 2026-27 choice is not just "can we afford this team next year," it is "what does this lock us into for 2027-28 and 2028-29," and the Gobert and Randle player options in 2027-28 are the release valve the whole plan hinges on.

---

## 12. Confirm before publishing

The items where I would do a primary-source check (Larry Coon's CBA FAQ or the CBA text) before stating a hard number in an article:

1. The exact first-apron salary-matching percentage (110 vs 100).
2. The exact luxury-tax bracket rates under the 2023 CBA, non-repeater and repeater.
3. The exact counting window for the frozen second-apron pick (3 of 5 vs 2 of 4).
4. The 2026-27 thresholds and exception amounts, which are projections until the cap is set in early July.

Everything else in this document is well sourced (NBA PR for the 2025-26 cap and exceptions, Hoops Rumors for the exception math and 2026-27 projections, ESPN/Bobby Marks for the Wolves' specific position and the $58.5M figure).

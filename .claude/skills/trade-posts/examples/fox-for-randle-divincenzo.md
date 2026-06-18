# Worked example: De'Aaron Fox carousel (hypothetical)

A hypothetical: the Wolves send Julius Randle and Donte DiVincenzo out for De'Aaron Fox. This is a trade idea, not a report, and the post should say so.

## Step 1: run it through the model
Run this exact trade and capture the full output. The fields map to slides like this. Brackets are filled from the model run, never typed by hand.
- Salary matching and legality: outgoing vs incoming salary, whether the deal is legal, any hard cap triggered.
- Per team books: each team's resulting payroll and its distance from the tax line, the first apron, and the second apron.
- Title odds: each relevant team's championship probability before and after, so the delta is [title_delta].
- Say yes: the model's probability each team accepts, [wolves_yes] and [other_yes].

## Step 2: the six slides (values are placeholders from the model)
1. Hook: "Should the Wolves trade for Fox?" plus "[title_delta] title odds" big, a small "hypothetical" tag, and "1 / 6."
2. The deal: OUT Julius Randle and Donte DiVincenzo, IN De'Aaron Fox, with salaries [sal_randle], [sal_ddv], [sal_fox].
3. The cap reality: a salary scale with the tax line, first apron, and second apron marked, each team placed on it, with [team_payroll] and the distance to the nearest line. Flag any hard cap.
4. Title odds: the team's championship probability [odds_before] to [odds_after].
5. Would they say yes: "My model says the Wolves do it [wolves_yes] percent of the time, the other side [other_yes] percent."
6. Verdict: your call in a sentence, then "Wolves fans, pulling the trigger?"

## Step 3: render and post
Render each slide as a 1080 x 1350 still and upload them in order. Open the caption with the hook and end it with "drop a trade and I'll run it through the model."

Every bracketed value above is filled from the model run, not entered by hand. If the model cannot produce one of them, do not guess. Fix the model query or cut that slide.

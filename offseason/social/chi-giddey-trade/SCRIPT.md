# Nembhard/Toppin trade carousel — caption + posting notes

**Hypothetical / trade idea.** Not a report. Six-slide swipeable carousel, 1080 x 1350.
Every number traces to the trade model (`python validate.py` re-checks them; the model is
seeded, so they reproduce exactly). Hot-take hook; the rest in the house editorial look.

## The deal (as modeled)
Minnesota sends **Julius Randle + Terrence Shannon Jr. + one future first** to Indiana for
**Andrew Nembhard + Obi Toppin.** A clean 2-for-2. Picked as the answer to "good now AND keep
the future": it fills the half-court-playmaking need, keeps 2027 open (one pick, MODERATE flex),
and is the only realistic deal whose cautious-view title floor stays clearly positive.

## The six slides
1. **Hook (title-odds led)** — big "1.9% -> 3.0%" title-odds jump as the hero, with "A title bump that costs zero of their 2027 picks." Randle -> Nembhard + Toppin. Tagged hypothetical.
2. **The deal** — Wolves get Nembhard ($19.6M) + Toppin ($15.0M); send Randle ($33.3M) + Shannon ($2.8M) + one future first.
3. **The cap reality** — Minnesota lands at $192.5M, under the tax by $8.5M, and never trips a hard cap (a near-even swap that sheds a little). The win-now deals slam into the first apron; this one stays free.
4. **The title odds** — 1.9% to ~3.0%, positive on all four model views (+0.9 to +1.6). Best cautious-view floor of any realistic Wolves deal.
5. **Would they say yes** — Indiana "YES, BUT": Toppin's the movable one (he's behind Pascal Siakam at the four), but Nembhard's a real starter, so giving up two rotation players for an aging Randle is a tougher sell than the model's tidy yes. The model says yes only because it grades Nembhard cheap, which also means Minnesota's getting a steal. Minnesota: the smart yes.
6. **The verdict** — better now without mortgaging 2027, with the 1-pick / 2-pick contrast, the question, and the "drop a trade" CTA.

## Caption (open with the hook, close with the engine)
> My model says this nudges the Wolves' title odds from 1.9% to 3.0%, and it costs zero 2027 picks. 🐺
>
> A hypothetical: Randle and Terrence Shannon Jr. to Indiana for Andrew Nembhard and Obi
> Toppin, plus one future first. I ran it through the model.
>
> Nembhard fills the half-court playmaking Minnesota actually lacks. The cap checks out: it's a
> near-even swap, so the Wolves stay $8M under the tax and never trip a hard cap (the
> blockbusters do). The catch is on Indiana's end: Toppin's expendable behind Siakam, but
> Nembhard's a starter, so this is a tougher sell for them than my model's tidy yes (the model
> only likes it because it grades Nembhard cheap, which also means Minnesota's getting a steal).
> Title odds still tick up on every way I value the players, the best floor of any realistic
> Wolves deal.
>
> Best part: it costs ONE pick, not two. 2027 stays wide open. Better now without mortgaging
> the future.
>
> Wolves fans: smarter than chasing a star? 👇 Drop a trade in the comments and I'll run it
> through the model.
>
> (Hypothetical, not a report. Every number is from my model.)
> #Timberwolves #NBA #WolvesBack #NBATrades #Pacers #Nembhard

## Render
From `offseason/social/chi-giddey-trade/`:
```
for id in S1-Hook S2-Deal S3-Cap S4-Title S5-SayYes S6-Verdict; do \
  npx remotion still "$id" "out/$id.png" --frame=0; done
```
Preview/tweak live with `npm run dev` (Remotion Studio). Upload the six PNGs in order 1->6.

## Caveats carried (the honest fine print)
- **Acceptance is willingness, not a report.** Nobody is reported shopping these players.
- **The Nembhard valuation is the load-bearing assumption.** The model rates Nembhard as a
  below-market contract, which is exactly why it has Indiana saying yes for so little. If he's
  better than that (most think so), Minnesota is getting a steal and a real Indiana asks for
  more. Slide 5 says this in the open.
- **Title odds are a range, never a point.** They are also modest by design (this is a fit +
  flexibility move, not a title leap). Use the 2-for-2 (15-man) values; the 1-for-2 version is
  an invalid roster the sim mis-rates.
- **Confirm Nembhard's / Toppin's exact 2026-27 cap hits on Spotrac** before publishing; salary
  matching is exact-number-sensitive.

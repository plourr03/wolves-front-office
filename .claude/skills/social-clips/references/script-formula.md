# Script formula for analytics clips

The video has to deliver a complete payoff on its own. If it feels like a trailer
for an article, people scroll. Give the whole insight in the clip, then point to
the article as the bonus for people who want the depth.

One clip makes one point. If a chart supports three ideas, that is three clips.

## The four parts

Hook, zero to two seconds. A bold claim, ideally with stakes attached. Not
"Let's break down the offense." Instead "The Wolves ran the most pickup-style
offense in the NBA last season, and it might be why the ceiling collapsed." The
first second decides whether anyone sees the rest.

Reveal, two to eight seconds. Show the visual and zoom to the subject. The
viewer should see the claim become a picture.

Insight, eight to about twenty-two seconds. The one idea and what it cost or what
it means. This is the substance. Keep sentences short and concrete.

Payoff and call to action, the last few seconds. Land the punchline, then the
call to action.

## Length and pace

Two lengths both work. A punchy 20 to 30 second cut for maximum completion, or a
deep 60 to 90 second cut that walks several points and gives each one 8 to 10
seconds with a real hold. The deep cut only works if it actually breathes: a move
at the top of each beat, then stillness while the number lands. Cramming the same
content faster is what makes a clip feel rushed and cheap.

Size each beat to how long its line takes to say, about 3.3 words per second. A
20-word sentence needs roughly 6 seconds, not 3. Count the words per line and set
the next beat's start accordingly, or the captions and the picture drift out of
sync with the voice. When in doubt, give a beat more room, not less.

## Hooks worth rotating

A claim. "Nobody on this roster created their own shot."
A question. "Why did the best defense in the league keep losing?"
A number led line. "Eighty-two games, and one number explains all of it."
A "nobody is talking about" line. "Everyone blames the offense. The tape says
otherwise."

Variety matters because the same opening every time trains people to skip.

## Captions

Most viewers watch muted, so the words you speak also appear on screen.

Keep each on-screen line to a few words, large and high contrast.
Show one line at a time, changing as you speak.
Keep them inside the safe area so the app UI does not cover them. The template
handles placement and sizing already.

## Call to action

Early on, while the page is small, lean on follows, because the algorithm rewards
follows far more than link taps. "Follow for more Wolves breakdowns."

Once there is an audience, alternate in the article. "Full breakdown at Wolves to
a T, link in bio." Treat the article as the bonus, not the reason to watch.

## Voice

Talk like you are telling a friend an unbelievable stat at a bar. Short
sentences, real energy. A flat read kills a great visual. You are not on camera,
so your voice carries the whole personality.

## The sample clip, written out

This is the script the sample beats in `timeline.ts` are timed to.

0 to 2s (hook): "The Wolves ran the most pickup-style offense in the entire NBA."
2 to 6s (reveal): "Here is every team ranked by how much of their offense was
just isolation and broken plays."
6 to 9s (zoom to Wolves): "And it is not close. Minnesota is alone at the top."
9 to 13s (insight): "Almost no structure, almost no movement, just one on one
basketball possession after possession."
13 to 17s (payoff): "Great in the regular season. In the playoffs it is exactly
why the ceiling collapsed."
17s to end (call to action): "Full breakdown at Wolves to a T, link in bio."

## Blank template to fill in

Hook: ____ (bold claim plus stakes)
Reveal: ____ (what the chart shows, in one sentence)
Zoom: ____ (name the subject as you push in)
Insight: ____ (the one idea and what it costs or means)
Payoff: ____ (the punchline)
Call to action: ____ (follow, or article link in bio)

Then open `timeline.ts` and set one beat per line above, choosing the move from
`shot-grammar.md` that fits each one.

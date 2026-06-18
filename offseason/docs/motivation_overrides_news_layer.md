# Trade Model: Motivation Overrides (News Layer)

Snapshot date: 2026-06-17. Highly time-sensitive: the draft is around June 23 and free agency opens June 30, so several of these resolve within days. Re-check right after the draft.

Author note for the agent: no em dashes or en dashes anywhere. Use commas, periods, or parentheses.

## What this is

The sourced news layer for Phase 2, Component B. It is the only channel for news-driven motivation. The computed urgency layer handles apron pressure, win-now pressure, asset hunger, and expiring risk from data. This file handles only what data cannot know: trade demands, extend-or-trade ultimatums, who is openly shopping whom, owner win-now mandates, and soft "not available" statements.

## Rules (non-negotiable)

- Every entry has a source and a date. No source means it does not go in the table.
- Every entry has an expiry. Past expiry, the build ignores it and prints a warning. These rot fast.
- The model never invents a motivation signal from stats. Absent an entry, a team is neutral on the news axis.
- `magnitude` is the strength of the signal, 0 to 1. The `type` sets the direction of the effect, which the acceptance code applies (seller-side types soften the required return and raise willingness to move, `win_now_mandate` adds to win-now pressure, `not_available_soft` raises the price and keeps the player speculative).

## Active entries

| Scope | Key | Type | Mag | Source | Date | Expiry | Conf | Note |
|---|---|---|---|---|---|---|---|---|
| player | Giannis Antetokounmpo (MIL) | extend_or_trade | 0.90 | CBS Sports; The Athletic (Amick, Nehm) | 2026-06-15 | 2026-07-15 | R | Bucks have signaled extend-or-trade this offseason, he is extension-eligible in October. Reportedly prefers the East, which lowers Minnesota's real odds. |
| player | Ja Morant (MEM) | shopping | 0.85 | NBC Sports / Yahoo (Helin); The Athletic | 2026-06-12 | 2026-07-12 | R | Expected to be traded, but Memphis waits until the Giannis situation resolves to see who pivots to Morant. |
| player | Kyrie Irving (DAL) | not_available_soft | 0.50 | NBC Sports / Yahoo (Helin); The Stein Line | 2026-06-12 | 2026-07-12 | R | Dallas says he is not available and there is no indication of a short-term trade. Raises his price, keep speculative. |
| player | Trae Young (WAS) | extend_or_trade | 0.60 | The Stein Line (Fischer) | 2026-06-16 | 2026-06-30 | R | Washington wants him to decline the $49M player option and extend at a lower number. If he opts IN by draft day, that is the tell he is about to be traded. Miami is a suitor. |
| team | MIN | win_now_mandate | 0.90 | The Athletic (Amick, Nehm); Krawczynski | 2026-06-13 | 2026-08-01 | R | Connelly is chasing a running mate for Edwards (pursued KD and Giannis, interest in Kyrie and Morant) and is expected to make significant changes. This is us. |
| team | MIA | win_now_mandate | 0.70 | The Stein Line (Fischer) | 2026-06-16 | 2026-07-15 | R | Chasing a star, Giannis primary, with Young, Morant, and Kawhi-if-available as fallbacks. |
| player | Tyler Herro (MIA) | shopping | 0.50 | CBS Sports; The Stein Line | 2026-06-15 | 2026-07-15 | J | Heat would move him to land a star, he is not untouchable. Available-for-upgrade, not a hard shop. |
| team | SAC | shopping | 0.60 | Locked on Kings (Ham) | 2026-06-03 | 2026-07-15 | R | Wants off one of LaVine, Sabonis, or DeRozan, with Sabonis the most movable. Apron-driven dump posture. |
| player | Herb Jones (NOP) | shopping | 0.40 | CBS Sports | 2026-06-15 | 2026-07-15 | J | Pelicans may move him at a value low point, durability and shooting questions. Soft availability. |

## CSV (drop into data/motivation_overrides.csv)

```csv
scope,key,team,type,magnitude,source,date,expiry,confidence,note
player,Giannis Antetokounmpo,MIL,extend_or_trade,0.90,"CBS Sports; The Athletic (Amick, Nehm)",2026-06-15,2026-07-15,R,"Bucks signaled extend-or-trade this offseason; ext-eligible Oct; prefers East"
player,Ja Morant,MEM,shopping,0.85,"NBC Sports/Yahoo (Helin); The Athletic",2026-06-12,2026-07-12,R,"Expected to be traded; Grizzlies wait until Giannis resolves"
player,Kyrie Irving,DAL,not_available_soft,0.50,"NBC Sports/Yahoo (Helin); The Stein Line",2026-06-12,2026-07-12,R,"Dallas says not available; no short-term trade indication; raises price"
player,Trae Young,WAS,extend_or_trade,0.60,"The Stein Line (Fischer)",2026-06-16,2026-06-30,R,"WAS wants PO declined and extension; opting in by draft day = trade tell; Miami suitor"
team,,MIN,win_now_mandate,0.90,"The Athletic (Amick, Nehm); Krawczynski",2026-06-13,2026-08-01,R,"Connelly chasing a running mate for Edwards; expected significant changes"
team,,MIA,win_now_mandate,0.70,"The Stein Line (Fischer)",2026-06-16,2026-07-15,R,"Chasing a star; Young/Morant/Kawhi-if-available as fallbacks"
player,Tyler Herro,MIA,shopping,0.50,"CBS Sports; The Stein Line",2026-06-15,2026-07-15,J,"Would move for a star; not untouchable; available-for-upgrade"
team,,SAC,shopping,0.60,"Locked on Kings (Ham)",2026-06-03,2026-07-15,R,"Wants off one of LaVine/Sabonis/DeRozan; Sabonis most movable"
player,Herb Jones,NOP,shopping,0.40,"CBS Sports",2026-06-15,2026-07-15,J,"May move at a value low point; soft availability"
```

## Deliberately excluded (considered, then rejected)

Keeping these visible so the model is not tempted to pick them up from mock trades, and so the choices are auditable.

- Kawhi Leonard (LAC): reported as not currently available (The Stein Line). Revisit only if that changes.
- Jalen Suggs (ORL): Krawczynski called this a thought exercise and walked it back. Not a real signal.
- Kevin Durant (HOU): rumor mill only, no trade request, reporting expects him to stay. No signal.
- Walker Kessler (UTA): restricted free agent. His movement is a sign-and-trade or offer-sheet question, handled in free agency, not in a trade override.
- Anthony Davis (WAS): appears only in columnist mock trades. No sourced report that Washington is shopping him. Add only if real reporting surfaces.
- Chet Holmgren (OKC): explicitly not being traded (The Oklahoman). Already a hard untouchable in the Phase 1 table.

## Belongs to computed urgency, not here

These are real situations, but the data layer should produce them, so do not double-count them as news.

- OKC: roughly $59M over the tax and above both aprons, so very high shed_pressure. Any Lu Dort-type move is apron-driven and computed.
- BOS: a very large projected payroll and tax bill in a Tatum-Achilles gap year, so high shed_pressure plus the Phase 1 health correction. They are also a Giannis suitor, which is a suitor data point, not an override on Boston itself.
- SAC: the broader bad-contract apron squeeze is computed shed_pressure. Only the specific "Sabonis is the most likely to move" piece is the news layer above.

## Maintenance

Re-check the day after the draft (around June 24) and again once free agency opens (June 30). Giannis, Morant, and Trae Young most likely resolve in that window. Drop expired rows. Never let a stale "available" linger after a player signs or stays.

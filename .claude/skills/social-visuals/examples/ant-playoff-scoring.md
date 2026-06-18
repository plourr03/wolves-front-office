# Worked example: Ant's playoff scoring

Goal: turn the existing "Ant scoring in the playoffs" visual into a silent narrative post.

## Step 0: the angle is a hypothesis, not a fact yet
The interesting story is usually that Ant's scoring did not just dip in the playoffs, it changed shape: less rim pressure, pushed into tougher jumpers, efficiency down. Do not assert that. Test it against the warehouse and let the validated numbers decide the beats. If the data says something different, the post says something different.

## Step 1: validate the data first
List the claims, back each with a query, run the manifest. Example claims (adapt ids and fields to your schema):
- rs_rim_rate: share of regular-season FGA at the rim
- po_rim_rate: share of playoff FGA at the rim
- rs_eff and po_eff: an efficiency measure (eFG percent, true shooting, or points per shot), regular season and playoffs
- driver: the mechanism the data supports, for example share of late-clock or guarded shots, or shots against switches if you track matchup data

Example SQL (illustrative, adapt table and column names):

```sql
-- Share of FGA at the rim, regular season
SELECT ROUND(100.0 * SUM(CASE WHEN shot_zone = 'rim' THEN 1 ELSE 0 END) / COUNT(*), 0) AS rim_rate
FROM shots
WHERE player = 'Anthony Edwards'
  AND season = '2025-26'
  AND season_type = 'regular';
```

Run the manifest through scripts/validate_claims.py. Proceed only when every claim returns a value, and confirm those values match the numbers already in your existing visual. If the visual disagrees with the warehouse, fix the visual or stop. Keep the provenance.json the validator writes next to the project so every number is traceable.

## Step 2: the silent storyboard (on-screen text plus motion)
Brackets are placeholders filled by validated values. Vertical, music under it, no voiceover.

- Hook (0 to 2s): TEXT "Everyone saw Ant's playoff dip." then "Few saw what changed." MOTION the shot chart snaps in, regular season.
- Build (2 to 8s): TEXT "Regular season at the rim: [rs_rim_rate]%." MOTION the rim zone highlights, the number counts up.
- Turn (8 to 15s): TEXT "Playoffs: [po_rim_rate]%." MOTION the chart morphs to the playoff distribution, the rim zone shrinks, a chalk circle draws the drop.
- Why (15 to 22s): TEXT one validated mechanism, for example "[driver_text]." MOTION the relevant zone or stat animates in.
- Payoff (22 to 28s): TEXT the consequence, for example "Efficiency fell from [rs_eff] to [po_eff]." MOTION the two numbers sit side by side, the playoff one in the alert color.
- Sign-off (28 to 31s): the Wolves to a T outro card. TEXT "More at Wolves to a T."

## Step 3: the look
Apply the human-look tokens. One alert color for the playoff drop, the brand green elsewhere, mono numerals, a whisper of grain, squared bars, at most one thin reference line, the wordmark footer. Match it to the voiceover clips so the feed feels like one publication.

## Step 4: render for music
Build it on the social-clips Remotion setup and render the animated visual with the on-screen text and no audio track. Drop it into the editor, add music (royalty-free is safe, a fitting trending sound can help discovery), and post.

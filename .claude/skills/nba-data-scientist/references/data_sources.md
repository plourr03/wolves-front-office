# Data Sources Reference

An inventory of NBA data sources, what each provides, and known quirks. Read this when planning a project that depends on specific data.

## NBA Stats API (stats.nba.com)

The official NBA stats API. The richest free data source. Most analytics work draws from here directly or indirectly.

### What it provides

- Box scores (game-level and player-level)
- Advanced stats (BPM, offensive rating, defensive rating, etc.)
- Tracking data (speed, distance, touches, drives, paint touches, post-ups, etc.)
- Play type stats (Synergy-derived for most play types)
- Shot charts and shot detail
- Lineup data (combinations of players, net ratings)
- Hustle stats (deflections, screen assists, contested shots)
- Defensive matchup data

### Known quirks

- Endpoints change without notice; scrapers break regularly
- Some endpoints rate limit aggressively; use delays
- Player IDs persist but team affiliations change mid-season
- Tracking data quality has improved over the years; data before 2013-14 is limited
- Synergy play type categorizations have known edge cases; treat as approximations not ground truth
- "Defense vs position" stats are positional matchups; not always meaningful for switching teams

### Practical tips

- Use the `nba_api` Python package as a starting point but expect to handle quirks
- Cache aggressively; some endpoints are slow
- Watch for stat corrections; the league occasionally retroactively updates historical box scores

## Basketball Reference (basketball-reference.com)

The historical record. Cleaner than NBA Stats for older data. Web scraping required (no API).

### What it provides

- Historical box scores back to early NBA era
- Advanced stats including BPM, VORP, win shares
- Team and player career data
- Coaching records
- Draft data
- Salary data (some years)
- Awards and honors

### Known quirks

- Web scraping required; HTML structure can change
- Rate limit your scraping; be polite
- Some advanced metrics (BPM, VORP) are Basketball Reference's own formulations
- Salary data is incomplete for older years
- Player IDs differ from NBA Stats IDs; map them carefully

### Use cases

- Historical comp analysis where era depth matters
- Cohort building across many decades
- Validation against NBA Stats for headline numbers
- Pulling consistent BPM/VORP across many seasons

## Cleaning the Glass

Premium subscription service. Worth it for serious work.

### What it provides

- Garbage time-filtered stats (the cleanest "real basketball" numbers available)
- Possession-level efficiency by play context
- Lineup data with appropriate filters
- Halfcourt vs transition splits
- Shot location buckets

### Known quirks

- Paid; budget for it
- Smaller historical depth than Basketball Reference

### Use cases

- Any analysis where garbage time is a concern
- Halfcourt offense diagnostics
- Lineup-level deep dives

## Synergy Sports

Premium service used by NBA teams. Hard to access publicly but worth knowing about.

### What it provides

- Hand-coded play type categorizations (more reliable than NBA Stats' automated version)
- Detailed scouting reports per player and team
- Video tagged by action type

### Known quirks

- Access is mostly limited to teams and media partners
- The hand-coding is high quality but expensive
- For non-team analysts, NBA Stats' Synergy-derived play type data is the accessible substitute

## Second Spectrum

Proprietary tracking provider. Used internally by the league and many teams.

### What it provides

- Advanced player tracking metrics
- Matchup difficulty scores
- Screen quality scores
- Coverage classifications

### Known quirks

- Almost entirely private; teams have access but public analysts rarely do
- For public work, approximations from NBA Stats tracking data are the alternative

## PBP (Play-by-Play) data

The raw event stream of NBA games. Can be derived from NBA Stats or pulled from third-party providers.

### What it provides

- Every event in every game: shots, passes, fouls, turnovers, substitutions, etc.
- Player IDs for each event
- Game clock and shot clock at each event
- Coordinates for shots (improved over time)

### Known quirks

- Older PBP data is less complete; pre-2000 PBP is patchy or absent
- Event coding has changed over time; pre-modern PBP uses different conventions
- Substitutions occasionally get logged incorrectly; need to validate lineup integrity
- Some event types are inconsistently coded across seasons

### Use cases

- Derived lineup data
- Possession-level analysis
- Building action classifiers
- Custom metrics not available from aggregate sources

### Practical tips

- Use Cleaning the Glass or pbpstats.com for cleaned PBP
- For raw work, parse NBA Stats' PBP endpoint output
- Validate lineup integrity (5 players per team per possession at all times)

## Tracking data sub-sources

NBA Stats exposes various tracking-derived endpoints:

- `playerdashptpass` for passing data
- `playerdashptshotdefend` for defensive matchup data
- `playerdashptshots` for shot characteristics (defender distance, dribbles, etc.)
- `synergyplaytypes` for play type frequencies

Each has its own quirks and rate limits.

## Spotrac and HoopsHype

For contract and cap data.

### What they provide

- Player salary information
- Team cap situations
- Contract details (option years, guarantees, trade restrictions)
- Free agency tracking

### Known quirks

- Salary data can lag actual contracts by days
- Specific contract details (incentives, triggers) sometimes not fully accurate

### Use cases

- Cap analysis for prescription work
- Free agency planning
- Trade scenario modeling

## Hispanos NBA, RealGM, BBM

Various community-maintained sources. Useful for specific niches:

- RealGM has good historical coaching and draft data
- BBM has detailed advanced metrics
- Various international scouting sites cover non-NBA prospects

## Data quality validation

For any project, validate against multiple sources for headline numbers. If Basketball Reference says player X averaged 22 PPG and NBA Stats says 21.8, there is a small discrepancy worth understanding (usually game corrections or rounding). If the difference is larger, investigate before using the data.

## Recommended starting stack for a serious project

1. NBA Stats API for current-season detail
2. Basketball Reference for historical depth
3. Cleaning the Glass subscription for garbage-time-filtered work
4. Spotrac for contract data
5. PBP data archive (self-maintained or via pbpstats.com)

This combination covers ~95% of public analytical work.

## Schema notes

When building your own data warehouse:

- Use player IDs from NBA Stats as the canonical identifier; map other sources to it
- Use season as a year (e.g. 2024 for 2023-24, 2025 for 2024-25) and document the convention
- Store possessions, not just games; many analyses operate at the possession level
- Cache raw API responses before transformation, so you can re-derive without re-pulling
- Use parquet not CSV for performance
- Version your snapshots; "this analysis used data pulled on date X"

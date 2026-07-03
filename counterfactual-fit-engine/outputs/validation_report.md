# fitengine validation report

Generated 2026-07-03T13:48:15 from committed artifacts. Gate FAILURES produce decision memos for Bobby; thresholds never move to make a row green.

## G1: data integrity (Layer 0)

Full panel: 15,669 games (1 quarantined).

| stratum | games | quarantine | recon TRUE 0.5 | recon relaxed | team secs (INVARIANT) | poss parity % (PARTITION) | verdict |
|---|---|---|---|---|---|---|---|
| pooled | 15,669 | 0.0064% | 99.9318% | 99.9396% | 0.9999 | 0.0000 | GREEN |
| legacy | 14,940 | 0.0067% | 99.9284% | 99.9366% | 0.9999 | 0.0000 | GREEN |
| live | 729 | 0.0000% | 100.0000% | 100.0000% | 1.0000 | 0.0000 | GREEN |

Gate bars: recon >= 99.5% on BOTH criteria (primary seconds-precise, secondary truncation-aware), quarantine < 0.5%, pooled AND per stratum. G1 GREEN on this scorecard.

Quarantine reasons (all read, none laundered; AM-3 counts their player-games as failures):

- 1 game(s): LegacySubResolutionError: legacy sub unparseable: 'SUB:  FOR...

## G2: Layer 1 (skills)

RAPM rows: see `outputs\rapm\g2_rapm_report.md` (YoY band 0.50-0.75 and top-20 face lists). Factor rows PENDING until F3.

## G3: Layer 2 (synergy, dev seasons)

PENDING: no Layer 2 fits exist (F4).

## G4: trade backtest

PENDING: harness plumbing only; dev iteration at F5. Sealed window untouched and unenumerated.

## G5: deployment sanity

PENDING: F6.

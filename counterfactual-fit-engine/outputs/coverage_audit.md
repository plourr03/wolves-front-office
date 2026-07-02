# fitengine coverage audit (R1 game-universe classification)

## Game-type census, seasons 2013-14 .. 2025-26 (PBP-present games)
type_prefix                   label  games
        002          regular_season  15669
        004                playoffs   1089
        001               preseason     66
        003                all_star      6
        005                 play_in      5
        006 other_league_or_unknown      1

Total PBP-present games in window: 16836 (raw, all types); regular season only: 15669

## Regular-season games per season (002 prefix)
  2013-14: 1230 / ~1230 expected
  2014-15: 1230 / ~1230 expected
  2015-16: 1230 / ~1230 expected
  2016-17: 1230 / ~1230 expected
  2017-18: 1230 / ~1230 expected
  2018-19: 1230 / ~1230 expected
  2019-20: 1059 / ~971 expected
  2020-21: 1080 / ~1080 expected
  2021-22: 1230 / ~1230 expected
  2022-23: 1230 / ~1230 expected
  2023-24: 1230 / ~1230 expected
  2024-25: 1230 / ~1230 expected
  2025-26: 1230 / ~1230 expected

## Reconciliation vs 2023-26 possessions cache (known-good)
cache parquets: 3939; warehouse RS+PO games 2023-26: 3941
in cache but not warehouse: 0; in warehouse but not cache: 2

game_universe.parquet written: 16836 games, 15669 train-eligible, 1089 flagged (playoffs)
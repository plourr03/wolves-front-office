# Cap position by Green branch

Green stretch schedule: $14,679,012 over 3 seasons = $4,893,004 per season.

Stretch ceiling (15% of the 2026-27 cap): $24,744,150. This uses 19.8% of it.

| season   | branch   | branch_label                | is_projection   |   committed_before_green |   green_adjustment |   dead_money |   team_salary |   n_under_contract |   salary_cap |   luxury_tax |   first_apron |   second_apron |   dist_to_tax |   dist_to_apron1 |   dist_to_apron2 |   over_tax_by |   est_tax_bill |   taxpayer_mle |
|:---------|:---------|:----------------------------|:----------------|-------------------------:|-------------------:|-------------:|--------------:|-------------------:|-------------:|-------------:|--------------:|---------------:|--------------:|-----------------:|-----------------:|--------------:|---------------:|---------------:|
| 2026-27  | trade    | A: Green traded (pure dump) | False           |              223,293,829 |        -14,679,012 |            0 |   210,364,817 |                 15 |    164961000 |    200428000 |     209015000 |      221686000 |    -9,936,817 |       -1,349,817 |       11,321,183 |     8,186,817 |      8,717,521 |        6064000 |
| 2026-27  | stretch  | B: Green waived + stretched | False           |              223,293,829 |        -14,679,012 |    4,893,004 |   215,257,821 |                 15 |    164961000 |    200428000 |     209015000 |      221686000 |   -14,829,821 |       -6,242,821 |        6,428,179 |    13,079,821 |     16,975,374 |        6064000 |
| 2027-28  | trade    | A: Green traded (pure dump) | True            |              202,118,980 |                  0 |            0 |   202,118,980 |                  9 |    176508000 |    214458000 |     223646000 |      237204000 |    12,339,020 |       21,527,020 |       35,085,020 |             0 |              0 |        6488000 |
| 2027-28  | stretch  | B: Green waived + stretched | True            |              202,118,980 |                  0 |    4,893,004 |   207,011,984 |                  9 |    176508000 |    214458000 |     223646000 |      237204000 |     7,446,016 |       16,634,016 |       30,192,016 |             0 |              0 |        6488000 |
| 2028-29  | trade    | A: Green traded (pure dump) | True            |              164,959,088 |                  0 |            0 |   164,959,088 |                  6 |    188864000 |    229470000 |     239301000 |      253808000 |    64,510,912 |       74,341,912 |       88,848,912 |             0 |              0 |        6942000 |
| 2028-29  | stretch  | B: Green waived + stretched | True            |              164,959,088 |                  0 |    4,893,004 |   169,852,092 |                  6 |    188864000 |    229470000 |     239301000 |      253808000 |    59,617,908 |       69,448,908 |       83,955,908 |             0 |              0 |        6942000 |

## The 14th and 15th man

| branch   |   room_under_apron2 | can_add_rookie_min   |   n_rookie_min_slots | can_add_vet_min   |
|:---------|--------------------:|:---------------------|---------------------:|:------------------|
| trade    |          11,321,183 | True                 |                    8 | True              |
| stretch  |           6,428,179 | True                 |                    4 | True              |

## Notes

- Gobert's 2027-28 season is a $38,000,000 PLAYER option, not a team option. The 2027-28 stretch charge lands in the same season he can choose to opt in, so Minnesota does not control both sides of that year.
- Edwards is signed through 2028-29 at $48,924,624 / $52,298,736 / $55,672,848 and becomes an unrestricted free agent after it. He was NOT supermax-eligible in 2026 (six years of service, one short, and he missed the 65-game threshold at 61 games so no All-NBA trigger). First eligible in the 2027 offseason, and only with a 2026-27 performance trigger.
- So under branch B the third stretch year (2028-29) sits in Edwards's walk year, alongside whatever an extension costs. That is the year the branch choice actually bites.
- 2027-28 and 2028-29 thresholds are the constants file's forward scale, not league-set figures. Treat distances in those seasons as directional.
- REPEATER TRIGGER. Minnesota is NOT a repeater in 2026-27: it paid the tax in 2024-25 and 2025-26 but not in 2022-23 or 2023-24, which is two of the last four against a three-of-four rule. But BOTH branches pay the tax in 2026-27, which makes it three of the last four and turns Minnesota into a REPEATER in 2027-28. The tax bills above use non-repeater rates, so they are a floor for any future season, not a forecast. The constants file also flags the exact bracket rates as needing a primary-source check.
- OUT-YEAR TOTALS ARE COMMITTED SALARY, NOT A ROSTER. The 2027-28 and 2028-29 figures count only players already under contract (nine and seven respectively), so they sit far below the tax line purely because the roster is not filled yet. They are not a projection that Minnesota escapes the tax; they are the floor those seasons start from. The stretch charge, by contrast, IS fully known in both of those years.

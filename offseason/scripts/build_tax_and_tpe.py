#!/usr/bin/env python3
"""
build_tax_and_tpe.py

Writes tax_history.csv and team_trade_exceptions.csv from gathered data
(Spotrac/SalarySwish final tax + apron trackers, June 2026).

tax_history feeds repeater_status (paid tax in 3 of the prior 4 seasons) and the
second-apron frozen-pick window. team_trade_exceptions is the TPE child table the
team_state summary points to. Data is encoded compactly (only the tax-payer and
second-apron cases are listed; everything else defaults to false) so it is easy to
audit and correct.
"""

import os
import csv
import time

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
TEAMS = ["ATL", "BOS", "BKN", "CHA", "CHI", "CLE", "DAL", "DEN", "DET", "GSW",
         "HOU", "IND", "LAC", "LAL", "MEM", "MIA", "MIL", "MIN", "NOP", "NYK",
         "OKC", "ORL", "PHI", "PHX", "POR", "SAC", "SAS", "TOR", "UTA", "WAS"]
SEASONS = ["2022-23", "2023-24", "2024-25", "2025-26"]

# Luxury-tax payers by season (second apron did not exist before 2023-24).
PAID = {
    "2022-23": ["BOS", "BKN", "DAL", "DEN", "GSW", "LAC", "LAL", "MIL", "PHX"],
    "2023-24": ["BOS", "DEN", "GSW", "LAC", "LAL", "MIA", "MIL", "PHX"],
    "2024-25": ["BOS", "DAL", "DEN", "GSW", "LAL", "MIA", "MIL", "MIN", "NYK", "PHX"],
    "2025-26": ["CLE", "GSW", "HOU", "LAC", "LAL", "MIN", "NYK"],
}
SECOND_APRON = {
    "2022-23": [],
    "2023-24": ["BOS", "GSW", "LAC", "MIL", "PHX"],
    "2024-25": ["BOS", "MIN", "PHX"],
    "2025-26": ["CLE"],
}
TAX_SRC = "Spotrac/SalarySwish final tax + apron trackers (gathered 2026-06)"

# Open TPEs as of June 2026. amount = exception size; remaining = usable left.
# (team, slug, amount, remaining, created, expiry, source_trade)
TPES = [
    ("MIN", "min_conley", 10774038, 10774038, "2026-02-03", "2027-02-03", "Conley to CHI (unused)"),
    ("MIN", "min_dillingham", 6576120, 6576120, "2026-02-05", "2027-02-05", "Dillingham to CHI (unused)"),
    ("MIN", "min_naw", 7580900, 62382, "2025-07-06", "2026-07-06", "NAW S&T to ATL ($7.52M used on Dosunmu; near-exhausted, expiring)"),
    ("MEM", "mem_jjj", 28872920, 28872920, "2026-02-03", "2027-02-03", "Jaren Jackson Jr. trade with UTA"),
    ("BOS", "bos_simons", 27678571, 27678571, "2026-02-05", "2027-02-05", "Anfernee Simons trade with CHI"),
    ("UTA", "uta_collins", 26580000, 2215000, "2025-07-07", "2026-07-07", "John Collins trade with LAC (mostly used; expiring)"),
    ("DAL", "dal_ad", 20830154, 20830154, "2026-02-05", "2027-02-05", "Anthony Davis trade with WAS"),
    ("CHI", "chi_huerter", 17991071, 17991071, "2026-02-03", "2027-02-03", "Kevin Huerter trade with DET"),
    ("DEN", "den_mpj", 17275985, 6880985, "2025-07-08", "2026-07-08", "Michael Porter Jr. trade with BKN (partly used; expiring)"),
    ("MIA", "mia_robinson", 16834692, 16834692, "2025-07-07", "2026-07-07", "Duncan Robinson trade with DET (expiring)"),
    ("DET", "det_schroder", 14104000, 8677600, "2025-07-07", "2026-07-07", "Schroder trade with SAC (partly used; expiring)"),
    ("NOP", "nop_olynyk", 13445122, 13445122, "2025-07-06", "2026-07-06", "Kelly Olynyk trade with WAS (expiring)"),
    ("WAS", "was_olynyk", 13445122, 13445122, "2025-07-08", "2026-07-08", "Kelly Olynyk trade with SAS (expiring)"),
    ("ATL", "atl_kennard", 11000000, 11000000, "2026-02-05", "2027-02-05", "Luke Kennard trade with LAL"),
    ("CLE", "cle_lonzo", 10000000, 10000000, "2026-02-05", "2027-02-05", "Lonzo Ball trade with UTA"),
    ("CHA", "cha_sexton", 8200962, 8200962, "2026-02-04", "2027-02-04", "Collin Sexton trade with CHI"),
    ("BOS", "bos_niang", 8200000, 8200000, "2025-08-06", "2026-08-06", "Georges Niang trade with UTA (expiring)"),
    ("ORL", "orl_tjones", 7000000, 7000000, "2026-02-04", "2027-02-04", "Tyus Jones trade with DAL"),
    ("CLE", "cle_hunter", 6897984, 6897984, "2026-02-01", "2027-02-01", "De'Andre Hunter trade with SAC"),
    ("ATL", "atl_capela", 6700000, 6700000, "2025-07-06", "2026-07-06", "Clint Capela trade with HOU (expiring)"),
]
TPE_SRC = "Spotrac transactions / SalarySwish trade-exception trackers (gathered 2026-06)"


def main():
    today = time.strftime("%Y-%m-%d")

    tax_path = os.path.join(DATA, "tax_history.csv")
    with open(tax_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["team_abbr", "season", "paid_luxury_tax", "was_second_apron", "source"])
        for season in SEASONS:
            for t in TEAMS:
                w.writerow([t, season,
                            "TRUE" if t in PAID[season] else "FALSE",
                            "TRUE" if t in SECOND_APRON[season] else "FALSE",
                            TAX_SRC])
    print(f"Wrote {len(TEAMS) * len(SEASONS)} tax rows -> {tax_path}")

    tpe_path = os.path.join(DATA, "team_trade_exceptions.csv")
    with open(tpe_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["team_abbr", "tpe_id", "amount", "remaining", "created_date",
                    "expiry_date", "source_trade", "is_active", "source"])
        for t, slug, amt, rem, created, expiry, src in TPES:
            w.writerow([t, slug, amt, rem, created, expiry, src, "TRUE", TPE_SRC])
    print(f"Wrote {len(TPES)} trade-exception rows -> {tpe_path}")


if __name__ == "__main__":
    main()

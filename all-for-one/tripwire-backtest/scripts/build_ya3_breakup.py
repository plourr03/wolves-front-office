"""YA3 breakup flags for the strict Scenario A class.

Definition (spec section 4): breakup within 18 months of arrival, the star
traded or a publicly reported trade request. Sourced from the transactions
table (arriving player's next outbound trade) plus a hand-curated column for
trade requests and non-trade departures the transactions table does not mark
as a Trade (amnesty/waiver).

Writes data/ya3_breakup.csv.
"""
import sys
from datetime import date
from pathlib import Path
import pandas as pd

REPO = Path(r"C:\Users\bobby\playground\wolves-front-office")
DATA = REPO / "all-for-one" / "tripwire-backtest" / "data"
sys.path.insert(0, str(REPO / "postmortem"))
from lib.db import query  # noqa: E402

A = pd.read_parquet(DATA / "refclass_A.parquet")
A = A[(A.prior_usg >= 0.28) & A.inc_strict].copy()
names = query("SELECT player_id, first_name||' '||last_name nm FROM nba.nba_player_bio")
nm2id = {n: p for p, n in zip(names.player_id, names.nm)}

# hand-curated overrides: (arriving, arr_ss) -> (ya3_breakup, note)
# Requests/departures the Trade-typed transactions miss or mis-time.
OVERRIDE = {
    ("James Harden", 2021): (1, "requested out of PHI summer 2023 (~16mo); traded Nov 2023"),
    ("Gilbert Arenas", 2010): (1, "amnestied by ORL Dec 2011 (~12mo); not a Trade row"),
}
MONTHS_18 = 548  # days

rows = []
for r in A.itertuples():
    pid = nm2id.get(r.arriving)
    t = query("""SELECT MIN(transaction_date) d FROM nba.nba_transactions
                 WHERE player_id=%s AND transaction_date > %s AND transaction_type='Trade'""",
              (pid, str(r.arr_date)))
    nxt = t.iloc[0].d if len(t) and t.iloc[0].d is not None else None
    days = (nxt - r.arr_date).days if nxt is not None else None
    breakup = int(days is not None and days <= MONTHS_18)
    note = f"traded {nxt} ({days}d)" if nxt is not None else "no outbound trade"
    key = (r.arriving, int(r.arr_ss))
    if key in OVERRIDE:
        breakup, note = OVERRIDE[key][0], OVERRIDE[key][1] + " [curated]"
    rows.append({"arriving": r.arriving, "arr_ss": int(r.arr_ss), "team": r.new_team,
                 "next_trade": str(nxt) if nxt is not None else "",
                 "days_to_trade": days, "ya3_breakup": breakup, "note": note})

df = pd.DataFrame(rows).sort_values(["arr_ss", "arriving"])
df.to_csv(DATA / "ya3_breakup.csv", index=False)
print(f"YA3: {df.ya3_breakup.sum()} breakups of {len(df)} strict Scenario A cases\n")
print(df.to_string(index=False))

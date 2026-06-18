import os, sys, csv, re, unicodedata
HERE = os.path.abspath(".")
POST = os.path.abspath(os.path.join(HERE, "..", "..", "postmortem"))
sys.path.insert(0, POST)
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(POST, ".env"))
    load_dotenv(os.path.abspath(os.path.join(HERE, "..", "..", ".env")))
except Exception: pass
from lib import db

def cols(t):
    df = db.query(f"""SELECT column_name, data_type FROM information_schema.columns
                      WHERE table_schema='nba' AND table_name='{t}' ORDER BY ordinal_position""")
    return list(zip(df.column_name, df.data_type))

print("=== nba_player_contracts columns ===")
for c,t in cols("nba_player_contracts"): print(f"   {c:28} {t}")
print("\n=== nba_transactions columns ===")
for c,t in cols("nba_transactions"): print(f"   {c:28} {t}")

print("\n=== nba_player_contracts sample (3 rows) ===")
df = db.query("SELECT * FROM nba_player_contracts LIMIT 3")
for _,r in df.iterrows(): print("  ", dict(r))

print("\n=== nba_transactions: type distribution ===")
df = db.query("SELECT transaction_type, COUNT(*) n FROM nba_transactions GROUP BY transaction_type ORDER BY n DESC")
for _,r in df.iterrows(): print(f"   {str(r.iloc[0]):28} {r.iloc[1]}")

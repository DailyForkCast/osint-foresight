#!/usr/bin/env python3
"""Check TED table schema"""
import sqlite3

db = "F:/OSINT_WAREHOUSE/osint_master.db"
conn = sqlite3.connect(db)
cur = conn.cursor()

print("TED Contracts Production Schema:")
cur.execute("PRAGMA table_info(ted_contracts_production)")
for row in cur.fetchall():
    print(f"  {row[1]} ({row[2]})")

print("\nSample row:")
cur.execute("SELECT * FROM ted_contracts_production LIMIT 1")
columns = [description[0] for description in cur.description]
for col in columns:
    print(f"  {col}")

conn.close()

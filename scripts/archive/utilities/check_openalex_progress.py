#!/usr/bin/env python3
"""Quick check of OpenAlex processing progress"""

import sqlite3
from pathlib import Path

DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Check total count
cur.execute("SELECT COUNT(*) FROM openalex_works")
total = cur.fetchone()[0]

# Check counts by technology
cur.execute("""
    SELECT technology_domain, COUNT(*)
    FROM openalex_works
    GROUP BY technology_domain
    ORDER BY technology_domain
""")

print("Current OpenAlex Works in Database:")
print("=" * 50)
for tech, count in cur.fetchall():
    print(f"{tech:20} {count:,}")
print("=" * 50)
print(f"{'TOTAL':20} {total:,}")

conn.close()

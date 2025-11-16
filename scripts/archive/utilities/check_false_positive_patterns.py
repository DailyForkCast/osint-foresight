#!/usr/bin/env python3
"""Check if false positive patterns actually exist in database"""

import sqlite3
from pathlib import Path

DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"

def check_pattern(pattern_desc, sql_pattern):
    """Check if a pattern exists in the database"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print(f"\n{'='*80}")
    print(f"Checking: {pattern_desc}")
    print(f"{'='*80}")

    # Check in usaspending_china_305
    cur.execute(f"""
        SELECT DISTINCT recipient_name
        FROM usaspending_china_305
        WHERE LOWER(recipient_name) LIKE ?
        LIMIT 10
    """, (sql_pattern,))

    results = cur.fetchall()

    if results:
        print(f"[FOUND] {len(results)} matches in usaspending_china_305:")
        for r in results:
            print(f"  - {r[0]}")
    else:
        print(f"[NOT FOUND] No matches in usaspending_china_305")

    conn.close()
    return len(results) > 0

# Check patterns
patterns = [
    ("American COSCO", "%american%cosco%"),
    ("Sino-European", "%sino%european%"),
    ("Sino-German", "%sino%german%"),
    ("Euro-China", "%euro%china%"),
    ("COSCO Fire", "%cosco%fire%"),
]

results = {}
for desc, pattern in patterns:
    results[desc] = check_pattern(desc, pattern)

print(f"\n{'='*80}")
print("SUMMARY")
print(f"{'='*80}")
for desc, found in results.items():
    status = "EXISTS" if found else "NOT FOUND"
    print(f"{desc:30} {status}")

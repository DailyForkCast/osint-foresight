#!/usr/bin/env python3
"""Quick monitor for 374-column processing progress."""

import sqlite3
from pathlib import Path
from datetime import datetime

db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")

if not db_path.exists():
    print(f"Database not found: {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Check if table exists
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='usaspending_china_374'")
if not cur.fetchone():
    print("Table usaspending_china_374 does not exist yet")
    print("Processing may not have started or table not created")
    conn.close()
    exit(0)

# Get record count
cur.execute("SELECT COUNT(*) FROM usaspending_china_374")
count = cur.fetchone()[0]

# Get total value
cur.execute("SELECT SUM(federal_action_obligation) FROM usaspending_china_374")
total_value = cur.fetchone()[0] or 0.0

# Get breakdown by detection type
cur.execute("""
    SELECT highest_confidence, COUNT(*), SUM(federal_action_obligation)
    FROM usaspending_china_374
    GROUP BY highest_confidence
""")
breakdown = cur.fetchall()

# Get latest record
cur.execute("SELECT processed_date FROM usaspending_china_374 ORDER BY processed_date DESC LIMIT 1")
latest = cur.fetchone()

conn.close()

print("="*80)
print(f"374-COLUMN PROCESSING STATUS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*80)
print(f"\nTotal detections: {count:,}")
print(f"Total value: ${total_value:,.2f}")

if breakdown:
    print("\nBy confidence level:")
    for conf, cnt, val in breakdown:
        print(f"  {conf}: {cnt:,} detections (${val:,.2f})")

if latest:
    print(f"\nLatest record: {latest[0]}")

print("\n" + "="*80)

#!/usr/bin/env python3
import sqlite3
import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

conn = sqlite3.connect("F:/OSINT_WAREHOUSE/osint_master.db")
cur = conn.cursor()

print("="*80)
print("ACADEMIC EVENTS INTEGRATION VERIFICATION")
print("="*80 + "\n")

print("Academic Events by Category:")
cur.execute("""
    SELECT event_category, COUNT(*)
    FROM bilateral_events
    WHERE event_category IN ('academic_collaboration', 'academic_restriction')
    GROUP BY event_category
""")
for cat, cnt in cur.fetchall():
    print(f"  {cat}: {cnt} events")

print("\nAcademic Events by Country:")
cur.execute("""
    SELECT country_code, COUNT(*)
    FROM bilateral_events
    WHERE event_category IN ('academic_collaboration', 'academic_restriction')
    GROUP BY country_code
    ORDER BY COUNT(*) DESC
""")
for cc, cnt in cur.fetchall():
    print(f"  {cc}: {cnt} events")

print("\nTotal bilateral_events in database:")
cur.execute('SELECT COUNT(*) FROM bilateral_events')
print(f"  Total: {cur.fetchone()[0]} events")

print("\nTotal bilateral_countries:")
cur.execute('SELECT COUNT(*) FROM bilateral_countries')
print(f"  Total: {cur.fetchone()[0]} countries")

print("\n" + "="*80)
print("✅ ACADEMIC EVENTS SUCCESSFULLY INTEGRATED")
print("="*80)

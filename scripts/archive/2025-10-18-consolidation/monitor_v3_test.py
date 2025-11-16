"""Monitor V3 Test Progress"""
import sqlite3
from pathlib import Path

DB = Path("F:/OSINT_WAREHOUSE/osint_master.db")

conn = sqlite3.connect(str(DB))

# Get total works by technology
print("=" * 80)
print("V3 TEST PROGRESS - CURRENT DATABASE STATE")
print("=" * 80)
print()

total = conn.execute("SELECT COUNT(*) FROM openalex_works WHERE validation_keyword IS NOT NULL").fetchone()[0]
print(f"Total works with validation: {total:,}")
print()

print("Works by technology:")
print("-" * 60)
for row in conn.execute("""
    SELECT technology_domain, COUNT(*)
    FROM openalex_works
    WHERE validation_keyword IS NOT NULL
    GROUP BY technology_domain
    ORDER BY technology_domain
"""):
    tech, count = row
    print(f"  {tech:20s}: {count:6,}")

print("-" * 60)
print(f"  {'TOTAL':20s}: {total:6,}")
print()

# Get last integration info
print("Last integration:")
for row in conn.execute("""
    SELECT integration_date, notes, SUM(works_processed)
    FROM openalex_integration_log
    GROUP BY integration_date, notes
    ORDER BY integration_date DESC
    LIMIT 1
"""):
    date, notes, works = row
    print(f"  Date: {date}")
    print(f"  Notes: {notes}")
    print(f"  Works: {works:,}")

conn.close()

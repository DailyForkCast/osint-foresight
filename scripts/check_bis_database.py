#!/usr/bin/env python3
"""Quick check of BIS Entity List in database"""
import sqlite3

db = "F:/OSINT_WAREHOUSE/osint_master.db"
conn = sqlite3.connect(db)
cur = conn.cursor()

print("=" * 80)
print("BIS ENTITY LIST - DATABASE STATUS")
print("=" * 80)

# Total count
cur.execute("SELECT COUNT(*) FROM bis_entity_list")
total = cur.fetchone()[0]
print(f"\nTotal entities: {total}")

# Chinese entities
cur.execute("SELECT COUNT(*) FROM bis_entity_list WHERE country LIKE '%China%' OR country LIKE '%Hong Kong%'")
chinese = cur.fetchone()[0]
print(f"Chinese entities: {chinese}")

# Sample Chinese entities
print("\nSample Chinese entities:")
cur.execute("""
    SELECT entity_name, country, reason_for_listing
    FROM bis_entity_list
    WHERE country LIKE '%China%' OR country LIKE '%Hong Kong%'
    LIMIT 10
""")
for row in cur.fetchall():
    name = row[0][:50] + '...' if len(row[0]) > 50 else row[0]
    print(f"  - {name}")
    print(f"    Country: {row[1]}")
    print(f"    Reason: {row[2][:70] + '...' if row[2] and len(row[2]) > 70 else row[2]}")
    print()

# Reasons breakdown
print("\nListing reasons (top 10):")
cur.execute("""
    SELECT reason_for_listing, COUNT(*) as count
    FROM bis_entity_list
    GROUP BY reason_for_listing
    ORDER BY count DESC
    LIMIT 10
""")
for row in cur.fetchall():
    reason = row[0][:60] + '...' if row[0] and len(row[0]) > 60 else row[0]
    print(f"  {reason}: {row[1]}")

conn.close()

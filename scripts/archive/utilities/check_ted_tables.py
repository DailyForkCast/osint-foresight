#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('F:/OSINT_WAREHOUSE/osint_master.db')
cursor = conn.cursor()

# Get all TED tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'ted%' ORDER BY name")
tables = cursor.fetchall()

print("="*80)
print("TED Tables Analysis:")
print("="*80)
for table_name in tables:
    table = table_name[0]
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"{table:50} {count:>10,} records")

# Check for CRRC/COSCO in usaspending
print("\n" + "="*80)
print("Searching USAspending for rail/shipping keywords:")
print("="*80)

keywords = [
    ('%rail%', 'Rail'),
    ('%CRRC%', 'CRRC'),
    ('%locomotive%', 'Locomotive'),
    ('%shipping%', 'Shipping'),
    ('%COSCO%', 'COSCO'),
    ('%maritime%', 'Maritime'),
    ('%transit%', 'Transit'),
]

for pattern, label in keywords:
    cursor.execute("""
        SELECT COUNT(*)
        FROM usaspending_china_comprehensive
        WHERE recipient_name LIKE ?
    """, (pattern,))
    count = cursor.fetchone()[0]
    print(f"{label:20} {count:>5} matches")

# Check if there are other TED tables with actual contract data
print("\n" + "="*80)
print("Checking ted_china_contracts_fixed:")
print("="*80)
cursor.execute("SELECT COUNT(*) FROM ted_china_contracts_fixed")
print(f"Total records: {cursor.fetchone()[0]:,}")

cursor.execute("""
    SELECT vendor_name, COUNT(*) as cnt
    FROM ted_china_contracts_fixed
    GROUP BY vendor_name
    ORDER BY cnt DESC
    LIMIT 20
""")
print("\nTop vendors:")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]}")

conn.close()

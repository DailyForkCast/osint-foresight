#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect("F:/OSINT_DATA/osint_master.db")
cursor = conn.cursor()

# Check total patents
cursor.execute("SELECT COUNT(*) FROM patents")
total = cursor.fetchone()[0]
print(f"Total patents in database: {total:,}")

# Check by company
print("\nPatents by company:")
cursor.execute("""
    SELECT company_name, COUNT(*) as count
    FROM patents
    GROUP BY company_name
    ORDER BY count DESC
""")
for company, count in cursor.fetchall():
    print(f"  {company}: {count:,}")

# Check collection stats
print("\nCollection statistics:")
cursor.execute("""
    SELECT query_name, total_collected, total_available
    FROM patent_collection_stats
    ORDER BY total_collected DESC
    LIMIT 10
""")
for query, collected, available in cursor.fetchall():
    print(f"  {query}: {collected:,} of {available:,}")

conn.close()

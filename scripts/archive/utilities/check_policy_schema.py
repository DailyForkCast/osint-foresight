#!/usr/bin/env python3
"""Check database schema for policy document storage"""
import sqlite3

db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 70)
print("CHECKING DATABASE SCHEMA FOR POLICY DOCUMENTS")
print("=" * 70)
print()

# Check for any tables related to policies, strategies, laws, regulations
cursor.execute("""
    SELECT name, type
    FROM sqlite_master
    WHERE type='table'
    AND (name LIKE '%polic%'
         OR name LIKE '%strateg%'
         OR name LIKE '%law%'
         OR name LIKE '%regulation%'
         OR name LIKE '%document%'
         OR name LIKE '%framework%'
         OR name LIKE '%plan%')
    ORDER BY name
""")

policy_tables = cursor.fetchall()
if policy_tables:
    print("Policy-related tables found:")
    for name, ttype in policy_tables:
        print(f"  - {name} ({ttype})")

        # Get schema
        cursor.execute(f"PRAGMA table_info({name})")
        columns = cursor.fetchall()
        if columns:
            print(f"    Columns:")
            for col in columns:
                col_id, col_name, col_type, not_null, default, pk = col
                print(f"      {col_name} ({col_type})")
        print()
else:
    print("No policy-related tables found.")
    print()

# Check if there are any generic document/publication tables
print("=" * 70)
print("CHECKING FOR GENERAL DOCUMENT TABLES")
print("=" * 70)
print()

cursor.execute("""
    SELECT name
    FROM sqlite_master
    WHERE type='table'
    ORDER BY name
""")

all_tables = [row[0] for row in cursor.fetchall()]
print(f"Total tables in database: {len(all_tables)}")
print()

# Look for promising tables
promising = [t for t in all_tables if any(keyword in t.lower()
    for keyword in ['tech', 'publication', 'report', 'bilateral', 'event'])]

if promising:
    print("Potentially relevant tables:")
    for table in promising:
        print(f"\n{table}:")
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        for col in columns:
            col_id, col_name, col_type, not_null, default, pk = col
            print(f"  {col_name} ({col_type})")

conn.close()

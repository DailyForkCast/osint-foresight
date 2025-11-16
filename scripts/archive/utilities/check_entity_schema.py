#!/usr/bin/env python3
"""Check schema of entity-related tables"""
import sqlite3

db_path = 'F:/OSINT_WAREHOUSE/osint_master.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check entity_linkages schema
print("=== entity_linkages schema ===")
cursor.execute("PRAGMA table_info(entity_linkages)")
for col in cursor.fetchall():
    print(f"  {col[1]} ({col[2]})")

# Check cross_system_entity_correlation schema
print("\n=== cross_system_entity_correlation schema ===")
cursor.execute("PRAGMA table_info(cross_system_entity_correlation)")
for col in cursor.fetchall():
    print(f"  {col[1]} ({col[2]})")

# Sample some entity_linkages data
print("\n=== entity_linkages sample ===")
cursor.execute("SELECT * FROM entity_linkages LIMIT 3")
for row in cursor.fetchall():
    print(f"  {row}")

conn.close()

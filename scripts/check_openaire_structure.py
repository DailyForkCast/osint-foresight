#!/usr/bin/env python3
"""Check OpenAIRE database structure"""

import sqlite3
from pathlib import Path

# Connect to OpenAIRE database
db_path = "F:/OSINT_Data/openaire_comprehensive_20250921/openaire_comprehensive.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check all tables
print("=== OpenAIRE Database Structure ===\n")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print(f"Tables found: {[t[0] for t in tables]}\n")

# Check collaborations table
print("=== Collaborations Table ===")
cursor.execute("PRAGMA table_info(collaborations)")
cols = cursor.fetchall()
print(f"Columns: {[c[1] for c in cols]}")

cursor.execute("SELECT COUNT(*) FROM collaborations")
total = cursor.fetchone()[0]
print(f"Total collaborations: {total:,}")

cursor.execute("SELECT * FROM collaborations WHERE country1 = 'China' OR country2 = 'China' LIMIT 5")
china_collabs = cursor.fetchall()
print(f"China collaborations found: {len(china_collabs)}")
for collab in china_collabs:
    print(f"  - {collab}")

# Check country_overview table
print("\n=== Country Overview Table ===")
cursor.execute("PRAGMA table_info(country_overview)")
cols = cursor.fetchall()
print(f"Columns: {[c[1] for c in cols]}")

cursor.execute("SELECT * FROM country_overview WHERE country_code = 'CN' OR country_name = 'China' LIMIT 5")
china_overview = cursor.fetchall()
print(f"China overview entries: {len(china_overview)}")
for entry in china_overview:
    print(f"  - {entry}")

# Check research_products for China
print("\n=== Research Products ===")
cursor.execute("SELECT COUNT(*) FROM research_products WHERE country_code = 'CN'")
china_products = cursor.fetchone()[0]
print(f"China research products: {china_products:,}")

conn.close()
print("\n=== Analysis Complete ===")

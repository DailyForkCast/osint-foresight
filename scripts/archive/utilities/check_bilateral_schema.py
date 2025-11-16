#!/usr/bin/env python3
import sqlite3

DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Check bilateral_countries schema
cursor.execute("PRAGMA table_info(bilateral_countries)")
columns = cursor.fetchall()
print("bilateral_countries columns:")
for col in columns:
    print(f"  {col[1]} ({col[2]})")

# Check sample data
cursor.execute("SELECT * FROM bilateral_countries LIMIT 5")
rows = cursor.fetchall()
print("\nSample data:")
for row in rows:
    print(f"  {row}")

conn.close()

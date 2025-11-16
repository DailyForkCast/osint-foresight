#!/usr/bin/env python3
import sqlite3

DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("bilateral_corporate_links schema:")
cursor.execute("PRAGMA table_info(bilateral_corporate_links)")
columns = cursor.fetchall()
for col in columns:
    print(f"  {col[1]:40} {col[2]:15} {'PRIMARY KEY' if col[5] else ''}")

print("\nSample record:")
cursor.execute("SELECT * FROM bilateral_corporate_links LIMIT 1")
row = cursor.fetchone()
if row:
    for i, val in enumerate(row):
        col_name = columns[i][1]
        print(f"  {col_name}: {val}")
else:
    print("  (No records yet)")

conn.close()

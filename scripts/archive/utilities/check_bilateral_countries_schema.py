#!/usr/bin/env python3
import sqlite3
from pathlib import Path

conn = sqlite3.connect("F:/OSINT_WAREHOUSE/osint_master.db")
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(bilateral_countries)")
columns = cursor.fetchall()

print("bilateral_countries columns:")
for col in columns:
    print(f"  {col[1]} ({col[2]})")

conn.close()

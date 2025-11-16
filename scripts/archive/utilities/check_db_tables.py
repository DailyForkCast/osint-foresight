#!/usr/bin/env python3
import sqlite3
from pathlib import Path

db_path = Path("F:/OSINT_Data/openalex_analytics/openalex_chinese_research.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]

print("Tables in database:")
for table in tables:
    print(f"  - {table}")

conn.close()

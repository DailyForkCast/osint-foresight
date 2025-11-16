#!/usr/bin/env python3
"""Check SEC 13D/13G table schema"""
import sqlite3

conn = sqlite3.connect("F:/OSINT_WAREHOUSE/osint_master.db")
cur = conn.cursor()

print("SEC 13D/13G Table Schema:")
cur.execute("PRAGMA table_info(sec_13d_13g_filings)")
for row in cur.fetchall():
    print(f"  {row[1]} ({row[2]})")

conn.close()

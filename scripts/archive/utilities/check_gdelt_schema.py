#!/usr/bin/env python3
"""Check GDELT Events schema"""

import sqlite3

conn = sqlite3.connect(r'F:/OSINT_WAREHOUSE/osint_master.db', uri=True)
cursor = conn.cursor()

# Get schema
cursor.execute("PRAGMA table_info(gdelt_events)")
schema = cursor.fetchall()

print("gdelt_events schema:")
for col in schema:
    print(f"  {col[1]} ({col[2]})")

conn.close()

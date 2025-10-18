#!/usr/bin/env python3
import sqlite3
from pathlib import Path

def check_cordis_schema():
    db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")
    if not db_path.exists():
        print("Database not found")
        return

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Check what CORDIS tables exist
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%cordis%'")
    cordis_tables = cur.fetchall()

    print("CORDIS Tables found:")
    for table in cordis_tables:
        print(f"- {table[0]}")

    # Check schema for each table
    for table in cordis_tables:
        table_name = table[0]
        print(f"\nSchema for {table_name}:")
        cur.execute(f"PRAGMA table_info({table_name})")
        columns = cur.fetchall()
        for col in columns:
            print(f"  {col[1]} ({col[2]})")

        # Show sample data
        cur.execute(f"SELECT * FROM {table_name} LIMIT 3")
        samples = cur.fetchall()
        print(f"\nSample data from {table_name}:")
        for row in samples:
            print(f"  {row}")

    conn.close()

if __name__ == "__main__":
    check_cordis_schema()

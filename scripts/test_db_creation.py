#!/usr/bin/env python3
import sqlite3

db_path = "F:/OSINT_DATA/osint_master.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Drop existing tables if needed for clean test
    cursor.execute("DROP TABLE IF EXISTS patent_inventors")
    cursor.execute("DROP TABLE IF EXISTS patent_applicants")
    cursor.execute("DROP TABLE IF EXISTS patent_collection_stats")
    cursor.execute("DROP TABLE IF EXISTS patents")

    # Create patents table
    cursor.execute("""
        CREATE TABLE patents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            publication_number TEXT UNIQUE,
            title TEXT,
            abstract TEXT,
            country TEXT,
            publication_date TEXT,
            query_source TEXT,
            company_name TEXT,
            technology_area TEXT,
            collection_date TEXT,
            data_source TEXT DEFAULT 'EPO'
        )
    """)
    print("Patents table created successfully")

    # Test if column exists
    cursor.execute("PRAGMA table_info(patents)")
    columns = cursor.fetchall()
    print("\nColumns in patents table:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")

    conn.commit()
    print("\nAll tables created successfully!")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    conn.close()

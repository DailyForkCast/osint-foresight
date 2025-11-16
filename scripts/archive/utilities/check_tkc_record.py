#!/usr/bin/env python3
"""Check actual T K C ENTERPRISES record in database to understand detection."""

import sqlite3
from pathlib import Path
import json

db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")
conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row

cursor = conn.execute("""
    SELECT transaction_id, recipient_name, pop_country_name, pop_country_code,
           recipient_country_name, recipient_country_code,
           award_description, detection_types, detection_details
    FROM usaspending_china_305
    WHERE transaction_id='20841746'
    LIMIT 1
""")

row = cursor.fetchone()
if row:
    row_dict = dict(row)
    print("T K C ENTERPRISES Record (Transaction 20841746):")
    print("="*100)
    for key, value in row_dict.items():
        if key == 'detection_details':
            try:
                details = json.loads(value) if value else None
                print(f"{key}: {json.dumps(details, indent=2)}")
            except:
                print(f"{key}: {value}")
        else:
            print(f"{key}: {value}")
else:
    print("Record not found!")

conn.close()

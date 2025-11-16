#!/usr/bin/env python3
"""
Examine Taiwan records that were incorrectly detected as China.
"""

import sqlite3
from pathlib import Path

db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")
conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row

print("="*100)
print("TAIWAN RECORDS INVESTIGATION")
print("="*100)

# Check 101-column format
print("\n101-COLUMN FORMAT:")
cursor = conn.execute("""
    SELECT * FROM usaspending_china_101
    WHERE recipient_country_name LIKE '%TAIWAN%'
       OR recipient_country_name LIKE '%TWN%'
       OR pop_country_name LIKE '%TAIWAN%'
       OR pop_country_name LIKE '%TWN%'
""")
for row in cursor.fetchall():
    print(f"\nTransaction ID: {row['transaction_id']}")
    print(f"Recipient: {row['recipient_name']}")
    print(f"Recipient Country: {row['recipient_country_name']}")
    print(f"POP Country: {row['pop_country_name']}")
    print(f"Confidence: {row['highest_confidence']}")
    print(f"Detection Types: {row['detection_types']}")

# Check 305-column format
print("\n\n305-COLUMN FORMAT:")
cursor = conn.execute("""
    SELECT * FROM usaspending_china_305
    WHERE recipient_country_name LIKE '%TAIWAN%'
       OR recipient_country_code = 'TWN'
       OR pop_country_name LIKE '%TAIWAN%'
       OR pop_country_code = 'TWN'
    LIMIT 10
""")
for row in cursor.fetchall():
    print(f"\nTransaction ID: {row['transaction_id']}")
    print(f"Recipient: {row['recipient_name']}")
    print(f"Recipient Country: {row['recipient_country_name']} ({row['recipient_country_code']})")
    print(f"POP Country: {row['pop_country_name']} ({row['pop_country_code']})")
    print(f"Confidence: {row['highest_confidence']}")
    print(f"Detection Types: {row['detection_types']}")

# Check 206-column format
print("\n\n206-COLUMN FORMAT:")
cursor = conn.execute("""
    SELECT * FROM usaspending_china_comprehensive
    WHERE recipient_country LIKE '%TAIWAN%'
       OR pop_country LIKE '%TAIWAN%'
       OR sub_awardee_country LIKE '%TAIWAN%'
""")
for row in cursor.fetchall():
    print(f"\nTransaction ID: {row['transaction_id']}")
    print(f"Recipient: {row['recipient_name']}")
    print(f"Recipient Country: {row['recipient_country']}")
    print(f"POP Country: {row['pop_country']}")
    print(f"Sub-Awardee Country: {row['sub_awardee_country']}")
    print(f"Confidence: {row['highest_confidence']}")
    print(f"Detection Types: {row['detection_types']}")

conn.close()

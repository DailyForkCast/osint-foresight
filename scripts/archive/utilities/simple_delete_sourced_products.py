#!/usr/bin/env python3
"""
Simple script to just delete china_sourced_product records from main DB
(They're already in supply chain DB)
"""

import sqlite3
import time

MAIN_DB = "F:/OSINT_WAREHOUSE/osint_master.db"

print("=" * 80)
print("DELETING CHINA_SOURCED_PRODUCT RECORDS FROM MAIN DB")
print("=" * 80)

# Wait a moment for any locks to clear
time.sleep(2)

try:
    conn = sqlite3.connect(MAIN_DB, timeout=60, isolation_level='IMMEDIATE')
    cursor = conn.cursor()

    # Count
    cursor.execute("""
        SELECT COUNT(*) FROM usaspending_china_305
        WHERE detection_types = '["china_sourced_product"]'
    """)
    count = cursor.fetchone()[0]
    print(f"\nRecords to delete: {count:,}")

    if count > 0:
        # Delete
        print("Deleting...")
        cursor.execute("""
            DELETE FROM usaspending_china_305
            WHERE detection_types = '["china_sourced_product"]'
        """)

        conn.commit()
        print(f"[OK] Deleted {count:,} records")
    else:
        print("No records to delete")

    conn.close()

except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()

#!/usr/bin/env python3
"""
Delete china_sourced_product records using WAL mode for better concurrency
"""

import sqlite3
import time

MAIN_DB = "F:/OSINT_WAREHOUSE/osint_master.db"

print("=" * 80)
print("DELETING CHINA_SOURCED_PRODUCT RECORDS (WAL MODE)")
print("=" * 80)

time.sleep(3)

try:
    conn = sqlite3.connect(MAIN_DB, timeout=120)
    cursor = conn.cursor()

    # Enable WAL mode for better concurrency
    print("\nEnabling WAL mode...")
    cursor.execute("PRAGMA journal_mode=WAL")
    print(f"Journal mode: {cursor.fetchone()[0]}")

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

        deleted = cursor.rowcount
        conn.commit()
        print(f"[OK] Deleted {deleted:,} records")

        # Verify
        cursor.execute("""
            SELECT COUNT(*) FROM usaspending_china_305
            WHERE detection_types = '["china_sourced_product"]'
        """)
        remaining = cursor.fetchone()[0]
        print(f"Remaining: {remaining:,}")
    else:
        print("No records to delete")

    conn.close()

except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()

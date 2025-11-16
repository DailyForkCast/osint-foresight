#!/usr/bin/env python3
"""
Clean up legacy TED records by archive name (2006-2022)
"""

import sqlite3

db_path = "F:/OSINT_WAREHOUSE/osint_master.db"

print("="*80)
print("TED LEGACY CLEANUP BY ARCHIVE")
print("="*80)

with sqlite3.connect(db_path) as conn:
    cur = conn.cursor()

    # Count records by archive year
    cur.execute("""
        SELECT
            SUBSTR(source_archive, 13, 4) as year,
            COUNT(*) as count
        FROM ted_contracts_production
        GROUP BY year
        ORDER BY year
    """)

    print("\nRecords by archive year:")
    for year, count in cur.fetchall():
        print(f"  {year}: {count:,}")

    # Delete 2006-2022 records (legacy format)
    print("\nDeleting legacy records (2006-2022)...")
    deleted_count = 0
    for year in range(2006, 2023):
        cur.execute("""
            DELETE FROM ted_contracts_production
            WHERE source_archive LIKE ?
        """, (f"TED_monthly_{year}%",))
        deleted = cur.rowcount
        deleted_count += deleted
        if deleted > 0:
            print(f"  {year}: Deleted {deleted:,} records")

    conn.commit()

    print(f"\nTotal deleted: {deleted_count:,}")

    # Verify what remains
    cur.execute("SELECT COUNT(*) FROM ted_contracts_production")
    remaining = cur.fetchone()[0]
    print(f"Total remaining: {remaining:,}")

    # Count by year
    cur.execute("""
        SELECT
            SUBSTR(source_archive, 13, 4) as year,
            COUNT(*) as count
        FROM ted_contracts_production
        GROUP BY year
        ORDER BY year
    """)

    print("\nRemaining records by year:")
    for year, count in cur.fetchall():
        print(f"  {year}: {count:,}")

print("\n" + "="*80)
print("CLEANUP COMPLETE")
print("="*80)

#!/usr/bin/env python3
"""
Clear May-August 2025 TED contracts to prepare for reprocessing with bug fix.
"""
import sqlite3
import time
import sys

DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"
ARCHIVES_TO_CLEAR = [
    "TED_monthly_2025_05.tar.gz",
    "TED_monthly_2025_06.tar.gz",
    "TED_monthly_2025_07.tar.gz",
    "TED_monthly_2025_08.tar.gz"
]

def clear_archives(max_retries=5):
    """Clear contracts from specified archives with retry logic."""
    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1}/{max_retries}: Connecting to database...")
            conn = sqlite3.connect(DB_PATH, timeout=60)
            conn.execute("PRAGMA journal_mode=WAL")  # Enable WAL mode for better concurrency
            cursor = conn.cursor()

            # Build DELETE query
            archive_list = ", ".join([f"'{a}'" for a in ARCHIVES_TO_CLEAR])
            query = f"DELETE FROM ted_contracts_production WHERE source_archive IN ({archive_list})"

            print(f"Executing: {query}")
            cursor.execute(query)
            deleted = cursor.rowcount

            conn.commit()
            conn.close()

            print(f"\n✓ SUCCESS: Deleted {deleted} contracts from May-August 2025")
            return deleted

        except sqlite3.OperationalError as e:
            if "locked" in str(e):
                print(f"Database locked, waiting 5 seconds before retry...")
                conn.close() if 'conn' in locals() else None
                time.sleep(5)
            else:
                raise
        except Exception as e:
            print(f"ERROR: {e}")
            conn.close() if 'conn' in locals() else None
            raise

    print("FAILED: Could not acquire database lock after all retries")
    sys.exit(1)

if __name__ == "__main__":
    clear_archives()

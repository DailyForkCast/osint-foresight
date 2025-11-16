#!/usr/bin/env python3
"""
Clean up legacy TED records and re-process with enhanced contractor extraction
"""

import sqlite3
from pathlib import Path

db_path = "F:/OSINT_WAREHOUSE/osint_master.db"

print("="*80)
print("TED LEGACY CLEANUP")
print("="*80)

with sqlite3.connect(db_path) as conn:
    cur = conn.cursor()

    # Count legacy records
    cur.execute("SELECT COUNT(*) FROM ted_contracts_production WHERE publication_date < '2023-01-01'")
    legacy_count = cur.fetchone()[0]
    print(f"\nLegacy records (pre-2023): {legacy_count:,}")

    # Count with contractor names
    cur.execute("""
        SELECT COUNT(*)
        FROM ted_contracts_production
        WHERE publication_date < '2023-01-01'
        AND contractor_name IS NOT NULL
        AND contractor_name != ''
    """)
    with_names = cur.fetchone()[0]
    print(f"With contractor names: {with_names} ({100*with_names/legacy_count:.2f}%)")

    # Delete legacy records to enable re-processing
    print(f"\nDeleting {legacy_count:,} legacy records to enable re-processing...")
    cur.execute("DELETE FROM ted_contracts_production WHERE publication_date < '2023-01-01'")
    conn.commit()

    # Verify deletion
    cur.execute("SELECT COUNT(*) FROM ted_contracts_production WHERE publication_date < '2023-01-01'")
    remaining = cur.fetchone()[0]
    print(f"Remaining legacy records: {remaining}")

    # Check total remaining
    cur.execute("SELECT COUNT(*) FROM ted_contracts_production")
    total_remaining = cur.fetchone()[0]
    print(f"Total remaining records: {total_remaining:,} (should be 2023-2024 only)")

print("\n" + "="*80)
print("CLEANUP COMPLETE - Ready for re-processing")
print("="*80)

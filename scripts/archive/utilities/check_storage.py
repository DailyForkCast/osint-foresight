#!/usr/bin/env python3
"""Check storage requirements for GKG collection"""

import sqlite3
import os
from pathlib import Path

db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")

# Check current database size
db_size_mb = db_path.stat().st_size / (1024**2)

print(f"Current database size: {db_size_mb:,.1f} MB")

# Check GKG table size
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Count current GKG records
cursor.execute("SELECT COUNT(*) FROM gdelt_gkg")
current_count = cursor.fetchone()[0]

print(f"Current GKG records: {current_count:,}")

# Get average row size by checking a sample
if current_count > 0:
    cursor.execute("""
        SELECT
            gkg_record_id,
            source_common_name,
            document_identifier,
            themes,
            locations,
            persons,
            organizations
        FROM gdelt_gkg
        LIMIT 100
    """)

    samples = cursor.fetchall()
    total_bytes = 0

    for row in samples:
        for field in row:
            if field:
                total_bytes += len(str(field))

    avg_bytes_per_record = total_bytes / len(samples) if samples else 0

    print(f"\nEstimated average record size: {avg_bytes_per_record:,.0f} bytes")

    # Estimate for 3 days
    records_per_day = 60709  # From Feb 3 test
    total_days = 3
    total_new_records = records_per_day * total_days

    estimated_new_data_mb = (total_new_records * avg_bytes_per_record) / (1024**2)

    # Add overhead for indexes, SQLite metadata (~30%)
    estimated_with_overhead = estimated_new_data_mb * 1.3

    print(f"\nStorage Estimates for 3 Days:")
    print(f"  New GKG records: {total_new_records:,}")
    print(f"  Raw data: {estimated_new_data_mb:,.1f} MB")
    print(f"  With indexes/overhead: {estimated_with_overhead:,.1f} MB")
    print(f"  Total database after: {db_size_mb + estimated_with_overhead:,.1f} MB")

# Check available space on F: drive
import shutil
total, used, free = shutil.disk_usage("F:/")
free_gb = free / (1024**3)

print(f"\nF: drive free space: {free_gb:,.1f} GB")

conn.close()

#!/usr/bin/env python3
"""
Monitor USAspending v2.0 reprocessing progress
Run this periodically to check status
"""

import sqlite3
from pathlib import Path
from datetime import datetime

def monitor():
    print("\n" + "="*80)
    print(f"REPROCESSING MONITOR - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")

    # Check database
    db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")
    if not db_path.exists():
        print("ERROR: Database not found")
        return

    conn = sqlite3.connect(db_path, timeout=30)
    cursor = conn.cursor()

    # Check if table exists
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='usaspending_china_374_v2'
    """)

    if not cursor.fetchone():
        print("Table usaspending_china_374_v2 not created yet")
        print("Processing may just be starting...")
        conn.close()
        return

    # Get total count
    cursor.execute("SELECT COUNT(*) FROM usaspending_china_374_v2")
    total = cursor.fetchone()[0]

    print(f"TOTAL DETECTIONS SO FAR: {total:,}\n")

    # By origin
    cursor.execute("""
        SELECT
            entity_country_of_origin,
            COUNT(*) as count,
            SUM(federal_action_obligation) as total_value
        FROM usaspending_china_374_v2
        GROUP BY entity_country_of_origin
        ORDER BY total_value DESC
    """)

    print("BY ORIGIN:")
    print("-" * 80)
    for origin, count, value in cursor.fetchall():
        print(f"  {origin:15s}: {count:8,} entities, ${value:>15,.0f}")

    # By confidence
    cursor.execute("""
        SELECT
            confidence_level,
            COUNT(*) as count
        FROM usaspending_china_374_v2
        GROUP BY confidence_level
        ORDER BY count DESC
    """)

    print("\nBY CONFIDENCE LEVEL:")
    print("-" * 80)
    for conf, count in cursor.fetchall():
        print(f"  {conf:15s}: {count:8,} detections")

    # Top 5 PRC entities
    cursor.execute("""
        SELECT
            recipient_name,
            COUNT(*) as contracts,
            SUM(federal_action_obligation) as total_value
        FROM usaspending_china_374_v2
        WHERE entity_country_of_origin = 'CN'
        GROUP BY recipient_name
        ORDER BY total_value DESC
        LIMIT 5
    """)

    print("\nTOP 5 PRC ENTITIES:")
    print("-" * 80)
    for name, contracts, value in cursor.fetchall():
        print(f"  {name[:50]:50s} {contracts:4d} contracts ${value:>12,.0f}")

    # Check for PRI-DJI (should be 0)
    cursor.execute("""
        SELECT COUNT(*) FROM usaspending_china_374_v2
        WHERE recipient_name LIKE '%PRI%DJI%'
    """)
    pri_dji_count = cursor.fetchone()[0]

    print("\nVALIDATION CHECKS:")
    print("-" * 80)
    if pri_dji_count > 0:
        print(f"  ERROR: Found {pri_dji_count} PRI-DJI entities (should be 0)")
    else:
        print(f"  OK - PRI-DJI entities correctly excluded (0 found)")

    # Estimate progress (assuming 90M total records, 42K detections expected)
    if total > 0:
        estimated_total = 42300  # From our extrapolation
        progress_pct = (total / estimated_total) * 100
        print(f"  Estimated progress: {progress_pct:.1f}% complete")

    conn.close()

    print("\n" + "="*80)
    print("Check again in 30-60 minutes for updated progress")
    print("="*80 + "\n")

if __name__ == "__main__":
    try:
        monitor()
    except Exception as e:
        print(f"Error: {e}")
        print("\nProcessing may still be starting up...")

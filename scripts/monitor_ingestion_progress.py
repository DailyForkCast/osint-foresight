#!/usr/bin/env python3
"""
Monitor Research Database Ingestion Progress

Usage:
    python scripts/monitor_ingestion_progress.py
"""

import sqlite3
import time
from datetime import datetime

def monitor():
    db_path = "F:/OSINT_WAREHOUSE/research_mapping_comprehensive.db"

    while True:
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Get counts
            cursor.execute('SELECT COUNT(*) FROM unified_publications')
            pubs = cursor.fetchone()[0]

            cursor.execute('SELECT COUNT(*) FROM research_authors')
            authors = cursor.fetchone()[0]

            cursor.execute('SELECT COUNT(*) FROM research_institutions')
            institutions = cursor.fetchone()[0]

            cursor.execute('SELECT COUNT(*) FROM processing_status WHERE status="complete"')
            completed = cursor.fetchone()[0]

            # Get latest partition being processed
            cursor.execute('''
                SELECT source_file
                FROM processing_status
                WHERE status="complete"
                ORDER BY completed_at DESC
                LIMIT 1
            ''')
            latest = cursor.fetchone()
            latest_file = latest[0] if latest else "Unknown"

            conn.close()

            # Calculate estimates
            total_partitions = 230
            pct_complete = (completed / total_partitions * 100) if completed > 0 else 0
            est_total = (pubs / completed * total_partitions) if completed > 0 else 0
            remaining = total_partitions - completed

            # Print status
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"\n[{timestamp}] INGESTION STATUS")
            print("=" * 60)
            print(f"Progress: {completed}/{total_partitions} partitions ({pct_complete:.1f}%)")
            print(f"Publications: {pubs:,}")
            print(f"Authors: {authors:,}")
            print(f"Institutions: {institutions:,}")
            print(f"Latest: {latest_file}")
            print(f"Estimated final: ~{est_total:,.0f} publications")
            print(f"Remaining: {remaining} partitions")

            if completed >= total_partitions:
                print("\n✓ INGESTION COMPLETE!")
                break

        except Exception as e:
            print(f"Error: {e}")

        # Wait 5 minutes
        time.sleep(300)

if __name__ == "__main__":
    print("Monitoring ingestion progress (updates every 5 minutes)...")
    print("Press Ctrl+C to stop")
    try:
        monitor()
    except KeyboardInterrupt:
        print("\nMonitoring stopped")

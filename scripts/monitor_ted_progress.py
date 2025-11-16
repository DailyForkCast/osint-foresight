#!/usr/bin/env python3
"""
Monitor TED Production Processing Progress
Real-time status of archive processing and China contract detection
"""

import json
import sqlite3
import time
from pathlib import Path
from datetime import datetime

def monitor_progress():
    """Display real-time processing progress"""

    checkpoint_file = Path("C:/Projects/OSINT - Foresight/data/ted_production_checkpoint.json")
    db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")

    while True:
        print("\n" + "="*80)
        print("TED PRODUCTION PROCESSING - LIVE MONITOR")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)

        # Read checkpoint
        if checkpoint_file.exists():
            with open(checkpoint_file) as f:
                checkpoint = json.load(f)

            stats = checkpoint.get('stats', {})

            print(f"\n📦 ARCHIVES:")
            print(f"  Processed: {stats.get('archives_processed', 0)}/{stats.get('archives_total', 139)}")
            print(f"  Inner archives: {stats.get('inner_archives_processed', 0)}")
            print(f"  Current: {stats.get('current_archive', 'N/A')}")

            print(f"\n📄 XML FILES:")
            print(f"  Processed: {stats.get('xml_files_processed', 0):,}")

            print(f"\n🇨🇳 CHINA CONTRACTS:")
            print(f"  Found: {stats.get('china_contracts_found', 0):,}")

            print(f"\n⚠️  ERRORS:")
            print(f"  Count: {len(stats.get('errors', []))}")

            # Database stats
            if db_path.exists():
                try:
                    conn = sqlite3.connect(db_path)
                    cur = conn.cursor()

                    cur.execute("SELECT COUNT(*) FROM ted_contracts_production")
                    total_in_db = cur.fetchone()[0]

                    cur.execute("SELECT COUNT(*) FROM ted_contracts_production WHERE is_chinese_related = 1")
                    china_in_db = cur.fetchone()[0]

                    conn.close()

                    print(f"\n💾 DATABASE:")
                    print(f"  Total contracts: {total_in_db:,}")
                    print(f"  China contracts: {china_in_db:,}")

                except Exception as e:
                    print(f"\n💾 DATABASE: Error - {e}")

            # Processing rate
            if stats.get('start_time'):
                start = datetime.fromisoformat(stats['start_time'])
                elapsed = (datetime.now() - start).total_seconds()
                if elapsed > 0:
                    archives_per_hour = (stats.get('archives_processed', 0) / elapsed) * 3600
                    xml_per_minute = (stats.get('xml_files_processed', 0) / elapsed) * 60

                    print(f"\n⚡ PROCESSING RATE:")
                    print(f"  Archives/hour: {archives_per_hour:.1f}")
                    print(f"  XML files/minute: {xml_per_minute:.1f}")

                    remaining = stats.get('archives_total', 139) - stats.get('archives_processed', 0)
                    if archives_per_hour > 0:
                        eta_hours = remaining / archives_per_hour
                        print(f"  ETA: {eta_hours:.1f} hours")

        else:
            print("\n⏳ Waiting for checkpoint file...")

        print("\n" + "="*80)
        print("Refreshing in 30 seconds... (Ctrl+C to stop)")
        print("="*80)

        time.sleep(30)


if __name__ == '__main__':
    try:
        monitor_progress()
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped.")

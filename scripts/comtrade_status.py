"""
UN Comtrade Collection Status Checker
Shows current progress and collection statistics
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime


CHECKPOINT_PATH = Path("C:/Projects/OSINT-Foresight/data/comtrade_checkpoint.json")
DATABASE_PATH = Path("F:/OSINT_WAREHOUSE/osint_master.db")


def load_checkpoint():
    """Load checkpoint data"""
    if CHECKPOINT_PATH.exists():
        with open(CHECKPOINT_PATH, 'r') as f:
            return json.load(f)
    return None


def get_database_stats():
    """Get statistics from database"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # Check if table exists
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='comtrade_data'
        """)
        if not cursor.fetchone():
            return None

        # Get total records
        cursor.execute("SELECT COUNT(*) FROM comtrade_data")
        total_records = cursor.fetchone()[0]

        # Get records by year
        cursor.execute("""
            SELECT year, COUNT(*) as count
            FROM comtrade_data
            GROUP BY year
            ORDER BY year DESC
        """)
        by_year = cursor.fetchall()

        # Get records by reporter
        cursor.execute("""
            SELECT reporter_code, COUNT(*) as count
            FROM comtrade_data
            GROUP BY reporter_code
            ORDER BY count DESC
            LIMIT 10
        """)
        by_reporter = cursor.fetchall()

        # Get records by commodity
        cursor.execute("""
            SELECT commodity_code, commodity_description, COUNT(*) as count
            FROM comtrade_data
            GROUP BY commodity_code
            ORDER BY count DESC
            LIMIT 10
        """)
        by_commodity = cursor.fetchall()

        # Get unique combinations
        cursor.execute("""
            SELECT
                COUNT(DISTINCT year) as unique_years,
                COUNT(DISTINCT reporter_code) as unique_reporters,
                COUNT(DISTINCT partner_code) as unique_partners,
                COUNT(DISTINCT commodity_code) as unique_commodities
            FROM comtrade_data
        """)
        uniques = cursor.fetchone()

        # Get date range of collection
        cursor.execute("""
            SELECT
                MIN(collected_date) as first_collection,
                MAX(collected_date) as last_collection
            FROM comtrade_data
        """)
        date_range = cursor.fetchone()

        conn.close()

        return {
            'total_records': total_records,
            'by_year': by_year,
            'by_reporter': by_reporter,
            'by_commodity': by_commodity,
            'unique_years': uniques[0],
            'unique_reporters': uniques[1],
            'unique_partners': uniques[2],
            'unique_commodities': uniques[3],
            'first_collection': date_range[0],
            'last_collection': date_range[1]
        }

    except Exception as e:
        print(f"Error querying database: {e}")
        return None


def print_status():
    """Print collection status"""
    print("="*80)
    print("UN COMTRADE COLLECTION STATUS")
    print("="*80)
    print()

    # Checkpoint status
    checkpoint = load_checkpoint()
    if checkpoint:
        print("CHECKPOINT STATUS:")
        print(f"  Current phase: {checkpoint.get('current_phase', 1)}")
        completed = len(checkpoint.get('completed_requests', []))
        print(f"  Completed requests: {completed:,}")
        if checkpoint.get('last_updated'):
            last_update = datetime.fromisoformat(checkpoint['last_updated'])
            print(f"  Last updated: {last_update.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
    else:
        print("No checkpoint found - collection not started")
        print()

    # Database status
    db_stats = get_database_stats()
    if db_stats:
        print("DATABASE STATISTICS:")
        print(f"  Total records: {db_stats['total_records']:,}")
        print(f"  Unique years: {db_stats['unique_years']}")
        print(f"  Unique reporters: {db_stats['unique_reporters']}")
        print(f"  Unique partners: {db_stats['unique_partners']}")
        print(f"  Unique commodities: {db_stats['unique_commodities']}")
        print()

        if db_stats['first_collection']:
            first = datetime.fromisoformat(db_stats['first_collection'])
            last = datetime.fromisoformat(db_stats['last_collection'])
            print(f"  First collection: {first.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"  Last collection: {last.strftime('%Y-%m-%d %H:%M:%S')}")
            duration = (last - first).total_seconds()
            if duration > 0:
                print(f"  Collection duration: {duration/3600:.1f} hours")
            print()

        print("RECORDS BY YEAR:")
        for year, count in db_stats['by_year']:
            print(f"  {year}: {count:>10,} records")
        print()

        print("TOP 10 REPORTERS:")
        for reporter, count in db_stats['by_reporter']:
            print(f"  {reporter}: {count:>10,} records")
        print()

        print("TOP 10 COMMODITIES:")
        for code, desc, count in db_stats['by_commodity']:
            desc_short = desc[:50] if desc else "Unknown"
            print(f"  {code} - {desc_short:50s} {count:>8,}")
        print()

    else:
        print("No data in database - collection not started")
        print()

    # Phase progress estimates
    print("PHASE PROGRESS ESTIMATES:")

    # Phase 1: 1,200 requests
    # Phase 2: 1,440 requests
    # Phase 3A: 2,520 requests
    # Phase 3B: 8,400 requests
    # Total: 13,560 requests

    if checkpoint:
        completed = len(checkpoint.get('completed_requests', []))
        current_phase = checkpoint.get('current_phase', 1)

        phase_1_total = 1200
        phase_2_total = 1440
        phase_3a_total = 2520
        phase_3b_total = 8400
        total_requests = phase_1_total + phase_2_total + phase_3a_total + phase_3b_total

        if current_phase == 1:
            progress = min(completed, phase_1_total)
            print(f"  Phase 1: {progress}/{phase_1_total} ({progress/phase_1_total*100:.1f}%)")
            print(f"  Phase 2: 0/{phase_2_total} (0.0%)")
            print(f"  Phase 3A: 0/{phase_3a_total} (0.0%)")
            print(f"  Phase 3B: 0/{phase_3b_total} (0.0%)")
        elif current_phase == 2:
            progress = completed - phase_1_total
            print(f"  Phase 1: {phase_1_total}/{phase_1_total} (100.0%) COMPLETE")
            print(f"  Phase 2: {progress}/{phase_2_total} ({progress/phase_2_total*100:.1f}%)")
            print(f"  Phase 3A: 0/{phase_3a_total} (0.0%)")
            print(f"  Phase 3B: 0/{phase_3b_total} (0.0%)")
        elif current_phase == 3:
            progress_3a = min(completed - phase_1_total - phase_2_total, phase_3a_total)
            progress_3b = max(0, completed - phase_1_total - phase_2_total - phase_3a_total)
            print(f"  Phase 1: {phase_1_total}/{phase_1_total} (100.0%) COMPLETE")
            print(f"  Phase 2: {phase_2_total}/{phase_2_total} (100.0%) COMPLETE")
            print(f"  Phase 3A: {progress_3a}/{phase_3a_total} ({progress_3a/phase_3a_total*100:.1f}%)")
            print(f"  Phase 3B: {progress_3b}/{phase_3b_total} ({progress_3b/phase_3b_total*100:.1f}%)")
        else:
            print(f"  All phases complete!")

        print()
        print(f"OVERALL PROGRESS: {completed}/{total_requests} ({completed/total_requests*100:.1f}%)")
        remaining = total_requests - completed
        print(f"Remaining requests: {remaining:,}")
        if remaining > 0:
            # Assume 90 requests per hour
            hours_remaining = remaining / 90
            print(f"Estimated time remaining: {hours_remaining:.1f} hours ({hours_remaining/24:.1f} days)")

    print()
    print("="*80)


if __name__ == '__main__':
    print_status()

#!/usr/bin/env python3
"""
Re-process PatentsView using patent number ranges to determine grant year
Filing dates are corrupted - use sequential patent numbers instead
"""

import sqlite3
from datetime import datetime

DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"

# Patent number milestones (from USPTO official records)
PATENT_MILESTONES = [
    (10000000, 2018, 6),   # Patent 10M: June 2018
    (11000000, 2021, 5),   # Patent 11M: May 2021
    (11500000, 2022, 6),   # Est: Mid 2022
    (12000000, 2024, 1),   # Est: Early 2024
    (12500000, 2025, 6),   # Est: Mid 2025
]

def estimate_grant_year_from_patent_id(patent_id_str):
    """
    Estimate grant year from sequential patent number
    """
    try:
        # Remove design patent prefix if present
        patent_num_str = patent_id_str.strip().lstrip('D')
        patent_num = int(patent_num_str)
    except:
        return None

    # Use milestones to estimate
    if patent_num < 6000000:
        return None  # Pre-2000, outside our range
    elif patent_num < 7000000:
        return 2002
    elif patent_num < 8000000:
        return 2011
    elif patent_num < 9000000:
        return 2015
    elif patent_num < 10000000:
        return 2017
    elif patent_num < 10500000:
        return 2018
    elif patent_num < 11000000:
        return 2020
    elif patent_num < 11250000:
        return 2021
    elif patent_num < 11500000:
        return 2022
    elif patent_num < 11750000:
        return 2022
    elif patent_num < 12000000:
        return 2023
    elif patent_num < 12250000:
        return 2024
    elif patent_num < 12500000:
        return 2024
    else:
        return 2025

def main():
    print("="*80)
    print("REPROCESSING PATENTSVIEW DATA WITH CORRECT YEAR ASSIGNMENT")
    print("="*80)
    print("Using patent_id number ranges instead of corrupted filing_date")
    print(f"Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    conn = sqlite3.connect(DB_PATH, timeout=300)
    cursor = conn.cursor()

    # Update years based on patent_id
    print("\nUpdating grant years from patent_id...")

    cursor.execute("SELECT patent_id, filing_year FROM patentsview_patents_chinese")
    updates = []

    for patent_id, old_year in cursor.fetchall():
        new_year = estimate_grant_year_from_patent_id(patent_id)
        if new_year and new_year != old_year:
            updates.append((new_year, patent_id))

    print(f"Updating {len(updates):,} records...")

    cursor.executemany("""
        UPDATE patentsview_patents_chinese
        SET filing_year = ?
        WHERE patent_id = ?
    """, updates)

    conn.commit()

    # Show new distribution
    cursor.execute("""
        SELECT filing_year, COUNT(*) as count
        FROM patentsview_patents_chinese
        WHERE filing_year >= 2021 AND filing_year <= 2025
        GROUP BY filing_year
        ORDER BY filing_year
    """)

    print("\nCorrected year distribution (2021-2025):")
    total = 0
    for year, count in cursor.fetchall():
        print(f"  {year}: {count:,} patents")
        total += count

    print(f"\nTotal 2021-2025: {total:,} patents")

    conn.close()

    print(f"\n{'='*80}")
    print("REPROCESSING COMPLETE")
    print(f"{'='*80}")
    print(f"End: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == '__main__':
    main()

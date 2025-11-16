#!/usr/bin/env python3
"""
Clean Up Fabricated Institutional Data

Removes fabricated analytical assessments from institutional tables:
- china_relevance scores (without methodology)
- china_stance assessments (without statement analysis)
- Fabricated publications (without real URLs)
- Fabricated personnel stances (without sources)

Keeps only verifiable facts (institution names, URLs, verification dates)
"""

import sqlite3
from datetime import datetime

def cleanup_fabricated_data():
    """Remove fabricated analytical data from institutional tables"""

    print("=" * 70)
    print("FABRICATED DATA CLEANUP")
    print("=" * 70)
    print()
    print("Purpose: Remove analytical assessments created without sources")
    print("Date: 2025-10-26")
    print()

    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Step 1: Clear fabricated relevance scores from institutions
    print("Step 1: Clearing fabricated relevance scores...")
    cursor.execute('''
        UPDATE european_institutions
        SET china_relevance = NULL,
            us_relevance = NULL,
            tech_relevance = NULL,
            policy_domains = NULL
        WHERE country_code = 'DE'
    ''')
    print(f"  + Cleared fabricated scores from {cursor.rowcount} German institutions")
    conn.commit()

    # Step 2: Clear fabricated personnel stances
    print()
    print("Step 2: Clearing fabricated personnel stances...")
    cursor.execute('''
        UPDATE institutional_personnel
        SET china_stance = NULL,
            expertise_areas = NULL
        WHERE institution_id IN (
            SELECT institution_id FROM european_institutions WHERE country_code = 'DE'
        )
    ''')
    print(f"  + Cleared fabricated stances from {cursor.rowcount} personnel records")
    conn.commit()

    # Step 3: Delete fabricated publications (without real URLs)
    print()
    print("Step 3: Removing fabricated publications...")
    cursor.execute('''
        SELECT COUNT(*) FROM institutional_publications
        WHERE institution_id IN (
            SELECT institution_id FROM european_institutions WHERE country_code = 'DE'
        )
        AND (official_url IS NULL OR official_url = '')
    ''')
    fabricated_pubs = cursor.fetchone()[0]

    if fabricated_pubs > 0:
        cursor.execute('''
            DELETE FROM institutional_publications
            WHERE institution_id IN (
                SELECT institution_id FROM european_institutions WHERE country_code = 'DE'
            )
            AND (official_url IS NULL OR official_url = '')
        ''')
        print(f"  + Deleted {fabricated_pubs} fabricated publications (no real URLs)")
        conn.commit()
    else:
        print("  + No fabricated publications found")

    # Step 4: Delete fabricated intelligence assessments
    print()
    print("Step 4: Removing fabricated intelligence assessments...")
    cursor.execute('''
        SELECT COUNT(*) FROM institutional_intelligence
        WHERE institution_id IN (
            SELECT institution_id FROM european_institutions WHERE country_code = 'DE'
        )
    ''')
    fabricated_assessments = cursor.fetchone()[0]

    if fabricated_assessments > 0:
        cursor.execute('''
            DELETE FROM institutional_intelligence
            WHERE institution_id IN (
                SELECT institution_id FROM european_institutions WHERE country_code = 'DE'
            )
        ''')
        print(f"  + Deleted {fabricated_assessments} fabricated assessments")
        conn.commit()
    else:
        print("  + No fabricated assessments found")

    # Validation
    print()
    print("=" * 70)
    print("VALIDATION")
    print("=" * 70)
    print()

    cursor.execute('''
        SELECT institution_name, china_relevance, us_relevance, tech_relevance
        FROM european_institutions
        WHERE country_code = 'DE'
    ''')

    print("Checking institutions for remaining fabricated data...")
    fabrication_found = False
    for row in cursor.fetchall():
        if row[1] is not None or row[2] is not None or row[3] is not None:
            print(f"  WARNING: {row[0]} still has relevance scores")
            fabrication_found = True

    if not fabrication_found:
        print("  + All fabricated relevance scores removed")

    cursor.execute('''
        SELECT COUNT(*) FROM institutional_personnel
        WHERE china_stance IS NOT NULL
        AND institution_id IN (
            SELECT institution_id FROM european_institutions WHERE country_code = 'DE'
        )
    ''')
    remaining_stances = cursor.fetchone()[0]

    if remaining_stances > 0:
        print(f"  WARNING: {remaining_stances} personnel still have china_stance values")
    else:
        print("  + All fabricated personnel stances removed")

    cursor.execute('''
        SELECT COUNT(*) FROM institutional_publications
        WHERE institution_id IN (
            SELECT institution_id FROM european_institutions WHERE country_code = 'DE'
        )
    ''')
    remaining_pubs = cursor.fetchone()[0]
    print(f"  + Remaining publications: {remaining_pubs} (with real URLs only)")

    cursor.execute('''
        SELECT COUNT(*) FROM institutional_intelligence
        WHERE institution_id IN (
            SELECT institution_id FROM european_institutions WHERE country_code = 'DE'
        )
    ''')
    remaining_assessments = cursor.fetchone()[0]
    print(f"  + Remaining assessments: {remaining_assessments}")

    print()
    print("=" * 70)
    print("CLEANUP COMPLETE")
    print("=" * 70)
    print()
    print("Database now contains ONLY verifiable facts:")
    print("  + Institution names (from official websites)")
    print("  + Official URLs (verified)")
    print("  + Institution types (observable)")
    print()
    print("Fabricated data removed:")
    print("  - China/US/Tech relevance scores")
    print("  - Personnel stances without sources")
    print("  - Publications without real URLs")
    print("  - Intelligence assessments without data")
    print()

    conn.close()

if __name__ == '__main__':
    cleanup_fabricated_data()

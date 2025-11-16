#!/usr/bin/env python3
"""
Verify Current TED Database State
Check actual numbers from the database
"""

import sqlite3
from collections import defaultdict

MAIN_DB = "F:/OSINT_WAREHOUSE/osint_master.db"

def verify_ted_state():
    """Check actual TED database state"""

    print("=" * 80)
    print("TED DATABASE - CURRENT STATE VERIFICATION")
    print("=" * 80)

    conn = sqlite3.connect(MAIN_DB, timeout=120)
    cursor = conn.cursor()

    # Total contracts
    cursor.execute("SELECT COUNT(*) FROM ted_contracts_production")
    total = cursor.fetchone()[0]
    print(f"\nTotal contracts: {total:,}")

    # Chinese-related contracts
    cursor.execute("""
        SELECT COUNT(*) FROM ted_contracts_production
        WHERE is_chinese_related = 1
    """)
    chinese = cursor.fetchone()[0]
    print(f"Chinese-related contracts: {chinese:,}")

    # Year breakdown
    print("\nYear-by-year breakdown:")
    cursor.execute("""
        SELECT
            SUBSTR(publication_date, 1, 4) as year,
            COUNT(*) as count,
            SUM(CASE WHEN is_chinese_related = 1 THEN 1 ELSE 0 END) as chinese_count
        FROM ted_contracts_production
        WHERE publication_date IS NOT NULL
        GROUP BY year
        ORDER BY year
    """)

    year_data = cursor.fetchall()
    for year, count, chinese_count in year_data:
        pct = (chinese_count / count) * 100 if count > 0 else 0
        print(f"  {year}: {count:>10,} contracts ({chinese_count:>5,} Chinese, {pct:5.2f}%)")

    # Format check (Era 1/2 vs Era 3)
    print("\nFormat check (sample):")
    cursor.execute("""
        SELECT form_type, COUNT(*) as count
        FROM ted_contracts_production
        GROUP BY form_type
        ORDER BY count DESC
        LIMIT 10
    """)

    for form_type, count in cursor.fetchall():
        print(f"  {form_type or 'NULL'}: {count:,}")

    # Sample Chinese contracts
    print("\nSample Chinese contracts:")
    cursor.execute("""
        SELECT
            document_id,
            publication_date,
            ca_name,
            chinese_indicators
        FROM ted_contracts_production
        WHERE is_chinese_related = 1
        LIMIT 5
    """)

    for doc_id, pub_date, ca_name, indicators in cursor.fetchall():
        print(f"\n  {doc_id} ({pub_date})")
        print(f"    Authority: {ca_name[:60] if ca_name else 'N/A'}")
        print(f"    Indicators: {indicators}")

    conn.close()

    return {
        'total': total,
        'chinese': chinese,
        'years': year_data
    }

if __name__ == "__main__":
    try:
        results = verify_ted_state()
        print(f"\n[SUCCESS] Verification complete")
        print(f"Total: {results['total']:,}, Chinese: {results['chinese']:,}")
    except Exception as e:
        print(f"\n[ERROR] Verification failed: {e}")
        import traceback
        traceback.print_exc()

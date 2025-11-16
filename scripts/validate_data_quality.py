#!/usr/bin/env python3
"""
Data Quality Validation Script
Validates NULL data handling across all data sources
"""

import sqlite3
from pathlib import Path
from datetime import datetime
import json

def validate_ted_data_quality():
    """Validate TED data quality distribution"""

    db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")
    if not db_path.exists():
        print(f"Database not found: {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    print("="*80)
    print("TED (EU PROCUREMENT) - DATA QUALITY VALIDATION")
    print("="*80)

    # Check if table exists
    cur.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='ted_contracts_production'
    """)

    if not cur.fetchone():
        print("Table 'ted_contracts_production' does not exist yet")
        print("Run the TED processor first to create data")
        conn.close()
        return

    # Total records
    cur.execute("SELECT COUNT(*) FROM ted_contracts_production")
    total = cur.fetchone()[0]

    print(f"\nTotal Records: {total:,}\n")

    if total == 0:
        print("No data in table yet")
        conn.close()
        return

    # Data quality flag distribution
    print("DATA QUALITY DISTRIBUTION:")
    print("-" * 80)

    cur.execute("""
        SELECT
            data_quality_flag,
            COUNT(*) as count,
            ROUND(COUNT(*) * 100.0 / ?, 2) as percentage,
            ROUND(AVG(fields_with_data_count), 2) as avg_fields
        FROM ted_contracts_production
        GROUP BY data_quality_flag
        ORDER BY count DESC
    """, (total,))

    quality_dist = {}
    for flag, count, percentage, avg_fields in cur.fetchall():
        flag_name = flag if flag else "NULL (not yet processed)"
        quality_dist[flag_name] = count
        print(f"{flag_name:30} | {count:>10,} | {percentage:>6.2f}% | {avg_fields or 0:.1f} fields")

    # Critical findings
    print("\n" + "="*80)
    print("CRITICAL FINDINGS:")
    print("="*80)

    # 1. Confirmed Chinese
    cur.execute("""
        SELECT COUNT(*) FROM ted_contracts_production
        WHERE data_quality_flag = 'CHINESE_CONFIRMED'
    """)
    chinese_confirmed = cur.fetchone()[0]
    print(f"\n1. CHINESE_CONFIRMED: {chinese_confirmed:,} contracts")

    if chinese_confirmed > 0:
        print("\n   Sample records:")
        cur.execute("""
            SELECT contractor_name, contractor_country, contractor_city, detection_rationale
            FROM ted_contracts_production
            WHERE data_quality_flag = 'CHINESE_CONFIRMED'
            LIMIT 5
        """)
        for name, country, city, rationale in cur.fetchall():
            print(f"     - {name} ({country}, {city})")
            print(f"       Rationale: {rationale}")

    # 2. No data / uncertain
    cur.execute("""
        SELECT COUNT(*) FROM ted_contracts_production
        WHERE data_quality_flag IN ('NO_DATA', 'LOW_DATA', 'UNCERTAIN_NEEDS_REVIEW')
    """)
    uncertain = cur.fetchone()[0]

    print(f"\n2. UNCERTAIN/UNKNOWN: {uncertain:,} contracts")
    print("   These records have insufficient data to determine if Chinese")
    print("   Following Zero Fabrication Protocol - we acknowledge what we don't know")

    if uncertain > 0:
        print("\n   Breakdown:")
        for flag in ['NO_DATA', 'LOW_DATA', 'UNCERTAIN_NEEDS_REVIEW']:
            # SECURITY: Use parameterized query for value
            cur.execute("""
                SELECT COUNT(*) FROM ted_contracts_production
                WHERE data_quality_flag = ?
            """, (flag,))
            count = cur.fetchone()[0]
            if count > 0:
                percentage = (count / uncertain) * 100
                print(f"     {flag}: {count:,} ({percentage:.1f}%)")

    # 3. Non-Chinese confirmed
    cur.execute("""
        SELECT COUNT(*) FROM ted_contracts_production
        WHERE data_quality_flag = 'NON_CHINESE_CONFIRMED'
    """)
    non_chinese = cur.fetchone()[0]

    print(f"\n3. NON_CHINESE_CONFIRMED: {non_chinese:,} contracts")
    print("   These have actual evidence they are NOT Chinese (e.g., country=FR)")

    # Country distribution for non-Chinese
    if non_chinese > 0:
        print("\n   Top 10 countries:")
        cur.execute("""
            SELECT contractor_country, COUNT(*) as count
            FROM ted_contracts_production
            WHERE data_quality_flag = 'NON_CHINESE_CONFIRMED'
            GROUP BY contractor_country
            ORDER BY count DESC
            LIMIT 10
        """)
        for country, count in cur.fetchall():
            print(f"     {country or 'NULL'}: {count:,}")

    # Key insight
    print("\n" + "="*80)
    print("KEY INSIGHT:")
    print("="*80)

    if uncertain > 0:
        uncertain_pct = (uncertain / total) * 100
        print(f"\n{uncertain:,} records ({uncertain_pct:.1f}%) are UNKNOWN due to NULL/insufficient data.")
        print("These are NOT confirmed as non-Chinese - we simply lack the data.")
        print("This distinction is CRITICAL for Zero Fabrication Protocol compliance.")

    # Save report
    report = {
        'timestamp': datetime.now().isoformat(),
        'source': 'TED_EU_Procurement',
        'total_records': total,
        'quality_distribution': quality_dist,
        'chinese_confirmed': chinese_confirmed,
        'uncertain_unknown': uncertain,
        'non_chinese_confirmed': non_chinese,
        'uncertain_percentage': round((uncertain / total) * 100, 2) if total > 0 else 0
    }

    report_path = Path("analysis/TED_DATA_QUALITY_REPORT.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\nReport saved: {report_path}")

    conn.close()


def validate_uspto_data_quality():
    """Validate USPTO data quality"""

    db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")
    if not db_path.exists():
        return

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    print("\n" + "="*80)
    print("USPTO (PATENTS) - DATA QUALITY VALIDATION")
    print("="*80)

    # Check if table exists
    cur.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='uspto_patents_chinese'
    """)

    if not cur.fetchone():
        print("Table 'uspto_patents_chinese' does not exist yet")
        conn.close()
        return

    # Check if data_quality_flag column exists
    cur.execute("PRAGMA table_info(uspto_patents_chinese)")
    columns = [row[1] for row in cur.fetchall()]
    has_quality_column = 'data_quality_flag' in columns

    # Get total
    cur.execute("SELECT COUNT(*) FROM uspto_patents_chinese")
    total = cur.fetchone()[0]

    print(f"\nTotal Records: {total:,}")
    print(f"Data Quality Column Exists: {'Yes' if has_quality_column else 'No (needs reprocessing)'}\n")

    if total == 0:
        print("No data in table yet")
        conn.close()
        return

    if not has_quality_column:
        print("NOTE: Table exists but data_quality_flag column not present.")
        print("      Run the updated USPTO processor to reprocess with quality tracking.")
        conn.close()
        return

    # Data quality distribution
    print("DATA QUALITY DISTRIBUTION:")
    print("-" * 80)

    cur.execute("""
        SELECT
            data_quality_flag,
            COUNT(*) as count,
            ROUND(COUNT(*) * 100.0 / ?, 2) as percentage,
            ROUND(AVG(fields_with_data_count), 2) as avg_fields
        FROM uspto_patents_chinese
        WHERE data_quality_flag IS NOT NULL
        GROUP BY data_quality_flag
        ORDER BY count DESC
    """, (total,))

    for flag, count, percentage, avg_fields in cur.fetchall():
        print(f"{flag:30} | {count:>10,} | {percentage:>6.2f}% | {avg_fields:.1f} fields")

    # Show sample NO_DATA records
    print("\n" + "="*80)
    print("SAMPLE NO_DATA RECORDS (for review):")
    print("="*80)

    cur.execute("""
        SELECT assignee_name, assignee_country, assignee_city, fields_with_data_count
        FROM uspto_patents_chinese
        WHERE data_quality_flag = 'NO_DATA'
        LIMIT 5
    """)

    for name, country, city, fields_count in cur.fetchall():
        print(f"  Name: {name or 'NULL'}")
        print(f"  Country: {country or 'NULL'}")
        print(f"  City: {city or 'NULL'}")
        print(f"  Fields Count: {fields_count}")
        print()

    conn.close()


if __name__ == '__main__':
    print("\n" + "="*80)
    print("DATA QUALITY VALIDATION - NULL DATA HANDLING FRAMEWORK")
    print("="*80)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("="*80)

    # Validate each data source
    validate_ted_data_quality()
    validate_uspto_data_quality()

    print("\n" + "="*80)
    print("[SUCCESS] Validation complete!")
    print("="*80)

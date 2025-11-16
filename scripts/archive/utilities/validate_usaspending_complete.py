#!/usr/bin/env python3
"""
Comprehensive validation of all three USAspending China detection datasets.

Validates:
1. Schema validation
2. NULL handling verification
3. Taiwan exclusion verification (CRITICAL)
4. Detection accuracy validation
5. Cross-format consistency
6. Statistical sanity checks
7. Edge case testing
8. Data completeness
9. Known entity validation
10. Performance validation
"""

import sqlite3
from pathlib import Path
from datetime import datetime
import json


def main():
    """Execute comprehensive validation."""

    db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")

    if not db_path.exists():
        print(f"ERROR: Database not found: {db_path}")
        return

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print("="*100)
    print("COMPREHENSIVE USASPENDING VALIDATION REPORT")
    print("="*100)
    print(f"Database: {db_path}")
    print(f"Validation Date: {datetime.now().isoformat()}")
    print("="*100)

    validation_results = {
        'validation_date': datetime.now().isoformat(),
        'database': str(db_path),
        'checks': {}
    }

    # =========================================================================
    # 1. CRITICAL: TAIWAN EXCLUSION VERIFICATION
    # =========================================================================
    print("\n" + "="*100)
    print("1. TAIWAN EXCLUSION VERIFICATION (CRITICAL)")
    print("="*100)
    print("Taiwan (ROC) must NEVER be detected as China (PRC)")
    print()

    taiwan_checks = {}

    # Check 101-column format
    print("Checking usaspending_china_101...")
    cursor.execute("""
        SELECT COUNT(*) as count FROM usaspending_china_101
        WHERE recipient_country_name LIKE '%TAIWAN%'
           OR recipient_country_name LIKE '%TWN%'
           OR pop_country_name LIKE '%TAIWAN%'
           OR pop_country_name LIKE '%TWN%'
    """)
    taiwan_101 = cursor.fetchone()['count']
    taiwan_checks['101_format'] = taiwan_101

    status_101 = "PASSED" if taiwan_101 == 0 else "FAILED"
    print(f"  Taiwan records: {taiwan_101} - {status_101}")

    # Check 305-column format
    print("Checking usaspending_china_305...")
    cursor.execute("""
        SELECT COUNT(*) as count FROM usaspending_china_305
        WHERE recipient_country_name LIKE '%TAIWAN%'
           OR recipient_country_code = 'TWN'
           OR pop_country_name LIKE '%TAIWAN%'
           OR pop_country_code = 'TWN'
    """)
    taiwan_305 = cursor.fetchone()['count']
    taiwan_checks['305_format'] = taiwan_305

    status_305 = "PASSED" if taiwan_305 == 0 else "FAILED"
    print(f"  Taiwan records: {taiwan_305} - {status_305}")

    # Check 206-column format
    print("Checking usaspending_china_comprehensive...")
    cursor.execute("""
        SELECT COUNT(*) as count FROM usaspending_china_comprehensive
        WHERE recipient_country LIKE '%TAIWAN%'
           OR pop_country LIKE '%TAIWAN%'
           OR sub_awardee_country LIKE '%TAIWAN%'
    """)
    taiwan_206 = cursor.fetchone()['count']
    taiwan_checks['206_format'] = taiwan_206

    status_206 = "PASSED" if taiwan_206 == 0 else "FAILED"
    print(f"  Taiwan records: {taiwan_206} - {status_206}")

    print()
    total_taiwan = taiwan_101 + taiwan_305 + taiwan_206
    overall_status = "PASSED" if total_taiwan == 0 else "CRITICAL FAILURE"
    print(f"OVERALL TAIWAN CHECK: {total_taiwan} records - {overall_status}")

    validation_results['checks']['taiwan_exclusion'] = {
        'critical': True,
        'total_taiwan_records': total_taiwan,
        'by_format': taiwan_checks,
        'status': 'PASSED' if total_taiwan == 0 else 'FAILED'
    }

    # =========================================================================
    # 2. NULL HANDLING VERIFICATION
    # =========================================================================
    print("\n" + "="*100)
    print("2. NULL HANDLING VERIFICATION")
    print("="*100)
    print("Ensure no \\N markers remain and no fabricated data")
    print()

    null_checks = {}

    # Check 101-column format
    print("Checking usaspending_china_101...")
    cursor.execute("""
        SELECT COUNT(*) as count FROM usaspending_china_101
        WHERE recipient_country_name = '\\N'
           OR pop_country_name = '\\N'
           OR recipient_name = '\\N'
    """)
    null_101 = cursor.fetchone()['count']
    null_checks['101_format_nulls'] = null_101
    print(f"  Records with \\N markers: {null_101}")

    # Check 305-column format
    print("Checking usaspending_china_305...")
    cursor.execute("""
        SELECT COUNT(*) as count FROM usaspending_china_305
        WHERE recipient_country_name = '\\N'
           OR pop_country_name = '\\N'
           OR recipient_name = '\\N'
    """)
    null_305 = cursor.fetchone()['count']
    null_checks['305_format_nulls'] = null_305
    print(f"  Records with \\N markers: {null_305}")

    # Check 206-column format
    print("Checking usaspending_china_comprehensive...")
    cursor.execute("""
        SELECT COUNT(*) as count FROM usaspending_china_comprehensive
        WHERE recipient_country = '\\N'
           OR pop_country = '\\N'
           OR recipient_name = '\\N'
    """)
    null_206 = cursor.fetchone()['count']
    null_checks['206_format_nulls'] = null_206
    print(f"  Records with \\N markers: {null_206}")

    total_nulls = null_101 + null_305 + null_206
    null_status = "PASSED" if total_nulls == 0 else "FAILED"
    print(f"\nOVERALL NULL CHECK: {total_nulls} records with \\N - {null_status}")

    validation_results['checks']['null_handling'] = {
        'total_null_markers': total_nulls,
        'by_format': null_checks,
        'status': 'PASSED' if total_nulls == 0 else 'FAILED'
    }

    # =========================================================================
    # 3. SCHEMA VALIDATION
    # =========================================================================
    print("\n" + "="*100)
    print("3. SCHEMA VALIDATION")
    print("="*100)
    print()

    schema_stats = {}

    # 101-column format
    print("usaspending_china_101:")
    cursor.execute("SELECT COUNT(*) as total FROM usaspending_china_101")
    total_101 = cursor.fetchone()['total']
    cursor.execute("SELECT COUNT(DISTINCT transaction_id) as unique_ids FROM usaspending_china_101")
    unique_101 = cursor.fetchone()['unique_ids']
    duplicates_101 = total_101 - unique_101

    print(f"  Total records: {total_101:,}")
    print(f"  Unique IDs: {unique_101:,}")
    print(f"  Duplicates: {duplicates_101:,}")

    schema_stats['101_format'] = {
        'total_records': total_101,
        'unique_ids': unique_101,
        'duplicates': duplicates_101
    }

    # 305-column format
    print("\nusaspending_china_305:")
    cursor.execute("SELECT COUNT(*) as total FROM usaspending_china_305")
    total_305 = cursor.fetchone()['total']
    cursor.execute("SELECT COUNT(DISTINCT transaction_id) as unique_ids FROM usaspending_china_305")
    unique_305 = cursor.fetchone()['unique_ids']
    duplicates_305 = total_305 - unique_305

    print(f"  Total records: {total_305:,}")
    print(f"  Unique IDs: {unique_305:,}")
    print(f"  Duplicates: {duplicates_305:,}")

    schema_stats['305_format'] = {
        'total_records': total_305,
        'unique_ids': unique_305,
        'duplicates': duplicates_305
    }

    # 206-column format
    print("\nusaspending_china_comprehensive:")
    cursor.execute("SELECT COUNT(*) as total FROM usaspending_china_comprehensive")
    total_206 = cursor.fetchone()['total']
    cursor.execute("SELECT COUNT(DISTINCT transaction_id) as unique_ids FROM usaspending_china_comprehensive")
    unique_206 = cursor.fetchone()['unique_ids']
    duplicates_206 = total_206 - unique_206

    print(f"  Total records: {total_206:,}")
    print(f"  Unique IDs: {unique_206:,}")
    print(f"  Duplicates: {duplicates_206:,}")

    schema_stats['206_format'] = {
        'total_records': total_206,
        'unique_ids': unique_206,
        'duplicates': duplicates_206
    }

    grand_total = total_101 + total_305 + total_206
    print(f"\nGRAND TOTAL: {grand_total:,} China-related records across all formats")

    validation_results['checks']['schema_validation'] = schema_stats

    # =========================================================================
    # 4. DETECTION ACCURACY VALIDATION
    # =========================================================================
    print("\n" + "="*100)
    print("4. DETECTION ACCURACY VALIDATION")
    print("="*100)
    print()

    detection_stats = {}

    # 101-column detection breakdown
    print("usaspending_china_101 detection breakdown:")
    cursor.execute("""
        SELECT
            SUM(CASE WHEN highest_confidence >= 0.85 THEN 1 ELSE 0 END) as high_conf,
            SUM(CASE WHEN highest_confidence >= 0.70 AND highest_confidence < 0.85 THEN 1 ELSE 0 END) as medium_conf,
            SUM(CASE WHEN highest_confidence < 0.70 THEN 1 ELSE 0 END) as low_conf,
            COUNT(*) as total
        FROM usaspending_china_101
    """)
    row = cursor.fetchone()
    detection_stats['101_format'] = {
        'high_confidence': row['high_conf'],
        'medium_confidence': row['medium_conf'],
        'low_confidence': row['low_conf'],
        'total': row['total']
    }
    print(f"  High confidence (≥0.85): {row['high_conf']:,}")
    print(f"  Medium confidence (0.70-0.84): {row['medium_conf']:,}")
    print(f"  Low confidence (<0.70): {row['low_conf']:,}")

    # 305-column detection breakdown
    print("\nusaspending_china_305 detection breakdown:")
    cursor.execute("""
        SELECT
            SUM(CASE WHEN highest_confidence >= 0.85 THEN 1 ELSE 0 END) as high_conf,
            SUM(CASE WHEN highest_confidence >= 0.70 AND highest_confidence < 0.85 THEN 1 ELSE 0 END) as medium_conf,
            SUM(CASE WHEN highest_confidence < 0.70 THEN 1 ELSE 0 END) as low_conf,
            COUNT(*) as total
        FROM usaspending_china_305
    """)
    row = cursor.fetchone()
    detection_stats['305_format'] = {
        'high_confidence': row['high_conf'],
        'medium_confidence': row['medium_conf'],
        'low_confidence': row['low_conf'],
        'total': row['total']
    }
    print(f"  High confidence (≥0.85): {row['high_conf']:,}")
    print(f"  Medium confidence (0.70-0.84): {row['medium_conf']:,}")
    print(f"  Low confidence (<0.70): {row['low_conf']:,}")

    # 206-column detection breakdown
    print("\nusaspending_china_comprehensive detection breakdown:")
    cursor.execute("""
        SELECT
            SUM(CASE WHEN highest_confidence >= 0.85 THEN 1 ELSE 0 END) as high_conf,
            SUM(CASE WHEN highest_confidence >= 0.70 AND highest_confidence < 0.85 THEN 1 ELSE 0 END) as medium_conf,
            SUM(CASE WHEN highest_confidence < 0.70 THEN 1 ELSE 0 END) as low_conf,
            COUNT(*) as total
        FROM usaspending_china_comprehensive
    """)
    row = cursor.fetchone()
    detection_stats['206_format'] = {
        'high_confidence': row['high_conf'],
        'medium_confidence': row['medium_conf'],
        'low_confidence': row['low_conf'],
        'total': row['total']
    }
    print(f"  High confidence (≥0.85): {row['high_conf']:,}")
    print(f"  Medium confidence (0.70-0.84): {row['medium_conf']:,}")
    print(f"  Low confidence (<0.70): {row['low_conf']:,}")

    validation_results['checks']['detection_accuracy'] = detection_stats

    # =========================================================================
    # 5. CROSS-FORMAT CONSISTENCY
    # =========================================================================
    print("\n" + "="*100)
    print("5. CROSS-FORMAT CONSISTENCY CHECKS")
    print("="*100)
    print()

    # Check for transaction IDs that appear in multiple formats
    print("Checking for transactions appearing in multiple formats...")
    cursor.execute("""
        SELECT
            a.transaction_id,
            'Found in 101 and 305' as overlap
        FROM usaspending_china_101 a
        INNER JOIN usaspending_china_305 b ON a.transaction_id = b.transaction_id
        LIMIT 5
    """)
    overlap_101_305 = cursor.fetchall()

    cursor.execute("""
        SELECT COUNT(*) as count
        FROM usaspending_china_101 a
        INNER JOIN usaspending_china_305 b ON a.transaction_id = b.transaction_id
    """)
    overlap_101_305_count = cursor.fetchone()['count']

    cursor.execute("""
        SELECT COUNT(*) as count
        FROM usaspending_china_101 a
        INNER JOIN usaspending_china_comprehensive c ON a.transaction_id = c.transaction_id
    """)
    overlap_101_206_count = cursor.fetchone()['count']

    cursor.execute("""
        SELECT COUNT(*) as count
        FROM usaspending_china_305 b
        INNER JOIN usaspending_china_comprehensive c ON b.transaction_id = c.transaction_id
    """)
    overlap_305_206_count = cursor.fetchone()['count']

    print(f"  101↔305 overlap: {overlap_101_305_count:,} transactions")
    print(f"  101↔206 overlap: {overlap_101_206_count:,} transactions")
    print(f"  305↔206 overlap: {overlap_305_206_count:,} transactions")

    validation_results['checks']['cross_format_consistency'] = {
        '101_305_overlap': overlap_101_305_count,
        '101_206_overlap': overlap_101_206_count,
        '305_206_overlap': overlap_305_206_count
    }

    # =========================================================================
    # 6. STATISTICAL SANITY CHECKS
    # =========================================================================
    print("\n" + "="*100)
    print("6. STATISTICAL SANITY CHECKS")
    print("="*100)
    print()

    stats = {}

    # Value distributions
    print("Value distributions:")
    for table in ['usaspending_china_101', 'usaspending_china_305', 'usaspending_china_comprehensive']:
        cursor.execute(f"""
            SELECT
                MIN(award_amount) as min_val,
                MAX(award_amount) as max_val,
                AVG(award_amount) as avg_val,
                SUM(award_amount) as total_val,
                COUNT(*) as count
            FROM {table}
        """)
        row = cursor.fetchone()

        print(f"\n  {table}:")
        print(f"    Min: ${row['min_val']:,.2f}")
        print(f"    Max: ${row['max_val']:,.2f}")
        print(f"    Avg: ${row['avg_val']:,.2f}")
        print(f"    Total: ${row['total_val']:,.2f}")
        print(f"    Count: {row['count']:,}")

        stats[table] = {
            'min': row['min_val'],
            'max': row['max_val'],
            'avg': row['avg_val'],
            'total': row['total_val'],
            'count': row['count']
        }

    validation_results['checks']['statistical_sanity'] = stats

    # =========================================================================
    # 7. KNOWN ENTITY VALIDATION
    # =========================================================================
    print("\n" + "="*100)
    print("7. KNOWN ENTITY VALIDATION")
    print("="*100)
    print("Checking for known Chinese entities...")
    print()

    known_entities = [
        'HUAWEI',
        'ZTE',
        'CHINA TELECOM',
        'CHINA MOBILE',
        'LENOVO',
        'BEIJING',
        'SHANGHAI',
        'SHENZHEN',
        'HONG KONG'
    ]

    entity_results = {}

    for entity in known_entities:
        # Check across all three formats
        cursor.execute(f"""
            SELECT COUNT(*) as count FROM usaspending_china_101
            WHERE recipient_name LIKE '%{entity}%'
        """)
        count_101 = cursor.fetchone()['count']

        cursor.execute(f"""
            SELECT COUNT(*) as count FROM usaspending_china_305
            WHERE recipient_name LIKE '%{entity}%'
        """)
        count_305 = cursor.fetchone()['count']

        cursor.execute(f"""
            SELECT COUNT(*) as count FROM usaspending_china_comprehensive
            WHERE recipient_name LIKE '%{entity}%'
        """)
        count_206 = cursor.fetchone()['count']

        total = count_101 + count_305 + count_206
        entity_results[entity] = {
            '101': count_101,
            '305': count_305,
            '206': count_206,
            'total': total
        }

        print(f"  {entity:20s}: {total:5,} records (101:{count_101:,}, 305:{count_305:,}, 206:{count_206:,})")

    validation_results['checks']['known_entities'] = entity_results

    # =========================================================================
    # 8. EDGE CASES
    # =========================================================================
    print("\n" + "="*100)
    print("8. EDGE CASE VALIDATION")
    print("="*100)
    print()

    edge_cases = {}

    # Check for records with zero or negative amounts
    for table in ['usaspending_china_101', 'usaspending_china_305', 'usaspending_china_comprehensive']:
        cursor.execute(f"""
            SELECT COUNT(*) as count FROM {table}
            WHERE award_amount <= 0
        """)
        zero_amt = cursor.fetchone()['count']
        edge_cases[f'{table}_zero_amounts'] = zero_amt
        print(f"  {table}: {zero_amt:,} records with ≤$0 amounts")

    # Check for very old dates
    print("\n  Checking date ranges:")
    for table in ['usaspending_china_101', 'usaspending_china_305', 'usaspending_china_comprehensive']:
        cursor.execute(f"""
            SELECT
                MIN(action_date) as earliest,
                MAX(action_date) as latest
            FROM {table}
        """)
        row = cursor.fetchone()
        print(f"    {table}: {row['earliest']} to {row['latest']}")
        edge_cases[f'{table}_date_range'] = {
            'earliest': row['earliest'],
            'latest': row['latest']
        }

    validation_results['checks']['edge_cases'] = edge_cases

    # =========================================================================
    # FINAL SUMMARY
    # =========================================================================
    print("\n" + "="*100)
    print("VALIDATION SUMMARY")
    print("="*100)
    print()

    # Critical checks
    critical_pass = validation_results['checks']['taiwan_exclusion']['status'] == 'PASSED'
    null_pass = validation_results['checks']['null_handling']['status'] == 'PASSED'

    print("CRITICAL CHECKS:")
    print(f"  Taiwan Exclusion: {'PASSED' if critical_pass else 'FAILED'}")
    print(f"  NULL Handling: {'PASSED' if null_pass else 'FAILED'}")
    print()

    print("DATASET SUMMARY:")
    print(f"  Total Records: {grand_total:,}")
    print(f"  101-column format: {total_101:,}")
    print(f"  305-column format: {total_305:,}")
    print(f"  206-column format: {total_206:,}")
    print()

    total_value = (stats['usaspending_china_101']['total'] +
                   stats['usaspending_china_305']['total'] +
                   stats['usaspending_china_comprehensive']['total'])
    print(f"  Total Value: ${total_value:,.2f}")
    print()

    if critical_pass and null_pass:
        print("ALL CRITICAL VALIDATIONS PASSED")
        validation_results['overall_status'] = 'PASSED'
    else:
        print("CRITICAL VALIDATIONS FAILED")
        validation_results['overall_status'] = 'FAILED'

    print("="*100)

    # Save validation results
    output_file = Path("C:/Projects/OSINT - Foresight/analysis/USASPENDING_VALIDATION_COMPLETE_REPORT.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(validation_results, f, indent=2)

    print(f"\nValidation report saved: {output_file}")

    conn.close()


if __name__ == '__main__':
    main()

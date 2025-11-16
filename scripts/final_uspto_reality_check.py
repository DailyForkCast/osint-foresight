#!/usr/bin/env python3
import re

# ============================================================================
# SECURITY: SQL injection prevention through identifier validation
# ============================================================================

def validate_sql_identifier(identifier):
    """
    SECURITY: Validate SQL identifier (table or column name).
    Only allows alphanumeric characters and underscores.
    Prevents SQL injection from dynamic SQL construction.
    """
    if not identifier:
        raise ValueError("Identifier cannot be empty")

    # Check for valid characters only (alphanumeric + underscore)
    if not re.match(r'^[a-zA-Z0-9_]+$', identifier):
        raise ValueError(f"Invalid identifier: {identifier}. Contains illegal characters.")

    # Check length (SQLite limit is 1024, we use 100 for safety)
    if len(identifier) > 100:
        raise ValueError(f"Identifier too long: {identifier}")

    # Blacklist dangerous SQL keywords
    dangerous_keywords = {'DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE',
                         'EXEC', 'EXECUTE', 'UNION', 'SELECT', '--', ';', '/*', '*/'}
    if identifier.upper() in dangerous_keywords:
        raise ValueError(f"Identifier contains SQL keyword: {identifier}")

    return identifier


"""
Final USPTO Reality Check
Understand the actual database structure and why counts are so low
"""

import sqlite3

DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"

print("=" * 80)
print("USPTO DATABASE REALITY CHECK")
print("=" * 80)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# ============================================================================
# Check database schema and tables
# ============================================================================
print("\n" + "=" * 80)
print("DATABASE TABLES")
print("=" * 80)

cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%uspto%'")
tables = cur.fetchall()

print("\nUSPTO-related tables:")
for table in tables:
    # SECURITY: Validate table name before use in SQL
    safe_table = validate_sql_identifier(table[0])
    cur.execute(f"SELECT COUNT(*) FROM {safe_table}")
    count = cur.fetchone()[0]
    print(f"  - {table[0]:30s}: {count:,} records")

# ============================================================================
# Check uspto_assignee schema
# ============================================================================
print("\n" + "=" * 80)
print("USPTO_ASSIGNEE SCHEMA")
print("=" * 80)

cur.execute("PRAGMA table_info(uspto_assignee)")
schema = cur.fetchall()

print("\nColumns:")
for col in schema:
    col_id, name, dtype, notnull, default, pk = col
    print(f"  {col_id}. {name:20s} {dtype:15s} {'NOT NULL' if notnull else ''}")

# ============================================================================
# Sample actual records
# ============================================================================
print("\n" + "=" * 80)
print("SAMPLE USPTO RECORDS (China country code)")
print("=" * 80)

cur.execute("""
    SELECT rf_id, ee_name, ee_city, ee_state, ee_country
    FROM uspto_assignee
    WHERE ee_country = 'CHINA'
    LIMIT 20
""")

china_samples = cur.fetchall()

print(f"\nFound {len(china_samples)} samples:")
for rf_id, name, city, state, country in china_samples:
    print(f"  - {name[:50]:50s} | {city or 'N/A':15s} | {country}")

# ============================================================================
# Check case_file table
# ============================================================================
print("\n" + "=" * 80)
print("USPTO CASE_FILE TABLE")
print("=" * 80)

try:
    cur.execute("PRAGMA table_info(uspto_case_file)")
    case_schema = cur.fetchall()

    print("\nColumns:")
    for col in case_schema[:10]:  # First 10 columns
        col_id, name, dtype, notnull, default, pk = col
        print(f"  {col_id}. {name:30s} {dtype:15s}")

    cur.execute("SELECT COUNT(*) FROM uspto_case_file")
    case_count = cur.fetchone()[0]
    print(f"\nTotal case_file records: {case_count:,}")

    # Try to find Chinese patents in case_file
    cur.execute("""
        SELECT application_number, applicant_name
        FROM uspto_case_file
        WHERE applicant_name LIKE '%HUAWEI%'
        LIMIT 5
    """)

    huawei_cases = cur.fetchall()
    if huawei_cases:
        print(f"\nFound {len(huawei_cases)} Huawei examples in case_file:")
        for app_num, name in huawei_cases:
            print(f"  - {app_num}: {name[:60]}")

except Exception as e:
    print(f"\nError accessing case_file: {e}")

# ============================================================================
# CRITICAL QUESTION: Is this a filtered subset?
# ============================================================================
print("\n" + "=" * 80)
print("CRITICAL DATA SCOPE ANALYSIS")
print("=" * 80)

# Check if this is recent data or historical
cur.execute("""
    SELECT MIN(rf_id), MAX(rf_id), COUNT(DISTINCT rf_id)
    FROM uspto_assignee
""")

min_id, max_id, distinct_count = cur.fetchone()

print(f"\nrf_id range: {min_id:,} to {max_id:,}")
print(f"Distinct rf_ids: {distinct_count:,}")

# Check NULL distribution
cur.execute("""
    SELECT
        SUM(CASE WHEN ee_country IS NULL OR ee_country = '' THEN 1 ELSE 0 END) as null_country,
        SUM(CASE WHEN ee_country IS NOT NULL AND ee_country != '' THEN 1 ELSE 0 END) as has_country,
        COUNT(*) as total
    FROM uspto_assignee
""")

null_cnt, has_cnt, total = cur.fetchone()

print(f"\nCountry field distribution:")
print(f"  NULL/empty:   {null_cnt:,} ({null_cnt*100/total:.1f}%)")
print(f"  Has country:  {has_cnt:,} ({has_cnt*100/total:.1f}%)")

# Top countries that DO have country codes
cur.execute("""
    SELECT ee_country, COUNT(*) as cnt
    FROM uspto_assignee
    WHERE ee_country IS NOT NULL AND ee_country != ''
    GROUP BY ee_country
    ORDER BY cnt DESC
    LIMIT 15
""")

top_countries = cur.fetchall()

print(f"\nTop 15 countries (by record count):")
for i, (country, count) in enumerate(top_countries, 1):
    pct = count * 100 / has_cnt
    print(f"{i:2d}. {country:30s}: {count:7,} ({pct:5.1f}%)")

# ============================================================================
# HYPOTHESIS: Check if data is pre-2000s or filtered
# ============================================================================
print("\n" + "=" * 80)
print("CONCLUSION & HYPOTHESIS")
print("=" * 80)

china_total = next((c for co, c in top_countries if 'CHINA' in co.upper()), 0)
japan_total = next((c for co, c in top_countries if 'JAPAN' in co.upper()), 0)

print(f"\nChina records: {china_total:,}")
print(f"Japan records: {japan_total:,}")
print(f"Ratio: Japan is {japan_total/max(china_total,1):.1f}x larger than China")

print("\nPOSSIBLE EXPLANATIONS FOR LOW CHINESE COUNT:")
print("1. Database is from pre-2000s (before China's patent boom)")
print("2. Database is filtered/sampled subset, not complete USPTO")
print("3. Chinese entities systematically use non-Chinese addresses")
print("4. Data extraction issue missed Chinese records")
print("5. Chinese patents are in case_file but not linked to assignee table")

conn.close()

print("\n" + "=" * 80)

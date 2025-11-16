#!/usr/bin/env python3
"""
Check USPTO database for date fields and time coverage
"""

import sqlite3
import re
from datetime import datetime

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

DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"

print("=" * 80)
print("USPTO DATABASE DATE ANALYSIS")
print("=" * 80)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Check assignee table schema for date fields
print("\n" + "=" * 80)
print("USPTO_ASSIGNEE TABLE SCHEMA")
print("=" * 80)

cur.execute("PRAGMA table_info(uspto_assignee)")
assignee_schema = cur.fetchall()

print("\nColumns in uspto_assignee:")
for col in assignee_schema:
    col_id, name, dtype, notnull, default, pk = col
    print(f"  {col_id}. {name:20s} {dtype:15s}")

# Check case_file table schema for date fields
print("\n" + "=" * 80)
print("USPTO_CASE_FILE TABLE SCHEMA")
print("=" * 80)

cur.execute("PRAGMA table_info(uspto_case_file)")
case_schema = cur.fetchall()

print("\nColumns in uspto_case_file (first 30):")
for col in case_schema[:30]:
    col_id, name, dtype, notnull, default, pk = col
    print(f"  {col_id:2d}. {name:30s} {dtype:15s}")

# Look for date-related columns
date_columns = [col for col in case_schema if 'dt' in col[1].lower() or 'date' in col[1].lower()]

print(f"\n\nDate-related columns in case_file ({len(date_columns)} found):")
for col in date_columns:
    col_id, name, dtype, notnull, default, pk = col
    print(f"  {col_id:2d}. {name:30s} {dtype:15s}")

# Check if there's a filing date or registration date
print("\n" + "=" * 80)
print("DATE FIELD ANALYSIS")
print("=" * 80)

# Sample some dates
if date_columns:
    first_date_col = date_columns[0][1]
    # SECURITY: Validate column name before use in SQL
    safe_col = validate_sql_identifier(first_date_col)

    print(f"\nAnalyzing column: {first_date_col}")

    cur.execute(f"""
        SELECT {safe_col}, COUNT(*) as cnt
        FROM uspto_case_file
        WHERE {safe_col} IS NOT NULL
        GROUP BY {safe_col}
        ORDER BY {safe_col}
        LIMIT 20
    """)

    samples = cur.fetchall()

    print(f"\nFirst 20 date values:")
    for date_val, count in samples:
        print(f"  {date_val}: {count:,} records")

# Check for earliest and latest dates
print("\n" + "=" * 80)
print("DATE RANGE ANALYSIS")
print("=" * 80)

# Try common date field names
potential_date_fields = ['filing_dt', 'registration_dt', 'abandon_dt', 'status_dt']

for field in potential_date_fields:
    try:
        # SECURITY: Validate column name before use in SQL
        safe_field = validate_sql_identifier(field)
        cur.execute(f"""
            SELECT MIN({safe_field}), MAX({safe_field}), COUNT(*)
            FROM uspto_case_file
            WHERE {safe_field} IS NOT NULL
        """)

        min_date, max_date, count = cur.fetchone()

        if min_date and max_date:
            print(f"\n{field}:")
            print(f"  Earliest: {min_date}")
            print(f"  Latest:   {max_date}")
            print(f"  Count:    {count:,}")

            # Try to parse if it's a numeric date (Excel serial number)
            try:
                # Excel epoch is 1899-12-30
                if isinstance(min_date, (int, float)) and min_date > 10000:
                    from datetime import datetime, timedelta
                    excel_epoch = datetime(1899, 12, 30)
                    min_dt = excel_epoch + timedelta(days=min_date)
                    max_dt = excel_epoch + timedelta(days=max_date)
                    print(f"  Converted earliest: {min_dt.strftime('%Y-%m-%d')}")
                    print(f"  Converted latest:   {max_dt.strftime('%Y-%m-%d')}")
            except:
                pass
    except Exception as e:
        pass

# Check metadata table
print("\n" + "=" * 80)
print("USPTO_METADATA TABLE")
print("=" * 80)

cur.execute("SELECT * FROM uspto_metadata")
metadata = cur.fetchall()

cur.execute("PRAGMA table_info(uspto_metadata)")
meta_schema = cur.fetchall()

print("\nMetadata schema:")
for col in meta_schema:
    col_id, name, dtype, notnull, default, pk = col
    print(f"  {name:20s} {dtype:15s}")

print("\nMetadata records:")
for row in metadata:
    print(f"  {row}")

# Try to find Chinese patents and their dates
print("\n" + "=" * 80)
print("SAMPLE CHINESE ENTITY DATES")
print("=" * 80)

# Get Beijing entities with dates
cur.execute("""
    SELECT a.ee_name, c.registration_dt, c.filing_dt
    FROM uspto_assignee a
    LEFT JOIN uspto_case_file c ON a.rf_id = c.serial_no
    WHERE UPPER(a.ee_city) = 'BEIJING'
    LIMIT 10
""")

beijing_dates = cur.fetchall()

print("\nBeijing entities with dates:")
for name, reg_dt, filing_dt in beijing_dates:
    reg_str = str(reg_dt) if reg_dt else "NULL"
    filing_str = str(filing_dt) if filing_dt else "NULL"
    print(f"  {name[:50]:50s} | Reg: {reg_str:10s} | Filing: {filing_str:10s}")

conn.close()

print("\n" + "=" * 80)

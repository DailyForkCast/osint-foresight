#!/usr/bin/env python3
"""
Deep analysis of OpenAIRE database structure to understand how to extract China-related data
"""

import sqlite3
import json
import re
from pathlib import Path
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

def analyze_openaire_structure():
    """Comprehensive analysis of OpenAIRE database structure"""

    db_path = "F:/OSINT_DATA/openaire_production_comprehensive/openaire_production.db"

    if not Path(db_path).exists():
        print(f"ERROR: Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("=" * 80)
    print("OPENAIRE DATABASE STRUCTURE ANALYSIS")
    print("=" * 80)

    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()

    print(f"\nTotal tables found: {len(tables)}")
    print("\nTables list:")
    for table in tables:
        print(f"  - {table[0]}")

    # Analyze each table
    print("\n" + "=" * 80)
    print("DETAILED TABLE ANALYSIS")
    print("=" * 80)

    for table in tables:
        table_name = table[0]
        # SECURITY: Validate table name before use in SQL
        safe_table = validate_sql_identifier(table_name)

        print(f"\n### Table: {table_name}")
        print("-" * 40)

        # Get column info
        cursor.execute(f"PRAGMA table_info({safe_table})")
        columns = cursor.fetchall()

        print(f"Columns ({len(columns)}):")
        for col in columns[:10]:  # Show first 10 columns
            print(f"  {col[1]:30} {col[2]:15} {'NOT NULL' if col[3] else 'NULL':10} {'PRIMARY KEY' if col[5] else ''}")
        if len(columns) > 10:
            print(f"  ... and {len(columns) - 10} more columns")

        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {safe_table}")
        row_count = cursor.fetchone()[0]
        print(f"\nRow count: {row_count:,}")

        # Sample data for China detection
        print("\nSearching for China-related content...")

        # Build dynamic query based on column names
        text_columns = [col[1] for col in columns if col[2] in ('TEXT', 'VARCHAR', 'CHAR')]

        if text_columns and row_count > 0:
            # Try different search patterns
            search_patterns = [
                ('China', 'china'),
                ('Chinese', 'chinese'),
                ('CN', 'cn'),
                ('Beijing', 'beijing'),
                ('Shanghai', 'shanghai'),
                ('Tsinghua', 'tsinghua'),
                ('中国', '中国'),
                ('中文', '中文')
            ]

            for pattern_name, pattern in search_patterns[:3]:  # Test first 3 patterns
                where_clauses = []
                for col in text_columns[:5]:  # Check first 5 text columns
                    where_clauses.append(f"LOWER(CAST({col} AS TEXT)) LIKE '%{pattern}%'")

                query = f"""
                    SELECT COUNT(*) FROM {safe_table}
                    WHERE {' OR '.join(where_clauses)}
                    LIMIT 1
                """

                try:
                    cursor.execute(query)
                    china_count = cursor.fetchone()[0]
                    if china_count > 0:
                        print(f"  ✓ Found {china_count:,} rows with '{pattern_name}'")

                        # Get sample records
                        sample_query = f"""
                            SELECT * FROM {safe_table}
                            WHERE {' OR '.join(where_clauses)}
                            LIMIT 3
                        """
                        cursor.execute(sample_query)
                        samples = cursor.fetchall()

                        if samples:
                            print(f"\n  Sample record (first 5 fields):")
                            for i, sample in enumerate(samples[:1], 1):
                                for j, (col_info, value) in enumerate(zip(columns[:5], sample[:5])):
                                    if value and str(value).strip():
                                        print(f"    {col_info[1]}: {str(value)[:100]}")
                        break
                except Exception as e:
                    pass  # Skip if column doesn't exist or query fails

        print()

    # Look for specific patterns across all tables
    print("\n" + "=" * 80)
    print("CROSS-TABLE CHINA ANALYSIS")
    print("=" * 80)

    china_tables = []

    for table in tables:
        table_name = table[0]
        # SECURITY: Validate table name before use in SQL
        safe_table = validate_sql_identifier(table_name)

        # Get columns
        cursor.execute(f"PRAGMA table_info({safe_table})")
        columns = cursor.fetchall()
        text_columns = [col[1] for col in columns if col[2] in ('TEXT', 'VARCHAR', 'CHAR')]

        if not text_columns:
            continue

        # Check for any China-related content
        where_clauses = []
        for col in text_columns[:3]:  # Check first 3 text columns
            where_clauses.append(f"LOWER(CAST({col} AS TEXT)) LIKE '%china%'")
            where_clauses.append(f"LOWER(CAST({col} AS TEXT)) LIKE '%chinese%'")

        try:
            query = f"""
                SELECT COUNT(*) FROM {safe_table}
                WHERE {' OR '.join(where_clauses)}
            """
            cursor.execute(query)
            count = cursor.fetchone()[0]

            if count > 0:
                china_tables.append((table_name, count))
                print(f"{table_name:40} {count:10,} China-related records")
        except:
            pass

    # Special analysis for key tables
    print("\n" + "=" * 80)
    print("SPECIAL TABLE INVESTIGATION")
    print("=" * 80)

    # Check if there are any research/publication tables
    research_tables = [t[0] for t in tables if any(keyword in t[0].lower()
                      for keyword in ['research', 'publication', 'paper', 'article', 'project', 'collaboration'])]

    if research_tables:
        print(f"\nFound {len(research_tables)} research-related tables:")
        for table in research_tables:
            print(f"  - {table}")

            # SECURITY: Validate table name before use in SQL
            safe_table = validate_sql_identifier(table)

            # Deep dive into this table
            cursor.execute(f"PRAGMA table_info({safe_table})")
            columns = cursor.fetchall()

            # Look for country, organization, author fields
            relevant_cols = [col[1] for col in columns if any(field in col[1].lower()
                            for field in ['country', 'org', 'author', 'institution', 'affiliation'])]

            if relevant_cols:
                print(f"    Relevant columns: {', '.join(relevant_cols[:5])}")

    # Check for country-specific tables
    country_tables = [t[0] for t in tables if 'country' in t[0].lower()]

    if country_tables:
        print(f"\nFound {len(country_tables)} country-related tables:")
        for table in country_tables:
            # SECURITY: Validate table name before use in SQL
            safe_table = validate_sql_identifier(table)
            cursor.execute(f"SELECT COUNT(*) FROM {safe_table}")
            count = cursor.fetchone()[0]
            print(f"  - {table}: {count:,} records")

            # Check specifically for China
            cursor.execute(f"PRAGMA table_info({safe_table})")
            columns = cursor.fetchall()

            for col in columns:
                if 'country' in col[1].lower() or 'code' in col[1].lower():
                    try:
                        cursor.execute(f"""
                            SELECT DISTINCT {col[1]} FROM {safe_table}
                            WHERE LOWER(CAST({col[1]} AS TEXT)) IN ('china', 'cn', 'chn')
                            LIMIT 5
                        """)
                        china_entries = cursor.fetchall()
                        if china_entries:
                            print(f"    ✓ Found China in {col[1]}: {china_entries}")
                    except:
                        pass

    conn.close()

    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)

    return china_tables

if __name__ == "__main__":
    china_tables = analyze_openaire_structure()

    if china_tables:
        print(f"\nTables with China data: {len(china_tables)}")
        print("\nRecommended extraction targets:")
        for table, count in sorted(china_tables, key=lambda x: x[1], reverse=True)[:5]:
            print(f"  {table:40} {count:10,} records")

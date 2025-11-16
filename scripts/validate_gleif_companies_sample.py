"""
GLEIF Chinese Companies Validation - Sample Verification
=========================================================
Validate that GLEIF database contains real Chinese company registrations in Europe
by sampling and preparing for manual verification.

Author: OSINT Foresight Analysis
Date: 2025-10-25
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import sqlite3
import json
import re
from datetime import datetime
from pathlib import Path

# ============================================================================
# SECURITY: SQL injection prevention through identifier validation
# ============================================================================

def validate_sql_identifier(identifier):
    """
    SECURITY: Validate SQL identifier (table or column name).
    Only allows alphanumeric characters and underscores.
    Prevents SQL injection from database metadata.
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

class GLEIFCompaniesValidator:
    def __init__(self):
        self.db_path = 'F:/OSINT_WAREHOUSE/osint_master.db'
        self.output_dir = Path('analysis/manual_review')
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def get_database_overview(self):
        """Get overview of GLEIF database"""
        print("\n" + "="*70)
        print("GLEIF CHINESE COMPANIES DATABASE OVERVIEW")
        print("="*70)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check if GLEIF table exists
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name LIKE '%gleif%'
        """)
        tables = cursor.fetchall()

        if not tables:
            print("\n⚠️  WARNING: No GLEIF tables found in database")
            print("Available tables with 'entity' or 'company' in name:")
            cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND (
                    name LIKE '%entity%' OR
                    name LIKE '%company%' OR
                    name LIKE '%gleif%'
                )
            """)
            for table in cursor.fetchall():
                print(f"  - {table[0]}")
            conn.close()
            return None

        print(f"\nFound GLEIF tables: {[t[0] for t in tables]}")

        # Prioritize gleif_entities table
        table_names = [t[0] for t in tables]
        if 'gleif_entities' in table_names:
            table_name = 'gleif_entities'
        else:
            table_name = table_names[0]

        # SECURITY: Validate table name before use in SQL
        safe_table = validate_sql_identifier(table_name)
        print(f"Using table: {safe_table}")

        # Get table schema
        print(f"\nTable schema:")
        cursor.execute(f'PRAGMA table_info({safe_table})')
        columns = cursor.fetchall()
        for col in columns:
            print(f"  {col[1]} ({col[2]})")

        # Total entities
        cursor.execute(f'SELECT COUNT(*) FROM {safe_table}')
        total_entities = cursor.fetchone()[0]
        print(f"\nTotal entities in database: {total_entities:,}")

        # Try to identify Chinese entities
        print("\n" + "="*70)
        print("IDENTIFYING CHINESE ENTITIES")
        print("="*70)

        # Method 1: Check for is_chinese_entity flag
        cursor.execute(f"""
            SELECT name FROM pragma_table_info('{safe_table}')
            WHERE name LIKE '%chinese%' OR name LIKE '%china%'
        """)
        chinese_columns = cursor.fetchall()

        if chinese_columns:
            print(f"\nFound Chinese detection columns: {[c[0] for c in chinese_columns]}")
            column_name = chinese_columns[0][0]
            # SECURITY: Validate column name before use in SQL
            safe_column = validate_sql_identifier(column_name)
            cursor.execute(f'SELECT COUNT(*) FROM {safe_table} WHERE {safe_column} = 1')
            chinese_entities = cursor.fetchone()[0]
            print(f"Chinese entities (via {safe_column}): {chinese_entities:,}")
        else:
            print("\n⚠️  No Chinese detection column found")
            # Try country-based detection
            cursor.execute(f"""
                SELECT name FROM pragma_table_info('{safe_table}')
                WHERE name LIKE '%country%' OR name LIKE '%jurisdiction%'
            """)
            country_columns = cursor.fetchall()

            if country_columns:
                country_col = country_columns[0][0]
                # SECURITY: Validate column name before use in SQL
                safe_country_col = validate_sql_identifier(country_col)
                print(f"Trying country-based detection via: {safe_country_col}")
                cursor.execute(f"""
                    SELECT COUNT(*) FROM {safe_table}
                    WHERE {safe_country_col} IN ('CN', 'HK', 'China', 'Hong Kong')
                """)
                chinese_entities = cursor.fetchone()[0]
                print(f"Chinese entities (via country): {chinese_entities:,}")
            else:
                print("❌ Cannot identify Chinese entities - no country column")
                chinese_entities = 0

        # Regional distribution
        print("\n" + "="*70)
        print("REGIONAL DISTRIBUTION (if available)")
        print("="*70)

        cursor.execute(f"""
            SELECT name FROM pragma_table_info('{safe_table}')
            WHERE name LIKE '%country%' OR name LIKE '%jurisdiction%' OR name LIKE '%region%'
        """)
        region_columns = cursor.fetchall()

        if region_columns:
            region_col = region_columns[0][0]
            # SECURITY: Validate column name before use in SQL
            safe_region_col = validate_sql_identifier(region_col)
            print(f"\nTop 10 countries/regions (via {safe_region_col}):")
            cursor.execute(f"""
                SELECT {safe_region_col}, COUNT(*) as count
                FROM {safe_table}
                GROUP BY {safe_region_col}
                ORDER BY count DESC
                LIMIT 10
            """)
            for country, count in cursor.fetchall():
                print(f"  {country}: {count:,}")

        conn.close()
        return table_name

    def check_for_synthetic_patterns(self, table_name):
        """Check if GLEIF data shows synthetic patterns like EPO did"""
        print("\n" + "="*70)
        print("SYNTHETIC DATA DETECTION")
        print("="*70)

        # SECURITY: Validate table name before use in SQL
        safe_table = validate_sql_identifier(table_name)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check 1: Date distribution
        print("\n[1/4] Checking date distribution...")
        cursor.execute(f"""
            SELECT name FROM pragma_table_info('{safe_table}')
            WHERE name LIKE '%date%' OR name LIKE '%created%' OR name LIKE '%registered%'
        """)
        date_columns = cursor.fetchall()

        if date_columns:
            date_col = date_columns[0][0]
            # SECURITY: Validate column name before use in SQL
            safe_date_col = validate_sql_identifier(date_col)
            cursor.execute(f"""
                SELECT {safe_date_col}, COUNT(*) as count
                FROM {safe_table}
                GROUP BY {safe_date_col}
                ORDER BY count DESC
                LIMIT 5
            """)
            results = cursor.fetchall()
            print(f"   Top 5 {safe_date_col} values:")
            for date_val, count in results:
                print(f"   {date_val}: {count:,} entities")

            # Red flag: >50% have same date
            if results and results[0][1] / sum(r[1] for r in results) > 0.5:
                print("   ⚠️  WARNING: >50% of entities have identical date (suspicious)")

        # Check 2: Sequential naming
        print("\n[2/4] Checking for sequential naming patterns...")
        cursor.execute(f"""
            SELECT name FROM pragma_table_info('{safe_table}')
            WHERE name LIKE '%name%' OR name LIKE '%legal%'
        """)
        name_columns = cursor.fetchall()

        if name_columns:
            name_col = name_columns[0][0]
            # SECURITY: Validate column name before use in SQL
            safe_name_col = validate_sql_identifier(name_col)
            cursor.execute(f"""
                SELECT {safe_name_col}
                FROM {safe_table}
                WHERE {safe_name_col} LIKE '%#%'
                LIMIT 10
            """)
            sequential = cursor.fetchall()
            if sequential:
                print(f"   ⚠️  Found {len(sequential)} entities with '#' in name (sequential numbering):")
                for name in sequential[:5]:
                    print(f"   - {name[0]}")

        # Check 3: Perfect round numbers
        print("\n[3/4] Checking for perfect round numbers in entity counts...")
        cursor.execute(f"""
            SELECT name FROM pragma_table_info('{safe_table}')
            WHERE name LIKE '%name%' OR name LIKE '%legal%'
        """)
        if name_columns:
            name_col = name_columns[0][0]
            # SECURITY: Validate column name before use in SQL (reusing safe_name_col if available)
            safe_name_col = validate_sql_identifier(name_col)
            cursor.execute(f"""
                SELECT SUBSTR({safe_name_col}, 1, 20) as prefix, COUNT(*) as count
                FROM {safe_table}
                GROUP BY prefix
                HAVING count > 100
                ORDER BY count DESC
                LIMIT 10
            """)
            results = cursor.fetchall()
            print("   Entity name prefix counts (>100):")
            for prefix, count in results:
                print(f"   {prefix}: {count:,}")
                # Red flag: exact multiples of 100
                if count % 100 == 0 and count > 100:
                    print(f"      ⚠️  Perfect multiple of 100 (suspicious)")

        # Check 4: Generic names
        print("\n[4/4] Checking for generic/synthetic names...")
        generic_patterns = ['Research Institute', 'Technology Company #', 'Corporation #']
        if name_columns:
            name_col = name_columns[0][0]
            # SECURITY: Validate column name before use in SQL
            safe_name_col = validate_sql_identifier(name_col)
            for pattern in generic_patterns:
                cursor.execute(f"""
                    SELECT COUNT(*) FROM {safe_table}
                    WHERE {safe_name_col} LIKE '%{pattern}%'
                """)
                count = cursor.fetchone()[0]
                if count > 0:
                    print(f"   ⚠️  Found {count} entities with pattern: '{pattern}'")

        conn.close()

    def generate_stratified_sample(self, table_name):
        """Generate stratified sample for manual verification"""
        print("\n" + "="*70)
        print("GENERATING STRATIFIED SAMPLE")
        print("="*70)

        # SECURITY: Validate table name before use in SQL
        safe_table = validate_sql_identifier(table_name)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get table schema to know what columns are available
        cursor.execute(f'PRAGMA table_info({safe_table})')
        columns = {col[1]: col[2] for col in cursor.fetchall()}

        # Identify key columns
        name_col = next((c for c in columns if 'name' in c.lower()), None)
        country_col = next((c for c in columns if 'country' in c.lower() or 'jurisdiction' in c.lower()), None)
        lei_col = next((c for c in columns if 'lei' in c.lower() or 'id' in c.lower()), None)

        print(f"\nKey columns identified:")
        print(f"  Name: {name_col}")
        print(f"  Country: {country_col}")
        print(f"  LEI: {lei_col}")

        if not name_col:
            print("\n❌ ERROR: Cannot find name column")
            conn.close()
            return []

        # SECURITY: Validate all column names before use in SQL
        safe_name_col = validate_sql_identifier(name_col)
        safe_country_col = validate_sql_identifier(country_col) if country_col else None
        safe_lei_col = validate_sql_identifier(lei_col) if lei_col else 'rowid'

        samples = []

        # Sample strategy depends on available columns
        # Try to get diverse sample from different European countries

        print("\n[1/3] Sampling Chinese entities in Europe...")

        # Build query based on available columns (using validated identifiers)
        select_cols = [safe_lei_col, safe_name_col]
        if safe_country_col:
            select_cols.append(safe_country_col)

        query = f"""
            SELECT {', '.join(select_cols)}
            FROM {safe_table}
            WHERE {safe_name_col} IS NOT NULL
        """

        # Add Chinese detection if possible
        if 'is_chinese_entity' in columns:
            query += " AND is_chinese_entity = 1"

        # Add European location if possible
        if safe_country_col:
            european_countries = ['GB', 'DE', 'FR', 'IT', 'ES', 'NL', 'BE', 'AT', 'SE', 'DK']
            query += f" AND {safe_country_col} IN ({','.join(['?' for _ in european_countries])})"
            query += " LIMIT 15"
            cursor.execute(query, european_countries)
        else:
            query += " LIMIT 15"
            cursor.execute(query)

        for row in cursor.fetchall():
            sample = {
                'sample_category': 'Chinese Entity in Europe',
                'lei_code': row[0],
                'legal_name': row[1]
            }
            if country_col and len(row) > 2:
                sample['country'] = row[2]
            samples.append(sample)

        print(f"   Found {len([s for s in samples if s['sample_category'] == 'Chinese Entity in Europe'])} entities")

        # Sample 2: Major Chinese companies (if identifiable)
        print("[2/3] Sampling major known Chinese companies...")
        major_companies = ['Huawei', 'Alibaba', 'Tencent', 'Xiaomi', 'Baidu', 'ZTE', 'BYD', 'Lenovo']

        for company in major_companies:
            query = f"""
                SELECT {', '.join(select_cols)}
                FROM {safe_table}
                WHERE {safe_name_col} LIKE '%{company}%'
                LIMIT 1
            """
            cursor.execute(query)
            row = cursor.fetchone()
            if row:
                sample = {
                    'sample_category': 'Major Chinese Company',
                    'lei_code': row[0],
                    'legal_name': row[1]
                }
                if country_col and len(row) > 2:
                    sample['country'] = row[2]
                samples.append(sample)

        print(f"   Found {len([s for s in samples if s['sample_category'] == 'Major Chinese Company'])} companies")

        # Sample 3: Random Chinese entities
        print("[3/3] Sampling random Chinese entities...")
        query = f"""
            SELECT {', '.join(select_cols)}
            FROM {safe_table}
            WHERE {safe_name_col} IS NOT NULL
        """

        if 'is_chinese_entity' in columns:
            query += " AND is_chinese_entity = 1"

        query += " ORDER BY RANDOM() LIMIT 10"
        cursor.execute(query)

        for row in cursor.fetchall():
            sample = {
                'sample_category': 'Random Chinese Entity',
                'lei_code': row[0],
                'legal_name': row[1]
            }
            if country_col and len(row) > 2:
                sample['country'] = row[2]
            samples.append(sample)

        print(f"   Found {len([s for s in samples if s['sample_category'] == 'Random Chinese Entity'])} entities")

        conn.close()

        print(f"\n[OK] Total sample size: {len(samples)} entities")
        return samples

    def save_sample(self, samples):
        """Save sample to JSON file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = self.output_dir / f'gleif_validation_sample_{timestamp}.json'

        output = {
            'validation_metadata': {
                'generated_timestamp': timestamp,
                'database_path': str(self.db_path),
                'total_sample_size': len(samples),
                'sample_categories': {}
            },
            'validation_protocol': {
                'for_each_entity': [
                    '1. Search GLEIF website for LEI code',
                    '2. Verify entity exists in GLEIF database',
                    '3. Verify legal name matches Chinese entity',
                    '4. Search web for company operations and ownership',
                    '5. Verify entity is actually Chinese (not false positive)',
                    '6. Categorize as: VERIFIED, FALSE POSITIVE, UNABLE TO VERIFY'
                ],
                'gleif_search_url': 'https://search.gleif.org/',
                'search_format': 'Enter LEI code in search box'
            },
            'samples': samples
        }

        # Count categories
        for sample in samples:
            cat = sample['sample_category']
            output['validation_metadata']['sample_categories'][cat] = \
                output['validation_metadata']['sample_categories'].get(cat, 0) + 1

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print(f"\n[OK] Sample saved: {output_file}")
        return output_file

    def run(self):
        """Run complete validation"""
        print("\n" + "="*70)
        print("GLEIF CHINESE COMPANIES VALIDATION")
        print("="*70)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Step 1: Database overview
        table_name = self.get_database_overview()

        if not table_name:
            print("\n❌ ERROR: Cannot proceed without GLEIF table")
            return

        # Step 2: Check for synthetic data patterns
        self.check_for_synthetic_patterns(table_name)

        # Step 3: Generate stratified sample
        samples = self.generate_stratified_sample(table_name)

        if not samples:
            print("\n❌ ERROR: No samples generated")
            return

        # Step 4: Save sample to JSON
        json_file = self.save_sample(samples)

        print("\n" + "="*70)
        print("VALIDATION PREPARATION COMPLETE")
        print("="*70)
        print(f"\nJSON sample: {json_file}")
        print(f"\nTotal entities to verify: {len(samples)}")
        print("\nNext steps:")
        print("  1. Open the JSON file")
        print("  2. For each entity, search GLEIF website")
        print("  3. Verify LEI code, legal name, and Chinese ownership")
        print("  4. Record findings")
        print("="*70)

if __name__ == '__main__':
    validator = GLEIFCompaniesValidator()
    validator.run()

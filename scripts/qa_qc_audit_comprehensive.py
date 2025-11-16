#!/usr/bin/env python3
"""
Comprehensive QA/QC Audit for OpenAIRE and OpenSanctions Data
Validates data quality, schema compliance, and field completeness
"""

import sqlite3
from datetime import datetime
from collections import defaultdict

def validate_column_name(col_name, valid_columns):
    """
    SECURITY: Validate column name against schema columns to prevent SQL injection.
    Only accepts column names from database schema (from PRAGMA table_info).
    """
    if col_name not in valid_columns:
        raise ValueError(f"Invalid column name: {col_name}. Not in schema.")
    return col_name

def main():
    print('=' * 80)
    print('COMPREHENSIVE QA/QC AUDIT - OpenAIRE & OpenSanctions')
    print('=' * 80)
    print(f'Audit Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print(f'Database: F:/OSINT_WAREHOUSE/osint_master.db')
    print()

    conn = sqlite3.connect('F:/OSINT_WAREHOUSE/osint_master.db', timeout=60)
    cur = conn.cursor()

    # ============================================================================
    # PART 1: OpenAIRE Research Products Validation
    # ============================================================================
    print('=' * 80)
    print('PART 1: OpenAIRE Research Products (openaire_research)')
    print('=' * 80)
    print()

    # 1. Schema Validation
    print('1. SCHEMA VALIDATION:')
    cur.execute('PRAGMA table_info(openaire_research)')
    schema = cur.fetchall()
    print(f'   Total columns: {len(schema)}')
    print('   Column structure:')
    for col in schema:
        col_id, name, dtype, notnull, default, pk = col
        nullable = 'NOT NULL' if notnull else 'NULLABLE'
        pk_flag = ' [PRIMARY KEY]' if pk else ''
        print(f'      {name:30} {dtype:15} {nullable:10}{pk_flag}')
    print()

    # 2. Record Count
    cur.execute('SELECT COUNT(*) FROM openaire_research')
    total_records = cur.fetchone()[0]
    print(f'2. TOTAL RECORDS: {total_records:,}')
    print()

    # 3. NULL Analysis
    print('3. NULL ANALYSIS (Field Completeness):')
    # SECURITY: Get valid column names from schema for validation
    valid_columns = {col[1] for col in schema}
    null_counts = {}
    for col in schema:
        col_name = col[1]
        # SECURITY: Validate column name (already from schema, but making it explicit)
        safe_col = validate_column_name(col_name, valid_columns)
        cur.execute(f'SELECT COUNT(*) FROM openaire_research WHERE "{safe_col}" IS NULL OR "{safe_col}" = ""')
        null_count = cur.fetchone()[0]
        null_pct = (null_count / total_records * 100) if total_records > 0 else 0
        null_counts[col_name] = {'count': null_count, 'pct': null_pct}
        status = 'OK' if null_pct < 5 else 'WARN' if null_pct < 20 else 'CRITICAL'
        print(f'   {col_name:30} NULL: {null_count:>8,} ({null_pct:>5.1f}%) [{status}]')
    print()

    # 4. Sample Records Inspection
    print('4. SAMPLE RECORDS (First 3):')
    cur.execute('SELECT * FROM openaire_research LIMIT 3')
    sample = cur.fetchall()
    if sample:
        col_names = [col[1] for col in schema]
        for i, record in enumerate(sample, 1):
            print(f'   Record {i}:')
            for col_name, value in zip(col_names, record):
                val_str = str(value)[:60] if value else '[NULL]'
                print(f'      {col_name:25} = {val_str}')
            print()
    print()

    # 5. Random Sample for Manual Review
    print('5. RANDOM SAMPLE (10 records for manual inspection):')
    cur.execute('SELECT research_id, title, publication_date FROM openaire_research ORDER BY RANDOM() LIMIT 10')
    random_sample = cur.fetchall()
    for i, row in enumerate(random_sample, 1):
        rid = row[0] if row[0] else '[NO ID]'
        title = row[1] if row[1] else '[NO TITLE]'
        pub_date = row[2] if row[2] else '[NO DATE]'
        title_short = (title[:70] + '...') if len(title) > 70 else title
        print(f'   {i:2}. [{rid}]')
        print(f'       Title: {title_short}')
        print(f'       Published: {pub_date}')
    print()

    # 6. Date Range Validation
    print('6. DATE RANGE VALIDATION:')
    cur.execute('SELECT MIN(publication_date), MAX(publication_date) FROM openaire_research WHERE publication_date IS NOT NULL')
    result = cur.fetchone()
    min_date = result[0] if result[0] else '[NONE]'
    max_date = result[1] if result[1] else '[NONE]'
    print(f'   Earliest publication: {min_date}')
    print(f'   Latest publication:   {max_date}')

    # Check for future dates
    # SECURITY NOTE: datetime.now() is programmatic (not user input), so this is safe
    current_date = datetime.now().strftime("%Y-%m-%d")
    cur.execute('SELECT COUNT(*) FROM openaire_research WHERE publication_date > ?', (current_date,))
    future_dates = cur.fetchone()[0]
    print(f'   Future dates found:   {future_dates:,} [{"OK" if future_dates == 0 else "ISSUE"}]')

    # Check for very old dates (before 1900)
    cur.execute('SELECT COUNT(*) FROM openaire_research WHERE publication_date < "1900-01-01"')
    ancient_dates = cur.fetchone()[0]
    print(f'   Pre-1900 dates:       {ancient_dates:,} [{"OK" if ancient_dates == 0 else "WARN"}]')
    print()

    # ============================================================================
    # PART 2: OpenAIRE Collaborations Validation
    # ============================================================================
    print('=' * 80)
    print('PART 2: OpenAIRE Collaborations (openaire_collaborations)')
    print('=' * 80)
    print()

    # 1. Schema Validation
    print('1. SCHEMA VALIDATION:')
    cur.execute('PRAGMA table_info(openaire_collaborations)')
    schema_collab = cur.fetchall()
    print(f'   Total columns: {len(schema_collab)}')
    print('   Column structure:')
    for col in schema_collab:
        col_id, name, dtype, notnull, default, pk = col
        nullable = 'NOT NULL' if notnull else 'NULLABLE'
        pk_flag = ' [PRIMARY KEY]' if pk else ''
        print(f'      {name:30} {dtype:15} {nullable:10}{pk_flag}')
    print()

    # 2. Record Count
    cur.execute('SELECT COUNT(*) FROM openaire_collaborations')
    total_collab = cur.fetchone()[0]
    print(f'2. TOTAL RECORDS: {total_collab:,}')
    print()

    # 3. NULL Analysis
    print('3. NULL ANALYSIS (Field Completeness):')
    # SECURITY: Get valid column names from schema for validation
    valid_collab_columns = {col[1] for col in schema_collab}
    for col in schema_collab:
        col_name = col[1]
        # SECURITY: Validate column name
        safe_col = validate_column_name(col_name, valid_collab_columns)
        cur.execute(f'SELECT COUNT(*) FROM openaire_collaborations WHERE "{safe_col}" IS NULL OR "{safe_col}" = ""')
        null_count = cur.fetchone()[0]
        null_pct = (null_count / total_collab * 100) if total_collab > 0 else 0
        status = 'OK' if null_pct < 5 else 'WARN' if null_pct < 20 else 'CRITICAL'
        print(f'   {col_name:30} NULL: {null_count:>8,} ({null_pct:>5.1f}%) [{status}]')
    print()

    # 4. Country Code Validation
    print('4. COUNTRY CODE VALIDATION:')
    cur.execute('SELECT country_code, COUNT(*) as cnt FROM openaire_collaborations WHERE country_code IS NOT NULL GROUP BY country_code ORDER BY cnt DESC LIMIT 20')
    top_countries = cur.fetchall()
    print(f'   Total distinct country codes: {len(top_countries)}')
    print('   Top 20 countries by collaboration count:')
    for country, count in top_countries:
        print(f'      {country:10} {count:>8,}')
    print()

    # Check for invalid country codes (not 2 letters)
    cur.execute('SELECT COUNT(*) FROM openaire_collaborations WHERE country_code IS NOT NULL AND LENGTH(country_code) != 2')
    invalid_codes = cur.fetchone()[0]
    print(f'   Invalid country codes (not 2 chars): {invalid_codes:,} [{"OK" if invalid_codes == 0 else "ISSUE"}]')
    print()

    # ============================================================================
    # PART 3: OpenSanctions Entities Validation
    # ============================================================================
    print('=' * 80)
    print('PART 3: OpenSanctions Entities (opensanctions_entities)')
    print('=' * 80)
    print()

    # 1. Schema Validation
    print('1. SCHEMA VALIDATION:')
    cur.execute('PRAGMA table_info(opensanctions_entities)')
    schema_sanctions = cur.fetchall()
    print(f'   Total columns: {len(schema_sanctions)}')
    print('   Column structure:')
    for col in schema_sanctions:
        col_id, name, dtype, notnull, default, pk = col
        nullable = 'NOT NULL' if notnull else 'NULLABLE'
        pk_flag = ' [PRIMARY KEY]' if pk else ''
        print(f'      {name:30} {dtype:15} {nullable:10}{pk_flag}')
    print()

    # 2. Record Count
    cur.execute('SELECT COUNT(*) FROM opensanctions_entities')
    total_sanctions = cur.fetchone()[0]
    print(f'2. TOTAL RECORDS: {total_sanctions:,}')
    print()

    # 3. NULL Analysis
    print('3. NULL ANALYSIS (Field Completeness):')
    # SECURITY: Get valid column names from schema for validation
    valid_sanction_columns = {col[1] for col in schema_sanctions}
    sanction_nulls = {}
    for col in schema_sanctions:
        col_name = col[1]
        # SECURITY: Validate column name
        safe_col = validate_column_name(col_name, valid_sanction_columns)
        cur.execute(f'SELECT COUNT(*) FROM opensanctions_entities WHERE "{safe_col}" IS NULL OR "{safe_col}" = ""')
        null_count = cur.fetchone()[0]
        null_pct = (null_count / total_sanctions * 100) if total_sanctions > 0 else 0
        sanction_nulls[col_name] = {'count': null_count, 'pct': null_pct}
        status = 'OK' if null_pct < 5 else 'WARN' if null_pct < 20 else 'CRITICAL'
        print(f'   {col_name:30} NULL: {null_count:>8,} ({null_pct:>5.1f}%) [{status}]')
    print()

    # 4. Entity Type Distribution
    print('4. ENTITY TYPE DISTRIBUTION:')
    cur.execute('SELECT entity_type, COUNT(*) as cnt FROM opensanctions_entities WHERE entity_type IS NOT NULL GROUP BY entity_type ORDER BY cnt DESC')
    entity_types = cur.fetchall()
    print(f'   Total entity types: {len(entity_types)}')
    for etype, count in entity_types:
        pct = (count / total_sanctions * 100) if total_sanctions > 0 else 0
        print(f'      {etype:30} {count:>8,} ({pct:>5.1f}%)')
    print()

    # 5. Chinese Affiliation Analysis
    print('5. CHINESE AFFILIATION ANALYSIS:')
    cur.execute('SELECT china_related, COUNT(*) as cnt FROM opensanctions_entities GROUP BY china_related')
    china_breakdown = cur.fetchall()
    for related, count in china_breakdown:
        pct = (count / total_sanctions * 100) if total_sanctions > 0 else 0
        if related == 1 or str(related) == '1':
            status = 'YES'
        elif related == 0 or str(related) == '0':
            status = 'NO'
        else:
            status = 'NULL'
        print(f'   China-related={status:5} {count:>8,} ({pct:>5.1f}%)')
    print()

    # 6. Sample Chinese Entities
    print('6. SAMPLE CHINESE ENTITIES (10 random):')
    cur.execute('SELECT entity_id, entity_name, entity_type, sanction_programs FROM opensanctions_entities WHERE china_related = 1 ORDER BY RANDOM() LIMIT 10')
    chinese_sample = cur.fetchall()
    for i, row in enumerate(chinese_sample, 1):
        eid = row[0] if row[0] else '[NO ID]'
        name = row[1] if row[1] else '[NO NAME]'
        etype = row[2] if row[2] else '[NO TYPE]'
        programs = row[3] if row[3] else '[NO PROGRAMS]'

        name_short = (name[:50] + '...') if len(name) > 50 else name
        programs_short = (programs[:50] + '...') if len(programs) > 50 else programs
        print(f'   {i:2}. [{eid}]')
        print(f'       Name: {name_short}')
        print(f'       Type: {etype}')
        print(f'       Programs: {programs_short}')
    print()

    # 7. Sample Non-Chinese Entities
    print('7. SAMPLE NON-CHINESE ENTITIES (10 random):')
    cur.execute('SELECT entity_id, entity_name, entity_type, countries FROM opensanctions_entities WHERE (china_related = 0 OR china_related IS NULL) ORDER BY RANDOM() LIMIT 10')
    non_chinese_sample = cur.fetchall()
    for i, row in enumerate(non_chinese_sample, 1):
        eid = row[0] if row[0] else '[NO ID]'
        name = row[1] if row[1] else '[NO NAME]'
        etype = row[2] if row[2] else '[NO TYPE]'
        countries = row[3] if row[3] else '[NO COUNTRIES]'

        name_short = (name[:50] + '...') if len(name) > 50 else name
        countries_short = (countries[:50] + '...') if len(countries) > 50 else countries
        print(f'   {i:2}. [{eid}]')
        print(f'       Name: {name_short}')
        print(f'       Type: {etype}')
        print(f'       Countries: {countries_short}')
    print()

    # 8. Sanction Programs Distribution
    print('8. SANCTION PROGRAMS (Top 20 by frequency):')
    cur.execute('SELECT sanction_programs, COUNT(*) as cnt FROM opensanctions_entities WHERE sanction_programs IS NOT NULL AND sanction_programs != "" GROUP BY sanction_programs ORDER BY cnt DESC LIMIT 20')
    programs = cur.fetchall()
    for program, count in programs:
        program_short = (program[:60] + '...') if program and len(program) > 60 else program
        print(f'      {count:>6,} entities: {program_short}')
    print()

    conn.close()

    print('=' * 80)
    print('QA/QC AUDIT COMPLETE')
    print('=' * 80)

if __name__ == '__main__':
    main()

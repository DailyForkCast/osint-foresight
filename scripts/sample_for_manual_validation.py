#!/usr/bin/env python3
"""
Sample records from each data source for manual validation
Generates Excel file with detection details for review
"""

import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime

DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"
OUTPUT_DIR = Path("C:/Projects/OSINT - Foresight/analysis/manual_review")
OUTPUT_DIR.mkdir(exist_ok=True)

SAMPLE_SIZE = 100

def sample_usaspending():
    """Sample USAspending detections"""
    print("\n" + "="*80)
    print("SAMPLING: USAspending")
    print("="*80)

    conn = sqlite3.connect(DB_PATH)

    # Check which table has data
    tables_to_check = [
        'usaspending_china_305',
        'usaspending_china_374',
        'usaspending_china_101'
    ]

    for table in tables_to_check:
        try:
            count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            if count > 0:
                print(f"  Found {count:,} records in {table}")

                query = f"""
                    SELECT
                        recipient_name,
                        award_description,
                        pop_country_name,
                        recipient_country_name,
                        award_amount,
                        importance_tier,
                        '{table}' as source_table
                    FROM {table}
                    ORDER BY RANDOM()
                    LIMIT {SAMPLE_SIZE}
                """

                df = pd.read_sql_query(query, conn)
                conn.close()
                print(f"  Sampled {len(df)} records")
                return df

        except sqlite3.OperationalError:
            continue

    conn.close()
    print("  No USAspending data found")
    return pd.DataFrame()

def sample_ted():
    """Sample TED contract detections"""
    print("\n" + "="*80)
    print("SAMPLING: TED Contracts")
    print("="*80)

    conn = sqlite3.connect(DB_PATH)

    # Check TED tables
    try:
        # Try ted_contracts_production first
        count = conn.execute("""
            SELECT COUNT(*) FROM ted_contracts_production
            WHERE is_chinese_related = 1
        """).fetchone()[0]

        if count > 0:
            print(f"  Found {count:,} Chinese-related contracts")

            query = f"""
                SELECT
                    ca_name as contractor_name,
                    contract_title,
                    contractor_info,
                    iso_country,
                    publication_date,
                    'ted_contracts_production' as source_table
                FROM ted_contracts_production
                WHERE is_chinese_related = 1
                ORDER BY RANDOM()
                LIMIT {SAMPLE_SIZE}
            """

            df = pd.read_sql_query(query, conn)
            conn.close()
            print(f"  Sampled {len(df)} records")
            return df

    except sqlite3.OperationalError as e:
        print(f"  Error accessing TED data: {e}")

    conn.close()
    return pd.DataFrame()

def sample_uspto():
    """Sample USPTO patent detections"""
    print("\n" + "="*80)
    print("SAMPLING: USPTO Patents")
    print("="*80)

    conn = sqlite3.connect(DB_PATH)

    # Check USPTO tables
    tables_to_check = [
        'uspto_patents_chinese',
        'uspto_patents_production'
    ]

    for table in tables_to_check:
        try:
            count_query = f"SELECT COUNT(*) FROM {table}"
            if table == 'uspto_patents_production':
                count_query = f"SELECT COUNT(*) FROM {table} WHERE is_chinese = 1"

            count = conn.execute(count_query).fetchone()[0]

            if count > 0:
                print(f"  Found {count:,} records in {table}")

                where_clause = "WHERE is_chinese = 1" if table == 'uspto_patents_production' else ""

                query = f"""
                    SELECT
                        assignee_name,
                        title as patent_title,
                        assignee_city,
                        assignee_country,
                        grant_date,
                        confidence,
                        '{table}' as source_table
                    FROM {table}
                    {where_clause}
                    ORDER BY RANDOM()
                    LIMIT {SAMPLE_SIZE}
                """

                df = pd.read_sql_query(query, conn)
                conn.close()
                print(f"  Sampled {len(df)} records")
                return df

        except sqlite3.OperationalError:
            continue

    conn.close()
    print("  No USPTO data found")
    return pd.DataFrame()

def sample_openalex():
    """Sample OpenAlex detections"""
    print("\n" + "="*80)
    print("SAMPLING: OpenAlex")
    print("="*80)

    conn = sqlite3.connect(DB_PATH)

    try:
        count = conn.execute("SELECT COUNT(*) FROM openalex_works").fetchone()[0]

        if count > 0:
            print(f"  Found {count:,} works")

            query = f"""
                SELECT
                    title,
                    technology_domain,
                    validation_keyword,
                    validation_topic,
                    primary_topic,
                    publication_year,
                    'openalex_works' as source_table
                FROM openalex_works
                ORDER BY RANDOM()
                LIMIT {SAMPLE_SIZE}
            """

            df = pd.read_sql_query(query, conn)
            conn.close()
            print(f"  Sampled {len(df)} records")
            return df

    except sqlite3.OperationalError as e:
        print(f"  Error accessing OpenAlex data: {e}")

    conn.close()
    return pd.DataFrame()

def main():
    """Main sampling function"""
    print("="*80)
    print("PRECISION VALIDATION - PRODUCTION DATA SAMPLING")
    print("="*80)
    print(f"Sample size: {SAMPLE_SIZE} records per source")
    print(f"Output directory: {OUTPUT_DIR}")

    # Sample from each source
    usaspending_sample = sample_usaspending()
    ted_sample = sample_ted()
    uspto_sample = sample_uspto()
    openalex_sample = sample_openalex()

    # Create Excel file with multiple sheets
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = OUTPUT_DIR / f"precision_validation_samples_{timestamp}.xlsx"

    print(f"\n{'='*80}")
    print("CREATING EXCEL FILE")
    print(f"{'='*80}")

    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:

        if not usaspending_sample.empty:
            # Add validation columns
            usaspending_sample['is_true_positive'] = ''
            usaspending_sample['notes'] = ''
            usaspending_sample.to_excel(writer, sheet_name='USAspending', index=False)
            print(f"  [OK] USAspending: {len(usaspending_sample)} records")

        if not ted_sample.empty:
            ted_sample['is_true_positive'] = ''
            ted_sample['notes'] = ''
            ted_sample.to_excel(writer, sheet_name='TED', index=False)
            print(f"  [OK] TED: {len(ted_sample)} records")

        if not uspto_sample.empty:
            uspto_sample['is_true_positive'] = ''
            uspto_sample['notes'] = ''
            uspto_sample.to_excel(writer, sheet_name='USPTO', index=False)
            print(f"  [OK] USPTO: {len(uspto_sample)} records")

        if not openalex_sample.empty:
            openalex_sample['is_true_positive'] = ''
            openalex_sample['notes'] = ''
            openalex_sample.to_excel(writer, sheet_name='OpenAlex', index=False)
            print(f"  [OK] OpenAlex: {len(openalex_sample)} records")

        # Add instructions sheet
        instructions = pd.DataFrame({
            'Column': ['is_true_positive', 'notes'],
            'Instructions': [
                'Enter YES if this is a genuine Chinese connection, NO if false positive, UNCERTAIN if unclear',
                'Add any notes about why this is/is not a true positive'
            ]
        })
        instructions.to_excel(writer, sheet_name='Instructions', index=False)
        print(f"  [OK] Instructions sheet added")

    print(f"\n{'='*80}")
    print("COMPLETE")
    print(f"{'='*80}")
    print(f"Output file: {output_file}")
    print(f"\nNext steps:")
    print(f"1. Open the Excel file")
    print(f"2. Review each record and fill in 'is_true_positive' column (YES/NO/UNCERTAIN)")
    print(f"3. Add notes for false positives or uncertain cases")
    print(f"4. Run calculate_precision_from_review.py to analyze results")

    return output_file

if __name__ == "__main__":
    output_file = main()

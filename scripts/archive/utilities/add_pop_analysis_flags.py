#!/usr/bin/env python3
"""
Add Place of Performance (POP) analysis flags to USAspending v2 data.

This addresses the data quality issue where recipient_country_code in USAspending
often reflects where work is performed, not where the company is based.
"""

import sqlite3
from pathlib import Path
from datetime import datetime

def add_pop_flags():
    """Add POP analysis columns and populate them."""

    db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")

    print("="*80)
    print("Adding Place of Performance (POP) Analysis Flags")
    print("="*80 + "\n")

    conn = sqlite3.connect(db_path, timeout=60)
    cursor = conn.cursor()

    # Step 1: Add new columns
    print("Step 1: Adding new columns...")

    try:
        cursor.execute('''
            ALTER TABLE usaspending_china_374_v2
            ADD COLUMN pop_matches_origin INTEGER DEFAULT 0
        ''')
        print("  Added pop_matches_origin column")
    except sqlite3.OperationalError:
        print("  pop_matches_origin column already exists")

    try:
        cursor.execute('''
            ALTER TABLE usaspending_china_374_v2
            ADD COLUMN pop_analysis_category TEXT
        ''')
        print("  Added pop_analysis_category column")
    except sqlite3.OperationalError:
        print("  pop_analysis_category column already exists")

    conn.commit()

    # Step 2: Populate the flags
    print("\nStep 2: Populating POP analysis flags...")

    cursor.execute('''
        UPDATE usaspending_china_374_v2
        SET
            pop_matches_origin = CASE
                -- Direct match: CHN recipient in CHN
                WHEN (entity_country_of_origin = 'CN' AND pop_country IN ('CHN', 'CHINA')) THEN 1
                -- Taiwan match
                WHEN (entity_country_of_origin = 'TW' AND pop_country = 'TWN') THEN 1
                -- Hong Kong match
                WHEN (entity_country_of_origin = 'HK' AND pop_country IN ('HKG', 'HONG KONG')) THEN 1
                -- Macao match
                WHEN (entity_country_of_origin = 'MO' AND pop_country IN ('MAC', 'MACAO')) THEN 1
                ELSE 0
            END,
            pop_analysis_category = CASE
                -- Category 1: Origin and POP match (highest confidence)
                WHEN (entity_country_of_origin = 'CN' AND pop_country IN ('CHN', 'CHINA')) THEN 'VERIFIED_POP_MATCH'
                WHEN (entity_country_of_origin = 'TW' AND pop_country = 'TWN') THEN 'VERIFIED_POP_MATCH'
                WHEN (entity_country_of_origin = 'HK' AND pop_country IN ('HKG', 'HONG KONG')) THEN 'VERIFIED_POP_MATCH'
                WHEN (entity_country_of_origin = 'MO' AND pop_country IN ('MAC', 'MACAO')) THEN 'VERIFIED_POP_MATCH'

                -- Category 2: Entity from origin country, work performed in USA
                WHEN pop_country = 'USA' THEN 'ENTITY_FROM_ORIGIN_WORK_IN_USA'

                -- Category 3: Entity from origin country, work performed elsewhere
                WHEN pop_country IS NOT NULL AND pop_country != '' THEN 'ENTITY_FROM_ORIGIN_WORK_ELSEWHERE'

                -- Category 4: POP unknown/null
                ELSE 'POP_UNKNOWN'
            END
    ''')

    rows_updated = cursor.rowcount
    conn.commit()

    print(f"  Updated {rows_updated:,} rows with POP analysis flags")

    # Step 3: Generate analysis report
    print("\nStep 3: Generating POP Analysis Report...")
    print("="*80 + "\n")

    # Overall breakdown by category
    cursor.execute('''
        SELECT
            pop_analysis_category,
            COUNT(*) as contracts,
            SUM(federal_action_obligation) as total_value
        FROM usaspending_china_374_v2
        GROUP BY pop_analysis_category
        ORDER BY total_value DESC
    ''')

    print("PLACE OF PERFORMANCE ANALYSIS:")
    print("-" * 80)
    for category, count, value in cursor.fetchall():
        print(f"{category:40s}: {count:6,} contracts, ${value:>15,.0f}")

    # Breakdown by origin
    print("\n\nBY ENTITY ORIGIN:")
    print("-" * 80)

    for origin in ['CN', 'TW', 'HK', 'MO', 'UNKNOWN']:
        cursor.execute('''
            SELECT
                pop_analysis_category,
                COUNT(*) as contracts,
                SUM(federal_action_obligation) as total_value
            FROM usaspending_china_374_v2
            WHERE entity_country_of_origin = ?
            GROUP BY pop_analysis_category
            ORDER BY total_value DESC
        ''', (origin,))

        results = cursor.fetchall()
        if results:
            print(f"\n{origin} Entities:")
            for category, count, value in results:
                print(f"  {category:38s}: {count:6,} contracts, ${value:>15,.0f}")

    # Key findings for PRC
    print("\n\nKEY FINDINGS FOR PRC (CN) ENTITIES:")
    print("-" * 80)

    cursor.execute('''
        SELECT
            pop_analysis_category,
            COUNT(*) as contracts,
            SUM(federal_action_obligation) as total_value,
            ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM usaspending_china_374_v2 WHERE entity_country_of_origin = 'CN'), 2) as pct_contracts,
            ROUND(100.0 * SUM(federal_action_obligation) / (SELECT SUM(federal_action_obligation) FROM usaspending_china_374_v2 WHERE entity_country_of_origin = 'CN'), 2) as pct_value
        FROM usaspending_china_374_v2
        WHERE entity_country_of_origin = 'CN'
        GROUP BY pop_analysis_category
        ORDER BY total_value DESC
    ''')

    for category, count, value, pct_contracts, pct_value in cursor.fetchall():
        print(f"\n{category}:")
        print(f"  Contracts: {count:,} ({pct_contracts}%)")
        print(f"  Value: ${value:,.0f} ({pct_value}%)")

    # Sample high-value entities in each category
    print("\n\nSAMPLE HIGH-VALUE ENTITIES BY CATEGORY:")
    print("-" * 80)

    categories = [
        'VERIFIED_POP_MATCH',
        'ENTITY_FROM_ORIGIN_WORK_IN_USA',
        'ENTITY_FROM_ORIGIN_WORK_ELSEWHERE'
    ]

    for category in categories:
        cursor.execute('''
            SELECT
                recipient_name,
                entity_country_of_origin,
                pop_country,
                SUM(federal_action_obligation) as total_value,
                COUNT(*) as contracts
            FROM usaspending_china_374_v2
            WHERE pop_analysis_category = ?
            GROUP BY recipient_name
            ORDER BY total_value DESC
            LIMIT 3
        ''', (category,))

        results = cursor.fetchall()
        if results:
            print(f"\n{category}:")
            for name, origin, pop, value, contracts in results:
                print(f"  {name[:45]:45s} ({origin}, POP:{pop:10s}): ${value:>12,.0f} ({contracts} contracts)")

    # Save report to file
    report_path = Path("analysis/USASPENDING_POP_ANALYSIS_REPORT.md")
    report_path.parent.mkdir(exist_ok=True)

    with open(report_path, 'w') as f:
        f.write("# USAspending Place of Performance (POP) Analysis Report\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")

        f.write("## Executive Summary\n\n")
        f.write("This report addresses a critical data quality issue in USAspending data:\n\n")
        f.write("**Finding:** The `recipient_country_code` field in USAspending often reflects where contract work is performed (Place of Performance), not where the company is legally based.\n\n")
        f.write("**Impact:** This causes significant false positives when trying to identify contracts with Chinese entities.\n\n")
        f.write("**Solution:** We've added POP analysis flags to help users filter based on their specific needs.\n\n")
        f.write("---\n\n")

        f.write("## Categories Explained\n\n")
        f.write("**1. VERIFIED_POP_MATCH**\n")
        f.write("   - Recipient country code matches place of performance\n")
        f.write("   - Example: Chinese entity (CHN) with work in China (CHN)\n")
        f.write("   - **Highest confidence** these are actual entities from origin country\n\n")

        f.write("**2. ENTITY_FROM_ORIGIN_WORK_IN_USA**\n")
        f.write("   - Recipient coded as from origin country, work performed in USA\n")
        f.write("   - **Likely false positives** due to USAspending data quality issues\n")
        f.write("   - Example: ZACHRY CADDELL JV (coded CHN but work in USA)\n\n")

        f.write("**3. ENTITY_FROM_ORIGIN_WORK_ELSEWHERE**\n")
        f.write("   - Recipient from origin country, work in third country\n")
        f.write("   - Example: Chinese entity doing work in Switzerland\n")
        f.write("   - **Mixed confidence** - could be legitimate global operations\n\n")

        f.write("**4. POP_UNKNOWN**\n")
        f.write("   - Place of performance not specified in contract data\n")
        f.write("   - Requires manual review\n\n")

        f.write("---\n\n")
        f.write("## Recommendations for Analysis\n\n")
        f.write("**For identifying actual Chinese entities:**\n")
        f.write("```sql\n")
        f.write("SELECT * FROM usaspending_china_374_v2\n")
        f.write("WHERE pop_analysis_category = 'VERIFIED_POP_MATCH'\n")
        f.write("```\n\n")

        f.write("**For identifying Chinese entities operating in USA:**\n")
        f.write("```sql\n")
        f.write("SELECT * FROM usaspending_china_374_v2\n")
        f.write("WHERE pop_analysis_category IN ('VERIFIED_POP_MATCH', 'ENTITY_FROM_ORIGIN_WORK_ELSEWHERE')\n")
        f.write("-- Excludes likely false positives from work-in-USA coding\n")
        f.write("```\n\n")

        f.write("**For conservative analysis (highest confidence only):**\n")
        f.write("```sql\n")
        f.write("SELECT * FROM usaspending_china_374_v2\n")
        f.write("WHERE pop_matches_origin = 1\n")
        f.write("```\n\n")

    print(f"\n\nReport saved to: {report_path}")

    conn.close()

    print("\n" + "="*80)
    print("POP ANALYSIS FLAGS ADDED SUCCESSFULLY")
    print("="*80)
    print("\nNew columns added to usaspending_china_374_v2:")
    print("  - pop_matches_origin (0/1 flag)")
    print("  - pop_analysis_category (classification)")
    print("\nUsers can now filter based on their specific needs!")

if __name__ == "__main__":
    try:
        add_pop_flags()
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

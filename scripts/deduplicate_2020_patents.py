#!/usr/bin/env python3
"""
Deduplicate 2020 Patents Between USPTO and PatentsView Datasets
Analyze overlap and create deduplication strategy
"""

import sqlite3
import json
from datetime import datetime

DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"

def main():
    print("="*80)
    print("2020 PATENT DEDUPLICATION ANALYSIS")
    print("="*80)
    print(f"Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Step 1: Get 2020 patents from USPTO dataset
    print("\n1. Analyzing USPTO 2011-2020 dataset...")
    cursor.execute("""
        SELECT COUNT(*) FROM uspto_patents_chinese
        WHERE year = 2020
    """)
    uspto_2020_count = cursor.fetchone()[0]
    print(f"   USPTO 2020 patents: {uspto_2020_count:,}")

    # Get USPTO 2020 patent IDs
    cursor.execute("""
        SELECT DISTINCT patent_number FROM uspto_patents_chinese
        WHERE year = 2020
    """)
    uspto_2020_ids = set(row[0] for row in cursor.fetchall())

    # Step 2: Get 2020 patents from PatentsView dataset
    print("\n2. Analyzing PatentsView 2020-2025 dataset...")
    cursor.execute("""
        SELECT COUNT(*) FROM patentsview_patents_chinese
        WHERE filing_year = 2020
    """)
    pv_2020_count = cursor.fetchone()[0]
    print(f"   PatentsView 2020 patents: {pv_2020_count:,}")

    # Get PatentsView 2020 patent IDs
    cursor.execute("""
        SELECT DISTINCT patent_id FROM patentsview_patents_chinese
        WHERE filing_year = 2020
    """)
    pv_2020_ids = set(row[0] for row in cursor.fetchall())

    # Step 3: Analyze overlap
    print("\n3. Analyzing overlap...")
    overlap_ids = uspto_2020_ids.intersection(pv_2020_ids)
    uspto_only = uspto_2020_ids - pv_2020_ids
    pv_only = pv_2020_ids - uspto_2020_ids

    print(f"   Overlap (in both datasets): {len(overlap_ids):,} patents")
    print(f"   USPTO only: {len(uspto_only):,} patents")
    print(f"   PatentsView only: {len(pv_only):,} patents")

    overlap_pct_uspto = (len(overlap_ids) / len(uspto_2020_ids) * 100) if uspto_2020_ids else 0
    overlap_pct_pv = (len(overlap_ids) / len(pv_2020_ids) * 100) if pv_2020_ids else 0

    print(f"\n   Overlap as % of USPTO 2020: {overlap_pct_uspto:.1f}%")
    print(f"   Overlap as % of PatentsView 2020: {overlap_pct_pv:.1f}%")

    # Step 4: Compare data quality for overlapping patents
    print("\n4. Comparing data quality for overlapping patents...")

    # Sample 100 overlapping patents
    sample_overlap = list(overlap_ids)[:100]

    uspto_has_title = 0
    uspto_has_assignee = 0
    pv_has_org = 0
    pv_has_location = 0

    for patent_id in sample_overlap:
        # Check USPTO data
        cursor.execute("""
            SELECT title, assignee_name
            FROM uspto_patents_chinese
            WHERE patent_number = ?
        """, (patent_id,))
        uspto_row = cursor.fetchone()
        if uspto_row:
            if uspto_row[0]:
                uspto_has_title += 1
            if uspto_row[1]:
                uspto_has_assignee += 1

        # Check PatentsView data
        cursor.execute("""
            SELECT assignee_organization, assignee_city
            FROM patentsview_patents_chinese
            WHERE patent_id = ?
        """, (patent_id,))
        pv_row = cursor.fetchone()
        if pv_row:
            if pv_row[0]:
                pv_has_org += 1
            if pv_row[1]:
                pv_has_location += 1

    print(f"\n   Sample size: {len(sample_overlap)} patents")
    print(f"   USPTO has title: {uspto_has_title}/{len(sample_overlap)} ({uspto_has_title/len(sample_overlap)*100:.1f}%)")
    print(f"   USPTO has assignee: {uspto_has_assignee}/{len(sample_overlap)} ({uspto_has_assignee/len(sample_overlap)*100:.1f}%)")
    print(f"   PatentsView has organization: {pv_has_org}/{len(sample_overlap)} ({pv_has_org/len(sample_overlap)*100:.1f}%)")
    print(f"   PatentsView has location: {pv_has_location}/{len(sample_overlap)} ({pv_has_location/len(sample_overlap)*100:.1f}%)")

    # Step 5: Deduplication recommendation
    print(f"\n{'='*80}")
    print("DEDUPLICATION RECOMMENDATION")
    print(f"{'='*80}")

    print("\nStrategy: Use PatentsView data for 2020 overlap")
    print("Rationale:")
    print("  1. PatentsView has disambiguated entities (better assignee resolution)")
    print("  2. PatentsView has standardized location data")
    print("  3. PatentsView CPC data already processed with strategic classifications")
    print("  4. Maintains consistency with 2021-2025 data from PatentsView")

    print(f"\nProposed combined dataset for 2011-2025:")
    print(f"  - USPTO 2011-2019: Use all USPTO data")
    print(f"  - 2020 overlap: Use PatentsView data (drop USPTO 2020 duplicates)")
    print(f"  - USPTO 2020 only: Keep USPTO unique 2020 patents")
    print(f"  - PatentsView 2021-2025: Use all PatentsView data")

    # Calculate totals
    uspto_2011_2019 = 0
    for year in range(2011, 2020):
        cursor.execute("""
            SELECT COUNT(*) FROM uspto_patents_chinese
            WHERE year = ?
        """, (year,))
        uspto_2011_2019 += cursor.fetchone()[0]

    pv_2021_2025 = 0
    for year in range(2021, 2026):
        cursor.execute("""
            SELECT COUNT(*) FROM patentsview_patents_chinese
            WHERE filing_year = ?
        """, (year,))
        pv_2021_2025 += cursor.fetchone()[0]

    total_combined = uspto_2011_2019 + len(pv_2020_ids) + len(uspto_only) + pv_2021_2025

    print(f"\nProjected totals:")
    print(f"  USPTO 2011-2019: {uspto_2011_2019:,}")
    print(f"  2020 (PatentsView): {len(pv_2020_ids):,}")
    print(f"  2020 (USPTO only): {len(uspto_only):,}")
    print(f"  PatentsView 2021-2025: {pv_2021_2025:,}")
    print(f"  TOTAL: {total_combined:,} unique patents")

    # Save analysis
    analysis = {
        "generated_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "uspto_2020_count": len(uspto_2020_ids),
        "patentsview_2020_count": len(pv_2020_ids),
        "overlap_count": len(overlap_ids),
        "uspto_only_count": len(uspto_only),
        "pv_only_count": len(pv_only),
        "overlap_pct_uspto": round(overlap_pct_uspto, 2),
        "overlap_pct_pv": round(overlap_pct_pv, 2),
        "deduplication_strategy": "Use PatentsView for overlap, USPTO for unique 2020 patents",
        "projected_combined_total": total_combined
    }

    with open("C:/Projects/OSINT - Foresight/analysis/2020_DEDUPLICATION_ANALYSIS.json", 'w') as f:
        json.dump(analysis, f, indent=2)

    print(f"\nAnalysis saved to: C:/Projects/OSINT - Foresight/analysis/2020_DEDUPLICATION_ANALYSIS.json")

    conn.close()

    print(f"\n{'='*80}")
    print("ANALYSIS COMPLETE")
    print(f"{'='*80}")
    print(f"End: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == '__main__':
    main()

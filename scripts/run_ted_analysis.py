#!/usr/bin/env python3
"""
Run TED analysis for OSINT learning project
Processes multiple months of data and generates strategic reports
"""

import os
import logging
from pathlib import Path
from ted_fixed_extractor import TEDFixedExtractor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Run comprehensive TED analysis"""

    # Use existing database with some data
    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"

    logger.info(f"Using database: {db_path}")
    extractor = TEDFixedExtractor(db_path)

    # Process available TED data
    years_months = [
        # Recent data
        (2024, 1),   # January 2024
        (2023, 12),  # December 2023
        (2023, 11),  # November 2023
        (2023, 10),  # October 2023
        (2023, 9),   # September 2023
        (2023, 8),   # August 2023
        (2023, 7),   # July 2023
        (2023, 6),   # June 2023
        (2023, 5),   # May 2023
        (2023, 4),   # April 2023
        (2023, 3),   # March 2023
        (2023, 2),   # February 2023
        (2023, 1),   # January 2023
        # Older data for trend analysis
        (2022, 12),  # December 2022
        (2022, 6),   # June 2022
        (2022, 1),   # January 2022
        (2021, 12),  # December 2021
        (2021, 6),   # June 2021
    ]

    processed = 0
    for year, month in years_months:
        tar_path = f"F:/TED_Data/monthly/{year}/TED_monthly_{year}_{month:02d}.tar.gz"
        if os.path.exists(tar_path):
            logger.info(f"Processing {tar_path}")
            try:
                extractor.process_tar_file(tar_path)
                processed += 1
                logger.info(f"Completed processing {tar_path}")

                # Show progress
                if processed % 3 == 0:
                    extractor.log_progress()

            except Exception as e:
                logger.error(f"Error processing {tar_path}: {e}")
        else:
            logger.warning(f"File not found: {tar_path}")

    # Final progress log
    logger.info("\n" + "="*60)
    logger.info("PROCESSING COMPLETE")
    logger.info("="*60)
    extractor.log_progress()

    # Generate strategic dependency analysis
    logger.info("\nGenerating strategic dependency map...")
    report = extractor.generate_strategic_dependency_map()

    # Additional analysis
    import sqlite3
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    print("\n" + "="*60)
    print("ADDITIONAL OSINT ANALYSIS")
    print("="*60)

    # Temporal trends
    print("\nTemporal Analysis:")
    cur.execute("""
        SELECT substr(publication_date, 1, 4) as year,
               COUNT(*) as total,
               SUM(CASE WHEN has_chinese_involvement = 1 THEN 1 ELSE 0 END) as chinese
        FROM ted_osint_analysis
        WHERE publication_date IS NOT NULL
        GROUP BY year
        ORDER BY year DESC
    """)

    for year, total, chinese in cur.fetchall():
        if total > 0:
            print(f"  {year}: {total} contracts, {chinese} Chinese ({chinese/total*100:.1f}%)")

    # Technology indicators
    print("\nTechnology/Product Indicators:")
    cur.execute("""
        SELECT chinese_evidence, COUNT(*) as count
        FROM ted_osint_analysis
        WHERE has_chinese_involvement = 1
          AND chinese_type = 'Chinese product/technology'
        GROUP BY chinese_evidence
        ORDER BY count DESC
        LIMIT 10
    """)

    for evidence, count in cur.fetchall():
        print(f"  {evidence}: {count}")

    # Critical insights
    print("\n" + "="*60)
    print("KEY INSIGHTS FOR OSINT ANALYSIS")
    print("="*60)

    cur.execute("SELECT COUNT(*) FROM ted_osint_analysis")
    total_analyzed = cur.fetchone()[0]

    cur.execute("SELECT COUNT(DISTINCT contractor_name) FROM ted_osint_analysis WHERE contractor_name IS NOT NULL")
    unique_contractors = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*) FROM ted_osint_analysis
        WHERE has_chinese_involvement = 1 AND confidence_score >= 0.8
    """)
    high_confidence = cur.fetchone()[0]

    print(f"\n1. Data Coverage:")
    print(f"   - Total contracts analyzed: {total_analyzed:,}")
    print(f"   - Unique contractors found: {unique_contractors:,}")
    print(f"   - Contractor extraction rate: {unique_contractors/max(1,total_analyzed)*100:.1f}%")

    print(f"\n2. Chinese Involvement:")
    print(f"   - High-confidence detections: {high_confidence}")
    print(f"   - Detection rate: {high_confidence/max(1,total_analyzed)*100:.2f}%")

    print(f"\n3. Data Quality Issues:")
    print(f"   - Missing contractor names: {total_analyzed - unique_contractors:,} records")
    print(f"   - This indicates incomplete XML extraction")

    conn.close()

    print("\n" + "="*60)
    print("Analysis complete. Report saved to:")
    print("C:/Projects/OSINT - Foresight/analysis/strategic_dependencies.json")
    print("="*60)

    return extractor.stats

if __name__ == "__main__":
    stats = main()
    print(f"\nFinal Statistics: {stats}")
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
Analyze USPTO CPC Strategic Technologies for Chinese Patents
BATCHED APPROACH - Process CPC records in chunks to avoid timeouts
"""

import sqlite3
import json
from datetime import datetime
from collections import defaultdict, Counter

DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"
OUTPUT_DIR = "C:/Projects/OSINT - Foresight/analysis"
CHECKPOINT_FILE = f"{OUTPUT_DIR}/cpc_strategic_checkpoint.json"
BATCH_SIZE = 100000  # Process 100K CPC records at a time

def load_checkpoint():
    """Load checkpoint from previous run if exists"""
    try:
        with open(CHECKPOINT_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            'last_rowid': 0,
            'strategic_tech_counts': {},
            'strategic_tech_patents': {},
            'chinese_strategic_count': 0,
            'total_processed': 0
        }

def save_checkpoint(checkpoint):
    """Save checkpoint for resumption"""
    # Convert sets to lists for JSON serialization
    checkpoint_copy = checkpoint.copy()
    checkpoint_copy['strategic_tech_patents'] = {
        tech: list(patents) for tech, patents in checkpoint['strategic_tech_patents'].items()
    }
    with open(CHECKPOINT_FILE, 'w') as f:
        json.dump(checkpoint_copy, f, indent=2)

def main():
    print("="*80)
    print("USPTO CPC STRATEGIC TECHNOLOGIES ANALYSIS - CHINESE PATENTS (BATCHED)")
    print("="*80)

    conn = sqlite3.connect(DB_PATH, timeout=300)
    cursor = conn.cursor()

    # Step 1: Get all Chinese patent application numbers
    print("\n1. Loading Chinese patent application numbers...")
    cursor.execute("""
        SELECT DISTINCT application_number
        FROM uspto_patents_chinese
        WHERE application_number IS NOT NULL
    """)
    chinese_app_numbers = set(row[0] for row in cursor.fetchall())
    print(f"   Found {len(chinese_app_numbers):,} unique Chinese patent application numbers")

    # Step 2: Load checkpoint if exists
    checkpoint = load_checkpoint()
    strategic_tech_counts = Counter(checkpoint['strategic_tech_counts'])
    strategic_tech_patents = defaultdict(set)
    for tech, patents in checkpoint.get('strategic_tech_patents', {}).items():
        strategic_tech_patents[tech] = set(patents)

    chinese_strategic_count = checkpoint['chinese_strategic_count']
    last_rowid = checkpoint['last_rowid']
    total_processed = checkpoint['total_processed']

    if last_rowid > 0:
        print(f"\n   Resuming from checkpoint (last ROWID: {last_rowid:,})")
        print(f"   Already processed: {total_processed:,} records")
        print(f"   Chinese matches so far: {chinese_strategic_count:,}")

    # Step 3: Process CPC classifications in batches
    print("\n2. Processing strategic CPC classifications in batches...")

    while True:
        # Fetch next batch
        # SECURITY: Use parameterized query to prevent SQL injection
        cursor.execute("""
            SELECT ROWID, application_number, technology_area, cpc_full
            FROM uspto_cpc_classifications
            WHERE is_strategic = 1
                AND application_number IS NOT NULL
                AND ROWID > ?
            ORDER BY ROWID
            LIMIT ?
        """, (last_rowid, BATCH_SIZE))

        batch = cursor.fetchall()

        if not batch:
            print(f"\n   No more records to process")
            break

        # Process this batch
        batch_chinese_count = 0
        for rowid, app_num, tech_area, cpc_full in batch:
            total_processed += 1
            last_rowid = rowid

            if app_num in chinese_app_numbers:
                strategic_tech_counts[tech_area] += 1
                strategic_tech_patents[tech_area].add(app_num)
                chinese_strategic_count += 1
                batch_chinese_count += 1

        print(f"   Processed batch ending at ROWID {last_rowid:,} | "
              f"Total: {total_processed:,} | Chinese matches: {chinese_strategic_count:,} "
              f"(+{batch_chinese_count} this batch)")

        # Save checkpoint every batch
        checkpoint = {
            'last_rowid': last_rowid,
            'strategic_tech_counts': dict(strategic_tech_counts),
            'strategic_tech_patents': strategic_tech_patents,
            'chinese_strategic_count': chinese_strategic_count,
            'total_processed': total_processed
        }
        save_checkpoint(checkpoint)

    print(f"\n   COMPLETE! Total strategic classifications processed: {total_processed:,}")
    print(f"   Chinese patent strategic matches: {chinese_strategic_count:,}")

    # Step 4: Generate report
    print("\n3. Generating strategic technology report...")

    report = {
        'generated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total_chinese_patents': len(chinese_app_numbers),
        'strategic_classifications_found': chinese_strategic_count,
        'total_cpc_records_processed': total_processed,
        'technologies': {}
    }

    # Sort by patent count
    sorted_techs = sorted(strategic_tech_counts.items(), key=lambda x: x[1], reverse=True)

    print("\n" + "="*80)
    print("STRATEGIC TECHNOLOGY AREAS - CHINESE PATENTS")
    print("="*80)
    print(f"\n{'Technology Area':<40} {'Patents':<10} {'% of Chinese':<12}")
    print("-"*80)

    for tech_area, count in sorted_techs[:25]:
        unique_patents = len(strategic_tech_patents[tech_area])
        pct = (unique_patents / len(chinese_app_numbers)) * 100
        print(f"{tech_area:<40} {unique_patents:<10,} {pct:<12.2f}%")

        report['technologies'][tech_area] = {
            'patent_count': unique_patents,
            'percentage': round(pct, 2)
        }

    # Save report
    output_file = f"{OUTPUT_DIR}/USPTO_CPC_STRATEGIC_TECHNOLOGIES_CHINESE.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print("\n" + "="*80)
    print(f"REPORT SAVED: {output_file}")
    print("="*80)

    # Step 5: Generate summary statistics
    print("\n4. Summary Statistics:")
    print(f"   Total Chinese patents: {len(chinese_app_numbers):,}")

    all_strategic_patents = set()
    for patents in strategic_tech_patents.values():
        all_strategic_patents.update(patents)

    print(f"   Patents with strategic tech: {len(all_strategic_patents):,}")
    pct_strategic = (len(all_strategic_patents) / len(chinese_app_numbers)) * 100
    print(f"   Percentage with strategic tech: {pct_strategic:.1f}%")

    print("\n   Top 15 Strategic Technology Areas:")
    for i, (tech_area, count) in enumerate(sorted_techs[:15], 1):
        unique_patents = len(strategic_tech_patents[tech_area])
        print(f"   {i:2d}. {tech_area:<35s}: {unique_patents:>6,} patents")

    # Clean up checkpoint file
    import os
    if os.path.exists(CHECKPOINT_FILE):
        os.remove(CHECKPOINT_FILE)
        print(f"\n   Checkpoint file removed")

    conn.close()
    print("\nAnalysis complete!")

if __name__ == '__main__':
    main()

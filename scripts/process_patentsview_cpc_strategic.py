#!/usr/bin/env python3
"""
Process PatentsView CPC Classifications for Chinese Patents (2020-2025)
Apply strategic technology categorization to g_cpc_current.tsv
"""

import csv
import sqlite3
import json
from datetime import datetime
from collections import Counter, defaultdict

# Paths
PATENTSVIEW_DIR = "F:/USPTO_PATENTSVIEW"
DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"
OUTPUT_FILE = "C:/Projects/OSINT - Foresight/analysis/PATENTSVIEW_CPC_STRATEGIC_TECHNOLOGIES.json"

# Strategic technology areas (same as 2011-2020 analysis)
STRATEGIC_CPC_CLASSES = {
    'H01L': 'Semiconductor Devices',
    'H01S': 'Lasers',
    'G02B': 'Optical Elements',
    'G06N': 'AI/Neural Networks',
    'G06F': 'Computing',
    'H04W': 'Wireless Communications',
    'H04B': 'Transmission',
    'G01S': 'Radar/Navigation',
    'B64': 'Aircraft/Spacecraft',
    'F41': 'Weapons',
    'F42': 'Ammunition/Blasting',
    'G21': 'Nuclear Physics',
    'C06': 'Explosives',
    'G08': 'Signalling/Control',
    'H01Q': 'Antennas',
    'B82': 'Nanotechnology',
    'G06T': 'Image Processing',
    'G05D': 'Autonomous Control',
    'H01M': 'Batteries/Fuel Cells',
    'C30B': 'Crystal Growth',
    'G06K': 'Biometrics/Recognition',
    'G02F': 'Optical Devices'
}

def read_tsv(filepath):
    """Read TSV file with progress"""
    print(f"Reading: {filepath}")
    count = 0
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        reader = csv.DictReader(f, delimiter='\t', quoting=csv.QUOTE_ALL)
        for row in reader:
            yield row
            count += 1
            if count % 1000000 == 0:
                print(f"  Read {count:,} rows...")

def get_strategic_category(cpc_class):
    """Map CPC class to strategic category"""
    # Direct match
    if cpc_class in STRATEGIC_CPC_CLASSES:
        return STRATEGIC_CPC_CLASSES[cpc_class]

    # Check if CPC class starts with strategic pattern (e.g., "B64D" matches "B64")
    for strategic_class, category in STRATEGIC_CPC_CLASSES.items():
        if cpc_class.startswith(strategic_class):
            return category

    return None

def create_tables(conn):
    """Create CPC classification table for PatentsView"""
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patentsview_cpc_strategic (
            patent_id TEXT,
            cpc_sequence INTEGER,
            cpc_section TEXT,
            cpc_class TEXT,
            cpc_subclass TEXT,
            cpc_group TEXT,
            cpc_full TEXT,
            cpc_type TEXT,
            strategic_category TEXT,
            is_strategic INTEGER,
            PRIMARY KEY (patent_id, cpc_sequence)
        )
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_pv_cpc_patent
        ON patentsview_cpc_strategic(patent_id)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_pv_cpc_strategic
        ON patentsview_cpc_strategic(is_strategic)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_pv_cpc_category
        ON patentsview_cpc_strategic(strategic_category)
    """)

    conn.commit()
    print("Tables created")

def main():
    print("="*80)
    print("PATENTSVIEW CPC STRATEGIC TECHNOLOGY PROCESSOR (2020-2025)")
    print("="*80)
    print(f"Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    conn = sqlite3.connect(DB_PATH, timeout=300)
    create_tables(conn)
    cursor = conn.cursor()

    # Step 1: Get Chinese patent IDs from 2020-2025
    print("\n1. Loading Chinese patent IDs (2020-2025)...")
    cursor.execute("""
        SELECT DISTINCT patent_id
        FROM patentsview_patents_chinese
        WHERE filing_year >= 2020 AND filing_year <= 2025
    """)
    chinese_patents = set(row[0] for row in cursor.fetchall())
    print(f"   Found {len(chinese_patents):,} Chinese patents")

    # Step 2: Process CPC classifications
    print("\n2. Processing CPC classifications...")

    strategic_counts = Counter()
    strategic_patents = defaultdict(set)
    total_cpc_records = 0
    chinese_cpc_count = 0
    strategic_cpc_count = 0

    batch = []
    batch_size = 10000

    for row in read_tsv(f"{PATENTSVIEW_DIR}/g_cpc_current.tsv"):
        total_cpc_records += 1

        patent_id = row.get('patent_id', '').strip()

        # Only process Chinese patents
        if patent_id not in chinese_patents:
            continue

        chinese_cpc_count += 1

        cpc_sequence = row.get('cpc_sequence', '')
        cpc_section = row.get('cpc_section', '').strip()
        cpc_class = row.get('cpc_class', '').strip()
        cpc_subclass = row.get('cpc_subclass', '').strip()
        cpc_group = row.get('cpc_group', '').strip()
        cpc_type = row.get('cpc_type', '').strip()

        # Determine if strategic (use cpc_subclass for detailed matching)
        strategic_category = get_strategic_category(cpc_subclass)
        is_strategic = 1 if strategic_category else 0

        if is_strategic:
            strategic_cpc_count += 1
            strategic_counts[strategic_category] += 1
            strategic_patents[strategic_category].add(patent_id)

        batch.append((
            patent_id,
            cpc_sequence,
            cpc_section,
            cpc_class,
            cpc_subclass,
            cpc_group,
            cpc_group,  # cpc_full = cpc_group for PatentsView
            cpc_type,
            strategic_category,
            is_strategic
        ))

        if len(batch) >= batch_size:
            cursor.executemany("""
                INSERT OR REPLACE INTO patentsview_cpc_strategic
                (patent_id, cpc_sequence, cpc_section, cpc_class, cpc_subclass,
                 cpc_group, cpc_full, cpc_type, strategic_category, is_strategic)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, batch)
            conn.commit()
            batch = []

            if chinese_cpc_count % 50000 == 0:
                print(f"   Processed {chinese_cpc_count:,} Chinese CPC records | Strategic: {strategic_cpc_count:,}")

    # Final batch
    if batch:
        cursor.executemany("""
            INSERT OR REPLACE INTO patentsview_cpc_strategic
            (patent_id, cpc_sequence, cpc_section, cpc_class, cpc_subclass,
             cpc_group, cpc_full, cpc_type, strategic_category, is_strategic)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, batch)
        conn.commit()

    # Step 3: Generate summary statistics
    print("\n3. Generating summary statistics...")

    # Technology distribution
    tech_summary = {}
    total_strategic_patents = len(chinese_patents)

    for category in sorted(strategic_counts.keys()):
        count = len(strategic_patents[category])
        pct = (count / total_strategic_patents * 100) if total_strategic_patents > 0 else 0
        tech_summary[category] = {
            "patent_count": count,
            "percentage": round(pct, 2)
        }

    # Create summary report
    report = {
        "generated_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "period": "2020-2025",
        "total_chinese_patents": len(chinese_patents),
        "total_cpc_records_processed": total_cpc_records,
        "chinese_cpc_records": chinese_cpc_count,
        "strategic_cpc_records": strategic_cpc_count,
        "technologies": tech_summary
    }

    # Save JSON report
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n{'='*80}")
    print("RESULTS")
    print(f"{'='*80}")
    print(f"Total CPC records processed: {total_cpc_records:,}")
    print(f"Chinese CPC records: {chinese_cpc_count:,}")
    print(f"Strategic CPC records: {strategic_cpc_count:,}")
    print(f"\nTop Strategic Technologies (2020-2025):")

    top_techs = sorted(tech_summary.items(), key=lambda x: x[1]['patent_count'], reverse=True)[:10]
    for tech, data in top_techs:
        print(f"  {tech:30s}: {data['patent_count']:>6,} patents ({data['percentage']:>5.1f}%)")

    print(f"\nReport saved to: {OUTPUT_FILE}")

    conn.close()

    print(f"\n{'='*80}")
    print("PROCESSING COMPLETE")
    print(f"{'='*80}")
    print(f"End: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == '__main__':
    main()

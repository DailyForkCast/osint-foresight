#!/usr/bin/env python3
"""
Generate 300-record multi-source validation sample for precision improvement
Identifies new false positive patterns across USAspending, TED, USPTO, OpenAlex

Purpose: Part of precision improvement roadmap to increase detection from 73% → 97%+
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

DB_PATH = Path("F:/OSINT_WAREHOUSE/osint_master.db")
OUTPUT_FILE = Path("C:/Projects/OSINT-Foresight/analysis/manual_review/precision_validation_300_records.json")
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

def generate_sample():
    """Generate stratified sample of 300 records for false positive pattern identification"""

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    samples = []

    print("=" * 80)
    print("PRECISION VALIDATION SAMPLE GENERATOR")
    print("=" * 80)
    print("Target: 300 records across 4 data sources")
    print("Purpose: Identify new false positive patterns")
    print("=" * 80)

    # Sample 1: USAspending awards (120 records)
    # Focus on recent awards with Chinese entity detections
    print("\n1. Sampling USAspending awards (120 records)...")
    cursor.execute("""
        SELECT
            'usaspending' as source,
            transaction_id,
            recipient_name,
            recipient_country,
            pop_country,
            detection_details,
            award_description,
            total_dollars_obligated,
            action_date
        FROM usaspending_china_comprehensive
        WHERE detection_count > 0
        AND action_date >= '2020-01-01'
        ORDER BY RANDOM()
        LIMIT 120
    """)

    for row in cursor.fetchall():
        samples.append({
            'source': 'usaspending',
            'record_id': row['transaction_id'],
            'entity_name': row['recipient_name'],
            'address': None,
            'city': None,
            'state': None,
            'country': row['recipient_country'],
            'detected_entity': row['detection_details'],
            'description': row['award_description'][:200] if row['award_description'] else None,
            'amount_usd': float(row['total_dollars_obligated']) if row['total_dollars_obligated'] else None,
            'date': row['action_date'],
            'review_status': 'pending',
            'is_true_positive': None,
            'false_positive_pattern': '',
            'notes': ''
        })

    print(f"   [OK] Collected {len([s for s in samples if s['source'] == 'usaspending'])} USAspending records")

    # Sample 2: TED contracts (80 records)
    print("\n2. Sampling TED contracts (80 records)...")
    cursor.execute("""
        SELECT
            'ted' as source,
            document_id,
            contractor_name,
            contractor_info,
            contractor_country,
            chinese_company_match,
            contract_title,
            publication_date
        FROM ted_contracts_production
        WHERE is_chinese_related = 1
        AND chinese_company_match IS NOT NULL
        ORDER BY RANDOM()
        LIMIT 80
    """)

    for row in cursor.fetchall():
        samples.append({
            'source': 'ted',
            'record_id': row['document_id'],
            'entity_name': row['contractor_name'],
            'address': row['contractor_info'],
            'city': None,
            'state': None,
            'country': row['contractor_country'],
            'detected_entity': row['chinese_company_match'],
            'description': row['contract_title'][:200] if row['contract_title'] else None,
            'amount_usd': None,
            'date': row['publication_date'],
            'review_status': 'pending',
            'is_true_positive': None,
            'false_positive_pattern': '',
            'notes': ''
        })

    print(f"   [OK] Collected {len([s for s in samples if s['source'] == 'ted'])} TED records")

    # Sample 3: USPTO patents (60 records)
    print("\n3. Sampling USPTO patents (60 records)...")
    cursor.execute("""
        SELECT
            'uspto' as source,
            patent_number,
            assignee_name,
            assignee_city,
            assignee_country,
            assignee_name as detected_entity,
            title,
            grant_date
        FROM uspto_patents_chinese
        WHERE grant_date >= '2020-01-01'
        ORDER BY RANDOM()
        LIMIT 60
    """)

    for row in cursor.fetchall():
        samples.append({
            'source': 'uspto',
            'record_id': row['patent_number'],
            'entity_name': row['assignee_name'],
            'address': None,
            'city': row['assignee_city'],
            'state': None,
            'country': row['assignee_country'],
            'detected_entity': row['detected_entity'],
            'description': row['title'][:200] if row['title'] else None,
            'amount_usd': None,
            'date': row['grant_date'],
            'review_status': 'pending',
            'is_true_positive': None,
            'false_positive_pattern': '',
            'notes': ''
        })

    print(f"   [OK] Collected {len([s for s in samples if s['source'] == 'uspto'])} USPTO records")

    # Sample 4: OpenAlex collaborations (40 records)
    print("\n4. Sampling OpenAlex collaborations (40 records)...")
    cursor.execute("""
        SELECT
            'openalex' as source,
            id,
            title,
            institutions,
            china_involvement,
            publication_date
        FROM openalex_china_deep
        WHERE china_involvement IS NOT NULL
        AND publication_date >= '2020-01-01'
        ORDER BY RANDOM()
        LIMIT 40
    """)

    for row in cursor.fetchall():
        samples.append({
            'source': 'openalex',
            'record_id': row['id'],
            'entity_name': row['institutions'][:100] if row['institutions'] else None,
            'address': None,
            'city': None,
            'state': None,
            'country': 'CN',
            'detected_entity': row['china_involvement'],
            'description': row['title'][:200] if row['title'] else None,
            'amount_usd': None,
            'date': row['publication_date'],
            'review_status': 'pending',
            'is_true_positive': None,
            'false_positive_pattern': '',
            'notes': ''
        })

    print(f"   [OK] Collected {len([s for s in samples if s['source'] == 'openalex'])} OpenAlex records")

    # Generate report
    report = {
        'generated_date': datetime.now().isoformat(),
        'total_samples': len(samples),
        'samples_by_source': {
            'usaspending': len([s for s in samples if s['source'] == 'usaspending']),
            'ted': len([s for s in samples if s['source'] == 'ted']),
            'uspto': len([s for s in samples if s['source'] == 'uspto']),
            'openalex': len([s for s in samples if s['source'] == 'openalex'])
        },
        'purpose': 'Identify new false positive patterns for precision improvement (73% → 97%)',
        'instructions': {
            'review_process': [
                'For each record, examine entity_name, address, city, country, detected_entity',
                'Determine if detection is TRUE POSITIVE or FALSE POSITIVE',
                'Set is_true_positive to true or false',
                'If FALSE POSITIVE, identify the pattern type in false_positive_pattern field',
                'Add notes explaining the reasoning',
                'Update review_status to "reviewed" when complete'
            ],
            'false_positive_patterns_to_look_for': [
                'substring_match - Entity name contains Chinese characters but is not Chinese',
                'european_company - European company with Chinese-related name',
                'us_company - US company with Chinese-related name',
                'joint_venture - JV/partnership name contains China references',
                'casino_hotel - Hospitality businesses (e.g., casino names with Chinese chars)',
                'historical_region - References to historical regions like Indochina',
                'language_services - Translation/interpretation services',
                'porcelain - China as material (fine china, bone china)',
                'personal_name - Person with Chinese surname, not organization',
                'city_state_error - Detected based on non-China location',
                'other - Describe new pattern in notes'
            ],
            'expected_outcome': 'List of new patterns to add to FALSE_POSITIVES filters'
        },
        'samples': samples
    }

    # Save to JSON
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 80)
    print("PRECISION VALIDATION SAMPLE GENERATED")
    print("=" * 80)
    print(f"Output file: {OUTPUT_FILE}")
    print(f"Total samples: {len(samples)}")
    print(f"  - USAspending: {report['samples_by_source']['usaspending']}")
    print(f"  - TED: {report['samples_by_source']['ted']}")
    print(f"  - USPTO: {report['samples_by_source']['uspto']}")
    print(f"  - OpenAlex: {report['samples_by_source']['openalex']}")
    print("\n" + "=" * 80)
    print("REVIEW INSTRUCTIONS")
    print("=" * 80)
    print("1. Open the JSON file in a text editor or JSON viewer")
    print("2. For each record in 'samples' array:")
    print("   - Review entity_name, address, detected_entity")
    print("   - Set is_true_positive: true/false")
    print("   - If false, set false_positive_pattern (see instructions in file)")
    print("   - Add notes explaining why")
    print("   - Change review_status to 'reviewed'")
    print("3. When complete, run analysis script to:")
    print("   - Calculate precision rate")
    print("   - Extract new patterns for FALSE_POSITIVES")
    print("=" * 80)

    conn.close()

if __name__ == "__main__":
    generate_sample()

#!/usr/bin/env python3
"""
TED Chinese Entity Sync - Data Quality Validation
Created: October 19, 2025
Purpose: Validate the 50,844 newly flagged TED contracts for data quality
"""

import sqlite3
import json
from datetime import datetime
from collections import Counter
import random

DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"

def main():
    print("=" * 80)
    print("TED CHINESE ENTITY SYNC - DATA QUALITY VALIDATION")
    print("=" * 80)
    print()

    conn = sqlite3.connect(DB_PATH, timeout=3600)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    results = {}

    # 1. Overall Statistics
    print("[1/7] Gathering overall statistics...")
    cursor.execute("SELECT COUNT(*) FROM ted_contracts_production WHERE is_chinese_related = 1")
    total_flagged = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT entity_name) FROM ted_procurement_chinese_entities_found")
    unique_entities = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM ted_contracts_production")
    total_contracts = cursor.fetchone()[0]

    results['overall'] = {
        'total_contracts': total_contracts,
        'total_flagged': total_flagged,
        'flagged_percentage': (total_flagged / total_contracts * 100),
        'unique_chinese_entities': unique_entities
    }

    print(f"  Total TED Contracts: {total_contracts:,}")
    print(f"  Total Flagged as Chinese: {total_flagged:,} ({total_flagged/total_contracts*100:.2f}%)")
    print(f"  Unique Chinese Entities: {unique_entities:,}")
    print()

    # 2. Analyze the match distribution
    print("[2/7] Analyzing match distribution by entity...")
    cursor.execute('''
        SELECT
            tpcef.entity_name,
            COUNT(DISTINCT tcp.id) as contract_count,
            MIN(tcp.contract_value_eur) as min_value,
            MAX(tcp.contract_value_eur) as max_value,
            COUNT(DISTINCT tcp.buyer_country) as countries
        FROM ted_contracts_production tcp
        JOIN ted_procurement_chinese_entities_found tpcef
            ON LOWER(tcp.contractor_name) = LOWER(tpcef.entity_name)
        WHERE tcp.is_chinese_related = 1
        GROUP BY tpcef.entity_name
        ORDER BY contract_count DESC
        LIMIT 50
    ''')

    top_matches = []
    for row in cursor.fetchall():
        top_matches.append({
            'entity_name': row['entity_name'],
            'contract_count': row['contract_count'],
            'min_value': row['min_value'],
            'max_value': row['max_value'],
            'countries': row['countries']
        })

    results['top_50_entities'] = top_matches

    print(f"  Top 10 entities by contract count:")
    for i, match in enumerate(top_matches[:10], 1):
        print(f"    {i:2d}. {match['entity_name']:40s} - {match['contract_count']:5,} contracts")
    print()

    # 3. Check for suspicious patterns (very short names, generic terms)
    print("[3/7] Checking for suspicious/generic entity names...")
    cursor.execute('''
        SELECT
            entity_name,
            LENGTH(entity_name) as name_length,
            COUNT(*) as match_count
        FROM ted_procurement_chinese_entities_found
        WHERE LENGTH(entity_name) < 10
        ORDER BY match_count DESC
    ''')

    short_names = []
    for row in cursor.fetchall():
        # Count how many contracts match this short name
        cursor.execute('''
            SELECT COUNT(*)
            FROM ted_contracts_production
            WHERE LOWER(contractor_name) = LOWER(?)
            AND is_chinese_related = 1
        ''', (row['entity_name'],))
        contracts = cursor.fetchone()[0]

        if contracts > 0:
            short_names.append({
                'entity_name': row['entity_name'],
                'name_length': row['name_length'],
                'contracts_matched': contracts
            })

    results['short_names'] = short_names

    if short_names:
        print(f"  Found {len(short_names)} entities with names < 10 characters:")
        for name_info in short_names[:10]:
            print(f"    '{name_info['entity_name']}' (len={name_info['name_length']}) - {name_info['contracts_matched']} contracts")
    else:
        print(f"  No concerning short names found")
    print()

    # 4. Sample random matches for manual inspection
    print("[4/7] Sampling 50 random matches for inspection...")
    cursor.execute('''
        SELECT
            tcp.id,
            tcp.notice_number,
            tcp.contractor_name,
            tcp.buyer_name,
            tcp.buyer_country,
            tcp.contract_value_eur,
            tcp.publication_date,
            tpcef.entity_name as matched_entity,
            tpcef.confidence_score
        FROM ted_contracts_production tcp
        JOIN ted_procurement_chinese_entities_found tpcef
            ON LOWER(tcp.contractor_name) = LOWER(tpcef.entity_name)
        WHERE tcp.is_chinese_related = 1
        ORDER BY RANDOM()
        LIMIT 50
    ''')

    sample_matches = []
    for row in cursor.fetchall():
        sample_matches.append({
            'notice_number': row['notice_number'],
            'contractor_name': row['contractor_name'],
            'matched_entity': row['matched_entity'],
            'buyer_name': row['buyer_name'],
            'buyer_country': row['buyer_country'],
            'contract_value_eur': row['contract_value_eur'],
            'publication_date': row['publication_date'],
            'confidence_score': row['confidence_score'],
            'exact_match': row['contractor_name'].lower() == row['matched_entity'].lower()
        })

    results['random_sample'] = sample_matches

    print(f"  Sample of 10 random matches:")
    for i, match in enumerate(sample_matches[:10], 1):
        exact = "✓" if match['exact_match'] else "✗"
        print(f"    {i:2d}. [{exact}] {match['contractor_name'][:40]:40s} | Buyer: {match['buyer_country']}")
    print()

    # 5. Check geographic distribution
    print("[5/7] Analyzing geographic distribution...")
    cursor.execute('''
        SELECT
            buyer_country,
            COUNT(*) as contract_count,
            COUNT(DISTINCT contractor_name) as unique_contractors
        FROM ted_contracts_production
        WHERE is_chinese_related = 1
        GROUP BY buyer_country
        ORDER BY contract_count DESC
    ''')

    geo_distribution = []
    for row in cursor.fetchall():
        geo_distribution.append({
            'country': row['buyer_country'],
            'contracts': row['contract_count'],
            'unique_contractors': row['unique_contractors']
        })

    results['geographic_distribution'] = geo_distribution

    print(f"  Top 10 buyer countries:")
    for i, geo in enumerate(geo_distribution[:10], 1):
        print(f"    {i:2d}. {geo['country']:5s} - {geo['contracts']:6,} contracts, {geo['unique_contractors']:4,} unique contractors")
    print()

    # 6. Check confidence score distribution
    print("[6/7] Analyzing confidence score distribution...")
    cursor.execute('''
        SELECT
            CASE
                WHEN tpcef.confidence_score >= 90 THEN '90-100 (High)'
                WHEN tpcef.confidence_score >= 70 THEN '70-89 (Medium-High)'
                WHEN tpcef.confidence_score >= 50 THEN '50-69 (Medium)'
                WHEN tpcef.confidence_score >= 30 THEN '30-49 (Low-Medium)'
                ELSE '0-29 (Low)'
            END as confidence_range,
            COUNT(DISTINCT tcp.id) as contract_count
        FROM ted_contracts_production tcp
        JOIN ted_procurement_chinese_entities_found tpcef
            ON LOWER(tcp.contractor_name) = LOWER(tpcef.entity_name)
        WHERE tcp.is_chinese_related = 1
        GROUP BY confidence_range
        ORDER BY MIN(tpcef.confidence_score) DESC
    ''')

    confidence_dist = []
    for row in cursor.fetchall():
        confidence_dist.append({
            'range': row['confidence_range'],
            'contracts': row['contract_count']
        })

    results['confidence_distribution'] = confidence_dist

    print(f"  Confidence score distribution:")
    for dist in confidence_dist:
        pct = (dist['contracts'] / total_flagged * 100) if total_flagged > 0 else 0
        print(f"    {dist['range']:20s} - {dist['contracts']:6,} contracts ({pct:5.1f}%)")
    print()

    # 7. Compare exact matches vs. the original 295
    print("[7/7] Analyzing the original 295 vs. new 50,844...")

    # Check if there's a timestamp or way to identify the original 295
    # For now, we can check if there are any contracts with specific detection indicators

    cursor.execute('''
        SELECT COUNT(*)
        FROM ted_contracts_production
        WHERE is_chinese_related = 1
        AND (
            detection_method IS NOT NULL
            OR detection_confidence IS NOT NULL
        )
    ''')

    original_with_metadata = cursor.fetchone()[0]

    results['original_detection_analysis'] = {
        'contracts_with_detection_metadata': original_with_metadata,
        'total_flagged': total_flagged,
        'likely_new_from_sync': total_flagged - original_with_metadata
    }

    print(f"  Contracts with detection metadata: {original_with_metadata:,}")
    print(f"  Total flagged: {total_flagged:,}")
    print(f"  Estimated new from sync: {total_flagged - original_with_metadata:,}")
    print()

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"analysis/ted_entity_sync_validation_{timestamp}.json"

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("=" * 80)
    print(f"VALIDATION COMPLETE - Results saved to: {output_file}")
    print("=" * 80)
    print()

    # CRITICAL ASSESSMENT
    print("CRITICAL ASSESSMENT:")
    print("=" * 80)

    # Flag potential issues
    issues = []

    if short_names:
        issues.append(f"⚠️  {len(short_names)} entities have suspiciously short names (< 10 chars)")

    if total_flagged > total_contracts * 0.1:
        issues.append(f"⚠️  {total_flagged/total_contracts*100:.1f}% of all contracts flagged (seems high)")

    # Check if top entity has disproportionate matches
    if top_matches and top_matches[0]['contract_count'] > 1000:
        issues.append(f"⚠️  Top entity '{top_matches[0]['entity_name']}' matches {top_matches[0]['contract_count']:,} contracts (potential false positive pattern)")

    if issues:
        print("POTENTIAL ISSUES DETECTED:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("✓ No obvious data quality issues detected")

    print()
    print("RECOMMENDATION:")
    print("  1. Manually review the random sample in the JSON output")
    print("  2. Investigate any entities with unusually high match counts")
    print("  3. Consider adding fuzzy match threshold or additional validation")
    print("  4. Verify short entity names are legitimate")
    print()

    conn.close()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Identify European Companies for Removal from TED Chinese Entities Table
Created: October 19, 2025
Purpose: Create exclusion list of European companies incorrectly flagged as Chinese
"""

import sqlite3
import json
from datetime import datetime

DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"

def main():
    print("="*80)
    print("IDENTIFYING EUROPEAN COMPANIES FOR REMOVAL")
    print("="*80)
    print()

    conn = sqlite3.connect(DB_PATH, timeout=60)
    cursor = conn.cursor()

    # European legal entity suffixes (definitive markers)
    european_suffixes = {
        # German
        'GmbH': 'German Limited Liability',
        ' AG': 'German/Austrian Stock Corp',
        ' KG': 'German Limited Partnership',

        # Polish
        'Sp. z o.o.': 'Polish LLC',
        ' S.A.': 'Polish/French/Spanish Stock Corp',

        # Czech/Slovak
        ' a.s.': 'Czech Joint-Stock',
        ' s.r.o.': 'Czech/Slovak LLC',

        # Nordic
        ' AB': 'Swedish/Lithuanian Stock Corp',
        ' AS': 'Norwegian/Danish Stock Corp',
        ' Oy': 'Finnish LLC',
        ' OY': 'Finnish LLC',

        # Italian
        ' S.p.A.': 'Italian Stock Corp',
        ' SpA': 'Italian Stock Corp',
        ' S.r.l.': 'Italian LLC',
        ' Srl': 'Italian LLC',

        # Dutch
        ' B.V.': 'Dutch Private Company',
        ' NV': 'Dutch Public Company',
        ' N.V.': 'Dutch Public Company',

        # British/Irish
        ' Ltd': 'British Limited',
        ' PLC': 'British Public Limited',
        ' Limited': 'British Limited',

        # French
        ' SAS': 'French Simplified Stock Corp',
        ' SARL': 'French LLC',

        # Spanish
        ' SL': 'Spanish LLC',

        # Belgian
        ' BVBA': 'Belgian Private Company',

        # Other
        ' OÜ': 'Estonian LLC',
        ' UAB': 'Lithuanian LLC',
        ' SIA': 'Latvian LLC'
    }

    print("Step 1: Getting all entities from ted_procurement_chinese_entities_found...")
    cursor.execute('''
        SELECT entity_id, entity_name, entity_type, contracts_count
        FROM ted_procurement_chinese_entities_found
        ORDER BY entity_name
    ''')

    all_entities = cursor.fetchall()
    print(f"  Total entities in table: {len(all_entities):,}")
    print()

    # Identify European companies
    print("Step 2: Identifying European companies...")
    european_companies = []

    for entity_id, entity_name, entity_type, contracts_count in all_entities:
        matched_suffix = None

        for suffix, description in european_suffixes.items():
            if suffix in entity_name:
                matched_suffix = (suffix, description)
                break

        if matched_suffix:
            european_companies.append({
                'entity_id': entity_id,
                'entity_name': entity_name,
                'entity_type': entity_type,
                'contracts_count': contracts_count,
                'european_suffix': matched_suffix[0],
                'suffix_description': matched_suffix[1]
            })

    print(f"  European companies identified: {len(european_companies):,}")
    print(f"  Percentage of total: {len(european_companies)/len(all_entities)*100:.1f}%")
    print()

    # Show summary by suffix
    print("European companies by legal suffix:")
    print("-" * 80)
    suffix_counts = {}
    for company in european_companies:
        suffix = company['european_suffix']
        suffix_counts[suffix] = suffix_counts.get(suffix, 0) + 1

    for suffix in sorted(suffix_counts.keys(), key=lambda x: suffix_counts[x], reverse=True):
        count = suffix_counts[suffix]
        desc = european_suffixes[suffix]
        print(f"  {suffix:20s} - {count:4d} companies ({desc})")
    print()

    # Show top 30 European companies by contract count
    print("Top 30 European companies (by contract count):")
    print("-" * 80)
    sorted_european = sorted(european_companies, key=lambda x: x['contracts_count'] or 0, reverse=True)
    for i, company in enumerate(sorted_european[:30], 1):
        name = company['entity_name'][:55]
        cnt = company['contracts_count'] or 0
        suffix = company['european_suffix']
        # Handle Unicode encoding errors gracefully
        try:
            print(f"  {i:2d}. {name:55s} {cnt:6,} [{suffix}]")
        except UnicodeEncodeError:
            # Fallback: encode as ASCII with replacement characters
            safe_name = name.encode('ascii', 'replace').decode('ascii')
            print(f"  {i:2d}. {safe_name:55s} {cnt:6,} [{suffix}]")
    print()

    # Calculate impact
    total_contracts_affected = sum(c['contracts_count'] or 0 for c in european_companies)
    total_contracts = sum(e[3] or 0 for e in all_entities)

    print("IMPACT ASSESSMENT:")
    print("-" * 80)
    print(f"  Entities to remove: {len(european_companies):,} of {len(all_entities):,} ({len(european_companies)/len(all_entities)*100:.1f}%)")
    print(f"  Contracts affected: {total_contracts_affected:,} of {total_contracts:,} ({total_contracts_affected/total_contracts*100:.1f}%)")
    print()

    # Save European companies list
    output_file = "analysis/european_companies_for_removal_20251019.json"
    output_data = {
        'timestamp': datetime.now().isoformat(),
        'total_entities': len(all_entities),
        'european_entities': len(european_companies),
        'european_percentage': len(european_companies)/len(all_entities)*100,
        'contracts_affected': total_contracts_affected,
        'suffix_counts': suffix_counts,
        'companies_to_remove': [
            {
                'entity_id': c['entity_id'],
                'entity_name': c['entity_name'],
                'contracts_count': c['contracts_count'],
                'european_suffix': c['european_suffix'],
                'reason': f"European company ({c['suffix_description']})"
            }
            for c in european_companies
        ]
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"European companies list saved to: {output_file}")
    print()

    # Generate entity IDs for SQL deletion
    entity_ids_to_remove = [c['entity_id'] for c in european_companies if c['entity_id']]

    print("="*80)
    print("REMOVAL SUMMARY")
    print("="*80)
    print(f"  {len(entity_ids_to_remove):,} entity IDs ready for deletion")
    print(f"  This will remove ~{total_contracts_affected:,} false positive contract associations")
    print()
    print("Next step: Run cleanup script to remove these entities from the database")
    print()

    conn.close()

    return len(european_companies)

if __name__ == "__main__":
    removed_count = main()
    print(f"Identified {removed_count:,} European companies for removal")

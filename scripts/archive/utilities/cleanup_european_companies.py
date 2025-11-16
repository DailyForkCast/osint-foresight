#!/usr/bin/env python3
"""
Clean European Companies from TED Chinese Entities Table
Created: October 19, 2025
Purpose: Remove 2,448 European companies incorrectly flagged as Chinese entities
"""

import sqlite3
import json
from datetime import datetime

DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"
EUROPEAN_COMPANIES_FILE = "analysis/european_companies_for_removal_20251019.json"

def main():
    print("="*80)
    print("CLEANING EUROPEAN COMPANIES FROM TED CHINESE ENTITIES TABLE")
    print("="*80)
    print()

    # Load European companies list
    print("[1/6] Loading European companies list...")
    with open(EUROPEAN_COMPANIES_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    companies_to_remove = data['companies_to_remove']
    print(f"  Loaded {len(companies_to_remove):,} European companies for removal")
    print(f"  Source: {EUROPEAN_COMPANIES_FILE}")
    print()

    # Connect to database
    conn = sqlite3.connect(DB_PATH, timeout=60)
    cursor = conn.cursor()

    # Check current state
    print("[2/6] Checking current state...")
    cursor.execute("SELECT COUNT(*) FROM ted_procurement_chinese_entities_found")
    before_count = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(contracts_count) FROM ted_procurement_chinese_entities_found")
    before_contracts = cursor.fetchone()[0] or 0

    print(f"  Current entities in table: {before_count:,}")
    print(f"  Current contract associations: {before_contracts:,}")
    print()

    # Verify entities exist
    print("[3/6] Verifying entities to remove exist in database...")
    entity_ids = [c['entity_id'] for c in companies_to_remove if c['entity_id']]

    placeholders = ','.join('?' * len(entity_ids))
    cursor.execute(f'''
        SELECT COUNT(*) FROM ted_procurement_chinese_entities_found
        WHERE entity_id IN ({placeholders})
    ''', entity_ids)

    found_count = cursor.fetchone()[0]
    print(f"  Entities found in database: {found_count:,} of {len(entity_ids):,}")

    if found_count != len(entity_ids):
        print(f"  WARNING: {len(entity_ids) - found_count:,} entities not found!")
    print()

    # Calculate impact
    cursor.execute(f'''
        SELECT SUM(contracts_count) FROM ted_procurement_chinese_entities_found
        WHERE entity_id IN ({placeholders})
    ''', entity_ids)

    contracts_to_remove = cursor.fetchone()[0] or 0
    print(f"  Contract associations to remove: {contracts_to_remove:,}")
    print()

    # Delete European companies
    print("[4/6] Deleting European companies from table...")
    cursor.execute(f'''
        DELETE FROM ted_procurement_chinese_entities_found
        WHERE entity_id IN ({placeholders})
    ''', entity_ids)

    deleted_count = cursor.rowcount
    print(f"  Deleted {deleted_count:,} entities")
    print()

    # Verify deletion
    print("[5/6] Verifying deletion...")
    cursor.execute("SELECT COUNT(*) FROM ted_procurement_chinese_entities_found")
    after_count = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(contracts_count) FROM ted_procurement_chinese_entities_found")
    after_contracts = cursor.fetchone()[0] or 0

    print(f"  Entities remaining in table: {after_count:,}")
    print(f"  Contract associations remaining: {after_contracts:,}")
    print(f"  Entities removed: {before_count - after_count:,}")
    print(f"  Contract associations removed: {before_contracts - after_contracts:,}")
    print()

    # Commit changes
    print("[6/6] Committing changes...")
    conn.commit()
    print("  Changes committed successfully")
    print()

    # Generate cleanup report
    cleanup_report = {
        'timestamp': datetime.now().isoformat(),
        'european_companies_file': EUROPEAN_COMPANIES_FILE,
        'before_cleanup': {
            'total_entities': before_count,
            'total_contract_associations': before_contracts
        },
        'after_cleanup': {
            'total_entities': after_count,
            'total_contract_associations': after_contracts
        },
        'removed': {
            'entities': before_count - after_count,
            'contract_associations': before_contracts - after_contracts,
            'percentage_entities': (before_count - after_count) / before_count * 100 if before_count > 0 else 0,
            'percentage_contracts': (before_contracts - after_contracts) / before_contracts * 100 if before_contracts > 0 else 0
        },
        'suffix_breakdown': data.get('suffix_counts', {})
    }

    report_file = "analysis/ted_european_cleanup_report_20251019.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(cleanup_report, f, indent=2, ensure_ascii=False)

    print(f"Cleanup report saved to: {report_file}")
    print()

    # Summary
    print("="*80)
    print("CLEANUP SUMMARY")
    print("="*80)
    print()
    print(f"Before Cleanup:")
    print(f"  Total entities: {before_count:,}")
    print(f"  Contract associations: {before_contracts:,}")
    print()
    print(f"After Cleanup:")
    print(f"  Total entities: {after_count:,} ({after_count/before_count*100:.1f}% remaining)")
    print(f"  Contract associations: {after_contracts:,} ({after_contracts/before_contracts*100:.1f}% remaining)")
    print()
    print(f"Removed:")
    print(f"  Entities: {before_count - after_count:,} ({(before_count - after_count)/before_count*100:.1f}%)")
    print(f"  Contract associations: {before_contracts - after_contracts:,} ({(before_contracts - after_contracts)/before_contracts*100:.1f}%)")
    print()
    print("Next Step: Re-sync ted_contracts_production with cleaned entity table")
    print()

    conn.close()

    return deleted_count

if __name__ == "__main__":
    removed = main()
    print(f"Successfully removed {removed:,} European companies from TED Chinese entities table")

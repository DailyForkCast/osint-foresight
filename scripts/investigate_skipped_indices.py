#!/usr/bin/env python3
"""
Investigate Skipped Indices - Find Actual Column Names
Analyzes database schema to identify correct column names for skipped indices
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

DB_PATH = Path("F:/OSINT_WAREHOUSE/osint_master.db")

# Indices that were skipped in Phase 1 and Phase 2
SKIPPED_INDICES = {
    # Phase 1 skipped (8 indices)
    'entity_cross_references': ['entity_id', 'external_id'],
    'document_entities': ['entity_id'],
    'gleif_entities': ['country_code'],
    'arxiv_authors': ['country_code'],
    'uspto_assignee': ['country_code'],
    'sec_edgar_companies': ['state'],
    'usaspending_contractors': ['contractor_name'],

    # Phase 2 skipped (8 indices)
    'arxiv_papers': ['publication_year', 'country_code'],
    'uspto_patents_chinese': ['publication_year'],
    'usaspending_contracts': ['award_date'],
    'openalex_works': ['is_chinese', 'publication_year'],
    'entities': ['country'],
    'ted_contracts_production': ['country_iso', 'contract_value'],
}

def investigate_table_schema(conn, table_name):
    """Get complete schema information for a table"""
    cursor = conn.cursor()

    # Check if table exists
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name=?
    """, (table_name,))

    if not cursor.fetchone():
        return None

    # Get column info
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()

    # Get row count
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    row_count = cursor.fetchone()[0]

    # Get sample data
    cursor.execute(f"SELECT * FROM {table_name} LIMIT 1")
    sample = cursor.fetchone()

    return {
        'exists': True,
        'columns': [
            {
                'id': col[0],
                'name': col[1],
                'type': col[2],
                'not_null': col[3],
                'default': col[4],
                'pk': col[5]
            }
            for col in columns
        ],
        'row_count': row_count,
        'has_data': sample is not None
    }

def find_similar_columns(actual_columns, expected_columns):
    """Find similar column names in actual schema"""
    matches = {}

    for expected in expected_columns:
        expected_lower = expected.lower()
        candidates = []

        for actual in actual_columns:
            actual_lower = actual['name'].lower()

            # Exact match
            if actual_lower == expected_lower:
                candidates.append({
                    'name': actual['name'],
                    'match_type': 'exact',
                    'confidence': 1.0
                })
            # Partial match (contains)
            elif expected_lower in actual_lower or actual_lower in expected_lower:
                candidates.append({
                    'name': actual['name'],
                    'match_type': 'partial',
                    'confidence': 0.8
                })
            # Fuzzy match (similar words)
            elif any(word in actual_lower for word in expected_lower.split('_')):
                candidates.append({
                    'name': actual['name'],
                    'match_type': 'fuzzy',
                    'confidence': 0.5
                })

        matches[expected] = sorted(candidates, key=lambda x: x['confidence'], reverse=True)

    return matches

def set_utf8_output():
    """Set UTF-8 encoding for Windows console output"""
    import sys
    import io
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def main():
    print("=" * 80)
    print("INVESTIGATING SKIPPED INDICES")
    print("=" * 80)
    print(f"Database: {DB_PATH}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("")

    conn = sqlite3.connect(DB_PATH)

    results = {
        'timestamp': datetime.now().isoformat(),
        'tables_investigated': {},
        'recommendations': []
    }

    for table_name, expected_columns in SKIPPED_INDICES.items():
        print(f"\n{'='*80}")
        print(f"Table: {table_name}")
        print(f"Expected columns: {', '.join(expected_columns)}")
        print("=" * 80)

        schema = investigate_table_schema(conn, table_name)

        if schema is None:
            print(f"  [X] Table does not exist")
            results['tables_investigated'][table_name] = {
                'exists': False,
                'reason': 'Table not found in database'
            }
            continue

        print(f"  [OK] Table exists: {schema['row_count']:,} rows")

        if schema['row_count'] == 0:
            print(f"  [!] WARNING: Table is empty!")

        print(f"\n  Actual columns ({len(schema['columns'])}):")
        for col in schema['columns']:
            pk_marker = " [PRIMARY KEY]" if col['pk'] else ""
            print(f"    - {col['name']:30} {col['type']:15}{pk_marker}")

        # Find similar columns
        matches = find_similar_columns(schema['columns'], expected_columns)

        print(f"\n  Column mapping suggestions:")
        for expected, candidates in matches.items():
            if candidates:
                best = candidates[0]
                match_icon = "[OK]" if best['match_type'] == 'exact' else "[~]"
                print(f"    {match_icon} {expected:20} -> {best['name']:30} ({best['match_type']}, {best['confidence']:.0%})")

                # Add recommendation
                if best['confidence'] >= 0.5:
                    results['recommendations'].append({
                        'table': table_name,
                        'expected_column': expected,
                        'actual_column': best['name'],
                        'match_type': best['match_type'],
                        'confidence': best['confidence'],
                        'row_count': schema['row_count']
                    })
            else:
                print(f"    [X] {expected:20} -> No match found")

        results['tables_investigated'][table_name] = {
            'exists': True,
            'row_count': schema['row_count'],
            'columns': [col['name'] for col in schema['columns']],
            'matches': matches
        }

    conn.close()

    # Save results
    output_file = Path("analysis/skipped_indices_investigation.json")
    output_file.parent.mkdir(exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print("\n" + "=" * 80)
    print("SUMMARY - RECOMMENDED INDICES TO CREATE")
    print("=" * 80)

    high_confidence = [r for r in results['recommendations'] if r['confidence'] >= 0.8]
    medium_confidence = [r for r in results['recommendations'] if 0.5 <= r['confidence'] < 0.8]

    print(f"\n[OK] HIGH CONFIDENCE ({len(high_confidence)} indices):")
    for rec in high_confidence:
        print(f"  - {rec['table']}.{rec['actual_column']} ({rec['row_count']:,} rows)")

    print(f"\n[~] MEDIUM CONFIDENCE ({len(medium_confidence)} indices):")
    for rec in medium_confidence:
        print(f"  - {rec['table']}.{rec['actual_column']} ({rec['row_count']:,} rows)")

    print(f"\n[#] Total: {len(results['recommendations'])} indices can be created")
    print(f"\n[SAVE] Full report saved: {output_file}")
    print("\n" + "=" * 80)
    print("INVESTIGATION COMPLETE")
    print("=" * 80)

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Comprehensive Data Source Inventory
Surveys osint_master.db to determine what's collected vs. truly missing
"""
import sqlite3
import sys
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")

# Define all known/planned data sources
DATA_SOURCES = {
    'OpenAlex': {
        'description': 'Open access bibliographic database',
        'table_prefixes': ['openalex_'],
        'priority': 'HIGH'
    },
    'CORDIS': {
        'description': 'EU research and innovation projects',
        'table_prefixes': ['cordis_'],
        'priority': 'HIGH'
    },
    'OpenAIRE': {
        'description': 'European research infrastructure',
        'table_prefixes': ['openaire_'],
        'priority': 'MEDIUM'
    },
    'TED': {
        'description': 'EU public procurement database',
        'table_prefixes': ['ted_'],
        'priority': 'HIGH'
    },
    'USAspending': {
        'description': 'US federal spending data',
        'table_prefixes': ['usaspending_'],
        'priority': 'HIGH'
    },
    'USPTO': {
        'description': 'US Patent and Trademark Office',
        'table_prefixes': ['uspto_'],
        'priority': 'HIGH'
    },
    'PatentsView': {
        'description': 'USPTO patent analytics platform',
        'table_prefixes': ['patentsview_'],
        'priority': 'MEDIUM'
    },
    'EPO': {
        'description': 'European Patent Office',
        'table_prefixes': ['epo_'],
        'priority': 'MEDIUM'
    },
    'GLEIF': {
        'description': 'Global Legal Entity Identifier Foundation',
        'table_prefixes': ['gleif_'],
        'priority': 'MEDIUM'
    },
    'SEC EDGAR': {
        'description': 'US Securities and Exchange Commission filings',
        'table_prefixes': ['sec_edgar_'],
        'priority': 'MEDIUM'
    },
    'AidData': {
        'description': 'Development finance tracking',
        'table_prefixes': ['aiddata_'],
        'priority': 'MEDIUM'
    },
    'BIS Entity List': {
        'description': 'US export control restricted entities',
        'table_prefixes': ['bis_entity_'],
        'priority': 'HIGH'
    },
    'Companies House': {
        'description': 'UK corporate registry',
        'table_prefixes': ['companies_house_'],
        'priority': 'LOW'
    },
    'OpenSanctions': {
        'description': 'Sanctions and entity watchlists',
        'table_prefixes': ['opensanctions_'],
        'priority': 'MEDIUM'
    },
    'Kaggle arXiv': {
        'description': 'Academic preprints dataset',
        'table_prefixes': ['arxiv_'],
        'priority': 'MEDIUM'
    },
    'GitHub': {
        'description': 'Open source activity tracking',
        'table_prefixes': ['github_'],
        'priority': 'LOW'
    },
    'ETO Datasets': {
        'description': 'Emerging Technology Observatory datasets',
        'table_prefixes': ['eto_'],
        'priority': 'MEDIUM'
    },
    'Think Tanks': {
        'description': 'Policy research publications',
        'table_prefixes': ['thinktank_', 'documents_'],
        'priority': 'MEDIUM'
    },
    'China Sources': {
        'description': 'Chinese official sources (Peoples Daily, Qiushi, etc.)',
        'table_prefixes': ['china_policy_'],
        'priority': 'LOW'
    },
    'WIPO PatentScope': {
        'description': 'World Intellectual Property Organization',
        'table_prefixes': ['wipo_'],
        'priority': 'LOW'
    }
}

print("="*80)
print("COMPREHENSIVE DATA SOURCE INVENTORY")
print(f"Timestamp: {datetime.now().isoformat()}")
print("="*80)

try:
    conn = sqlite3.connect(str(db_path), timeout=10)
    cursor = conn.cursor()

    # Get all tables
    cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name NOT LIKE "sqlite_%"')
    all_tables = [row[0] for row in cursor.fetchall()]

    print(f"\nDatabase: {db_path}")
    print(f"Total tables: {len(all_tables)}")

    inventory = {}

    # Survey each data source
    for source_name, source_info in DATA_SOURCES.items():
        print(f"\n{'='*80}")
        print(f"{source_name}")
        print(f"Description: {source_info['description']}")
        print(f"Priority: {source_info['priority']}")
        print('='*80)

        # Find matching tables
        matching_tables = []
        for prefix in source_info['table_prefixes']:
            matching_tables.extend([t for t in all_tables if t.startswith(prefix)])

        matching_tables = list(set(matching_tables))  # Remove duplicates
        matching_tables.sort()

        if not matching_tables:
            print(f"  [NOT COLLECTED] No tables found")
            inventory[source_name] = {
                'status': 'NOT COLLECTED',
                'tables': [],
                'total_records': 0,
                'description': source_info['description'],
                'priority': source_info['priority']
            }
            continue

        # Count records in each table
        table_stats = []
        total_records = 0
        populated_count = 0
        empty_count = 0

        for table in matching_tables:
            try:
                cursor.execute(f'SELECT COUNT(*) FROM "{table}"')
                count = cursor.fetchone()[0]
                total_records += count

                if count > 0:
                    populated_count += 1
                    print(f"  ✓ {table}: {count:,} records")
                else:
                    empty_count += 1
                    print(f"  ○ {table}: EMPTY (infrastructure)")

                table_stats.append({
                    'name': table,
                    'records': count
                })
            except Exception as e:
                print(f"  ✗ {table}: ERROR - {e}")
                table_stats.append({
                    'name': table,
                    'records': -1,
                    'error': str(e)
                })

        # Determine status
        if total_records > 0:
            status = 'COLLECTED & POPULATED'
        elif matching_tables:
            status = 'INFRASTRUCTURE ONLY'
        else:
            status = 'NOT COLLECTED'

        print(f"\n  Summary: {len(matching_tables)} tables ({populated_count} populated, {empty_count} empty)")
        print(f"  Total records: {total_records:,}")
        print(f"  Status: {status}")

        inventory[source_name] = {
            'status': status,
            'tables': table_stats,
            'table_count': len(matching_tables),
            'populated_tables': populated_count,
            'empty_tables': empty_count,
            'total_records': total_records,
            'description': source_info['description'],
            'priority': source_info['priority']
        }

    # Check for unclassified tables
    classified_tables = set()
    for source_name, source_info in DATA_SOURCES.items():
        for prefix in source_info['table_prefixes']:
            classified_tables.update([t for t in all_tables if t.startswith(prefix)])

    unclassified = set(all_tables) - classified_tables - {t for t in all_tables if t.startswith('ref_') or t.startswith('import_') or t.startswith('entity_')}

    if unclassified:
        print(f"\n{'='*80}")
        print("UNCLASSIFIED TABLES")
        print('='*80)
        for table in sorted(unclassified):
            try:
                cursor.execute(f'SELECT COUNT(*) FROM "{table}"')
                count = cursor.fetchone()[0]
                print(f"  {table}: {count:,} records")
            except:
                print(f"  {table}: ERROR")

    # Generate summary statistics
    print(f"\n{'='*80}")
    print("INVENTORY SUMMARY")
    print('='*80)

    collected = [s for s, data in inventory.items() if data['status'] == 'COLLECTED & POPULATED']
    infrastructure_only = [s for s, data in inventory.items() if data['status'] == 'INFRASTRUCTURE ONLY']
    not_collected = [s for s, data in inventory.items() if data['status'] == 'NOT COLLECTED']

    print(f"\n[COLLECTED & POPULATED] - {len(collected)} sources")
    for source in collected:
        data = inventory[source]
        print(f"  ✓ {source}: {data['total_records']:,} records across {data['table_count']} tables")

    print(f"\n[INFRASTRUCTURE ONLY] - {len(infrastructure_only)} sources")
    for source in infrastructure_only:
        data = inventory[source]
        print(f"  ○ {source}: {data['table_count']} tables (awaiting data processing)")

    print(f"\n[NOT COLLECTED] - {len(not_collected)} sources")
    for source in not_collected:
        data = inventory[source]
        print(f"  ✗ {source}: No data collected (Priority: {data['priority']})")

    # Save report
    report = {
        'timestamp': datetime.now().isoformat(),
        'database': str(db_path),
        'total_tables': len(all_tables),
        'inventory': inventory,
        'summary': {
            'collected_and_populated': collected,
            'infrastructure_only': infrastructure_only,
            'not_collected': not_collected
        },
        'unclassified_tables': sorted(list(unclassified))
    }

    report_path = Path("C:/Projects/OSINT - Foresight/analysis/DATA_SOURCE_INVENTORY.json")
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    print(f"\n[SAVED] Detailed report: {report_path}")
    print("="*80)

    conn.close()
    sys.exit(0)

except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

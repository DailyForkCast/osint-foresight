#!/usr/bin/env python3
"""Categorize the 59 empty tables from the audit results"""
import json
from pathlib import Path
from collections import defaultdict

# Load the audit results
audit_path = Path("C:/Projects/OSINT - Foresight/analysis/DATABASE_AUDIT_RESULTS.json")
with open(audit_path, 'r') as f:
    audit = json.load(f)

empty_tables = audit['findings']['empty_tables']
all_tables = audit['findings']['all_table_names']

# Find all empty tables (audit only showed first 20)
import sqlite3
db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")
conn = sqlite3.connect(str(db_path), timeout=10)
cursor = conn.cursor()

empty_tables_full = []
for table in all_tables:
    try:
        cursor.execute(f'SELECT COUNT(*) FROM "{table}"')
        if cursor.fetchone()[0] == 0:
            empty_tables_full.append(table)
    except:
        pass

conn.close()

def categorize(name):
    """Categorize table by prefix"""
    if name.startswith('aiddata_'): return 'AidData (Development Finance)'
    if name.startswith('bis_'): return 'BIS Entity List (Export Controls)'
    if name.startswith('comtrade_'): return 'UN Comtrade (Trade Data)'
    if name.startswith('cordis_'): return 'CORDIS (EU Research)'
    if name.startswith('eto_'): return 'ETO (Emerging Tech Observatory)'
    if name.startswith('gleif_'): return 'GLEIF (Legal Entity IDs)'
    if name.startswith('entity_'): return 'Entity Management Infrastructure'
    if name.startswith('report_'): return 'Report Generation System'
    if name.startswith('risk_'): return 'Risk Assessment System'
    if name.startswith('import_'): return 'Data Import Staging'
    if name.startswith('intelligence_'): return 'Intelligence Analysis'
    if name.startswith('ref_'): return 'Reference/Lookup Tables'
    if name.startswith('mcf_'): return 'MCF Document System'
    if name.startswith('openaire_'): return 'OpenAIRE Research Data'
    if name.startswith('openalex_'): return 'OpenAlex Academic Data'
    if name.startswith('usgov_'): return 'US Gov Document Sweeps'
    return 'Other/Uncategorized'

def recommend(table, category):
    """Recommend action"""
    name_lower = table.lower()

    # DROP candidates
    if 'temp' in name_lower or 'staging' in name_lower:
        return 'DROP', 'Temporary table - no longer needed'
    if 'import_' in table:
        return 'DROP', 'Import staging table - data already integrated'
    if 'fixed' in name_lower:
        return 'DROP', 'Duplicate/corrected table - original exists'

    # KEEP candidates - infrastructure
    if category in ['Entity Management Infrastructure', 'Risk Assessment System',
                    'Report Generation System', 'Reference/Lookup Tables']:
        return 'KEEP', 'Core infrastructure - keep as placeholder'

    # KEEP candidates - future data sources
    if category in ['AidData (Development Finance)', 'UN Comtrade (Trade Data)',
                    'ETO (Emerging Tech Observatory)']:
        return 'KEEP', 'Future data source - keep as placeholder'

    # INVESTIGATE - may have value
    if category in ['GLEIF (Legal Entity IDs)']:
        return 'INVESTIGATE', 'Check if GLEIF processing incomplete'

    # ARCHIVE - low priority
    return 'ARCHIVE', 'Empty data table - archive for reference'

# Categorize all
categories = defaultdict(list)
recommendations = defaultdict(list)

for table in empty_tables_full:
    cat = categorize(table)
    action, reason = recommend(table, cat)

    categories[cat].append(table)
    recommendations[action].append({
        'table': table,
        'category': cat,
        'reason': reason
    })

# Print results
print("="*70)
print(f"EMPTY TABLES CATEGORIZATION ({len(empty_tables_full)} tables)")
print("="*70)

print("\n[BY CATEGORY]")
for cat in sorted(categories.keys()):
    tables = categories[cat]
    print(f"\n{cat}: {len(tables)} tables")
    for t in tables:
        print(f"  - {t}")

print("\n" + "="*70)
print("[RECOMMENDATIONS]")
print("="*70)

for action in ['DROP', 'ARCHIVE', 'KEEP', 'INVESTIGATE']:
    items = recommendations[action]
    print(f"\n{action}: {len(items)} tables")
    for item in items[:10]:
        print(f"  - {item['table']}")
        print(f"    Category: {item['category']}")
        print(f"    Reason: {item['reason']}")
    if len(items) > 10:
        print(f"  ... and {len(items) - 10} more")

# Save detailed analysis
output = {
    'summary': {
        'total_empty_tables': len(empty_tables_full),
        'categories': {cat: len(tables) for cat, tables in categories.items()},
        'recommendations': {action: len(items) for action, items in recommendations.items()}
    },
    'by_category': {cat: tables for cat, tables in categories.items()},
    'by_recommendation': {action: items for action, items in recommendations.items()},
    'all_empty_tables': sorted(empty_tables_full)
}

output_path = Path("C:/Projects/OSINT - Foresight/analysis/EMPTY_TABLES_CATEGORIZED.json")
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)

print(f"\n[SAVED] Full analysis: {output_path}")
print("="*70)

# Print action summary
print("\n[CLEANUP PLAN]")
print(f"  DROP: {len(recommendations['DROP'])} tables (safe to remove)")
print(f"  ARCHIVE: {len(recommendations['ARCHIVE'])} tables (move to archive)")
print(f"  KEEP: {len(recommendations['KEEP'])} tables (infrastructure/placeholders)")
print(f"  INVESTIGATE: {len(recommendations['INVESTIGATE'])} tables (needs review)")

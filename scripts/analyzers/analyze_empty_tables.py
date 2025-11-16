#!/usr/bin/env python3
"""
analyze_empty_tables.py - Categorize and Analyze Empty Tables

Identifies what each empty table is supposed to be for and provides cleanup recommendations.
"""

import sqlite3
import json
import sys
from pathlib import Path
from collections import defaultdict

# Set encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def categorize_table(table_name):
    """Categorize table by its prefix or naming pattern"""

    # Data source prefixes
    if table_name.startswith('aiddata_'):
        return 'AidData (Development Finance)'
    elif table_name.startswith('bis_'):
        return 'BIS Entity List (Commerce Controls)'
    elif table_name.startswith('comtrade_'):
        return 'UN Comtrade (International Trade)'
    elif table_name.startswith('cordis_'):
        return 'CORDIS (EU Research Projects)'
    elif table_name.startswith('eto_'):
        return 'ETO (Emerging Tech Observatory)'
    elif table_name.startswith('gleif_'):
        return 'GLEIF (Legal Entity Identifiers)'
    elif table_name.startswith('github_'):
        return 'GitHub (Code Repositories)'
    elif table_name.startswith('openaire_'):
        return 'OpenAIRE (Research Publications)'
    elif table_name.startswith('openalex_'):
        return 'OpenAlex (Academic Research)'
    elif table_name.startswith('patents_'):
        return 'Patents (USPTO/EPO)'
    elif table_name.startswith('patentsview_'):
        return 'PatentsView (USPTO Database)'
    elif table_name.startswith('ted_'):
        return 'TED (EU Public Procurement)'
    elif table_name.startswith('usaspending_'):
        return 'USASpending (US Government Contracts)'
    elif table_name.startswith('uspto_'):
        return 'USPTO (US Patent Office)'
    elif table_name.startswith('sec_'):
        return 'SEC EDGAR (Company Filings)'
    elif table_name.startswith('rss_'):
        return 'RSS Monitoring (News/Updates)'
    elif table_name.startswith('arxiv_'):
        return 'arXiv (Preprint Publications)'
    elif table_name.startswith('prc_') or table_name.startswith('china_'):
        return 'China-Specific Data'
    elif 'entity' in table_name.lower() or 'entities' in table_name.lower():
        return 'Entity Management'
    elif 'detection' in table_name.lower():
        return 'Detection Systems'
    elif 'validation' in table_name.lower():
        return 'Validation/QA'
    elif 'metadata' in table_name.lower() or 'config' in table_name.lower():
        return 'Configuration/Metadata'
    else:
        return 'Other/Uncategorized'

def get_table_schema(cursor, table_name):
    """Get schema information for a table"""
    try:
        cursor.execute(f'PRAGMA table_info("{table_name}")')
        columns = cursor.fetchall()
        return [{'name': col[1], 'type': col[2], 'notnull': col[3], 'pk': col[5]} for col in columns]
    except Exception as e:
        return None

def analyze_purpose(table_name, schema):
    """Infer table's intended purpose from name and schema"""

    purposes = []

    # Check schema for clues
    if schema:
        col_names = [col['name'].lower() for col in schema]

        if any('country' in c for c in col_names):
            purposes.append("Country-specific data")
        if any('date' in c or 'time' in c for c in col_names):
            purposes.append("Temporal data tracking")
        if any('entity' in c or 'organization' in c for c in col_names):
            purposes.append("Entity/organization records")
        if any('patent' in c for c in col_names):
            purposes.append("Patent information")
        if any('contract' in c or 'procurement' in c for c in col_names):
            purposes.append("Contract/procurement data")
        if any('tech' in c or 'technology' in c for c in col_names):
            purposes.append("Technology categorization")
        if any('score' in c or 'confidence' in c for c in col_names):
            purposes.append("Analysis/scoring system")

    # Check name for clues
    name_lower = table_name.lower()
    if 'temp' in name_lower or 'staging' in name_lower:
        purposes.append("Temporary/staging table")
    if 'archive' in name_lower or 'backup' in name_lower:
        purposes.append("Archive/backup storage")
    if 'raw' in name_lower:
        purposes.append("Raw data ingestion")
    if 'processed' in name_lower or 'clean' in name_lower:
        purposes.append("Processed/cleaned data")
    if 'link' in name_lower or 'relationship' in name_lower:
        purposes.append("Relationship/linkage table")

    return purposes if purposes else ["Purpose unclear from schema"]

def recommend_action(table_name, category, schema, purposes):
    """Recommend action for empty table"""

    name_lower = table_name.lower()

    # Drop candidates
    if 'temp' in name_lower or 'staging' in name_lower:
        return 'DROP', 'Temporary table - no longer needed'

    if 'test' in name_lower:
        return 'DROP', 'Test table - safe to remove'

    # Archive candidates
    if 'archive' in name_lower or 'backup' in name_lower:
        return 'DROP', 'Archive table that was never populated'

    # Keep as placeholder candidates
    if category in ['AidData (Development Finance)', 'UN Comtrade (International Trade)',
                    'ETO (Emerging Tech Observatory)']:
        return 'KEEP', 'Data source placeholder - may be populated in future'

    if 'Entity Management' in category or 'Detection Systems' in category:
        return 'KEEP', 'Core infrastructure table - keep as placeholder'

    if schema and len(schema) > 5:
        return 'INVESTIGATE', 'Complex schema - investigate before dropping'

    return 'ARCHIVE', 'Low priority - archive for reference'

def main():
    db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")

    print("=" * 70)
    print("EMPTY TABLES ANALYSIS")
    print("=" * 70)

    try:
        conn = sqlite3.connect(str(db_path), timeout=10)
        cursor = conn.cursor()

        # Get all tables
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)
        all_tables = [row[0] for row in cursor.fetchall()]

        print(f"\nTotal tables in database: {len(all_tables)}")

        # Find empty tables
        empty_tables = []
        for table in all_tables:
            try:
                cursor.execute(f'SELECT COUNT(*) FROM "{table}"')
                count = cursor.fetchone()[0]
                if count == 0:
                    empty_tables.append(table)
            except:
                pass

        print(f"Empty tables found: {len(empty_tables)}")

        # Analyze each empty table
        analysis = {
            'summary': {
                'total_tables': len(all_tables),
                'empty_tables': len(empty_tables),
                'percent_empty': round(len(empty_tables) / len(all_tables) * 100, 1)
            },
            'by_category': defaultdict(list),
            'recommendations': {
                'DROP': [],
                'KEEP': [],
                'ARCHIVE': [],
                'INVESTIGATE': []
            },
            'detailed_analysis': []
        }

        print("\n" + "=" * 70)
        print("CATEGORIZATION AND RECOMMENDATIONS")
        print("=" * 70)

        for table_name in empty_tables:
            category = categorize_table(table_name)
            schema = get_table_schema(cursor, table_name)
            purposes = analyze_purpose(table_name, schema)
            action, reason = recommend_action(table_name, category, schema, purposes)

            table_info = {
                'table_name': table_name,
                'category': category,
                'schema': schema,
                'inferred_purposes': purposes,
                'recommendation': action,
                'reason': reason,
                'column_count': len(schema) if schema else 0
            }

            analysis['by_category'][category].append(table_name)
            analysis['recommendations'][action].append(table_name)
            analysis['detailed_analysis'].append(table_info)

        # Print by category
        print("\n[BY CATEGORY]")
        for category in sorted(analysis['by_category'].keys()):
            tables = analysis['by_category'][category]
            print(f"\n{category}: {len(tables)} tables")
            for table in sorted(tables)[:5]:
                print(f"  - {table}")
            if len(tables) > 5:
                print(f"  ... and {len(tables) - 5} more")

        # Print recommendations
        print("\n" + "=" * 70)
        print("[RECOMMENDATIONS SUMMARY]")
        print("=" * 70)

        for action in ['DROP', 'ARCHIVE', 'KEEP', 'INVESTIGATE']:
            tables = analysis['recommendations'][action]
            print(f"\n{action}: {len(tables)} tables")
            for table in sorted(tables)[:5]:
                # Find the detailed info
                detail = next(d for d in analysis['detailed_analysis'] if d['table_name'] == table)
                print(f"  - {table}")
                print(f"    Category: {detail['category']}")
                print(f"    Reason: {detail['reason']}")
            if len(tables) > 5:
                print(f"  ... and {len(tables) - 5} more")

        # Save detailed report
        output_path = Path("C:/Projects/OSINT - Foresight/analysis/EMPTY_TABLES_ANALYSIS.json")
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2)

        print("\n" + "=" * 70)
        print(f"[SAVED] Full analysis: {output_path}")
        print("=" * 70)

        # Print action summary
        print("\n[ACTION SUMMARY]")
        print(f"  DROP: {len(analysis['recommendations']['DROP'])} tables (temp/test tables)")
        print(f"  ARCHIVE: {len(analysis['recommendations']['ARCHIVE'])} tables (low priority)")
        print(f"  KEEP: {len(analysis['recommendations']['KEEP'])} tables (future use)")
        print(f"  INVESTIGATE: {len(analysis['recommendations']['INVESTIGATE'])} tables (complex schemas)")

        conn.close()

    except Exception as e:
        print(f"\n[ERROR] Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Phase 2: Investigate 20 Empty Tables for Functional Duplicates
Checks if empty tables have populated equivalents serving the same purpose
"""
import sqlite3
import sys
import json
from pathlib import Path
from datetime import datetime
from difflib import SequenceMatcher

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")

# 20 tables to investigate
investigation_targets = {
    'GLEIF Mappings': [
        'gleif_bic_mapping',
        'gleif_cross_references',
        'gleif_isin_mapping',
        'gleif_opencorporates_mapping',
        'gleif_qcc_mapping',
        'gleif_repex'
    ],
    'OpenAIRE': [
        'openaire_china_collaborations',
        'openaire_china_deep',
        'openaire_china_research',
        'openaire_chinese_organizations',
        'openaire_collaborations',
        'openaire_country_china_stats',
        'openaire_country_metrics'
    ],
    'CORDIS': [
        'cordis_china_collaborations',
        'cordis_organizations',
        'cordis_project_participants'
    ],
    'Others': [
        'aiddata_cross_reference',
        'entity_risk_factors',
        'entity_risk_scores',
        'import_openalex_china_entities'
    ]
}

def get_schema(cursor, table):
    """Get table schema as list of column names"""
    try:
        cursor.execute(f'PRAGMA table_info("{table}")')
        return [col[1] for col in cursor.fetchall()]
    except:
        return []

def schema_similarity(schema1, schema2):
    """Calculate schema similarity (0.0 to 1.0)"""
    if not schema1 or not schema2:
        return 0.0

    # Jaccard similarity of column names
    set1 = set(schema1)
    set2 = set(schema2)
    intersection = len(set1 & set2)
    union = len(set1 | set2)

    return intersection / union if union > 0 else 0.0

def name_similarity(name1, name2):
    """Calculate name similarity using SequenceMatcher"""
    return SequenceMatcher(None, name1.lower(), name2.lower()).ratio()

def find_similar_tables(cursor, empty_table, all_populated_tables):
    """Find potentially duplicate populated tables"""
    empty_schema = get_schema(cursor, empty_table)
    candidates = []

    for pop_table in all_populated_tables:
        pop_schema = get_schema(cursor, pop_table)

        # Calculate similarities
        schema_sim = schema_similarity(empty_schema, pop_schema)
        name_sim = name_similarity(empty_table, pop_table)

        # Get record count
        try:
            cursor.execute(f'SELECT COUNT(*) FROM "{pop_table}"')
            record_count = cursor.fetchone()[0]
        except:
            record_count = 0

        # Only consider tables with some similarity
        if schema_sim > 0.3 or name_sim > 0.5:
            candidates.append({
                'table': pop_table,
                'schema_similarity': round(schema_sim, 3),
                'name_similarity': round(name_sim, 3),
                'records': record_count,
                'schema_overlap': list(set(empty_schema) & set(pop_schema))
            })

    # Sort by combined similarity score
    candidates.sort(key=lambda x: x['schema_similarity'] * 0.6 + x['name_similarity'] * 0.4, reverse=True)
    return candidates[:5]  # Top 5 matches

print("="*80)
print("PHASE 2: EMPTY TABLE INVESTIGATION")
print(f"Timestamp: {datetime.now().isoformat()}")
print("="*80)

try:
    conn = sqlite3.connect(str(db_path), timeout=30)
    cursor = conn.cursor()

    # Get all populated tables
    cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name NOT LIKE "sqlite_%"')
    all_tables = [row[0] for row in cursor.fetchall()]

    populated_tables = []
    for table in all_tables:
        try:
            cursor.execute(f'SELECT COUNT(*) FROM "{table}"')
            if cursor.fetchone()[0] > 0:
                populated_tables.append(table)
        except:
            pass

    print(f"\n[INVESTIGATION SCOPE]")
    print(f"Total tables: {len(all_tables)}")
    print(f"Populated tables: {len(populated_tables)}")
    print(f"Tables to investigate: {sum(len(v) for v in investigation_targets.values())}")

    investigation_results = {}

    # Investigate each category
    for category, tables in investigation_targets.items():
        print(f"\n{'='*80}")
        print(f"{category}: {len(tables)} empty tables")
        print('='*80)

        category_results = []

        for empty_table in tables:
            # Verify table is empty
            try:
                cursor.execute(f'SELECT COUNT(*) FROM "{empty_table}"')
                count = cursor.fetchone()[0]
            except:
                count = -1

            empty_schema = get_schema(cursor, empty_table)
            similar_tables = find_similar_tables(cursor, empty_table, populated_tables)

            result = {
                'table': empty_table,
                'record_count': count,
                'schema': empty_schema,
                'similar_populated_tables': similar_tables,
                'recommendation': 'INVESTIGATE'
            }

            # Generate recommendation
            if count > 0:
                result['recommendation'] = 'NOT EMPTY - REVIEW'
                result['reason'] = f'Has {count:,} records'
            elif similar_tables and similar_tables[0]['schema_similarity'] > 0.8:
                result['recommendation'] = 'LIKELY DUPLICATE - DROP'
                result['reason'] = f"Very similar to {similar_tables[0]['table']} ({similar_tables[0]['schema_similarity']:.1%} schema match)"
            elif similar_tables and similar_tables[0]['name_similarity'] > 0.7:
                result['recommendation'] = 'POSSIBLE DUPLICATE - VERIFY'
                result['reason'] = f"Similar name to {similar_tables[0]['table']}"
            elif not empty_schema:
                result['recommendation'] = 'CORRUPTED - DROP'
                result['reason'] = 'No schema found'
            else:
                result['recommendation'] = 'KEEP AS INFRASTRUCTURE'
                result['reason'] = 'No duplicate found, unique purpose'

            category_results.append(result)

            # Print result
            print(f"\n  [{result['recommendation']}] {empty_table}")
            print(f"    Records: {count:,}" if count >= 0 else "    Records: ERROR")
            print(f"    Columns: {len(empty_schema)}")
            print(f"    Reason: {result['reason']}")

            if similar_tables:
                print(f"    Top match: {similar_tables[0]['table']} ({similar_tables[0]['schema_similarity']:.1%} schema, {similar_tables[0]['name_similarity']:.1%} name)")
                if similar_tables[0]['schema_overlap']:
                    print(f"    Shared columns: {', '.join(similar_tables[0]['schema_overlap'][:5])}" +
                          (f"... +{len(similar_tables[0]['schema_overlap'])-5} more" if len(similar_tables[0]['schema_overlap']) > 5 else ""))

        investigation_results[category] = category_results

    # Summary
    print(f"\n{'='*80}")
    print("INVESTIGATION SUMMARY")
    print('='*80)

    recommendations = {}
    for category, results in investigation_results.items():
        for result in results:
            rec = result['recommendation']
            if rec not in recommendations:
                recommendations[rec] = []
            recommendations[rec].append(result['table'])

    print(f"\nRecommendations by action:")
    for rec, tables in sorted(recommendations.items()):
        print(f"\n[{rec}] - {len(tables)} tables")
        for table in tables:
            print(f"  - {table}")

    # Save detailed report
    report = {
        'timestamp': datetime.now().isoformat(),
        'investigation_targets': investigation_targets,
        'results': investigation_results,
        'summary': recommendations,
        'statistics': {
            'total_investigated': sum(len(v) for v in investigation_targets.values()),
            'by_recommendation': {k: len(v) for k, v in recommendations.items()}
        }
    }

    report_path = Path("C:/Projects/OSINT - Foresight/analysis/PHASE2_INVESTIGATION_REPORT.json")
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    print(f"\n[SAVED] Detailed report: {report_path}")
    print("="*80)

    conn.close()
    sys.exit(0)

except Exception as e:
    print(f"\n[FATAL ERROR] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

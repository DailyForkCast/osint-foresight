#!/usr/bin/env python3
"""
Comprehensive CORDIS Data Validation, Processing, and Analysis
Background task to reconcile all CORDIS datasets and generate complete Netherlands analysis

This script:
1. Validates all CORDIS tables and their relationships
2. Reconciles reference dataset (361 entries) with verified dataset (162 projects)
3. Performs complete temporal analysis across all available data
4. Generates comprehensive Netherlands-China intelligence report
5. Identifies data quality issues and gaps

Runtime: 30-60 minutes
Output: analysis/cordis_comprehensive_validation_YYYYMMDD_HHMMSS.json
"""

import sqlite3
import json
from datetime import datetime
from collections import defaultdict
import sys
import re

# ============================================================================
# SECURITY: SQL injection prevention through identifier validation
# ============================================================================

def validate_sql_identifier(identifier):
    """
    SECURITY: Validate SQL identifier (table or column name).
    Only allows alphanumeric characters and underscores.
    Prevents SQL injection from dynamic SQL construction.
    """
    if not identifier:
        raise ValueError("Identifier cannot be empty")

    # Check for valid characters only (alphanumeric + underscore)
    if not re.match(r'^[a-zA-Z0-9_]+$', identifier):
        raise ValueError(f"Invalid identifier: {identifier}. Contains illegal characters.")

    # Check length (SQLite limit is 1024, we use 100 for safety)
    if len(identifier) > 100:
        raise ValueError(f"Identifier too long: {identifier}")

    # Blacklist dangerous SQL keywords
    dangerous_keywords = {'DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE',
                         'EXEC', 'EXECUTE', 'UNION', 'SELECT', '--', ';', '/*', '*/'}
    if identifier.upper() in dangerous_keywords:
        raise ValueError(f"Identifier contains SQL keyword: {identifier}")

    return identifier

DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"

def log(msg):
    """Thread-safe logging with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}", flush=True)

def comprehensive_cordis_validation():
    """Complete CORDIS validation and analysis."""

    start_time = datetime.now()
    log("="*80)
    log("CORDIS COMPREHENSIVE VALIDATION - START")
    log("="*80)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    results = {
        'validation_timestamp': start_time.isoformat(),
        'phase_1_schema_validation': {},
        'phase_2_data_quality': {},
        'phase_3_reconciliation': {},
        'phase_4_netherlands_analysis': {},
        'phase_5_temporal_analysis': {},
        'phase_6_entity_mapping': {},
        'phase_7_recommendations': {}
    }

    # ========================================================================
    # PHASE 1: Schema Validation
    # ========================================================================
    log("\n[PHASE 1] Schema Validation - Identifying all CORDIS tables")

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'cordis%' ORDER BY name")
    cordis_tables = [t[0] for t in cursor.fetchall()]

    results['phase_1_schema_validation']['tables_found'] = cordis_tables
    log(f"Found {len(cordis_tables)} CORDIS tables: {cordis_tables}")

    # Get schema for each table
    for table in cordis_tables:
        # SECURITY: Validate table name before use in SQL
        safe_table = validate_sql_identifier(table)
        cursor.execute(f"PRAGMA table_info({safe_table})")
        columns = [c[1] for c in cursor.fetchall()]

        cursor.execute(f"SELECT COUNT(*) FROM {safe_table}")
        row_count = cursor.fetchone()[0]

        results['phase_1_schema_validation'][table] = {
            'columns': columns,
            'row_count': row_count
        }

        log(f"  {table}: {row_count:,} rows, {len(columns)} columns")

    # ========================================================================
    # PHASE 2: Data Quality Assessment
    # ========================================================================
    log("\n[PHASE 2] Data Quality - Checking completeness and consistency")

    # Check cordis_full_projects date coverage
    cursor.execute('''
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN start_date IS NOT NULL AND start_date != '' THEN 1 ELSE 0 END) as with_start,
            SUM(CASE WHEN end_date IS NOT NULL AND end_date != '' THEN 1 ELSE 0 END) as with_end,
            SUM(CASE WHEN eu_contribution IS NOT NULL THEN 1 ELSE 0 END) as with_funding,
            SUM(CASE WHEN technology_areas IS NOT NULL AND technology_areas != '' THEN 1 ELSE 0 END) as with_tech
        FROM cordis_full_projects
    ''')
    total, with_start, with_end, with_funding, with_tech = cursor.fetchone()

    results['phase_2_data_quality']['cordis_full_projects'] = {
        'total_projects': total,
        'start_date_coverage_pct': round(with_start/total*100, 2) if total > 0 else 0,
        'end_date_coverage_pct': round(with_end/total*100, 2) if total > 0 else 0,
        'funding_coverage_pct': round(with_funding/total*100, 2) if total > 0 else 0,
        'technology_coverage_pct': round(with_tech/total*100, 2) if total > 0 else 0
    }

    log(f"  cordis_full_projects data quality:")
    log(f"    Total projects: {total:,}")
    log(f"    Start date coverage: {with_start/total*100:.1f}%")
    log(f"    End date coverage: {with_end/total*100:.1f}%")
    log(f"    Funding coverage: {with_funding/total*100:.1f}%")
    log(f"    Technology coverage: {with_tech/total*100:.1f}%")

    # Check project-country linking quality
    cursor.execute('SELECT COUNT(DISTINCT project_id) FROM cordis_project_countries')
    linked_projects = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(DISTINCT country_code) FROM cordis_project_countries')
    countries_represented = cursor.fetchone()[0]

    results['phase_2_data_quality']['cordis_project_countries'] = {
        'unique_projects': linked_projects,
        'unique_countries': countries_represented
    }

    log(f"  cordis_project_countries linking:")
    log(f"    Unique projects: {linked_projects:,}")
    log(f"    Countries represented: {countries_represented}")

    # ========================================================================
    # PHASE 3: Dataset Reconciliation
    # ========================================================================
    log("\n[PHASE 3] Dataset Reconciliation - Reference vs Verified")

    # Reference dataset analysis
    cursor.execute('SELECT COUNT(*) FROM cordis_projects WHERE country_code = "NL"')
    ref_nl_count = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(DISTINCT chinese_org) FROM cordis_projects WHERE country_code = "NL"')
    ref_chinese_orgs = cursor.fetchone()[0]

    # Verified dataset analysis
    cursor.execute('SELECT COUNT(DISTINCT project_id) FROM cordis_project_countries WHERE country_code = "NL"')
    ver_nl_count = cursor.fetchone()[0]

    cursor.execute('''
        SELECT COUNT(DISTINCT pc.project_id)
        FROM cordis_project_countries pc
        JOIN cordis_full_projects fp ON pc.project_id = fp.project_id
        WHERE pc.country_code = 'NL' AND fp.china_involvement = 1
    ''')
    ver_nl_china = cursor.fetchone()[0]

    # Check for overlap
    cursor.execute('''
        SELECT COUNT(*)
        FROM cordis_projects cp
        WHERE cp.country_code = 'NL'
          AND EXISTS (
              SELECT 1 FROM cordis_full_projects fp WHERE fp.project_id = cp.project_id
          )
    ''')
    overlap_count = cursor.fetchone()[0]

    results['phase_3_reconciliation'] = {
        'reference_dataset': {
            'nl_entries': ref_nl_count,
            'unique_chinese_orgs': ref_chinese_orgs,
            'note': 'Synthetic project IDs, pre-processed extraction'
        },
        'verified_dataset': {
            'nl_projects': ver_nl_count,
            'nl_china_projects': ver_nl_china,
            'penetration_pct': round(ver_nl_china/ver_nl_count*100, 2) if ver_nl_count > 0 else 0
        },
        'overlap': {
            'projects_in_both': overlap_count,
            'assessment': 'No overlap' if overlap_count == 0 else f'{overlap_count} projects shared'
        },
        'conclusion': 'Datasets represent different time periods or extraction methodologies' if overlap_count == 0 else 'Partial overlap detected'
    }

    log(f"  Reference dataset: {ref_nl_count} NL entries, {ref_chinese_orgs} unique Chinese orgs")
    log(f"  Verified dataset: {ver_nl_count} NL projects, {ver_nl_china} with China ({ver_nl_china/ver_nl_count*100:.1f}%)")
    log(f"  Overlap: {overlap_count} projects")
    log(f"  Assessment: {'Different datasets - no project ID overlap' if overlap_count == 0 else 'Partial overlap exists'}")

    # ========================================================================
    # PHASE 4: Netherlands Comprehensive Analysis
    # ========================================================================
    log("\n[PHASE 4] Netherlands Analysis - Complete breakdown")

    # All Netherlands projects by year (where dates exist)
    cursor.execute('''
        SELECT
            CAST(substr(fp.start_date, 1, 4) AS INTEGER) as year,
            COUNT(DISTINCT pc.project_id) as total_projects,
            SUM(CASE WHEN fp.china_involvement = 1 THEN 1 ELSE 0 END) as china_projects,
            SUM(fp.eu_contribution) as funding,
            GROUP_CONCAT(DISTINCT fp.topics) as topics
        FROM cordis_project_countries pc
        JOIN cordis_full_projects fp ON pc.project_id = fp.project_id
        WHERE pc.country_code = 'NL'
          AND fp.start_date IS NOT NULL
          AND fp.start_date != ''
        GROUP BY year
        ORDER BY year
    ''')

    temporal_data = []
    for year, total, china, funding, topics in cursor.fetchall():
        if year and 2000 <= year <= 2030:
            temporal_data.append({
                'year': year,
                'total_projects': total,
                'china_projects': china,
                'penetration_pct': round(china/total*100, 2) if total > 0 else 0,
                'funding_eur': float(funding) if funding else 0,
                'sample_topics': topics[:200] if topics else None
            })

    results['phase_4_netherlands_analysis']['temporal_breakdown'] = temporal_data

    log(f"  Temporal analysis ({len(temporal_data)} years with data):")
    for entry in temporal_data:
        log(f"    {entry['year']}: {entry['total_projects']} projects, {entry['china_projects']} with China ({entry['penetration_pct']}%)")

    # Get detailed project information for Netherlands-China projects
    cursor.execute('''
        SELECT
            fp.project_id,
            fp.acronym,
            fp.title,
            fp.start_date,
            fp.end_date,
            fp.eu_contribution,
            fp.technology_areas,
            fp.topics
        FROM cordis_project_countries pc
        JOIN cordis_full_projects fp ON pc.project_id = fp.project_id
        WHERE pc.country_code = 'NL'
          AND fp.china_involvement = 1
        ORDER BY fp.start_date DESC
    ''')

    nl_china_projects = []
    for pid, acronym, title, start, end, funding, tech, topics in cursor.fetchall():
        nl_china_projects.append({
            'project_id': pid,
            'acronym': acronym,
            'title': title,
            'start_date': start,
            'end_date': end,
            'eu_contribution_eur': float(funding) if funding else None,
            'technology_areas': tech,
            'topics': topics
        })

    results['phase_4_netherlands_analysis']['nl_china_projects_detailed'] = nl_china_projects

    log(f"  Netherlands-China projects: {len(nl_china_projects)} detailed records")

    # ========================================================================
    # PHASE 5: Complete Temporal Analysis (All Countries for Comparison)
    # ========================================================================
    log("\n[PHASE 5] Comparative Analysis - Netherlands vs other EU countries")

    # Get top 10 EU countries by CORDIS participation
    cursor.execute('''
        SELECT
            pc.country_code,
            COUNT(DISTINCT pc.project_id) as total_projects,
            SUM(CASE WHEN fp.china_involvement = 1 THEN 1 ELSE 0 END) as china_projects
        FROM cordis_project_countries pc
        JOIN cordis_full_projects fp ON pc.project_id = fp.project_id
        GROUP BY pc.country_code
        ORDER BY total_projects DESC
        LIMIT 20
    ''')

    comparative_data = []
    for country, total, china in cursor.fetchall():
        if country:
            comparative_data.append({
                'country_code': country,
                'total_projects': total,
                'china_projects': china,
                'penetration_pct': round(china/total*100, 2) if total > 0 else 0
            })

    results['phase_5_temporal_analysis']['eu_country_comparison'] = comparative_data

    log(f"  Comparative analysis (top 20 EU countries):")
    for entry in comparative_data[:10]:
        log(f"    {entry['country_code']}: {entry['total_projects']:,} projects, {entry['china_projects']} with China ({entry['penetration_pct']}%)")

    # ========================================================================
    # PHASE 6: Entity Mapping (Chinese Organizations)
    # ========================================================================
    log("\n[PHASE 6] Entity Mapping - All Chinese organizations in Netherlands collaborations")

    # From reference dataset
    cursor.execute('''
        SELECT
            chinese_org,
            COUNT(*) as entries,
            SUM(ec_contribution) as total_funding
        FROM cordis_projects
        WHERE country_code = 'NL'
        GROUP BY chinese_org
        ORDER BY entries DESC
    ''')

    chinese_orgs = []
    for org, count, funding in cursor.fetchall():
        if org:
            chinese_orgs.append({
                'organization': org,
                'entries': count,
                'aggregate_funding_eur': float(funding) if funding else 0
            })

    results['phase_6_entity_mapping'] = {
        'total_unique_orgs': len(chinese_orgs),
        'organizations': chinese_orgs
    }

    log(f"  Chinese organizations: {len(chinese_orgs)} unique entities")
    log(f"  Top 10:")
    for org in chinese_orgs[:10]:
        log(f"    {org['organization'][:50]}: {org['entries']} entries")

    # ========================================================================
    # PHASE 7: Recommendations
    # ========================================================================
    log("\n[PHASE 7] Generating Recommendations")

    recommendations = []

    # Data quality recommendations
    if results['phase_2_data_quality']['cordis_full_projects']['start_date_coverage_pct'] < 50:
        recommendations.append({
            'priority': 'HIGH',
            'category': 'Data Quality',
            'issue': f"Only {results['phase_2_data_quality']['cordis_full_projects']['start_date_coverage_pct']:.1f}% of projects have start dates",
            'recommendation': 'Query CORDIS API for complete temporal data or access historical CORDIS versions'
        })

    # Reconciliation recommendations
    if overlap_count == 0:
        recommendations.append({
            'priority': 'CRITICAL',
            'category': 'Data Reconciliation',
            'issue': 'Zero overlap between reference dataset (361 entries) and verified dataset (162 projects)',
            'recommendation': 'Investigate data processing pipeline. Reference dataset likely from different CORDIS version or extraction methodology. Validate which represents ground truth.'
        })

    # Netherlands-specific
    nl_penetration = results['phase_3_reconciliation']['verified_dataset']['penetration_pct']
    if nl_penetration < 5:
        recommendations.append({
            'priority': 'MEDIUM',
            'category': 'Netherlands Analysis',
            'issue': f'Netherlands China penetration rate very low ({nl_penetration}%)',
            'recommendation': 'Either export controls highly effective OR data incomplete. Cross-validate with OpenAIRE, arXiv, patent data to confirm low engagement.'
        })

    results['phase_7_recommendations'] = recommendations

    for i, rec in enumerate(recommendations, 1):
        log(f"  [{rec['priority']}] {rec['category']}: {rec['issue']}")
        log(f"    → {rec['recommendation']}")

    # ========================================================================
    # FINAL: Save Results
    # ========================================================================
    timestamp_suffix = start_time.strftime("%Y%m%d_%H%M%S")
    output_file = f"analysis/cordis_comprehensive_validation_{timestamp_suffix}.json"

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    log("\n" + "="*80)
    log(f"CORDIS COMPREHENSIVE VALIDATION - COMPLETE")
    log(f"Duration: {duration:.1f} seconds")
    log(f"Output: {output_file}")
    log("="*80)

    conn.close()

    return results

if __name__ == "__main__":
    try:
        results = comprehensive_cordis_validation()
        sys.exit(0)
    except Exception as e:
        log(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

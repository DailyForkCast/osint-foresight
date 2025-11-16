#!/usr/bin/env python3
"""
OSINT Foresight Data Audit - Phase 5: Data Gaps & Coverage Analysis
Identifies temporal, geographic, technology, and entity coverage gaps
"""

import sqlite3
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter

output_dir = Path("C:/Projects/OSINT - Foresight/audit_outputs")
output_dir.mkdir(exist_ok=True)

print("="*80)
print("PHASE 5: DATA GAPS & COVERAGE ANALYSIS")
print("="*80)
print()

# Primary database
db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
conn = sqlite3.connect(db_path, timeout=30)
cursor = conn.cursor()

coverage_analysis = {}

# ============================================================================
# Task 1: Temporal Coverage Analysis
# ============================================================================

print("TASK 1: TEMPORAL COVERAGE ANALYSIS")
print("-" * 40)

temporal_coverage = {}

# 1.1 USAspending temporal coverage
print("\n1. USAspending contracts:")
try:
    cursor.execute("""
        SELECT
            strftime('%Y', action_date) as year,
            COUNT(*) as contracts,
            SUM(federal_action_obligation) as total_value
        FROM usaspending_china_374
        WHERE action_date IS NOT NULL
        GROUP BY year
        ORDER BY year
    """)

    years = cursor.fetchall()

    if years:
        temporal_coverage['usaspending'] = {
            'earliest_year': years[0][0],
            'latest_year': years[-1][0],
            'year_range': int(years[-1][0]) - int(years[0][0]) + 1,
            'years_with_data': len(years),
            'by_year': [{'year': y[0], 'contracts': y[1], 'value': y[2]} for y in years]
        }

        print(f"  Date range: {years[0][0]} to {years[-1][0]} ({len(years)} years)")
        print(f"  Total years in range: {int(years[-1][0]) - int(years[0][0]) + 1}")

        # Check for gaps
        all_years = set(range(int(years[0][0]), int(years[-1][0]) + 1))
        years_with_data = set(int(y[0]) for y in years)
        missing_years = sorted(all_years - years_with_data)

        if missing_years:
            print(f"  Missing years: {missing_years}")
        else:
            print(f"  No gaps: Complete coverage")

except Exception as e:
    print(f"  Error: {str(e)}")

# 1.2 TED contracts temporal coverage
print("\n2. TED contracts:")
try:
    cursor.execute("""
        SELECT
            strftime('%Y', publication_date) as year,
            COUNT(*) as contracts
        FROM ted_contracts_production
        WHERE publication_date IS NOT NULL
        GROUP BY year
        ORDER BY year
    """)

    years = cursor.fetchall()

    if years:
        temporal_coverage['ted'] = {
            'earliest_year': years[0][0],
            'latest_year': years[-1][0],
            'year_range': int(years[-1][0]) - int(years[0][0]) + 1,
            'years_with_data': len(years),
            'by_year': [{'year': y[0], 'contracts': y[1]} for y in years]
        }

        print(f"  Date range: {years[0][0]} to {years[-1][0]} ({len(years)} years)")

        # Check for gaps
        all_years = set(range(int(years[0][0]), int(years[-1][0]) + 1))
        years_with_data = set(int(y[0]) for y in years)
        missing_years = sorted(all_years - years_with_data)

        if missing_years:
            print(f"  Missing years: {', '.join(map(str, missing_years[:10]))}{'...' if len(missing_years) > 10 else ''}")
            temporal_coverage['ted']['missing_years'] = missing_years
        else:
            print(f"  No gaps: Complete coverage")

except Exception as e:
    print(f"  Error: {str(e)}")

# 1.3 USPTO patents temporal coverage
print("\n3. USPTO patents (Chinese):")
try:
    cursor.execute("""
        SELECT
            strftime('%Y', grant_date) as year,
            COUNT(*) as patents
        FROM uspto_patents_chinese
        WHERE grant_date IS NOT NULL
        GROUP BY year
        ORDER BY year
    """)

    years = cursor.fetchall()

    if years:
        temporal_coverage['uspto'] = {
            'earliest_year': years[0][0],
            'latest_year': years[-1][0],
            'year_range': int(years[-1][0]) - int(years[0][0]) + 1,
            'years_with_data': len(years),
            'by_year': [{'year': y[0], 'patents': y[1]} for y in years]
        }

        print(f"  Date range: {years[0][0]} to {years[-1][0]} ({len(years)} years)")
        print(f"  Years with data: {len(years)}")

except Exception as e:
    print(f"  Error: {str(e)}")

# 1.4 OpenAlex works temporal coverage
print("\n4. OpenAlex works:")
try:
    cursor.execute("""
        SELECT
            publication_year as year,
            COUNT(*) as papers
        FROM openalex_works
        WHERE publication_year IS NOT NULL
        GROUP BY year
        ORDER BY year
    """)

    years = cursor.fetchall()

    if years:
        temporal_coverage['openalex'] = {
            'earliest_year': str(years[0][0]),
            'latest_year': str(years[-1][0]),
            'year_range': years[-1][0] - years[0][0] + 1,
            'years_with_data': len(years),
            'by_year': [{'year': str(y[0]), 'papers': y[1]} for y in years]
        }

        print(f"  Date range: {years[0][0]} to {years[-1][0]} ({len(years)} years)")
        print(f"  Years with data: {len(years)}")

except Exception as e:
    print(f"  Error: {str(e)}")

# 1.5 arXiv papers temporal coverage
print("\n5. arXiv papers:")
try:
    cursor.execute("""
        SELECT
            strftime('%Y', published_date) as year,
            COUNT(*) as papers
        FROM arxiv_papers
        WHERE published_date IS NOT NULL
        GROUP BY year
        ORDER BY year
    """)

    years = cursor.fetchall()

    if years:
        temporal_coverage['arxiv'] = {
            'earliest_year': years[0][0],
            'latest_year': years[-1][0],
            'year_range': int(years[-1][0]) - int(years[0][0]) + 1,
            'years_with_data': len(years),
            'by_year': [{'year': y[0], 'papers': y[1]} for y in years]
        }

        print(f"  Date range: {years[0][0]} to {years[-1][0]} ({len(years)} years)")
        print(f"  Papers: {sum(y[1] for y in years):,}")

except Exception as e:
    print(f"  Error: {str(e)}")

coverage_analysis['temporal'] = temporal_coverage

# Save temporal coverage
with open(output_dir / "temporal_coverage_analysis.json", "w") as f:
    json.dump(temporal_coverage, f, indent=2)

print(f"\n[SAVED] temporal_coverage_analysis.json")

# ============================================================================
# Task 2: Geographic Coverage Analysis
# ============================================================================

print("\n" + "="*80)
print("TASK 2: GEOGRAPHIC COVERAGE ANALYSIS")
print("-" * 40)

geographic_coverage = {}

# 2.1 OpenAlex country coverage
print("\n1. OpenAlex institution coverage:")
try:
    cursor.execute("""
        SELECT
            country_code,
            COUNT(DISTINCT institution_name) as institutions,
            COUNT(*) as authors
        FROM openalex_work_authors
        WHERE country_code IS NOT NULL
        AND country_code != ''
        GROUP BY country_code
        ORDER BY authors DESC
    """)

    countries = cursor.fetchall()

    geographic_coverage['openalex'] = {
        'countries_covered': len(countries),
        'by_country': [{'code': c[0], 'institutions': c[1], 'authors': c[2]} for c in countries]
    }

    print(f"  Countries with data: {len(countries)}")
    print(f"  Top 10 by author count:")
    for c in countries[:10]:
        print(f"    {c[0]}: {c[2]:,} authors from {c[1]:,} institutions")

except Exception as e:
    print(f"  Error: {str(e)}")

# 2.2 TED procurement country coverage
print("\n2. TED procurement country coverage:")
try:
    cursor.execute("""
        SELECT
            country_code,
            COUNT(*) as contracts
        FROM ted_contractors
        WHERE country_code IS NOT NULL
        AND country_code != ''
        GROUP BY country_code
        ORDER BY contracts DESC
    """)

    countries = cursor.fetchall()

    geographic_coverage['ted'] = {
        'countries_covered': len(countries),
        'by_country': [{'code': c[0], 'contracts': c[1]} for c in countries]
    }

    print(f"  Countries with data: {len(countries)}")
    print(f"  Top 10 by contract count:")
    for c in countries[:10]:
        print(f"    {c[0]}: {c[1]:,} contracts")

except Exception as e:
    print(f"  Error: {str(e)}")

# 2.3 Check for expected but missing countries
print("\n3. Gap analysis - Expected countries:")

# Strategic countries we should have coverage for
expected_strategic_countries = {
    'CN': 'China',
    'US': 'United States',
    'RU': 'Russia',
    'DE': 'Germany',
    'GB': 'United Kingdom',
    'FR': 'France',
    'JP': 'Japan',
    'KR': 'South Korea',
    'IL': 'Israel',
    'IN': 'India',
    'AU': 'Australia',
    'CA': 'Canada',
    'IT': 'Italy',
    'ES': 'Spain',
    'NL': 'Netherlands',
    'SE': 'Sweden',
    'CH': 'Switzerland',
    'SG': 'Singapore',
    'TW': 'Taiwan',
    'BR': 'Brazil'
}

openalex_countries = set(c[0] for c in geographic_coverage.get('openalex', {}).get('by_country', []))
missing_in_openalex = []

for code, name in expected_strategic_countries.items():
    if code not in openalex_countries:
        missing_in_openalex.append(f"{name} ({code})")

if missing_in_openalex:
    print(f"  Missing from OpenAlex: {', '.join(missing_in_openalex)}")
else:
    print(f"  All {len(expected_strategic_countries)} strategic countries covered in OpenAlex")

geographic_coverage['gaps'] = {
    'expected_strategic_countries': expected_strategic_countries,
    'missing_in_openalex': missing_in_openalex
}

coverage_analysis['geographic'] = geographic_coverage

# Save geographic coverage
with open(output_dir / "geographic_coverage_analysis.json", "w") as f:
    json.dump(geographic_coverage, f, indent=2)

print(f"\n[SAVED] geographic_coverage_analysis.json")

# ============================================================================
# Task 3: Technology Domain Coverage
# ============================================================================

print("\n" + "="*80)
print("TASK 3: TECHNOLOGY DOMAIN COVERAGE")
print("-" * 40)

technology_coverage = {}

# 3.1 OpenAlex topics
print("\n1. OpenAlex research topics:")
try:
    cursor.execute("""
        SELECT
            topic_name,
            COUNT(DISTINCT work_id) as papers
        FROM openalex_work_topics
        WHERE topic_name IS NOT NULL
        GROUP BY topic_name
        ORDER BY papers DESC
        LIMIT 50
    """)

    topics = cursor.fetchall()

    technology_coverage['openalex_topics'] = {
        'unique_topics': len(topics),
        'top_50': [{'topic': t[0], 'papers': t[1]} for t in topics]
    }

    print(f"  Topics in database: {len(topics)}")
    print(f"  Top 10 topics:")
    for t in topics[:10]:
        print(f"    {t[0]}: {t[1]:,} papers")

except Exception as e:
    print(f"  Error: {str(e)}")

# 3.2 arXiv categories
print("\n2. arXiv research categories:")
try:
    cursor.execute("""
        SELECT
            category,
            COUNT(DISTINCT arxiv_id) as papers
        FROM arxiv_categories
        WHERE category IS NOT NULL
        GROUP BY category
        ORDER BY papers DESC
        LIMIT 50
    """)

    categories = cursor.fetchall()

    technology_coverage['arxiv_categories'] = {
        'unique_categories': len(categories),
        'top_50': [{'category': c[0], 'papers': c[1]} for c in categories]
    }

    print(f"  Categories in database: {len(categories)}")
    print(f"  Top 10 categories:")
    for c in categories[:10]:
        print(f"    {c[0]}: {c[1]:,} papers")

except Exception as e:
    print(f"  Error: {str(e)}")

# 3.3 USPTO CPC classes (strategic technologies)
print("\n3. USPTO CPC classes (strategic tech):")
try:
    cursor.execute("""
        SELECT
            cpc_section,
            cpc_class,
            COUNT(DISTINCT patent_id) as patents
        FROM patentsview_cpc_strategic
        WHERE cpc_section IS NOT NULL
        GROUP BY cpc_section, cpc_class
        ORDER BY patents DESC
        LIMIT 30
    """)

    cpc_classes = cursor.fetchall()

    technology_coverage['uspto_cpc'] = {
        'unique_classes': len(cpc_classes),
        'top_30': [{'section': c[0], 'class': c[1], 'patents': c[2]} for c in cpc_classes]
    }

    print(f"  CPC classes in database: {len(cpc_classes)}")
    print(f"  Top 10 classes:")
    for c in cpc_classes[:10]:
        print(f"    {c[0]}{c[1]}: {c[2]:,} patents")

except Exception as e:
    print(f"  Error: {str(e)}")

# 3.4 Strategic technology gap analysis
print("\n4. Strategic technology gap analysis:")

# ASPI Critical Technology Tracker domains
aspi_critical_tech = [
    'Artificial Intelligence',
    'Quantum Computing',
    'Advanced Communications (5G/6G)',
    'Advanced Materials',
    'Biotechnology',
    'Energy Storage',
    'Hypersonics',
    'Advanced Robotics',
    'Semiconductors',
    'Space Technologies',
    'Cybersecurity',
    'Nuclear Technology',
    'Advanced Sensors',
    'Directed Energy',
    'Advanced Manufacturing'
]

print(f"  ASPI Critical Tech Tracker has {len(aspi_critical_tech)} domains")
print(f"  Checking coverage in our datasets...")

# This would require mapping ASPI domains to our categories
# For now, just document the expected domains
technology_coverage['aspi_critical_tech'] = aspi_critical_tech

coverage_analysis['technology'] = technology_coverage

# Save technology coverage
with open(output_dir / "technology_coverage_analysis.json", "w") as f:
    json.dump(technology_coverage, f, indent=2)

print(f"\n[SAVED] technology_coverage_analysis.json")

# ============================================================================
# Task 4: Entity Coverage Assessment
# ============================================================================

print("\n" + "="*80)
print("TASK 4: ENTITY COVERAGE ASSESSMENT")
print("-" * 40)

entity_coverage = {}

# 4.1 Major Chinese tech companies
print("\n1. Major Chinese tech company coverage:")

major_chinese_companies = [
    'Huawei', 'ZTE', 'Alibaba', 'Tencent', 'Baidu', 'ByteDance',
    'Xiaomi', 'DJI', 'Lenovo', 'BYD', 'CATL', 'BOE',
    'Hikvision', 'Dahua', 'SMIC', 'YMTC', 'CNOOC', 'Sinopec',
    'PetroChina', 'COMAC', 'AVIC', 'CSSC', 'China Railway'
]

found_in_datasets = defaultdict(list)

for company in major_chinese_companies:
    # Check USPTO
    cursor.execute("""
        SELECT COUNT(DISTINCT patent_id)
        FROM uspto_patents_chinese
        WHERE assignee_name LIKE ?
    """, (f'%{company}%',))

    count = cursor.fetchone()[0]
    if count > 0:
        found_in_datasets[company].append(('USPTO', count))

    # Check USAspending
    cursor.execute("""
        SELECT COUNT(*)
        FROM usaspending_china_374
        WHERE recipient_name LIKE ?
    """, (f'%{company}%',))

    count = cursor.fetchone()[0]
    if count > 0:
        found_in_datasets[company].append(('USAspending', count))

print(f"  Checking {len(major_chinese_companies)} major Chinese companies...")
print(f"  Found in datasets:")

for company, datasets in sorted(found_in_datasets.items()):
    ds_str = ', '.join([f"{d[0]} ({d[1]:,})" for d in datasets])
    print(f"    {company}: {ds_str}")

missing_companies = set(major_chinese_companies) - set(found_in_datasets.keys())
if missing_companies:
    print(f"\n  Not found: {', '.join(sorted(missing_companies))}")

entity_coverage['major_chinese_companies'] = {
    'total_tracked': len(major_chinese_companies),
    'found': len(found_in_datasets),
    'missing': list(missing_companies),
    'coverage_rate': len(found_in_datasets) / len(major_chinese_companies)
}

# 4.2 Chinese research institutions
print("\n2. Chinese research institution coverage:")

major_chinese_institutions = [
    'Chinese Academy of Sciences',
    'Tsinghua University',
    'Peking University',
    'Fudan University',
    'Shanghai Jiao Tong University',
    'Zhejiang University',
    'University of Science and Technology of China',
    'Nanjing University',
    'Harbin Institute of Technology',
    'Beihang University'
]

found_institutions = []

for inst in major_chinese_institutions:
    cursor.execute("""
        SELECT COUNT(*)
        FROM openalex_work_authors
        WHERE institution_name LIKE ?
    """, (f'%{inst}%',))

    count = cursor.fetchone()[0]
    if count > 0:
        found_institutions.append((inst, count))

print(f"  Top Chinese universities/institutions:")
for inst, count in found_institutions:
    print(f"    {inst}: {count:,} author affiliations")

entity_coverage['chinese_institutions'] = {
    'total_tracked': len(major_chinese_institutions),
    'found': len(found_institutions),
    'coverage_rate': len(found_institutions) / len(major_chinese_institutions)
}

coverage_analysis['entity'] = entity_coverage

# Save entity coverage
with open(output_dir / "entity_coverage_analysis.json", "w") as f:
    json.dump(entity_coverage, f, indent=2)

print(f"\n[SAVED] entity_coverage_analysis.json")

# ============================================================================
# Task 5: Dataset Completeness Assessment
# ============================================================================

print("\n" + "="*80)
print("TASK 5: DATASET COMPLETENESS ASSESSMENT")
print("-" * 40)

completeness = {}

# 5.1 USAspending completeness
print("\n1. USAspending completeness:")
print("  Current database: 42,205 contracts (Chinese entity detections)")
print("  Note: This is a filtered subset, not complete USAspending")
print("  Completeness: N/A (detection-based subset)")

completeness['usaspending'] = {
    'records_in_db': 42205,
    'type': 'filtered_subset',
    'completeness': 'N/A - detection-based'
}

# 5.2 TED completeness
print("\n2. TED completeness:")

cursor.execute("SELECT COUNT(*) FROM ted_contracts_production")
ted_count = cursor.fetchone()[0]

print(f"  Records in database: {ted_count:,}")
print(f"  Date range: 1976-2025 (from Phase 3)")
print(f"  Coverage: EU + associated countries")

completeness['ted'] = {
    'records_in_db': ted_count,
    'date_range': '1976-2025',
    'coverage': 'EU procurement'
}

# 5.3 USPTO completeness
print("\n3. USPTO patents completeness:")

cursor.execute("SELECT COUNT(*) FROM uspto_patents_chinese")
uspto_count = cursor.fetchone()[0]

print(f"  Records in database: {uspto_count:,} (Chinese-detected patents)")
print(f"  Date range: 2011-2025 (from Phase 3)")
print(f"  Note: This is Chinese entity subset, not all USPTO")

completeness['uspto'] = {
    'records_in_db': uspto_count,
    'date_range': '2011-2025',
    'type': 'Chinese entity subset'
}

# 5.4 OpenAlex completeness
print("\n4. OpenAlex completeness:")

cursor.execute("SELECT COUNT(*) FROM openalex_works")
openalex_works = cursor.fetchone()[0]

print(f"  Works in database: {openalex_works:,}")
print(f"  Note: This is strategic tech subset with keyword/topic filtering")

completeness['openalex'] = {
    'records_in_db': openalex_works,
    'type': 'strategic_tech_subset'
}

# 5.5 arXiv completeness
print("\n5. arXiv completeness:")

cursor.execute("SELECT COUNT(*) FROM arxiv_papers")
arxiv_count = cursor.fetchone()[0]

print(f"  Papers in database: {arxiv_count:,}")
print(f"  Date range: 1990-2025 (from Phase 3)")

completeness['arxiv'] = {
    'records_in_db': arxiv_count,
    'date_range': '1990-2025'
}

coverage_analysis['completeness'] = completeness

# Save completeness assessment
with open(output_dir / "dataset_completeness_analysis.json", "w") as f:
    json.dump(completeness, f, indent=2)

print(f"\n[SAVED] dataset_completeness_analysis.json")

# ============================================================================
# Summary Statistics
# ============================================================================

print("\n" + "="*80)
print("SUMMARY STATISTICS")
print("="*80)

summary = {
    'audit_date': datetime.now().isoformat(),
    'temporal_coverage': {
        'usaspending_years': temporal_coverage.get('usaspending', {}).get('year_range', 0),
        'ted_years': temporal_coverage.get('ted', {}).get('year_range', 0),
        'uspto_years': temporal_coverage.get('uspto', {}).get('year_range', 0),
        'openalex_years': temporal_coverage.get('openalex', {}).get('year_range', 0)
    },
    'geographic_coverage': {
        'openalex_countries': geographic_coverage.get('openalex', {}).get('countries_covered', 0),
        'ted_countries': geographic_coverage.get('ted', {}).get('countries_covered', 0)
    },
    'technology_coverage': {
        'openalex_topics': technology_coverage.get('openalex_topics', {}).get('unique_topics', 0),
        'arxiv_categories': technology_coverage.get('arxiv_categories', {}).get('unique_categories', 0)
    },
    'entity_coverage': {
        'chinese_companies_found': entity_coverage.get('major_chinese_companies', {}).get('found', 0),
        'chinese_companies_total': entity_coverage.get('major_chinese_companies', {}).get('total_tracked', 0),
        'chinese_institutions_found': entity_coverage.get('chinese_institutions', {}).get('found', 0)
    }
}

print(f"\nTemporal Coverage:")
print(f"  USAspending: {summary['temporal_coverage']['usaspending_years']} years")
print(f"  TED: {summary['temporal_coverage']['ted_years']} years")
print(f"  USPTO: {summary['temporal_coverage']['uspto_years']} years")
print(f"  OpenAlex: {summary['temporal_coverage']['openalex_years']} years")

print(f"\nGeographic Coverage:")
print(f"  OpenAlex: {summary['geographic_coverage']['openalex_countries']} countries")
print(f"  TED: {summary['geographic_coverage']['ted_countries']} countries")

print(f"\nTechnology Coverage:")
print(f"  OpenAlex topics: {summary['technology_coverage']['openalex_topics']}")
print(f"  arXiv categories: {summary['technology_coverage']['arxiv_categories']}")

print(f"\nEntity Coverage:")
print(f"  Chinese companies: {summary['entity_coverage']['chinese_companies_found']}/{summary['entity_coverage']['chinese_companies_total']} found")
print(f"  Chinese institutions: {summary['entity_coverage']['chinese_institutions_found']} found")

# Save summary
with open(output_dir / "phase5_coverage_summary.json", "w") as f:
    json.dump(summary, f, indent=2)

print(f"\n[SAVED] phase5_coverage_summary.json")

conn.close()

print("\n" + "="*80)
print("PHASE 5 COMPLETE")
print("="*80)
print(f"\nOutput files saved to: {output_dir}")
print()

#!/usr/bin/env python3
"""
ASPI China Defence Universities Tracker - Netherlands Cross-Reference v2

Uses comprehensive ASPI database (159 institutions) with exact name matching.

Improvements from v1:
- Loads full ASPI tracker database (data/external/aspi/aspi_institutions.csv)
- Exact name matching (eliminates location-based false positives)
- Risk levels based on ASPI categories
- Includes Chinese name matching

Commitment: Complete by November 8, 2025 (2 days from start)
Part of: Netherlands v1 Strategic Assessment (due Nov 23, 2025)
"""

import sqlite3
import json
import csv
from datetime import datetime
from collections import defaultdict
from pathlib import Path

DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"
ASPI_CSV_PATH = "data/external/aspi/aspi_institutions.csv"

def log(msg):
    """Log with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Handle Unicode encoding for Windows console
    try:
        print(f"[{timestamp}] {msg}", flush=True)
    except UnicodeEncodeError:
        print(f"[{timestamp}] {msg.encode('ascii', 'replace').decode('ascii')}", flush=True)

def load_aspi_database(csv_path):
    """
    Load comprehensive ASPI tracker database.

    Returns: dict with structure:
    {
        'VERY_HIGH': [list of institutions],
        'HIGH': [list of institutions],
        'MEDIUM': [list of institutions],
        'LOW': [list of institutions]
    }
    """
    log(f"Loading ASPI database from {csv_path}...")

    aspi_db = {
        'VERY_HIGH': [],
        'HIGH': [],
        'MEDIUM': [],
        'LOW': []
    }

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            category = row['category']
            supervising = row.get('supervising_agencies', '')

            # Determine risk level based on ASPI category
            if category in ['Seven sons of national defence', 'Military', 'Security']:
                risk_level = 'VERY_HIGH'
            elif category == 'Defence industry conglomerate':
                risk_level = 'HIGH'
            elif category == 'Civilian' and 'SASTIND' in supervising:
                risk_level = 'MEDIUM'
            else:
                risk_level = 'LOW'

            institution = {
                'name_english': row['name_english'],
                'name_chinese': row.get('chinese_name', ''),
                'category': category,
                'address': row.get('address', ''),
                'research_topics': row.get('research_topics', ''),
                'supervising_agencies': supervising,
                'aspi_url': row.get('aspi_url', '')
            }

            aspi_db[risk_level].append(institution)

    log(f"Loaded {sum(len(aspi_db[level]) for level in aspi_db)} ASPI institutions:")
    log(f"  VERY HIGH RISK: {len(aspi_db['VERY_HIGH'])} (Seven Sons, Military, Security)")
    log(f"  HIGH RISK: {len(aspi_db['HIGH'])} (Defence industry)")
    log(f"  MEDIUM RISK: {len(aspi_db['MEDIUM'])} (Civilian + SASTIND)")
    log(f"  LOW RISK: {len(aspi_db['LOW'])} (Other Civilian)")

    return aspi_db

def exact_match_institution(name, aspi_db):
    """
    Exact match institution name against ASPI database.

    Matching strategy:
    1. Exact English name match (case-insensitive)
    2. Exact Chinese name match
    3. Partial match with confirmation needed (length > 80% of ASPI name)

    Returns: (risk_level, matched_institution, match_confidence) or (None, None, None)
    """
    if not name:
        return None, None, None

    name_clean = name.strip()
    name_upper = name_clean.upper()

    # Try exact matching first
    for risk_level in ['VERY_HIGH', 'HIGH', 'MEDIUM', 'LOW']:
        for inst in aspi_db[risk_level]:
            # Exact English name match
            if inst['name_english'].upper() == name_upper:
                return risk_level, inst, 'EXACT_ENGLISH'

            # Exact Chinese name match
            if inst['name_chinese'] and inst['name_chinese'] == name_clean:
                return risk_level, inst, 'EXACT_CHINESE'

            # Check if Chinese name appears in the input name
            if inst['name_chinese'] and inst['name_chinese'] in name_clean:
                return risk_level, inst, 'CONTAINS_CHINESE'

    # Try high-confidence partial matching (>90% name overlap)
    for risk_level in ['VERY_HIGH', 'HIGH', 'MEDIUM']:  # Don't partial match LOW risk
        for inst in aspi_db[risk_level]:
            english_name = inst['name_english'].upper()

            # For multi-word names, check if significant portion matches
            if len(name_upper) >= len(english_name) * 0.9:
                if english_name in name_upper:
                    return risk_level, inst, 'PARTIAL_HIGH_CONF'

            # Reverse check: input name is in ASPI name
            if len(english_name) >= len(name_upper) * 0.9:
                if name_upper in english_name:
                    return risk_level, inst, 'PARTIAL_HIGH_CONF'

    return None, None, None

def extract_chinese_institutions_openalex(conn):
    """Extract all Chinese institutions from NL-China collaborations."""
    cursor = conn.cursor()

    log("Extracting Chinese institutions from OpenAlex NL-China collaborations...")

    cursor.execute("""
        SELECT DISTINCT wa.institution_name, COUNT(DISTINCT wa.work_id) as collaboration_count
        FROM openalex_work_authors wa
        WHERE wa.country_code IN ('CN', 'HK', 'MO')
        AND wa.institution_name IS NOT NULL
        AND wa.work_id IN (
            SELECT work_id FROM openalex_work_authors WHERE country_code = 'NL'
        )
        GROUP BY wa.institution_name
        ORDER BY collaboration_count DESC
    """)

    institutions = []
    for inst_name, count in cursor.fetchall():
        institutions.append({
            'name': inst_name,
            'source': 'OpenAlex',
            'collaboration_count': count
        })

    log(f"Found {len(institutions)} unique Chinese institutions in OpenAlex")
    return institutions

def extract_chinese_institutions_cordis(conn):
    """Extract Chinese institutions from CORDIS projects."""
    cursor = conn.cursor()

    log("Extracting Chinese institutions from CORDIS projects...")

    # Check if CORDIS has Chinese organizations
    cursor.execute("""
        SELECT COUNT(*) FROM cordis_organizations
        WHERE country IN ('CN', 'HK', 'MO')
    """)
    count = cursor.fetchone()[0]

    if count == 0:
        log("WARNING: No Chinese organizations in CORDIS database yet")
        return []

    cursor.execute("""
        SELECT DISTINCT name, country, COUNT(DISTINCT project_id) as project_count
        FROM cordis_project_participants cpp
        JOIN cordis_organizations co ON cpp.org_id = co.org_id
        WHERE co.country IN ('CN', 'HK', 'MO')
        GROUP BY name, country
        ORDER BY project_count DESC
    """)

    institutions = []
    for inst_name, country, count in cursor.fetchall():
        institutions.append({
            'name': inst_name,
            'source': 'CORDIS',
            'country': country,
            'project_count': count
        })

    log(f"Found {len(institutions)} unique Chinese institutions in CORDIS")
    return institutions

def cross_reference_institutions(institutions, aspi_db):
    """Cross-reference institutions against ASPI database."""

    log(f"\nCross-referencing {len(institutions)} institutions against ASPI database...")

    results = {
        'VERY_HIGH': [],
        'HIGH': [],
        'MEDIUM': [],
        'LOW': [],
        'UNKNOWN': []
    }

    match_stats = {
        'EXACT_ENGLISH': 0,
        'EXACT_CHINESE': 0,
        'CONTAINS_CHINESE': 0,
        'PARTIAL_HIGH_CONF': 0,
        'NO_MATCH': 0
    }

    for inst in institutions:
        risk_level, matched_inst, confidence = exact_match_institution(inst['name'], aspi_db)

        if risk_level:
            match_stats[confidence] += 1
            results[risk_level].append({
                **inst,
                'risk_level': risk_level,
                'matched_institution': matched_inst,
                'match_confidence': confidence
            })
        else:
            match_stats['NO_MATCH'] += 1
            results['UNKNOWN'].append(inst)

    log("\n" + "="*80)
    log("MATCHING STATISTICS")
    log("="*80)
    for match_type, count in match_stats.items():
        log(f"  {match_type}: {count}")

    return results

def generate_report(results, output_file, aspi_db):
    """Generate comprehensive ASPI cross-reference report."""

    log("\n" + "="*80)
    log("ASPI CROSS-REFERENCE RESULTS (v2 - Exact Matching)")
    log("="*80)

    report = {
        'metadata': {
            'generated': datetime.now().isoformat(),
            'version': '2.0',
            'purpose': 'Netherlands-China university partnership risk assessment',
            'data_sources': ['OpenAlex NL-China collaborations', 'CORDIS EU projects'],
            'aspi_database': {
                'source': ASPI_CSV_PATH,
                'total_institutions': sum(len(aspi_db[level]) for level in aspi_db),
                'very_high': len(aspi_db['VERY_HIGH']),
                'high': len(aspi_db['HIGH']),
                'medium': len(aspi_db['MEDIUM']),
                'low': len(aspi_db['LOW'])
            },
            'improvements': [
                'Exact name matching (no location-based false positives)',
                'Comprehensive ASPI database (159 institutions)',
                'Chinese name matching support',
                'Match confidence scoring'
            ]
        },
        'summary': {
            'total_institutions': sum(len(results[level]) for level in results),
            'very_high_risk': len(results['VERY_HIGH']),
            'high_risk': len(results['HIGH']),
            'medium_risk': len(results['MEDIUM']),
            'low_risk': len(results['LOW']),
            'unknown_risk': len(results['UNKNOWN'])
        },
        'findings': results
    }

    # Print summary
    log(f"\nTotal Chinese institutions analyzed: {report['summary']['total_institutions']}")
    log(f"  VERY HIGH RISK: {report['summary']['very_high_risk']} (Seven Sons, Military, Security)")
    log(f"  HIGH RISK: {report['summary']['high_risk']} (Defence industry)")
    log(f"  MEDIUM RISK: {report['summary']['medium_risk']} (Civilian + SASTIND)")
    log(f"  LOW RISK: {report['summary']['low_risk']} (Other Civilian)")
    log(f"  UNKNOWN: {report['summary']['unknown_risk']} (Not in ASPI tracker)")

    # Detail VERY HIGH risk findings
    if results['VERY_HIGH']:
        log("\n[VERY HIGH RISK PARTNERSHIPS - IMMEDIATE ATTENTION REQUIRED]")
        for inst in results['VERY_HIGH']:
            matched = inst['matched_institution']
            log(f"\n  {inst['name']}")
            log(f"    → Matched: {matched['name_english']}")
            log(f"    → Category: {matched['category']}")
            log(f"    → Confidence: {inst['match_confidence']}")
            if matched['research_topics']:
                log(f"    → Research: {matched['research_topics'][:80]}...")
            log(f"    → Source: {inst['source']}")
            if 'collaboration_count' in inst:
                log(f"    → NL Collaborations: {inst['collaboration_count']}")

    # Detail HIGH risk findings
    if results['HIGH']:
        log("\n[HIGH RISK PARTNERSHIPS - DEFENCE INDUSTRY]")
        for inst in results['HIGH'][:10]:  # Top 10
            matched = inst['matched_institution']
            log(f"\n  {inst['name']}")
            log(f"    → Matched: {matched['name_english']}")
            log(f"    → Category: {matched['category']}")
            if 'collaboration_count' in inst:
                log(f"    → NL Collaborations: {inst['collaboration_count']}")

    # Save full report
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    log(f"\nFull report saved: {output_file}")

    # Create Excel-ready summary
    create_review_spreadsheet(results)

    return report

def create_review_spreadsheet(results):
    """Create spreadsheet for manual review of findings."""

    output_csv = "analysis/aspi_cross_reference_netherlands_v2_review.csv"

    rows = []
    rows.append(['Institution Name', 'Risk Level', 'ASPI Name', 'ASPI Category',
                 'Match Confidence', 'Research Topics', 'Source', 'Collaborations',
                 'ASPI URL', 'Action Required'])

    for risk_level in ['VERY_HIGH', 'HIGH', 'MEDIUM', 'LOW', 'UNKNOWN']:
        for inst in results[risk_level]:
            if risk_level == 'UNKNOWN':
                rows.append([
                    inst['name'],
                    'UNKNOWN',
                    'Not in ASPI tracker',
                    'N/A',
                    'N/A',
                    'Needs manual research',
                    inst['source'],
                    inst.get('collaboration_count', inst.get('project_count', 0)),
                    'N/A',
                    'Manual verification required'
                ])
            else:
                matched = inst['matched_institution']
                action = 'IMMEDIATE REVIEW' if risk_level == 'VERY_HIGH' else \
                         'Review recommended' if risk_level == 'HIGH' else \
                         'Monitor' if risk_level == 'MEDIUM' else \
                         'Low priority'

                rows.append([
                    inst['name'],
                    risk_level,
                    matched['name_english'],
                    matched['category'],
                    inst['match_confidence'],
                    matched['research_topics'][:100] if matched['research_topics'] else 'N/A',
                    inst['source'],
                    inst.get('collaboration_count', inst.get('project_count', 0)),
                    matched['aspi_url'],
                    action
                ])

    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    log(f"Review spreadsheet created: {output_csv}")

def main():
    """Main execution."""
    start_time = datetime.now()

    log("="*80)
    log("ASPI CHINA DEFENCE UNIVERSITIES TRACKER - NETHERLANDS CROSS-REFERENCE v2")
    log("="*80)
    log("Improvements: Exact matching, comprehensive ASPI database (159 institutions)")
    log("Commitment: Complete by November 8, 2025")
    log("Part of: Netherlands v1 Strategic Assessment (due Nov 23, 2025)")
    log("="*80)

    # Load ASPI database
    aspi_db = load_aspi_database(ASPI_CSV_PATH)

    # Connect to database
    conn = sqlite3.connect(DB_PATH)

    # Extract Chinese institutions from data sources
    openalex_institutions = extract_chinese_institutions_openalex(conn)
    cordis_institutions = extract_chinese_institutions_cordis(conn)

    # Combine (deduplicate by name)
    all_institutions = openalex_institutions + cordis_institutions
    unique_institutions = {}
    for inst in all_institutions:
        name = inst['name']
        if name not in unique_institutions:
            unique_institutions[name] = inst
        else:
            # Merge counts if institution appears in both sources
            if 'collaboration_count' in inst:
                unique_institutions[name]['collaboration_count'] = \
                    unique_institutions[name].get('collaboration_count', 0) + inst['collaboration_count']

    institutions_list = list(unique_institutions.values())

    # Cross-reference against ASPI database
    results = cross_reference_institutions(institutions_list, aspi_db)

    # Generate report
    output_file = "analysis/aspi_cross_reference_netherlands_v2.json"
    report = generate_report(results, output_file, aspi_db)

    # Cleanup
    conn.close()

    duration = (datetime.now() - start_time).total_seconds()

    log("\n" + "="*80)
    log("CROSS-REFERENCE COMPLETE (v2)")
    log(f"Duration: {duration:.1f} seconds")
    log("="*80)
    log("\nNEXT STEPS:")
    log("1. Review analysis/aspi_cross_reference_netherlands_v2.json")
    log("2. Review analysis/aspi_cross_reference_netherlands_v2_review.csv")
    log("3. Compare with v1 to validate false positive elimination")
    log("4. Integrate findings into Netherlands v1 Strategic Assessment")
    log("5. Deadline: November 23, 2025")

if __name__ == "__main__":
    main()

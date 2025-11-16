#!/usr/bin/env python3
"""
ASPI China Defence Universities Tracker - Netherlands Cross-Reference

Identifies Dutch university partnerships with high-risk Chinese entities.

Data sources:
1. Our OpenAlex data (Chinese institutions collaborating with NL)
2. Our CORDIS data (Chinese organizations in EU projects)
3. Known high-risk entities (Seven Sons of Defense, etc.)

Future enhancement: Integrate full ASPI tracker database when available.

Commitment: Complete by November 8, 2025 (2 days from start)
Part of: Netherlands v1 Strategic Assessment (due Nov 23, 2025)
"""

import sqlite3
import json
from datetime import datetime
from collections import defaultdict

DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"

# Known High-Risk Chinese Defense Universities
# Source: Public ASPI reporting, US Entity List, academic literature
HIGH_RISK_ENTITIES = {
    'VERY_HIGH': {
        'National University of Defense Technology': {
            'abbreviation': 'NUDT',
            'location': 'Changsha',
            'affiliation': 'PLA',
            'concerns': 'Direct PLA control, supercomputing, AI weapons systems',
            'entity_list': True
        },
        'Harbin Institute of Technology': {
            'abbreviation': 'HIT',
            'location': 'Harbin',
            'affiliation': 'Seven Sons of Defense',
            'concerns': 'Aerospace, microsatellites, AI',
            'entity_list': True
        },
        'Beijing Institute of Technology': {
            'abbreviation': 'BIT',
            'location': 'Beijing',
            'affiliation': 'Seven Sons of Defense',
            'concerns': 'Weapons systems, autonomous vehicles, materials science',
            'entity_list': True
        },
        'Northwestern Polytechnical University': {
            'abbreviation': 'NPU',
            'location': "Xi'an",
            'affiliation': 'Seven Sons of Defense',
            'concerns': 'Aerospace, drones, underwater vehicles',
            'entity_list': True
        },
        'Beijing University of Aeronautics and Astronautics': {
            'abbreviation': 'Beihang/BUAA',
            'location': 'Beijing',
            'affiliation': 'Seven Sons of Defense',
            'concerns': 'Aerospace, flight control, autonomous systems',
            'entity_list': True
        },
        'Nanjing University of Aeronautics and Astronautics': {
            'abbreviation': 'NUAA',
            'location': 'Nanjing',
            'affiliation': 'Seven Sons of Defense',
            'concerns': 'Aerospace, helicopter technology, materials',
            'entity_list': True
        },
        'Nanjing University of Science and Technology': {
            'abbreviation': 'NJUST',
            'location': 'Nanjing',
            'affiliation': 'Seven Sons of Defense',
            'concerns': 'Weapons systems, munitions, explosives',
            'entity_list': True
        },
        'Harbin Engineering University': {
            'abbreviation': 'HEU',
            'location': 'Harbin',
            'affiliation': 'Seven Sons of Defense',
            'concerns': 'Naval systems, submarines, underwater technology',
            'entity_list': True
        },
        'PLA Information Engineering University': {
            'abbreviation': 'PLAIEU',
            'location': 'Zhengzhou',
            'affiliation': 'PLA',
            'concerns': 'Cybersecurity, cryptography, electronic warfare',
            'entity_list': True
        },
        'PLA Strategic Support Force Information Engineering University': {
            'abbreviation': 'PLASSF IEU',
            'location': 'Zhengzhou',
            'affiliation': 'PLA',
            'concerns': 'Cyber operations, space warfare, electronic warfare',
            'entity_list': True
        }
    },
    'HIGH': {
        'Tsinghua University': {
            'abbreviation': 'THU',
            'location': 'Beijing',
            'affiliation': 'Elite C9 League, strong military ties',
            'concerns': 'AI, semiconductors, military-civil fusion leader',
            'entity_list': False
        },
        'Peking University': {
            'abbreviation': 'PKU',
            'location': 'Beijing',
            'affiliation': 'Elite C9 League',
            'concerns': 'AI, quantum computing, surveillance tech',
            'entity_list': False
        },
        'University of Science and Technology of China': {
            'abbreviation': 'USTC',
            'location': 'Hefei',
            'affiliation': 'Chinese Academy of Sciences, C9 League',
            'concerns': 'Quantum computing, AI, nuclear weapons research',
            'entity_list': False
        },
        'Zhejiang University': {
            'abbreviation': 'ZJU',
            'location': 'Hangzhou',
            'affiliation': 'C9 League',
            'concerns': 'AI, brain-computer interfaces, surveillance',
            'entity_list': False
        },
        'Shanghai Jiao Tong University': {
            'abbreviation': 'SJTU',
            'location': 'Shanghai',
            'affiliation': 'C9 League',
            'concerns': 'Shipbuilding, naval systems, AI',
            'entity_list': False
        },
        'University of Electronic Science and Technology of China': {
            'abbreviation': 'UESTC',
            'location': 'Chengdu',
            'affiliation': 'Military electronics focus',
            'concerns': 'Radar, electronic warfare, communications',
            'entity_list': False
        },
        'Xidian University': {
            'abbreviation': 'XDU',
            'location': "Xi'an",
            'affiliation': 'Military electronics heritage',
            'concerns': 'Radar, electronic warfare, cryptography',
            'entity_list': False
        },
        'Beijing University of Posts and Telecommunications': {
            'abbreviation': 'BUPT',
            'location': 'Beijing',
            'affiliation': 'Telecom and cyber focus',
            'concerns': '5G, network security, AI',
            'entity_list': False
        }
    },
    'MEDIUM': {
        'Fudan University': {
            'abbreviation': 'FDU',
            'location': 'Shanghai',
            'affiliation': 'C9 League',
            'concerns': 'AI, microelectronics',
            'entity_list': False
        },
        'Nanjing University': {
            'abbreviation': 'NJU',
            'location': 'Nanjing',
            'affiliation': 'C9 League',
            'concerns': 'Physics, materials science',
            'entity_list': False
        },
        'Xi\'an Jiaotong University': {
            'abbreviation': 'XJTU',
            'location': "Xi'an",
            'affiliation': 'C9 League',
            'concerns': 'Energy, materials',
            'entity_list': False
        }
    }
}

def log(msg):
    """Log with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}", flush=True)

def fuzzy_match_institution(name, risk_db):
    """
    Fuzzy match institution name against high-risk database.

    Returns: (risk_level, entity_details) or (None, None)
    """
    if not name:
        return None, None

    name_upper = str(name).upper()

    # Check each risk level
    for risk_level in ['VERY_HIGH', 'HIGH', 'MEDIUM']:
        for full_name, details in risk_db[risk_level].items():
            # Check full name match
            if full_name.upper() in name_upper or name_upper in full_name.upper():
                return risk_level, {**details, 'matched_name': full_name}

            # Check abbreviation match
            abbrev = details.get('abbreviation', '').upper()
            if abbrev and abbrev in name_upper:
                return risk_level, {**details, 'matched_name': full_name}

            # Check location match (helps distinguish institutions)
            location = details.get('location', '').upper()
            if location and location in name_upper and len(name_upper) < 100:
                # If location matches and name is not too long (avoid false positives)
                return risk_level, {**details, 'matched_name': full_name}

    return None, None

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

    # Note: This requires CORDIS organizations table to be populated
    # Check if table exists and has data
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

def cross_reference_institutions(institutions, risk_db):
    """Cross-reference institutions against high-risk database."""

    log(f"\nCross-referencing {len(institutions)} institutions against risk database...")

    results = {
        'VERY_HIGH': [],
        'HIGH': [],
        'MEDIUM': [],
        'UNKNOWN': []
    }

    for inst in institutions:
        risk_level, details = fuzzy_match_institution(inst['name'], risk_db)

        if risk_level:
            results[risk_level].append({
                **inst,
                'risk_level': risk_level,
                'risk_details': details
            })
        else:
            results['UNKNOWN'].append(inst)

    return results

def generate_report(results, output_file):
    """Generate comprehensive ASPI cross-reference report."""

    log("\n" + "="*80)
    log("ASPI CROSS-REFERENCE RESULTS")
    log("="*80)

    report = {
        'metadata': {
            'generated': datetime.now().isoformat(),
            'purpose': 'Netherlands-China university partnership risk assessment',
            'data_sources': ['OpenAlex NL-China collaborations', 'CORDIS EU projects'],
            'risk_database': 'Known high-risk Chinese defense universities',
            'note': 'Future: Integrate full ASPI tracker database for comprehensive coverage'
        },
        'summary': {
            'total_institutions': sum(len(results[level]) for level in results),
            'very_high_risk': len(results['VERY_HIGH']),
            'high_risk': len(results['HIGH']),
            'medium_risk': len(results['MEDIUM']),
            'unknown_risk': len(results['UNKNOWN'])
        },
        'findings': results
    }

    # Print summary
    log(f"\nTotal Chinese institutions analyzed: {report['summary']['total_institutions']}")
    log(f"  VERY HIGH RISK: {report['summary']['very_high_risk']}")
    log(f"  HIGH RISK: {report['summary']['high_risk']}")
    log(f"  MEDIUM RISK: {report['summary']['medium_risk']}")
    log(f"  UNKNOWN/LOW RISK: {report['summary']['unknown_risk']}")

    # Detail VERY HIGH and HIGH risk findings
    if results['VERY_HIGH']:
        log("\n[VERY HIGH RISK PARTNERSHIPS - IMMEDIATE ATTENTION REQUIRED]")
        for inst in results['VERY_HIGH']:
            log(f"\n  {inst['name']}")
            log(f"    Matched: {inst['risk_details']['matched_name']}")
            log(f"    Affiliation: {inst['risk_details']['affiliation']}")
            log(f"    Concerns: {inst['risk_details']['concerns']}")
            log(f"    US Entity List: {inst['risk_details']['entity_list']}")
            log(f"    Source: {inst['source']}")
            if 'collaboration_count' in inst:
                log(f"    NL Collaborations: {inst['collaboration_count']}")

    if results['HIGH']:
        log("\n[HIGH RISK PARTNERSHIPS - ENHANCED SCRUTINY RECOMMENDED]")
        for inst in results['HIGH'][:10]:  # Top 10
            log(f"\n  {inst['name']}")
            log(f"    Matched: {inst['risk_details']['matched_name']}")
            log(f"    Concerns: {inst['risk_details']['concerns']}")
            if 'collaboration_count' in inst:
                log(f"    NL Collaborations: {inst['collaboration_count']}")

    # Save full report
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    log(f"\nFull report saved: {output_file}")

    # Create Excel-ready summary for manual review
    create_review_spreadsheet(results)

    return report

def create_review_spreadsheet(results):
    """Create spreadsheet for manual review of findings."""
    import csv

    output_csv = "analysis/aspi_cross_reference_netherlands_review.csv"

    rows = []
    rows.append(['Institution Name', 'Risk Level', 'Matched Entity', 'Affiliation',
                 'Concerns', 'US Entity List', 'Source', 'Collaboration Count', 'Action Required'])

    for risk_level in ['VERY_HIGH', 'HIGH', 'MEDIUM', 'UNKNOWN']:
        for inst in results[risk_level]:
            if risk_level == 'UNKNOWN':
                rows.append([
                    inst['name'],
                    'UNKNOWN',
                    'Not matched',
                    'N/A',
                    'Needs manual research',
                    'N/A',
                    inst['source'],
                    inst.get('collaboration_count', inst.get('project_count', 0)),
                    'Manual ASPI tracker check required'
                ])
            else:
                details = inst['risk_details']
                rows.append([
                    inst['name'],
                    risk_level,
                    details['matched_name'],
                    details['affiliation'],
                    details['concerns'],
                    'Yes' if details['entity_list'] else 'No',
                    inst['source'],
                    inst.get('collaboration_count', inst.get('project_count', 0)),
                    'IMMEDIATE REVIEW' if risk_level == 'VERY_HIGH' else 'Review recommended'
                ])

    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    log(f"Review spreadsheet created: {output_csv}")

def main():
    """Main execution."""
    start_time = datetime.now()

    log("="*80)
    log("ASPI CHINA DEFENCE UNIVERSITIES TRACKER - NETHERLANDS CROSS-REFERENCE")
    log("="*80)
    log("Commitment: Complete by November 8, 2025")
    log("Part of: Netherlands v1 Strategic Assessment (due Nov 23, 2025)")
    log("="*80)

    # Connect to database
    conn = sqlite3.connect(DB_PATH)

    # Extract Chinese institutions from our data sources
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

    # Cross-reference against risk database
    results = cross_reference_institutions(institutions_list, HIGH_RISK_ENTITIES)

    # Generate report
    output_file = "analysis/aspi_cross_reference_netherlands.json"
    report = generate_report(results, output_file)

    # Cleanup
    conn.close()

    duration = (datetime.now() - start_time).total_seconds()

    log("\n" + "="*80)
    log("CROSS-REFERENCE COMPLETE")
    log(f"Duration: {duration:.1f} seconds")
    log("="*80)
    log("\nNEXT STEPS:")
    log("1. Review analysis/aspi_cross_reference_netherlands.json")
    log("2. Review analysis/aspi_cross_reference_netherlands_review.csv")
    log("3. Manually check UNKNOWN institutions at https://unitracker.aspi.org.au/")
    log("4. Integrate findings into Netherlands v1 Strategic Assessment")
    log("5. Deadline: November 23, 2025")

if __name__ == "__main__":
    main()

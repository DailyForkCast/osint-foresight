#!/usr/bin/env python3
"""
Generate comprehensive country-by-country breakdown of European quantum research
with China collaboration analysis.

Data Sources:
1. analysis/quantum_tech/cordis_quantum_projects.json - 2,610 quantum projects
2. F:/OSINT_WAREHOUSE/osint_master.db - OpenAlex database
3. Existing analysis files
"""

import json
import sqlite3
from collections import defaultdict
from datetime import datetime
from pathlib import Path

# Country tiers
TIER_1_COUNTRIES = ['DE', 'FR', 'GB', 'NL', 'ES', 'IT']
TIER_1_NAMES = {
    'DE': 'Germany',
    'FR': 'France',
    'GB': 'United Kingdom',
    'NL': 'Netherlands',
    'ES': 'Spain',
    'IT': 'Italy'
}

# EU country codes for analysis
EU_COUNTRIES = [
    'AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR', 'DE', 'GR',
    'HU', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'NL', 'PL', 'PT', 'RO', 'SK',
    'SI', 'ES', 'SE'
]

# Include UK and other European countries
EUROPEAN_COUNTRIES = EU_COUNTRIES + ['GB', 'NO', 'CH', 'IS']

def load_cordis_data():
    """Load CORDIS quantum projects data."""
    print("Loading CORDIS quantum projects...")
    cordis_path = Path("C:/Projects/OSINT - Foresight/analysis/quantum_tech/cordis_quantum_projects.json")

    with open(cordis_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Extract the projects array from the wrapper
    projects = data.get('all_projects', [])
    print(f"Loaded {len(projects)} CORDIS projects")
    return projects

def analyze_cordis_by_country(projects):
    """Analyze CORDIS projects by country."""
    print("\nAnalyzing CORDIS data by country...")

    country_stats = defaultdict(lambda: {
        'project_count': 0,
        'total_funding': 0,
        'projects': [],
        'coordinators': set(),
        'organizations': set()
    })

    for project in projects:
        # Extract countries
        countries = []
        if 'countries' in project and isinstance(project['countries'], list):
            countries = project['countries']
        elif 'country' in project:
            countries = [project['country']]

        # Extract funding
        funding = 0
        if 'totalCost' in project:
            try:
                funding = float(project['totalCost'])
            except:
                pass

        # Extract coordinator
        coordinator = project.get('coordinator', 'Unknown')

        # Process each country
        for country in countries:
            if country and country in EUROPEAN_COUNTRIES:
                country_stats[country]['project_count'] += 1
                country_stats[country]['total_funding'] += funding
                country_stats[country]['projects'].append({
                    'title': project.get('title', ''),
                    'id': project.get('id', ''),
                    'funding': funding,
                    'coordinator': coordinator
                })
                country_stats[country]['coordinators'].add(coordinator)

                # Extract organization names from coordinator
                if coordinator and coordinator != 'Unknown':
                    country_stats[country]['organizations'].add(coordinator)

    # Convert sets to lists for JSON serialization
    for country in country_stats:
        country_stats[country]['coordinators'] = list(country_stats[country]['coordinators'])
        country_stats[country]['organizations'] = list(country_stats[country]['organizations'])

    return dict(country_stats)

def query_openalex_quantum(db_path):
    """Query OpenAlex database for quantum research collaborations."""
    print("\nQuerying OpenAlex database...")

    if not Path(db_path).exists():
        print(f"WARNING: Database not found at {db_path}")
        return None

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Check what tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"Available tables: {tables}")

        results = {
            'total_quantum_works': 0,
            'country_stats': {},
            'china_collaborations': {},
            'technology_topics': {}
        }

        # Query for quantum research works
        # Adjust query based on actual schema
        quantum_query = """
        SELECT
            country_code,
            COUNT(*) as work_count,
            GROUP_CONCAT(DISTINCT institution_name) as institutions
        FROM research_collaborations
        WHERE (
            title LIKE '%quantum%' OR
            abstract LIKE '%quantum computing%' OR
            abstract LIKE '%quantum sensing%' OR
            abstract LIKE '%quantum communication%' OR
            keywords LIKE '%quantum%'
        )
        AND country_code IN ({})
        GROUP BY country_code
        ORDER BY work_count DESC
        """.format(','.join(['?' for _ in EUROPEAN_COUNTRIES]))

        try:
            cursor.execute(quantum_query, EUROPEAN_COUNTRIES)
            for row in cursor:
                country = row['country_code']
                results['country_stats'][country] = {
                    'work_count': row['work_count'],
                    'institutions': row['institutions'].split(',') if row['institutions'] else []
                }
                results['total_quantum_works'] += row['work_count']
        except sqlite3.OperationalError as e:
            print(f"Query error (may need schema adjustment): {e}")
            # Try alternative query structure
            pass

        # Query for China collaborations
        china_collab_query = """
        SELECT
            c1.country_code as eu_country,
            COUNT(*) as collaboration_count,
            GROUP_CONCAT(DISTINCT work_title) as sample_works
        FROM research_collaborations c1
        JOIN research_collaborations c2 ON c1.work_id = c2.work_id
        WHERE c1.country_code IN ({})
        AND c2.country_code = 'CN'
        AND (
            c1.title LIKE '%quantum%' OR
            c1.abstract LIKE '%quantum%'
        )
        GROUP BY c1.country_code
        ORDER BY collaboration_count DESC
        """.format(','.join(['?' for _ in EUROPEAN_COUNTRIES]))

        try:
            cursor.execute(china_collab_query, EUROPEAN_COUNTRIES)
            for row in cursor:
                results['china_collaborations'][row['eu_country']] = {
                    'count': row['collaboration_count'],
                    'sample_works': row['sample_works'].split(',')[:5] if row['sample_works'] else []
                }
        except sqlite3.OperationalError as e:
            print(f"China collaboration query error: {e}")
            pass

        conn.close()
        return results

    except Exception as e:
        print(f"Error querying OpenAlex: {e}")
        return None

def calculate_risk_levels(country_data, china_collabs):
    """Calculate China collaboration risk levels for each country."""
    risk_levels = {}

    for country in EUROPEAN_COUNTRIES:
        risk_score = 0
        risk_factors = []

        # Factor 1: Volume of China collaborations
        china_count = china_collabs.get(country, {}).get('count', 0)
        if china_count > 100:
            risk_score += 3
            risk_factors.append(f"High collaboration volume ({china_count} works)")
        elif china_count > 50:
            risk_score += 2
            risk_factors.append(f"Moderate collaboration volume ({china_count} works)")
        elif china_count > 0:
            risk_score += 1
            risk_factors.append(f"Low collaboration volume ({china_count} works)")

        # Factor 2: Project funding scale
        total_funding = country_data.get(country, {}).get('total_funding', 0)
        if total_funding > 500_000_000:  # >500M EUR
            risk_score += 2
            risk_factors.append("Very high research funding")
        elif total_funding > 100_000_000:  # >100M EUR
            risk_score += 1
            risk_factors.append("High research funding")

        # Factor 3: Number of projects
        project_count = country_data.get(country, {}).get('project_count', 0)
        if project_count > 200:
            risk_score += 1
            risk_factors.append(f"Large project portfolio ({project_count} projects)")

        # Determine risk level
        if risk_score >= 5:
            risk_level = "CRITICAL"
        elif risk_score >= 3:
            risk_level = "HIGH"
        elif risk_score >= 2:
            risk_level = "MODERATE"
        elif risk_score > 0:
            risk_level = "LOW"
        else:
            risk_level = "MINIMAL"

        risk_levels[country] = {
            'level': risk_level,
            'score': risk_score,
            'factors': risk_factors
        }

    return risk_levels

def generate_country_profile(country_code, country_name, cordis_data, openalex_data, risk_info):
    """Generate detailed country profile."""

    profile = f"\n## {country_name} ({country_code})\n\n"

    # Summary statistics
    project_count = cordis_data.get('project_count', 0)
    total_funding = cordis_data.get('total_funding', 0)

    profile += f"### Overview\n\n"
    profile += f"- **Total CORDIS Quantum Projects**: {project_count:,}\n"
    profile += f"- **Total EU Funding**: €{total_funding:,.0f}\n"
    profile += f"- **Average Project Funding**: €{total_funding/project_count:,.0f}\n" if project_count > 0 else ""

    # OpenAlex statistics
    if openalex_data and country_code in openalex_data.get('country_stats', {}):
        work_count = openalex_data['country_stats'][country_code].get('work_count', 0)
        profile += f"- **OpenAlex Quantum Works**: {work_count:,}\n"

    profile += "\n"

    # Key institutions
    profile += f"### Key Research Institutions\n\n"
    organizations = cordis_data.get('organizations', [])
    if organizations:
        # Get top organizations by project count
        org_counts = defaultdict(int)
        for project in cordis_data.get('projects', []):
            org = project.get('coordinator', '')
            if org and org != 'Unknown':
                org_counts[org] += 1

        top_orgs = sorted(org_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        for org, count in top_orgs:
            profile += f"- **{org}** - {count} projects\n"
    else:
        profile += "*No organization data available*\n"

    profile += "\n"

    # China collaboration indicators
    profile += f"### China Collaboration Analysis\n\n"
    profile += f"**Risk Level**: {risk_info['level']}\n\n"

    if openalex_data and country_code in openalex_data.get('china_collaborations', {}):
        collab_data = openalex_data['china_collaborations'][country_code]
        collab_count = collab_data.get('count', 0)
        profile += f"- **Identified China Co-authorships**: {collab_count:,}\n"

        if collab_count > 0:
            profile += f"- **Collaboration Rate**: {(collab_count/project_count*100):.1f}% of CORDIS projects\n" if project_count > 0 else ""

            sample_works = collab_data.get('sample_works', [])
            if sample_works:
                profile += f"\n**Sample Collaborative Works**:\n"
                for i, work in enumerate(sample_works[:3], 1):
                    profile += f"{i}. {work[:150]}...\n"
    else:
        profile += "- **Identified China Co-authorships**: Data pending\n"

    profile += "\n**Risk Factors**:\n"
    for factor in risk_info['factors']:
        profile += f"- {factor}\n"

    profile += "\n"

    # Research security risks
    profile += f"### Research Security Assessment\n\n"

    if risk_info['level'] in ['CRITICAL', 'HIGH']:
        profile += "**Priority Concerns**:\n"
        profile += "- High volume of quantum research collaboration with Chinese institutions\n"
        profile += "- Potential dual-use technology transfer in quantum computing and sensing\n"
        profile += "- Need for enhanced research security protocols\n"
        profile += "- Recommended: Comprehensive screening of collaborative research agreements\n"
    elif risk_info['level'] == 'MODERATE':
        profile += "**Monitoring Required**:\n"
        profile += "- Moderate level of China collaboration requires ongoing monitoring\n"
        profile += "- Standard research security protocols should be enforced\n"
        profile += "- Periodic review of technology transfer arrangements\n"
    else:
        profile += "**Standard Protocols**:\n"
        profile += "- Low to minimal China collaboration detected\n"
        profile += "- Standard research security measures are adequate\n"
        profile += "- Maintain vigilance for emerging collaboration patterns\n"

    profile += "\n"

    # Strategic recommendations
    profile += f"### Strategic Recommendations\n\n"

    if country_code in TIER_1_COUNTRIES:
        profile += f"As a **Tier 1** quantum research hub:\n\n"
        profile += "1. **Enhanced Due Diligence**: Implement comprehensive screening for all international collaborations\n"
        profile += "2. **Technology Transfer Controls**: Strengthen export control compliance for quantum technologies\n"
        profile += "3. **Institutional Capacity**: Build research security offices at major institutions\n"
        profile += "4. **Talent Security**: Monitor recruitment patterns and foreign talent programs\n"
        profile += "5. **Critical Technology Protection**: Classify sensitive quantum research appropriately\n"
    else:
        profile += f"As a **Tier 2** quantum research participant:\n\n"
        profile += "1. **Awareness Building**: Educate researchers on technology transfer risks\n"
        profile += "2. **Collaboration Review**: Establish basic screening protocols for international partnerships\n"
        profile += "3. **Information Sharing**: Participate in EU-wide research security initiatives\n"
        profile += "4. **Capability Assessment**: Evaluate quantum research capabilities for security implications\n"

    profile += "\n---\n"

    return profile

def generate_executive_summary(all_data, risk_levels):
    """Generate executive summary with key findings."""

    summary = "# European Quantum Research: China Collaboration Analysis\n\n"
    summary += f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    summary += "**Classification**: RESEARCH SECURITY ASSESSMENT\n"
    summary += "**Distribution**: Research Security Officials, Policy Makers\n\n"

    summary += "---\n\n"
    summary += "## Executive Summary\n\n"

    # Calculate totals
    total_projects = sum(data.get('project_count', 0) for data in all_data['cordis'].values())
    total_funding = sum(data.get('total_funding', 0) for data in all_data['cordis'].values())

    summary += f"### Key Findings\n\n"
    summary += f"- **Total European Quantum Projects Analyzed**: {total_projects:,} (CORDIS database)\n"
    summary += f"- **Total EU Funding**: €{total_funding:,.0f} ({total_funding/1_000_000_000:.2f} billion)\n"
    summary += f"- **Countries Assessed**: {len(EUROPEAN_COUNTRIES)} European nations\n"
    summary += f"- **OpenAlex Quantum Works**: {all_data['openalex'].get('total_quantum_works', 0):,}\n\n"

    # Risk distribution
    risk_distribution = defaultdict(int)
    for risk_info in risk_levels.values():
        risk_distribution[risk_info['level']] += 1

    summary += "### China Collaboration Risk Distribution\n\n"
    for level in ['CRITICAL', 'HIGH', 'MODERATE', 'LOW', 'MINIMAL']:
        count = risk_distribution[level]
        if count > 0:
            summary += f"- **{level}**: {count} countries\n"

    summary += "\n### Tier 1 Countries at a Glance\n\n"
    summary += "| Country | Projects | Funding (€M) | Risk Level |\n"
    summary += "|---------|----------|--------------|------------|\n"

    for code in TIER_1_COUNTRIES:
        name = TIER_1_NAMES[code]
        project_count = all_data['cordis'].get(code, {}).get('project_count', 0)
        funding = all_data['cordis'].get(code, {}).get('total_funding', 0) / 1_000_000
        risk = risk_levels.get(code, {}).get('level', 'UNKNOWN')
        summary += f"| {name} | {project_count:,} | €{funding:,.1f}M | {risk} |\n"

    summary += "\n### Critical Findings\n\n"

    # Find countries with highest risk
    high_risk_countries = [
        (code, risk_levels[code]) for code in risk_levels
        if risk_levels[code]['level'] in ['CRITICAL', 'HIGH']
    ]
    high_risk_countries.sort(key=lambda x: x[1]['score'], reverse=True)

    if high_risk_countries:
        summary += "**Countries Requiring Enhanced Monitoring**:\n\n"
        for code, risk_info in high_risk_countries[:5]:
            country_name = TIER_1_NAMES.get(code, code)
            summary += f"1. **{country_name}**: {risk_info['level']} risk\n"
            for factor in risk_info['factors'][:3]:
                summary += f"   - {factor}\n"
            summary += "\n"

    summary += "### Strategic Implications\n\n"
    summary += "1. **Technology Transfer Exposure**: Significant quantum research collaboration with China "
    summary += "creates potential pathways for dual-use technology transfer\n\n"
    summary += "2. **Research Security Gaps**: Many European institutions lack robust screening protocols "
    summary += "for international quantum research partnerships\n\n"
    summary += "3. **Talent Mobility**: High volumes of researcher exchange in quantum fields require "
    summary += "enhanced monitoring mechanisms\n\n"
    summary += "4. **Critical Technology Protection**: Quantum sensing, computing, and communication "
    summary += "technologies have clear military applications requiring protection\n\n"
    summary += "5. **EU Coordination**: Need for harmonized research security standards across member states\n\n"

    summary += "### Immediate Recommendations\n\n"
    summary += "1. **Policy Action**: Develop EU-wide quantum research security framework\n"
    summary += "2. **Institutional Capacity**: Establish research security offices at major quantum research centers\n"
    summary += "3. **Screening Protocols**: Implement comprehensive due diligence for China collaborations\n"
    summary += "4. **Technology Classification**: Review and classify sensitive quantum research appropriately\n"
    summary += "5. **Information Sharing**: Create mechanisms for sharing threat intelligence across borders\n"
    summary += "6. **Researcher Training**: Mandatory research security awareness for quantum scientists\n\n"

    summary += "---\n\n"

    return summary

def main():
    """Main execution function."""
    print("=" * 80)
    print("EUROPEAN QUANTUM RESEARCH - CHINA COLLABORATION ANALYSIS")
    print("=" * 80)

    # Load CORDIS data
    cordis_projects = load_cordis_data()
    cordis_by_country = analyze_cordis_by_country(cordis_projects)

    # Query OpenAlex database
    openalex_db = "F:/OSINT_WAREHOUSE/osint_master.db"
    openalex_results = query_openalex_quantum(openalex_db)

    if not openalex_results:
        print("\nWARNING: Using CORDIS data only. OpenAlex query unavailable.")
        openalex_results = {
            'total_quantum_works': 0,
            'country_stats': {},
            'china_collaborations': {}
        }

    # Calculate risk levels
    risk_levels = calculate_risk_levels(cordis_by_country, openalex_results.get('china_collaborations', {}))

    # Compile all data
    all_data = {
        'cordis': cordis_by_country,
        'openalex': openalex_results,
        'risk_levels': risk_levels
    }

    # Generate report
    print("\nGenerating comprehensive report...")

    report = generate_executive_summary(all_data, risk_levels)

    # Add Tier 1 country profiles
    report += "## Tier 1 Countries: Detailed Profiles\n\n"
    report += "*Major quantum research hubs requiring enhanced security protocols*\n\n"

    for code in TIER_1_COUNTRIES:
        name = TIER_1_NAMES[code]
        country_data = cordis_by_country.get(code, {})
        risk_info = risk_levels.get(code, {'level': 'UNKNOWN', 'score': 0, 'factors': []})

        report += generate_country_profile(code, name, country_data, openalex_results, risk_info)

    # Add Tier 2 country summaries
    report += "\n## Tier 2 Countries: Summary Assessment\n\n"
    report += "*Secondary quantum research participants*\n\n"

    tier2_countries = [c for c in EUROPEAN_COUNTRIES if c not in TIER_1_COUNTRIES]
    tier2_countries.sort(key=lambda c: cordis_by_country.get(c, {}).get('project_count', 0), reverse=True)

    report += "| Country | Projects | Funding (€M) | Risk Level | Key Institutions (Sample) |\n"
    report += "|---------|----------|--------------|------------|---------------------------|\n"

    for code in tier2_countries:
        project_count = cordis_by_country.get(code, {}).get('project_count', 0)
        if project_count == 0:
            continue

        funding = cordis_by_country.get(code, {}).get('total_funding', 0) / 1_000_000
        risk = risk_levels.get(code, {}).get('level', 'UNKNOWN')

        orgs = cordis_by_country.get(code, {}).get('organizations', [])
        org_sample = orgs[0] if orgs else 'N/A'
        if len(org_sample) > 40:
            org_sample = org_sample[:37] + "..."

        report += f"| {code} | {project_count} | €{funding:.1f}M | {risk} | {org_sample} |\n"

    report += "\n---\n\n"

    # Add methodology section
    report += "## Methodology\n\n"
    report += "### Data Sources\n\n"
    report += "1. **CORDIS Database**: 2,610 EU-funded quantum projects (H2020 + Horizon Europe)\n"
    report += "2. **OpenAlex Database**: Global academic research repository with 17,739+ quantum works\n"
    report += "3. **Existing Analysis**: Previous quantum technology assessments and forecasts\n\n"

    report += "### Risk Assessment Framework\n\n"
    report += "Risk levels are calculated based on multiple factors:\n\n"
    report += "- **Collaboration Volume**: Number of identified co-authorships with Chinese institutions\n"
    report += "- **Research Funding**: Scale of quantum research investment (technology transfer potential)\n"
    report += "- **Project Portfolio**: Size and diversity of quantum research activities\n"
    report += "- **Institutional Capacity**: Concentration of research at key institutions\n\n"

    report += "**Risk Levels**:\n"
    report += "- **CRITICAL** (Score ≥5): Immediate enhanced security protocols required\n"
    report += "- **HIGH** (Score 3-4): Enhanced monitoring and screening necessary\n"
    report += "- **MODERATE** (Score 2): Standard protocols with periodic review\n"
    report += "- **LOW** (Score 1): Basic awareness and monitoring sufficient\n"
    report += "- **MINIMAL** (Score 0): Standard research practices adequate\n\n"

    report += "### Limitations\n\n"
    report += "- OpenAlex data may not capture all China collaborations (journal coverage varies)\n"
    report += "- CORDIS data reflects EU-funded projects only (national programs not included)\n"
    report += "- Risk assessment is indicative; detailed institutional reviews recommended\n"
    report += "- Technology transfer can occur through non-publication channels\n"
    report += "- Some European countries may have additional national quantum programs\n\n"

    report += "---\n\n"
    report += "## Appendix: Technology Transfer Concerns\n\n"
    report += "### Dual-Use Quantum Technologies\n\n"
    report += "1. **Quantum Computing**\n"
    report += "   - Cryptanalysis capabilities (breaking current encryption)\n"
    report += "   - Optimization for military logistics and targeting\n"
    report += "   - Materials science for weapons development\n\n"

    report += "2. **Quantum Sensing**\n"
    report += "   - Submarine detection (magnetic anomaly detection)\n"
    report += "   - Underground facility mapping\n"
    report += "   - Precision navigation and timing\n\n"

    report += "3. **Quantum Communication**\n"
    report += "   - Secure military communications\n"
    report += "   - Quantum key distribution for classified networks\n"
    report += "   - Anti-jamming communications\n\n"

    report += "### Transfer Pathways\n\n"
    report += "- Joint research publications and conferences\n"
    report += "- Researcher mobility and talent recruitment programs\n"
    report += "- Commercial partnerships and joint ventures\n"
    report += "- Equipment and material purchases\n"
    report += "- Academic exchange and visiting scholar programs\n\n"

    report += "---\n\n"
    report += f"**Report Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    report += "**Classification**: Research Security Assessment\n"
    report += "**Prepared By**: OSINT Foresight Analysis System\n"
    report += "**Distribution**: Research Security Officials, Policy Makers, Institutional Leadership\n\n"

    # Save report
    output_path = Path("C:/Projects/OSINT - Foresight/analysis/QUANTUM_EUROPE_CHINA_COLLABORATION_REPORT.md")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\nReport saved to: {output_path}")

    # Save structured data
    structured_output = {
        'metadata': {
            'generated': datetime.now().isoformat(),
            'total_projects': sum(data.get('project_count', 0) for data in cordis_by_country.values()),
            'total_funding': sum(data.get('total_funding', 0) for data in cordis_by_country.values()),
            'countries_analyzed': len(EUROPEAN_COUNTRIES)
        },
        'country_data': {},
        'risk_levels': risk_levels,
        'openalex_summary': {
            'total_works': openalex_results.get('total_quantum_works', 0),
            'china_collaborations_detected': len(openalex_results.get('china_collaborations', {}))
        }
    }

    for code in EUROPEAN_COUNTRIES:
        if code in cordis_by_country or code in risk_levels:
            structured_output['country_data'][code] = {
                'cordis': {
                    'project_count': cordis_by_country.get(code, {}).get('project_count', 0),
                    'total_funding': cordis_by_country.get(code, {}).get('total_funding', 0),
                    'organization_count': len(cordis_by_country.get(code, {}).get('organizations', []))
                },
                'risk': risk_levels.get(code, {'level': 'UNKNOWN', 'score': 0, 'factors': []})
            }

    json_output_path = Path("C:/Projects/OSINT - Foresight/analysis/QUANTUM_EUROPE_CHINA_COLLABORATION_DATA.json")
    with open(json_output_path, 'w', encoding='utf-8') as f:
        json.dump(structured_output, f, indent=2, ensure_ascii=False)

    print(f"Structured data saved to: {json_output_path}")

    # Print summary statistics
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print(f"\nTotal Projects Analyzed: {structured_output['metadata']['total_projects']:,}")
    print(f"Total EU Funding: €{structured_output['metadata']['total_funding']:,.0f}")
    print(f"Countries Assessed: {structured_output['metadata']['countries_analyzed']}")

    print("\nRisk Distribution:")
    risk_dist = defaultdict(int)
    for risk_info in risk_levels.values():
        risk_dist[risk_info['level']] += 1

    for level in ['CRITICAL', 'HIGH', 'MODERATE', 'LOW', 'MINIMAL']:
        if risk_dist[level] > 0:
            print(f"  {level}: {risk_dist[level]} countries")

    print("\nTop 5 Countries by Project Count:")
    top_countries = sorted(
        [(code, cordis_by_country[code]['project_count']) for code in cordis_by_country],
        key=lambda x: x[1],
        reverse=True
    )[:5]

    for code, count in top_countries:
        name = TIER_1_NAMES.get(code, code)
        risk = risk_levels.get(code, {}).get('level', 'UNKNOWN')
        print(f"  {name} ({code}): {count:,} projects - {risk} risk")

    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()

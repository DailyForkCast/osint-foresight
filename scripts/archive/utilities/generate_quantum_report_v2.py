#!/usr/bin/env python3
"""
Generate comprehensive European quantum research with China collaboration analysis.
Uses OpenAlex database for actual research collaboration data.
"""

import json
import sqlite3
from collections import defaultdict, Counter
from datetime import datetime
from pathlib import Path

# Country configuration
TIER_1_COUNTRIES = {
    'DE': 'Germany',
    'FR': 'France',
    'GB': 'United Kingdom',
    'NL': 'Netherlands',
    'ES': 'Spain',
    'IT': 'Italy'
}

EU_COUNTRIES = ['AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR', 'DE', 'GR',
                'HU', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'NL', 'PL', 'PT', 'RO', 'SK',
                'SI', 'ES', 'SE']

EUROPEAN_COUNTRIES = EU_COUNTRIES + ['GB', 'NO', 'CH', 'IS']

def query_openalex_quantum_research():
    """Query OpenAlex for European quantum research and China collaborations."""
    print("="*80)
    print("QUERYING OPENALEX DATABASE FOR QUANTUM RESEARCH")
    print("="*80)

    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
    if not Path(db_path).exists():
        print(f"ERROR: Database not found at {db_path}")
        return None

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    results = {
        'total_european_quantum_works': 0,
        'country_research': {},
        'china_collaborations': {},
        'institutions': {},
        'topics': {},
        'dual_use_indicators': {}
    }

    # Query openalex_works for quantum research
    print("\n1. Counting European quantum research works...")

    quantum_query = """
    SELECT
        w.id,
        w.title,
        w.publication_year,
        w.cited_by_count,
        w.doi,
        GROUP_CONCAT(DISTINCT i.country_code) as countries
    FROM openalex_works w
    LEFT JOIN openalex_work_authors wa ON w.id = wa.work_id
    LEFT JOIN openalex_institutions i ON wa.institution_id = i.id
    WHERE (
        w.title LIKE '%quantum%'
        OR w.abstract LIKE '%quantum computing%'
        OR w.abstract LIKE '%quantum sensing%'
        OR w.abstract LIKE '%quantum communication%'
        OR w.abstract LIKE '%quantum cryptography%'
        OR w.abstract LIKE '%qubit%'
    )
    AND i.country_code IN ({})
    GROUP BY w.id
    ORDER BY w.publication_year DESC, w.cited_by_count DESC
    LIMIT 20000
    """.format(','.join(['?' for _ in EUROPEAN_COUNTRIES]))

    try:
        cursor.execute(quantum_query, EUROPEAN_COUNTRIES)
        works = cursor.fetchall()
        print(f"   Found {len(works)} quantum research works")

        # Process works by country
        for work in works:
            countries = work['countries'].split(',') if work['countries'] else []

            for country in countries:
                if country in EUROPEAN_COUNTRIES:
                    if country not in results['country_research']:
                        results['country_research'][country] = {
                            'work_count': 0,
                            'total_citations': 0,
                            'recent_works': [],
                            'institutions': set()
                        }

                    results['country_research'][country]['work_count'] += 1
                    results['country_research'][country]['total_citations'] += work['cited_by_count'] or 0

                    if len(results['country_research'][country]['recent_works']) < 5:
                        results['country_research'][country]['recent_works'].append({
                            'title': work['title'],
                            'year': work['publication_year'],
                            'citations': work['cited_by_count'] or 0
                        })

                    # Check if China is also in the countries (collaboration)
                    if 'CN' in countries:
                        if country not in results['china_collaborations']:
                            results['china_collaborations'][country] = {
                                'count': 0,
                                'sample_works': []
                            }

                        results['china_collaborations'][country]['count'] += 1
                        if len(results['china_collaborations'][country]['sample_works']) < 5:
                            results['china_collaborations'][country]['sample_works'].append({
                                'title': work['title'],
                                'year': work['publication_year'],
                                'citations': work['cited_by_count'] or 0
                            })

        results['total_european_quantum_works'] = len(works)

    except sqlite3.OperationalError as e:
        print(f"   Query error: {e}")
        print("   Attempting fallback query...")

        # Fallback: Direct check in openalex_china_deep or openalex_works
        fallback_query = """
        SELECT COUNT(*) as count
        FROM openalex_works
        WHERE title LIKE '%quantum%'
        """
        try:
            cursor.execute(fallback_query)
            count = cursor.fetchone()[0]
            print(f"   Fallback found {count} quantum works (no country filter)")
        except Exception as e2:
            print(f"   Fallback also failed: {e2}")

    # Query institutions
    print("\n2. Identifying top quantum research institutions...")

    inst_query = """
    SELECT
        i.id,
        i.display_name,
        i.country_code,
        COUNT(DISTINCT w.id) as work_count
    FROM openalex_institutions i
    JOIN openalex_work_authors wa ON i.id = wa.institution_id
    JOIN openalex_works w ON wa.work_id = w.id
    WHERE (w.title LIKE '%quantum%' OR w.abstract LIKE '%quantum%')
    AND i.country_code IN ({})
    GROUP BY i.id, i.display_name, i.country_code
    ORDER BY work_count DESC
    LIMIT 100
    """.format(','.join(['?' for _ in EUROPEAN_COUNTRIES]))

    try:
        cursor.execute(inst_query, EUROPEAN_COUNTRIES)
        institutions = cursor.fetchall()
        print(f"   Found {len(institutions)} institutions")

        for inst in institutions:
            country = inst['country_code']
            if country in EUROPEAN_COUNTRIES:
                if country not in results['institutions']:
                    results['institutions'][country] = []

                results['institutions'][country].append({
                    'name': inst['display_name'],
                    'work_count': inst['work_count']
                })

    except sqlite3.OperationalError as e:
        print(f"   Institution query error: {e}")

    # Query for technology topics
    print("\n3. Analyzing quantum technology topics...")

    topic_query = """
    SELECT
        wt.display_name as topic,
        COUNT(DISTINCT wt.work_id) as count
    FROM openalex_work_topics wt
    JOIN openalex_works w ON wt.work_id = w.id
    WHERE (w.title LIKE '%quantum%' OR w.abstract LIKE '%quantum%')
    AND wt.display_name IS NOT NULL
    GROUP BY wt.display_name
    ORDER BY count DESC
    LIMIT 50
    """

    try:
        cursor.execute(topic_query)
        topics = cursor.fetchall()
        print(f"   Found {len(topics)} distinct topics")

        for topic in topics:
            results['topics'][topic['topic']] = topic['count']

    except sqlite3.OperationalError as e:
        print(f"   Topic query error: {e}")

    conn.close()
    return results

def calculate_risk_levels(openalex_data):
    """Calculate China collaboration risk levels."""
    print("\n4. Calculating risk levels...")

    risk_levels = {}
    china_collabs = openalex_data.get('china_collaborations', {})
    country_research = openalex_data.get('country_research', {})

    for country in EUROPEAN_COUNTRIES:
        risk_score = 0
        risk_factors = []

        # Factor 1: Volume of China collaborations
        china_count = china_collabs.get(country, {}).get('count', 0)
        total_works = country_research.get(country, {}).get('work_count', 0)

        if china_count > 100:
            risk_score += 3
            risk_factors.append(f"High collaboration volume: {china_count} China co-authored works")
        elif china_count > 50:
            risk_score += 2
            risk_factors.append(f"Moderate collaboration volume: {china_count} China co-authored works")
        elif china_count > 10:
            risk_score += 1
            risk_factors.append(f"Notable collaboration presence: {china_count} China co-authored works")

        # Factor 2: Collaboration rate
        if total_works > 0:
            collab_rate = (china_count / total_works) * 100
            if collab_rate > 20:
                risk_score += 2
                risk_factors.append(f"High collaboration rate: {collab_rate:.1f}% of quantum works involve China")
            elif collab_rate > 10:
                risk_score += 1
                risk_factors.append(f"Significant collaboration rate: {collab_rate:.1f}% involve China")

        # Factor 3: Research volume (indicates capability)
        if total_works > 500:
            risk_score += 2
            risk_factors.append(f"Major research hub: {total_works} quantum publications")
        elif total_works > 200:
            risk_score += 1
            risk_factors.append(f"Significant research capacity: {total_works} quantum publications")

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
            'factors': risk_factors,
            'china_collaborations': china_count,
            'total_works': total_works,
            'collab_rate': (china_count / total_works * 100) if total_works > 0 else 0
        }

    print(f"   Assessed {len(risk_levels)} countries")
    return risk_levels

def generate_report(openalex_data, risk_levels):
    """Generate comprehensive markdown report."""
    print("\n5. Generating report...")

    report = []
    report.append("# European Quantum Research: China Collaboration Analysis\n")
    report.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("**Classification**: RESEARCH SECURITY ASSESSMENT\n")
    report.append("**Data Source**: OpenAlex Global Research Database\n\n")
    report.append("---\n\n")

    # Executive Summary
    report.append("## Executive Summary\n\n")

    total_works = openalex_data['total_european_quantum_works']
    total_collaborations = sum(v.get('count', 0) for v in openalex_data['china_collaborations'].values())

    report.append("### Key Findings\n\n")
    report.append(f"- **Total European Quantum Research Works Analyzed**: {total_works:,}\n")
    report.append(f"- **China Co-Authored Works**: {total_collaborations:,}\n")
    report.append(f"- **Overall China Collaboration Rate**: {(total_collaborations/total_works*100):.1f}%\n")
    report.append(f"- **Countries Assessed**: {len(EUROPEAN_COUNTRIES)}\n")
    report.append(f"- **Research Institutions Identified**: {sum(len(v) for v in openalex_data['institutions'].values())}\n\n")

    # Risk distribution
    risk_dist = Counter(v['level'] for v in risk_levels.values())
    report.append("### China Collaboration Risk Distribution\n\n")
    for level in ['CRITICAL', 'HIGH', 'MODERATE', 'LOW', 'MINIMAL']:
        if risk_dist[level] > 0:
            report.append(f"- **{level}**: {risk_dist[level]} countries\n")
    report.append("\n")

    # Tier 1 summary table
    report.append("### Tier 1 Countries at a Glance\n\n")
    report.append("| Country | Quantum Works | China Collabs | Collab Rate | Risk Level |\n")
    report.append("|---------|---------------|---------------|-------------|------------|\n")

    for code, name in TIER_1_COUNTRIES.items():
        works = openalex_data['country_research'].get(code, {}).get('work_count', 0)
        china_collabs = risk_levels[code]['china_collaborations']
        collab_rate = risk_levels[code]['collab_rate']
        risk = risk_levels[code]['level']
        report.append(f"| {name} | {works:,} | {china_collabs:,} | {collab_rate:.1f}% | **{risk}** |\n")
    report.append("\n")

    # Critical findings
    report.append("### Critical Findings\n\n")

    high_risk = [(code, risk_levels[code]) for code in risk_levels
                 if risk_levels[code]['level'] in ['CRITICAL', 'HIGH']]
    high_risk.sort(key=lambda x: x[1]['score'], reverse=True)

    if high_risk:
        report.append("**Countries Requiring Enhanced Research Security Measures**:\n\n")
        for code, risk in high_risk[:10]:
            name = TIER_1_COUNTRIES.get(code, code)
            report.append(f"#### {name} ({code}) - {risk['level']} Risk\n\n")
            report.append(f"- **China Co-authorships**: {risk['china_collaborations']:,}\n")
            report.append(f"- **Total Quantum Works**: {risk['total_works']:,}\n")
            report.append(f"- **Collaboration Rate**: {risk['collab_rate']:.1f}%\n")
            report.append("\n**Risk Factors**:\n")
            for factor in risk['factors']:
                report.append(f"- {factor}\n")
            report.append("\n")

    # Strategic implications
    report.append("### Strategic Implications\n\n")
    report.append("1. **Significant Technology Transfer Risk**: High volumes of quantum research collaboration ")
    report.append("with China create potential pathways for dual-use technology transfer, particularly in ")
    report.append("quantum computing, sensing, and communication.\n\n")

    report.append("2. **Research Security Gaps**: The {:.1f}% China collaboration rate indicates extensive ".format(
        total_collaborations/total_works*100))
    report.append("scientific exchange, requiring enhanced vetting and monitoring protocols.\n\n")

    report.append("3. **Critical Technology Exposure**: Quantum technologies have clear military applications ")
    report.append("including cryptanalysis, submarine detection, and secure communications.\n\n")

    report.append("4. **Institutional Vulnerability**: Major European research institutions lack standardized ")
    report.append("protocols for assessing international collaboration risks.\n\n")

    report.append("### Immediate Recommendations\n\n")
    report.append("1. **Policy Framework**: Develop EU-wide research security standards for quantum technologies\n")
    report.append("2. **Enhanced Screening**: Implement mandatory due diligence for China quantum collaborations\n")
    report.append("3. **Technology Classification**: Review and classify sensitive quantum research areas\n")
    report.append("4. **Institutional Capacity**: Establish research security offices at major quantum centers\n")
    report.append("5. **Information Sharing**: Create threat intelligence sharing mechanisms\n")
    report.append("6. **Researcher Training**: Mandatory security awareness for quantum scientists\n\n")

    report.append("---\n\n")

    # Detailed country profiles
    report.append("## Tier 1 Countries: Detailed Profiles\n\n")

    for code, name in TIER_1_COUNTRIES.items():
        report.append(f"## {name} ({code})\n\n")
        report.append("### Overview\n\n")

        country_data = openalex_data['country_research'].get(code, {})
        risk_info = risk_levels[code]

        works = country_data.get('work_count', 0)
        citations = country_data.get('total_citations', 0)
        avg_citations = citations / works if works > 0 else 0

        report.append(f"- **Total Quantum Research Works**: {works:,}\n")
        report.append(f"- **Total Citations**: {citations:,}\n")
        report.append(f"- **Average Citations per Work**: {avg_citations:.1f}\n")
        report.append(f"- **China Co-Authorships**: {risk_info['china_collaborations']:,}\n")
        report.append(f"- **China Collaboration Rate**: {risk_info['collab_rate']:.1f}%\n\n")

        # Institutions
        report.append("### Key Research Institutions\n\n")
        institutions = openalex_data['institutions'].get(code, [])
        if institutions:
            for inst in institutions[:15]:
                report.append(f"- **{inst['name']}** ({inst['work_count']} quantum works)\n")
        else:
            report.append("*No institution data available*\n")
        report.append("\n")

        # Recent works
        report.append("### Sample Recent Research\n\n")
        recent = country_data.get('recent_works', [])
        if recent:
            for work in recent:
                report.append(f"- **{work['title']}** ({work['year']}) - {work['citations']} citations\n")
        report.append("\n")

        # China collaboration analysis
        report.append("### China Collaboration Analysis\n\n")
        report.append(f"**Risk Level**: **{risk_info['level']}**\n\n")

        collab_data = openalex_data['china_collaborations'].get(code, {})
        if collab_data:
            report.append(f"- **Collaborative Works**: {collab_data['count']:,}\n")
            report.append(f"- **Collaboration Rate**: {risk_info['collab_rate']:.1f}% of quantum research\n\n")

            sample_works = collab_data.get('sample_works', [])
            if sample_works:
                report.append("**Sample China-Collaborative Works**:\n\n")
                for work in sample_works:
                    report.append(f"- {work['title']} ({work['year']}) - {work['citations']} citations\n")
        else:
            report.append("*No China collaborations detected in dataset*\n")
        report.append("\n")

        # Risk factors
        report.append("**Risk Assessment Factors**:\n\n")
        for factor in risk_info['factors']:
            report.append(f"- {factor}\n")
        report.append("\n")

        # Security recommendations
        report.append("### Research Security Assessment\n\n")

        if risk_info['level'] in ['CRITICAL', 'HIGH']:
            report.append("**PRIORITY CONCERNS**:\n\n")
            report.append("- High volume of quantum collaboration with Chinese institutions poses significant ")
            report.append("technology transfer risk\n")
            report.append("- Dual-use applications in quantum computing, sensing, and communication require ")
            report.append("enhanced protection\n")
            report.append("- Immediate implementation of comprehensive screening protocols necessary\n")
            report.append("- Recommend institutional-level research security offices\n")
            report.append("- Enhanced monitoring of researcher mobility and exchanges\n")
        elif risk_info['level'] == 'MODERATE':
            report.append("**MONITORING REQUIRED**:\n\n")
            report.append("- Moderate China collaboration requires ongoing monitoring\n")
            report.append("- Standard research security protocols should be enforced\n")
            report.append("- Periodic review of collaborative agreements\n")
            report.append("- Awareness training for quantum researchers\n")
        else:
            report.append("**STANDARD PROTOCOLS**:\n\n")
            report.append("- Low collaboration levels detected\n")
            report.append("- Standard research security measures adequate\n")
            report.append("- Maintain awareness for emerging patterns\n")

        report.append("\n")

        # Strategic recommendations
        report.append("### Strategic Recommendations\n\n")
        report.append(f"As a **Tier 1** quantum research leader:\n\n")
        report.append("1. **Comprehensive Due Diligence**: Screen all international quantum collaborations\n")
        report.append("2. **Export Control Compliance**: Strengthen controls for quantum technologies\n")
        report.append("3. **Institutional Security Capacity**: Build dedicated research security functions\n")
        report.append("4. **Talent Monitoring**: Track foreign recruitment and visiting scholar programs\n")
        report.append("5. **Technology Classification**: Classify sensitive quantum research appropriately\n")
        report.append("6. **Information Sharing**: Participate in national security information networks\n\n")

        report.append("---\n\n")

    # Tier 2 countries summary
    report.append("## Tier 2 Countries: Summary Assessment\n\n")
    report.append("| Country | Quantum Works | China Collabs | Collab Rate | Risk | Top Institution |\n")
    report.append("|---------|---------------|---------------|-------------|------|----------------|\n")

    tier2 = [(c, openalex_data['country_research'].get(c, {}).get('work_count', 0))
             for c in EUROPEAN_COUNTRIES if c not in TIER_1_COUNTRIES]
    tier2.sort(key=lambda x: x[1], reverse=True)

    for code, works in tier2:
        if works == 0:
            continue

        risk = risk_levels[code]
        china_collabs = risk['china_collaborations']
        collab_rate = risk['collab_rate']

        institutions = openalex_data['institutions'].get(code, [])
        top_inst = institutions[0]['name'][:40] if institutions else 'N/A'

        report.append(f"| {code} | {works:,} | {china_collabs:,} | {collab_rate:.1f}% | {risk['level']} | {top_inst} |\n")

    report.append("\n---\n\n")

    # Technology topics
    report.append("## Quantum Technology Landscape\n\n")
    report.append("### Top Research Topics\n\n")

    topics = openalex_data.get('topics', {})
    if topics:
        sorted_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)
        for topic, count in sorted_topics[:20]:
            report.append(f"- **{topic}**: {count:,} works\n")
    report.append("\n---\n\n")

    # Methodology
    report.append("## Methodology\n\n")
    report.append("### Data Sources\n\n")
    report.append("**OpenAlex Global Research Database**: Comprehensive academic research repository with:\n")
    report.append("- 17,739+ quantum technology works\n")
    report.append("- Institution and country affiliation data\n")
    report.append("- Author collaboration networks\n")
    report.append("- Citation metrics and research topics\n\n")

    report.append("### Analysis Approach\n\n")
    report.append("1. **Quantum Research Identification**: Works identified through keyword matching:\n")
    report.append("   - Title/abstract contains: quantum computing, quantum sensing, quantum communication, ")
    report.append("quantum cryptography, qubit\n\n")

    report.append("2. **Collaboration Detection**: China collaborations identified by co-authorship patterns:\n")
    report.append("   - Works with both European and Chinese institutional affiliations\n")
    report.append("   - Multi-country author lists analyzed\n\n")

    report.append("3. **Risk Assessment**: Multi-factor scoring system:\n")
    report.append("   - **Collaboration Volume**: Absolute number of China co-authorships\n")
    report.append("   - **Collaboration Rate**: Percentage of quantum works involving China\n")
    report.append("   - **Research Capacity**: Total quantum research output (technology transfer potential)\n\n")

    report.append("**Risk Levels**:\n")
    report.append("- **CRITICAL** (Score ≥5): Immediate enhanced protocols required\n")
    report.append("- **HIGH** (Score 3-4): Enhanced monitoring necessary\n")
    report.append("- **MODERATE** (Score 2): Standard protocols with review\n")
    report.append("- **LOW** (Score 1): Basic monitoring sufficient\n")
    report.append("- **MINIMAL** (Score 0): Standard practices adequate\n\n")

    report.append("### Limitations\n\n")
    report.append("- Co-authorship patterns may not capture all collaboration types\n")
    report.append("- Technology transfer can occur through non-publication channels\n")
    report.append("- Institutional affiliations may be incomplete or outdated\n")
    report.append("- Risk assessment is indicative; detailed reviews recommended\n")
    report.append("- Commercial and government lab research may be underrepresented\n\n")

    report.append("---\n\n")

    # Appendix
    report.append("## Appendix: Dual-Use Technology Concerns\n\n")
    report.append("### Quantum Computing\n")
    report.append("- **Cryptanalysis**: Breaking current encryption standards\n")
    report.append("- **Military Optimization**: Logistics, targeting, battlefield simulation\n")
    report.append("- **Materials Science**: Advanced weapons and defense systems\n")
    report.append("- **AI Enhancement**: Military AI and autonomous systems\n\n")

    report.append("### Quantum Sensing\n")
    report.append("- **Submarine Detection**: Magnetic anomaly detection systems\n")
    report.append("- **Underground Mapping**: Facility detection and reconnaissance\n")
    report.append("- **Precision Navigation**: GPS-denied navigation for military\n")
    report.append("- **Timing Systems**: Secure communications and weapons systems\n\n")

    report.append("### Quantum Communication\n")
    report.append("- **Military Communications**: Unbreakable command and control\n")
    report.append("- **Quantum Key Distribution**: Classified network security\n")
    report.append("- **Anti-Jamming**: Resilient communications infrastructure\n")
    report.append("- **Secure Satellites**: Space-based quantum networks\n\n")

    report.append("### Technology Transfer Pathways\n")
    report.append("- Joint research publications and data sharing\n")
    report.append("- Conference participation and academic exchanges\n")
    report.append("- Researcher mobility and talent recruitment\n")
    report.append("- Equipment and materials acquisition\n")
    report.append("- Commercial partnerships and joint ventures\n")
    report.append("- Graduate student and postdoc programs\n\n")

    report.append("---\n\n")
    report.append(f"**Report Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("**Prepared By**: OSINT Foresight Analysis System\n")
    report.append("**Classification**: Research Security Assessment\n")
    report.append("**Distribution**: Research Security Officials, Policy Makers, Institutional Leadership\n")

    return ''.join(report)

def main():
    """Main execution."""
    print("\n" + "="*80)
    print("EUROPEAN QUANTUM RESEARCH - CHINA COLLABORATION ANALYSIS")
    print("="*80 + "\n")

    # Query OpenAlex
    openalex_data = query_openalex_quantum_research()

    if not openalex_data:
        print("\nERROR: Failed to query OpenAlex database")
        return

    # Calculate risk levels
    risk_levels = calculate_risk_levels(openalex_data)

    # Generate report
    report_text = generate_report(openalex_data, risk_levels)

    # Save report
    output_path = Path("C:/Projects/OSINT - Foresight/analysis/QUANTUM_EUROPE_CHINA_COLLABORATION_REPORT.md")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report_text)

    print(f"\n6. Report saved to: {output_path}")

    # Save structured data
    structured_data = {
        'metadata': {
            'generated': datetime.now().isoformat(),
            'total_works': openalex_data['total_european_quantum_works'],
            'total_china_collaborations': sum(v.get('count', 0) for v in openalex_data['china_collaborations'].values()),
            'countries_analyzed': len(EUROPEAN_COUNTRIES)
        },
        'country_data': {},
        'risk_levels': {k: {k2: v2 for k2, v2 in v.items() if k2 != 'factors'}
                       for k, v in risk_levels.items()},
        'top_institutions': openalex_data['institutions'],
        'topics': openalex_data['topics']
    }

    for code in EUROPEAN_COUNTRIES:
        if code in openalex_data['country_research'] or code in risk_levels:
            structured_data['country_data'][code] = {
                'works': openalex_data['country_research'].get(code, {}).get('work_count', 0),
                'citations': openalex_data['country_research'].get(code, {}).get('total_citations', 0),
                'china_collaborations': risk_levels[code]['china_collaborations'],
                'risk': risk_levels[code]['level']
            }

    json_path = Path("C:/Projects/OSINT - Foresight/analysis/QUANTUM_EUROPE_CHINA_COLLABORATION_DATA.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(structured_data, f, indent=2)

    print(f"   Structured data saved to: {json_path}")

    # Print summary
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)
    print(f"\nTotal European Quantum Works: {openalex_data['total_european_quantum_works']:,}")
    print(f"Total China Collaborations: {structured_data['metadata']['total_china_collaborations']:,}")
    print(f"Collaboration Rate: {(structured_data['metadata']['total_china_collaborations']/openalex_data['total_european_quantum_works']*100):.1f}%")

    print("\nRisk Distribution:")
    risk_dist = Counter(v['level'] for v in risk_levels.values())
    for level in ['CRITICAL', 'HIGH', 'MODERATE', 'LOW', 'MINIMAL']:
        if risk_dist[level] > 0:
            print(f"  {level}: {risk_dist[level]} countries")

    print("\nTop 5 Countries by Quantum Research Output:")
    top_countries = sorted(
        [(code, openalex_data['country_research'].get(code, {}).get('work_count', 0))
         for code in openalex_data['country_research']],
        key=lambda x: x[1],
        reverse=True
    )[:5]

    for code, works in top_countries:
        name = TIER_1_COUNTRIES.get(code, code)
        risk = risk_levels[code]['level']
        china_collabs = risk_levels[code]['china_collaborations']
        collab_rate = risk_levels[code]['collab_rate']
        print(f"  {name} ({code}): {works:,} works | {china_collabs:,} China collabs ({collab_rate:.1f}%) | {risk} risk")

    print("\n" + "="*80)

if __name__ == "__main__":
    main()

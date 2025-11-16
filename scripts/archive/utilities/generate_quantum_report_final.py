#!/usr/bin/env python3
"""
Generate comprehensive European quantum research with China collaboration analysis.
Uses OpenAlex osint_master.db with correct schema.
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
        'works_by_year': {}
    }

    # Step 1: Find all quantum works with European authors
    print("\n1. Finding quantum research works...")

    quantum_query = """
    SELECT DISTINCT
        w.work_id,
        w.title,
        w.publication_year,
        w.cited_by_count,
        w.doi,
        w.abstract,
        w.primary_topic
    FROM openalex_works w
    JOIN openalex_work_authors wa ON w.work_id = wa.work_id
    WHERE (
        w.title LIKE '%quantum%'
        OR w.abstract LIKE '%quantum computing%'
        OR w.abstract LIKE '%quantum sensing%'
        OR w.abstract LIKE '%quantum communication%'
        OR w.abstract LIKE '%quantum cryptography%'
        OR w.abstract LIKE '%qubit%'
        OR w.abstract LIKE '%quantum entanglement%'
        OR w.abstract LIKE '%quantum information%'
    )
    AND wa.country_code IN ({})
    ORDER BY w.publication_year DESC, w.cited_by_count DESC
    """.format(','.join(['?' for _ in EUROPEAN_COUNTRIES]))

    cursor.execute(quantum_query, EUROPEAN_COUNTRIES)
    european_quantum_works = cursor.fetchall()
    print(f"   Found {len(european_quantum_works)} European quantum works")

    results['total_european_quantum_works'] = len(european_quantum_works)

    # Step 2: For each work, get all country affiliations
    print("\n2. Analyzing country affiliations and China collaborations...")

    work_countries = {}  # work_id -> set of country codes
    work_details = {}  # work_id -> work details

    for work in european_quantum_works:
        work_id = work['work_id']
        work_details[work_id] = dict(work)

        # Get all countries for this work
        cursor.execute("""
            SELECT DISTINCT country_code
            FROM openalex_work_authors
            WHERE work_id = ? AND country_code IS NOT NULL
        """, (work_id,))

        countries = set(row['country_code'] for row in cursor.fetchall())
        work_countries[work_id] = countries

        # Track if this is a China collaboration
        is_china_collab = 'CN' in countries
        european_countries_in_work = countries.intersection(EUROPEAN_COUNTRIES)

        # Process each European country in this work
        for country in european_countries_in_work:
            if country not in results['country_research']:
                results['country_research'][country] = {
                    'work_count': 0,
                    'total_citations': 0,
                    'recent_works': [],
                    'institutions': set()
                }

            results['country_research'][country]['work_count'] += 1
            results['country_research'][country]['total_citations'] += work['cited_by_count'] or 0

            # Add to recent works (top 5 by citations)
            if len(results['country_research'][country]['recent_works']) < 5:
                results['country_research'][country]['recent_works'].append({
                    'title': work['title'],
                    'year': work['publication_year'],
                    'citations': work['cited_by_count'] or 0
                })

            # Track China collaboration
            if is_china_collab:
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

    print(f"   Processed {len(work_countries)} works across {len(results['country_research'])} countries")
    print(f"   Detected China collaborations in {len(results['china_collaborations'])} countries")

    # Step 3: Get institutions
    print("\n3. Identifying top research institutions...")

    for country in results['country_research'].keys():
        cursor.execute("""
            SELECT
                i.institution_id,
                i.display_name,
                COUNT(DISTINCT wa.work_id) as work_count
            FROM openalex_institutions i
            JOIN openalex_work_authors wa ON i.institution_id = wa.institution_id
            JOIN openalex_works w ON wa.work_id = w.work_id
            WHERE i.country_code = ?
            AND (w.title LIKE '%quantum%' OR w.abstract LIKE '%quantum%')
            GROUP BY i.institution_id, i.display_name
            ORDER BY work_count DESC
            LIMIT 20
        """, (country,))

        institutions = cursor.fetchall()
        results['institutions'][country] = [
            {'name': inst['display_name'], 'work_count': inst['work_count']}
            for inst in institutions
        ]

    print(f"   Found institutions for {len(results['institutions'])} countries")

    # Step 4: Analyze topics
    print("\n4. Analyzing research topics...")

    topic_counter = Counter()
    for work in european_quantum_works:
        if work['primary_topic']:
            topic_counter[work['primary_topic']] += 1

    results['topics'] = dict(topic_counter.most_common(30))
    print(f"   Identified {len(results['topics'])} distinct topics")

    # Step 5: Temporal analysis
    print("\n5. Analyzing temporal trends...")

    year_counter = Counter()
    for work in european_quantum_works:
        if work['publication_year']:
            year_counter[work['publication_year']] += 1

    results['works_by_year'] = dict(sorted(year_counter.items()))
    print(f"   Temporal range: {min(year_counter.keys())} - {max(year_counter.keys())}")

    conn.close()
    return results

def calculate_risk_levels(openalex_data):
    """Calculate China collaboration risk levels."""
    print("\n6. Calculating risk levels...")

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
    print("\n7. Generating report...")

    report = []
    report.append("# European Quantum Research: China Collaboration Analysis\n\n")
    report.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("**Classification**: RESEARCH SECURITY ASSESSMENT\n")
    report.append("**Data Source**: OpenAlex Global Research Database (F:/OSINT_WAREHOUSE/osint_master.db)\n\n")
    report.append("---\n\n")

    # Executive Summary
    report.append("## Executive Summary\n\n")

    total_works = openalex_data['total_european_quantum_works']
    total_collaborations = sum(v.get('count', 0) for v in openalex_data['china_collaborations'].values())

    if total_works == 0:
        total_works = 1  # Avoid division by zero

    report.append("### Key Findings\n\n")
    report.append(f"- **Total European Quantum Research Works Analyzed**: {total_works:,}\n")
    report.append(f"- **China Co-Authored Works**: {total_collaborations:,}\n")
    report.append(f"- **Overall China Collaboration Rate**: {(total_collaborations/total_works*100):.1f}%\n")
    report.append(f"- **European Countries with Quantum Research**: {len([c for c in openalex_data['country_research'] if openalex_data['country_research'][c]['work_count'] > 0])}\n")
    report.append(f"- **Research Institutions Identified**: {sum(len(v) for v in openalex_data['institutions'].values())}\n\n")

    # Risk distribution
    risk_dist = Counter(v['level'] for v in risk_levels.values() if v['total_works'] > 0)
    report.append("### China Collaboration Risk Distribution\n\n")
    for level in ['CRITICAL', 'HIGH', 'MODERATE', 'LOW', 'MINIMAL']:
        if risk_dist[level] > 0:
            report.append(f"- **{level}**: {risk_dist[level]} countries\n")
    report.append("\n")

    # Tier 1 summary table
    report.append("### Tier 1 Countries at a Glance\n\n")
    report.append("| Country | Quantum Works | China Collabs | Collab Rate | Risk Level |\n")
    report.append("|---------|---------------|---------------|-------------|------------|\n")

    for code, name in sorted(TIER_1_COUNTRIES.items(), key=lambda x: x[1]):
        works = openalex_data['country_research'].get(code, {}).get('work_count', 0)
        china_collabs = risk_levels[code]['china_collaborations']
        collab_rate = risk_levels[code]['collab_rate']
        risk = risk_levels[code]['level']
        report.append(f"| {name} | {works:,} | {china_collabs:,} | {collab_rate:.1f}% | **{risk}** |\n")
    report.append("\n")

    # Critical findings
    report.append("### Critical Findings\n\n")

    high_risk = [(code, risk_levels[code]) for code in risk_levels
                 if risk_levels[code]['level'] in ['CRITICAL', 'HIGH'] and risk_levels[code]['total_works'] > 0]
    high_risk.sort(key=lambda x: x[1]['score'], reverse=True)

    if high_risk:
        report.append("**Countries Requiring Enhanced Research Security Measures**:\n\n")
        for code, risk in high_risk[:10]:
            name = TIER_1_COUNTRIES.get(code, code)
            report.append(f"#### {name} ({code}) - {risk['level']} Risk\n\n")
            report.append(f"- **China Co-authorships**: {risk['china_collaborations']:,}\n")
            report.append(f"- **Total Quantum Works**: {risk['total_works']:,}\n")
            report.append(f"- **Collaboration Rate**: {risk['collab_rate']:.1f}%\n\n")
            if risk['factors']:
                report.append("**Risk Factors**:\n")
                for factor in risk['factors']:
                    report.append(f"- {factor}\n")
            report.append("\n")
    else:
        report.append("*No high-risk countries identified in current dataset.*\n\n")

    # Strategic implications
    report.append("### Strategic Implications\n\n")
    report.append("1. **Significant Technology Transfer Risk**: ")
    if total_collaborations > 0:
        report.append(f"With {total_collaborations:,} China co-authored quantum works, ")
    report.append("European quantum research collaboration creates potential pathways for dual-use technology transfer.\n\n")

    report.append("2. **Research Security Gaps**: The {:.1f}% China collaboration rate indicates substantial ".format(
        total_collaborations/total_works*100))
    report.append("scientific exchange requiring enhanced vetting protocols.\n\n")

    report.append("3. **Critical Technology Exposure**: Quantum technologies have clear military applications ")
    report.append("including cryptanalysis, submarine detection, and secure communications.\n\n")

    report.append("4. **Institutional Vulnerability**: Many European research institutions lack standardized ")
    report.append("protocols for assessing international collaboration risks.\n\n")

    report.append("### Immediate Recommendations\n\n")
    report.append("1. **Policy Framework**: Develop EU-wide research security standards for quantum technologies\n")
    report.append("2. **Enhanced Screening**: Implement mandatory due diligence for China quantum collaborations\n")
    report.append("3. **Technology Classification**: Review and classify sensitive quantum research areas\n")
    report.append("4. **Institutional Capacity**: Establish research security offices at major quantum centers\n")
    report.append("5. **Information Sharing**: Create threat intelligence sharing mechanisms across EU\n")
    report.append("6. **Researcher Training**: Mandatory security awareness for quantum scientists\n\n")

    report.append("---\n\n")

    # Detailed country profiles - Tier 1
    report.append("## Tier 1 Countries: Detailed Profiles\n\n")
    report.append("*Major quantum research hubs requiring comprehensive security protocols*\n\n")

    for code, name in sorted(TIER_1_COUNTRIES.items(), key=lambda x: x[1]):
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
        if works > 0:
            report.append("### Sample Recent Research\n\n")
            recent = country_data.get('recent_works', [])
            if recent:
                for work in recent:
                    title = work['title'][:150] + "..." if len(work['title']) > 150 else work['title']
                    report.append(f"- **{title}** ({work['year']}) - {work['citations']} citations\n")
            report.append("\n")

        # China collaboration analysis
        report.append("### China Collaboration Analysis\n\n")
        report.append(f"**Risk Level**: **{risk_info['level']}**\n\n")

        collab_data = openalex_data['china_collaborations'].get(code, {})
        if collab_data and collab_data.get('count', 0) > 0:
            report.append(f"- **Collaborative Works**: {collab_data['count']:,}\n")
            report.append(f"- **Collaboration Rate**: {risk_info['collab_rate']:.1f}% of quantum research\n\n")

            sample_works = collab_data.get('sample_works', [])
            if sample_works:
                report.append("**Sample China-Collaborative Works**:\n\n")
                for work in sample_works:
                    title = work['title'][:150] + "..." if len(work['title']) > 150 else work['title']
                    report.append(f"- {title} ({work['year']}) - {work['citations']} citations\n")
        else:
            report.append("*No China collaborations detected in dataset*\n")
        report.append("\n")

        # Risk factors
        if risk_info['factors']:
            report.append("**Risk Assessment Factors**:\n\n")
            for factor in risk_info['factors']:
                report.append(f"- {factor}\n")
            report.append("\n")

        # Security recommendations
        report.append("### Research Security Assessment\n\n")

        if risk_info['level'] in ['CRITICAL', 'HIGH']:
            report.append("**PRIORITY CONCERNS**:\n\n")
            report.append("- High volume of quantum collaboration with Chinese institutions poses significant technology transfer risk\n")
            report.append("- Dual-use applications in quantum computing, sensing, and communication require enhanced protection\n")
            report.append("- Immediate implementation of comprehensive screening protocols necessary\n")
            report.append("- Recommend institutional-level research security offices with dedicated quantum expertise\n")
            report.append("- Enhanced monitoring of researcher mobility, exchanges, and equipment transfers\n")
        elif risk_info['level'] == 'MODERATE':
            report.append("**MONITORING REQUIRED**:\n\n")
            report.append("- Moderate China collaboration requires ongoing monitoring\n")
            report.append("- Standard research security protocols should be enforced and periodically reviewed\n")
            report.append("- Implement screening for sensitive quantum technology collaborations\n")
            report.append("- Regular awareness training for quantum researchers\n")
        else:
            report.append("**STANDARD PROTOCOLS**:\n\n")
            report.append("- Lower collaboration levels detected\n")
            report.append("- Standard research security measures adequate with ongoing vigilance\n")
            report.append("- Maintain awareness for emerging collaboration patterns\n")
            report.append("- Baseline security training recommended\n")

        report.append("\n")

        # Strategic recommendations
        report.append("### Strategic Recommendations\n\n")
        report.append(f"As a **Tier 1** quantum research leader, {name} should:\n\n")
        report.append("1. **Comprehensive Due Diligence**: Screen all international quantum collaborations for technology transfer risks\n")
        report.append("2. **Export Control Compliance**: Strengthen controls for quantum technologies and related equipment\n")
        report.append("3. **Institutional Security Capacity**: Build dedicated research security functions with quantum domain expertise\n")
        report.append("4. **Talent Monitoring**: Track foreign recruitment programs and visiting scholar arrangements\n")
        report.append("5. **Technology Classification**: Classify sensitive quantum research with appropriate access controls\n")
        report.append("6. **Information Sharing**: Participate actively in national and EU security information networks\n")
        report.append("7. **Researcher Education**: Mandate security awareness training covering technology transfer risks\n\n")

        report.append("---\n\n")

    # Tier 2 countries summary
    report.append("## Tier 2 Countries: Summary Assessment\n\n")
    report.append("*Secondary quantum research participants*\n\n")
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
        top_inst = institutions[0]['name'][:40] + "..." if institutions and len(institutions[0]['name']) > 40 else (institutions[0]['name'] if institutions else 'N/A')

        report.append(f"| {code} | {works:,} | {china_collabs:,} | {collab_rate:.1f}% | {risk['level']} | {top_inst} |\n")

    report.append("\n---\n\n")

    # Technology landscape
    report.append("## Quantum Technology Landscape\n\n")
    report.append("### Top Research Topics\n\n")

    topics = openalex_data.get('topics', {})
    if topics:
        sorted_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)
        report.append("| Research Topic | Works |\n")
        report.append("|----------------|-------|\n")
        for topic, count in sorted_topics[:20]:
            report.append(f"| {topic} | {count:,} |\n")
    else:
        report.append("*Topic data not available*\n")
    report.append("\n")

    # Temporal trends
    report.append("### Temporal Trends\n\n")
    years = openalex_data.get('works_by_year', {})
    if years:
        recent_years = {k: v for k, v in sorted(years.items(), reverse=True)[:10]}
        report.append("| Year | Publications |\n")
        report.append("|------|-------------|\n")
        for year, count in sorted(recent_years.items(), reverse=True):
            report.append(f"| {year} | {count:,} |\n")
    report.append("\n---\n\n")

    # Methodology
    report.append("## Methodology\n\n")
    report.append("### Data Sources\n\n")
    report.append("**OpenAlex Global Research Database (osint_master.db)**:\n")
    report.append("- Comprehensive academic research repository\n")
    report.append(f"- {total_works:,} European quantum technology works identified\n")
    report.append("- Institution and country affiliation data via author metadata\n")
    report.append("- Citation metrics and research topics included\n")
    report.append("- Cross-national collaboration patterns analyzed\n\n")

    report.append("### Analysis Approach\n\n")
    report.append("1. **Quantum Research Identification**: Works identified through comprehensive keyword matching:\n")
    report.append("   - Keywords: quantum, quantum computing, quantum sensing, quantum communication, quantum cryptography, qubit, quantum entanglement, quantum information\n")
    report.append("   - Searched in: titles and abstracts\n\n")

    report.append("2. **Collaboration Detection**: China collaborations identified through co-authorship analysis:\n")
    report.append("   - Works with authors from both European and Chinese institutions\n")
    report.append("   - Country affiliations determined via openalex_work_authors table\n\n")

    report.append("3. **Risk Assessment Framework**: Multi-factor scoring system:\n")
    report.append("   - **Collaboration Volume** (0-3 points): Absolute number of China co-authorships\n")
    report.append("   - **Collaboration Rate** (0-2 points): Percentage of quantum works involving China\n")
    report.append("   - **Research Capacity** (0-2 points): Total quantum research output indicating technology transfer potential\n\n")

    report.append("**Risk Level Thresholds**:\n")
    report.append("- **CRITICAL** (Score ≥5): Immediate enhanced protocols required\n")
    report.append("- **HIGH** (Score 3-4): Enhanced monitoring and screening necessary\n")
    report.append("- **MODERATE** (Score 2): Standard protocols with periodic review\n")
    report.append("- **LOW** (Score 1): Basic monitoring sufficient\n")
    report.append("- **MINIMAL** (Score 0): Standard research practices adequate\n\n")

    report.append("### Limitations\n\n")
    report.append("- **Co-authorship Coverage**: Not all collaboration types captured (consulting, equipment sharing, etc.)\n")
    report.append("- **Publication Lag**: Recent collaborations may not yet be published\n")
    report.append("- **Institutional Affiliations**: May be incomplete or outdated in source data\n")
    report.append("- **Keyword Matching**: May miss some quantum research with specialized terminology\n")
    report.append("- **Commercial Research**: Industry and classified government research not included\n")
    report.append("- **Risk Assessment**: Indicative only; detailed institutional reviews recommended\n\n")

    report.append("---\n\n")

    # Appendix
    report.append("## Appendix: Dual-Use Technology Concerns\n\n")
    report.append("### Quantum Computing\n\n")
    report.append("**Military Applications**:\n")
    report.append("- **Cryptanalysis**: Breaking current encryption standards (RSA, ECC)\n")
    report.append("- **Military Optimization**: Logistics, targeting, resource allocation\n")
    report.append("- **Materials Science**: Design of advanced weapons and defense systems\n")
    report.append("- **AI Enhancement**: Quantum machine learning for autonomous weapons\n")
    report.append("- **Simulation**: Nuclear weapons, hypersonic systems modeling\n\n")

    report.append("### Quantum Sensing\n\n")
    report.append("**Military Applications**:\n")
    report.append("- **Submarine Detection**: Ultra-sensitive magnetic anomaly detection\n")
    report.append("- **Underground Mapping**: Detection of tunnels and buried facilities\n")
    report.append("- **Precision Navigation**: GPS-denied navigation for missiles and aircraft\n")
    report.append("- **Timing Systems**: Secure communications and weapons synchronization\n")
    report.append("- **Gravimetry**: Mapping underground structures and resources\n\n")

    report.append("### Quantum Communication\n\n")
    report.append("**Military Applications**:\n")
    report.append("- **Secure C2**: Unbreakable command and control networks\n")
    report.append("- **Quantum Key Distribution**: Protection of classified communications\n")
    report.append("- **Anti-Jamming**: Resilient communications infrastructure\n")
    report.append("- **Satellite Networks**: Space-based quantum-secure communications\n")
    report.append("- **Nuclear Command**: Ultra-secure strategic communications\n\n")

    report.append("### Technology Transfer Pathways\n\n")
    report.append("**Direct Pathways**:\n")
    report.append("- Joint research publications with technical details\n")
    report.append("- Conference presentations and proceedings\n")
    report.append("- Researcher exchanges and visiting scholar programs\n")
    report.append("- Graduate student training and postdoctoral fellows\n")
    report.append("- Equipment procurement and material purchases\n\n")

    report.append("**Indirect Pathways**:\n")
    report.append("- Technical consulting arrangements\n")
    report.append("- Commercial joint ventures and licensing\n")
    report.append("- Academic-industry partnerships\n")
    report.append("- Open-source software and algorithms\n")
    report.append("- Patent applications and technical documentation\n\n")

    report.append("---\n\n")
    report.append(f"**Report Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("**Prepared By**: OSINT Foresight Analysis System\n")
    report.append("**Classification**: Research Security Assessment\n")
    report.append("**Distribution**: Research Security Officials, Policy Makers, Institutional Leadership\n")
    report.append("**Contact**: For methodology questions or data requests, contact institutional research security office\n")

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

    print(f"\n   Report saved to: {output_path}")

    # Save structured data
    structured_data = {
        'metadata': {
            'generated': datetime.now().isoformat(),
            'total_works': openalex_data['total_european_quantum_works'],
            'total_china_collaborations': sum(v.get('count', 0) for v in openalex_data['china_collaborations'].values()),
            'countries_analyzed': len(EUROPEAN_COUNTRIES),
            'countries_with_research': len([c for c in openalex_data['country_research'] if openalex_data['country_research'][c]['work_count'] > 0])
        },
        'country_data': {},
        'risk_levels': {k: {k2: v2 for k2, v2 in v.items() if k2 != 'factors'}
                       for k, v in risk_levels.items() if v['total_works'] > 0},
        'top_institutions': {k: v[:10] for k, v in openalex_data['institutions'].items()},
        'topics': openalex_data['topics'],
        'temporal_trends': openalex_data['works_by_year']
    }

    for code in EUROPEAN_COUNTRIES:
        if code in openalex_data['country_research'] and openalex_data['country_research'][code]['work_count'] > 0:
            structured_data['country_data'][code] = {
                'works': openalex_data['country_research'][code]['work_count'],
                'citations': openalex_data['country_research'][code]['total_citations'],
                'china_collaborations': risk_levels[code]['china_collaborations'],
                'collab_rate': risk_levels[code]['collab_rate'],
                'risk': risk_levels[code]['level']
            }

    json_path = Path("C:/Projects/OSINT - Foresight/analysis/QUANTUM_EUROPE_CHINA_COLLABORATION_DATA.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(structured_data, f, indent=2)

    print(f"   Structured data saved to: {json_path}")

    # Print summary
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE - KEY FINDINGS")
    print("="*80)
    print(f"\nTotal European Quantum Works: {openalex_data['total_european_quantum_works']:,}")
    print(f"Total China Collaborations: {structured_data['metadata']['total_china_collaborations']:,}")

    if openalex_data['total_european_quantum_works'] > 0:
        print(f"Overall Collaboration Rate: {(structured_data['metadata']['total_china_collaborations']/openalex_data['total_european_quantum_works']*100):.1f}%")

    print("\nRisk Distribution (countries with research):")
    risk_dist = Counter(v['level'] for v in risk_levels.values() if v['total_works'] > 0)
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

#!/usr/bin/env python3
"""
OpenAlex bulk data processor for Italy-China research collaborations
Processes large-scale collaboration networks with proper methodology
"""

import json
import requests
import logging
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict
from datetime import datetime
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OpenAlexBulkProcessor:
    """Process OpenAlex data to map Italy-China research collaborations"""

    def __init__(self):
        self.base_url = "https://api.openalex.org"
        self.output_dir = Path("data/processed/openalex_bulk")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Critical technology domains for security assessment
        self.critical_domains = {
            'artificial_intelligence': ['artificial intelligence', 'machine learning', 'deep learning', 'neural network'],
            'quantum': ['quantum computing', 'quantum communication', 'quantum cryptography', 'quantum sensor'],
            'biotechnology': ['crispr', 'gene editing', 'synthetic biology', 'bioweapon', 'pathogen'],
            'semiconductors': ['semiconductor', 'microchip', 'processor', 'lithography', 'wafer'],
            'aerospace': ['satellite', 'rocket', 'spacecraft', 'hypersonic', 'missile'],
            'nuclear': ['nuclear', 'uranium', 'plutonium', 'fusion', 'fission'],
            'cyber': ['cybersecurity', 'encryption', 'vulnerability', 'exploit', 'malware'],
            'materials': ['graphene', 'metamaterial', 'superconductor', 'nanomaterial', 'composite'],
            'energy': ['battery', 'solar cell', 'fuel cell', 'energy storage', 'renewable'],
            'defense': ['radar', 'sonar', 'stealth', 'electronic warfare', 'targeting']
        }

        # Top Italian research institutions to analyze
        self.italian_institutions = [
            "I4706267",  # Sapienza
            "I861853513",  # Bologna
            "I189158063",  # Milan
            "I9360294",  # Padua
            "I136199984",  # Politecnico Milano
            "I158479042",  # Turin
            "I29078006",  # Pisa
            "I30642925",  # Florence
            "I107660666",  # Rome Tor Vergata
            "I119021686",  # CNR
            "I868745443",  # INFN
            "I200765121",  # Politecnico Torino
            "I39565521",  # Naples Federico II
            "I74801974",  # Genoa
            "I119985460",  # ENEA
            "I198244214",  # IIT
            "I4210107718",  # Sant'Anna Pisa
            "I204730241",  # Trieste
            "I168635309",  # Bocconi
            "I70931966"  # Catholic University
        ]

    def fetch_institution_collaborations(self, institution_id: str, year: int) -> Dict:
        """Fetch all papers from an institution for a given year"""
        logger.info(f"Fetching papers for institution {institution_id} in {year}")

        url = f"{self.base_url}/works"
        params = {
            'filter': f'institutions.id:{institution_id},publication_year:{year}',
            'per_page': 200,
            'cursor': '*'
        }

        all_works = []
        page = 0

        while True:
            try:
                response = requests.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                if not data.get('results'):
                    break

                all_works.extend(data['results'])
                page += 1

                # Check for next page
                if not data.get('meta', {}).get('next_cursor'):
                    break

                params['cursor'] = data['meta']['next_cursor']

                # Rate limiting
                time.sleep(0.1)

                # Log progress
                if page % 10 == 0:
                    logger.info(f"  Processed {len(all_works)} papers...")

            except Exception as e:
                logger.error(f"Error fetching page {page}: {e}")
                break

        logger.info(f"  Total papers found: {len(all_works)}")
        return {'institution_id': institution_id, 'year': year, 'works': all_works}

    def analyze_china_collaborations(self, works: List[Dict]) -> Dict:
        """Analyze works for China collaborations with detailed classification"""

        analysis = {
            'total_papers': len(works),
            'china_collaborations': 0,
            'critical_tech_collaborations': 0,
            'by_domain': defaultdict(int),
            'chinese_institutions': defaultdict(int),
            'collaboration_types': defaultdict(int),
            'high_impact_collaborations': [],
            'security_concerns': []
        }

        for work in works:
            # Check all author affiliations
            has_italian = False
            has_chinese = False
            chinese_institutions = []

            for authorship in work.get('authorships', []):
                for institution in authorship.get('institutions', []):
                    country = institution.get('country_code', '')

                    if country == 'IT':
                        has_italian = True
                    elif country == 'CN':
                        has_chinese = True
                        chinese_institutions.append(institution.get('display_name', 'Unknown'))

            # Count if both Italian and Chinese authors
            if has_italian and has_chinese:
                analysis['china_collaborations'] += 1

                # Track Chinese institutions
                for inst in chinese_institutions:
                    analysis['chinese_institutions'][inst] += 1

                # Analyze research domain
                title = work.get('title', '').lower()
                abstract = work.get('abstract', '').lower() if work.get('abstract') else ''
                full_text = f"{title} {abstract}"

                # Check critical domains
                is_critical = False
                for domain, keywords in self.critical_domains.items():
                    if any(kw in full_text for kw in keywords):
                        analysis['by_domain'][domain] += 1
                        is_critical = True

                        # Flag high-risk collaborations
                        if any(risky in inst.lower() for inst in chinese_institutions
                               for risky in ['military', 'defense', 'pla', 'nudt', 'caep']):
                            concern = {
                                'title': work.get('title', 'Unknown'),
                                'year': work.get('publication_year'),
                                'domain': domain,
                                'chinese_institutions': chinese_institutions,
                                'doi': work.get('doi'),
                                'concern_level': 'HIGH'
                            }
                            analysis['security_concerns'].append(concern)

                if is_critical:
                    analysis['critical_tech_collaborations'] += 1

                # Track high-impact collaborations
                citations = work.get('cited_by_count', 0)
                if citations > 50:  # Highly cited
                    analysis['high_impact_collaborations'].append({
                        'title': work.get('title', 'Unknown'),
                        'citations': citations,
                        'chinese_institutions': chinese_institutions,
                        'doi': work.get('doi')
                    })

                # Classify collaboration type
                num_authors = len(work.get('authorships', []))
                if num_authors > 10:
                    analysis['collaboration_types']['large_consortium'] += 1
                elif num_authors > 4:
                    analysis['collaboration_types']['multi_group'] += 1
                else:
                    analysis['collaboration_types']['bilateral'] += 1

        return analysis

    def process_institution_bulk(self, institution_id: str, institution_name: str,
                               start_year: int = 2020, end_year: int = 2024) -> Dict:
        """Process all years for an institution"""
        logger.info(f"Processing {institution_name} ({institution_id})")

        institution_analysis = {
            'institution_id': institution_id,
            'institution_name': institution_name,
            'period': f"{start_year}-{end_year}",
            'by_year': {},
            'total_papers': 0,
            'total_china_collaborations': 0,
            'total_critical_tech': 0,
            'top_chinese_partners': defaultdict(int),
            'domain_breakdown': defaultdict(int),
            'security_concerns': []
        }

        for year in range(start_year, end_year + 1):
            # Fetch data
            year_data = self.fetch_institution_collaborations(institution_id, year)

            # Analyze collaborations
            analysis = self.analyze_china_collaborations(year_data['works'])

            # Store year analysis
            institution_analysis['by_year'][year] = {
                'total_papers': analysis['total_papers'],
                'china_collaborations': analysis['china_collaborations'],
                'critical_tech': analysis['critical_tech_collaborations'],
                'collaboration_rate': (analysis['china_collaborations'] / analysis['total_papers'] * 100)
                                     if analysis['total_papers'] > 0 else 0
            }

            # Aggregate totals
            institution_analysis['total_papers'] += analysis['total_papers']
            institution_analysis['total_china_collaborations'] += analysis['china_collaborations']
            institution_analysis['total_critical_tech'] += analysis['critical_tech_collaborations']

            # Aggregate partners
            for partner, count in analysis['chinese_institutions'].items():
                institution_analysis['top_chinese_partners'][partner] += count

            # Aggregate domains
            for domain, count in analysis['by_domain'].items():
                institution_analysis['domain_breakdown'][domain] += count

            # Collect security concerns
            institution_analysis['security_concerns'].extend(analysis['security_concerns'])

        # Calculate overall rate
        institution_analysis['overall_collaboration_rate'] = (
            institution_analysis['total_china_collaborations'] /
            institution_analysis['total_papers'] * 100
        ) if institution_analysis['total_papers'] > 0 else 0

        return institution_analysis

    def generate_comprehensive_report(self, all_analyses: List[Dict]):
        """Generate comprehensive OpenAlex analysis report"""
        report_lines = [
            "# Italy-China Research Collaboration Analysis (OpenAlex)",
            f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d')}",
            "**Period:** 2020-2024",
            "**Methodology:** Institutional country code analysis (accurate method)",
            "",
            "## Executive Summary",
            "",
            "Analysis of research collaborations between Italian and Chinese institutions",
            "reveals strategic vulnerabilities in critical technology domains.",
            "",
            "## Key Findings",
            ""
        ]

        # Calculate aggregates
        total_papers = sum(a['total_papers'] for a in all_analyses)
        total_china = sum(a['total_china_collaborations'] for a in all_analyses)
        total_critical = sum(a['total_critical_tech'] for a in all_analyses)
        avg_rate = (total_china / total_papers * 100) if total_papers > 0 else 0

        report_lines.extend([
            f"- **Total Papers Analyzed:** {total_papers:,}",
            f"- **Italy-China Collaborations:** {total_china:,}",
            f"- **Average Collaboration Rate:** {avg_rate:.2f}%",
            f"- **Critical Technology Papers:** {total_critical:,}",
            "",
            "## Institution-Level Analysis",
            ""
        ])

        # Sort by collaboration rate
        sorted_analyses = sorted(all_analyses,
                               key=lambda x: x['overall_collaboration_rate'],
                               reverse=True)

        for analysis in sorted_analyses[:10]:  # Top 10
            report_lines.extend([
                f"### {analysis['institution_name']}",
                f"- Total Papers: {analysis['total_papers']:,}",
                f"- China Collaborations: {analysis['total_china_collaborations']:,}",
                f"- Collaboration Rate: {analysis['overall_collaboration_rate']:.2f}%",
                f"- Critical Tech Papers: {analysis['total_critical_tech']:,}",
                ""
            ])

            # Top Chinese partners
            if analysis['top_chinese_partners']:
                report_lines.append("**Top Chinese Partners:**")
                for partner, count in sorted(dict(analysis['top_chinese_partners']).items(),
                                           key=lambda x: x[1], reverse=True)[:5]:
                    report_lines.append(f"- {partner}: {count} papers")
                report_lines.append("")

            # Domain breakdown
            if analysis['domain_breakdown']:
                report_lines.append("**Critical Domains:**")
                for domain, count in sorted(dict(analysis['domain_breakdown']).items(),
                                          key=lambda x: x[1], reverse=True):
                    report_lines.append(f"- {domain}: {count} papers")
                report_lines.append("")

        # Security concerns section
        all_concerns = []
        for analysis in all_analyses:
            all_concerns.extend(analysis['security_concerns'])

        if all_concerns:
            report_lines.extend([
                "## Security Concerns",
                "",
                f"**High-Risk Collaborations Identified:** {len(all_concerns)}",
                "",
                "### Examples of Concerning Collaborations:",
                ""
            ])

            for concern in all_concerns[:10]:  # Top 10
                report_lines.extend([
                    f"**{concern['title'][:100]}...**",
                    f"- Domain: {concern['domain']}",
                    f"- Chinese Partners: {', '.join(concern['chinese_institutions'][:3])}",
                    f"- Concern Level: {concern['concern_level']}",
                    ""
                ])

        # Risk assessment
        report_lines.extend([
            "## Risk Assessment",
            "",
            "### Technology Transfer Risks",
            ""
        ])

        # Aggregate domain risks
        all_domains = defaultdict(int)
        for analysis in all_analyses:
            for domain, count in analysis['domain_breakdown'].items():
                all_domains[domain] += count

        for domain, count in sorted(all_domains.items(), key=lambda x: x[1], reverse=True):
            risk_level = "CRITICAL" if count > 100 else "HIGH" if count > 50 else "MEDIUM"
            report_lines.append(f"- **{domain.replace('_', ' ').title()}:** {count} papers ({risk_level} risk)")

        report_lines.extend([
            "",
            "## Recommendations",
            "",
            "1. **Immediate:** Review all critical technology collaborations with Chinese military-affiliated institutions",
            "2. **Short-term:** Implement approval process for sensitive research collaborations",
            "3. **Medium-term:** Develop guidelines for international research partnerships",
            "4. **Long-term:** Build domestic research capacity to reduce dependency",
            "",
            "## Conclusion",
            "",
            f"The {avg_rate:.2f}% collaboration rate with China, while not extreme, concentrates in",
            "critical technology areas that could enable strategic vulnerabilities. The presence of",
            f"{len(all_concerns)} high-risk collaborations requires immediate review and potential",
            "restrictions to protect Italian technological sovereignty."
        ])

        return "\n".join(report_lines)

    def run_bulk_analysis(self):
        """Run comprehensive bulk analysis"""
        logger.info("Starting OpenAlex bulk analysis...")

        # Map institution IDs to names
        institution_names = {
            "I4706267": "Sapienza University of Rome",
            "I861853513": "University of Bologna",
            "I189158063": "University of Milan",
            "I9360294": "University of Padua",
            "I136199984": "Politecnico di Milano",
            "I158479042": "University of Turin",
            "I29078006": "University of Pisa",
            "I30642925": "University of Florence",
            "I107660666": "University of Rome Tor Vergata",
            "I119021686": "CNR (National Research Council)"
        }

        all_analyses = []

        # Process top institutions
        for inst_id in list(institution_names.keys())[:5]:  # Start with top 5
            inst_name = institution_names[inst_id]

            try:
                analysis = self.process_institution_bulk(inst_id, inst_name)
                all_analyses.append(analysis)

                # Save individual analysis
                output_file = self.output_dir / f"{inst_id}_analysis.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(analysis, f, indent=2, ensure_ascii=False)

                logger.info(f"Completed {inst_name}: {analysis['overall_collaboration_rate']:.2f}% China collaboration")

            except Exception as e:
                logger.error(f"Failed to process {inst_name}: {e}")
                continue

            # Rate limiting between institutions
            time.sleep(2)

        # Generate report
        report = self.generate_comprehensive_report(all_analyses)
        report_file = self.output_dir / "OPENALEX_COMPREHENSIVE_ANALYSIS.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)

        logger.info(f"Analysis complete. Report saved to {report_file}")
        return all_analyses

if __name__ == "__main__":
    processor = OpenAlexBulkProcessor()
    processor.run_bulk_analysis()

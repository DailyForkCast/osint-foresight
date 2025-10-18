"""
USAspending.gov Comprehensive Multi-Country Analysis Script
Analyzes US federal contracts and grants for ALL priority countries and China connections
Based on OSINT Foresight Framework Priority Countries (EU 27+3 + China + US domestic)
"""

import json
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set
from collections import defaultdict, Counter
import time
import logging
import re
from dataclasses import dataclass, asdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CountryEntity:
    """Represents an entity with country affiliations"""
    name: str
    country_codes: List[str]
    entity_type: str  # company, university, government, ngo
    risk_level: str  # low, medium, high, critical
    technology_areas: List[str]
    aliases: List[str]

@dataclass
class ContractMatch:
    """Represents a matched contract"""
    award_id: str
    recipient_name: str
    amount: float
    agency: str
    description: str
    action_date: str
    country_connections: List[str]
    technology_categories: List[str]
    risk_assessment: str
    place_of_performance: str

class USAspendingComprehensiveAnalyzer:
    """Comprehensive analyzer for USAspending data across all priority countries"""

    def __init__(self):
        self.base_url = "https://api.usaspending.gov/api/v2"
        self.output_path = Path("C:/Projects/OSINT - Foresight/data/processed/usaspending_comprehensive")
        self.output_path.mkdir(parents=True, exist_ok=True)

        # EU Priority Countries (from README.md framework)
        self.priority_countries = {
            # Tier 1 - Gateway Countries
            'HU': {'name': 'Hungary', 'tier': 1, 'notes': '17+1 format leader, unrestricted Chinese access'},
            'GR': {'name': 'Greece', 'tier': 1, 'notes': 'COSCO port control, BRI gateway to EU'},

            # Tier 2 - BRI & High Penetration
            'IT': {'name': 'Italy', 'tier': 2, 'notes': 'G7 country in BRI, Leonardo defense concerns'},
            'PL': {'name': 'Poland', 'tier': 2, 'notes': 'Central Europe pivot, 5G battleground'},
            'PT': {'name': 'Portugal', 'tier': 2, 'notes': 'Strategic Atlantic position'},
            'CZ': {'name': 'Czech Republic', 'tier': 2, 'notes': 'Former pro-China, recent restrictions'},

            # Tier 3 - Major Economies
            'DE': {'name': 'Germany', 'tier': 3, 'notes': 'Target despite restrictions'},
            'FR': {'name': 'France', 'tier': 3, 'notes': 'EU leader, technology transfer concerns'},
            'ES': {'name': 'Spain', 'tier': 3, 'notes': 'Growing Chinese presence'},

            # BRI EU Members (18 total)
            'BG': {'name': 'Bulgaria', 'tier': 4, 'notes': 'BRI member'},
            'HR': {'name': 'Croatia', 'tier': 4, 'notes': 'BRI member'},
            'EE': {'name': 'Estonia', 'tier': 4, 'notes': 'BRI member'},
            'LV': {'name': 'Latvia', 'tier': 4, 'notes': 'BRI member'},
            'LT': {'name': 'Lithuania', 'tier': 4, 'notes': 'BRI member'},
            'LU': {'name': 'Luxembourg', 'tier': 4, 'notes': 'BRI member'},
            'MT': {'name': 'Malta', 'tier': 4, 'notes': 'BRI member'},
            'RO': {'name': 'Romania', 'tier': 4, 'notes': 'BRI member'},
            'SK': {'name': 'Slovakia', 'tier': 4, 'notes': 'BRI member'},
            'SI': {'name': 'Slovenia', 'tier': 4, 'notes': 'BRI member'},
            'CY': {'name': 'Cyprus', 'tier': 4, 'notes': 'BRI member'},

            # Other EU Countries
            'AT': {'name': 'Austria', 'tier': 5, 'notes': 'EU member'},
            'BE': {'name': 'Belgium', 'tier': 5, 'notes': 'EU member'},
            'DK': {'name': 'Denmark', 'tier': 5, 'notes': 'EU member'},
            'FI': {'name': 'Finland', 'tier': 5, 'notes': 'EU member'},
            'IE': {'name': 'Ireland', 'tier': 5, 'notes': 'EU member'},
            'NL': {'name': 'Netherlands', 'tier': 5, 'notes': 'EU member'},
            'SE': {'name': 'Sweden', 'tier': 5, 'notes': 'EU member'},

            # EU+3 Countries
            'IS': {'name': 'Iceland', 'tier': 6, 'notes': 'EU+3 member'},
            'LI': {'name': 'Liechtenstein', 'tier': 6, 'notes': 'EU+3 member'},
            'NO': {'name': 'Norway', 'tier': 6, 'notes': 'EU+3 member'},

            # China & US
            'CN': {'name': 'China', 'tier': 0, 'notes': 'Primary target'},
            'US': {'name': 'United States', 'tier': 0, 'notes': 'Domestic analysis'}
        }

        # Chinese entity patterns (comprehensive)
        self.china_patterns = {
            'companies': [
                # Tech giants
                'huawei', 'zte', 'lenovo', 'xiaomi', 'alibaba', 'tencent',
                'baidu', 'dji', 'hikvision', 'dahua', 'bgi', 'bytedance',
                'smic', 'byd', 'geely', 'haier', 'tcl', 'oppo', 'vivo',
                'sensetime', 'megvii', 'cambricon', 'horizon robotics',
                # State-owned enterprises
                'china telecom', 'china mobile', 'china unicom',
                'sinopec', 'petrochina', 'cnooc', 'sinochem',
                'cosco', 'china shipping', 'china merchants',
                'bank of china', 'icbc', 'ccb', 'agricultural bank',
                'china construction bank', 'ping an', 'china life',
                # Defense & aerospace
                'avic', 'casic', 'china aerospace', 'norinco',
                'china shipbuilding', 'china electronics',
                # Universities & research
                'tsinghua', 'peking university', 'beihang', 'harbin',
                'xian jiaotong', 'southeast university', 'cas',
                'chinese academy', 'academy of sciences'
            ],
            'geographic': [
                'beijing', 'shanghai', 'shenzhen', 'guangzhou', 'hong kong',
                'macau', 'chengdu', 'wuhan', 'nanjing', 'tianjin',
                'xian', 'hangzhou', 'suzhou', 'dalian', 'qingdao',
                'china', 'chinese', 'prc', 'peoples republic'
            ],
            'subsidiaries': [
                'sino-', 'china-', 'zh-', 'cn-', 'hk-', 'beijing-',
                'shanghai-', 'shenzhen-', 'guangzhou-'
            ]
        }

        # EU country entity patterns
        self.eu_patterns = self._build_eu_patterns()

        # Critical technology keywords (aligned with framework)
        self.tech_keywords = {
            'ai_ml': [
                'artificial intelligence', 'machine learning', 'neural network',
                'deep learning', 'computer vision', 'natural language',
                'pattern recognition', 'automated decision'
            ],
            'quantum': [
                'quantum computing', 'quantum', 'qubit', 'quantum cryptography',
                'quantum communication', 'quantum sensing'
            ],
            'semiconductors': [
                'semiconductor', 'chip', 'microprocessor', 'integrated circuit',
                'silicon', 'wafer', 'foundry', 'fab', 'eda software'
            ],
            '5g_6g': [
                '5g', '6g', 'wireless', 'telecommunications', 'base station',
                'antenna', 'spectrum', 'cellular', 'mobile network'
            ],
            'hypersonics': [
                'hypersonic', 'scramjet', 'high speed', 'mach 5',
                'boost glide', 'hypersonic weapon'
            ],
            'biotechnology': [
                'biotechnology', 'genomics', 'synthetic biology', 'crispr',
                'gene editing', 'bioinformatics', 'proteomics'
            ],
            'autonomous': [
                'autonomous', 'unmanned', 'drone', 'uav', 'robotics',
                'self-driving', 'automated vehicle'
            ],
            'cyber': [
                'cybersecurity', 'encryption', 'cryptography', 'cyber warfare',
                'information security', 'network security'
            ],
            'space': [
                'satellite', 'spacecraft', 'launch vehicle', 'space technology',
                'orbital', 'rocket', 'space station'
            ],
            'energy': [
                'battery', 'solar', 'renewable energy', 'nuclear',
                'energy storage', 'fuel cell', 'smart grid'
            ],
            'advanced_materials': [
                'carbon fiber', 'composite', 'nanomaterial', 'metamaterial',
                'smart material', 'superalloy'
            ],
            'manufacturing': [
                'additive manufacturing', '3d printing', 'industrial robot',
                'digital twin', 'smart factory', 'industry 4.0'
            ]
        }

        self.stats = defaultdict(lambda: defaultdict(int))
        self.matches = []

    def _build_eu_patterns(self) -> Dict[str, List[str]]:
        """Build entity patterns for EU countries"""
        patterns = {}

        # Major defense companies by country
        patterns['IT'] = [
            'leonardo', 'finmeccanica', 'fiat', 'eni', 'telecom italia',
            'politecnico', 'roma tre', 'milano', 'torino'
        ]
        patterns['DE'] = [
            'siemens', 'sap', 'bmw', 'mercedes', 'volkswagen', 'bosch',
            'airbus', 'rheinmetall', 'thyssenkrupp', 'max planck'
        ]
        patterns['FR'] = [
            'thales', 'dassault', 'safran', 'airbus', 'total', 'orange',
            'sorbonne', 'cnrs', 'inria', 'cea'
        ]
        patterns['ES'] = [
            'indra', 'telefonica', 'repsol', 'bbva', 'santander',
            'universidad', 'csic'
        ]
        patterns['NL'] = [
            'philips', 'shell', 'asml', 'tno', 'delft', 'eindhoven'
        ]

        # Add geographic indicators for all countries
        for code, info in self.priority_countries.items():
            if code not in patterns:
                patterns[code] = []
            patterns[code].extend([
                info['name'].lower(),
                code.lower(),
                f"{info['name'].lower()} university",
                f"{info['name'].lower()} institute"
            ])

        return patterns

    def search_contracts_advanced(self, filters: Dict, limit: int = 100) -> List[Dict]:
        """Advanced contract search with comprehensive filters"""

        endpoint = f"{self.base_url}/search/spending_by_award/"

        payload = {
            "filters": filters,
            "fields": [
                "Award ID", "Recipient Name", "Award Amount",
                "Awarding Agency", "Awarding Sub Agency",
                "Contract Award Type", "Description",
                "Place of Performance City", "Place of Performance State",
                "Place of Performance Country Code",
                "Action Date", "Period of Performance Start Date",
                "Period of Performance Current End Date",
                "NAICS Code", "NAICS Description",
                "Primary Place of Performance Country Code",
                "Recipient Location Country Code"
            ],
            "page": 1,
            "limit": limit,
            "sort": "Award Amount",
            "order": "desc"
        }

        all_results = []
        max_pages = 50  # Limit to prevent excessive API calls

        while len(all_results) < 5000 and payload['page'] <= max_pages:
            try:
                response = requests.post(endpoint, json=payload, timeout=30)
                response.raise_for_status()
                data = response.json()

                results = data.get('results', [])
                if not results:
                    break

                all_results.extend(results)
                logger.info(f"Retrieved page {payload['page']}: {len(results)} contracts (total: {len(all_results)})")

                if not data.get('hasNext', False):
                    break

                payload['page'] += 1
                time.sleep(0.5)  # Rate limiting

            except Exception as e:
                logger.error(f"Error searching contracts page {payload['page']}: {e}")
                break

        return all_results

    def analyze_entity_connections(self, entity_name: str, description: str = "") -> Dict:
        """Analyze entity for country connections and risk assessment"""

        connections = {
            'countries': [],
            'risk_level': 'low',
            'evidence': [],
            'technology_areas': []
        }

        if not entity_name:
            return connections

        entity_lower = entity_name.lower()
        desc_lower = description.lower() if description else ""
        combined_text = f"{entity_lower} {desc_lower}"

        # Check China connections
        china_score = 0
        for pattern_type, patterns in self.china_patterns.items():
            for pattern in patterns:
                if pattern in combined_text:
                    connections['countries'].append('CN')
                    connections['evidence'].append(f"China pattern: {pattern} ({pattern_type})")
                    china_score += 1

        # Check EU country connections
        for country_code, patterns in self.eu_patterns.items():
            for pattern in patterns:
                if pattern in combined_text:
                    connections['countries'].append(country_code)
                    connections['evidence'].append(f"{country_code} pattern: {pattern}")

        # Assess risk level
        if china_score >= 3:
            connections['risk_level'] = 'critical'
        elif china_score >= 2:
            connections['risk_level'] = 'high'
        elif china_score >= 1:
            connections['risk_level'] = 'medium'

        # Identify technology areas
        for tech_category, keywords in self.tech_keywords.items():
            if any(keyword in combined_text for keyword in keywords):
                connections['technology_areas'].append(tech_category)

        # Remove duplicates
        connections['countries'] = list(set(connections['countries']))
        connections['technology_areas'] = list(set(connections['technology_areas']))

        return connections

    def search_by_country_keywords(self, country_code: str, start_date: str, end_date: str) -> List[Dict]:
        """Search contracts using country-specific keywords"""

        if country_code not in self.eu_patterns:
            return []

        country_info = self.priority_countries.get(country_code, {})
        patterns = self.eu_patterns[country_code]

        logger.info(f"Searching for {country_info.get('name', country_code)} contracts ({len(patterns)} patterns)")

        all_results = []

        # Search in chunks to avoid overwhelming the API
        for i in range(0, len(patterns), 5):
            chunk_patterns = patterns[i:i+5]

            filters = {
                "keywords": chunk_patterns,
                "time_period": [{
                    "start_date": start_date,
                    "end_date": end_date
                }]
            }

            try:
                results = self.search_contracts_advanced(filters, limit=50)
                if results:
                    logger.info(f"  Found {len(results)} contracts for patterns: {chunk_patterns}")
                    all_results.extend(results)

                time.sleep(1)  # Rate limiting

            except Exception as e:
                logger.error(f"Error searching {country_code} patterns {chunk_patterns}: {e}")

        return all_results

    def search_critical_technologies(self, start_date: str, end_date: str) -> List[Dict]:
        """Search for contracts involving critical technologies"""

        logger.info("Searching for critical technology contracts")

        all_results = []

        for tech_category, keywords in self.tech_keywords.items():
            logger.info(f"  Searching {tech_category}: {len(keywords)} keywords")

            # Search in smaller chunks
            for i in range(0, len(keywords), 3):
                chunk_keywords = keywords[i:i+3]

                filters = {
                    "keywords": chunk_keywords,
                    "time_period": [{
                        "start_date": start_date,
                        "end_date": end_date
                    }]
                }

                try:
                    results = self.search_contracts_advanced(filters, limit=50)
                    if results:
                        logger.info(f"    Found {len(results)} contracts for {chunk_keywords}")
                        all_results.extend(results)

                    time.sleep(0.5)

                except Exception as e:
                    logger.error(f"Error searching tech keywords {chunk_keywords}: {e}")

        return all_results

    def analyze_comprehensive(self, start_year: int = 2020, end_year: int = 2024):
        """Run comprehensive analysis across all priority countries"""

        logger.info(f"Starting comprehensive USAspending analysis ({start_year}-{end_year})")
        logger.info(f"Priority countries: {len(self.priority_countries)}")
        logger.info(f"Technology categories: {len(self.tech_keywords)}")

        start_date = f"{start_year}-01-01"
        end_date = f"{end_year}-12-31"

        all_contracts = []

        # 1. Search by priority countries (top tiers first)
        for tier in range(0, 7):
            tier_countries = [code for code, info in self.priority_countries.items() if info['tier'] == tier]

            if not tier_countries:
                continue

            logger.info(f"\nProcessing Tier {tier} countries: {tier_countries}")

            for country_code in tier_countries:
                country_results = self.search_by_country_keywords(country_code, start_date, end_date)
                if country_results:
                    all_contracts.extend(country_results)
                    logger.info(f"  {country_code}: {len(country_results)} contracts found")

        # 2. Search by critical technologies
        tech_results = self.search_critical_technologies(start_date, end_date)
        all_contracts.extend(tech_results)
        logger.info(f"\nTechnology search: {len(tech_results)} contracts found")

        # 3. Remove duplicates
        unique_contracts = {}
        for contract in all_contracts:
            award_id = contract.get('Award ID')
            if award_id and award_id not in unique_contracts:
                unique_contracts[award_id] = contract

        logger.info(f"\nTotal unique contracts: {len(unique_contracts)}")

        # 4. Analyze each contract for connections
        logger.info("Analyzing contracts for country connections and risk...")

        analyzed_matches = []
        for i, (award_id, contract) in enumerate(unique_contracts.items()):
            if i % 100 == 0:
                logger.info(f"  Analyzed {i}/{len(unique_contracts)} contracts")

            recipient = contract.get('Recipient Name', '')
            description = contract.get('Description', '')

            connections = self.analyze_entity_connections(recipient, description)

            if connections['countries'] or connections['technology_areas']:
                match = ContractMatch(
                    award_id=award_id,
                    recipient_name=recipient,
                    amount=float(contract.get('Award Amount', 0)),
                    agency=contract.get('Awarding Agency', ''),
                    description=description[:500] if description else '',
                    action_date=contract.get('Action Date', ''),
                    country_connections=connections['countries'],
                    technology_categories=connections['technology_areas'],
                    risk_assessment=connections['risk_level'],
                    place_of_performance=f"{contract.get('Place of Performance City', '')}, {contract.get('Place of Performance State', '')}"
                )
                analyzed_matches.append(match)

                # Update statistics
                for country in connections['countries']:
                    self.stats[country]['contracts'] += 1
                    self.stats[country]['total_value'] += match.amount

                for tech in connections['technology_areas']:
                    self.stats['technologies'][tech] += 1

        self.matches = analyzed_matches
        logger.info(f"Analysis complete: {len(analyzed_matches)} relevant contracts identified")

        # 5. Generate comprehensive report
        self.generate_comprehensive_report(start_year, end_year)

        return {
            'total_contracts_searched': len(unique_contracts),
            'relevant_matches': len(analyzed_matches),
            'country_stats': dict(self.stats),
            'matches': analyzed_matches[:100]  # Top 100 for quick review
        }

    def generate_comprehensive_report(self, start_year: int, end_year: int):
        """Generate comprehensive analysis report"""

        report = []
        report.append("# USAspending Comprehensive Multi-Country Analysis Report")
        report.append(f"\n**Generated:** {datetime.now().isoformat()}")
        report.append(f"**Analysis Period:** {start_year}-{end_year}")
        report.append(f"**Framework:** OSINT Foresight Multi-Country Intelligence")
        report.append(f"**Data Source:** USAspending.gov API v2")

        # Executive Summary
        total_matches = len(self.matches)
        total_value = sum(match.amount for match in self.matches)
        china_matches = [m for m in self.matches if 'CN' in m.country_connections]
        high_risk_matches = [m for m in self.matches if m.risk_assessment in ['high', 'critical']]

        report.append("\n## Executive Summary")
        report.append(f"- **Total Relevant Contracts:** {total_matches:,}")
        report.append(f"- **Total Contract Value:** ${total_value:,.2f}")
        report.append(f"- **China-Connected Contracts:** {len(china_matches):,}")
        report.append(f"- **High/Critical Risk Contracts:** {len(high_risk_matches):,}")
        report.append(f"- **Countries with Activity:** {len([c for c in self.stats.keys() if c != 'technologies'])}")

        # Priority Country Analysis
        report.append("\n## Priority Country Analysis")
        report.append("\n### Tier 1 Gateway Countries (HIGHEST CONCERN)")

        tier1_countries = ['HU', 'GR']
        for country in tier1_countries:
            if country in self.stats:
                stats = self.stats[country]
                country_name = self.priority_countries[country]['name']
                report.append(f"- **{country_name} ({country}):** {stats['contracts']} contracts, ${stats['total_value']:,.2f}")

        report.append("\n### Tier 2 BRI & High Penetration Countries")
        tier2_countries = ['IT', 'PL', 'PT', 'CZ']
        for country in tier2_countries:
            if country in self.stats:
                stats = self.stats[country]
                country_name = self.priority_countries[country]['name']
                report.append(f"- **{country_name} ({country}):** {stats['contracts']} contracts, ${stats['total_value']:,.2f}")

        # China Analysis
        if 'CN' in self.stats:
            china_stats = self.stats['CN']
            report.append(f"\n### China Analysis")
            report.append(f"- **Total China Connections:** {china_stats['contracts']} contracts")
            report.append(f"- **Total Value:** ${china_stats['total_value']:,.2f}")

            # China contract breakdown by risk
            china_by_risk = defaultdict(int)
            for match in china_matches:
                china_by_risk[match.risk_assessment] += 1

            report.append(f"- **Critical Risk:** {china_by_risk['critical']} contracts")
            report.append(f"- **High Risk:** {china_by_risk['high']} contracts")
            report.append(f"- **Medium Risk:** {china_by_risk['medium']} contracts")

        # Technology Analysis
        if 'technologies' in self.stats:
            tech_stats = self.stats['technologies']
            report.append("\n## Critical Technology Analysis")

            for tech, count in sorted(tech_stats.items(), key=lambda x: x[1], reverse=True):
                tech_name = tech.replace('_', ' ').title()
                report.append(f"- **{tech_name}:** {count} contracts")

        # Risk Assessment
        risk_counts = defaultdict(int)
        for match in self.matches:
            risk_counts[match.risk_assessment] += 1

        report.append("\n## Risk Assessment Summary")
        report.append(f"- **Critical Risk:** {risk_counts['critical']} contracts")
        report.append(f"- **High Risk:** {risk_counts['high']} contracts")
        report.append(f"- **Medium Risk:** {risk_counts['medium']} contracts")
        report.append(f"- **Low Risk:** {risk_counts['low']} contracts")

        # Top High-Risk Contracts
        critical_contracts = [m for m in self.matches if m.risk_assessment == 'critical']
        if critical_contracts:
            report.append("\n## Top Critical Risk Contracts")

            for i, contract in enumerate(sorted(critical_contracts, key=lambda x: x.amount, reverse=True)[:10]):
                report.append(f"\n### {i+1}. {contract.recipient_name}")
                report.append(f"- **Award ID:** {contract.award_id}")
                report.append(f"- **Amount:** ${contract.amount:,.2f}")
                report.append(f"- **Agency:** {contract.agency}")
                report.append(f"- **Countries:** {', '.join(contract.country_connections)}")
                report.append(f"- **Technologies:** {', '.join(contract.technology_categories)}")
                report.append(f"- **Description:** {contract.description[:200]}...")

        # Next Steps
        report.append("\n## Recommended Next Steps")
        report.append("1. **Immediate Review:** Critical risk contracts require detailed investigation")
        report.append("2. **Cross-Reference:** Compare with CORDIS/OpenAlex findings for pattern validation")
        report.append("3. **Historical Analysis:** Extend timeframe to 2015-2025 for complete picture")
        report.append("4. **Entity Mapping:** Build comprehensive entity relationship maps")
        report.append("5. **Technology Transfer Analysis:** Focus on dual-use technology flows")

        # Save report
        report_file = self.output_path / f"USASPENDING_COMPREHENSIVE_ANALYSIS_{start_year}_{end_year}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report))

        # Save detailed data
        data_file = self.output_path / f"usaspending_comprehensive_data_{start_year}_{end_year}.json"
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump({
                'metadata': {
                    'generated': datetime.now().isoformat(),
                    'period': f"{start_year}-{end_year}",
                    'total_matches': len(self.matches),
                    'total_value': total_value
                },
                'statistics': dict(self.stats),
                'priority_countries': self.priority_countries,
                'matches': [asdict(match) for match in self.matches]
            }, f, indent=2, default=str)

        logger.info(f"\n{'='*80}")
        logger.info("COMPREHENSIVE ANALYSIS COMPLETE")
        logger.info(f"Report: {report_file}")
        logger.info(f"Data: {data_file}")
        logger.info(f"Total matches: {total_matches:,}")
        logger.info(f"China connections: {len(china_matches):,}")
        logger.info(f"Critical risk: {len(high_risk_matches):,}")
        logger.info(f"{'='*80}")

if __name__ == "__main__":
    analyzer = USAspendingComprehensiveAnalyzer()

    # Run comprehensive analysis for recent years
    results = analyzer.analyze_comprehensive(start_year=2020, end_year=2024)

    print(f"\n{'='*80}")
    print("USASPENDING COMPREHENSIVE ANALYSIS SUMMARY")
    print(f"{'='*80}")
    print(f"Total contracts analyzed: {results['total_contracts_searched']:,}")
    print(f"Relevant matches found: {results['relevant_matches']:,}")
    print(f"Countries with activity: {len([c for c in results['country_stats'].keys() if c != 'technologies'])}")

    if 'CN' in results['country_stats']:
        china_contracts = results['country_stats']['CN']['contracts']
        china_value = results['country_stats']['CN']['total_value']
        print(f"China-connected contracts: {china_contracts:,} (${china_value:,.2f})")

    print("\nTop countries by contract count:")
    country_counts = [(c, stats['contracts']) for c, stats in results['country_stats'].items()
                     if c != 'technologies' and 'contracts' in stats]

    for country, count in sorted(country_counts, key=lambda x: x[1], reverse=True)[:10]:
        country_name = analyzer.priority_countries.get(country, {}).get('name', country)
        print(f"  {country_name} ({country}): {count} contracts")

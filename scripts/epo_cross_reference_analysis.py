#!/usr/bin/env python3
"""
EPO Cross-Reference Analysis
Cross-reference patent findings with CORDIS and OpenAlex data
"""

import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, List

class EPOCrossReferenceAnalysis:
    """Cross-reference EPO patents with other data sources"""

    def __init__(self):
        self.start_time = datetime.now()

        # Data directories
        self.epo_dir = Path("F:/OSINT_DATA/epo_targeted_patents")
        self.cordis_dir = Path("data/processed/cordis_comprehensive")
        self.openalex_dir = Path("data/processed/openalex_real_data")
        self.output_dir = Path("F:/OSINT_DATA/epo_intelligence_fusion")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def load_epo_patents(self) -> List[Dict]:
        """Load all EPO patent documents"""
        patents = []

        # Load individual patent files
        for patent_file in self.epo_dir.glob("*.json"):
            if 'summary' not in patent_file.name:
                with open(patent_file, 'r', encoding='utf-8') as f:
                    patents.append(json.load(f))

        return patents

    def extract_entities(self, patents: List[Dict]) -> Dict:
        """Extract key entities from patents"""
        entities = {
            'companies': defaultdict(list),
            'technologies': defaultdict(list),
            'countries': defaultdict(int),
            'collaborations': []
        }

        for patent in patents:
            patent_id = patent.get('patent_id', '')
            extracted = patent.get('extracted_info', {})

            # Extract companies
            for applicant in extracted.get('applicants', []):
                company_name = applicant.get('name', '')
                country = applicant.get('country', '')

                if company_name:
                    entities['companies'][company_name].append({
                        'patent_id': patent_id,
                        'country': country,
                        'title': extracted.get('title', ''),
                        'category': extracted.get('category', '')
                    })

                if country:
                    entities['countries'][country] += 1

            # Identify cross-border collaborations
            applicant_countries = [a.get('country', '') for a in extracted.get('applicants', [])]
            if 'CN' in applicant_countries and any(c in ['DE', 'FR', 'IT'] for c in applicant_countries):
                entities['collaborations'].append({
                    'patent_id': patent_id,
                    'title': extracted.get('title', ''),
                    'countries': list(set(applicant_countries)),
                    'applicants': extracted.get('applicants', [])
                })

            # Extract technology classifications
            for classification in extracted.get('classifications', []):
                entities['technologies'][classification[:4]].append({
                    'patent_id': patent_id,
                    'full_classification': classification
                })

        return entities

    def identify_critical_patterns(self, entities: Dict) -> Dict:
        """Identify critical technology transfer patterns"""
        patterns = {
            'timestamp': datetime.now().isoformat(),
            'chinese_entities_in_eu': [],
            'eu_china_joint_ventures': [],
            'technology_clusters': {},
            'risk_indicators': []
        }

        # Identify Chinese entities with EU patents
        for company, patents in entities['companies'].items():
            # Check for Chinese companies based on patent data
            if any('CN' in p.get('country', '') for p in patents):
                patterns['chinese_entities_in_eu'].append({
                    'company': company,
                    'patent_count': len(patents),
                    'categories': list(set(p['category'] for p in patents))
                })

        # Identify EU-China joint ventures
        for collab in entities['collaborations']:
            patterns['eu_china_joint_ventures'].append({
                'patent_id': collab['patent_id'],
                'title': collab['title'],
                'countries': collab['countries'],
                'applicant_count': len(collab['applicants'])
            })

        # Technology clusters
        tech_groups = {
            'H04': '5G/Telecommunications',
            'G06': 'Computing/AI',
            'H01': 'Electronic Components',
            'B29': 'Advanced Materials',
            'C07': 'Organic Chemistry/Pharma',
            'G01': 'Measurement/Testing'
        }

        for tech_code, patents in entities['technologies'].items():
            if tech_code in tech_groups:
                patterns['technology_clusters'][tech_groups[tech_code]] = len(patents)

        # Risk indicators
        if len(patterns['chinese_entities_in_eu']) > 0:
            patterns['risk_indicators'].append({
                'indicator': 'Chinese entities filing EU patents',
                'severity': 'HIGH',
                'count': len(patterns['chinese_entities_in_eu'])
            })

        if len(patterns['eu_china_joint_ventures']) > 0:
            patterns['risk_indicators'].append({
                'indicator': 'EU-China joint patent applications',
                'severity': 'CRITICAL',
                'count': len(patterns['eu_china_joint_ventures'])
            })

        return patterns

    def generate_intelligence_report(self, entities: Dict, patterns: Dict) -> Dict:
        """Generate comprehensive intelligence report"""
        report = {
            'metadata': {
                'generation_time': datetime.now().isoformat(),
                'data_sources': ['EPO OPS API', 'Patent document analysis'],
                'scope': 'EU-China technology collaboration',
                'classification': 'SENSITIVE'
            },
            'executive_summary': {
                'total_patents_analyzed': len(self.load_epo_patents()),
                'chinese_entities_identified': len(patterns['chinese_entities_in_eu']),
                'joint_ventures_found': len(patterns['eu_china_joint_ventures']),
                'critical_technologies': list(patterns['technology_clusters'].keys())
            },
            'key_findings': [],
            'entity_analysis': entities,
            'pattern_analysis': patterns,
            'recommendations': []
        }

        # Key findings
        if patterns['chinese_entities_in_eu']:
            report['key_findings'].append({
                'finding': 'Chinese entities actively filing patents in EU',
                'evidence': f"{len(patterns['chinese_entities_in_eu'])} Chinese companies identified",
                'implication': 'Technology transfer and IP acquisition ongoing'
            })

        if patterns['eu_china_joint_ventures']:
            report['key_findings'].append({
                'finding': 'Direct EU-China collaboration in patent filings',
                'evidence': f"{len(patterns['eu_china_joint_ventures'])} joint patents found",
                'implication': 'Technology sharing agreements in place'
            })

        # Technology-specific findings
        for tech, count in patterns['technology_clusters'].items():
            if count > 0:
                report['key_findings'].append({
                    'finding': f'Activity in {tech}',
                    'evidence': f'{count} patents classified',
                    'implication': f'Focus area for technology acquisition'
                })

        # Recommendations
        if patterns['risk_indicators']:
            report['recommendations'].append({
                'priority': 'IMMEDIATE',
                'action': 'Review identified Chinese entities for export control compliance',
                'rationale': 'Multiple risk indicators present'
            })

        report['recommendations'].append({
            'priority': 'HIGH',
            'action': 'Cross-reference patent applicants with sanctions databases',
            'rationale': 'Ensure no prohibited technology transfer'
        })

        report['recommendations'].append({
            'priority': 'MEDIUM',
            'action': 'Monitor patent citation networks for technology flow patterns',
            'rationale': 'Early warning of emerging collaborations'
        })

        return report

    def cross_reference_cordis(self, entities: Dict) -> Dict:
        """Cross-reference with CORDIS data if available"""
        cordis_matches = {
            'matched_organizations': [],
            'potential_links': []
        }

        # Check if CORDIS data exists
        cordis_file = self.cordis_dir / "cordis_comprehensive_results.json"
        if cordis_file.exists():
            with open(cordis_file, 'r', encoding='utf-8') as f:
                cordis_data = json.load(f)

            # Simple name matching (would be enhanced with fuzzy matching in production)
            for company in entities['companies'].keys():
                # Check if company appears in CORDIS
                company_lower = company.lower()

                # This would search through CORDIS participants
                # For now, we note the capability
                cordis_matches['potential_links'].append({
                    'patent_entity': company,
                    'search_status': 'CORDIS cross-reference available',
                    'action': 'Manual verification recommended'
                })

        return cordis_matches

    def run_analysis(self):
        """Run complete cross-reference analysis"""
        print("="*60)
        print("EPO CROSS-REFERENCE ANALYSIS")
        print(f"Start: {self.start_time.isoformat()}")
        print("="*60)

        # Load EPO patents
        print("\n1. Loading EPO patent data...")
        patents = self.load_epo_patents()
        print(f"   Loaded {len(patents)} patent documents")

        # Extract entities
        print("\n2. Extracting entities...")
        entities = self.extract_entities(patents)
        print(f"   Found {len(entities['companies'])} unique companies")
        print(f"   Found {len(entities['collaborations'])} cross-border collaborations")
        print(f"   Found {len(entities['technologies'])} technology classifications")

        # Identify patterns
        print("\n3. Identifying critical patterns...")
        patterns = self.identify_critical_patterns(entities)
        print(f"   Chinese entities in EU: {len(patterns['chinese_entities_in_eu'])}")
        print(f"   EU-China joint ventures: {len(patterns['eu_china_joint_ventures'])}")
        print(f"   Risk indicators: {len(patterns['risk_indicators'])}")

        # Cross-reference with CORDIS
        print("\n4. Cross-referencing with CORDIS...")
        cordis_matches = self.cross_reference_cordis(entities)
        print(f"   Potential CORDIS links: {len(cordis_matches['potential_links'])}")

        # Generate intelligence report
        print("\n5. Generating intelligence report...")
        report = self.generate_intelligence_report(entities, patterns)

        # Add CORDIS cross-reference
        report['cross_references'] = {
            'cordis': cordis_matches
        }

        # Save report
        output_file = self.output_dir / f"epo_intelligence_fusion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\n   Report saved: {output_file}")

        # Print summary
        print("\n" + "="*60)
        print("INTELLIGENCE SUMMARY")
        print("="*60)

        print("\nKEY FINDINGS:")
        for finding in report['key_findings'][:5]:
            print(f"\n- {finding['finding']}")
            print(f"  Evidence: {finding['evidence']}")
            print(f"  Implication: {finding['implication']}")

        print("\nCRITICAL ENTITIES:")
        for entity in patterns['chinese_entities_in_eu'][:3]:
            print(f"\n- {entity['company']}")
            print(f"  Patents: {entity['patent_count']}")
            print(f"  Categories: {', '.join(entity['categories'])}")

        print("\nRECOMMENDATIONS:")
        for rec in report['recommendations']:
            print(f"\n[{rec['priority']}] {rec['action']}")
            print(f"  Rationale: {rec['rationale']}")

        return report

def main():
    analyzer = EPOCrossReferenceAnalysis()
    analyzer.run_analysis()

if __name__ == "__main__":
    main()

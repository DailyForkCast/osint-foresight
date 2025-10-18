#!/usr/bin/env python3
"""
Comprehensive Dual-Use Technology Taxonomy Builder
Creates structured taxonomy of advanced and dual-use technologies from all collected intelligence
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set
import networkx as nx

class DualUseTaxonomyBuilder:
    def __init__(self):
        self.db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")
        self.output_path = Path("C:/Projects/OSINT - Foresight/analysis")

        # Source databases
        self.source_dbs = {
            'mcf': Path("F:/OSINT_WAREHOUSE/osint_master.db"),
            'arctic': Path("F:/OSINT_WAREHOUSE/osint_master.db"),
            'leonardo': Path("F:/OSINT_WAREHOUSE/osint_master.db"),
            'master': Path("F:/OSINT_WAREHOUSE/osint_master.db")
        }

        # Comprehensive dual-use technology taxonomy framework
        self.taxonomy_framework = {
            'Artificial Intelligence & Machine Learning': {
                'subcategories': [
                    'Computer Vision', 'Natural Language Processing', 'Machine Learning Algorithms',
                    'Neural Networks', 'Deep Learning', 'AI Chips', 'Edge AI', 'Autonomous Systems'
                ],
                'dual_use_examples': [
                    'facial recognition', 'voice recognition', 'predictive analytics',
                    'autonomous vehicles', 'drone navigation', 'surveillance systems'
                ]
            },
            'Quantum Technologies': {
                'subcategories': [
                    'Quantum Computing', 'Quantum Communications', 'Quantum Sensing',
                    'Quantum Cryptography', 'Quantum Materials', 'Quantum Radar'
                ],
                'dual_use_examples': [
                    'quantum encryption', 'quantum sensing for navigation',
                    'quantum computing for optimization', 'quantum radar for stealth detection'
                ]
            },
            'Advanced Manufacturing': {
                'subcategories': [
                    'Additive Manufacturing', 'Advanced Materials', 'Precision Manufacturing',
                    'Robotics', 'Automation', 'Digital Manufacturing'
                ],
                'dual_use_examples': [
                    '3d printing of weapons components', 'advanced composites',
                    'precision machining', 'industrial robotics'
                ]
            },
            'Biotechnology': {
                'subcategories': [
                    'Genetic Engineering', 'Synthetic Biology', 'Biomanufacturing',
                    'Gene Editing', 'Biomaterials', 'Bioinformatics'
                ],
                'dual_use_examples': [
                    'gene therapy', 'biological weapons research',
                    'enhanced human performance', 'biological detection'
                ]
            },
            'Space & Satellite Technology': {
                'subcategories': [
                    'Satellite Systems', 'Launch Vehicles', 'Space Sensors',
                    'Navigation Systems', 'Earth Observation', 'Space Communications'
                ],
                'dual_use_examples': [
                    'gps systems', 'satellite imagery', 'space-based radar',
                    'anti-satellite weapons', 'space debris tracking'
                ]
            },
            'Semiconductors & Microelectronics': {
                'subcategories': [
                    'Advanced Processors', 'Memory Technologies', 'Sensor Chips',
                    'Power Electronics', 'RF/Microwave', 'Photonics'
                ],
                'dual_use_examples': [
                    'high-performance computing', 'signal processing',
                    'electronic warfare', 'radar systems'
                ]
            },
            'Energy & Power Systems': {
                'subcategories': [
                    'Advanced Batteries', 'Power Generation', 'Energy Storage',
                    'Nuclear Technology', 'Renewable Energy', 'Power Electronics'
                ],
                'dual_use_examples': [
                    'portable power systems', 'nuclear reactors',
                    'directed energy weapons', 'electromagnetic pulse'
                ]
            },
            'Arctic & Polar Technologies': {
                'subcategories': [
                    'Ice Navigation', 'Cold Weather Equipment', 'Arctic Communications',
                    'Polar Construction', 'Ice Monitoring', 'Arctic Transportation'
                ],
                'dual_use_examples': [
                    'icebreaker technology', 'arctic surveillance',
                    'polar research stations', 'northern sea route navigation'
                ]
            },
            'Hypersonics & Advanced Propulsion': {
                'subcategories': [
                    'Hypersonic Vehicles', 'Scramjet Engines', 'Advanced Materials',
                    'Thermal Management', 'Guidance Systems', 'Propulsion Technology'
                ],
                'dual_use_examples': [
                    'hypersonic missiles', 'space launch systems',
                    'atmospheric research', 'high-speed transportation'
                ]
            },
            'Cyber & Information Technologies': {
                'subcategories': [
                    'Cybersecurity', 'Information Warfare', 'Network Technologies',
                    'Data Analytics', 'Cloud Computing', 'Blockchain'
                ],
                'dual_use_examples': [
                    'cyber defense systems', 'information operations',
                    'critical infrastructure protection', 'secure communications'
                ]
            }
        }

        self.setup_database()

    def setup_database(self):
        """Create dual-use technology taxonomy database"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute('''
            CREATE TABLE IF NOT EXISTS technology_categories (
                category_id TEXT PRIMARY KEY,
                category_name TEXT,
                parent_category TEXT,
                description TEXT,
                dual_use_potential TEXT,
                strategic_importance INTEGER,
                chinese_capabilities TEXT,
                us_dependencies TEXT
            )
        ''')

        cur.execute('''
            CREATE TABLE IF NOT EXISTS technology_entities (
                entity_id TEXT PRIMARY KEY,
                technology_name TEXT,
                category_id TEXT,
                entity_name TEXT,
                country TEXT,
                capability_level TEXT,
                threat_assessment TEXT,
                source_intelligence TEXT
            )
        ''')

        cur.execute('''
            CREATE TABLE IF NOT EXISTS dual_use_assessments (
                assessment_id TEXT PRIMARY KEY,
                technology_name TEXT,
                civilian_applications TEXT,
                military_applications TEXT,
                proliferation_risk TEXT,
                export_control_status TEXT,
                leonardo_score INTEGER,
                confidence_level TEXT
            )
        ''')

        cur.execute('''
            CREATE TABLE IF NOT EXISTS technology_relationships (
                relationship_id TEXT PRIMARY KEY,
                tech1 TEXT,
                tech2 TEXT,
                relationship_type TEXT,
                dependency_level TEXT,
                strategic_implications TEXT
            )
        ''')

        conn.commit()
        conn.close()

    def collect_technology_intelligence(self):
        """Collect technology data from all source databases"""
        print("Collecting technology intelligence from all sources...")

        all_technologies = {}

        # Collect from MCF database
        mcf_tech = self.collect_mcf_technologies()
        for tech in mcf_tech:
            tech_key = tech['name'].lower()
            if tech_key not in all_technologies:
                all_technologies[tech_key] = {
                    'name': tech['name'],
                    'sources': [],
                    'entities': [],
                    'applications': set(),
                    'categories': set()
                }
            all_technologies[tech_key]['sources'].append('MCF Analysis')
            all_technologies[tech_key]['entities'].extend(tech.get('entities', []))

        # Collect from Arctic database
        arctic_tech = self.collect_arctic_technologies()
        for tech in arctic_tech:
            tech_key = tech['name'].lower()
            if tech_key not in all_technologies:
                all_technologies[tech_key] = {
                    'name': tech['name'],
                    'sources': [],
                    'entities': [],
                    'applications': set(),
                    'categories': set()
                }
            all_technologies[tech_key]['sources'].append('Arctic Intelligence')
            all_technologies[tech_key]['categories'].add('Arctic & Polar Technologies')

        # Collect from Leonardo assessments
        leonardo_tech = self.collect_leonardo_technologies()
        for tech in leonardo_tech:
            tech_key = tech['name'].lower()
            if tech_key not in all_technologies:
                all_technologies[tech_key] = {
                    'name': tech['name'],
                    'sources': [],
                    'entities': [],
                    'applications': set(),
                    'categories': set()
                }
            all_technologies[tech_key]['sources'].append('Leonardo Assessment')
            all_technologies[tech_key]['entities'].append(tech.get('entity', ''))

        print(f"Collected {len(all_technologies)} unique technologies")
        return all_technologies

    def collect_mcf_technologies(self) -> List[Dict]:
        """Collect technologies from MCF database"""
        try:
            conn = sqlite3.connect(self.source_dbs['mcf'])
            cur = conn.cursor()

            cur.execute('SELECT technology_name FROM dual_use_technologies')
            technologies = []
            for row in cur.fetchall():
                technologies.append({'name': row[0]})

            conn.close()
            return technologies
        except:
            return []

    def collect_arctic_technologies(self) -> List[Dict]:
        """Collect technologies from Arctic database"""
        try:
            conn = sqlite3.connect(self.source_dbs['arctic'])
            cur = conn.cursor()

            cur.execute('SELECT technology_name FROM arctic_technologies')
            technologies = []
            for row in cur.fetchall():
                technologies.append({'name': row[0]})

            conn.close()
            return technologies
        except:
            return []

    def collect_leonardo_technologies(self) -> List[Dict]:
        """Collect technologies from Leonardo assessments"""
        try:
            conn = sqlite3.connect(self.source_dbs['leonardo'])
            cur = conn.cursor()

            cur.execute('SELECT entity_name, technology_name FROM technology_assessments')
            technologies = []
            for row in cur.fetchall():
                technologies.append({'entity': row[0], 'name': row[1]})

            conn.close()
            return technologies
        except:
            return []

    def classify_technologies(self, technologies: Dict) -> Dict:
        """Classify technologies into taxonomy framework"""
        print("Classifying technologies into taxonomy framework...")

        classified = {}

        for tech_key, tech_data in technologies.items():
            tech_name = tech_data['name']
            best_category = self.find_best_category(tech_name)

            if best_category not in classified:
                classified[best_category] = []

            # Enhanced technology record
            tech_record = {
                'name': tech_name,
                'category': best_category,
                'sources': tech_data['sources'],
                'entities': list(set(tech_data['entities'])),
                'dual_use_potential': self.assess_dual_use_potential(tech_name),
                'strategic_importance': self.assess_strategic_importance(tech_name, tech_data),
                'chinese_involvement': self.assess_chinese_involvement(tech_data['entities']),
                'applications': self.identify_applications(tech_name)
            }

            classified[best_category].append(tech_record)

        return classified

    def find_best_category(self, tech_name: str) -> str:
        """Find best taxonomy category for a technology"""
        tech_lower = tech_name.lower()

        # Direct matching
        for category, details in self.taxonomy_framework.items():
            # Check subcategories
            for subcat in details['subcategories']:
                if subcat.lower() in tech_lower or tech_lower in subcat.lower():
                    return category

            # Check dual-use examples
            for example in details['dual_use_examples']:
                if example.lower() in tech_lower or tech_lower in example.lower():
                    return category

        # Keyword-based classification
        if any(keyword in tech_lower for keyword in ['ai', 'artificial', 'machine learning', 'neural']):
            return 'Artificial Intelligence & Machine Learning'
        elif any(keyword in tech_lower for keyword in ['quantum', 'qubit']):
            return 'Quantum Technologies'
        elif any(keyword in tech_lower for keyword in ['arctic', 'polar', 'ice']):
            return 'Arctic & Polar Technologies'
        elif any(keyword in tech_lower for keyword in ['space', 'satellite', 'gps']):
            return 'Space & Satellite Technology'
        elif any(keyword in tech_lower for keyword in ['semiconductor', 'chip', 'microelectronics']):
            return 'Semiconductors & Microelectronics'
        elif any(keyword in tech_lower for keyword in ['hypersonic', 'scramjet']):
            return 'Hypersonics & Advanced Propulsion'
        elif any(keyword in tech_lower for keyword in ['cyber', 'network', 'blockchain']):
            return 'Cyber & Information Technologies'
        elif any(keyword in tech_lower for keyword in ['bio', 'gene', 'synthetic']):
            return 'Biotechnology'
        elif any(keyword in tech_lower for keyword in ['manufacturing', 'robotics', '3d print']):
            return 'Advanced Manufacturing'
        elif any(keyword in tech_lower for keyword in ['battery', 'energy', 'power', 'nuclear']):
            return 'Energy & Power Systems'
        else:
            return 'Emerging Technologies'

    def assess_dual_use_potential(self, tech_name: str) -> str:
        """Assess dual-use potential of a technology"""
        high_dual_use_keywords = [
            'artificial intelligence', 'quantum', 'hypersonic', 'biotechnology',
            'semiconductor', 'space', 'autonomous', 'surveillance'
        ]

        tech_lower = tech_name.lower()
        if any(keyword in tech_lower for keyword in high_dual_use_keywords):
            return 'HIGH'
        else:
            return 'MEDIUM'

    def assess_strategic_importance(self, tech_name: str, tech_data: Dict) -> int:
        """Assess strategic importance (1-100 scale)"""
        base_score = 50

        # Boost for multiple sources
        if len(tech_data['sources']) > 1:
            base_score += 20

        # Boost for known entities
        if tech_data['entities']:
            base_score += 15

        # Boost for high dual-use potential
        if self.assess_dual_use_potential(tech_name) == 'HIGH':
            base_score += 15

        return min(base_score, 100)

    def assess_chinese_involvement(self, entities: List[str]) -> str:
        """Assess level of Chinese involvement"""
        chinese_entities = [
            'huawei', 'zte', 'smic', 'dji', 'iflytek', 'tsinghua', 'beijing university',
            'china', 'chinese', 'pla', 'people\'s liberation army'
        ]

        entity_text = ' '.join(entities).lower()
        if any(entity in entity_text for entity in chinese_entities):
            return 'HIGH'
        else:
            return 'UNKNOWN'

    def identify_applications(self, tech_name: str) -> Dict:
        """Identify civilian and military applications"""
        applications = {
            'civilian': [],
            'military': []
        }

        tech_lower = tech_name.lower()

        # AI applications
        if 'artificial intelligence' in tech_lower or 'ai' in tech_lower:
            applications['civilian'] = ['automation', 'healthcare', 'transportation', 'finance']
            applications['military'] = ['autonomous weapons', 'surveillance', 'cyber warfare', 'intelligence analysis']

        # Space applications
        elif 'space' in tech_lower or 'satellite' in tech_lower:
            applications['civilian'] = ['communications', 'navigation', 'weather monitoring', 'earth observation']
            applications['military'] = ['reconnaissance', 'missile guidance', 'communications', 'anti-satellite weapons']

        # Quantum applications
        elif 'quantum' in tech_lower:
            applications['civilian'] = ['secure communications', 'drug discovery', 'financial modeling']
            applications['military'] = ['cryptography breaking', 'secure military communications', 'advanced sensing']

        return applications

    def store_taxonomy(self, classified_technologies: Dict):
        """Store taxonomy in database"""
        print("Storing taxonomy in database...")

        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        # Store categories
        for category, technologies in classified_technologies.items():
            category_id = category.replace(' ', '_').replace('&', 'and').lower()

            cur.execute('''
                INSERT OR REPLACE INTO technology_categories
                (category_id, category_name, description, strategic_importance)
                VALUES (?, ?, ?, ?)
            ''', (
                category_id,
                category,
                f"Advanced technologies in {category.lower()}",
                len(technologies) * 10  # Importance based on number of technologies
            ))

            # Store individual technologies
            for tech in technologies:
                assessment_id = f"assessment_{tech['name'].replace(' ', '_')}_{category_id}"

                cur.execute('''
                    INSERT OR REPLACE INTO dual_use_assessments
                    (assessment_id, technology_name, civilian_applications,
                     military_applications, proliferation_risk, confidence_level)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    assessment_id,
                    tech['name'],
                    json.dumps(tech['applications'].get('civilian', [])),
                    json.dumps(tech['applications'].get('military', [])),
                    tech['dual_use_potential'],
                    'HIGH' if len(tech['sources']) > 1 else 'MEDIUM'
                ))

        conn.commit()
        conn.close()

    def generate_taxonomy_report(self, classified_technologies: Dict):
        """Generate comprehensive taxonomy report"""
        total_technologies = sum(len(techs) for techs in classified_technologies.values())

        report = f"""# COMPREHENSIVE DUAL-USE TECHNOLOGY TAXONOMY
Generated: {datetime.now().isoformat()}
Source: Multi-Source Intelligence Fusion

## EXECUTIVE SUMMARY

### Technology Intelligence Overview
- **Total Technologies Classified**: {total_technologies}
- **Technology Categories**: {len(classified_technologies)}
- **Multi-Source Validated**: {sum(1 for techs in classified_technologies.values() for tech in techs if len(tech['sources']) > 1)}
- **High Dual-Use Potential**: {sum(1 for techs in classified_technologies.values() for tech in techs if tech['dual_use_potential'] == 'HIGH')}

## DUAL-USE TECHNOLOGY TAXONOMY

"""

        for category, technologies in classified_technologies.items():
            if not technologies:
                continue

            high_importance = [t for t in technologies if t['strategic_importance'] > 70]
            chinese_involved = [t for t in technologies if t['chinese_involvement'] == 'HIGH']

            report += f"""### {category}

**Technologies Identified**: {len(technologies)}
**High Strategic Importance**: {len(high_importance)}
**Chinese Involvement**: {len(chinese_involved)}

#### Key Technologies
"""
            # Show top 5 technologies by strategic importance
            sorted_techs = sorted(technologies, key=lambda x: x['strategic_importance'], reverse=True)
            for tech in sorted_techs[:5]:
                report += f"""
**{tech['name']}**
- Strategic Importance: {tech['strategic_importance']}/100
- Dual-Use Potential: {tech['dual_use_potential']}
- Chinese Involvement: {tech['chinese_involvement']}
- Sources: {', '.join(tech['sources'])}
"""

        report += """
## STRATEGIC ASSESSMENT BY CATEGORY

### Critical Dual-Use Technologies (High Priority)
"""

        # Identify critical technologies across all categories
        all_techs = []
        for techs in classified_technologies.values():
            all_techs.extend(techs)

        critical_techs = sorted(
            [t for t in all_techs if t['strategic_importance'] > 80],
            key=lambda x: x['strategic_importance'],
            reverse=True
        )

        for tech in critical_techs[:10]:
            report += f"""
**{tech['name']}** ({tech['category']})
- Strategic Score: {tech['strategic_importance']}/100
- Dual-Use: {tech['dual_use_potential']} potential
- Chinese Activity: {tech['chinese_involvement']}
"""

        report += """
## TECHNOLOGY INTERDEPENDENCIES

### Critical Technology Clusters
1. **AI-Semiconductor Nexus**: AI chips, advanced processors, machine learning
2. **Space-Communication Integration**: Satellite systems, navigation, communications
3. **Quantum-Crypto Convergence**: Quantum computing, cryptography, secure communications
4. **Arctic-Resource Technologies**: Ice navigation, resource extraction, polar communications

## THREAT ASSESSMENT

### High-Priority Monitoring Areas
1. **Technologies with High Chinese Involvement + High Strategic Importance**
2. **Emerging Technologies in Early Development Phases**
3. **Critical Supply Chain Dependencies**
4. **Dual-Use Technologies in Export Control Gaps**

## RECOMMENDED ACTIONS

### Immediate (24-48 Hours)
1. Review critical dual-use technologies for current export control status
2. Assess Chinese involvement in high-priority technology areas
3. Identify technology transfer and investment vulnerabilities

### Short-term (1-2 Weeks)
1. Deep-dive analysis of technology clusters and interdependencies
2. Enhanced monitoring of emerging technologies
3. Supply chain vulnerability assessment for critical technologies

### Strategic (1-3 Months)
1. Comprehensive technology competition strategy
2. Advanced dual-use technology tracking system
3. International coordination on critical technology protection

---
*Comprehensive Dual-Use Technology Taxonomy*
*Classification: For Official Use Only*
*Database: F:/OSINT_WAREHOUSE/dualuse_taxonomy.db*
*Next Update: Quarterly taxonomy revision*
"""

        # Save report
        report_path = self.output_path / "DUALUSE_TECHNOLOGY_TAXONOMY.md"
        report_path.write_text(report)
        print(f"Taxonomy report saved to {report_path}")

        return report

def main():
    builder = DualUseTaxonomyBuilder()

    print("Comprehensive Dual-Use Technology Taxonomy Builder")
    print("=" * 60)

    # Collect technology intelligence
    print("\nCollecting technology intelligence...")
    technologies = builder.collect_technology_intelligence()

    # Classify technologies
    print("\nClassifying technologies...")
    classified = builder.classify_technologies(technologies)

    # Store taxonomy
    print("\nStoring taxonomy...")
    builder.store_taxonomy(classified)

    # Generate report
    print("\nGenerating taxonomy report...")
    builder.generate_taxonomy_report(classified)

    print(f"\nTaxonomy Building Complete!")
    print(f"Categories: {len(classified)}")
    print(f"Technologies: {sum(len(techs) for techs in classified.values())}")
    print(f"Database: {builder.db_path}")
    print(f"Report: {builder.output_path / 'DUALUSE_TECHNOLOGY_TAXONOMY.md'}")

if __name__ == "__main__":
    main()

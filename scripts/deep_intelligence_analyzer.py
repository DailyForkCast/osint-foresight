#!/usr/bin/env python3
"""
Deep Intelligence Analysis System
Performs comprehensive analysis of all collected OSINT data
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import numpy as np
from collections import defaultdict

class DeepIntelligenceAnalyzer:
    def __init__(self):
        self.warehouse_path = Path("F:/OSINT_WAREHOUSE")
        self.output_path = Path("C:/Projects/OSINT - Foresight/analysis")

        # All intelligence databases
        self.databases = {
            'patents': self.warehouse_path / 'osint_master.db',
            'leonardo': self.warehouse_path / 'osint_master.db',
            'master': self.warehouse_path / 'osint_master.db',
            'predictive': self.warehouse_path / 'osint_master.db',
            'mcf': self.warehouse_path / 'osint_master.db',
            'arctic': self.warehouse_path / 'osint_master.db',
            'taxonomy': self.warehouse_path / 'osint_master.db',
            'network': self.warehouse_path / 'osint_master.db',
            'rss': self.warehouse_path / 'osint_master.db'
        }

    def perform_deep_analysis(self):
        """Perform comprehensive analysis across all data sources"""
        print("Performing deep intelligence analysis...")

        analysis_results = {
            'entity_profiles': self.build_entity_profiles(),
            'technology_convergence': self.analyze_technology_convergence(),
            'threat_patterns': self.identify_threat_patterns(),
            'capability_gaps': self.assess_capability_gaps(),
            'strategic_priorities': self.determine_strategic_priorities()
        }

        return analysis_results

    def build_entity_profiles(self) -> Dict:
        """Build comprehensive profiles for key entities"""
        profiles = {}

        # Get Leonardo assessments
        if self.databases['leonardo'].exists():
            conn = sqlite3.connect(self.databases['leonardo'])
            cur = conn.cursor()
            cur.execute('''
                SELECT entity_name, technology_name, leonardo_composite_score, risk_category
                FROM technology_assessments
            ''')
            for row in cur.fetchall():
                entity = row[0]
                if entity not in profiles:
                    profiles[entity] = {
                        'technologies': [],
                        'risk_scores': [],
                        'categories': set(),
                        'sources': set()
                    }
                profiles[entity]['technologies'].append(row[1])
                profiles[entity]['risk_scores'].append(row[2])
                profiles[entity]['categories'].add(row[3])
                profiles[entity]['sources'].add('Leonardo')
            conn.close()

        # Add MCF intelligence
        if self.databases['mcf'].exists():
            conn = sqlite3.connect(self.databases['mcf'])
            cur = conn.cursor()
            cur.execute('SELECT entity_name FROM mcf_entities')
            for row in cur.fetchall():
                entity = row[0]
                if entity not in profiles:
                    profiles[entity] = {
                        'technologies': [],
                        'risk_scores': [],
                        'categories': set(),
                        'sources': set()
                    }
                profiles[entity]['sources'].add('MCF')
            conn.close()

        # Calculate composite profiles
        for entity, data in profiles.items():
            if data['risk_scores']:
                data['avg_risk'] = np.mean(data['risk_scores'])
                data['max_risk'] = max(data['risk_scores'])
            else:
                data['avg_risk'] = 0
                data['max_risk'] = 0

        return profiles

    def analyze_technology_convergence(self) -> Dict:
        """Identify converging technology clusters"""
        convergence = {
            'ai_quantum': [],
            'space_cyber': [],
            'bio_nano': [],
            'arctic_energy': []
        }

        # Check technology combinations from taxonomy
        if self.databases['taxonomy'].exists():
            conn = sqlite3.connect(self.databases['taxonomy'])
            cur = conn.cursor()
            cur.execute('''
                SELECT technology_name, civilian_applications, military_applications
                FROM dual_use_assessments
            ''')

            for row in cur.fetchall():
                tech = row[0].lower()

                # AI-Quantum convergence
                if ('ai' in tech or 'artificial' in tech) and 'quantum' in tech:
                    convergence['ai_quantum'].append(tech)

                # Space-Cyber convergence
                if ('space' in tech or 'satellite' in tech) and ('cyber' in tech or 'network' in tech):
                    convergence['space_cyber'].append(tech)

                # Bio-Nano convergence
                if ('bio' in tech or 'gene' in tech) and 'nano' in tech:
                    convergence['bio_nano'].append(tech)

                # Arctic-Energy convergence
                if 'arctic' in tech and ('energy' in tech or 'resource' in tech):
                    convergence['arctic_energy'].append(tech)

            conn.close()

        return convergence

    def identify_threat_patterns(self) -> List[Dict]:
        """Identify emerging threat patterns"""
        patterns = []

        # Pattern 1: High-risk entities with multiple technologies
        entity_profiles = self.build_entity_profiles()
        for entity, profile in entity_profiles.items():
            if profile['max_risk'] > 85 and len(profile['technologies']) > 2:
                patterns.append({
                    'type': 'HIGH_RISK_MULTI_TECH',
                    'entity': entity,
                    'risk': profile['max_risk'],
                    'tech_count': len(profile['technologies']),
                    'severity': 'CRITICAL'
                })

        # Pattern 2: Arctic technology with Chinese involvement
        if self.databases['arctic'].exists():
            conn = sqlite3.connect(self.databases['arctic'])
            cur = conn.cursor()
            cur.execute('''
                SELECT filename, chinese_arctic_score, arctic_relevance_score
                FROM arctic_reports
                WHERE chinese_arctic_score > 0
            ''')
            for row in cur.fetchall():
                if row[1] > 50:  # Significant Chinese Arctic content
                    patterns.append({
                        'type': 'CHINESE_ARCTIC_EXPANSION',
                        'source': row[0],
                        'chinese_score': row[1],
                        'arctic_score': row[2],
                        'severity': 'HIGH'
                    })
            conn.close()

        # Pattern 3: Technology transfer indicators
        if self.databases['mcf'].exists():
            conn = sqlite3.connect(self.databases['mcf'])
            cur = conn.cursor()
            cur.execute('''
                SELECT COUNT(*) FROM dual_use_technologies
            ''')
            dual_use_count = cur.fetchone()[0]
            if dual_use_count > 30:
                patterns.append({
                    'type': 'EXTENSIVE_DUAL_USE_ACTIVITY',
                    'count': dual_use_count,
                    'severity': 'ELEVATED'
                })
            conn.close()

        return patterns

    def assess_capability_gaps(self) -> Dict:
        """Identify capability gaps and dependencies"""
        gaps = {
            'technology_gaps': [],
            'intelligence_gaps': [],
            'coverage_gaps': []
        }

        # Technology gaps from Leonardo scores
        if self.databases['leonardo'].exists():
            conn = sqlite3.connect(self.databases['leonardo'])
            cur = conn.cursor()
            cur.execute('''
                SELECT technology_name, supply_chain_score
                FROM technology_assessments
                WHERE supply_chain_score > 70
            ''')
            for row in cur.fetchall():
                gaps['technology_gaps'].append({
                    'technology': row[0],
                    'vulnerability': row[1],
                    'type': 'SUPPLY_CHAIN_DEPENDENCY'
                })
            conn.close()

        # Intelligence coverage gaps
        if self.databases['master'].exists():
            conn = sqlite3.connect(self.databases['master'])
            cur = conn.cursor()
            cur.execute('''
                SELECT entity_name FROM intelligence_fusion
                WHERE confidence_score < 0.5
            ''')
            for row in cur.fetchall():
                gaps['intelligence_gaps'].append({
                    'entity': row[0],
                    'type': 'LOW_CONFIDENCE_ASSESSMENT'
                })
            conn.close()

        return gaps

    def determine_strategic_priorities(self) -> List[Dict]:
        """Determine strategic priorities based on analysis"""
        priorities = []

        # Priority 1: Critical technologies at risk
        entity_profiles = self.build_entity_profiles()
        critical_entities = [e for e, p in entity_profiles.items()
                           if p['max_risk'] > 90]
        if critical_entities:
            priorities.append({
                'priority': 1,
                'category': 'CRITICAL_TECHNOLOGY_PROTECTION',
                'entities': critical_entities,
                'action': 'Immediate defensive measures required'
            })

        # Priority 2: Arctic strategic competition
        threat_patterns = self.identify_threat_patterns()
        arctic_threats = [p for p in threat_patterns
                         if p['type'] == 'CHINESE_ARCTIC_EXPANSION']
        if arctic_threats:
            priorities.append({
                'priority': 2,
                'category': 'ARCTIC_DOMAIN_AWARENESS',
                'threats': len(arctic_threats),
                'action': 'Enhanced Arctic monitoring and presence'
            })

        # Priority 3: Supply chain vulnerabilities
        gaps = self.assess_capability_gaps()
        if gaps['technology_gaps']:
            priorities.append({
                'priority': 3,
                'category': 'SUPPLY_CHAIN_RESILIENCE',
                'vulnerabilities': len(gaps['technology_gaps']),
                'action': 'Diversify critical technology suppliers'
            })

        return priorities

    def generate_deep_analysis_report(self):
        """Generate comprehensive deep analysis report"""
        analysis = self.perform_deep_analysis()

        report = f"""# DEEP INTELLIGENCE ANALYSIS REPORT
Generated: {datetime.now().isoformat()}
Analysis Type: Comprehensive Multi-Source Deep Dive

## EXECUTIVE SUMMARY

### Key Findings
- **Entity Profiles Built**: {len(analysis['entity_profiles'])}
- **Threat Patterns Identified**: {len(analysis['threat_patterns'])}
- **Strategic Priorities**: {len(analysis['strategic_priorities'])}
- **Capability Gaps**: {sum(len(v) for v in analysis['capability_gaps'].values())}

## ENTITY THREAT PROFILES

### Highest Risk Entities
"""
        # Sort entities by risk
        sorted_entities = sorted(analysis['entity_profiles'].items(),
                               key=lambda x: x[1]['max_risk'],
                               reverse=True)

        for entity, profile in sorted_entities[:5]:
            report += f"""
**{entity}**
- Maximum Risk Score: {profile['max_risk']}/100
- Average Risk Score: {profile['avg_risk']:.1f}/100
- Technologies: {', '.join(profile['technologies'][:3])}
- Intelligence Sources: {', '.join(profile['sources'])}
"""

        report += """
## TECHNOLOGY CONVERGENCE ANALYSIS

### Emerging Technology Clusters
"""
        for cluster, technologies in analysis['technology_convergence'].items():
            if technologies:
                report += f"""
**{cluster.replace('_', '-').upper()}**
- Technologies Identified: {len(technologies)}
- Examples: {', '.join(technologies[:3])}
"""

        report += """
## THREAT PATTERN ANALYSIS

### Critical Threat Patterns Detected
"""
        critical_patterns = [p for p in analysis['threat_patterns']
                           if p.get('severity') == 'CRITICAL']
        for pattern in critical_patterns:
            report += f"""
**{pattern['type']}**
- Entity: {pattern.get('entity', 'N/A')}
- Risk Level: {pattern.get('risk', 'N/A')}
- Severity: {pattern['severity']}
"""

        report += """
## CAPABILITY GAP ASSESSMENT

### Critical Dependencies and Vulnerabilities
"""
        for gap_type, gaps in analysis['capability_gaps'].items():
            if gaps:
                report += f"""
**{gap_type.replace('_', ' ').title()}**: {len(gaps)} identified
"""
                for gap in gaps[:3]:
                    report += f"- {gap.get('technology', gap.get('entity', 'Unknown'))}: {gap.get('type', 'N/A')}\n"

        report += """
## STRATEGIC PRIORITIES

### Recommended Priority Actions
"""
        for priority in analysis['strategic_priorities']:
            report += f"""
**Priority {priority['priority']}: {priority['category']}**
- Action Required: {priority['action']}
- Scope: {priority.get('entities', priority.get('threats', priority.get('vulnerabilities', 'N/A')))}
"""

        report += """
## INTELLIGENCE ASSESSMENT CONFIDENCE

### Analysis Confidence Levels
- **High Confidence**: Multi-source validated findings
- **Medium Confidence**: Dual-source or pattern-based findings
- **Low Confidence**: Single-source or emerging indicators

## RECOMMENDED ACTIONS

### Immediate (24 Hours)
1. Address Priority 1 critical technology protection needs
2. Enhance monitoring of identified threat patterns
3. Initiate supply chain risk mitigation

### Short-term (1 Week)
1. Deep-dive analysis of technology convergence clusters
2. Expand intelligence collection on capability gaps
3. Coordinate defensive measures for critical entities

### Strategic (1 Month)
1. Comprehensive technology competition strategy
2. Enhanced domain awareness capabilities
3. Resilience building for identified vulnerabilities

---
*Deep Intelligence Analysis Report*
*Personal OSINT Learning Project*
*Next Analysis: Weekly comprehensive review*
"""

        # Save report
        report_path = self.output_path / "DEEP_INTELLIGENCE_ANALYSIS.md"
        report_path.write_text(report)
        print(f"Deep analysis report saved to {report_path}")

        return report

def main():
    analyzer = DeepIntelligenceAnalyzer()
    analyzer.generate_deep_analysis_report()
    print("Deep intelligence analysis complete!")

if __name__ == "__main__":
    main()

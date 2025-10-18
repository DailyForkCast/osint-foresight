#!/usr/bin/env python3
"""
Leonardo Standard Technology Assessment Scoring System
Implements Leonardo DRS-style technology readiness and risk scoring
"""

import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Tuple
from pathlib import Path

class LeonardoStandardScorer:
    def __init__(self):
        self.db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")
        self.output_path = Path("C:/Projects/OSINT - Foresight/analysis")

        # Leonardo Standard scoring dimensions
        self.scoring_dimensions = {
            'technology_readiness': {
                'TRL_9': 100,  # Operational system proven
                'TRL_7-8': 80,  # System prototype demonstrated
                'TRL_5-6': 60,  # Technology demonstrated in environment
                'TRL_3-4': 40,  # Proof of concept
                'TRL_1-2': 20   # Basic principles
            },
            'dual_use_potential': {
                'explicit_military': 100,
                'aerospace_defense': 90,
                'surveillance_security': 85,
                'critical_infrastructure': 80,
                'telecommunications': 75,
                'ai_ml': 70,
                'semiconductors': 70,
                'quantum': 65,
                'robotics': 60,
                'general_purpose': 30
            },
            'supply_chain_criticality': {
                'single_source': 100,
                'limited_suppliers': 80,
                'concentrated_region': 70,
                'multiple_sources': 40,
                'widely_available': 20
            },
            'export_control_status': {
                'bis_entity_list': 100,
                'export_controlled': 90,
                'itar_controlled': 85,
                'dual_use_listed': 75,
                'monitoring_required': 50,
                'unrestricted': 10
            },
            'technology_transfer_risk': {
                'direct_transfer': 100,
                'joint_venture': 85,
                'licensing': 70,
                'academic_collaboration': 60,
                'open_publication': 40,
                'no_transfer': 10
            }
        }

        self.setup_database()

    def setup_database(self):
        """Create Leonardo scoring database"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute('''
            CREATE TABLE IF NOT EXISTS technology_assessments (
                entity_name TEXT,
                technology_name TEXT,
                assessment_date DATE,
                trl_score INTEGER,
                dual_use_score INTEGER,
                supply_chain_score INTEGER,
                export_control_score INTEGER,
                transfer_risk_score INTEGER,
                leonardo_composite_score INTEGER,
                risk_category TEXT,
                assessment_notes TEXT,
                PRIMARY KEY (entity_name, technology_name, assessment_date)
            )
        ''')

        cur.execute('''
            CREATE TABLE IF NOT EXISTS scoring_thresholds (
                score_min INTEGER,
                score_max INTEGER,
                category TEXT,
                action_required TEXT,
                leonardo_designation TEXT
            )
        ''')

        # Insert Leonardo Standard thresholds
        thresholds = [
            (90, 100, 'CRITICAL', 'Immediate intervention required', 'L1-CRITICAL'),
            (75, 89, 'HIGH', 'Enhanced monitoring required', 'L2-HIGH'),
            (60, 74, 'ELEVATED', 'Regular monitoring', 'L3-ELEVATED'),
            (40, 59, 'MODERATE', 'Periodic review', 'L4-MODERATE'),
            (0, 39, 'LOW', 'Standard procedures', 'L5-LOW')
        ]

        cur.executemany('''
            INSERT OR REPLACE INTO scoring_thresholds VALUES (?, ?, ?, ?, ?)
        ''', thresholds)

        conn.commit()
        conn.close()

    def calculate_leonardo_score(self, entity: str, technology: str,
                                attributes: Dict) -> Dict:
        """Calculate Leonardo Standard composite score"""

        # Calculate individual dimension scores
        scores = {
            'trl': self.calculate_trl_score(attributes.get('readiness_level', 'TRL_1-2')),
            'dual_use': self.calculate_dual_use_score(attributes.get('technology_type', 'general_purpose')),
            'supply_chain': self.calculate_supply_chain_score(attributes.get('supply_status', 'widely_available')),
            'export_control': self.calculate_export_control_score(attributes.get('export_status', 'unrestricted')),
            'transfer_risk': self.calculate_transfer_risk_score(attributes.get('transfer_type', 'no_transfer'))
        }

        # Leonardo weighted composite formula
        weights = {
            'dual_use': 0.30,
            'export_control': 0.25,
            'transfer_risk': 0.20,
            'supply_chain': 0.15,
            'trl': 0.10
        }

        composite_score = sum(scores[dim] * weight
                            for dim, weight in weights.items())

        # Determine risk category
        risk_category = self.get_risk_category(composite_score)

        result = {
            'entity': entity,
            'technology': technology,
            'individual_scores': scores,
            'leonardo_composite': int(composite_score),
            'risk_category': risk_category,
            'assessment_date': datetime.now().isoformat()
        }

        # Store in database
        self.store_assessment(result)

        return result

    def calculate_trl_score(self, trl_level: str) -> int:
        """Calculate Technology Readiness Level score"""
        return self.scoring_dimensions['technology_readiness'].get(trl_level, 20)

    def calculate_dual_use_score(self, tech_type: str) -> int:
        """Calculate dual-use potential score"""
        return self.scoring_dimensions['dual_use_potential'].get(tech_type, 30)

    def calculate_supply_chain_score(self, supply_status: str) -> int:
        """Calculate supply chain criticality score"""
        return self.scoring_dimensions['supply_chain_criticality'].get(supply_status, 20)

    def calculate_export_control_score(self, export_status: str) -> int:
        """Calculate export control status score"""
        return self.scoring_dimensions['export_control_status'].get(export_status, 10)

    def calculate_transfer_risk_score(self, transfer_type: str) -> int:
        """Calculate technology transfer risk score"""
        return self.scoring_dimensions['technology_transfer_risk'].get(transfer_type, 10)

    def get_risk_category(self, score: float) -> str:
        """Determine risk category from composite score"""
        if score >= 90:
            return 'L1-CRITICAL'
        elif score >= 75:
            return 'L2-HIGH'
        elif score >= 60:
            return 'L3-ELEVATED'
        elif score >= 40:
            return 'L4-MODERATE'
        else:
            return 'L5-LOW'

    def store_assessment(self, assessment: Dict):
        """Store assessment in database"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        scores = assessment['individual_scores']
        cur.execute('''
            INSERT OR REPLACE INTO technology_assessments
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            assessment['entity'],
            assessment['technology'],
            assessment['assessment_date'],
            scores['trl'],
            scores['dual_use'],
            scores['supply_chain'],
            scores['export_control'],
            scores['transfer_risk'],
            assessment['leonardo_composite'],
            assessment['risk_category'],
            json.dumps(assessment)
        ))

        conn.commit()
        conn.close()

    def assess_known_entities(self):
        """Assess known Chinese entities using Leonardo Standard"""

        # Known entities with their technology profiles
        entities = [
            {
                'entity': 'Huawei Technologies',
                'technology': '5G Infrastructure',
                'attributes': {
                    'readiness_level': 'TRL_9',
                    'technology_type': 'telecommunications',
                    'supply_status': 'limited_suppliers',
                    'export_status': 'bis_entity_list',
                    'transfer_type': 'direct_transfer'
                }
            },
            {
                'entity': 'SMIC',
                'technology': 'Semiconductor Manufacturing',
                'attributes': {
                    'readiness_level': 'TRL_7-8',
                    'technology_type': 'semiconductors',
                    'supply_status': 'single_source',
                    'export_status': 'bis_entity_list',
                    'transfer_type': 'joint_venture'
                }
            },
            {
                'entity': 'DJI',
                'technology': 'Drone Systems',
                'attributes': {
                    'readiness_level': 'TRL_9',
                    'technology_type': 'aerospace_defense',
                    'supply_status': 'concentrated_region',
                    'export_status': 'export_controlled',
                    'transfer_type': 'licensing'
                }
            },
            {
                'entity': 'iFlytek',
                'technology': 'AI Voice Recognition',
                'attributes': {
                    'readiness_level': 'TRL_7-8',
                    'technology_type': 'ai_ml',
                    'supply_status': 'multiple_sources',
                    'export_status': 'bis_entity_list',
                    'transfer_type': 'academic_collaboration'
                }
            },
            {
                'entity': 'Tsinghua University',
                'technology': 'Quantum Computing Research',
                'attributes': {
                    'readiness_level': 'TRL_3-4',
                    'technology_type': 'quantum',
                    'supply_status': 'limited_suppliers',
                    'export_status': 'monitoring_required',
                    'transfer_type': 'academic_collaboration'
                }
            },
            {
                'entity': 'Beijing University',
                'technology': 'Hypersonic Research',
                'attributes': {
                    'readiness_level': 'TRL_5-6',
                    'technology_type': 'aerospace_defense',
                    'supply_status': 'single_source',
                    'export_status': 'export_controlled',
                    'transfer_type': 'direct_transfer'
                }
            }
        ]

        results = []
        for entity_data in entities:
            result = self.calculate_leonardo_score(
                entity_data['entity'],
                entity_data['technology'],
                entity_data['attributes']
            )
            results.append(result)
            print(f"Assessed {entity_data['entity']}: Leonardo Score = {result['leonardo_composite']} ({result['risk_category']})")

        return results

    def generate_leonardo_report(self):
        """Generate Leonardo Standard assessment report"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        # Get all assessments
        cur.execute('''
            SELECT * FROM technology_assessments
            ORDER BY leonardo_composite_score DESC
        ''')
        assessments = cur.fetchall()

        # Get category counts
        cur.execute('''
            SELECT risk_category, COUNT(*) as count
            FROM technology_assessments
            GROUP BY risk_category
            ORDER BY leonardo_composite_score DESC
        ''')
        categories = cur.fetchall()

        conn.close()

        # Generate report
        report = f"""# LEONARDO STANDARD TECHNOLOGY ASSESSMENT REPORT
Generated: {datetime.now().isoformat()}
Assessment Framework: Leonardo DRS Technology Risk Matrix v2.0

## EXECUTIVE SUMMARY

### Risk Distribution
"""
        for category, count in categories:
            report += f"- **{category}**: {count} technologies\n"

        report += """
## CRITICAL TECHNOLOGIES (L1-CRITICAL)

Technologies requiring immediate intervention:

"""
        for assessment in assessments:
            if assessment[10] == 'L1-CRITICAL':
                report += f"""### {assessment[0]} - {assessment[1]}
- **Leonardo Composite Score**: {assessment[9]}/100
- **TRL Score**: {assessment[3]}
- **Dual-Use Score**: {assessment[4]}
- **Supply Chain Score**: {assessment[5]}
- **Export Control Score**: {assessment[6]}
- **Transfer Risk Score**: {assessment[7]}

"""

        report += """
## HIGH RISK TECHNOLOGIES (L2-HIGH)

Technologies requiring enhanced monitoring:

"""
        for assessment in assessments:
            if assessment[10] == 'L2-HIGH':
                report += f"""### {assessment[0]} - {assessment[1]}
- **Leonardo Composite Score**: {assessment[9]}/100
- **Key Risk Factors**: Export={assessment[6]}, Transfer={assessment[7]}

"""

        report += """
## LEONARDO SCORING METHODOLOGY

The Leonardo Standard uses five weighted dimensions:
1. **Dual-Use Potential** (30%): Military/civilian application overlap
2. **Export Control Status** (25%): Regulatory restrictions
3. **Technology Transfer Risk** (20%): Knowledge proliferation potential
4. **Supply Chain Criticality** (15%): Dependency and concentration
5. **Technology Readiness** (10%): Operational maturity

### Risk Categories
- **L1-CRITICAL** (90-100): Immediate intervention required
- **L2-HIGH** (75-89): Enhanced monitoring required
- **L3-ELEVATED** (60-74): Regular monitoring
- **L4-MODERATE** (40-59): Periodic review
- **L5-LOW** (0-39): Standard procedures

## RECOMMENDED ACTIONS

1. **Immediate**: Review all L1-CRITICAL technologies for active countermeasures
2. **Short-term**: Implement enhanced monitoring for L2-HIGH technologies
3. **Strategic**: Develop alternative suppliers for critical supply chain dependencies

---
*Leonardo Standard Technology Assessment System*
*Classification: For Official Use Only*
"""

        # Save report
        report_path = self.output_path / "LEONARDO_STANDARD_ASSESSMENT.md"
        report_path.write_text(report)
        print(f"Leonardo report saved to {report_path}")

        return report

def main():
    scorer = LeonardoStandardScorer()

    print("Leonardo Standard Technology Assessment System")
    print("=" * 50)

    # Assess known entities
    print("\nAssessing known entities...")
    results = scorer.assess_known_entities()

    # Generate report
    print("\nGenerating Leonardo Standard report...")
    scorer.generate_leonardo_report()

    print("\nAssessment complete!")
    print(f"Database: {scorer.db_path}")
    print(f"Report: {scorer.output_path / 'LEONARDO_STANDARD_ASSESSMENT.md'}")

if __name__ == "__main__":
    main()

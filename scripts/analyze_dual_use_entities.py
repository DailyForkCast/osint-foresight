#!/usr/bin/env python3
"""
analyze_dual_use_entities.py - Dual-Use Entity Checker

Automatically checks cancer research and environmental science entities against:
1. BIS Entity List (sanctions)
2. Seven Sons Defense Universities
3. Dual-use technology keywords in contract descriptions

Generates risk assessment report for TIER_1 reclassification.

Usage:
    python analyze_dual_use_entities.py --input importance_tier_sample_20251018_075329.csv

Output:
    - dual_use_risk_report.json
    - dual_use_risk_report.csv
"""

import sqlite3
import pandas as pd
import json
import re
from pathlib import Path
from datetime import datetime

class DualUseAnalyzer:
    """Analyzes entities for dual-use technology concerns"""

    # Seven Sons Defense Universities (China)
    SEVEN_SONS = [
        "Beijing Institute of Technology",
        "Beijing University of Aeronautics and Astronautics",
        "Beihang University",
        "Harbin Engineering University",
        "Harbin Institute of Technology",
        "Nanjing University of Aeronautics and Astronautics",
        "Nanjing University of Science and Technology",
        "Northwestern Polytechnical University",
        "National University of Defense Technology"
    ]

    # Dual-use keywords for cancer/biotech research
    CANCER_DUALUSE_KEYWORDS = [
        'genomics', 'genome', 'crispr', 'gene editing', 'gene therapy',
        'viral vector', 'immunotherapy', 'synthetic biology',
        'cell culture', 'pathogen', 'biosafety level', 'bsl-',
        'recombinant', 'genetic engineering', 'biotechnology',
        'dna sequencing', 'rna', 'vaccine development'
    ]

    # Dual-use keywords for environmental science
    ENVIRONMENTAL_DUALUSE_KEYWORDS = [
        'biosurveillance', 'pathogen surveillance', 'disease monitoring',
        'environmental sampling', 'remote sensing', 'satellite',
        'drone', 'uav', 'sensor network', 'microbial',
        'bioremediation', 'agricultural biotechnology', 'crop engineering',
        'water security', 'critical infrastructure', 'geographic mapping',
        'biological samples', 'environmental dna'
    ]

    def __init__(self, db_path="F:/OSINT_WAREHOUSE/osint_master.db"):
        """Initialize with database connection"""
        self.db_path = db_path
        self.conn = None

    def connect_db(self):
        """Connect to master database"""
        self.conn = sqlite3.connect(self.db_path)
        print(f"[OK] Connected to database: {self.db_path}")

    def close_db(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print("[OK] Database connection closed")

    def check_bis_entity_list(self, entity_name):
        """Check if entity is on BIS Entity List"""
        query = """
        SELECT entity_name, federal_register_notice, country
        FROM bis_entity_list_fixed
        WHERE LOWER(entity_name) LIKE LOWER(?)
        """

        cursor = self.conn.cursor()
        cursor.execute(query, (f"%{entity_name}%",))
        results = cursor.fetchall()

        if results:
            return {
                'on_bis_list': True,
                'matches': [{'name': r[0], 'citation': r[1], 'country': r[2]} for r in results]
            }
        return {'on_bis_list': False, 'matches': []}

    def check_seven_sons(self, entity_name):
        """Check if entity is a Seven Sons university or affiliated"""
        for university in self.SEVEN_SONS:
            if university.lower() in entity_name.lower():
                return {
                    'is_seven_sons': True,
                    'university': university
                }

        # Also check cross-references table
        query = """
        SELECT entity_name, sources
        FROM entity_cross_references
        WHERE LOWER(entity_name) LIKE LOWER(?)
        """

        cursor = self.conn.cursor()
        cursor.execute(query, (f"%{entity_name}%",))
        results = cursor.fetchall()

        for result in results:
            for university in self.SEVEN_SONS:
                if university.lower() in result[0].lower():
                    return {
                        'is_seven_sons': True,
                        'university': university,
                        'cross_referenced': True,
                        'sources': result[1]
                    }

        return {'is_seven_sons': False, 'university': None}

    def check_dual_use_keywords(self, description, entity_type):
        """Check for dual-use keywords in contract description"""
        if pd.isna(description) or not description:
            return {'has_dual_use_keywords': False, 'keywords_found': []}

        description_lower = description.lower()
        keywords = []

        if entity_type == 'cancer':
            keyword_list = self.CANCER_DUALUSE_KEYWORDS
        elif entity_type == 'environmental':
            keyword_list = self.ENVIRONMENTAL_DUALUSE_KEYWORDS
        else:
            return {'has_dual_use_keywords': False, 'keywords_found': []}

        for keyword in keyword_list:
            if keyword in description_lower:
                keywords.append(keyword)

        return {
            'has_dual_use_keywords': len(keywords) > 0,
            'keywords_found': keywords,
            'keyword_count': len(keywords)
        }

    def identify_entity_type(self, recipient_name, vendor_name, description):
        """Identify if entity is cancer/environmental related"""
        text = f"{recipient_name} {vendor_name} {description}".lower()

        cancer_indicators = [
            'cancer', 'oncology', 'tumor', 'hospital', 'medical center',
            'health sciences', 'clinical', 'biotechnology'
        ]

        environmental_indicators = [
            'environmental', 'ecology', 'ecosystem', 'climate',
            'pollution', 'conservation', 'sustainability', 'green',
            'eco-', 'natural resources'
        ]

        is_cancer = any(indicator in text for indicator in cancer_indicators)
        is_environmental = any(indicator in text for indicator in environmental_indicators)

        if is_cancer:
            return 'cancer'
        elif is_environmental:
            return 'environmental'
        else:
            return 'other'

    def calculate_risk_score(self, bis_check, seven_sons_check, keyword_check, award_amount):
        """Calculate risk score based on findings"""
        score = 0.0
        reasons = []

        # BIS Entity List = Highest risk
        if bis_check['on_bis_list']:
            score += 0.5
            reasons.append("On BIS Entity List (sanctioned)")

        # Seven Sons = High risk
        if seven_sons_check['is_seven_sons']:
            score += 0.3
            reasons.append(f"Seven Sons university: {seven_sons_check['university']}")

        # Dual-use keywords
        if keyword_check['has_dual_use_keywords']:
            keyword_score = min(0.3, keyword_check['keyword_count'] * 0.05)
            score += keyword_score
            reasons.append(f"Dual-use keywords found: {', '.join(keyword_check['keywords_found'][:3])}")

        # High-value contracts (>$500K)
        if not pd.isna(award_amount):
            try:
                amount = float(award_amount)
                if amount > 500000:
                    score += 0.1
                    reasons.append(f"High-value contract: ${amount:,.2f}")
            except (ValueError, TypeError):
                pass

        # Cap score at 1.0
        score = min(1.0, score)

        # Determine tier recommendation
        if score >= 0.5:
            tier_recommendation = "TIER_1"
        elif score >= 0.3:
            tier_recommendation = "TIER_2"
        else:
            tier_recommendation = "TIER_3"

        return {
            'risk_score': round(score, 2),
            'tier_recommendation': tier_recommendation,
            'reasons': reasons
        }

    def analyze_sample(self, csv_path):
        """Analyze entities in sample CSV"""
        print(f"\nAnalyzing sample: {csv_path}")

        # Load CSV
        df = pd.read_csv(csv_path)
        print(f"[OK] Loaded {len(df)} records")

        # Connect to database
        self.connect_db()

        # Analyze each record
        results = []

        for idx, row in df.iterrows():
            # Identify entity type
            entity_type = self.identify_entity_type(
                str(row.get('Recipient_Name', '')),
                str(row.get('Vendor_Name', '')),
                str(row.get('Award_Description', ''))
            )

            # Only analyze cancer and environmental entities
            if entity_type not in ['cancer', 'environmental']:
                continue

            print(f"\nAnalyzing {idx+1}/{len(df)}: {row.get('Recipient_Name', 'N/A')} ({entity_type})")

            # Check BIS Entity List
            bis_check = self.check_bis_entity_list(str(row.get('Recipient_Name', '')))
            if bis_check['on_bis_list']:
                print(f"  [!] BIS Entity List match found!")

            # Check Seven Sons
            seven_sons_check = self.check_seven_sons(str(row.get('Recipient_Name', '')))
            if seven_sons_check['is_seven_sons']:
                print(f"  [!] Seven Sons university: {seven_sons_check['university']}")

            # Check dual-use keywords
            keyword_check = self.check_dual_use_keywords(
                str(row.get('Award_Description', '')),
                entity_type
            )
            if keyword_check['has_dual_use_keywords']:
                print(f"  [!] Dual-use keywords: {', '.join(keyword_check['keywords_found'][:3])}")

            # Calculate risk score
            risk_assessment = self.calculate_risk_score(
                bis_check,
                seven_sons_check,
                keyword_check,
                row.get('Award_Amount')
            )

            # Compile result
            result = {
                'transaction_id': row.get('Transaction_ID'),
                'recipient_name': row.get('Recipient_Name'),
                'vendor_name': row.get('Vendor_Name'),
                'entity_type': entity_type,
                'current_tier': row.get('Importance_Tier'),
                'recommended_tier': risk_assessment['tier_recommendation'],
                'risk_score': risk_assessment['risk_score'],
                'on_bis_list': bis_check['on_bis_list'],
                'bis_matches': bis_check['matches'],
                'is_seven_sons': seven_sons_check['is_seven_sons'],
                'seven_sons_university': seven_sons_check.get('university'),
                'dual_use_keywords': keyword_check['keywords_found'],
                'risk_reasons': risk_assessment['reasons'],
                'award_amount': row.get('Award_Amount'),
                'award_description': str(row.get('Award_Description', ''))[:200] if pd.notna(row.get('Award_Description')) else '',
                'needs_reclassification': row.get('Importance_Tier') != risk_assessment['tier_recommendation']
            }

            results.append(result)

            print(f"  >> Risk Score: {risk_assessment['risk_score']} | Recommended: {risk_assessment['tier_recommendation']}")

        self.close_db()

        return results

    def generate_report(self, results, output_dir="analysis"):
        """Generate dual-use risk assessment report"""
        Path(output_dir).mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # JSON report
        json_path = Path(output_dir) / f"dual_use_risk_report_{timestamp}.json"
        with open(json_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n[OK] JSON report saved: {json_path}")

        # CSV report
        df = pd.DataFrame(results)
        csv_path = Path(output_dir) / f"dual_use_risk_report_{timestamp}.csv"
        df.to_csv(csv_path, index=False)
        print(f"[OK] CSV report saved: {csv_path}")

        # Summary statistics
        print("\n" + "="*60)
        print("DUAL-USE RISK ASSESSMENT SUMMARY")
        print("="*60)

        total = len(results)
        cancer = len([r for r in results if r['entity_type'] == 'cancer'])
        environmental = len([r for r in results if r['entity_type'] == 'environmental'])

        print(f"\nTotal analyzed: {total}")
        print(f"  Cancer/Biotech: {cancer}")
        print(f"  Environmental: {environmental}")

        print(f"\nHigh-Risk Findings:")
        print(f"  BIS Entity List matches: {len([r for r in results if r['on_bis_list']])}")
        print(f"  Seven Sons affiliations: {len([r for r in results if r['is_seven_sons']])}")
        print(f"  Dual-use keywords detected: {len([r for r in results if r['dual_use_keywords']])}")

        print(f"\nTier Recommendations:")
        print(f"  TIER_1 (Strategic): {len([r for r in results if r['recommended_tier'] == 'TIER_1'])}")
        print(f"  TIER_2 (Dual-Use): {len([r for r in results if r['recommended_tier'] == 'TIER_2'])}")
        print(f"  TIER_3 (Low Risk): {len([r for r in results if r['recommended_tier'] == 'TIER_3'])}")

        needs_reclass = len([r for r in results if r['needs_reclassification']])
        print(f"\nNeeds Reclassification: {needs_reclass} records ({needs_reclass/total*100:.1f}%)")

        # High-risk entities
        high_risk = [r for r in results if r['risk_score'] >= 0.5]
        if high_risk:
            print(f"\n[!] HIGH-RISK ENTITIES (score >=0.5):")
            for entity in high_risk[:10]:  # Show top 10
                print(f"  - {entity['recipient_name']}")
                print(f"    Risk Score: {entity['risk_score']} | {', '.join(entity['risk_reasons'])}")

        print("\n" + "="*60)

        return json_path, csv_path

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Analyze dual-use technology entities')
    parser.add_argument('--input',
                       default='data/processed/usaspending_manual_review/importance_tier_sample_20251018_075329.csv',
                       help='Input CSV file path')
    parser.add_argument('--db',
                       default='F:/OSINT_WAREHOUSE/osint_master.db',
                       help='Database path')
    parser.add_argument('--output-dir',
                       default='analysis',
                       help='Output directory for reports')

    args = parser.parse_args()

    print("="*60)
    print("DUAL-USE ENTITY ANALYZER")
    print("="*60)
    print(f"Input: {args.input}")
    print(f"Database: {args.db}")
    print(f"Output: {args.output_dir}/")

    # Create analyzer
    analyzer = DualUseAnalyzer(db_path=args.db)

    # Analyze sample
    results = analyzer.analyze_sample(args.input)

    # Generate report
    analyzer.generate_report(results, output_dir=args.output_dir)

    print("\n[SUCCESS] Analysis complete!")

if __name__ == "__main__":
    main()

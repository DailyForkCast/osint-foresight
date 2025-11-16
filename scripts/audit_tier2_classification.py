#!/usr/bin/env python3
"""
audit_tier2_classification.py - TIER_2 Systemic Audit

Identifies classification problems in TIER_2:
1. False positives (substring matches like "Kachina", casinos, etc.)
2. Under-classified entities (biotech/pharma that should be TIER_1)
3. Supply chain entities that should be separate

Based on manual review findings:
- Substring false positives: Kachina, Catalina China, Facchina
- Casinos/hotels: Not Chinese entities
- Biotech/pharma: Need dual-use risk assessment
- Italian companies: SOC COOP LIVORNESE

Usage:
    python audit_tier2_classification.py --input importance_tier_sample_20251018_075329.csv
"""

import pandas as pd
import json
import re
from pathlib import Path
from datetime import datetime

class Tier2Auditor:
    """Audit TIER_2 classifications for systematic errors"""

    # False positive patterns identified from manual review
    FALSE_POSITIVE_PATTERNS = {
        # Substring matches (not actually Chinese)
        'substring_china': [
            r'\bkachina\b',  # Kachina Investments/Ventures
            r'\bcatalina china\b',  # Catalina China Inc (US company)
            r'\bfacchina\b',  # Italian logistics company
            r'\bchina\s+grove\b',  # US location
            r'\bchina\s+lake\b',  # US Naval base
            r'\bchina\s+spring\b',  # US location
        ],

        # Casinos and hotels (place of performance, not entity nationality)
        'casino_hotel': [
            r'\bcasino\b',
            r'\bresort\b',
            r'\bhotel\b',
            r'\bgaming\b',
            r'\bharrahs\b',
            r'\bsafari\s+park\b',
        ],

        # Italian companies with China in name
        'italian_companies': [
            r'\bsoc\s+coop\s+livornese\b',
            r'\bfacchinaggi\b',
            r'\btrasporti\b',
        ],

        # Skydiving/recreational
        'recreational': [
            r'\bskydive\b',
            r'\bparachute\b',
        ],

        # Generic consulting (US companies)
        'us_consulting': [
            r'\bmsd\s+biztech\b',
            r'\brushinov\b',
        ],

        # Insurance companies
        'insurance': [
            r'\binsurance\s+company\b',
            r'\bassurance\b',
        ]
    }

    # Biotech/pharma companies that need dual-use assessment
    BIOTECH_PHARMA_INDICATORS = [
        'pharmaron', 'chempartner', 'wuxi', 'biologics', 'pharma',
        'drug', 'medicine', 'clinical', 'biotechnology', 'bio-tech',
        'pharmaceutical', 'therapeutics', 'cro', 'cdmo'
    ]

    # Laser/optics companies (military dual-use)
    LASER_OPTICS_INDICATORS = [
        'laser', 'optics', 'photonics', 'optical', 'electro-optical',
        'infrared', 'lidar', 'fiber optic'
    ]

    # Known supply chain entities
    SUPPLY_CHAIN_ENTITIES = [
        'lenovo', 'huawei technologies usa', 'zte corporation',
        'tp-link', 'haier', 'hisense', 'tcl', 'xiaomi'
    ]

    def __init__(self):
        self.audit_results = {
            'false_positives': [],
            'under_classified': [],
            'supply_chain': [],
            'needs_review': []
        }

    def check_false_positive(self, entity_name, description):
        """Check if entity matches false positive patterns"""
        text = f"{entity_name} {description}".lower()

        matches = []
        for pattern_type, patterns in self.FALSE_POSITIVE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    matches.append({
                        'type': pattern_type,
                        'pattern': pattern
                    })

        return matches

    def check_biotech_pharma(self, entity_name, description):
        """Check if biotech/pharma entity needs TIER_1 assessment"""
        text = f"{entity_name} {description}".lower()

        for indicator in self.BIOTECH_PHARMA_INDICATORS:
            if indicator in text:
                return True
        return False

    def check_laser_optics(self, entity_name, description):
        """Check if laser/optics entity (dual-use military)"""
        text = f"{entity_name} {description}".lower()

        for indicator in self.LASER_OPTICS_INDICATORS:
            if indicator in text:
                return True
        return False

    def check_supply_chain(self, entity_name):
        """Check if known supply chain entity"""
        entity_lower = entity_name.lower()

        for supplier in self.SUPPLY_CHAIN_ENTITIES:
            if supplier in entity_lower:
                return True
        return False

    def audit_record(self, row):
        """Audit a single TIER_2 record"""
        entity_name = str(row.get('Recipient_Name', ''))
        vendor_name = str(row.get('Vendor_Name', ''))
        description = str(row.get('Award_Description', ''))

        # Check false positives
        fp_matches = self.check_false_positive(entity_name, description)
        if fp_matches:
            return {
                'issue_type': 'FALSE_POSITIVE',
                'pattern_type': fp_matches[0]['type'],
                'recommendation': 'REMOVE',
                'reason': f"Matches false positive pattern: {fp_matches[0]['pattern']}"
            }

        # Check biotech/pharma
        if self.check_biotech_pharma(entity_name, description):
            return {
                'issue_type': 'UNDER_CLASSIFIED',
                'category': 'BIOTECH_PHARMA',
                'recommendation': 'ASSESS_FOR_TIER_1',
                'reason': 'Biotech/pharma entity with potential dual-use concerns'
            }

        # Check laser/optics
        if self.check_laser_optics(entity_name, description):
            return {
                'issue_type': 'UNDER_CLASSIFIED',
                'category': 'LASER_OPTICS',
                'recommendation': 'ASSESS_FOR_TIER_1',
                'reason': 'Laser/optics entity with military dual-use potential'
            }

        # Check supply chain
        if self.check_supply_chain(entity_name):
            return {
                'issue_type': 'SUPPLY_CHAIN',
                'category': 'COMMERCIAL_IT',
                'recommendation': 'MOVE_TO_SUPPLY_CHAIN_TRACKER',
                'reason': 'Known commercial IT supplier'
            }

        # No issues found
        return {
            'issue_type': 'OK',
            'recommendation': 'KEEP_TIER_2',
            'reason': 'No classification issues detected'
        }

    def audit_sample(self, csv_path):
        """Audit all TIER_2 records in sample"""
        print(f"\nAuditing TIER_2 records in: {csv_path}")

        df = pd.read_csv(csv_path)

        # Filter to TIER_2 only
        tier2_df = df[df['Importance_Tier'] == 'TIER_2']
        print(f"[OK] Found {len(tier2_df)} TIER_2 records")

        results = []

        for idx, row in tier2_df.iterrows():
            audit_result = self.audit_record(row)

            result = {
                'transaction_id': row.get('Transaction_ID'),
                'recipient_name': row.get('Recipient_Name'),
                'vendor_name': row.get('Vendor_Name'),
                'award_description': str(row.get('Award_Description', ''))[:200],
                'current_tier': row.get('Importance_Tier'),
                'issue_type': audit_result['issue_type'],
                'recommendation': audit_result['recommendation'],
                'reason': audit_result['reason']
            }

            if 'category' in audit_result:
                result['category'] = audit_result['category']
            if 'pattern_type' in audit_result:
                result['pattern_type'] = audit_result['pattern_type']

            results.append(result)

            # Categorize
            if audit_result['issue_type'] == 'FALSE_POSITIVE':
                self.audit_results['false_positives'].append(result)
                print(f"  [FP] {row.get('Recipient_Name')} - {audit_result['reason']}")
            elif audit_result['issue_type'] == 'UNDER_CLASSIFIED':
                self.audit_results['under_classified'].append(result)
                print(f"  [UP] {row.get('Recipient_Name')} - {audit_result['reason']}")
            elif audit_result['issue_type'] == 'SUPPLY_CHAIN':
                self.audit_results['supply_chain'].append(result)
                print(f"  [SC] {row.get('Recipient_Name')} - {audit_result['reason']}")

        return results

    def generate_report(self, results, output_dir="analysis"):
        """Generate audit report"""
        Path(output_dir).mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # JSON report
        json_path = Path(output_dir) / f"tier2_audit_report_{timestamp}.json"
        with open(json_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n[OK] JSON report: {json_path}")

        # CSV report
        df = pd.DataFrame(results)
        csv_path = Path(output_dir) / f"tier2_audit_report_{timestamp}.csv"
        df.to_csv(csv_path, index=False)
        print(f"[OK] CSV report: {csv_path}")

        # Summary
        print("\n" + "="*60)
        print("TIER_2 AUDIT SUMMARY")
        print("="*60)

        total = len(results)
        fp_count = len(self.audit_results['false_positives'])
        uc_count = len(self.audit_results['under_classified'])
        sc_count = len(self.audit_results['supply_chain'])
        ok_count = total - fp_count - uc_count - sc_count

        print(f"\nTotal TIER_2 records audited: {total}")
        print(f"\nClassification Issues:")
        print(f"  FALSE POSITIVES: {fp_count} ({fp_count/total*100:.1f}%)")
        print(f"  UNDER-CLASSIFIED: {uc_count} ({uc_count/total*100:.1f}%)")
        print(f"  SUPPLY CHAIN: {sc_count} ({sc_count/total*100:.1f}%)")
        print(f"  CORRECTLY CLASSIFIED: {ok_count} ({ok_count/total*100:.1f}%)")

        # False positive breakdown
        if fp_count > 0:
            print(f"\nFalse Positive Patterns:")
            fp_df = pd.DataFrame(self.audit_results['false_positives'])
            for pattern_type in fp_df['pattern_type'].unique():
                count = len(fp_df[fp_df['pattern_type'] == pattern_type])
                print(f"  {pattern_type}: {count}")

        # Under-classified breakdown
        if uc_count > 0:
            print(f"\nUnder-Classified Categories:")
            uc_df = pd.DataFrame(self.audit_results['under_classified'])
            for category in uc_df['category'].unique():
                count = len(uc_df[uc_df['category'] == category])
                print(f"  {category}: {count}")
                # Show examples
                examples = uc_df[uc_df['category'] == category]['recipient_name'].head(3)
                for ex in examples:
                    print(f"    - {ex}")

        print("\n" + "="*60)
        print("RECOMMENDATIONS")
        print("="*60)

        print(f"\n1. REMOVE {fp_count} false positives from detections")
        print(f"2. ASSESS {uc_count} under-classified entities for TIER_1")
        print(f"3. MOVE {sc_count} entities to supply chain tracker")
        print(f"4. RE-PROCESS all TIER_2 with updated logic")

        print("\n" + "="*60)

        return json_path, csv_path

    def generate_false_positive_filters(self, output_path="scripts/tier2_false_positives.py"):
        """Generate Python code for false positive filters"""

        if not self.audit_results['false_positives']:
            print("No false positives to generate filters for")
            return

        # Collect unique entities
        fp_entities = set()
        for fp in self.audit_results['false_positives']:
            fp_entities.add(fp['recipient_name'])

        # Generate Python code
        code = '''#!/usr/bin/env python3
"""
TIER_2 False Positive Filters
Auto-generated from manual audit on {timestamp}

Add these to your processors' FALSE_POSITIVES list
"""

TIER2_FALSE_POSITIVES = [
    # Substring matches (Kachina, Catalina, Facchina)
'''.format(timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        for entity in sorted(fp_entities):
            code += f'    "{entity}",\n'

        code += ''']

# Pattern-based filters (add to processor logic)
FALSE_POSITIVE_PATTERNS = {
    'substring_china': [
        r'\\bkachina\\b',
        r'\\bcatalina china\\b',
        r'\\bfacchina\\b',
    ],
    'casino_hotel': [
        r'\\bcasino\\b',
        r'\\bresort\\b',
        r'\\bhotel\\b',
    ],
    'italian_companies': [
        r'\\bsoc coop livornese\\b',
        r'\\bfacchinaggi\\b',
    ]
}
'''

        with open(output_path, 'w') as f:
            f.write(code)

        print(f"[OK] False positive filters generated: {output_path}")

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Audit TIER_2 classifications')
    parser.add_argument('--input',
                       default='data/processed/usaspending_manual_review/importance_tier_sample_20251018_075329.csv',
                       help='Input CSV file')
    parser.add_argument('--output-dir',
                       default='analysis',
                       help='Output directory')

    args = parser.parse_args()

    print("="*60)
    print("TIER_2 CLASSIFICATION AUDIT")
    print("="*60)

    auditor = Tier2Auditor()
    results = auditor.audit_sample(args.input)
    auditor.generate_report(results, output_dir=args.output_dir)
    auditor.generate_false_positive_filters()

    print("\n[SUCCESS] TIER_2 audit complete!")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
extract_medical_research_entities.py - Extract Medical Research Entities

Extracts all medical/cancer/biotech research entities and screens for PLA connections.
"""

import sqlite3
import pandas as pd
from datetime import datetime
from pathlib import Path
import json

class MedicalResearchExtractor:
    """Extract and screen medical research entities"""

    # Medical research keywords
    MEDICAL_KEYWORDS = [
        'hospital', 'medical', 'cancer', 'oncology', 'tumor', 'genomics',
        'genetics', 'biotech', 'pharmaceutical', 'clinical', 'medicine',
        'health', 'disease', 'pathology', 'immunology', 'virology',
        'biotechnology', 'bioscience', 'biomedical', 'pharmacy',
        'therapeutics', 'diagnosis', 'treatment', 'cure', 'therapy'
    ]

    # Seven Sons Universities
    SEVEN_SONS = [
        'beijing institute of technology',
        'beijing university of aeronautics',
        'beihang',
        'harbin engineering university',
        'harbin institute of technology',
        'nanjing university of aeronautics',
        'nanjing university of science and technology',
        'northwestern polytechnical',
        'national university of defense'
    ]

    # Known PLA medical institutions
    PLA_MEDICAL = [
        'pla', 'people.*liberation.*army',
        'military.*medical', 'military.*hospital',
        'general hospital of.*military',
        '301.*hospital', '302.*hospital', '307.*hospital',
        'chinese academy of military',
        'academy of military medical sciences',
        'fourth military medical university',
        'second military medical university',
        'third military medical university'
    ]

    # Chinese Academy of Sciences institutes
    CAS_INSTITUTES = [
        'chinese academy of sciences',
        'cas',
        'beijing institute of genomics',
        'shanghai institute.*biological',
        'institute of biophysics'
    ]

    def __init__(self):
        self.db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
        self.conn = sqlite3.connect(self.db_path)

    def extract_medical_entities(self):
        """Extract all medical research entities"""

        print("="*60)
        print("MEDICAL RESEARCH ENTITY EXTRACTION")
        print("="*60)

        tables = ['usaspending_china_305', 'usaspending_china_101', 'usaspending_china_comprehensive']

        all_entities = []

        for table in tables:
            print(f"\n[{table}]")

            # Build query with medical keywords
            conditions = " OR ".join([f"recipient_name LIKE '%{kw}%' OR award_description LIKE '%{kw}%'"
                                     for kw in self.MEDICAL_KEYWORDS])

            query = f"""
                SELECT DISTINCT
                    recipient_name,
                    award_description,
                    importance_tier,
                    highest_confidence,
                    COUNT(*) as contract_count,
                    SUM(CAST(award_amount AS REAL)) as total_value
                FROM {table}
                WHERE ({conditions})
                  AND recipient_name IS NOT NULL
                GROUP BY recipient_name
                ORDER BY total_value DESC
            """

            try:
                df = pd.read_sql(query, self.conn)
                df['source_table'] = table
                all_entities.append(df)
                print(f"  Found {len(df)} medical entities")
            except Exception as e:
                print(f"  Error: {e}")

        # Combine results
        combined = pd.concat(all_entities, ignore_index=True)
        print(f"\nTotal unique medical entities: {len(combined)}")

        return combined

    def screen_pla_connections(self, entities_df):
        """Screen entities for PLA/military connections"""

        print("\n" + "="*60)
        print("PLA CONNECTION SCREENING")
        print("="*60)

        results = []

        for _, row in entities_df.iterrows():
            entity_name = str(row['recipient_name']).lower()
            description = str(row.get('award_description', '')).lower()
            text = f"{entity_name} {description}"

            result = {
                'entity_name': row['recipient_name'],
                'tier': row['importance_tier'],
                'confidence': row['highest_confidence'],
                'contract_count': row['contract_count'],
                'total_value': row['total_value'],
                'source_table': row['source_table'],
                'pla_risk_level': 'LOW',
                'risk_factors': [],
                'recommendation': 'MONITOR'
            }

            # Check Seven Sons
            for uni in self.SEVEN_SONS:
                if uni in entity_name:
                    result['risk_factors'].append(f'SEVEN_SONS: {uni}')
                    result['pla_risk_level'] = 'CRITICAL'
                    result['recommendation'] = 'TIER_1_UPGRADE'

            # Check PLA institutions
            import re
            for pla in self.PLA_MEDICAL:
                if re.search(pla, entity_name, re.I):
                    result['risk_factors'].append(f'PLA_MEDICAL: {pla}')
                    result['pla_risk_level'] = 'CRITICAL'
                    result['recommendation'] = 'TIER_1_UPGRADE'

            # Check CAS
            for cas in self.CAS_INSTITUTES:
                if cas in entity_name:
                    result['risk_factors'].append(f'CAS_INSTITUTE: {cas}')
                    if result['pla_risk_level'] == 'LOW':
                        result['pla_risk_level'] = 'HIGH'
                    result['recommendation'] = 'TIER_1_UPGRADE'

            # Dual-use keywords
            dualuse_keywords = [
                'genomics', 'gene editing', 'crispr', 'synthetic biology',
                'viral vector', 'pathogen', 'bioweapon', 'biosafety',
                'military', 'defense', 'weapons'
            ]

            for keyword in dualuse_keywords:
                if keyword in text:
                    result['risk_factors'].append(f'DUAL_USE: {keyword}')
                    if result['pla_risk_level'] == 'LOW':
                        result['pla_risk_level'] = 'MEDIUM'

            results.append(result)

        return pd.DataFrame(results)

    def generate_report(self, screened_df):
        """Generate medical research report"""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path("analysis")
        output_dir.mkdir(exist_ok=True)

        # Excel report
        excel_path = output_dir / f"medical_research_pla_screening_{timestamp}.xlsx"

        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            # Summary
            summary_data = {
                'Metric': [
                    'Total Medical Entities',
                    'CRITICAL Risk (PLA/Seven Sons)',
                    'HIGH Risk (CAS)',
                    'MEDIUM Risk (Dual-use)',
                    'LOW Risk',
                    'Recommend TIER_1 Upgrade'
                ],
                'Value': [
                    len(screened_df),
                    len(screened_df[screened_df['pla_risk_level'] == 'CRITICAL']),
                    len(screened_df[screened_df['pla_risk_level'] == 'HIGH']),
                    len(screened_df[screened_df['pla_risk_level'] == 'MEDIUM']),
                    len(screened_df[screened_df['pla_risk_level'] == 'LOW']),
                    len(screened_df[screened_df['recommendation'] == 'TIER_1_UPGRADE'])
                ]
            }
            pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)

            # All entities
            screened_df.to_excel(writer, sheet_name='All Entities', index=False)

            # Critical risk
            critical = screened_df[screened_df['pla_risk_level'] == 'CRITICAL']
            if len(critical) > 0:
                critical.to_excel(writer, sheet_name='CRITICAL - PLA Linked', index=False)

            # High risk
            high = screened_df[screened_df['pla_risk_level'] == 'HIGH']
            if len(high) > 0:
                high.to_excel(writer, sheet_name='HIGH - CAS Institutes', index=False)

            # Needs upgrade
            upgrade = screened_df[screened_df['recommendation'] == 'TIER_1_UPGRADE']
            if len(upgrade) > 0:
                upgrade.to_excel(writer, sheet_name='Recommend TIER_1 Upgrade', index=False)

        print(f"\n[OK] Excel report: {excel_path}")

        # JSON report
        json_path = output_dir / f"medical_research_pla_screening_{timestamp}.json"

        report = {
            'extraction_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'total_entities': len(screened_df),
            'risk_breakdown': screened_df['pla_risk_level'].value_counts().to_dict(),
            'entities': screened_df.to_dict('records')
        }

        with open(json_path, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"[OK] JSON report: {json_path}")

        # Print summary
        print("\n" + "="*60)
        print("SCREENING SUMMARY")
        print("="*60)

        print(f"\nTotal medical entities: {len(screened_df)}")
        print("\nRisk Breakdown:")
        for risk, count in screened_df['pla_risk_level'].value_counts().items():
            print(f"  {risk}: {count}")

        print("\nCRITICAL Risk Entities (PLA/Seven Sons):")
        critical = screened_df[screened_df['pla_risk_level'] == 'CRITICAL']
        if len(critical) > 0:
            for _, row in critical.iterrows():
                print(f"  - {row['entity_name']}")
                print(f"    Tier: {row['tier']}, Contracts: {row['contract_count']}")
                print(f"    Risk Factors: {', '.join(row['risk_factors'])}")
        else:
            print("  (None found)")

        print("\nHIGH Risk Entities (CAS):")
        high = screened_df[screened_df['pla_risk_level'] == 'HIGH']
        if len(high) > 0:
            for _, row in high.head(10).iterrows():
                print(f"  - {row['entity_name']}")
                print(f"    Tier: {row['tier']}, Contracts: {row['contract_count']}")
                print(f"    Risk Factors: {', '.join(row['risk_factors'])}")
        else:
            print("  (None found)")

        print("\n" + "="*60)

        return excel_path, json_path

    def close(self):
        self.conn.close()

def main():
    extractor = MedicalResearchExtractor()

    # Extract entities
    entities_df = extractor.extract_medical_entities()

    # Screen for PLA
    screened_df = extractor.screen_pla_connections(entities_df)

    # Generate report
    extractor.generate_report(screened_df)

    extractor.close()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
generate_validation_sample.py - Generate Stratified Sample for Manual Validation

Creates representative sample of 50 Form D entities for manual review to:
1. Calculate false positive rate
2. Categorize types of China-linked activity
3. Identify concerning vs non-concerning matches

Stratification:
- Time period: Recent (2024-2025) vs Historical (2015-2020)
- Industry: Dual-use sectors vs Pooled Funds vs Other
- Detection method: City match vs State match
- Capital size: Large (>$100M) vs Small (<$100M)

Output: Excel file with entity details + manual review columns

Last Updated: 2025-10-23
"""

import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime
import random

class ValidationSampleGenerator:
    """Generate stratified validation sample"""

    def __init__(self, db_path='F:/OSINT_WAREHOUSE/osint_master.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.samples = []

        print("="*70)
        print("VALIDATION SAMPLE GENERATOR")
        print("="*70)
        print(f"Database: {db_path}")
        print(f"Target sample size: 50 entities")
        print("="*70)

    def get_recent_dual_use(self, n=10):
        """Get recent dual-use technology sector matches"""
        print(f"\n1. Sampling {n} recent dual-use technology entities (2024-2025)...")

        dual_use_sectors = [
            'Biotechnology', 'Pharmaceuticals', 'Other Technology',
            'Semiconductors', 'Artificial Intelligence', 'Aerospace',
            'Manufacturing'
        ]

        query = f"""
            SELECT DISTINCT
                o.accession_number,
                o.issuer_name,
                o.industry_group_type,
                o.total_offering_amount,
                o.collected_quarter,
                p.person_name,
                p.person_address_city,
                p.person_address_state,
                p.relationship
            FROM sec_form_d_persons p
            JOIN sec_form_d_offerings o ON p.accession_number = o.accession_number
            WHERE (
                p.person_address_state LIKE '%Hong Kong%'
                OR p.person_address_state LIKE '%China%'
                OR p.person_address_city IN ('Beijing', 'Shanghai', 'Shenzhen', 'Hangzhou', 'Guangzhou')
            )
            AND o.collected_quarter >= '2024q1'
            AND o.industry_group_type IN ({','.join(['?']*len(dual_use_sectors))})
            ORDER BY RANDOM()
            LIMIT ?
        """

        cursor = self.conn.cursor()
        cursor.execute(query, dual_use_sectors + [n])
        results = cursor.fetchall()

        for row in results:
            self.samples.append({
                'accession_number': row[0],
                'issuer_name': row[1],
                'industry': row[2],
                'offering_amount': row[3],
                'quarter': row[4],
                'person_name': row[5],
                'person_city': row[6],
                'person_state': row[7],
                'person_relationship': row[8],
                'sample_category': 'Recent Dual-Use Tech',
                'priority': 'HIGH'
            })

        print(f"   Found {len(results)} dual-use tech entities")
        return len(results)

    def get_recent_pooled_funds(self, n=10):
        """Get recent pooled investment fund matches"""
        print(f"\n2. Sampling {n} recent pooled investment funds (2024-2025)...")

        query = """
            SELECT DISTINCT
                o.accession_number,
                o.issuer_name,
                o.industry_group_type,
                o.total_offering_amount,
                o.collected_quarter,
                p.person_name,
                p.person_address_city,
                p.person_address_state,
                p.relationship
            FROM sec_form_d_persons p
            JOIN sec_form_d_offerings o ON p.accession_number = o.accession_number
            WHERE (
                p.person_address_state LIKE '%Hong Kong%'
                OR p.person_address_state LIKE '%China%'
                OR p.person_address_city IN ('Beijing', 'Shanghai', 'Shenzhen', 'Hangzhou', 'Guangzhou')
            )
            AND o.collected_quarter >= '2024q1'
            AND o.industry_group_type = 'Pooled Investment Fund'
            ORDER BY RANDOM()
            LIMIT ?
        """

        cursor = self.conn.cursor()
        cursor.execute(query, (n,))
        results = cursor.fetchall()

        for row in results:
            self.samples.append({
                'accession_number': row[0],
                'issuer_name': row[1],
                'industry': row[2],
                'offering_amount': row[3],
                'quarter': row[4],
                'person_name': row[5],
                'person_city': row[6],
                'person_state': row[7],
                'person_relationship': row[8],
                'sample_category': 'Recent Pooled Fund',
                'priority': 'MEDIUM'
            })

        print(f"   Found {len(results)} pooled fund entities")
        return len(results)

    def get_historical_high_value(self, n=10):
        """Get historical high-value offerings (>$100M)"""
        print(f"\n3. Sampling {n} historical high-value offerings (2015-2023)...")

        query = """
            SELECT DISTINCT
                o.accession_number,
                o.issuer_name,
                o.industry_group_type,
                o.total_offering_amount,
                o.collected_quarter,
                p.person_name,
                p.person_address_city,
                p.person_address_state,
                p.relationship
            FROM sec_form_d_persons p
            JOIN sec_form_d_offerings o ON p.accession_number = o.accession_number
            WHERE (
                p.person_address_state LIKE '%Hong Kong%'
                OR p.person_address_state LIKE '%China%'
                OR p.person_address_city IN ('Beijing', 'Shanghai', 'Shenzhen', 'Hangzhou', 'Guangzhou')
            )
            AND o.collected_quarter < '2024q1'
            AND o.total_offering_amount > 100000000
            ORDER BY RANDOM()
            LIMIT ?
        """

        cursor = self.conn.cursor()
        cursor.execute(query, (n,))
        results = cursor.fetchall()

        for row in results:
            self.samples.append({
                'accession_number': row[0],
                'issuer_name': row[1],
                'industry': row[2],
                'offering_amount': row[3],
                'quarter': row[4],
                'person_name': row[5],
                'person_city': row[6],
                'person_state': row[7],
                'person_relationship': row[8],
                'sample_category': 'Historical High-Value',
                'priority': 'MEDIUM'
            })

        print(f"   Found {len(results)} high-value historical entities")
        return len(results)

    def get_known_vc_firms(self, n=10):
        """Get matches to known Chinese VC firms"""
        print(f"\n4. Sampling {n} known Chinese VC firm matches...")

        known_firms = [
            'Sequoia Capital China',
            'IDG Capital',
            'Hillhouse',
            'Qiming',
            'GGV Capital',
            'Sinovation',
            'ZhenFund',
            'Matrix Partners China',
            'Shunwei'
        ]

        samples_collected = []

        for firm in known_firms:
            if len(samples_collected) >= n:
                break

            query = """
                SELECT DISTINCT
                    o.accession_number,
                    o.issuer_name,
                    o.industry_group_type,
                    o.total_offering_amount,
                    o.collected_quarter,
                    p.person_name,
                    p.person_address_city,
                    p.person_address_state,
                    p.relationship
                FROM sec_form_d_persons p
                JOIN sec_form_d_offerings o ON p.accession_number = o.accession_number
                WHERE o.issuer_name LIKE ?
                ORDER BY o.collected_quarter DESC
                LIMIT 2
            """

            cursor = self.conn.cursor()
            cursor.execute(query, (f'%{firm}%',))
            results = cursor.fetchall()

            for row in results:
                if len(samples_collected) >= n:
                    break

                self.samples.append({
                    'accession_number': row[0],
                    'issuer_name': row[1],
                    'industry': row[2],
                    'offering_amount': row[3],
                    'quarter': row[4],
                    'person_name': row[5],
                    'person_city': row[6],
                    'person_state': row[7],
                    'person_relationship': row[8],
                    'sample_category': 'Known VC Firm',
                    'priority': 'HIGH'
                })
                samples_collected.append(row)

        print(f"   Found {len(samples_collected)} known VC firm entities")
        return len(samples_collected)

    def get_random_mixed(self, n=10):
        """Get random mixed sample from remaining"""
        print(f"\n5. Sampling {n} random mixed entities (all periods/types)...")

        query = """
            SELECT DISTINCT
                o.accession_number,
                o.issuer_name,
                o.industry_group_type,
                o.total_offering_amount,
                o.collected_quarter,
                p.person_name,
                p.person_address_city,
                p.person_address_state,
                p.relationship
            FROM sec_form_d_persons p
            JOIN sec_form_d_offerings o ON p.accession_number = o.accession_number
            WHERE (
                p.person_address_state LIKE '%Hong Kong%'
                OR p.person_address_state LIKE '%China%'
                OR p.person_address_city IN ('Beijing', 'Shanghai', 'Shenzhen', 'Hangzhou', 'Guangzhou')
            )
            ORDER BY RANDOM()
            LIMIT ?
        """

        cursor = self.conn.cursor()
        cursor.execute(query, (n,))
        results = cursor.fetchall()

        for row in results:
            self.samples.append({
                'accession_number': row[0],
                'issuer_name': row[1],
                'industry': row[2],
                'offering_amount': row[3],
                'quarter': row[4],
                'person_name': row[5],
                'person_city': row[6],
                'person_state': row[7],
                'person_relationship': row[8],
                'sample_category': 'Random Mixed',
                'priority': 'LOW'
            })

        print(f"   Found {len(results)} random mixed entities")
        return len(results)

    def generate_sample(self):
        """Generate full stratified sample"""
        print("\nGenerating stratified validation sample...\n")

        # Get samples from each category
        self.get_recent_dual_use(10)
        self.get_recent_pooled_funds(10)
        self.get_known_vc_firms(10)
        self.get_historical_high_value(10)
        self.get_random_mixed(10)

        print("\n" + "="*70)
        print(f"SAMPLE GENERATION COMPLETE: {len(self.samples)} entities")
        print("="*70)

        return self.samples

    def export_to_excel(self, samples):
        """Export sample to Excel for manual review"""
        print("\nExporting to Excel for manual review...")

        # Create DataFrame
        df = pd.DataFrame(samples)

        # Add manual review columns
        df['manual_category'] = ''
        df['manual_category_notes'] = """
Options:
1. CHINESE_GOV_VC - Chinese government-backed VC firm
2. CHINESE_PRIVATE_VC - Private Chinese VC firm
3. US_EU_FUND_CHINA_FOCUS - US/EU fund investing IN China
4. LEGITIMATE_BUSINESS - Legitimate cross-border business
5. FALSE_POSITIVE - Clear false positive
"""

        df['concern_level'] = ''
        df['concern_level_notes'] = """
Options:
HIGH - National security concern
MEDIUM - Potential concern, needs more review
LOW - Minimal concern
NONE - No concern
"""

        df['dual_use_technology'] = ''
        df['dual_use_notes'] = 'Y/N - Does this involve dual-use technology?'

        df['verification_source'] = ''
        df['verification_source_notes'] = 'URL or source used to verify entity'

        df['reviewer_name'] = ''
        df['review_date'] = ''
        df['additional_notes'] = ''

        # Format offering amount
        df['offering_amount_formatted'] = df['offering_amount'].apply(
            lambda x: f"${x/1e6:.2f}M" if pd.notna(x) and x > 0 else "Not disclosed"
        )

        # Reorder columns for easy review
        review_cols = [
            'priority',
            'sample_category',
            'issuer_name',
            'industry',
            'offering_amount_formatted',
            'quarter',
            'person_name',
            'person_city',
            'person_state',
            'person_relationship',
            'accession_number',
            'manual_category',
            'concern_level',
            'dual_use_technology',
            'verification_source',
            'reviewer_name',
            'review_date',
            'additional_notes'
        ]

        df_export = df[review_cols]

        # Export
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = Path(f'analysis/manual_review/validation_sample_{timestamp}.xlsx')
        output_path.parent.mkdir(parents=True, exist_ok=True)

        df_export.to_excel(output_path, index=False, sheet_name='Validation Sample')

        print(f"\n[OK] Exported to: {output_path}")
        print(f"     Total entities: {len(df_export)}")
        print(f"     Ready for manual review")

        # Also save summary
        summary_path = Path(f'analysis/manual_review/validation_sample_{timestamp}_summary.txt')
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("VALIDATION SAMPLE SUMMARY\n")
            f.write("="*70 + "\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total entities: {len(df_export)}\n\n")
            f.write("Sample Breakdown:\n")
            f.write(df['sample_category'].value_counts().to_string())
            f.write("\n\nPriority Breakdown:\n")
            f.write(df['priority'].value_counts().to_string())
            f.write("\n\nIndustry Breakdown:\n")
            f.write(df['industry'].value_counts().to_string())
            f.write("\n\n" + "="*70 + "\n")
            f.write("MANUAL REVIEW INSTRUCTIONS\n")
            f.write("="*70 + "\n\n")
            f.write("For each entity:\n")
            f.write("1. Google the issuer_name\n")
            f.write("2. Check SEC EDGAR for accession_number\n")
            f.write("3. Categorize into manual_category (see Excel notes)\n")
            f.write("4. Assess concern_level (HIGH/MEDIUM/LOW/NONE)\n")
            f.write("5. Note if dual-use technology involved (Y/N)\n")
            f.write("6. Record verification source (URL)\n")
            f.write("7. Add your name and date\n\n")
            f.write("When complete, calculate:\n")
            f.write("- False positive rate = (FALSE_POSITIVE count) / (Total count)\n")
            f.write("- Concerning entities = (CHINESE_GOV_VC + concern_level=HIGH)\n")
            f.write("- Actual Chinese VC rate = (Total - FALSE_POSITIVE - US_EU_FUND) / Total\n")
            f.write("\n" + "="*70 + "\n")

        print(f"[OK] Summary saved to: {summary_path}")

        return output_path, summary_path


def main():
    """Generate validation sample"""
    generator = ValidationSampleGenerator()
    samples = generator.generate_sample()
    excel_path, summary_path = generator.export_to_excel(samples)

    print("\n" + "="*70)
    print("NEXT STEPS")
    print("="*70)
    print(f"1. Open Excel file: {excel_path}")
    print(f"2. Review summary: {summary_path}")
    print(f"3. For each entity:")
    print(f"   - Google the company name")
    print(f"   - Check SEC EDGAR filing")
    print(f"   - Categorize and assess concern level")
    print(f"4. Calculate false positive rate from results")
    print("="*70)


if __name__ == '__main__':
    main()

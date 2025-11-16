"""
EPO Patents Validation - Sample Verification
============================================
Validate that EPO patents database contains real Chinese patent applications
by sampling and preparing for manual verification.

Author: OSINT Foresight Analysis
Date: 2025-10-25
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path

class EPOPatentsValidator:
    def __init__(self):
        self.db_path = 'F:/OSINT_WAREHOUSE/osint_master.db'
        self.output_dir = Path('analysis/manual_review')
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def get_database_overview(self):
        """Get overview of EPO patents database"""
        print("\n" + "="*70)
        print("EPO PATENTS DATABASE OVERVIEW")
        print("="*70)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Total patents
        cursor.execute('SELECT COUNT(*) FROM epo_patents')
        total_patents = cursor.fetchone()[0]
        print(f"\nTotal patents in database: {total_patents:,}")

        # Chinese entities verification
        cursor.execute('SELECT COUNT(*) FROM epo_patents WHERE is_chinese_entity = 1')
        chinese_patents = cursor.fetchone()[0]
        print(f"Chinese entity patents: {chinese_patents:,} ({chinese_patents/total_patents*100:.1f}%)")

        # Dual-use flagged
        cursor.execute('SELECT COUNT(*) FROM epo_patents WHERE has_dual_use = 1')
        dual_use_patents = cursor.fetchone()[0]
        print(f"Dual-use flagged: {dual_use_patents:,} ({dual_use_patents/total_patents*100:.1f}%)")

        # Date range
        cursor.execute('SELECT MIN(filing_date), MAX(filing_date) FROM epo_patents')
        min_date, max_date = cursor.fetchone()
        print(f"\nFiling date range: {min_date} to {max_date}")

        # Top applicant countries
        print("\nTop applicant countries:")
        cursor.execute('''
            SELECT applicant_country, COUNT(*) as count
            FROM epo_patents
            GROUP BY applicant_country
            ORDER BY count DESC
            LIMIT 10
        ''')
        for country, count in cursor.fetchall():
            print(f"  {country}: {count:,}")

        # Top applicants
        print("\nTop 10 Chinese applicants:")
        cursor.execute('''
            SELECT applicant_name, COUNT(*) as count
            FROM epo_patents
            WHERE is_chinese_entity = 1
            GROUP BY applicant_name
            ORDER BY count DESC
            LIMIT 10
        ''')
        for applicant, count in cursor.fetchall():
            print(f"  {applicant}: {count:,}")

        conn.close()

    def generate_stratified_sample(self):
        """Generate stratified sample for manual verification"""
        print("\n" + "="*70)
        print("GENERATING STRATIFIED SAMPLE")
        print("="*70)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        samples = []

        # Sample 1: Recent dual-use patents (5)
        print("\n[1/5] Sampling recent dual-use patents...")
        cursor.execute('''
            SELECT
                patent_id,
                publication_number,
                applicant_name,
                applicant_country,
                title,
                filing_date,
                publication_date,
                ipc_classifications,
                technology_domain,
                risk_score,
                has_dual_use
            FROM epo_patents
            WHERE has_dual_use = 1
            ORDER BY filing_date DESC
            LIMIT 5
        ''')
        for row in cursor.fetchall():
            samples.append({
                'sample_category': 'Recent Dual-Use',
                'patent_id': row[0],
                'publication_number': row[1],
                'applicant_name': row[2],
                'applicant_country': row[3],
                'title': row[4],
                'filing_date': row[5],
                'publication_date': row[6],
                'ipc_classifications': row[7],
                'technology_domain': row[8],
                'risk_score': row[9],
                'has_dual_use': bool(row[10])
            })
        print(f"   Found {len([s for s in samples if s['sample_category'] == 'Recent Dual-Use'])} patents")

        # Sample 2: Historical dual-use patents (5)
        print("[2/5] Sampling historical dual-use patents...")
        cursor.execute('''
            SELECT
                patent_id,
                publication_number,
                applicant_name,
                applicant_country,
                title,
                filing_date,
                publication_date,
                ipc_classifications,
                technology_domain,
                risk_score,
                has_dual_use
            FROM epo_patents
            WHERE has_dual_use = 1
            ORDER BY filing_date ASC
            LIMIT 5
        ''')
        for row in cursor.fetchall():
            samples.append({
                'sample_category': 'Historical Dual-Use',
                'patent_id': row[0],
                'publication_number': row[1],
                'applicant_name': row[2],
                'applicant_country': row[3],
                'title': row[4],
                'filing_date': row[5],
                'publication_date': row[6],
                'ipc_classifications': row[7],
                'technology_domain': row[8],
                'risk_score': row[9],
                'has_dual_use': bool(row[10])
            })
        print(f"   Found {len([s for s in samples if s['sample_category'] == 'Historical Dual-Use'])} patents")

        # Sample 3: High risk score patents (5)
        print("[3/5] Sampling high risk score patents...")
        cursor.execute('''
            SELECT
                patent_id,
                publication_number,
                applicant_name,
                applicant_country,
                title,
                filing_date,
                publication_date,
                ipc_classifications,
                technology_domain,
                risk_score,
                has_dual_use
            FROM epo_patents
            WHERE risk_score IS NOT NULL
            ORDER BY risk_score DESC
            LIMIT 5
        ''')
        for row in cursor.fetchall():
            samples.append({
                'sample_category': 'High Risk Score',
                'patent_id': row[0],
                'publication_number': row[1],
                'applicant_name': row[2],
                'applicant_country': row[3],
                'title': row[4],
                'filing_date': row[5],
                'publication_date': row[6],
                'ipc_classifications': row[7],
                'technology_domain': row[8],
                'risk_score': row[9],
                'has_dual_use': bool(row[10])
            })
        print(f"   Found {len([s for s in samples if s['sample_category'] == 'High Risk Score'])} patents")

        # Sample 4: Major Chinese companies (5)
        print("[4/5] Sampling major Chinese company patents...")
        major_companies = ['Huawei', 'ZTE', 'Xiaomi', 'OPPO', 'BOE']
        for company in major_companies:
            cursor.execute('''
                SELECT
                    patent_id,
                    publication_number,
                    applicant_name,
                    applicant_country,
                    title,
                    filing_date,
                    publication_date,
                    ipc_classifications,
                    technology_domain,
                    risk_score,
                    has_dual_use
                FROM epo_patents
                WHERE applicant_name LIKE ?
                ORDER BY filing_date DESC
                LIMIT 1
            ''', (f'%{company}%',))
            row = cursor.fetchone()
            if row:
                samples.append({
                    'sample_category': 'Major Chinese Company',
                    'patent_id': row[0],
                    'publication_number': row[1],
                    'applicant_name': row[2],
                    'applicant_country': row[3],
                    'title': row[4],
                    'filing_date': row[5],
                    'publication_date': row[6],
                    'ipc_classifications': row[7],
                    'technology_domain': row[8],
                    'risk_score': row[9],
                    'has_dual_use': bool(row[10])
                })
        print(f"   Found {len([s for s in samples if s['sample_category'] == 'Major Chinese Company'])} patents")

        # Sample 5: Random non-dual-use (5)
        print("[5/5] Sampling random non-dual-use patents...")
        cursor.execute('''
            SELECT
                patent_id,
                publication_number,
                applicant_name,
                applicant_country,
                title,
                filing_date,
                publication_date,
                ipc_classifications,
                technology_domain,
                risk_score,
                has_dual_use
            FROM epo_patents
            WHERE has_dual_use = 0 OR has_dual_use IS NULL
            ORDER BY RANDOM()
            LIMIT 5
        ''')
        for row in cursor.fetchall():
            samples.append({
                'sample_category': 'Random Non-Dual-Use',
                'patent_id': row[0],
                'publication_number': row[1],
                'applicant_name': row[2],
                'applicant_country': row[3],
                'title': row[4],
                'filing_date': row[5],
                'publication_date': row[6],
                'ipc_classifications': row[7],
                'technology_domain': row[8],
                'risk_score': row[9],
                'has_dual_use': bool(row[10])
            })
        print(f"   Found {len([s for s in samples if s['sample_category'] == 'Random Non-Dual-Use'])} patents")

        conn.close()

        print(f"\n[OK] Total sample size: {len(samples)} patents")
        return samples

    def save_sample(self, samples):
        """Save sample to JSON file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = self.output_dir / f'epo_patents_validation_sample_{timestamp}.json'

        output = {
            'validation_metadata': {
                'generated_timestamp': timestamp,
                'database_path': str(self.db_path),
                'total_sample_size': len(samples),
                'sample_categories': {
                    'Recent Dual-Use': len([s for s in samples if s['sample_category'] == 'Recent Dual-Use']),
                    'Historical Dual-Use': len([s for s in samples if s['sample_category'] == 'Historical Dual-Use']),
                    'High Risk Score': len([s for s in samples if s['sample_category'] == 'High Risk Score']),
                    'Major Chinese Company': len([s for s in samples if s['sample_category'] == 'Major Chinese Company']),
                    'Random Non-Dual-Use': len([s for s in samples if s['sample_category'] == 'Random Non-Dual-Use'])
                }
            },
            'validation_protocol': {
                'for_each_patent': [
                    '1. Search EPO website for publication number',
                    '2. Verify patent exists in EPO database',
                    '3. Verify applicant name matches Chinese entity',
                    '4. Verify filing date is plausible',
                    '5. Assess if dual-use classification is accurate',
                    '6. Categorize as: VERIFIED, FALSE POSITIVE, MISCATEGORIZED, or UNABLE TO VERIFY'
                ],
                'epo_search_url': 'https://worldwide.espacenet.com/',
                'search_format': 'Enter publication number in search box'
            },
            'samples': samples
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print(f"\n[OK] Sample saved: {output_file}")
        return output_file

    def generate_verification_template(self, samples):
        """Generate markdown template for manual verification"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = self.output_dir / f'epo_patents_manual_review_{timestamp}.md'

        content = f"""# EPO Patents Manual Verification
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Database**: {self.db_path}
**Sample Size**: {len(samples)} patents

## Verification Protocol

For each patent below:
1. Search [EPO Espacenet](https://worldwide.espacenet.com/) for the publication number
2. Verify patent exists in EPO database
3. Verify applicant is actually a Chinese entity
4. Verify filing date is plausible
5. Assess if dual-use classification is accurate
6. Categorize as:
   - **VERIFIED**: Real Chinese patent, correctly classified
   - **FALSE POSITIVE**: Not a Chinese entity, or doesn't exist
   - **MISCATEGORIZED**: Real patent, wrong dual-use classification
   - **UNABLE TO VERIFY**: Can't find sufficient information

---

"""

        for i, sample in enumerate(samples, 1):
            content += f"""## Patent {i}: {sample['publication_number']}

**Category**: {sample['sample_category']}
**Applicant**: {sample['applicant_name']}
**Country**: {sample['applicant_country']}
**Title**: {sample['title']}
**Filing Date**: {sample['filing_date']}
**Publication Date**: {sample['publication_date']}
**IPC Classifications**: {sample['ipc_classifications']}
**Technology Domain**: {sample['technology_domain']}
**Risk Score**: {sample['risk_score']}
**Dual-Use Flagged**: {sample['has_dual_use']}

**Search URL**: https://worldwide.espacenet.com/patent/search?q=pn%3D{sample['publication_number']}

**Verification Result**:
- [ ] VERIFIED
- [ ] FALSE POSITIVE
- [ ] MISCATEGORIZED
- [ ] UNABLE TO VERIFY

**Notes**:
```
[Add notes from manual verification here]
```

---

"""

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"[OK] Verification template saved: {output_file}")
        return output_file

    def run(self):
        """Run complete validation"""
        print("\n" + "="*70)
        print("EPO PATENTS VALIDATION")
        print("="*70)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Step 1: Database overview
        self.get_database_overview()

        # Step 2: Generate stratified sample
        samples = self.generate_stratified_sample()

        # Step 3: Save sample to JSON
        json_file = self.save_sample(samples)

        # Step 4: Generate markdown verification template
        md_file = self.generate_verification_template(samples)

        print("\n" + "="*70)
        print("VALIDATION PREPARATION COMPLETE")
        print("="*70)
        print(f"\nJSON sample: {json_file}")
        print(f"Markdown template: {md_file}")
        print(f"\nTotal patents to verify: {len(samples)}")
        print("\nNext steps:")
        print("  1. Open the markdown file")
        print("  2. For each patent, search EPO Espacenet")
        print("  3. Verify applicant, dates, and classifications")
        print("  4. Record findings in markdown file")
        print("="*70)

if __name__ == '__main__':
    validator = EPOPatentsValidator()
    validator.run()

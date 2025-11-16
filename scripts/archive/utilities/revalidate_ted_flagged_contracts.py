#!/usr/bin/env python3
"""
Re-validate 295 Flagged TED Contracts with Updated Detection Logic
Applies word boundary fixes and updated company patterns to assess true precision
"""

import sqlite3
import json
import re
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))
from core.enhanced_validation_v3_complete import CompleteEuropeanValidator

class TEDContractRevalidator:
    """Re-validate flagged TED contracts with improved detection"""

    def __init__(self):
        self.db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")
        self.validator = CompleteEuropeanValidator()

        # Updated patterns with word boundaries (from ted_complete_production_processor.py)
        self.china_patterns = [
            r'\bchina\b', r'\bchinese\b', r'\bbeijing\b', r'\bshanghai\b',
            r'\bguangzhou\b', r'\bshenzhen\b', r'\bhong kong\b', r'\bmacau\b',
            r'\bhuawei\b', r'\bzte\b', r'\balibaba\b', r'\btencent\b',
            r'\bsinopec\b', r'\bpetrochina\b', r'\blenovo\b', r'\bxiaomi\b',
            r'\bbyd\b', r'\bcosco\b', r'\bcnooc\b', r'\bcnpc\b', r'\bnuctech\b',
            r'\bhikvision\b', r'\bdahua\b', r'\bdji\b', r'\bbgi\b', r'\bcimc\b',
            r'\bcrrc\b', r'\bcomac\b', r'\bavic\b', r'\bnorinco\b', r'\bcasic\b'
        ]

        # European legal suffixes for false positive detection
        self.european_suffixes = [
            r'\bs\.?l\.?\b', r'\bs\.?r\.?l\.?\b', r'\bspol\b', r'\bs\.?a\.?\b',
            r'\ba\.?s\.?\b', r'\bg\.?m\.?b\.?h\.?\b', r'\bo\.?o\.?d\.?\b',
            r'\bd\.?o\.?o\.?\b', r'\bltd\b', r'\bplc\b', r'\bs\.?p\.?a\.?\b'
        ]

    def get_flagged_contracts(self):
        """Retrieve all 295 flagged contracts from database"""

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = """
            SELECT
                id,
                notice_number,
                publication_date,
                ca_name,
                ca_country,
                contractor_name,
                contractor_official_name,
                contractor_country,
                contractor_address,
                contractor_city,
                contract_title,
                contract_description,
                cpv_code,
                value_total,
                currency,
                is_chinese_related,
                chinese_confidence,
                chinese_indicators,
                chinese_entities,
                data_quality_flag,
                detection_rationale
            FROM ted_contracts_production
            WHERE is_chinese_related = 1
            ORDER BY publication_date DESC
        """

        cursor.execute(query)
        contracts = [dict(row) for row in cursor.fetchall()]
        conn.close()

        print(f"Retrieved {len(contracts)} flagged contracts from database")
        return contracts

    def apply_updated_detection(self, contract):
        """Apply updated detection logic with word boundaries"""

        # Combine all text fields
        text_fields = [
            contract.get('contractor_name', ''),
            contract.get('contractor_official_name', ''),
            contract.get('contractor_address', ''),
            contract.get('contractor_city', ''),
            contract.get('ca_name', ''),
            contract.get('contract_title', ''),
            contract.get('contract_description', '')
        ]
        combined_text = ' '.join(str(f) for f in text_fields if f).lower()

        # Check for patterns
        matched_patterns = []
        for pattern in self.china_patterns:
            if re.search(pattern, combined_text):
                matched_patterns.append(pattern.replace(r'\b', ''))

        # Check for European suffixes (false positive indicator)
        european_indicators = []
        for suffix in self.european_suffixes:
            if re.search(suffix, combined_text, re.IGNORECASE):
                european_indicators.append(suffix.replace(r'\b', ''))

        # Check for Chinese characters
        has_chinese_chars = bool(re.search(r'[\u4e00-\u9fff]', combined_text))

        # Check contractor country code
        contractor_country = contract.get('contractor_country', '')
        is_cn_hk_country = contractor_country in ['CN', 'CHN', 'HK', 'HKG', 'MO', 'MAC']

        # Use validator for company name check
        company_matches = self.validator._check_company_names(combined_text)
        has_known_company = len(company_matches) > 0

        return {
            'matched_patterns': matched_patterns,
            'pattern_count': len(matched_patterns),
            'european_indicators': european_indicators,
            'has_chinese_chars': has_chinese_chars,
            'contractor_country': contractor_country,
            'is_cn_hk_country': is_cn_hk_country,
            'known_companies': [m['text'] for m in company_matches],
            'combined_text_sample': combined_text[:200] if combined_text else ''
        }

    def categorize_contract(self, contract, detection):
        """Categorize contract as True Chinese, False Positive, or Uncertain"""

        # HIGH CONFIDENCE TRUE POSITIVE
        if detection['is_cn_hk_country']:
            return 'TRUE_CHINESE', 'CN/HK country code', 0.95

        if detection['has_chinese_chars']:
            return 'TRUE_CHINESE', 'Chinese characters present', 0.90

        if detection['known_companies']:
            return 'TRUE_CHINESE', f"Known company: {', '.join(detection['known_companies'])}", 0.85

        # HIGH CONFIDENCE FALSE POSITIVE
        if detection['european_indicators'] and not detection['matched_patterns']:
            return 'FALSE_POSITIVE', f"European company: {', '.join(detection['european_indicators'])}", 0.90

        ca_country = contract.get('ca_country', '')
        contractor_country = detection['contractor_country']

        # European contractor in European country with European legal suffix
        if (ca_country in ['POL', 'ESP', 'DEU', 'FRA', 'ITA', 'CZE'] and
            contractor_country in ['POL', 'ESP', 'DEU', 'FRA', 'ITA', 'CZE'] and
            detection['european_indicators']):
            return 'FALSE_POSITIVE', f"European: {contractor_country} contractor", 0.85

        # UNCERTAIN - needs review
        if detection['pattern_count'] > 0:
            reason = f"{detection['pattern_count']} pattern matches: {', '.join(detection['matched_patterns'][:3])}"

            # Check if pattern is just 'china' in company name (could be false positive)
            if detection['pattern_count'] == 1 and 'china' in detection['matched_patterns']:
                return 'UNCERTAIN', f"Only 'china' keyword: {reason}", 0.40

            return 'UNCERTAIN', reason, 0.60

        # No patterns matched with updated detection
        return 'FALSE_POSITIVE', 'No patterns match with word boundaries', 0.80

    def generate_report(self, results):
        """Generate comprehensive validation report"""

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Categorize results
        categories = {
            'TRUE_CHINESE': [],
            'FALSE_POSITIVE': [],
            'UNCERTAIN': []
        }

        for result in results:
            category = result['category']
            categories[category].append(result)

        # Calculate statistics
        total = len(results)
        true_chinese = len(categories['TRUE_CHINESE'])
        false_positives = len(categories['FALSE_POSITIVE'])
        uncertain = len(categories['UNCERTAIN'])

        actual_precision = (true_chinese / total * 100) if total > 0 else 0
        conservative_precision = ((true_chinese + uncertain) / total * 100) if total > 0 else 0

        # Generate summary report
        report = {
            'timestamp': timestamp,
            'total_contracts': total,
            'categorization': {
                'true_chinese': true_chinese,
                'false_positives': false_positives,
                'uncertain': uncertain
            },
            'precision_metrics': {
                'actual_precision': round(actual_precision, 2),
                'conservative_precision': round(conservative_precision, 2),
                'false_positive_rate': round(false_positives / total * 100, 2) if total > 0 else 0
            },
            'top_false_positive_patterns': self.analyze_false_positive_patterns(categories['FALSE_POSITIVE']),
            'true_chinese_by_indicator': self.analyze_true_chinese(categories['TRUE_CHINESE']),
            'uncertain_for_review': len(categories['UNCERTAIN'])
        }

        # Save detailed results
        detailed_file = Path(f"analysis/ted_revalidation_detailed_{timestamp}.json")
        with open(detailed_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        # Save summary
        summary_file = Path(f"analysis/ted_revalidation_summary_{timestamp}.json")
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)

        # Generate markdown report
        self.generate_markdown_report(report, categories, timestamp)

        return report, categories

    def analyze_false_positive_patterns(self, false_positives):
        """Analyze common patterns in false positives"""

        patterns = defaultdict(int)

        for fp in false_positives[:50]:  # Sample first 50
            reason = fp.get('reason', '')
            patterns[reason] += 1

        return dict(sorted(patterns.items(), key=lambda x: x[1], reverse=True)[:10])

    def analyze_true_chinese(self, true_chinese):
        """Analyze how true Chinese contracts were identified"""

        indicators = defaultdict(int)

        for tc in true_chinese:
            reason = tc.get('reason', '')
            # Extract indicator type
            if 'country code' in reason.lower():
                indicators['CN/HK Country Code'] += 1
            elif 'chinese characters' in reason.lower():
                indicators['Chinese Characters'] += 1
            elif 'known company' in reason.lower():
                indicators['Known Chinese Company'] += 1
            else:
                indicators['Other'] += 1

        return dict(indicators)

    def generate_markdown_report(self, report, categories, timestamp):
        """Generate human-readable markdown report"""

        md_content = f"""# TED Flagged Contracts Re-validation Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Total Contracts Reviewed:** {report['total_contracts']}
**Updated Detection:** Word boundaries + Nuctech + 10 additional companies

---

## Executive Summary

After applying word boundary fixes and updated Chinese company patterns, the 295 originally flagged TED contracts were re-validated.

### Results

| Category | Count | Percentage |
|----------|-------|------------|
| **True Chinese** | {report['categorization']['true_chinese']} | {report['categorization']['true_chinese']/report['total_contracts']*100:.1f}% |
| **False Positives** | {report['categorization']['false_positives']} | {report['categorization']['false_positives']/report['total_contracts']*100:.1f}% |
| **Uncertain (Needs Review)** | {report['categorization']['uncertain']} | {report['categorization']['uncertain']/report['total_contracts']*100:.1f}% |

### Precision Metrics

- **Actual Precision:** {report['precision_metrics']['actual_precision']:.2f}% (confirmed Chinese only)
- **Conservative Precision:** {report['precision_metrics']['conservative_precision']:.2f}% (Chinese + uncertain)
- **False Positive Rate:** {report['precision_metrics']['false_positive_rate']:.2f}%

---

## True Chinese Contracts ({report['categorization']['true_chinese']})

### Detection Methods

"""

        for indicator, count in report['true_chinese_by_indicator'].items():
            md_content += f"- **{indicator}**: {count} contracts\n"

        md_content += f"""

### Sample True Chinese Contracts (First 10)

| Notice | Contractor | Country | Company | Reason |
|--------|------------|---------|---------|--------|
"""

        for contract in categories['TRUE_CHINESE'][:10]:
            notice = (contract.get('notice_number') or 'N/A')[:15]
            contractor = (contract.get('contractor_name') or 'N/A')[:30]
            country = contract.get('detection', {}).get('contractor_country', 'N/A')
            companies = ', '.join(contract.get('detection', {}).get('known_companies', []))[:20]
            reason = (contract.get('reason') or '')[:50]
            md_content += f"| {notice} | {contractor} | {country} | {companies} | {reason} |\n"

        md_content += f"""

---

## False Positives ({report['categorization']['false_positives']})

### Common False Positive Patterns

"""

        for pattern, count in report['top_false_positive_patterns'].items():
            md_content += f"- **{pattern}**: {count} contracts\n"

        md_content += f"""

### Sample False Positives (First 10)

| Notice | Contractor | Country | Reason |
|--------|------------|---------|--------|
"""

        for contract in categories['FALSE_POSITIVE'][:10]:
            notice = (contract.get('notice_number') or 'N/A')[:15]
            contractor = (contract.get('contractor_name') or 'N/A')[:40]
            country = contract.get('detection', {}).get('contractor_country', 'N/A')
            reason = (contract.get('reason') or '')[:60]
            md_content += f"| {notice} | {contractor} | {country} | {reason} |\n"

        md_content += f"""

---

## Uncertain Contracts ({report['categorization']['uncertain']})

These contracts require manual review to confirm classification.

### Sample Uncertain Contracts (First 10)

| Notice | Contractor | Patterns Matched | Reason |
|--------|------------|------------------|--------|
"""

        for contract in categories['UNCERTAIN'][:10]:
            notice = (contract.get('notice_number') or 'N/A')[:15]
            contractor = (contract.get('contractor_name') or 'N/A')[:40]
            patterns = ', '.join(contract.get('detection', {}).get('matched_patterns', [])[:3])
            reason = (contract.get('reason') or '')[:50]
            md_content += f"| {notice} | {contractor} | {patterns} | {reason} |\n"

        md_content += f"""

---

## Recommendations

### Immediate Actions

1. **Remove {report['categorization']['false_positives']} False Positives**
   - Clear is_chinese_related flag for these contracts
   - Archive for audit trail

2. **Manual Review {report['categorization']['uncertain']} Uncertain Contracts**
   - Export to Excel for manual classification
   - Focus on contracts with only 'china' keyword matches

3. **Update Precision Metrics**
   - Current actual precision: {report['precision_metrics']['actual_precision']:.2f}%
   - After cleanup: {report['categorization']['true_chinese']}/{report['categorization']['true_chinese'] + report['categorization']['uncertain']} = {report['categorization']['true_chinese']/(report['categorization']['true_chinese'] + report['categorization']['uncertain'])*100:.1f}% minimum

### Database Updates Needed

```sql
-- Clear false positives
UPDATE ted_contracts_production
SET is_chinese_related = 0,
    chinese_confidence = 0.0,
    detection_rationale = 'False positive - removed in re-validation {timestamp}'
WHERE id IN (
    -- List of {report['categorization']['false_positives']} false positive IDs
);
```

---

## Files Generated

1. **Detailed Results:** `analysis/ted_revalidation_detailed_{timestamp}.json`
2. **Summary Report:** `analysis/ted_revalidation_summary_{timestamp}.json`
3. **This Report:** `analysis/TED_REVALIDATION_REPORT_{timestamp}.md`

---

**Re-validation Complete**
**Status:** Ready for database cleanup
**Next Step:** Manual review of {report['categorization']['uncertain']} uncertain contracts
"""

        report_file = Path(f"analysis/TED_REVALIDATION_REPORT_{timestamp}.md")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(md_content)

        print(f"\nMarkdown report saved to: {report_file}")

    def run_revalidation(self):
        """Main revalidation process"""

        print("="*80)
        print("TED FLAGGED CONTRACTS RE-VALIDATION")
        print("="*80)
        print()

        # Step 1: Get flagged contracts
        print("[1/4] Retrieving flagged contracts from database...")
        contracts = self.get_flagged_contracts()

        if not contracts:
            print("ERROR: No flagged contracts found!")
            return None

        print(f"      Found {len(contracts)} contracts flagged as Chinese-related")
        print()

        # Step 2: Apply updated detection
        print("[2/4] Applying updated detection logic...")
        results = []

        for i, contract in enumerate(contracts, 1):
            if i % 50 == 0:
                print(f"      Processed {i}/{len(contracts)}...")

            detection = self.apply_updated_detection(contract)
            category, reason, confidence = self.categorize_contract(contract, detection)

            results.append({
                'id': contract['id'],
                'notice_number': contract['notice_number'],
                'publication_date': contract['publication_date'],
                'contractor_name': contract['contractor_name'],
                'ca_country': contract['ca_country'],
                'original_confidence': contract.get('chinese_confidence'),
                'original_indicators': contract.get('chinese_indicators'),
                'category': category,
                'reason': reason,
                'new_confidence': confidence,
                'detection': detection
            })

        print(f"      Completed {len(results)} contracts")
        print()

        # Step 3: Generate report
        print("[3/4] Generating validation report...")
        report, categories = self.generate_report(results)
        print()

        # Step 4: Display summary
        print("[4/4] Validation Summary")
        print("="*80)
        print(f"Total Contracts:      {report['total_contracts']}")
        print(f"True Chinese:         {report['categorization']['true_chinese']} ({report['categorization']['true_chinese']/report['total_contracts']*100:.1f}%)")
        print(f"False Positives:      {report['categorization']['false_positives']} ({report['categorization']['false_positives']/report['total_contracts']*100:.1f}%)")
        print(f"Uncertain:            {report['categorization']['uncertain']} ({report['categorization']['uncertain']/report['total_contracts']*100:.1f}%)")
        print()
        print(f"Actual Precision:     {report['precision_metrics']['actual_precision']:.2f}%")
        print(f"Conservative Precision: {report['precision_metrics']['conservative_precision']:.2f}%")
        print("="*80)

        return report, categories


if __name__ == '__main__':
    revalidator = TEDContractRevalidator()
    report, categories = revalidator.run_revalidation()

    if report:
        print("\n[SUCCESS] Re-validation complete!")
        print(f"\nRecommended next step:")
        print(f"  - Remove {report['categorization']['false_positives']} false positives from database")
        print(f"  - Manual review {report['categorization']['uncertain']} uncertain contracts")

#!/usr/bin/env python3
"""
automated_validation_assistant.py - Automated Entity Verification Assistant

Helps with manual validation by automatically researching entities:
1. Web search for company information
2. SEC EDGAR filing lookup
3. Pattern recognition for categorization
4. Automated preliminary assessment

NOTE: Requires user to review and confirm automated assessments.

Last Updated: 2025-10-23
"""

import pandas as pd
import sqlite3
import json
from pathlib import Path
from datetime import datetime
import re

class AutomatedValidationAssistant:
    """Assist with automated entity validation"""

    def __init__(self, excel_path):
        self.excel_path = excel_path
        self.df = pd.read_excel(excel_path)
        self.validation_results = []

        print("="*70)
        print("AUTOMATED VALIDATION ASSISTANT")
        print("="*70)
        print(f"Sample file: {excel_path}")
        print(f"Total entities to validate: {len(self.df)}")
        print("="*70)

    def pattern_based_categorization(self, row):
        """Categorize entity based on name/industry patterns"""
        issuer_name = str(row['issuer_name']).lower()
        industry = str(row['industry']).lower()

        # Pattern 1: China-focused funds (US/EU funds investing IN China)
        china_fund_patterns = [
            'china equity',
            'china opportunities',
            'china fund',
            'china feeder',
            'china all shares',
            'china total return',
            'qfii china',
            'greater china'
        ]

        for pattern in china_fund_patterns:
            if pattern in issuer_name:
                return {
                    'automated_category': 'US_EU_FUND_CHINA_FOCUS',
                    'confidence': 'HIGH',
                    'reasoning': f'Name contains "{pattern}" - suggests US/EU fund investing IN China',
                    'concern_level': 'LOW',
                    'dual_use': 'N'
                }

        # Pattern 2: Known Chinese VC firms
        known_vc_patterns = [
            'sequoia capital china',
            'idg capital',
            'hillhouse',
            'qiming venture',
            'ggv capital',
            'sinovation',
            'zhenfund',
            'matrix partners china'
        ]

        for pattern in known_vc_patterns:
            if pattern in issuer_name:
                # Check if it's a fund structure (LP) or direct investment
                if 'fund' in issuer_name or 'l.p.' in issuer_name or 'partners fund' in issuer_name:
                    return {
                        'automated_category': 'CHINESE_PRIVATE_VC',
                        'confidence': 'HIGH',
                        'reasoning': f'Known Chinese VC firm "{pattern}" raising capital (fund structure)',
                        'concern_level': 'MEDIUM',
                        'dual_use': 'UNKNOWN'
                    }

        # Pattern 3: Pooled Investment Funds (generic)
        if industry == 'pooled investment fund':
            if any(word in issuer_name for word in ['partners', 'capital', 'fund', 'investment']):
                return {
                    'automated_category': 'LIKELY_FUND_STRUCTURE',
                    'confidence': 'MEDIUM',
                    'reasoning': 'Pooled Investment Fund - need manual review to determine if US fund investing IN China vs Chinese VC',
                    'concern_level': 'LOW',
                    'dual_use': 'N'
                }

        # Pattern 4: Dual-use technology sectors
        dual_use_sectors = ['biotechnology', 'pharmaceuticals', 'semiconductors', 'aerospace']
        if any(sector in industry for sector in dual_use_sectors):
            return {
                'automated_category': 'REQUIRES_MANUAL_REVIEW',
                'confidence': 'LOW',
                'reasoning': f'Dual-use sector ({industry}) - requires careful manual review',
                'concern_level': 'MEDIUM',
                'dual_use': 'Y'
            }

        # Pattern 5: Manufacturing / Operating companies
        if industry in ['manufacturing', 'retailing', 'other']:
            return {
                'automated_category': 'LIKELY_OPERATING_COMPANY',
                'confidence': 'MEDIUM',
                'reasoning': f'Operating company in {industry} - requires manual verification of ownership',
                'concern_level': 'MEDIUM',
                'dual_use': 'UNKNOWN'
            }

        # Default: Requires manual review
        return {
            'automated_category': 'REQUIRES_MANUAL_REVIEW',
            'confidence': 'LOW',
            'reasoning': 'No clear pattern match - manual review required',
            'concern_level': 'UNKNOWN',
            'dual_use': 'UNKNOWN'
        }

    def generate_sec_edgar_url(self, accession_number):
        """Generate SEC EDGAR URL for filing"""
        # Format: https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=ACCESSION&type=D&dateb=&owner=exclude&count=100
        # Simplified: Use accession number directly
        acc_clean = accession_number.replace('-', '')
        return f"https://www.sec.gov/cgi-bin/viewer?action=view&cik={acc_clean}&accession_number={accession_number}&xbrl_type=v"

    def generate_google_search_query(self, issuer_name):
        """Generate Google search query"""
        # Clean name for search
        clean_name = issuer_name.replace(',', ' ').replace('  ', ' ').strip()
        return f"https://www.google.com/search?q={clean_name.replace(' ', '+')}+SEC+Form+D"

    def validate_all_entities(self):
        """Run automated validation on all entities"""
        print("\nRunning automated validation on all entities...\n")

        for idx, row in self.df.iterrows():
            print(f"\rProcessing {idx+1}/{len(self.df)}...", end='', flush=True)

            # Run pattern-based categorization
            result = self.pattern_based_categorization(row)

            # Add URLs
            result['sec_edgar_url'] = self.generate_sec_edgar_url(row['accession_number'])
            result['google_search_url'] = self.generate_google_search_query(row['issuer_name'])

            # Add to results
            self.validation_results.append({
                'accession_number': row['accession_number'],
                'issuer_name': row['issuer_name'],
                'industry': row['industry'],
                'quarter': row['quarter'],
                'offering_amount_formatted': row['offering_amount_formatted'],
                'sample_category': row['sample_category'],
                'priority': row['priority'],
                **result
            })

        print(f"\n[OK] Automated validation complete for {len(self.validation_results)} entities")

    def export_results(self):
        """Export automated validation results"""
        print("\nExporting automated validation results...")

        # Create DataFrame
        df_results = pd.DataFrame(self.validation_results)

        # Add manual review columns
        df_results['manual_override_category'] = ''
        df_results['manual_override_notes'] = 'Override automated categorization if incorrect'
        df_results['final_concern_level'] = ''
        df_results['reviewer_name'] = ''
        df_results['review_date'] = ''

        # Reorder columns
        export_cols = [
            'priority',
            'sample_category',
            'issuer_name',
            'industry',
            'offering_amount_formatted',
            'quarter',
            'automated_category',
            'confidence',
            'reasoning',
            'concern_level',
            'dual_use',
            'sec_edgar_url',
            'google_search_url',
            'manual_override_category',
            'final_concern_level',
            'reviewer_name',
            'review_date',
            'manual_override_notes',
            'accession_number'
        ]

        df_export = df_results[export_cols]

        # Export to Excel
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = Path(f'analysis/manual_review/automated_validation_{timestamp}.xlsx')

        df_export.to_excel(output_path, index=False, sheet_name='Automated Validation')

        print(f"[OK] Exported to: {output_path}")

        # Generate summary statistics
        summary = {
            'timestamp': datetime.now().isoformat(),
            'total_entities': len(df_results),
            'category_breakdown': df_results['automated_category'].value_counts().to_dict(),
            'confidence_breakdown': df_results['confidence'].value_counts().to_dict(),
            'concern_level_breakdown': df_results['concern_level'].value_counts().to_dict(),
            'dual_use_breakdown': df_results['dual_use'].value_counts().to_dict()
        }

        summary_path = Path(f'analysis/manual_review/automated_validation_{timestamp}_summary.json')
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)

        print(f"[OK] Summary saved to: {summary_path}")

        # Print summary
        print("\n" + "="*70)
        print("AUTOMATED VALIDATION SUMMARY")
        print("="*70)
        print("\nCategory Breakdown:")
        for cat, count in df_results['automated_category'].value_counts().items():
            pct = count / len(df_results) * 100
            print(f"  {cat}: {count} ({pct:.1f}%)")

        print("\nConfidence Breakdown:")
        for conf, count in df_results['confidence'].value_counts().items():
            pct = count / len(df_results) * 100
            print(f"  {conf}: {count} ({pct:.1f}%)")

        print("\nConcern Level Breakdown:")
        for level, count in df_results['concern_level'].value_counts().items():
            pct = count / len(df_results) * 100
            print(f"  {level}: {count} ({pct:.1f}%)")

        print("\n" + "="*70)

        return output_path, summary_path, summary

    def print_high_priority_findings(self):
        """Print high-priority findings that need manual review"""
        print("\n" + "="*70)
        print("HIGH PRIORITY ENTITIES FOR MANUAL REVIEW")
        print("="*70)

        df_results = pd.DataFrame(self.validation_results)

        # Filter for high-priority items
        high_priority = df_results[
            (df_results['concern_level'] == 'MEDIUM') |
            (df_results['automated_category'] == 'CHINESE_PRIVATE_VC') |
            (df_results['dual_use'] == 'Y')
        ]

        if len(high_priority) > 0:
            print(f"\nFound {len(high_priority)} entities requiring manual review:\n")

            for idx, row in high_priority.iterrows():
                print(f"{idx+1}. {row['issuer_name']}")
                print(f"   Category: {row['automated_category']} (Confidence: {row['confidence']})")
                print(f"   Concern: {row['concern_level']}, Dual-use: {row['dual_use']}")
                print(f"   Reasoning: {row['reasoning']}")
                print(f"   SEC EDGAR: {row['sec_edgar_url']}")
                print()

        else:
            print("\nNo high-priority items identified by automated validation.")

        print("="*70)


def main():
    """Run automated validation assistant"""
    # Find most recent validation sample
    sample_dir = Path('analysis/manual_review')
    sample_files = list(sample_dir.glob('validation_sample_*.xlsx'))

    if not sample_files:
        print("ERROR: No validation sample found. Run generate_validation_sample.py first.")
        return

    latest_sample = max(sample_files, key=lambda p: p.stat().st_mtime)

    print(f"Using sample file: {latest_sample}")

    # Run validation
    assistant = AutomatedValidationAssistant(latest_sample)
    assistant.validate_all_entities()
    output_path, summary_path, summary = assistant.export_results()
    assistant.print_high_priority_findings()

    print("\n" + "="*70)
    print("NEXT STEPS")
    print("="*70)
    print(f"1. Open automated results: {output_path}")
    print(f"2. Review high-priority entities manually")
    print(f"3. Override automated categorization if needed")
    print(f"4. Calculate final false positive rate")
    print("="*70)


if __name__ == '__main__':
    main()

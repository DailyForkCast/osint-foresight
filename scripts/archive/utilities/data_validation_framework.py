#!/usr/bin/env python3
"""
Data Validation Framework
Validate all extracted BigQuery datasets for completeness, accuracy, and consistency
"""

import pandas as pd
from pathlib import Path
import json
from datetime import datetime

class DataValidator:
    def __init__(self):
        self.data_dir = Path("data/bigquery_comprehensive")
        self.cnipa_dir = Path("data/cnipa_comprehensive")
        self.validation_results = []

    def validate_file_exists(self, filename):
        """Check if file exists and is readable"""
        filepath = self.data_dir / filename
        if not filepath.exists():
            return False, f"File not found: {filename}"

        try:
            if filename.endswith('.csv'):
                df = pd.read_csv(filepath)
                return True, f"File OK: {len(df):,} records"
            elif filename.endswith('.json'):
                with open(filepath) as f:
                    data = json.load(f)
                return True, f"File OK: {len(data)} items"
        except Exception as e:
            return False, f"Error reading {filename}: {e}"

    def validate_patents_data(self):
        """Validate patent datasets"""
        print("\n" + "="*80)
        print("VALIDATING PATENT DATASETS")
        print("="*80)

        datasets = {
            'assignees': 'patent_assignees_annual.csv',
            'citations': 'patent_citations_annual.csv',
            'inventors': 'patent_inventors_annual.csv',
            'families': 'patent_families_annual.csv'
        }

        results = {}

        for name, filename in datasets.items():
            print(f"\n[{name.upper()}]")

            exists, msg = self.validate_file_exists(filename)
            print(f"  File check: {msg}")

            if exists:
                df = pd.read_csv(self.data_dir / filename)

                # Check for nulls
                null_counts = df.isnull().sum()
                if null_counts.sum() > 0:
                    print(f"  WARNING: {null_counts.sum()} null values found")
                    for col in null_counts[null_counts > 0].index:
                        print(f"    - {col}: {null_counts[col]} nulls")
                else:
                    print(f"  Nulls: None (clean data)")

                # Check year coverage
                if 'year' in df.columns:
                    years = sorted(df['year'].unique())
                    print(f"  Years: {years[0]}-{years[-1]} ({len(years)} years)")

                    # Check for gaps
                    expected_years = set(range(years[0], years[-1] + 1))
                    actual_years = set(years)
                    missing_years = expected_years - actual_years

                    if missing_years:
                        print(f"  WARNING: Missing years: {sorted(missing_years)}")
                    else:
                        print(f"  Year coverage: Complete")

                # Dataset-specific validation
                if name == 'assignees':
                    print(f"  Unique assignees: {df['assignee_name'].nunique():,}")
                    print(f"  Total patent records: {df['patent_count'].sum():,}")

                elif name == 'citations':
                    print(f"  Total citations: {df['total_citations'].sum():,}")
                    avg_cite = df['avg_citations_per_patent'].mean()
                    print(f"  Avg citations/patent: {avg_cite:.2f}")

                elif name == 'inventors':
                    print(f"  Total unique inventors: {df['unique_inventors'].sum():,}")
                    avg_collab = df['collaboration_rate_pct'].mean()
                    print(f"  Avg collaboration rate: {avg_collab:.1f}%")

                elif name == 'families':
                    print(f"  Total patent families: {df['unique_families'].sum():,}")
                    avg_intl = df['international_filing_rate_pct'].mean()
                    print(f"  Avg intl filing rate: {avg_intl:.1f}%")

                results[name] = {'status': 'PASS', 'records': len(df)}
            else:
                results[name] = {'status': 'FAIL', 'error': msg}

        return results

    def validate_github_data(self):
        """Validate GitHub datasets"""
        print("\n" + "="*80)
        print("VALIDATING GITHUB DATASETS")
        print("="*80)

        # Check 2024 data (already extracted)
        print("\n[GITHUB 2024]")
        exists, msg = self.validate_file_exists('github_chinese_companies_2024.csv')
        print(f"  File check: {msg}")

        results = {}

        if exists:
            df = pd.read_csv(self.data_dir / 'github_chinese_companies_2024.csv')

            print(f"  Records: {len(df):,}")
            print(f"  Unique repos: {df['repo_name'].nunique():,}")
            print(f"  Event types: {df['event_type'].nunique()}")
            print(f"  Months: {sorted(df['month'].unique())}")

            # Check for unexpected values
            if df['event_count'].min() < 0:
                print(f"  WARNING: Negative event counts found")

            results['2024'] = {'status': 'PASS', 'records': len(df)}
        else:
            results['2024'] = {'status': 'FAIL', 'error': msg}

        # Check full history (if available)
        print("\n[GITHUB FULL HISTORY]")
        full_history_file = 'github_chinese_companies_full_history.csv'

        if (self.data_dir / full_history_file).exists():
            df_full = pd.read_csv(self.data_dir / full_history_file)

            print(f"  Records: {len(df_full):,}")
            print(f"  Unique repos: {df_full['repo_name'].nunique():,}")
            print(f"  Unique months: {df_full['month'].nunique()}")

            # Extract years from months
            df_full['year'] = df_full['month'].astype(str).str[:4].astype(int)
            years = sorted(df_full['year'].unique())
            print(f"  Year range: {years[0]}-{years[-1]}")

            results['full_history'] = {'status': 'PASS', 'records': len(df_full)}
        else:
            print(f"  Status: Extraction in progress or not started")
            results['full_history'] = {'status': 'PENDING'}

        return results

    def validate_world_bank_data(self):
        """Validate World Bank datasets"""
        print("\n" + "="*80)
        print("VALIDATING WORLD BANK DATASETS")
        print("="*80)

        results = {}

        # Check comprehensive indicators
        print("\n[WORLD BANK COMPREHENSIVE]")
        exists, msg = self.validate_file_exists('world_bank_china_comprehensive.csv')
        print(f"  File check: {msg}")

        if exists:
            df = pd.read_csv(self.data_dir / 'world_bank_china_comprehensive.csv')

            print(f"  Records: {len(df):,}")
            print(f"  Unique indicators: {df['indicator_code'].nunique()}")
            print(f"  Year range: {df['year'].min()}-{df['year'].max()}")

            # Check indicator coverage
            indicators_with_data = df.groupby('indicator_code').size()
            print(f"\n  Indicator coverage:")
            for ind_code, count in list(indicators_with_data.items())[:10]:
                ind_name = df[df['indicator_code'] == ind_code]['indicator_name'].iloc[0]
                print(f"    {ind_code}: {count} years")

            # Check for nulls in value column
            null_values = df['value'].isnull().sum()
            if null_values > 0:
                print(f"\n  WARNING: {null_values} null values in data")
            else:
                print(f"\n  Data quality: No nulls")

            results['comprehensive'] = {'status': 'PASS', 'records': len(df)}
        else:
            results['comprehensive'] = {'status': 'FAIL', 'error': msg}

        return results

    def validate_cnipa_data(self):
        """Validate CNIPA patent datasets"""
        print("\n" + "="*80)
        print("VALIDATING CNIPA DATASETS")
        print("="*80)

        if not self.cnipa_dir.exists():
            print("  CNIPA directory not found")
            return {'status': 'NOT_FOUND'}

        datasets = {
            'annual_filing': 'annual_filing_dates.csv',
            'annual_grant': 'annual_grant_dates.csv',
            'sector_filing': 'sector_annual_filing.csv',
            'sector_grant': 'sector_annual_grant.csv',
            'advanced_it': 'advanced_it_subcategories.csv'
        }

        results = {}

        for name, filename in datasets.items():
            filepath = self.cnipa_dir / filename
            print(f"\n[{name.upper()}]")

            if filepath.exists():
                df = pd.read_csv(filepath)
                print(f"  Records: {len(df):,}")

                if 'year' in df.columns:
                    years = sorted(df['year'].unique())
                    print(f"  Years: {years[0]}-{years[-1]}")

                if 'sector' in df.columns:
                    print(f"  Sectors: {df['sector'].nunique()}")

                if 'patent_count' in df.columns:
                    print(f"  Total patents: {df['patent_count'].sum():,}")

                results[name] = {'status': 'PASS', 'records': len(df)}
            else:
                print(f"  File not found: {filename}")
                results[name] = {'status': 'NOT_FOUND'}

        return results

    def validate_other_datasets(self):
        """Validate Stack Overflow, PyPI, Ethereum"""
        print("\n" + "="*80)
        print("VALIDATING OTHER DATASETS")
        print("="*80)

        datasets = {
            'stackoverflow': 'stackoverflow_technology_adoption.csv',
            'pypi': 'pypi_china_downloads.csv',
            'ethereum': 'ethereum_activity_sample.csv'
        }

        results = {}

        for name, filename in datasets.items():
            print(f"\n[{name.upper()}]")
            exists, msg = self.validate_file_exists(filename)
            print(f"  File check: {msg}")

            if exists:
                df = pd.read_csv(self.data_dir / filename)
                print(f"  Records: {len(df):,}")

                if 'year' in df.columns:
                    years = sorted(df['year'].unique())
                    print(f"  Years: {min(years)}-{max(years)}")

                results[name] = {'status': 'PASS', 'records': len(df)}
            else:
                results[name] = {'status': 'FAIL', 'error': msg}

        return results

    def generate_summary_report(self):
        """Generate overall validation summary"""
        print("\n" + "="*80)
        print("VALIDATION SUMMARY")
        print("="*80)

        patents = self.validate_patents_data()
        github = self.validate_github_data()
        world_bank = self.validate_world_bank_data()
        cnipa = self.validate_cnipa_data()
        other = self.validate_other_datasets()

        # Count statuses
        all_results = {**patents, **github, **world_bank, **cnipa, **other}

        pass_count = sum(1 for r in all_results.values() if r.get('status') == 'PASS')
        fail_count = sum(1 for r in all_results.values() if r.get('status') == 'FAIL')
        pending_count = sum(1 for r in all_results.values() if r.get('status') == 'PENDING')

        total_records = sum(r.get('records', 0) for r in all_results.values() if r.get('status') == 'PASS')

        print(f"\n[OVERALL STATUS]")
        print(f"  PASS: {pass_count}")
        print(f"  FAIL: {fail_count}")
        print(f"  PENDING: {pending_count}")
        print(f"  Total records validated: {total_records:,}")

        # Save report
        report = {
            'validation_date': datetime.now().isoformat(),
            'summary': {
                'pass': pass_count,
                'fail': fail_count,
                'pending': pending_count,
                'total_records': total_records
            },
            'datasets': {
                'patents': patents,
                'github': github,
                'world_bank': world_bank,
                'cnipa': cnipa,
                'other': other
            }
        }

        report_file = self.data_dir / 'validation_report.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\nValidation report saved: {report_file}")

        return report

def main():
    print("="*80)
    print("DATA VALIDATION FRAMEWORK")
    print("Comprehensive validation of all BigQuery extractions")
    print("="*80)

    validator = DataValidator()
    report = validator.generate_summary_report()

    print("\n" + "="*80)
    print("VALIDATION COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Comprehensive Data Quality Assessment
Validate, clean, and assess all extracted BigQuery datasets
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
from datetime import datetime
import sqlite3

class DataQualityAssessor:
    def __init__(self):
        self.bigquery_dir = Path("data/bigquery_comprehensive")
        self.cnipa_dir = Path("data/cnipa_comprehensive")
        self.issues = []
        self.stats = {}

    def assess_patent_assignees(self):
        """Assess patent assignees dataset"""
        print("\n" + "="*80)
        print("ASSESSING: Patent Assignees")
        print("="*80)

        df = pd.read_csv(self.bigquery_dir / 'patent_assignees_annual.csv')

        issues = []

        # Check for duplicates
        duplicates = df.duplicated(subset=['assignee_name', 'year']).sum()
        if duplicates > 0:
            issues.append(f"Found {duplicates} duplicate assignee-year combinations")
            print(f"  [!] Duplicates: {duplicates}")
        else:
            print(f"  [OK] No duplicates")

        # Check for anomalous patent counts
        mean_patents = df['patent_count'].mean()
        std_patents = df['patent_count'].std()
        outliers = df[df['patent_count'] > mean_patents + 3*std_patents]
        print(f"  [OK] Mean patents per assignee-year: {mean_patents:.1f}")
        print(f"  [OK] Outliers (>3 std): {len(outliers)} assignees")
        if len(outliers) > 0:
            print(f"    Top outliers:")
            for _, row in outliers.nlargest(5, 'patent_count').iterrows():
                print(f"      - {row['assignee_name'][:50]}: {row['patent_count']:,} patents ({row['year']})")

        # Check for empty/null names
        null_names = df['assignee_name'].isnull().sum()
        empty_names = (df['assignee_name'].str.strip() == '').sum()
        if null_names > 0 or empty_names > 0:
            issues.append(f"Null names: {null_names}, Empty names: {empty_names}")
            print(f"  [!] Null/empty names: {null_names + empty_names}")
        else:
            print(f"  [OK] All names valid")

        # Check year range
        year_range = f"{df['year'].min()}-{df['year'].max()}"
        print(f"  [OK] Year range: {year_range}")

        # Check for year gaps
        expected_years = set(range(df['year'].min(), df['year'].max() + 1))
        actual_years = set(df['year'].unique())
        missing_years = expected_years - actual_years
        if missing_years:
            issues.append(f"Missing years: {sorted(missing_years)}")
            print(f"  [!] Missing years: {sorted(missing_years)}")
        else:
            print(f"  [OK] Complete year coverage")

        # Data type validation
        print(f"  [OK] Data types: assignee_name={df['assignee_name'].dtype}, year={df['year'].dtype}, patent_count={df['patent_count'].dtype}")

        self.stats['patent_assignees'] = {
            'records': len(df),
            'unique_assignees': df['assignee_name'].nunique(),
            'year_range': year_range,
            'issues': issues
        }

        return df, issues

    def assess_github_full_history(self):
        """Assess GitHub full history dataset"""
        print("\n" + "="*80)
        print("ASSESSING: GitHub Full History")
        print("="*80)

        df = pd.read_csv(self.bigquery_dir / 'github_chinese_companies_full_history.csv')

        issues = []

        # Check for duplicates
        duplicates = df.duplicated(subset=['month', 'repo_name', 'event_type']).sum()
        if duplicates > 0:
            issues.append(f"Found {duplicates} duplicate records")
            print(f"  [!] Duplicates: {duplicates}")
        else:
            print(f"  [OK] No duplicates")

        # Check month format
        df['month_str'] = df['month'].astype(str)
        invalid_months = df[df['month_str'].str.len() != 6]
        if len(invalid_months) > 0:
            issues.append(f"Invalid month format: {len(invalid_months)} records")
            print(f"  [!] Invalid month format: {len(invalid_months)}")
        else:
            print(f"  [OK] All months valid format (YYYYMM)")

        # Extract year from month
        df['year'] = df['month_str'].str[:4].astype(int)
        df['month_num'] = df['month_str'].str[4:6].astype(int)

        # Check for invalid months (01-12)
        invalid_month_nums = df[(df['month_num'] < 1) | (df['month_num'] > 12)]
        if len(invalid_month_nums) > 0:
            issues.append(f"Invalid month numbers: {len(invalid_month_nums)}")
            print(f"  [!] Invalid month numbers: {len(invalid_month_nums)}")
        else:
            print(f"  [OK] All month numbers valid (1-12)")

        # Check event counts
        negative_counts = df[df['event_count'] < 0]
        if len(negative_counts) > 0:
            issues.append(f"Negative event counts: {len(negative_counts)}")
            print(f"  [!] Negative event counts: {len(negative_counts)}")
        else:
            print(f"  [OK] All event counts valid (non-negative)")

        # Check repo name format
        invalid_repos = df[~df['repo_name'].str.contains('/')]
        if len(invalid_repos) > 0:
            issues.append(f"Invalid repo names (no slash): {len(invalid_repos)}")
            print(f"  [!] Invalid repo names: {len(invalid_repos)}")
        else:
            print(f"  [OK] All repo names valid (org/repo format)")

        # Event type distribution
        print(f"\n  Event type distribution:")
        event_counts = df.groupby('event_type')['event_count'].sum().sort_values(ascending=False)
        for event_type, count in event_counts.head(10).items():
            print(f"    {event_type}: {count:,}")

        # Temporal analysis
        print(f"\n  Temporal coverage:")
        print(f"    First month: {df['month'].min()}")
        print(f"    Last month: {df['month'].max()}")
        print(f"    Total months: {df['month'].nunique()}")

        # Top repositories
        print(f"\n  Top repositories by activity:")
        top_repos = df.groupby('repo_name')['event_count'].sum().sort_values(ascending=False)
        for repo, count in top_repos.head(5).items():
            print(f"    {repo}: {count:,} events")

        self.stats['github_full_history'] = {
            'records': len(df),
            'unique_repos': df['repo_name'].nunique(),
            'unique_months': df['month'].nunique(),
            'event_types': df['event_type'].nunique(),
            'issues': issues
        }

        return df, issues

    def assess_world_bank(self):
        """Assess World Bank dataset"""
        print("\n" + "="*80)
        print("ASSESSING: World Bank Indicators")
        print("="*80)

        df = pd.read_csv(self.bigquery_dir / 'world_bank_china_comprehensive.csv')

        issues = []

        # Check for duplicates
        duplicates = df.duplicated(subset=['indicator_code', 'year']).sum()
        if duplicates > 0:
            issues.append(f"Found {duplicates} duplicate indicator-year combinations")
            print(f"  [!] Duplicates: {duplicates}")
        else:
            print(f"  [OK] No duplicates")

        # Check for null values
        null_values = df['value'].isnull().sum()
        if null_values > 0:
            issues.append(f"Null values: {null_values}")
            print(f"  [!] Null values: {null_values}")
        else:
            print(f"  [OK] No null values")

        # Check indicator coverage
        print(f"\n  Indicator coverage:")
        indicators = df.groupby('indicator_code').agg({
            'year': ['min', 'max', 'count'],
            'indicator_name': 'first'
        }).reset_index()

        for _, row in indicators.iterrows():
            code = row[('indicator_code', '')]
            name = row[('indicator_name', 'first')][:60]
            year_min = row[('year', 'min')]
            year_max = row[('year', 'max')]
            count = row[('year', 'count')]
            print(f"    [{code}] {name}")
            print(f"      {year_min}-{year_max} ({count} years)")

        # Check for data quality issues
        print(f"\n  Value range checks:")
        for indicator in df['indicator_code'].unique()[:5]:
            ind_data = df[df['indicator_code'] == indicator]
            print(f"    {indicator}: {ind_data['value'].min():.2f} - {ind_data['value'].max():.2f}")

        self.stats['world_bank'] = {
            'records': len(df),
            'indicators': df['indicator_code'].nunique(),
            'year_range': f"{df['year'].min()}-{df['year'].max()}",
            'issues': issues
        }

        return df, issues

    def assess_cnipa_datasets(self):
        """Assess all CNIPA datasets"""
        print("\n" + "="*80)
        print("ASSESSING: CNIPA Datasets")
        print("="*80)

        datasets = {
            'annual_filing': 'annual_filing_dates.csv',
            'annual_grant': 'annual_grant_dates.csv',
            'sector_filing': 'sector_annual_filing.csv',
            'sector_grant': 'sector_annual_grant.csv',
            'advanced_it': 'advanced_it_subcategories.csv'
        }

        all_issues = []

        for name, filename in datasets.items():
            print(f"\n  [{name.upper()}]")
            df = pd.read_csv(self.cnipa_dir / filename)

            issues = []

            # Check for duplicates based on key columns
            if 'sector' in df.columns:
                dup_cols = ['year', 'sector']
            elif 'subcategory' in df.columns:
                dup_cols = ['year', 'subcategory']
            else:
                dup_cols = ['year']

            duplicates = df.duplicated(subset=dup_cols).sum()
            if duplicates > 0:
                issues.append(f"{name}: {duplicates} duplicates")
                print(f"    [!] Duplicates: {duplicates}")
            else:
                print(f"    [OK] No duplicates")

            # Check for negative patent counts
            negative = df[df['patent_count'] < 0]
            if len(negative) > 0:
                issues.append(f"{name}: {len(negative)} negative counts")
                print(f"    [!] Negative counts: {len(negative)}")
            else:
                print(f"    [OK] All counts non-negative")

            # Check year range
            year_range = f"{df['year'].min()}-{df['year'].max()}"
            print(f"    [OK] Year range: {year_range}")

            all_issues.extend(issues)

            self.stats[f'cnipa_{name}'] = {
                'records': len(df),
                'year_range': year_range,
                'issues': issues
            }

        return all_issues

    def check_existing_database(self):
        """Check existing OSINT database structure"""
        print("\n" + "="*80)
        print("ASSESSING: Existing OSINT Database")
        print("="*80)

        db_path = Path("F:/OSINT_Consolidated.db")

        if not db_path.exists():
            print(f"  [!] Database not found at {db_path}")
            return None

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Get all table names
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
            tables = [row[0] for row in cursor.fetchall()]

            print(f"\n  Found {len(tables)} tables in database")
            print(f"\n  Tables:")

            db_schema = {}

            for table in tables:
                cursor.execute(f"PRAGMA table_info({table})")
                columns = cursor.fetchall()

                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                row_count = cursor.fetchone()[0]

                print(f"\n    [{table}] - {row_count:,} records")

                col_info = []
                for col in columns[:10]:  # Show first 10 columns
                    col_name = col[1]
                    col_type = col[2]
                    print(f"      - {col_name} ({col_type})")
                    col_info.append({'name': col_name, 'type': col_type})

                if len(columns) > 10:
                    print(f"      ... and {len(columns) - 10} more columns")

                db_schema[table] = {
                    'columns': len(columns),
                    'records': row_count,
                    'sample_columns': col_info
                }

            conn.close()

            self.stats['existing_database'] = db_schema
            return db_schema

        except Exception as e:
            print(f"  [!] Error accessing database: {e}")
            return None

    def generate_assessment_report(self):
        """Generate comprehensive assessment report"""
        print("\n" + "="*80)
        print("GENERATING ASSESSMENT REPORT")
        print("="*80)

        # Run all assessments
        assignees_df, assignees_issues = self.assess_patent_assignees()
        github_df, github_issues = self.assess_github_full_history()
        wb_df, wb_issues = self.assess_world_bank()
        cnipa_issues = self.assess_cnipa_datasets()
        db_schema = self.check_existing_database()

        # Compile report
        report = {
            'assessment_date': datetime.now().isoformat(),
            'datasets_assessed': len(self.stats),
            'total_issues_found': sum(len(v.get('issues', [])) for v in self.stats.values()),
            'statistics': self.stats,
            'all_issues': {
                'patent_assignees': assignees_issues,
                'github_full_history': github_issues,
                'world_bank': wb_issues,
                'cnipa': cnipa_issues
            }
        }

        # Save report
        output_file = self.bigquery_dir / 'data_quality_assessment_report.json'
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n\n" + "="*80)
        print("ASSESSMENT SUMMARY")
        print("="*80)
        print(f"\nDatasets assessed: {report['datasets_assessed']}")
        print(f"Total issues found: {report['total_issues_found']}")

        if report['total_issues_found'] == 0:
            print("\n[OK] All datasets passed quality assessment")
        else:
            print("\n[!] Issues found requiring attention:")
            for dataset, issues in report['all_issues'].items():
                if issues:
                    print(f"\n  {dataset}:")
                    for issue in issues:
                        print(f"    - {issue}")

        print(f"\nReport saved: {output_file}")

        return report

def main():
    print("="*80)
    print("DATA QUALITY ASSESSMENT")
    print("Comprehensive validation and cleaning of BigQuery datasets")
    print("="*80)

    assessor = DataQualityAssessor()
    report = assessor.generate_assessment_report()

    print("\n" + "="*80)
    print("ASSESSMENT COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()

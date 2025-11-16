#!/usr/bin/env python3
"""
Data Integration Assessment
Analyze existing databases, assess new BigQuery data, and create integration plan
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
from datetime import datetime
import sqlite3

class IntegrationAssessor:
    def __init__(self):
        self.bigquery_dir = Path("data/bigquery_comprehensive")
        self.cnipa_dir = Path("data/cnipa_comprehensive")
        self.osint_data_dir = Path("F:/OSINT_Data")
        self.integration_plan = {}

    def analyze_existing_databases(self):
        """Analyze all existing OSINT databases"""
        print("\n" + "="*80)
        print("ANALYZING EXISTING DATABASES")
        print("="*80)

        databases = {
            'openaire_production': self.osint_data_dir / 'openaire_production_comprehensive' / 'openaire_production.db',
            'uk_companies': self.osint_data_dir / 'CompaniesHouse_UK' / 'uk_companies_20251001.db',
            'usaspending': self.osint_data_dir / 'ARCHIVED_DATABASES_20251028_SUPERSEDED' / 'usaspending_fixed_detection.db',
            'openaire_comprehensive': self.osint_data_dir / 'openaire_comprehensive_20250921' / 'openaire_comprehensive.db',
        }

        db_inventory = {}

        for db_name, db_path in databases.items():
            if not db_path.exists():
                print(f"\n[{db_name.upper()}]")
                print(f"  [!] Not found: {db_path}")
                continue

            print(f"\n[{db_name.upper()}]")
            print(f"  Path: {db_path}")
            print(f"  Size: {db_path.stat().st_size / (1024**3):.2f} GB")

            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()

                # Get tables
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
                tables = [row[0] for row in cursor.fetchall()]

                print(f"  Tables: {len(tables)}")

                table_info = {}

                for table in tables:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        row_count = cursor.fetchone()[0]

                        cursor.execute(f"PRAGMA table_info({table})")
                        columns = cursor.fetchall()

                        print(f"    - {table}: {row_count:,} records, {len(columns)} columns")

                        table_info[table] = {
                            'records': row_count,
                            'columns': [col[1] for col in columns]
                        }

                    except Exception as e:
                        print(f"    - {table}: ERROR - {str(e)[:50]}")

                conn.close()

                db_inventory[db_name] = {
                    'path': str(db_path),
                    'size_gb': db_path.stat().st_size / (1024**3),
                    'tables': table_info
                }

            except Exception as e:
                print(f"  [!] Error accessing database: {str(e)[:100]}")

        return db_inventory

    def analyze_new_bigquery_data(self):
        """Analyze what new data we have from BigQuery"""
        print("\n" + "="*80)
        print("ANALYZING NEW BIGQUERY DATA")
        print("="*80)

        datasets = {
            'patent_assignees': self.bigquery_dir / 'patent_assignees_annual.csv',
            'patent_citations': self.bigquery_dir / 'patent_citations_annual.csv',
            'patent_inventors': self.bigquery_dir / 'patent_inventors_annual.csv',
            'patent_families': self.bigquery_dir / 'patent_families_annual.csv',
            'github_full_history': self.bigquery_dir / 'github_chinese_companies_full_history.csv',
            'github_2024': self.bigquery_dir / 'github_chinese_companies_2024.csv',
            'world_bank': self.bigquery_dir / 'world_bank_china_comprehensive.csv',
            'stackoverflow': self.bigquery_dir / 'stackoverflow_technology_adoption.csv',
            'pypi': self.bigquery_dir / 'pypi_china_downloads.csv',
            'ethereum': self.bigquery_dir / 'ethereum_activity_sample.csv',
        }

        cnipa_datasets = {
            'cnipa_annual_filing': self.cnipa_dir / 'annual_filing_dates.csv',
            'cnipa_annual_grant': self.cnipa_dir / 'annual_grant_dates.csv',
            'cnipa_sector_filing': self.cnipa_dir / 'sector_annual_filing.csv',
            'cnipa_sector_grant': self.cnipa_dir / 'sector_annual_grant.csv',
            'cnipa_advanced_it': self.cnipa_dir / 'advanced_it_subcategories.csv',
        }

        new_data_inventory = {}

        for name, filepath in {**datasets, **cnipa_datasets}.items():
            if not filepath.exists():
                print(f"\n[{name.upper()}]")
                print(f"  [!] Not found: {filepath}")
                continue

            df = pd.read_csv(filepath)

            print(f"\n[{name.upper()}]")
            print(f"  Records: {len(df):,}")
            print(f"  Columns: {', '.join(df.columns.tolist()[:10])}")
            if len(df.columns) > 10:
                print(f"           ... and {len(df.columns) - 10} more")

            # Sample data characteristics
            if 'year' in df.columns:
                print(f"  Year range: {df['year'].min()}-{df['year'].max()}")

            new_data_inventory[name] = {
                'records': len(df),
                'columns': df.columns.tolist(),
                'file_size_mb': filepath.stat().st_size / (1024**2)
            }

        return new_data_inventory

    def assess_data_overlap(self, db_inventory, new_data_inventory):
        """Assess overlap between existing and new data"""
        print("\n" + "="*80)
        print("ASSESSING DATA OVERLAP AND GAPS")
        print("="*80)

        overlaps = []
        gaps = []

        # Check for patent data overlap
        print("\n[PATENT DATA]")
        has_patent_db = any('patent' in db.lower() or 'uspto' in db.lower()
                           for db in db_inventory.keys())
        has_new_patents = any('patent' in name for name in new_data_inventory.keys())

        if has_new_patents:
            if has_patent_db:
                print("  [!] Overlap: Patent data exists in both existing DB and new data")
                print("      Action: Compare and merge/update")
                overlaps.append({
                    'category': 'Patents',
                    'existing': 'USPTO databases',
                    'new': 'BigQuery patent datasets',
                    'action': 'Merge/update with new company-level aggregations'
                })
            else:
                print("  [OK] New data: Patent datasets from BigQuery")
                print("      Action: Create new patent analytics tables")
                gaps.append({
                    'category': 'Patents',
                    'new_data': 'BigQuery patent assignees, citations, inventors, families',
                    'action': 'Create patent_analytics database'
                })

        # Check for academic publication overlap
        print("\n[ACADEMIC PUBLICATIONS]")
        has_openaire = 'openaire_production' in db_inventory
        has_new_academic = False  # BigQuery doesn't have academic pubs

        if has_openaire:
            print("  [OK] Existing: OpenAIRE production database (2.1GB)")
            print("      Coverage: European research publications")
            print("  [!] Gap: BigQuery has no academic publication data")
            print("      Action: Keep existing OpenAIRE, no merge needed")

        # Check for GitHub data
        print("\n[SOFTWARE DEVELOPMENT - GITHUB]")
        has_github_db = False  # No existing GitHub database
        has_new_github = 'github_full_history' in new_data_inventory

        if has_new_github:
            print("  [OK] New data: GitHub full history (2011-2025)")
            print("      Coverage: 14 Chinese tech companies, 139K events")
            print("      Action: Create new github_analytics table")
            gaps.append({
                'category': 'Software Development',
                'new_data': 'GitHub activity 2011-2025',
                'action': 'Create github_analytics database'
            })

        # Check for economic indicators
        print("\n[ECONOMIC INDICATORS]")
        has_economic_db = False
        has_new_economic = 'world_bank' in new_data_inventory

        if has_new_economic:
            print("  [OK] New data: World Bank indicators (1990-2020)")
            print("      Coverage: 30 indicators - R&D, GDP, trade, manufacturing")
            print("      Action: Create economic_indicators table")
            gaps.append({
                'category': 'Economic Indicators',
                'new_data': 'World Bank comprehensive indicators',
                'action': 'Create economic_indicators table'
            })

        # Check for company data
        print("\n[COMPANY DATA]")
        has_uk_companies = 'uk_companies' in db_inventory
        has_new_companies = False  # BigQuery has patent assignees

        if has_uk_companies:
            print("  [OK] Existing: UK Companies House (715MB)")
            print("      Coverage: UK registered companies")

        print("  [OK] New data: Patent assignees (449,725 unique companies)")
        print("      Coverage: Chinese companies/institutions filing patents")
        print("      Action: Create company_patent_profiles table")

        # Check for CNIPA data
        print("\n[CNIPA PATENTS (DOMESTIC)]")
        has_cnipa_db = False
        has_new_cnipa = any('cnipa' in name for name in new_data_inventory.keys())

        if has_new_cnipa:
            print("  [OK] New data: CNIPA comprehensive (2011-2025)")
            print("      Coverage: 46.9M Chinese domestic patents")
            print("      Coverage: 11 technology sectors, Made in China 2025 tracking")
            print("      Action: Create cnipa_analytics database")
            gaps.append({
                'category': 'CNIPA Patents',
                'new_data': 'Complete CNIPA dataset with sector analysis',
                'action': 'Create cnipa_analytics database with policy tracking'
            })

        return overlaps, gaps

    def create_integration_plan(self, db_inventory, new_data_inventory, overlaps, gaps):
        """Create comprehensive integration plan"""
        print("\n" + "="*80)
        print("INTEGRATION PLAN")
        print("="*80)

        plan = {
            'created': datetime.now().isoformat(),
            'existing_databases': len(db_inventory),
            'new_datasets': len(new_data_inventory),
            'overlaps': len(overlaps),
            'gaps': len(gaps),
            'recommendations': []
        }

        # Recommendation 1: Create new consolidated database
        print("\n[RECOMMENDATION 1: CREATE CONSOLIDATED ANALYTICS DATABASE]")
        print("  Create: F:/OSINT_Data/bigquery_analytics/consolidated.db")
        print("  Purpose: Integrate all BigQuery-sourced data for technology analytics")
        print("  Tables:")

        tables_to_create = [
            {
                'name': 'patent_assignees_annual',
                'source': 'patent_assignees_annual.csv',
                'records': new_data_inventory.get('patent_assignees', {}).get('records', 0),
                'purpose': 'Track patent activity by company/institution over time'
            },
            {
                'name': 'patent_citations_annual',
                'source': 'patent_citations_annual.csv',
                'records': new_data_inventory.get('patent_citations', {}).get('records', 0),
                'purpose': 'Measure patent impact and citation networks'
            },
            {
                'name': 'patent_inventors_annual',
                'source': 'patent_inventors_annual.csv',
                'records': new_data_inventory.get('patent_inventors', {}).get('records', 0),
                'purpose': 'Track inventor collaboration and networks'
            },
            {
                'name': 'patent_families_annual',
                'source': 'patent_families_annual.csv',
                'records': new_data_inventory.get('patent_families', {}).get('records', 0),
                'purpose': 'Analyze international patent strategies'
            },
            {
                'name': 'github_activity',
                'source': 'github_chinese_companies_full_history.csv',
                'records': new_data_inventory.get('github_full_history', {}).get('records', 0),
                'purpose': 'Track open-source development activity 2011-2025'
            },
            {
                'name': 'economic_indicators',
                'source': 'world_bank_china_comprehensive.csv',
                'records': new_data_inventory.get('world_bank', {}).get('records', 0),
                'purpose': 'Macroeconomic context for technology development'
            },
            {
                'name': 'technology_adoption',
                'source': 'stackoverflow_technology_adoption.csv',
                'records': new_data_inventory.get('stackoverflow', {}).get('records', 0),
                'purpose': 'Track technology discussion and adoption patterns'
            }
        ]

        for table in tables_to_create:
            print(f"    - {table['name']}: {table['records']:,} records")
            print(f"      Purpose: {table['purpose']}")

        plan['recommendations'].append({
            'priority': 'HIGH',
            'action': 'Create consolidated BigQuery analytics database',
            'tables': tables_to_create
        })

        # Recommendation 2: Create CNIPA database
        print("\n[RECOMMENDATION 2: CREATE CNIPA ANALYTICS DATABASE]")
        print("  Create: F:/OSINT_Data/cnipa_analytics/cnipa_analytics.db")
        print("  Purpose: Track Made in China 2025 policy impact")
        print("  Tables:")

        cnipa_tables = [
            {
                'name': 'annual_filing_dates',
                'source': 'annual_filing_dates.csv',
                'records': new_data_inventory.get('cnipa_annual_filing', {}).get('records', 0),
                'purpose': 'Annual patent filing trends'
            },
            {
                'name': 'annual_grant_dates',
                'source': 'annual_grant_dates.csv',
                'records': new_data_inventory.get('cnipa_annual_grant', {}).get('records', 0),
                'purpose': 'Annual patent grant trends'
            },
            {
                'name': 'sector_analysis',
                'source': 'sector_annual_filing.csv + sector_annual_grant.csv',
                'records': new_data_inventory.get('cnipa_sector_filing', {}).get('records', 0),
                'purpose': 'Track 11 MIC2025 priority sectors'
            },
            {
                'name': 'advanced_it_subcategories',
                'source': 'advanced_it_subcategories.csv',
                'records': new_data_inventory.get('cnipa_advanced_it', {}).get('records', 0),
                'purpose': 'Detailed analysis: semiconductors, AI, 5G, etc.'
            },
            {
                'name': 'mic2025_impact_metrics',
                'source': 'CALCULATED',
                'records': 15,
                'purpose': 'Pre/post policy growth rates for validation'
            }
        ]

        for table in cnipa_tables:
            print(f"    - {table['name']}: {table['records']:,} records")
            print(f"      Purpose: {table['purpose']}")

        plan['recommendations'].append({
            'priority': 'HIGH',
            'action': 'Create CNIPA analytics database for policy tracking',
            'tables': cnipa_tables
        })

        # Recommendation 3: Link to existing databases
        print("\n[RECOMMENDATION 3: CROSS-DATABASE LINKAGES]")
        print("  Maintain existing databases, create linkage tables:")
        print("    - OpenAIRE (2.1GB) - Keep as-is, link via company names")
        print("    - UK Companies (715MB) - Keep as-is, link via company names")
        print("    - USASpending (27MB) - Keep as-is, link via contractor names")
        print("  Create: linkage_tables.db with cross-reference mappings")

        plan['recommendations'].append({
            'priority': 'MEDIUM',
            'action': 'Create cross-database linkages',
            'linkages': [
                'Patent assignees <-> OpenAIRE institutions',
                'Patent assignees <-> UK Companies registry',
                'Patent assignees <-> USASpending contractors'
            ]
        })

        # Recommendation 4: Add indices and views
        print("\n[RECOMMENDATION 4: PERFORMANCE OPTIMIZATION]")
        print("  Add indices:")
        print("    - company_name, year (for time series queries)")
        print("    - year (for annual aggregations)")
        print("    - indicator_code (for World Bank data)")
        print("    - repo_name, month (for GitHub trends)")

        plan['recommendations'].append({
            'priority': 'MEDIUM',
            'action': 'Add performance indices',
            'indices': [
                'CREATE INDEX idx_assignee_year ON patent_assignees_annual(assignee_name, year)',
                'CREATE INDEX idx_year ON economic_indicators(year)',
                'CREATE INDEX idx_indicator ON economic_indicators(indicator_code)',
                'CREATE INDEX idx_github_repo ON github_activity(repo_name, month)'
            ]
        })

        return plan

    def generate_integration_report(self):
        """Generate complete integration assessment report"""
        print("="*80)
        print("DATA INTEGRATION ASSESSMENT")
        print("="*80)

        # Step 1: Analyze existing
        db_inventory = self.analyze_existing_databases()

        # Step 2: Analyze new data
        new_data_inventory = self.analyze_new_bigquery_data()

        # Step 3: Assess overlap
        overlaps, gaps = self.assess_data_overlap(db_inventory, new_data_inventory)

        # Step 4: Create integration plan
        plan = self.create_integration_plan(db_inventory, new_data_inventory, overlaps, gaps)

        # Save report
        report = {
            'assessment_date': datetime.now().isoformat(),
            'existing_databases': db_inventory,
            'new_bigquery_data': new_data_inventory,
            'overlaps': overlaps,
            'gaps': gaps,
            'integration_plan': plan
        }

        output_file = self.bigquery_dir / 'integration_assessment_report.json'
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)

        print("\n" + "="*80)
        print("ASSESSMENT COMPLETE")
        print("="*80)
        print(f"\nReport saved: {output_file}")

        return report

def main():
    assessor = IntegrationAssessor()
    report = assessor.generate_integration_report()

    print("\n" + "="*80)
    print("NEXT STEPS")
    print("="*80)
    print("\n1. Review integration_assessment_report.json")
    print("2. Run data cleaning script (if needed)")
    print("3. Execute database creation scripts")
    print("4. Create linkage tables for cross-database queries")
    print("5. Add performance indices")

if __name__ == "__main__":
    main()

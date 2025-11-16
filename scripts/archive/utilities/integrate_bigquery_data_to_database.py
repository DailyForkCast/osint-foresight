#!/usr/bin/env python3
"""
Integrate BigQuery Data to Database
Create new databases and load all BigQuery/CNIPA data with proper schema
"""

import pandas as pd
import sqlite3
from pathlib import Path
from datetime import datetime
import json

class DatabaseIntegrator:
    def __init__(self):
        self.bigquery_dir = Path("data/bigquery_comprehensive")
        self.cnipa_dir = Path("data/cnipa_comprehensive")
        self.output_dir = Path("F:/OSINT_Data/bigquery_analytics")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.cnipa_output_dir = Path("F:/OSINT_Data/cnipa_analytics")
        self.cnipa_output_dir.mkdir(parents=True, exist_ok=True)

        self.stats = {}

    def create_bigquery_analytics_db(self):
        """Create consolidated BigQuery analytics database"""
        print("\n" + "="*80)
        print("CREATING: BigQuery Analytics Database")
        print("="*80)

        db_path = self.output_dir / 'consolidated.db'
        print(f"\nDatabase: {db_path}")

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        total_records = 0

        # Table 1: Patent Assignees
        print("\n[1/7] Loading patent_assignees_annual...")
        df = pd.read_csv(self.bigquery_dir / 'patent_assignees_annual.csv')
        df.to_sql('patent_assignees_annual', conn, if_exists='replace', index=False)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_assignee_year ON patent_assignees_annual(assignee_name, year)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_year_pa ON patent_assignees_annual(year)")
        print(f"  Loaded: {len(df):,} records")
        print(f"  Indices: assignee_name+year, year")
        total_records += len(df)

        # Table 2: Patent Citations
        print("\n[2/7] Loading patent_citations_annual...")
        df = pd.read_csv(self.bigquery_dir / 'patent_citations_annual.csv')
        df.to_sql('patent_citations_annual', conn, if_exists='replace', index=False)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_year_pc ON patent_citations_annual(year)")
        print(f"  Loaded: {len(df):,} records")
        print(f"  Indices: year")
        total_records += len(df)

        # Table 3: Patent Inventors
        print("\n[3/7] Loading patent_inventors_annual...")
        df = pd.read_csv(self.bigquery_dir / 'patent_inventors_annual.csv')
        df.to_sql('patent_inventors_annual', conn, if_exists='replace', index=False)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_year_pi ON patent_inventors_annual(year)")
        print(f"  Loaded: {len(df):,} records")
        print(f"  Indices: year")
        total_records += len(df)

        # Table 4: Patent Families
        print("\n[4/7] Loading patent_families_annual...")
        df = pd.read_csv(self.bigquery_dir / 'patent_families_annual.csv')
        df.to_sql('patent_families_annual', conn, if_exists='replace', index=False)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_year_pf ON patent_families_annual(year)")
        print(f"  Loaded: {len(df):,} records")
        print(f"  Indices: year")
        total_records += len(df)

        # Table 5: GitHub Activity
        print("\n[5/7] Loading github_activity...")
        df = pd.read_csv(self.bigquery_dir / 'github_chinese_companies_full_history.csv')
        df.to_sql('github_activity', conn, if_exists='replace', index=False)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_repo_month ON github_activity(repo_name, month)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_month ON github_activity(month)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_event_type ON github_activity(event_type)")
        print(f"  Loaded: {len(df):,} records")
        print(f"  Indices: repo_name+month, month, event_type")
        total_records += len(df)

        # Table 6: Economic Indicators
        print("\n[6/7] Loading economic_indicators...")
        df = pd.read_csv(self.bigquery_dir / 'world_bank_china_comprehensive.csv')
        df.to_sql('economic_indicators', conn, if_exists='replace', index=False)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_indicator_year ON economic_indicators(indicator_code, year)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_year_ei ON economic_indicators(year)")
        print(f"  Loaded: {len(df):,} records")
        print(f"  Indices: indicator_code+year, year")
        total_records += len(df)

        # Table 7: Technology Adoption (Stack Overflow)
        print("\n[7/7] Loading technology_adoption...")
        df = pd.read_csv(self.bigquery_dir / 'stackoverflow_technology_adoption.csv')
        df.to_sql('technology_adoption', conn, if_exists='replace', index=False)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_year_ta ON technology_adoption(year)")
        print(f"  Loaded: {len(df):,} records")
        print(f"  Indices: year")
        total_records += len(df)

        # Create metadata table
        print("\n[METADATA] Creating database_metadata...")
        metadata = {
            'created': datetime.now().isoformat(),
            'source': 'Google BigQuery Public Datasets',
            'total_records': total_records,
            'tables': 7,
            'date_range': '2011-2025',
            'purpose': 'Consolidated technology analytics for Chinese innovation tracking'
        }

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS database_metadata (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)

        for key, value in metadata.items():
            cursor.execute("INSERT OR REPLACE INTO database_metadata (key, value) VALUES (?, ?)",
                         (key, str(value)))

        conn.commit()
        conn.close()

        print(f"\n[OK] Database created successfully")
        print(f"  Total records: {total_records:,}")
        print(f"  Size: {db_path.stat().st_size / (1024**2):.2f} MB")

        self.stats['bigquery_analytics'] = {
            'path': str(db_path),
            'records': total_records,
            'tables': 7,
            'size_mb': db_path.stat().st_size / (1024**2)
        }

        return db_path

    def create_cnipa_analytics_db(self):
        """Create CNIPA analytics database for Made in China 2025 tracking"""
        print("\n" + "="*80)
        print("CREATING: CNIPA Analytics Database")
        print("="*80)

        db_path = self.cnipa_output_dir / 'cnipa_analytics.db'
        print(f"\nDatabase: {db_path}")

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        total_records = 0

        # Table 1: Annual Filing
        print("\n[1/5] Loading annual_filing_dates...")
        df = pd.read_csv(self.cnipa_dir / 'annual_filing_dates.csv')
        df.to_sql('annual_filing_dates', conn, if_exists='replace', index=False)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_year_filing ON annual_filing_dates(year)")
        print(f"  Loaded: {len(df):,} records")
        total_records += len(df)

        # Table 2: Annual Grant
        print("\n[2/5] Loading annual_grant_dates...")
        df = pd.read_csv(self.cnipa_dir / 'annual_grant_dates.csv')
        df.to_sql('annual_grant_dates', conn, if_exists='replace', index=False)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_year_grant ON annual_grant_dates(year)")
        print(f"  Loaded: {len(df):,} records")
        total_records += len(df)

        # Table 3: Sector Filing
        print("\n[3/5] Loading sector_filing_annual...")
        df = pd.read_csv(self.cnipa_dir / 'sector_annual_filing.csv')
        df.to_sql('sector_filing_annual', conn, if_exists='replace', index=False)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sector_year_f ON sector_filing_annual(sector, year)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_year_sf ON sector_filing_annual(year)")
        print(f"  Loaded: {len(df):,} records")
        total_records += len(df)

        # Table 4: Sector Grant
        print("\n[4/5] Loading sector_grant_annual...")
        df = pd.read_csv(self.cnipa_dir / 'sector_annual_grant.csv')
        df.to_sql('sector_grant_annual', conn, if_exists='replace', index=False)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sector_year_g ON sector_grant_annual(sector, year)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_year_sg ON sector_grant_annual(year)")
        print(f"  Loaded: {len(df):,} records")
        total_records += len(df)

        # Table 5: Advanced IT Subcategories
        print("\n[5/5] Loading advanced_it_subcategories...")
        df = pd.read_csv(self.cnipa_dir / 'advanced_it_subcategories.csv')
        df.to_sql('advanced_it_subcategories', conn, if_exists='replace', index=False)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_subcat_year ON advanced_it_subcategories(subcategory, year)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_year_ait ON advanced_it_subcategories(year)")
        print(f"  Loaded: {len(df):,} records")
        total_records += len(df)

        # Create MIC2025 impact metrics view
        print("\n[VIEW] Creating mic2025_impact_metrics...")
        cursor.execute("""
            CREATE VIEW IF NOT EXISTS mic2025_impact_metrics AS
            SELECT
                sector,
                SUM(CASE WHEN year < 2015 THEN patent_count ELSE 0 END) as pre_policy_total,
                SUM(CASE WHEN year >= 2015 THEN patent_count ELSE 0 END) as post_policy_total,
                ROUND(
                    (CAST(SUM(CASE WHEN year >= 2015 THEN patent_count ELSE 0 END) AS REAL) /
                     SUM(CASE WHEN year < 2015 THEN patent_count ELSE 0 END) - 1) * 100,
                    1
                ) as growth_pct
            FROM sector_filing_annual
            GROUP BY sector
            ORDER BY growth_pct DESC
        """)
        print(f"  Created view for policy impact analysis")

        # Create metadata
        print("\n[METADATA] Creating database_metadata...")
        metadata = {
            'created': datetime.now().isoformat(),
            'source': 'Google BigQuery - CNIPA Patents',
            'total_records': total_records,
            'tables': 5,
            'views': 1,
            'date_range': '2011-2025',
            'policy_date': '2015-05-08',
            'purpose': 'Track Made in China 2025 policy impact on domestic patents',
            'total_patents_analyzed': '46,886,314'
        }

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS database_metadata (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)

        for key, value in metadata.items():
            cursor.execute("INSERT OR REPLACE INTO database_metadata (key, value) VALUES (?, ?)",
                         (key, str(value)))

        conn.commit()
        conn.close()

        print(f"\n[OK] Database created successfully")
        print(f"  Total records: {total_records:,}")
        print(f"  Size: {db_path.stat().st_size / (1024**2):.2f} MB")

        self.stats['cnipa_analytics'] = {
            'path': str(db_path),
            'records': total_records,
            'tables': 5,
            'views': 1,
            'size_mb': db_path.stat().st_size / (1024**2)
        }

        return db_path

    def create_supplementary_tables(self):
        """Create supplementary data tables (PyPI, Ethereum)"""
        print("\n" + "="*80)
        print("CREATING: Supplementary Data Tables")
        print("="*80)

        db_path = self.output_dir / 'supplementary_data.db'
        print(f"\nDatabase: {db_path}")

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        total_records = 0

        # Table 1: PyPI Downloads
        print("\n[1/2] Loading pypi_downloads...")
        df = pd.read_csv(self.bigquery_dir / 'pypi_china_downloads.csv')
        df.to_sql('pypi_downloads', conn, if_exists='replace', index=False)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_package_year ON pypi_downloads(package_name, year)")
        print(f"  Loaded: {len(df):,} records")
        total_records += len(df)

        # Table 2: Ethereum Activity
        print("\n[2/2] Loading ethereum_activity...")
        df = pd.read_csv(self.bigquery_dir / 'ethereum_activity_sample.csv')
        df.to_sql('ethereum_activity', conn, if_exists='replace', index=False)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_date ON ethereum_activity(date)")
        print(f"  Loaded: {len(df):,} records")
        total_records += len(df)

        conn.commit()
        conn.close()

        print(f"\n[OK] Database created successfully")
        print(f"  Total records: {total_records:,}")
        print(f"  Size: {db_path.stat().st_size / (1024**2):.2f} MB")

        self.stats['supplementary_data'] = {
            'path': str(db_path),
            'records': total_records,
            'tables': 2,
            'size_mb': db_path.stat().st_size / (1024**2)
        }

        return db_path

    def generate_integration_summary(self):
        """Generate summary of integration"""
        print("\n" + "="*80)
        print("INTEGRATION SUMMARY")
        print("="*80)

        summary = {
            'integration_date': datetime.now().isoformat(),
            'databases_created': len(self.stats),
            'total_records': sum(s['records'] for s in self.stats.values()),
            'total_size_mb': sum(s['size_mb'] for s in self.stats.values()),
            'databases': self.stats
        }

        output_file = self.output_dir / 'integration_summary.json'
        with open(output_file, 'w') as f:
            json.dump(summary, f, indent=2)

        print(f"\nDatabases created: {summary['databases_created']}")
        print(f"Total records: {summary['total_records']:,}")
        print(f"Total size: {summary['total_size_mb']:.2f} MB")

        print("\n[DATABASE LOCATIONS]")
        for db_name, info in self.stats.items():
            print(f"\n  {db_name}:")
            print(f"    Path: {info['path']}")
            print(f"    Records: {info['records']:,}")
            print(f"    Tables: {info['tables']}")
            print(f"    Size: {info['size_mb']:.2f} MB")

        print(f"\n\nSummary saved: {output_file}")

        return summary

    def integrate_all(self):
        """Run complete integration"""
        print("="*80)
        print("BIGQUERY DATA INTEGRATION")
        print("="*80)

        # Create databases
        bigquery_db = self.create_bigquery_analytics_db()
        cnipa_db = self.create_cnipa_analytics_db()
        supplementary_db = self.create_supplementary_tables()

        # Generate summary
        summary = self.generate_integration_summary()

        print("\n" + "="*80)
        print("INTEGRATION COMPLETE")
        print("="*80)

        return summary

def main():
    integrator = DatabaseIntegrator()
    summary = integrator.integrate_all()

    print("\n" + "="*80)
    print("NEXT STEPS")
    print("="*80)
    print("\n1. Query databases using SQLite:")
    print("   sqlite3 F:/OSINT_Data/bigquery_analytics/consolidated.db")
    print("\n2. Create cross-database linkages (future work)")
    print("\n3. Build analysis scripts/dashboards on top of databases")
    print("\n4. Regular updates: Re-run BigQuery extractions quarterly")

if __name__ == "__main__":
    main()

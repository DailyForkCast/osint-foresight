#!/usr/bin/env python3
"""
Comprehensive BigQuery Data Extraction
Extract all valuable datasets for China technology analysis
"""

from google.cloud import bigquery
from datetime import datetime
import pandas as pd
import json
from pathlib import Path
import time

class BigQueryExtractor:
    def __init__(self):
        self.client = bigquery.Client()
        self.output_dir = Path("data/bigquery_comprehensive")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.total_cost = 0
        self.results_log = []

    def log_extraction(self, name, rows, cost, status="SUCCESS"):
        """Log extraction results"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'dataset': name,
            'rows': rows,
            'cost_usd': cost,
            'status': status
        }
        self.results_log.append(entry)
        self.total_cost += cost

    def save_log(self):
        """Save extraction log"""
        with open(self.output_dir / 'extraction_log.json', 'w') as f:
            json.dump({
                'total_cost_usd': round(self.total_cost, 4),
                'extractions': self.results_log
            }, f, indent=2)

    # =========================================================================
    # PHASE 1: PATENT ASSIGNEES
    # =========================================================================
    def extract_patent_assignees(self):
        """
        Extract top Chinese patent assignees (companies, universities)
        Annual time series 2011-2025
        """
        print("\n" + "="*80)
        print("[1/9] EXTRACTING PATENT ASSIGNEES (Companies/Universities)")
        print("="*80)

        query = """
        SELECT
            assignee.name as assignee_name,
            CAST(p.filing_date / 10000 AS INT64) as year,
            COUNT(DISTINCT p.publication_number) as patent_count
        FROM `patents-public-data.patents.publications` p,
            UNNEST(p.assignee_harmonized) as assignee
        WHERE p.country_code = 'CN'
            AND p.filing_date >= 20110101
            AND p.filing_date <= 20251231
            AND assignee.name IS NOT NULL
        GROUP BY assignee_name, year
        HAVING patent_count >= 10
        ORDER BY year, patent_count DESC
        """

        print("\nQuerying patent assignees (2-3 minutes)...")
        job = self.client.query(query)
        results = list(job.result())

        df = pd.DataFrame([{
            'assignee_name': r['assignee_name'],
            'year': r['year'],
            'patent_count': r['patent_count']
        } for r in results])

        output_file = self.output_dir / 'patent_assignees_annual.csv'
        df.to_csv(output_file, index=False, encoding='utf-8')

        cost = (job.total_bytes_billed / 1e12) * 5
        print(f"  Extracted: {len(df):,} records")
        print(f"  Unique assignees: {df['assignee_name'].nunique():,}")
        print(f"  Cost: ${cost:.4f}")

        self.log_extraction('patent_assignees', len(df), cost)
        return df

    # =========================================================================
    # PHASE 2: PATENT CITATIONS
    # =========================================================================
    def extract_patent_citations(self):
        """
        Extract citation patterns for Chinese patents
        """
        print("\n" + "="*80)
        print("[2/9] EXTRACTING PATENT CITATIONS")
        print("="*80)

        # Get citation counts by year
        query = """
        SELECT
            CAST(filing_date / 10000 AS INT64) as year,
            COUNT(DISTINCT publication_number) as patents_total,
            COUNT(DISTINCT CASE WHEN ARRAY_LENGTH(citation) > 0 THEN publication_number END) as patents_with_citations,
            SUM(ARRAY_LENGTH(citation)) as total_citations,
            AVG(ARRAY_LENGTH(citation)) as avg_citations_per_patent
        FROM `patents-public-data.patents.publications`
        WHERE country_code = 'CN'
            AND filing_date >= 20110101
            AND filing_date <= 20251231
        GROUP BY year
        ORDER BY year
        """

        print("\nQuerying citation statistics (3-4 minutes)...")
        job = self.client.query(query)
        results = list(job.result())

        df = pd.DataFrame([{
            'year': r['year'],
            'patents_total': r['patents_total'],
            'patents_with_citations': r['patents_with_citations'],
            'total_citations': r['total_citations'],
            'avg_citations_per_patent': round(r['avg_citations_per_patent'], 2) if r['avg_citations_per_patent'] else 0
        } for r in results])

        output_file = self.output_dir / 'patent_citations_annual.csv'
        df.to_csv(output_file, index=False)

        cost = (job.total_bytes_billed / 1e12) * 5
        print(f"  Extracted: {len(df)} years")
        print(f"  Total citations tracked: {df['total_citations'].sum():,}")
        print(f"  Cost: ${cost:.4f}")

        self.log_extraction('patent_citations', len(df), cost)
        return df

    # =========================================================================
    # PHASE 3: PATENT INVENTORS
    # =========================================================================
    def extract_patent_inventors(self):
        """
        Extract inventor statistics and collaboration patterns
        """
        print("\n" + "="*80)
        print("[3/9] EXTRACTING PATENT INVENTOR NETWORKS")
        print("="*80)

        # Get inventor counts and collaboration metrics
        query = """
        SELECT
            CAST(p.filing_date / 10000 AS INT64) as year,
            COUNT(DISTINCT p.publication_number) as patents,
            COUNT(DISTINCT inventor.name) as unique_inventors,
            AVG(ARRAY_LENGTH(p.inventor_harmonized)) as avg_inventors_per_patent,
            COUNT(DISTINCT CASE
                WHEN ARRAY_LENGTH(p.inventor_harmonized) > 1 THEN p.publication_number
            END) as collaborative_patents
        FROM `patents-public-data.patents.publications` p,
            UNNEST(p.inventor_harmonized) as inventor
        WHERE p.country_code = 'CN'
            AND p.filing_date >= 20110101
            AND p.filing_date <= 20251231
        GROUP BY year
        ORDER BY year
        """

        print("\nQuerying inventor statistics (3-4 minutes)...")
        job = self.client.query(query)
        results = list(job.result())

        df = pd.DataFrame([{
            'year': r['year'],
            'patents': r['patents'],
            'unique_inventors': r['unique_inventors'],
            'avg_inventors_per_patent': round(r['avg_inventors_per_patent'], 2) if r['avg_inventors_per_patent'] else 0,
            'collaborative_patents': r['collaborative_patents'],
            'collaboration_rate_pct': round((r['collaborative_patents'] / r['patents'] * 100), 1) if r['patents'] > 0 else 0
        } for r in results])

        output_file = self.output_dir / 'patent_inventors_annual.csv'
        df.to_csv(output_file, index=False)

        cost = (job.total_bytes_billed / 1e12) * 5
        print(f"  Extracted: {len(df)} years")
        print(f"  Total unique inventors: {df['unique_inventors'].sum():,}")
        print(f"  Cost: ${cost:.4f}")

        self.log_extraction('patent_inventors', len(df), cost)
        return df

    # =========================================================================
    # PHASE 4: PATENT FAMILIES (International Filing)
    # =========================================================================
    def extract_patent_families(self):
        """
        Extract patent family statistics (international filing patterns)
        """
        print("\n" + "="*80)
        print("[4/9] EXTRACTING PATENT FAMILIES (International Filing)")
        print("="*80)

        query = """
        SELECT
            CAST(filing_date / 10000 AS INT64) as year,
            COUNT(DISTINCT publication_number) as cn_patents,
            COUNT(DISTINCT family_id) as unique_families,
            COUNT(DISTINCT CASE
                WHEN family_id IS NOT NULL THEN publication_number
            END) as patents_in_families
        FROM `patents-public-data.patents.publications`
        WHERE country_code = 'CN'
            AND filing_date >= 20110101
            AND filing_date <= 20251231
        GROUP BY year
        ORDER BY year
        """

        print("\nQuerying patent families (2-3 minutes)...")
        job = self.client.query(query)
        results = list(job.result())

        df = pd.DataFrame([{
            'year': r['year'],
            'cn_patents': r['cn_patents'],
            'unique_families': r['unique_families'],
            'patents_in_families': r['patents_in_families'],
            'international_filing_rate_pct': round((r['patents_in_families'] / r['cn_patents'] * 100), 1) if r['cn_patents'] > 0 else 0
        } for r in results])

        output_file = self.output_dir / 'patent_families_annual.csv'
        df.to_csv(output_file, index=False)

        cost = (job.total_bytes_billed / 1e12) * 5
        print(f"  Extracted: {len(df)} years")
        print(f"  Unique patent families: {df['unique_families'].sum():,}")
        print(f"  Cost: ${cost:.4f}")

        self.log_extraction('patent_families', len(df), cost)
        return df

    # =========================================================================
    # PHASE 5: GITHUB ARCHIVE - Chinese Tech Companies
    # =========================================================================
    def extract_github_chinese_companies(self):
        """
        Extract GitHub activity for major Chinese tech companies
        """
        print("\n" + "="*80)
        print("[5/9] EXTRACTING GITHUB ACTIVITY - Chinese Tech Companies")
        print("="*80)

        # Major Chinese tech companies GitHub orgs
        companies = [
            'huawei', 'alibaba', 'tencent', 'bytedance', 'baidu',
            'xiaomi', 'zte', 'dji', 'meituan', 'pinduoduo',
            'jd', 'netease', 'bilibili', 'kuaishou', 'wechat'
        ]

        # Sample recent months (avoid huge query)
        recent_months = ['202401', '202402', '202403', '202404', '202405', '202406',
                        '202407', '202408', '202409', '202410', '202411', '202412']

        all_data = []

        for month in recent_months:
            try:
                # Build org filter
                org_conditions = " OR ".join([f"repo.name LIKE '{company}/%'" for company in companies])

                query = f"""
                SELECT
                    '{month}' as month,
                    repo.name as repo_name,
                    type as event_type,
                    COUNT(*) as event_count
                FROM `githubarchive.month.{month}`
                WHERE ({org_conditions})
                GROUP BY repo_name, event_type
                """

                print(f"\n  Querying {month}...")
                job = self.client.query(query)
                results = list(job.result())

                month_data = [{
                    'month': r['month'],
                    'repo_name': r['repo_name'],
                    'event_type': r['event_type'],
                    'event_count': r['event_count']
                } for r in results]

                all_data.extend(month_data)

                cost = (job.total_bytes_billed / 1e12) * 5
                print(f"    Extracted: {len(results)} records, Cost: ${cost:.4f}")

                self.total_cost += cost

            except Exception as e:
                print(f"    Error for {month}: {e}")
                continue

        df = pd.DataFrame(all_data)

        if len(df) > 0:
            output_file = self.output_dir / 'github_chinese_companies_2024.csv'
            df.to_csv(output_file, index=False)
            print(f"\n  Total extracted: {len(df):,} records")

        self.log_extraction('github_chinese_companies', len(df), self.total_cost)
        return df

    # =========================================================================
    # PHASE 6: STACK OVERFLOW - Technology Adoption
    # =========================================================================
    def extract_stackoverflow_china(self):
        """
        Extract Stack Overflow technology adoption patterns
        """
        print("\n" + "="*80)
        print("[6/9] EXTRACTING STACK OVERFLOW - Technology Adoption")
        print("="*80)

        # Get question counts by tag and year for key technologies
        query = """
        SELECT
            EXTRACT(YEAR FROM creation_date) as year,
            tags,
            COUNT(*) as question_count
        FROM `bigquery-public-data.stackoverflow.posts_questions`
        WHERE EXTRACT(YEAR FROM creation_date) >= 2011
            AND (
                tags LIKE '%semiconductor%' OR
                tags LIKE '%ai%' OR
                tags LIKE '%machine-learning%' OR
                tags LIKE '%quantum%' OR
                tags LIKE '%tensorflow%' OR
                tags LIKE '%pytorch%' OR
                tags LIKE '%5g%' OR
                tags LIKE '%robotics%' OR
                tags LIKE '%blockchain%'
            )
        GROUP BY year, tags
        ORDER BY year DESC, question_count DESC
        LIMIT 10000
        """

        print("\nQuerying Stack Overflow patterns (1-2 minutes)...")
        job = self.client.query(query)
        results = list(job.result())

        df = pd.DataFrame([{
            'year': r['year'],
            'tags': r['tags'],
            'question_count': r['question_count']
        } for r in results])

        output_file = self.output_dir / 'stackoverflow_technology_adoption.csv'
        df.to_csv(output_file, index=False)

        cost = (job.total_bytes_billed / 1e12) * 5
        print(f"  Extracted: {len(df):,} records")
        print(f"  Cost: ${cost:.4f}")

        self.log_extraction('stackoverflow', len(df), cost)
        return df

    # =========================================================================
    # PHASE 7: WORLD BANK - R&D and Economic Indicators
    # =========================================================================
    def extract_world_bank_indicators(self):
        """
        Extract World Bank development indicators for China
        """
        print("\n" + "="*80)
        print("[7/9] EXTRACTING WORLD BANK INDICATORS")
        print("="*80)

        # Key indicators for technology analysis
        indicators = [
            'GB.XPD.RSDV.GD.ZS',  # R&D expenditure (% of GDP)
            'IP.PAT.RESD',         # Patent applications, residents
            'IP.PAT.NRES',         # Patent applications, nonresidents
            'NY.GDP.MKTP.CD',      # GDP (current US$)
            'SP.POP.TOTL',         # Population
        ]

        query = f"""
        SELECT
            country_name,
            country_code,
            indicator_name,
            indicator_code,
            year,
            value
        FROM `bigquery-public-data.world_bank_wdi.indicators_data`
        WHERE country_code = 'CHN'
            AND year >= 2011
            AND indicator_code IN UNNEST({indicators})
        ORDER BY year, indicator_code
        """

        print("\nQuerying World Bank indicators...")
        job = self.client.query(query)
        results = list(job.result())

        df = pd.DataFrame([{
            'country_name': r['country_name'],
            'country_code': r['country_code'],
            'indicator_name': r['indicator_name'],
            'indicator_code': r['indicator_code'],
            'year': r['year'],
            'value': r['value']
        } for r in results])

        output_file = self.output_dir / 'world_bank_china_indicators.csv'
        df.to_csv(output_file, index=False)

        cost = (job.total_bytes_billed / 1e12) * 5
        print(f"  Extracted: {len(df)} records")
        print(f"  Years: {df['year'].min()}-{df['year'].max()}")
        print(f"  Cost: ${cost:.4f}")

        self.log_extraction('world_bank', len(df), cost)
        return df

    # =========================================================================
    # PHASE 8: PYTHON PACKAGE INDEX
    # =========================================================================
    def extract_pypi_downloads(self):
        """
        Extract Python package download patterns (AI/ML libraries)
        """
        print("\n" + "="*80)
        print("[8/9] EXTRACTING PYPI - Python Package Downloads")
        print("="*80)

        # Key AI/ML packages
        packages = [
            'tensorflow', 'pytorch', 'keras', 'scikit-learn',
            'numpy', 'pandas', 'transformers', 'jax'
        ]

        query = f"""
        SELECT
            file.project as package_name,
            EXTRACT(YEAR FROM timestamp) as year,
            EXTRACT(MONTH FROM timestamp) as month,
            country_code,
            COUNT(*) as download_count
        FROM `bigquery-public-data.pypi.file_downloads`
        WHERE file.project IN UNNEST({packages})
            AND country_code = 'CN'
            AND timestamp >= '2020-01-01'
        GROUP BY package_name, year, month, country_code
        ORDER BY year DESC, month DESC, download_count DESC
        LIMIT 5000
        """

        print("\nQuerying PyPI downloads (1-2 minutes)...")
        try:
            job = self.client.query(query)
            results = list(job.result())

            df = pd.DataFrame([{
                'package_name': r['package_name'],
                'year': r['year'],
                'month': r['month'],
                'country_code': r['country_code'],
                'download_count': r['download_count']
            } for r in results])

            output_file = self.output_dir / 'pypi_china_downloads.csv'
            df.to_csv(output_file, index=False)

            cost = (job.total_bytes_billed / 1e12) * 5
            print(f"  Extracted: {len(df)} records")
            print(f"  Cost: ${cost:.4f}")

            self.log_extraction('pypi', len(df), cost)
            return df

        except Exception as e:
            print(f"  Error: {e}")
            print(f"  Note: PyPI downloads may have data access restrictions")
            self.log_extraction('pypi', 0, 0, "FAILED")
            return pd.DataFrame()

    # =========================================================================
    # PHASE 9: ETHEREUM BLOCKCHAIN
    # =========================================================================
    def extract_ethereum_china(self):
        """
        Extract Ethereum activity (Chinese addresses/contracts)
        """
        print("\n" + "="*80)
        print("[9/9] EXTRACTING ETHEREUM BLOCKCHAIN")
        print("="*80)

        # Sample transaction patterns (full analysis would be expensive)
        query = """
        SELECT
            DATE(block_timestamp) as date,
            COUNT(*) as transaction_count,
            SUM(value) / 1e18 as total_eth_value,
            COUNT(DISTINCT from_address) as unique_senders
        FROM `bigquery-public-data.crypto_ethereum.transactions`
        WHERE DATE(block_timestamp) >= '2020-01-01'
            AND DATE(block_timestamp) < '2025-01-01'
        GROUP BY date
        ORDER BY date
        LIMIT 1000
        """

        print("\nQuerying Ethereum data (sample)...")
        try:
            job = self.client.query(query)
            results = list(job.result())

            df = pd.DataFrame([{
                'date': r['date'],
                'transaction_count': r['transaction_count'],
                'total_eth_value': float(r['total_eth_value']) if r['total_eth_value'] else 0,
                'unique_senders': r['unique_senders']
            } for r in results])

            output_file = self.output_dir / 'ethereum_activity_sample.csv'
            df.to_csv(output_file, index=False)

            cost = (job.total_bytes_billed / 1e12) * 5
            print(f"  Extracted: {len(df)} days")
            print(f"  Cost: ${cost:.4f}")
            print(f"  Note: This is a sample. Full Chinese address tracking would require additional filtering.")

            self.log_extraction('ethereum', len(df), cost)
            return df

        except Exception as e:
            print(f"  Error: {e}")
            self.log_extraction('ethereum', 0, 0, "FAILED")
            return pd.DataFrame()

    # =========================================================================
    # MAIN EXECUTION
    # =========================================================================
    def run_all_extractions(self):
        """
        Run all extractions in sequence
        """
        print("="*80)
        print("COMPREHENSIVE BIGQUERY DATA EXTRACTION")
        print("China Technology Analysis - Complete Dataset")
        print("="*80)
        print(f"\nStart time: {datetime.now()}")
        print(f"Output directory: {self.output_dir}")

        try:
            # Phase 1: Patents - Assignees
            df_assignees = self.extract_patent_assignees()

            # Phase 2: Patents - Citations
            df_citations = self.extract_patent_citations()

            # Phase 3: Patents - Inventors
            df_inventors = self.extract_patent_inventors()

            # Phase 4: Patents - Families
            df_families = self.extract_patent_families()

            # Phase 5: GitHub
            df_github = self.extract_github_chinese_companies()

            # Phase 6: Stack Overflow
            df_stackoverflow = self.extract_stackoverflow_china()

            # Phase 7: World Bank
            df_worldbank = self.extract_world_bank_indicators()

            # Phase 8: PyPI
            df_pypi = self.extract_pypi_downloads()

            # Phase 9: Ethereum
            df_ethereum = self.extract_ethereum_china()

            # Save log
            self.save_log()

            print("\n" + "="*80)
            print("EXTRACTION COMPLETE")
            print("="*80)
            print(f"\nEnd time: {datetime.now()}")
            print(f"Total cost: ${self.total_cost:.4f}")
            print(f"\nFiles saved to: {self.output_dir}/")
            print(f"  - patent_assignees_annual.csv")
            print(f"  - patent_citations_annual.csv")
            print(f"  - patent_inventors_annual.csv")
            print(f"  - patent_families_annual.csv")
            print(f"  - github_chinese_companies_2024.csv")
            print(f"  - stackoverflow_technology_adoption.csv")
            print(f"  - world_bank_china_indicators.csv")
            print(f"  - pypi_china_downloads.csv")
            print(f"  - ethereum_activity_sample.csv")
            print(f"  - extraction_log.json")

        except Exception as e:
            print(f"\n\nERROR during extraction: {e}")
            import traceback
            traceback.print_exc()
            self.save_log()

        return self.total_cost

if __name__ == "__main__":
    extractor = BigQueryExtractor()
    total_cost = extractor.run_all_extractions()

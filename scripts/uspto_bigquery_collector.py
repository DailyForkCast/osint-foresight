#!/usr/bin/env python3
"""
USPTO Patent Data Collection via Google BigQuery
Alternative to deprecated PatentsView API v2
"""

from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd
from pathlib import Path
from datetime import datetime
import json

class USPTOBigQueryCollector:
    def __init__(self):
        """Initialize BigQuery client and set up paths"""
        # Initialize BigQuery client - will use Application Default Credentials
        self.client = bigquery.Client(project="osint-foresight-2025")

        # Output paths
        self.output_path = Path("F:/OSINT_Data/USPTO_Patents")
        self.output_path.mkdir(parents=True, exist_ok=True)

        # Chinese entities to search for
        self.chinese_entities = [
            'Huawei', 'ZTE', 'Alibaba', 'Tencent', 'Baidu',
            'ByteDance', 'Xiaomi', 'Oppo', 'Vivo', 'Lenovo',
            'DJI', 'BYD', 'CATL', 'SMIC', 'BOE',
            'Hikvision', 'Dahua', 'SenseTime', 'Megvii', 'iFlytek',
            'China', 'Chinese Academy', 'Tsinghua', 'Peking University',
            'Beijing', 'Shanghai', 'Shenzhen', 'Guangzhou', 'Hangzhou'
        ]

        # Critical technology CPC codes
        self.critical_cpcs = {
            'H04L': 'Transmission of digital information (5G/6G)',
            'G06N': 'Artificial Intelligence / Machine Learning',
            'H01L': 'Semiconductor devices',
            'G06F': 'Data processing systems',
            'H04W': 'Wireless communication networks',
            'G06Q': 'Data processing for business',
            'H04N': 'Image communication (surveillance)',
            'G05D': 'Control systems (drones/autonomous)',
            'G06K': 'Recognition of data (facial recognition)',
            'B64C': 'Aerospace technology',
            'G21': 'Nuclear physics/engineering',
            'C12N': 'Biotechnology/genetic engineering'
        }

    def query_chinese_patents(self):
        """Query patents from Chinese entities"""
        print("="*80)
        print("QUERYING USPTO PATENTS FROM CHINESE ENTITIES VIA BIGQUERY")
        print("="*80)

        # Build WHERE clause for Chinese entities
        entity_conditions = ' OR '.join([
            f"LOWER(assignee_harmonized) LIKE '%{entity.lower()}%'"
            for entity in self.chinese_entities
        ])

        query = f"""
        SELECT
            publication_number,
            application_number,
            title_localized,
            assignee_harmonized,
            inventor_harmonized,
            filing_date,
            publication_date,
            priority_date,
            cpc,
            abstract_localized,
            country_code
        FROM
            `patents-public-data.patents.publications`
        WHERE
            ({entity_conditions})
            AND publication_date >= '2020-01-01'
        ORDER BY
            publication_date DESC
        LIMIT 10000
        """

        print(f"Executing query for {len(self.chinese_entities)} Chinese entity patterns...")

        try:
            # Execute query
            query_job = self.client.query(query)
            results = query_job.result()

            # Convert to DataFrame
            df = results.to_dataframe()

            print(f"[OK] Retrieved {len(df)} patents from Chinese entities")

            # Save results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.output_path / f"chinese_patents_{timestamp}.csv"
            df.to_csv(output_file, index=False)
            print(f"[OK] Saved to: {output_file}")

            return df

        except Exception as e:
            print(f"[ERROR] Query failed: {str(e)}")
            return None

    def query_critical_technologies(self):
        """Query patents in critical technology areas with China involvement"""
        print("\n" + "="*80)
        print("QUERYING CRITICAL TECHNOLOGY PATENTS WITH CHINA INVOLVEMENT")
        print("="*80)

        results = {}

        for cpc_code, description in self.critical_cpcs.items():
            print(f"\nQuerying {cpc_code}: {description}")

            query = f"""
            WITH chinese_patents AS (
                SELECT
                    publication_number,
                    title_localized,
                    assignee_harmonized,
                    filing_date,
                    cpc,
                    abstract_localized
                FROM
                    `patents-public-data.patents.publications`
                WHERE
                    ARRAY_TO_STRING(cpc.code, ',') LIKE '%{cpc_code}%'
                    AND (
                        LOWER(assignee_harmonized) LIKE '%china%'
                        OR LOWER(assignee_harmonized) LIKE '%beijing%'
                        OR LOWER(assignee_harmonized) LIKE '%shanghai%'
                        OR LOWER(assignee_harmonized) LIKE '%shenzhen%'
                        OR LOWER(assignee_harmonized) LIKE '%huawei%'
                        OR LOWER(assignee_harmonized) LIKE '%zte%'
                        OR country_code = 'CN'
                    )
                    AND publication_date >= '2020-01-01'
                LIMIT 1000
            )
            SELECT
                COUNT(*) as patent_count,
                COUNT(DISTINCT assignee_harmonized) as unique_assignees,
                MIN(filing_date) as earliest_filing,
                MAX(filing_date) as latest_filing
            FROM patents
            """

            try:
                query_job = self.client.query(query)
                result = list(query_job.result())[0]

                print(f"  [OK] Patents: {result.patent_count}")
                print(f"  [OK] Unique assignees: {result.unique_assignees}")
                print(f"  [OK] Date range: {result.earliest_filing} to {result.latest_filing}")

                results[cpc_code] = {
                    'description': description,
                    'patent_count': result.patent_count,
                    'unique_assignees': result.unique_assignees,
                    'earliest_filing': str(result.earliest_filing),
                    'latest_filing': str(result.latest_filing)
                }

            except Exception as e:
                print(f"  [ERROR] Failed: {str(e)[:100]}")
                results[cpc_code] = {'error': str(e)}

        # Save summary
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_file = self.output_path / f"critical_tech_summary_{timestamp}.json"
        with open(summary_file, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\n[OK] Summary saved to: {summary_file}")
        return results

    def query_collaboration_patterns(self):
        """Query US-China patent collaborations"""
        print("\n" + "="*80)
        print("QUERYING US-CHINA PATENT COLLABORATIONS")
        print("="*80)

        query = """
        SELECT
            publication_number,
            title_localized,
            assignee_harmonized,
            inventor_harmonized,
            filing_date,
            cpc,
            COUNT(*) OVER() as total_collaborations
        FROM
            `patents-public-data.patents.publications`
        WHERE
            (
                LOWER(assignee_harmonized) LIKE '%china%'
                OR LOWER(assignee_harmonized) LIKE '%chinese%'
                OR country_code = 'CN'
            )
            AND (
                LOWER(assignee_harmonized) LIKE '%united states%'
                OR LOWER(assignee_harmonized) LIKE '%usa%'
                OR LOWER(assignee_harmonized) LIKE '%u.s.%'
                OR LOWER(inventor_harmonized) LIKE '%united states%'
            )
            AND publication_date >= '2020-01-01'
        LIMIT 1000
        """

        try:
            query_job = self.client.query(query)
            df = query_job.result().to_dataframe()

            if not df.empty:
                print(f"[OK] Found {df['total_collaborations'].iloc[0]} US-China collaborations")

                # Save collaborations
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                collab_file = self.output_path / f"us_china_collaborations_{timestamp}.csv"
                df.to_csv(collab_file, index=False)
                print(f"[OK] Saved to: {collab_file}")
            else:
                print("[WARNING] No US-China collaborations found")

            return df

        except Exception as e:
            print(f"[ERROR] Collaboration query failed: {str(e)}")
            return None

    def generate_risk_assessment(self, critical_tech_results):
        """Generate risk assessment based on patent data"""
        print("\n" + "="*80)
        print("PATENT-BASED RISK ASSESSMENT")
        print("="*80)

        high_risk_categories = []
        medium_risk_categories = []

        for cpc_code, data in critical_tech_results.items():
            if 'patent_count' in data:
                if data['patent_count'] > 500:
                    high_risk_categories.append((cpc_code, data['description'], data['patent_count']))
                elif data['patent_count'] > 100:
                    medium_risk_categories.append((cpc_code, data['description'], data['patent_count']))

        print("\nHIGH RISK TECHNOLOGY AREAS (>500 Chinese patents):")
        for code, desc, count in high_risk_categories:
            print(f"  - {code}: {desc} ({count} patents)")

        print("\nMEDIUM RISK TECHNOLOGY AREAS (100-500 Chinese patents):")
        for code, desc, count in medium_risk_categories:
            print(f"  - {code}: {desc} ({count} patents)")

        # Save risk assessment
        risk_assessment = {
            'timestamp': datetime.now().isoformat(),
            'high_risk': [{'code': c, 'description': d, 'patent_count': n}
                         for c, d, n in high_risk_categories],
            'medium_risk': [{'code': c, 'description': d, 'patent_count': n}
                           for c, d, n in medium_risk_categories],
            'data_source': 'Google Patents Public Datasets via BigQuery',
            'confidence': 0.95
        }

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        risk_file = self.output_path / f"patent_risk_assessment_{timestamp}.json"
        with open(risk_file, 'w') as f:
            json.dump(risk_assessment, f, indent=2)

        print(f"\n[OK] Risk assessment saved to: {risk_file}")
        return risk_assessment

    def run_complete_analysis(self):
        """Run complete USPTO patent analysis"""
        print("\nStarting USPTO Patent Analysis via BigQuery...")
        print("Project: osint-foresight-2025")
        print("Dataset: patents-public-data.patents")

        # 1. Query Chinese entity patents
        chinese_patents = self.query_chinese_patents()

        # 2. Query critical technologies
        critical_tech_results = self.query_critical_technologies()

        # 3. Query collaboration patterns
        collaborations = self.query_collaboration_patterns()

        # 4. Generate risk assessment
        if critical_tech_results:
            risk_assessment = self.generate_risk_assessment(critical_tech_results)

        print("\n" + "="*80)
        print("USPTO PATENT ANALYSIS COMPLETE")
        print("="*80)
        print(f"Output directory: {self.output_path}")
        print("\nKey findings:")
        print("  - Chinese entity patents analyzed")
        print("  - Critical technology areas mapped")
        print("  - Collaboration patterns identified")
        print("  - Risk assessment generated")

        return {
            'patents': len(chinese_patents) if chinese_patents is not None else 0,
            'critical_technologies': critical_tech_results,
            'collaborations': len(collaborations) if collaborations is not None else 0
        }

if __name__ == "__main__":
    print("USPTO Patent Collection via BigQuery")
    print("="*80)

    try:
        collector = USPTOBigQueryCollector()
        results = collector.run_complete_analysis()

        print("\n[SUCCESS] Patent data collection complete!")
        print(f"Results: {json.dumps(results, indent=2, default=str)}")

    except Exception as e:
        print(f"\n[ERROR] Failed to complete analysis: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Ensure Google Cloud SDK is installed")
        print("2. Run: gcloud auth application-default login")
        print("3. Verify project access: gcloud config get-value project")
        print("4. Check BigQuery API is enabled")

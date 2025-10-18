#!/usr/bin/env python3
"""
USPTO Patent Data Collection via Google BigQuery - Fixed Version
Handles ARRAY and STRUCT fields properly
"""

from google.cloud import bigquery
import pandas as pd
from pathlib import Path
from datetime import datetime
import json

class USPTOBigQueryCollector:
    def __init__(self):
        """Initialize BigQuery client and set up paths"""
        # Initialize BigQuery client
        self.client = bigquery.Client(project="osint-foresight-2025")

        # Output paths
        self.output_path = Path("F:/OSINT_Data/USPTO_Patents")
        self.output_path.mkdir(parents=True, exist_ok=True)

        # Chinese entities to search for
        self.chinese_entities = [
            'Huawei', 'ZTE', 'Alibaba', 'Tencent', 'Baidu',
            'ByteDance', 'Xiaomi', 'Oppo', 'Vivo', 'Lenovo',
            'DJI', 'BYD', 'CATL', 'SMIC', 'BOE'
        ]

        # Critical technology CPC codes
        self.critical_cpcs = {
            'H04L': 'Transmission of digital information (5G/6G)',
            'G06N': 'Artificial Intelligence / Machine Learning',
            'H01L': 'Semiconductor devices',
            'G06F': 'Data processing systems',
            'H04W': 'Wireless communication networks'
        }

    def query_chinese_patents(self):
        """Query patents from Chinese entities - Fixed for ARRAY fields"""
        print("="*80)
        print("QUERYING USPTO PATENTS FROM CHINESE ENTITIES")
        print("="*80)

        # Fixed query handling ARRAY fields properly
        query = """
        SELECT
            publication_number,
            application_number,
            title,
            ARRAY_TO_STRING(assignee, ', ') as assignee_list,
            ARRAY_TO_STRING(inventor, ', ') as inventor_list,
            filing_date,
            publication_date,
            priority_date,
            ARRAY_TO_STRING(cpc, ', ') as cpc_codes,
            abstract,
            country_code
        FROM
            `patents-public-data.patents.publications`
        WHERE
            publication_date >= '2020-01-01'
            AND (
                country_code = 'CN'
                OR EXISTS(
                    SELECT 1 FROM UNNEST(assignee) AS a
                    WHERE LOWER(a) LIKE '%huawei%'
                       OR LOWER(a) LIKE '%zte%'
                       OR LOWER(a) LIKE '%alibaba%'
                       OR LOWER(a) LIKE '%tencent%'
                       OR LOWER(a) LIKE '%baidu%'
                       OR LOWER(a) LIKE '%bytedance%'
                       OR LOWER(a) LIKE '%xiaomi%'
                       OR LOWER(a) LIKE '%china%'
                       OR LOWER(a) LIKE '%chinese%'
                       OR LOWER(a) LIKE '%beijing%'
                       OR LOWER(a) LIKE '%shanghai%'
                       OR LOWER(a) LIKE '%shenzhen%'
                )
            )
        ORDER BY publication_date DESC
        LIMIT 5000
        """

        print("Executing query for Chinese entity patents...")

        try:
            query_job = self.client.query(query)
            results = query_job.result()
            df = results.to_dataframe()

            print(f"[OK] Retrieved {len(df)} patents from Chinese entities")

            if len(df) > 0:
                # Analyze top assignees
                top_assignees = df['assignee_list'].value_counts().head(10)
                print("\nTop 10 Chinese assignees:")
                for assignee, count in top_assignees.items():
                    if assignee:
                        print(f"  - {assignee[:50]}: {count} patents")

                # Save results
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = self.output_path / f"chinese_patents_{timestamp}.csv"
                df.to_csv(output_file, index=False)
                print(f"\n[OK] Saved {len(df)} patents to: {output_file}")

            return df

        except Exception as e:
            print(f"[ERROR] Query failed: {str(e)[:200]}")
            return None

    def query_critical_technologies(self):
        """Query patents in critical technology areas - Fixed for nested CPC field"""
        print("\n" + "="*80)
        print("QUERYING CRITICAL TECHNOLOGY PATENTS")
        print("="*80)

        results = {}

        for cpc_code, description in self.critical_cpcs.items():
            print(f"\nQuerying {cpc_code}: {description}")

            # Fixed query for nested CPC structure
            query = f"""
            SELECT
                COUNT(*) as patent_count,
                COUNT(DISTINCT ARRAY_TO_STRING(assignee, ', ')) as unique_assignees
            FROM
                `patents-public-data.patents.publications`
            WHERE
                publication_date >= '2020-01-01'
                AND EXISTS(
                    SELECT 1 FROM UNNEST(cpc) AS c
                    WHERE c.code LIKE '{cpc_code}%'
                )
                AND (
                    country_code = 'CN'
                    OR EXISTS(
                        SELECT 1 FROM UNNEST(assignee) AS a
                        WHERE LOWER(a) LIKE '%china%'
                           OR LOWER(a) LIKE '%chinese%'
                           OR LOWER(a) LIKE '%beijing%'
                           OR LOWER(a) LIKE '%shanghai%'
                           OR LOWER(a) LIKE '%huawei%'
                    )
                )
            """

            try:
                query_job = self.client.query(query)
                result = list(query_job.result())[0]

                print(f"  [OK] Patents: {result.patent_count}")
                print(f"  [OK] Unique assignees: {result.unique_assignees}")

                results[cpc_code] = {
                    'description': description,
                    'patent_count': result.patent_count,
                    'unique_assignees': result.unique_assignees
                }

            except Exception as e:
                print(f"  [ERROR] Failed: {str(e)[:100]}")
                results[cpc_code] = {'error': str(e)[:200]}

        # Save summary
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_file = self.output_path / f"critical_tech_summary_{timestamp}.json"
        with open(summary_file, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\n[OK] Summary saved to: {summary_file}")
        return results

    def query_recent_trends(self):
        """Query recent patent filing trends"""
        print("\n" + "="*80)
        print("QUERYING RECENT CHINESE PATENT TRENDS (2020-2025)")
        print("="*80)

        query = """
        SELECT
            EXTRACT(YEAR FROM publication_date) as year,
            EXTRACT(MONTH FROM publication_date) as month,
            COUNT(*) as patent_count,
            COUNT(DISTINCT ARRAY_TO_STRING(assignee, ', ')) as unique_assignees
        FROM
            `patents-public-data.patents.publications`
        WHERE
            publication_date >= '2020-01-01'
            AND (
                country_code = 'CN'
                OR EXISTS(
                    SELECT 1 FROM UNNEST(assignee) AS a
                    WHERE LOWER(a) LIKE '%china%'
                       OR LOWER(a) LIKE '%huawei%'
                       OR LOWER(a) LIKE '%zte%'
                )
            )
        GROUP BY year, month
        ORDER BY year DESC, month DESC
        LIMIT 100
        """

        try:
            query_job = self.client.query(query)
            df = query_job.result().to_dataframe()

            if not df.empty:
                print(f"[OK] Retrieved trend data for {len(df)} months")

                # Show recent months
                recent = df.head(6)
                print("\nRecent 6 months:")
                for _, row in recent.iterrows():
                    print(f"  {int(row['year'])}-{int(row['month']):02d}: {row['patent_count']} patents, {row['unique_assignees']} assignees")

                # Save trends
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                trends_file = self.output_path / f"chinese_patent_trends_{timestamp}.csv"
                df.to_csv(trends_file, index=False)
                print(f"\n[OK] Trends saved to: {trends_file}")

            return df

        except Exception as e:
            print(f"[ERROR] Trends query failed: {str(e)[:200]}")
            return None

    def generate_summary_report(self, chinese_patents, critical_tech_results, trends):
        """Generate comprehensive summary report"""
        print("\n" + "="*80)
        print("GENERATING SUMMARY REPORT")
        print("="*80)

        report = {
            'generated_at': datetime.now().isoformat(),
            'data_source': 'Google Patents Public Datasets via BigQuery',
            'chinese_patents_collected': len(chinese_patents) if chinese_patents is not None else 0,
            'critical_technologies': critical_tech_results,
            'trend_months_analyzed': len(trends) if trends is not None else 0
        }

        # Risk assessment
        high_risk = []
        medium_risk = []
        for code, data in critical_tech_results.items():
            if 'patent_count' in data:
                if data['patent_count'] > 1000:
                    high_risk.append(code)
                elif data['patent_count'] > 500:
                    medium_risk.append(code)

        report['risk_assessment'] = {
            'high_risk_categories': high_risk,
            'medium_risk_categories': medium_risk
        }

        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.output_path / f"patent_analysis_report_{timestamp}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"[OK] Summary report saved to: {report_file}")

        # Print summary
        print("\nKEY FINDINGS:")
        print(f"  - Chinese patents analyzed: {report['chinese_patents_collected']}")
        print(f"  - High risk technology areas: {len(high_risk)}")
        print(f"  - Medium risk technology areas: {len(medium_risk)}")
        print(f"  - Trend data: {report['trend_months_analyzed']} months")

        return report

    def run_complete_analysis(self):
        """Run complete USPTO patent analysis"""
        print("\nStarting USPTO Patent Analysis via BigQuery...")
        print("Project: osint-foresight-2025")
        print("Dataset: patents-public-data.patents")

        # 1. Query Chinese entity patents
        chinese_patents = self.query_chinese_patents()

        # 2. Query critical technologies
        critical_tech_results = self.query_critical_technologies()

        # 3. Query recent trends
        trends = self.query_recent_trends()

        # 4. Generate summary report
        report = self.generate_summary_report(chinese_patents, critical_tech_results, trends)

        print("\n" + "="*80)
        print("USPTO PATENT ANALYSIS COMPLETE")
        print("="*80)
        print(f"Output directory: {self.output_path}")

        return report

if __name__ == "__main__":
    print("USPTO Patent Collection via BigQuery - Fixed Version")
    print("="*80)

    try:
        collector = USPTOBigQueryCollector()
        report = collector.run_complete_analysis()

        print("\n[SUCCESS] Patent data collection complete!")

    except Exception as e:
        print(f"\n[ERROR] Failed to complete analysis: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Ensure Google Cloud SDK is installed")
        print("2. Run: gcloud auth application-default login")
        print("3. Verify project: osint-foresight-2025")
        print("4. Check BigQuery API is enabled")

#!/usr/bin/env python3
"""
BigQuery GH Archive Analysis
Query GitHub organizational activity via BigQuery public dataset
"""

import os
from google.cloud import bigquery
from datetime import datetime, timedelta
import json
from pathlib import Path

# Initialize BigQuery client
client = bigquery.Client(project='osint-foresight-2025')

# Output directory
output_dir = Path("C:/Projects/OSINT - Foresight/data/processed/github_bigquery")
output_dir.mkdir(parents=True, exist_ok=True)

# Target organizations
TARGET_ORGS = [
    # Chinese Tech
    'alibaba', 'alipay', 'ant-design', 'tencent', 'TencentARC',
    'baidu', 'PaddlePaddle', 'huawei', 'mindspore-ai', 'bytedance',
    # Chinese Research
    'THUDM', 'PKU-IDEA', 'CASIA-IVA-Lab', 'OpenGVLab',
    # Defense
    'lockheedmartin', 'raytheontech', 'northrop-grumman',
    # Semiconductors
    'intel', 'AMD', 'NVIDIA',
    # Strategic
    'tensorflow', 'pytorch', 'kubernetes', 'docker'
]

def query_org_activity_2024():
    """Query organizational activity for 2024"""
    print("\n" + "="*60)
    print("Querying GH Archive for organizational activity (2024)")
    print("="*60 + "\n")

    org_list = "', '".join(TARGET_ORGS)

    query = f"""
    SELECT
      org.login as organization,
      COUNT(*) as total_events,
      COUNTIF(type = 'PushEvent') as push_events,
      COUNTIF(type = 'ReleaseEvent') as release_events,
      COUNTIF(type = 'PullRequestEvent') as pull_request_events,
      COUNTIF(type = 'IssuesEvent') as issues_events,
      COUNTIF(type = 'WatchEvent') as watch_events,
      COUNTIF(type = 'ForkEvent') as fork_events,
      COUNT(DISTINCT repo.name) as unique_repos,
      COUNT(DISTINCT actor.login) as unique_contributors
    FROM `githubarchive.day.2024*`
    WHERE org.login IN ('{org_list}')
    GROUP BY organization
    ORDER BY total_events DESC
    """

    print(f"Executing query...")
    print(f"Target organizations: {len(TARGET_ORGS)}")

    try:
        query_job = client.query(query)
        results = list(query_job.result())

        print(f"✓ Query completed")
        print(f"  Bytes processed: {query_job.total_bytes_processed:,}")
        print(f"  Results: {len(results)} organizations\n")

        # Convert to list of dicts
        data = []
        for row in results:
            data.append({
                'organization': row.organization,
                'total_events': row.total_events,
                'push_events': row.push_events,
                'release_events': row.release_events,
                'pull_request_events': row.pull_request_events,
                'issues_events': row.issues_events,
                'watch_events': row.watch_events,
                'fork_events': row.fork_events,
                'unique_repos': row.unique_repos,
                'unique_contributors': row.unique_contributors
            })

        # Save results
        output_file = output_dir / f"org_activity_2024_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump({
                'query_date': datetime.now().isoformat(),
                'period': '2024-01-01 to 2024-12-31',
                'organizations': len(results),
                'bytes_processed': query_job.total_bytes_processed,
                'data': data
            }, f, indent=2)

        print(f"✓ Results saved: {output_file}\n")

        # Print top 10
        print("Top 10 Organizations by Activity (2024):")
        print("-" * 60)
        for row in data[:10]:
            print(f"  {row['organization']:20s}: {row['total_events']:8,} events, "
                  f"{row['push_events']:6,} commits, {row['release_events']:4,} releases")

        return data

    except Exception as e:
        print(f"✗ Error: {e}")
        return None


def query_chinese_tech_monthly():
    """Query Chinese tech companies' monthly activity trends"""
    print("\n" + "="*60)
    print("Querying Chinese Tech Monthly Trends (2024)")
    print("="*60 + "\n")

    chinese_orgs = ['alibaba', 'tencent', 'baidu', 'huawei', 'bytedance']
    org_list = "', '".join(chinese_orgs)

    query = f"""
    SELECT
      FORMAT_DATE('%Y-%m', PARSE_TIMESTAMP('%Y%m%d', CAST(_TABLE_SUFFIX AS STRING))) as month,
      org.login as organization,
      COUNT(*) as total_events,
      COUNTIF(type = 'PushEvent') as commits,
      COUNTIF(type = 'ReleaseEvent') as releases
    FROM `githubarchive.day.2024*`
    WHERE org.login IN ('{org_list}')
    GROUP BY month, organization
    ORDER BY month, total_events DESC
    """

    print(f"Executing query for: {', '.join(chinese_orgs)}")

    try:
        query_job = client.query(query)
        results = list(query_job.result())

        print(f"✓ Query completed")
        print(f"  Bytes processed: {query_job.total_bytes_processed:,}")
        print(f"  Results: {len(results)} month-org pairs\n")

        # Convert to list of dicts
        data = []
        for row in results:
            data.append({
                'month': row.month,
                'organization': row.organization,
                'total_events': row.total_events,
                'commits': row.commits,
                'releases': row.releases
            })

        # Save results
        output_file = output_dir / f"chinese_tech_monthly_2024_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump({
                'query_date': datetime.now().isoformat(),
                'period': '2024 (monthly breakdown)',
                'organizations': chinese_orgs,
                'bytes_processed': query_job.total_bytes_processed,
                'data': data
            }, f, indent=2)

        print(f"✓ Results saved: {output_file}\n")

        # Print summary
        print("Chinese Tech Activity by Month (2024):")
        print("-" * 60)
        for row in data[:20]:  # First 20 rows
            print(f"  {row['month']} - {row['organization']:15s}: {row['total_events']:6,} events")

        return data

    except Exception as e:
        print(f"✗ Error: {e}")
        return None


def query_tech_repos_by_keywords():
    """Query repositories by technology keywords"""
    print("\n" + "="*60)
    print("Querying Technology Repositories (Quantum & AI)")
    print("="*60 + "\n")

    # Note: This queries the github_repos dataset, not githubarchive
    # Simplified query due to dataset structure
    query = """
    SELECT
      repo.name as repo_name,
      COUNT(*) as activity_count,
      COUNTIF(type = 'PushEvent') as commits,
      COUNTIF(type = 'ReleaseEvent') as releases,
      COUNTIF(type = 'WatchEvent') as stars
    FROM `githubarchive.day.202410*`
    WHERE (
      LOWER(repo.name) LIKE '%quantum%'
      OR LOWER(repo.name) LIKE '%qiskit%'
      OR LOWER(repo.name) LIKE '%cirq%'
      OR LOWER(repo.name) LIKE '%machine-learning%'
      OR LOWER(repo.name) LIKE '%deep-learning%'
    )
    GROUP BY repo_name
    HAVING activity_count > 10
    ORDER BY activity_count DESC
    LIMIT 100
    """

    print(f"Executing query for tech repositories (October 2024)...")

    try:
        query_job = client.query(query)
        results = list(query_job.result())

        print(f"✓ Query completed")
        print(f"  Bytes processed: {query_job.total_bytes_processed:,}")
        print(f"  Results: {len(results)} repositories\n")

        # Convert to list of dicts
        data = []
        for row in results:
            data.append({
                'repo_name': row.repo_name,
                'activity_count': row.activity_count,
                'commits': row.commits,
                'releases': row.releases,
                'stars': row.stars
            })

        # Save results
        output_file = output_dir / f"tech_repos_oct2024_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump({
                'query_date': datetime.now().isoformat(),
                'period': 'October 2024',
                'keywords': ['quantum', 'qiskit', 'cirq', 'machine-learning', 'deep-learning'],
                'bytes_processed': query_job.total_bytes_processed,
                'data': data
            }, f, indent=2)

        print(f"✓ Results saved: {output_file}\n")

        # Print top 20
        print("Top 20 Technology Repositories (Oct 2024):")
        print("-" * 60)
        for row in data[:20]:
            print(f"  {row['repo_name']:50s}: {row['activity_count']:5,} events")

        return data

    except Exception as e:
        print(f"✗ Error: {e}")
        return None


def generate_summary():
    """Generate summary of BigQuery analysis"""
    print("\n" + "="*60)
    print("BIGQUERY GITHUB ANALYSIS SUMMARY")
    print("="*60 + "\n")

    # List all output files
    output_files = list(output_dir.glob("*.json"))

    print(f"Output files generated: {len(output_files)}")
    for f in output_files:
        size = f.stat().st_size / 1024  # KB
        print(f"  - {f.name} ({size:.1f} KB)")

    print(f"\nData saved to: {output_dir}")
    print("="*60 + "\n")


def main():
    """Main execution"""
    print("\n" + "="*60)
    print("BIGQUERY GH ARCHIVE ANALYSIS")
    print("="*60)
    print(f"Project: osint-foresight-2025")
    print(f"Output: {output_dir}\n")

    # Run queries
    print("Running 3 analysis queries...\n")

    # Query 1: Organizational activity 2024
    org_activity = query_org_activity_2024()

    # Query 2: Chinese tech monthly trends
    chinese_trends = query_chinese_tech_monthly()

    # Query 3: Technology repositories
    tech_repos = query_tech_repos_by_keywords()

    # Generate summary
    generate_summary()

    print("✓ BigQuery analysis complete!")


if __name__ == "__main__":
    main()

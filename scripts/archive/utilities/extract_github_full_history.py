#!/usr/bin/env python3
"""
Extract full GitHub Archive history for Chinese tech companies
2011-2025 (all available years)
"""

from google.cloud import bigquery
import pandas as pd
from pathlib import Path
import json
from datetime import datetime

def extract_github_full_history():
    """
    Extract GitHub activity for Chinese tech companies across all years
    """
    print("="*80)
    print("GITHUB ARCHIVE - FULL HISTORY EXTRACTION")
    print("="*80)

    client = bigquery.Client()
    output_dir = Path("data/bigquery_comprehensive")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Chinese tech companies
    companies = [
        'huawei', 'alibaba', 'tencent', 'bytedance', 'baidu',
        'xiaomi', 'zte', 'dji', 'meituan', 'pinduoduo',
        'jd', 'netease', 'bilibili', 'kuaishou'
    ]

    # Get all available month tables
    dataset_ref = "githubarchive.month"
    dataset = client.get_dataset(dataset_ref)
    tables = list(client.list_tables(dataset))

    # Extract YYYYMM from table names and sort
    available_months = sorted([t.table_id for t in tables if len(t.table_id) == 6 and t.table_id.isdigit()])

    print(f"\nTotal months available: {len(available_months)}")
    print(f"Range: {available_months[0]} - {available_months[-1]}")
    print(f"\nExtracting data for {len(companies)} companies...")

    all_data = []
    total_cost = 0
    failed_months = []

    for month in available_months:
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

            print(f"  [{month}] Querying...", end='', flush=True)
            job = client.query(query)
            results = list(job.result())

            month_data = [{
                'month': r['month'],
                'repo_name': r['repo_name'],
                'event_type': r['event_type'],
                'event_count': r['event_count']
            } for r in results]

            all_data.extend(month_data)

            cost = (job.total_bytes_billed / 1e12) * 5
            total_cost += cost

            print(f" {len(results):,} records, ${cost:.4f}")

            # Save checkpoint every 12 months
            if len(all_data) > 0 and (available_months.index(month) + 1) % 12 == 0:
                checkpoint_file = output_dir / f'github_checkpoint_{month}.csv'
                df_checkpoint = pd.DataFrame(all_data)
                df_checkpoint.to_csv(checkpoint_file, index=False)
                print(f"    Checkpoint saved: {len(all_data):,} records total")

        except Exception as e:
            print(f" ERROR: {str(e)[:100]}")
            failed_months.append(month)
            continue

    # Save final data
    if len(all_data) > 0:
        df = pd.DataFrame(all_data)
        output_file = output_dir / 'github_chinese_companies_full_history.csv'
        df.to_csv(output_file, index=False)

        # Save summary
        summary = {
            'extraction_date': datetime.now().isoformat(),
            'total_records': len(df),
            'months_extracted': len(available_months) - len(failed_months),
            'months_failed': len(failed_months),
            'failed_months': failed_months,
            'date_range': f"{available_months[0]}-{available_months[-1]}",
            'total_cost_usd': round(total_cost, 4),
            'companies': companies,
            'unique_repos': df['repo_name'].nunique() if len(df) > 0 else 0,
            'unique_event_types': df['event_type'].nunique() if len(df) > 0 else 0
        }

        with open(output_dir / 'github_extraction_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)

        print("\n" + "="*80)
        print("EXTRACTION COMPLETE")
        print("="*80)
        print(f"\nTotal records: {len(df):,}")
        print(f"Unique repos: {df['repo_name'].nunique():,}")
        print(f"Unique event types: {df['event_type'].nunique()}")
        print(f"Months extracted: {len(available_months) - len(failed_months)}/{len(available_months)}")
        print(f"Total cost: ${total_cost:.4f}")
        print(f"\nSaved to: {output_file}")
        print(f"Summary: {output_dir / 'github_extraction_summary.json'}")

        return df, total_cost
    else:
        print("\nNo data extracted")
        return None, 0

if __name__ == "__main__":
    df, cost = extract_github_full_history()

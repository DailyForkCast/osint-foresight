#!/usr/bin/env python3
"""
Concurrent monitoring of all three data collection processes:
1. Kaggle arXiv processing
2. GitHub organizational activity collection
3. BigQuery GH Archive analysis
"""

import sqlite3
import json
import time
from pathlib import Path
from datetime import datetime
import os

def check_kaggle_status():
    """Check Kaggle arXiv processing status"""
    db_path = "C:/Projects/OSINT - Foresight/data/kaggle_arxiv_processing.db"

    if not Path(db_path).exists():
        return {'status': 'not_started', 'papers': 0, 'progress': 0}

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        papers = cursor.execute("SELECT COUNT(*) FROM kaggle_arxiv_papers").fetchone()[0]
        tech_count = cursor.execute("SELECT COUNT(*) FROM kaggle_arxiv_technology").fetchone()[0]
        conn.close()

        progress = (papers / 2300000) * 100
        return {
            'status': 'processing' if papers < 2300000 else 'complete',
            'papers': papers,
            'tech_classifications': tech_count,
            'progress': progress,
            'remaining': 2300000 - papers
        }
    except:
        return {'status': 'error', 'papers': 0, 'progress': 0}


def check_github_status():
    """Check GitHub collector status"""
    db_paths = [
        "C:/Projects/OSINT - Foresight/data/github_metadata.db",
        "C:/Projects/OSINT - Foresight/data/github_activity.db"
    ]

    for db_path in db_paths:
        if Path(db_path).exists():
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                orgs = cursor.execute("SELECT COUNT(*) FROM github_organizations").fetchone()[0]
                repos = cursor.execute("SELECT COUNT(*) FROM github_repositories").fetchone()[0]
                conn.close()

                return {
                    'status': 'collecting',
                    'organizations': orgs,
                    'repositories': repos,
                    'progress': (orgs / 41) * 100 if orgs < 41 else 100,
                    'database': db_path
                }
            except:
                pass

    return {'status': 'not_started', 'organizations': 0, 'repositories': 0, 'progress': 0}


def check_bigquery_status():
    """Check BigQuery analysis results"""
    output_dir = Path("C:/Projects/OSINT - Foresight/data/processed/github_bigquery")

    if not output_dir.exists():
        return {'status': 'not_started', 'files': 0}

    json_files = list(output_dir.glob("*.json"))
    total_size = sum(f.stat().st_size for f in json_files)

    if len(json_files) > 0:
        # Read latest file to get info
        latest = max(json_files, key=lambda f: f.stat().st_mtime)
        try:
            with open(latest) as f:
                data = json.load(f)
                return {
                    'status': 'complete',
                    'files': len(json_files),
                    'total_size_kb': total_size / 1024,
                    'latest_query': latest.name,
                    'bytes_processed': data.get('bytes_processed', 0)
                }
        except:
            pass

    return {'status': 'processing', 'files': len(json_files)}


def print_status():
    """Print combined status of all three processes"""
    print("\n" + "="*80)
    print("CONCURRENT DATA COLLECTION STATUS")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")

    # Kaggle arXiv
    kaggle = check_kaggle_status()
    print("1. KAGGLE ARXIV PROCESSING")
    print("-" * 80)
    if kaggle['status'] == 'processing':
        print(f"   Status: Processing - {kaggle['progress']:.1f}% complete")
        print(f"   Papers: {kaggle['papers']:,} / 2,300,000")
        print(f"   Remaining: {kaggle['remaining']:,} papers")
        print(f"   Tech Classifications: {kaggle['tech_classifications']:,}")
    elif kaggle['status'] == 'complete':
        print(f"   Status: COMPLETE")
        print(f"   Total Papers: {kaggle['papers']:,}")
    else:
        print(f"   Status: {kaggle['status']}")

    # GitHub Collection
    github = check_github_status()
    print(f"\n2. GITHUB ORGANIZATIONAL ACTIVITY")
    print("-" * 80)
    if github['status'] == 'collecting':
        print(f"   Status: Collecting - {github['progress']:.1f}% complete")
        print(f"   Organizations: {github['organizations']} / 41")
        print(f"   Repositories: {github['repositories']:,}")
        print(f"   Database: {Path(github['database']).name}")
    else:
        print(f"   Status: {github['status']}")

    # BigQuery Analysis
    bigquery = check_bigquery_status()
    print(f"\n3. BIGQUERY GH ARCHIVE ANALYSIS")
    print("-" * 80)
    if bigquery['status'] == 'complete':
        print(f"   Status: COMPLETE")
        print(f"   Query Results: {bigquery['files']} files")
        print(f"   Total Size: {bigquery['total_size_kb']:.1f} KB")
        print(f"   Bytes Processed: {bigquery.get('bytes_processed', 0):,}")
        print(f"   Latest: {bigquery.get('latest_query', 'N/A')}")
    elif bigquery['status'] == 'processing':
        print(f"   Status: Processing")
        print(f"   Files: {bigquery['files']}")
    else:
        print(f"   Status: {bigquery['status']}")

    # Overall progress
    print(f"\n" + "="*80)
    overall = []
    if kaggle['status'] == 'complete':
        overall.append("Kaggle: DONE")
    elif kaggle['status'] == 'processing':
        overall.append(f"Kaggle: {kaggle['progress']:.0f}%")

    if github['status'] == 'collecting':
        overall.append(f"GitHub: {github['organizations']}/41 orgs")

    if bigquery['status'] == 'complete':
        overall.append("BigQuery: DONE")

    print(f"Overall Progress: {' | '.join(overall)}")
    print("="*80 + "\n")


def monitor_loop(interval=30, duration=300):
    """Monitor all processes for specified duration"""
    start_time = time.time()
    iteration = 0

    while time.time() - start_time < duration:
        iteration += 1
        print(f"\n{'#'*80}")
        print(f"# Monitoring Iteration {iteration}")
        print(f"{'#'*80}")

        print_status()

        # Check if all complete
        kaggle = check_kaggle_status()
        github = check_github_status()
        bigquery = check_bigquery_status()

        if (kaggle['status'] == 'complete' and
            github['progress'] >= 100 and
            bigquery['status'] == 'complete'):
            print("\n*** ALL PROCESSES COMPLETE! ***\n")
            break

        if time.time() - start_time < duration:
            print(f"Next update in {interval} seconds...\n")
            time.sleep(interval)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--loop":
        # Continuous monitoring mode
        monitor_loop(interval=30, duration=3600)  # 1 hour
    else:
        # Single status check
        print_status()

#!/usr/bin/env python3
"""
BigQuery Quota Checker
Tests if BigQuery quota is available and optionally resumes patent expansion
Run weekly via Task Scheduler
"""

import sys
from pathlib import Path
from datetime import datetime
from google.cloud import bigquery

def check_quota():
    """
    Test BigQuery quota with a minimal query
    Returns True if quota available, False if exceeded
    """
    try:
        client = bigquery.Client()

        # Minimal test query (scans very little data)
        test_query = """
        SELECT COUNT(*) as total
        FROM `patents-public-data.patents.publications`
        WHERE publication_date = 20250101
        LIMIT 1
        """

        print(f"[{datetime.now()}] Testing BigQuery quota...")
        query_job = client.query(test_query)
        result = query_job.result()

        # If we get here, quota is available
        print(f"✅ BigQuery quota available!")
        print(f"   Project: {client.project}")
        print(f"   Test query succeeded")
        return True

    except Exception as e:
        error_str = str(e)
        if "quotaExceeded" in error_str or "quota" in error_str.lower():
            print(f"❌ BigQuery quota still exceeded")
            print(f"   Error: {error_str[:200]}")
            return False
        else:
            print(f"⚠️  Other error (not quota): {error_str}")
            return False

def main():
    """Main function"""

    log_file = Path("logs/bigquery_quota_check.log")
    log_file.parent.mkdir(exist_ok=True)

    # Run quota check
    quota_available = check_quota()

    # Log result
    with open(log_file, 'a', encoding='utf-8') as f:
        timestamp = datetime.now().isoformat()
        status = "AVAILABLE" if quota_available else "EXCEEDED"
        f.write(f"{timestamp},{status}\n")

    if quota_available:
        print("\n" + "="*80)
        print("QUOTA AVAILABLE - You can resume patent expansion!")
        print("="*80)
        print("\nTo resume patent expansion, run:")
        print('  python "scripts/expand_patents_81_countries.py"')
        print("\nOr uncomment the auto-resume code below to run automatically.")
        print("="*80)

        # OPTIONAL: Auto-resume patent expansion
        # Uncomment these lines to automatically restart when quota is available
        # import subprocess
        # print("\n🚀 Auto-resuming patent expansion...")
        # subprocess.Popen([
        #     sys.executable,
        #     "scripts/expand_patents_81_countries.py"
        # ])

    else:
        print("\nQuota still exceeded. Will check again next week.")
        print(f"Log: {log_file}")

    return 0 if quota_available else 1

if __name__ == "__main__":
    sys.exit(main())

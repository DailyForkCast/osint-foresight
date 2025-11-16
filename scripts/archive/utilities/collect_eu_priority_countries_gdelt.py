"""
EU Priority Countries GDELT Collection (2020-2025)
Comprehensive collection for multi-country trade pattern validation

Collection Strategy:
- Priority 1 (HIGH): Greece, Slovakia (identical patterns to Lithuania)
- Priority 2 (MEDIUM): Finland, Sweden, Denmark, Netherlands, Ireland, Spain
- Time period: 2020-01-01 to 2025-12-31
- Query: (Actor1CountryCode = X OR Actor2CountryCode = X) AND (Actor1CountryCode = 'CHN' OR Actor2CountryCode = 'CHN')
"""

import subprocess
import json
import time
import sys
from datetime import datetime
from pathlib import Path

# Set UTF-8 encoding for output
sys.stdout.reconfigure(encoding='utf-8')

# Priority countries based on trade analysis
PRIORITY_COUNTRIES = {
    'HIGH': [
        {'code': 'GRC', 'name': 'Greece', 'reason': '-88% exports, procurement cessation'},
        {'code': 'SVK', 'name': 'Slovakia', 'reason': '-90% exports, identical to Lithuania'},
    ],
    'MEDIUM': [
        {'code': 'FIN', 'name': 'Finland', 'reason': '-69% exports'},
        {'code': 'SWE', 'name': 'Sweden', 'reason': '-69% exports'},
        {'code': 'DNK', 'name': 'Denmark', 'reason': '-56% exports'},
        {'code': 'NLD', 'name': 'Netherlands', 'reason': '-54% exports'},
        {'code': 'IRL', 'name': 'Ireland', 'reason': '-53% exports, procurement decrease'},
        {'code': 'ESP', 'name': 'Spain', 'reason': '-25% exports, -68% procurement'},
    ],
    'REFERENCE': [
        {'code': 'LTU', 'name': 'Lithuania', 'reason': 'Already collected (Jul-Dec 2021 only) - EXPAND to full 2020-2025'},
    ]
}

# Date ranges - collect by year to manage query size
DATE_RANGES = [
    ('20200101', '20201231', '2020'),
    ('20210101', '20211231', '2021'),
    ('20220101', '20221231', '2022'),
    ('20230101', '20231231', '2023'),
    ('20240101', '20241231', '2024'),
    ('20250101', '20251231', '2025'),
]

def run_collection(country_code, country_name, start_date, end_date, year):
    """
    Run GDELT collection for one country-year combination
    """
    print(f"\n{'='*100}")
    print(f"COLLECTING: {country_name} ({country_code}) - {year}")
    print(f"Date Range: {start_date} to {end_date}")
    print(f"{'='*100}\n")

    # Build command
    cmd = [
        'python',
        'scripts/collectors/gdelt_eu_china_bilateral_collector.py',
        '--country', country_code,
        '--start-date', start_date,
        '--end-date', end_date,
        '--db', 'F:/OSINT_WAREHOUSE/osint_master.db'
    ]

    # Run collection
    start_time = time.time()
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=1800  # 30 minute timeout per collection
        )

        elapsed = time.time() - start_time

        print(f"\n{'-'*100}")
        print(f"Collection completed in {elapsed:.1f} seconds")
        print(f"{'-'*100}\n")

        if result.returncode == 0:
            print("[SUCCESS]")
            # Try to extract stats from output
            if 'events collected' in result.stdout.lower():
                print(result.stdout[-500:])  # Last 500 chars with summary
        else:
            print(f"[WARNING] Non-zero return code: {result.returncode}")
            print(f"STDOUT: {result.stdout[-500:]}")
            print(f"STDERR: {result.stderr[-500:]}")

        return {
            'country': country_name,
            'code': country_code,
            'year': year,
            'start_date': start_date,
            'end_date': end_date,
            'success': result.returncode == 0,
            'elapsed_seconds': elapsed,
            'stdout': result.stdout[-1000:],
            'stderr': result.stderr[-1000:] if result.stderr else None
        }

    except subprocess.TimeoutExpired:
        print(f"[TIMEOUT] Collection exceeded 30 minutes")
        return {
            'country': country_name,
            'code': country_code,
            'year': year,
            'success': False,
            'error': 'Timeout after 30 minutes'
        }
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return {
            'country': country_name,
            'code': country_code,
            'year': year,
            'success': False,
            'error': str(e)
        }

def main():
    """
    Main collection orchestrator
    """
    print("="*100)
    print("EU PRIORITY COUNTRIES GDELT COLLECTION (2020-2025)")
    print("="*100)
    print()
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Collection summary
    print("Collection Plan:")
    print(f"  Time Period: 2020-2025 (6 years)")
    print(f"  Countries: {sum(len(countries) for countries in PRIORITY_COUNTRIES.values())}")
    print(f"  Total Collections: {sum(len(countries) for countries in PRIORITY_COUNTRIES.values()) * len(DATE_RANGES)}")
    print()

    for priority, countries in PRIORITY_COUNTRIES.items():
        print(f"  {priority} Priority: {len(countries)} countries")
        for country in countries:
            print(f"    - {country['name']} ({country['code']}): {country['reason']}")
    print()

    # Auto-proceed for automated execution
    # input("Press ENTER to begin collection (or Ctrl+C to cancel)...")
    print("Auto-proceeding with collection...")
    print()

    # Track results
    all_results = []
    total_collections = 0
    successful_collections = 0
    failed_collections = 0

    # Collect by priority
    for priority in ['HIGH', 'MEDIUM', 'REFERENCE']:
        countries = PRIORITY_COUNTRIES.get(priority, [])

        if not countries:
            continue

        print(f"\n{'#'*100}")
        print(f"PRIORITY: {priority}")
        print(f"{'#'*100}\n")

        for country in countries:
            country_code = country['code']
            country_name = country['name']

            print(f"\n{'='*100}")
            print(f"COUNTRY: {country_name} ({country_code})")
            print(f"Reason: {country['reason']}")
            print(f"{'='*100}\n")

            for start_date, end_date, year in DATE_RANGES:
                result = run_collection(country_code, country_name, start_date, end_date, year)
                all_results.append(result)
                total_collections += 1

                if result['success']:
                    successful_collections += 1
                else:
                    failed_collections += 1

                # Progress update
                print(f"\nProgress: {total_collections} collections, {successful_collections} successful, {failed_collections} failed\n")

                # Brief pause between collections
                time.sleep(2)

            # Longer pause between countries
            print(f"\n{country_name} complete. Pausing 10 seconds before next country...")
            time.sleep(10)

        # Save checkpoint after each priority level
        checkpoint_file = f"analysis/gdelt_collection_checkpoint_{priority}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(checkpoint_file, 'w') as f:
            json.dump(all_results, f, indent=2)
        print(f"\n[CHECKPOINT] Saved: {checkpoint_file}\n")

    # Final summary
    print("\n" + "="*100)
    print("COLLECTION COMPLETE")
    print("="*100)
    print()
    print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print(f"Total Collections: {total_collections}")
    print(f"Successful: {successful_collections}")
    print(f"Failed: {failed_collections}")
    print(f"Success Rate: {successful_collections/total_collections*100:.1f}%")
    print()

    # Save final results
    results_file = f"analysis/gdelt_collection_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w') as f:
        json.dump({
            'summary': {
                'total_collections': total_collections,
                'successful': successful_collections,
                'failed': failed_collections,
                'success_rate': successful_collections/total_collections
            },
            'results': all_results
        }, f, indent=2)

    print(f"Results saved to: {results_file}")
    print()

    # List failed collections for retry
    if failed_collections > 0:
        print("Failed collections (for manual retry):")
        for result in all_results:
            if not result['success']:
                print(f"  - {result['country']} ({result['code']}) {result['year']}")

if __name__ == '__main__':
    main()

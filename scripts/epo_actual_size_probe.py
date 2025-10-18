#!/usr/bin/env python3
"""
EPO Actual Database Size Probe
Use specific queries to find actual database scope beyond 10,000 limit
"""

import requests
import json
import time
from pathlib import Path
from datetime import datetime

def probe_actual_epo_size():
    """Find actual EPO database size using targeted queries"""

    # Load authentication
    auth_config_path = Path("C:/Projects/OSINT - Foresight/config/patent_auth.json")
    with open(auth_config_path, 'r') as f:
        config = json.load(f)

    access_token = config['epo_ops']['access_token']

    # Setup session
    session = requests.Session()
    session.headers.update({
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json',
        'User-Agent': 'OSINT-Research-System/1.0'
    })

    print("=" * 60)
    print("EPO Actual Database Size Probe")
    print("Finding real database scope beyond 10,000 API limit")
    print("=" * 60)

    search_url = "https://ops.epo.org/3.2/rest-services/published-data/search"

    # Targeted queries to find actual scope
    scope_queries = [
        # Try very specific queries that should have < 10,000 results
        ('txt="patent cooperation treaty" AND pd=2023', 'PCT 2023 specific'),
        ('txt="quantum computing" AND pa=IBM AND pd=2023', 'IBM quantum 2023'),
        ('txt="5G" AND pa=huawei AND pd=2022', 'Huawei 5G 2022'),
        ('txt="artificial intelligence" AND pa=google AND pd=2023', 'Google AI 2023'),

        # Year-specific queries
        ('pd=2023', 'All patents 2023'),
        ('pd=2022', 'All patents 2022'),
        ('pd=2021', 'All patents 2021'),
        ('pd=2020', 'All patents 2020'),

        # Try broad but constrained queries
        ('pa=china AND pd=2023', 'China patents 2023'),
        ('pa=united AND pd=2023', 'US patents 2023'),
        ('pa=samsung AND pd=2023', 'Samsung 2023'),

        # Technology + year combinations
        ('txt=semiconductor AND pd=2023', 'Semiconductor 2023'),
        ('txt=battery AND pd=2023', 'Battery 2023'),
        ('txt=AI AND pd=2023', 'AI 2023 short'),

        # Very specific technical terms
        ('txt="machine learning algorithm"', 'ML algorithms'),
        ('txt="quantum entanglement"', 'Quantum entanglement'),
        ('txt="5G network infrastructure"', '5G infrastructure'),
        ('txt="lithium ion battery"', 'Lithium batteries'),

        # Specific company + technology
        ('pa=microsoft AND txt=cloud', 'Microsoft cloud'),
        ('pa=tesla AND txt=battery', 'Tesla battery'),
        ('pa=nvidia AND txt=gpu', 'NVIDIA GPU'),
    ]

    results = {
        'probe_time': datetime.now().isoformat(),
        'actual_counts': {},
        'quota_usage': [],
        'max_found': 0,
        'under_10k_results': [],
        'database_scope_estimate': None
    }

    for i, (query, description) in enumerate(scope_queries, 1):
        print(f"\n{i:2d}. {description}")
        print(f"    Query: {query}")

        try:
            params = {
                'q': query,
                'Range': '1-1'  # Just get count
            }

            response = session.get(search_url, params=params, timeout=15)
            print(f"    Status: {response.status_code}")

            # Track quota
            if 'x-registeredquotaperweek-used' in response.headers:
                quota_used = int(response.headers['x-registeredquotaperweek-used'])
                results['quota_usage'].append(quota_used)

            if response.status_code == 200:
                data = response.json()

                # Parse total count
                total_found = 0
                if 'ops:world-patent-data' in data:
                    world_data = data['ops:world-patent-data']
                    if 'ops:biblio-search' in world_data:
                        biblio_search = world_data['ops:biblio-search']
                        if '@total-result-count' in biblio_search:
                            total_found = int(biblio_search['@total-result-count'])

                print(f"    Found: {total_found:,} patents")

                results['actual_counts'][description] = {
                    'query': query,
                    'count': total_found
                }

                # Track results under 10k (these are actual counts)
                if total_found < 10000:
                    results['under_10k_results'].append({
                        'description': description,
                        'query': query,
                        'count': total_found
                    })

                if total_found > results['max_found']:
                    results['max_found'] = total_found

                time.sleep(1)

            else:
                print(f"    Error: {response.text[:100]}")

        except Exception as e:
            print(f"    Exception: {e}")

    # Analysis
    print("\n" + "=" * 60)
    print("ACTUAL DATABASE SIZE ANALYSIS")
    print("=" * 60)

    # Show results under 10k (actual counts)
    if results['under_10k_results']:
        print("Actual counts (under API limit):")
        for result in sorted(results['under_10k_results'], key=lambda x: x['count'], reverse=True):
            print(f"  {result['description']}: {result['count']:,}")

        # Estimate based on specific year data
        year_counts = [r for r in results['under_10k_results'] if 'All patents' in r['description']]
        if year_counts:
            total_recent = sum(r['count'] for r in year_counts)
            years_covered = len(year_counts)
            print(f"\nRecent {years_covered} years total: {total_recent:,} patents")

            # Estimate total database (assuming 20+ years of data)
            estimated_total = total_recent * (25 / years_covered)  # Rough 25-year estimate
            results['database_scope_estimate'] = int(estimated_total)
            print(f"Estimated total database size: ~{estimated_total:,.0f} patents")

    # Show all results that hit 10k limit (incomplete)
    hit_limit = [desc for desc, data in results['actual_counts'].items() if data['count'] >= 10000]
    if hit_limit:
        print(f"\nQueries hitting 10,000 limit (actual count unknown):")
        for desc in hit_limit:
            print(f"  {desc}: 10,000+ (truncated)")

    # Quota analysis
    if results['quota_usage']:
        current_quota = results['quota_usage'][-1]
        weekly_limit = 4 * 1024 * 1024 * 1024  # 4GB
        remaining = weekly_limit - current_quota

        print(f"\nQuota status:")
        print(f"  Used: {current_quota:,} bytes ({current_quota/1024/1024:.1f} MB)")
        print(f"  Remaining: {remaining:,} bytes ({remaining/1024/1024/1024:.2f} GB)")

    # Save results
    output_dir = Path("F:/OSINT_DATA/epo_database_analysis")
    output_dir.mkdir(parents=True, exist_ok=True)

    results_file = output_dir / f"actual_size_probe_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nDetailed analysis saved to: {results_file}")

    return results

if __name__ == "__main__":
    probe_actual_epo_size()

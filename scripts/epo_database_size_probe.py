#!/usr/bin/env python3
"""
EPO Database Size Estimation
Probe the EPO database to estimate total size and scope
"""

import requests
import json
import time
from pathlib import Path
from datetime import datetime

def probe_epo_database_size():
    """Probe EPO database to estimate total size"""

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
    print("EPO Database Size Estimation")
    print(f"Analysis time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    search_url = "https://ops.epo.org/3.2/rest-services/published-data/search"

    # Probe queries to estimate database scope
    probe_queries = [
        # Total database probes
        ('txt=*', 'Total database (wildcard)'),
        ('txt=a', 'Contains letter "a"'),
        ('txt=the', 'Contains "the"'),

        # By country/jurisdiction
        ('pn=EP*', 'European patents'),
        ('pn=US*', 'US patents in EPO'),
        ('pn=WO*', 'PCT patents'),
        ('pn=CN*', 'Chinese patents'),

        # By year ranges
        ('pd>=20200101', 'Published since 2020'),
        ('pd>=20100101', 'Published since 2010'),
        ('pd>=20000101', 'Published since 2000'),

        # Technology areas
        ('txt=artificial intelligence', 'AI patents'),
        ('txt=5G', '5G patents'),
        ('txt=quantum', 'Quantum patents'),
        ('txt=semiconductor', 'Semiconductor patents'),

        # Major countries
        ('pa=china', 'China applicants'),
        ('pa=united states', 'US applicants'),
        ('pa=germany', 'German applicants'),
        ('pa=japan', 'Japanese applicants'),
    ]

    results = {
        'probe_time': datetime.now().isoformat(),
        'database_estimates': {},
        'quota_usage': {},
        'max_results_found': 0,
        'total_scope_estimate': 0
    }

    for i, (query, description) in enumerate(probe_queries, 1):
        print(f"\n{i:2d}. {description}")
        print(f"    Query: {query}")

        try:
            params = {
                'q': query,
                'Range': '1-1'  # Just get count, not actual data
            }

            response = session.get(search_url, params=params, timeout=15)
            print(f"    Status: {response.status_code}")

            # Check quota usage from headers
            if 'x-registeredquotaperweek-used' in response.headers:
                quota_used = response.headers['x-registeredquotaperweek-used']
                results['quota_usage'][query] = quota_used
                print(f"    Quota used: {quota_used} bytes")

            if response.status_code == 200:
                data = response.json()

                # Parse EPO response for total count
                total_found = 0
                if 'ops:world-patent-data' in data:
                    world_data = data['ops:world-patent-data']
                    if 'ops:biblio-search' in world_data:
                        biblio_search = world_data['ops:biblio-search']
                        if '@total-result-count' in biblio_search:
                            total_found = int(biblio_search['@total-result-count'])

                print(f"    Found: {total_found:,} patents")

                results['database_estimates'][description] = {
                    'query': query,
                    'total_found': total_found,
                    'response_size_estimate': len(response.text)
                }

                # Track maximum
                if total_found > results['max_results_found']:
                    results['max_results_found'] = total_found

                # Rate limiting
                time.sleep(2)

            else:
                print(f"    Error: {response.text[:100]}")
                results['database_estimates'][description] = {
                    'query': query,
                    'error': response.text[:200]
                }

        except Exception as e:
            print(f"    Exception: {e}")
            results['database_estimates'][description] = {
                'query': query,
                'exception': str(e)
            }

    # Additional analysis
    print("\n" + "=" * 60)
    print("DATABASE SIZE ANALYSIS")
    print("=" * 60)

    # Find largest counts
    valid_counts = [(desc, data['total_found']) for desc, data in results['database_estimates'].items()
                   if 'total_found' in data and data['total_found'] > 0]

    valid_counts.sort(key=lambda x: x[1], reverse=True)

    print("Largest patent counts:")
    for desc, count in valid_counts[:10]:
        print(f"  {desc}: {count:,}")

    # Estimate total database size
    if valid_counts:
        max_count = valid_counts[0][1]
        results['total_scope_estimate'] = max_count

        print(f"\nEstimated total EPO database scope: ~{max_count:,} patents")

        # Estimate data volume
        if results['quota_usage']:
            avg_quota_per_query = sum(int(q) for q in results['quota_usage'].values()) / len(results['quota_usage'])
            print(f"Average quota per query: ~{avg_quota_per_query:.0f} bytes")

            # Rough estimate of full database download size
            estimated_full_size = max_count * (avg_quota_per_query / 1)  # Assuming 1 patent per query response
            print(f"Estimated full database size: ~{estimated_full_size/1024/1024/1024:.1f} GB")

        # Weekly quota analysis
        current_quota = int(list(results['quota_usage'].values())[-1]) if results['quota_usage'] else 0
        weekly_limit = 4 * 1024 * 1024 * 1024  # 4GB
        remaining_quota = weekly_limit - current_quota

        print(f"\nQuota analysis:")
        print(f"  Current usage: {current_quota:,} bytes ({current_quota/1024/1024:.1f} MB)")
        print(f"  Weekly limit: {weekly_limit:,} bytes (4.0 GB)")
        print(f"  Remaining: {remaining_quota:,} bytes ({remaining_quota/1024/1024/1024:.2f} GB)")

        # Estimate how much data we can get this week
        patents_per_mb = 1024 * 1024 / avg_quota_per_query if results['quota_usage'] else 1000
        remaining_patents = remaining_quota / (avg_quota_per_query if results['quota_usage'] else 1000)
        print(f"  Can retrieve ~{remaining_patents:,.0f} more patents this week")

    # Save results
    output_dir = Path("F:/OSINT_DATA/epo_database_analysis")
    output_dir.mkdir(parents=True, exist_ok=True)

    results_file = output_dir / f"database_size_probe_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nAnalysis saved to: {results_file}")

    return results

if __name__ == "__main__":
    probe_epo_database_size()

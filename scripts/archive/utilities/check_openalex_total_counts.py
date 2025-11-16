#!/usr/bin/env python3
"""
Check total available records in OpenAlex for each topic
"""

import requests

def check_total_counts():
    """Get total counts for each topic"""

    base_url = "https://api.openalex.org"

    tech_topics = {
        'semiconductors': 'T10995',
        'artificial_intelligence': 'T11490',
        'quantum_computing': 'T10116',
        'advanced_materials': 'T10466',
        '5g_wireless': 'T10103',
        'robotics': 'T10069',
        'biotechnology': 'T10178',
        'aerospace': 'T10924',
        'new_energy': 'T10302',
        'advanced_manufacturing': 'T10825'
    }

    print("="*80)
    print("OPENALEX TOTAL AVAILABLE RECORDS")
    print("="*80)

    results = {}

    for topic_name, topic_id in tech_topics.items():
        # Build filter for Chinese research 2011-2025
        filter_str = f"authorships.countries:CN,topics.id:{topic_id},publication_year:2011-2025"

        url = f"{base_url}/works"
        params = {
            'filter': filter_str,
            'per-page': 1  # We only need the count
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            total = data.get('meta', {}).get('count', 0)
            extracted = {
                'semiconductors': 10000,
                'artificial_intelligence': 8917,
                'quantum_computing': 10000,
                'advanced_materials': 10000,
                '5g_wireless': 3155,
                'robotics': 10000,
                'biotechnology': 5186,
                'aerospace': 10000,
                'new_energy': 10000,
                'advanced_manufacturing': 10000
            }

            we_got = extracted[topic_name]
            remaining = total - we_got
            coverage_pct = (we_got / total * 100) if total > 0 else 0

            results[topic_name] = {
                'total_available': total,
                'extracted': we_got,
                'remaining': remaining,
                'coverage_pct': coverage_pct
            }

            status = "COMPLETE" if we_got >= total else "PARTIAL"

            print(f"\n[{topic_name.upper().replace('_', ' ')}]")
            print(f"  Total available: {total:,}")
            print(f"  Extracted: {we_got:,}")
            print(f"  Remaining: {remaining:,}")
            print(f"  Coverage: {coverage_pct:.1f}%")
            print(f"  Status: {status}")

        except Exception as e:
            print(f"\n[{topic_name.upper()}]")
            print(f"  Error: {str(e)[:100]}")

    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)

    total_available = sum(r['total_available'] for r in results.values())
    total_extracted = sum(r['extracted'] for r in results.values())
    total_remaining = sum(r['remaining'] for r in results.values())

    print(f"\nTotal available across all topics: {total_available:,}")
    print(f"Total extracted: {total_extracted:,}")
    print(f"Total remaining: {total_remaining:,}")
    print(f"Overall coverage: {total_extracted/total_available*100:.1f}%")

    # Which topics have more data?
    print("\n" + "="*80)
    print("TOPICS WITH MORE DATA AVAILABLE")
    print("="*80)

    can_extract_more = [(name, stats) for name, stats in results.items()
                       if stats['remaining'] > 0]

    if can_extract_more:
        can_extract_more.sort(key=lambda x: x[1]['remaining'], reverse=True)

        for topic_name, stats in can_extract_more:
            print(f"\n{topic_name}:")
            print(f"  Can extract {stats['remaining']:,} more papers")
            print(f"  Currently at {stats['coverage_pct']:.1f}% coverage")
    else:
        print("\n[OK] All available data has been extracted!")

    return results

if __name__ == "__main__":
    results = check_total_counts()

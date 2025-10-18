#!/usr/bin/env python3
"""
Quick test to find China collaborations in OpenAIRE
"""

import requests
import json
from datetime import datetime

def test_china_search():
    """Test different search approaches for China data"""

    print("="*60)
    print("TESTING CHINA COLLABORATION SEARCHES IN OPENAIRE")
    print("="*60)

    base_url = "https://api.openaire.eu/search/researchProducts"
    tests = []

    # Test 1: Direct China search
    print("\n1. Testing direct China search...")
    try:
        response = requests.get(
            base_url,
            params={
                'format': 'json',
                'country': 'CN',
                'size': 5
            },
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            total = data.get('response', {}).get('header', {}).get('total', {}).get('$', 0)
            print(f"   China (CN) research products: {total}")
            tests.append(('China direct', int(total)))

    except Exception as e:
        print(f"   ERROR: {e}")

    # Test 2: Italy-China collaboration
    print("\n2. Testing Italy-China collaboration...")
    try:
        response = requests.get(
            base_url,
            params={
                'format': 'json',
                'country': 'IT,CN',  # Both countries
                'size': 5
            },
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            total = data.get('response', {}).get('header', {}).get('total', {}).get('$', 0)
            print(f"   Italy-China collaborations: {total}")
            tests.append(('Italy-China', int(total)))

            # Show sample if found
            if int(total) > 0 and 'result' in data.get('response', {}).get('results', {}):
                results = data['response']['results']['result']
                if not isinstance(results, list):
                    results = [results]

                print("\n   Sample collaboration:")
                for r in results[:1]:  # First result
                    metadata = r.get('metadata', {}).get('oaf:entity', {}).get('oaf:result', {})
                    title = metadata.get('title', {}).get('$', 'No title')
                    print(f"   - Title: {title[:80]}...")

    except Exception as e:
        print(f"   ERROR: {e}")

    # Test 3: Germany-China collaboration
    print("\n3. Testing Germany-China collaboration...")
    try:
        response = requests.get(
            base_url,
            params={
                'format': 'json',
                'country': 'DE,CN',
                'size': 5
            },
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            total = data.get('response', {}).get('header', {}).get('total', {}).get('$', 0)
            print(f"   Germany-China collaborations: {total}")
            tests.append(('Germany-China', int(total)))

    except Exception as e:
        print(f"   ERROR: {e}")

    # Test 4: Search by Chinese institution
    print("\n4. Testing Chinese institution search...")
    try:
        response = requests.get(
            base_url,
            params={
                'format': 'json',
                'organizationName': 'Chinese Academy',
                'size': 5
            },
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            total = data.get('response', {}).get('header', {}).get('total', {}).get('$', 0)
            print(f"   Chinese Academy of Sciences: {total}")
            tests.append(('Chinese Academy', int(total)))

    except Exception as e:
        print(f"   ERROR: {e}")

    # Test 5: Keyword search for China
    print("\n5. Testing keyword search...")
    try:
        response = requests.get(
            base_url,
            params={
                'format': 'json',
                'country': 'IT',
                'keywords': 'China',
                'size': 5
            },
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            total = data.get('response', {}).get('header', {}).get('total', {}).get('$', 0)
            print(f"   Italy research mentioning 'China': {total}")
            tests.append(('Italy+China keyword', int(total)))

    except Exception as e:
        print(f"   ERROR: {e}")

    # Test 6: Try alternative China codes
    print("\n6. Testing alternative country codes...")
    alt_codes = ['CHN', 'china', 'China', 'CN']

    for code in alt_codes:
        try:
            response = requests.get(
                base_url,
                params={
                    'format': 'json',
                    'country': f'IT,{code}',
                    'size': 1
                },
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                total = data.get('response', {}).get('header', {}).get('total', {}).get('$', 0)
                if int(total) > 0:
                    print(f"   SUCCESS with code '{code}': {total} results")
                    tests.append((f'Code: {code}', int(total)))

        except:
            pass

    # Test 7: Hong Kong as proxy
    print("\n7. Testing Hong Kong (HK)...")
    try:
        response = requests.get(
            base_url,
            params={
                'format': 'json',
                'country': 'HK',
                'size': 5
            },
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            total = data.get('response', {}).get('header', {}).get('total', {}).get('$', 0)
            print(f"   Hong Kong research: {total}")
            tests.append(('Hong Kong', int(total)))

    except Exception as e:
        print(f"   ERROR: {e}")

    # Summary
    print("\n" + "="*60)
    print("SUMMARY OF FINDINGS")
    print("="*60)

    if tests:
        # Sort by count
        tests.sort(key=lambda x: x[1], reverse=True)

        print("\nTop results:")
        for name, count in tests[:10]:
            if count > 0:
                print(f"  {name}: {count:,} results")

        total_found = sum(count for _, count in tests)
        print(f"\nTotal China-related results found: {total_found:,}")

        if total_found == 0:
            print("\nWARNING: No China collaborations found!")
            print("Possible issues:")
            print("- API may use different country codes")
            print("- Data may be incomplete")
            print("- Access restrictions")
        else:
            print("\nSUCCESS: China collaborations DO exist in OpenAIRE!")
            print("The original scripts may have issues with:")
            print("- Country code format")
            print("- Search parameters")
            print("- Data extraction logic")

    # Save results
    output = {
        'test_time': datetime.now().isoformat(),
        'tests_performed': len(tests),
        'results': tests,
        'total_found': sum(count for _, count in tests)
    }

    output_file = f"F:/OSINT_DATA/openaire_china_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nTest results saved to: {output_file}")

if __name__ == "__main__":
    test_china_search()

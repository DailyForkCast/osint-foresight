#!/usr/bin/env python3
"""
Simple EPO OPS Test with Correct Query Format
Test basic functionality with authenticated access
"""

import requests
import json
from pathlib import Path

def test_epo_direct():
    """Test EPO OPS API directly with correct format"""

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
    print("EPO OPS Direct API Test")
    print("=" * 60)

    # Test 1: Check what endpoints are available
    print("1. Testing EPO endpoints...")

    endpoints_to_test = [
        "https://ops.epo.org/3.2/rest-services/published-data/search",
        "https://ops.epo.org/3.2/rest-services/published-data/publication",
        "https://ops.epo.org/3.2/rest-services/family",
        "https://ops.epo.org/3.2/rest-services/legal"
    ]

    for endpoint in endpoints_to_test:
        try:
            response = session.get(endpoint, timeout=10)
            print(f"  {endpoint.split('/')[-1]}: {response.status_code}")
        except Exception as e:
            print(f"  {endpoint.split('/')[-1]}: Error - {e}")

    # Test 2: Try simple search query
    print("\n2. Testing simple search...")

    try:
        # Very simple search for European patents
        search_url = "https://ops.epo.org/3.2/rest-services/published-data/search"
        params = {
            'q': 'txt=artificial',  # Simple text search
            'Range': '1-3'  # Just 3 results
        }

        response = session.get(search_url, params=params, timeout=10)
        print(f"  Search status: {response.status_code}")

        if response.status_code == 200:
            print("  Search successful!")
            # Try to parse response
            content_type = response.headers.get('content-type', '')
            print(f"  Content-Type: {content_type}")

            if 'json' in content_type:
                data = response.json()
                print(f"  Results: {type(data)}")
            else:
                print(f"  Response length: {len(response.text)} chars")
                print(f"  Response preview: {response.text[:200]}...")

        else:
            print(f"  Search failed: {response.text[:200]}")

    except Exception as e:
        print(f"  Search error: {e}")

    # Test 3: Check quota/limits
    print("\n3. Checking EPO quota information...")
    try:
        # EPO sometimes includes quota info in headers
        response = session.get(
            "https://ops.epo.org/3.2/rest-services/published-data/search",
            params={'q': 'txt=test', 'Range': '1-1'},
            timeout=10
        )

        print(f"  Response headers relevant to quota:")
        for header, value in response.headers.items():
            if any(word in header.lower() for word in ['limit', 'quota', 'rate', 'remaining']):
                print(f"    {header}: {value}")

    except Exception as e:
        print(f"  Quota check error: {e}")

if __name__ == "__main__":
    test_epo_direct()

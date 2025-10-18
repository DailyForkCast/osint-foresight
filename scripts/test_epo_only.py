#!/usr/bin/env python3
"""
Test EPO OPS with working queries
Focus on EPO authentication and query format
"""

import sys
from pathlib import Path

# Add collectors to path
sys.path.append(str(Path(__file__).parent / "collectors"))
from epo_ops_client import EPOOPSClient

def test_epo_basic_search():
    """Test EPO with simpler query formats"""

    print("=" * 60)
    print("EPO OPS Basic Search Test")
    print("=" * 60)

    client = EPOOPSClient()

    # Test 1: Basic search without country filter
    print("1. Testing basic search without country filter...")
    try:
        # Simple query for AI patents
        results = client.search_patents(
            query="artificial intelligence",
            max_results=5
        )

        if results.get('patents'):
            print(f"Found {len(results['patents'])} patents")
            sample = results['patents'][0]
            print(f"Sample: {sample.get('title', 'No title')[:50]}...")
        else:
            print("No patents found")

    except Exception as e:
        print(f"Basic search failed: {e}")

    # Test 2: Test different query syntax
    print("\n2. Testing different query syntax...")
    try:
        # Try simpler format
        results = client.search_patents(
            query="5G",
            country="EP",  # European patents
            max_results=3
        )

        if results.get('patents'):
            print(f"Found {len(results['patents'])} 5G patents")
        else:
            print("No 5G patents found")

    except Exception as e:
        print(f"5G search failed: {e}")

    # Test 3: Check what actually works
    print("\n3. Testing what EPO endpoints are available...")
    try:
        # Try manual URL construction to see what's accessible
        response = client.session.get(
            "https://ops.epo.org/3.2/rest-services",
            timeout=10
        )
        print(f"EPO base endpoint status: {response.status_code}")

        if response.status_code == 200:
            print("EPO base endpoint accessible")

    except Exception as e:
        print(f"Endpoint test failed: {e}")

if __name__ == "__main__":
    test_epo_basic_search()

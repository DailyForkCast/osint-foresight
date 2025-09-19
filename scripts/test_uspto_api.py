#!/usr/bin/env python
"""Test USPTO API key and endpoints"""

import os
import requests
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment
env_path = Path("C:/Projects/OSINT - Foresight/.env.local")
load_dotenv(env_path)

def test_api_key():
    """Test various API configurations"""
    api_key = os.getenv('USPTO_API_KEY')

    print("="*60)
    print("USPTO API Diagnostic Test")
    print("="*60)

    if not api_key:
        print("ERROR: No API key found in environment")
        return

    print(f"API Key: {api_key[:8]}...{api_key[-4:]}")
    print()

    # Test different endpoints and formats
    tests = [
        {
            "name": "Test 1: Basic patent search (GET)",
            "method": "GET",
            "url": "https://search.patentsview.org/api/v1/patent/",
            "headers": {"X-API-Key": api_key},
            "params": {"q": '{"patent_number":"10000000"}'}
        },
        {
            "name": "Test 2: With different header format",
            "method": "GET",
            "url": "https://search.patentsview.org/api/v1/patent/",
            "headers": {"x-api-key": api_key},  # lowercase
            "params": {"q": '{"patent_number":"10000000"}'}
        },
        {
            "name": "Test 3: API key as parameter",
            "method": "GET",
            "url": "https://search.patentsview.org/api/v1/patent/",
            "headers": {},
            "params": {
                "q": '{"patent_number":"10000000"}',
                "api_key": api_key
            }
        },
        {
            "name": "Test 4: Without API key (baseline)",
            "method": "GET",
            "url": "https://search.patentsview.org/api/v1/patent/",
            "headers": {},
            "params": {"q": '{"patent_number":"10000000"}'}
        },
        {
            "name": "Test 5: Alternative endpoint format",
            "method": "GET",
            "url": "https://api.patentsview.org/patents/query",
            "headers": {},
            "params": {"q": '{"patent_number":"10000000"}'}
        }
    ]

    for test in tests:
        print(f"\n{test['name']}")
        print("-" * 40)

        try:
            if test['method'] == "GET":
                response = requests.get(
                    test['url'],
                    headers=test['headers'],
                    params=test.get('params', {}),
                    timeout=10
                )
            else:
                response = requests.post(
                    test['url'],
                    headers=test['headers'],
                    data=test.get('data', {}),
                    timeout=10
                )

            print(f"Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                if 'patents' in data:
                    print(f"SUCCESS: Found {len(data['patents'])} patents")
                elif 'patent' in data:
                    print(f"SUCCESS: Found patent data")
                else:
                    print(f"Response keys: {list(data.keys())[:5]}")
            else:
                print(f"Response: {response.text[:200]}")

        except Exception as e:
            print(f"ERROR: {e}")

    print("\n" + "="*60)
    print("Recommendations:")
    print("-" * 40)
    print("1. If all tests fail with 403, the API key may be invalid")
    print("2. If Test 4 (without key) works, the key format may be wrong")
    print("3. Check if you need to activate the key at:")
    print("   https://search.patentsview.org/")
    print("4. The API may require email verification")
    print("\nAPI Documentation:")
    print("https://search.patentsview.org/docs/")
    print("="*60)

if __name__ == "__main__":
    test_api_key()

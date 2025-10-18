#!/usr/bin/env python3
"""
Simple test of UN Comtrade v2 API
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')

# Get keys
primary_key = os.getenv('UNCOMTRADE_PRIMARY_KEY')

print("="*80)
print("Testing UN Comtrade API v2 Direct")
print("="*80)

if primary_key:
    print(f"Primary key found: {primary_key[:10]}...")

    # Test different endpoints
    endpoints = [
        "https://comtradeapi.un.org/data/v1/get/C/A/HS",
        "https://comtradeapi.un.org/public/v1/preview/C/A/HS",
        "https://comtradeapi.un.org/public/v1/get/C/A/HS"
    ]

    headers = {
        'Ocp-Apim-Subscription-Key': primary_key,
        'Accept': 'application/json'
    }

    params = {
        'reporterCode': '156',  # China
        'period': '2023',
        'partnerCode': '0',     # World
        'flowCode': 'X',        # Exports
        'cmdCode': 'TOTAL',
        'maxRecords': '1'
    }

    for url in endpoints:
        print(f"\nTrying: {url}")
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"  [OK] Success! Data keys: {list(data.keys())[:5]}")
                if 'data' in data:
                    print(f"  Records found: {len(data['data'])}")
                break
            else:
                print(f"  Response: {response.text[:200]}")
        except Exception as e:
            print(f"  Error: {e}")

else:
    print("[ERROR] No API key found")

print("\n" + "="*80)

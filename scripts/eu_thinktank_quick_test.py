#!/usr/bin/env python3
"""
Quick European Think Tank Test - Minimal paths
"""

import urllib.request
import urllib.parse
import ssl
import re
import json
import time
from datetime import datetime

# Disable SSL verification
ssl._create_default_https_context = ssl._create_unverified_context

def quick_test(name: str, base_url: str):
    """Quick test with just 3 key paths"""
    print(f"\n{name}: {base_url}")

    result = {
        'name': name,
        'base_url': base_url,
        'china_found': False,
        'best_path': None,
        'mentions': 0
    }

    # Test just 3 key paths
    paths = ['', '/china', '/search?q=china']

    for path in paths:
        try:
            url = urllib.parse.urljoin(base_url, path)
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0'
            })
            with urllib.request.urlopen(req, timeout=3) as response:
                if response.status == 200:
                    content = response.read(51200).decode('utf-8', errors='ignore').lower()
                    china_count = content.count('china') + content.count('chinese')
                    if china_count > 0:
                        print(f"  Found: {path or '/'} ({china_count} mentions)")
                        if china_count > result['mentions']:
                            result['china_found'] = True
                            result['best_path'] = path or '/'
                            result['mentions'] = china_count
        except Exception as e:
            print(f"  Error on {path}: {str(e)[:50]}")

        time.sleep(0.2)

    if result['china_found']:
        print(f"  [+] Best: {result['best_path']} ({result['mentions']} mentions)")
    else:
        print(f"  [-] No China content found")

    return result

# European Think Tanks
eu_tanks = {
    'Chatham House': 'https://www.chathamhouse.org',
    'IISS': 'https://www.iiss.org',
    'ECFR': 'https://ecfr.eu',
    'SWP': 'https://www.swp-berlin.org',
    'MERICS': 'https://merics.org',
    'RUSI': 'https://rusi.org',
    'DGAP': 'https://dgap.org',
    'NUPI': 'https://www.nupi.no',
    'FOI': 'https://www.foi.se',
    'FRS': 'https://www.frstrategie.org',
    'IAI': 'https://www.iai.it'
}

if __name__ == '__main__':
    print("="*60)
    print("EUROPEAN THINK TANK QUICK TEST")
    print("="*60)

    results = {}

    for name, url in eu_tanks.items():
        result = quick_test(name, url)
        results[name] = result

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    with_china = [k for k, v in results.items() if v['china_found']]
    without_china = [k for k, v in results.items() if not v['china_found']]

    print(f"Total tested: {len(results)}")
    print(f"With China content: {len(with_china)}")
    print(f"Without China content: {len(without_china)}")

    if with_china:
        print("\n[+] WITH CHINA CONTENT:")
        for name in with_china:
            r = results[name]
            print(f"  {name}: {r['best_path']} ({r['mentions']} mentions)")

    if without_china:
        print("\n[-] WITHOUT CHINA CONTENT:")
        for name in without_china:
            print(f"  {name}")

    # Save
    with open('data/test_harvest/eu_quick_test.json', 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nSaved to: data/test_harvest/eu_quick_test.json")

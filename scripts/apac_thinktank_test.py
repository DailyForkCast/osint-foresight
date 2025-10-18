#!/usr/bin/env python3
"""
Asia-Pacific Think Tank Test for China Content
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
    """Quick test with key paths"""
    print(f"\n{name}: {base_url}")

    result = {
        'name': name,
        'base_url': base_url,
        'china_found': False,
        'best_path': None,
        'mentions': 0,
        'tested_paths': []
    }

    # Test key paths for Asia-Pacific think tanks
    paths = ['', '/china', '/publications', '/research', '/search?q=china', '/?s=china']

    for path in paths:
        try:
            url = urllib.parse.urljoin(base_url, path)
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    content = response.read(51200).decode('utf-8', errors='ignore').lower()
                    china_count = content.count('china') + content.count('chinese')
                    if china_count > 0:
                        print(f"  Found: {path or '/'} ({china_count} mentions)")
                        result['tested_paths'].append({'path': path or '/', 'mentions': china_count})
                        if china_count > result['mentions']:
                            result['china_found'] = True
                            result['best_path'] = path or '/'
                            result['mentions'] = china_count
        except Exception as e:
            if 'HTTP Error' in str(e):
                error_msg = str(e).split('\n')[0]
                print(f"  {path}: {error_msg}")

        time.sleep(0.3)

    if result['china_found']:
        print(f"  [+] Best: {result['best_path']} ({result['mentions']} mentions)")
    else:
        print(f"  [-] No China content found")

    return result

# Asia-Pacific Think Tanks
apac_tanks = {
    'ASPI': 'https://www.aspi.org.au',
    'Lowy': 'https://www.lowyinstitute.org',
    'IDSA': 'https://www.idsa.in',
    'ORF': 'https://www.orfonline.org',
    'ISEAS': 'https://www.iseas.edu.sg',
    'RSIS': 'https://www.rsis.edu.sg',
    'ISDP': 'https://www.isdp.eu',
    'JIIA': 'https://www.jiia.or.jp'
}

# Other Research Centers
other_tanks = {
    'Belfer': 'https://www.belfercenter.org',
    'MITRE': 'https://www.mitre.org',
    'IGCC': 'https://ucigcc.org',
    'NBR': 'https://www.nbr.org'
}

if __name__ == '__main__':
    print("="*60)
    print("ASIA-PACIFIC & OTHER THINK TANK TEST")
    print("="*60)

    all_results = {}

    # Test Asia-Pacific tanks
    print("\n[ASIA-PACIFIC THINK TANKS]")
    for name, url in apac_tanks.items():
        result = quick_test(name, url)
        all_results[name] = result

    # Test other research centers
    print("\n[OTHER RESEARCH CENTERS]")
    for name, url in other_tanks.items():
        result = quick_test(name, url)
        all_results[name] = result

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    with_china = [k for k, v in all_results.items() if v['china_found']]
    without_china = [k for k, v in all_results.items() if not v['china_found']]

    print(f"Total tested: {len(all_results)}")
    print(f"With China content: {len(with_china)}")
    print(f"Without China content: {len(without_china)}")

    print("\n[+] WITH CHINA CONTENT:")
    for name in with_china:
        r = all_results[name]
        print(f"  {name}: {r['best_path']} ({r['mentions']} mentions)")

    if without_china:
        print("\n[-] WITHOUT CHINA CONTENT:")
        for name in without_china:
            print(f"  {name}")

    # Save results
    output = {
        'scan_date': datetime.now().isoformat(),
        'summary': {
            'total_tested': len(all_results),
            'with_china_content': len(with_china),
            'without_china_content': len(without_china)
        },
        'results': all_results
    }

    with open('data/test_harvest/apac_other_test.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved to: data/test_harvest/apac_other_test.json")

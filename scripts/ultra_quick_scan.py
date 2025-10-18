#!/usr/bin/env python3
"""
Ultra Quick Homepage Scan for All Remaining Think Tanks
"""

import urllib.request
import ssl
import json
from datetime import datetime

# Disable SSL verification
ssl._create_default_https_context = ssl._create_unverified_context

def homepage_test(name, url):
    """Test just the homepage"""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=3) as response:
            content = response.read(30000).decode('utf-8', errors='ignore').lower()
            china_count = content.count('china') + content.count('chinese')
            return china_count
    except:
        return -1

# All think tanks to test
all_tanks = {
    # Asia-Pacific
    'ASPI': 'https://www.aspi.org.au',
    'Lowy': 'https://www.lowyinstitute.org',
    'IDSA': 'https://www.idsa.in',
    'ORF': 'https://www.orfonline.org',
    'ISEAS': 'https://www.iseas.edu.sg',
    'RSIS': 'https://www.rsis.edu.sg',
    'ISDP': 'https://www.isdp.eu',
    'JIIA': 'https://www.jiia.or.jp',

    # Others
    'Belfer': 'https://www.belfercenter.org',
    'MITRE': 'https://www.mitre.org',
    'IGCC': 'https://ucigcc.org',
    'NBR': 'https://www.nbr.org',

    # European (re-test those that failed)
    'SWP': 'https://www.swp-berlin.org/en',
    'RUSI': 'https://rusi.org',
    'NUPI': 'https://www.nupi.no/en',
    'FOI': 'https://www.foi.se/en',
    'IAI': 'https://www.iai.it/en'
}

results = {}
print("ULTRA QUICK SCAN - HOMEPAGE ONLY")
print("="*60)

for name, url in all_tanks.items():
    count = homepage_test(name, url)
    if count == -1:
        print(f"{name:15} {url:40} ERROR")
    elif count == 0:
        print(f"{name:15} {url:40} NO CHINA")
    else:
        print(f"{name:15} {url:40} CHINA: {count}")
    results[name] = {'url': url, 'china_mentions': count}

# Summary
with_china = [k for k, v in results.items() if v['china_mentions'] > 0]
no_china = [k for k, v in results.items() if v['china_mentions'] == 0]
errors = [k for k, v in results.items() if v['china_mentions'] == -1]

print(f"\n{len(with_china)} with China | {len(no_china)} without | {len(errors)} errors")

# Save
with open('data/test_harvest/ultra_quick_scan.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"Saved to: data/test_harvest/ultra_quick_scan.json")

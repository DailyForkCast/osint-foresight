#!/usr/bin/env python3
"""
Quick Think Tank Scanner for China Content
Faster version with focused path testing
"""

import urllib.request
import urllib.parse
import ssl
import re
import json
import time
from typing import List, Dict
from datetime import datetime

# Disable SSL verification
ssl._create_default_https_context = ssl._create_unverified_context

class QuickThinkTankScanner:
    def __init__(self):
        # Priority paths to test (most likely to contain China content)
        self.priority_paths = [
            '',  # Homepage
            '/china',
            '/topics/china',
            '/research/china',
            '/publications',
            '/asia',
            '/search?q=china',
            '/?s=china'
        ]

    def fetch_page(self, url: str, timeout: int = 5) -> str:
        """Quick fetch with shorter timeout"""
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            with urllib.request.urlopen(req, timeout=timeout) as response:
                if response.status == 200:
                    # Read only first 100KB to speed up
                    content = response.read(102400).decode('utf-8', errors='ignore')
                    return content
        except:
            pass
        return ''

    def quick_analyze(self, html: str) -> Dict:
        """Quick content analysis"""
        text_lower = html.lower()

        # Quick China detection
        china_count = text_lower.count('china') + text_lower.count('chinese')

        # Extract title
        title_match = re.search(r'<title[^>]*>([^<]+)</title>', html, re.IGNORECASE)
        title = title_match.group(1).strip() if title_match else 'No title'

        return {
            'title': title[:100],
            'china_mentions': china_count,
            'has_content': len(html) > 1000
        }

    def scan_batch(self, think_tanks: Dict) -> Dict:
        """Scan a batch of think tanks"""
        results = {}

        for key, info in think_tanks.items():
            print(f"\nScanning: {info['name']}")
            print(f"  URL: {info['base_url']}")

            result = {
                'name': info['name'],
                'base_url': info['base_url'],
                'working_paths': [],
                'china_content': False,
                'best_path': None,
                'max_mentions': 0
            }

            for path in self.priority_paths:
                url = urllib.parse.urljoin(info['base_url'], path)
                html = self.fetch_page(url)

                if html:
                    analysis = self.quick_analyze(html)

                    if analysis['has_content']:
                        if analysis['china_mentions'] > 0:
                            result['china_content'] = True
                            result['working_paths'].append({
                                'path': path or '/',
                                'mentions': analysis['china_mentions'],
                                'title': analysis['title']
                            })

                            if analysis['china_mentions'] > result['max_mentions']:
                                result['max_mentions'] = analysis['china_mentions']
                                result['best_path'] = path or '/'

                            print(f"    Found: {path or '/'} ({analysis['china_mentions']} mentions)")

                time.sleep(0.3)  # Quick rate limit

            if result['china_content']:
                print(f"  [+] China content found - Best: {result['best_path']}")
            else:
                print(f"  [-] No China content found")

            results[key] = result

        return results

# US Think Tanks Batch 1
us_batch1 = {
    'CFR': {
        'name': 'Council on Foreign Relations',
        'base_url': 'https://www.cfr.org'
    },
    'Brookings': {
        'name': 'Brookings Institution',
        'base_url': 'https://www.brookings.edu'
    },
    'CSIS': {
        'name': 'CSIS',
        'base_url': 'https://www.csis.org'
    },
    'RAND': {
        'name': 'RAND Corporation',
        'base_url': 'https://www.rand.org'
    },
    'Atlantic_Council': {
        'name': 'Atlantic Council',
        'base_url': 'https://www.atlanticcouncil.org'
    }
}

# US Think Tanks Batch 2
us_batch2 = {
    'AEI': {
        'name': 'American Enterprise Institute',
        'base_url': 'https://www.aei.org'
    },
    'Carnegie': {
        'name': 'Carnegie Endowment',
        'base_url': 'https://carnegieendowment.org'
    },
    'Wilson': {
        'name': 'Wilson Center',
        'base_url': 'https://www.wilsoncenter.org'
    },
    'Hoover': {
        'name': 'Hoover Institution',
        'base_url': 'https://www.hoover.org'
    },
    'USIP': {
        'name': 'US Institute of Peace',
        'base_url': 'https://www.usip.org'
    }
}

# US Think Tanks Batch 3
us_batch3 = {
    'CNAS': {
        'name': 'CNAS',
        'base_url': 'https://www.cnas.org'
    },
    'FDD': {
        'name': 'FDD',
        'base_url': 'https://www.fdd.org'
    },
    'Heritage': {
        'name': 'Heritage Foundation',
        'base_url': 'https://www.heritage.org'
    },
    'Hudson': {
        'name': 'Hudson Institute',
        'base_url': 'https://www.hudson.org'
    }
}

if __name__ == '__main__':
    scanner = QuickThinkTankScanner()

    print("="*60)
    print("QUICK THINK TANK CHINA CONTENT SCAN")
    print("="*60)

    # Scan US Batch 1
    print("\n[US THINK TANKS - BATCH 1]")
    batch1_results = scanner.scan_batch(us_batch1)

    # Scan US Batch 2
    print("\n[US THINK TANKS - BATCH 2]")
    batch2_results = scanner.scan_batch(us_batch2)

    # Scan US Batch 3
    print("\n[US THINK TANKS - BATCH 3]")
    batch3_results = scanner.scan_batch(us_batch3)

    # Combine results
    all_results = {**batch1_results, **batch2_results, **batch3_results}

    # Summary
    print("\n" + "="*60)
    print("SUMMARY - US THINK TANKS")
    print("="*60)

    with_china = [k for k, v in all_results.items() if v['china_content']]
    without_china = [k for k, v in all_results.items() if not v['china_content']]

    print(f"Total scanned: {len(all_results)}")
    print(f"With China content: {len(with_china)}")
    print(f"Without China content: {len(without_china)}")

    print("\n[+] THINK TANKS WITH CHINA CONTENT:")
    for key in with_china:
        result = all_results[key]
        print(f"  {result['name']}")
        print(f"    Best path: {result['best_path']} ({result['max_mentions']} mentions)")

    if without_china:
        print("\n[-] THINK TANKS WITHOUT CHINA CONTENT:")
        for key in without_china:
            print(f"  {all_results[key]['name']}")

    # Save results
    output = {
        'scan_date': datetime.now().isoformat(),
        'summary': {
            'total_scanned': len(all_results),
            'with_china_content': len(with_china),
            'without_china_content': len(without_china)
        },
        'results': all_results
    }

    with open('data/test_harvest/us_thinktanks_scan.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nResults saved to: data/test_harvest/us_thinktanks_scan.json")

#!/usr/bin/env python3
"""
European Think Tank Scanner for China Content
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

class EUThinkTankScanner:
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
            '/?s=china',
            '/en/china',  # For multilingual sites
            '/en/publications'
        ]

    def fetch_page(self, url: str, timeout: int = 5) -> str:
        """Quick fetch with shorter timeout"""
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept-Language': 'en-US,en;q=0.9'
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

        # Quick China detection (including European language variations)
        china_count = (text_lower.count('china') + text_lower.count('chinese') +
                      text_lower.count('chine') + text_lower.count('chinois') +  # French
                      text_lower.count('cina') +  # Italian
                      text_lower.count('kina'))  # Swedish/Norwegian

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

# European Think Tanks Batch 1
eu_batch1 = {
    'Chatham_House': {
        'name': 'Chatham House',
        'base_url': 'https://www.chathamhouse.org'
    },
    'IISS': {
        'name': 'IISS',
        'base_url': 'https://www.iiss.org'
    },
    'ECFR': {
        'name': 'European Council on Foreign Relations',
        'base_url': 'https://ecfr.eu'
    },
    'SWP': {
        'name': 'SWP Berlin',
        'base_url': 'https://www.swp-berlin.org'
    },
    'MERICS': {
        'name': 'MERICS',
        'base_url': 'https://merics.org'
    }
}

# European Think Tanks Batch 2
eu_batch2 = {
    'RUSI': {
        'name': 'RUSI',
        'base_url': 'https://rusi.org'
    },
    'DGAP': {
        'name': 'German Council on Foreign Relations',
        'base_url': 'https://dgap.org'
    },
    'NUPI': {
        'name': 'Norwegian Institute',
        'base_url': 'https://www.nupi.no'
    },
    'FOI': {
        'name': 'Swedish Defence Research',
        'base_url': 'https://www.foi.se'
    },
    'FRS': {
        'name': 'Foundation for Strategic Research',
        'base_url': 'https://www.frstrategie.org'
    },
    'IAI': {
        'name': 'Italian Institute',
        'base_url': 'https://www.iai.it'
    }
}

if __name__ == '__main__':
    scanner = EUThinkTankScanner()

    print("="*60)
    print("EUROPEAN THINK TANK CHINA CONTENT SCAN")
    print("="*60)

    # Scan EU Batch 1
    print("\n[EUROPEAN THINK TANKS - BATCH 1]")
    batch1_results = scanner.scan_batch(eu_batch1)

    # Scan EU Batch 2
    print("\n[EUROPEAN THINK TANKS - BATCH 2]")
    batch2_results = scanner.scan_batch(eu_batch2)

    # Combine results
    all_results = {**batch1_results, **batch2_results}

    # Summary
    print("\n" + "="*60)
    print("SUMMARY - EUROPEAN THINK TANKS")
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

    with open('data/test_harvest/eu_thinktanks_scan.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nResults saved to: data/test_harvest/eu_thinktanks_scan.json")

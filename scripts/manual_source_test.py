#!/usr/bin/env python3
"""
Manual source testing to find correct URLs
"""

import urllib.request
import urllib.parse
import ssl
import re

# Disable SSL verification
ssl._create_default_https_context = ssl._create_unverified_context

def test_source(name, base_url, test_paths):
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"Base URL: {base_url}")
    print('='*60)

    for path in test_paths:
        url = urllib.parse.urljoin(base_url, path)
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Research Bot) OSINT-Foresight/1.0'
            })
            with urllib.request.urlopen(req, timeout=10) as response:
                content = response.read().decode('utf-8', errors='ignore')
                # Count links
                link_count = len(re.findall(r'<a[^>]*href=', content))
                # Look for publication/article patterns
                pub_patterns = [
                    r'publication', r'article', r'brief', r'report',
                    r'analysis', r'research', r'insight', r'paper'
                ]
                pub_matches = sum(len(re.findall(pattern, content, re.IGNORECASE))
                                for pattern in pub_patterns)
                print(f"✓ {url} - Status: {response.status}, Links: {link_count}, Pub indicators: {pub_matches}")

                # Check for specific content structures
                if 'china' in content.lower():
                    china_count = content.lower().count('china')
                    print(f"  → Contains 'china' {china_count} times")

        except Exception as e:
            print(f"✗ {url} - Error: {e}")

# Test sources with various path combinations
sources_to_test = [
    ('CEIAS', 'https://ceias.eu', [
        '/',
        '/publications/',
        '/insights/',
        '/research/',
        '/articles/',
        '/analyses/',
        '/china/',
        '/commentary/'
    ]),
    ('IFRI', 'https://www.ifri.org', [
        '/en/',
        '/en/publications/',
        '/en/research/',
        '/en/analyses/',
        '/en/espace-presse/',
        '/fr/publications/'
    ]),
    ('Arctic Institute', 'https://www.thearcticinstitute.org', [
        '/',
        '/articles/',
        '/features/',
        '/briefing-papers/',
        '/research/',
        '/analysis/',
        '/publications/'
    ])
]

for name, base_url, paths in sources_to_test:
    test_source(name, base_url, paths)

print("\n" + "="*80)
print("TESTING COMPLETE")
print("="*80)

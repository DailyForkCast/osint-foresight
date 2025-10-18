#!/usr/bin/env python3
"""
CEIAS Simple Website Investigation
No unicode issues, comprehensive search for China content
"""

import urllib.request
import urllib.parse
import ssl
import re
import json
import time
from typing import List, Dict, Set

# Disable SSL verification
ssl._create_default_https_context = ssl._create_unverified_context

class CEIASInvestigator:
    def __init__(self):
        self.base_url = 'https://ceias.eu'
        self.china_urls = set()

    def fetch_page(self, url: str) -> str:
        """Fetch page content"""
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            with urllib.request.urlopen(req, timeout=15) as response:
                if response.status == 200:
                    return response.read().decode('utf-8', errors='ignore')
        except Exception as e:
            print(f"Error fetching {url}: {e}")
        return ''

    def analyze_page(self, url: str, html: str) -> Dict:
        """Analyze page for content indicators"""
        # Extract title
        title_match = re.search(r'<title[^>]*>([^<]+)</title>', html, re.IGNORECASE)
        title = title_match.group(1).strip() if title_match else 'No title'

        # Count content indicators
        indicators = {
            'china_mentions': len(re.findall(r'china', html, re.IGNORECASE)),
            'publications': len(re.findall(r'publication', html, re.IGNORECASE)),
            'research': len(re.findall(r'research', html, re.IGNORECASE)),
            'analysis': len(re.findall(r'analysis', html, re.IGNORECASE)),
            'articles': len(re.findall(r'article', html, re.IGNORECASE)),
            'reports': len(re.findall(r'report', html, re.IGNORECASE)),
            'commentaries': len(re.findall(r'commentary', html, re.IGNORECASE))
        }

        # Extract links
        links = re.findall(r'href=["\']([^"\'>]+)["\']', html, re.IGNORECASE)
        ceias_links = []
        for link in links:
            if link.startswith('/'):
                full_link = urllib.parse.urljoin(self.base_url, link)
                if 'ceias.eu' in full_link:
                    ceias_links.append(full_link)
            elif 'ceias.eu' in link:
                ceias_links.append(link)

        return {
            'url': url,
            'title': title,
            'indicators': indicators,
            'ceias_links': list(set(ceias_links)),
            'page_size': len(html),
            'has_china_content': indicators['china_mentions'] > 0
        }

    def investigate(self):
        """Main investigation"""
        print("=" * 60)
        print("CEIAS WEBSITE INVESTIGATION")
        print("=" * 60)

        # Test many possible paths
        test_paths = [
            # Basic paths
            '',
            '/en',
            '/sk',

            # Content paths
            '/publications',
            '/en/publications',
            '/sk/publications',
            '/research',
            '/en/research',
            '/sk/research',
            '/insights',
            '/en/insights',
            '/sk/insights',
            '/commentaries',
            '/en/commentaries',
            '/sk/commentaries',
            '/articles',
            '/en/articles',
            '/sk/articles',
            '/analyses',
            '/en/analyses',
            '/sk/analyses',
            '/blog',
            '/en/blog',
            '/sk/blog',
            '/news',
            '/en/news',
            '/sk/news',

            # Topic-specific paths
            '/china',
            '/en/china',
            '/sk/china',
            '/asia',
            '/en/asia',
            '/sk/asia',
            '/topics/china',
            '/en/topics/china',
            '/category/china',
            '/en/category/china',
            '/tag/china',
            '/en/tag/china',

            # Archive paths
            '/archive',
            '/en/archive',
            '/library',
            '/en/library',
            '/documents',
            '/en/documents',

            # Search and listing paths
            '/search',
            '/en/search',
            '/all-publications',
            '/en/all-publications',
            '/publications-list',
            '/en/publications-list'
        ]

        results = {}
        working_urls = []
        china_content_urls = []

        for path in test_paths:
            url = urllib.parse.urljoin(self.base_url, path)
            print(f"\nTesting: {url}")

            html = self.fetch_page(url)
            if html and len(html) > 1000:  # Minimum content threshold
                analysis = self.analyze_page(url, html)
                results[url] = analysis
                working_urls.append(url)

                print(f"  SUCCESS - Title: {analysis['title'][:60]}")
                print(f"  China mentions: {analysis['indicators']['china_mentions']}")
                print(f"  Publications: {analysis['indicators']['publications']}")
                print(f"  Research: {analysis['indicators']['research']}")
                print(f"  Articles: {analysis['indicators']['articles']}")
                print(f"  Links found: {len(analysis['ceias_links'])}")

                if analysis['has_china_content']:
                    china_content_urls.append(url)
                    print(f"  *** CHINA CONTENT DETECTED ***")

                # Look for article/publication links in the content
                promising_links = []
                for link in analysis['ceias_links'][:20]:  # Limit
                    if any(term in link.lower() for term in ['publication', 'article', 'research', 'china', 'analysis']):
                        promising_links.append(link)

                if promising_links:
                    print(f"  Promising links found: {len(promising_links)}")
                    for link in promising_links[:3]:
                        print(f"    -> {link}")
            else:
                print(f"  FAILED - 404 or minimal content")

            time.sleep(0.5)  # Rate limiting

        # Summary
        print(f"\n" + "=" * 60)
        print("INVESTIGATION SUMMARY")
        print("=" * 60)

        print(f"Total paths tested: {len(test_paths)}")
        print(f"Working URLs: {len(working_urls)}")
        print(f"China content URLs: {len(china_content_urls)}")

        # Best sources for publications
        pub_ranked = sorted(results.items(),
                           key=lambda x: x[1]['indicators']['publications'],
                           reverse=True)

        print(f"\nTOP PUBLICATION SOURCES:")
        for url, data in pub_ranked[:5]:
            if data['indicators']['publications'] > 0:
                print(f"  {data['indicators']['publications']} pubs: {url}")

        # Best sources for China content
        china_ranked = sorted(results.items(),
                             key=lambda x: x[1]['indicators']['china_mentions'],
                             reverse=True)

        print(f"\nTOP CHINA CONTENT SOURCES:")
        for url, data in china_ranked[:5]:
            if data['indicators']['china_mentions'] > 0:
                print(f"  {data['indicators']['china_mentions']} mentions: {url}")

        # Save detailed results
        output_data = {
            'investigation_date': '2025-09-19',
            'total_paths_tested': len(test_paths),
            'working_urls': working_urls,
            'china_content_urls': china_content_urls,
            'detailed_results': results,
            'recommendations': {
                'best_publication_paths': [url for url, _ in pub_ranked[:5] if results[url]['indicators']['publications'] > 5],
                'best_china_paths': [url for url, _ in china_ranked[:5] if results[url]['indicators']['china_mentions'] > 5]
            }
        }

        with open('data/test_harvest/ceias_investigation.json', 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        print(f"\nResults saved to: data/test_harvest/ceias_investigation.json")

        # Extract specific recommendations
        print(f"\nRECOMMENDED PATHS FOR HARVESTER UPDATE:")
        recommended_paths = []
        for url, data in results.items():
            if (data['indicators']['publications'] > 5 or
                data['indicators']['china_mentions'] > 5 or
                data['indicators']['articles'] > 10):
                path = url.replace(self.base_url, '') or '/'
                score = (data['indicators']['publications'] * 3 +
                        data['indicators']['china_mentions'] * 2 +
                        data['indicators']['articles'])
                recommended_paths.append((path, score))

        recommended_paths.sort(key=lambda x: x[1], reverse=True)

        print("\nUPDATE YOUR HARVESTER WITH THESE PATHS:")
        for path, score in recommended_paths[:8]:
            print(f"  '{path}',  # Score: {score}")

        return results

if __name__ == '__main__':
    investigator = CEIASInvestigator()
    investigator.investigate()

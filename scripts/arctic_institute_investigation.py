#!/usr/bin/env python3
"""
Arctic Institute Deep Website Investigation
Comprehensive search for China content on Arctic/polar research website
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

class ArcticInstituteInvestigator:
    def __init__(self):
        self.base_url = 'https://www.thearcticinstitute.org'
        self.found_urls = set()
        self.china_urls = set()

    def fetch_page(self, url: str) -> str:
        """Fetch page content"""
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })
            with urllib.request.urlopen(req, timeout=15) as response:
                if response.status == 200:
                    return response.read().decode('utf-8', errors='ignore')
        except Exception as e:
            print(f"Error fetching {url}: {e}")
        return ''

    def check_china_arctic_content(self, text: str) -> bool:
        """Check for China and Arctic content"""
        china_terms = [
            # Standard China terms
            'china', 'chinese', 'beijing', 'prc', 'peoples republic',
            'xi jinping', 'ccp', 'communist party', 'mainland china',
            'sino-', 'hong kong', 'taiwan',

            # Arctic-specific China terms
            'polar silk road', 'belt and road', 'bri',
            'china arctic', 'chinese arctic', 'sino-arctic',
            'china polar', 'chinese polar', 'china ice',
            'cosco', 'cnooc', 'china shipping',
            'chinese icebreaker', 'xuelong', 'snow dragon',
            'china arctic station', 'chinese arctic research',
            'polar research institute', 'china arctic council',
            'china observer', 'china greenland', 'china iceland',
            'china russia arctic', 'china northern sea route',
            'china arctic resources', 'china arctic mineral'
        ]
        text_lower = text.lower()
        found_terms = [term for term in china_terms if term in text_lower]
        return len(found_terms) > 0, found_terms

    def analyze_arctic_page(self, url: str, html: str) -> Dict:
        """Comprehensive page analysis for Arctic content"""
        # Extract title
        title_match = re.search(r'<title[^>]*>([^<]+)</title>', html, re.IGNORECASE)
        title = title_match.group(1).strip() if title_match else 'No title'

        # Extract main content areas
        content_patterns = [
            r'<article[^>]*>(.*?)</article>',
            r'<main[^>]*>(.*?)</main>',
            r'<div[^>]*class="[^"]*content[^"]*"[^>]*>(.*?)</div>',
            r'<div[^>]*class="[^"]*post[^"]*"[^>]*>(.*?)</div>',
            r'<section[^>]*class="[^"]*articles[^"]*"[^>]*>(.*?)</section>',
            r'<div[^>]*class="[^"]*entry[^"]*"[^>]*>(.*?)</div>'
        ]

        extracted_content = []
        for pattern in content_patterns:
            matches = re.findall(pattern, html, re.DOTALL | re.IGNORECASE)
            extracted_content.extend(matches)

        # Combine all content for analysis
        full_content = ' '.join(extracted_content) if extracted_content else html

        # Check for China content
        has_china, china_terms = self.check_china_arctic_content(full_content)
        china_count = len(china_terms)

        # Count various content types
        indicators = {
            'articles': len(re.findall(r'article', html, re.IGNORECASE)),
            'research': len(re.findall(r'research', html, re.IGNORECASE)),
            'analysis': len(re.findall(r'analysis', html, re.IGNORECASE)),
            'studies': len(re.findall(r'studies', html, re.IGNORECASE)),
            'reports': len(re.findall(r'report', html, re.IGNORECASE)),
            'publications': len(re.findall(r'publication', html, re.IGNORECASE)),
            'china_mentions': china_count,
            'arctic_mentions': len(re.findall(r'arctic', html, re.IGNORECASE)),
            'polar_mentions': len(re.findall(r'polar', html, re.IGNORECASE)),
            'ice_mentions': len(re.findall(r'ice', html, re.IGNORECASE)),
            'geopolitics': len(re.findall(r'geopolitic', html, re.IGNORECASE)),
            'security': len(re.findall(r'security', html, re.IGNORECASE))
        }

        # Extract links
        links = re.findall(r'href=["\']([^"\']+)["\']', html, re.IGNORECASE)
        arctic_links = []
        for link in links:
            if link.startswith('/'):
                full_link = urllib.parse.urljoin(self.base_url, link)
                arctic_links.append(full_link)
            elif 'thearcticinstitute.org' in link:
                arctic_links.append(link)

        # Look for article/post patterns
        article_patterns = []
        article_regexes = [
            r'<h[1-6][^>]*>([^<]*china[^<]*)</h[1-6]>',
            r'<a[^>]*href="([^"]*)"[^>]*>([^<]*china[^<]*)</a>',
            r'<span[^>]*class="[^"]*title[^"]*"[^>]*>([^<]*china[^<]*)</span>'
        ]

        for regex in article_regexes:
            matches = re.findall(regex, html, re.IGNORECASE)
            article_patterns.extend(matches)

        return {
            'url': url,
            'title': title,
            'indicators': indicators,
            'arctic_links': list(set(arctic_links)),
            'has_china_content': has_china,
            'china_terms_found': china_terms,
            'article_patterns': article_patterns,
            'page_size': len(html),
            'content_preview': full_content[:500] if full_content else html[:500]
        }

    def investigate_arctic_institute(self):
        """Main Arctic Institute investigation"""
        print("=" * 80)
        print("ARCTIC INSTITUTE COMPREHENSIVE WEBSITE INVESTIGATION")
        print("=" * 80)

        # Test comprehensive paths for Arctic Institute
        test_paths = [
            # Main sections
            '',
            '/articles',
            '/research',
            '/publications',
            '/analysis',
            '/reports',
            '/blog',
            '/news',

            # Topic-specific paths
            '/china',
            '/chinese',
            '/sino',
            '/geopolitics',
            '/security',
            '/policy',
            '/governance',
            '/resources',
            '/shipping',
            '/ice',
            '/climate',
            '/environment',

            # Regional focus
            '/asia',
            '/russia',
            '/nordic',
            '/greenland',
            '/iceland',
            '/norway',
            '/canada',
            '/alaska',

            # Category/tag patterns
            '/category/china',
            '/category/geopolitics',
            '/category/security',
            '/category/policy',
            '/tag/china',
            '/tag/chinese',
            '/tag/geopolitics',
            '/tag/policy',
            '/tags/china',
            '/tags/chinese',

            # Archive patterns
            '/archive',
            '/archives',
            '/2024',
            '/2023',
            '/2022',
            '/all-articles',
            '/all-posts',

            # Search patterns
            '/search',
            '/search?q=china',
            '/?s=china',
            '/?search=china'
        ]

        results = {}
        china_content_found = []
        working_urls = []

        for path in test_paths:
            url = urllib.parse.urljoin(self.base_url, path)
            print(f"\nTesting: {url}")

            html = self.fetch_page(url)
            if html and len(html) > 1000:
                analysis = self.analyze_arctic_page(url, html)
                results[url] = analysis
                working_urls.append(url)

                print(f"  SUCCESS - {len(html)} chars")
                print(f"  Title: {analysis['title'][:60]}")
                print(f"  China mentions: {analysis['indicators']['china_mentions']}")
                print(f"  Arctic mentions: {analysis['indicators']['arctic_mentions']}")
                print(f"  Articles: {analysis['indicators']['articles']}")
                print(f"  Research: {analysis['indicators']['research']}")
                print(f"  Geopolitics: {analysis['indicators']['geopolitics']}")
                print(f"  Links found: {len(analysis['arctic_links'])}")

                if analysis['has_china_content']:
                    china_content_found.append(url)
                    print(f"  *** CHINA CONTENT DETECTED! ***")
                    print(f"      Terms found: {', '.join(analysis['china_terms_found'][:5])}")

                if analysis['article_patterns']:
                    print(f"  Article patterns found: {len(analysis['article_patterns'])}")
                    for pattern in analysis['article_patterns'][:3]:
                        if isinstance(pattern, tuple):
                            print(f"      -> {pattern[1] if len(pattern) > 1 else pattern[0]}")
                        else:
                            print(f"      -> {pattern}")

                # Look for promising China/Arctic links
                promising_links = []
                for link in analysis['arctic_links'][:25]:
                    link_lower = link.lower()
                    if any(term in link_lower for term in ['china', 'chinese', 'sino', 'geopolitic', 'policy', 'security']):
                        promising_links.append(link)

                if promising_links:
                    print(f"  Promising China/Arctic links: {len(promising_links)}")
                    for link in promising_links[:3]:
                        print(f"      -> {link}")
            else:
                print(f"  FAILED - 404 or minimal content")

            time.sleep(0.8)  # Rate limiting

        # Phase 2: Investigate promising links
        print(f"\n" + "=" * 80)
        print("PHASE 2: INVESTIGATING CHINA/ARCTIC CONTENT")
        print("=" * 80)

        # Collect all promising links from discovered pages
        all_promising_links = set()
        for page_data in results.values():
            for link in page_data['arctic_links']:
                link_lower = link.lower()
                if any(term in link_lower for term in ['china', 'chinese', 'sino', 'geopolitic', 'security', 'policy', 'russia']):
                    all_promising_links.add(link)

        # Investigate top promising links
        for link in list(all_promising_links)[:20]:
            if link not in results:
                print(f"\nDeep dive: {link}")
                html = self.fetch_page(link)
                if html and len(html) > 500:
                    analysis = self.analyze_arctic_page(link, html)
                    results[link] = analysis

                    if analysis['has_china_content']:
                        print(f"  CHINA CONTENT! ({analysis['indicators']['china_mentions']} mentions)")
                        china_content_found.append(link)
                        if analysis['china_terms_found']:
                            print(f"      Terms: {', '.join(analysis['china_terms_found'][:5])}")

                    if analysis['indicators']['articles'] > 10:
                        print(f"  Article hub ({analysis['indicators']['articles']} articles)")

                    if analysis['indicators']['geopolitics'] > 5:
                        print(f"  Geopolitics focus ({analysis['indicators']['geopolitics']} mentions)")

                time.sleep(1)

        # Summary and recommendations
        self.print_summary(results, china_content_found, working_urls)
        self.save_results(results, china_content_found)

        return results

    def print_summary(self, results: Dict, china_content_found: List, working_urls: List):
        """Print investigation summary"""
        print(f"\n" + "=" * 80)
        print("ARCTIC INSTITUTE INVESTIGATION SUMMARY")
        print("=" * 80)

        print(f"Total paths tested: {len(results)}")
        print(f"Working URLs: {len(working_urls)}")
        print(f"China content URLs: {len(china_content_found)}")

        # Best China content sources
        china_ranked = sorted(results.items(),
                             key=lambda x: x[1]['indicators']['china_mentions'],
                             reverse=True)

        print(f"\nTOP CHINA CONTENT SOURCES:")
        for url, data in china_ranked[:5]:
            if data['indicators']['china_mentions'] > 0:
                print(f"  {data['indicators']['china_mentions']} mentions: {url}")
                print(f"      Title: {data['title'][:60]}")

        # Best article sources
        article_ranked = sorted(results.items(),
                               key=lambda x: x[1]['indicators']['articles'],
                               reverse=True)

        print(f"\nTOP ARTICLE SOURCES:")
        for url, data in article_ranked[:5]:
            if data['indicators']['articles'] > 0:
                print(f"  {data['indicators']['articles']} articles: {url}")

        # Best geopolitics sources
        geo_ranked = sorted(results.items(),
                           key=lambda x: x[1]['indicators']['geopolitics'],
                           reverse=True)

        print(f"\nTOP GEOPOLITICS SOURCES:")
        for url, data in geo_ranked[:5]:
            if data['indicators']['geopolitics'] > 0:
                print(f"  {data['indicators']['geopolitics']} geopolitics: {url}")

        # Recommendations for harvester
        print(f"\nRECOMMENDED HARVESTER PATHS:")
        recommended = []
        for url, data in results.items():
            if (data['indicators']['china_mentions'] > 2 or
                data['indicators']['articles'] > 15 or
                data['indicators']['geopolitics'] > 5):
                score = (data['indicators']['china_mentions'] * 4 +
                        data['indicators']['geopolitics'] * 2 +
                        data['indicators']['articles'])
                recommended.append((url, score, data))

        recommended.sort(key=lambda x: x[1], reverse=True)

        for url, score, data in recommended[:10]:
            path = url.replace(self.base_url, '') or '/'
            print(f"  Score {score:3d}: {path}")

    def save_results(self, results: Dict, china_content_found: List):
        """Save investigation results"""
        output_file = 'data/test_harvest/arctic_investigation_results.json'

        output_data = {
            'investigation_date': '2025-09-19',
            'base_url': self.base_url,
            'summary': {
                'total_pages_investigated': len(results),
                'china_content_pages': len(china_content_found),
                'china_urls': china_content_found
            },
            'page_details': results,
            'recommendations': {
                'high_priority_paths': [],
                'medium_priority_paths': [],
                'arctic_specialization_notes': [
                    'Arctic Institute focuses on polar geopolitics',
                    'China Arctic engagement is a key research area',
                    'Look for Polar Silk Road and BRI Arctic content'
                ]
            }
        }

        # Generate path recommendations
        for url, data in results.items():
            path = url.replace(self.base_url, '')
            if data['indicators']['china_mentions'] > 5 or data['indicators']['geopolitics'] > 10:
                output_data['recommendations']['high_priority_paths'].append(path)
            elif data['indicators']['china_mentions'] > 1 or data['indicators']['articles'] > 20:
                output_data['recommendations']['medium_priority_paths'].append(path)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        print(f"\nResults saved to: {output_file}")

if __name__ == '__main__':
    investigator = ArcticInstituteInvestigator()
    investigator.investigate_arctic_institute()

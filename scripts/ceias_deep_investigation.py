#!/usr/bin/env python3
"""
CEIAS Deep Website Investigation
Comprehensive search for China content structure
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
        self.found_urls = set()
        self.china_urls = set()
        self.site_structure = {}

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

    def extract_links(self, html: str, base_url: str) -> List[str]:
        """Extract all links from HTML"""
        links = []
        # More comprehensive link patterns
        patterns = [
            r'href=["\']([^"\'>]+)["\']',
            r'src=["\']([^"\'>]+)["\']'
        ]

        for pattern in patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            for match in matches:
                if match.startswith('http'):
                    links.append(match)
                elif match.startswith('/'):
                    links.append(urllib.parse.urljoin(base_url, match))
                elif not match.startswith('#') and not match.startswith('javascript:'):
                    links.append(urllib.parse.urljoin(base_url, match))

        return list(set(links))

    def check_china_content(self, text: str) -> bool:
        """Check if content is China-related"""
        china_terms = [
            'china', 'chinese', 'beijing', 'prc', 'peoples republic',
            'xi jinping', 'ccp', 'communist party', 'mainland china',
            'sino-', 'hong kong', 'taiwan', 'tibet', 'xinjiang',
            'belt and road', 'bri', 'silk road', 'middle kingdom'
        ]
        text_lower = text.lower()
        return any(term in text_lower for term in china_terms)

    def analyze_page_structure(self, url: str, html: str) -> Dict:
        """Analyze page structure and content"""
        # Extract title
        title_match = re.search(r'<title[^>]*>([^<]+)</title>', html, re.IGNORECASE)
        title = title_match.group(1) if title_match else 'No title'

        # Extract navigation structure
        nav_patterns = [
            r'<nav[^>]*>(.*?)</nav>',
            r'<ul[^>]*class="[^"]*menu[^"]*"[^>]*>(.*?)</ul>',
            r'<div[^>]*class="[^"]*nav[^"]*"[^>]*>(.*?)</div>'
        ]

        navigation_links = []
        for pattern in nav_patterns:
            nav_matches = re.findall(pattern, html, re.DOTALL | re.IGNORECASE)
            for nav_html in nav_matches:
                nav_links = self.extract_links(nav_html, url)
                navigation_links.extend(nav_links)

        # Look for specific content indicators
        content_indicators = {
            'publications': len(re.findall(r'publication', html, re.IGNORECASE)),
            'research': len(re.findall(r'research', html, re.IGNORECASE)),
            'analysis': len(re.findall(r'analysis', html, re.IGNORECASE)),
            'china_mentions': len(re.findall(r'china', html, re.IGNORECASE)),
            'articles': len(re.findall(r'article', html, re.IGNORECASE)),
            'reports': len(re.findall(r'report', html, re.IGNORECASE))
        }

        # Check for dynamic content indicators
        has_javascript = 'javascript' in html.lower()
        has_react = any(term in html.lower() for term in ['react', 'vue', 'angular'])
        has_ajax = any(term in html.lower() for term in ['ajax', 'fetch', 'xhr'])

        return {
            'url': url,
            'title': title.strip(),
            'content_indicators': content_indicators,
            'navigation_links': list(set(navigation_links)),
            'has_dynamic_content': has_javascript or has_react or has_ajax,
            'is_china_related': self.check_china_content(html),
            'page_size': len(html)
        }

    def investigate_comprehensive(self):
        """Comprehensive investigation of CEIAS website"""
        print("="*80)
        print("CEIAS COMPREHENSIVE WEBSITE INVESTIGATION")
        print("="*80)

        # Start with multiple entry points
        entry_points = [
            '',  # Homepage
            '/en',
            '/sk',  # Slovak language
            '/publications',
            '/en/publications',
            '/research',
            '/en/research',
            '/insights',
            '/en/insights',
            '/commentaries',
            '/en/commentaries',
            '/articles',
            '/en/articles',
            '/analyses',
            '/en/analyses',
            '/china',
            '/en/china',
            '/asia',
            '/en/asia',
            '/blog',
            '/en/blog',
            '/news',
            '/en/news'
        ]

        investigated_pages = {}

        for path in entry_points:
            url = urllib.parse.urljoin(self.base_url, path)
            print(f"\n🔍 Investigating: {url}")

            html = self.fetch_page(url)
            if html:
                analysis = self.analyze_page_structure(url, html)
                investigated_pages[url] = analysis

                print(f"  ✅ Status: SUCCESS")
                print(f"  📄 Title: {analysis['title'][:80]}")
                print(f"  🇨🇳 China mentions: {analysis['content_indicators']['china_mentions']}")
                print(f"  📚 Publications: {analysis['content_indicators']['publications']}")
                print(f"  📊 Research: {analysis['content_indicators']['research']}")
                print(f"  🔗 Nav links found: {len(analysis['navigation_links'])}")
                print(f"  ⚡ Dynamic content: {analysis['has_dynamic_content']}")

                if analysis['is_china_related']:
                    self.china_urls.add(url)
                    print(f"  🎯 CHINA CONTENT DETECTED!")

                # Extract and queue more URLs to investigate
                page_links = self.extract_links(html, url)
                ceias_links = [link for link in page_links if 'ceias.eu' in link]

                # Look for promising paths
                for link in ceias_links[:10]:  # Limit to avoid infinite crawling
                    if any(term in link.lower() for term in ['china', 'publication', 'research', 'analysis', 'article']):
                        if link not in investigated_pages:
                            print(f"    🔗 Found promising link: {link}")
            else:
                print(f"  ❌ Status: FAILED (404 or error)")

            time.sleep(1)  # Rate limiting

        # Second phase: investigate promising links found
        print(f"\n" + "="*80)
        print("PHASE 2: INVESTIGATING PROMISING LINKS")
        print("="*80)

        promising_links = set()
        for page_data in investigated_pages.values():
            for nav_link in page_data['navigation_links']:
                if 'ceias.eu' in nav_link and any(term in nav_link.lower() for term in
                    ['china', 'publication', 'research', 'analysis', 'article', 'commentary']):
                    promising_links.add(nav_link)

        for link in list(promising_links)[:15]:  # Limit investigation
            if link not in investigated_pages:
                print(f"\n🔍 Deep dive: {link}")
                html = self.fetch_page(link)
                if html:
                    analysis = self.analyze_page_structure(link, html)
                    investigated_pages[link] = analysis

                    if analysis['is_china_related'] or analysis['content_indicators']['china_mentions'] > 5:
                        print(f"  🎯 CHINA CONTENT FOUND! ({analysis['content_indicators']['china_mentions']} mentions)")
                        self.china_urls.add(link)

                    if analysis['content_indicators']['publications'] > 10:
                        print(f"  📚 MAJOR PUBLICATION HUB! ({analysis['content_indicators']['publications']} publications)")
                time.sleep(1)

        # Summary
        self.print_investigation_summary(investigated_pages)
        self.save_results(investigated_pages)

        return investigated_pages

    def print_investigation_summary(self, investigated_pages: Dict):
        """Print comprehensive summary"""
        print(f"\n" + "="*80)
        print("INVESTIGATION SUMMARY")
        print("="*80)

        total_pages = len(investigated_pages)
        china_pages = len(self.china_urls)
        accessible_pages = len([p for p in investigated_pages.values() if p['page_size'] > 0])

        print(f"📊 Pages investigated: {total_pages}")
        print(f"✅ Successfully accessed: {accessible_pages}")
        print(f"🇨🇳 China content pages: {china_pages}")

        # Best publication sources
        print(f"\n🏆 TOP PUBLICATION SOURCES:")
        pub_sources = sorted(investigated_pages.items(),
                           key=lambda x: x[1]['content_indicators']['publications'],
                           reverse=True)[:5]

        for url, data in pub_sources:
            if data['content_indicators']['publications'] > 0:
                print(f"  📚 {data['content_indicators']['publications']} pubs: {url}")
                print(f"      Title: {data['title'][:60]}")

        # Best China content sources
        print(f"\n🇨🇳 TOP CHINA CONTENT SOURCES:")
        china_sources = sorted(investigated_pages.items(),
                             key=lambda x: x[1]['content_indicators']['china_mentions'],
                             reverse=True)[:5]

        for url, data in china_sources:
            if data['content_indicators']['china_mentions'] > 0:
                print(f"  🎯 {data['content_indicators']['china_mentions']} mentions: {url}")
                print(f"      Title: {data['title'][:60]}")

        # Recommended paths for harvester
        print(f"\n🎯 RECOMMENDED HARVESTER PATHS:")
        recommended = []
        for url, data in investigated_pages.items():
            if (data['content_indicators']['publications'] > 5 or
                data['content_indicators']['china_mentions'] > 10 or
                data['is_china_related']):
                score = (data['content_indicators']['publications'] * 2 +
                        data['content_indicators']['china_mentions'] +
                        data['content_indicators']['research'])
                recommended.append((url, score, data))

        recommended.sort(key=lambda x: x[1], reverse=True)

        for url, score, data in recommended[:8]:
            path = url.replace(self.base_url, '')
            print(f"  ⭐ Score {score:3d}: {path or '/'} - {data['title'][:50]}")

    def save_results(self, investigated_pages: Dict):
        """Save investigation results"""
        output_file = 'data/test_harvest/ceias_investigation_results.json'

        results = {
            'investigation_date': '2025-09-19',
            'base_url': self.base_url,
            'summary': {
                'total_pages_investigated': len(investigated_pages),
                'china_content_pages': len(self.china_urls),
                'china_urls': list(self.china_urls)
            },
            'page_details': investigated_pages,
            'recommendations': {
                'high_priority_paths': [],
                'medium_priority_paths': [],
                'notes': []
            }
        }

        # Generate recommendations
        for url, data in investigated_pages.items():
            path = url.replace(self.base_url, '')
            if data['content_indicators']['publications'] > 10 or data['content_indicators']['china_mentions'] > 15:
                results['recommendations']['high_priority_paths'].append(path)
            elif data['content_indicators']['publications'] > 3 or data['content_indicators']['china_mentions'] > 5:
                results['recommendations']['medium_priority_paths'].append(path)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Results saved to: {output_file}")

if __name__ == '__main__':
    investigator = CEIASInvestigator()
    investigator.investigate_comprehensive()

#!/usr/bin/env python3
"""
IFRI Deep Website Investigation
Comprehensive search for China content on French website
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

class IFRIInvestigator:
    def __init__(self):
        self.base_url = 'https://www.ifri.org'
        self.found_urls = set()
        self.china_urls = set()

    def fetch_page(self, url: str) -> str:
        """Fetch page content"""
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8'
            })
            with urllib.request.urlopen(req, timeout=15) as response:
                if response.status == 200:
                    return response.read().decode('utf-8', errors='ignore')
        except Exception as e:
            print(f"Error fetching {url}: {e}")
        return ''

    def check_china_content_french(self, text: str) -> bool:
        """Check for China content in French and English"""
        china_terms = [
            # French terms
            'chine', 'chinois', 'chinoise', 'pekin', 'beijing',
            'republique populaire de chine', 'rpc',
            'xi jinping', 'parti communiste chinois', 'pcc',
            'hong kong', 'taiwan', 'tibet', 'xinjiang',
            'route de la soie', 'nouvelles routes de la soie',
            'sino-', 'asie-pacifique',

            # English terms (in case of mixed content)
            'china', 'chinese', 'beijing', 'prc',
            'xi jinping', 'ccp', 'communist party',
            'belt and road', 'bri', 'silk road',
            'hong kong', 'taiwan', 'tibet', 'xinjiang'
        ]
        text_lower = text.lower()
        found_terms = [term for term in china_terms if term in text_lower]
        return len(found_terms) > 0, found_terms

    def analyze_page_comprehensive(self, url: str, html: str) -> Dict:
        """Comprehensive page analysis for French content"""
        # Extract title
        title_match = re.search(r'<title[^>]*>([^<]+)</title>', html, re.IGNORECASE)
        title = title_match.group(1).strip() if title_match else 'No title'

        # Extract main content areas
        content_patterns = [
            r'<article[^>]*>(.*?)</article>',
            r'<main[^>]*>(.*?)</main>',
            r'<div[^>]*class="[^"]*content[^"]*"[^>]*>(.*?)</div>',
            r'<div[^>]*class="[^"]*publication[^"]*"[^>]*>(.*?)</div>',
            r'<section[^>]*class="[^"]*research[^"]*"[^>]*>(.*?)</section>'
        ]

        extracted_content = []
        for pattern in content_patterns:
            matches = re.findall(pattern, html, re.DOTALL | re.IGNORECASE)
            extracted_content.extend(matches)

        # Combine all content for analysis
        full_content = ' '.join(extracted_content) if extracted_content else html

        # Check for China content
        has_china, china_terms = self.check_china_content_french(full_content)
        china_count = len(china_terms)

        # Count various content types
        indicators = {
            'publications': len(re.findall(r'publication', html, re.IGNORECASE)),
            'recherche': len(re.findall(r'recherche', html, re.IGNORECASE)),
            'analyse': len(re.findall(r'analyse', html, re.IGNORECASE)),
            'etude': len(re.findall(r'etude', html, re.IGNORECASE)),
            'rapport': len(re.findall(r'rapport', html, re.IGNORECASE)),
            'articles': len(re.findall(r'article', html, re.IGNORECASE)),
            'chine_mentions': china_count,
            'asie_mentions': len(re.findall(r'asie', html, re.IGNORECASE)),
            'indo_pacifique': len(re.findall(r'indo.pacifique', html, re.IGNORECASE))
        }

        # Extract links
        links = re.findall(r'href=["\']([^"\']+)["\']', html, re.IGNORECASE)
        ifri_links = []
        for link in links:
            if link.startswith('/'):
                full_link = urllib.parse.urljoin(self.base_url, link)
                ifri_links.append(full_link)
            elif 'ifri.org' in link:
                ifri_links.append(link)

        # Look for specific Asia/China sections
        asia_sections = []
        asia_patterns = [
            r'asie[^<]*<',
            r'chine[^<]*<',
            r'indo.pacifique[^<]*<',
            r'centre.*asie[^<]*<'
        ]

        for pattern in asia_patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            asia_sections.extend(matches)

        return {
            'url': url,
            'title': title,
            'indicators': indicators,
            'ifri_links': list(set(ifri_links)),
            'has_china_content': has_china,
            'china_terms_found': china_terms,
            'asia_sections': asia_sections,
            'page_size': len(html),
            'content_preview': full_content[:500] if full_content else html[:500]
        }

    def investigate_ifri(self):
        """Main IFRI investigation"""
        print("=" * 80)
        print("IFRI COMPREHENSIVE WEBSITE INVESTIGATION")
        print("=" * 80)

        # Test comprehensive paths including French structure
        test_paths = [
            # Main sections
            '',
            '/fr',
            '/en',

            # Publications and research
            '/fr/publications',
            '/en/publications',
            '/fr/recherche',
            '/en/research',
            '/fr/analyses',
            '/en/analyses',
            '/fr/etudes',
            '/en/studies',
            '/fr/rapports',
            '/en/reports',
            '/fr/actualites',
            '/en/news',
            '/fr/evenements',
            '/en/events',

            # Regional focus areas
            '/fr/recherche/asie',
            '/en/research/asia',
            '/fr/programmes/asie-visions',
            '/en/programs/asia-visions',
            '/fr/recherche/chine',
            '/en/research/china',
            '/fr/themes/asie-pacifique',
            '/en/themes/asia-pacific',
            '/fr/programmes/centre-asie',
            '/en/programs/asia-center',

            # Specific China-related paths
            '/fr/chine',
            '/en/china',
            '/fr/sino',
            '/en/sino',
            '/fr/relations-sino',
            '/en/sino-relations',

            # Archive and search
            '/fr/archives',
            '/en/archives',
            '/fr/rechercher',
            '/en/search',
            '/fr/toutes-publications',
            '/en/all-publications'
        ]

        results = {}
        china_content_found = []
        working_urls = []

        for path in test_paths:
            url = urllib.parse.urljoin(self.base_url, path)
            print(f"\nTesting: {url}")

            html = self.fetch_page(url)
            if html and len(html) > 1000:
                analysis = self.analyze_page_comprehensive(url, html)
                results[url] = analysis
                working_urls.append(url)

                print(f"  SUCCESS - {len(html)} chars")
                print(f"  Title: {analysis['title'][:60]}")
                print(f"  China mentions: {analysis['indicators']['chine_mentions']}")
                print(f"  Asia mentions: {analysis['indicators']['asie_mentions']}")
                print(f"  Publications: {analysis['indicators']['publications']}")
                print(f"  Research: {analysis['indicators']['recherche']}")
                print(f"  Links found: {len(analysis['ifri_links'])}")

                if analysis['has_china_content']:
                    china_content_found.append(url)
                    print(f"  *** CHINA CONTENT DETECTED! ***")
                    print(f"      Terms found: {', '.join(analysis['china_terms_found'][:5])}")

                if analysis['asia_sections']:
                    print(f"  Asia sections found: {len(analysis['asia_sections'])}")
                    for section in analysis['asia_sections'][:3]:
                        print(f"      -> {section[:50]}")

                # Look for promising article links
                promising_links = []
                for link in analysis['ifri_links'][:20]:
                    link_lower = link.lower()
                    if any(term in link_lower for term in ['chine', 'china', 'asie', 'asia', 'sino']):
                        promising_links.append(link)

                if promising_links:
                    print(f"  Promising China/Asia links: {len(promising_links)}")
                    for link in promising_links[:3]:
                        print(f"      -> {link}")
            else:
                print(f"  FAILED - 404 or minimal content")

            time.sleep(0.8)  # Rate limiting

        # Phase 2: Investigate promising links
        print(f"\n" + "=" * 80)
        print("PHASE 2: INVESTIGATING CHINA/ASIA CONTENT")
        print("=" * 80)

        # Collect all promising links from discovered pages
        all_promising_links = set()
        for page_data in results.values():
            for link in page_data['ifri_links']:
                link_lower = link.lower()
                if any(term in link_lower for term in ['chine', 'china', 'asie', 'asia', 'sino', 'beijing', 'pekin']):
                    all_promising_links.add(link)

        # Investigate top promising links
        for link in list(all_promising_links)[:15]:
            if link not in results:
                print(f"\nDeep dive: {link}")
                html = self.fetch_page(link)
                if html and len(html) > 500:
                    analysis = self.analyze_page_comprehensive(link, html)
                    results[link] = analysis

                    if analysis['has_china_content']:
                        print(f"  CHINA CONTENT! ({analysis['indicators']['chine_mentions']} mentions)")
                        china_content_found.append(link)
                        print(f"      Preview: {analysis['content_preview'][:100]}...")

                    if analysis['indicators']['publications'] > 5:
                        print(f"  Publication hub ({analysis['indicators']['publications']} pubs)")

                time.sleep(1)

        # Summary and recommendations
        self.print_summary(results, china_content_found, working_urls)
        self.save_results(results, china_content_found)

        return results

    def print_summary(self, results: Dict, china_content_found: List, working_urls: List):
        """Print investigation summary"""
        print(f"\n" + "=" * 80)
        print("IFRI INVESTIGATION SUMMARY")
        print("=" * 80)

        print(f"Total paths tested: {len(results)}")
        print(f"Working URLs: {len(working_urls)}")
        print(f"China content URLs: {len(china_content_found)}")

        # Best China content sources
        china_ranked = sorted(results.items(),
                             key=lambda x: x[1]['indicators']['chine_mentions'],
                             reverse=True)

        print(f"\nTOP CHINA CONTENT SOURCES:")
        for url, data in china_ranked[:5]:
            if data['indicators']['chine_mentions'] > 0:
                print(f"  {data['indicators']['chine_mentions']} mentions: {url}")
                print(f"      Title: {data['title'][:60]}")

        # Best publication sources
        pub_ranked = sorted(results.items(),
                           key=lambda x: x[1]['indicators']['publications'],
                           reverse=True)

        print(f"\nTOP PUBLICATION SOURCES:")
        for url, data in pub_ranked[:5]:
            if data['indicators']['publications'] > 0:
                print(f"  {data['indicators']['publications']} pubs: {url}")

        # Recommendations for harvester
        print(f"\nRECOMMENDED HARVESTER PATHS:")
        recommended = []
        for url, data in results.items():
            if (data['indicators']['chine_mentions'] > 2 or
                data['indicators']['publications'] > 10 or
                data['indicators']['asie_mentions'] > 5):
                score = (data['indicators']['chine_mentions'] * 3 +
                        data['indicators']['asie_mentions'] +
                        data['indicators']['publications'])
                recommended.append((url, score, data))

        recommended.sort(key=lambda x: x[1], reverse=True)

        for url, score, data in recommended[:8]:
            path = url.replace(self.base_url, '') or '/'
            print(f"  Score {score:3d}: {path}")

    def save_results(self, results: Dict, china_content_found: List):
        """Save investigation results"""
        output_file = 'data/test_harvest/ifri_investigation_results.json'

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
                'language_notes': [
                    'IFRI is primarily French-language',
                    'China content exists but may require French search terms',
                    'Asia-Pacific research center identified'
                ]
            }
        }

        # Generate path recommendations
        for url, data in results.items():
            path = url.replace(self.base_url, '')
            if data['indicators']['chine_mentions'] > 5 or data['indicators']['publications'] > 15:
                output_data['recommendations']['high_priority_paths'].append(path)
            elif data['indicators']['chine_mentions'] > 1 or data['indicators']['asie_mentions'] > 10:
                output_data['recommendations']['medium_priority_paths'].append(path)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        print(f"\nResults saved to: {output_file}")

if __name__ == '__main__':
    investigator = IFRIInvestigator()
    investigator.investigate_ifri()

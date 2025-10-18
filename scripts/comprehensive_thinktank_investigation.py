#!/usr/bin/env python3
"""
Comprehensive Think Tank Investigation for China Content
Tests multiple paths and search patterns for each think tank
"""

import urllib.request
import urllib.parse
import ssl
import re
import json
import time
from typing import List, Dict, Set, Tuple
from datetime import datetime

# Disable SSL verification
ssl._create_default_https_context = ssl._create_unverified_context

class ComprehensiveThinkTankInvestigator:
    def __init__(self):
        # Complete list of think tanks to investigate
        self.think_tanks = {
            # US Think Tanks
            'CFR': {
                'name': 'Council on Foreign Relations',
                'base_url': 'https://www.cfr.org',
                'type': 'US'
            },
            'Brookings': {
                'name': 'Brookings Institution',
                'base_url': 'https://www.brookings.edu',
                'type': 'US'
            },
            'CSIS': {
                'name': 'Center for Strategic and International Studies',
                'base_url': 'https://www.csis.org',
                'type': 'US'
            },
            'RAND': {
                'name': 'RAND Corporation',
                'base_url': 'https://www.rand.org',
                'type': 'US'
            },
            'Atlantic Council': {
                'name': 'Atlantic Council',
                'base_url': 'https://www.atlanticcouncil.org',
                'type': 'US'
            },
            'AEI': {
                'name': 'American Enterprise Institute',
                'base_url': 'https://www.aei.org',
                'type': 'US'
            },
            'Carnegie': {
                'name': 'Carnegie Endowment',
                'base_url': 'https://carnegieendowment.org',
                'type': 'US'
            },
            'Wilson Center': {
                'name': 'Wilson Center',
                'base_url': 'https://www.wilsoncenter.org',
                'type': 'US'
            },
            'Hoover': {
                'name': 'Hoover Institution',
                'base_url': 'https://www.hoover.org',
                'type': 'US'
            },
            'USIP': {
                'name': 'US Institute of Peace',
                'base_url': 'https://www.usip.org',
                'type': 'US'
            },
            'CNAS': {
                'name': 'Center for a New American Security',
                'base_url': 'https://www.cnas.org',
                'type': 'US'
            },
            'FDD': {
                'name': 'Foundation for Defense of Democracies',
                'base_url': 'https://www.fdd.org',
                'type': 'US'
            },
            'Heritage': {
                'name': 'Heritage Foundation',
                'base_url': 'https://www.heritage.org',
                'type': 'US'
            },
            'Hudson': {
                'name': 'Hudson Institute',
                'base_url': 'https://www.hudson.org',
                'type': 'US'
            },

            # European Think Tanks
            'Chatham House': {
                'name': 'Chatham House',
                'base_url': 'https://www.chathamhouse.org',
                'type': 'EU'
            },
            'IISS': {
                'name': 'International Institute for Strategic Studies',
                'base_url': 'https://www.iiss.org',
                'type': 'EU'
            },
            'ECFR': {
                'name': 'European Council on Foreign Relations',
                'base_url': 'https://ecfr.eu',
                'type': 'EU'
            },
            'SWP': {
                'name': 'German Institute for International and Security Affairs',
                'base_url': 'https://www.swp-berlin.org',
                'type': 'EU'
            },
            'MERICS': {
                'name': 'Mercator Institute for China Studies',
                'base_url': 'https://merics.org',
                'type': 'EU'
            },
            'RUSI': {
                'name': 'Royal United Services Institute',
                'base_url': 'https://rusi.org',
                'type': 'EU'
            },
            'DGAP': {
                'name': 'German Council on Foreign Relations',
                'base_url': 'https://dgap.org',
                'type': 'EU'
            },
            'NUPI': {
                'name': 'Norwegian Institute of International Affairs',
                'base_url': 'https://www.nupi.no',
                'type': 'EU'
            },
            'FOI': {
                'name': 'Swedish Defence Research Agency',
                'base_url': 'https://www.foi.se',
                'type': 'EU'
            },
            'FRS': {
                'name': 'Foundation for Strategic Research',
                'base_url': 'https://www.frstrategie.org',
                'type': 'EU'
            },
            'IAI': {
                'name': 'Istituto Affari Internazionali',
                'base_url': 'https://www.iai.it',
                'type': 'EU'
            },

            # Asia-Pacific Think Tanks
            'ASPI': {
                'name': 'Australian Strategic Policy Institute',
                'base_url': 'https://www.aspi.org.au',
                'type': 'APAC'
            },
            'Lowy': {
                'name': 'Lowy Institute',
                'base_url': 'https://www.lowyinstitute.org',
                'type': 'APAC'
            },
            'IDSA': {
                'name': 'Institute for Defence Studies and Analyses',
                'base_url': 'https://www.idsa.in',
                'type': 'APAC'
            },
            'ORF': {
                'name': 'Observer Research Foundation',
                'base_url': 'https://www.orfonline.org',
                'type': 'APAC'
            },
            'ISEAS': {
                'name': 'ISEAS-Yusof Ishak Institute',
                'base_url': 'https://www.iseas.edu.sg',
                'type': 'APAC'
            },
            'RSIS': {
                'name': 'S. Rajaratnam School of International Studies',
                'base_url': 'https://www.rsis.edu.sg',
                'type': 'APAC'
            },
            'ISDP': {
                'name': 'Institute for Security and Development Policy',
                'base_url': 'https://www.isdp.eu',
                'type': 'APAC'
            },
            'JIIA': {
                'name': 'Japan Institute of International Affairs',
                'base_url': 'https://www.jiia.or.jp',
                'type': 'APAC'
            },

            # Other Research Centers
            'Belfer': {
                'name': 'Belfer Center',
                'base_url': 'https://www.belfercenter.org',
                'type': 'OTHER'
            },
            'MITRE': {
                'name': 'MITRE Corporation',
                'base_url': 'https://www.mitre.org',
                'type': 'OTHER'
            },
            'IGCC': {
                'name': 'Institute on Global Conflict and Cooperation',
                'base_url': 'https://ucigcc.org',
                'type': 'OTHER'
            },
            'NBR': {
                'name': 'National Bureau of Asian Research',
                'base_url': 'https://www.nbr.org',
                'type': 'OTHER'
            }
        }

        # Common path patterns to test
        self.common_paths = [
            '',  # Homepage
            '/china',
            '/china-research',
            '/topics/china',
            '/research/china',
            '/programs/china',
            '/projects/china',
            '/asia',
            '/asia-pacific',
            '/indo-pacific',
            '/publications',
            '/articles',
            '/analysis',
            '/research',
            '/reports',
            '/briefs',
            '/commentary',
            '/blog',
            '/news',
            '/insights',
            '/papers',
            '/studies',
            '/search?q=china',
            '/search?query=china',
            '/?s=china',
            '/tag/china',
            '/tags/china',
            '/category/china',
            '/categories/china',
            '/topic/china'
        ]

    def fetch_page(self, url: str) -> str:
        """Fetch page content"""
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5'
            })
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    return response.read().decode('utf-8', errors='ignore')
        except Exception as e:
            return ''
        return ''

    def analyze_content(self, html: str) -> Dict:
        """Analyze page content for China-related material"""
        china_keywords = [
            'china', 'chinese', 'beijing', 'prc', 'peoples republic',
            'xi jinping', 'ccp', 'zhongnanhai', 'sino-',
            'belt and road', 'bri', 'silk road', 'made in china',
            'huawei', 'zte', 'bytedance', 'tencent', 'alibaba'
        ]

        tech_keywords = [
            'artificial intelligence', 'ai', 'quantum', 'semiconductor',
            'biotechnology', '5g', '6g', 'cyber', 'space', 'technology',
            'innovation', 'research', 'development', 'science'
        ]

        text_lower = html.lower()

        china_count = sum(text_lower.count(kw.lower()) for kw in china_keywords)
        tech_count = sum(text_lower.count(kw.lower()) for kw in tech_keywords)

        # Extract title
        title_match = re.search(r'<title[^>]*>([^<]+)</title>', html, re.IGNORECASE)
        title = title_match.group(1).strip() if title_match else 'No title'

        # Look for article/publication counts
        article_count = len(re.findall(r'<article', html, re.IGNORECASE))
        link_count = len(re.findall(r'<a[^>]*href=', html, re.IGNORECASE))

        return {
            'title': title,
            'china_mentions': china_count,
            'tech_mentions': tech_count,
            'article_elements': article_count,
            'total_links': link_count,
            'page_size': len(html),
            'has_china_content': china_count > 0,
            'has_tech_content': tech_count > 0
        }

    def investigate_think_tank(self, key: str, info: Dict) -> Dict:
        """Investigate a single think tank"""
        results = {
            'name': info['name'],
            'base_url': info['base_url'],
            'type': info['type'],
            'working_paths': [],
            'china_paths': [],
            'best_path': None,
            'total_china_mentions': 0,
            'investigation_time': datetime.now().isoformat()
        }

        print(f"\nInvestigating: {info['name']}")
        print(f"Base URL: {info['base_url']}")
        print("-" * 50)

        best_score = 0

        for path in self.common_paths[:15]:  # Test first 15 paths
            url = urllib.parse.urljoin(info['base_url'], path)
            html = self.fetch_page(url)

            if html and len(html) > 1000:
                analysis = self.analyze_content(html)

                if analysis['page_size'] > 5000:  # Meaningful content
                    results['working_paths'].append(path or '/')

                    score = analysis['china_mentions'] + (analysis['tech_mentions'] * 0.5)

                    if analysis['china_mentions'] > 0:
                        results['china_paths'].append({
                            'path': path or '/',
                            'china_mentions': analysis['china_mentions'],
                            'tech_mentions': analysis['tech_mentions'],
                            'title': analysis['title'][:60]
                        })
                        results['total_china_mentions'] += analysis['china_mentions']

                        if score > best_score:
                            best_score = score
                            results['best_path'] = path or '/'

                        print(f"  FOUND: {path or '/'} - China: {analysis['china_mentions']}, Tech: {analysis['tech_mentions']}")

            time.sleep(0.5)  # Rate limiting

        if results['china_paths']:
            print(f"  BEST PATH: {results['best_path']} (Score: {best_score:.1f})")
        else:
            print(f"  WARNING: No China content found on tested paths")

        return results

    def run_investigation(self, subset: str = None):
        """Run investigation on all or subset of think tanks"""
        all_results = {}

        # Filter think tanks if subset specified
        if subset:
            tanks_to_test = {k: v for k, v in self.think_tanks.items()
                            if v['type'] == subset}
        else:
            tanks_to_test = self.think_tanks

        print(f"\n{'='*60}")
        print(f"COMPREHENSIVE THINK TANK INVESTIGATION")
        print(f"Testing {len(tanks_to_test)} think tanks")
        print(f"{'='*60}")

        for key, info in tanks_to_test.items():
            result = self.investigate_think_tank(key, info)
            all_results[key] = result
            time.sleep(1)  # Pause between think tanks

        return all_results

    def save_results(self, results: Dict, filename: str):
        """Save investigation results"""
        # Calculate summary statistics
        summary = {
            'total_investigated': len(results),
            'with_china_content': len([r for r in results.values() if r['china_paths']]),
            'total_china_mentions': sum(r['total_china_mentions'] for r in results.values()),
            'investigation_date': datetime.now().isoformat()
        }

        output = {
            'summary': summary,
            'results': results,
            'recommendations': self.generate_recommendations(results)
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print(f"\nResults saved to: {filename}")

    def generate_recommendations(self, results: Dict) -> Dict:
        """Generate harvesting recommendations"""
        recommendations = {
            'high_priority': [],  # >50 China mentions
            'medium_priority': [],  # 10-50 China mentions
            'low_priority': [],  # <10 China mentions
            'no_content': []  # No China content found
        }

        for key, result in results.items():
            if result['total_china_mentions'] == 0:
                recommendations['no_content'].append(key)
            elif result['total_china_mentions'] >= 50:
                recommendations['high_priority'].append({
                    'name': key,
                    'base_url': result['base_url'],
                    'best_path': result['best_path'],
                    'china_mentions': result['total_china_mentions']
                })
            elif result['total_china_mentions'] >= 10:
                recommendations['medium_priority'].append({
                    'name': key,
                    'base_url': result['base_url'],
                    'best_path': result['best_path'],
                    'china_mentions': result['total_china_mentions']
                })
            else:
                recommendations['low_priority'].append({
                    'name': key,
                    'base_url': result['base_url'],
                    'best_path': result['best_path'],
                    'china_mentions': result['total_china_mentions']
                })

        return recommendations

    def print_summary(self, results: Dict):
        """Print investigation summary"""
        print(f"\n{'='*60}")
        print("INVESTIGATION SUMMARY")
        print(f"{'='*60}")

        total = len(results)
        with_content = len([r for r in results.values() if r['china_paths']])

        print(f"Total think tanks investigated: {total}")
        print(f"Think tanks with China content: {with_content} ({with_content/total*100:.1f}%)")
        print(f"Total China mentions found: {sum(r['total_china_mentions'] for r in results.values())}")

        # Top 5 by China mentions
        sorted_results = sorted(results.items(),
                               key=lambda x: x[1]['total_china_mentions'],
                               reverse=True)

        print(f"\nTOP 5 THINK TANKS BY CHINA CONTENT:")
        for key, result in sorted_results[:5]:
            if result['total_china_mentions'] > 0:
                print(f"  {result['name']}: {result['total_china_mentions']} mentions")
                print(f"    Best path: {result['best_path']}")

if __name__ == '__main__':
    investigator = ComprehensiveThinkTankInvestigator()

    # Run investigation on US think tanks first
    print("\nStarting with US Think Tanks...")
    us_results = investigator.run_investigation('US')
    investigator.save_results(us_results, 'data/test_harvest/us_thinktanks_investigation.json')
    investigator.print_summary(us_results)

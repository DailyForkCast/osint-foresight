#!/usr/bin/env python3
"""
Reinvestigate Think Tanks That Showed No China Content
Using more targeted paths and search strategies
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

class ThinkTankReinvestigator:
    def __init__(self):
        # Think tanks to reinvestigate with specialized paths
        self.targets = {
            'SWP': {
                'name': 'SWP Berlin',
                'base_url': 'https://www.swp-berlin.org',
                'specialized_paths': [
                    '/en',
                    '/en/research/asia',
                    '/en/research/china',
                    '/en/publications',
                    '/en/publication?search=china',
                    '/en/topics/asia',
                    '/en/dossier/china',
                    '/en/research'
                ]
            },
            'RUSI': {
                'name': 'Royal United Services Institute',
                'base_url': 'https://rusi.org',
                'specialized_paths': [
                    '',
                    '/explore-our-research/publications',
                    '/explore-our-research/publications?search=china',
                    '/topics/china',
                    '/regions/asia-pacific',
                    '/explore-our-research',
                    '/research/china',
                    '/search?q=china'
                ]
            },
            'NUPI': {
                'name': 'Norwegian Institute',
                'base_url': 'https://www.nupi.no',
                'specialized_paths': [
                    '/en',
                    '/en/Research/China',
                    '/en/Research/Asia',
                    '/en/Publications',
                    '/en/About-NUPI/Research-groups/Research-group-on-Asia',
                    '/en/Topics/China',
                    '/en/search?q=china'
                ]
            },
            'FOI': {
                'name': 'Swedish Defence Research',
                'base_url': 'https://www.foi.se',
                'specialized_paths': [
                    '/en',
                    '/en/foi/research/asia-and-the-pacific.html',
                    '/en/foi/research/china.html',
                    '/en/foi/reports.html',
                    '/en/search.html?q=china',
                    '/en/foi/research.html',
                    '/en/foi/news-and-pressroom.html'
                ]
            },
            'IAI': {
                'name': 'Italian Institute',
                'base_url': 'https://www.iai.it',
                'specialized_paths': [
                    '/en',
                    '/en/ricerca/regioni/asia',
                    '/en/ricerca/regioni/china',
                    '/en/pubblicazioni',
                    '/en/tags/china',
                    '/en/search?search_api_fulltext=china',
                    '/en/research'
                ]
            },
            'ASPI': {
                'name': 'Australian Strategic Policy Institute',
                'base_url': 'https://www.aspi.org.au',
                'specialized_paths': [
                    '',
                    '/report',
                    '/search?keywords=china',
                    '/topics/china',
                    '/program/international-cyber-policy-centre',
                    '/program/defence-strategy-and-capability',
                    '/publications',
                    '/china',
                    '/report/china-defence-universities-tracker'
                ]
            },
            'IDSA': {
                'name': 'Institute for Defence Studies',
                'base_url': 'https://www.idsa.in',
                'specialized_paths': [
                    '',
                    '/china',
                    '/askstheexpert/china',
                    '/category/china',
                    '/search/node/china',
                    '/specialfeature/china',
                    '/backgrounder/china',
                    '/issuebrief',
                    '/publication'
                ]
            },
            'ORF': {
                'name': 'Observer Research Foundation',
                'base_url': 'https://www.orfonline.org',
                'specialized_paths': [
                    '',
                    '/topics/china',
                    '/region/china',
                    '/research',
                    '/expert/china',
                    '/tags/china',
                    '/search?q=china',
                    '/publications'
                ]
            },
            'ISEAS': {
                'name': 'ISEAS Yusof Ishak',
                'base_url': 'https://www.iseas.edu.sg',
                'specialized_paths': [
                    '',
                    '/articles-commentaries',
                    '/articles-commentaries/iseas-perspective',
                    '/centres-and-programmes/asean-studies-centre',
                    '/centres-and-programmes/regional-strategic-and-political-studies-programme',
                    '/search?q=china',
                    '/category/china',
                    '/publications'
                ]
            },
            'RSIS': {
                'name': 'S. Rajaratnam School',
                'base_url': 'https://www.rsis.edu.sg',
                'specialized_paths': [
                    '',
                    '/research',
                    '/research/china-programme',
                    '/publications',
                    '/publications/search?keyword=china',
                    '/research/idss-papers',
                    '/staff-publication',
                    '/commentary'
                ]
            },
            'NBR': {
                'name': 'National Bureau of Asian Research',
                'base_url': 'https://www.nbr.org',
                'specialized_paths': [
                    '',
                    '/research/china',
                    '/topics/china',
                    '/publications',
                    '/publications?topic=china',
                    '/research',
                    '/search?q=china',
                    '/asia-policy'
                ]
            },
            'MITRE': {
                'name': 'MITRE Corporation',
                'base_url': 'https://www.mitre.org',
                'specialized_paths': [
                    '',
                    '/publications',
                    '/publications/all/c/china',
                    '/focus-areas/cybersecurity',
                    '/news-insights',
                    '/search?search=china',
                    '/focus-areas',
                    '/publications/technical-papers'
                ]
            }
        }

    def fetch_page(self, url: str, timeout: int = 7) -> str:
        """Fetch page with longer timeout"""
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5'
            })
            with urllib.request.urlopen(req, timeout=timeout) as response:
                if response.status == 200:
                    return response.read().decode('utf-8', errors='ignore')
        except Exception as e:
            return ''
        return ''

    def analyze_content(self, html: str) -> dict:
        """Analyze page for China content"""
        text_lower = html.lower()

        # Count China mentions
        china_count = (text_lower.count('china') + text_lower.count('chinese') +
                      text_lower.count('beijing') + text_lower.count('prc'))

        # Extract title
        title_match = re.search(r'<title[^>]*>([^<]+)</title>', html, re.IGNORECASE)
        title = title_match.group(1).strip() if title_match else 'No title'

        # Look for specific indicators
        has_publications = 'publication' in text_lower or 'article' in text_lower
        has_research = 'research' in text_lower or 'analysis' in text_lower
        has_asia = 'asia' in text_lower or 'pacific' in text_lower

        # Extract sample article titles if present
        article_titles = []
        title_patterns = [
            r'<h[1-6][^>]*>([^<]*[Cc]hina[^<]*)</h[1-6]>',
            r'title="([^"]*[Cc]hina[^"]*)"',
            r'<a[^>]*>([^<]*[Cc]hina[^<]*)</a>'
        ]

        for pattern in title_patterns[:1]:  # Just check headlines
            matches = re.findall(pattern, html)
            for match in matches[:3]:  # First 3 matches
                clean_title = re.sub(r'<[^>]+>', '', match).strip()
                if len(clean_title) > 10 and len(clean_title) < 200:
                    article_titles.append(clean_title)

        return {
            'title': title,
            'china_mentions': china_count,
            'has_publications': has_publications,
            'has_research': has_research,
            'has_asia': has_asia,
            'page_size': len(html),
            'sample_articles': article_titles[:3]
        }

    def investigate_think_tank(self, key: str, info: dict) -> dict:
        """Deep investigation of a single think tank"""
        print(f"\n{'='*60}")
        print(f"INVESTIGATING: {info['name']}")
        print(f"Base URL: {info['base_url']}")
        print(f"Testing {len(info['specialized_paths'])} specialized paths")
        print('-'*60)

        result = {
            'name': info['name'],
            'base_url': info['base_url'],
            'china_found': False,
            'working_paths': [],
            'best_path': None,
            'max_mentions': 0,
            'sample_content': []
        }

        for path in info['specialized_paths']:
            url = urllib.parse.urljoin(info['base_url'], path)
            print(f"\nTesting: {path or '/'}")

            html = self.fetch_page(url)
            if html and len(html) > 500:
                analysis = self.analyze_content(html)

                print(f"  Status: SUCCESS ({len(html)} bytes)")
                print(f"  Title: {analysis['title'][:60]}")
                print(f"  China mentions: {analysis['china_mentions']}")

                if analysis['china_mentions'] > 0:
                    result['china_found'] = True
                    path_data = {
                        'path': path or '/',
                        'mentions': analysis['china_mentions'],
                        'title': analysis['title'],
                        'has_publications': analysis['has_publications'],
                        'has_research': analysis['has_research']
                    }

                    if analysis['sample_articles']:
                        path_data['samples'] = analysis['sample_articles']
                        print(f"  Sample content found:")
                        for sample in analysis['sample_articles'][:2]:
                            print(f"    - {sample[:80]}")

                    result['working_paths'].append(path_data)

                    if analysis['china_mentions'] > result['max_mentions']:
                        result['max_mentions'] = analysis['china_mentions']
                        result['best_path'] = path or '/'
                        result['sample_content'] = analysis['sample_articles']
            else:
                print(f"  Status: FAILED (no content or error)")

            time.sleep(0.5)  # Rate limiting

        # Summary for this think tank
        if result['china_found']:
            print(f"\n[+] CHINA CONTENT CONFIRMED")
            print(f"    Best path: {result['best_path']} ({result['max_mentions']} mentions)")
            if result['sample_content']:
                print(f"    Sample articles found: {len(result['sample_content'])}")
        else:
            print(f"\n[-] NO CHINA CONTENT FOUND")
            print(f"    May need different access method or paths")

        return result

    def run_investigation(self):
        """Run investigation on all targets"""
        all_results = {}

        print("="*60)
        print("REINVESTIGATION OF THINK TANKS")
        print("="*60)
        print(f"Investigating {len(self.targets)} think tanks with specialized paths")

        for key, info in self.targets.items():
            result = self.investigate_think_tank(key, info)
            all_results[key] = result
            time.sleep(1)  # Pause between think tanks

        return all_results

    def save_results(self, results: dict):
        """Save investigation results"""
        # Prepare summary
        with_china = [k for k, v in results.items() if v['china_found']]
        without_china = [k for k, v in results.items() if not v['china_found']]

        summary = {
            'investigation_date': datetime.now().isoformat(),
            'total_investigated': len(results),
            'with_china_content': len(with_china),
            'without_china_content': len(without_china),
            'success_rate': f"{len(with_china)/len(results)*100:.1f}%"
        }

        output = {
            'summary': summary,
            'results': results,
            'confirmed_sources': {},
            'still_missing': []
        }

        # Extract confirmed sources
        for key, data in results.items():
            if data['china_found']:
                output['confirmed_sources'][key] = {
                    'name': data['name'],
                    'base_url': data['base_url'],
                    'best_path': data['best_path'],
                    'china_mentions': data['max_mentions'],
                    'sample_content': data['sample_content'][:2] if data['sample_content'] else []
                }
            else:
                output['still_missing'].append(data['name'])

        # Save to file
        with open('data/test_harvest/reinvestigation_results.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        # Print summary
        print("\n" + "="*60)
        print("REINVESTIGATION SUMMARY")
        print("="*60)
        print(f"Total investigated: {summary['total_investigated']}")
        print(f"Now with China content: {summary['with_china_content']}")
        print(f"Still without content: {summary['without_china_content']}")
        print(f"Success rate: {summary['success_rate']}")

        if with_china:
            print(f"\n[+] NEWLY CONFIRMED SOURCES:")
            for key in with_china:
                r = results[key]
                print(f"  {r['name']}: {r['best_path']} ({r['max_mentions']} mentions)")

        if without_china:
            print(f"\n[-] STILL NO CONTENT (may need API/login):")
            for key in without_china:
                print(f"  {results[key]['name']}")

        print(f"\nDetailed results saved to: data/test_harvest/reinvestigation_results.json")

if __name__ == '__main__':
    investigator = ThinkTankReinvestigator()
    results = investigator.run_investigation()
    investigator.save_results(results)

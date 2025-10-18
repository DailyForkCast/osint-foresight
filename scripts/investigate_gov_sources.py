#!/usr/bin/env python3
"""
Investigate US Government/Military Sources for China Research
Identify and test key government repositories and reports
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

class GovSourceInvestigator:
    def __init__(self):
        self.sources = {
            'NDU_CSCMA': {
                'name': 'NDU Center for Study of Chinese Military Affairs',
                'base_url': 'https://digitalcommons.ndu.edu',
                'paths': [
                    '/cscma-allpubs/',
                    '/china-strategic-perspectives/',
                    '/cscma-books/',
                    '/cscma-commentary/',
                    '/cscma-testimonies/'
                ],
                'type': 'Military Academic',
                'focus': 'Chinese military strategy and competition'
            },
            'DoD_CMPR': {
                'name': 'DoD China Military Power Report',
                'base_url': 'https://www.defense.gov',
                'paths': [
                    '/News/Releases/Release/Article/',
                    '/Portals/1/Documents/pubs/',
                    '/News/Special-Reports/',
                    '/News/Releases/'
                ],
                'alternate_url': 'https://media.defense.gov',
                'type': 'Annual Report',
                'focus': 'Annual assessment of PLA capabilities'
            },
            'USCC': {
                'name': 'US-China Economic and Security Review Commission',
                'base_url': 'https://www.uscc.gov',
                'paths': [
                    '/Research',
                    '/Research/Research-Archive',
                    '/Annual-Reports',
                    '/Hearings',
                    '/Research/Staff-Research'
                ],
                'type': 'Congressional Commission',
                'focus': 'Economic and security implications of US-China relationship'
            },
            'CRS': {
                'name': 'Congressional Research Service',
                'base_url': 'https://crsreports.congress.gov',
                'paths': [
                    '/',
                    '/search/#/?termsInTitle=china',
                    '/product/pdf/',
                    '/reports'
                ],
                'type': 'Congressional Research',
                'focus': 'Policy analysis for Congress on China issues'
            },
            'DIA': {
                'name': 'Defense Intelligence Agency',
                'base_url': 'https://www.dia.mil',
                'paths': [
                    '/News/Articles/',
                    '/News/Speeches-and-Testimonies/',
                    '/Portals/110/Documents/',
                    '/Military-Power-Publications/'
                ],
                'type': 'Intelligence Agency',
                'focus': 'China military intelligence assessments'
            },
            'State_Dept': {
                'name': 'State Department China Reports',
                'base_url': 'https://www.state.gov',
                'paths': [
                    '/reports/2024-report-on-adherence-to-and-compliance-with-arms-control/',
                    '/bureaus-offices/under-secretary-for-arms-control-and-international-security/',
                    '/military-civil-fusion/',
                    '/key-topics-bureau-of-east-asian-and-pacific-affairs/china/',
                    '/reports/'
                ],
                'type': 'Diplomatic/Policy',
                'focus': 'China diplomatic and human rights reports'
            },
            'ODNI': {
                'name': 'Office of Director of National Intelligence',
                'base_url': 'https://www.dni.gov',
                'paths': [
                    '/index.php/newsroom/reports-publications',
                    '/files/ODNI/documents/',
                    '/index.php/what-we-do/what-is-intelligence',
                    '/index.php/nctc-home'
                ],
                'type': 'Intelligence Community',
                'focus': 'Annual Threat Assessment including China'
            },
            'CSET': {
                'name': 'Center for Security and Emerging Technology',
                'base_url': 'https://cset.georgetown.edu',
                'paths': [
                    '/research/',
                    '/publications/',
                    '/research/chinese-talent-program-tracker/',
                    '/research/map-of-science/',
                    '/research/foretell/'
                ],
                'type': 'University/Government Partnership',
                'focus': 'China AI and emerging technology competition'
            }
        }

    def test_url(self, url: str, timeout: int = 5) -> dict:
        """Test a URL and analyze content"""
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            with urllib.request.urlopen(req, timeout=timeout) as response:
                if response.status == 200:
                    content = response.read(102400).decode('utf-8', errors='ignore')

                    # Count China mentions
                    content_lower = content.lower()
                    china_count = (content_lower.count('china') +
                                 content_lower.count('chinese') +
                                 content_lower.count('prc') +
                                 content_lower.count('pla'))

                    # Extract title
                    title_match = re.search(r'<title[^>]*>([^<]+)</title>', content, re.IGNORECASE)
                    title = title_match.group(1).strip() if title_match else 'No title'

                    return {
                        'status': 'SUCCESS',
                        'china_mentions': china_count,
                        'title': title[:100],
                        'size': len(content)
                    }
        except Exception as e:
            return {'status': 'ERROR', 'error': str(e)[:50]}

        return {'status': 'FAILED'}

    def investigate_source(self, key: str, info: dict) -> dict:
        """Investigate a single government source"""
        print(f"\n{'='*70}")
        print(f"{info['name']}")
        print(f"Type: {info['type']}")
        print(f"Focus: {info['focus']}")
        print('-'*70)

        results = {
            'name': info['name'],
            'base_url': info['base_url'],
            'type': info['type'],
            'focus': info['focus'],
            'working_paths': [],
            'china_content_found': False,
            'total_china_mentions': 0
        }

        for path in info['paths']:
            url = urllib.parse.urljoin(info['base_url'], path)
            print(f"\nTesting: {path}")

            result = self.test_url(url)

            if result['status'] == 'SUCCESS':
                print(f"  Status: SUCCESS ({result['size']} bytes)")
                print(f"  Title: {result['title']}")
                print(f"  China mentions: {result['china_mentions']}")

                if result['china_mentions'] > 0:
                    results['china_content_found'] = True
                    results['total_china_mentions'] += result['china_mentions']
                    results['working_paths'].append({
                        'path': path,
                        'mentions': result['china_mentions'],
                        'title': result['title']
                    })
            else:
                print(f"  Status: {result['status']}")
                if 'error' in result:
                    print(f"  Error: {result['error']}")

            time.sleep(0.5)

        return results

    def investigate_ndu_special(self):
        """Special investigation of NDU Digital Commons"""
        print("\n" + "="*70)
        print("SPECIAL: NDU DIGITAL COMMONS DEEP DIVE")
        print("="*70)

        ndu_url = 'https://digitalcommons.ndu.edu/cscma-allpubs/'
        print(f"\nTesting main CSCMA publications page:")
        print(f"  {ndu_url}")

        result = self.test_url(ndu_url, timeout=10)
        if result['status'] == 'SUCCESS':
            print(f"  SUCCESS: {result['china_mentions']} China mentions")
            print(f"  Page size: {result['size']} bytes")

            # Test specific document patterns
            doc_patterns = [
                'https://digitalcommons.ndu.edu/cgi/viewcontent.cgi?article=',
                'https://digitalcommons.ndu.edu/china-strategic-perspectives/',
                'https://digitalcommons.ndu.edu/cscma-books/'
            ]

            print(f"\nDocument access patterns:")
            for pattern in doc_patterns:
                print(f"  - {pattern}...")

    def investigate_dod_cmpr(self):
        """Special investigation of DoD China Military Power Report"""
        print("\n" + "="*70)
        print("SPECIAL: DoD CHINA MILITARY POWER REPORT")
        print("="*70)

        # Known CMPR URLs
        cmpr_urls = [
            'https://media.defense.gov/2023/Oct/19/2003323409/-1/-1/1/2023-MILITARY-AND-SECURITY-DEVELOPMENTS-INVOLVING-THE-PEOPLES-REPUBLIC-OF-CHINA.PDF',
            'https://www.defense.gov/CMPR/',
            'https://media.defense.gov/2022/Nov/29/2003122279/-1/-1/1/2022-MILITARY-AND-SECURITY-DEVELOPMENTS-INVOLVING-THE-PEOPLES-REPUBLIC-OF-CHINA.PDF'
        ]

        print("\nKnown China Military Power Report locations:")
        for url in cmpr_urls:
            if '.PDF' in url:
                print(f"  [PDF] {url[-50:]}")
            else:
                print(f"  [Web] {url}")
                result = self.test_url(url)
                if result['status'] == 'SUCCESS':
                    print(f"    Found: {result['china_mentions']} China mentions")

    def run_investigation(self):
        """Run investigation on all government sources"""
        all_results = {}

        print("="*70)
        print("US GOVERNMENT/MILITARY CHINA RESEARCH SOURCES")
        print("="*70)
        print(f"Investigating {len(self.sources)} key government sources")

        # Test main sources
        for key, info in self.sources.items():
            if key in ['NDU_CSCMA', 'USCC', 'CRS', 'CSET']:  # Priority sources
                results = self.investigate_source(key, info)
                all_results[key] = results
                time.sleep(1)

        # Special investigations
        self.investigate_ndu_special()
        self.investigate_dod_cmpr()

        return all_results

    def print_summary(self, results):
        """Print summary of findings"""
        print("\n" + "="*70)
        print("GOVERNMENT SOURCES SUMMARY")
        print("="*70)

        confirmed = [k for k, v in results.items() if v['china_content_found']]

        print(f"\nSources tested: {len(results)}")
        print(f"Sources with China content: {len(confirmed)}")

        print("\n[+] CONFIRMED GOVERNMENT SOURCES:")
        for key in confirmed:
            r = results[key]
            print(f"\n{r['name']}")
            print(f"  Type: {r['type']}")
            print(f"  Focus: {r['focus']}")
            print(f"  China mentions: {r['total_china_mentions']}")
            if r['working_paths']:
                print(f"  Best path: {r['working_paths'][0]['path']}")

        print("\n[+] RECOMMENDED ADDITIONS:")
        print("\n1. NDU CSCMA - National Defense University")
        print("   URL: https://digitalcommons.ndu.edu/cscma-allpubs/")
        print("   Content: China Strategic Perspectives, military analysis")

        print("\n2. USCC - US-China Economic & Security Review Commission")
        print("   URL: https://www.uscc.gov")
        print("   Content: Annual reports, hearings, research archive")

        print("\n3. DoD China Military Power Report (Annual)")
        print("   URL: https://www.defense.gov/CMPR/")
        print("   Content: Comprehensive PLA assessment")

        print("\n4. Congressional Research Service")
        print("   URL: https://crsreports.congress.gov")
        print("   Content: China policy reports for Congress")

        print("\n5. CSET - Georgetown")
        print("   URL: https://cset.georgetown.edu")
        print("   Content: China AI and tech competition research")

        print("\n6. State Department")
        print("   URL: https://www.state.gov")
        print("   Content: Military-Civil Fusion, compliance reports")

if __name__ == '__main__':
    investigator = GovSourceInvestigator()
    results = investigator.run_investigation()
    investigator.print_summary(results)

    # Save results
    output = {
        'investigation_date': datetime.now().isoformat(),
        'sources_investigated': len(results),
        'results': results,
        'recommendations': [
            'NDU CSCMA - Priority for military strategy',
            'USCC - Priority for economic/security nexus',
            'DoD CMPR - Annual must-read report',
            'CRS - Congress-focused analysis',
            'CSET - AI/tech competition focus',
            'State Dept - MCF and compliance'
        ]
    }

    with open('data/test_harvest/gov_sources_investigation.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n\nResults saved to: data/test_harvest/gov_sources_investigation.json")

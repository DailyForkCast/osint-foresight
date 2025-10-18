#!/usr/bin/env python3
"""
Investigate CASI - China Aerospace Studies Institute
US Air Force's dedicated China aerospace/military research center
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

class CASIInvestigator:
    def __init__(self):
        self.base_url = 'https://www.airuniversity.af.edu'
        self.casi_paths = []
        self.china_content = []

    def fetch_page(self, url: str, timeout: int = 7) -> str:
        """Fetch page content"""
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            })
            with urllib.request.urlopen(req, timeout=timeout) as response:
                if response.status == 200:
                    return response.read().decode('utf-8', errors='ignore')
        except Exception as e:
            print(f"    Error: {str(e)[:50]}")
        return ''

    def analyze_content(self, html: str) -> dict:
        """Analyze page for China content"""
        text_lower = html.lower()

        # Count China mentions
        china_count = (text_lower.count('china') + text_lower.count('chinese') +
                      text_lower.count('pla') + text_lower.count('prc') +
                      text_lower.count('beijing'))

        # Extract title
        title_match = re.search(r'<title[^>]*>([^<]+)</title>', html, re.IGNORECASE)
        title = title_match.group(1).strip() if title_match else 'No title'

        # Look for specific CASI indicators
        casi_mentions = text_lower.count('casi') + text_lower.count('china aerospace')
        aerospace_mentions = text_lower.count('aerospace') + text_lower.count('space')
        military_mentions = text_lower.count('military') + text_lower.count('defense')

        # Extract publication/report titles
        report_titles = []
        patterns = [
            r'<h[1-6][^>]*>([^<]*[Cc]hina[^<]*)</h[1-6]>',
            r'<a[^>]*>([^<]*[Cc]hina[^<]*)</a>',
            r'title="([^"]*[Cc]hina[^"]*)"'
        ]

        for pattern in patterns[:2]:
            matches = re.findall(pattern, html)
            for match in matches[:5]:
                clean = re.sub(r'<[^>]+>', '', match).strip()
                if 20 < len(clean) < 200 and 'china' in clean.lower():
                    report_titles.append(clean)

        return {
            'title': title,
            'china_mentions': china_count,
            'casi_mentions': casi_mentions,
            'aerospace_mentions': aerospace_mentions,
            'military_mentions': military_mentions,
            'report_titles': list(set(report_titles))[:5],
            'page_size': len(html)
        }

    def investigate(self):
        """Investigate CASI website"""
        print("="*70)
        print("CHINA AEROSPACE STUDIES INSTITUTE (CASI) INVESTIGATION")
        print("="*70)
        print("US Air University's China military/aerospace research center")
        print("-"*70)

        # Test paths for CASI
        test_paths = [
            ('/CASI/', 'CASI Homepage'),
            ('/CASI/Publications/', 'CASI Publications'),
            ('/CASI/Research/', 'CASI Research'),
            ('/CASI/About/', 'CASI About'),
            ('/CASI/Display/Article/', 'CASI Articles'),
            ('/CASI/Books/', 'CASI Books'),
            ('/CASI/Reports/', 'CASI Reports'),
            ('/CASI/Translations/', 'CASI Translations'),
            ('/CASI/Analysis/', 'CASI Analysis'),
            ('/CASI/PLA/', 'PLA Research'),
            ('/CASI/China/', 'China Focus'),
            ('/CASI/Space/', 'Space Research'),
            ('/Portals/10/', 'Portal 10 (CASI)'),
            ('/Wild-Blue-Yonder/CASI/', 'Wild Blue Yonder CASI')
        ]

        results = {}
        successful_paths = []

        for path, description in test_paths:
            url = urllib.parse.urljoin(self.base_url, path)
            print(f"\nTesting: {description}")
            print(f"  URL: {url}")

            html = self.fetch_page(url)
            if html:
                analysis = self.analyze_content(html)
                results[path] = analysis

                print(f"  Status: SUCCESS ({len(html)} bytes)")
                print(f"  Title: {analysis['title'][:60]}")
                print(f"  China mentions: {analysis['china_mentions']}")
                print(f"  CASI mentions: {analysis['casi_mentions']}")

                if analysis['china_mentions'] > 0:
                    successful_paths.append({
                        'path': path,
                        'description': description,
                        'china_mentions': analysis['china_mentions'],
                        'title': analysis['title']
                    })

                    if analysis['report_titles']:
                        print(f"  Sample China content found:")
                        for report in analysis['report_titles'][:3]:
                            print(f"    - {report[:80]}")

                    self.china_content.append(analysis)
            else:
                print(f"  Status: FAILED")

            time.sleep(0.5)

        return results, successful_paths

    def test_document_access(self):
        """Test access to CASI documents and PDFs"""
        print("\n" + "="*70)
        print("TESTING CASI DOCUMENT ACCESS")
        print("-"*70)

        # Common CASI document patterns
        doc_patterns = [
            '/Portals/10/Documents/',
            '/Portals/10/PDF/',
            '/CASI/Documents/',
            '/LinkClick.aspx?fileticket=',
            '/Portals/10/Imports/CASI/'
        ]

        print("\nDocument path patterns:")
        for pattern in doc_patterns:
            print(f"  {pattern}")

        # Test a known CASI publication path
        test_url = 'https://www.airuniversity.af.edu/CASI/Display/Article/2299104/'
        print(f"\nTesting sample article URL:")
        print(f"  {test_url}")

        html = self.fetch_page(test_url)
        if html:
            analysis = self.analyze_content(html)
            if analysis['china_mentions'] > 0:
                print(f"  SUCCESS: Found {analysis['china_mentions']} China mentions")
                if analysis['report_titles']:
                    print(f"  Content: {analysis['report_titles'][0][:100]}")

    def print_summary(self, results, successful_paths):
        """Print investigation summary"""
        print("\n" + "="*70)
        print("CASI INVESTIGATION SUMMARY")
        print("="*70)

        print(f"\nTotal paths tested: {len(results)}")
        print(f"Successful paths with China content: {len(successful_paths)}")

        if successful_paths:
            print(f"\n[+] CONFIRMED: CASI has extensive China aerospace/military content")
            print(f"\nBest paths for China content:")
            for item in sorted(successful_paths, key=lambda x: x['china_mentions'], reverse=True)[:5]:
                print(f"  {item['description']:20} {item['path']:25} ({item['china_mentions']} mentions)")

        # Calculate total China mentions
        total_mentions = sum(r['china_mentions'] for r in results.values())
        print(f"\nTotal China mentions across all pages: {total_mentions}")

        # Sample content found
        all_titles = []
        for result in results.values():
            all_titles.extend(result.get('report_titles', []))

        if all_titles:
            print(f"\nSample CASI China research topics:")
            for title in list(set(all_titles))[:5]:
                print(f"  - {title}")

        print(f"\n[+] RECOMMENDATION: Add CASI as HIGH PRIORITY source")
        print(f"    Specialization: China aerospace, military, PLA research")
        print(f"    Type: US Government/Military think tank")

if __name__ == '__main__':
    investigator = CASIInvestigator()

    # Main investigation
    results, successful_paths = investigator.investigate()

    # Test document access
    investigator.test_document_access()

    # Print summary
    investigator.print_summary(results, successful_paths)

    # Save results
    output = {
        'name': 'China Aerospace Studies Institute (CASI)',
        'base_url': 'https://www.airuniversity.af.edu/CASI/',
        'type': 'US Government/Military',
        'specialization': 'China aerospace, military, PLA research',
        'investigation_date': datetime.now().isoformat(),
        'china_content_confirmed': len(successful_paths) > 0,
        'working_paths': successful_paths,
        'priority': 'HIGH',
        'notes': 'US Air Force dedicated China research institute'
    }

    with open('data/test_harvest/casi_investigation.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: data/test_harvest/casi_investigation.json")

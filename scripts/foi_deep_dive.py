#!/usr/bin/env python3
"""
FOI Deep Dive Investigation
Identify what's blocking access and find working paths
"""

import urllib.request
import urllib.parse
import urllib.error
import ssl
import re
import json
import time
from datetime import datetime

# Disable SSL verification
ssl._create_default_https_context = ssl._create_unverified_context

class FOIDeepDive:
    def __init__(self):
        self.base_url = 'https://www.foi.se'
        self.successful_paths = []
        self.failed_paths = []
        self.blocking_patterns = {}

    def test_url_detailed(self, url: str) -> dict:
        """Test URL with detailed error reporting"""
        result = {
            'url': url,
            'status': None,
            'status_code': None,
            'error_type': None,
            'error_details': None,
            'content_type': None,
            'content_length': 0,
            'china_mentions': 0,
            'redirect_url': None
        }

        try:
            # Create request with multiple headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }

            req = urllib.request.Request(url, headers=headers)

            # Try to open with longer timeout
            with urllib.request.urlopen(req, timeout=10) as response:
                result['status_code'] = response.status
                result['content_type'] = response.headers.get('Content-Type', 'Unknown')

                # Check for redirects
                if response.url != url:
                    result['redirect_url'] = response.url

                # Read content
                content = response.read()

                # Try to decode
                try:
                    if 'gzip' in response.headers.get('Content-Encoding', ''):
                        import gzip
                        content = gzip.decompress(content)

                    text = content.decode('utf-8', errors='ignore')
                    result['content_length'] = len(text)

                    # Count China mentions
                    text_lower = text.lower()
                    result['china_mentions'] = (text_lower.count('china') +
                                               text_lower.count('kina') +  # Swedish for China
                                               text_lower.count('chinese'))

                    result['status'] = 'SUCCESS'

                except Exception as decode_error:
                    result['error_type'] = 'DECODE_ERROR'
                    result['error_details'] = str(decode_error)
                    result['status'] = 'PARTIAL'

        except urllib.error.HTTPError as e:
            result['status'] = 'HTTP_ERROR'
            result['status_code'] = e.code
            result['error_type'] = f'HTTP {e.code}'
            result['error_details'] = e.reason

        except urllib.error.URLError as e:
            result['status'] = 'URL_ERROR'
            result['error_type'] = 'CONNECTION'
            result['error_details'] = str(e.reason)

        except TimeoutError:
            result['status'] = 'TIMEOUT'
            result['error_type'] = 'TIMEOUT'
            result['error_details'] = 'Request timed out after 10 seconds'

        except Exception as e:
            result['status'] = 'ERROR'
            result['error_type'] = type(e).__name__
            result['error_details'] = str(e)

        return result

    def investigate_paths(self):
        """Test various path patterns"""

        # Comprehensive path list
        test_paths = [
            # Base paths
            ('/', 'Homepage'),
            ('/en', 'English homepage'),
            ('/en/', 'English homepage with slash'),

            # Reports paths - various formats
            ('/rapporter', 'Swedish reports'),
            ('/reports', 'English reports simple'),
            ('/en/reports', 'English reports with /en'),
            ('/en/foi/reports', 'Full English reports path'),
            ('/en/foi/reports.html', 'Reports with .html'),
            ('/en/foi/reports/', 'Reports with trailing slash'),

            # Search variations
            ('/search', 'Simple search'),
            ('/en/search', 'English search'),
            ('/sok', 'Swedish search'),
            ('/en/search?q=china', 'Search with query'),
            ('/en/foi/search.html?q=china', 'Full search path'),

            # News paths
            ('/news', 'Simple news'),
            ('/en/news', 'English news'),
            ('/nyheter', 'Swedish news'),
            ('/en/foi/news-and-pressroom', 'News without .html'),
            ('/en/foi/news-and-pressroom/', 'News with slash'),
            ('/en/foi/news-and-pressroom/news', 'News subdirectory'),

            # Research areas
            ('/research', 'Simple research'),
            ('/en/research', 'English research'),
            ('/forskning', 'Swedish research'),
            ('/en/foi/research', 'Full research path'),
            ('/en/foi/research/security-policy', 'Security policy'),

            # Direct China attempts
            ('/china', 'Direct China'),
            ('/kina', 'Swedish China'),
            ('/en/china', 'English China'),
            ('/en/topics/china', 'Topics China'),
            ('/en/research/china', 'Research China'),

            # API/data endpoints
            ('/api/search?q=china', 'API search'),
            ('/data/publications', 'Data endpoint'),

            # Known working patterns from user URLs
            ('/en/foi/news-and-pressroom/news/2025-09-17-developing-an-analytical-framework-and-methods-for-studying-chinas-military-power.html',
             'Known China article'),
            ('/en/foi/reports/report-summary.html', 'Report summary base')
        ]

        results = []

        print("="*70)
        print("FOI DEEP DIVE INVESTIGATION")
        print("="*70)
        print(f"Testing {len(test_paths)} different path patterns")
        print("-"*70)

        for path, description in test_paths:
            url = urllib.parse.urljoin(self.base_url, path)
            print(f"\nTesting: {description}")
            print(f"  Path: {path}")

            result = self.test_url_detailed(url)
            results.append(result)

            # Print detailed results
            print(f"  Status: {result['status']}")

            if result['status'] == 'SUCCESS':
                print(f"  [OK] Content length: {result['content_length']} bytes")
                print(f"  [OK] Content type: {result['content_type']}")
                if result['china_mentions'] > 0:
                    print(f"  [OK] China mentions: {result['china_mentions']}")
                if result['redirect_url']:
                    print(f"  [OK] Redirected to: {result['redirect_url']}")
                self.successful_paths.append((path, description, result))

            elif result['status'] == 'HTTP_ERROR':
                print(f"  [X] HTTP Error: {result['status_code']} - {result['error_details']}")
                self.failed_paths.append((path, description, result))

                # Track error patterns
                error_key = f"HTTP_{result['status_code']}"
                if error_key not in self.blocking_patterns:
                    self.blocking_patterns[error_key] = []
                self.blocking_patterns[error_key].append(path)

            else:
                print(f"  [X] Error: {result['error_type']} - {result['error_details']}")
                self.failed_paths.append((path, description, result))

                if result['error_type'] not in self.blocking_patterns:
                    self.blocking_patterns[result['error_type']] = []
                self.blocking_patterns[result['error_type']].append(path)

            time.sleep(0.5)  # Rate limiting

        return results

    def test_headers_and_methods(self):
        """Test different headers and methods"""
        print("\n" + "="*70)
        print("TESTING DIFFERENT ACCESS METHODS")
        print("-"*70)

        test_url = self.base_url + '/en/foi/reports.html'

        # Test 1: Different User-Agents
        user_agents = [
            ('Chrome', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'),
            ('Firefox', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'),
            ('Bot', 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'),
            ('Curl', 'curl/7.68.0'),
            ('Python', 'Python-urllib/3.9')
        ]

        print("\nTesting different User-Agents:")
        for name, agent in user_agents:
            try:
                req = urllib.request.Request(test_url, headers={'User-Agent': agent})
                with urllib.request.urlopen(req, timeout=5) as response:
                    print(f"  {name:10} - SUCCESS (Status: {response.status})")
            except Exception as e:
                error_msg = str(e).split('\n')[0] if '\n' in str(e) else str(e)[:50]
                print(f"  {name:10} - FAILED ({error_msg})")
            time.sleep(0.5)

        # Test 2: HEAD request
        print("\nTesting HEAD request:")
        try:
            req = urllib.request.Request(test_url, headers={'User-Agent': 'Mozilla/5.0'})
            req.get_method = lambda: 'HEAD'
            with urllib.request.urlopen(req, timeout=5) as response:
                print(f"  HEAD request - SUCCESS")
                print(f"    Server: {response.headers.get('Server', 'Unknown')}")
                print(f"    Content-Type: {response.headers.get('Content-Type', 'Unknown')}")
        except Exception as e:
            print(f"  HEAD request - FAILED ({str(e)[:50]})")

    def analyze_blocking(self):
        """Analyze what's blocking access"""
        print("\n" + "="*70)
        print("BLOCKING ANALYSIS")
        print("-"*70)

        if self.blocking_patterns:
            print("\nError patterns detected:")
            for error_type, paths in self.blocking_patterns.items():
                print(f"\n{error_type}: {len(paths)} paths affected")
                for path in paths[:3]:  # Show first 3
                    print(f"  - {path}")

        if self.successful_paths:
            print(f"\n[+] SUCCESSFUL PATHS: {len(self.successful_paths)}")
            for path, desc, result in self.successful_paths:
                if result['china_mentions'] > 0:
                    print(f"  {desc}: {path}")
                    print(f"    China mentions: {result['china_mentions']}")

        # Diagnosis
        print("\n" + "="*70)
        print("DIAGNOSIS")
        print("-"*70)

        if 'HTTP_404' in self.blocking_patterns:
            print("\n[!] Many 404 errors - Paths may have changed or require exact URLs")

        if 'HTTP_403' in self.blocking_patterns:
            print("\n[!] 403 Forbidden errors - May require authentication or different access method")

        if 'HTTP_500' in self.blocking_patterns or 'HTTP_502' in self.blocking_patterns:
            print("\n[!] Server errors - Site may have issues or block automated access")

        if 'TIMEOUT' in self.blocking_patterns:
            print("\n[!] Timeouts - Site may be slow or blocking requests")

        if self.successful_paths:
            print("\n[+] Some paths work - Site is accessible but structure is specific")
        else:
            print("\n[-] No paths work - Site may have strong bot protection")

    def save_results(self, results):
        """Save investigation results"""
        output = {
            'investigation_date': datetime.now().isoformat(),
            'base_url': self.base_url,
            'total_paths_tested': len(results),
            'successful_paths': len(self.successful_paths),
            'failed_paths': len(self.failed_paths),
            'blocking_patterns': self.blocking_patterns,
            'working_paths': [
                {
                    'path': path,
                    'description': desc,
                    'china_mentions': result['china_mentions']
                }
                for path, desc, result in self.successful_paths
            ],
            'recommendations': []
        }

        # Add recommendations
        if self.successful_paths:
            output['recommendations'].append("Site is accessible but requires exact paths")
            output['recommendations'].append("Use known article URLs directly")
            output['recommendations'].append("Consider scraping from news listing pages")
        else:
            output['recommendations'].append("Site may require browser automation (Selenium)")
            output['recommendations'].append("Consider using RSS feeds if available")
            output['recommendations'].append("May need to respect robots.txt strictly")

        with open('data/test_harvest/foi_deep_dive.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print(f"\nResults saved to: data/test_harvest/foi_deep_dive.json")

if __name__ == '__main__':
    investigator = FOIDeepDive()

    # Run comprehensive path investigation
    results = investigator.investigate_paths()

    # Test different access methods
    investigator.test_headers_and_methods()

    # Analyze blocking patterns
    investigator.analyze_blocking()

    # Save results
    investigator.save_results(results)

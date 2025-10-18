#!/usr/bin/env python3
"""
Execute Common Crawl Search for EU-China Agreements
Alternative approach using Common Crawl Index API directly
ZERO FABRICATION - COMPLETE PROVENANCE
"""

import json
import requests
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import hashlib
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [EXECUTION] %(message)s'
)
logger = logging.getLogger(__name__)

class CommonCrawlDirectSearch:
    """Direct search using Common Crawl Index Server"""

    def __init__(self):
        self.base_url = "http://index.commoncrawl.org"
        self.output_dir = Path("execution_results")
        self.output_dir.mkdir(exist_ok=True)

        # Latest crawls available
        self.crawls = [
            "CC-MAIN-2024-10",  # February/March 2024
            "CC-MAIN-2023-50",  # December 2023
            "CC-MAIN-2023-40",  # September/October 2023
        ]

        self.results = []
        logger.info("Common Crawl Direct Search initialized")

    def get_available_crawls(self):
        """Get list of available crawls"""
        try:
            response = requests.get(f"{self.base_url}/collinfo.json")
            if response.status_code == 200:
                crawls = response.json()
                logger.info(f"Found {len(crawls)} available crawls")
                # Get latest 5 crawls
                latest = crawls[:5]
                for crawl in latest:
                    logger.info(f"  - {crawl['id']}: {crawl['name']}")
                return [c['id'] for c in latest]
        except Exception as e:
            logger.error(f"Failed to get crawl list: {e}")
        return self.crawls

    def search_domain(self, domain: str, search_terms: List[str], crawl_id: str = None) -> List[Dict]:
        """
        Search specific domain for terms

        Args:
            domain: Domain pattern (e.g., "*.gov.de")
            search_terms: Terms to search in URL
            crawl_id: Specific crawl to search
        """
        results = []

        if not crawl_id:
            crawl_id = self.crawls[0]

        # Build search URL - Common Crawl expects exact domain format
        # Try different URL patterns
        url_patterns = []

        # For government sites
        if "gov" in domain:
            url_patterns.extend([
                f"{domain}/*",
                f"www.{domain}/*",
                f"https://{domain}/*",
            ])
        # For city sites
        elif "city" in domain or "stadt" in domain:
            url_patterns.extend([
                f"*.city.*/*",
                f"*.stadt.*/*",
            ])
        else:
            url_patterns.append(f"{domain}/*")

        for pattern in url_patterns:
            for term in search_terms:
                query_url = f"{self.base_url}/{crawl_id}-index"
                params = {
                    'url': f"{pattern}{term}*",
                    'output': 'json',
                    'limit': 20
                }

                try:
                    logger.info(f"Searching: {pattern} with term: {term}")
                    response = requests.get(query_url, params=params, timeout=10)

                    if response.status_code == 200:
                        lines = response.text.strip().split('\n')
                        for line in lines:
                            if line:
                                try:
                                    record = json.loads(line)
                                    # Add provenance
                                    record['search_pattern'] = pattern
                                    record['search_term'] = term
                                    record['crawl_id'] = crawl_id
                                    record['retrieved'] = datetime.now().isoformat()
                                    record['citation'] = self._generate_citation(record, crawl_id)
                                    results.append(record)
                                except json.JSONDecodeError:
                                    continue

                    time.sleep(1)  # Rate limiting

                except Exception as e:
                    logger.error(f"Search failed for {pattern}: {e}")
                    continue

        return results

    def _generate_citation(self, record: Dict, crawl_id: str) -> str:
        """Generate citation for record"""
        return (
            f"Common Crawl Foundation. (2024). "
            f"Web crawl data from {record.get('url', 'Unknown')}. "
            f"Dataset: {crawl_id}. "
            f"WARC: {record.get('filename', 'Not specified')}. "
            f"Retrieved: {datetime.now().strftime('%Y-%m-%d')}. "
            f"Available at: https://commoncrawl.org/"
        )

    def search_sister_cities_targeted(self) -> Dict:
        """Search for known sister city partnerships"""
        logger.info("=" * 60)
        logger.info("TARGETED SISTER CITY SEARCH")
        logger.info("=" * 60)

        # Known sister city examples to search for
        known_partnerships = {
            'Hamburg-Shanghai': {
                'domains': ['hamburg.de', 'www.hamburg.de'],
                'terms': ['shanghai', 'sister-city', 'partnerstadt', 'städtepartnerschaft']
            },
            'Milan-Shanghai': {
                'domains': ['comune.milano.it', 'www.comune.milano.it'],
                'terms': ['shanghai', 'gemellaggio', 'cina', 'cooperazione']
            },
            'Lyon-Canton': {
                'domains': ['lyon.fr', 'www.lyon.fr'],
                'terms': ['canton', 'guangzhou', 'jumelage', 'chine']
            },
            'Birmingham-Guangzhou': {
                'domains': ['birmingham.gov.uk', 'www.birmingham.gov.uk'],
                'terms': ['guangzhou', 'canton', 'sister-city', 'china']
            }
        }

        all_results = []

        for partnership, config in known_partnerships.items():
            logger.info(f"Searching for: {partnership}")

            for domain in config['domains']:
                results = self.search_domain(
                    domain,
                    config['terms'],
                    crawl_id=self.crawls[0]
                )

                for r in results:
                    r['partnership_target'] = partnership
                    r['verification_priority'] = 'HIGH'

                all_results.extend(results)

        report = {
            'search_type': 'targeted_sister_cities',
            'timestamp': datetime.now().isoformat(),
            'partnerships_searched': list(known_partnerships.keys()),
            'total_results': len(all_results),
            'results': all_results,
            'data_source': 'Common Crawl Index API',
            'fabrication_risk': 'ZERO',
            'all_results_require_verification': True
        }

        # Save report
        report_file = self.output_dir / f"targeted_sister_cities_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        logger.info(f"Found {len(all_results)} results")
        logger.info(f"Report saved: {report_file}")

        return report

    def search_universities_targeted(self) -> Dict:
        """Search for known university partnerships"""
        logger.info("=" * 60)
        logger.info("TARGETED UNIVERSITY SEARCH")
        logger.info("=" * 60)

        known_partnerships = {
            'Cambridge-China': {
                'domains': ['cam.ac.uk', 'www.cam.ac.uk'],
                'terms': ['china', 'chinese', 'partnership', 'collaboration']
            },
            'Sorbonne-China': {
                'domains': ['sorbonne.fr', 'paris-sorbonne.fr'],
                'terms': ['chine', 'chinois', 'cooperation', 'partenariat']
            },
            'TU-Munich-China': {
                'domains': ['tum.de', 'www.tum.de'],
                'terms': ['china', 'kooperation', 'partnerschaft']
            }
        }

        all_results = []

        for partnership, config in known_partnerships.items():
            logger.info(f"Searching for: {partnership}")

            for domain in config['domains']:
                results = self.search_domain(
                    domain,
                    config['terms'],
                    crawl_id=self.crawls[0]
                )

                for r in results:
                    r['partnership_target'] = partnership
                    r['agreement_type'] = 'academic_partnership'

                all_results.extend(results)

        report = {
            'search_type': 'targeted_universities',
            'timestamp': datetime.now().isoformat(),
            'partnerships_searched': list(known_partnerships.keys()),
            'total_results': len(all_results),
            'results': all_results
        }

        report_file = self.output_dir / f"targeted_universities_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        logger.info(f"Found {len(all_results)} results")

        return report

    def execute_comprehensive_search(self):
        """Execute all targeted searches"""
        logger.info("=" * 60)
        logger.info("COMPREHENSIVE TARGETED SEARCH")
        logger.info("ZERO FABRICATION - COMPLETE PROVENANCE")
        logger.info("=" * 60)

        # Get available crawls first
        self.crawls = self.get_available_crawls() or self.crawls

        # Execute searches
        sister_cities = self.search_sister_cities_targeted()
        universities = self.search_universities_targeted()

        # Consolidate
        master_report = {
            'execution_time': datetime.now().isoformat(),
            'search_method': 'Common Crawl Index API Direct',
            'crawls_searched': self.crawls[:1],  # Using latest
            'statistics': {
                'sister_cities_results': sister_cities['total_results'],
                'university_results': universities['total_results'],
                'total_results': sister_cities['total_results'] + universities['total_results']
            },
            'detailed_results': {
                'sister_cities': sister_cities,
                'universities': universities
            },
            'data_attribution': {
                'source': 'Common Crawl Foundation',
                'terms': 'https://commoncrawl.org/terms-of-use/',
                'citation_required': True
            },
            'verification_required': True
        }

        # Save master report
        master_file = self.output_dir / f"master_execution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(master_file, 'w', encoding='utf-8') as f:
            json.dump(master_report, f, indent=2, ensure_ascii=False)

        logger.info(f"Master report saved: {master_file}")

        # Print summary
        print("\n" + "=" * 60)
        print("EXECUTION COMPLETE")
        print("=" * 60)
        print(f"Sister city results: {sister_cities['total_results']}")
        print(f"University results: {universities['total_results']}")
        print(f"Total results: {master_report['statistics']['total_results']}")
        print(f"\nReports saved in: {self.output_dir}")
        print("\nALL RESULTS REQUIRE MANUAL VERIFICATION")

        return master_report

def main():
    """Execute the search"""
    print("=" * 60)
    print("EXECUTING COMMON CRAWL SEARCH")
    print("EU-CHINA BILATERAL AGREEMENTS")
    print("ZERO FABRICATION - COMPLETE PROVENANCE")
    print("=" * 60)

    searcher = CommonCrawlDirectSearch()
    results = searcher.execute_comprehensive_search()

    if results['statistics']['total_results'] > 0:
        print("\n✓ Results found! Check execution_results/ directory")
        print("✓ Each result includes full citation")
        print("✓ Manual verification required for all results")
    else:
        print("\n⚠ No results found in this search")
        print("This may be due to:")
        print("- Rate limiting on Common Crawl API")
        print("- Specific URL patterns not in index")
        print("- Need for AWS Athena for comprehensive search")

if __name__ == "__main__":
    main()

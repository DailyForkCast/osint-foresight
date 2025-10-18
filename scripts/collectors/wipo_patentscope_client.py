#!/usr/bin/env python3
"""
WIPO PATENTSCOPE Client

Accesses WIPO's PATENTSCOPE database including:
- PCT (Patent Cooperation Treaty) applications
- International patent families
- Global patent landscape data
- Technology classification analysis
"""

import os
import json
import time
import requests
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import logging
import xml.etree.ElementTree as ET
from urllib.parse import quote

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WIPOPatentscopeClient:
    """Client for WIPO PATENTSCOPE database"""

    def __init__(self, output_dir: str = None):
        """Initialize WIPO PATENTSCOPE client"""

        # WIPO API endpoints
        self.base_url = "https://patentscope.wipo.int"
        self.search_url = f"{self.base_url}/search/api/v1/patent/search"
        self.detail_url = f"{self.base_url}/search/api/v1/patent/detail"

        # Alternative endpoints for different data types
        self.pct_url = f"{self.base_url}/search/en/search.jsf"
        self.brand_url = f"{self.base_url}/search/api/v1/brand"

        # Setup output directory
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            self.output_dir = Path("C:/Projects/OSINT - Foresight/data/collected/wipo_patentscope")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Session setup
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'OSINT-Research-System/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })

        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 1.0  # Conservative rate limiting

    def _rate_limit(self):
        """Enforce rate limiting"""
        now = time.time()
        elapsed = now - self.last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)
        self.last_request_time = time.time()

    def search_patents(self, query: str, max_results: int = 100,
                      start: int = 0, sort_field: str = "DP") -> Dict:
        """Search patents in WIPO PATENTSCOPE

        Args:
            query: Search query string
            max_results: Maximum number of results
            start: Starting position for pagination
            sort_field: Sort field (DP=Date Published, etc.)
        """

        self._rate_limit()

        # WIPO PATENTSCOPE search parameters
        search_params = {
            "query": query,
            "maxRec": min(max_results, 500),  # WIPO limit
            "startRec": start,
            "sortField": sort_field,
            "sortOrder": "Desc"
        }

        try:
            logger.debug(f"WIPO search query: {query}")

            response = self.session.post(self.search_url, json=search_params)

            # Handle different response formats
            if response.status_code == 200:
                try:
                    return response.json()
                except:
                    # Sometimes WIPO returns XML
                    return self.parse_xml_response(response.text)
            else:
                logger.warning(f"WIPO search returned status {response.status_code}")
                return {}

        except Exception as e:
            logger.error(f"WIPO search failed: {e}")
            return {}

    def parse_xml_response(self, xml_text: str) -> Dict:
        """Parse XML response from WIPO"""

        try:
            root = ET.fromstring(xml_text)

            # Extract patent records from XML
            patents = []
            for patent_elem in root.findall('.//patent'):
                patent_data = self.extract_patent_from_xml(patent_elem)
                if patent_data:
                    patents.append(patent_data)

            return {
                'patents': patents,
                'total_found': len(patents)
            }

        except Exception as e:
            logger.error(f"Error parsing XML response: {e}")
            return {}

    def extract_patent_from_xml(self, patent_elem) -> Dict:
        """Extract patent data from XML element"""

        try:
            patent_data = {}

            # Basic fields
            patent_data['publication_number'] = self.get_xml_text(patent_elem, 'publicationNumber')
            patent_data['publication_date'] = self.get_xml_text(patent_elem, 'publicationDate')
            patent_data['application_number'] = self.get_xml_text(patent_elem, 'applicationNumber')
            patent_data['title'] = self.get_xml_text(patent_elem, 'inventionTitle')

            # Applicants
            applicants = []
            for applicant_elem in patent_elem.findall('.//applicant'):
                name = self.get_xml_text(applicant_elem, 'name')
                country = self.get_xml_text(applicant_elem, 'country')
                if name:
                    applicants.append({'name': name, 'country': country})
            patent_data['applicants'] = applicants

            # Inventors
            inventors = []
            for inventor_elem in patent_elem.findall('.//inventor'):
                name = self.get_xml_text(inventor_elem, 'name')
                if name:
                    inventors.append(name)
            patent_data['inventors'] = inventors

            # Classifications
            ipc_classes = []
            for ipc_elem in patent_elem.findall('.//ipc'):
                ipc_code = self.get_xml_text(ipc_elem, 'classificationSymbol')
                if ipc_code:
                    ipc_classes.append(ipc_code)
            patent_data['ipc_classifications'] = ipc_classes

            return patent_data

        except Exception as e:
            logger.error(f"Error extracting patent from XML: {e}")
            return {}

    def get_xml_text(self, parent_elem, tag_name: str) -> str:
        """Safely extract text from XML element"""
        elem = parent_elem.find(tag_name)
        return elem.text if elem is not None and elem.text else ''

    def search_pct_applications(self, query_params: Dict) -> List[Dict]:
        """Search PCT applications specifically

        Args:
            query_params: Dictionary with search parameters like:
                - applicant: Applicant name
                - inventor: Inventor name
                - title: Title keywords
                - abstract: Abstract keywords
                - date_from: Start date (YYYY-MM-DD)
                - date_to: End date (YYYY-MM-DD)
        """

        # Build WIPO search query string
        query_parts = []

        if query_params.get('applicant'):
            query_parts.append(f'PA:("{query_params["applicant"]}")')

        if query_params.get('inventor'):
            query_parts.append(f'IN:("{query_params["inventor"]}")')

        if query_params.get('title'):
            query_parts.append(f'TI:("{query_params["title"]}")')

        if query_params.get('abstract'):
            query_parts.append(f'AB:("{query_params["abstract"]}")')

        if query_params.get('date_from') or query_params.get('date_to'):
            date_from = query_params.get('date_from', '1900-01-01').replace('-', '')
            date_to = query_params.get('date_to', '2030-12-31').replace('-', '')
            query_parts.append(f'DP:[{date_from} TO {date_to}]')

        if not query_parts:
            raise ValueError("At least one search parameter must be provided")

        query_string = ' AND '.join(query_parts)

        logger.info(f"Searching PCT applications with query: {query_string}")

        # Execute search
        results = self.search_patents(query_string, max_results=500)

        patents = results.get('patents', [])
        logger.info(f"Found {len(patents)} PCT applications")

        return patents

    def analyze_china_pct_activity(self, years: List[str] = None,
                                  technology_areas: List[str] = None) -> Dict:
        """Analyze China's PCT filing activity

        Args:
            years: Years to analyze (e.g., ['2020', '2021'])
            technology_areas: Technology keywords to search for
        """

        if not years:
            years = ['2020', '2021', '2022', '2023']

        if not technology_areas:
            technology_areas = [
                'artificial intelligence', 'machine learning', '5G',
                'quantum computing', 'semiconductor', 'battery',
                'solar energy', 'biotechnology', 'nanotechnology'
            ]

        logger.info(f"Analyzing China PCT activity for {len(years)} years, {len(technology_areas)} technologies")

        analysis_results = {
            'summary': {
                'years_analyzed': years,
                'technologies_analyzed': technology_areas,
                'total_applications_found': 0,
                'analysis_date': datetime.now().isoformat()
            },
            'by_year': {},
            'by_technology': {},
            'key_applicants': {},
            'technology_trends': []
        }

        # Search for Chinese PCT applications by year and technology
        for year in years:
            year_total = 0
            analysis_results['by_year'][year] = {}

            for tech in technology_areas:
                logger.info(f"Searching {year} for {tech} applications from China")

                try:
                    # Search parameters for Chinese applicants
                    search_params = {
                        'applicant': 'china OR chinese OR beijing OR shanghai OR shenzhen OR guangzhou',
                        'title': tech,
                        'date_from': f'{year}-01-01',
                        'date_to': f'{year}-12-31'
                    }

                    applications = self.search_pct_applications(search_params)

                    app_count = len(applications)
                    analysis_results['by_year'][year][tech] = app_count
                    year_total += app_count

                    # Track technology totals
                    if tech not in analysis_results['by_technology']:
                        analysis_results['by_technology'][tech] = 0
                    analysis_results['by_technology'][tech] += app_count

                    # Extract key applicants
                    for app in applications:
                        for applicant_info in app.get('applicants', []):
                            applicant_name = applicant_info.get('name', '')
                            if self.is_chinese_applicant(applicant_name):
                                if applicant_name not in analysis_results['key_applicants']:
                                    analysis_results['key_applicants'][applicant_name] = 0
                                analysis_results['key_applicants'][applicant_name] += 1

                    time.sleep(2)  # Rate limiting between searches

                except Exception as e:
                    logger.error(f"Error searching {year}/{tech}: {e}")
                    continue

            analysis_results['by_year'][year]['total'] = year_total
            analysis_results['summary']['total_applications_found'] += year_total

        return analysis_results

    def is_chinese_applicant(self, applicant_name: str) -> bool:
        """Check if applicant appears to be Chinese"""

        applicant_lower = applicant_name.lower()

        chinese_indicators = [
            'china', 'chinese', 'beijing', 'shanghai', 'shenzhen',
            'guangzhou', 'hong kong', 'macau', 'taiwan',
            'huawei', 'xiaomi', 'alibaba', 'tencent', 'baidu',
            'byd', 'dji', 'lenovo', 'zte', 'sinopec', 'petrochina',
            'ping an', 'ant group', 'bytedance', 'meituan',
            'smic', 'cnooc', 'cosco', 'state grid'
        ]

        return any(indicator in applicant_lower for indicator in chinese_indicators)

    def get_patent_families(self, patent_numbers: List[str]) -> Dict:
        """Get patent family information for multiple patents"""

        families = {}

        for patent_num in patent_numbers:
            try:
                self._rate_limit()

                # Use detail API to get family information
                params = {'publicationNumber': patent_num}
                response = self.session.get(self.detail_url, params=params)

                if response.status_code == 200:
                    patent_detail = response.json()

                    # Extract family information
                    family_info = patent_detail.get('patentFamily', {})
                    families[patent_num] = family_info

                    logger.debug(f"Retrieved family info for {patent_num}")

            except Exception as e:
                logger.error(f"Error getting family info for {patent_num}: {e}")
                continue

        return families

    def save_analysis_results(self, results: Dict, filename: str):
        """Save analysis results"""

        # Save JSON
        json_path = self.output_dir / f"{filename}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)

        logger.info(f"Saved analysis to {json_path}")

        # Save summary report
        report_path = self.output_dir / f"{filename}_report.md"

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# WIPO PATENTSCOPE China Analysis\n\n")
            f.write(f"**Analysis Date:** {results['summary']['analysis_date']}\n")
            f.write(f"**Years Analyzed:** {', '.join(results['summary']['years_analyzed'])}\n")
            f.write(f"**Total Applications Found:** {results['summary']['total_applications_found']:,}\n\n")

            # By year analysis
            if results['by_year']:
                f.write("## Applications by Year\n\n")
                for year, data in sorted(results['by_year'].items()):
                    total = data.get('total', 0)
                    f.write(f"### {year}: {total} applications\n\n")

                    for tech, count in data.items():
                        if tech != 'total' and count > 0:
                            f.write(f"- **{tech}:** {count}\n")
                    f.write("\n")

            # Technology trends
            if results['by_technology']:
                f.write("## Top Technologies\n\n")
                sorted_tech = sorted(results['by_technology'].items(),
                                   key=lambda x: x[1], reverse=True)
                for tech, count in sorted_tech:
                    if count > 0:
                        f.write(f"- **{tech}:** {count} applications\n")

            # Key applicants
            if results['key_applicants']:
                f.write(f"\n## Top Chinese Applicants\n\n")
                sorted_applicants = sorted(results['key_applicants'].items(),
                                         key=lambda x: x[1], reverse=True)
                for applicant, count in sorted_applicants[:15]:
                    f.write(f"- **{applicant}:** {count} applications\n")

        logger.info(f"Saved report to {report_path}")

def main():
    """Test WIPO PATENTSCOPE client"""

    print("="*60)
    print("WIPO PATENTSCOPE Client Test")
    print("="*60)

    client = WIPOPatentscopeClient()

    # Test 1: Basic search
    print("1. Testing basic patent search...")

    try:
        results = client.search_patents("artificial intelligence", max_results=10)

        if results:
            print(f"Search completed: {results.get('total_found', 0)} results")

            patents = results.get('patents', [])
            if patents:
                print(f"Sample patent: {patents[0].get('publication_number', 'N/A')}")
                print(f"Title: {patents[0].get('title', 'N/A')[:60]}...")

    except Exception as e:
        print(f"Basic search test failed: {e}")

    # Test 2: PCT applications search
    print("\n2. Testing PCT applications search...")

    try:
        search_params = {
            'applicant': 'Huawei',
            'title': '5G',
            'date_from': '2022-01-01',
            'date_to': '2022-12-31'
        }

        pct_apps = client.search_pct_applications(search_params)
        print(f"Found {len(pct_apps)} Huawei 5G PCT applications in 2022")

        if pct_apps:
            sample = pct_apps[0]
            print(f"Sample: {sample.get('publication_number', 'N/A')} - {sample.get('title', 'N/A')[:50]}...")

    except Exception as e:
        print(f"PCT search test failed: {e}")

    # Test 3: China analysis (limited scope for testing)
    print("\n3. Testing China PCT analysis...")

    try:
        analysis = client.analyze_china_pct_activity(
            years=['2023'],
            technology_areas=['5G', 'artificial intelligence']
        )

        print(f"Analysis completed: {analysis['summary']['total_applications_found']} applications found")

        if analysis['key_applicants']:
            top_applicant = max(analysis['key_applicants'].items(), key=lambda x: x[1])
            print(f"Top applicant: {top_applicant[0]} ({top_applicant[1]} applications)")

        # Save results
        client.save_analysis_results(analysis, "wipo_china_analysis_test")

    except Exception as e:
        print(f"China analysis test failed: {e}")

    print("\n" + "="*60)
    print("WIPO PATENTSCOPE client test completed!")

if __name__ == "__main__":
    main()

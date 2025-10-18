#!/usr/bin/env python3
"""
USPTO Bulk Data Client

Accesses USPTO bulk patent data including:
- Full-text patent documents
- Patent Trial and Appeal Board (PTAB) data
- Legal status and prosecution history
- Bulk download capabilities
"""

import os
import json
import time
import requests
import pandas as pd
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class USPTOBulkClient:
    """Client for USPTO bulk patent data"""

    def __init__(self, output_dir: str = None):
        """Initialize USPTO bulk client"""

        # USPTO bulk data URLs
        self.bulk_base_url = "https://bulkdata.uspto.gov"
        self.patent_grant_url = f"{self.bulk_base_url}/data/patent/grant/redbook/fulltext"
        self.patent_app_url = f"{self.bulk_base_url}/data/patent/application/redbook/fulltext"
        self.ptab_url = f"{self.bulk_base_url}/data/patent/trial"

        # PatentsView API (complementary)
        self.patentsview_url = "https://search.patentsview.org/api/v1/patent"

        # Setup output directory
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            self.output_dir = Path("C:/Projects/OSINT - Foresight/data/collected/uspto_bulk")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Session setup
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'OSINT-Research-System/1.0',
            'Accept': 'application/json'
        })

        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 0.5

    def _rate_limit(self):
        """Basic rate limiting"""
        now = time.time()
        elapsed = now - self.last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)
        self.last_request_time = time.time()

    def get_available_bulk_files(self, data_type: str = 'grant') -> List[Dict]:
        """Get list of available bulk files

        Args:
            data_type: 'grant', 'application', or 'ptab'
        """

        if data_type == 'grant':
            base_url = self.patent_grant_url
        elif data_type == 'application':
            base_url = self.patent_app_url
        elif data_type == 'ptab':
            base_url = self.ptab_url
        else:
            raise ValueError("data_type must be 'grant', 'application', or 'ptab'")

        self._rate_limit()

        try:
            # Get directory listing
            response = self.session.get(base_url)
            response.raise_for_status()

            # Parse HTML to find ZIP files
            content = response.text
            zip_files = re.findall(r'href="([^"]*\.zip)"', content)

            # Extract metadata from filenames
            files_info = []
            for zip_file in zip_files:
                # Extract year and week/date from filename
                year_match = re.search(r'(\d{4})', zip_file)
                date_match = re.search(r'(\d{8})', zip_file)

                if year_match:
                    year = year_match.group(1)
                    date_info = date_match.group(1) if date_match else None

                    files_info.append({
                        'filename': zip_file,
                        'url': f"{base_url}/{zip_file}",
                        'year': year,
                        'date_info': date_info,
                        'data_type': data_type
                    })

            logger.info(f"Found {len(files_info)} {data_type} files")
            return sorted(files_info, key=lambda x: x['filename'])

        except Exception as e:
            logger.error(f"Error getting bulk file list: {e}")
            return []

    def download_bulk_file(self, file_info: Dict, extract: bool = True) -> Path:
        """Download and optionally extract bulk file"""

        filename = file_info['filename']
        url = file_info['url']

        local_path = self.output_dir / filename
        extract_dir = self.output_dir / filename.replace('.zip', '')

        # Skip if already downloaded
        if local_path.exists():
            logger.info(f"File already exists: {filename}")
            if extract and extract_dir.exists():
                return extract_dir
            elif not extract:
                return local_path

        logger.info(f"Downloading {filename} from USPTO...")

        try:
            self._rate_limit()

            response = self.session.get(url, stream=True)
            response.raise_for_status()

            # Download with progress
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            logger.info(f"Downloaded {filename} ({local_path.stat().st_size / 1024 / 1024:.1f} MB)")

            # Extract if requested
            if extract:
                extract_dir.mkdir(exist_ok=True)

                with zipfile.ZipFile(local_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)

                logger.info(f"Extracted to {extract_dir}")
                return extract_dir
            else:
                return local_path

        except Exception as e:
            logger.error(f"Error downloading {filename}: {e}")
            if local_path.exists():
                local_path.unlink()  # Remove partial download
            return None

    def parse_patent_xml(self, xml_file: Path) -> List[Dict]:
        """Parse USPTO XML patent file"""

        patents = []

        try:
            # Handle different XML structures
            tree = ET.parse(xml_file)
            root = tree.getroot()

            # Find patent documents
            patent_elements = root.findall('.//us-patent-grant') or root.findall('.//us-patent-application')

            for patent_elem in patent_elements:
                patent_data = self.extract_patent_data(patent_elem)
                if patent_data:
                    patents.append(patent_data)

            logger.info(f"Parsed {len(patents)} patents from {xml_file.name}")

        except Exception as e:
            logger.error(f"Error parsing {xml_file}: {e}")

        return patents

    def extract_patent_data(self, patent_elem) -> Dict:
        """Extract key data from patent XML element"""

        try:
            # Basic identifiers
            patent_data = {}

            # Publication reference
            pub_ref = patent_elem.find('.//publication-reference/document-id')
            if pub_ref is not None:
                patent_data['patent_number'] = self.get_text(pub_ref, 'doc-number')
                patent_data['country'] = self.get_text(pub_ref, 'country')
                patent_data['kind'] = self.get_text(pub_ref, 'kind')
                patent_data['date'] = self.get_text(pub_ref, 'date')

            # Application reference
            app_ref = patent_elem.find('.//application-reference/document-id')
            if app_ref is not None:
                patent_data['application_number'] = self.get_text(app_ref, 'doc-number')
                patent_data['filing_date'] = self.get_text(app_ref, 'date')

            # Title
            title_elem = patent_elem.find('.//invention-title')
            if title_elem is not None:
                patent_data['title'] = title_elem.text or ''

            # Assignees (current patent holders)
            assignees = []
            for assignee in patent_elem.findall('.//assignee'):
                name_elem = assignee.find('.//orgname') or assignee.find('.//first-name')
                if name_elem is not None:
                    assignees.append(name_elem.text or '')
            patent_data['assignees'] = assignees

            # Inventors
            inventors = []
            for inventor in patent_elem.findall('.//inventor'):
                first_name = self.get_text(inventor, './/first-name')
                last_name = self.get_text(inventor, './/last-name')
                if first_name or last_name:
                    inventors.append(f"{first_name} {last_name}".strip())
            patent_data['inventors'] = inventors

            # Classifications
            classifications = []
            for class_elem in patent_elem.findall('.//classification-ipc/main-classification'):
                if class_elem.text:
                    classifications.append(class_elem.text)
            patent_data['ipc_classifications'] = classifications

            # CPC classifications
            cpc_classes = []
            for cpc_elem in patent_elem.findall('.//classification-cpc//classification-symbol'):
                if cpc_elem.text:
                    cpc_classes.append(cpc_elem.text)
            patent_data['cpc_classifications'] = cpc_classes

            # Abstract
            abstract_elem = patent_elem.find('.//abstract')
            if abstract_elem is not None:
                abstract_text = ET.tostring(abstract_elem, encoding='unicode', method='text')
                patent_data['abstract'] = abstract_text.strip()

            # Check for China connections
            patent_data['china_connection'] = self.detect_china_connection(patent_data)

            return patent_data

        except Exception as e:
            logger.error(f"Error extracting patent data: {e}")
            return {}

    def get_text(self, parent_elem, xpath: str) -> str:
        """Safely extract text from XML element"""
        elem = parent_elem.find(xpath)
        return elem.text if elem is not None and elem.text else ''

    def detect_china_connection(self, patent_data: Dict) -> Dict:
        """Detect various types of China connections in patent data"""

        connections = {
            'has_chinese_assignee': False,
            'has_chinese_inventor': False,
            'china_related_keywords': False,
            'chinese_entities': []
        }

        # Check assignees for Chinese entities
        assignees = patent_data.get('assignees', [])
        for assignee in assignees:
            if self.is_chinese_entity(assignee):
                connections['has_chinese_assignee'] = True
                connections['chinese_entities'].append(assignee)

        # Check inventors for Chinese names/locations
        inventors = patent_data.get('inventors', [])
        for inventor in inventors:
            if self.is_chinese_name(inventor):
                connections['has_chinese_inventor'] = True

        # Check title and abstract for China-related keywords
        text_fields = [
            patent_data.get('title', ''),
            patent_data.get('abstract', '')
        ]

        china_keywords = [
            'china', 'chinese', 'beijing', 'shanghai', 'shenzhen',
            'guangzhou', 'hong kong', 'macau', 'taiwan'
        ]

        for text in text_fields:
            if any(keyword in text.lower() for keyword in china_keywords):
                connections['china_related_keywords'] = True
                break

        return connections

    def is_chinese_entity(self, entity_name: str) -> bool:
        """Check if entity name suggests Chinese organization"""

        entity_lower = entity_name.lower()

        chinese_indicators = [
            'china', 'chinese', 'beijing', 'shanghai', 'shenzhen',
            'guangzhou', 'hong kong', 'macau', 'taiwan',
            'huawei', 'xiaomi', 'alibaba', 'tencent', 'baidu',
            'byd', 'dji', 'lenovo', 'zte', 'sinopec', 'petrochina',
            'ping an', 'ant group', 'bytedance', 'meituan'
        ]

        return any(indicator in entity_lower for indicator in chinese_indicators)

    def is_chinese_name(self, name: str) -> bool:
        """Basic check for Chinese names (simplified)"""

        # This is a basic implementation - more sophisticated name detection
        # would require specialized libraries
        common_chinese_surnames = [
            'wang', 'li', 'zhang', 'liu', 'chen', 'yang', 'huang', 'zhao',
            'wu', 'zhou', 'xu', 'sun', 'ma', 'zhu', 'hu', 'guo', 'he', 'lin'
        ]

        name_lower = name.lower()
        return any(surname in name_lower for surname in common_chinese_surnames)

    def search_patents_by_assignee(self, assignee: str, max_results: int = 1000) -> List[Dict]:
        """Search patents by assignee using PatentsView API"""

        self._rate_limit()

        params = {
            'q': f'assignee_organization:"{assignee}"',
            'f': [
                'patent_number', 'patent_title', 'patent_date',
                'assignee_organization', 'inventor_name_first', 'inventor_name_last',
                'cpc_current_mainclass_title', 'uspc_current_mainclass_title'
            ],
            'o': {'per_page': min(max_results, 1000)}
        }

        try:
            response = self.session.post(self.patentsview_url, json=params)
            response.raise_for_status()

            data = response.json()
            patents = data.get('patents', [])

            logger.info(f"Found {len(patents)} patents for assignee: {assignee}")
            return patents

        except Exception as e:
            logger.error(f"Error searching patents for {assignee}: {e}")
            return []

    def analyze_china_technology_transfer(self, years: List[str] = None,
                                        technology_areas: List[str] = None) -> Dict:
        """Analyze China technology transfer patterns in USPTO data"""

        if not years:
            years = ['2020', '2021', '2022', '2023']

        if not technology_areas:
            technology_areas = [
                'artificial intelligence', '5G', 'quantum computing',
                'semiconductor', 'battery technology', 'solar energy',
                'biotechnology', 'nanotechnology', 'robotics'
            ]

        logger.info(f"Analyzing China technology transfer for {len(years)} years, {len(technology_areas)} technologies")

        analysis_results = {
            'summary': {
                'years_analyzed': years,
                'technologies_analyzed': technology_areas,
                'total_patents_analyzed': 0,
                'china_connected_patents': 0,
                'analysis_date': datetime.now().isoformat()
            },
            'by_year': {},
            'by_technology': {},
            'key_entities': {},
            'technology_patterns': []
        }

        # Get available bulk files for the specified years
        grant_files = self.get_available_bulk_files('grant')
        relevant_files = [f for f in grant_files if any(year in f['filename'] for year in years)]

        logger.info(f"Found {len(relevant_files)} relevant bulk files")

        for file_info in relevant_files[:5]:  # Limit for testing
            logger.info(f"Processing {file_info['filename']}")

            # Download and extract
            extract_dir = self.download_bulk_file(file_info, extract=True)
            if not extract_dir:
                continue

            # Process XML files in the extracted directory
            xml_files = list(extract_dir.glob('*.xml'))
            for xml_file in xml_files[:2]:  # Limit for testing

                patents = self.parse_patent_xml(xml_file)
                analysis_results['summary']['total_patents_analyzed'] += len(patents)

                # Analyze each patent
                for patent in patents:
                    if patent.get('china_connection', {}).get('has_chinese_assignee') or \
                       patent.get('china_connection', {}).get('has_chinese_inventor') or \
                       patent.get('china_connection', {}).get('china_related_keywords'):

                        analysis_results['summary']['china_connected_patents'] += 1

                        # Track by year
                        patent_year = patent.get('date', '')[:4]
                        if patent_year not in analysis_results['by_year']:
                            analysis_results['by_year'][patent_year] = 0
                        analysis_results['by_year'][patent_year] += 1

                        # Track entities
                        for entity in patent.get('china_connection', {}).get('chinese_entities', []):
                            if entity not in analysis_results['key_entities']:
                                analysis_results['key_entities'][entity] = 0
                            analysis_results['key_entities'][entity] += 1

        return analysis_results

    def save_analysis_results(self, results: Dict, filename: str):
        """Save analysis results"""

        filepath = self.output_dir / f"{filename}.json"

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)

        logger.info(f"Saved analysis results to {filepath}")

        # Create summary report
        report_path = self.output_dir / f"{filename}_summary.md"

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# USPTO China Technology Transfer Analysis\n\n")
            f.write(f"**Analysis Date:** {results['summary']['analysis_date']}\n")
            f.write(f"**Years Analyzed:** {', '.join(results['summary']['years_analyzed'])}\n")
            f.write(f"**Total Patents:** {results['summary']['total_patents_analyzed']:,}\n")
            f.write(f"**China Connected:** {results['summary']['china_connected_patents']}\n\n")

            if results['by_year']:
                f.write("## Patents by Year\n\n")
                for year, count in sorted(results['by_year'].items()):
                    f.write(f"- **{year}:** {count} patents\n")

            if results['key_entities']:
                f.write("\n## Top Chinese Entities\n\n")
                sorted_entities = sorted(results['key_entities'].items(),
                                       key=lambda x: x[1], reverse=True)
                for entity, count in sorted_entities[:10]:
                    f.write(f"- **{entity}:** {count} patents\n")

        logger.info(f"Saved summary report to {report_path}")

def main():
    """Test USPTO bulk client"""

    print("="*60)
    print("USPTO Bulk Data Client Test")
    print("="*60)

    client = USPTOBulkClient()

    # Test 1: Get available files
    print("1. Getting available bulk files...")
    grant_files = client.get_available_bulk_files('grant')
    print(f"Found {len(grant_files)} grant files")

    if grant_files:
        print(f"Latest file: {grant_files[-1]['filename']}")

    # Test 2: PatentsView API search
    print("\n2. Testing PatentsView API search...")
    huawei_patents = client.search_patents_by_assignee("Huawei", max_results=50)
    print(f"Found {len(huawei_patents)} Huawei patents")

    if huawei_patents:
        sample = huawei_patents[0]
        print(f"Sample patent: {sample.get('patent_number')} - {sample.get('patent_title', '')[:50]}...")

    # Test 3: Download and analyze small sample
    print("\n3. Testing bulk file download and analysis...")

    if grant_files:
        # Get most recent file for testing
        recent_file = grant_files[-1]
        print(f"Testing with: {recent_file['filename']}")

        # Note: In practice, you might want to test with a smaller/older file first
        # as recent files can be very large

    print("\n" + "="*60)
    print("USPTO bulk client test completed!")

if __name__ == "__main__":
    main()

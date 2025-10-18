#!/usr/bin/env python3
"""
USPTO Bulk Data Downloader and Processor
Downloads and processes USPTO patent data for Italy-China analysis
"""

import json
import requests
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime, timedelta
import logging
import re
from collections import defaultdict
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class USPTOBulkProcessor:
    def __init__(self):
        self.base_url = "https://bulkdata.uspto.gov/data/patent/grant/redbook/"
        self.download_path = Path("data/collected/uspto_bulk")
        self.download_path.mkdir(parents=True, exist_ok=True)
        self.output_path = Path("data/processed/uspto_italy")
        self.output_path.mkdir(parents=True, exist_ok=True)

        # Patterns for detection
        self.italy_pattern = re.compile(
            r'\b(italy|italian|italia|rome|milan|turin|bologna|florence|venice|naples|genoa|'
            r'leonardo|finmeccanica|stmicroelectronics|fincantieri|eni|enel|pirelli|'
            r'politecnico|sapienza|universita)\b',
            re.IGNORECASE
        )

        self.china_pattern = re.compile(
            r'\b(china|chinese|beijing|shanghai|shenzhen|guangzhou|wuhan|'
            r'huawei|zte|alibaba|tencent|baidu|xiaomi|lenovo|dji|byd|'
            r'chinese academy|tsinghua|peking|zhejiang|fudan)\b',
            re.IGNORECASE
        )

        # Dual-use IPC/CPC classifications
        self.dual_use_classes = [
            'H04L',  # Digital transmission
            'H04K',  # Secret communication
            'G06N',  # AI/ML computing
            'H01L',  # Semiconductors
            'B64C',  # Aircraft
            'B64D',  # Aircraft equipment
            'G01S',  # Radio/radar navigation
            'F41',   # Weapons
            'F42',   # Ammunition
            'G21',   # Nuclear physics
            'C12N',  # Microorganisms/enzymes
            'C07K',  # Peptides
        ]

        self.results = {
            'italian_patents': [],
            'china_coinventions': [],
            'dual_use_patents': [],
            'technology_transfers': [],
            'statistics': defaultdict(int)
        }

    def download_recent_data(self, year: int = 2024) -> list:
        """Download recent USPTO grant data"""
        logger.info(f"Checking USPTO bulk data for {year}...")

        downloaded_files = []

        # USPTO releases weekly files
        # Format: ipgYYMMDD.zip
        base_url = f"https://bulkdata.uspto.gov/data/patent/grant/redbook/{year}/"

        try:
            # Try to get directory listing
            response = requests.get(base_url, timeout=10)
            if response.status_code == 200:
                # Parse for zip files
                files = re.findall(r'href="(ipg\d{6}\.zip)"', response.text)

                logger.info(f"Found {len(files)} weekly files for {year}")

                # Download most recent files
                for filename in files[-4:]:  # Last 4 weeks
                    file_url = base_url + filename
                    local_path = self.download_path / filename

                    if not local_path.exists():
                        logger.info(f"Downloading {filename}...")
                        try:
                            r = requests.get(file_url, stream=True, timeout=30)
                            if r.status_code == 200:
                                with open(local_path, 'wb') as f:
                                    for chunk in r.iter_content(chunk_size=8192):
                                        f.write(chunk)
                                downloaded_files.append(local_path)
                                logger.info(f"  Downloaded: {local_path}")
                        except Exception as e:
                            logger.error(f"  Failed to download {filename}: {e}")
                    else:
                        logger.info(f"  Already exists: {local_path}")
                        downloaded_files.append(local_path)

        except Exception as e:
            logger.error(f"Failed to access USPTO bulk data: {e}")

        return downloaded_files

    def process_patent_xml(self, xml_content: str) -> dict:
        """Process a single patent from XML"""
        try:
            root = ET.fromstring(xml_content)

            # Extract basic info
            patent = {
                'number': self._extract_text(root, './/publication-reference/document-id/doc-number'),
                'date': self._extract_text(root, './/publication-reference/document-id/date'),
                'title': self._extract_text(root, './/invention-title'),
                'abstract': self._extract_text(root, './/abstract'),
                'inventors': [],
                'assignees': [],
                'classifications': [],
                'italy_related': False,
                'china_related': False,
                'dual_use': False
            }

            # Extract inventors
            for inventor in root.findall('.//inventors/inventor'):
                inv_data = {
                    'name': self._extract_text(inventor, './/name/given-name') + ' ' +
                           self._extract_text(inventor, './/name/family-name'),
                    'country': self._extract_text(inventor, './/residence/country')
                }
                patent['inventors'].append(inv_data)

                # Check for Italy/China
                if inv_data['country'] in ['IT', 'ITA']:
                    patent['italy_related'] = True
                if inv_data['country'] in ['CN', 'CHN']:
                    patent['china_related'] = True

            # Extract assignees
            for assignee in root.findall('.//assignees/assignee'):
                ass_data = {
                    'name': self._extract_text(assignee, './/orgname'),
                    'country': self._extract_text(assignee, './/country')
                }
                patent['assignees'].append(ass_data)

                # Check assignee names
                if ass_data['name']:
                    if self.italy_pattern.search(ass_data['name']):
                        patent['italy_related'] = True
                    if self.china_pattern.search(ass_data['name']):
                        patent['china_related'] = True

            # Extract classifications
            for classification in root.findall('.//classifications-ipcr/classification-ipcr'):
                ipc = self._extract_text(classification, './/section') + \
                      self._extract_text(classification, './/class') + \
                      self._extract_text(classification, './/subclass')
                patent['classifications'].append(ipc)

                # Check for dual-use
                for dual_use_class in self.dual_use_classes:
                    if ipc.startswith(dual_use_class):
                        patent['dual_use'] = True
                        break

            # Text-based detection
            full_text = (patent['title'] + ' ' + patent['abstract']).lower()
            if self.italy_pattern.search(full_text):
                patent['italy_related'] = True
            if self.china_pattern.search(full_text):
                patent['china_related'] = True

            return patent

        except Exception as e:
            return None

    def _extract_text(self, element, xpath):
        """Extract text from XML element"""
        try:
            elem = element.find(xpath)
            if elem is not None and elem.text:
                return elem.text.strip()
        except:
            pass
        return ""

    def process_bulk_file(self, file_path: Path) -> dict:
        """Process a USPTO bulk data file"""
        logger.info(f"Processing {file_path.name}...")

        stats = {
            'file': file_path.name,
            'total_patents': 0,
            'italian_patents': 0,
            'china_connections': 0,
            'dual_use': 0,
            'italy_china_overlap': 0
        }

        try:
            # Extract ZIP file
            with zipfile.ZipFile(file_path, 'r') as zip_file:
                for member in zip_file.namelist():
                    if member.endswith('.xml'):
                        logger.info(f"  Processing {member}...")

                        with zip_file.open(member) as xml_file:
                            content = xml_file.read().decode('utf-8', errors='ignore')

                            # Split into individual patents
                            patents = re.split(r'<\?xml', content)

                            for patent_xml in patents[1:]:  # Skip first empty split
                                patent_xml = '<?xml' + patent_xml

                                # Extract patent data
                                patent = self.process_patent_xml(patent_xml)

                                if patent:
                                    stats['total_patents'] += 1

                                    if patent['italy_related']:
                                        stats['italian_patents'] += 1
                                        self.results['italian_patents'].append(patent)

                                        if patent['china_related']:
                                            stats['italy_china_overlap'] += 1
                                            self.results['china_coinventions'].append(patent)

                                    if patent['china_related']:
                                        stats['china_connections'] += 1

                                    if patent['dual_use']:
                                        stats['dual_use'] += 1
                                        if patent['italy_related']:
                                            self.results['dual_use_patents'].append(patent)

                                # Process in batches
                                if stats['total_patents'] % 100 == 0:
                                    logger.info(f"    Processed {stats['total_patents']} patents...")

        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")

        # Update global statistics
        for key, value in stats.items():
            if key != 'file':
                self.results['statistics'][key] += value

        logger.info(f"  Results: {stats['italian_patents']} IT, "
                   f"{stats['italy_china_overlap']} IT-CN, "
                   f"{stats['dual_use']} dual-use")

        return stats

    def analyze_technology_transfers(self):
        """Identify potential technology transfer patterns"""
        transfers = []

        for patent in self.results['china_coinventions']:
            if patent['dual_use']:
                transfers.append({
                    'patent_number': patent['number'],
                    'title': patent['title'],
                    'classifications': patent['classifications'],
                    'italian_inventors': [i for i in patent['inventors']
                                         if i['country'] in ['IT', 'ITA']],
                    'chinese_entities': [i for i in patent['inventors']
                                        if i['country'] in ['CN', 'CHN']] +
                                       [a for a in patent['assignees']
                                        if self.china_pattern.search(a.get('name', ''))],
                    'risk_level': 'HIGH'
                })

        self.results['technology_transfers'] = transfers
        self.results['statistics']['potential_transfers'] = len(transfers)

        return transfers

    def generate_report(self) -> dict:
        """Generate analysis report"""
        total = self.results['statistics']['total_patents']
        italian = self.results['statistics']['italian_patents']
        overlap = self.results['statistics']['italy_china_overlap']

        report = {
            'generated_at': datetime.now().isoformat(),
            'statistics': dict(self.results['statistics']),
            'italy_percentage': (italian / total * 100) if total > 0 else 0,
            'china_overlap_rate': (overlap / italian * 100) if italian > 0 else 0,
            'high_risk_patents': len(self.results['technology_transfers']),
            'risk_assessment': self.assess_risk(),
            'recommendations': self.generate_recommendations()
        }

        return report

    def assess_risk(self) -> dict:
        """Assess overall risk"""
        overlap = self.results['statistics']['italy_china_overlap']
        transfers = len(self.results['technology_transfers'])

        risk_level = 'LOW'
        if overlap > 10:
            risk_level = 'MEDIUM'
        if overlap > 50 or transfers > 5:
            risk_level = 'HIGH'
        if transfers > 10:
            risk_level = 'CRITICAL'

        return {
            'level': risk_level,
            'confidence': 0.7
        }

    def generate_recommendations(self) -> list:
        """Generate recommendations"""
        recs = []

        if self.results['statistics']['italy_china_overlap'] > 20:
            recs.append("CRITICAL: Review all Italy-China co-invention patents")

        if len(self.results['technology_transfers']) > 5:
            recs.append("HIGH PRIORITY: Investigate technology transfer risks")

        recs.extend([
            "EXPAND: Download full year of USPTO data",
            "VALIDATE: Cross-reference with trade data",
            "MONITOR: Set up weekly patent monitoring"
        ])

        return recs

def main():
    processor = USPTOBulkProcessor()

    logger.info("="*60)
    logger.info("USPTO BULK DATA PROCESSING - ITALY-CHINA ANALYSIS")
    logger.info("="*60)

    # Download recent data
    files = processor.download_recent_data(2024)

    if not files:
        logger.info("\nAttempting to process existing files...")
        files = list(processor.download_path.glob("*.zip"))

    # Process files
    for file_path in files[:2]:  # Process first 2 files as demo
        stats = processor.process_bulk_file(file_path)

    # Analyze patterns
    processor.analyze_technology_transfers()

    # Generate report
    report = processor.generate_report()

    # Save results
    output_file = processor.output_path / f"uspto_bulk_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)

    # Display summary
    logger.info("\n" + "="*60)
    logger.info("ANALYSIS SUMMARY")
    logger.info("="*60)
    logger.info(f"Total Patents Processed: {report['statistics']['total_patents']:,}")
    logger.info(f"Italian Patents: {report['statistics']['italian_patents']}")
    logger.info(f"Italy-China Co-inventions: {report['statistics']['italy_china_overlap']}")
    logger.info(f"Dual-Use Patents: {report['statistics']['dual_use']}")
    logger.info(f"High-Risk Transfers: {report['high_risk_patents']}")
    logger.info(f"\nRisk Level: {report['risk_assessment']['level']}")

    logger.info(f"\nResults saved to: {output_file}")

    return report

if __name__ == "__main__":
    main()

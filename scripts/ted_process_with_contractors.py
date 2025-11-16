#!/usr/bin/env python3
"""
TED processor that properly extracts CONTRACTOR information
This is what we should have been doing from the start!
"""

import tarfile
import sqlite3
import json
import hashlib
import logging
from pathlib import Path
from datetime import datetime
from lxml import etree

# Setup logging
log_file = Path("C:/Projects/OSINT - Foresight/logs") / f"ted_contractors_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"
ARCHIVE_PATH = "F:/TED_Data/monthly/2024/TED_monthly_2024_09.tar.gz"  # Sample recent month
TEMP_BASE = Path("C:/Projects/OSINT - Foresight/data/temp/contractor_test")
TEMP_BASE.mkdir(parents=True, exist_ok=True)

# Chinese companies
CHINESE_COMPANIES = [
    'huawei', 'zte', 'alibaba', 'tencent', 'baidu', 'xiaomi', 'oppo', 'vivo',
    'lenovo', 'dahua', 'hikvision', 'tiktok', 'bytedance', 'dji',
    'longi', 'ja solar', 'trina', 'jinko', 'canadian solar', 'risen energy',
    'byd', 'geely', 'great wall', 'nio', 'xpeng', 'li auto', 'chery',
    'crrc', 'china railway', 'cosco', 'china shipping',
    'china state construction', 'cscec',
    'sany', 'zoomlion', 'xcmg', 'weichai', 'midea', 'gree electric',
    'sinopec', 'petrochina', 'cnooc', 'comac', 'avic'
]

class ContractorProcessor:
    def __init__(self):
        self.ns = {'ted': 'http://publications.europa.eu/TED_schema/Export'}
        self.stats = {
            'xml_processed': 0,
            'contracts_with_contractors': 0,
            'chinese_contractors': 0,
            'chinese_details': []
        }

    def extract_contractor_info(self, root):
        """Extract contractor information from XML"""
        contractors = []

        # Find all ECONOMIC_OPERATOR sections
        for operator in root.findall('.//ECONOMIC_OPERATOR_NAME_ADDRESS', self.ns):
            contractor = {}

            # Get official name
            org = operator.find('.//OFFICIALNAME', self.ns)
            if org is not None and org.text:
                contractor['name'] = org.text.strip()

            # Get country
            country = operator.find('.//COUNTRY', self.ns)
            if country is not None:
                contractor['country'] = country.get('VALUE', '')

            # Get address
            address = operator.find('.//ADDRESS', self.ns)
            if address is not None and address.text:
                contractor['address'] = address.text.strip()

            # Get town
            town = operator.find('.//TOWN', self.ns)
            if town is not None and town.text:
                if 'address' in contractor:
                    contractor['address'] += f", {town.text.strip()}"
                else:
                    contractor['address'] = town.text.strip()

            if contractor.get('name'):
                contractors.append(contractor)

        return contractors

    def check_chinese(self, contractor_name, contractor_country):
        """Check if contractor is Chinese"""
        if contractor_country == 'CN':
            return True, ['country_code_CN']

        if not contractor_name:
            return False, []

        name_lower = contractor_name.lower()
        matched = []

        for company in CHINESE_COMPANIES:
            if company in name_lower:
                matched.append(company)

        # Check for generic China indicators
        if any(word in name_lower for word in ['china', 'chinese', 'beijing', 'shanghai', 'shenzhen', 'guangzhou']):
            if 'generic_china_mention' not in matched:
                matched.append('generic_china_mention')

        return len(matched) > 0, matched

    def process_xml(self, xml_path):
        """Process single XML file"""
        try:
            tree = etree.parse(str(xml_path))
            root = tree.getroot()

            # Extract basic info
            doc_num = root.find('.//ted:NO_DOC_OJS', self.ns)
            date_pub = root.find('.//ted:DATE_PUB', self.ns)
            iso_country = root.find('.//ted:ISO_COUNTRY', self.ns)

            # Get title
            title = None
            ml_title = root.find('.//ted:ML_TI_DOC[@LG="EN"]', self.ns)
            if ml_title is not None:
                title_elem = ml_title.find('ted:TI_TEXT', self.ns)
                if title_elem is not None and title_elem.text:
                    title = title_elem.text.strip()

            # Extract contractors - THIS IS THE KEY PART!
            contractors = self.extract_contractor_info(root)

            self.stats['xml_processed'] += 1

            if contractors:
                self.stats['contracts_with_contractors'] += 1

                # Check first contractor
                contractor = contractors[0]
                is_chinese, matched = self.check_chinese(
                    contractor.get('name', ''),
                    contractor.get('country', '')
                )

                if is_chinese:
                    self.stats['chinese_contractors'] += 1
                    self.stats['chinese_details'].append({
                        'date': date_pub.text if date_pub is not None else '',
                        'doc_id': doc_num.text if doc_num is not None else '',
                        'title': title,
                        'contractor_name': contractor.get('name', ''),
                        'contractor_country': contractor.get('country', ''),
                        'contractor_address': contractor.get('address', ''),
                        'matched_indicators': matched
                    })

                    logger.info(f"  CHINESE: {contractor.get('name', '')} ({contractor.get('country', '')})")

        except Exception as e:
            logger.debug(f"Failed to parse {xml_path.name}: {e}")

    def process_archive(self):
        """Process one TED monthly archive"""
        logger.info("="*80)
        logger.info(f"PROCESSING: {ARCHIVE_PATH}")
        logger.info("="*80)

        archive_temp = TEMP_BASE / "monthly"
        archive_temp.mkdir(exist_ok=True)

        # Extract monthly archive
        logger.info("Extracting monthly archive...")
        with tarfile.open(ARCHIVE_PATH, 'r:gz') as tar:
            tar.extractall(archive_temp)

        # Find daily archives
        daily_archives = list(archive_temp.rglob("*.tar.gz"))
        logger.info(f"Found {len(daily_archives)} daily archives")

        # Process first 5 daily archives as sample
        for daily_archive in daily_archives[:5]:
            logger.info(f"\nProcessing: {daily_archive.name}")

            daily_temp = TEMP_BASE / "daily" / daily_archive.stem
            daily_temp.mkdir(parents=True, exist_ok=True)

            try:
                with tarfile.open(daily_archive, 'r:gz') as tar:
                    tar.extractall(daily_temp)

                # Find XML files
                xml_files = list(daily_temp.rglob("*.xml"))
                logger.info(f"  Found {len(xml_files)} XML files")

                for xml_file in xml_files:
                    self.process_xml(xml_file)

            except Exception as e:
                logger.warning(f"  Failed: {e}")

        # Report
        logger.info("\n" + "="*80)
        logger.info("RESULTS")
        logger.info("="*80)
        logger.info(f"XML files processed: {self.stats['xml_processed']:,}")
        logger.info(f"Contracts with contractor info: {self.stats['contracts_with_contractors']:,}")
        logger.info(f"Chinese contractors found: {self.stats['chinese_contractors']}")

        if self.stats['chinese_details']:
            logger.info("\n" + "="*80)
            logger.info("CHINESE CONTRACTOR DETAILS")
            logger.info("="*80)
            for detail in self.stats['chinese_details']:
                logger.info(f"\n{detail['date']} - {detail['doc_id']}")
                logger.info(f"  Contractor: {detail['contractor_name']}")
                logger.info(f"  Country: {detail['contractor_country']}")
                logger.info(f"  Address: {detail['contractor_address']}")
                logger.info(f"  Contract: {detail['title']}")
                logger.info(f"  Matched: {detail['matched_indicators']}")

        # Save results
        report_path = Path("C:/Projects/OSINT - Foresight/analysis/ted_contractor_sample_report.json")
        with open(report_path, 'w') as f:
            json.dump(self.stats, f, indent=2)

        logger.info(f"\nReport saved: {report_path}")

if __name__ == '__main__':
    processor = ContractorProcessor()
    processor.process_archive()

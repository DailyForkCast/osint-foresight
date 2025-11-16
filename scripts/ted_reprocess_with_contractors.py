#!/usr/bin/env python3
"""
Re-process existing TED archives to properly extract contractor information
Uses correct XML path: ECONOMIC_OPERATOR_NAME_ADDRESS -> CONTACT_DATA_WITHOUT_RESPONSIBLE_NAME -> ORGANISATION
"""

import tarfile
import sqlite3
import json
import logging
from pathlib import Path
from datetime import datetime
from lxml import etree
import sys

# Setup logging with UTF-8 encoding
log_file = Path("C:/Projects/OSINT - Foresight/logs") / f"ted_contractors_full_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"
ARCHIVE_DIR = Path("F:/TED_Data/monthly")

# Process just 2014-2015 since that's what we have in the database
ARCHIVES_TO_PROCESS = [
    "2014/TED_monthly_2014_02.tar.gz",  # Sample month
]

TEMP_BASE = Path("C:/Projects/OSINT - Foresight/data/temp/contractor_full")
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

class ProperContractorExtractor:
    def __init__(self):
        self.ns = {'ted': 'http://publications.europa.eu/TED_schema/Export'}
        self.stats = {
            'xml_processed': 0,
            'contractors_found': 0,
            'chinese_found': 0,
            'chinese_details': []
        }

    def extract_contractors(self, root):
        """Extract contractor info using CORRECT XML path"""
        contractors = []

        operators = root.findall('.//ted:ECONOMIC_OPERATOR_NAME_ADDRESS', self.ns)

        for op in operators:
            contractor = {}

            # Navigate the correct path!
            contact = op.find('ted:CONTACT_DATA_WITHOUT_RESPONSIBLE_NAME', self.ns)
            if contact is not None:
                # Get name
                org = contact.find('ted:ORGANISATION', self.ns)
                if org is not None:
                    name_elem = org.find('ted:OFFICIALNAME', self.ns)
                    if name_elem is not None and name_elem.text:
                        contractor['name'] = name_elem.text.strip()

                # Get country
                country_elem = contact.find('ted:COUNTRY', self.ns)
                if country_elem is not None:
                    contractor['country'] = country_elem.get('VALUE', '')

                # Get address
                addr_elem = contact.find('ted:ADDRESS', self.ns)
                if addr_elem is not None and addr_elem.text:
                    contractor['address'] = addr_elem.text.strip()

                town_elem = contact.find('ted:TOWN', self.ns)
                if town_elem is not None and town_elem.text:
                    if 'address' in contractor:
                        contractor['address'] += f", {town_elem.text.strip()}"
                    else:
                        contractor['address'] = town_elem.text.strip()

            if contractor.get('name'):
                contractors.append(contractor)

        return contractors

    def check_chinese(self, contractor_name, contractor_country):
        """Check if contractor is Chinese"""
        matched = []

        # Country code check
        if contractor_country == 'CN':
            return True, ['country_CN']

        if not contractor_name:
            return False, []

        name_lower = contractor_name.lower()

        # Company name matching
        for company in CHINESE_COMPANIES:
            if company in name_lower:
                matched.append(company)

        # Location indicators
        chinese_locations = ['china', 'chinese', 'beijing', 'shanghai', 'shenzhen', 'guangzhou', 'hangzhou']
        for loc in chinese_locations:
            if loc in name_lower:
                matched.append(f'location_{loc}')

        return len(matched) > 0, matched

    def process_xml(self, xml_path):
        """Process single XML file"""
        try:
            tree = etree.parse(str(xml_path))
            root = tree.getroot()

            # Get basic info
            doc_num = root.find('.//ted:NO_DOC_OJS', self.ns)
            date_pub = root.find('.//ted:DATE_PUB', self.ns)

            # Get title
            title = None
            ml_title = root.find('.//ted:ML_TI_DOC[@LG="EN"]', self.ns)
            if ml_title is not None:
                title_elem = ml_title.find('ted:TI_TEXT', self.ns)
                if title_elem is not None and title_elem.text:
                    title = title_elem.text.strip()

            # Extract contractors
            contractors = self.extract_contractors(root)

            self.stats['xml_processed'] += 1

            if contractors:
                self.stats['contractors_found'] += len(contractors)

                # Check first contractor
                contractor = contractors[0]
                is_chinese, matched = self.check_chinese(
                    contractor.get('name', ''),
                    contractor.get('country', '')
                )

                if is_chinese:
                    self.stats['chinese_found'] += 1

                    detail = {
                        'date': date_pub.text if date_pub is not None else '',
                        'doc_id': doc_num.text if doc_num is not None else '',
                        'title': title,
                        'contractor_name': contractor.get('name', ''),
                        'contractor_country': contractor.get('country', ''),
                        'contractor_address': contractor.get('address', ''),
                        'matched_indicators': matched
                    }

                    self.stats['chinese_details'].append(detail)
                    logger.info(f"  CHINESE: {contractor.get('name', '')} ({contractor.get('country', '')})")

        except Exception as e:
            logger.debug(f"Failed to parse {xml_path.name}: {e}")

    def process_archive(self, archive_path):
        """Process one monthly archive"""
        logger.info("="*80)
        logger.info(f"PROCESSING: {archive_path.name}")
        logger.info("="*80)

        archive_temp = TEMP_BASE / archive_path.stem
        archive_temp.mkdir(exist_ok=True)

        # Extract monthly archive
        logger.info("Extracting monthly archive...")
        with tarfile.open(archive_path, 'r:gz') as tar:
            tar.extractall(archive_temp)

        # Find daily archives
        daily_archives = list(archive_temp.rglob("*.tar.gz"))
        logger.info(f"Found {len(daily_archives)} daily archives")

        for i, daily_archive in enumerate(daily_archives):
            logger.info(f"\n[{i+1}/{len(daily_archives)}] Processing: {daily_archive.name}")

            daily_temp = TEMP_BASE / "daily" / daily_archive.stem
            daily_temp.mkdir(parents=True, exist_ok=True)

            try:
                with tarfile.open(daily_archive, 'r:gz') as tar:
                    tar.extractall(daily_temp)

                xml_files = list(daily_temp.rglob("*.xml"))
                logger.info(f"  Found {len(xml_files)} XML files")

                for xml_file in xml_files:
                    self.process_xml(xml_file)

            except Exception as e:
                logger.warning(f"  Failed: {e}")

    def run(self):
        """Process all archives"""
        for archive_rel in ARCHIVES_TO_PROCESS:
            archive_path = ARCHIVE_DIR / archive_rel
            if archive_path.exists():
                self.process_archive(archive_path)
            else:
                logger.warning(f"Archive not found: {archive_path}")

        # Report
        logger.info("\n" + "="*80)
        logger.info("FINAL RESULTS")
        logger.info("="*80)
        logger.info(f"XML files processed: {self.stats['xml_processed']:,}")
        logger.info(f"Contractors found: {self.stats['contractors_found']:,}")
        logger.info(f"Chinese contractors: {self.stats['chinese_found']}")

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

        # Save report
        report_path = Path("C:/Projects/OSINT - Foresight/analysis/ted_contractors_proper_extraction.json")
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, indent=2, ensure_ascii=False)

        logger.info(f"\nReport saved: {report_path}")

if __name__ == '__main__':
    extractor = ProperContractorExtractor()
    extractor.run()

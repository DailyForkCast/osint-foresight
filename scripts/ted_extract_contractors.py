#!/usr/bin/env python3
"""
Extract contractor/supplier information from TED contracts
This is the CRITICAL missing piece - we were only searching titles, not actual contractor names!
"""

import sqlite3
import json
import logging
from pathlib import Path
from datetime import datetime
from lxml import etree

# Setup logging
log_dir = Path("C:/Projects/OSINT - Foresight/logs")
log_file = log_dir / f"ted_contractors_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"

# Chinese company list
CHINESE_COMPANIES = [
    'huawei', 'zte', 'alibaba', 'tencent', 'baidu', 'xiaomi', 'oppo', 'vivo',
    'lenovo', 'dahua', 'hikvision', 'tiktok', 'bytedance', 'dji',
    'longi', 'ja solar', 'trina', 'jinko', 'canadian solar', 'risen energy',
    'byd', 'geely', 'great wall', 'nio', 'xpeng', 'li auto', 'chery',
    'crrc', 'china railway', 'cosco', 'china shipping',
    'china state construction', 'cscec', 'china railway construction',
    'sany', 'zoomlion', 'xcmg', 'weichai', 'midea', 'gree electric',
    'sinopec', 'petrochina', 'cnooc', 'chalco', 'baoshan steel',
    'comac', 'avic'
]

class ContractorExtractor:
    """Extract contractor names from existing TED contract XML"""

    def __init__(self):
        self.ns = {'ted': 'http://publications.europa.eu/TED_schema/Export'}
        self.conn = sqlite3.connect(DB_PATH)
        self.cur = self.conn.cursor()

        # Add contractor fields if they don't exist
        try:
            self.cur.execute('''
                ALTER TABLE ted_contracts_production
                ADD COLUMN contractor_name TEXT
            ''')
            self.cur.execute('''
                ALTER TABLE ted_contracts_production
                ADD COLUMN contractor_country TEXT
            ''')
            self.cur.execute('''
                ALTER TABLE ted_contracts_production
                ADD COLUMN contractor_address TEXT
            ''')
            self.conn.commit()
            logger.info("Added contractor fields to database")
        except sqlite3.OperationalError:
            logger.info("Contractor fields already exist")

        self.stats = {
            'contracts_checked': 0,
            'contractors_extracted': 0,
            'chinese_contractors_found': 0,
            'files_not_found': 0
        }

    def extract_contractor_from_xml(self, xml_path):
        """Extract contractor information from TED XML file"""
        try:
            tree = etree.parse(str(xml_path))
            root = tree.getroot()

            contractors = []

            # Look for ECONOMIC_OPERATOR_NAME_ADDRESS in all language versions
            # This appears in AWARD_OF_CONTRACT sections
            operator_sections = root.findall('.//ECONOMIC_OPERATOR_NAME_ADDRESS', self.ns)

            if not operator_sections:
                # Try without namespace (some files might not use it consistently)
                operator_sections = root.findall('.//ECONOMIC_OPERATOR_NAME_ADDRESS')

            for operator in operator_sections:
                contractor_info = {}

                # Get company name
                org_name = operator.find('.//OFFICIALNAME', self.ns)
                if org_name is None:
                    org_name = operator.find('.//OFFICIALNAME')

                if org_name is not None and org_name.text:
                    contractor_info['name'] = org_name.text.strip()

                # Get country
                country = operator.find('.//COUNTRY', self.ns)
                if country is None:
                    country = operator.find('.//COUNTRY')

                if country is not None:
                    contractor_info['country'] = country.get('VALUE', '')

                # Get address
                address_elem = operator.find('.//ADDRESS', self.ns)
                if address_elem is None:
                    address_elem = operator.find('.//ADDRESS')

                if address_elem is not None and address_elem.text:
                    contractor_info['address'] = address_elem.text.strip()

                # Get town
                town_elem = operator.find('.//TOWN', self.ns)
                if town_elem is None:
                    town_elem = operator.find('.//TOWN')

                if town_elem is not None and town_elem.text:
                    if 'address' in contractor_info:
                        contractor_info['address'] += f", {town_elem.text.strip()}"
                    else:
                        contractor_info['address'] = town_elem.text.strip()

                if contractor_info.get('name'):
                    contractors.append(contractor_info)

            return contractors

        except Exception as e:
            logger.debug(f"Failed to parse {xml_path}: {e}")
            return []

    def check_chinese_contractor(self, contractor_name):
        """Check if contractor name matches Chinese companies"""
        if not contractor_name:
            return False, []

        name_lower = contractor_name.lower()

        matched_companies = []
        for company in CHINESE_COMPANIES:
            # Check for company name in contractor name
            if company in name_lower:
                matched_companies.append(company)

        # Also check for China-specific indicators
        if 'china' in name_lower or 'chinese' in name_lower or 'beijing' in name_lower or 'shanghai' in name_lower:
            if 'china' not in matched_companies:
                matched_companies.append('(generic china mention)')

        return len(matched_companies) > 0, matched_companies

    def process_all_contracts(self):
        """Process all existing contracts to extract contractor information"""
        logger.info("="*80)
        logger.info("EXTRACTING CONTRACTOR INFORMATION FROM TED CONTRACTS")
        logger.info("="*80)

        # Get all contracts with source XML files
        self.cur.execute('''
            SELECT id, source_xml_file, contract_title
            FROM ted_contracts_production
            WHERE source_xml_file IS NOT NULL
        ''')

        contracts = self.cur.fetchall()
        logger.info(f"Found {len(contracts):,} contracts to process")

        for contract_id, xml_file, title in contracts:
            self.stats['contracts_checked'] += 1

            if not xml_file or not Path(xml_file).exists():
                self.stats['files_not_found'] += 1
                continue

            # Extract contractors
            contractors = self.extract_contractor_from_xml(xml_file)

            if contractors:
                # Use first contractor (primary winner)
                contractor = contractors[0]

                contractor_name = contractor.get('name', '')
                contractor_country = contractor.get('country', '')
                contractor_address = contractor.get('address', '')

                # Update database
                self.cur.execute('''
                    UPDATE ted_contracts_production
                    SET contractor_name = ?,
                        contractor_country = ?,
                        contractor_address = ?
                    WHERE id = ?
                ''', (contractor_name, contractor_country, contractor_address, contract_id))

                self.stats['contractors_extracted'] += 1

                # Check if Chinese
                is_chinese, matched = self.check_chinese_contractor(contractor_name)
                if is_chinese or contractor_country == 'CN':
                    self.cur.execute('''
                        UPDATE ted_contracts_production
                        SET is_chinese_related = 1,
                            chinese_confidence = 0.95,
                            chinese_indicators = ?
                        WHERE id = ?
                    ''', (json.dumps({
                        'contractor': contractor_name,
                        'country': contractor_country,
                        'matched_companies': matched
                    }), contract_id))

                    self.stats['chinese_contractors_found'] += 1

                    logger.info(f"  CHINESE CONTRACTOR FOUND: {contractor_name} ({contractor_country})")

            # Commit every 10,000 contracts
            if self.stats['contracts_checked'] % 10000 == 0:
                self.conn.commit()
                logger.info(f"  Processed {self.stats['contracts_checked']:,} contracts, "
                           f"{self.stats['contractors_extracted']:,} contractors extracted, "
                           f"{self.stats['chinese_contractors_found']} Chinese contractors")

        # Final commit
        self.conn.commit()

        logger.info("\n" + "="*80)
        logger.info("CONTRACTOR EXTRACTION COMPLETE")
        logger.info("="*80)
        logger.info(f"Contracts checked: {self.stats['contracts_checked']:,}")
        logger.info(f"Contractors extracted: {self.stats['contractors_extracted']:,}")
        logger.info(f"Chinese contractors found: {self.stats['chinese_contractors_found']}")
        logger.info(f"Files not found: {self.stats['files_not_found']:,}")

        # Generate detailed report
        logger.info("\n" + "="*80)
        logger.info("CHINESE CONTRACTOR DETAILS")
        logger.info("="*80)

        self.cur.execute('''
            SELECT contractor_name, contractor_country, contract_title, publication_date, chinese_indicators
            FROM ted_contracts_production
            WHERE is_chinese_related = 1
            ORDER BY publication_date
        ''')

        for row in self.cur.fetchall():
            name, country, title, date, indicators = row
            logger.info(f"\n{date} - {country}")
            logger.info(f"  Contractor: {name}")
            logger.info(f"  Contract: {title[:100]}")
            if indicators:
                logger.info(f"  Indicators: {indicators}")

        self.conn.close()

if __name__ == '__main__':
    extractor = ContractorExtractor()
    extractor.process_all_contracts()

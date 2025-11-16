#!/usr/bin/env python3
"""
Complete TED contractor extraction - ALL archives, ALL years
Handles both OLD (2006-2024) and NEW (2025+) XML formats
"""

import tarfile
import sqlite3
import json
import hashlib
import logging
from pathlib import Path
from datetime import datetime
from lxml import etree
import sys

# Setup logging
log_file = Path("C:/Projects/OSINT - Foresight/logs") / f"ted_complete_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

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
TEMP_BASE = Path("C:/Projects/OSINT - Foresight/data/temp/complete_extraction")
TEMP_BASE.mkdir(parents=True, exist_ok=True)

CHECKPOINT_FILE = Path("C:/Projects/OSINT - Foresight/data/ted_contractor_checkpoint.json")

# Chinese companies and locations
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

# Load comprehensive Chinese locations
with open('C:/Projects/OSINT - Foresight/data/chinese_locations.json') as f:
    locations_data = json.load(f)

# Flatten all location lists
CHINESE_LOCATIONS = []
for key in ['tier1_cities', 'tier1_special', 'provincial_capitals', 'tier2_cities', 'tier3_major',
            'economic_zones', 'provinces', 'autonomous_regions', 'special_administrative_regions']:
    if key in locations_data:
        CHINESE_LOCATIONS.extend(locations_data[key])

# Add alternative romanizations
for alts in locations_data.get('alternative_romanizations', {}).values():
    CHINESE_LOCATIONS.extend(alts)

# Remove duplicates and sort by length (longer first for better matching)
CHINESE_LOCATIONS = sorted(list(set(CHINESE_LOCATIONS)), key=len, reverse=True)

class ComprehensiveContractorExtractor:
    def __init__(self):
        self.ns_old = {'ted': 'http://publications.europa.eu/TED_schema/Export'}
        self.ns_new = {
            'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
            'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
        }

        self.conn = sqlite3.connect(DB_PATH)
        self.cur = self.conn.cursor()

        # Create contractor extraction table
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS ted_contractors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id TEXT,
                contractor_name TEXT,
                contractor_country TEXT,
                contractor_address TEXT,
                is_chinese BOOLEAN,
                chinese_indicators TEXT,
                contract_title TEXT,
                publication_date TEXT,
                source_archive TEXT,
                processing_timestamp TEXT,
                UNIQUE(document_id, contractor_name)
            )
        ''')
        self.conn.commit()

        self.stats = {
            'archives_processed': 0,
            'archives_total': 0,
            'xml_files_processed': 0,
            'contractors_extracted': 0,
            'chinese_contractors_found': 0,
            'errors': []
        }

        # Load checkpoint
        self.checkpoint = self.load_checkpoint()

    def load_checkpoint(self):
        """Load processing checkpoint"""
        if CHECKPOINT_FILE.exists():
            with open(CHECKPOINT_FILE) as f:
                return json.load(f)
        return {'processed_archives': []}

    def save_checkpoint(self):
        """Save processing checkpoint"""
        with open(CHECKPOINT_FILE, 'w') as f:
            json.dump(self.checkpoint, f, indent=2)

    def extract_contractors_old_format(self, root):
        """Extract contractors from OLD format (2006-2024)"""
        contractors = []

        ops = root.findall('.//ted:ECONOMIC_OPERATOR_NAME_ADDRESS', self.ns_old)

        for op in ops:
            contractor = {}

            contact = op.find('ted:CONTACT_DATA_WITHOUT_RESPONSIBLE_NAME', self.ns_old)
            if contact is not None:
                org = contact.find('ted:ORGANISATION', self.ns_old)
                if org is not None:
                    name_elem = org.find('ted:OFFICIALNAME', self.ns_old)
                    if name_elem is not None and name_elem.text:
                        contractor['name'] = name_elem.text.strip()

                country_elem = contact.find('ted:COUNTRY', self.ns_old)
                if country_elem is not None:
                    contractor['country'] = country_elem.get('VALUE', '')

                addr_elem = contact.find('ted:ADDRESS', self.ns_old)
                town_elem = contact.find('ted:TOWN', self.ns_old)

                address_parts = []
                if addr_elem is not None and addr_elem.text:
                    address_parts.append(addr_elem.text.strip())
                if town_elem is not None and town_elem.text:
                    address_parts.append(town_elem.text.strip())

                if address_parts:
                    contractor['address'] = ', '.join(address_parts)

            if contractor.get('name'):
                contractors.append(contractor)

        return contractors

    def extract_contractors_new_format(self, root):
        """Extract contractors from NEW format (2025+)"""
        contractors = []

        parties = root.findall('.//cac:Party', self.ns_new)

        for party in parties:
            contractor = {}

            name_elem = party.find('.//cbc:Name', self.ns_new)
            if name_elem is not None and name_elem.text:
                contractor['name'] = name_elem.text.strip()

            country_elem = party.find('.//cac:Country/cbc:IdentificationCode', self.ns_new)
            if country_elem is not None and country_elem.text:
                contractor['country'] = country_elem.text.strip()

            # Address
            addr_lines = party.findall('.//cac:PostalAddress/cbc:StreetName', self.ns_new)
            city_elem = party.find('.//cac:PostalAddress/cbc:CityName', self.ns_new)

            address_parts = []
            for addr in addr_lines:
                if addr.text:
                    address_parts.append(addr.text.strip())
            if city_elem is not None and city_elem.text:
                address_parts.append(city_elem.text.strip())

            if address_parts:
                contractor['address'] = ', '.join(address_parts)

            if contractor.get('name'):
                contractors.append(contractor)

        return contractors

    def check_chinese(self, contractor_name, contractor_country):
        """Check if contractor is Chinese"""
        matched = []

        # Country code
        if contractor_country == 'CN':
            return True, ['country_CN']

        if not contractor_name:
            return False, []

        name_lower = contractor_name.lower()

        # Company names
        for company in CHINESE_COMPANIES:
            if company in name_lower and len(company) > 3:  # Avoid short false positives like "nio" in "union"
                # Verify it's a word boundary match for short names
                if len(company) <= 5:
                    if f' {company} ' in f' {name_lower} ' or name_lower.startswith(f'{company} ') or name_lower.endswith(f' {company}'):
                        matched.append(company)
                else:
                    matched.append(company)

        # Locations (high confidence)
        for loc in CHINESE_LOCATIONS:
            if loc in name_lower:
                matched.append(f'location_{loc}')

        return len(matched) > 0, matched

    def process_xml(self, xml_path, source_archive):
        """Process single XML file"""
        try:
            tree = etree.parse(str(xml_path))
            root = tree.getroot()

            # Detect format
            root_tag = root.tag.split('}')[-1] if '}' in root.tag else root.tag

            # Extract basic info
            doc_id = None
            pub_date = None
            title = None

            if 'TED_EXPORT' in root_tag:
                # OLD format
                doc_num = root.find('.//ted:NO_DOC_OJS', self.ns_old)
                date_pub = root.find('.//ted:DATE_PUB', self.ns_old)
                ml_title = root.find('.//ted:ML_TI_DOC[@LG="EN"]', self.ns_old)

                if doc_num is not None:
                    doc_id = doc_num.text
                if date_pub is not None:
                    pub_date = date_pub.text
                if ml_title is not None:
                    title_elem = ml_title.find('ted:TI_TEXT', self.ns_old)
                    if title_elem is not None and title_elem.text:
                        title = title_elem.text.strip()

                contractors = self.extract_contractors_old_format(root)
            else:
                # NEW format
                doc_id_elem = root.find('.//cbc:ID', self.ns_new)
                date_elem = root.find('.//cbc:IssueDate', self.ns_new)
                title_elem = root.find('.//cbc:Title', self.ns_new)

                if doc_id_elem is not None:
                    doc_id = doc_id_elem.text
                if date_elem is not None:
                    pub_date = date_elem.text
                if title_elem is not None and title_elem.text:
                    title = title_elem.text.strip()

                contractors = self.extract_contractors_new_format(root)

            self.stats['xml_files_processed'] += 1

            # Save contractors
            for contractor in contractors:
                self.stats['contractors_extracted'] += 1

                is_chinese, matched = self.check_chinese(
                    contractor.get('name', ''),
                    contractor.get('country', '')
                )

                if is_chinese:
                    self.stats['chinese_contractors_found'] += 1
                    logger.info(f"  CHINESE: {contractor.get('name', '')} ({contractor.get('country', '')})")

                # Insert into database
                try:
                    self.cur.execute('''
                        INSERT OR IGNORE INTO ted_contractors (
                            document_id, contractor_name, contractor_country, contractor_address,
                            is_chinese, chinese_indicators, contract_title, publication_date,
                            source_archive, processing_timestamp
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        doc_id,
                        contractor.get('name', ''),
                        contractor.get('country', ''),
                        contractor.get('address', ''),
                        is_chinese,
                        json.dumps(matched) if matched else None,
                        title,
                        pub_date,
                        source_archive,
                        datetime.now().isoformat()
                    ))
                except Exception as e:
                    logger.debug(f"Failed to insert contractor: {e}")

        except Exception as e:
            logger.debug(f"Failed to parse {xml_path.name}: {e}")

    def process_archive(self, archive_path):
        """Process one monthly archive"""
        archive_name = archive_path.name

        if archive_name in self.checkpoint['processed_archives']:
            logger.info(f"Skipping {archive_name} (already processed)")
            return

        logger.info(f"\n{'='*80}")
        logger.info(f"[{self.stats['archives_processed']+1}/{self.stats['archives_total']}] {archive_name}")
        logger.info(f"{'='*80}")

        archive_temp = TEMP_BASE / archive_path.stem
        archive_temp.mkdir(exist_ok=True)

        try:
            # Extract monthly archive
            with tarfile.open(archive_path, 'r:gz', errorlevel=0) as tar:
                tar.extractall(archive_temp)

            # Find daily archives
            daily_archives = list(archive_temp.rglob("*.tar.gz"))
            logger.info(f"Found {len(daily_archives)} daily archives")

            for i, daily_archive in enumerate(daily_archives):
                if i % 5 == 0:
                    logger.info(f"  Processing daily [{i+1}/{len(daily_archives)}]...")

                daily_temp = TEMP_BASE / "daily" / daily_archive.stem
                daily_temp.mkdir(parents=True, exist_ok=True)

                try:
                    with tarfile.open(daily_archive, 'r:gz', errorlevel=0) as tar:
                        tar.extractall(daily_temp)

                    xml_files = list(daily_temp.rglob("*.xml"))

                    for xml_file in xml_files:
                        self.process_xml(xml_file, archive_name)

                    # Cleanup daily temp
                    import shutil
                    shutil.rmtree(daily_temp, ignore_errors=True)

                except Exception as e:
                    self.stats['errors'].append(f"{daily_archive.name}: {str(e)}")

            # Cleanup archive temp
            import shutil
            shutil.rmtree(archive_temp, ignore_errors=True)

            # Mark as processed
            self.checkpoint['processed_archives'].append(archive_name)
            self.stats['archives_processed'] += 1

            # Commit and save checkpoint every archive
            self.conn.commit()
            self.save_checkpoint()

            logger.info(f"  Total contractors: {self.stats['contractors_extracted']:,}")
            logger.info(f"  Chinese contractors: {self.stats['chinese_contractors_found']}")

        except Exception as e:
            logger.error(f"Failed to process {archive_name}: {e}")
            self.stats['errors'].append(f"{archive_name}: {str(e)}")

    def run(self):
        """Process all TED archives"""
        logger.info("="*80)
        logger.info("TED COMPLETE CONTRACTOR EXTRACTION")
        logger.info("="*80)

        # Find all archives
        all_archives = []
        for year_dir in sorted(ARCHIVE_DIR.iterdir()):
            if year_dir.is_dir():
                archives = sorted(list(year_dir.glob("TED_monthly_*.tar.gz")))
                all_archives.extend(archives)

        self.stats['archives_total'] = len(all_archives)
        logger.info(f"Found {len(all_archives)} archives to process")
        logger.info(f"Already processed: {len(self.checkpoint['processed_archives'])}")

        # Process each archive
        for archive in all_archives:
            self.process_archive(archive)

        # Final report
        logger.info("\n" + "="*80)
        logger.info("EXTRACTION COMPLETE")
        logger.info("="*80)
        logger.info(f"Archives processed: {self.stats['archives_processed']}/{self.stats['archives_total']}")
        logger.info(f"XML files processed: {self.stats['xml_files_processed']:,}")
        logger.info(f"Contractors extracted: {self.stats['contractors_extracted']:,}")
        logger.info(f"Chinese contractors found: {self.stats['chinese_contractors_found']}")
        logger.info(f"Errors: {len(self.stats['errors'])}")

        # Query final stats
        logger.info("\n" + "="*80)
        logger.info("DATABASE STATISTICS")
        logger.info("="*80)

        self.cur.execute("SELECT COUNT(*) FROM ted_contractors")
        logger.info(f"Total contractors in database: {self.cur.fetchone()[0]:,}")

        self.cur.execute("SELECT COUNT(*) FROM ted_contractors WHERE is_chinese = 1")
        logger.info(f"Chinese contractors: {self.cur.fetchone()[0]}")

        # Show verified Chinese contractors
        logger.info("\n" + "="*80)
        logger.info("VERIFIED CHINESE CONTRACTORS")
        logger.info("="*80)

        self.cur.execute('''
            SELECT contractor_name, contractor_country, contract_title, publication_date, chinese_indicators
            FROM ted_contractors
            WHERE is_chinese = 1
            AND (contractor_country = 'CN' OR chinese_indicators LIKE '%beijing%' OR chinese_indicators LIKE '%shanghai%')
            ORDER BY publication_date
        ''')

        for row in self.cur.fetchall():
            name, country, title, date, indicators = row
            logger.info(f"\n{date}")
            logger.info(f"  {name} ({country})")
            logger.info(f"  {title[:100] if title else 'No title'}")

        self.conn.close()

if __name__ == '__main__':
    extractor = ComprehensiveContractorExtractor()
    extractor.run()

#!/usr/bin/env python3
"""
Process recovered TED archives and extract contract data
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
log_dir = Path("C:/Projects/OSINT - Foresight/logs")
log_file = log_dir / f"ted_recovered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

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
RECOVERY_BASE = Path("C:/Projects/OSINT - Foresight/data/temp/raw_recovery")

class RecoveredProcessor:
    """Process recovered TED data with namespace support"""

    def __init__(self):
        self.ns = {'ted': 'http://publications.europa.eu/TED_schema/Export'}
        self.conn = sqlite3.connect(DB_PATH)
        self.cur = self.conn.cursor()

        self.stats = {
            'daily_archives_processed': 0,
            'xml_files_processed': 0,
            'contracts_saved': 0,
            'china_contracts': 0,
            'errors': []
        }

        # Chinese company list for detection
        self.chinese_companies = [
            'huawei', 'zte', 'alibaba', 'tencent', 'baidu', 'xiaomi', 'oppo', 'vivo',
            'lenovo', 'dahua', 'hikvision', 'tiktok', 'bytedance', 'dji',
            'longi', 'ja solar', 'trina', 'jinko', 'canadian solar',
            'byd', 'geely', 'nio', 'xpeng', 'crrc', 'cosco', 'sany', 'zoomlion'
        ]

    def process_daily_archive(self, daily_archive, source_monthly):
        """Extract and process XML files from daily archive"""
        daily_temp = Path("C:/Projects/OSINT - Foresight/data/temp/daily_recovery")
        daily_temp.mkdir(parents=True, exist_ok=True)

        try:
            # Extract daily archive
            with tarfile.open(daily_archive, 'r:gz', errorlevel=0) as tar:
                tar.extractall(daily_temp)

            # Find XML files
            xml_files = list(daily_temp.rglob("*.xml"))
            logger.info(f"    Found {len(xml_files)} XML files in {daily_archive.name}")

            for xml_file in xml_files:
                self.process_xml_file(xml_file, source_monthly)

            self.stats['daily_archives_processed'] += 1

            # Cleanup
            import shutil
            shutil.rmtree(daily_temp, ignore_errors=True)

        except Exception as e:
            logger.warning(f"    Failed to process {daily_archive.name}: {e}")
            self.stats['errors'].append(f"{daily_archive.name}: {str(e)}")

    def process_xml_file(self, xml_path, source_archive):
        """Extract contract data from XML using namespace-aware parsing"""
        try:
            tree = etree.parse(str(xml_path))
            root = tree.getroot()

            # Extract basic metadata with namespace
            doc_num = root.find('.//ted:NO_DOC_OJS', self.ns)
            date_pub = root.find('.//ted:DATE_PUB', self.ns)
            iso_country = root.find('.//ted:ISO_COUNTRY', self.ns)

            # Get contract title from multilingual section
            title = None
            ml_title = root.find('.//ted:ML_TI_DOC[@LG="EN"]', self.ns)
            if ml_title is not None:
                title_elem = ml_title.find('ted:TI_TEXT', self.ns)
                if title_elem is not None and title_elem.text:
                    title = title_elem.text.strip()

            # Get CPV code
            cpv_code = root.find('.//ted:CPV_CODE', self.ns)

            # Get contracting authority name
            ca_name = root.find('.//ted:OFFICIALNAME', self.ns)

            # Create contract record
            document_id = doc_num.text if doc_num is not None else None
            if not document_id:
                return  # Skip if no document ID

            # Calculate hash for deduplication
            xml_hash = hashlib.md5(etree.tostring(root)).hexdigest()

            # Check for Chinese indicators
            is_chinese = False
            chinese_confidence = 0.0
            chinese_indicators = {}

            if title:
                title_lower = title.lower()
                matched_companies = [c for c in self.chinese_companies if c in title_lower]
                if matched_companies:
                    is_chinese = True
                    chinese_confidence = 0.9
                    chinese_indicators['companies'] = matched_companies

            # Insert into database
            self.cur.execute('''
                INSERT OR IGNORE INTO ted_contracts_production (
                    document_id, notice_number, publication_date, iso_country,
                    contract_title, cpv_code, ca_name, source_archive, source_xml_file,
                    is_chinese_related, chinese_confidence, chinese_indicators,
                    processing_timestamp, xml_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                document_id,
                doc_num.text if doc_num is not None else None,
                date_pub.text if date_pub is not None else None,
                iso_country.text if iso_country is not None else None,
                title,
                cpv_code.get('CODE') if cpv_code is not None else None,
                ca_name.text if ca_name is not None else None,
                source_archive,
                str(xml_path),
                is_chinese,
                chinese_confidence,
                json.dumps(chinese_indicators) if chinese_indicators else None,
                datetime.now().isoformat(),
                xml_hash
            ))

            self.stats['xml_files_processed'] += 1
            if is_chinese:
                self.stats['china_contracts'] += 1

            if self.conn.total_changes > 0:
                self.stats['contracts_saved'] += 1

        except Exception as e:
            logger.debug(f"      Failed to parse {xml_path.name}: {e}")

    def process_all(self):
        """Process all recovered archives"""
        logger.info(f"\n{'='*80}")
        logger.info("PROCESSING RECOVERED ARCHIVES")
        logger.info(f"{'='*80}")

        # Find all monthly recovery directories
        monthly_dirs = [d for d in RECOVERY_BASE.iterdir() if d.is_dir()]

        for monthly_dir in monthly_dirs:
            logger.info(f"\nProcessing: {monthly_dir.name}")

            # Find all .tar.gz files
            daily_archives = list(monthly_dir.glob("*.tar.gz")) + list(monthly_dir.glob("*/*.tar.gz"))
            logger.info(f"  Found {len(daily_archives)} daily archives")

            for daily_archive in daily_archives:
                self.process_daily_archive(daily_archive, monthly_dir.name)

                # Commit after each daily archive
                self.conn.commit()

        # Final commit and report
        self.conn.commit()

        logger.info(f"\n{'='*80}")
        logger.info("RECOVERED DATA PROCESSING COMPLETE")
        logger.info(f"{'='*80}")
        logger.info(f"Daily archives processed: {self.stats['daily_archives_processed']}")
        logger.info(f"XML files processed: {self.stats['xml_files_processed']:,}")
        logger.info(f"Contracts saved: {self.stats['contracts_saved']:,}")
        logger.info(f"China-related contracts: {self.stats['china_contracts']}")
        logger.info(f"Errors: {len(self.stats['errors'])}")

        self.conn.close()

if __name__ == '__main__':
    processor = RecoveredProcessor()
    processor.process_all()

#!/usr/bin/env python3
"""
Recover data from corrupted TED archives using permissive extraction
Uses errorlevel=0 to extract as much data as possible despite EOF errors
"""

import tarfile
import gzip
import sqlite3
import json
import hashlib
import logging
from pathlib import Path
from datetime import datetime
from lxml import etree

# Setup logging
log_dir = Path("C:/Projects/OSINT - Foresight/logs")
log_dir.mkdir(exist_ok=True)
log_file = log_dir / f"ted_recovery_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Database and paths
DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"
TEMP_BASE = Path("C:/Projects/OSINT - Foresight/data/temp/recovery")
TEMP_BASE.mkdir(parents=True, exist_ok=True)

# Corrupted archives to recover
CORRUPTED_ARCHIVES = [
    "F:/TED_Data/monthly/2011/TED_monthly_2011_01.tar.gz",
    "F:/TED_Data/monthly/2014/TED_monthly_2014_01.tar.gz",
    "F:/TED_Data/monthly/2024/TED_monthly_2024_08.tar.gz"
]

class TEDRecoveryProcessor:
    """Process TED XML with namespace support and permissive error handling"""

    def __init__(self):
        self.ns = {'ted': 'http://publications.europa.eu/TED_schema/Export'}
        self.conn = sqlite3.connect(DB_PATH)
        self.cur = self.conn.cursor()

        self.stats = {
            'archives_attempted': 0,
            'archives_recovered': 0,
            'inner_archives_extracted': 0,
            'xml_files_processed': 0,
            'contracts_saved': 0,
            'china_contracts': 0,
            'extraction_errors': [],
            'processing_errors': []
        }

    def extract_archive_permissive(self, archive_path):
        """Extract archive using permissive mode (errorlevel=0)"""
        archive_name = Path(archive_path).name
        logger.info(f"\n{'='*80}")
        logger.info(f"RECOVERING: {archive_name}")
        logger.info(f"{'='*80}")

        # Create temp directory for this archive
        temp_dir = TEMP_BASE / archive_name.replace('.tar.gz', '')
        temp_dir.mkdir(parents=True, exist_ok=True)

        extracted_members = []

        try:
            # Try to open with permissive mode
            with tarfile.open(archive_path, 'r:gz', errorlevel=0) as tar:
                for member in tar:
                    try:
                        tar.extract(member, temp_dir)
                        extracted_members.append(member.name)

                        if len(extracted_members) % 100 == 0:
                            logger.info(f"  Extracted {len(extracted_members)} members...")

                    except Exception as e:
                        self.stats['extraction_errors'].append(f"{archive_name}/{member.name}: {str(e)}")
                        logger.warning(f"  Skipping member {member.name}: {e}")
                        continue

            logger.info(f"  ✓ Extracted {len(extracted_members)} members from {archive_name}")
            self.stats['archives_recovered'] += 1
            return temp_dir

        except Exception as e:
            logger.error(f"  ✗ Failed to open {archive_name}: {e}")
            self.stats['extraction_errors'].append(f"{archive_name}: {str(e)}")
            return None

    def process_inner_archive(self, inner_path, source_archive):
        """Process nested .tar.gz archive"""
        try:
            daily_temp = TEMP_BASE / f"daily_{Path(inner_path).stem}"
            daily_temp.mkdir(parents=True, exist_ok=True)

            with tarfile.open(inner_path, 'r:gz', errorlevel=0) as daily_tar:
                daily_tar.extractall(daily_temp)

            self.stats['inner_archives_extracted'] += 1

            # Find all XML files recursively
            xml_files = list(daily_temp.rglob("*.xml"))
            logger.info(f"    Found {len(xml_files)} XML files in {Path(inner_path).name}")

            # Process each XML
            for xml_file in xml_files:
                self.process_xml_file(xml_file, source_archive)

            # Cleanup
            import shutil
            shutil.rmtree(daily_temp, ignore_errors=True)

        except Exception as e:
            logger.warning(f"    Failed to process inner archive {inner_path}: {e}")
            self.stats['processing_errors'].append(f"{inner_path}: {str(e)}")

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
                chinese_companies = [
                    'huawei', 'zte', 'alibaba', 'tencent', 'baidu', 'xiaomi', 'oppo', 'vivo',
                    'lenovo', 'dahua', 'hikvision', 'tiktok', 'bytedance', 'dji',
                    'longi', 'ja solar', 'trina', 'jinko', 'canadian solar',
                    'byd', 'geely', 'nio', 'xpeng', 'crrc', 'cosco', 'sany'
                ]

                matched_companies = [c for c in chinese_companies if c in title_lower]
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
            self.stats['processing_errors'].append(f"{xml_path.name}: {str(e)}")

    def process_all(self):
        """Process all corrupted archives"""
        start_time = datetime.now()

        for archive_path in CORRUPTED_ARCHIVES:
            self.stats['archives_attempted'] += 1

            # Extract outer archive
            temp_dir = self.extract_archive_permissive(archive_path)
            if not temp_dir:
                continue

            # Find and process all .tar.gz files inside
            inner_archives = list(temp_dir.rglob("*.tar.gz"))
            logger.info(f"  Found {len(inner_archives)} inner archives")

            for inner_archive in inner_archives:
                self.process_inner_archive(inner_archive, Path(archive_path).name)

                # Commit every inner archive
                self.conn.commit()
                logger.info(f"    Stats: {self.stats['contracts_saved']:,} contracts saved, "
                           f"{self.stats['china_contracts']} China-related")

            # Cleanup temp directory
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)

        # Final commit
        self.conn.commit()

        # Generate report
        duration = (datetime.now() - start_time).total_seconds()

        logger.info(f"\n{'='*80}")
        logger.info("RECOVERY COMPLETE")
        logger.info(f"{'='*80}")
        logger.info(f"Duration: {duration:.1f} seconds")
        logger.info(f"\nArchives:")
        logger.info(f"  Attempted: {self.stats['archives_attempted']}")
        logger.info(f"  Recovered: {self.stats['archives_recovered']}")
        logger.info(f"  Inner archives extracted: {self.stats['inner_archives_extracted']}")
        logger.info(f"\nData:")
        logger.info(f"  XML files processed: {self.stats['xml_files_processed']:,}")
        logger.info(f"  Contracts saved: {self.stats['contracts_saved']:,}")
        logger.info(f"  China-related contracts: {self.stats['china_contracts']}")
        logger.info(f"\nErrors:")
        logger.info(f"  Extraction errors: {len(self.stats['extraction_errors'])}")
        logger.info(f"  Processing errors: {len(self.stats['processing_errors'])}")

        if len(self.stats['extraction_errors']) <= 10:
            for err in self.stats['extraction_errors']:
                logger.info(f"    {err}")

        # Save report
        report_path = Path("C:/Projects/OSINT - Foresight/analysis/ted_recovery_report.json")
        with open(report_path, 'w') as f:
            json.dump({
                **self.stats,
                'duration_seconds': duration,
                'timestamp': datetime.now().isoformat()
            }, f, indent=2)

        logger.info(f"\nReport saved: {report_path}")

        self.conn.close()

if __name__ == '__main__':
    processor = TEDRecoveryProcessor()
    processor.process_all()

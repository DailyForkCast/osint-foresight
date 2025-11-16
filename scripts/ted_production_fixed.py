#!/usr/bin/env python3
"""
TED Production Processor - FIXED VERSION
Correctly handles XML namespaces and actual TED XML structure
"""

import os
import sys
import tarfile
import logging
import json
import sqlite3
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import hashlib
import re

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s',
    handlers=[
        logging.FileHandler('C:/Projects/OSINT - Foresight/logs/ted_prod_20251001_170740.log', mode='a'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TEDProcessorFixed:
    """TED processor with correct namespace handling"""

    def __init__(self):
        self.source_dir = Path("F:/TED_Data/monthly")
        self.db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")
        self.temp_dir = Path("C:/Projects/OSINT - Foresight/data/temp/ted_extraction")
        self.checkpoint_file = Path("C:/Projects/OSINT - Foresight/data/ted_production_checkpoint.json")

        # TED XML namespace
        self.ns = {'ted': 'http://publications.europa.eu/TED_schema/Export'}

        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.init_database()
        self.checkpoint = self.load_checkpoint()

        self.stats = {
            'archives_processed': 0,
            'archives_total': 0,
            'inner_archives_processed': 0,
            'xml_files_processed': 0,
            'china_contracts_found': 0,
            'total_contracts_saved': 0,
            'errors': [],
            'start_time': datetime.now().isoformat()
        }

    def init_database(self):
        """Create database table"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute('''
            CREATE TABLE IF NOT EXISTS ted_contracts_production (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id TEXT UNIQUE,
                notice_number TEXT,
                publication_date TEXT,
                iso_country TEXT,
                contract_title TEXT,
                cpv_code TEXT,

                ca_name TEXT,

                contractor_info TEXT,

                source_archive TEXT,
                source_xml_file TEXT,

                is_chinese_related BOOLEAN DEFAULT 0,
                chinese_confidence REAL DEFAULT 0,
                chinese_indicators TEXT,

                processing_timestamp TEXT,
                xml_hash TEXT
            )
        ''')
        conn.commit()
        conn.close()
        logger.info("Database initialized")

    def load_checkpoint(self) -> Dict:
        """Load processing checkpoint"""
        if self.checkpoint_file.exists():
            with open(self.checkpoint_file, 'r') as f:
                return json.load(f)
        return {'processed_archives': [], 'last_archive': None, 'last_update': None, 'stats': {}}

    def save_checkpoint(self):
        """Save processing checkpoint"""
        self.checkpoint['processed_archives'] = list(set(self.checkpoint.get('processed_archives', [])))
        self.checkpoint['last_update'] = datetime.now().isoformat()
        self.checkpoint['stats'] = self.stats

        with open(self.checkpoint_file, 'w') as f:
            json.dump(self.checkpoint, f, indent=2)

    def run(self):
        """Main processing loop"""
        archives = sorted(self.source_dir.rglob("TED_monthly_*.tar.gz"))
        self.stats['archives_total'] = len(archives)

        processed_set = set(self.checkpoint.get('processed_archives', []))

        logger.info(f"Found {len(archives)} total archives")
        logger.info(f"Already processed: {len(processed_set)}")

        for idx, archive_path in enumerate(archives, 1):
            archive_str = str(archive_path)

            if archive_str in processed_set:
                logger.info(f"[{idx}/{len(archives)}] SKIPPING (already processed): {archive_path.name}")
                continue

            logger.info("=" * 80)
            logger.info(f"[{idx}/{len(archives)}] PROCESSING: {archive_path.name}")
            logger.info("=" * 80)

            try:
                self.process_monthly_archive(archive_path)
                self.checkpoint['processed_archives'].append(archive_str)
                self.stats['archives_processed'] += 1
                self.save_checkpoint()
            except Exception as e:
                error_msg = f"FAILED to process {archive_path.name}: {e}"
                logger.error(error_msg)
                self.stats['errors'].append(error_msg)
                self.save_checkpoint()
                continue

    def process_monthly_archive(self, monthly_archive: Path):
        """Process one monthly archive"""
        archive_temp = self.temp_dir / f"monthly_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        archive_temp.mkdir(parents=True, exist_ok=True)

        try:
            # Extract monthly archive
            logger.info(f"Extracting outer archive: {monthly_archive.name}")
            with tarfile.open(monthly_archive, 'r:gz', errorlevel=1) as outer_tar:
                outer_tar.extractall(archive_temp)

            # Find daily archives
            daily_archives = sorted(archive_temp.rglob("*.tar.gz"))
            logger.info(f"Found {len(daily_archives)} inner (daily) archives")

            for daily_idx, daily_archive in enumerate(daily_archives, 1):
                self.process_daily_archive(daily_archive, monthly_archive.name, daily_idx, len(daily_archives))
                self.stats['inner_archives_processed'] += 1

        finally:
            import shutil
            if archive_temp.exists():
                shutil.rmtree(archive_temp, ignore_errors=True)

    def process_daily_archive(self, daily_archive: Path, monthly_name: str, idx: int, total: int):
        """Process one daily archive"""
        daily_temp = self.temp_dir / f"daily_{datetime.now().strftime('%Y%m%d_%H%M%S%f')}"
        daily_temp.mkdir(parents=True, exist_ok=True)

        try:
            logger.info(f"  [{idx}/{total}] Processing: {daily_archive.name}")

            with tarfile.open(daily_archive, 'r:gz', errorlevel=1) as daily_tar:
                daily_tar.extractall(daily_temp)

            # Find all XML files recursively
            xml_files = list(daily_temp.rglob("*.xml"))
            logger.info(f"    Found {len(xml_files)} XML files")

            china_count = 0
            for xml_file in xml_files:
                try:
                    contract = self.process_xml(xml_file, monthly_name, daily_archive.name)
                    if contract:
                        if contract.get('is_chinese_related'):
                            china_count += 1
                            self.stats['china_contracts_found'] += 1
                        self.stats['total_contracts_saved'] += 1

                    self.stats['xml_files_processed'] += 1

                    if self.stats['xml_files_processed'] % 1000 == 0:
                        logger.info(f"    Progress: {self.stats['xml_files_processed']} XML, {self.stats['total_contracts_saved']} contracts, {self.stats['china_contracts_found']} China")

                except Exception as e:
                    logger.debug(f"Error processing {xml_file.name}: {e}")

            if china_count > 0:
                logger.info(f"    ✓ Found {china_count} China-related contracts")

        finally:
            import shutil
            if daily_temp.exists():
                shutil.rmtree(daily_temp, ignore_errors=True)

    def process_xml(self, xml_file: Path, monthly_name: str, daily_name: str) -> Optional[Dict]:
        """Process single XML file with CORRECT namespace handling"""
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()

            # Extract basic data using correct namespace
            doc_num = root.find('.//ted:NO_DOC_OJS', self.ns)
            date_pub = root.find('.//ted:DATE_PUB', self.ns)
            iso_country = root.find('.//ted:ISO_COUNTRY', self.ns)
            cpv_elem = root.find('.//ted:ORIGINAL_CPV', self.ns)

            # Get English title from multilingual section
            title = None
            ml_title = root.find('.//ted:ML_TI_DOC[@LG="EN"]', self.ns)
            if ml_title is not None:
                title_elem = ml_title.find('ted:TI_TEXT', self.ns)
                if title_elem is not None:
                    title = title_elem.text

            # Get authority name
            ca_name = None
            aa_name = root.find('.//ted:AA_NAME[@LG="EN"]', self.ns)
            if aa_name is not None:
                ca_name = aa_name.text

            # Build contract record
            doc_id = (doc_num.text if doc_num is not None else xml_file.name).replace('/', '_')

            contract = {
                'document_id': doc_id,
                'notice_number': doc_num.text if doc_num is not None else None,
                'publication_date': date_pub.text if date_pub is not None else None,
                'iso_country': iso_country.get('VALUE') if iso_country is not None else None,
                'contract_title': title,
                'cpv_code': cpv_elem.get('CODE') if cpv_elem is not None else None,
                'ca_name': ca_name,
                'contractor_info': None,  # TED structure complex - extract later if needed
                'source_archive': monthly_name,
                'source_xml_file': f"{daily_name}/{xml_file.name}",
                'processing_timestamp': datetime.now().isoformat(),
                'xml_hash': hashlib.sha256(ET.tostring(root)).hexdigest()[:16]
            }

            # Check for China involvement
            china_check = self.check_china(contract, root)
            contract.update(china_check)

            # Only save if has meaningful data
            if contract.get('notice_number') or contract.get('contract_title'):
                self.save_contract(contract)
                return contract

        except ET.ParseError:
            pass
        except Exception as e:
            logger.debug(f"Error in {xml_file.name}: {e}")

        return None

    def check_china(self, contract: Dict, root: ET.Element) -> Dict:
        """Check for China involvement"""
        # Get full XML text for searching
        xml_text = ET.tostring(root, encoding='unicode', method='text').lower()

        # China patterns
        patterns = [
            r'\bchina\b', r'\bchinese\b', r'\bbeijing\b', r'\bshanghai\b',
            r'\bguangzhou\b', r'\bshenzhen\b', r'\bhong kong\b', r'\bmacau\b',
            r'\bhuawei\b', r'\bzte\b', r'\balibaba\b', r'\btencent\b'
        ]

        matches = []
        for pattern in patterns:
            if re.search(pattern, xml_text):
                matches.append(pattern)

        if matches:
            return {
                'is_chinese_related': True,
                'chinese_confidence': min(0.5 + (len(matches) * 0.1), 1.0),
                'chinese_indicators': json.dumps(matches)
            }

        return {
            'is_chinese_related': False,
            'chinese_confidence': 0.0,
            'chinese_indicators': None
        }

    def save_contract(self, contract: Dict):
        """Save contract to database"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        try:
            cur.execute('''
                INSERT OR IGNORE INTO ted_contracts_production
                (document_id, notice_number, publication_date, iso_country, contract_title,
                 cpv_code, ca_name, contractor_info, source_archive, source_xml_file,
                 is_chinese_related, chinese_confidence, chinese_indicators,
                 processing_timestamp, xml_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                contract['document_id'],
                contract['notice_number'],
                contract['publication_date'],
                contract['iso_country'],
                contract['contract_title'],
                contract['cpv_code'],
                contract['ca_name'],
                contract['contractor_info'],
                contract['source_archive'],
                contract['source_xml_file'],
                contract['is_chinese_related'],
                contract['chinese_confidence'],
                contract['chinese_indicators'],
                contract['processing_timestamp'],
                contract['xml_hash']
            ))
            conn.commit()
        except Exception as e:
            logger.error(f"DB error: {e}")
        finally:
            conn.close()


def main():
    processor = TEDProcessorFixed()
    processor.run()


if __name__ == '__main__':
    main()

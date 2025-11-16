#!/usr/bin/env python3
"""
TED Complete Production Processor
Processes all 139 TED archives (2006-2025) with Complete European Validator v3.0
Handles double-nested tar.gz structure, extracts China-related contracts
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
from typing import Dict, List, Optional, Any
import traceback
import hashlib

# Add src to path for validator
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from core.enhanced_validation_v3_complete import CompleteEuropeanValidator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/ted_production_processor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TEDProductionProcessor:
    """Complete TED archive processor with v3 validation"""

    def __init__(self):
        self.source_dir = Path("F:/TED_Data/monthly")
        self.db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")
        self.temp_dir = Path("C:/Projects/OSINT - Foresight/data/temp/ted_extraction")
        self.checkpoint_file = Path("C:/Projects/OSINT - Foresight/data/ted_production_checkpoint.json")

        # Initialize validator
        self.validator = CompleteEuropeanValidator()

        # Create temp directory
        self.temp_dir.mkdir(parents=True, exist_ok=True)

        # Initialize database
        self.init_database()

        # Load checkpoint
        self.checkpoint = self.load_checkpoint()

        # Statistics
        self.stats = {
            'archives_processed': 0,
            'archives_total': 0,
            'inner_archives_processed': 0,
            'xml_files_processed': 0,
            'china_contracts_found': 0,
            'errors': [],
            'start_time': datetime.now().isoformat(),
            'current_archive': None
        }

    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        # Create comprehensive TED table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS ted_contracts_production (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                -- Document identification
                document_id TEXT UNIQUE,
                notice_number TEXT,
                publication_date TEXT,
                document_type TEXT,
                form_type TEXT,
                source_archive TEXT,
                source_xml_file TEXT,

                -- Contracting authority
                ca_name TEXT,
                ca_official_name TEXT,
                ca_address TEXT,
                ca_city TEXT,
                ca_postal_code TEXT,
                ca_country TEXT,
                ca_type TEXT,
                ca_main_activity TEXT,

                -- Contract information
                contract_title TEXT,
                contract_description TEXT,
                contract_type TEXT,
                cpv_main TEXT,
                cpv_additional TEXT,
                nuts_code TEXT,
                place_of_performance TEXT,

                -- Contract value
                value_estimated REAL,
                value_total REAL,
                currency TEXT,

                -- Award information
                award_date TEXT,
                number_tenders_received INTEGER,

                -- Contractor information
                contractor_name TEXT,
                contractor_official_name TEXT,
                contractor_address TEXT,
                contractor_city TEXT,
                contractor_postal_code TEXT,
                contractor_country TEXT,
                contractor_sme BOOLEAN,

                -- Additional contractors (JSON)
                additional_contractors TEXT,
                subcontractors TEXT,

                -- Procedure information
                procedure_type TEXT,
                award_criteria TEXT,
                submission_deadline TEXT,
                framework_agreement BOOLEAN,
                gpa_covered BOOLEAN,

                -- China detection (v3 validator)
                is_chinese_related BOOLEAN DEFAULT 0,
                chinese_confidence REAL DEFAULT 0,
                chinese_indicators TEXT,
                chinese_entities TEXT,
                validator_version TEXT DEFAULT 'v3.0',

                -- Metadata
                processing_timestamp TEXT,
                xml_hash TEXT,

                UNIQUE(document_id)
            )
        ''')

        # Create indexes
        cur.execute('CREATE INDEX IF NOT EXISTS idx_ted_prod_contractor_country ON ted_contracts_production(contractor_country)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_ted_prod_ca_country ON ted_contracts_production(ca_country)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_ted_prod_chinese ON ted_contracts_production(is_chinese_related)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_ted_prod_pub_date ON ted_contracts_production(publication_date)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_ted_prod_archive ON ted_contracts_production(source_archive)')

        conn.commit()
        conn.close()
        logger.info("Database initialized")

    def load_checkpoint(self) -> Dict:
        """Load processing checkpoint"""
        if self.checkpoint_file.exists():
            with open(self.checkpoint_file) as f:
                return json.load(f)
        return {'processed_archives': [], 'last_archive': None, 'last_update': None}

    def save_checkpoint(self):
        """Save processing checkpoint"""
        self.checkpoint['last_update'] = datetime.now().isoformat()
        self.checkpoint['stats'] = self.stats
        with open(self.checkpoint_file, 'w') as f:
            json.dump(self.checkpoint, f, indent=2)

    def run(self):
        """Main processing loop"""
        logger.info("="*80)
        logger.info("TED PRODUCTION PROCESSOR - ALL ARCHIVES (2006-2025)")
        logger.info("Complete European Validator v3.0 - 40 Languages")
        logger.info("="*80)

        # Find all monthly archives
        archives = sorted(self.source_dir.rglob("TED_monthly_*.tar.gz"))
        self.stats['archives_total'] = len(archives)

        logger.info(f"Found {len(archives)} TED monthly archives")
        logger.info(f"Previously processed: {len(self.checkpoint['processed_archives'])} archives")

        # Process each archive
        for archive_num, archive in enumerate(archives, 1):
            # Skip if already processed
            if str(archive) in self.checkpoint['processed_archives']:
                logger.info(f"[{archive_num}/{len(archives)}] SKIP (already processed): {archive.name}")
                continue

            self.stats['current_archive'] = archive.name
            logger.info(f"\n{'='*80}")
            logger.info(f"[{archive_num}/{len(archives)}] PROCESSING: {archive.name}")
            logger.info(f"{'='*80}")

            try:
                self.process_monthly_archive(archive)

                # Mark as processed
                self.checkpoint['processed_archives'].append(str(archive))
                self.stats['archives_processed'] += 1

                # Save checkpoint after each archive
                self.save_checkpoint()

            except Exception as e:
                error_msg = f"FAILED to process {archive.name}: {e}"
                logger.error(error_msg)
                logger.error(traceback.format_exc())
                self.stats['errors'].append(error_msg)

                # Save checkpoint even on error
                self.save_checkpoint()

        # Final summary
        self.print_summary()
        self.save_final_report()

    def process_monthly_archive(self, monthly_archive: Path):
        """Process a single monthly archive (outer tar.gz)"""
        logger.info(f"Extracting outer archive: {monthly_archive.name}")

        # Create temp directory for this archive
        archive_temp = self.temp_dir / monthly_archive.stem
        archive_temp.mkdir(parents=True, exist_ok=True)

        try:
            # Extract outer archive (with error handling for corrupted archives)
            try:
                with tarfile.open(monthly_archive, 'r:gz', errorlevel=1) as outer_tar:
                    # Extract with ignore_errors to handle partial corruption
                    outer_tar.extractall(archive_temp)
            except (EOFError, tarfile.ReadError, OSError) as e:
                logger.warning(f"Archive partially corrupted, attempting recovery: {e}")
                # Try to extract what we can
                try:
                    with tarfile.open(monthly_archive, 'r:gz', errorlevel=0) as outer_tar:
                        for member in outer_tar:
                            try:
                                outer_tar.extract(member, archive_temp)
                            except Exception:
                                logger.debug(f"Skipping corrupt member: {member.name}")
                                continue
                except Exception as e2:
                    raise Exception(f"Archive completely corrupted, skipping: {e2}")

            # Find inner archives (daily archives)
            inner_archives = list(archive_temp.rglob("*.tar.gz"))
            logger.info(f"Found {len(inner_archives)} inner (daily) archives")

            # Process each inner archive
            for inner_num, inner_archive in enumerate(inner_archives, 1):
                logger.info(f"  [{inner_num}/{len(inner_archives)}] Processing: {inner_archive.name}")

                try:
                    self.process_daily_archive(inner_archive, monthly_archive.name)
                    self.stats['inner_archives_processed'] += 1
                except Exception as e:
                    logger.error(f"    Failed to process inner archive: {e}")
                    self.stats['errors'].append(f"{monthly_archive.name}/{inner_archive.name}: {e}")

        finally:
            # Clean up temp directory
            import shutil
            if archive_temp.exists():
                shutil.rmtree(archive_temp, ignore_errors=True)

    def process_daily_archive(self, daily_archive: Path, monthly_name: str):
        """Process a single daily archive (inner tar.gz)"""
        daily_temp = daily_archive.parent / daily_archive.stem
        daily_temp.mkdir(parents=True, exist_ok=True)

        try:
            # Extract daily archive (with error handling)
            try:
                with tarfile.open(daily_archive, 'r:gz', errorlevel=1) as daily_tar:
                    daily_tar.extractall(daily_temp)
            except (EOFError, tarfile.ReadError, OSError) as e:
                logger.warning(f"    Daily archive corrupted, attempting recovery: {e}")
                try:
                    with tarfile.open(daily_archive, 'r:gz', errorlevel=0) as daily_tar:
                        for member in daily_tar:
                            try:
                                daily_tar.extract(member, daily_temp)
                            except Exception:
                                continue
                except Exception:
                    logger.error(f"    Daily archive completely corrupted, skipping")
                    return

            # Find XML files (recursively, as they may be in subdirectories)
            xml_files = list(daily_temp.rglob("*.xml"))
            logger.info(f"    Found {len(xml_files)} XML files")

            # Process XML files
            china_count = 0
            for xml_file in xml_files:
                try:
                    contract = self.process_xml_file(xml_file, monthly_name, daily_archive.name)
                    if contract and contract.get('is_chinese_related'):
                        china_count += 1
                        self.stats['china_contracts_found'] += 1

                    self.stats['xml_files_processed'] += 1

                    # Log progress every 1000 files
                    if self.stats['xml_files_processed'] % 1000 == 0:
                        logger.info(f"    Progress: {self.stats['xml_files_processed']} XML files processed, {self.stats['china_contracts_found']} China contracts found")

                except Exception as e:
                    logger.debug(f"      Error processing {xml_file.name}: {e}")

            if china_count > 0:
                logger.info(f"    ✓ Found {china_count} China-related contracts in this daily archive")

        finally:
            # Clean up daily temp
            import shutil
            if daily_temp.exists():
                shutil.rmtree(daily_temp, ignore_errors=True)

    def process_xml_file(self, xml_file: Path, monthly_name: str, daily_name: str) -> Optional[Dict]:
        """Process single XML file and extract contract data"""
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()

            # Extract contract data
            contract = self.extract_contract_data(root, xml_file.name, monthly_name, daily_name)

            if not contract:
                return None

            # Apply v3 validator
            validation_result = self.validate_china_involvement(contract)
            contract.update(validation_result)

            # Save to database (only if has meaningful data)
            if contract.get('notice_number') or contract.get('contract_title'):
                self.save_contract(contract)
                return contract

        except ET.ParseError:
            logger.debug(f"XML parse error: {xml_file.name}")
        except Exception as e:
            logger.debug(f"Error processing {xml_file.name}: {e}")

        return None

    def extract_contract_data(self, root: ET.Element, xml_filename: str, monthly_name: str, daily_name: str) -> Dict:
        """Extract structured data from TED XML"""

        # Generate unique document ID
        notice_id = self.get_text(root, './/NOTICE_NUMBER') or xml_filename
        doc_id = hashlib.sha256(f"{monthly_name}_{daily_name}_{xml_filename}_{notice_id}".encode()).hexdigest()[:16]

        contract = {
            'document_id': doc_id,
            'source_archive': monthly_name,
            'source_xml_file': f"{daily_name}/{xml_filename}",
            'processing_timestamp': datetime.now().isoformat(),
            'xml_hash': self.hash_xml(root),

            # Document identification
            'notice_number': self.get_text(root, './/NOTICE_NUMBER'),
            'publication_date': self.get_text(root, './/DATE_PUB'),
            'document_type': self.get_text(root, './/FORM_TYPE'),
            'form_type': root.tag,

            # Contracting authority
            'ca_name': self.get_text(root, './/CONTRACTING_AUTHORITY/NAME') or self.get_text(root, './/CA_NAME'),
            'ca_official_name': self.get_text(root, './/CONTRACTING_AUTHORITY/OFFICIALNAME'),
            'ca_address': self.get_text(root, './/CONTRACTING_AUTHORITY/ADDRESS'),
            'ca_city': self.get_text(root, './/CONTRACTING_AUTHORITY/TOWN'),
            'ca_postal_code': self.get_text(root, './/CONTRACTING_AUTHORITY/POSTAL_CODE'),
            'ca_country': self.get_text(root, './/CONTRACTING_AUTHORITY/COUNTRY'),
            'ca_type': self.get_text(root, './/CA_TYPE'),
            'ca_main_activity': self.get_text(root, './/CA_ACTIVITY'),

            # Contract information
            'contract_title': self.get_text(root, './/TITLE') or self.get_text(root, './/CONTRACT_TITLE'),
            'contract_description': self.get_text(root, './/SHORT_DESCR') or self.get_text(root, './/DESCRIPTION'),
            'contract_type': self.get_text(root, './/CONTRACT_TYPE'),
            'cpv_main': self.get_text(root, './/CPV_CODE[@PROCUREMENT_MAIN="yes"]'),
            'nuts_code': self.get_text(root, './/NUTS'),

            # Contract value
            'value_estimated': self.get_number(root, './/VAL_ESTIMATED'),
            'value_total': self.get_number(root, './/VAL_TOTAL'),
            'currency': self.get_text(root, './/CURRENCY') or 'EUR',

            # Award information
            'award_date': self.get_text(root, './/AWARD_DATE') or self.get_text(root, './/DATE_CONCLUSION_CONTRACT'),
            'number_tenders_received': self.get_number(root, './/NB_TENDERS_RECEIVED'),

            # Contractor information
            'contractor_name': self.get_text(root, './/CONTRACTOR/NAME') or self.get_text(root, './/ECONOMIC_OPERATOR/NAME'),
            'contractor_official_name': self.get_text(root, './/CONTRACTOR/OFFICIALNAME'),
            'contractor_address': self.get_text(root, './/CONTRACTOR/ADDRESS'),
            'contractor_city': self.get_text(root, './/CONTRACTOR/TOWN'),
            'contractor_postal_code': self.get_text(root, './/CONTRACTOR/POSTAL_CODE'),
            'contractor_country': self.get_text(root, './/CONTRACTOR/COUNTRY'),
            'contractor_sme': self.get_bool(root, './/SME'),

            # Procedure
            'procedure_type': self.get_text(root, './/PROCEDURE_TYPE'),
            'award_criteria': self.get_text(root, './/AWARD_CRITERIA'),
            'framework_agreement': self.get_bool(root, './/FRAMEWORK'),
            'gpa_covered': self.get_bool(root, './/GPA'),
        }

        # Extract additional contractors if present
        contractors = root.findall('.//CONTRACTOR') or root.findall('.//ECONOMIC_OPERATOR')
        if len(contractors) > 1:
            additional = []
            for contractor in contractors[1:]:
                additional.append({
                    'name': self.get_text(contractor, './/NAME'),
                    'country': self.get_text(contractor, './/COUNTRY'),
                    'city': self.get_text(contractor, './/TOWN')
                })
            contract['additional_contractors'] = json.dumps(additional)

        return contract

    def validate_china_involvement(self, contract: Dict) -> Dict:
        """Apply Complete European Validator v3.0"""

        # Combine all text fields for validation
        text_fields = [
            contract.get('contractor_name', ''),
            contract.get('contractor_official_name', ''),
            contract.get('contractor_address', ''),
            contract.get('contractor_city', ''),
            contract.get('ca_name', ''),
            contract.get('contract_title', ''),
            contract.get('contract_description', ''),
            contract.get('additional_contractors', '')
        ]
        combined_text = ' '.join(str(f) for f in text_fields if f).lower()

        # Check contractor country
        contractor_country = (contract.get('contractor_country') or '').upper()

        # Direct China match
        if contractor_country in ['CN', 'CHN', 'CHINA']:
            return {
                'is_chinese_related': True,
                'chinese_confidence': 1.0,
                'chinese_indicators': json.dumps(['contractor_country_CN']),
                'chinese_entities': json.dumps([contract.get('contractor_name', 'Unknown')])
            }

        # Simple pattern matching for China indicators
        china_patterns = [
            r'\bchina\b', r'\bchinese\b', r'\bbeijing\b', r'\bshanghai\b',
            r'\bguangzhou\b', r'\bshenzhen\b', r'\bhong kong\b', r'\bmacau\b',
            r'\bhuawei\b', r'\bzte\b', r'\balibaba\b', r'\btencent\b',
            r'\bsinopec\b', r'\bpetrochin', r'\blenovo\b', r'\bxiaomi\b',
            r'\bbyd\b', r'\bcosco\b', r'\bcnooc\b', r'\bcnpc\b'
        ]

        import re
        matches = []
        for pattern in china_patterns:
            if re.search(pattern, combined_text):
                matches.append(pattern)

        if matches:
            return {
                'is_chinese_related': True,
                'chinese_confidence': min(0.5 + (len(matches) * 0.1), 1.0),
                'chinese_indicators': json.dumps(matches),
                'chinese_entities': json.dumps([contract.get('contractor_name', 'Unknown')])
            }

        return {
            'is_chinese_related': False,
            'chinese_confidence': 0.0,
            'chinese_indicators': None,
            'chinese_entities': None
        }

    def save_contract(self, contract: Dict):
        """Save contract to database"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        # Use INSERT OR IGNORE to avoid duplicates
        placeholders = ', '.join(['?' for _ in contract.keys()])
        columns = ', '.join(contract.keys())

        try:
            cur.execute(f'''
                INSERT OR IGNORE INTO ted_contracts_production ({columns})
                VALUES ({placeholders})
            ''', list(contract.values()))
            conn.commit()
        except Exception as e:
            logger.error(f"Database insert error: {e}")
        finally:
            conn.close()

    def get_text(self, root: ET.Element, xpath: str) -> Optional[str]:
        """Get text from XML element"""
        elem = root.find(xpath)
        if elem is not None:
            text = elem.text or elem.get('VALUE') or elem.get('value')
            return str(text).strip() if text else None
        return None

    def get_number(self, root: ET.Element, xpath: str) -> Optional[float]:
        """Get numeric value from XML"""
        text = self.get_text(root, xpath)
        if text:
            try:
                return float(text.replace(',', ''))
            except:
                pass
        return None

    def get_bool(self, root: ET.Element, xpath: str) -> bool:
        """Get boolean from XML presence"""
        return root.find(xpath) is not None

    def hash_xml(self, root: ET.Element) -> str:
        """Generate hash of XML content"""
        xml_string = ET.tostring(root, encoding='unicode')
        return hashlib.sha256(xml_string.encode()).hexdigest()[:16]

    def print_summary(self):
        """Print processing summary"""
        logger.info("\n" + "="*80)
        logger.info("TED PRODUCTION PROCESSING COMPLETE")
        logger.info("="*80)
        logger.info(f"Archives processed: {self.stats['archives_processed']}/{self.stats['archives_total']}")
        logger.info(f"Inner archives processed: {self.stats['inner_archives_processed']}")
        logger.info(f"XML files processed: {self.stats['xml_files_processed']:,}")
        logger.info(f"China contracts found: {self.stats['china_contracts_found']:,}")
        logger.info(f"Errors: {len(self.stats['errors'])}")
        logger.info("="*80)

    def save_final_report(self):
        """Save final processing report"""
        report_path = Path("C:/Projects/OSINT - Foresight/analysis/TED_PRODUCTION_REPORT.json")
        report_path.parent.mkdir(parents=True, exist_ok=True)

        with open(report_path, 'w') as f:
            json.dump(self.stats, f, indent=2)

        logger.info(f"Final report saved: {report_path}")


def main():
    """Main entry point"""
    processor = TEDProductionProcessor()
    processor.run()


if __name__ == '__main__':
    main()

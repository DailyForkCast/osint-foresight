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
from core.data_quality_assessor import DataQualityAssessor

# Add UBL eForms parser for Era 3 (Feb 2024+)
sys.path.insert(0, str(Path(__file__).parent))
from ted_ubl_eforms_parser import UBLEFormsParser

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

        # TED XML namespace
        self.namespaces = {
            'ted': 'http://publications.europa.eu/TED_schema/Export',
            'ted_export': 'http://publications.europa.eu/TED_schema/Export',
            '': 'http://publications.europa.eu/TED_schema/Export'
        }

        # Initialize validator
        self.validator = CompleteEuropeanValidator()

        # Initialize data quality assessor
        self.quality_assessor = DataQualityAssessor()

        # Initialize UBL eForms parser (for Era 3: Feb 2024+)
        self.ubl_parser = UBLEFormsParser()

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
            'era_1_2_files': 0,
            'era_3_ubl_files': 0,
            'china_contracts_found': 0,
            'china_contracts_era_3': 0,
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

                -- Data quality tracking (NULL data handling)
                data_quality_flag TEXT,
                fields_with_data_count INTEGER,
                negative_signals TEXT,
                positive_signals TEXT,
                detection_rationale TEXT,

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
        cur.execute('CREATE INDEX IF NOT EXISTS idx_ted_prod_data_quality ON ted_contracts_production(data_quality_flag)')

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
            # STEP 1: Detect format (Era 1/2 vs Era 3)
            xml_format = self.detect_xml_format(xml_file)

            # STEP 2: Route to appropriate parser
            if xml_format == 'ERA_3_UBL_EFORMS':
                self.stats['era_3_ubl_files'] += 1
                contract = self.process_ubl_file(xml_file, monthly_name, daily_name)
            else:
                # Era 1/2 - use existing parser
                self.stats['era_1_2_files'] += 1
                tree = ET.parse(xml_file)
                root = tree.getroot()
                contract = self.extract_contract_data(root, xml_file.name, monthly_name, daily_name)

            if not contract:
                return None

            # Apply v3 validator
            validation_result = self.validate_china_involvement(contract)
            contract.update(validation_result)

            # Track Era 3 Chinese contracts separately
            if contract.get('is_chinese_related') and xml_format == 'ERA_3_UBL_EFORMS':
                self.stats['china_contracts_era_3'] += 1

            # Save to database (only if has meaningful data)
            if contract.get('notice_number') or contract.get('contract_title'):
                self.save_contract(contract)
                return contract

        except ET.ParseError:
            logger.debug(f"XML parse error: {xml_file.name}")
        except Exception as e:
            logger.debug(f"Error processing {xml_file.name}: {e}")

        return None

    def detect_xml_format(self, xml_file: Path) -> str:
        """
        Detect if XML is Era 1/2 (TED schema) or Era 3 (UBL eForms)

        Returns:
            'ERA_1_2_TED' or 'ERA_3_UBL_EFORMS'
        """
        try:
            # Read first few lines to check root element
            with open(xml_file, 'rb') as f:
                header = f.read(2000).decode('utf-8', errors='ignore')

            # Era 3 UBL eForms uses these root elements:
            # ContractAwardNotice, ContractNotice, CompetitionNotice, PlanningNotice
            # with UBL namespaces
            era_3_indicators = [
                'ContractAwardNotice',
                'ContractNotice',
                'CompetitionNotice',
                'PlanningNotice',
                'urn:oasis:names:specification:ubl:schema:xsd',
                'http://data.europa.eu/p27/eforms-ubl-extensions',
                'xmlns:cac=',
                'xmlns:cbc='
            ]

            # Era 1/2 uses TED namespace
            era_1_2_indicators = [
                'TED_EXPORT',
                'http://publications.europa.eu/TED_schema/Export',
                '<FORM_SECTION>',
                '<CODED_DATA_SECTION>'
            ]

            # Check for Era 3 indicators
            if any(indicator in header for indicator in era_3_indicators):
                return 'ERA_3_UBL_EFORMS'

            # Default to Era 1/2
            return 'ERA_1_2_TED'

        except Exception as e:
            logger.debug(f"Format detection error for {xml_file.name}: {e}")
            return 'ERA_1_2_TED'  # Default to old format

    def process_ubl_file(self, xml_file: Path, monthly_name: str, daily_name: str) -> Optional[Dict]:
        """Process Era 3 UBL eForms XML file using integrated parser"""
        try:
            # Parse with UBL parser
            notice_data = self.ubl_parser.parse_notice(xml_file)

            if not notice_data:
                return None

            # Convert to detection schema (same structure as Era 1/2)
            detection_record = self.ubl_parser.to_detection_schema(notice_data)

            # Convert to production database format
            contract = self.convert_ubl_to_production_format(
                detection_record,
                xml_file.name,
                monthly_name,
                daily_name
            )

            return contract

        except Exception as e:
            logger.debug(f"UBL parse error for {xml_file.name}: {e}")
            return None

    def convert_ubl_to_production_format(self, detection_record: Dict, xml_filename: str,
                                         monthly_name: str, daily_name: str) -> Dict:
        """Convert UBL detection schema to production database format"""

        # Generate unique document ID
        notice_id = detection_record.get('notice_number') or xml_filename
        doc_id = hashlib.sha256(f"{monthly_name}_{daily_name}_{xml_filename}_{notice_id}".encode()).hexdigest()[:16]

        # Extract first contractor (for flat fields)
        contractors = detection_record.get('contractors', [])
        first_contractor = contractors[0] if contractors else {}

        contract = {
            'document_id': doc_id,
            'source_archive': monthly_name,
            'source_xml_file': f"{daily_name}/{xml_filename}",
            'processing_timestamp': datetime.now().isoformat(),

            # Document identification
            'notice_number': detection_record.get('notice_number'),
            'publication_date': detection_record.get('notice_date'),
            'document_type': detection_record.get('notice_type'),
            'form_type': 'UBL_eForms_Era3',

            # Contracting authority
            'ca_name': detection_record.get('ca_name'),
            'ca_city': detection_record.get('ca_city'),
            'ca_country': detection_record.get('ca_country'),

            # Contract information
            'contract_title': detection_record.get('contract_title'),
            'contract_description': detection_record.get('contract_description'),
            'cpv_main': detection_record.get('cpv_code'),
            'nuts_code': first_contractor.get('nuts_code'),

            # Contract value
            'value_total': float(detection_record.get('award_value')) if detection_record.get('award_value') else None,
            'currency': detection_record.get('award_currency'),

            # Award information
            'award_date': detection_record.get('award_date'),
            'number_tenders_received': detection_record.get('contractor_count'),

            # Contractor information (first contractor)
            'contractor_name': first_contractor.get('name'),
            'contractor_city': first_contractor.get('city'),
            'contractor_postal_code': first_contractor.get('postal_code'),
            'contractor_country': first_contractor.get('country'),

            # Additional contractors (JSON)
            'additional_contractors': json.dumps(contractors[1:]) if len(contractors) > 1 else None,
        }

        return contract

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

        # Extract additional contractors if present (namespace-aware)
        contractors = root.findall('.//CONTRACTOR', self.namespaces)
        if not contractors:
            contractors = root.findall('.//ECONOMIC_OPERATOR', self.namespaces)
        if not contractors:
            # Fallback to non-namespaced (backward compatibility)
            contractors = root.findall('.//CONTRACTOR') or root.findall('.//ECONOMIC_OPERATOR')

        if contractors and len(contractors) > 1:
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
        """Apply Complete European Validator v3.0 + Data Quality Assessment"""

        # STEP 1: Data Quality Assessment (NULL data handling)
        # Prepare record for quality assessment
        quality_record = {
            'country': contract.get('contractor_country'),
            'city': contract.get('contractor_city'),
            'name': contract.get('contractor_name'),
            'address': contract.get('contractor_address')
        }

        key_fields = ['contractor_country', 'contractor_city', 'contractor_name', 'contractor_address', 'contractor_postal_code']

        # Assess data quality
        quality_assessment = self.quality_assessor.assess(quality_record, key_fields)

        # STEP 2: China Detection (only if not already confirmed by quality assessor)
        if quality_assessment.data_quality_flag == 'CHINESE_CONFIRMED':
            # Already confirmed Chinese by quality assessor
            return {
                'is_chinese_related': True,
                'chinese_confidence': 1.0,
                'chinese_indicators': json.dumps(quality_assessment.positive_signals) if quality_assessment.positive_signals else None,
                'chinese_entities': json.dumps([contract.get('contractor_name', 'Unknown')]),
                'data_quality_flag': quality_assessment.data_quality_flag,
                'fields_with_data_count': quality_assessment.fields_with_data_count,
                'negative_signals': json.dumps(quality_assessment.negative_signals),
                'positive_signals': json.dumps(quality_assessment.positive_signals),
                'detection_rationale': quality_assessment.rationale
            }

        elif quality_assessment.data_quality_flag == 'NON_CHINESE_CONFIRMED':
            # Confirmed non-Chinese by quality assessor - skip detection
            return {
                'is_chinese_related': False,
                'chinese_confidence': 0.0,
                'chinese_indicators': None,
                'chinese_entities': None,
                'data_quality_flag': quality_assessment.data_quality_flag,
                'fields_with_data_count': quality_assessment.fields_with_data_count,
                'negative_signals': json.dumps(quality_assessment.negative_signals),
                'positive_signals': json.dumps(quality_assessment.positive_signals),
                'detection_rationale': quality_assessment.rationale
            }

        # STEP 3: For NO_DATA / LOW_DATA / UNCERTAIN - try pattern matching
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

        # Simple pattern matching for China indicators
        china_patterns = [
            r'\bchina\b', r'\bchinese\b', r'\bbeijing\b', r'\bshanghai\b',
            r'\bguangzhou\b', r'\bshenzhen\b', r'\bhong kong\b', r'\bmacau\b',
            r'\bhuawei\b', r'\bzte\b', r'\balibaba\b', r'\btencent\b',
            r'\bsinopec\b', r'\bpetrochina\b', r'\blenovo\b', r'\bxiaomi\b',
            r'\bbyd\b', r'\bcosco\b', r'\bcnooc\b', r'\bcnpc\b', r'\bnuctech\b',
            r'\bhikvision\b', r'\bdahua\b', r'\bdji\b', r'\bbgi\b', r'\bcimc\b',
            r'\bcrrc\b', r'\bcomac\b', r'\bavic\b', r'\bnorinco\b', r'\bcasic\b'
        ]

        import re
        matches = []
        for pattern in china_patterns:
            if re.search(pattern, combined_text):
                matches.append(pattern)

        if matches:
            # Found Chinese patterns despite uncertain data quality
            return {
                'is_chinese_related': True,
                'chinese_confidence': min(0.5 + (len(matches) * 0.1), 1.0),
                'chinese_indicators': json.dumps(matches),
                'chinese_entities': json.dumps([contract.get('contractor_name', 'Unknown')]),
                'data_quality_flag': quality_assessment.data_quality_flag,  # Still mark quality flag
                'fields_with_data_count': quality_assessment.fields_with_data_count,
                'negative_signals': json.dumps(quality_assessment.negative_signals),
                'positive_signals': json.dumps(quality_assessment.positive_signals),
                'detection_rationale': f"{quality_assessment.rationale} | Pattern match: {len(matches)} indicators"
            }

        # No Chinese patterns found
        return {
            'is_chinese_related': False,
            'chinese_confidence': 0.0,
            'chinese_indicators': None,
            'chinese_entities': None,
            'data_quality_flag': quality_assessment.data_quality_flag,
            'fields_with_data_count': quality_assessment.fields_with_data_count,
            'negative_signals': json.dumps(quality_assessment.negative_signals),
            'positive_signals': json.dumps(quality_assessment.positive_signals),
            'detection_rationale': quality_assessment.rationale
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
        """Get text from XML element (namespace-aware)"""
        # Try with namespace first
        elem = root.find(xpath, self.namespaces)

        # If not found, try without namespace (backward compatibility)
        if elem is None:
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
        """Get boolean from XML presence (namespace-aware)"""
        elem = root.find(xpath, self.namespaces)
        if elem is None:
            elem = root.find(xpath)
        return elem is not None

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
        logger.info(f"  - Era 1/2 (TED schema): {self.stats['era_1_2_files']:,}")
        logger.info(f"  - Era 3 (UBL eForms): {self.stats['era_3_ubl_files']:,}")
        logger.info(f"China contracts found: {self.stats['china_contracts_found']:,}")
        logger.info(f"  - From Era 3 (UBL): {self.stats['china_contracts_era_3']:,}")
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

#!/usr/bin/env python3
"""
TED Enhanced eForms Processor
Handles BOTH old-format XML (2006-2022) AND new eForms UBL format (2023-2024)

Key Features:
- Dual-format support (legacy + eForms)
- Namespace-aware XML parsing
- Full contractor extraction (name, address, city, country)
- NULL data handling integration
- Chinese detection with enhanced substring matching
"""

import os
import sys
import sqlite3
import tarfile
import gzip
import io
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import json
import hashlib
import logging

# Add src to path for data quality assessor
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
from core.data_quality_assessor import DataQualityAssessor

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TEDEFormsProcessor:
    """Enhanced TED processor supporting both legacy and eForms formats"""

    # eForms namespaces (2023+)
    EFORMS_NAMESPACES = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2'
    }

    def __init__(self, db_path: str = "F:/OSINT_WAREHOUSE/osint_master.db"):
        self.db_path = Path(db_path)
        self.quality_assessor = DataQualityAssessor()
        self.checkpoint_file = Path("data/ted_eforms_checkpoint.json")
        self.processed_count = 0
        self.chinese_detected = 0

    def is_eforms_format(self, root: ET.Element) -> bool:
        """Detect if XML is eForms format (has UBL namespaces)"""
        # Check root tag for eForms indicators
        root_tag = root.tag
        return any(ns in root_tag for ns in ['ContractAwardNotice', 'ContractNotice', 'ubl'])

    def get_text_eforms(self, root: ET.Element, xpath: str, namespaces: dict = None) -> Optional[str]:
        """Get text from eForms XML with namespace support"""
        if namespaces is None:
            namespaces = self.EFORMS_NAMESPACES

        try:
            elem = root.find(xpath, namespaces)
            if elem is not None and elem.text:
                return elem.text.strip()
        except Exception:
            pass
        return None

    def get_text_legacy(self, root: ET.Element, xpath: str) -> Optional[str]:
        """Get text from legacy XML format"""
        try:
            elem = root.find(xpath)
            if elem is not None and elem.text:
                return elem.text.strip()
        except Exception:
            pass
        return None

    def extract_contractors_eforms(self, root: ET.Element) -> List[Dict]:
        """Extract all contractors from eForms UBL format"""
        contractors = []
        ns = self.EFORMS_NAMESPACES

        try:
            # Step 1: Find all TenderingParty elements
            tendering_parties = root.findall('.//efac:TenderingParty', ns)

            for party in tendering_parties:
                # Get party ID and name
                party_id = self.get_text_eforms(party, './cbc:ID', ns)
                party_name = self.get_text_eforms(party, './cbc:Name', ns)

                # Get Tenderer organization ID
                org_id = self.get_text_eforms(party, './/efac:Tenderer/cbc:ID', ns)

                if org_id:
                    # Step 2: Find the corresponding Organization in efac:Company (not cac:Party!)
                    organization = None
                    for company_elem in root.findall('.//efac:Company', ns):
                        company_id_elem = company_elem.find('./cac:PartyIdentification/cbc:ID[@schemeName="organization"]', ns)
                        if company_id_elem is not None and company_id_elem.text == org_id:
                            organization = company_elem
                            break

                    if organization is not None:
                        # Extract organization details
                        contractor = {
                            'contractor_name': party_name or self.get_text_eforms(organization, './/cac:PartyName/cbc:Name', ns),
                            'contractor_official_name': self.get_text_eforms(organization, './/cac:PartyName/cbc:Name', ns),
                            'contractor_address': self.get_text_eforms(organization, './/cac:PostalAddress/cbc:StreetName', ns),
                            'contractor_city': self.get_text_eforms(organization, './/cac:PostalAddress/cbc:CityName', ns),
                            'contractor_postal_code': self.get_text_eforms(organization, './/cac:PostalAddress/cbc:PostalZone', ns),
                            'contractor_country': self.get_text_eforms(organization, './/cac:PostalAddress/cac:Country/cbc:IdentificationCode', ns),
                            'contractor_id': self.get_text_eforms(organization, './/cac:PartyLegalEntity/cbc:CompanyID', ns)
                        }

                        # Only add if has at least name or ID
                        if contractor['contractor_name'] or contractor['contractor_id']:
                            contractors.append(contractor)

        except Exception as e:
            logger.warning(f"Error extracting eForms contractors: {e}")

        return contractors

    def extract_contractors_legacy(self, root: ET.Element) -> List[Dict]:
        """Extract contractors from legacy XML format (2006-2022)"""
        contractors = []

        # Try multiple legacy paths
        legacy_paths = [
            './/CONTRACTOR',
            './/ECONOMIC_OPERATOR',
            './/AWARDED_CONTRACT/CONTRACTOR',
            './/AWARDED_TO_GROUP/CONTRACTOR'
        ]

        for path in legacy_paths:
            for contractor_elem in root.findall(path):
                contractor = {
                    'contractor_name': self.get_text_legacy(contractor_elem, './NAME') or self.get_text_legacy(contractor_elem, './OFFICIALNAME'),
                    'contractor_official_name': self.get_text_legacy(contractor_elem, './OFFICIALNAME'),
                    'contractor_address': self.get_text_legacy(contractor_elem, './ADDRESS'),
                    'contractor_city': self.get_text_legacy(contractor_elem, './TOWN'),
                    'contractor_postal_code': self.get_text_legacy(contractor_elem, './POSTAL_CODE'),
                    'contractor_country': self.get_text_legacy(contractor_elem, './COUNTRY'),
                    'contractor_id': self.get_text_legacy(contractor_elem, './NATIONALID')
                }

                # Only add if has at least name
                if contractor['contractor_name']:
                    contractors.append(contractor)

        return contractors

    def extract_contract_data(self, root: ET.Element, xml_filename: str, monthly_name: str, daily_name: str) -> List[Dict]:
        """Extract contract data with dual-format support - returns list of contracts (one per contractor)"""

        # Detect format
        is_eforms = self.is_eforms_format(root)

        # Generate unique document ID
        notice_id = xml_filename
        doc_id = hashlib.sha256(f"{monthly_name}_{daily_name}_{xml_filename}".encode()).hexdigest()[:16]

        # Base contract information (common to all formats)
        base_contract = {
            'document_id': doc_id,
            'source_archive': monthly_name,
            'source_xml_file': f"{daily_name}/{xml_filename}",
            'processing_timestamp': datetime.now().isoformat(),
            'is_eforms': is_eforms
        }

        # Extract basic information based on format
        if is_eforms:
            ns = self.EFORMS_NAMESPACES
            base_contract.update({
                'notice_number': self.get_text_eforms(root, './/cbc:ID', ns),
                'publication_date': self.get_text_eforms(root, './/cbc:IssueDate', ns),
                'contract_title': self.get_text_eforms(root, './/cbc:Title', ns),
                'iso_country': self.get_text_eforms(root, './/cac:Country/cbc:IdentificationCode', ns),
                'ca_name': self.get_text_eforms(root, './/cac:ContractingParty/cac:Party/cac:PartyName/cbc:Name', ns)
            })
        else:
            base_contract.update({
                'notice_number': self.get_text_legacy(root, './/NOTICE_NUMBER'),
                'publication_date': self.get_text_legacy(root, './/DATE_PUB'),
                'contract_title': self.get_text_legacy(root, './/TITLE'),
                'iso_country': self.get_text_legacy(root, './/ISO_COUNTRY'),
                'ca_name': self.get_text_legacy(root, './/CONTRACTING_AUTHORITY/NAME')
            })

        # Extract contractors
        if is_eforms:
            contractors = self.extract_contractors_eforms(root)
        else:
            contractors = self.extract_contractors_legacy(root)

        # Create one contract record per contractor
        contracts = []
        if contractors:
            for contractor in contractors:
                contract = base_contract.copy()
                contract.update(contractor)
                contracts.append(contract)
        else:
            # No contractors found - save base contract with NULLs
            contract = base_contract.copy()
            contract.update({
                'contractor_name': None,
                'contractor_official_name': None,
                'contractor_address': None,
                'contractor_city': None,
                'contractor_postal_code': None,
                'contractor_country': None,
                'contractor_id': None
            })
            contracts.append(contract)

        return contracts

    def assess_contractor_quality(self, contract: Dict) -> Dict:
        """Assess data quality for contractor using enhanced detection"""

        quality_record = {
            'country': contract.get('contractor_country'),
            'city': contract.get('contractor_city'),
            'name': contract.get('contractor_name'),
            'address': contract.get('contractor_address')
        }

        key_fields = ['contractor_country', 'contractor_city', 'contractor_name', 'contractor_address']

        # Filter to only fields that have data
        actual_key_fields = [
            field.replace('contractor_', '')
            for field in key_fields
            if contract.get(field)
        ]

        assessment = self.quality_assessor.assess(quality_record, actual_key_fields if actual_key_fields else ['country'])

        return {
            'data_quality_flag': assessment.data_quality_flag,
            'fields_with_data_count': assessment.fields_with_data_count,
            'negative_signals': json.dumps(assessment.negative_signals),
            'positive_signals': json.dumps(assessment.positive_signals),
            'detection_rationale': assessment.rationale,
            'is_chinese_related': assessment.data_quality_flag == 'CHINESE_CONFIRMED',
            'chinese_confidence': assessment.confidence
        }

    def process_xml_file(self, xml_content: bytes, xml_filename: str, monthly_name: str, daily_name: str) -> int:
        """Process single XML file and return number of contracts inserted"""

        try:
            root = ET.fromstring(xml_content)
        except ET.ParseError as e:
            logger.warning(f"XML parse error in {xml_filename}: {e}")
            return 0

        # Extract contracts (one per contractor)
        contracts = self.extract_contract_data(root, xml_filename, monthly_name, daily_name)

        # Save to database
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        inserted = 0
        for contract in contracts:
            # Assess data quality
            quality = self.assess_contractor_quality(contract)
            contract.update(quality)

            # Check if already processed
            cur.execute("""
                SELECT id FROM ted_contracts_production
                WHERE document_id = ? AND contractor_name = ?
            """, (contract['document_id'], contract.get('contractor_name')))

            if cur.fetchone():
                continue  # Skip duplicate

            # Insert (using existing schema columns only)
            cur.execute("""
                INSERT INTO ted_contracts_production (
                    document_id, source_archive, source_xml_file, processing_timestamp,
                    notice_number, publication_date, contract_title, iso_country,
                    ca_name, contractor_name, contractor_address, contractor_country,
                    contractor_info,
                    data_quality_flag, fields_with_data_count,
                    negative_signals, positive_signals, detection_rationale,
                    is_chinese_related, chinese_confidence, chinese_indicators
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                contract['document_id'], contract['source_archive'], contract['source_xml_file'],
                contract['processing_timestamp'], contract.get('notice_number'),
                contract.get('publication_date'), contract.get('contract_title'),
                contract.get('iso_country'), contract.get('ca_name'),
                contract.get('contractor_name'), contract.get('contractor_address'),
                contract.get('contractor_country'),
                json.dumps({
                    'contractor_id': contract.get('contractor_id'),
                    'contractor_city': contract.get('contractor_city'),
                    'contractor_postal_code': contract.get('contractor_postal_code'),
                    'contractor_official_name': contract.get('contractor_official_name')
                }),
                quality['data_quality_flag'], quality['fields_with_data_count'],
                quality['negative_signals'], quality['positive_signals'],
                quality['detection_rationale'], quality['is_chinese_related'],
                quality['chinese_confidence'], quality.get('positive_signals', '[]')
            ))

            inserted += 1

            if quality['is_chinese_related']:
                self.chinese_detected += 1

        conn.commit()
        conn.close()

        self.processed_count += inserted
        return inserted

    def process_monthly_archive(self, archive_path: Path, year: int, month: int) -> Dict:
        """Process one monthly TED archive"""

        monthly_name = f"TED_monthly_{year}_{month:02d}.tar.gz"
        logger.info(f"Processing {monthly_name}")

        stats = {
            'monthly_name': monthly_name,
            'daily_archives': 0,
            'xml_files': 0,
            'contracts_inserted': 0,
            'chinese_found': 0,
            'errors': 0
        }

        try:
            with tarfile.open(archive_path, 'r:gz') as outer_tar:
                # Extract daily archives
                for member in outer_tar.getmembers():
                    if member.name.endswith('.tar.gz'):
                        stats['daily_archives'] += 1
                        daily_name = Path(member.name).stem

                        # Extract daily archive to memory
                        daily_tar_content = outer_tar.extractfile(member).read()

                        # Process XMLs in daily archive
                        try:
                            # Wrap bytes in BytesIO for gzip
                            daily_tar_file = io.BytesIO(daily_tar_content)
                            with tarfile.open(fileobj=gzip.GzipFile(fileobj=daily_tar_file), mode='r') as daily_tar:
                                for xml_member in daily_tar.getmembers():
                                    if xml_member.name.endswith('.xml') and not xml_member.name.startswith('error'):
                                        stats['xml_files'] += 1

                                        xml_content = daily_tar.extractfile(xml_member).read()
                                        xml_filename = Path(xml_member.name).name

                                        contracts_inserted = self.process_xml_file(
                                            xml_content, xml_filename, monthly_name, daily_name
                                        )

                                        stats['contracts_inserted'] += contracts_inserted

                                        if stats['xml_files'] % 1000 == 0:
                                            logger.info(f"  Processed {stats['xml_files']} XMLs, {stats['contracts_inserted']} contracts, {self.chinese_detected} Chinese")

                        except Exception as e:
                            logger.error(f"Error processing daily archive {daily_name}: {e}")
                            stats['errors'] += 1

        except Exception as e:
            logger.error(f"Error processing monthly archive: {e}")
            stats['errors'] += 1

        stats['chinese_found'] = self.chinese_detected
        logger.info(f"Completed {monthly_name}: {stats['contracts_inserted']} contracts, {self.chinese_detected} Chinese total")

        return stats

    def process_all_archives(self, ted_data_path: str = "F:/TED_Data/monthly", start_year: int = 2023, end_year: int = 2024):
        """Process all TED archives for specified year range"""

        logger.info("="*80)
        logger.info("TED ENHANCED eFORMS PROCESSOR")
        logger.info("="*80)
        logger.info(f"Processing years: {start_year}-{end_year}")
        logger.info(f"Database: {self.db_path}")

        ted_path = Path(ted_data_path)
        total_stats = {
            'archives_processed': 0,
            'total_contracts': 0,
            'total_chinese': 0,
            'errors': 0
        }

        for year in range(start_year, end_year + 1):
            year_path = ted_path / str(year)

            if not year_path.exists():
                logger.warning(f"Year directory not found: {year_path}")
                continue

            for month in range(1, 13):
                archive_name = f"TED_monthly_{year}_{month:02d}.tar.gz"
                archive_path = year_path / archive_name

                if not archive_path.exists():
                    continue

                stats = self.process_monthly_archive(archive_path, year, month)

                total_stats['archives_processed'] += 1
                total_stats['total_contracts'] += stats['contracts_inserted']
                total_stats['total_chinese'] += stats['chinese_found']
                total_stats['errors'] += stats['errors']

        logger.info("="*80)
        logger.info("PROCESSING COMPLETE")
        logger.info("="*80)
        logger.info(f"Archives processed: {total_stats['archives_processed']}")
        logger.info(f"Total contracts: {total_stats['total_contracts']:,}")
        logger.info(f"Chinese detected: {total_stats['total_chinese']:,}")
        logger.info(f"Errors: {total_stats['errors']}")

        return total_stats


if __name__ == '__main__':
    processor = TEDEFormsProcessor()

    # Process 2023-2024 (eForms format)
    stats = processor.process_all_archives(start_year=2023, end_year=2024)

    print("\n" + "="*80)
    print(f"[SUCCESS] Processed {stats['total_contracts']:,} contracts")
    print(f"[SUCCESS] Detected {stats['total_chinese']:,} Chinese-related contracts")
    print("="*80)

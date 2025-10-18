#!/usr/bin/env python3
"""
TED Comprehensive XML Parser
Extracts ALL data from TED XML files, handling multiple formats
"""

import tarfile
import gzip
import xml.etree.ElementTree as ET
import sqlite3
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import re
import hashlib

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TEDComprehensiveParser:
    """Comprehensive parser for all TED XML formats"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()
        self.stats = {
            'total_processed': 0,
            'successfully_parsed': 0,
            'parsing_errors': 0,
            'document_types': {},
            'contractors_found': 0,
            'chinese_entities': 0
        }

    def init_database(self):
        """Create comprehensive database schema"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        # Drop old table if exists
        cur.execute('DROP TABLE IF EXISTS ted_contracts_comprehensive')

        # Create new comprehensive table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS ted_contracts_comprehensive (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                -- Document identification
                document_id TEXT UNIQUE,
                notice_number TEXT,
                publication_date TEXT,
                document_type TEXT,
                form_type TEXT,

                -- Contracting authority
                ca_name TEXT,
                ca_official_name TEXT,
                ca_address TEXT,
                ca_city TEXT,
                ca_postal_code TEXT,
                ca_country TEXT,
                ca_contact_point TEXT,
                ca_telephone TEXT,
                ca_email TEXT,
                ca_url TEXT,
                ca_type TEXT,
                ca_main_activity TEXT,

                -- Contract information
                contract_title TEXT,
                contract_description TEXT,
                contract_type TEXT,
                contract_nature TEXT,
                cpv_main TEXT,
                cpv_additional TEXT,
                nuts_code TEXT,
                place_of_performance TEXT,

                -- Contract value
                value_estimated TEXT,
                value_total TEXT,
                value_min TEXT,
                value_max TEXT,
                currency TEXT,

                -- Award information (for award notices)
                award_date TEXT,
                number_tenders_received INTEGER,
                number_tenders_electronic INTEGER,

                -- Contractor information (primary)
                contractor_name TEXT,
                contractor_official_name TEXT,
                contractor_address TEXT,
                contractor_city TEXT,
                contractor_postal_code TEXT,
                contractor_country TEXT,
                contractor_nuts TEXT,
                contractor_telephone TEXT,
                contractor_email TEXT,
                contractor_url TEXT,
                contractor_sme BOOLEAN,

                -- Additional contractors (JSON array)
                additional_contractors TEXT,

                -- Consortium/Subcontractor information
                consortium_members TEXT,
                subcontractors TEXT,
                joint_procurement BOOLEAN,

                -- Procedure information
                procedure_type TEXT,
                award_criteria TEXT,
                submission_deadline TEXT,
                framework_agreement BOOLEAN,
                dynamic_purchasing BOOLEAN,
                electronic_auction BOOLEAN,
                gpa_covered BOOLEAN,

                -- Chinese detection fields
                is_chinese_related BOOLEAN DEFAULT 0,
                chinese_confidence REAL DEFAULT 0,
                chinese_indicators TEXT,
                chinese_entities TEXT,

                -- Metadata
                xml_file_path TEXT,
                processing_timestamp TEXT,
                raw_xml_hash TEXT
            )
        ''')

        # Create indices for performance
        cur.execute('CREATE INDEX IF NOT EXISTS idx_contractor_country ON ted_contracts_comprehensive(contractor_country)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_ca_country ON ted_contracts_comprehensive(ca_country)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_document_type ON ted_contracts_comprehensive(document_type)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_publication_date ON ted_contracts_comprehensive(publication_date)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_is_chinese ON ted_contracts_comprehensive(is_chinese_related)')

        conn.commit()
        conn.close()

    def parse_xml_file(self, xml_content: bytes, file_path: str) -> Optional[Dict[str, Any]]:
        """Parse a single XML file, handling multiple formats"""
        try:
            # Parse XML
            root = ET.fromstring(xml_content)

            # Detect format and extract accordingly
            root_tag = root.tag.split('}')[-1] if '}' in root.tag else root.tag

            if 'TED_EXPORT' in root_tag:
                return self.parse_ted_export(root, file_path, xml_content)
            elif 'ContractAwardNotice' in root_tag:
                return self.parse_contract_award_notice(root, file_path, xml_content)
            elif 'ContractNotice' in root_tag:
                return self.parse_contract_notice(root, file_path, xml_content)
            elif 'PriorInformationNotice' in root_tag:
                return self.parse_prior_information_notice(root, file_path, xml_content)
            else:
                logger.warning(f"Unknown XML format: {root_tag}")
                return None

        except Exception as e:
            logger.error(f"Error parsing {file_path}: {e}")
            self.stats['parsing_errors'] += 1
            return None

    def parse_ted_export(self, root: ET.Element, file_path: str, xml_content: bytes) -> Dict[str, Any]:
        """Parse TED_EXPORT format (most common)"""
        data = self.init_data_dict(file_path, xml_content)
        data['document_type'] = 'TED_EXPORT'

        # Define namespace
        ns = {}  # TED_EXPORT often doesn't use namespaces consistently

        # Extract document info
        doc_id = root.get('DOC_ID') or self.find_text(root, './/NOTICE_DATA/NO_DOC_OJS')
        data['document_id'] = doc_id or hashlib.md5(xml_content).hexdigest()

        # Get form type to determine notice type
        form_section = root.find('.//FORM_SECTION')
        if form_section is not None:
            for child in form_section:
                form_tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                data['form_type'] = form_tag

                # Parse based on form type
                if 'F02' in form_tag:
                    # Contract notice
                    self.parse_f02_contract_notice(child, data)
                elif 'F03' in form_tag:
                    # Contract award notice
                    self.parse_f03_award_notice(child, data)
                elif 'F01' in form_tag:
                    # Prior information notice
                    self.parse_f01_prior_notice(child, data)
                else:
                    # Generic parsing
                    self.parse_generic_form(child, data)

        # Extract coded data
        self.extract_coded_data(root, data)

        return data

    def parse_f03_award_notice(self, form: ET.Element, data: Dict[str, Any]):
        """Parse F03 Contract Award Notice"""
        data['document_type'] = 'Contract Award Notice'

        # Contracting authority
        ca = form.find('.//CONTRACTING_BODY') or form.find('.//CONTRACTING_AUTHORITY')
        if ca is not None:
            data['ca_official_name'] = self.find_text(ca, './/OFFICIALNAME')
            data['ca_country'] = self.find_text(ca, './/COUNTRY') or self.find_attr(ca, './/COUNTRY', 'VALUE')
            data['ca_city'] = self.find_text(ca, './/TOWN')
            data['ca_postal_code'] = self.find_text(ca, './/POSTAL_CODE')
            data['ca_email'] = self.find_text(ca, './/E_MAIL')
            data['ca_url'] = self.find_text(ca, './/URL')
            data['ca_type'] = self.find_attr(ca, './/CA_TYPE', 'VALUE')

        # Object of contract
        obj = form.find('.//OBJECT_CONTRACT')
        if obj is not None:
            data['contract_title'] = self.find_text(obj, './/TITLE')
            data['contract_description'] = self.find_text(obj, './/SHORT_DESCR')
            data['cpv_main'] = self.find_attr(obj, './/CPV_MAIN/CPV_CODE', 'CODE')
            data['nuts_code'] = self.find_attr(obj, './/NUTS', 'CODE')
            data['place_of_performance'] = self.find_text(obj, './/MAIN_SITE')

            # Contract value
            data['value_total'] = self.find_text(obj, './/VAL_TOTAL')
            data['value_estimated'] = self.find_text(obj, './/VAL_ESTIMATED')
            data['currency'] = self.find_attr(obj, './/VAL_TOTAL', 'CURRENCY') or self.find_attr(obj, './/VALUES', 'CURRENCY')

        # Award information - THIS IS THE CRITICAL PART
        award_sections = form.findall('.//AWARD_CONTRACT') or form.findall('.//AWARDED_CONTRACT')
        contractors = []

        for award in award_sections:
            # Get award details
            award_date = self.find_text(award, './/DATE_CONCLUSION_CONTRACT')
            if award_date:
                data['award_date'] = award_date

            # Get contractor information
            contractor_elements = award.findall('.//CONTRACTOR') or award.findall('.//ECONOMIC_OPERATOR')

            for contractor_elem in contractor_elements:
                contractor_info = {
                    'name': self.find_text(contractor_elem, './/OFFICIALNAME'),
                    'address': self.find_text(contractor_elem, './/ADDRESS'),
                    'city': self.find_text(contractor_elem, './/TOWN'),
                    'postal_code': self.find_text(contractor_elem, './/POSTAL_CODE'),
                    'country': self.find_text(contractor_elem, './/COUNTRY') or self.find_attr(contractor_elem, './/COUNTRY', 'VALUE'),
                    'nuts': self.find_attr(contractor_elem, './/NUTS', 'CODE'),
                    'email': self.find_text(contractor_elem, './/E_MAIL'),
                    'phone': self.find_text(contractor_elem, './/PHONE'),
                    'url': self.find_text(contractor_elem, './/URL'),
                    'sme': self.find_text(contractor_elem, './/SME') == 'YES'
                }

                # Filter out empty contractors
                if contractor_info['name'] or contractor_info['country']:
                    contractors.append(contractor_info)

                    # Check for Chinese indicators
                    self.check_chinese_indicators(contractor_info, data)

        # Store contractors
        if contractors:
            # Primary contractor
            primary = contractors[0]
            data['contractor_name'] = primary['name']
            data['contractor_official_name'] = primary['name']
            data['contractor_address'] = primary['address']
            data['contractor_city'] = primary['city']
            data['contractor_postal_code'] = primary['postal_code']
            data['contractor_country'] = primary['country']
            data['contractor_nuts'] = primary['nuts']
            data['contractor_email'] = primary['email']
            data['contractor_telephone'] = primary['phone']
            data['contractor_url'] = primary['url']
            data['contractor_sme'] = primary['sme']

            # Additional contractors
            if len(contractors) > 1:
                data['additional_contractors'] = json.dumps(contractors[1:])

            self.stats['contractors_found'] += len(contractors)

    def parse_f02_contract_notice(self, form: ET.Element, data: Dict[str, Any]):
        """Parse F02 Contract Notice (call for tender)"""
        data['document_type'] = 'Contract Notice'

        # Similar structure to F03 but without contractor info
        ca = form.find('.//CONTRACTING_BODY') or form.find('.//CONTRACTING_AUTHORITY')
        if ca is not None:
            data['ca_official_name'] = self.find_text(ca, './/OFFICIALNAME')
            data['ca_country'] = self.find_text(ca, './/COUNTRY') or self.find_attr(ca, './/COUNTRY', 'VALUE')
            data['ca_city'] = self.find_text(ca, './/TOWN')

        # Object of contract
        obj = form.find('.//OBJECT_CONTRACT')
        if obj is not None:
            data['contract_title'] = self.find_text(obj, './/TITLE')
            data['contract_description'] = self.find_text(obj, './/SHORT_DESCR')
            data['cpv_main'] = self.find_attr(obj, './/CPV_MAIN/CPV_CODE', 'CODE')
            data['value_estimated'] = self.find_text(obj, './/VAL_ESTIMATED')

        # Procedure info
        proc = form.find('.//PROCEDURE')
        if proc is not None:
            data['procedure_type'] = self.find_attr(proc, './/PT_OPEN', 'VALUE') or self.find_text(proc, './/TYPE_PROCEDURE')
            data['submission_deadline'] = self.find_text(proc, './/DATE_RECEIPT_TENDERS')

    def parse_f01_prior_notice(self, form: ET.Element, data: Dict[str, Any]):
        """Parse F01 Prior Information Notice"""
        data['document_type'] = 'Prior Information Notice'

        # Extract basic information
        ca = form.find('.//CONTRACTING_BODY')
        if ca is not None:
            data['ca_official_name'] = self.find_text(ca, './/OFFICIALNAME')
            data['ca_country'] = self.find_text(ca, './/COUNTRY') or self.find_attr(ca, './/COUNTRY', 'VALUE')

    def parse_contract_award_notice(self, root: ET.Element, file_path: str, xml_content: bytes) -> Dict[str, Any]:
        """Parse UBL ContractAwardNotice format"""
        data = self.init_data_dict(file_path, xml_content)
        data['document_type'] = 'UBL Contract Award Notice'

        # Define UBL namespaces
        ns = {
            'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
            'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
            'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2'
        }

        # Document ID
        data['document_id'] = self.find_text(root, './/cbc:ID', ns) or hashlib.md5(xml_content).hexdigest()
        data['publication_date'] = self.find_text(root, './/cbc:IssueDate', ns)

        # Contracting party
        ca = root.find('.//cac:ContractingParty', ns)
        if ca is not None:
            party = ca.find('.//cac:Party', ns)
            if party is not None:
                data['ca_official_name'] = self.find_text(party, './/cac:PartyName/cbc:Name', ns)
                data['ca_country'] = self.find_text(party, './/cac:PostalAddress/cac:Country/cbc:IdentificationCode', ns)
                data['ca_city'] = self.find_text(party, './/cac:PostalAddress/cbc:CityName', ns)

        # Tendered project
        project = root.find('.//cac:ProcurementProject', ns)
        if project is not None:
            data['contract_title'] = self.find_text(project, './/cbc:Name', ns)
            data['contract_description'] = self.find_text(project, './/cbc:Description', ns)

        # Winning party (contractor)
        winning_parties = root.findall('.//cac:TenderResult/cac:WinningParty', ns)
        contractors = []

        for winning in winning_parties:
            party = winning.find('.//cac:Party', ns)
            if party is not None:
                contractor_info = {
                    'name': self.find_text(party, './/cac:PartyName/cbc:Name', ns),
                    'country': self.find_text(party, './/cac:PostalAddress/cac:Country/cbc:IdentificationCode', ns),
                    'city': self.find_text(party, './/cac:PostalAddress/cbc:CityName', ns),
                    'postal_code': self.find_text(party, './/cac:PostalAddress/cbc:PostalZone', ns)
                }

                if contractor_info['name']:
                    contractors.append(contractor_info)
                    self.check_chinese_indicators(contractor_info, data)

        # Store contractor info
        if contractors:
            primary = contractors[0]
            data['contractor_name'] = primary['name']
            data['contractor_country'] = primary['country']
            data['contractor_city'] = primary['city']

            if len(contractors) > 1:
                data['additional_contractors'] = json.dumps(contractors[1:])

            self.stats['contractors_found'] += len(contractors)

        return data

    def parse_contract_notice(self, root: ET.Element, file_path: str, xml_content: bytes) -> Dict[str, Any]:
        """Parse UBL ContractNotice format"""
        data = self.init_data_dict(file_path, xml_content)
        data['document_type'] = 'UBL Contract Notice'

        # Similar structure to award notice but without winning party
        ns = {
            'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
            'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
        }

        data['document_id'] = self.find_text(root, './/cbc:ID', ns) or hashlib.md5(xml_content).hexdigest()
        data['publication_date'] = self.find_text(root, './/cbc:IssueDate', ns)

        # Extract contracting party and project info
        ca = root.find('.//cac:ContractingParty', ns)
        if ca is not None:
            party = ca.find('.//cac:Party', ns)
            if party is not None:
                data['ca_official_name'] = self.find_text(party, './/cac:PartyName/cbc:Name', ns)
                data['ca_country'] = self.find_text(party, './/cac:PostalAddress/cac:Country/cbc:IdentificationCode', ns)

        return data

    def parse_prior_information_notice(self, root: ET.Element, file_path: str, xml_content: bytes) -> Dict[str, Any]:
        """Parse UBL PriorInformationNotice format"""
        data = self.init_data_dict(file_path, xml_content)
        data['document_type'] = 'UBL Prior Information Notice'

        # Basic extraction for prior notices
        ns = {
            'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
            'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
        }

        data['document_id'] = self.find_text(root, './/cbc:ID', ns) or hashlib.md5(xml_content).hexdigest()

        return data

    def parse_generic_form(self, form: ET.Element, data: Dict[str, Any]):
        """Generic parsing for unknown form types"""
        # Try to extract basic fields
        data['ca_official_name'] = self.find_text(form, './/OFFICIALNAME')
        data['contract_title'] = self.find_text(form, './/TITLE')
        data['contract_description'] = self.find_text(form, './/SHORT_DESCR')

        # Look for any contractor information
        contractors = form.findall('.//CONTRACTOR')
        if contractors:
            contractor = contractors[0]
            data['contractor_name'] = self.find_text(contractor, './/OFFICIALNAME')
            data['contractor_country'] = self.find_text(contractor, './/COUNTRY') or self.find_attr(contractor, './/COUNTRY', 'VALUE')

    def extract_coded_data(self, root: ET.Element, data: Dict[str, Any]):
        """Extract coded/metadata section"""
        coded = root.find('.//CODED_DATA_SECTION') or root.find('.//CODIF_DATA')
        if coded is not None:
            data['notice_number'] = self.find_text(coded, './/NO_DOC_OJS')

            # Try to get publication date
            date_pub = self.find_text(coded, './/DATE_PUB')
            if date_pub:
                data['publication_date'] = date_pub

    def check_chinese_indicators(self, contractor_info: Dict[str, Any], data: Dict[str, Any]):
        """Check for Chinese indicators in contractor information"""
        chinese_indicators = []

        # Country code check
        country = contractor_info.get('country', '')
        if country in ['CN', 'CHN', 'HK', 'MO']:
            chinese_indicators.append(f'Country code: {country}')
            data['is_chinese_related'] = True
            data['chinese_confidence'] = 1.0

        # Name checks
        name = contractor_info.get('name', '')
        if name:
            chinese_terms = ['China', 'Chinese', 'Beijing', 'Shanghai', 'Shenzhen',
                           'Guangzhou', 'Huawei', 'ZTE', 'Alibaba', 'Tencent',
                           'Xiaomi', 'Lenovo', 'BYD', 'DJI', 'Hikvision']

            for term in chinese_terms:
                if term.lower() in name.lower():
                    chinese_indicators.append(f'Name contains: {term}')
                    data['is_chinese_related'] = True
                    data['chinese_confidence'] = max(data.get('chinese_confidence', 0), 0.8)

        if chinese_indicators:
            data['chinese_indicators'] = json.dumps(chinese_indicators)

            # Add to Chinese entities list
            chinese_entities = json.loads(data.get('chinese_entities', '[]'))
            chinese_entities.append({
                'name': name,
                'country': country,
                'indicators': chinese_indicators
            })
            data['chinese_entities'] = json.dumps(chinese_entities)

            self.stats['chinese_entities'] += 1

    def init_data_dict(self, file_path: str, xml_content: bytes) -> Dict[str, Any]:
        """Initialize data dictionary with defaults"""
        return {
            'xml_file_path': file_path,
            'processing_timestamp': datetime.now().isoformat(),
            'raw_xml_hash': hashlib.md5(xml_content).hexdigest(),
            'chinese_entities': '[]'
        }

    def find_text(self, elem: ET.Element, path: str, ns: dict = None) -> Optional[str]:
        """Safely find and extract text from element"""
        if elem is None:
            return None
        found = elem.find(path, ns) if ns else elem.find(path)
        return found.text if found is not None else None

    def find_attr(self, elem: ET.Element, path: str, attr: str, ns: dict = None) -> Optional[str]:
        """Safely find and extract attribute from element"""
        if elem is None:
            return None
        found = elem.find(path, ns) if ns else elem.find(path)
        return found.get(attr) if found is not None else None

    def process_tar_file(self, tar_path: str):
        """Process a tar.gz file containing TED data"""
        logger.info(f"Processing {tar_path}")

        try:
            with tarfile.open(tar_path, 'r:gz') as tar:
                # Check if it's a monthly file with daily tars
                tar_files = [f for f in tar.getnames() if f.endswith('.tar.gz')]
                xml_files = [f for f in tar.getnames() if f.endswith('.xml')]

                if tar_files:
                    # Process nested daily tars
                    for daily_tar in tar_files[:5]:  # Process first 5 days for testing
                        logger.info(f"  Processing daily tar: {daily_tar}")
                        daily_obj = tar.extractfile(daily_tar)
                        if daily_obj:
                            self.process_daily_tar(daily_obj)
                else:
                    # Process XML files directly
                    for xml_file in xml_files[:100]:  # Process first 100 for testing
                        xml_obj = tar.extractfile(xml_file)
                        if xml_obj:
                            self.process_xml(xml_obj.read(), xml_file)

        except Exception as e:
            logger.error(f"Error processing tar file {tar_path}: {e}")

    def process_daily_tar(self, daily_tar_obj):
        """Process a daily tar file"""
        try:
            with tarfile.open(fileobj=daily_tar_obj, mode='r:gz') as daily_tar:
                xml_files = [f for f in daily_tar.getnames() if f.endswith('.xml')]

                for xml_file in xml_files[:100]:  # Process first 100 XMLs
                    try:
                        xml_obj = daily_tar.extractfile(xml_file)
                        if xml_obj:
                            self.process_xml(xml_obj.read(), xml_file)
                    except Exception as e:
                        logger.warning(f"Error processing XML {xml_file}: {e}")

        except Exception as e:
            logger.error(f"Error processing daily tar: {e}")

    def process_xml(self, xml_content: bytes, file_path: str):
        """Process a single XML file"""
        self.stats['total_processed'] += 1

        # Parse XML
        data = self.parse_xml_file(xml_content, file_path)

        if data:
            # Save to database
            self.save_to_database(data)
            self.stats['successfully_parsed'] += 1

            # Update document type stats
            doc_type = data.get('document_type', 'Unknown')
            if doc_type not in self.stats['document_types']:
                self.stats['document_types'][doc_type] = 0
            self.stats['document_types'][doc_type] += 1

            # Log progress
            if self.stats['total_processed'] % 100 == 0:
                logger.info(f"Progress: {self.stats['total_processed']} processed, "
                          f"{self.stats['successfully_parsed']} successful, "
                          f"{self.stats['contractors_found']} contractors found, "
                          f"{self.stats['chinese_entities']} Chinese entities")

    def save_to_database(self, data: Dict[str, Any]):
        """Save parsed data to database"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        # Prepare column names and values
        columns = []
        values = []

        for key, value in data.items():
            columns.append(key)
            values.append(value)

        # Create insert query
        placeholders = ','.join(['?' for _ in values])
        columns_str = ','.join(columns)

        query = f"INSERT OR REPLACE INTO ted_contracts_comprehensive ({columns_str}) VALUES ({placeholders})"

        try:
            cur.execute(query, values)
            conn.commit()
        except Exception as e:
            logger.error(f"Database error: {e}")
            logger.debug(f"Query: {query}")
            logger.debug(f"Values: {values}")
        finally:
            conn.close()

    def generate_report(self):
        """Generate processing report"""
        print("\n" + "="*80)
        print("TED COMPREHENSIVE PARSING REPORT")
        print("="*80)
        print(f"\nTotal XML files processed: {self.stats['total_processed']:,}")
        print(f"Successfully parsed: {self.stats['successfully_parsed']:,}")
        print(f"Parsing errors: {self.stats['parsing_errors']:,}")
        print(f"Success rate: {self.stats['successfully_parsed']/max(1,self.stats['total_processed'])*100:.1f}%")

        print(f"\nContractors found: {self.stats['contractors_found']:,}")
        print(f"Chinese entities detected: {self.stats['chinese_entities']:,}")

        print("\nDocument types processed:")
        for doc_type, count in sorted(self.stats['document_types'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {doc_type}: {count:,}")

        # Database statistics
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) FROM ted_contracts_comprehensive WHERE contractor_name IS NOT NULL")
        with_contractor = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM ted_contracts_comprehensive WHERE is_chinese_related = 1")
        chinese_related = cur.fetchone()[0]

        cur.execute("SELECT COUNT(DISTINCT contractor_country) FROM ted_contracts_comprehensive WHERE contractor_country IS NOT NULL")
        countries = cur.fetchone()[0]

        print(f"\nDatabase Statistics:")
        print(f"  Records with contractors: {with_contractor:,}")
        print(f"  Chinese-related records: {chinese_related:,}")
        print(f"  Countries represented: {countries}")

        conn.close()

        return self.stats


def main():
    """Main execution function"""
    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"

    parser = TEDComprehensiveParser(db_path)

    # Process January 2024 data
    tar_path = "F:/TED_Data/monthly/2024/TED_monthly_2024_01.tar.gz"

    logger.info("Starting comprehensive TED data extraction...")
    parser.process_tar_file(tar_path)

    # Generate report
    stats = parser.generate_report()

    # Save stats to file
    with open("C:/Projects/OSINT - Foresight/analysis/ted_comprehensive_stats.json", 'w') as f:
        json.dump(stats, f, indent=2)

    logger.info("Processing complete!")

    return stats


if __name__ == "__main__":
    main()

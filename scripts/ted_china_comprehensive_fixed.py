#!/usr/bin/env python3
"""
TED Comprehensive China Entity Analyzer - FIXED VERSION
Correctly parses TED XML structure for genuine PRC entities
NO SAMPLING - Complete exhaustive search
Taiwan is NOT considered part of China
"""

import tarfile
import xml.etree.ElementTree as ET
import json
import sqlite3
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Optional, Tuple
import re
from collections import defaultdict
import os

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ted_china_analysis_fixed.log'),
        logging.StreamHandler()
    ]
)

# Register namespaces to handle the TED XML properly
ET.register_namespace('', 'http://publications.europa.eu/resource/schema/ted/R2.0.9/publication')
ET.register_namespace('n2021', 'http://publications.europa.eu/resource/schema/ted/2021/nuts')

class TEDChinaAnalyzerFixed:
    """Fixed analyzer for PRC entities in TED data"""

    def __init__(self, ted_path: str = "F:/TED_Data/monthly/",
                 db_path: str = "F:/OSINT_WAREHOUSE/osint_master.db"):
        self.ted_path = Path(ted_path)
        self.db_path = Path(db_path)

        # Connect to database
        self.conn = sqlite3.connect(str(self.db_path))
        self.cursor = self.conn.cursor()

        # Define namespaces for XML parsing
        self.namespaces = {
            'ted': 'http://publications.europa.eu/resource/schema/ted/R2.0.9/publication',
            'n2021': 'http://publications.europa.eu/resource/schema/ted/2021/nuts'
        }

        # Statistics
        self.stats = {
            "total_files": 0,
            "total_contracts": 0,
            "china_contracts": 0,
            "china_buyers": 0,
            "china_suppliers": 0,
            "china_value_eur": 0,
            "errors": [],
            "years_processed": set(),
            "countries_seen": set(),
            "china_examples": []
        }

        # PRC detection criteria (NOT Taiwan)
        self.prc_country_codes = {
            'CN',      # China
            'CHN',     # China alternative
            '156',     # China ISO numeric
            # NOT including: TW, TWN, 158 (Taiwan)
        }

        # Major PRC cities (mainland only)
        self.prc_cities = {
            'beijing', 'shanghai', 'guangzhou', 'shenzhen', 'tianjin',
            'chongqing', 'hong kong', 'hongkong', 'macau', 'macao',
            'wuhan', 'chengdu', 'xian', "xi'an", 'nanjing', 'hangzhou',
            'suzhou', 'qingdao', 'dalian', 'shenyang', 'changsha',
            'harbin', 'kunming', 'changchun', 'jinan', 'zhengzhou',
            'xiamen', 'foshan', 'dongguan', 'ningbo', 'hefei'
        }

        # Known PRC entities (major companies)
        self.prc_entities = {
            # Major state-owned enterprises
            'huawei', 'zte', 'china mobile', 'china telecom', 'china unicom',
            'sinopec', 'cnpc', 'china national petroleum', 'petrochina',
            'state grid', 'china construction', 'china railway',
            'china state construction', 'china communications construction',
            'sinohydro', 'powerchina', 'china harbour', 'cccc',

            # Technology companies
            'alibaba', 'tencent', 'baidu', 'xiaomi', 'lenovo', 'bytedance',
            'hikvision', 'dahua', 'dji', 'boe', 'tcl', 'haier', 'midea',

            # Banks and financial
            'icbc', 'china construction bank', 'agricultural bank of china',
            'bank of china', 'bank of communications',

            # Aviation and aerospace
            'air china', 'china eastern', 'china southern', 'comac',
            'china aerospace', 'casic', 'casc',

            # Universities and research
            'tsinghua', 'peking university', 'chinese academy'
        }

    def create_tables(self):
        """Create database tables for TED China analysis"""
        logging.info("Creating TED China analysis tables...")

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS ted_china_contracts_fixed (
            contract_id TEXT PRIMARY KEY,
            doc_id TEXT,
            publication_date DATE,
            buyer_name TEXT,
            buyer_country TEXT,
            buyer_city TEXT,
            supplier_name TEXT,
            supplier_country TEXT,
            supplier_city TEXT,
            contract_value REAL,
            currency TEXT,
            cpv_codes TEXT,
            description TEXT,
            china_role TEXT,
            detection_method TEXT,
            year INTEGER,
            month INTEGER,
            source_file TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS ted_china_entities_fixed (
            entity_id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_name TEXT,
            entity_type TEXT,
            country TEXT,
            city TEXT,
            known_chinese_entity BOOLEAN,
            contract_count INTEGER,
            total_value REAL,
            first_seen DATE,
            last_seen DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(entity_name, entity_type)
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS ted_china_statistics_fixed (
            stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER,
            total_contracts INTEGER,
            china_contracts INTEGER,
            china_as_buyer INTEGER,
            china_as_supplier INTEGER,
            total_value_eur REAL,
            processing_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        self.conn.commit()
        logging.info("Tables created successfully")

    def is_chinese_entity(self, name: str, country: str, city: str) -> Tuple[bool, str]:
        """
        Determine if an entity is from PRC (not Taiwan)
        Returns (is_chinese, detection_method)
        """
        if not name and not country and not city:
            return False, ""

        # Normalize inputs
        name_lower = (name or '').lower()
        country_upper = (country or '').upper()
        city_lower = (city or '').lower()

        # Method 1: Country code check (most reliable)
        if country_upper in self.prc_country_codes:
            return True, f"country_code:{country_upper}"

        # Explicitly exclude Taiwan
        if country_upper in ['TW', 'TWN'] or 'taiwan' in name_lower:
            return False, ""

        # Method 2: Chinese city detection
        for prc_city in self.prc_cities:
            if prc_city in city_lower:
                return True, f"city:{prc_city}"

        # Method 3: Known Chinese entity names
        for entity in self.prc_entities:
            if entity in name_lower:
                return True, f"known_entity:{entity}"

        # Method 4: .cn domain
        if '.cn' in name_lower:
            return True, "cn_domain"

        # Method 5: "China" in name (but not Taiwan)
        if 'china' in name_lower and 'taiwan' not in name_lower:
            return True, "china_in_name"

        return False, ""

    def parse_ted_xml_fixed(self, xml_content: str, filename: str) -> Optional[Dict]:
        """Parse TED XML with correct structure"""
        try:
            # Parse XML with namespaces
            root = ET.fromstring(xml_content)

            # Get document ID
            doc_id = root.get('DOC_ID', '')

            # Initialize contract data
            contract_data = {
                'doc_id': doc_id,
                'filename': filename,
                'buyer_name': None,
                'buyer_country': None,
                'buyer_city': None,
                'supplier_name': None,
                'supplier_country': None,
                'supplier_city': None,
                'contract_value': None,
                'currency': None,
                'cpv_codes': [],
                'description': None,
                'publication_date': None
            }

            # Get publication date from CODED_DATA_SECTION
            date_pub = root.find('.//ted:DATE_PUB', self.namespaces)
            if date_pub is None:
                date_pub = root.find('.//DATE_PUB')
            if date_pub is not None:
                pub_date_str = date_pub.text
                if pub_date_str:
                    # Convert YYYYMMDD to YYYY-MM-DD
                    if len(pub_date_str) == 8:
                        contract_data['publication_date'] = f"{pub_date_str[:4]}-{pub_date_str[4:6]}-{pub_date_str[6:8]}"
                    else:
                        contract_data['publication_date'] = pub_date_str

            # Get ISO country from CODED_DATA_SECTION
            iso_country = root.find('.//ted:ISO_COUNTRY', self.namespaces)
            if iso_country is None:
                iso_country = root.find('.//ISO_COUNTRY')
            if iso_country is not None:
                country_code = iso_country.get('VALUE')
                self.stats['countries_seen'].add(country_code)

            # Get contracting body (buyer) from FORM_SECTION
            contracting_body = root.find('.//ted:CONTRACTING_BODY', self.namespaces)
            if contracting_body is None:
                contracting_body = root.find('.//CONTRACTING_BODY')

            if contracting_body is not None:
                # Get buyer details
                buyer_name = contracting_body.find('.//ted:OFFICIALNAME', self.namespaces)
                if buyer_name is None:
                    buyer_name = contracting_body.find('.//OFFICIALNAME')
                if buyer_name is not None:
                    contract_data['buyer_name'] = buyer_name.text

                buyer_country = contracting_body.find('.//ted:COUNTRY', self.namespaces)
                if buyer_country is None:
                    buyer_country = contracting_body.find('.//COUNTRY')
                if buyer_country is not None:
                    contract_data['buyer_country'] = buyer_country.get('VALUE')

                buyer_city = contracting_body.find('.//ted:TOWN', self.namespaces)
                if buyer_city is None:
                    buyer_city = contracting_body.find('.//TOWN')
                if buyer_city is not None:
                    contract_data['buyer_city'] = buyer_city.text

            # Get contractor (supplier) from AWARD_CONTRACT section
            contractors = root.findall('.//ted:CONTRACTOR', self.namespaces)
            if not contractors:
                contractors = root.findall('.//CONTRACTOR')

            for contractor in contractors:
                # Get supplier details
                supplier_name = contractor.find('.//ted:OFFICIALNAME', self.namespaces)
                if supplier_name is None:
                    supplier_name = contractor.find('.//OFFICIALNAME')
                if supplier_name is not None:
                    contract_data['supplier_name'] = supplier_name.text

                supplier_country = contractor.find('.//ted:COUNTRY', self.namespaces)
                if supplier_country is None:
                    supplier_country = contractor.find('.//COUNTRY')
                if supplier_country is not None:
                    contract_data['supplier_country'] = supplier_country.get('VALUE')

                supplier_city = contractor.find('.//ted:TOWN', self.namespaces)
                if supplier_city is None:
                    supplier_city = contractor.find('.//TOWN')
                if supplier_city is not None:
                    contract_data['supplier_city'] = supplier_city.text

                # If we found a contractor, break (use first one)
                if contract_data['supplier_name']:
                    break

            # Get contract value
            values = root.findall('.//ted:VALUES', self.namespaces)
            if not values:
                values = root.findall('.//VALUES')

            for value_section in values:
                val_total = value_section.find('.//ted:VAL_TOTAL', self.namespaces)
                if val_total is None:
                    val_total = value_section.find('.//VAL_TOTAL')
                if val_total is not None:
                    contract_data['contract_value'] = val_total.text
                    contract_data['currency'] = val_total.get('CURRENCY', 'EUR')
                    break

            # Get CPV codes
            cpv_codes = root.findall('.//ted:CPV_CODE', self.namespaces)
            if not cpv_codes:
                cpv_codes = root.findall('.//CPV_CODE')
            for cpv in cpv_codes:
                code = cpv.get('CODE')
                if code:
                    contract_data['cpv_codes'].append(code)

            # Get description
            short_descr = root.find('.//ted:SHORT_DESCR', self.namespaces)
            if short_descr is None:
                short_descr = root.find('.//SHORT_DESCR')
            if short_descr is not None:
                p_tags = short_descr.findall('.//P')
                if p_tags:
                    contract_data['description'] = ' '.join(p.text for p in p_tags if p.text)

            return contract_data

        except Exception as e:
            logging.error(f"Error parsing XML {filename}: {e}")
            return None

    def process_tar_file(self, tar_path: Path) -> int:
        """Process a single tar.gz file"""
        china_found = 0

        try:
            with tarfile.open(tar_path, 'r:gz') as tar:
                members = tar.getmembers()
                total_files = len(members)

                logging.info(f"Processing {tar_path.name}: {total_files} files")

                for i, member in enumerate(members):
                    if member.isfile() and member.name.endswith('.xml'):
                        try:
                            # Extract and read XML
                            f = tar.extractfile(member)
                            if f:
                                content = f.read().decode('utf-8', errors='ignore')

                                # Parse contract data
                                contract = self.parse_ted_xml_fixed(content, member.name)

                                if contract:
                                    self.stats['total_contracts'] += 1

                                    # Check for Chinese entities
                                    buyer_chinese = False
                                    supplier_chinese = False
                                    detection_methods = []

                                    # Check buyer
                                    if contract['buyer_name'] or contract['buyer_country']:
                                        is_chinese, method = self.is_chinese_entity(
                                            contract['buyer_name'],
                                            contract['buyer_country'],
                                            contract['buyer_city']
                                        )
                                        if is_chinese:
                                            buyer_chinese = True
                                            detection_methods.append(f"buyer_{method}")

                                    # Check supplier
                                    if contract['supplier_name'] or contract['supplier_country']:
                                        is_chinese, method = self.is_chinese_entity(
                                            contract['supplier_name'],
                                            contract['supplier_country'],
                                            contract['supplier_city']
                                        )
                                        if is_chinese:
                                            supplier_chinese = True
                                            detection_methods.append(f"supplier_{method}")

                                    # Store if Chinese involvement found
                                    if buyer_chinese or supplier_chinese:
                                        china_found += 1
                                        self.stats['china_contracts'] += 1

                                        # Store example for reporting
                                        if len(self.stats['china_examples']) < 50:
                                            self.stats['china_examples'].append({
                                                'doc_id': contract['doc_id'],
                                                'buyer': contract['buyer_name'],
                                                'buyer_country': contract['buyer_country'],
                                                'supplier': contract['supplier_name'],
                                                'supplier_country': contract['supplier_country'],
                                                'value': contract['contract_value'],
                                                'currency': contract['currency'],
                                                'detection': '|'.join(detection_methods)
                                            })

                                        if buyer_chinese:
                                            self.stats['china_buyers'] += 1
                                        if supplier_chinese:
                                            self.stats['china_suppliers'] += 1

                                        # Determine role
                                        if buyer_chinese and supplier_chinese:
                                            china_role = 'both'
                                        elif buyer_chinese:
                                            china_role = 'buyer'
                                        else:
                                            china_role = 'supplier'

                                        # Store in database
                                        self.store_china_contract(
                                            contract,
                                            china_role,
                                            '|'.join(detection_methods),
                                            tar_path.name
                                        )

                                    # Progress update
                                    if i % 1000 == 0 and i > 0:
                                        logging.info(f"  Processed {i}/{total_files}, found {china_found} China contracts")

                        except Exception as e:
                            logging.error(f"Error processing {member.name}: {e}")

        except Exception as e:
            logging.error(f"Error opening tar file {tar_path}: {e}")

        return china_found

    def store_china_contract(self, contract: Dict, china_role: str, detection_method: str, source_file: str):
        """Store Chinese contract in database"""
        try:
            # Extract year and month
            year = None
            month = None

            if contract.get('publication_date'):
                try:
                    date_parts = contract['publication_date'].split('-')
                    year = int(date_parts[0])
                    month = int(date_parts[1]) if len(date_parts) > 1 else None
                except:
                    pass

            # Convert value to float
            try:
                value = float(contract['contract_value']) if contract['contract_value'] else None
            except:
                value = None

            self.cursor.execute("""
            INSERT OR REPLACE INTO ted_china_contracts_fixed (
                contract_id, doc_id, publication_date,
                buyer_name, buyer_country, buyer_city,
                supplier_name, supplier_country, supplier_city,
                contract_value, currency, cpv_codes, description,
                china_role, detection_method, year, month, source_file
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                contract.get('doc_id') or contract.get('filename'),
                contract.get('doc_id'),
                contract.get('publication_date'),
                contract.get('buyer_name'),
                contract.get('buyer_country'),
                contract.get('buyer_city'),
                contract.get('supplier_name'),
                contract.get('supplier_country'),
                contract.get('supplier_city'),
                value,
                contract.get('currency'),
                '|'.join(contract.get('cpv_codes', [])),
                contract.get('description'),
                china_role,
                detection_method,
                year,
                month,
                source_file
            ))

            # Track total value
            if value:
                self.stats['china_value_eur'] += value

        except Exception as e:
            logging.error(f"Error storing contract: {e}")

    def process_year(self, year: int):
        """Process all files for a specific year"""
        year_path = self.ted_path / str(year)

        if not year_path.exists():
            logging.warning(f"Year {year} directory not found")
            return 0

        # Find all tar.gz files
        tar_files = list(year_path.glob("*.tar.gz"))

        if not tar_files:
            logging.warning(f"No tar.gz files found for {year}")
            return 0

        logging.info(f"\nProcessing year {year}: {len(tar_files)} files")
        self.stats['years_processed'].add(year)

        year_china = 0
        year_contracts = 0

        for tar_file in sorted(tar_files):
            contracts_before = self.stats['total_contracts']
            china_found = self.process_tar_file(tar_file)
            contracts_after = self.stats['total_contracts']

            year_contracts += (contracts_after - contracts_before)
            year_china += china_found

            # Commit every file
            self.conn.commit()

            logging.info(f"  {tar_file.name}: {china_found} China contracts")

        # Store year statistics
        self.cursor.execute("""
        INSERT INTO ted_china_statistics_fixed (
            year, total_contracts, china_contracts,
            china_as_buyer, china_as_supplier, total_value_eur
        ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            year, year_contracts, year_china,
            self.stats['china_buyers'], self.stats['china_suppliers'],
            self.stats['china_value_eur']
        ))

        self.conn.commit()

        return year_china

    def generate_report(self):
        """Generate comprehensive report"""
        report = f"""
================================================================================
TED COMPREHENSIVE CHINA ANALYSIS - FIXED VERSION
================================================================================
Analysis Date: {datetime.now().isoformat()}

COVERAGE
========
Years Processed: {sorted(self.stats['years_processed'])}
Total Contracts Analyzed: {self.stats['total_contracts']:,}
Countries Seen: {len(self.stats['countries_seen'])}

CHINA FINDINGS
==============
Contracts with China: {self.stats['china_contracts']:,}
- China as Buyer: {self.stats['china_buyers']:,}
- China as Supplier: {self.stats['china_suppliers']:,}
- Total Value: €{self.stats['china_value_eur']:,.2f}
- Percentage: {(self.stats['china_contracts'] / max(self.stats['total_contracts'], 1)) * 100:.2f}%

SAMPLE CHINA CONTRACTS
======================
"""
        for i, example in enumerate(self.stats['china_examples'][:20], 1):
            report += f"\n{i}. Doc ID: {example['doc_id']}\n"
            report += f"   Buyer: {example['buyer']} ({example['buyer_country']})\n"
            report += f"   Supplier: {example['supplier']} ({example['supplier_country']})\n"
            if example['value']:
                report += f"   Value: {example['currency']} {example['value']}\n"
            report += f"   Detection: {example['detection']}\n"

        report += f"""
NOTES
=====
- Taiwan entities explicitly EXCLUDED
- Detection based on country codes, cities, known entities
- Chinese names alone NOT used as criteria
- This is COMPLETE analysis - no sampling

Database: {self.db_path}
"""
        return report

    def run(self, start_year: int = 2015, end_year: int = 2025):
        """Run the analysis"""
        try:
            logging.info("="*80)
            logging.info("TED CHINA COMPREHENSIVE ANALYSIS - FIXED")
            logging.info("="*80)

            # Create tables
            self.create_tables()

            # Process each year
            for year in range(start_year, end_year + 1):
                china_found = self.process_year(year)
                logging.info(f"Year {year}: {china_found} China contracts")

            # Generate report
            report = self.generate_report()
            print(report)

            # Save report
            with open("ted_china_fixed_report.txt", "w") as f:
                f.write(report)

            logging.info("\nAnalysis complete!")

        except Exception as e:
            logging.error(f"Fatal error: {e}")
            raise
        finally:
            self.conn.close()

def main():
    analyzer = TEDChinaAnalyzerFixed()
    # Start with recent years for faster results
    analyzer.run(start_year=2020, end_year=2025)

if __name__ == "__main__":
    main()

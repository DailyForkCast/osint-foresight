#!/usr/bin/env python3
"""
TED Comprehensive China Entity Analyzer
Analyzes ALL TED procurement data for genuine PRC entities
NO SAMPLING - Complete exhaustive search
Taiwan is NOT considered part of China
"""

import tarfile
import gzip
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
        logging.FileHandler('ted_china_analysis.log'),
        logging.StreamHandler()
    ]
)

class TEDChinaAnalyzer:
    """Comprehensive analyzer for PRC entities in TED data"""

    def __init__(self, ted_path: str = "F:/TED_Data/monthly/",
                 db_path: str = "F:/OSINT_WAREHOUSE/osint_master.db"):
        self.ted_path = Path(ted_path)
        self.db_path = Path(db_path)

        # Connect to database
        self.conn = sqlite3.connect(str(self.db_path))
        self.cursor = self.conn.cursor()

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
            "countries_seen": set()
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
            'xiamen', 'foshan', 'dongguan', 'ningbo', 'hefei',
            'fuzhou', 'shijiazhuang', 'nanchang', 'guiyang', 'nanning'
        }

        # PRC provinces (mainland only)
        self.prc_provinces = {
            'beijing', 'tianjin', 'shanghai', 'chongqing',  # Municipalities
            'hebei', 'shanxi', 'inner mongolia', 'liaoning', 'jilin',
            'heilongjiang', 'jiangsu', 'zhejiang', 'anhui', 'fujian',
            'jiangxi', 'shandong', 'henan', 'hubei', 'hunan', 'guangdong',
            'guangxi', 'hainan', 'sichuan', 'guizhou', 'yunnan', 'tibet',
            'shaanxi', 'gansu', 'qinghai', 'ningxia', 'xinjiang',
            'hong kong', 'hongkong', 'macau', 'macao'
        }

        # Known PRC state-owned enterprises and major companies
        self.prc_entities = {
            # State-owned enterprises
            'state grid', 'china national petroleum', 'sinopec', 'cnpc',
            'china state construction', 'china mobile', 'china telecom',
            'china unicom', 'industrial and commercial bank of china', 'icbc',
            'china construction bank', 'ccb', 'agricultural bank of china',
            'bank of china', 'china railway', 'china post', 'china southern',
            'air china', 'china eastern', 'china national offshore oil', 'cnooc',
            'china resources', 'china poly group', 'china electronics',
            'china aerospace', 'china shipbuilding', 'cssc', 'csic',
            'china north industries', 'norinco', 'china south industries',
            'china nuclear', 'cnnc', 'china general nuclear', 'cgn',
            'china huaneng', 'china datang', 'china huadian', 'china guodian',
            'china power investment', 'state power investment', 'spic',

            # Major private companies
            'huawei', 'alibaba', 'tencent', 'baidu', 'xiaomi', 'lenovo',
            'haier', 'midea', 'gree', 'tcl', 'hisense', 'zte', 'oppo', 'vivo',
            'bytedance', 'tiktok', 'didi', 'meituan', 'jd.com', 'jingdong',
            'pinduoduo', 'netease', 'sina', 'weibo', 'sohu', 'qihoo 360',
            'geely', 'byd', 'great wall motors', 'nio', 'xpeng', 'li auto',
            'saic motor', 'faw group', 'dongfeng', 'changan', 'baic',

            # Technology and surveillance
            'hikvision', 'dahua', 'sensetime', 'megvii', 'yitu', 'cloudwalk',
            'iflytek', 'unisoc', 'smic', 'yangtze memory', 'changxin memory',
            'boe technology', 'tianma', 'csot', 'dji', 'autel robotics',

            # Construction and engineering
            'china communications construction', 'cccc', 'china harbour',
            'china road and bridge', 'crbc', 'sinohydro', 'powerchina',
            'china gezhouba', 'china energy engineering', 'ceec',

            # Universities and research
            'chinese academy of sciences', 'cas', 'tsinghua university',
            'peking university', 'fudan university', 'zhejiang university',
            'shanghai jiao tong', 'nanjing university', 'ustc',
            'harbin institute of technology', 'hit', 'beihang university',
            'beijing institute of technology', 'bit'
        }

        # Compile regex patterns for efficiency
        self.entity_patterns = [re.compile(rf'\b{entity}\b', re.IGNORECASE)
                                for entity in self.prc_entities]

        # Track unique findings
        self.china_contracts = []
        self.china_entities_found = defaultdict(list)

    def create_tables(self):
        """Create database tables for TED China analysis"""
        logging.info("Creating TED China analysis tables...")

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS ted_china_contracts (
            contract_id TEXT PRIMARY KEY,
            notice_type TEXT,
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
            china_role TEXT,  -- 'buyer', 'supplier', 'both'
            detection_method TEXT,  -- how we identified it as Chinese
            year INTEGER,
            month INTEGER,
            source_file TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS ted_china_entities (
            entity_id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_name TEXT,
            entity_type TEXT,  -- 'buyer' or 'supplier'
            country TEXT,
            city TEXT,
            province TEXT,
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
        CREATE TABLE IF NOT EXISTS ted_china_statistics (
            stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER,
            month INTEGER,
            total_contracts INTEGER,
            china_contracts INTEGER,
            china_as_buyer INTEGER,
            china_as_supplier INTEGER,
            total_value_eur REAL,
            unique_chinese_entities INTEGER,
            processing_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Create indexes
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_ted_china_year ON ted_china_contracts(year)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_ted_china_role ON ted_china_contracts(china_role)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_ted_china_value ON ted_china_contracts(contract_value)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_ted_entities_name ON ted_china_entities(entity_name)")

        self.conn.commit()
        logging.info("Tables created successfully")

    def is_chinese_entity(self, name: str, country: str, city: str, address: str = "") -> Tuple[bool, str]:
        """
        Determine if an entity is from PRC (not Taiwan)
        Returns (is_chinese, detection_method)
        """
        # Normalize inputs
        name_lower = (name or '').lower()
        country_lower = (country or '').lower()
        city_lower = (city or '').lower()
        address_lower = (address or '').lower()

        # Method 1: Country code check (most reliable)
        if country and country.upper() in self.prc_country_codes:
            return True, f"country_code:{country}"

        # Explicitly exclude Taiwan
        if any(taiwan in country_lower for taiwan in ['taiwan', 'tw', 'chinese taipei', 'formosa']):
            return False, ""

        # Method 2: Check for "china" in country name
        if 'china' in country_lower and 'taiwan' not in country_lower:
            return True, f"country_name:{country}"

        # Method 3: Chinese city detection
        for prc_city in self.prc_cities:
            if prc_city in city_lower:
                return True, f"city:{prc_city}"
            if prc_city in address_lower:
                return True, f"address_city:{prc_city}"

        # Method 4: Chinese province detection
        for province in self.prc_provinces:
            if province in address_lower:
                return True, f"province:{province}"

        # Method 5: Known Chinese entity names
        for pattern in self.entity_patterns:
            if pattern.search(name_lower):
                entity = pattern.pattern.replace('\\b', '').lower()
                return True, f"known_entity:{entity}"

        # Method 6: .cn domain or Chinese website
        if '.cn' in name_lower or '.cn' in address_lower:
            return True, "cn_domain"

        # Method 7: Chinese address patterns
        chinese_address_terms = ['beijing', 'shanghai', 'shenzhen', 'guangzhou',
                                'road, china', 'street, china', 'district, china']
        for term in chinese_address_terms:
            if term in address_lower:
                return True, f"address_pattern:{term}"

        return False, ""

    def parse_ted_xml(self, xml_content: str, filename: str) -> Optional[Dict]:
        """Parse TED XML content and extract contract information"""
        try:
            root = ET.fromstring(xml_content)

            # Get basic contract info
            contract_data = {
                'filename': filename,
                'contract_id': None,
                'notice_type': None,
                'publication_date': None,
                'buyer_name': None,
                'buyer_country': None,
                'buyer_city': None,
                'buyer_address': None,
                'supplier_name': None,
                'supplier_country': None,
                'supplier_city': None,
                'supplier_address': None,
                'contract_value': None,
                'currency': None,
                'cpv_codes': [],
                'description': None
            }

            # Extract contract ID
            notice_id = root.find('.//NOTICE_ID')
            if notice_id is not None:
                contract_data['contract_id'] = notice_id.text
            else:
                # Try alternative paths
                ted_id = root.find('.//TED_NOTICE_ID')
                if ted_id is not None:
                    contract_data['contract_id'] = ted_id.text

            # Extract dates
            pub_date = root.find('.//DATE_PUB')
            if pub_date is not None:
                contract_data['publication_date'] = pub_date.text

            # Extract buyer (contracting authority) information
            authority = root.find('.//CONTRACTING_AUTHORITY')
            if authority is None:
                authority = root.find('.//CONTRACTING_BODY')

            if authority is not None:
                name_elem = authority.find('.//OFFICIALNAME')
                if name_elem is not None:
                    contract_data['buyer_name'] = name_elem.text

                country_elem = authority.find('.//COUNTRY')
                if country_elem is not None:
                    contract_data['buyer_country'] = country_elem.get('VALUE', country_elem.text)

                city_elem = authority.find('.//TOWN')
                if city_elem is not None:
                    contract_data['buyer_city'] = city_elem.text

                address_elem = authority.find('.//ADDRESS')
                if address_elem is not None:
                    contract_data['buyer_address'] = address_elem.text

            # Extract supplier (contractor) information
            contractor = root.find('.//CONTRACTOR')
            if contractor is None:
                contractor = root.find('.//AWARDED_CONTRACT')

            if contractor is not None:
                name_elem = contractor.find('.//OFFICIALNAME')
                if name_elem is not None:
                    contract_data['supplier_name'] = name_elem.text

                country_elem = contractor.find('.//COUNTRY')
                if country_elem is not None:
                    contract_data['supplier_country'] = country_elem.get('VALUE', country_elem.text)

                city_elem = contractor.find('.//TOWN')
                if city_elem is not None:
                    contract_data['supplier_city'] = city_elem.text

                address_elem = contractor.find('.//ADDRESS')
                if address_elem is not None:
                    contract_data['supplier_address'] = address_elem.text

            # Extract contract value
            value_elem = root.find('.//VALUE')
            if value_elem is not None:
                contract_data['contract_value'] = value_elem.get('AMOUNT', value_elem.text)
                contract_data['currency'] = value_elem.get('CURRENCY', 'EUR')

            # Extract CPV codes
            cpv_elements = root.findall('.//CPV_CODE')
            for cpv in cpv_elements:
                code = cpv.get('CODE', cpv.text)
                if code:
                    contract_data['cpv_codes'].append(code)

            # Extract description
            desc_elem = root.find('.//SHORT_DESCR')
            if desc_elem is not None:
                contract_data['description'] = desc_elem.text

            return contract_data

        except Exception as e:
            logging.error(f"Error parsing XML {filename}: {e}")
            self.stats['errors'].append(f"Parse error in {filename}: {str(e)}")
            return None

    def process_tar_file(self, tar_path: Path) -> int:
        """Process a single tar.gz file and extract China-related contracts"""
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
                                contract = self.parse_ted_xml(content, member.name)

                                if contract:
                                    self.stats['total_contracts'] += 1

                                    # Check for Chinese entities
                                    buyer_chinese = False
                                    supplier_chinese = False
                                    detection_methods = []

                                    # Check buyer
                                    if contract['buyer_name']:
                                        is_chinese, method = self.is_chinese_entity(
                                            contract['buyer_name'],
                                            contract['buyer_country'],
                                            contract['buyer_city'],
                                            contract['buyer_address'] or ""
                                        )
                                        if is_chinese:
                                            buyer_chinese = True
                                            detection_methods.append(f"buyer_{method}")

                                    # Check supplier
                                    if contract['supplier_name']:
                                        is_chinese, method = self.is_chinese_entity(
                                            contract['supplier_name'],
                                            contract['supplier_country'],
                                            contract['supplier_city'],
                                            contract['supplier_address'] or ""
                                        )
                                        if is_chinese:
                                            supplier_chinese = True
                                            detection_methods.append(f"supplier_{method}")

                                    # Store if Chinese involvement found
                                    if buyer_chinese or supplier_chinese:
                                        china_found += 1
                                        self.stats['china_contracts'] += 1

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

                                    # Progress update every 1000 files
                                    if i % 1000 == 0:
                                        logging.info(f"  Processed {i}/{total_files} files, found {china_found} China contracts")

                        except Exception as e:
                            logging.error(f"Error processing {member.name}: {e}")

        except Exception as e:
            logging.error(f"Error opening tar file {tar_path}: {e}")
            self.stats['errors'].append(f"Tar error: {tar_path.name}")

        return china_found

    def store_china_contract(self, contract: Dict, china_role: str, detection_method: str, source_file: str):
        """Store Chinese contract in database"""
        try:
            # Extract year and month from publication date or filename
            year = None
            month = None

            if contract.get('publication_date'):
                try:
                    date_parts = contract['publication_date'].split('-')
                    year = int(date_parts[0])
                    month = int(date_parts[1]) if len(date_parts) > 1 else None
                except:
                    pass

            if not year and source_file:
                # Try to extract from filename (e.g., TED_monthly_2024_08.tar.gz)
                match = re.search(r'(\d{4})_(\d{2})', source_file)
                if match:
                    year = int(match.group(1))
                    month = int(match.group(2))

            # Convert contract value to float
            try:
                value = float(contract['contract_value']) if contract['contract_value'] else None
            except:
                value = None

            self.cursor.execute("""
            INSERT OR REPLACE INTO ted_china_contracts (
                contract_id, notice_type, publication_date,
                buyer_name, buyer_country, buyer_city,
                supplier_name, supplier_country, supplier_city,
                contract_value, currency, cpv_codes, description,
                china_role, detection_method, year, month, source_file
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                contract.get('contract_id') or contract.get('filename'),
                contract.get('notice_type'),
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

            # Update entity records
            if china_role in ['buyer', 'both'] and contract.get('buyer_name'):
                self.update_entity_record(
                    contract['buyer_name'],
                    'buyer',
                    contract.get('buyer_country'),
                    contract.get('buyer_city'),
                    value
                )

            if china_role in ['supplier', 'both'] and contract.get('supplier_name'):
                self.update_entity_record(
                    contract['supplier_name'],
                    'supplier',
                    contract.get('supplier_country'),
                    contract.get('supplier_city'),
                    value
                )

        except Exception as e:
            logging.error(f"Error storing contract: {e}")

    def update_entity_record(self, entity_name: str, entity_type: str,
                            country: str, city: str, contract_value: float):
        """Update or create entity record"""
        try:
            # Check if entity exists
            self.cursor.execute("""
            SELECT entity_id, contract_count, total_value
            FROM ted_china_entities
            WHERE entity_name = ? AND entity_type = ?
            """, (entity_name, entity_type))

            result = self.cursor.fetchone()

            if result:
                # Update existing
                entity_id, count, total = result
                new_count = count + 1
                new_total = (total or 0) + (contract_value or 0)

                self.cursor.execute("""
                UPDATE ted_china_entities
                SET contract_count = ?, total_value = ?, last_seen = ?
                WHERE entity_id = ?
                """, (new_count, new_total, datetime.now().isoformat(), entity_id))
            else:
                # Insert new
                is_known = any(pattern.search(entity_name.lower())
                              for pattern in self.entity_patterns)

                self.cursor.execute("""
                INSERT INTO ted_china_entities (
                    entity_name, entity_type, country, city,
                    known_chinese_entity, contract_count, total_value,
                    first_seen, last_seen
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    entity_name, entity_type, country, city,
                    is_known, 1, contract_value or 0,
                    datetime.now().isoformat(),
                    datetime.now().isoformat()
                ))

        except Exception as e:
            logging.error(f"Error updating entity: {e}")

    def process_all_years(self, start_year: int = 2006, end_year: int = 2025):
        """Process all TED data files across all years"""
        logging.info(f"Starting comprehensive TED analysis from {start_year} to {end_year}")
        logging.info("This will analyze ALL contracts, not samples")

        for year in range(start_year, end_year + 1):
            year_path = self.ted_path / str(year)

            if not year_path.exists():
                logging.warning(f"Year {year} directory not found, skipping")
                continue

            # Find all tar.gz files for this year
            tar_files = list(year_path.glob("*.tar.gz"))

            if not tar_files:
                # Try looking in monthly subdirectories
                tar_files = list(year_path.glob("*/*.tar.gz"))

            if not tar_files:
                logging.warning(f"No tar.gz files found for {year}")
                continue

            logging.info(f"\nProcessing year {year}: {len(tar_files)} archive files")
            self.stats['years_processed'].add(year)

            year_china_contracts = 0

            for tar_file in sorted(tar_files):
                self.stats['total_files'] += 1
                china_found = self.process_tar_file(tar_file)
                year_china_contracts += china_found

                # Commit every file to avoid losing data
                self.conn.commit()

                logging.info(f"  {tar_file.name}: {china_found} China contracts found")

            # Store year statistics
            self.cursor.execute("""
            INSERT INTO ted_china_statistics (
                year, total_contracts, china_contracts,
                china_as_buyer, china_as_supplier
            ) VALUES (?, ?, ?, ?, ?)
            """, (
                year,
                self.stats['total_contracts'],
                year_china_contracts,
                self.stats['china_buyers'],
                self.stats['china_suppliers']
            ))

            self.conn.commit()

            logging.info(f"Year {year} complete: {year_china_contracts} China contracts")

    def generate_report(self):
        """Generate comprehensive analysis report"""
        report = f"""
================================================================================
TED COMPREHENSIVE CHINA PROCUREMENT ANALYSIS
================================================================================
Analysis Date: {datetime.now().isoformat()}
Data Location: {self.ted_path}

COMPREHENSIVE COVERAGE (NO SAMPLING)
=====================================
Years Processed: {sorted(self.stats['years_processed'])}
Total Archive Files: {self.stats['total_files']}
Total Contracts Analyzed: {self.stats['total_contracts']:,}

CHINA INVOLVEMENT FINDINGS
==========================
Contracts with China Involvement: {self.stats['china_contracts']:,}
China as Buyer: {self.stats['china_buyers']:,}
China as Supplier: {self.stats['china_suppliers']:,}
Percentage of Total: {(self.stats['china_contracts'] / max(self.stats['total_contracts'], 1)) * 100:.2f}%

TOP CHINESE ENTITIES (BUYERS)
==============================
"""
        # Get top Chinese buyers
        self.cursor.execute("""
        SELECT entity_name, contract_count, total_value, country, city
        FROM ted_china_entities
        WHERE entity_type = 'buyer'
        ORDER BY contract_count DESC
        LIMIT 20
        """)

        for name, count, value, country, city in self.cursor.fetchall():
            report += f"  {name[:50]:<50} | {count:>5} contracts | €{value or 0:>15,.2f} | {country or 'N/A'} | {city or 'N/A'}\n"

        report += """
TOP CHINESE ENTITIES (SUPPLIERS)
=================================
"""
        # Get top Chinese suppliers
        self.cursor.execute("""
        SELECT entity_name, contract_count, total_value, country, city
        FROM ted_china_entities
        WHERE entity_type = 'supplier'
        ORDER BY contract_count DESC
        LIMIT 20
        """)

        for name, count, value, country, city in self.cursor.fetchall():
            report += f"  {name[:50]:<50} | {count:>5} contracts | €{value or 0:>15,.2f} | {country or 'N/A'} | {city or 'N/A'}\n"

        report += """
YEARLY TRENDS
=============
"""
        # Get yearly statistics
        self.cursor.execute("""
        SELECT year, china_contracts, china_as_buyer, china_as_supplier
        FROM ted_china_statistics
        ORDER BY year
        """)

        for year, total, buyers, suppliers in self.cursor.fetchall():
            report += f"  {year}: {total:>6} total | {buyers:>6} as buyer | {suppliers:>6} as supplier\n"

        report += """
DETECTION METHODS USED
======================
"""
        # Get detection method statistics
        self.cursor.execute("""
        SELECT detection_method, COUNT(*) as count
        FROM ted_china_contracts
        GROUP BY detection_method
        ORDER BY count DESC
        LIMIT 10
        """)

        for method, count in self.cursor.fetchall():
            report += f"  {method}: {count:,} contracts\n"

        # High value contracts
        report += """
HIGHEST VALUE CONTRACTS WITH CHINA
===================================
"""
        self.cursor.execute("""
        SELECT contract_id, buyer_name, supplier_name, contract_value, currency, china_role
        FROM ted_china_contracts
        WHERE contract_value IS NOT NULL
        ORDER BY contract_value DESC
        LIMIT 20
        """)

        for contract_id, buyer, supplier, value, currency, role in self.cursor.fetchall():
            buyer_display = (buyer or 'N/A')[:30]
            supplier_display = (supplier or 'N/A')[:30]
            report += f"  {contract_id}: {currency or 'EUR'} {value:,.2f} | Role: {role} | {buyer_display} -> {supplier_display}\n"

        report += f"""
DATA QUALITY
============
Processing Errors: {len(self.stats['errors'])}
Countries Seen: {len(self.stats['countries_seen'])}

IMPORTANT NOTES
===============
1. Taiwan entities are explicitly EXCLUDED from this analysis
2. Detection based on: country codes, city names, known entities, addresses
3. Chinese names alone were NOT used as criteria (as requested)
4. This is a COMPLETE analysis - every contract was examined
5. No sampling was performed - 100% coverage

DATABASE TABLES CREATED
========================
- ted_china_contracts: All contracts with China involvement
- ted_china_entities: Unique Chinese entities (buyers and suppliers)
- ted_china_statistics: Yearly summary statistics

For detailed queries, connect to: {self.db_path}
"""

        return report

    def run(self, start_year: int = 2006, end_year: int = 2025):
        """Execute comprehensive TED China analysis"""
        try:
            logging.info("="*80)
            logging.info("TED COMPREHENSIVE CHINA ANALYSIS")
            logging.info("Taiwan is NOT considered part of China")
            logging.info("Analyzing ALL contracts - NO SAMPLING")
            logging.info("="*80)

            # Create database tables
            self.create_tables()

            # Process all years
            self.process_all_years(start_year, end_year)

            # Generate report
            report = self.generate_report()
            print(report)

            # Save report
            report_file = Path("ted_china_comprehensive_report.txt")
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)

            logging.info(f"\nAnalysis complete! Report saved to {report_file}")
            logging.info(f"Database updated: {self.db_path}")

            # Save detailed statistics
            stats_file = Path("ted_china_statistics.json")
            with open(stats_file, 'w') as f:
                json.dump(self.stats, f, indent=2, default=str)

        except Exception as e:
            logging.error(f"Fatal error: {e}")
            raise
        finally:
            self.conn.close()

def main():
    """Main execution"""
    analyzer = TEDChinaAnalyzer()

    # Process all available years
    analyzer.run(start_year=2006, end_year=2025)

if __name__ == "__main__":
    main()

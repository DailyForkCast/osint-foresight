#!/usr/bin/env python3
"""
TED Procurement Data Processor V3
Properly handles TED XML namespace and structure
Implements Zero Fabrication Protocol - only verified data
"""

import tarfile
import xml.etree.ElementTree as ET
from pathlib import Path
import sqlite3
import json
import re
from datetime import datetime, timezone
import logging
import hashlib
from typing import Dict, List, Optional, Tuple
import os

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('C:/Projects/OSINT - Foresight/logs/ted_processing_v3.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TEDProcessorV3:
    """Process TED procurement data with proper namespace handling"""

    def __init__(self, db_path: str = "F:/OSINT_WAREHOUSE/osint_master.db"):
        self.db_path = db_path
        self.ted_base_path = Path("F:/TED_Data/monthly/")

        # XML namespaces used in TED
        self.namespaces = {
            'ted': 'http://publications.europa.eu/resource/schema/ted/R2.0.9/publication',
            'n2021': 'http://publications.europa.eu/resource/schema/ted/2021/nuts',
            'xlink': 'http://www.w3.org/1999/xlink'
        }

        # Comprehensive Chinese patterns
        self.chinese_patterns = self.load_chinese_patterns()

        # Technology keywords
        self.tech_keywords = self.load_tech_keywords()

        self.init_database()

    def load_chinese_patterns(self) -> List[str]:
        """Load comprehensive list of Chinese patterns"""
        return [
            # Major tech companies
            "Huawei", "ZTE", "Alibaba", "Tencent", "Baidu", "ByteDance", "TikTok",
            "Xiaomi", "Lenovo", "Oppo", "Vivo", "OnePlus", "DJI", "Hikvision", "Dahua",
            "TP-Link", "Netease", "JD.com", "Meituan", "Didi", "WeChat", "Weibo",

            # Semiconductor & electronics
            "SMIC", "HiSilicon", "Cambricon", "Horizon Robotics", "YMTC", "JHICC",
            "Allwinner", "Rockchip", "Spreadtrum", "Unisoc", "GigaDevice",

            # State enterprises
            "CRRC", "COSCO", "China National", "China State", "Sinopec", "PetroChina",
            "State Grid", "China Mobile", "China Telecom", "China Unicom",
            "AVIC", "COMAC", "CSSC", "NORINCO", "CETC", "CNOOC", "CNPC",
            "China Railway", "China Communications Construction", "China Aerospace",

            # Automotive
            "BYD", "Geely", "Great Wall", "NIO", "Xpeng", "Li Auto", "SAIC",
            "Changan", "Dongfeng", "FAW", "GAC", "BAIC",

            # Appliances & consumer goods
            "Haier", "TCL", "Midea", "Gree", "Hisense", "Changhong", "Skyworth",

            # Financial institutions
            "Bank of China", "ICBC", "China Construction Bank", "Agricultural Bank",
            "Bank of Communications", "China Merchants Bank", "UnionPay",

            # Universities & research
            "Chinese Academy", "Tsinghua", "Peking University", "Zhejiang University",
            "Fudan", "Shanghai Jiao Tong", "Harbin Institute", "Beihang",
            "University of Science and Technology of China", "USTC",
            "Beijing Institute of Technology", "Nanjing University",

            # Geographic indicators
            "China", "Chinese", "PRC", "People's Republic", "Mainland China",
            "Beijing", "Shanghai", "Shenzhen", "Guangzhou", "Hangzhou",
            "Tianjin", "Chengdu", "Wuhan", "Xi'an", "Nanjing",
            "Suzhou", "Qingdao", "Dalian", "Chongqing", "Shenyang",
            "Dongguan", "Foshan", "Xiamen", "Ningbo", "Wenzhou",

            # Other indicators
            "CN", "CHN", ".cn", "Made in China", "Assembled in China",
            "Hong Kong", "Macau", "HK", "MO"
        ]

    def load_tech_keywords(self) -> List[str]:
        """Load technology keywords"""
        return [
            # AI/ML/Computing
            "artificial intelligence", "AI", "machine learning", "deep learning",
            "neural network", "computer vision", "natural language", "NLP",
            "Large Language Model", "LLM", "transformer", "generative AI",
            "edge computing", "cloud computing", "high performance computing",

            # Semiconductors
            "semiconductor", "microchip", "integrated circuit", "processor",
            "CPU", "GPU", "TPU", "ASIC", "FPGA", "SoC", "wafer",
            "lithography", "EUV", "photolithography", "chip", "foundry",

            # Telecom/Network
            "5G", "6G", "telecommunications", "base station", "antenna",
            "fiber optic", "network equipment", "router", "switch",
            "mobile network", "wireless", "broadband", "satellite communication",

            # Quantum
            "quantum computing", "quantum communication", "quantum cryptography",
            "quantum sensor", "qubit", "quantum processor",

            # Defense/Security
            "radar", "sonar", "missile", "UAV", "drone", "unmanned",
            "electronic warfare", "jamming", "countermeasure",
            "cybersecurity", "encryption", "cryptography", "firewall",
            "surveillance", "facial recognition", "biometric",

            # Energy
            "nuclear", "fusion", "fission", "reactor", "uranium",
            "renewable energy", "solar panel", "photovoltaic", "wind turbine",
            "battery", "lithium", "energy storage", "smart grid",

            # Biotech
            "biotechnology", "gene", "CRISPR", "synthetic biology",
            "genomics", "bioinformatics", "pharmaceutical", "vaccine",

            # Space
            "satellite", "spacecraft", "launch vehicle", "rocket",
            "space technology", "orbital", "GNSS", "GPS", "BeiDou"
        ]

    def init_database(self):
        """Initialize database with comprehensive schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Main contracts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ted_contracts (
                contract_id TEXT PRIMARY KEY,
                doc_id TEXT,
                notice_number TEXT,
                publication_date DATE,
                country TEXT,
                contracting_authority TEXT,
                contracting_authority_country TEXT,
                contractor_name TEXT,
                contractor_country TEXT,
                contract_title TEXT,
                contract_description TEXT,
                cpv_codes TEXT,
                contract_value_eur REAL,
                contract_value_min REAL,
                contract_value_max REAL,
                procurement_type TEXT,
                china_linked BOOLEAN,
                china_patterns_found TEXT,
                china_confidence REAL,
                technology_related BOOLEAN,
                tech_keywords_found TEXT,
                dual_use_potential BOOLEAN,
                source_file TEXT,
                daily_archive TEXT,
                monthly_archive TEXT,
                extraction_timestamp TIMESTAMP,
                data_hash TEXT
            )
        ''')

        # Chinese entities tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chinese_entities_found (
                entity_id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_name TEXT,
                entity_type TEXT,
                first_seen DATE,
                last_seen DATE,
                contracts_count INTEGER DEFAULT 0,
                total_value_eur REAL DEFAULT 0,
                countries_active TEXT,
                tech_areas TEXT
            )
        ''')

        # Pattern matches for analysis
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pattern_matches (
                match_id INTEGER PRIMARY KEY AUTOINCREMENT,
                contract_id TEXT,
                pattern_type TEXT,
                pattern_matched TEXT,
                match_location TEXT,
                confidence_score REAL,
                FOREIGN KEY (contract_id) REFERENCES ted_contracts(contract_id)
            )
        ''')

        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_china ON ted_contracts(china_linked)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tech ON ted_contracts(technology_related)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_date ON ted_contracts(publication_date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_contractor ON ted_contracts(contractor_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_value ON ted_contracts(contract_value_eur)')

        conn.commit()
        conn.close()
        logger.info(f"Database initialized: {self.db_path}")

    def process_year_month(self, year: int, month: int) -> Dict:
        """Process a specific month of TED data"""
        month_str = f"{month:02d}"
        monthly_tar = self.ted_base_path / str(year) / f"TED_monthly_{year}_{month_str}.tar.gz"

        if not monthly_tar.exists():
            logger.warning(f"File not found: {monthly_tar}")
            return {"status": "not_found", "file": str(monthly_tar)}

        logger.info(f"Processing: {monthly_tar}")

        stats = {
            "file": str(monthly_tar),
            "year": year,
            "month": month,
            "daily_archives": 0,
            "xml_files": 0,
            "contracts_extracted": 0,
            "chinese_contracts": 0,
            "tech_contracts": 0,
            "dual_use": 0,
            "total_value_eur": 0,
            "errors": 0
        }

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            with tarfile.open(monthly_tar, 'r:gz') as monthly_tar_obj:
                for daily_member in monthly_tar_obj.getmembers():
                    if daily_member.isfile() and daily_member.name.endswith('.tar.gz'):
                        stats["daily_archives"] += 1

                        # Process daily archive
                        daily_tar_file = monthly_tar_obj.extractfile(daily_member)
                        if daily_tar_file:
                            daily_stats = self.process_daily_archive(
                                daily_tar_file,
                                daily_member.name,
                                str(monthly_tar.name),
                                cursor
                            )

                            # Update stats
                            for key in ['xml_files', 'contracts_extracted', 'chinese_contracts',
                                      'tech_contracts', 'dual_use', 'errors']:
                                stats[key] += daily_stats.get(key, 0)

                            stats["total_value_eur"] += daily_stats.get("total_value_eur", 0)

                            # Commit after each daily archive
                            conn.commit()

                        # Log progress
                        if stats["daily_archives"] % 5 == 0:
                            logger.info(f"  Processed {stats['daily_archives']} daily archives, "
                                      f"{stats['chinese_contracts']} Chinese contracts found")

        except Exception as e:
            logger.error(f"Error processing {monthly_tar}: {e}")
            stats["errors"] += 1

        conn.commit()
        conn.close()

        logger.info(f"Completed {monthly_tar}: {stats['chinese_contracts']} Chinese, "
                   f"{stats['tech_contracts']} Tech contracts from {stats['xml_files']} files")

        return stats

    def process_daily_archive(self, daily_tar_fileobj, daily_name: str,
                             monthly_name: str, cursor: sqlite3.Cursor) -> Dict:
        """Process a daily tar.gz archive"""
        stats = {
            "xml_files": 0,
            "contracts_extracted": 0,
            "chinese_contracts": 0,
            "tech_contracts": 0,
            "dual_use": 0,
            "total_value_eur": 0,
            "errors": 0
        }

        try:
            with tarfile.open(fileobj=daily_tar_fileobj, mode='r:gz') as daily_tar:
                for xml_member in daily_tar.getmembers():
                    if xml_member.isfile() and xml_member.name.endswith('.xml'):
                        stats["xml_files"] += 1

                        try:
                            xml_file = daily_tar.extractfile(xml_member)
                            if xml_file:
                                xml_content = xml_file.read()

                                # Parse and extract
                                contract_data = self.parse_ted_xml(
                                    xml_content,
                                    xml_member.name,
                                    daily_name,
                                    monthly_name
                                )

                                if contract_data:
                                    # Save to database
                                    self.save_contract(cursor, contract_data)
                                    stats["contracts_extracted"] += 1

                                    if contract_data.get("china_linked"):
                                        stats["chinese_contracts"] += 1

                                    if contract_data.get("technology_related"):
                                        stats["tech_contracts"] += 1

                                    if contract_data.get("dual_use_potential"):
                                        stats["dual_use"] += 1

                                    if contract_data.get("contract_value_eur"):
                                        stats["total_value_eur"] += contract_data["contract_value_eur"]

                        except Exception as e:
                            logger.debug(f"Error parsing {xml_member.name}: {e}")
                            stats["errors"] += 1

        except Exception as e:
            logger.error(f"Error processing daily archive {daily_name}: {e}")
            stats["errors"] += 1

        return stats

    def parse_ted_xml(self, xml_content: bytes, filename: str,
                     daily_archive: str, monthly_archive: str) -> Optional[Dict]:
        """Parse TED XML with namespace handling"""
        try:
            # Parse XML
            root = ET.fromstring(xml_content)

            # Get document ID
            doc_id = root.get('DOC_ID', '')

            # Initialize contract data
            contract_data = {
                "source_file": filename,
                "daily_archive": daily_archive,
                "monthly_archive": monthly_archive,
                "extraction_timestamp": datetime.now(timezone.utc).isoformat(),
                "data_hash": hashlib.md5(xml_content).hexdigest(),
                "doc_id": doc_id
            }

            # Extract notice number
            notice_elem = root.find('.//ted:NOTICE_DATA/ted:NO_DOC_OJS', self.namespaces)
            if notice_elem is not None:
                contract_data["notice_number"] = notice_elem.text
                contract_data["contract_id"] = notice_elem.text
            else:
                contract_data["contract_id"] = doc_id or hashlib.md5(xml_content).hexdigest()[:16]

            # Extract publication date
            date_elem = root.find('.//ted:REF_OJS/ted:DATE_PUB', self.namespaces)
            if date_elem is not None:
                contract_data["publication_date"] = date_elem.text

            # Extract country
            country_elem = root.find('.//ted:ISO_COUNTRY', self.namespaces)
            if country_elem is not None:
                contract_data["country"] = country_elem.get('VALUE', '')

            # Extract contracting authority (multiple possible paths)
            ca_name = None
            for path in ['.//ted:CONTRACTING_BODY/ted:ADDRESS_CONTRACTING_BODY/ted:OFFICIALNAME',
                        './/ted:ML_AA_NAMES/ted:AA_NAME',
                        './/ted:TRANSLITERATIONS/ted:TRANSLITERATED_ADDR/ted:OFFICIALNAME']:
                elem = root.find(path, self.namespaces)
                if elem is not None and elem.text:
                    ca_name = elem.text
                    break
            contract_data["contracting_authority"] = ca_name

            # Extract contractor/winner
            contractor_name = None
            contractor_country = None
            for path in ['.//ted:CONTRACTOR/ted:ADDRESS_CONTRACTOR/ted:OFFICIALNAME',
                        './/ted:CONTRACTORS/ted:CONTRACTOR/ted:ADDRESS_CONTRACTOR/ted:OFFICIALNAME']:
                elem = root.find(path, self.namespaces)
                if elem is not None and elem.text:
                    contractor_name = elem.text
                    # Try to get contractor country
                    country_elem = root.find(path + '/../ted:COUNTRY', self.namespaces)
                    if country_elem is not None:
                        contractor_country = country_elem.get('VALUE', '')
                    break

            contract_data["contractor_name"] = contractor_name
            contract_data["contractor_country"] = contractor_country

            # Extract contract value
            value_elem = root.find('.//ted:VALUES/ted:VAL_TOTAL', self.namespaces)
            if value_elem is not None:
                try:
                    value_text = value_elem.text
                    if value_text:
                        contract_data["contract_value_eur"] = float(value_text)
                except:
                    pass

            # Extract title
            title_elem = root.find('.//ted:TITLE/ted:P', self.namespaces)
            if title_elem is not None:
                contract_data["contract_title"] = title_elem.text

            # Extract CPV codes
            cpv_codes = []
            for cpv_elem in root.findall('.//ted:CPV_CODE', self.namespaces):
                code = cpv_elem.get('CODE')
                if code:
                    cpv_codes.append(code)
            contract_data["cpv_codes"] = json.dumps(cpv_codes)

            # Get full text for pattern matching
            full_text = ET.tostring(root, encoding='unicode', method='text')

            # Check for Chinese connections
            china_check = self.check_chinese_patterns(full_text, contractor_name, contractor_country)
            contract_data["china_linked"] = china_check["found"]
            contract_data["china_patterns_found"] = json.dumps(china_check["patterns"])
            contract_data["china_confidence"] = china_check["confidence"]

            # Check for technology relevance
            tech_check = self.check_technology_keywords(full_text)
            contract_data["technology_related"] = tech_check["found"]
            contract_data["tech_keywords_found"] = json.dumps(tech_check["keywords"])

            # Check dual-use potential
            contract_data["dual_use_potential"] = self.check_dual_use(full_text, cpv_codes)

            # Only return if China-linked or tech-related
            if contract_data["china_linked"] or contract_data["technology_related"]:
                return contract_data

            return None

        except Exception as e:
            logger.debug(f"XML parsing error for {filename}: {e}")
            return None

    def check_chinese_patterns(self, text: str, contractor_name: str, contractor_country: str) -> Dict:
        """Check for Chinese patterns with confidence scoring"""
        text_lower = text.lower()
        found_patterns = []
        confidence = 0.0

        # Check contractor country first (highest confidence)
        if contractor_country and contractor_country in ['CN', 'CHN', 'HK', 'MO']:
            found_patterns.append(f"Country: {contractor_country}")
            confidence = 1.0

        # Check contractor name
        if contractor_name:
            contractor_lower = contractor_name.lower()
            for pattern in self.chinese_patterns:
                if pattern.lower() in contractor_lower:
                    found_patterns.append(pattern)
                    confidence = max(confidence, 0.9)

        # Check full text
        for pattern in self.chinese_patterns:
            if pattern.lower() in text_lower and pattern not in found_patterns:
                found_patterns.append(pattern)
                confidence = max(confidence, 0.7)

        return {
            "found": len(found_patterns) > 0,
            "patterns": found_patterns,
            "confidence": confidence
        }

    def check_technology_keywords(self, text: str) -> Dict:
        """Check for technology keywords"""
        text_lower = text.lower()
        found_keywords = []

        for keyword in self.tech_keywords:
            if keyword.lower() in text_lower:
                found_keywords.append(keyword)

        return {
            "found": len(found_keywords) > 0,
            "keywords": found_keywords
        }

    def check_dual_use(self, text: str, cpv_codes: List[str]) -> bool:
        """Check for dual-use potential"""
        dual_use_indicators = [
            "dual-use", "dual use", "military", "defense", "defence",
            "strategic", "critical", "export control", "wassenaar",
            "missile", "ITAR", "EAR", "munitions", "warfare"
        ]

        # Check text
        text_lower = text.lower()
        for indicator in dual_use_indicators:
            if indicator.lower() in text_lower:
                return True

        # Check CPV codes for sensitive categories
        # These are example CPV codes that might indicate dual-use
        sensitive_cpv_prefixes = [
            "35",  # Defence and security equipment
            "38",  # Laboratory equipment
            "31",  # Electrical equipment
            "32",  # Radio, television, communication
        ]

        for code in cpv_codes:
            for prefix in sensitive_cpv_prefixes:
                if code.startswith(prefix):
                    return True

        return False

    def save_contract(self, cursor: sqlite3.Cursor, contract_data: Dict):
        """Save contract to database"""
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO ted_china_contracts (
                    contract_id, doc_id, notice_number, publication_date, country,
                    contracting_authority, contracting_authority_country,
                    contractor_name, contractor_country,
                    contract_title, cpv_codes, contract_value_eur,
                    china_linked, china_patterns_found, china_confidence,
                    technology_related, tech_keywords_found, dual_use_potential,
                    source_file, daily_archive, monthly_archive,
                    extraction_timestamp, data_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                contract_data.get("contract_id"),
                contract_data.get("doc_id"),
                contract_data.get("notice_number"),
                contract_data.get("publication_date"),
                contract_data.get("country"),
                contract_data.get("contracting_authority"),
                contract_data.get("contracting_authority_country"),
                contract_data.get("contractor_name"),
                contract_data.get("contractor_country"),
                contract_data.get("contract_title"),
                contract_data.get("cpv_codes"),
                contract_data.get("contract_value_eur"),
                contract_data.get("china_linked"),
                contract_data.get("china_patterns_found"),
                contract_data.get("china_confidence"),
                contract_data.get("technology_related"),
                contract_data.get("tech_keywords_found"),
                contract_data.get("dual_use_potential"),
                contract_data.get("source_file"),
                contract_data.get("daily_archive"),
                contract_data.get("monthly_archive"),
                contract_data.get("extraction_timestamp"),
                contract_data.get("data_hash")
            ))

            # Track Chinese entities
            if contract_data.get("china_linked") and contract_data.get("contractor_name"):
                self.track_chinese_entity(cursor, contract_data)

        except sqlite3.IntegrityError:
            pass  # Duplicate, skip
        except Exception as e:
            logger.error(f"Database error: {e}")

    def track_chinese_entity(self, cursor: sqlite3.Cursor, contract_data: Dict):
        """Track Chinese entities for analysis"""
        entity_name = contract_data.get("contractor_name")
        if not entity_name:
            return

        # Check if entity exists
        cursor.execute('''
            SELECT entity_id, contracts_count, total_value_eur
            FROM ted_procurement_chinese_entities_found
            WHERE entity_name = ?
        ''', (entity_name,))

        result = cursor.fetchone()

        value = contract_data.get("contract_value_eur", 0) or 0

        if result:
            # Update existing
            cursor.execute('''
                UPDATE chinese_entities_found
                SET contracts_count = contracts_count + 1,
                    total_value_eur = total_value_eur + ?,
                    last_seen = ?
                WHERE entity_name = ?
            ''', (value, contract_data.get("publication_date"), entity_name))
        else:
            # Insert new
            cursor.execute('''
                INSERT INTO ted_procurement_chinese_entities_found
                (entity_name, first_seen, last_seen, contracts_count, total_value_eur)
                VALUES (?, ?, ?, 1, ?)
            ''', (entity_name, contract_data.get("publication_date"),
                  contract_data.get("publication_date"), value))

    def process_priority_months(self):
        """Process recent months with highest priority"""
        results = []

        # Process most recent data first
        priority_periods = [
            (2024, [1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12]),  # Skip August (corrupted)
            (2023, [12, 11, 10, 9, 8, 7])  # Recent 2023
        ]

        for year, months in priority_periods:
            for month in months:
                logger.info(f"Processing {year}-{month:02d}")
                result = self.process_year_month(year, month)
                results.append(result)

                # Check if we found enough Chinese contracts
                if sum(r.get("chinese_contracts", 0) for r in results) >= 100:
                    logger.info("Found sufficient Chinese contracts for analysis")
                    break

        return results

    def generate_comprehensive_report(self):
        """Generate comprehensive analysis report"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        report = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "database": self.db_path,
            "zero_fabrication_compliance": True,
            "data_source": "TED Europa Public Procurement Database"
        }

        # Overall statistics
        cursor.execute("SELECT COUNT(*) FROM ted_china_contracts")
        report["total_contracts_analyzed"] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM ted_china_contracts WHERE china_linked = 1")
        report["chinese_contracts_found"] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM ted_china_contracts WHERE technology_related = 1")
        report["technology_contracts"] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM ted_china_contracts WHERE dual_use_potential = 1")
        report["dual_use_contracts"] = cursor.fetchone()[0]

        # Total contract values
        cursor.execute('''
            SELECT SUM(contract_value_eur)
            FROM ted_china_contracts
            WHERE china_linked = 1 AND contract_value_eur IS NOT NULL
        ''')
        result = cursor.fetchone()[0]
        report["total_chinese_contract_value_eur"] = result if result else 0

        # Top Chinese contractors
        cursor.execute('''
            SELECT contractor_name, contractor_country,
                   COUNT(*) as contracts,
                   SUM(contract_value_eur) as total_value
            FROM ted_china_contracts
            WHERE china_linked = 1
            AND contractor_name IS NOT NULL
            GROUP BY contractor_name
            ORDER BY contracts DESC
            LIMIT 20
        ''')
        report["top_chinese_contractors"] = [
            {
                "name": row[0],
                "country": row[1],
                "contracts": row[2],
                "total_value_eur": row[3] if row[3] else 0
            }
            for row in cursor.fetchall()
        ]

        # Technology areas in Chinese contracts
        tech_areas = {}
        cursor.execute('''
            SELECT tech_keywords_found
            FROM ted_china_contracts
            WHERE china_linked = 1 AND technology_related = 1
        ''')
        for row in cursor.fetchall():
            if row[0]:
                keywords = json.loads(row[0])
                for keyword in keywords:
                    tech_areas[keyword] = tech_areas.get(keyword, 0) + 1

        report["technology_areas_chinese_contracts"] = sorted(
            [{"technology": k, "occurrences": v} for k, v in tech_areas.items()],
            key=lambda x: x["occurrences"],
            reverse=True
        )[:20]

        # Countries awarding to Chinese contractors
        cursor.execute('''
            SELECT country, COUNT(*) as contracts
            FROM ted_china_contracts
            WHERE china_linked = 1 AND country IS NOT NULL
            GROUP BY country
            ORDER BY contracts DESC
        ''')
        report["countries_awarding_to_china"] = [
            {"country": row[0], "contracts": row[1]}
            for row in cursor.fetchall()
        ]

        # Chinese entities summary
        cursor.execute('''
            SELECT entity_name, contracts_count, total_value_eur
            FROM ted_procurement_chinese_entities_found
            ORDER BY contracts_count DESC
            LIMIT 20
        ''')
        report["tracked_chinese_entities"] = [
            {
                "entity": row[0],
                "contracts": row[1],
                "total_value_eur": row[2] if row[2] else 0
            }
            for row in cursor.fetchall()
        ]

        conn.close()

        # Save report
        report_path = Path("C:/Projects/OSINT - Foresight/analysis/ted_china_analysis_report.json")
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"Report saved to {report_path}")
        return report


def main():
    """Main execution"""
    processor = TEDProcessorV3()

    logger.info("Starting TED China Risk Analysis")

    # Process priority months
    results = processor.process_priority_months()

    # Generate report
    report = processor.generate_comprehensive_report()

    print("\n=== TED CHINA RISK ANALYSIS REPORT ===")
    print(f"Total Contracts Analyzed: {report['total_contracts_analyzed']}")
    print(f"Chinese Contracts Found: {report['chinese_contracts_found']}")
    print(f"Technology Contracts: {report['technology_contracts']}")
    print(f"Dual-Use Contracts: {report['dual_use_contracts']}")
    print(f"Total Chinese Contract Value: €{report['total_chinese_contract_value_eur']:,.2f}")

    if report['top_chinese_contractors']:
        print("\n=== Top Chinese Contractors ===")
        for contractor in report['top_chinese_contractors'][:5]:
            print(f"- {contractor['name']}: {contractor['contracts']} contracts")

    return report


if __name__ == "__main__":
    main()

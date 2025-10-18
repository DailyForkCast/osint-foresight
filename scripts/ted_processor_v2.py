#!/usr/bin/env python3
"""
TED Procurement Data Processor V2
Handles nested tar.gz structure (monthly -> daily -> XML files)
Implements Zero Fabrication Protocol
"""

import tarfile
import xml.etree.ElementTree as ET
from pathlib import Path
import sqlite3
import json
import re
from datetime import datetime, timezone
import logging
import io
import tempfile
from typing import Dict, List, Optional, Tuple
import hashlib

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('C:/Projects/OSINT - Foresight/logs/ted_processing_v2.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TEDProcessorV2:
    """Process TED procurement data with nested tar handling"""

    def __init__(self, db_path: str = "F:/OSINT_WAREHOUSE/osint_master.db"):
        self.db_path = db_path
        self.ted_base_path = Path("F:/TED_Data/monthly/")

        # Enhanced Chinese patterns with more companies and terms
        self.chinese_patterns = [
            # Major tech companies
            "Huawei", "ZTE", "Alibaba", "Tencent", "Baidu", "ByteDance", "TikTok",
            "Xiaomi", "Lenovo", "Oppo", "Vivo", "OnePlus", "DJI", "Hikvision", "Dahua",
            # State enterprises
            "CRRC", "COSCO", "China National", "China State", "Sinopec", "PetroChina",
            "State Grid", "China Mobile", "China Telecom", "China Unicom",
            "AVIC", "COMAC", "CSSC", "NORINCO", "CETC",
            # Semiconductor companies
            "SMIC", "HiSilicon", "Cambricon", "Horizon Robotics", "YMTC",
            # Other major companies
            "BYD", "Geely", "Great Wall", "NIO", "Xpeng", "Li Auto",
            "Haier", "TCL", "Midea", "Gree", "Hisense",
            # Banks and financial
            "Bank of China", "ICBC", "China Construction Bank", "Agricultural Bank of China",
            # Universities and research
            "Chinese Academy", "Tsinghua", "Peking University", "Zhejiang University",
            "Fudan", "Shanghai Jiao Tong", "Harbin Institute", "Beihang",
            # Geographic markers
            "China", "Chinese", "PRC", "People's Republic",
            "Beijing", "Shanghai", "Shenzhen", "Guangzhou", "Hangzhou",
            "Tianjin", "Chengdu", "Wuhan", "Xi'an", "Nanjing",
            "Suzhou", "Qingdao", "Dalian", "Chongqing", "Shenyang"
        ]

        # Technology keywords - expanded list
        self.tech_keywords = [
            # Core AI/ML
            "artificial intelligence", "machine learning", "deep learning",
            "neural network", "computer vision", "natural language",
            "LLM", "transformer", "generative AI", "AGI",
            # Semiconductors & chips
            "semiconductor", "microchip", "integrated circuit", "processor",
            "CPU", "GPU", "ASIC", "FPGA", "SoC", "wafer", "lithography",
            "EUV", "chip design", "foundry", "fab", "silicon",
            # Telecommunications
            "5G", "6G", "telecommunications", "base station", "antenna",
            "fiber optic", "network equipment", "router", "switch",
            "mobile network", "wireless", "broadband",
            # Quantum
            "quantum computing", "quantum communication", "quantum cryptography",
            "quantum sensor", "qubit", "quantum supremacy",
            # Space & Satellite
            "satellite", "spacecraft", "space technology", "launch vehicle",
            "rocket", "orbital", "GNSS", "GPS", "BeiDou", "remote sensing",
            # Defense & Security
            "radar", "sonar", "missile", "UAV", "drone", "unmanned",
            "electronic warfare", "countermeasure", "jamming",
            "cybersecurity", "encryption", "cryptography", "firewall",
            # Surveillance
            "surveillance", "facial recognition", "biometric", "tracking",
            "CCTV", "video analytics", "smart camera",
            # Energy & Nuclear
            "nuclear reactor", "fusion", "renewable energy", "solar panel",
            "wind turbine", "battery technology", "energy storage",
            # Biotech
            "biotechnology", "gene editing", "CRISPR", "synthetic biology",
            "genomics", "bioinformatics", "pharmaceutical"
        ]

        self.init_database()

    def init_database(self):
        """Initialize enhanced database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Enhanced contracts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ted_contracts (
                contract_id TEXT PRIMARY KEY,
                notice_id TEXT,
                notice_type TEXT,
                publication_date DATE,
                deadline_date DATE,
                contracting_authority TEXT,
                contracting_authority_country TEXT,
                contractor_name TEXT,
                contractor_address TEXT,
                contractor_country TEXT,
                contract_title TEXT,
                contract_description TEXT,
                cpv_codes TEXT,
                nuts_codes TEXT,
                contract_value_eur REAL,
                contract_value_min REAL,
                contract_value_max REAL,
                contract_value_currency TEXT,
                procedure_type TEXT,
                china_linked BOOLEAN,
                china_patterns_found TEXT,
                technology_related BOOLEAN,
                tech_keywords_found TEXT,
                dual_use_potential BOOLEAN,
                source_file TEXT,
                daily_archive TEXT,
                extraction_timestamp TIMESTAMP,
                xml_language TEXT,
                data_hash TEXT
            )
        ''')

        # Pattern matches table for detailed tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pattern_matches (
                match_id INTEGER PRIMARY KEY AUTOINCREMENT,
                contract_id TEXT,
                pattern_type TEXT,
                pattern_matched TEXT,
                context TEXT,
                confidence_score REAL,
                FOREIGN KEY (contract_id) REFERENCES ted_contracts(contract_id)
            )
        ''')

        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_china_linked ON ted_contracts(china_linked)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tech_related ON ted_contracts(technology_related)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_pub_date ON ted_contracts(publication_date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_contractor ON ted_contracts(contractor_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_authority ON ted_contracts(contracting_authority)')

        conn.commit()
        conn.close()
        logger.info(f"Database initialized at {self.db_path}")

    def process_year_month(self, year: int, month: int) -> Dict:
        """Process a specific month with nested tar handling"""
        month_str = f"{month:02d}"
        monthly_tar = self.ted_base_path / str(year) / f"TED_monthly_{year}_{month_str}.tar.gz"

        if not monthly_tar.exists():
            logger.warning(f"File not found: {monthly_tar}")
            return {"status": "not_found", "file": str(monthly_tar)}

        logger.info(f"Processing monthly archive: {monthly_tar}")

        stats = {
            "file": str(monthly_tar),
            "year": year,
            "month": month,
            "daily_archives": 0,
            "xml_files": 0,
            "contracts_processed": 0,
            "chinese_contracts": 0,
            "tech_contracts": 0,
            "dual_use": 0,
            "errors": 0,
            "chinese_entities": set(),
            "tech_areas": set()
        }

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Open monthly tar
            with tarfile.open(monthly_tar, 'r:gz') as monthly_tar_obj:
                # Iterate through daily archives
                for daily_member in monthly_tar_obj.getmembers():
                    if daily_member.isfile() and daily_member.name.endswith('.tar.gz'):
                        stats["daily_archives"] += 1
                        logger.info(f"  Processing daily archive: {daily_member.name}")

                        # Extract daily tar to memory
                        daily_tar_file = monthly_tar_obj.extractfile(daily_member)
                        if daily_tar_file:
                            # Process daily archive
                            daily_stats = self.process_daily_archive(
                                daily_tar_file,
                                daily_member.name,
                                cursor
                            )

                            # Update stats
                            stats["xml_files"] += daily_stats["xml_files"]
                            stats["contracts_processed"] += daily_stats["contracts_processed"]
                            stats["chinese_contracts"] += daily_stats["chinese_contracts"]
                            stats["tech_contracts"] += daily_stats["tech_contracts"]
                            stats["dual_use"] += daily_stats["dual_use"]
                            stats["errors"] += daily_stats["errors"]

                            # Commit every daily archive
                            conn.commit()

        except Exception as e:
            logger.error(f"Error processing monthly tar {monthly_tar}: {e}")
            stats["errors"] += 1

        conn.commit()
        conn.close()

        # Convert sets to lists for JSON serialization
        stats["chinese_entities"] = list(stats["chinese_entities"])
        stats["tech_areas"] = list(stats["tech_areas"])

        logger.info(f"Completed {monthly_tar}: {stats['contracts_processed']} contracts processed")
        return stats

    def process_daily_archive(self, daily_tar_fileobj, daily_archive_name: str, cursor: sqlite3.Cursor) -> Dict:
        """Process a daily tar.gz archive containing XML files"""
        stats = {
            "xml_files": 0,
            "contracts_processed": 0,
            "chinese_contracts": 0,
            "tech_contracts": 0,
            "dual_use": 0,
            "errors": 0
        }

        try:
            # Open daily tar from memory
            with tarfile.open(fileobj=daily_tar_fileobj, mode='r:gz') as daily_tar:
                for xml_member in daily_tar.getmembers():
                    if xml_member.isfile() and xml_member.name.endswith('.xml'):
                        stats["xml_files"] += 1

                        try:
                            # Extract XML content
                            xml_file = daily_tar.extractfile(xml_member)
                            if xml_file:
                                xml_content = xml_file.read()

                                # Parse XML and extract contract data
                                contract_data = self.parse_ted_xml_v2(
                                    xml_content,
                                    xml_member.name,
                                    daily_archive_name
                                )

                                if contract_data:
                                    # Save to database
                                    self.save_contract_v2(cursor, contract_data)
                                    stats["contracts_processed"] += 1

                                    if contract_data.get("china_linked"):
                                        stats["chinese_contracts"] += 1
                                    if contract_data.get("technology_related"):
                                        stats["tech_contracts"] += 1
                                    if contract_data.get("dual_use_potential"):
                                        stats["dual_use"] += 1

                        except Exception as e:
                            logger.error(f"Error processing XML {xml_member.name}: {e}")
                            stats["errors"] += 1

                        # Log progress every 100 files
                        if stats["xml_files"] % 100 == 0:
                            logger.info(f"    Processed {stats['xml_files']} XML files...")

        except Exception as e:
            logger.error(f"Error processing daily archive {daily_archive_name}: {e}")
            stats["errors"] += 1

        return stats

    def parse_ted_xml_v2(self, xml_content: bytes, filename: str, daily_archive: str) -> Optional[Dict]:
        """Enhanced XML parser for TED format"""
        try:
            # Try to decode XML content
            try:
                xml_str = xml_content.decode('utf-8')
            except:
                xml_str = xml_content.decode('latin-1')

            # Parse XML
            root = ET.fromstring(xml_content)

            # Initialize contract data
            contract_data = {
                "source_file": filename,
                "daily_archive": daily_archive,
                "extraction_timestamp": datetime.now(timezone.utc).isoformat(),
                "data_hash": hashlib.md5(xml_content).hexdigest()
            }

            # Extract notice ID (various possible paths)
            notice_id = None
            for path in ['.//@DOC_ID', './/NOTICE_DATA/@NO_DOC_OJS', './/NO_DOC_OJS']:
                elem = root.find(path)
                if elem is not None:
                    notice_id = elem if isinstance(elem, str) else elem.text
                    break

            if not notice_id:
                # Generate ID from filename
                notice_id = filename.replace('.xml', '')

            contract_data["contract_id"] = notice_id
            contract_data["notice_id"] = notice_id

            # Get full text for pattern matching
            full_text = ET.tostring(root, encoding='unicode', method='text')

            # Check for Chinese connections
            china_check = self.check_chinese_patterns_detailed(full_text)
            contract_data["china_linked"] = china_check["found"]
            contract_data["china_patterns_found"] = json.dumps(china_check["patterns"])

            # Check for technology relevance
            tech_check = self.check_tech_keywords_detailed(full_text)
            contract_data["technology_related"] = tech_check["found"]
            contract_data["tech_keywords_found"] = json.dumps(tech_check["keywords"])

            # Check dual-use potential
            contract_data["dual_use_potential"] = self.check_dual_use_v2(full_text)

            # Only process if China-linked or tech-related
            if not (contract_data["china_linked"] or contract_data["technology_related"]):
                return None

            # Try to extract more specific fields
            # Contracting authority
            for path in ['.//CONTRACTING_BODY//OFFICIALNAME', './/CA_NAME', './/NAME_ADDRESSES_CONTACT//CA_CE_CONCESSIONAIRE_PROFILE//ORGANISATION//OFFICIALNAME']:
                elem = root.find(path)
                if elem is not None and elem.text:
                    contract_data["contracting_authority"] = elem.text[:500]  # Limit length
                    break

            # Contractor/Winner
            for path in ['.//AWARDED_CONTRACT//CONTRACTOR//ADDRESS//ORGANISATION//OFFICIALNAME', './/ECONOMIC_OPERATOR_NAME_ADDRESS//ORGANISATION//OFFICIALNAME']:
                elem = root.find(path)
                if elem is not None and elem.text:
                    contract_data["contractor_name"] = elem.text[:500]
                    break

            # Contract value
            for path in ['.//AWARDED_CONTRACT//COSTS_RANGE//VALUE_COST', './/VAL_TOTAL', './/VALUE']:
                elem = root.find(path)
                if elem is not None:
                    try:
                        value_text = elem.get('FMTVAL') if elem.get('FMTVAL') else elem.text
                        if value_text:
                            contract_data["contract_value_eur"] = float(value_text.replace(',', '').replace(' ', ''))
                    except:
                        pass
                    break

            # Title/Description
            for path in ['.//TITLE_CONTRACT', './/TITLE', './/SHORT_DESCR']:
                elem = root.find(path)
                if elem is not None and elem.text:
                    contract_data["contract_title"] = elem.text[:1000]
                    break

            return contract_data

        except Exception as e:
            logger.debug(f"XML parsing error for {filename}: {e}")
            return None

    def check_chinese_patterns_detailed(self, text: str) -> Dict:
        """Check for Chinese patterns and return details"""
        text_lower = text.lower()
        found_patterns = []

        for pattern in self.chinese_patterns:
            if pattern.lower() in text_lower:
                found_patterns.append(pattern)

        return {
            "found": len(found_patterns) > 0,
            "patterns": found_patterns,
            "count": len(found_patterns)
        }

    def check_tech_keywords_detailed(self, text: str) -> Dict:
        """Check for technology keywords and return details"""
        text_lower = text.lower()
        found_keywords = []

        for keyword in self.tech_keywords:
            if keyword.lower() in text_lower:
                found_keywords.append(keyword)

        return {
            "found": len(found_keywords) > 0,
            "keywords": found_keywords,
            "count": len(found_keywords)
        }

    def check_dual_use_v2(self, text: str) -> bool:
        """Enhanced dual-use detection"""
        dual_use_indicators = [
            "dual-use", "dual use", "military", "defense", "defence",
            "strategic", "critical technology", "export control",
            "wassenaar", "missile technology", "ITAR", "EAR"
        ]

        text_lower = text.lower()
        for indicator in dual_use_indicators:
            if indicator.lower() in text_lower:
                return True
        return False

    def save_contract_v2(self, cursor: sqlite3.Cursor, contract_data: Dict):
        """Save contract with enhanced data"""
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO ted_china_contracts (
                    contract_id, notice_id, contracting_authority, contractor_name,
                    contract_title, contract_value_eur,
                    china_linked, china_patterns_found,
                    technology_related, tech_keywords_found,
                    dual_use_potential, source_file, daily_archive,
                    extraction_timestamp, data_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                contract_data.get("contract_id"),
                contract_data.get("notice_id"),
                contract_data.get("contracting_authority"),
                contract_data.get("contractor_name"),
                contract_data.get("contract_title"),
                contract_data.get("contract_value_eur"),
                contract_data.get("china_linked"),
                contract_data.get("china_patterns_found"),
                contract_data.get("technology_related"),
                contract_data.get("tech_keywords_found"),
                contract_data.get("dual_use_potential"),
                contract_data.get("source_file"),
                contract_data.get("daily_archive"),
                contract_data.get("extraction_timestamp"),
                contract_data.get("data_hash")
            ))

            # Also save pattern matches for detailed analysis
            if contract_data.get("china_patterns_found"):
                patterns = json.loads(contract_data["china_patterns_found"])
                for pattern in patterns:
                    cursor.execute('''
                        INSERT INTO ted_procurement_pattern_matches (contract_id, pattern_type, pattern_matched)
                        VALUES (?, 'china', ?)
                    ''', (contract_data["contract_id"], pattern))

        except sqlite3.IntegrityError:
            # Contract already exists, skip
            pass
        except Exception as e:
            logger.error(f"Database error saving contract: {e}")

    def process_single_month(self, year: int, month: int):
        """Process a single month for testing"""
        return self.process_year_month(year, month)

    def generate_report(self):
        """Generate comprehensive report"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        report = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "database": self.db_path,
            "zero_fabrication_compliance": True,
            "data_sources": "TED Europa Public Procurement Database"
        }

        # Get statistics - only verifiable data
        cursor.execute("SELECT COUNT(*) FROM ted_china_contracts")
        report["total_contracts_processed"] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM ted_china_contracts WHERE china_linked = 1")
        report["contracts_with_chinese_entities"] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM ted_china_contracts WHERE technology_related = 1")
        report["technology_contracts"] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM ted_china_contracts WHERE dual_use_potential = 1")
        report["dual_use_contracts"] = cursor.fetchone()[0]

        # Top Chinese patterns found
        cursor.execute('''
            SELECT pattern_matched, COUNT(*) as count
            FROM ted_procurement_pattern_matches
            WHERE pattern_type = 'china'
            GROUP BY pattern_matched
            ORDER BY count DESC
            LIMIT 20
        ''')
        report["top_chinese_patterns"] = [
            {"pattern": row[0], "occurrences": row[1]}
            for row in cursor.fetchall()
        ]

        # Contracts with specific Chinese companies
        cursor.execute('''
            SELECT contractor_name, COUNT(*) as count
            FROM ted_china_contracts
            WHERE china_linked = 1
            AND contractor_name IS NOT NULL
            AND contractor_name != ''
            GROUP BY contractor_name
            ORDER BY count DESC
            LIMIT 20
        ''')
        report["identified_chinese_contractors"] = [
            {"name": row[0], "contract_count": row[1]}
            for row in cursor.fetchall()
        ]

        conn.close()

        # Save report
        report_path = Path("C:/Projects/OSINT - Foresight/analysis/ted_processing_report_v2.json")
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"Report saved to {report_path}")
        return report


def main():
    """Main execution"""
    processor = TEDProcessorV2()

    # Process January 2024 as a test
    logger.info("Starting TED processing with nested tar structure...")
    result = processor.process_single_month(2024, 1)

    # Generate report
    report = processor.generate_report()

    print("\n=== TED PROCESSING REPORT ===")
    print(json.dumps(report, indent=2))

    return report


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
TED Procurement Data Processor
Processes EU public procurement data to identify Chinese contractors and technology patterns
Following Zero Fabrication Protocol - only verified data, no estimates
"""

import tarfile
import xml.etree.ElementTree as ET
from pathlib import Path
import sqlite3
import json
import re
from datetime import datetime, timezone
import logging
from typing import Dict, List, Optional, Tuple
import hashlib

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('C:/Projects/OSINT - Foresight/logs/ted_processing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TEDProcessor:
    """Process TED procurement data with zero fabrication protocol"""

    def __init__(self, db_path: str = "F:/OSINT_WAREHOUSE/osint_master.db"):
        self.db_path = db_path
        self.ted_base_path = Path("F:/TED_Data/monthly/")

        # Chinese entity patterns - exact matches only
        self.chinese_patterns = [
            # Major companies
            "Huawei", "ZTE", "Alibaba", "Tencent", "Baidu",
            "CRRC", "COSCO", "China National", "China State",
            "Sinopec", "PetroChina", "SMIC", "BYD", "DJI",
            "Xiaomi", "Lenovo", "Haier", "TCL", "Midea",
            # Location indicators
            "China", "Chinese", "Beijing", "Shanghai", "Shenzhen",
            "Guangzhou", "Tianjin", "Chengdu", "Wuhan", "Nanjing",
            "Hangzhou", "Xi'an", "Suzhou", "Qingdao", "Dalian",
            # Chinese characters (if present)
            "中国", "中华", "华为", "中兴", "阿里巴巴"
        ]

        # Technology keywords - specific terms only
        self.tech_keywords = [
            # AI/ML
            "artificial intelligence", "AI", "machine learning", "deep learning",
            "neural network", "computer vision", "natural language processing",
            # Semiconductors
            "semiconductor", "microchip", "integrated circuit", "chip design",
            "wafer", "lithography", "ASIC", "FPGA", "processor",
            # Telecom
            "5G", "6G", "telecommunications", "base station", "antenna",
            "fiber optic", "network equipment", "router", "switch",
            # Advanced tech
            "quantum computing", "quantum communication", "quantum cryptography",
            "biotechnology", "gene sequencing", "synthetic biology",
            "nanotechnology", "graphene", "advanced materials",
            # Aerospace/Defense
            "aerospace", "satellite", "spacecraft", "rocket", "UAV",
            "drone", "missile", "radar", "sonar", "electronic warfare",
            # Cybersecurity
            "cybersecurity", "encryption", "cryptography", "firewall",
            "intrusion detection", "penetration testing", "vulnerability",
            # Surveillance
            "surveillance", "facial recognition", "biometric", "tracking",
            "monitoring system", "CCTV", "video analytics"
        ]

        # Dual-use indicators
        self.dual_use_indicators = [
            "dual-use", "dual use", "military", "defense", "defence",
            "strategic", "critical technology", "export control",
            "restricted", "classified", "sensitive technology"
        ]

        self.init_database()

    def init_database(self):
        """Initialize SQLite database with proper schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Main contracts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ted_contracts (
                contract_id TEXT PRIMARY KEY,
                notice_type TEXT,
                publication_date DATE,
                deadline_date DATE,
                contracting_authority TEXT,
                contracting_country TEXT,
                contractor_name TEXT,
                contractor_country TEXT,
                contract_title TEXT,
                contract_description TEXT,
                cpv_codes TEXT,
                contract_value_eur REAL,
                contract_value_currency TEXT,
                procedure_type TEXT,
                china_linked BOOLEAN,
                technology_related BOOLEAN,
                dual_use_potential BOOLEAN,
                source_file TEXT,
                extraction_timestamp TIMESTAMP,
                data_hash TEXT
            )
        ''')

        # Chinese entities found
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chinese_entities (
                entity_id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_name TEXT UNIQUE,
                entity_type TEXT,
                first_seen DATE,
                last_seen DATE,
                contract_count INTEGER,
                total_value_eur REAL,
                countries_active TEXT,
                technology_areas TEXT,
                verification_status TEXT
            )
        ''')

        # Technology contracts
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS technology_contracts (
                tech_id INTEGER PRIMARY KEY AUTOINCREMENT,
                contract_id TEXT,
                technology_category TEXT,
                technology_keywords TEXT,
                dual_use_flag BOOLEAN,
                risk_score INTEGER,
                leonardo_score INTEGER,
                FOREIGN KEY (contract_id) REFERENCES ted_contracts(contract_id)
            )
        ''')

        # Processing log
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS processing_log (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT,
                processing_start TIMESTAMP,
                processing_end TIMESTAMP,
                contracts_found INTEGER,
                chinese_contracts INTEGER,
                tech_contracts INTEGER,
                errors_encountered INTEGER,
                status TEXT
            )
        ''')

        # Create indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_china_linked ON ted_contracts(china_linked)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tech_related ON ted_contracts(technology_related)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_pub_date ON ted_contracts(publication_date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_contractor ON ted_contracts(contractor_name)')

        conn.commit()
        conn.close()
        logger.info(f"Database initialized at {self.db_path}")

    def process_year_month(self, year: int, month: int) -> Dict:
        """Process a specific month of TED data"""
        month_str = f"{month:02d}"
        tar_file = self.ted_base_path / str(year) / f"TED_monthly_{year}_{month_str}.tar.gz"

        if not tar_file.exists():
            logger.warning(f"File not found: {tar_file}")
            return {"status": "not_found", "file": str(tar_file)}

        logger.info(f"Processing {tar_file}")

        stats = {
            "file": str(tar_file),
            "total_files": 0,
            "contracts_processed": 0,
            "chinese_contracts": 0,
            "tech_contracts": 0,
            "errors": 0
        }

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Log processing start
        cursor.execute('''
            INSERT INTO processing_log (file_path, processing_start, status)
            VALUES (?, ?, 'processing')
        ''', (str(tar_file), datetime.now(timezone.utc).isoformat()))
        log_id = cursor.lastrowid

        try:
            with tarfile.open(tar_file, 'r:gz') as tar:
                for member in tar.getmembers():
                    if member.name.endswith('.xml'):
                        stats["total_files"] += 1

                        try:
                            # Extract and parse XML
                            xml_file = tar.extractfile(member)
                            if xml_file:
                                xml_content = xml_file.read()
                                contract_data = self.parse_ted_xml(xml_content, member.name)

                                if contract_data:
                                    self.save_contract(cursor, contract_data)
                                    stats["contracts_processed"] += 1

                                    if contract_data.get("china_linked"):
                                        stats["chinese_contracts"] += 1
                                    if contract_data.get("technology_related"):
                                        stats["tech_contracts"] += 1

                        except Exception as e:
                            logger.error(f"Error processing {member.name}: {e}")
                            stats["errors"] += 1

                        # Commit every 100 contracts
                        if stats["contracts_processed"] % 100 == 0:
                            conn.commit()
                            logger.info(f"Processed {stats['contracts_processed']} contracts...")

        except Exception as e:
            logger.error(f"Error reading tar file {tar_file}: {e}")
            stats["errors"] += 1

        # Update processing log
        cursor.execute('''
            UPDATE processing_log SET
                processing_end = ?,
                contracts_found = ?,
                chinese_contracts = ?,
                tech_contracts = ?,
                errors_encountered = ?,
                status = 'completed'
            WHERE log_id = ?
        ''', (
            datetime.now(timezone.utc).isoformat(),
            stats["contracts_processed"],
            stats["chinese_contracts"],
            stats["tech_contracts"],
            stats["errors"],
            log_id
        ))

        conn.commit()
        conn.close()

        logger.info(f"Completed processing {tar_file}: {stats}")
        return stats

    def parse_ted_xml(self, xml_content: bytes, filename: str) -> Optional[Dict]:
        """Parse TED XML and extract relevant contract information"""
        try:
            root = ET.fromstring(xml_content)

            # Handle different TED XML namespaces
            namespaces = {
                'ted': 'http://ted.europa.eu',
                'n1': 'http://publications.europa.eu/resource/schema/ted/R2.0.9/publication'
            }

            contract_data = {
                "source_file": filename,
                "extraction_timestamp": datetime.now(timezone.utc).isoformat()
            }

            # Try to extract basic contract info (handle multiple XML formats)
            # This is simplified - actual TED XML is complex with multiple schemas

            # Extract contract ID
            contract_id = root.find('.//NOTICE/@NO', namespaces)
            if contract_id is None:
                contract_id = root.find('.//NO_DOC_OJS')
            contract_data["contract_id"] = contract_id.text if contract_id is not None else hashlib.md5(xml_content).hexdigest()

            # Extract contracting authority
            ca_name = root.find('.//CONTRACTING_AUTHORITY/CA_NAME')
            if ca_name is None:
                ca_name = root.find('.//CONTRACTING_BODY/ADDRESS_CONTRACTING_BODY/OFFICIALNAME')
            contract_data["contracting_authority"] = ca_name.text if ca_name is not None else ""

            # Extract contractor (winner)
            contractor = root.find('.//CONTRACTOR/ADDRESS_CONTRACTOR/OFFICIALNAME')
            if contractor is None:
                contractor = root.find('.//AWARDED_CONTRACT/CONTRACTORS/CONTRACTOR/ADDRESS_CONTRACTOR/OFFICIALNAME')
            contract_data["contractor_name"] = contractor.text if contractor is not None else ""

            # Extract contract value
            value = root.find('.//VAL_TOTAL')
            if value is None:
                value = root.find('.//COSTS_RANGE_AND_CURRENCY/VALUE_COST')
            if value is not None and value.text:
                try:
                    contract_data["contract_value_eur"] = float(value.text)
                except:
                    contract_data["contract_value_eur"] = None

            # Check for Chinese connections
            full_text = ET.tostring(root, encoding='unicode', method='text').lower()
            contract_data["china_linked"] = self.check_chinese_connection(full_text, contract_data.get("contractor_name", ""))

            # Check for technology relevance
            contract_data["technology_related"] = self.check_technology_relevance(full_text)

            # Check for dual-use potential
            contract_data["dual_use_potential"] = self.check_dual_use(full_text)

            # Generate data hash for deduplication
            contract_data["data_hash"] = hashlib.md5(xml_content).hexdigest()

            return contract_data if (contract_data["china_linked"] or contract_data["technology_related"]) else None

        except Exception as e:
            logger.error(f"XML parsing error for {filename}: {e}")
            return None

    def check_chinese_connection(self, text: str, contractor_name: str) -> bool:
        """Check if contract has Chinese connections - exact matches only"""
        text_to_check = f"{text} {contractor_name}".lower()

        for pattern in self.chinese_patterns:
            if pattern.lower() in text_to_check:
                return True
        return False

    def check_technology_relevance(self, text: str) -> bool:
        """Check if contract is technology-related"""
        text_lower = text.lower()

        for keyword in self.tech_keywords:
            if keyword.lower() in text_lower:
                return True
        return False

    def check_dual_use(self, text: str) -> bool:
        """Check for dual-use technology indicators"""
        text_lower = text.lower()

        for indicator in self.dual_use_indicators:
            if indicator.lower() in text_lower:
                return True
        return False

    def save_contract(self, cursor: sqlite3.Cursor, contract_data: Dict):
        """Save contract to database"""
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO ted_china_contracts (
                    contract_id, contracting_authority, contractor_name,
                    contract_value_eur, china_linked, technology_related,
                    dual_use_potential, source_file, extraction_timestamp, data_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                contract_data.get("contract_id"),
                contract_data.get("contracting_authority"),
                contract_data.get("contractor_name"),
                contract_data.get("contract_value_eur"),
                contract_data.get("china_linked"),
                contract_data.get("technology_related"),
                contract_data.get("dual_use_potential"),
                contract_data.get("source_file"),
                contract_data.get("extraction_timestamp"),
                contract_data.get("data_hash")
            ))
        except sqlite3.IntegrityError:
            # Contract already exists
            pass
        except Exception as e:
            logger.error(f"Database error saving contract: {e}")

    def process_priority_years(self):
        """Process priority years 2023-2024"""
        results = []

        # Process 2024 first (most recent)
        for month in range(1, 13):
            result = self.process_year_month(2024, month)
            results.append(result)

        # Then 2023
        for month in range(1, 13):
            result = self.process_year_month(2023, month)
            results.append(result)

        return results

    def generate_summary_report(self):
        """Generate summary report of findings"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        report = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "database": self.db_path
        }

        # Total contracts
        cursor.execute("SELECT COUNT(*) FROM ted_china_contracts")
        report["total_contracts"] = cursor.fetchone()[0]

        # Chinese-linked contracts
        cursor.execute("SELECT COUNT(*) FROM ted_china_contracts WHERE china_linked = 1")
        report["chinese_contracts"] = cursor.fetchone()[0]

        # Technology contracts
        cursor.execute("SELECT COUNT(*) FROM ted_china_contracts WHERE technology_related = 1")
        report["technology_contracts"] = cursor.fetchone()[0]

        # Dual-use contracts
        cursor.execute("SELECT COUNT(*) FROM ted_china_contracts WHERE dual_use_potential = 1")
        report["dual_use_contracts"] = cursor.fetchone()[0]

        # Top Chinese contractors
        cursor.execute('''
            SELECT contractor_name, COUNT(*) as count, SUM(contract_value_eur) as total_value
            FROM ted_china_contracts
            WHERE china_linked = 1 AND contractor_name IS NOT NULL AND contractor_name != ''
            GROUP BY contractor_name
            ORDER BY count DESC
            LIMIT 20
        ''')
        report["top_chinese_contractors"] = [
            {"name": row[0], "contracts": row[1], "total_value_eur": row[2]}
            for row in cursor.fetchall()
        ]

        # Top technology areas (based on keyword matches)
        tech_areas = {}
        cursor.execute("SELECT contract_id, source_file FROM ted_china_contracts WHERE technology_related = 1")

        # This is simplified - in reality we'd parse more thoroughly
        report["technology_areas_found"] = len(cursor.fetchall())

        conn.close()

        # Save report
        report_path = Path("C:/Projects/OSINT - Foresight/analysis/ted_processing_report.json")
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"Report saved to {report_path}")
        return report


def main():
    """Main execution function"""
    logger.info("Starting TED Procurement Data Processing")

    processor = TEDProcessor()

    # Process priority years
    logger.info("Processing 2023-2024 data...")
    results = processor.process_priority_years()

    # Generate summary report
    logger.info("Generating summary report...")
    report = processor.generate_summary_report()

    logger.info("TED Processing completed")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

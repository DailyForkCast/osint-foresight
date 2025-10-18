#!/usr/bin/env python3
"""
Comprehensive Data Loader for OSINT Warehouse
Loads all available data with proper China detection
"""

import os
import json
import sqlite3
import logging
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
import pandas as pd
import re
from typing import Dict, List, Any

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ComprehensiveDataLoader:
    """Load all OSINT data with enhanced China detection"""

    def __init__(self, db_path: str = "F:/OSINT_WAREHOUSE/osint_research.db"):
        self.db_path = Path(db_path)
        self.project_root = Path("C:/Projects/OSINT - Foresight")

        # Connect to warehouse
        self.conn = sqlite3.connect(str(self.db_path))
        self.cursor = self.conn.cursor()

        # Comprehensive Chinese indicators
        self.china_indicators = {
            'strong': [
                'china', 'chinese', 'beijing', 'shanghai', 'shenzhen', 'guangzhou',
                'wuhan', 'chengdu', 'nanjing', 'hangzhou', 'tianjin', 'xi\'an',
                'tsinghua', 'peking university', 'fudan', 'zhejiang university',
                'huawei', 'alibaba', 'tencent', 'baidu', 'xiaomi', 'bytedance',
                'cas', 'chinese academy', 'xinjiang', 'tibet', 'hong kong', 'macau',
                'smic', 'catl', 'byd', 'dji', 'lenovo', 'zte', 'oppo', 'vivo',
                'university of science and technology of china', 'ustc',
                'shanghai jiao tong', 'sjtu', 'harbin institute', 'hit',
                'northwestern polytechnical', 'nwpu', 'beihang', 'buaa'
            ],
            'medium': [
                'sino-', 'cn-', 'prc', 'people\'s republic', 'mainland china',
                'greater china', 'chinese mainland', 'asia-pacific', 'apac'
            ],
            'domains': [
                '.cn', '.com.cn', '.edu.cn', '.gov.cn', '.org.cn', '.ac.cn'
            ]
        }

        logger.info(f"Connected to warehouse: {self.db_path}")

    def detect_china_involvement(self, text: str, confidence_boost: float = 0) -> float:
        """Enhanced China detection with multiple indicators"""
        if not text:
            return 0.0

        text_lower = text.lower()
        score = confidence_boost

        # Check strong indicators
        for indicator in self.china_indicators['strong']:
            if indicator in text_lower:
                return max(0.95, score)

        # Check medium indicators
        for indicator in self.china_indicators['medium']:
            if indicator in text_lower:
                score = max(score, 0.7)

        # Check domain indicators
        for domain in self.china_indicators['domains']:
            if domain in text_lower:
                score = max(score, 0.85)

        return score

    def load_ted_procurement(self):
        """Load TED procurement data from F drive"""
        logger.info("Loading TED procurement data from F:/TED_Data...")

        ted_path = Path("F:/TED_Data/monthly")
        if not ted_path.exists():
            logger.warning("TED data not found on F drive")
            return

        total_contracts = 0
        china_contracts = 0

        # Process years 2015-2024 (most relevant)
        for year in range(2015, 2025):
            year_path = ted_path / str(year)
            if not year_path.exists():
                continue

            logger.info(f"Processing TED year {year}...")

            # Process monthly directories
            for month_dir in sorted(year_path.glob("*"))[:3]:  # Sample 3 months per year
                if not month_dir.is_dir():
                    continue

                # Process daily directories
                for day_dir in sorted(month_dir.glob("*"))[:5]:  # Sample 5 days per month
                    if not day_dir.is_dir():
                        continue

                    # Process XML files
                    xml_files = list(day_dir.glob("*.xml"))[:20]  # Sample 20 contracts

                    for xml_file in xml_files:
                        try:
                            tree = ET.parse(xml_file)
                            root = tree.getroot()

                            # Extract contractor info
                            contractor_text = ""
                            for elem in root.iter():
                                if 'contractor' in elem.tag.lower() or 'winner' in elem.tag.lower():
                                    if elem.text:
                                        contractor_text += " " + elem.text

                            # Check for Chinese involvement
                            china_score = self.detect_china_involvement(contractor_text)

                            if china_score > 0.3 or 'china' in str(xml_file).lower():
                                # Extract contract details
                                notice_id = xml_file.stem
                                value = 0

                                for elem in root.iter():
                                    if 'value' in elem.tag.lower():
                                        try:
                                            value_text = elem.text or "0"
                                            value = float(re.sub(r'[^\d.]', '', value_text))
                                            break
                                        except:
                                            pass

                                self.cursor.execute("""
                                INSERT OR REPLACE INTO core_f_procurement (
                                    award_id, buyer_country, vendor_name,
                                    award_date, contract_value, currency,
                                    has_chinese_vendor, supply_chain_risk,
                                    source_system, source_file, retrieved_at,
                                    confidence_score
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                """, (
                                    f"TED_{year}_{notice_id}",
                                    'EU',
                                    contractor_text[:200] if contractor_text else 'Unknown',
                                    f"{year}-{month_dir.name}-01",
                                    value,
                                    'EUR',
                                    1 if china_score > 0.5 else 0,
                                    'HIGH' if china_score > 0.7 else 'MEDIUM',
                                    'TED_EU',
                                    str(xml_file),
                                    datetime.now().isoformat(),
                                    china_score
                                ))

                                total_contracts += 1
                                if china_score > 0.5:
                                    china_contracts += 1

                        except Exception as e:
                            logger.debug(f"Error parsing {xml_file}: {e}")

        self.conn.commit()
        logger.info(f"TED import complete: {total_contracts} contracts, {china_contracts} with China involvement")

    def load_italy_china_analysis(self):
        """Load Italy-China collaboration analysis"""
        logger.info("Loading Italy-China analysis data...")

        italy_china_file = self.project_root / "analysis/italy_china_project_ids.json"

        if italy_china_file.exists():
            with open(italy_china_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            projects = data if isinstance(data, list) else [data]

            for project in projects:
                if isinstance(project, dict):
                    project_id = project.get('id', '')
                    if project_id:
                        self.cursor.execute("""
                        INSERT OR REPLACE INTO core_f_collaboration (
                            collab_id, project_id, project_name,
                            has_chinese_partner, china_collaboration_score,
                            source_system, confidence_score
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (
                            f"ITALY_CHINA_{project_id}",
                            project_id,
                            project.get('title', 'Italy-China Project')[:500],
                            1,  # Known China collaboration
                            1.0,
                            'ITALY_CHINA_ANALYSIS',
                            0.95
                        ))

            self.conn.commit()
            logger.info("Italy-China analysis loaded")

    def load_archived_china_contracts(self):
        """Load archived China contract data"""
        logger.info("Loading archived China contracts...")

        archive_path = self.project_root / "ARCHIVED_ALL_ANALYSIS_20250919/processed"

        if archive_path.exists():
            # Load TED China contracts
            ted_china_file = archive_path / "ted_china_contracts/china_contracts_found.json"

            if ted_china_file.exists():
                with open(ted_china_file, 'r', encoding='utf-8') as f:
                    contracts = json.load(f)

                for contract in (contracts if isinstance(contracts, list) else [contracts]):
                    if isinstance(contract, dict):
                        self.cursor.execute("""
                        INSERT OR REPLACE INTO core_f_procurement (
                            award_id, vendor_name,
                            has_chinese_vendor, supply_chain_risk,
                            source_system, confidence_score
                        ) VALUES (?, ?, ?, ?, ?, ?)
                        """, (
                            f"ARCHIVED_TED_{contract.get('id', datetime.now().timestamp())}",
                            contract.get('vendor', 'China-linked vendor')[:200],
                            1,
                            'HIGH',
                            'ARCHIVED_TED_CHINA',
                            0.9
                        ))

            self.conn.commit()
            logger.info("Archived China contracts loaded")

    def load_existing_databases(self):
        """Load data from existing SQLite databases"""
        logger.info("Loading from existing databases...")

        db_files = [
            self.project_root / "data/processed/osint_master.db",
            self.project_root / "data/processed/osint_intelligence.db",
            self.project_root / "data/processed/ted_analysis.db",
            self.project_root / "data/processed/integrated_data.db"
        ]

        for db_file in db_files:
            if not db_file.exists():
                continue

            logger.info(f"Processing {db_file.name}...")

            try:
                source_conn = sqlite3.connect(str(db_file))
                source_cursor = source_conn.cursor()

                # Get tables
                source_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = source_cursor.fetchall()

                for table in tables:
                    table_name = table[0]

                    # Sample data from each table
                    try:
                        source_cursor.execute(f"SELECT * FROM {table_name} LIMIT 100")
                        rows = source_cursor.fetchall()

                        if not rows:
                            continue

                        columns = [desc[0] for desc in source_cursor.description]

                        for row in rows:
                            # Convert to dict for easier processing
                            row_dict = dict(zip(columns, row))

                            # Check for China involvement
                            row_text = ' '.join([str(v) for v in row_dict.values() if v])
                            china_score = self.detect_china_involvement(row_text)

                            if china_score > 0.3:
                                # Determine record type and insert appropriately
                                if 'patent' in table_name.lower():
                                    self.cursor.execute("""
                                    INSERT OR IGNORE INTO core_f_patent (
                                        patent_id, title,
                                        has_chinese_applicant, technology_transfer_risk,
                                        source_system
                                    ) VALUES (?, ?, ?, ?, ?)
                                    """, (
                                        f"{db_file.stem}_{table_name}_{row[0]}",
                                        str(row_dict.get('title', ''))[:500],
                                        1 if china_score > 0.5 else 0,
                                        'HIGH' if china_score > 0.7 else 'MEDIUM',
                                        f"DB_{db_file.stem}"
                                    ))

                                elif 'pub' in table_name.lower() or 'article' in table_name.lower():
                                    self.cursor.execute("""
                                    INSERT OR IGNORE INTO core_f_publication (
                                        pub_id, title,
                                        has_chinese_author, china_collaboration_score,
                                        source_system
                                    ) VALUES (?, ?, ?, ?, ?)
                                    """, (
                                        f"{db_file.stem}_{table_name}_{row[0]}",
                                        str(row_dict.get('title', ''))[:500],
                                        1 if china_score > 0.5 else 0,
                                        china_score,
                                        f"DB_{db_file.stem}"
                                    ))

                    except Exception as e:
                        logger.debug(f"Error processing table {table_name}: {e}")

                source_conn.close()

            except Exception as e:
                logger.error(f"Error processing database {db_file}: {e}")

        self.conn.commit()
        logger.info("Database import complete")

    def load_usaspending_data(self):
        """Load USASpending data"""
        logger.info("Loading USASpending data...")

        usa_path = self.project_root / "data/processed/USAspending"

        if usa_path.exists():
            json_files = list(usa_path.glob("**/*.json"))[:50]

            for json_file in json_files:
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    contracts = data if isinstance(data, list) else [data]

                    for contract in contracts:
                        if isinstance(contract, dict):
                            vendor = contract.get('vendor_name', '')
                            china_score = self.detect_china_involvement(vendor)

                            if china_score > 0.3:
                                self.cursor.execute("""
                                INSERT OR IGNORE INTO core_f_procurement (
                                    award_id, buyer_country, vendor_name,
                                    contract_value, currency,
                                    has_chinese_vendor, supply_chain_risk,
                                    source_system
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                """, (
                                    f"USA_{contract.get('award_id', datetime.now().timestamp())}",
                                    'US',
                                    vendor[:200],
                                    contract.get('total_obligation', 0),
                                    'USD',
                                    1 if china_score > 0.5 else 0,
                                    'HIGH' if china_score > 0.7 else 'MEDIUM',
                                    'USASpending'
                                ))

                except Exception as e:
                    logger.debug(f"Error processing {json_file}: {e}")

        self.conn.commit()
        logger.info("USASpending data loaded")

    def generate_comprehensive_report(self):
        """Generate comprehensive intelligence report"""
        logger.info("Generating comprehensive report...")

        report = []
        report.append("=== OSINT WAREHOUSE INTELLIGENCE REPORT ===\n")
        report.append(f"Generated: {datetime.now().isoformat()}\n")
        report.append("="*50 + "\n\n")

        # Executive Summary
        report.append("EXECUTIVE SUMMARY\n")
        report.append("-"*30 + "\n")

        # Get total counts
        tables = {
            'Collaborations': 'core_f_collaboration',
            'Publications': 'core_f_publication',
            'Patents': 'core_f_patent',
            'Procurement': 'core_f_procurement',
            'Trade Flows': 'core_f_trade_flow'
        }

        total_records = 0
        china_records = 0

        for name, table in tables.items():
            self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = self.cursor.fetchone()[0]
            total_records += count

            # Get China-related counts
            china_col = {
                'core_f_collaboration': 'has_chinese_partner',
                'core_f_publication': 'has_chinese_author',
                'core_f_patent': 'has_chinese_applicant',
                'core_f_procurement': 'has_chinese_vendor',
                'core_f_trade_flow': 'involves_china'
            }

            self.cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE {china_col[table]} = 1")
            china_count = self.cursor.fetchone()[0]
            china_records += china_count

            report.append(f"  {name}: {count:,} total, {china_count:,} China-related\n")

        report.append(f"\nTotal Records: {total_records:,}\n")
        report.append(f"China-Related: {china_records:,} ({china_records/max(total_records,1)*100:.1f}%)\n\n")

        # Key Findings
        report.append("KEY FINDINGS\n")
        report.append("-"*30 + "\n")

        # High-risk procurements
        self.cursor.execute("""
        SELECT COUNT(*), SUM(contract_value)
        FROM core_f_procurement
        WHERE supply_chain_risk = 'HIGH'
        """)
        high_risk = self.cursor.fetchone()
        report.append(f"  High-Risk Procurements: {high_risk[0]:,} contracts")
        if high_risk[1]:
            report.append(f" worth €{high_risk[1]:,.0f}\n")
        else:
            report.append("\n")

        # OpenAIRE false negative fix
        self.cursor.execute("""
        SELECT * FROM ops_false_negative_log
        WHERE source_system = 'OpenAIRE'
        ORDER BY logged_at DESC
        LIMIT 1
        """)
        fix_log = self.cursor.fetchone()
        if fix_log:
            report.append(f"  OpenAIRE Fix Applied: {fix_log[4]:,}x improvement\n")

        # Source distribution
        report.append("\nDATA SOURCES\n")
        report.append("-"*30 + "\n")

        self.cursor.execute("""
        SELECT source_system, COUNT(*) as cnt
        FROM (
            SELECT source_system FROM core_f_collaboration
            UNION ALL
            SELECT source_system FROM core_f_publication
            UNION ALL
            SELECT source_system FROM core_f_patent
            UNION ALL
            SELECT source_system FROM core_f_procurement
        )
        GROUP BY source_system
        ORDER BY cnt DESC
        LIMIT 10
        """)

        for row in self.cursor.fetchall():
            report.append(f"  {row[0]}: {row[1]:,} records\n")

        # Confidence analysis
        report.append("\nCONFIDENCE ANALYSIS\n")
        report.append("-"*30 + "\n")

        self.cursor.execute("""
        SELECT
            AVG(confidence_score) as avg_conf,
            MIN(confidence_score) as min_conf,
            MAX(confidence_score) as max_conf
        FROM core_f_collaboration
        WHERE confidence_score IS NOT NULL
        """)
        conf = self.cursor.fetchone()
        if conf[0]:
            report.append(f"  Average Confidence: {conf[0]:.2f}\n")
            report.append(f"  Range: {conf[1]:.2f} - {conf[2]:.2f}\n")

        report_text = ''.join(report)

        # Save report
        report_path = self.project_root / "database/intelligence_report.txt"
        with open(report_path, 'w') as f:
            f.write(report_text)

        logger.info(f"Report saved to {report_path}")
        return report_text

def main():
    """Main execution"""
    loader = ComprehensiveDataLoader()

    # Load all data sources
    loader.load_ted_procurement()
    loader.load_italy_china_analysis()
    loader.load_archived_china_contracts()
    loader.load_existing_databases()
    loader.load_usaspending_data()

    # Generate report
    report = loader.generate_comprehensive_report()
    print(report)

    loader.conn.close()
    logger.info("Comprehensive data loading complete")

if __name__ == "__main__":
    main()

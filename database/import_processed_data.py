#!/usr/bin/env python3
"""
Import processed OSINT data into warehouse
Works with actual data structure in C:/Projects/OSINT - Foresight/data/processed
"""

import os
import json
import sqlite3
import logging
from pathlib import Path
from datetime import datetime
import pandas as pd
import glob

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProcessedDataImporter:
    """Import data from processed directories"""

    def __init__(self, db_path: str = "F:/OSINT_WAREHOUSE/osint_research.db"):
        self.db_path = Path(db_path)
        self.project_root = Path("C:/Projects/OSINT - Foresight")
        self.processed_dir = self.project_root / "data/processed"

        # Connect to warehouse
        self.conn = sqlite3.connect(str(self.db_path))
        self.cursor = self.conn.cursor()

        logger.info(f"Connected to warehouse at {self.db_path}")

    def import_cordis_data(self):
        """Import CORDIS data from processed directories"""
        logger.info("Importing CORDIS data...")

        cordis_dirs = [
            self.processed_dir / "cordis_multicountry",
            self.processed_dir / "cordis_specific_countries",
            self.processed_dir / "cordis_unified"
        ]

        total_imported = 0
        china_collaborations = 0

        for dir_path in cordis_dirs:
            if not dir_path.exists():
                logger.warning(f"CORDIS directory not found: {dir_path}")
                continue

            # Process JSON files
            json_files = list(dir_path.glob("**/*.json"))
            logger.info(f"Found {len(json_files)} JSON files in {dir_path.name}")

            for json_file in json_files[:100]:  # Process first 100 files
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    # Handle different data structures
                    if isinstance(data, dict):
                        projects = data.get('projects', [data])
                    elif isinstance(data, list):
                        projects = data
                    else:
                        projects = [data]

                    for project in projects:
                        if not isinstance(project, dict):
                            continue

                        # Extract project details
                        project_id = project.get('id', '') or project.get('projectID', '')
                        title = project.get('title', '') or project.get('projectTitle', '')

                        # Check for Chinese collaboration
                        project_text = f"{title} {project.get('objective', '')} {project.get('participants', '')}"
                        china_score = self._detect_chinese_involvement(project_text)

                        if project_id:
                            self.cursor.execute("""
                            INSERT OR REPLACE INTO core_f_collaboration (
                                collab_id, project_id, project_name,
                                funding_amount, funding_currency,
                                has_chinese_partner, china_collaboration_score,
                                source_system, retrieved_at, confidence_score
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                f"CORDIS_{project_id}",
                                project_id,
                                title[:500] if title else "Unknown Project",
                                project.get('totalCost', 0) or project.get('ecMaxContribution', 0),
                                'EUR',
                                1 if china_score > 0.5 else 0,
                                china_score,
                                'CORDIS',
                                datetime.now().isoformat(),
                                0.8
                            ))

                            total_imported += 1
                            if china_score > 0.5:
                                china_collaborations += 1

                except Exception as e:
                    logger.error(f"Error processing {json_file}: {e}")

        self.conn.commit()
        logger.info(f"CORDIS import completed: {total_imported} projects, {china_collaborations} with China involvement")

    def import_openaire_data(self):
        """Import OpenAIRE data with keyword search fix"""
        logger.info("Importing OpenAIRE data...")

        openaire_dirs = [
            self.processed_dir / "openaire_comprehensive",
            self.processed_dir / "openaire_multicountry",
            self.processed_dir / "openaire_technology",
            self.processed_dir / "openalex_real_data"  # Contains keyword search results
        ]

        total_imported = 0
        china_collaborations = 0

        for dir_path in openaire_dirs:
            if not dir_path.exists():
                logger.warning(f"OpenAIRE directory not found: {dir_path}")
                continue

            json_files = list(dir_path.glob("**/*.json"))
            logger.info(f"Found {len(json_files)} files in {dir_path.name}")

            for json_file in json_files[:100]:
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    # Handle OpenAIRE data structure
                    results = []
                    if isinstance(data, dict):
                        results = data.get('results', data.get('response', []))
                    elif isinstance(data, list):
                        results = data

                    for item in results:
                        if not isinstance(item, dict):
                            continue

                        # Extract publication details
                        pub_id = item.get('id', '')
                        title = item.get('title', {})
                        if isinstance(title, dict):
                            title = title.get('$', '')

                        # These are from keyword searches - already China-related
                        is_keyword_search = 'openalex_real_data' in str(json_file)

                        if pub_id:
                            self.cursor.execute("""
                            INSERT OR REPLACE INTO core_f_publication (
                                pub_id, doi, title,
                                has_chinese_author, china_collaboration_score,
                                source_system, retrieved_at, confidence_score
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                pub_id,
                                item.get('doi', ''),
                                str(title)[:500] if title else "Unknown Publication",
                                1 if is_keyword_search else 0,
                                1.0 if is_keyword_search else 0.5,
                                'OpenAIRE_Keyword' if is_keyword_search else 'OpenAIRE',
                                datetime.now().isoformat(),
                                0.9 if is_keyword_search else 0.7
                            ))

                            total_imported += 1
                            if is_keyword_search:
                                china_collaborations += 1

                except Exception as e:
                    logger.error(f"Error processing {json_file}: {e}")

        self.conn.commit()
        logger.info(f"OpenAIRE import completed: {total_imported} publications, {china_collaborations} China-related")

    def import_ted_procurement(self):
        """Import TED procurement data"""
        logger.info("Importing TED procurement data...")

        ted_dirs = [
            self.processed_dir / "ted_2023_2025",
            self.processed_dir / "ted_historical_2010_2022",
            self.processed_dir / "ted_flexible_2016_2022"
        ]

        # Also check F: drive
        ted_main = Path("F:/TED_Data/monthly")
        if ted_main.exists():
            ted_dirs.append(ted_main)

        total_imported = 0
        china_contracts = 0

        for dir_path in ted_dirs:
            if not dir_path.exists():
                logger.warning(f"TED directory not found: {dir_path}")
                continue

            # Process JSON files from processed directories
            json_files = list(dir_path.glob("**/*.json"))[:50]

            for json_file in json_files:
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    contracts = []
                    if isinstance(data, dict):
                        contracts = data.get('contracts', data.get('results', []))
                    elif isinstance(data, list):
                        contracts = data

                    for contract in contracts:
                        if not isinstance(contract, dict):
                            continue

                        # Check for Chinese vendors
                        vendor_info = str(contract.get('vendor', '')) + str(contract.get('contractor', ''))
                        china_score = self._detect_chinese_involvement(vendor_info)

                        award_id = contract.get('id', '') or contract.get('notice_id', '')

                        if award_id:
                            self.cursor.execute("""
                            INSERT OR REPLACE INTO core_f_procurement (
                                award_id, buyer_country, vendor_name,
                                contract_value, currency,
                                has_chinese_vendor, supply_chain_risk,
                                source_system, retrieved_at, confidence_score
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                f"TED_{award_id}",
                                contract.get('country', 'EU'),
                                contract.get('vendor_name', 'Unknown'),
                                contract.get('value', 0),
                                contract.get('currency', 'EUR'),
                                1 if china_score > 0.5 else 0,
                                'HIGH' if china_score > 0.7 else 'MEDIUM' if china_score > 0.3 else 'LOW',
                                'TED_EU',
                                datetime.now().isoformat(),
                                0.85
                            ))

                            total_imported += 1
                            if china_score > 0.5:
                                china_contracts += 1

                except Exception as e:
                    logger.error(f"Error processing {json_file}: {e}")

        self.conn.commit()
        logger.info(f"TED import completed: {total_imported} contracts, {china_contracts} with potential China involvement")

    def import_patent_data(self):
        """Import patent data from EPO and USPTO"""
        logger.info("Importing patent data...")

        patent_dirs = [
            self.processed_dir / "patents_multicountry",
            self.processed_dir / "epo_targeted_patents",
            self.processed_dir / "USPTO"
        ]

        total_imported = 0
        china_patents = 0

        for dir_path in patent_dirs:
            if not dir_path.exists():
                continue

            json_files = list(dir_path.glob("**/*.json"))[:100]

            for json_file in json_files:
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    patents = []
                    if isinstance(data, dict):
                        patents = data.get('patents', data.get('results', []))
                    elif isinstance(data, list):
                        patents = data

                    for patent in patents:
                        if not isinstance(patent, dict):
                            continue

                        # Check for Chinese applicants
                        applicant_info = str(patent.get('applicant', '')) + str(patent.get('inventor', ''))
                        china_score = self._detect_chinese_involvement(applicant_info)

                        patent_id = patent.get('patent_number', '') or patent.get('publication_number', '')

                        if patent_id:
                            self.cursor.execute("""
                            INSERT OR REPLACE INTO core_f_patent (
                                patent_id, patent_number, title,
                                applicant_name, filing_date,
                                has_chinese_applicant, technology_transfer_risk,
                                source_system, retrieved_at, confidence_score
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                patent_id,
                                patent_id,
                                patent.get('title', 'Unknown Patent')[:500],
                                patent.get('applicant', 'Unknown'),
                                patent.get('filing_date', ''),
                                1 if china_score > 0.5 else 0,
                                'HIGH' if china_score > 0.7 else 'MEDIUM' if china_score > 0.3 else 'LOW',
                                'EPO' if 'epo' in str(json_file).lower() else 'USPTO',
                                datetime.now().isoformat(),
                                0.9
                            ))

                            total_imported += 1
                            if china_score > 0.5:
                                china_patents += 1

                except Exception as e:
                    logger.error(f"Error processing {json_file}: {e}")

        self.conn.commit()
        logger.info(f"Patent import completed: {total_imported} patents, {china_patents} with China involvement")

    def import_existing_databases(self):
        """Import from existing SQLite databases in processed directory"""
        logger.info("Importing from existing databases...")

        db_files = list(self.processed_dir.glob("*.db"))

        for db_file in db_files:
            logger.info(f"Processing database: {db_file.name}")

            try:
                source_conn = sqlite3.connect(str(db_file))
                source_cursor = source_conn.cursor()

                # Get table list
                source_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = source_cursor.fetchall()

                for table in tables:
                    table_name = table[0]

                    # Map to appropriate warehouse table
                    if 'collab' in table_name.lower() or 'project' in table_name.lower():
                        self._import_collaboration_data(source_cursor, table_name)
                    elif 'pub' in table_name.lower() or 'article' in table_name.lower():
                        self._import_publication_data(source_cursor, table_name)
                    elif 'patent' in table_name.lower():
                        self._import_patent_table(source_cursor, table_name)
                    elif 'procurement' in table_name.lower() or 'contract' in table_name.lower():
                        self._import_procurement_data(source_cursor, table_name)

                source_conn.close()

            except Exception as e:
                logger.error(f"Error processing {db_file}: {e}")

        logger.info("Database import completed")

    def _detect_chinese_involvement(self, text: str) -> float:
        """Detect Chinese involvement in text"""
        if not text:
            return 0.0

        text_lower = text.lower()

        # Strong indicators
        strong_keywords = [
            'china', 'chinese', 'beijing', 'shanghai', 'shenzhen',
            'guangzhou', 'wuhan', 'chengdu', 'nanjing', 'hangzhou',
            'tsinghua', 'peking university', 'fudan', 'zhejiang',
            'huawei', 'alibaba', 'tencent', 'baidu', 'xiaomi',
            'cas', 'chinese academy', 'xinjiang', 'tibet'
        ]

        for keyword in strong_keywords:
            if keyword in text_lower:
                return 0.9

        # Medium indicators
        medium_keywords = ['asia', 'asian', 'sino']
        for keyword in medium_keywords:
            if keyword in text_lower:
                return 0.5

        return 0.0

    def _import_collaboration_data(self, source_cursor, table_name):
        """Import collaboration data from source table"""
        try:
            source_cursor.execute(f"SELECT * FROM {table_name} LIMIT 1000")
            columns = [desc[0] for desc in source_cursor.description]

            source_cursor.execute(f"SELECT * FROM {table_name} LIMIT 1000")

            for row in source_cursor.fetchall():
                row_dict = dict(zip(columns, row))

                # Map to warehouse schema
                project_text = ' '.join([str(v) for v in row_dict.values() if v])
                china_score = self._detect_chinese_involvement(project_text)

                self.cursor.execute("""
                INSERT OR IGNORE INTO core_f_collaboration (
                    collab_id, project_name, has_chinese_partner,
                    china_collaboration_score, source_system
                ) VALUES (?, ?, ?, ?, ?)
                """, (
                    f"{table_name}_{row[0]}",
                    str(row_dict.get('title', row_dict.get('name', 'Unknown')))[:500],
                    1 if china_score > 0.5 else 0,
                    china_score,
                    f"DB_{table_name}"
                ))

        except Exception as e:
            logger.error(f"Error importing from {table_name}: {e}")

    def _import_publication_data(self, source_cursor, table_name):
        """Import publication data from source table"""
        try:
            source_cursor.execute(f"SELECT * FROM {table_name} LIMIT 1000")
            columns = [desc[0] for desc in source_cursor.description]

            source_cursor.execute(f"SELECT * FROM {table_name} LIMIT 1000")

            for row in source_cursor.fetchall():
                row_dict = dict(zip(columns, row))

                pub_text = ' '.join([str(v) for v in row_dict.values() if v])
                china_score = self._detect_chinese_involvement(pub_text)

                self.cursor.execute("""
                INSERT OR IGNORE INTO core_f_publication (
                    pub_id, title, has_chinese_author,
                    china_collaboration_score, source_system
                ) VALUES (?, ?, ?, ?, ?)
                """, (
                    f"{table_name}_{row[0]}",
                    str(row_dict.get('title', 'Unknown'))[:500],
                    1 if china_score > 0.5 else 0,
                    china_score,
                    f"DB_{table_name}"
                ))

        except Exception as e:
            logger.error(f"Error importing publications from {table_name}: {e}")

    def _import_patent_table(self, source_cursor, table_name):
        """Import patent data from source table"""
        try:
            source_cursor.execute(f"SELECT * FROM {table_name} LIMIT 1000")
            columns = [desc[0] for desc in source_cursor.description]

            source_cursor.execute(f"SELECT * FROM {table_name} LIMIT 1000")

            for row in source_cursor.fetchall():
                row_dict = dict(zip(columns, row))

                patent_text = ' '.join([str(v) for v in row_dict.values() if v])
                china_score = self._detect_chinese_involvement(patent_text)

                self.cursor.execute("""
                INSERT OR IGNORE INTO core_f_patent (
                    patent_id, title, has_chinese_applicant,
                    technology_transfer_risk, source_system
                ) VALUES (?, ?, ?, ?, ?)
                """, (
                    f"{table_name}_{row[0]}",
                    str(row_dict.get('title', 'Unknown Patent'))[:500],
                    1 if china_score > 0.5 else 0,
                    'HIGH' if china_score > 0.7 else 'MEDIUM',
                    f"DB_{table_name}"
                ))

        except Exception as e:
            logger.error(f"Error importing patents from {table_name}: {e}")

    def _import_procurement_data(self, source_cursor, table_name):
        """Import procurement data from source table"""
        try:
            source_cursor.execute(f"SELECT * FROM {table_name} LIMIT 1000")
            columns = [desc[0] for desc in source_cursor.description]

            source_cursor.execute(f"SELECT * FROM {table_name} LIMIT 1000")

            for row in source_cursor.fetchall():
                row_dict = dict(zip(columns, row))

                vendor_text = ' '.join([str(v) for v in row_dict.values() if v])
                china_score = self._detect_chinese_involvement(vendor_text)

                self.cursor.execute("""
                INSERT OR IGNORE INTO core_f_procurement (
                    award_id, has_chinese_vendor,
                    supply_chain_risk, source_system
                ) VALUES (?, ?, ?, ?)
                """, (
                    f"{table_name}_{row[0]}",
                    1 if china_score > 0.5 else 0,
                    'HIGH' if china_score > 0.7 else 'MEDIUM',
                    f"DB_{table_name}"
                ))

        except Exception as e:
            logger.error(f"Error importing procurement from {table_name}: {e}")

    def generate_import_report(self):
        """Generate detailed import report"""
        logger.info("Generating import report...")

        report = []
        report.append("=== DATA IMPORT REPORT ===\n")
        report.append(f"Generated: {datetime.now().isoformat()}\n\n")

        # Get counts by source
        self.cursor.execute("""
        SELECT source_system, COUNT(*) as count
        FROM core_f_collaboration
        GROUP BY source_system
        ORDER BY count DESC
        """)

        report.append("Collaborations by Source:\n")
        for row in self.cursor.fetchall():
            report.append(f"  {row[0]}: {row[1]:,}\n")

        # China detection rates
        self.cursor.execute("""
        SELECT
            source_system,
            COUNT(*) as total,
            SUM(has_chinese_partner) as china_found,
            AVG(china_collaboration_score) as avg_score
        FROM core_f_collaboration
        GROUP BY source_system
        """)

        report.append("\nChina Detection Rates:\n")
        for row in self.cursor.fetchall():
            if row[1] > 0:
                rate = (row[2] / row[1]) * 100
                report.append(f"  {row[0]}: {row[2]:,}/{row[1]:,} ({rate:.1f}%), avg score: {row[3]:.2f}\n")

        # Publication counts
        self.cursor.execute("SELECT COUNT(*) FROM core_f_publication WHERE has_chinese_author = 1")
        china_pubs = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COUNT(*) FROM core_f_publication")
        total_pubs = self.cursor.fetchone()[0]

        report.append(f"\nPublications: {total_pubs:,} total, {china_pubs:,} with Chinese authors\n")

        # Patent counts
        self.cursor.execute("SELECT COUNT(*) FROM core_f_patent WHERE has_chinese_applicant = 1")
        china_patents = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COUNT(*) FROM core_f_patent")
        total_patents = self.cursor.fetchone()[0]

        report.append(f"Patents: {total_patents:,} total, {china_patents:,} with Chinese applicants\n")

        # Procurement counts
        self.cursor.execute("SELECT COUNT(*) FROM core_f_procurement WHERE has_chinese_vendor = 1")
        china_contracts = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COUNT(*) FROM core_f_procurement")
        total_contracts = self.cursor.fetchone()[0]

        report.append(f"Procurement: {total_contracts:,} total, {china_contracts:,} with Chinese vendors\n")

        report_text = ''.join(report)

        # Save report
        report_path = self.project_root / "database/import_report.txt"
        with open(report_path, 'w') as f:
            f.write(report_text)

        logger.info(f"Report saved to {report_path}")
        return report_text

def main():
    """Main execution"""
    importer = ProcessedDataImporter()

    # Import all data sources
    importer.import_cordis_data()
    importer.import_openaire_data()
    importer.import_ted_procurement()
    importer.import_patent_data()
    importer.import_existing_databases()

    # Generate report
    report = importer.generate_import_report()
    print(report)

    importer.conn.close()
    logger.info("Data import completed")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
AidData Comprehensive Processor
Integrates all AidData datasets into OSINT Master Database

Datasets Processed:
1. Global Chinese Development Finance v3.0 (20,985 projects)
2. Geospatial data (13,908 geocoded projects)
3. Chinese AI Exports (155 projects)
4. Chinese Loan Contracts (371 contracts)
5. Chinese Collateralized Loans (620 loans)
6. China Lender of Last Resort (emergency rescue lending)
7. China Seaport Finance (123 ports)

Output: F:/OSINT_WAREHOUSE/osint_master.db
"""

import sys
import json
import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/aiddata_processing.log'),
        logging.StreamHandler()
    ]
)

class AidDataProcessor:
    def __init__(self,
                 aiddata_dir="F:/OSINT_DATA/AidData",
                 master_db="F:/OSINT_WAREHOUSE/osint_master.db"):
        self.aiddata_dir = Path(aiddata_dir)
        self.master_db = Path(master_db)
        self.conn = None

        # Dataset paths
        self.datasets = {
            "global_finance": self.aiddata_dir / "global_chinese_finance_v3" /
                            "AidDatas_Global_Chinese_Development_Finance_Dataset_Version_3_0" /
                            "AidDatasGlobalChineseDevelopmentFinanceDataset_v3.0.xlsx",
            "ai_exports": self.aiddata_dir / "chinese_ai_exports" / "TL-A2696-1-CAIED.xlsx",
            "loan_contracts": self.aiddata_dir / "chinese_loan_contracts_v2" /
                            "How_China_Lends_Dataset_Version_2_0.xlsx",
            "collateralized": self.aiddata_dir / "chinese_collateralized_loans" /
                            "How_China_Collateralizes_Dataset_Version_1_0.xlsx",
            "rescue_lending": self.aiddata_dir / "china_lender_last_resort" /
                            "WPS124_China_as_an_International_Lender_of_Last_Resort_Version_1_0_1" /
                            "WPS124_China_as_an_International_Lender_of_Last_Resort.xlsx",
            "seaport_finance": self.aiddata_dir / "china_seaport_finance" /
                             "China's Official Seaport Finance Dataset, 2000-2021.xlsx",
            "adm1_locations": self.aiddata_dir / "global_chinese_finance_v3" /
                            "AidDatas_Global_Chinese_Development_Finance_Dataset_Version_3_0" /
                            "ADM Location Data" / "GCDF_3.0_ADM1_Locations.csv",
            "adm2_locations": self.aiddata_dir / "global_chinese_finance_v3" /
                            "AidDatas_Global_Chinese_Development_Finance_Dataset_Version_3_0" /
                            "ADM Location Data" / "GCDF_3.0_ADM2_Locations.csv"
        }

        self.stats = {
            "global_finance": 0,
            "ai_exports": 0,
            "loan_contracts": 0,
            "collateralized": 0,
            "rescue_lending": 0,
            "seaport_finance": 0,
            "locations": 0,
            "errors": []
        }

    def connect(self):
        """Connect to master database"""
        logging.info(f"Connecting to master database: {self.master_db}")
        self.master_db.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.master_db)
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA synchronous=NORMAL")
        self.conn.execute("PRAGMA cache_size=-64000")

    def create_tables(self):
        """Create AidData tables in master database"""
        logging.info("Creating AidData tables...")

        tables = {
            "aiddata_global_finance": """
                CREATE TABLE IF NOT EXISTS aiddata_global_finance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    aiddata_project_id TEXT UNIQUE,
                    recipient_country TEXT,
                    recipient_iso3 TEXT,
                    project_title TEXT,
                    project_description TEXT,
                    commitment_year INTEGER,
                    commitment_amount_usd REAL,
                    flow_type TEXT,
                    sector_name TEXT,
                    lender_name TEXT,
                    borrower_name TEXT,
                    project_status TEXT,
                    start_year INTEGER,
                    completion_year INTEGER,
                    raw_data TEXT,
                    source TEXT DEFAULT 'aiddata_gcdf_v3',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """,
            "aiddata_ai_exports": """
                CREATE TABLE IF NOT EXISTS aiddata_ai_exports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id TEXT,
                    recipient_country TEXT,
                    recipient_iso3 TEXT,
                    ai_technology_type TEXT,
                    vendor_name TEXT,
                    amount_usd REAL,
                    project_year INTEGER,
                    project_description TEXT,
                    raw_data TEXT,
                    source TEXT DEFAULT 'aiddata_caied',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """,
            "aiddata_loan_contracts": """
                CREATE TABLE IF NOT EXISTS aiddata_loan_contracts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    contract_id TEXT,
                    borrower_country TEXT,
                    borrower_iso3 TEXT,
                    lender_name TEXT,
                    amount_usd REAL,
                    interest_rate REAL,
                    maturity_years INTEGER,
                    contract_terms TEXT,
                    confidentiality_clause TEXT,
                    cancellation_clause TEXT,
                    raw_data TEXT,
                    source TEXT DEFAULT 'aiddata_how_china_lends_v2',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """,
            "aiddata_collateralized_loans": """
                CREATE TABLE IF NOT EXISTS aiddata_collateralized_loans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    loan_id TEXT,
                    borrower_country TEXT,
                    borrower_iso3 TEXT,
                    creditor_name TEXT,
                    amount_usd REAL,
                    collateral_type TEXT,
                    collateral_description TEXT,
                    commitment_year INTEGER,
                    raw_data TEXT,
                    source TEXT DEFAULT 'aiddata_how_china_collateralizes_v1',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """,
            "aiddata_rescue_lending": """
                CREATE TABLE IF NOT EXISTS aiddata_rescue_lending (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    operation_id TEXT,
                    borrower_country TEXT,
                    borrower_iso3 TEXT,
                    lender_name TEXT,
                    amount_usd REAL,
                    operation_year INTEGER,
                    operation_type TEXT,
                    description TEXT,
                    raw_data TEXT,
                    source TEXT DEFAULT 'aiddata_lender_last_resort_v1',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """,
            "aiddata_seaport_finance": """
                CREATE TABLE IF NOT EXISTS aiddata_seaport_finance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id TEXT,
                    port_name TEXT,
                    country TEXT,
                    country_iso3 TEXT,
                    amount_usd REAL,
                    commitment_year INTEGER,
                    lender_name TEXT,
                    latitude REAL,
                    longitude REAL,
                    project_description TEXT,
                    raw_data TEXT,
                    source TEXT DEFAULT 'aiddata_seaport_finance_2021',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """,
            "aiddata_locations": """
                CREATE TABLE IF NOT EXISTS aiddata_locations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    aiddata_project_id TEXT,
                    location_name TEXT,
                    location_type TEXT,
                    country_iso3 TEXT,
                    adm1_name TEXT,
                    adm2_name TEXT,
                    latitude REAL,
                    longitude REAL,
                    precision_code TEXT,
                    source TEXT DEFAULT 'aiddata_gcdf_v3',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """,
            "aiddata_cross_reference": """
                CREATE TABLE IF NOT EXISTS aiddata_cross_reference (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    aiddata_id TEXT,
                    aiddata_table TEXT,
                    external_system TEXT,
                    external_id TEXT,
                    match_confidence REAL,
                    match_method TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
        }

        for table_name, create_sql in tables.items():
            logging.info(f"Creating table: {table_name}")
            self.conn.execute(create_sql)

        self.conn.commit()

    def process_global_finance(self):
        """Process Global Chinese Development Finance v3.0"""
        logging.info("Processing Global Chinese Development Finance v3.0...")

        try:
            if not self.datasets["global_finance"].exists():
                logging.error(f"File not found: {self.datasets['global_finance']}")
                return

            # Read Excel file
            df = pd.read_excel(self.datasets["global_finance"])
            logging.info(f"Loaded {len(df)} projects from GCDF v3.0")

            # Insert into database
            cursor = self.conn.cursor()

            for idx, row in df.iterrows():
                try:
                    cursor.execute("""
                        INSERT OR IGNORE INTO aiddata_global_finance (
                            aiddata_project_id, recipient_country, recipient_iso3,
                            project_title, project_description, commitment_year,
                            commitment_amount_usd, flow_type, sector_name,
                            lender_name, borrower_name, project_status, raw_data
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        str(row.get('AidData Project ID', '')),
                        str(row.get('Recipient', '')),
                        str(row.get('Recipient ISO3', '')),
                        str(row.get('Project Title', '')),
                        str(row.get('Project Description', ''))[:1000],
                        int(row.get('Commitment Year', 0)) if pd.notna(row.get('Commitment Year')) else None,
                        float(row.get('Commitment Amount (Nominal)', 0)) if pd.notna(row.get('Commitment Amount (Nominal)')) else None,
                        str(row.get('Flow Type', '')),
                        str(row.get('Sector Name', '')),
                        str(row.get('Lender', '')),
                        str(row.get('Borrower', '')),
                        str(row.get('Status', '')),
                        json.dumps(row.to_dict(), default=str)
                    ))

                    if idx % 1000 == 0:
                        self.conn.commit()
                        logging.info(f"  Processed {idx}/{len(df)} projects...")

                except Exception as e:
                    logging.error(f"Error processing row {idx}: {str(e)}")
                    self.stats["errors"].append(f"GCDF row {idx}: {str(e)}")

            self.conn.commit()
            self.stats["global_finance"] = len(df)
            logging.info(f"Completed: {len(df)} projects loaded")

        except Exception as e:
            logging.error(f"Error processing global finance: {str(e)}")
            self.stats["errors"].append(f"Global finance: {str(e)}")

    def process_ai_exports(self):
        """Process Chinese AI Exports Database (CAIED)"""
        logging.info("Processing Chinese AI Exports Database...")

        try:
            if not self.datasets["ai_exports"].exists():
                logging.error(f"File not found: {self.datasets['ai_exports']}")
                return

            df = pd.read_excel(self.datasets["ai_exports"])
            logging.info(f"Loaded {len(df)} AI export projects")

            cursor = self.conn.cursor()

            for idx, row in df.iterrows():
                try:
                    cursor.execute("""
                        INSERT OR IGNORE INTO aiddata_ai_exports (
                            project_id, recipient_country, recipient_iso3,
                            ai_technology_type, vendor_name, amount_usd,
                            project_year, project_description, raw_data
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        str(row.get('Project ID', f"CAIED_{idx}")),
                        str(row.get('Country', '')),
                        str(row.get('ISO3', '')),
                        str(row.get('AI Technology Type', '')),
                        str(row.get('Vendor', '')),
                        float(row.get('Amount (USD)', 0)) if pd.notna(row.get('Amount (USD)')) else None,
                        int(row.get('Year', 0)) if pd.notna(row.get('Year')) else None,
                        str(row.get('Description', ''))[:1000],
                        json.dumps(row.to_dict(), default=str)
                    ))

                except Exception as e:
                    logging.error(f"Error processing AI export row {idx}: {str(e)}")
                    self.stats["errors"].append(f"AI exports row {idx}: {str(e)}")

            self.conn.commit()
            self.stats["ai_exports"] = len(df)
            logging.info(f"Completed: {len(df)} AI export projects loaded")

        except Exception as e:
            logging.error(f"Error processing AI exports: {str(e)}")
            self.stats["errors"].append(f"AI exports: {str(e)}")

    def process_loan_contracts(self):
        """Process How China Lends v2.0"""
        logging.info("Processing Chinese Loan Contracts...")

        try:
            if not self.datasets["loan_contracts"].exists():
                logging.error(f"File not found: {self.datasets['loan_contracts']}")
                return

            df = pd.read_excel(self.datasets["loan_contracts"])
            logging.info(f"Loaded {len(df)} loan contracts")

            cursor = self.conn.cursor()

            for idx, row in df.iterrows():
                try:
                    cursor.execute("""
                        INSERT OR IGNORE INTO aiddata_loan_contracts (
                            contract_id, borrower_country, borrower_iso3,
                            lender_name, amount_usd, interest_rate,
                            maturity_years, contract_terms, raw_data
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        str(row.get('Contract ID', f"HCL_{idx}")),
                        str(row.get('Borrower Country', '')),
                        str(row.get('ISO3', '')),
                        str(row.get('Lender', '')),
                        float(row.get('Amount (USD)', 0)) if pd.notna(row.get('Amount (USD)')) else None,
                        float(row.get('Interest Rate', 0)) if pd.notna(row.get('Interest Rate')) else None,
                        int(row.get('Maturity (Years)', 0)) if pd.notna(row.get('Maturity (Years)')) else None,
                        str(row.get('Contract Terms', '')),
                        json.dumps(row.to_dict(), default=str)
                    ))

                except Exception as e:
                    logging.error(f"Error processing loan contract row {idx}: {str(e)}")
                    self.stats["errors"].append(f"Loan contracts row {idx}: {str(e)}")

            self.conn.commit()
            self.stats["loan_contracts"] = len(df)
            logging.info(f"Completed: {len(df)} loan contracts loaded")

        except Exception as e:
            logging.error(f"Error processing loan contracts: {str(e)}")
            self.stats["errors"].append(f"Loan contracts: {str(e)}")

    def process_collateralized_loans(self):
        """Process How China Collateralizes v1.0"""
        logging.info("Processing Chinese Collateralized Loans...")

        try:
            if not self.datasets["collateralized"].exists():
                logging.error(f"File not found: {self.datasets['collateralized']}")
                return

            df = pd.read_excel(self.datasets["collateralized"])
            logging.info(f"Loaded {len(df)} collateralized loans")

            cursor = self.conn.cursor()

            for idx, row in df.iterrows():
                try:
                    cursor.execute("""
                        INSERT OR IGNORE INTO aiddata_collateralized_loans (
                            loan_id, borrower_country, borrower_iso3,
                            creditor_name, amount_usd, collateral_type,
                            collateral_description, commitment_year, raw_data
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        str(row.get('Loan ID', f"COLL_{idx}")),
                        str(row.get('Borrower Country', '')),
                        str(row.get('ISO3', '')),
                        str(row.get('Creditor', '')),
                        float(row.get('Amount (USD)', 0)) if pd.notna(row.get('Amount (USD)')) else None,
                        str(row.get('Collateral Type', '')),
                        str(row.get('Collateral Description', ''))[:1000],
                        int(row.get('Commitment Year', 0)) if pd.notna(row.get('Commitment Year')) else None,
                        json.dumps(row.to_dict(), default=str)
                    ))

                except Exception as e:
                    logging.error(f"Error processing collateralized loan row {idx}: {str(e)}")
                    self.stats["errors"].append(f"Collateralized loans row {idx}: {str(e)}")

            self.conn.commit()
            self.stats["collateralized"] = len(df)
            logging.info(f"Completed: {len(df)} collateralized loans loaded")

        except Exception as e:
            logging.error(f"Error processing collateralized loans: {str(e)}")
            self.stats["errors"].append(f"Collateralized loans: {str(e)}")

    def process_rescue_lending(self):
        """Process China as Lender of Last Resort v1.0.1"""
        logging.info("Processing China Rescue Lending...")

        try:
            if not self.datasets["rescue_lending"].exists():
                logging.error(f"File not found: {self.datasets['rescue_lending']}")
                return

            df = pd.read_excel(self.datasets["rescue_lending"])
            logging.info(f"Loaded {len(df)} rescue lending operations")

            cursor = self.conn.cursor()

            for idx, row in df.iterrows():
                try:
                    cursor.execute("""
                        INSERT OR IGNORE INTO aiddata_rescue_lending (
                            operation_id, borrower_country, borrower_iso3,
                            lender_name, amount_usd, operation_year,
                            operation_type, description, raw_data
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        str(row.get('Operation ID', f"RESCUE_{idx}")),
                        str(row.get('Country', '')),
                        str(row.get('ISO3', '')),
                        str(row.get('Lender', '')),
                        float(row.get('Amount (USD)', 0)) if pd.notna(row.get('Amount (USD)')) else None,
                        int(row.get('Year', 0)) if pd.notna(row.get('Year')) else None,
                        str(row.get('Operation Type', '')),
                        str(row.get('Description', ''))[:1000],
                        json.dumps(row.to_dict(), default=str)
                    ))

                except Exception as e:
                    logging.error(f"Error processing rescue lending row {idx}: {str(e)}")
                    self.stats["errors"].append(f"Rescue lending row {idx}: {str(e)}")

            self.conn.commit()
            self.stats["rescue_lending"] = len(df)
            logging.info(f"Completed: {len(df)} rescue lending operations loaded")

        except Exception as e:
            logging.error(f"Error processing rescue lending: {str(e)}")
            self.stats["errors"].append(f"Rescue lending: {str(e)}")

    def process_seaport_finance(self):
        """Process China Seaport Finance 2000-2021"""
        logging.info("Processing China Seaport Finance...")

        try:
            if not self.datasets["seaport_finance"].exists():
                logging.error(f"File not found: {self.datasets['seaport_finance']}")
                return

            df = pd.read_excel(self.datasets["seaport_finance"])
            logging.info(f"Loaded {len(df)} seaport projects")

            cursor = self.conn.cursor()

            for idx, row in df.iterrows():
                try:
                    cursor.execute("""
                        INSERT OR IGNORE INTO aiddata_seaport_finance (
                            project_id, port_name, country, country_iso3,
                            amount_usd, commitment_year, lender_name,
                            latitude, longitude, project_description, raw_data
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        str(row.get('Project ID', f"PORT_{idx}")),
                        str(row.get('Port Name', '')),
                        str(row.get('Country', '')),
                        str(row.get('ISO3', '')),
                        float(row.get('Amount (USD)', 0)) if pd.notna(row.get('Amount (USD)')) else None,
                        int(row.get('Commitment Year', 0)) if pd.notna(row.get('Commitment Year')) else None,
                        str(row.get('Lender', '')),
                        float(row.get('Latitude', 0)) if pd.notna(row.get('Latitude')) else None,
                        float(row.get('Longitude', 0)) if pd.notna(row.get('Longitude')) else None,
                        str(row.get('Description', ''))[:1000],
                        json.dumps(row.to_dict(), default=str)
                    ))

                except Exception as e:
                    logging.error(f"Error processing seaport row {idx}: {str(e)}")
                    self.stats["errors"].append(f"Seaport finance row {idx}: {str(e)}")

            self.conn.commit()
            self.stats["seaport_finance"] = len(df)
            logging.info(f"Completed: {len(df)} seaport projects loaded")

        except Exception as e:
            logging.error(f"Error processing seaport finance: {str(e)}")
            self.stats["errors"].append(f"Seaport finance: {str(e)}")

    def process_locations(self):
        """Process ADM location data"""
        logging.info("Processing location data...")

        try:
            locations_loaded = 0

            for location_file in [self.datasets["adm1_locations"], self.datasets["adm2_locations"]]:
                if not location_file.exists():
                    logging.warning(f"File not found: {location_file}")
                    continue

                df = pd.read_csv(location_file)
                logging.info(f"Loaded {len(df)} locations from {location_file.name}")

                cursor = self.conn.cursor()

                for idx, row in df.iterrows():
                    try:
                        cursor.execute("""
                            INSERT OR IGNORE INTO aiddata_locations (
                                aiddata_project_id, location_name, location_type,
                                country_iso3, adm1_name, adm2_name,
                                latitude, longitude, precision_code
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            str(row.get('project_id', '')),
                            str(row.get('location_name', '')),
                            str(row.get('location_type', '')),
                            str(row.get('iso3', '')),
                            str(row.get('adm1', '')),
                            str(row.get('adm2', '')),
                            float(row.get('latitude', 0)) if pd.notna(row.get('latitude')) else None,
                            float(row.get('longitude', 0)) if pd.notna(row.get('longitude')) else None,
                            str(row.get('precision_code', ''))
                        ))

                        locations_loaded += 1

                    except Exception as e:
                        logging.error(f"Error processing location row {idx}: {str(e)}")
                        self.stats["errors"].append(f"Locations row {idx}: {str(e)}")

                self.conn.commit()

            self.stats["locations"] = locations_loaded
            logging.info(f"Completed: {locations_loaded} locations loaded")

        except Exception as e:
            logging.error(f"Error processing locations: {str(e)}")
            self.stats["errors"].append(f"Locations: {str(e)}")

    def generate_summary(self):
        """Generate processing summary"""
        summary = {
            "processing_date": datetime.now().isoformat(),
            "datasets_processed": {
                "global_finance": self.stats["global_finance"],
                "ai_exports": self.stats["ai_exports"],
                "loan_contracts": self.stats["loan_contracts"],
                "collateralized_loans": self.stats["collateralized"],
                "rescue_lending": self.stats["rescue_lending"],
                "seaport_finance": self.stats["seaport_finance"],
                "locations": self.stats["locations"]
            },
            "total_records": sum([
                self.stats["global_finance"],
                self.stats["ai_exports"],
                self.stats["loan_contracts"],
                self.stats["collateralized"],
                self.stats["rescue_lending"],
                self.stats["seaport_finance"],
                self.stats["locations"]
            ]),
            "errors": self.stats["errors"]
        }

        # Save summary
        summary_file = Path("F:/OSINT_DATA/AidData/PROCESSING_SUMMARY.json")
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

        logging.info("\n" + "="*80)
        logging.info("AIDDATA PROCESSING SUMMARY")
        logging.info("="*80)
        logging.info(f"Global Finance projects: {summary['datasets_processed']['global_finance']:,}")
        logging.info(f"AI Export projects: {summary['datasets_processed']['ai_exports']:,}")
        logging.info(f"Loan Contracts: {summary['datasets_processed']['loan_contracts']:,}")
        logging.info(f"Collateralized Loans: {summary['datasets_processed']['collateralized_loans']:,}")
        logging.info(f"Rescue Lending operations: {summary['datasets_processed']['rescue_lending']:,}")
        logging.info(f"Seaport Finance projects: {summary['datasets_processed']['seaport_finance']:,}")
        logging.info(f"Location records: {summary['datasets_processed']['locations']:,}")
        logging.info(f"Total records loaded: {summary['total_records']:,}")
        logging.info(f"Errors encountered: {len(summary['errors'])}")
        logging.info("="*80)

        return summary

    def process_all(self):
        """Process all AidData datasets"""
        logging.info("Starting AidData comprehensive processing...")

        try:
            self.connect()
            self.create_tables()

            # Process each dataset
            self.process_global_finance()
            self.process_ai_exports()
            self.process_loan_contracts()
            self.process_collateralized_loans()
            self.process_rescue_lending()
            self.process_seaport_finance()
            self.process_locations()

            # Generate summary
            summary = self.generate_summary()

            logging.info("AidData processing complete!")
            return summary

        except Exception as e:
            logging.error(f"Fatal error in processing: {str(e)}")
            raise
        finally:
            if self.conn:
                self.conn.close()

def main():
    processor = AidDataProcessor()
    summary = processor.process_all()
    print(f"\nProcessing complete. Total records: {summary['total_records']:,}")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
SEC EDGAR to SQL Database Importer
Imports all SEC EDGAR Chinese company data into the OSINT SQL database
"""

import sqlite3
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sec_edgar_sql_import.log'),
        logging.StreamHandler()
    ]
)

class SECEdgarSQLImporter:
    """Import SEC EDGAR data to SQL database"""

    def __init__(self, db_path: str = "F:/OSINT_WAREHOUSE/osint_master.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Data source
        self.sec_edgar_dir = Path("data/processed/sec_edgar_comprehensive")

        # Database connection
        self.conn = sqlite3.connect(str(self.db_path))
        self.cursor = self.conn.cursor()

        # Enable foreign keys
        self.cursor.execute("PRAGMA foreign_keys = ON")

        logging.info(f"Connected to database: {self.db_path}")

        # Statistics
        self.stats = {
            "companies_imported": 0,
            "filings_imported": 0,
            "addresses_imported": 0,
            "errors": []
        }

    def create_tables(self):
        """Create SEC EDGAR tables in database"""
        logging.info("Creating SEC EDGAR tables...")

        # Main companies table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS sec_edgar_companies (
            cik TEXT PRIMARY KEY,
            ticker TEXT,
            name TEXT NOT NULL,
            entity_type TEXT,
            sic TEXT,
            sic_description TEXT,
            category TEXT,
            state_of_incorporation TEXT,
            ein TEXT,
            phone TEXT,
            website TEXT,
            investor_website TEXT,
            is_chinese BOOLEAN DEFAULT 0,
            detection_reasons TEXT,
            data_fetched_date TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Company addresses table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS sec_edgar_addresses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cik TEXT NOT NULL,
            address_type TEXT NOT NULL,
            street1 TEXT,
            street2 TEXT,
            city TEXT,
            state_or_country TEXT,
            state_or_country_description TEXT,
            zip_code TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cik) REFERENCES sec_edgar_companies(cik) ON DELETE CASCADE
        )
        """)

        # Filings table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS sec_edgar_filings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cik TEXT NOT NULL,
            form TEXT NOT NULL,
            filing_date DATE,
            accession_number TEXT,
            primary_document TEXT,
            file_number TEXT,
            film_number TEXT,
            items TEXT,
            size INTEGER,
            is_xbrl BOOLEAN DEFAULT 0,
            is_inline_xbrl BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cik) REFERENCES sec_edgar_companies(cik) ON DELETE CASCADE
        )
        """)

        # Chinese company indicators table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS sec_edgar_chinese_indicators (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cik TEXT NOT NULL,
            indicator_type TEXT NOT NULL,
            indicator_value TEXT NOT NULL,
            confidence_score REAL DEFAULT 1.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cik) REFERENCES sec_edgar_companies(cik) ON DELETE CASCADE
        )
        """)

        # Create indexes for performance
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_companies_ticker ON sec_edgar_companies(ticker)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_companies_name ON sec_edgar_companies(name)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_companies_chinese ON sec_edgar_companies(is_chinese)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_companies_sic ON sec_edgar_companies(sic)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_filings_cik ON sec_edgar_filings(cik)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_filings_form ON sec_edgar_filings(form)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_filings_date ON sec_edgar_filings(filing_date)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_addresses_cik ON sec_edgar_addresses(cik)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_indicators_cik ON sec_edgar_chinese_indicators(cik)")

        # Create view for Chinese companies
        self.cursor.execute("""
        CREATE VIEW IF NOT EXISTS v_chinese_companies AS
        SELECT
            c.cik,
            c.ticker,
            c.name,
            c.sic,
            c.sic_description,
            c.state_of_incorporation,
            c.detection_reasons,
            COUNT(DISTINCT f.id) as filing_count,
            MAX(f.filing_date) as latest_filing_date,
            GROUP_CONCAT(DISTINCT i.indicator_type) as indicator_types
        FROM sec_edgar_companies c
        LEFT JOIN sec_edgar_filings f ON c.cik = f.cik
        LEFT JOIN sec_edgar_chinese_indicators i ON c.cik = i.cik
        WHERE c.is_chinese = 1
        GROUP BY c.cik
        """)

        self.conn.commit()
        logging.info("Tables created successfully")

    def import_company(self, filepath: Path):
        """Import a single company JSON file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Determine if Chinese based on detection_reasons or origins
            is_chinese = False
            detection_reasons = ""

            if 'detection_reasons' in data:
                is_chinese = True
                detection_reasons = json.dumps(data['detection_reasons'])
            elif 'origins' in data and data['origins']:
                origins = data['origins']
                if any(origin in ['china', 'hong_kong', 'cayman', 'bvi', 'bermuda'] for origin in origins):
                    is_chinese = True
                    detection_reasons = json.dumps(origins)

            # Insert company data
            self.cursor.execute("""
            INSERT OR REPLACE INTO sec_edgar_companies (
                cik, ticker, name, entity_type, sic, sic_description,
                category, state_of_incorporation, ein, phone, website,
                investor_website, is_chinese, detection_reasons,
                data_fetched_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data.get('cik'),
                data.get('ticker'),
                data.get('name'),
                data.get('entityType'),
                data.get('sic'),
                data.get('sicDescription'),
                data.get('category'),
                data.get('stateOfIncorporation'),
                data.get('ein'),
                data.get('phone'),
                data.get('website'),
                data.get('investorWebsite'),
                is_chinese,
                detection_reasons,
                datetime.now().isoformat()
            ))

            # Insert addresses
            if 'addresses' in data:
                for addr_type, addr_data in data['addresses'].items():
                    if isinstance(addr_data, dict):
                        self.cursor.execute("""
                        INSERT INTO sec_edgar_addresses (
                            cik, address_type, street1, street2, city,
                            state_or_country, state_or_country_description, zip_code
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            data['cik'],
                            addr_type,
                            addr_data.get('street1'),
                            addr_data.get('street2'),
                            addr_data.get('city'),
                            addr_data.get('stateOrCountry'),
                            addr_data.get('stateOrCountryDescription'),
                            addr_data.get('zipCode')
                        ))
                        self.stats["addresses_imported"] += 1

            # Insert recent filings if available
            if 'filings' in data and 'recent' in data['filings']:
                recent = data['filings']['recent']
                forms = recent.get('form', [])
                dates = recent.get('filingDate', [])
                accessions = recent.get('accessionNumber', [])
                primary_docs = recent.get('primaryDocument', [])
                file_numbers = recent.get('fileNumber', [])
                film_numbers = recent.get('filmNumber', [])
                items = recent.get('items', [])
                sizes = recent.get('size', [])
                is_xbrls = recent.get('isXBRL', [])
                is_inline_xbrls = recent.get('isInlineXBRL', [])

                # Import up to 100 most recent filings
                for i in range(min(100, len(forms))):
                    self.cursor.execute("""
                    INSERT INTO sec_edgar_filings (
                        cik, form, filing_date, accession_number,
                        primary_document, file_number, film_number,
                        items, size, is_xbrl, is_inline_xbrl
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        data['cik'],
                        forms[i] if i < len(forms) else None,
                        dates[i] if i < len(dates) else None,
                        accessions[i] if i < len(accessions) else None,
                        primary_docs[i] if i < len(primary_docs) else None,
                        file_numbers[i] if i < len(file_numbers) else None,
                        film_numbers[i] if i < len(film_numbers) else None,
                        items[i] if i < len(items) else None,
                        sizes[i] if i < len(sizes) else None,
                        is_xbrls[i] if i < len(is_xbrls) else 0,
                        is_inline_xbrls[i] if i < len(is_inline_xbrls) else 0
                    ))
                    self.stats["filings_imported"] += 1

            # Insert Chinese indicators if detected
            if is_chinese and 'detection_reasons' in data:
                for reason in data['detection_reasons']:
                    if ':' in reason:
                        indicator_type, indicator_value = reason.split(':', 1)
                        self.cursor.execute("""
                        INSERT INTO sec_edgar_chinese_indicators (
                            cik, indicator_type, indicator_value
                        ) VALUES (?, ?, ?)
                        """, (data['cik'], indicator_type, indicator_value))

            self.stats["companies_imported"] += 1

            if self.stats["companies_imported"] % 10 == 0:
                logging.info(f"Imported {self.stats['companies_imported']} companies...")

        except Exception as e:
            logging.error(f"Error importing {filepath}: {e}")
            self.stats["errors"].append(f"{filepath.name}: {str(e)}")

    def import_all_companies(self):
        """Import all company JSON files"""
        logging.info(f"Scanning {self.sec_edgar_dir} for company files...")

        # Find all JSON files
        json_files = list(self.sec_edgar_dir.glob("*.json"))

        # Exclude summary files
        company_files = [
            f for f in json_files
            if not f.name.startswith(("chinese_companies", "sec_edgar"))
        ]

        logging.info(f"Found {len(company_files)} company files to import")

        # Import each file
        for filepath in company_files:
            self.import_company(filepath)

        # Also check chinese subdirectory if it exists
        chinese_dir = self.sec_edgar_dir / "chinese"
        if chinese_dir.exists():
            chinese_files = list(chinese_dir.glob("*.json"))
            logging.info(f"Found {len(chinese_files)} files in chinese directory")

            for filepath in chinese_files:
                if not filepath.name.startswith(("chinese_companies", "sec_edgar")):
                    self.import_company(filepath)

        self.conn.commit()
        logging.info("All companies imported successfully")

    def generate_statistics(self):
        """Generate and display import statistics"""
        logging.info("\n" + "="*60)
        logging.info("SEC EDGAR SQL IMPORT STATISTICS")
        logging.info("="*60)

        # Get counts
        self.cursor.execute("SELECT COUNT(*) FROM sec_edgar_companies")
        total_companies = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COUNT(*) FROM sec_edgar_companies WHERE is_chinese = 1")
        chinese_companies = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COUNT(*) FROM sec_edgar_filings")
        total_filings = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COUNT(*) FROM sec_edgar_addresses")
        total_addresses = self.cursor.fetchone()[0]

        # Top Chinese companies by filings
        self.cursor.execute("""
        SELECT c.ticker, c.name, COUNT(f.id) as filing_count
        FROM sec_edgar_companies c
        LEFT JOIN sec_edgar_filings f ON c.cik = f.cik
        WHERE c.is_chinese = 1
        GROUP BY c.cik
        ORDER BY filing_count DESC
        LIMIT 10
        """)
        top_companies = self.cursor.fetchall()

        # SIC code distribution
        self.cursor.execute("""
        SELECT sic, sic_description, COUNT(*) as count
        FROM sec_edgar_companies
        WHERE is_chinese = 1 AND sic IS NOT NULL
        GROUP BY sic
        ORDER BY count DESC
        LIMIT 10
        """)
        sic_distribution = self.cursor.fetchall()

        logging.info(f"Total Companies: {total_companies}")
        logging.info(f"Chinese Companies: {chinese_companies}")
        logging.info(f"Total Filings: {total_filings}")
        logging.info(f"Total Addresses: {total_addresses}")
        logging.info(f"Import Errors: {len(self.stats['errors'])}")

        logging.info("\nTop Chinese Companies by Filing Count:")
        for ticker, name, count in top_companies:
            logging.info(f"  {ticker}: {name[:40]} - {count} filings")

        logging.info("\nChinese Companies by Industry (SIC):")
        for sic, desc, count in sic_distribution:
            logging.info(f"  {sic}: {desc[:30]} - {count} companies")

        logging.info("="*60)

    def run(self):
        """Execute the complete import process"""
        try:
            # Create tables
            self.create_tables()

            # Import all companies
            self.import_all_companies()

            # Generate statistics
            self.generate_statistics()

            # Save any errors
            if self.stats["errors"]:
                error_file = Path("sec_edgar_import_errors.txt")
                with open(error_file, 'w') as f:
                    for error in self.stats["errors"]:
                        f.write(f"{error}\n")
                logging.warning(f"Import errors saved to {error_file}")

            logging.info("\nSEC EDGAR data successfully imported to SQL database!")
            logging.info(f"Database location: {self.db_path}")

        except Exception as e:
            logging.error(f"Fatal error during import: {e}")
            self.conn.rollback()
            raise
        finally:
            self.conn.close()

def main():
    """Main execution function"""
    importer = SECEdgarSQLImporter()
    importer.run()

if __name__ == "__main__":
    main()

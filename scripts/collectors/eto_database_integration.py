#!/usr/bin/env python3
"""
ETO Database Integration - Import ETO datasets into osint_master.db

Handles CSV imports for all 6 ETO datasets with proper schema and indexing.
"""

import sqlite3
import csv
import zipfile
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# Database location
WAREHOUSE_DB = Path("F:/OSINT_WAREHOUSE/osint_master.db")


class ETODatabaseIntegration:
    """Import ETO datasets into osint_master.db"""

    def __init__(self):
        self.conn = None
        self.cursor = None

    def __enter__(self):
        """Context manager entry"""
        self.conn = sqlite3.connect(WAREHOUSE_DB)
        self.cursor = self.conn.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.conn:
            self.conn.close()

    def create_schemas(self):
        """Create all ETO dataset tables"""
        logger.info("Creating ETO dataset schemas...")

        schemas = [
            # Country AI Activity Metrics (9 tables from ZIP)
            """
            CREATE TABLE IF NOT EXISTS eto_country_ai_publications_yearly (
                country TEXT,
                field TEXT,
                year INTEGER,
                article_count INTEGER,
                imported_at TEXT,
                PRIMARY KEY (country, field, year)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS eto_country_ai_publications_citations (
                country TEXT,
                field TEXT,
                year INTEGER,
                citation_count INTEGER,
                imported_at TEXT,
                PRIMARY KEY (country, field, year)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS eto_country_ai_publications_summary (
                country TEXT,
                field TEXT,
                total_articles INTEGER,
                total_citations INTEGER,
                avg_citations_per_article REAL,
                imported_at TEXT,
                PRIMARY KEY (country, field)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS eto_country_ai_patents_applications (
                country TEXT,
                field TEXT,
                year INTEGER,
                application_count INTEGER,
                imported_at TEXT,
                PRIMARY KEY (country, field, year)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS eto_country_ai_patents_granted (
                country TEXT,
                field TEXT,
                year INTEGER,
                granted_count INTEGER,
                imported_at TEXT,
                PRIMARY KEY (country, field, year)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS eto_country_ai_patents_summary (
                country TEXT,
                field TEXT,
                total_applications INTEGER,
                total_granted INTEGER,
                grant_rate REAL,
                imported_at TEXT,
                PRIMARY KEY (country, field)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS eto_country_ai_companies_disclosed (
                country TEXT,
                field TEXT,
                year INTEGER,
                disclosed_investment_usd REAL,
                company_count INTEGER,
                imported_at TEXT,
                PRIMARY KEY (country, field, year)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS eto_country_ai_companies_estimated (
                country TEXT,
                field TEXT,
                year INTEGER,
                estimated_investment_usd REAL,
                company_count INTEGER,
                imported_at TEXT,
                PRIMARY KEY (country, field, year)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS eto_country_ai_companies_summary (
                country TEXT,
                field TEXT,
                total_disclosed_usd REAL,
                total_estimated_usd REAL,
                total_companies INTEGER,
                imported_at TEXT,
                PRIMARY KEY (country, field)
            )
            """,

            # Semiconductor Supply Chain (5 tables)
            """
            CREATE TABLE IF NOT EXISTS eto_semiconductor_inputs (
                input_id TEXT PRIMARY KEY,
                input_name TEXT,
                input_type TEXT,
                stage TEXT,
                market_size_usd_billions REAL,
                market_year INTEGER,
                description TEXT,
                imported_at TEXT
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS eto_semiconductor_providers (
                provider_id TEXT PRIMARY KEY,
                provider_name TEXT,
                country TEXT,
                provider_type TEXT,
                description TEXT,
                imported_at TEXT
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS eto_semiconductor_provision (
                provision_id TEXT PRIMARY KEY,
                input_id TEXT,
                provider_id TEXT,
                market_share_percent REAL,
                notes TEXT,
                imported_at TEXT,
                FOREIGN KEY (input_id) REFERENCES eto_semiconductor_inputs(input_id),
                FOREIGN KEY (provider_id) REFERENCES eto_semiconductor_providers(provider_id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS eto_semiconductor_sequence (
                sequence_id TEXT PRIMARY KEY,
                parent_input_id TEXT,
                child_input_id TEXT,
                relationship_type TEXT,
                imported_at TEXT,
                FOREIGN KEY (parent_input_id) REFERENCES eto_semiconductor_inputs(input_id),
                FOREIGN KEY (child_input_id) REFERENCES eto_semiconductor_inputs(input_id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS eto_semiconductor_stages (
                stage_id TEXT PRIMARY KEY,
                stage_name TEXT,
                stage_order INTEGER,
                description TEXT,
                imported_at TEXT
            )
            """,

            # Cross-Border Research (1 table)
            """
            CREATE TABLE IF NOT EXISTS eto_cross_border_research (
                research_id INTEGER PRIMARY KEY AUTOINCREMENT,
                country_1 TEXT,
                country_2 TEXT,
                technology_domain TEXT,
                year INTEGER,
                collaboration_count INTEGER,
                paper_count INTEGER,
                imported_at TEXT
            )
            """,

            # Private Sector AI (1 table)
            """
            CREATE TABLE IF NOT EXISTS eto_private_sector_ai (
                company_id TEXT,
                company_name TEXT,
                country TEXT,
                year INTEGER,
                metric_type TEXT,
                metric_value REAL,
                imported_at TEXT,
                PRIMARY KEY (company_id, year, metric_type)
            )
            """,

            # AGORA AI Governance (2 tables)
            """
            CREATE TABLE IF NOT EXISTS eto_agora_documents (
                document_id TEXT PRIMARY KEY,
                title TEXT,
                country TEXT,
                jurisdiction TEXT,
                document_type TEXT,
                publication_date TEXT,
                url TEXT,
                topics TEXT,
                imported_at TEXT
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS eto_agora_metadata (
                document_id TEXT,
                metadata_key TEXT,
                metadata_value TEXT,
                imported_at TEXT,
                PRIMARY KEY (document_id, metadata_key),
                FOREIGN KEY (document_id) REFERENCES eto_agora_documents(document_id)
            )
            """,

            # OpenAlex Overlay (1 table)
            """
            CREATE TABLE IF NOT EXISTS eto_openalex_overlay (
                work_id TEXT PRIMARY KEY,
                emerging_tech_label TEXT,
                confidence_score REAL,
                tech_domain TEXT,
                imported_at TEXT
            )
            """
        ]

        for schema in schemas:
            self.cursor.execute(schema)

        self.conn.commit()
        logger.info("ETO schemas created successfully")

    def create_indexes(self):
        """Create indexes for performance"""
        logger.info("Creating indexes...")

        indexes = [
            # Country AI indexes
            "CREATE INDEX IF NOT EXISTS idx_country_ai_pub_country ON eto_country_ai_publications_yearly(country)",
            "CREATE INDEX IF NOT EXISTS idx_country_ai_pub_year ON eto_country_ai_publications_yearly(year)",
            "CREATE INDEX IF NOT EXISTS idx_country_ai_patents_country ON eto_country_ai_patents_applications(country)",
            "CREATE INDEX IF NOT EXISTS idx_country_ai_companies_country ON eto_country_ai_companies_disclosed(country)",

            # Semiconductor indexes
            "CREATE INDEX IF NOT EXISTS idx_semiconductor_providers_country ON eto_semiconductor_providers(country)",
            "CREATE INDEX IF NOT EXISTS idx_semiconductor_provision_input ON eto_semiconductor_provision(input_id)",
            "CREATE INDEX IF NOT EXISTS idx_semiconductor_provision_provider ON eto_semiconductor_provision(provider_id)",

            # Cross-border indexes
            "CREATE INDEX IF NOT EXISTS idx_cross_border_country1 ON eto_cross_border_research(country_1)",
            "CREATE INDEX IF NOT EXISTS idx_cross_border_country2 ON eto_cross_border_research(country_2)",
            "CREATE INDEX IF NOT EXISTS idx_cross_border_tech ON eto_cross_border_research(technology_domain)",

            # Private sector indexes
            "CREATE INDEX IF NOT EXISTS idx_private_sector_country ON eto_private_sector_ai(country)",
            "CREATE INDEX IF NOT EXISTS idx_private_sector_year ON eto_private_sector_ai(year)",

            # AGORA indexes
            "CREATE INDEX IF NOT EXISTS idx_agora_country ON eto_agora_documents(country)",
            "CREATE INDEX IF NOT EXISTS idx_agora_type ON eto_agora_documents(document_type)",
            "CREATE INDEX IF NOT EXISTS idx_agora_date ON eto_agora_documents(publication_date)",

            # OpenAlex overlay indexes
            "CREATE INDEX IF NOT EXISTS idx_openalex_overlay_domain ON eto_openalex_overlay(tech_domain)"
        ]

        for index in indexes:
            self.cursor.execute(index)

        self.conn.commit()
        logger.info("Indexes created successfully")

    def extract_zip(self, zip_path: Path, extract_dir: Path) -> List[Path]:
        """Extract ZIP file and return list of extracted CSV files"""
        logger.info(f"Extracting {zip_path.name}...")

        extract_dir.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)

        # Find all CSV files in extracted directory
        csv_files = list(extract_dir.glob("**/*.csv"))
        logger.info(f"Extracted {len(csv_files)} CSV files")

        return csv_files

    def import_csv_generic(self, csv_path: Path, table_name: str,
                          column_mapping: Dict[str, str] = None) -> int:
        """
        Generic CSV import with optional column mapping.

        Args:
            csv_path: Path to CSV file
            table_name: Target table name
            column_mapping: Optional dict mapping CSV columns to DB columns

        Returns:
            Number of rows imported
        """
        logger.info(f"Importing {csv_path.name} into {table_name}...")

        rows_imported = 0
        timestamp = datetime.now(timezone.utc).isoformat()

        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)

                for row in reader:
                    # Apply column mapping if provided
                    if column_mapping:
                        # Only map columns that exist in CSV and have a mapping
                        mapped_row = {}
                        for csv_col, db_col in column_mapping.items():
                            if csv_col in row and row[csv_col]:  # Only if column exists and has value
                                mapped_row[db_col] = row[csv_col]
                    else:
                        mapped_row = row

                    # Add import timestamp
                    mapped_row['imported_at'] = timestamp

                    # Special handling for provision table (needs provision_id)
                    if table_name == 'eto_semiconductor_provision':
                        # Generate provision_id from input_id + provider_id
                        if 'input_id' in mapped_row and 'provider_id' in mapped_row:
                            mapped_row['provision_id'] = f"{mapped_row['provider_id']}_{mapped_row['input_id']}"

                    # Special handling for sequence table (needs sequence_id)
                    if table_name == 'eto_semiconductor_sequence':
                        # Generate sequence_id from child_id + parent_id + relationship
                        if 'child_input_id' in mapped_row:
                            parent_id = mapped_row.get('parent_input_id', 'none')
                            rel_type = mapped_row.get('relationship_type', 'none')
                            mapped_row['sequence_id'] = f"{mapped_row['child_input_id']}_{parent_id}_{rel_type}"

                    # Generate INSERT statement
                    columns = list(mapped_row.keys())
                    placeholders = ','.join(['?' for _ in columns])
                    values = [mapped_row[col] for col in columns]

                    sql = f"INSERT OR REPLACE INTO {table_name} ({','.join(columns)}) VALUES ({placeholders})"
                    self.cursor.execute(sql, values)

                    rows_imported += 1

                    if rows_imported % 1000 == 0:
                        self.conn.commit()
                        logger.info(f"  Imported {rows_imported} rows...")

            self.conn.commit()
            logger.info(f"✓ Imported {rows_imported} rows into {table_name}")

        except Exception as e:
            logger.error(f"Error importing {csv_path.name}: {e}")
            self.conn.rollback()

        return rows_imported

    def import_semiconductor_supply_chain(self, download_dir: Path) -> Dict[str, int]:
        """Import semiconductor supply chain CSVs"""
        logger.info("Importing semiconductor supply chain data...")

        stats = {}

        # Map CSV files to tables with column mappings
        file_configs = {
            'inputs.csv': {
                'table': 'eto_semiconductor_inputs',
                'columns': {
                    'input_id': 'input_id',
                    'input_name': 'input_name',
                    'type': 'input_type',
                    'stage_name': 'stage',
                    'description': 'description',
                    'year': 'market_year',
                    'market_share_chart_global_market_size_info': 'market_size_usd_billions'
                }
            },
            'providers.csv': {
                'table': 'eto_semiconductor_providers',
                'columns': {
                    'provider_id': 'provider_id',
                    'provider_name': 'provider_name',
                    'country': 'country',
                    'provider_type': 'provider_type',
                    'alias': 'description'
                }
            },
            'provision.csv': {
                'table': 'eto_semiconductor_provision',
                'columns': {
                    'provided_id': 'input_id',
                    'provider_id': 'provider_id',
                    'share_provided': 'market_share_percent',
                    'source': 'notes'
                }
            },
            'sequence.csv': {
                'table': 'eto_semiconductor_sequence',
                'columns': {
                    'goes_into_id': 'parent_input_id',
                    'input_id': 'child_input_id',
                    'is_type_of_id': 'relationship_type'
                }
            },
            'stages.csv': {
                'table': 'eto_semiconductor_stages',
                'columns': {
                    'stage_id': 'stage_id',
                    'stage_name': 'stage_name',
                    'description': 'description'
                }
            }
        }

        for csv_file, config in file_configs.items():
            csv_path = download_dir / csv_file
            if csv_path.exists():
                rows = self.import_csv_generic(csv_path, config['table'], config['columns'])
                stats[config['table']] = rows

        return stats

    def import_country_ai_metrics(self, zip_path: Path) -> Dict[str, int]:
        """Import Country AI Activity Metrics from ZIP"""
        logger.info("Importing Country AI Activity Metrics...")

        stats = {}

        # Extract ZIP
        extract_dir = zip_path.parent / "cat"
        csv_files = self.extract_zip(zip_path, extract_dir)

        # Map CSV files to tables with column mappings
        file_configs = {
            'publications_yearly_articles.csv': {
                'table': 'eto_country_ai_publications_yearly',
                'columns': {'country': 'country', 'field': 'field', 'year': 'year', 'num_articles': 'article_count'}
            },
            'publications_yearly_citations.csv': {
                'table': 'eto_country_ai_publications_citations',
                'columns': {'country': 'country', 'field': 'field', 'year': 'year', 'num_citations': 'citation_count'}
            },
            'publications_summary.csv': {
                'table': 'eto_country_ai_publications_summary',
                'columns': {'country': 'country', 'field': 'field', 'num_articles': 'total_articles',
                           'num_citations': 'total_citations', 'citations_per_article': 'avg_citations_per_article'}
            },
            'patents_yearly_applications.csv': {
                'table': 'eto_country_ai_patents_applications',
                'columns': {'country': 'country', 'field': 'field', 'year': 'year', 'num_applications': 'application_count'}
            },
            'patents_yearly_granted.csv': {
                'table': 'eto_country_ai_patents_granted',
                'columns': {'country': 'country', 'field': 'field', 'year': 'year', 'num_granted': 'granted_count'}
            },
            'patents_summary.csv': {
                'table': 'eto_country_ai_patents_summary',
                'columns': {'country': 'country', 'field': 'field', 'num_applications': 'total_applications',
                           'num_granted': 'total_granted', 'grant_rate': 'grant_rate'}
            },
            'companies_yearly_disclosed.csv': {
                'table': 'eto_country_ai_companies_disclosed',
                'columns': {'country': 'country', 'field': 'field', 'year': 'year',
                           'disclosed_investment': 'disclosed_investment_usd', 'num_companies': 'company_count'}
            },
            'companies_yearly_estimated.csv': {
                'table': 'eto_country_ai_companies_estimated',
                'columns': {'country': 'country', 'field': 'field', 'year': 'year',
                           'estimated_investment': 'estimated_investment_usd', 'num_companies': 'company_count'}
            },
            'companies_summary.csv': {
                'table': 'eto_country_ai_companies_summary',
                'columns': {'country': 'country', 'field': 'field', 'disclosed_investment': 'total_disclosed_usd',
                           'estimated_investment': 'total_estimated_usd', 'num_companies': 'total_companies'}
            }
        }

        for csv_file in csv_files:
            # Find matching configuration
            for file_pattern, config in file_configs.items():
                if file_pattern in csv_file.name:
                    rows = self.import_csv_generic(csv_file, config['table'], config['columns'])
                    stats[config['table']] = rows
                    break

        return stats

    def import_all_datasets(self, download_dir: Path) -> Dict[str, Dict[str, int]]:
        """
        Import all downloaded ETO datasets.

        Args:
            download_dir: F:/ETO_Datasets/downloads/

        Returns:
            Dict of dataset stats
        """
        logger.info("Starting import of all ETO datasets...")

        all_stats = {}

        # 1. Country AI Metrics (ZIP)
        country_ai_dir = download_dir / "country_ai_metrics"
        if country_ai_dir.exists():
            # Find latest version
            versions = sorted(country_ai_dir.glob("*"), reverse=True)
            if versions:
                zip_files = list(versions[0].glob("*.zip"))
                if zip_files:
                    stats = self.import_country_ai_metrics(zip_files[0])
                    all_stats['country_ai_metrics'] = stats

        # 2. Semiconductor Supply Chain (CSVs)
        semiconductor_dir = download_dir / "semiconductor_supply_chain"
        if semiconductor_dir.exists():
            # Find latest version
            versions = sorted(semiconductor_dir.glob("*"), reverse=True)
            if versions:
                stats = self.import_semiconductor_supply_chain(versions[0])
                all_stats['semiconductor_supply_chain'] = stats

        # 3. Cross-Border Research (will implement after seeing CSV structure)
        # 4. Private Sector AI (will implement after seeing CSV structure)
        # 5. AGORA (will implement after seeing CSV structure)
        # 6. OpenAlex Overlay (will implement after seeing CSV structure)

        logger.info("Import complete!")
        return all_stats


def main():
    """Test import"""
    logging.basicConfig(level=logging.INFO)

    with ETODatabaseIntegration() as db:
        # Create schemas
        db.create_schemas()
        db.create_indexes()

        # Import datasets
        download_dir = Path("F:/ETO_Datasets/downloads")
        stats = db.import_all_datasets(download_dir)

        print("\nImport Statistics:")
        for dataset, tables in stats.items():
            print(f"\n{dataset}:")
            for table, rows in tables.items():
                print(f"  {table}: {rows} rows")


if __name__ == "__main__":
    main()

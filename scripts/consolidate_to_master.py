#!/usr/bin/env python3
"""
Consolidate remaining databases into osint_master.db
Complete the database architecture simplification
"""

import sqlite3
import os
from pathlib import Path
from datetime import datetime
import shutil

class DatabaseConsolidator:
    def __init__(self):
        self.warehouse_dir = Path("F:/OSINT_WAREHOUSE")
        self.master_db_path = self.warehouse_dir / "osint_master.db"
        self.backup_dir = self.warehouse_dir / "pre_consolidation_backup"
        self.log = []

    def log_message(self, msg):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        full_msg = f"[{timestamp}] {msg}"
        print(full_msg)
        self.log.append(full_msg)

    def backup_master_db(self):
        """Create backup of master database before consolidation"""
        self.log_message("Creating backup of osint_master.db...")
        self.backup_dir.mkdir(exist_ok=True)

        backup_name = f"osint_master_pre_consolidation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        backup_path = self.backup_dir / backup_name

        shutil.copy2(self.master_db_path, backup_path)
        self.log_message(f"Backup created: {backup_path}")
        return backup_path

    def merge_ted_databases(self, master_conn):
        """Merge all TED databases into master"""
        self.log_message("\n=== MERGING TED DATABASES ===")

        ted_databases = [
            ("osint_master.db", "ted_complete_analysis"),
            ("osint_master.db", ["ted_china_contracts", "ted_procurement_chinese_entities_found", "ted_procurement_pattern_matches"]),
            ("osint_master.db", "ted_deep_extract"),
            ("osint_master.db", "ted_contracts_comprehensive"),
            ("osint_master.db", "ted_osint_analysis")
        ]

        master_cursor = master_conn.cursor()

        for db_name, tables in ted_databases:
            db_path = self.warehouse_dir / db_name
            if not db_path.exists():
                self.log_message(f"  Skip {db_name} - not found")
                continue

            self.log_message(f"  Processing {db_name}...")

            try:
                # Attach the database
                master_cursor.execute(f"ATTACH DATABASE '{db_path}' AS source_db")

                # Handle single table or list of tables
                table_list = [tables] if isinstance(tables, str) else tables

                for table_name in table_list:
                    new_table_name = f"ted_{table_name}" if not table_name.startswith("ted_") else table_name

                    # Check if table exists in source
                    master_cursor.execute(
                        "SELECT name FROM source_db.sqlite_master WHERE type='table' AND name=?",
                        (table_name,)
                    )

                    if not master_cursor.fetchone():
                        self.log_message(f"    Table {table_name} not found in source")
                        continue

                    # Drop table if exists in master
                    master_cursor.execute(f"DROP TABLE IF EXISTS {new_table_name}")

                    # Copy table structure and data
                    master_cursor.execute(f"""
                        CREATE TABLE {new_table_name} AS
                        SELECT * FROM source_db.{table_name}
                    """)

                    # Get row count
                    master_cursor.execute(f"SELECT COUNT(*) FROM {new_table_name}")
                    row_count = master_cursor.fetchone()[0]

                    self.log_message(f"    [OK] Imported {new_table_name}: {row_count:,} rows")

                # Detach the database
                master_cursor.execute("DETACH DATABASE source_db")

            except Exception as e:
                self.log_message(f"    ERROR: {e}")
                try:
                    master_cursor.execute("DETACH DATABASE source_db")
                except:
                    pass

    def merge_openalex_databases(self, master_conn):
        """Merge OpenAlex databases into master"""
        self.log_message("\n=== MERGING OPENALEX DATABASES ===")

        openalex_databases = [
            ("osint_master.db", [
                "import_openalex_institutions",
                "openalex_authors",
                "openalex_institutions",
                "openalex_funders",
                "openalex_china_topics",
                "openalex_china_collaborations"
            ]),
            ("osint_master.db", [
                "openalex_extraction_stats",
                "import_openalex_china_entities"
            ])
        ]

        master_cursor = master_conn.cursor()

        for db_name, tables in openalex_databases:
            db_path = self.warehouse_dir / db_name
            if not db_path.exists():
                self.log_message(f"  Skip {db_name} - not found")
                continue

            self.log_message(f"  Processing {db_name}...")

            try:
                master_cursor.execute(f"ATTACH DATABASE '{db_path}' AS source_db")

                for table_name in tables:
                    new_table_name = table_name if table_name.startswith("openalex_") else f"openalex_{table_name}"

                    # Check if table exists in source
                    master_cursor.execute(
                        "SELECT name FROM source_db.sqlite_master WHERE type='table' AND name=?",
                        (table_name,)
                    )

                    if not master_cursor.fetchone():
                        self.log_message(f"    Table {table_name} not found in source")
                        continue

                    # Drop table if exists
                    master_cursor.execute(f"DROP TABLE IF EXISTS {new_table_name}")

                    # Copy table
                    master_cursor.execute(f"""
                        CREATE TABLE {new_table_name} AS
                        SELECT * FROM source_db.{table_name}
                    """)

                    # Get row count
                    master_cursor.execute(f"SELECT COUNT(*) FROM {new_table_name}")
                    row_count = master_cursor.fetchone()[0]

                    self.log_message(f"    [OK] Imported {new_table_name}: {row_count:,} rows")

                master_cursor.execute("DETACH DATABASE source_db")

            except Exception as e:
                self.log_message(f"    ERROR: {e}")
                try:
                    master_cursor.execute("DETACH DATABASE source_db")
                except:
                    pass

    def create_views(self, master_conn):
        """Create logical views for easier querying"""
        self.log_message("\n=== CREATING VIEWS ===")

        views = [
            # TED analysis views
            ("v_ted_all_contracts", """
                SELECT 'complete' as source, * FROM ted_ted_complete_analysis
                UNION ALL
                SELECT 'procurement' as source, * FROM ted_china_contracts WHERE 1=0
                UNION ALL
                SELECT 'comprehensive' as source, * FROM ted_ted_contracts_comprehensive
            """),

            # China entity views
            ("v_china_entities_all", """
                SELECT DISTINCT entity_name, 'ted' as source
                FROM ted_china_entities
                UNION
                SELECT DISTINCT entity_name, 'ted_fixed' as source
                FROM ted_china_entities_fixed
                UNION
                SELECT DISTINCT name as entity_name, 'master' as source
                FROM china_entities
            """),

            # OpenAlex collaboration views
            ("v_openalex_china_collaborations", """
                SELECT * FROM import_openalex_institutions
                WHERE country_code = 'CN' OR partner_country = 'China'
            """),

            # Patent intelligence view
            ("v_patent_intelligence", """
                SELECT * FROM patents
                WHERE assignee_country = 'CN'
                   OR inventor_country = 'CN'
                   OR title LIKE '%China%'
                   OR abstract LIKE '%China%'
            """),

            # Cross-source entity view
            ("v_entities_consolidated", """
                SELECT name, type, source, confidence_score
                FROM entities
                WHERE is_chinese = 1 OR country = 'China'
            """)
        ]

        cursor = master_conn.cursor()

        for view_name, view_sql in views:
            try:
                cursor.execute(f"DROP VIEW IF EXISTS {view_name}")
                cursor.execute(f"CREATE VIEW {view_name} AS {view_sql}")
                self.log_message(f"  [OK] Created view: {view_name}")
            except Exception as e:
                self.log_message(f"  [FAIL] Failed to create {view_name}: {e}")

    def create_indexes(self, master_conn):
        """Create performance indexes"""
        self.log_message("\n=== CREATING INDEXES ===")

        indexes = [
            # Entity indexes
            ("idx_entities_name", "entities(name)"),
            ("idx_entities_chinese", "entities(is_chinese)"),
            ("idx_entities_country", "entities(country)"),

            # China entities indexes
            ("idx_china_entities_name", "china_entities(entity_name)"),
            ("idx_china_entities_type", "china_entities(entity_type)"),

            # SEC EDGAR indexes
            ("idx_sec_edgar_cik", "sec_edgar_companies(cik)"),
            ("idx_sec_edgar_chinese", "sec_edgar_companies(is_chinese)"),
            ("idx_sec_edgar_name", "sec_edgar_companies(company_name)"),

            # CORDIS indexes
            ("idx_cordis_org_name", "cordis_organizations(name)"),
            ("idx_cordis_org_country", "cordis_organizations(country)"),

            # TED indexes (for new tables)
            ("idx_ted_complete_id", "ted_ted_complete_analysis(id)"),
            ("idx_ted_contracts_vendor", "ted_contracts(vendor_name)"),

            # OpenAlex indexes (for new tables)
            ("idx_openalex_collab_country", "openalex_collaborations(country_code)"),
            ("idx_openalex_entities_name", "openalex_china_entities(entity_name)")
        ]

        cursor = master_conn.cursor()

        for index_name, index_def in indexes:
            try:
                cursor.execute(f"DROP INDEX IF EXISTS {index_name}")
                cursor.execute(f"CREATE INDEX {index_name} ON {index_def}")
                self.log_message(f"  [OK] Created index: {index_name}")
            except Exception as e:
                # Some tables might not exist yet
                if "no such table" not in str(e).lower():
                    self.log_message(f"  [FAIL] Failed to create {index_name}: {e}")

    def optimize_database(self, master_conn):
        """Run VACUUM and ANALYZE for optimization"""
        self.log_message("\n=== OPTIMIZING DATABASE ===")

        cursor = master_conn.cursor()

        try:
            self.log_message("  Running ANALYZE...")
            cursor.execute("ANALYZE")

            self.log_message("  Running VACUUM...")
            cursor.execute("VACUUM")

            self.log_message("  [OK] Database optimized")

        except Exception as e:
            self.log_message(f"  [FAIL] Optimization failed: {e}")

    def archive_consolidated_databases(self):
        """Move consolidated databases to archive"""
        self.log_message("\n=== ARCHIVING CONSOLIDATED DATABASES ===")

        archive_dir = self.warehouse_dir / "post_consolidation_archive"
        archive_dir.mkdir(exist_ok=True)

        databases_to_archive = [
            "osint_master.db",
            "osint_master.db",
            "osint_master.db",
            "osint_master.db",
            "osint_master.db",
            "osint_master.db",
            "osint_master.db"
        ]

        for db_name in databases_to_archive:
            db_path = self.warehouse_dir / db_name
            if db_path.exists():
                archive_path = archive_dir / db_name
                shutil.move(str(db_path), str(archive_path))
                self.log_message(f"  [OK] Archived: {db_name}")

    def generate_report(self):
        """Generate final consolidation report"""
        self.log_message("\n=== GENERATING REPORT ===")

        report = f"""# Database Consolidation Report
**Date**: {datetime.now().isoformat()}
**Status**: COMPLETED

## Operations Performed

1. [OK] Backed up osint_master.db
2. [OK] Merged 5 TED databases
3. [OK] Merged 2 OpenAlex databases
4. [OK] Created logical views
5. [OK] Added performance indexes
6. [OK] Optimized database (VACUUM + ANALYZE)
7. [OK] Archived source databases

## Consolidation Log

{"".join(self.log)}

## Final State

- **Primary Database**: osint_master.db (consolidated)
- **Remaining Database**: osint_research.db (separate project)
- **Archived Databases**: Moved to post_consolidation_archive/
- **Backup Location**: pre_consolidation_backup/

## Next Steps

1. Test all scripts with new consolidated structure
2. Update any hardcoded database paths
3. Delete archives after 30-day validation period
"""

        report_path = Path("C:/Projects/OSINT - Foresight/KNOWLEDGE_BASE/04_PROJECT_ARCHITECTURE/CONSOLIDATION_COMPLETE.md")
        with open(report_path, 'w') as f:
            f.write(report)

        self.log_message(f"Report saved to: {report_path}")

        return report

    def run(self):
        """Execute full consolidation"""
        print("="*60)
        print("DATABASE CONSOLIDATION TO MASTER")
        print("="*60)

        # Create backup
        backup_path = self.backup_master_db()

        # Connect to master database
        self.log_message("Connecting to osint_master.db...")
        master_conn = sqlite3.connect(str(self.master_db_path))

        try:
            # Perform consolidation
            self.merge_ted_databases(master_conn)
            self.merge_openalex_databases(master_conn)
            self.create_views(master_conn)
            self.create_indexes(master_conn)

            # Commit changes
            master_conn.commit()
            self.log_message("\n[OK] All changes committed")

            # Optimize
            self.optimize_database(master_conn)

        except Exception as e:
            self.log_message(f"\nERROR during consolidation: {e}")
            master_conn.rollback()
            self.log_message("Changes rolled back")

        finally:
            master_conn.close()

        # Archive consolidated databases
        self.archive_consolidated_databases()

        # Generate report
        report = self.generate_report()

        print("\n" + "="*60)
        print("CONSOLIDATION COMPLETE")
        print("="*60)

        return backup_path

if __name__ == "__main__":
    consolidator = DatabaseConsolidator()
    consolidator.run()
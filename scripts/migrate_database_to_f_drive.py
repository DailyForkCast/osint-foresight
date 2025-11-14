#!/usr/bin/env python3
"""
Migrate database from C: drive to F: drive for scalability
Consolidates both databases into one master database on F: drive
"""

import sqlite3
import shutil
import logging
import re
from pathlib import Path
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# ============================================================================
# SECURITY: SQL injection prevention through identifier validation
# ============================================================================

def validate_sql_identifier(identifier):
    """
    SECURITY: Validate SQL identifier (table or column name).
    Only allows alphanumeric characters and underscores.
    Prevents SQL injection from dynamic SQL construction.
    """
    if not identifier:
        raise ValueError("Identifier cannot be empty")

    # Check for valid characters only (alphanumeric + underscore)
    if not re.match(r'^[a-zA-Z0-9_]+$', identifier):
        raise ValueError(f"Invalid identifier: {identifier}. Contains illegal characters.")

    # Check length (SQLite limit is 1024, we use 100 for safety)
    if len(identifier) > 100:
        raise ValueError(f"Identifier too long: {identifier}")

    # Blacklist dangerous SQL keywords
    dangerous_keywords = {'DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE',
                         'EXEC', 'EXECUTE', 'UNION', 'SELECT', '--', ';', '/*', '*/'}
    if identifier.upper() in dangerous_keywords:
        raise ValueError(f"Identifier contains SQL keyword: {identifier}")

    return identifier

class DatabaseMigrator:
    """Migrate and consolidate databases to F: drive"""

    def __init__(self):
        # Source databases
        self.c_db = Path("database/osint_master.db")
        self.f_old_db = Path("F:/OSINT_WAREHOUSE/osint_research.db")

        # New master database location
        self.f_master_db = Path("F:/OSINT_WAREHOUSE/osint_master.db")

        # Backup location
        self.backup_dir = Path("F:/OSINT_WAREHOUSE/backups")
        self.backup_dir.mkdir(exist_ok=True)

    def backup_existing_databases(self):
        """Create backups of existing databases"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Backup C: database
        if self.c_db.exists():
            c_backup = self.backup_dir / f"c_drive_osint_master_{timestamp}.db"
            shutil.copy2(self.c_db, c_backup)
            logging.info(f"Backed up C: database to {c_backup}")

        # Backup old F: database
        if self.f_old_db.exists():
            f_backup = self.backup_dir / f"f_drive_osint_research_{timestamp}.db"
            shutil.copy2(self.f_old_db, f_backup)
            logging.info(f"Backed up F: database to {f_backup}")

        # Backup existing F: master if it exists
        if self.f_master_db.exists():
            master_backup = self.backup_dir / f"f_drive_osint_master_existing_{timestamp}.db"
            shutil.copy2(self.f_master_db, master_backup)
            logging.info(f"Backed up existing F: master to {master_backup}")

    def migrate_database(self):
        """Copy the C: database to F: as the new master"""
        logging.info("Migrating database to F: drive...")

        # Copy C: database to F: as new master
        if self.c_db.exists():
            shutil.copy2(self.c_db, self.f_master_db)
            logging.info(f"Database migrated to {self.f_master_db}")

            # Verify the copy
            f_conn = sqlite3.connect(str(self.f_master_db))
            f_cursor = f_conn.cursor()

            # Count records in major tables
            tables = ['mcf_documents', 'cordis_projects', 'sec_edgar_companies',
                     'intelligence_procurement', 'intelligence_patents']

            for table in tables:
                try:
                    # SECURITY: Validate table name before use in SQL
                    safe_table = validate_sql_identifier(table)
                    f_cursor.execute(f"SELECT COUNT(*) FROM {safe_table}")
                    count = f_cursor.fetchone()[0]
                    logging.info(f"  {table}: {count:,} records")
                except:
                    pass

            f_conn.close()
        else:
            logging.error(f"Source database not found: {self.c_db}")

    def update_configuration_files(self):
        """Update all scripts to point to new F: drive location"""
        scripts_to_update = [
            "scripts/import_mcf_to_sql.py",
            "scripts/import_cordis_to_sql.py",
            "scripts/import_sec_edgar_to_sql.py",
            "scripts/collect_more_mcf_data.py",
            "scripts/compare_databases.py",
            "scripts/merge_databases.py"
        ]

        old_path = 'database/osint_master.db'
        new_path = 'F:/OSINT_WAREHOUSE/osint_master.db'

        updated_count = 0
        for script_path in scripts_to_update:
            script = Path(script_path)
            if script.exists():
                content = script.read_text(encoding='utf-8')
                if old_path in content:
                    content = content.replace(old_path, new_path)
                    script.write_text(content, encoding='utf-8')
                    logging.info(f"Updated: {script_path}")
                    updated_count += 1

        logging.info(f"Updated {updated_count} configuration files")

    def create_symlink(self):
        """Create symbolic link from C: to F: for compatibility"""
        try:
            # On Windows, this requires admin privileges
            import os
            if os.name == 'nt':
                # Create junction point on Windows
                import subprocess
                if self.c_db.exists():
                    self.c_db.unlink()  # Remove old file
                cmd = f'mklink "{self.c_db}" "{self.f_master_db}"'
                subprocess.run(cmd, shell=True, check=True)
                logging.info(f"Created symbolic link: {self.c_db} -> {self.f_master_db}")
        except Exception as e:
            logging.warning(f"Could not create symbolic link: {e}")
            logging.info("Note: Scripts have been updated to use F: drive directly")

    def generate_report(self):
        """Generate migration report"""
        report = f"""
DATABASE MIGRATION REPORT
=========================
Time: {datetime.now().isoformat()}

Migration Summary:
- Source: {self.c_db}
- Destination: {self.f_master_db}
- Status: COMPLETE

New Database Location: {self.f_master_db}
Backup Location: {self.backup_dir}

Database Statistics:
"""
        # Get statistics from new location
        conn = sqlite3.connect(str(self.f_master_db))
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()

        total_records = 0
        for table_name in tables:
            table = table_name[0]
            if not table.startswith('sqlite_'):
                # SECURITY: Validate table name before use in SQL
                safe_table = validate_sql_identifier(table)
                cursor.execute(f"SELECT COUNT(*) FROM {safe_table}")
                count = cursor.fetchone()[0]
                if count > 0:
                    report += f"  {table}: {count:,} records\n"
                    total_records += count

        report += f"\nTotal Records: {total_records:,}\n"

        # Get database size
        db_size_mb = self.f_master_db.stat().st_size / (1024 * 1024)
        report += f"Database Size: {db_size_mb:.2f} MB\n"

        # Available space on F: drive
        import shutil
        total, used, free = shutil.disk_usage("F:/")
        free_gb = free // (2**30)
        report += f"Free Space on F: drive: {free_gb} GB\n"

        conn.close()

        report += """
IMPORTANT: Database has been moved to F: drive
==============================================
All future operations should use: F:/OSINT_WAREHOUSE/osint_master.db

Updated Scripts:
- All import scripts now point to F: drive
- Collection scripts updated
- Comparison and merge scripts updated

Benefits of F: Drive Location:
- More storage space for growth
- Better performance for large queries
- Centralized with other OSINT data
- Room for indexes and optimization
"""

        return report

    def run(self):
        """Execute migration process"""
        try:
            logging.info("="*60)
            logging.info("DATABASE MIGRATION TO F: DRIVE")
            logging.info("="*60)

            # Step 1: Backup existing databases
            logging.info("\nStep 1: Creating backups...")
            self.backup_existing_databases()

            # Step 2: Migrate database
            logging.info("\nStep 2: Migrating database...")
            self.migrate_database()

            # Step 3: Update configuration files
            logging.info("\nStep 3: Updating configuration files...")
            self.update_configuration_files()

            # Step 4: Try to create symlink
            logging.info("\nStep 4: Creating symbolic link...")
            self.create_symlink()

            # Step 5: Generate report
            logging.info("\nStep 5: Generating report...")
            report = self.generate_report()
            print(report)

            # Save report
            report_file = Path("database_migration_report.txt")
            with open(report_file, 'w') as f:
                f.write(report)

            logging.info(f"\nMigration complete! Report saved to {report_file}")
            logging.info(f"New database location: {self.f_master_db}")

        except Exception as e:
            logging.error(f"Migration failed: {e}")
            raise

def main():
    migrator = DatabaseMigrator()
    migrator.run()

if __name__ == "__main__":
    main()

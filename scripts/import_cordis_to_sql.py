#!/usr/bin/env python3
"""
CORDIS to SQL Database Importer
Imports CORDIS EU research project data with China collaborations
"""

import sqlite3
import json
import logging
from pathlib import Path
from datetime import datetime
import pandas as pd

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cordis_sql_import.log'),
        logging.StreamHandler()
    ]
)

class CORDISSQLImporter:
    """Import CORDIS data to main SQL database"""

    def __init__(self,
                 source_db: str = "data/processed/cordis_unified/cordis_china_projects.db",
                 target_db: str = "F:/OSINT_WAREHOUSE/osint_master.db"):

        self.source_db = Path(source_db)
        self.target_db = Path(target_db)
        self.target_db.parent.mkdir(parents=True, exist_ok=True)

        # JSON data file
        self.json_file = Path("data/processed/cordis_unified/cordis_complete_analysis_20250921_161957.json")

        # Connect to databases
        self.source_conn = sqlite3.connect(str(self.source_db))
        self.target_conn = sqlite3.connect(str(self.target_db))
        self.target_cursor = self.target_conn.cursor()

        # Enable foreign keys
        self.target_cursor.execute("PRAGMA foreign_keys = ON")

        logging.info(f"Source database: {self.source_db}")
        logging.info(f"Target database: {self.target_db}")

        # Statistics
        self.stats = {
            "projects_imported": 0,
            "organizations_imported": 0,
            "collaborations_imported": 0,
            "china_projects": 0,
            "errors": []
        }

    def create_tables(self):
        """Create CORDIS tables in target database"""
        logging.info("Creating CORDIS tables...")

        # Projects table
        self.target_cursor.execute("""
        CREATE TABLE IF NOT EXISTS cordis_projects (
            project_id TEXT PRIMARY KEY,
            acronym TEXT,
            title TEXT,
            objective TEXT,
            total_cost REAL,
            eu_contribution REAL,
            programme TEXT,
            funding_scheme TEXT,
            coordinator_country TEXT,
            start_date DATE,
            end_date DATE,
            status TEXT,
            has_china_collaboration BOOLEAN DEFAULT 0,
            china_collaboration_type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Organizations table
        self.target_cursor.execute("""
        CREATE TABLE IF NOT EXISTS cordis_organizations (
            org_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            short_name TEXT,
            country TEXT,
            city TEXT,
            organization_type TEXT,
            is_chinese BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(name, country)
        )
        """)

        # Project-Organization relationship table
        self.target_cursor.execute("""
        CREATE TABLE IF NOT EXISTS cordis_project_participants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id TEXT NOT NULL,
            org_id INTEGER NOT NULL,
            role TEXT,
            eu_contribution REAL,
            is_coordinator BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES cordis_projects(project_id) ON DELETE CASCADE,
            FOREIGN KEY (org_id) REFERENCES cordis_organizations(org_id) ON DELETE CASCADE,
            UNIQUE(project_id, org_id)
        )
        """)

        # China collaboration details table
        self.target_cursor.execute("""
        CREATE TABLE IF NOT EXISTS cordis_china_collaborations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id TEXT NOT NULL,
            chinese_org_name TEXT,
            collaboration_type TEXT,
            technology_area TEXT,
            risk_level TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES cordis_projects(project_id) ON DELETE CASCADE
        )
        """)

        # Project countries table
        self.target_cursor.execute("""
        CREATE TABLE IF NOT EXISTS cordis_project_countries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id TEXT NOT NULL,
            country_code TEXT NOT NULL,
            participant_count INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES cordis_projects(project_id) ON DELETE CASCADE,
            UNIQUE(project_id, country_code)
        )
        """)

        # Create indexes
        self.target_cursor.execute("CREATE INDEX IF NOT EXISTS idx_projects_china ON cordis_projects(has_china_collaboration)")
        self.target_cursor.execute("CREATE INDEX IF NOT EXISTS idx_projects_programme ON cordis_projects(programme)")
        self.target_cursor.execute("CREATE INDEX IF NOT EXISTS idx_projects_coordinator ON cordis_projects(coordinator_country)")
        self.target_cursor.execute("CREATE INDEX IF NOT EXISTS idx_orgs_country ON cordis_organizations(country)")
        self.target_cursor.execute("CREATE INDEX IF NOT EXISTS idx_orgs_chinese ON cordis_organizations(is_chinese)")
        self.target_cursor.execute("CREATE INDEX IF NOT EXISTS idx_participants_project ON cordis_project_participants(project_id)")
        self.target_cursor.execute("CREATE INDEX IF NOT EXISTS idx_participants_org ON cordis_project_participants(org_id)")
        self.target_cursor.execute("CREATE INDEX IF NOT EXISTS idx_countries_project ON cordis_project_countries(project_id)")
        self.target_cursor.execute("CREATE INDEX IF NOT EXISTS idx_countries_code ON cordis_project_countries(country_code)")

        # Create view for China collaborations
        self.target_cursor.execute("""
        CREATE VIEW IF NOT EXISTS v_cordis_china_projects AS
        SELECT
            p.project_id,
            p.acronym,
            p.title,
            p.total_cost,
            p.eu_contribution,
            p.programme,
            p.coordinator_country,
            p.start_date,
            p.end_date,
            COUNT(DISTINCT pp.org_id) as participant_count,
            COUNT(DISTINCT pc.country_code) as country_count,
            GROUP_CONCAT(DISTINCT pc.country_code) as countries
        FROM cordis_projects p
        LEFT JOIN cordis_project_participants pp ON p.project_id = pp.project_id
        LEFT JOIN cordis_project_countries pc ON p.project_id = pc.project_id
        WHERE p.has_china_collaboration = 1
        GROUP BY p.project_id
        """)

        self.target_conn.commit()
        logging.info("Tables created successfully")

    def import_from_source_db(self):
        """Import data from source CORDIS database"""
        logging.info("Importing from source database...")

        # Import projects
        projects_df = pd.read_sql_query(
            "SELECT * FROM projects",
            self.source_conn
        )

        for _, project in projects_df.iterrows():
            try:
                # Check for China involvement
                has_china = False
                if 'CN' in str(project.get('countries', '')):
                    has_china = True

                self.target_cursor.execute("""
                INSERT OR REPLACE INTO cordis_projects (
                    project_id, acronym, title, objective,
                    total_cost, eu_contribution, programme,
                    funding_scheme, coordinator_country,
                    start_date, end_date, status,
                    has_china_collaboration
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    project['project_id'],
                    project.get('acronym'),
                    project.get('title'),
                    project.get('objective'),
                    project.get('total_cost'),
                    project.get('eu_contribution'),
                    project.get('programme'),
                    project.get('funding_scheme'),
                    project.get('coordinator_country'),
                    project.get('start_date'),
                    project.get('end_date'),
                    project.get('status'),
                    has_china
                ))

                self.stats["projects_imported"] += 1
                if has_china:
                    self.stats["china_projects"] += 1

            except Exception as e:
                logging.error(f"Error importing project {project.get('project_id')}: {e}")
                self.stats["errors"].append(f"Project {project.get('project_id')}: {str(e)}")

        # Import organizations
        orgs_df = pd.read_sql_query(
            "SELECT * FROM organizations",
            self.source_conn
        )

        for _, org in orgs_df.iterrows():
            try:
                is_chinese = org.get('country') == 'CN'

                self.target_cursor.execute("""
                INSERT OR IGNORE INTO cordis_organizations (
                    name, short_name, country, city,
                    organization_type, is_chinese
                ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    org['name'],
                    org.get('short_name'),
                    org.get('country'),
                    org.get('city'),
                    org.get('organization_type'),
                    is_chinese
                ))

                self.stats["organizations_imported"] += 1

            except Exception as e:
                logging.error(f"Error importing organization {org.get('name')}: {e}")
                self.stats["errors"].append(f"Org {org.get('name')}: {str(e)}")

        # Import project countries
        countries_df = pd.read_sql_query(
            "SELECT * FROM project_countries",
            self.source_conn
        )

        for _, country in countries_df.iterrows():
            try:
                self.target_cursor.execute("""
                INSERT OR IGNORE INTO cordis_project_countries (
                    project_id, country_code, participant_count
                ) VALUES (?, ?, ?)
                """, (
                    country['project_id'],
                    country['country_code'],
                    country.get('participant_count', 1)
                ))

            except Exception as e:
                logging.error(f"Error importing country data: {e}")

        self.target_conn.commit()
        logging.info(f"Imported {self.stats['projects_imported']} projects")
        logging.info(f"Imported {self.stats['organizations_imported']} organizations")

    def import_from_json(self):
        """Import additional data from JSON analysis file"""
        if not self.json_file.exists():
            logging.warning(f"JSON file not found: {self.json_file}")
            return

        logging.info("Importing from JSON analysis...")

        with open(self.json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Process China collaborations
        for country_data in data.get('analysis_by_country', []):
            for project in country_data.get('china_projects', []):
                try:
                    project_id = project.get('project_id')
                    if not project_id:
                        continue

                    # Update project with China collaboration details
                    self.target_cursor.execute("""
                    UPDATE cordis_projects
                    SET has_china_collaboration = 1,
                        china_collaboration_type = ?
                    WHERE project_id = ?
                    """, (
                        project.get('funding_scheme'),
                        project_id
                    ))

                    # Add collaboration details
                    for participant in project.get('participants', []):
                        if participant.get('country') == 'CN':
                            self.target_cursor.execute("""
                            INSERT OR IGNORE INTO cordis_china_collaborations (
                                project_id, chinese_org_name,
                                collaboration_type, technology_area
                            ) VALUES (?, ?, ?, ?)
                            """, (
                                project_id,
                                participant.get('name'),
                                project.get('funding_scheme'),
                                project.get('programme')
                            ))
                            self.stats["collaborations_imported"] += 1

                except Exception as e:
                    logging.error(f"Error processing collaboration: {e}")

        self.target_conn.commit()
        logging.info(f"Imported {self.stats['collaborations_imported']} China collaborations")

    def generate_statistics(self):
        """Generate and display import statistics"""
        logging.info("\n" + "="*60)
        logging.info("CORDIS SQL IMPORT STATISTICS")
        logging.info("="*60)

        # Get counts
        self.target_cursor.execute("SELECT COUNT(*) FROM cordis_projects")
        total_projects = self.target_cursor.fetchone()[0]

        self.target_cursor.execute("SELECT COUNT(*) FROM cordis_projects WHERE has_china_collaboration = 1")
        china_projects = self.target_cursor.fetchone()[0]

        self.target_cursor.execute("SELECT COUNT(*) FROM cordis_organizations")
        total_orgs = self.target_cursor.fetchone()[0]

        self.target_cursor.execute("SELECT COUNT(*) FROM cordis_organizations WHERE is_chinese = 1")
        chinese_orgs = self.target_cursor.fetchone()[0]

        # Top countries collaborating with China
        self.target_cursor.execute("""
        SELECT pc.country_code, COUNT(DISTINCT pc.project_id) as project_count
        FROM cordis_project_countries pc
        JOIN cordis_projects p ON pc.project_id = p.project_id
        WHERE p.has_china_collaboration = 1
        GROUP BY pc.country_code
        ORDER BY project_count DESC
        LIMIT 10
        """)
        top_countries = self.target_cursor.fetchall()

        # Programme distribution
        self.target_cursor.execute("""
        SELECT programme, COUNT(*) as count
        FROM cordis_projects
        WHERE has_china_collaboration = 1
        GROUP BY programme
        ORDER BY count DESC
        LIMIT 5
        """)
        programmes = self.target_cursor.fetchall()

        logging.info(f"Total Projects: {total_projects}")
        logging.info(f"China Collaboration Projects: {china_projects} ({china_projects*100/total_projects:.1f}%)")
        logging.info(f"Total Organizations: {total_orgs}")
        logging.info(f"Chinese Organizations: {chinese_orgs}")

        logging.info("\nTop Countries Collaborating with China:")
        for country, count in top_countries:
            logging.info(f"  {country}: {count} projects")

        logging.info("\nChina Projects by Programme:")
        for programme, count in programmes:
            logging.info(f"  {programme}: {count} projects")

        logging.info(f"\nImport Errors: {len(self.stats['errors'])}")
        logging.info("="*60)

    def run(self):
        """Execute the complete import process"""
        try:
            # Create tables
            self.create_tables()

            # Import from source database
            self.import_from_source_db()

            # Import from JSON analysis
            self.import_from_json()

            # Generate statistics
            self.generate_statistics()

            # Save any errors
            if self.stats["errors"]:
                error_file = Path("cordis_import_errors.txt")
                with open(error_file, 'w') as f:
                    for error in self.stats["errors"]:
                        f.write(f"{error}\n")
                logging.warning(f"Import errors saved to {error_file}")

            logging.info("\nCORDIS data successfully imported to SQL database!")
            logging.info(f"Database location: {self.target_db}")

        except Exception as e:
            logging.error(f"Fatal error during import: {e}")
            self.target_conn.rollback()
            raise
        finally:
            self.source_conn.close()
            self.target_conn.close()

def main():
    """Main execution function"""
    importer = CORDISSQLImporter()
    importer.run()

if __name__ == "__main__":
    main()

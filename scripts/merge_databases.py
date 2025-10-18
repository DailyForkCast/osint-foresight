#!/usr/bin/env python3
"""
Merge missing data from F: drive database into main database
"""

import sqlite3
import logging
from pathlib import Path
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class DatabaseMerger:
    """Merge data from two SQL databases"""

    def __init__(self):
        self.source_db = "F:/OSINT_WAREHOUSE/osint_research.db"
        self.target_db = "F:/OSINT_WAREHOUSE/osint_master.db"

        # Connect to both databases
        self.source_conn = sqlite3.connect(self.source_db)
        self.target_conn = sqlite3.connect(self.target_db)

        self.source_cursor = self.source_conn.cursor()
        self.target_cursor = self.target_conn.cursor()

        # Enable foreign keys
        self.target_cursor.execute("PRAGMA foreign_keys = ON")

        self.stats = {
            "mcf_imported": 0,
            "procurement_imported": 0,
            "patents_imported": 0,
            "publications_imported": 0,
            "collaborations_imported": 0,
            "errors": []
        }

    def merge_mcf_documents(self):
        """Merge missing MCF documents"""
        logging.info("Merging MCF documents...")

        # Get existing URLs from target to avoid duplicates
        self.target_cursor.execute("SELECT url FROM mcf_documents WHERE url IS NOT NULL")
        existing_urls = set(row[0] for row in self.target_cursor.fetchall())

        # Get documents from source
        self.source_cursor.execute("""
            SELECT url, title, content, relevance_score, collector,
                   collection_timestamp, metadata
            FROM mcf_documents
        """)

        for row in self.source_cursor.fetchall():
            url, title, content, relevance, collector, timestamp, metadata = row

            # Skip if URL already exists or is None
            if not url or url in existing_urls:
                continue

            try:
                # Generate doc_id from URL or title
                import hashlib
                doc_id = hashlib.md5((url or title or "").encode()).hexdigest()[:16]

                self.target_cursor.execute("""
                INSERT OR IGNORE INTO mcf_documents (
                    doc_id, title, url, source, collection_date,
                    content, relevance_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    doc_id,
                    title or "Untitled",
                    url,
                    collector or "F_drive_import",
                    timestamp or datetime.now().isoformat(),
                    content,
                    relevance or 0.5
                ))

                if self.target_cursor.rowcount > 0:
                    self.stats["mcf_imported"] += 1
                    logging.info(f"  Imported: {title[:60]}...")

            except Exception as e:
                error = f"MCF import error: {e}"
                logging.error(error)
                self.stats["errors"].append(error)

        self.target_conn.commit()
        logging.info(f"Imported {self.stats['mcf_imported']} new MCF documents")

    def create_intelligence_tables(self):
        """Create tables for additional intelligence data"""
        logging.info("Creating intelligence tables...")

        # Procurement data table
        self.target_cursor.execute("""
        CREATE TABLE IF NOT EXISTS intelligence_procurement (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contract_id TEXT,
            buyer TEXT,
            supplier TEXT,
            description TEXT,
            value REAL,
            date TEXT,
            country TEXT,
            china_related BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Patent data table
        self.target_cursor.execute("""
        CREATE TABLE IF NOT EXISTS intelligence_patents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patent_number TEXT UNIQUE,
            title TEXT,
            assignee TEXT,
            inventor TEXT,
            filing_date DATE,
            technology_area TEXT,
            china_related BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Publication data table
        self.target_cursor.execute("""
        CREATE TABLE IF NOT EXISTS intelligence_publications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            publication_id TEXT,
            title TEXT,
            authors TEXT,
            institution TEXT,
            year INTEGER,
            journal TEXT,
            china_collaboration BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Collaboration data table
        self.target_cursor.execute("""
        CREATE TABLE IF NOT EXISTS intelligence_collaborations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity1 TEXT,
            entity2 TEXT,
            collaboration_type TEXT,
            date TEXT,
            description TEXT,
            risk_level TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        self.target_conn.commit()
        logging.info("Intelligence tables created")

    def import_procurement_data(self):
        """Import procurement data from source"""
        logging.info("Importing procurement data...")

        try:
            self.source_cursor.execute("SELECT * FROM core_f_procurement LIMIT 1000")
            columns = [desc[0] for desc in self.source_cursor.description]

            self.source_cursor.execute("SELECT * FROM core_f_procurement")
            for row in self.source_cursor.fetchall():
                data = dict(zip(columns, row))

                # Check for China-related keywords
                text = str(data.get('buyer', '')) + str(data.get('supplier', '')) + str(data.get('description', ''))
                china_related = any(kw in text.lower() for kw in ['china', 'chinese', 'beijing', 'shanghai'])

                self.target_cursor.execute("""
                INSERT OR IGNORE INTO intelligence_procurement (
                    buyer, supplier, description, value, date, china_related
                ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    data.get('buyer'),
                    data.get('supplier'),
                    data.get('description'),
                    data.get('value'),
                    data.get('date'),
                    china_related
                ))

                if self.target_cursor.rowcount > 0:
                    self.stats["procurement_imported"] += 1

        except Exception as e:
            logging.warning(f"Could not import procurement data: {e}")

        self.target_conn.commit()
        logging.info(f"Imported {self.stats['procurement_imported']} procurement records")

    def import_patent_data(self):
        """Import patent data from source"""
        logging.info("Importing patent data...")

        try:
            self.source_cursor.execute("SELECT * FROM core_f_patent")
            columns = [desc[0] for desc in self.source_cursor.description]

            for row in self.source_cursor.fetchall():
                data = dict(zip(columns, row))

                # Check for China-related
                text = str(data.get('assignee', '')) + str(data.get('inventor', ''))
                china_related = any(kw in text.lower() for kw in ['china', 'chinese', 'beijing', 'shanghai'])

                self.target_cursor.execute("""
                INSERT OR IGNORE INTO intelligence_patents (
                    patent_number, title, assignee, inventor, filing_date, china_related
                ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    data.get('patent_number'),
                    data.get('title'),
                    data.get('assignee'),
                    data.get('inventor'),
                    data.get('filing_date'),
                    china_related
                ))

                if self.target_cursor.rowcount > 0:
                    self.stats["patents_imported"] += 1

        except Exception as e:
            logging.warning(f"Could not import patent data: {e}")

        self.target_conn.commit()
        logging.info(f"Imported {self.stats['patents_imported']} patent records")

    def import_publication_data(self):
        """Import publication data from source"""
        logging.info("Importing publication data...")

        try:
            self.source_cursor.execute("SELECT * FROM core_f_publication")
            columns = [desc[0] for desc in self.source_cursor.description]

            for row in self.source_cursor.fetchall():
                data = dict(zip(columns, row))

                # Check for China collaboration
                text = str(data.get('authors', '')) + str(data.get('institution', ''))
                china_collab = any(kw in text.lower() for kw in ['china', 'chinese', 'beijing', 'tsinghua', 'peking'])

                self.target_cursor.execute("""
                INSERT OR IGNORE INTO intelligence_publications (
                    title, authors, institution, year, journal, china_collaboration
                ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    data.get('title'),
                    data.get('authors'),
                    data.get('institution'),
                    data.get('year'),
                    data.get('journal'),
                    china_collab
                ))

                if self.target_cursor.rowcount > 0:
                    self.stats["publications_imported"] += 1

        except Exception as e:
            logging.warning(f"Could not import publication data: {e}")

        self.target_conn.commit()
        logging.info(f"Imported {self.stats['publications_imported']} publication records")

    def import_collaboration_data(self):
        """Import collaboration data from source"""
        logging.info("Importing collaboration data...")

        try:
            self.source_cursor.execute("SELECT * FROM core_f_collaboration")
            columns = [desc[0] for desc in self.source_cursor.description]

            for row in self.source_cursor.fetchall():
                data = dict(zip(columns, row))

                self.target_cursor.execute("""
                INSERT OR IGNORE INTO intelligence_collaborations (
                    entity1, entity2, collaboration_type, date, description
                ) VALUES (?, ?, ?, ?, ?)
                """, (
                    data.get('entity1'),
                    data.get('entity2'),
                    data.get('collaboration_type'),
                    data.get('date'),
                    data.get('description')
                ))

                if self.target_cursor.rowcount > 0:
                    self.stats["collaborations_imported"] += 1

        except Exception as e:
            logging.warning(f"Could not import collaboration data: {e}")

        self.target_conn.commit()
        logging.info(f"Imported {self.stats['collaborations_imported']} collaboration records")

    def generate_report(self):
        """Generate merge report"""
        report = f"""
DATABASE MERGE REPORT
====================
Time: {datetime.now().isoformat()}

Data Imported:
- MCF Documents: {self.stats['mcf_imported']}
- Procurement Records: {self.stats['procurement_imported']}
- Patent Records: {self.stats['patents_imported']}
- Publication Records: {self.stats['publications_imported']}
- Collaboration Records: {self.stats['collaborations_imported']}

Total New Records: {sum([
    self.stats['mcf_imported'],
    self.stats['procurement_imported'],
    self.stats['patents_imported'],
    self.stats['publications_imported'],
    self.stats['collaborations_imported']
])}

Errors: {len(self.stats['errors'])}
"""
        if self.stats['errors']:
            report += "\nError Details:\n"
            for error in self.stats['errors'][:10]:
                report += f"  - {error}\n"

        return report

    def run(self):
        """Execute the merge process"""
        try:
            logging.info("=" * 60)
            logging.info("DATABASE MERGE PROCESS")
            logging.info("=" * 60)
            logging.info(f"Source: {self.source_db}")
            logging.info(f"Target: {self.target_db}")
            logging.info("")

            # Merge MCF documents
            self.merge_mcf_documents()

            # Create intelligence tables
            self.create_intelligence_tables()

            # Import other data types
            self.import_procurement_data()
            self.import_patent_data()
            self.import_publication_data()
            self.import_collaboration_data()

            # Generate report
            report = self.generate_report()
            print(report)

            # Save report
            with open("database_merge_report.txt", "w") as f:
                f.write(report)

            logging.info("\nMerge complete! Report saved to database_merge_report.txt")

        except Exception as e:
            logging.error(f"Fatal error during merge: {e}")
            raise
        finally:
            self.source_conn.close()
            self.target_conn.close()

def main():
    merger = DatabaseMerger()
    merger.run()

if __name__ == "__main__":
    main()

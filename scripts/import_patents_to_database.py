#!/usr/bin/env python3
"""
Import EPO Patent Data to Database
Reads all collected patent JSON files and imports them into the OSINT database
"""

import json
import sqlite3
import os
from datetime import datetime
from pathlib import Path

class PatentDatabaseImporter:
    def __init__(self):
        self.db_path = "F:/OSINT_DATA/osint_master.db"
        self.paginated_dir = "F:/OSINT_DATA/epo_paginated"
        self.expanded_dir = "F:/OSINT_DATA/epo_expanded"

    def create_tables(self, conn):
        """Create patent tables if they don't exist"""
        cursor = conn.cursor()

        # Main patents table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                publication_number TEXT UNIQUE,
                title TEXT,
                abstract TEXT,
                country TEXT,
                publication_date TEXT,
                query_source TEXT,
                company_name TEXT,
                technology_area TEXT,
                collection_date TEXT,
                data_source TEXT DEFAULT 'EPO'
            )
        """)

        # Applicants table (many-to-many relationship)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patent_applicants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patent_id INTEGER,
                applicant_name TEXT,
                applicant_country TEXT,
                FOREIGN KEY (patent_id) REFERENCES patents(id)
            )
        """)

        # Inventors table (many-to-many relationship)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patent_inventors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patent_id INTEGER,
                inventor_name TEXT,
                inventor_country TEXT,
                FOREIGN KEY (patent_id) REFERENCES patents(id)
            )
        """)

        # Collection statistics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patent_collection_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_name TEXT,
                company_name TEXT,
                total_available INTEGER,
                total_collected INTEGER,
                collection_date TEXT,
                file_path TEXT,
                status TEXT
            )
        """)

        conn.commit()

        # Create indexes for better query performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_patents_company ON patents(company_name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_patents_tech ON patents(technology_area)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_patents_country ON patents(country)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_applicants_name ON patent_applicants(applicant_name)")

        conn.commit()
        print("Database tables created/verified")

    def extract_company_tech(self, filename, description=""):
        """Extract company name and technology area from filename and description"""
        company_map = {
            'huawei': 'Huawei Technologies',
            'alibaba': 'Alibaba Group',
            'tencent': 'Tencent',
            'baidu': 'Baidu',
            'xiaomi': 'Xiaomi',
            'bytedance': 'ByteDance',
            'zte': 'ZTE',
            'lenovo': 'Lenovo',
            'dji': 'DJI',
            'oppo': 'OPPO',
            'vivo': 'VIVO',
            'byd': 'BYD'
        }

        tech_map = {
            'semiconductors': 'Semiconductors',
            'quantum_computing': 'Quantum Computing',
            'ai_china': 'Artificial Intelligence',
            'ml_china': 'Machine Learning',
            '5g_china': '5G Technology',
            '6g_china': '6G Technology',
            'blockchain_china': 'Blockchain',
            'autonomous_china': 'Autonomous Systems',
            'drone_china': 'Drone Technology',
            'radar_china': 'Radar Technology',
            'satellite_china': 'Satellite Technology'
        }

        # Extract from filename
        filename_lower = filename.lower()
        company = None
        technology = None

        for key, value in company_map.items():
            if key in filename_lower:
                company = value
                break

        for key, value in tech_map.items():
            if key in filename_lower:
                technology = value
                break

        # If no company found but has technology, it's a technology-focused query
        if not company and technology:
            company = 'Multiple Chinese Companies'

        # Use description as fallback
        if not company and not technology and description:
            if 'China Semiconductor' in description:
                technology = 'Semiconductors'
                company = 'Multiple Chinese Companies'

        return company, technology

    def import_json_file(self, conn, filepath):
        """Import a single JSON file into the database"""
        print(f"\nProcessing: {filepath}")

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            cursor = conn.cursor()

            # Extract metadata
            filename = os.path.basename(filepath)
            query = data.get('query', '')
            description = data.get('description', '')
            collection_time = data.get('collection_time', datetime.now().isoformat())

            # Extract company and technology info
            company, technology = self.extract_company_tech(filename, description)

            # Handle different JSON structures
            patents = []

            # Structure 1: Patents in 'patents' field
            if 'patents' in data:
                patents = data['patents']

            # Structure 2: Patents in 'patent_batches' field
            elif 'patent_batches' in data:
                for batch in data['patent_batches']:
                    if 'raw_data' in batch:
                        # Parse the raw_data structure
                        # This is simplified - actual structure may vary
                        patents.append(batch['raw_data'])

            # Structure 3: Direct results
            elif 'results' in data:
                patents = data['results']

            # Track statistics
            total_collected = len(patents)
            if 'batch_info' in data:
                total_available = data['batch_info'].get('total_available', total_collected)
            elif 'total_available' in data:
                total_available = data['total_available']
            else:
                total_available = total_collected

            # Insert collection statistics
            cursor.execute("""
                INSERT OR REPLACE INTO patent_collection_stats
                (query_name, company_name, total_available, total_collected,
                 collection_date, file_path, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (query, company or 'Unknown', total_available, total_collected,
                  collection_time, filepath, 'imported'))

            # Insert patents
            imported = 0
            skipped = 0

            for patent in patents:
                if isinstance(patent, dict):
                    pub_number = patent.get('publication_number')

                    if not pub_number:
                        skipped += 1
                        continue

                    try:
                        cursor.execute("""
                            INSERT OR IGNORE INTO patents
                            (publication_number, title, abstract, country,
                             publication_date, query_source, company_name,
                             technology_area, collection_date)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            pub_number,
                            patent.get('title', ''),
                            patent.get('abstract', ''),
                            patent.get('country', ''),
                            patent.get('publication_date', ''),
                            query,
                            company,
                            technology,
                            collection_time
                        ))

                        if cursor.rowcount > 0:
                            imported += 1
                            patent_id = cursor.lastrowid

                            # Insert applicants
                            applicants = patent.get('applicants', [])
                            if isinstance(applicants, list):
                                for applicant in applicants:
                                    if isinstance(applicant, str):
                                        cursor.execute("""
                                            INSERT INTO patent_applicants
                                            (patent_id, applicant_name)
                                            VALUES (?, ?)
                                        """, (patent_id, applicant))

                            # Insert inventors
                            inventors = patent.get('inventors', [])
                            if isinstance(inventors, list):
                                for inventor in inventors:
                                    if isinstance(inventor, str):
                                        cursor.execute("""
                                            INSERT INTO patent_inventors
                                            (patent_id, inventor_name)
                                            VALUES (?, ?)
                                        """, (patent_id, inventor))
                        else:
                            skipped += 1

                    except sqlite3.Error as e:
                        print(f"  Error inserting patent {pub_number}: {e}")
                        skipped += 1

            conn.commit()
            print(f"  Imported: {imported} patents, Skipped: {skipped} (duplicates/errors)")
            return imported, skipped

        except Exception as e:
            print(f"  Error processing file: {e}")
            return 0, 0

    def import_all_patents(self):
        """Import all patent files from both directories"""
        print("="*60)
        print("EPO PATENT DATABASE IMPORT")
        print("="*60)

        conn = sqlite3.connect(self.db_path)
        self.create_tables(conn)

        total_imported = 0
        total_skipped = 0

        # Import paginated collection files
        print("\nImporting paginated collection files...")
        if os.path.exists(self.paginated_dir):
            for file in os.listdir(self.paginated_dir):
                if file.endswith('.json'):
                    filepath = os.path.join(self.paginated_dir, file)
                    imported, skipped = self.import_json_file(conn, filepath)
                    total_imported += imported
                    total_skipped += skipped

        # Import expanded collection files
        print("\nImporting expanded collection files...")
        if os.path.exists(self.expanded_dir):
            for file in os.listdir(self.expanded_dir):
                if file.endswith('.json') and 'summary' not in file:
                    filepath = os.path.join(self.expanded_dir, file)
                    imported, skipped = self.import_json_file(conn, filepath)
                    total_imported += imported
                    total_skipped += skipped

        # Show summary statistics
        cursor = conn.cursor()

        print("\n" + "="*60)
        print("IMPORT COMPLETE")
        print("="*60)
        print(f"Total patents imported: {total_imported:,}")
        print(f"Total skipped (duplicates): {total_skipped:,}")

        # Query statistics
        cursor.execute("SELECT COUNT(*) FROM patents")
        total_in_db = cursor.fetchone()[0]
        print(f"Total patents in database: {total_in_db:,}")

        # Company breakdown
        print("\nPatents by Company:")
        cursor.execute("""
            SELECT company_name, COUNT(*) as count
            FROM patents
            WHERE company_name IS NOT NULL
            GROUP BY company_name
            ORDER BY count DESC
            LIMIT 10
        """)
        for company, count in cursor.fetchall():
            print(f"  {company}: {count:,}")

        # Technology breakdown
        print("\nPatents by Technology Area:")
        cursor.execute("""
            SELECT technology_area, COUNT(*) as count
            FROM patents
            WHERE technology_area IS NOT NULL
            GROUP BY technology_area
            ORDER BY count DESC
            LIMIT 10
        """)
        for tech, count in cursor.fetchall():
            print(f"  {tech}: {count:,}")

        conn.close()
        print("\nDatabase saved to:", self.db_path)

def main():
    importer = PatentDatabaseImporter()
    importer.import_all_patents()

if __name__ == "__main__":
    main()

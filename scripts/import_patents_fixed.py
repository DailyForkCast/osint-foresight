#!/usr/bin/env python3
"""
Fixed Patent Database Importer - Handles actual EPO JSON structure
"""

import json
import sqlite3
import os
from datetime import datetime

class PatentDatabaseImporter:
    def __init__(self):
        self.db_path = "F:/OSINT_DATA/osint_master.db"
        self.paginated_dir = "F:/OSINT_DATA/epo_paginated"
        self.expanded_dir = "F:/OSINT_DATA/epo_expanded"
        self.patents_imported = 0
        self.patents_skipped = 0

    def create_tables(self, conn):
        """Create patent tables if they don't exist"""
        cursor = conn.cursor()

        # Drop old tables if they exist
        cursor.execute("DROP TABLE IF EXISTS patent_inventors")
        cursor.execute("DROP TABLE IF EXISTS patent_applicants")
        cursor.execute("DROP TABLE IF EXISTS patent_collection_stats")
        cursor.execute("DROP TABLE IF EXISTS patents")

        # Main patents table
        cursor.execute("""
            CREATE TABLE patents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                publication_number TEXT UNIQUE,
                doc_number TEXT,
                country TEXT,
                kind TEXT,
                publication_date TEXT,
                title TEXT,
                abstract TEXT,
                query_source TEXT,
                company_name TEXT,
                technology_area TEXT,
                collection_date TEXT,
                data_source TEXT DEFAULT 'EPO'
            )
        """)

        # Collection statistics table
        cursor.execute("""
            CREATE TABLE patent_collection_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_name TEXT,
                company_name TEXT,
                total_available INTEGER,
                total_collected INTEGER,
                collection_date TEXT,
                file_path TEXT
            )
        """)

        # Create indexes
        cursor.execute("CREATE INDEX idx_patents_company ON patents(company_name)")
        cursor.execute("CREATE INDEX idx_patents_tech ON patents(technology_area)")
        cursor.execute("CREATE INDEX idx_patents_country ON patents(country)")
        cursor.execute("CREATE INDEX idx_patents_date ON patents(publication_date)")

        conn.commit()
        print("Database tables created")

    def extract_company_tech(self, filename, description=""):
        """Extract company name and technology from filename/description"""
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

        if not company and technology:
            company = 'Chinese Companies'

        if 'China Semiconductor' in description:
            technology = 'Semiconductors'
            company = 'Chinese Companies'

        return company, technology

    def extract_patent_from_exchange_doc(self, doc):
        """Extract patent information from exchange-document structure"""
        try:
            patent = {}

            # Basic document info
            patent['country'] = doc.get('@country', '')
            patent['doc_number'] = doc.get('@doc-number', '')
            patent['kind'] = doc.get('@kind', '')

            # Extract from bibliographic data
            biblio = doc.get('bibliographic-data', {})
            pub_ref = biblio.get('publication-reference', {})
            doc_ids = pub_ref.get('document-id', [])

            if not isinstance(doc_ids, list):
                doc_ids = [doc_ids]

            # Get the epodoc format publication number
            for doc_id in doc_ids:
                if doc_id.get('@document-id-type') == 'epodoc':
                    doc_num = doc_id.get('doc-number', {})
                    if isinstance(doc_num, dict) and '$' in doc_num:
                        patent['publication_number'] = doc_num['$']
                    elif isinstance(doc_num, str):
                        patent['publication_number'] = doc_num

                    date_val = doc_id.get('date', {})
                    if isinstance(date_val, dict) and '$' in date_val:
                        patent['publication_date'] = date_val['$']
                    elif isinstance(date_val, str):
                        patent['publication_date'] = date_val
                    break

            # Fallback to docdb format if no epodoc
            if not patent.get('publication_number'):
                for doc_id in doc_ids:
                    if doc_id.get('@document-id-type') == 'docdb':
                        country = doc_id.get('country', {})
                        if isinstance(country, dict) and '$' in country:
                            country = country['$']

                        number = doc_id.get('doc-number', {})
                        if isinstance(number, dict) and '$' in number:
                            number = number['$']

                        if country and number:
                            patent['publication_number'] = f"{country}{number}"

                        date_val = doc_id.get('date', {})
                        if isinstance(date_val, dict) and '$' in date_val:
                            patent['publication_date'] = date_val['$']
                        elif isinstance(date_val, str):
                            patent['publication_date'] = date_val
                        break

            # Get abstract
            abstract_data = doc.get('abstract', {})
            if isinstance(abstract_data, dict):
                abstract_p = abstract_data.get('p', {})
                if isinstance(abstract_p, dict):
                    patent['abstract'] = abstract_p.get('$', '')
                else:
                    patent['abstract'] = str(abstract_p)

            # Title (if available - often not in search results)
            patent['title'] = ''

            return patent

        except Exception as e:
            print(f"Error extracting patent: {e}")
            return None

    def import_json_file(self, conn, filepath):
        """Import a single JSON file"""
        filename = os.path.basename(filepath)
        print(f"\nProcessing: {filename}")

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            cursor = conn.cursor()

            # Extract metadata
            query = data.get('query', '')
            description = data.get('description', '')
            collection_time = data.get('timestamp', data.get('collection_time', ''))
            total_available = data.get('total_available', 0)
            total_collected = data.get('total_collected', 0)

            # Extract company and technology
            company, technology = self.extract_company_tech(filename, description)

            # Save collection stats
            cursor.execute("""
                INSERT INTO patent_collection_stats
                (query_name, company_name, total_available, total_collected,
                 collection_date, file_path)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (query, company or 'Unknown', total_available, total_collected,
                  collection_time, filepath))

            # Process patents
            file_imported = 0
            file_skipped = 0

            # Handle patent batches structure
            if 'patent_batches' in data:
                for batch in data['patent_batches']:
                    raw_data = batch.get('raw_data', {})
                    exchange_docs = raw_data.get('exchange-documents', [])

                    if not isinstance(exchange_docs, list):
                        exchange_docs = [exchange_docs]

                    for doc_wrapper in exchange_docs:
                        if 'exchange-document' in doc_wrapper:
                            patent = self.extract_patent_from_exchange_doc(
                                doc_wrapper['exchange-document']
                            )

                            if patent and patent.get('publication_number'):
                                try:
                                    # Make sure all values are strings, not dicts
                                    pub_num = patent['publication_number']
                                    if isinstance(pub_num, dict):
                                        pub_num = str(pub_num)

                                    cursor.execute("""
                                        INSERT OR IGNORE INTO patents
                                        (publication_number, doc_number, country, kind,
                                         publication_date, title, abstract,
                                         query_source, company_name, technology_area,
                                         collection_date)
                                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                    """, (
                                        str(pub_num) if pub_num else '',
                                        str(patent.get('doc_number', '')),
                                        str(patent.get('country', '')),
                                        str(patent.get('kind', '')),
                                        str(patent.get('publication_date', '')),
                                        str(patent.get('title', '')),
                                        str(patent.get('abstract', ''))[:1000],  # Truncate abstract
                                        str(query),
                                        str(company) if company else '',
                                        str(technology) if technology else '',
                                        str(collection_time)
                                    ))

                                    if cursor.rowcount > 0:
                                        file_imported += 1
                                    else:
                                        file_skipped += 1

                                except Exception as e:
                                    print(f"  Error with patent {pub_num}: {e}")
                                    file_skipped += 1

            # Handle patents array structure (simplified format)
            elif 'patents' in data:
                for patent in data['patents']:
                    if isinstance(patent, dict) and patent.get('publication_number'):
                        try:
                            cursor.execute("""
                                INSERT OR IGNORE INTO patents
                                (publication_number, title, abstract, country,
                                 publication_date, query_source, company_name,
                                 technology_area, collection_date)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                patent['publication_number'],
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
                                file_imported += 1
                            else:
                                file_skipped += 1

                        except sqlite3.Error as e:
                            print(f"  DB error: {e}")
                            file_skipped += 1

            conn.commit()
            self.patents_imported += file_imported
            self.patents_skipped += file_skipped

            print(f"  Imported: {file_imported}, Skipped: {file_skipped}")
            return file_imported, file_skipped

        except Exception as e:
            print(f"  File error: {e}")
            return 0, 0

    def import_all_patents(self):
        """Import all patent files"""
        print("="*60)
        print("EPO PATENT DATABASE IMPORT")
        print("="*60)

        conn = sqlite3.connect(self.db_path)
        self.create_tables(conn)

        # Import paginated files
        print("\nImporting paginated collection...")
        if os.path.exists(self.paginated_dir):
            for file in sorted(os.listdir(self.paginated_dir)):
                if file.endswith('.json'):
                    filepath = os.path.join(self.paginated_dir, file)
                    self.import_json_file(conn, filepath)

        # Import expanded files
        print("\nImporting expanded collection...")
        if os.path.exists(self.expanded_dir):
            for file in sorted(os.listdir(self.expanded_dir)):
                if file.endswith('.json') and 'summary' not in file:
                    filepath = os.path.join(self.expanded_dir, file)
                    self.import_json_file(conn, filepath)

        # Show statistics
        cursor = conn.cursor()

        print("\n" + "="*60)
        print("IMPORT SUMMARY")
        print("="*60)
        print(f"Total patents imported: {self.patents_imported:,}")
        print(f"Total duplicates skipped: {self.patents_skipped:,}")

        cursor.execute("SELECT COUNT(*) FROM patents")
        total_in_db = cursor.fetchone()[0]
        print(f"Total unique patents in database: {total_in_db:,}")

        print("\nPatents by Company:")
        cursor.execute("""
            SELECT company_name, COUNT(*) as count
            FROM patents
            WHERE company_name IS NOT NULL
            GROUP BY company_name
            ORDER BY count DESC
        """)
        for company, count in cursor.fetchall():
            print(f"  {company}: {count:,}")

        print("\nPatents by Technology:")
        cursor.execute("""
            SELECT technology_area, COUNT(*) as count
            FROM patents
            WHERE technology_area IS NOT NULL
            GROUP BY technology_area
            ORDER BY count DESC
        """)
        for tech, count in cursor.fetchall():
            print(f"  {tech}: {count:,}")

        print("\nRecent Patents (last 5):")
        cursor.execute("""
            SELECT publication_number, company_name, publication_date
            FROM patents
            WHERE publication_date != ''
            ORDER BY publication_date DESC
            LIMIT 5
        """)
        for pub_num, company, date in cursor.fetchall():
            print(f"  {pub_num} - {company} ({date})")

        conn.close()
        print(f"\nDatabase saved to: {self.db_path}")

def main():
    importer = PatentDatabaseImporter()
    importer.import_all_patents()

if __name__ == "__main__":
    main()

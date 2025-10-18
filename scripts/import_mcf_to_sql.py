#!/usr/bin/env python3
"""
MCF (Military-Civil Fusion) Think Tank Data to SQL Importer
Imports intelligence documents from US think tanks on China's MCF strategy
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
        logging.FileHandler('mcf_sql_import.log'),
        logging.StreamHandler()
    ]
)

class MCFSQLImporter:
    """Import MCF think tank data to SQL database"""

    def __init__(self,
                 mcf_file: str = "data/processed/mcf_orchestrated/mcf_comprehensive_collection_20250922_223007.json",
                 db_path: str = "F:/OSINT_WAREHOUSE/osint_master.db"):

        self.mcf_file = Path(mcf_file)
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Database connection
        self.conn = sqlite3.connect(str(self.db_path))
        self.cursor = self.conn.cursor()

        # Enable foreign keys
        self.cursor.execute("PRAGMA foreign_keys = ON")

        logging.info(f"MCF data source: {self.mcf_file}")
        logging.info(f"Target database: {self.db_path}")

        # Statistics
        self.stats = {
            "documents_imported": 0,
            "entities_imported": 0,
            "relationships_imported": 0,
            "errors": []
        }

    def create_tables(self):
        """Create MCF tables in database"""
        logging.info("Creating MCF tables...")

        # Main documents table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS mcf_documents (
            doc_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            url TEXT,
            source TEXT NOT NULL,
            collection_date TIMESTAMP,
            published_date TEXT,
            content TEXT,
            summary TEXT,
            doc_type TEXT,
            relevance_score REAL,
            china_relevance TEXT,
            technology_areas TEXT,
            risk_level TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Entities table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS mcf_entities (
            entity_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            entity_type TEXT NOT NULL,
            chinese_name TEXT,
            description TEXT,
            risk_category TEXT,
            first_seen DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(name, entity_type)
        )
        """)

        # Document-Entity relationships
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS mcf_document_entities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doc_id TEXT NOT NULL,
            entity_id INTEGER NOT NULL,
            mention_count INTEGER DEFAULT 1,
            context TEXT,
            sentiment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (doc_id) REFERENCES mcf_documents(doc_id) ON DELETE CASCADE,
            FOREIGN KEY (entity_id) REFERENCES mcf_entities(entity_id) ON DELETE CASCADE,
            UNIQUE(doc_id, entity_id)
        )
        """)

        # Think tank sources table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS mcf_sources (
            source_id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_name TEXT UNIQUE NOT NULL,
            source_type TEXT,
            url TEXT,
            credibility_rating TEXT,
            focus_areas TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Technology areas table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS mcf_technologies (
            tech_id INTEGER PRIMARY KEY AUTOINCREMENT,
            technology TEXT UNIQUE NOT NULL,
            category TEXT,
            dual_use BOOLEAN DEFAULT 0,
            critical_level TEXT,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Document technology mapping
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS mcf_document_technologies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doc_id TEXT NOT NULL,
            tech_id INTEGER NOT NULL,
            relevance TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (doc_id) REFERENCES mcf_documents(doc_id) ON DELETE CASCADE,
            FOREIGN KEY (tech_id) REFERENCES mcf_technologies(tech_id) ON DELETE CASCADE,
            UNIQUE(doc_id, tech_id)
        )
        """)

        # Create indexes
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_docs_source ON mcf_documents(source)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_docs_relevance ON mcf_documents(relevance_score)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_entities_type ON mcf_entities(entity_type)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_entities_risk ON mcf_entities(risk_category)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_doc_entities_doc ON mcf_document_entities(doc_id)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_doc_entities_entity ON mcf_document_entities(entity_id)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_tech_dual ON mcf_technologies(dual_use)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_tech_critical ON mcf_technologies(critical_level)")

        # Create view for high-risk entities
        self.cursor.execute("""
        CREATE VIEW IF NOT EXISTS v_mcf_high_risk_entities AS
        SELECT
            e.name,
            e.entity_type,
            e.risk_category,
            COUNT(DISTINCT de.doc_id) as document_mentions,
            GROUP_CONCAT(DISTINCT d.source) as sources,
            MAX(d.relevance_score) as max_relevance
        FROM mcf_entities e
        JOIN mcf_document_entities de ON e.entity_id = de.entity_id
        JOIN mcf_documents d ON de.doc_id = d.doc_id
        WHERE e.risk_category IN ('HIGH', 'CRITICAL')
           OR e.entity_type IN ('Military', 'Defense', 'Dual-Use')
        GROUP BY e.entity_id
        ORDER BY document_mentions DESC
        """)

        # Create view for technology mapping
        self.cursor.execute("""
        CREATE VIEW IF NOT EXISTS v_mcf_china_technologies AS
        SELECT
            t.technology,
            t.category,
            t.dual_use,
            t.critical_level,
            COUNT(DISTINCT dt.doc_id) as document_count,
            AVG(d.relevance_score) as avg_relevance
        FROM mcf_technologies t
        JOIN mcf_document_technologies dt ON t.tech_id = dt.tech_id
        JOIN mcf_documents d ON dt.doc_id = d.doc_id
        GROUP BY t.tech_id
        ORDER BY document_count DESC, avg_relevance DESC
        """)

        self.conn.commit()
        logging.info("Tables created successfully")

    def import_mcf_data(self):
        """Import MCF data from JSON file"""
        if not self.mcf_file.exists():
            logging.error(f"MCF file not found: {self.mcf_file}")
            return

        logging.info(f"Loading MCF data from {self.mcf_file}...")

        with open(self.mcf_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Navigate to the actual documents within the nested structure
        documents = []
        phase_results = data.get('phase_results', {})

        # Process each phase
        for phase_name, phase_data in phase_results.items():
            collector_results = phase_data.get('collector_results', {})

            # Process each collector's results
            for collector_name, collector_data in collector_results.items():
                collector_docs = collector_data.get('documents', [])
                documents.extend(collector_docs)
        for doc in documents:
            try:
                # Generate doc_id if not present
                doc_id = doc.get('id', f"{doc.get('source_id', 'unknown')}_{doc.get('url', '').replace('/', '_')[:50]}")

                self.cursor.execute("""
                INSERT OR REPLACE INTO mcf_documents (
                    doc_id, title, url, source, collection_date,
                    published_date, content, summary, doc_type,
                    relevance_score, china_relevance, technology_areas
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    doc_id,
                    doc.get('title', 'Untitled'),
                    doc.get('url'),
                    doc.get('source_id', 'Unknown'),
                    doc.get('provenance', {}).get('collected_date'),
                    doc.get('publication_date'),
                    doc.get('content_text', doc.get('text', '')),
                    doc.get('summary'),
                    doc.get('document_type', doc.get('type')),
                    doc.get('mcf_relevance_score', doc.get('relevance', 0)),
                    doc.get('china_relevance'),
                    json.dumps(doc.get('technologies', []))
                ))

                self.stats["documents_imported"] += 1

                # Import entities from document
                entities = doc.get('entities', {})
                for entity_type, entity_list in entities.items():
                    if isinstance(entity_list, list):
                        for entity_name in entity_list:
                            # Insert entity
                            self.cursor.execute("""
                            INSERT OR IGNORE INTO mcf_entities (name, entity_type)
                            VALUES (?, ?)
                            """, (entity_name, entity_type))

                            # Get entity_id
                            self.cursor.execute(
                                "SELECT entity_id FROM mcf_entities WHERE name = ? AND entity_type = ?",
                                (entity_name, entity_type)
                            )
                            entity_id = self.cursor.fetchone()[0]

                            # Link document to entity
                            self.cursor.execute("""
                            INSERT OR REPLACE INTO mcf_document_entities (doc_id, entity_id)
                            VALUES (?, ?)
                            """, (doc_id, entity_id))

                            self.stats["relationships_imported"] += 1

            except Exception as e:
                logging.error(f"Error importing document: {e}")
                self.stats["errors"].append(str(e))

        # Import global entities if present
        global_entities = data.get('entities_by_type', {})
        for entity_type, entities in global_entities.items():
            for entity in entities:
                try:
                    if isinstance(entity, dict):
                        name = entity.get('name')
                        count = entity.get('count', 0)
                    else:
                        name = entity
                        count = 1

                    if name:
                        self.cursor.execute("""
                        INSERT OR IGNORE INTO mcf_entities (name, entity_type)
                        VALUES (?, ?)
                        """, (name, entity_type))
                        self.stats["entities_imported"] += 1

                except Exception as e:
                    logging.error(f"Error importing entity {entity}: {e}")

        # Import sources
        sources = set()
        for doc in documents:
            source = doc.get('source')
            if source:
                sources.add(source)

        for source in sources:
            self.cursor.execute("""
            INSERT OR IGNORE INTO mcf_sources (source_name, source_type)
            VALUES (?, ?)
            """, (source, 'Think Tank'))

        # Import technologies
        tech_keywords = [
            'AI', 'artificial intelligence', 'quantum', 'semiconductor', '5G', '6G',
            'hypersonic', 'space', 'cyber', 'biotech', 'nuclear', 'surveillance',
            'robotics', 'autonomous', 'blockchain', 'nanotechnology'
        ]

        for tech in tech_keywords:
            dual_use = tech in ['AI', 'quantum', 'semiconductor', 'biotech', 'nuclear', 'space']
            critical = 'CRITICAL' if tech in ['quantum', 'semiconductor', 'hypersonic', 'nuclear'] else 'HIGH'

            self.cursor.execute("""
            INSERT OR IGNORE INTO mcf_technologies (
                technology, category, dual_use, critical_level
            ) VALUES (?, ?, ?, ?)
            """, (tech, 'Advanced Technology', dual_use, critical))

        self.conn.commit()
        logging.info(f"Imported {self.stats['documents_imported']} documents")
        logging.info(f"Imported {self.stats['entities_imported']} entities")
        logging.info(f"Created {self.stats['relationships_imported']} relationships")

    def generate_statistics(self):
        """Generate and display import statistics"""
        logging.info("\n" + "="*60)
        logging.info("MCF SQL IMPORT STATISTICS")
        logging.info("="*60)

        # Get counts
        self.cursor.execute("SELECT COUNT(*) FROM mcf_documents")
        total_docs = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COUNT(*) FROM mcf_entities")
        total_entities = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COUNT(*) FROM mcf_document_entities")
        total_relationships = self.cursor.fetchone()[0]

        # Entity type distribution
        self.cursor.execute("""
        SELECT entity_type, COUNT(*) as count
        FROM mcf_entities
        GROUP BY entity_type
        ORDER BY count DESC
        LIMIT 10
        """)
        entity_types = self.cursor.fetchall()

        # Source distribution
        self.cursor.execute("""
        SELECT source, COUNT(*) as count, AVG(relevance_score) as avg_relevance
        FROM mcf_documents
        GROUP BY source
        ORDER BY count DESC
        """)
        sources = self.cursor.fetchall()

        # Top entities by mentions
        self.cursor.execute("""
        SELECT e.name, e.entity_type, COUNT(de.doc_id) as mentions
        FROM mcf_entities e
        JOIN mcf_document_entities de ON e.entity_id = de.entity_id
        GROUP BY e.entity_id
        ORDER BY mentions DESC
        LIMIT 10
        """)
        top_entities = self.cursor.fetchall()

        logging.info(f"Total Documents: {total_docs}")
        logging.info(f"Total Entities: {total_entities}")
        logging.info(f"Total Relationships: {total_relationships}")
        logging.info(f"Import Errors: {len(self.stats['errors'])}")

        logging.info("\nEntity Types:")
        for entity_type, count in entity_types:
            logging.info(f"  {entity_type}: {count}")

        logging.info("\nSources:")
        for source, count, relevance in sources:
            logging.info(f"  {source}: {count} docs, {relevance:.2f} avg relevance")

        logging.info("\nTop Entities by Mentions:")
        for name, entity_type, mentions in top_entities:
            logging.info(f"  {name} ({entity_type}): {mentions} mentions")

        logging.info("="*60)

    def run(self):
        """Execute the complete import process"""
        try:
            # Create tables
            self.create_tables()

            # Import MCF data
            self.import_mcf_data()

            # Generate statistics
            self.generate_statistics()

            # Save any errors
            if self.stats["errors"]:
                error_file = Path("mcf_import_errors.txt")
                with open(error_file, 'w') as f:
                    for error in self.stats["errors"]:
                        f.write(f"{error}\n")
                logging.warning(f"Import errors saved to {error_file}")

            logging.info("\nMCF data successfully imported to SQL database!")
            logging.info(f"Database location: {self.db_path}")

        except Exception as e:
            logging.error(f"Fatal error during import: {e}")
            self.conn.rollback()
            raise
        finally:
            self.conn.close()

def main():
    """Main execution function"""
    importer = MCFSQLImporter()
    importer.run()

if __name__ == "__main__":
    main()

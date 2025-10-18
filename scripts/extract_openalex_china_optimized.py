#!/usr/bin/env python3
"""
Optimized extraction of China-related data from OpenAlex snapshot
Processes data in batches to avoid timeouts
"""

import sqlite3
import json
import gzip
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Generator
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class OpenAlexChinaExtractor:
    def __init__(self):
        self.base_path = Path("F:/OSINT_BACKUPS/openalex/data")
        self.output_db = "F:/OSINT_WAREHOUSE/osint_master.db"
        self.batch_size = 10000  # Process in batches
        self.china_keywords = {
            'china', 'chinese', 'beijing', 'shanghai', 'guangzhou',
            'shenzhen', 'wuhan', 'tianjin', 'chengdu', 'nanjing',
            'tsinghua', 'peking', 'fudan', 'zhejiang', 'cas',
            'academy of sciences', '中国', '中文', '北京', '上海'
        }

    def setup_database(self):
        """Create optimized database schema with indexes"""
        conn = sqlite3.connect(self.output_db)
        cursor = conn.cursor()

        # Main extraction table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS china_entities (
                entity_id TEXT PRIMARY KEY,
                entity_type TEXT,
                name TEXT,
                chinese_name TEXT,
                location TEXT,
                risk_indicators TEXT,
                collaboration_count INTEGER,
                citation_count INTEGER,
                h_index INTEGER,
                works_count INTEGER,
                extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Collaborations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS china_collaborations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chinese_entity_id TEXT,
                partner_entity_id TEXT,
                partner_name TEXT,
                partner_country TEXT,
                collaboration_type TEXT,
                work_count INTEGER,
                latest_year INTEGER
            )
        """)

        # Research topics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS china_research_topics (
                entity_id TEXT,
                topic TEXT,
                count INTEGER,
                PRIMARY KEY (entity_id, topic)
            )
        """)

        # Create indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_entity_type ON china_entities(entity_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_risk ON china_entities(risk_indicators)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chinese_entity ON china_collaborations(chinese_entity_id)")

        conn.commit()
        conn.close()
        logging.info("Database schema created with indexes")

    def is_china_related(self, text: str) -> bool:
        """Quick check if text is China-related"""
        if not text:
            return False
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.china_keywords)

    def extract_risk_indicators(self, entity: Dict) -> List[str]:
        """Extract risk indicators from entity data"""
        indicators = []

        # Check name for defense/military keywords
        name_lower = str(entity.get('display_name', '')).lower()
        if any(word in name_lower for word in ['defense', 'defence', 'military', 'army', 'navy', 'air force']):
            indicators.append('DEFENSE')
        if any(word in name_lower for word in ['nuclear', 'atomic', 'missile', 'rocket']):
            indicators.append('NUCLEAR')
        if any(word in name_lower for word in ['aerospace', 'space', 'satellite']):
            indicators.append('AEROSPACE')
        if 'academy of sciences' in name_lower:
            indicators.append('CAS')
        if any(word in name_lower for word in ['artificial intelligence', 'ai ', 'machine learning', 'deep learning']):
            indicators.append('AI')
        if any(word in name_lower for word in ['quantum', 'cryptograph']):
            indicators.append('QUANTUM')
        if any(word in name_lower for word in ['semiconductor', 'chip', 'integrated circuit']):
            indicators.append('SEMICONDUCTOR')

        return indicators

    def process_institutions_batch(self):
        """Process institutions in batches"""
        logging.info("Starting batch processing of institutions")

        institutions_path = self.base_path / "institutions"
        if not institutions_path.exists():
            logging.warning(f"Institutions path not found: {institutions_path}")
            return

        conn = sqlite3.connect(self.output_db)
        cursor = conn.cursor()

        china_count = 0
        total_processed = 0
        batch_data = []

        # Process only first few files to avoid timeout
        gz_files = list(institutions_path.glob("*.gz"))[:5]  # Process first 5 files

        for gz_file in gz_files:
            logging.info(f"Processing {gz_file.name}")

            try:
                with gzip.open(gz_file, 'rt', encoding='utf-8') as f:
                    for line in f:
                        if not line.strip():
                            continue

                        try:
                            data = json.loads(line)
                            total_processed += 1

                            # Check if China-related
                            is_china = False

                            # Check country
                            country = data.get('country_code', '')
                            if country in ['CN', 'CHN', 'China']:
                                is_china = True

                            # Check display name
                            if not is_china and self.is_china_related(data.get('display_name', '')):
                                is_china = True

                            # Check location
                            geo = data.get('geo', {})
                            if geo and not is_china:
                                if self.is_china_related(geo.get('city', '')) or \
                                   self.is_china_related(geo.get('region', '')):
                                    is_china = True

                            if is_china:
                                china_count += 1

                                # Extract risk indicators
                                risk_indicators = self.extract_risk_indicators(data)

                                # Prepare data for batch insert
                                batch_data.append((
                                    data.get('id', ''),
                                    'institution',
                                    data.get('display_name', ''),
                                    data.get('display_name_alternatives', [None])[0] if data.get('display_name_alternatives') else None,
                                    f"{geo.get('city', '')}, {geo.get('region', '')}" if geo else '',
                                    ','.join(risk_indicators),
                                    data.get('works_count', 0),
                                    data.get('cited_by_count', 0),
                                    None,  # h_index not available for institutions
                                    data.get('works_count', 0)
                                ))

                                # Insert in batches
                                if len(batch_data) >= self.batch_size:
                                    cursor.executemany("""
                                        INSERT OR IGNORE INTO china_entities
                                        (entity_id, entity_type, name, chinese_name, location,
                                         risk_indicators, collaboration_count, citation_count, h_index, works_count)
                                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                    """, batch_data)
                                    conn.commit()
                                    logging.info(f"Inserted batch of {len(batch_data)} institutions")
                                    batch_data = []

                            if total_processed % 10000 == 0:
                                logging.info(f"Processed {total_processed:,} institutions, found {china_count:,} Chinese")

                        except json.JSONDecodeError:
                            continue
                        except Exception as e:
                            continue

            except Exception as e:
                logging.error(f"Error processing {gz_file}: {e}")
                continue

        # Insert remaining data
        if batch_data:
            cursor.executemany("""
                INSERT OR IGNORE INTO china_entities
                (entity_id, entity_type, name, chinese_name, location,
                 risk_indicators, collaboration_count, citation_count, h_index, works_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, batch_data)
            conn.commit()

        conn.close()
        logging.info(f"Completed institutions: {total_processed:,} processed, {china_count:,} Chinese found")
        return china_count

    def process_authors_sample(self):
        """Process a sample of authors to find Chinese researchers"""
        logging.info("Processing sample of authors")

        authors_path = self.base_path / "authors"
        if not authors_path.exists():
            logging.warning(f"Authors path not found: {authors_path}")
            return

        conn = sqlite3.connect(self.output_db)
        cursor = conn.cursor()

        china_count = 0
        total_processed = 0
        batch_data = []

        # Process only first 2 files as sample
        gz_files = list(authors_path.glob("*.gz"))[:2]

        for gz_file in gz_files:
            logging.info(f"Processing {gz_file.name}")

            try:
                with gzip.open(gz_file, 'rt', encoding='utf-8') as f:
                    for line in f:
                        if not line.strip():
                            continue

                        try:
                            data = json.loads(line)
                            total_processed += 1

                            # Check last known institution
                            last_inst = data.get('last_known_institution', {})
                            is_china = False

                            if last_inst:
                                country = last_inst.get('country_code', '')
                                if country in ['CN', 'CHN', 'China']:
                                    is_china = True
                                elif self.is_china_related(last_inst.get('display_name', '')):
                                    is_china = True

                            # Check display name
                            if not is_china and self.is_china_related(data.get('display_name', '')):
                                is_china = True

                            if is_china:
                                china_count += 1

                                # Extract topics
                                topics = data.get('topics', [])
                                if topics:
                                    for topic in topics[:5]:  # Top 5 topics
                                        cursor.execute("""
                                            INSERT OR REPLACE INTO china_research_topics
                                            (entity_id, topic, count)
                                            VALUES (?, ?, ?)
                                        """, (
                                            data.get('id', ''),
                                            topic.get('display_name', ''),
                                            topic.get('count', 0)
                                        ))

                                batch_data.append((
                                    data.get('id', ''),
                                    'author',
                                    data.get('display_name', ''),
                                    None,  # No Chinese name for authors
                                    last_inst.get('display_name', '') if last_inst else '',
                                    '',  # Risk indicators computed separately
                                    0,  # Collaboration count computed separately
                                    data.get('cited_by_count', 0),
                                    data.get('summary_stats', {}).get('h_index', 0),
                                    data.get('works_count', 0)
                                ))

                                if len(batch_data) >= self.batch_size:
                                    cursor.executemany("""
                                        INSERT OR IGNORE INTO china_entities
                                        (entity_id, entity_type, name, chinese_name, location,
                                         risk_indicators, collaboration_count, citation_count, h_index, works_count)
                                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                    """, batch_data)
                                    conn.commit()
                                    batch_data = []

                            if total_processed % 10000 == 0:
                                logging.info(f"Processed {total_processed:,} authors, found {china_count:,} Chinese")

                        except Exception:
                            continue

            except Exception as e:
                logging.error(f"Error processing {gz_file}: {e}")

        # Insert remaining data
        if batch_data:
            cursor.executemany("""
                INSERT OR IGNORE INTO china_entities
                (entity_id, entity_type, name, chinese_name, location,
                 risk_indicators, collaboration_count, citation_count, h_index, works_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, batch_data)
            conn.commit()

        conn.close()
        logging.info(f"Completed authors sample: {total_processed:,} processed, {china_count:,} Chinese found")
        return china_count

    def generate_summary_report(self):
        """Generate summary statistics"""
        conn = sqlite3.connect(self.output_db)
        cursor = conn.cursor()

        report = []
        report.append("=" * 80)
        report.append("OPENALEX CHINA DATA EXTRACTION SUMMARY")
        report.append("=" * 80)

        # Entity counts by type
        cursor.execute("""
            SELECT entity_type, COUNT(*)
            FROM china_entities
            GROUP BY entity_type
        """)
        type_counts = cursor.fetchall()

        report.append("\n### Entities by Type:")
        for entity_type, count in type_counts:
            report.append(f"  {entity_type}: {count:,}")

        # Top risk indicators
        cursor.execute("""
            SELECT risk_indicators, COUNT(*) as cnt
            FROM china_entities
            WHERE risk_indicators != ''
            GROUP BY risk_indicators
            ORDER BY cnt DESC
            LIMIT 10
        """)
        risk_counts = cursor.fetchall()

        if risk_counts:
            report.append("\n### Top Risk Indicators:")
            for indicators, count in risk_counts:
                report.append(f"  {indicators}: {count:,}")

        # Top institutions by citations
        cursor.execute("""
            SELECT name, citation_count, risk_indicators
            FROM china_entities
            WHERE entity_type = 'institution'
            ORDER BY citation_count DESC
            LIMIT 10
        """)
        top_institutions = cursor.fetchall()

        if top_institutions:
            report.append("\n### Top Institutions by Citations:")
            for i, (name, citations, risk) in enumerate(top_institutions, 1):
                risk_str = f" [{risk}]" if risk else ""
                report.append(f"  {i}. {name}: {citations:,} citations{risk_str}")

        # Research topics
        cursor.execute("""
            SELECT topic, SUM(count) as total
            FROM china_research_topics
            GROUP BY topic
            ORDER BY total DESC
            LIMIT 10
        """)
        topics = cursor.fetchall()

        if topics:
            report.append("\n### Top Research Topics:")
            for topic, count in topics:
                report.append(f"  {topic}: {count:,}")

        conn.close()
        return "\n".join(report)

def main():
    """Main execution"""
    start_time = time.time()

    extractor = OpenAlexChinaExtractor()

    # Setup database
    extractor.setup_database()

    # Process data in stages
    logging.info("Starting optimized OpenAlex China extraction")

    # Stage 1: Institutions (most important)
    inst_count = extractor.process_institutions_batch()

    # Stage 2: Authors sample
    author_count = extractor.process_authors_sample()

    # Generate report
    report = extractor.generate_summary_report()
    print(report)

    # Save report
    report_path = Path("C:/Projects/OSINT - Foresight/analysis/openalex_china_extraction_report.md")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    elapsed = time.time() - start_time
    logging.info(f"Extraction completed in {elapsed:.1f} seconds")
    logging.info(f"Report saved to {report_path}")

    return {
        'institutions': inst_count,
        'authors': author_count,
        'elapsed_time': elapsed
    }

if __name__ == "__main__":
    results = main()
    print(f"\nExtraction complete: {results}")

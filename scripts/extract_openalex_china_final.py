#!/usr/bin/env python3
"""
Final OpenAlex China extraction with correct directory structure
"""

import sqlite3
import json
import gzip
import logging
from pathlib import Path
from datetime import datetime
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class OpenAlexChinaFinalExtractor:
    def __init__(self):
        self.base_path = Path("F:/OSINT_BACKUPS/openalex/data")
        self.output_db = "F:/OSINT_WAREHOUSE/osint_master.db"
        self.master_db = "F:/OSINT_WAREHOUSE/osint_master.db"
        self.batch_size = 5000
        self.china_keywords = {
            'china', 'chinese', 'beijing', 'shanghai', 'guangzhou',
            'shenzhen', 'wuhan', 'tianjin', 'chengdu', 'nanjing',
            'tsinghua', 'peking', 'fudan', 'zhejiang', 'cas',
            'academy of sciences', '中国', '中文', '北京', '上海'
        }

    def setup_database(self):
        """Create database schema"""
        conn = sqlite3.connect(self.output_db)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS openalex_china_entities (
                entity_id TEXT PRIMARY KEY,
                entity_type TEXT,
                name TEXT,
                country_code TEXT,
                city TEXT,
                region TEXT,
                works_count INTEGER,
                cited_by_count INTEGER,
                h_index INTEGER,
                risk_indicators TEXT,
                extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS openalex_extraction_stats (
                entity_type TEXT PRIMARY KEY,
                total_processed INTEGER,
                china_found INTEGER,
                high_risk_found INTEGER,
                extraction_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()
        logging.info("Database schema created")

    def is_china_related(self, data: dict) -> bool:
        """Check if entity is China-related"""
        # Check country code
        country = data.get('country_code', '')
        if country in ['CN', 'CHN', 'China']:
            return True

        # Check display name
        name = str(data.get('display_name', '')).lower()
        if any(keyword in name for keyword in self.china_keywords):
            return True

        # Check geo location
        geo = data.get('geo', {})
        if geo:
            city = str(geo.get('city', '')).lower()
            region = str(geo.get('region', '')).lower()
            if any(keyword in city for keyword in self.china_keywords) or \
               any(keyword in region for keyword in self.china_keywords):
                return True

        # Check alternative names
        alt_names = data.get('display_name_alternatives', [])
        if alt_names:
            for alt in alt_names:
                if any(keyword in str(alt).lower() for keyword in self.china_keywords):
                    return True

        return False

    def extract_risk_indicators(self, data: dict) -> list:
        """Extract risk indicators"""
        indicators = []
        name_lower = str(data.get('display_name', '')).lower()

        # Defense/Military
        if any(word in name_lower for word in ['defense', 'defence', 'military', 'army', 'navy', 'air force', '国防', '军事']):
            indicators.append('DEFENSE')

        # Nuclear/Weapons
        if any(word in name_lower for word in ['nuclear', 'atomic', 'missile', 'rocket', 'weapon', '核', '导弹']):
            indicators.append('NUCLEAR')

        # Aerospace
        if any(word in name_lower for word in ['aerospace', 'space', 'satellite', 'aviation', '航空', '航天']):
            indicators.append('AEROSPACE')

        # Academy of Sciences
        if 'academy of sciences' in name_lower or '科学院' in name_lower or 'cas' in name_lower:
            indicators.append('CAS')

        # AI/ML
        if any(word in name_lower for word in ['artificial intelligence', 'machine learning', 'deep learning', 'ai ', '人工智能']):
            indicators.append('AI')

        # Quantum
        if any(word in name_lower for word in ['quantum', 'cryptograph', '量子']):
            indicators.append('QUANTUM')

        # Semiconductor
        if any(word in name_lower for word in ['semiconductor', 'chip', 'integrated circuit', '半导体', '芯片']):
            indicators.append('SEMICONDUCTOR')

        # Seven Sons universities
        seven_sons = ['beihang', 'beijing institute of technology', 'harbin institute',
                      'harbin engineering', 'northwestern polytechnical', 'nanjing university of aeronautics',
                      'nanjing university of science']
        if any(uni in name_lower for uni in seven_sons):
            indicators.append('SEVEN_SONS')

        return indicators

    def process_institutions(self):
        """Process institution files from all date directories"""
        logging.info("Processing institutions")

        institutions_path = self.base_path / "institutions"
        if not institutions_path.exists():
            logging.error(f"Institutions path not found: {institutions_path}")
            return 0

        conn = sqlite3.connect(self.output_db)
        cursor = conn.cursor()

        total_processed = 0
        china_found = 0
        high_risk_found = 0
        batch_data = []

        # Get all date directories
        date_dirs = sorted([d for d in institutions_path.iterdir() if d.is_dir() and 'updated_date=' in d.name])

        # Process recent directories (last 10)
        for date_dir in date_dirs[-10:]:
            logging.info(f"Processing {date_dir.name}")

            # Get gz files in this directory
            gz_files = list(date_dir.glob("*.gz"))

            for gz_file in gz_files:
                try:
                    with gzip.open(gz_file, 'rt', encoding='utf-8') as f:
                        for line in f:
                            if not line.strip():
                                continue

                            try:
                                data = json.loads(line)
                                total_processed += 1

                                if self.is_china_related(data):
                                    china_found += 1

                                    # Extract risk indicators
                                    risk_indicators = self.extract_risk_indicators(data)
                                    if risk_indicators:
                                        high_risk_found += 1

                                    # Extract geo data
                                    geo = data.get('geo', {})

                                    batch_data.append((
                                        data.get('id', ''),
                                        'institution',
                                        data.get('display_name', ''),
                                        data.get('country_code', ''),
                                        geo.get('city', '') if geo else '',
                                        geo.get('region', '') if geo else '',
                                        data.get('works_count', 0),
                                        data.get('cited_by_count', 0),
                                        None,  # h_index
                                        ','.join(risk_indicators)
                                    ))

                                    # Insert batch
                                    if len(batch_data) >= self.batch_size:
                                        cursor.executemany("""
                                            INSERT OR IGNORE INTO import_openalex_china_entities
                                            (entity_id, entity_type, name, country_code, city, region,
                                             works_count, cited_by_count, h_index, risk_indicators)
                                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                        """, batch_data)
                                        conn.commit()
                                        logging.info(f"Inserted batch: {total_processed:,} processed, {china_found:,} Chinese")
                                        batch_data = []

                                if total_processed % 10000 == 0:
                                    logging.info(f"Progress: {total_processed:,} processed, {china_found:,} Chinese, {high_risk_found:,} high-risk")

                            except json.JSONDecodeError:
                                continue
                            except Exception:
                                continue

                except Exception as e:
                    logging.error(f"Error processing {gz_file}: {e}")
                    continue

        # Insert remaining
        if batch_data:
            cursor.executemany("""
                INSERT OR IGNORE INTO import_openalex_china_entities
                (entity_id, entity_type, name, country_code, city, region,
                 works_count, cited_by_count, h_index, risk_indicators)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, batch_data)
            conn.commit()

        # Save stats
        cursor.execute("""
            INSERT OR REPLACE INTO openalex_extraction_stats
            (entity_type, total_processed, china_found, high_risk_found)
            VALUES (?, ?, ?, ?)
        """, ('institution', total_processed, china_found, high_risk_found))

        conn.commit()
        conn.close()

        logging.info(f"Institutions complete: {total_processed:,} processed, {china_found:,} Chinese, {high_risk_found:,} high-risk")
        return china_found

    def process_authors_sample(self):
        """Process sample of authors"""
        logging.info("Processing authors sample")

        authors_path = self.base_path / "authors"
        if not authors_path.exists():
            logging.error(f"Authors path not found: {authors_path}")
            return 0

        conn = sqlite3.connect(self.output_db)
        cursor = conn.cursor()

        total_processed = 0
        china_found = 0
        batch_data = []

        # Get recent date directories
        date_dirs = sorted([d for d in authors_path.iterdir() if d.is_dir() and 'updated_date=' in d.name])

        # Process only last 2 directories as sample
        for date_dir in date_dirs[-2:]:
            logging.info(f"Processing {date_dir.name}")

            # Get first gz file only
            gz_files = list(date_dir.glob("*.gz"))[:1]

            for gz_file in gz_files:
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
                                    elif any(keyword in str(last_inst.get('display_name', '')).lower()
                                           for keyword in self.china_keywords):
                                        is_china = True

                                if is_china:
                                    china_found += 1

                                    batch_data.append((
                                        data.get('id', ''),
                                        'author',
                                        data.get('display_name', ''),
                                        last_inst.get('country_code', '') if last_inst else '',
                                        '',  # city
                                        '',  # region
                                        data.get('works_count', 0),
                                        data.get('cited_by_count', 0),
                                        data.get('summary_stats', {}).get('h_index', 0) if data.get('summary_stats') else 0,
                                        ''  # risk indicators
                                    ))

                                    if len(batch_data) >= self.batch_size:
                                        cursor.executemany("""
                                            INSERT OR IGNORE INTO import_openalex_china_entities
                                            (entity_id, entity_type, name, country_code, city, region,
                                             works_count, cited_by_count, h_index, risk_indicators)
                                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                        """, batch_data)
                                        conn.commit()
                                        batch_data = []

                                if total_processed >= 50000:  # Limit sample size
                                    break

                            except Exception:
                                continue

                except Exception as e:
                    logging.error(f"Error processing {gz_file}: {e}")

        # Insert remaining
        if batch_data:
            cursor.executemany("""
                INSERT OR IGNORE INTO import_openalex_china_entities
                (entity_id, entity_type, name, country_code, city, region,
                 works_count, cited_by_count, h_index, risk_indicators)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, batch_data)
            conn.commit()

        # Save stats
        cursor.execute("""
            INSERT OR REPLACE INTO openalex_extraction_stats
            (entity_type, total_processed, china_found, high_risk_found)
            VALUES (?, ?, ?, ?)
        """, ('author', total_processed, china_found, 0))

        conn.commit()
        conn.close()

        logging.info(f"Authors complete: {total_processed:,} processed, {china_found:,} Chinese")
        return china_found

    def store_in_master_db(self):
        """Store high-value entities in master database"""
        logging.info("Storing high-value entities in master database")

        # Connect to both databases
        conn_source = sqlite3.connect(self.output_db)
        conn_master = sqlite3.connect(self.master_db)

        cursor_source = conn_source.cursor()
        cursor_master = conn_master.cursor()

        # Create table in master
        cursor_master.execute("""
            CREATE TABLE IF NOT EXISTS openalex_china_high_risk (
                entity_id TEXT PRIMARY KEY,
                entity_type TEXT,
                name TEXT,
                country_code TEXT,
                location TEXT,
                works_count INTEGER,
                cited_by_count INTEGER,
                h_index INTEGER,
                risk_indicators TEXT,
                risk_score INTEGER,
                extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Get high-risk entities
        cursor_source.execute("""
            SELECT * FROM import_openalex_china_entities
            WHERE risk_indicators != ''
            ORDER BY cited_by_count DESC
            LIMIT 1000
        """)

        high_risk_entities = cursor_source.fetchall()

        for entity in high_risk_entities:
            # Calculate risk score
            risk_indicators = entity[9] if len(entity) > 9 else ''
            risk_score = 0

            if 'DEFENSE' in risk_indicators:
                risk_score += 90
            if 'NUCLEAR' in risk_indicators:
                risk_score += 100
            if 'CAS' in risk_indicators:
                risk_score += 70
            if 'SEVEN_SONS' in risk_indicators:
                risk_score += 85
            if 'AI' in risk_indicators:
                risk_score += 60
            if 'QUANTUM' in risk_indicators:
                risk_score += 80
            if 'SEMICONDUCTOR' in risk_indicators:
                risk_score += 75
            if 'AEROSPACE' in risk_indicators:
                risk_score += 70

            location = f"{entity[4]}, {entity[5]}" if len(entity) > 5 else ''

            cursor_master.execute("""
                INSERT OR REPLACE INTO openalex_china_high_risk
                (entity_id, entity_type, name, country_code, location,
                 works_count, cited_by_count, h_index, risk_indicators, risk_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                entity[0], entity[1], entity[2], entity[3], location,
                entity[6] if len(entity) > 6 else 0,
                entity[7] if len(entity) > 7 else 0,
                entity[8] if len(entity) > 8 else 0,
                risk_indicators, risk_score
            ))

        conn_master.commit()

        # Get counts
        cursor_master.execute("SELECT COUNT(*) FROM openalex_china_high_risk")
        high_risk_count = cursor_master.fetchone()[0]

        conn_source.close()
        conn_master.close()

        logging.info(f"Stored {high_risk_count} high-risk entities in master database")
        return high_risk_count

    def generate_report(self):
        """Generate final report"""
        conn = sqlite3.connect(self.output_db)
        cursor = conn.cursor()

        report = []
        report.append("=" * 80)
        report.append("OPENALEX CHINA EXTRACTION - FINAL REPORT")
        report.append("=" * 80)
        report.append(f"\nExtraction Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Get stats
        cursor.execute("SELECT * FROM openalex_extraction_stats")
        stats = cursor.fetchall()

        report.append("\n### Extraction Statistics:")
        total_china = 0
        total_high_risk = 0
        for stat in stats:
            report.append(f"  {stat[0].capitalize()}:")
            report.append(f"    - Total processed: {stat[1]:,}")
            report.append(f"    - China found: {stat[2]:,}")
            report.append(f"    - High risk: {stat[3]:,}")
            total_china += stat[2]
            total_high_risk += stat[3]

        report.append(f"\n  TOTAL China entities: {total_china:,}")
        report.append(f"  TOTAL High-risk entities: {total_high_risk:,}")

        # Top institutions by citations
        cursor.execute("""
            SELECT name, cited_by_count, works_count, risk_indicators
            FROM import_openalex_china_entities
            WHERE entity_type = 'institution'
            ORDER BY cited_by_count DESC
            LIMIT 15
        """)
        top_institutions = cursor.fetchall()

        if top_institutions:
            report.append("\n### Top Chinese Institutions by Citations:")
            for i, (name, citations, works, risk) in enumerate(top_institutions, 1):
                risk_str = f" [{risk}]" if risk else ""
                report.append(f"  {i:2}. {name[:60]:<60} {citations:>10,} citations, {works:>7,} works{risk_str}")

        # Risk indicator distribution
        cursor.execute("""
            SELECT risk_indicators, COUNT(*) as cnt
            FROM import_openalex_china_entities
            WHERE risk_indicators != ''
            GROUP BY risk_indicators
            ORDER BY cnt DESC
            LIMIT 10
        """)
        risk_dist = cursor.fetchall()

        if risk_dist:
            report.append("\n### Risk Indicator Distribution:")
            for indicators, count in risk_dist:
                report.append(f"  {indicators:<30} {count:>5,} entities")

        # Geographic distribution
        cursor.execute("""
            SELECT city, COUNT(*) as cnt
            FROM import_openalex_china_entities
            WHERE city != '' AND entity_type = 'institution'
            GROUP BY city
            ORDER BY cnt DESC
            LIMIT 10
        """)
        cities = cursor.fetchall()

        if cities:
            report.append("\n### Top Chinese Cities:")
            for city, count in cities:
                report.append(f"  {city:<25} {count:>5,} institutions")

        conn.close()
        return "\n".join(report)

def main():
    """Main execution"""
    start_time = time.time()

    extractor = OpenAlexChinaFinalExtractor()

    # Setup
    extractor.setup_database()

    # Process institutions
    inst_count = extractor.process_institutions()

    # Process authors sample
    auth_count = extractor.process_authors_sample()

    # Store in master database
    high_risk_stored = extractor.store_in_master_db()

    # Generate report
    report = extractor.generate_report()
    print(report)

    # Save report
    report_path = Path("C:/Projects/OSINT - Foresight/analysis/OPENALEX_CHINA_FINAL_REPORT.md")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    elapsed = time.time() - start_time

    print(f"\n" + "=" * 80)
    print(f"Extraction completed in {elapsed:.1f} seconds")
    print(f"Institutions found: {inst_count:,}")
    print(f"Authors found: {auth_count:,}")
    print(f"High-risk entities stored: {high_risk_stored:,}")
    print(f"Report saved to: {report_path}")

    return {
        'institutions': inst_count,
        'authors': auth_count,
        'high_risk': high_risk_stored,
        'elapsed': elapsed
    }

if __name__ == "__main__":
    results = main()

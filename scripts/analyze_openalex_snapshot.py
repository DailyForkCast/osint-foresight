#!/usr/bin/env python3
"""
Comprehensive analysis of OpenAlex snapshot data to extract China-related research intelligence
OpenAlex contains: authors, institutions, works, concepts, funders, publishers, sources
"""

import gzip
import json
import sqlite3
import logging
from pathlib import Path
from datetime import datetime
from collections import defaultdict

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class OpenAlexAnalyzer:
    def __init__(self):
        self.base_path = Path("F:/OSINT_BACKUPS/openalex/data")
        self.output_db = "F:/OSINT_WAREHOUSE/osint_master.db"
        self.master_db = "F:/OSINT_WAREHOUSE/osint_master.db"

        # Chinese institution identifiers
        self.chinese_keywords = {
            'institutions': ['China', 'Chinese', 'Beijing', 'Shanghai', 'Tsinghua',
                           'Peking', 'Fudan', 'Zhejiang', 'Nanjing', 'Wuhan',
                           'Harbin', 'Xi\'an', 'Chengdu', 'Guangzhou', 'Shenzhen'],
            'countries': ['CN', 'CHN', 'China', 'P.R. China', 'PRC'],
            'languages': ['zh', 'chinese', 'mandarin']
        }

        # High-risk institutions
        self.high_risk_institutions = {
            'Chinese Academy of Sciences': 'CAS',
            'Tsinghua University': 'TOP_UNI',
            'Peking University': 'TOP_UNI',
            'Harbin Institute of Technology': 'DEFENSE_UNI',
            'Beijing Institute of Technology': 'DEFENSE_UNI',
            'Northwestern Polytechnical University': 'DEFENSE_UNI',
            'Beihang University': 'DEFENSE_UNI',
            'Harbin Engineering University': 'DEFENSE_UNI',
            'Nanjing University of Aeronautics': 'DEFENSE_UNI',
            'Nanjing University of Science': 'DEFENSE_UNI'
        }

        self.results = {
            'institutions': [],
            'authors': [],
            'works': [],
            'funders': [],
            'collaborations': defaultdict(int),
            'topics': defaultdict(int),
            'temporal_patterns': defaultdict(int)
        }

    def setup_database(self):
        """Create database schema for OpenAlex analysis"""
        conn = sqlite3.connect(self.output_db)
        cursor = conn.cursor()

        # Institutions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS openalex_institutions (
                id TEXT PRIMARY KEY,
                display_name TEXT,
                country_code TEXT,
                type TEXT,
                works_count INTEGER,
                cited_by_count INTEGER,
                is_chinese BOOLEAN,
                risk_category TEXT,
                homepage_url TEXT,
                ror_id TEXT,
                created_date TEXT,
                updated_date TEXT
            )
        """)

        # Authors table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS openalex_authors (
                id TEXT PRIMARY KEY,
                display_name TEXT,
                orcid TEXT,
                works_count INTEGER,
                cited_by_count INTEGER,
                last_known_institution TEXT,
                institution_country TEXT,
                is_chinese_affiliated BOOLEAN,
                h_index INTEGER,
                i10_index INTEGER,
                created_date TEXT,
                updated_date TEXT
            )
        """)

        # Works table (papers, publications)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS openalex_works (
                id TEXT PRIMARY KEY,
                doi TEXT,
                title TEXT,
                publication_year INTEGER,
                type TEXT,
                cited_by_count INTEGER,
                is_open_access BOOLEAN,
                chinese_authors INTEGER,
                total_authors INTEGER,
                chinese_institutions INTEGER,
                total_institutions INTEGER,
                primary_topic TEXT,
                topics TEXT,
                abstract TEXT,
                created_date TEXT
            )
        """)

        # Funders table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS openalex_funders (
                id TEXT PRIMARY KEY,
                display_name TEXT,
                country_code TEXT,
                is_chinese BOOLEAN,
                works_count INTEGER,
                grant_count INTEGER,
                created_date TEXT,
                updated_date TEXT
            )
        """)

        # Collaborations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS openalex_collaborations (
                chinese_institution TEXT,
                partner_institution TEXT,
                partner_country TEXT,
                collaboration_count INTEGER,
                PRIMARY KEY (chinese_institution, partner_institution)
            )
        """)

        # Topics analysis table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS openalex_china_topics (
                topic TEXT PRIMARY KEY,
                work_count INTEGER,
                is_sensitive BOOLEAN,
                technology_area TEXT
            )
        """)

        conn.commit()
        conn.close()
        logging.info("Database schema created")

    def is_chinese_entity(self, entity_data):
        """Check if an entity is Chinese based on various fields"""
        # Check country field
        if 'country' in entity_data:
            if entity_data['country'] in self.chinese_keywords['countries']:
                return True

        if 'country_code' in entity_data:
            if entity_data['country_code'] in ['CN', 'CHN']:
                return True

        # Check display name
        if 'display_name' in entity_data:
            name = entity_data['display_name'].lower()
            for keyword in self.chinese_keywords['institutions']:
                if keyword.lower() in name:
                    return True

        # Check geo coordinates (rough China boundaries)
        if 'geo' in entity_data and entity_data['geo']:
            lat = entity_data['geo'].get('latitude', 0)
            lon = entity_data['geo'].get('longitude', 0)
            if 18 < lat < 54 and 73 < lon < 135:  # Rough China boundaries
                return True

        return False

    def analyze_institutions(self):
        """Analyze institutions data"""
        logging.info("Analyzing institutions...")

        institutions_path = self.base_path / "institutions"
        if not institutions_path.exists():
            logging.warning("Institutions directory not found")
            return

        conn = sqlite3.connect(self.output_db)
        cursor = conn.cursor()

        chinese_count = 0
        total_count = 0

        # Process all institution files
        for date_dir in institutions_path.glob("updated_date=*/"):
            for gz_file in date_dir.glob("*.gz"):
                try:
                    with gzip.open(gz_file, 'rt', encoding='utf-8') as f:
                        for line in f:
                            if line.strip():
                                inst = json.loads(line)
                                total_count += 1

                                is_chinese = self.is_chinese_entity(inst)

                                if is_chinese or any(keyword.lower() in inst.get('display_name', '').lower()
                                                    for keyword in self.chinese_keywords['institutions']):
                                    chinese_count += 1

                                    # Determine risk category
                                    risk_category = None
                                    inst_name = inst.get('display_name', '')
                                    for risk_inst, category in self.high_risk_institutions.items():
                                        if risk_inst.lower() in inst_name.lower():
                                            risk_category = category
                                            break

                                    # Store in database
                                    cursor.execute("""
                                        INSERT OR REPLACE INTO openalex_institutions
                                        (id, display_name, country_code, type, works_count,
                                         cited_by_count, is_chinese, risk_category, homepage_url,
                                         ror_id, created_date, updated_date)
                                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                    """, (
                                        inst.get('id'),
                                        inst.get('display_name'),
                                        inst.get('country_code'),
                                        inst.get('type'),
                                        inst.get('works_count', 0),
                                        inst.get('cited_by_count', 0),
                                        1,
                                        risk_category,
                                        inst.get('homepage_url'),
                                        inst.get('ror'),
                                        inst.get('created_date'),
                                        inst.get('updated_date')
                                    ))

                                    self.results['institutions'].append({
                                        'name': inst.get('display_name'),
                                        'type': inst.get('type'),
                                        'works_count': inst.get('works_count', 0),
                                        'risk': risk_category
                                    })

                except Exception as e:
                    logging.error(f"Error processing {gz_file}: {e}")

        conn.commit()
        conn.close()

        logging.info(f"Found {chinese_count} Chinese institutions out of {total_count} total")
        return chinese_count

    def analyze_authors(self):
        """Analyze authors data"""
        logging.info("Analyzing authors...")

        authors_path = self.base_path / "authors"
        if not authors_path.exists():
            logging.warning("Authors directory not found")
            return

        conn = sqlite3.connect(self.output_db)
        cursor = conn.cursor()

        chinese_authors = 0
        sample_limit = 10000  # Process sample for performance

        # Get list of Chinese institutions
        cursor.execute("SELECT id, display_name FROM openalex_institutions WHERE is_chinese = 1")
        chinese_inst_ids = {row[0]: row[1] for row in cursor.fetchall()}

        # Process author files
        for date_dir in authors_path.glob("updated_date=*/"):
            for gz_file in date_dir.glob("*.gz"):
                try:
                    with gzip.open(gz_file, 'rt', encoding='utf-8') as f:
                        for i, line in enumerate(f):
                            if i > sample_limit:
                                break
                            if line.strip():
                                author = json.loads(line)

                                # Check if affiliated with Chinese institution
                                last_inst = author.get('last_known_institution', {})
                                is_chinese_affiliated = False

                                if last_inst:
                                    inst_id = last_inst.get('id')
                                    if inst_id in chinese_inst_ids:
                                        is_chinese_affiliated = True
                                    elif self.is_chinese_entity(last_inst):
                                        is_chinese_affiliated = True

                                if is_chinese_affiliated:
                                    chinese_authors += 1

                                    cursor.execute("""
                                        INSERT OR REPLACE INTO openalex_authors
                                        (id, display_name, orcid, works_count, cited_by_count,
                                         last_known_institution, institution_country,
                                         is_chinese_affiliated, h_index, i10_index,
                                         created_date, updated_date)
                                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                    """, (
                                        author.get('id'),
                                        author.get('display_name'),
                                        author.get('orcid'),
                                        author.get('works_count', 0),
                                        author.get('cited_by_count', 0),
                                        last_inst.get('display_name'),
                                        last_inst.get('country_code'),
                                        1,
                                        author.get('summary_stats', {}).get('h_index'),
                                        author.get('summary_stats', {}).get('i10_index'),
                                        author.get('created_date'),
                                        author.get('updated_date')
                                    ))

                except Exception as e:
                    logging.error(f"Error processing {gz_file}: {e}")

        conn.commit()
        conn.close()

        logging.info(f"Found {chinese_authors} Chinese-affiliated authors")
        return chinese_authors

    def analyze_works_sample(self):
        """Analyze a sample of works (papers) for China involvement"""
        logging.info("Analyzing works (sample)...")

        works_path = self.base_path / "works"
        if not works_path.exists():
            logging.warning("Works directory not found")
            return

        conn = sqlite3.connect(self.output_db)
        cursor = conn.cursor()

        # Get Chinese institutions and authors
        cursor.execute("SELECT id FROM openalex_institutions WHERE is_chinese = 1")
        chinese_inst_ids = {row[0] for row in cursor.fetchall()}

        cursor.execute("SELECT id FROM openalex_authors WHERE is_chinese_affiliated = 1")
        chinese_author_ids = {row[0] for row in cursor.fetchall()}

        china_works = 0
        sample_limit = 5000

        # Process only recent works for efficiency
        recent_dirs = sorted(works_path.glob("updated_date=*/"), reverse=True)[:5]

        for date_dir in recent_dirs:
            for gz_file in list(date_dir.glob("*.gz"))[:2]:  # Sample 2 files per date
                try:
                    with gzip.open(gz_file, 'rt', encoding='utf-8') as f:
                        for i, line in enumerate(f):
                            if i > sample_limit:
                                break
                            if line.strip():
                                work = json.loads(line)

                                # Check for Chinese involvement
                                chinese_auth_count = 0
                                chinese_inst_count = 0

                                # Check authorships
                                for authorship in work.get('authorships', []):
                                    if authorship.get('author', {}).get('id') in chinese_author_ids:
                                        chinese_auth_count += 1

                                    for inst in authorship.get('institutions', []):
                                        if inst.get('id') in chinese_inst_ids:
                                            chinese_inst_count += 1
                                            break

                                if chinese_auth_count > 0 or chinese_inst_count > 0:
                                    china_works += 1

                                    # Extract topics
                                    topics = []
                                    primary_topic = None
                                    if work.get('topics'):
                                        for topic in work['topics']:
                                            topics.append(topic.get('display_name'))
                                            if topic.get('score', 0) > 0.5:
                                                primary_topic = topic.get('display_name')
                                                self.results['topics'][primary_topic] += 1

                                    # Extract year for temporal analysis
                                    pub_year = work.get('publication_year')
                                    if pub_year:
                                        self.results['temporal_patterns'][pub_year] += 1

                                    cursor.execute("""
                                        INSERT OR IGNORE INTO openalex_works
                                        (id, doi, title, publication_year, type, cited_by_count,
                                         is_open_access, chinese_authors, total_authors,
                                         chinese_institutions, total_institutions,
                                         primary_topic, topics, created_date)
                                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                    """, (
                                        work.get('id'),
                                        work.get('doi'),
                                        work.get('title'),
                                        pub_year,
                                        work.get('type'),
                                        work.get('cited_by_count', 0),
                                        work.get('is_open_access', False),
                                        chinese_auth_count,
                                        len(work.get('authorships', [])),
                                        chinese_inst_count,
                                        len(set(inst.get('id') for auth in work.get('authorships', [])
                                               for inst in auth.get('institutions', []))),
                                        primary_topic,
                                        json.dumps(topics[:10]),
                                        work.get('created_date')
                                    ))

                except Exception as e:
                    logging.error(f"Error processing {gz_file}: {e}")

        conn.commit()
        conn.close()

        logging.info(f"Found {china_works} works with Chinese involvement")
        return china_works

    def analyze_funders(self):
        """Analyze funders data"""
        logging.info("Analyzing funders...")

        funders_path = self.base_path / "funders"
        if not funders_path.exists():
            logging.warning("Funders directory not found")
            return

        conn = sqlite3.connect(self.output_db)
        cursor = conn.cursor()

        chinese_funders = 0

        for date_dir in funders_path.glob("updated_date=*/"):
            for gz_file in date_dir.glob("*.gz"):
                try:
                    with gzip.open(gz_file, 'rt', encoding='utf-8') as f:
                        for line in f:
                            if line.strip():
                                funder = json.loads(line)

                                is_chinese = self.is_chinese_entity(funder)

                                if is_chinese:
                                    chinese_funders += 1

                                    cursor.execute("""
                                        INSERT OR REPLACE INTO openalex_funders
                                        (id, display_name, country_code, is_chinese,
                                         works_count, grant_count, created_date, updated_date)
                                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                    """, (
                                        funder.get('id'),
                                        funder.get('display_name'),
                                        funder.get('country_code'),
                                        1,
                                        funder.get('works_count', 0),
                                        funder.get('grants_count', 0),
                                        funder.get('created_date'),
                                        funder.get('updated_date')
                                    ))

                except Exception as e:
                    logging.error(f"Error processing {gz_file}: {e}")

        conn.commit()
        conn.close()

        logging.info(f"Found {chinese_funders} Chinese funding organizations")
        return chinese_funders

    def integrate_to_master(self):
        """Integrate results into master OSINT database"""
        logging.info("Integrating to master database...")

        conn_source = sqlite3.connect(self.output_db)
        conn_master = sqlite3.connect(self.master_db)

        cursor_master = conn_master.cursor()

        # Create summary table in master
        cursor_master.execute("""
            CREATE TABLE IF NOT EXISTS openalex_china_summary (
                entity_type TEXT PRIMARY KEY,
                entity_count INTEGER,
                high_risk_count INTEGER,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Get counts
        cursor_source = conn_source.cursor()

        cursor_source.execute("SELECT COUNT(*) FROM openalex_institutions WHERE is_chinese = 1")
        inst_count = cursor_source.fetchone()[0]

        cursor_source.execute("SELECT COUNT(*) FROM openalex_institutions WHERE risk_category IS NOT NULL")
        risk_count = cursor_source.fetchone()[0]

        cursor_source.execute("SELECT COUNT(*) FROM openalex_authors WHERE is_chinese_affiliated = 1")
        author_count = cursor_source.fetchone()[0]

        cursor_source.execute("SELECT COUNT(*) FROM openalex_works WHERE chinese_authors > 0")
        works_count = cursor_source.fetchone()[0]

        # Store summary
        cursor_master.execute("""
            INSERT OR REPLACE INTO openalex_china_summary
            (entity_type, entity_count, high_risk_count)
            VALUES
            ('institutions', ?, ?),
            ('authors', ?, 0),
            ('works', ?, 0)
        """, (inst_count, risk_count, author_count, works_count))

        conn_master.commit()
        conn_source.close()
        conn_master.close()

        logging.info("Integration complete")

    def generate_report(self):
        """Generate analysis report"""

        conn = sqlite3.connect(self.output_db)
        cursor = conn.cursor()

        print("\n" + "=" * 80)
        print("OPENALEX CHINA INTELLIGENCE ANALYSIS")
        print("=" * 80)

        # Institution statistics
        cursor.execute("""
            SELECT COUNT(*), SUM(works_count), SUM(cited_by_count)
            FROM openalex_institutions WHERE is_chinese = 1
        """)
        inst_stats = cursor.fetchone()
        print(f"\nChinese Institutions: {inst_stats[0]}")
        print(f"  Total works: {inst_stats[1]:,}")
        print(f"  Total citations: {inst_stats[2]:,}")

        # Top institutions
        print("\nTop 10 Chinese Institutions by Output:")
        cursor.execute("""
            SELECT display_name, works_count, cited_by_count, risk_category
            FROM openalex_institutions
            WHERE is_chinese = 1
            ORDER BY works_count DESC
            LIMIT 10
        """)
        for inst in cursor.fetchall():
            risk = f" [{inst[3]}]" if inst[3] else ""
            print(f"  {inst[0]}: {inst[1]:,} works, {inst[2]:,} citations{risk}")

        # High-risk institutions
        print("\nHigh-Risk Institutions Identified:")
        cursor.execute("""
            SELECT display_name, risk_category, works_count
            FROM openalex_institutions
            WHERE risk_category IS NOT NULL
            ORDER BY works_count DESC
        """)
        for inst in cursor.fetchall():
            print(f"  {inst[0]} ({inst[1]}): {inst[2]:,} works")

        # Author statistics
        cursor.execute("SELECT COUNT(*) FROM openalex_authors WHERE is_chinese_affiliated = 1")
        author_count = cursor.fetchone()[0]
        print(f"\nChinese-Affiliated Authors: {author_count}")

        # Work statistics
        cursor.execute("""
            SELECT COUNT(*), AVG(cited_by_count), MAX(cited_by_count)
            FROM openalex_works WHERE chinese_authors > 0
        """)
        work_stats = cursor.fetchone()
        print(f"\nWorks with Chinese Authors: {work_stats[0]}")
        print(f"  Average citations: {work_stats[1]:.1f}")
        print(f"  Most cited: {work_stats[2]:,} citations")

        # Top research topics
        if self.results['topics']:
            print("\nTop Research Topics:")
            for topic, count in sorted(self.results['topics'].items(),
                                      key=lambda x: x[1], reverse=True)[:10]:
                print(f"  {topic}: {count} papers")

        # Temporal trends
        if self.results['temporal_patterns']:
            print("\nPublication Trends (Last 5 Years):")
            recent_years = sorted(self.results['temporal_patterns'].keys(), reverse=True)[:5]
            for year in recent_years:
                count = self.results['temporal_patterns'][year]
                print(f"  {year}: {count} papers")

        conn.close()

        print("\n" + "=" * 80)
        print(f"Analysis complete. Database saved to: {self.output_db}")

    def run_analysis(self):
        """Run complete analysis pipeline"""
        logging.info("Starting OpenAlex analysis")

        self.setup_database()

        # Analyze each data type
        self.analyze_institutions()
        self.analyze_authors()
        self.analyze_works_sample()
        self.analyze_funders()

        # Integrate and report
        self.integrate_to_master()
        self.generate_report()

if __name__ == "__main__":
    analyzer = OpenAlexAnalyzer()
    analyzer.run_analysis()

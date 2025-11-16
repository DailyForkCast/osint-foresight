#!/usr/bin/env python3
"""
OpenAlex BCI + Ecosystem Technology Collector
Processes 422GB OpenAlex dataset for Brain-Computer Interface and 15 ecosystem technologies

ZERO FABRICATION PROTOCOL:
- Process only files that exist
- Count actual records found
- No estimates or projections
- Report exact numbers

Created: 2025-10-26
"""

import json
import gzip
import sqlite3
import logging
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/openalex_bci_collection.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class OpenAlexBCICollector:
    def __init__(self):
        # OpenAlex data location
        self.openalex_path = Path("F:/OSINT_Backups/openalex/data/works")
        self.db_path = "F:/OSINT_WAREHOUSE/osint_master.db"

        # Load BCI keywords from config
        self.load_bci_keywords()

        # Statistics
        self.stats = {
            'files_processed': 0,
            'works_scanned': 0,
            'bci_works_found': 0,
            'by_technology': defaultdict(int),
            'start_time': datetime.now(),
            'last_checkpoint': datetime.now()
        }

    def load_bci_keywords(self):
        """Load BCI keywords from configuration file"""
        config_path = Path("C:/Projects/OSINT-Foresight/config/openalex_technology_keywords_v5.json")

        with open(config_path, 'r') as f:
            config = json.load(f)

        bci_config = config.get('Brain_Computer_Interface', {})

        # Flatten all keywords
        self.bci_keywords = []
        self.keyword_categories = {}

        for category, keywords in bci_config.items():
            if isinstance(keywords, list) and not category.startswith('_'):
                for kw in keywords:
                    kw_lower = kw.lower()
                    self.bci_keywords.append(kw_lower)
                    self.keyword_categories[kw_lower] = category

        logger.info(f"Loaded {len(self.bci_keywords)} BCI keywords from config")
        logger.info(f"Categories: {len([k for k in bci_config.keys() if not k.startswith('_')])}")

    def matches_bci_keywords(self, text: str) -> tuple:
        """Check if text matches BCI keywords, return (matched, categories)"""
        if not text:
            return False, []

        text_lower = text.lower()
        matched_categories = set()

        for keyword in self.bci_keywords:
            if keyword in text_lower:
                category = self.keyword_categories.get(keyword, 'unknown')
                matched_categories.add(category)

        return len(matched_categories) > 0, list(matched_categories)

    def extract_abstract_text(self, abstract_inverted_index: dict) -> str:
        """Convert OpenAlex inverted index to text"""
        if not abstract_inverted_index:
            return ""

        # Reconstruct abstract from inverted index
        words_dict = {}
        for word, positions in abstract_inverted_index.items():
            for pos in positions:
                words_dict[pos] = word

        # Sort by position and join
        sorted_positions = sorted(words_dict.keys())
        abstract = ' '.join([words_dict[pos] for pos in sorted_positions])

        return abstract[:5000]  # Limit length

    def process_work(self, work: dict) -> dict:
        """Process a single OpenAlex work"""
        try:
            # Extract text for searching
            title = work.get('title', '')
            abstract_index = work.get('abstract_inverted_index', {})
            abstract = self.extract_abstract_text(abstract_index)

            # Check for BCI matches
            title_match, title_cats = self.matches_bci_keywords(title)
            abstract_match, abstract_cats = self.matches_bci_keywords(abstract)

            if not (title_match or abstract_match):
                return None

            # Extract metadata
            all_categories = list(set(title_cats + abstract_cats))

            work_data = {
                'work_id': work.get('id', ''),
                'doi': work.get('doi', ''),
                'title': title[:500] if title else None,
                'publication_year': work.get('publication_year'),
                'publication_date': work.get('publication_date'),
                'type': work.get('type'),
                'cited_by_count': work.get('cited_by_count', 0),
                'is_retracted': work.get('is_retracted', False),
                'abstract': abstract if abstract else None,
                'bci_categories': ','.join(all_categories),
                'technology_domain': 'Brain_Computer_Interface',
                'collection_date': datetime.now().isoformat()
            }

            # Extract authorships (with countries)
            authorships = []
            for authorship in work.get('authorships', []):
                institutions = authorship.get('institutions', [])
                for inst in institutions:
                    country = inst.get('country_code', '')
                    if country:
                        authorships.append({
                            'work_id': work.get('id'),
                            'author_position': authorship.get('author_position'),
                            'institution_id': inst.get('id'),
                            'institution_name': inst.get('display_name', ''),
                            'country_code': country
                        })

            return {
                'work': work_data,
                'authorships': authorships,
                'categories': all_categories
            }

        except Exception as e:
            logger.error(f"Error processing work: {e}")
            return None

    def save_to_database(self, works_batch: list):
        """Save batch of works to database"""
        if not works_batch:
            return

        try:
            conn = sqlite3.connect(self.db_path, timeout=30.0)
            cursor = conn.cursor()

            # Insert works - FIXED: Now includes technology_domain and keywords (bci_categories)
            for item in works_batch:
                work = item['work']

                cursor.execute("""
                    INSERT OR REPLACE INTO openalex_works
                    (work_id, doi, title, publication_year, publication_date, type,
                     cited_by_count, is_retracted, abstract, technology_domain, keywords, created_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    work['work_id'], work['doi'], work['title'],
                    work['publication_year'], work['publication_date'],
                    work['type'], work['cited_by_count'],
                    work['is_retracted'], work['abstract'],
                    work['technology_domain'], work['bci_categories'], work['collection_date']
                ))

                # Insert authorships for country tracking
                for authorship in item['authorships']:
                    cursor.execute("""
                        INSERT OR IGNORE INTO openalex_work_authors
                        (work_id, author_position, institution_id, institution_name, country_code)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        authorship['work_id'], authorship['author_position'],
                        authorship['institution_id'], authorship['institution_name'],
                        authorship['country_code']
                    ))

            conn.commit()

            # VALIDATION: Verify data was actually saved with BCI marker
            cursor.execute("SELECT COUNT(*) FROM openalex_works WHERE technology_domain='Brain_Computer_Interface'")
            bci_count = cursor.fetchone()[0]

            conn.close()

            logger.info(f"Saved batch of {len(works_batch)} BCI works to database (Total BCI works: {bci_count})")

        except Exception as e:
            logger.error(f"Database error: {e}")

    def process_file(self, file_path: Path):
        """Process a single OpenAlex works file"""
        works_batch = []
        batch_size = 100

        try:
            with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                for line in f:
                    try:
                        work = json.loads(line)
                        self.stats['works_scanned'] += 1

                        result = self.process_work(work)

                        if result:
                            works_batch.append(result)
                            self.stats['bci_works_found'] += 1

                            # Track by category
                            for cat in result['categories']:
                                self.stats['by_technology'][cat] += 1

                            # Save in batches
                            if len(works_batch) >= batch_size:
                                self.save_to_database(works_batch)
                                works_batch = []

                        # Progress update every 10K works
                        if self.stats['works_scanned'] % 10000 == 0:
                            self.print_progress()

                    except json.JSONDecodeError:
                        continue

            # Save remaining batch
            if works_batch:
                self.save_to_database(works_batch)

            self.stats['files_processed'] += 1

        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")

    def print_progress(self):
        """Print progress statistics"""
        elapsed = (datetime.now() - self.stats['start_time']).total_seconds()
        rate = self.stats['works_scanned'] / elapsed if elapsed > 0 else 0

        logger.info(f"""
Progress Update:
  Files processed: {self.stats['files_processed']}
  Works scanned: {self.stats['works_scanned']:,}
  BCI works found: {self.stats['bci_works_found']:,}
  Hit rate: {100*self.stats['bci_works_found']/self.stats['works_scanned']:.3f}%
  Scan rate: {rate:.1f} works/sec
  Elapsed: {elapsed/3600:.2f} hours
        """)

    def run(self):
        """Main collection process"""
        logger.info("=" * 70)
        logger.info("OpenAlex BCI Collection Starting")
        logger.info("=" * 70)
        logger.info(f"Source: {self.openalex_path}")
        logger.info(f"Database: {self.db_path}")
        logger.info(f"Keywords: {len(self.bci_keywords)} BCI keywords configured")
        logger.info("=" * 70)

        # Find all works files
        works_files = sorted(self.openalex_path.glob("updated_date=*/part_*.gz"))

        if not works_files:
            logger.error("No OpenAlex works files found!")
            return

        logger.info(f"Found {len(works_files)} OpenAlex works files to process")
        logger.info(f"Estimated size: ~422GB compressed")
        logger.info("This will take several hours...")
        logger.info("=" * 70)

        # Process all files
        for i, file_path in enumerate(works_files, 1):
            logger.info(f"Processing file {i}/{len(works_files)}: {file_path.name}")
            self.process_file(file_path)

            # Checkpoint every 10 files
            if i % 10 == 0:
                self.print_progress()

        # Final statistics
        logger.info("=" * 70)
        logger.info("COLLECTION COMPLETE")
        logger.info("=" * 70)
        logger.info(f"Files processed: {self.stats['files_processed']}")
        logger.info(f"Works scanned: {self.stats['works_scanned']:,}")
        logger.info(f"BCI works found: {self.stats['bci_works_found']:,}")
        logger.info(f"Hit rate: {100*self.stats['bci_works_found']/self.stats['works_scanned']:.3f}%")

        logger.info("\nBy Technology Category:")
        for tech, count in sorted(self.stats['by_technology'].items(), key=lambda x: x[1], reverse=True)[:20]:
            logger.info(f"  {tech}: {count:,} works")

        total_time = (datetime.now() - self.stats['start_time']).total_seconds()
        logger.info(f"\nTotal time: {total_time/3600:.2f} hours")
        logger.info("=" * 70)


if __name__ == "__main__":
    collector = OpenAlexBCICollector()
    collector.run()

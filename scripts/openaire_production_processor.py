#!/usr/bin/env python3
"""
OpenAIRE Production Processor - ALL EU Countries

Processes ALL OpenAIRE research data for comprehensive China collaboration
analysis across all EU countries and key targets.

Production configuration:
- All EU-27 countries + key non-EU
- Complete processing (no batch limits)
- Optimized for long-running operation
- Fixed Unicode issues for Windows
- Resume capability for multi-day processing
"""

import os
import sys
import json
import time
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Set
import logging

# Set UTF-8 encoding for Windows console
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add the collectors directory to Python path
sys.path.append(str(Path(__file__).parent / "collectors"))
from openaire_client import OpenAIREClient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ALL EU + key countries for complete coverage
ALL_TARGET_COUNTRIES = {
    # EU-27 Members (PRIMARY TARGETS)
    'AT': 'Austria', 'BE': 'Belgium', 'BG': 'Bulgaria', 'HR': 'Croatia',
    'CY': 'Cyprus', 'CZ': 'Czech Republic', 'DK': 'Denmark', 'EE': 'Estonia',
    'FI': 'Finland', 'FR': 'France', 'DE': 'Germany', 'GR': 'Greece',
    'HU': 'Hungary', 'IE': 'Ireland', 'IT': 'Italy', 'LV': 'Latvia',
    'LT': 'Lithuania', 'LU': 'Luxembourg', 'MT': 'Malta', 'NL': 'Netherlands',
    'PL': 'Poland', 'PT': 'Portugal', 'RO': 'Romania', 'SK': 'Slovakia',
    'SI': 'Slovenia', 'ES': 'Spain', 'SE': 'Sweden',

    # Key Non-EU European Countries
    'NO': 'Norway', 'CH': 'Switzerland', 'UK': 'United Kingdom', 'IS': 'Iceland',

    # Target Countries for Comparison
    'US': 'United States', 'JP': 'Japan', 'KR': 'South Korea',
    'CA': 'Canada', 'AU': 'Australia', 'IN': 'India', 'SG': 'Singapore',
    'TW': 'Taiwan', 'HK': 'Hong Kong'
}

# Priority order for processing
COUNTRY_PROCESSING_ORDER = [
    # Tier 1: Gateway Countries (HIGHEST PRIORITY)
    'HU', 'GR', 'IT', 'PL',

    # Tier 2: Major EU Economies
    'DE', 'FR', 'ES', 'NL', 'BE', 'SE', 'DK', 'FI', 'AT',

    # Tier 3: All other EU countries
    'CZ', 'PT', 'BG', 'HR', 'EE', 'LV', 'LT', 'LU', 'MT', 'RO', 'SK', 'SI', 'CY', 'IE',

    # Tier 4: Non-EU European
    'NO', 'CH', 'UK', 'IS',

    # Tier 5: Global comparison
    'US', 'JP', 'KR', 'CA', 'AU', 'IN', 'SG', 'TW', 'HK'
]

class ProductionOpenAIREProcessor:
    """Production OpenAIRE processor for complete coverage"""

    def __init__(self, output_dir: str = None):
        """Initialize production processor"""

        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            self.output_dir = Path("F:/OSINT_DATA/openaire_production_comprehensive")

        self.output_dir.mkdir(parents=True, exist_ok=True)

        print(f"OpenAIRE Production Processor")
        print(f"Output directory: {self.output_dir}")
        print(f"Target countries: {len(ALL_TARGET_COUNTRIES)}")
        print()

        # Initialize client with production settings
        self.client = OpenAIREClient(output_dir=str(self.output_dir))
        self.client.min_request_interval = 0.8  # Production rate limiting

        # Initialize database
        self.db_path = self.output_dir / "openaire_production.db"
        self.init_database()

        # Processing state
        self.checkpoint_file = self.output_dir / "production_checkpoint.json"
        self.load_checkpoint()

    def init_database(self):
        """Initialize production database"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Enhanced schema for production
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS country_overview (
                country_code TEXT PRIMARY KEY,
                country_name TEXT,
                total_research_products INTEGER,
                recent_publications INTEGER,
                processing_start TEXT,
                processing_end TEXT,
                processing_status TEXT,
                batches_completed INTEGER,
                total_collaborations INTEGER,
                china_collaborations INTEGER,
                error_count INTEGER
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS research_products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                country_code TEXT,
                title TEXT,
                date_accepted TEXT,
                result_type TEXT,
                doi TEXT,
                processing_batch INTEGER,
                has_collaboration BOOLEAN,
                raw_data TEXT,
                UNIQUE(country_code, doi, title)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS collaborations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                primary_country TEXT,
                partner_countries TEXT,
                title TEXT,
                date_accepted TEXT,
                result_type TEXT,
                doi TEXT,
                num_countries INTEGER,
                organizations TEXT,
                is_china_collaboration BOOLEAN,
                processing_batch INTEGER,
                UNIQUE(primary_country, doi, title)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS processing_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                country_code TEXT,
                batch_number INTEGER,
                start_time TEXT,
                end_time TEXT,
                records_processed INTEGER,
                collaborations_found INTEGER,
                china_collaborations INTEGER,
                status TEXT,
                error_message TEXT,
                processing_time_seconds REAL
            )
        ''')

        # Create indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_collaborations_china ON collaborations(is_china_collaboration)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_collaborations_country ON collaborations(primary_country)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_research_country ON research_products(country_code)')

        conn.commit()
        conn.close()

    def load_checkpoint(self):
        """Load production checkpoint"""

        if self.checkpoint_file.exists():
            with open(self.checkpoint_file, 'r') as f:
                self.checkpoint = json.load(f)
            print(f"Resuming from checkpoint:")
            print(f"  Completed countries: {len(self.checkpoint.get('completed_countries', []))}")
            print(f"  Current country: {self.checkpoint.get('current_country', 'None')}")
            print(f"  Total processed: {self.checkpoint.get('total_processed', 0):,}")
            print(f"  China collaborations: {self.checkpoint.get('china_collaborations', 0)}")
            print()
        else:
            self.checkpoint = {
                'completed_countries': [],
                'current_country': None,
                'current_batch': 0,
                'total_processed': 0,
                'total_collaborations': 0,
                'china_collaborations': 0,
                'start_time': datetime.now().isoformat(),
                'estimated_completion': None,
                'countries_with_china_collabs': []
            }

    def save_checkpoint(self):
        """Save production checkpoint"""

        with open(self.checkpoint_file, 'w') as f:
            json.dump(self.checkpoint, f, indent=2, default=str)

    def process_country_complete(self, country_code: str) -> Dict:
        """Process ALL research data for a country (no limits)"""

        logger.info(f"Starting COMPLETE processing for {country_code}")
        country_name = ALL_TARGET_COUNTRIES[country_code]

        processing_start = datetime.now()

        # Get country overview
        try:
            overview = self.client.get_country_research_overview(country_code)
            total_products = overview['total_research_products']

            if total_products == 0:
                logger.info(f"{country_code} has no research products, skipping")
                return {'status': 'skipped', 'reason': 'no_research_products'}

            logger.info(f"{country_code} has {total_products:,} total research products")

        except Exception as e:
            logger.error(f"Error getting overview for {country_code}: {e}")
            return {'status': 'error', 'error': str(e)}

        # Calculate processing strategy
        batch_size = 1000
        estimated_batches = (total_products + batch_size - 1) // batch_size

        logger.info(f"Will process {estimated_batches:,} batches of {batch_size} products each")

        # Initialize country in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO country_overview
            (country_code, country_name, total_research_products, recent_publications,
             processing_start, processing_status, batches_completed,
             total_collaborations, china_collaborations, error_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            country_code, country_name, total_products, overview.get('recent_publications', 0),
            processing_start.isoformat(), 'processing', 0, 0, 0, 0
        ))

        conn.commit()
        conn.close()

        # Process all batches
        total_collaborations = 0
        china_collaborations = 0
        error_count = 0
        completed_batches = 0

        for batch_num in range(1, estimated_batches + 1):
            batch_start = datetime.now()

            if batch_num % 100 == 0:  # Progress update every 100 batches
                logger.info(f"Processing batch {batch_num:,}/{estimated_batches:,} for {country_code}")

            try:
                # Calculate page range for this batch
                start_page = ((batch_num - 1) * batch_size // 50) + 1
                end_page = (batch_num * batch_size // 50) + 1

                batch_data = []

                # Collect data for this batch
                for page in range(start_page, end_page + 1):
                    page_data = self.client.search_research_products(
                        country=country_code,
                        size=50,
                        page=page
                    )

                    if page_data.get('response', {}).get('results', {}).get('result'):
                        results = page_data['response']['results']['result']
                        if not isinstance(results, list):
                            results = [results]
                        batch_data.extend(results)

                    # Check if we've reached the end
                    if not page_data.get('response', {}).get('results', {}).get('result'):
                        break

                    time.sleep(self.client.min_request_interval)

                # Process collaborations for this batch
                if batch_data:
                    collaborations_df = self.client.extract_collaboration_data(batch_data)

                    # Store data in database
                    self.store_research_products(country_code, batch_data, batch_num)
                    batch_collaborations = self.store_collaborations(
                        country_code, collaborations_df, batch_num
                    )

                    batch_china_collabs = len(collaborations_df[
                        collaborations_df['countries'].apply(
                            lambda x: 'CN' in x if isinstance(x, list) else False
                        )
                    ])

                    total_collaborations += batch_collaborations
                    china_collaborations += batch_china_collabs
                    completed_batches += 1

                    # Log batch completion
                    self.log_batch_completion(
                        country_code, batch_num, batch_start, datetime.now(),
                        len(batch_data), batch_collaborations, batch_china_collabs,
                        'completed'
                    )

                else:
                    # No more data, break early
                    logger.info(f"No more data at batch {batch_num} for {country_code}")
                    break

            except Exception as e:
                error_count += 1
                logger.error(f"Error processing batch {batch_num} for {country_code}: {e}")

                self.log_batch_completion(
                    country_code, batch_num, batch_start, datetime.now(),
                    0, 0, 0, f'error: {str(e)}'
                )

                # Continue processing despite errors (production resilience)
                continue

            # Update checkpoint every 50 batches
            if batch_num % 50 == 0:
                self.checkpoint['current_country'] = country_code
                self.checkpoint['current_batch'] = batch_num
                self.checkpoint['total_processed'] += len(batch_data) if batch_data else 0
                self.checkpoint['total_collaborations'] += batch_collaborations if batch_data else 0
                self.checkpoint['china_collaborations'] += batch_china_collabs if batch_data else 0
                self.save_checkpoint()

        # Mark country as completed
        processing_end = datetime.now()
        processing_time = (processing_end - processing_start).total_seconds()

        # Update database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE country_overview
            SET processing_end = ?, processing_status = ?, batches_completed = ?,
                total_collaborations = ?, china_collaborations = ?, error_count = ?
            WHERE country_code = ?
        ''', (
            processing_end.isoformat(), 'completed', completed_batches,
            total_collaborations, china_collaborations, error_count, country_code
        ))

        conn.commit()
        conn.close()

        # Update checkpoint
        if country_code not in self.checkpoint['completed_countries']:
            self.checkpoint['completed_countries'].append(country_code)

        if china_collaborations > 0 and country_code not in self.checkpoint['countries_with_china_collabs']:
            self.checkpoint['countries_with_china_collabs'].append(country_code)

        self.checkpoint['current_country'] = None
        self.checkpoint['current_batch'] = 0
        self.save_checkpoint()

        result = {
            'country': country_code,
            'status': 'completed',
            'total_products': total_products,
            'batches_processed': completed_batches,
            'total_collaborations': total_collaborations,
            'china_collaborations': china_collaborations,
            'error_count': error_count,
            'processing_time_seconds': processing_time
        }

        logger.info(f"COMPLETED {country_code}: {total_collaborations:,} total collaborations, "
                   f"{china_collaborations} with China")

        return result

    def store_research_products(self, country_code: str, batch_data: List[Dict], batch_num: int):
        """Store research products in database"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for item in batch_data:
            try:
                result = item['metadata']['oaf:entity']['oaf:result']

                title = result.get('title', {}).get('$', '')
                date = result.get('dateofacceptance', {}).get('$', '')
                result_type = result.get('resulttype', {}).get('@classid', '')

                # Extract DOI
                doi = None
                if 'pid' in result:
                    pids = result['pid'] if isinstance(result['pid'], list) else [result['pid']]
                    for pid in pids:
                        if pid.get('@classid') == 'doi':
                            doi = pid.get('$')
                            break

                # Check for collaborations
                has_collaboration = False
                if 'rels' in result and 'rel' in result['rels']:
                    has_collaboration = True

                cursor.execute('''
                    INSERT OR IGNORE INTO research_products
                    (country_code, title, date_accepted, result_type, doi,
                     processing_batch, has_collaboration, raw_data)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    country_code, title, date, result_type, doi,
                    batch_num, has_collaboration, json.dumps(item)
                ))

            except Exception as e:
                logger.debug(f"Error storing research product: {e}")
                continue

        conn.commit()
        conn.close()

    def store_collaborations(self, country_code: str, collaborations_df: pd.DataFrame, batch_num: int) -> int:
        """Store collaborations in database"""

        if collaborations_df.empty:
            return 0

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        collaborations_stored = 0

        for _, row in collaborations_df.iterrows():
            try:
                is_china = 'CN' in row['countries'] if isinstance(row['countries'], list) else False
                partner_countries = ','.join(row['countries']) if isinstance(row['countries'], list) else ''

                cursor.execute('''
                    INSERT OR IGNORE INTO collaborations
                    (primary_country, partner_countries, title, date_accepted, result_type,
                     doi, num_countries, organizations, is_china_collaboration, processing_batch)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    country_code, partner_countries, row.get('title', ''),
                    row.get('date', ''), row.get('result_type', ''), row.get('doi', ''),
                    row.get('num_countries', 0), json.dumps(row.get('organizations', [])),
                    is_china, batch_num
                ))

                collaborations_stored += 1

            except Exception as e:
                logger.debug(f"Error storing collaboration: {e}")
                continue

        conn.commit()
        conn.close()

        return collaborations_stored

    def log_batch_completion(self, country_code: str, batch_num: int, start_time: datetime,
                           end_time: datetime, records: int, collaborations: int,
                           china_collabs: int, status: str):
        """Log batch completion"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        processing_time = (end_time - start_time).total_seconds()

        cursor.execute('''
            INSERT INTO processing_log
            (country_code, batch_number, start_time, end_time, records_processed,
             collaborations_found, china_collaborations, status, error_message, processing_time_seconds)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            country_code, batch_num, start_time.isoformat(), end_time.isoformat(),
            records, collaborations, china_collabs,
            status if not status.startswith('error') else 'error',
            status if status.startswith('error') else None,
            processing_time
        ))

        conn.commit()
        conn.close()

def main():
    """Execute production OpenAIRE processing"""

    print("="*80)
    print("OpenAIRE Production Processor - ALL EU Countries")
    print("="*80)
    print(f"Target countries: {len(ALL_TARGET_COUNTRIES)}")
    print(f"Processing order: {len(COUNTRY_PROCESSING_ORDER)} countries prioritized")
    print(f"Output: F:/OSINT_DATA/openaire_production_comprehensive/")
    print()

    processor = ProductionOpenAIREProcessor()

    # Process countries in priority order
    for country_code in COUNTRY_PROCESSING_ORDER:
        if country_code not in ALL_TARGET_COUNTRIES:
            continue

        if country_code in processor.checkpoint['completed_countries']:
            print(f"SKIPPING {country_code} (already completed)")
            continue

        country_name = ALL_TARGET_COUNTRIES[country_code]
        print(f"PROCESSING {country_name} ({country_code})...")

        try:
            result = processor.process_country_complete(country_code)

            if result.get('status') == 'completed':
                china_count = result['china_collaborations']
                total_count = result['total_collaborations']
                print(f"  COMPLETED {country_code}: {china_count} China collaborations / {total_count:,} total")
            else:
                print(f"  FAILED {country_code}: {result}")

        except KeyboardInterrupt:
            print(f"\nProcessing interrupted by user at {country_code}")
            break
        except Exception as e:
            print(f"  ERROR {country_code}: {e}")
            logger.error(f"Error processing {country_code}: {e}")

        print()

    # Generate final comprehensive report
    print("GENERATING FINAL COMPREHENSIVE REPORT...")

    conn = sqlite3.connect(processor.db_path)

    # Summary statistics
    summary_query = '''
        SELECT
            COUNT(*) as countries_processed,
            SUM(total_collaborations) as total_collaborations,
            SUM(china_collaborations) as china_collaborations,
            SUM(total_research_products) as total_research_products
        FROM country_overview
        WHERE processing_status = 'completed'
    '''

    summary = pd.read_sql_query(summary_query, conn)

    # Top countries by China collaborations
    china_by_country = pd.read_sql_query('''
        SELECT country_code, country_name, china_collaborations, total_collaborations
        FROM country_overview
        WHERE processing_status = 'completed' AND china_collaborations > 0
        ORDER BY china_collaborations DESC
    ''', conn)

    conn.close()

    print("\nFINAL RESULTS:")
    print("="*50)
    print(f"Countries processed: {summary.iloc[0]['countries_processed']}")
    print(f"Total research products: {summary.iloc[0]['total_research_products']:,}")
    print(f"Total collaborations: {summary.iloc[0]['total_collaborations']:,}")
    print(f"China collaborations: {summary.iloc[0]['china_collaborations']}")
    print(f"Countries with China collaborations: {len(china_by_country)}")

    if len(china_by_country) > 0:
        print(f"\nTOP COUNTRIES BY CHINA COLLABORATIONS:")
        for _, row in china_by_country.head(10).iterrows():
            print(f"  {row['country_code']}: {row['china_collaborations']} China / {row['total_collaborations']:,} total")

    print(f"\nDatabase saved to: {processor.db_path}")
    print(f"Size: {processor.db_path.stat().st_size / 1024 / 1024:.1f} MB")
    print("="*80)

if __name__ == "__main__":
    main()

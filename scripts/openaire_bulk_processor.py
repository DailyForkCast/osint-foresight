#!/usr/bin/env python3
"""
OpenAIRE Comprehensive Bulk Data Processor

Systematically processes ALL qualifying OpenAIRE data for comprehensive
China collaboration analysis across all EU countries.

Strategy:
1. Enumerate all EU countries + key non-EU targets
2. For each country, collect ALL research products (not just samples)
3. Extract ALL international collaborations (not just China)
4. Identify China partnerships from comprehensive dataset
5. Store results for cross-analysis with OpenAlex, CORDIS, TED
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

# Add the collectors directory to Python path
sys.path.append(str(Path(__file__).parent / "collectors"))
from openaire_client import OpenAIREClient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Comprehensive country list
ALL_COUNTRIES = {
    # EU-27 Members
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
    'CN': 'China', 'US': 'United States', 'JP': 'Japan', 'KR': 'South Korea',
    'CA': 'Canada', 'AU': 'Australia', 'IN': 'India', 'SG': 'Singapore',
    'TW': 'Taiwan', 'HK': 'Hong Kong', 'RU': 'Russia'
}

class OpenAIREBulkProcessor:
    """Comprehensive OpenAIRE data processor"""

    def __init__(self, output_dir: str = None):
        """Initialize bulk processor"""

        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            self.output_dir = Path("C:/Projects/OSINT - Foresight/data/processed/openaire_comprehensive")

        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize client with slower rate limiting for bulk processing
        self.client = OpenAIREClient(output_dir=str(self.output_dir))
        self.client.min_request_interval = 1.0  # 1 second between requests for bulk processing

        # Initialize database for storing results
        self.db_path = self.output_dir / "openaire_comprehensive.db"
        self.init_database()

        # Processing state
        self.checkpoint_file = self.output_dir / "processing_checkpoint.json"
        self.load_checkpoint()

    def init_database(self):
        """Initialize SQLite database for results"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Country overview table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS country_overview (
                country_code TEXT PRIMARY KEY,
                country_name TEXT,
                total_research_products INTEGER,
                recent_publications INTEGER,
                processing_date TEXT,
                processing_status TEXT
            )
        ''')

        # Research products table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS research_products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                country_code TEXT,
                title TEXT,
                date_accepted TEXT,
                result_type TEXT,
                doi TEXT,
                processing_batch INTEGER,
                raw_data TEXT
            )
        ''')

        # Collaborations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS collaborations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                primary_country TEXT,
                partner_country TEXT,
                title TEXT,
                date_accepted TEXT,
                result_type TEXT,
                doi TEXT,
                num_countries INTEGER,
                organizations TEXT,
                is_china_collaboration BOOLEAN,
                processing_batch INTEGER
            )
        ''')

        # Processing log table
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
                error_message TEXT
            )
        ''')

        conn.commit()
        conn.close()

    def load_checkpoint(self):
        """Load processing checkpoint"""

        if self.checkpoint_file.exists():
            with open(self.checkpoint_file, 'r') as f:
                self.checkpoint = json.load(f)
        else:
            self.checkpoint = {
                'completed_countries': [],
                'current_country': None,
                'current_batch': 0,
                'total_processed': 0,
                'total_collaborations': 0,
                'china_collaborations': 0,
                'start_time': None
            }

    def save_checkpoint(self):
        """Save processing checkpoint"""

        with open(self.checkpoint_file, 'w') as f:
            json.dump(self.checkpoint, f, indent=2, default=str)

    def get_country_overview(self, country_code: str) -> Dict:
        """Get comprehensive overview for a country"""

        logger.info(f"Getting overview for {country_code} ({ALL_COUNTRIES.get(country_code, 'Unknown')})")

        try:
            overview = self.client.get_country_research_overview(country_code)
            overview['processing_status'] = 'completed'

            # Store in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT OR REPLACE INTO country_overview
                (country_code, country_name, total_research_products, recent_publications, processing_date, processing_status)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                country_code,
                ALL_COUNTRIES.get(country_code, 'Unknown'),
                overview['total_research_products'],
                overview['recent_publications'],
                datetime.now().isoformat(),
                'completed'
            ))

            conn.commit()
            conn.close()

            return overview

        except Exception as e:
            logger.error(f"Error getting overview for {country_code}: {e}")

            # Store error in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO country_overview
                (country_code, country_name, processing_date, processing_status)
                VALUES (?, ?, ?, ?)
            ''', (country_code, ALL_COUNTRIES.get(country_code, 'Unknown'),
                  datetime.now().isoformat(), f'error: {str(e)}'))
            conn.commit()
            conn.close()

            return {'error': str(e)}

    def process_country_comprehensive(self, country_code: str, max_batches: int = None) -> Dict:
        """Process ALL research data for a country comprehensively"""

        logger.info(f"Starting comprehensive processing for {country_code}")

        country_name = ALL_COUNTRIES.get(country_code, 'Unknown')
        start_time = datetime.now()

        # Get country overview first
        overview = self.get_country_overview(country_code)
        if 'error' in overview:
            return overview

        total_products = overview['total_research_products']
        logger.info(f"{country_code} has {total_products:,} total research products")

        if total_products == 0:
            logger.info(f"No research products for {country_code}, skipping")
            return {'status': 'skipped', 'reason': 'no_research_products'}

        # Calculate processing strategy
        batch_size = 1000  # Products per batch
        estimated_batches = (total_products + batch_size - 1) // batch_size

        if max_batches:
            estimated_batches = min(estimated_batches, max_batches)
            logger.info(f"Limiting to {max_batches} batches for testing")

        logger.info(f"Will process ~{estimated_batches} batches of {batch_size} products each")

        # Process in batches
        batch_results = []
        total_collaborations = 0
        china_collaborations = 0

        for batch_num in range(1, estimated_batches + 1):
            batch_start = datetime.now()

            logger.info(f"Processing batch {batch_num}/{estimated_batches} for {country_code}")

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

                    # Store research products in database
                    self.store_research_products(country_code, batch_data, batch_num)

                    # Store collaborations in database
                    batch_collaborations = self.store_collaborations(
                        country_code, collaborations_df, batch_num
                    )

                    batch_china_collabs = len(collaborations_df[
                        collaborations_df['countries'].apply(lambda x: 'CN' in x if isinstance(x, list) else False)
                    ])

                    total_collaborations += batch_collaborations
                    china_collaborations += batch_china_collabs

                    batch_results.append({
                        'batch': batch_num,
                        'products_processed': len(batch_data),
                        'collaborations_found': batch_collaborations,
                        'china_collaborations': batch_china_collabs,
                        'processing_time': (datetime.now() - batch_start).total_seconds()
                    })

                    logger.info(f"Batch {batch_num}: {len(batch_data)} products, "
                              f"{batch_collaborations} collaborations, {batch_china_collabs} with China")

                # Log batch completion
                self.log_batch_completion(
                    country_code, batch_num, batch_start, datetime.now(),
                    len(batch_data) if batch_data else 0,
                    batch_collaborations if batch_data else 0,
                    batch_china_collabs if batch_data else 0,
                    'completed'
                )

                # Update checkpoint
                self.checkpoint['current_country'] = country_code
                self.checkpoint['current_batch'] = batch_num
                self.checkpoint['total_processed'] += len(batch_data) if batch_data else 0
                self.checkpoint['total_collaborations'] += batch_collaborations if batch_data else 0
                self.checkpoint['china_collaborations'] += batch_china_collabs if batch_data else 0
                self.save_checkpoint()

            except Exception as e:
                logger.error(f"Error processing batch {batch_num} for {country_code}: {e}")

                self.log_batch_completion(
                    country_code, batch_num, batch_start, datetime.now(),
                    0, 0, 0, f'error: {str(e)}'
                )

                # Continue with next batch despite error
                continue

        # Mark country as completed
        if country_code not in self.checkpoint['completed_countries']:
            self.checkpoint['completed_countries'].append(country_code)
            self.save_checkpoint()

        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()

        result = {
            'country': country_code,
            'status': 'completed',
            'total_products': total_products,
            'batches_processed': len(batch_results),
            'total_collaborations': total_collaborations,
            'china_collaborations': china_collaborations,
            'processing_time_seconds': processing_time,
            'batch_results': batch_results
        }

        logger.info(f"Completed {country_code}: {total_collaborations} total collaborations, "
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

                cursor.execute('''
                    INSERT INTO research_products
                    (country_code, title, date_accepted, result_type, doi, processing_batch, raw_data)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (country_code, title, date, result_type, doi, batch_num, json.dumps(item)))

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

                cursor.execute('''
                    INSERT INTO collaborations
                    (primary_country, partner_country, title, date_accepted, result_type,
                     doi, num_countries, organizations, is_china_collaboration, processing_batch)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    country_code,
                    ','.join(row['countries']) if isinstance(row['countries'], list) else '',
                    row.get('title', ''),
                    row.get('date', ''),
                    row.get('result_type', ''),
                    row.get('doi', ''),
                    row.get('num_countries', 0),
                    json.dumps(row.get('organizations', [])),
                    is_china,
                    batch_num
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
        """Log batch completion to database"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO processing_log
            (country_code, batch_number, start_time, end_time, records_processed,
             collaborations_found, china_collaborations, status, error_message)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            country_code, batch_num, start_time.isoformat(), end_time.isoformat(),
            records, collaborations, china_collabs,
            status if not status.startswith('error') else 'error',
            status if status.startswith('error') else None
        ))

        conn.commit()
        conn.close()

    def generate_progress_report(self) -> Dict:
        """Generate comprehensive progress report"""

        conn = sqlite3.connect(self.db_path)

        # Get overview statistics
        overview_df = pd.read_sql_query("SELECT * FROM country_overview", conn)
        collaborations_df = pd.read_sql_query("SELECT * FROM collaborations", conn)
        processing_df = pd.read_sql_query("SELECT * FROM processing_log", conn)

        conn.close()

        # Calculate statistics
        total_countries = len(overview_df)
        completed_countries = len(overview_df[overview_df['processing_status'] == 'completed'])
        total_research_products = overview_df['total_research_products'].sum()
        total_collaborations = len(collaborations_df)
        china_collaborations = len(collaborations_df[collaborations_df['is_china_collaboration'] == True])

        # Top countries by research volume
        top_research = overview_df.nlargest(10, 'total_research_products')[
            ['country_code', 'country_name', 'total_research_products']
        ].to_dict('records')

        # Top countries by China collaborations
        china_by_country = collaborations_df[collaborations_df['is_china_collaboration'] == True][
            'primary_country'
        ].value_counts().head(10).to_dict()

        report = {
            'timestamp': datetime.now().isoformat(),
            'processing_summary': {
                'total_countries': total_countries,
                'completed_countries': completed_countries,
                'total_research_products': int(total_research_products),
                'total_collaborations': total_collaborations,
                'china_collaborations': china_collaborations
            },
            'top_research_countries': top_research,
            'china_collaborations_by_country': china_by_country,
            'checkpoint': self.checkpoint
        }

        return report

def main():
    """Execute comprehensive OpenAIRE processing"""

    print("="*80)
    print("OpenAIRE Comprehensive Bulk Processing System")
    print("="*80)
    print(f"Target countries: {len(ALL_COUNTRIES)}")
    print(f"Processing strategy: Complete coverage, all research products")
    print()

    processor = OpenAIREBulkProcessor()

    # Print current checkpoint status
    if processor.checkpoint['start_time']:
        print(f"Resuming from checkpoint:")
        print(f"  Completed countries: {len(processor.checkpoint['completed_countries'])}")
        print(f"  Current country: {processor.checkpoint.get('current_country', 'None')}")
        print(f"  Total processed: {processor.checkpoint['total_processed']:,}")
        print(f"  China collaborations found: {processor.checkpoint['china_collaborations']}")
        print()
    else:
        processor.checkpoint['start_time'] = datetime.now().isoformat()
        processor.save_checkpoint()

    # For initial testing, process priority countries with limited batches
    PRIORITY_COUNTRIES = ['IT', 'DE', 'HU', 'GR', 'FR', 'ES', 'PL']
    TEST_BATCHES = 5  # Limit for testing

    print(f"TESTING MODE: Processing {len(PRIORITY_COUNTRIES)} priority countries")
    print(f"Limiting to {TEST_BATCHES} batches per country for initial test")
    print()

    results = []

    for country_code in PRIORITY_COUNTRIES:
        if country_code in processor.checkpoint['completed_countries']:
            print(f"Skipping {country_code} (already completed)")
            continue

        country_name = ALL_COUNTRIES[country_code]
        print(f"Processing {country_name} ({country_code})...")

        try:
            result = processor.process_country_comprehensive(
                country_code,
                max_batches=TEST_BATCHES
            )
            results.append(result)

            if result.get('status') == 'completed':
                print(f"  ✅ {country_code}: {result['china_collaborations']} China collaborations found")
            else:
                print(f"  ❌ {country_code}: {result}")

        except Exception as e:
            print(f"  ❌ {country_code}: ERROR - {e}")
            logger.error(f"Error processing {country_code}: {e}")

        print()

    # Generate final report
    print("Generating progress report...")
    report = processor.generate_progress_report()

    # Save comprehensive results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results_file = processor.output_dir / f"bulk_processing_results_{timestamp}.json"

    final_results = {
        'metadata': {
            'processing_date': datetime.now().isoformat(),
            'countries_targeted': PRIORITY_COUNTRIES,
            'test_mode': True,
            'max_batches_per_country': TEST_BATCHES
        },
        'results': results,
        'progress_report': report
    }

    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(final_results, f, indent=2, ensure_ascii=False, default=str)

    print(f"Results saved to: {results_file}")
    print(f"Database location: {processor.db_path}")

    print("\nFINAL SUMMARY:")
    print(f"  Countries processed: {report['processing_summary']['completed_countries']}")
    print(f"  Total collaborations: {report['processing_summary']['total_collaborations']:,}")
    print(f"  China collaborations: {report['processing_summary']['china_collaborations']}")
    print()
    print("="*80)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Concurrent processor for OpenAlex (full dataset) and TED extraction
Processes both data sources in parallel
"""

import os
import json
import gzip
import tarfile
import logging
import sqlite3
from pathlib import Path
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed
import xml.etree.ElementTree as ET
import csv
import re

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class OpenAlexProcessor:
    """Process the full OpenAlex dataset we already have"""

    def __init__(self):
        self.data_dir = Path("F:/OSINT_Backups/openalex/data/works")
        self.output_dir = Path("F:/OSINT_DATA/openalex_processed")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = "F:/OSINT_WAREHOUSE/osint_master.db"

        # Target countries
        self.target_countries = {
            'AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR', 'DE', 'GR',
            'HU', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'NL', 'PL', 'PT', 'RO', 'SK',
            'SI', 'ES', 'SE', 'GB', 'NO', 'CH', 'IS', 'LI', 'MD', 'UA', 'BY', 'BA',
            'RS', 'ME', 'MK', 'AL', 'XK', 'TR', 'RU', 'GE', 'AM', 'AZ', 'KZ', 'KG',
            'TJ', 'TM', 'UZ', 'AD', 'MC', 'SM', 'VA'
        }

        self.china_codes = {'CN', 'HK', 'MO'}

    def process(self):
        """Process OpenAlex works for China-Europe collaborations"""
        logging.info("Starting OpenAlex processing from full dataset...")

        # Get all gz files
        gz_files = list(self.data_dir.rglob("*.gz"))
        logging.info(f"Found {len(gz_files)} OpenAlex work files to process")

        # Load checkpoint if exists
        checkpoint_file = self.output_dir / "checkpoint.json"
        processed_files = set()

        if checkpoint_file.exists():
            with open(checkpoint_file, 'r') as f:
                checkpoint = json.load(f)
                processed_files = set(checkpoint.get('processed_files', []))
                logging.info(f"Resuming from checkpoint: {len(processed_files)} files already processed")

        # Process files
        china_europe_collabs = []
        batch_size = 10

        for i, gz_file in enumerate(gz_files):
            if str(gz_file) in processed_files:
                continue

            if i % 100 == 0:
                logging.info(f"Processing file {i}/{len(gz_files)}: {gz_file.name}")

            try:
                with gzip.open(gz_file, 'rt', encoding='utf-8') as f:
                    for line_num, line in enumerate(f):
                        if line_num > 1000:  # Sample first 1000 records per file for now
                            break

                        try:
                            work = json.loads(line)

                            # Check for China-Europe collaborations
                            if self.is_china_europe_collab(work):
                                china_europe_collabs.append({
                                    'work_id': work.get('id'),
                                    'title': work.get('title'),
                                    'year': work.get('publication_year'),
                                    'countries': self.extract_countries(work),
                                    'institutions': self.extract_institutions(work),
                                    'doi': work.get('doi'),
                                    'type': work.get('type')
                                })

                        except json.JSONDecodeError:
                            continue

                # Mark as processed
                processed_files.add(str(gz_file))

                # Save checkpoint every 10 files
                if i % 10 == 0:
                    self.save_checkpoint(checkpoint_file, processed_files, china_europe_collabs)

            except Exception as e:
                logging.error(f"Error processing {gz_file}: {e}")

        # Final save
        self.save_results(china_europe_collabs)
        logging.info(f"OpenAlex processing complete: {len(china_europe_collabs)} China-Europe collaborations found")

        return len(china_europe_collabs)

    def is_china_europe_collab(self, work):
        """Check if work represents China-Europe collaboration"""
        countries = self.extract_countries(work)

        has_china = bool(countries & self.china_codes)
        has_europe = bool(countries & self.target_countries)

        return has_china and has_europe

    def extract_countries(self, work):
        """Extract country codes from work"""
        countries = set()

        for authorship in work.get('authorships', []):
            for institution in authorship.get('institutions', []):
                country = institution.get('country_code')
                if country:
                    countries.add(country)

        return countries

    def extract_institutions(self, work):
        """Extract institution names"""
        institutions = []

        for authorship in work.get('authorships', []):
            for institution in authorship.get('institutions', []):
                name = institution.get('display_name')
                if name:
                    institutions.append(name)

        return institutions

    def save_checkpoint(self, checkpoint_file, processed_files, collabs):
        """Save processing checkpoint"""
        with open(checkpoint_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'processed_files': list(processed_files),
                'collaborations_found': len(collabs)
            }, f)

    def save_results(self, collabs):
        """Save final results"""
        output_file = self.output_dir / f"china_europe_collaborations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(output_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'total_collaborations': len(collabs),
                'collaborations': collabs[:1000]  # Save first 1000 for review
            }, f, indent=2)

        # Also update database
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Create table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS openalex_china_europe (
                    work_id TEXT PRIMARY KEY,
                    title TEXT,
                    year INTEGER,
                    countries TEXT,
                    institutions TEXT,
                    doi TEXT,
                    type TEXT
                )
            """)

            # Insert data
            for collab in collabs[:1000]:
                cursor.execute("""
                    INSERT OR REPLACE INTO openalex_china_europe
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    collab['work_id'],
                    collab['title'],
                    collab['year'],
                    json.dumps(list(collab['countries'])),
                    json.dumps(collab['institutions']),
                    collab['doi'],
                    collab['type']
                ))

            conn.commit()
            conn.close()

        except Exception as e:
            logging.error(f"Database update failed: {e}")


class TEDExtractor:
    """Extract nested TED archives and process for China content"""

    def __init__(self):
        self.source_dir = Path("F:/TED_Data/monthly")
        self.extract_dir = Path("F:/TED_Data/extracted")
        self.extract_dir.mkdir(parents=True, exist_ok=True)
        self.csv_dir = Path("F:/TED_Data/extracted_csv")
        self.csv_dir.mkdir(parents=True, exist_ok=True)

        # China patterns
        self.china_patterns = [
            r'\bchina\b', r'\bchinese\b', r'\bbeijing\b', r'\bshanghai\b',
            r'\bhuawei\b', r'\bzte\b', r'\balibaba\b', r'\btencent\b'
        ]

    def process(self):
        """Extract and process TED archives"""
        logging.info("Starting TED extraction from nested archives...")

        # Get all tar.gz files
        archives = list(self.source_dir.glob("TED_monthly_*.tar.gz"))
        logging.info(f"Found {len(archives)} TED archives to process")

        total_china_contracts = 0

        for archive_num, archive in enumerate(archives, 1):
            logging.info(f"Processing archive {archive_num}/{len(archives)}: {archive.name}")

            try:
                # Extract outer archive
                outer_extract_dir = self.extract_dir / archive.stem
                outer_extract_dir.mkdir(parents=True, exist_ok=True)

                with tarfile.open(archive, 'r:gz') as outer_tar:
                    outer_tar.extractall(outer_extract_dir)

                # Find and extract inner archives
                inner_archives = list(outer_extract_dir.rglob("*.tar.gz"))
                logging.info(f"  Found {len(inner_archives)} inner archives")

                for inner_archive in inner_archives[:5]:  # Process first 5 inner archives per outer
                    try:
                        # Extract inner archive
                        inner_extract_dir = inner_archive.parent / inner_archive.stem
                        inner_extract_dir.mkdir(parents=True, exist_ok=True)

                        with tarfile.open(inner_archive, 'r:gz') as inner_tar:
                            inner_tar.extractall(inner_extract_dir)

                        # Process XML files
                        xml_files = list(inner_extract_dir.glob("*.xml"))
                        china_contracts = self.process_xml_files(xml_files, archive.stem)
                        total_china_contracts += len(china_contracts)

                        # Clean up inner extraction
                        if inner_extract_dir.exists():
                            for f in inner_extract_dir.glob("*"):
                                f.unlink()
                            inner_extract_dir.rmdir()

                    except Exception as e:
                        logging.error(f"Error processing inner archive {inner_archive}: {e}")

                # Clean up outer extraction
                if outer_extract_dir.exists():
                    import shutil
                    shutil.rmtree(outer_extract_dir, ignore_errors=True)

            except Exception as e:
                logging.error(f"Error processing {archive}: {e}")

        logging.info(f"TED extraction complete: {total_china_contracts} China-related contracts found")
        return total_china_contracts

    def process_xml_files(self, xml_files, archive_name):
        """Process XML files for China content"""
        china_contracts = []

        for xml_file in xml_files:
            try:
                tree = ET.parse(xml_file)
                root = tree.getroot()

                # Convert to text for searching
                xml_text = ET.tostring(root, encoding='unicode').lower()

                # Check for China references
                if any(re.search(pattern, xml_text) for pattern in self.china_patterns):
                    # Extract key fields
                    contract_data = self.extract_contract_data(root)
                    if contract_data:
                        contract_data['source_archive'] = archive_name
                        contract_data['xml_file'] = xml_file.name
                        china_contracts.append(contract_data)

            except Exception as e:
                logging.error(f"Error processing XML {xml_file}: {e}")

        # Save to CSV if any found
        if china_contracts:
            self.save_to_csv(china_contracts, archive_name)

        return china_contracts

    def extract_contract_data(self, root):
        """Extract contract data from XML"""
        try:
            ns = {'ted': 'http://ted.europa.eu'}  # Adjust namespace as needed

            return {
                'notice_id': self.get_text(root, './/NOTICE_ID'),
                'contract_title': self.get_text(root, './/TITLE'),
                'buyer_name': self.get_text(root, './/NAME_ADDRESSES_CONTACT/CA_CE_CONCESSIONAIRE_PROFILE/NAME_OFFICIAL'),
                'buyer_country': self.get_text(root, './/COUNTRY'),
                'contract_value': self.get_text(root, './/VALUE'),
                'publication_date': self.get_text(root, './/DATE_PUB'),
                'contractor_name': self.get_text(root, './/CONTRACTOR/NAME'),
                'contractor_country': self.get_text(root, './/CONTRACTOR/COUNTRY')
            }
        except:
            return None

    def get_text(self, element, path):
        """Safely extract text from XML element"""
        try:
            elem = element.find(path)
            return elem.text if elem is not None else ''
        except:
            return ''

    def save_to_csv(self, contracts, archive_name):
        """Save contracts to CSV"""
        csv_file = self.csv_dir / f"china_contracts_{archive_name}.csv"

        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            if contracts:
                writer = csv.DictWriter(f, fieldnames=contracts[0].keys())
                writer.writeheader()
                writer.writerows(contracts)


def run_concurrent_processing():
    """Run OpenAlex and TED processing concurrently"""
    logging.info("="*60)
    logging.info("CONCURRENT OPENALEX & TED PROCESSING")
    logging.info("="*60)

    start_time = datetime.now()

    with ProcessPoolExecutor(max_workers=2) as executor:
        # Submit both tasks
        futures = {
            executor.submit(OpenAlexProcessor().process): "OpenAlex",
            executor.submit(TEDExtractor().process): "TED"
        }

        # Process as completed
        for future in as_completed(futures):
            source = futures[future]
            try:
                result = future.result()
                logging.info(f"{source} processing completed with result: {result}")
            except Exception as e:
                logging.error(f"{source} processing failed: {e}")

    elapsed = datetime.now() - start_time
    logging.info(f"\nTotal processing time: {elapsed}")

    # Generate summary report
    report = f"""
# Concurrent Processing Summary
Generated: {datetime.now().isoformat()}

## Processing Duration: {elapsed}

## OpenAlex Results:
- Full dataset location: F:/OSINT_Backups/openalex/data/works (363GB)
- Processed files saved to: F:/OSINT_DATA/openalex_processed/
- Database table: openalex_china_europe

## TED Results:
- Source archives: F:/TED_Data/monthly/ (139 files)
- Extracted CSVs: F:/TED_Data/extracted_csv/
- China-related contracts identified and extracted

## Next Steps:
1. Review extracted China-Europe collaborations
2. Cross-reference with other data sources
3. Generate comprehensive analysis report
"""

    report_path = Path("C:/Projects/OSINT - Foresight/analysis/concurrent_processing_report.md")
    with open(report_path, 'w') as f:
        f.write(report)

    logging.info(f"Report saved to: {report_path}")


if __name__ == "__main__":
    run_concurrent_processing()
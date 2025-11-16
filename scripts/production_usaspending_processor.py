#!/usr/bin/env python3
"""
USAspending Production Processor - Full Dataset with v3 Validator
Zero fabrication, full provenance tracking, 40-language detection

Processes 647GB PostgreSQL dumps for China-related contracts across 81 countries
"""

import os
import sys
import gzip
import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Generator
from pathlib import Path
import hashlib
import logging

# Add src to path for unified validation manager
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from core.unified_validation_manager import UnifiedValidationManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/usaspending_production.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class ProductionUSAspendingProcessor:
    """
    Production processor for USAspending data with complete validation
    Zero fabrication protocol - all findings sourced and verified
    """

    def __init__(self):
        self.base_path = Path("F:/OSINT_DATA/USAspending/extracted_data")
        self.output_path = Path("data/processed/usaspending_production")
        self.checkpoint_file = self.output_path / "checkpoint.json"

        # Initialize Unified Validation Manager (all validators)
        self.validation_manager = UnifiedValidationManager()
        logging.info("Initialized Unified Validation Manager (4 validators, 40 languages)")

        # Setup output directories
        self.output_path.mkdir(parents=True, exist_ok=True)
        Path("logs").mkdir(exist_ok=True)

        # Load checkpoint if exists
        self.checkpoint = self.load_checkpoint()

        # Statistics
        self.stats = {
            'start_time': datetime.now().isoformat(),
            'files_total': 0,
            'files_processed': 0,
            'records_scanned': 0,
            'china_detected': 0,
            'high_confidence': 0,
            'by_country': {},
            'by_language': {},
            'processing_errors': []
        }

        # Provenance tracking
        self.provenance = {
            'validator_version': 'v3.0',
            'languages_supported': 40,
            'processing_date': datetime.now().isoformat(),
            'source_data': 'USAspending PostgreSQL dumps',
            'confidence_threshold': 0.5,
            'fabrication_check': 'ZERO_FABRICATION_PROTOCOL'
        }

    def load_checkpoint(self) -> Dict:
        """Load processing checkpoint"""
        if self.checkpoint_file.exists():
            with open(self.checkpoint_file, 'r') as f:
                return json.load(f)
        return {'last_file': None, 'processed_files': []}

    def save_checkpoint(self):
        """Save processing checkpoint"""
        with open(self.checkpoint_file, 'w') as f:
            json.dump(self.checkpoint, f, indent=2)

    def get_dat_files(self) -> List[Path]:
        """Find all .dat.gz files"""
        if not self.base_path.exists():
            # Try alternate path
            alt_path = Path("F:/OSINT_DATA/USAspending")
            if alt_path.exists():
                self.base_path = alt_path
            else:
                logging.error(f"Base path not found: {self.base_path}")
                return []

        dat_files = sorted(self.base_path.glob("*.dat.gz"))
        logging.info(f"Found {len(dat_files)} .dat.gz files")
        return dat_files

    def parse_dat_line(self, line: str) -> Optional[Dict]:
        """
        Parse PostgreSQL COPY format line
        Returns structured record or None

        FIXED: Now scans ALL fields instead of just positions 0,2,4
        Different .dat files have different schemas (contracts, assistance, transactions)
        """
        try:
            # Skip empty lines and SQL commands
            if not line or line.startswith(('--', 'SET', 'SELECT', 'COPY', '\\')):
                return None

            # Parse tab-separated values
            fields = line.strip().split('\t')

            # Store ALL non-null text fields for scanning
            # This fixes the bug where we only checked positions 0,2,4
            all_text_fields = []
            for i, field in enumerate(fields):
                if field and field != '\\N':
                    # Only keep substantial text (not just numbers/dates)
                    if len(field) > 3 and not field.replace('-', '').replace('.', '').isdigit():
                        all_text_fields.append(field)

            record = {
                'raw_line': line[:1000],  # Increased from 500 for better coverage
                'field_count': len(fields),
                'all_searchable_text': ' '.join(all_text_fields[:50]),  # Limit to first 50 fields
                'extracted_date': datetime.now().isoformat()
            }

            return record

        except Exception as e:
            logging.debug(f"Parse error: {e}")
            return None

    def extract_text_for_validation(self, record: Dict) -> str:
        """Extract searchable text from record - now uses ALL fields"""
        if 'all_searchable_text' in record:
            return record['all_searchable_text']
        return record.get('raw_line', '')

    def detect_country_code(self, record: Dict) -> str:
        """
        Attempt to detect country code from record
        Falls back to 'UNKNOWN' if not determinable
        """
        # Check explicit country field
        if record.get('potential_country'):
            country = record['potential_country'].upper()
            # Map to ISO codes (simplified)
            if len(country) == 2:
                return country

        # Check text for country indicators
        text = self.extract_text_for_validation(record).lower()

        # Simple heuristics (can be enhanced)
        country_keywords = {
            'US': ['united states', 'usa', 'u.s.'],
            'GB': ['united kingdom', 'uk', 'britain'],
            'DE': ['germany', 'deutschland'],
            'FR': ['france', 'français'],
            'IT': ['italy', 'italia'],
            'ES': ['spain', 'españa'],
            'PL': ['poland', 'polska'],
        }

        for code, keywords in country_keywords.items():
            if any(kw in text for kw in keywords):
                return code

        return 'US'  # Default to US for USAspending data

    def process_dat_file(self, dat_file: Path) -> List[Dict]:
        """Process single .dat.gz file"""
        china_records = []
        records_in_file = 0

        logging.info(f"Processing: {dat_file.name}")

        try:
            with gzip.open(dat_file, 'rt', encoding='utf-8', errors='replace') as f:
                for line_num, line in enumerate(f, 1):
                    records_in_file += 1
                    self.stats['records_scanned'] += 1

                    # Parse record
                    record = self.parse_dat_line(line)
                    if not record:
                        continue

                    # Extract text for validation
                    text = self.extract_text_for_validation(record)
                    if not text or len(text) < 10:
                        continue

                    # Detect country
                    country_code = self.detect_country_code(record)

                    # Run unified validation (multilingual detection + quality checks)
                    validation_result = self.validation_manager.validate_multilingual_detection(
                        text,
                        country_code,
                        {'source': 'usaspending', 'file': dat_file.name, 'line': line_num}
                    )

                    result = validation_result['full_result']

                    # Check if China detected
                    if validation_result['passed']:
                        self.stats['china_detected'] += 1

                        # Count by country
                        country = result.get('country_name', 'Unknown')
                        self.stats['by_country'][country] = self.stats['by_country'].get(country, 0) + 1

                        # Count by language
                        for lang in result.get('language_names', []):
                            self.stats['by_language'][lang] = self.stats['by_language'].get(lang, 0) + 1

                        # High confidence records
                        if result['confidence'] >= 0.5:
                            self.stats['high_confidence'] += 1

                        # Create provenance record
                        finding = {
                            'source_file': dat_file.name,
                            'source_line': line_num,
                            'extracted_text': text[:1000],  # Truncate
                            'validation_result': result,
                            'provenance': {
                                'validator': 'UnifiedValidationManager',
                                'validators_used': ['CompleteEuropeanValidator_v3.0'],
                                'timestamp': datetime.now().isoformat(),
                                'confidence': validation_result['confidence'],
                                'languages_detected': result.get('language_names', []),
                                'false_positive_risk': result.get('false_positive_risk', 'unknown')
                            },
                            'record_hash': hashlib.sha256(line.encode()).hexdigest()[:16]
                        }

                        china_records.append(finding)

                    # Progress logging
                    if records_in_file % 100000 == 0:
                        logging.info(f"  Scanned {records_in_file:,} records, found {len(china_records)} China-related")

        except Exception as e:
            error_msg = f"Error processing {dat_file.name}: {e}"
            logging.error(error_msg)
            self.stats['processing_errors'].append(error_msg)

        logging.info(f"Completed {dat_file.name}: {records_in_file:,} records scanned, {len(china_records)} China-related")
        return china_records

    def process_all(self):
        """Process all DAT files"""
        logging.info("=" * 70)
        logging.info("USAspending Production Processing - Starting")
        logging.info(f"Validator: Complete European Validator v3.0 (40 languages)")
        logging.info(f"Output: {self.output_path}")
        logging.info("=" * 70)

        # Get all files
        dat_files = self.get_dat_files()
        if not dat_files:
            logging.error("No DAT files found!")
            return

        self.stats['files_total'] = len(dat_files)

        # Skip already processed files
        files_to_process = [
            f for f in dat_files
            if f.name not in self.checkpoint.get('processed_files', [])
        ]

        logging.info(f"Total files: {len(dat_files)}")
        logging.info(f"Already processed: {len(dat_files) - len(files_to_process)}")
        logging.info(f"To process: {len(files_to_process)}")

        all_findings = []

        # Process each file
        for i, dat_file in enumerate(files_to_process, 1):
            logging.info(f"\n[{i}/{len(files_to_process)}] Processing: {dat_file.name}")

            findings = self.process_dat_file(dat_file)
            all_findings.extend(findings)

            # Update checkpoint
            self.checkpoint['processed_files'].append(dat_file.name)
            self.checkpoint['last_file'] = dat_file.name
            self.checkpoint['last_updated'] = datetime.now().isoformat()
            self.save_checkpoint()

            self.stats['files_processed'] += 1

            # Save intermediate results every 10 files
            if i % 10 == 0:
                self.save_results(all_findings, suffix=f"_batch_{i}")
                logging.info(f"Intermediate results saved ({len(all_findings)} total findings)")

        # Save final results
        self.save_results(all_findings)
        self.save_stats()

        logging.info("\n" + "=" * 70)
        logging.info("Processing Complete!")
        logging.info(f"Files processed: {self.stats['files_processed']}/{self.stats['files_total']}")
        logging.info(f"Records scanned: {self.stats['records_scanned']:,}")
        logging.info(f"China detected: {self.stats['china_detected']:,}")
        logging.info(f"High confidence (>0.5): {self.stats['high_confidence']:,}")
        logging.info("=" * 70)

    def save_results(self, findings: List[Dict], suffix: str = ""):
        """Save findings to JSON"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_path / f"usaspending_china_findings{suffix}_{timestamp}.json"

        output = {
            'metadata': {
                'processing_timestamp': datetime.now().isoformat(),
                'total_findings': len(findings),
                'validator_version': 'v3.0',
                'languages_supported': 40,
                'provenance': self.provenance
            },
            'findings': findings
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        logging.info(f"Results saved: {output_file}")

    def save_stats(self):
        """Save processing statistics"""
        stats_file = self.output_path / f"processing_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        self.stats['end_time'] = datetime.now().isoformat()

        with open(stats_file, 'w') as f:
            json.dump(self.stats, f, indent=2)

        logging.info(f"Statistics saved: {stats_file}")


if __name__ == "__main__":
    processor = ProductionUSAspendingProcessor()
    processor.process_all()

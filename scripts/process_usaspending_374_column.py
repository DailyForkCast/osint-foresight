#!/usr/bin/env python3
"""
USAspending 374-Column Format Processor

Specialized processor for 374-column USAspending format (files 5877, 5878).
This format represents 100GB of data (46% of total dataset).

Key differences from 206-column format:
- Different field positions
- No sub-awardee fields detected
- Focus on prime recipient detection

Based on field analysis:
  [69]  recipient_name
  [72]  recipient_parent_name
  [41]  recipient_location_country_name
  [42]  recipient_location_country_code
  [54]  pop_country (place of performance)

Input: F:/OSINT_DATA/USAspending/extracted_data/5877.dat.gz, 5878.dat.gz
Output: F:/OSINT_WAREHOUSE/osint_master.db
"""

import gzip
import sqlite3
import json
import re
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from collections import defaultdict

@dataclass
class DetectionResult:
    """Result of China entity detection."""
    is_detected: bool
    detection_type: str  # 'country', 'entity_name', 'parent'
    field_index: int
    field_name: str
    matched_value: str
    confidence: str  # 'HIGH', 'MEDIUM', 'LOW'
    rationale: str

@dataclass
class Transaction374:
    """USAspending transaction record (374-column format)."""
    transaction_id: str
    piid: str
    recipient_name: str
    recipient_parent_name: str
    recipient_country_name: str
    recipient_country_code: str
    pop_country: str
    federal_action_obligation: float
    action_date: str
    fiscal_year: str
    awarding_agency: str
    naics_code: str
    naics_description: str
    recipient_uei: str
    recipient_duns: str
    # No sub-awardee fields in this format

class USAspending374Processor:
    """
    Processor for 374-column USAspending format.

    Focuses on prime recipient detection (no sub-awardee data).
    """

    # 374-column schema mapping (confirmed through analysis)
    SCHEMA = {
        0: 'transaction_id',
        8: 'piid',
        69: 'recipient_name',
        72: 'recipient_parent_name',
        41: 'recipient_location_country_name',
        42: 'recipient_location_country_code',
        54: 'pop_country',
        24: 'federal_action_obligation',
        9: 'action_date',
        13: 'fiscal_year',
        # Agency fields appear to be in different positions
        # NAICS fields to be identified
        70: 'recipient_uei',  # To be confirmed
        71: 'recipient_duns',  # To be confirmed
    }

    # China detection patterns
    CHINA_COUNTRIES = [
        'china', 'hong kong', 'prc', "people's republic of china",
        'peoples republic of china', 'mainland china', 'chn'
    ]

    CHINA_ENTITIES = [
        # Telecommunications
        'huawei', 'zte', 'china telecom', 'china mobile', 'china unicom',
        # Surveillance
        'hikvision', 'dahua', 'zhejiang dahua',
        # Technology
        'lenovo', 'xiaomi', 'oppo electronics', 'vivo mobile', 'oneplus technology', 'realme',
        'alibaba', 'tencent', 'baidu', 'bytedance', 'tiktok',
        # Drones
        'dji', 'autel robotics',
        # Aviation
        'comac', 'avic',
        # Electronics
        'boe technology', 'tcl corporation', 'hisense', 'haier',
        # Semiconductors
        'smic', 'semiconductor manufacturing international',
        # Shipping
        'cosco', 'china ocean shipping',
        # Energy
        'cnooc', 'sinopec', 'petrochina',
        # Nuclear
        'cgnpc', 'china general nuclear',
        # Rail
        'china railway rolling stock', 'crrc corporation',
        # Automotive
        'nio inc', 'byd company', 'geely',
    ]

    # Known false positives to exclude
    FALSE_POSITIVES = [
        'boeing',  # Don't match 'boe' in 'boeing'
        'comboed',  # Don't match 'boe' in 'comboed'
        'senior',  # Don't match 'nio' in 'senior'
        'union',  # Don't match 'nio' in 'union'
        'junior',  # Don't match 'nio' in 'junior'
        'opportunities',  # Don't match 'oppo'
        'opportunity',
        'opposite',
        'opposition',
        'corrections',  # Don't match 'crrc'
        'crrctns',
        # Geographic false positives (historical regions)
        'indochina',  # Historical region, not PRC
        'indo-china',
        'french indochina',
        # Company name false positives - COSCO Fire Protection (US company)
        'cosco fire protection',  # US fire protection company (owned by German Minimax), not COSCO Shipping
        'cosco fire',
        'american cosco',  # American COSCO (not China COSCO Shipping)
        # European companies/joint ventures with Chinese-related names
        'sino european',  # European joint ventures
        'sino-german',
        'euro-china',
        'sino-french',
        'sino-italian',
        # Language service companies (translation/interpreting, not China-based)
        'chinese language services',  # e.g., ACTA CHINESE LANGUAGE SERVICES LLC
        'chinese language service',
        'chinese translation services',
        'chinese translation service',
        'chinese interpreting services',
        'chinese interpreting service',
        'chinese interpreter services',
        'chinese interpretation services',
    ]

    def __init__(self):
        self.output_dir = Path("data/processed/usaspending_374_production")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")

        # Statistics
        self.stats = {
            'files_processed': 0,
            'total_records': 0,
            'china_detected': 0,
            'by_detection_type': defaultdict(int),
            'by_confidence': defaultdict(int),
            'total_value': 0.0,
        }

    def process_file(self, file_path: Path, batch_size: int = 5000,
                     max_records: Optional[int] = None) -> int:
        """
        Process a single 374-column .dat.gz file with streaming database saves.

        Args:
            file_path: Path to .dat.gz file
            batch_size: Number of detections to accumulate before saving (default: 5000)
            max_records: Maximum records to process (for testing)

        Returns:
            Total number of detections found
        """

        print(f"\n{'='*80}")
        print(f"Processing 374-column format: {file_path.name}")
        print(f"Size: {file_path.stat().st_size / (1024**3):.1f} GB")
        print(f"{'='*80}\n")

        detections_batch = []
        total_detections = 0
        record_count = 0

        with gzip.open(file_path, 'rt', encoding='utf-8', errors='replace') as f:
            for line_num, line in enumerate(f, 1):
                # Progress indicator
                if line_num % 100000 == 0:
                    print(f"  Processed {line_num:,} lines, "
                          f"detected {total_detections:,} China-related (batch: {len(detections_batch)})")

                # Parse record
                fields = line.strip().split('\t')

                # Validate 374-column format
                if len(fields) < 100:  # Allow some flexibility but filter obvious bad records
                    continue

                # Extract transaction
                try:
                    transaction = self._extract_transaction(fields)
                except Exception as e:
                    continue  # Skip malformed records

                # Detect China entities
                detection_results = self._detect_china_entity(transaction, fields)

                if detection_results:
                    # Build detection record
                    detection_record = self._build_detection_record(
                        transaction, detection_results, fields
                    )
                    detections_batch.append(detection_record)

                    # Update statistics
                    self.stats['china_detected'] += 1
                    self.stats['total_value'] += transaction.federal_action_obligation

                    for result in detection_results:
                        self.stats['by_detection_type'][result.detection_type] += 1
                        self.stats['by_confidence'][result.confidence] += 1

                    # Save batch to database when it reaches batch_size
                    if len(detections_batch) >= batch_size:
                        self._save_to_database(detections_batch)
                        total_detections += len(detections_batch)
                        detections_batch = []  # Clear batch

                record_count += 1
                self.stats['total_records'] += 1

                # Stop if reached max
                if max_records and record_count >= max_records:
                    print(f"\n  Reached max records limit: {max_records:,}")
                    break

        # Save any remaining detections
        if detections_batch:
            self._save_to_database(detections_batch)
            total_detections += len(detections_batch)

        print(f"\n  Completed: {record_count:,} records processed")
        print(f"  Detected: {total_detections:,} China-related transactions")

        return total_detections

    def _extract_transaction(self, fields: List[str]) -> Transaction374:
        """Extract transaction from 374-column fields."""

        def get_field(idx: int) -> str:
            """Get field value, handling NULL."""
            if idx < len(fields):
                val = fields[idx]
                return '' if val in ['\\N', '', 'NULL'] else val
            return ''

        def get_float(idx: int) -> float:
            """Get float field, handling NULL."""
            val = get_field(idx)
            try:
                return float(val) if val else 0.0
            except:
                return 0.0

        return Transaction374(
            transaction_id=get_field(0),
            piid=get_field(8),
            recipient_name=get_field(69),
            recipient_parent_name=get_field(72),
            recipient_country_name=get_field(41),
            recipient_country_code=get_field(42),
            pop_country=get_field(54),
            federal_action_obligation=get_float(24),
            action_date=get_field(9),
            fiscal_year=get_field(13),
            awarding_agency=get_field(76),  # Estimated position
            naics_code=get_field(25),  # Estimated position
            naics_description=get_field(26),  # Estimated position
            recipient_uei=get_field(70),  # Estimated position
            recipient_duns=get_field(71),  # Estimated position
        )

    def _detect_china_entity(self, transaction: Transaction374,
                             fields: List[str]) -> List[DetectionResult]:
        """
        Multi-field China entity detection for 374-column format.

        Focus on prime recipient (no sub-awardee data available).
        """

        results = []

        # 1. COUNTRY CHECK (highest confidence)
        # Check recipient country name
        if self._is_china_country(transaction.recipient_country_name):
            results.append(DetectionResult(
                is_detected=True,
                detection_type='country',
                field_index=41,
                field_name='recipient_location_country_name',
                matched_value=transaction.recipient_country_name,
                confidence='HIGH',
                rationale=f'Recipient located in {transaction.recipient_country_name}'
            ))

        # Check recipient country code
        if self._is_china_country(transaction.recipient_country_code):
            results.append(DetectionResult(
                is_detected=True,
                detection_type='country',
                field_index=42,
                field_name='recipient_location_country_code',
                matched_value=transaction.recipient_country_code,
                confidence='HIGH',
                rationale=f'Recipient country code: {transaction.recipient_country_code}'
            ))

        # Check place of performance country
        if self._is_china_country(transaction.pop_country):
            results.append(DetectionResult(
                is_detected=True,
                detection_type='country',
                field_index=54,
                field_name='pop_country',
                matched_value=transaction.pop_country,
                confidence='HIGH',
                rationale=f'Work performed in {transaction.pop_country}'
            ))

        # 2. ENTITY NAME CHECK (high confidence)
        # Check recipient name
        entity_match = self._find_china_entity(transaction.recipient_name)
        if entity_match:
            results.append(DetectionResult(
                is_detected=True,
                detection_type='entity_name',
                field_index=69,
                field_name='recipient_name',
                matched_value=entity_match,
                confidence='HIGH',
                rationale=f'Known Chinese entity: {entity_match} in recipient name'
            ))

        # Check recipient parent name
        entity_match = self._find_china_entity(transaction.recipient_parent_name)
        if entity_match:
            results.append(DetectionResult(
                is_detected=True,
                detection_type='parent',
                field_index=72,
                field_name='recipient_parent_name',
                matched_value=entity_match,
                confidence='HIGH',
                rationale=f'Chinese parent company: {entity_match}'
            ))

        return results

    def _is_china_country(self, country: str) -> bool:
        """Check if country field indicates China (PRC only, NOT Taiwan/ROC)."""
        if not country:
            return False
        country_lower = country.lower()

        # CRITICAL: Taiwan (ROC) is NOT China (PRC)
        # Exclude Taiwan before checking for China
        if 'taiwan' in country_lower or country_lower == 'twn':
            return False

        return any(china_country in country_lower
                   for china_country in self.CHINA_COUNTRIES)

    def _find_china_entity(self, text: str) -> Optional[str]:
        """
        Find known Chinese entity in text.

        Uses word boundary matching for short entities to avoid false positives.
        """
        if not text:
            return None
        text_lower = text.lower()

        # Check for false positives first
        for false_positive in self.FALSE_POSITIVES:
            if false_positive in text_lower:
                return None

        # Check for Chinese entities
        for entity in self.CHINA_ENTITIES:
            if entity in text_lower:
                # Apply word boundary to ALL entities (not just short ones)
                # This prevents false positives like "MACHINARY" matching "CHINA"
                pattern = r'\b' + re.escape(entity) + r'\b'
                if re.search(pattern, text_lower):
                    return entity
        return None

    def _build_detection_record(self, transaction: Transaction374,
                                 results: List[DetectionResult],
                                 fields: List[str]) -> Dict:
        """Build comprehensive detection record."""

        return {
            # Transaction identifiers
            'transaction_id': transaction.transaction_id,
            'piid': transaction.piid,
            'recipient_uei': transaction.recipient_uei,
            'recipient_duns': transaction.recipient_duns,

            # Entity information
            'recipient_name': transaction.recipient_name,
            'recipient_parent_name': transaction.recipient_parent_name,
            'recipient_country_name': transaction.recipient_country_name,
            'recipient_country_code': transaction.recipient_country_code,
            'pop_country': transaction.pop_country,

            # Financial
            'federal_action_obligation': transaction.federal_action_obligation,

            # Agency and classification
            'awarding_agency': transaction.awarding_agency,
            'naics_code': transaction.naics_code,
            'naics_description': transaction.naics_description,

            # Dates
            'action_date': transaction.action_date,
            'fiscal_year': transaction.fiscal_year,

            # Detection metadata
            'detection_count': len(results),
            'detection_types': [r.detection_type for r in results],
            'highest_confidence': self._get_highest_confidence(results),
            'detection_details': [
                {
                    'type': r.detection_type,
                    'field_index': r.field_index,
                    'field_name': r.field_name,
                    'matched_value': r.matched_value,
                    'confidence': r.confidence,
                    'rationale': r.rationale,
                }
                for r in results
            ],

            # Processing metadata
            'processed_date': datetime.now().isoformat(),
            'format': '374-column',
        }

    def _get_highest_confidence(self, results: List[DetectionResult]) -> str:
        """Get highest confidence level from results."""
        if not results:
            return 'NONE'

        confidences = [r.confidence for r in results]
        if 'HIGH' in confidences:
            return 'HIGH'
        elif 'MEDIUM' in confidences:
            return 'MEDIUM'
        else:
            return 'LOW'

    def save_results(self, detections: List[Dict], file_name: str):
        """Save detection results."""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save JSON
        output_file = self.output_dir / f"{file_name}_{timestamp}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'extraction_date': timestamp,
                'file_processed': file_name,
                'format': '374-column',
                'total_detections': len(detections),
                'statistics': dict(self.stats),
                'detections': detections
            }, f, indent=2)

        print(f"\nSaved {len(detections):,} detections to: {output_file}")

        # Save to database
        self._save_to_database(detections)

    def _save_to_database(self, detections: List[Dict]):
        """Save detections to master database."""

        if not self.db_path.exists():
            print(f"Warning: Database not found: {self.db_path}")
            return

        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        # Create table if not exists
        cur.execute('''
            CREATE TABLE IF NOT EXISTS usaspending_china_374 (
                transaction_id TEXT PRIMARY KEY,
                piid TEXT,
                recipient_uei TEXT,
                recipient_duns TEXT,
                recipient_name TEXT,
                recipient_parent_name TEXT,
                recipient_country_name TEXT,
                recipient_country_code TEXT,
                pop_country TEXT,
                federal_action_obligation REAL,
                awarding_agency TEXT,
                naics_code TEXT,
                naics_description TEXT,
                action_date TEXT,
                fiscal_year TEXT,
                detection_count INTEGER,
                detection_types TEXT,
                highest_confidence TEXT,
                detection_details TEXT,
                processed_date TEXT,
                format TEXT
            )
        ''')

        # Create indexes
        cur.execute('CREATE INDEX IF NOT EXISTS idx_374_recipient ON usaspending_china_374(recipient_name)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_374_country ON usaspending_china_374(recipient_country_name)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_374_confidence ON usaspending_china_374(highest_confidence)')

        # Insert records
        for detection in detections:
            cur.execute('''
                INSERT OR REPLACE INTO usaspending_china_374 VALUES
                (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                detection['transaction_id'],
                detection['piid'],
                detection['recipient_uei'],
                detection['recipient_duns'],
                detection['recipient_name'],
                detection['recipient_parent_name'],
                detection['recipient_country_name'],
                detection['recipient_country_code'],
                detection['pop_country'],
                detection['federal_action_obligation'],
                detection['awarding_agency'],
                detection['naics_code'],
                detection['naics_description'],
                detection['action_date'],
                detection['fiscal_year'],
                detection['detection_count'],
                json.dumps(detection['detection_types']),
                detection['highest_confidence'],
                json.dumps(detection['detection_details']),
                detection['processed_date'],
                detection['format'],
            ))

        conn.commit()
        conn.close()

        print(f"Saved {len(detections):,} records to database table: usaspending_china_374")

    def print_summary(self):
        """Print processing summary."""

        print(f"\n{'='*80}")
        print("374-COLUMN PROCESSING SUMMARY")
        print(f"{'='*80}")
        print(f"Files processed: {self.stats['files_processed']}")
        print(f"Total records: {self.stats['total_records']:,}")
        print(f"China detections: {self.stats['china_detected']:,} "
              f"({self.stats['china_detected']/max(self.stats['total_records'], 1)*100:.2f}%)")
        print(f"Total value: ${self.stats['total_value']:,.2f}")

        print(f"\nDetection Types:")
        for det_type, count in sorted(self.stats['by_detection_type'].items()):
            print(f"  {det_type}: {count:,}")

        print(f"\nConfidence Levels:")
        for confidence, count in sorted(self.stats['by_confidence'].items()):
            print(f"  {confidence}: {count:,}")

        print(f"{'='*80}\n")


def main():
    """Test on sample from 374-column file."""

    print("USAspending 374-Column Format Processor")
    print("="*80)

    processor = USAspending374Processor()

    # Test on 374-column file with limited records
    test_file = Path("F:/OSINT_DATA/USAspending/extracted_data/5877.dat.gz")

    if not test_file.exists():
        print(f"ERROR: Test file not found: {test_file}")
        return

    print(f"\nTEST MODE: Processing first 100,000 records")
    print(f"File: {test_file.name}")
    print(f"Expected format: 374 columns\n")

    # Process (streaming mode - saves to database automatically)
    total_detections = processor.process_file(test_file, max_records=100000)

    # Summary
    processor.stats['files_processed'] = 1
    processor.print_summary()

    # Note about detections
    if total_detections > 0:
        print(f"\nTest complete: {total_detections} detections saved to database")
        print("Run monitor_374_progress.py to view detection details")
    else:
        print("\nNo detections found in test sample.")
        print("This may indicate:")
        print("  1. Schema mapping needs adjustment")
        print("  2. No China-related transactions in first 100K records")
        print("  3. Field positions are different than expected")


if __name__ == '__main__':
    main()

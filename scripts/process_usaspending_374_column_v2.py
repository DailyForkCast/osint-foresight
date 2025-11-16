#!/usr/bin/env python3
"""
USAspending 374-Column Format Processor v2.0 (October 2025)

CRITICAL CHANGES FROM v1.0:
- Integrates entity_classification_validator.py for country code verification
- Prevents $1.65B false positive error (PRI-DJI entities)
- Implements Taiwan/PRC separation policy
- Adds mandatory validation for high-value entities (>$10M)
- Uses country code as PRIMARY detection method

This version addresses the critical false positive error discovered in the data audit
where US companies with "DJI" in their names were incorrectly classified as Chinese.

Key differences from v1.0:
- Country code verification is now MANDATORY
- False positives (PRI-DJI entities) are explicitly excluded
- Taiwan (TW), Hong Kong (HK), and Macao (MO) classified separately from PRC (CN)
- High-value entities flagged for manual verification
- Confidence levels aligned with Taiwan/PRC Classification Policy

Input: F:/OSINT_DATA/USAspending/extracted_data/5877.dat.gz, 5878.dat.gz
Output: F:/OSINT_WAREHOUSE/osint_master.db (table: usaspending_china_374_v2)
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

# Import the corrected validator
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.entity_classification_validator import (
    EntityClassificationValidator,
    EntityOrigin,
    ConfidenceLevel,
    validate_chinese_entity_detection
)

@dataclass
class DetectionResult:
    """Result of China entity detection (v2.0 with enhanced validation)."""
    is_detected: bool
    detection_type: str  # 'country_verified', 'entity_name_verified', 'needs_verification'
    field_index: int
    field_name: str
    matched_value: str
    confidence: str  # 'VERIFIED', 'HIGH', 'MEDIUM', 'LOW', 'NEEDS_REVIEW'
    rationale: str
    entity_origin: str  # 'CN', 'TW', 'HK', 'MO', 'OTHER', 'UNKNOWN'
    validation_warnings: str  # Warnings from validator

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

class USAspending374ProcessorV2:
    """
    Processor for 374-column USAspending format v2.0.

    Implements corrected detection algorithm with mandatory country code verification.
    Prevents false positives and implements Taiwan/PRC separation policy.
    """

    # 374-column schema mapping
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
        70: 'recipient_uei',
        71: 'recipient_duns',
    }

    def __init__(self):
        self.output_dir = Path("data/processed/usaspending_374_production_v2")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")

        # Initialize the corrected validator
        self.validator = EntityClassificationValidator()

        # Statistics (enhanced for v2.0)
        self.stats = {
            'files_processed': 0,
            'total_records': 0,
            'prc_detected': 0,  # PRC (CN) only
            'taiwan_detected': 0,  # Taiwan (TW) separate
            'hong_kong_detected': 0,  # Hong Kong SAR (HK)
            'macao_detected': 0,  # Macao SAR (MO)
            'needs_verification': 0,  # Flagged for manual review
            'false_positives_excluded': 0,  # Known false positives (PRI-DJI, etc.)
            'high_value_flagged': 0,  # >$10M requiring manual verification
            'by_detection_type': defaultdict(int),
            'by_confidence': defaultdict(int),
            'by_origin': defaultdict(int),
            'total_value_prc': 0.0,
            'total_value_taiwan': 0.0,
            'total_value_hong_kong': 0.0,
        }

    def process_file(self, file_path: Path, batch_size: int = 5000,
                     max_records: Optional[int] = None) -> int:
        """
        Process a single 374-column .dat.gz file with corrected detection algorithm.

        Args:
            file_path: Path to .dat.gz file
            batch_size: Number of detections to accumulate before saving (default: 5000)
            max_records: Maximum records to process (for testing)

        Returns:
            Total number of detections found
        """

        print(f"\n{'='*80}")
        print(f"Processing 374-column format v2.0: {file_path.name}")
        print(f"Size: {file_path.stat().st_size / (1024**3):.1f} GB")
        print(f"Using corrected detection algorithm with country code verification")
        print(f"{'='*80}\n")

        detections_batch = []
        total_detections = 0
        record_count = 0

        with gzip.open(file_path, 'rt', encoding='utf-8', errors='replace') as f:
            for line_num, line in enumerate(f, 1):
                # Progress indicator
                if line_num % 100000 == 0:
                    print(f"  Processed {line_num:,} lines, "
                          f"detected {total_detections:,} entities "
                          f"(PRC: {self.stats['prc_detected']}, TW: {self.stats['taiwan_detected']}, "
                          f"HK: {self.stats['hong_kong_detected']}, batch: {len(detections_batch)})")

                # Parse record
                fields = line.strip().split('\t')

                # Validate 374-column format
                if len(fields) < 100:
                    continue

                # Extract transaction
                try:
                    transaction = self._extract_transaction(fields)
                except Exception as e:
                    continue

                # CORRECTED DETECTION: Use validator with country code verification
                detection_results = self._detect_entity_validated(transaction, fields)

                if detection_results:
                    # Build detection record
                    detection_record = self._build_detection_record(
                        transaction, detection_results, fields
                    )
                    detections_batch.append(detection_record)

                    # Update statistics by origin
                    for result in detection_results:
                        if result.entity_origin == 'CN':
                            self.stats['prc_detected'] += 1
                            self.stats['total_value_prc'] += transaction.federal_action_obligation
                        elif result.entity_origin == 'TW':
                            self.stats['taiwan_detected'] += 1
                            self.stats['total_value_taiwan'] += transaction.federal_action_obligation
                        elif result.entity_origin == 'HK':
                            self.stats['hong_kong_detected'] += 1
                            self.stats['total_value_hong_kong'] += transaction.federal_action_obligation
                        elif result.entity_origin == 'MO':
                            self.stats['macao_detected'] += 1
                        elif result.entity_origin == 'UNKNOWN':
                            self.stats['needs_verification'] += 1

                        self.stats['by_detection_type'][result.detection_type] += 1
                        self.stats['by_confidence'][result.confidence] += 1
                        self.stats['by_origin'][result.entity_origin] += 1

                    # Save batch to database
                    if len(detections_batch) >= batch_size:
                        self._save_to_database(detections_batch)
                        total_detections += len(detections_batch)
                        detections_batch = []

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
        print(f"  Detected: {total_detections:,} entities")
        print(f"  - PRC (CN): {self.stats['prc_detected']:,} (${self.stats['total_value_prc']:,.0f})")
        print(f"  - Taiwan (TW): {self.stats['taiwan_detected']:,} (${self.stats['total_value_taiwan']:,.0f})")
        print(f"  - Hong Kong SAR (HK): {self.stats['hong_kong_detected']:,} (${self.stats['total_value_hong_kong']:,.0f})")
        print(f"  - Needs Verification: {self.stats['needs_verification']:,}")
        print(f"  - False Positives Excluded: {self.stats['false_positives_excluded']:,}")

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
            awarding_agency=get_field(76),
            naics_code=get_field(25),
            naics_description=get_field(26),
            recipient_uei=get_field(70),
            recipient_duns=get_field(71),
        )

    def _detect_entity_validated(self, transaction: Transaction374,
                                   fields: List[str]) -> List[DetectionResult]:
        """
        CORRECTED: Multi-field entity detection with mandatory country code verification.

        Uses entity_classification_validator.py to prevent false positives.
        Implements Taiwan/PRC separation policy.
        """

        results = []

        # Validate recipient using corrected algorithm
        recipient_classification = self.validator.classify_entity(
            entity_name=transaction.recipient_name,
            country_code=transaction.recipient_country_code,
            value=transaction.federal_action_obligation
        )

        # Only include if PRC, Taiwan, Hong Kong, or Macao (exclude OTHER)
        if recipient_classification.origin in [
            EntityOrigin.PRC,
            EntityOrigin.TAIWAN,
            EntityOrigin.HONG_KONG,
            EntityOrigin.MACAO,
            EntityOrigin.UNKNOWN  # Include unknowns for manual verification
        ]:
            # Map confidence level
            confidence_map = {
                ConfidenceLevel.VERIFIED: 'VERIFIED',
                ConfidenceLevel.HIGH: 'HIGH',
                ConfidenceLevel.MEDIUM: 'MEDIUM',
                ConfidenceLevel.LOW: 'LOW',
                ConfidenceLevel.NEEDS_REVIEW: 'NEEDS_REVIEW',
            }

            results.append(DetectionResult(
                is_detected=True,
                detection_type='country_verified',
                field_index=69,
                field_name='recipient_name',
                matched_value=transaction.recipient_name,
                confidence=confidence_map[recipient_classification.confidence],
                rationale=recipient_classification.reasoning,
                entity_origin=recipient_classification.origin.value,
                validation_warnings='; '.join(recipient_classification.warnings) if recipient_classification.warnings else 'None'
            ))

            # Track false positives excluded
            if 'false positive' in recipient_classification.reasoning.lower():
                self.stats['false_positives_excluded'] += 1

            # Track high-value entities flagged for verification
            if recipient_classification.verification_required:
                self.stats['high_value_flagged'] += 1

        # Also check parent company if available
        if transaction.recipient_parent_name and transaction.recipient_parent_name != transaction.recipient_name:
            parent_classification = self.validator.classify_entity(
                entity_name=transaction.recipient_parent_name,
                country_code=transaction.recipient_country_code,  # Use same country code
                value=transaction.federal_action_obligation
            )

            if parent_classification.origin in [
                EntityOrigin.PRC,
                EntityOrigin.TAIWAN,
                EntityOrigin.HONG_KONG,
                EntityOrigin.MACAO,
                EntityOrigin.UNKNOWN
            ]:
                confidence_map = {
                    ConfidenceLevel.VERIFIED: 'VERIFIED',
                    ConfidenceLevel.HIGH: 'HIGH',
                    ConfidenceLevel.MEDIUM: 'MEDIUM',
                    ConfidenceLevel.LOW: 'LOW',
                    ConfidenceLevel.NEEDS_REVIEW: 'NEEDS_REVIEW',
                }

                results.append(DetectionResult(
                    is_detected=True,
                    detection_type='parent_verified',
                    field_index=72,
                    field_name='recipient_parent_name',
                    matched_value=transaction.recipient_parent_name,
                    confidence=confidence_map[parent_classification.confidence],
                    rationale=parent_classification.reasoning,
                    entity_origin=parent_classification.origin.value,
                    validation_warnings='; '.join(parent_classification.warnings) if parent_classification.warnings else 'None'
                ))

        return results

    def _build_detection_record(self, transaction: Transaction374,
                                 results: List[DetectionResult],
                                 fields: List[str]) -> Dict:
        """Build comprehensive detection record with v2.0 enhancements."""

        # Get primary origin (from first result)
        primary_origin = results[0].entity_origin if results else 'UNKNOWN'
        primary_confidence = results[0].confidence if results else 'UNKNOWN'
        validation_warnings = results[0].validation_warnings if results else 'None'

        return {
            # Transaction identifiers
            'transaction_id': transaction.transaction_id,
            'piid': transaction.piid,

            # Entity information
            'recipient_name': transaction.recipient_name,
            'recipient_parent_name': transaction.recipient_parent_name,
            'recipient_uei': transaction.recipient_uei,
            'recipient_duns': transaction.recipient_duns,

            # Geographic classification (v2.0: Separate PRC/TW/HK/MO)
            'recipient_country_name': transaction.recipient_country_name,
            'recipient_country_code': transaction.recipient_country_code,
            'entity_country_of_origin': primary_origin,  # NEW: CN, TW, HK, MO, UNKNOWN
            'pop_country': transaction.pop_country,

            # Financial
            'federal_action_obligation': transaction.federal_action_obligation,
            'action_date': transaction.action_date,
            'fiscal_year': transaction.fiscal_year,

            # Agency and classification
            'awarding_agency': transaction.awarding_agency,
            'naics_code': transaction.naics_code,
            'naics_description': transaction.naics_description,

            # Detection metadata (v2.0: Enhanced)
            'detection_method': ', '.join([r.detection_type for r in results]),
            'matched_fields': ', '.join([r.field_name for r in results]),
            'matched_values': ', '.join([r.matched_value for r in results]),
            'confidence_level': primary_confidence,
            'detection_rationale': results[0].rationale if results else '',
            'validation_warnings': validation_warnings,  # NEW: Warnings from validator

            # Processing metadata
            'processed_date': datetime.now().isoformat(),
            'processor_version': '2.0',
            'taiwan_prc_policy_compliant': True,  # NEW: Policy compliance flag
        }

    def _save_to_database(self, detections: List[Dict]):
        """Save detection batch to database with v2.0 schema and retry logic."""
        import time

        if not detections:
            return

        # Retry logic for database locks
        max_retries = 5
        for retry in range(max_retries):
            try:
                conn = sqlite3.connect(self.db_path, timeout=60)
                cursor = conn.cursor()

                # Create table with v2.0 schema (includes entity_country_of_origin)
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS usaspending_china_374_v2 (
                        transaction_id TEXT,
                        piid TEXT,
                        recipient_name TEXT,
                        recipient_parent_name TEXT,
                        recipient_uei TEXT,
                        recipient_duns TEXT,
                        recipient_country_name TEXT,
                        recipient_country_code TEXT,
                        entity_country_of_origin TEXT,
                        pop_country TEXT,
                        federal_action_obligation REAL,
                        action_date TEXT,
                        fiscal_year TEXT,
                        awarding_agency TEXT,
                        naics_code TEXT,
                        naics_description TEXT,
                        detection_method TEXT,
                        matched_fields TEXT,
                        matched_values TEXT,
                        confidence_level TEXT,
                        detection_rationale TEXT,
                        validation_warnings TEXT,
                        processed_date TEXT,
                        processor_version TEXT,
                        taiwan_prc_policy_compliant INTEGER,
                        PRIMARY KEY (transaction_id)
                    )
                ''')

                # Insert detections
                for detection in detections:
                    cursor.execute('''
                        INSERT OR REPLACE INTO usaspending_china_374_v2
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        detection['transaction_id'],
                        detection['piid'],
                        detection['recipient_name'],
                        detection['recipient_parent_name'],
                        detection['recipient_uei'],
                        detection['recipient_duns'],
                        detection['recipient_country_name'],
                        detection['recipient_country_code'],
                        detection['entity_country_of_origin'],
                        detection['pop_country'],
                        detection['federal_action_obligation'],
                        detection['action_date'],
                        detection['fiscal_year'],
                        detection['awarding_agency'],
                        detection['naics_code'],
                        detection['naics_description'],
                        detection['detection_method'],
                        detection['matched_fields'],
                        detection['matched_values'],
                        detection['confidence_level'],
                        detection['detection_rationale'],
                        detection['validation_warnings'],
                        detection['processed_date'],
                        detection['processor_version'],
                        1 if detection['taiwan_prc_policy_compliant'] else 0,
                    ))

                conn.commit()
                conn.close()

                print(f"    Saved {len(detections)} detections to database")
                return  # Success - exit retry loop

            except sqlite3.OperationalError as e:
                if 'locked' in str(e).lower():
                    if retry < max_retries - 1:
                        print(f"    Database locked, retry {retry+1}/{max_retries} in 10 seconds...")
                        time.sleep(10)
                    else:
                        print(f"    ERROR: Database still locked after {max_retries} retries")
                        raise
                else:
                    # Other operational error, don't retry
                    raise

    def print_final_stats(self):
        """Print comprehensive final statistics."""

        print(f"\n{'='*80}")
        print(f"PROCESSING COMPLETE - STATISTICS v2.0")
        print(f"{'='*80}\n")

        print(f"Files Processed: {self.stats['files_processed']}")
        print(f"Total Records Scanned: {self.stats['total_records']:,}\n")

        print(f"GEOGRAPHIC CLASSIFICATION (Taiwan/PRC Policy v1.0):")
        print(f"  PRC (mainland CN): {self.stats['prc_detected']:,} (${self.stats['total_value_prc']:,.0f})")
        print(f"  Taiwan (TW): {self.stats['taiwan_detected']:,} (${self.stats['total_value_taiwan']:,.0f})")
        print(f"  Hong Kong SAR (HK): {self.stats['hong_kong_detected']:,} (${self.stats['total_value_hong_kong']:,.0f})")
        print(f"  Macao SAR (MO): {self.stats['macao_detected']:,}")
        print(f"  Needs Verification: {self.stats['needs_verification']:,}\n")

        print(f"QUALITY ASSURANCE:")
        print(f"  False Positives Excluded: {self.stats['false_positives_excluded']:,}")
        print(f"  High-Value Flagged (>$10M): {self.stats['high_value_flagged']:,}\n")

        print(f"BY DETECTION TYPE:")
        for det_type, count in sorted(self.stats['by_detection_type'].items()):
            print(f"  {det_type}: {count:,}")

        print(f"\nBY CONFIDENCE:")
        for conf, count in sorted(self.stats['by_confidence'].items()):
            print(f"  {conf}: {count:,}")

        print(f"\nBY ORIGIN:")
        for origin, count in sorted(self.stats['by_origin'].items()):
            print(f"  {origin}: {count:,}")


def main():
    """Main processing function."""

    processor = USAspending374ProcessorV2()

    # Process 374-column files
    data_dir = Path("F:/OSINT_DATA/USAspending/extracted_data")
    files_374 = [
        data_dir / "5877.dat.gz",
        data_dir / "5878.dat.gz",
    ]

    for file_path in files_374:
        if file_path.exists():
            processor.process_file(file_path)
            processor.stats['files_processed'] += 1
        else:
            print(f"WARNING: File not found: {file_path}")

    processor.print_final_stats()

    print(f"\n{'='*80}")
    print(f"DATA SAVED TO: F:/OSINT_WAREHOUSE/osint_master.db")
    print(f"TABLE: usaspending_china_374_v2")
    print(f"POLICY COMPLIANT: Taiwan/PRC Classification Policy v1.0")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()

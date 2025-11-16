#!/usr/bin/env python3
"""
TED Chinese Entity Rebuild with Null Protocols
Created: October 20, 2025
Purpose: Rebuild Chinese entity table with proper validation and comprehensive null handling
"""

import sqlite3
import json
import time
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from ted_validation_rules import TEDEntityValidator

DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"
CHECKPOINT_FILE = "data/ted_rebuild_checkpoint.json"
BATCH_SIZE = 10000


class TEDEntityRebuilder:
    """
    Rebuilds TED Chinese entity table with comprehensive null protocols and validation.
    """

    def __init__(self, min_confidence: float = 70.0, dry_run: bool = False):
        """
        Initialize rebuilder with validation parameters.

        Args:
            min_confidence: Minimum confidence score to classify as Chinese entity (default 70%)
            dry_run: If True, perform analysis only without database updates
        """
        self.min_confidence = min_confidence
        self.dry_run = dry_run
        self.validator = TEDEntityValidator()
        self.conn = None
        self.cursor = None

        # Statistics tracking
        self.stats = {
            'start_time': datetime.now().isoformat(),
            'contracts_processed': 0,
            'entities_detected': 0,
            'entities_validated': 0,
            'entities_added': 0,
            'european_exclusions': 0,
            'low_confidence_exclusions': 0,
            'null_fields_recovered': 0,
            'batches_completed': 0,
            'checkpoint_saves': 0,
            'quality_checks_passed': 0,
            'quality_checks_failed': 0
        }

        # Entity tracking (entity_name -> entity_data)
        self.entities = {}

    # ========================================================================
    # NULL PROTOCOL FUNCTIONS
    # ========================================================================

    def get_contractor_name_with_null_protocol(self, row: Dict) -> Optional[str]:
        """
        Get contractor name with null protocol.

        For TED, we only have contractor_name - no fallback needed.

        Returns:
            Contractor name or None if NULL
        """
        # Only contractor_name exists in TED table
        if row['contractor_name'] and str(row['contractor_name']).strip():
            return str(row['contractor_name']).strip()

        # No valid name found
        return None

    def get_country_code_with_null_protocol(self, row: Dict) -> Optional[str]:
        """
        Get country code with null protocol - check available country fields.

        Cascading fallback chain:
        1. contractor_country (2-char ISO)
        2. iso_country (2-char ISO)
        3. Extract from nuts_code (first 2 chars)

        Returns:
            Country code (uppercase) or None if all fields are NULL
        """
        # Try contractor_country first
        if row['contractor_country']:
            code = str(row['contractor_country']).strip().upper()
            if len(code) == 2:
                return code

        # Try iso_country as fallback
        if row['iso_country']:
            code = str(row['iso_country']).strip().upper()
            if len(code) == 2:
                self.stats['null_fields_recovered'] += 1
                return code

        # Extract from NUTS code (first 2 chars)
        if row['nuts_code']:
            nuts = str(row['nuts_code']).strip()
            if len(nuts) >= 2:
                self.stats['null_fields_recovered'] += 1
                return nuts[:2].upper()

        # No valid country code found
        return None

    def get_address_with_null_protocol(self, row: Dict) -> Optional[str]:
        """
        Get address with null protocol - check available address fields.

        Cascading fallback chain:
        1. contractor_address
        2. Combine: contractor_city + contractor_postal_code + place_of_performance

        Returns:
            Address string or None if all fields are NULL
        """
        # Try contractor_address first
        if row['contractor_address'] and str(row['contractor_address']).strip():
            return str(row['contractor_address']).strip()

        # Combine available location data as fallback
        location_parts = []
        if row['contractor_city'] and str(row['contractor_city']).strip():
            location_parts.append(str(row['contractor_city']).strip())
        if row['contractor_postal_code'] and str(row['contractor_postal_code']).strip():
            location_parts.append(str(row['contractor_postal_code']).strip())
        if row['place_of_performance'] and str(row['place_of_performance']).strip():
            location_parts.append(str(row['place_of_performance']).strip())

        if location_parts:
            self.stats['null_fields_recovered'] += 1
            return ', '.join(location_parts)

        # No valid address found
        return None

    # ========================================================================
    # DATABASE OPERATIONS
    # ========================================================================

    def connect_database(self):
        """Connect to database."""
        self.conn = sqlite3.connect(DB_PATH, timeout=60)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def close_database(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()

    # ========================================================================
    # CHECKPOINT/RESUME FUNCTIONALITY
    # ========================================================================

    def load_checkpoint(self) -> Dict:
        """
        Load checkpoint from file if exists.

        Returns:
            Checkpoint data or empty dict if no checkpoint
        """
        try:
            with open(CHECKPOINT_FILE, 'r', encoding='utf-8') as f:
                checkpoint = json.load(f)
                print(f"Checkpoint loaded: {checkpoint['contracts_processed']:,} contracts already processed")
                return checkpoint
        except FileNotFoundError:
            return {}
        except Exception as e:
            print(f"Warning: Could not load checkpoint - {e}")
            return {}

    def save_checkpoint(self, offset: int):
        """
        Save checkpoint to file.

        Args:
            offset: Current offset in contract processing
        """
        checkpoint = {
            'timestamp': datetime.now().isoformat(),
            'contracts_processed': offset,
            'entities_detected': self.stats['entities_detected'],
            'entities_added': self.stats['entities_added'],
            'batches_completed': self.stats['batches_completed']
        }

        try:
            with open(CHECKPOINT_FILE, 'w', encoding='utf-8') as f:
                json.dump(checkpoint, f, indent=2)
            self.stats['checkpoint_saves'] += 1
        except Exception as e:
            print(f"Warning: Could not save checkpoint - {e}")

    # ========================================================================
    # QUALITY GATES
    # ========================================================================

    def quality_gate_check(self, sample_size: int = 100) -> bool:
        """
        Quality gate: Check precision of entities added so far.

        Args:
            sample_size: Number of entities to sample for validation

        Returns:
            True if quality gate passed, False otherwise
        """
        print()
        print("="*80)
        print(f"QUALITY GATE CHECK - {self.stats['contracts_processed']:,} contracts processed")
        print("="*80)

        if len(self.entities) == 0:
            print("No entities detected yet, skipping quality gate")
            return True

        # Sample entities
        entity_names = list(self.entities.keys())
        sample = entity_names[:min(sample_size, len(entity_names))]

        print(f"Sampling {len(sample)} entities for validation...")

        passed = 0
        european = 0
        low_confidence = 0

        for entity_name in sample:
            entity_data = self.entities[entity_name]

            # Validate
            result = self.validator.validate_entity(
                entity_name=entity_name,
                contractor_country=entity_data.get('country_code'),
                contractor_address=entity_data.get('address'),
                min_confidence=self.min_confidence
            )

            if result['is_european_exclusion']:
                european += 1
            elif result['confidence_score'] < self.min_confidence:
                low_confidence += 1
            elif result['validation_passed']:
                passed += 1

        # Calculate precision
        precision = (passed / len(sample) * 100) if sample else 0
        european_pct = (european / len(sample) * 100) if sample else 0

        print()
        print(f"Quality Gate Results:")
        print(f"  Valid entities: {passed} ({precision:.1f}%)")
        print(f"  European exclusions: {european} ({european_pct:.1f}%)")
        print(f"  Low confidence: {low_confidence}")
        print()

        # Quality gate thresholds
        if precision < 70.0:
            print(f"QUALITY GATE FAILED: Precision {precision:.1f}% below 70% threshold")
            print("Recommendation: Review detection logic")
            self.stats['quality_checks_failed'] += 1
            return False

        if european_pct > 5.0:
            print(f"QUALITY GATE WARNING: {european_pct:.1f}% European entities detected")
            print("Recommendation: Strengthen European exclusion logic")

        print(f"QUALITY GATE PASSED: Precision {precision:.1f}% meets threshold")
        self.stats['quality_checks_passed'] += 1
        print()

        return True

    # ========================================================================
    # MAIN PROCESSING LOGIC
    # ========================================================================

    def process_batch(self, offset: int, limit: int) -> int:
        """
        Process a batch of contracts.

        Args:
            offset: Starting offset in contract table
            limit: Number of contracts to process

        Returns:
            Number of contracts processed
        """
        # Query contracts with all relevant fields (only columns that exist in TED table)
        self.cursor.execute(f'''
            SELECT
                id,
                contractor_name,
                contractor_country,
                contractor_address,
                contractor_city,
                contractor_postal_code,
                iso_country,
                nuts_code,
                place_of_performance
            FROM ted_contracts_production
            ORDER BY id
            LIMIT {limit} OFFSET {offset}
        ''')

        contracts = self.cursor.fetchall()

        if len(contracts) == 0:
            return 0

        for contract in contracts:
            # Apply null protocols
            contractor_name = self.get_contractor_name_with_null_protocol(contract)
            country_code = self.get_country_code_with_null_protocol(contract)
            address = self.get_address_with_null_protocol(contract)

            # Skip if no contractor name
            if not contractor_name:
                continue

            # Detect Chinese entity
            result = self.validator.validate_entity(
                entity_name=contractor_name,
                contractor_country=country_code,
                contractor_address=address,
                min_confidence=self.min_confidence
            )

            self.stats['entities_validated'] += 1

            # Track exclusions
            if result['is_european_exclusion']:
                self.stats['european_exclusions'] += 1
                continue

            if result['confidence_score'] < self.min_confidence:
                self.stats['low_confidence_exclusions'] += 1
                continue

            # Valid Chinese entity
            if result['validation_passed']:
                self.stats['entities_detected'] += 1

                # Add or update entity
                if contractor_name not in self.entities:
                    self.entities[contractor_name] = {
                        'entity_name': contractor_name,
                        'country_code': country_code,
                        'address': address,
                        'confidence': result['confidence_score'],
                        'has_chinese_characters': result['has_chinese_chars'],
                        'contracts_count': 1,
                        'first_seen': contract['id'],
                        'last_seen': contract['id']
                    }
                    self.stats['entities_added'] += 1
                else:
                    # Update existing entity
                    self.entities[contractor_name]['contracts_count'] += 1
                    self.entities[contractor_name]['last_seen'] = contract['id']

        self.stats['contracts_processed'] += len(contracts)

        return len(contracts)

    def flush_entities_to_database(self):
        """
        Flush accumulated entities to database.
        """
        if self.dry_run:
            print(f"DRY RUN: Would flush {len(self.entities):,} entities to database")
            return

        if len(self.entities) == 0:
            return

        print(f"Flushing {len(self.entities):,} entities to database...")

        for entity_name, entity_data in self.entities.items():
            self.cursor.execute('''
                INSERT INTO ted_procurement_chinese_entities_found
                (entity_name, entity_type, contracts_count, countries_active,
                 first_seen, last_seen, detection_confidence, has_chinese_characters,
                 validated_country_code)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                entity_data['entity_name'],
                'contractor',
                entity_data['contracts_count'],
                entity_data.get('country_code', 'UNKNOWN'),
                entity_data['first_seen'],
                entity_data['last_seen'],
                entity_data['confidence'],
                1 if entity_data['has_chinese_characters'] else 0,
                entity_data.get('country_code')
            ))

        self.conn.commit()
        print(f"  {len(self.entities):,} entities committed to database")

    def execute_rebuild(self, test_mode: bool = False, test_limit: int = 10000) -> Dict:
        """
        Execute full rebuild of Chinese entity table.

        Args:
            test_mode: If True, only process limited number of contracts
            test_limit: Number of contracts to process in test mode

        Returns:
            Dictionary with rebuild results and statistics
        """
        print("="*80)
        print("TED CHINESE ENTITY REBUILD WITH NULL PROTOCOLS")
        print("="*80)
        print()
        print(f"Configuration:")
        print(f"  Minimum confidence threshold: {self.min_confidence}%")
        print(f"  Batch size: {BATCH_SIZE:,} contracts")
        print(f"  Quality gate frequency: Every 50,000 contracts")
        print(f"  Dry run mode: {self.dry_run}")
        print(f"  Test mode: {test_mode}")
        if test_mode:
            print(f"  Test limit: {test_limit:,} contracts")
        print()

        try:
            self.connect_database()

            # Get total contract count
            self.cursor.execute("SELECT COUNT(*) FROM ted_contracts_production")
            total_contracts = self.cursor.fetchone()[0]
            print(f"Total TED contracts: {total_contracts:,}")
            print()

            # Check for checkpoint
            checkpoint = self.load_checkpoint()
            start_offset = checkpoint.get('contracts_processed', 0)

            if start_offset > 0:
                print(f"Resuming from checkpoint at offset {start_offset:,}")
                print()

            # Calculate processing limit
            if test_mode:
                max_contracts = min(test_limit, total_contracts)
            else:
                max_contracts = total_contracts

            # Process in batches
            offset = start_offset
            batch_num = 0

            while offset < max_contracts:
                batch_num += 1
                batch_start_time = time.time()

                # Process batch
                processed = self.process_batch(offset, BATCH_SIZE)

                if processed == 0:
                    break

                batch_elapsed = time.time() - batch_start_time
                contracts_per_sec = processed / batch_elapsed if batch_elapsed > 0 else 0

                self.stats['batches_completed'] += 1

                # Progress report
                progress_pct = (offset / max_contracts * 100) if max_contracts > 0 else 0
                print(f"Batch {batch_num}: Processed {processed:,} contracts "
                      f"({offset:,}/{max_contracts:,}, {progress_pct:.1f}%) "
                      f"[{contracts_per_sec:.0f} contracts/sec]")
                print(f"  Entities detected so far: {self.stats['entities_detected']:,}")
                print(f"  Unique entities: {len(self.entities):,}")

                offset += processed

                # Save checkpoint every batch
                self.save_checkpoint(offset)

                # Quality gate check every 50,000 contracts
                if offset % 50000 < BATCH_SIZE and offset > start_offset:
                    if not self.quality_gate_check():
                        print("STOPPING: Quality gate failed")
                        return {'status': 'failed', 'reason': 'quality_gate_failed', 'stats': self.stats}

            # Final flush to database
            print()
            print("="*80)
            print("FINALIZING")
            print("="*80)
            self.flush_entities_to_database()

            # Final statistics
            print()
            print("="*80)
            print("REBUILD COMPLETE")
            print("="*80)
            print()
            print(f"Contracts processed: {self.stats['contracts_processed']:,}")
            print(f"Entities detected: {self.stats['entities_detected']:,}")
            print(f"Unique entities added: {len(self.entities):,}")
            print(f"European exclusions: {self.stats['european_exclusions']:,}")
            print(f"Low confidence exclusions: {self.stats['low_confidence_exclusions']:,}")
            print(f"Null fields recovered: {self.stats['null_fields_recovered']:,}")
            print(f"Quality checks passed: {self.stats['quality_checks_passed']}")
            print(f"Quality checks failed: {self.stats['quality_checks_failed']}")
            print()

            self.stats['end_time'] = datetime.now().isoformat()
            self.stats['status'] = 'success'

            return {'status': 'success', 'stats': self.stats}

        except Exception as e:
            print(f"ERROR: Rebuild failed - {e}")
            import traceback
            traceback.print_exc()

            if not self.dry_run:
                print("Rolling back changes...")
                self.conn.rollback()

            self.stats['status'] = 'error'
            self.stats['error'] = str(e)
            return {'status': 'error', 'error': str(e), 'stats': self.stats}

        finally:
            self.close_database()


def main():
    """Main execution function."""
    print("TED Chinese Entity Rebuild - Comprehensive Detection with Null Protocols")
    print("="*80)
    print()

    # Configuration
    MIN_CONFIDENCE = 70.0  # Confidence threshold
    DRY_RUN = False  # Set to True for dry run
    TEST_MODE = False  # Production mode - process all contracts
    TEST_LIMIT = 10000  # Test with 10,000 contracts first

    # Create rebuilder instance
    rebuilder = TEDEntityRebuilder(
        min_confidence=MIN_CONFIDENCE,
        dry_run=DRY_RUN
    )

    # Execute rebuild
    result = rebuilder.execute_rebuild(
        test_mode=TEST_MODE,
        test_limit=TEST_LIMIT
    )

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"analysis/ted_rebuild_report_{timestamp}.json"

    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print("="*80)
    print("REPORT SAVED")
    print("="*80)
    print(f"Report: {report_file}")
    print()

    if result['status'] == 'success':
        stats = result['stats']
        print("Summary:")
        print(f"  Contracts processed: {stats.get('contracts_processed', 0):,}")
        print(f"  Entities detected: {stats.get('entities_detected', 0):,}")
        print(f"  Entities added to database: {stats.get('entities_added', 0):,}")
        print(f"  Null fields recovered: {stats.get('null_fields_recovered', 0):,}")
        print(f"  European exclusions: {stats.get('european_exclusions', 0):,}")
        print(f"  Quality checks passed: {stats.get('quality_checks_passed', 0)}")
    else:
        print(f"Status: {result['status']}")
        print(f"Error: {result.get('error', 'unknown')}")

    print()

    return 0 if result['status'] == 'success' else 1


if __name__ == "__main__":
    exit(main())

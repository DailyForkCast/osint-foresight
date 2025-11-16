#!/usr/bin/env python3
"""
TED Improved Entity Sync with Validation
Created: October 20, 2025
Purpose: Sync TED Chinese entities with comprehensive quality controls
"""

import sqlite3
import json
import random
from datetime import datetime
from typing import Dict, List, Tuple
from ted_validation_rules import TEDEntityValidator

DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"

class TEDImprovedSync:
    """
    Improved TED synchronization with multi-stage validation and quality gates.
    """

    def __init__(self, min_confidence: float = 70.0, dry_run: bool = False):
        """
        Initialize sync with validation parameters.

        Args:
            min_confidence: Minimum confidence score to flag entity (default 70%)
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
            'entities_in_table': 0,
            'contracts_before': 0,
            'contracts_after': 0,
            'entities_validated': 0,
            'entities_passed_validation': 0,
            'entities_failed_validation': 0,
            'european_exclusions': 0,
            'low_confidence_exclusions': 0,
            'contracts_to_flag': 0,
            'contracts_flagged': 0,
            'validation_samples': [],
            'quality_gates_passed': []
        }

    def connect_database(self):
        """Connect to database."""
        self.conn = sqlite3.connect(DB_PATH, timeout=60)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def close_database(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()

    def quality_gate_1_validate_source_table(self) -> bool:
        """
        Quality Gate 1: Validate source entity table before sync.

        Returns:
            True if validation passed, False otherwise
        """
        print("="*80)
        print("QUALITY GATE 1: Validate Source Entity Table")
        print("="*80)
        print()

        # Get all entities from source table
        self.cursor.execute('''
            SELECT entity_id, entity_name, entity_type,
                   contracts_count
            FROM ted_procurement_chinese_entities_found
            ORDER BY contracts_count DESC
        ''')

        entities = self.cursor.fetchall()
        self.stats['entities_in_table'] = len(entities)

        print(f"Total entities in source table: {len(entities):,}")
        print()

        # Sample entities for validation
        sample_size = min(100, len(entities))
        sample = random.sample(list(entities), sample_size)

        print(f"Validating random sample of {sample_size} entities...")
        print()

        validation_results = []
        european_count = 0
        low_confidence_count = 0
        passed_count = 0

        for entity in sample:
            entity_name = entity['entity_name']

            # Run validation
            result = self.validator.validate_entity(
                entity_name=entity_name,
                min_confidence=self.min_confidence
            )

            validation_results.append({
                'entity_id': entity['entity_id'],
                'entity_name': entity_name,
                'is_valid': result['validation_passed'],
                'confidence': result['confidence_score'],
                'is_european': result['is_european_exclusion'],
                'european_suffix': result['european_suffix']
            })

            if result['is_european_exclusion']:
                european_count += 1
            elif result['confidence_score'] < self.min_confidence:
                low_confidence_count += 1
            elif result['validation_passed']:
                passed_count += 1

        # Calculate statistics
        total_sample = len(validation_results)
        precision = (passed_count / total_sample * 100) if total_sample > 0 else 0
        european_pct = (european_count / total_sample * 100) if total_sample > 0 else 0

        print(f"Validation Results:")
        print(f"  Passed validation: {passed_count} ({passed_count/total_sample*100:.1f}%)")
        print(f"  European exclusions: {european_count} ({european_pct:.1f}%)")
        print(f"  Low confidence: {low_confidence_count} ({low_confidence_count/total_sample*100:.1f}%)")
        print(f"  Estimated precision: {precision:.1f}%")
        print()

        # Store samples for reporting
        self.stats['validation_samples'] = validation_results[:20]  # Top 20 for report

        # Quality gate threshold: minimum 70% precision
        if precision < 70.0:
            print(f"QUALITY GATE 1 FAILED: Precision {precision:.1f}% below 70% threshold")
            print(f"  Too many false positives in source table!")
            print(f"  Recommendation: Clean source table before sync")
            return False

        if european_pct > 5.0:
            print(f"QUALITY GATE 1 WARNING: {european_pct:.1f}% European companies detected")
            print(f"  Recommendation: Remove European entities from source table")
            # Continue but warn

        print(f"QUALITY GATE 1 PASSED: Precision {precision:.1f}% meets threshold")
        self.stats['quality_gates_passed'].append('QG1: Source Table Validation')
        print()

        return True

    def quality_gate_2_validate_matches(self) -> bool:
        """
        Quality Gate 2: Validate proposed matches before flagging.

        Returns:
            True if validation passed, False otherwise
        """
        print("="*80)
        print("QUALITY GATE 2: Validate Proposed Matches")
        print("="*80)
        print()

        # Find contracts that would be flagged
        self.cursor.execute('''
            SELECT
                tcp.id,
                tcp.contractor_name,
                tcp.contractor_country,
                tcp.contractor_address,
                tpcef.entity_name
            FROM ted_contracts_production tcp
            JOIN ted_procurement_chinese_entities_found tpcef
                ON LOWER(tcp.contractor_name) = LOWER(tpcef.entity_name)
            WHERE tcp.is_chinese_related != 1 OR tcp.is_chinese_related IS NULL
            LIMIT 1000
        ''')

        proposed_matches = self.cursor.fetchall()
        total_proposed = len(proposed_matches)

        print(f"Proposed contracts to flag: {total_proposed:,}")
        print()

        if total_proposed == 0:
            print("No new contracts to flag. Sync not needed.")
            return False

        # Sample proposed matches for validation
        sample_size = min(100, len(proposed_matches))
        sample = random.sample(list(proposed_matches), sample_size)

        print(f"Validating random sample of {sample_size} proposed matches...")
        print()

        validation_results = []
        passed_count = 0
        failed_count = 0
        european_count = 0

        for match in sample:
            # Validate with full contract context
            result = self.validator.validate_entity(
                entity_name=match['contractor_name'],
                contractor_country=match['contractor_country'],
                contractor_address=match['contractor_address'],
                min_confidence=self.min_confidence
            )

            validation_results.append({
                'contract_id': match['id'],
                'contractor_name': match['contractor_name'],
                'contractor_country': match['contractor_country'],
                'is_valid': result['validation_passed'],
                'confidence': result['confidence_score'],
                'is_european': result['is_european_exclusion']
            })

            if result['validation_passed']:
                passed_count += 1
            else:
                failed_count += 1
                if result['is_european_exclusion']:
                    european_count += 1

        # Calculate precision
        precision = (passed_count / len(validation_results) * 100) if validation_results else 0

        print(f"Match Validation Results:")
        print(f"  Valid matches: {passed_count} ({precision:.1f}%)")
        print(f"  Invalid matches: {failed_count} ({100-precision:.1f}%)")
        print(f"  European false positives: {european_count}")
        print()

        # Store for reporting
        self.stats['match_validation_samples'] = validation_results[:20]

        # Quality gate threshold: minimum 90% precision on matches
        if precision < 90.0:
            print(f"QUALITY GATE 2 FAILED: Match precision {precision:.1f}% below 90% threshold")
            print(f"  Too many false positives would be flagged!")
            print(f"  Recommendation: Improve entity table quality or increase confidence threshold")
            return False

        print(f"QUALITY GATE 2 PASSED: Match precision {precision:.1f}% meets threshold")
        self.stats['quality_gates_passed'].append('QG2: Match Validation')
        print()

        return True

    def execute_sync(self, test_mode: bool = False, test_limit: int = 1000) -> Dict:
        """
        Execute synchronization with validation.

        Args:
            test_mode: If True, only process limited number of contracts
            test_limit: Number of contracts to process in test mode

        Returns:
            Dictionary with sync results and statistics
        """
        print("="*80)
        print("TED IMPROVED SYNC WITH VALIDATION")
        print("="*80)
        print()
        print(f"Configuration:")
        print(f"  Minimum confidence threshold: {self.min_confidence}%")
        print(f"  Dry run mode: {self.dry_run}")
        print(f"  Test mode: {test_mode}")
        if test_mode:
            print(f"  Test limit: {test_limit:,} contracts")
        print()

        try:
            self.connect_database()

            # Get current state
            self.cursor.execute("SELECT COUNT(*) FROM ted_contracts_production WHERE is_chinese_related = 1")
            self.stats['contracts_before'] = self.cursor.fetchone()[0]

            print(f"Current state: {self.stats['contracts_before']:,} contracts flagged")
            print()

            # Quality Gate 1: Validate source table
            if not self.quality_gate_1_validate_source_table():
                print("SYNC ABORTED: Quality Gate 1 failed")
                return {'status': 'failed', 'gate_failed': 'QG1', 'stats': self.stats}

            # Quality Gate 2: Validate proposed matches
            if not self.quality_gate_2_validate_matches():
                print("SYNC ABORTED: Quality Gate 2 failed")
                return {'status': 'failed', 'gate_failed': 'QG2', 'stats': self.stats}

            # All quality gates passed - proceed with sync
            print("="*80)
            print("EXECUTING SYNC")
            print("="*80)
            print()

            if self.dry_run:
                print("DRY RUN MODE: No database changes will be made")
                print()

            # Build update query with validation
            update_query = '''
                UPDATE ted_contracts_production
                SET is_chinese_related = 1
                WHERE id IN (
                    SELECT DISTINCT tcp.id
                    FROM ted_contracts_production tcp
                    JOIN ted_procurement_chinese_entities_found tpcef
                        ON LOWER(tcp.contractor_name) = LOWER(tpcef.entity_name)
                    WHERE (tcp.is_chinese_related != 1 OR tcp.is_chinese_related IS NULL)
            '''

            if test_mode:
                update_query += f' LIMIT {test_limit}'

            update_query += ')'

            if not self.dry_run:
                print("Executing sync...")
                self.cursor.execute(update_query)
                self.stats['contracts_flagged'] = self.cursor.rowcount
                print(f"  Flagged {self.stats['contracts_flagged']:,} contracts")
                print()

                # Commit changes
                print("Committing changes...")
                self.conn.commit()
                print("  Changes committed successfully")
                print()

                # Verify
                self.cursor.execute("SELECT COUNT(*) FROM ted_contracts_production WHERE is_chinese_related = 1")
                self.stats['contracts_after'] = self.cursor.fetchone()[0]

                print(f"Verification:")
                print(f"  Before: {self.stats['contracts_before']:,} flagged")
                print(f"  After: {self.stats['contracts_after']:,} flagged")
                print(f"  Added: {self.stats['contracts_after'] - self.stats['contracts_before']:,} flags")
                print()

            else:
                print("DRY RUN: Skipping database update")
                print()

            self.stats['status'] = 'success'
            self.stats['end_time'] = datetime.now().isoformat()

            return {'status': 'success', 'stats': self.stats}

        except Exception as e:
            print(f"ERROR: Sync failed - {e}")
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
    print("TED Improved Sync - Quality-Controlled Entity Synchronization")
    print("="*80)
    print()

    # Configuration
    MIN_CONFIDENCE = 70.0  # Confidence threshold
    DRY_RUN = False  # Set to True for dry run
    TEST_MODE = True  # Start with test mode
    TEST_LIMIT = 100  # Test with 100 contracts first

    # Create sync instance
    sync = TEDImprovedSync(
        min_confidence=MIN_CONFIDENCE,
        dry_run=DRY_RUN
    )

    # Execute sync
    result = sync.execute_sync(
        test_mode=TEST_MODE,
        test_limit=TEST_LIMIT
    )

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"analysis/ted_improved_sync_report_{timestamp}.json"

    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print("="*80)
    print("SYNC COMPLETE")
    print("="*80)
    print()
    print(f"Status: {result['status'].upper()}")
    print(f"Report saved to: {report_file}")
    print()

    if result['status'] == 'success':
        stats = result['stats']
        print("Summary:")
        print(f"  Quality gates passed: {len(stats.get('quality_gates_passed', []))}")
        print(f"  Entities in table: {stats.get('entities_in_table', 0):,}")
        print(f"  Contracts before: {stats.get('contracts_before', 0):,}")
        print(f"  Contracts after: {stats.get('contracts_after', 0):,}")
        print(f"  Contracts flagged: {stats.get('contracts_flagged', 0):,}")
    else:
        print(f"Failed at: {result.get('gate_failed', 'unknown')}")
        print(f"Error: {result.get('error', 'unknown')}")

    print()

    return 0 if result['status'] == 'success' else 1


if __name__ == "__main__":
    exit(main())

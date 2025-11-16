#!/usr/bin/env python3
"""
Reclassify USPTO Patents v2.0 - Taiwan/PRC Separation

Applies entity_classification_validator to existing uspto_patents_chinese table
to properly separate Taiwan, PRC, Hong Kong, and Macao patents.

Based on learnings from USAspending v2.0 processing.
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.entity_classification_validator import (
    EntityClassificationValidator,
    EntityOrigin,
    ConfidenceLevel
)

class USPTOPatentReclassifier:
    """Reclassify existing USPTO patents with Taiwan/PRC separation."""

    def __init__(self):
        self.db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")
        self.validator = EntityClassificationValidator()

        self.stats = {
            'total_processed': 0,
            'prc_classified': 0,
            'taiwan_classified': 0,
            'hong_kong_classified': 0,
            'macao_classified': 0,
            'unknown_classified': 0,
            'by_confidence': {},
            'taiwan_companies_found': {},
        }

    def create_v2_table(self, conn):
        """Create uspto_patents_chinese_v2 table with new fields."""

        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS uspto_patents_chinese_v2 (
                application_number TEXT,
                patent_number TEXT PRIMARY KEY,
                filing_date TEXT,
                grant_date TEXT,
                title TEXT,
                status TEXT,
                assignee_name TEXT,
                assignee_country TEXT,
                assignee_city TEXT,

                -- NEW v2.0 FIELDS
                entity_country_of_origin TEXT,  -- CN, TW, HK, MO, UNKNOWN
                confidence_level TEXT,  -- VERIFIED, HIGH, MEDIUM, LOW, NEEDS_REVIEW
                detection_method TEXT,
                validation_warnings TEXT,
                taiwan_prc_policy_compliant INTEGER DEFAULT 1,
                processor_version TEXT DEFAULT '2.0',

                -- LEGACY FIELDS (for comparison)
                old_confidence TEXT,
                old_confidence_score INTEGER,
                old_detection_signals TEXT,

                year INTEGER,
                processed_date TEXT,
                data_quality_flag TEXT,
                fields_with_data_count INTEGER
            )
        ''')

        conn.commit()
        print("✓ Created uspto_patents_chinese_v2 table")

    def classify_patent(self, assignee_name: str, assignee_city: str = None) -> dict:
        """
        Classify a patent using entity_classification_validator.

        Since assignee_country is NULL for all records, we rely on name-based detection.
        """

        # Use validator to classify
        classification = self.validator.classify_entity(
            entity_name=assignee_name,
            country_code=None,  # All NULL in USPTO data
            value=0  # Patents don't have monetary value
        )

        # Map to our output format
        result = {
            'entity_country_of_origin': classification.origin.value,
            'confidence_level': classification.confidence.value,
            'detection_method': 'name_based',  # Since no country code
            'validation_warnings': ', '.join(classification.warnings) if classification.warnings else None,
            'taiwan_prc_policy_compliant': 1
        }

        # Track Taiwan companies found
        if classification.origin == EntityOrigin.TAIWAN:
            company_key = assignee_name[:50] if assignee_name else 'Unknown'
            self.stats['taiwan_companies_found'][company_key] = \
                self.stats['taiwan_companies_found'].get(company_key, 0) + 1

        return result

    def reclassify_all_patents(self):
        """Main processing loop - reclassify all existing patents."""

        print("="*80)
        print("USPTO Patents v2.0 Reclassification")
        print("="*80)
        print("\nApplying Taiwan/PRC Classification Policy v1.0")
        print("Using entity_classification_validator v2.0\n")

        conn = sqlite3.connect(self.db_path, timeout=60)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Create v2 table
        self.create_v2_table(conn)

        # Get total count
        cursor.execute("SELECT COUNT(*) FROM uspto_patents_chinese")
        total = cursor.fetchone()[0]
        print(f"Total patents to reclassify: {total:,}\n")

        # Process in batches
        batch_size = 5000
        processed = 0

        cursor.execute("SELECT * FROM uspto_patents_chinese")

        batch = []

        while True:
            row = cursor.fetchone()

            if row is None:
                # Process final batch
                if batch:
                    self._save_batch(conn, batch)
                break

            # Classify this patent
            classification = self.classify_patent(
                assignee_name=row['assignee_name'],
                assignee_city=row['assignee_city']
            )

            # Prepare record for v2 table
            record = {
                'application_number': row['application_number'],
                'patent_number': row['patent_number'],
                'filing_date': row['filing_date'],
                'grant_date': row['grant_date'],
                'title': row['title'],
                'status': row['status'],
                'assignee_name': row['assignee_name'],
                'assignee_country': row['assignee_country'],
                'assignee_city': row['assignee_city'],

                # New v2.0 fields
                'entity_country_of_origin': classification['entity_country_of_origin'],
                'confidence_level': classification['confidence_level'],
                'detection_method': classification['detection_method'],
                'validation_warnings': classification['validation_warnings'],
                'taiwan_prc_policy_compliant': classification['taiwan_prc_policy_compliant'],
                'processor_version': '2.0',

                # Legacy fields
                'old_confidence': row['confidence'],
                'old_confidence_score': row['confidence_score'],
                'old_detection_signals': row['detection_signals'],

                'year': row['year'],
                'processed_date': datetime.now().strftime('%Y-%m-%d'),
                'data_quality_flag': row['data_quality_flag'],
                'fields_with_data_count': row['fields_with_data_count']
            }

            batch.append(record)

            # Update stats
            origin = classification['entity_country_of_origin']
            if origin == 'CN':
                self.stats['prc_classified'] += 1
            elif origin == 'TW':
                self.stats['taiwan_classified'] += 1
            elif origin == 'HK':
                self.stats['hong_kong_classified'] += 1
            elif origin == 'MO':
                self.stats['macao_classified'] += 1
            else:
                self.stats['unknown_classified'] += 1

            confidence = classification['confidence_level']
            self.stats['by_confidence'][confidence] = \
                self.stats['by_confidence'].get(confidence, 0) + 1

            # Save batch
            if len(batch) >= batch_size:
                self._save_batch(conn, batch)
                batch = []
                processed += batch_size
                self.stats['total_processed'] = processed

                if processed % 50000 == 0:
                    self._print_progress()

        self.stats['total_processed'] = total
        conn.close()

        print("\n" + "="*80)
        print("RECLASSIFICATION COMPLETE")
        print("="*80)
        self._print_final_stats()

    def _save_batch(self, conn, batch):
        """Save a batch of reclassified patents."""

        cursor = conn.cursor()

        for record in batch:
            cursor.execute('''
                INSERT OR REPLACE INTO uspto_patents_chinese_v2
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                record['application_number'],
                record['patent_number'],
                record['filing_date'],
                record['grant_date'],
                record['title'],
                record['status'],
                record['assignee_name'],
                record['assignee_country'],
                record['assignee_city'],
                record['entity_country_of_origin'],
                record['confidence_level'],
                record['detection_method'],
                record['validation_warnings'],
                record['taiwan_prc_policy_compliant'],
                record['processor_version'],
                record['old_confidence'],
                record['old_confidence_score'],
                record['old_detection_signals'],
                record['year'],
                record['processed_date'],
                record['data_quality_flag'],
                record['fields_with_data_count']
            ))

        conn.commit()

    def _print_progress(self):
        """Print progress update."""

        print(f"\nProcessed: {self.stats['total_processed']:,} patents")
        print(f"  PRC (CN): {self.stats['prc_classified']:,}")
        print(f"  Taiwan (TW): {self.stats['taiwan_classified']:,}")
        print(f"  Hong Kong (HK): {self.stats['hong_kong_classified']:,}")
        print(f"  Macao (MO): {self.stats['macao_classified']:,}")
        print(f"  Unknown: {self.stats['unknown_classified']:,}")

    def _print_final_stats(self):
        """Print comprehensive final statistics."""

        print(f"\nTotal Patents Processed: {self.stats['total_processed']:,}")
        print("\nGEOGRAPHIC CLASSIFICATION (Taiwan/PRC Policy v1.0):")
        print(f"  PRC (CN): {self.stats['prc_classified']:,} patents")
        print(f"  Taiwan (TW): {self.stats['taiwan_classified']:,} patents")
        print(f"  Hong Kong SAR (HK): {self.stats['hong_kong_classified']:,} patents")
        print(f"  Macao SAR (MO): {self.stats['macao_classified']:,} patents")
        print(f"  Unknown: {self.stats['unknown_classified']:,} patents")

        print("\nBY CONFIDENCE LEVEL:")
        for confidence, count in sorted(self.stats['by_confidence'].items()):
            print(f"  {confidence}: {count:,} patents")

        # Top Taiwan companies
        if self.stats['taiwan_companies_found']:
            print("\nTOP TAIWAN COMPANIES IDENTIFIED:")
            sorted_companies = sorted(
                self.stats['taiwan_companies_found'].items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
            for company, count in sorted_companies:
                print(f"  {company:50s}: {count:,} patents")

        print("\n" + "="*80)
        print("DATA SAVED TO: F:/OSINT_WAREHOUSE/osint_master.db")
        print("TABLE: uspto_patents_chinese_v2")
        print("POLICY COMPLIANT: Taiwan/PRC Classification Policy v1.0")
        print("="*80)


def main():
    """Main entry point."""

    try:
        reclassifier = USPTOPatentReclassifier()
        reclassifier.reclassify_all_patents()

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

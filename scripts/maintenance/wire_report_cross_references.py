#!/usr/bin/env python3
"""
Report Cross-Reference Wiring System
====================================
Links thinktank_reports to TED/CORDIS/OpenAlex based on entity and topic matches.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
import argparse

class CrossReferenceWirer:
    def __init__(self, db_path: str = "F:/OSINT_WAREHOUSE/osint_master.db"):
        self.db_path = db_path

    def find_matches(self):
        """Find potential cross-references."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        matches = []

        # Get unique entities from reports (limit to significant ones)
        cursor.execute('''
            SELECT DISTINCT entity_name
            FROM report_entities
            WHERE entity_name IS NOT NULL
              AND LENGTH(entity_name) >= 5
            LIMIT 50
        ''')

        entities = [row[0] for row in cursor.fetchall()]
        print(f"Processing {len(entities)} unique entities...")

        for i, entity in enumerate(entities, 1):
            if i % 10 == 0:
                print(f"  Processed {i}/{len(entities)} entities...")

            # Get reports mentioning this entity
            cursor.execute('''
                SELECT report_id
                FROM report_entities
                WHERE entity_name = ?
            ''', (entity,))
            report_ids = [row[0] for row in cursor.fetchall()]

            # Find TED exact matches (faster)
            cursor.execute('''
                SELECT id, contractor_name, contractor_country
                FROM ted_contractors
                WHERE contractor_name = ?
                LIMIT 5
            ''', (entity,))

            ted_matches = cursor.fetchall()

            # If no exact match, try substring (limited)
            if not ted_matches and len(entity) > 10:
                cursor.execute('''
                    SELECT id, contractor_name, contractor_country
                    FROM ted_contractors
                    WHERE contractor_name LIKE ?
                    LIMIT 3
                ''', (f'%{entity}%',))
                ted_matches = cursor.fetchall()

            for ted_id, contractor_name, country in ted_matches:
                for report_id in report_ids:
                    matches.append({
                        'report_id': report_id,
                        'source_type': 'TED',
                        'source_record_id': f'contractor_{ted_id}',
                        'reference_type': 'entity_match',
                        'confidence': 0.8 if contractor_name == entity else 0.6,
                        'validation_notes': f'Entity "{entity}" matches TED contractor "{contractor_name}" ({country})'
                    })

        conn.close()
        return matches

    def insert_matches(self, matches, dry_run=True):
        """Insert cross-references."""
        if dry_run:
            print(f"[DRY RUN] Would insert {len(matches)} cross-references")
            return 0

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        inserted = 0

        for m in matches:
            try:
                cursor.execute('''
                    INSERT INTO report_cross_references
                    (report_id, source_type, source_record_id, reference_type, confidence, validation_notes)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (m['report_id'], m['source_type'], m['source_record_id'],
                      m['reference_type'], m['confidence'], m['validation_notes']))
                inserted += 1
            except sqlite3.IntegrityError:
                continue

        conn.commit()
        conn.close()
        return inserted

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--auto', action='store_true')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    wirer = CrossReferenceWirer()

    print("Finding cross-reference matches...")
    matches = wirer.find_matches()
    print(f"Found {len(matches)} potential matches")

    if args.auto:
        inserted = wirer.insert_matches(matches, dry_run=args.dry_run)
        print(f"Inserted {inserted} cross-references")

if __name__ == "__main__":
    main()

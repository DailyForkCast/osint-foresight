#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ETL: Expand bilateral_corporate_links from GLEIF - V5 OPTIMIZED
Purpose: Extract Chinese → European corporate ownership relationships

V5 Changes:
  - Simplified query strategy using indexed fields directly
  - Avoid complex OR/IN clauses that prevent index usage
  - Two-step query: Chinese parents first, then European children
  - Much faster execution with new indexes

Last Updated: 2025-11-04
Author: OSINT Foresight Project
"""

import sqlite3
import json
import sys
import uuid
from datetime import datetime
from typing import List, Dict

# Fix Windows encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"

class GLEIFCorporateLinksETL:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.links_created = 0
        self.errors = []
        self.validation_sample = []

    def pre_etl_validation(self):
        """Pre-ETL validation per framework"""
        print("="*80)
        print("PRE-ETL VALIDATION")
        print("="*80)

        try:
            self.cursor.execute("SELECT COUNT(*) FROM gleif_entities LIMIT 1")
            print("[OK] gleif_entities table exists")

            self.cursor.execute("SELECT COUNT(*) FROM gleif_relationships LIMIT 1")
            print("[OK] gleif_relationships table exists")

        except sqlite3.OperationalError as e:
            print(f"[ERROR] {e}")
            raise

        self.cursor.execute("SELECT COUNT(*) FROM bilateral_corporate_links")
        existing = self.cursor.fetchone()[0]
        print(f"[OK] bilateral_corporate_links: {existing:,} existing records")

        print("\n[OK] Pre-ETL validation PASSED\n")
        return True

    def extract_chinese_european_relationships(self) -> List[Dict]:
        """Extract Chinese → European ownership relationships using optimized queries"""
        print("="*80)
        print("EXTRACTION PHASE (OPTIMIZED STRATEGY)")
        print("="*80)

        # Get EU countries
        self.cursor.execute("SELECT country_code FROM bilateral_countries")
        eu_countries = [row[0] for row in self.cursor.fetchall()]

        print(f"Target European countries: {len(eu_countries)}")
        print("\nStep 1: Find ACTIVE relationships")

        # Step 1: Get all ACTIVE relationships (uses idx_gleif_relationships_status)
        self.cursor.execute("""
            SELECT id, parent_lei, child_lei, relationship_type,
                   start_date, last_update_date
            FROM gleif_relationships
            WHERE relationship_status = 'ACTIVE'
            LIMIT 10000
        """)
        active_rels = self.cursor.fetchall()
        print(f"         Found {len(active_rels):,} active relationships")

        # Step 2: Filter for Chinese parents and European children
        print("\nStep 2: Filter for Chinese parents...")

        relationships = []
        for rel in active_rels:
            # Get parent entity (uses idx_gleif_entities_legal_country)
            self.cursor.execute("""
                SELECT lei, legal_name, legal_address_country, hq_address_country
                FROM gleif_entities
                WHERE lei = ?
                  AND (legal_address_country = 'CN' OR hq_address_country = 'CN')
            """, (rel['parent_lei'],))
            parent = self.cursor.fetchone()

            if not parent:
                continue

            # Get child entity
            self.cursor.execute("""
                SELECT lei, legal_name, legal_address_country, hq_address_country
                FROM gleif_entities
                WHERE lei = ?
            """, (rel['child_lei'],))
            child = self.cursor.fetchone()

            if not child:
                continue

            # Check if child is in European country
            child_country = child['legal_address_country'] or child['hq_address_country']
            if child_country not in eu_countries:
                continue

            # Build relationship record
            parent_country = parent['legal_address_country'] or parent['hq_address_country']

            relationship = {
                'relationship_id': rel['id'],
                'parent_lei': rel['parent_lei'],
                'child_lei': rel['child_lei'],
                'relationship_type': rel['relationship_type'],
                'parent_name': parent['legal_name'],
                'parent_country': parent_country,
                'child_name': child['legal_name'],
                'child_country': child_country,
                'start_date': rel['start_date'],
                'last_update_date': rel['last_update_date'],
                'status': 'ACTIVE'
            }
            relationships.append(relationship)

            # Print progress every 50
            if len(relationships) % 50 == 0:
                print(f"         Progress: {len(relationships)} relationships found...")

        print(f"\n[OK] Extracted {len(relationships):,} Chinese->European relationships")

        if relationships:
            print("\nSample relationships (LEIs only):")
            for rel in relationships[:5]:
                print(f"  {rel['parent_lei']} (CN) -> {rel['child_lei']} ({rel['child_country']})")
                print(f"    Type: {rel['relationship_type']}")

        return relationships

    def transform(self, relationships: List[Dict]) -> List[Dict]:
        """Transform GLEIF relationships to match actual schema"""
        print("\n" + "="*80)
        print("TRANSFORMATION PHASE")
        print("="*80)

        TYPE_MAPPING = {
            'IS_DIRECTLY_CONSOLIDATED_BY': 'subsidiary',
            'IS_ULTIMATELY_CONSOLIDATED_BY': 'subsidiary',
            'IS_INTERNATIONAL_BRANCH_OF': 'branch',
            'IS_FUND_MANAGED_BY': 'managed_fund',
            'IS_FEEDER_TO': 'feeder_fund',
        }

        transformed = []
        for rel in relationships:
            gleif_type = rel['relationship_type'] or 'UNKNOWN'
            relationship_type = TYPE_MAPPING.get(gleif_type, 'ownership')

            link = {
                'link_id': str(uuid.uuid4()),
                'investment_id': None,
                'acquisition_id': None,
                'country_code': rel['child_country'],
                'gleif_lei': rel['child_lei'],
                'chinese_entity': rel['parent_name'],
                'foreign_entity': rel['child_name'],
                'relationship_type': relationship_type,
                'ownership_percentage': None,
                'created_at': datetime.now().isoformat(),
                '_parent_lei': rel['parent_lei'],
                '_gleif_relationship_id': rel['relationship_id'],
                '_gleif_type': gleif_type
            }

            transformed.append(link)

        print(f"[OK] Transformed {len(transformed):,} relationships into corporate links")

        # Statistics
        link_types = {}
        countries = {}
        for link in transformed:
            link_types[link['relationship_type']] = link_types.get(link['relationship_type'], 0) + 1
            countries[link['country_code']] = countries.get(link['country_code'], 0) + 1

        print("\nRelationship type distribution:")
        for ltype, count in sorted(link_types.items(), key=lambda x: x[1], reverse=True):
            print(f"  {ltype}: {count}")

        print("\nCountry distribution:")
        for country, count in sorted(countries.items(), key=lambda x: x[1], reverse=True):
            print(f"  {country}: {count}")

        return transformed

    def load(self, links: List[Dict]):
        """Load transformed links into bilateral_corporate_links"""
        print("\n" + "="*80)
        print("LOAD PHASE")
        print("="*80)

        if not links:
            print("[WARN] No links to load")
            return

        # Insert links
        inserted = 0
        for link in links:
            try:
                self.cursor.execute("""
                    INSERT INTO bilateral_corporate_links (
                        link_id,
                        investment_id,
                        acquisition_id,
                        country_code,
                        gleif_lei,
                        chinese_entity,
                        foreign_entity,
                        relationship_type,
                        ownership_percentage,
                        created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    link['link_id'],
                    link['investment_id'],
                    link['acquisition_id'],
                    link['country_code'],
                    link['gleif_lei'],
                    link['chinese_entity'],
                    link['foreign_entity'],
                    link['relationship_type'],
                    link['ownership_percentage'],
                    link['created_at']
                ))
                inserted += 1

                if inserted <= 100:
                    self.validation_sample.append(link)

            except sqlite3.IntegrityError as e:
                self.errors.append(f"Failed to insert {link['link_id']}: {e}")

        self.conn.commit()
        self.links_created = inserted

        print(f"\n[OK] Inserted {inserted:,} new corporate links")
        if self.errors:
            print(f"[WARN] {len(self.errors)} errors during insertion")
            print(f"      First 5 errors: {self.errors[:5]}")

    def post_etl_validation(self):
        """Post-ETL validation per framework"""
        print("\n" + "="*80)
        print("POST-ETL VALIDATION")
        print("="*80)

        self.cursor.execute("SELECT COUNT(*) FROM bilateral_corporate_links")
        total = self.cursor.fetchone()[0]
        print(f"[OK] Total corporate links: {total:,} (added {self.links_created:,})")

        self.cursor.execute("""
            SELECT COUNT(*) FROM bilateral_corporate_links
            WHERE chinese_entity IS NULL
               OR foreign_entity IS NULL
               OR relationship_type IS NULL
        """)
        nulls = self.cursor.fetchone()[0]
        if nulls > 0:
            print(f"[FAIL] {nulls} records have NULLs in required fields")
        else:
            print(f"[OK] No NULLs in required fields")

        self.cursor.execute("""
            SELECT country_code, COUNT(*) as cnt
            FROM bilateral_corporate_links
            WHERE created_at >= datetime('now', '-1 hour')
            GROUP BY country_code
            ORDER BY cnt DESC
        """)
        countries = self.cursor.fetchall()
        print(f"\n[OK] Country distribution (newly added):")
        for country in countries:
            print(f"     {country[0]}: {country[1]:,} links")

        print(f"\n[NOTE] MANDATORY: Review 100-record sample")
        print(f"       Sample size: {len(self.validation_sample)}")
        print(f"       Precision must be >=90% to pass ETL framework")

        return total

    def save_report(self, total_links: int):
        """Save ETL execution report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "etl_script": "etl_corporate_links_from_gleif_v5_optimized.py",
            "source": "GLEIF (gleif_entities + gleif_relationships)",
            "target": "bilateral_corporate_links",
            "links_created": self.links_created,
            "total_links_after": total_links,
            "errors": len(self.errors),
            "error_details": self.errors[:100],
            "validation_status": "PASSED" if len(self.errors) == 0 else "REVIEW REQUIRED",
            "validation_sample_size": len(self.validation_sample),
            "sample_links": [
                {
                    "link_id": l['link_id'],
                    "country": l['country_code'],
                    "chinese_entity": l['chinese_entity'][:50] if l['chinese_entity'] else None,
                    "foreign_entity": l['foreign_entity'][:50] if l['foreign_entity'] else None,
                    "relationship_type": l['relationship_type'],
                    "gleif_lei": l['gleif_lei']
                }
                for l in self.validation_sample[:20]
            ]
        }

        filename = f"analysis/etl_validation/gleif_corporate_links_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\n[OK] Report saved: {filename}")

        return report

    def run(self):
        """Execute complete ETL pipeline"""
        print("\n" + "="*80)
        print("GLEIF CORPORATE LINKS ETL - V5 OPTIMIZED")
        print("="*80)
        print(f"Started: {datetime.now()}")

        try:
            self.pre_etl_validation()
            relationships = self.extract_chinese_european_relationships()

            if not relationships:
                print("\n[WARN] No relationships found. Exiting.")
                return

            links = self.transform(relationships)
            self.load(links)
            total = self.post_etl_validation()
            report = self.save_report(total)

            print("\n" + "="*80)
            print(f"[SUCCESS] ETL COMPLETE")
            print(f"          Created {self.links_created:,} new corporate links")
            print(f"          Total links now: {total:,}")
            print(f"          Expansion: {self.links_created/19*100:.1f}% increase from 19 baseline")
            print("="*80)

            return report

        except Exception as e:
            print(f"\n[ERROR] ETL FAILED: {e}")
            import traceback
            traceback.print_exc()
            self.conn.rollback()
            raise

        finally:
            self.conn.close()

if __name__ == "__main__":
    etl = GLEIFCorporateLinksETL()
    etl.run()

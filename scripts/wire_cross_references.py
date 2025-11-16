#!/usr/bin/env python3
"""
Wire Cross-References - Move 8
Links intelligence reports to underlying data sources (TED, CORDIS, OpenAlex)
"""

import sqlite3
from pathlib import Path
from datetime import datetime
import hashlib

DB_PATH = Path("F:/OSINT_WAREHOUSE/osint_master.db")

class CrossReferenceWirer:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH, timeout=60)
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA synchronous=NORMAL")
        self.conn.commit()
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.wired_count = 0

        print("=" * 80)
        print("CROSS-REFERENCE WIRING - Move 8")
        print("=" * 80)

    def check_current_state(self):
        """Check current state of cross-references"""
        print("\nCurrent state:")

        # Check reports
        self.cursor.execute("SELECT COUNT(*) FROM reports")
        reports_count = self.cursor.fetchone()[0]
        print(f"  Reports: {reports_count:,}")

        # Check existing cross-references
        self.cursor.execute("SELECT COUNT(*) FROM report_cross_references")
        xref_count = self.cursor.fetchone()[0]
        print(f"  Existing cross-references: {xref_count:,}")

        # Check data sources
        self.cursor.execute("SELECT COUNT(*) FROM ted_contracts_production WHERE is_chinese_related = 1")
        ted_count = self.cursor.fetchone()[0]
        print(f"  TED Chinese contracts: {ted_count:,}")

        self.cursor.execute("SELECT COUNT(*) FROM cordis_china_collaborations")
        cordis_count = self.cursor.fetchone()[0]
        print(f"  CORDIS China collaborations: {cordis_count:,}")

        self.cursor.execute("SELECT COUNT(*) FROM openalex_china_deep")
        openalex_count = self.cursor.fetchone()[0]
        print(f"  OpenAlex China research: {openalex_count:,}")

        return reports_count

    def wire_intelligence_to_ted(self):
        """Wire intelligence_procurement records to TED contracts"""
        print("\n1. Wiring intelligence_procurement -> TED contracts...")

        # Get intelligence procurement records
        self.cursor.execute("""
            SELECT DISTINCT
                supplier,
                country
            FROM intelligence_procurement
            WHERE china_related = 1
            LIMIT 50
        """)

        intel_records = self.cursor.fetchall()
        wired = 0

        for record in intel_records:
            if not record['supplier']:
                continue

            # Find matching TED contracts
            self.cursor.execute("""
                SELECT document_id, contractor_name
                FROM ted_contracts_production
                WHERE is_chinese_related = 1
                AND chinese_company_match LIKE ?
                LIMIT 5
            """, (f"%{record['supplier'][:30]}%",))

            ted_matches = self.cursor.fetchall()

            for ted in ted_matches:
                xref_id = hashlib.md5(
                    f"intel_proc_{record['supplier']}_{ted['document_id']}".encode()
                ).hexdigest()[:16]

                try:
                    self.cursor.execute("""
                        INSERT OR IGNORE INTO report_cross_references
                        (xref_id, source_type, source_record_id, reference_type, confidence, validation_notes)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        xref_id,
                        'TED',
                        ted['document_id'],
                        'procurement_evidence',
                        0.85,
                        f"Matched entity: {record['supplier']}"
                    ))
                    wired += 1
                except Exception as e:
                    pass

        self.conn.commit()
        print(f"   [OK] Wired {wired} intelligence_procurement -> TED links")
        self.wired_count += wired
        return wired

    def wire_intelligence_to_cordis(self):
        """Wire intelligence_collaborations to CORDIS projects"""
        print("\n2. Wiring intelligence_collaborations -> CORDIS...")

        # Get intelligence collaboration records
        self.cursor.execute("""
            SELECT DISTINCT
                entity1,
                entity2,
                collaboration_type
            FROM intelligence_collaborations
            LIMIT 50
        """)

        intel_records = self.cursor.fetchall()
        wired = 0

        for record in intel_records:
            entity = record['entity1'] or record['entity2']
            if not entity:
                continue

            # Find matching CORDIS projects
            self.cursor.execute("""
                SELECT project_id, chinese_org_name
                FROM cordis_china_collaborations
                WHERE chinese_org_name LIKE ?
                LIMIT 5
            """, (f"%{entity[:20]}%",))

            cordis_matches = self.cursor.fetchall()

            for cordis in cordis_matches:
                xref_id = hashlib.md5(
                    f"intel_collab_{entity}_{cordis['project_id']}".encode()
                ).hexdigest()[:16]

                try:
                    self.cursor.execute("""
                        INSERT OR IGNORE INTO report_cross_references
                        (xref_id, source_type, source_record_id, reference_type, confidence, validation_notes)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        xref_id,
                        'CORDIS',
                        cordis['project_id'],
                        'research_collaboration',
                        0.90,
                        f"Matched institution: {entity}"
                    ))
                    wired += 1
                except Exception as e:
                    pass

        self.conn.commit()
        print(f"   [OK] Wired {wired} intelligence_collaborations -> CORDIS links")
        self.wired_count += wired
        return wired

    def wire_intelligence_to_openalex(self):
        """Wire intelligence_publications to OpenAlex"""
        print("\n3. Wiring intelligence_publications -> OpenAlex...")

        # Get intelligence publication records
        self.cursor.execute("""
            SELECT DISTINCT
                institution,
                title
            FROM intelligence_publications
            WHERE china_collaboration = 1
            LIMIT 50
        """)

        intel_records = self.cursor.fetchall()
        wired = 0

        for record in intel_records:
            if not record['institution']:
                continue

            # Find matching OpenAlex works
            self.cursor.execute("""
                SELECT id, title
                FROM openalex_china_deep
                WHERE institutions LIKE ?
                LIMIT 5
            """, (f"%{record['institution'][:30]}%",))

            openalex_matches = self.cursor.fetchall()

            for work in openalex_matches:
                xref_id = hashlib.md5(
                    f"intel_pub_{record['institution']}_{work['id']}".encode()
                ).hexdigest()[:16]

                try:
                    self.cursor.execute("""
                        INSERT OR IGNORE INTO report_cross_references
                        (xref_id, source_type, source_record_id, reference_type, confidence, validation_notes)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        xref_id,
                        'OpenAlex',
                        work['id'],
                        'research_publication',
                        0.80,
                        f"Matched institution: {record['institution']}"
                    ))
                    wired += 1
                except Exception as e:
                    pass

        self.conn.commit()
        print(f"   [OK] Wired {wired} intelligence_publications -> OpenAlex links")
        self.wired_count += wired
        return wired

    def generate_summary(self):
        """Generate wiring summary"""
        print("\n" + "=" * 80)
        print("CROSS-REFERENCE WIRING SUMMARY")
        print("=" * 80)

        # Total cross-references
        self.cursor.execute("SELECT COUNT(*) FROM report_cross_references")
        total = self.cursor.fetchone()[0]

        # By source type
        self.cursor.execute("""
            SELECT source_type, COUNT(*) as count
            FROM report_cross_references
            GROUP BY source_type
            ORDER BY count DESC
        """)
        by_source = self.cursor.fetchall()

        # By reference type
        self.cursor.execute("""
            SELECT reference_type, COUNT(*) as count
            FROM report_cross_references
            GROUP BY reference_type
            ORDER BY count DESC
        """)
        by_type = self.cursor.fetchall()

        print(f"\nTotal cross-references: {total:,}")
        print(f"New cross-references wired: {self.wired_count:,}")

        print(f"\nBy source type:")
        for row in by_source:
            print(f"  {row['source_type']}: {row['count']}")

        print(f"\nBy reference type:")
        for row in by_type:
            print(f"  {row['reference_type']}: {row['count']}")

        print("\n" + "=" * 80)

    def run(self):
        """Main wiring workflow"""
        try:
            # Check current state
            reports_count = self.check_current_state()

            if reports_count == 0:
                print("\n[WARNING] No reports found in database")
                print("[INFO] Cross-reference wiring requires intelligence reports")
                print("[INFO] Creating demo cross-references from intelligence tables...")

            # Wire cross-references
            self.wire_intelligence_to_ted()
            self.wire_intelligence_to_cordis()
            self.wire_intelligence_to_openalex()

            # Generate summary
            self.generate_summary()

        finally:
            self.conn.close()

if __name__ == "__main__":
    wirer = CrossReferenceWirer()
    wirer.run()

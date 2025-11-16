#!/usr/bin/env python3
"""
GLEIF Data Quality Validation Script
Comprehensive QA/QC checks for all GLEIF components
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

DB_PATH = Path("F:/OSINT_WAREHOUSE/osint_master.db")

class GLEIFValidator:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH, timeout=60)
        self.issues = defaultdict(list)
        self.stats = {}

    def run_all_validations(self):
        """Run all validation checks"""
        print("=" * 80)
        print("GLEIF DATA QUALITY VALIDATION")
        print("=" * 80)
        print()

        # Basic integrity checks
        self.validate_entities()
        self.validate_relationships()
        self.validate_repex()
        self.validate_bic_mapping()
        self.validate_isin_mapping()
        self.validate_qcc_mapping()
        self.validate_opencorporates_mapping()

        # Cross-reference checks
        self.validate_chinese_entities()
        self.validate_cross_references()

        # Generate report
        self.generate_report()

    def validate_entities(self):
        """Validate gleif_entities table"""
        print("1. VALIDATING ENTITIES TABLE")
        print("-" * 80)

        cur = self.conn.cursor()

        # Basic counts
        cur.execute("SELECT COUNT(*) FROM gleif_entities")
        total = cur.fetchone()[0]
        print(f"   Total entities: {total:,}")
        self.stats['entities_total'] = total

        # Check for NULL LEIs
        cur.execute("SELECT COUNT(*) FROM gleif_entities WHERE lei IS NULL OR lei = ''")
        null_lei = cur.fetchone()[0]
        if null_lei > 0:
            self.issues['entities'].append(f"NULL/empty LEI: {null_lei}")
        print(f"   NULL/empty LEI: {null_lei} {'[OK]' if null_lei == 0 else '[ISSUE] ISSUE'}")

        # Check LEI format (should be 20 characters, alphanumeric)
        cur.execute("""
            SELECT COUNT(*) FROM gleif_entities
            WHERE length(lei) != 20 OR lei GLOB '*[^A-Z0-9]*'
        """)
        invalid_lei = cur.fetchone()[0]
        if invalid_lei > 0:
            self.issues['entities'].append(f"Invalid LEI format: {invalid_lei}")
        print(f"   Invalid LEI format: {invalid_lei} {'[OK]' if invalid_lei == 0 else '[ISSUE] ISSUE'}")

        # Check for duplicate LEIs
        cur.execute("""
            SELECT lei, COUNT(*) as cnt
            FROM gleif_entities
            GROUP BY lei
            HAVING cnt > 1
        """)
        duplicates = cur.fetchall()
        if duplicates:
            self.issues['entities'].append(f"Duplicate LEIs: {len(duplicates)}")
            print(f"   Duplicate LEIs: {len(duplicates)} [ISSUE]")
            for lei, cnt in duplicates[:5]:
                print(f"      {lei}: {cnt} occurrences")
        else:
            print(f"   Duplicate LEIs: 0 [OK]")

        # Check country distribution
        cur.execute("""
            SELECT legal_address_country, COUNT(*) as cnt
            FROM gleif_entities
            WHERE legal_address_country IS NOT NULL
            GROUP BY legal_address_country
            ORDER BY cnt DESC
            LIMIT 10
        """)
        print(f"   Top 10 countries:")
        for country, cnt in cur.fetchall():
            print(f"      {country}: {cnt:,}")

        # Chinese entities breakdown
        cur.execute("""
            SELECT legal_address_country, COUNT(*) as cnt
            FROM gleif_entities
            WHERE legal_address_country IN ('CN', 'HK', 'MO', 'TW')
            GROUP BY legal_address_country
        """)
        chinese_breakdown = cur.fetchall()
        print(f"   Chinese entities:")
        cn_total = 0
        for country, cnt in chinese_breakdown:
            cn_total += cnt
            region = {'CN': 'Mainland', 'HK': 'Hong Kong', 'MO': 'Macau', 'TW': 'Taiwan'}.get(country, country)
            print(f"      {region}: {cnt:,}")
        print(f"      TOTAL: {cn_total:,}")
        self.stats['chinese_entities'] = cn_total

        print()

    def validate_relationships(self):
        """Validate gleif_relationships table"""
        print("2. VALIDATING RELATIONSHIPS TABLE")
        print("-" * 80)

        cur = self.conn.cursor()

        # Basic counts
        cur.execute("SELECT COUNT(*) FROM gleif_relationships")
        total = cur.fetchone()[0]
        print(f"   Total relationships: {total:,}")
        self.stats['relationships_total'] = total

        # Check for NULL values
        cur.execute("""
            SELECT COUNT(*) FROM gleif_relationships
            WHERE child_lei IS NULL OR parent_lei IS NULL
        """)
        null_lei = cur.fetchone()[0]
        if null_lei > 0:
            self.issues['relationships'].append(f"NULL LEI: {null_lei}")
        print(f"   NULL LEI values: {null_lei} {'[OK]' if null_lei == 0 else '[ISSUE] ISSUE'}")

        # Check if child_lei exists in entities table
        cur.execute("""
            SELECT COUNT(*) FROM gleif_relationships r
            WHERE NOT EXISTS (
                SELECT 1 FROM gleif_entities e WHERE e.lei = r.child_lei
            )
        """)
        orphan_children = cur.fetchone()[0]
        if orphan_children > 0:
            self.issues['relationships'].append(f"Child LEIs not in entities: {orphan_children}")
        print(f"   Orphan child LEIs: {orphan_children} {'[OK]' if orphan_children == 0 else '[WARN] WARNING'}")

        # Check if parent_lei exists in entities table
        cur.execute("""
            SELECT COUNT(*) FROM gleif_relationships r
            WHERE NOT EXISTS (
                SELECT 1 FROM gleif_entities e WHERE e.lei = r.parent_lei
            )
        """)
        orphan_parents = cur.fetchone()[0]
        if orphan_parents > 0:
            self.issues['relationships'].append(f"Parent LEIs not in entities: {orphan_parents}")
        print(f"   Orphan parent LEIs: {orphan_parents} {'[OK]' if orphan_parents == 0 else '[WARN] WARNING'}")

        # Relationship type distribution
        cur.execute("""
            SELECT relationship_type, COUNT(*) as cnt
            FROM gleif_relationships
            GROUP BY relationship_type
            ORDER BY cnt DESC
        """)
        print(f"   Relationship types:")
        for rel_type, cnt in cur.fetchall():
            print(f"      {rel_type}: {cnt:,}")

        # Check for circular references (child = parent)
        cur.execute("""
            SELECT COUNT(*) FROM gleif_relationships
            WHERE child_lei = parent_lei
        """)
        circular = cur.fetchone()[0]
        if circular > 0:
            self.issues['relationships'].append(f"Circular references: {circular}")
        print(f"   Circular references (child=parent): {circular} {'[OK]' if circular == 0 else '[ISSUE] ISSUE'}")

        print()

    def validate_repex(self):
        """Validate gleif_repex table"""
        print("3. VALIDATING REPEX TABLE")
        print("-" * 80)

        cur = self.conn.cursor()

        # Basic counts
        cur.execute("SELECT COUNT(*) FROM gleif_repex")
        total = cur.fetchone()[0]
        print(f"   Total REPEX records: {total:,}")
        self.stats['repex_total'] = total

        # Check for duplicates
        cur.execute("""
            SELECT lei, exception_category, COUNT(*) as cnt
            FROM gleif_repex
            GROUP BY lei, exception_category
            HAVING cnt > 1
        """)
        duplicates = cur.fetchall()
        duplicate_count = len(duplicates)
        if duplicate_count > 0:
            total_dupes = sum(cnt - 1 for _, _, cnt in duplicates)
            self.issues['repex'].append(f"Duplicate records: {total_dupes:,} duplicates from {duplicate_count:,} LEI/category pairs")
            print(f"   Duplicate records: {total_dupes:,} [WARN] WARNING (expected from v4+v5 runs)")
            print(f"      Unique LEI/category pairs with dupes: {duplicate_count:,}")

            # Estimate unique records
            cur.execute("""
                SELECT COUNT(DISTINCT lei || '|' || exception_category)
                FROM gleif_repex
            """)
            unique = cur.fetchone()[0]
            print(f"      Estimated unique records: {unique:,}")
            self.stats['repex_unique'] = unique
        else:
            print(f"   Duplicate records: 0 [OK]")
            self.stats['repex_unique'] = total

        # Check LEI format
        cur.execute("""
            SELECT COUNT(*) FROM gleif_repex
            WHERE length(lei) != 20 OR lei GLOB '*[^A-Z0-9]*'
        """)
        invalid_lei = cur.fetchone()[0]
        if invalid_lei > 0:
            self.issues['repex'].append(f"Invalid LEI format: {invalid_lei}")
        print(f"   Invalid LEI format: {invalid_lei} {'[OK]' if invalid_lei == 0 else '[ISSUE] ISSUE'}")

        # Check orphan LEIs
        cur.execute("""
            SELECT COUNT(DISTINCT r.lei) FROM gleif_repex r
            WHERE NOT EXISTS (
                SELECT 1 FROM gleif_entities e WHERE e.lei = r.lei
            )
        """)
        orphan_lei = cur.fetchone()[0]
        if orphan_lei > 0:
            self.issues['repex'].append(f"LEIs not in entities: {orphan_lei}")
        print(f"   Orphan LEIs (not in entities): {orphan_lei} {'[OK]' if orphan_lei == 0 else '[WARN] WARNING'}")

        # Category distribution
        cur.execute("""
            SELECT exception_category, COUNT(*) as cnt
            FROM gleif_repex
            GROUP BY exception_category
            ORDER BY cnt DESC
        """)
        print(f"   Exception categories:")
        for cat, cnt in cur.fetchall():
            print(f"      {cat}: {cnt:,}")

        # Top reasons
        cur.execute("""
            SELECT exception_reason, COUNT(*) as cnt
            FROM gleif_repex
            WHERE exception_reason IS NOT NULL
            GROUP BY exception_reason
            ORDER BY cnt DESC
            LIMIT 10
        """)
        print(f"   Top 10 exception reasons:")
        for reason, cnt in cur.fetchall():
            print(f"      {reason}: {cnt:,}")

        print()

    def validate_bic_mapping(self):
        """Validate gleif_bic_mapping table"""
        print("4. VALIDATING BIC MAPPING TABLE")
        print("-" * 80)

        cur = self.conn.cursor()

        cur.execute("SELECT COUNT(*) FROM gleif_bic_mapping")
        total = cur.fetchone()[0]
        print(f"   Total BIC mappings: {total:,}")
        self.stats['bic_total'] = total

        # Check orphan LEIs
        cur.execute("""
            SELECT COUNT(*) FROM gleif_bic_mapping b
            WHERE NOT EXISTS (
                SELECT 1 FROM gleif_entities e WHERE e.lei = b.lei
            )
        """)
        orphan = cur.fetchone()[0]
        if orphan > 0:
            self.issues['bic'].append(f"LEIs not in entities: {orphan}")
        print(f"   Orphan LEIs: {orphan} {'[OK]' if orphan == 0 else '[WARN] WARNING'}")

        # Check for duplicates
        cur.execute("""
            SELECT lei, COUNT(*) as cnt
            FROM gleif_bic_mapping
            GROUP BY lei
            HAVING cnt > 1
        """)
        duplicates = len(cur.fetchall())
        if duplicates > 0:
            self.issues['bic'].append(f"Duplicate LEIs: {duplicates}")
        print(f"   Duplicate LEIs: {duplicates} {'[OK]' if duplicates == 0 else '[WARN] WARNING'}")

        print()

    def validate_isin_mapping(self):
        """Validate gleif_isin_mapping table"""
        print("5. VALIDATING ISIN MAPPING TABLE")
        print("-" * 80)

        cur = self.conn.cursor()

        cur.execute("SELECT COUNT(*) FROM gleif_isin_mapping")
        total = cur.fetchone()[0]
        print(f"   Total ISIN mappings: {total:,}")
        self.stats['isin_total'] = total

        # Check orphan LEIs
        cur.execute("""
            SELECT COUNT(DISTINCT lei) FROM gleif_isin_mapping i
            WHERE NOT EXISTS (
                SELECT 1 FROM gleif_entities e WHERE e.lei = i.lei
            )
        """)
        orphan = cur.fetchone()[0]
        if orphan > 0:
            self.issues['isin'].append(f"Unique LEIs not in entities: {orphan}")
        print(f"   Orphan LEIs: {orphan} {'[OK]' if orphan == 0 else '[WARN] WARNING'}")

        # Entities with multiple ISINs
        cur.execute("""
            SELECT lei, COUNT(*) as cnt
            FROM gleif_isin_mapping
            GROUP BY lei
            ORDER BY cnt DESC
            LIMIT 5
        """)
        print(f"   Top 5 entities by ISIN count:")
        for lei, cnt in cur.fetchall():
            cur.execute("SELECT legal_name FROM gleif_entities WHERE lei = ?", (lei,))
            name_result = cur.fetchone()
            name = name_result[0] if name_result else "Unknown"
            print(f"      {name[:50]}: {cnt:,} ISINs")

        print()

    def validate_qcc_mapping(self):
        """Validate gleif_qcc_mapping table - CRITICAL FOR CHINA"""
        print("6. VALIDATING QCC MAPPING TABLE (CRITICAL)")
        print("-" * 80)

        cur = self.conn.cursor()

        cur.execute("SELECT COUNT(*) FROM gleif_qcc_mapping")
        total = cur.fetchone()[0]
        print(f"   Total QCC mappings: {total:,}")
        self.stats['qcc_total'] = total

        # Check orphan LEIs
        cur.execute("""
            SELECT COUNT(*) FROM gleif_qcc_mapping q
            WHERE NOT EXISTS (
                SELECT 1 FROM gleif_entities e WHERE e.lei = q.lei
            )
        """)
        orphan = cur.fetchone()[0]
        if orphan > 0:
            self.issues['qcc'].append(f"LEIs not in entities: {orphan}")
        print(f"   Orphan LEIs: {orphan} {'[OK]' if orphan == 0 else '[WARN] WARNING'}")

        # Check how many Chinese entities have QCC mappings
        cur.execute("""
            SELECT COUNT(DISTINCT e.lei)
            FROM gleif_entities e
            JOIN gleif_qcc_mapping q ON e.lei = q.lei
            WHERE e.legal_address_country IN ('CN', 'HK')
        """)
        mapped_chinese = cur.fetchone()[0]

        cur.execute("""
            SELECT COUNT(*)
            FROM gleif_entities
            WHERE legal_address_country IN ('CN', 'HK')
        """)
        total_chinese = cur.fetchone()[0]

        coverage = (mapped_chinese / total_chinese * 100) if total_chinese > 0 else 0
        print(f"   Chinese entities with QCC mapping: {mapped_chinese:,} / {total_chinese:,} ({coverage:.1f}%)")
        self.stats['qcc_chinese_coverage'] = coverage

        if coverage < 50:
            self.issues['qcc'].append(f"Low Chinese coverage: {coverage:.1f}%")
            print(f"      [WARN] WARNING: Coverage below 50%")

        # Check for duplicates
        cur.execute("""
            SELECT lei, COUNT(*) as cnt
            FROM gleif_qcc_mapping
            GROUP BY lei
            HAVING cnt > 1
        """)
        duplicates = len(cur.fetchall())
        if duplicates > 0:
            self.issues['qcc'].append(f"Duplicate LEIs: {duplicates}")
        print(f"   Duplicate LEIs: {duplicates} {'[OK]' if duplicates == 0 else '[WARN] WARNING'}")

        print()

    def validate_opencorporates_mapping(self):
        """Validate gleif_opencorporates_mapping table"""
        print("7. VALIDATING OPENCORPORATES MAPPING TABLE")
        print("-" * 80)

        cur = self.conn.cursor()

        cur.execute("SELECT COUNT(*) FROM gleif_opencorporates_mapping")
        total = cur.fetchone()[0]
        print(f"   Total OpenCorporates mappings: {total:,}")
        self.stats['oc_total'] = total

        # Check orphan LEIs
        cur.execute("""
            SELECT COUNT(*) FROM gleif_opencorporates_mapping o
            WHERE NOT EXISTS (
                SELECT 1 FROM gleif_entities e WHERE e.lei = o.lei
            )
        """)
        orphan = cur.fetchone()[0]
        if orphan > 0:
            self.issues['oc'].append(f"LEIs not in entities: {orphan}")
        print(f"   Orphan LEIs: {orphan} {'[OK]' if orphan == 0 else '[WARN] WARNING'}")

        print()

    def validate_chinese_entities(self):
        """Validate Chinese entity data specifically"""
        print("8. CHINESE ENTITY VALIDATION")
        print("-" * 80)

        cur = self.conn.cursor()

        # Total Chinese entities
        chinese_total = self.stats.get('chinese_entities', 0)
        print(f"   Total Chinese entities: {chinese_total:,}")

        # Chinese entities with relationships
        cur.execute("""
            SELECT COUNT(DISTINCT r.child_lei)
            FROM gleif_relationships r
            JOIN gleif_entities e ON r.child_lei = e.lei
            WHERE e.legal_address_country IN ('CN', 'HK')
        """)
        cn_with_rel = cur.fetchone()[0]
        rel_pct = (cn_with_rel / chinese_total * 100) if chinese_total > 0 else 0
        print(f"   Chinese entities with relationships: {cn_with_rel:,} ({rel_pct:.1f}%)")

        # Chinese entities with REPEX
        cur.execute("""
            SELECT COUNT(DISTINCT r.lei)
            FROM gleif_repex r
            JOIN gleif_entities e ON r.lei = e.lei
            WHERE e.legal_address_country IN ('CN', 'HK')
        """)
        cn_with_repex = cur.fetchone()[0]
        repex_pct = (cn_with_repex / chinese_total * 100) if chinese_total > 0 else 0
        print(f"   Chinese entities with REPEX: {cn_with_repex:,} ({repex_pct:.1f}%)")

        # Chinese entities with QCC
        cn_with_qcc = int(self.stats.get('qcc_chinese_coverage', 0) * chinese_total / 100)
        print(f"   Chinese entities with QCC: {cn_with_qcc:,} ({self.stats.get('qcc_chinese_coverage', 0):.1f}%)")

        # Chinese entities with ISIN
        cur.execute("""
            SELECT COUNT(DISTINCT i.lei)
            FROM gleif_isin_mapping i
            JOIN gleif_entities e ON i.lei = e.lei
            WHERE e.legal_address_country IN ('CN', 'HK')
        """)
        cn_with_isin = cur.fetchone()[0]
        isin_pct = (cn_with_isin / chinese_total * 100) if chinese_total > 0 else 0
        print(f"   Chinese entities with ISIN: {cn_with_isin:,} ({isin_pct:.1f}%)")

        print()

    def validate_cross_references(self):
        """Validate cross-references between tables"""
        print("9. CROSS-REFERENCE VALIDATION")
        print("-" * 80)

        cur = self.conn.cursor()

        # Entities with at least one mapping
        cur.execute("""
            SELECT COUNT(DISTINCT e.lei)
            FROM gleif_entities e
            WHERE EXISTS (
                SELECT 1 FROM gleif_bic_mapping WHERE lei = e.lei
            ) OR EXISTS (
                SELECT 1 FROM gleif_isin_mapping WHERE lei = e.lei
            ) OR EXISTS (
                SELECT 1 FROM gleif_qcc_mapping WHERE lei = e.lei
            ) OR EXISTS (
                SELECT 1 FROM gleif_opencorporates_mapping WHERE lei = e.lei
            )
        """)
        with_mapping = cur.fetchone()[0]
        total_entities = self.stats['entities_total']
        mapping_pct = (with_mapping / total_entities * 100) if total_entities > 0 else 0
        print(f"   Entities with at least one mapping: {with_mapping:,} / {total_entities:,} ({mapping_pct:.1f}%)")

        # Entities with relationships AND mappings
        cur.execute("""
            SELECT COUNT(DISTINCT e.lei)
            FROM gleif_entities e
            WHERE EXISTS (
                SELECT 1 FROM gleif_relationships WHERE child_lei = e.lei OR parent_lei = e.lei
            ) AND EXISTS (
                SELECT 1 FROM gleif_qcc_mapping WHERE lei = e.lei
            )
        """)
        with_both = cur.fetchone()[0]
        print(f"   Entities with both relationships AND QCC mapping: {with_both:,}")

        # Entities with REPEX but no relationships
        cur.execute("""
            SELECT COUNT(DISTINCT r.lei)
            FROM gleif_repex r
            WHERE NOT EXISTS (
                SELECT 1 FROM gleif_relationships rel
                WHERE rel.child_lei = r.lei
            )
        """)
        repex_no_rel = cur.fetchone()[0]
        print(f"   Entities with REPEX but no relationships: {repex_no_rel:,}")
        print(f"      (Expected - REPEX explains why they don't report relationships)")

        print()

    def generate_report(self):
        """Generate final validation report"""
        print("=" * 80)
        print("VALIDATION SUMMARY")
        print("=" * 80)
        print()

        # Count issues by severity
        critical = []
        warnings = []

        for category, issue_list in self.issues.items():
            for issue in issue_list:
                if 'NULL' in issue or 'Invalid' in issue or 'Duplicate LEIs' in issue:
                    critical.append(f"{category}: {issue}")
                else:
                    warnings.append(f"{category}: {issue}")

        if critical:
            print(f"CRITICAL ISSUES: {len(critical)}")
            for issue in critical:
                print(f"   [ISSUE] {issue}")
            print()
        else:
            print("CRITICAL ISSUES: 0 [OK]")
            print()

        if warnings:
            print(f"WARNINGS: {len(warnings)}")
            for issue in warnings:
                print(f"   [WARN] {issue}")
            print()
        else:
            print("WARNINGS: 0 [OK]")
            print()

        # Overall assessment
        print("OVERALL ASSESSMENT:")
        if not critical and not warnings:
            print("   [OK] All validation checks passed")
            print("   [OK] Data quality is excellent")
            print("   [OK] Ready for production use")
        elif not critical:
            print("   [OK] No critical issues found")
            print("   [WARN] Minor warnings present (see above)")
            print("   [OK] Data is usable for analysis")
        else:
            print("   [ISSUE] Critical issues require attention")
            print("   [WARN] Review issues before production use")

        print()

        # Save report to file
        report = {
            'timestamp': datetime.utcnow().isoformat(),
            'stats': self.stats,
            'issues': dict(self.issues),
            'critical_count': len(critical),
            'warning_count': len(warnings)
        }

        report_path = Path("analysis/GLEIF_VALIDATION_REPORT_20251030.json")
        report_path.parent.mkdir(exist_ok=True)
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"Detailed report saved to: {report_path}")
        print()

    def close(self):
        """Close database connection"""
        self.conn.close()

if __name__ == "__main__":
    validator = GLEIFValidator()
    try:
        validator.run_all_validations()
    finally:
        validator.close()

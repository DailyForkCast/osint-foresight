#!/usr/bin/env python3
"""
Check the impact of database lock errors during concurrent processing
"""
import sqlite3
from pathlib import Path

DB_PATH = Path("F:/OSINT_WAREHOUSE/osint_master.db")

def check_database_status():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("="*80)
    print("DATABASE LOCK IMPACT ANALYSIS")
    print("="*80)

    # Check USPTO CPC data
    print("\n1. USPTO CPC CLASSIFICATIONS:")
    total_cpc = cursor.execute("SELECT COUNT(*) FROM uspto_cpc_classifications").fetchone()[0]
    print(f"   Total records in database: {total_cpc:,}")

    strategic_cpc = cursor.execute("""
        SELECT COUNT(*) FROM uspto_cpc_classifications
        WHERE is_strategic = 1
    """).fetchone()[0]
    print(f"   Strategic technology records: {strategic_cpc:,}")

    # Expected vs actual
    expected_total = 65_590_414
    expected_strategic = 14_154_434

    print(f"\n   Expected total: {expected_total:,}")
    print(f"   Missing records: {expected_total - total_cpc:,} ({(expected_total - total_cpc) / expected_total * 100:.3f}%)")

    print(f"\n   Expected strategic: {expected_strategic:,}")
    print(f"   Missing strategic: {expected_strategic - strategic_cpc:,} ({(expected_strategic - strategic_cpc) / expected_strategic * 100:.3f}%)")

    # Check GLEIF data
    print("\n2. GLEIF ENTITIES:")
    total_entities = cursor.execute("SELECT COUNT(*) FROM gleif_entities").fetchone()[0]
    print(f"   Total entities in database: {total_entities:,}")

    expected_entities = 3_086_233
    print(f"   Expected entities: {expected_entities:,}")
    print(f"   Missing entities: {expected_entities - total_entities:,} ({(expected_entities - total_entities) / expected_entities * 100:.3f}%)")

    # Check China entities
    cn_entities = cursor.execute("""
        SELECT COUNT(*) FROM gleif_entities
        WHERE legal_address_country = 'CN'
    """).fetchone()[0]
    print(f"   Mainland China entities: {cn_entities:,}")

    hk_entities = cursor.execute("""
        SELECT COUNT(*) FROM gleif_entities
        WHERE legal_address_country = 'HK'
    """).fetchone()[0]
    print(f"   Hong Kong entities: {hk_entities:,}")

    # Check GLEIF relationships
    print("\n3. GLEIF RELATIONSHIPS:")
    total_relationships = cursor.execute("SELECT COUNT(*) FROM gleif_relationships").fetchone()[0]
    print(f"   Total relationships in database: {total_relationships:,}")

    expected_relationships = 464_565
    print(f"   Expected relationships: {expected_relationships:,}")
    print(f"   Missing relationships: {expected_relationships - total_relationships:,} ({(expected_relationships - total_relationships) / expected_relationships * 100:.3f}%)")

    # Check relationship types
    rel_types = cursor.execute("""
        SELECT relationship_type, COUNT(*) as cnt
        FROM gleif_relationships
        WHERE relationship_type != ''
        GROUP BY relationship_type
        ORDER BY cnt DESC
    """).fetchall()

    if rel_types:
        print("\n   Relationship types:")
        for rel_type, cnt in rel_types:
            print(f"     - {rel_type}: {cnt:,}")

    # Database file size
    db_size_gb = DB_PATH.stat().st_size / (1024**3)
    print(f"\n4. DATABASE FILE SIZE:")
    print(f"   {db_size_gb:.2f} GB")

    print("\n" + "="*80)
    print("CONCLUSION:")
    print("="*80)

    total_errors = 45 + 242  # USPTO + GLEIF errors
    total_expected = expected_total + expected_entities + expected_relationships
    total_actual = total_cpc + total_entities + total_relationships
    missing = total_expected - total_actual

    print(f"Total database lock errors: {total_errors}")
    print(f"Total records missing: {missing:,}")
    print(f"Overall data loss: {missing / total_expected * 100:.3f}%")

    if missing / total_expected < 0.01:
        print("\n✅ MINIMAL IMPACT - Data loss is negligible (<1%)")
    elif missing / total_expected < 0.05:
        print("\n⚠️  MINOR IMPACT - Data loss is acceptable (<5%)")
    else:
        print("\n❌ SIGNIFICANT IMPACT - Should consider reprocessing")

    conn.close()

if __name__ == "__main__":
    check_database_status()

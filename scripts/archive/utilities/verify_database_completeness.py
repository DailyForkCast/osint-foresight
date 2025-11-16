#!/usr/bin/env python3
"""
Comprehensive verification of database contents after concurrent processing
Checks for data loss due to database lock errors
"""
import sqlite3
from pathlib import Path
import json

DB_PATH = Path("F:/OSINT_WAREHOUSE/osint_master.db")

def verify_database():
    print("="*80)
    print("COMPREHENSIVE DATABASE VERIFICATION")
    print("="*80)

    conn = sqlite3.connect(DB_PATH, timeout=30)
    cursor = conn.cursor()

    results = {
        'timestamp': '2025-10-11',
        'database_size_gb': DB_PATH.stat().st_size / (1024**3),
        'issues': []
    }

    # 1. CHECK USPTO CPC DATA
    print("\n1. USPTO CPC CLASSIFICATIONS")
    print("-" * 80)

    total_cpc = cursor.execute("SELECT COUNT(*) FROM uspto_cpc_classifications").fetchone()[0]
    print(f"   Total CPC records: {total_cpc:,}")

    strategic_cpc = cursor.execute("""
        SELECT COUNT(*) FROM uspto_cpc_classifications
        WHERE is_strategic = 1
    """).fetchone()[0]
    print(f"   Strategic tech records: {strategic_cpc:,}")

    # Check by technology area
    print("\n   Top strategic technology areas:")
    tech_areas = cursor.execute("""
        SELECT strategic_area, COUNT(*) as cnt
        FROM uspto_cpc_classifications
        WHERE is_strategic = 1
        GROUP BY strategic_area
        ORDER BY cnt DESC
        LIMIT 10
    """).fetchall()

    for area, cnt in tech_areas:
        print(f"     - {area}: {cnt:,}")

    # Expected vs actual
    expected_cpc_total = 65_590_414
    expected_cpc_strategic = 14_154_434

    cpc_loss = expected_cpc_total - total_cpc
    cpc_loss_pct = (cpc_loss / expected_cpc_total * 100) if expected_cpc_total > 0 else 0

    print(f"\n   Expected total: {expected_cpc_total:,}")
    print(f"   Missing: {cpc_loss:,} ({cpc_loss_pct:.4f}%)")

    if cpc_loss_pct > 1.0:
        results['issues'].append({
            'category': 'USPTO_CPC',
            'severity': 'HIGH',
            'message': f'Missing {cpc_loss:,} CPC records ({cpc_loss_pct:.2f}%)'
        })
    elif cpc_loss_pct > 0.1:
        results['issues'].append({
            'category': 'USPTO_CPC',
            'severity': 'MEDIUM',
            'message': f'Missing {cpc_loss:,} CPC records ({cpc_loss_pct:.4f}%)'
        })
    else:
        print("   ✅ CPC data is complete (loss < 0.1%)")

    results['uspto_cpc'] = {
        'total': total_cpc,
        'strategic': strategic_cpc,
        'expected_total': expected_cpc_total,
        'missing': cpc_loss,
        'loss_pct': cpc_loss_pct
    }

    # 2. CHECK GLEIF ENTITIES
    print("\n2. GLEIF ENTITIES")
    print("-" * 80)

    total_entities = cursor.execute("SELECT COUNT(*) FROM gleif_entities").fetchone()[0]
    print(f"   Total entities: {total_entities:,}")

    # By country
    print("\n   Top 10 countries:")
    top_countries = cursor.execute("""
        SELECT legal_address_country, COUNT(*) as cnt
        FROM gleif_entities
        WHERE legal_address_country IS NOT NULL AND legal_address_country != ''
        GROUP BY legal_address_country
        ORDER BY cnt DESC
        LIMIT 10
    """).fetchall()

    for country, cnt in top_countries:
        print(f"     - {country}: {cnt:,}")

    # China-specific
    cn_entities = cursor.execute("""
        SELECT COUNT(*) FROM gleif_entities WHERE legal_address_country = 'CN'
    """).fetchone()[0]
    hk_entities = cursor.execute("""
        SELECT COUNT(*) FROM gleif_entities WHERE legal_address_country = 'HK'
    """).fetchone()[0]

    print(f"\n   Mainland China (CN): {cn_entities:,}")
    print(f"   Hong Kong (HK): {hk_entities:,}")

    expected_entities = 3_086_233
    entity_loss = expected_entities - total_entities
    entity_loss_pct = (entity_loss / expected_entities * 100) if expected_entities > 0 else 0

    print(f"\n   Expected total: {expected_entities:,}")
    print(f"   Missing: {entity_loss:,} ({entity_loss_pct:.4f}%)")

    if entity_loss_pct > 1.0:
        results['issues'].append({
            'category': 'GLEIF_ENTITIES',
            'severity': 'HIGH',
            'message': f'Missing {entity_loss:,} entities ({entity_loss_pct:.2f}%)'
        })
    elif entity_loss_pct > 0.1:
        results['issues'].append({
            'category': 'GLEIF_ENTITIES',
            'severity': 'MEDIUM',
            'message': f'Missing {entity_loss:,} entities ({entity_loss_pct:.4f}%)'
        })
    else:
        print("   ✅ Entity data is complete (loss < 0.1%)")

    results['gleif_entities'] = {
        'total': total_entities,
        'china_cn': cn_entities,
        'hong_kong_hk': hk_entities,
        'expected_total': expected_entities,
        'missing': entity_loss,
        'loss_pct': entity_loss_pct
    }

    # 3. CHECK GLEIF RELATIONSHIPS
    print("\n3. GLEIF RELATIONSHIPS")
    print("-" * 80)

    total_relationships = cursor.execute("SELECT COUNT(*) FROM gleif_relationships").fetchone()[0]
    print(f"   Total relationships: {total_relationships:,}")

    # Check relationship types
    rel_types = cursor.execute("""
        SELECT relationship_type, COUNT(*) as cnt
        FROM gleif_relationships
        WHERE relationship_type IS NOT NULL AND relationship_type != ''
        GROUP BY relationship_type
        ORDER BY cnt DESC
    """).fetchall()

    if rel_types:
        print("\n   Relationship types:")
        for rel_type, cnt in rel_types:
            print(f"     - {rel_type}: {cnt:,}")
    else:
        print("\n   ⚠️  No valid relationship types found!")

    expected_relationships = 464_565
    rel_loss = expected_relationships - total_relationships
    rel_loss_pct = (rel_loss / expected_relationships * 100) if expected_relationships > 0 else 0

    print(f"\n   Expected total: {expected_relationships:,}")
    print(f"   Missing: {rel_loss:,} ({rel_loss_pct:.2f}%)")

    if rel_loss_pct > 90.0:
        results['issues'].append({
            'category': 'GLEIF_RELATIONSHIPS',
            'severity': 'CRITICAL',
            'message': f'Missing {rel_loss:,} relationships ({rel_loss_pct:.2f}%) - NEEDS REPROCESSING'
        })
        print("   ❌ CRITICAL: Relationship data is incomplete - needs reprocessing")
    elif rel_loss_pct > 10.0:
        results['issues'].append({
            'category': 'GLEIF_RELATIONSHIPS',
            'severity': 'HIGH',
            'message': f'Missing {rel_loss:,} relationships ({rel_loss_pct:.2f}%)'
        })
    elif rel_loss_pct > 1.0:
        results['issues'].append({
            'category': 'GLEIF_RELATIONSHIPS',
            'severity': 'MEDIUM',
            'message': f'Missing {rel_loss:,} relationships ({rel_loss_pct:.2f}%)'
        })
    else:
        print("   ✅ Relationship data is complete")

    results['gleif_relationships'] = {
        'total': total_relationships,
        'expected_total': expected_relationships,
        'missing': rel_loss,
        'loss_pct': rel_loss_pct,
        'has_valid_types': len(rel_types) > 0
    }

    # 4. CHECK OTHER GLEIF TABLES
    print("\n4. OTHER GLEIF TABLES")
    print("-" * 80)

    # Check if other GLEIF tables exist and have data
    other_tables = [
        'gleif_qcc_mapping',
        'gleif_isin_mapping',
        'gleif_bic_mapping',
        'gleif_opencorporates_mapping',
        'gleif_repex'
    ]

    for table in other_tables:
        try:
            count = cursor.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            print(f"   {table}: {count:,} records")
            results[table] = count
        except sqlite3.OperationalError:
            print(f"   {table}: Table does not exist")
            results[table] = None

    # 5. DATABASE HEALTH
    print("\n5. DATABASE HEALTH")
    print("-" * 80)
    print(f"   Database file size: {results['database_size_gb']:.2f} GB")

    # Check for integrity
    integrity = cursor.execute("PRAGMA integrity_check").fetchone()[0]
    print(f"   Integrity check: {integrity}")
    results['integrity'] = integrity

    # 6. SUMMARY
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)

    if len(results['issues']) == 0:
        print("✅ ALL DATA COMPLETE - No significant data loss detected")
    else:
        print(f"⚠️  FOUND {len(results['issues'])} ISSUE(S):\n")
        for i, issue in enumerate(results['issues'], 1):
            severity_symbol = {
                'CRITICAL': '❌',
                'HIGH': '⚠️ ',
                'MEDIUM': '⚠️ ',
                'LOW': 'ℹ️ '
            }.get(issue['severity'], '•')
            print(f"   {i}. {severity_symbol} [{issue['severity']}] {issue['category']}")
            print(f"      {issue['message']}")

    # Save results
    output_file = Path("analysis/database_verification_results.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nDetailed results saved to: {output_file}")
    print("="*80)

    conn.close()
    return results

if __name__ == "__main__":
    verify_database()

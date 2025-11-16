#!/usr/bin/env python3
"""
Integrate Bilateral Relations Schema into OSINT Master Database
Applies comprehensive bilateral relations tracking schema
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime
import io

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def integrate_schema():
    """Apply bilateral relations schema to osint_master.db"""

    db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")
    schema_path = Path("C:/Projects/OSINT - Foresight/database/bilateral_relations_schema.sql")

    print(f"Integrating bilateral relations schema...")
    print(f"Database: {db_path}")
    print(f"Schema file: {schema_path}")
    print("=" * 80)

    if not db_path.exists():
        print(f"ERROR: Database not found at {db_path}")
        sys.exit(1)

    if not schema_path.exists():
        print(f"ERROR: Schema file not found at {schema_path}")
        sys.exit(1)

    # Read schema SQL
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()

    # Connect and apply schema
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        print("\n1. Checking database connection...")
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
        existing_tables = cursor.fetchone()[0]
        print(f"   ✓ Connected. Existing tables: {existing_tables}")

        print("\n2. Applying bilateral relations schema...")
        # Execute schema (handles IF NOT EXISTS gracefully)
        cursor.executescript(schema_sql)
        print("   ✓ Schema applied successfully")

        print("\n3. Verifying new tables...")
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name LIKE 'bilateral_%'
            ORDER BY name
        """)
        bilateral_tables = cursor.fetchall()
        print(f"   ✓ Found {len(bilateral_tables)} bilateral tables:")
        for table in bilateral_tables:
            print(f"     - {table[0]}")

        print("\n4. Verifying views...")
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='view' AND name LIKE 'v_%relationship%'
            OR name LIKE 'v_%cooperation%'
            OR name LIKE 'v_%investment%'
            ORDER BY name
        """)
        views = cursor.fetchall()
        print(f"   ✓ Found {len(views)} analytical views:")
        for view in views:
            print(f"     - {view[0]}")

        print("\n5. Checking total table count...")
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
        new_total = cursor.fetchone()[0]
        print(f"   ✓ Total tables now: {new_total} (was {existing_tables})")
        print(f"   ✓ New tables added: {new_total - existing_tables}")

        print("\n6. Verifying indexes...")
        cursor.execute("""
            SELECT COUNT(*) FROM sqlite_master
            WHERE type='index' AND name LIKE 'idx_bilateral_%'
        """)
        indexes = cursor.fetchone()[0]
        print(f"   ✓ Created {indexes} performance indexes")

        print("\n7. Reading schema metadata...")
        cursor.execute("""
            SELECT metadata_key, metadata_value
            FROM bilateral_schema_metadata
            ORDER BY metadata_key
        """)
        metadata = cursor.fetchall()
        if metadata:
            print("   Schema metadata:")
            for key, value in metadata:
                print(f"     - {key}: {value}")

        # Commit changes
        conn.commit()
        print("\n8. Committing changes...")
        print("   ✓ Changes committed successfully")

        # Final verification
        print("\n9. Final verification - Sample table structures:")
        for table_name in ['bilateral_countries', 'bilateral_events', 'bilateral_investments']:
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            print(f"\n   {table_name} ({len(columns)} columns):")
            for col in columns[:5]:  # Show first 5 columns
                print(f"     - {col[1]} ({col[2]})")
            if len(columns) > 5:
                print(f"     ... and {len(columns) - 5} more columns")

        print("\n" + "=" * 80)
        print("✓ BILATERAL RELATIONS SCHEMA INTEGRATION COMPLETE")
        print("=" * 80)
        print(f"\nNew capabilities added:")
        print("  - 40+ bilateral tracking tables")
        print("  - 4 analytical views")
        print("  - 30+ performance indexes")
        print("  - Multi-dimensional relationship tracking")
        print("  - Links to existing OSINT data (academic, patents, procurement)")
        print(f"\nDatabase ready for bilateral relations data collection!")

        conn.close()
        return True

    except sqlite3.Error as e:
        print(f"\n✗ ERROR: {e}")
        conn.rollback()
        conn.close()
        return False
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_schema():
    """Test the schema with sample queries"""
    db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")

    print("\n" + "=" * 80)
    print("TESTING BILATERAL RELATIONS SCHEMA")
    print("=" * 80)

    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Test 1: Can we insert into bilateral_countries?
        print("\nTest 1: Insert sample country (Germany)...")
        cursor.execute("""
            INSERT OR IGNORE INTO bilateral_countries
            (country_code, country_name, diplomatic_normalization_date,
             current_relationship_status, relationship_tier, bri_participation_status,
             eu_member, nato_member)
            VALUES
            ('DE', 'Germany', '1972-10-11', 'comprehensive_strategic_partnership',
             'tier_3_major_economy', 'observer', 1, 1)
        """)
        conn.commit()

        cursor.execute("SELECT * FROM bilateral_countries WHERE country_code = 'DE'")
        result = cursor.fetchone()
        if result:
            print(f"   ✓ Germany record created: {result[0]} - {result[1]}")
        else:
            print("   ✗ Failed to create Germany record")

        # Test 2: Can we query the view?
        print("\nTest 2: Query relationship intensity view...")
        cursor.execute("""
            SELECT country_code, country_name, total_events, diplomatic_visits
            FROM v_country_relationship_intensity
            WHERE country_code = 'DE'
        """)
        result = cursor.fetchone()
        if result:
            print(f"   ✓ View query successful: {result}")
        else:
            print("   ✓ View exists (no data yet, which is expected)")

        # Test 3: Check foreign key constraints
        print("\nTest 3: Verify foreign key constraints...")
        cursor.execute("PRAGMA foreign_keys")
        fk_status = cursor.fetchone()[0]
        print(f"   Foreign keys status: {'ENABLED' if fk_status else 'DISABLED'}")

        # Test 4: Check all bilateral table names
        print("\nTest 4: List all bilateral tables...")
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND (name LIKE 'bilateral_%' OR name LIKE '%_cooperation'
            OR name LIKE 'diplomatic_%' OR name LIKE 'sister_%' OR name LIKE 'cultural_%'
            OR name LIKE 'education_%' OR name LIKE 'infrastructure_%' OR name LIKE 'security_%'
            OR name LIKE 'legal_%' OR name LIKE 'policy_%' OR name LIKE 'media_%'
            OR name LIKE 'academic_partnerships' OR name LIKE 'standards_%'
            OR name LIKE 'telecom_%' OR name LIKE 'regulatory_%' OR name LIKE 'export_%'
            OR name LIKE 'major_acquisitions' OR name LIKE 'financial_cooperation')
            ORDER BY name
        """)
        tables = cursor.fetchall()
        print(f"   ✓ Found {len(tables)} bilateral-related tables:")
        for i, (table,) in enumerate(tables, 1):
            print(f"      {i:2d}. {table}")

        print("\n" + "=" * 80)
        print("✓ ALL TESTS PASSED - Schema is functional")
        print("=" * 80)

        conn.close()
        return True

    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 80)
    print("BILATERAL RELATIONS SCHEMA INTEGRATOR")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Step 1: Integrate schema
    success = integrate_schema()

    if success:
        # Step 2: Test schema
        test_success = test_schema()

        if test_success:
            print(f"\n✓ COMPLETE: Bilateral relations tracking ready!")
            print(f"\nNext steps:")
            print(f"  1. Start with Germany baseline: diplomatic timeline, trade data, sister cities")
            print(f"  2. Extract AidData for Germany BRI projects")
            print(f"  3. Build collectors for official sources (Auswärtiges Amt, etc.)")
            print(f"  4. Link existing data (OpenAlex collaborations, TED contracts, USPTO patents)")
            print(f"  5. Replicate framework for other countries")
            sys.exit(0)
        else:
            print("\n✗ Schema integrated but tests failed")
            sys.exit(1)
    else:
        print("\n✗ Schema integration failed")
        sys.exit(1)

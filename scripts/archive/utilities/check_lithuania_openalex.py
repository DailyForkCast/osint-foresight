"""
Check OpenAlex data for Lithuania
Validate academic collaboration patterns with China (2019-2023)
"""

import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')

db = sqlite3.connect('F:/OSINT_WAREHOUSE/osint_master.db')
cursor = db.cursor()

print('='*100)
print('LITHUANIA OPENALEX DATA AVAILABILITY CHECK')
print('='*100)
print()

# Check for Lithuanian institutions
print('STEP 1: LITHUANIAN INSTITUTIONS IN DATABASE')
print('-'*100)
cursor.execute("""
    SELECT COUNT(*)
    FROM openalex_institutions
    WHERE country_code = 'LT'
""")
lt_institutions = cursor.fetchone()[0]
print(f"Lithuanian institutions (country_code = 'LT'): {lt_institutions:,}")

if lt_institutions > 0:
    cursor.execute("""
        SELECT
            institution_id,
            display_name,
            country_code,
            type,
            works_count,
            cited_by_count
        FROM openalex_institutions
        WHERE country_code = 'LT'
        ORDER BY works_count DESC
        LIMIT 10
    """)
    print("\nTop 10 Lithuanian institutions by works count:")
    print(f"{'Institution':<50} {'Type':<20} {'Works':<10} {'Citations':<15}")
    print('-'*100)
    for row in cursor.fetchall():
        inst_id, name, country, inst_type, works, citations = row
        print(f"{name[:48]:<50} {inst_type:<20} {works:<10,} {citations:<15,}")
    print()

# Check for works with Lithuanian institutions
print('STEP 2: WORKS WITH LITHUANIAN INSTITUTIONS')
print('-'*100)
cursor.execute("""
    SELECT COUNT(DISTINCT w.work_id)
    FROM openalex_works w
    JOIN openalex_institutions i ON w.institution_id = i.institution_id
    WHERE i.country_code = 'LT'
""")
lt_works = cursor.fetchone()[0]
print(f"Works from Lithuanian institutions: {lt_works:,}")
print()

if lt_works > 0:
    # Check Lithuania-China collaborations
    print('STEP 3: LITHUANIA-CHINA COLLABORATIONS')
    print('-'*100)
    cursor.execute("""
        SELECT
            strftime('%Y', w.publication_date) as year,
            COUNT(DISTINCT w.work_id) as works
        FROM openalex_works w
        WHERE w.work_id IN (
            SELECT w1.work_id
            FROM openalex_works w1
            JOIN openalex_institutions i1 ON w1.institution_id = i1.institution_id
            WHERE i1.country_code = 'LT'
            INTERSECT
            SELECT w2.work_id
            FROM openalex_works w2
            JOIN openalex_institutions i2 ON w2.institution_id = i2.institution_id
            WHERE i2.country_code = 'CN'
        )
        AND year IS NOT NULL
        GROUP BY year
        ORDER BY year
    """)
    collab_data = cursor.fetchall()
    if collab_data:
        print("Lithuania-China co-authored works by year:")
        print(f"{'Year':<6} {'Works':<10}")
        print('-'*20)
        for year, works in collab_data:
            print(f"{year:<6} {works:<10,}")
    else:
        print("No Lithuania-China collaborations found in current data")
    print()

else:
    print("No works from Lithuanian institutions in current database")
    print()

# Check if we have works table at all
print('STEP 4: OVERALL DATABASE STATUS')
print('-'*100)
cursor.execute("SELECT COUNT(*) FROM openalex_works")
total_works = cursor.fetchone()[0]
print(f"Total works in database: {total_works:,}")

cursor.execute("SELECT COUNT(*) FROM openalex_institutions")
total_institutions = cursor.fetchone()[0]
print(f"Total institutions in database: {total_institutions:,}")

cursor.execute("""
    SELECT country_code, COUNT(*) as count
    FROM openalex_institutions
    WHERE country_code IS NOT NULL
    GROUP BY country_code
    ORDER BY count DESC
    LIMIT 20
""")
print("\nTop 20 countries by institution count:")
print(f"{'Country':<10} {'Institutions':<15}")
print('-'*30)
for country, count in cursor.fetchall():
    print(f"{country:<10} {count:<15,}")
print()

print('='*100)
print('NEXT STEPS')
print('='*100)
if lt_institutions == 0:
    print("\n1. Need to collect OpenAlex data for Lithuania")
    print("   - Option A: OpenAlex API (free, requires API requests)")
    print("   - Option B: OpenAlex snapshot (Kaggle dataset)")
    print("   - Recommended: API collection for Lithuania institutions + works")
    print()
    print("2. Once Lithuania data available:")
    print("   - Query Lithuania-China co-authorships by year (2019-2023)")
    print("   - Compare to GDELT timeline (December 2021 peak)")
    print("   - Cross-reference with trade data patterns")
else:
    print("\n1. Lithuania data available - proceeding with collaboration analysis")
    print("2. Extract temporal patterns")
    print("3. Cross-reference with GDELT and trade data")
print()
print('='*100)

db.close()

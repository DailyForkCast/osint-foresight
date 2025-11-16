#!/usr/bin/env python3
"""
Query and Display Compliant Institutional Data

Shows what we ACTUALLY have in the database (verified facts only)
"""

import sqlite3
import json

def query_compliant_data():
    """Display current compliant institutional data"""

    print("=" * 70)
    print("COMPLIANT INSTITUTIONAL DATA - CURRENT STATUS")
    print("=" * 70)
    print()

    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Show institutions
    print("TIER 1: VERIFIED INSTITUTIONS")
    print("=" * 70)
    print()

    cursor.execute('''
        SELECT institution_name, institution_name_native, institution_type,
               official_website, china_relevance, us_relevance, tech_relevance,
               notes
        FROM european_institutions
        WHERE country_code = 'DE' AND jurisdiction_level = 'national'
        ORDER BY institution_name
    ''')

    for row in cursor.fetchall():
        name, name_native, inst_type, url, china_rel, us_rel, tech_rel, notes = row

        print(f"Institution: {name}")
        print(f"  Native Name: {name_native}")
        print(f"  Type: {inst_type}")
        print(f"  URL: {url}")
        print()
        print(f"  Analytical Fields (Properly NULL):")
        print(f"    China Relevance: {china_rel if china_rel else 'NULL (not fabricated)'}")
        print(f"    US Relevance: {us_rel if us_rel else 'NULL (not fabricated)'}")
        print(f"    Tech Relevance: {tech_rel if tech_rel else 'NULL (not fabricated)'}")
        print()

        if notes:
            try:
                notes_obj = json.loads(notes)
                if 'collection_date' in notes_obj:
                    print(f"  Collection Date: {notes_obj['collection_date']}")
                if 'collection_method' in notes_obj:
                    print(f"  Collection Method: {notes_obj['collection_method']}")
                if 'not_collected' in notes_obj:
                    print(f"  Not Collected (Properly Marked):")
                    for key, value in notes_obj['not_collected'].items():
                        if '[NOT COLLECTED' in value:
                            print(f"    - {key}: {value[:80]}...")
            except:
                pass

        print()
        print("-" * 70)
        print()

    # Count summary
    cursor.execute('''
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN china_relevance IS NULL THEN 1 ELSE 0 END) as null_china,
            SUM(CASE WHEN us_relevance IS NULL THEN 1 ELSE 0 END) as null_us,
            SUM(CASE WHEN tech_relevance IS NULL THEN 1 ELSE 0 END) as null_tech
        FROM european_institutions
        WHERE country_code = 'DE' AND jurisdiction_level = 'national'
    ''')

    total, null_china, null_us, null_tech = cursor.fetchone()

    print("=" * 70)
    print("ZERO FABRICATION COMPLIANCE METRICS")
    print("=" * 70)
    print()
    print(f"Total Institutions: {total}")
    print()
    print(f"Analytical Fields Properly NULL (not fabricated):")
    print(f"  China Relevance NULL: {null_china}/{total} ({100*null_china//total if total > 0 else 0}%)")
    print(f"  US Relevance NULL: {null_us}/{total} ({100*null_us//total if total > 0 else 0}%)")
    print(f"  Tech Relevance NULL: {null_tech}/{total} ({100*null_tech//total if total > 0 else 0}%)")
    print()

    if null_china == total and null_us == total and null_tech == total:
        print("+ COMPLIANCE STATUS: PASSED")
        print("+ All analytical fields properly NULL")
        print("+ No fabricated data detected")
    else:
        print("WARNING: Fabricated data detected")
        print(f"  {total - null_china} institutions have fabricated china_relevance")
        print(f"  {total - null_us} institutions have fabricated us_relevance")
        print(f"  {total - null_tech} institutions have fabricated tech_relevance")

    print()

    # Check personnel
    cursor.execute('''
        SELECT COUNT(*) FROM institutional_personnel p
        JOIN european_institutions i ON p.institution_id = i.institution_id
        WHERE i.country_code = 'DE'
    ''')
    personnel_count = cursor.fetchone()[0]

    print("TIER 2: PERSONNEL (From Official Biographies)")
    print("=" * 70)
    print(f"Records: {personnel_count}")
    if personnel_count == 0:
        print("Status: [NOT YET COLLECTED]")
        print("Next Step: Build Tier 2 collector with official bio sources")
    print()

    # Check publications
    cursor.execute('''
        SELECT COUNT(*) FROM institutional_publications p
        JOIN european_institutions i ON p.institution_id = i.institution_id
        WHERE i.country_code = 'DE'
    ''')
    pub_count = cursor.fetchone()[0]

    print("TIER 3: PUBLICATIONS (From Official Press Releases)")
    print("=" * 70)
    print(f"Records: {pub_count}")
    if pub_count == 0:
        print("Status: [NOT YET COLLECTED]")
        print("Next Step: Build press release scraper with URL tracking")
    print()

    # Check assessments
    cursor.execute('''
        SELECT COUNT(*) FROM institutional_intelligence i
        JOIN european_institutions e ON i.institution_id = e.institution_id
        WHERE e.country_code = 'DE'
    ''')
    assess_count = cursor.fetchone()[0]

    print("TIER 4: INTELLIGENCE ASSESSMENTS (Analytical)")
    print("=" * 70)
    print(f"Records: {assess_count}")
    if assess_count == 0:
        print("Status: [NOT YET CREATED]")
        print("Next Step: Build analytical framework FROM collected data")
    print()

    conn.close()

if __name__ == '__main__':
    query_compliant_data()

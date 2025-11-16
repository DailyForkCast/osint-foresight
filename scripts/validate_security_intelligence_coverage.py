#!/usr/bin/env python3
"""Validate Military and Intelligence Agency Coverage"""
import sqlite3

def validate_security_intel():
    print("=" * 80)
    print("MILITARY & INTELLIGENCE AGENCY COVERAGE VALIDATION")
    print("=" * 80)
    print()

    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Intelligence agencies
    cursor.execute('''
        SELECT country_code, institution_name, official_website
        FROM european_institutions
        WHERE jurisdiction_level = "national"
        AND (
            LOWER(institution_name) LIKE '%intelligence%'
            OR LOWER(institution_name) LIKE '%security service%'
            OR LOWER(institution_name) LIKE '%mi5%'
            OR LOWER(institution_name) LIKE '%mi6%'
            OR LOWER(institution_name) LIKE '%gchq%'
            OR LOWER(institution_name) LIKE '%nachrichtendienst%'
            OR LOWER(institution_name) LIKE '%renseignement%'
            OR LOWER(institution_name) LIKE '%zpravodajstv%'
            OR LOWER(institution_name) LIKE '%etterretningstjenesten%'
            OR LOWER(institution_name) LIKE '%informační služba%'
            OR LOWER(institution_name) LIKE '%obavještajno%'
            OR LOWER(institution_name) LIKE '%bezpečnostní%'
        )
        ORDER BY country_code
    ''')

    intel_agencies = cursor.fetchall()

    print("INTELLIGENCE & SECURITY AGENCIES:")
    print(f"Total: {len(intel_agencies)}")
    print()

    for row in intel_agencies:
        print(f"  [{row[0]}] {row[1]}")
        print(f"       {row[2]}")
        print()

    # Defence ministries
    cursor.execute('''
        SELECT country_code, institution_name, official_website
        FROM european_institutions
        WHERE jurisdiction_level = "national"
        AND (
            LOWER(institution_name) LIKE '%defence%'
            OR LOWER(institution_name) LIKE '%defense%'
            OR LOWER(institution_name) LIKE '%verteidigung%'
            OR LOWER(institution_name) LIKE '%défense%'
            OR LOWER(institution_name) LIKE '%obrany%'
            OR LOWER(institution_name) LIKE '%forsvar%'
            OR LOWER(institution_name) LIKE '%odbrane%'
            OR LOWER(institution_name) LIKE '%mbrojtjes%'
            OR institution_name = 'Armed Forces of Malta'
        )
        ORDER BY country_code
    ''')

    defence = cursor.fetchall()

    print("=" * 80)
    print("DEFENCE MINISTRIES & MILITARY:")
    print(f"Total: {len(defence)}")
    print()

    for row in defence:
        print(f"  [{row[0]}] {row[1]}")
        print(f"       {row[2]}")
        print()

    # Cybersecurity agencies
    cursor.execute('''
        SELECT country_code, institution_name, official_website
        FROM european_institutions
        WHERE jurisdiction_level = "national"
        AND (
            LOWER(institution_name) LIKE '%cyber%'
            OR LOWER(institution_name) LIKE '%ncsc%'
        )
        ORDER BY country_code
    ''')

    cyber = cursor.fetchall()

    print("=" * 80)
    print("CYBERSECURITY AGENCIES:")
    print(f"Total: {len(cyber)}")
    print()

    for row in cyber:
        print(f"  [{row[0]}] {row[1]}")
        print(f"       {row[2]}")
        print()

    # Summary
    print("=" * 80)
    print("SECURITY & DEFENCE COVERAGE SUMMARY:")
    print(f"  Intelligence/Security Agencies: {len(intel_agencies)}")
    print(f"  Defence Ministries/Military: {len(defence)}")
    print(f"  Cybersecurity Agencies: {len(cyber)}")
    print(f"  TOTAL: {len(intel_agencies) + len(defence) + len(cyber)}")
    print("=" * 80)

    conn.close()

if __name__ == '__main__':
    validate_security_intel()

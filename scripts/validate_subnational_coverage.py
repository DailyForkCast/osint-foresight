#!/usr/bin/env python3
"""Validate Subnational Coverage Across Europe"""
import sqlite3
import json

def validate_subnational():
    print("=" * 80)
    print("EUROPEAN SUBNATIONAL INSTITUTIONAL COVERAGE - VALIDATION")
    print("=" * 80)
    print()

    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Overall stats
    cursor.execute('SELECT COUNT(*) FROM european_institutions WHERE jurisdiction_level LIKE "subnational%"')
    total_subnational = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM european_institutions WHERE jurisdiction_level = "national"')
    total_national = cursor.fetchone()[0]

    print("OVERALL COVERAGE:")
    print(f"  National Institutions: {total_national}")
    print(f"  Subnational Institutions: {total_subnational}")
    print(f"  TOTAL: {total_national + total_subnational}")
    print()

    # By country
    print("SUBNATIONAL COVERAGE BY COUNTRY:")
    cursor.execute('''
        SELECT country_code,
               COUNT(*) as total,
               COUNT(DISTINCT subnational_jurisdiction) as jurisdictions
        FROM european_institutions
        WHERE jurisdiction_level LIKE "subnational%"
        GROUP BY country_code
        ORDER BY total DESC
    ''')

    country_data = []
    for row in cursor.fetchall():
        country_data.append({
            'country': row[0],
            'institutions': row[1],
            'jurisdictions': row[2]
        })
        print(f"  {row[0]}: {row[1]} institutions across {row[2]} jurisdictions")

    print()

    # Detailed breakdown by country
    print("=" * 80)
    print("DETAILED BREAKDOWN:")
    print("=" * 80)

    for country in country_data:
        print(f"\n{country['country']} - {country['institutions']} institutions, {country['jurisdictions']} jurisdictions:")
        cursor.execute('''
            SELECT subnational_jurisdiction, COUNT(*) as cnt
            FROM european_institutions
            WHERE country_code = ? AND jurisdiction_level LIKE "subnational%"
            GROUP BY subnational_jurisdiction
            ORDER BY cnt DESC
        ''', (country['country'],))

        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]}")

    # By institution type in subnational
    print("\n" + "=" * 80)
    print("SUBNATIONAL INSTITUTIONS BY TYPE:")
    cursor.execute('''
        SELECT institution_type, COUNT(*)
        FROM european_institutions
        WHERE jurisdiction_level LIKE "subnational%"
        GROUP BY institution_type
        ORDER BY COUNT(*) DESC
    ''')

    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]}")

    # Generate summary report
    summary = {
        'validation_date': '2025-10-26',
        'total_subnational': total_subnational,
        'total_national': total_national,
        'total_institutions': total_national + total_subnational,
        'countries_with_subnational': len(country_data),
        'countries': country_data
    }

    with open('analysis/SUBNATIONAL_COVERAGE_REPORT.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)

    print("\n" + "=" * 80)
    print(f"SUMMARY:")
    print(f"  Countries with subnational coverage: {len(country_data)}")
    print(f"  Total subnational institutions: {total_subnational}")
    print(f"  Report saved: analysis/SUBNATIONAL_COVERAGE_REPORT.json")
    print("=" * 80)

    conn.close()

if __name__ == '__main__':
    validate_subnational()

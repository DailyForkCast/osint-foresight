#!/usr/bin/env python3
"""Generate Final Subnational Coverage Report"""
import sqlite3
import json
from datetime import datetime

def generate_final_report():
    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Overall stats
    cursor.execute('SELECT COUNT(*) FROM european_institutions WHERE jurisdiction_level = "national"')
    total_national = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM european_institutions WHERE jurisdiction_level LIKE "subnational%"')
    total_subnational = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(DISTINCT country_code) FROM european_institutions WHERE jurisdiction_level LIKE "subnational%"')
    countries_with_subnational = cursor.fetchone()[0]

    # By country
    cursor.execute('''
        SELECT country_code,
               COUNT(*) as total,
               COUNT(DISTINCT subnational_jurisdiction) as jurisdictions
        FROM european_institutions
        WHERE jurisdiction_level LIKE "subnational%"
        GROUP BY country_code
        ORDER BY total DESC
    ''')

    countries = []
    for row in cursor.fetchall():
        countries.append({
            'country': row[0],
            'institutions': row[1],
            'jurisdictions': row[2]
        })

    # By type
    cursor.execute('''
        SELECT institution_type, COUNT(*)
        FROM european_institutions
        WHERE jurisdiction_level LIKE "subnational%"
        GROUP BY institution_type
        ORDER BY COUNT(*) DESC
    ''')
    types = [{'type': row[0], 'count': row[1]} for row in cursor.fetchall()]

    report = {
        'report_date': datetime.now().isoformat(),
        'summary': {
            'total_institutions': total_national + total_subnational,
            'national_institutions': total_national,
            'subnational_institutions': total_subnational,
            'countries_with_subnational': countries_with_subnational,
            'subnational_jurisdictions_total': sum([c['jurisdictions'] for c in countries])
        },
        'countries': countries,
        'institution_types': types
    }

    with open('analysis/SUBNATIONAL_FINAL_REPORT.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print("=" * 80)
    print("EUROPEAN SUBNATIONAL COVERAGE - FINAL REPORT")
    print("=" * 80)
    print()
    print(f"TOTAL INSTITUTIONS: {total_national + total_subnational}")
    print(f"  National: {total_national}")
    print(f"  Subnational: {total_subnational}")
    print()
    print(f"COVERAGE:")
    print(f"  Countries with subnational coverage: {countries_with_subnational}")
    print(f"  Total subnational jurisdictions: {sum([c['jurisdictions'] for c in countries])}")
    print()
    print("BY COUNTRY:")
    for c in countries:
        print(f"  {c['country']}: {c['institutions']} institutions, {c['jurisdictions']} jurisdictions")
    print()
    print("Report saved to: analysis/SUBNATIONAL_FINAL_REPORT.json")
    print("=" * 80)

    conn.close()

if __name__ == '__main__':
    generate_final_report()

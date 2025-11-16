#!/usr/bin/env python3
"""
Comprehensive Audit of ALL European Countries
Compare current database vs BigQuery using ALL geographic fields
"""
from google.cloud import bigquery
import sqlite3
import json
from datetime import datetime

project_id = "osint-foresight-2025"
client = bigquery.Client(project=project_id)

# All European countries with their code variants
european_countries = {
    'Albania': {'codes': ['ALB', 'AL'], 'search_terms': ['albania', 'albanian']},
    'Andorra': {'codes': ['AND', 'AD'], 'search_terms': ['andorra', 'andorran']},
    'Armenia': {'codes': ['ARM', 'AM'], 'search_terms': ['armenia', 'armenian']},
    'Austria': {'codes': ['AUT', 'AT'], 'search_terms': ['austria', 'austrian']},
    'Azerbaijan': {'codes': ['AZE', 'AZ'], 'search_terms': ['azerbaijan', 'azerbaijani']},
    'Belarus': {'codes': ['BLR', 'BY'], 'search_terms': ['belarus', 'belarusian']},
    'Belgium': {'codes': ['BEL', 'BE'], 'search_terms': ['belgium', 'belgian']},
    'Bosnia': {'codes': ['BIH', 'BOS', 'BA'], 'search_terms': ['bosnia', 'bosnian', 'herzegovina']},
    'Bulgaria': {'codes': ['BGR', 'BG'], 'search_terms': ['bulgaria', 'bulgarian']},
    'Croatia': {'codes': ['HRV', 'HR'], 'search_terms': ['croatia', 'croatian']},
    'Cyprus': {'codes': ['CYP', 'CY'], 'search_terms': ['cyprus', 'cypriot']},
    'Czechia': {'codes': ['CZE', 'CZ'], 'search_terms': ['czech', 'czechia']},
    'Denmark': {'codes': ['DNK', 'DK'], 'search_terms': ['denmark', 'danish']},
    'Estonia': {'codes': ['EST', 'EE'], 'search_terms': ['estonia', 'estonian']},
    'Finland': {'codes': ['FIN', 'FI'], 'search_terms': ['finland', 'finnish']},
    'France': {'codes': ['FRA', 'FR'], 'search_terms': ['france', 'french']},
    'Georgia': {'codes': ['GEO', 'GE'], 'search_terms': ['georgia', 'georgian']},
    'Germany': {'codes': ['DEU', 'DE', 'GER'], 'search_terms': ['germany', 'german']},
    'Greece': {'codes': ['GRC', 'GR'], 'search_terms': ['greece', 'greek']},
    'Hungary': {'codes': ['HUN', 'HU'], 'search_terms': ['hungary', 'hungarian']},
    'Iceland': {'codes': ['ISL', 'IS'], 'search_terms': ['iceland', 'icelandic']},
    'Ireland': {'codes': ['IRL', 'IE'], 'search_terms': ['ireland', 'irish']},
    'Italy': {'codes': ['ITA', 'IT'], 'search_terms': ['italy', 'italian']},
    'Kosovo': {'codes': ['KOS', 'KSV', 'XK', 'XKX'], 'search_terms': ['kosovo', 'kosovar']},
    'Latvia': {'codes': ['LVA', 'LV'], 'search_terms': ['latvia', 'latvian']},
    'Liechtenstein': {'codes': ['LIE', 'LI'], 'search_terms': ['liechtenstein']},
    'Lithuania': {'codes': ['LTU', 'LT'], 'search_terms': ['lithuania', 'lithuanian']},
    'Luxembourg': {'codes': ['LUX', 'LU'], 'search_terms': ['luxembourg']},
    'Malta': {'codes': ['MLT', 'MT'], 'search_terms': ['malta', 'maltese']},
    'Moldova': {'codes': ['MDA', 'MD'], 'search_terms': ['moldova', 'moldovan']},
    'Monaco': {'codes': ['MCO', 'MC'], 'search_terms': ['monaco', 'monacan']},
    'Montenegro': {'codes': ['MNE', 'MNG', 'MNT', 'ME'], 'search_terms': ['montenegro', 'montenegrin']},
    'Netherlands': {'codes': ['NLD', 'NL'], 'search_terms': ['netherlands', 'dutch']},
    'North Macedonia': {'codes': ['MKD', 'MK'], 'search_terms': ['macedonia', 'macedonian']},
    'Norway': {'codes': ['NOR', 'NO'], 'search_terms': ['norway', 'norwegian']},
    'Poland': {'codes': ['POL', 'PL'], 'search_terms': ['poland', 'polish']},
    'Portugal': {'codes': ['PRT', 'PT'], 'search_terms': ['portugal', 'portuguese']},
    'Romania': {'codes': ['ROU', 'ROM', 'RO'], 'search_terms': ['romania', 'romanian']},
    'Russia': {'codes': ['RUS', 'RU'], 'search_terms': ['russia', 'russian']},
    'San Marino': {'codes': ['SMR', 'SM'], 'search_terms': ['san marino']},
    'Serbia': {'codes': ['SRB', 'RS'], 'search_terms': ['serbia', 'serbian']},
    'Slovakia': {'codes': ['SVK', 'SK'], 'search_terms': ['slovakia', 'slovak']},
    'Slovenia': {'codes': ['SVN', 'SLO', 'SI'], 'search_terms': ['slovenia', 'slovenian']},
    'Spain': {'codes': ['ESP', 'ES'], 'search_terms': ['spain', 'spanish']},
    'Sweden': {'codes': ['SWE', 'SE'], 'search_terms': ['sweden', 'swedish']},
    'Switzerland': {'codes': ['CHE', 'CH'], 'search_terms': ['switzerland', 'swiss']},
    'Turkey': {'codes': ['TUR', 'TR'], 'search_terms': ['turkey', 'turkish']},
    'UK': {'codes': ['GBR', 'GB', 'UK'], 'search_terms': ['united kingdom', 'britain', 'british']},
    'Ukraine': {'codes': ['UKR', 'UA'], 'search_terms': ['ukraine', 'ukrainian']},
    'Vatican': {'codes': ['VAT', 'VA'], 'search_terms': ['vatican', 'holy see']},
}

print("\n" + "=" * 100)
print("COMPREHENSIVE AUDIT: ALL EUROPEAN COUNTRIES")
print("=" * 100)
print(f"Checking {len(european_countries)} countries...")
print("Comparing: Current DB vs BigQuery Comprehensive")
print("=" * 100)

# Connect to local database
conn = sqlite3.connect('F:/OSINT_WAREHOUSE/osint_master.db')
cursor = conn.cursor()

results = {}

for country_name, config in sorted(european_countries.items()):
    print(f"\n{country_name:20s}", end=" ", flush=True)

    codes = config['codes']
    search_terms = config['search_terms']

    # Get current database count (primary code only)
    primary_code = codes[0]
    cursor.execute('''
        SELECT COUNT(*)
        FROM gdelt_events
        WHERE (actor1_country_code = ? OR actor2_country_code = ?)
          AND (actor1_country_code = 'CHN' OR actor2_country_code = 'CHN')
          AND sqldate >= 20200101
    ''', (primary_code, primary_code))
    db_count = cursor.fetchone()[0]

    # Build comprehensive BigQuery query
    code_conditions = []
    for code in codes:
        code_conditions.extend([
            f"Actor1CountryCode = '{code}'",
            f"Actor2CountryCode = '{code}'",
            f"Actor1Geo_CountryCode = '{code}'",
            f"Actor2Geo_CountryCode = '{code}'",
            f"ActionGeo_CountryCode = '{code}'"
        ])

    name_conditions = []
    for term in search_terms:
        name_conditions.extend([
            f"LOWER(Actor1Name) LIKE '%{term}%'",
            f"LOWER(Actor2Name) LIKE '%{term}%'",
            f"LOWER(Actor1Geo_FullName) LIKE '%{term}%'",
            f"LOWER(Actor2Geo_FullName) LIKE '%{term}%'",
            f"LOWER(ActionGeo_FullName) LIKE '%{term}%'"
        ])

    all_conditions = code_conditions + name_conditions
    where_clause = " OR ".join(all_conditions)

    query = f"""
        SELECT COUNT(DISTINCT GLOBALEVENTID) as count
        FROM `gdelt-bq.gdeltv2.events`
        WHERE ({where_clause})
          AND (Actor1CountryCode = 'CHN' OR Actor2CountryCode = 'CHN')
          AND SQLDATE >= 20200101
    """

    try:
        query_job = client.query(query)
        result = query_job.result()

        for row in result:
            bq_count = row.count
            gap = bq_count - db_count
            gap_pct = (gap / bq_count * 100) if bq_count > 0 else 0

            results[country_name] = {
                'db_count': db_count,
                'bq_comprehensive_count': bq_count,
                'gap': gap,
                'gap_pct': gap_pct,
                'codes_checked': codes,
                'primary_code': primary_code
            }

            if gap > 0:
                print(f"DB: {db_count:6,} | BQ: {bq_count:6,} | GAP: {gap:6,} ({gap_pct:5.1f}%)")
            else:
                print(f"DB: {db_count:6,} | BQ: {bq_count:6,} | COMPLETE")

    except Exception as e:
        print(f"ERROR: {str(e)}")
        results[country_name] = {'error': str(e)}

conn.close()

# Summary
print("\n" + "=" * 100)
print("SUMMARY: COUNTRIES WITH GAPS")
print("=" * 100)

gaps = [(name, data) for name, data in results.items()
        if 'gap' in data and data['gap'] > 0]
gaps.sort(key=lambda x: x[1]['gap'], reverse=True)

total_gap = sum(data['gap'] for _, data in gaps)
total_db = sum(data['db_count'] for _, data in results.items() if 'db_count' in data)
total_bq = sum(data['bq_comprehensive_count'] for _, data in results.items() if 'bq_comprehensive_count' in data)

print(f"\nCountries with missing data: {len(gaps)}")
print(f"Total gap: {total_gap:,} events")
print(f"Current DB total: {total_db:,}")
print(f"BigQuery comprehensive total: {total_bq:,}")
print(f"Overall coverage: {(total_db / total_bq * 100):.1f}%")

print("\n" + "-" * 100)
print(f"{'Country':20s} {'DB Count':>10s} {'BQ Count':>10s} {'Gap':>10s} {'% Missing':>10s}")
print("-" * 100)

for name, data in gaps:
    print(f"{name:20s} {data['db_count']:10,} {data['bq_comprehensive_count']:10,} "
          f"{data['gap']:10,} {data['gap_pct']:9.1f}%")

# Save results
output = {
    'timestamp': datetime.now().isoformat(),
    'total_db_events': total_db,
    'total_bq_comprehensive': total_bq,
    'total_gap': total_gap,
    'countries_with_gaps': len(gaps),
    'results': results
}

with open('analysis/european_countries_comprehensive_audit.json', 'w') as f:
    json.dump(output, f, indent=2)

print("\n" + "=" * 100)
print(f"Results saved to: analysis/european_countries_comprehensive_audit.json")
print("=" * 100)

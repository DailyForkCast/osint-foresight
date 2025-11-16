#!/usr/bin/env python3
"""
Assess current country coverage and bilateral data availability - V2
"""
import sqlite3
import json
import sys

# Fix encoding for Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print("="*80)
    print("COUNTRY COVERAGE ASSESSMENT")
    print("="*80)

    # 1. List all bilateral tables
    print("\n1. BILATERAL TABLES STATUS:")
    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='table' AND name LIKE 'bilateral%'
        ORDER BY name
    """)
    bilateral_tables = [row[0] for row in cursor.fetchall()]

    table_status = {}
    for table in bilateral_tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        status = "POPULATED" if count > 0 else "EMPTY"
        table_status[table] = count
        print(f"  [{status:9}] {table:35} {count:,} records")

    # 2. Countries configured
    print("\n2. COUNTRIES CONFIGURED:")
    cursor.execute("SELECT COUNT(*) FROM bilateral_countries")
    country_count = cursor.fetchone()[0]
    print(f"  Total countries: {country_count}")

    cursor.execute("""
        SELECT country_code, country_name, eu_member, bri_participation_status
        FROM bilateral_countries
        ORDER BY country_code
    """)
    countries = cursor.fetchall()
    print("\n  Configured countries:")
    country_list = []
    for country in countries:
        eu = "EU" if country['eu_member'] else "Non-EU"
        bri = country['bri_participation_status'] if country['bri_participation_status'] else "No BRI"
        print(f"    {country['country_code']}: {country['country_name']:30} ({eu:7}, {bri})")
        country_list.append({
            "code": country['country_code'],
            "name": country['country_name'],
            "eu_member": country['eu_member'],
            "bri_status": country['bri_participation_status']
        })

    # 3. Bilateral events by country
    print("\n3. BILATERAL EVENTS BY COUNTRY:")
    cursor.execute("""
        SELECT country_code, country_name, COUNT(*) as event_count
        FROM bilateral_events
        GROUP BY country_code, country_name
        ORDER BY event_count DESC
    """)
    events = cursor.fetchall()
    event_data = []
    for event in events[:10]:  # Top 10
        print(f"  {event['country_code']:3}: {event['event_count']:3,} events  ({event['country_name']})")
        event_data.append({"code": event['country_code'], "events": event['event_count']})

    # 4. Academic links by country (from OpenAlex)
    print("\n4. ACADEMIC COLLABORATIONS BY COUNTRY:")
    cursor.execute("""
        SELECT country_code, COUNT(*) as collab_count
        FROM bilateral_academic_links
        GROUP BY country_code
        ORDER BY collab_count DESC
    """)
    academic = cursor.fetchall()
    if academic:
        for row in academic[:10]:
            print(f"  {row['country_code']:3}: {row['collab_count']:,} collaborations")
    else:
        print("  No data yet")

    # 5. Patent links by country
    print("\n5. PATENT COLLABORATIONS BY COUNTRY:")
    cursor.execute("""
        SELECT country_code, COUNT(*) as patent_count
        FROM bilateral_patent_links
        GROUP BY country_code
        ORDER BY patent_count DESC
    """)
    patents = cursor.fetchall()
    if patents:
        for row in patents[:10]:
            print(f"  {row['country_code']:3}: {row['patent_count']:,} patents")
    else:
        print("  No data yet")

    # 6. Procurement links by country
    print("\n6. PROCUREMENT CONTRACTS BY COUNTRY:")
    cursor.execute("""
        SELECT country_code, COUNT(*) as contract_count
        FROM bilateral_procurement_links
        GROUP BY country_code
        ORDER BY contract_count DESC
    """)
    procurement = cursor.fetchall()
    if procurement:
        for row in procurement[:10]:
            print(f"  {row['country_code']:3}: {row['contract_count']:,} contracts")
    else:
        print("  No data yet")

    # 7. Check OpenAlex data availability
    print("\n7. OPENALEX DATA AVAILABILITY:")
    try:
        cursor.execute("""
            SELECT COUNT(DISTINCT country_code) as countries,
                   COUNT(*) as total_works
            FROM openalex_works
            WHERE country_code IS NOT NULL AND country_code != ''
        """)
        openalex = cursor.fetchone()
        if openalex:
            print(f"  Countries with data: {openalex['countries']}")
            print(f"  Total works: {openalex['total_works']:,}")
    except:
        print("  Table not available or empty")
        openalex = None

    # 8. Check GDELT data availability
    print("\n8. GDELT DATA AVAILABILITY:")
    try:
        cursor.execute("SELECT COUNT(*) FROM gdelt_events WHERE event_date >= '2020-01-01'")
        gdelt = cursor.fetchone()
        if gdelt:
            print(f"  Total events (2020+): {gdelt[0]:,}")

        cursor.execute("""
            SELECT COUNT(DISTINCT actor1_country_code) as countries
            FROM gdelt_events
            WHERE actor1_country_code IS NOT NULL
        """)
        gdelt_countries = cursor.fetchone()
        if gdelt_countries:
            print(f"  Countries in GDELT: {gdelt_countries[0]}")
    except:
        print("  Table not available")
        gdelt = None

    # 9. Investment data
    print("\n9. INVESTMENT DATA:")
    cursor.execute("""
        SELECT target_country, COUNT(*) as investment_count,
               SUM(CAST(investment_amount_usd AS REAL)) as total_usd
        FROM bilateral_investments
        GROUP BY target_country
        ORDER BY investment_count DESC
    """)
    investments = cursor.fetchall()
    if investments:
        for row in investments:
            amount = f"${row['total_usd']/1e9:.1f}B" if row['total_usd'] else "N/A"
            print(f"  {row['target_country']:3}: {row['investment_count']:,} investments ({amount})")

    # 10. Generate summary JSON
    summary = {
        "timestamp": "2025-11-03",
        "bilateral_tables": table_status,
        "countries_configured": country_count,
        "country_list": country_list,
        "top_event_countries": event_data,
        "data_sources_available": {
            "openalex": openalex['total_works'] if openalex else 0,
            "gdelt": gdelt[0] if gdelt else 0,
            "ted_procurement": table_status.get('bilateral_procurement_links', 0),
            "investments": table_status.get('bilateral_investments', 0),
            "academic_links": table_status.get('bilateral_academic_links', 0),
            "patent_links": table_status.get('bilateral_patent_links', 0)
        }
    }

    with open("analysis/country_coverage_assessment.json", "w", encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print("\n" + "="*80)
    print("SUMMARY saved to: analysis/country_coverage_assessment.json")
    print("="*80)

    conn.close()

if __name__ == "__main__":
    main()

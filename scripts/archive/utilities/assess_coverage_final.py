#!/usr/bin/env python3
"""
Assess current country coverage and bilateral data availability - FINAL
"""
import sqlite3
import json

DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print("="*80)
    print("COUNTRY COVERAGE ASSESSMENT")
    print("="*80)

    # 1. Bilateral tables status
    print("\n1. BILATERAL TABLES STATUS:")
    cursor.execute("""
        SELECT name FROM sqlite_master
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
    print("\n2. COUNTRIES CONFIGURED (24 total):")
    cursor.execute("""
        SELECT country_code, country_name, eu_member, bri_participation_status
        FROM bilateral_countries
        ORDER BY country_code
    """)
    countries = cursor.fetchall()

    country_list = []
    for country in countries:
        eu = "EU" if country['eu_member'] else "   "
        bri = country['bri_participation_status'] if country['bri_participation_status'] else "No BRI"
        print(f"    {country['country_code']}: {country['country_name']:30} [{eu}] {bri}")
        country_list.append({
            "code": country['country_code'],
            "name": country['country_name'],
            "eu_member": country['eu_member'],
            "bri_status": country['bri_participation_status']
        })

    # 3. Events by country
    print("\n3. BILATERAL EVENTS BY COUNTRY:")
    cursor.execute("""
        SELECT e.country_code, c.country_name, COUNT(*) as event_count
        FROM bilateral_events e
        JOIN bilateral_countries c ON e.country_code = c.country_code
        GROUP BY e.country_code, c.country_name
        ORDER BY event_count DESC
    """)
    events = cursor.fetchall()
    event_data = []
    for event in events:
        print(f"  {event['country_code']:3}: {event['event_count']:3,} events  ({event['country_name']})")
        event_data.append({"code": event['country_code'], "events": event['event_count']})

    # 4. Academic by country
    print("\n4. ACADEMIC COLLABORATIONS BY COUNTRY:")
    cursor.execute("""
        SELECT a.country_code, c.country_name, COUNT(*) as collab_count
        FROM bilateral_academic_links a
        JOIN bilateral_countries c ON a.country_code = c.country_code
        GROUP BY a.country_code, c.country_name
        ORDER BY collab_count DESC
    """)
    academic = cursor.fetchall()
    for row in academic:
        print(f"  {row['country_code']:3}: {row['collab_count']:4,} collaborations ({row['country_name']})")

    # 5. Patents by country
    print("\n5. PATENT COLLABORATIONS BY COUNTRY:")
    cursor.execute("""
        SELECT p.country_code, c.country_name, COUNT(*) as patent_count
        FROM bilateral_patent_links p
        JOIN bilateral_countries c ON p.country_code = c.country_code
        GROUP BY p.country_code, c.country_name
        ORDER BY patent_count DESC
    """)
    patents = cursor.fetchall()
    for row in patents:
        print(f"  {row['country_code']:3}: {row['patent_count']:4,} patents ({row['country_name']})")

    # 6. Procurement by country
    print("\n6. PROCUREMENT CONTRACTS BY COUNTRY:")
    cursor.execute("""
        SELECT pr.country_code, c.country_name, COUNT(*) as contract_count
        FROM bilateral_procurement_links pr
        JOIN bilateral_countries c ON pr.country_code = c.country_code
        GROUP BY pr.country_code, c.country_name
        ORDER BY contract_count DESC
    """)
    procurement = cursor.fetchall()
    for row in procurement:
        print(f"  {row['country_code']:3}: {row['contract_count']:5,} contracts ({row['country_name']})")

    # 7. Investments
    print("\n7. INVESTMENT DATA:")
    cursor.execute("""
        SELECT target_country, COUNT(*) as investment_count,
               SUM(CAST(investment_amount_usd AS REAL)) as total_usd
        FROM bilateral_investments
        GROUP BY target_country
        ORDER BY investment_count DESC
    """)
    investments = cursor.fetchall()
    for row in investments:
        amount = f"${row['total_usd']/1e9:.1f}B" if row['total_usd'] else "N/A"
        print(f"  {row['target_country']:3}: {row['investment_count']:,} investments ({amount})")

    # 8. Corporate links
    print("\n8. CORPORATE LINKS:")
    cursor.execute("SELECT COUNT(*) FROM bilateral_corporate_links")
    corp_count = cursor.fetchone()[0]
    print(f"  Total corporate links: {corp_count}")

    # 9. Generate summary
    summary = {
        "timestamp": "2025-11-03",
        "bilateral_tables": table_status,
        "countries_configured": len(country_list),
        "country_list": country_list,
        "top_event_countries": event_data,
        "summary_stats": {
            "events": sum(e['events'] for e in event_data),
            "academic_links": table_status.get('bilateral_academic_links', 0),
            "patent_links": table_status.get('bilateral_patent_links', 0),
            "procurement": table_status.get('bilateral_procurement_links', 0),
            "investments": table_status.get('bilateral_investments', 0),
            "corporate_links": corp_count
        }
    }

    with open("analysis/country_coverage_assessment.json", "w", encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print("\n" + "="*80)
    print("SUMMARY STATISTICS:")
    print(f"  Countries configured: {summary['countries_configured']}")
    print(f"  Total events: {summary['summary_stats']['events']}")
    print(f"  Academic links: {summary['summary_stats']['academic_links']}")
    print(f"  Patent links: {summary['summary_stats']['patent_links']}")
    print(f"  Procurement contracts: {summary['summary_stats']['procurement']}")
    print(f"  Investments: {summary['summary_stats']['investments']}")
    print(f"  Corporate links: {summary['summary_stats']['corporate_links']}")
    print("\nSUMMARY saved to: analysis/country_coverage_assessment.json")
    print("="*80)

    conn.close()

if __name__ == "__main__":
    main()

"""
Lithuania TED Procurement Analysis
Check for Lithuanian government contracts with Chinese companies (2020-2023)
Cross-reference with GDELT economic measures events
"""

import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')

db = sqlite3.connect('F:/OSINT_WAREHOUSE/osint_master.db')
cursor = db.cursor()

print('='*100)
print('LITHUANIA TED PROCUREMENT: CHINESE CONTRACTORS CHECK')
print('Data Source: TED (Tenders Electronic Daily) - EU public procurement database')
print('Purpose: Cross-reference with GDELT economic measures events (Aug-Dec 2021)')
print('='*100)
print()

# Check ted_china_contracts_fixed for Lithuanian contracts
print('STEP 1: LITHUANIAN CONTRACTS WITH CHINESE ENTITIES')
print('-'*100)

cursor.execute("""
    SELECT COUNT(*)
    FROM ted_china_contracts_fixed
    WHERE iso_country_code = 'LT'
""")
lt_contracts = cursor.fetchone()[0]
print(f"Lithuanian contracts with Chinese entities: {lt_contracts:,}")
print()

if lt_contracts > 0:
    # Get details by year
    cursor.execute("""
        SELECT
            year,
            COUNT(*) as contracts,
            SUM(CASE WHEN value_euro IS NOT NULL THEN value_euro ELSE 0 END) as total_value
        FROM ted_china_contracts_fixed
        WHERE iso_country_code = 'LT'
          AND year IS NOT NULL
        GROUP BY year
        ORDER BY year
    """)

    print('Lithuanian contracts with Chinese entities by year:')
    print(f"{'Year':<8} {'Contracts':<15} {'Value (M EUR)':<20}")
    print('-'*50)
    year_data = cursor.fetchall()
    for year, contracts, value in year_data:
        value_m = value / 1_000_000 if value else 0
        marker = ' <- Taiwan events' if year in [2021, 2022] else ''
        print(f"{year:<8} {contracts:<15,} {value_m:>18.2f}{marker}")
    print()

    # Check 2021-2022 specifically
    cursor.execute("""
        SELECT
            award_date,
            name,
            value_euro,
            title
        FROM ted_china_contracts_fixed
        WHERE iso_country_code = 'LT'
          AND year IN (2021, 2022)
        ORDER BY award_date
    """)
    contracts_2021_2022 = cursor.fetchall()

    if contracts_2021_2022:
        print('='*100)
        print('DETAILED VIEW: LITHUANIA 2021-2022 CONTRACTS')
        print('Period Context: Lithuania Taiwan events (Jul-Dec 2021), GDELT peak activity Dec 2021')
        print('='*100)
        print()
        for award_date, name, value, title in contracts_2021_2022:
            value_str = f"€{value:,.0f}" if value else "N/A"
            print(f"Date: {award_date}")
            print(f"Contractor: {name}")
            print(f"Value: {value_str}")
            print(f"Title: {title[:80]}...")
            print('-'*100)
    else:
        print("No Lithuanian contracts with Chinese entities found in 2021-2022")
        print()
else:
    print("No Lithuanian contracts with Chinese entities found in database")
    print()

# Check overall TED Lithuania statistics
print('='*100)
print('STEP 2: OVERALL LITHUANIAN TED PROCUREMENT CONTEXT')
print('-'*100)

# Check if we have general Lithuanian TED data
cursor.execute("""
    SELECT COUNT(*)
    FROM ted_contracts_production
    WHERE iso_country_code = 'LT'
""")
total_lt_contracts = cursor.fetchone()[0]
print(f"Total Lithuanian TED contracts (all contractors): {total_lt_contracts:,}")

if total_lt_contracts > 0:
    cursor.execute("""
        SELECT
            CAST(strftime('%Y', award_decision_date) AS INTEGER) as year,
            COUNT(*) as contracts
        FROM ted_contracts_production
        WHERE iso_country_code = 'LT'
          AND award_decision_date IS NOT NULL
          AND CAST(strftime('%Y', award_decision_date) AS INTEGER) BETWEEN 2020 AND 2023
        GROUP BY year
        ORDER BY year
    """)
    print()
    print("Lithuanian TED contracts by year (all contractors, 2020-2023):")
    print(f"{'Year':<8} {'Contracts':<15}")
    print('-'*30)
    for year, contracts in cursor.fetchall():
        print(f"{year:<8} {contracts:<15,}")
    print()

print('='*100)
print('CROSS-REFERENCE FINDING')
print('='*100)
print()

if lt_contracts == 0:
    print("OBSERVATION: No Lithuanian government contracts with Chinese entities found in TED data.")
    print()
    print("Interpretation (neutral, factual):")
    print("  - Either Lithuania did not award contracts to Chinese companies")
    print("  - Or such contracts were not reported in TED (below reporting thresholds)")
    print("  - Or Chinese contractor names not detected by our detection system")
    print()
    print("This finding is CONSISTENT with GDELT economic measures events, which suggest")
    print("reduced Lithuania-China commercial engagement during the Taiwan events period.")
    print()
    print("NOTE: Absence of contracts does not prove causation. Alternative explanations:")
    print("  - Lithuania may have had few China contracts pre-events (baseline unknown)")
    print("  - TED reporting thresholds (contracts below €144k may not appear)")
    print("  - Detection limitations (transliterated Chinese names may not match)")
else:
    print(f"OBSERVATION: Found {lt_contracts:,} Lithuanian contracts with Chinese entities")
    print()
    print("Further analysis needed:")
    print("  - Compare 2021-2022 contracts to pre-events baseline (2019-2020)")
    print("  - Identify if contract volume/value decreased during events period")
    print("  - Cross-reference contractor names with Chinese entity databases")

print()
print('='*100)
print('NEXT STEPS')
print('='*100)
print()
print("1. If contracts found: Analyze temporal pattern vs. GDELT timeline")
print("2. Check for Lithuanian contracts with Taiwan companies (comparative analysis)")
print("3. Expand to other EU countries for control group comparison")
print("4. Document procurement findings in validation report")
print()
print('='*100)

db.close()

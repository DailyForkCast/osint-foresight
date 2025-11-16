"""
Lithuania-China Trade Data Extraction
Cross-reference with GDELT events (Dec 2021 peak activity)
Language: Neutral, factual presentation per LANGUAGE_TONE_STANDARDS.md
"""

import sqlite3
import sys

# Fix Windows console encoding
sys.stdout.reconfigure(encoding='utf-8')

db = sqlite3.connect('F:/OSINT_WAREHOUSE/osint_master.db')
cursor = db.cursor()

print('='*100)
print('LITHUANIA-CHINA TRADE DATA EXTRACTION')
print('Data Source: Eurostat COMEXT')
print('Purpose: Cross-reference with GDELT events (2020-2023)')
print('='*100)
print()

# Check overall Lithuania-China trade data availability
print('STEP 1: DATA AVAILABILITY CHECK')
print('-'*100)
cursor.execute("""
    SELECT
        COUNT(*) as records,
        MIN(year) as min_year,
        MAX(year) as max_year,
        MIN(period) as min_period,
        MAX(period) as max_period
    FROM eurostat_comext
    WHERE reporter = 'LT' AND partner = 'CN'
""")
result = cursor.fetchone()

if result and result[0] > 0:
    print(f"Lithuania-China bilateral trade records found:")
    print(f"  Total Records: {result[0]:,}")
    print(f"  Year Range: {result[1]} to {result[2]}")
    print(f"  Period Range: {result[3]} to {result[4]}")
    print()
else:
    print("No Lithuania-China trade data found in eurostat_comext table")
    print()

    # Check reverse direction
    cursor.execute("""
        SELECT COUNT(*)
        FROM eurostat_comext
        WHERE reporter = 'CN' AND partner = 'LT'
    """)
    reverse = cursor.fetchone()
    if reverse and reverse[0] > 0:
        print(f"Note: Found {reverse[0]:,} records with China as reporter, Lithuania as partner")
    db.close()
    sys.exit(0)

# Get trade by year for 2020-2023
print('STEP 2: ANNUAL TRADE VOLUMES (2020-2023)')
print('-'*100)
cursor.execute("""
    SELECT
        year,
        COUNT(*) as records,
        SUM(CASE WHEN value_eur IS NOT NULL THEN value_eur ELSE 0 END) as total_value_eur
    FROM eurostat_comext
    WHERE reporter = 'LT' AND partner = 'CN'
      AND year BETWEEN 2020 AND 2023
    GROUP BY year
    ORDER BY year
""")

years_data = cursor.fetchall()
if years_data:
    print("Lithuania to China trade by year:")
    print(f"{'Year':<6} {'Records':<10} {'Value (EUR)':<20} {'Value (Million EUR)':<20}")
    print('-'*70)
    for row in years_data:
        year, records, value = row
        value_million = value / 1_000_000 if value else 0
        print(f"{year:<6} {records:<10,} {value:>18,.0f}  {value_million:>18,.2f}M")
    print()
else:
    print("No trade data found for 2020-2023 period")
    print()

# Get quarterly breakdown for 2021-2022 (Lithuania Taiwan events period)
print('STEP 3: QUARTERLY BREAKDOWN (2021-2022)')
print('Period Context: Lithuania Taiwan office events (Jul 2021 - Dec 2021)')
print('GDELT Peak Activity: December 2021 (1,338 events, 707 relationship-weakening events)')
print('-'*100)

cursor.execute("""
    SELECT
        year,
        CAST(SUBSTR(period, 5, 2) AS INTEGER) as month,
        COUNT(*) as records,
        SUM(CASE WHEN value_eur IS NOT NULL THEN value_eur ELSE 0 END) as total_value_eur
    FROM eurostat_comext
    WHERE reporter = 'LT' AND partner = 'CN'
      AND year IN (2021, 2022)
      AND LENGTH(period) = 6
    GROUP BY year, month
    ORDER BY year, month
""")

monthly_data = cursor.fetchall()
if monthly_data:
    print("Lithuania to China trade by month (2021-2022):")
    print(f"{'Year-Month':<12} {'Records':<10} {'Value (EUR)':<20} {'Value (Million EUR)':<20}")
    print('-'*70)

    # Calculate quarterly totals
    q_totals = {}
    for row in monthly_data:
        year, month, records, value = row
        quarter = ((month - 1) // 3) + 1
        q_key = f"{year}-Q{quarter}"
        if q_key not in q_totals:
            q_totals[q_key] = {'records': 0, 'value': 0}
        q_totals[q_key]['records'] += records
        q_totals[q_key]['value'] += value

        value_million = value / 1_000_000 if value else 0
        print(f"{year}-{month:02d}      {records:<10,} {value:>18,.0f}  {value_million:>18,.2f}M")

    print()
    print("Quarterly Summary:")
    print(f"{'Quarter':<12} {'Records':<10} {'Value (Million EUR)':<20}")
    print('-'*50)
    for q in sorted(q_totals.keys()):
        records = q_totals[q]['records']
        value_million = q_totals[q]['value'] / 1_000_000
        print(f"{q:<12} {records:<10,} {value_million:>18,.2f}M")
    print()

    # Calculate year-over-year changes
    if '2021-Q4' in q_totals and '2020-Q4' in q_totals:
        q4_2020 = q_totals['2020-Q4']['value']
        q4_2021 = q_totals['2021-Q4']['value']
        change = ((q4_2021 - q4_2020) / q4_2020 * 100) if q4_2020 else 0
        print(f"Q4 2020 to Q4 2021 change: {change:+.1f}%")
        print("(Q4 2021 includes Lithuania Taiwan office events and GDELT peak activity)")
        print()

    if '2022-Q1' in q_totals and '2021-Q4' in q_totals:
        q4_2021 = q_totals['2021-Q4']['value']
        q1_2022 = q_totals['2022-Q1']['value']
        change = ((q1_2022 - q4_2021) / q4_2021 * 100) if q4_2021 else 0
        print(f"Q4 2021 to Q1 2022 change: {change:+.1f}%")
        print("(Transition from peak event period to post-event period)")
        print()
else:
    print("No monthly trade data found for 2021-2022")
    print()

# Check trade flow direction (imports vs exports)
print('STEP 4: TRADE FLOW ANALYSIS (2021-2022)')
print('-'*100)
cursor.execute("""
    SELECT
        year,
        flow,
        COUNT(*) as records,
        SUM(CASE WHEN value_eur IS NOT NULL THEN value_eur ELSE 0 END) as total_value_eur
    FROM eurostat_comext
    WHERE reporter = 'LT' AND partner = 'CN'
      AND year IN (2021, 2022)
    GROUP BY year, flow
    ORDER BY year, flow
""")

flow_data = cursor.fetchall()
if flow_data:
    print("Lithuania-China trade by flow type:")
    print(f"{'Year':<6} {'Flow':<10} {'Records':<10} {'Value (Million EUR)':<20}")
    print('-'*60)
    for row in flow_data:
        year, flow, records, value = row
        value_million = value / 1_000_000 if value else 0
        flow_desc = 'Import' if flow == '1' else 'Export' if flow == '2' else f'Flow {flow}'
        print(f"{year:<6} {flow_desc:<10} {records:<10,} {value_million:>18,.2f}M")
    print()
else:
    print("No flow-specific data available")
    print()

print('='*100)
print('ANALYSIS COMPLETE')
print('Next: Compare trade patterns to GDELT event timeline')
print('='*100)

db.close()

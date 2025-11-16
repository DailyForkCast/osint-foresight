#!/usr/bin/env python3
"""
Create Bilateral Procurement Links
Links TED China contracts to bilateral procurement framework
"""

import sqlite3
from pathlib import Path
from datetime import datetime
import hashlib

DB_PATH = Path("F:/OSINT_WAREHOUSE/osint_master.db")
conn = sqlite3.connect(str(DB_PATH), timeout=120.0)
cur = conn.cursor()

print("="*80)
print("CREATING BILATERAL PROCUREMENT LINKS")
print("="*80)

# Step 1: Load TED China contracts
print("\n1. Loading TED China contracts...")
print("-"*80)

cur.execute("""
    SELECT
        contract_id,
        buyer_country,
        publication_date,
        buyer_name,
        supplier_name,
        contract_value,
        currency,
        cpv_codes,
        description,
        china_role,
        detection_method
    FROM ted_china_contracts_fixed
    WHERE buyer_country IS NOT NULL
""")

contracts = cur.fetchall()
print(f"Found {len(contracts):,} TED contracts with Chinese involvement")

# Step 2: Create procurement links
print("\n2. Creating bilateral procurement links...")
print("-"*80)

links_created = 0
role_counts = {'buyer': 0, 'supplier': 0, 'both': 0}
country_links = {}

for (contract_id, buyer_country, pub_date, buyer_name, supplier_name,
     value, currency, cpv_codes, description, china_role, detection_method) in contracts:

    # Generate unique link_id
    link_id = f"TED_{contract_id}"

    # Determine strategic significance
    strategic_sig = []

    # High-value contracts (>€1M)
    if value and value > 1000000:
        strategic_sig.append(f"HIGH_VALUE:€{value/1000000:.1f}M")

    # Role-based significance
    if china_role == 'supplier':
        strategic_sig.append("CHINESE_SUPPLIER")
    elif china_role == 'buyer':
        strategic_sig.append("CHINESE_BUYER")
    elif china_role == 'both':
        strategic_sig.append("BILATERAL_CONTRACT")

    # Strategic sectors (CPV codes)
    if cpv_codes:
        strategic_cpv = []
        # ICT equipment (30200000)
        if '30200000' in cpv_codes or '32400000' in cpv_codes:
            strategic_cpv.append("ICT_EQUIPMENT")
        # Railway equipment (34600000)
        if '34600000' in cpv_codes or '34100000' in cpv_codes:
            strategic_cpv.append("RAIL_TRANSPORT")
        # Telecom (32500000)
        if '32500000' in cpv_codes or '32552000' in cpv_codes:
            strategic_cpv.append("TELECOMMUNICATIONS")
        # Energy (09000000, 31000000)
        if '09000000' in cpv_codes or '31000000' in cpv_codes:
            strategic_cpv.append("ENERGY_EQUIPMENT")
        # Defense (35000000)
        if '35000000' in cpv_codes:
            strategic_cpv.append("DEFENSE_EQUIPMENT")

        if strategic_cpv:
            strategic_sig.extend(strategic_cpv)

    # Detection method significance
    if detection_method:
        if 'name_match' in detection_method.lower():
            strategic_sig.append("VERIFIED_ENTITY")
        elif 'pattern' in detection_method.lower():
            strategic_sig.append("INFERRED_LINK")

    strategic_str = "; ".join(strategic_sig) if strategic_sig else None

    # Convert value to USD (approximate: 1 EUR = 1.1 USD)
    value_usd = value * 1.1 if value else None

    # Insert link
    try:
        conn.execute("""
            INSERT OR REPLACE INTO bilateral_procurement_links
            (link_id, country_code, ted_contract_id, contract_date,
             contract_value_usd, strategic_significance, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            link_id,
            buyer_country,
            contract_id,
            pub_date,
            value_usd,
            strategic_str,
            datetime.now()
        ))

        links_created += 1
        role_counts[china_role] = role_counts.get(china_role, 0) + 1
        country_links[buyer_country] = country_links.get(buyer_country, 0) + 1

        # Progress updates
        if links_created % 500 == 0:
            print(f"  Created {links_created:,} links...")
            conn.commit()

    except Exception as e:
        print(f"  ERROR creating link {link_id}: {e}")

conn.commit()

# Step 3: Verification
print("\n" + "="*80)
print("LINKAGE VERIFICATION")
print("="*80)

cur.execute('SELECT COUNT(*) FROM bilateral_procurement_links')
total_links = cur.fetchone()[0]
print(f"\nTotal procurement links: {total_links:,}")

# Links by country
print("\nLinks by country:")
cur.execute("""
    SELECT country_code, COUNT(*) as count
    FROM bilateral_procurement_links
    GROUP BY country_code
    ORDER BY count DESC
    LIMIT 15
""")
for country, count in cur.fetchall():
    print(f"  {country}: {count:,} contracts")

# Strategic significance analysis
print("\n" + "="*80)
print("STRATEGIC SIGNIFICANCE ANALYSIS")
print("="*80)

# High-value contracts
cur.execute("""
    SELECT COUNT(*)
    FROM bilateral_procurement_links
    WHERE strategic_significance LIKE '%HIGH_VALUE%'
""")
high_value = cur.fetchone()[0]
print(f"\nHigh-value contracts (>€1M): {high_value:,}")

# Chinese suppliers vs buyers
cur.execute("""
    SELECT COUNT(*)
    FROM bilateral_procurement_links
    WHERE strategic_significance LIKE '%CHINESE_SUPPLIER%'
""")
chinese_suppliers = cur.fetchone()[0]

cur.execute("""
    SELECT COUNT(*)
    FROM bilateral_procurement_links
    WHERE strategic_significance LIKE '%CHINESE_BUYER%'
""")
chinese_buyers = cur.fetchone()[0]

print(f"Chinese as supplier: {chinese_suppliers:,} contracts")
print(f"Chinese as buyer: {chinese_buyers:,} contracts")

# Strategic sectors
print("\nStrategic sectors:")
for sector in ['ICT_EQUIPMENT', 'RAIL_TRANSPORT', 'TELECOMMUNICATIONS',
               'ENERGY_EQUIPMENT', 'DEFENSE_EQUIPMENT']:
    cur.execute(f"""
        SELECT COUNT(*)
        FROM bilateral_procurement_links
        WHERE strategic_significance LIKE '%{sector}%'
    """)
    count = cur.fetchone()[0]
    if count > 0:
        print(f"  {sector.replace('_', ' ')}: {count:,} contracts")

# Sample high-value contracts
print("\n" + "="*80)
print("SAMPLE HIGH-VALUE STRATEGIC CONTRACTS")
print("="*80)

cur.execute("""
    SELECT
        bpl.country_code,
        bpl.contract_date,
        tc.supplier_name,
        tc.buyer_name,
        bpl.contract_value_usd,
        bpl.strategic_significance
    FROM bilateral_procurement_links bpl
    JOIN ted_china_contracts_fixed tc ON bpl.ted_contract_id = tc.contract_id
    WHERE bpl.contract_value_usd > 1000000
    ORDER BY bpl.contract_value_usd DESC
    LIMIT 10
""")

print("\nTop 10 highest-value contracts:")
for country, date, supplier, buyer, value_usd, significance in cur.fetchall():
    year = date[:4] if date else "????"
    supplier_str = (supplier[:40] if supplier else "Unknown")
    buyer_str = (buyer[:40] if buyer else "Unknown")
    value_str = f"${value_usd/1000000:.1f}M" if value_usd else "N/A"
    print(f"\n  [{country}] [{year}] {value_str}")
    print(f"    Supplier: {supplier_str}")
    print(f"    Buyer: {buyer_str}")
    if significance:
        print(f"    Strategic: {significance[:80]}")

# Temporal analysis
print("\n" + "="*80)
print("TEMPORAL ANALYSIS")
print("="*80)

cur.execute("""
    SELECT
        CAST(SUBSTR(contract_date, 1, 4) AS INTEGER) as year,
        COUNT(*) as count,
        SUM(contract_value_usd) as total_value
    FROM bilateral_procurement_links
    WHERE contract_date IS NOT NULL
    GROUP BY year
    ORDER BY year
""")

print("\nContracts by year:")
years = cur.fetchall()
if years:
    for year, count, total_value in years:
        value_str = f"${total_value/1000000:.0f}M" if total_value else "N/A"
        print(f"  {year}: {count:4,} contracts | {value_str:>10}")
else:
    print("  (No date data available)")

# Intelligence assessment
print("\n" + "="*80)
print("INTELLIGENCE ASSESSMENT")
print("="*80)

print(f"""
PROCUREMENT LINKAGE RESULTS:

COVERAGE:
  - {total_links:,} EU public procurement contracts with Chinese involvement
  - Spanning {len(country_links)} European countries
  - {len(years)} years of procurement data ({years[0][0]}-{years[-1][0]})

CHINA'S ROLE:
  - Supplier to EU: {chinese_suppliers:,} contracts ({100*chinese_suppliers/total_links:.1f}%)
  - Buyer from EU: {chinese_buyers:,} contracts ({100*chinese_buyers/total_links:.1f}%)
  - High-value deals (>€1M): {high_value:,} contracts

STRATEGIC SECTORS IDENTIFIED:
  - ICT Equipment, Rail Transport, Telecommunications
  - Energy Equipment, Defense Equipment
  - Enables tracking of critical infrastructure dependencies

TOP COUNTRIES:
  - Hungary: {country_links.get('HU', 0):,} contracts (largest)
  - Germany: {country_links.get('DE', 0):,} contracts
  - Netherlands: {country_links.get('NL', 0):,} contracts

INTELLIGENCE APPLICATIONS:
  - Track Chinese market penetration in EU public sector
  - Identify strategic dependency patterns (e.g., rail, telecom)
  - Monitor state-owned enterprise activity in Europe
  - Cross-reference with entity sanctions, security clearances
  - Assess compliance with EU procurement rules on Chinese suppliers
""")

print(f"\n[SUCCESS] Created {total_links:,} bilateral procurement links!")
conn.close()

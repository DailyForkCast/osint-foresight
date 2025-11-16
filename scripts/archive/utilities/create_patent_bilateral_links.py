#!/usr/bin/env python3
"""
Create Bilateral Patent Links
Links patents showing China-Europe collaboration to bilateral framework
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path("F:/OSINT_WAREHOUSE/osint_master.db")
conn = sqlite3.connect(str(DB_PATH), timeout=120.0)
cur = conn.cursor()

print("="*80)
print("CREATING BILATERAL PATENT LINKS")
print("="*80)

# EU country codes
EU_COUNTRIES = ['AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR',
                'DE', 'GR', 'HU', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'NL',
                'PL', 'PT', 'RO', 'SK', 'SI', 'ES', 'SE']

# Step 1: EPO Patents with Chinese entities
print("\n1. Processing EPO patents with Chinese involvement...")
print("-"*80)

cur.execute("""
    SELECT
        patent_id,
        applicant_country,
        filing_date,
        publication_date,
        applicant_name,
        technology_domain,
        ipc_classifications,
        risk_score,
        has_dual_use
    FROM epo_patents
    WHERE is_chinese_entity = 1
      AND applicant_country IS NOT NULL
""")

epo_patents = cur.fetchall()
print(f"Found {len(epo_patents):,} EPO patents with Chinese involvement")

epo_links = 0
for (patent_id, country, filing_date, pub_date, applicant, tech_domain,
     ipc_class, risk_score, dual_use) in epo_patents:

    # Determine if this is bilateral (European applicant working with Chinese entity)
    is_bilateral = country in EU_COUNTRIES

    if is_bilateral:
        link_id = f"EPO_{patent_id}"

        # Strategic significance
        strategic_sig = []
        strategic_sig.append(f"EU_CHINESE_COLLABORATION")

        if tech_domain:
            strategic_sig.append(f"TECH:{tech_domain.upper()}")

        if risk_score and risk_score > 50:
            strategic_sig.append(f"HIGH_RISK:score_{risk_score}")

        if dual_use:
            strategic_sig.append("DUAL_USE_TECHNOLOGY")

        strategic_str = "; ".join(strategic_sig) if strategic_sig else None

        try:
            conn.execute("""
                INSERT OR REPLACE INTO bilateral_patent_links
                (link_id, country_code, epo_patent_number, patent_filing_date,
                 technology_area, strategic_significance, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                link_id,
                country,
                patent_id,
                filing_date,
                tech_domain,
                strategic_str,
                datetime.now()
            ))
            epo_links += 1

            if epo_links % 1000 == 0:
                print(f"  Created {epo_links:,} EPO links...")
                conn.commit()

        except Exception as e:
            print(f"  ERROR creating EPO link {link_id}: {e}")

conn.commit()
print(f"Created {epo_links:,} EPO bilateral patent links")

# Step 2: USPTO PatentsView Chinese patents with European assignees
print("\n2. Processing USPTO patents with China-Europe collaboration...")
print("-"*80)

cur.execute("""
    SELECT
        patent_id,
        filing_date,
        filing_year,
        assignee_organization,
        assignee_country,
        detection_score,
        confidence
    FROM patentsview_patents_chinese
    WHERE assignee_country IN ('DE', 'FR', 'IT', 'ES', 'NL', 'SE', 'BE', 'AT',
                               'PL', 'DK', 'FI', 'IE', 'PT', 'RO', 'CZ', 'GR',
                               'HU', 'SK', 'BG', 'HR', 'SI', 'LT', 'LV', 'EE',
                               'CY', 'LU', 'MT')
""")

uspto_patents = cur.fetchall()
print(f"Found {len(uspto_patents):,} USPTO patents from European assignees with Chinese connections")

uspto_links = 0
confidence_counts = {'VERY_HIGH': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}

for patent_id, filing_date, filing_year, assignee, country, score, confidence in uspto_patents:

    link_id = f"USPTO_{patent_id}"

    # Strategic significance based on detection confidence
    strategic_sig = []

    if confidence == 'VERY_HIGH':
        strategic_sig.append("VERIFIED_CHINESE_ENTITY")
    elif confidence == 'HIGH':
        strategic_sig.append("LIKELY_CHINESE_ENTITY")
    else:
        strategic_sig.append("POSSIBLE_CHINESE_LINK")

    strategic_sig.append(f"EU_ASSIGNEE:{country}")
    strategic_sig.append("BILATERAL_PATENT")

    if score and score >= 90:
        strategic_sig.append("HIGH_CONFIDENCE")

    strategic_str = "; ".join(strategic_sig)

    # Use filing_date if available, otherwise construct from filing_year
    patent_date = filing_date if filing_date else f"{filing_year}-01-01" if filing_year else None

    try:
        conn.execute("""
            INSERT OR REPLACE INTO bilateral_patent_links
            (link_id, country_code, uspto_patent_number, patent_filing_date,
             technology_area, strategic_significance, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            link_id,
            country,
            patent_id,
            patent_date,
            None,  # Technology area not available in this table
            strategic_str,
            datetime.now()
        ))
        uspto_links += 1
        confidence_counts[confidence] = confidence_counts.get(confidence, 0) + 1

        if uspto_links % 100 == 0:
            print(f"  Created {uspto_links:,} USPTO links...")
            conn.commit()

    except Exception as e:
        print(f"  ERROR creating USPTO link {link_id}: {e}")

conn.commit()
print(f"Created {uspto_links:,} USPTO bilateral patent links")

# Step 3: Verification
print("\n" + "="*80)
print("LINKAGE VERIFICATION")
print("="*80)

cur.execute('SELECT COUNT(*) FROM bilateral_patent_links')
total_links = cur.fetchone()[0]
print(f"\nTotal bilateral patent links: {total_links:,}")

# Links by country
print("\nLinks by country:")
cur.execute("""
    SELECT country_code, COUNT(*) as count
    FROM bilateral_patent_links
    GROUP BY country_code
    ORDER BY count DESC
""")
for country, count in cur.fetchall():
    print(f"  {country}: {count:,} patents")

# Source distribution
cur.execute('SELECT COUNT(*) FROM bilateral_patent_links WHERE epo_patent_number IS NOT NULL')
epo_count = cur.fetchone()[0]

cur.execute('SELECT COUNT(*) FROM bilateral_patent_links WHERE uspto_patent_number IS NOT NULL')
uspto_count = cur.fetchone()[0]

print(f"\nBy source:")
print(f"  EPO patents: {epo_count:,}")
print(f"  USPTO patents: {uspto_count:,}")

# Strategic significance analysis
print("\n" + "="*80)
print("STRATEGIC SIGNIFICANCE ANALYSIS")
print("="*80)

# Confidence distribution (USPTO only)
print("\nConfidence distribution (USPTO patents):")
for conf_level in ['VERIFIED', 'LIKELY', 'POSSIBLE']:
    cur.execute(f"""
        SELECT COUNT(*)
        FROM bilateral_patent_links
        WHERE strategic_significance LIKE '%{conf_level}%'
    """)
    count = cur.fetchone()[0]
    if count > 0:
        print(f"  {conf_level}: {count:,} patents")

# Dual-use technologies
cur.execute("""
    SELECT COUNT(*)
    FROM bilateral_patent_links
    WHERE strategic_significance LIKE '%DUAL_USE%'
""")
dual_use_count = cur.fetchone()[0]
print(f"\nDual-use technologies: {dual_use_count:,} patents")

# High-risk patents
cur.execute("""
    SELECT COUNT(*)
    FROM bilateral_patent_links
    WHERE strategic_significance LIKE '%HIGH_RISK%'
""")
high_risk_count = cur.fetchone()[0]
print(f"High-risk patents: {high_risk_count:,} patents")

# Technology domains (EPO only)
print("\n" + "="*80)
print("TECHNOLOGY DOMAINS (EPO Patents)")
print("="*80)

cur.execute("""
    SELECT technology_area, COUNT(*) as count
    FROM bilateral_patent_links
    WHERE technology_area IS NOT NULL
    GROUP BY technology_area
    ORDER BY count DESC
    LIMIT 15
""")

print("\nTop technology domains:")
for tech, count in cur.fetchall():
    print(f"  {tech:30} {count:,} patents")

# Sample high-priority patents
print("\n" + "="*80)
print("SAMPLE HIGH-PRIORITY BILATERAL PATENTS")
print("="*80)

print("\nVerified Chinese Entity Patents (USPTO):")
cur.execute("""
    SELECT
        bpl.country_code,
        bpl.patent_filing_date,
        pv.assignee_organization,
        bpl.strategic_significance
    FROM bilateral_patent_links bpl
    JOIN patentsview_patents_chinese pv ON bpl.uspto_patent_number = pv.patent_id
    WHERE bpl.strategic_significance LIKE '%VERIFIED%'
    LIMIT 5
""")

for country, date, assignee, significance in cur.fetchall():
    year = date[:4] if date else "????"
    assignee_str = (assignee[:50] if assignee else "Unknown")
    print(f"\n  [{country}] [{year}]")
    print(f"    Assignee: {assignee_str}")
    print(f"    Strategic: {significance[:80]}")

# Temporal analysis
print("\n" + "="*80)
print("TEMPORAL ANALYSIS")
print("="*80)

cur.execute("""
    SELECT
        CAST(SUBSTR(patent_filing_date, 1, 4) AS INTEGER) as year,
        COUNT(*) as count
    FROM bilateral_patent_links
    WHERE patent_filing_date IS NOT NULL
    GROUP BY year
    ORDER BY year
""")

print("\nPatents by year:")
years = cur.fetchall()
if years:
    for year, count in years:
        if 2000 <= year <= 2025:  # Filter reasonable years
            print(f"  {year}: {count:4,} patents")
else:
    print("  (No date data available)")

# Intelligence assessment
print("\n" + "="*80)
print("INTELLIGENCE ASSESSMENT")
print("="*80)

print(f"""
BILATERAL PATENT LINKAGE RESULTS:

COVERAGE:
  - {total_links:,} patents showing China-Europe collaboration
  - {epo_count:,} from EPO (European Patent Office)
  - {uspto_count:,} from USPTO (Chinese & European co-assignees)
  - Spanning {len(set([row[0] for row in cur.execute('SELECT DISTINCT country_code FROM bilateral_patent_links').fetchall()]))} European countries

STRATEGIC ASSESSMENT:
  - Verified Chinese entities: {confidence_counts.get('VERY_HIGH', 0):,} patents
  - Likely Chinese entities: {confidence_counts.get('HIGH', 0):,} patents
  - Possible Chinese links: {confidence_counts.get('MEDIUM', 0) + confidence_counts.get('LOW', 0):,} patents
  - Dual-use technologies: {dual_use_count:,} patents
  - High-risk indicators: {high_risk_count:,} patents

TECHNOLOGY TRANSFER PATHWAYS:
  - Patents represent formal IP collaboration mechanisms
  - Can identify technology flows between institutions
  - Cross-reference with academic partnerships for complete picture
  - Track co-inventorship patterns over time

INTELLIGENCE APPLICATIONS:
  - Map technology transfer networks through patent co-assignees
  - Identify dual-use tech with China military-civilian fusion concerns
  - Monitor strategic dependency in critical technology areas
  - Assess compliance with export control regulations (EAR, EU dual-use)
  - Cross-reference patent assignees with entity sanctions lists

TOP COUNTRIES (by patent count):
""")

# Print top 5 countries
cur.execute("""
    SELECT country_code, COUNT(*) as count
    FROM bilateral_patent_links
    GROUP BY country_code
    ORDER BY count DESC
    LIMIT 5
""")
for i, (country, count) in enumerate(cur.fetchall(), 1):
    pct = 100 * count / total_links if total_links > 0 else 0
    print(f"  {i}. {country}: {count:,} patents ({pct:.1f}%)")

print(f"\n[SUCCESS] Created {total_links:,} bilateral patent links!")
conn.close()

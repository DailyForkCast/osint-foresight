#!/usr/bin/env python3
"""
Create Bilateral Academic Links
Links academic_partnerships to OpenAlex research outputs (works, collaborations)
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path("F:/OSINT_WAREHOUSE/osint_master.db")
conn = sqlite3.connect(str(DB_PATH), timeout=120.0)
cur = conn.cursor()

print("="*80)
print("CREATING BILATERAL ACADEMIC LINKS")
print("="*80)

# Step 1: Get all academic partnerships
print("\n1. Loading academic partnerships...")
print("-"*80)

cur.execute("""
    SELECT
        partnership_id,
        country_code,
        foreign_institution,
        chinese_institution,
        partnership_type,
        cooperation_areas
    FROM academic_partnerships
""")

partnerships = cur.fetchall()
print(f"Found {len(partnerships)} academic partnerships")

# Step 2: For each partnership, find related OpenAlex works
print("\n2. Finding related OpenAlex research outputs...")
print("-"*80)

links_created = 0
partnerships_with_links = 0
no_match_count = 0

for p_id, country, foreign_inst, chinese_inst, p_type, coop_areas in partnerships:

    # Search for OpenAlex works where both institutions appear as authors
    # This indicates actual research collaboration

    # Use simplified approach: find works with both institution names
    cur.execute("""
        SELECT DISTINCT w.work_id, w.title, w.publication_year
        FROM openalex_works w
        WHERE w.work_id IN (
            SELECT wa1.work_id
            FROM openalex_work_authors wa1
            WHERE wa1.institution_name LIKE ?
               OR wa1.institution_name LIKE ?
        )
        AND w.work_id IN (
            SELECT wa2.work_id
            FROM openalex_work_authors wa2
            WHERE wa2.institution_name LIKE ?
               OR wa2.institution_name LIKE ?
        )
        LIMIT 100
    """, (
        f"%{foreign_inst}%", f"%{foreign_inst.split()[0] if len(foreign_inst.split()) > 0 else foreign_inst}%",
        f"%{chinese_inst}%", f"%{chinese_inst.split()[0] if len(chinese_inst.split()) > 0 else chinese_inst}%"
    ))

    works = cur.fetchall()

    if works:
        partnerships_with_links += 1
        print(f"\n  {p_id}:")
        print(f"    {foreign_inst} <-> {chinese_inst}")
        print(f"    Found {len(works)} collaborative research outputs")

        for work_id, title, year in works[:5]:  # Show first 5
            # Create link record
            link_id = f"{p_id}_{work_id.split('/')[-1]}"

            try:
                conn.execute("""
                    INSERT OR REPLACE INTO bilateral_academic_links
                    (link_id, country_code, openalex_work_id, collaboration_date,
                     collaboration_type, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    link_id,
                    country,
                    work_id,
                    f"{year}-01-01" if year else None,
                    p_type,
                    datetime.now()
                ))

                links_created += 1

                print(f"      [{year}] {title[:60]}...")

            except Exception as e:
                print(f"      ERROR creating link: {e}")

        if len(works) > 5:
            print(f"      ... and {len(works)-5} more works")
            # Create links for remaining works too
            for work_id, title, year in works[5:]:
                link_id = f"{p_id}_{work_id.split('/')[-1]}"
                try:
                    conn.execute("""
                        INSERT OR REPLACE INTO bilateral_academic_links
                        (link_id, country_code, openalex_work_id, collaboration_date,
                         collaboration_type, created_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        link_id,
                        country,
                        work_id,
                        f"{year}-01-01" if year else None,
                        p_type,
                        datetime.now()
                    ))
                    links_created += 1
                except:
                    pass
    else:
        no_match_count += 1

conn.commit()

# Step 3: Verification
print("\n" + "="*80)
print("LINKAGE VERIFICATION")
print("="*80)

cur.execute('SELECT COUNT(*) FROM bilateral_academic_links')
total_links = cur.fetchone()[0]
print(f"\nTotal links created: {total_links:,}")
print(f"Partnerships with links: {partnerships_with_links}/{len(partnerships)} ({100*partnerships_with_links/len(partnerships):.1f}%)")
print(f"Partnerships without matches: {no_match_count}")

# Links by country
cur.execute("""
    SELECT country_code, COUNT(*) as count
    FROM bilateral_academic_links
    GROUP BY country_code
    ORDER BY count DESC
""")

print("\nLinks by country:")
for country, count in cur.fetchall():
    print(f"  {country}: {count:,} research outputs")

# Links by year
cur.execute("""
    SELECT
        CAST(SUBSTR(collaboration_date, 1, 4) AS INTEGER) as year,
        COUNT(*) as count
    FROM bilateral_academic_links
    WHERE collaboration_date IS NOT NULL
    GROUP BY year
    ORDER BY year
""")

print("\nLinks by year:")
years = cur.fetchall()
if years:
    for year, count in years:
        print(f"  {year}: {count:,} outputs")
else:
    print("  (No year data available)")

# Sample links
print("\n" + "="*80)
print("SAMPLE COLLABORATIVE RESEARCH OUTPUTS")
print("="*80)

cur.execute("""
    SELECT
        bal.link_id,
        bal.country_code,
        bal.collaboration_date,
        w.title,
        w.cited_by_count
    FROM bilateral_academic_links bal
    JOIN openalex_works w ON bal.openalex_work_id = w.work_id
    ORDER BY w.cited_by_count DESC
    LIMIT 10
""")

print("\nTop 10 most-cited collaborative works:")
for link_id, country, date, title, citations in cur.fetchall():
    year = date[:4] if date else "????"
    print(f"\n  [{country}] [{year}] {title[:70]}")
    print(f"    Citations: {citations if citations else 0}")

# Strategic assessment
print("\n" + "="*80)
print("STRATEGIC ASSESSMENT")
print("="*80)

print(f"""
ACADEMIC LINKAGE RESULTS:

COVERAGE:
  - {len(partnerships)} academic partnerships analyzed
  - {partnerships_with_links} partnerships ({100*partnerships_with_links/len(partnerships):.1f}%) have traceable research outputs
  - {total_links:,} collaborative research works linked
  - {no_match_count} partnerships without OpenAlex matches

LINKAGE METHOD:
  - Matched institution names in OpenAlex work authorship
  - Required both institutions to appear on same work
  - Limited to 100 works per partnership to avoid overwhelming data

GAPS AND LIMITATIONS:

Partnerships WITHOUT Matches ({no_match_count}):
  - May use different institution names in publications
  - May be newer partnerships (research not yet published)
  - May focus on non-research activities (student exchanges, conferences)
  - OpenAlex coverage gaps (not all journals indexed)

RECOMMENDED IMPROVEMENTS:
  1. Add fuzzy matching for institution name variations
  2. Link to CORDIS projects (EU research funding)
  3. Link to ArXiv preprints (faster than journal publications)
  4. Add manual curation for strategic partnerships (Seven Sons, Huawei)

INTELLIGENCE VALUE:
  - Can now trace actual research outputs from partnerships
  - Can identify most productive collaborations by publication count
  - Can assess technology transfer via research topics and citations
  - Can track collaboration intensity over time
""")

print(f"\n[SUCCESS] Created {total_links:,} academic partnership links!")
conn.close()

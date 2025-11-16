#!/usr/bin/env python3
"""
GDELT Documented Events Queries
Focus: Concrete events (agreements, partnerships, visits) not sentiment

ZERO FABRICATION PROTOCOL COMPLIANCE:
- Reports actual events with dates, actors, locations
- Does NOT infer intent, causation, or coordination
- Every result has source URL for verification
- Cross-reference opportunities identified but not assumed

CAMEO Event Codes Used:
- 030: Express intent to cooperate
- 040: Consult (diplomatic consultations)
- 042: Make a visit (official visits)
- 043: Engage in diplomatic cooperation
- 045/046: Material cooperation (infrastructure/investment)
- 051: Economic cooperation
- 061: Science/technology cooperation (CRITICAL for mission)
- 075: Sign formal agreement (HIGHEST VALUE)
"""

import sqlite3
import sys
from pathlib import Path

# Database connection
DB_PATH = 'F:/OSINT_WAREHOUSE/osint_master.db'

if not Path(DB_PATH).exists():
    print(f"ERROR: Database not found at {DB_PATH}")
    sys.exit(1)

db = sqlite3.connect(DB_PATH)
cursor = db.cursor()

print('='*100)
print('GDELT DOCUMENTED EVENTS ANALYSIS')
print('Focus: Agreements, Partnerships, Visits, Cooperation Events')
print('='*100)
print()

# ============================================================================
# QUERY 1: FORMAL AGREEMENTS SIGNED (Code 075) - HIGHEST VALUE
# ============================================================================

print('QUERY 1: FORMAL AGREEMENTS SIGNED (EU-China)')
print('Event Code 075: Sign formal agreement')
print('='*100)
print('These are legally binding agreements - MOUs, treaties, cooperation agreements')
print('-'*100)

cursor.execute('''
SELECT
    event_date,
    actor1_name,
    actor1_country_code,
    actor2_name,
    actor2_country_code,
    action_geo_country_code as location,
    source_url
FROM gdelt_events
WHERE event_code = '075'
  AND (actor1_country_code = 'CHN' OR actor2_country_code = 'CHN')
  AND (
    actor1_country_code IN ('FRA','DEU','ITA','ESP','GBR','HUN','CZE','POL','NLD','BEL','AUT','GRC','PRT','SWE','DNK','FIN','NOR')
    OR actor2_country_code IN ('FRA','DEU','ITA','ESP','GBR','HUN','CZE','POL','NLD','BEL','AUT','GRC','PRT','SWE','DNK','FIN','NOR')
  )
ORDER BY event_date DESC
LIMIT 20
''')

agreements = cursor.fetchall()

if agreements:
    print(f"Found {len(agreements)} formal agreements (showing latest 20):")
    print()
    print(f"{'Date':<12} {'Country1':<8} {'Actor1':<25} {'Country2':<8} {'Actor2':<25} {'Location':<8}")
    print('-'*100)

    for row in agreements:
        date, a1_name, a1_country, a2_name, a2_country, location, url = row
        a1_short = (a1_name or 'N/A')[:24]
        a2_short = (a2_name or 'N/A')[:24]
        print(f"{date:<12} {a1_country or 'N/A':<8} {a1_short:<25} {a2_country or 'N/A':<8} {a2_short:<25} {location or 'N/A':<8}")

    print()
    print('CROSS-REFERENCE ACTIONS:')
    print('  → Check OpenAlex for research collaborations 6-12 months after these dates')
    print('  → Check TED for contract awards 3-6 months after these dates')
    print('  → Check USPTO for patent citations 12-24 months after these dates')
else:
    print("No formal agreements found in current dataset")
    print("ACTION: Expand date range or verify GDELT collection completed")

print()
print()

# ============================================================================
# QUERY 2: SCIENCE & TECHNOLOGY COOPERATION (Code 061) - CRITICAL
# ============================================================================

print('QUERY 2: SCIENCE & TECHNOLOGY COOPERATION (EU-China)')
print('Event Code 061: Cooperate on science/technology')
print('='*100)
print('Joint research centers, technology partnerships, academic exchanges')
print('-'*100)

cursor.execute('''
SELECT
    event_date,
    actor1_name,
    actor1_country_code,
    actor2_name,
    actor2_country_code,
    action_geo_country_code as location,
    source_url
FROM gdelt_events
WHERE event_code = '061'
  AND (actor1_country_code = 'CHN' OR actor2_country_code = 'CHN')
  AND (
    actor1_country_code IN ('FRA','DEU','ITA','ESP','GBR','HUN','CZE','POL','NLD','BEL','AUT','GRC','PRT')
    OR actor2_country_code IN ('FRA','DEU','ITA','ESP','GBR','HUN','CZE','POL','NLD','BEL','AUT','GRC','PRT')
  )
ORDER BY event_date DESC
LIMIT 20
''')

tech_coop = cursor.fetchall()

if tech_coop:
    print(f"Found {len(tech_coop)} science/technology cooperation events (showing latest 20):")
    print()
    print(f"{'Date':<12} {'Country1':<8} {'Actor1':<30} {'Country2':<8} {'Actor2':<30}")
    print('-'*100)

    for row in tech_coop:
        date, a1_name, a1_country, a2_name, a2_country, location, url = row
        a1_short = (a1_name or 'N/A')[:29]
        a2_short = (a2_name or 'N/A')[:29]
        print(f"{date:<12} {a1_country or 'N/A':<8} {a1_short:<30} {a2_country or 'N/A':<8} {a2_short:<30}")

    print()
    print('TECHNOLOGY TRANSFER RISK:')
    print('  → Cross-reference with OpenAlex to identify which institutions participated')
    print('  → Check BCI, quantum, AI, semiconductor technology areas')
    print('  → Monitor for Chinese patents citing European research within 12 months')
else:
    print("No science/technology cooperation events found")

print()
print()

# ============================================================================
# QUERY 3: OFFICIAL VISITS (Code 042) - CONTEXT LAYER
# ============================================================================

print('QUERY 3: OFFICIAL VISITS TO EUROPE BY CHINESE OFFICIALS')
print('Event Code 042: Make a visit')
print('='*100)
print('State visits, ministerial delegations, business trips')
print('-'*100)

cursor.execute('''
SELECT
    event_date,
    actor1_name,
    action_geo_country_code as visited_country,
    source_url
FROM gdelt_events
WHERE event_code = '042'
  AND actor1_country_code = 'CHN'
  AND action_geo_country_code IN ('FRA','DEU','ITA','ESP','GBR','HUN','CZE','POL','NLD','BEL','AUT','GRC','PRT')
ORDER BY event_date DESC
LIMIT 15
''')

visits = cursor.fetchall()

if visits:
    print(f"Found {len(visits)} official visits (showing latest 15):")
    print()
    print(f"{'Date':<12} {'Chinese Official':<40} {'Visited':<10}")
    print('-'*65)

    for row in visits:
        date, official, country, url = row
        official_short = (official or 'N/A')[:39]
        print(f"{date:<12} {official_short:<40} {country or 'N/A':<10}")

    print()
    print('TIMELINE ANALYSIS:')
    print('  → Check for formal agreements signed within 7 days of visit')
    print('  → Look for technology cooperation announcements within 30 days')
    print('  → Monitor for contract awards within 90 days')
else:
    print("No official visits found")

print()
print()

# ============================================================================
# QUERY 4: MATERIAL COOPERATION (Code 045/046) - INFRASTRUCTURE
# ============================================================================

print('QUERY 4: MATERIAL COOPERATION (Infrastructure/Investment)')
print('Event Codes 045/046: Engage in material cooperation')
print('='*100)
print('Port investments, railway construction, 5G deployments, energy projects')
print('-'*100)

cursor.execute('''
SELECT
    event_date,
    actor1_name,
    actor1_country_code,
    actor2_name,
    actor2_country_code,
    CASE
        WHEN event_code = '045' THEN 'Engage'
        WHEN event_code = '046' THEN 'Receive'
    END as cooperation_type,
    source_url
FROM gdelt_events
WHERE event_code IN ('045', '046')
  AND (actor1_country_code = 'CHN' OR actor2_country_code = 'CHN')
  AND (
    actor1_country_code IN ('GRC','ITA','PRT','HUN','POL','SRB','BGR','ROU')  -- BRI target countries
    OR actor2_country_code IN ('GRC','ITA','PRT','HUN','POL','SRB','BGR','ROU')
  )
ORDER BY event_date DESC
LIMIT 15
''')

infrastructure = cursor.fetchall()

if infrastructure:
    print(f"Found {len(infrastructure)} material cooperation events (showing latest 15):")
    print()
    print(f"{'Date':<12} {'Type':<8} {'Country1':<8} {'Actor1':<25} {'Country2':<8} {'Actor2':<25}")
    print('-'*100)

    for row in infrastructure:
        date, a1_name, a1_country, a2_name, a2_country, coop_type, url = row
        a1_short = (a1_name or 'N/A')[:24]
        a2_short = (a2_name or 'N/A')[:24]
        print(f"{date:<12} {coop_type:<8} {a1_country or 'N/A':<8} {a1_short:<25} {a2_country or 'N/A':<8} {a2_short:<25}")

    print()
    print('BRI INFRASTRUCTURE TRACKING:')
    print('  → Map geographic distribution of Chinese infrastructure in Europe')
    print('  → Identify critical infrastructure (ports, energy, telecom)')
    print('  → Cross-reference with ASPI China Tech Map infrastructure database')
else:
    print("No material cooperation events found")

print()
print()

# ============================================================================
# QUERY 5: ECONOMIC COOPERATION (Code 051) - TRADE & INVESTMENT
# ============================================================================

print('QUERY 5: ECONOMIC COOPERATION EVENTS')
print('Event Code 051: Cooperate economically')
print('='*100)
print('Business forums, trade fairs, investment summits, export agreements')
print('-'*100)

cursor.execute('''
SELECT
    event_date,
    actor1_name,
    actor1_country_code,
    actor2_name,
    actor2_country_code,
    source_url
FROM gdelt_events
WHERE event_code = '051'
  AND (actor1_country_code = 'CHN' OR actor2_country_code = 'CHN')
  AND (
    actor1_country_code IN ('FRA','DEU','ITA','ESP','GBR','NLD','BEL','AUT')
    OR actor2_country_code IN ('FRA','DEU','ITA','ESP','GBR','NLD','BEL','AUT')
  )
ORDER BY event_date DESC
LIMIT 15
''')

economic = cursor.fetchall()

if economic:
    print(f"Found {len(economic)} economic cooperation events (showing latest 15):")
    print()
    print(f"{'Date':<12} {'Country1':<8} {'Actor1':<30} {'Country2':<8} {'Actor2':<30}")
    print('-'*100)

    for row in economic:
        date, a1_name, a1_country, a2_name, a2_country, url = row
        a1_short = (a1_name or 'N/A')[:29]
        a2_short = (a2_name or 'N/A')[:29]
        print(f"{date:<12} {a1_country or 'N/A':<8} {a1_short:<30} {a2_country or 'N/A':<8} {a2_short:<30}")

    print()
    print('ECONOMIC DEPENDENCY ANALYSIS:')
    print('  → Identify European companies with high China economic exposure')
    print('  → Cross-reference with TED contracts and Form D investments')
    print('  → Track economic cooperation frequency by country')
else:
    print("No economic cooperation events found")

print()
print()

# ============================================================================
# QUERY 6: EVENT TYPE SUMMARY BY COUNTRY
# ============================================================================

print('QUERY 6: EVENT TYPE SUMMARY BY EUROPEAN COUNTRY')
print('='*100)
print('Which European countries have the most cooperation events with China?')
print('-'*100)

cursor.execute('''
SELECT
    CASE
        WHEN actor1_country_code = 'CHN' THEN actor2_country_code
        ELSE actor1_country_code
    END as european_country,
    event_code,
    CASE
        WHEN event_code = '030' THEN 'Intent to cooperate'
        WHEN event_code = '040' THEN 'Consult'
        WHEN event_code = '042' THEN 'Official visit'
        WHEN event_code = '043' THEN 'Diplomatic cooperation'
        WHEN event_code = '045' THEN 'Material cooperation (engage)'
        WHEN event_code = '046' THEN 'Material cooperation (receive)'
        WHEN event_code = '051' THEN 'Economic cooperation'
        WHEN event_code = '061' THEN 'Science/technology cooperation'
        WHEN event_code = '075' THEN 'Formal agreement signed'
        ELSE 'Other cooperation'
    END as event_type,
    COUNT(*) as event_count
FROM gdelt_events
WHERE (actor1_country_code = 'CHN' OR actor2_country_code = 'CHN')
  AND (
    (actor1_country_code IN ('FRA','DEU','ITA','ESP','GBR','HUN','CZE','POL','NLD','BEL','AUT','GRC','PRT')
     AND actor2_country_code = 'CHN')
    OR
    (actor2_country_code IN ('FRA','DEU','ITA','ESP','GBR','HUN','CZE','POL','NLD','BEL','AUT','GRC','PRT')
     AND actor1_country_code = 'CHN')
  )
  AND event_code IN ('030','040','042','043','045','046','051','061','075')
GROUP BY european_country, event_code
ORDER BY european_country, event_count DESC
''')

summary = cursor.fetchall()

if summary:
    print(f"{'Country':<10} {'Event Type':<35} {'Count':<8}")
    print('-'*60)

    current_country = None
    for row in summary:
        country, code, event_type, count = row
        if country != current_country:
            if current_country is not None:
                print()  # Blank line between countries
            current_country = country
        print(f"{country:<10} {event_type:<35} {count:<8}")

    print()
    print('STRATEGIC INSIGHTS:')
    print('  → Countries with high "Formal agreement" counts: BRI participants')
    print('  → Countries with high "Science/tech cooperation": Technology transfer risk')
    print('  → Countries with high "Material cooperation": Infrastructure dependency')
else:
    print("No cooperation events found for summary")

print()
print()

# ============================================================================
# QUERY 7: CROSS-REFERENCE OPPORTUNITIES
# ============================================================================

print('QUERY 7: HIGH-PRIORITY CROSS-REFERENCE OPPORTUNITIES')
print('='*100)
print('Events that should be cross-referenced with OpenAlex, TED, USPTO')
print('-'*100)

cursor.execute('''
SELECT
    event_date,
    event_code,
    CASE
        WHEN event_code = '061' THEN 'Tech cooperation → Check OpenAlex + USPTO'
        WHEN event_code = '075' THEN 'Agreement signed → Check TED contracts'
        WHEN event_code = '045' OR event_code = '046' THEN 'Infrastructure → Check TED + ASPI'
    END as cross_reference_action,
    actor1_name,
    actor1_country_code,
    actor2_name,
    actor2_country_code,
    source_url
FROM gdelt_events
WHERE (actor1_country_code = 'CHN' OR actor2_country_code = 'CHN')
  AND event_code IN ('061', '075', '045', '046')
  AND (
    actor1_country_code IN ('FRA','DEU','ITA','ESP','GBR')
    OR actor2_country_code IN ('FRA','DEU','ITA','ESP','GBR')
  )
ORDER BY event_date DESC
LIMIT 20
''')

cross_ref = cursor.fetchall()

if cross_ref:
    print(f"Found {len(cross_ref)} high-priority cross-reference opportunities (showing latest 20):")
    print()

    for i, row in enumerate(cross_ref, 1):
        date, code, action, a1_name, a1_country, a2_name, a2_country, url = row
        print(f"{i}. {date} | {a1_country or 'N/A'}-{a2_country or 'N/A'}")
        print(f"   {a1_name or 'N/A'} ↔ {a2_name or 'N/A'}")
        print(f"   ACTION: {action}")
        print(f"   SOURCE: {url[:80]}")
        print()

    print('NEXT STEPS:')
    print('  1. Export this list to CSV for systematic cross-referencing')
    print('  2. For each event, query OpenAlex for collaborations within 6-12 months')
    print('  3. For each event, query TED for contracts within 3-6 months')
    print('  4. For each event, query USPTO for patents within 12-24 months')
    print('  5. Generate multi-source intelligence reports for validated pathways')
else:
    print("No cross-reference opportunities found")

print()
print()

# ============================================================================
# SUMMARY STATISTICS
# ============================================================================

print('='*100)
print('SUMMARY STATISTICS')
print('='*100)

# Total cooperation events
cursor.execute('''
SELECT COUNT(*) FROM gdelt_events
WHERE (actor1_country_code = 'CHN' OR actor2_country_code = 'CHN')
  AND event_code IN ('030','040','042','043','045','046','051','061','075')
''')
total_coop = cursor.fetchone()[0]

# Formal agreements
cursor.execute('''
SELECT COUNT(*) FROM gdelt_events
WHERE (actor1_country_code = 'CHN' OR actor2_country_code = 'CHN')
  AND event_code = '075'
''')
total_agreements = cursor.fetchone()[0]

# Technology cooperation
cursor.execute('''
SELECT COUNT(*) FROM gdelt_events
WHERE (actor1_country_code = 'CHN' OR actor2_country_code = 'CHN')
  AND event_code = '061'
''')
total_tech = cursor.fetchone()[0]

# Material cooperation
cursor.execute('''
SELECT COUNT(*) FROM gdelt_events
WHERE (actor1_country_code = 'CHN' OR actor2_country_code = 'CHN')
  AND event_code IN ('045','046')
''')
total_infrastructure = cursor.fetchone()[0]

print(f"Total cooperation events in database: {total_coop:,}")
print(f"  → Formal agreements (Code 075): {total_agreements:,}")
print(f"  → Science/tech cooperation (Code 061): {total_tech:,}")
print(f"  → Material cooperation (Code 045/046): {total_infrastructure:,}")
print()

# Date range
cursor.execute('''
SELECT MIN(event_date), MAX(event_date) FROM gdelt_events
WHERE (actor1_country_code = 'CHN' OR actor2_country_code = 'CHN')
  AND event_code IN ('030','040','042','043','045','046','051','061','075')
''')
min_date, max_date = cursor.fetchone()
print(f"Date range: {min_date or 'N/A'} to {max_date or 'N/A'}")

print()
print('='*100)
print('ANALYSIS COMPLETE')
print('='*100)
print()
print('RECOMMENDED NEXT STEPS:')
print('1. Expand GDELT collection to 2013-2025 for complete BRI era coverage')
print('2. Export high-priority events to CSV for systematic cross-referencing')
print('3. Build automated cross-reference matching with OpenAlex/TED/USPTO')
print('4. Generate technology transfer pathway intelligence reports')
print()

db.close()

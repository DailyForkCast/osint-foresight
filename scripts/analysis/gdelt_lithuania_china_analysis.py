#!/usr/bin/env python3
"""
GDELT Lithuania-China Event Analysis
Focus: Lithuania-Taiwan office events (2021-2022) and aftermath

This analysis uses the Lithuania case to demonstrate:
1. Event detection across all 89 CAMEO codes
2. Temporal event patterns
3. Cross-reference opportunities with other data sources
4. Relationship change indicators

Key Events Timeline:
- Jul 2021: Lithuania allows Taiwan to open representative office
- Aug 2021: China recalls ambassador, demands Lithuania withdraw approval
- Nov 2021: Taiwan office opens as "Taiwanese Representative Office"
- Dec 2021: China downgrades diplomatic relations
- Jan-Mar 2022: Economic measures increase (import restrictions, EU company pressure)
- 2023-2025: Gradual normalization attempts
"""

import sqlite3
import sys
from datetime import datetime
from collections import defaultdict

DB_PATH = 'F:/OSINT_WAREHOUSE/osint_master.db'

def get_event_type_description(code):
    """Return human-readable description for event code"""
    descriptions = {
        # Original codes
        '030': 'Express intent to cooperate',
        '040': 'Consult',
        '042': 'Make a visit',
        '043': 'Host a visit',
        '057': 'Sign formal agreement',
        '061': 'Cooperate economically',
        '064': 'Share intelligence or information',
        '120': 'Reject',
        '130': 'Threaten',
        '140': 'Engage in political dissent',

        # Diplomatic support/rhetoric
        '051': 'Praise or endorse',
        '052': 'Defend verbally',
        '019': 'Express accord',

        # Diplomatic engagement
        '044': 'Meet at a third location',
        '045': 'Mediate',
        '046': 'Engage in negotiation',

        # Appeals
        '022': 'Appeal for diplomatic cooperation',
        '026': 'Appeal to meet/negotiate',
        '0214': 'Appeal for intelligence',
        '1053': 'Demand release of persons',
        '021': 'Appeal for material cooperation',
        '0213': 'Appeal for judicial cooperation',
        '0232': 'Appeal for military aid',
        '0234': 'Appeal for military protection',

        # Aid/Investment
        '070': 'Provide aid',
        '071': 'Provide economic aid',
        '072': 'Provide military aid',
        '073': 'Provide humanitarian aid',
        '074': 'Provide military protection',

        # Sanctions
        '081': 'Ease administrative sanctions',
        '085': 'Ease economic sanctions',
        '163': 'Impose embargo/sanctions',
        '172': 'Impose administrative sanctions',

        # Legal/Security
        '111': 'Criticize or denounce',
        '112': 'Accuse',
        '1125': 'Accuse of espionage/treason',
        '1123': 'Accuse of aggression',
        '115': 'Bring lawsuit against',
        '116': 'Find guilty or liable',
        '173': 'Arrest, detain, charge',
        '1711': 'Confiscate property',

        # Deportations/Expulsions
        '174': 'Expel or deport individuals',
        '166': 'Expel or withdraw',

        # Investigations
        '092': 'Investigate human rights',
        '093': 'Investigate military action',

        # Intent/Planning
        '036': 'Express intent to meet/negotiate',
        '0311': 'Express intent to cooperate economically',
        '0331': 'Express intent to provide economic aid',
        '032': 'Express intent for diplomatic cooperation',
        '031': 'Express intent to cooperate materially',
        '0313': 'Express intent for judicial cooperation',
        '0332': 'Express intent to provide military aid',
        '0334': 'Express intent to provide military protection',

        # Complaints/Violations
        '114': 'Complain officially',
        '1042': 'Demand policy change',
        '102': 'Demand policy support',

        # Protests/Dissent
        '141': 'Demonstrate or rally',
        '143': 'Conduct strike or boycott',
        '144': 'Obstruct passage/block',

        # Releases/Asylum
        '0841': 'Return/release person(s)',
        '075': 'Grant asylum',

        # Military/Security Cooperation
        '062': 'Cooperate militarily',
        '050': 'Diplomatic cooperation (general)',
        '060': 'Material cooperation (general)',

        # Diplomatic Recognition
        '054': 'Grant diplomatic recognition',

        # Relationship Deterioration
        '161': 'Reduce or break diplomatic relations',
        '164': 'Halt negotiations',
        '125': 'Reject proposal to meet/negotiate',
        '128': 'Defy norms, law',
        '121': 'Reject material cooperation',
        '1241': 'Refuse to ease administrative sanctions',
        '1242': 'Refuse to ease popular dissent',

        # Multilateral
        '129': 'Veto',

        # Violent Events
        '181': 'Abduct, hijack, take hostage',
        '186': 'Assassinate',

        # Threats
        '131': 'Threaten non-force',
        '132': 'Threaten with administrative sanctions',
        '138': 'Threaten to use military force',
        '1381': 'Threaten blockade',
        '1382': 'Threaten occupation',
        '1383': 'Threaten unconventional violence',
        '1384': 'Threaten conventional attack',
        '1385': 'Threaten attack with WMD',

        # Force Posture
        '150': 'Demonstrate military/police power',

        # Coercion
        '170': 'Coerce, not specified',

        # Fight/Blockade
        '191': 'Impose blockade, restrict movement',

        # WMD
        '204': 'Use unconventional mass violence',
        '2041': 'Use CBR weapons',
        '2042': 'Detonate nuclear weapons',
    }
    return descriptions.get(code, f'Unknown code: {code}')

db = sqlite3.connect(DB_PATH)
cursor = db.cursor()

print('='*100)
print('LITHUANIA-CHINA GDELT EVENT ANALYSIS')
print('Test Case: Lithuania-Taiwan Office Events (2021-2022)')
print('='*100)
print()

# Overall statistics
cursor.execute("""
    SELECT COUNT(*)
    FROM gdelt_events
    WHERE (actor1_country_code = 'LTU' AND actor2_country_code = 'CHN')
       OR (actor1_country_code = 'CHN' AND actor2_country_code = 'LTU')
""")
total_events = cursor.fetchone()[0]

cursor.execute("""
    SELECT MIN(event_date), MAX(event_date)
    FROM gdelt_events
    WHERE (actor1_country_code = 'LTU' AND actor2_country_code = 'CHN')
       OR (actor1_country_code = 'CHN' AND actor2_country_code = 'LTU')
""")
date_range = cursor.fetchone()

print(f'Total Lithuania-China events: {total_events:,}')
print(f'Date range: {date_range[0]} to {date_range[1]}')
print()

# Event breakdown by CAMEO code
print('='*100)
print('EVENT BREAKDOWN BY CAMEO CODE')
print('='*100)

cursor.execute("""
    SELECT event_code, COUNT(*) as count
    FROM gdelt_events
    WHERE (actor1_country_code = 'LTU' AND actor2_country_code = 'CHN')
       OR (actor1_country_code = 'CHN' AND actor2_country_code = 'LTU')
    GROUP BY event_code
    ORDER BY count DESC
""")

event_breakdown = cursor.fetchall()
print(f"{'Code':<6} {'Count':>6} {'Description':<60}")
print('-'*100)
for code, count in event_breakdown[:30]:  # Top 30
    desc = get_event_type_description(code)
    print(f"{code:<6} {count:>6} {desc:<60}")

print()
print(f'Total unique event codes: {len(event_breakdown)}')
print()

# Temporal analysis by year-month
print('='*100)
print('TEMPORAL ANALYSIS: Lithuania-China Event Timeline')
print('='*100)

cursor.execute("""
    SELECT
        SUBSTR(event_date, 1, 6) as year_month,
        COUNT(*) as total_events,
        SUM(CASE WHEN event_code IN ('161', '164', '125', '128', '163', '172') THEN 1 ELSE 0 END) as deterioration_events,
        SUM(CASE WHEN event_code IN ('130', '131', '132', '138', '1381', '1382', '1383', '1384', '1385') THEN 1 ELSE 0 END) as threat_events,
        SUM(CASE WHEN event_code IN ('111', '112', '1123', '1125') THEN 1 ELSE 0 END) as criticism_events,
        SUM(CASE WHEN event_code IN ('051', '052', '019', '057', '061') THEN 1 ELSE 0 END) as cooperation_events
    FROM gdelt_events
    WHERE (actor1_country_code = 'LTU' AND actor2_country_code = 'CHN')
       OR (actor1_country_code = 'CHN' AND actor2_country_code = 'LTU')
    GROUP BY year_month
    ORDER BY year_month
""")

temporal_data = cursor.fetchall()

print(f"{'Year-Month':<12} {'Total':>6} {'Deterior':>8} {'Threats':>8} {'Criticism':>10} {'Cooperate':>10}")
print('-'*100)

for ym, total, determ, threat, critic, coop in temporal_data:
    year = ym[:4]
    month = ym[4:6]
    print(f"{year}-{month:<7} {total:>6} {determ:>8} {threat:>8} {critic:>10} {coop:>10}")

print()

# Peak event identification
print('='*100)
print('PEAK EVENT ANALYSIS')
print('='*100)

# Find peak deterioration months
cursor.execute("""
    SELECT
        SUBSTR(event_date, 1, 6) as year_month,
        COUNT(*) as deterioration_count
    FROM gdelt_events
    WHERE (actor1_country_code = 'LTU' AND actor2_country_code = 'CHN')
       OR (actor1_country_code = 'CHN' AND actor2_country_code = 'LTU')
      AND event_code IN ('161', '164', '125', '128', '163', '172')
    GROUP BY year_month
    ORDER BY deterioration_count DESC
    LIMIT 10
""")

print('Top 10 months with most relationship deterioration events:')
print(f"{'Year-Month':<12} {'Deterioration Events':>20}")
print('-'*50)
for ym, count in cursor.fetchall():
    year, month = ym[:4], ym[4:6]
    print(f"{year}-{month:<7} {count:>20}")

print()

# Key events during peak months
print('='*100)
print('KEY EVENTS: December 2021 (Peak Activity Month)')
print('='*100)

cursor.execute("""
    SELECT
        event_date,
        event_code,
        actor1_name,
        actor2_name,
        source_url
    FROM gdelt_events
    WHERE (actor1_country_code = 'LTU' AND actor2_country_code = 'CHN')
       OR (actor1_country_code = 'CHN' AND actor2_country_code = 'LTU')
      AND SUBSTR(event_date, 1, 6) = '202112'
    ORDER BY event_date DESC
    LIMIT 50
""")

dec_2021_events = cursor.fetchall()
print(f"Found {len(dec_2021_events)} events in December 2021 (showing latest 50)")
print()
print(f"{'Date':<12} {'Code':<6} {'Actor1':<25} {'Actor2':<25} {'Event Type':<40}")
print('-'*100)

for date, code, a1, a2, url in dec_2021_events[:20]:
    desc = get_event_type_description(code)
    a1_short = (a1 or 'N/A')[:24]
    a2_short = (a2 or 'N/A')[:24]
    print(f"{date:<12} {code:<6} {a1_short:<25} {a2_short:<25} {desc[:38]:<40}")

print()

# Economic measures events
print('='*100)
print('ECONOMIC MEASURES ANALYSIS')
print('='*100)

cursor.execute("""
    SELECT
        event_date,
        event_code,
        actor1_name,
        actor2_name
    FROM gdelt_events
    WHERE (actor1_country_code = 'LTU' AND actor2_country_code = 'CHN')
       OR (actor1_country_code = 'CHN' AND actor2_country_code = 'LTU')
      AND event_code IN ('163', '172', '170', '191')  -- Sanctions, coercion, blockades
    ORDER BY event_date DESC
    LIMIT 20
""")

economic_events = cursor.fetchall()
if economic_events:
    print(f"Economic measures events (latest 20):")
    print()
    for date, code, a1, a2 in economic_events:
        desc = get_event_type_description(code)
        print(f"{date}: {code} ({desc}) - {a1} -> {a2}")
else:
    print("No economic measures events found")

print()

# Cross-reference opportunities
print('='*100)
print('CROSS-REFERENCE OPPORTUNITIES FOR LITHUANIA CASE')
print('='*100)
print()
print('1. TRADE DATA (COMTRADE/Eurostat):')
print('   -> Analyze Lithuania-China bilateral trade 2020-2023')
print('   -> Track import/export changes during the period (Dec 2021-Mar 2022)')
print('   -> Verify economic measures claims with actual trade data')
print()
print('2. PROCUREMENT (TED):')
print('   -> Check if Lithuanian govt excluded Chinese firms (Huawei, etc.)')
print('   -> Track Taiwanese company contracts in Lithuania')
print()
print('3. SANCTIONS (Open Sanctions, BIS):')
print('   -> Cross-reference accused/sanctioned entities')
print('   -> Verify entity identities with GLEIF')
print()
print('4. ACADEMIC (OpenAlex/OpenAire/arXiv):')
print('   -> Track Lithuania-China research collaboration changes')
print('   -> Identify if academic partnerships changed')
print()
print('5. COMPANY OWNERSHIP (GLEIF, Companies House):')
print('   -> Track Lithuanian companies with China exposure')
print('   -> Identify subsidiary/ownership links')
print()
print('6. PATENTS (USPTO/EPO):')
print('   -> Monitor Lithuania-China joint patent applications')
print('   -> Track technology transfer changes')
print()

db.close()

print('='*100)
print('ANALYSIS COMPLETE')
print('='*100)

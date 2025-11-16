#!/usr/bin/env python3
"""
GDELT Documented Events Queries - COMPREHENSIVE EUROPEAN COVERAGE
VERIFIED AND CORRECTED - All codes verified against official CAMEO documentation

Focus: Concrete events (agreements, partnerships, visits) not sentiment

ZERO FABRICATION PROTOCOL COMPLIANCE:
- Reports actual events with dates, actors, locations
- Does NOT infer intent, causation, or coordination
- Every result has source URL for verification
- Cross-reference opportunities identified but not assumed
- ALL CODES VERIFIED against official CAMEO documentation (2025-11-02)

GEOGRAPHIC COVERAGE: ALL 50 EUROPEAN COUNTRIES
- EU27 member states
- EEA/EFTA countries (Norway, Iceland, Switzerland, Liechtenstein)
- Balkans (Albania, Bosnia, Serbia, Montenegro, North Macedonia)
- Eastern Europe (Ukraine, Belarus, Moldova)
- Caucasus (Georgia, Armenia, Azerbaijan)
- Turkey, UK, Russia, and other European states

CAMEO EVENT CODES USED (38 codes total - VERIFIED):

ORIGINAL CODES - VERIFIED (10 codes):
- 030: Express intent to cooperate
- 040: Consult
- 042: Make a visit
- 043: Host a visit
- 057: Sign formal agreement (HIGH VALUE)
- 061: Cooperate economically
- 064: Share intelligence or information
- 120: Reject
- 130: Threaten
- 140: Engage in political dissent

DIPLOMATIC ENGAGEMENT (3 codes):
- 045: Mediate (third-party mediation)
- 046: Engage in negotiation (bilateral/multilateral talks)
- 044: Meet at a third location (multilateral summits) - NEW

PHASE 1 - AID/INVESTMENT (3 codes):
- 070: Provide aid, not specified below
- 071: Provide economic aid (BRI)
- 072: Provide military aid

PHASE 1 - SANCTIONS (4 codes - CORRECTED):
- 081: Ease administrative sanctions
- 085: Ease economic sanctions, boycott, embargo - NEW (REAL ease sanctions code)
- 163: Impose embargo, boycott, or sanctions - NEW (REAL impose sanctions code)
- 172: Impose administrative sanctions

PHASE 1 - LEGAL/SECURITY (7 codes):
- 111: Criticize or denounce
- 112: Accuse, not specified below
- 1125: Accuse of espionage, treason
- 115: Bring lawsuit against
- 116: Find guilty or liable (legally)
- 173: Arrest, detain, or charge with legal action
- 1711: Confiscate property

PHASE 1 - DEPORTATIONS/EXPULSIONS (1 code - MOVED from sanctions):
- 174: Expel or deport individuals

PHASE 2 TIER 1 - INTENT/PLANNING (2 codes - NEW):
- 036: Express intent to meet or negotiate (1,668 events - CRITICAL)
- 0311: Express intent to cooperate economically (219 events)

PHASE 2 TIER 1 - COMPLAINTS/VIOLATIONS (2 codes - NEW):
- 114: Complain officially (176 events)
- 1042: Demand policy change (REAL policy change code, replacing 106)

PHASE 2 TIER 1 - PROTESTS/DISSENT (1 code - NEW):
- 141: Demonstrate or rally (208 events)

PHASE 2 TIER 1 - RELEASES (1 code - NEW):
- 0841: Return, release person(s) (171 events)

REMOVED CODES (with reasons):
- 051: Praise or endorse (was mislabeled as "Economic cooperation" - 1,865 events of diplomatic rhetoric, not cooperation)
- 0234: Appeal for military protection (was mislabeled as "technical aid" - not mission-relevant)
- 082: Ease political dissent (was mislabeled as "Ease economic sanctions" - wrong code)
- 106: Demand withdrawal (was mislabeled as "Demand policy change" - replaced with 1042)
"""

import sqlite3
import sys
from pathlib import Path

# Database connection
DB_PATH = 'F:/OSINT_WAREHOUSE/osint_master.db'

if not Path(DB_PATH).exists():
    print(f"ERROR: Database not found at {DB_PATH}")
    sys.exit(1)

# COMPREHENSIVE EUROPEAN COUNTRY LIST (50 countries)
# Based on ISO 3166-1 alpha-3 codes used by GDELT

EUROPEAN_COUNTRIES = [
    # EU27 Member States
    'AUT',  # Austria
    'BEL',  # Belgium
    'BGR',  # Bulgaria
    'HRV',  # Croatia
    'CYP',  # Cyprus
    'CZE',  # Czech Republic
    'DNK',  # Denmark
    'EST',  # Estonia
    'FIN',  # Finland
    'FRA',  # France
    'DEU',  # Germany
    'GRC',  # Greece
    'HUN',  # Hungary
    'IRL',  # Ireland
    'ITA',  # Italy
    'LVA',  # Latvia
    'LTU',  # Lithuania
    'LUX',  # Luxembourg
    'MLT',  # Malta
    'NLD',  # Netherlands
    'POL',  # Poland
    'PRT',  # Portugal
    'ROU',  # Romania
    'SVK',  # Slovakia
    'SVN',  # Slovenia
    'ESP',  # Spain
    'SWE',  # Sweden

    # EEA/EFTA (non-EU)
    'NOR',  # Norway
    'ISL',  # Iceland
    'CHE',  # Switzerland
    'LIE',  # Liechtenstein

    # United Kingdom (post-Brexit)
    'GBR',  # United Kingdom

    # Balkans
    'ALB',  # Albania
    'BIH',  # Bosnia and Herzegovina
    'SRB',  # Serbia
    'MNE',  # Montenegro
    'MKD',  # North Macedonia

    # Eastern Europe
    'UKR',  # Ukraine
    'BLR',  # Belarus
    'MDA',  # Moldova

    # Caucasus
    'GEO',  # Georgia
    'ARM',  # Armenia
    'AZE',  # Azerbaijan

    # Other European
    'TUR',  # Turkey
    'AND',  # Andorra
    'MCO',  # Monaco
    'SMR',  # San Marino
    'VAT',  # Vatican City
    'RUS',  # Russia (for completeness)
]

# Event codes we're tracking - ALL VERIFIED against official CAMEO
EVENT_CODES = [
    # Original codes - VERIFIED
    '030', '040', '042', '043', '057', '061', '064', '120', '130', '140',

    # Diplomatic engagement
    '044', '045', '046',

    # Phase 1: Aid/Investment
    '070', '071', '072',

    # Phase 1: Sanctions - CORRECTED
    '081', '085', '163', '172',

    # Phase 1: Legal/Security
    '111', '112', '1125', '115', '116', '173', '1711',

    # Phase 1: Deportations (moved from sanctions)
    '174',

    # Phase 2 Tier 1: Intent/Planning
    '036', '0311',

    # Phase 2 Tier 1: Complaints/Violations
    '114', '1042',

    # Phase 2 Tier 1: Protests
    '141',

    # Phase 2 Tier 1: Releases
    '0841',
]

# SQL-safe lists
COUNTRY_LIST_SQL = "'" + "','".join(EUROPEAN_COUNTRIES) + "'"
EVENT_CODE_LIST_SQL = "'" + "','".join(EVENT_CODES) + "'"

def get_event_type_description(code):
    """Return human-readable description for event code - ALL VERIFIED"""
    descriptions = {
        # Original codes - VERIFIED
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

        # Diplomatic engagement
        '044': 'Meet at a third location',
        '045': 'Mediate',
        '046': 'Engage in negotiation',

        # Phase 1: Aid/Investment
        '070': 'Provide aid, not specified below',
        '071': 'Provide economic aid',
        '072': 'Provide military aid',

        # Phase 1: Sanctions - CORRECTED
        '081': 'Ease administrative sanctions',
        '085': 'Ease economic sanctions, boycott, embargo',
        '163': 'Impose embargo, boycott, or sanctions',
        '172': 'Impose administrative sanctions',

        # Phase 1: Legal/Security
        '111': 'Criticize or denounce',
        '112': 'Accuse, not specified below',
        '1125': 'Accuse of espionage, treason',
        '115': 'Bring lawsuit against',
        '116': 'Find guilty or liable (legally)',
        '173': 'Arrest, detain, or charge with legal action',
        '1711': 'Confiscate property',

        # Phase 1: Deportations
        '174': 'Expel or deport individuals',

        # Phase 2 Tier 1: Intent/Planning
        '036': 'Express intent to meet or negotiate',
        '0311': 'Express intent to cooperate economically',

        # Phase 2 Tier 1: Complaints/Violations
        '114': 'Complain officially',
        '1042': 'Demand policy change',

        # Phase 2 Tier 1: Protests
        '141': 'Demonstrate or rally',

        # Phase 2 Tier 1: Releases
        '0841': 'Return, release person(s)',
    }
    return descriptions.get(code, 'Unknown code')

db = sqlite3.connect(DB_PATH)
cursor = db.cursor()

print('='*100)
print('GDELT DOCUMENTED EVENTS ANALYSIS - COMPREHENSIVE EUROPEAN COVERAGE')
print('*** VERIFIED AND CORRECTED VERSION ***')
print(f'Geographic Scope: {len(EUROPEAN_COUNTRIES)} European countries')
print(f'Event Types: {len(EVENT_CODES)} CAMEO codes (ALL VERIFIED against official documentation)')
print('Major Corrections: Fixed codes 046, 163, 174, 082, 106; Added codes 036, 141, 114, 0841, 085')
print('='*100)
print()

# ============================================================================
# QUERY 1: FORMAL AGREEMENTS SIGNED (Code 057) - HIGHEST VALUE
# ============================================================================

print('QUERY 1: FORMAL AGREEMENTS SIGNED (China-Europe)')
print('Event Code 057: Sign formal agreement')
print('='*100)
print('These are legally binding agreements - MOUs, treaties, cooperation agreements')
print(f'Coverage: All {len(EUROPEAN_COUNTRIES)} European countries')
print('-'*100)

query = f'''
SELECT
    event_date,
    actor1_name,
    actor1_country_code,
    actor2_name,
    actor2_country_code,
    action_geo_country_code as location,
    source_url
FROM gdelt_events
WHERE event_code = '057'
  AND (actor1_country_code = 'CHN' OR actor2_country_code = 'CHN')
  AND (
    actor1_country_code IN ({COUNTRY_LIST_SQL})
    OR actor2_country_code IN ({COUNTRY_LIST_SQL})
  )
ORDER BY event_date DESC
LIMIT 50
'''

cursor.execute(query)
agreements = cursor.fetchall()

if agreements:
    print(f"Found {len(agreements)} formal agreements (showing latest 50):")
    print()
    print(f"{'Date':<12} {'Cntry1':<6} {'Actor1':<30} {'Cntry2':<6} {'Actor2':<30} {'Location':<8}")
    print('-'*100)

    for row in agreements:
        date, a1_name, a1_country, a2_name, a2_country, location, url = row
        a1_short = (a1_name or 'N/A')[:29]
        a2_short = (a2_name or 'N/A')[:29]
        loc_short = (location or 'N/A')[:7]
        print(f"{date:<12} {a1_country or 'N/A':<6} {a1_short:<30} {a2_country or 'N/A':<6} {a2_short:<30} {loc_short:<8}")

    print()
    print('CROSS-REFERENCE ACTIONS:')
    print('  -> Check OpenAlex for research collaborations 6-12 months after these dates')
    print('  -> Check TED for contract awards 3-6 months after these dates')
    print('  -> Check USPTO for patent citations 12-24 months after these dates')
else:
    print("No formal agreements found in current dataset")
    print("ACTION: Expand date range or verify GDELT collection completed")

print()
print()

# ============================================================================
# QUERY 2: INTENT TO COOPERATE/NEGOTIATE (Codes 036, 0311) - NEW!
# ============================================================================

print('QUERY 2: INTENT TO COOPERATE/NEGOTIATE (China-Europe) - NEW QUERY')
print('Event Codes: 036 (Intent to meet/negotiate), 0311 (Intent to cooperate economically)')
print('='*100)
print('Pre-agreement positioning - signals of upcoming formal cooperation')
print('CRITICAL: Code 036 has 1,668 events - largest unused code')
print(f'Coverage: All {len(EUROPEAN_COUNTRIES)} European countries')
print('-'*100)

query = f'''
SELECT
    event_date,
    event_code,
    actor1_name,
    actor1_country_code,
    actor2_name,
    actor2_country_code,
    source_url
FROM gdelt_events
WHERE event_code IN ('036', '0311')
  AND (actor1_country_code = 'CHN' OR actor2_country_code = 'CHN')
  AND (
    actor1_country_code IN ({COUNTRY_LIST_SQL})
    OR actor2_country_code IN ({COUNTRY_LIST_SQL})
  )
ORDER BY event_date DESC
LIMIT 50
'''

cursor.execute(query)
intent_events = cursor.fetchall()

if intent_events:
    print(f"Found {len(intent_events)} intent events (showing latest 50):")
    print()
    print(f"{'Date':<12} {'Type':<8} {'Cntry1':<6} {'Actor1':<25} {'Cntry2':<6} {'Actor2':<25}")
    print('-'*100)

    for row in intent_events:
        date, code, a1_name, a1_country, a2_name, a2_country, url = row
        event_type = '036-Neg' if code == '036' else '0311-Econ'
        a1_short = (a1_name or 'N/A')[:24]
        a2_short = (a2_name or 'N/A')[:24]
        print(f"{date:<12} {event_type:<8} {a1_country or 'N/A':<6} {a1_short:<25} {a2_country or 'N/A':<6} {a2_short:<25}")

    print()
    print('INTELLIGENCE VALUE:')
    print('  -> Track which relationships are warming (intent statements before formal agreements)')
    print('  -> Monitor for formal agreements 3-12 months after intent statements')
    print('  -> Identify stalled negotiations (intent without follow-through)')
else:
    print("No intent events found in current dataset")

print()
print()

# ============================================================================
# QUERY 3: DIPLOMATIC ENGAGEMENT (Codes 045, 046, 044) - RESTRUCTURED
# ============================================================================

print('QUERY 3: DIPLOMATIC ENGAGEMENT (China-Europe) - RESTRUCTURED')
print('Event Codes: 045 (Mediate), 046 (Negotiate), 044 (Meet at third location)')
print('='*100)
print('Code 046 CORRECTED: Was labeled "Material cooperation" - actually "Engage in negotiation"')
print('Code 046 has 1,969 events - major mislabeling fixed!')
print(f'Coverage: All {len(EUROPEAN_COUNTRIES)} European countries')
print('-'*100)

query = f'''
SELECT
    event_date,
    event_code,
    actor1_name,
    actor1_country_code,
    actor2_name,
    actor2_country_code,
    source_url
FROM gdelt_events
WHERE event_code IN ('044', '045', '046')
  AND (actor1_country_code = 'CHN' OR actor2_country_code = 'CHN')
  AND (
    actor1_country_code IN ({COUNTRY_LIST_SQL})
    OR actor2_country_code IN ({COUNTRY_LIST_SQL})
  )
ORDER BY event_date DESC
LIMIT 50
'''

cursor.execute(query)
diplomatic_events = cursor.fetchall()

if diplomatic_events:
    print(f"Found {len(diplomatic_events)} diplomatic engagement events (showing latest 50):")
    print()
    print(f"{'Date':<12} {'Type':<10} {'Cntry1':<6} {'Actor1':<25} {'Cntry2':<6} {'Actor2':<25}")
    print('-'*100)

    for row in diplomatic_events:
        date, code, a1_name, a1_country, a2_name, a2_country, url = row
        event_type = {'044': '044-Meet3rd', '045': '045-Mediate', '046': '046-Negotiate'}[code]
        a1_short = (a1_name or 'N/A')[:24]
        a2_short = (a2_name or 'N/A')[:24]
        print(f"{date:<12} {event_type:<10} {a1_country or 'N/A':<6} {a1_short:<25} {a2_country or 'N/A':<6} {a2_short:<25}")

    print()
    print('INTELLIGENCE VALUE:')
    print('  -> Code 046 (Negotiate): Partnership talks, trade negotiations, cooperation frameworks')
    print('  -> Code 045 (Mediate): China as third-party mediator - diplomatic influence')
    print('  -> Code 044 (Meet 3rd): Multilateral summits, third-country meetings')
    print('  -> Monitor for formal agreements (057) following negotiations')
else:
    print("No diplomatic engagement events found")

print()
print()

# ============================================================================
# QUERY 4: AID & INVESTMENT PROVISION (Codes 070, 071, 072)
# ============================================================================

print('QUERY 4: AID & INVESTMENT PROVISION (China to Europe)')
print('Event Codes 070-072: Provide aid (general, economic/BRI, military)')
print('='*100)
print('BRI funding, grants, loans, infrastructure investment, military assistance')
print(f'Coverage: All {len(EUROPEAN_COUNTRIES)} European countries')
print('-'*100)

query = f'''
SELECT
    event_date,
    CASE
        WHEN event_code = '070' THEN 'Aid (general)'
        WHEN event_code = '071' THEN 'Economic aid (BRI)'
        WHEN event_code = '072' THEN 'Military aid'
    END as aid_type,
    actor1_country_code as from_country,
    actor1_name,
    actor2_country_code as to_country,
    actor2_name,
    source_url
FROM gdelt_events
WHERE event_code IN ('070', '071', '072')
  AND (actor1_country_code = 'CHN' OR actor2_country_code = 'CHN')
  AND (
    actor1_country_code IN ({COUNTRY_LIST_SQL})
    OR actor2_country_code IN ({COUNTRY_LIST_SQL})
  )
ORDER BY event_date DESC
LIMIT 50
'''

cursor.execute(query)
aid_events = cursor.fetchall()

if aid_events:
    print(f"Found {len(aid_events)} aid/investment events (showing latest 50):")
    print()
    print(f"{'Date':<12} {'Aid Type':<20} {'From':<6} {'Actor1':<25} {'To':<6} {'Actor2':<25}")
    print('-'*100)

    for row in aid_events:
        date, aid_type, from_c, a1, to_c, a2, url = row
        a1_short = (a1 or 'N/A')[:24]
        a2_short = (a2 or 'N/A')[:24]
        print(f"{date:<12} {aid_type:<20} {from_c or 'N/A':<6} {a1_short:<25} {to_c or 'N/A':<6} {a2_short:<25}")

    print()
    print('BRI INTELLIGENCE VALUE:')
    print('  -> Track which countries receive Chinese economic aid (BRI participants)')
    print('  -> Identify military aid recipients (defense dependencies)')
    print('  -> Cross-reference with ASPI China Tech Map infrastructure projects')
else:
    print("No aid/investment events found")

print()
print()

# ============================================================================
# QUERY 5: IMPOSE SANCTIONS (Codes 163, 172) - CORRECTED!
# ============================================================================

print('QUERY 5: IMPOSE SANCTIONS (Europe-China) - CORRECTED!')
print('Event Codes: 163 (Impose embargo/boycott/sanctions), 172 (Impose administrative sanctions)')
print('='*100)
print('MAJOR CORRECTION: Code 163 is the REAL economic sanctions code (not 174!)')
print('Code 163 has 188 events we were completely missing!')
print('5G bans, Huawei restrictions, trade sanctions, embargoes, export controls')
print(f'Coverage: All {len(EUROPEAN_COUNTRIES)} European countries')
print('-'*100)

query = f'''
SELECT
    event_date,
    CASE
        WHEN event_code = '163' THEN 'Impose embargo/boycott/sanctions'
        WHEN event_code = '172' THEN 'Impose administrative sanctions'
    END as action_type,
    actor1_country_code,
    actor1_name,
    actor2_country_code,
    actor2_name,
    source_url
FROM gdelt_events
WHERE event_code IN ('163', '172')
  AND (actor1_country_code = 'CHN' OR actor2_country_code = 'CHN')
  AND (
    actor1_country_code IN ({COUNTRY_LIST_SQL})
    OR actor2_country_code IN ({COUNTRY_LIST_SQL})
  )
ORDER BY event_date DESC
LIMIT 50
'''

cursor.execute(query)
sanctions_events = cursor.fetchall()

if sanctions_events:
    print(f"Found {len(sanctions_events)} sanction imposition events (showing latest 50):")
    print()
    print(f"{'Date':<12} {'Action Type':<35} {'Cntry1':<6} {'Actor1':<20}")
    print('-'*100)

    for row in sanctions_events:
        date, action_type, c1, a1, c2, a2, url = row
        a1_short = (a1 or 'N/A')[:19]
        print(f"{date:<12} {action_type:<35} {c1 or 'N/A':<6} {a1_short:<20}")

    print()
    print('POLICY INTELLIGENCE VALUE:')
    print('  -> Track 5G/Huawei ban timeline across European countries (code 163)')
    print('  -> Monitor technology export controls and embargoes (code 163)')
    print('  -> Identify administrative penalties and travel bans (code 172)')
    print('  -> Cross-reference with trade data for economic impact')
else:
    print("No sanction imposition events found")

print()
print()

# ============================================================================
# QUERY 6: EASE SANCTIONS (Codes 081, 085) - CORRECTED!
# ============================================================================

print('QUERY 6: EASE SANCTIONS (Europe-China) - CORRECTED!')
print('Event Codes: 081 (Ease administrative sanctions), 085 (Ease economic sanctions/embargo)')
print('='*100)
print('MAJOR CORRECTION: Code 085 is the REAL "ease economic sanctions" code (not 082!)')
print('Code 082 is actually "Ease political dissent" - completely different!')
print('Tracks sanctions de-escalation, 5G ban reversals, trade restriction easing')
print(f'Coverage: All {len(EUROPEAN_COUNTRIES)} European countries')
print('-'*100)

query = f'''
SELECT
    event_date,
    CASE
        WHEN event_code = '081' THEN 'Ease administrative sanctions'
        WHEN event_code = '085' THEN 'Ease economic sanctions/embargo'
    END as action_type,
    actor1_country_code,
    actor1_name,
    actor2_country_code,
    actor2_name,
    source_url
FROM gdelt_events
WHERE event_code IN ('081', '085')
  AND (actor1_country_code = 'CHN' OR actor2_country_code = 'CHN')
  AND (
    actor1_country_code IN ({COUNTRY_LIST_SQL})
    OR actor2_country_code IN ({COUNTRY_LIST_SQL})
  )
ORDER BY event_date DESC
LIMIT 50
'''

cursor.execute(query)
ease_sanctions = cursor.fetchall()

if ease_sanctions:
    print(f"Found {len(ease_sanctions)} sanctions easing events (showing latest 50):")
    print()
    print(f"{'Date':<12} {'Action Type':<35} {'Cntry1':<6} {'Actor1':<20}")
    print('-'*100)

    for row in ease_sanctions:
        date, action_type, c1, a1, c2, a2, url = row
        a1_short = (a1 or 'N/A')[:19]
        print(f"{date:<12} {action_type:<35} {c1 or 'N/A':<6} {a1_short:<20}")

    print()
    print('POLICY INTELLIGENCE VALUE:')
    print('  -> Track relationship warming (sanctions de-escalation)')
    print('  -> Monitor 5G/Huawei ban reversals or easings')
    print('  -> Identify technology export control relaxations')
else:
    print("No sanctions easing events found")

print()
print()

# ============================================================================
# QUERY 7: POLICY DEMANDS (Code 1042) - CORRECTED!
# ============================================================================

print('QUERY 7: POLICY DEMANDS (Code 1042) - CORRECTED!')
print('Event Code 1042: Demand policy change')
print('='*100)
print('MAJOR CORRECTION: Code 1042 is the REAL "demand policy change" code (not 106!)')
print('Code 106 is actually "Demand withdrawal" - military/territorial context')
print('Policy demands on Xinjiang, Hong Kong, tech practices, trade policies')
print(f'Coverage: All {len(EUROPEAN_COUNTRIES)} European countries')
print('-'*100)

query = f'''
SELECT
    event_date,
    actor1_country_code,
    actor1_name,
    actor2_country_code,
    actor2_name,
    source_url
FROM gdelt_events
WHERE event_code = '1042'
  AND (actor1_country_code = 'CHN' OR actor2_country_code = 'CHN')
  AND (
    actor1_country_code IN ({COUNTRY_LIST_SQL})
    OR actor2_country_code IN ({COUNTRY_LIST_SQL})
  )
ORDER BY event_date DESC
LIMIT 50
'''

cursor.execute(query)
policy_demands = cursor.fetchall()

if policy_demands:
    print(f"Found {len(policy_demands)} policy demand events (showing latest 50):")
    print()
    print(f"{'Date':<12} {'Cntry1':<6} {'Actor1':<30} {'Cntry2':<6} {'Actor2':<30}")
    print('-'*100)

    for row in policy_demands:
        date, c1, a1, c2, a2, url = row
        a1_short = (a1 or 'N/A')[:29]
        a2_short = (a2 or 'N/A')[:29]
        print(f"{date:<12} {c1 or 'N/A':<6} {a1_short:<30} {c2 or 'N/A':<6} {a2_short:<30}")

    print()
    print('POLICY INTELLIGENCE VALUE:')
    print('  -> Monitor EU/European demands on China (Xinjiang, Hong Kong, tech practices)')
    print('  -> Track Chinese demands on European policy (Taiwan, trade, etc.)')
else:
    print("No policy demand events found in current dataset")

print()
print()

# ============================================================================
# QUERY 8: LEGAL & SECURITY ACTIONS (Codes 111, 112, 1125, 115, 116, 173, 1711)
# ============================================================================

print('QUERY 8: LEGAL & SECURITY ACTIONS (Europe-China)')
print('Event Codes: Accusations (111/112/1125), Lawsuits (115/116), Arrests (173), Seizures (1711)')
print('='*100)
print('Espionage accusations, IP theft lawsuits, arrests, asset seizures')
print(f'Coverage: All {len(EUROPEAN_COUNTRIES)} European countries')
print('-'*100)

query = f'''
SELECT
    event_date,
    CASE
        WHEN event_code = '111' THEN 'Criticize/denounce'
        WHEN event_code = '112' THEN 'Accuse (general)'
        WHEN event_code = '1125' THEN 'Accuse of espionage'
        WHEN event_code = '115' THEN 'Bring lawsuit'
        WHEN event_code = '116' THEN 'Find guilty/liable'
        WHEN event_code = '173' THEN 'Arrest/detain/charge'
        WHEN event_code = '1711' THEN 'Confiscate property'
    END as action_type,
    actor1_country_code,
    actor1_name,
    actor2_country_code,
    actor2_name,
    source_url
FROM gdelt_events
WHERE event_code IN ('111', '112', '1125', '115', '116', '173', '1711')
  AND (actor1_country_code = 'CHN' OR actor2_country_code = 'CHN')
  AND (
    actor1_country_code IN ({COUNTRY_LIST_SQL})
    OR actor2_country_code IN ({COUNTRY_LIST_SQL})
  )
ORDER BY event_date DESC
LIMIT 50
'''

cursor.execute(query)
legal_events = cursor.fetchall()

if legal_events:
    print(f"Found {len(legal_events)} legal/security events (showing latest 50):")
    print()
    print(f"{'Date':<12} {'Action Type':<22} {'Cntry1':<6} {'Actor1':<25}")
    print('-'*100)

    for row in legal_events:
        date, action_type, c1, a1, c2, a2, url = row
        a1_short = (a1 or 'N/A')[:24]
        print(f"{date:<12} {action_type:<22} {c1 or 'N/A':<6} {a1_short:<25}")

    print()
    print('SECURITY INTELLIGENCE VALUE:')
    print('  -> Track espionage accusations and arrests (researcher/scientist cases)')
    print('  -> Monitor IP theft lawsuits and court verdicts')
    print('  -> Identify asset seizures and confiscations')
    print('  -> Cross-reference with USPTO patents and academic collaborations')
else:
    print("No legal/security events found")

print()
print()

# ============================================================================
# QUERY 9: DEPORTATIONS & EXPULSIONS (Code 174) - MOVED FROM SANCTIONS!
# ============================================================================

print('QUERY 9: DEPORTATIONS & EXPULSIONS (Code 174) - MOVED FROM SANCTIONS!')
print('Event Code 174: Expel or deport individuals')
print('='*100)
print('MAJOR CORRECTION: Code 174 is deportations/expulsions (NOT economic sanctions!)')
print('Tracks expelled Chinese diplomats, deported researchers, extradited individuals')
print(f'Coverage: All {len(EUROPEAN_COUNTRIES)} European countries')
print('-'*100)

query = f'''
SELECT
    event_date,
    actor1_country_code,
    actor1_name,
    actor2_country_code,
    actor2_name,
    source_url
FROM gdelt_events
WHERE event_code = '174'
  AND (actor1_country_code = 'CHN' OR actor2_country_code = 'CHN')
  AND (
    actor1_country_code IN ({COUNTRY_LIST_SQL})
    OR actor2_country_code IN ({COUNTRY_LIST_SQL})
  )
ORDER BY event_date DESC
LIMIT 50
'''

cursor.execute(query)
deportation_events = cursor.fetchall()

if deportation_events:
    print(f"Found {len(deportation_events)} deportation/expulsion events (showing latest 50):")
    print()
    print(f"{'Date':<12} {'Cntry1':<6} {'Actor1':<30} {'Cntry2':<6} {'Actor2':<30}")
    print('-'*100)

    for row in deportation_events:
        date, c1, a1, c2, a2, url = row
        a1_short = (a1 or 'N/A')[:29]
        a2_short = (a2 or 'N/A')[:29]
        print(f"{date:<12} {c1 or 'N/A':<6} {a1_short:<30} {c2 or 'N/A':<6} {a2_short:<30}")

    print()
    print('SECURITY INTELLIGENCE VALUE:')
    print('  -> Track expelled Chinese diplomats (espionage cases)')
    print('  -> Monitor deported researchers/academics (technology transfer concerns)')
    print('  -> Identify extradited individuals (criminal cases)')
else:
    print("No deportation/expulsion events found")

print()
print()

# ============================================================================
# QUERY 10: PROTESTS & DEMONSTRATIONS (Code 141) - NEW!
# ============================================================================

print('QUERY 10: PROTESTS & DEMONSTRATIONS (Code 141) - NEW!')
print('Event Code 141: Demonstrate or rally')
print('='*100)
print('NEW: Code 141 has 208 events - tracks anti-China protests, demonstrations')
print('Public opposition to Chinese influence, technology, investments')
print(f'Coverage: All {len(EUROPEAN_COUNTRIES)} European countries')
print('-'*100)

query = f'''
SELECT
    event_date,
    actor1_country_code,
    actor1_name,
    actor2_country_code,
    actor2_name,
    source_url
FROM gdelt_events
WHERE event_code = '141'
  AND (actor1_country_code = 'CHN' OR actor2_country_code = 'CHN')
  AND (
    actor1_country_code IN ({COUNTRY_LIST_SQL})
    OR actor2_country_code IN ({COUNTRY_LIST_SQL})
  )
ORDER BY event_date DESC
LIMIT 50
'''

cursor.execute(query)
protest_events = cursor.fetchall()

if protest_events:
    print(f"Found {len(protest_events)} protest/demonstration events (showing latest 50):")
    print()
    print(f"{'Date':<12} {'Cntry1':<6} {'Actor1':<30} {'Cntry2':<6} {'Actor2':<30}")
    print('-'*100)

    for row in protest_events:
        date, c1, a1, c2, a2, url = row
        a1_short = (a1 or 'N/A')[:29]
        a2_short = (a2 or 'N/A')[:29]
        print(f"{date:<12} {c1 or 'N/A':<6} {a1_short:<30} {c2 or 'N/A':<6} {a2_short:<30}")

    print()
    print('PUBLIC OPINION INTELLIGENCE VALUE:')
    print('  -> Track public opposition to Chinese influence in Europe')
    print('  -> Monitor anti-5G/Huawei protests')
    print('  -> Identify locations of strongest public resistance')
else:
    print("No protest/demonstration events found")

print()
print()

# ============================================================================
# QUERY 11: RELEASES & COMPLAINTS (Codes 0841, 114) - NEW!
# ============================================================================

print('QUERY 11: RELEASES & OFFICIAL COMPLAINTS - NEW!')
print('Event Codes: 0841 (Return/release persons), 114 (Complain officially)')
print('='*100)
print('NEW: Code 0841 has 171 events, Code 114 has 176 events')
print('Tracks released detainees/executives and official government complaints')
print(f'Coverage: All {len(EUROPEAN_COUNTRIES)} European countries')
print('-'*100)

query = f'''
SELECT
    event_date,
    CASE
        WHEN event_code = '0841' THEN 'Return/release person(s)'
        WHEN event_code = '114' THEN 'Complain officially'
    END as action_type,
    actor1_country_code,
    actor1_name,
    actor2_country_code,
    actor2_name,
    source_url
FROM gdelt_events
WHERE event_code IN ('0841', '114')
  AND (actor1_country_code = 'CHN' OR actor2_country_code = 'CHN')
  AND (
    actor1_country_code IN ({COUNTRY_LIST_SQL})
    OR actor2_country_code IN ({COUNTRY_LIST_SQL})
  )
ORDER BY event_date DESC
LIMIT 50
'''

cursor.execute(query)
release_complaint_events = cursor.fetchall()

if release_complaint_events:
    print(f"Found {len(release_complaint_events)} release/complaint events (showing latest 50):")
    print()
    print(f"{'Date':<12} {'Action Type':<25} {'Cntry1':<6} {'Actor1':<25}")
    print('-'*100)

    for row in release_complaint_events:
        date, action_type, c1, a1, c2, a2, url = row
        a1_short = (a1 or 'N/A')[:24]
        print(f"{date:<12} {action_type:<25} {c1 or 'N/A':<6} {a1_short:<25}")

    print()
    print('INTELLIGENCE VALUE:')
    print('  -> Code 0841: Track releases of detained executives, researchers, prisoners')
    print('  -> Code 114: Monitor official government-to-government complaints')
    print('  -> Cross-reference releases with prior arrest events (code 173)')
else:
    print("No release/complaint events found")

print()
print()

# ============================================================================
# QUERY 12: ECONOMIC COOPERATION (Code 061) - VERIFIED
# ============================================================================

print('QUERY 12: ECONOMIC COOPERATION (China-Europe) - VERIFIED')
print('Event Code 061: Cooperate economically')
print('='*100)
print('Commercial partnerships, trade deals, technology trade agreements')
print('NOTE: Code 051 (Praise/endorse) REMOVED - was incorrectly labeled as cooperation')
print(f'Coverage: All {len(EUROPEAN_COUNTRIES)} European countries')
print('-'*100)

query = f'''
SELECT
    event_date,
    actor1_name,
    actor1_country_code,
    actor2_name,
    actor2_country_code,
    source_url
FROM gdelt_events
WHERE event_code = '061'
  AND (actor1_country_code = 'CHN' OR actor2_country_code = 'CHN')
  AND (
    actor1_country_code IN ({COUNTRY_LIST_SQL})
    OR actor2_country_code IN ({COUNTRY_LIST_SQL})
  )
ORDER BY event_date DESC
LIMIT 50
'''

cursor.execute(query)
econ_coop = cursor.fetchall()

if econ_coop:
    print(f"Found {len(econ_coop)} economic cooperation events (showing latest 50):")
    print()
    print(f"{'Date':<12} {'Cntry1':<6} {'Actor1':<35} {'Cntry2':<6} {'Actor2':<35}")
    print('-'*100)

    for row in econ_coop:
        date, a1_name, a1_country, a2_name, a2_country, url = row
        a1_short = (a1_name or 'N/A')[:34]
        a2_short = (a2_name or 'N/A')[:34]
        print(f"{date:<12} {a1_country or 'N/A':<6} {a1_short:<35} {a2_country or 'N/A':<6} {a2_short:<35}")

    print()
    print('INTELLIGENCE VALUE:')
    print('  -> Includes commercial tech partnerships and trade deals')
    print('  -> Cross-reference with OpenAlex for academic research')
    print('  -> Check BCI, quantum, AI, semiconductor technology areas')
else:
    print("No economic cooperation events found")

print()
print()

# ============================================================================
# SUMMARY STATISTICS
# ============================================================================

print('='*100)
print('SUMMARY STATISTICS - CORRECTED EVENT COVERAGE')
print('='*100)

# Total events by category
categories = {
    'Cooperation (verified codes)': ['030','040','042','043','057','061','064','120','130','140'],
    'Diplomatic Engagement (corrected)': ['044','045','046'],
    'Intent/Planning (NEW - Phase 2 Tier 1)': ['036','0311'],
    'Aid/Investment (Phase 1)': ['070','071','072'],
    'Sanctions - IMPOSE (CORRECTED!)': ['163','172'],
    'Sanctions - EASE (CORRECTED!)': ['081','085'],
    'Policy Demands (CORRECTED!)': ['1042'],
    'Legal/Security (Phase 1)': ['111','112','1125','115','116','173','1711'],
    'Deportations (moved from sanctions!)': ['174'],
    'Protests (NEW - Phase 2 Tier 1)': ['141'],
    'Releases/Complaints (NEW - Phase 2 Tier 1)': ['0841','114'],
}

for category_name, codes in categories.items():
    codes_sql = "'" + "','".join(codes) + "'"
    query = f'''
        SELECT COUNT(*)
        FROM gdelt_events
        WHERE event_code IN ({codes_sql})
        AND (actor1_country_code = 'CHN' OR actor2_country_code = 'CHN')
        AND (
            actor1_country_code IN ({COUNTRY_LIST_SQL})
            OR actor2_country_code IN ({COUNTRY_LIST_SQL})
        )
    '''
    cursor.execute(query)
    count = cursor.fetchone()[0]
    print(f"{category_name:<50} {count:>6} events")

print()
print('='*100)
print('VERIFICATION STATUS')
print('='*100)
print(f'Total codes in use: {len(EVENT_CODES)}')
print(f'All codes verified against official CAMEO documentation: 2025-11-02')
print()
print('MAJOR CORRECTIONS APPLIED:')
print('  - Code 051 REMOVED (was "Economic cooperation" - actually "Praise/endorse")')
print('  - Code 046 CORRECTED (was "Material cooperation" - actually "Engage in negotiation")')
print('  - Code 163 ADDED (REAL "Impose embargo/sanctions" code - 188 events)')
print('  - Code 085 ADDED (REAL "Ease economic sanctions" code)')
print('  - Code 174 MOVED (was in sanctions - actually deportations)')
print('  - Code 1042 ADDED (REAL "Demand policy change" code, replaced 106)')
print('  - Code 036 ADDED (Intent to meet/negotiate - 1,668 events!)')
print('  - Code 141 ADDED (Demonstrate/rally - 208 events)')
print('  - Code 114 ADDED (Complain officially - 176 events)')
print('  - Code 0841 ADDED (Return/release persons - 171 events)')
print()
print('Codes removed due to mislabeling:')
print('  - 051 (Praise/endorse - not economic cooperation)')
print('  - 0234 (Appeal for military protection - not technical aid)')
print('  - 082 (Ease political dissent - not ease economic sanctions)')
print('  - 106 (Demand withdrawal - not demand policy change)')
print()
print('='*100)

db.close()

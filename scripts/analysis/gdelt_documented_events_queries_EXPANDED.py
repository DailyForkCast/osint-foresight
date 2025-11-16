#!/usr/bin/env python3
"""
GDELT Documented Events Queries - COMPREHENSIVE EUROPEAN COVERAGE
EXPANDED VERSION - All verified codes + Phase 2 Tier 2 & 3

Focus: Concrete events (agreements, partnerships, visits) + diplomatic support tracking

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

CAMEO EVENT CODES USED (89 codes total - ALL VERIFIED):
VERSION 4.0 - COMPREHENSIVE RELATIONSHIP COVERAGE

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

DIPLOMATIC SUPPORT/RHETORIC (3 codes - RE-ADDED 051):
- 051: Praise or endorse (RE-ADDED - tracks diplomatic support for China)
- 052: Defend verbally (NEW - Tier 3)
- 019: Express accord (NEW - Tier 3)

DIPLOMATIC ENGAGEMENT (3 codes):
- 044: Meet at a third location (multilateral summits)
- 045: Mediate (third-party mediation)
- 046: Engage in negotiation (bilateral/multilateral talks)

APPEALS (4 codes - NEW Tier 3):
- 022: Appeal for diplomatic cooperation, such as policy support
- 026: Appeal to others to meet or negotiate
- 0214: Appeal for intelligence
- 1053: Demand release of persons or property

PHASE 1 - AID/INVESTMENT (4 codes - EXPANDED):
- 070: Provide aid, not specified below
- 071: Provide economic aid (BRI)
- 072: Provide military aid
- 073: Provide humanitarian aid (NEW - Tier 2)

PHASE 1 - SANCTIONS (4 codes - CORRECTED):
- 081: Ease administrative sanctions
- 085: Ease economic sanctions, boycott, embargo
- 163: Impose embargo, boycott, or sanctions (REAL impose sanctions code)
- 172: Impose administrative sanctions

PHASE 1 - LEGAL/SECURITY (7 codes):
- 111: Criticize or denounce
- 112: Accuse, not specified below
- 1125: Accuse of espionage, treason
- 115: Bring lawsuit against
- 116: Find guilty or liable (legally)
- 173: Arrest, detain, or charge with legal action
- 1711: Confiscate property

PHASE 1 - DEPORTATIONS/EXPULSIONS (1 code):
- 174: Expel or deport individuals

INVESTIGATIONS (1 code - NEW Tier 3):
- 092: Investigate human rights abuses

PHASE 2 TIER 1 - INTENT/PLANNING (3 codes - EXPANDED):
- 036: Express intent to meet or negotiate (1,668 events)
- 0311: Express intent to cooperate economically
- 0331: Express intent to provide economic aid (NEW - Tier 3)
- 032: Express intent to provide diplomatic cooperation (NEW - Tier 3)

PHASE 2 TIER 1 - COMPLAINTS/VIOLATIONS (2 codes):
- 114: Complain officially
- 1042: Demand policy change

PHASE 2 TIER 1 - PROTESTS/DISSENT (2 codes - EXPANDED):
- 141: Demonstrate or rally
- 143: Conduct strike or boycott (NEW - Tier 3)

PHASE 2 TIER 1 - RELEASES (2 codes - EXPANDED):
- 0841: Return, release person(s)
- 075: Grant asylum (NEW - Tier 3 - Xinjiang refugees)

PHASE 2 TIER 2 - MILITARY/SECURITY COOPERATION (1 code - NEW):
- 062: Cooperate militarily

PHASE 2 TIER 2 - DIPLOMATIC RECOGNITION (1 code - NEW):
- 054: Grant diplomatic recognition

PHASE 2 TIER 2 - RELATIONSHIP DETERIORATION (4 codes - NEW):
- 161: Reduce or break diplomatic relations
- 164: Halt negotiations
- 125: Reject proposal to meet, discuss, or negotiate
- 128: Defy norms, law

PHASE 2 TIER 2 - MULTILATERAL DIPLOMACY (1 code - NEW):
- 129: Veto

PHASE 2 TIER 3 - VIOLENT EVENTS (2 codes - NEW):
- 181: Abduct, hijack, or take hostage
- 186: Assassinate

PHASE 3 - COMPREHENSIVE RELATIONSHIP COVERAGE (33 NEW CODES):
Rationale: "Get a fuller understanding of the entirety of their relationship"
Captures military dimensions, threats, coercion, and escalation pathways

APPEALS - MATERIAL/MILITARY COOPERATION (4 codes):
- 021: Appeal for material cooperation
- 0213: Appeal for judicial cooperation
- 0232: Appeal for military aid
- 0234: Appeal for military protection or peacekeeping

INTENT - MATERIAL/MILITARY COOPERATION (4 codes):
- 031: Express intent to cooperate materially
- 0313: Express intent for judicial cooperation
- 0332: Express intent to provide military aid
- 0334: Express intent to provide military protection or peacekeeping

COOPERATION - GENERAL CATEGORIES (2 codes):
- 050: Engage in diplomatic cooperation (general)
- 060: Engage in material cooperation (general)

AID - MILITARY PROTECTION (1 code):
- 074: Provide military protection or peacekeeping

INVESTIGATIONS - MILITARY ACTIONS (1 code):
- 093: Investigate military action

DEMANDS - POLICY SUPPORT (1 code):
- 102: Demand policy support

DISAPPROVE - ACCUSATIONS (1 code):
- 1123: Accuse of aggression

REJECT - MATERIAL/MILITARY/SANCTIONS (3 codes):
- 121: Reject material cooperation
- 1241: Refuse to ease administrative sanctions
- 1242: Refuse to ease popular dissent

THREATEN - NON-FORCE, ADMINISTRATIVE, MILITARY (8 codes):
- 131: Threaten non-force, not specified below
- 132: Threaten with administrative sanctions
- 138: Threaten to use military force, not specified below
- 1381: Threaten blockade
- 1382: Threaten occupation
- 1383: Threaten unconventional violence
- 1384: Threaten conventional attack
- 1385: Threaten attack with WMD

PROTEST - OBSTRUCTION (1 code):
- 144: Obstruct passage, block

FORCE POSTURE (1 code):
- 150: Demonstrate military or police power

REDUCE RELATIONS - EXPULSION (1 code):
- 166: Expel or withdraw, not specified below

COERCION - GENERAL (1 code):
- 170: Coerce, not specified below

FIGHT - BLOCKADE (1 code):
- 191: Impose blockade, restrict movement

UNCONVENTIONAL MASS VIOLENCE - WMD (3 codes):
- 204: Use unconventional mass violence, not specified below
- 2041: Use chemical, biological, or radiological weapons
- 2042: Detonate nuclear weapons
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
EUROPEAN_COUNTRIES = [
    # EU27 Member States
    'AUT', 'BEL', 'BGR', 'HRV', 'CYP', 'CZE', 'DNK', 'EST', 'FIN', 'FRA',
    'DEU', 'GRC', 'HUN', 'IRL', 'ITA', 'LVA', 'LTU', 'LUX', 'MLT', 'NLD',
    'POL', 'PRT', 'ROU', 'SVK', 'SVN', 'ESP', 'SWE',
    # EEA/EFTA (non-EU)
    'NOR', 'ISL', 'CHE', 'LIE',
    # United Kingdom (post-Brexit)
    'GBR',
    # Balkans
    'ALB', 'BIH', 'SRB', 'MNE', 'MKD',
    # Eastern Europe
    'UKR', 'BLR', 'MDA',
    # Caucasus
    'GEO', 'ARM', 'AZE',
    # Other European
    'TUR', 'AND', 'MCO', 'SMR', 'VAT', 'RUS',
]

# Event codes we're tracking - ALL VERIFIED against official CAMEO
EVENT_CODES = [
    # Original codes - VERIFIED
    '030', '040', '042', '043', '057', '061', '064', '120', '130', '140',

    # Diplomatic support/rhetoric - RE-ADDED 051 + NEW
    '051', '052', '019',

    # Diplomatic engagement
    '044', '045', '046',

    # Appeals - NEW
    '022', '026', '0214', '1053',

    # Phase 1: Aid/Investment - EXPANDED
    '070', '071', '072', '073',

    # Phase 1: Sanctions - CORRECTED
    '081', '085', '163', '172',

    # Phase 1: Legal/Security
    '111', '112', '1125', '115', '116', '173', '1711',

    # Phase 1: Deportations
    '174',

    # Investigations - NEW
    '092',

    # Phase 2 Tier 1: Intent/Planning - EXPANDED
    '036', '0311', '0331', '032',

    # Phase 2 Tier 1: Complaints/Violations
    '114', '1042',

    # Phase 2 Tier 1: Protests - EXPANDED
    '141', '143',

    # Phase 2 Tier 1: Releases - EXPANDED
    '0841', '075',

    # Phase 2 Tier 2: Military/Security - NEW
    '062',

    # Phase 2 Tier 2: Diplomatic Recognition - NEW
    '054',

    # Phase 2 Tier 2: Relationship Deterioration - NEW
    '161', '164', '125', '128',

    # Phase 2 Tier 2: Multilateral - NEW
    '129',

    # Phase 2 Tier 3: Violent Events - NEW
    '181', '186',

    # PHASE 3: COMPREHENSIVE RELATIONSHIP COVERAGE (32 NEW CODES)

    # Appeals - Material/Military Cooperation (Category 02)
    '021', '0213', '0232', '0234',

    # Intent - Material/Military Cooperation (Category 03)
    '031', '0313', '0332', '0334',

    # Cooperation - General Categories (Category 05-06)
    '050', '060',

    # Aid - Military Protection (Category 07)
    '074',

    # Investigate - Military Actions (Category 09)
    '093',

    # Demand - Policy Support (Category 10)
    '102',

    # Disapprove - Accuse of Aggression (Category 11)
    '1123',

    # Reject - Material/Military Cooperation, Sanctions (Category 12)
    '121', '1241', '1242',

    # Threaten - Non-force, Administrative, Military Force (Category 13)
    '131', '132', '138', '1381', '1382', '1383', '1384', '1385',

    # Protest - Obstruct Passage (Category 14)
    '144',

    # Force Posture - Demonstrate Military/Police Power (Category 15)
    '150',

    # Reduce Relations - Expel/Withdraw (Category 16)
    '166',

    # Coerce - General (Category 17)
    '170',

    # Fight - Impose Blockade (Category 19)
    '191',

    # Unconventional Mass Violence - WMD Use (Category 20)
    '204', '2041', '2042',
]

# SQL-safe lists
COUNTRY_LIST_SQL = "'" + "','".join(EUROPEAN_COUNTRIES) + "'"
EVENT_CODE_LIST_SQL = "'" + "','".join(EVENT_CODES) + "'"

def get_event_type_description(code):
    """Return human-readable description for event code - ALL VERIFIED"""
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
        '022': 'Appeal for diplomatic cooperation, such as policy support',
        '026': 'Appeal to others to meet or negotiate',
        '0214': 'Appeal for intelligence',
        '1053': 'Demand release of persons or property',

        # Aid/Investment
        '070': 'Provide aid, not specified below',
        '071': 'Provide economic aid',
        '072': 'Provide military aid',
        '073': 'Provide humanitarian aid',

        # Sanctions
        '081': 'Ease administrative sanctions',
        '085': 'Ease economic sanctions, boycott, embargo',
        '163': 'Impose embargo, boycott, or sanctions',
        '172': 'Impose administrative sanctions',

        # Legal/Security
        '111': 'Criticize or denounce',
        '112': 'Accuse, not specified below',
        '1125': 'Accuse of espionage, treason',
        '115': 'Bring lawsuit against',
        '116': 'Find guilty or liable (legally)',
        '173': 'Arrest, detain, or charge with legal action',
        '1711': 'Confiscate property',

        # Deportations
        '174': 'Expel or deport individuals',

        # Investigations
        '092': 'Investigate human rights abuses',

        # Intent/Planning
        '036': 'Express intent to meet or negotiate',
        '0311': 'Express intent to cooperate economically',
        '0331': 'Express intent to provide economic aid',
        '032': 'Express intent to provide diplomatic cooperation such as policy support',

        # Complaints/Violations
        '114': 'Complain officially',
        '1042': 'Demand policy change',

        # Protests
        '141': 'Demonstrate or rally',
        '143': 'Conduct strike or boycott',

        # Releases
        '0841': 'Return, release person(s)',
        '075': 'Grant asylum',

        # Military/Security Cooperation
        '062': 'Cooperate militarily',

        # Diplomatic Recognition
        '054': 'Grant diplomatic recognition',

        # Relationship Deterioration
        '161': 'Reduce or break diplomatic relations',
        '164': 'Halt negotiations',
        '125': 'Reject proposal to meet, discuss, or negotiate',
        '128': 'Defy norms, law',

        # Multilateral
        '129': 'Veto',

        # Violent Events
        '181': 'Abduct, hijack, or take hostage',
        '186': 'Assassinate',

        # PHASE 3: COMPREHENSIVE RELATIONSHIP COVERAGE

        # Appeals - Material/Military Cooperation
        '021': 'Appeal for material cooperation',
        '0213': 'Appeal for judicial cooperation',
        '0232': 'Appeal for military aid',
        '0234': 'Appeal for military protection or peacekeeping',

        # Intent - Material/Military Cooperation
        '031': 'Express intent to cooperate materially',
        '0313': 'Express intent for judicial cooperation',
        '0332': 'Express intent to provide military aid',
        '0334': 'Express intent to provide military protection or peacekeeping',

        # Cooperation - General Categories
        '050': 'Engage in diplomatic cooperation (general)',
        '060': 'Engage in material cooperation (general)',

        # Aid - Military Protection
        '074': 'Provide military protection or peacekeeping',

        # Investigate - Military Actions
        '093': 'Investigate military action',

        # Demand - Policy Support
        '102': 'Demand policy support',

        # Disapprove - Accuse of Aggression
        '1123': 'Accuse of aggression',

        # Reject - Material/Military Cooperation, Sanctions
        '121': 'Reject material cooperation',
        '1241': 'Refuse to ease administrative sanctions',
        '1242': 'Refuse to ease popular dissent',

        # Threaten - Non-force, Administrative, Military Force
        '131': 'Threaten non-force, not specified below',
        '132': 'Threaten with administrative sanctions',
        '138': 'Threaten to use military force, not specified below',
        '1381': 'Threaten blockade',
        '1382': 'Threaten occupation',
        '1383': 'Threaten unconventional violence',
        '1384': 'Threaten conventional attack',
        '1385': 'Threaten attack with WMD',

        # Protest - Obstruct Passage
        '144': 'Obstruct passage, block',

        # Force Posture - Demonstrate Military/Police Power
        '150': 'Demonstrate military or police power',

        # Reduce Relations - Expel/Withdraw
        '166': 'Expel or withdraw, not specified below',

        # Coerce - General
        '170': 'Coerce, not specified below',

        # Fight - Impose Blockade
        '191': 'Impose blockade, restrict movement',

        # Unconventional Mass Violence - WMD Use
        '204': 'Use unconventional mass violence, not specified below',
        '2041': 'Use chemical, biological, or radiological weapons',
        '2042': 'Detonate nuclear weapons',
    }
    return descriptions.get(code, 'Unknown code')

db = sqlite3.connect(DB_PATH)
cursor = db.cursor()

print('='*100)
print('GDELT DOCUMENTED EVENTS ANALYSIS - COMPREHENSIVE EUROPEAN COVERAGE')
print('*** VERSION 4.0 - COMPREHENSIVE RELATIONSHIP COVERAGE (89 CODES) ***')
print(f'Geographic Scope: {len(EUROPEAN_COUNTRIES)} European countries')
print(f'Event Types: {len(EVENT_CODES)} CAMEO codes (ALL VERIFIED against official documentation)')
print('NEW: Added 33 Phase 3 codes for military dimensions, threats, coercion, escalation')
print('='*100)
print()

# Get total event counts for all codes
print('QUICK STATISTICS - Event Counts by Code Category')
print('='*100)

code_categories = {
    'Diplomatic Support (051, 052, 019) - RE-ADDED': ['051', '052', '019'],
    'Formal Agreements (057)': ['057'],
    'Intent to Cooperate (036, 0311, 0331, 032) - EXPANDED': ['036', '0311', '0331', '032'],
    'Negotiations (046, 045, 044)': ['046', '045', '044'],
    'Aid & Investment (070-073) - EXPANDED': ['070', '071', '072', '073'],
    'Military Cooperation (062) - NEW': ['062'],
    'Impose Sanctions (163, 172)': ['163', '172'],
    'Ease Sanctions (081, 085)': ['081', '085'],
    'Legal/Security (111, 112, 1125, 115, 116, 173, 1711)': ['111', '112', '1125', '115', '116', '173', '1711'],
    'Deportations (174)': ['174'],
    'Investigations (092) - NEW': ['092'],
    'Diplomatic Recognition (054) - NEW': ['054'],
    'Relationship Deterioration (161, 164, 125, 128) - NEW': ['161', '164', '125', '128'],
    'Protests & Strikes (141, 143) - EXPANDED': ['141', '143'],
    'Releases & Asylum (0841, 075) - EXPANDED': ['0841', '075'],
    'Complaints (114, 1042)': ['114', '1042'],
    'Appeals (022, 026, 0214, 1053) - NEW': ['022', '026', '0214', '1053'],
    'Multilateral (129) - NEW': ['129'],
    'Violent Events (181, 186) - NEW': ['181', '186'],
    'Reject/Veto (120, 129)': ['120', '129'],
    'Threaten (130)': ['130'],
}

for category_name, codes in code_categories.items():
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
    print(f"{category_name:<65} {count:>6} events")

print()
print('='*100)
print('NOTE: These are total counts across ALL available data in database')
print('Detailed queries below show latest 50 events per category')
print('='*100)
print()
print()

# ============================================================================
# QUERY 1: DIPLOMATIC SUPPORT & RHETORIC (Codes 051, 052, 019) - RE-ADDED!
# ============================================================================

print('QUERY 1: DIPLOMATIC SUPPORT & RHETORIC (China from/to Europe) - RE-ADDED!')
print('Event Codes: 051 (Praise/endorse), 052 (Defend verbally), 019 (Express accord)')
print('='*100)
print('RE-ADDED Code 051: Track extent of diplomatic support China receives (or gives)')
print('Intelligence Value: Diplomatic warming/cooling, coalition building, isolation indicators')
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
WHERE event_code IN ('051', '052', '019')
  AND (actor1_country_code = 'CHN' OR actor2_country_code = 'CHN')
  AND (
    actor1_country_code IN ({COUNTRY_LIST_SQL})
    OR actor2_country_code IN ({COUNTRY_LIST_SQL})
  )
ORDER BY event_date DESC
LIMIT 50
'''

cursor.execute(query)
rhetoric_events = cursor.fetchall()

if rhetoric_events:
    print(f"Found {len(rhetoric_events)} diplomatic support/rhetoric events (showing latest 50):")
    print()
    print(f"{'Date':<12} {'Type':<12} {'Cntry1':<6} {'Actor1':<25} {'Cntry2':<6} {'Actor2':<25}")
    print('-'*100)

    for row in rhetoric_events:
        date, code, a1_name, a1_country, a2_name, a2_country, url = row
        event_type = {
            '051': '051-Praise',
            '052': '052-Defend',
            '019': '019-Accord'
        }[code]
        a1_short = (a1_name or 'N/A')[:24]
        a2_short = (a2_name or 'N/A')[:24]
        print(f"{date:<12} {event_type:<12} {a1_country or 'N/A':<6} {a1_short:<25} {a2_country or 'N/A':<6} {a2_short:<25}")

    print()
    print('INTELLIGENCE VALUE:')
    print('  -> Code 051: Who praises/endorses China? Track diplomatic support levels')
    print('  -> Code 052: Who defends China verbally? Identify China allies in disputes')
    print('  -> Code 019: Express accord - agreement statements before formal signing')
    print('  -> Monitor trends: Is China gaining or losing diplomatic support in Europe?')
    print()
    print('CROSS-REFERENCE:')
    print('  -> OpenAlex/OpenAire/arXiv/Conferences: Do praise events correlate with research collaborations?')
    print('  -> TED/USASPENDING: Do supportive countries award more contracts to Chinese firms?')
    print('  -> AidData: Does diplomatic support lead to development finance?')
    print('  -> GitHub: Track open source collaboration with supportive countries')
else:
    print("No diplomatic support/rhetoric events found")

print()
print()

# ============================================================================
# QUERY 2: FORMAL AGREEMENTS (Code 057)
# ============================================================================

print('QUERY 2: FORMAL AGREEMENTS (China-Europe)')
print('Event Code: 057 (Sign formal agreement)')
print('='*100)
print('HIGH VALUE: Treaties, contracts, MOUs, joint declarations')
print('Intelligence Value: BRI agreements, tech partnerships, 5G contracts, research collaboration')
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
agreement_events = cursor.fetchall()

if agreement_events:
    print(f"Found {len(agreement_events)} formal agreement events (showing latest 50):")
    print()
    print(f"{'Date':<12} {'Cntry1':<6} {'Actor1':<30} {'Cntry2':<6} {'Actor2':<30}")
    print('-'*100)

    for row in agreement_events:
        date, a1_name, a1_country, a2_name, a2_country, url = row
        a1_short = (a1_name or 'N/A')[:29]
        a2_short = (a2_name or 'N/A')[:29]
        print(f"{date:<12} {a1_country or 'N/A':<6} {a1_short:<30} {a2_country or 'N/A':<6} {a2_short:<30}")

    print()
    print('CROSS-REFERENCE OPPORTUNITIES:')
    print('  -> OpenAlex: Match agreements to research collaborations')
    print('  -> TED: Match to EU public procurement contracts')
    print('  -> USPTO: Match to joint patent applications')
else:
    print("No formal agreement events found")

print()
print()


# ============================================================================
# QUERY 3: INTENT TO COOPERATE/NEGOTIATE (Codes 036, 0311, 0331, 032, 031, 0313, 0332, 0334) - EXPANDED!
# ============================================================================

print('QUERY 3: INTENT TO COOPERATE/NEGOTIATE - EXPANDED!')
print('Event Codes: 036 (Intent meet), 0311 (Intent econ coop), 0331 (Intent econ aid), 032 (Intent diplo coop),')
print('             031 (Intent material coop), 0313 (Intent judicial coop), 0332 (Intent mil aid), 0334 (Intent mil protection)')
print('='*100)
print('EXPANDED: Now includes material/military/judicial cooperation intents (8 codes total)')
print('Intelligence Value: Pre-agreement positioning, relationship warming, military cooperation signals')
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
WHERE event_code IN ('036', '0311', '0331', '032', '031', '0313', '0332', '0334')
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
    print(f"Found {len(intent_events)} intent to cooperate/negotiate events (showing latest 50):")
    print()
    print(f"{'Date':<12} {'Type':<18} {'Cntry1':<6} {'Actor1':<21} {'Cntry2':<6} {'Actor2':<21}")
    print('-'*100)

    for row in intent_events:
        date, code, a1_name, a1_country, a2_name, a2_country, url = row
        event_type = {
            '036': '036-IntMeet',
            '0311': '0311-IntEcon',
            '0331': '0331-IntAid',
            '032': '032-IntDiplo',
            '031': '031-IntMaterial',
            '0313': '0313-IntJudicial',
            '0332': '0332-IntMilAid',
            '0334': '0334-IntMilProt'
        }[code]
        a1_short = (a1_name or 'N/A')[:20]
        a2_short = (a2_name or 'N/A')[:20]
        print(f"{date:<12} {event_type:<18} {a1_country or 'N/A':<6} {a1_short:<21} {a2_country or 'N/A':<6} {a2_short:<21}")

    print()
    print('INTELLIGENCE VALUE:')
    print('  -> Track relationship warming before formal agreements')
    print('  -> Identify upcoming BRI deals (0331) and military cooperation (0332, 0334)')
    print('  -> Monitor diplomatic/judicial/material cooperation signals (032, 0313, 031)')
else:
    print("No intent to cooperate/negotiate events found")

print()
print()


# ============================================================================
# QUERY 4: DIPLOMATIC ENGAGEMENT (Codes 044, 045, 046)
# ============================================================================

print('QUERY 4: DIPLOMATIC ENGAGEMENT (Mediation, Negotiations, Multilateral Meetings)')
print('Event Codes: 044 (Meet at third location), 045 (Mediate), 046 (Engage in negotiation)')
print('='*100)
print('Code 046 CORRECTED: Was labeled "material cooperation", actually "engage in negotiation"')
print('Intelligence Value: Track multilateral summit participation, negotiation patterns')
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
engagement_events = cursor.fetchall()

if engagement_events:
    print(f"Found {len(engagement_events)} diplomatic engagement events (showing latest 50):")
    print()
    print(f"{'Date':<12} {'Type':<13} {'Cntry1':<6} {'Actor1':<23} {'Cntry2':<6} {'Actor2':<23}")
    print('-'*100)

    for row in engagement_events:
        date, code, a1_name, a1_country, a2_name, a2_country, url = row
        event_type = {
            '044': '044-Meet3rd',
            '045': '045-Mediate',
            '046': '046-Negotiate'
        }[code]
        a1_short = (a1_name or 'N/A')[:22]
        a2_short = (a2_name or 'N/A')[:22]
        print(f"{date:<12} {event_type:<13} {a1_country or 'N/A':<6} {a1_short:<23} {a2_country or 'N/A':<6} {a2_short:<23}")

    print()
    print('INTELLIGENCE VALUE:')
    print('  -> Code 044: Multilateral summit participation (Belt & Road Forums, etc.)')
    print('  -> Code 045: Mediation efforts (who mediates China-Europe disputes?)')
    print('  -> Code 046: Bilateral/multilateral negotiations')
else:
    print("No diplomatic engagement events found")

print()
print()


# ============================================================================
# QUERY 5: APPEALS (Codes 022, 026, 0214, 1053, 021, 0213, 0232, 0234) - EXPANDED!
# ============================================================================

print('QUERY 5: APPEALS & DEMANDS - EXPANDED!')
print('Event Codes: 022 (Appeal diplomatic coop), 026 (Appeal to meet), 0214 (Appeal intelligence),')
print('             1053 (Demand release), 021 (Appeal material coop), 0213 (Appeal judicial coop),')
print('             0232 (Appeal military aid), 0234 (Appeal military protection)')
print('='*100)
print('EXPANDED: Comprehensive appeal/demand tracking including military cooperation')
print('Intelligence Value: Diplomatic pressure, hostage situations, cooperation requests, military appeals')
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
WHERE event_code IN ('022', '026', '0214', '1053', '021', '0213', '0232', '0234')
  AND (actor1_country_code = 'CHN' OR actor2_country_code = 'CHN')
  AND (
    actor1_country_code IN ({COUNTRY_LIST_SQL})
    OR actor2_country_code IN ({COUNTRY_LIST_SQL})
  )
ORDER BY event_date DESC
LIMIT 50
'''

cursor.execute(query)
appeal_events = cursor.fetchall()

if appeal_events:
    print(f"Found {len(appeal_events)} appeal/demand events (showing latest 50):")
    print()
    print(f"{'Date':<12} {'Type':<15} {'Cntry1':<6} {'Actor1':<22} {'Cntry2':<6} {'Actor2':<22}")
    print('-'*100)

    for row in appeal_events:
        date, code, a1_name, a1_country, a2_name, a2_country, url = row
        event_type = {
            '022': '022-AppealDiplo',
            '026': '026-AppealMeet',
            '0214': '0214-AppealIntel',
            '1053': '1053-DemandRel',
            '021': '021-AppealMaterial',
            '0213': '0213-AppealJudicial',
            '0232': '0232-AppealMilAid',
            '0234': '0234-AppealMilProt'
        }[code]
        a1_short = (a1_name or 'N/A')[:21]
        a2_short = (a2_name or 'N/A')[:21]
        print(f"{date:<12} {event_type:<15} {a1_country or 'N/A':<6} {a1_short:<22} {a2_country or 'N/A':<6} {a2_short:<22}")

    print()
    print('INTELLIGENCE VALUE:')
    print('  -> Code 1053: Demand release - Track detention cases (Two Michaels, etc.)')
    print('  -> Codes 022/026: Diplomatic cooperation/meeting appeals - Who seeks China support?')
    print('  -> Codes 021/0232/0234: Material/military cooperation appeals - Military dimension')
    print('  -> Code 0213: Judicial cooperation appeals - Legal/security cooperation')
else:
    print("No appeal/demand events found")

print()
print()


# ============================================================================
# QUERY 6: AID & INVESTMENT (Codes 070, 071, 072, 073) - EXPANDED!
# ============================================================================

print('QUERY 6: AID & INVESTMENT - EXPANDED!')
print('Event Codes: 070 (Provide aid), 071 (Economic aid), 072 (Military aid), 073 (Humanitarian aid)')
print('='*100)
print('EXPANDED: Added code 073 (Humanitarian aid - 143 events)')
print('Intelligence Value: BRI funding, infrastructure investment, aid packages')
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
WHERE event_code IN ('070', '071', '072', '073')
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
    print(f"{'Date':<12} {'Type':<12} {'Cntry1':<6} {'Actor1':<23} {'Cntry2':<6} {'Actor2':<23}")
    print('-'*100)

    for row in aid_events:
        date, code, a1_name, a1_country, a2_name, a2_country, url = row
        event_type = {
            '070': '070-Aid',
            '071': '071-EconAid',
            '072': '072-MilAid',
            '073': '073-HumAid'
        }[code]
        a1_short = (a1_name or 'N/A')[:22]
        a2_short = (a2_name or 'N/A')[:22]
        print(f"{date:<12} {event_type:<12} {a1_country or 'N/A':<6} {a1_short:<23} {a2_country or 'N/A':<6} {a2_short:<23}")

    print()
    print('CROSS-REFERENCE OPPORTUNITIES:')
    print('  -> CORDIS: Match to EU research grants')
    print('  -> TED/USASPENDING: Match to infrastructure contracts')
    print('  -> OpenAlex/OpenAire/arXiv: Link economic aid to research funding')
    print('  -> Open Sanctions/BIS: Check aid recipients for sanctions/PEPs/export controls')
    print('  -> AidData: Cross-reference with development finance database')
    print('  -> SEC EDGAR: Track equity stakes in aid recipient companies')
    print('  -> GLEIF/Companies House: Verify recipient entity structures')
    print('  -> BRI project tracking: Cross-reference economic aid events')
else:
    print("No aid/investment events found")

print()
print()


# ============================================================================
# QUERY 7: MILITARY COOPERATION (Code 062) - NEW!
# ============================================================================

print('QUERY 7: MILITARY COOPERATION - NEW!')
print('Event Code: 062 (Cooperate militarily)')
print('='*100)
print('NEW: Track military exercises, defense partnerships, arms deals')
print('Intelligence Value: China-Russia military cooperation, defense industry ties')
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
WHERE event_code = '062'
  AND (actor1_country_code = 'CHN' OR actor2_country_code = 'CHN')
  AND (
    actor1_country_code IN ({COUNTRY_LIST_SQL})
    OR actor2_country_code IN ({COUNTRY_LIST_SQL})
  )
ORDER BY event_date DESC
LIMIT 50
'''

cursor.execute(query)
mil_events = cursor.fetchall()

if mil_events:
    print(f"Found {len(mil_events)} military cooperation events (showing latest 50):")
    print()
    print(f"{'Date':<12} {'Cntry1':<6} {'Actor1':<30} {'Cntry2':<6} {'Actor2':<30}")
    print('-'*100)

    for row in mil_events:
        date, a1_name, a1_country, a2_name, a2_country, url = row
        a1_short = (a1_name or 'N/A')[:29]
        a2_short = (a2_name or 'N/A')[:29]
        print(f"{date:<12} {a1_country or 'N/A':<6} {a1_short:<30} {a2_country or 'N/A':<6} {a2_short:<30}")

    print()
    print('INTELLIGENCE VALUE:')
    print('  -> China-Russia military exercises')
    print('  -> Defense technology transfers')
    print('  -> Naval cooperation (ports, joint patrols)')
    print()
    print('CROSS-REFERENCE:')
    print('  -> BIS: Check entities against export control lists (military end-use)')
    print('  -> Open Sanctions: Verify military entities against sanctions databases')
    print('  -> USPTO/EPO: Track defense-related patent applications')
    print('  -> SEC EDGAR: Monitor defense contractor 13D/13G/13F filings')
    print('  -> GLEIF: Verify military entity legal identifiers')
    print('  -> PRC SOE database: Check if entities are state-owned enterprises')
else:
    print("No military cooperation events found")

print()
print()


# ============================================================================
# QUERY 8: IMPOSE SANCTIONS (Codes 163, 172) - CORRECTED!
# ============================================================================

print('QUERY 8: IMPOSE SANCTIONS - CORRECTED!')
print('Event Codes: 163 (Impose embargo/boycott/sanctions), 172 (Impose administrative sanctions)')
print('='*100)
print('MAJOR FIX: Added code 163 (REAL sanctions code), removed 174 (deportations)')
print('Intelligence Value: 5G bans, Xinjiang sanctions, tech export controls')
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
sanction_events = cursor.fetchall()

if sanction_events:
    print(f"Found {len(sanction_events)} impose sanctions events (showing latest 50):")
    print()
    print(f"{'Date':<12} {'Type':<11} {'Cntry1':<6} {'Actor1':<24} {'Cntry2':<6} {'Actor2':<24}")
    print('-'*100)

    for row in sanction_events:
        date, code, a1_name, a1_country, a2_name, a2_country, url = row
        event_type = '163-Embargo' if code == '163' else '172-AdminSanc'
        a1_short = (a1_name or 'N/A')[:23]
        a2_short = (a2_name or 'N/A')[:23]
        print(f"{date:<12} {event_type:<11} {a1_country or 'N/A':<6} {a1_short:<24} {a2_country or 'N/A':<6} {a2_short:<24}")

    print()
    print('INTELLIGENCE VALUE:')
    print('  -> Code 163: Economic embargoes, trade restrictions, boycotts')
    print('  -> Track EU sanctions on Chinese entities (Huawei, Hikvision, etc.)')
    print('  -> Monitor counter-sanctions from China on European entities')
    print()
    print('CROSS-REFERENCE:')
    print('  -> Open Sanctions: Match sanctioned entities to comprehensive sanctions databases')
    print('  -> BIS: Check Entity List, Denied Parties List, Unverified List')
    print('  -> TED/USASPENDING: Track procurement exclusions of sanctioned entities')
    print('  -> SEC EDGAR: Monitor 13D/G filings for sanctioned entity ownership changes')
    print('  -> GLEIF/Companies House: Track sanctioned entity subsidiaries and ownership')
    print('  -> USPTO/EPO: Monitor patent applications by sanctioned entities')
    print('  -> COMTRADE/Eurostat: Analyze trade impacts of sanctions')
else:
    print("No impose sanctions events found")

print()
print()


# ============================================================================
# QUERY 9: EASE SANCTIONS (Codes 081, 085) - CORRECTED!
# ============================================================================

print('QUERY 9: EASE SANCTIONS - CORRECTED!')
print('Event Codes: 081 (Ease administrative sanctions), 085 (Ease economic sanctions/boycott/embargo)')
print('='*100)
print('MAJOR FIX: Added code 085 (REAL ease sanctions code), removed 082 (political dissent)')
print('Intelligence Value: Sanctions de-escalation, 5G ban reversals, trade normalization')
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
ease_events = cursor.fetchall()

if ease_events:
    print(f"Found {len(ease_events)} ease sanctions events (showing latest 50):")
    print()
    print(f"{'Date':<12} {'Type':<12} {'Cntry1':<6} {'Actor1':<24} {'Cntry2':<6} {'Actor2':<24}")
    print('-'*100)

    for row in ease_events:
        date, code, a1_name, a1_country, a2_name, a2_country, url = row
        event_type = '081-EaseAdmin' if code == '081' else '085-EaseEcon'
        a1_short = (a1_name or 'N/A')[:23]
        a2_short = (a2_name or 'N/A')[:23]
        print(f"{date:<12} {event_type:<12} {a1_country or 'N/A':<6} {a1_short:<24} {a2_country or 'N/A':<6} {a2_short:<24}")

    print()
    print('INTELLIGENCE VALUE:')
    print('  -> Track sanctions de-escalation, normalization')
    print('  -> Identify countries easing restrictions on Chinese companies')
else:
    print("No ease sanctions events found")

print()
print()


# ============================================================================
# QUERY 10: POLICY DEMANDS (Code 1042) - CORRECTED!
# ============================================================================

print('QUERY 10: POLICY DEMANDS - CORRECTED!')
print('Event Code: 1042 (Demand policy change)')
print('='*100)
print('CORRECTED: Now using code 1042 (was 106 - which is actually "Demand withdrawal")')
print('Intelligence Value: Demands on Xinjiang, Hong Kong, Taiwan, tech practices')
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
demand_events = cursor.fetchall()

if demand_events:
    print(f"Found {len(demand_events)} policy demand events (showing latest 50):")
    print()
    print(f"{'Date':<12} {'Cntry1':<6} {'Actor1':<30} {'Cntry2':<6} {'Actor2':<30}")
    print('-'*100)

    for row in demand_events:
        date, a1_name, a1_country, a2_name, a2_country, url = row
        a1_short = (a1_name or 'N/A')[:29]
        a2_short = (a2_name or 'N/A')[:29]
        print(f"{date:<12} {a1_country or 'N/A':<6} {a1_short:<30} {a2_country or 'N/A':<6} {a2_short:<30}")

    print()
    print('INTELLIGENCE VALUE:')
    print('  -> European demands on China: human rights, trade practices, IP theft')
    print('  -> Chinese demands on Europe: Taiwan, Hong Kong, Xinjiang policies')
else:
    print("No policy demand events found")

print()
print()


# ============================================================================
# QUERY 11: LEGAL & SECURITY ACTIONS (7 codes)
# ============================================================================

print('QUERY 11: LEGAL & SECURITY ACTIONS')
print('Event Codes: 111 (Criticize/denounce), 112 (Accuse), 1125 (Accuse of espionage),')
print('             115 (Lawsuit), 116 (Find guilty), 173 (Arrest/detain), 1711 (Confiscate property)')
print('='*100)
print('Intelligence Value: Espionage accusations, IP theft lawsuits, arrests, asset seizures')
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
    print(f"{'Date':<12} {'Type':<13} {'Cntry1':<6} {'Actor1':<22} {'Cntry2':<6} {'Actor2':<22}")
    print('-'*100)

    for row in legal_events:
        date, code, a1_name, a1_country, a2_name, a2_country, url = row
        event_type = {
            '111': '111-Criticize',
            '112': '112-Accuse',
            '1125': '1125-AccuEsp',
            '115': '115-Lawsuit',
            '116': '116-FindGuilty',
            '173': '173-Arrest',
            '1711': '1711-Confiscate'
        }[code]
        a1_short = (a1_name or 'N/A')[:21]
        a2_short = (a2_name or 'N/A')[:21]
        print(f"{date:<12} {event_type:<13} {a1_country or 'N/A':<6} {a1_short:<22} {a2_country or 'N/A':<6} {a2_short:<22}")

    print()
    print('INTELLIGENCE VALUE:')
    print('  -> Code 1125: Espionage accusations (Huawei spying, researcher arrests)')
    print('  -> Code 173: Arrests of Chinese nationals, executives, researchers')
    print('  -> Code 1711: Asset confiscations, property seizures')
    print()
    print('CROSS-REFERENCE:')
    print('  -> Open Sanctions: Check arrested/accused entities for sanctions, PEPs, adverse media')
    print('  -> BIS: Verify against denied parties list, export violations')
    print('  -> USPTO/EPO: Track patent applications by arrested researchers/companies')
    print('  -> SEC EDGAR: Check 13D/G filings for ownership by arrested entities')
    print('  -> GLEIF/Companies House: Verify entity ownership structures')
    print('  -> PRC identifiers: Match to Chinese entity database')
    print('  -> GitHub: Check for code contributions by arrested researchers')
else:
    print("No legal/security events found")

print()
print()


# ============================================================================
# QUERY 12: DEPORTATIONS & EXPULSIONS (Code 174) - SEPARATED!
# ============================================================================

print('QUERY 12: DEPORTATIONS & EXPULSIONS - SEPARATED FROM SANCTIONS!')
print('Event Code: 174 (Expel or deport individuals)')
print('='*100)
print('MAJOR FIX: Separated from sanctions query - these are different event types')
print('Intelligence Value: Expelled diplomats, deported researchers, extradited individuals')
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
deport_events = cursor.fetchall()

if deport_events:
    print(f"Found {len(deport_events)} deportation/expulsion events (showing latest 50):")
    print()
    print(f"{'Date':<12} {'Cntry1':<6} {'Actor1':<30} {'Cntry2':<6} {'Actor2':<30}")
    print('-'*100)

    for row in deport_events:
        date, a1_name, a1_country, a2_name, a2_country, url = row
        a1_short = (a1_name or 'N/A')[:29]
        a2_short = (a2_name or 'N/A')[:29]
        print(f"{date:<12} {a1_country or 'N/A':<6} {a1_short:<30} {a2_country or 'N/A':<6} {a2_short:<30}")

    print()
    print('INTELLIGENCE VALUE:')
    print('  -> Track expelled Chinese diplomats (espionage, interference)')
    print('  -> Deported Chinese nationals (illegal activity, visa violations)')
    print('  -> Extraditions related to Chinese cases')
else:
    print("No deportation/expulsion events found")

print()
print()


# ============================================================================
# QUERY 13: INVESTIGATIONS (Code 092) - NEW!
# ============================================================================

print('QUERY 13: INVESTIGATIONS - NEW!')
print('Event Code: 092 (Investigate human rights abuses)')
print('='*100)
print('NEW: Track investigations into Chinese human rights issues')
print('Intelligence Value: Xinjiang investigations, Hong Kong abuses, forced labor probes')
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
WHERE event_code = '092'
  AND (actor1_country_code = 'CHN' OR actor2_country_code = 'CHN')
  AND (
    actor1_country_code IN ({COUNTRY_LIST_SQL})
    OR actor2_country_code IN ({COUNTRY_LIST_SQL})
  )
ORDER BY event_date DESC
LIMIT 50
'''

cursor.execute(query)
invest_events = cursor.fetchall()

if invest_events:
    print(f"Found {len(invest_events)} investigation events (showing latest 50):")
    print()
    print(f"{'Date':<12} {'Cntry1':<6} {'Actor1':<30} {'Cntry2':<6} {'Actor2':<30}")
    print('-'*100)

    for row in invest_events:
        date, a1_name, a1_country, a2_name, a2_country, url = row
        a1_short = (a1_name or 'N/A')[:29]
        a2_short = (a2_name or 'N/A')[:29]
        print(f"{date:<12} {a1_country or 'N/A':<6} {a1_short:<30} {a2_country or 'N/A':<6} {a2_short:<30}")

    print()
    print('INTELLIGENCE VALUE:')
    print('  -> European investigations into Xinjiang forced labor')
    print('  -> Hong Kong National Security Law violations')
    print('  -> Tibet human rights abuses')
else:
    print("No investigation events found")

print()
print()


# ============================================================================
# QUERY 14: DIPLOMATIC RECOGNITION (Code 054) - NEW!
# ============================================================================

print('QUERY 14: DIPLOMATIC RECOGNITION - NEW!')
print('Event Code: 054 (Grant diplomatic recognition)')
print('='*100)
print('NEW: Track Taiwan/China recognition switches, Kosovo, etc.')
print('Intelligence Value: One-China policy shifts, diplomatic competition')
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
WHERE event_code = '054'
  AND (actor1_country_code = 'CHN' OR actor2_country_code = 'CHN')
  AND (
    actor1_country_code IN ({COUNTRY_LIST_SQL})
    OR actor2_country_code IN ({COUNTRY_LIST_SQL})
  )
ORDER BY event_date DESC
LIMIT 50
'''

cursor.execute(query)
recog_events = cursor.fetchall()

if recog_events:
    print(f"Found {len(recog_events)} diplomatic recognition events (showing latest 50):")
    print()
    print(f"{'Date':<12} {'Cntry1':<6} {'Actor1':<30} {'Cntry2':<6} {'Actor2':<30}")
    print('-'*100)

    for row in recog_events:
        date, a1_name, a1_country, a2_name, a2_country, url = row
        a1_short = (a1_name or 'N/A')[:29]
        a2_short = (a2_name or 'N/A')[:29]
        print(f"{date:<12} {a1_country or 'N/A':<6} {a1_short:<30} {a2_country or 'N/A':<6} {a2_short:<30}")

    print()
    print('INTELLIGENCE VALUE:')
    print('  -> Track One-China policy adherence/shifts')
    print('  -> Lithuania-Taiwan representative office controversy')
    print('  -> Diplomatic competition with Taiwan in Europe')
else:
    print("No diplomatic recognition events found")

print()
print()


# ============================================================================
# QUERY 15: RELATIONSHIP DETERIORATION (Codes 161, 164, 125, 128) - NEW!
# ============================================================================

print('QUERY 15: RELATIONSHIP DETERIORATION - NEW!')
print('Event Codes: 161 (Reduce/break diplomatic relations), 164 (Halt negotiations),')
print('             125 (Reject proposal to meet/negotiate), 128 (Defy norms, law)')
print('='*100)
print('NEW: Track relationship cooling, breakdown of engagement')
print('Intelligence Value: Diplomatic crises, decoupling indicators, norm violations')
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
WHERE event_code IN ('161', '164', '125', '128')
  AND (actor1_country_code = 'CHN' OR actor2_country_code = 'CHN')
  AND (
    actor1_country_code IN ({COUNTRY_LIST_SQL})
    OR actor2_country_code IN ({COUNTRY_LIST_SQL})
  )
ORDER BY event_date DESC
LIMIT 50
'''

cursor.execute(query)
deterioration_events = cursor.fetchall()

if deterioration_events:
    print(f"Found {len(deterioration_events)} relationship deterioration events (showing latest 50):")
    print()
    print(f"{'Date':<12} {'Type':<13} {'Cntry1':<6} {'Actor1':<22} {'Cntry2':<6} {'Actor2':<22}")
    print('-'*100)

    for row in deterioration_events:
        date, code, a1_name, a1_country, a2_name, a2_country, url = row
        event_type = {
            '161': '161-BreakRel',
            '164': '164-HaltNegot',
            '125': '125-RejectMeet',
            '128': '128-DefyNorms'
        }[code]
        a1_short = (a1_name or 'N/A')[:21]
        a2_short = (a2_name or 'N/A')[:21]
        print(f"{date:<12} {event_type:<13} {a1_country or 'N/A':<6} {a1_short:<22} {a2_country or 'N/A':<6} {a2_short:<22}")

    print()
    print('INTELLIGENCE VALUE:')
    print('  -> Code 161: Diplomatic relations downgrade/severance')
    print('  -> Code 164: Halted negotiations - breakdown of engagement')
    print('  -> Code 128: Norm violations - WTO, international law, trade rules')
else:
    print("No relationship deterioration events found")

print()
print()


# ============================================================================
# QUERY 16: PROTESTS & STRIKES (Codes 141, 143) - EXPANDED!
# ============================================================================

print('QUERY 16: PROTESTS & STRIKES - EXPANDED!')
print('Event Codes: 141 (Demonstrate or rally), 143 (Conduct strike or boycott)')
print('='*100)
print('EXPANDED: Added code 143 (strikes/boycotts)')
print('Intelligence Value: Anti-China protests, Hong Kong solidarity, Xinjiang boycotts')
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
WHERE event_code IN ('141', '143')
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
    print(f"Found {len(protest_events)} protest/strike events (showing latest 50):")
    print()
    print(f"{'Date':<12} {'Type':<12} {'Cntry1':<6} {'Actor1':<24} {'Cntry2':<6} {'Actor2':<24}")
    print('-'*100)

    for row in protest_events:
        date, code, a1_name, a1_country, a2_name, a2_country, url = row
        event_type = '141-Protest' if code == '141' else '143-Strike'
        a1_short = (a1_name or 'N/A')[:23]
        a2_short = (a2_name or 'N/A')[:23]
        print(f"{date:<12} {event_type:<12} {a1_country or 'N/A':<6} {a1_short:<24} {a2_country or 'N/A':<6} {a2_short:<24}")

    print()
    print('INTELLIGENCE VALUE:')
    print('  -> Code 141: Anti-China protests, demonstrations')
    print('  -> Code 143: Boycotts (Xinjiang cotton, Beijing Olympics)')
    print('  -> Public opposition to Chinese influence')
else:
    print("No protest/strike events found")

print()
print()


# ============================================================================
# QUERY 17: RELEASES & ASYLUM (Codes 0841, 075) - EXPANDED!
# ============================================================================

print('QUERY 17: RELEASES & ASYLUM - EXPANDED!')
print('Event Codes: 0841 (Return, release person(s)), 075 (Grant asylum)')
print('='*100)
print('EXPANDED: Added code 075 (asylum - Xinjiang refugees, Hong Kong activists)')
print('Intelligence Value: Released detainees, asylum for dissidents, detention cycles')
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
WHERE event_code IN ('0841', '075')
  AND (actor1_country_code = 'CHN' OR actor2_country_code = 'CHN')
  AND (
    actor1_country_code IN ({COUNTRY_LIST_SQL})
    OR actor2_country_code IN ({COUNTRY_LIST_SQL})
  )
ORDER BY event_date DESC
LIMIT 50
'''

cursor.execute(query)
release_events = cursor.fetchall()

if release_events:
    print(f"Found {len(release_events)} release/asylum events (showing latest 50):")
    print()
    print(f"{'Date':<12} {'Type':<12} {'Cntry1':<6} {'Actor1':<24} {'Cntry2':<6} {'Actor2':<24}")
    print('-'*100)

    for row in release_events:
        date, code, a1_name, a1_country, a2_name, a2_country, url = row
        event_type = '0841-Release' if code == '0841' else '075-Asylum'
        a1_short = (a1_name or 'N/A')[:23]
        a2_short = (a2_name or 'N/A')[:23]
        print(f"{date:<12} {event_type:<12} {a1_country or 'N/A':<6} {a1_short:<24} {a2_country or 'N/A':<6} {a2_short:<24}")

    print()
    print('INTELLIGENCE VALUE:')
    print('  -> Code 0841: Released detainees (Two Michaels, executives, researchers)')
    print('  -> Code 075: Asylum granted to Uyghurs, Hong Kong activists, dissidents')
    print('  -> Track detention-release cycles as bargaining tool')
else:
    print("No release/asylum events found")

print()
print()


# ============================================================================
# QUERY 18: COMPLAINTS & OFFICIAL PROTESTS (Codes 114, 1042)
# ============================================================================

print('QUERY 18: COMPLAINTS & OFFICIAL PROTESTS')
print('Event Codes: 114 (Complain officially), 1042 (Demand policy change)')
print('='*100)
print('Intelligence Value: Government-to-government complaints, diplomatic tensions')
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
WHERE event_code IN ('114', '1042')
  AND (actor1_country_code = 'CHN' OR actor2_country_code = 'CHN')
  AND (
    actor1_country_code IN ({COUNTRY_LIST_SQL})
    OR actor2_country_code IN ({COUNTRY_LIST_SQL})
  )
ORDER BY event_date DESC
LIMIT 50
'''

cursor.execute(query)
complaint_events = cursor.fetchall()

if complaint_events:
    print(f"Found {len(complaint_events)} complaint/demand events (showing latest 50):")
    print()
    print(f"{'Date':<12} {'Type':<13} {'Cntry1':<6} {'Actor1':<23} {'Cntry2':<6} {'Actor2':<23}")
    print('-'*100)

    for row in complaint_events:
        date, code, a1_name, a1_country, a2_name, a2_country, url = row
        event_type = '114-Complain' if code == '114' else '1042-DemandPol'
        a1_short = (a1_name or 'N/A')[:22]
        a2_short = (a2_name or 'N/A')[:22]
        print(f"{date:<12} {event_type:<13} {a1_country or 'N/A':<6} {a1_short:<23} {a2_country or 'N/A':<6} {a2_short:<23}")

    print()
    print('INTELLIGENCE VALUE:')
    print('  -> Track diplomatic complaints and tensions')
    print('  -> Policy demands on both sides')
else:
    print("No complaint/demand events found")

print()
print()


# ============================================================================
# QUERY 19: MULTILATERAL DIPLOMACY (Code 129) - NEW!
# ============================================================================

print('QUERY 19: MULTILATERAL DIPLOMACY - VETO - NEW!')
print('Event Code: 129 (Veto)')
print('='*100)
print('NEW: Track Chinese/Russian vetoes at UN Security Council, European vetoes of China')
print('Intelligence Value: UN voting patterns, multilateral blocking')
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
WHERE event_code = '129'
  AND (actor1_country_code = 'CHN' OR actor2_country_code = 'CHN')
  AND (
    actor1_country_code IN ({COUNTRY_LIST_SQL})
    OR actor2_country_code IN ({COUNTRY_LIST_SQL})
  )
ORDER BY event_date DESC
LIMIT 50
'''

cursor.execute(query)
veto_events = cursor.fetchall()

if veto_events:
    print(f"Found {len(veto_events)} veto events (showing latest 50):")
    print()
    print(f"{'Date':<12} {'Cntry1':<6} {'Actor1':<30} {'Cntry2':<6} {'Actor2':<30}")
    print('-'*100)

    for row in veto_events:
        date, a1_name, a1_country, a2_name, a2_country, url = row
        a1_short = (a1_name or 'N/A')[:29]
        a2_short = (a2_name or 'N/A')[:29]
        print(f"{date:<12} {a1_country or 'N/A':<6} {a1_short:<30} {a2_country or 'N/A':<6} {a2_short:<30}")

    print()
    print('INTELLIGENCE VALUE:')
    print('  -> Chinese vetoes at UN Security Council')
    print('  -> EU/European vetoes of China-related initiatives')
    print('  -> Multilateral coalition patterns')
else:
    print("No veto events found")

print()
print()


# ============================================================================
# QUERY 20: VIOLENT EVENTS (Codes 181, 186) - NEW!
# ============================================================================

print('QUERY 20: VIOLENT EVENTS - NEW!')
print('Event Codes: 181 (Abduct, hijack, or take hostage), 186 (Assassinate)')
print('='*100)
print('NEW: Track hostage-taking, assassinations related to China-Europe')
print('Intelligence Value: High-profile incidents, security crises')
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
WHERE event_code IN ('181', '186')
  AND (actor1_country_code = 'CHN' OR actor2_country_code = 'CHN')
  AND (
    actor1_country_code IN ({COUNTRY_LIST_SQL})
    OR actor2_country_code IN ({COUNTRY_LIST_SQL})
  )
ORDER BY event_date DESC
LIMIT 50
'''

cursor.execute(query)
violent_events = cursor.fetchall()

if violent_events:
    print(f"Found {len(violent_events)} violent events (showing latest 50):")
    print()
    print(f"{'Date':<12} {'Type':<13} {'Cntry1':<6} {'Actor1':<23} {'Cntry2':<6} {'Actor2':<23}")
    print('-'*100)

    for row in violent_events:
        date, code, a1_name, a1_country, a2_name, a2_country, url = row
        event_type = '181-Hostage' if code == '181' else '186-Assassinate'
        a1_short = (a1_name or 'N/A')[:22]
        a2_short = (a2_name or 'N/A')[:22]
        print(f"{date:<12} {event_type:<13} {a1_country or 'N/A':<6} {a1_short:<23} {a2_country or 'N/A':<6} {a2_short:<23}")

    print()
    print('INTELLIGENCE VALUE:')
    print('  -> Code 181: Hostage situations (Two Michaels case)')
    print('  -> Code 186: Assassinations of dissidents, defectors')
    print('  -> High-profile security incidents')
else:
    print("No violent events found")

print()
print()


# ============================================================================
# QUERY 21: ECONOMIC COOPERATION (Code 061)
# ============================================================================

print('QUERY 21: ECONOMIC COOPERATION')
print('Event Code: 061 (Cooperate economically)')
print('='*100)
print('Intelligence Value: Trade deals, tech partnerships, commercial cooperation')
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
econ_coop_events = cursor.fetchall()

if econ_coop_events:
    print(f"Found {len(econ_coop_events)} economic cooperation events (showing latest 50):")
    print()
    print(f"{'Date':<12} {'Cntry1':<6} {'Actor1':<30} {'Cntry2':<6} {'Actor2':<30}")
    print('-'*100)

    for row in econ_coop_events:
        date, a1_name, a1_country, a2_name, a2_country, url = row
        a1_short = (a1_name or 'N/A')[:29]
        a2_short = (a2_name or 'N/A')[:29]
        print(f"{date:<12} {a1_country or 'N/A':<6} {a1_short:<30} {a2_country or 'N/A':<6} {a2_short:<30}")

    print()
    print('CROSS-REFERENCE OPPORTUNITIES:')
    print('  -> OpenAlex/OpenAire/arXiv: Match cooperation to research partnerships, co-authorships')
    print('  -> TED/USASPENDING: Match to EU/US public procurement contracts')
    print('  -> USPTO/EPO/CORDIS: Match to US/EU patent applications, EU research grants')
    print('  -> Open Sanctions/BIS: Verify entity sanctions status, PEPs, export controls')
    print('  -> SEC EDGAR: Check 13D/13G/13F filings for ownership stakes')
    print('  -> GLEIF/Companies House: Verify legal entity identifiers, ownership structures')
    print('  -> COMTRADE/Eurostat: Cross-check with bilateral trade flows')
    print('  -> GitHub: Track open source collaboration patterns')
    print('  -> Conferences: Match to academic/industry conference attendance')
else:
    print("No economic cooperation events found")

print()
print()


# ============================================================================
# QUERY 22: DEMANDS - POLICY SUPPORT (Code 102) - NEW!
# ============================================================================

print('QUERY 22: DEMANDS - POLICY SUPPORT - NEW!')
print('Event Code: 102 (Demand policy support)')
print('='*100)
print('NEW: Track demands for policy support and backing')
print('Intelligence Value: Political pressure, diplomatic coercion attempts')
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
WHERE event_code = '102'
  AND (actor1_country_code = 'CHN' OR actor2_country_code = 'CHN')
  AND (
    actor1_country_code IN ({COUNTRY_LIST_SQL})
    OR actor2_country_code IN ({COUNTRY_LIST_SQL})
  )
ORDER BY event_date DESC
LIMIT 50
'''

cursor.execute(query)
demand_events = cursor.fetchall()

if demand_events:
    print(f"Found {len(demand_events)} policy demand events (showing latest 50):")
    print()
    for row in demand_events[:10]:
        date, a1_name, a1_country, a2_name, a2_country, url = row
        print(f"{date}: {a1_name} ({a1_country}) -> {a2_name} ({a2_country})")
else:
    print("No policy demand events found")

print()
print()


# ============================================================================
# QUERY 23: ACCUSATIONS - AGGRESSION (Code 1123) - NEW!
# ============================================================================

print('QUERY 23: ACCUSATIONS OF AGGRESSION - NEW!')
print('Event Code: 1123 (Accuse of aggression)')
print('='*100)
print('NEW: Track accusations of aggression')
print('Intelligence Value: Conflict indicators, diplomatic tensions')
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
WHERE event_code = '1123'
  AND (actor1_country_code = 'CHN' OR actor2_country_code = 'CHN')
  AND (
    actor1_country_code IN ({COUNTRY_LIST_SQL})
    OR actor2_country_code IN ({COUNTRY_LIST_SQL})
  )
ORDER BY event_date DESC
LIMIT 50
'''

cursor.execute(query)
accusation_events = cursor.fetchall()

if accusation_events:
    print(f"Found {len(accusation_events)} aggression accusation events (showing latest 50):")
    print()
    for row in accusation_events[:10]:
        date, a1_name, a1_country, a2_name, a2_country, url = row
        print(f"{date}: {a1_name} ({a1_country}) accuses {a2_name} ({a2_country})")
else:
    print("No aggression accusation events found")

print()
print()


# ============================================================================
# QUERY 24: REJECTIONS - MATERIAL/MILITARY/SANCTIONS (Codes 121, 1241, 1242) - NEW!
# ============================================================================

print('QUERY 24: REJECTIONS - MATERIAL/MILITARY/SANCTIONS - NEW!')
print('Event Codes: 121 (Reject material cooperation), 1241 (Refuse ease admin sanctions),')
print('             1242 (Refuse ease dissent)')
print('='*100)
print('NEW: Track refusals of cooperation and sanctions relief')
print('Intelligence Value: Relationship breakdown indicators, sanctions persistence')
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
WHERE event_code IN ('121', '1241', '1242')
  AND (actor1_country_code = 'CHN' OR actor2_country_code = 'CHN')
  AND (
    actor1_country_code IN ({COUNTRY_LIST_SQL})
    OR actor2_country_code IN ({COUNTRY_LIST_SQL})
  )
ORDER BY event_date DESC
LIMIT 50
'''

cursor.execute(query)
rejection_events = cursor.fetchall()

if rejection_events:
    print(f"Found {len(rejection_events)} rejection events (showing latest 50):")
    print()
    for row in rejection_events[:10]:
        date, code, a1_name, a1_country, a2_name, a2_country, url = row
        event_type = {'121': 'REJECT MATERIAL COOP', '1241': 'REFUSE EASE SANCTIONS', '1242': 'REFUSE EASE DISSENT'}[code]
        print(f"{date}: {event_type} - {a1_name} ({a1_country}) -> {a2_name} ({a2_country})")
else:
    print("No rejection events found")

print()
print()


# ============================================================================
# QUERY 25: THREATS - COMPREHENSIVE (Codes 131, 132, 138, 1381-1385) - NEW!
# ============================================================================

print('QUERY 25: THREATS - COMPREHENSIVE TAXONOMY - NEW!')
print('Event Codes: 131 (Threaten non-force), 132 (Threaten admin sanctions), 138 (Threaten mil force),')
print('             1381 (Threaten blockade), 1382 (Threaten occupation), 1383 (Threaten unconventional),')
print('             1384 (Threaten attack), 1385 (Threaten WMD)')
print('='*100)
print('NEW: Full spectrum of threat types from diplomatic to WMD')
print('Intelligence Value: Escalation indicators, coercive diplomacy patterns')
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
WHERE event_code IN ('131', '132', '138', '1381', '1382', '1383', '1384', '1385')
  AND (actor1_country_code = 'CHN' OR actor2_country_code = 'CHN')
  AND (
    actor1_country_code IN ({COUNTRY_LIST_SQL})
    OR actor2_country_code IN ({COUNTRY_LIST_SQL})
  )
ORDER BY event_date DESC
LIMIT 50
'''

cursor.execute(query)
threat_events = cursor.fetchall()

if threat_events:
    print(f"Found {len(threat_events)} threat events (showing latest 50):")
    print()
    for row in threat_events[:10]:
        date, code, a1_name, a1_country, a2_name, a2_country, url = row
        threat_types = {
            '131': 'THREAT NON-FORCE',
            '132': 'THREAT ADMIN SANCT',
            '138': 'THREAT MIL FORCE',
            '1381': 'THREAT BLOCKADE',
            '1382': 'THREAT OCCUPATION',
            '1383': 'THREAT UNCONVENT',
            '1384': 'THREAT ATTACK',
            '1385': 'THREAT WMD'
        }
        event_type = threat_types[code]
        print(f"{date}: {event_type} - {a1_name} ({a1_country}) -> {a2_name} ({a2_country})")
else:
    print("No threat events found")

print()
print()


# ============================================================================
# QUERY 26: FORCE POSTURE (Code 150) - NEW!
# ============================================================================

print('QUERY 26: FORCE POSTURE - DEMONSTRATE MILITARY/POLICE POWER - NEW!')
print('Event Code: 150 (Demonstrate military or police power)')
print('='*100)
print('NEW: Track military demonstrations and power projection')
print('Intelligence Value: Intimidation tactics, territorial assertions')
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
WHERE event_code = '150'
  AND (actor1_country_code = 'CHN' OR actor2_country_code = 'CHN')
  AND (
    actor1_country_code IN ({COUNTRY_LIST_SQL})
    OR actor2_country_code IN ({COUNTRY_LIST_SQL})
  )
ORDER BY event_date DESC
LIMIT 50
'''

cursor.execute(query)
force_events = cursor.fetchall()

if force_events:
    print(f"Found {len(force_events)} force posture events (showing latest 50):")
    print()
    for row in force_events[:10]:
        date, a1_name, a1_country, a2_name, a2_country, url = row
        print(f"{date}: {a1_name} ({a1_country}) demonstrates power vs {a2_name} ({a2_country})")
else:
    print("No force posture events found")

print()
print()


# ============================================================================
# QUERY 27: COERCION (Code 170) - NEW!
# ============================================================================

print('QUERY 27: COERCION - GENERAL - NEW!')
print('Event Code: 170 (Coerce, not specified below)')
print('='*100)
print('NEW: Track coercive actions not otherwise categorized')
print('Intelligence Value: Economic coercion, diplomatic pressure tactics')
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
WHERE event_code = '170'
  AND (actor1_country_code = 'CHN' OR actor2_country_code = 'CHN')
  AND (
    actor1_country_code IN ({COUNTRY_LIST_SQL})
    OR actor2_country_code IN ({COUNTRY_LIST_SQL})
  )
ORDER BY event_date DESC
LIMIT 50
'''

cursor.execute(query)
coercion_events = cursor.fetchall()

if coercion_events:
    print(f"Found {len(coercion_events)} coercion events (showing latest 50):")
    print()
    for row in coercion_events[:10]:
        date, a1_name, a1_country, a2_name, a2_country, url = row
        print(f"{date}: {a1_name} ({a1_country}) coerces {a2_name} ({a2_country})")
else:
    print("No coercion events found")

print()
print()


# ============================================================================
# QUERY 28: MILITARY BLOCKADES (Code 191) - NEW!
# ============================================================================

print('QUERY 28: MILITARY BLOCKADES - NEW!')
print('Event Code: 191 (Impose blockade, restrict movement)')
print('='*100)
print('NEW: Track naval/military blockades and movement restrictions')
print('Intelligence Value: Maritime security, territorial disputes, Taiwan Strait')
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
WHERE event_code = '191'
  AND (actor1_country_code = 'CHN' OR actor2_country_code = 'CHN')
  AND (
    actor1_country_code IN ({COUNTRY_LIST_SQL})
    OR actor2_country_code IN ({COUNTRY_LIST_SQL})
  )
ORDER BY event_date DESC
LIMIT 50
'''

cursor.execute(query)
blockade_events = cursor.fetchall()

if blockade_events:
    print(f"Found {len(blockade_events)} military blockade events (showing latest 50):")
    print()
    for row in blockade_events[:10]:
        date, a1_name, a1_country, a2_name, a2_country, url = row
        print(f"{date}: {a1_name} ({a1_country}) imposes blockade vs {a2_name} ({a2_country})")
else:
    print("No military blockade events found")

print()
print()


# ============================================================================
# QUERY 29: WMD & UNCONVENTIONAL MASS VIOLENCE (Codes 204, 2041, 2042) - NEW!
# ============================================================================

print('QUERY 29: WMD & UNCONVENTIONAL MASS VIOLENCE - NEW!')
print('Event Codes: 204 (Unconventional mass violence), 2041 (CBR weapons), 2042 (Nuclear weapons)')
print('='*100)
print('NEW: Track WMD use and unconventional violence')
print('Intelligence Value: Extreme escalation indicators, nuclear threat tracking')
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
WHERE event_code IN ('204', '2041', '2042')
  AND (actor1_country_code = 'CHN' OR actor2_country_code = 'CHN')
  AND (
    actor1_country_code IN ({COUNTRY_LIST_SQL})
    OR actor2_country_code IN ({COUNTRY_LIST_SQL})
  )
ORDER BY event_date DESC
LIMIT 50
'''

cursor.execute(query)
wmd_events = cursor.fetchall()

if wmd_events:
    print(f"Found {len(wmd_events)} WMD/mass violence events (showing latest 50):")
    print()
    for row in wmd_events[:10]:
        date, code, a1_name, a1_country, a2_name, a2_country, url = row
        wmd_types = {
            '204': 'UNCONVENTIONAL VIOLENCE',
            '2041': 'CBR WEAPONS USE',
            '2042': 'NUCLEAR WEAPONS USE'
        }
        event_type = wmd_types[code]
        print(f"{date}: {event_type} - {a1_name} ({a1_country}) -> {a2_name} ({a2_country})")
    print()
    print('⚠️  CRITICAL: WMD events require immediate escalation and verification')
else:
    print("No WMD/mass violence events found")

print()
print()


print('='*100)
print('SUMMARY STATISTICS - EXPANDED EVENT COVERAGE (89 CODES)')
print('='*100)

categories = {
    'Cooperation (verified codes)': ['030','040','042','043','057','061','064','120','130','140'],
    'Diplomatic Support/Rhetoric (RE-ADDED + NEW)': ['051','052','019'],
    'Diplomatic Engagement': ['044','045','046'],
    'Intent/Planning (EXPANDED)': ['036','0311','0331','032'],
    'Appeals (NEW)': ['022','026','0214','1053'],
    'Aid/Investment (EXPANDED)': ['070','071','072','073'],
    'Military Cooperation (NEW)': ['062'],
    'Sanctions - IMPOSE': ['163','172'],
    'Sanctions - EASE': ['081','085'],
    'Policy Demands': ['1042'],
    'Legal/Security': ['111','112','1125','115','116','173','1711'],
    'Deportations': ['174'],
    'Investigations (NEW)': ['092'],
    'Diplomatic Recognition (NEW)': ['054'],
    'Relationship Deterioration (NEW)': ['161','164','125','128'],
    'Protests/Strikes (EXPANDED)': ['141','143'],
    'Releases/Asylum (EXPANDED)': ['0841','075'],
    'Complaints/Violations': ['114','1042'],
    'Multilateral (NEW)': ['129'],
    'Violent Events (NEW)': ['181','186'],
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
print('EXPANSION CHANGES:')
print('  - Code 051 RE-ADDED (Praise/endorse - diplomatic support tracking)')
print('  - Code 073 ADDED (Provide humanitarian aid - 143 events)')
print('  - Code 062 ADDED (Cooperate militarily - 146 events)')
print('  - Code 054 ADDED (Grant diplomatic recognition - 115 events)')
print('  - Code 161 ADDED (Reduce/break diplomatic relations - 76 events)')
print('  - Code 129 ADDED (Veto - 68 events)')
print('  - Code 128 ADDED (Defy norms, law - 70 events)')
print('  - Code 164 ADDED (Halt negotiations - 60 events)')
print('  - Code 125 ADDED (Reject proposal to meet/negotiate - 60 events)')
print('  + 13 additional Tier 3 codes (appeals, strikes, asylum, investigations, etc.)')
print()
print(f'Previous version: 34 codes')
print(f'Expanded version: {len(EVENT_CODES)} codes')
print(f'Net addition: +{len(EVENT_CODES) - 34} codes')
print()
print('='*100)

db.close()

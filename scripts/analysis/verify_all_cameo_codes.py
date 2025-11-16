#!/usr/bin/env python3
"""
COMPREHENSIVE CAMEO CODE VERIFICATION
Systematically verify ALL CAMEO codes against official documentation
and database reality to identify mislabeling and missed opportunities.
"""

import sqlite3
import json
from pathlib import Path
from collections import defaultdict

DB_PATH = 'F:/OSINT_WAREHOUSE/osint_master.db'

# Official CAMEO event codes from https://www.gdeltproject.org/data/lookups/CAMEO.eventcodes.txt
OFFICIAL_CAMEO_CODES = {
    # Category 01: MAKE PUBLIC STATEMENT
    '010': 'Make statement, not specified below',
    '011': 'Decline comment',
    '012': 'Make pessimistic comment',
    '013': 'Make optimistic comment',
    '014': 'Consider policy option',
    '015': 'Acknowledge or claim responsibility',
    '016': 'Deny responsibility',
    '017': 'Engage in symbolic act',
    '018': 'Make empathetic comment',
    '019': 'Express accord',

    # Category 02: APPEAL
    '020': 'Appeal, not specified below',
    '021': 'Appeal for material cooperation, not specified below',
    '0211': 'Appeal for economic cooperation',
    '0212': 'Appeal for military cooperation',
    '0213': 'Appeal for judicial cooperation',
    '0214': 'Appeal for intelligence',
    '022': 'Appeal for diplomatic cooperation, such as policy support',
    '023': 'Appeal for aid, not specified below',
    '0231': 'Appeal for economic aid',
    '0232': 'Appeal for military aid',
    '0233': 'Appeal for humanitarian aid',
    '0234': 'Appeal for military protection or peacekeeping',
    '024': 'Appeal for political reform, not specified below',
    '0241': 'Appeal for change in leadership',
    '0242': 'Appeal for policy change',
    '0243': 'Appeal for rights',
    '0244': 'Appeal for change in institutions, regime',
    '025': 'Appeal to yield',
    '0251': 'Appeal for easing of administrative sanctions',
    '0252': 'Appeal for easing of popular dissent',
    '0253': 'Appeal for release of persons or property',
    '0254': 'Appeal for easing of economic sanctions, boycott, or embargo',
    '0255': 'Appeal for target to allow international involvement (non-mediation)',
    '0256': 'Appeal for de-escalation of military engagement',
    '026': 'Appeal to others to meet or negotiate',
    '027': 'Appeal to others to settle dispute',
    '028': 'Appeal to others to engage in or accept mediation',

    # Category 03: EXPRESS INTENT TO COOPERATE
    '030': 'Express intent to cooperate, not specified below',
    '031': 'Express intent to engage in material cooperation, not specified below',
    '0311': 'Express intent to cooperate economically',
    '0312': 'Express intent to cooperate militarily',
    '0313': 'Express intent to cooperate on judicial matters',
    '0314': 'Express intent to cooperate on intelligence',
    '032': 'Express intent to provide diplomatic cooperation such as policy support',
    '033': 'Express intent to provide material aid, not specified below',
    '0331': 'Express intent to provide economic aid',
    '0332': 'Express intent to provide military aid',
    '0333': 'Express intent to provide humanitarian aid',
    '0334': 'Express intent to provide military protection or peacekeeping',
    '034': 'Express intent to institute political reform, not specified below',
    '0341': 'Express intent to change leadership',
    '0342': 'Express intent to change policy',
    '0343': 'Express intent to provide rights',
    '0344': 'Express intent to change institutions, regime',
    '035': 'Express intent to yield, not specified below',
    '0351': 'Express intent to ease administrative sanctions',
    '0352': 'Express intent to ease popular dissent',
    '0353': 'Express intent to release persons or property',
    '0354': 'Express intent to ease economic sanctions, boycott, or embargo',
    '0355': 'Express intent allow international involvement (not mediation)',
    '0356': 'Express intent to de-escalate military engagement',
    '036': 'Express intent to meet or negotiate',
    '037': 'Express intent to settle dispute',
    '038': 'Express intent to accept mediation',
    '039': 'Express intent to mediate',

    # Category 04: CONSULT
    '040': 'Consult, not specified below',
    '041': 'Discuss by telephone',
    '042': 'Make a visit',
    '043': 'Host a visit',
    '044': 'Meet at a third location',
    '045': 'Mediate',
    '046': 'Engage in negotiation',

    # Category 05: ENGAGE IN DIPLOMATIC COOPERATION
    '050': 'Engage in diplomatic cooperation, not specified below',
    '051': 'Praise or endorse',
    '052': 'Defend verbally',
    '053': 'Rally support on behalf of',
    '054': 'Grant diplomatic recognition',
    '055': 'Apologize',
    '056': 'Forgive',
    '057': 'Sign formal agreement',

    # Category 06: ENGAGE IN MATERIAL COOPERATION
    '060': 'Engage in material cooperation, not specified below',
    '061': 'Cooperate economically',
    '062': 'Cooperate militarily',
    '063': 'Engage in judicial cooperation',
    '064': 'Share intelligence or information',

    # Category 07: PROVIDE AID
    '070': 'Provide aid, not specified below',
    '071': 'Provide economic aid',
    '072': 'Provide military aid',
    '073': 'Provide humanitarian aid',
    '074': 'Provide military protection or peacekeeping',
    '075': 'Grant asylum',

    # Category 08: YIELD
    '080': 'Yield, not specified below',
    '081': 'Ease administrative sanctions',
    '0811': 'Ease restrictions on political freedoms',
    '0812': 'Ease ban on political parties or politicians',
    '0813': 'Ease curfew',
    '0814': 'Ease state of emergency or martial law',
    '082': 'Ease political dissent',
    '083': 'Accede to requests or demands for political reform not specified below',
    '0831': 'Accede to demands for change in leadership',
    '0832': 'Accede to demands for change in policy',
    '0833': 'Accede to demands for rights',
    '0834': 'Accede to demands for change in institutions, regime',
    '084': 'Return, release, not specified below',
    '0841': 'Return, release person(s)',
    '0842': 'Return, release property',
    '085': 'Ease economic sanctions, boycott, embargo',
    '086': 'Allow international involvement not specified below',
    '0861': 'Receive deployment of peacekeepers',
    '0862': 'Receive inspectors',
    '0863': 'Allow delivery of humanitarian aid',
    '087': 'De-escalate military engagement',
    '0871': 'Declare truce, ceasefire',
    '0872': 'Ease military blockade',
    '0873': 'Demobilize armed forces',
    '0874': 'Retreat or surrender militarily',

    # Category 09: INVESTIGATE
    '090': 'Investigate, not specified below',
    '091': 'Investigate crime, corruption',
    '092': 'Investigate human rights abuses',
    '093': 'Investigate military action',
    '094': 'Investigate war crimes',

    # Category 10: DEMAND
    '100': 'Demand, not specified below',
    '101': 'Demand information, investigation',
    '1011': 'Demand economic cooperation',
    '1012': 'Demand military cooperation',
    '1013': 'Demand judicial cooperation',
    '1014': 'Demand intelligence cooperation',
    '102': 'Demand policy support',
    '103': 'Demand aid, protection, or peacekeeping',
    '1031': 'Demand economic aid',
    '1032': 'Demand military aid',
    '1033': 'Demand humanitarian aid',
    '1034': 'Demand military protection or peacekeeping',
    '104': 'Demand political reform, not specified below',
    '1041': 'Demand change in leadership',
    '1042': 'Demand policy change',
    '1043': 'Demand rights',
    '1044': 'Demand change in institutions, regime',
    '105': 'Demand mediation',
    '1051': 'Demand easing of administrative sanctions',
    '1052': 'Demand easing of political dissent',
    '1053': 'Demand release of persons or property',
    '1054': 'Demand easing of economic sanctions, boycott, or embargo',
    '1055': 'Demand that target allows international involvement (non-mediation)',
    '1056': 'Demand de-escalation of military engagement',
    '106': 'Demand withdrawal',
    '107': 'Demand ceasefire',
    '108': 'Demand meeting, negotiation',

    # Category 11: DISAPPROVE
    '110': 'Disapprove, not specified below',
    '111': 'Criticize or denounce',
    '112': 'Accuse, not specified below',
    '1121': 'Accuse of crime, corruption',
    '1122': 'Accuse of human rights abuses',
    '1123': 'Accuse of aggression',
    '1124': 'Accuse of war crimes',
    '1125': 'Accuse of espionage, treason',
    '113': 'Rally opposition against',
    '114': 'Complain officially',
    '115': 'Bring lawsuit against',
    '116': 'Find guilty or liable (legally)',

    # Category 12: REJECT
    '120': 'Reject, not specified below',
    '121': 'Reject material cooperation',
    '1211': 'Reject economic cooperation',
    '1212': 'Reject military cooperation',
    '122': 'Reject request or demand for material aid, not specified below',
    '1221': 'Reject request for economic aid',
    '1222': 'Reject request for military aid',
    '1223': 'Reject request for humanitarian aid',
    '1224': 'Reject request for military protection or peacekeeping',
    '123': 'Reject request or demand for political reform, not specified below',
    '1231': 'Reject request for change in leadership',
    '1232': 'Reject request for policy change',
    '1233': 'Reject request for rights',
    '1234': 'Reject request for change in institutions, regime',
    '124': 'Refuse to yield, not specified below',
    '1241': 'Refuse to ease administrative sanctions',
    '1242': 'Refuse to ease popular dissent',
    '1243': 'Refuse to release persons or property',
    '1244': 'Refuse to ease economic sanctions, boycott, or embargo',
    '1245': 'Refuse to allow international involvement (non mediation)',
    '1246': 'Refuse to de-escalate military engagement',
    '125': 'Reject proposal to meet, discuss, or negotiate',
    '126': 'Reject mediation',
    '127': 'Reject plan, agreement to settle dispute',
    '128': 'Defy norms, law',
    '129': 'Veto',

    # Category 13: THREATEN
    '130': 'Threaten, not specified below',
    '131': 'Threaten non-force, not specified below',
    '1311': 'Threaten to reduce or stop aid',
    '1312': 'Threaten to boycott, embargo, or sanction',
    '1313': 'Threaten to reduce or break relations',
    '132': 'Threaten with administrative sanctions, not specified below',
    '1321': 'Threaten to impose restrictions on political freedoms',
    '1322': 'Threaten to ban political parties or politicians',
    '1323': 'Threaten to impose curfew',
    '1324': 'Threaten to impose state of emergency or martial law',
    '133': 'Threaten political dissent, protest',
    '134': 'Threaten to halt negotiations',
    '135': 'Threaten to halt mediation',
    '136': 'Threaten to halt international involvement (non-mediation)',
    '137': 'Threaten with violent repression',
    '138': 'Threaten to use military force, not specified below',
    '1381': 'Threaten blockade',
    '1382': 'Threaten occupation',
    '1383': 'Threaten unconventional violence',
    '1384': 'Threaten conventional attack',
    '1385': 'Threaten attack with WMD',
    '139': 'Give ultimatum',

    # Category 14: PROTEST
    '140': 'Engage in political dissent, not specified below',
    '141': 'Demonstrate or rally',
    '1411': 'Demonstrate for leadership change',
    '1412': 'Demonstrate for policy change',
    '1413': 'Demonstrate for rights',
    '1414': 'Demonstrate for change in institutions, regime',
    '142': 'Conduct hunger strike, not specified below',
    '1421': 'Conduct hunger strike for leadership change',
    '1422': 'Conduct hunger strike for policy change',
    '1423': 'Conduct hunger strike for rights',
    '1424': 'Conduct hunger strike for change in institutions, regime',
    '143': 'Conduct strike or boycott, not specified below',
    '1431': 'Conduct strike or boycott for leadership change',
    '1432': 'Conduct strike or boycott for policy change',
    '1433': 'Conduct strike or boycott for rights',
    '1434': 'Conduct strike or boycott for change in institutions, regime',
    '144': 'Obstruct passage, block',
    '1441': 'Obstruct passage to demand leadership change',
    '1442': 'Obstruct passage to demand policy change',
    '1443': 'Obstruct passage to demand rights',
    '1444': 'Obstruct passage to demand change in institutions, regime',
    '145': 'Protest violently, riot',
    '1451': 'Engage in violent protest for leadership change',
    '1452': 'Engage in violent protest for policy change',
    '1453': 'Engage in violent protest for rights',
    '1454': 'Engage in violent protest for change in institutions, regime',

    # Category 15: EXHIBIT FORCE POSTURE
    '150': 'Demonstrate military or police power, not specified below',
    '151': 'Increase police alert status',
    '152': 'Increase military alert status',
    '153': 'Mobilize or increase police power',
    '154': 'Mobilize or increase armed forces',

    # Category 16: REDUCE RELATIONS
    '160': 'Reduce relations, not specified below',
    '161': 'Reduce or break diplomatic relations',
    '162': 'Reduce or stop aid, not specified below',
    '1621': 'Reduce or stop economic assistance',
    '1622': 'Reduce or stop military assistance',
    '1623': 'Reduce or stop humanitarian assistance',
    '163': 'Impose embargo, boycott, or sanctions',
    '164': 'Halt negotiations',
    '165': 'Halt mediation',
    '166': 'Expel or withdraw, not specified below',
    '1661': 'Expel or withdraw peacekeepers',
    '1662': 'Expel or withdraw inspectors, observers',
    '1663': 'Expel or withdraw aid agencies',

    # Category 17: COERCE
    '170': 'Coerce, not specified below',
    '171': 'Seize or damage property, not specified below',
    '1711': 'Confiscate property',
    '1712': 'Destroy property',
    '172': 'Impose administrative sanctions',
    '1721': 'Impose restrictions on political freedoms',
    '1722': 'Ban political parties or politicians',
    '1723': 'Impose curfew',
    '1724': 'Impose state of emergency or martial law',
    '173': 'Arrest, detain, or charge with legal action',
    '174': 'Expel or deport individuals',
    '175': 'Use tactics of violent repression',

    # Category 18: ASSAULT
    '180': 'Use unconventional violence, not specified below',
    '181': 'Abduct, hijack, or take hostage',
    '182': 'Physically assault, not specified below',
    '1821': 'Sexually assault',
    '1822': 'Torture',
    '1823': 'Kill by physical assault',
    '183': 'Conduct suicide, car, or other non-military bombing, not spec below',
    '1831': 'Carry out suicide bombing',
    '1832': 'Carry out car bombing',
    '1833': 'Carry out roadside bombing',
    '184': 'Use as human shield',
    '185': 'Attempt to assassinate',
    '186': 'Assassinate',

    # Category 19: FIGHT
    '190': 'Use conventional military force, not specified below',
    '191': 'Impose blockade, restrict movement',
    '192': 'Occupy territory',
    '193': 'Fight with small arms and light weapons',
    '194': 'Fight with artillery and tanks',
    '195': 'Employ aerial weapons',
    '196': 'Violate ceasefire',

    # Category 20: USE UNCONVENTIONAL MASS VIOLENCE
    '200': 'Use unconventional mass violence, not specified below',
    '201': 'Engage in mass expulsion',
    '202': 'Engage in mass killings',
    '203': 'Engage in ethnic cleansing',
    '204': 'Use weapons of mass destruction, not specified below',
    '2041': 'Use chemical, biological, or radiological weapons',
    '2042': 'Detonate nuclear weapons',
}

# Codes we're currently using with our labels
OUR_CURRENT_CODES = {
    # Original codes
    '030': 'Intent to cooperate',
    '040': 'Consult',
    '042': 'Official visit',
    '043': 'Diplomatic cooperation',
    '045': 'Material cooperation (engage)',
    '046': 'Material cooperation (receive)',  # SUSPECTED ERROR
    '051': 'Economic cooperation',
    '057': 'Formal agreement signed',
    '061': 'Cooperate economically',
    '064': 'Share intelligence/information',

    # Phase 1: Aid/Investment
    '070': 'Provide aid (general)',
    '071': 'Provide economic aid (BRI)',
    '072': 'Provide military aid',
    '0234': 'Appeal for technical aid',

    # Phase 1: Sanctions/Policy
    '081': 'Ease administrative sanctions',
    '082': 'Ease economic sanctions',
    '106': 'Demand policy change',
    '172': 'Impose administrative sanctions',
    '174': 'Impose economic sanctions',  # SUSPECTED ERROR

    # Phase 1: Legal/Security
    '111': 'Criticize/denounce',
    '112': 'Accuse (general)',
    '1125': 'Accuse of espionage',
    '115': 'Bring lawsuit',
    '116': 'Find guilty/liable',
    '173': 'Arrest/detain/charge',
    '1711': 'Confiscate property',

    # Multilateral
    '120': 'Reject',
    '130': 'Threaten',
    '140': 'Protest'
}

def connect_db():
    """Connect to GDELT database"""
    return sqlite3.connect(DB_PATH)

def get_sample_events(conn, code, limit=5):
    """Get sample events for a given code"""
    cur = conn.cursor()
    cur.execute('''
        SELECT event_date, actor1_name, actor1_country_code,
               actor2_name, actor2_country_code, source_url
        FROM gdelt_events
        WHERE event_code = ?
        AND (actor1_country_code = 'CHN' OR actor2_country_code = 'CHN')
        ORDER BY event_date DESC
        LIMIT ?
    ''', (code, limit))
    return cur.fetchall()

def get_event_count(conn, code):
    """Get total count of events for a code"""
    cur = conn.cursor()
    cur.execute('''
        SELECT COUNT(*)
        FROM gdelt_events
        WHERE event_code = ?
        AND (actor1_country_code = 'CHN' OR actor2_country_code = 'CHN')
    ''', (code,))
    return cur.fetchone()[0]

def main():
    print('='*100)
    print('COMPREHENSIVE CAMEO CODE VERIFICATION')
    print('Verifying ALL codes against official CAMEO documentation and database reality')
    print('='*100)
    print()

    conn = connect_db()

    verification_results = {
        'correct': [],
        'incorrect': [],
        'not_in_use_high_value': [],
        'not_in_use_moderate_value': [],
        'verification_details': {}
    }

    # Phase 1: Verify codes we're currently using
    print('PHASE 1: VERIFYING CODES CURRENTLY IN USE (30 codes)')
    print('='*100)
    print()

    for code, our_label in sorted(OUR_CURRENT_CODES.items()):
        official_label = OFFICIAL_CAMEO_CODES.get(code, 'CODE NOT FOUND IN OFFICIAL CAMEO')
        count = get_event_count(conn, code)
        samples = get_sample_events(conn, code, 3)

        # Check if labels match (fuzzy matching for minor wording differences)
        labels_match = (
            our_label.lower() in official_label.lower() or
            official_label.lower() in our_label.lower() or
            our_label.lower().replace('/', ' ') == official_label.lower().replace('/', ' ')
        )

        result = {
            'code': code,
            'our_label': our_label,
            'official_label': official_label,
            'count': count,
            'samples': samples,
            'match': labels_match
        }

        verification_results['verification_details'][code] = result

        if labels_match:
            verification_results['correct'].append(code)
            status = '[OK] CORRECT'
        else:
            verification_results['incorrect'].append(code)
            status = '[ERROR] MISMATCH'

        print(f'Code {code:6s} | {status}')
        print(f'  Our Label:      {our_label}')
        print(f'  Official Label: {official_label}')
        print(f'  Count: {count:,} events')

        if samples:
            print(f'  Sample Events:')
            for event in samples[:2]:
                date, a1, c1, a2, c2, url = event
                a1 = (a1 or 'N/A')[:20]
                a2 = (a2 or 'N/A')[:20]
                print(f'    {date[:8]}: {a1} -> {a2}')
        else:
            print(f'  No sample events found')

        print()

    print()
    print('='*100)
    print('PHASE 2: CHECKING HIGH-VALUE UNUSED CODES')
    print('='*100)
    print()

    # High-priority codes to check (from earlier analysis)
    high_priority_unused = [
        '019', '0211', '0214', '022', '026',  # Statements and appeals
        '0311', '0314', '036', '032', '0331',  # Intent to cooperate
        '044', '052', '053', '054',  # Consult and diplomatic
        '062', '063', '073', '075',  # Material cooperation and aid
        '085', '0841', '0862',  # Yield
        '091', '092',  # Investigate
        '1011', '1053', '101', '1054',  # Demand
        '1121', '114', '113',  # Disapprove
        '1211', '125', '128', '129', '1244',  # Reject
        '1312', '134', '139', '1311', '1313',  # Threaten
        '141', '143', '1412',  # Protest
        '161', '163', '164', '1621',  # Reduce relations (163 is CRITICAL!)
        '181', '186',  # Assault
    ]

    for code in high_priority_unused:
        if code in OUR_CURRENT_CODES:
            continue  # Skip codes we're already using

        official_label = OFFICIAL_CAMEO_CODES.get(code, 'CODE NOT FOUND')
        count = get_event_count(conn, code)
        samples = get_sample_events(conn, code, 3)

        # Assess value based on count and description
        if count > 50:
            value = 'HIGH'
            verification_results['not_in_use_high_value'].append({
                'code': code,
                'label': official_label,
                'count': count,
                'samples': samples
            })
        elif count > 10:
            value = 'MODERATE'
            verification_results['not_in_use_moderate_value'].append({
                'code': code,
                'label': official_label,
                'count': count,
                'samples': samples
            })
        else:
            continue  # Skip low-count codes in summary

        print(f'Code {code:6s} | {value} VALUE | Count: {count:,}')
        print(f'  Official Label: {official_label}')

        if samples:
            print(f'  Sample Events:')
            for event in samples[:2]:
                date, a1, c1, a2, c2, url = event
                a1 = (a1 or 'N/A')[:20]
                a2 = (a2 or 'N/A')[:20]
                print(f'    {date[:8]}: {c1 or "??"} {a1} -> {c2 or "??"} {a2}')
                if url:
                    domain = url.split('/')[2] if len(url.split('/')) > 2 else url[:50]
                    print(f'              {domain}')
        print()

    print()
    print('='*100)
    print('SUMMARY')
    print('='*100)
    print()
    print(f'Codes Currently in Use: {len(OUR_CURRENT_CODES)}')
    print(f'  [OK] Correctly Labeled: {len(verification_results["correct"])}')
    print(f'  [ERROR] Incorrectly Labeled: {len(verification_results["incorrect"])}')
    print()
    print(f'High-Value Unused Codes Found: {len(verification_results["not_in_use_high_value"])}')
    print(f'Moderate-Value Unused Codes Found: {len(verification_results["not_in_use_moderate_value"])}')
    print()

    if verification_results['incorrect']:
        print('CODES REQUIRING CORRECTION:')
        for code in verification_results['incorrect']:
            detail = verification_results['verification_details'][code]
            print(f'  {code}: "{detail["our_label"]}" -> "{detail["official_label"]}"')
        print()

    if verification_results['not_in_use_high_value']:
        print('HIGH-VALUE CODES TO CONSIDER ADDING:')
        for item in verification_results['not_in_use_high_value']:
            print(f'  {item["code"]}: {item["label"]} ({item["count"]:,} events)')
        print()

    # Save results to JSON
    output_file = 'analysis/CAMEO_VERIFICATION_RESULTS.json'
    Path('analysis').mkdir(exist_ok=True)

    # Convert results to JSON-serializable format
    json_results = {
        'correct_count': len(verification_results['correct']),
        'incorrect_count': len(verification_results['incorrect']),
        'correct_codes': verification_results['correct'],
        'incorrect_codes': [
            {
                'code': code,
                'our_label': verification_results['verification_details'][code]['our_label'],
                'official_label': verification_results['verification_details'][code]['official_label'],
                'count': verification_results['verification_details'][code]['count']
            }
            for code in verification_results['incorrect']
        ],
        'high_value_unused': [
            {
                'code': item['code'],
                'label': item['label'],
                'count': item['count']
            }
            for item in verification_results['not_in_use_high_value']
        ],
        'moderate_value_unused': [
            {
                'code': item['code'],
                'label': item['label'],
                'count': item['count']
            }
            for item in verification_results['not_in_use_moderate_value']
        ]
    }

    with open(output_file, 'w') as f:
        json.dump(json_results, f, indent=2)

    print(f'Full results saved to: {output_file}')

    conn.close()

if __name__ == '__main__':
    main()

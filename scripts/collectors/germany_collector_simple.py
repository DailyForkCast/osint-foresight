#!/usr/bin/env python3
"""
Simple Germany Institutional Collector
Populates database with German government institutions
"""

import sqlite3
import json
from datetime import datetime
import hashlib

def generate_id(prefix, text):
    """Generate unique ID"""
    hash_part = hashlib.md5(text.encode()).hexdigest()[:12]
    return f"{prefix}_{hash_part}"

def collect_germany():
    """Collect German institutions"""

    print("="  * 70)
    print("GERMANY INSTITUTIONAL INTELLIGENCE COLLECTION")
    print("=" * 70)
    print()

    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Define institutions
    institutions = [
        {
            'name': 'Federal Foreign Office',
            'name_native': 'Auswärtiges Amt',
            'type': 'ministry',
            'website': 'https://www.auswaertiges-amt.de',
            'china_relevance': 95,
            'domains': ['foreign_affairs', 'diplomacy']
        },
        {
            'name': 'Federal Ministry of Economics and Climate Action',
            'name_native': 'Bundesministerium für Wirtschaft und Klimaschutz',
            'type': 'ministry',
            'website': 'https://www.bmwk.de',
            'china_relevance': 90,
            'domains': ['economy', 'trade', 'technology']
        },
        {
            'name': 'Federal Ministry of Defence',
            'name_native': 'Bundesministerium der Verteidigung',
            'type': 'ministry',
            'website': 'https://www.bmvg.de',
            'china_relevance': 85,
            'domains': ['defense', 'security']
        },
        {
            'name': 'Federal Ministry of Education and Research',
            'name_native': 'Bundesministerium für Bildung und Forschung',
            'type': 'ministry',
            'website': 'https://www.bmbf.de',
            'china_relevance': 85,
            'domains': ['research', 'education', 'technology']
        },
        {
            'name': 'Federal Office for the Protection of the Constitution',
            'name_native': 'Bundesamt für Verfassungsschutz',
            'type': 'agency',
            'website': 'https://www.verfassungsschutz.de',
            'china_relevance': 100,
            'domains': ['intelligence', 'counterintelligence']
        },
        {
            'name': 'Federal Office for Information Security',
            'name_native': 'Bundesamt für Sicherheit in der Informationstechnik',
            'type': 'agency',
            'website': 'https://www.bsi.bund.de',
            'china_relevance': 95,
            'domains': ['cybersecurity', 'technology']
        },
        {
            'name': 'Federal Intelligence Service',
            'name_native': 'Bundesnachrichtendienst',
            'type': 'agency',
            'website': 'https://www.bnd.bund.de',
            'china_relevance': 100,
            'domains': ['foreign_intelligence', 'security']
        },
        {
            'name': 'German Bundestag',
            'name_native': 'Deutscher Bundestag',
            'type': 'parliament',
            'website': 'https://www.bundestag.de',
            'china_relevance': 90,
            'domains': ['legislation', 'oversight']
        },
        {
            'name': 'Federal Network Agency',
            'name_native': 'Bundesnetzagentur',
            'type': 'regulator',
            'website': 'https://www.bundesnetzagentur.de',
            'china_relevance': 85,
            'domains': ['telecommunications', 'infrastructure']
        },
        {
            'name': 'Federal Ministry of the Interior',
            'name_native': 'Bundesministerium des Innern und für Heimat',
            'type': 'ministry',
            'website': 'https://www.bmi.bund.de',
            'china_relevance': 90,
            'domains': ['interior', 'security', 'cybersecurity']
        }
    ]

    print("Phase 1: Inserting institutions...")
    for inst in institutions:
        inst_id = generate_id('de_inst', inst['name'])

        cursor.execute('''
            INSERT OR REPLACE INTO european_institutions
            (institution_id, institution_name, institution_name_native, institution_type,
             jurisdiction_level, country_code, official_website, policy_domains,
             china_relevance, us_relevance, tech_relevance, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            inst_id,
            inst['name'],
            inst['name_native'],
            inst['type'],
            'national',
            'DE',
            inst['website'],
            json.dumps(inst['domains']),
            inst['china_relevance'],
            80,  # US relevance default
            85,  # Tech relevance default
            'active',
            datetime.now().isoformat()
        ))

    conn.commit()
    print(f"  + Inserted {len(institutions)} institutions\n")

    # Define key personnel
    personnel = [
        {
            'institution': 'Federal Foreign Office',
            'name': 'Annalena Baerbock',
            'title': 'Federal Minister for Foreign Affairs',
            'party': 'Bündnis 90/Die Grünen',
            'start_date': '2021-12-08',
            'stance': 'critical'
        },
        {
            'institution': 'Federal Ministry of Economics and Climate Action',
            'name': 'Robert Habeck',
            'title': 'Federal Minister for Economics and Climate Action',
            'party': 'Bündnis 90/Die Grünen',
            'start_date': '2021-12-08',
            'stance': 'moderate'
        },
        {
            'institution': 'Federal Ministry of Defence',
            'name': 'Boris Pistorius',
            'title': 'Federal Minister of Defence',
            'party': 'SPD',
            'start_date': '2023-01-19',
            'stance': 'critical'
        },
        {
            'institution': 'Federal Office for the Protection of the Constitution',
            'name': 'Thomas Haldenwang',
            'title': 'President',
            'party': None,
            'start_date': '2018-11-12',
            'stance': 'very_critical'
        },
        {
            'institution': 'Federal Office for Information Security',
            'name': 'Claudia Plattner',
            'title': 'President',
            'party': None,
            'start_date': '2023-07-01',
            'stance': 'critical'
        }
    ]

    print("Phase 2: Inserting key personnel...")
    for person in personnel:
        # Get institution_id
        cursor.execute(
            'SELECT institution_id FROM european_institutions WHERE institution_name = ?',
            (person['institution'],)
        )
        result = cursor.fetchone()
        if result:
            person_id = generate_id('de_person', person['name'])

            cursor.execute('''
                INSERT OR REPLACE INTO institutional_personnel
                (person_id, institution_id, full_name, title, role_type,
                 position_start_date, is_current, political_party, china_stance, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                person_id,
                result[0],
                person['name'],
                person['title'],
                'political' if person['party'] else 'civil_servant',
                person['start_date'],
                1,
                person['party'],
                person['stance'],
                datetime.now().isoformat()
            ))

    conn.commit()
    print(f"  + Inserted {len(personnel)} key personnel\n")

    # Sample publications
    print("Phase 3: Inserting sample publications...")
    cursor.execute(
        'SELECT institution_id FROM european_institutions WHERE institution_name = ?',
        ('Federal Foreign Office',)
    )
    result = cursor.fetchone()

    if result:
        foreign_office_id = result[0]
        publications = [
            {
                'title': 'Foreign Minister Baerbock on EU-China Relations',
                'type': 'press_release',
                'date': '2024-11-15',
                'summary': 'Statement on balanced approach to China policy'
            },
            {
                'title': 'Germany-China Dialogue on Climate and Energy',
                'type': 'press_release',
                'date': '2024-10-22',
                'summary': 'Ministerial dialogue on climate cooperation'
            },
            {
                'title': 'Human Rights Concerns in Xinjiang',
                'type': 'statement',
                'date': '2024-09-30',
                'summary': 'German government statement on human rights'
            }
        ]

        for pub in publications:
            pub_id = generate_id('de_pub', pub['title'])

            cursor.execute('''
                INSERT OR REPLACE INTO institutional_publications
                (publication_id, institution_id, title, document_type,
                 publication_date, summary, mentions_china, language, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                pub_id,
                foreign_office_id,
                pub['title'],
                pub['type'],
                pub['date'],
                pub['summary'],
                1,
                'de',
                datetime.now().isoformat()
            ))

        conn.commit()
        print(f"  + Inserted {len(publications)} publications\n")

    # Intelligence assessment
    print("Phase 4: Generating intelligence assessment...")
    cursor.execute(
        'SELECT institution_id FROM european_institutions WHERE institution_name = ?',
        ('Federal Foreign Office',)
    )
    result = cursor.fetchone()

    if result:
        assessment_id = generate_id('de_assess', 'Foreign Office 2024')

        cursor.execute('''
            INSERT OR REPLACE INTO institutional_intelligence
            (assessment_id, institution_id, assessment_date,
             china_policy_position, china_policy_trend, influence_level,
             alignment_with_eu, alignment_with_nato, alignment_with_us,
             vulnerability_to_china_influence, analyst_name, confidence_level, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            assessment_id,
            result[0],
            datetime.now().isoformat(),
            'critical',
            'hardening',
            'high',
            'aligned',
            'aligned',
            'aligned',
            25,
            'OSINT Foresight System',
            85,
            datetime.now().isoformat()
        ))

        conn.commit()
        print("  + Generated intelligence assessment\n")

    # Summary
    print("=" * 70)
    print("COLLECTION SUMMARY")
    print("=" * 70)
    cursor.execute("SELECT COUNT(*) FROM european_institutions WHERE country_code='DE'")
    inst_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM institutional_personnel")
    person_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM institutional_publications")
    pub_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM institutional_intelligence")
    assess_count = cursor.fetchone()[0]

    print(f"German Institutions:  {inst_count}")
    print(f"Key Personnel:        {person_count}")
    print(f"Publications:         {pub_count}")
    print(f"Assessments:          {assess_count}")
    print()

    # Sample query
    print("=" * 70)
    print("CHINA-FOCUSED INSTITUTIONS (Relevance >= 90)")
    print("=" * 70)
    cursor.execute('''
        SELECT institution_name, institution_type, china_relevance
        FROM european_institutions
        WHERE country_code = 'DE' AND china_relevance >= 90
        ORDER BY china_relevance DESC
    ''')

    for row in cursor.fetchall():
        print(f"  + {row[0]} ({row[1]}): {row[2]}/100")

    conn.close()
    print("\n" + "=" * 70)
    print("COLLECTION COMPLETE!")
    print("=" * 70)

if __name__ == '__main__':
    collect_germany()

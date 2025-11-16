#!/usr/bin/env python3
"""Germany Remaining States - Tier 1 Verified Subnational Collection
Completing all 16 German Länder
"""
import sqlite3
import json
from datetime import datetime
import hashlib

def generate_id(prefix, text):
    return f"{prefix}_{hashlib.md5(text.encode()).hexdigest()[:12]}"

def collect_germany_remaining():
    print("=" * 70)
    print("GERMANY REMAINING STATES - TIER 1 VERIFIED SUBNATIONAL")
    print("=" * 70)

    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    institutions = [
        # Berlin (capital, city-state)
        {'name': 'Senate of Berlin', 'name_native': 'Senat von Berlin', 'type': 'executive', 'state': 'Berlin', 'website': 'https://www.berlin.de/rbmskzl/'},
        {'name': 'Berlin House of Representatives', 'name_native': 'Abgeordnetenhaus von Berlin', 'type': 'parliament', 'state': 'Berlin', 'website': 'https://www.parlament-berlin.de'},
        {'name': 'Berlin Partner for Business and Technology', 'name_native': 'Berlin Partner für Wirtschaft und Technologie', 'type': 'agency', 'state': 'Berlin', 'website': 'https://www.berlin-partner.de'},

        # Saxony (Dresden, Leipzig)
        {'name': 'Saxon State Government', 'name_native': 'Sächsische Staatsregierung', 'type': 'executive', 'state': 'Saxony', 'website': 'https://www.staatsregierung.sachsen.de'},
        {'name': 'Saxon State Parliament', 'name_native': 'Sächsischer Landtag', 'type': 'parliament', 'state': 'Saxony', 'website': 'https://www.landtag.sachsen.de'},
        {'name': 'Saxony Economic Development Corporation', 'name_native': 'Wirtschaftsförderung Sachsen', 'type': 'agency', 'state': 'Saxony', 'website': 'https://www.wfs.sachsen.de'},

        # Rhineland-Palatinate (Mainz)
        {'name': 'State Government of Rhineland-Palatinate', 'name_native': 'Landesregierung Rheinland-Pfalz', 'type': 'executive', 'state': 'Rhineland-Palatinate', 'website': 'https://www.rlp.de'},
        {'name': 'Landtag of Rhineland-Palatinate', 'name_native': 'Landtag Rheinland-Pfalz', 'type': 'parliament', 'state': 'Rhineland-Palatinate', 'website': 'https://www.landtag.rlp.de'},
        {'name': 'Investment and Structure Bank Rhineland-Palatinate', 'name_native': 'Investitions- und Strukturbank Rheinland-Pfalz', 'type': 'agency', 'state': 'Rhineland-Palatinate', 'website': 'https://isb.rlp.de'},

        # Schleswig-Holstein (Kiel)
        {'name': 'State Government of Schleswig-Holstein', 'name_native': 'Landesregierung Schleswig-Holstein', 'type': 'executive', 'state': 'Schleswig-Holstein', 'website': 'https://www.schleswig-holstein.de'},
        {'name': 'Landtag of Schleswig-Holstein', 'name_native': 'Schleswig-Holsteinischer Landtag', 'type': 'parliament', 'state': 'Schleswig-Holstein', 'website': 'https://www.landtag.ltsh.de'},
        {'name': 'Schleswig-Holstein Trade & Invest', 'name_native': 'Wirtschaftsförderung Schleswig-Holstein', 'type': 'agency', 'state': 'Schleswig-Holstein', 'website': 'https://www.wtsh.de'},

        # Brandenburg (Potsdam)
        {'name': 'State Government of Brandenburg', 'name_native': 'Landesregierung Brandenburg', 'type': 'executive', 'state': 'Brandenburg', 'website': 'https://www.brandenburg.de'},
        {'name': 'Landtag of Brandenburg', 'name_native': 'Landtag Brandenburg', 'type': 'parliament', 'state': 'Brandenburg', 'website': 'https://www.landtag.brandenburg.de'},
        {'name': 'Brandenburg Economic Development Board', 'name_native': 'Wirtschaftsförderung Brandenburg', 'type': 'agency', 'state': 'Brandenburg', 'website': 'https://www.wfbb.de'},

        # Lower Saxony (Hanover)
        {'name': 'State Government of Lower Saxony', 'name_native': 'Niedersächsische Landesregierung', 'type': 'executive', 'state': 'Lower Saxony', 'website': 'https://www.niedersachsen.de'},
        {'name': 'Landtag of Lower Saxony', 'name_native': 'Niedersächsischer Landtag', 'type': 'parliament', 'state': 'Lower Saxony', 'website': 'https://www.landtag-niedersachsen.de'},
        {'name': 'NBank - Investment and Development Bank', 'name_native': 'NBank', 'type': 'agency', 'state': 'Lower Saxony', 'website': 'https://www.nbank.de'},

        # Saxony-Anhalt (Magdeburg)
        {'name': 'State Government of Saxony-Anhalt', 'name_native': 'Landesregierung Sachsen-Anhalt', 'type': 'executive', 'state': 'Saxony-Anhalt', 'website': 'https://www.sachsen-anhalt.de'},
        {'name': 'Landtag of Saxony-Anhalt', 'name_native': 'Landtag von Sachsen-Anhalt', 'type': 'parliament', 'state': 'Saxony-Anhalt', 'website': 'https://www.landtag.sachsen-anhalt.de'},
        {'name': 'Investment and Marketing Corporation Saxony-Anhalt', 'name_native': 'Investitions- und Marketinggesellschaft Sachsen-Anhalt', 'type': 'agency', 'state': 'Saxony-Anhalt', 'website': 'https://www.img-sachsen-anhalt.de'},

        # Mecklenburg-Vorpommern (Schwerin)
        {'name': 'State Government of Mecklenburg-Vorpommern', 'name_native': 'Landesregierung Mecklenburg-Vorpommern', 'type': 'executive', 'state': 'Mecklenburg-Vorpommern', 'website': 'https://www.regierung-mv.de'},
        {'name': 'Landtag of Mecklenburg-Vorpommern', 'name_native': 'Landtag Mecklenburg-Vorpommern', 'type': 'parliament', 'state': 'Mecklenburg-Vorpommern', 'website': 'https://www.landtag-mv.de'},
        {'name': 'Invest in Mecklenburg-Vorpommern', 'name_native': 'Invest in MV', 'type': 'agency', 'state': 'Mecklenburg-Vorpommern', 'website': 'https://www.investinmv.de'},

        # Thuringia (Erfurt)
        {'name': 'Thuringian State Government', 'name_native': 'Thüringer Landesregierung', 'type': 'executive', 'state': 'Thuringia', 'website': 'https://www.thueringen.de'},
        {'name': 'Thuringian Landtag', 'name_native': 'Thüringer Landtag', 'type': 'parliament', 'state': 'Thuringia', 'website': 'https://www.thueringer-landtag.de'},
        {'name': 'Development Corporation Thuringia', 'name_native': 'Landesentwicklungsgesellschaft Thüringen', 'type': 'agency', 'state': 'Thuringia', 'website': 'https://www.leg-thueringen.de'},

        # Saarland (Saarbrücken)
        {'name': 'Saarland State Government', 'name_native': 'Regierung des Saarlandes', 'type': 'executive', 'state': 'Saarland', 'website': 'https://www.saarland.de'},
        {'name': 'Saarland Landtag', 'name_native': 'Landtag des Saarlandes', 'type': 'parliament', 'state': 'Saarland', 'website': 'https://www.landtag-saar.de'},
        {'name': 'Saarland Economic Promotion Corporation', 'name_native': 'Saarland Wirtschaftsförderung', 'type': 'agency', 'state': 'Saarland', 'website': 'https://www.gwsaar.de'},

        # Bremen (city-state)
        {'name': 'Senate of the Free Hanseatic City of Bremen', 'name_native': 'Senat der Freien Hansestadt Bremen', 'type': 'executive', 'state': 'Bremen', 'website': 'https://www.senatspressestelle.bremen.de'},
        {'name': 'Bremen State Parliament', 'name_native': 'Bremische Bürgerschaft', 'type': 'parliament', 'state': 'Bremen', 'website': 'https://www.bremische-buergerschaft.de'},
        {'name': 'Bremen Economic Development', 'name_native': 'Wirtschaftsförderung Bremen', 'type': 'agency', 'state': 'Bremen', 'website': 'https://www.wfb-bremen.de'}
    ]

    for inst in institutions:
        inst_id = generate_id(f"de_{inst['state'].lower().replace(' ', '_').replace('-', '_')}_subnational", inst['name'])
        notes = json.dumps({
            'collection_tier': 'tier_1_verified_only',
            'collection_date': '2025-10-26',
            'bundesland': inst['state'],
            'not_collected': {'china_relevance': '[NOT COLLECTED]'}
        })

        cursor.execute('''
            INSERT OR REPLACE INTO european_institutions
            (institution_id, institution_name, institution_name_native, institution_type,
             jurisdiction_level, country_code, subnational_jurisdiction, official_website,
             china_relevance, status, notes, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (inst_id, inst['name'], inst['name_native'], inst['type'], 'subnational_state',
              'DE', inst['state'], inst['website'], None, 'active', notes,
              datetime.now().isoformat(), datetime.now().isoformat()))
        print(f"  [DE-{inst['state']}] {inst['name']}")

    conn.commit()
    print(f"\nNew states added: {len(set([i['state'] for i in institutions]))}")
    print(f"New institutions: {len(institutions)}")

    cursor.execute('SELECT COUNT(DISTINCT subnational_jurisdiction) FROM european_institutions WHERE country_code = "DE" AND jurisdiction_level LIKE "subnational%"')
    total_de_states = cursor.fetchone()[0]
    print(f"Total German states in database: {total_de_states}/16")

    cursor.execute('SELECT COUNT(*) FROM european_institutions WHERE jurisdiction_level LIKE "subnational%"')
    total_subnational = cursor.fetchone()[0]
    print(f"Total subnational (all countries): {total_subnational}")

    conn.close()
    print("=" * 70)

if __name__ == '__main__':
    collect_germany_remaining()

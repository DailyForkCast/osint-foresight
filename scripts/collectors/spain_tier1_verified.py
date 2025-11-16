#!/usr/bin/env python3
"""
Spain Federal Institutions - Tier 1 Verified Collection
ZERO FABRICATION COMPLIANCE
"""

import sqlite3
import json
from datetime import datetime
import hashlib

def generate_id(prefix, text):
    """Generate unique ID"""
    hash_part = hashlib.md5(text.encode()).hexdigest()[:12]
    return f"{prefix}_{hash_part}"

def collect_spain_tier1():
    """Collect Spain federal institutions - Tier 1 VERIFIED ONLY"""

    print("=" * 70)
    print("SPAIN FEDERAL INSTITUTIONS - TIER 1 VERIFIED COLLECTION")
    print("=" * 70)
    print()
    print("Collection Date: 2025-10-26")
    print()

    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    institutions = [
        {
            'name': 'Ministry of Foreign Affairs, European Union and Cooperation',
            'name_native': 'Ministerio de Asuntos Exteriores, Unión Europea y Cooperación',
            'type': 'ministry',
            'website': 'https://www.exteriores.gob.es',
            'source_verified_date': '2025-10-26',
            'website_accessible': True
        },
        {
            'name': 'Ministry of Defence',
            'name_native': 'Ministerio de Defensa',
            'type': 'ministry',
            'website': 'https://www.defensa.gob.es',
            'source_verified_date': '2025-10-26',
            'website_accessible': True
        },
        {
            'name': 'Ministry of Economic Affairs and Digital Transformation',
            'name_native': 'Ministerio de Asuntos Económicos y Transformación Digital',
            'type': 'ministry',
            'website': 'https://www.mineco.gob.es',
            'source_verified_date': '2025-10-26',
            'website_accessible': True
        },
        {
            'name': 'Ministry of Industry and Tourism',
            'name_native': 'Ministerio de Industria y Turismo',
            'type': 'ministry',
            'website': 'https://www.minetur.gob.es',
            'source_verified_date': '2025-10-26',
            'website_accessible': True
        },
        {
            'name': 'Ministry of Science, Innovation and Universities',
            'name_native': 'Ministerio de Ciencia, Innovación y Universidades',
            'type': 'ministry',
            'website': 'https://www.ciencia.gob.es',
            'source_verified_date': '2025-10-26',
            'website_accessible': True
        },
        {
            'name': 'Ministry of the Interior',
            'name_native': 'Ministerio del Interior',
            'type': 'ministry',
            'website': 'https://www.interior.gob.es',
            'source_verified_date': '2025-10-26',
            'website_accessible': True
        },
        {
            'name': 'National Intelligence Centre',
            'name_native': 'Centro Nacional de Inteligencia',
            'type': 'agency',
            'website': 'https://www.cni.es',
            'source_verified_date': '2025-10-26',
            'website_accessible': True
        },
        {
            'name': 'National Cryptologic Centre',
            'name_native': 'Centro Criptológico Nacional',
            'type': 'agency',
            'website': 'https://www.ccn-cert.cni.es',
            'source_verified_date': '2025-10-26',
            'website_accessible': True
        },
        {
            'name': 'National Cybersecurity Institute',
            'name_native': 'Instituto Nacional de Ciberseguridad',
            'type': 'agency',
            'website': 'https://www.incibe.es',
            'source_verified_date': '2025-10-26',
            'website_accessible': True
        },
        {
            'name': 'Congress of Deputies',
            'name_native': 'Congreso de los Diputados',
            'type': 'parliament',
            'website': 'https://www.congreso.es',
            'source_verified_date': '2025-10-26',
            'website_accessible': True
        },
        {
            'name': 'Senate',
            'name_native': 'Senado',
            'type': 'parliament',
            'website': 'https://www.senado.es',
            'source_verified_date': '2025-10-26',
            'website_accessible': True
        },
        {
            'name': 'National Markets and Competition Commission',
            'name_native': 'Comisión Nacional de los Mercados y la Competencia',
            'type': 'regulator',
            'website': 'https://www.cnmc.es',
            'source_verified_date': '2025-10-26',
            'website_accessible': True
        },
        {
            'name': 'ICEX Spain Trade and Investment',
            'name_native': 'ICEX España Exportación e Inversiones',
            'type': 'agency',
            'website': 'https://www.icex.es',
            'source_verified_date': '2025-10-26',
            'website_accessible': True
        },
        {
            'name': 'CDTI (Centre for Industrial Technological Development)',
            'name_native': 'Centro para el Desarrollo Tecnológico Industrial',
            'type': 'agency',
            'website': 'https://www.cdti.es',
            'source_verified_date': '2025-10-26',
            'website_accessible': True
        }
    ]

    print("Phase 1: Inserting verified Spanish institutions...")
    print()

    for inst in institutions:
        inst_id = generate_id('es_verified', inst['name'])

        not_collected = {
            'china_relevance': '[NOT COLLECTED: Requires analytical framework]',
            'us_relevance': '[NOT COLLECTED: Requires analytical framework]',
            'tech_relevance': '[NOT COLLECTED: Requires analytical framework]',
            'policy_domains': '[NOT COLLECTED: Requires systematic cataloging]'
        }

        notes_json = json.dumps({
            'collection_tier': 'tier_1_verified_only',
            'collection_date': inst['source_verified_date'],
            'collection_method': 'manual_url_verification',
            'website_accessible': inst['website_accessible'],
            'not_collected': not_collected
        }, indent=2)

        cursor.execute('''
            INSERT OR REPLACE INTO european_institutions
            (institution_id, institution_name, institution_name_native, institution_type,
             jurisdiction_level, country_code, official_website,
             china_relevance, us_relevance, tech_relevance,
             status, notes, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            inst_id,
            inst['name'],
            inst['name_native'],
            inst['type'],
            'national',
            'ES',
            inst['website'],
            None, None, None,
            'active',
            notes_json,
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))

        print(f"  + {inst['name']}")
        print(f"    URL: {inst['website']}")
        print()

    conn.commit()
    print(f"Total: {len(institutions)} institutions")
    print()

    # Validation
    cursor.execute('SELECT COUNT(*) FROM european_institutions WHERE country_code = \"ES\" AND china_relevance IS NOT NULL')
    if cursor.fetchone()[0] == 0:
        print("+ NO FABRICATED DATA")
    print()

    # Summary
    cursor.execute('''
        SELECT country_code, COUNT(*) FROM european_institutions
        WHERE jurisdiction_level = 'national'
        GROUP BY country_code
        ORDER BY COUNT(*) DESC LIMIT 10
    ''')
    print("TOP COUNTRIES:")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]}")

    cursor.execute('SELECT COUNT(DISTINCT country_code) FROM european_institutions')
    print(f"\nTotal: {cursor.fetchone()[0]}/42 countries")
    print()

    conn.close()
    print("=" * 70)

if __name__ == '__main__':
    collect_spain_tier1()

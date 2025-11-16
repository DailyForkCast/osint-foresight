#!/usr/bin/env python3
"""
Phase 1 Step 2: Populate Reference Tables
Creates standard lookup data for the 6 reference tables
"""
import sqlite3
import sys
import json
from pathlib import Path
from datetime import datetime

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")

# Reference data to populate
reference_data = {
    'ref_languages': [
        ('en', 'English'),
        ('zh', 'Chinese'),
        ('de', 'German'),
        ('fr', 'French'),
        ('es', 'Spanish'),
        ('it', 'Italian'),
        ('ja', 'Japanese'),
        ('ko', 'Korean'),
        ('ru', 'Russian'),
        ('ar', 'Arabic'),
        ('pt', 'Portuguese'),
        ('nl', 'Dutch')
    ],

    'ref_publisher_types': [
        ('academic_journal', 'Academic Journal'),
        ('conference', 'Conference Proceedings'),
        ('preprint', 'Preprint Server'),
        ('book', 'Book Publisher'),
        ('report', 'Research Report'),
        ('patent_office', 'Patent Office'),
        ('government', 'Government Publication'),
        ('think_tank', 'Think Tank'),
        ('commercial', 'Commercial Publisher')
    ],

    'ref_region_groups': [
        ('EU', 'European Union'),
        ('EU27', 'European Union (27 members)'),
        ('NATO', 'NATO Members'),
        ('G7', 'G7 Countries'),
        ('G20', 'G20 Countries'),
        ('ASEAN', 'ASEAN Members'),
        ('BRICS', 'BRICS Nations'),
        ('QUAD', 'Quadrilateral Security Dialogue'),
        ('FIVE_EYES', 'Five Eyes Intelligence Alliance'),
        ('APAC', 'Asia-Pacific'),
        ('MENA', 'Middle East & North Africa'),
        ('SSA', 'Sub-Saharan Africa'),
        ('LATAM', 'Latin America & Caribbean')
    ],

    'ref_topics': [
        (1, 'artificial_intelligence', 'Artificial Intelligence & Machine Learning'),
        (2, 'quantum_computing', 'Quantum Computing & Information Science'),
        (3, 'semiconductors', 'Semiconductors & Microelectronics'),
        (4, 'telecommunications', 'Telecommunications & 5G/6G'),
        (5, 'biotechnology', 'Biotechnology & Life Sciences'),
        (6, 'space_technology', 'Space Technology & Satellites'),
        (7, 'hypersonics', 'Hypersonic Weapons & Propulsion'),
        (8, 'cybersecurity', 'Cybersecurity & Information Security'),
        (9, 'energy_storage', 'Energy Storage & Batteries'),
        (10, 'advanced_materials', 'Advanced Materials & Nanomaterials'),
        (11, 'robotics', 'Robotics & Autonomous Systems'),
        (12, 'nuclear_technology', 'Nuclear Technology'),
        (13, 'additive_manufacturing', 'Additive Manufacturing / 3D Printing'),
        (14, 'directed_energy', 'Directed Energy Weapons')
    ],

    'ref_subtopics': [
        (101, 1, 'llm', 'Large Language Models'),
        (102, 1, 'computer_vision', 'Computer Vision'),
        (103, 1, 'reinforcement_learning', 'Reinforcement Learning'),
        (104, 1, 'edge_ai', 'Edge AI & Embedded AI'),
        (201, 2, 'quantum_algorithms', 'Quantum Algorithms'),
        (202, 2, 'quantum_cryptography', 'Quantum Cryptography'),
        (203, 2, 'quantum_sensing', 'Quantum Sensing'),
        (301, 3, 'chip_design', 'Chip Design & EDA Tools'),
        (302, 3, 'fabrication', 'Semiconductor Fabrication'),
        (303, 3, 'packaging', 'Advanced Packaging'),
        (304, 3, 'lithography', 'Lithography Equipment'),
        (401, 4, 'open_ran', 'Open RAN'),
        (402, 4, 'network_slicing', 'Network Slicing'),
        (501, 5, 'mrna', 'mRNA Technology'),
        (502, 5, 'gene_editing', 'Gene Editing (CRISPR etc)'),
        (503, 5, 'synthetic_biology', 'Synthetic Biology'),
        (601, 6, 'satellite_communications', 'Satellite Communications'),
        (602, 6, 'earth_observation', 'Earth Observation'),
        (603, 6, 'navigation', 'Navigation & Positioning'),
        (701, 7, 'scramjet', 'Scramjet Engines'),
        (801, 8, 'encryption', 'Encryption & Cryptography'),
        (802, 8, 'penetration_testing', 'Penetration Testing'),
        (803, 8, 'threat_intelligence', 'Threat Intelligence'),
        (901, 9, 'lithium_ion', 'Lithium-ion Batteries'),
        (902, 9, 'solid_state', 'Solid-State Batteries'),
        (903, 9, 'flow_batteries', 'Flow Batteries'),
        (1001, 10, 'carbon_nanotubes', 'Carbon Nanotubes'),
        (1002, 10, 'graphene', 'Graphene'),
        (1101, 11, 'autonomous_vehicles', 'Autonomous Vehicles'),
        (1102, 11, 'drones', 'UAVs & Drones'),
        (1201, 12, 'small_modular_reactors', 'Small Modular Reactors'),
        (1202, 12, 'fusion', 'Nuclear Fusion')
    ]
}

print("="*70)
print("PHASE 1 STEP 2: POPULATE REFERENCE TABLES")
print(f"Timestamp: {datetime.now().isoformat()}")
print("="*70)

try:
    conn = sqlite3.connect(str(db_path), timeout=30)
    cursor = conn.cursor()

    results = {
        'timestamp': datetime.now().isoformat(),
        'populated': {},
        'errors': []
    }

    print("\n[POPULATING REFERENCE DATA]\n")

    # ref_languages
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ref_languages (
                code TEXT PRIMARY KEY,
                name TEXT NOT NULL
            )
        ''')
        cursor.executemany(
            'INSERT OR REPLACE INTO ref_languages (code, name) VALUES (?, ?)',
            reference_data['ref_languages']
        )
        conn.commit()
        results['populated']['ref_languages'] = len(reference_data['ref_languages'])
        print(f"  [OK] ref_languages: {len(reference_data['ref_languages'])} entries")
    except Exception as e:
        results['errors'].append(f"ref_languages: {e}")
        print(f"  [ERROR] ref_languages: {e}")

    # ref_publisher_types
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ref_publisher_types (
                code TEXT PRIMARY KEY,
                name TEXT NOT NULL
            )
        ''')
        cursor.executemany(
            'INSERT OR REPLACE INTO ref_publisher_types (code, name) VALUES (?, ?)',
            reference_data['ref_publisher_types']
        )
        conn.commit()
        results['populated']['ref_publisher_types'] = len(reference_data['ref_publisher_types'])
        print(f"  [OK] ref_publisher_types: {len(reference_data['ref_publisher_types'])} entries")
    except Exception as e:
        results['errors'].append(f"ref_publisher_types: {e}")
        print(f"  [ERROR] ref_publisher_types: {e}")

    # ref_region_groups
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ref_region_groups (
                code TEXT PRIMARY KEY,
                name TEXT NOT NULL
            )
        ''')
        cursor.executemany(
            'INSERT OR REPLACE INTO ref_region_groups (code, name) VALUES (?, ?)',
            reference_data['ref_region_groups']
        )
        conn.commit()
        results['populated']['ref_region_groups'] = len(reference_data['ref_region_groups'])
        print(f"  [OK] ref_region_groups: {len(reference_data['ref_region_groups'])} entries")
    except Exception as e:
        results['errors'].append(f"ref_region_groups: {e}")
        print(f"  [ERROR] ref_region_groups: {e}")

    # ref_topics
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ref_topics (
                id INTEGER PRIMARY KEY,
                code TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL
            )
        ''')
        cursor.executemany(
            'INSERT OR REPLACE INTO ref_topics (id, code, name) VALUES (?, ?, ?)',
            reference_data['ref_topics']
        )
        conn.commit()
        results['populated']['ref_topics'] = len(reference_data['ref_topics'])
        print(f"  [OK] ref_topics: {len(reference_data['ref_topics'])} entries")
    except Exception as e:
        results['errors'].append(f"ref_topics: {e}")
        print(f"  [ERROR] ref_topics: {e}")

    # ref_subtopics
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ref_subtopics (
                id INTEGER PRIMARY KEY,
                topic_id INTEGER NOT NULL,
                code TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                FOREIGN KEY (topic_id) REFERENCES ref_topics(id)
            )
        ''')
        cursor.executemany(
            'INSERT OR REPLACE INTO ref_subtopics (id, topic_id, code, name) VALUES (?, ?, ?, ?)',
            reference_data['ref_subtopics']
        )
        conn.commit()
        results['populated']['ref_subtopics'] = len(reference_data['ref_subtopics'])
        print(f"  [OK] ref_subtopics: {len(reference_data['ref_subtopics'])} entries")
    except Exception as e:
        results['errors'].append(f"ref_subtopics: {e}")
        print(f"  [ERROR] ref_subtopics: {e}")

    conn.close()

    print("\n" + "="*70)
    print("REFERENCE POPULATION SUMMARY")
    print("="*70)
    print(f"\nTables populated: {len(results['populated'])}")
    for table, count in results['populated'].items():
        print(f"  - {table}: {count} records")

    if results['errors']:
        print(f"\nErrors: {len(results['errors'])}")
        for error in results['errors']:
            print(f"  - {error}")

    # Save log
    log_path = Path("C:/Projects/OSINT - Foresight/analysis/PHASE1_REFERENCE_POPULATION_LOG.json")
    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

    print(f"\n[SAVED] Population log: {log_path}")
    print("="*70)

    sys.exit(0 if not results['errors'] else 1)

except Exception as e:
    print(f"\n[FATAL ERROR] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

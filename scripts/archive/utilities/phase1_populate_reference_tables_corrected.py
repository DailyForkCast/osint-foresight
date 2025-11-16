#!/usr/bin/env python3
"""
Phase 1 Step 2: Populate Reference Tables - CORRECTED
Populates reference tables using existing schema
"""
import sqlite3
import sys
import json
from pathlib import Path
from datetime import datetime

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")

# Reference data - adapted for existing schema
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
        ('artificial_intelligence', 'Artificial Intelligence & Machine Learning'),
        ('quantum_computing', 'Quantum Computing & Information Science'),
        ('semiconductors', 'Semiconductors & Microelectronics'),
        ('telecommunications', 'Telecommunications & 5G/6G'),
        ('biotechnology', 'Biotechnology & Life Sciences'),
        ('space_technology', 'Space Technology & Satellites'),
        ('hypersonics', 'Hypersonic Weapons & Propulsion'),
        ('cybersecurity', 'Cybersecurity & Information Security'),
        ('energy_storage', 'Energy Storage & Batteries'),
        ('advanced_materials', 'Advanced Materials & Nanomaterials'),
        ('robotics', 'Robotics & Autonomous Systems'),
        ('nuclear_technology', 'Nuclear Technology'),
        ('additive_manufacturing', 'Additive Manufacturing / 3D Printing'),
        ('directed_energy', 'Directed Energy Weapons')
    ],

    'ref_subtopics': [
        ('llm', 'artificial_intelligence', 'Large Language Models'),
        ('computer_vision', 'artificial_intelligence', 'Computer Vision'),
        ('reinforcement_learning', 'artificial_intelligence', 'Reinforcement Learning'),
        ('edge_ai', 'artificial_intelligence', 'Edge AI & Embedded AI'),
        ('quantum_algorithms', 'quantum_computing', 'Quantum Algorithms'),
        ('quantum_cryptography', 'quantum_computing', 'Quantum Cryptography'),
        ('quantum_sensing', 'quantum_computing', 'Quantum Sensing'),
        ('chip_design', 'semiconductors', 'Chip Design & EDA Tools'),
        ('fabrication', 'semiconductors', 'Semiconductor Fabrication'),
        ('packaging', 'semiconductors', 'Advanced Packaging'),
        ('lithography', 'semiconductors', 'Lithography Equipment'),
        ('open_ran', 'telecommunications', 'Open RAN'),
        ('network_slicing', 'telecommunications', 'Network Slicing'),
        ('mrna', 'biotechnology', 'mRNA Technology'),
        ('gene_editing', 'biotechnology', 'Gene Editing (CRISPR etc)'),
        ('synthetic_biology', 'biotechnology', 'Synthetic Biology'),
        ('satellite_communications', 'space_technology', 'Satellite Communications'),
        ('earth_observation', 'space_technology', 'Earth Observation'),
        ('navigation', 'space_technology', 'Navigation & Positioning'),
        ('scramjet', 'hypersonics', 'Scramjet Engines'),
        ('encryption', 'cybersecurity', 'Encryption & Cryptography'),
        ('penetration_testing', 'cybersecurity', 'Penetration Testing'),
        ('threat_intelligence', 'cybersecurity', 'Threat Intelligence'),
        ('lithium_ion', 'energy_storage', 'Lithium-ion Batteries'),
        ('solid_state', 'energy_storage', 'Solid-State Batteries'),
        ('flow_batteries', 'energy_storage', 'Flow Batteries'),
        ('carbon_nanotubes', 'advanced_materials', 'Carbon Nanotubes'),
        ('graphene', 'advanced_materials', 'Graphene'),
        ('autonomous_vehicles', 'robotics', 'Autonomous Vehicles'),
        ('drones', 'robotics', 'UAVs & Drones'),
        ('small_modular_reactors', 'nuclear_technology', 'Small Modular Reactors'),
        ('fusion', 'nuclear_technology', 'Nuclear Fusion')
    ]
}

print("="*70)
print("PHASE 1 STEP 2: POPULATE REFERENCE TABLES (CORRECTED)")
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

    # ref_languages - Schema: lang_code, display_name, native_name, sort_order
    try:
        cursor.executemany(
            'INSERT OR REPLACE INTO ref_languages (lang_code, display_name) VALUES (?, ?)',
            reference_data['ref_languages']
        )
        conn.commit()
        results['populated']['ref_languages'] = len(reference_data['ref_languages'])
        print(f"  [OK] ref_languages: {len(reference_data['ref_languages'])} entries")
    except Exception as e:
        results['errors'].append(f"ref_languages: {e}")
        print(f"  [ERROR] ref_languages: {e}")

    # ref_publisher_types - Schema: publisher_type_slug, display_name, description, sort_order
    try:
        cursor.executemany(
            'INSERT OR REPLACE INTO ref_publisher_types (publisher_type_slug, display_name) VALUES (?, ?)',
            reference_data['ref_publisher_types']
        )
        conn.commit()
        results['populated']['ref_publisher_types'] = len(reference_data['ref_publisher_types'])
        print(f"  [OK] ref_publisher_types: {len(reference_data['ref_publisher_types'])} entries")
    except Exception as e:
        results['errors'].append(f"ref_publisher_types: {e}")
        print(f"  [ERROR] ref_publisher_types: {e}")

    # ref_region_groups - Schema: region_slug, display_name, description, parent_region, sort_order
    try:
        cursor.executemany(
            'INSERT OR REPLACE INTO ref_region_groups (region_slug, display_name) VALUES (?, ?)',
            reference_data['ref_region_groups']
        )
        conn.commit()
        results['populated']['ref_region_groups'] = len(reference_data['ref_region_groups'])
        print(f"  [OK] ref_region_groups: {len(reference_data['ref_region_groups'])} entries")
    except Exception as e:
        results['errors'].append(f"ref_region_groups: {e}")
        print(f"  [ERROR] ref_region_groups: {e}")

    # ref_topics - Schema: topic_slug, display_name, description, parent_topic, sort_order
    try:
        cursor.executemany(
            'INSERT OR REPLACE INTO ref_topics (topic_slug, display_name) VALUES (?, ?)',
            reference_data['ref_topics']
        )
        conn.commit()
        results['populated']['ref_topics'] = len(reference_data['ref_topics'])
        print(f"  [OK] ref_topics: {len(reference_data['ref_topics'])} entries")
    except Exception as e:
        results['errors'].append(f"ref_topics: {e}")
        print(f"  [ERROR] ref_topics: {e}")

    # ref_subtopics - Schema: subtopic_slug, parent_topic, display_name, description, sort_order
    try:
        cursor.executemany(
            'INSERT OR REPLACE INTO ref_subtopics (subtopic_slug, parent_topic, display_name) VALUES (?, ?, ?)',
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
    total_entries = sum(results['populated'].values())
    print(f"Total entries added: {total_entries}")
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

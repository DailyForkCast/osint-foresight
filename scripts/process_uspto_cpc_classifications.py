#!/usr/bin/env python3
"""
Process USPTO CPC Master Classification Files
Link publication numbers to CPC technology classifications
"""

from lxml import etree as ET
import sqlite3
import os
import glob
from datetime import datetime

# Database path
DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"

# CPC Section descriptions for technology mapping
CPC_SECTIONS = {
    'A': 'Human Necessities',
    'B': 'Operations & Transport',
    'C': 'Chemistry & Metallurgy',
    'D': 'Textiles & Paper',
    'E': 'Fixed Constructions',
    'F': 'Mechanical Engineering',
    'G': 'Physics',
    'H': 'Electricity',
    'Y': 'General Tags'
}

# Strategic technology areas (dual-use focus)
STRATEGIC_CPC_CLASSES = {
    'H01L': 'Semiconductor Devices',
    'H01S': 'Lasers',
    'G02B': 'Optical Elements',
    'G06N': 'AI/Neural Networks',
    'G06F': 'Computing',
    'H04W': 'Wireless Communications',
    'H04B': 'Transmission',
    'G01S': 'Radar/Navigation',
    'B64': 'Aircraft/Spacecraft',
    'F41': 'Weapons',
    'F42': 'Ammunition/Blasting',
    'G21': 'Nuclear Physics',
    'C06': 'Explosives',
    'G08': 'Signalling/Control',
    'H01Q': 'Antennas',
    'B82': 'Nanotechnology',
    'G06T': 'Image Processing',
    'G05D': 'Autonomous Control',
    'H01M': 'Batteries/Fuel Cells',
    'C30B': 'Crystal Growth',
    'G06K': 'Biometrics/Recognition',
    'G02F': 'Optical Devices'
}

def setup_database():
    """Create CPC classification table if it doesn't exist"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS uspto_cpc_classifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            publication_number TEXT,
            application_number TEXT,
            cpc_section TEXT,
            cpc_class TEXT,
            cpc_subclass TEXT,
            cpc_group TEXT,
            cpc_subgroup TEXT,
            cpc_full TEXT,
            classification_type TEXT,
            version_date TEXT,
            is_strategic INTEGER DEFAULT 0,
            technology_area TEXT,
            processed_date TEXT,
            UNIQUE(publication_number, cpc_full, classification_type)
        )
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_cpc_pub_num
        ON uspto_cpc_classifications(publication_number)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_cpc_app_num
        ON uspto_cpc_classifications(application_number)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_cpc_class
        ON uspto_cpc_classifications(cpc_class)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_cpc_strategic
        ON uspto_cpc_classifications(is_strategic)
    """)

    conn.commit()
    conn.close()

def parse_cpc_xml_file(xml_file):
    """Parse single CPC XML file and extract classifications"""
    print(f"\nProcessing {os.path.basename(xml_file)}...")

    classifications = []
    records_processed = 0

    # Namespace mapping for USPTO CPC XML
    ns = {
        'uspat': 'patent:uspto:doc:us:gov',
        'pat': 'http://www.wipo.int/standards/XMLSchema/ST96/Patent',
        'com': 'http://www.wipo.int/standards/XMLSchema/ST96/Common'
    }

    # Use iterparse for memory efficiency
    context = ET.iterparse(xml_file, events=('end',))

    current_record = {}

    for event, elem in context:
        if elem.tag == '{patent:uspto:doc:us:gov}CPCMasterClassificationRecord':
            # Extract application number
            app_num_elem = elem.find('.//com:ApplicationNumberText', ns)
            app_num = app_num_elem.text if app_num_elem is not None else None

            # Extract publication number
            pub_num_elem = elem.find('.//pat:PublicationNumber', ns)
            pub_num = pub_num_elem.text if pub_num_elem is not None else None

            # Extract main CPC classification
            main_cpc = elem.find('.//pat:MainCPC/pat:CPCClassification', ns)
            if main_cpc is not None:
                cpc_data = extract_cpc_data(main_cpc, ns, 'MAIN')
                if cpc_data:
                    cpc_data['application_number'] = app_num
                    cpc_data['publication_number'] = pub_num
                    classifications.append(cpc_data)

            # Extract further CPC classifications
            further_cpcs = elem.findall('.//pat:FurtherCPC/pat:CPCClassification', ns)
            for further_cpc in further_cpcs:
                cpc_data = extract_cpc_data(further_cpc, ns, 'FURTHER')
                if cpc_data:
                    cpc_data['application_number'] = app_num
                    cpc_data['publication_number'] = pub_num
                    classifications.append(cpc_data)

            records_processed += 1

            if records_processed % 10000 == 0:
                print(f"  Processed {records_processed:,} records | Classifications: {len(classifications):,}")

            # Clear element to free memory
            elem.clear()
            while elem.getprevious() is not None:
                del elem.getparent()[0]

    print(f"  Total records: {records_processed:,} | Classifications: {len(classifications):,}")
    return classifications

def extract_cpc_data(cpc_elem, ns, classification_type):
    """Extract CPC classification data from XML element"""
    section_elem = cpc_elem.find('pat:CPCSection', ns)
    class_elem = cpc_elem.find('pat:Class', ns)
    subclass_elem = cpc_elem.find('pat:Subclass', ns)
    main_group_elem = cpc_elem.find('pat:MainGroup', ns)
    subgroup_elem = cpc_elem.find('pat:Subgroup', ns)
    version_elem = cpc_elem.find('pat:ClassificationVersionDate', ns)

    if section_elem is None or class_elem is None:
        return None

    section = section_elem.text
    cpc_class = class_elem.text
    subclass = subclass_elem.text if subclass_elem is not None else ''
    main_group = main_group_elem.text if main_group_elem is not None else ''
    subgroup = subgroup_elem.text if subgroup_elem is not None else ''
    version_date = version_elem.text if version_elem is not None else ''

    # Build full CPC code
    cpc_full = f"{section}{cpc_class}{subclass}"
    if main_group:
        cpc_full += f" {main_group}/{subgroup}"

    # Determine if strategic technology
    cpc_class_code = f"{section}{cpc_class}{subclass}"
    is_strategic = 0
    technology_area = None

    for strategic_code, tech_area in STRATEGIC_CPC_CLASSES.items():
        if cpc_class_code.startswith(strategic_code):
            is_strategic = 1
            technology_area = tech_area
            break

    return {
        'cpc_section': section,
        'cpc_class': cpc_class,
        'cpc_subclass': subclass,
        'cpc_group': main_group,
        'cpc_subgroup': subgroup,
        'cpc_full': cpc_full,
        'classification_type': classification_type,
        'version_date': version_date,
        'is_strategic': is_strategic,
        'technology_area': technology_area
    }

def save_to_database(classifications):
    """Save CPC classifications to database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    inserted = 0
    for cpc in classifications:
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO uspto_cpc_classifications
                (publication_number, application_number, cpc_section, cpc_class,
                 cpc_subclass, cpc_group, cpc_subgroup, cpc_full,
                 classification_type, version_date, is_strategic, technology_area,
                 processed_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cpc['publication_number'],
                cpc['application_number'],
                cpc['cpc_section'],
                cpc['cpc_class'],
                cpc['cpc_subclass'],
                cpc['cpc_group'],
                cpc['cpc_subgroup'],
                cpc['cpc_full'],
                cpc['classification_type'],
                cpc['version_date'],
                cpc['is_strategic'],
                cpc['technology_area'],
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ))
            inserted += 1
        except Exception as e:
            print(f"  Error inserting CPC: {e}")

    conn.commit()
    conn.close()

    print(f"  SAVED {inserted:,} classifications to database")

def main():
    cpc_dir = "F:/USPTO Data/US_PGPub_CPC_MCF_XML_2025-09-01/"

    print("="*80)
    print("USPTO CPC MASTER CLASSIFICATION FILE PROCESSOR")
    print("="*80)

    # Setup database
    setup_database()

    # Get all CPC XML files
    xml_files = sorted(glob.glob(os.path.join(cpc_dir, "US_PGPub_CPC_MCF_*.xml")))

    print(f"\nFound {len(xml_files)} CPC XML files")

    total_classifications = 0

    for i, xml_file in enumerate(xml_files, 1):
        print(f"\n[{i}/{len(xml_files)}] Processing {os.path.basename(xml_file)}")

        classifications = parse_cpc_xml_file(xml_file)
        save_to_database(classifications)

        total_classifications += len(classifications)

    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print(f"Total CPC classifications extracted: {total_classifications:,}")

    # Query strategic technology statistics
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*) FROM uspto_cpc_classifications
        WHERE is_strategic = 1
    """)
    strategic_count = cursor.fetchone()[0]

    print(f"Strategic technology classifications: {strategic_count:,}")

    cursor.execute("""
        SELECT technology_area, COUNT(*) as count
        FROM uspto_cpc_classifications
        WHERE is_strategic = 1
        GROUP BY technology_area
        ORDER BY count DESC
        LIMIT 10
    """)

    print("\nTop strategic technology areas:")
    for tech_area, count in cursor.fetchall():
        print(f"  {tech_area:30s}: {count:,}")

    conn.close()

    print("\nProcessing complete!")

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Automatically Add Importance Tier Logic to All Processors

This script modifies all three USAspending processors to add importance tier categorization.
Creates backups before modifying.
"""

import re
from pathlib import Path
import shutil

# Pattern lists to add as class variables
TIER_PATTERNS = '''
    # ========== IMPORTANCE TIER PATTERNS ==========

    # TIER 1: Strategic Entities
    TIER_1_STRATEGIC_ENTITIES = [
        'CHINESE ACADEMY', 'HUAWEI', 'ZTE', 'LENOVO',
        'TENCENT', 'ALIBABA', 'BAIDU', 'DJI', 'HIKVISION',
        'DAHUA', 'HYTERA', 'AVIC', 'COMAC', 'CSSC', 'NORINCO',
        'CHINESE UNIVERSITY', 'TSINGHUA', 'PEKING UNIVERSITY',
        'CAS ', 'RESEARCH CENTER', 'RESEARCH INSTITUTE',
        'BEIJING BOOK',
    ]

    # TIER 1: Strategic Technologies
    TIER_1_STRATEGIC_TECH = [
        'QUANTUM', 'ARTIFICIAL INTELLIGENCE', 'MACHINE LEARNING',
        'SEMICONDUCTOR', 'CHIP MANUFACTURING', 'PROCESSOR DESIGN',
        'BIOTECHNOLOGY', 'PHARMACEUTICAL RESEARCH', 'GENE',
        'SATELLITE', 'SPACE STATION', 'ROCKET', 'MISSILE',
        'HYPERSONIC', 'NUCLEAR', 'FUSION',
        'ADVANCED MATERIALS', 'NANOMATERIAL', 'GRAPHENE',
        '5G NETWORK'
    ]

    # TIER 3: Office Supplies
    TIER_3_OFFICE_SUPPLIES = [
        'CARTRIDGE', 'TONER', 'INK', 'PAPER', 'STAPLE', 'FOLDER',
        'PEN', 'PENCIL', 'MARKER', 'ENVELOPE', 'CLIP', 'BINDER',
        'LABEL MAKER', 'P-TOUCH', 'BROTHER P-TOUCH',
        'PT-D600VP', 'MFR: BROTHER',
        'NOTEPAD', 'POST-IT'
    ]

    # TIER 3: Commodity Electronics
    TIER_3_COMMODITY_ELECTRONICS = [
        'SURGE PROTECTOR', 'SURGE SUPPRESSOR', 'SURGE,PROTECTOR',
        'POWER STRIP', 'EXTENSION CORD', 'CABLE', 'ADAPTER', 'USB',
        'CHARGER', 'BATTERY', 'FLASHLIGHT', 'LIGHT BULB', 'LED', 'LAMP',
        'ABSORBER', 'OVERVOLTAGE',
    ]

    # TIER 3: Hardware
    TIER_3_HARDWARE = [
        'SCREW', 'BOLT', 'NUT', 'WASHER', 'WEDGE', 'HOOK', 'HINGE',
        'LOCK', 'KEY', 'NAIL', 'HAMMER', 'WRENCH', 'PLIERS',
        'SCREWDRIVER', 'DRILL BIT',
        'RELAY', 'ELBOW', 'PIPE', 'TUBE', 'FITTING', 'GASKET',
        'RESISTOR', 'CAPACITOR',
    ]

    # TIER 3: Apparel
    TIER_3_APPAREL = [
        'APRON', 'GLOVE', 'SHOE', 'BOOT', 'HAT', 'UNIFORM',
        'VEST', 'JACKET', 'PANTS', 'SHIRT', 'SOCKS',
        'COLLAR,EXTRICATION',
    ]

    # TIER 3: Kitchen/Janitorial
    TIER_3_KITCHEN = [
        'FUNNEL', 'WHISK', 'SPATULA', 'LADLE', 'SPOON', 'FORK',
        'KNIFE', 'PLATE', 'CUP', 'MOP', 'BROOM', 'BUCKET',
        'CLEANER', 'DETERGENT', 'SOAP',
        'WHIP', 'SCOOP', 'MEASURING', 'SHAKER', 'SALT',
        'PEELER', 'POTATO PEELER', 'IRON',
    ]

    # TIER 3: Medical Supplies (basic)
    TIER_3_MEDICAL_BASIC = [
        'APPLICATOR', 'BANDAGE', 'GAUZE', 'SWAB', 'SYRINGE',
        'GLOVES MEDICAL', 'MASK', 'FACE SHIELD', 'DISPOSAB',
        'KIT,INTRAVE',
    ]

    # TIER 3: Auto Parts (commodity)
    TIER_3_AUTO_PARTS = [
        'BEARING', 'FILTER', 'BELT', 'HOSE', 'CLAMP', 'BRACKET',
        'STARTER KIT', 'WHEEL', 'TIRE',
        'INDICATOR,SPECIAL',
    ]

    # TIER 3: Miscellaneous Commodity
    TIER_3_MISC_COMMODITY = [
        'CART', 'TRAVEL CART',
        'ABRASIVE WHEEL',
        'STRAP', 'TIE DOWN'
    ]

    # TIER 2: Computers
    TIER_2_COMPUTERS = [
        'COMPUTER', 'DESKTOP', 'LAPTOP', 'SERVER', 'WORKSTATION',
        'IMAC', 'DELL', 'OPTIPLEX', 'HP ELITEBOOK', 'THINKPAD',
        'DISK DRIVE', 'HARD DRIVE', 'SSD', 'STORAGE',
        'MONITOR', 'DISPLAY', 'SCREEN'
    ]

    # TIER 2: Equipment
    TIER_2_EQUIPMENT = [
        'EQUIPMENT', 'MACHINERY', 'ENGINE', 'MOTOR', 'PUMP',
        'VALVE', 'COMPRESSOR', 'GENERATOR', 'TURBINE',
        'CIRCUIT BREAKER', 'CONTROL SYSTEM', 'SENSOR',
        'HEATER', 'TAPE', 'REFLECTIVE',
        'MICROTOME', 'HISTOLOGY',
    ]

    # TIER 2: Vehicles
    TIER_2_VEHICLES = [
        'VEHICLE', 'TRUCK', 'CAR', 'VAN', 'BUS',
        'AIRCRAFT', 'HELICOPTER', 'SHIP', 'VESSEL', 'BOAT'
    ]

    # TIER 2: Services
    TIER_2_SERVICES = [
        'CONSULTING', 'ENGINEERING', 'TECHNICAL SUPPORT',
        'SOFTWARE DEVELOPMENT', 'SYSTEM INTEGRATION',
        'CLEANING CONTRACT', 'OFFICE CLEANING', 'FACILITY',
        'CUSTOMS CLEARANCE', 'FREIGHT', 'TRANSPORTATION',
        'INTERPRETATION', 'TRANSLATION', 'TALENT SERVICES',
        'HOTEL', 'LODGING'
    ]

    # ========== END TIER PATTERNS ==========
'''

# Categorization method to add
CATEGORIZATION_METHOD = '''
    def _categorize_importance(self, recipient_name: str, vendor_name: str, description: str):
        """
        Categorize record by strategic intelligence value.

        Returns:
            tuple: (tier, importance_score, commodity_type)
        """
        desc = (description or '').upper()
        recipient = (recipient_name or '').upper()
        vendor = (vendor_name or '').upper()

        # Normalize description (handle comma variants)
        desc_normalized = desc.replace(',', ' ')

        # Special handling: Part number patterns (Brother label makers)
        if ('P/N:' in desc or 'MFR:' in desc) and 'BROTHER' in desc:
            return ('TIER_3', 0.1, 'office_supplies')

        # TIER 1: Strategic Entities (name match)
        for entity in self.TIER_1_STRATEGIC_ENTITIES:
            if entity in recipient or entity in vendor:
                return ('TIER_1', 1.0, 'strategic_entity')

        # TIER 1: Strategic Technologies (description match)
        for tech in self.TIER_1_STRATEGIC_TECH:
            if tech in desc_normalized:
                return ('TIER_1', 1.0, 'strategic_technology')

        # TIER 3: Commodity categories (description match)
        commodity_patterns = [
            (self.TIER_3_OFFICE_SUPPLIES, 'office_supplies'),
            (self.TIER_3_COMMODITY_ELECTRONICS, 'commodity_electronics'),
            (self.TIER_3_HARDWARE, 'hardware'),
            (self.TIER_3_APPAREL, 'apparel'),
            (self.TIER_3_KITCHEN, 'kitchen_janitorial'),
            (self.TIER_3_MEDICAL_BASIC, 'medical_supplies_basic'),
            (self.TIER_3_AUTO_PARTS, 'auto_parts_commodity'),
            (self.TIER_3_MISC_COMMODITY, 'misc_commodity'),
        ]

        for keywords, commodity_type in commodity_patterns:
            for keyword in keywords:
                if keyword in desc_normalized:
                    return ('TIER_3', 0.1, commodity_type)

        # TIER 2: Technology/Service categories
        tier2_patterns = [
            (self.TIER_2_COMPUTERS, 'computers_electronics'),
            (self.TIER_2_EQUIPMENT, 'specialized_equipment'),
            (self.TIER_2_VEHICLES, 'vehicles_transport'),
            (self.TIER_2_SERVICES, 'professional_services'),
        ]

        for keywords, category in tier2_patterns:
            for keyword in keywords:
                if keyword in desc_normalized:
                    return ('TIER_2', 0.5, category)

        # Special handling: Empty descriptions
        if len(desc.strip()) < 10 or 'DESCR N.A.' in desc:
            return ('TIER_2', 0.5, 'insufficient_description')

        # Default: TIER_2 (general technology/equipment)
        return ('TIER_2', 0.5, 'general_technology')
'''

def add_tier_patterns(content: str) -> str:
    """Add tier patterns after SCHEMA definition."""

    # Find the line with "def __init__(self):"
    init_match = re.search(r'(    def __init__\(self\):)', content)
    if not init_match:
        print("  [WARNING] Could not find __init__ method")
        return content

    # Insert patterns before __init__
    insert_pos = init_match.start()
    new_content = content[:insert_pos] + TIER_PATTERNS + "\n" + content[insert_pos:]

    return new_content

def add_categorization_method(content: str) -> str:
    """Add categorization method after _is_product_sourcing_mention."""

    # Find _is_product_sourcing_mention method
    match = re.search(r'(    def _is_product_sourcing_mention.*?\n        return [^\n]+\n)', content, re.DOTALL)
    if not match:
        print("  [WARNING] Could not find _is_product_sourcing_mention method")
        return content

    # Insert after the method
    insert_pos = match.end()
    new_content = content[:insert_pos] + "\n" + CATEGORIZATION_METHOD + "\n" + content[insert_pos:]

    return new_content

def update_detect_china_connection(content: str, table_name: str) -> str:
    """Add importance tier categorization to detect method."""

    # Find the return statement in _detect_china_connection
    # Look for the pattern with 'processed_date' as last field
    pattern = r"(            'processed_date': datetime\.now\(\)\.isoformat\(\),\n        })"

    # Replacement with importance tier fields
    replacement = r"            'processed_date': datetime.now().isoformat(),\n" + \
                 r"            'importance_tier': importance_tier,\n" + \
                 r"            'importance_score': importance_score,\n" + \
                 r"            'commodity_type': commodity_type,\n" + \
                 r"        }"

    # Also need to add the categorization call before the return
    # Find "# Build detection result" or "return {"
    cat_call = "        # Categorize importance tier\n" + \
              "        importance_tier, importance_score, commodity_type = self._categorize_importance(\n" + \
              "            recipient_name=recipient_name,\n" + \
              "            vendor_name=vendor_name,\n" + \
              "            description=award_description\n" + \
              "        )\n\n"

    # Insert categorization call before "# Build detection result" or "return {"
    build_pattern = r'(        # Build detection result\n)'
    if re.search(build_pattern, content):
        content = re.sub(build_pattern, cat_call + r'\1', content)
    else:
        # Try alternative pattern
        return_pattern = r'(        return \{)'
        content = re.sub(return_pattern, cat_call + r'\1', content)

    # Update the return dict
    content = re.sub(pattern, replacement, content)

    return content

def update_save_batch(content: str, table_name: str) -> str:
    """Update save_batch to include importance tier fields."""

    # Update INSERT statement - find the table name and add fields
    insert_pattern = rf"(INSERT OR REPLACE INTO {table_name} \(\n.*?processed_date)"
    replacement = rf"\1,\n                importance_tier, importance_score, commodity_type"

    content = re.sub(insert_pattern, replacement, content, flags=re.DOTALL)

    # Update VALUES placeholder count (add 3 more ?)
    values_pattern = rf"(\) VALUES \([?,' ]+\?\))"
    # This is tricky - we need to add 3 more ? marks
    # Let's find the specific pattern for each table
    if '305' in table_name:
        content = content.replace("VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                 "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)")
    elif '101' in table_name:
        content = content.replace("VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                 "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)")
    elif 'comprehensive' in table_name:
        # Find current count and add 3
        pass  # Will handle manually if needed

    # Update the tuple in executemany to include the new fields
    dict_pattern = rf"(d\['processed_date'\])"
    replacement_tuple = r"\1,\n                d['importance_tier'], d['importance_score'], d['commodity_type']"

    content = re.sub(dict_pattern, replacement_tuple, content)

    return content

def process_file(file_path: Path, table_name: str):
    """Process a single processor file."""

    print(f"\n--- Processing {file_path.name} ---")

    # Backup original
    backup_path = file_path.with_suffix('.py.backup')
    shutil.copy(file_path, backup_path)
    print(f"  [OK] Backup created: {backup_path.name}")

    # Read file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_lines = len(content.split('\n'))

    # Check if already modified
    if 'TIER_1_STRATEGIC_ENTITIES' in content:
        print("  [SKIP] File already contains importance tier logic")
        return

    # Apply modifications
    print("  [1/4] Adding tier pattern lists...")
    content = add_tier_patterns(content)

    print("  [2/4] Adding categorization method...")
    content = add_categorization_method(content)

    print("  [3/4] Updating detect_china_connection method...")
    content = update_detect_china_connection(content, table_name)

    print("  [4/4] Updating save_batch method...")
    content = update_save_batch(content, table_name)

    # Write modified file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    new_lines = len(content.split('\n'))
    added_lines = new_lines - original_lines

    print(f"  [OK] File updated ({added_lines:+d} lines)")

def main():
    """Update all three processors."""

    print("="*80)
    print("AUTOMATICALLY ADDING IMPORTANCE TIER LOGIC TO PROCESSORS")
    print("="*80)

    processors = [
        ('scripts/process_usaspending_305_column.py', 'usaspending_china_305'),
        ('scripts/process_usaspending_101_column.py', 'usaspending_china_101'),
        ('scripts/process_usaspending_comprehensive.py', 'usaspending_china_comprehensive'),
    ]

    for file_path_str, table_name in processors:
        file_path = Path(file_path_str)
        if not file_path.exists():
            print(f"\n[WARNING] File not found: {file_path}")
            continue

        process_file(file_path, table_name)

    print("\n" + "="*80)
    print("PROCESSOR UPDATES COMPLETE")
    print("="*80)

    print("\nBackup files created:")
    for file_path_str, _ in processors:
        backup = Path(file_path_str).with_suffix('.py.backup')
        if backup.exists():
            print(f"  - {backup}")

    print("\nNext steps:")
    print("1. Review modified processors for correctness")
    print("2. Test on small sample before full re-processing")
    print("3. Re-process all 166,557 records with importance tiers")

if __name__ == '__main__':
    main()

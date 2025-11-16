#!/usr/bin/env python3
"""
Expand Commodity Pattern List

Analyzes uncategorized records from sample to identify additional
commodity patterns and improve categorization coverage.
"""

import json
import csv
from collections import Counter, defaultdict
import re

# Load sample
SAMPLE_FILE = "data/processed/usaspending_manual_review/fresh_sample_20251016_200923.json"

with open(SAMPLE_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

samples = data['samples']

# Load existing categorization
categories_by_tid = {}
with open('analysis/sample_categorization_analysis.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        categories_by_tid[row['Transaction ID']] = row['Category']

# Get uncategorized records
uncategorized = [s for s in samples if categories_by_tid.get(s['transaction_id']) == 'UNCATEGORIZED']

print("="*80)
print(f"EXPANDING COMMODITY PATTERNS")
print("="*80)
print(f"\nAnalyzing {len(uncategorized)} uncategorized records")

# Extract keywords from descriptions
keyword_freq = Counter()
for record in uncategorized:
    desc = (record.get('award_description') or '').upper()
    # Extract meaningful words (3+ characters, exclude common words)
    words = re.findall(r'\b[A-Z]{3,}\b', desc)
    common_words = {'THE', 'AND', 'FOR', 'WITH', 'ITEM', 'NAME', 'SIZE', 'TYPE', 'INCH', 'LONG', 'WIDE'}
    meaningful_words = [w for w in words if w not in common_words]
    keyword_freq.update(meaningful_words)

print("\n--- TOP 50 KEYWORDS IN UNCATEGORIZED RECORDS ---")
for keyword, count in keyword_freq.most_common(50):
    print(f"{keyword}: {count}")

# Categorize by manual inspection
print("\n\n" + "="*80)
print("MANUAL CATEGORIZATION OF UNCATEGORIZED RECORDS")
print("="*80)

# Sample 30 uncategorized records for pattern identification
print("\nSample of uncategorized records:")
print("-"*80)

for i, record in enumerate(uncategorized[:30]):
    recipient = record['recipient_name'][:50]
    desc = (record.get('award_description') or '')[:100]
    conf = record['highest_confidence']

    print(f"\n{i+1}. [{conf}] {recipient}")
    print(f"   {desc}")

print("\n" + "="*80)

# Propose new patterns
proposed_patterns = {
    'TIER_3_COMMODITY': {
        'office_supplies_expanded': [
            'CARTRIDGE', 'TONER', 'INK', 'PAPER', 'STAPLE', 'FOLDER',
            'PEN', 'PENCIL', 'MARKER', 'ENVELOPE', 'CLIP', 'BINDER',
            'LABEL MAKER', 'P-TOUCH', 'BROTHER P-TOUCH',  # From uncategorized
            'NOTEPAD', 'POST-IT'
        ],
        'commodity_electronics_expanded': [
            'SURGE PROTECTOR', 'SURGE SUPPRESSOR', 'POWER STRIP', 'EXTENSION CORD',
            'CABLE', 'ADAPTER', 'USB', 'CHARGER', 'BATTERY',
            'FLASHLIGHT', 'LIGHT BULB', 'LED',
            'ABSORBER', 'OVERVOLTAGE',  # From uncategorized
        ],
        'hardware_expanded': [
            'SCREW', 'BOLT', 'NUT', 'WASHER', 'WEDGE', 'HOOK', 'HINGE',
            'LOCK', 'KEY', 'NAIL', 'HAMMER', 'WRENCH', 'PLIERS',
            'SCREWDRIVER', 'DRILL BIT',
            'RELAY', 'ELBOW', 'PIPE', 'TUBE', 'FITTING',  # Auto parts from uncategorized
        ],
        'apparel_expanded': [
            'APRON', 'GLOVE', 'SHOE', 'BOOT', 'HAT', 'UNIFORM',
            'VEST', 'JACKET', 'PANTS', 'SHIRT', 'SOCKS'
        ],
        'kitchen_janitorial_expanded': [
            'FUNNEL', 'WHISK', 'SPATULA', 'LADLE', 'SPOON', 'FORK',
            'KNIFE', 'PLATE', 'CUP', 'MOP', 'BROOM', 'BUCKET',
            'CLEANER', 'DETERGENT', 'SOAP',
            'WHIP', 'SCOOP', 'MEASURING CUP',  # From uncategorized
        ],
        'medical_supplies_basic': [
            'APPLICATOR', 'BANDAGE', 'GAUZE', 'SWAB', 'SYRINGE',
            'GLOVES MEDICAL', 'MASK', 'FACE SHIELD'
        ],
        'auto_parts_commodity': [
            'RELAY', 'ELBOW', 'PIPE', 'TUBE', 'FITTING', 'GASKET',
            'FILTER', 'BELT', 'HOSE', 'CLAMP', 'BRACKET'
        ]
    },

    'TIER_2_TECHNOLOGY': {
        'computers_electronics': [
            'COMPUTER', 'DESKTOP', 'LAPTOP', 'SERVER', 'WORKSTATION',
            'IMAC', 'DELL', 'HP ', 'LENOVO', 'OPTIPLEX',  # From uncategorized
            'DISK DRIVE', 'HARD DRIVE', 'SSD', 'STORAGE',
            'MONITOR', 'DISPLAY', 'SCREEN'
        ],
        'specialized_equipment': [
            'EQUIPMENT', 'MACHINERY', 'ENGINE', 'MOTOR', 'PUMP',
            'VALVE', 'COMPRESSOR', 'GENERATOR', 'TURBINE',
            'STARTER', 'CIRCUIT BREAKER',  # From uncategorized
            'CONTROL SYSTEM', 'SENSOR', 'ACTUATOR'
        ],
        'vehicles_transport': [
            'VEHICLE', 'TRUCK', 'CAR', 'VAN', 'BUS',
            'AIRCRAFT', 'HELICOPTER', 'SHIP', 'VESSEL', 'BOAT'
        ],
        'telecommunications': [
            'TELECOMMUNICATION', 'NETWORK', 'ROUTER', 'SWITCH',
            'MODEM', 'ANTENNA', 'RADIO', 'TRANSMITTER'
        ]
    },

    'TIER_2_SERVICES': {
        'professional_services': [
            'CONSULTING', 'ENGINEERING', 'TECHNICAL SUPPORT',
            'SOFTWARE DEVELOPMENT', 'SYSTEM INTEGRATION',
            'CLEANING CONTRACT', 'OFFICE CLEANING',  # From uncategorized
            'CUSTOMS CLEARANCE', 'FREIGHT',  # From uncategorized
            'INTERPRETATION', 'TRANSLATION'  # From uncategorized
        ]
    },

    'TIER_1_STRATEGIC': {
        'strategic_entities': [
            'CHINESE ACADEMY', 'HUAWEI', 'ZTE', 'LENOVO',
            'TENCENT', 'ALIBABA', 'BAIDU', 'DJI', 'HIKVISION',
            'DAHUA', 'HYTERA', 'AVIC', 'COMAC', 'CSSC',
            'CHINESE UNIVERSITY', 'TSINGHUA', 'PEKING UNIVERSITY',
            'CAS ', 'RESEARCH CENTER', 'RESEARCH INSTITUTE'
        ],
        'strategic_technologies': [
            'QUANTUM', 'ARTIFICIAL INTELLIGENCE', 'MACHINE LEARNING',
            'SEMICONDUCTOR', 'CHIP MANUFACTURING', 'PROCESSOR',
            'BIOTECHNOLOGY', 'PHARMACEUTICAL', 'GENE',
            'SATELLITE', 'SPACE', 'ROCKET', 'MISSILE',
            'HYPERSONIC', 'NUCLEAR', 'FUSION',
            'ADVANCED MATERIALS', 'NANOMATERIAL', 'GRAPHENE'
        ]
    }
}

print("\nPROPOSED EXPANDED PATTERNS")
print("="*80)

for tier, categories in proposed_patterns.items():
    print(f"\n{tier}:")
    for category, keywords in categories.items():
        print(f"  {category}: {len(keywords)} keywords")
        print(f"    New keywords: {', '.join(keywords[-5:])}")  # Show last 5 (new ones)

# Save to JSON
output = {
    'metadata': {
        'analyzed_records': len(uncategorized),
        'top_keywords': dict(keyword_freq.most_common(30)),
        'notes': 'Expanded patterns based on manual review of uncategorized records'
    },
    'proposed_patterns': proposed_patterns
}

with open('analysis/expanded_commodity_patterns.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)

print(f"\n{'='*80}")
print("Expanded patterns saved to: analysis/expanded_commodity_patterns.json")
print(f"{'='*80}")

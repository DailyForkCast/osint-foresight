#!/usr/bin/env python3
"""
Deep analysis of 101-column schema to map ALL detection fields properly.

Strategy:
1. Analyze 50+ records to find consistent patterns
2. Map country fields precisely
3. Map name/organization fields
4. Identify parent company fields if present
5. Map financial, date, and agency fields
6. Verify schema consistency across both files
"""

import gzip
from pathlib import Path
from collections import defaultdict

data_dir = Path('F:/OSINT_DATA/USAspending/extracted_data')

# Both 101-column files
files = [
    ('5847.dat.gz', 14.5),
    ('5836.dat.gz', 12.2),
]

print('='*80)
print('COMPREHENSIVE 101-COLUMN SCHEMA ANALYSIS')
print('='*80)

for filename, size_gb in files:
    filepath = data_dir / filename

    print(f'\n{"="*80}')
    print(f'{filename} - {size_gb:.1f} GB')
    print(f'{"="*80}')

    # Collect field statistics
    field_types = defaultdict(lambda: defaultdict(int))
    field_samples = defaultdict(set)

    with gzip.open(filepath, 'rt', encoding='utf-8', errors='replace') as f:
        # Read 50 records for pattern analysis
        for rec_num in range(50):
            line = f.readline()
            if not line:
                break

            fields = line.strip().split('\t')

            for i, val in enumerate(fields):
                if val and val != r'\N':
                    # Categorize field types
                    if val.upper() in ['USA', 'CHN', 'CHINA', 'HONG KONG', 'UNITED STATES',
                                       'CANADA', 'CAN', 'JPN', 'JAPAN', 'GBR', 'UNITED KINGDOM',
                                       'DEU', 'GERMANY', 'TAIWAN', 'TWN']:
                        field_types[i]['country'] += 1
                        field_samples[i].add(val)

                    elif any(kw in val.upper() for kw in ['INC', 'LLC', 'CORP', 'COMPANY',
                                                           'UNIVERSITY', 'LTD', 'ASSOCIATION']):
                        if len(val) > 10 and len(val) < 100:
                            field_types[i]['organization'] += 1
                            if len(field_samples[i]) < 3:
                                field_samples[i].add(val)

                    elif val.replace('-', '').replace('.', '').replace('$', '').replace(',', '').isdigit():
                        field_types[i]['numeric'] += 1

                    elif len(val) == 4 and val.isdigit():
                        field_types[i]['year'] += 1

                    elif '-' in val and len(val) == 10:
                        field_types[i]['date'] += 1

    # Print findings
    print('\nCOUNTRY FIELDS (detected in 5+ records):')
    for i in sorted(field_types.keys()):
        if field_types[i]['country'] >= 5:
            samples = list(field_samples[i])[:5]
            print(f'  [{i:3d}]: {field_types[i]["country"]:2d} country values - {", ".join(samples)}')

    print('\nORGANIZATION/NAME FIELDS (detected in 5+ records):')
    for i in sorted(field_types.keys()):
        if field_types[i]['organization'] >= 5:
            samples = list(field_samples[i])[:2]
            print(f'  [{i:3d}]: {field_types[i]["organization"]:2d} org names')
            for sample in samples:
                print(f'        {sample[:70]}')

    print('\nFIELD TYPE SUMMARY:')
    for i in sorted(field_types.keys())[:30]:  # First 30 fields
        types = field_types[i]
        if any(types.values()):
            type_str = ', '.join(f'{k}:{v}' for k, v in types.items() if v > 0)
            print(f'  [{i:3d}]: {type_str}')

# Now do detailed record inspection
print('\n' + '='*80)
print('DETAILED RECORD INSPECTION (First 3 records from 5847.dat.gz)')
print('='*80)

filepath = data_dir / '5847.dat.gz'
with gzip.open(filepath, 'rt', encoding='utf-8', errors='replace') as f:
    for rec_num in range(3):
        print(f'\nRecord {rec_num + 1}:')
        print('-'*80)
        fields = f.readline().strip().split('\t')

        # Show all fields with labels
        for i, val in enumerate(fields):
            if val and val != r'\N':
                val_display = val[:70] if len(val) > 70 else val
                print(f'  [{i:3d}]: {val_display}')

print('\n' + '='*80)
print('SCHEMA MAPPING RECOMMENDATION')
print('='*80)
print('''
Based on analysis above, map the following for 101-column format:

CRITICAL FIELDS FOR CHINA DETECTION:
- [9]: recipient_name (organization/individual name)
- [55]: recipient_country_code (USA, CHN, etc.)
- [56]: recipient_country_name (UNITED STATES, CHINA, etc.)
- [73]: pop_country_code (place of performance)
- [74]: pop_country_name

ADDITIONAL FIELDS TO CAPTURE:
- [0]: transaction_id
- [8]: award_description/program_title (may contain entity info)
- [11]: agency_code
- [12]: agency_name
- [15]: sub_agency_code
- [16]: sub_agency_name

NOTE: This format appears to be for grants/assistance rather than contracts.
May have different detection patterns than contract data.
''')

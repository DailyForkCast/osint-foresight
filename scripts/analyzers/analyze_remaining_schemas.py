#!/usr/bin/env python3
"""
Analyze remaining USAspending files to map detection fields.

Strategy:
1. Sample first 5 records from each major file
2. Find fields containing country data
3. Find fields containing organization names
4. Map field positions for each schema
"""

import gzip
from pathlib import Path
from collections import defaultdict

data_dir = Path('F:/OSINT_DATA/USAspending/extracted_data')

# Target files by size
targets = [
    ('5879.dat.gz', 150, 47.7),  # LARGEST
    ('5848.dat.gz', 305, 15.4),
    ('5847.dat.gz', 101, 14.5),
    ('5836.dat.gz', 101, 12.2),
    ('5801.dat.gz', 58, 13.3),
    ('5876.dat.gz', 206, 4.9),   # Known schema
]

print('='*80)
print('DETAILED SCHEMA ANALYSIS FOR DETECTION FIELDS')
print('='*80)

for filename, expected_cols, size_gb in targets:
    filepath = data_dir / filename

    print(f'\n{"="*80}')
    print(f'{filename} - {expected_cols} columns - {size_gb:.1f} GB')
    print(f'{"="*80}')

    try:
        with gzip.open(filepath, 'rt', encoding='utf-8', errors='replace') as f:
            # Read 5 sample records
            records = []
            for i in range(5):
                line = f.readline()
                if not line:
                    break
                records.append(line.strip().split('\t'))

            if not records:
                print('No records found!')
                continue

            # Find country fields (must have China, USA, or other countries in multiple records)
            country_candidates = defaultdict(set)
            for record in records:
                for i, val in enumerate(record):
                    if val.upper() in ['CHINA', 'USA', 'UNITED STATES', 'HONG KONG',
                                       'CHN', 'JPN', 'JAPAN', 'CANADA', 'CAN', 'GBR',
                                       'UNITED KINGDOM', 'GERMANY', 'DEU']:
                        country_candidates[i].add(val)

            print('\nCOUNTRY FIELDS:')
            for idx in sorted(country_candidates.keys()):
                values = country_candidates[idx]
                print(f'  [{idx:3d}]: {", ".join(list(values)[:5])}')

            # Find name fields (containing organization patterns)
            name_candidates = defaultdict(list)
            org_keywords = ['INC', 'LLC', 'CORP', 'COMPANY', 'LTD', 'UNIVERSITY',
                           'GOVERNMENT', 'INTERNATIONAL', 'ASSOCIATION']

            for record in records:
                for i, val in enumerate(record):
                    if len(val) > 10 and val != '\\N':
                        val_upper = val.upper()
                        if any(kw in val_upper for kw in org_keywords):
                            if len(name_candidates[i]) < 2:  # Keep 2 examples
                                name_candidates[i].append(val[:60])

            print('\nNAME/ORGANIZATION FIELDS:')
            for idx in sorted(name_candidates.keys()):
                examples = name_candidates[idx]
                print(f'  [{idx:3d}]:')
                for ex in examples:
                    print(f'        {ex}')

            # Check for typical USAspending field patterns
            print('\nFIELD POSITION HINTS:')
            for i, val in enumerate(records[0][:20]):  # Check first 20 fields
                if val and val != '\\N':
                    val_display = val[:40] if len(val) > 40 else val
                    print(f'  [{i:3d}]: {val_display}')

    except Exception as e:
        print(f'ERROR: {e}')
        import traceback
        traceback.print_exc()

print('\n' + '='*80)
print('SUMMARY & RECOMMENDATIONS')
print('='*80)
print('''
Based on the analysis above:

1. 206-column (5876.dat.gz, 4.9GB): Use existing schema
2. 150-column (5879.dat.gz, 47.7GB): Map country fields at [46-47, 59-60]
3. 305-column (5848.dat.gz, 15.4GB): Map country fields at [107-108]
4. 101-column (5847/5836, 26.7GB): Map country fields at [55-56, 73-74]
5. 58-column (5801.dat.gz, 13.3GB): Needs further analysis

Priority: 150-column (48GB) + 101-column (27GB) + 305-column (15GB) = 90GB (78%)
''')

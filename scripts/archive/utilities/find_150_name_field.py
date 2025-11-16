#!/usr/bin/env python3
"""Find recipient name field in 150-column format."""

import gzip
from pathlib import Path

filepath = Path('F:/OSINT_DATA/USAspending/extracted_data/5879.dat.gz')

print('DEEP ANALYSIS: 150-column format (47.7GB - LARGEST remaining file)')
print('='*80)

with gzip.open(filepath, 'rt', encoding='utf-8', errors='replace') as f:
    # Read 5 records to find patterns
    for rec_num in range(5):
        record = f.readline().strip().split('\t')

        print(f'\nRecord {rec_num+1} (showing potential name/org fields):')
        print('-'*80)

        # Show all non-null fields between positions 17-30 (typical name field range)
        print('Fields 17-30 (typical recipient name range):')
        for i in range(17, min(30, len(record))):
            val = record[i]
            if val and val != r'\N':
                print(f'  [{i:3d}]: {val[:70]}')

        # Also check fields around country fields (46-60)
        print('\nFields around country (40-70):')
        for i in range(40, min(70, len(record))):
            val = record[i]
            if val and val != r'\N' and len(val) > 10:
                if not val.startswith('[') and not val.startswith('{'):
                    print(f'  [{i:3d}]: {val[:70]}')

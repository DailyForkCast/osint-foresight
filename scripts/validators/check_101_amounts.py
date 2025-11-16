#!/usr/bin/env python3
"""Check award amount field in 101-column format."""

import gzip
from pathlib import Path

filepath = Path('F:/OSINT_DATA/USAspending/extracted_data/5847.dat.gz')

print('Checking award amount field (position 27) in first 10 records:')
print('='*80)

with gzip.open(filepath, 'rt', encoding='utf-8', errors='replace') as f:
    for i in range(10):
        line = f.readline()
        fields = line.strip().split('\t')

        # Check fields around position 27 for numeric amounts
        print(f'\nRecord {i+1}:')
        for idx in [25, 26, 27, 28, 29, 30]:
            if idx < len(fields):
                val = fields[idx]
                if val and val != r'\N':
                    print(f'  [{idx}]: {val}')

#!/usr/bin/env python3
"""Verify 101-column test detections."""

import sqlite3
from pathlib import Path

db_path = Path('F:/OSINT_WAREHOUSE/osint_master.db')

with sqlite3.connect(db_path) as conn:
    cur = conn.cursor()

    print('='*80)
    print('101-COLUMN TEST DETECTIONS (9 records)')
    print('='*80)

    cur.execute('''
        SELECT
            recipient_name,
            recipient_country_name,
            pop_country_name,
            award_amount,
            detection_types
        FROM usaspending_china_101
        ORDER BY award_amount DESC
    ''')

    for i, row in enumerate(cur.fetchall(), 1):
        recip_name, recip_country, pop_country, amount, det_types = row
        print(f'\nDetection {i}:')
        print(f'  Recipient: {recip_name}')
        print(f'  Recipient Country: {recip_country or "N/A"}')
        print(f'  Performance Country: {pop_country or "N/A"}')
        print(f'  Amount: ${amount:,.2f}')
        print(f'  Detection Types: {det_types}')

    # Check if any Taiwan false positives
    print('\n' + '='*80)
    print('TAIWAN CHECK (should be 0):')
    print('='*80)

    cur.execute('''
        SELECT COUNT(*) FROM usaspending_china_101
        WHERE recipient_country_name LIKE '%TAIWAN%'
           OR recipient_country_code = 'TWN'
           OR pop_country_code = 'TWN'
    ''')

    taiwan_count = cur.fetchone()[0]
    print(f'Taiwan records: {taiwan_count}')

    if taiwan_count == 0:
        print('✓ PASSED: No Taiwan false positives')
    else:
        print('✗ FAILED: Taiwan detections found!')

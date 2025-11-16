#!/usr/bin/env python3
"""
Quick script to add missing countries to bilateral_countries table
"""

import sqlite3
import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

DB_PATH = Path("F:/OSINT_WAREHOUSE/osint_master.db")
conn = sqlite3.connect(str(DB_PATH), timeout=30.0)

countries = [
    ('GB', 'United Kingdom', '英国', True, True, True),  # EU(was), NATO, Five Eyes
    ('SE', 'Sweden', '瑞典', True, True, False),  # EU, NATO, not Five Eyes
    ('BE', 'Belgium', '比利时', True, True, False),  # EU, NATO HQ
    ('CZ', 'Czech Republic', '捷克', True, True, False),  # EU, NATO
    ('LT', 'Lithuania', '立陶宛', True, True, False),  # EU, NATO
    ('FR', 'France', '法国', True, True, False),  # EU, NATO
    ('PL', 'Poland', '波兰', True, True, False),  # EU, NATO
    ('NL', 'Netherlands', '荷兰', True, True, False),  # EU, NATO
    ('DK', 'Denmark', '丹麦', True, True, False),  # EU, NATO
]

for cc, name, name_cn, eu, nato, fvey in countries:
    conn.execute("""
        INSERT OR REPLACE INTO bilateral_countries
        (country_code, country_name, country_name_chinese, eu_member, nato_member, five_eyes)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (cc, name, name_cn, eu, nato, fvey))
    print(f"✓ Added {cc}: {name}")

conn.commit()
print(f"\n✓ Added {len(countries)} countries to bilateral_countries")
conn.close()

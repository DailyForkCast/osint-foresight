#!/usr/bin/env python3
"""Add Romania, Czech Republic, Poland, Hungary to bilateral_countries"""
import sqlite3
from pathlib import Path

DB_PATH = Path("F:/OSINT_WAREHOUSE/osint_master.db")
conn = sqlite3.connect(str(DB_PATH), timeout=30.0)

countries = [
    ('RO', 'Romania', '罗马尼亚', True, True, False),
    ('CZ', 'Czech Republic', '捷克', True, True, False),
    ('PL', 'Poland', '波兰', True, True, False),
    ('HU', 'Hungary', '匈牙利', True, True, False),
]

for cc, name, name_cn, eu, nato, fvey in countries:
    conn.execute("""
        INSERT OR REPLACE INTO bilateral_countries
        (country_code, country_name, country_name_chinese, eu_member, nato_member, five_eyes)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (cc, name, name_cn, eu, nato, fvey))
    print(f"Added: {name} ({cc})")

conn.commit()
conn.close()
print("\n✅ All 4 countries added to bilateral_countries table")

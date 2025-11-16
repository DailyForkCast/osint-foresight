#!/usr/bin/env python3
"""Check GDELT collection totals for Lithuania 2021 crisis"""

import sqlite3

db = sqlite3.connect('F:/OSINT_WAREHOUSE/osint_master.db')
cur = db.cursor()

# Total for Jul-Nov 2021
cur.execute('''
    SELECT COUNT(*)
    FROM gdelt_events
    WHERE sqldate BETWEEN 20210701 AND 20211130
''')
total = cur.fetchone()[0]

# By month
cur.execute('''
    SELECT
        sqldate/100 as month,
        COUNT(*) as events
    FROM gdelt_events
    WHERE sqldate BETWEEN 20210701 AND 20211130
    GROUP BY month
    ORDER BY month
''')

print("Lithuania 2021 Crisis - Full Collection Results")
print("=" * 60)
for row in cur.fetchall():
    month = int(row[0])
    events = row[1]
    month_name = {
        202107: "July 2021",
        202108: "August 2021",
        202109: "September 2021",
        202110: "October 2021",
        202111: "November 2021",
        202112: "December 2021"
    }.get(month, str(month))
    print(f"  {month_name}: {events:,} events")

print("=" * 60)
print(f"  TOTAL (Jul-Nov): {total:,} events")

# Check December too
cur.execute('''
    SELECT COUNT(*)
    FROM gdelt_events
    WHERE sqldate BETWEEN 20211201 AND 20211231
''')
dec_total = cur.fetchone()[0]
print(f"  December 2021: {dec_total:,} events")
print(f"  GRAND TOTAL (Jul-Dec): {total + dec_total:,} events")
print("=" * 60)

db.close()

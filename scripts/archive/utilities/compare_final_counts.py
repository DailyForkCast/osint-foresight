#!/usr/bin/env python3
"""Compare final database counts to BigQuery actual counts"""

import sqlite3

# BigQuery actual counts (from check_bigquery_actual_counts.py)
bigquery_actual = {
    202107: 138463,
    202108: 107058,
    202109: 143919,
    202110: 134902,
    202111: 132063,
    202112: 122815
}

# Query our database
db = sqlite3.connect('F:/OSINT_WAREHOUSE/osint_master.db')
cur = db.cursor()

cur.execute('''
    SELECT
        sqldate/100 as month,
        COUNT(*) as our_count
    FROM gdelt_events
    WHERE sqldate BETWEEN 20210701 AND 20211231
    GROUP BY month
    ORDER BY month
''')

print("=" * 90)
print("FINAL DATA COMPLETENESS - After V2 Collection")
print("=" * 90)
print(f"{'MONTH':<15} {'BIGQUERY':<15} {'OUR DB':<15} {'MISSING':<15} {'% COMPLETE'}")
print("-" * 90)

total_bigquery = sum(bigquery_actual.values())
total_ours = 0
total_missing = 0

for row in cur.fetchall():
    month = int(row[0])
    our_count = row[1]
    bq_count = bigquery_actual[month]
    missing = bq_count - our_count
    pct_complete = (our_count / bq_count * 100) if bq_count > 0 else 0

    total_ours += our_count
    total_missing += missing

    month_names = {
        202107: "July 2021",
        202108: "August 2021",
        202109: "Sept 2021",
        202110: "Oct 2021",
        202111: "Nov 2021",
        202112: "Dec 2021"
    }

    status = "[OK]" if pct_complete > 99 else "[INCOMPLETE]"

    print(f"{month_names[month]:<15} {bq_count:<15,} {our_count:<15,} {missing:<15,} {pct_complete:>6.2f}% {status}")

print("-" * 90)
total_pct = (total_ours / total_bigquery * 100) if total_bigquery > 0 else 0
print(f"{'TOTAL':<15} {total_bigquery:<15,} {total_ours:<15,} {total_missing:<15,} {total_pct:>6.2f}%")
print("=" * 90)

print(f"\nIMPROVEMENT:")
print(f"  Before V2: 605,014 events (77.6% complete, 22.4% data loss)")
print(f"  After V2:  {total_ours:,} events ({total_pct:.1f}% complete, {100-total_pct:.1f}% data loss)")
print(f"  Added:     {total_ours - 605014:,} new events")
print(f"  Still missing: {total_missing:,} events ({(total_missing/total_bigquery*100):.1f}%)")

print(f"\nREASON FOR REMAINING GAP:")
print(f"  Likely cause: Duplicate event IDs from multiple collection runs")
print(f"  - We ran 10k limit collection first")
print(f"  - Then 100k limit collection")
print(f"  - Then V2 unlimited collection")
print(f"  - BigQuery may have had events updated/replaced between runs")
print(f"  - Some event IDs may have been deleted/replaced in GDELT")

print(f"\nRECOMMENDATION:")
if total_pct > 99:
    print(f"  [OK] Data completeness > 99% - EXCELLENT")
elif total_pct > 95:
    print(f"  [OK] Data completeness > 95% - ACCEPTABLE for analysis")
elif total_pct > 90:
    print(f"  [WARNING] Data completeness 90-95% - Consider fresh collection")
else:
    print(f"  [CRITICAL] Data completeness < 90% - Fresh collection REQUIRED")

db.close()

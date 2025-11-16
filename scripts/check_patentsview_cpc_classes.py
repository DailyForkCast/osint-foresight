#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('F:/OSINT_WAREHOUSE/osint_master.db')
cursor = conn.cursor()

# Check what CPC classes we found
cursor.execute("""
    SELECT cpc_class, COUNT(*) as count
    FROM patentsview_cpc_strategic
    GROUP BY cpc_class
    ORDER BY count DESC
    LIMIT 30
""")

print("Top CPC Classes in PatentsView Chinese Patents:")
print("{:<15} {:<10}".format("CPC Class", "Count"))
print("-"*30)
for cpc_class, count in cursor.fetchall():
    print("{:<15} {:<10,}".format(cpc_class, count))

# Check for major strategic classes
print("\nChecking for major strategic classes:")
strategic_classes = ['H01L', 'G06F', 'H04W', 'H04B', 'G06N', 'G06T', 'H01M', 'G02B', 'G02F']
for sc in strategic_classes:
    cursor.execute("""
        SELECT COUNT(*) FROM patentsview_cpc_strategic
        WHERE cpc_class LIKE ?
    """, (sc + '%',))
    count = cursor.fetchone()[0]
    print("  {}: {:,} records".format(sc, count))

# Check strategic vs non-strategic
cursor.execute("SELECT is_strategic, COUNT(*) FROM patentsview_cpc_strategic GROUP BY is_strategic")
print("\nStrategic distribution:")
for is_strat, count in cursor.fetchall():
    label = "Strategic" if is_strat else "Non-strategic"
    print("  {}: {:,}".format(label, count))

conn.close()

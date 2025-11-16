#!/usr/bin/env python3
"""
Verify Cleanup Complete
Check that contamination has been removed
"""

import sqlite3

MAIN_DB = "F:/OSINT_WAREHOUSE/osint_master.db"

conn = sqlite3.connect(MAIN_DB)
cursor = conn.cursor()

print("=" * 80)
print("CLEANUP VERIFICATION")
print("=" * 80)

# Total count
cursor.execute("SELECT COUNT(*) FROM usaspending_china_305")
total = cursor.fetchone()[0]
print(f"\nTotal records: {total:,}")

# Check for china_sourced_product
print("\n[1/3] Checking for china_sourced_product records...")
cursor.execute("SELECT COUNT(*) FROM usaspending_china_305 WHERE detection_types = '[\"china_sourced_product\"]'")
sourced = cursor.fetchone()[0]
if sourced == 0:
    print(f"  [OK] No china_sourced_product records found")
else:
    print(f"  [WARNING] Found {sourced:,} china_sourced_product records")

# Check for Catalina China
print("\n[2/3] Checking for Catalina China (ceramics)...")
cursor.execute("""
    SELECT COUNT(*) FROM usaspending_china_305
    WHERE recipient_name LIKE '%CATALINA CHINA%' OR vendor_name LIKE '%CATALINA CHINA%'
""")
catalina = cursor.fetchone()[0]
if catalina == 0:
    print(f"  [OK] No Catalina China records found")
else:
    print(f"  [WARNING] Found {catalina:,} Catalina China records")

# Check for Facchinaggi
print("\n[3/3] Checking for Facchinaggi/Facchina (Italian)...")
cursor.execute("""
    SELECT COUNT(*) FROM usaspending_china_305
    WHERE recipient_name LIKE '%FACCHIN%' OR vendor_name LIKE '%FACCHIN%'
""")
facchin = cursor.fetchone()[0]
if facchin == 0:
    print(f"  [OK] No Facchinaggi/Facchina records found")
else:
    print(f"  [WARNING] Found {facchin:,} Facchinaggi/Facchina records")

# Detection types breakdown
print("\n" + "=" * 80)
print("DETECTION TYPES BREAKDOWN")
print("=" * 80)

cursor.execute("""
    SELECT detection_types, COUNT(*) as count
    FROM usaspending_china_305
    GROUP BY detection_types
    ORDER BY count DESC
""")

print("\nAll detection type combinations:")
for detection_types, count in cursor.fetchall():
    pct = (count / total) * 100
    print(f"  {count:5d} ({pct:5.1f}%) | {detection_types}")

conn.close()

print("\n" + "=" * 80)
if sourced == 0 and catalina == 0 and facchin == 0:
    print("[SUCCESS] Cleanup verified - all contamination removed")
else:
    print("[WARNING] Some contamination remains")
print("=" * 80)

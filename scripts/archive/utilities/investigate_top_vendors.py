#!/usr/bin/env python3
"""
Investigate Top Vendors in Chinese Entities Database
Check detection types and validate Chinese entity classification
"""

import sqlite3
import json

MAIN_DB = "F:/OSINT_WAREHOUSE/osint_master.db"

def investigate_vendors():
    """Investigate top vendors to validate Chinese entity detection"""

    print("=" * 80)
    print("INVESTIGATING TOP VENDORS - CHINESE ENTITY VALIDATION")
    print("=" * 80)

    conn = sqlite3.connect(MAIN_DB)
    cursor = conn.cursor()

    # Vendors to investigate
    suspicious_vendors = [
        "MMG TECHNOLOGY GROUP, INC.",
        "CATALINA CHINA, INC.",
        "FGS, LLC",
        "SOC COOP LIVORNESE FACCHINAGGI E TRASPORTI",
        "LENOVO (UNITED STATES) INC.",
    ]

    for vendor in suspicious_vendors:
        print(f"\n{'-' * 80}")
        print(f"VENDOR: {vendor}")
        print(f"{'-' * 80}")

        # Get sample records
        cursor.execute("""
            SELECT
                transaction_id,
                recipient_name,
                vendor_name,
                pop_country_code,
                pop_country_name,
                award_description,
                detection_types,
                highest_confidence
            FROM usaspending_china_305
            WHERE vendor_name LIKE ?
            LIMIT 3
        """, (f"%{vendor}%",))

        records = cursor.fetchall()

        if records:
            print(f"\nTotal records: {len(records)}")
            for i, record in enumerate(records, 1):
                (tid, recipient, vendor_name, pop_code, pop_name,
                 desc, detection_types, confidence) = record

                print(f"\n  Record {i}:")
                print(f"    Transaction ID: {tid}")
                print(f"    Recipient: {recipient[:60] if recipient else 'N/A'}")
                print(f"    Vendor: {vendor_name[:60] if vendor_name else 'N/A'}")
                print(f"    PoP Country: {pop_name or pop_code or 'N/A'}")
                print(f"    Description: {desc[:80] if desc else 'N/A'}...")
                print(f"    Detection Types: {detection_types}")
                print(f"    Confidence: {confidence}")

        else:
            print(f"  No records found for {vendor}")

    # Check for Italian company
    print(f"\n{'=' * 80}")
    print("CHECKING FOR ITALIAN COMPANY FALSE POSITIVE")
    print(f"{'=' * 80}")

    cursor.execute("""
        SELECT COUNT(*) FROM usaspending_china_305
        WHERE vendor_name LIKE '%FACCHINAGGI%'
           OR recipient_name LIKE '%FACCHINAGGI%'
    """)
    facchinaggi_count = cursor.fetchone()[0]
    print(f"\nFacchinaggi records: {facchinaggi_count}")

    if facchinaggi_count > 0:
        cursor.execute("""
            SELECT vendor_name, recipient_name, detection_types
            FROM usaspending_china_305
            WHERE vendor_name LIKE '%FACCHINAGGI%'
               OR recipient_name LIKE '%FACCHINAGGI%'
            LIMIT 1
        """)
        vendor, recipient, detection = cursor.fetchone()
        print(f"  Vendor: {vendor}")
        print(f"  Recipient: {recipient}")
        print(f"  Detection: {detection}")
        print(f"\n  ISSUE: Italian company detected as Chinese")
        print(f"  Reason: Name contains 'chin' substring?")

    # Summary statistics
    print(f"\n{'=' * 80}")
    print("DETECTION TYPE BREAKDOWN")
    print(f"{'=' * 80}")

    cursor.execute("""
        SELECT detection_types, COUNT(*) as count
        FROM usaspending_china_305
        GROUP BY detection_types
        ORDER BY count DESC
        LIMIT 10
    """)

    print("\nTop 10 detection type combinations:")
    for detection_types, count in cursor.fetchall():
        print(f"  {count:5d} | {detection_types}")

    conn.close()

if __name__ == "__main__":
    try:
        investigate_vendors()
    except Exception as e:
        print(f"\n[ERROR] Investigation failed: {e}")
        import traceback
        traceback.print_exc()

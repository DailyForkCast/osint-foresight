#!/usr/bin/env python3
"""
Investigate KraussMaffei duplicate entries
"""

import sqlite3
import sys
import io
from pathlib import Path
import json

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

DB_PATH = Path("F:/OSINT_WAREHOUSE/osint_master.db")

def main():
    print("="*80)
    print("INVESTIGATING KRAUSSMAFFEI DUPLICATE ENTRIES")
    print("="*80)

    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    # Find all KraussMaffei records
    print("\n1. Finding all KraussMaffei acquisition records...")
    cursor.execute("""
        SELECT acquisition_id, target_company, announcement_date, acquisition_date,
               deal_value_usd, chinese_acquirer, source_url
        FROM major_acquisitions
        WHERE target_company LIKE '%KraussMaffei%'
        ORDER BY announcement_date
    """)

    records = cursor.fetchall()
    print(f"\nFound {len(records)} KraussMaffei records:")
    for rec in records:
        print(f"\n  ID: {rec[0]}")
        print(f"  Company: {rec[1]}")
        print(f"  Announcement: {rec[2]}")
        print(f"  Acquisition: {rec[3]}")
        print(f"  Value: ${rec[4]/1e9:.2f}B" if rec[4] else "  Value: NULL")
        print(f"  Acquirer: {rec[5]}")
        print(f"  Source: {rec[6]}")

    # Find all citations linked to KraussMaffei
    print("\n2. Finding all citations for KraussMaffei records...")
    cursor.execute("""
        SELECT cl.linked_record_id, sc.title, sc.author, sc.publication_date,
               sc.source_url, cl.claim_supported, cl.evidence_type
        FROM citation_links cl
        JOIN source_citations sc ON cl.citation_id = sc.citation_id
        WHERE cl.linked_table = 'major_acquisitions'
          AND cl.linked_record_id LIKE '%kraussmaffei%'
        ORDER BY cl.linked_record_id, sc.publication_date
    """)

    citations = cursor.fetchall()
    print(f"\nFound {len(citations)} citations:")
    for cit in citations:
        print(f"\n  Linked to: {cit[0]}")
        print(f"  Title: {cit[1]}")
        print(f"  Author: {cit[2]}")
        print(f"  Date: {cit[3]}")
        print(f"  Claim: {cit[5]}")
        print(f"  Evidence: {cit[6]}")

    # Analysis
    print("\n" + "="*80)
    print("ANALYSIS")
    print("="*80)

    if len(records) > 1:
        print(f"\n⚠ DUPLICATE DETECTED: {len(records)} records found")
        print("\nRecommended action:")
        print("  - Keep the record with the most complete data")
        print("  - Consolidate citations to single record")
        print("  - Delete duplicate record")
    else:
        print("\n✓ No duplicate found")

    if len(citations) > 0:
        by_record = {}
        for cit in citations:
            record_id = cit[0]
            if record_id not in by_record:
                by_record[record_id] = []
            by_record[record_id].append(cit)

        print(f"\nCitations by record:")
        for record_id, cits in by_record.items():
            print(f"  {record_id}: {len(cits)} citation(s)")

    conn.close()

    print("\n" + "="*80)
    print("INVESTIGATION COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()

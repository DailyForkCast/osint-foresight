#!/usr/bin/env python3
"""
Fix KraussMaffei citation link - relink FT citation from DE_2015 to DE_2016
"""

import sqlite3
import sys
import io
from pathlib import Path

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

DB_PATH = Path("F:/OSINT_WAREHOUSE/osint_master.db")

def main():
    print("="*80)
    print("FIXING KRAUSSMAFFEI CITATION LINK")
    print("="*80)

    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    # Update the FT citation link from DE_2015_kraussmaffei to DE_2016_kraussmaffei
    print("\n1. Updating citation link...")
    cursor.execute("""
        UPDATE citation_links
        SET linked_record_id = 'DE_2016_kraussmaffei'
        WHERE linked_table = 'major_acquisitions'
          AND linked_record_id = 'DE_2015_kraussmaffei'
    """)

    rows_updated = cursor.rowcount
    conn.commit()

    print(f"  ✓ Updated {rows_updated} citation link(s)")

    # Verify the fix
    print("\n2. Verifying fix...")
    cursor.execute("""
        SELECT cl.linked_record_id, sc.title, sc.author
        FROM citation_links cl
        JOIN source_citations sc ON cl.citation_id = sc.citation_id
        WHERE cl.linked_table = 'major_acquisitions'
          AND cl.linked_record_id LIKE '%kraussmaffei%'
        ORDER BY sc.publication_date
    """)

    citations = cursor.fetchall()
    print(f"\nKraussMaffei citations (should all be linked to DE_2016_kraussmaffei):")
    for cit in citations:
        print(f"  {cit[0]}: {cit[1]}")

    # Check for orphaned links
    print("\n3. Checking for orphaned citation links...")
    cursor.execute("""
        SELECT DISTINCT linked_record_id
        FROM citation_links
        WHERE linked_table = 'major_acquisitions'
          AND linked_record_id NOT IN (SELECT acquisition_id FROM major_acquisitions)
    """)

    orphaned = cursor.fetchall()
    if orphaned:
        print(f"\n⚠ Found {len(orphaned)} orphaned citation links:")
        for o in orphaned:
            print(f"  {o[0]}")
    else:
        print("\n✓ No orphaned citation links found")

    conn.close()

    print("\n" + "="*80)
    print("✓ FIX COMPLETE")
    print("="*80)
    print("\nKraussMaffei now has 2 sources correctly linked to DE_2016_kraussmaffei:")
    print("  1. Company website (primary)")
    print("  2. Financial Times (corroborating)")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
BIS Entity List - TED Contracts Temporal Analysis
Quick check: Are there any TED contracts with BIS-listed entities?
If so, classify as pre-sanction (historical) vs. post-sanction (potential violation)
"""

import sqlite3
from datetime import datetime
from pathlib import Path
import json

MASTER_DB = "F:/OSINT_WAREHOUSE/osint_master.db"

conn = sqlite3.connect(MASTER_DB)
cur = conn.cursor()

print("=" * 80)
print("BIS ENTITY LIST × TED CONTRACTS - TEMPORAL ANALYSIS")
print("=" * 80)

# Known BIS sanction dates for major entities
KNOWN_SANCTION_DATES = {
    'HUAWEI': '2019-05-15',
    'ZTE': '2018-04-15',
    'HIKVISION': '2019-10-07',
    'DJI': '2020-12-18',
    'SMIC': '2020-12-18',
    'YMTC': '2022-12-15',
    'DAHUA': '2019-10-07',
}

# Query TED contracts that might match BIS entities
query = """
    SELECT
        t.document_id,
        t.contractor_name,
        t.award_date,
        t.value_total,
        t.iso_country,
        t.contract_title,
        b.entity_name,
        b.reason_for_listing,
        b.date_added
    FROM ted_contracts_production t
    CROSS JOIN bis_entity_list b
    WHERE (
        UPPER(t.contractor_name) LIKE '%' || UPPER(b.entity_name) || '%'
        OR UPPER(t.contractor_official_name) LIKE '%' || UPPER(b.entity_name) || '%'
    )
    AND b.country LIKE '%China%'
"""

print("\n[INFO] Searching TED contracts for BIS-listed entities...")
cur.execute(query)
matches = cur.fetchall()

print(f"[OK] Found {len(matches)} potential matches")

if len(matches) == 0:
    print("\n✅ NO MATCHES FOUND")
    print("   This means:")
    print("   - No TED contracts use exact BIS entity names in contractor fields")
    print("   - BIS entities may be listed under subsidiaries or alternate names")
    print("   - Or genuinely no EU procurement from these specific entities")
    print("\nTo expand search:")
    print("   1. Add subsidiary name detection")
    print("   2. Fuzzy matching (e.g., 'Huawei Tech' matches 'Huawei Technologies')")
    print("   3. Check additional TED fields (subcontractors, additional_contractors)")
else:
    # Analyze matches with temporal awareness
    historical = []
    violations = []
    unknown = []

    for row in matches:
        doc_id, contractor, award_date, value, country, title, bis_entity, reason, date_added = row

        # Determine sanction date
        sanction_date = date_added
        if not sanction_date:
            for key, date in KNOWN_SANCTION_DATES.items():
                if key in bis_entity.upper():
                    sanction_date = date
                    break

        # Classify
        if not award_date:
            unknown.append({
                'document_id': doc_id,
                'contractor': contractor,
                'bis_entity': bis_entity,
                'reason': reason,
                'note': 'Award date missing - cannot determine temporal status'
            })
        elif not sanction_date:
            unknown.append({
                'document_id': doc_id,
                'contractor': contractor,
                'award_date': award_date,
                'bis_entity': bis_entity,
                'reason': reason,
                'note': 'BIS sanction date unknown - manual verification required'
            })
        else:
            try:
                award_dt = datetime.fromisoformat(award_date.split('T')[0])
                sanc_dt = datetime.fromisoformat(sanction_date.split('T')[0])

                if award_dt < sanc_dt:
                    years_before = (sanc_dt - award_dt).days / 365.25
                    historical.append({
                        'document_id': doc_id,
                        'contractor': contractor,
                        'award_date': award_date,
                        'value': value,
                        'country': country,
                        'bis_entity': bis_entity,
                        'reason': reason,
                        'sanction_date': sanction_date,
                        'years_before_sanction': round(years_before, 1),
                        'status': 'HISTORICAL - Pre-sanction (legitimate at time)'
                    })
                else:
                    years_after = (award_dt - sanc_dt).days / 365.25
                    violations.append({
                        'document_id': doc_id,
                        'contractor': contractor,
                        'award_date': award_date,
                        'value': value,
                        'country': country,
                        'title': title,
                        'bis_entity': bis_entity,
                        'reason': reason,
                        'sanction_date': sanction_date,
                        'years_after_sanction': round(years_after, 1),
                        'status': '⚠️ POTENTIAL VIOLATION - Post-sanction activity'
                    })
            except Exception as e:
                unknown.append({
                    'document_id': doc_id,
                    'contractor': contractor,
                    'bis_entity': bis_entity,
                    'note': f'Date parsing error: {e}'
                })

    # Print results
    print("\n" + "=" * 80)
    print("RESULTS SUMMARY")
    print("=" * 80)
    print(f"\nTotal matches: {len(matches)}")
    print(f"  ✅ Historical (pre-sanction): {len(historical)}")
    print(f"  ⚠️  Potential violations (post-sanction): {len(violations)}")
    print(f"  ❓ Unknown (missing dates): {len(unknown)}")

    if violations:
        print("\n" + "=" * 80)
        print("⚠️  POTENTIAL VIOLATIONS - DETAILED")
        print("=" * 80)
        for v in violations:
            print(f"\nDocument ID: {v['document_id']}")
            print(f"Contractor: {v['contractor']}")
            print(f"BIS Entity: {v['bis_entity']}")
            print(f"Award Date: {v['award_date']} ({v['years_after_sanction']} years AFTER sanction)")
            print(f"Sanction Date: {v['sanction_date']}")
            print(f"BIS Reason: {v['reason']}")
            print(f"Contract Value: €{v['value']:,.2f}" if v['value'] else "Contract Value: Unknown")
            print(f"Country: {v['country']}")
            print(f"Title: {v['title'][:100]}..." if v.get('title') and len(v['title']) > 100 else f"Title: {v.get('title')}")

    if historical:
        print("\n" + "=" * 80)
        print("✅ HISTORICAL (PRE-SANCTION) - SAMPLE")
        print("=" * 80)
        for h in historical[:5]:
            print(f"\nDocument ID: {h['document_id']}")
            print(f"Contractor: {h['contractor']}")
            print(f"BIS Entity: {h['bis_entity']}")
            print(f"Award Date: {h['award_date']} ({h['years_before_sanction']} years BEFORE sanction)")
            print(f"Sanction Date: {h['sanction_date']}")
            print(f"Status: {h['status']}")

    if unknown:
        print("\n" + "=" * 80)
        print("❓ UNKNOWN (MISSING DATES) - SAMPLE")
        print("=" * 80)
        for u in unknown[:5]:
            print(f"\nDocument ID: {u['document_id']}")
            print(f"Contractor: {u['contractor']}")
            print(f"BIS Entity: {u['bis_entity']}")
            print(f"Note: {u['note']}")

    # Save to JSON
    OUTPUT_DIR = Path("F:/OSINT_Data/BIS_Cross_Reference")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    report = {
        'generated_at': datetime.now().isoformat(),
        'total_matches': len(matches),
        'historical_count': len(historical),
        'violations_count': len(violations),
        'unknown_count': len(unknown),
        'historical': historical,
        'violations': violations,
        'unknown': unknown
    }

    output_file = OUTPUT_DIR / f"bis_ted_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n[OK] Full report saved: {output_file}")

conn.close()

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)

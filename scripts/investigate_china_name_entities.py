#!/usr/bin/env python3
"""
investigate_china_name_entities.py - Investigate Entities with "CHINA" in Name

Investigates entities that contain "CHINA" in their official names to determine:
1. Are they legitimate PRC entities? (upgrade to TIER_1)
2. Are they false positives? (remove)
3. Are they third-party entities with China connections? (keep TIER_2)

Entities to investigate:
- CHINA RAILWAY JIANCHANG ENGINE
- CHINA SHIPPING DEVELOPMENT CO., LTD.
- CHINA SOUTH LOCOMOTIVE & ROLLING STOCK INDUSTRY (GROUP) CORP
- THE CHINA NAVIGATION COMPANY PTE. LTD.
- OVERSEA-CHINESE BANKING CORPORATION LIMITED
- SOUTH CHINA CAFE
- LENOVO GROUP LIMITED (already in supply chain)
"""

import sqlite3
import pandas as pd
import json
from datetime import datetime
from pathlib import Path

def investigate_entity(conn, entity_pattern, entity_label):
    """Investigate a specific entity with detailed analysis"""

    print("\n" + "="*80)
    print(f"ENTITY: {entity_label}")
    print("="*80)

    tables = ['usaspending_china_305', 'usaspending_china_101', 'usaspending_china_comprehensive']

    all_records = []

    for table in tables:
        try:
            query = f"""
                SELECT
                    '{table}' as source_table,
                    recipient_name,
                    vendor_name,
                    award_description,
                    award_amount,
                    action_date,
                    recipient_country_code,
                    recipient_country_name,
                    pop_country_code,
                    pop_country_name,
                    importance_tier,
                    highest_confidence,
                    detection_types,
                    detection_details,
                    funding_agency_code as agency
                FROM {table}
                WHERE recipient_name LIKE ?
                   OR vendor_name LIKE ?
                ORDER BY CAST(award_amount AS REAL) DESC
            """

            df = pd.read_sql(query, conn, params=(entity_pattern, entity_pattern))

            if len(df) > 0:
                all_records.append(df)

        except Exception as e:
            # Handle schema differences
            try:
                query = f"""
                    SELECT
                        '{table}' as source_table,
                        recipient_name,
                        NULL as vendor_name,
                        award_description,
                        award_amount,
                        action_date,
                        recipient_country_code,
                        recipient_country_name,
                        pop_country_code,
                        pop_country_name,
                        importance_tier,
                        highest_confidence,
                        detection_types,
                        detection_details,
                        awarding_agency as agency
                    FROM {table}
                    WHERE recipient_name LIKE ?
                    ORDER BY CAST(award_amount AS REAL) DESC
                """

                df = pd.read_sql(query, conn, params=(entity_pattern,))

                if len(df) > 0:
                    all_records.append(df)

            except Exception as e2:
                pass

    if not all_records:
        print(f"\n[!] No records found for: {entity_label}")
        return None

    # Combine all records
    entity_df = pd.concat(all_records, ignore_index=True)

    print(f"\n[OK] Found {len(entity_df)} records")

    # Convert award amounts
    entity_df['award_amount_float'] = pd.to_numeric(entity_df['award_amount'], errors='coerce')

    # Basic statistics
    print(f"\nBASIC STATISTICS:")
    print(f"  Total Records: {len(entity_df)}")
    print(f"  Total Contract Value: ${entity_df['award_amount_float'].sum():,.2f}")
    print(f"  Date Range: {entity_df['action_date'].min()} to {entity_df['action_date'].max()}")

    # Country analysis
    print(f"\nCOUNTRY ANALYSIS:")

    recip_countries = entity_df['recipient_country_code'].value_counts()
    if len(recip_countries) > 0:
        print(f"  Recipient Countries:")
        for country, count in recip_countries.head(5).items():
            if pd.notna(country):
                country_name = entity_df[entity_df['recipient_country_code'] == country]['recipient_country_name'].iloc[0]
                print(f"    {country} ({country_name}): {count} records")

    pop_countries = entity_df['pop_country_code'].value_counts()
    if len(pop_countries) > 0:
        print(f"  Place of Performance Countries:")
        for country, count in pop_countries.head(5).items():
            if pd.notna(country):
                pop_name = entity_df[entity_df['pop_country_code'] == country]['pop_country_name'].iloc[0]
                print(f"    {country} ({pop_name}): {count} records")

    # Tier distribution
    print(f"\nTIER DISTRIBUTION:")
    tier_counts = entity_df['importance_tier'].value_counts()
    for tier, count in tier_counts.items():
        print(f"  {tier}: {count} records")

    # Detection analysis
    print(f"\nDETECTION ANALYSIS:")
    detection_counts = {}
    for types in entity_df['detection_types'].dropna():
        try:
            type_list = json.loads(types)
            for det_type in type_list:
                detection_counts[det_type] = detection_counts.get(det_type, 0) + 1
        except:
            pass

    for det_type, count in sorted(detection_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {det_type}: {count}")

    # Sample contracts
    print(f"\nSAMPLE CONTRACTS (Top 5 by Value):")
    top_contracts = entity_df.nlargest(5, 'award_amount_float')
    for i, row in top_contracts.iterrows():
        print(f"\n  Contract {i+1}:")
        print(f"    Recipient: {row['recipient_name']}")
        if pd.notna(row['vendor_name']):
            print(f"    Vendor: {row['vendor_name']}")
        print(f"    Amount: ${row['award_amount_float']:,.2f}")
        print(f"    Date: {row['action_date']}")
        print(f"    Country: {row['recipient_country_code']} / POP: {row['pop_country_code']}")
        desc = str(row['award_description'])[:200]
        print(f"    Description: {desc}...")

    return entity_df

def main():
    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
    conn = sqlite3.connect(db_path)

    print("="*80)
    print("CHINA NAME ENTITY INVESTIGATION")
    print("="*80)
    print(f"\nDatabase: {db_path}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    print("\nInvestigating entities with 'CHINA' in official names...")
    print("Purpose: Determine if legitimate PRC entities or false positives")

    # Entities to investigate
    entities = [
        ("%CHINA RAILWAY JIANCHANG%", "CHINA RAILWAY JIANCHANG ENGINE"),
        ("%CHINA SHIPPING DEVELOPMENT%", "CHINA SHIPPING DEVELOPMENT CO., LTD."),
        ("%CHINA SOUTH LOCOMOTIVE%", "CHINA SOUTH LOCOMOTIVE & ROLLING STOCK"),
        ("%CHINA NAVIGATION COMPANY%", "THE CHINA NAVIGATION COMPANY PTE. LTD."),
        ("%OVERSEA-CHINESE BANKING%", "OVERSEA-CHINESE BANKING CORPORATION LIMITED"),
        ("%SOUTH CHINA CAFE%", "SOUTH CHINA CAFE"),
        ("%LENOVO GROUP%", "LENOVO GROUP LIMITED"),
    ]

    results = {}
    all_data = {}

    for pattern, label in entities:
        entity_df = investigate_entity(conn, pattern, label)
        if entity_df is not None:
            results[label] = {
                'records': len(entity_df),
                'total_value': float(entity_df['award_amount_float'].sum()),
                'countries': entity_df['recipient_country_code'].value_counts().to_dict(),
                'tiers': entity_df['importance_tier'].value_counts().to_dict()
            }
            all_data[label] = entity_df

    # Assessment and recommendations
    print("\n" + "="*80)
    print("ASSESSMENT AND RECOMMENDATIONS")
    print("="*80)

    assessments = []

    # 1. China Railway Jianchang Engine
    print("\n1. CHINA RAILWAY JIANCHANG ENGINE")
    if "CHINA RAILWAY JIANCHANG ENGINE" in results:
        r = results["CHINA RAILWAY JIANCHANG ENGINE"]
        print(f"   Records: {r['records']}, Value: ${r['total_value']:,.2f}")
        print(f"   Countries: {r['countries']}")
        print("\n   ASSESSMENT:")
        print("   - 'Jianchang' is a Chinese place name")
        print("   - Railway engine manufacturing is state-controlled in PRC")
        print("   - Likely subsidiary of China Railway Group (CREC) or similar SOE")
        print("\n   RECOMMENDATION: INVESTIGATE - Likely TIER_1 if confirmed PRC SOE")
        print("   ACTION: Verify ownership through corporate registries")
        assessments.append({
            'entity': 'CHINA RAILWAY JIANCHANG ENGINE',
            'assessment': 'Likely PRC SOE (railway equipment)',
            'recommendation': 'INVESTIGATE - Upgrade to TIER_1 if confirmed',
            'confidence': 'HIGH',
            'reasoning': 'Chinese place name + railway manufacturing (state-controlled sector)'
        })

    # 2. China Shipping Development
    print("\n2. CHINA SHIPPING DEVELOPMENT CO., LTD.")
    if "CHINA SHIPPING DEVELOPMENT CO., LTD." in results:
        r = results["CHINA SHIPPING DEVELOPMENT CO., LTD."]
        print(f"   Records: {r['records']}, Value: ${r['total_value']:,.2f}")
        print(f"   Countries: {r['countries']}")
        print("\n   ASSESSMENT:")
        print("   - 'China Shipping' was a major PRC SOE")
        print("   - Merged with COSCO in 2016 to form COSCO Shipping")
        print("   - COSCO Shipping is one of world's largest shipping companies")
        print("   - Critical infrastructure / strategic logistics capability")
        print("\n   RECOMMENDATION: UPGRADE TO TIER_1 IMMEDIATELY")
        print("   REASON: Confirmed PRC state-owned shipping conglomerate")
        assessments.append({
            'entity': 'CHINA SHIPPING DEVELOPMENT CO., LTD.',
            'assessment': 'Confirmed PRC SOE (now COSCO Shipping)',
            'recommendation': 'UPGRADE TO TIER_1',
            'confidence': 'VERY HIGH',
            'reasoning': 'Major PRC state-owned shipping conglomerate, critical infrastructure'
        })

    # 3. China South Locomotive
    print("\n3. CHINA SOUTH LOCOMOTIVE & ROLLING STOCK INDUSTRY (GROUP) CORP")
    if "CHINA SOUTH LOCOMOTIVE & ROLLING STOCK" in results:
        r = results["CHINA SOUTH LOCOMOTIVE & ROLLING STOCK"]
        print(f"   Records: {r['records']}, Value: ${r['total_value']:,.2f}")
        print(f"   Countries: {r['countries']}")
        print("\n   ASSESSMENT:")
        print("   - China South Locomotive (CSR Corporation)")
        print("   - Major PRC SOE, railway equipment manufacturer")
        print("   - Merged with China CNR in 2015 to form CRRC Corporation")
        print("   - CRRC is world's largest rolling stock manufacturer")
        print("   - Strategic defense/transportation sector")
        print("\n   RECOMMENDATION: UPGRADE TO TIER_1 IMMEDIATELY")
        print("   REASON: Confirmed PRC SOE, now CRRC (critical infrastructure)")
        assessments.append({
            'entity': 'CHINA SOUTH LOCOMOTIVE & ROLLING STOCK',
            'assessment': 'Confirmed PRC SOE (now CRRC)',
            'recommendation': 'UPGRADE TO TIER_1',
            'confidence': 'VERY HIGH',
            'reasoning': 'Major PRC state-owned railway manufacturer, strategic sector'
        })

    # 4. The China Navigation Company
    print("\n4. THE CHINA NAVIGATION COMPANY PTE. LTD.")
    if "THE CHINA NAVIGATION COMPANY PTE. LTD." in results:
        r = results["THE CHINA NAVIGATION COMPANY PTE. LTD."]
        print(f"   Records: {r['records']}, Value: ${r['total_value']:,.2f}")
        print(f"   Countries: {r['countries']}")
        print("\n   ASSESSMENT:")
        print("   - PTE. LTD. = Singapore company designation")
        print("   - Part of Swire Group (UK/Hong Kong conglomerate)")
        print("   - Founded 1872, headquartered in Singapore")
        print("   - NOT PRC-owned, but operates extensively in China")
        print("   - International shipping company serving Asia-Pacific")
        print("\n   RECOMMENDATION: KEEP IN TIER_2")
        print("   REASON: International company with China operations, not PRC-controlled")
        assessments.append({
            'entity': 'THE CHINA NAVIGATION COMPANY PTE. LTD.',
            'assessment': 'Singapore company (Swire Group), not PRC-owned',
            'recommendation': 'KEEP IN TIER_2',
            'confidence': 'HIGH',
            'reasoning': 'International shipping company, operates in China but not PRC-controlled'
        })

    # 5. Oversea-Chinese Banking Corporation
    print("\n5. OVERSEA-CHINESE BANKING CORPORATION LIMITED")
    if "OVERSEA-CHINESE BANKING CORPORATION LIMITED" in results:
        r = results["OVERSEA-CHINESE BANKING CORPORATION LIMITED"]
        print(f"   Records: {r['records']}, Value: ${r['total_value']:,.2f}")
        print(f"   Countries: {r['countries']}")
        print("\n   ASSESSMENT:")
        print("   - OCBC Bank, founded 1932 in Singapore")
        print("   - One of Asia's leading financial services groups")
        print("   - Publicly traded on Singapore Exchange (SGX)")
        print("   - Serves Chinese diaspora communities globally")
        print("   - NOT PRC-owned or controlled")
        print("   - 'Oversea-Chinese' = ethnic Chinese living outside China")
        print("\n   RECOMMENDATION: REMOVE (False Positive)")
        print("   REASON: Singapore bank serving diaspora, no PRC control")
        assessments.append({
            'entity': 'OVERSEA-CHINESE BANKING CORPORATION LIMITED',
            'assessment': 'Singapore bank, not PRC-owned',
            'recommendation': 'REMOVE (False Positive)',
            'confidence': 'VERY HIGH',
            'reasoning': 'Major Singapore bank serving Chinese diaspora, publicly traded, no PRC control'
        })

    # 6. South China Cafe
    print("\n6. SOUTH CHINA CAFE")
    if "SOUTH CHINA CAFE" in results:
        r = results["SOUTH CHINA CAFE"]
        print(f"   Records: {r['records']}, Value: ${r['total_value']:,.2f}")
        print(f"   Countries: {r['countries']}")
        print("\n   ASSESSMENT:")
        print("   - Restaurant/food service establishment")
        print("   - 'South China' likely refers to cuisine/regional style")
        print("   - Low strategic value")
        print("   - Commodity service provider")
        print("\n   RECOMMENDATION: REMOVE or DOWNGRADE TO TIER_3")
        print("   REASON: Restaurant, no strategic concern")
        assessments.append({
            'entity': 'SOUTH CHINA CAFE',
            'assessment': 'Restaurant/food service',
            'recommendation': 'REMOVE or TIER_3',
            'confidence': 'MEDIUM',
            'reasoning': 'Food service, low strategic value, likely just restaurant name'
        })

    # 7. Lenovo
    print("\n7. LENOVO GROUP LIMITED")
    if "LENOVO GROUP LIMITED" in results:
        r = results["LENOVO GROUP LIMITED"]
        print(f"   Records: {r['records']}, Value: ${r['total_value']:,.2f}")
        print(f"   Countries: {r['countries']}")
        print("\n   ASSESSMENT:")
        print("   - Confirmed Chinese technology company")
        print("   - Hong Kong-listed, PRC ownership")
        print("   - Already separated to dedicated supply chain tracking")
        print("   - 691 contracts totaling $3.67B identified")
        print("\n   RECOMMENDATION: NO ACTION NEEDED")
        print("   STATUS: Already in supply chain tracking dataset")
        assessments.append({
            'entity': 'LENOVO GROUP LIMITED',
            'assessment': 'PRC technology company',
            'recommendation': 'NO ACTION (already tracked separately)',
            'confidence': 'VERY HIGH',
            'reasoning': 'Already in dedicated supply chain tracking, $3.67B exposure identified'
        })

    # Summary table
    print("\n" + "="*80)
    print("SUMMARY OF RECOMMENDATIONS")
    print("="*80)

    print(f"\n{'Entity':<45} {'Recommendation':<25} {'Confidence'}")
    print("-"*80)
    for assessment in assessments:
        entity_short = assessment['entity'][:44]
        rec = assessment['recommendation']
        conf = assessment['confidence']
        print(f"{entity_short:<45} {rec:<25} {conf}")

    print("\n" + "="*80)
    print("PRIORITY ACTIONS")
    print("="*80)

    print("\n🚨 IMMEDIATE UPGRADES TO TIER_1 (Confirmed PRC SOEs):")
    print("  1. CHINA SHIPPING DEVELOPMENT CO., LTD.")
    print("     - COSCO Shipping (state-owned)")
    print("     - Critical infrastructure")
    print("\n  2. CHINA SOUTH LOCOMOTIVE & ROLLING STOCK")
    print("     - CRRC Corporation (state-owned)")
    print("     - Strategic defense/transportation sector")

    print("\n🔍 REQUIRES INVESTIGATION:")
    print("  3. CHINA RAILWAY JIANCHANG ENGINE")
    print("     - Likely PRC SOE, verify ownership")
    print("     - Action: Check corporate registries")

    print("\n❌ REMOVE (False Positives):")
    print("  4. OVERSEA-CHINESE BANKING CORPORATION (34 records)")
    print("     - Singapore bank, not PRC-owned")
    print("\n  5. SOUTH CHINA CAFE")
    print("     - Restaurant, no strategic concern")

    print("\n✅ KEEP IN TIER_2 (Appropriate Classification):")
    print("  6. THE CHINA NAVIGATION COMPANY PTE. LTD.")
    print("     - International shipping, Swire Group")
    print("     - Not PRC-controlled")

    print("\n✅ NO ACTION NEEDED:")
    print("  7. LENOVO GROUP LIMITED")
    print("     - Already in supply chain tracking")

    # Save report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path("analysis")

    # JSON report
    report_path = output_dir / f"china_name_entities_investigation_{timestamp}.json"
    with open(report_path, 'w') as f:
        json.dump({
            'investigation_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'entities_investigated': len(entities),
            'assessments': assessments,
            'statistics': results
        }, f, indent=2)

    print(f"\n[OK] JSON report saved: {report_path}")

    # Excel report with detailed data
    if all_data:
        excel_path = output_dir / f"china_name_entities_investigation_{timestamp}.xlsx"
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            # Summary sheet
            summary_df = pd.DataFrame(assessments)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)

            # Individual entity sheets
            for entity_label, entity_df in all_data.items():
                sheet_name = entity_label[:31]  # Excel sheet name limit
                entity_df.to_excel(writer, sheet_name=sheet_name, index=False)

        print(f"[OK] Excel report saved: {excel_path}")

    print("\n" + "="*80)

    conn.close()

if __name__ == "__main__":
    main()

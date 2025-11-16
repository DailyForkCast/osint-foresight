#!/usr/bin/env python3
"""
create_lenovo_tracking_dataset.py - Lenovo Tracking Dataset

Creates comprehensive tracking dataset for all Lenovo contracts across all tiers.
Tracks $3.6B+ in Lenovo government contracts with detailed categorization.
"""

import sqlite3
import pandas as pd
from datetime import datetime
from pathlib import Path
import json

def create_lenovo_dataset():
    """Extract and analyze all Lenovo contracts"""

    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("="*60)
    print("LENOVO TRACKING DATASET CREATION")
    print("="*60)
    print(f"\nDatabase: {db_path}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Extract all Lenovo contracts
    tables = ['usaspending_china_305', 'usaspending_china_101', 'usaspending_china_comprehensive']

    all_lenovo = []

    for table in tables:
        print(f"\n[{table}]")

        try:
            query = f"""
                SELECT
                    recipient_name,
                    vendor_name,
                    award_description,
                    award_amount,
                    action_date,
                    importance_tier,
                    highest_confidence,
                    funding_agency_code as agency,
                    '{table}' as source_table
                FROM {table}
                WHERE recipient_name LIKE '%LENOVO%'
                   OR vendor_name LIKE '%LENOVO%'
                ORDER BY CAST(award_amount AS REAL) DESC
            """

            df = pd.read_sql(query, conn)
            all_lenovo.append(df)
            print(f"  Found {len(df)} Lenovo contracts")

        except Exception as e:
            # Handle tables with different schemas
            try:
                query = f"""
                    SELECT
                        recipient_name,
                        NULL as vendor_name,
                        award_description,
                        award_amount,
                        action_date,
                        importance_tier,
                        highest_confidence,
                        awarding_agency as agency,
                        '{table}' as source_table
                    FROM {table}
                    WHERE recipient_name LIKE '%LENOVO%'
                    ORDER BY CAST(award_amount AS REAL) DESC
                """

                df = pd.read_sql(query, conn)
                all_lenovo.append(df)
                print(f"  Found {len(df)} Lenovo contracts")

            except Exception as e2:
                print(f"  Error: {e2}")

    # Combine all Lenovo contracts
    if not all_lenovo:
        print("\n[!] No Lenovo contracts found")
        conn.close()
        return

    lenovo_df = pd.concat(all_lenovo, ignore_index=True)

    print(f"\n{'='*60}")
    print(f"TOTAL LENOVO CONTRACTS: {len(lenovo_df)}")
    print(f"{'='*60}")

    # Categorization
    def categorize_contract(row):
        """Categorize Lenovo contract by type and risk"""

        desc = str(row['award_description']).lower()
        name = str(row['recipient_name']).lower()
        amount = float(row['award_amount']) if row['award_amount'] else 0

        # Product categories
        if any(kw in desc for kw in ['laptop', 'notebook', 'thinkpad']):
            product = 'LAPTOP'
        elif any(kw in desc for kw in ['desktop', 'computer', 'pc', 'workstation']):
            product = 'DESKTOP'
        elif any(kw in desc for kw in ['server', 'datacenter', 'rack']):
            product = 'SERVER'
        elif any(kw in desc for kw in ['tablet', 'ipad']):
            product = 'TABLET'
        elif any(kw in desc for kw in ['monitor', 'display', 'screen']):
            product = 'MONITOR'
        elif any(kw in desc for kw in ['storage', 'hard drive', 'disk', 'ssd']):
            product = 'STORAGE'
        elif any(kw in desc for kw in ['network', 'switch', 'router']):
            product = 'NETWORKING'
        else:
            product = 'OTHER_IT'

        # Risk assessment
        if any(kw in desc for kw in ['classified', 'secret', 'secure', 'dod', 'intelligence']):
            risk = 'HIGH'
            concern = 'Classified/sensitive systems'
        elif any(kw in desc for kw in ['server', 'datacenter', 'infrastructure', 'network']):
            risk = 'MEDIUM'
            concern = 'Infrastructure/data security'
        elif amount > 1000000:
            risk = 'MEDIUM'
            concern = 'High-value contract'
        else:
            risk = 'LOW'
            concern = 'Commodity IT purchase'

        # Strategic concerns
        if 'server' in desc or 'datacenter' in desc:
            strategic = 'Data access potential'
        elif 'network' in desc:
            strategic = 'Network infrastructure access'
        elif any(kw in desc for kw in ['dod', 'defense', 'military']):
            strategic = 'Military/defense use'
        else:
            strategic = 'None apparent'

        return pd.Series({
            'product_category': product,
            'risk_level': risk,
            'risk_concern': concern,
            'strategic_concern': strategic
        })

    # Apply categorization
    categorization = lenovo_df.apply(categorize_contract, axis=1)
    lenovo_df = pd.concat([lenovo_df, categorization], axis=1)

    # Convert amounts
    lenovo_df['award_amount_float'] = pd.to_numeric(lenovo_df['award_amount'], errors='coerce')

    # Extract year
    lenovo_df['year'] = pd.to_datetime(lenovo_df['action_date'], errors='coerce').dt.year

    # Generate Excel report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path("analysis")
    output_dir.mkdir(exist_ok=True)

    excel_path = output_dir / f"lenovo_tracking_dataset_{timestamp}.xlsx"

    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        # Summary sheet
        summary_data = {
            'Metric': [
                'Total Contracts',
                'Total Value',
                'HIGH Risk Contracts',
                'MEDIUM Risk Contracts',
                'LOW Risk Contracts',
                'Earliest Contract',
                'Latest Contract',
                'Unique Agencies',
                'Date Created'
            ],
            'Value': [
                len(lenovo_df),
                f"${lenovo_df['award_amount_float'].sum():,.2f}",
                len(lenovo_df[lenovo_df['risk_level'] == 'HIGH']),
                len(lenovo_df[lenovo_df['risk_level'] == 'MEDIUM']),
                len(lenovo_df[lenovo_df['risk_level'] == 'LOW']),
                lenovo_df['year'].min() if lenovo_df['year'].notna().any() else 'N/A',
                lenovo_df['year'].max() if lenovo_df['year'].notna().any() else 'N/A',
                lenovo_df['agency'].nunique(),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ]
        }
        pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)

        # All contracts
        lenovo_df.to_excel(writer, sheet_name='All Contracts', index=False)

        # By risk level
        risk_summary = lenovo_df.groupby('risk_level').agg({
            'award_amount_float': ['count', 'sum'],
            'recipient_name': 'count'
        }).reset_index()
        risk_summary.columns = ['Risk Level', 'Contract Count', 'Total Value', 'Entity Count']
        risk_summary.to_excel(writer, sheet_name='By Risk Level', index=False)

        # HIGH risk contracts
        high_risk = lenovo_df[lenovo_df['risk_level'] == 'HIGH']
        if len(high_risk) > 0:
            high_risk.to_excel(writer, sheet_name='HIGH Risk Contracts', index=False)

        # MEDIUM risk contracts
        med_risk = lenovo_df[lenovo_df['risk_level'] == 'MEDIUM']
        if len(med_risk) > 0:
            med_risk.to_excel(writer, sheet_name='MEDIUM Risk Contracts', index=False)

        # By product category
        product_summary = lenovo_df.groupby('product_category').agg({
            'award_amount_float': ['count', 'sum']
        }).reset_index()
        product_summary.columns = ['Product Category', 'Contract Count', 'Total Value']
        product_summary.to_excel(writer, sheet_name='By Product', index=False)

        # Temporal analysis
        if lenovo_df['year'].notna().any():
            temporal = lenovo_df.groupby('year').agg({
                'award_amount_float': ['count', 'sum']
            }).reset_index()
            temporal.columns = ['Year', 'Contract Count', 'Total Value']
            temporal.to_excel(writer, sheet_name='Temporal Trend', index=False)

        # By agency
        agency_summary = lenovo_df.groupby('agency').agg({
            'award_amount_float': ['count', 'sum']
        }).reset_index()
        agency_summary.columns = ['Agency', 'Contract Count', 'Total Value']
        agency_summary = agency_summary.sort_values('Total Value', ascending=False)
        agency_summary.to_excel(writer, sheet_name='By Agency', index=False)

        # By importance tier
        tier_summary = lenovo_df.groupby('importance_tier').agg({
            'award_amount_float': ['count', 'sum']
        }).reset_index()
        tier_summary.columns = ['Importance Tier', 'Contract Count', 'Total Value']
        tier_summary.to_excel(writer, sheet_name='By Importance Tier', index=False)

    print(f"\n[OK] Excel report saved: {excel_path}")

    # JSON report
    json_path = output_dir / f"lenovo_tracking_dataset_{timestamp}.json"

    report = {
        'extraction_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'total_contracts': len(lenovo_df),
        'total_value': float(lenovo_df['award_amount_float'].sum()),
        'risk_breakdown': lenovo_df['risk_level'].value_counts().to_dict(),
        'product_breakdown': lenovo_df['product_category'].value_counts().to_dict(),
        'tier_breakdown': lenovo_df['importance_tier'].value_counts().to_dict(),
        'contracts': lenovo_df.to_dict('records')
    }

    with open(json_path, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"[OK] JSON report saved: {json_path}")

    # Print summary
    print("\n" + "="*60)
    print("LENOVO TRACKING DATASET SUMMARY")
    print("="*60)

    print(f"\nTotal Lenovo contracts: {len(lenovo_df)}")
    print(f"Total contract value: ${lenovo_df['award_amount_float'].sum():,.2f}")

    print("\nBy Risk Level:")
    for risk, count in lenovo_df['risk_level'].value_counts().items():
        value = lenovo_df[lenovo_df['risk_level'] == risk]['award_amount_float'].sum()
        print(f"  {risk}: {count} contracts (${value:,.2f})")

    print("\nBy Product Category:")
    for product, count in lenovo_df['product_category'].value_counts().head(5).items():
        value = lenovo_df[lenovo_df['product_category'] == product]['award_amount_float'].sum()
        print(f"  {product}: {count} contracts (${value:,.2f})")

    print("\nBy Importance Tier:")
    for tier, count in lenovo_df['importance_tier'].value_counts().items():
        value = lenovo_df[lenovo_df['importance_tier'] == tier]['award_amount_float'].sum()
        print(f"  {tier}: {count} contracts (${value:,.2f})")

    print("\nTop 5 Agencies by Contract Value:")
    top_agencies = lenovo_df.groupby('agency')['award_amount_float'].sum().nlargest(5)
    for agency, value in top_agencies.items():
        count = len(lenovo_df[lenovo_df['agency'] == agency])
        print(f"  {agency}: ${value:,.2f} ({count} contracts)")

    print("\nTemporal Distribution:")
    if lenovo_df['year'].notna().any():
        yearly = lenovo_df.groupby('year')['award_amount_float'].sum().sort_index()
        for year, value in yearly.tail(5).items():
            count = len(lenovo_df[lenovo_df['year'] == year])
            print(f"  {int(year)}: ${value:,.2f} ({count} contracts)")

    print("\n" + "="*60)
    print("KEY FINDINGS")
    print("="*60)

    high_risk_count = len(lenovo_df[lenovo_df['risk_level'] == 'HIGH'])
    med_risk_count = len(lenovo_df[lenovo_df['risk_level'] == 'MEDIUM'])

    if high_risk_count > 0:
        print(f"\n[!] {high_risk_count} HIGH RISK contracts found:")
        print("    - Classified/sensitive systems")
        print("    - Requires immediate review")

    if med_risk_count > 0:
        print(f"\n[!] {med_risk_count} MEDIUM RISK contracts found:")
        print("    - Infrastructure/data security concerns")
        print("    - High-value contracts")

    # Strategic concerns
    strategic = lenovo_df[lenovo_df['strategic_concern'] != 'None apparent']
    if len(strategic) > 0:
        print(f"\n[!] {len(strategic)} contracts with strategic concerns:")
        for concern in strategic['strategic_concern'].unique():
            count = len(strategic[strategic['strategic_concern'] == concern])
            print(f"    - {concern}: {count} contracts")

    print("\n" + "="*60)

    conn.close()

    return excel_path, json_path

if __name__ == "__main__":
    create_lenovo_dataset()

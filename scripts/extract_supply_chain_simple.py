#!/usr/bin/env python3
"""
extract_supply_chain_simple.py - Extract Supply Chain Entities (Simple)

Extracts the 702 entities marked as 'SUPPLY_CHAIN' during TIER_2 reprocessing
and generates Excel/JSON reports.

Usage:
    python extract_supply_chain_simple.py
"""

import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime
import json

def extract_supply_chain_entities():
    """Extract marked supply chain entities to reports"""

    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
    conn = sqlite3.connect(db_path)

    print("=" * 60)
    print("SUPPLY CHAIN ENTITY EXTRACTION")
    print("=" * 60)
    print(f"\nDatabase: {db_path}")
    print("Extracting 702 entities marked during TIER_2 reprocessing")

    # Extract from 305 table (has vendor_name)
    print("\n[usaspending_china_305]")

    # Count supply chain entities
    count_query = """
        SELECT COUNT(*) as count
        FROM usaspending_china_305
        WHERE commodity_type = 'SUPPLY_CHAIN'
    """

    count = pd.read_sql(count_query, conn)['count'].iloc[0]
    print(f"  Found {count} supply chain records")

    # Extract supply chain entities with aggregation
    extract_query = """
        SELECT
            recipient_name as entity_name,
            vendor_name,
            COUNT(*) as contract_count,
            SUM(CAST(award_amount AS REAL)) as total_value,
            MIN(action_date) as first_seen,
            MAX(action_date) as last_seen,
            'usaspending_china_305' as source_table
        FROM usaspending_china_305
        WHERE commodity_type = 'SUPPLY_CHAIN'
        GROUP BY recipient_name, vendor_name
        ORDER BY total_value DESC
    """

    entities_df = pd.read_sql(extract_query, conn)

    print(f"  Unique entities: {len(entities_df)}")
    print(f"  Total contract value: ${entities_df['total_value'].sum():,.2f}")

    # Categorize entities
    def categorize_entity(name, vendor):
        text = f"{name} {vendor}".lower()

        if 'lenovo' in text:
            return 'IT_EQUIPMENT', 'MEDIUM'
        elif 'huawei' in text:
            return 'TELECOMMUNICATIONS', 'HIGH'
        elif 'zte' in text:
            return 'TELECOMMUNICATIONS', 'HIGH'
        elif 'tp-link' in text or 'tplink' in text:
            return 'NETWORKING', 'MEDIUM'
        elif any(x in text for x in ['haier', 'hisense', 'tcl']):
            return 'CONSUMER_ELECTRONICS', 'LOW'
        elif 'xiaomi' in text:
            return 'CONSUMER_ELECTRONICS', 'MEDIUM'
        elif 'hikvision' in text or 'dahua' in text:
            return 'SURVEILLANCE', 'HIGH'
        elif 'dji' in text:
            return 'DRONES', 'MEDIUM'
        else:
            return 'OTHER', 'MEDIUM'

    entities_df['category'] = entities_df.apply(
        lambda row: categorize_entity(row['entity_name'], row['vendor_name'])[0], axis=1
    )
    entities_df['risk_level'] = entities_df.apply(
        lambda row: categorize_entity(row['entity_name'], row['vendor_name'])[1], axis=1
    )

    # Generate Excel report
    print("\n[OK] Generating Excel report...")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path("analysis")
    output_dir.mkdir(exist_ok=True)

    excel_path = output_dir / f"supply_chain_extraction_{timestamp}.xlsx"

    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        # Summary sheet
        summary_data = {
            'Metric': [
                'Total Supply Chain Records',
                'Unique Entities',
                'Total Contract Value',
                'Extraction Date'
            ],
            'Value': [
                count,
                len(entities_df),
                f"${entities_df['total_value'].sum():,.2f}",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ]
        }
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)

        # All entities
        entities_df.to_excel(writer, sheet_name='All Entities', index=False)

        # By category
        category_summary = entities_df.groupby('category').agg({
            'contract_count': 'sum',
            'total_value': 'sum',
            'entity_name': 'count'
        }).reset_index()
        category_summary.columns = ['Category', 'Total Contracts', 'Total Value', 'Entity Count']
        category_summary.to_excel(writer, sheet_name='By Category', index=False)

        # By risk level
        risk_summary = entities_df.groupby('risk_level').agg({
            'contract_count': 'sum',
            'total_value': 'sum',
            'entity_name': 'count'
        }).reset_index()
        risk_summary.columns = ['Risk Level', 'Total Contracts', 'Total Value', 'Entity Count']
        risk_summary.to_excel(writer, sheet_name='By Risk Level', index=False)

        # High risk entities only
        high_risk = entities_df[entities_df['risk_level'] == 'HIGH']
        if len(high_risk) > 0:
            high_risk.to_excel(writer, sheet_name='High Risk Entities', index=False)

    print(f"[OK] Excel report saved: {excel_path}")

    # Generate JSON report
    json_path = output_dir / f"supply_chain_extraction_{timestamp}.json"

    report = {
        'extraction_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'total_records': int(count),
        'unique_entities': len(entities_df),
        'total_value': float(entities_df['total_value'].sum()),
        'by_category': category_summary.to_dict(orient='records'),
        'by_risk': risk_summary.to_dict(orient='records'),
        'entities': entities_df.to_dict(orient='records')
    }

    with open(json_path, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"[OK] JSON report saved: {json_path}")

    # Summary
    print("\n" + "=" * 60)
    print("SUPPLY CHAIN EXTRACTION COMPLETE")
    print("=" * 60)

    print(f"\nTotal supply chain records: {count}")
    print(f"Unique entities extracted: {len(entities_df)}")
    print(f"Total contract value: ${entities_df['total_value'].sum():,.2f}")

    print("\nBy Category:")
    for _, row in category_summary.iterrows():
        print(f"  {row['Category']}: {row['Entity Count']} entities, ${row['Total Value']:,.2f}")

    print("\nBy Risk Level:")
    for _, row in risk_summary.iterrows():
        print(f"  {row['Risk Level']}: {row['Entity Count']} entities, ${row['Total Value']:,.2f}")

    print("\nTop 10 Entities by Contract Value:")
    top_entities = entities_df.nlargest(10, 'total_value')
    for _, row in top_entities.iterrows():
        print(f"  {row['entity_name']}: ${row['total_value']:,.2f} ({row['contract_count']} contracts)")

    print("\n" + "=" * 60)
    print(f"\nExcel report: {excel_path}")
    print(f"JSON report: {json_path}")
    print("\n" + "=" * 60)

    conn.close()
    return excel_path, json_path

if __name__ == "__main__":
    extract_supply_chain_entities()

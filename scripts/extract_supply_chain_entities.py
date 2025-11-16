#!/usr/bin/env python3
"""
extract_supply_chain_entities.py - Extract Supply Chain Entities

Extracts the 702 entities marked as 'SUPPLY_CHAIN' during TIER_2 reprocessing
and populates the supply_chain_entities table.

Usage:
    python extract_supply_chain_entities.py
"""

import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime
import json

def extract_supply_chain_entities():
    """Extract marked supply chain entities to dedicated tracker"""

    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("=" * 60)
    print("SUPPLY CHAIN ENTITY EXTRACTION")
    print("=" * 60)
    print(f"\nDatabase: {db_path}")
    print("Extracting 702 entities marked during TIER_2 reprocessing")

    # Check if supply_chain_entities table exists
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='supply_chain_entities'
    """)

    if not cursor.fetchone():
        print("\n[!] Creating supply_chain_entities table...")
        cursor.execute("""
            CREATE TABLE supply_chain_entities (
                entity_id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_name TEXT,
                vendor_name TEXT,
                contract_count INTEGER,
                total_value REAL,
                category TEXT,
                risk_level TEXT,
                source_table TEXT,
                first_seen DATE,
                last_seen DATE,
                notes TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        print("[OK] Table created")

    # Extract from each table
    # Using 305 table only (has vendor_name column)
    tables_info = [
        ('usaspending_china_305', 'recipient_name', 'vendor_name', 'award_description',
         'award_amount', 'action_date', 'commodity_type'),
    ]

    all_entities = []
    extraction_stats = {}

    for table_name, recip_col, vendor_col, desc_col, amount_col, date_col, comm_col in tables_info:
        print(f"\n[{table_name}]")

        # Count supply chain entities
        count_query = f"""
            SELECT COUNT(*) as count
            FROM {table_name}
            WHERE {comm_col} = 'SUPPLY_CHAIN'
        """

        count = pd.read_sql(count_query, conn)['count'].iloc[0]
        print(f"  Found {count} supply chain records")

        if count == 0:
            continue

        # Extract supply chain entities with aggregation
        extract_query = f"""
            SELECT
                {recip_col} as entity_name,
                {vendor_col} as vendor_name,
                COUNT(*) as contract_count,
                SUM(CAST({amount_col} AS REAL)) as total_value,
                MIN({date_col}) as first_seen,
                MAX({date_col}) as last_seen,
                '{table_name}' as source_table
            FROM {table_name}
            WHERE {comm_col} = 'SUPPLY_CHAIN'
            GROUP BY {recip_col}, {vendor_col}
        """

        entities_df = pd.read_sql(extract_query, conn)
        all_entities.append(entities_df)

        extraction_stats[table_name] = {
            'records': count,
            'unique_entities': len(entities_df)
        }

        print(f"  Unique entities: {len(entities_df)}")
        print(f"  Total contract value: ${entities_df['total_value'].sum():,.2f}")

    # Combine entities
    combined_entities = pd.concat(all_entities, ignore_index=True)

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

    combined_entities['category'] = combined_entities.apply(
        lambda row: categorize_entity(row['entity_name'], row['vendor_name'])[0], axis=1
    )
    combined_entities['risk_level'] = combined_entities.apply(
        lambda row: categorize_entity(row['entity_name'], row['vendor_name'])[1], axis=1
    )

    # Insert into supply_chain_entities table
    print("\n[OK] Populating supply_chain_entities table...")

    for _, row in combined_entities.iterrows():
        cursor.execute("""
            INSERT INTO supply_chain_entities
            (entity_name, vendor_name, contract_count, total_value, category,
             risk_level, source_table, first_seen, last_seen)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row['entity_name'],
            row['vendor_name'],
            row['contract_count'],
            row['total_value'],
            row['category'],
            row['risk_level'],
            row['source_table'],
            row['first_seen'],
            row['last_seen']
        ))

    conn.commit()
    print(f"[OK] Inserted {len(combined_entities)} unique entities")

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
                'Tables Processed',
                'Extraction Date'
            ],
            'Value': [
                sum(s['records'] for s in extraction_stats.values()),
                len(combined_entities),
                f"${combined_entities['total_value'].sum():,.2f}",
                len(extraction_stats),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ]
        }
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)

        # All entities
        combined_entities.to_excel(writer, sheet_name='All Entities', index=False)

        # By category
        category_summary = combined_entities.groupby('category').agg({
            'contract_count': 'sum',
            'total_value': 'sum',
            'entity_name': 'count'
        }).reset_index()
        category_summary.columns = ['Category', 'Total Contracts', 'Total Value', 'Entity Count']
        category_summary.to_excel(writer, sheet_name='By Category', index=False)

        # By risk level
        risk_summary = combined_entities.groupby('risk_level').agg({
            'contract_count': 'sum',
            'total_value': 'sum',
            'entity_name': 'count'
        }).reset_index()
        risk_summary.columns = ['Risk Level', 'Total Contracts', 'Total Value', 'Entity Count']
        risk_summary.to_excel(writer, sheet_name='By Risk Level', index=False)

        # High risk entities only
        high_risk = combined_entities[combined_entities['risk_level'] == 'HIGH']
        if len(high_risk) > 0:
            high_risk.to_excel(writer, sheet_name='High Risk Entities', index=False)

    print(f"[OK] Excel report saved: {excel_path}")

    # Generate JSON report
    json_path = output_dir / f"supply_chain_extraction_{timestamp}.json"

    report = {
        'extraction_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'total_records': sum(s['records'] for s in extraction_stats.values()),
        'unique_entities': len(combined_entities),
        'total_value': float(combined_entities['total_value'].sum()),
        'by_table': extraction_stats,
        'by_category': category_summary.to_dict(orient='records'),
        'by_risk': risk_summary.to_dict(orient='records'),
        'entities': combined_entities.to_dict(orient='records')
    }

    with open(json_path, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"[OK] JSON report saved: {json_path}")

    # Summary
    print("\n" + "=" * 60)
    print("SUPPLY CHAIN EXTRACTION COMPLETE")
    print("=" * 60)

    print(f"\nTotal supply chain records: {sum(s['records'] for s in extraction_stats.values())}")
    print(f"Unique entities extracted: {len(combined_entities)}")
    print(f"Total contract value: ${combined_entities['total_value'].sum():,.2f}")

    print("\nBy Category:")
    for _, row in category_summary.iterrows():
        print(f"  {row['Category']}: {row['Entity Count']} entities, ${row['Total Value']:,.2f}")

    print("\nBy Risk Level:")
    for _, row in risk_summary.iterrows():
        print(f"  {row['Risk Level']}: {row['Entity Count']} entities, ${row['Total Value']:,.2f}")

    print("\nTop 10 Entities by Contract Value:")
    top_entities = combined_entities.nlargest(10, 'total_value')
    for _, row in top_entities.iterrows():
        print(f"  {row['entity_name']}: ${row['total_value']:,.2f} ({row['contract_count']} contracts)")

    print("\n" + "=" * 60)
    print(f"\nDatabase table: supply_chain_entities ({len(combined_entities)} records)")
    print(f"Excel report: {excel_path}")
    print(f"JSON report: {json_path}")
    print("\n" + "=" * 60)

    conn.close()
    return excel_path, json_path

if __name__ == "__main__":
    extract_supply_chain_entities()

#!/usr/bin/env python3
"""
map_cosco_relationship.py - Comprehensive COSCO Contract Mapping

Maps all COSCO/China Shipping/China Ocean Shipping contracts across all databases
and creates complete timeline (2000-2025).

Outputs:
- Complete contract list with all details
- Timeline analysis (pre-merger vs. post-merger)
- Agency breakdown
- Geographic distribution
- Value analysis
- Entity lineage tracking
"""

import sqlite3
import pandas as pd
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

class COSCOContractMapper:
    """Map complete COSCO relationship across all data sources"""

    # COSCO entity name variations
    COSCO_PATTERNS = [
        # China Ocean Shipping Company (COSCO Group - pre-2016)
        '%CHINA OCEAN SHIPPING%',
        '%COSCO%',
        '%DALIAN OCEAN SHIPPING%',

        # China Shipping Group (pre-2016)
        '%CHINA SHIPPING%',

        # Post-2016 merged entity
        '%CHINA COSCO SHIPPING%',
        '%COSCO SHIPPING%',
    ]

    # Merger date
    COSCO_MERGER_DATE = '2016-02-18'

    def __init__(self, db_path="F:/OSINT_WAREHOUSE/osint_master.db"):
        self.db_path = db_path
        self.conn = None
        self.all_contracts = []

    def connect(self):
        """Connect to database"""
        self.conn = sqlite3.connect(self.db_path)
        print(f"[OK] Connected to: {self.db_path}")

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print("[OK] Database connection closed")

    def extract_usaspending_305(self):
        """Extract COSCO contracts from 305-column format"""
        print(f"\n{'='*80}")
        print("EXTRACTING: usaspending_china_305")
        print(f"{'='*80}")

        # Build OR conditions for all patterns
        conditions = []
        params = []
        for pattern in self.COSCO_PATTERNS:
            conditions.append("recipient_name LIKE ?")
            params.append(pattern)
            conditions.append("vendor_name LIKE ?")
            params.append(pattern)

        where_clause = " OR ".join(conditions)

        query = f"""
        SELECT
            'usaspending_305' as source_table,
            transaction_id,
            award_id,
            recipient_name,
            vendor_name,
            award_description,
            award_amount,
            action_date,
            recipient_country_code,
            recipient_country_name,
            pop_country_code,
            pop_country_name,
            funding_agency_code,
            importance_tier,
            detection_types,
            detection_details,
            processed_date
        FROM usaspending_china_305
        WHERE {where_clause}
        ORDER BY action_date DESC
        """

        df = pd.read_sql(query, self.conn, params=params)
        print(f"  Found: {len(df)} contracts")

        # Convert to list of dicts
        contracts = df.to_dict('records')
        self.all_contracts.extend(contracts)

        return contracts

    def extract_usaspending_101(self):
        """Extract COSCO contracts from 101-column format (no vendor_name)"""
        print(f"\n{'='*80}")
        print("EXTRACTING: usaspending_china_101")
        print(f"{'='*80}")

        # Only recipient_name (101 format doesn't have vendor_name)
        conditions = []
        params = []
        for pattern in self.COSCO_PATTERNS:
            conditions.append("recipient_name LIKE ?")
            params.append(pattern)

        where_clause = " OR ".join(conditions)

        query = f"""
        SELECT
            'usaspending_101' as source_table,
            transaction_id,
            award_id,
            recipient_name,
            NULL as vendor_name,
            award_description,
            award_amount,
            action_date,
            recipient_country_code,
            recipient_country_name,
            pop_country_code,
            pop_country_name,
            funding_agency_code,
            importance_tier,
            detection_types,
            detection_details,
            processed_date
        FROM usaspending_china_101
        WHERE {where_clause}
        ORDER BY action_date DESC
        """

        try:
            df = pd.read_sql(query, self.conn, params=params)
            print(f"  Found: {len(df)} contracts")

            contracts = df.to_dict('records')
            self.all_contracts.extend(contracts)

            return contracts
        except Exception as e:
            print(f"  [WARNING] Error extracting from 101 table: {e}")
            return []

    def extract_usaspending_comprehensive(self):
        """Extract COSCO contracts from comprehensive format"""
        print(f"\n{'='*80}")
        print("EXTRACTING: usaspending_china_comprehensive")
        print(f"{'='*80}")

        # Check if vendor_name exists in this table
        cursor = self.conn.cursor()
        cursor.execute("PRAGMA table_info(usaspending_china_comprehensive)")
        columns = [col[1] for col in cursor.fetchall()]

        if 'vendor_name' in columns:
            conditions = []
            params = []
            for pattern in self.COSCO_PATTERNS:
                conditions.append("recipient_name LIKE ?")
                params.append(pattern)
                conditions.append("vendor_name LIKE ?")
                params.append(pattern)

            where_clause = " OR ".join(conditions)
            vendor_field = "vendor_name"
        else:
            conditions = []
            params = []
            for pattern in self.COSCO_PATTERNS:
                conditions.append("recipient_name LIKE ?")
                params.append(pattern)

            where_clause = " OR ".join(conditions)
            vendor_field = "NULL"

        query = f"""
        SELECT
            'usaspending_comprehensive' as source_table,
            transaction_id,
            award_id,
            recipient_name,
            {vendor_field} as vendor_name,
            award_description,
            award_amount,
            action_date,
            recipient_country_code,
            recipient_country_name,
            pop_country_code,
            pop_country_name,
            funding_agency_code,
            importance_tier,
            detection_types,
            detection_details,
            processed_date
        FROM usaspending_china_comprehensive
        WHERE {where_clause}
        ORDER BY action_date DESC
        """

        try:
            df = pd.read_sql(query, self.conn, params=params)
            print(f"  Found: {len(df)} contracts")

            contracts = df.to_dict('records')
            self.all_contracts.extend(contracts)

            return contracts
        except Exception as e:
            print(f"  [WARNING] Error extracting from comprehensive table: {e}")
            return []

    def analyze_contracts(self):
        """Analyze all extracted contracts"""
        print(f"\n{'='*80}")
        print("ANALYSIS SUMMARY")
        print(f"{'='*80}")

        if not self.all_contracts:
            print("\nNo COSCO contracts found.")
            return {}

        df = pd.DataFrame(self.all_contracts)

        # Overall stats
        total_contracts = len(df)
        total_value = df['award_amount'].sum()

        # Date range
        df['action_date_parsed'] = pd.to_datetime(df['action_date'], errors='coerce')
        min_date = df['action_date_parsed'].min()
        max_date = df['action_date_parsed'].max()

        # Pre/post merger
        merger_date = pd.to_datetime(self.COSCO_MERGER_DATE)
        pre_merger = df[df['action_date_parsed'] < merger_date]
        post_merger = df[df['action_date_parsed'] >= merger_date]

        # By source table
        by_table = df.groupby('source_table').size()

        # By agency
        by_agency = df.groupby('funding_agency_code').size().sort_values(ascending=False)

        # By tier
        by_tier = df.groupby('importance_tier').size()

        # DPRK contracts
        dprk_contracts = df[df['award_description'].str.contains('DPRK', case=False, na=False)]

        # Print summary
        print(f"\nOVERALL STATISTICS:")
        print(f"  Total Contracts: {total_contracts}")
        print(f"  Total Value: ${total_value:,.2f}")
        print(f"  Date Range: {min_date.strftime('%Y-%m-%d') if pd.notna(min_date) else 'N/A'} to {max_date.strftime('%Y-%m-%d') if pd.notna(max_date) else 'N/A'}")

        print(f"\nPRE/POST MERGER (Feb 18, 2016):")
        print(f"  Pre-Merger: {len(pre_merger)} contracts")
        print(f"  Post-Merger: {len(post_merger)} contracts")

        print(f"\nBY SOURCE TABLE:")
        for table, count in by_table.items():
            print(f"  {table}: {count}")

        print(f"\nBY AGENCY:")
        for agency, count in by_agency.head(10).items():
            agency_str = str(agency) if pd.notna(agency) else 'Unknown'
            print(f"  {agency_str}: {count}")

        print(f"\nBY IMPORTANCE TIER:")
        for tier, count in by_tier.items():
            tier_str = str(tier) if pd.notna(tier) else 'Unknown'
            print(f"  {tier_str}: {count}")

        print(f"\nCRITICAL CONTRACTS:")
        print(f"  DPRK-related: {len(dprk_contracts)} contracts")

        return {
            'total_contracts': total_contracts,
            'total_value': float(total_value),
            'date_range': {
                'min': min_date.strftime('%Y-%m-%d') if pd.notna(min_date) else None,
                'max': max_date.strftime('%Y-%m-%d') if pd.notna(max_date) else None
            },
            'pre_merger': len(pre_merger),
            'post_merger': len(post_merger),
            'by_table': by_table.to_dict(),
            'by_agency': by_agency.to_dict(),
            'by_tier': by_tier.to_dict(),
            'dprk_contracts': len(dprk_contracts)
        }

    def generate_report(self, output_dir="analysis"):
        """Generate comprehensive JSON and Markdown reports"""
        Path(output_dir).mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(self.all_contracts)

        # JSON export (full data)
        json_path = Path(output_dir) / f"cosco_contracts_complete_{timestamp}.json"
        with open(json_path, 'w') as f:
            json.dump({
                'extraction_date': timestamp,
                'total_contracts': len(self.all_contracts),
                'contracts': self.all_contracts,
                'analysis': self.analyze_contracts()
            }, f, indent=2, default=str)

        print(f"\n[OK] JSON report saved: {json_path}")

        # CSV export (for Excel)
        csv_path = Path(output_dir) / f"cosco_contracts_complete_{timestamp}.csv"
        df.to_csv(csv_path, index=False)

        print(f"[OK] CSV export saved: {csv_path}")

        # Markdown timeline
        self.generate_markdown_timeline(df, output_dir, timestamp)

        return json_path, csv_path

    def generate_markdown_timeline(self, df, output_dir, timestamp):
        """Generate detailed Markdown timeline report"""
        md_path = Path(output_dir) / f"COSCO_CONTRACT_TIMELINE_{timestamp}.md"

        with open(md_path, 'w') as f:
            f.write("# COSCO Contract Timeline (Complete)\n")
            f.write(f"## Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("---\n\n")
            f.write("## Summary\n\n")

            # Overall stats
            total = len(df)
            total_value = df['award_amount'].sum()

            f.write(f"**Total Contracts:** {total}\n\n")
            f.write(f"**Total Value:** ${total_value:,.2f}\n\n")

            # Timeline
            df['action_date_parsed'] = pd.to_datetime(df['action_date'], errors='coerce')
            df_sorted = df.sort_values('action_date_parsed')

            f.write("---\n\n")
            f.write("## Complete Contract Timeline\n\n")

            for idx, row in df_sorted.iterrows():
                date = row['action_date_parsed'].strftime('%Y-%m-%d') if pd.notna(row['action_date_parsed']) else 'Unknown'
                amount = row['award_amount']
                entity = row['recipient_name'] or row['vendor_name']
                desc = str(row['award_description'])[:150] if pd.notna(row['award_description']) else 'No description'
                agency = row['funding_agency_code'] if pd.notna(row['funding_agency_code']) else 'Unknown'
                tier = row['importance_tier'] if pd.notna(row['importance_tier']) else 'Unknown'

                # Highlight DPRK contracts
                is_dprk = 'DPRK' in desc or 'NORTH KOREA' in desc
                dprk_marker = " **[DPRK]**" if is_dprk else ""

                f.write(f"### {date}{dprk_marker}\n\n")
                f.write(f"- **Entity:** {entity}\n")
                f.write(f"- **Amount:** ${amount:,.2f}\n")
                f.write(f"- **Agency:** {agency}\n")
                f.write(f"- **Tier:** {tier}\n")
                f.write(f"- **Description:** {desc}\n")
                f.write(f"- **Source:** {row['source_table']}\n")
                f.write(f"- **Transaction ID:** {row['transaction_id']}\n\n")

        print(f"[OK] Markdown timeline saved: {md_path}")

    def run(self):
        """Execute full mapping process"""
        print("="*80)
        print("COSCO CONTRACT COMPREHENSIVE MAPPING")
        print("="*80)
        print(f"Database: {self.db_path}")
        print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        self.connect()

        try:
            # Extract from all tables
            self.extract_usaspending_305()
            self.extract_usaspending_101()
            self.extract_usaspending_comprehensive()

            # Analyze
            analysis = self.analyze_contracts()

            # Generate reports
            json_path, csv_path = self.generate_report()

            print("\n" + "="*80)
            print("MAPPING COMPLETE")
            print("="*80)
            print(f"\nTotal contracts mapped: {len(self.all_contracts)}")
            print(f"Reports generated:")
            print(f"  - JSON: {json_path}")
            print(f"  - CSV: {csv_path}")
            print(f"  - Markdown timeline")

        finally:
            self.close()


def main():
    mapper = COSCOContractMapper()
    mapper.run()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import re

# ============================================================================
# SECURITY: SQL injection prevention through identifier validation
# ============================================================================

def validate_sql_identifier(identifier):
    """
    SECURITY: Validate SQL identifier (table or column name).
    Only allows alphanumeric characters and underscores.
    Prevents SQL injection from dynamic SQL construction.
    """
    if not identifier:
        raise ValueError("Identifier cannot be empty")

    # Check for valid characters only (alphanumeric + underscore)
    if not re.match(r'^[a-zA-Z0-9_]+$', identifier):
        raise ValueError(f"Invalid identifier: {identifier}. Contains illegal characters.")

    # Check length (SQLite limit is 1024, we use 100 for safety)
    if len(identifier) > 100:
        raise ValueError(f"Identifier too long: {identifier}")

    # Blacklist dangerous SQL keywords
    dangerous_keywords = {'DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE',
                         'EXEC', 'EXECUTE', 'UNION', 'SELECT', '--', ';', '/*', '*/'}
    if identifier.upper() in dangerous_keywords:
        raise ValueError(f"Identifier contains SQL keyword: {identifier}")

    return identifier


"""
Germany-China Bilateral Relations Baseline Collector
Extracts and populates bilateral relations data for Germany

Phase 1: Data we already have
- AidData Global Chinese Development Finance
- Existing OpenAlex collaborations (31,329 papers)
- Major acquisitions (documented list)

Phase 2: Web collection
- Sister cities
- Diplomatic timeline
- Trade statistics
"""

import sqlite3
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import hashlib
import sys
import io

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

class GermanyBaselineCollector:
    def __init__(self):
        self.db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")
        self.aiddata_path = Path("F:/OSINT_Data/AidData/global_chinese_finance_v3/AidDatas_Global_Chinese_Development_Finance_Dataset_Version_3_0/AidDatasGlobalChineseDevelopmentFinanceDataset_v3.0.xlsx")
        self.conn = None

    def connect_db(self):
        """Connect to database"""
        self.conn = sqlite3.connect(str(self.db_path))
        print(f"Connected to {self.db_path}")

    def initialize_germany(self):
        """Initialize Germany in bilateral_countries if not exists"""
        print("\n=== Initializing Germany in bilateral_countries ===")

        cursor = self.conn.cursor()

        # Check if Germany already exists
        cursor.execute("SELECT country_code FROM bilateral_countries WHERE country_code = 'DE'")
        if cursor.fetchone():
            print("  Germany already initialized")
            return

        # Insert Germany
        cursor.execute("""
            INSERT INTO bilateral_countries
            (country_code, country_name, country_name_chinese,
             diplomatic_normalization_date, current_relationship_status,
             relationship_tier, bri_participation_status,
             eu_member, nato_member, five_eyes, notes, last_updated)
            VALUES
            ('DE', 'Germany', '德国',
             '1972-10-11', 'comprehensive_strategic_partnership',
             'tier_3_major_economy', 'observer',
             1, 1, 0,
             'West Germany normalized 1972; Unified Germany 1990. 12 Merkel visits 2005-2019. Major economy with significant Chinese investment.',
             CURRENT_TIMESTAMP)
        """)
        self.conn.commit()
        print("  ✓ Germany initialized successfully")

        # Display the record
        cursor.execute("SELECT * FROM bilateral_countries WHERE country_code = 'DE'")
        record = cursor.fetchone()
        print(f"  Country: {record[1]}")
        print(f"  Normalized: {record[3]}")
        print(f"  Status: {record[4]}")
        print(f"  Tier: {record[5]}")

    def extract_aiddata_germany(self):
        """Extract Germany projects from AidData"""
        print("\n=== Extracting Germany Data from AidData ===")

        if not self.aiddata_path.exists():
            print(f"  ✗ AidData file not found: {self.aiddata_path}")
            return

        print(f"  Reading: {self.aiddata_path.name}")

        # Read AidData Excel file (GCDF_3.0 sheet contains the data)
        df = pd.read_excel(self.aiddata_path, sheet_name='GCDF_3.0')
        print(f"  Total records: {len(df):,}")

        # Filter for Germany
        # AidData typically has 'recipient' or 'country' column
        # Check column names
        print(f"  Columns: {list(df.columns)[:10]}...")

        # Common column names for recipient country
        recipient_cols = ['Recipient', 'recipient', 'Country', 'country', 'Recipient Country']
        recipient_col = None
        for col in recipient_cols:
            if col in df.columns:
                recipient_col = col
                break

        if not recipient_col:
            print("  ✗ Could not find recipient country column")
            print(f"  Available columns: {list(df.columns)}")
            return

        print(f"  Using recipient column: {recipient_col}")

        # Filter for Germany (various spellings)
        germany_mask = df[recipient_col].str.contains('Germany', case=False, na=False) | \
                      df[recipient_col].str.contains('FRG', case=False, na=False) | \
                      df[recipient_col].str.contains('GDR', case=False, na=False)

        germany_df = df[germany_mask].copy()
        print(f"  Germany projects found: {len(germany_df)}")

        if len(germany_df) == 0:
            # Try checking unique recipient values
            unique_recipients = df[recipient_col].value_counts().head(20)
            print("  Top 20 recipients in dataset:")
            print(unique_recipients)
            print("\n  Note: Germany may have zero Chinese development projects (expected for developed EU country)")
            return

        # Insert into infrastructure_projects table
        cursor = self.conn.cursor()
        inserted = 0

        for idx, row in germany_df.iterrows():
            try:
                project_id = f"DE_aiddata_{hashlib.md5(str(row.to_dict()).encode()).hexdigest()[:12]}"

                # Extract relevant fields (adapt based on actual column names)
                project_data = {
                    'project_id': project_id,
                    'country_code': 'DE',
                    'project_name': row.get('Title', row.get('Project Title', 'Unknown')),
                    'project_type': self._classify_project_type(row),
                    'project_category': row.get('Sector', 'unknown'),
                    'bri_affiliated': 1 if 'BRI' in str(row.get('Status', '')) else 0,
                    'chinese_entity': row.get('Lender', row.get('Financial Institution', 'Unknown')),
                    'project_value_usd': self._extract_amount(row),
                    'chinese_investment_usd': self._extract_amount(row),
                    'project_status': row.get('Status', 'unknown'),
                    'announcement_date': self._extract_date(row, 'Year'),
                    'financing_structure': row.get('Flow Type', 'unknown'),
                    'source': 'AidData Global Chinese Development Finance v3.0',
                    'source_url': 'https://www.aiddata.org/data/aiddatas-global-chinese-development-finance-dataset-version-3-0'
                }

                # Insert
                cursor.execute("""
                    INSERT OR IGNORE INTO infrastructure_projects
                    (project_id, country_code, project_name, project_type, project_category,
                     bri_affiliated, chinese_entity, project_value_usd, chinese_investment_usd,
                     project_status, announcement_date, financing_structure, source, source_url)
                    VALUES
                    (:project_id, :country_code, :project_name, :project_type, :project_category,
                     :bri_affiliated, :chinese_entity, :project_value_usd, :chinese_investment_usd,
                     :project_status, :announcement_date, :financing_structure, :source, :source_url)
                """, project_data)

                inserted += 1

            except Exception as e:
                print(f"  Warning: Could not insert project {idx}: {e}")
                continue

        self.conn.commit()
        print(f"  ✓ Inserted {inserted} infrastructure projects")

    def _classify_project_type(self, row):
        """Classify project type based on sector/description"""
        sector = str(row.get('Sector', '')).lower()

        if 'transport' in sector or 'road' in sector or 'rail' in sector:
            return 'transport'
        elif 'energy' in sector or 'power' in sector:
            return 'energy'
        elif 'telecom' in sector or 'communication' in sector:
            return 'telecom'
        elif 'industrial' in sector:
            return 'industrial_park'
        else:
            return 'other'

    def _extract_amount(self, row):
        """Extract amount from row"""
        amount_cols = ['Amount (Constant 2021 USD, Millions)', 'Amount', 'Commitment Amount']
        for col in amount_cols:
            if col in row.index:
                try:
                    val = row[col]
                    if pd.notna(val):
                        # Convert millions to dollars
                        return float(val) * 1_000_000
                except:
                    continue
        return None

    def _extract_date(self, row, *col_names):
        """Extract date from row"""
        for col in col_names:
            if col in row.index and pd.notna(row[col]):
                try:
                    year = int(row[col])
                    return f"{year}-01-01"
                except:
                    continue
        return None

    def populate_major_acquisitions(self):
        """Populate known major Chinese acquisitions in Germany"""
        print("\n=== Populating Major Chinese Acquisitions ===")

        acquisitions = [
            {
                'acquisition_id': 'DE_2016_kuka',
                'country_code': 'DE',
                'target_company': 'Kuka AG',
                'target_sector': 'robotics',
                'target_technology_area': 'Industrial robotics, automation systems, AI-powered manufacturing',
                'chinese_acquirer': 'Midea Group',
                'acquirer_type': 'private',
                'acquisition_date': '2016-08-08',
                'announcement_date': '2016-05-18',
                'deal_value_usd': 5000000000,
                'ownership_acquired_percentage': 94.5,
                'deal_structure': 'full_acquisition',
                'strategic_rationale': 'Access to Industry 4.0 robotics technology, manufacturing automation expertise',
                'technology_acquired': 'Advanced industrial robotics, automation systems, AI-powered manufacturing, automotive assembly robots',
                'market_access_gained': 'European automotive and manufacturing sectors',
                'employees_at_acquisition': 13300,
                'government_review_process': 'Controversial in Bundestag, concerns about technology transfer',
                'approval_conditions': 'Employment guarantees for German workers',
                'political_controversy': 1,
                'media_attention_level': 'high',
                'post_acquisition_performance': 'Retained in Germany, employment guarantees maintained',
                'source': 'Public records, media reports',
                'source_url': 'https://www.reuters.com/article/us-kuka-m-a-midea-group-idUSKCN0Z50WX'
            },
            {
                'acquisition_id': 'DE_2012_putzmeister',
                'country_code': 'DE',
                'target_company': 'Putzmeister Holding GmbH',
                'target_sector': 'construction_equipment',
                'target_technology_area': 'Concrete pumping technology',
                'chinese_acquirer': 'Sany Heavy Industry',
                'acquirer_type': 'private',
                'acquisition_date': '2012-01-31',
                'announcement_date': '2012-01-31',
                'deal_value_usd': 525000000,
                'ownership_acquired_percentage': 100.0,
                'deal_structure': 'full_acquisition',
                'strategic_rationale': 'Technology acquisition for infrastructure projects, particularly relevant post-Fukushima',
                'technology_acquired': 'Large-scale concrete pumping systems (used at Fukushima)',
                'employees_at_acquisition': 3200,
                'political_controversy': 0,
                'media_attention_level': 'medium',
                'post_acquisition_performance': 'Operations maintained in Germany',
                'source': 'Public records',
                'source_url': 'https://www.bbc.com/news/business-16822285'
            },
            {
                'acquisition_id': 'DE_2016_kraussmaffei',
                'country_code': 'DE',
                'target_company': 'KraussMaffei Group',
                'target_sector': 'machinery',
                'target_technology_area': 'Plastics and rubber processing machinery',
                'chinese_acquirer': 'ChemChina',
                'acquirer_type': 'soe',
                'acquisition_date': '2016-01-15',
                'announcement_date': '2015-09-15',
                'deal_value_usd': 1000000000,
                'ownership_acquired_percentage': 100.0,
                'deal_structure': 'full_acquisition',
                'strategic_rationale': 'Advanced manufacturing technology, plastics processing expertise',
                'technology_acquired': 'Injection molding machines, extrusion technology, reaction process machinery',
                'employees_at_acquisition': 4700,
                'political_controversy': 0,
                'media_attention_level': 'medium',
                'source': 'Public records',
                'source_url': 'https://www.kraussmaffei.com/'
            },
            {
                'acquisition_id': 'DE_2016_aixtron_blocked',
                'country_code': 'DE',
                'target_company': 'Aixtron SE',
                'target_sector': 'semiconductors',
                'target_technology_area': 'Semiconductor manufacturing equipment',
                'chinese_acquirer': 'Fujian Grand Chip Investment Fund',
                'acquirer_type': 'state_backed',
                'acquisition_date': None,
                'announcement_date': '2016-05-23',
                'deal_value_usd': 742000000,
                'ownership_acquired_percentage': 100.0,
                'deal_structure': 'full_acquisition',
                'deal_status': 'blocked',
                'government_approval_required': 1,
                'government_approval_status': 'blocked',
                'blocking_reason': 'National security concerns, US-Germany coordination, semiconductor technology protection',
                'strategic_asset': 1,
                'technology_transfer_involved': 1,
                'national_security_review': 1,
                'strategic_rationale': 'Access to advanced semiconductor deposition equipment technology',
                'technology_acquired': 'MOCVD systems for LED and semiconductor production',
                'political_controversy': 1,
                'media_attention_level': 'high',
                'controversy_notes': 'Germany blocked acquisition following US pressure; led to tightening of FDI screening',
                'source': 'Public records, government statements',
                'source_url': 'https://www.reuters.com/article/us-aixtron-m-a-china-idUSKBN12N20M'
            },
            {
                'acquisition_id': 'DE_2018_50hertz_blocked',
                'country_code': 'DE',
                'target_company': '50Hertz Transmission GmbH',
                'target_sector': 'energy_infrastructure',
                'target_technology_area': 'Electricity transmission grid',
                'chinese_acquirer': 'State Grid Corporation of China',
                'acquirer_type': 'soe',
                'acquisition_date': None,
                'announcement_date': '2018-07-27',
                'deal_value_usd': 1100000000,
                'ownership_acquired_percentage': 20.0,
                'deal_structure': 'minority_stake',
                'deal_status': 'blocked',
                'government_approval_required': 1,
                'government_approval_status': 'blocked',
                'blocking_reason': 'Critical infrastructure protection; KfW (German state bank) intervened to acquire stake',
                'strategic_asset': 1,
                'national_security_review': 1,
                'strategic_rationale': 'Access to European electricity grid infrastructure',
                'political_controversy': 1,
                'media_attention_level': 'high',
                'controversy_notes': 'Government intervention via KfW to prevent Chinese control of critical infrastructure',
                'source': 'Public records, government statements',
                'source_url': 'https://www.reuters.com/article/us-elia-m-a-50hertz-idUSKBN1KI0RD'
            },
            {
                'acquisition_id': 'DE_2022_hamburg_port_partial',
                'country_code': 'DE',
                'target_company': 'Hamburg Port Terminal Tollerort (CTT)',
                'target_sector': 'port_infrastructure',
                'target_technology_area': 'Container terminal operations',
                'chinese_acquirer': 'COSCO Shipping Ports',
                'acquirer_type': 'soe',
                'acquisition_date': '2022-10-26',
                'announcement_date': '2021-09-01',
                'deal_value_usd': None,  # Not disclosed
                'ownership_acquired_percentage': 24.9,
                'deal_structure': 'minority_stake',
                'deal_status': 'completed',
                'government_approval_required': 1,
                'government_approval_status': 'approved_with_conditions',
                'approval_conditions': 'Reduced from 35% to 24.9% stake; no board representation; no veto rights',
                'strategic_asset': 1,
                'national_security_review': 1,
                'strategic_rationale': 'Access to major European port, connection to Duisburg logistics hub',
                'political_controversy': 1,
                'media_attention_level': 'high',
                'controversy_notes': 'Coalition government split; Scholz approved despite opposition from Foreign, Economy, and Interior ministries',
                'source': 'Public records, government statements',
                'source_url': 'https://www.dw.com/en/germany-approves-cosco-stake-in-hamburg-port/a-63569781'
            }
        ]

        cursor = self.conn.cursor()
        inserted = 0

        for acq in acquisitions:
            try:
                # Build column names and values
                # SECURITY: Validate all column names before use in SQL
                safe_cols = [validate_sql_identifier(k) for k in acq.keys()]
                columns = ', '.join(safe_cols)
                placeholders = ', '.join([f':{k}' for k in acq.keys()])

                cursor.execute(f"""
                    INSERT OR REPLACE INTO major_acquisitions ({columns})
                    VALUES ({placeholders})
                """, acq)

                inserted += 1
                print(f"  ✓ {acq['target_company']}: ${acq['deal_value_usd']/1e9:.1f}B by {acq['chinese_acquirer']}")

            except Exception as e:
                print(f"  ✗ Error inserting {acq.get('target_company', 'unknown')}: {e}")

        self.conn.commit()
        print(f"\n  Total acquisitions inserted: {inserted}")

    def link_openalex_collaborations(self):
        """Link existing Germany-China OpenAlex collaborations"""
        print("\n=== Linking OpenAlex Collaborations ===")

        cursor = self.conn.cursor()

        # Check if we have OpenAlex Germany-China data
        cursor.execute("""
            SELECT COUNT(*) FROM openalex_works
            WHERE id IN (
                SELECT work_id FROM openalex_authorships
                WHERE institution_id IN (
                    SELECT id FROM openalex_institutions WHERE country_code = 'DE'
                )
            )
        """)

        # For now, create a placeholder linking framework
        # We'll populate this with actual data once we verify the OpenAlex schema

        print("  Creating linking framework for 31,329 Germany-China papers")
        print("  (Full linking will be implemented after OpenAlex schema verification)")

        # Create sample link for demonstration
        cursor.execute("""
            INSERT OR IGNORE INTO bilateral_academic_links
            (link_id, country_code, collaboration_type, strategic_significance)
            VALUES
            ('DE_openalex_link_framework', 'DE', 'research_collaboration',
             'Framework for linking 31,329 Germany-China academic collaborations')
        """)
        self.conn.commit()

        print("  ✓ Linking framework created")

    def generate_summary_report(self):
        """Generate summary of what was collected"""
        print("\n" + "="*80)
        print("GERMANY BASELINE COLLECTION SUMMARY")
        print("="*80)

        cursor = self.conn.cursor()

        # Country status
        cursor.execute("SELECT * FROM bilateral_countries WHERE country_code = 'DE'")
        country = cursor.fetchone()
        if country:
            print(f"\n✓ Country: {country[1]} ({country[2]})")
            print(f"  Normalized: {country[3]}")
            print(f"  Status: {country[4]}")
            print(f"  BRI: {country[6]}")

        # Infrastructure projects
        cursor.execute("SELECT COUNT(*), SUM(project_value_usd) FROM infrastructure_projects WHERE country_code = 'DE'")
        projects, project_value = cursor.fetchone()
        print(f"\n✓ Infrastructure Projects: {projects}")
        if project_value:
            print(f"  Total value: ${project_value/1e9:.2f}B")

        # Major acquisitions
        cursor.execute("""
            SELECT COUNT(*), SUM(deal_value_usd),
                   SUM(CASE WHEN deal_status = 'blocked' THEN 1 ELSE 0 END)
            FROM major_acquisitions WHERE country_code = 'DE'
        """)
        acqs, acq_value, blocked = cursor.fetchone()
        print(f"\n✓ Major Acquisitions: {acqs}")
        if acq_value:
            print(f"  Total value: ${acq_value/1e9:.2f}B")
        print(f"  Blocked deals: {blocked}")

        # List major acquisitions
        cursor.execute("""
            SELECT target_company, chinese_acquirer, deal_value_usd,
                   acquisition_date, deal_status
            FROM major_acquisitions
            WHERE country_code = 'DE'
            ORDER BY deal_value_usd DESC
        """)
        print("\n  Major Acquisitions Detail:")
        for company, acquirer, value, date, status in cursor.fetchall():
            value_str = f"${value/1e9:.1f}B" if value else "undisclosed"
            status_marker = "✗ BLOCKED" if status == 'blocked' else "✓"
            print(f"    {status_marker} {company}: {value_str} by {acquirer} ({date or 'N/A'})")

        # Academic links
        cursor.execute("SELECT COUNT(*) FROM bilateral_academic_links WHERE country_code = 'DE'")
        links = cursor.fetchone()[0]
        print(f"\n✓ Academic Collaboration Links: {links} (framework created)")
        print("  Ready to link 31,329 OpenAlex Germany-China papers")

        print("\n" + "="*80)
        print("NEXT STEPS:")
        print("="*80)
        print("1. Build sister cities collector")
        print("2. Create diplomatic timeline from official sources")
        print("3. Import Destatis trade statistics")
        print("4. Link existing OpenAlex papers (requires schema verification)")
        print("5. Generate comprehensive Germany-China report")
        print("="*80)

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print("\nDatabase connection closed")

def main():
    print("="*80)
    print("GERMANY-CHINA BILATERAL RELATIONS BASELINE COLLECTOR")
    print("="*80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    collector = GermanyBaselineCollector()

    try:
        # Connect to database
        collector.connect_db()

        # Initialize Germany
        collector.initialize_germany()

        # Extract data we already have
        collector.extract_aiddata_germany()

        # Populate known acquisitions
        collector.populate_major_acquisitions()

        # Create framework for OpenAlex linking
        collector.link_openalex_collaborations()

        # Generate summary
        collector.generate_summary_report()

        print("\n✓ GERMANY BASELINE COLLECTION COMPLETE")

    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        collector.close()

    return True

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)

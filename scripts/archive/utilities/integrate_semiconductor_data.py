"""
Integrate semiconductor data into osint_master.db
- Create tables from schema
- Load WSTS historical billings data
- Load SIA industry metrics
- Load comprehensive taxonomy
Zero Fabrication Protocol: All data sourced from verified reports
"""

import sqlite3
import json
from datetime import datetime

# Database path
DB_PATH = 'F:/OSINT_WAREHOUSE/osint_master.db'

# Connect to database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("=== Semiconductor Data Integration ===")
print(f"Database: {DB_PATH}")
print("")

# ============================================================================
# 1. CREATE TABLES
# ============================================================================

print("Step 1: Creating database tables...")

# Read and execute schema
with open('C:/Projects/OSINT-Foresight/schema/semiconductor_data_integration_schema.sql', 'r') as f:
    schema_sql = f.read()

# Execute schema (split by semicolons for SQLite)
for statement in schema_sql.split(';'):
    statement = statement.strip()
    if statement and not statement.startswith('--'):
        try:
            cursor.execute(statement)
        except sqlite3.OperationalError as e:
            # Skip if table already exists
            if 'already exists' not in str(e):
                print(f"Warning: {e}")

conn.commit()
print("  Tables created successfully")

# ============================================================================
# 2. LOAD WSTS HISTORICAL BILLINGS DATA
# ============================================================================

print("\nStep 2: Loading WSTS historical billings data...")

# Load actual monthly/quarterly data
with open('C:/Projects/OSINT-Foresight/data/external/wsts_historical_billings_2025.json', 'r') as f:
    wsts_data = json.load(f)

count = 0
for record in wsts_data['data']:
    cursor.execute("""
        INSERT OR REPLACE INTO semiconductor_market_billings
        (year, region, january, february, march, april, may, june, july, august,
         september, october, november, december, q1, q2, q3, q4, total_year, data_type)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'actual')
    """, (
        record['year'], record['region'],
        record.get('january'), record.get('february'), record.get('march'),
        record.get('april'), record.get('may'), record.get('june'),
        record.get('july'), record.get('august'), record.get('september'),
        record.get('october'), record.get('november'), record.get('december'),
        record.get('q1'), record.get('q2'), record.get('q3'), record.get('q4'),
        record.get('total_year')
    ))
    count += 1

print(f"  Loaded {count} records (actual data)")

# Load 3MMA data
with open('C:/Projects/OSINT-Foresight/data/external/wsts_3mma_billings_2025.json', 'r') as f:
    wsts_3mma = json.load(f)

count = 0
for record in wsts_3mma['data']:
    cursor.execute("""
        INSERT OR REPLACE INTO semiconductor_market_billings
        (year, region, january, february, march, april, may, june, july, august,
         september, october, november, december, data_type)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '3mma')
    """, (
        record['year'], record['region'],
        record.get('january'), record.get('february'), record.get('march'),
        record.get('april'), record.get('may'), record.get('june'),
        record.get('july'), record.get('august'), record.get('september'),
        record.get('october'), record.get('november'), record.get('december')
    ))
    count += 1

print(f"  Loaded {count} records (3-month moving average)")

conn.commit()

# ============================================================================
# 3. LOAD SIA INDUSTRY METRICS
# ============================================================================

print("\nStep 3: Loading SIA industry metrics...")

with open('C:/Projects/OSINT-Foresight/data/external/sia_industry_metrics_2025.json', 'r') as f:
    sia_data = json.load(f)

# Market overview metrics
year = 2024
count = 0

cursor.execute("""
    INSERT OR REPLACE INTO semiconductor_industry_metrics
    (year, metric_category, metric_name, metric_value, metric_unit, metric_description)
    VALUES (?, 'market', 'global_sales', ?, ?, 'Global semiconductor sales')
""", (year, sia_data['market_overview']['global_sales_2024']['value'], 'USD billions'))
count += 1

cursor.execute("""
    INSERT OR REPLACE INTO semiconductor_industry_metrics
    (year, metric_category, metric_name, metric_value, metric_unit, metric_description)
    VALUES (2025, 'market', 'projected_sales', ?, ?, 'Projected global semiconductor sales')
""", (sia_data['market_overview']['projected_sales_2025']['value'], 'USD billions'))
count += 1

cursor.execute("""
    INSERT OR REPLACE INTO semiconductor_industry_metrics
    (year, metric_category, metric_name, metric_value, metric_unit, metric_description)
    VALUES (?, 'market', 'us_market_share', ?, ?, 'US companies share of global sales')
""", (year, sia_data['market_overview']['us_market_share_global']['value'], 'percent'))
count += 1

# R&D metrics
cursor.execute("""
    INSERT OR REPLACE INTO semiconductor_industry_metrics
    (year, metric_category, metric_name, metric_value, metric_unit, metric_description)
    VALUES (?, 'rd', 'us_rd_spending', ?, ?, 'US semiconductor R&D spending')
""", (year, sia_data['us_industry_metrics']['rd_spending_2024']['value'], 'USD billions'))
count += 1

cursor.execute("""
    INSERT OR REPLACE INTO semiconductor_industry_metrics
    (year, metric_category, metric_name, metric_value, metric_unit, metric_description)
    VALUES (?, 'rd', 'us_rd_percentage_revenue', ?, ?, 'US R&D as percentage of revenue')
""", (year, sia_data['us_industry_metrics']['rd_spending_2024']['percentage_of_revenue'], 'percent'))
count += 1

# Employment metrics
cursor.execute("""
    INSERT OR REPLACE INTO semiconductor_industry_metrics
    (year, metric_category, metric_name, metric_value, metric_unit, metric_description)
    VALUES (?, 'employment', 'direct_jobs', ?, ?, 'Direct semiconductor jobs in US')
""", (year, sia_data['us_industry_metrics']['us_employment']['direct_jobs_2024']['value'], 'count'))
count += 1

cursor.execute("""
    INSERT OR REPLACE INTO semiconductor_industry_metrics
    (year, metric_category, metric_name, metric_value, metric_unit, metric_description)
    VALUES (2032, 'employment', 'projected_jobs', ?, ?, 'Projected jobs from CHIPS Act')
""", (sia_data['us_industry_metrics']['us_employment']['projected_jobs_2032']['value'], 'count'))
count += 1

# CHIPS Act funding
cursor.execute("""
    INSERT OR REPLACE INTO semiconductor_industry_metrics
    (year, metric_category, metric_name, metric_value, metric_unit, metric_description)
    VALUES (?, 'policy', 'chips_act_total_funding', ?, ?, 'Total CHIPS Act funding')
""", (year, sia_data['chips_act_funding']['total_funding']['value'], 'USD billions'))
count += 1

cursor.execute("""
    INSERT OR REPLACE INTO semiconductor_industry_metrics
    (year, metric_category, metric_name, metric_value, metric_unit, metric_description)
    VALUES (?, 'policy', 'chips_act_manufacturing', ?, ?, 'CHIPS Act manufacturing incentives')
""", (year, sia_data['chips_act_funding']['total_funding']['breakdown']['manufacturing_incentives'], 'USD billions'))
count += 1

cursor.execute("""
    INSERT OR REPLACE INTO semiconductor_industry_metrics
    (year, metric_category, metric_name, metric_value, metric_unit, metric_description)
    VALUES (?, 'policy', 'chips_act_rd_workforce', ?, ?, 'CHIPS Act R&D and workforce funding')
""", (year, sia_data['chips_act_funding']['total_funding']['breakdown']['rd_and_workforce'], 'USD billions'))
count += 1

print(f"  Loaded {count} industry metrics")

# ============================================================================
# 4. LOAD MARKET SEGMENTS
# ============================================================================

print("\nStep 4: Loading market segments...")

count = 0
for segment_name, segment_data in sia_data['market_segments_2024'].items():
    cursor.execute("""
        INSERT OR REPLACE INTO semiconductor_market_segments
        (year, segment_name, market_share, segment_description)
        VALUES (2024, ?, ?, ?)
    """, (segment_name, segment_data['value'], segment_data['description']))
    count += 1

print(f"  Loaded {count} market segments")

# ============================================================================
# 5. LOAD SUPPLY CHAIN REGIONAL DATA
# ============================================================================

print("\nStep 5: Loading supply chain regional data...")

count = 0
for region, stages in sia_data['supply_chain_value_added']['regions'].items():
    for stage, percentage in stages.items():
        if stage != 'unit':
            cursor.execute("""
                INSERT OR REPLACE INTO semiconductor_supply_chain_regional
                (year, region, value_chain_stage, percentage)
                VALUES (2024, ?, ?, ?)
            """, (region, stage, percentage))
            count += 1

print(f"  Loaded {count} supply chain records")

conn.commit()

# ============================================================================
# 6. LOAD COMPREHENSIVE TAXONOMY
# ============================================================================

print("\nStep 6: Loading comprehensive taxonomy...")

with open('C:/Projects/OSINT-Foresight/config/semiconductor_comprehensive_taxonomy.json', 'r') as f:
    taxonomy = json.load(f)

# Load critical minerals
count_minerals = 0
if 'semiconductor_value_chain' in taxonomy and 'upstream' in taxonomy['semiconductor_value_chain']:
    upstream = taxonomy['semiconductor_value_chain']['upstream']
    if 'critical_minerals' in upstream:
        for mineral_name, mineral_data in upstream['critical_minerals'].items():
            cursor.execute("""
                INSERT OR REPLACE INTO semiconductor_critical_minerals
                (mineral_name, mineral_description, primary_use, supply_chain_risk,
                 primary_suppliers, china_market_share, strategic_importance, substitution_difficulty)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                mineral_name,
                mineral_data.get('description', ''),
                mineral_data.get('primary_use', ''),
                mineral_data.get('supply_chain_risk', ''),
                json.dumps(mineral_data.get('primary_suppliers', [])),
                mineral_data.get('china_market_share'),
                mineral_data.get('strategic_importance', ''),
                mineral_data.get('substitution_difficulty', '')
            ))
            count_minerals += 1

print(f"  Loaded {count_minerals} critical minerals")

# Load equipment suppliers
count_equipment = 0
if 'semiconductor_equipment' in taxonomy:
    for equipment_type, equipment_data in taxonomy['semiconductor_equipment'].items():
        if isinstance(equipment_data, dict) and 'suppliers' in equipment_data:
            for supplier_name, supplier_data in equipment_data['suppliers'].items():
                cursor.execute("""
                    INSERT OR REPLACE INTO semiconductor_equipment_suppliers
                    (equipment_type, supplier_name, supplier_country, market_share,
                     technology_focus, strategic_importance)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    equipment_type,
                    supplier_name,
                    supplier_data.get('country', ''),
                    supplier_data.get('market_share'),
                    supplier_data.get('technology', ''),
                    supplier_data.get('strategic_importance', '')
                ))
                count_equipment += 1

print(f"  Loaded {count_equipment} equipment suppliers")

# Load research areas
count_research = 0
if 'research_areas' in taxonomy:
    for research_area, research_data in taxonomy['research_areas'].items():
        if isinstance(research_data, dict):
            cursor.execute("""
                INSERT OR REPLACE INTO semiconductor_research_areas
                (research_area, description, subcategories, strategic_importance,
                 timeframe, leading_countries, leading_companies)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                research_area,
                research_data.get('description', ''),
                json.dumps(research_data.get('subcategories', [])),
                research_data.get('strategic_importance', ''),
                research_data.get('timeframe', ''),
                json.dumps(research_data.get('leading_countries', [])),
                json.dumps(research_data.get('leading_companies', []))
            ))
            count_research += 1

print(f"  Loaded {count_research} research areas")

conn.commit()

# ============================================================================
# SUMMARY
# ============================================================================

print("\n=== Integration Complete ===")

# Get table counts
tables = [
    'semiconductor_market_billings',
    'semiconductor_industry_metrics',
    'semiconductor_market_segments',
    'semiconductor_supply_chain_regional',
    'semiconductor_critical_minerals',
    'semiconductor_equipment_suppliers',
    'semiconductor_research_areas'
]

print("\nTable Record Counts:")
for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"  {table}: {count:,} records")

# Show some sample data
print("\n=== Sample Data: WSTS 2024 Worldwide ===")
cursor.execute("""
    SELECT year, region, q1, q2, q3, q4, total_year
    FROM semiconductor_market_billings
    WHERE year = 2024 AND region = 'Worldwide' AND data_type = 'actual'
""")
row = cursor.fetchone()
if row:
    print(f"Year: {row[0]}, Region: {row[1]}")
    print(f"Q1: ${row[2]/1000:.1f}B, Q2: ${row[3]/1000:.1f}B, Q3: ${row[4]/1000:.1f}B, Q4: ${row[5]/1000:.1f}B")
    print(f"Total: ${row[6]/1000:.1f}B")

print("\n=== Sample Data: Critical Minerals ===")
cursor.execute("""
    SELECT mineral_name, supply_chain_risk, strategic_importance
    FROM semiconductor_critical_minerals
    WHERE supply_chain_risk = 'CRITICAL'
    ORDER BY mineral_name
    LIMIT 5
""")
for row in cursor.fetchall():
    print(f"  {row[0]}: Risk={row[1]}, Importance={row[2]}")

conn.close()

print("\nDatabase connection closed.")
print("SUCCESS: All semiconductor data integrated into osint_master.db")

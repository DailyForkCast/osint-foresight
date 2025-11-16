"""
Load comprehensive taxonomy data into database
Handles the actual JSON structure with categories and items
"""
import sqlite3
import json

DB_PATH = 'F:/OSINT_WAREHOUSE/osint_master.db'
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print('=== Loading Comprehensive Taxonomy ===\n')

with open('C:/Projects/OSINT-Foresight/config/semiconductor_comprehensive_taxonomy.json', 'r') as f:
    taxonomy = json.load(f)

# ============================================================================
# 1. Load Critical Minerals & Raw Materials
# ============================================================================

print('1. Loading critical minerals & raw materials...')
count = 0

upstream = taxonomy['semiconductor_value_chain']['upstream']
for category in upstream['categories']:
    if category['name'] == 'Critical Minerals & Raw Materials':
        for item in category['items']:
            if isinstance(item, dict) and 'material' in item:
                # Build primary_use from applications
                primary_use = ', '.join(item.get('applications', [])) if 'applications' in item else ''

                cursor.execute('''
                    INSERT OR REPLACE INTO semiconductor_critical_minerals
                    (mineral_name, mineral_description, primary_use, supply_chain_risk,
                     primary_suppliers, strategic_importance)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    item.get('material', ''),
                    item.get('purity', ''),
                    primary_use,
                    item.get('supply_chain_risk', ''),
                    json.dumps(item.get('major_suppliers', [])),
                    item.get('strategic_importance', '')
                ))
                count += 1

print(f'   Loaded {count} critical minerals')

# ============================================================================
# 2. Load Equipment Suppliers
# ============================================================================

print('2. Loading equipment suppliers...')
count = 0

if 'semiconductor_equipment' in taxonomy:
    equipment = taxonomy['semiconductor_equipment']
    if 'categories' in equipment:
        for category in equipment['categories']:
            equipment_type = category.get('name', '')

            if 'suppliers' in category:
                for supplier in category['suppliers']:
                    if isinstance(supplier, dict):
                        cursor.execute('''
                            INSERT OR REPLACE INTO semiconductor_equipment_suppliers
                            (equipment_type, supplier_name, supplier_country, market_share,
                             technology_focus, strategic_importance)
                            VALUES (?, ?, ?, ?, ?, ?)
                        ''', (
                            equipment_type,
                            supplier.get('company', ''),
                            supplier.get('country', ''),
                            supplier.get('market_share'),
                            supplier.get('technology', ''),
                            supplier.get('strategic_importance', '')
                        ))
                        count += 1

print(f'   Loaded {count} equipment suppliers')

# ============================================================================
# 3. Load Research Areas
# ============================================================================

print('3. Loading research areas...')
count = 0

if 'research_areas' in taxonomy:
    research = taxonomy['research_areas']
    if 'categories' in research:
        for category in research['categories']:
            research_area = category.get('name', '')
            description = category.get('description', '')

            # Get subcategories if present
            subcategories = []
            if 'subcategories' in category:
                subcategories = category['subcategories']
            elif 'focus_areas' in category:
                subcategories = category['focus_areas']

            cursor.execute('''
                INSERT OR REPLACE INTO semiconductor_research_areas
                (research_area, description, subcategories, strategic_importance, timeframe)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                research_area,
                description,
                json.dumps(subcategories),
                category.get('strategic_importance', ''),
                category.get('timeframe', '')
            ))
            count += 1

print(f'   Loaded {count} research areas')

conn.commit()

# ============================================================================
# Summary and Verification
# ============================================================================

print('\n=== Summary ===')

tables = [
    'semiconductor_market_billings',
    'semiconductor_industry_metrics',
    'semiconductor_market_segments',
    'semiconductor_supply_chain_regional',
    'semiconductor_critical_minerals',
    'semiconductor_equipment_suppliers',
    'semiconductor_research_areas'
]

print('\nTable Record Counts:')
for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"  {table}: {count:,} records")

# Show sample data
print('\n=== Sample Data: 2024 Worldwide Market ===')
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

print('\n=== Sample Data: Critical Minerals ===')
cursor.execute("""
    SELECT mineral_name, supply_chain_risk, strategic_importance
    FROM semiconductor_critical_minerals
    ORDER BY CASE supply_chain_risk WHEN 'CRITICAL' THEN 1 WHEN 'HIGH' THEN 2 WHEN 'MEDIUM' THEN 3 ELSE 4 END
    LIMIT 5
""")
for row in cursor.fetchall():
    print(f"  {row[0]}: Risk={row[1]}, Importance={row[2]}")

print('\n=== Sample Data: Market Segments (2024) ===')
cursor.execute("""
    SELECT segment_name, market_share, segment_description
    FROM semiconductor_market_segments
    WHERE year = 2024
    ORDER BY market_share DESC
""")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]}% - {row[2]}")

conn.close()

print('\n✓ SUCCESS: All semiconductor data integrated into osint_master.db')

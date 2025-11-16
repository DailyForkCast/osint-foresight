"""
Create all semiconductor database tables
"""
import sqlite3

DB_PATH = 'F:/OSINT_WAREHOUSE/osint_master.db'
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("Creating semiconductor database tables...")

# Table 1: Market billings (already created)
print("  1. semiconductor_market_billings... (already exists)")

# Table 2: Industry metrics
cursor.execute('''
CREATE TABLE IF NOT EXISTS semiconductor_industry_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER NOT NULL,
    metric_category TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    metric_value REAL,
    metric_unit TEXT,
    metric_description TEXT,
    source TEXT DEFAULT 'SIA-State-of-the-Industry-Report-2025.pdf',
    source_page TEXT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(year, metric_category, metric_name)
)
''')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_metrics_year_category ON semiconductor_industry_metrics(year, metric_category)')
print("  2. semiconductor_industry_metrics... created")

# Table 3: Market segments
cursor.execute('''
CREATE TABLE IF NOT EXISTS semiconductor_market_segments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER NOT NULL,
    segment_name TEXT NOT NULL,
    market_share REAL,
    segment_description TEXT,
    source TEXT DEFAULT 'SIA-State-of-the-Industry-Report-2025.pdf',
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(year, segment_name)
)
''')
print("  3. semiconductor_market_segments... created")

# Table 4: Supply chain regional
cursor.execute('''
CREATE TABLE IF NOT EXISTS semiconductor_supply_chain_regional (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER NOT NULL,
    region TEXT NOT NULL,
    value_chain_stage TEXT NOT NULL,
    percentage REAL,
    source TEXT DEFAULT 'SIA-State-of-the-Industry-Report-2025.pdf',
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(year, region, value_chain_stage)
)
''')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_supply_chain_region ON semiconductor_supply_chain_regional(region, value_chain_stage)')
print("  4. semiconductor_supply_chain_regional... created")

# Table 5: Critical minerals
cursor.execute('''
CREATE TABLE IF NOT EXISTS semiconductor_critical_minerals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mineral_name TEXT NOT NULL UNIQUE,
    mineral_description TEXT,
    primary_use TEXT,
    supply_chain_risk TEXT,
    primary_suppliers TEXT,
    china_market_share REAL,
    strategic_importance TEXT,
    substitution_difficulty TEXT,
    source TEXT DEFAULT 'semiconductor_comprehensive_taxonomy.json',
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')
print("  5. semiconductor_critical_minerals... created")

# Table 6: Equipment suppliers
cursor.execute('''
CREATE TABLE IF NOT EXISTS semiconductor_equipment_suppliers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    equipment_type TEXT NOT NULL,
    supplier_name TEXT NOT NULL,
    supplier_country TEXT,
    market_share REAL,
    technology_focus TEXT,
    strategic_importance TEXT,
    source TEXT DEFAULT 'semiconductor_comprehensive_taxonomy.json',
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(equipment_type, supplier_name)
)
''')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_equipment_type ON semiconductor_equipment_suppliers(equipment_type)')
print("  6. semiconductor_equipment_suppliers... created")

# Table 7: Research areas
cursor.execute('''
CREATE TABLE IF NOT EXISTS semiconductor_research_areas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    research_area TEXT NOT NULL UNIQUE,
    description TEXT,
    subcategories TEXT,
    strategic_importance TEXT,
    timeframe TEXT,
    leading_countries TEXT,
    leading_companies TEXT,
    source TEXT DEFAULT 'semiconductor_comprehensive_taxonomy.json',
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')
print("  7. semiconductor_research_areas... created")

# Views
cursor.execute('''
CREATE VIEW IF NOT EXISTS v_semiconductor_market_latest AS
SELECT year, region, total_year, q1, q2, q3, q4
FROM semiconductor_market_billings
WHERE data_type = 'actual'
ORDER BY year DESC, CASE region WHEN 'Worldwide' THEN 1 WHEN 'Asia Pacific' THEN 2
    WHEN 'Americas' THEN 3 WHEN 'Europe' THEN 4 WHEN 'Japan' THEN 5 END
''')
print("  8. v_semiconductor_market_latest view... created")

conn.commit()
conn.close()

print("\nAll tables and views created successfully!")

#!/usr/bin/env python3
"""
Create SQL database schema for TED procurement analysis
Normalized structure for efficient querying and analysis
"""

import sqlite3
from pathlib import Path
import logging

def create_database(db_path: str = "F:/OSINT_Data/ted_analysis.db"):
    """Create normalized database schema for TED data"""

    # Ensure directory exists
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")

    # 1. Contracts table - core procurement records
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS contracts (
        contract_id TEXT PRIMARY KEY,
        notice_number TEXT,
        publication_date DATE,
        authority_country TEXT,
        contracting_authority TEXT,
        contract_value REAL,
        currency TEXT,
        contract_type TEXT,
        cpv_code TEXT,
        procedure_type TEXT,
        award_date DATE,
        source_archive TEXT,
        source_file TEXT,
        processing_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Create indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_pub_date ON contracts(publication_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_country ON contracts(authority_country)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_cpv ON contracts(cpv_code)")

    # 2. Chinese entities table - normalized entity list
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chinese_entities (
        entity_id INTEGER PRIMARY KEY AUTOINCREMENT,
        entity_name TEXT UNIQUE NOT NULL,
        entity_type TEXT,  -- company, state_owned, subsidiary
        sector TEXT,        -- telecom, ev, battery, etc.
        parent_company TEXT,
        country_of_origin TEXT DEFAULT 'China'
    )
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_entity_name ON chinese_entities(entity_name)")

    # 3. Contract-Entity junction table (many-to-many)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS contract_entities (
        contract_id TEXT,
        entity_id INTEGER,
        mention_type TEXT,  -- winner, participant, subcontractor, mentioned
        confidence_score REAL DEFAULT 1.0,
        PRIMARY KEY (contract_id, entity_id),
        FOREIGN KEY (contract_id) REFERENCES contracts(contract_id),
        FOREIGN KEY (entity_id) REFERENCES chinese_entities(entity_id)
    )
    """)

    # 4. Temporal analysis table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS temporal_analysis (
        year INTEGER,
        month INTEGER,
        country TEXT,
        entity_id INTEGER,
        contract_count INTEGER DEFAULT 0,
        total_value REAL,
        PRIMARY KEY (year, month, country, entity_id),
        FOREIGN KEY (entity_id) REFERENCES chinese_entities(entity_id)
    )
    """)

    # 5. Processing log table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS processing_log (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        archive_path TEXT,
        year INTEGER,
        month INTEGER,
        xml_files_processed INTEGER,
        contracts_found INTEGER,
        processing_time_seconds REAL,
        processing_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT,
        error_message TEXT
    )
    """)

    # 6. Geographic distribution
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS geographic_distribution (
        country TEXT,
        entity_id INTEGER,
        first_appearance DATE,
        latest_appearance DATE,
        total_contracts INTEGER,
        total_value REAL,
        PRIMARY KEY (country, entity_id),
        FOREIGN KEY (entity_id) REFERENCES chinese_entities(entity_id)
    )
    """)

    # Pre-populate Chinese entities
    chinese_companies = [
        ('Huawei', 'company', 'telecommunications'),
        ('ZTE', 'company', 'telecommunications'),
        ('Lenovo', 'company', 'computers'),
        ('Xiaomi', 'company', 'electronics'),
        ('Alibaba', 'company', 'ecommerce'),
        ('Tencent', 'company', 'technology'),
        ('Baidu', 'company', 'internet'),
        ('ByteDance', 'company', 'social_media'),
        ('TikTok', 'subsidiary', 'social_media'),
        ('DJI', 'company', 'drones'),
        ('Dahua', 'company', 'surveillance'),
        ('Hikvision', 'company', 'surveillance'),
        ('BYD', 'company', 'electric_vehicles'),
        ('Geely', 'company', 'automotive'),
        ('NIO', 'company', 'electric_vehicles'),
        ('Xpeng', 'company', 'electric_vehicles'),
        ('CATL', 'company', 'batteries'),
        ('BOE', 'company', 'displays'),
        ('SMIC', 'company', 'semiconductors'),
        ('CRRC', 'state_owned', 'rail'),
        ('COMAC', 'state_owned', 'aerospace'),
        ('AVIC', 'state_owned', 'aerospace'),
        ('State Grid', 'state_owned', 'energy'),
        ('China Mobile', 'state_owned', 'telecommunications'),
        ('China Telecom', 'state_owned', 'telecommunications'),
        ('China Unicom', 'state_owned', 'telecommunications'),
    ]

    cursor.executemany("""
    INSERT OR IGNORE INTO chinese_entities (entity_name, entity_type, sector)
    VALUES (?, ?, ?)
    """, chinese_companies)

    # Create useful views

    # View: Contracts with Chinese entities
    cursor.execute("""
    CREATE VIEW IF NOT EXISTS china_contracts_view AS
    SELECT
        c.*,
        GROUP_CONCAT(e.entity_name, ', ') as chinese_entities,
        COUNT(DISTINCT ce.entity_id) as entity_count
    FROM contracts c
    JOIN contract_entities ce ON c.contract_id = ce.contract_id
    JOIN chinese_entities e ON ce.entity_id = e.entity_id
    GROUP BY c.contract_id
    """)

    # View: Annual summary
    cursor.execute("""
    CREATE VIEW IF NOT EXISTS annual_summary AS
    SELECT
        strftime('%Y', publication_date) as year,
        authority_country,
        e.entity_name,
        COUNT(*) as contract_count,
        SUM(contract_value) as total_value,
        AVG(contract_value) as avg_value
    FROM contracts c
    JOIN contract_entities ce ON c.contract_id = ce.contract_id
    JOIN chinese_entities e ON ce.entity_id = e.entity_id
    WHERE c.publication_date IS NOT NULL
    GROUP BY year, authority_country, e.entity_name
    ORDER BY year DESC, contract_count DESC
    """)

    # View: Entity dominance by country
    cursor.execute("""
    CREATE VIEW IF NOT EXISTS entity_dominance AS
    SELECT
        e.entity_name,
        e.sector,
        authority_country,
        COUNT(*) as contracts,
        MIN(publication_date) as first_contract,
        MAX(publication_date) as latest_contract,
        julianday(MAX(publication_date)) - julianday(MIN(publication_date)) as days_active
    FROM contracts c
    JOIN contract_entities ce ON c.contract_id = ce.contract_id
    JOIN chinese_entities e ON ce.entity_id = e.entity_id
    GROUP BY e.entity_name, authority_country
    ORDER BY contracts DESC
    """)

    conn.commit()
    conn.close()

    logging.info(f"Database created at {db_path}")
    return db_path

# Example queries to run after population:
USEFUL_QUERIES = """
-- Find temporal progression of Chinese presence
SELECT
    strftime('%Y', publication_date) as year,
    COUNT(DISTINCT c.contract_id) as contracts,
    COUNT(DISTINCT ce.entity_id) as unique_entities
FROM contracts c
JOIN contract_entities ce ON c.contract_id = ce.contract_id
GROUP BY year
ORDER BY year;

-- Top Chinese entities by country
SELECT
    authority_country,
    e.entity_name,
    COUNT(*) as contract_count
FROM contracts c
JOIN contract_entities ce ON c.contract_id = ce.contract_id
JOIN chinese_entities e ON ce.entity_id = e.entity_id
GROUP BY authority_country, e.entity_name
ORDER BY authority_country, contract_count DESC;

-- Sector penetration analysis
SELECT
    e.sector,
    COUNT(DISTINCT e.entity_id) as companies,
    COUNT(DISTINCT c.contract_id) as contracts,
    COUNT(DISTINCT c.authority_country) as countries
FROM chinese_entities e
JOIN contract_entities ce ON e.entity_id = ce.entity_id
JOIN contracts c ON ce.contract_id = c.contract_id
GROUP BY e.sector
ORDER BY contracts DESC;

-- Geographic expansion timeline
SELECT
    authority_country,
    MIN(publication_date) as first_chinese_contract,
    COUNT(DISTINCT ce.entity_id) as total_entities
FROM contracts c
JOIN contract_entities ce ON c.contract_id = ce.contract_id
GROUP BY authority_country
ORDER BY first_chinese_contract;
"""

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    db_path = create_database()
    print(f"Database created: {db_path}")
    print("\nUseful queries saved in USEFUL_QUERIES variable")

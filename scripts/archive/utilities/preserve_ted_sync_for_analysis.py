#!/usr/bin/env python3
"""
Preserve TED Sync Results for Further Analysis
Created: October 19, 2025
Purpose: Export the 51,139 flagged records to separate database before rollback
"""

import sqlite3
import json
from datetime import datetime

DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"
ANALYSIS_DB = "F:/OSINT_WAREHOUSE/ted_sync_analysis_20251019.db"

def main():
    print("=" * 80)
    print("PRESERVING TED SYNC DATA FOR ANALYSIS")
    print("=" * 80)
    print()
    print(f"Source Database: {DB_PATH}")
    print(f"Analysis Database: {ANALYSIS_DB}")
    print()

    # Connect to both databases
    source_conn = sqlite3.connect(DB_PATH, timeout=3600)
    source_conn.row_factory = sqlite3.Row
    analysis_conn = sqlite3.connect(ANALYSIS_DB)
    analysis_cursor = analysis_conn.cursor()

    print("[1/5] Creating analysis database structure...")

    # Create table to store all 51,139 flagged contracts
    analysis_cursor.execute('''
        CREATE TABLE IF NOT EXISTS flagged_contracts_full (
            id INTEGER PRIMARY KEY,
            document_id TEXT,
            notice_number TEXT,
            publication_date TEXT,
            iso_country TEXT,
            contract_title TEXT,
            cpv_code TEXT,
            ca_name TEXT,
            ca_country TEXT,
            contractor_name TEXT,
            contractor_country TEXT,
            contractor_address TEXT,
            contractor_city TEXT,
            value_total REAL,
            currency TEXT,
            award_date TEXT,
            chinese_entities TEXT,
            chinese_confidence REAL,
            chinese_indicators TEXT,
            detection_rationale TEXT,
            is_chinese_related BOOLEAN,
            sync_timestamp TEXT
        )
    ''')

    # Create table for entity matches
    analysis_cursor.execute('''
        CREATE TABLE IF NOT EXISTS entity_matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_name TEXT,
            contractor_name TEXT,
            contract_notice_number TEXT,
            contract_id INTEGER,
            match_timestamp TEXT
        )
    ''')

    # Create table for entity details
    analysis_cursor.execute('''
        CREATE TABLE IF NOT EXISTS chinese_entities_source (
            entity_id INTEGER,
            entity_name TEXT,
            entity_type TEXT,
            first_seen TEXT,
            last_seen TEXT,
            contracts_count INTEGER,
            total_value_eur REAL,
            countries_active TEXT,
            tech_areas TEXT
        )
    ''')

    # Create metadata table
    analysis_cursor.execute('''
        CREATE TABLE IF NOT EXISTS preservation_metadata (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')

    analysis_conn.commit()
    print("  Database structure created")
    print()

    # Store metadata
    print("[2/5] Storing preservation metadata...")
    metadata = {
        'preservation_timestamp': datetime.now().isoformat(),
        'source_database': DB_PATH,
        'sync_execution_date': '2025-10-19',
        'sync_duration_seconds': '1162',
        'records_before_sync': '295',
        'records_after_sync': '51139',
        'records_added': '50844',
        'purpose': 'Preserve flagged contracts for manual review before rollback',
        'issue_identified': 'False positives - European companies flagged as Chinese',
        'rollback_backup': 'osint_master_backup_20251019_105606.db'
    }

    for key, value in metadata.items():
        analysis_cursor.execute(
            'INSERT OR REPLACE INTO preservation_metadata (key, value) VALUES (?, ?)',
            (key, value)
        )

    analysis_conn.commit()
    print("  Metadata stored")
    print()

    # Copy all flagged contracts
    print("[3/5] Copying all 51,139 flagged contracts...")
    source_cursor = source_conn.cursor()

    source_cursor.execute('''
        SELECT
            id, document_id, notice_number, publication_date, iso_country,
            contract_title, cpv_code, ca_name, ca_country,
            contractor_name, contractor_country, contractor_address, contractor_city,
            value_total, currency, award_date,
            chinese_entities, chinese_confidence, chinese_indicators,
            detection_rationale, is_chinese_related
        FROM ted_contracts_production
        WHERE is_chinese_related = 1
    ''')

    contracts = source_cursor.fetchall()
    print(f"  Found {len(contracts):,} flagged contracts")

    timestamp = datetime.now().isoformat()

    for contract in contracts:
        analysis_cursor.execute('''
            INSERT INTO flagged_contracts_full VALUES
            (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (*contract, timestamp))

    analysis_conn.commit()
    print(f"  Copied {len(contracts):,} contracts to analysis database")
    print()

    # Copy entity matches
    print("[4/5] Copying entity match data...")
    source_cursor.execute('''
        SELECT
            tpcef.entity_name,
            tcp.contractor_name,
            tcp.notice_number,
            tcp.id
        FROM ted_contracts_production tcp
        JOIN ted_procurement_chinese_entities_found tpcef
            ON LOWER(tcp.contractor_name) = LOWER(tpcef.entity_name)
        WHERE tcp.is_chinese_related = 1
    ''')

    matches = source_cursor.fetchall()
    print(f"  Found {len(matches):,} entity matches")

    for match in matches:
        analysis_cursor.execute('''
            INSERT INTO entity_matches (entity_name, contractor_name, contract_notice_number, contract_id, match_timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (*match, timestamp))

    analysis_conn.commit()
    print(f"  Copied {len(matches):,} entity matches")
    print()

    # Copy source entity data
    print("[5/5] Copying Chinese entities source data...")
    source_cursor.execute('''
        SELECT entity_id, entity_name, entity_type, first_seen, last_seen,
               contracts_count, total_value_eur, countries_active, tech_areas
        FROM ted_procurement_chinese_entities_found
    ''')

    entities = source_cursor.fetchall()
    print(f"  Found {len(entities):,} entities in source table")

    for entity in entities:
        analysis_cursor.execute('''
            INSERT INTO chinese_entities_source VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', entity)

    analysis_conn.commit()
    print(f"  Copied {len(entities):,} entities")
    print()

    # Create summary statistics
    print("=" * 80)
    print("PRESERVATION SUMMARY")
    print("=" * 80)
    print()

    # Top entities by contract count
    analysis_cursor.execute('''
        SELECT entity_name, COUNT(*) as cnt
        FROM entity_matches
        GROUP BY entity_name
        ORDER BY cnt DESC
        LIMIT 20
    ''')

    top_entities = analysis_cursor.fetchall()
    print("Top 20 Entities (by contract count):")
    for i, (name, cnt) in enumerate(top_entities, 1):
        print(f"  {i:2d}. {name[:60]:60s} {cnt:6,} contracts")
    print()

    # Country distribution
    analysis_cursor.execute('''
        SELECT ca_country, COUNT(*) as cnt
        FROM flagged_contracts_full
        WHERE ca_country IS NOT NULL
        GROUP BY ca_country
        ORDER BY cnt DESC
        LIMIT 15
    ''')

    countries = analysis_cursor.fetchall()
    print("Top 15 Buyer Countries:")
    for i, (country, cnt) in enumerate(countries, 1):
        print(f"  {i:2d}. {country:5s} - {cnt:6,} contracts")
    print()

    # Statistics
    analysis_cursor.execute('SELECT COUNT(*) FROM flagged_contracts_full')
    total_contracts = analysis_cursor.fetchone()[0]

    analysis_cursor.execute('SELECT COUNT(DISTINCT entity_name) FROM entity_matches')
    unique_entities = analysis_cursor.fetchone()[0]

    analysis_cursor.execute('SELECT COUNT(*) FROM entity_matches')
    total_matches = analysis_cursor.fetchone()[0]

    analysis_cursor.execute('SELECT SUM(value_total) FROM flagged_contracts_full WHERE value_total IS NOT NULL')
    total_value = analysis_cursor.fetchone()[0]

    print("Final Statistics:")
    print(f"  Total contracts preserved: {total_contracts:,}")
    print(f"  Unique entities: {unique_entities:,}")
    print(f"  Total entity matches: {total_matches:,}")
    print(f"  Total contract value: €{total_value:,.2f}" if total_value else "  Total contract value: N/A")
    print()

    # Create indexes for analysis
    print("Creating indexes for analysis...")
    analysis_cursor.execute('CREATE INDEX IF NOT EXISTS idx_flagged_contractor ON flagged_contracts_full(contractor_name)')
    analysis_cursor.execute('CREATE INDEX IF NOT EXISTS idx_flagged_country ON flagged_contracts_full(ca_country)')
    analysis_cursor.execute('CREATE INDEX IF NOT EXISTS idx_matches_entity ON entity_matches(entity_name)')
    analysis_cursor.execute('CREATE INDEX IF NOT EXISTS idx_matches_contractor ON entity_matches(contractor_name)')
    analysis_conn.commit()
    print("  Indexes created")
    print()

    # Export summary JSON
    summary_file = "analysis/ted_sync_preservation_summary_20251019.json"
    summary = {
        'preservation_timestamp': datetime.now().isoformat(),
        'total_contracts': total_contracts,
        'unique_entities': unique_entities,
        'total_matches': total_matches,
        'total_value_eur': total_value,
        'top_20_entities': [
            {'entity_name': name, 'contract_count': cnt}
            for name, cnt in top_entities
        ],
        'top_15_countries': [
            {'country': country, 'contract_count': cnt}
            for country, cnt in countries
        ],
        'metadata': metadata
    }

    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"Summary exported to: {summary_file}")
    print()

    # Close connections
    source_conn.close()
    analysis_conn.close()

    print("=" * 80)
    print("PRESERVATION COMPLETE")
    print("=" * 80)
    print()
    print(f"Analysis database created: {ANALYSIS_DB}")
    print(f"  Size: {sqlite3.connect(ANALYSIS_DB).execute('SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()').fetchone()[0] / (1024**2):.2f} MB")
    print()
    print("You can now safely rollback the main database.")
    print("The flagged data is preserved for manual review and classification.")
    print()
    print("To analyze the preserved data:")
    print(f"  sqlite3 {ANALYSIS_DB}")
    print()
    print("Sample queries:")
    print("  SELECT * FROM flagged_contracts_full LIMIT 10;")
    print("  SELECT * FROM entity_matches WHERE entity_name LIKE '%GmbH%';")
    print("  SELECT * FROM preservation_metadata;")
    print()

if __name__ == "__main__":
    main()

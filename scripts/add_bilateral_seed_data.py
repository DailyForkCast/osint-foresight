#!/usr/bin/env python3
"""
Add seed bilateral investment data - high-profile deals
Quick script to populate bilateral_investments with known strategic deals
"""

import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path("F:/OSINT_WAREHOUSE/osint_master.db")

def add_seed_investments():
    """Add well-known high-profile China-Europe/US investments"""
    print("Adding seed bilateral investment data...")

    conn = sqlite3.connect(DB_PATH, timeout=60)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.commit()

    # Seed data: Major known investments
    seed_deals = [
        {
            'investment_id': 'FR_PSA_DONGFENG_2014',
            'country_code': 'FR',
            'transaction_date': '2014-02-19',
            'year': 2014,
            'investment_direction': 'inbound',
            'investment_type': 'acquisition',
            'investor_entity': 'Dongfeng Motor Corporation',
            'investor_entity_type': 'soe',
            'investor_country': 'China',
            'target_entity': 'PSA Peugeot Citroën',
            'target_entity_type': 'private',
            'target_country': 'France',
            'sector': 'Automotive',
            'subsector': 'Auto Manufacturing',
            'deal_value_usd': 900000000,
            'ownership_percentage': 14.1,
            'deal_status': 'completed',
            'strategic_asset': 1,
            'strategic_significance': 'First major Chinese investment in European auto industry',
            'source': 'Reuters',
            'source_url': 'https://www.reuters.com/article/us-peugeot-china-idUSBREA1I0PY20140219',
            'created_at': datetime.now().isoformat()
        },
        {
            'investment_id': 'CH_SINOCHEM_SYNGENTA_2017',
            'country_code': 'CH',
            'transaction_date': '2017-06-08',
            'year': 2017,
            'investment_direction': 'inbound',
            'investment_type': 'acquisition',
            'investor_entity': 'ChemChina (Sinochem)',
            'investor_entity_type': 'soe',
            'investor_country': 'China',
            'target_entity': 'Syngenta AG',
            'target_entity_type': 'private',
            'target_country': 'Switzerland',
            'sector': 'Agriculture',
            'subsector': 'Agricultural Chemicals',
            'deal_value_usd': 43000000000,
            'ownership_percentage': 100.0,
            'deal_status': 'completed',
            'strategic_asset': 1,
            'technology_transfer_involved': 1,
            'strategic_significance': 'Largest foreign acquisition by Chinese company (2017), agriculture technology',
            'controversy_notes': 'National security reviews in multiple countries. Technology transfer concerns.',
            'source': 'ChemChina official',
            'source_url': 'https://www.ft.com/content/7c6f4894-4c7c-11e7-a3f4-c742b9791d43',
            'created_at': datetime.now().isoformat()
        },
        {
            'investment_id': 'US_SMITHFIELD_SHUANGHUI_2013',
            'country_code': 'US',
            'transaction_date': '2013-09-26',
            'year': 2013,
            'investment_direction': 'inbound',
            'investment_type': 'acquisition',
            'investor_entity': 'Shuanghui International (WH Group)',
            'investor_entity_type': 'private',
            'investor_country': 'China',
            'target_entity': 'Smithfield Foods',
            'target_entity_type': 'private',
            'target_country': 'United States',
            'sector': 'Food & Agriculture',
            'subsector': 'Meat Processing',
            'deal_value_usd': 7100000000,
            'ownership_percentage': 100.0,
            'deal_status': 'completed',
            'national_security_review': 1,
            'strategic_significance': 'Largest Chinese acquisition of US company at the time. Food security concerns.',
            'controversy_notes': 'CFIUS review due to food security implications. Largest pork producer in US.',
            'source': 'SEC filing',
            'source_url': 'https://www.sec.gov/Archives/edgar/data/93388/000119312513352948/d592850ddefm14a.htm',
            'created_at': datetime.now().isoformat()
        },
        {
            'investment_id': 'IT_TYRE_PIRELLI_2015',
            'country_code': 'IT',
            'transaction_date': '2015-03-23',
            'year': 2015,
            'investment_direction': 'inbound',
            'investment_type': 'acquisition',
            'investor_entity': 'ChemChina',
            'investor_entity_type': 'soe',
            'investor_country': 'China',
            'target_entity': 'Pirelli & C. SpA',
            'target_entity_type': 'private',
            'target_country': 'Italy',
            'sector': 'Automotive',
            'subsector': 'Tire Manufacturing',
            'deal_value_usd': 7900000000,
            'ownership_percentage': 100.0,
            'deal_status': 'completed',
            'strategic_asset': 1,
            'technology_transfer_involved': 1,
            'strategic_significance': 'Premium tire technology acquisition, Formula 1 supplier',
            'source': 'ChemChina announcement',
            'source_url': 'https://www.reuters.com/article/us-pirelli-chemchina-idUSKBN0MJ0KX20150323',
            'created_at': datetime.now().isoformat()
        },
        {
            'investment_id': 'SE_VOLVO_GEELY_2010',
            'country_code': 'SE',
            'transaction_date': '2010-08-02',
            'year': 2010,
            'investment_direction': 'inbound',
            'investment_type': 'acquisition',
            'investor_entity': 'Geely Holding Group',
            'investor_entity_type': 'private',
            'investor_country': 'China',
            'target_entity': 'Volvo Cars',
            'target_entity_type': 'private',
            'target_country': 'Sweden',
            'sector': 'Automotive',
            'subsector': 'Auto Manufacturing',
            'deal_value_usd': 1800000000,
            'ownership_percentage': 100.0,
            'deal_status': 'completed',
            'strategic_asset': 1,
            'technology_transfer_involved': 1,
            'strategic_significance': 'Major European automotive brand acquisition, safety technology transfer',
            'source': 'Geely official',
            'source_url': 'https://www.bbc.com/news/business-10807218',
            'created_at': datetime.now().isoformat()
        }
    ]

    # Check existing
    cursor = conn.cursor()
    cursor.execute("SELECT investment_id FROM bilateral_investments")
    existing_ids = set(row[0] for row in cursor.fetchall())

    new_count = 0
    for deal in seed_deals:
        if deal['investment_id'] in existing_ids:
            print(f"  [SKIP] {deal['investment_id']} already exists")
            continue

        # Insert
        columns = ', '.join(deal.keys())
        placeholders = ', '.join(['?' for _ in deal])
        query = f"INSERT INTO bilateral_investments ({columns}) VALUES ({placeholders})"

        try:
            cursor.execute(query, list(deal.values()))
            print(f"  [OK] Inserted {deal['investment_id']}")
            new_count += 1
        except Exception as e:
            print(f"  [ERROR] Failed to insert {deal['investment_id']}: {e}")

    conn.commit()

    # Summary
    cursor.execute("SELECT COUNT(*) FROM bilateral_investments")
    total = cursor.fetchone()[0]

    print(f"\n{'='*60}")
    print(f"Added {new_count} new investments")
    print(f"Total bilateral investments: {total}")
    print(f"{'='*60}")

    conn.close()

if __name__ == "__main__":
    add_seed_investments()

#!/usr/bin/env python3
"""
Process PatentsView Disambiguated Data for Chinese Patent Detection (2020-2025)
CORRECTED: Uses patent number ranges instead of corrupted filing_date field
"""

import csv
import sqlite3
import json
from datetime import datetime
from collections import Counter

# Paths
PATENTSVIEW_DIR = "F:/USPTO_PATENTSVIEW"
DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"

# Chinese detection patterns (same as 2011-2020 methodology)
CHINESE_COUNTRY_CODES = {'CN', 'CHN', 'HK', 'MO', 'MAC'}

CHINESE_CITIES = {
    'BEIJING', 'SHANGHAI', 'SHENZHEN', 'GUANGZHOU', 'HANGZHOU', 'NANJING',
    'WUHAN', 'CHENGDU', 'XIAN', 'TIANJIN', 'CHONGQING', 'SUZHOU', 'NINGBO',
    'QINGDAO', 'DALIAN', 'XIAMEN', 'CHANGSHA', 'ZHENGZHOU', 'HEFEI', 'JINAN',
    'KUNMING', 'HARBIN', 'SHENYANG', 'CHANGCHUN', 'URUMQI', 'LANZHOU', 'HAIKOU',
    'NANCHANG', 'GUIYANG', 'TAIYUAN', 'SHIJIAZHUANG', 'HOHHOT', 'YINCHUAN',
    'XINING', 'NANNING', 'FUZHOU', 'HONG KONG', 'MACAU', 'TAIPEI', 'SHANTOU',
    'DONGGUAN', 'FOSHAN', 'ZHUHAI'
}

CHINESE_PROVINCES = {
    'BEIJING', 'SHANGHAI', 'TIANJIN', 'CHONGQING', 'HEBEI', 'SHANXI',
    'LIAONING', 'JILIN', 'HEILONGJIANG', 'JIANGSU', 'ZHEJIANG', 'ANHUI',
    'FUJIAN', 'JIANGXI', 'SHANDONG', 'HENAN', 'HUBEI', 'HUNAN', 'GUANGDONG',
    'HAINAN', 'SICHUAN', 'GUIZHOU', 'YUNNAN', 'SHAANXI', 'GANSU', 'QINGHAI',
    'TAIWAN', 'GUANGXI', 'INNER MONGOLIA', 'TIBET', 'NINGXIA', 'XINJIANG'
}

CHINESE_COMPANIES = {
    'HUAWEI', 'ZTE', 'TENCENT', 'ALIBABA', 'BAIDU', 'XIAOMI', 'OPPO', 'VIVO',
    'BOE', 'LENOVO', 'DJI', 'BYTEDANCE', 'HAIER', 'MIDEA', 'GREE', 'TCL',
    'BYD', 'GEELY', 'SMIC', 'HIKVISION', 'DAHUA', 'MEGVII', 'SENSETIME'
}

def estimate_grant_year_from_patent_id(patent_id_str):
    """
    Estimate grant year from sequential patent number
    (filing_date field is corrupted, so use patent number milestones)
    """
    try:
        # Remove design patent prefix if present
        patent_num_str = patent_id_str.strip().lstrip('D')
        patent_num = int(patent_num_str)
    except:
        return None

    # Use milestones to estimate grant year
    if patent_num < 6000000:
        return None  # Pre-2000, outside our range
    elif patent_num < 7000000:
        return 2002
    elif patent_num < 8000000:
        return 2011
    elif patent_num < 9000000:
        return 2015
    elif patent_num < 10000000:
        return 2017
    elif patent_num < 10500000:
        return 2019
    elif patent_num < 11000000:
        return 2020
    elif patent_num < 11250000:
        return 2021
    elif patent_num < 11500000:
        return 2022
    elif patent_num < 11750000:
        return 2022
    elif patent_num < 12000000:
        return 2023
    elif patent_num < 12250000:
        return 2024
    elif patent_num < 12500000:
        return 2024
    else:
        return 2025

def score_chinese_entity(assignee_org, location_data):
    """
    Apply 10-tier scoring methodology
    Returns: (score, signals, confidence)
    """
    score = 0
    signals = []

    # Location fields
    city = (location_data.get('city') or '').upper().strip()
    state = (location_data.get('state') or '').upper().strip()
    country = (location_data.get('country') or '').upper().strip()

    # 1. Country code (100 points)
    if country in CHINESE_COUNTRY_CODES:
        score += 100
        signals.append('country_CN')

    # 2. Known Chinese company (80 points)
    assignee_upper = (assignee_org or '').upper()
    for company in CHINESE_COMPANIES:
        if company in assignee_upper:
            score += 80
            signals.append(f'company_{company}')
            break

    # 3. Chinese city (50 points)
    if city in CHINESE_CITIES:
        score += 50
        signals.append(f'city_{city}')

    # 4. Chinese province (40 points)
    if state in CHINESE_PROVINCES:
        score += 40
        signals.append(f'province_{state}')

    # Determine confidence
    if score >= 100:
        confidence = 'VERY_HIGH'
    elif score >= 70:
        confidence = 'HIGH'
    elif score >= 50:
        confidence = 'MEDIUM'
    else:
        confidence = 'LOW'

    return score, signals, confidence

def read_tsv(filepath, max_rows=None):
    """Read TSV file with progress"""
    print(f"Reading: {filepath}")
    count = 0
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        reader = csv.DictReader(f, delimiter='\t', quoting=csv.QUOTE_ALL)
        for row in reader:
            yield row
            count += 1
            if max_rows and count >= max_rows:
                break
            if count % 500000 == 0:
                print(f"  Read {count:,} rows...")

def create_tables(conn):
    """Create tables for PatentsView data"""
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patentsview_patents_chinese (
            patent_id TEXT PRIMARY KEY,
            filing_date TEXT,
            filing_year INTEGER,
            assignee_id TEXT,
            assignee_organization TEXT,
            assignee_city TEXT,
            assignee_state TEXT,
            assignee_country TEXT,
            location_id TEXT,
            detection_score INTEGER,
            detection_signals TEXT,
            confidence TEXT,
            created_at TEXT
        )
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_pv_chinese_year
        ON patentsview_patents_chinese(filing_year)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_pv_chinese_confidence
        ON patentsview_patents_chinese(confidence)
    """)

    conn.commit()
    print("Tables created")

def main():
    print("="*80)
    print("PATENTSVIEW CORRECTED PROCESSOR (2020-2025)")
    print("="*80)
    print("Using patent number ranges instead of corrupted filing_date")
    print(f"Data dir: {PATENTSVIEW_DIR}")
    print(f"Database: {DB_PATH}")
    print(f"Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    conn = sqlite3.connect(DB_PATH, timeout=300)
    create_tables(conn)
    cursor = conn.cursor()

    # STEP 1: Load locations into memory (only 98K records)
    print("\n" + "="*80)
    print("STEP 1: Loading location data")
    print("="*80)

    locations = {}
    for row in read_tsv(f"{PATENTSVIEW_DIR}/g_location_disambiguated.tsv"):
        location_id = row.get('location_id', '').strip()
        if location_id:
            locations[location_id] = {
                'city': row.get('disambig_city', ''),
                'state': row.get('disambig_state', ''),
                'country': row.get('disambig_country', '')
            }

    print(f"Loaded {len(locations):,} locations")

    # STEP 2: Process assignees directly (NO pre-filtering by corrupted date)
    print("\n" + "="*80)
    print("STEP 2: Chinese Entity Detection (All Patents)")
    print("="*80)
    print("Processing ALL assignees, assigning years from patent numbers")

    chinese_found = 0
    confidence_dist = Counter()
    year_dist = Counter()
    batch = []
    batch_size = 10000
    processed = 0
    skipped_no_year = 0

    for row in read_tsv(f"{PATENTSVIEW_DIR}/g_assignee_disambiguated.tsv"):
        processed += 1
        if processed % 500000 == 0:
            print(f"  Processed {processed:,} assignees | Chinese found: {chinese_found:,} | Skipped (no year): {skipped_no_year:,}")

        patent_id = row.get('patent_id', '').strip()

        # Estimate year from patent number
        year = estimate_grant_year_from_patent_id(patent_id)

        if year is None:
            skipped_no_year += 1
            continue

        # Filter to 2020-2025 range AFTER year assignment
        if not (2020 <= year <= 2025):
            continue

        # Get assignee info
        assignee_id = row.get('assignee_id', '').strip()
        assignee_org = row.get('disambig_assignee_organization', '').strip()
        location_id = row.get('location_id', '').strip()

        # Get location data
        location_data = locations.get(location_id, {})

        # Apply Chinese detection
        score, signals, confidence = score_chinese_entity(assignee_org, location_data)

        # Only keep MEDIUM, HIGH, VERY_HIGH
        if confidence in ('MEDIUM', 'HIGH', 'VERY_HIGH'):
            batch.append((
                patent_id,
                '',  # filing_date is corrupted, leave blank
                year,
                assignee_id,
                assignee_org,
                location_data.get('city', ''),
                location_data.get('state', ''),
                location_data.get('country', ''),
                location_id,
                score,
                ','.join(signals),
                confidence,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ))

            chinese_found += 1
            confidence_dist[confidence] += 1
            year_dist[year] += 1

            if len(batch) >= batch_size:
                cursor.executemany("""
                    INSERT OR REPLACE INTO patentsview_patents_chinese
                    (patent_id, filing_date, filing_year, assignee_id, assignee_organization,
                     assignee_city, assignee_state, assignee_country, location_id,
                     detection_score, detection_signals, confidence, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, batch)
                conn.commit()
                batch = []

    # Final batch
    if batch:
        cursor.executemany("""
            INSERT OR REPLACE INTO patentsview_patents_chinese
            (patent_id, filing_date, filing_year, assignee_id, assignee_organization,
             assignee_city, assignee_state, assignee_country, location_id,
             detection_score, detection_signals, confidence, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, batch)
        conn.commit()

    print(f"\n{'='*80}")
    print("RESULTS")
    print(f"{'='*80}")
    print(f"Total assignees processed: {processed:,}")
    print(f"Skipped (no year): {skipped_no_year:,}")
    print(f"Chinese patents found: {chinese_found:,}")

    print("\nConfidence distribution:")
    for conf in ['VERY_HIGH', 'HIGH', 'MEDIUM']:
        count = confidence_dist.get(conf, 0)
        pct = (count / chinese_found * 100) if chinese_found > 0 else 0
        print(f"  {conf:12s}: {count:,} ({pct:.1f}%)")

    print("\nYear distribution (2020-2025):")
    total_2020_2025 = 0
    for year in sorted(year_dist.keys()):
        count = year_dist[year]
        total_2020_2025 += count
        print(f"  {year}: {count:,} patents")
    print(f"\nTotal 2020-2025: {total_2020_2025:,} patents")

    conn.close()

    print(f"\n{'='*80}")
    print("PROCESSING COMPLETE")
    print(f"{'='*80}")
    print(f"End: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == '__main__':
    main()

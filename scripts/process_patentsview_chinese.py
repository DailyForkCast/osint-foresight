#!/usr/bin/env python3
"""
Process PatentsView Data for Chinese Patent Detection (2021-2025 Extension)
Applies same 10-tier scoring methodology to PatentsView TSV format
"""

import csv
import sqlite3
import json
import re
from datetime import datetime
from collections import Counter, defaultdict

# Paths
PATENTSVIEW_DIR = "F:/USPTO_PATENTSVIEW"
DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"
OUTPUT_DIR = "C:/Projects/OSINT - Foresight/analysis"

# Chinese detection patterns (same as existing methodology)
CHINESE_COUNTRY_CODES = {'CN', 'CHN', 'HK', 'MO', 'MAC'}
CHINESE_POSTAL_PATTERN = re.compile(r'\b\d{6}\b')  # Chinese postal codes

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

CHINESE_DISTRICTS = {
    'HAIDIAN', 'CHAOYANG', 'PUDONG', 'NANSHAN', 'FUTIAN', 'LUOHU',
    'BAOAN', 'LONGGANG', 'YANTIAN', 'XUHUI', 'JINGAN', 'CHANGNING',
    'TIANHE', 'YUEXIU', 'HAIZHU', 'LIWAN'
}

# Known Chinese companies (top ones)
CHINESE_COMPANIES = {
    'HUAWEI', 'ZTE', 'TENCENT', 'ALIBABA', 'BAIDU', 'XIAOMI', 'OPPO', 'VIVO',
    'BOE', 'LENOVO', 'DJI', 'BYTEDANCE', 'HAIER', 'MIDEA', 'GREE', 'TCL',
    'BYD', 'GEELY', 'SMIC', 'HIKVISION', 'DAHUA', 'MEGVII', 'SENSETIME'
}

def score_chinese_entity(assignee_name, location_data):
    """
    Apply 10-tier scoring to determine if entity is Chinese
    Returns: (score, signals_detected, confidence_level)
    """
    score = 0
    signals = []

    # Location data: city, state, country
    city = (location_data.get('city') or '').upper().strip()
    state = (location_data.get('state') or '').upper().strip()
    country = (location_data.get('country') or '').upper().strip()

    # 1. Country code (100 points)
    if country in CHINESE_COUNTRY_CODES:
        score += 100
        signals.append('country_CN')

    # 2. Known Chinese company (80 points)
    assignee_upper = (assignee_name or '').upper()
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

    # 5. Chinese district (25 points)
    for district in CHINESE_DISTRICTS:
        if district in city:
            score += 25
            signals.append(f'district_{district}')
            break

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

def read_tsv_file(filepath, max_rows=None):
    """Read TSV file and yield rows as dictionaries"""
    print(f"Reading: {filepath}")
    count = 0
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            yield row
            count += 1
            if max_rows and count >= max_rows:
                break
            if count % 100000 == 0:
                print(f"  Read {count:,} rows...")

def create_patentsview_tables(conn):
    """Create tables for PatentsView data"""
    cursor = conn.cursor()

    # PatentsView patents table (2021-2025 focus)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patentsview_patents (
            patent_id TEXT PRIMARY KEY,
            patent_date TEXT,
            patent_title TEXT,
            patent_abstract TEXT,
            patent_year INTEGER,
            num_claims INTEGER,
            patent_type TEXT
        )
    """)

    # PatentsView Chinese patents
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patentsview_patents_chinese (
            patent_id TEXT PRIMARY KEY,
            patent_date TEXT,
            patent_year INTEGER,
            assignee_id TEXT,
            assignee_name TEXT,
            assignee_city TEXT,
            assignee_state TEXT,
            assignee_country TEXT,
            detection_score INTEGER,
            detection_signals TEXT,
            confidence TEXT,
            created_at TEXT
        )
    """)

    # Indexes
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_pv_patents_year
        ON patentsview_patents(patent_year)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_pv_chinese_year
        ON patentsview_patents_chinese(patent_year)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_pv_chinese_confidence
        ON patentsview_patents_chinese(confidence)
    """)

    conn.commit()
    print("✅ PatentsView tables created")

def process_patents(conn):
    """Load core patent data (focusing on 2021-2025)"""
    print("\n" + "="*80)
    print("STEP 1: Processing Patent Core Data (2021-2025)")
    print("="*80)

    cursor = conn.cursor()
    patent_file = f"{PATENTSVIEW_DIR}/patent.tsv"

    # Load patents from 2021-2025
    patents_loaded = 0
    batch = []
    batch_size = 10000

    for row in read_tsv_file(patent_file):
        patent_id = row.get('patent_id', '').strip()
        patent_date = row.get('patent_date', '').strip()

        # Extract year
        if patent_date and len(patent_date) >= 4:
            try:
                year = int(patent_date[:4])
            except:
                continue
        else:
            continue

        # Focus on 2021-2025
        if year < 2021:
            continue

        batch.append((
            patent_id,
            patent_date,
            row.get('patent_title', ''),
            row.get('patent_abstract', ''),
            year,
            row.get('num_claims', None),
            row.get('patent_type', '')
        ))

        if len(batch) >= batch_size:
            cursor.executemany("""
                INSERT OR IGNORE INTO patentsview_patents
                (patent_id, patent_date, patent_title, patent_abstract,
                 patent_year, num_claims, patent_type)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, batch)
            conn.commit()
            patents_loaded += len(batch)
            print(f"  Loaded {patents_loaded:,} patents (2021-2025)")
            batch = []

    # Final batch
    if batch:
        cursor.executemany("""
            INSERT OR IGNORE INTO patentsview_patents
            (patent_id, patent_date, patent_title, patent_abstract,
             patent_year, num_claims, patent_type)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, batch)
        conn.commit()
        patents_loaded += len(batch)

    print(f"\n✅ Loaded {patents_loaded:,} patents from 2021-2025")
    return patents_loaded

def process_chinese_detection(conn):
    """Apply Chinese entity detection to PatentsView data"""
    print("\n" + "="*80)
    print("STEP 2: Chinese Entity Detection")
    print("="*80)

    cursor = conn.cursor()

    # Load location data into memory
    print("\nLoading assignee location data...")
    location_file = f"{PATENTSVIEW_DIR}/location_assignee.tsv"
    locations = {}

    for row in read_tsv_file(location_file):
        location_id = row.get('location_id', '').strip()
        locations[location_id] = {
            'city': row.get('city', ''),
            'state': row.get('state', ''),
            'country': row.get('country', '')
        }

    print(f"  Loaded {len(locations):,} location records")

    # Load assignee data
    print("\nLoading assignee data...")
    assignee_file = f"{PATENTSVIEW_DIR}/assignee.tsv"
    assignees = {}

    for row in read_tsv_file(assignee_file):
        assignee_id = row.get('assignee_id', '').strip()
        assignees[assignee_id] = {
            'name': row.get('assignee_name', ''),
            'location_id': row.get('location_id', '')
        }

    print(f"  Loaded {len(assignees):,} assignee records")

    # Process patent-assignee linkages
    print("\nProcessing patent-assignee linkages for Chinese detection...")
    patent_assignee_file = f"{PATENTSVIEW_DIR}/patent_assignee.tsv"

    chinese_found = 0
    confidence_dist = Counter()
    batch = []
    batch_size = 10000
    processed = 0

    for row in read_tsv_file(patent_assignee_file):
        processed += 1
        if processed % 100000 == 0:
            print(f"  Processed {processed:,} linkages | Chinese found: {chinese_found:,}")

        patent_id = row.get('patent_id', '').strip()
        assignee_id = row.get('assignee_id', '').strip()

        # Check if patent is in 2021-2025 range
        cursor.execute("""
            SELECT patent_year, patent_date
            FROM patentsview_patents
            WHERE patent_id = ?
        """, (patent_id,))

        result = cursor.fetchone()
        if not result:
            continue

        year, patent_date = result

        # Get assignee info
        assignee_info = assignees.get(assignee_id, {})
        assignee_name = assignee_info.get('name', '')
        location_id = assignee_info.get('location_id', '')

        # Get location info
        location_data = locations.get(location_id, {})

        # Apply Chinese detection scoring
        score, signals, confidence = score_chinese_entity(assignee_name, location_data)

        # Only keep MEDIUM, HIGH, VERY_HIGH
        if confidence in ('MEDIUM', 'HIGH', 'VERY_HIGH'):
            batch.append((
                patent_id,
                patent_date,
                year,
                assignee_id,
                assignee_name,
                location_data.get('city', ''),
                location_data.get('state', ''),
                location_data.get('country', ''),
                score,
                ','.join(signals),
                confidence,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ))

            chinese_found += 1
            confidence_dist[confidence] += 1

            if len(batch) >= batch_size:
                cursor.executemany("""
                    INSERT OR REPLACE INTO patentsview_patents_chinese
                    (patent_id, patent_date, patent_year, assignee_id, assignee_name,
                     assignee_city, assignee_state, assignee_country,
                     detection_score, detection_signals, confidence, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, batch)
                conn.commit()
                batch = []

    # Final batch
    if batch:
        cursor.executemany("""
            INSERT OR REPLACE INTO patentsview_patents_chinese
            (patent_id, patent_date, patent_year, assignee_id, assignee_name,
             assignee_city, assignee_state, assignee_country,
             detection_score, detection_signals, confidence, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, batch)
        conn.commit()

    print(f"\n✅ Chinese patents found: {chinese_found:,}")
    print(f"\nConfidence distribution:")
    for conf in ['VERY_HIGH', 'HIGH', 'MEDIUM']:
        count = confidence_dist.get(conf, 0)
        pct = (count / chinese_found * 100) if chinese_found > 0 else 0
        print(f"  {conf:12s}: {count:,} ({pct:.1f}%)")

    return chinese_found

def main():
    print("="*80)
    print("PATENTSVIEW CHINESE PATENT PROCESSOR (2021-2025)")
    print("="*80)
    print(f"Data directory: {PATENTSVIEW_DIR}")
    print(f"Database: {DB_PATH}")
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Connect to database
    conn = sqlite3.connect(DB_PATH, timeout=300)

    # Create tables
    create_patentsview_tables(conn)

    # Process patents (2021-2025)
    patents_loaded = process_patents(conn)

    if patents_loaded == 0:
        print("\n⚠️  No patents loaded. Check if TSV files are extracted.")
        return

    # Process Chinese detection
    chinese_found = process_chinese_detection(conn)

    conn.close()

    print(f"\n{'='*80}")
    print("PROCESSING COMPLETE")
    print(f"{'='*80}")
    print(f"Total patents loaded (2021-2025): {patents_loaded:,}")
    print(f"Chinese patents identified: {chinese_found:,}")
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == '__main__':
    main()

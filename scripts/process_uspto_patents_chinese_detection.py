#!/usr/bin/env python3
"""
Process USPTO Patent Filewrapper JSON (2011-2020)
Multi-signal Chinese entity detection with confidence scoring
"""

import json
import zipfile
import sqlite3
from pathlib import Path
from datetime import datetime
from collections import Counter

# File paths
ZIP_PATH = "F:/USPTO Data/2011-2020-patent-filewrapper-full-json-20251005.zip"
DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"
CHECKPOINT_FILE = "C:/Projects/OSINT - Foresight/data/temp/uspto_patent_checkpoint.json"

# Load Chinese entity detection lists
CHINESE_CITIES = {
    'BEIJING', 'SHANGHAI', 'SHENZHEN', 'GUANGZHOU', 'HANGZHOU', 'NANJING',
    'WUHAN', 'CHENGDU', 'TIANJIN', 'CHONGQING', 'SUZHOU', 'XIAN', "XI'AN",
    'DONGGUAN', 'QINGDAO', 'DALIAN', 'SHENYANG', 'HARBIN', 'CHANGSHA',
    'KUNMING', 'XIAMEN', 'FOSHAN', 'NINGBO', 'ZHENGZHOU', 'JINAN', 'HEFEI',
    'FUZHOU', 'CHANGCHUN', 'SHIJIAZHUANG', 'TAIYUAN', 'HOHHOT', 'LANZHOU',
    'XINING', 'YINCHUAN', 'URUMQI', 'LHASA', 'NANNING', 'HAIKOU', 'GUIYANG',
    'NANCHANG', 'WENZHOU', 'ZHUHAI', 'SHANTOU', 'HUIZHOU'
}

# Chinese provinces and autonomous regions
CHINESE_PROVINCES = {
    'ANHUI', 'FUJIAN', 'GANSU', 'GUANGDONG', 'GUIZHOU', 'HAINAN', 'HEBEI',
    'HEILONGJIANG', 'HENAN', 'HUBEI', 'HUNAN', 'JIANGSU', 'JIANGXI', 'JILIN',
    'LIAONING', 'QINGHAI', 'SHAANXI', 'SHANDONG', 'SHANXI', 'SICHUAN',
    'YUNNAN', 'ZHEJIANG',
    'GUANGXI', 'INNER MONGOLIA', 'NINGXIA', 'TIBET', 'XINJIANG'
}

# Tech hub districts
CHINESE_DISTRICTS = {
    'HAIDIAN', 'PUDONG', 'NANSHAN', 'ZHONGGUANCUN', 'LUOHU', 'FUTIAN',
    'SONGJIANG', 'MINHANG', 'BAOSHAN', 'CHAOYANG', 'FENGTAI'
}

# Chinese street patterns (Pinyin romanization)
CHINESE_STREET_PATTERNS = {
    ' LU', ' ROAD', ' JIE', ' STREET', ' DADAO', ' AVENUE',
    ' XIANG', ' LANE', ' HUTONG', ' ALLEY'
}

PRC_COMPANIES = {
    'HUAWEI', 'ZTE', 'XIAOMI', 'OPPO', 'VIVO', 'ALIBABA', 'TENCENT', 'BAIDU',
    'BYTEDANCE', 'TIKTOK', 'LENOVO', 'DJI', 'BYD', 'HIKVISION', 'DAHUA',
    'SENSETIME', 'MEGVII', 'XPENG', 'NIO INC', 'GEELY', 'BOE TECHOLOG',
    'TCL', 'HAIER', 'MIDEA', 'GREE ELECTRIC', 'HISENSE', 'CATL',
    'CONTEMPORARY AMPEREX', 'SMIC', 'SEMICONDUCTOR MANUFACTURING INTERNATIONAL',
    'UNISOC', 'SPREADTRUM', 'ROCKCHIP', 'SINOPEC', 'PETROCHINA', 'CNOOC',
    'CHINA NATIONAL PETROLEUM', 'ICBC', 'BANK OF CHINA', 'CHINA CONSTRUCTION BANK',
    'AVIC', 'COMAC', 'NORINCO', 'NUCTECH', 'CASIC', 'CASC',
    'CHINA MOBILE', 'CHINA TELECOM', 'CHINA UNICOM'
}

def is_chinese_postal_code(postal_code):
    """Check if postal code matches Chinese 6-digit format"""
    if not postal_code:
        return False
    postal_str = str(postal_code).strip()
    if len(postal_str) == 6 and postal_str.isdigit():
        first_digit = int(postal_str[0])
        return 1 <= first_digit <= 9
    return False

def check_chinese_company(name):
    """Check if name contains known Chinese company with word boundaries"""
    if not name:
        return None
    name_upper = name.upper()

    # Special handling for short names that need word boundaries
    special_cases = {
        'NIO': ['NIO INC', 'NIO USA', 'NEXTEV'],
        'BOE': ['BOE TECHOLOG', 'BEIJING BOE'],
        'TCL': ['TCL CORP', 'TCL COMM'],
        'BYD': ['BYD COMPANY', 'BYD AUTO', 'BYD BATTERY'],
        'DJI': ['DJI INNOV', 'DJI TECHNO'],
    }

    for company, patterns in special_cases.items():
        for pattern in patterns:
            if pattern in name_upper:
                return company

    # Check other companies
    for company in PRC_COMPANIES:
        if len(company) > 4 and company in name_upper:
            return company

    return None

def detect_chinese_entity(data):
    """
    Multi-signal Chinese entity detection with confidence scoring

    Returns: (is_chinese, confidence_score, signals_triggered)
    """
    score = 0
    signals = []

    # Extract relevant fields
    country_code = None
    city = None
    assignee_name = None
    assignee_address = None
    postal_code = None
    inventor_countries = []

    # Check assigneeBag
    assignment_bag = data.get('assignmentBag', [])
    if assignment_bag:
        for assignment in assignment_bag:
            assignee_bag = assignment.get('assigneeBag', [])
            for assignee in assignee_bag:
                assignee_name = assignee.get('assigneeNameText', '')
                addr = assignee.get('assigneeAddress', {})
                country_code = addr.get('geographicRegionCode') or addr.get('countryCode')
                city = addr.get('cityName')
                postal_code = addr.get('postalCode')
                assignee_address = addr.get('addressLineOneText', '')

                # TIER 1: Country code (100 points)
                if country_code in ('CN', 'CHN', 'HK', 'MO'):
                    # High confidence - these are definitively Chinese codes
                    score += 100
                    signals.append(f'country_{country_code}')
                elif country_code == 'JPX':
                    # JPX sometimes used for China - verify with city
                    if city and city.upper() in CHINESE_CITIES:
                        score += 100
                        signals.append(f'country_JPX_verified')

                # TIER 2: Known Chinese company (80 points)
                company_match = check_chinese_company(assignee_name)
                if company_match:
                    score += 80
                    signals.append(f'company_{company_match}')

                # TIER 2: Chinese city (50 points)
                if city and city.upper() in CHINESE_CITIES:
                    score += 50
                    signals.append(f'city_{city.upper()}')

                # TIER 3: Postal code (60 points)
                if is_chinese_postal_code(postal_code):
                    score += 60
                    signals.append(f'postal_{postal_code}')

                # TIER 3: Address contains "CHINA" (30 points)
                if assignee_address and 'CHINA' in assignee_address.upper():
                    score += 30
                    signals.append('address_china')

                # TIER 4: Chinese province (40 points)
                full_address = f"{assignee_address} {city or ''}".upper()
                for province in CHINESE_PROVINCES:
                    if province in full_address:
                        score += 40
                        signals.append(f'province_{province}')
                        break

                # TIER 4: Chinese district (25 points)
                for district in CHINESE_DISTRICTS:
                    if district in full_address:
                        score += 25
                        signals.append(f'district_{district}')
                        break

                # TIER 4: Chinese street pattern (15 points)
                for pattern in CHINESE_STREET_PATTERNS:
                    if pattern in full_address:
                        score += 15
                        signals.append(f'street_pattern')
                        break

    # Check for +86 phone numbers in correspondence addresses
    correspondence_bag = assignment_bag[0].get('correspondenceAddressBag', []) if assignment_bag else []
    for corr_addr in correspondence_bag:
        # Check for telecommunication numbers
        if 'telecommunicationNumber' in str(corr_addr):
            telecom_num = str(corr_addr.get('telecommunicationNumber', ''))
            if '+86' in telecom_num or telecom_num.startswith('86') and len(telecom_num) > 10:
                score += 50
                signals.append('phone_cn')

    # Check inventorBag
    app_metadata = data.get('applicationMetaData', {})
    inventor_bag = app_metadata.get('inventorBag', [])
    for inventor in inventor_bag:
        inv_country = inventor.get('countryCode')
        if inv_country:
            inventor_countries.append(inv_country)

            # Chinese inventors (20 points each, max 60)
            if inv_country in ('CN', 'CHN', 'HK', 'MO'):
                score += min(20, 60 - score % 60)
                signals.append(f'inventor_{inv_country}')

    # Determine final classification
    is_chinese = score >= 50  # Threshold for inclusion

    # Confidence levels
    if score >= 100:
        confidence = 'VERY_HIGH'
    elif score >= 70:
        confidence = 'HIGH'
    elif score >= 50:
        confidence = 'MEDIUM'
    else:
        confidence = 'LOW'

    return is_chinese, score, confidence, signals

def process_year_file(zip_file, year, conn, stats):
    """Process a single year JSON file from the ZIP"""
    print(f"\n{'='*80}")
    print(f"Processing {year}.json")
    print(f"{'='*80}")

    # Read JSON from ZIP
    with zip_file.open(f"{year}.json") as f:
        # Read in chunks to handle large file
        content = f.read()
        data = json.loads(content)

    total_count = data.get('count', 0)
    patents = data.get('patentFileWrapperDataBag', [])

    print(f"Total patents in {year}: {total_count:,}")

    chinese_patents = []
    confidence_dist = Counter()
    signal_dist = Counter()

    processed = 0
    for patent in patents:
        processed += 1

        if processed % 10000 == 0:
            print(f"  Processed {processed:,} / {total_count:,} ({processed*100/total_count:.1f}%)")

        is_chinese, score, confidence, signals = detect_chinese_entity(patent)

        if is_chinese:
            app_metadata = patent.get('applicationMetaData', {})

            # Extract key fields
            app_number = patent.get('applicationNumberText', '')
            title = app_metadata.get('inventionTitle', '')
            filing_date = app_metadata.get('filingDate', '')
            grant_date = app_metadata.get('grantDate')
            patent_number = app_metadata.get('patentNumber')
            status = app_metadata.get('applicationStatusDescriptionText', '')

            # Assignee info
            assignee_name = ''
            assignee_country = ''
            assignee_city = ''

            assignment_bag = patent.get('assignmentBag', [])
            if assignment_bag:
                assignee_bag = assignment_bag[0].get('assigneeBag', [])
                if assignee_bag:
                    assignee_name = assignee_bag[0].get('assigneeNameText', '')
                    addr = assignee_bag[0].get('assigneeAddress', {})
                    assignee_country = addr.get('countryCode', '')
                    assignee_city = addr.get('cityName', '')

            chinese_patents.append({
                'application_number': app_number,
                'patent_number': patent_number,
                'filing_date': filing_date,
                'grant_date': grant_date,
                'title': title,
                'status': status,
                'assignee_name': assignee_name,
                'assignee_country': assignee_country,
                'assignee_city': assignee_city,
                'confidence': confidence,
                'confidence_score': score,
                'detection_signals': ','.join(signals),
                'year': year
            })

            confidence_dist[confidence] += 1
            for signal in signals:
                signal_type = signal.split('_')[0]
                signal_dist[signal_type] += 1

    print(f"\n  Chinese patents found: {len(chinese_patents):,}")
    print(f"  Confidence distribution:")
    for conf in ['VERY_HIGH', 'HIGH', 'MEDIUM', 'LOW']:
        count = confidence_dist[conf]
        if count > 0:
            print(f"    {conf:12s}: {count:,}")

    print(f"  Signal distribution:")
    for signal, count in signal_dist.most_common(10):
        print(f"    {signal:12s}: {count:,}")

    # Update stats
    stats['total_patents'] += total_count
    stats['chinese_patents'] += len(chinese_patents)
    stats['by_year'][year] = len(chinese_patents)
    stats['by_confidence'][year] = dict(confidence_dist)

    return chinese_patents

def create_database_tables(conn):
    """Create USPTO patent tables"""
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS uspto_patents_chinese (
            application_number TEXT PRIMARY KEY,
            patent_number TEXT,
            filing_date TEXT,
            grant_date TEXT,
            title TEXT,
            status TEXT,
            assignee_name TEXT,
            assignee_country TEXT,
            assignee_city TEXT,
            confidence TEXT,
            confidence_score INTEGER,
            detection_signals TEXT,
            year INTEGER,
            processed_date TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS uspto_patents_metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER,
            total_patents INTEGER,
            chinese_patents INTEGER,
            processing_date TEXT,
            processing_status TEXT
        )
    """)

    conn.commit()

def save_to_database(chinese_patents, year, conn):
    """Save Chinese patents to database"""
    cur = conn.cursor()

    processed_date = datetime.now().isoformat()

    for patent in chinese_patents:
        cur.execute("""
            INSERT OR REPLACE INTO uspto_patents_chinese
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            patent['application_number'],
            patent['patent_number'],
            patent['filing_date'],
            patent['grant_date'],
            patent['title'],
            patent['status'],
            patent['assignee_name'],
            patent['assignee_country'],
            patent['assignee_city'],
            patent['confidence'],
            patent['confidence_score'],
            patent['detection_signals'],
            patent['year'],
            processed_date
        ))

    cur.execute("""
        INSERT INTO uspto_patents_metadata (year, total_patents, chinese_patents, processing_date, processing_status)
        VALUES (?, ?, ?, ?, ?)
    """, (year, len(chinese_patents), len(chinese_patents), processed_date, 'COMPLETE'))

    conn.commit()

def main():
    print("="*80)
    print("USPTO PATENT CHINESE ENTITY DETECTION (2011-2020)")
    print("="*80)

    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    create_database_tables(conn)

    # Open ZIP file
    with zipfile.ZipFile(ZIP_PATH, 'r') as zip_file:
        # Get list of year files
        year_files = [name for name in zip_file.namelist() if name.endswith('.json')]
        year_files.sort()

        print(f"\nFound {len(year_files)} year files:")
        for yf in year_files:
            print(f"  - {yf}")

        stats = {
            'total_patents': 0,
            'chinese_patents': 0,
            'by_year': {},
            'by_confidence': {}
        }

        # Process each year
        years = [2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020]

        for year in years:
            try:
                chinese_patents = process_year_file(zip_file, year, conn, stats)
                save_to_database(chinese_patents, year, conn)

                print(f"  ✓ Saved {len(chinese_patents):,} patents to database")

            except Exception as e:
                print(f"  ✗ Error processing {year}: {e}")
                continue

    # Final summary
    print("\n" + "="*80)
    print("FINAL SUMMARY")
    print("="*80)

    print(f"\nTotal patents processed: {stats['total_patents']:,}")
    print(f"Chinese patents identified: {stats['chinese_patents']:,}")
    print(f"Percentage: {stats['chinese_patents']*100/stats['total_patents']:.2f}%")

    print(f"\nChinese patents by year:")
    for year in sorted(stats['by_year'].keys()):
        count = stats['by_year'][year]
        print(f"  {year}: {count:,}")

    # Save stats
    stats_file = "C:/Projects/OSINT - Foresight/analysis/uspto_patent_chinese_stats.json"
    with open(stats_file, 'w') as f:
        json.dump(stats, f, indent=2)
    print(f"\nStats saved to: {stats_file}")

    conn.close()
    print("\nProcessing complete!")

if __name__ == '__main__':
    main()

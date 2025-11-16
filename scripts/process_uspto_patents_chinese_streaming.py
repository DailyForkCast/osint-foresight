#!/usr/bin/env python3
"""
Process USPTO Patent Filewrapper JSON (2011-2020) with STREAMING
Multi-signal Chinese entity detection with confidence scoring
Uses streaming to handle 19-27GB JSON files without MemoryError
"""

import json
import zipfile
import sqlite3
import ijson  # For streaming JSON parsing
from datetime import datetime
from collections import Counter
import sys

# File paths
ZIP_PATH = "F:/USPTO Data/2011-2020-patent-filewrapper-full-json-20251005.zip"
DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"

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

CHINESE_PROVINCES = {
    'ANHUI', 'FUJIAN', 'GANSU', 'GUANGDONG', 'GUIZHOU', 'HAINAN', 'HEBEI',
    'HEILONGJIANG', 'HENAN', 'HUBEI', 'HUNAN', 'JIANGSU', 'JIANGXI', 'JILIN',
    'LIAONING', 'QINGHAI', 'SHAANXI', 'SHANDONG', 'SHANXI', 'SICHUAN',
    'YUNNAN', 'ZHEJIANG',
    'GUANGXI', 'INNER MONGOLIA', 'NINGXIA', 'TIBET', 'XINJIANG'
}

CHINESE_DISTRICTS = {
    'HAIDIAN', 'PUDONG', 'NANSHAN', 'ZHONGGUANCUN', 'LUOHU', 'FUTIAN',
    'SONGJIANG', 'MINHANG', 'BAOSHAN', 'CHAOYANG', 'FENGTAI'
}

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

    special_cases = {
        'NIO': ['NIO INC', 'NIO USA', 'NEXTEV'],
        'BOE': ['BOE TECHOLOG', 'BEIJING BOE'],
        'TCL': ['TCL CORP', 'TCL COMM'],
        'BYD': ['BYD COMPANY', 'BYD AUTO', 'BYD BATTERY'],
        'DJI': ['DJI INNOV', 'DJI TECHNO'],
    }

    for company, patterns in special_cases.items():
        for pattern in patterns:
            # Apply word boundary check to prevent false positives
            import re
            word_pattern = r'\b' + re.escape(pattern) + r'\b'
            if re.search(word_pattern, name_upper):
                return company

    for company in PRC_COMPANIES:
        if len(company) > 4:
            # Apply word boundary check to prevent false positives
            word_pattern = r'\b' + re.escape(company) + r'\b'
            if re.search(word_pattern, name_upper):
                return company

    return None

def detect_chinese_entity(data):
    """
    Multi-signal Chinese entity detection with confidence scoring

    Returns: (is_chinese, score, confidence, signals, data_quality_flag, fields_with_data)
    """
    score = 0
    signals = []
    negative_signals = []  # Evidence it's NOT Chinese
    fields_with_data = []  # Track which fields have actual data

    country_code = None
    city = None
    assignee_name = None
    assignee_address = None
    postal_code = None

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

                # Track which fields have actual data
                if country_code:
                    fields_with_data.append('country')
                if city:
                    fields_with_data.append('city')
                if assignee_name:
                    fields_with_data.append('assignee_name')
                if assignee_address:
                    fields_with_data.append('address')
                if postal_code:
                    fields_with_data.append('postal_code')

                # TIER 1: Country code (100 points)
                if country_code in ('CN', 'CHN', 'HK', 'MO'):
                    score += 100
                    signals.append(f'country_{country_code}')
                elif country_code == 'JPX':
                    if city and city.upper() in CHINESE_CITIES:
                        score += 100
                        signals.append(f'country_JPX_verified')
                elif country_code in ('US', 'USA', 'JP', 'JPN', 'JAPAN', 'DE', 'DEU', 'GERMANY',
                                     'KR', 'KOR', 'KOREA', 'GB', 'UK', 'FR', 'FRANCE', 'CA', 'CANADA',
                                     'IT', 'ITALY', 'ES', 'SPAIN', 'NL', 'NETHERLANDS', 'SE', 'SWEDEN',
                                     'CH', 'SWITZERLAND', 'AU', 'AUSTRALIA', 'IN', 'INDIA', 'BR', 'BRAZIL'):
                    # Definitive non-Chinese country code
                    negative_signals.append(f'country_{country_code}')

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
                    # Apply word boundary to prevent false positives
                    import re
                    word_pattern = r'\b' + re.escape(province) + r'\b'
                    if re.search(word_pattern, full_address):
                        score += 40
                        signals.append(f'province_{province}')
                        break

                # TIER 4: Chinese district (25 points)
                for district in CHINESE_DISTRICTS:
                    # Apply word boundary to prevent false positives
                    word_pattern = r'\b' + re.escape(district) + r'\b'
                    if re.search(word_pattern, full_address):
                        score += 25
                        signals.append(f'district_{district}')
                        break

                # TIER 4: Chinese street pattern (15 points)
                for pattern in CHINESE_STREET_PATTERNS:
                    # Apply word boundary to prevent false positives
                    word_pattern = r'\b' + re.escape(pattern) + r'\b'
                    if re.search(word_pattern, full_address):
                        score += 15
                        signals.append(f'street_pattern')
                        break

    # Check inventorBag
    app_metadata = data.get('applicationMetaData', {})
    inventor_bag = app_metadata.get('inventorBag', [])
    inventor_cn_count = 0
    for inventor in inventor_bag:
        inv_country = inventor.get('countryCode')
        if inv_country in ('CN', 'CHN', 'HK', 'MO'):
            inventor_cn_count += 1

    if inventor_cn_count > 0:
        score += min(inventor_cn_count * 20, 60)
        signals.append(f'inventors_{inventor_cn_count}')

    # Determine final classification
    is_chinese = score >= 50

    if score >= 100:
        confidence = 'VERY_HIGH'
    elif score >= 70:
        confidence = 'HIGH'
    elif score >= 50:
        confidence = 'MEDIUM'
    else:
        confidence = 'LOW'

    # Determine data quality flag (NULL data handling)
    fields_count = len(set(fields_with_data))  # Unique fields

    if score >= 100 and 'country' in fields_with_data:
        # Has Chinese country code
        data_quality_flag = 'CHINESE_CONFIRMED'
    elif negative_signals:
        # Has non-Chinese country code
        data_quality_flag = 'NON_CHINESE_CONFIRMED'
    elif fields_count == 0:
        # No data at all
        data_quality_flag = 'NO_DATA'
    elif fields_count <= 2:
        # Minimal data
        data_quality_flag = 'LOW_DATA'
    else:
        # Has data but no clear signals
        data_quality_flag = 'UNCERTAIN_NEEDS_REVIEW'

    return is_chinese, score, confidence, signals, data_quality_flag, fields_count

def process_year_streaming(zip_file, year, conn, stats):
    """Process a single year JSON file using streaming parser"""
    print(f"\n{'='*80}")
    print(f"Processing {year}.json (STREAMING MODE)")
    print(f"{'='*80}")

    chinese_patents = []
    confidence_dist = Counter()
    signal_dist = Counter()
    processed = 0

    # Stream the JSON file
    with zip_file.open(f"{year}.json") as f:
        # Use ijson to stream parse the patentFileWrapperDataBag array
        parser = ijson.items(f, 'patentFileWrapperDataBag.item')

        for patent in parser:
            processed += 1

            if processed % 10000 == 0:
                print(f"  Processed {processed:,} patents | Chinese found: {len(chinese_patents):,}")

            is_chinese, score, confidence, signals, data_quality_flag, fields_count = detect_chinese_entity(patent)

            if is_chinese:
                app_metadata = patent.get('applicationMetaData', {})

                app_number = patent.get('applicationNumberText', '')
                title = app_metadata.get('inventionTitle', '')
                filing_date = app_metadata.get('filingDate', '')
                grant_date = app_metadata.get('grantDate')
                patent_number = app_metadata.get('patentNumber')
                status = app_metadata.get('applicationStatusDescriptionText', '')

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
                    'data_quality_flag': data_quality_flag,
                    'fields_with_data_count': fields_count,
                    'year': year
                })

                confidence_dist[confidence] += 1
                for signal in signals:
                    signal_type = signal.split('_')[0]
                    signal_dist[signal_type] += 1

    print(f"\n  Total processed: {processed:,}")
    print(f"  Chinese patents found: {len(chinese_patents):,}")
    print(f"  Confidence distribution:")
    for conf in ['VERY_HIGH', 'HIGH', 'MEDIUM']:
        count = confidence_dist[conf]
        if count > 0:
            print(f"    {conf:12s}: {count:,}")

    print(f"  Top signals:")
    for signal, count in signal_dist.most_common(10):
        print(f"    {signal:12s}: {count:,}")

    stats['total_patents'] += processed
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
            data_quality_flag TEXT,
            fields_with_data_count INTEGER,
            year INTEGER,
            processed_date TEXT
        )
    """)

    # Create index on data quality flag
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_uspto_data_quality
        ON uspto_patents_chinese(data_quality_flag)
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
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            patent['data_quality_flag'],
            patent['fields_with_data_count'],
            patent['year'],
            processed_date
        ))

    total_in_year = len(chinese_patents)
    cur.execute("""
        INSERT INTO uspto_patents_metadata (year, total_patents, chinese_patents, processing_date, processing_status)
        VALUES (?, ?, ?, ?, ?)
    """, (year, total_in_year, total_in_year, processed_date, 'COMPLETE'))

    conn.commit()

def main():
    print("="*80)
    print("USPTO PATENT CHINESE ENTITY DETECTION (2011-2020) - STREAMING")
    print("="*80)

    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    create_database_tables(conn)

    # Open ZIP file
    with zipfile.ZipFile(ZIP_PATH, 'r') as zip_file:
        year_files = [name for name in zip_file.namelist() if name.endswith('.json')]
        year_files.sort()

        print(f"\nFound {len(year_files)} year files")

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
                chinese_patents = process_year_streaming(zip_file, year, conn, stats)
                save_to_database(chinese_patents, year, conn)

                print(f"  SAVED {len(chinese_patents):,} patents to database")

            except Exception as e:
                print(f"  ERROR processing {year}: {e}")
                import traceback
                traceback.print_exc()
                continue

    # Final summary
    print("\n" + "="*80)
    print("FINAL SUMMARY")
    print("="*80)

    print(f"\nTotal patents processed: {stats['total_patents']:,}")
    print(f"Chinese patents identified: {stats['chinese_patents']:,}")
    if stats['total_patents'] > 0:
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

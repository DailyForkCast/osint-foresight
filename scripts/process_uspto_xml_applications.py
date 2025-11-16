#!/usr/bin/env python3
"""
Process USPTO XML Patent Applications for Chinese Entity Detection
Handles ipa251002.xml and ipab20251002.xml files
"""

from lxml import etree as ET
import sqlite3
import json
from datetime import datetime
import os
import sys

# Database path
DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"

# Chinese Detection Logic (same as streaming processor)
CHINESE_COUNTRY_CODES = ['CN', 'CHN', 'CHINA', 'PRC', 'HK', 'HKG', 'HONG KONG', 'MO', 'MAC', 'MACAU']

CHINESE_CITIES = {
    'BEIJING', 'SHANGHAI', 'SHENZHEN', 'GUANGZHOU', 'HANGZHOU', 'CHENGDU',
    'NANJING', 'WUHAN', 'XIAN', 'TIANJIN', 'CHONGQING', 'SUZHOU', 'DONGGUAN',
    'QINGDAO', 'SHENYANG', 'DALIAN', 'NINGBO', 'XIAMEN', 'HEFEI', 'FUZHOU',
    'HARBIN', 'CHANGSHA', 'ZHENGZHOU', 'KUNMING', 'JINAN', 'FOSHAN', 'CHANGCHUN',
    'WENZHOU', 'SHIJIAZHUANG', 'NANCHANG', 'GUIYANG', 'TAIYUAN', 'URUMQI',
    'NANNING', 'LANZHOU', 'ZHUHAI', 'HUIZHOU', 'JIANGMEN', 'SHAOXING', 'YANTAI',
    'ZIBO', 'WEIFANG', 'TANGSHAN'
}

CHINESE_PROVINCES = {
    'GUANGDONG', 'ZHEJIANG', 'JIANGSU', 'SHANDONG', 'BEIJING', 'SHANGHAI',
    'SICHUAN', 'HUBEI', 'FUJIAN', 'ANHUI', 'SHAANXI', 'LIAONING', 'HENAN',
    'HUNAN', 'HEILONGJIANG', 'HEBEI', 'YUNNAN', 'JIANGXI', 'SHANXI', 'GUIZHOU',
    'GANSU', 'INNER MONGOLIA', 'XINJIANG', 'JILIN', 'GUANGXI', 'TIANJIN',
    'CHONGQING'
}

CHINESE_DISTRICTS = {
    'HAIDIAN', 'CHAOYANG', 'XUHUI', 'PUDONG', 'NANSHAN', 'FUTIAN', 'LUOHU',
    'TIANHE', 'YUEXIU', 'XIHU', 'BINJIANG'
}

KNOWN_CHINESE_COMPANIES = {
    'HUAWEI', 'TENCENT', 'ALIBABA', 'XIAOMI', 'BYTEDANCE', 'ZTE', 'LENOVO',
    'BOE TECHNOLOGY', 'BEIJING BOE', 'OPPO', 'VIVO', 'DJI', 'BAIDU', 'SINIC',
    'PING AN', 'CHINA MOBILE', 'CHINA TELECOM', 'CHINA UNICOM', 'SINOPEC',
    'CNPC', 'STATE GRID', 'SAIC MOTOR', 'CHINA RAILWAY', 'BYD', 'GEELY',
    'GREAT WALL MOTOR', 'NIO INC', 'XPENG', 'SMIC', 'YMTC', 'HIKVISION',
    'DAHUA', 'MEGVII', 'SENSETIME', 'CAMBRICON', 'HORIZON ROBOTICS'
}

def detect_chinese_entity(assignee_data):
    """Detect if assignee is Chinese entity with scoring"""
    score = 0
    signals = []

    name = assignee_data.get('name', '').upper()
    country = assignee_data.get('country', '').upper()
    city = assignee_data.get('city', '').upper()
    state = assignee_data.get('state', '').upper()
    address = assignee_data.get('address', '').upper()
    postal = assignee_data.get('postal', '')

    # TIER 1: Country codes (100 points - definitive)
    if any(code in country for code in CHINESE_COUNTRY_CODES):
        score += 100
        signals.append(f'country_{country[:10]}')

    # TIER 2: Known Chinese companies (80 points)
    for company in KNOWN_CHINESE_COMPANIES:
        if company in name:
            score += 80
            signals.append(f'company_{company[:20]}')
            break

    # TIER 2: Postal code (60 points)
    if postal and len(postal) == 6 and postal.isdigit():
        if postal[0] in '123456789':
            score += 60
            signals.append('postal')

    # TIER 2: Cities (50 points)
    if city and city in CHINESE_CITIES:
        score += 50
        signals.append(f'city_{city[:15]}')

    # TIER 3: Provinces (40 points)
    if state in CHINESE_PROVINCES or any(prov in address for prov in CHINESE_PROVINCES):
        score += 40
        signals.append('province')

    # TIER 3: Districts (25 points)
    if any(dist in address or dist in city for dist in CHINESE_DISTRICTS):
        score += 25
        signals.append('district')

    # TIER 4: Street patterns (15 points)
    chinese_street_keywords = ['LU', 'DADAO', 'JIE', 'ROAD', 'AVENUE']
    if any(kw in address for kw in chinese_street_keywords):
        if any(city_name in address for city_name in CHINESE_CITIES):
            score += 15
            signals.append('street')

    # Determine confidence
    if score >= 100:
        confidence = 'VERY_HIGH'
    elif score >= 70:
        confidence = 'HIGH'
    elif score >= 50:
        confidence = 'MEDIUM'
    else:
        confidence = 'LOW'

    is_chinese = score >= 50

    return is_chinese, score, confidence, signals

def parse_xml_assignees(xml_file):
    """Parse USPTO XML file for patent assignees using streaming"""
    print(f"\n{'='*80}")
    print(f"Processing {os.path.basename(xml_file)}")
    print(f"{'='*80}")

    chinese_patents = []
    total_patents = 0
    chinese_count = 0

    # Use iterparse for memory efficiency
    context = ET.iterparse(xml_file, events=('start', 'end'))
    context = iter(context)

    current_patent = {}
    current_assignee = {}
    in_assignees = False
    in_assignee = False

    for event, elem in context:
        if event == 'start':
            if elem.tag == 'us-bibliographic-data-application':
                current_patent = {}
                current_assignee = {}
            elif elem.tag == 'assignees':
                in_assignees = True
            elif elem.tag == 'assignee' and in_assignees:
                in_assignee = True
                current_assignee = {}

        elif event == 'end':
            # Extract publication number
            if elem.tag == 'doc-number' and elem.getparent() is not None:
                parent = elem.getparent()
                if parent.tag == 'document-id':
                    grandparent = parent.getparent()
                    if grandparent is not None and grandparent.tag == 'publication-reference':
                        current_patent['publication_number'] = elem.text

            # Extract application number
            if elem.tag == 'doc-number' and elem.getparent() is not None:
                parent = elem.getparent()
                if parent.tag == 'document-id':
                    grandparent = parent.getparent()
                    if grandparent is not None and grandparent.tag == 'application-reference':
                        current_patent['application_number'] = elem.text

            # Extract filing date
            if elem.tag == 'date' and elem.getparent() is not None:
                parent = elem.getparent()
                if parent.tag == 'document-id':
                    grandparent = parent.getparent()
                    if grandparent is not None and grandparent.tag == 'application-reference':
                        current_patent['filing_date'] = elem.text

            # Extract publication date
            if elem.tag == 'date' and elem.getparent() is not None:
                parent = elem.getparent()
                if parent.tag == 'document-id':
                    grandparent = parent.getparent()
                    if grandparent is not None and grandparent.tag == 'publication-reference':
                        current_patent['publication_date'] = elem.text

            # Extract title
            if elem.tag == 'invention-title':
                current_patent['title'] = elem.text

            # Extract assignee info
            if in_assignee:
                if elem.tag == 'orgname':
                    current_assignee['name'] = elem.text
                elif elem.tag == 'country':
                    current_assignee['country'] = elem.text
                elif elem.tag == 'city':
                    current_assignee['city'] = elem.text
                elif elem.tag == 'state':
                    current_assignee['state'] = elem.text
                elif elem.tag == 'address-1':
                    current_assignee['address'] = elem.text
                elif elem.tag == 'postcode':
                    current_assignee['postal'] = elem.text

            # End of assignee
            if elem.tag == 'assignee' and in_assignee:
                in_assignee = False
                # Detect Chinese entity
                is_chinese, score, confidence, signals = detect_chinese_entity(current_assignee)

                if is_chinese:
                    patent_data = {
                        'application_number': current_patent.get('application_number'),
                        'publication_number': current_patent.get('publication_number'),
                        'filing_date': current_patent.get('filing_date'),
                        'publication_date': current_patent.get('publication_date'),
                        'title': current_patent.get('title', '')[:500],
                        'assignee_name': current_assignee.get('name', ''),
                        'assignee_country': current_assignee.get('country', ''),
                        'assignee_city': current_assignee.get('city', ''),
                        'assignee_state': current_assignee.get('state', ''),
                        'confidence': confidence,
                        'confidence_score': score,
                        'detection_signals': ','.join(signals)
                    }
                    chinese_patents.append(patent_data)
                    chinese_count += 1

            # End of assignees section
            if elem.tag == 'assignees':
                in_assignees = False

            # End of patent record
            if elem.tag == 'us-bibliographic-data-application':
                total_patents += 1

                if total_patents % 5000 == 0:
                    print(f"  Processed {total_patents:,} patents | Chinese found: {chinese_count:,}")

                # Clear element to free memory
                elem.clear()
                while elem.getprevious() is not None:
                    del elem.getparent()[0]

    print(f"\n  Total processed: {total_patents:,}")
    print(f"  Chinese patents found: {chinese_count:,}")

    return chinese_patents

def save_to_database(patents, source_file):
    """Save detected Chinese patents to database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Insert patents
    inserted = 0
    for patent in patents:
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO uspto_patents_chinese
                (application_number, publication_number, filing_date, publication_date,
                 title, assignee_name, assignee_country, assignee_city,
                 confidence, confidence_score, detection_signals, source_file, processed_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                patent['application_number'],
                patent['publication_number'],
                patent['filing_date'],
                patent['publication_date'],
                patent['title'],
                patent['assignee_name'],
                patent['assignee_country'],
                patent['assignee_city'],
                patent['confidence'],
                patent['confidence_score'],
                patent['detection_signals'],
                source_file,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ))
            inserted += 1
        except Exception as e:
            print(f"  Error inserting patent: {e}")

    conn.commit()
    conn.close()

    print(f"  SAVED {inserted:,} patents to database")

def main():
    xml_files = [
        "F:/USPTO Data/ipa251002.xml",
        "F:/USPTO Data/ipab20251002.xml"
    ]

    print("="*80)
    print("USPTO XML PATENT APPLICATION CHINESE ENTITY DETECTION")
    print("="*80)

    all_patents = []

    for xml_file in xml_files:
        if os.path.exists(xml_file):
            patents = parse_xml_assignees(xml_file)
            all_patents.extend(patents)
            save_to_database(patents, os.path.basename(xml_file))
        else:
            print(f"\nFile not found: {xml_file}")

    # Generate summary statistics
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print(f"Total Chinese patents found: {len(all_patents):,}")

    confidence_dist = {}
    for patent in all_patents:
        conf = patent['confidence']
        confidence_dist[conf] = confidence_dist.get(conf, 0) + 1

    print("\nConfidence distribution:")
    for conf, count in sorted(confidence_dist.items()):
        print(f"  {conf:12s}: {count:,}")

    print("\nProcessing complete!")

if __name__ == '__main__':
    main()

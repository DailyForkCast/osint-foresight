#!/usr/bin/env python3
"""
TED Fixed Data Extractor for OSINT Analysis
A practical, working extractor that properly handles TED data
Focused on finding real Chinese involvement without false positives
"""

import tarfile
import xml.etree.ElementTree as ET
import sqlite3
import json
import logging
from datetime import datetime
from pathlib import Path
import re
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TEDFixedExtractor:
    """Fixed TED data extractor with proper Chinese detection"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()
        self.stats = {
            'files_processed': 0,
            'contractors_found': 0,
            'chinese_confirmed': 0,
            'performance_in_china': 0,
            'chinese_products': 0
        }

        # Fixed Chinese detection patterns with word boundaries
        self.chinese_companies = [
            r'\bHuawei\b', r'\bZTE\b', r'\bAlibaba\b', r'\bTencent\b',
            r'\bXiaomi\b', r'\bLenovo\b', r'\bBYD\b', r'\bDJI\b',
            r'\bHikvision\b', r'\bDahua\b', r'\bCOSCO\b', r'\bSinopec\b',
            r'\bCRRC\b', r'\bSMIC\b', r'\bChina Mobile\b', r'\bChina Telecom\b'
        ]

        self.chinese_cities = [
            r'\bBeijing\b', r'\bShanghai\b', r'\bShenzhen\b', r'\bGuangzhou\b',
            r'\bHangzhou\b', r'\bTianjin\b', r'\bWuhan\b', r'\bChengdu\b'
        ]

    def init_database(self):
        """Create simple, practical database schema"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute('DROP TABLE IF EXISTS ted_osint_analysis')

        cur.execute('''
            CREATE TABLE ted_osint_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                -- Document identification
                doc_id TEXT,
                publication_date TEXT,
                form_type TEXT,

                -- Contract info
                contract_title TEXT,
                cpv_code TEXT,
                sector TEXT,

                -- Location data
                contracting_country TEXT,
                performance_location TEXT,

                -- Contractor data
                contractor_name TEXT,
                contractor_country TEXT,

                -- Chinese involvement
                has_chinese_involvement BOOLEAN DEFAULT 0,
                chinese_type TEXT,
                chinese_evidence TEXT,
                confidence_score REAL,

                -- Critical sector flag
                is_critical_sector BOOLEAN DEFAULT 0,

                -- Processing metadata
                xml_file TEXT,
                processed_date TEXT
            )
        ''')

        conn.commit()
        conn.close()

    def extract_from_xml(self, xml_content: bytes, file_path: str) -> dict:
        """Extract key data from XML with fixed patterns"""
        try:
            xml_str = xml_content.decode('utf-8', errors='ignore')

            data = {
                'doc_id': self.extract_pattern(xml_str, r'DOC_ID="([^"]+)"'),
                'publication_date': self.extract_pattern(xml_str, r'<DATE_PUB>(\d{8})</DATE_PUB>'),
                'form_type': self.extract_pattern(xml_str, r'<(F\d{2}_\d{4})'),
                'contract_title': self.extract_pattern(xml_str, r'<TITLE[^>]*>([^<]+)</TITLE>'),
                'cpv_code': self.extract_pattern(xml_str, r'CPV_CODE[^>]*CODE="(\d+)"'),
                'contracting_country': self.extract_pattern(xml_str, r'<CONTRACTING_BODY.*?<COUNTRY[^>]*VALUE="([^"]+)"', re.DOTALL),
                'contractor_name': self.extract_pattern(xml_str, r'<CONTRACTOR.*?<OFFICIALNAME>([^<]+)</OFFICIALNAME>', re.DOTALL),
                'contractor_country': self.extract_pattern(xml_str, r'<CONTRACTOR.*?<COUNTRY[^>]*VALUE="([^"]+)"', re.DOTALL),
                'performance_location': self.extract_pattern(xml_str, r'PERFORMANCE_NUTS[^>]*CODE="([^"]+)"'),
                'xml_file': file_path,
                'processed_date': datetime.now().isoformat()
            }

            # Determine sector from CPV code
            if data['cpv_code']:
                data['sector'] = self.get_sector(data['cpv_code'])
                data['is_critical_sector'] = self.is_critical(data['cpv_code'])

            # Check for Chinese involvement
            chinese_result = self.check_chinese_involvement(xml_str, data)
            data.update(chinese_result)

            # Update stats
            if data['contractor_name']:
                self.stats['contractors_found'] += 1
            if data['has_chinese_involvement']:
                self.stats['chinese_confirmed'] += 1
                if 'Performance' in data['chinese_type']:
                    self.stats['performance_in_china'] += 1
                if 'Product' in data['chinese_type']:
                    self.stats['chinese_products'] += 1

            return data

        except Exception as e:
            logger.warning(f"Error extracting from {file_path}: {e}")
            return None

    def extract_pattern(self, text: str, pattern: str, flags=0) -> str:
        """Extract first match of pattern from text"""
        match = re.search(pattern, text, flags)
        return match.group(1) if match else None

    def check_chinese_involvement(self, xml_str: str, data: dict) -> dict:
        """Check for Chinese involvement with proper word boundaries"""
        result = {
            'has_chinese_involvement': False,
            'chinese_type': None,
            'chinese_evidence': None,
            'confidence_score': 0.0
        }

        # 1. Check contractor country (highest confidence)
        if data['contractor_country'] in ['CN', 'CHN', 'HK', 'MO']:
            result['has_chinese_involvement'] = True
            result['chinese_type'] = 'Chinese contractor'
            result['chinese_evidence'] = f"Contractor country: {data['contractor_country']}"
            result['confidence_score'] = 1.0
            return result

        # 2. Check performance location
        if data['performance_location'] == 'CN':
            result['has_chinese_involvement'] = True
            result['chinese_type'] = 'Performance in China'
            result['chinese_evidence'] = 'Work performed in China'
            result['confidence_score'] = 1.0
            return result

        # 3. Check for Chinese companies (with word boundaries)
        for pattern in self.chinese_companies:
            if re.search(pattern, xml_str, re.IGNORECASE):
                result['has_chinese_involvement'] = True
                result['chinese_type'] = 'Chinese product/technology'
                company_name = pattern.replace(r'\\b', '')
                result['chinese_evidence'] = f"Chinese company mentioned: {company_name}"
                result['confidence_score'] = 0.8
                return result

        # 4. Check for Chinese cities (with word boundaries)
        for pattern in self.chinese_cities:
            if re.search(pattern, xml_str, re.IGNORECASE):
                result['has_chinese_involvement'] = True
                result['chinese_type'] = 'Chinese location reference'
                city_name = pattern.replace(r'\\b', '')
                result['chinese_evidence'] = f"Chinese city mentioned: {city_name}"
                result['confidence_score'] = 0.6
                return result

        return result

    def get_sector(self, cpv_code: str) -> str:
        """Get sector name from CPV code"""
        if not cpv_code or len(cpv_code) < 2:
            return 'Unknown'

        sectors = {
            '30': 'IT Hardware',
            '31': 'Electrical Machinery',
            '32': 'Telecommunications',
            '33': 'Medical Equipment',
            '34': 'Transport Equipment',
            '35': 'Defense/Security',
            '45': 'Construction',
            '48': 'Software',
            '50': 'Maintenance',
            '64': 'Postal/Telecom Services',
            '71': 'Engineering',
            '72': 'IT Services',
            '73': 'R&D',
            '79': 'Business Services'
        }

        prefix = cpv_code[:2]
        return sectors.get(prefix, f'Sector {prefix}')

    def is_critical(self, cpv_code: str) -> bool:
        """Check if CPV code represents critical sector"""
        if not cpv_code or len(cpv_code) < 2:
            return False

        critical_prefixes = ['30', '31', '32', '33', '34', '35', '48', '64', '72', '73']
        return cpv_code[:2] in critical_prefixes

    def save_to_database(self, data: dict):
        """Save extracted data to database"""
        if not data:
            return

        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        try:
            cur.execute('''
                INSERT INTO ted_osint_analysis (
                    doc_id, publication_date, form_type,
                    contract_title, cpv_code, sector,
                    contracting_country, performance_location,
                    contractor_name, contractor_country,
                    has_chinese_involvement, chinese_type,
                    chinese_evidence, confidence_score,
                    is_critical_sector, xml_file, processed_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('doc_id'), data.get('publication_date'), data.get('form_type'),
                data.get('contract_title'), data.get('cpv_code'), data.get('sector'),
                data.get('contracting_country'), data.get('performance_location'),
                data.get('contractor_name'), data.get('contractor_country'),
                data.get('has_chinese_involvement'), data.get('chinese_type'),
                data.get('chinese_evidence'), data.get('confidence_score'),
                data.get('is_critical_sector'), data.get('xml_file'), data.get('processed_date')
            ))
            conn.commit()
        except Exception as e:
            logger.error(f"Database error: {e}")
        finally:
            conn.close()

    def process_tar_file(self, tar_path: str):
        """Process a TED tar file"""
        logger.info(f"Processing {tar_path}")

        try:
            with tarfile.open(tar_path, 'r:gz') as monthly_tar:
                daily_files = [f for f in monthly_tar.getnames() if f.endswith('.tar.gz')]

                for daily_file in daily_files[:5]:  # Process 5 days for testing
                    logger.info(f"  Processing {daily_file}")

                    daily_obj = monthly_tar.extractfile(daily_file)
                    with tarfile.open(fileobj=daily_obj, mode='r:gz') as daily_tar:
                        xml_files = [f for f in daily_tar.getnames() if f.endswith('.xml')]

                        for xml_file in xml_files[:100]:  # Process 100 files per day
                            try:
                                xml_obj = daily_tar.extractfile(xml_file)
                                content = xml_obj.read()

                                data = self.extract_from_xml(content, xml_file)
                                if data:
                                    self.save_to_database(data)
                                    self.stats['files_processed'] += 1

                                    if self.stats['files_processed'] % 100 == 0:
                                        self.log_progress()

                            except Exception as e:
                                logger.warning(f"Error processing {xml_file}: {e}")

        except Exception as e:
            logger.error(f"Error processing tar: {e}")

    def log_progress(self):
        """Log processing progress"""
        logger.info(f"Progress: {self.stats['files_processed']} files, "
                   f"{self.stats['contractors_found']} contractors, "
                   f"{self.stats['chinese_confirmed']} Chinese confirmed")

    def generate_strategic_dependency_map(self):
        """Generate strategic dependency analysis for OSINT"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        print("\n" + "="*80)
        print("STRATEGIC DEPENDENCY MAPPING - EU-CHINA PROCUREMENT")
        print("="*80)

        # Overall statistics
        cur.execute("SELECT COUNT(*) FROM ted_osint_analysis")
        total = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM ted_osint_analysis WHERE has_chinese_involvement = 1")
        chinese = cur.fetchone()[0]

        print(f"\nTotal contracts analyzed: {total:,}")
        print(f"Chinese involvement detected: {chinese:,}")
        print(f"Penetration rate: {chinese/max(1,total)*100:.2f}%")

        # Critical sector analysis
        print("\n" + "="*50)
        print("CRITICAL SECTOR DEPENDENCIES")
        print("="*50)

        cur.execute('''
            SELECT sector,
                   COUNT(*) as total,
                   SUM(CASE WHEN has_chinese_involvement = 1 THEN 1 ELSE 0 END) as chinese
            FROM ted_osint_analysis
            WHERE is_critical_sector = 1
            GROUP BY sector
            ORDER BY chinese DESC
        ''')

        critical_sectors = []
        for sector, total, chinese_count in cur.fetchall():
            if chinese_count > 0:
                risk_level = 'HIGH' if chinese_count/total > 0.1 else 'MEDIUM' if chinese_count/total > 0.05 else 'LOW'
                critical_sectors.append({
                    'sector': sector,
                    'total': total,
                    'chinese': chinese_count,
                    'rate': chinese_count/total*100,
                    'risk': risk_level
                })
                print(f"\n{sector}:")
                print(f"  Total contracts: {total}")
                print(f"  Chinese involvement: {chinese_count} ({chinese_count/total*100:.1f}%)")
                print(f"  Risk level: {risk_level}")

        # Chinese involvement types
        print("\n" + "="*50)
        print("TYPES OF CHINESE INVOLVEMENT")
        print("="*50)

        cur.execute('''
            SELECT chinese_type, COUNT(*) as count
            FROM ted_osint_analysis
            WHERE has_chinese_involvement = 1
            GROUP BY chinese_type
            ORDER BY count DESC
        ''')

        for inv_type, count in cur.fetchall():
            print(f"  {inv_type}: {count}")

        # Geographic distribution
        print("\n" + "="*50)
        print("EU COUNTRIES WITH CHINESE EXPOSURE")
        print("="*50)

        cur.execute('''
            SELECT contracting_country, COUNT(*) as chinese_contracts
            FROM ted_osint_analysis
            WHERE has_chinese_involvement = 1
            AND contracting_country IS NOT NULL
            GROUP BY contracting_country
            ORDER BY chinese_contracts DESC
            LIMIT 10
        ''')

        for country, count in cur.fetchall():
            print(f"  {country}: {count} contracts")

        # Sample high-confidence Chinese involvement
        print("\n" + "="*50)
        print("HIGH-CONFIDENCE CHINESE ENTITIES")
        print("="*50)

        cur.execute('''
            SELECT contractor_name, contractor_country, chinese_evidence
            FROM ted_osint_analysis
            WHERE confidence_score >= 0.8
            AND contractor_name IS NOT NULL
            LIMIT 10
        ''')

        for name, country, evidence in cur.fetchall():
            print(f"  {name[:60]} ({country})")
            print(f"    Evidence: {evidence}")

        conn.close()

        # Generate JSON report for further analysis
        report = {
            'generated': datetime.now().isoformat(),
            'total_analyzed': total,
            'chinese_involvement': chinese,
            'penetration_rate': chinese/max(1,total)*100,
            'critical_sectors': critical_sectors,
            'stats': self.stats
        }

        with open('C:/Projects/OSINT - Foresight/analysis/strategic_dependencies.json', 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n\nStrategic dependency report saved to: strategic_dependencies.json")

        return report


def main():
    """Main execution for OSINT analysis"""
    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"

    extractor = TEDFixedExtractor(db_path)

    # Process some TED data
    years_months = [
        (2024, 1),  # January 2024
        (2023, 12), # December 2023
        (2023, 6),  # June 2023
    ]

    for year, month in years_months:
        tar_path = f"F:/TED_Data/monthly/{year}/TED_monthly_{year}_{month:02d}.tar.gz"
        if os.path.exists(tar_path):
            extractor.process_tar_file(tar_path)
        else:
            logger.warning(f"File not found: {tar_path}")

    # Generate strategic dependency analysis
    extractor.generate_strategic_dependency_map()

    return extractor.stats


if __name__ == "__main__":
    main()
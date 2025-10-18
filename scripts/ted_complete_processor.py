#!/usr/bin/env python3
"""
TED Complete Dataset Processor
Processes all available TED data to map EU-China relationships
"""

import tarfile
import xml.etree.ElementTree as ET
import sqlite3
import json
import logging
from datetime import datetime
from pathlib import Path
import hashlib
import re
import os
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TEDCompleteProcessor:
    """Process all TED data systematically"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()
        self.stats = {
            'start_time': time.time(),
            'years_processed': [],
            'months_processed': 0,
            'total_files': 0,
            'chinese_indicators': 0,
            'contractors_found': 0,
            'by_year': {},
            'chinese_companies': set(),
            'performance_locations': set(),
            'critical_sectors': 0
        }

    def init_database(self):
        """Enhanced database schema for complete analysis"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute('DROP TABLE IF EXISTS ted_complete_analysis')

        cur.execute('''
            CREATE TABLE ted_complete_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                -- Document info
                doc_id TEXT,
                form_type TEXT,
                publication_date TEXT,
                year INTEGER,
                month INTEGER,

                -- Contract details
                contract_title TEXT,
                contract_description TEXT,
                cpv_main TEXT,
                contract_value TEXT,

                -- Location info
                contracting_country TEXT,
                performance_location TEXT,
                performance_country_code TEXT,

                -- Contractor info
                contractors_json TEXT,
                num_contractors INTEGER DEFAULT 0,

                -- Chinese analysis
                has_chinese_involvement BOOLEAN DEFAULT 0,
                chinese_involvement_type TEXT,
                chinese_entities_found TEXT,
                chinese_confidence REAL DEFAULT 0,

                -- Sector analysis
                is_critical_sector BOOLEAN DEFAULT 0,
                technology_type TEXT,

                -- Meta
                xml_file TEXT,
                processing_date TEXT
            )
        ''')

        # Create indexes
        cur.execute('CREATE INDEX IF NOT EXISTS idx_year ON ted_complete_analysis(year)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_chinese ON ted_complete_analysis(has_chinese_involvement)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_perf_country ON ted_complete_analysis(performance_country_code)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_cpv ON ted_complete_analysis(cpv_main)')

        conn.commit()
        conn.close()

    def extract_comprehensive_data(self, xml_content, file_path):
        """Extract all relevant data from XML"""
        try:
            xml_str = xml_content.decode('utf-8', errors='ignore')

            # Basic document info
            doc_id = self.extract_doc_id(xml_str)
            form_type = self.extract_form_type(xml_str)
            pub_date = self.extract_publication_date(xml_str)

            # Contract details
            title = self.extract_contract_title(xml_str)
            description = self.extract_contract_description(xml_str)
            cpv_code = self.extract_cpv_code(xml_str)
            value = self.extract_contract_value(xml_str)

            # Location information
            contracting_country = self.extract_contracting_country(xml_str)
            performance_location, performance_code = self.extract_performance_location(xml_str)

            # Contractor information
            contractors = self.extract_contractors(xml_str)

            # Chinese involvement analysis
            chinese_analysis = self.analyze_chinese_involvement(
                xml_str, contractors, performance_code, title, description
            )

            # Sector analysis
            sector_analysis = self.analyze_sector(cpv_code, title, description)

            # Compile data
            data = {
                'doc_id': doc_id,
                'form_type': form_type,
                'publication_date': pub_date,
                'year': int(pub_date[:4]) if pub_date and len(pub_date) >= 4 and pub_date[:4].isdigit() else None,
                'month': int(pub_date[4:6]) if pub_date and len(pub_date) >= 6 and pub_date[4:6].isdigit() else None,
                'contract_title': title,
                'contract_description': description,
                'cpv_main': cpv_code,
                'contract_value': value,
                'contracting_country': contracting_country,
                'performance_location': performance_location,
                'performance_country_code': performance_code,
                'contractors_json': json.dumps(contractors) if contractors else None,
                'num_contractors': len(contractors),
                'has_chinese_involvement': chinese_analysis['has_involvement'],
                'chinese_involvement_type': chinese_analysis['type'],
                'ted_procurement_chinese_entities_found': json.dumps(chinese_analysis['entities']),
                'chinese_confidence': chinese_analysis['confidence'],
                'is_critical_sector': sector_analysis['is_critical'],
                'technology_type': sector_analysis['tech_type'],
                'xml_file': file_path,
                'processing_date': datetime.now().isoformat()
            }

            # Update stats
            if chinese_analysis['has_involvement']:
                self.stats['chinese_indicators'] += 1
                if sector_analysis['is_critical']:
                    self.stats['critical_sectors'] += 1

                # Track entities
                for entity in chinese_analysis['entities']:
                    self.stats['chinese_companies'].add(entity.get('name', ''))

            if performance_code:
                self.stats['performance_locations'].add(performance_code)

            if contractors:
                self.stats['contractors_found'] += len(contractors)

            return data

        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            return None

    def extract_doc_id(self, xml_str):
        """Extract document ID"""
        patterns = [
            r'DOC_ID="([^"]+)"',
            r'<cbc:ID>([^<]+)</cbc:ID>',
            r'(\d{6}-\d{4})'
        ]

        for pattern in patterns:
            match = re.search(pattern, xml_str)
            if match:
                return match.group(1)
        return None

    def extract_form_type(self, xml_str):
        """Extract form type"""
        patterns = [
            r'<(F\d{2}_\d{4})',
            r'ContractAwardNotice',
            r'ContractNotice',
            r'PriorInformationNotice'
        ]

        for pattern in patterns:
            match = re.search(pattern, xml_str)
            if match:
                return match.group(1) if 'F' in match.group(1) else match.group(0)
        return None

    def extract_publication_date(self, xml_str):
        """Extract publication date"""
        patterns = [
            r'<DATE_PUB>(\d{8})</DATE_PUB>',
            r'<cbc:IssueDate>([^<]+)</cbc:IssueDate>',
            r'EDITION="(\d{7})"'
        ]

        for pattern in patterns:
            match = re.search(pattern, xml_str)
            if match:
                return match.group(1)
        return None

    def extract_contract_title(self, xml_str):
        """Extract contract title"""
        patterns = [
            r'<TITLE[^>]*>([^<]+)</TITLE>',
            r'<cbc:Name[^>]*>([^<]+)</cbc:Name>',
            r'<TI_TEXT><P>([^<]+)</P></TI_TEXT>'
        ]

        for pattern in patterns:
            matches = re.findall(pattern, xml_str, re.DOTALL)
            if matches:
                # Return first non-empty match
                for match in matches:
                    if match.strip() and len(match.strip()) > 10:
                        return match.strip()[:500]
        return None

    def extract_contract_description(self, xml_str):
        """Extract contract description"""
        patterns = [
            r'<SHORT_DESCR[^>]*>([^<]+)</SHORT_DESCR>',
            r'<cbc:Description[^>]*>([^<]+)</cbc:Description>'
        ]

        for pattern in patterns:
            matches = re.findall(pattern, xml_str, re.DOTALL)
            if matches:
                for match in matches:
                    if match.strip() and len(match.strip()) > 20:
                        return match.strip()[:1000]
        return None

    def extract_cpv_code(self, xml_str):
        """Extract CPV code"""
        patterns = [
            r'<CPV_CODE[^>]*CODE="([^"]+)"',
            r'<CPV_MAIN[^>]*>([^<]+)</CPV_MAIN>'
        ]

        for pattern in patterns:
            match = re.search(pattern, xml_str)
            if match:
                return match.group(1)
        return None

    def extract_contract_value(self, xml_str):
        """Extract contract value"""
        patterns = [
            r'<VAL_TOTAL[^>]*>([^<]+)</VAL_TOTAL>',
            r'<cbc:TotalAmount[^>]*>([^<]+)</cbc:TotalAmount>'
        ]

        for pattern in patterns:
            match = re.search(pattern, xml_str)
            if match:
                return match.group(1)
        return None

    def extract_contracting_country(self, xml_str):
        """Extract contracting authority country"""
        patterns = [
            r'<CONTRACTING_BODY.*?<COUNTRY[^>]*VALUE="([^"]+)"',
            r'<cac:PostalAddress.*?<cbc:IdentificationCode>([^<]+)</cbc:IdentificationCode>'
        ]

        for pattern in patterns:
            match = re.search(pattern, xml_str, re.DOTALL)
            if match:
                return match.group(1)
        return None

    def extract_performance_location(self, xml_str):
        """Extract performance location and country code"""
        location = None
        country_code = None

        # Look for performance NUTS codes
        perf_match = re.search(r'PERFORMANCE_NUTS[^>]*CODE="([^"]+)"[^>]*>([^<]*)', xml_str)
        if perf_match:
            country_code = perf_match.group(1)
            location = perf_match.group(2) if perf_match.group(2) else country_code

        # Look for MAIN_SITE
        site_match = re.search(r'<MAIN_SITE[^>]*>.*?<P>([^<]+)</P>', xml_str, re.DOTALL)
        if site_match and not location:
            location = site_match.group(1)

        # Look for NUTS codes
        nuts_match = re.search(r'<.*?NUTS[^>]*CODE="([^"]+)"', xml_str)
        if nuts_match and not country_code:
            nuts_code = nuts_match.group(1)
            if len(nuts_code) == 2:  # Country level NUTS
                country_code = nuts_code

        return location, country_code

    def extract_contractors(self, xml_str):
        """Extract contractor information"""
        contractors = []

        # Pattern for TED format contractors
        contractor_patterns = [
            r'<CONTRACTOR[^>]*>.*?<OFFICIALNAME>([^<]+)</OFFICIALNAME>.*?<COUNTRY[^>]*VALUE="([^"]+)".*?</CONTRACTOR>',
            r'<CONTRACTOR[^>]*>.*?<OFFICIALNAME>([^<]+)</OFFICIALNAME>.*?</CONTRACTOR>',
            r'<cac:WinningParty.*?<cbc:Name>([^<]+)</cbc:Name>.*?<cbc:IdentificationCode>([^<]+)</cbc:IdentificationCode>',
            r'<cac:WinningParty.*?<cbc:Name>([^<]+)</cbc:Name>'
        ]

        for pattern in contractor_patterns:
            matches = re.findall(pattern, xml_str, re.DOTALL | re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    name = match[0].strip()
                    country = match[1].strip() if len(match) > 1 else None
                else:
                    name = match.strip()
                    country = None

                if name and len(name) > 3:
                    contractors.append({
                        'name': name,
                        'country': country
                    })

        return contractors

    def analyze_chinese_involvement(self, xml_str, contractors, performance_code, title, description):
        """Comprehensive Chinese involvement analysis"""
        involvement = {
            'has_involvement': False,
            'type': None,
            'entities': [],
            'confidence': 0.0
        }

        # Check performance location
        if performance_code == 'CN':
            involvement['has_involvement'] = True
            involvement['type'] = 'Performance in China'
            involvement['confidence'] = 1.0
            involvement['entities'].append({
                'type': 'performance_location',
                'name': 'China',
                'evidence': 'Performance country code: CN'
            })

        # Check contractor countries
        for contractor in contractors:
            if contractor.get('country') in ['CN', 'CHN', 'HK', 'MO']:
                involvement['has_involvement'] = True
                involvement['type'] = 'Chinese contractor'
                involvement['confidence'] = 1.0
                involvement['entities'].append({
                    'type': 'contractor',
                    'name': contractor['name'],
                    'country': contractor['country'],
                    'evidence': f'Contractor country: {contractor["country"]}'
                })

        # Check for Chinese companies/products
        chinese_indicators = [
            'Huawei', 'ZTE', 'Alibaba', 'Tencent', 'Xiaomi', 'Lenovo',
            'BYD', 'DJI', 'Hikvision', 'Dahua', 'COSCO', 'Sinopec',
            'CRRC', 'SMIC', 'China Mobile', 'China Telecom', 'China Unicom',
            'Great Wall Motors', 'Geely', 'NIO', 'Xpeng', 'Li Auto'
        ]

        text_to_search = f"{title or ''} {description or ''} {xml_str}"

        for indicator in chinese_indicators:
            if indicator.lower() in text_to_search.lower():
                involvement['has_involvement'] = True
                if not involvement['type']:
                    involvement['type'] = 'Chinese product/technology'
                involvement['confidence'] = max(involvement['confidence'], 0.8)
                involvement['entities'].append({
                    'type': 'technology/product',
                    'name': indicator,
                    'evidence': f'Mentioned in contract text'
                })

        # Check for general China references
        china_terms = ['China', 'Chinese', 'Beijing', 'Shanghai', 'Shenzhen']
        for term in china_terms:
            if term.lower() in text_to_search.lower():
                if not involvement['has_involvement']:
                    involvement['has_involvement'] = True
                    involvement['type'] = 'China reference'
                    involvement['confidence'] = 0.5
                    involvement['entities'].append({
                        'type': 'reference',
                        'name': term,
                        'evidence': f'Mentioned in contract'
                    })

        return involvement

    def analyze_sector(self, cpv_code, title, description):
        """Analyze sector criticality"""
        critical_cpv_prefixes = [
            '30',  # Office machinery and computers
            '31',  # Electrical machinery
            '32',  # Radio, television, communication
            '33',  # Medical and precision instruments
            '34',  # Motor vehicles
            '35',  # Other transport equipment
            '48',  # Software and information systems
            '64',  # Telecommunications
            '71',  # Architectural and engineering
            '72',  # IT services
            '73',  # Research and development
            '79'   # Security services
        ]

        is_critical = False
        tech_type = None

        if cpv_code:
            prefix = cpv_code[:2]
            if prefix in critical_cpv_prefixes:
                is_critical = True

                # Determine technology type
                tech_mapping = {
                    '30': 'IT Hardware',
                    '31': 'Electrical Systems',
                    '32': 'Telecommunications',
                    '33': 'Medical Technology',
                    '34': 'Automotive',
                    '35': 'Transportation',
                    '48': 'Software',
                    '64': 'Telecommunications',
                    '71': 'Engineering',
                    '72': 'IT Services',
                    '73': 'R&D',
                    '79': 'Security'
                }
                tech_type = tech_mapping.get(prefix, 'Critical Technology')

        # Also check title/description for critical keywords
        text = f"{title or ''} {description or ''}".lower()
        critical_keywords = [
            '5g', 'artificial intelligence', 'ai', 'cybersecurity',
            'surveillance', 'defense', 'military', 'critical infrastructure',
            'telecommunications', 'semiconductor', 'quantum'
        ]

        for keyword in critical_keywords:
            if keyword in text:
                is_critical = True
                tech_type = keyword.title()
                break

        return {
            'is_critical': is_critical,
            'tech_type': tech_type
        }

    def save_to_database(self, data):
        """Save extracted data to database"""
        if not data:
            return

        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        columns = list(data.keys())
        values = list(data.values())
        placeholders = ','.join(['?' for _ in values])
        columns_str = ','.join(columns)

        try:
            cur.execute(f'INSERT INTO ted_complete_analysis ({columns_str}) VALUES ({placeholders})', values)
            conn.commit()
        except Exception as e:
            logger.error(f"Database error: {e}")
        finally:
            conn.close()

    def process_tar_file(self, tar_path, year, month):
        """Process a single tar file"""
        logger.info(f"Processing {tar_path}")

        if not os.path.exists(tar_path):
            logger.warning(f"File not found: {tar_path}")
            return

        try:
            with tarfile.open(tar_path, 'r:gz') as monthly_tar:
                daily_files = [f for f in monthly_tar.getnames() if f.endswith('.tar.gz')]

                # Process all daily files
                for daily_file in daily_files:
                    try:
                        daily_obj = monthly_tar.extractfile(daily_file)

                        with tarfile.open(fileobj=daily_obj, mode='r:gz') as daily_tar:
                            xml_files = [f for f in daily_tar.getnames() if f.endswith('.xml')]

                            # Process all XML files
                            for xml_file in xml_files:
                                try:
                                    xml_obj = daily_tar.extractfile(xml_file)
                                    content = xml_obj.read()

                                    data = self.extract_comprehensive_data(content, xml_file)
                                    if data:
                                        self.save_to_database(data)
                                        self.stats['total_files'] += 1

                                        # Progress logging
                                        if self.stats['total_files'] % 1000 == 0:
                                            self.log_progress()

                                except Exception as e:
                                    logger.warning(f"Error processing XML {xml_file}: {e}")

                    except Exception as e:
                        logger.warning(f"Error processing daily tar {daily_file}: {e}")

        except Exception as e:
            logger.error(f"Error processing monthly tar {tar_path}: {e}")

    def log_progress(self):
        """Log processing progress"""
        elapsed = time.time() - self.stats['start_time']
        rate = self.stats['total_files'] / elapsed if elapsed > 0 else 0

        logger.info(f"Progress: {self.stats['total_files']:,} files, "
                   f"{self.stats['chinese_indicators']:,} Chinese indicators, "
                   f"{self.stats['contractors_found']:,} contractors, "
                   f"Rate: {rate:.1f} files/sec")

    def process_year(self, year):
        """Process all months of a year"""
        logger.info(f"Processing year {year}")

        year_stats = {
            'files': 0,
            'chinese': 0,
            'contractors': 0
        }

        for month in range(1, 13):
            tar_path = f"F:/TED_Data/monthly/{year}/TED_monthly_{year}_{month:02d}.tar.gz"

            if os.path.exists(tar_path):
                files_before = self.stats['total_files']
                chinese_before = self.stats['chinese_indicators']

                self.process_tar_file(tar_path, year, month)
                self.stats['months_processed'] += 1

                files_this_month = self.stats['total_files'] - files_before
                chinese_this_month = self.stats['chinese_indicators'] - chinese_before

                year_stats['files'] += files_this_month
                year_stats['chinese'] += chinese_this_month

                logger.info(f"Month {year}-{month:02d}: {files_this_month:,} files, "
                           f"{chinese_this_month:,} Chinese indicators")

        self.stats['by_year'][year] = year_stats
        self.stats['years_processed'].append(year)

        logger.info(f"Year {year} complete: {year_stats['files']:,} files, "
                   f"{year_stats['chinese']:,} Chinese indicators")

    def generate_final_report(self):
        """Generate comprehensive final report"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        print("\n" + "="*80)
        print("TED COMPLETE DATASET ANALYSIS - FINAL REPORT")
        print("="*80)

        elapsed = time.time() - self.stats['start_time']

        print(f"\nProcessing Summary:")
        print(f"  Duration: {elapsed/3600:.1f} hours")
        print(f"  Years processed: {sorted(self.stats['years_processed'])}")
        print(f"  Months processed: {self.stats['months_processed']}")
        print(f"  Total files: {self.stats['total_files']:,}")
        print(f"  Chinese indicators found: {self.stats['chinese_indicators']:,}")
        print(f"  Penetration rate: {self.stats['chinese_indicators']/max(1,self.stats['total_files'])*100:.2f}%")

        # Database summary
        cur.execute("SELECT COUNT(*) FROM ted_complete_analysis")
        total_records = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM ted_complete_analysis WHERE has_chinese_involvement = 1")
        chinese_records = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM ted_complete_analysis WHERE is_critical_sector = 1 AND has_chinese_involvement = 1")
        critical_chinese = cur.fetchone()[0]

        print(f"\nDatabase Analysis:")
        print(f"  Total records: {total_records:,}")
        print(f"  Chinese involvement: {chinese_records:,}")
        print(f"  Critical sector Chinese: {critical_chinese:,}")
        print(f"  Chinese penetration: {chinese_records/max(1,total_records)*100:.2f}%")

        # Year by year
        print(f"\nYear-by-Year Analysis:")
        for year in sorted(self.stats['by_year'].keys()):
            stats = self.stats['by_year'][year]
            rate = stats['chinese']/max(1,stats['files'])*100
            print(f"  {year}: {stats['files']:,} files, {stats['chinese']:,} Chinese ({rate:.2f}%)")

        # Chinese involvement types
        cur.execute('''
            SELECT chinese_involvement_type, COUNT(*) as count
            FROM ted_complete_analysis
            WHERE has_chinese_involvement = 1
            GROUP BY chinese_involvement_type
            ORDER BY count DESC
        ''')

        print(f"\nChinese Involvement Types:")
        for inv_type, count in cur.fetchall():
            print(f"  {inv_type}: {count:,}")

        # Critical sectors
        cur.execute('''
            SELECT technology_type, COUNT(*) as count
            FROM ted_complete_analysis
            WHERE is_critical_sector = 1 AND has_chinese_involvement = 1
            GROUP BY technology_type
            ORDER BY count DESC
        ''')

        print(f"\nCritical Sectors with Chinese Involvement:")
        for tech_type, count in cur.fetchall():
            print(f"  {tech_type}: {count:,}")

        # Performance locations
        cur.execute('''
            SELECT performance_country_code, COUNT(*) as count
            FROM ted_complete_analysis
            WHERE performance_country_code IS NOT NULL
            GROUP BY performance_country_code
            ORDER BY count DESC
            LIMIT 10
        ''')

        print(f"\nTop Performance Locations:")
        for country, count in cur.fetchall():
            print(f"  {country}: {count:,}")

        conn.close()

        return {
            'total_files': self.stats['total_files'],
            'chinese_indicators': self.stats['chinese_indicators'],
            'penetration_rate': self.stats['chinese_indicators']/max(1,self.stats['total_files'])*100,
            'years_processed': self.stats['years_processed'],
            'critical_sectors': self.stats['critical_sectors']
        }


def main():
    """Main execution"""
    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"

    processor = TEDCompleteProcessor(db_path)

    # Process multiple years
    years_to_process = [2024, 2023, 2022]  # Start with recent years

    for year in years_to_process:
        processor.process_year(year)

    # Generate final report
    results = processor.generate_final_report()

    # Save results
    with open("C:/Projects/OSINT - Foresight/analysis/ted_complete_results.json", 'w') as f:
        json.dump(results, f, indent=2)

    logger.info("Complete processing finished!")

    return results


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
TED XML Deep Extractor
Extracts ALL data from complex nested TED XML structures
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

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TEDDeepExtractor:
    """Deep extraction of all TED XML data"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()
        self.stats = {
            'total_processed': 0,
            'with_contractors': 0,
            'chinese_found': 0,
            'forms': {}
        }

    def init_database(self):
        """Create database for extracted data"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute('DROP TABLE IF EXISTS ted_deep_extract')

        cur.execute('''
            CREATE TABLE ted_deep_extract (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                doc_id TEXT,
                form_type TEXT,
                language TEXT,
                publication_date TEXT,

                -- Full text extraction
                full_text TEXT,

                -- Contractor data (JSON array for multiple)
                contractors_json TEXT,
                num_contractors INTEGER DEFAULT 0,

                -- Chinese detection
                has_chinese_indicators BOOLEAN DEFAULT 0,
                chinese_terms_found TEXT,

                -- Raw data
                xml_file TEXT,
                processing_date TEXT
            )
        ''')

        conn.commit()
        conn.close()

    def extract_all_text(self, element, prefix=""):
        """Recursively extract all text from XML element"""
        texts = []

        # Get element text
        if element.text and element.text.strip():
            texts.append(f"{prefix}{element.tag}: {element.text.strip()}")

        # Get attributes
        if element.attrib:
            for key, value in element.attrib.items():
                texts.append(f"{prefix}{element.tag}@{key}: {value}")

        # Process children
        for child in element:
            child_texts = self.extract_all_text(child, prefix + "  ")
            texts.extend(child_texts)

        return texts

    def find_contractors_deep(self, root):
        """Deep search for contractor information anywhere in XML"""
        contractors = []

        # Convert to string and search
        xml_str = ET.tostring(root, encoding='unicode')

        # Multiple patterns to find contractors
        patterns = [
            r'<OFFICIALNAME>(.*?)</OFFICIALNAME>',
            r'<cbc:Name>(.*?)</cbc:Name>',
            r'<Name>(.*?)</Name>',
            r'CONTRACTOR.*?OFFICIALNAME>(.*?)</OFFICIALNAME',
            r'WinningParty.*?Name>(.*?)</.*?Name>'
        ]

        for pattern in patterns:
            matches = re.findall(pattern, xml_str, re.DOTALL | re.IGNORECASE)
            for match in matches:
                if match and len(match) > 3:  # Filter out short matches
                    # Clean the match
                    clean = match.strip().replace('\n', ' ').replace('\t', ' ')
                    if clean and 'CONTRACTING' not in clean.upper():  # Exclude contracting authorities
                        contractors.append(clean)

        # Also look for country codes
        country_patterns = [
            r'<COUNTRY.*?VALUE="(.*?)"',
            r'<COUNTRY>(.*?)</COUNTRY>',
            r'<cbc:IdentificationCode>(.*?)</cbc:IdentificationCode>'
        ]

        countries = []
        for pattern in country_patterns:
            matches = re.findall(pattern, xml_str, re.IGNORECASE)
            countries.extend(matches)

        # Combine contractors with countries if possible
        contractor_data = []
        for i, contractor in enumerate(contractors):
            data = {
                'name': contractor,
                'country': countries[i] if i < len(countries) else None
            }
            contractor_data.append(data)

        return contractor_data

    def check_chinese_indicators(self, xml_str):
        """Check for Chinese indicators in entire XML"""
        chinese_terms = [
            'China', 'Chinese', 'Beijing', 'Shanghai', 'Shenzhen',
            'Guangzhou', 'Huawei', 'ZTE', 'Alibaba', 'Tencent',
            'Xiaomi', 'Lenovo', 'BYD', 'DJI', 'Hikvision',
            'COSCO', 'Sinopec', 'PetroChina', 'CRRC'
        ]

        # Also check country codes
        if re.search(r'<COUNTRY.*?VALUE="CN"', xml_str, re.IGNORECASE):
            return True, ['Country code: CN']
        if re.search(r'<COUNTRY>CN</COUNTRY>', xml_str, re.IGNORECASE):
            return True, ['Country code: CN']

        found_terms = []
        for term in chinese_terms:
            if term.lower() in xml_str.lower():
                # Get context
                pattern = f'.{{0,50}}{term}.{{0,50}}'
                matches = re.findall(pattern, xml_str, re.IGNORECASE)
                if matches:
                    found_terms.append(f"{term}: {matches[0][:100]}")

        return len(found_terms) > 0, found_terms

    def process_xml_file(self, xml_content, file_path):
        """Process a single XML file"""
        self.stats['total_processed'] += 1

        try:
            root = ET.fromstring(xml_content)
            xml_str = xml_content.decode('utf-8', errors='ignore')

            # Extract basic info
            doc_id = None
            form_type = None

            # Get document ID
            if 'DOC_ID' in root.attrib:
                doc_id = root.attrib['DOC_ID']
            else:
                # Try to find it in the XML
                doc_match = re.search(r'DOC_ID["\']?\s*[:=]\s*["\']?(\d+-\d+)', xml_str)
                if doc_match:
                    doc_id = doc_match.group(1)

            # Get form type
            form_matches = re.findall(r'<(F\d{2}_\d{4})', xml_str)
            if form_matches:
                form_type = form_matches[0]

            # Extract all text
            full_text = ' '.join(self.extract_all_text(root))

            # Find contractors
            contractors = self.find_contractors_deep(root)

            # Check for Chinese indicators
            has_chinese, chinese_terms = self.check_chinese_indicators(xml_str)

            # Update stats
            if contractors:
                self.stats['with_contractors'] += 1
            if has_chinese:
                self.stats['chinese_found'] += 1
            if form_type:
                if form_type not in self.stats['forms']:
                    self.stats['forms'][form_type] = 0
                self.stats['forms'][form_type] += 1

            # Save to database
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()

            cur.execute('''
                INSERT INTO ted_deep_extract (
                    doc_id, form_type, full_text,
                    contractors_json, num_contractors,
                    has_chinese_indicators, chinese_terms_found,
                    xml_file, processing_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                doc_id,
                form_type,
                full_text[:10000],  # Limit text length
                json.dumps(contractors) if contractors else None,
                len(contractors),
                has_chinese,
                json.dumps(chinese_terms) if chinese_terms else None,
                file_path,
                datetime.now().isoformat()
            ))

            conn.commit()
            conn.close()

            # Log progress
            if self.stats['total_processed'] % 100 == 0:
                logger.info(f"Processed {self.stats['total_processed']} files: "
                          f"{self.stats['with_contractors']} with contractors, "
                          f"{self.stats['chinese_found']} with Chinese indicators")

            # Log Chinese findings immediately
            if has_chinese:
                logger.info(f"CHINESE FOUND in {doc_id}: {chinese_terms[:2]}")

        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")

    def process_tar_file(self, tar_path):
        """Process TED tar file"""
        logger.info(f"Processing {tar_path}")

        with tarfile.open(tar_path, 'r:gz') as monthly_tar:
            daily_files = [f for f in monthly_tar.getnames() if f.endswith('.tar.gz')]

            # Process first 3 daily files
            for daily_file in daily_files[:3]:
                logger.info(f"Processing daily: {daily_file}")

                daily_obj = monthly_tar.extractfile(daily_file)
                with tarfile.open(fileobj=daily_obj, mode='r:gz') as daily_tar:
                    xml_files = [f for f in daily_tar.getnames() if f.endswith('.xml')]

                    # Process first 200 XMLs per day
                    for xml_file in xml_files[:200]:
                        try:
                            xml_obj = daily_tar.extractfile(xml_file)
                            content = xml_obj.read()
                            self.process_xml_file(content, xml_file)
                        except Exception as e:
                            logger.warning(f"Error with {xml_file}: {e}")

    def generate_report(self):
        """Generate extraction report"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        print("\n" + "="*80)
        print("TED DEEP EXTRACTION REPORT")
        print("="*80)

        print(f"\nFiles processed: {self.stats['total_processed']}")
        print(f"Files with contractors: {self.stats['with_contractors']}")
        print(f"Files with Chinese indicators: {self.stats['chinese_found']}")

        print("\nForm types found:")
        for form, count in sorted(self.stats['forms'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {form}: {count}")

        # Database analysis
        cur.execute("SELECT COUNT(*) FROM ted_deep_extract WHERE num_contractors > 0")
        with_contractors = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM ted_deep_extract WHERE has_chinese_indicators = 1")
        chinese_count = cur.fetchone()[0]

        print(f"\nDatabase summary:")
        print(f"  Records with contractors: {with_contractors}")
        print(f"  Records with Chinese indicators: {chinese_count}")

        # Show Chinese examples
        if chinese_count > 0:
            print("\nChinese indicators found:")
            cur.execute('''
                SELECT doc_id, form_type, chinese_terms_found
                FROM ted_deep_extract
                WHERE has_chinese_indicators = 1
                LIMIT 10
            ''')

            for doc_id, form_type, terms in cur.fetchall():
                print(f"  {doc_id} ({form_type}): {terms[:100]}")

        # Show contractor examples
        print("\nSample contractors:")
        cur.execute('''
            SELECT doc_id, contractors_json
            FROM ted_deep_extract
            WHERE num_contractors > 0
            LIMIT 5
        ''')

        for doc_id, contractors_json in cur.fetchall():
            if contractors_json:
                contractors = json.loads(contractors_json)
                for contractor in contractors[:2]:
                    print(f"  {doc_id}: {contractor.get('name', 'N/A')[:60]} ({contractor.get('country', 'N/A')})")

        conn.close()


def main():
    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"

    extractor = TEDDeepExtractor(db_path)

    # Process January 2024
    tar_path = "F:/TED_Data/monthly/2024/TED_monthly_2024_01.tar.gz"
    extractor.process_tar_file(tar_path)

    # Generate report
    extractor.generate_report()

    return extractor.stats


if __name__ == "__main__":
    main()

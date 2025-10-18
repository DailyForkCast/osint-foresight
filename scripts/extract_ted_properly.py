#!/usr/bin/env python3
"""
Extract TED nested archives properly from year-organized structure
"""

import os
import tarfile
import logging
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
import json
import csv
import re

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class TEDExtractorFixed:
    """Extract nested TED archives from year directories"""

    def __init__(self):
        self.source_dir = Path("F:/TED_Data/monthly")
        self.extract_dir = Path("F:/TED_Data/extracted")
        self.extract_dir.mkdir(parents=True, exist_ok=True)
        self.csv_dir = Path("F:/TED_Data/extracted_csv")
        self.csv_dir.mkdir(parents=True, exist_ok=True)

        # China and Europe patterns
        self.china_patterns = [
            r'\bchina\b', r'\bchinese\b', r'\bbeijing\b', r'\bshanghai\b',
            r'\bguangzhou\b', r'\bshenzhen\b', r'\bhong kong\b',
            r'\bhuawei\b', r'\bzte\b', r'\balibaba\b', r'\btencent\b',
            r'\bsinopec\b', r'\bpetrochin', r'\blenovo\b', r'\bxiaomi\b'
        ]

        self.europe_countries = {
            'AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR', 'DE', 'GR',
            'HU', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'NL', 'PL', 'PT', 'RO', 'SK',
            'SI', 'ES', 'SE', 'GB', 'NO', 'CH', 'IS', 'LI', 'TR', 'RU', 'UA'
        }

    def run(self):
        """Main extraction process"""
        logging.info("="*60)
        logging.info("TED NESTED ARCHIVE EXTRACTION")
        logging.info("="*60)

        # Find all tar.gz files recursively
        archives = list(self.source_dir.rglob("*.tar.gz"))
        logging.info(f"Found {len(archives)} TED archives to process")

        stats = {
            'total_archives': len(archives),
            'processed_archives': 0,
            'china_contracts': 0,
            'xml_files_processed': 0,
            'errors': []
        }

        # Process each archive
        for archive_num, archive in enumerate(archives, 1):
            if archive_num > 10:  # Process first 10 for testing
                break

            logging.info(f"\n[{archive_num}/{len(archives)}] Processing: {archive.name}")

            try:
                china_contracts = self.process_archive(archive)
                stats['china_contracts'] += len(china_contracts)
                stats['processed_archives'] += 1

            except Exception as e:
                error_msg = f"Failed to process {archive.name}: {e}"
                logging.error(error_msg)
                stats['errors'].append(error_msg)

        # Save summary
        self.save_summary(stats)

        logging.info("\n" + "="*60)
        logging.info("EXTRACTION COMPLETE")
        logging.info("="*60)
        logging.info(f"Archives processed: {stats['processed_archives']}/{stats['total_archives']}")
        logging.info(f"China-related contracts found: {stats['china_contracts']}")
        logging.info(f"XML files processed: {stats['xml_files_processed']}")

        return stats

    def process_archive(self, archive_path):
        """Process a single archive"""
        china_contracts = []

        # Create temporary extraction directory
        temp_dir = self.extract_dir / f"temp_{archive_path.stem}"
        temp_dir.mkdir(parents=True, exist_ok=True)

        try:
            # Extract outer archive
            logging.info(f"  Extracting outer archive...")
            with tarfile.open(archive_path, 'r:gz') as outer_tar:
                outer_tar.extractall(temp_dir)

            # Find inner archives
            inner_archives = list(temp_dir.rglob("*.tar.gz"))
            logging.info(f"  Found {len(inner_archives)} inner archives")

            # Process each inner archive
            for inner_num, inner_archive in enumerate(inner_archives, 1):
                if inner_num > 5:  # Limit inner archives per outer
                    break

                logging.info(f"    Processing inner archive {inner_num}/{len(inner_archives)}: {inner_archive.name}")

                # Extract inner archive
                inner_dir = inner_archive.parent / inner_archive.stem
                inner_dir.mkdir(parents=True, exist_ok=True)

                try:
                    with tarfile.open(inner_archive, 'r:gz') as inner_tar:
                        inner_tar.extractall(inner_dir)

                    # Process XML files
                    xml_files = list(inner_dir.glob("*.xml"))
                    logging.info(f"      Found {len(xml_files)} XML files")

                    for xml_file in xml_files[:100]:  # Process first 100 XML per inner archive
                        contract_data = self.process_xml(xml_file)
                        if contract_data:
                            china_contracts.append(contract_data)

                finally:
                    # Clean up inner extraction
                    if inner_dir.exists():
                        import shutil
                        shutil.rmtree(inner_dir, ignore_errors=True)

            # Save contracts to CSV if found
            if china_contracts:
                self.save_contracts_csv(china_contracts, archive_path.stem)

        finally:
            # Clean up temp directory
            if temp_dir.exists():
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)

        return china_contracts

    def process_xml(self, xml_file):
        """Process single XML file for China content"""
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()

            # Convert to text for searching
            xml_text = ET.tostring(root, encoding='unicode').lower()

            # Check for China references
            has_china = any(re.search(pattern, xml_text) for pattern in self.china_patterns)

            if has_china:
                # Extract contract data
                return self.extract_contract_data(root, xml_file.name)

        except Exception as e:
            logging.debug(f"Error parsing {xml_file}: {e}")

        return None

    def extract_contract_data(self, root, filename):
        """Extract structured data from XML"""
        try:
            # Common TED XML paths (adjust based on actual structure)
            data = {
                'filename': filename,
                'notice_id': self.get_text(root, './/NOTICE/@VALUE'),
                'title': self.get_text(root, './/TITLE'),
                'buyer_name': self.get_text(root, './/NAME'),
                'buyer_country': self.get_text(root, './/COUNTRY/@VALUE'),
                'contract_value': self.get_text(root, './/VALUE/@AMOUNT'),
                'currency': self.get_text(root, './/VALUE/@CURRENCY'),
                'publication_date': self.get_text(root, './/DATE_PUB'),
                'contractor_name': self.get_text(root, './/CONTRACTOR/NAME'),
                'contractor_country': self.get_text(root, './/CONTRACTOR/COUNTRY/@VALUE'),
                'cpv_codes': self.get_text(root, './/CPV_CODE/@CODE'),
                'procedure_type': self.get_text(root, './/PROCEDURE/@VALUE')
            }

            # Only return if we have meaningful data
            if data['notice_id'] or data['title']:
                return data

        except Exception as e:
            logging.debug(f"Error extracting data: {e}")

        return None

    def get_text(self, element, path):
        """Safely extract text from XML element"""
        try:
            elem = element.find(path)
            if elem is not None:
                if elem.text:
                    return elem.text
                # Check for attribute value
                if '@' in path:
                    attr_name = path.split('@')[-1]
                    return elem.get(attr_name, '')
            return ''
        except:
            return ''

    def save_contracts_csv(self, contracts, archive_name):
        """Save contracts to CSV file"""
        csv_file = self.csv_dir / f"china_contracts_{archive_name}.csv"

        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            if contracts:
                writer = csv.DictWriter(f, fieldnames=contracts[0].keys())
                writer.writeheader()
                writer.writerows(contracts)

        logging.info(f"      Saved {len(contracts)} contracts to {csv_file.name}")

    def save_summary(self, stats):
        """Save extraction summary"""
        summary = {
            'timestamp': datetime.now().isoformat(),
            'stats': stats
        }

        summary_file = self.csv_dir / 'extraction_summary.json'
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

        # Also create markdown report
        report = f"""
# TED Extraction Report
Generated: {datetime.now().isoformat()}

## Statistics
- Total archives found: {stats['total_archives']}
- Archives processed: {stats['processed_archives']}
- China-related contracts: {stats['china_contracts']}
- XML files processed: {stats['xml_files_processed']}

## Errors
{chr(10).join(stats['errors']) if stats['errors'] else 'No errors'}

## Output Files
- Extracted CSVs: F:/TED_Data/extracted_csv/
- Summary: F:/TED_Data/extracted_csv/extraction_summary.json
"""

        report_file = Path("C:/Projects/OSINT - Foresight/analysis/TED_EXTRACTION_REPORT.md")
        with open(report_file, 'w') as f:
            f.write(report)


if __name__ == "__main__":
    extractor = TEDExtractorFixed()
    extractor.run()
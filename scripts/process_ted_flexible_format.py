#!/usr/bin/env python3
"""
TED Flexible Format Processor
Handles both nested (tar.gz in tar.gz) and direct XML archive formats
Designed to process the 2016-2022 gap where format changed
"""

import tarfile
import xml.etree.ElementTree as ET
from pathlib import Path
import logging
import json
from datetime import datetime
from typing import Dict, List, Set
import time
import re
import io

class FlexibleTEDProcessor:
    """Process TED archives regardless of format (nested or direct XML)"""

    def __init__(self, output_dir: Path = None):
        self.output_dir = output_dir or Path("data/processed/ted_flexible_2016_2022")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Load previous results if they exist
        self.load_existing_results()

        # Chinese entities to search for - using word boundaries for accuracy
        # High-confidence entities (distinctive names)
        self.chinese_entities = [
            'huawei', 'zte', 'lenovo', 'xiaomi', 'alibaba', 'tencent',
            'baidu', 'bytedance', 'tiktok', 'dji', 'dahua', 'hikvision',
            'china mobile', 'china telecom', 'china unicom',
            'haier', 'hisense', 'tcl', 'oppo', 'vivo', 'oneplus',
            'byd', 'geely', 'xpeng', 'li auto',
            'smic', 'boe', 'catl', 'ganfeng', 'tianqi',
            'sinopec', 'petrochina', 'cnooc', 'state grid',
            'china railway', 'china construction', 'china communications',
            'crrc', 'comac', 'avic',
            'bank of china', 'icbc', 'china construction bank',
            'agricultural bank', 'ping an', 'china life',
            'jd.com', 'jd com', 'pinduoduo', 'meituan', 'didi',
            'netease', 'weibo',
            'wechat', 'alipay', 'unionpay',
            'cosco', 'china shipping', 'china merchants',
            'sinochem', 'chemchina', 'sinopharm',
            'beijing', 'shanghai', 'shenzhen', 'guangzhou', 'hong kong'
        ]

        # Special handling for ambiguous terms
        # NIO - only match when uppercase or with specific context
        self.special_entities = {
            'NIO': r'\bNIO\b',  # Only match uppercase NIO
            'China': r'\bChina\b',  # Case-sensitive China
            'Chinese': r'\bChinese\b',  # Case-sensitive Chinese
            'PRC': r'\bPRC\b',  # Only uppercase PRC (People's Republic of China)
            'People\'s Republic of China': r'\bPeople\'s Republic of China\b',
            'SINA': r'\bSINA\b',  # Only uppercase SINA Corporation
            'Sohu': r'\bSohu\b'  # Case-sensitive Sohu
        }

        # Compile regex patterns with word boundaries for accurate matching
        self.china_patterns = []

        # Standard entities with case-insensitive matching
        for entity in self.chinese_entities:
            pattern = r'\b' + re.escape(entity) + r'\b'
            self.china_patterns.append(re.compile(pattern, re.IGNORECASE))

        # Special entities with case-sensitive or specific patterns
        for entity, pattern in self.special_entities.items():
            self.china_patterns.append(re.compile(pattern))

        # EU country codes
        self.eu_countries = {
            'AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR',
            'DE', 'GR', 'HU', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'NL',
            'PL', 'PT', 'RO', 'SK', 'SI', 'ES', 'SE',
            'GB', 'UK', 'NO', 'CH', 'IS', 'LI',  # Include UK, Norway, Switzerland, Iceland
            'AL', 'BA', 'XK', 'ME', 'MK', 'RS', 'TR', 'UA', 'MD', 'GE', 'AM',
            'GL', 'FO'  # Greenland, Faroe Islands
        }

        self.results = {
            "china_contracts": [],
            "archives_processed": 0,
            "xml_files_processed": 0,
            "processing_errors": [],
            "format_detection": {},
            "processed_archives": set()  # Track which archives we've already done
        }

    def load_existing_results(self):
        """Load previous results if they exist"""
        results_file = self.output_dir / "results.json"
        if results_file.exists():
            try:
                with open(results_file, 'r') as f:
                    existing = json.load(f)
                    self.results = existing
                    # Convert list to set for processed archives
                    if "processed_archives" in self.results:
                        self.results["processed_archives"] = set(self.results["processed_archives"])
                    else:
                        # Build from format_detection keys
                        self.results["processed_archives"] = set()
                        for archive_path in self.results.get("format_detection", {}).keys():
                            archive_name = Path(archive_path).name
                            self.results["processed_archives"].add(archive_name)

                    logging.info(f"Loaded existing results: {self.results['archives_processed']} archives already processed")
                    logging.info(f"Found {len(self.results['china_contracts'])} existing contracts")
            except Exception as e:
                logging.warning(f"Could not load existing results: {e}")

    def detect_archive_format(self, archive_path: Path) -> str:
        """Detect if archive contains nested tar.gz or direct XML files"""
        try:
            with tarfile.open(archive_path, 'r:gz') as tar:
                # Check first few members
                members = tar.getmembers()[:10]

                has_tar_gz = any(m.name.endswith('.tar.gz') for m in members)
                has_xml = any(m.name.endswith('.xml') for m in members)

                if has_tar_gz:
                    return "nested"
                elif has_xml:
                    return "direct"
                else:
                    return "unknown"
        except Exception as e:
            logging.error(f"Error detecting format for {archive_path}: {e}")
            return "error"

    def search_chinese_entities(self, text: str) -> List[str]:
        """Search for Chinese entities in text"""
        found_entities = []

        # Check standard entities
        for i, entity in enumerate(self.chinese_entities):
            if self.china_patterns[i].search(text):
                found_entities.append(entity)

        # Check special entities (starting after standard entities)
        special_start_idx = len(self.chinese_entities)
        for j, (entity_name, _) in enumerate(self.special_entities.items()):
            pattern_idx = special_start_idx + j
            if pattern_idx < len(self.china_patterns) and self.china_patterns[pattern_idx].search(text):
                found_entities.append(entity_name)

        return list(set(found_entities))  # Remove duplicates

    def parse_xml_content(self, xml_content: bytes, source_info: Dict) -> Dict:
        """Parse XML content and search for Chinese entities"""
        try:
            # Parse XML
            root = ET.fromstring(xml_content)

            # Convert entire XML to string for searching
            xml_text = xml_content.decode('utf-8', errors='ignore')

            # Search for Chinese entities
            found_entities = self.search_chinese_entities(xml_text)

            if found_entities:
                # Extract contract details
                contract_id = None
                country = None
                date = None
                value = None

                # Try to extract contract ID
                notice_elem = root.find('.//{*}NO_DOC_OJS')
                if notice_elem is not None:
                    contract_id = notice_elem.text

                # Try to extract country
                country_elem = root.find('.//{*}ISO_COUNTRY')
                if country_elem is not None:
                    country = country_elem.get('VALUE')

                # Try to extract date
                date_elem = root.find('.//{*}DATE_PUB')
                if date_elem is not None:
                    date = date_elem.text

                # Try to extract value
                value_elem = root.find('.//{*}VALUE')
                if value_elem is not None:
                    value = value_elem.text
                    currency = value_elem.get('CURRENCY', 'EUR')
                else:
                    currency = 'EUR'

                return {
                    "contract_id": contract_id or "unknown",
                    "authority_country": country or "unknown",
                    "chinese_entities": found_entities,
                    "date": date or "unknown",
                    "value": value,
                    "currency": currency,
                    "source_archive": source_info["archive"],
                    "source_file": source_info["file"],
                    "xml_snippet": xml_text[:500]  # First 500 chars for verification
                }

        except Exception as e:
            logging.debug(f"Error parsing XML: {e}")
            return None

    def process_nested_archive(self, archive_path: Path) -> int:
        """Process archive with nested tar.gz structure (2014-2015 format)"""
        xml_count = 0
        logging.info(f"Processing as NESTED format: {archive_path.name}")

        try:
            with tarfile.open(archive_path, 'r:gz') as outer_tar:
                inner_archives = [m for m in outer_tar.getmembers() if m.name.endswith('.tar.gz')]

                for inner_member in inner_archives:
                    try:
                        inner_file_obj = outer_tar.extractfile(inner_member)
                        if inner_file_obj:
                            with tarfile.open(fileobj=inner_file_obj, mode='r:gz') as inner_tar:
                                xml_members = [m for m in inner_tar.getmembers() if m.name.endswith('.xml')]

                                for xml_member in xml_members:
                                    xml_file_obj = inner_tar.extractfile(xml_member)
                                    if xml_file_obj:
                                        xml_content = xml_file_obj.read()
                                        source_info = {
                                            "archive": str(archive_path),
                                            "file": f"{inner_member.name}/{xml_member.name}"
                                        }

                                        result = self.parse_xml_content(xml_content, source_info)
                                        if result:
                                            self.results["china_contracts"].append(result)
                                            logging.info(f"*** FOUND: {result['chinese_entities']} in {xml_member.name}")

                                        xml_count += 1
                                        if xml_count % 1000 == 0:
                                            logging.info(f"  Processed {xml_count} XML files...")

                    except Exception as e:
                        logging.debug(f"Error processing inner archive {inner_member.name}: {e}")

        except Exception as e:
            logging.error(f"Error processing nested archive {archive_path}: {e}")

        return xml_count

    def process_direct_archive(self, archive_path: Path) -> int:
        """Process archive with direct XML files (2016-2022 format)"""
        xml_count = 0
        logging.info(f"Processing as DIRECT format: {archive_path.name}")

        try:
            with tarfile.open(archive_path, 'r:gz') as tar:
                xml_members = [m for m in tar.getmembers() if m.name.endswith('.xml')]
                total_xmls = len(xml_members)
                logging.info(f"  Found {total_xmls:,} XML files to process")

                for i, xml_member in enumerate(xml_members):
                    try:
                        xml_file_obj = tar.extractfile(xml_member)
                        if xml_file_obj:
                            xml_content = xml_file_obj.read()
                            source_info = {
                                "archive": str(archive_path),
                                "file": xml_member.name
                            }

                            result = self.parse_xml_content(xml_content, source_info)
                            if result:
                                self.results["china_contracts"].append(result)
                                logging.info(f"*** FOUND: {result['chinese_entities']} in {xml_member.name}")

                            xml_count += 1

                            # Progress update every 5000 files
                            if xml_count % 5000 == 0:
                                percent = (xml_count / total_xmls) * 100
                                logging.info(f"  Progress: {xml_count:,}/{total_xmls:,} ({percent:.1f}%)")

                    except Exception as e:
                        logging.debug(f"Error processing XML {xml_member.name}: {e}")

        except Exception as e:
            logging.error(f"Error processing direct archive {archive_path}: {e}")

        return xml_count

    def process_archive(self, archive_path: Path) -> Dict:
        """Process a single archive file with format detection"""
        # Skip if already processed
        if archive_path.name in self.results.get("processed_archives", set()):
            logging.info(f"Skipping already processed: {archive_path.name}")
            return {}

        logging.info(f"\\nProcessing: {archive_path.name}")
        start_time = time.time()

        # Detect format
        format_type = self.detect_archive_format(archive_path)
        self.results["format_detection"][str(archive_path)] = format_type

        xml_count = 0

        if format_type == "nested":
            xml_count = self.process_nested_archive(archive_path)
        elif format_type == "direct":
            xml_count = self.process_direct_archive(archive_path)
        else:
            logging.warning(f"Unknown format for {archive_path.name}: {format_type}")
            self.results["processing_errors"].append({
                "archive": str(archive_path),
                "error": f"Unknown format: {format_type}"
            })

        self.results["archives_processed"] += 1
        self.results["xml_files_processed"] += xml_count
        self.results["processed_archives"].add(archive_path.name)

        duration = time.time() - start_time
        contracts_found = len([c for c in self.results["china_contracts"] if c["source_archive"] == str(archive_path)])

        logging.info(f"Completed {archive_path.name}:")
        logging.info(f"  Format: {format_type}")
        logging.info(f"  XML files: {xml_count:,}")
        logging.info(f"  Contracts found: {contracts_found}")
        logging.info(f"  Time: {duration:.1f}s")

        return {
            "archive": str(archive_path),
            "format": format_type,
            "xml_files_processed": xml_count,
            "china_contracts_found": contracts_found,
            "processing_time": duration
        }

    def save_results(self):
        """Save all results to JSON files"""
        # Convert set to list for JSON serialization
        results_to_save = self.results.copy()
        results_to_save["processed_archives"] = list(self.results.get("processed_archives", set()))

        # Save main results
        with open(self.output_dir / "results.json", 'w') as f:
            json.dump(results_to_save, f, indent=2)

        # Save contracts separately for easier analysis
        if self.results["china_contracts"]:
            with open(self.output_dir / "china_contracts_found.json", 'w') as f:
                json.dump(self.results["china_contracts"], f, indent=2)

        # Save summary
        summary = {
            "processing_date": datetime.now().isoformat(),
            "archives_processed": self.results["archives_processed"],
            "xml_files_processed": self.results["xml_files_processed"],
            "china_contracts_found": len(self.results["china_contracts"]),
            "chinese_entities_detected": list(set(
                entity for contract in self.results["china_contracts"]
                for entity in contract.get("chinese_entities", [])
            )),
            "format_breakdown": {
                "nested": sum(1 for f in self.results["format_detection"].values() if f == "nested"),
                "direct": sum(1 for f in self.results["format_detection"].values() if f == "direct"),
                "unknown": sum(1 for f in self.results["format_detection"].values() if f == "unknown"),
                "error": sum(1 for f in self.results["format_detection"].values() if f == "error")
            }
        }

        with open(self.output_dir / "summary.json", 'w') as f:
            json.dump(summary, f, indent=2)

        logging.info(f"\\nResults saved to {self.output_dir}")


def main():
    """Process TED 2016-2022 with flexible format handling"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    processor = FlexibleTEDProcessor()

    # Years to process
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022]

    logging.info("="*70)
    logging.info("TED FLEXIBLE FORMAT PROCESSOR")
    logging.info("Processing 2016-2022 with both nested and direct XML support")
    logging.info("="*70)

    ted_path = Path("F:/TED_Data/monthly")

    for year in years:
        year_path = ted_path / str(year)
        if not year_path.exists():
            logging.warning(f"Year {year} directory not found")
            continue

        archives = sorted(year_path.glob("*.tar.gz"))
        logging.info(f"\\nProcessing {year}: {len(archives)} archives")

        for archive in archives:
            processor.process_archive(archive)

            # Save intermediate results every 10 archives
            if processor.results["archives_processed"] % 10 == 0:
                processor.save_results()

    # Save final results
    processor.save_results()

    # Print summary
    logging.info("\\n" + "="*70)
    logging.info("PROCESSING COMPLETE")
    logging.info("="*70)
    logging.info(f"Total archives processed: {processor.results['archives_processed']}")
    logging.info(f"Total XML files processed: {processor.results['xml_files_processed']:,}")
    logging.info(f"Total Chinese contracts found: {len(processor.results['china_contracts'])}")

    if processor.results["china_contracts"]:
        logging.info("\\n*** CHINESE CONTRACTS DETECTED! ***")
        entities = set()
        countries = set()
        for contract in processor.results["china_contracts"]:
            entities.update(contract.get("chinese_entities", []))
            countries.add(contract.get("authority_country", "unknown"))

        logging.info(f"Unique Chinese entities: {', '.join(sorted(entities))}")
        logging.info(f"EU countries involved: {', '.join(sorted(countries))}")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
TED Multi-Year Processor for China Analysis
Processes multiple years of TED data to find Chinese involvement trends
"""

import tarfile
import gzip
import xml.etree.ElementTree as ET
import sqlite3
import json
import logging
from pathlib import Path
from datetime import datetime
import sys
sys.path.append('C:/Projects/OSINT - Foresight/scripts')
from refined_chinese_detector import RefinedChineseDetector

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TEDMultiYearProcessor:
    """Process multiple years of TED data for Chinese involvement"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.detector = RefinedChineseDetector()
        self.stats = {
            'years_processed': [],
            'total_contracts': 0,
            'chinese_contracts': 0,
            'by_year': {},
            'by_country': {},
            'chinese_companies': {},
            'processing_errors': []
        }

    def process_year(self, year: int, months: list = None):
        """Process specific months of a year"""

        if months is None:
            months = range(1, 13)  # All months

        logger.info(f"Processing year {year}, months {list(months)}")

        year_stats = {
            'total_contracts': 0,
            'chinese_contracts': 0,
            'chinese_companies': []
        }

        for month in months:
            month_file = f"F:/TED_Data/monthly/{year}/TED_monthly_{year}_{month:02d}.tar.gz"

            if not Path(month_file).exists():
                logger.warning(f"File not found: {month_file}")
                continue

            try:
                self.process_month_file(month_file, year, month, year_stats)
            except Exception as e:
                logger.error(f"Error processing {month_file}: {e}")
                self.stats['processing_errors'].append({
                    'file': month_file,
                    'error': str(e)
                })

        self.stats['by_year'][str(year)] = year_stats
        self.stats['years_processed'].append(year)
        self.stats['total_contracts'] += year_stats['total_contracts']
        self.stats['chinese_contracts'] += year_stats['chinese_contracts']

        logger.info(f"Year {year} complete: {year_stats['total_contracts']} contracts, "
                   f"{year_stats['chinese_contracts']} Chinese")

    def process_month_file(self, tar_path: str, year: int, month: int, year_stats: dict):
        """Process a single month's tar file"""

        logger.info(f"Processing {year}-{month:02d}...")

        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        contracts_processed = 0
        chinese_found = 0

        try:
            with tarfile.open(tar_path, 'r:gz') as monthly_tar:
                # Get daily tar files
                daily_files = [f for f in monthly_tar.getnames() if f.endswith('.tar.gz')]

                for daily_file in daily_files[:3]:  # Process first 3 days per month for speed
                    try:
                        daily_tar_obj = monthly_tar.extractfile(daily_file)
                        if daily_tar_obj:
                            contracts, chinese = self.process_daily_tar(
                                daily_tar_obj, year, month, cur
                            )
                            contracts_processed += contracts
                            chinese_found += chinese
                    except Exception as e:
                        logger.warning(f"Error processing daily tar {daily_file}: {e}")

        except Exception as e:
            logger.error(f"Error opening monthly tar {tar_path}: {e}")

        conn.commit()
        conn.close()

        year_stats['total_contracts'] += contracts_processed
        year_stats['chinese_contracts'] += chinese_found

        logger.info(f"  {year}-{month:02d}: {contracts_processed} contracts, {chinese_found} Chinese")

    def process_daily_tar(self, daily_tar_obj, year: int, month: int, cursor):
        """Process a daily tar file"""

        contracts_processed = 0
        chinese_found = 0

        try:
            with tarfile.open(fileobj=daily_tar_obj, mode='r:gz') as daily_tar:
                xml_files = [f for f in daily_tar.getnames() if f.endswith('.xml')]

                for xml_file in xml_files[:50]:  # Process first 50 XMLs per day
                    try:
                        xml_obj = daily_tar.extractfile(xml_file)
                        if xml_obj:
                            is_chinese = self.process_xml_contract(xml_obj, year, month, cursor)
                            contracts_processed += 1
                            if is_chinese:
                                chinese_found += 1
                    except Exception as e:
                        pass  # Skip individual XML errors

        except Exception as e:
            logger.warning(f"Error processing daily tar: {e}")

        return contracts_processed, chinese_found

    def process_xml_contract(self, xml_obj, year: int, month: int, cursor):
        """Process a single XML contract and check for Chinese involvement"""

        try:
            tree = ET.parse(xml_obj)
            root = tree.getroot()

            # Define namespaces
            ns = {
                'ted': 'http://publications.europa.eu/TED_schema',
                'nuts': 'http://publications.europa.eu/NUTS_schema'
            }

            # Extract key fields
            contractor_name = None
            contractor_country = None
            contracting_authority = None
            contract_title = None
            cpv_code = None
            contract_value = None

            # Try different paths for contractor info
            contractor_elem = root.find('.//ted:CONTRACTOR', ns)
            if contractor_elem is not None:
                name_elem = contractor_elem.find('.//ted:OFFICIALNAME', ns)
                if name_elem is not None and name_elem.text:
                    contractor_name = name_elem.text

                country_elem = contractor_elem.find('.//ted:COUNTRY', ns)
                if country_elem is not None and country_elem.text:
                    contractor_country = country_elem.text

            # Get contracting authority
            auth_elem = root.find('.//ted:CONTRACTING_BODY/ted:OFFICIALNAME', ns)
            if auth_elem is not None and auth_elem.text:
                contracting_authority = auth_elem.text

            # Get contract title
            title_elem = root.find('.//ted:OBJECT_CONTRACT/ted:TITLE', ns)
            if title_elem is not None and title_elem.text:
                contract_title = title_elem.text

            # Get CPV code
            cpv_elem = root.find('.//ted:CPV_MAIN/ted:CPV_CODE', ns)
            if cpv_elem is not None:
                cpv_code = cpv_elem.get('CODE')

            # Get contract value
            value_elem = root.find('.//ted:VAL_TOTAL', ns)
            if value_elem is not None and value_elem.text:
                contract_value = value_elem.text

            # Check if contractor is Chinese
            is_chinese = False
            confidence = 0.0
            detection_method = "none"

            if contractor_name or contractor_country:
                result = self.detector.detect_chinese_entity(
                    contractor_name or "",
                    contractor_country or "",
                    contracting_authority or "",
                    contract_title or ""
                )

                is_chinese = result.is_chinese
                confidence = result.confidence
                detection_method = result.method

                if is_chinese:
                    # Store in database
                    cursor.execute('''
                        INSERT INTO ted_china_contracts (
                            publication_date, country, contractor_name,
                            contractor_country, contracting_authority,
                            contract_title, cpv_codes, contract_value_eur,
                            refined_china_linked, refined_china_confidence,
                            refined_detection_method
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        f"{year}{month:02d}01",  # Approximate date
                        contractor_country,
                        contractor_name,
                        contractor_country,
                        contracting_authority,
                        contract_title,
                        cpv_code,
                        contract_value,
                        1,
                        confidence,
                        detection_method
                    ))

                    # Track the company
                    if contractor_name:
                        if contractor_name not in self.stats['chinese_companies']:
                            self.stats['chinese_companies'][contractor_name] = {
                                'country': contractor_country,
                                'contracts': 0,
                                'first_seen': f"{year}-{month:02d}",
                                'confidence': confidence
                            }
                        self.stats['chinese_companies'][contractor_name]['contracts'] += 1

            return is_chinese

        except Exception as e:
            return False

    def generate_temporal_report(self):
        """Generate report on Chinese involvement over time"""

        print("\n" + "="*80)
        print("TED MULTI-YEAR CHINESE INVOLVEMENT ANALYSIS")
        print("="*80)

        print(f"\nYears Processed: {sorted(self.stats['years_processed'])}")
        print(f"Total Contracts Analyzed: {self.stats['total_contracts']:,}")
        print(f"Chinese Contracts Found: {self.stats['chinese_contracts']}")

        if self.stats['total_contracts'] > 0:
            rate = (self.stats['chinese_contracts'] / self.stats['total_contracts']) * 100
            print(f"Overall Chinese Penetration: {rate:.4f}%")

        # Year by year breakdown
        print("\n" + "="*50)
        print("YEAR-BY-YEAR ANALYSIS")
        print("="*50)

        for year in sorted(self.stats['by_year'].keys()):
            data = self.stats['by_year'][year]
            if data['total_contracts'] > 0:
                rate = (data['chinese_contracts'] / data['total_contracts']) * 100
                print(f"\n{year}:")
                print(f"  Contracts: {data['total_contracts']:,}")
                print(f"  Chinese: {data['chinese_contracts']}")
                print(f"  Rate: {rate:.4f}%")

        # Top Chinese companies
        if self.stats['chinese_companies']:
            print("\n" + "="*50)
            print("CHINESE COMPANIES IDENTIFIED")
            print("="*50)

            sorted_companies = sorted(
                self.stats['chinese_companies'].items(),
                key=lambda x: x[1]['contracts'],
                reverse=True
            )[:10]

            for name, data in sorted_companies:
                print(f"\n{name[:80]}:")
                print(f"  Country: {data['country']}")
                print(f"  Contracts: {data['contracts']}")
                print(f"  First Seen: {data['first_seen']}")
                print(f"  Confidence: {data['confidence']:.2%}")

        # Save detailed report
        report_path = Path("C:/Projects/OSINT - Foresight/analysis/ted_temporal_china_analysis.json")
        with open(report_path, 'w') as f:
            json.dump(self.stats, f, indent=2)

        print(f"\n\nDetailed report saved to: {report_path}")

        return self.stats


def main():
    """Main execution"""
    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"

    processor = TEDMultiYearProcessor(db_path)

    # Process recent years (sample months for speed)
    years_to_process = [
        (2023, [1, 6, 12]),  # Jan, Jun, Dec 2023
        (2022, [1, 6, 12]),  # Jan, Jun, Dec 2022
        (2021, [1, 6, 12]),  # Jan, Jun, Dec 2021
    ]

    for year, months in years_to_process:
        processor.process_year(year, months)

    # Generate report
    processor.generate_temporal_report()

    return processor.stats


if __name__ == "__main__":
    main()

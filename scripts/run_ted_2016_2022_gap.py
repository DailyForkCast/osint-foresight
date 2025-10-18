#!/usr/bin/env python3
"""
TED 2016-2022 Gap Processing
Fill the critical gap in our temporal analysis
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.process_ted_procurement_multicountry import MultiCountryTEDProcessor
import logging
from pathlib import Path
import json
from datetime import datetime

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('ted_2016_2022_gap.log'),
            logging.StreamHandler()
        ]
    )

def main():
    """Process the critical 2016-2022 gap period"""
    setup_logging()

    logging.info("=" * 70)
    logging.info("TED 2016-2022 GAP PROCESSING")
    logging.info("Filling the critical timeline gap")
    logging.info("=" * 70)

    # Output directory
    output_dir = Path("data/processed/ted_2016_2022_gap")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize analyzer
    analyzer = MultiCountryTEDProcessor(output_dir)

    # Process each year individually for better tracking
    years_to_process = [2016, 2017, 2018, 2019, 2020, 2021, 2022]

    for year in years_to_process:
        logging.info(f"\\n{'='*50}")
        logging.info(f"PROCESSING YEAR: {year}")
        logging.info(f"{'='*50}")

        year_start = datetime.now()

        # Find archives for this year
        ted_data_path = Path("F:/TED_Data/monthly")
        year_archives = list((ted_data_path / str(year)).glob("*.tar.gz"))
        year_archives.sort()

        logging.info(f"Found {len(year_archives)} archives for {year}")

        year_findings = 0
        year_xml_count = 0

        for i, archive_path in enumerate(year_archives, 1):
            logging.info(f"[{year}] Processing {i}/{len(year_archives)}: {archive_path.name}")

            try:
                # Process single archive
                findings = analyzer.process_archive(archive_path)

                xml_count = findings.get('xml_files_processed', 0)
                contracts_found = len(findings.get('china_contracts', []))

                year_findings += contracts_found
                year_xml_count += xml_count

                logging.info(f"Archive {archive_path.name}: {contracts_found} contracts from {xml_count} XML files")

                if contracts_found > 0:
                    logging.info(f"*** CONTRACTS FOUND IN {year}! ***")
                    for contract in findings.get('china_contracts', []):
                        logging.info(f"  - {contract.get('chinese_entity', 'unknown')}: {contract.get('contract_id', 'no-id')}")

            except Exception as e:
                logging.error(f"Error processing {archive_path.name}: {e}")
                continue

        year_duration = datetime.now() - year_start
        logging.info(f"\\n{year} COMPLETE:")
        logging.info(f"  - Total contracts found: {year_findings}")
        logging.info(f"  - Total XML files processed: {year_xml_count:,}")
        logging.info(f"  - Processing time: {year_duration}")

        # Save year summary
        year_summary = {
            "year": year,
            "contracts_found": year_findings,
            "xml_files_processed": year_xml_count,
            "archives_processed": len(year_archives),
            "processing_time_seconds": year_duration.total_seconds(),
            "completion_date": datetime.now().isoformat()
        }

        with open(output_dir / f"year_{year}_summary.json", 'w') as f:
            json.dump(year_summary, f, indent=2)

    # Generate comprehensive timeline
    logging.info("\\n" + "="*70)
    logging.info("GENERATING COMPREHENSIVE TIMELINE")
    logging.info("="*70)

    timeline = {}
    total_contracts = 0
    total_xml = 0

    for year in years_to_process:
        summary_file = output_dir / f"year_{year}_summary.json"
        if summary_file.exists():
            with open(summary_file, 'r') as f:
                year_data = json.load(f)
                timeline[year] = year_data
                total_contracts += year_data['contracts_found']
                total_xml += year_data['xml_files_processed']

    # Create master timeline
    master_timeline = {
        "processing_completed": datetime.now().isoformat(),
        "period_analyzed": "2016-2022",
        "total_contracts_found": total_contracts,
        "total_xml_files_processed": total_xml,
        "yearly_breakdown": timeline,
        "strategic_periods": {
            "2016": "BRI Implementation Phase",
            "2017-2019": "Peak Expansion Period",
            "2020-2021": "COVID Impact Period",
            "2022": "Pre-Current State"
        }
    }

    with open(output_dir / "master_timeline_2016_2022.json", 'w') as f:
        json.dump(master_timeline, f, indent=2)

    logging.info(f"PROCESSING COMPLETE!")
    logging.info(f"Total contracts found (2016-2022): {total_contracts}")
    logging.info(f"Total XML files processed: {total_xml:,}")
    logging.info(f"Results saved to: {output_dir}")

    # Generate findings summary
    if total_contracts > 0:
        logging.info("\\n*** CHINESE CONTRACTS DETECTED IN 2016-2022 PERIOD! ***")
        for year, data in timeline.items():
            if data['contracts_found'] > 0:
                logging.info(f"  {year}: {data['contracts_found']} contracts")
    else:
        logging.info("\\nNo Chinese contracts found in 2016-2022 period")
        logging.info("This confirms gradual transition from zero (2014-2015) to significant presence (2023-2025)")

if __name__ == "__main__":
    main()

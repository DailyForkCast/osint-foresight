#!/usr/bin/env python3
"""
Continue TED processing from 2018_04 onwards
Picks up where we left off after processing 2016-2018_03
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.process_ted_flexible_format import FlexibleTEDProcessor
import logging
from pathlib import Path
import json

def main():
    """Continue processing from 2018_04"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    processor = FlexibleTEDProcessor()

    # Load existing results
    results_file = Path("data/processed/ted_flexible_2016_2022/results.json")
    if results_file.exists():
        with open(results_file, 'r') as f:
            existing = json.load(f)
            processor.results = existing
            # Ensure processed_archives exists
            if "processed_archives" not in processor.results:
                processor.results["processed_archives"] = set()
            else:
                processor.results["processed_archives"] = set(processor.results["processed_archives"])
            logging.info(f"Loaded {len(existing['china_contracts'])} existing contracts")
            logging.info(f"Already processed {existing['archives_processed']} archives")

    # Start from May 2018 (April already processed)
    ted_path = Path("F:/TED_Data/monthly")

    # Process 2018 remaining months (May-December)
    logging.info("\n" + "="*70)
    logging.info("CONTINUING FROM 2018 MAY")
    logging.info("="*70)

    year = 2018
    start_month = 5  # Start from May (April completed)

    for month in range(start_month, 13):  # April to December
        month_pattern = f"TED_monthly_{year}_{month:02d}.tar.gz"
        archives = list(ted_path.glob(f"{year}/*{month:02d}.tar.gz"))

        for archive in archives:
            if archive.name == month_pattern:
                logging.info(f"\nProcessing {year} month {month:02d}")
                processor.process_archive(archive)
                processor.save_results()
                break

    # Process 2019-2022
    for year in [2019, 2020, 2021, 2022]:
        year_path = ted_path / str(year)
        if not year_path.exists():
            logging.warning(f"Year {year} directory not found")
            continue

        archives = sorted(year_path.glob("*.tar.gz"))
        logging.info(f"\nProcessing {year}: {len(archives)} archives")

        for archive in archives:
            processor.process_archive(archive)

            # Save after every archive
            processor.save_results()

    # Final save
    processor.save_results()

    logging.info("\n" + "="*70)
    logging.info("PROCESSING COMPLETE")
    logging.info("="*70)
    logging.info(f"Total archives processed: {processor.results['archives_processed']}")
    logging.info(f"Total XML files processed: {processor.results['xml_files_processed']:,}")
    logging.info(f"Total Chinese contracts found: {len(processor.results['china_contracts'])}")

if __name__ == "__main__":
    main()

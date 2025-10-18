#!/usr/bin/env python3
"""
Process TED data for 2023-2025 period
"""

import sys
import logging
from pathlib import Path

# Add scripts directory to path
sys.path.append(str(Path(__file__).parent))

from process_ted_procurement_multicountry import MultiCountryTEDProcessor

def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('ted_2023_2025_processing.log'),
            logging.StreamHandler()
        ]
    )

    # Create processor for 2023-2025 data
    processor = MultiCountryTEDProcessor(
        data_dir="F:/TED_Data",
        output_dir="data/processed/ted_2023_2025"
    )

    # Filter to only process 2023-2025 archives
    logging.info("Starting TED 2023-2025 Processing...")

    monthly_dir = Path("F:/TED_Data/monthly")
    recent_archives = []

    for year in ["2023", "2024", "2025"]:
        year_dir = monthly_dir / year
        if year_dir.exists():
            for archive in sorted(year_dir.glob("TED_monthly_*.tar.gz")):
                recent_archives.append(archive)

    logging.info(f"Found {len(recent_archives)} archives for 2023-2025")

    # Process each archive
    for i, archive_path in enumerate(recent_archives):
        logging.info(f"Processing {i+1}/{len(recent_archives)}: {archive_path.name}")

        try:
            results = processor.process_archive(archive_path)

            # Save checkpoint
            processor.checkpoint["processed_files"].append(str(archive_path))
            processor.checkpoint["last_file"] = str(archive_path)

            # Collect findings
            for country, findings in results["findings_by_country"].items():
                processor.checkpoint["country_findings"][country].extend([finding.__dict__ for finding in findings])

            processor.save_checkpoint()
            logging.info(f"  --> Completed: {results['total_findings']} China-related contracts found")

        except Exception as e:
            logging.error(f"Error processing {archive_path}: {e}")
            continue

    # Generate outputs
    processor.save_findings_by_country()
    processor.save_findings_by_company()
    processor.save_findings_by_sector()

    logging.info("TED 2023-2025 Processing Complete!")
    logging.info(f"Results saved to: data/processed/ted_2023_2025")

if __name__ == "__main__":
    main()

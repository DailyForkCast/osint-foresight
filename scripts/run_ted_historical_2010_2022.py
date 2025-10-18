#!/usr/bin/env python3
"""
Process TED historical data for 2010-2022 period
This captures the full China entry and expansion timeline
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
            logging.FileHandler('ted_historical_2010_2022_processing.log'),
            logging.StreamHandler()
        ]
    )

    # Create processor for historical data
    processor = MultiCountryTEDProcessor(
        data_dir="F:/TED_Data",
        output_dir="data/processed/ted_historical_2010_2022"
    )

    # Process historical periods as documented in TED_TEMPORAL_ANALYSIS_STRATEGY.md
    periods = {
        "baseline_2010_2012": ["2010", "2011", "2012"],      # Pre-BRI baseline
        "bri_launch_2013_2016": ["2013", "2014", "2015", "2016"],  # Belt & Road launch
        "expansion_2017_2019": ["2017", "2018", "2019"],      # Peak expansion
        "covid_2020_2022": ["2020", "2021", "2022"]           # COVID & awareness period
    }

    logging.info("Starting TED Historical 2010-2022 Processing...")
    logging.info("Processing periods: Pre-BRI → BRI Launch → Expansion → COVID")

    monthly_dir = Path("F:/TED_Data/monthly")

    for period_name, years in periods.items():
        logging.info(f"\n{'='*50}")
        logging.info(f"PROCESSING PERIOD: {period_name}")
        logging.info(f"Years: {', '.join(years)}")
        logging.info(f"{'='*50}")

        period_archives = []
        for year in years:
            year_dir = monthly_dir / year
            if year_dir.exists():
                for archive in sorted(year_dir.glob("TED_monthly_*.tar.gz")):
                    period_archives.append(archive)

        logging.info(f"Found {len(period_archives)} archives for {period_name}")

        # Process period archives
        period_findings = 0
        for i, archive_path in enumerate(period_archives):
            logging.info(f"[{period_name}] Processing {i+1}/{len(period_archives)}: {archive_path.name}")

            try:
                results = processor.process_archive(archive_path)

                # Save checkpoint
                processor.checkpoint["processed_files"].append(str(archive_path))
                processor.checkpoint["last_file"] = str(archive_path)

                # Collect findings
                archive_findings = 0
                for country, findings in results["findings_by_country"].items():
                    processor.checkpoint["country_findings"][country].extend([finding.__dict__ for finding in findings])
                    archive_findings += len(findings)

                period_findings += archive_findings
                processor.save_checkpoint()

                logging.info(f"  --> Completed: {archive_findings} China-related contracts found")

            except Exception as e:
                logging.error(f"Error processing {archive_path}: {e}")
                continue

        logging.info(f"Period {period_name} complete: {period_findings} total findings")

    # Generate outputs
    logging.info("\nGenerating historical analysis outputs...")
    processor.save_findings_by_country()
    processor.save_findings_by_company()
    processor.save_findings_by_sector()

    # Generate temporal analysis
    generate_temporal_analysis(processor)

    logging.info("TED Historical 2010-2022 Processing Complete!")
    logging.info(f"Results saved to: data/processed/ted_historical_2010_2022")

def generate_temporal_analysis(processor):
    """Generate temporal pattern analysis"""
    import json
    from collections import defaultdict

    # Analyze progression patterns
    temporal_analysis = {
        "periods": {
            "baseline_2010_2012": {"description": "Pre-BRI baseline", "contracts": 0, "entities": set()},
            "bri_launch_2013_2016": {"description": "Belt & Road Initiative launch", "contracts": 0, "entities": set()},
            "expansion_2017_2019": {"description": "Peak expansion period", "contracts": 0, "entities": set()},
            "covid_2020_2022": {"description": "COVID & security awareness", "contracts": 0, "entities": set()}
        },
        "entity_timeline": defaultdict(lambda: {"first_appearance": None, "peak_year": None, "contracts_by_year": defaultdict(int)}),
        "country_timeline": defaultdict(lambda: {"first_china_contract": None, "peak_year": None, "contracts_by_year": defaultdict(int)})
    }

    # Analyze findings by time periods
    for country, findings_dicts in processor.checkpoint["country_findings"].items():
        for finding in findings_dicts:
            year = finding.get("date", "")[:4] if finding.get("date") else ""
            entity = finding.get("chinese_entity", "")

            # Skip if no year or entity
            if not year or not entity:
                continue

            # Determine period
            period = None
            if year in ["2010", "2011", "2012"]:
                period = "baseline_2010_2012"
            elif year in ["2013", "2014", "2015", "2016"]:
                period = "bri_launch_2013_2016"
            elif year in ["2017", "2018", "2019"]:
                period = "expansion_2017_2019"
            elif year in ["2020", "2021", "2022"]:
                period = "covid_2020_2022"

            if period:
                temporal_analysis["periods"][period]["contracts"] += 1
                temporal_analysis["periods"][period]["entities"].add(entity)

            # Track entity timeline
            entity_data = temporal_analysis["entity_timeline"][entity]
            if entity_data["first_appearance"] is None or year < entity_data["first_appearance"]:
                entity_data["first_appearance"] = year
            entity_data["contracts_by_year"][year] += 1

            # Track country timeline
            country_data = temporal_analysis["country_timeline"][country]
            if country_data["first_china_contract"] is None or year < country_data["first_china_contract"]:
                country_data["first_china_contract"] = year
            country_data["contracts_by_year"][year] += 1

    # Convert sets to lists for JSON serialization
    for period_data in temporal_analysis["periods"].values():
        period_data["entities"] = list(period_data["entities"])

    # Save temporal analysis
    temporal_dir = Path("data/processed/ted_historical_2010_2022/temporal")
    temporal_dir.mkdir(exist_ok=True)

    with open(temporal_dir / "temporal_analysis.json", 'w') as f:
        json.dump(temporal_analysis, f, indent=2, default=str)

    logging.info("Temporal analysis saved to temporal/temporal_analysis.json")

if __name__ == "__main__":
    main()

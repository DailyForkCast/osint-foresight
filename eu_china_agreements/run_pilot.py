#!/usr/bin/env python3
"""
EU-China Agreements Pilot Runner
Execute the pilot harvest for 5 EU countries
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime

# Add scripts directory to path
sys.path.append(str(Path(__file__).parent / 'scripts'))

from eu_china_agreements_harvester import EUChinaAgreementsHarvester
from web_scraper import OfficialSiteSearcher

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'pilot_run_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_pilot():
    """Run the complete pilot harvest"""
    logger.info("=" * 60)
    logger.info("EU-China Agreements Harvester - Pilot Run")
    logger.info("=" * 60)

    # Setup paths
    base_dir = Path(__file__).parent
    config_path = base_dir / 'config' / 'countries.json'
    output_dir = base_dir / 'out'

    # Countries to process
    countries = ['IT']  # Start with Italy, then expand to ['IT', 'DE', 'FR', 'PL', 'ES']

    # Phase 1: Web scraping
    logger.info("\nPhase 1: Web Scraping and Data Collection")
    logger.info("-" * 40)

    searcher = OfficialSiteSearcher(str(config_path))
    scraped_data = {}

    try:
        for country in countries:
            logger.info(f"\nScraping data for {country}...")
            results = searcher.collect_agreements(country, output_dir / 'scraped')
            scraped_data[country] = results
            logger.info(f"Collected {results['total_results']} results for {country}")

    except Exception as e:
        logger.error(f"Error in web scraping phase: {e}")
    finally:
        searcher.close()

    # Phase 2: Processing and extraction
    logger.info("\nPhase 2: Processing and Extraction")
    logger.info("-" * 40)

    harvester = EUChinaAgreementsHarvester(str(config_path), str(output_dir))
    processed_agreements = {}

    for country in countries:
        logger.info(f"\nProcessing agreements for {country}...")
        try:
            # Process scraped files
            scraped_dir = output_dir / 'scraped' / country / 'raw'
            if scraped_dir.exists():
                agreements = []
                for html_file in scraped_dir.glob('*.html'):
                    logger.info(f"Processing {html_file.name}")
                    with open(html_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Extract agreement
                    agreement = harvester.extractor.extract_from_html(
                        content, str(html_file), country
                    )
                    if agreement:
                        agreements.append(agreement)

                processed_agreements[country] = agreements
                logger.info(f"Extracted {len(agreements)} agreements for {country}")
            else:
                logger.warning(f"No scraped data found for {country}")

        except Exception as e:
            logger.error(f"Error processing {country}: {e}")

    # Phase 3: Deduplication and validation
    logger.info("\nPhase 3: Deduplication and Validation")
    logger.info("-" * 40)

    final_agreements = {}
    for country, agreements in processed_agreements.items():
        if agreements:
            # Deduplicate
            clusters = harvester.deduplicator.find_duplicates(agreements)
            logger.info(f"Found {len(clusters)} duplicate clusters for {country}")

            # Merge duplicates
            for cluster in clusters:
                merged = harvester.deduplicator.merge_agreements(cluster)
                for agreement in cluster:
                    if agreement in agreements:
                        agreements.remove(agreement)
                agreements.append(merged)

            # Validate
            valid_count = 0
            for agreement in agreements:
                is_valid, issues = harvester.validator.validate(agreement)
                if is_valid:
                    valid_count += 1
                else:
                    logger.debug(f"Validation issues: {issues}")

            logger.info(f"{valid_count}/{len(agreements)} agreements passed validation for {country}")
            final_agreements[country] = agreements

    # Phase 4: Output generation
    logger.info("\nPhase 4: Output Generation")
    logger.info("-" * 40)

    for country, agreements in final_agreements.items():
        # Save agreements
        country_dir = output_dir / 'agreements' / country
        country_dir.mkdir(parents=True, exist_ok=True)

        output_file = country_dir / 'agreements.ndjson'
        with open(output_file, 'w', encoding='utf-8') as f:
            for agreement in agreements:
                json.dump(agreement.to_dict(), f, ensure_ascii=False)
                f.write('\n')
        logger.info(f"Saved {len(agreements)} agreements to {output_file}")

        # Generate report
        qa_report = harvester.validator.generate_qa_report(agreements)
        report_file = output_dir / 'logs' / f'{country}_coverage.json'
        report_file.parent.mkdir(exist_ok=True)

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(qa_report, f, indent=2, ensure_ascii=False)
        logger.info(f"Generated QA report: {report_file}")

    # Phase 5: Final summary
    logger.info("\nPhase 5: Final Summary")
    logger.info("-" * 40)

    summary = {
        'timestamp': datetime.now().isoformat(),
        'countries_processed': countries,
        'results': {}
    }

    for country in countries:
        scraped = scraped_data.get(country, {})
        agreements = final_agreements.get(country, [])

        summary['results'][country] = {
            'scraped_results': scraped.get('total_results', 0),
            'saved_files': scraped.get('saved_files', 0),
            'extracted_agreements': len(agreements),
            'types': {},
            'statuses': {},
            'jurisdictions': {}
        }

        # Aggregate statistics
        for agreement in agreements:
            # Type distribution
            ag_type = agreement.type
            summary['results'][country]['types'][ag_type] = \
                summary['results'][country]['types'].get(ag_type, 0) + 1

            # Status distribution
            status = agreement.status
            summary['results'][country]['statuses'][status] = \
                summary['results'][country]['statuses'].get(status, 0) + 1

            # Jurisdiction distribution
            jurisdiction = agreement.jurisdiction_level
            summary['results'][country]['jurisdictions'][jurisdiction] = \
                summary['results'][country]['jurisdictions'].get(jurisdiction, 0) + 1

    # Save summary
    summary_file = output_dir / 'pilot_summary.json'
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    logger.info(f"\nPilot Summary saved to: {summary_file}")
    logger.info("\n" + "=" * 60)
    logger.info("Pilot Run Complete!")
    logger.info("=" * 60)

    # Print summary
    print("\nPILOT RUN SUMMARY")
    print("=" * 60)
    for country, data in summary['results'].items():
        print(f"\n{country}:")
        print(f"  - Scraped results: {data['scraped_results']}")
        print(f"  - Saved files: {data['saved_files']}")
        print(f"  - Extracted agreements: {data['extracted_agreements']}")
        if data['types']:
            print(f"  - Types: {data['types']}")
        if data['statuses']:
            print(f"  - Statuses: {data['statuses']}")
        if data['jurisdictions']:
            print(f"  - Jurisdictions: {data['jurisdictions']}")

    return summary

if __name__ == "__main__":
    try:
        summary = run_pilot()
    except KeyboardInterrupt:
        logger.info("\nPilot run interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
    finally:
        logger.info("Pilot run ended")

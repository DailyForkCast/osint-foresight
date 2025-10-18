#!/usr/bin/env python3
"""
Italy-China Agreements Harvester
Uses Edge/Firefox for actual data collection
"""

import json
import time
import logging
from pathlib import Path
from datetime import datetime
import sys

# Add scripts to path
sys.path.append(str(Path(__file__).parent / 'scripts'))

from multi_browser_scraper import MultiBrowserScraper
from eu_china_agreements_harvester import AgreementExtractor, DeduplicationEngine, ValidationEngine

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def harvest_italy_china_agreements():
    """Harvest Italy-China agreements using browser automation"""

    logger.info("="*60)
    logger.info("Italy-China Agreements Harvester")
    logger.info("="*60)

    # Initialize components
    base_dir = Path(__file__).parent
    config_path = base_dir / 'config' / 'countries.json'
    output_dir = base_dir / 'out'

    # Create output directories
    italy_dir = output_dir / 'agreements' / 'IT'
    raw_dir = italy_dir / 'raw'
    raw_dir.mkdir(parents=True, exist_ok=True)

    # Initialize scraper with Edge (works on Windows)
    scraper = MultiBrowserScraper(browser='edge', headless=True)

    # Initialize processors
    extractor = AgreementExtractor(str(config_path))
    deduplicator = DeduplicationEngine()
    validator = ValidationEngine()

    all_results = []
    agreements = []

    try:
        # Define search queries for Italy
        search_queries = [
            # Official Italian government sites
            'site:esteri.it accordo Cina 2020..2025',
            'site:esteri.it memorandum Cina',
            'site:esteri.it intesa Cina',
            'site:governo.it cooperazione Cina',
            'site:governo.it accordo Cina',

            # Specific agreements
            '"Belt and Road" site:governo.it',
            '"Via della Seta" site:esteri.it',
            'memorandum understanding China site:esteri.it',

            # Municipal agreements
            'site:comune.roma.it Cina',
            'site:comune.milano.it Cina',
            'gemellaggio Cina site:.it',

            # University agreements
            'site:unive.it Cina accordo',
            'site:unimi.it China cooperation',
            'site:polimi.it Cina memorandum',

            # Chinese side
            'Italy agreement site:fmprc.gov.cn',
            '意大利 协议 site:fmprc.gov.cn',
            'Italia cooperazione site:it.china-embassy.gov.cn'
        ]

        logger.info(f"Executing {len(search_queries)} search queries...")

        # Execute searches using Bing (more tolerant of automation)
        for i, query in enumerate(search_queries, 1):
            logger.info(f"Query {i}/{len(search_queries)}: {query}")

            # Search with Bing
            results = scraper.search_with_browser(query, search_engine='bing')

            if results:
                logger.info(f"  Found {len(results)} results")
                all_results.extend(results)

                # Save top results
                for result in results[:3]:  # Top 3 per query
                    url = result['url']
                    logger.info(f"  Fetching: {url}")

                    # Fetch page content
                    content = scraper.fetch_page(url)
                    if content:
                        # Save raw HTML
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = raw_dir / f"italy_{timestamp}_{hash(url)}.html"

                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write(content)

                        # Extract agreement data
                        agreement = extractor.extract_from_html(content, url, 'IT')
                        if agreement:
                            agreements.append(agreement)
                            logger.info(f"    Extracted agreement: {agreement.title_native[:50]}...")

            # Rate limiting
            time.sleep(2)

        logger.info(f"\nTotal search results collected: {len(all_results)}")
        logger.info(f"Agreements extracted: {len(agreements)}")

        # Save all search results
        results_file = italy_dir / 'search_results.json'
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'total_results': len(all_results),
                'results': all_results
            }, f, indent=2, ensure_ascii=False)

        # Deduplicate agreements
        if agreements:
            logger.info("\nDeduplicating agreements...")
            clusters = deduplicator.find_duplicates(agreements)
            logger.info(f"Found {len(clusters)} duplicate clusters")

            for cluster in clusters:
                merged = deduplicator.merge_agreements(cluster)
                for agreement in cluster:
                    if agreement in agreements:
                        agreements.remove(agreement)
                agreements.append(merged)

            # Validate agreements
            logger.info("\nValidating agreements...")
            valid_count = 0
            for agreement in agreements:
                is_valid, issues = validator.validate(agreement)
                if is_valid:
                    valid_count += 1
                elif issues:
                    logger.debug(f"Validation issues for {agreement.title_native}: {issues}")

            logger.info(f"{valid_count}/{len(agreements)} agreements passed validation")

            # Save agreements
            agreements_file = italy_dir / 'agreements.ndjson'
            with open(agreements_file, 'w', encoding='utf-8') as f:
                for agreement in agreements:
                    json.dump(agreement.to_dict(), f, ensure_ascii=False)
                    f.write('\n')

            logger.info(f"\nSaved {len(agreements)} agreements to {agreements_file}")

            # Generate QA report
            qa_report = validator.generate_qa_report(agreements)
            report_file = output_dir / 'logs' / 'IT_coverage.json'
            report_file.parent.mkdir(exist_ok=True)

            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(qa_report, f, indent=2, ensure_ascii=False)

            logger.info(f"Generated QA report: {report_file}")

            # Print summary
            print("\n" + "="*60)
            print("HARVEST SUMMARY")
            print("="*60)
            print(f"Total search results: {len(all_results)}")
            print(f"Agreements extracted: {len(agreements)}")
            print(f"Valid agreements: {valid_count}")

            if qa_report.get('type_distribution'):
                print("\nAgreement Types:")
                for ag_type, count in qa_report['type_distribution'].items():
                    print(f"  {ag_type}: {count}")

            if qa_report.get('status_distribution'):
                print("\nStatus Distribution:")
                for status, count in qa_report['status_distribution'].items():
                    print(f"  {status}: {count}")

            if qa_report.get('kpis'):
                print("\nKPIs:")
                for kpi, value in qa_report['kpis'].items():
                    print(f"  {kpi}: {value:.2%}")

            # Sample agreements
            if agreements:
                print("\nSample Agreements Found:")
                for i, agreement in enumerate(agreements[:5], 1):
                    print(f"\n{i}. {agreement.title_native or agreement.title_en}")
                    print(f"   Type: {agreement.type}")
                    print(f"   Status: {agreement.status}")
                    print(f"   Date: {agreement.date_signed or 'Unknown'}")
                    print(f"   Source: {agreement.sources[0] if agreement.sources else 'N/A'}")

    except Exception as e:
        logger.error(f"Error during harvest: {e}", exc_info=True)

    finally:
        scraper.close()
        logger.info("\nHarvest complete!")

if __name__ == "__main__":
    harvest_italy_china_agreements()

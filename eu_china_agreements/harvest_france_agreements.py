#!/usr/bin/env python3
"""
France-China Agreements Harvester
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

def harvest_france_china_agreements():
    """Harvest France-China agreements using browser automation"""

    logger.info("="*60)
    logger.info("France-China Agreements Harvester")
    logger.info("="*60)

    # Initialize components
    base_dir = Path(__file__).parent
    config_path = base_dir / 'config' / 'countries.json'
    output_dir = base_dir / 'out'

    # Create output directories
    france_dir = output_dir / 'agreements' / 'FR'
    raw_dir = france_dir / 'raw'
    raw_dir.mkdir(parents=True, exist_ok=True)

    # Initialize scraper with Edge
    scraper = MultiBrowserScraper(browser='edge', headless=True)

    # Initialize processors
    extractor = AgreementExtractor(str(config_path))
    deduplicator = DeduplicationEngine()
    validator = ValidationEngine()

    all_results = []
    agreements = []

    try:
        # Define search queries for France
        search_queries = [
            # Official French government sites
            'site:diplomatie.gouv.fr accord Chine 2020..2025',
            'site:diplomatie.gouv.fr mémorandum Chine',
            'site:diplomatie.gouv.fr protocole Chine',
            'site:gouvernement.fr coopération Chine',
            'site:gouvernement.fr partenariat Chine',
            'site:legifrance.gouv.fr accord Chine',
            'site:elysee.fr Chine accord',

            # Specific agreements and initiatives
            '"Route de la Soie" site:diplomatie.gouv.fr',
            '"Belt and Road" site:gouvernement.fr',
            '"protocole d\'accord" Chine site:diplomatie.gouv.fr',

            # Regional agreements
            'site:iledefrance.fr Chine coopération',
            'site:auvergnerhonealpes.fr Chine partenariat',
            'site:nouvelle-aquitaine.fr Chine accord',
            'site:bretagne.bzh Chine coopération',

            # Municipal agreements (sister cities)
            'site:paris.fr jumelage Chine',
            'site:lyon.fr Chine partenariat',
            'site:marseille.fr Chine coopération',
            'site:toulouse.fr Chine jumelage',
            'site:nice.fr Chine accord',
            'jumelage Chine site:.fr ville',

            # University and research agreements
            'site:sorbonne.fr Chine mémorandum',
            'site:sciences-po.fr Chine accord',
            'site:cnrs.fr Chine coopération',
            'site:univ-paris.fr Chine partenariat',
            'site:polytechnique.edu Chine accord',

            # Chinese side
            'France agreement site:fmprc.gov.cn',
            '法国 协议 site:fmprc.gov.cn',
            'France coopération site:fr.china-embassy.gov.cn'
        ]

        logger.info(f"Executing {len(search_queries)} search queries...")

        # Execute searches using Bing
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
                        filename = raw_dir / f"france_{timestamp}_{hash(url)}.html"

                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write(content)

                        # Extract agreement data
                        agreement = extractor.extract_from_html(content, url, 'FR')
                        if agreement:
                            agreements.append(agreement)
                            logger.info(f"    Extracted: {agreement.title_native[:50] if agreement.title_native else 'Agreement'}...")

            # Rate limiting
            time.sleep(2)

        logger.info(f"\nTotal search results collected: {len(all_results)}")
        logger.info(f"Agreements extracted: {len(agreements)}")

        # Save all search results
        results_file = france_dir / 'search_results.json'
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'total_results': len(all_results),
                'results': all_results
            }, f, indent=2, ensure_ascii=False)

        # Process agreements
        if agreements:
            logger.info("\nProcessing agreements...")

            # Deduplicate
            clusters = deduplicator.find_duplicates(agreements)
            logger.info(f"Found {len(clusters)} duplicate clusters")

            for cluster in clusters:
                merged = deduplicator.merge_agreements(cluster)
                for agreement in cluster:
                    if agreement in agreements:
                        agreements.remove(agreement)
                agreements.append(merged)

            # Validate
            valid_count = 0
            for agreement in agreements:
                is_valid, issues = validator.validate(agreement)
                if is_valid:
                    valid_count += 1

            logger.info(f"{valid_count}/{len(agreements)} agreements passed validation")

            # Save agreements
            agreements_file = france_dir / 'agreements.ndjson'
            with open(agreements_file, 'w', encoding='utf-8') as f:
                for agreement in agreements:
                    json.dump(agreement.to_dict(), f, ensure_ascii=False)
                    f.write('\n')

            logger.info(f"Saved {len(agreements)} agreements to {agreements_file}")

            # Generate QA report
            qa_report = validator.generate_qa_report(agreements)
            report_file = output_dir / 'logs' / 'FR_coverage.json'
            report_file.parent.mkdir(exist_ok=True)

            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(qa_report, f, indent=2, ensure_ascii=False)

            # Print summary
            print("\n" + "="*60)
            print("FRANCE HARVEST SUMMARY")
            print("="*60)
            print(f"Total search results: {len(all_results)}")
            print(f"Agreements extracted: {len(agreements)}")
            print(f"Valid agreements: {valid_count}")

            if agreements:
                print("\nSample Agreements:")
                for i, ag in enumerate(agreements[:5], 1):
                    print(f"{i}. {ag.title_native or ag.title_en}")
                    print(f"   Type: {ag.type}, Status: {ag.status}")

    except Exception as e:
        logger.error(f"Error during harvest: {e}", exc_info=True)

    finally:
        scraper.close()
        logger.info("\nFrance harvest complete!")

if __name__ == "__main__":
    harvest_france_china_agreements()

#!/usr/bin/env python3
"""
Spain-China Agreements Harvester
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

def harvest_spain_china_agreements():
    """Harvest Spain-China agreements using browser automation"""

    logger.info("="*60)
    logger.info("Spain-China Agreements Harvester")
    logger.info("="*60)

    # Initialize components
    base_dir = Path(__file__).parent
    config_path = base_dir / 'config' / 'countries.json'
    output_dir = base_dir / 'out'

    # Create output directories
    spain_dir = output_dir / 'agreements' / 'ES'
    raw_dir = spain_dir / 'raw'
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
        # Define search queries for Spain
        search_queries = [
            # Official Spanish government sites
            'site:exteriores.gob.es acuerdo China 2020..2025',
            'site:exteriores.gob.es memorando China',
            'site:exteriores.gob.es protocolo China',
            'site:lamoncloa.gob.es cooperación China',
            'site:lamoncloa.gob.es asociación China',
            'site:boe.es China acuerdo',
            'site:congreso.es China convenio',
            'site:senado.es China acuerdo',

            # Specific agreements and initiatives
            '"Franja y Ruta" site:exteriores.gob.es',
            '"Belt and Road" site:lamoncloa.gob.es',
            '"protocolo de colaboración" China site:exteriores.gob.es',
            '"memorando de entendimiento" China site:exteriores.gob.es',

            # Autonomous communities (Comunidades Autónomas)
            'site:madrid.org China acuerdo',
            'site:gencat.cat China cooperación',
            'site:juntadeandalucia.es China convenio',
            'site:euskadi.eus China acuerdo',
            'site:gva.es China cooperación',
            'site:xunta.gal China convenio',
            'site:castillalamancha.es China acuerdo',

            # Municipal agreements (hermanamiento)
            'site:madrid.es hermanamiento China',
            'site:bcn.cat acuerdo China',
            'site:valencia.es cooperación China',
            'site:sevilla.org hermanamiento China',
            'site:zaragoza.es China convenio',
            'site:malaga.eu China cooperación',
            'site:bilbao.eus China acuerdo',
            'hermanamiento China site:.es ayuntamiento',

            # University agreements
            'site:ucm.es memorando China',
            'site:uab.cat acuerdo China',
            'site:uv.es cooperación China',
            'site:us.es convenio China',
            'site:unizar.es China acuerdo',
            'site:upm.es China cooperación',
            'site:ub.edu China convenio',

            # Chinese side
            'Spain agreement site:fmprc.gov.cn',
            '西班牙 协议 site:fmprc.gov.cn',
            'España cooperación site:es.china-embassy.gov.cn'
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
                        filename = raw_dir / f"spain_{timestamp}_{hash(url)}.html"

                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write(content)

                        # Extract agreement data
                        agreement = extractor.extract_from_html(content, url, 'ES')
                        if agreement:
                            agreements.append(agreement)
                            logger.info(f"    Extracted: {agreement.title_native[:50] if agreement.title_native else 'Agreement'}...")

            # Rate limiting
            time.sleep(2)

        logger.info(f"\nTotal search results collected: {len(all_results)}")
        logger.info(f"Agreements extracted: {len(agreements)}")

        # Save all search results
        results_file = spain_dir / 'search_results.json'
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
            agreements_file = spain_dir / 'agreements.ndjson'
            with open(agreements_file, 'w', encoding='utf-8') as f:
                for agreement in agreements:
                    json.dump(agreement.to_dict(), f, ensure_ascii=False)
                    f.write('\n')

            logger.info(f"Saved {len(agreements)} agreements to {agreements_file}")

            # Generate QA report
            qa_report = validator.generate_qa_report(agreements)
            report_file = output_dir / 'logs' / 'ES_coverage.json'
            report_file.parent.mkdir(exist_ok=True)

            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(qa_report, f, indent=2, ensure_ascii=False)

            # Print summary
            print("\n" + "="*60)
            print("SPAIN HARVEST SUMMARY")
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
        logger.info("\nSpain harvest complete!")

if __name__ == "__main__":
    harvest_spain_china_agreements()

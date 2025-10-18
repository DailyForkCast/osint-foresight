#!/usr/bin/env python3
"""
Master harvester for all EU countries
Runs individual country harvesters in sequence or parallel
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime
import concurrent.futures
import time

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'harvest_all_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import country harvesters
sys.path.append(str(Path(__file__).parent))
from harvest_italy_agreements import harvest_italy_china_agreements
from harvest_germany_agreements import harvest_germany_china_agreements
from harvest_france_agreements import harvest_france_china_agreements
from harvest_poland_agreements import harvest_poland_china_agreements
from harvest_spain_agreements import harvest_spain_china_agreements

def run_country_harvest(country_code: str):
    """Run harvest for a specific country"""
    harvesters = {
        'IT': harvest_italy_china_agreements,
        'DE': harvest_germany_china_agreements,
        'FR': harvest_france_china_agreements,
        'PL': harvest_poland_china_agreements,
        'ES': harvest_spain_china_agreements
    }

    if country_code not in harvesters:
        logger.error(f"Unknown country code: {country_code}")
        return None

    logger.info(f"\n{'='*60}")
    logger.info(f"Starting harvest for {country_code}")
    logger.info(f"{'='*60}")

    try:
        start_time = time.time()
        harvesters[country_code]()
        elapsed_time = time.time() - start_time

        logger.info(f"Completed {country_code} in {elapsed_time:.2f} seconds")
        return {
            'country': country_code,
            'status': 'success',
            'duration': elapsed_time
        }
    except Exception as e:
        logger.error(f"Failed to harvest {country_code}: {e}")
        return {
            'country': country_code,
            'status': 'failed',
            'error': str(e)
        }

def harvest_all_sequential():
    """Run all country harvesters sequentially"""
    countries = ['IT', 'DE', 'FR', 'PL', 'ES']
    results = []

    logger.info("\n" + "="*60)
    logger.info("EU-CHINA AGREEMENTS MASTER HARVESTER")
    logger.info("Mode: Sequential")
    logger.info("="*60)

    start_time = time.time()

    for country in countries:
        result = run_country_harvest(country)
        results.append(result)

        # Small delay between countries
        time.sleep(5)

    total_time = time.time() - start_time

    # Generate summary report
    generate_summary_report(results, total_time)

    return results

def harvest_all_parallel(max_workers: int = 2):
    """Run country harvesters in parallel"""
    countries = ['IT', 'DE', 'FR', 'PL', 'ES']
    results = []

    logger.info("\n" + "="*60)
    logger.info("EU-CHINA AGREEMENTS MASTER HARVESTER")
    logger.info(f"Mode: Parallel (max {max_workers} workers)")
    logger.info("="*60)

    start_time = time.time()

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_country = {
            executor.submit(run_country_harvest, country): country
            for country in countries
        }

        # Collect results as they complete
        for future in concurrent.futures.as_completed(future_to_country):
            country = future_to_country[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                logger.error(f"Country {country} generated exception: {e}")
                results.append({
                    'country': country,
                    'status': 'failed',
                    'error': str(e)
                })

    total_time = time.time() - start_time

    # Generate summary report
    generate_summary_report(results, total_time)

    return results

def generate_summary_report(results: list, total_time: float):
    """Generate and save summary report"""
    base_dir = Path(__file__).parent
    output_dir = base_dir / 'out' / 'reports'
    output_dir.mkdir(parents=True, exist_ok=True)

    # Count successes and failures
    successful = [r for r in results if r.get('status') == 'success']
    failed = [r for r in results if r.get('status') == 'failed']

    report = {
        'timestamp': datetime.now().isoformat(),
        'total_duration_seconds': total_time,
        'total_duration_formatted': f"{int(total_time//60)}m {int(total_time%60)}s",
        'countries_processed': len(results),
        'successful': len(successful),
        'failed': len(failed),
        'results': results,
        'statistics': {}
    }

    # Read individual country results if available
    for result in successful:
        country = result['country']
        try:
            # Try to read agreements file
            agreements_file = base_dir / 'out' / 'agreements' / country / 'agreements.ndjson'
            if agreements_file.exists():
                agreements = []
                with open(agreements_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        agreements.append(json.loads(line))

                report['statistics'][country] = {
                    'total_agreements': len(agreements),
                    'types': {},
                    'statuses': {}
                }

                # Count types and statuses
                for ag in agreements:
                    ag_type = ag.get('type', 'unknown')
                    ag_status = ag.get('status', 'unknown')

                    report['statistics'][country]['types'][ag_type] = \
                        report['statistics'][country]['types'].get(ag_type, 0) + 1
                    report['statistics'][country]['statuses'][ag_status] = \
                        report['statistics'][country]['statuses'].get(ag_status, 0) + 1

        except Exception as e:
            logger.debug(f"Could not read results for {country}: {e}")

    # Save report
    report_file = output_dir / f'master_harvest_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    logger.info(f"\n{'='*60}")
    logger.info("HARVEST COMPLETE")
    logger.info(f"{'='*60}")
    logger.info(f"Total time: {report['total_duration_formatted']}")
    logger.info(f"Successful: {len(successful)}/{len(results)}")

    if report['statistics']:
        logger.info("\nAgreements found by country:")
        for country, stats in report['statistics'].items():
            logger.info(f"  {country}: {stats['total_agreements']} agreements")

    logger.info(f"\nFull report saved to: {report_file}")

    # Print summary to console
    print("\n" + "="*60)
    print("EU-CHINA AGREEMENTS HARVEST SUMMARY")
    print("="*60)
    print(f"Duration: {report['total_duration_formatted']}")
    print(f"Countries: {len(results)} processed, {len(successful)} successful")

    if report['statistics']:
        total_agreements = sum(s['total_agreements'] for s in report['statistics'].values())
        print(f"Total agreements found: {total_agreements}")
        print("\nBy country:")
        for country, stats in report['statistics'].items():
            print(f"  {country}: {stats['total_agreements']} agreements")

    if failed:
        print(f"\nFailed countries: {', '.join(f['country'] for f in failed)}")

    print(f"\nDetailed report: {report_file}")

def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Harvest EU-China agreements for multiple countries'
    )
    parser.add_argument(
        '--mode',
        choices=['sequential', 'parallel'],
        default='sequential',
        help='Run mode (sequential or parallel)'
    )
    parser.add_argument(
        '--countries',
        nargs='+',
        choices=['IT', 'DE', 'FR', 'PL', 'ES', 'ALL'],
        default=['ALL'],
        help='Countries to harvest (default: ALL)'
    )
    parser.add_argument(
        '--workers',
        type=int,
        default=2,
        help='Max parallel workers (default: 2)'
    )

    args = parser.parse_args()

    # If specific countries selected
    if 'ALL' not in args.countries:
        logger.info(f"Harvesting specific countries: {args.countries}")
        results = []
        for country in args.countries:
            result = run_country_harvest(country)
            results.append(result)
        generate_summary_report(results, 0)
    else:
        # Run all countries
        if args.mode == 'parallel':
            harvest_all_parallel(max_workers=args.workers)
        else:
            harvest_all_sequential()

if __name__ == "__main__":
    main()

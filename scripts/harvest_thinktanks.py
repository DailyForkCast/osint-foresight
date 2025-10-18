#!/usr/bin/env python3
"""
Think Tank Harvesting Execution Script

This script orchestrates the complete think tank research harvesting process,
from crawling through analysis and export. It provides a command-line interface
for configuring and running harvesting operations.

Usage:
    python scripts/harvest_thinktanks.py --config config/thinktank_sources.yaml --output data/thinktank_harvest

Features:
- Full harvesting pipeline execution
- Progress tracking and logging
- Configurable filtering and processing
- Multiple output formats
- Error handling and recovery
- Performance monitoring
"""

import asyncio
import argparse
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
import json
import time

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.harvesters.thinktank_harvester import ThinkTankHarvester, HarvestConfig
from src.harvesters.thinktank_crawler import ThinkTankCrawler
from src.harvesters.thinktank_classifier import ThinkTankClassifier
from src.harvesters.thinktank_summarizer import ThinkTankSummarizer


def setup_logging(output_dir: Path, log_level: str = "INFO") -> logging.Logger:
    """Setup comprehensive logging for the harvesting process"""

    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)

    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))

    # Clear existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler
    log_file = output_dir / f"harvest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    return logger


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Think Tank Research Harvester",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic harvest with default settings
  python scripts/harvest_thinktanks.py --config config/thinktank_sources.yaml --output data/harvest

  # Harvest specific sources only
  python scripts/harvest_thinktanks.py --config config/thinktank_sources.yaml --output data/harvest --sources csis aspi merics

  # Harvest with custom settings
  python scripts/harvest_thinktanks.py --config config/thinktank_sources.yaml --output data/harvest --max-pages 100 --delay 2.0

  # Test run with limited scope
  python scripts/harvest_thinktanks.py --config config/thinktank_sources.yaml --output data/test --test-mode --max-pages 5
        """
    )

    # Required arguments
    parser.add_argument(
        "--config", "-c",
        type=Path,
        required=True,
        help="Path to think tank sources configuration file"
    )

    parser.add_argument(
        "--output", "-o",
        type=Path,
        required=True,
        help="Output directory for harvested data"
    )

    # Optional filtering
    parser.add_argument(
        "--sources",
        nargs="+",
        help="Specific think tank sources to harvest (default: all)"
    )

    parser.add_argument(
        "--countries",
        nargs="+",
        help="Filter sources by country codes (e.g., US GB DE)"
    )

    parser.add_argument(
        "--focus-areas",
        nargs="+",
        choices=["china", "technology", "arctic", "defense", "policy"],
        help="Filter sources by focus areas"
    )

    # Performance settings
    parser.add_argument(
        "--max-concurrent-sites",
        type=int,
        default=3,
        help="Maximum concurrent sites to process (default: 3)"
    )

    parser.add_argument(
        "--max-concurrent-pages",
        type=int,
        default=10,
        help="Maximum concurrent pages per site (default: 10)"
    )

    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Minimum delay between requests in seconds (default: 1.0)"
    )

    parser.add_argument(
        "--max-pages",
        type=int,
        help="Maximum pages to harvest per source (for testing)"
    )

    # Content settings
    parser.add_argument(
        "--content-age-days",
        type=int,
        default=1095,  # 3 years
        help="Maximum age of content in days (default: 1095 = 3 years)"
    )

    parser.add_argument(
        "--include-pdf",
        action="store_true",
        default=True,
        help="Include PDF documents (default: True)"
    )

    parser.add_argument(
        "--include-html",
        action="store_true",
        default=True,
        help="Include HTML documents (default: True)"
    )

    parser.add_argument(
        "--save-raw-files",
        action="store_true",
        help="Save raw downloaded files"
    )

    # Processing settings
    parser.add_argument(
        "--enable-translation",
        action="store_true",
        default=True,
        help="Enable translation to English (default: True)"
    )

    parser.add_argument(
        "--use-gpu",
        action="store_true",
        help="Use GPU for ML processing if available"
    )

    # Output settings
    parser.add_argument(
        "--formats",
        nargs="+",
        choices=["xlsx", "csv", "jsonl"],
        default=["xlsx", "csv", "jsonl"],
        help="Output formats (default: all)"
    )

    # Operational modes
    parser.add_argument(
        "--test-mode",
        action="store_true",
        help="Test mode: limited scope for testing"
    )

    parser.add_argument(
        "--resume",
        help="Resume from previous harvest (provide run ID)"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Dry run: show what would be harvested without actually harvesting"
    )

    # Logging
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)"
    )

    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress console output except errors"
    )

    return parser.parse_args()


def create_harvest_config(args: argparse.Namespace) -> HarvestConfig:
    """Create harvest configuration from command line arguments"""

    # Adjust settings for test mode
    if args.test_mode:
        max_concurrent_sites = 1
        max_concurrent_pages = 3
        min_delay = 2.0
        content_age_limit = 365  # 1 year for testing
    else:
        max_concurrent_sites = args.max_concurrent_sites
        max_concurrent_pages = args.max_concurrent_pages
        min_delay = args.delay
        content_age_limit = args.content_age_days

    return HarvestConfig(
        output_dir=args.output,
        max_concurrent_sites=max_concurrent_sites,
        max_concurrent_pages=max_concurrent_pages,
        min_delay_between_requests=min_delay,
        content_age_limit_days=content_age_limit,
        enable_translation=args.enable_translation,
        include_pdf=args.include_pdf,
        include_html=args.include_html,
        save_raw_files=args.save_raw_files
    )


def filter_sources(sources_config: Dict[str, Any], args: argparse.Namespace) -> Dict[str, Any]:
    """Filter sources based on command line arguments"""
    think_tanks = sources_config.get('think_tanks', {})
    filtered_tanks = {}

    for source_id, source_config in think_tanks.items():
        # Filter by source names
        if args.sources and source_id not in args.sources:
            continue

        # Filter by countries
        if args.countries:
            source_country = source_config.get('country', '').upper()
            if source_country not in [c.upper() for c in args.countries]:
                continue

        # Filter by focus areas
        if args.focus_areas:
            source_focus = source_config.get('focus_areas', [])
            if not any(area in source_focus for area in args.focus_areas):
                continue

        filtered_tanks[source_id] = source_config

    # Update sources config
    filtered_config = sources_config.copy()
    filtered_config['think_tanks'] = filtered_tanks

    return filtered_config


async def run_harvest(args: argparse.Namespace) -> Dict[str, Any]:
    """Run the complete harvesting process"""

    logger = logging.getLogger(__name__)
    start_time = time.time()

    try:
        # Create harvest configuration
        config = create_harvest_config(args)
        logger.info(f"Created harvest configuration: {config}")

        # Load and filter sources
        import yaml
        with open(args.config, 'r', encoding='utf-8') as f:
            sources_config = yaml.safe_load(f)

        # Apply filters
        sources_config = filter_sources(sources_config, args)

        num_sources = len(sources_config.get('think_tanks', {}))
        logger.info(f"Selected {num_sources} think tank sources for harvesting")

        if args.dry_run:
            logger.info("DRY RUN MODE: Would harvest from these sources:")
            for source_id, source_info in sources_config.get('think_tanks', {}).items():
                logger.info(f"  - {source_id}: {source_info.get('name')} ({source_info.get('country')})")
            return {"status": "dry_run_complete", "sources": num_sources}

        if num_sources == 0:
            logger.warning("No sources selected for harvesting!")
            return {"status": "no_sources", "sources": 0}

        # Save filtered configuration
        filtered_config_path = config.output_dir / "sources_config_filtered.yaml"
        with open(filtered_config_path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(sources_config, f, default_flow_style=False)

        # Initialize harvester
        logger.info("Initializing think tank harvester...")
        harvester = ThinkTankHarvester(config, filtered_config_path)

        # Run the harvest
        logger.info("Starting think tank research harvest...")
        documents = await harvester.harvest_all_sources()

        # Export results
        logger.info(f"Exporting {len(documents)} documents...")
        exported_files = harvester.export_results(args.formats)

        # Generate report
        report = harvester.generate_harvest_report()

        # Calculate metrics
        end_time = time.time()
        duration = end_time - start_time

        results = {
            "status": "success",
            "documents_collected": len(documents),
            "sources_processed": num_sources,
            "duration_seconds": duration,
            "exported_files": {k: str(v) for k, v in exported_files.items()},
            "report": report
        }

        logger.info(f"Harvest completed successfully!")
        logger.info(f"Documents collected: {len(documents)}")
        logger.info(f"Duration: {duration:.1f} seconds")
        logger.info(f"Exported files: {list(exported_files.keys())}")

        return results

    except Exception as e:
        logger.error(f"Harvest failed: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "duration_seconds": time.time() - start_time
        }


def save_run_metadata(args: argparse.Namespace, results: Dict[str, Any]):
    """Save metadata about the harvest run"""

    metadata = {
        "run_id": datetime.now().strftime('%Y%m%d_%H%M%S'),
        "timestamp": datetime.now().isoformat(),
        "arguments": vars(args),
        "results": results,
        "version": "1.0"
    }

    # Convert Path objects to strings for JSON serialization
    for key, value in metadata["arguments"].items():
        if isinstance(value, Path):
            metadata["arguments"][key] = str(value)

    metadata_file = args.output / f"harvest_metadata_{metadata['run_id']}.json"
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"Run metadata saved: {metadata_file}")


def main():
    """Main execution function"""

    # Parse arguments
    args = parse_arguments()

    # Adjust logging for quiet mode
    if args.quiet:
        log_level = "ERROR"
    else:
        log_level = args.log_level

    # Setup logging
    logger = setup_logging(args.output, log_level)

    # Log startup information
    logger.info("="*60)
    logger.info("Think Tank Research Harvester")
    logger.info("="*60)
    logger.info(f"Configuration: {args.config}")
    logger.info(f"Output directory: {args.output}")
    logger.info(f"Test mode: {args.test_mode}")
    logger.info(f"Dry run: {args.dry_run}")

    try:
        # Run the harvest
        results = asyncio.run(run_harvest(args))

        # Save run metadata
        save_run_metadata(args, results)

        # Print summary
        if not args.quiet:
            print("\n" + "="*60)
            print("HARVEST SUMMARY")
            print("="*60)
            print(f"Status: {results['status']}")
            if results['status'] == 'success':
                print(f"Documents collected: {results['documents_collected']}")
                print(f"Sources processed: {results['sources_processed']}")
                print(f"Duration: {results['duration_seconds']:.1f} seconds")
                print(f"Output files:")
                for format_type, file_path in results['exported_files'].items():
                    print(f"  - {format_type.upper()}: {file_path}")
            elif results['status'] == 'error':
                print(f"Error: {results['error']}")

        # Exit with appropriate code
        if results['status'] == 'success':
            sys.exit(0)
        else:
            sys.exit(1)

    except KeyboardInterrupt:
        logger.info("Harvest interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

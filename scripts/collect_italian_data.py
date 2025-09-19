"""
Focused Italian Company Data Collector
Downloads only Italian-related data to F: drive
"""

import os
import json
import time
from pathlib import Path
from datetime import datetime
import logging

# External drive setup
EXTERNAL_DRIVE = Path("F:/OSINT_DATA/Italy")
EXTERNAL_DRIVE.mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def collect_italian_company_data():
    """Collect Italian company data from all sources"""

    results = {
        'timestamp': datetime.now().isoformat(),
        'location': str(EXTERNAL_DRIVE),
        'data_collected': {}
    }

    # 1. SEC EDGAR - Leonardo DRS
    print("\n" + "="*50)
    print("COLLECTING LEONARDO DRS (SEC EDGAR)")
    print("="*50)

    try:
        from scripts.sec_edgar_client import SECEdgarClient
        sec_client = SECEdgarClient()

        # Get Leonardo DRS data
        leonardo_analysis = sec_client.analyze_leonardo_drs()

        # Save to F: drive
        sec_dir = EXTERNAL_DRIVE / 'SEC_EDGAR'
        sec_dir.mkdir(exist_ok=True)

        output_file = sec_dir / f"leonardo_drs_{datetime.now().strftime('%Y%m%d')}.json"
        with open(output_file, 'w') as f:
            json.dump(leonardo_analysis, f, indent=2, default=str)

        results['data_collected']['leonardo_drs'] = str(output_file)
        print(f"✓ Saved Leonardo DRS data: {output_file}")

        # Get all Italian connections
        italian_connections = sec_client.search_italian_connections()

        output_file = sec_dir / f"italian_sec_companies_{datetime.now().strftime('%Y%m%d')}.json"
        with open(output_file, 'w') as f:
            json.dump(italian_connections, f, indent=2)

        results['data_collected']['italian_sec_companies'] = str(output_file)
        print(f"✓ Saved Italian SEC companies: {output_file}")

    except Exception as e:
        logger.error(f"SEC EDGAR collection failed: {e}")
        results['data_collected']['sec_error'] = str(e)

    # 2. EPO Patents
    print("\n" + "="*50)
    print("COLLECTING ITALIAN PATENTS (EPO)")
    print("="*50)

    try:
        from scripts.epo_ops_client import EPOOPSClient
        epo_client = EPOOPSClient()

        epo_dir = EXTERNAL_DRIVE / 'EPO_PATENTS'
        epo_dir.mkdir(exist_ok=True)

        # Leonardo patents
        print("Searching Leonardo patents...")
        leonardo_patents = epo_client.search_leonardo_patents()

        output_file = epo_dir / f"leonardo_patents_{datetime.now().strftime('%Y%m%d')}.json"
        with open(output_file, 'w') as f:
            json.dump(leonardo_patents, f, indent=2)

        results['data_collected']['leonardo_patents'] = str(output_file)
        print(f"✓ Saved Leonardo patents: {output_file}")

        # Italy-China collaborations
        print("Searching Italy-China patent collaborations...")
        collaborations = epo_client.search_italy_china_collaborations()

        output_file = epo_dir / f"italy_china_patents_{datetime.now().strftime('%Y%m%d')}.json"
        with open(output_file, 'w') as f:
            json.dump(collaborations, f, indent=2)

        results['data_collected']['italy_china_patents'] = str(output_file)
        print(f"✓ Saved Italy-China patents: {output_file}")

    except Exception as e:
        logger.error(f"EPO collection failed: {e}")
        results['data_collected']['epo_error'] = str(e)

    # 3. TED Procurement (if needed)
    print("\n" + "="*50)
    print("CHECKING TED PROCUREMENT DATA")
    print("="*50)

    ted_local_dir = Path("data/collected/ted")
    if ted_local_dir.exists():
        ted_dir = EXTERNAL_DRIVE / 'TED_PROCUREMENT'
        ted_dir.mkdir(exist_ok=True)

        # Copy existing TED data
        for file in ted_local_dir.glob("*.json"):
            output_file = ted_dir / file.name
            with open(file, 'r') as f:
                data = json.load(f)
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"✓ Copied TED data: {output_file.name}")

    # Save summary
    summary_file = EXTERNAL_DRIVE / f"collection_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(summary_file, 'w') as f:
        json.dump(results, f, indent=2)

    print("\n" + "="*50)
    print("COLLECTION COMPLETE")
    print("="*50)
    print(f"Data saved to: {EXTERNAL_DRIVE}")
    print(f"Summary: {summary_file}")

    # List all files collected
    print("\nFiles collected:")
    for key, path in results['data_collected'].items():
        if not key.endswith('_error'):
            print(f"  - {key}: {Path(path).name if isinstance(path, str) else path}")

    return results


if __name__ == "__main__":
    print("ITALIAN COMPANY DATA COLLECTOR")
    print("="*50)
    print(f"Target: F:/OSINT_DATA/Italy")
    print("\nThis will collect:")
    print("- Leonardo DRS SEC filings")
    print("- Italian companies in SEC")
    print("- Leonardo patents from EPO")
    print("- Italy-China patent collaborations")
    print("- TED procurement data (if available)")

    results = collect_italian_company_data()

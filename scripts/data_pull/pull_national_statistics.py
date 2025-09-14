#!/usr/bin/env python3
"""
Pull data from National Statistics Offices across Europe
Handles multiple API types: OData, REST/JSON, PX-Web, SDMX, JSON-stat
"""
import os
import json
import yaml
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime
import logging
from typing import Dict, List, Optional
import time

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StatisticsOfficePuller:
    """Base class for statistics office data pullers"""

    def __init__(self, country: str, config: Dict, output_dir: Path):
        self.country = country
        self.config = config
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def pull_data(self) -> bool:
        """Override in subclasses"""
        raise NotImplementedError


class ODataPuller(StatisticsOfficePuller):
    """Pull data from OData APIs (Austria, Netherlands)"""

    def pull_data(self) -> bool:
        base_url = self.config['api']['base_url']

        try:
            # Get metadata first
            metadata_url = f"{base_url}/$metadata"
            response = requests.get(metadata_url, timeout=30)

            if response.status_code == 200:
                # Save metadata
                metadata_file = self.output_dir / f"metadata_{datetime.now().strftime('%Y%m%d')}.xml"
                metadata_file.write_text(response.text)

                # Pull specific datasets
                for dataset in self.config.get('datasets', []):
                    self.pull_dataset(base_url, dataset)

                return True

        except Exception as e:
            logger.error(f"OData pull failed for {self.country}: {e}")
            return False

    def pull_dataset(self, base_url: str, dataset: str):
        """Pull individual dataset from OData"""
        try:
            url = f"{base_url}/{dataset}?$format=json"
            response = requests.get(url, timeout=60)

            if response.status_code == 200:
                data = response.json()

                # Save raw data
                output_file = self.output_dir / f"{dataset}_{datetime.now().strftime('%Y%m%d')}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)

                logger.info(f"Saved {dataset} for {self.country}")

                # Convert to CSV if possible
                if 'value' in data:
                    df = pd.DataFrame(data['value'])
                    csv_file = self.output_dir / f"{dataset}_{datetime.now().strftime('%Y%m%d')}.csv"
                    df.to_csv(csv_file, index=False)

        except Exception as e:
            logger.error(f"Failed to pull dataset {dataset}: {e}")


class JSONStatPuller(StatisticsOfficePuller):
    """Pull data from JSON-stat APIs (Norway, Ireland)"""

    def pull_data(self) -> bool:
        base_url = self.config['api']['base_url']

        try:
            for dataset_id in self.config.get('datasets', []):
                self.pull_dataset(base_url, dataset_id)
            return True

        except Exception as e:
            logger.error(f"JSON-stat pull failed for {self.country}: {e}")
            return False

    def pull_dataset(self, base_url: str, dataset_id: str):
        """Pull dataset in JSON-stat format"""
        try:
            # Build query for JSON-stat
            if self.country == 'NO':  # Norway specific
                url = f"{base_url}/en/table/{dataset_id}"
                query = {
                    "query": [],
                    "response": {"format": "json-stat2"}
                }
            elif self.country == 'IE':  # Ireland specific
                url = f"{base_url}/{dataset_id}/JSON-stat/2.0/en"
                query = None
            else:
                url = f"{base_url}/{dataset_id}"
                query = None

            if query:
                response = requests.post(url, json=query, timeout=60)
            else:
                response = requests.get(url, timeout=60)

            if response.status_code == 200:
                data = response.json()

                # Save JSON-stat data
                output_file = self.output_dir / f"{dataset_id}_{datetime.now().strftime('%Y%m%d')}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)

                logger.info(f"Saved {dataset_id} for {self.country}")

                # Parse JSON-stat to DataFrame
                self.parse_jsonstat_to_csv(data, dataset_id)

        except Exception as e:
            logger.error(f"Failed to pull dataset {dataset_id}: {e}")

    def parse_jsonstat_to_csv(self, data: Dict, dataset_id: str):
        """Convert JSON-stat to CSV"""
        try:
            # This is simplified - full JSON-stat parsing is complex
            if 'value' in data and 'dimension' in data:
                values = data['value']

                # Create simple CSV
                csv_file = self.output_dir / f"{dataset_id}_{datetime.now().strftime('%Y%m%d')}.csv"

                df = pd.DataFrame({'value': values if isinstance(values, list) else list(values.values())})
                df.to_csv(csv_file, index=False)

        except Exception as e:
            logger.warning(f"Could not convert JSON-stat to CSV: {e}")


class PXWebPuller(StatisticsOfficePuller):
    """Pull data from PX-Web APIs (Finland, Sweden, Switzerland)"""

    def pull_data(self) -> bool:
        base_url = self.config['api']['base_url']

        try:
            # First get database structure
            response = requests.get(base_url, timeout=30)

            if response.status_code == 200:
                databases = response.json()

                # Pull configured datasets
                for dataset in self.config.get('datasets', []):
                    self.pull_dataset(base_url, dataset)

                return True

        except Exception as e:
            logger.error(f"PX-Web pull failed for {self.country}: {e}")
            return False

    def pull_dataset(self, base_url: str, dataset: str):
        """Pull dataset from PX-Web API"""
        try:
            # Get table metadata
            table_url = f"{base_url}/{dataset}"
            response = requests.get(table_url, timeout=30)

            if response.status_code == 200:
                metadata = response.json()

                # Build query to get all data
                query = self.build_pxweb_query(metadata)

                # Get data
                response = requests.post(table_url, json=query, timeout=60)

                if response.status_code == 200:
                    data = response.json()

                    # Save data
                    output_file = self.output_dir / f"{dataset}_{datetime.now().strftime('%Y%m%d')}.json"
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)

                    logger.info(f"Saved {dataset} for {self.country}")

        except Exception as e:
            logger.error(f"Failed to pull dataset {dataset}: {e}")

    def build_pxweb_query(self, metadata: Dict) -> Dict:
        """Build query for PX-Web API"""
        query = {
            "query": [],
            "response": {"format": "json"}
        }

        # Select all values for each variable (simplified)
        if 'variables' in metadata:
            for var in metadata['variables']:
                query['query'].append({
                    "code": var['code'],
                    "selection": {
                        "filter": "all",
                        "values": ["*"]
                    }
                })

        return query


class SDMXPuller(StatisticsOfficePuller):
    """Pull data from SDMX APIs (Italy ISTAT)"""

    def pull_data(self) -> bool:
        base_url = self.config['api']['base_url']

        try:
            for dataset in self.config.get('datasets', []):
                self.pull_dataset(base_url, dataset)
            return True

        except Exception as e:
            logger.error(f"SDMX pull failed for {self.country}: {e}")
            return False

    def pull_dataset(self, base_url: str, dataset: str):
        """Pull dataset in SDMX format"""
        try:
            # SDMX REST API pattern
            url = f"{base_url}/data/{dataset}/all?format=jsondata"
            response = requests.get(url, timeout=60)

            if response.status_code == 200:
                data = response.json()

                # Save SDMX data
                output_file = self.output_dir / f"{dataset}_{datetime.now().strftime('%Y%m%d')}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)

                logger.info(f"Saved {dataset} for {self.country}")

        except Exception as e:
            logger.error(f"Failed to pull dataset {dataset}: {e}")


class RESTJSONPuller(StatisticsOfficePuller):
    """Generic REST/JSON API puller"""

    def pull_data(self) -> bool:
        base_url = self.config['api']['base_url']
        auth = self.config['api'].get('authentication', 'none')

        headers = {}
        if auth == 'api_key':
            # Would need to load API key from environment
            api_key = os.environ.get(f"{self.country}_API_KEY")
            if api_key:
                headers['Authorization'] = f"Bearer {api_key}"

        try:
            for dataset in self.config.get('datasets', []):
                self.pull_dataset(base_url, dataset, headers)
            return True

        except Exception as e:
            logger.error(f"REST/JSON pull failed for {self.country}: {e}")
            return False

    def pull_dataset(self, base_url: str, dataset: str, headers: Dict):
        """Pull dataset from REST API"""
        try:
            url = f"{base_url}/{dataset}"
            response = requests.get(url, headers=headers, timeout=60)

            if response.status_code == 200:
                data = response.json()

                # Save data
                output_file = self.output_dir / f"{dataset}_{datetime.now().strftime('%Y%m%d')}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)

                logger.info(f"Saved {dataset} for {self.country}")

        except Exception as e:
            logger.error(f"Failed to pull dataset {dataset}: {e}")


class NationalStatisticsPuller:
    """Main orchestrator for pulling from all national statistics offices"""

    def __init__(self, output_base_dir: Path = Path("F:/OSINT_Data/statistics")):
        self.output_base_dir = output_base_dir
        self.config = self.load_config()

    def load_config(self) -> Dict:
        """Load statistics offices configuration"""
        config_file = Path("C:/Projects/OSINT - Foresight/config/national_statistics_offices.yaml")
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)

    def get_puller_class(self, api_type: str):
        """Get appropriate puller class for API type"""
        pullers = {
            'OData': ODataPuller,
            'REST/JSON': RESTJSONPuller,
            'PX-Web API': PXWebPuller,
            'SDMX': SDMXPuller,
            'REST/JSON-stat': JSONStatPuller,
            'JSON-stat': JSONStatPuller
        }
        return pullers.get(api_type)

    def pull_country(self, country_code: str) -> bool:
        """Pull data for a specific country"""
        if country_code not in self.config['statistics_offices']:
            logger.error(f"Country {country_code} not configured")
            return False

        country_config = self.config['statistics_offices'][country_code]

        # Check if API is available
        if not country_config.get('api', {}).get('available', False):
            logger.warning(f"{country_code} ({country_config['name']}) requires manual download")
            return False

        # Get appropriate puller
        api_type = country_config['api'].get('type')
        puller_class = self.get_puller_class(api_type)

        if not puller_class:
            logger.warning(f"No puller available for API type: {api_type}")
            return False

        # Create output directory
        output_dir = self.output_base_dir / f"country={country_code}"

        # Initialize and run puller
        try:
            puller = puller_class(country_code, country_config, output_dir)
            return puller.pull_data()
        except Exception as e:
            logger.error(f"Failed to pull data for {country_code}: {e}")
            return False

    def pull_tier(self, tier: int) -> Dict[str, bool]:
        """Pull data for all countries in a priority tier"""
        results = {}

        tier_countries = self.config['summary']['priority_for_automation'].get(f'tier_{tier}', [])

        for country in tier_countries:
            logger.info(f"Pulling data for {country}...")
            results[country] = self.pull_country(country)
            time.sleep(2)  # Be polite to APIs

        return results

    def pull_all_automated(self) -> Dict[str, bool]:
        """Pull data from all countries with automation available"""
        results = {}

        for country_code, config in self.config['statistics_offices'].items():
            if config.get('automation_status') in ['FULL', 'PARTIAL']:
                logger.info(f"Pulling data for {country_code}...")
                results[country_code] = self.pull_country(country_code)
                time.sleep(2)  # Rate limiting

        return results

    def generate_manual_report(self) -> str:
        """Generate report of offices requiring manual attention"""
        report = []
        report.append("National Statistics Offices Requiring Manual Download")
        report.append("=" * 60)

        manual_offices = []

        for country_code, config in self.config['statistics_offices'].items():
            if config.get('automation_status') == 'MANUAL':
                manual_offices.append({
                    'code': country_code,
                    'name': config['name'],
                    'website': config['website'],
                    'process': config.get('manual_process', ['Visit website and download manually']),
                    'notes': config.get('notes', '')
                })

        for office in sorted(manual_offices, key=lambda x: x['code']):
            report.append(f"\n{office['code']} - {office['name']}")
            report.append(f"Website: {office['website']}")
            report.append("Process:")
            for step in office['process']:
                report.append(f"  - {step}")
            if office['notes']:
                report.append(f"Notes: {office['notes']}")

        report.append(f"\nTotal requiring manual download: {len(manual_offices)}")

        return "\n".join(report)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Pull data from National Statistics Offices")
    parser.add_argument("--country", help="Specific country code (e.g., DE, FR)")
    parser.add_argument("--tier", type=int, choices=[1, 2, 3],
                      help="Pull all countries in priority tier")
    parser.add_argument("--all", action="store_true",
                      help="Pull from all automated sources")
    parser.add_argument("--manual-report", action="store_true",
                      help="Generate report of manual download requirements")
    parser.add_argument("--output", default="F:/OSINT_Data/statistics",
                      help="Base output directory")

    args = parser.parse_args()

    puller = NationalStatisticsPuller(Path(args.output))

    if args.manual_report:
        report = puller.generate_manual_report()
        print(report)

        # Save report
        report_file = Path(args.output) / f"manual_offices_report_{datetime.now().strftime('%Y%m%d')}.txt"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        report_file.write_text(report)

    elif args.country:
        success = puller.pull_country(args.country)
        if success:
            print(f"Successfully pulled data for {args.country}")
        else:
            print(f"Failed to pull data for {args.country}")

    elif args.tier:
        results = puller.pull_tier(args.tier)

        print(f"\nTier {args.tier} Pull Results:")
        for country, success in results.items():
            status = "✓" if success else "✗"
            print(f"  {status} {country}")

    elif args.all:
        results = puller.pull_all_automated()

        print("\nPull Results:")
        successful = [c for c, s in results.items() if s]
        failed = [c for c, s in results.items() if not s]

        print(f"Successful: {', '.join(successful)}")
        if failed:
            print(f"Failed: {', '.join(failed)}")

    else:
        print("Please specify --country, --tier, --all, or --manual-report")


if __name__ == "__main__":
    main()

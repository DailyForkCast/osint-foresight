"""
USAspending.gov Data Collector for OSINT Foresight
Downloads federal spending data focusing on Italian companies
Particularly Leonardo DRS contracts
"""

import os
import json
import requests
import zipfile
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class USAspendingCollector:
    """Collect US federal spending data for Italian companies"""

    def __init__(self):
        """Initialize USAspending collector"""
        # API endpoints
        self.api_base = "https://api.usaspending.gov/api/v2"
        self.download_base = "https://files.usaspending.gov"

        # External drive paths
        self.external_base = Path("F:/OSINT_DATA/Italy/USASPENDING")
        self.external_base.mkdir(parents=True, exist_ok=True)

        # Headers for API requests
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "OSINT-Foresight/1.0"
        }

        # Italian companies to search
        self.italian_companies = [
            {
                "name": "LEONARDO DRS, INC.",
                "duns": "080318379",  # DRS Consolidated Controls
                "cage_codes": ["1YQE8", "64678", "0YPM0"],
                "parent": "Leonardo S.p.A"
            },
            {
                "name": "LEONARDO ELECTRONICS US INC",
                "duns": "824510457",
                "cage_codes": ["4YDQ2"],
                "parent": "Leonardo S.p.A"
            },
            {
                "name": "FINCANTIERI MARINE GROUP LLC",
                "duns": "968819509",
                "cage_codes": ["69H39"],
                "parent": "Fincantieri S.p.A"
            },
            {
                "name": "FINCANTIERI BAY SHIPBUILDING",
                "duns": "007141486",
                "cage_codes": ["21839"],
                "parent": "Fincantieri S.p.A"
            }
        ]

    def search_company_awards(self, company_name: str, start_date: str = "2020-01-01", end_date: str = "2024-12-31") -> Dict:
        """
        Search for federal awards to a specific company

        Args:
            company_name: Company name to search
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            Award data
        """
        logger.info(f"Searching awards for {company_name}...")

        endpoint = f"{self.api_base}/search/spending_by_award/"

        payload = {
            "filters": {
                "time_period": [
                    {
                        "start_date": start_date,
                        "end_date": end_date
                    }
                ],
                "recipient_search_text": [company_name],
                "award_type_codes": ["A", "B", "C", "D"]  # Contract types
            },
            "fields": [
                "Award ID",
                "Recipient Name",
                "Start Date",
                "End Date",
                "Award Amount",
                "Total Outlays",
                "Description",
                "Awarding Agency",
                "Awarding Sub Agency",
                "Contract Award Type",
                "recipient_id"
            ],
            "page": 1,
            "limit": 100,
            "sort": "Award Amount",
            "order": "desc"
        }

        try:
            response = requests.post(endpoint, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to search awards: {e}")
            return {}

    def get_recipient_profile(self, recipient_id: str) -> Dict:
        """
        Get detailed profile of a recipient

        Args:
            recipient_id: USAspending recipient ID (usually DUNS)

        Returns:
            Recipient profile data
        """
        endpoint = f"{self.api_base}/recipient/duns/{recipient_id}/"

        try:
            response = requests.get(endpoint, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get recipient profile: {e}")
            return {}

    def download_leonardo_contracts(self) -> Dict:
        """
        Download all Leonardo DRS and related contracts

        Returns:
            Summary of downloaded data
        """
        logger.info("Downloading Leonardo DRS contracts...")

        results = {
            "companies_searched": [],
            "total_contracts": 0,
            "total_value": 0,
            "files_saved": []
        }

        for company in self.italian_companies:
            if "Leonardo" not in company["name"] and "LEONARDO" not in company["name"]:
                continue

            logger.info(f"Processing {company['name']}...")

            # Search for awards
            awards = self.search_company_awards(
                company["name"],
                start_date="2020-01-01",
                end_date="2024-12-31"
            )

            if awards and "results" in awards:
                company_data = {
                    "company": company["name"],
                    "parent": company["parent"],
                    "duns": company["duns"],
                    "cage_codes": company.get("cage_codes", []),
                    "awards": awards["results"],
                    "total_awards": len(awards["results"]),
                    "total_value": sum(float(a.get("Award Amount", 0)) for a in awards["results"] if a.get("Award Amount"))
                }

                results["companies_searched"].append(company["name"])
                results["total_contracts"] += company_data["total_awards"]
                results["total_value"] += company_data["total_value"]

                # Save to file
                timestamp = datetime.now().strftime("%Y%m%d")
                filename = f"{company['name'].replace(' ', '_').replace(',', '')}_{timestamp}.json"
                output_file = self.external_base / filename

                with open(output_file, 'w') as f:
                    json.dump(company_data, f, indent=2)

                results["files_saved"].append(str(output_file))
                logger.info(f"Saved {company_data['total_awards']} contracts to {output_file}")

            time.sleep(0.5)  # Rate limiting

        return results

    def search_italy_related_spending(self) -> Dict:
        """
        Search for all Italy-related federal spending

        Returns:
            Italy-related spending data
        """
        logger.info("Searching for Italy-related federal spending...")

        # Search by country
        endpoint = f"{self.api_base}/search/spending_by_geography/"

        payload = {
            "filters": {
                "time_period": [
                    {
                        "start_date": "2020-01-01",
                        "end_date": "2024-12-31"
                    }
                ],
                "place_of_performance_locations": [
                    {
                        "country": "ITA"
                    }
                ]
            },
            "subawards": False,
            "scope": "place_of_performance",
            "geo_layer": "country"
        }

        try:
            response = requests.post(endpoint, headers=self.headers, json=payload)
            response.raise_for_status()

            italy_spending = response.json()

            # Save results
            output_file = self.external_base / f"italy_federal_spending_{datetime.now().strftime('%Y%m%d')}.json"
            with open(output_file, 'w') as f:
                json.dump(italy_spending, f, indent=2)

            logger.info(f"Saved Italy spending data to {output_file}")

            return italy_spending

        except Exception as e:
            logger.error(f"Failed to search Italy spending: {e}")
            return {}

    def download_bulk_contract_data(self, year: int = 2024) -> str:
        """
        Download bulk contract data files

        Args:
            year: Fiscal year to download

        Returns:
            Path to downloaded file
        """
        logger.info(f"Downloading bulk contract data for FY{year}...")

        # Construct download URL
        # Note: These URLs follow a pattern but may need verification
        url = f"{self.download_base}/award_data_archive/FY{year}_All_Contracts_Full_{datetime.now().strftime('%Y%m%d')}.zip"

        output_file = self.external_base / f"FY{year}_contracts_bulk.zip"

        if output_file.exists():
            logger.info(f"File already exists: {output_file}")
            return str(output_file)

        try:
            # Note: This may fail if the exact URL is different
            response = requests.get(url, headers=self.headers, stream=True)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            chunk_size = 8192

            with open(output_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"\rDownloading: {progress:.1f}%", end='')

            print()
            logger.info(f"Downloaded bulk data to {output_file}")
            return str(output_file)

        except Exception as e:
            logger.warning(f"Could not download bulk file: {e}")
            logger.info("Please download manually from https://www.usaspending.gov/download_center/award_data_archive")
            return ""

    def collect_all_data(self) -> Dict:
        """
        Collect all USAspending data for Italian companies

        Returns:
            Collection summary
        """
        logger.info("Starting USAspending data collection...")

        results = {
            "timestamp": datetime.now().isoformat(),
            "location": str(self.external_base),
            "leonardo_contracts": {},
            "italy_spending": {},
            "other_italian_companies": {}
        }

        # 1. Download Leonardo DRS contracts
        print("\n" + "="*50)
        print("LEONARDO DRS CONTRACTS")
        print("="*50)
        results["leonardo_contracts"] = self.download_leonardo_contracts()

        # 2. Search Italy-related spending
        print("\n" + "="*50)
        print("ITALY-RELATED FEDERAL SPENDING")
        print("="*50)
        results["italy_spending"] = self.search_italy_related_spending()

        # 3. Search other Italian companies
        print("\n" + "="*50)
        print("OTHER ITALIAN COMPANIES")
        print("="*50)

        for company in self.italian_companies:
            if "Leonardo" not in company["name"] and "LEONARDO" not in company["name"]:
                logger.info(f"Searching for {company['name']}...")
                awards = self.search_company_awards(company["name"])

                if awards and "results" in awards:
                    results["other_italian_companies"][company["name"]] = {
                        "total_awards": len(awards["results"]),
                        "parent": company["parent"]
                    }

        # Save summary
        summary_file = self.external_base / f"collection_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_file, 'w') as f:
            json.dump(results, f, indent=2)

        print("\n" + "="*50)
        print("COLLECTION COMPLETE")
        print("="*50)
        print(f"Data saved to: {self.external_base}")
        print(f"Summary: {summary_file}")

        if results["leonardo_contracts"]:
            print(f"\nLeonardo contracts found: {results['leonardo_contracts'].get('total_contracts', 0)}")
            print(f"Total value: ${results['leonardo_contracts'].get('total_value', 0):,.2f}")

        return results


if __name__ == "__main__":
    collector = USAspendingCollector()

    print("USASPENDING.GOV DATA COLLECTOR")
    print("="*50)
    print("Target: F:/OSINT_DATA/Italy/USASPENDING")
    print("\nThis will collect:")
    print("- Leonardo DRS federal contracts")
    print("- Other Italian company contracts")
    print("- Italy-related federal spending")
    print()

    results = collector.collect_all_data()

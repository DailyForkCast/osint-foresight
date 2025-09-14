#!/usr/bin/env python3
"""
Pull World Bank indicators for a country
"""
import os
import json
import argparse
import requests
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorldBankPuller:
    """Pull data from World Bank API"""

    def __init__(self, country: str, output_dir: Path):
        self.country = country
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.base_url = "https://api.worldbank.org/v2"

        # Key indicators for technology assessment
        self.indicators = [
            "GB.XPD.RSDV.GD.ZS",  # R&D expenditure (% of GDP)
            "IP.PAT.RESD",  # Patent applications, residents
            "IP.PAT.NRES",  # Patent applications, non-residents
            "TX.VAL.TECH.CD",  # High-technology exports (current US$)
            "TX.VAL.TECH.MF.ZS",  # High-technology exports (% of manufactured exports)
            "IT.NET.USER.ZS",  # Individuals using the Internet (% of population)
            "IT.CEL.SETS.P2",  # Mobile cellular subscriptions (per 100 people)
            "SE.TER.GRAD.SC.ZS",  # STEM graduates (% of total)
            "SL.TLF.ADVN.ZS",  # Labor force with advanced education (% of total)
            "NY.GDP.PCAP.PP.CD",  # GDP per capita, PPP (current international $)
            "NE.EXP.GNFS.ZS",  # Exports of goods and services (% of GDP)
            "BX.KLT.DINV.WD.GD.ZS",  # Foreign direct investment, net inflows (% of GDP)
            "SP.POP.SCIE.RD.P6",  # Researchers in R&D (per million people)
            "GB.XPD.RSDV.GD.ZS",  # Research and development expenditure (% of GDP)
            "IP.TMK.RESD",  # Trademark applications, direct resident
        ]

    def get_country_code(self) -> str:
        """Convert 2-letter to 3-letter country code for World Bank API"""
        # Mapping of 2-letter to 3-letter codes
        country_codes = {
            "AT": "AUT", "BE": "BEL", "BG": "BGR", "HR": "HRV", "CY": "CYP",
            "CZ": "CZE", "DK": "DNK", "EE": "EST", "FI": "FIN", "FR": "FRA",
            "DE": "DEU", "GR": "GRC", "HU": "HUN", "IE": "IRL", "IT": "ITA",
            "LV": "LVA", "LT": "LTU", "LU": "LUX", "MT": "MLT", "NL": "NLD",
            "PL": "POL", "PT": "PRT", "RO": "ROU", "SK": "SVK", "SI": "SVN",
            "ES": "ESP", "SE": "SWE", "GB": "GBR", "NO": "NOR", "CH": "CHE",
            "IS": "ISL", "LI": "LIE", "TR": "TUR", "RS": "SRB", "ME": "MNE",
            "MK": "MKD", "AL": "ALB", "BA": "BIH", "XK": "XKX", "MD": "MDA",
            "UA": "UKR", "GE": "GEO", "AM": "ARM", "AZ": "AZE"
        }
        return country_codes.get(self.country, self.country)

    def pull_indicator(self, indicator: str, start_year: int = 2010) -> dict:
        """Pull single indicator data"""
        country_code = self.get_country_code()

        url = f"{self.base_url}/country/{country_code}/indicator/{indicator}"
        params = {
            "format": "json",
            "date": f"{start_year}:{datetime.now().year}",
            "per_page": 100
        }

        try:
            response = requests.get(url, params=params, timeout=30)

            if response.status_code == 200:
                data = response.json()

                # World Bank API returns metadata in first element
                if len(data) > 1:
                    return {
                        "indicator": indicator,
                        "country": self.country,
                        "data": data[1] if data[1] else []
                    }
            else:
                logger.warning(f"Failed to pull {indicator}: {response.status_code}")

        except Exception as e:
            logger.error(f"Error pulling {indicator}: {e}")

        return {"indicator": indicator, "country": self.country, "data": []}

    def pull_all_indicators(self):
        """Pull all configured indicators"""
        logger.info(f"Pulling World Bank indicators for {self.country}")

        all_data = {
            "country": self.country,
            "country_code": self.get_country_code(),
            "pull_date": datetime.now().isoformat(),
            "indicators": {}
        }

        for indicator in self.indicators:
            logger.info(f"  Pulling {indicator}")
            indicator_data = self.pull_indicator(indicator)

            if indicator_data["data"]:
                all_data["indicators"][indicator] = indicator_data["data"]

        # Save data
        output_file = self.output_dir / f"wb_indicators_{datetime.now().strftime('%Y%m%d')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved {len(all_data['indicators'])} indicators to {output_file}")

        # Also save as CSV for easier analysis
        self.save_as_csv(all_data)

        return len(all_data["indicators"])

    def save_as_csv(self, data: dict):
        """Save indicators as CSV for easier analysis"""
        import csv

        csv_file = self.output_dir / f"wb_indicators_{datetime.now().strftime('%Y%m%d')}.csv"

        # Flatten the data structure
        rows = []
        for indicator_code, values in data["indicators"].items():
            for entry in values:
                if entry and entry.get("value") is not None:
                    rows.append({
                        "country": self.country,
                        "indicator": indicator_code,
                        "year": entry.get("date"),
                        "value": entry.get("value")
                    })

        if rows:
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=["country", "indicator", "year", "value"])
                writer.writeheader()
                writer.writerows(rows)

            logger.info(f"Saved CSV with {len(rows)} data points to {csv_file}")


def main():
    parser = argparse.ArgumentParser(description="Pull World Bank indicator data")
    parser.add_argument("--country", required=True, help="Country code (e.g., AT, DE)")
    parser.add_argument("--output", required=True, help="Output directory")
    parser.add_argument("--start-year", type=int, default=2010, help="Start year for data")

    args = parser.parse_args()

    puller = WorldBankPuller(args.country, args.output)
    indicator_count = puller.pull_all_indicators()

    logger.info(f"Pull complete: {indicator_count} indicators retrieved")


if __name__ == "__main__":
    main()

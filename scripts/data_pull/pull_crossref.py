#!/usr/bin/env python3
"""
Pull Crossref publication and event data for a country
"""
import os
import json
import time
import argparse
import requests
from pathlib import Path
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CrossrefPuller:
    """Pull data from Crossref API"""

    def __init__(self, country: str, output_dir: Path):
        self.country = country
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.base_url = "https://api.crossref.org"
        self.headers = {
            "User-Agent": "OSINT-Foresight/1.0 (mailto:osint@example.com)"
        }

    def get_country_affiliations(self) -> list:
        """Get country-specific affiliation strings"""
        # Country-specific affiliations
        affiliations = {
            "AT": ["Austria", "Austrian", "Wien", "Vienna", "Graz", "Linz", "Salzburg", "Innsbruck"],
            "DE": ["Germany", "German", "Deutschland", "Berlin", "Munich", "München", "Hamburg", "Frankfurt"],
            "FR": ["France", "French", "Paris", "Lyon", "Marseille", "Toulouse", "CNRS", "INRIA"],
            "IT": ["Italy", "Italian", "Italia", "Rome", "Roma", "Milan", "Milano", "Turin", "Torino"],
            "ES": ["Spain", "Spanish", "España", "Madrid", "Barcelona", "Valencia", "Sevilla", "CSIC"],
            "NL": ["Netherlands", "Dutch", "Nederland", "Amsterdam", "Rotterdam", "Utrecht", "Eindhoven"],
            "PL": ["Poland", "Polish", "Polska", "Warsaw", "Warszawa", "Krakow", "Kraków", "Wrocław"],
            "SE": ["Sweden", "Swedish", "Sverige", "Stockholm", "Gothenburg", "Göteborg", "Uppsala"],
            "NO": ["Norway", "Norwegian", "Norge", "Oslo", "Bergen", "Trondheim", "NTNU"],
            "CH": ["Switzerland", "Swiss", "Schweiz", "Suisse", "Zurich", "Zürich", "Geneva", "ETH", "EPFL"],
            "GB": ["United Kingdom", "UK", "Britain", "British", "England", "London", "Oxford", "Cambridge"],
        }
        return affiliations.get(self.country, [self.country])

    def pull_publications(self, since_date: str = None, limit: int = 1000):
        """Pull publications from Crossref"""
        logger.info(f"Pulling publications for {self.country} since {since_date}")

        if not since_date:
            since_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        affiliations = self.get_country_affiliations()
        all_results = []

        for affiliation in affiliations[:3]:  # Limit affiliations for testing
            query_params = {
                "query.affiliation": affiliation,
                "filter": f"from-pub-date:{since_date}",
                "rows": 100,
                "cursor": "*"
            }

            total_results = 0
            while total_results < limit:
                try:
                    response = requests.get(
                        f"{self.base_url}/works",
                        params=query_params,
                        headers=self.headers,
                        timeout=30
                    )

                    if response.status_code == 200:
                        data = response.json()
                        items = data.get("message", {}).get("items", [])

                        if not items:
                            break

                        all_results.extend(items)
                        total_results += len(items)

                        # Get next cursor
                        next_cursor = data.get("message", {}).get("next-cursor")
                        if not next_cursor:
                            break

                        query_params["cursor"] = next_cursor

                        # Rate limiting
                        time.sleep(0.1)

                    else:
                        logger.error(f"API error: {response.status_code}")
                        break

                except Exception as e:
                    logger.error(f"Error pulling publications: {e}")
                    break

            logger.info(f"Found {len(all_results)} publications for {affiliation}")

        # Save results
        if all_results:
            output_file = self.output_dir / f"publications_{datetime.now().strftime('%Y%m%d')}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(all_results, f, indent=2, ensure_ascii=False)

            logger.info(f"Saved {len(all_results)} publications to {output_file}")

        return len(all_results)

    def pull_events(self, since_date: str = None):
        """Pull event data from Crossref"""
        logger.info(f"Pulling events for {self.country}")

        # Events endpoint for tracking citations, mentions, etc.
        events_url = f"{self.base_url}/events"

        query_params = {
            "rows": 100,
            "cursor": "*"
        }

        if since_date:
            query_params["from-occurred-date"] = since_date

        all_events = []

        try:
            response = requests.get(
                events_url,
                params=query_params,
                headers=self.headers,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                events = data.get("message", {}).get("events", [])
                all_events.extend(events)

                # Save events
                if all_events:
                    output_file = self.output_dir / f"events_{datetime.now().strftime('%Y%m%d')}.json"
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(all_events, f, indent=2, ensure_ascii=False)

                    logger.info(f"Saved {len(all_events)} events to {output_file}")

        except Exception as e:
            logger.error(f"Error pulling events: {e}")

        return len(all_events)


def main():
    parser = argparse.ArgumentParser(description="Pull Crossref data")
    parser.add_argument("--country", required=True, help="Country code (e.g., AT, DE)")
    parser.add_argument("--output", required=True, help="Output directory")
    parser.add_argument("--since", help="Pull data since date (YYYY-MM-DD)")
    parser.add_argument("--limit", type=int, default=1000, help="Maximum publications to pull")

    args = parser.parse_args()

    puller = CrossrefPuller(args.country, args.output)

    # Pull publications
    pub_count = puller.pull_publications(args.since, args.limit)

    # Pull events
    event_count = puller.pull_events(args.since)

    logger.info(f"Pull complete: {pub_count} publications, {event_count} events")


if __name__ == "__main__":
    main()

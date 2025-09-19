"""
CrossRef Events API Collector for Conference Intelligence
Tracks conference attendance and subsequent technology progression
"""

import os
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CrossRefEventsCollector:
    """Collect conference and event data from CrossRef Events API"""

    def __init__(self):
        self.base_url = "https://api.eventdata.crossref.org/v1/events"
        self.email = os.getenv("CONTACT_EMAIL", "research@osint.org")

        # Headers with polite contact
        self.headers = {
            "User-Agent": f"OSINT-Foresight/1.0 (mailto:{self.email})"
        }

        # Output directory
        self.output_dir = Path("F:/OSINT_DATA/conferences")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Target organizations and keywords
        self.italy_orgs = [
            "Leonardo", "Finmeccanica", "Politecnico di Milano",
            "Sapienza", "CNR", "ENEA", "IIT", "Alenia", "Selex"
        ]

        self.china_orgs = [
            "Chinese Academy", "Tsinghua", "Beihang", "Harbin Institute",
            "Beijing Institute", "Zhejiang", "Huawei", "ZTE"
        ]

        self.tech_keywords = [
            "aerospace", "defense", "quantum", "artificial intelligence",
            "5G", "6G", "hypersonic", "UAV", "satellite", "radar"
        ]

    def fetch_events(self,
                    from_date: str = None,
                    until_date: str = None,
                    source: str = None,
                    obj_id: Optional[str] = None) -> List[Dict]:
        """
        Fetch events from CrossRef Events API

        Args:
            from_date: Start date (YYYY-MM-DD)
            until_date: End date (YYYY-MM-DD)
            source: Event source (e.g., 'twitter', 'reddit', 'wikipedia')
            obj_id: DOI or other identifier

        Returns:
            List of events
        """

        params = {
            "mailto": self.email,
            "rows": 1000
        }

        if from_date:
            params["from-occurred-date"] = from_date
        if until_date:
            params["until-occurred-date"] = until_date
        if source:
            params["source"] = source
        if obj_id:
            params["obj-id"] = obj_id

        all_events = []
        cursor = None

        while True:
            if cursor:
                params["cursor"] = cursor

            try:
                response = requests.get(
                    self.base_url,
                    headers=self.headers,
                    params=params,
                    timeout=30
                )
                response.raise_for_status()

                data = response.json()
                events = data.get("message", {}).get("events", [])
                all_events.extend(events)

                # Check for more pages
                cursor = data.get("message", {}).get("next-cursor")
                if not cursor or len(events) == 0:
                    break

                # Rate limiting
                time.sleep(0.5)

            except Exception as e:
                logger.error(f"Error fetching events: {e}")
                break

        return all_events

    def analyze_conference_papers(self, doi_list: List[str]) -> Dict:
        """
        Analyze papers presented at conferences

        Args:
            doi_list: List of DOIs from conference

        Returns:
            Analysis of authors and institutions
        """

        analysis = {
            "total_papers": len(doi_list),
            "italy_papers": [],
            "china_papers": [],
            "collaborations": []
        }

        for doi in doi_list[:100]:  # Limit for demo
            # Fetch paper metadata from CrossRef
            try:
                response = requests.get(
                    f"https://api.crossref.org/works/{doi}",
                    headers=self.headers,
                    timeout=10
                )

                if response.status_code == 200:
                    paper = response.json().get("message", {})

                    # Check authors and affiliations
                    authors = paper.get("author", [])
                    title = paper.get("title", [""])[0]

                    italy_affiliated = False
                    china_affiliated = False

                    for author in authors:
                        affiliation = author.get("affiliation", [])
                        for aff in affiliation:
                            aff_name = aff.get("name", "").lower()

                            # Check for Italian institutions
                            for org in self.italy_orgs:
                                if org.lower() in aff_name:
                                    italy_affiliated = True
                                    break

                            # Check for Chinese institutions
                            for org in self.china_orgs:
                                if org.lower() in aff_name:
                                    china_affiliated = True
                                    break

                    # Categorize paper
                    if italy_affiliated and china_affiliated:
                        analysis["collaborations"].append({
                            "doi": doi,
                            "title": title,
                            "type": "Italy-China"
                        })
                    elif italy_affiliated:
                        analysis["italy_papers"].append({
                            "doi": doi,
                            "title": title
                        })
                    elif china_affiliated:
                        analysis["china_papers"].append({
                            "doi": doi,
                            "title": title
                        })

                time.sleep(0.1)  # Rate limiting

            except Exception as e:
                logger.debug(f"Could not fetch metadata for {doi}: {e}")

        return analysis

    def find_tech_conferences(self,
                             start_date: str = "2020-01-01",
                             end_date: str = None) -> Dict:
        """
        Find technology conferences with Italy-China participation

        Args:
            start_date: Start date for search
            end_date: End date for search

        Returns:
            Conference intelligence
        """

        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")

        logger.info(f"Searching for conferences from {start_date} to {end_date}")

        results = {
            "search_period": {
                "start": start_date,
                "end": end_date
            },
            "conferences": [],
            "italy_china_events": [],
            "high_risk_conferences": []
        }

        # Search for events mentioning our keywords
        for keyword in self.tech_keywords[:5]:  # Limit for demo
            logger.info(f"Searching for '{keyword}' conferences...")

            events = self.fetch_events(
                from_date=start_date,
                until_date=end_date
            )

            for event in events:
                # Check if event mentions our organizations
                event_data = json.dumps(event).lower()

                italy_mentioned = any(org.lower() in event_data for org in self.italy_orgs)
                china_mentioned = any(org.lower() in event_data for org in self.china_orgs)

                if italy_mentioned or china_mentioned:
                    conf_entry = {
                        "event_id": event.get("id"),
                        "occurred_at": event.get("occurred_at"),
                        "source": event.get("source_id"),
                        "relation_type": event.get("relation_type_id"),
                        "italy_present": italy_mentioned,
                        "china_present": china_mentioned,
                        "keyword": keyword
                    }

                    if italy_mentioned and china_mentioned:
                        results["italy_china_events"].append(conf_entry)

                        # Check if high-risk based on keywords
                        if any(risk_word in keyword.lower() for risk_word in ["quantum", "defense", "5g", "hypersonic"]):
                            results["high_risk_conferences"].append(conf_entry)

                    results["conferences"].append(conf_entry)

        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"crossref_conferences_{timestamp}.json"

        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)

        logger.info(f"Found {len(results['conferences'])} relevant conferences")
        logger.info(f"Italy-China events: {len(results['italy_china_events'])}")
        logger.info(f"High-risk conferences: {len(results['high_risk_conferences'])}")
        logger.info(f"Results saved to {output_file}")

        return results

    def track_conference_to_patent(self, conference_data: Dict) -> Dict:
        """
        Track progression from conference to patent filings

        Args:
            conference_data: Conference information

        Returns:
            Patent filing analysis
        """

        # This would integrate with USPTO/EPO APIs
        # For now, return structure

        return {
            "conference": conference_data,
            "patent_search_window": "24_months",
            "patents_found": [],
            "technology_transfer_indicators": []
        }


if __name__ == "__main__":
    collector = CrossRefEventsCollector()

    # Find recent conferences
    print("Searching for Italy-China technology conferences...")
    conferences = collector.find_tech_conferences(
        start_date="2023-01-01",
        end_date="2024-12-31"
    )

    print(f"\nAnalysis complete. Results saved to F:/OSINT_DATA/conferences/")

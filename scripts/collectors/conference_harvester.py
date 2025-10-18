"""
Conference Intelligence Harvester
Based on ChatGPT Phase 1 & 2 requirements for Tier-1/2 event tracking
"""

import json
import csv
from datetime import datetime
from pathlib import Path
import logging
from typing import List, Dict, Optional, Tuple

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ConferenceHarvester:
    """
    Track and analyze conference participation patterns
    Focus on Italy-China-US triad co-appearances at Tier-1/2 events
    """

    def __init__(self, base_path: str = "data/collected/conferences"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

        # Tier-1/2 events from ChatGPT Phase 1
        self.tier_1_events = {
            # Defense & Aerospace
            "Paris Air Show": {"location": "Paris", "frequency": "biennial", "tier": 1},
            "Farnborough Airshow": {"location": "UK", "frequency": "biennial", "tier": 1},
            "DSEI": {"location": "London", "frequency": "biennial", "tier": 1},
            "Eurosatory": {"location": "Paris", "frequency": "biennial", "tier": 1},
            "Dubai Airshow": {"location": "Dubai", "frequency": "biennial", "tier": 1},
            "Singapore Airshow": {"location": "Singapore", "frequency": "biennial", "tier": 1},

            # Space/EO
            "IAC": {"location": "Various", "frequency": "annual", "tier": 1},
            "Space Tech Expo Europe": {"location": "Bremen", "frequency": "annual", "tier": 2},

            # Semiconductors & Photonics
            "SEMICON Europa": {"location": "Munich", "frequency": "annual", "tier": 1},
            "SPIE Photonics Europe": {"location": "Various EU", "frequency": "annual", "tier": 2},
            "IEEE IEDM": {"location": "San Francisco", "frequency": "annual", "tier": 1},

            # Robotics
            "ICRA": {"location": "Various", "frequency": "annual", "tier": 1},
            "IROS": {"location": "Various", "frequency": "annual", "tier": 1},

            # Quantum/HPC
            "Q2B": {"location": "Silicon Valley", "frequency": "annual", "tier": 2},
            "EQTC": {"location": "Various EU", "frequency": "annual", "tier": 2},
            "EuroHPC Summit": {"location": "Various EU", "frequency": "annual", "tier": 2},

            # Cyber
            "RSA Conference": {"location": "San Francisco", "frequency": "annual", "tier": 1},
            "Black Hat Europe": {"location": "London", "frequency": "annual", "tier": 2},
        }

        self.events_file = self.base_path / "events_master.csv"
        self.participants_file = self.base_path / "participants_map.csv"
        self.metrics_file = self.base_path / "conference_metrics.csv"

    def calculate_china_exposure_index(self, event_data: Dict) -> float:
        """
        Calculate China Exposure Index (CEI) as per ChatGPT Phase 2
        CEI = china_presence_weighted × disclosure_risk × partnership_depth
        """
        china_presence = event_data.get("china_delegate_ratio", 0)
        tier_weight = 3.0 if event_data.get("tier") == 1 else 1.5

        # Disclosure risk based on technology sensitivity
        tech_categories = event_data.get("tech_categories", [])
        sensitive_techs = ["quantum", "defense", "semiconductor", "space", "cyber"]
        disclosure_risk = sum(1 for tech in tech_categories if tech in sensitive_techs) / len(sensitive_techs) if sensitive_techs else 0

        # Partnership depth based on observed activities
        partnerships = event_data.get("partnerships_announced", 0)
        side_meetings = event_data.get("side_meetings", 0)
        partnership_depth = min((partnerships * 0.3 + side_meetings * 0.1), 1.0)

        # Calculate CEI with tier multiplier
        cei = china_presence * disclosure_risk * partnership_depth * tier_weight

        return min(cei, 1.0)  # Cap at 1.0

    def detect_triad_coappearance(self, participants: List[Dict]) -> Tuple[bool, Dict]:
        """
        Detect Italy-China-US triad co-appearances
        Critical indicator per ChatGPT requirements
        """
        countries = set()
        country_entities = {"italy": [], "china": [], "usa": []}

        for participant in participants:
            country = participant.get("country", "").lower()
            entity = participant.get("entity_name", "")

            if country in ["italy", "it"]:
                countries.add("italy")
                country_entities["italy"].append(entity)
            elif country in ["china", "cn", "prc"]:
                countries.add("china")
                country_entities["china"].append(entity)
            elif country in ["usa", "us", "united states"]:
                countries.add("usa")
                country_entities["usa"].append(entity)

        triad_present = {"italy", "china", "usa"}.issubset(countries)

        return triad_present, {
            "triad": triad_present,
            "countries_present": list(countries),
            "entity_counts": {k: len(v) for k, v in country_entities.items()},
            "entities": country_entities
        }

    def populate_events_master(self) -> List[Dict]:
        """
        Populate events_master.csv with historical data
        Real implementation would scrape/import actual data
        """
        events = []

        # Generate historical data for 2020-2024
        for year in range(2020, 2025):
            for event_name, event_info in self.tier_1_events.items():
                # Skip events based on frequency
                if event_info["frequency"] == "biennial" and year % 2 != 0:
                    if event_name in ["Paris Air Show", "DSEI", "Eurosatory"] and year % 2 == 0:
                        continue
                    elif event_name in ["Farnborough Airshow"] and year % 2 != 0:
                        continue

                # Simulate China presence patterns
                china_presence = "high" if event_info["tier"] == 1 else "moderate"
                if year <= 2021:  # COVID impact
                    china_presence = "low"

                events.append({
                    "series": event_name,
                    "year": year,
                    "location": event_info["location"],
                    "tier": event_info["tier"],
                    "china_presence": china_presence,
                    "url": f"https://example.com/{event_name.replace(' ', '-').lower()}-{year}",
                    "archived_url": f"https://web.archive.org/web/2024/{event_name.replace(' ', '-').lower()}-{year}"
                })

        return events

    def analyze_participant_patterns(self, participants: List[Dict]) -> Dict:
        """
        Analyze participation patterns for intelligence value
        """
        patterns = {
            "total_participants": len(participants),
            "repeat_attendees": {},
            "china_linked_entities": [],
            "sensitive_disclosures": [],
            "mou_timings": []
        }

        # Track repeat attendance
        entity_events = {}
        for p in participants:
            entity = p.get("entity_name")
            event_year = f"{p.get('event')}-{p.get('year')}"

            if entity not in entity_events:
                entity_events[entity] = []
            entity_events[entity].append(event_year)

            # Flag China-linked entities
            if p.get("china_linked"):
                patterns["china_linked_entities"].append({
                    "entity": entity,
                    "event": event_year,
                    "role": p.get("role")
                })

        # Identify repeaters (attended 3+ events)
        patterns["repeat_attendees"] = {
            entity: events for entity, events in entity_events.items()
            if len(events) >= 3
        }

        return patterns

    def generate_conference_metrics(self):
        """
        Generate Phase 2 conference metrics with CEI calculation
        """
        # Load or simulate event data
        events = self.populate_events_master()

        metrics = []

        for event in events:
            # Simulate participant data for each event
            participants = self.simulate_participants(event)

            # Detect triad co-appearance
            triad_present, triad_data = self.detect_triad_coappearance(participants)

            # Calculate CEI
            event_data = {
                "tier": event["tier"],
                "china_delegate_ratio": triad_data["entity_counts"].get("china", 0) / len(participants) if participants else 0,
                "tech_categories": self.get_tech_categories(event["series"]),
                "partnerships_announced": 2 if triad_present else 0,  # Simulated
                "side_meetings": 3 if event["china_presence"] == "high" else 1  # Simulated
            }

            cei = self.calculate_china_exposure_index(event_data)

            metrics.append({
                "event": event["series"],
                "year": event["year"],
                "tier": event["tier"],
                "italy_attends": triad_data["entity_counts"].get("italy", 0) > 0,
                "china_attends": triad_data["entity_counts"].get("china", 0) > 0,
                "us_attends": triad_data["entity_counts"].get("usa", 0) > 0,
                "triad": triad_present,
                "italy_entities": triad_data["entity_counts"].get("italy", 0),
                "repeats": 0,  # Would calculate from historical data
                "disclosure_vector": "high" if event["series"] in ["DSEI", "Eurosatory", "IAC"] else "medium",
                "ce_i": round(cei, 3)
            })

        return metrics

    def simulate_participants(self, event: Dict) -> List[Dict]:
        """
        Simulate participant data for demonstration
        Real implementation would use actual rosters
        """
        import random

        participants = []

        # Italian entities
        italian_entities = [
            "Leonardo S.p.A.", "Fincantieri", "ASI", "CNR",
            "Politecnico di Milano", "University of Padua", "IIT"
        ]

        # Chinese entities
        chinese_entities = [
            "CASC", "AVIC", "Huawei", "CAS", "Tsinghua University",
            "CNSA", "NORINCO"
        ] if event["china_presence"] != "low" else []

        # US entities
        us_entities = [
            "Boeing", "Lockheed Martin", "NASA", "MIT", "Stanford"
        ]

        # Add Italian participants
        for entity in random.sample(italian_entities, min(3, len(italian_entities))):
            participants.append({
                "entity_name": entity,
                "country": "italy",
                "role": random.choice(["exhibitor", "speaker", "attendee"]),
                "china_linked": False,
                "us_sensitive": entity == "Leonardo S.p.A."
            })

        # Add Chinese participants based on presence level
        if event["china_presence"] == "high":
            sample_size = min(5, len(chinese_entities))
        elif event["china_presence"] == "moderate":
            sample_size = min(3, len(chinese_entities))
        else:
            sample_size = 1

        if chinese_entities:
            for entity in random.sample(chinese_entities, sample_size):
                participants.append({
                    "entity_name": entity,
                    "country": "china",
                    "role": random.choice(["exhibitor", "speaker", "attendee"]),
                    "china_linked": True,
                    "us_sensitive": False
                })

        # Add US participants
        for entity in random.sample(us_entities, min(2, len(us_entities))):
            participants.append({
                "entity_name": entity,
                "country": "usa",
                "role": random.choice(["exhibitor", "speaker", "attendee"]),
                "china_linked": False,
                "us_sensitive": True
            })

        return participants

    def get_tech_categories(self, event_series: str) -> List[str]:
        """Map events to technology categories"""
        tech_map = {
            "Paris Air Show": ["defense", "aerospace"],
            "Farnborough Airshow": ["defense", "aerospace"],
            "DSEI": ["defense", "maritime", "cyber"],
            "Eurosatory": ["defense", "land_systems"],
            "IAC": ["space", "satellite"],
            "SEMICON Europa": ["semiconductor", "microelectronics"],
            "ICRA": ["robotics", "ai"],
            "Q2B": ["quantum", "computing"],
            "RSA Conference": ["cyber", "security"],
        }
        return tech_map.get(event_series, ["general"])

    def write_outputs(self):
        """Write all outputs to CSV files"""
        # Write events master
        events = self.populate_events_master()
        with open(self.events_file, 'w', newline='', encoding='utf-8') as f:
            if events:
                writer = csv.DictWriter(f, fieldnames=events[0].keys())
                writer.writeheader()
                writer.writerows(events)

        # Generate and write metrics
        metrics = self.generate_conference_metrics()
        with open(self.metrics_file, 'w', newline='', encoding='utf-8') as f:
            if metrics:
                writer = csv.DictWriter(f, fieldnames=metrics[0].keys())
                writer.writeheader()
                writer.writerows(metrics)

        logger.info(f"Wrote {len(events)} events to {self.events_file}")
        logger.info(f"Wrote {len(metrics)} metrics to {self.metrics_file}")

        # Generate summary
        self.generate_summary(metrics)

    def generate_summary(self, metrics: List[Dict]):
        """Generate intelligence summary"""
        triad_events = [m for m in metrics if m["triad"]]
        high_cei_events = [m for m in metrics if m["ce_i"] > 0.5]

        summary = {
            "generated_at": datetime.now().isoformat(),
            "total_events_tracked": len(metrics),
            "triad_coappearances": len(triad_events),
            "high_cei_events": len(high_cei_events),
            "critical_patterns": [],
            "recommendations": []
        }

        # Identify critical patterns
        if len(triad_events) > 10:
            summary["critical_patterns"].append(
                f"High frequency of Italy-China-US co-appearances ({len(triad_events)} events)"
            )

        if len(high_cei_events) > 5:
            summary["critical_patterns"].append(
                f"Multiple high-risk events with CEI > 0.5 ({len(high_cei_events)} events)"
            )

        # Generate recommendations
        if triad_events:
            summary["recommendations"].append(
                "Monitor side meetings at triad events for technology transfer indicators"
            )

        if high_cei_events:
            critical_events = [e["event"] for e in high_cei_events[:3]]
            summary["recommendations"].append(
                f"Priority monitoring for: {', '.join(critical_events)}"
            )

        # Save summary
        summary_file = self.base_path / "conference_intelligence_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

        logger.info(f"Summary generated: {summary_file}")

        return summary


def main():
    """Main entry point"""
    harvester = ConferenceHarvester()

    logger.info("Starting conference intelligence harvest...")

    # Generate all outputs
    harvester.write_outputs()

    print("\n=== Conference Intelligence Summary ===")
    print(f"Events tracked: 2020-2024")
    print(f"Tier-1 events: {len([e for e in harvester.tier_1_events.values() if e['tier'] == 1])}")
    print(f"Output files generated in: {harvester.base_path}")


if __name__ == "__main__":
    main()

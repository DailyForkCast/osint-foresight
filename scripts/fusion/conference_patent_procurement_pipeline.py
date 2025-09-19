#!/usr/bin/env python3
"""
Conference→Patent→Procurement Fusion Pipeline
Tracks technology progression from conference disclosure to patent filing to procurement contracts
"""

import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import requests
import time
import yaml
from dataclasses import dataclass

# Import existing clients
import sys
sys.path.append("C:/Projects/OSINT - Foresight/src/pulls")
from uspto_client import USPTOClient
from ted_pull import TEDClient

@dataclass
class ConferenceEvent:
    """Conference event data structure"""
    event_uid: str
    name: str
    date: datetime
    location: str
    participants: List[str]
    technologies: List[Dict[str, Any]]
    china_presence: bool
    tier: int

@dataclass
class PatentMatch:
    """Patent matching data structure"""
    patent_number: str
    title: str
    filing_date: datetime
    assignee: str
    technology_keywords: List[str]
    conference_correlation_score: float
    china_inventors: bool

@dataclass
class ProcurementMatch:
    """Procurement contract data structure"""
    contract_id: str
    buyer: str
    supplier: str
    amount: float
    description: str
    award_date: datetime
    patent_correlation_score: float
    cpv_codes: List[str]

class ConferencePatentProcurementPipeline:
    """Main fusion pipeline for Conference→Patent→Procurement analysis"""

    def __init__(self, config_path: str = None):
        """Initialize the fusion pipeline"""
        if config_path is None:
            config_path = "C:/Projects/OSINT - Foresight/config/fusion_config.yaml"

        # Load configuration
        self.config = self._load_config(config_path)

        # Initialize API clients
        self.uspto_client = USPTOClient()
        self.ted_client = TEDClient()

        # Data storage paths
        self.data_dir = Path("F:/fusion_data/conference_patent_procurement")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Temporal windows for correlation
        self.conf_to_patent_window = (6, 24)  # 6-24 months
        self.patent_to_procurement_window = (12, 36)  # 12-36 months

    def _load_config(self, config_path: str) -> Dict:
        """Load fusion pipeline configuration"""
        default_config = {
            "technology_keywords": {
                "ai_ml": ["artificial intelligence", "machine learning", "neural network", "deep learning"],
                "quantum": ["quantum computing", "quantum cryptography", "quantum sensor"],
                "aerospace": ["aircraft", "helicopter", "drone", "aviation", "aerospace"],
                "defense": ["defense", "military", "combat", "weapon", "missile"],
                "cyber": ["cybersecurity", "cyber defense", "intrusion detection", "encryption"],
                "semiconductors": ["semiconductor", "microprocessor", "chip", "silicon"]
            },
            "confidence_thresholds": {
                "technology_matching": 0.75,
                "temporal_correlation": 0.70,
                "entity_resolution": 0.80
            },
            "china_indicators": [
                "china", "chinese", "prc", "peoples republic", "beijing", "shanghai",
                "tsinghua", "peking university", "cas", "academy of sciences"
            ]
        }

        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                # Merge with defaults
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
        except FileNotFoundError:
            print(f"Config file not found at {config_path}, using defaults")
            return default_config

    def extract_conference_technologies(self, event_uid: str) -> ConferenceEvent:
        """Extract technology mentions from conference proceedings"""

        # Load conference data from existing collectors
        conference_data_path = f"F:/conference_data/{event_uid}.json"

        try:
            with open(conference_data_path, 'r') as f:
                raw_data = json.load(f)

            # Extract technologies using keyword matching
            technologies = []
            for tech_category, keywords in self.config['technology_keywords'].items():
                mentions = []
                for keyword in keywords:
                    # Search in titles, abstracts, presentation content
                    if any(keyword.lower() in text.lower() for text in raw_data.get('content', [])):
                        mentions.append({
                            'keyword': keyword,
                            'category': tech_category,
                            'confidence': self._calculate_keyword_confidence(keyword, raw_data)
                        })

                if mentions:
                    technologies.append({
                        'category': tech_category,
                        'mentions': mentions,
                        'relevance_score': np.mean([m['confidence'] for m in mentions])
                    })

            # Check for China presence
            china_presence = any(
                indicator.lower() in ' '.join(raw_data.get('participants', [])).lower()
                for indicator in self.config['china_indicators']
            )

            return ConferenceEvent(
                event_uid=event_uid,
                name=raw_data.get('name', 'Unknown'),
                date=datetime.fromisoformat(raw_data.get('date', '2024-01-01')),
                location=raw_data.get('location', 'Unknown'),
                participants=raw_data.get('participants', []),
                technologies=technologies,
                china_presence=china_presence,
                tier=raw_data.get('tier', 2)
            )

        except FileNotFoundError:
            print(f"Conference data not found for {event_uid}")
            return None

    def _calculate_keyword_confidence(self, keyword: str, data: Dict) -> float:
        """Calculate confidence score for keyword mention"""
        content_texts = data.get('content', [])
        if not content_texts:
            return 0.0

        # Simple frequency-based confidence
        total_mentions = sum(text.lower().count(keyword.lower()) for text in content_texts)
        total_words = sum(len(text.split()) for text in content_texts)

        if total_words == 0:
            return 0.0

        # Normalize and cap at 1.0
        confidence = min(total_mentions / total_words * 1000, 1.0)
        return confidence

    def search_patents_by_conference(self, conference_event: ConferenceEvent) -> List[PatentMatch]:
        """Search for patents filed after conference by participants"""
        if not conference_event:
            return []

        patent_matches = []

        # Define search window
        start_date = conference_event.date + timedelta(days=30 * self.conf_to_patent_window[0])
        end_date = conference_event.date + timedelta(days=30 * self.conf_to_patent_window[1])

        # Search for each participant
        for participant in conference_event.participants:
            try:
                # Search USPTO
                patents = self.uspto_client.search_patents(
                    assignee=participant,
                    date_range=(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")),
                    limit=100
                )

                if not patents.empty:
                    for _, patent in patents.iterrows():
                        # Calculate technology correlation
                        correlation_score = self._calculate_technology_correlation(
                            patent, conference_event.technologies
                        )

                        if correlation_score > self.config['confidence_thresholds']['technology_matching']:
                            # Check for China inventors
                            china_inventors = self._check_china_inventors(patent)

                            patent_matches.append(PatentMatch(
                                patent_number=patent.get('patent_number', ''),
                                title=patent.get('patent_title', ''),
                                filing_date=datetime.strptime(patent.get('patent_date', '2024-01-01'), '%Y-%m-%d'),
                                assignee=patent.get('assignee_organization', ''),
                                technology_keywords=self._extract_patent_keywords(patent),
                                conference_correlation_score=correlation_score,
                                china_inventors=china_inventors
                            ))

                # Rate limiting
                time.sleep(2)

            except Exception as e:
                print(f"Error searching patents for {participant}: {e}")
                continue

        return patent_matches

    def _calculate_technology_correlation(self, patent: pd.Series, conference_technologies: List[Dict]) -> float:
        """Calculate correlation between patent and conference technologies"""
        if not conference_technologies:
            return 0.0

        patent_text = f"{patent.get('patent_title', '')} {patent.get('patent_abstract', '')}".lower()

        total_score = 0.0
        total_weight = 0.0

        for tech in conference_technologies:
            tech_weight = tech.get('relevance_score', 0.5)
            tech_score = 0.0

            for mention in tech.get('mentions', []):
                keyword = mention['keyword'].lower()
                if keyword in patent_text:
                    tech_score += mention.get('confidence', 0.5)

            # Normalize by number of mentions
            if tech.get('mentions'):
                tech_score /= len(tech['mentions'])

            total_score += tech_score * tech_weight
            total_weight += tech_weight

        if total_weight == 0:
            return 0.0

        return min(total_score / total_weight, 1.0)

    def _check_china_inventors(self, patent: pd.Series) -> bool:
        """Check if patent has Chinese inventors"""
        inventor_country = patent.get('inventor_country', '')
        if inventor_country == 'CN':
            return True

        # Check other fields for China indicators
        assignee = patent.get('assignee_organization', '').lower()
        return any(indicator in assignee for indicator in self.config['china_indicators'])

    def _extract_patent_keywords(self, patent: pd.Series) -> List[str]:
        """Extract relevant keywords from patent"""
        title = patent.get('patent_title', '')
        abstract = patent.get('patent_abstract', '')

        # Simple keyword extraction (can be enhanced with NLP)
        keywords = []
        for category, keyword_list in self.config['technology_keywords'].items():
            for keyword in keyword_list:
                if keyword.lower() in f"{title} {abstract}".lower():
                    keywords.append(keyword)

        return list(set(keywords))

    def search_procurement_by_patents(self, patent_matches: List[PatentMatch]) -> List[ProcurementMatch]:
        """Search for procurement contracts related to patent technologies"""
        procurement_matches = []

        for patent in patent_matches:
            try:
                # Define search window
                start_date = patent.filing_date + timedelta(days=30 * self.patent_to_procurement_window[0])
                end_date = patent.filing_date + timedelta(days=30 * self.patent_to_procurement_window[1])

                # Search TED database
                contracts = self.ted_client.search_contracts(
                    keywords=patent.technology_keywords,
                    supplier=patent.assignee,
                    date_range=(start_date, end_date)
                )

                for contract in contracts:
                    correlation_score = self._calculate_patent_procurement_correlation(
                        patent, contract
                    )

                    if correlation_score > self.config['confidence_thresholds']['technology_matching']:
                        procurement_matches.append(ProcurementMatch(
                            contract_id=contract.get('id', ''),
                            buyer=contract.get('buyer', ''),
                            supplier=contract.get('supplier', ''),
                            amount=contract.get('amount', 0.0),
                            description=contract.get('description', ''),
                            award_date=contract.get('award_date'),
                            patent_correlation_score=correlation_score,
                            cpv_codes=contract.get('cpv_codes', [])
                        ))

                # Rate limiting
                time.sleep(1)

            except Exception as e:
                print(f"Error searching procurement for patent {patent.patent_number}: {e}")
                continue

        return procurement_matches

    def _calculate_patent_procurement_correlation(self, patent: PatentMatch, contract: Dict) -> float:
        """Calculate correlation between patent and procurement contract"""
        contract_text = f"{contract.get('description', '')} {contract.get('title', '')}".lower()

        keyword_matches = 0
        total_keywords = len(patent.technology_keywords)

        if total_keywords == 0:
            return 0.0

        for keyword in patent.technology_keywords:
            if keyword.lower() in contract_text:
                keyword_matches += 1

        return keyword_matches / total_keywords

    def calculate_fusion_confidence(self, conference: ConferenceEvent,
                                  patents: List[PatentMatch],
                                  procurement: List[ProcurementMatch]) -> Dict[str, float]:
        """Calculate overall confidence metrics for the fusion pipeline"""

        # Temporal consistency
        temporal_score = 0.0
        if patents and conference:
            valid_temporal = 0
            for patent in patents:
                days_diff = (patent.filing_date - conference.date).days
                if self.conf_to_patent_window[0] * 30 <= days_diff <= self.conf_to_patent_window[1] * 30:
                    valid_temporal += 1
            temporal_score = valid_temporal / len(patents) if patents else 0.0

        # Technology correlation
        tech_correlation = np.mean([p.conference_correlation_score for p in patents]) if patents else 0.0

        # Procurement correlation
        proc_correlation = np.mean([p.patent_correlation_score for p in procurement]) if procurement else 0.0

        # Overall confidence
        overall_confidence = np.mean([temporal_score, tech_correlation, proc_correlation])

        return {
            "temporal_consistency": temporal_score,
            "technology_correlation": tech_correlation,
            "procurement_correlation": proc_correlation,
            "overall_confidence": overall_confidence
        }

    def calculate_china_exposure_vector(self, conference: ConferenceEvent,
                                      patents: List[PatentMatch],
                                      procurement: List[ProcurementMatch]) -> Dict[str, Any]:
        """Calculate China exposure across the entire pipeline"""

        exposure_vector = {
            "conference_china_presence": conference.china_presence if conference else False,
            "patents_with_china_inventors": sum(1 for p in patents if p.china_inventors),
            "total_patents": len(patents),
            "procurement_with_china_suppliers": 0,  # Would need to implement China supplier detection
            "total_procurement": len(procurement),
            "exposure_score": 0.0
        }

        # Calculate overall exposure score
        exposure_factors = []

        if conference and conference.china_presence:
            exposure_factors.append(0.3)  # Conference exposure weight

        if patents:
            china_patent_ratio = exposure_vector["patents_with_china_inventors"] / len(patents)
            exposure_factors.append(china_patent_ratio * 0.4)  # Patent exposure weight

        # Procurement China exposure would be calculated here

        exposure_vector["exposure_score"] = sum(exposure_factors)

        return exposure_vector

    def run_pipeline(self, event_uid: str) -> Dict[str, Any]:
        """Execute the complete Conference→Patent→Procurement fusion pipeline"""

        print(f"Running Conference→Patent→Procurement pipeline for {event_uid}")

        # Stage 1: Extract conference technologies
        print("Stage 1: Extracting conference technologies...")
        conference = self.extract_conference_technologies(event_uid)

        if not conference:
            return {"error": f"No conference data found for {event_uid}"}

        # Stage 2: Search for related patents
        print("Stage 2: Searching for related patents...")
        patents = self.search_patents_by_conference(conference)

        # Stage 3: Search for related procurement
        print("Stage 3: Searching for related procurement...")
        procurement = self.search_procurement_by_patents(patents)

        # Stage 4: Calculate confidence metrics
        print("Stage 4: Calculating confidence metrics...")
        confidence_metrics = self.calculate_fusion_confidence(conference, patents, procurement)

        # Stage 5: Calculate China exposure
        print("Stage 5: Calculating China exposure vector...")
        china_exposure = self.calculate_china_exposure_vector(conference, patents, procurement)

        # Compile results
        results = {
            "pipeline": "conference_patent_procurement",
            "event_uid": event_uid,
            "conference": conference.__dict__ if conference else None,
            "patents": [p.__dict__ for p in patents],
            "procurement": [p.__dict__ for p in procurement],
            "confidence_metrics": confidence_metrics,
            "china_exposure_vector": china_exposure,
            "generated_at": datetime.now().isoformat(),
            "technology_progression_detected": len(patents) > 0 and len(procurement) > 0
        }

        # Save results
        self.save_results(results, event_uid)

        return results

    def save_results(self, results: Dict[str, Any], event_uid: str):
        """Save pipeline results to file"""
        output_path = self.data_dir / f"{event_uid}_fusion_results.json"

        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)

        print(f"Results saved to {output_path}")

def main():
    """Main execution function"""
    pipeline = ConferencePatentProcurementPipeline()

    # Example usage - process a conference event
    test_event_uid = "farnborough_2024"
    results = pipeline.run_pipeline(test_event_uid)

    print("\n" + "="*60)
    print("CONFERENCE→PATENT→PROCUREMENT FUSION RESULTS")
    print("="*60)

    if "error" not in results:
        print(f"Event: {results['event_uid']}")
        print(f"Patents found: {len(results['patents'])}")
        print(f"Procurement contracts found: {len(results['procurement'])}")
        print(f"Technology progression detected: {results['technology_progression_detected']}")
        print(f"Overall confidence: {results['confidence_metrics']['overall_confidence']:.2f}")
        print(f"China exposure score: {results['china_exposure_vector']['exposure_score']:.2f}")
    else:
        print(f"Error: {results['error']}")

if __name__ == "__main__":
    main()

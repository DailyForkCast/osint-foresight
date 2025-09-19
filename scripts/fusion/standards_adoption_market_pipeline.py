#!/usr/bin/env python3
"""
Standards→Adoption→Market_Position Fusion Pipeline
Tracks standards participation to market adoption to strategic position
"""

import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Set
from pathlib import Path
import requests
import time
import yaml
from dataclasses import dataclass, asdict
import xml.etree.ElementTree as ET
from collections import defaultdict

@dataclass
class StandardsParticipation:
    """Standards body participation data"""
    organization: str
    standards_body: str
    working_group: str
    role: str  # member, editor, chair, rapporteur
    standard_identifier: str
    standard_title: str
    participation_start: datetime
    participation_end: Optional[datetime]
    contribution_score: float  # 0-10 based on role weight

@dataclass
class StandardAdoption:
    """Market adoption tracking for standards"""
    standard_identifier: str
    adoption_metrics: Dict[str, Any]
    market_segments: List[str]
    adopting_organizations: List[str]
    adoption_timeline: List[Dict[str, Any]]
    china_adoption: bool
    competitive_standards: List[str]

@dataclass
class MarketPosition:
    """Market position analysis"""
    organization: str
    market_influence_score: float
    standards_leadership_areas: List[str]
    competitive_advantages: List[str]
    market_share_indicators: Dict[str, float]
    china_collaboration_risk: float
    strategic_vulnerabilities: List[str]

class StandardsAdoptionMarketPipeline:
    """Main fusion pipeline for Standards→Adoption→Market_Position analysis"""

    def __init__(self, config_path: str = None):
        """Initialize the standards adoption pipeline"""
        if config_path is None:
            config_path = "C:/Projects/OSINT - Foresight/config/fusion_config.yaml"

        # Load configuration
        self.config = self._load_config(config_path)

        # Data storage paths
        self.data_dir = Path("F:/fusion_data/standards_adoption_market")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Standards body APIs and endpoints
        self.standards_apis = {
            'etsi': {
                'base_url': 'https://www.etsi.org/standards',
                'api_url': 'https://www.etsi.org/standards-search',
                'working_groups_url': 'https://www.etsi.org/committee'
            },
            'ietf': {
                'base_url': 'https://datatracker.ietf.org/api/v1',
                'documents': 'https://datatracker.ietf.org/api/v1/doc/document/',
                'groups': 'https://datatracker.ietf.org/api/v1/group/group/',
                'persons': 'https://datatracker.ietf.org/api/v1/person/person/'
            },
            'ieee': {
                'base_url': 'https://standards.ieee.org',
                'search_url': 'https://ieeexplore.ieee.org/search/searchresult.jsp'
            },
            'iso': {
                'base_url': 'https://www.iso.org/standards-catalogue',
                'api_url': 'https://www.iso.org/obp/ui'
            },
            '3gpp': {
                'base_url': 'https://www.3gpp.org/specifications',
                'ftp_url': 'https://www.3gpp.org/ftp/Specs'
            }
        }

        # Role weight mapping for influence calculation
        self.role_weights = {
            'chair': 10,
            'vice-chair': 8,
            'rapporteur': 7,
            'editor': 6,
            'co-editor': 5,
            'contributor': 3,
            'member': 1,
            'observer': 0.5
        }

    def _load_config(self, config_path: str) -> Dict:
        """Load standards adoption pipeline configuration"""
        default_config = {
            "target_standards_bodies": [
                "ETSI", "IETF", "IEEE", "ISO", "IEC", "3GPP", "ITU", "W3C"
            ],
            "technology_domains": {
                "telecommunications": ["5G", "6G", "LTE", "cellular", "mobile"],
                "cybersecurity": ["security", "crypto", "authentication", "privacy"],
                "ai_ml": ["artificial intelligence", "machine learning", "neural"],
                "iot": ["internet of things", "IoT", "smart", "connected"],
                "quantum": ["quantum", "qkd", "quantum communication"],
                "automotive": ["automotive", "connected vehicle", "V2X"],
                "aerospace": ["aerospace", "aviation", "satellite", "space"]
            },
            "china_indicators": {
                "organizations": [
                    "Huawei", "ZTE", "China Mobile", "China Telecom", "China Unicom",
                    "Tencent", "Alibaba", "Baidu", "CAICT", "CCSA", "Lenovo",
                    "Xiaomi", "OPPO", "Vivo", "DJI", "BYD"
                ],
                "countries": ["CN", "China", "People's Republic of China"],
                "research_institutes": [
                    "Tsinghua University", "Peking University", "CAS",
                    "Chinese Academy of Sciences", "BUPT", "CAICT"
                ]
            },
            "adoption_indicators": {
                "implementation_keywords": [
                    "implementation", "deployment", "adopted", "compliant",
                    "certified", "conformance", "interoperability"
                ],
                "market_keywords": [
                    "product", "commercial", "market", "industry", "vendor",
                    "solution", "platform", "service"
                ]
            }
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

    def mine_standards_participation(self, org_ror: str) -> List[StandardsParticipation]:
        """Mine standards participation data for an organization"""

        participation_records = []

        # Load organization mapping to get alternative names
        org_names = self._get_organization_names(org_ror)

        # Search each standards body
        for body in self.config['target_standards_bodies']:
            body_participation = self._search_standards_body_participation(body.lower(), org_names)
            participation_records.extend(body_participation)

        return participation_records

    def _get_organization_names(self, org_ror: str) -> List[str]:
        """Get all known names and aliases for an organization"""
        org_mapping_path = f"F:/org_mappings/{org_ror}_names.json"

        try:
            with open(org_mapping_path, 'r') as f:
                mapping_data = json.load(f)
                return mapping_data.get('names', [mapping_data.get('primary_name', '')])
        except FileNotFoundError:
            # Fallback to extracting from ROR ID or other sources
            return [org_ror]  # Placeholder

    def _search_standards_body_participation(self, standards_body: str, org_names: List[str]) -> List[StandardsParticipation]:
        """Search for organization participation in a specific standards body"""

        participation = []

        if standards_body == 'ietf':
            participation = self._search_ietf_participation(org_names)
        elif standards_body == 'etsi':
            participation = self._search_etsi_participation(org_names)
        elif standards_body == 'ieee':
            participation = self._search_ieee_participation(org_names)
        elif standards_body == '3gpp':
            participation = self._search_3gpp_participation(org_names)
        # Add more standards bodies as needed

        return participation

    def _search_ietf_participation(self, org_names: List[str]) -> List[StandardsParticipation]:
        """Search IETF datatracker for organization participation"""
        participation = []

        try:
            # Search for documents authored by organization members
            for org_name in org_names:
                time.sleep(1)  # Rate limiting

                # Search for RFCs and Internet Drafts
                url = f"{self.standards_apis['ietf']['base_url']}/doc/document/"
                params = {
                    'format': 'json',
                    'limit': 100,
                    'author__person__name__icontains': org_name
                }

                response = requests.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()

                    for doc in data.get('objects', []):
                        # Extract participation details
                        participation_record = StandardsParticipation(
                            organization=org_name,
                            standards_body='IETF',
                            working_group=doc.get('group', {}).get('name', ''),
                            role='author',  # Default role for document authors
                            standard_identifier=doc.get('name', ''),
                            standard_title=doc.get('title', ''),
                            participation_start=datetime.fromisoformat(doc.get('time', '2020-01-01T00:00:00')),
                            participation_end=None,
                            contribution_score=self.role_weights.get('contributor', 3)
                        )
                        participation.append(participation_record)

        except Exception as e:
            print(f"Error searching IETF participation: {e}")

        return participation

    def _search_etsi_participation(self, org_names: List[str]) -> List[StandardsParticipation]:
        """Search ETSI for organization participation"""
        # ETSI requires more complex scraping as they don't have a public API
        # This would be implemented with web scraping techniques
        return []

    def _search_ieee_participation(self, org_names: List[str]) -> List[StandardsParticipation]:
        """Search IEEE for organization participation"""
        # IEEE participation would require access to IEEE Xplore or membership data
        return []

    def _search_3gpp_participation(self, org_names: List[str]) -> List[StandardsParticipation]:
        """Search 3GPP for organization participation"""
        # 3GPP maintains membership lists and working group participation
        return []

    def track_market_adoption(self, standard_identifier: str, monitoring_period: int = 36) -> StandardAdoption:
        """Track market adoption of a specific standard"""

        # Search for adoption indicators across multiple sources
        adoption_data = {
            'implementations': self._search_standard_implementations(standard_identifier),
            'certifications': self._search_standard_certifications(standard_identifier),
            'market_mentions': self._search_market_mentions(standard_identifier),
            'competitive_analysis': self._analyze_competitive_standards(standard_identifier)
        }

        # Analyze adoption timeline
        adoption_timeline = self._build_adoption_timeline(standard_identifier, adoption_data)

        # Check for China adoption
        china_adoption = self._check_china_adoption(standard_identifier, adoption_data)

        return StandardAdoption(
            standard_identifier=standard_identifier,
            adoption_metrics=adoption_data,
            market_segments=self._identify_market_segments(adoption_data),
            adopting_organizations=self._extract_adopting_organizations(adoption_data),
            adoption_timeline=adoption_timeline,
            china_adoption=china_adoption,
            competitive_standards=adoption_data['competitive_analysis']
        )

    def _search_standard_implementations(self, standard_identifier: str) -> List[Dict[str, Any]]:
        """Search for implementations of a standard"""
        implementations = []

        # Search Common Crawl or web sources for implementation mentions
        # This would integrate with the Common Crawl pipeline

        # Search patent databases for standard implementations
        # This would integrate with the patent pipeline

        # Search procurement databases for standard-compliant purchases
        # This would integrate with the procurement pipeline

        return implementations

    def _search_standard_certifications(self, standard_identifier: str) -> List[Dict[str, Any]]:
        """Search for certifications and conformance testing"""
        certifications = []

        # Search certification body databases
        # Examples: FCC database, CE marking database, industry certification bodies

        return certifications

    def _search_market_mentions(self, standard_identifier: str) -> List[Dict[str, Any]]:
        """Search for market mentions and commercial adoption"""
        mentions = []

        # Search company websites, press releases, product documentation
        # This would use the Common Crawl pipeline

        return mentions

    def _analyze_competitive_standards(self, standard_identifier: str) -> List[str]:
        """Identify competing standards in the same domain"""
        competitors = []

        # Analyze standards in similar technology domains
        # Look for overlapping scope and functionality

        return competitors

    def _build_adoption_timeline(self, standard_identifier: str, adoption_data: Dict) -> List[Dict[str, Any]]:
        """Build timeline of standard adoption events"""
        timeline = []

        # Combine data from all sources to create chronological timeline
        # Include: publication date, first implementations, certifications, major adoptions

        return timeline

    def _check_china_adoption(self, standard_identifier: str, adoption_data: Dict) -> bool:
        """Check if China has adopted or implemented the standard"""
        china_indicators = self.config['china_indicators']

        # Check implementing organizations
        for impl in adoption_data.get('implementations', []):
            org = impl.get('organization', '').lower()
            if any(indicator.lower() in org for indicator in china_indicators['organizations']):
                return True

        # Check certifications from China
        for cert in adoption_data.get('certifications', []):
            country = cert.get('country', '').lower()
            if country in ['cn', 'china']:
                return True

        return False

    def _identify_market_segments(self, adoption_data: Dict) -> List[str]:
        """Identify market segments where standard is adopted"""
        segments = []

        # Analyze adoption data to identify industry segments
        # Examples: telecommunications, automotive, aerospace, IoT

        for domain, keywords in self.config['technology_domains'].items():
            if any(keyword.lower() in str(adoption_data).lower() for keyword in keywords):
                segments.append(domain)

        return segments

    def _extract_adopting_organizations(self, adoption_data: Dict) -> List[str]:
        """Extract list of organizations that have adopted the standard"""
        organizations = set()

        # Extract from implementations
        for impl in adoption_data.get('implementations', []):
            if 'organization' in impl:
                organizations.add(impl['organization'])

        # Extract from certifications
        for cert in adoption_data.get('certifications', []):
            if 'organization' in cert:
                organizations.add(cert['organization'])

        return list(organizations)

    def analyze_market_position(self, standards_activity: List[StandardsParticipation],
                              adoption_metrics: Dict[str, StandardAdoption],
                              competitor_analysis: bool = True) -> MarketPosition:
        """Analyze market position based on standards influence"""

        # Calculate standards leadership score
        leadership_score = self._calculate_leadership_score(standards_activity)

        # Identify areas of leadership
        leadership_areas = self._identify_leadership_areas(standards_activity)

        # Analyze competitive advantages
        competitive_advantages = self._analyze_competitive_advantages(
            standards_activity, adoption_metrics
        )

        # Calculate market share indicators
        market_share = self._calculate_market_share_indicators(adoption_metrics)

        # Assess China collaboration risk
        china_risk = self._assess_china_collaboration_risk(standards_activity)

        # Identify strategic vulnerabilities
        vulnerabilities = self._identify_strategic_vulnerabilities(
            standards_activity, adoption_metrics
        )

        return MarketPosition(
            organization=standards_activity[0].organization if standards_activity else '',
            market_influence_score=leadership_score,
            standards_leadership_areas=leadership_areas,
            competitive_advantages=competitive_advantages,
            market_share_indicators=market_share,
            china_collaboration_risk=china_risk,
            strategic_vulnerabilities=vulnerabilities
        )

    def _calculate_leadership_score(self, standards_activity: List[StandardsParticipation]) -> float:
        """Calculate overall standards leadership score"""
        if not standards_activity:
            return 0.0

        total_score = sum(activity.contribution_score for activity in standards_activity)
        max_possible = len(standards_activity) * 10  # Maximum score per activity

        # Normalize to 0-10 scale
        leadership_score = (total_score / max_possible) * 10 if max_possible > 0 else 0

        return min(leadership_score, 10.0)

    def _identify_leadership_areas(self, standards_activity: List[StandardsParticipation]) -> List[str]:
        """Identify technology areas where organization has leadership"""
        leadership_areas = []

        # Group activities by technology domain
        domain_scores = defaultdict(list)

        for activity in standards_activity:
            # Map standard to technology domain
            domain = self._map_standard_to_domain(activity.standard_title)
            if domain:
                domain_scores[domain].append(activity.contribution_score)

        # Identify domains with high average scores
        for domain, scores in domain_scores.items():
            avg_score = np.mean(scores)
            if avg_score >= 5.0:  # Threshold for leadership
                leadership_areas.append(domain)

        return leadership_areas

    def _map_standard_to_domain(self, standard_title: str) -> Optional[str]:
        """Map a standard title to a technology domain"""
        title_lower = standard_title.lower()

        for domain, keywords in self.config['technology_domains'].items():
            if any(keyword.lower() in title_lower for keyword in keywords):
                return domain

        return None

    def _analyze_competitive_advantages(self, standards_activity: List[StandardsParticipation],
                                      adoption_metrics: Dict[str, StandardAdoption]) -> List[str]:
        """Analyze competitive advantages from standards position"""
        advantages = []

        # High influence in key standards
        high_influence_standards = [
            activity for activity in standards_activity
            if activity.contribution_score >= 7  # Chair/editor level
        ]

        if high_influence_standards:
            advantages.append("Leadership roles in key standards bodies")

        # Standards with high market adoption
        successful_standards = [
            std_id for std_id, adoption in adoption_metrics.items()
            if len(adoption.adopting_organizations) >= 10  # Arbitrary threshold
        ]

        if successful_standards:
            advantages.append("Standards with proven market adoption")

        # Multi-domain presence
        domains = set(self._map_standard_to_domain(activity.standard_title)
                     for activity in standards_activity)
        domains.discard(None)

        if len(domains) >= 3:
            advantages.append("Cross-domain standards influence")

        return advantages

    def _calculate_market_share_indicators(self, adoption_metrics: Dict[str, StandardAdoption]) -> Dict[str, float]:
        """Calculate market share indicators based on standards adoption"""
        indicators = {}

        # Calculate adoption success rate
        total_standards = len(adoption_metrics)
        if total_standards > 0:
            adopted_standards = sum(
                1 for adoption in adoption_metrics.values()
                if len(adoption.adopting_organizations) > 0
            )
            indicators['adoption_success_rate'] = adopted_standards / total_standards

        # Calculate average adoption breadth
        if adoption_metrics:
            avg_adopters = np.mean([
                len(adoption.adopting_organizations)
                for adoption in adoption_metrics.values()
            ])
            indicators['average_adoption_breadth'] = avg_adopters

        return indicators

    def _assess_china_collaboration_risk(self, standards_activity: List[StandardsParticipation]) -> float:
        """Assess risk from China collaboration in standards"""
        if not standards_activity:
            return 0.0

        # This would analyze China participation in same working groups
        # For now, return placeholder calculation
        china_collaboration_count = 0  # Would be calculated from actual data

        risk_score = min(china_collaboration_count / len(standards_activity), 1.0)
        return risk_score

    def _identify_strategic_vulnerabilities(self, standards_activity: List[StandardsParticipation],
                                          adoption_metrics: Dict[str, StandardAdoption]) -> List[str]:
        """Identify strategic vulnerabilities in standards position"""
        vulnerabilities = []

        # Low adoption of led standards
        low_adoption_standards = [
            activity for activity in standards_activity
            if (activity.contribution_score >= 5 and  # Significant contribution
                adoption_metrics.get(activity.standard_identifier, StandardAdoption('', {}, [], [], [], False, [])).adopting_organizations.__len__() < 3)
        ]

        if low_adoption_standards:
            vulnerabilities.append("Led standards with limited market adoption")

        # Dependence on single standards body
        bodies = set(activity.standards_body for activity in standards_activity)
        if len(bodies) == 1:
            vulnerabilities.append("Concentration in single standards body")

        # China competition in same domains
        china_adoption_count = sum(
            1 for adoption in adoption_metrics.values()
            if adoption.china_adoption
        )

        if china_adoption_count > len(adoption_metrics) * 0.3:  # >30% China adoption
            vulnerabilities.append("High China adoption of organization's standards")

        return vulnerabilities

    def run_pipeline(self, org_ror: str) -> Dict[str, Any]:
        """Execute the complete Standards→Adoption→Market_Position fusion pipeline"""

        print(f"Running Standards→Adoption→Market_Position pipeline for {org_ror}")

        # Stage 1: Mine standards participation
        print("Stage 1: Mining standards participation...")
        standards_activity = self.mine_standards_participation(org_ror)

        if not standards_activity:
            return {"error": f"No standards participation found for {org_ror}"}

        # Stage 2: Track market adoption for each standard
        print("Stage 2: Tracking market adoption...")
        adoption_metrics = {}

        for activity in standards_activity:
            if activity.standard_identifier not in adoption_metrics:
                adoption = self.track_market_adoption(
                    activity.standard_identifier,
                    monitoring_period=36
                )
                adoption_metrics[activity.standard_identifier] = adoption

        # Stage 3: Analyze market position
        print("Stage 3: Analyzing market position...")
        market_position = self.analyze_market_position(
            standards_activity,
            adoption_metrics,
            competitor_analysis=True
        )

        # Stage 4: Calculate summary metrics
        print("Stage 4: Calculating summary metrics...")

        # China collaboration analysis
        china_collaboration_standards = [
            activity.standard_identifier for activity in standards_activity
            if adoption_metrics.get(activity.standard_identifier, StandardAdoption('', {}, [], [], [], False, [])).china_adoption
        ]

        # Calculate overall influence score
        influence_score = market_position.market_influence_score

        # Compile results
        results = {
            "pipeline": "standards_adoption_market",
            "org_ror": org_ror,
            "standards_participation": [asdict(activity) for activity in standards_activity],
            "adoption_metrics": {
                std_id: asdict(adoption) for std_id, adoption in adoption_metrics.items()
            },
            "market_position": asdict(market_position),
            "summary_metrics": {
                "total_standards": len(standards_activity),
                "standards_bodies": len(set(activity.standards_body for activity in standards_activity)),
                "leadership_positions": len([a for a in standards_activity if a.contribution_score >= 7]),
                "market_influence_score": influence_score,
                "china_collaboration_standards": len(china_collaboration_standards),
                "adoption_success_rate": market_position.market_share_indicators.get('adoption_success_rate', 0)
            },
            "china_collaboration_risk": {
                "standards_with_china_adoption": china_collaboration_standards,
                "risk_score": market_position.china_collaboration_risk,
                "risk_level": "high" if market_position.china_collaboration_risk > 0.3 else "medium" if market_position.china_collaboration_risk > 0.1 else "low"
            },
            "generated_at": datetime.now().isoformat()
        }

        # Save results
        self.save_results(results, org_ror)

        return results

    def save_results(self, results: Dict[str, Any], org_ror: str):
        """Save pipeline results to file"""
        output_path = self.data_dir / f"{org_ror}_standards_market_position.json"

        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)

        print(f"Results saved to {output_path}")

def main():
    """Main execution function"""
    pipeline = StandardsAdoptionMarketPipeline()

    # Example usage
    test_org_ror = "ror:01111111"  # Replace with actual ROR ID
    results = pipeline.run_pipeline(test_org_ror)

    print("\n" + "="*60)
    print("STANDARDS→ADOPTION→MARKET_POSITION FUSION RESULTS")
    print("="*60)

    if "error" not in results:
        print(f"Organization: {results['org_ror']}")
        print(f"Standards participation: {results['summary_metrics']['total_standards']}")
        print(f"Standards bodies: {results['summary_metrics']['standards_bodies']}")
        print(f"Leadership positions: {results['summary_metrics']['leadership_positions']}")
        print(f"Market influence score: {results['summary_metrics']['market_influence_score']:.2f}")
        print(f"China collaboration risk: {results['china_collaboration_risk']['risk_level']}")
        print(f"Adoption success rate: {results['summary_metrics']['adoption_success_rate']:.2f}")
    else:
        print(f"Error: {results['error']}")

if __name__ == "__main__":
    main()

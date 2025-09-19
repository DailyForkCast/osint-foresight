#!/usr/bin/env python3
"""
Funding→Spinout→Technology_Transfer Fusion Pipeline
Tracks funding through spinout creation to technology transfer events
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
import re
from collections import defaultdict

@dataclass
class FundingSource:
    """Funding source data structure"""
    project_id: str
    program_name: str
    funding_agency: str
    principal_investigator: str
    institution: str
    amount: float
    currency: str
    start_date: datetime
    end_date: datetime
    technology_area: str
    project_description: str
    participants: List[str]

@dataclass
class SpinoutCompany:
    """Spinout company data structure"""
    company_name: str
    incorporation_date: datetime
    founders: List[str]
    parent_institution: str
    parent_project_id: str
    technology_focus: str
    initial_funding: float
    lei: Optional[str]
    website: str
    legal_status: str

@dataclass
class TechnologyTransfer:
    """Technology transfer event data structure"""
    transfer_id: str
    transfer_type: str  # licensing, acquisition, partnership, joint_venture
    source_entity: str
    target_entity: str
    technology_description: str
    transfer_date: datetime
    value: Optional[float]
    china_involvement: bool
    transfer_mechanism: str
    ip_assets: List[str]

@dataclass
class TransferRisk:
    """Technology transfer risk assessment"""
    spinout_company: str
    risk_level: str  # low, medium, high, critical
    risk_factors: List[str]
    china_exposure: bool
    protection_measures: List[str]
    recommended_actions: List[str]

class FundingSpinoutTransferPipeline:
    """Main fusion pipeline for Funding→Spinout→Technology_Transfer analysis"""

    def __init__(self, config_path: str = None):
        """Initialize the funding spinout transfer pipeline"""
        if config_path is None:
            config_path = "C:/Projects/OSINT - Foresight/config/fusion_config.yaml"

        # Load configuration
        self.config = self._load_config(config_path)

        # Data storage paths
        self.data_dir = Path("F:/fusion_data/funding_spinout_transfer")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # API endpoints for funding databases
        self.funding_apis = {
            'cordis': {
                'base_url': 'https://cordis.europa.eu/api',
                'projects': 'https://cordis.europa.eu/api/projects'
            },
            'nsf': {
                'base_url': 'https://api.nsf.gov',
                'awards': 'https://api.nsf.gov/services/v1/awards.json'
            },
            'ukri': {
                'base_url': 'https://gtr.ukri.org/api',
                'projects': 'https://gtr.ukri.org/api/projects'
            },
            'dfg': {
                'base_url': 'https://gepris.dfg.de/gepris/OCTOPUS',
                'projects': 'https://gepris.dfg.de/gepris/OCTOPUS/projektverzeichnis'
            }
        }

        # Company registration APIs
        self.company_apis = {
            'companies_house': 'https://api.company-information.service.gov.uk',
            'opencorporates': 'https://api.opencorporates.com/v0.4',
            'gleif': 'https://api.gleif.org/api/v1'
        }

        # Detection windows for spinout and transfer events
        self.spinout_detection_window = 60  # months post-funding
        self.transfer_detection_window = 84  # months post-spinout

    def _load_config(self, config_path: str) -> Dict:
        """Load funding spinout transfer pipeline configuration"""
        default_config = {
            "funding_agencies": {
                "eu": ["European Commission", "ERC", "Horizon 2020", "Horizon Europe"],
                "us": ["NSF", "NIH", "DOD", "DOE", "DARPA", "IARPA"],
                "uk": ["UKRI", "EPSRC", "BBSRC", "NERC", "Innovate UK"],
                "germany": ["DFG", "BMBF", "BMWi"],
                "france": ["ANR", "CNRS", "CEA"],
                "italy": ["MIUR", "CNR", "ENEA"]
            },
            "spinout_indicators": [
                "spin-off", "spinoff", "spin-out", "spinout", "startup", "start-up",
                "technology transfer", "commercialization", "licence", "license",
                "intellectual property", "patent licensing"
            ],
            "transfer_mechanisms": [
                "acquisition", "merger", "joint venture", "licensing agreement",
                "technology partnership", "strategic alliance", "investment",
                "research collaboration", "consulting agreement"
            ],
            "china_entities": {
                "companies": [
                    "Huawei", "ZTE", "Tencent", "Alibaba", "Baidu", "ByteDance",
                    "Xiaomi", "DJI", "BYD", "CATL", "SMIC", "Lenovo"
                ],
                "investment_funds": [
                    "China Investment Corporation", "SAFE Investment", "China Development Bank",
                    "Tsinghua Holdings", "Legend Capital", "IDG Capital", "Qiming Venture"
                ],
                "research_institutes": [
                    "Chinese Academy of Sciences", "Tsinghua University", "Peking University",
                    "CAICT", "CAS", "BUPT", "HKUST"
                ]
            },
            "risk_indicators": {
                "technology_areas": [
                    "artificial intelligence", "quantum", "semiconductor", "aerospace",
                    "defense", "cybersecurity", "biotechnology", "advanced materials"
                ],
                "dual_use_keywords": [
                    "dual-use", "military application", "defense application",
                    "surveillance", "reconnaissance", "encryption", "cryptography"
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

    def analyze_funding_sources(self, project_id: str) -> FundingSource:
        """Analyze funding sources for a specific project"""

        # Try different funding databases
        funding_data = None

        # Check CORDIS (EU projects)
        funding_data = self._search_cordis_project(project_id)

        if not funding_data:
            # Check NSF (US projects)
            funding_data = self._search_nsf_project(project_id)

        if not funding_data:
            # Check UKRI (UK projects)
            funding_data = self._search_ukri_project(project_id)

        if not funding_data:
            # Check national databases
            funding_data = self._search_national_databases(project_id)

        if funding_data:
            return FundingSource(
                project_id=project_id,
                program_name=funding_data.get('program', ''),
                funding_agency=funding_data.get('agency', ''),
                principal_investigator=funding_data.get('pi', ''),
                institution=funding_data.get('institution', ''),
                amount=funding_data.get('amount', 0.0),
                currency=funding_data.get('currency', 'EUR'),
                start_date=datetime.fromisoformat(funding_data.get('start_date', '2020-01-01')),
                end_date=datetime.fromisoformat(funding_data.get('end_date', '2023-01-01')),
                technology_area=funding_data.get('technology_area', ''),
                project_description=funding_data.get('description', ''),
                participants=funding_data.get('participants', [])
            )
        else:
            return None

    def _search_cordis_project(self, project_id: str) -> Optional[Dict]:
        """Search CORDIS database for EU project"""
        try:
            # Load from local CORDIS data if available
            cordis_data_path = f"F:/cordis_data/projects/{project_id}.json"

            with open(cordis_data_path, 'r') as f:
                project_data = json.load(f)

            return {
                'program': project_data.get('programme', ''),
                'agency': 'European Commission',
                'pi': project_data.get('coordinator', ''),
                'institution': project_data.get('coordinator_organization', ''),
                'amount': float(project_data.get('total_cost', 0)),
                'currency': 'EUR',
                'start_date': project_data.get('start_date', '2020-01-01'),
                'end_date': project_data.get('end_date', '2023-01-01'),
                'technology_area': self._extract_technology_area(project_data.get('description', '')),
                'description': project_data.get('description', ''),
                'participants': project_data.get('participants', [])
            }

        except FileNotFoundError:
            return None

    def _search_nsf_project(self, project_id: str) -> Optional[Dict]:
        """Search NSF database for US project"""
        # Implementation would query NSF API
        return None

    def _search_ukri_project(self, project_id: str) -> Optional[Dict]:
        """Search UKRI database for UK project"""
        # Implementation would query UKRI Gateway to Research API
        return None

    def _search_national_databases(self, project_id: str) -> Optional[Dict]:
        """Search national funding databases"""
        # Implementation would search various national databases
        return None

    def _extract_technology_area(self, description: str) -> str:
        """Extract technology area from project description"""
        description_lower = description.lower()

        for area, keywords in self.config['risk_indicators']['technology_areas']:
            if isinstance(keywords, list):
                if any(keyword.lower() in description_lower for keyword in keywords):
                    return area
            elif area.lower() in description_lower:
                return area

        return "general"

    def detect_project_spinouts(self, project_id: str, detection_window: int = 60) -> List[SpinoutCompany]:
        """Detect spinout companies created from a project"""

        funding_source = self.analyze_funding_sources(project_id)
        if not funding_source:
            return []

        spinouts = []

        # Define search window
        search_start = funding_source.start_date
        search_end = funding_source.end_date + timedelta(days=30 * detection_window)

        # Search for company incorporations
        potential_spinouts = self._search_company_incorporations(
            funding_source.institution,
            funding_source.principal_investigator,
            search_start,
            search_end
        )

        # Filter and validate spinouts
        for company_data in potential_spinouts:
            if self._validate_spinout_connection(company_data, funding_source):
                spinout = SpinoutCompany(
                    company_name=company_data.get('name', ''),
                    incorporation_date=datetime.fromisoformat(company_data.get('incorporation_date', '2020-01-01')),
                    founders=company_data.get('founders', []),
                    parent_institution=funding_source.institution,
                    parent_project_id=project_id,
                    technology_focus=company_data.get('technology_focus', ''),
                    initial_funding=company_data.get('initial_funding', 0.0),
                    lei=company_data.get('lei'),
                    website=company_data.get('website', ''),
                    legal_status=company_data.get('status', 'active')
                )
                spinouts.append(spinout)

        return spinouts

    def _search_company_incorporations(self, institution: str, pi_name: str,
                                     start_date: datetime, end_date: datetime) -> List[Dict]:
        """Search for company incorporations related to institution/PI"""

        incorporations = []

        # Search Companies House (UK)
        uk_incorporations = self._search_companies_house(institution, pi_name, start_date, end_date)
        incorporations.extend(uk_incorporations)

        # Search other national registries
        # This would be expanded to include multiple countries

        return incorporations

    def _search_companies_house(self, institution: str, pi_name: str,
                               start_date: datetime, end_date: datetime) -> List[Dict]:
        """Search UK Companies House for related incorporations"""

        companies = []

        try:
            # Extract key terms for search
            search_terms = self._extract_search_terms(institution, pi_name)

            for term in search_terms:
                # Search Companies House API (would require API key)
                # For now, load from local data if available

                companies_data_path = f"F:/companies_house_data/search_{term.replace(' ', '_')}.json"
                try:
                    with open(companies_data_path, 'r') as f:
                        company_data = json.load(f)
                        companies.extend(company_data.get('companies', []))
                except FileNotFoundError:
                    continue

        except Exception as e:
            print(f"Error searching Companies House: {e}")

        return companies

    def _extract_search_terms(self, institution: str, pi_name: str) -> List[str]:
        """Extract search terms for company searches"""
        terms = []

        # Institution abbreviations
        if institution:
            terms.append(institution)
            # Add common abbreviations (would be more sophisticated)
            words = institution.split()
            if len(words) > 1:
                abbreviation = ''.join(word[0].upper() for word in words if len(word) > 2)
                if len(abbreviation) >= 2:
                    terms.append(abbreviation)

        # PI surname
        if pi_name:
            name_parts = pi_name.split()
            if name_parts:
                terms.append(name_parts[-1])  # Surname

        return terms

    def _validate_spinout_connection(self, company_data: Dict, funding_source: FundingSource) -> bool:
        """Validate that a company is genuinely a spinout from the project"""

        # Check founder connections
        founders = company_data.get('founders', [])
        if funding_source.principal_investigator in ' '.join(founders):
            return True

        # Check company description for technology keywords
        description = company_data.get('description', '').lower()
        funding_description = funding_source.project_description.lower()

        # Simple keyword overlap (can be enhanced with NLP)
        common_keywords = set(description.split()) & set(funding_description.split())
        if len(common_keywords) >= 3:  # Threshold for connection
            return True

        # Check for spinout indicators in company name/description
        spinout_indicators = self.config['spinout_indicators']
        if any(indicator.lower() in description for indicator in spinout_indicators):
            return True

        return False

    def track_technology_transfers(self, spinout: SpinoutCompany,
                                 include_licensing: bool = True,
                                 include_acquisitions: bool = True,
                                 include_partnerships: bool = True) -> List[TechnologyTransfer]:
        """Track technology transfer events for a spinout company"""

        transfers = []

        # Search for licensing agreements
        if include_licensing:
            licensing_events = self._search_licensing_events(spinout)
            transfers.extend(licensing_events)

        # Search for acquisitions
        if include_acquisitions:
            acquisition_events = self._search_acquisition_events(spinout)
            transfers.extend(acquisition_events)

        # Search for partnerships
        if include_partnerships:
            partnership_events = self._search_partnership_events(spinout)
            transfers.extend(partnership_events)

        return transfers

    def _search_licensing_events(self, spinout: SpinoutCompany) -> List[TechnologyTransfer]:
        """Search for licensing events"""
        transfers = []

        # Search patent licensing databases
        # Search company announcements and press releases
        # Search regulatory filings

        return transfers

    def _search_acquisition_events(self, spinout: SpinoutCompany) -> List[TechnologyTransfer]:
        """Search for acquisition events"""
        transfers = []

        # Search M&A databases
        # Search regulatory filings
        # Search news and announcements

        return transfers

    def _search_partnership_events(self, spinout: SpinoutCompany) -> List[TechnologyTransfer]:
        """Search for partnership events"""
        transfers = []

        # Search partnership announcements
        # Search joint venture filings
        # Search collaboration agreements

        return transfers

    def analyze_china_interest_in_transfers(self, transfers: List[TechnologyTransfer]) -> Dict[str, Any]:
        """Analyze China interest and involvement in technology transfers"""

        china_interest = {
            'china_involved_transfers': [],
            'china_acquisition_attempts': [],
            'china_partnership_count': 0,
            'risk_assessment': 'low'
        }

        china_entities = self.config['china_entities']

        for transfer in transfers:
            # Check target entity
            target_entity = transfer.target_entity.lower()

            # Check for Chinese companies
            for company in china_entities['companies']:
                if company.lower() in target_entity:
                    china_interest['china_involved_transfers'].append(transfer)
                    transfer.china_involvement = True
                    break

            # Check for Chinese investment funds
            for fund in china_entities['investment_funds']:
                if fund.lower() in target_entity:
                    china_interest['china_involved_transfers'].append(transfer)
                    transfer.china_involvement = True
                    break

            # Check for Chinese research institutes
            for institute in china_entities['research_institutes']:
                if institute.lower() in target_entity:
                    china_interest['china_involved_transfers'].append(transfer)
                    transfer.china_involvement = True
                    break

        # Count partnership types
        china_interest['china_partnership_count'] = len(china_interest['china_involved_transfers'])

        # Assess risk level
        if china_interest['china_partnership_count'] > 2:
            china_interest['risk_assessment'] = 'high'
        elif china_interest['china_partnership_count'] > 0:
            china_interest['risk_assessment'] = 'medium'

        return china_interest

    def calculate_technology_leakage_risk(self, funding_source: FundingSource,
                                        spinouts: List[SpinoutCompany],
                                        transfers: List[TechnologyTransfer]) -> Dict[str, Any]:
        """Calculate technology leakage risk assessment"""

        risk_factors = []
        risk_score = 0.0

        # High-risk technology area
        technology_area = funding_source.technology_area.lower()
        high_risk_areas = [area.lower() for area in self.config['risk_indicators']['technology_areas']]

        if any(area in technology_area for area in high_risk_areas):
            risk_factors.append("high_risk_technology_area")
            risk_score += 3.0

        # Dual-use technology indicators
        description = funding_source.project_description.lower()
        dual_use_keywords = self.config['risk_indicators']['dual_use_keywords']

        if any(keyword.lower() in description for keyword in dual_use_keywords):
            risk_factors.append("dual_use_technology")
            risk_score += 2.0

        # China involvement in transfers
        china_transfers = [t for t in transfers if t.china_involvement]
        if china_transfers:
            risk_factors.append("china_technology_transfers")
            risk_score += len(china_transfers) * 2.0

        # Multiple spinouts (higher exposure)
        if len(spinouts) > 2:
            risk_factors.append("multiple_spinouts")
            risk_score += 1.0

        # Determine risk level
        if risk_score >= 5.0:
            risk_level = "critical"
        elif risk_score >= 3.0:
            risk_level = "high"
        elif risk_score >= 1.0:
            risk_level = "medium"
        else:
            risk_level = "low"

        return {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "risk_factors": risk_factors,
            "china_transfer_count": len(china_transfers),
            "mitigation_required": risk_score >= 3.0
        }

    def assess_protection_measures(self, funding_source: FundingSource,
                                 spinouts: List[SpinoutCompany]) -> Dict[str, Any]:
        """Assess adequacy of technology protection measures"""

        protection_assessment = {
            "ip_protection": "unknown",
            "export_controls": "unknown",
            "security_measures": [],
            "gaps_identified": [],
            "recommendations": []
        }

        # Check for IP protection indicators
        # Check for export control compliance
        # Check for security clearance requirements
        # Check for foreign investment screening

        return protection_assessment

    def run_pipeline(self, project_id: str) -> Dict[str, Any]:
        """Execute the complete Funding→Spinout→Technology_Transfer fusion pipeline"""

        print(f"Running Funding→Spinout→Technology_Transfer pipeline for {project_id}")

        # Stage 1: Analyze funding sources
        print("Stage 1: Analyzing funding sources...")
        funding_source = self.analyze_funding_sources(project_id)

        if not funding_source:
            return {"error": f"No funding data found for {project_id}"}

        # Stage 2: Detect project spinouts
        print("Stage 2: Detecting project spinouts...")
        spinouts = self.detect_project_spinouts(project_id, self.spinout_detection_window)

        # Stage 3: Track technology transfers
        print("Stage 3: Tracking technology transfers...")
        all_transfers = []

        for spinout in spinouts:
            transfers = self.track_technology_transfers(
                spinout,
                include_licensing=True,
                include_acquisitions=True,
                include_partnerships=True
            )
            all_transfers.extend(transfers)

        # Stage 4: Analyze China interest
        print("Stage 4: Analyzing China interest...")
        china_interest = self.analyze_china_interest_in_transfers(all_transfers)

        # Stage 5: Calculate technology leakage risk
        print("Stage 5: Calculating technology leakage risk...")
        leakage_risk = self.calculate_technology_leakage_risk(
            funding_source, spinouts, all_transfers
        )

        # Stage 6: Assess protection measures
        print("Stage 6: Assessing protection measures...")
        protection_assessment = self.assess_protection_measures(funding_source, spinouts)

        # Compile results
        results = {
            "pipeline": "funding_spinout_transfer",
            "project_id": project_id,
            "funding_source": asdict(funding_source),
            "spinout_companies": [asdict(spinout) for spinout in spinouts],
            "technology_transfers": [asdict(transfer) for transfer in all_transfers],
            "china_interest_analysis": china_interest,
            "technology_leakage_risk": leakage_risk,
            "protection_assessment": protection_assessment,
            "summary_metrics": {
                "total_spinouts": len(spinouts),
                "total_transfers": len(all_transfers),
                "china_involved_transfers": len([t for t in all_transfers if t.china_involvement]),
                "risk_level": leakage_risk['risk_level'],
                "funding_amount": funding_source.amount,
                "funding_currency": funding_source.currency
            },
            "generated_at": datetime.now().isoformat()
        }

        # Save results
        self.save_results(results, project_id)

        return results

    def save_results(self, results: Dict[str, Any], project_id: str):
        """Save pipeline results to file"""
        output_path = self.data_dir / f"{project_id}_funding_transfer_analysis.json"

        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)

        print(f"Results saved to {output_path}")

def main():
    """Main execution function"""
    pipeline = FundingSpinoutTransferPipeline()

    # Example usage
    test_project_id = "H2020-123456"  # Replace with actual project ID
    results = pipeline.run_pipeline(test_project_id)

    print("\n" + "="*60)
    print("FUNDING→SPINOUT→TECHNOLOGY_TRANSFER FUSION RESULTS")
    print("="*60)

    if "error" not in results:
        print(f"Project: {results['project_id']}")
        print(f"Funding amount: {results['summary_metrics']['funding_amount']} {results['summary_metrics']['funding_currency']}")
        print(f"Spinout companies: {results['summary_metrics']['total_spinouts']}")
        print(f"Technology transfers: {results['summary_metrics']['total_transfers']}")
        print(f"China-involved transfers: {results['summary_metrics']['china_involved_transfers']}")
        print(f"Technology leakage risk: {results['summary_metrics']['risk_level']}")
    else:
        print(f"Error: {results['error']}")

if __name__ == "__main__":
    main()

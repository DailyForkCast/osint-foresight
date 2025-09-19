"""
GLEIF Ownership Tracker
Free API for tracking corporate ownership chains through Legal Entity Identifiers (LEI)
No API key required - completely free public access
"""

import json
import logging
import requests
from datetime import datetime
from typing import Dict, List, Optional, Set
from pathlib import Path
import pandas as pd
from enum import Enum

logger = logging.getLogger(__name__)

class OwnershipType(Enum):
    """Types of ownership relationships"""
    DIRECT_PARENT = "direct"
    ULTIMATE_PARENT = "ultimate"
    BRANCH = "branch"
    FUND_FAMILY = "fund"

class RiskLevel(Enum):
    """Risk assessment levels"""
    CRITICAL = "critical"  # China/Russia ultimate owner
    HIGH = "high"  # China/Russia in ownership chain
    MEDIUM = "medium"  # Complex ownership structure
    LOW = "low"  # Clear Western ownership
    UNKNOWN = "unknown"  # Unable to determine

class GLEIFOwnershipTracker:
    """
    Track corporate ownership using GLEIF's free public API
    No authentication required
    """

    def __init__(self, country_iso3: str):
        self.country = country_iso3
        self.base_url = "https://api.gleif.org/api/v1"
        self.output_dir = Path(f"artifacts/{country_iso3}/phase06_funders")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Countries of concern for ownership
        self.concern_countries = {"CN", "RU", "IR", "KP"}  # China, Russia, Iran, North Korea

        # Cache to avoid redundant API calls
        self.cache = {}

        # Session for connection pooling
        self.session = requests.Session()

    def get_lei_record(self, lei: str) -> Optional[Dict]:
        """
        Get basic entity information

        Args:
            lei: Legal Entity Identifier (20 characters)

        Returns:
            Entity details or None if not found
        """
        if lei in self.cache:
            return self.cache[lei]

        try:
            url = f"{self.base_url}/lei-records/{lei}"
            response = self.session.get(url, timeout=10)

            if response.status_code == 404:
                logger.warning(f"LEI not found: {lei}")
                return None

            response.raise_for_status()
            data = response.json()

            if 'data' in data and len(data['data']) > 0:
                entity = data['data'][0]['attributes']['entity']
                record = {
                    "lei": lei,
                    "name": entity['legalName']['name'],
                    "country": entity['legalAddress']['country'],
                    "city": entity['legalAddress'].get('city', ''),
                    "status": entity.get('status', 'ACTIVE'),
                    "registration_date": data['data'][0]['attributes']['registration'].get('initialRegistrationDate'),
                    "last_update": data['data'][0]['attributes']['registration'].get('lastUpdateDate')
                }

                # Cache the result
                self.cache[lei] = record
                return record

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching LEI {lei}: {e}")
            return None

    def get_direct_parent(self, lei: str) -> Optional[Dict]:
        """
        Get direct parent company

        Args:
            lei: Legal Entity Identifier

        Returns:
            Parent company details or None
        """
        try:
            url = f"{self.base_url}/lei-records/{lei}/direct-parent-relationship"
            response = self.session.get(url, timeout=10)

            if response.status_code == 404:
                # No parent relationship
                return None

            response.raise_for_status()
            data = response.json()

            if 'data' in data and len(data['data']) > 0:
                parent_data = data['data'][0]['attributes']['relationship']
                parent_lei = parent_data['parentLei']

                # Get parent details
                parent_record = self.get_lei_record(parent_lei)

                if parent_record:
                    parent_record['ownership_type'] = parent_data.get('relationshipType', 'DIRECT')
                    parent_record['ownership_percent'] = parent_data.get('ownershipPercent', {})
                    parent_record['relationship_status'] = parent_data.get('status', 'ACTIVE')
                    parent_record['start_date'] = parent_data.get('startDate')

                return parent_record

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching parent for {lei}: {e}")
            return None

    def get_ultimate_parent(self, lei: str) -> Optional[Dict]:
        """
        Get ultimate parent (beneficial owner)

        Args:
            lei: Legal Entity Identifier

        Returns:
            Ultimate parent details or None
        """
        try:
            url = f"{self.base_url}/lei-records/{lei}/ultimate-parent-relationship"
            response = self.session.get(url, timeout=10)

            if response.status_code == 404:
                # No ultimate parent relationship
                return None

            response.raise_for_status()
            data = response.json()

            if 'data' in data and len(data['data']) > 0:
                parent_data = data['data'][0]['attributes']['relationship']
                parent_lei = parent_data['parentLei']

                # Get ultimate parent details
                parent_record = self.get_lei_record(parent_lei)

                if parent_record:
                    parent_record['ownership_type'] = 'ULTIMATE'
                    parent_record['accounting_standard'] = parent_data.get('accountingStandard')
                    parent_record['relationship_status'] = parent_data.get('status', 'ACTIVE')

                return parent_record

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching ultimate parent for {lei}: {e}")
            return None

    def trace_ownership_chain(self, lei: str, max_depth: int = 10) -> Dict:
        """
        Trace complete ownership chain

        Args:
            lei: Starting Legal Entity Identifier
            max_depth: Maximum levels to trace

        Returns:
            Complete ownership structure with risk assessment
        """
        chain = {
            "lei": lei,
            "entity": self.get_lei_record(lei),
            "direct_parent": None,
            "ultimate_parent": None,
            "ownership_chain": [],
            "china_owned": False,
            "russia_owned": False,
            "concern_countries": [],
            "risk_level": RiskLevel.UNKNOWN.value,
            "risk_factors": []
        }

        if not chain['entity']:
            return chain

        # Get direct parent
        direct_parent = self.get_direct_parent(lei)
        if direct_parent:
            chain['direct_parent'] = direct_parent

            # Trace up the chain
            current_lei = direct_parent['lei']
            depth = 0
            visited = {lei}  # Prevent cycles

            while current_lei and depth < max_depth:
                if current_lei in visited:
                    chain['risk_factors'].append("Circular ownership detected")
                    break

                visited.add(current_lei)
                parent = self.get_direct_parent(current_lei)

                if parent:
                    chain['ownership_chain'].append(parent)
                    current_lei = parent['lei']

                    # Check for concerning countries
                    if parent['country'] in self.concern_countries:
                        chain['concern_countries'].append({
                            "country": parent['country'],
                            "entity": parent['name'],
                            "level": depth + 1
                        })
                else:
                    break

                depth += 1

        # Get ultimate parent (may be different from chain traversal)
        ultimate = self.get_ultimate_parent(lei)
        if ultimate:
            chain['ultimate_parent'] = ultimate

            # Check ultimate owner country
            if ultimate['country'] == 'CN':
                chain['china_owned'] = True
            if ultimate['country'] == 'RU':
                chain['russia_owned'] = True

        # Assess risk level
        chain['risk_level'] = self.assess_ownership_risk(chain).value

        return chain

    def assess_ownership_risk(self, chain: Dict) -> RiskLevel:
        """
        Assess ownership risk based on chain analysis

        Args:
            chain: Ownership chain data

        Returns:
            Risk level assessment
        """
        risk_factors = chain['risk_factors']

        # Critical risk - China/Russia ultimate owner
        if chain['china_owned']:
            risk_factors.append("Chinese ultimate ownership")
            return RiskLevel.CRITICAL

        if chain['russia_owned']:
            risk_factors.append("Russian ultimate ownership")
            return RiskLevel.CRITICAL

        # High risk - China/Russia in chain
        if any(c['country'] in ['CN', 'RU'] for c in chain['concern_countries']):
            risk_factors.append("China/Russia in ownership chain")
            return RiskLevel.HIGH

        # Medium risk - Other concern countries or complex structure
        if chain['concern_countries']:
            risk_factors.append("Concern country in ownership chain")
            return RiskLevel.MEDIUM

        if len(chain['ownership_chain']) > 5:
            risk_factors.append("Complex ownership structure (>5 levels)")
            return RiskLevel.MEDIUM

        # Low risk - Clear Western ownership
        if chain['ultimate_parent']:
            ultimate_country = chain['ultimate_parent']['country']
            # NATO/EU countries
            if ultimate_country in ['US', 'GB', 'FR', 'DE', 'IT', 'ES', 'NL', 'BE', 'CA']:
                return RiskLevel.LOW

        # Unknown - Unable to determine
        if not chain['direct_parent'] and not chain['ultimate_parent']:
            risk_factors.append("No ownership information available")
            return RiskLevel.UNKNOWN

        return RiskLevel.LOW

    def analyze_sector_ownership(self, leis: List[str], sector: str) -> Dict:
        """
        Analyze ownership patterns in a sector

        Args:
            leis: List of LEIs to analyze
            sector: Sector name

        Returns:
            Sector ownership analysis
        """
        results = {
            "sector": sector,
            "total_entities": len(leis),
            "analyzed": 0,
            "china_owned": [],
            "russia_owned": [],
            "concern_owned": [],
            "complex_structures": [],
            "risk_summary": {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
                "unknown": 0
            }
        }

        for lei in leis:
            logger.info(f"Analyzing ownership for {lei}")
            chain = self.trace_ownership_chain(lei)

            if chain['entity']:
                results['analyzed'] += 1

                # Track concerning ownership
                if chain['china_owned']:
                    results['china_owned'].append({
                        "lei": lei,
                        "name": chain['entity']['name'],
                        "ultimate_owner": chain['ultimate_parent']['name'] if chain['ultimate_parent'] else None
                    })

                if chain['russia_owned']:
                    results['russia_owned'].append({
                        "lei": lei,
                        "name": chain['entity']['name'],
                        "ultimate_owner": chain['ultimate_parent']['name'] if chain['ultimate_parent'] else None
                    })

                if chain['concern_countries']:
                    results['concern_owned'].append({
                        "lei": lei,
                        "name": chain['entity']['name'],
                        "concerns": chain['concern_countries']
                    })

                if len(chain['ownership_chain']) > 5:
                    results['complex_structures'].append({
                        "lei": lei,
                        "name": chain['entity']['name'],
                        "levels": len(chain['ownership_chain'])
                    })

                # Update risk summary
                results['risk_summary'][chain['risk_level']] += 1

        # Calculate percentages
        if results['analyzed'] > 0:
            results['china_ownership_pct'] = len(results['china_owned']) / results['analyzed'] * 100
            results['russia_ownership_pct'] = len(results['russia_owned']) / results['analyzed'] * 100
            results['concern_ownership_pct'] = len(results['concern_owned']) / results['analyzed'] * 100
            results['complex_structure_pct'] = len(results['complex_structures']) / results['analyzed'] * 100

        return results

    def search_by_name(self, company_name: str, country: Optional[str] = None) -> List[Dict]:
        """
        Search for companies by name (uses GLEIF search)
        Note: This requires using the GLEIF website or bulk download

        Args:
            company_name: Company name to search
            country: Optional country filter

        Returns:
            List of matching companies with LEIs
        """
        # The GLEIF API doesn't support search by name directly
        # You would need to use their bulk download or web interface
        # This is a placeholder for the implementation

        logger.info(f"Name search requires GLEIF bulk data or web scraping")
        logger.info(f"Visit: https://search.gleif.org/search/entity?q={company_name}")

        return []

    def generate_ownership_report(self, leis: List[str]) -> Dict:
        """
        Generate comprehensive ownership report for country

        Args:
            leis: List of LEIs to analyze

        Returns:
            Ownership analysis report
        """
        timestamp = datetime.now().isoformat()

        # Sector categorization (would need additional data source)
        sectors = {
            "aerospace": [],
            "technology": [],
            "defense": [],
            "energy": [],
            "other": leis  # For now, all in other
        }

        report = {
            "generated_at": timestamp,
            "country": self.country,
            "total_entities": len(leis),
            "sectors": {}
        }

        # Analyze each sector
        for sector_name, sector_leis in sectors.items():
            if sector_leis:
                logger.info(f"Analyzing {sector_name} sector ({len(sector_leis)} entities)")
                report['sectors'][sector_name] = self.analyze_sector_ownership(
                    sector_leis[:10],  # Limit for demonstration
                    sector_name
                )

        # Overall statistics
        total_analyzed = sum(s.get('analyzed', 0) for s in report['sectors'].values())
        total_china = sum(len(s.get('china_owned', [])) for s in report['sectors'].values())
        total_russia = sum(len(s.get('russia_owned', [])) for s in report['sectors'].values())

        report['summary'] = {
            "entities_analyzed": total_analyzed,
            "china_owned_count": total_china,
            "russia_owned_count": total_russia,
            "china_ownership_pct": (total_china / total_analyzed * 100) if total_analyzed > 0 else 0,
            "russia_ownership_pct": (total_russia / total_analyzed * 100) if total_analyzed > 0 else 0
        }

        # Critical findings
        report['critical_findings'] = []
        for sector_name, sector_data in report['sectors'].items():
            if sector_data.get('china_owned'):
                for entity in sector_data['china_owned']:
                    report['critical_findings'].append({
                        "type": "CHINESE_OWNERSHIP",
                        "sector": sector_name,
                        "entity": entity['name'],
                        "lei": entity['lei'],
                        "ultimate_owner": entity.get('ultimate_owner')
                    })

        # Save report
        output_file = self.output_dir / "ownership_analysis_report.json"
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"Ownership report saved to {output_file}")

        return report

def main():
    """Test GLEIF ownership tracking"""
    import sys

    country = sys.argv[1] if len(sys.argv) > 1 else "ITA"

    # Example LEIs (Leonardo, ENI, etc.)
    test_leis = [
        "549300MLUDYVRQOOXS22",  # Leonardo S.p.A.
        "BUCRF72VH5RBN7X3HF75",  # ENI S.p.A.
        # Add more Italian company LEIs here
    ]

    tracker = GLEIFOwnershipTracker(country)

    print(f"\n=== GLEIF Ownership Analysis for {country} ===\n")

    # Test single company
    if test_leis:
        test_lei = test_leis[0]
        print(f"Testing with LEI: {test_lei}")

        # Get basic info
        entity = tracker.get_lei_record(test_lei)
        if entity:
            print(f"Entity: {entity['name']}")
            print(f"Country: {entity['country']}")
            print(f"Status: {entity['status']}")

            # Trace ownership
            print("\nTracing ownership chain...")
            chain = tracker.trace_ownership_chain(test_lei)

            if chain['direct_parent']:
                print(f"Direct Parent: {chain['direct_parent']['name']} ({chain['direct_parent']['country']})")

            if chain['ultimate_parent']:
                print(f"Ultimate Parent: {chain['ultimate_parent']['name']} ({chain['ultimate_parent']['country']})")

            print(f"Risk Level: {chain['risk_level']}")

            if chain['risk_factors']:
                print("Risk Factors:")
                for factor in chain['risk_factors']:
                    print(f"  - {factor}")

            if chain['china_owned']:
                print("⚠️  WARNING: Chinese ultimate ownership detected!")

            if chain['russia_owned']:
                print("⚠️  WARNING: Russian ultimate ownership detected!")

    # Generate full report
    if len(test_leis) > 1:
        print("\nGenerating ownership report for all entities...")
        report = tracker.generate_ownership_report(test_leis)

        print(f"\nReport Summary:")
        print(f"Entities analyzed: {report['summary']['entities_analyzed']}")
        print(f"China-owned: {report['summary']['china_owned_count']} ({report['summary']['china_ownership_pct']:.1f}%)")
        print(f"Russia-owned: {report['summary']['russia_owned_count']} ({report['summary']['russia_ownership_pct']:.1f}%)")

        if report['critical_findings']:
            print(f"\n⚠️  CRITICAL FINDINGS: {len(report['critical_findings'])}")
            for finding in report['critical_findings'][:3]:  # Show first 3
                print(f"  - {finding['entity']}: {finding['type']}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()

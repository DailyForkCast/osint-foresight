"""
Eurostat COMEXT Trade Data Analyzer
Completely FREE access to EU trade statistics
No API key required - direct database access
Better than UN Comtrade for European trade analysis
"""

import json
import logging
import requests
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple
from pathlib import Path
from io import StringIO

logger = logging.getLogger(__name__)

class CriticalComponents:
    """HS codes for critical technology components"""

    # Semiconductors and electronics
    SEMICONDUCTORS = {
        "8541": "Semiconductor devices",
        "8542": "Electronic integrated circuits",
        "854231": "Electronic integrated circuits: Processors and controllers",
        "854232": "Electronic integrated circuits: Memories",
        "854233": "Electronic integrated circuits: Amplifiers",
        "854239": "Other integrated circuits"
    }

    # Rare earth and critical materials
    CRITICAL_MATERIALS = {
        "2805": "Alkali or alkaline-earth metals; rare-earth metals",
        "280530": "Rare-earth metals, scandium and yttrium",
        "2846": "Compounds of rare-earth metals",
        "8105": "Cobalt and articles thereof",
        "8112": "Beryllium, chromium, germanium, vanadium, gallium"
    }

    # Aerospace and defense
    AEROSPACE = {
        "8802": "Aircraft, spacecraft, and parts thereof",
        "8803": "Parts of aircraft and spacecraft",
        "880330": "Parts of aeroplanes or helicopters",
        "8805": "Aircraft launching gear; deck-arrestor",
        "9306": "Bombs, grenades, ammunition and parts"
    }

    # Advanced technology
    ADVANCED_TECH = {
        "9013": "Optical devices, lasers",
        "901320": "Lasers, other than laser diodes",
        "9027": "Instruments for physical or chemical analysis",
        "9031": "Measuring or checking instruments",
        "8471": "Automatic data processing machines (computers)",
        "847130": "Portable digital automatic data processing machines"
    }

    # Energy and batteries
    ENERGY = {
        "8506": "Primary cells and primary batteries",
        "8507": "Electric accumulators (batteries)",
        "850710": "Lead-acid accumulators",
        "850760": "Lithium-ion accumulators"
    }

class EurostatTradeAnalyzer:
    """
    Analyze EU trade data using Eurostat COMEXT
    Completely free, no authentication required
    """

    def __init__(self, country_iso2: str):
        """
        Initialize analyzer

        Args:
            country_iso2: Two-letter country code (e.g., 'IT' for Italy)
        """
        self.country = country_iso2
        self.base_url = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data"
        self.output_dir = Path(f"artifacts/{country_iso2}/phase04_supply_chain")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Map of country codes
        self.eu_countries = {
            'AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR',
            'DE', 'GR', 'HU', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'NL',
            'PL', 'PT', 'RO', 'SK', 'SI', 'ES', 'SE'
        }

        # Countries of concern for supply chain
        self.concern_partners = {
            'CN': 'China',
            'RU': 'Russia',
            'BY': 'Belarus',
            'IR': 'Iran'
        }

        # Session for connection pooling
        self.session = requests.Session()

    def get_trade_data(self, dataset: str, filters: Dict) -> pd.DataFrame:
        """
        Get trade data from Eurostat API

        Args:
            dataset: Eurostat dataset code (e.g., 'DS-018995' for EU trade)
            filters: Query filters

        Returns:
            Trade data as DataFrame
        """
        try:
            # Construct URL with filters
            filter_string = ""
            for key, value in filters.items():
                if isinstance(value, list):
                    filter_string += f"&{key}=" + "+".join(value)
                else:
                    filter_string += f"&{key}={value}"

            url = f"{self.base_url}/{dataset}?format=JSON{filter_string}"

            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            data = response.json()

            # Parse the complex Eurostat JSON structure
            df = self._parse_eurostat_json(data)
            return df

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching Eurostat data: {e}")
            return pd.DataFrame()

    def _parse_eurostat_json(self, data: Dict) -> pd.DataFrame:
        """
        Parse Eurostat's complex JSON structure

        Args:
            data: Raw JSON from Eurostat API

        Returns:
            Parsed DataFrame
        """
        # This is simplified - actual Eurostat JSON is quite complex
        # In production, you'd want to use the eurostat Python package
        values = data.get('value', {})
        dimensions = data.get('dimension', {})

        # Convert to DataFrame (simplified)
        records = []
        for key, value in values.items():
            record = {'value': value, 'index': key}
            records.append(record)

        return pd.DataFrame(records)

    def analyze_component_dependence(self, hs_code: str, year: int = 2024) -> Dict:
        """
        Analyze import dependence for critical component

        Args:
            hs_code: Harmonized System code
            year: Year to analyze

        Returns:
            Dependency analysis
        """
        analysis = {
            "hs_code": hs_code,
            "description": CriticalComponents.SEMICONDUCTORS.get(hs_code, "Unknown"),
            "year": year,
            "total_imports": 0,
            "china_imports": 0,
            "china_dependence": 0,
            "top_suppliers": [],
            "concern_country_share": 0,
            "risk_level": "UNKNOWN"
        }

        # For Eurostat, we would construct a specific query
        # This is a simplified example - actual implementation would use proper API
        filters = {
            "reporter": self.country,
            "partner": ["CN", "US", "DE", "JP", "KR", "TW"],
            "product": hs_code,
            "flow": "IMPORT",
            "period": str(year)
        }

        # Get trade data (simplified for demo)
        logger.info(f"Analyzing imports for HS {hs_code}")

        # Mock data for demonstration
        # In reality, this would come from the API
        mock_data = {
            "CN": 45000000,  # China: 45M EUR
            "US": 20000000,  # USA: 20M EUR
            "DE": 15000000,  # Germany: 15M EUR
            "JP": 10000000,  # Japan: 10M EUR
            "KR": 5000000,   # Korea: 5M EUR
            "TW": 5000000    # Taiwan: 5M EUR
        }

        total = sum(mock_data.values())
        analysis['total_imports'] = total
        analysis['china_imports'] = mock_data.get('CN', 0)

        if total > 0:
            analysis['china_dependence'] = (mock_data.get('CN', 0) / total) * 100

            # Calculate concern country share
            concern_total = sum(mock_data.get(c, 0) for c in self.concern_partners.keys())
            analysis['concern_country_share'] = (concern_total / total) * 100

            # Top suppliers
            sorted_suppliers = sorted(mock_data.items(), key=lambda x: x[1], reverse=True)
            analysis['top_suppliers'] = [
                {
                    "country": country,
                    "value": value,
                    "share": (value / total) * 100
                }
                for country, value in sorted_suppliers[:5]
            ]

        # Risk assessment
        if analysis['china_dependence'] > 50:
            analysis['risk_level'] = "CRITICAL"
        elif analysis['china_dependence'] > 30:
            analysis['risk_level'] = "HIGH"
        elif analysis['china_dependence'] > 15:
            analysis['risk_level'] = "MEDIUM"
        else:
            analysis['risk_level'] = "LOW"

        return analysis

    def analyze_critical_components(self) -> Dict:
        """
        Analyze all critical component categories

        Returns:
            Comprehensive supply chain risk assessment
        """
        timestamp = datetime.now().isoformat()

        report = {
            "generated_at": timestamp,
            "country": self.country,
            "categories": {},
            "critical_dependencies": [],
            "recommendations": []
        }

        # Analyze each category
        categories = [
            ("semiconductors", CriticalComponents.SEMICONDUCTORS),
            ("critical_materials", CriticalComponents.CRITICAL_MATERIALS),
            ("aerospace", CriticalComponents.AEROSPACE),
            ("advanced_tech", CriticalComponents.ADVANCED_TECH),
            ("energy", CriticalComponents.ENERGY)
        ]

        for category_name, hs_codes in categories:
            logger.info(f"Analyzing {category_name} category")

            category_analysis = {
                "components": [],
                "average_china_dependence": 0,
                "high_risk_count": 0
            }

            china_deps = []
            for hs_code, description in list(hs_codes.items())[:3]:  # Limit for demo
                component = self.analyze_component_dependence(hs_code)
                category_analysis['components'].append(component)

                china_deps.append(component['china_dependence'])

                if component['risk_level'] in ['CRITICAL', 'HIGH']:
                    category_analysis['high_risk_count'] += 1

                    # Add to critical dependencies
                    if component['china_dependence'] > 40:
                        report['critical_dependencies'].append({
                            "category": category_name,
                            "hs_code": hs_code,
                            "description": description,
                            "china_dependence": component['china_dependence'],
                            "risk_level": component['risk_level']
                        })

            if china_deps:
                category_analysis['average_china_dependence'] = sum(china_deps) / len(china_deps)

            report['categories'][category_name] = category_analysis

        # Generate recommendations
        if report['critical_dependencies']:
            report['recommendations'].append(
                f"URGENT: {len(report['critical_dependencies'])} components with >40% China dependence require supply chain diversification"
            )

        semiconductors = report['categories'].get('semiconductors', {})
        if semiconductors.get('average_china_dependence', 0) > 30:
            report['recommendations'].append(
                f"Semiconductor supply chain vulnerability: {semiconductors['average_china_dependence']:.1f}% average China dependence"
            )

        return report

    def track_trade_trends(self, hs_codes: List[str], years: int = 5) -> Dict:
        """
        Track multi-year trade trends for components

        Args:
            hs_codes: List of HS codes to track
            years: Number of years to analyze

        Returns:
            Trend analysis
        """
        current_year = datetime.now().year
        start_year = current_year - years

        trends = {
            "period": f"{start_year}-{current_year}",
            "components": {}
        }

        for hs_code in hs_codes:
            logger.info(f"Tracking trends for HS {hs_code}")

            component_trends = {
                "description": CriticalComponents.SEMICONDUCTORS.get(hs_code, ""),
                "yearly_data": [],
                "china_share_trend": [],
                "trend_direction": None
            }

            # Analyze each year
            for year in range(start_year, current_year + 1):
                year_data = self.analyze_component_dependence(hs_code, year)
                component_trends['yearly_data'].append({
                    "year": year,
                    "china_dependence": year_data['china_dependence'],
                    "total_imports": year_data['total_imports']
                })
                component_trends['china_share_trend'].append(year_data['china_dependence'])

            # Determine trend direction
            if len(component_trends['china_share_trend']) >= 3:
                recent = component_trends['china_share_trend'][-3:]
                if all(recent[i] <= recent[i+1] for i in range(len(recent)-1)):
                    component_trends['trend_direction'] = "INCREASING"
                elif all(recent[i] >= recent[i+1] for i in range(len(recent)-1)):
                    component_trends['trend_direction'] = "DECREASING"
                else:
                    component_trends['trend_direction'] = "STABLE"

            trends['components'][hs_code] = component_trends

        return trends

    def generate_supply_chain_report(self) -> Dict:
        """
        Generate comprehensive supply chain risk report

        Returns:
            Supply chain assessment report
        """
        logger.info(f"Generating supply chain report for {self.country}")

        # Analyze critical components
        component_analysis = self.analyze_critical_components()

        # Track trends for key semiconductors
        key_semiconductors = ["8542", "8541", "854231"]
        trends = self.track_trade_trends(key_semiconductors, years=3)

        report = {
            "generated_at": datetime.now().isoformat(),
            "country": self.country,
            "component_analysis": component_analysis,
            "trend_analysis": trends,
            "risk_summary": {
                "critical_dependencies": len(component_analysis['critical_dependencies']),
                "categories_at_risk": [],
                "overall_china_dependence": 0
            },
            "recommendations": component_analysis['recommendations']
        }

        # Calculate overall risk metrics
        total_china_dep = []
        for category, data in component_analysis['categories'].items():
            if data['average_china_dependence'] > 30:
                report['risk_summary']['categories_at_risk'].append({
                    "category": category,
                    "china_dependence": data['average_china_dependence'],
                    "high_risk_components": data['high_risk_count']
                })
            total_china_dep.append(data['average_china_dependence'])

        if total_china_dep:
            report['risk_summary']['overall_china_dependence'] = sum(total_china_dep) / len(total_china_dep)

        # Add trend-based recommendations
        for hs_code, trend_data in trends['components'].items():
            if trend_data['trend_direction'] == "INCREASING":
                report['recommendations'].append(
                    f"WARNING: China dependence increasing for {hs_code} ({trend_data['description']})"
                )

        # Save report
        output_file = self.output_dir / "supply_chain_risk_report.json"
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"Supply chain report saved to {output_file}")

        return report

def main():
    """Test Eurostat trade analysis"""
    import sys

    country = sys.argv[1] if len(sys.argv) > 1 else "IT"  # Italy

    analyzer = EurostatTradeAnalyzer(country)

    print(f"\n=== Eurostat Trade Analysis for {country} ===\n")

    # Test single component analysis
    test_hs = "8542"  # Integrated circuits
    print(f"Analyzing component: {test_hs} (Integrated Circuits)")

    component = analyzer.analyze_component_dependence(test_hs)

    print(f"\nResults for HS {test_hs}:")
    print(f"  Total imports: €{component['total_imports']:,.0f}")
    print(f"  China imports: €{component['china_imports']:,.0f}")
    print(f"  China dependence: {component['china_dependence']:.1f}%")
    print(f"  Risk level: {component['risk_level']}")

    print("\n  Top suppliers:")
    for supplier in component['top_suppliers'][:3]:
        print(f"    - {supplier['country']}: {supplier['share']:.1f}%")

    # Generate full report
    print("\n\nGenerating comprehensive supply chain report...")
    report = analyzer.generate_supply_chain_report()

    print(f"\nReport Summary:")
    print(f"  Critical dependencies: {report['risk_summary']['critical_dependencies']}")
    print(f"  Overall China dependence: {report['risk_summary']['overall_china_dependence']:.1f}%")
    print(f"  Categories at risk: {len(report['risk_summary']['categories_at_risk'])}")

    if report['risk_summary']['categories_at_risk']:
        print("\n  High-risk categories:")
        for category in report['risk_summary']['categories_at_risk']:
            print(f"    - {category['category']}: {category['china_dependence']:.1f}% China dependence")

    if report['recommendations']:
        print("\n  Recommendations:")
        for rec in report['recommendations'][:3]:
            print(f"    • {rec}")

    print(f"\nNote: This uses mock data for demonstration.")
    print(f"For real analysis, register at https://ec.europa.eu/eurostat/")
    print(f"Eurostat COMEXT provides free access to all EU trade data.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()

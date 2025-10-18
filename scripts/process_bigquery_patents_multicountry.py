#!/usr/bin/env python3
"""
Google BigQuery Patents Multi-Country Analysis
Analyzes patent collaborations between China and all countries of interest
Using FREE public patents dataset
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict
from google.cloud import bigquery
from google.oauth2 import service_account

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bigquery_patents_processing.log'),
        logging.StreamHandler()
    ]
)

class PatentsMultiCountryAnalyzer:
    """Analyze patent collaborations between China and target countries"""

    def __init__(self, output_dir: str = "data/processed/patents_multicountry"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize BigQuery client
        self.client = self.setup_bigquery_client()

        # Countries of interest (from our expanded list)
        self.countries = {
            # EU Core
            "DE": "Germany", "FR": "France", "IT": "Italy", "ES": "Spain",
            "NL": "Netherlands", "BE": "Belgium", "LU": "Luxembourg",

            # Nordic
            "SE": "Sweden", "DK": "Denmark", "FI": "Finland", "NO": "Norway", "IS": "Iceland",

            # Central/Eastern EU
            "PL": "Poland", "CZ": "Czech Republic", "SK": "Slovakia",
            "HU": "Hungary", "RO": "Romania", "BG": "Bulgaria",
            "HR": "Croatia", "SI": "Slovenia", "EE": "Estonia",
            "LV": "Latvia", "LT": "Lithuania",

            # Mediterranean
            "GR": "Greece", "CY": "Cyprus", "MT": "Malta", "PT": "Portugal",

            # Other EU
            "AT": "Austria", "IE": "Ireland", "CH": "Switzerland", "GB": "United Kingdom",

            # EU Candidates & Balkans
            "AL": "Albania", "MK": "North Macedonia", "RS": "Serbia", "ME": "Montenegro",
            "BA": "Bosnia and Herzegovina", "TR": "Turkey", "UA": "Ukraine", "XK": "Kosovo",

            # Strategic Non-EU
            "GE": "Georgia", "AM": "Armenia",

            # Five Eyes
            "US": "United States", "CA": "Canada", "AU": "Australia", "NZ": "New Zealand",

            # Asia-Pacific
            "JP": "Japan", "KR": "South Korea", "SG": "Singapore", "TW": "Taiwan",
            "IN": "India", "TH": "Thailand", "MY": "Malaysia", "VN": "Vietnam",

            # Middle East
            "IL": "Israel", "AE": "United Arab Emirates", "SA": "Saudi Arabia",

            # Latin America
            "BR": "Brazil", "MX": "Mexico", "AR": "Argentina", "CL": "Chile",

            # Africa
            "ZA": "South Africa", "EG": "Egypt", "KE": "Kenya", "NG": "Nigeria",

            # Strategic Partners
            "RU": "Russia", "BY": "Belarus", "KZ": "Kazakhstan"
        }

        # Dual-use technology categories
        self.tech_categories = {
            "artificial_intelligence": [
                "artificial intelligence", "machine learning", "deep learning",
                "neural network", "computer vision", "natural language"
            ],
            "quantum": [
                "quantum computing", "quantum communication", "quantum cryptography",
                "quantum entanglement", "quantum algorithm"
            ],
            "semiconductors": [
                "semiconductor", "microprocessor", "integrated circuit",
                "chip design", "lithography", "silicon wafer"
            ],
            "biotechnology": [
                "biotechnology", "genetic engineering", "CRISPR",
                "gene therapy", "synthetic biology"
            ],
            "telecommunications": [
                "5G", "6G", "wireless communication", "telecommunications",
                "network infrastructure", "fiber optic"
            ],
            "aerospace": [
                "aerospace", "satellite", "rocket", "missile",
                "space technology", "launch vehicle", "hypersonic"
            ],
            "nuclear": [
                "nuclear reactor", "uranium enrichment", "nuclear fuel",
                "fusion", "fission", "radioactive"
            ],
            "cybersecurity": [
                "cybersecurity", "encryption", "cryptography",
                "network security", "malware", "cyber warfare"
            ],
            "drones": [
                "unmanned aerial", "UAV", "drone", "autonomous flight",
                "remote piloting"
            ],
            "robotics": [
                "robotics", "autonomous systems", "robotic arm",
                "industrial robot", "service robot"
            ]
        }

        # Initialize results storage
        self.results = {
            "metadata": {
                "processing_date": datetime.now().isoformat(),
                "countries_analyzed": len(self.countries),
                "tech_categories": len(self.tech_categories),
                "data_source": "Google BigQuery patents-public-data"
            },
            "by_country": defaultdict(list),
            "by_technology": defaultdict(list),
            "temporal_analysis": defaultdict(lambda: defaultdict(int)),
            "risk_assessment": []
        }

    def setup_bigquery_client(self):
        """Setup BigQuery client with authentication"""
        try:
            # Try to use application default credentials
            client = bigquery.Client()
            logging.info("BigQuery client initialized with default credentials")
            return client
        except Exception as e:
            logging.warning(f"Could not use default credentials: {e}")

            # Try to use service account if available
            cred_path = Path(".env.local")
            if cred_path.exists():
                try:
                    client = bigquery.Client.from_service_account_json(str(cred_path))
                    logging.info("BigQuery client initialized with service account")
                    return client
                except Exception as e:
                    logging.error(f"Could not use service account: {e}")

            # Use public access (limited but free)
            logging.info("Using public BigQuery access (rate limited)")
            return bigquery.Client(project="patents-public-data")

    def analyze_china_collaborations(self, country_code: str, limit: int = 1000):
        """Analyze patent collaborations between China and a specific country"""

        country_name = self.countries.get(country_code, country_code)
        logging.info(f"Analyzing China-{country_name} patent collaborations...")

        # Query for joint patents
        query = f"""
        SELECT DISTINCT
            p.publication_number,
            p.family_id,
            ARRAY_AGG(DISTINCT t.text IGNORE NULLS) as title,
            ARRAY_AGG(DISTINCT a.text IGNORE NULLS) as abstract,
            p.filing_date,
            p.publication_date,
            p.inventor_harmonized,
            p.assignee_harmonized,
            p.cpc
        FROM
            `patents-public-data.patents.publications` p,
            UNNEST(p.title_localized) as t,
            UNNEST(p.abstract_localized) as a,
            UNNEST(p.assignee_harmonized) as assignee_cn,
            UNNEST(p.assignee_harmonized) as assignee_target
        WHERE
            p.publication_date >= 20000101
            AND assignee_cn.country_code = 'CN'
            AND assignee_target.country_code = '{country_code}'
            AND assignee_cn != assignee_target
        GROUP BY
            p.publication_number,
            p.family_id,
            p.filing_date,
            p.publication_date,
            p.inventor_harmonized,
            p.assignee_harmonized,
            p.cpc
        LIMIT {limit}
        """

        try:
            # Execute query
            query_job = self.client.query(query)
            results = query_job.result()

            patents = []
            for row in results:
                # Handle aggregated arrays from query
                title = row.title[0] if row.title else None
                abstract = row.abstract[0] if row.abstract else None

                patent_data = {
                    "publication_number": row.publication_number,
                    "family_id": row.family_id,
                    "title": title,
                    "abstract": abstract,
                    "filing_date": str(row.filing_date) if row.filing_date else None,
                    "publication_date": str(row.publication_date) if row.publication_date else None,
                    "technology_categories": self.classify_technology(title, abstract),
                    "risk_level": "MEDIUM",  # Default, will enhance
                    "verification": {
                        "source": "Google BigQuery patents-public-data",
                        "query_timestamp": datetime.now().isoformat(),
                        "reproduction_query": query.replace('\n', ' ').strip()
                    }
                }

                # Assess risk based on technology
                if any(cat in ["artificial_intelligence", "quantum", "semiconductors", "nuclear"]
                       for cat in patent_data["technology_categories"]):
                    patent_data["risk_level"] = "CRITICAL"
                elif any(cat in ["telecommunications", "aerospace", "cybersecurity", "drones"]
                         for cat in patent_data["technology_categories"]):
                    patent_data["risk_level"] = "HIGH"

                patents.append(patent_data)

                # Store by country
                self.results["by_country"][country_code].append(patent_data)

                # Store by technology
                for tech in patent_data["technology_categories"]:
                    self.results["by_technology"][tech].append({
                        "country": country_code,
                        "patent": patent_data
                    })

                # Temporal analysis
                if patent_data["publication_date"]:
                    year = patent_data["publication_date"][:4]
                    self.results["temporal_analysis"][year][country_code] += 1

            logging.info(f"Found {len(patents)} China-{country_name} patent collaborations")
            return patents

        except Exception as e:
            logging.error(f"Error querying patents for {country_name}: {e}")
            return []

    def classify_technology(self, title: str, abstract: str) -> List[str]:
        """Classify patent into technology categories"""
        categories = []
        text = f"{title or ''} {abstract or ''}".lower()

        for category, keywords in self.tech_categories.items():
            if any(keyword.lower() in text for keyword in keywords):
                categories.append(category)

        if not categories:
            categories.append("other")

        return categories

    def analyze_all_countries(self):
        """Analyze patent collaborations for all countries"""
        logging.info(f"Starting multi-country patent analysis for {len(self.countries)} countries...")

        for country_code, country_name in self.countries.items():
            logging.info(f"Processing {country_name} ({country_code})...")
            self.analyze_china_collaborations(country_code, limit=100)  # Start with 100 per country

            # Save checkpoint after each country
            self.save_checkpoint()

        # Generate final analysis
        self.generate_risk_assessment()
        self.save_results()
        self.generate_report()

    def generate_risk_assessment(self):
        """Generate country risk assessment based on patent collaborations"""
        country_risks = []

        for country_code, patents in self.results["by_country"].items():
            if patents:
                critical_count = sum(1 for p in patents if p["risk_level"] == "CRITICAL")
                high_count = sum(1 for p in patents if p["risk_level"] == "HIGH")

                risk_score = (critical_count * 10) + (high_count * 5) + len(patents)

                country_risks.append({
                    "country_code": country_code,
                    "country_name": self.countries[country_code],
                    "total_patents": len(patents),
                    "critical_tech_patents": critical_count,
                    "high_risk_patents": high_count,
                    "risk_score": risk_score,
                    "top_technologies": self.get_top_technologies(patents)
                })

        # Sort by risk score
        country_risks.sort(key=lambda x: x["risk_score"], reverse=True)
        self.results["risk_assessment"] = country_risks

    def get_top_technologies(self, patents: List[Dict]) -> List[str]:
        """Get top technology categories from patent list"""
        tech_count = defaultdict(int)
        for patent in patents:
            for tech in patent.get("technology_categories", []):
                tech_count[tech] += 1

        return [tech for tech, _ in sorted(tech_count.items(),
                                          key=lambda x: x[1],
                                          reverse=True)[:3]]

    def save_checkpoint(self):
        """Save processing checkpoint"""
        checkpoint_file = self.output_dir / "checkpoint.json"
        with open(checkpoint_file, 'w') as f:
            json.dump({
                "last_update": datetime.now().isoformat(),
                "countries_processed": list(self.results["by_country"].keys()),
                "total_patents": sum(len(p) for p in self.results["by_country"].values())
            }, f, indent=2)

    def save_results(self):
        """Save all results to structured output"""
        # Save by country
        for country_code, patents in self.results["by_country"].items():
            if patents:
                country_dir = self.output_dir / "by_country" / f"{country_code}_china"
                country_dir.mkdir(parents=True, exist_ok=True)

                with open(country_dir / "patents.json", 'w') as f:
                    json.dump(patents, f, indent=2)

        # Save by technology
        for tech, items in self.results["by_technology"].items():
            if items:
                tech_dir = self.output_dir / "by_technology" / tech
                tech_dir.mkdir(parents=True, exist_ok=True)

                with open(tech_dir / "patents.json", 'w') as f:
                    json.dump(items, f, indent=2)

        # Save temporal analysis
        temporal_dir = self.output_dir / "temporal"
        temporal_dir.mkdir(exist_ok=True)

        with open(temporal_dir / "yearly_collaborations.json", 'w') as f:
            json.dump(dict(self.results["temporal_analysis"]), f, indent=2)

        # Save risk assessment
        with open(self.output_dir / "risk_assessment.json", 'w') as f:
            json.dump(self.results["risk_assessment"], f, indent=2)

    def generate_report(self):
        """Generate comprehensive markdown report"""
        report = f"""# Google BigQuery Patents Multi-Country Analysis Report

## Executive Summary
- **Countries Analyzed:** {len(self.results['by_country'])}
- **Total China Collaboration Patents Found:** {sum(len(p) for p in self.results['by_country'].values())}
- **Processing Date:** {datetime.now().strftime('%Y-%m-%d')}
- **Data Source:** Google BigQuery patents-public-data (FREE tier)

## Top Risk Countries (by China Patent Collaboration)
"""

        # Add top 10 countries by risk
        for i, country in enumerate(self.results["risk_assessment"][:10], 1):
            report += f"""
### {i}. {country['country_name']} ({country['country_code']})
- **Total Patents with China:** {country['total_patents']}
- **Critical Technology Patents:** {country['critical_tech_patents']}
- **High Risk Patents:** {country['high_risk_patents']}
- **Risk Score:** {country['risk_score']}
- **Top Technologies:** {', '.join(country['top_technologies'])}
"""

        # Add technology breakdown
        report += """
## Technology Category Analysis
"""
        for tech, items in self.results["by_technology"].items():
            if items:
                report += f"- **{tech}:** {len(items)} patents\n"

        # Add temporal trends
        report += """
## Temporal Trends
"""
        yearly_totals = {}
        for year, countries in self.results["temporal_analysis"].items():
            yearly_totals[year] = sum(countries.values())

        for year in sorted(yearly_totals.keys())[-10:]:  # Last 10 years
            report += f"- **{year}:** {yearly_totals[year]} patents\n"

        report += """
## Verification
All findings can be verified using Google BigQuery with the provided queries.
Each patent includes reproduction instructions for third-party validation.

---
*Report generated using FREE Google BigQuery public patents dataset*
"""

        # Save report
        with open(self.output_dir / "PATENTS_ANALYSIS_REPORT.md", 'w') as f:
            f.write(report)

        logging.info(f"Report saved to {self.output_dir}/PATENTS_ANALYSIS_REPORT.md")


def main():
    """Main execution function"""
    logging.info("=" * 50)
    logging.info("Starting Google BigQuery Patents Multi-Country Analysis")
    logging.info("=" * 50)

    analyzer = PatentsMultiCountryAnalyzer()

    # Test with a few countries first
    test_countries = ["US", "DE", "JP", "KR", "IL"]

    logging.info(f"Testing with {len(test_countries)} countries first...")

    for country in test_countries:
        analyzer.analyze_china_collaborations(country, limit=50)

    # Generate reports
    analyzer.generate_risk_assessment()
    analyzer.save_results()
    analyzer.generate_report()

    logging.info("=" * 50)
    logging.info("Patents analysis complete!")
    logging.info(f"Results saved to: data/processed/patents_multicountry")
    logging.info("=" * 50)


if __name__ == "__main__":
    main()

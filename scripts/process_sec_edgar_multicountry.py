#!/usr/bin/env python3
"""
SEC EDGAR Multi-Country Analysis
Analyzes foreign company filings in US markets with focus on China and strategic countries
Using SEC EDGAR API (FREE)
"""

import os
import json
import logging
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict
import time

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sec_edgar_processing.log'),
        logging.StreamHandler()
    ]
)

class SECEdgarMultiCountryAnalyzer:
    """Analyze foreign company SEC filings with focus on China relationships"""

    def __init__(self, output_dir: str = "data/processed/sec_edgar_multicountry"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # SEC EDGAR API settings
        self.base_url = "https://data.sec.gov"
        self.headers = {
            "User-Agent": "OSINT-Foresight Research (osint-research@example.com)"
        }

        # Countries of interest - same as patent analysis
        self.countries = {
            # Priority countries for SEC filings
            "CN": "China", "HK": "Hong Kong", "TW": "Taiwan",
            "JP": "Japan", "KR": "South Korea", "SG": "Singapore",
            "IL": "Israel", "IN": "India", "RU": "Russia",

            # EU countries that may have US listings
            "DE": "Germany", "FR": "France", "IT": "Italy", "GB": "United Kingdom",
            "NL": "Netherlands", "CH": "Switzerland", "IE": "Ireland",
            "SE": "Sweden", "DK": "Denmark", "NO": "Norway",

            # Other strategic countries
            "CA": "Canada", "AU": "Australia", "BR": "Brazil",
            "MX": "Mexico", "SA": "Saudi Arabia", "AE": "UAE"
        }

        # Risk indicators in filings
        self.risk_indicators = {
            "china_exposure": [
                "China operations", "Chinese market", "PRC", "mainland China",
                "China revenue", "China subsidiary", "China joint venture"
            ],
            "technology_transfer": [
                "technology transfer", "technology licensing", "joint development",
                "research collaboration", "technology sharing"
            ],
            "supply_chain": [
                "supply chain", "Chinese suppliers", "manufacturing in China",
                "China factory", "Shenzhen", "Shanghai facility"
            ],
            "regulatory_risk": [
                "CFIUS", "export controls", "sanctions", "national security",
                "foreign ownership", "data localization", "cybersecurity"
            ],
            "vie_structure": [
                "VIE", "variable interest entity", "contractual arrangements",
                "control through contracts", "Cayman Islands", "BVI"
            ]
        }

        # SEC form types to analyze
        self.form_types = [
            "20-F",  # Annual report for foreign companies
            "6-K",   # Current report for foreign companies
            "F-1",   # Registration for foreign IPOs
            "8-K",   # Current report (may include China-related material events)
            "10-K",  # Annual report (for US companies with China exposure)
            "10-Q",  # Quarterly report
            "DEF 14A", # Proxy statement (ownership info)
            "SC 13D",  # Beneficial ownership >5%
            "SC 13G"   # Beneficial ownership passive
        ]

        # Initialize results
        self.results = {
            "metadata": {
                "processing_date": datetime.now().isoformat(),
                "countries_analyzed": len(self.countries),
                "data_source": "SEC EDGAR API"
            },
            "by_country": defaultdict(list),
            "by_risk_type": defaultdict(list),
            "china_exposed_companies": [],
            "vie_structures": [],
            "risk_assessment": []
        }

    def search_company_filings(self, country_code: str, limit: int = 100):
        """Search for company filings from specific country"""

        country_name = self.countries.get(country_code, country_code)
        logging.info(f"Searching SEC filings for {country_name} companies...")

        # Get company tickers list
        tickers_url = "https://www.sec.gov/files/company_tickers.json"

        # Also search for well-known companies from each country
        known_companies = {
            "CN": ["BABA", "BIDU", "JD", "NIO", "XPEV", "LI", "PDD", "BILI", "IQ", "TME"],
            "HK": ["HK", "HSBC"],
            "IL": ["NICE", "CHKP", "WIX", "FVRR", "MNDY"],
            "DE": ["SAP", "SIEGY"],
            "JP": ["SONY", "TM", "HMC", "NTT"]
        }

        try:
            # Get all company tickers
            response = requests.get(tickers_url, headers=self.headers)
            time.sleep(0.1)  # Rate limiting

            if response.status_code == 200:
                all_companies = response.json()

                # Filter for country-related companies
                country_companies = []

                # First, add known companies from the country
                if country_code in known_companies:
                    for ticker in known_companies[country_code]:
                        for idx, company_data in all_companies.items():
                            if company_data.get("ticker", "") == ticker:
                                country_companies.append({
                                    "cik": str(company_data.get("cik_str", "")).zfill(10),
                                    "name": company_data.get("title", ""),
                                    "ticker": ticker,
                                    "country": country_code
                                })
                                break

                # Also search by country name in company title
                for idx, company_data in all_companies.items():
                    title = company_data.get("title", "").upper()
                    if country_name.upper() in title or \
                       (country_code == "CN" and ("CHINA" in title or "CHINESE" in title)) or \
                       (country_code == "IL" and "ISRAEL" in title) or \
                       (country_code == "HK" and "HONG KONG" in title):
                        cik_str = str(company_data.get("cik_str", "")).zfill(10)
                        if not any(c["cik"] == cik_str for c in country_companies):
                            country_companies.append({
                                "cik": cik_str,
                                "name": company_data.get("title", ""),
                                "ticker": company_data.get("ticker", ""),
                                "country": country_code
                            })

                # Analyze recent filings for each company
                logging.info(f"Analyzing filings for {len(country_companies[:limit])} {country_name} companies...")
                for company in country_companies[:limit]:
                    logging.debug(f"Processing {company['name']} ({company.get('ticker', 'No ticker')})")
                    self.analyze_company_filings(company)

                logging.info(f"Found {len(country_companies)} {country_name} companies in SEC")

        except Exception as e:
            logging.error(f"Error searching {country_name} companies: {e}")

    def analyze_company_filings(self, company: Dict):
        """Analyze specific company's recent filings"""

        cik = company["cik"].zfill(10)  # CIK must be 10 digits
        logging.debug(f"Fetching filings for {company['name']} (CIK: {cik})")

        try:
            # Get company submissions
            submissions_url = f"{self.base_url}/submissions/CIK{cik}.json"
            response = requests.get(submissions_url, headers=self.headers)
            time.sleep(0.1)  # Rate limiting

            if response.status_code == 200:
                data = response.json()

                # Extract recent filings
                recent_filings = data.get("filings", {}).get("recent", {})

                # Analyze each filing for risk indicators
                num_filings = len(recent_filings.get("form", []))
                logging.debug(f"Found {num_filings} filings for {company['name']}")

                for i in range(min(5, num_filings)):  # Reduce to 5 for faster testing
                    filing = {
                        "form": recent_filings["form"][i],
                        "date": recent_filings["filingDate"][i],
                        "accession": recent_filings["accessionNumber"][i],
                        "primary_doc": recent_filings.get("primaryDocument", [None] * num_filings)[i],
                        "company": company["name"],
                        "country": company["country"],
                        "cik": company["cik"]
                    }

                    logging.debug(f"Checking filing {filing['form']} dated {filing['date']}")

                    # Check if filing type is relevant
                    if filing["form"] in self.form_types:
                        logging.debug(f"Analyzing {filing['form']} content...")
                        risks = self.analyze_filing_content(filing)
                        if risks:
                            logging.info(f"Found risks in {company['name']} filing: {risks['risk_score']}")
                            filing["risks"] = risks
                            self.store_finding(filing)
                        else:
                            logging.debug(f"No risks found in {filing['form']}")
            else:
                logging.warning(f"Failed to get submissions for {company['name']}: HTTP {response.status_code}")

        except Exception as e:
            logging.error(f"Error analyzing company {company['name']}: {e}")

    def analyze_filing_content(self, filing: Dict) -> Dict:
        """Analyze filing content for risk indicators"""

        risks = {
            "china_exposure": False,
            "technology_transfer": False,
            "supply_chain": False,
            "regulatory_risk": False,
            "vie_structure": False,
            "risk_score": 0
        }

        try:
            # Get filing document
            cik_unpadded = filing['cik'].lstrip('0')  # Remove leading zeros
            accession_no_dash = filing['accession'].replace('-', '')

            # Use primary document if available, otherwise use index
            if filing.get('primary_doc'):
                doc_url = f"https://www.sec.gov/Archives/edgar/data/{cik_unpadded}/{accession_no_dash}/{filing['primary_doc']}"
            else:
                doc_url = f"https://www.sec.gov/Archives/edgar/data/{cik_unpadded}/{accession_no_dash}/{filing['accession']}-index.html"

            response = requests.get(doc_url, headers=self.headers)
            time.sleep(0.1)

            if response.status_code == 200:
                content = response.text.lower()

                # Check for risk indicators
                for risk_type, keywords in self.risk_indicators.items():
                    for keyword in keywords:
                        if keyword.lower() in content:
                            risks[risk_type] = True
                            risks["risk_score"] += 10
                            break

                # Special scoring for China exposure
                china_mentions = content.count("china") + content.count("chinese") + content.count("prc")
                if china_mentions > 50:
                    risks["risk_score"] += 20
                    risks["high_china_exposure"] = True

        except Exception as e:
            logging.error(f"Error analyzing filing content: {e}")

        return risks if risks["risk_score"] > 0 else None

    def store_finding(self, filing: Dict):
        """Store filing with risk indicators"""

        # Store by country
        self.results["by_country"][filing["country"]].append(filing)

        # Store by risk type
        for risk_type in filing.get("risks", {}):
            if filing["risks"].get(risk_type):
                self.results["by_risk_type"][risk_type].append(filing)

        # Track China-exposed companies
        if filing.get("risks", {}).get("china_exposure"):
            self.results["china_exposed_companies"].append({
                "company": filing["company"],
                "country": filing["country"],
                "risk_score": filing["risks"]["risk_score"],
                "filing_date": filing["date"]
            })

        # Track VIE structures
        if filing.get("risks", {}).get("vie_structure"):
            self.results["vie_structures"].append({
                "company": filing["company"],
                "country": filing["country"],
                "filing": filing["form"],
                "date": filing["date"]
            })

    def analyze_all_countries(self):
        """Analyze SEC filings for all countries of interest"""

        logging.info(f"Starting SEC EDGAR analysis for {len(self.countries)} countries...")

        # Priority: Start with China and related jurisdictions
        priority_countries = ["CN", "HK", "TW", "KY", "VG"]  # Include Cayman, BVI

        for country_code in priority_countries:
            if country_code in self.countries:
                self.search_company_filings(country_code, limit=50)

        # Then analyze other countries
        for country_code in self.countries:
            if country_code not in priority_countries:
                self.search_company_filings(country_code, limit=20)

        # Generate risk assessment
        self.generate_risk_assessment()
        self.save_results()
        self.generate_report()

    def generate_risk_assessment(self):
        """Generate country risk assessment based on SEC filings"""

        country_risks = []

        for country_code, filings in self.results["by_country"].items():
            if filings:
                total_risk_score = sum(f.get("risks", {}).get("risk_score", 0) for f in filings)
                china_exposed = sum(1 for f in filings if f.get("risks", {}).get("china_exposure"))
                vie_structures = sum(1 for f in filings if f.get("risks", {}).get("vie_structure"))

                country_risks.append({
                    "country_code": country_code,
                    "country_name": self.countries.get(country_code, country_code),
                    "total_filings": len(filings),
                    "china_exposed_companies": china_exposed,
                    "vie_structures": vie_structures,
                    "total_risk_score": total_risk_score,
                    "avg_risk_score": total_risk_score / len(filings) if filings else 0
                })

        # Sort by total risk score
        country_risks.sort(key=lambda x: x["total_risk_score"], reverse=True)
        self.results["risk_assessment"] = country_risks

    def save_results(self):
        """Save analysis results"""

        # Save by country
        for country_code, filings in self.results["by_country"].items():
            if filings:
                country_dir = self.output_dir / "by_country" / country_code
                country_dir.mkdir(parents=True, exist_ok=True)

                with open(country_dir / "sec_filings.json", 'w') as f:
                    json.dump(filings, f, indent=2)

        # Save China-exposed companies
        with open(self.output_dir / "china_exposed_companies.json", 'w') as f:
            json.dump(self.results["china_exposed_companies"], f, indent=2)

        # Save VIE structures
        with open(self.output_dir / "vie_structures.json", 'w') as f:
            json.dump(self.results["vie_structures"], f, indent=2)

        # Save risk assessment
        with open(self.output_dir / "risk_assessment.json", 'w') as f:
            json.dump(self.results["risk_assessment"], f, indent=2)

    def generate_report(self):
        """Generate markdown report"""

        report = f"""# SEC EDGAR Multi-Country Analysis Report

## Executive Summary
- **Countries Analyzed:** {len(self.results['by_country'])}
- **Total Companies with China Exposure:** {len(self.results['china_exposed_companies'])}
- **VIE Structures Detected:** {len(self.results['vie_structures'])}
- **Processing Date:** {datetime.now().strftime('%Y-%m-%d')}
- **Data Source:** SEC EDGAR API (FREE)

## Top Risk Countries (by SEC Filing Analysis)
"""

        for i, country in enumerate(self.results["risk_assessment"][:10], 1):
            report += f"""
### {i}. {country['country_name']} ({country['country_code']})
- **Total SEC Filings:** {country['total_filings']}
- **China-Exposed Companies:** {country['china_exposed_companies']}
- **VIE Structures:** {country['vie_structures']}
- **Total Risk Score:** {country['total_risk_score']}
- **Average Risk Score:** {country['avg_risk_score']:.1f}
"""

        report += """
## China Exposure Analysis
"""
        for company in sorted(self.results["china_exposed_companies"],
                             key=lambda x: x["risk_score"], reverse=True)[:20]:
            report += f"- **{company['company']}** ({company['country']}): Risk Score {company['risk_score']}\n"

        report += """
## VIE Structure Companies
"""
        for vie in self.results["vie_structures"]:
            report += f"- **{vie['company']}** ({vie['country']}): {vie['filing']} on {vie['date']}\n"

        report += """
---
*Report generated using FREE SEC EDGAR API*
"""

        # Save report
        with open(self.output_dir / "SEC_EDGAR_ANALYSIS_REPORT.md", 'w') as f:
            f.write(report)

        logging.info(f"Report saved to {self.output_dir}/SEC_EDGAR_ANALYSIS_REPORT.md")

def main():
    """Main execution function"""
    logging.info("=" * 50)
    logging.info("Starting SEC EDGAR Multi-Country Analysis")
    logging.info("=" * 50)

    analyzer = SECEdgarMultiCountryAnalyzer()

    # Test with a few priority countries first
    test_countries = ["CN", "HK", "IL", "DE", "JP"]

    logging.info(f"Testing with {len(test_countries)} countries first...")

    for country in test_countries:
        analyzer.search_company_filings(country, limit=10)

    # Generate reports
    analyzer.generate_risk_assessment()
    analyzer.save_results()
    analyzer.generate_report()

    logging.info("=" * 50)
    logging.info("SEC EDGAR analysis complete!")
    logging.info(f"Results saved to: data/processed/sec_edgar_multicountry")
    logging.info("=" * 50)

if __name__ == "__main__":
    main()

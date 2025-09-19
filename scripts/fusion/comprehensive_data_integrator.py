"""
Comprehensive Data Integrator for All Available Sources
Integrates OpenAlex, CORDIS, USASpending, TED, SEC EDGAR, EPO, USPTO, and more
into the fusion pipeline for complete country analysis
"""

import os
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Set, Any
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ComprehensiveDataIntegrator:
    """Integrates all available data sources into the fusion pipeline"""

    def __init__(self):
        self.f_drive = Path("F:/OSINT_DATA")
        self.base_path = Path("C:/Projects/OSINT - Foresight")

        # Map all available data sources
        self.data_sources = {
            # Academic/Research
            "OPENALEX": self.f_drive / "OPENALEX",
            "CORDIS": self.f_drive / "CORDIS",

            # Patents
            "EPO_PATENTS": self.f_drive / "EPO_PATENTS",
            "USPTO": self.f_drive / "uspto_monitoring",
            "THE_LENS": self.f_drive / "THE_LENS",

            # Procurement/Contracts
            "USASPENDING": self.f_drive / "Italy/USASPENDING",
            "TED_PROCUREMENT": self.f_drive / "TED_PROCUREMENT",
            "SEC_EDGAR": self.f_drive / "SEC_EDGAR",

            # Conference/Events
            "CONFERENCES": self.f_drive / "conferences",

            # GitHub/Software
            "GITHUB": self.f_drive / "github_dependencies",

            # Country-specific
            "ITALY": self.f_drive / "Italy",
            "COUNTRY_ANALYSIS": self.f_drive / "country_analysis",
            "FUSION_RESULTS": self.f_drive / "fusion_results"
        }

        # Initialize integration database
        self.db_path = self.f_drive / "integrated_data.db"
        self.init_integration_database()

        # Country entity mappings for data correlation
        self.entity_mappings = self.load_entity_mappings()

    def init_integration_database(self):
        """Initialize database for integrated data tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Master entity resolution table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS entity_resolution (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                canonical_name TEXT,
                country TEXT,
                entity_type TEXT,
                aliases TEXT,
                lei TEXT,
                cage_code TEXT,
                duns TEXT,
                cik TEXT,
                vat_number TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Integrated data tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS integrated_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                country TEXT,
                data_source TEXT,
                data_type TEXT,
                file_path TEXT,
                records_count INTEGER,
                china_exposure_detected BOOLEAN,
                integration_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Cross-source correlations
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS data_correlations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_name TEXT,
                source1 TEXT,
                source2 TEXT,
                correlation_type TEXT,
                confidence_score REAL,
                china_link BOOLEAN,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

    def load_entity_mappings(self) -> Dict:
        """Load comprehensive entity mappings for all countries"""
        mappings = {}

        # Key technology companies by country
        mappings["Italy"] = {
            "defense": ["Leonardo S.p.A", "Leonardo DRS", "Fincantieri", "Telespazio"],
            "tech": ["STMicroelectronics", "Prysmian", "Saipem"],
            "research": ["CNR", "ENEA", "IIT", "Politecnico di Milano"]
        }

        mappings["Germany"] = {
            "defense": ["Rheinmetall", "ThyssenKrupp Marine Systems"],
            "tech": ["SAP", "Siemens", "Infineon", "ASML"],
            "research": ["Fraunhofer", "Max Planck", "Helmholtz"]
        }

        mappings["France"] = {
            "defense": ["Thales", "Dassault Aviation", "Safran", "Naval Group"],
            "tech": ["Atos", "Capgemini", "Schneider Electric"],
            "research": ["CNRS", "CEA", "INRIA"]
        }

        mappings["United Kingdom"] = {
            "defense": ["BAE Systems", "Rolls-Royce", "QinetiQ"],
            "tech": ["ARM Holdings", "DeepMind"],
            "research": ["DSTL", "Turing Institute"]
        }

        mappings["Netherlands"] = {
            "defense": ["Thales Nederland", "Damen Shipyards"],
            "tech": ["ASML", "NXP Semiconductors", "Philips"],
            "research": ["TNO", "ASTRON"]
        }

        # Add more countries as needed
        return mappings

    def integrate_openalex_data(self, country: str) -> Dict:
        """Integrate OpenAlex academic publication data"""
        logger.info(f"Integrating OpenAlex data for {country}")

        results = {
            "source": "OpenAlex",
            "country": country,
            "publications_found": 0,
            "china_collaborations": [],
            "key_research_areas": [],
            "top_institutions": []
        }

        # Check for OpenAlex data files
        openalex_path = self.data_sources["OPENALEX"]
        country_file = openalex_path / f"{country.lower()}_publications.json"

        if country_file.exists():
            with open(country_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

                # Analyze publications for China collaborations
                for pub in data.get("publications", []):
                    authors = pub.get("authorships", [])

                    china_collab = False
                    country_present = False

                    for author in authors:
                        institution = author.get("institutions", [{}])[0]
                        inst_country = institution.get("country", "")

                        if inst_country == "CN":
                            china_collab = True
                        if inst_country == country[:2].upper():
                            country_present = True

                    if china_collab and country_present:
                        results["china_collaborations"].append({
                            "title": pub.get("title"),
                            "year": pub.get("publication_year"),
                            "doi": pub.get("doi"),
                            "fields": pub.get("concepts", [])
                        })

                results["publications_found"] = len(data.get("publications", []))

        return results

    def integrate_cordis_data(self, country: str) -> Dict:
        """Integrate CORDIS EU funding data"""
        logger.info(f"Integrating CORDIS data for {country}")

        results = {
            "source": "CORDIS",
            "country": country,
            "projects_found": 0,
            "total_funding": 0,
            "china_linked_projects": [],
            "dual_use_tech": []
        }

        # Check for CORDIS data
        cordis_path = self.data_sources["CORDIS"]
        country_file = cordis_path / f"{country.lower()}_projects.json"

        if country_file.exists():
            with open(country_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

                for project in data.get("projects", []):
                    # Check for China involvement
                    participants = project.get("participants", [])

                    china_involved = any("China" in p.get("country", "") for p in participants)

                    if china_involved:
                        results["china_linked_projects"].append({
                            "project_id": project.get("id"),
                            "title": project.get("title"),
                            "funding": project.get("totalCost", 0),
                            "topics": project.get("topics", [])
                        })

                    # Check for dual-use technology
                    dual_use_keywords = ["aerospace", "quantum", "AI", "robotics", "materials"]
                    project_text = json.dumps(project).lower()

                    if any(keyword.lower() in project_text for keyword in dual_use_keywords):
                        results["dual_use_tech"].append(project.get("id"))

                results["projects_found"] = len(data.get("projects", []))
                results["total_funding"] = sum(p.get("totalCost", 0) for p in data.get("projects", []))

        return results

    def integrate_usaspending_data(self, country: str) -> Dict:
        """Integrate USAspending.gov contract data"""
        logger.info(f"Integrating USAspending data for {country}")

        results = {
            "source": "USAspending",
            "country": country,
            "contracts_found": 0,
            "total_value": 0,
            "defense_contracts": [],
            "technology_contracts": []
        }

        # Map country to potential contractors
        if country in self.entity_mappings:
            entities = self.entity_mappings[country].get("defense", []) + \
                      self.entity_mappings[country].get("tech", [])

            # Check USAspending data for these entities
            usa_path = self.data_sources["USASPENDING"]

            for entity in entities:
                entity_file = usa_path / f"{entity.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.json"

                if entity_file.exists():
                    with open(entity_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                        contracts = data.get("contracts", [])
                        for contract in contracts:
                            if "defense" in contract.get("category", "").lower():
                                results["defense_contracts"].append({
                                    "contractor": entity,
                                    "amount": contract.get("amount", 0),
                                    "description": contract.get("description", "")
                                })

                            results["total_value"] += contract.get("amount", 0)

                        results["contracts_found"] += len(contracts)

        return results

    def integrate_ted_procurement(self, country: str) -> Dict:
        """Integrate TED Europe procurement data"""
        logger.info(f"Integrating TED procurement data for {country}")

        results = {
            "source": "TED_Europe",
            "country": country,
            "tenders_found": 0,
            "china_bidders": [],
            "technology_tenders": []
        }

        ted_path = self.data_sources["TED_PROCUREMENT"]
        country_file = ted_path / f"{country.lower()}_tenders.json"

        if country_file.exists():
            with open(country_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

                for tender in data.get("tenders", []):
                    bidders = tender.get("bidders", [])

                    # Check for Chinese bidders
                    china_bidders = [b for b in bidders if "China" in b.get("country", "")]

                    if china_bidders:
                        results["china_bidders"].append({
                            "tender_id": tender.get("id"),
                            "description": tender.get("description"),
                            "china_companies": [b.get("name") for b in china_bidders]
                        })

                    # Check for technology tenders
                    if any(tech in tender.get("cpv_codes", "") for tech in ["30", "32", "48"]):
                        results["technology_tenders"].append(tender.get("id"))

                results["tenders_found"] = len(data.get("tenders", []))

        return results

    def integrate_patent_data(self, country: str) -> Dict:
        """Integrate patent data from EPO, USPTO, and The Lens"""
        logger.info(f"Integrating patent data for {country}")

        results = {
            "source": "Patents_Combined",
            "country": country,
            "total_patents": 0,
            "china_co_inventions": [],
            "technology_areas": {},
            "filing_trend": {}
        }

        # EPO Patents
        epo_path = self.data_sources["EPO_PATENTS"]
        epo_file = epo_path / f"{country.lower()}_patents.json"

        if epo_file.exists():
            with open(epo_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

                for patent in data.get("patents", []):
                    inventors = patent.get("inventors", [])

                    # Check for China co-invention
                    countries = [inv.get("country") for inv in inventors]

                    if "CN" in countries and country[:2].upper() in countries:
                        results["china_co_inventions"].append({
                            "patent_number": patent.get("publication_number"),
                            "title": patent.get("title"),
                            "filing_date": patent.get("filing_date"),
                            "ipc_codes": patent.get("ipc_codes", [])
                        })

                    results["total_patents"] += 1

                    # Track technology areas
                    for ipc in patent.get("ipc_codes", []):
                        tech_area = ipc[:3] if ipc else "Unknown"
                        results["technology_areas"][tech_area] = \
                            results["technology_areas"].get(tech_area, 0) + 1

        # USPTO Patents
        uspto_path = self.data_sources["USPTO"]
        uspto_file = uspto_path / f"{country.lower()}_uspto_{datetime.now().strftime('%Y%m%d')}.json"

        if uspto_file.exists():
            with open(uspto_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                results["total_patents"] += data.get("patents_found", 0)

        return results

    def integrate_sec_edgar_data(self, country: str) -> Dict:
        """Integrate SEC EDGAR filings for country entities"""
        logger.info(f"Integrating SEC EDGAR data for {country}")

        results = {
            "source": "SEC_EDGAR",
            "country": country,
            "filings_found": 0,
            "china_mentions": [],
            "risk_disclosures": []
        }

        # Check for country entities with US listings
        sec_path = self.data_sources["SEC_EDGAR"]

        if country in self.entity_mappings:
            for entity in self.entity_mappings[country].get("defense", []) + \
                        self.entity_mappings[country].get("tech", []):

                entity_file = sec_path / f"{entity.replace(' ', '_')}_filings.json"

                if entity_file.exists():
                    with open(entity_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                        for filing in data.get("filings", []):
                            filing_text = filing.get("text", "").lower()

                            # Check for China mentions
                            china_keywords = ["china", "chinese", "beijing", "shanghai"]

                            if any(keyword in filing_text for keyword in china_keywords):
                                results["china_mentions"].append({
                                    "entity": entity,
                                    "filing_type": filing.get("type"),
                                    "date": filing.get("filing_date")
                                })

                            # Check for risk disclosures
                            if "risk factor" in filing_text:
                                results["risk_disclosures"].append(entity)

                        results["filings_found"] += len(data.get("filings", []))

        return results

    def integrate_github_data(self, country: str) -> Dict:
        """Integrate GitHub dependency scanning results"""
        logger.info(f"Integrating GitHub data for {country}")

        results = {
            "source": "GitHub",
            "country": country,
            "organizations_scanned": 0,
            "china_dependencies": [],
            "vulnerability_score": 0
        }

        github_path = self.data_sources["GITHUB"]
        country_file = github_path / f"{country.replace(' ', '_')}_github_{datetime.now().strftime('%Y%m%d')}.json"

        if country_file.exists():
            with open(country_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

                results["organizations_scanned"] = data.get("orgs_scanned", 0)
                results["vulnerability_score"] = data.get("vulnerabilities_found", 0)

                # Extract China dependencies
                for org_data in data.get("organizations_scanned", []):
                    if org_data.get("china_dependencies"):
                        results["china_dependencies"].extend(org_data["china_dependencies"])

        return results

    def integrate_conference_data(self, country: str) -> Dict:
        """Integrate conference participation data"""
        logger.info(f"Integrating conference data for {country}")

        results = {
            "source": "Conferences",
            "country": country,
            "conferences_found": 0,
            "china_co_participation": [],
            "technology_events": []
        }

        conf_path = self.data_sources["CONFERENCES"]
        country_file = conf_path / f"{country.replace(' ', '_')}_conferences_{datetime.now().strftime('%Y%m%d')}.json"

        if country_file.exists():
            with open(country_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                results["conferences_found"] = data.get("conferences_found", 0)

                # Additional analysis could be done here

        return results

    def perform_comprehensive_integration(self, country: str) -> Dict:
        """Perform comprehensive data integration for a country"""
        logger.info(f"Starting comprehensive integration for {country}")

        integration_result = {
            "country": country,
            "integration_timestamp": datetime.now().isoformat(),
            "data_sources": {},
            "china_exposure_analysis": {},
            "risk_assessment": {},
            "recommendations": []
        }

        # Run all integrations in parallel
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = {
                executor.submit(self.integrate_openalex_data, country): "OpenAlex",
                executor.submit(self.integrate_cordis_data, country): "CORDIS",
                executor.submit(self.integrate_usaspending_data, country): "USAspending",
                executor.submit(self.integrate_ted_procurement, country): "TED",
                executor.submit(self.integrate_patent_data, country): "Patents",
                executor.submit(self.integrate_sec_edgar_data, country): "SEC_EDGAR",
                executor.submit(self.integrate_github_data, country): "GitHub",
                executor.submit(self.integrate_conference_data, country): "Conferences"
            }

            for future in as_completed(futures):
                source_name = futures[future]
                try:
                    result = future.result()
                    integration_result["data_sources"][source_name] = result
                except Exception as e:
                    logger.error(f"Error integrating {source_name} for {country}: {e}")
                    integration_result["data_sources"][source_name] = {"error": str(e)}

        # Perform cross-source analysis
        integration_result["china_exposure_analysis"] = self.analyze_china_exposure(integration_result)
        integration_result["risk_assessment"] = self.assess_comprehensive_risk(integration_result)
        integration_result["recommendations"] = self.generate_recommendations(integration_result)

        # Save integration results
        self.save_integration_results(integration_result)

        # Log to database
        self.log_integration(integration_result)

        return integration_result

    def analyze_china_exposure(self, integration_data: Dict) -> Dict:
        """Analyze China exposure across all data sources"""

        exposure = {
            "exposure_score": 0,
            "exposure_vectors": [],
            "critical_dependencies": [],
            "timeline": {}
        }

        # Academic collaboration exposure
        openalex = integration_data["data_sources"].get("OpenAlex", {})
        if openalex.get("china_collaborations"):
            exposure["exposure_vectors"].append({
                "vector": "Academic Collaboration",
                "count": len(openalex["china_collaborations"]),
                "severity": "MEDIUM"
            })
            exposure["exposure_score"] += 0.2

        # Funding exposure
        cordis = integration_data["data_sources"].get("CORDIS", {})
        if cordis.get("china_linked_projects"):
            exposure["exposure_vectors"].append({
                "vector": "EU Funding Projects",
                "count": len(cordis["china_linked_projects"]),
                "severity": "HIGH" if len(cordis["china_linked_projects"]) > 5 else "MEDIUM"
            })
            exposure["exposure_score"] += 0.3

        # Patent co-invention exposure
        patents = integration_data["data_sources"].get("Patents", {})
        if patents.get("china_co_inventions"):
            exposure["exposure_vectors"].append({
                "vector": "Patent Co-invention",
                "count": len(patents["china_co_inventions"]),
                "severity": "HIGH"
            })
            exposure["exposure_score"] += 0.4

        # Supply chain exposure
        github = integration_data["data_sources"].get("GitHub", {})
        if github.get("china_dependencies"):
            exposure["critical_dependencies"].extend(github["china_dependencies"])
            exposure["exposure_score"] += 0.3

        # Normalize score
        exposure["exposure_score"] = min(1.0, exposure["exposure_score"])

        # Risk level classification
        if exposure["exposure_score"] >= 0.7:
            exposure["risk_level"] = "CRITICAL"
        elif exposure["exposure_score"] >= 0.5:
            exposure["risk_level"] = "HIGH"
        elif exposure["exposure_score"] >= 0.3:
            exposure["risk_level"] = "MEDIUM"
        else:
            exposure["risk_level"] = "LOW"

        return exposure

    def assess_comprehensive_risk(self, integration_data: Dict) -> Dict:
        """Assess comprehensive risk based on all data sources"""

        risk = {
            "overall_risk_score": 0,
            "risk_categories": {},
            "mitigation_priority": []
        }

        china_exposure = integration_data["china_exposure_analysis"]

        # Technology transfer risk
        if china_exposure.get("exposure_vectors"):
            patent_vectors = [v for v in china_exposure["exposure_vectors"]
                            if "Patent" in v.get("vector", "")]
            if patent_vectors:
                risk["risk_categories"]["Technology Transfer"] = "HIGH"
                risk["mitigation_priority"].append("Review patent filing procedures")

        # Supply chain risk
        github = integration_data["data_sources"].get("GitHub", {})
        if github.get("vulnerability_score", 0) > 0:
            risk["risk_categories"]["Supply Chain"] = "MEDIUM"
            risk["mitigation_priority"].append("Audit software dependencies")

        # Economic dependency risk
        ted = integration_data["data_sources"].get("TED", {})
        if ted.get("china_bidders"):
            risk["risk_categories"]["Economic Dependency"] = "MEDIUM"
            risk["mitigation_priority"].append("Diversify procurement sources")

        # Calculate overall risk
        risk_values = {"HIGH": 1.0, "MEDIUM": 0.5, "LOW": 0.2}
        if risk["risk_categories"]:
            risk["overall_risk_score"] = sum(
                risk_values.get(level, 0) for level in risk["risk_categories"].values()
            ) / len(risk["risk_categories"])

        return risk

    def generate_recommendations(self, integration_data: Dict) -> List[str]:
        """Generate actionable recommendations based on integrated data"""

        recommendations = []
        china_exposure = integration_data["china_exposure_analysis"]
        risk = integration_data["risk_assessment"]

        # High exposure recommendations
        if china_exposure.get("exposure_score", 0) > 0.5:
            recommendations.append(
                f"PRIORITY: {integration_data['country']} shows high China exposure "
                f"({china_exposure['exposure_score']:.2f}). Immediate review required."
            )

        # Critical dependencies
        if china_exposure.get("critical_dependencies"):
            recommendations.append(
                f"Review {len(china_exposure['critical_dependencies'])} critical "
                "China-maintained software dependencies"
            )

        # Patent collaboration
        patents = integration_data["data_sources"].get("Patents", {})
        if len(patents.get("china_co_inventions", [])) > 5:
            recommendations.append(
                "High level of patent co-invention with Chinese entities detected. "
                "Review IP protection measures."
            )

        # Funding programs
        cordis = integration_data["data_sources"].get("CORDIS", {})
        if cordis.get("dual_use_tech"):
            recommendations.append(
                f"Monitor {len(cordis['dual_use_tech'])} dual-use technology projects "
                "for potential technology transfer risks"
            )

        return recommendations

    def save_integration_results(self, integration_result: Dict):
        """Save comprehensive integration results"""

        country = integration_result["country"].replace(" ", "_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        output_file = self.f_drive / "comprehensive_integration" / f"{country}_integrated_{timestamp}.json"
        output_file.parent.mkdir(exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(integration_result, f, indent=2, ensure_ascii=False)

        logger.info(f"Integration results saved: {output_file}")

    def log_integration(self, integration_result: Dict):
        """Log integration to database"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for source, data in integration_result["data_sources"].items():
            if "error" not in data:
                cursor.execute('''
                    INSERT INTO integrated_data
                    (country, data_source, data_type, records_count, china_exposure_detected)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    integration_result["country"],
                    source,
                    data.get("source", source),
                    data.get("publications_found", 0) + data.get("projects_found", 0) +
                    data.get("contracts_found", 0) + data.get("patents_found", 0),
                    bool(integration_result["china_exposure_analysis"].get("exposure_score", 0) > 0)
                ))

        conn.commit()
        conn.close()

    def run_all_countries_integration(self, countries: List[str]) -> Dict:
        """Run comprehensive integration for all countries"""

        session_results = {
            "session_id": f"integration_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "start_time": datetime.now().isoformat(),
            "countries_processed": [],
            "high_risk_countries": [],
            "total_china_exposures": 0
        }

        for country in countries:
            logger.info(f"Processing comprehensive integration for {country}")

            result = self.perform_comprehensive_integration(country)
            session_results["countries_processed"].append(country)

            if result["china_exposure_analysis"].get("risk_level") in ["HIGH", "CRITICAL"]:
                session_results["high_risk_countries"].append({
                    "country": country,
                    "risk_level": result["china_exposure_analysis"]["risk_level"],
                    "exposure_score": result["china_exposure_analysis"]["exposure_score"]
                })
                session_results["total_china_exposures"] += 1

        session_results["end_time"] = datetime.now().isoformat()

        # Save session summary
        summary_file = self.f_drive / "integration_sessions" / f"{session_results['session_id']}.json"
        summary_file.parent.mkdir(exist_ok=True)

        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(session_results, f, indent=2, ensure_ascii=False)

        return session_results


if __name__ == "__main__":
    integrator = ComprehensiveDataIntegrator()

    print("[COMPREHENSIVE DATA INTEGRATION]")
    print(f"Available data sources: {len(integrator.data_sources)}")
    for source, path in integrator.data_sources.items():
        exists = "EXISTS" if path.exists() else "NOT FOUND"
        print(f"  - {source}: {exists}")

    # Test with a specific country
    test_country = "Italy"
    print(f"\nPerforming comprehensive integration for {test_country}...")

    result = integrator.perform_comprehensive_integration(test_country)

    print(f"\n[INTEGRATION COMPLETE]")
    print(f"China Exposure Score: {result['china_exposure_analysis'].get('exposure_score', 0):.3f}")
    print(f"Risk Level: {result['china_exposure_analysis'].get('risk_level', 'UNKNOWN')}")
    print(f"Data Sources Integrated: {len(result['data_sources'])}")

    if result["recommendations"]:
        print(f"\n[RECOMMENDATIONS]")
        for rec in result["recommendations"]:
            print(f"  - {rec}")

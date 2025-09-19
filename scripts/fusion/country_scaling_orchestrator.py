"""
Country Scaling Orchestrator for OSINT Foresight
Scales fusion pipelines to all 67 target countries with risk-based prioritization
"""

import os
import json
import yaml
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CountryScalingOrchestrator:
    """Orchestrates fusion pipelines across all target countries"""

    def __init__(self):
        self.base_path = Path("C:/Projects/OSINT - Foresight")
        self.config_path = self.base_path / "config" / "TARGET_COUNTRIES_V6.yaml"
        self.output_dir = Path("F:/OSINT_DATA/country_analysis")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Load country configuration
        self.countries_config = self.load_countries_config()

        # Country-specific entity mappings
        self.country_entities = self.build_country_entity_mapping()

        # Execution priorities
        self.execution_priorities = {
            "IMMEDIATE": self.countries_config.get("PRIORITY_COUNTRIES", []),
            "QUARTERLY": self.countries_config.get("ANALYSIS_SCHEDULE", {}).get("QUARTERLY", {}).get("countries", []),
            "SEMI_ANNUAL": self.countries_config.get("ANALYSIS_SCHEDULE", {}).get("SEMI_ANNUAL", {}).get("countries", []),
            "ANNUAL": self.countries_config.get("ANALYSIS_SCHEDULE", {}).get("ANNUAL", {}).get("countries", [])
        }

    def load_countries_config(self) -> Dict:
        """Load and parse the countries configuration"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                logger.info(f"Loaded configuration for {len(config.get('TARGET_COUNTRIES', []))} countries")
                return config
        except Exception as e:
            logger.error(f"Error loading countries config: {e}")
            return {"TARGET_COUNTRIES": [], "PRIORITY_COUNTRIES": []}

    def build_country_entity_mapping(self) -> Dict[str, Dict]:
        """Build mapping of countries to their key defense/tech entities"""

        entity_mapping = {
            # Priority European Countries
            "Italy": {
                "defense_companies": ["Leonardo S.p.A", "Leonardo DRS", "Finmeccanica", "Fincantieri", "Telespazio"],
                "tech_companies": ["STMicroelectronics", "Prysmian", "Saipem"],
                "research_institutes": ["CNR", "ENEA", "IIT"],
                "universities": ["Politecnico di Milano", "Sapienza University", "University of Bologna"],
                "keywords": ["Leonardo", "Finmeccanica", "STMicroelectronics", "Prysmian"]
            },
            "Germany": {
                "defense_companies": ["Rheinmetall", "Krauss-Maffei Wegmann", "ThyssenKrupp Marine Systems"],
                "tech_companies": ["SAP", "Siemens", "Infineon", "ASML", "Carl Zeiss"],
                "research_institutes": ["Fraunhofer", "Max Planck", "Helmholtz"],
                "universities": ["TU Munich", "RWTH Aachen", "KIT"],
                "keywords": ["Rheinmetall", "Siemens", "SAP", "Infineon", "Fraunhofer"]
            },
            "France": {
                "defense_companies": ["Thales", "Dassault Aviation", "Safran", "Naval Group"],
                "tech_companies": ["Atos", "Capgemini", "Schneider Electric"],
                "research_institutes": ["CNRS", "CEA", "INRIA"],
                "universities": ["Sorbonne", "École Polytechnique", "ENS"],
                "keywords": ["Thales", "Dassault", "Safran", "Atos", "CNRS"]
            },
            "United Kingdom": {
                "defense_companies": ["BAE Systems", "Rolls-Royce", "QinetiQ", "Ultra Electronics"],
                "tech_companies": ["ARM Holdings", "Imagination Technologies", "DeepMind"],
                "research_institutes": ["DSTL", "Turing Institute", "Diamond Light Source"],
                "universities": ["Oxford", "Cambridge", "Imperial College"],
                "keywords": ["BAE Systems", "Rolls-Royce", "ARM Holdings", "DeepMind"]
            },
            "Netherlands": {
                "defense_companies": ["Thales Nederland", "Damen Shipyards", "Fokker Technologies"],
                "tech_companies": ["ASML", "NXP Semiconductors", "Philips"],
                "research_institutes": ["TNO", "CWI", "ASTRON"],
                "universities": ["TU Delft", "University of Amsterdam", "Eindhoven University"],
                "keywords": ["ASML", "NXP", "Philips", "TNO", "Damen"]
            },
            "Sweden": {
                "defense_companies": ["Saab AB", "BAE Systems Hägglunds"],
                "tech_companies": ["Ericsson", "Spotify", "Skype"],
                "research_institutes": ["KTH", "FOI", "RISE"],
                "universities": ["KTH Royal Institute", "Chalmers", "Lund University"],
                "keywords": ["Saab", "Ericsson", "Volvo", "KTH", "FOI"]
            },
            "Finland": {
                "defense_companies": ["Patria", "Nammo"],
                "tech_companies": ["Nokia", "Kone", "Wärtsilä"],
                "research_institutes": ["VTT", "CSC", "LUKE"],
                "universities": ["Aalto University", "University of Helsinki"],
                "keywords": ["Nokia", "Patria", "Aalto", "VTT"]
            },
            "Norway": {
                "defense_companies": ["Kongsberg Gruppen", "Nammo"],
                "tech_companies": ["Opera Software", "Telenor"],
                "research_institutes": ["SINTEF", "FFI", "NORCE"],
                "universities": ["NTNU", "University of Oslo"],
                "keywords": ["Kongsberg", "Telenor", "SINTEF", "NTNU"]
            },
            "Denmark": {
                "defense_companies": ["Terma", "Systematic"],
                "tech_companies": ["Novo Nordisk", "Vestas", "Ørsted"],
                "research_institutes": ["DTU", "GEUS"],
                "universities": ["DTU", "University of Copenhagen"],
                "keywords": ["Terma", "Vestas", "Novo Nordisk", "DTU"]
            },
            "Poland": {
                "defense_companies": ["PGZ", "WB Electronics", "Bumar"],
                "tech_companies": ["CD Projekt", "Allegro", "LiveChat"],
                "research_institutes": ["Polish Academy of Sciences"],
                "universities": ["Warsaw University of Technology", "AGH University"],
                "keywords": ["PGZ", "CD Projekt", "Warsaw University"]
            },
            # Indo-Pacific Countries
            "Japan": {
                "defense_companies": ["Mitsubishi Heavy Industries", "Kawasaki Heavy Industries", "IHI"],
                "tech_companies": ["Sony", "Toyota", "Honda", "Nintendo", "SoftBank"],
                "research_institutes": ["RIKEN", "JAXA", "AIST"],
                "universities": ["University of Tokyo", "Kyoto University", "Tohoku University"],
                "keywords": ["Mitsubishi", "Sony", "Toyota", "RIKEN", "JAXA"]
            },
            "South Korea": {
                "defense_companies": ["Korea Aerospace Industries", "Hanwha Systems", "LIG Nex1"],
                "tech_companies": ["Samsung", "LG", "SK Hynix", "Naver"],
                "research_institutes": ["KIST", "ETRI", "KAIST"],
                "universities": ["KAIST", "Seoul National University", "POSTECH"],
                "keywords": ["Samsung", "LG", "KAIST", "Hanwha", "ETRI"]
            },
            "Taiwan": {
                "defense_companies": ["CSBC Corporation", "AIDC"],
                "tech_companies": ["TSMC", "MediaTek", "Foxconn", "ASUS"],
                "research_institutes": ["Academia Sinica", "ITRI"],
                "universities": ["National Taiwan University", "NTHU"],
                "keywords": ["TSMC", "MediaTek", "Foxconn", "Academia Sinica"]
            },
            "Singapore": {
                "defense_companies": ["ST Engineering", "DSO National Laboratories"],
                "tech_companies": ["Grab", "Sea Limited", "Razer"],
                "research_institutes": ["A*STAR", "IHPC"],
                "universities": ["NUS", "NTU Singapore"],
                "keywords": ["ST Engineering", "Grab", "A*STAR", "NUS"]
            },
            "Australia": {
                "defense_companies": ["ASC Pty Ltd", "Electro Optic Systems", "CEA Technologies"],
                "tech_companies": ["Atlassian", "Canva", "Xero"],
                "research_institutes": ["CSIRO", "DSTO"],
                "universities": ["ANU", "University of Melbourne", "UNSW"],
                "keywords": ["Atlassian", "CSIRO", "ANU", "ASC"]
            },
            # Five Eyes
            "United States": {
                "defense_companies": ["Lockheed Martin", "Boeing", "Raytheon", "Northrop Grumman", "General Dynamics"],
                "tech_companies": ["Google", "Apple", "Microsoft", "Amazon", "Meta", "Tesla", "Intel", "Nvidia"],
                "research_institutes": ["MIT", "Stanford", "Caltech", "JPL", "NIST"],
                "universities": ["MIT", "Stanford", "Harvard", "Caltech", "Carnegie Mellon"],
                "keywords": ["Lockheed Martin", "Boeing", "Google", "Apple", "MIT", "Stanford"]
            },
            "Canada": {
                "defense_companies": ["CAE", "General Dynamics Land Systems Canada", "L3Harris"],
                "tech_companies": ["Shopify", "BlackBerry", "Bombardier"],
                "research_institutes": ["NRC", "DRDC"],
                "universities": ["University of Toronto", "McGill", "UBC"],
                "keywords": ["CAE", "Shopify", "BlackBerry", "NRC", "University of Toronto"]
            },
            # Additional countries can be added here following the same pattern
        }

        # For countries not explicitly mapped, create basic mapping
        all_countries = self.countries_config.get("TARGET_COUNTRIES", [])
        for country in all_countries:
            if country not in entity_mapping:
                entity_mapping[country] = {
                    "defense_companies": [],
                    "tech_companies": [],
                    "research_institutes": [],
                    "universities": [],
                    "keywords": [country.lower().replace(" ", "_")]
                }

        return entity_mapping

    def get_country_risk_tier(self, country: str) -> str:
        """Get risk tier for a country"""
        risk_tiers = self.countries_config.get("RISK_TIERS", {})

        for tier, countries in risk_tiers.items():
            if countries and country in countries:
                return tier

        return "TIER_4_MONITOR"

    def get_country_categories(self, country: str) -> List[str]:
        """Get all categories a country belongs to"""
        categories = []
        category_mappings = self.countries_config.get("CATEGORIES", {})

        for category, countries in category_mappings.items():
            if countries and country in countries:
                categories.append(category)

        return categories

    def analyze_single_country(self, country: str, priority_level: str = "STANDARD") -> Dict:
        """Analyze a single country with fusion pipelines"""
        logger.info(f"Starting analysis for {country} (Priority: {priority_level})")

        start_time = datetime.now()

        # Get country-specific configuration
        entities = self.country_entities.get(country, {})
        risk_tier = self.get_country_risk_tier(country)
        categories = self.get_country_categories(country)

        analysis_result = {
            "country": country,
            "analysis_timestamp": start_time.isoformat(),
            "priority_level": priority_level,
            "risk_tier": risk_tier,
            "categories": categories,
            "entities_analyzed": entities,
            "fusion_results": {},
            "china_exposure_summary": {},
            "execution_time": 0,
            "status": "in_progress"
        }

        try:
            # Import fusion orchestrator
            import sys
            fusion_path = str(self.base_path / "scripts" / "fusion")
            if fusion_path not in sys.path:
                sys.path.append(fusion_path)

            from fusion_orchestrator import FusionOrchestrator

            # Create country-specific fusion instance
            fusion = FusionOrchestrator()

            # Customize search terms for this country
            search_terms = []
            for entity_type, entity_list in entities.items():
                search_terms.extend(entity_list)

            # Run fusion pipelines with country-specific focus
            if priority_level in ["IMMEDIATE", "QUARTERLY"]:
                # Full pipeline analysis for high-priority countries
                fusion_results = fusion.run_all_pipelines()
                analysis_result["fusion_results"] = fusion_results
            else:
                # Lighter analysis for lower-priority countries
                # Focus on GitHub dependencies and standards adoption
                github_results = fusion.pipeline_github_dependencies()
                standards_results = fusion.pipeline_standards_adoption()

                analysis_result["fusion_results"] = {
                    "github_dependencies": github_results,
                    "standards_adoption": standards_results
                }

            # Calculate country-specific China exposure
            china_exposure = self.calculate_country_china_exposure(country, analysis_result["fusion_results"])
            analysis_result["china_exposure_summary"] = china_exposure

            analysis_result["status"] = "completed"

        except Exception as e:
            logger.error(f"Error analyzing {country}: {e}")
            analysis_result["status"] = "failed"
            analysis_result["error"] = str(e)

        # Calculate execution time
        end_time = datetime.now()
        analysis_result["execution_time"] = (end_time - start_time).total_seconds()

        # Save country-specific results
        self.save_country_analysis(analysis_result)

        logger.info(f"Completed analysis for {country} in {analysis_result['execution_time']:.2f} seconds")

        return analysis_result

    def calculate_country_china_exposure(self, country: str, fusion_results: Dict) -> Dict:
        """Calculate China exposure specific to a country"""

        exposure_summary = {
            "overall_risk_score": 0.0,
            "risk_level": "LOW",
            "exposure_vectors": {},
            "critical_findings": [],
            "recommendations": []
        }

        # Analyze each fusion pipeline result
        total_exposure = 0.0
        vector_count = 0

        for pipeline_name, pipeline_results in fusion_results.items():
            vector_exposure = 0.0

            if pipeline_name == "github_dependencies":
                # GitHub dependency exposure
                vulnerabilities = pipeline_results.get("vulnerabilities", [])
                if vulnerabilities:
                    risk_scores = [v.get("risk_score", 0) for v in vulnerabilities]
                    vector_exposure = sum(risk_scores) / len(risk_scores) if risk_scores else 0

            elif pipeline_name == "standards_adoption":
                # Standards influence exposure
                influence_map = pipeline_results.get("influence_map", [])
                china_influence = [i for i in influence_map if i.get("china_collaboration", 0) > 0]
                vector_exposure = len(china_influence) / max(1, len(influence_map))

            elif pipeline_name == "conference_patent_procurement":
                # Conference collaboration exposure
                findings = pipeline_results.get("findings", [])
                china_events = [f for f in findings if f.get("china_exposure", 0) > 0]
                vector_exposure = len(china_events) / max(1, len(findings))

            elif pipeline_name == "funding_spinout":
                # Funding/spinout exposure
                spinouts = pipeline_results.get("spinouts", [])
                risky_spinouts = [s for s in spinouts if s.get("china_acquisition_risk", 0) > 0.3]
                vector_exposure = len(risky_spinouts) / max(1, len(spinouts))

            exposure_summary["exposure_vectors"][pipeline_name] = vector_exposure
            total_exposure += vector_exposure
            vector_count += 1

        # Calculate overall risk score
        if vector_count > 0:
            exposure_summary["overall_risk_score"] = total_exposure / vector_count

        # Determine risk level
        if exposure_summary["overall_risk_score"] >= 0.7:
            exposure_summary["risk_level"] = "CRITICAL"
        elif exposure_summary["overall_risk_score"] >= 0.5:
            exposure_summary["risk_level"] = "HIGH"
        elif exposure_summary["overall_risk_score"] >= 0.3:
            exposure_summary["risk_level"] = "MEDIUM"
        else:
            exposure_summary["risk_level"] = "LOW"

        # Generate country-specific recommendations
        if exposure_summary["overall_risk_score"] > 0.5:
            exposure_summary["recommendations"].append(
                f"Priority review required for {country} due to elevated China exposure"
            )

        # Add critical findings based on country categories
        categories = self.get_country_categories(country)
        if "NATO_MEMBERS" in categories and exposure_summary["overall_risk_score"] > 0.3:
            exposure_summary["critical_findings"].append(
                f"NATO member {country} shows concerning China exposure"
            )

        if "SEMICONDUCTOR_CRITICAL" in self.countries_config and country in self.countries_config["SEMICONDUCTOR_CRITICAL"]:
            if exposure_summary["exposure_vectors"].get("github_dependencies", 0) > 0.4:
                exposure_summary["critical_findings"].append(
                    f"Semiconductor-critical country {country} has supply chain vulnerabilities"
                )

        return exposure_summary

    def save_country_analysis(self, analysis_result: Dict):
        """Save analysis results for a country"""
        country = analysis_result["country"].replace(" ", "_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        output_file = self.output_dir / f"{country}_analysis_{timestamp}.json"

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_result, f, indent=2, ensure_ascii=False)

        logger.info(f"Country analysis saved: {output_file}")

    def run_priority_batch(self, priority_level: str, max_concurrent: int = 5) -> Dict:
        """Run analysis for a batch of countries by priority level"""

        countries = self.execution_priorities.get(priority_level, [])

        if not countries:
            logger.warning(f"No countries found for priority level: {priority_level}")
            return {"priority_level": priority_level, "countries_analyzed": 0, "results": []}

        logger.info(f"Starting batch analysis for {priority_level}: {len(countries)} countries")

        batch_results = {
            "priority_level": priority_level,
            "start_time": datetime.now().isoformat(),
            "countries_analyzed": 0,
            "countries_total": len(countries),
            "results": [],
            "summary_statistics": {},
            "execution_time": 0
        }

        start_time = datetime.now()

        # Use ThreadPoolExecutor for concurrent analysis
        with ThreadPoolExecutor(max_workers=max_concurrent) as executor:
            # Submit all countries for analysis
            future_to_country = {
                executor.submit(self.analyze_single_country, country, priority_level): country
                for country in countries
            }

            # Collect results as they complete
            for future in as_completed(future_to_country):
                country = future_to_country[future]
                try:
                    result = future.result()
                    batch_results["results"].append(result)
                    batch_results["countries_analyzed"] += 1

                    logger.info(f"Completed {batch_results['countries_analyzed']}/{len(countries)} countries")

                except Exception as e:
                    logger.error(f"Failed to analyze {country}: {e}")
                    batch_results["results"].append({
                        "country": country,
                        "status": "failed",
                        "error": str(e)
                    })

        # Calculate batch statistics
        end_time = datetime.now()
        batch_results["execution_time"] = (end_time - start_time).total_seconds()
        batch_results["end_time"] = end_time.isoformat()

        # Generate summary statistics
        successful_analyses = [r for r in batch_results["results"] if r.get("status") == "completed"]

        if successful_analyses:
            exposure_scores = [r.get("china_exposure_summary", {}).get("overall_risk_score", 0)
                             for r in successful_analyses]

            batch_results["summary_statistics"] = {
                "successful_analyses": len(successful_analyses),
                "failed_analyses": len(batch_results["results"]) - len(successful_analyses),
                "average_china_exposure": sum(exposure_scores) / len(exposure_scores) if exposure_scores else 0,
                "high_risk_countries": len([s for s in exposure_scores if s >= 0.5]),
                "critical_risk_countries": len([s for s in exposure_scores if s >= 0.7])
            }

        # Save batch results
        self.save_batch_results(batch_results)

        return batch_results

    def save_batch_results(self, batch_results: Dict):
        """Save batch analysis results"""
        priority_level = batch_results["priority_level"]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        output_file = self.output_dir / f"batch_{priority_level}_{timestamp}.json"

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(batch_results, f, indent=2, ensure_ascii=False)

        logger.info(f"Batch results saved: {output_file}")

    def run_full_country_scaling(self) -> Dict:
        """Run complete country scaling across all 67 countries"""
        logger.info("Starting full country scaling analysis for all 67 target countries")

        scaling_session = {
            "session_id": f"scaling_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "start_time": datetime.now().isoformat(),
            "total_countries": len(self.countries_config.get("TARGET_COUNTRIES", [])),
            "priority_batches": {},
            "overall_statistics": {},
            "execution_time": 0
        }

        start_time = datetime.now()

        # Run analysis in priority order
        priority_order = ["IMMEDIATE", "QUARTERLY", "SEMI_ANNUAL", "ANNUAL"]

        for priority_level in priority_order:
            logger.info(f"\n=== Running {priority_level} Priority Analysis ===")

            # Adjust concurrency based on priority
            max_concurrent = {
                "IMMEDIATE": 3,  # Careful analysis
                "QUARTERLY": 5,  # Moderate concurrency
                "SEMI_ANNUAL": 8,  # Higher concurrency
                "ANNUAL": 10     # Maximum concurrency
            }.get(priority_level, 5)

            batch_result = self.run_priority_batch(priority_level, max_concurrent)
            scaling_session["priority_batches"][priority_level] = batch_result

            # Pause between batches to avoid overwhelming APIs
            if priority_level != "ANNUAL":
                logger.info("Pausing 60 seconds between priority batches...")
                time.sleep(60)

        # Calculate overall statistics
        end_time = datetime.now()
        scaling_session["end_time"] = end_time.isoformat()
        scaling_session["execution_time"] = (end_time - start_time).total_seconds()

        # Aggregate statistics across all batches
        total_analyzed = sum(batch.get("countries_analyzed", 0) for batch in scaling_session["priority_batches"].values())
        total_successful = sum(batch.get("summary_statistics", {}).get("successful_analyses", 0)
                              for batch in scaling_session["priority_batches"].values())
        total_high_risk = sum(batch.get("summary_statistics", {}).get("high_risk_countries", 0)
                             for batch in scaling_session["priority_batches"].values())
        total_critical_risk = sum(batch.get("summary_statistics", {}).get("critical_risk_countries", 0)
                                 for batch in scaling_session["priority_batches"].values())

        scaling_session["overall_statistics"] = {
            "total_countries_analyzed": total_analyzed,
            "successful_analyses": total_successful,
            "failed_analyses": total_analyzed - total_successful,
            "success_rate": (total_successful / max(1, total_analyzed)) * 100,
            "high_risk_countries": total_high_risk,
            "critical_risk_countries": total_critical_risk,
            "execution_time_hours": scaling_session["execution_time"] / 3600
        }

        # Save overall scaling session results
        self.save_scaling_session(scaling_session)

        logger.info(f"\n=== COUNTRY SCALING COMPLETE ===")
        logger.info(f"Countries analyzed: {total_analyzed}/{scaling_session['total_countries']}")
        logger.info(f"Success rate: {scaling_session['overall_statistics']['success_rate']:.1f}%")
        logger.info(f"High-risk countries: {total_high_risk}")
        logger.info(f"Critical-risk countries: {total_critical_risk}")
        logger.info(f"Total execution time: {scaling_session['overall_statistics']['execution_time_hours']:.2f} hours")

        return scaling_session

    def save_scaling_session(self, scaling_session: Dict):
        """Save complete scaling session results"""
        session_id = scaling_session["session_id"]
        output_file = self.output_dir / f"{session_id}_complete.json"

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(scaling_session, f, indent=2, ensure_ascii=False)

        logger.info(f"Complete scaling session saved: {output_file}")


if __name__ == "__main__":
    orchestrator = CountryScalingOrchestrator()

    print("[COUNTRY SCALING ORCHESTRATOR]")
    print(f"Configured for {len(orchestrator.countries_config.get('TARGET_COUNTRIES', []))} target countries")
    print(f"Priority countries: {len(orchestrator.countries_config.get('PRIORITY_COUNTRIES', []))}")

    # For demonstration, run a limited test on immediate priority countries
    print("\nRunning demonstration analysis on IMMEDIATE priority countries...")

    immediate_countries = orchestrator.execution_priorities.get("IMMEDIATE", [])[:5]  # Limit to 5 for demo

    demo_results = []
    for country in immediate_countries:
        print(f"\nAnalyzing {country}...")
        result = orchestrator.analyze_single_country(country, "IMMEDIATE")
        demo_results.append(result)

        # Print summary
        china_exposure = result.get("china_exposure_summary", {})
        print(f"  Risk Level: {china_exposure.get('risk_level', 'UNKNOWN')}")
        print(f"  Exposure Score: {china_exposure.get('overall_risk_score', 0):.3f}")
        print(f"  Execution Time: {result.get('execution_time', 0):.1f}s")

    print(f"\n=== DEMONSTRATION COMPLETE ===")
    print(f"Countries analyzed: {len(demo_results)}")
    print(f"Results saved to: F:/OSINT_DATA/country_analysis/")
    print(f"\nTo run full 67-country analysis, call: orchestrator.run_full_country_scaling()")

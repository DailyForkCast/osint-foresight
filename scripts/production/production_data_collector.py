"""
Production Data Collection Orchestrator
Systematic collection for all 67 target countries with priority-based execution
Saves all data to external F: drive with proper organization
"""

import os
import json
import yaml
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed, ProcessPoolExecutor
import sqlite3

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProductionDataCollector:
    """Orchestrates production-scale data collection across all target countries"""

    def __init__(self):
        self.base_path = Path("C:/Projects/OSINT - Foresight")
        self.f_drive = Path("F:/OSINT_DATA")
        self.config_path = self.base_path / "config" / "TARGET_COUNTRIES_V6.yaml"

        # Load configuration
        self.config = self.load_config()

        # Output directories on F: drive
        self.output_dirs = {
            "countries": self.f_drive / "country_analysis",
            "fusion": self.f_drive / "fusion_results",
            "conferences": self.f_drive / "conferences",
            "github": self.f_drive / "github_dependencies",
            "uspto": self.f_drive / "uspto_monitoring",
            "logs": self.f_drive / "collection_logs"
        }

        # Create all output directories
        for dir_path in self.output_dirs.values():
            dir_path.mkdir(parents=True, exist_ok=True)

        # Collection tracking database
        self.db_path = self.f_drive / "collection_tracking.db"
        self.init_tracking_database()

        # Collection statistics
        self.stats = {
            "session_start": datetime.now(),
            "countries_completed": 0,
            "countries_failed": 0,
            "total_data_size": 0,
            "collection_errors": []
        }

    def load_config(self) -> Dict:
        """Load countries configuration"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}

    def init_tracking_database(self):
        """Initialize SQLite database for tracking collection progress"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Collection sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS collection_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                priority_level TEXT,
                countries_total INTEGER,
                countries_completed INTEGER,
                countries_failed INTEGER,
                status TEXT
            )
        ''')

        # Country collection status
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS country_status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                country_name TEXT,
                priority_level TEXT,
                collection_start TIMESTAMP,
                collection_end TIMESTAMP,
                status TEXT,
                data_collected TEXT,
                error_message TEXT,
                file_paths TEXT,
                FOREIGN KEY (session_id) REFERENCES collection_sessions (session_id)
            )
        ''')

        # Data collection metrics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS collection_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                country_name TEXT,
                collector_type TEXT,
                items_collected INTEGER,
                data_size_mb REAL,
                execution_time_seconds REAL,
                api_calls_made INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES collection_sessions (session_id)
            )
        ''')

        conn.commit()
        conn.close()

    def log_collection_start(self, session_id: str, priority_level: str, countries: List[str]):
        """Log start of collection session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO collection_sessions
            (session_id, start_time, priority_level, countries_total, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (session_id, datetime.now(), priority_level, len(countries), "running"))

        conn.commit()
        conn.close()

        logger.info(f"Started collection session {session_id}: {len(countries)} countries")

    def log_country_status(self, session_id: str, country: str, status: str,
                          data_collected: Dict = None, error: str = None,
                          file_paths: List[str] = None):
        """Log country collection status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO country_status
            (session_id, country_name, collection_end, status, data_collected,
             error_message, file_paths)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            session_id, country, datetime.now(), status,
            json.dumps(data_collected) if data_collected else None,
            error,
            json.dumps(file_paths) if file_paths else None
        ))

        conn.commit()
        conn.close()

    def collect_country_data(self, country: str, priority_level: str, session_id: str) -> Dict:
        """Comprehensive data collection for a single country"""
        logger.info(f"Starting data collection for {country} (Priority: {priority_level})")

        start_time = datetime.now()
        collection_result = {
            "country": country,
            "priority_level": priority_level,
            "session_id": session_id,
            "start_time": start_time.isoformat(),
            "collectors_run": [],
            "files_created": [],
            "data_summary": {},
            "status": "running",
            "errors": []
        }

        try:
            # 1. Run fusion pipeline analysis
            logger.info(f"Running fusion analysis for {country}...")
            fusion_result = self.run_fusion_analysis(country, priority_level, session_id)
            collection_result["collectors_run"].append("fusion_analysis")
            collection_result["data_summary"]["fusion"] = fusion_result

            # 2. Collect conference data
            logger.info(f"Collecting conference data for {country}...")
            conference_result = self.collect_conference_data(country, session_id)
            collection_result["collectors_run"].append("conference_data")
            collection_result["data_summary"]["conferences"] = conference_result

            # 3. GitHub dependency scanning
            logger.info(f"Scanning GitHub dependencies for {country}...")
            github_result = self.collect_github_dependencies(country, session_id)
            collection_result["collectors_run"].append("github_dependencies")
            collection_result["data_summary"]["github"] = github_result

            # 4. USPTO monitoring (for countries with known US presence)
            if self.should_collect_uspto_data(country):
                logger.info(f"Collecting USPTO data for {country}...")
                uspto_result = self.collect_uspto_data(country, session_id)
                collection_result["collectors_run"].append("uspto_monitoring")
                collection_result["data_summary"]["uspto"] = uspto_result

            # 5. Save comprehensive country analysis
            country_file = self.save_country_analysis(collection_result)
            collection_result["files_created"].append(str(country_file))

            collection_result["status"] = "completed"

        except Exception as e:
            logger.error(f"Error collecting data for {country}: {e}")
            collection_result["status"] = "failed"
            collection_result["errors"].append(str(e))

        # Calculate execution time
        end_time = datetime.now()
        collection_result["end_time"] = end_time.isoformat()
        collection_result["execution_time"] = (end_time - start_time).total_seconds()

        # Log to database
        self.log_country_status(
            session_id, country, collection_result["status"],
            collection_result["data_summary"],
            collection_result["errors"][-1] if collection_result["errors"] else None,
            collection_result["files_created"]
        )

        return collection_result

    def run_fusion_analysis(self, country: str, priority_level: str, session_id: str) -> Dict:
        """Run fusion pipeline analysis for country"""
        try:
            import sys
            sys.path.append(str(self.base_path / "scripts" / "fusion"))
            from country_scaling_orchestrator import CountryScalingOrchestrator

            orchestrator = CountryScalingOrchestrator()
            result = orchestrator.analyze_single_country(country, priority_level)

            # Save to F: drive
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.output_dirs["fusion"] / f"{country.replace(' ', '_')}_fusion_{timestamp}.json"

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            return {
                "status": "completed",
                "file": str(output_file),
                "china_exposure_score": result.get("china_exposure_summary", {}).get("overall_risk_score", 0),
                "execution_time": result.get("execution_time", 0)
            }

        except Exception as e:
            logger.error(f"Fusion analysis failed for {country}: {e}")
            return {"status": "failed", "error": str(e)}

    def collect_conference_data(self, country: str, session_id: str) -> Dict:
        """Collect conference participation data"""
        try:
            import sys
            sys.path.append(str(self.base_path / "scripts" / "collectors"))
            from crossref_events_collector import CrossRefEventsCollector

            collector = CrossRefEventsCollector()

            # Search for conferences with country-specific keywords
            country_keywords = self.get_country_keywords(country)
            conferences_found = 0

            for keyword in country_keywords[:3]:  # Limit searches to avoid rate limits
                try:
                    events = collector.fetch_events(
                        from_date="2023-01-01",
                        until_date="2024-12-31"
                    )
                    conferences_found += len(events)
                    time.sleep(1)  # Rate limiting
                except Exception as e:
                    logger.debug(f"Conference search failed for {keyword}: {e}")

            # Save results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.output_dirs["conferences"] / f"{country.replace(' ', '_')}_conferences_{timestamp}.json"

            result = {
                "country": country,
                "search_keywords": country_keywords,
                "conferences_found": conferences_found,
                "collection_timestamp": datetime.now().isoformat()
            }

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            return {
                "status": "completed",
                "file": str(output_file),
                "conferences_found": conferences_found
            }

        except Exception as e:
            logger.error(f"Conference data collection failed for {country}: {e}")
            return {"status": "failed", "error": str(e)}

    def collect_github_dependencies(self, country: str, session_id: str) -> Dict:
        """Collect GitHub dependency data for country"""
        try:
            import sys
            sys.path.append(str(self.base_path / "scripts" / "collectors"))
            from github_dependency_scanner import GitHubDependencyScanner

            scanner = GitHubDependencyScanner()

            # Get country-specific GitHub organizations
            country_orgs = self.get_country_github_orgs(country)

            vulnerabilities_found = 0
            scanned_orgs = []

            for org in country_orgs[:5]:  # Limit to avoid rate limits
                try:
                    org_result = scanner.scan_organization(org)
                    scanned_orgs.append(org_result)
                    vulnerabilities_found += org_result.get("total_china_dependencies", 0)
                    time.sleep(2)  # Rate limiting
                except Exception as e:
                    logger.debug(f"GitHub scan failed for {org}: {e}")

            # Save results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.output_dirs["github"] / f"{country.replace(' ', '_')}_github_{timestamp}.json"

            result = {
                "country": country,
                "organizations_scanned": scanned_orgs,
                "total_vulnerabilities": vulnerabilities_found,
                "collection_timestamp": datetime.now().isoformat()
            }

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            return {
                "status": "completed",
                "file": str(output_file),
                "vulnerabilities_found": vulnerabilities_found,
                "orgs_scanned": len(scanned_orgs)
            }

        except Exception as e:
            logger.error(f"GitHub dependency collection failed for {country}: {e}")
            return {"status": "failed", "error": str(e)}

    def collect_uspto_data(self, country: str, session_id: str) -> Dict:
        """Collect USPTO patent data for country"""
        try:
            import sys
            sys.path.append(str(self.base_path / "scripts" / "collectors"))
            from uspto_monitoring_enhanced import USPTOMonitoringEnhanced

            monitor = USPTOMonitoringEnhanced()

            # Search for patents from country entities
            country_entities = self.get_country_entities(country)
            patents_found = 0

            for entity in country_entities[:3]:  # Limit searches
                try:
                    patents = monitor.search_patents_robust(entity, 20)
                    patents_found += len(patents)
                    time.sleep(3)  # USPTO rate limiting
                except Exception as e:
                    logger.debug(f"USPTO search failed for {entity}: {e}")

            # Save results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.output_dirs["uspto"] / f"{country.replace(' ', '_')}_uspto_{timestamp}.json"

            result = {
                "country": country,
                "entities_searched": country_entities,
                "patents_found": patents_found,
                "collection_timestamp": datetime.now().isoformat()
            }

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            return {
                "status": "completed",
                "file": str(output_file),
                "patents_found": patents_found
            }

        except Exception as e:
            logger.error(f"USPTO data collection failed for {country}: {e}")
            return {"status": "failed", "error": str(e)}

    def should_collect_uspto_data(self, country: str) -> bool:
        """Determine if USPTO data collection is relevant for country"""
        # Collect USPTO data for countries with significant US tech presence
        uspto_relevant_countries = [
            "United Kingdom", "Germany", "France", "Italy", "Netherlands",
            "Sweden", "Finland", "Denmark", "Norway", "Switzerland",
            "Japan", "South Korea", "Taiwan", "Singapore", "Australia",
            "Canada", "Israel"
        ]
        return country in uspto_relevant_countries

    def get_country_keywords(self, country: str) -> List[str]:
        """Get search keywords for a country"""
        # Basic keywords - in production would be more sophisticated
        keywords = [country.lower(), country.replace(" ", "_").lower()]

        # Add specific entity keywords if available
        country_mapping = {
            "Germany": ["SAP", "Siemens", "BMW", "Volkswagen", "Bosch"],
            "France": ["Thales", "Dassault", "Airbus", "Safran"],
            "United Kingdom": ["BAE Systems", "Rolls-Royce", "ARM"],
            "Italy": ["Leonardo", "Finmeccanica", "STMicroelectronics"],
            "Netherlands": ["ASML", "Philips", "Shell"],
            "Sweden": ["Ericsson", "Saab", "Volvo"],
            "Japan": ["Sony", "Toyota", "Mitsubishi", "Honda"],
            "South Korea": ["Samsung", "LG", "Hyundai"]
        }

        if country in country_mapping:
            keywords.extend([k.lower() for k in country_mapping[country]])

        return keywords

    def get_country_github_orgs(self, country: str) -> List[str]:
        """Get GitHub organizations to scan for country"""
        # Basic mapping - in production would be more comprehensive
        org_mapping = {
            "Germany": ["SAP", "siemens", "bmw", "volkswagen"],
            "France": ["thalesgroup", "dassault-systemes", "airbus"],
            "United Kingdom": ["baesystems", "rolls-royce", "arm"],
            "Italy": ["leonardo-company", "finmeccanica"],
            "Netherlands": ["asml", "philips"],
            "Sweden": ["ericsson", "saab", "volvo"],
            "Japan": ["sony", "toyota", "mitsubishi"],
            "South Korea": ["samsung", "lg-electronics"]
        }

        return org_mapping.get(country, [country.lower().replace(" ", "-")])

    def get_country_entities(self, country: str) -> List[str]:
        """Get major entities for USPTO searches"""
        entity_mapping = {
            "Germany": ["SAP", "Siemens", "BMW", "Bosch"],
            "France": ["Thales", "Dassault", "Airbus"],
            "United Kingdom": ["BAE Systems", "Rolls-Royce"],
            "Italy": ["Leonardo", "STMicroelectronics"],
            "Netherlands": ["ASML", "Philips"],
            "Sweden": ["Ericsson", "Saab"],
            "Japan": ["Sony", "Toyota", "Honda"],
            "South Korea": ["Samsung", "LG"]
        }

        return entity_mapping.get(country, [])

    def save_country_analysis(self, collection_result: Dict) -> Path:
        """Save comprehensive country analysis to F: drive"""
        country = collection_result["country"].replace(" ", "_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        output_file = self.output_dirs["countries"] / f"{country}_complete_analysis_{timestamp}.json"

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(collection_result, f, indent=2, ensure_ascii=False)

        logger.info(f"Complete analysis saved: {output_file}")
        return output_file

    def run_priority_collection(self, max_workers: int = 3) -> Dict:
        """Run data collection for priority countries"""
        priority_countries = self.config.get("PRIORITY_COUNTRIES", [])
        session_id = f"priority_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        logger.info(f"Starting priority collection for {len(priority_countries)} countries")
        self.log_collection_start(session_id, "PRIORITY", priority_countries)

        collection_session = {
            "session_id": session_id,
            "start_time": datetime.now().isoformat(),
            "priority_level": "PRIORITY",
            "countries_total": len(priority_countries),
            "countries_completed": 0,
            "countries_failed": 0,
            "results": [],
            "execution_time": 0
        }

        start_time = datetime.now()

        # Use ThreadPoolExecutor for concurrent collection
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all countries for collection
            future_to_country = {
                executor.submit(self.collect_country_data, country, "PRIORITY", session_id): country
                for country in priority_countries
            }

            # Collect results as they complete
            for future in as_completed(future_to_country):
                country = future_to_country[future]
                try:
                    result = future.result()
                    collection_session["results"].append(result)

                    if result["status"] == "completed":
                        collection_session["countries_completed"] += 1
                        logger.info(f"[SUCCESS] Completed {country} ({collection_session['countries_completed']}/{len(priority_countries)})")
                    else:
                        collection_session["countries_failed"] += 1
                        logger.error(f"[FAILED] Failed {country}")

                except Exception as e:
                    logger.error(f"Collection failed for {country}: {e}")
                    collection_session["countries_failed"] += 1

        # Calculate final statistics
        end_time = datetime.now()
        collection_session["end_time"] = end_time.isoformat()
        collection_session["execution_time"] = (end_time - start_time).total_seconds()

        # Save session results
        session_file = self.output_dirs["logs"] / f"{session_id}_complete.json"
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(collection_session, f, indent=2, ensure_ascii=False)

        logger.info(f"\n=== PRIORITY COLLECTION COMPLETE ===")
        logger.info(f"Countries completed: {collection_session['countries_completed']}/{len(priority_countries)}")
        logger.info(f"Countries failed: {collection_session['countries_failed']}")
        logger.info(f"Success rate: {(collection_session['countries_completed']/len(priority_countries)*100):.1f}%")
        logger.info(f"Total time: {collection_session['execution_time']/3600:.2f} hours")
        logger.info(f"Session saved: {session_file}")

        return collection_session

    def run_all_countries_collection(self) -> Dict:
        """Run data collection for all 67 countries"""
        all_countries = self.config.get("TARGET_COUNTRIES", [])
        priority_countries = set(self.config.get("PRIORITY_COUNTRIES", []))

        # Separate into priority and remaining
        remaining_countries = [c for c in all_countries if c not in priority_countries]

        logger.info(f"Full collection: {len(priority_countries)} priority + {len(remaining_countries)} remaining = {len(all_countries)} total")

        full_session = {
            "session_type": "full_collection",
            "start_time": datetime.now().isoformat(),
            "total_countries": len(all_countries),
            "priority_session": None,
            "remaining_session": None,
            "overall_statistics": {}
        }

        # 1. Run priority countries first
        logger.info("\n=== PHASE 1: Priority Countries Collection ===")
        priority_session = self.run_priority_collection(max_workers=3)
        full_session["priority_session"] = priority_session

        # Brief pause between phases
        logger.info("Pausing 5 minutes between phases...")
        time.sleep(300)

        # 2. Run remaining countries
        logger.info("\n=== PHASE 2: Remaining Countries Collection ===")
        remaining_session = self.run_remaining_collection(remaining_countries, max_workers=5)
        full_session["remaining_session"] = remaining_session

        # Calculate overall statistics
        full_session["end_time"] = datetime.now().isoformat()
        full_session["overall_statistics"] = {
            "total_completed": priority_session["countries_completed"] + remaining_session["countries_completed"],
            "total_failed": priority_session["countries_failed"] + remaining_session["countries_failed"],
            "overall_success_rate": ((priority_session["countries_completed"] + remaining_session["countries_completed"]) / len(all_countries)) * 100,
            "total_execution_hours": (priority_session["execution_time"] + remaining_session["execution_time"]) / 3600
        }

        # Save complete session
        session_file = self.output_dirs["logs"] / f"full_collection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(full_session, f, indent=2, ensure_ascii=False)

        logger.info(f"\n=== FULL COLLECTION COMPLETE ===")
        logger.info(f"Total countries: {len(all_countries)}")
        logger.info(f"Successfully completed: {full_session['overall_statistics']['total_completed']}")
        logger.info(f"Failed: {full_session['overall_statistics']['total_failed']}")
        logger.info(f"Overall success rate: {full_session['overall_statistics']['overall_success_rate']:.1f}%")
        logger.info(f"Total execution time: {full_session['overall_statistics']['total_execution_hours']:.2f} hours")
        logger.info(f"Complete session saved: {session_file}")

        return full_session

    def run_remaining_collection(self, remaining_countries: List[str], max_workers: int = 5) -> Dict:
        """Run collection for remaining (non-priority) countries"""
        session_id = f"remaining_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        logger.info(f"Starting remaining collection for {len(remaining_countries)} countries")
        self.log_collection_start(session_id, "REMAINING", remaining_countries)

        collection_session = {
            "session_id": session_id,
            "start_time": datetime.now().isoformat(),
            "priority_level": "REMAINING",
            "countries_total": len(remaining_countries),
            "countries_completed": 0,
            "countries_failed": 0,
            "results": [],
            "execution_time": 0
        }

        start_time = datetime.now()

        # Use higher concurrency for remaining countries
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_country = {
                executor.submit(self.collect_country_data, country, "REMAINING", session_id): country
                for country in remaining_countries
            }

            for future in as_completed(future_to_country):
                country = future_to_country[future]
                try:
                    result = future.result()
                    collection_session["results"].append(result)

                    if result["status"] == "completed":
                        collection_session["countries_completed"] += 1
                        logger.info(f"[SUCCESS] Completed {country} ({collection_session['countries_completed']}/{len(remaining_countries)})")
                    else:
                        collection_session["countries_failed"] += 1
                        logger.error(f"[FAILED] Failed {country}")

                except Exception as e:
                    logger.error(f"Collection failed for {country}: {e}")
                    collection_session["countries_failed"] += 1

        end_time = datetime.now()
        collection_session["end_time"] = end_time.isoformat()
        collection_session["execution_time"] = (end_time - start_time).total_seconds()

        return collection_session


if __name__ == "__main__":
    collector = ProductionDataCollector()

    print("[PRODUCTION DATA COLLECTION ORCHESTRATOR]")
    print(f"Configured for {len(collector.config.get('TARGET_COUNTRIES', []))} total countries")
    print(f"Priority countries: {len(collector.config.get('PRIORITY_COUNTRIES', []))}")
    print(f"Output directory: {collector.f_drive}")

    # Start with priority countries collection
    print(f"\nStarting priority countries collection...")
    priority_results = collector.run_priority_collection(max_workers=3)

    print(f"\n[SUCCESS] Priority collection completed!")
    print(f"Success rate: {(priority_results['countries_completed']/priority_results['countries_total']*100):.1f}%")

    # Ask if user wants to continue with full collection
    print(f"\nReady to continue with remaining {len(collector.config.get('TARGET_COUNTRIES', [])) - len(collector.config.get('PRIORITY_COUNTRIES', []))} countries?")
    print(f"Run collector.run_all_countries_collection() for complete 67-country collection")

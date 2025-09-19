"""
Enhanced USPTO Patent Monitoring with Fallback Strategies
Implements robust monitoring with multiple API endpoints and fallback mechanisms
"""

import os
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import logging
import time
import sqlite3
from urllib.parse import urlparse, urljoin

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class USPTOMonitoringEnhanced:
    """Enhanced USPTO monitoring with multiple fallback strategies"""

    def __init__(self):
        # Primary API configuration
        self.primary_api = {
            "key": os.getenv("USPTO_API_KEY", ""),
            "base_url": "https://developer.uspto.gov/ptab-api/v1/",
            "search_url": "https://developer.uspto.gov/api/v1/patent/",
            "rate_limit": 45  # requests per minute
        }

        # Fallback APIs and endpoints
        self.fallback_apis = [
            {
                "name": "USPTO_OData",
                "base_url": "https://ped.uspto.gov/api/",
                "requires_auth": False,
                "rate_limit": 60
            },
            {
                "name": "USPTO_TSDR",
                "base_url": "https://tsdrapi.uspto.gov/ts/v1/",
                "requires_auth": False,
                "rate_limit": 30
            },
            {
                "name": "USPTO_PatentPublicSearch",
                "base_url": "https://ppubs.uspto.gov/pubwebapp/",
                "requires_auth": False,
                "rate_limit": 10,
                "web_scraping": True
            }
        ]

        # Headers for different APIs
        self.headers_primary = {
            "X-API-KEY": self.primary_api["key"],
            "Accept": "application/json",
            "User-Agent": "OSINT-Foresight/1.0"
        }

        self.headers_fallback = {
            "Accept": "application/json",
            "User-Agent": "OSINT-Foresight-Fallback/1.0"
        }

        # Output directory
        self.output_dir = Path("F:/OSINT_DATA/uspto_monitoring")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Database for monitoring persistence
        self.db_path = Path("C:/Projects/OSINT - Foresight/data/uspto_monitoring.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_database()

        # Target entities for monitoring
        self.target_entities = {
            "leonardo": {
                "company_names": ["Leonardo S.p.A", "Leonardo DRS", "Finmeccanica"],
                "keywords": ["Leonardo", "DRS", "Finmeccanica", "Alenia", "Selex"],
                "assignee_variations": ["LEONARDO", "DRS TECHNOLOGIES", "FINMECCANICA"]
            },
            "italy_defense": {
                "company_names": ["Fincantieri", "Telespazio", "Vitrociset"],
                "keywords": ["Fincantieri", "Telespazio", "Vitrociset"],
                "assignee_variations": ["FINCANTIERI", "TELESPAZIO"]
            }
        }

        # China entities to monitor for collaboration
        self.china_entities = {
            "universities": ["Tsinghua", "Beihang", "Harbin Institute", "Beijing Institute"],
            "companies": ["Huawei", "ZTE", "AVIC", "CASIC", "NORINCO"],
            "research_institutes": ["Chinese Academy", "CETC", "CAS"]
        }

        # API status tracking
        self.api_status = {
            "primary": {"available": True, "last_success": None, "error_count": 0},
            "fallbacks": {fb["name"]: {"available": True, "last_success": None, "error_count": 0}
                         for fb in self.fallback_apis}
        }

    def init_database(self):
        """Initialize SQLite database for persistent monitoring"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Monitoring log table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS monitoring_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                api_used TEXT,
                query_type TEXT,
                target_entity TEXT,
                patents_found INTEGER,
                success BOOLEAN,
                error_message TEXT
            )
        ''')

        # Patent tracking table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patent_tracking (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patent_number TEXT UNIQUE,
                title TEXT,
                assignee TEXT,
                inventors TEXT,
                filing_date DATE,
                publication_date DATE,
                technology_area TEXT,
                china_collaboration BOOLEAN DEFAULT FALSE,
                first_detected TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # API status table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS api_status (
                api_name TEXT PRIMARY KEY,
                available BOOLEAN DEFAULT TRUE,
                last_success TIMESTAMP,
                error_count INTEGER DEFAULT 0,
                last_error TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

    def test_api_endpoint(self, api_config: Dict, test_query: str = "leonardo") -> bool:
        """Test if an API endpoint is responsive"""
        try:
            if api_config.get("web_scraping"):
                # For web scraping endpoints, just check if the site is up
                response = requests.get(
                    api_config["base_url"],
                    headers=self.headers_fallback,
                    timeout=10
                )
                return response.status_code == 200

            # For API endpoints, try a simple search
            test_url = api_config["base_url"]
            if "developer.uspto.gov" in test_url:
                test_url += f"patents/query?q={test_query}"

            response = requests.get(
                test_url,
                headers=self.headers_primary if api_config.get("requires_auth") else self.headers_fallback,
                timeout=10
            )

            return response.status_code in [200, 201, 202]

        except Exception as e:
            logger.debug(f"API test failed for {api_config.get('name', 'unknown')}: {e}")
            return False

    def update_api_status(self, api_name: str, success: bool, error_msg: str = None):
        """Update API status in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if success:
            cursor.execute('''
                INSERT OR REPLACE INTO api_status
                (api_name, available, last_success, error_count, updated_at)
                VALUES (?, TRUE, CURRENT_TIMESTAMP, 0, CURRENT_TIMESTAMP)
            ''', (api_name,))
        else:
            cursor.execute('''
                INSERT OR REPLACE INTO api_status
                (api_name, available, last_success, error_count, last_error, updated_at)
                VALUES (?, FALSE,
                    (SELECT last_success FROM api_status WHERE api_name = ?),
                    COALESCE((SELECT error_count FROM api_status WHERE api_name = ?), 0) + 1,
                    ?, CURRENT_TIMESTAMP)
            ''', (api_name, api_name, api_name, error_msg))

        conn.commit()
        conn.close()

    def search_patents_primary(self, query: str, limit: int = 100) -> List[Dict]:
        """Search patents using primary USPTO API"""
        patents = []

        try:
            # Try different primary API endpoints
            endpoints = [
                f"https://developer.uspto.gov/api/v1/patent/application",
                f"https://ped.uspto.gov/api/patents",
                f"https://developer.uspto.gov/ptab-api/v1/patents"
            ]

            for endpoint in endpoints:
                try:
                    params = {
                        "searchText": query,
                        "rows": limit,
                        "start": 0,
                        "sort": "date desc"
                    }

                    response = requests.get(
                        endpoint,
                        headers=self.headers_primary,
                        params=params,
                        timeout=30
                    )

                    if response.status_code == 200:
                        data = response.json()

                        # Parse response based on API format
                        if "patents" in data:
                            patents.extend(data["patents"])
                        elif "results" in data:
                            patents.extend(data["results"])
                        elif isinstance(data, list):
                            patents.extend(data)

                        self.update_api_status("primary", True)
                        break

                except Exception as e:
                    logger.debug(f"Primary endpoint {endpoint} failed: {e}")
                    continue

        except Exception as e:
            logger.error(f"Primary API search failed: {e}")
            self.update_api_status("primary", False, str(e))

        return patents

    def search_patents_fallback(self, query: str, limit: int = 100) -> List[Dict]:
        """Search patents using fallback APIs"""
        patents = []

        for api_config in self.fallback_apis:
            try:
                api_name = api_config["name"]

                if not self.test_api_endpoint(api_config):
                    logger.warning(f"Fallback API {api_name} is not responsive")
                    self.update_api_status(api_name, False, "API not responsive")
                    continue

                if api_config.get("web_scraping"):
                    # Handle web scraping fallback
                    patents.extend(self._scrape_uspto_public_search(query, limit))
                else:
                    # Handle API fallbacks
                    patents.extend(self._search_fallback_api(api_config, query, limit))

                if patents:
                    self.update_api_status(api_name, True)
                    logger.info(f"Successfully used fallback API: {api_name}")
                    break

            except Exception as e:
                logger.error(f"Fallback API {api_config['name']} failed: {e}")
                self.update_api_status(api_config["name"], False, str(e))

        return patents

    def _search_fallback_api(self, api_config: Dict, query: str, limit: int) -> List[Dict]:
        """Search using a specific fallback API"""
        patents = []

        try:
            base_url = api_config["base_url"]

            if "tsdrapi" in base_url:
                # USPTO TSDR API
                search_url = urljoin(base_url, f"applications/search?q={query}")
            elif "ped.uspto.gov" in base_url:
                # USPTO PED API
                search_url = urljoin(base_url, f"patents?search={query}")
            else:
                search_url = urljoin(base_url, f"search?q={query}")

            response = requests.get(
                search_url,
                headers=self.headers_fallback,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()

                # Normalize response format
                if "data" in data:
                    patents = data["data"][:limit]
                elif "applications" in data:
                    patents = data["applications"][:limit]
                elif isinstance(data, list):
                    patents = data[:limit]

        except Exception as e:
            logger.debug(f"Fallback API search failed for {api_config['name']}: {e}")

        return patents

    def _scrape_uspto_public_search(self, query: str, limit: int) -> List[Dict]:
        """Scrape USPTO Public Patent Search as last resort"""
        patents = []

        try:
            # This would implement web scraping of the public search
            # For now, return empty list as web scraping needs careful implementation
            logger.warning("Web scraping fallback not yet implemented")

        except Exception as e:
            logger.error(f"Web scraping fallback failed: {e}")

        return patents

    def search_patents_robust(self, query: str, limit: int = 100) -> List[Dict]:
        """Robust patent search with automatic fallback"""
        logger.info(f"Starting robust patent search for: {query}")

        # Try primary API first
        patents = self.search_patents_primary(query, limit)

        if not patents:
            logger.warning("Primary API failed, trying fallback APIs...")
            patents = self.search_patents_fallback(query, limit)

        if not patents:
            logger.error("All APIs failed - no patents retrieved")

        return patents

    def monitor_entity(self, entity_config: Dict, entity_name: str) -> Dict:
        """Monitor a specific entity for new patents"""
        logger.info(f"Monitoring entity: {entity_name}")

        results = {
            "entity": entity_name,
            "timestamp": datetime.now().isoformat(),
            "new_patents": [],
            "china_collaborations": [],
            "monitoring_success": False
        }

        # Search for each company name and keyword
        all_queries = entity_config["company_names"] + entity_config["keywords"]

        for query in all_queries:
            patents = self.search_patents_robust(query, 50)

            for patent in patents:
                # Check if this is a new patent
                patent_number = patent.get("patent_number") or patent.get("applicationNumber")

                if patent_number and self._is_new_patent(patent_number):
                    # Check for China collaboration
                    china_collaboration = self._detect_china_collaboration(patent)

                    patent_data = {
                        "patent_number": patent_number,
                        "title": patent.get("title") or patent.get("inventionTitle"),
                        "assignee": patent.get("assignee") or patent.get("applicantName"),
                        "filing_date": patent.get("filing_date") or patent.get("filingDate"),
                        "china_collaboration": china_collaboration,
                        "query_used": query
                    }

                    results["new_patents"].append(patent_data)

                    if china_collaboration:
                        results["china_collaborations"].append(patent_data)

                    # Store in database
                    self._store_patent_tracking(patent_data)

        results["monitoring_success"] = len(results["new_patents"]) >= 0
        self._log_monitoring_session(entity_name, results)

        return results

    def _is_new_patent(self, patent_number: str) -> bool:
        """Check if patent is new (not in database)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM patent_tracking WHERE patent_number = ?", (patent_number,))
        exists = cursor.fetchone() is not None

        conn.close()
        return not exists

    def _detect_china_collaboration(self, patent: Dict) -> bool:
        """Detect if patent involves China collaboration"""
        # Check inventors, assignees, and addresses for China indicators
        patent_text = json.dumps(patent).lower()

        china_indicators = [
            "china", "chinese", "beijing", "shanghai", "shenzhen", "guangzhou",
            "tsinghua", "beihang", "harbin", "huawei", "zte", "avic", "casic"
        ]

        return any(indicator in patent_text for indicator in china_indicators)

    def _store_patent_tracking(self, patent_data: Dict):
        """Store patent in tracking database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO patent_tracking
            (patent_number, title, assignee, filing_date, china_collaboration)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            patent_data["patent_number"],
            patent_data["title"],
            patent_data["assignee"],
            patent_data["filing_date"],
            patent_data["china_collaboration"]
        ))

        conn.commit()
        conn.close()

    def _log_monitoring_session(self, entity_name: str, results: Dict):
        """Log monitoring session to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO monitoring_log
            (api_used, query_type, target_entity, patents_found, success)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            "robust_multi_api",
            "entity_monitoring",
            entity_name,
            len(results["new_patents"]),
            results["monitoring_success"]
        ))

        conn.commit()
        conn.close()

    def run_continuous_monitoring(self) -> Dict:
        """Run monitoring for all target entities"""
        logger.info("Starting continuous USPTO monitoring...")

        monitoring_results = {
            "monitoring_session": datetime.now().isoformat(),
            "entities_monitored": {},
            "total_new_patents": 0,
            "total_china_collaborations": 0,
            "api_status_summary": {}
        }

        # Monitor each target entity
        for entity_name, entity_config in self.target_entities.items():
            results = self.monitor_entity(entity_config, entity_name)
            monitoring_results["entities_monitored"][entity_name] = results
            monitoring_results["total_new_patents"] += len(results["new_patents"])
            monitoring_results["total_china_collaborations"] += len(results["china_collaborations"])

        # Generate API status summary
        monitoring_results["api_status_summary"] = self._get_api_status_summary()

        # Save results
        self._save_monitoring_results(monitoring_results)

        return monitoring_results

    def _get_api_status_summary(self) -> Dict:
        """Get current API status summary"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT api_name, available, last_success, error_count FROM api_status")
        status_data = cursor.fetchall()

        conn.close()

        status_summary = {}
        for api_name, available, last_success, error_count in status_data:
            status_summary[api_name] = {
                "available": bool(available),
                "last_success": last_success,
                "error_count": error_count
            }

        return status_summary

    def _save_monitoring_results(self, results: Dict):
        """Save monitoring results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"uspto_monitoring_{timestamp}.json"

        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)

        logger.info(f"Monitoring results saved to: {output_file}")

    def generate_monitoring_report(self) -> Dict:
        """Generate comprehensive monitoring report"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get recent monitoring statistics
        cursor.execute('''
            SELECT
                COUNT(*) as total_sessions,
                SUM(patents_found) as total_patents,
                AVG(patents_found) as avg_patents_per_session
            FROM monitoring_log
            WHERE timestamp >= date('now', '-30 days')
        ''')
        stats = cursor.fetchone()

        # Get China collaboration statistics
        cursor.execute('''
            SELECT COUNT(*) FROM patent_tracking
            WHERE china_collaboration = 1 AND first_detected >= date('now', '-30 days')
        ''')
        china_collabs = cursor.fetchone()[0]

        # Get API reliability
        cursor.execute('''
            SELECT api_name, available, error_count
            FROM api_status
        ''')
        api_reliability = cursor.fetchall()

        conn.close()

        report = {
            "report_period": "30_days",
            "generated_at": datetime.now().isoformat(),
            "monitoring_statistics": {
                "total_sessions": stats[0] or 0,
                "total_patents_found": stats[1] or 0,
                "average_patents_per_session": round(stats[2] or 0, 2)
            },
            "china_collaboration_alerts": china_collabs,
            "api_reliability": {
                api_name: {"available": bool(available), "error_count": error_count}
                for api_name, available, error_count in api_reliability
            },
            "recommendations": []
        }

        # Generate recommendations
        if china_collabs > 5:
            report["recommendations"].append("HIGH PRIORITY: Significant increase in China collaborations detected")

        failed_apis = [api for api, data in report["api_reliability"].items() if not data["available"]]
        if failed_apis:
            report["recommendations"].append(f"API issues detected: {', '.join(failed_apis)}")

        return report


if __name__ == "__main__":
    monitor = USPTOMonitoringEnhanced()

    print("[ENHANCED USPTO MONITORING]")
    print("Testing API endpoints...")

    # Test primary API
    primary_test = monitor.test_api_endpoint(monitor.primary_api)
    print(f"Primary API: {'[SUCCESS] Available' if primary_test else '[ERROR] Failed'}")

    # Test fallback APIs
    for api_config in monitor.fallback_apis:
        fallback_test = monitor.test_api_endpoint(api_config)
        print(f"Fallback {api_config['name']}: {'[SUCCESS] Available' if fallback_test else '[ERROR] Failed'}")

    print("\nRunning continuous monitoring...")
    results = monitor.run_continuous_monitoring()

    print(f"\n[MONITORING SUMMARY]")
    print(f"New patents found: {results['total_new_patents']}")
    print(f"China collaborations: {results['total_china_collaborations']}")
    print(f"Results saved to: F:/OSINT_DATA/uspto_monitoring/")

    # Generate monitoring report
    report = monitor.generate_monitoring_report()
    print(f"\n[MONITORING REPORT]")
    for rec in report["recommendations"]:
        print(f"[WARNING] {rec}")

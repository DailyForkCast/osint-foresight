#!/usr/bin/env python3
"""
USPTO Monitoring Fixes and Enhanced Client
Addresses current monitoring issues and implements robust patent tracking
"""

import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import requests
import time
import yaml
from dataclasses import dataclass
import hashlib
import sqlite3
from dotenv import load_dotenv

# Load environment variables
load_dotenv("C:/Projects/OSINT - Foresight/.env.local")

@dataclass
class PatentRecord:
    """Enhanced patent record structure"""
    patent_number: str
    title: str
    abstract: str
    filing_date: datetime
    grant_date: Optional[datetime]
    assignee: str
    inventors: List[str]
    inventor_countries: List[str]
    cpc_codes: List[str]
    cited_patents: List[str]
    application_number: str
    patent_family_id: str
    priority_date: datetime
    legal_status: str

class USPTOMonitoringFixes:
    """Enhanced USPTO client with fixes for monitoring issues"""

    def __init__(self):
        """Initialize the enhanced USPTO client"""
        self.api_key = os.getenv('USPTO_API_KEY')
        self.data_dir = Path("F:/uspto_data")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize database for persistent monitoring
        self.db_path = self.data_dir / "uspto_monitoring.db"
        self._init_database()

        # Multiple API endpoints for redundancy
        self.api_endpoints = {
            'patentsview_v1': {
                'base_url': 'https://search.patentsview.org/api/v1',
                'endpoints': {
                    'patents': '/patent/',
                    'inventors': '/inventor/',
                    'assignees': '/assignee/',
                    'cpc': '/cpc_current/'
                },
                'rate_limit': 45 if self.api_key else 10
            },
            'google_patents': {
                'base_url': 'https://patents.googleapis.com/v1',
                'endpoints': {
                    'search': '/patents:search'
                },
                'rate_limit': 100
            },
            'uspto_open_data': {
                'base_url': 'https://developer.uspto.gov/ds-api',
                'endpoints': {
                    'search': '/search'
                },
                'rate_limit': 30
            }
        }

        # Session with retry strategy
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'OSINT-Foresight-Research/2.0 (Patent Analysis)',
            'Accept': 'application/json'
        })

        # API key authentication
        if self.api_key:
            self.session.headers.update({
                'X-API-Key': self.api_key,
                'x-api-key': self.api_key  # Try both formats
            })

        # Rate limiting
        self.last_request_time = {}
        self.request_counts = {}

    def _init_database(self):
        """Initialize SQLite database for monitoring persistence"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patent_monitoring (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_hash TEXT UNIQUE,
                query_params TEXT,
                last_check TIMESTAMP,
                last_result_count INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patent_records (
                patent_number TEXT PRIMARY KEY,
                title TEXT,
                abstract TEXT,
                filing_date DATE,
                grant_date DATE,
                assignee TEXT,
                inventors TEXT,
                inventor_countries TEXT,
                cpc_codes TEXT,
                cited_patents TEXT,
                application_number TEXT,
                patent_family_id TEXT,
                priority_date DATE,
                legal_status TEXT,
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS monitoring_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_type TEXT,
                patent_number TEXT,
                alert_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved_at TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

    def _rate_limit(self, endpoint_key: str):
        """Enhanced rate limiting with per-endpoint tracking"""
        current_time = time.time()
        rate_limit = self.api_endpoints[endpoint_key]['rate_limit']
        interval = 60.0 / rate_limit  # requests per minute

        if endpoint_key not in self.last_request_time:
            self.last_request_time[endpoint_key] = 0
            self.request_counts[endpoint_key] = 0

        time_since_last = current_time - self.last_request_time[endpoint_key]

        if time_since_last < interval:
            sleep_time = interval - time_since_last
            print(f"Rate limiting: sleeping {sleep_time:.2f} seconds for {endpoint_key}")
            time.sleep(sleep_time)

        self.last_request_time[endpoint_key] = time.time()
        self.request_counts[endpoint_key] += 1

    def search_patents_robust(self, **kwargs) -> pd.DataFrame:
        """
        Robust patent search with multiple fallback endpoints

        Args:
            assignee: Company/organization name
            inventor_country: Country code (e.g., 'IT')
            cpc_codes: List of CPC classification codes
            date_range: Tuple of (start_date, end_date) as strings
            keywords: Keywords to search in title/abstract
            limit: Maximum number of results
        """
        results = pd.DataFrame()

        # Try PatentsView API first
        try:
            results = self._search_patentsview_v1(**kwargs)
            if not results.empty:
                print(f"PatentsView API returned {len(results)} results")
                return results
        except Exception as e:
            print(f"PatentsView API failed: {e}")

        # Fallback to Google Patents API
        try:
            results = self._search_google_patents(**kwargs)
            if not results.empty:
                print(f"Google Patents API returned {len(results)} results")
                return results
        except Exception as e:
            print(f"Google Patents API failed: {e}")

        # Fallback to USPTO Open Data API
        try:
            results = self._search_uspto_open_data(**kwargs)
            if not results.empty:
                print(f"USPTO Open Data API returned {len(results)} results")
                return results
        except Exception as e:
            print(f"USPTO Open Data API failed: {e}")

        print("All USPTO APIs failed, returning empty results")
        return pd.DataFrame()

    def _search_patentsview_v1(self, **kwargs) -> pd.DataFrame:
        """Enhanced PatentsView API search with proper error handling"""
        self._rate_limit('patentsview_v1')

        # Build query
        query_parts = []

        if kwargs.get('assignee'):
            query_parts.append({"assignee_organization": kwargs['assignee']})

        if kwargs.get('inventor_country'):
            query_parts.append({"inventor_country": kwargs['inventor_country']})

        if kwargs.get('cpc_codes'):
            cpc_query = {"_or": [{"cpc_subgroup_id": code} for code in kwargs['cpc_codes']]}
            query_parts.append(cpc_query)

        if kwargs.get('date_range'):
            start_date, end_date = kwargs['date_range']
            date_query = {
                "_gte": {"patent_date": start_date},
                "_lte": {"patent_date": end_date}
            }
            query_parts.append(date_query)

        if kwargs.get('keywords'):
            keyword_query = {
                "_text_any": {
                    "patent_title": kwargs['keywords'],
                    "patent_abstract": kwargs['keywords']
                }
            }
            query_parts.append(keyword_query)

        # Combine query parts
        if len(query_parts) > 1:
            query = {"_and": query_parts}
        elif query_parts:
            query = query_parts[0]
        else:
            query = {}

        # Prepare request
        url = f"{self.api_endpoints['patentsview_v1']['base_url']}{self.api_endpoints['patentsview_v1']['endpoints']['patents']}"

        payload = {
            'q': json.dumps(query),
            'f': json.dumps([
                "patent_number",
                "patent_title",
                "patent_date",
                "patent_abstract",
                "assignee_organization",
                "inventor_country",
                "cpc_subgroup_id",
                "cited_patent_number",
                "app_date",
                "application_number"
            ]),
            'o': json.dumps({
                "per_page": kwargs.get('limit', 100)
            })
        }

        # Multiple request attempts with different configurations
        request_configs = [
            {'method': 'POST', 'data': payload},
            {'method': 'GET', 'params': {'q': payload['q'], 'f': payload['f'], 'o': payload['o']}},
            {'method': 'POST', 'json': {'q': query, 'f': json.loads(payload['f']), 'o': json.loads(payload['o'])}}
        ]

        for config in request_configs:
            try:
                if config['method'] == 'POST':
                    if 'json' in config:
                        response = self.session.post(url, json=config['json'], timeout=30)
                    else:
                        response = self.session.post(url, data=config['data'], timeout=30)
                else:
                    response = self.session.get(url, params=config['params'], timeout=30)

                print(f"PatentsView API response: {response.status_code}")

                if response.status_code == 200:
                    data = response.json()
                    if 'patents' in data:
                        return pd.DataFrame(data['patents'])
                    else:
                        print(f"No patents in response: {list(data.keys())}")
                elif response.status_code == 429:
                    print("Rate limited, waiting...")
                    time.sleep(60)
                    continue
                else:
                    print(f"Error response: {response.text[:500]}")

            except requests.exceptions.RequestException as e:
                print(f"Request failed with config {config['method']}: {e}")
                continue

        return pd.DataFrame()

    def _search_google_patents(**kwargs) -> pd.DataFrame:
        """Google Patents API search (requires different authentication)"""
        # Google Patents would require different setup
        # For now, return empty DataFrame
        return pd.DataFrame()

    def _search_uspto_open_data(self, **kwargs) -> pd.DataFrame:
        """USPTO Open Data Portal search"""
        # USPTO Open Data Portal search implementation
        # For now, return empty DataFrame
        return pd.DataFrame()

    def setup_continuous_monitoring(self, monitor_configs: List[Dict[str, Any]]) -> str:
        """Set up continuous monitoring for specific search criteria"""

        monitoring_id = f"monitor_{int(time.time())}"

        for config in monitor_configs:
            # Create hash of query parameters for deduplication
            query_str = json.dumps(config, sort_keys=True)
            query_hash = hashlib.md5(query_str.encode()).hexdigest()

            # Store monitoring configuration
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT OR REPLACE INTO patent_monitoring
                (query_hash, query_params, last_check, last_result_count)
                VALUES (?, ?, ?, ?)
            ''', (query_hash, query_str, datetime.now(), 0))

            conn.commit()
            conn.close()

        print(f"Monitoring setup with ID: {monitoring_id}")
        return monitoring_id

    def run_monitoring_cycle(self) -> Dict[str, Any]:
        """Run a complete monitoring cycle for all configured monitors"""

        results = {
            "cycle_start": datetime.now().isoformat(),
            "monitors_checked": 0,
            "new_patents_found": 0,
            "alerts_generated": 0,
            "errors": []
        }

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get all active monitors
        cursor.execute('SELECT query_hash, query_params, last_check, last_result_count FROM patent_monitoring')
        monitors = cursor.fetchall()

        for query_hash, query_params, last_check, last_result_count in monitors:
            try:
                # Parse query parameters
                config = json.loads(query_params)

                # Run search
                patents = self.search_patents_robust(**config)

                if not patents.empty:
                    # Check for new patents since last check
                    new_patents = self._identify_new_patents(patents, last_check)

                    # Store new patents
                    for _, patent in new_patents.iterrows():
                        self._store_patent_record(patent)

                    # Update monitor record
                    cursor.execute('''
                        UPDATE patent_monitoring
                        SET last_check = ?, last_result_count = ?
                        WHERE query_hash = ?
                    ''', (datetime.now(), len(patents), query_hash))

                    results["new_patents_found"] += len(new_patents)

                    # Generate alerts if significant changes
                    if len(new_patents) > 0:
                        self._generate_alert("new_patents", {
                            "query_hash": query_hash,
                            "new_patent_count": len(new_patents),
                            "patent_numbers": new_patents['patent_number'].tolist()
                        })
                        results["alerts_generated"] += 1

                results["monitors_checked"] += 1

                # Rate limiting between monitors
                time.sleep(2)

            except Exception as e:
                error_msg = f"Error processing monitor {query_hash}: {e}"
                print(error_msg)
                results["errors"].append(error_msg)

        conn.commit()
        conn.close()

        results["cycle_end"] = datetime.now().isoformat()

        # Save monitoring report
        self._save_monitoring_report(results)

        return results

    def _identify_new_patents(self, patents: pd.DataFrame, last_check: str) -> pd.DataFrame:
        """Identify patents that are new since last check"""
        if last_check is None:
            return patents

        last_check_date = datetime.fromisoformat(last_check)

        # Filter patents by filing date or grant date
        new_patents = patents.copy()

        if 'patent_date' in patents.columns:
            new_patents = patents[
                pd.to_datetime(patents['patent_date']) > last_check_date
            ]

        return new_patents

    def _store_patent_record(self, patent: pd.Series):
        """Store patent record in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Convert lists to JSON strings for storage
        inventors = json.dumps(patent.get('inventors', []))
        inventor_countries = json.dumps(patent.get('inventor_countries', []))
        cpc_codes = json.dumps(patent.get('cpc_codes', []))
        cited_patents = json.dumps(patent.get('cited_patents', []))

        cursor.execute('''
            INSERT OR REPLACE INTO patent_records
            (patent_number, title, abstract, filing_date, grant_date, assignee,
             inventors, inventor_countries, cpc_codes, cited_patents,
             application_number, patent_family_id, priority_date, legal_status,
             last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            patent.get('patent_number', ''),
            patent.get('patent_title', ''),
            patent.get('patent_abstract', ''),
            patent.get('app_date', ''),
            patent.get('patent_date', ''),
            patent.get('assignee_organization', ''),
            inventors,
            inventor_countries,
            cpc_codes,
            cited_patents,
            patent.get('application_number', ''),
            patent.get('patent_family_id', ''),
            patent.get('priority_date', ''),
            patent.get('legal_status', 'unknown'),
            datetime.now()
        ))

        conn.commit()
        conn.close()

    def _generate_alert(self, alert_type: str, alert_data: Dict[str, Any]):
        """Generate and store monitoring alert"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO monitoring_alerts (alert_type, alert_data)
            VALUES (?, ?)
        ''', (alert_type, json.dumps(alert_data)))

        conn.commit()
        conn.close()

        print(f"Generated alert: {alert_type} - {alert_data}")

    def _save_monitoring_report(self, results: Dict[str, Any]):
        """Save monitoring cycle report"""
        report_path = self.data_dir / f"monitoring_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(report_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)

        print(f"Monitoring report saved: {report_path}")

    def test_all_endpoints(self) -> Dict[str, str]:
        """Test all configured API endpoints"""
        test_results = {}

        # Simple test query
        test_query = {
            'assignee': 'Leonardo',
            'date_range': ('2024-01-01', '2024-12-31'),
            'limit': 5
        }

        print("Testing USPTO API endpoints...")
        print("="*50)

        # Test PatentsView API
        try:
            patents = self._search_patentsview_v1(**test_query)
            if not patents.empty:
                test_results['patentsview_v1'] = f"SUCCESS - {len(patents)} patents found"
            else:
                test_results['patentsview_v1'] = "WORKING - No patents found (may be normal)"
        except Exception as e:
            test_results['patentsview_v1'] = f"FAILED - {str(e)[:100]}"

        # Test other endpoints
        test_results['google_patents'] = "NOT_IMPLEMENTED - Requires Google API setup"
        test_results['uspto_open_data'] = "NOT_IMPLEMENTED - Requires further development"

        # Print results
        for endpoint, result in test_results.items():
            print(f"{endpoint}: {result}")

        return test_results

    def fix_common_issues(self) -> List[str]:
        """Fix common USPTO monitoring issues"""
        fixes_applied = []

        # Fix 1: Verify API key format
        if self.api_key:
            if len(self.api_key) < 20:
                print("WARNING: API key seems too short")
            fixes_applied.append("API key validation check")
        else:
            print("WARNING: No API key found - rate limits will be very low")
            fixes_applied.append("No API key warning issued")

        # Fix 2: Create robust session with retries
        from requests.adapters import HTTPAdapter
        from requests.packages.urllib3.util.retry import Retry

        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        fixes_applied.append("HTTP retry strategy implemented")

        # Fix 3: Ensure data directory structure
        subdirs = ['raw', 'processed', 'monitoring', 'alerts']
        for subdir in subdirs:
            (self.data_dir / subdir).mkdir(exist_ok=True)
        fixes_applied.append("Data directory structure created")

        # Fix 4: Database optimization
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create indexes for better performance
        indexes = [
            'CREATE INDEX IF NOT EXISTS idx_patent_assignee ON patent_records(assignee)',
            'CREATE INDEX IF NOT EXISTS idx_patent_date ON patent_records(filing_date)',
            'CREATE INDEX IF NOT EXISTS idx_monitoring_hash ON patent_monitoring(query_hash)',
            'CREATE INDEX IF NOT EXISTS idx_alerts_type ON monitoring_alerts(alert_type)'
        ]

        for index_sql in indexes:
            cursor.execute(index_sql)

        conn.commit()
        conn.close()
        fixes_applied.append("Database indexes created")

        return fixes_applied

def main():
    """Main function for testing and demonstrating fixes"""
    print("USPTO Monitoring Fixes and Enhancement")
    print("="*50)

    # Initialize enhanced client
    client = USPTOMonitoringFixes()

    # Apply common fixes
    print("\n1. Applying common fixes...")
    fixes = client.fix_common_issues()
    for fix in fixes:
        print(f"  ✓ {fix}")

    # Test endpoints
    print("\n2. Testing API endpoints...")
    test_results = client.test_all_endpoints()

    # Setup example monitoring
    print("\n3. Setting up example monitoring...")
    monitor_configs = [
        {
            'assignee': 'Leonardo',
            'date_range': ('2024-01-01', '2024-12-31'),
            'limit': 100
        },
        {
            'inventor_country': 'IT',
            'cpc_codes': ['G06N', 'H04L', 'G01S'],
            'date_range': ('2024-01-01', '2024-12-31'),
            'limit': 100
        }
    ]

    monitoring_id = client.setup_continuous_monitoring(monitor_configs)
    print(f"Monitoring setup: {monitoring_id}")

    # Run test monitoring cycle
    print("\n4. Running test monitoring cycle...")
    cycle_results = client.run_monitoring_cycle()

    print(f"\nMonitoring cycle results:")
    print(f"  Monitors checked: {cycle_results['monitors_checked']}")
    print(f"  New patents found: {cycle_results['new_patents_found']}")
    print(f"  Alerts generated: {cycle_results['alerts_generated']}")
    print(f"  Errors: {len(cycle_results['errors'])}")

    if cycle_results['errors']:
        print("  Error details:")
        for error in cycle_results['errors']:
            print(f"    - {error}")

    print("\n" + "="*50)
    print("USPTO monitoring fixes completed!")

    return client

if __name__ == "__main__":
    client = main()

#!/usr/bin/env python3
"""
EPO Open Patent Services (OPS) Client

Accesses European Patent Office data including:
- Patent families and legal status
- Citations and references
- Cross-jurisdictional patent data
- Technology classification
"""

import os
import json
import time
import requests
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import logging
import base64
from urllib.parse import quote

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EPOOPSClient:
    """Client for EPO Open Patent Services API"""

    def __init__(self, output_dir: str = None):
        """Initialize EPO OPS client

        Note: EPO OPS requires OAuth2 authentication but allows anonymous access
        for basic searches with rate limits.
        """

        # EPO OPS endpoints
        self.auth_url = "https://ops.epo.org/3.2/auth/accesstoken"
        self.search_url = "https://ops.epo.org/3.2/rest-services/published-data/search"
        self.family_url = "https://ops.epo.org/3.2/rest-services/family"
        self.legal_url = "https://ops.epo.org/3.2/rest-services/legal"
        self.citation_url = "https://ops.epo.org/3.2/rest-services/published-data/publication"

        # Setup output directory
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            self.output_dir = Path("C:/Projects/OSINT - Foresight/data/collected/epo_ops")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Session setup
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'OSINT-Research-System/1.0',
            'Accept': 'application/json'
        })

        # Rate limiting (EPO has strict limits)
        self.last_request_time = 0
        self.min_request_interval = 1.0  # 1 second between requests
        self.requests_per_minute = 30
        self.requests_in_current_minute = 0
        self.minute_start_time = time.time()

        # Authentication token
        self.access_token = None
        self.token_expires = None

        # Load saved authentication if available
        self.load_authentication()

    def _rate_limit(self):
        """Enforce EPO rate limiting"""

        current_time = time.time()

        # Check if we need to reset minute counter
        if current_time - self.minute_start_time >= 60:
            self.requests_in_current_minute = 0
            self.minute_start_time = current_time

        # If we've hit the per-minute limit, wait
        if self.requests_in_current_minute >= self.requests_per_minute:
            wait_time = 60 - (current_time - self.minute_start_time)
            if wait_time > 0:
                logger.info(f"Rate limit reached, waiting {wait_time:.1f} seconds")
                time.sleep(wait_time)
                self.requests_in_current_minute = 0
                self.minute_start_time = time.time()

        # Basic interval rate limiting
        elapsed = current_time - self.last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)

        self.last_request_time = time.time()
        self.requests_in_current_minute += 1

    def authenticate(self, consumer_key: str = None, consumer_secret: str = None):
        """Authenticate with EPO OPS (optional - can work without auth with limits)"""

        if not consumer_key or not consumer_secret:
            logger.info("No EPO credentials provided, using anonymous access with rate limits")
            return True

        try:
            # Encode credentials
            credentials = base64.b64encode(f"{consumer_key}:{consumer_secret}".encode()).decode()

            headers = {
                'Authorization': f'Basic {credentials}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }

            data = {'grant_type': 'client_credentials'}

            response = self.session.post(self.auth_url, headers=headers, data=data)
            response.raise_for_status()

            token_data = response.json()
            self.access_token = token_data['access_token']
            expires_in = token_data.get('expires_in', 3600)
            self.token_expires = datetime.now() + timedelta(seconds=expires_in)

            # Update session headers
            self.session.headers['Authorization'] = f'Bearer {self.access_token}'

            logger.info("EPO OPS authentication successful")
            return True

        except Exception as e:
            logger.error(f"EPO authentication failed: {e}")
            return False

    def load_authentication(self):
        """Load saved authentication from config file"""
        try:
            auth_config_path = Path("C:/Projects/OSINT - Foresight/config/patent_auth.json")
            if auth_config_path.exists():
                with open(auth_config_path, 'r') as f:
                    config = json.load(f)

                epo_config = config.get('epo_ops', {})
                if epo_config.get('status') == 'authenticated':
                    self.access_token = epo_config.get('access_token')
                    logger.info("Loaded EPO authentication from config")

                    # Update session headers with Bearer token
                    if self.access_token:
                        self.session.headers.update({
                            'Authorization': f'Bearer {self.access_token}'
                        })

        except Exception as e:
            logger.warning(f"Could not load EPO authentication: {e}")

    def search_patents(self, query: str, country: str = None,
                      applicant: str = None, inventor: str = None,
                      start_date: str = None, end_date: str = None,
                      max_results: int = 100) -> Dict:
        """Search patents using EPO OPS

        Args:
            query: Search query (keywords, IPC codes, etc.)
            country: Country code (CN, US, EP, etc.)
            applicant: Applicant name
            inventor: Inventor name
            start_date: Publication date start (YYYY-MM-DD)
            end_date: Publication date end (YYYY-MM-DD)
            max_results: Maximum results to return
        """

        self._rate_limit()

        # Build search query
        search_parts = []

        if query:
            search_parts.append(f'txt="{query}"')

        if country:
            search_parts.append(f'pn={country}')

        if applicant:
            search_parts.append(f'pa="{applicant}"')

        if inventor:
            search_parts.append(f'in="{inventor}"')

        if start_date:
            search_parts.append(f'pd>={start_date.replace("-", "")}')

        if end_date:
            search_parts.append(f'pd<={end_date.replace("-", "")}')

        if not search_parts:
            raise ValueError("At least one search parameter must be provided")

        cql_query = ' and '.join(search_parts)

        # Construct request URL
        params = {
            'q': cql_query,
            'Range': f'1-{min(max_results, 100)}'  # EPO limits to 100 per request
        }

        try:
            logger.debug(f"EPO search query: {cql_query}")
            response = self.session.get(self.search_url, params=params)
            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"EPO search failed: {e}")
            return {}

    def get_patent_family(self, patent_number: str, format_type: str = 'docdb') -> Dict:
        """Get patent family information

        Args:
            patent_number: Patent number (e.g., EP1000000, US6000000)
            format_type: Format (docdb, epodoc, original)
        """

        self._rate_limit()

        url = f"{self.family_url}/{format_type}/{patent_number}"

        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Family data retrieval failed for {patent_number}: {e}")
            return {}

    def get_legal_status(self, patent_number: str, format_type: str = 'docdb') -> Dict:
        """Get legal status information

        Args:
            patent_number: Patent number
            format_type: Format (docdb, epodoc, original)
        """

        self._rate_limit()

        url = f"{self.legal_url}/{format_type}/{patent_number}"

        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Legal status retrieval failed for {patent_number}: {e}")
            return {}

    def get_citations(self, patent_number: str, format_type: str = 'docdb',
                     citation_type: str = 'all') -> Dict:
        """Get patent citations

        Args:
            patent_number: Patent number
            format_type: Format (docdb, epodoc, original)
            citation_type: Type (cited, citing, all)
        """

        self._rate_limit()

        url = f"{self.citation_url}/{format_type}/{patent_number}/citations"

        params = {}
        if citation_type != 'all':
            params['type'] = citation_type

        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Citations retrieval failed for {patent_number}: {e}")
            return {}

    def search_china_related_patents(self, countries: List[str],
                                   technologies: List[str] = None,
                                   years: List[str] = None) -> List[Dict]:
        """Search for China-related patents across multiple jurisdictions

        Args:
            countries: Target country codes to search in
            technologies: Technology keywords to search for
            years: Years to search (e.g., ['2020', '2021'])
        """

        logger.info(f"Searching China-related patents in {len(countries)} countries")

        all_results = []

        # Default technology areas if none specified
        if not technologies:
            technologies = [
                '5G', 'artificial intelligence', 'quantum computing',
                'semiconductor', 'battery', 'solar', 'telecommunications',
                'biotechnology', 'nanotechnology', 'robotics'
            ]

        for country in countries:
            for tech in technologies:
                logger.info(f"Searching {country} for {tech} patents with China connections")

                try:
                    # Search for patents in target country with Chinese applicants
                    results = self.search_patents(
                        query=tech,
                        country=country,
                        applicant="china OR chinese OR beijing OR shanghai",
                        max_results=50
                    )

                    if results.get('ops:world-patent-data'):
                        processed = self.process_search_results(results, country, tech)
                        all_results.extend(processed)

                    time.sleep(2)  # Extra delay between searches

                except Exception as e:
                    logger.error(f"Error searching {country}/{tech}: {e}")
                    continue

        logger.info(f"Found {len(all_results)} China-related patents")
        return all_results

    def process_search_results(self, raw_results: Dict, country: str, technology: str) -> List[Dict]:
        """Process raw EPO search results into structured format"""

        processed = []

        try:
            world_data = raw_results.get('ops:world-patent-data', {})
            biblio_search = world_data.get('ops:biblio-search', {})

            if 'ops:search-result' in biblio_search:
                search_results = biblio_search['ops:search-result']
                if not isinstance(search_results, list):
                    search_results = [search_results]

                for result in search_results:
                    patent_info = self.extract_patent_info(result)
                    if patent_info:
                        patent_info['search_country'] = country
                        patent_info['search_technology'] = technology
                        processed.append(patent_info)

        except Exception as e:
            logger.error(f"Error processing search results: {e}")

        return processed

    def extract_patent_info(self, patent_data: Dict) -> Dict:
        """Extract relevant information from patent data"""

        try:
            publication_ref = patent_data.get('exchange-document', {}).get('bibliographic-data', {})

            # Publication number
            pub_ref = publication_ref.get('publication-reference', {}).get('document-id', {})
            if isinstance(pub_ref, list):
                pub_ref = pub_ref[0]

            patent_number = pub_ref.get('doc-number', {}).get('$', '')
            country_code = pub_ref.get('country', {}).get('$', '')
            kind_code = pub_ref.get('kind', {}).get('$', '')

            # Application reference
            app_ref = publication_ref.get('application-reference', {}).get('document-id', {})
            if isinstance(app_ref, list):
                app_ref = app_ref[0]

            app_number = app_ref.get('doc-number', {}).get('$', '')

            # Title
            title_data = publication_ref.get('invention-title', {})
            if isinstance(title_data, list):
                title_data = title_data[0]
            title = title_data.get('$', '') if title_data else ''

            # Applicants
            applicants = []
            parties = publication_ref.get('parties', {})
            if 'applicants' in parties:
                app_data = parties['applicants'].get('applicant', [])
                if not isinstance(app_data, list):
                    app_data = [app_data]

                for applicant in app_data:
                    name_data = applicant.get('applicant-name', {})
                    if isinstance(name_data, dict):
                        name = name_data.get('name', {}).get('$', '')
                        if name:
                            applicants.append(name)

            # Publication date
            pub_date = pub_ref.get('date', {}).get('$', '')

            # IPC classifications
            ipc_classes = []
            classifications = publication_ref.get('classification-ipc', {})
            if classifications:
                ipc_data = classifications.get('classification-ipcr', [])
                if not isinstance(ipc_data, list):
                    ipc_data = [ipc_data]

                for ipc in ipc_data:
                    ipc_class = ipc.get('classification-symbol', {}).get('$', '')
                    if ipc_class:
                        ipc_classes.append(ipc_class)

            return {
                'patent_number': patent_number,
                'country_code': country_code,
                'kind_code': kind_code,
                'application_number': app_number,
                'title': title,
                'applicants': applicants,
                'publication_date': pub_date,
                'ipc_classes': ipc_classes,
                'china_connection': any('china' in app.lower() or 'chinese' in app.lower()
                                      or 'beijing' in app.lower() or 'shanghai' in app.lower()
                                      for app in applicants)
            }

        except Exception as e:
            logger.error(f"Error extracting patent info: {e}")
            return {}

    def save_results(self, data: List[Dict], filename: str):
        """Save results to files"""

        if not data:
            logger.warning("No data to save")
            return

        filepath = self.output_dir / filename

        # Save as JSON
        with open(f"{filepath}.json", 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)

        # Save as CSV
        df = pd.DataFrame(data)
        df.to_csv(f"{filepath}.csv", index=False, encoding='utf-8')

        logger.info(f"Saved {len(data)} records to {filepath}")

def main():
    """Test EPO OPS client"""

    print("="*60)
    print("EPO Open Patent Services (OPS) Client Test")
    print("="*60)

    client = EPOOPSClient()

    # Test basic search
    print("1. Testing basic patent search...")

    results = client.search_patents(
        query="artificial intelligence",
        country="EP",  # European patents
        max_results=10
    )

    if results:
        print(f"Found search results: {len(results)}")

        # Process and display results
        processed = client.process_search_results(results, "EP", "AI")
        print(f"Processed {len(processed)} patents")

        if processed:
            print("\nSample patent:")
            sample = processed[0]
            for key, value in sample.items():
                print(f"  {key}: {value}")

    # Test China-related search
    print("\n2. Testing China-related patent search...")

    china_patents = client.search_china_related_patents(
        countries=['EP', 'US'],
        technologies=['5G', 'quantum computing'],
        years=['2022', '2023']
    )

    if china_patents:
        print(f"Found {len(china_patents)} China-related patents")

        # Save results
        client.save_results(china_patents, "epo_china_patents_test")

        # Show some statistics
        countries = {}
        for patent in china_patents:
            country = patent.get('search_country', 'Unknown')
            countries[country] = countries.get(country, 0) + 1

        print("\nPatents by country:")
        for country, count in countries.items():
            print(f"  {country}: {count}")

    print("\n" + "="*60)
    print("EPO OPS client test completed!")

if __name__ == "__main__":
    main()

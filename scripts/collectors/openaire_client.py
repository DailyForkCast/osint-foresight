#!/usr/bin/env python3
"""
OpenAIRE Client for OSINT Research Data Collection

Connects to OpenAIRE Graph API to collect European research data
for technology assessment and collaboration analysis.
"""

import os
import json
import time
import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpenAIREClient:
    """Client for accessing OpenAIRE Graph API"""

    def __init__(self, output_dir: str = None):
        """Initialize OpenAIRE client

        Args:
            output_dir: Directory to save collected data
        """
        self.base_url = "https://api.openaire.eu/search"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'OSINT-Research-System/1.0',
            'Accept': 'application/json'
        })

        # Setup output directory
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            self.output_dir = Path("C:/Projects/OSINT - Foresight/data/collected/openaire")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 0.5  # 500ms between requests

    def _rate_limit(self):
        """Enforce rate limiting between requests"""
        now = time.time()
        elapsed = now - self.last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)
        self.last_request_time = time.time()

    def search_research_products(self,
                               country: str = None,
                               keywords: str = None,
                               author: str = None,
                               title: str = None,
                               funder: str = None,
                               project_id: str = None,
                               from_date: str = None,
                               to_date: str = None,
                               size: int = 50,
                               page: int = 1,
                               result_type: str = None) -> Dict:
        """Search research products with filters

        Args:
            country: Two-letter country code (IT, DE, SK, etc.)
            keywords: Keywords to search for
            author: Author name
            title: Title search
            funder: Funding organization
            project_id: Project identifier
            from_date: Start date (YYYY-MM-DD)
            to_date: End date (YYYY-MM-DD)
            size: Results per page (max 50)
            page: Page number
            result_type: Type filter (publication, dataset, software)

        Returns:
            JSON response from API
        """
        self._rate_limit()

        params = {
            'format': 'json',
            'size': min(size, 50),  # API limit
            'page': page
        }

        # Add filters
        if country:
            params['country'] = country.upper()
        if keywords:
            params['keywords'] = keywords
        if author:
            params['author'] = author
        if title:
            params['title'] = title
        if funder:
            params['funder'] = funder
        if project_id:
            params['projectID'] = project_id
        if from_date:
            params['fromDateAccepted'] = from_date
        if to_date:
            params['toDateAccepted'] = to_date

        url = f"{self.base_url}/researchProducts"

        try:
            logger.debug(f"Requesting: {url} with params: {params}")
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode failed: {e}")
            return {}

    def search_projects(self,
                       country: str = None,
                       funder: str = None,
                       keywords: str = None,
                       size: int = 50,
                       page: int = 1) -> Dict:
        """Search research projects

        Args:
            country: Country code
            funder: Funding organization
            keywords: Keywords
            size: Results per page
            page: Page number

        Returns:
            JSON response from API
        """
        self._rate_limit()

        params = {
            'format': 'json',
            'size': min(size, 50),
            'page': page
        }

        if country:
            params['country'] = country.upper()
        if funder:
            params['funder'] = funder
        if keywords:
            params['keywords'] = keywords

        url = f"{self.base_url}/projects"

        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Project search failed: {e}")
            return {}

    def get_country_research_overview(self, country: str) -> Dict:
        """Get high-level research overview for a country

        Args:
            country: Two-letter country code

        Returns:
            Dictionary with research statistics
        """
        logger.info(f"Getting research overview for {country}")

        # Get total count
        data = self.search_research_products(country=country, size=1)
        total = 0
        if data.get('response', {}).get('header', {}).get('total'):
            total = int(data['response']['header']['total']['$'])

        # Get recent publications (last year)
        from_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        recent_data = self.search_research_products(
            country=country,
            from_date=from_date,
            size=1
        )
        recent_count = 0
        if recent_data.get('response', {}).get('header', {}).get('total'):
            recent_count = int(recent_data['response']['header']['total']['$'])

        return {
            'country': country,
            'total_research_products': total,
            'recent_publications': recent_count,
            'last_updated': datetime.now().isoformat()
        }

    def collect_country_research(self,
                               country: str,
                               max_results: int = 1000,
                               keywords: List[str] = None,
                               from_date: str = None) -> List[Dict]:
        """Collect comprehensive research data for a country

        Args:
            country: Country code
            max_results: Maximum number of results to collect
            keywords: Optional keyword filters
            from_date: Optional start date filter

        Returns:
            List of research product records
        """
        logger.info(f"Collecting research data for {country} (max: {max_results})")

        all_results = []
        page = 1
        size = 50

        while len(all_results) < max_results:
            logger.info(f"Fetching page {page} for {country}... ({len(all_results)} collected)")

            # If keywords provided, search for each
            if keywords:
                for keyword in keywords:
                    data = self.search_research_products(
                        country=country,
                        keywords=keyword,
                        from_date=from_date,
                        size=size,
                        page=page
                    )
                    if data.get('response', {}).get('results', {}).get('result'):
                        results = data['response']['results']['result']
                        if not isinstance(results, list):
                            results = [results]
                        all_results.extend(results)
            else:
                # Get all research for country
                data = self.search_research_products(
                    country=country,
                    from_date=from_date,
                    size=size,
                    page=page
                )
                if not data.get('response', {}).get('results', {}).get('result'):
                    break

                results = data['response']['results']['result']
                if not isinstance(results, list):
                    results = [results]
                all_results.extend(results)

                # Check if we've reached the end
                total = int(data['response']['header']['total']['$'])
                if len(all_results) >= total:
                    break

            page += 1

            # Prevent infinite loops
            if page > 200:  # 10,000 results max (50 * 200)
                logger.warning(f"Reached page limit for {country}")
                break

        logger.info(f"Collected {len(all_results)} research products for {country}")
        return all_results[:max_results]

    def extract_collaboration_data(self, research_data: List[Dict]) -> pd.DataFrame:
        """Extract international collaboration patterns from research data

        Args:
            research_data: List of research product records

        Returns:
            DataFrame with collaboration information
        """
        logger.info(f"Extracting collaborations from {len(research_data)} records")

        collaborations = []

        for item in research_data:
            try:
                result = item['metadata']['oaf:entity']['oaf:result']

                # Extract basic info
                title = result.get('title', {}).get('$', '')
                date = result.get('dateofacceptance', {}).get('$', '')
                result_type = result.get('resulttype', {}).get('@classid', '')

                # Extract DOI if available
                doi = None
                if 'pid' in result:
                    pids = result['pid'] if isinstance(result['pid'], list) else [result['pid']]
                    for pid in pids:
                        if pid.get('@classid') == 'doi':
                            doi = pid.get('$')
                            break

                # Extract organization relationships
                countries = set()
                organizations = []

                if 'rels' in result and 'rel' in result['rels']:
                    rels = result['rels']['rel']
                    if not isinstance(rels, list):
                        rels = [rels]

                    for rel in rels:
                        if rel.get('to', {}).get('@type') == 'organization':
                            country = rel.get('country', {}).get('@classid', '')
                            org_name = rel.get('legalname', {}).get('$', '')

                            if country:
                                countries.add(country)
                                organizations.append({
                                    'country': country,
                                    'organization': org_name
                                })

                # If multiple countries, it's a collaboration
                if len(countries) > 1:
                    collaborations.append({
                        'title': title,
                        'date': date,
                        'result_type': result_type,
                        'doi': doi,
                        'countries': list(countries),
                        'num_countries': len(countries),
                        'organizations': organizations,
                        'is_international': True
                    })
                elif len(countries) == 1:
                    # Still record single-country research
                    collaborations.append({
                        'title': title,
                        'date': date,
                        'result_type': result_type,
                        'doi': doi,
                        'countries': list(countries),
                        'num_countries': 1,
                        'organizations': organizations,
                        'is_international': False
                    })

            except Exception as e:
                logger.debug(f"Error processing record: {e}")
                continue

        df = pd.DataFrame(collaborations)
        logger.info(f"Extracted {len(df)} research records with collaboration data")

        return df

    def analyze_china_collaborations(self, country: str, max_results: int = 500) -> pd.DataFrame:
        """Analyze collaborations between target country and China

        Args:
            country: Target country code (IT, DE, SK, etc.)
            max_results: Maximum results to analyze

        Returns:
            DataFrame with China collaboration analysis
        """
        logger.info(f"Analyzing {country}-China research collaborations")

        # Collect recent research data
        from_date = "2020-01-01"  # Last 5 years
        research_data = self.collect_country_research(
            country=country,
            max_results=max_results,
            from_date=from_date
        )

        # Extract collaboration patterns
        collaborations = self.extract_collaboration_data(research_data)

        # Filter for China collaborations
        china_collabs = collaborations[
            collaborations['countries'].apply(lambda x: 'CN' in x)
        ].copy()

        # Add analysis fields
        china_collabs['primary_country'] = country
        china_collabs['collaboration_type'] = china_collabs.apply(
            lambda x: f"{country}-CN" if x['num_countries'] == 2 else f"{country}-CN-Multi",
            axis=1
        )

        # Extract year for trend analysis
        china_collabs['year'] = pd.to_datetime(china_collabs['date'], errors='coerce').dt.year

        logger.info(f"Found {len(china_collabs)} {country}-China collaborations")

        return china_collabs

    def save_data(self, data: pd.DataFrame, filename: str):
        """Save collected data to file

        Args:
            data: DataFrame to save
            filename: Output filename
        """
        filepath = self.output_dir / filename

        # Save as both CSV and JSON
        data.to_csv(f"{filepath}.csv", index=False)

        # Convert to JSON-serializable format
        json_data = data.to_dict('records')
        with open(f"{filepath}.json", 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False, default=str)

        logger.info(f"Saved data to {filepath}.csv and {filepath}.json")

def main():
    """Main function for testing OpenAIRE client"""
    print("="*60)
    print("OpenAIRE Client Test")
    print("="*60)

    client = OpenAIREClient()

    # Test 1: Get Italy overview
    print("\n1. Getting Italy research overview...")
    italy_overview = client.get_country_research_overview('IT')
    print(f"Italy total research products: {italy_overview['total_research_products']:,}")
    print(f"Recent publications (last year): {italy_overview['recent_publications']:,}")

    # Test 2: Search for Italy-China collaborations
    print("\n2. Analyzing Italy-China research collaborations...")
    china_collabs = client.analyze_china_collaborations('IT', max_results=100)

    if not china_collabs.empty:
        print(f"Found {len(china_collabs)} Italy-China collaborations")
        print(f"Years covered: {china_collabs['year'].min()}-{china_collabs['year'].max()}")

        # Show research types
        type_counts = china_collabs['result_type'].value_counts()
        print("\nResearch types:")
        for rtype, count in type_counts.items():
            print(f"  {rtype}: {count}")

        # Save results
        client.save_data(china_collabs, "italy_china_collaborations")

    # Test 3: Get sample research data
    print("\n3. Getting sample Italian research...")
    sample_research = client.collect_country_research('IT', max_results=50)

    if sample_research:
        print(f"Collected {len(sample_research)} research records")

        # Extract basic info
        titles = []
        for record in sample_research[:5]:
            try:
                title = record['metadata']['oaf:entity']['oaf:result']['title']['$']
                titles.append(title)
            except:
                continue

        print("\nSample titles:")
        for i, title in enumerate(titles, 1):
            print(f"  {i}. {title[:80]}...")

    print("\n" + "="*60)
    print("OpenAIRE client test completed!")
    print(f"Data saved to: {client.output_dir}")

if __name__ == "__main__":
    main()

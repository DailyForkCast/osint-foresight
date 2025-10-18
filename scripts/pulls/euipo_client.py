"""EUIPO (European Union Intellectual Property Office) Client

Access European trademark and design data for Italian technology companies.
EUIPO provides free access to EU trademark data through various APIs.

Documentation: https://euipo.europa.eu/ohimportal/en/web/observatory/open-data
"""

import os
import json
import time
import requests
import pandas as pd
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import xml.etree.ElementTree as ET

class EUIPOClient:
    """Client for EUIPO trademark and design searches"""

    def __init__(self):
        """Initialize EUIPO client"""
        # EUIPO APIs (no authentication required for basic access)
        self.tm_view_url = "https://www.tmdn.org/tmview/api"  # TMview API (may be unreliable)
        self.euipo_search_url = "https://euipo.europa.eu/eSearch"  # eSearch Web Interface
        self.open_data_url = "https://data.euipo.europa.eu/api/v1"  # Open Data Portal
        # Alternative: Use the web search interface
        self.web_search_url = "https://euipo.europa.eu/eSearch/api"

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'OSINT-Italy-Research/1.0',
            'Accept': 'application/json, application/xml'
        })

        # Rate limiting
        self.last_request = 0
        self.min_interval = 1.0  # 1 second between requests

        print("EUIPO client initialized (no API key required)")

    def _rate_limit(self):
        """Enforce rate limiting"""
        now = time.time()
        elapsed = now - self.last_request
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_request = time.time()

    def search_by_owner(self,
                       owner_name: str,
                       country_code: str = "IT",
                       limit: int = 100) -> pd.DataFrame:
        """Search EU trademarks by owner name

        Args:
            owner_name: Company/owner name
            country_code: Country code (default IT for Italy)
            limit: Maximum results

        Returns:
            DataFrame with trademark results
        """
        self._rate_limit()

        # TMview search endpoint
        url = f"{self.tm_view_url}/search"

        params = {
            'applicant': owner_name,
            'country': country_code,
            'pageSize': min(limit, 500),
            'page': 1,
            'sort': 'applicationDate:desc'
        }

        try:
            response = self.session.get(url, params=params, timeout=30)

            if response.status_code == 200:
                data = response.json()
                if 'results' in data:
                    df = pd.DataFrame(data['results'])
                    print(f"Found {len(df)} EU trademarks for {owner_name}")
                    return df
                else:
                    print(f"No results found for {owner_name}")
                    return pd.DataFrame()
            else:
                print(f"Error {response.status_code}: {response.text[:200]}")
                return pd.DataFrame()

        except Exception as e:
            print(f"Search failed: {e}")
            return pd.DataFrame()

    def search_italian_companies(self, companies: List[str] = None) -> pd.DataFrame:
        """Search EU trademarks for Italian technology companies

        Args:
            companies: List of company names (uses defaults if None)

        Returns:
            DataFrame with all trademark results
        """
        if companies is None:
            # Major Italian technology companies
            companies = [
                "Leonardo",
                "Leonardo S.p.A.",
                "Finmeccanica",  # Leonardo's former name
                "Fincantieri",
                "STMicroelectronics",
                "Thales Alenia Space Italia",
                "Telespazio",
                "Ansaldo Energia",
                "Pirelli",
                "Iveco",
                "Magneti Marelli",
                "Datalogic",
                "Engineering Ingegneria Informatica"
            ]

        all_results = []

        for company in companies:
            print(f"\nSearching EU trademarks for: {company}")
            results = self.search_by_owner(company, country_code="IT", limit=50)

            if not results.empty:
                results['search_company'] = company
                results['search_date'] = datetime.now().isoformat()
                all_results.append(results)

            # Rate limiting between searches
            time.sleep(2)

        if all_results:
            combined_df = pd.concat(all_results, ignore_index=True)
            print(f"\nTotal EU trademarks found: {len(combined_df)}")
            return combined_df
        else:
            print("\nNo EU trademarks found")
            return pd.DataFrame()

    def search_by_nice_class(self,
                            nice_classes: List[int],
                            country: str = "IT",
                            limit: int = 100) -> pd.DataFrame:
        """Search trademarks by Nice Classification

        Args:
            nice_classes: List of Nice class numbers (1-45)
            country: Country code
            limit: Maximum results

        Returns:
            DataFrame with trademark results
        """
        self._rate_limit()

        # Technology-related Nice classes:
        # Class 9: Scientific apparatus, computers, software
        # Class 35: Business management, data processing
        # Class 38: Telecommunications
        # Class 42: Scientific and technological services

        url = f"{self.tm_view_url}/search"

        params = {
            'niceClass': ','.join(str(c) for c in nice_classes),
            'country': country,
            'pageSize': min(limit, 500),
            'page': 1
        }

        try:
            response = self.session.get(url, params=params, timeout=30)

            if response.status_code == 200:
                data = response.json()
                if 'results' in data:
                    return pd.DataFrame(data['results'])
            return pd.DataFrame()

        except Exception as e:
            print(f"Search by Nice class failed: {e}")
            return pd.DataFrame()

    def analyze_portfolio(self, trademarks_df: pd.DataFrame) -> Dict:
        """Analyze EU trademark portfolio

        Args:
            trademarks_df: DataFrame with trademark data

        Returns:
            Dictionary with portfolio analysis
        """
        if trademarks_df.empty:
            return {}

        analysis = {
            'total_trademarks': len(trademarks_df),
            'companies': {},
            'nice_classes': {},
            'status_distribution': {},
            'filing_trends': {},
            'geographic_coverage': {}
        }

        # Companies
        if 'search_company' in trademarks_df:
            company_counts = trademarks_df['search_company'].value_counts()
            analysis['companies'] = company_counts.to_dict()

        # Nice classes
        if 'niceClasses' in trademarks_df:
            class_counts = {}
            for classes in trademarks_df['niceClasses'].dropna():
                if isinstance(classes, list):
                    for cls in classes:
                        class_counts[str(cls)] = class_counts.get(str(cls), 0) + 1
                else:
                    for cls in str(classes).split(','):
                        cls = cls.strip()
                        if cls:
                            class_counts[cls] = class_counts.get(cls, 0) + 1

            analysis['nice_classes'] = dict(
                sorted(class_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            )

        # Status
        if 'status' in trademarks_df:
            status_counts = trademarks_df['status'].value_counts()
            analysis['status_distribution'] = status_counts.to_dict()

        # Filing trends
        if 'applicationDate' in trademarks_df:
            trademarks_df['filing_year'] = pd.to_datetime(
                trademarks_df['applicationDate'], errors='coerce'
            ).dt.year

            year_counts = trademarks_df['filing_year'].value_counts().sort_index()
            analysis['filing_trends'] = year_counts.to_dict()

        # Geographic coverage
        if 'territory' in trademarks_df:
            territory_counts = trademarks_df['territory'].value_counts()
            analysis['geographic_coverage'] = territory_counts.head(10).to_dict()

        return analysis

    def find_technology_trademarks(self, trademarks_df: pd.DataFrame) -> pd.DataFrame:
        """Filter technology-related trademarks

        Args:
            trademarks_df: DataFrame with trademark data

        Returns:
            DataFrame with technology trademarks
        """
        # Technology-related Nice classes
        tech_classes = [9, 35, 38, 42, 45]  # Core technology classes

        if 'niceClasses' in trademarks_df:
            def has_tech_class(classes):
                if pd.isna(classes):
                    return False
                if isinstance(classes, list):
                    return any(c in tech_classes for c in classes)
                else:
                    class_list = [int(c.strip()) for c in str(classes).split(',') if c.strip().isdigit()]
                    return any(c in tech_classes for c in class_list)

            tech_mask = trademarks_df['niceClasses'].apply(has_tech_class)
            return trademarks_df[tech_mask]
        else:
            return trademarks_df

    def save_results(self,
                    df: pd.DataFrame,
                    filename: str,
                    analysis: Dict = None):
        """Save search results

        Args:
            df: DataFrame to save
            filename: Base filename
            analysis: Optional analysis
        """
        output_dir = Path("C:/Projects/OSINT - Foresight/data/collected/euipo")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save data
        csv_path = output_dir / f"{filename}.csv"
        df.to_csv(csv_path, index=False)
        print(f"Saved {len(df)} trademarks to {csv_path}")

        # Save analysis
        if analysis:
            json_path = output_dir / f"{filename}_analysis.json"
            with open(json_path, 'w') as f:
                json.dump(analysis, f, indent=2, default=str)
            print(f"Saved analysis to {json_path}")

def test_euipo():
    """Test EUIPO client"""
    print("="*60)
    print("EUIPO (EU Intellectual Property Office) Test")
    print("="*60)

    client = EUIPOClient()

    print("\n1. Testing search for Italian technology companies...")

    # Test with key Italian tech companies
    test_companies = [
        "Leonardo",
        "STMicroelectronics",
        "Fincantieri"
    ]

    results = client.search_italian_companies(test_companies)

    if not results.empty:
        # Analyze portfolio
        print("\n2. Analyzing EU trademark portfolio...")
        analysis = client.analyze_portfolio(results)

        if analysis:
            print(f"\nPortfolio Summary:")
            print(f"  Total trademarks: {analysis['total_trademarks']}")

            if analysis.get('companies'):
                print(f"\n  Trademarks by company:")
                for company, count in analysis['companies'].items():
                    print(f"    {company}: {count}")

            if analysis.get('nice_classes'):
                print(f"\n  Top Nice classes:")
                for cls, count in list(analysis['nice_classes'].items())[:5]:
                    nice_descriptions = {
                        '9': 'Scientific/Computing',
                        '35': 'Business Services',
                        '38': 'Telecommunications',
                        '42': 'Technology Services',
                        '12': 'Vehicles',
                        '7': 'Machinery'
                    }
                    desc = nice_descriptions.get(cls, 'Other')
                    print(f"    Class {cls} ({desc}): {count}")

        # Filter technology trademarks
        print("\n3. Filtering technology-related trademarks...")
        tech_marks = client.find_technology_trademarks(results)
        print(f"  Found {len(tech_marks)} technology-related trademarks")
        print(f"  Percentage: {len(tech_marks)/len(results)*100:.1f}%")

        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        client.save_results(
            results,
            f"italian_eu_trademarks_{timestamp}",
            analysis
        )
    else:
        print("\nNo results found. Checking alternative endpoints...")

        # Try searching by Nice class
        print("\n4. Testing search by Nice class (Class 9 - Technology)...")
        tech_results = client.search_by_nice_class([9], country="IT", limit=10)

        if not tech_results.empty:
            print(f"  Found {len(tech_results)} Italian technology trademarks")

    print("\n" + "="*60)
    print("Note: EUIPO provides comprehensive EU trademark data")
    print("This is more relevant for Italian companies than USPTO")
    print("="*60)

if __name__ == "__main__":
    test_euipo()

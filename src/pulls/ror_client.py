#!/usr/bin/env python3
"""
ROR (Research Organization Registry) Client
For institutional normalization and standardized org_ror joins
Priority MCF Dataset Integration - Week 1
"""

import json
import requests
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import zipfile
import io

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RORClient:
    """
    Client for Research Organization Registry data
    Provides standardized institutional identifiers
    """

    def __init__(self, cache_dir: str = "data/collected/ror"):
        self.base_url = "https://api.ror.org"
        self.data_dump_url = "https://zenodo.org/api/records/?communities=ror-data&sort=mostrecent"
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Current data version
        self.current_version = None
        self.organizations = {}

        # Load cached data if available
        self.load_cached_data()

    def download_latest_dump(self) -> bool:
        """
        Download latest ROR data dump from Zenodo
        Monthly releases provide complete institutional data
        """
        try:
            # Get latest release info
            response = requests.get(self.data_dump_url)
            response.raise_for_status()

            records = response.json()
            if not records.get('hits', {}).get('hits'):
                logger.error("No ROR data releases found")
                return False

            latest = records['hits']['hits'][0]
            version = latest['metadata']['version']

            # Check if we already have this version
            if version == self.current_version:
                logger.info(f"Already have latest ROR version: {version}")
                return True

            # Find JSON dump file
            json_file = None
            for file in latest['files']:
                if file['key'].endswith('.json.zip'):
                    json_file = file
                    break

            if not json_file:
                logger.error("No JSON dump found in latest release")
                return False

            # Download the file
            logger.info(f"Downloading ROR v{version} ({json_file['size'] / 1024 / 1024:.1f} MB)...")
            dump_response = requests.get(json_file['links']['self'], stream=True)
            dump_response.raise_for_status()

            # Extract and save
            with zipfile.ZipFile(io.BytesIO(dump_response.content)) as zf:
                # Find the JSON file in the archive
                json_filename = [f for f in zf.namelist() if f.endswith('.json')][0]

                # Extract to cache directory
                output_path = self.cache_dir / f"ror_v{version}.json"
                with zf.open(json_filename) as source, open(output_path, 'wb') as target:
                    target.write(source.read())

            # Update version info
            self.current_version = version
            version_file = self.cache_dir / "version.txt"
            version_file.write_text(version)

            logger.info(f"Successfully downloaded ROR v{version}")
            return True

        except Exception as e:
            logger.error(f"Failed to download ROR data: {e}")
            return False

    def load_cached_data(self) -> bool:
        """Load cached ROR data if available"""
        try:
            version_file = self.cache_dir / "version.txt"
            if version_file.exists():
                self.current_version = version_file.read_text().strip()

                data_file = self.cache_dir / f"ror_v{self.current_version}.json"
                if data_file.exists():
                    with open(data_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    # Index organizations by ROR ID
                    for org in data:
                        ror_id = org['id'].split('/')[-1]  # Extract ID from URL
                        self.organizations[ror_id] = org

                    logger.info(f"Loaded {len(self.organizations)} organizations from cache")
                    return True

        except Exception as e:
            logger.warning(f"Could not load cached data: {e}")

        return False

    def search_organization(self, name: str, country: str = None) -> List[Dict[str, Any]]:
        """
        Search for organizations by name and optionally country
        Uses local data for fast lookups
        """
        if not self.organizations:
            # Try to download if we don't have data
            if not self.download_latest_dump():
                # Fall back to API
                return self._search_via_api(name, country)

        results = []
        name_lower = name.lower()

        for ror_id, org in self.organizations.items():
            # Check name matches (including aliases)
            names_to_check = [org.get('name', '').lower()]
            names_to_check.extend([alias.lower() for alias in org.get('aliases', [])])
            names_to_check.extend([label.get('label', '').lower()
                                   for label in org.get('labels', [])])

            if any(name_lower in check_name or check_name in name_lower
                   for check_name in names_to_check):

                # Apply country filter if specified
                if country:
                    org_country = org.get('country', {}).get('country_code', '')
                    if country.upper() != org_country:
                        continue

                results.append({
                    'ror_id': ror_id,
                    'name': org.get('name'),
                    'country': org.get('country', {}).get('country_name'),
                    'country_code': org.get('country', {}).get('country_code'),
                    'types': org.get('types', []),
                    'established': org.get('established'),
                    'grid_id': self._extract_grid_id(org),
                    'confidence': self._calculate_match_confidence(name, org)
                })

        # Sort by confidence
        results.sort(key=lambda x: x['confidence'], reverse=True)
        return results[:10]  # Return top 10 matches

    def _search_via_api(self, name: str, country: str = None) -> List[Dict[str, Any]]:
        """Fallback to API search if local data not available"""
        try:
            params = {'query': name}
            if country:
                params['filter'] = f'country.country_code:{country}'

            response = requests.get(f"{self.base_url}/organizations", params=params)
            response.raise_for_status()

            results = []
            for item in response.json().get('items', []):
                results.append({
                    'ror_id': item['id'].split('/')[-1],
                    'name': item['name'],
                    'country': item.get('country', {}).get('country_name'),
                    'country_code': item.get('country', {}).get('country_code'),
                    'types': item.get('types', []),
                    'confidence': item.get('score', 0)
                })

            return results

        except Exception as e:
            logger.error(f"API search failed: {e}")
            return []

    def get_organization(self, ror_id: str) -> Optional[Dict[str, Any]]:
        """Get full organization details by ROR ID"""

        # Clean the ID (remove URL prefix if present)
        if '/' in ror_id:
            ror_id = ror_id.split('/')[-1]

        # Check local cache first
        if ror_id in self.organizations:
            return self.organizations[ror_id]

        # Fall back to API
        try:
            response = requests.get(f"{self.base_url}/organizations/{ror_id}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get organization {ror_id}: {e}")
            return None

    def normalize_institutions(self, institution_list: List[str]) -> Dict[str, Any]:
        """
        Normalize a list of institution names to ROR IDs
        Critical for consistent joins across datasets
        """
        normalized = {
            'successful': [],
            'failed': [],
            'ambiguous': []
        }

        for institution in institution_list:
            results = self.search_organization(institution)

            if not results:
                normalized['failed'].append({
                    'original': institution,
                    'reason': 'No matches found'
                })
            elif len(results) == 1 or (results and results[0]['confidence'] > 0.9):
                # Clear match
                normalized['successful'].append({
                    'original': institution,
                    'ror_id': results[0]['ror_id'],
                    'normalized_name': results[0]['name'],
                    'country': results[0]['country_code'],
                    'confidence': results[0]['confidence']
                })
            else:
                # Multiple possible matches
                normalized['ambiguous'].append({
                    'original': institution,
                    'candidates': results[:3]  # Top 3 candidates
                })

        return normalized

    def _extract_grid_id(self, org: Dict) -> Optional[str]:
        """Extract GRID ID for backwards compatibility"""
        for ext_id in org.get('external_ids', {}).get('GRID', {}).get('all', []):
            if ext_id:
                return ext_id
        return None

    def _calculate_match_confidence(self, query: str, org: Dict) -> float:
        """Calculate confidence score for name match"""
        query_lower = query.lower()
        org_name_lower = org.get('name', '').lower()

        # Exact match
        if query_lower == org_name_lower:
            return 1.0

        # Contains match
        if query_lower in org_name_lower or org_name_lower in query_lower:
            return 0.8

        # Alias match
        for alias in org.get('aliases', []):
            if query_lower == alias.lower():
                return 0.9
            if query_lower in alias.lower() or alias.lower() in query_lower:
                return 0.7

        # Partial match
        return 0.5

    def build_country_index(self, country_code: str) -> Dict[str, List[str]]:
        """Build index of all organizations in a country"""
        if not self.organizations:
            self.download_latest_dump()
            self.load_cached_data()

        country_orgs = {
            'universities': [],
            'companies': [],
            'government': [],
            'facilities': [],
            'healthcare': [],
            'nonprofits': [],
            'archives': [],
            'other': []
        }

        for ror_id, org in self.organizations.items():
            if org.get('country', {}).get('country_code') == country_code.upper():
                org_types = org.get('types', [])

                categorized = False
                for org_type in org_types:
                    if org_type == 'Education':
                        country_orgs['universities'].append(ror_id)
                        categorized = True
                    elif org_type == 'Company':
                        country_orgs['companies'].append(ror_id)
                        categorized = True
                    elif org_type == 'Government':
                        country_orgs['government'].append(ror_id)
                        categorized = True
                    elif org_type == 'Facility':
                        country_orgs['facilities'].append(ror_id)
                        categorized = True
                    elif org_type == 'Healthcare':
                        country_orgs['healthcare'].append(ror_id)
                        categorized = True
                    elif org_type == 'Nonprofit':
                        country_orgs['nonprofits'].append(ror_id)
                        categorized = True
                    elif org_type == 'Archive':
                        country_orgs['archives'].append(ror_id)
                        categorized = True

                if not categorized:
                    country_orgs['other'].append(ror_id)

        return country_orgs

def demonstrate_ror_integration():
    """Demonstrate ROR integration capabilities"""

    print("="*70)
    print("ROR (Research Organization Registry) Integration")
    print("="*70)

    client = RORClient()

    # Download latest data
    print("\n1. Downloading latest ROR data dump...")
    if client.download_latest_dump():
        print(f"✓ Downloaded version: {client.current_version}")
        print(f"✓ Total organizations: {len(client.organizations)}")
    else:
        print("⚠ Using cached data or API fallback")

    # Test organization search
    print("\n2. Testing organization search...")
    test_institutions = [
        "Leonardo S.p.A.",
        "University of Rome La Sapienza",
        "Max Planck Society",
        "Chinese Academy of Sciences"
    ]

    for inst in test_institutions:
        results = client.search_organization(inst)
        if results:
            top = results[0]
            print(f"\n'{inst}' → {top['name']}")
            print(f"  ROR ID: {top['ror_id']}")
            print(f"  Country: {top['country']}")
            print(f"  Confidence: {top['confidence']:.2f}")

    # Test normalization
    print("\n3. Testing batch normalization...")
    institutions = [
        "MIT",
        "Cambridge University",
        "Tsinghua University",
        "CNRS",
        "Fraunhofer Society"
    ]

    normalized = client.normalize_institutions(institutions)

    print(f"\nNormalization Results:")
    print(f"  Successful: {len(normalized['successful'])}")
    print(f"  Failed: {len(normalized['failed'])}")
    print(f"  Ambiguous: {len(normalized['ambiguous'])}")

    for success in normalized['successful']:
        print(f"\n  ✓ {success['original']}")
        print(f"    → {success['normalized_name']} ({success['ror_id']})")

    # Build country index
    print("\n4. Building country index for Italy (IT)...")
    italy_index = client.build_country_index('IT')

    print(f"\nItalian Organizations by Type:")
    for org_type, ror_ids in italy_index.items():
        if ror_ids:
            print(f"  {org_type.capitalize()}: {len(ror_ids)}")

    return client

if __name__ == "__main__":
    demonstrate_ror_integration()

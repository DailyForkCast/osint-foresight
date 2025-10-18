#!/usr/bin/env python3
"""
Standards Bodies API Integration
IETF, W3C, 3GPP, ETSI for standards influence tracking
Priority MCF Dataset Integration - Week 1
"""

import json
import requests
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StandardsAPIsClient:
    """
    Unified client for standards bodies APIs
    Critical for tracking standards influence in MCF analysis
    """

    def __init__(self, cache_dir: str = "data/collected/standards"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # API endpoints
        self.apis = {
            'ietf': {
                'base_url': 'https://datatracker.ietf.org/api/v1',
                'rate_limit': 1.0  # seconds between requests
            },
            'etsi': {
                'base_url': 'https://ipr.etsi.org',
                'rate_limit': 2.0
            },
            '3gpp': {
                'base_url': 'https://www.3gpp.org/DynaReport',
                'rate_limit': 2.0
            },
            'w3c': {
                'github_api': 'https://api.github.com/orgs/w3c',
                'rate_limit': 1.0
            }
        }

        self.last_request_time = {}

    def _rate_limit(self, api_name: str):
        """Enforce rate limiting for API calls"""
        if api_name in self.last_request_time:
            elapsed = time.time() - self.last_request_time[api_name]
            wait_time = self.apis[api_name]['rate_limit'] - elapsed
            if wait_time > 0:
                time.sleep(wait_time)
        self.last_request_time[api_name] = time.time()

    # ===== IETF Integration =====
    def get_ietf_contributions(self, organization: str = None,
                               country: str = None,
                               since: datetime = None) -> Dict[str, Any]:
        """
        Get IETF contributions by organization or country
        Tracks standards influence through drafts and RFCs
        """
        self._rate_limit('ietf')

        results = {
            'drafts': [],
            'rfcs': [],
            'authors': set(),
            'working_groups': set(),
            'influence_metrics': {}
        }

        try:
            # Search for documents
            params = {}
            if since:
                params['time__gte'] = since.isoformat()

            # Get drafts
            drafts_url = f"{self.apis['ietf']['base_url']}/doc/document/"
            response = requests.get(drafts_url, params=params)
            response.raise_for_status()

            drafts_data = response.json()

            for draft in drafts_data.get('objects', []):
                # Check if matches organization/country
                if self._matches_criteria(draft, organization, country):
                    results['drafts'].append({
                        'name': draft.get('name'),
                        'title': draft.get('title'),
                        'date': draft.get('time'),
                        'authors': self._extract_ietf_authors(draft),
                        'working_group': draft.get('group', {}).get('acronym')
                    })

                    # Track unique authors and working groups
                    for author in draft.get('authors', []):
                        results['authors'].add(author.get('person', {}).get('name'))
                    if draft.get('group'):
                        results['working_groups'].add(draft['group'].get('acronym'))

            # Calculate influence metrics
            results['influence_metrics'] = self._calculate_ietf_influence(results)

        except Exception as e:
            logger.error(f"Failed to get IETF contributions: {e}")

        return results

    def _extract_ietf_authors(self, document: Dict) -> List[str]:
        """Extract author information from IETF document"""
        authors = []
        for author in document.get('authors', []):
            person = author.get('person', {})
            if person:
                authors.append({
                    'name': person.get('name'),
                    'email': author.get('email'),
                    'affiliation': author.get('affiliation')
                })
        return authors

    def _calculate_ietf_influence(self, contributions: Dict) -> Dict[str, Any]:
        """Calculate IETF influence metrics"""
        return {
            'draft_count': len(contributions['drafts']),
            'rfc_count': len(contributions['rfcs']),
            'unique_authors': len(contributions['authors']),
            'working_groups': len(contributions['working_groups']),
            'influence_score': self._compute_influence_score(contributions)
        }

    def _compute_influence_score(self, contributions: Dict) -> float:
        """
        Compute weighted influence score
        RFCs worth more than drafts, WG participation matters
        """
        score = 0.0
        score += len(contributions['rfcs']) * 5.0  # RFCs have high value
        score += len(contributions['drafts']) * 1.0  # Drafts have lower value
        score += len(contributions['working_groups']) * 2.0  # WG participation
        score += len(contributions['authors']) * 0.5  # Unique contributors

        return round(score, 2)

    # ===== ETSI IPR Database =====
    def get_etsi_sep_declarations(self, company: str = None,
                                  standard: str = None) -> Dict[str, Any]:
        """
        Get ETSI Standard Essential Patent (SEP) declarations
        Critical for understanding patent-standards leverage
        """
        results = {
            'declarations': [],
            'standards': set(),
            'companies': set(),
            'total_seps': 0
        }

        # Note: ETSI IPR database requires web scraping or manual download
        # This is a placeholder for the integration
        logger.info("ETSI IPR integration requires additional setup")

        # For now, return cached data if available
        cache_file = self.cache_dir / "etsi_seps_cache.json"
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                cached = json.load(f)
                if company:
                    cached = [d for d in cached if company.lower() in d.get('company', '').lower()]
                if standard:
                    cached = [d for d in cached if standard.lower() in d.get('standard', '').lower()]
                results['declarations'] = cached
                results['total_seps'] = len(cached)

        return results

    # ===== 3GPP Contributions =====
    def get_3gpp_contributions(self, company: str = None,
                               meeting: str = None) -> Dict[str, Any]:
        """
        Get 3GPP technical contributions
        Essential for 5G/6G standards influence tracking
        """
        results = {
            'contributions': [],
            'meetings': set(),
            'companies': set(),
            'work_items': set()
        }

        # 3GPP requires specific meeting codes or work item tracking
        # This would need enhanced implementation with proper 3GPP portal access
        logger.info("3GPP integration requires meeting-specific queries")

        return results

    # ===== W3C GitHub Activity =====
    def get_w3c_activity(self, organization: str = None,
                         since: datetime = None) -> Dict[str, Any]:
        """
        Track W3C standards participation through GitHub activity
        W3C uses GitHub for specifications development
        """
        self._rate_limit('w3c')

        results = {
            'repositories': [],
            'contributors': set(),
            'commits': 0,
            'issues': 0,
            'pull_requests': 0
        }

        try:
            # Get W3C repositories
            repos_url = f"{self.apis['w3c']['github_api']}/repos"
            params = {'per_page': 100, 'sort': 'updated'}

            response = requests.get(repos_url, params=params)
            response.raise_for_status()

            repos = response.json()

            for repo in repos[:20]:  # Analyze top 20 most active repos
                # Get contributors for each repo
                contrib_url = f"https://api.github.com/repos/w3c/{repo['name']}/contributors"
                self._rate_limit('w3c')

                contrib_response = requests.get(contrib_url, params={'per_page': 100})
                if contrib_response.status_code == 200:
                    contributors = contrib_response.json()

                    # Check if organization matches
                    if organization:
                        org_contributors = [c for c in contributors
                                          if organization.lower() in (c.get('company', '') or '').lower()]
                        if org_contributors:
                            results['repositories'].append({
                                'name': repo['name'],
                                'description': repo.get('description'),
                                'contributors_from_org': len(org_contributors),
                                'total_contributors': len(contributors)
                            })

                            for contrib in org_contributors:
                                results['contributors'].add(contrib.get('login'))

        except Exception as e:
            logger.error(f"Failed to get W3C activity: {e}")

        return results

    # ===== Cross-Standards Analysis =====
    def analyze_standards_influence(self, entity: str,
                                   entity_type: str = 'company') -> Dict[str, Any]:
        """
        Comprehensive standards influence analysis across all bodies
        This is the key MCF metric for standards dominance
        """
        influence_report = {
            'entity': entity,
            'entity_type': entity_type,
            'timestamp': datetime.now().isoformat(),
            'standards_bodies': {},
            'overall_influence_score': 0.0,
            'key_findings': [],
            'china_collaboration_indicators': []
        }

        # Check each standards body
        logger.info(f"Analyzing standards influence for {entity}...")

        # IETF contributions
        ietf_data = self.get_ietf_contributions(organization=entity)
        influence_report['standards_bodies']['ietf'] = {
            'contributions': ietf_data['draft_count'],
            'influence_score': ietf_data['influence_metrics']['influence_score']
        }

        # W3C activity
        w3c_data = self.get_w3c_activity(organization=entity)
        influence_report['standards_bodies']['w3c'] = {
            'repositories': len(w3c_data['repositories']),
            'contributors': len(w3c_data['contributors'])
        }

        # ETSI SEPs
        etsi_data = self.get_etsi_sep_declarations(company=entity)
        influence_report['standards_bodies']['etsi'] = {
            'sep_declarations': etsi_data['total_seps']
        }

        # Calculate overall influence
        influence_report['overall_influence_score'] = self._calculate_overall_influence(
            influence_report['standards_bodies']
        )

        # Identify key findings
        if influence_report['overall_influence_score'] > 50:
            influence_report['key_findings'].append(
                f"{entity} shows significant standards influence (score: {influence_report['overall_influence_score']})"
            )

        # Check for China collaboration patterns
        china_entities = ['huawei', 'zte', 'china mobile', 'china telecom', 'china unicom',
                         'baidu', 'alibaba', 'tencent', 'xiaomi', 'oppo', 'vivo']

        for chinese_entity in china_entities:
            # This would check for co-authorship, joint contributions, etc.
            # Placeholder for demonstration
            pass

        return influence_report

    def _calculate_overall_influence(self, bodies_data: Dict) -> float:
        """Calculate weighted overall influence score"""
        weights = {
            'ietf': 0.3,
            'etsi': 0.3,
            '3gpp': 0.25,
            'w3c': 0.15
        }

        total_score = 0.0

        for body, weight in weights.items():
            if body in bodies_data:
                body_score = 0.0
                if body == 'ietf':
                    body_score = bodies_data[body].get('influence_score', 0)
                elif body == 'etsi':
                    body_score = bodies_data[body].get('sep_declarations', 0) * 2
                elif body == 'w3c':
                    body_score = bodies_data[body].get('repositories', 0) * 3

                total_score += body_score * weight

        return round(total_score, 2)

    def _matches_criteria(self, document: Dict, organization: str, country: str) -> bool:
        """Check if document matches search criteria"""
        if not organization and not country:
            return True

        # Check organization match
        if organization:
            authors = document.get('authors', [])
            for author in authors:
                if organization.lower() in (author.get('affiliation', '') or '').lower():
                    return True

        # Check country match
        if country:
            # Would need to resolve author affiliations to countries
            # Placeholder for now
            pass

        return False

    def generate_standards_influence_index(self, countries: List[str]) -> Dict[str, Any]:
        """
        Generate Standards Influence Index for multiple countries
        Key MCF metric for technology dominance assessment
        """
        index = {
            'generated_at': datetime.now().isoformat(),
            'countries': {},
            'rankings': [],
            'china_collaboration_matrix': {}
        }

        for country in countries:
            logger.info(f"Analyzing standards influence for {country}...")

            # Aggregate influence across major organizations from country
            # This would query ROR for organizations, then check standards participation
            country_influence = {
                'ietf_score': 0,
                'etsi_score': 0,
                '3gpp_score': 0,
                'w3c_score': 0,
                'total_score': 0,
                'key_players': []
            }

            # Placeholder for country-level aggregation
            # Would integrate with ROR to get organizations by country
            # Then sum their standards contributions

            index['countries'][country] = country_influence

        # Generate rankings
        index['rankings'] = sorted(
            [(c, d['total_score']) for c, d in index['countries'].items()],
            key=lambda x: x[1],
            reverse=True
        )

        return index

def demonstrate_standards_integration():
    """Demonstrate standards API integration"""

    print("="*70)
    print("STANDARDS BODIES API INTEGRATION")
    print("="*70)

    client = StandardsAPIsClient()

    # Test IETF contributions
    print("\n1. Testing IETF Datatracker API...")
    ietf_data = client.get_ietf_contributions(
        organization="Huawei",
        since=datetime.now() - timedelta(days=365)
    )
    print(f"  Drafts found: {len(ietf_data['drafts'])}")
    print(f"  Unique authors: {len(ietf_data['authors'])}")
    print(f"  Working groups: {len(ietf_data['working_groups'])}")
    print(f"  Influence score: {ietf_data['influence_metrics'].get('influence_score', 0)}")

    # Test W3C activity
    print("\n2. Testing W3C GitHub tracking...")
    w3c_data = client.get_w3c_activity(organization="Microsoft")
    print(f"  Repositories with contributions: {len(w3c_data['repositories'])}")
    print(f"  Contributors tracked: {len(w3c_data['contributors'])}")

    # Test comprehensive influence analysis
    print("\n3. Running comprehensive standards influence analysis...")
    test_entities = ["Huawei", "Ericsson", "Nokia", "Samsung"]

    for entity in test_entities:
        influence = client.analyze_standards_influence(entity)
        print(f"\n{entity}:")
        print(f"  Overall influence score: {influence['overall_influence_score']}")
        for body, data in influence['standards_bodies'].items():
            print(f"  {body.upper()}: {data}")

    # Generate multi-country index
    print("\n4. Generating Standards Influence Index...")
    countries = ["US", "CN", "DE", "FR", "GB"]
    index = client.generate_standards_influence_index(countries)

    print(f"\nCountry Rankings by Standards Influence:")
    for rank, (country, score) in enumerate(index['rankings'], 1):
        print(f"  {rank}. {country}: {score}")

    return client

if __name__ == "__main__":
    demonstrate_standards_integration()

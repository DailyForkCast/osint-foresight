#!/usr/bin/env python3
"""
GitHub→Dependencies→Supply_Chain Fusion Pipeline
Maps organizational GitHub dependencies to supply chain vulnerabilities
"""

import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Set
from pathlib import Path
import requests
import time
import yaml
from dataclasses import dataclass, asdict
import hashlib
import base64

@dataclass
class GitHubOrganization:
    """GitHub organization data structure"""
    login: str
    name: str
    description: str
    public_repos: int
    created_at: datetime
    updated_at: datetime
    location: str
    org_ror: str

@dataclass
class Repository:
    """Repository data structure"""
    name: str
    full_name: str
    description: str
    language: str
    size: int
    stargazers_count: int
    forks_count: int
    created_at: datetime
    updated_at: datetime
    topics: List[str]
    license: str

@dataclass
class Dependency:
    """Dependency data structure"""
    name: str
    version: str
    ecosystem: str  # npm, pypi, maven, nuget, etc.
    scope: str  # direct, transitive
    license: str
    maintainers: List[str]
    download_count: int
    last_updated: datetime
    china_maintained: bool
    security_advisories: List[str]

@dataclass
class SupplyChainRisk:
    """Supply chain risk assessment"""
    repository: str
    dependency: Dependency
    risk_level: str  # low, medium, high, critical
    risk_factors: List[str]
    china_exposure: bool
    critical_path: bool
    mitigation_options: List[str]

class GitHubDependenciesSupplyPipeline:
    """Main fusion pipeline for GitHub→Dependencies→Supply_Chain analysis"""

    def __init__(self, config_path: str = None):
        """Initialize the GitHub dependencies pipeline"""
        if config_path is None:
            config_path = "C:/Projects/OSINT - Foresight/config/fusion_config.yaml"

        # Load configuration
        self.config = self._load_config(config_path)

        # GitHub API setup
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.github_headers = {
            'Authorization': f'token {self.github_token}' if self.github_token else '',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'OSINT-Foresight-Research/1.0'
        }

        # Data storage paths
        self.data_dir = Path("F:/fusion_data/github_dependencies_supply")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Package ecosystem APIs
        self.ecosystem_apis = {
            'npm': 'https://registry.npmjs.org',
            'pypi': 'https://pypi.org/pypi',
            'maven': 'https://search.maven.org/solrsearch/select',
            'nuget': 'https://api-v2v3search-0.nuget.org',
            'rubygems': 'https://rubygems.org/api/v1',
            'crates': 'https://crates.io/api/v1'
        }

        # Rate limiting
        self.last_github_request = 0
        self.github_rate_limit = 1  # 1 request per second

    def _load_config(self, config_path: str) -> Dict:
        """Load GitHub dependencies pipeline configuration"""
        default_config = {
            "github_search_terms": [
                "artificial intelligence", "machine learning", "defense", "aerospace",
                "quantum", "cybersecurity", "semiconductor", "surveillance"
            ],
            "critical_dependencies": [
                "tensorflow", "pytorch", "opencv", "numpy", "kubernetes", "docker",
                "openssl", "nginx", "apache", "postgresql", "mysql", "redis"
            ],
            "china_indicators": {
                "maintainer_patterns": [
                    "@baidu.com", "@alibaba.com", "@tencent.com", "@bytedance.com",
                    "@huawei.com", "@xiaomi.com", "@qq.com", "@163.com", "@sina.com"
                ],
                "location_patterns": [
                    "beijing", "shanghai", "shenzhen", "guangzhou", "hangzhou",
                    "china", "prc", "peoples republic"
                ],
                "org_patterns": [
                    "tsinghua", "peking university", "chinese academy"
                ]
            },
            "risk_thresholds": {
                "high_dependency_count": 1000,
                "china_maintained_threshold": 0.1,  # 10% of deps
                "critical_path_threshold": 0.05,  # 5% of critical deps
                "security_advisory_threshold": 5
            }
        }

        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                # Merge with defaults
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
        except FileNotFoundError:
            print(f"Config file not found at {config_path}, using defaults")
            return default_config

    def _rate_limit_github(self):
        """Enforce GitHub API rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_github_request
        if time_since_last < self.github_rate_limit:
            time.sleep(self.github_rate_limit - time_since_last)
        self.last_github_request = time.time()

    def discover_github_organizations(self, org_ror: str) -> List[GitHubOrganization]:
        """Discover GitHub organizations linked to a research organization"""

        # Load organization mapping from existing data
        org_mapping_path = f"F:/org_mappings/{org_ror}_github.json"

        organizations = []

        try:
            with open(org_mapping_path, 'r') as f:
                mapping_data = json.load(f)

            for github_org in mapping_data.get('github_organizations', []):
                org_data = self._get_github_organization(github_org)
                if org_data:
                    organizations.append(org_data)

        except FileNotFoundError:
            # Fallback: search for organizations using the org name
            print(f"No GitHub mapping found for {org_ror}, attempting search...")
            organizations = self._search_github_organizations(org_ror)

        return organizations

    def _get_github_organization(self, org_login: str) -> Optional[GitHubOrganization]:
        """Get GitHub organization details"""
        self._rate_limit_github()

        url = f"https://api.github.com/orgs/{org_login}"
        response = requests.get(url, headers=self.github_headers)

        if response.status_code == 200:
            data = response.json()
            return GitHubOrganization(
                login=data.get('login', ''),
                name=data.get('name', ''),
                description=data.get('description', ''),
                public_repos=data.get('public_repos', 0),
                created_at=datetime.fromisoformat(data.get('created_at', '2020-01-01T00:00:00Z').replace('Z', '+00:00')),
                updated_at=datetime.fromisoformat(data.get('updated_at', '2020-01-01T00:00:00Z').replace('Z', '+00:00')),
                location=data.get('location', ''),
                org_ror=''  # Will be filled by caller
            )
        else:
            print(f"Failed to get organization {org_login}: {response.status_code}")
            return None

    def _search_github_organizations(self, org_ror: str) -> List[GitHubOrganization]:
        """Search for GitHub organizations by name (fallback method)"""
        # This would implement search logic based on organization name
        # For now, return empty list as this requires complex matching
        return []

    def get_organization_repositories(self, github_org: GitHubOrganization) -> List[Repository]:
        """Get all repositories for a GitHub organization"""
        repositories = []
        page = 1
        per_page = 100

        while True:
            self._rate_limit_github()

            url = f"https://api.github.com/orgs/{github_org.login}/repos"
            params = {
                'type': 'all',
                'sort': 'updated',
                'per_page': per_page,
                'page': page
            }

            response = requests.get(url, headers=self.github_headers, params=params)

            if response.status_code != 200:
                print(f"Failed to get repositories for {github_org.login}: {response.status_code}")
                break

            repos_data = response.json()
            if not repos_data:
                break

            for repo_data in repos_data:
                repository = Repository(
                    name=repo_data.get('name', ''),
                    full_name=repo_data.get('full_name', ''),
                    description=repo_data.get('description', ''),
                    language=repo_data.get('language', ''),
                    size=repo_data.get('size', 0),
                    stargazers_count=repo_data.get('stargazers_count', 0),
                    forks_count=repo_data.get('forks_count', 0),
                    created_at=datetime.fromisoformat(repo_data.get('created_at', '2020-01-01T00:00:00Z').replace('Z', '+00:00')),
                    updated_at=datetime.fromisoformat(repo_data.get('updated_at', '2020-01-01T00:00:00Z').replace('Z', '+00:00')),
                    topics=repo_data.get('topics', []),
                    license=repo_data.get('license', {}).get('name', '') if repo_data.get('license') else ''
                )
                repositories.append(repository)

            page += 1

        return repositories

    def extract_dependencies(self, repository: Repository, include_transitive: bool = True) -> List[Dependency]:
        """Extract dependencies from a repository"""
        dependencies = []

        # Get repository content to find dependency files
        dependency_files = self._find_dependency_files(repository)

        for dep_file in dependency_files:
            file_dependencies = self._parse_dependency_file(repository, dep_file)
            dependencies.extend(file_dependencies)

        # Get transitive dependencies if requested
        if include_transitive and dependencies:
            transitive_deps = self._get_transitive_dependencies(dependencies)
            dependencies.extend(transitive_deps)

        return dependencies

    def _find_dependency_files(self, repository: Repository) -> List[Dict[str, str]]:
        """Find dependency manifest files in a repository"""
        self._rate_limit_github()

        # Common dependency files
        dependency_patterns = {
            'package.json': 'npm',
            'requirements.txt': 'pypi',
            'Pipfile': 'pypi',
            'setup.py': 'pypi',
            'pom.xml': 'maven',
            'build.gradle': 'gradle',
            'Gemfile': 'rubygems',
            'Cargo.toml': 'crates',
            'go.mod': 'go',
            'composer.json': 'composer'
        }

        found_files = []

        url = f"https://api.github.com/repos/{repository.full_name}/contents"
        response = requests.get(url, headers=self.github_headers)

        if response.status_code == 200:
            contents = response.json()
            for item in contents:
                if item['name'] in dependency_patterns:
                    found_files.append({
                        'name': item['name'],
                        'ecosystem': dependency_patterns[item['name']],
                        'download_url': item['download_url'],
                        'path': item['path']
                    })

        return found_files

    def _parse_dependency_file(self, repository: Repository, dep_file: Dict[str, str]) -> List[Dependency]:
        """Parse a dependency file to extract dependencies"""
        dependencies = []

        try:
            # Download the file content
            response = requests.get(dep_file['download_url'])
            if response.status_code != 200:
                return dependencies

            content = response.text
            ecosystem = dep_file['ecosystem']

            # Parse based on ecosystem
            if ecosystem == 'npm':
                dependencies = self._parse_npm_dependencies(content)
            elif ecosystem == 'pypi':
                dependencies = self._parse_python_dependencies(content, dep_file['name'])
            elif ecosystem == 'maven':
                dependencies = self._parse_maven_dependencies(content)
            # Add more parsers as needed

            # Enrich dependencies with metadata
            for dep in dependencies:
                dep = self._enrich_dependency_metadata(dep, ecosystem)

        except Exception as e:
            print(f"Error parsing {dep_file['name']} in {repository.full_name}: {e}")

        return dependencies

    def _parse_npm_dependencies(self, content: str) -> List[Dependency]:
        """Parse npm package.json dependencies"""
        dependencies = []

        try:
            package_data = json.loads(content)

            # Parse dependencies and devDependencies
            for dep_type in ['dependencies', 'devDependencies']:
                deps = package_data.get(dep_type, {})
                for name, version in deps.items():
                    dependency = Dependency(
                        name=name,
                        version=version,
                        ecosystem='npm',
                        scope='direct',
                        license='',
                        maintainers=[],
                        download_count=0,
                        last_updated=datetime.now(),
                        china_maintained=False,
                        security_advisories=[]
                    )
                    dependencies.append(dependency)

        except json.JSONDecodeError:
            pass

        return dependencies

    def _parse_python_dependencies(self, content: str, filename: str) -> List[Dependency]:
        """Parse Python dependencies from requirements.txt or setup.py"""
        dependencies = []

        if filename == 'requirements.txt':
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Simple parsing (can be enhanced)
                    name = line.split('==')[0].split('>=')[0].split('<=')[0].split('>')[0].split('<')[0].strip()
                    version = ''
                    if '==' in line:
                        version = line.split('==')[1].strip()

                    dependency = Dependency(
                        name=name,
                        version=version,
                        ecosystem='pypi',
                        scope='direct',
                        license='',
                        maintainers=[],
                        download_count=0,
                        last_updated=datetime.now(),
                        china_maintained=False,
                        security_advisories=[]
                    )
                    dependencies.append(dependency)

        return dependencies

    def _parse_maven_dependencies(self, content: str) -> List[Dependency]:
        """Parse Maven pom.xml dependencies"""
        # This would require XML parsing - simplified for example
        return []

    def _enrich_dependency_metadata(self, dependency: Dependency, ecosystem: str) -> Dependency:
        """Enrich dependency with metadata from package registries"""

        try:
            if ecosystem == 'npm':
                self._enrich_npm_dependency(dependency)
            elif ecosystem == 'pypi':
                self._enrich_pypi_dependency(dependency)
            # Add more enrichment methods

            # Check for China maintainers
            dependency.china_maintained = self._check_china_maintainers(dependency)

        except Exception as e:
            print(f"Error enriching dependency {dependency.name}: {e}")

        return dependency

    def _enrich_npm_dependency(self, dependency: Dependency):
        """Enrich npm dependency with registry data"""
        url = f"{self.ecosystem_apis['npm']}/{dependency.name}"

        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()

                # Extract maintainers
                maintainers = data.get('maintainers', [])
                dependency.maintainers = [m.get('email', '') for m in maintainers]

                # Extract license
                license_info = data.get('license', '')
                if isinstance(license_info, dict):
                    dependency.license = license_info.get('type', '')
                else:
                    dependency.license = str(license_info)

                # Extract download stats (would need separate API call)
                dependency.download_count = 0  # Placeholder

                # Last update
                time_data = data.get('time', {})
                if 'modified' in time_data:
                    dependency.last_updated = datetime.fromisoformat(
                        time_data['modified'].replace('Z', '+00:00')
                    )

        except Exception as e:
            print(f"Failed to enrich npm package {dependency.name}: {e}")

    def _enrich_pypi_dependency(self, dependency: Dependency):
        """Enrich PyPI dependency with registry data"""
        url = f"{self.ecosystem_apis['pypi']}/{dependency.name}/json"

        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()

                # Extract maintainers
                maintainers = data.get('info', {}).get('maintainer_email', '')
                if maintainers:
                    dependency.maintainers = [maintainers]

                # Extract license
                dependency.license = data.get('info', {}).get('license', '')

                # Last update
                releases = data.get('releases', {})
                if dependency.version in releases:
                    upload_time = releases[dependency.version][0].get('upload_time', '')
                    if upload_time:
                        dependency.last_updated = datetime.fromisoformat(upload_time)

        except Exception as e:
            print(f"Failed to enrich PyPI package {dependency.name}: {e}")

    def _check_china_maintainers(self, dependency: Dependency) -> bool:
        """Check if dependency has Chinese maintainers"""
        china_indicators = self.config['china_indicators']

        # Check maintainer emails
        for maintainer in dependency.maintainers:
            for pattern in china_indicators['maintainer_patterns']:
                if pattern.lower() in maintainer.lower():
                    return True

        return False

    def _get_transitive_dependencies(self, direct_dependencies: List[Dependency]) -> List[Dependency]:
        """Get transitive dependencies (simplified implementation)"""
        # This would require recursive dependency resolution
        # For now, return empty list
        return []

    def assess_dependency_risk(self, dependency: Dependency) -> Dict[str, Any]:
        """Assess risk level of a dependency"""
        risk_factors = []
        risk_score = 0

        # China maintainer risk
        if dependency.china_maintained:
            risk_factors.append("china_maintained")
            risk_score += 3

        # License risk
        if not dependency.license or dependency.license.lower() in ['unknown', 'proprietary']:
            risk_factors.append("unclear_license")
            risk_score += 1

        # Age risk
        days_since_update = (datetime.now() - dependency.last_updated).days
        if days_since_update > 365:
            risk_factors.append("outdated_package")
            risk_score += 2

        # Security advisories
        if dependency.security_advisories:
            risk_factors.append("security_vulnerabilities")
            risk_score += len(dependency.security_advisories)

        # Determine risk level
        if risk_score >= 5:
            risk_level = "critical"
        elif risk_score >= 3:
            risk_level = "high"
        elif risk_score >= 1:
            risk_level = "medium"
        else:
            risk_level = "low"

        return {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "risk_factors": risk_factors,
            "mitigation_required": risk_score >= 3
        }

    def identify_supply_chain_bottlenecks(self, dependencies: Dict[str, List[Dependency]]) -> List[Dict[str, Any]]:
        """Identify critical supply chain bottlenecks"""
        bottlenecks = []

        # Count dependency usage across repositories
        dependency_usage = {}
        for repo, deps in dependencies.items():
            for dep in deps:
                key = f"{dep.ecosystem}:{dep.name}"
                if key not in dependency_usage:
                    dependency_usage[key] = {
                        'dependency': dep,
                        'used_in_repos': [],
                        'total_usage': 0
                    }
                dependency_usage[key]['used_in_repos'].append(repo)
                dependency_usage[key]['total_usage'] += 1

        # Identify high-usage dependencies
        threshold = max(1, len(dependencies) * 0.1)  # Used in >10% of repos

        for key, usage_data in dependency_usage.items():
            if usage_data['total_usage'] >= threshold:
                risk_assessment = self.assess_dependency_risk(usage_data['dependency'])

                if risk_assessment['risk_level'] in ['high', 'critical']:
                    bottlenecks.append({
                        'dependency': usage_data['dependency'],
                        'usage_count': usage_data['total_usage'],
                        'affected_repositories': usage_data['used_in_repos'],
                        'risk_assessment': risk_assessment,
                        'bottleneck_severity': 'critical' if usage_data['total_usage'] > len(dependencies) * 0.3 else 'high'
                    })

        return sorted(bottlenecks, key=lambda x: x['usage_count'], reverse=True)

    def run_pipeline(self, org_ror: str) -> Dict[str, Any]:
        """Execute the complete GitHub→Dependencies→Supply_Chain fusion pipeline"""

        print(f"Running GitHub→Dependencies→Supply_Chain pipeline for {org_ror}")

        # Stage 1: Discover GitHub organizations
        print("Stage 1: Discovering GitHub organizations...")
        github_orgs = self.discover_github_organizations(org_ror)

        if not github_orgs:
            return {"error": f"No GitHub organizations found for {org_ror}"}

        # Stage 2: Get repositories
        print("Stage 2: Collecting repositories...")
        all_repositories = []
        for org in github_orgs:
            repos = self.get_organization_repositories(org)
            all_repositories.extend(repos)

        # Stage 3: Extract dependencies
        print("Stage 3: Extracting dependencies...")
        dependencies = {}
        for repo in all_repositories:
            repo_deps = self.extract_dependencies(repo, include_transitive=True)
            if repo_deps:
                dependencies[repo.full_name] = repo_deps

        # Stage 4: Assess supply chain risks
        print("Stage 4: Assessing supply chain risks...")
        supply_risks = []
        china_maintained_count = 0
        total_deps = 0

        for repo_name, deps in dependencies.items():
            for dep in deps:
                total_deps += 1
                risk_assessment = self.assess_dependency_risk(dep)

                if dep.china_maintained:
                    china_maintained_count += 1

                if risk_assessment['risk_level'] in ['high', 'critical']:
                    supply_risks.append(SupplyChainRisk(
                        repository=repo_name,
                        dependency=dep,
                        risk_level=risk_assessment['risk_level'],
                        risk_factors=risk_assessment['risk_factors'],
                        china_exposure=dep.china_maintained,
                        critical_path=True,  # Would be calculated based on dependency graph
                        mitigation_options=[]  # Would be populated with specific recommendations
                    ))

        # Stage 5: Identify bottlenecks
        print("Stage 5: Identifying supply chain bottlenecks...")
        bottlenecks = self.identify_supply_chain_bottlenecks(dependencies)

        # Compile results
        results = {
            "pipeline": "github_dependencies_supply",
            "org_ror": org_ror,
            "github_organizations": [asdict(org) for org in github_orgs],
            "total_repositories": len(all_repositories),
            "total_dependencies": total_deps,
            "china_maintained_dependencies": china_maintained_count,
            "china_exposure_percentage": (china_maintained_count / total_deps * 100) if total_deps > 0 else 0,
            "high_risk_dependencies": len(supply_risks),
            "supply_chain_risks": [asdict(risk) for risk in supply_risks],
            "supply_chain_bottlenecks": bottlenecks,
            "generated_at": datetime.now().isoformat()
        }

        # Save results
        self.save_results(results, org_ror)

        return results

    def save_results(self, results: Dict[str, Any], org_ror: str):
        """Save pipeline results to file"""
        output_path = self.data_dir / f"{org_ror}_github_supply_chain.json"

        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)

        print(f"Results saved to {output_path}")

def main():
    """Main execution function"""
    pipeline = GitHubDependenciesSupplyPipeline()

    # Example usage
    test_org_ror = "ror:01111111"  # Replace with actual ROR ID
    results = pipeline.run_pipeline(test_org_ror)

    print("\n" + "="*60)
    print("GITHUB→DEPENDENCIES→SUPPLY_CHAIN FUSION RESULTS")
    print("="*60)

    if "error" not in results:
        print(f"Organization: {results['org_ror']}")
        print(f"GitHub organizations found: {len(results['github_organizations'])}")
        print(f"Total repositories: {results['total_repositories']}")
        print(f"Total dependencies: {results['total_dependencies']}")
        print(f"China-maintained dependencies: {results['china_maintained_dependencies']} ({results['china_exposure_percentage']:.1f}%)")
        print(f"High-risk dependencies: {results['high_risk_dependencies']}")
        print(f"Supply chain bottlenecks: {len(results['supply_chain_bottlenecks'])}")
    else:
        print(f"Error: {results['error']}")

if __name__ == "__main__":
    main()

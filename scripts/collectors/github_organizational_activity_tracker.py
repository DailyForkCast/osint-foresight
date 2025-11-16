#!/usr/bin/env python3
"""
GitHub Organizational Activity Tracker
Collects metadata about what organizations publish on GitHub using multiple sources
"""

import os
import json
import sqlite3
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import logging
import time
from dataclasses import dataclass, asdict
import hashlib

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class GitHubOrganization:
    """GitHub organization metadata"""
    github_login: str
    org_name: str
    description: str
    location: str
    public_repos: int
    followers: int
    created_at: datetime
    last_updated: datetime
    ror_id: Optional[str] = None
    entity_name: Optional[str] = None


@dataclass
class GitHubRepository:
    """GitHub repository metadata"""
    github_id: int
    org_login: str
    repo_name: str
    full_name: str
    description: str
    homepage_url: str
    primary_language: str
    topics: List[str]
    stars: int
    forks: int
    watchers: int
    open_issues: int
    created_at: datetime
    last_updated: datetime
    last_pushed: datetime
    license: str
    technology_domains: List[str]


class GitHubActivityTracker:
    """Track organizational GitHub activity for OSINT intelligence"""

    # Technology keyword mapping (aligned with arXiv categories)
    TECHNOLOGY_KEYWORDS = {
        'AI': {
            'topics': ['machine-learning', 'deep-learning', 'artificial-intelligence',
                      'neural-networks', 'computer-vision', 'nlp', 'reinforcement-learning'],
            'languages': ['python', 'jupyter-notebook'],
            'keywords': ['tensorflow', 'pytorch', 'keras', 'transformers', 'llm',
                        'gpt', 'bert', 'vision', 'classification']
        },
        'Quantum': {
            'topics': ['quantum-computing', 'quantum', 'qiskit', 'cirq'],
            'languages': ['python', 'q#', 'qasm'],
            'keywords': ['quantum', 'qubit', 'entanglement', 'superposition',
                        'quantum-algorithm', 'quantum-circuit']
        },
        'Space': {
            'topics': ['aerospace', 'satellite', 'space', 'astronomy', 'astrophysics'],
            'languages': ['python', 'c++', 'fortran'],
            'keywords': ['satellite', 'orbit', 'spacecraft', 'astronomy', 'astrophysics',
                        'remote-sensing', 'earth-observation']
        },
        'Semiconductors': {
            'topics': ['hardware', 'electronics', 'fpga', 'asic', 'vlsi', 'eda'],
            'languages': ['verilog', 'vhdl', 'systemverilog', 'chisel'],
            'keywords': ['chip', 'semiconductor', 'lithography', 'circuit-design',
                        'fpga', 'asic', 'rtl', 'synthesis']
        },
        'Smart_City': {
            'topics': ['iot', 'smart-city', 'urban-computing', 'smart-grid'],
            'languages': ['python', 'javascript', 'c'],
            'keywords': ['iot', 'sensor', 'smart-city', 'urban', 'traffic',
                        'smart-grid', 'energy-management']
        },
        'Neuroscience': {
            'topics': ['neuroscience', 'brain-computer-interface', 'neuroimaging'],
            'languages': ['python', 'matlab', 'r'],
            'keywords': ['brain', 'neural', 'neuroscience', 'fmri', 'eeg',
                        'brain-computer-interface', 'cognitive']
        },
        'Biotechnology': {
            'topics': ['bioinformatics', 'computational-biology', 'genomics', 'biotech'],
            'languages': ['python', 'r', 'julia'],
            'keywords': ['gene', 'protein', 'bioinformatics', 'genomics', 'crispr',
                        'drug-discovery', 'molecular']
        },
        'Advanced_Materials': {
            'topics': ['materials-science', 'nanotechnology', 'chemistry'],
            'languages': ['python', 'fortran', 'c++'],
            'keywords': ['materials', 'nanotechnology', 'polymer', 'composite',
                        'graphene', '2d-materials', 'catalyst']
        },
        'Energy': {
            'topics': ['renewable-energy', 'battery', 'solar', 'energy', 'sustainability'],
            'languages': ['python', 'matlab'],
            'keywords': ['battery', 'solar', 'wind', 'energy-storage', 'fuel-cell',
                        'photovoltaic', 'renewable']
        }
    }

    # Target organizations for intelligence collection
    TARGET_ORGANIZATIONS = {
        'chinese_tech': [
            'alibaba', 'alipay', 'ant-design', 'alibaba-cloud',
            'tencent', 'TencentCloudBase', 'TencentARC',
            'baidu', 'PaddlePaddle', 'BaiduResearch',
            'huawei', 'huawei-noah', 'mindspore-ai',
            'bytedance', 'ByteDance',
            'xiaomi', 'MIUI'
        ],
        'chinese_academic': [
            'tsinghua-ZKC', 'THU-MIG', 'THUDM',
            'PKU-IDEA', 'PKU-YuanGroup',
            'CASIA-IVA-Lab', 'CASIA-AI'
        ],
        'defense_contractors': [
            'leonardo-company', 'leonardo-drs',
            'raytheontech', 'lockheed-martin',
            'northrop-grumman', 'BAESystemsInc'
        ],
        'semiconductors': [
            'intel', 'intel-AI', 'AMD', 'NVIDIA', 'NVIDIA-AI-IOT'
        ],
        'strategic_opensource': [
            'tensorflow', 'pytorch', 'kubernetes', 'docker',
            'apache', 'openai', 'microsoft'
        ]
    }

    def __init__(self, github_token: Optional[str] = None):
        """Initialize the GitHub activity tracker"""
        self.github_token = github_token or os.getenv("GITHUB_TOKEN")

        if not self.github_token:
            logger.warning("No GitHub token - limited to 60 requests/hour")
        else:
            logger.info("GitHub token found - 5000 requests/hour available")

        self.headers = {
            'Authorization': f'Bearer {self.github_token}' if self.github_token else '',
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28',
            'User-Agent': 'OSINT-Foresight-Research/1.0'
        }

        # Database setup
        self.master_db = Path("F:/OSINT_WAREHOUSE/osint_master.db")
        self.processing_db = Path("C:/Projects/OSINT - Foresight/data/github_activity.db")

        # Output directory
        self.output_dir = Path("C:/Projects/OSINT - Foresight/data/processed/github_activity")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Rate limiting
        self.last_request = 0
        self.min_request_interval = 0.72  # ~5000 requests/hour

        self._init_database()

    def _init_database(self):
        """Initialize GitHub activity database"""
        conn = sqlite3.connect(self.processing_db)
        cursor = conn.cursor()

        # Organizations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS github_organizations (
                org_id INTEGER PRIMARY KEY AUTOINCREMENT,
                github_login TEXT UNIQUE NOT NULL,
                org_name TEXT,
                description TEXT,
                location TEXT,
                public_repos INTEGER,
                followers INTEGER,
                created_at TIMESTAMP,
                last_updated TIMESTAMP,
                ror_id TEXT,
                entity_name TEXT,
                category TEXT,
                collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Repositories table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS github_repositories (
                repo_id INTEGER PRIMARY KEY AUTOINCREMENT,
                github_id INTEGER UNIQUE NOT NULL,
                org_login TEXT NOT NULL,
                repo_name TEXT NOT NULL,
                full_name TEXT UNIQUE NOT NULL,
                description TEXT,
                homepage_url TEXT,
                primary_language TEXT,
                topics TEXT,
                stars INTEGER,
                forks INTEGER,
                watchers INTEGER,
                open_issues INTEGER,
                created_at TIMESTAMP,
                last_updated TIMESTAMP,
                last_pushed TIMESTAMP,
                license TEXT,
                technology_domains TEXT,
                collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (org_login) REFERENCES github_organizations(github_login)
            )
        """)

        # Releases table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS github_releases (
                release_id INTEGER PRIMARY KEY AUTOINCREMENT,
                repo_full_name TEXT NOT NULL,
                tag_name TEXT NOT NULL,
                release_name TEXT,
                description TEXT,
                author_login TEXT,
                created_at TIMESTAMP,
                published_at TIMESTAMP,
                is_prerelease BOOLEAN,
                tarball_url TEXT,
                UNIQUE(repo_full_name, tag_name),
                FOREIGN KEY (repo_full_name) REFERENCES github_repositories(full_name)
            )
        """)

        # Processing log
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS processing_log (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                org_login TEXT NOT NULL,
                process_type TEXT,
                status TEXT,
                message TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_repos_org ON github_repositories(org_login)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_repos_language ON github_repositories(primary_language)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_repos_updated ON github_repositories(last_updated)")

        conn.commit()
        conn.close()

        logger.info(f"Database initialized: {self.processing_db}")

    def _rate_limit(self):
        """Enforce rate limiting"""
        elapsed = time.time() - self.last_request
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)
        self.last_request = time.time()

    def check_rate_limit(self) -> Dict:
        """Check GitHub API rate limit status"""
        try:
            response = requests.get(
                'https://api.github.com/rate_limit',
                headers=self.headers,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                core = data.get('rate', {})
                return {
                    'limit': core.get('limit'),
                    'remaining': core.get('remaining'),
                    'reset': datetime.fromtimestamp(core.get('reset', 0)),
                    'used': core.get('used')
                }
        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")

        return {'limit': 60, 'remaining': 0, 'reset': datetime.now()}

    def get_organization(self, org_login: str) -> Optional[GitHubOrganization]:
        """Get GitHub organization metadata"""
        self._rate_limit()

        try:
            url = f'https://api.github.com/orgs/{org_login}'
            response = requests.get(url, headers=self.headers, timeout=30)

            if response.status_code == 200:
                data = response.json()

                return GitHubOrganization(
                    github_login=data.get('login', ''),
                    org_name=data.get('name') or data.get('login', ''),
                    description=data.get('description', ''),
                    location=data.get('location', ''),
                    public_repos=data.get('public_repos', 0),
                    followers=data.get('followers', 0),
                    created_at=datetime.fromisoformat(data.get('created_at', '2020-01-01T00:00:00Z').replace('Z', '')),
                    last_updated=datetime.fromisoformat(data.get('updated_at', '2020-01-01T00:00:00Z').replace('Z', ''))
                )
            elif response.status_code == 404:
                logger.warning(f"Organization not found: {org_login}")
            else:
                logger.error(f"Error fetching {org_login}: {response.status_code}")

        except Exception as e:
            logger.error(f"Exception fetching org {org_login}: {e}")

        return None

    def get_organization_repositories(self, org_login: str, max_repos: int = 500) -> List[GitHubRepository]:
        """Get repositories for an organization"""
        repositories = []
        page = 1
        per_page = 100

        logger.info(f"Fetching repositories for {org_login}...")

        while len(repositories) < max_repos:
            self._rate_limit()

            try:
                url = f'https://api.github.com/orgs/{org_login}/repos'
                params = {
                    'type': 'all',
                    'sort': 'updated',
                    'direction': 'desc',
                    'per_page': per_page,
                    'page': page
                }

                response = requests.get(url, headers=self.headers, params=params, timeout=30)

                if response.status_code == 200:
                    repos_data = response.json()

                    if not repos_data:
                        break

                    for repo in repos_data:
                        # Get topics (requires separate API call or accept header)
                        topics = repo.get('topics', [])

                        # Classify into technology domains
                        tech_domains = self._classify_technology(
                            description=repo.get('description', ''),
                            topics=topics,
                            language=repo.get('language', ''),
                            repo_name=repo.get('name', '')
                        )

                        repository = GitHubRepository(
                            github_id=repo.get('id'),
                            org_login=org_login,
                            repo_name=repo.get('name', ''),
                            full_name=repo.get('full_name', ''),
                            description=repo.get('description', ''),
                            homepage_url=repo.get('homepage', ''),
                            primary_language=repo.get('language', ''),
                            topics=topics,
                            stars=repo.get('stargazers_count', 0),
                            forks=repo.get('forks_count', 0),
                            watchers=repo.get('watchers_count', 0),
                            open_issues=repo.get('open_issues_count', 0),
                            created_at=datetime.fromisoformat(repo.get('created_at', '2020-01-01T00:00:00Z').replace('Z', '')),
                            last_updated=datetime.fromisoformat(repo.get('updated_at', '2020-01-01T00:00:00Z').replace('Z', '')),
                            last_pushed=datetime.fromisoformat(repo.get('pushed_at', '2020-01-01T00:00:00Z').replace('Z', '')),
                            license=repo.get('license', {}).get('name', '') if repo.get('license') else '',
                            technology_domains=tech_domains
                        )

                        repositories.append(repository)

                    page += 1

                else:
                    logger.error(f"Error fetching repos (page {page}): {response.status_code}")
                    break

            except Exception as e:
                logger.error(f"Exception fetching repos page {page}: {e}")
                break

        logger.info(f"Collected {len(repositories)} repositories for {org_login}")
        return repositories

    def _classify_technology(self, description: str, topics: List[str],
                            language: str, repo_name: str) -> List[str]:
        """Classify repository into technology domains"""
        matched_domains = []
        text = f"{description} {repo_name}".lower()

        for domain, indicators in self.TECHNOLOGY_KEYWORDS.items():
            score = 0

            # Check topics (highest weight)
            for topic in topics:
                if topic.lower() in indicators['topics']:
                    score += 3

            # Check language (medium weight)
            if language.lower() in [lang.lower() for lang in indicators['languages']]:
                score += 2

            # Check keywords in description (low weight)
            for keyword in indicators['keywords']:
                if keyword in text:
                    score += 1

            if score >= 2:  # Threshold for classification
                matched_domains.append(domain)

        return matched_domains

    def save_organization(self, org: GitHubOrganization, category: str):
        """Save organization to database"""
        conn = sqlite3.connect(self.processing_db)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO github_organizations
            (github_login, org_name, description, location, public_repos, followers,
             created_at, last_updated, category)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            org.github_login, org.org_name, org.description, org.location,
            org.public_repos, org.followers, org.created_at, org.last_updated,
            category
        ))

        conn.commit()
        conn.close()

    def save_repositories(self, repositories: List[GitHubRepository]):
        """Save repositories to database"""
        conn = sqlite3.connect(self.processing_db)
        cursor = conn.cursor()

        for repo in repositories:
            cursor.execute("""
                INSERT OR REPLACE INTO github_repositories
                (github_id, org_login, repo_name, full_name, description, homepage_url,
                 primary_language, topics, stars, forks, watchers, open_issues,
                 created_at, last_updated, last_pushed, license, technology_domains)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                repo.github_id, repo.org_login, repo.repo_name, repo.full_name,
                repo.description, repo.homepage_url, repo.primary_language,
                json.dumps(repo.topics), repo.stars, repo.forks, repo.watchers,
                repo.open_issues, repo.created_at, repo.last_updated, repo.last_pushed,
                repo.license, json.dumps(repo.technology_domains)
            ))

        conn.commit()
        conn.close()

        logger.info(f"Saved {len(repositories)} repositories to database")

    def collect_organization_activity(self, org_login: str, category: str):
        """Collect complete activity for an organization"""
        logger.info(f"\n{'='*60}")
        logger.info(f"Collecting activity for: {org_login} ({category})")
        logger.info(f"{'='*60}")

        # Get organization metadata
        org = self.get_organization(org_login)
        if not org:
            logger.warning(f"Skipping {org_login} - not found")
            return

        self.save_organization(org, category)
        logger.info(f"Organization: {org.org_name}")
        logger.info(f"Public repos: {org.public_repos}")
        logger.info(f"Followers: {org.followers}")

        # Get repositories
        repositories = self.get_organization_repositories(org_login, max_repos=500)
        if repositories:
            self.save_repositories(repositories)

            # Technology breakdown
            tech_counts = {}
            for repo in repositories:
                for domain in repo.technology_domains:
                    tech_counts[domain] = tech_counts.get(domain, 0) + 1

            logger.info(f"\nTechnology Distribution:")
            for domain, count in sorted(tech_counts.items(), key=lambda x: x[1], reverse=True):
                logger.info(f"  {domain}: {count} repos")

    def collect_all_targets(self):
        """Collect activity for all target organizations"""
        logger.info(f"\n{'='*60}")
        logger.info("GITHUB ORGANIZATIONAL ACTIVITY COLLECTION")
        logger.info(f"{'='*60}\n")

        # Check rate limit
        rate_info = self.check_rate_limit()
        logger.info(f"Rate limit: {rate_info['remaining']}/{rate_info['limit']}")
        logger.info(f"Reset at: {rate_info['reset']}\n")

        total_orgs = sum(len(orgs) for orgs in self.TARGET_ORGANIZATIONS.values())
        collected = 0

        for category, org_list in self.TARGET_ORGANIZATIONS.items():
            logger.info(f"\n--- Category: {category.upper().replace('_', ' ')} ---")

            for org_login in org_list:
                try:
                    self.collect_organization_activity(org_login, category)
                    collected += 1

                    # Progress update
                    logger.info(f"\nProgress: {collected}/{total_orgs} organizations")

                    # Check rate limit periodically
                    if collected % 10 == 0:
                        rate_info = self.check_rate_limit()
                        logger.info(f"Rate limit remaining: {rate_info['remaining']}")

                        if rate_info['remaining'] < 100:
                            logger.warning("Low rate limit - pausing for 1 minute")
                            time.sleep(60)

                except Exception as e:
                    logger.error(f"Error processing {org_login}: {e}")
                    continue

        logger.info(f"\n{'='*60}")
        logger.info(f"Collection complete: {collected}/{total_orgs} organizations")
        logger.info(f"{'='*60}")

        self.generate_summary_report()

    def generate_summary_report(self):
        """Generate summary statistics"""
        conn = sqlite3.connect(self.processing_db)

        # Overall statistics
        stats = {
            'collection_date': datetime.now().isoformat(),
            'organizations': {},
            'repositories': {},
            'technologies': {}
        }

        # Organization counts by category
        cursor = conn.execute("""
            SELECT category, COUNT(*) as count, SUM(public_repos) as total_repos
            FROM github_organizations
            GROUP BY category
        """)

        for row in cursor:
            stats['organizations'][row[0]] = {
                'count': row[1],
                'total_repos': row[2]
            }

        # Repository statistics
        cursor = conn.execute("""
            SELECT COUNT(*) as total, SUM(stars) as total_stars,
                   SUM(forks) as total_forks, COUNT(DISTINCT primary_language) as languages
            FROM github_repositories
        """)

        row = cursor.fetchone()
        stats['repositories'] = {
            'total': row[0],
            'total_stars': row[1],
            'total_forks': row[2],
            'unique_languages': row[3]
        }

        # Technology domain distribution
        cursor = conn.execute("""
            SELECT technology_domains FROM github_repositories
            WHERE technology_domains != '[]'
        """)

        tech_counts = {}
        for row in cursor:
            domains = json.loads(row[0])
            for domain in domains:
                tech_counts[domain] = tech_counts.get(domain, 0) + 1

        stats['technologies'] = tech_counts

        conn.close()

        # Save report
        output_file = self.output_dir / f"github_activity_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(stats, f, indent=2)

        logger.info(f"\nSummary report saved: {output_file}")

        # Print summary
        logger.info(f"\n{'='*60}")
        logger.info("COLLECTION SUMMARY")
        logger.info(f"{'='*60}")
        logger.info(f"Total organizations: {sum(cat['count'] for cat in stats['organizations'].values())}")
        logger.info(f"Total repositories: {stats['repositories']['total']}")
        logger.info(f"Total stars: {stats['repositories']['total_stars']:,}")
        logger.info(f"Total forks: {stats['repositories']['total_forks']:,}")
        logger.info(f"\nTop technologies:")
        for domain, count in sorted(tech_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            logger.info(f"  {domain}: {count} repos")


def main():
    """Main execution"""
    tracker = GitHubActivityTracker()

    # Collect all target organizations
    tracker.collect_all_targets()


if __name__ == "__main__":
    main()

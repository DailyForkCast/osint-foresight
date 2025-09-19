"""
GitHub Dependency Scanner for Supply Chain Intelligence
Analyzes GitHub organizations for China-maintained dependencies and vulnerabilities
"""

import os
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import logging
import time
import base64
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GitHubDependencyScanner:
    """Scan GitHub organizations for supply chain vulnerabilities"""

    def __init__(self):
        # GitHub API configuration
        self.github_token = os.getenv("GITHUB_TOKEN", "")
        self.base_url = "https://api.github.com"

        # Headers with authentication if available
        self.headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }

        if self.github_token:
            self.headers["Authorization"] = f"Bearer {self.github_token}"
            logger.info("GitHub API authenticated")
        else:
            logger.warning("No GitHub token found - API rate limited to 60 requests/hour")

        # Output directory
        self.output_dir = Path("F:/OSINT_DATA/github_dependencies")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # China-maintained packages database
        self.china_packages = {
            "npm": {
                "vue": {"maintainer": "Evan You", "org": "vuejs", "risk": "medium"},
                "element-ui": {"maintainer": "ElemeFE", "org": "ElemeFE", "risk": "medium"},
                "ant-design": {"maintainer": "Ant Design Team", "org": "ant-design", "risk": "medium"},
                "vant": {"maintainer": "Youzan", "org": "youzan", "risk": "low"},
                "weex": {"maintainer": "Alibaba", "org": "alibaba", "risk": "high"},
                "egg": {"maintainer": "Alibaba", "org": "eggjs", "risk": "medium"},
                "ice": {"maintainer": "Alibaba", "org": "alibaba", "risk": "medium"},
            },
            "python": {
                "paddlepaddle": {"maintainer": "Baidu", "org": "PaddlePaddle", "risk": "high"},
                "jieba": {"maintainer": "Sun Junyi", "org": "fxsjy", "risk": "low"},
                "dragonfly": {"maintainer": "Alibaba", "org": "alibaba", "risk": "medium"},
            },
            "go": {
                "tidb": {"maintainer": "PingCAP", "org": "pingcap", "risk": "high"},
                "harbor": {"maintainer": "VMware China", "org": "goharbor", "risk": "medium"},
                "k3s": {"maintainer": "Rancher (SUSE China)", "org": "k3s-io", "risk": "medium"},
                "dragonfly": {"maintainer": "Alibaba", "org": "dragonflyoss", "risk": "medium"},
            },
            "java": {
                "dubbo": {"maintainer": "Alibaba", "org": "apache", "risk": "high"},
                "fastjson": {"maintainer": "Alibaba", "org": "alibaba", "risk": "high"},
                "druid": {"maintainer": "Alibaba", "org": "alibaba", "risk": "medium"},
                "seata": {"maintainer": "Alibaba", "org": "seata", "risk": "medium"},
            }
        }

        # Target organizations
        self.italy_orgs = [
            "leonardo-company",
            "finmeccanica",
            "leonardo-drs",
            "telespazio",
            "vitrociset",
            "selex-es"
        ]

        self.china_orgs = [
            "alibaba",
            "tencent",
            "baidu",
            "huawei",
            "xiaomi",
            "bytedance",
            "didi",
            "pingcap"
        ]

    def check_rate_limit(self) -> Dict:
        """Check GitHub API rate limit status"""
        try:
            response = requests.get(
                f"{self.base_url}/rate_limit",
                headers=self.headers,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                core = data.get("rate", {})
                return {
                    "limit": core.get("limit"),
                    "remaining": core.get("remaining"),
                    "reset": datetime.fromtimestamp(core.get("reset", 0))
                }
        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")

        return {"limit": 60, "remaining": 0, "reset": datetime.now()}

    def get_org_repos(self, org: str) -> List[Dict]:
        """Get all repositories for an organization"""
        repos = []
        page = 1

        while True:
            try:
                response = requests.get(
                    f"{self.base_url}/orgs/{org}/repos",
                    headers=self.headers,
                    params={
                        "type": "all",
                        "per_page": 100,
                        "page": page
                    },
                    timeout=30
                )

                if response.status_code == 404:
                    logger.warning(f"Organization {org} not found")
                    break
                elif response.status_code == 200:
                    page_repos = response.json()
                    if not page_repos:
                        break
                    repos.extend(page_repos)
                    page += 1
                    time.sleep(0.5)  # Rate limiting
                else:
                    logger.error(f"Error fetching repos for {org}: {response.status_code}")
                    break

            except Exception as e:
                logger.error(f"Error fetching repos for {org}: {e}")
                break

        return repos

    def analyze_package_json(self, org: str, repo: str) -> Dict:
        """Analyze package.json for npm dependencies"""
        china_deps = []

        try:
            # Try to fetch package.json
            response = requests.get(
                f"{self.base_url}/repos/{org}/{repo}/contents/package.json",
                headers=self.headers,
                timeout=10
            )

            if response.status_code == 200:
                content = response.json()
                package_json = json.loads(
                    base64.b64decode(content["content"]).decode("utf-8")
                )

                # Check dependencies
                all_deps = {}
                for dep_type in ["dependencies", "devDependencies", "peerDependencies"]:
                    all_deps.update(package_json.get(dep_type, {}))

                # Check for China-maintained packages
                for pkg_name in all_deps:
                    base_pkg = pkg_name.split("/")[-1]  # Handle scoped packages
                    if base_pkg in self.china_packages["npm"]:
                        china_info = self.china_packages["npm"][base_pkg]
                        china_deps.append({
                            "package": pkg_name,
                            "version": all_deps[pkg_name],
                            "maintainer": china_info["maintainer"],
                            "risk": china_info["risk"],
                            "type": "npm"
                        })

        except Exception as e:
            logger.debug(f"No package.json or error in {org}/{repo}: {e}")

        return {"npm": china_deps}

    def analyze_requirements_txt(self, org: str, repo: str) -> Dict:
        """Analyze requirements.txt for Python dependencies"""
        china_deps = []

        try:
            # Try to fetch requirements.txt
            for req_file in ["requirements.txt", "requirements.pip", "Pipfile"]:
                response = requests.get(
                    f"{self.base_url}/repos/{org}/{repo}/contents/{req_file}",
                    headers=self.headers,
                    timeout=10
                )

                if response.status_code == 200:
                    content = response.json()
                    requirements = base64.b64decode(content["content"]).decode("utf-8")

                    # Parse requirements
                    for line in requirements.split("\n"):
                        line = line.strip()
                        if line and not line.startswith("#"):
                            # Extract package name
                            pkg_name = re.split(r'[<>=!~]', line)[0].strip()

                            if pkg_name in self.china_packages["python"]:
                                china_info = self.china_packages["python"][pkg_name]
                                china_deps.append({
                                    "package": pkg_name,
                                    "requirement": line,
                                    "maintainer": china_info["maintainer"],
                                    "risk": china_info["risk"],
                                    "type": "python"
                                })
                    break

        except Exception as e:
            logger.debug(f"No requirements.txt or error in {org}/{repo}: {e}")

        return {"python": china_deps}

    def analyze_go_mod(self, org: str, repo: str) -> Dict:
        """Analyze go.mod for Go dependencies"""
        china_deps = []

        try:
            response = requests.get(
                f"{self.base_url}/repos/{org}/{repo}/contents/go.mod",
                headers=self.headers,
                timeout=10
            )

            if response.status_code == 200:
                content = response.json()
                go_mod = base64.b64decode(content["content"]).decode("utf-8")

                # Parse go.mod
                for line in go_mod.split("\n"):
                    if "require" in line or line.strip().startswith("github.com"):
                        # Check for known China packages
                        for pkg_name, china_info in self.china_packages["go"].items():
                            if pkg_name in line or china_info["org"] in line:
                                china_deps.append({
                                    "package": pkg_name,
                                    "line": line.strip(),
                                    "maintainer": china_info["maintainer"],
                                    "risk": china_info["risk"],
                                    "type": "go"
                                })

        except Exception as e:
            logger.debug(f"No go.mod or error in {org}/{repo}: {e}")

        return {"go": china_deps}

    def analyze_pom_xml(self, org: str, repo: str) -> Dict:
        """Analyze pom.xml for Java/Maven dependencies"""
        china_deps = []

        try:
            response = requests.get(
                f"{self.base_url}/repos/{org}/{repo}/contents/pom.xml",
                headers=self.headers,
                timeout=10
            )

            if response.status_code == 200:
                content = response.json()
                pom_xml = base64.b64decode(content["content"]).decode("utf-8")

                # Simple pattern matching for dependencies
                for pkg_name, china_info in self.china_packages["java"].items():
                    if pkg_name in pom_xml or f"com.alibaba" in pom_xml:
                        china_deps.append({
                            "package": pkg_name,
                            "maintainer": china_info["maintainer"],
                            "risk": china_info["risk"],
                            "type": "java"
                        })

        except Exception as e:
            logger.debug(f"No pom.xml or error in {org}/{repo}: {e}")

        return {"java": china_deps}

    def scan_repository(self, org: str, repo_name: str) -> Dict:
        """Comprehensive scan of a single repository"""
        logger.info(f"Scanning {org}/{repo_name}")

        results = {
            "repository": f"{org}/{repo_name}",
            "scanned_at": datetime.now().isoformat(),
            "china_dependencies": {},
            "risk_score": 0,
            "vulnerability_count": 0
        }

        # Scan different package managers
        npm_deps = self.analyze_package_json(org, repo_name)
        python_deps = self.analyze_requirements_txt(org, repo_name)
        go_deps = self.analyze_go_mod(org, repo_name)
        java_deps = self.analyze_pom_xml(org, repo_name)

        # Combine results
        all_china_deps = []
        for deps in [npm_deps, python_deps, go_deps, java_deps]:
            for dep_type, dep_list in deps.items():
                if dep_list:
                    all_china_deps.extend(dep_list)
                    results["china_dependencies"][dep_type] = dep_list

        # Calculate risk score
        if all_china_deps:
            high_risk = sum(1 for d in all_china_deps if d.get("risk") == "high")
            medium_risk = sum(1 for d in all_china_deps if d.get("risk") == "medium")
            low_risk = sum(1 for d in all_china_deps if d.get("risk") == "low")

            results["risk_score"] = min(1.0, (high_risk * 0.5 + medium_risk * 0.3 + low_risk * 0.1))
            results["vulnerability_count"] = len(all_china_deps)

        time.sleep(0.5)  # Rate limiting

        return results

    def scan_organization(self, org_name: str) -> Dict:
        """Scan all repositories in an organization"""
        logger.info(f"\n[SCANNING] Organization: {org_name}")

        # Check rate limit
        rate_info = self.check_rate_limit()
        logger.info(f"Rate limit: {rate_info['remaining']}/{rate_info['limit']}")

        if rate_info["remaining"] < 10:
            logger.warning(f"Low rate limit. Reset at {rate_info['reset']}")

        # Get organization repositories
        repos = self.get_org_repos(org_name)

        if not repos:
            logger.warning(f"No repositories found for {org_name}")
            return {
                "organization": org_name,
                "status": "not_found",
                "repositories_scanned": 0
            }

        logger.info(f"Found {len(repos)} repositories for {org_name}")

        # Scan each repository
        org_results = {
            "organization": org_name,
            "scan_timestamp": datetime.now().isoformat(),
            "total_repositories": len(repos),
            "repositories_scanned": 0,
            "china_exposed_repos": [],
            "total_china_dependencies": 0,
            "high_risk_dependencies": 0,
            "organization_risk_score": 0
        }

        # Limit to top 10 repos for rate limiting
        for repo in repos[:10]:
            repo_name = repo["name"]
            repo_results = self.scan_repository(org_name, repo_name)

            if repo_results["china_dependencies"]:
                org_results["china_exposed_repos"].append(repo_results)
                org_results["total_china_dependencies"] += repo_results["vulnerability_count"]

                # Count high risk
                for dep_type, deps in repo_results["china_dependencies"].items():
                    high_risk = sum(1 for d in deps if d.get("risk") == "high")
                    org_results["high_risk_dependencies"] += high_risk

            org_results["repositories_scanned"] += 1

        # Calculate organization risk score
        if org_results["repositories_scanned"] > 0:
            exposed_ratio = len(org_results["china_exposed_repos"]) / org_results["repositories_scanned"]
            high_risk_ratio = org_results["high_risk_dependencies"] / max(1, org_results["total_china_dependencies"])
            org_results["organization_risk_score"] = (exposed_ratio * 0.6 + high_risk_ratio * 0.4)

        return org_results

    def scan_italy_defense_contractors(self) -> Dict:
        """Scan Italian defense contractors for China dependencies"""
        results = {
            "scan_type": "italy_defense_contractors",
            "timestamp": datetime.now().isoformat(),
            "organizations": {}
        }

        for org in self.italy_orgs:
            logger.info(f"\nScanning Italian organization: {org}")
            org_results = self.scan_organization(org)
            results["organizations"][org] = org_results

            # Save intermediate results
            self.save_scan_results(org_results, f"italy_{org}")

        # Summary statistics
        results["summary"] = {
            "total_organizations": len(self.italy_orgs),
            "organizations_with_repos": sum(
                1 for r in results["organizations"].values()
                if r.get("status") != "not_found"
            ),
            "total_china_dependencies": sum(
                r.get("total_china_dependencies", 0)
                for r in results["organizations"].values()
            ),
            "high_risk_dependencies": sum(
                r.get("high_risk_dependencies", 0)
                for r in results["organizations"].values()
            )
        }

        return results

    def check_vulnerability_database(self, package_info: Dict) -> List[Dict]:
        """Check for known vulnerabilities in a package"""
        # This would integrate with vulnerability databases
        # For now, return simulated vulnerabilities for high-risk packages

        vulnerabilities = []
        if package_info.get("risk") == "high":
            vulnerabilities.append({
                "cve": "CVE-2024-SIMULATED",
                "severity": "HIGH",
                "description": "Potential supply chain vulnerability",
                "china_attribution": True
            })

        return vulnerabilities

    def analyze_commit_history(self, org: str, repo: str) -> Dict:
        """Analyze commit history for China-affiliated contributors"""
        china_contributors = []

        try:
            # Get recent commits
            response = requests.get(
                f"{self.base_url}/repos/{org}/{repo}/commits",
                headers=self.headers,
                params={"per_page": 100},
                timeout=30
            )

            if response.status_code == 200:
                commits = response.json()

                # Analyze committer emails and names
                china_domains = [".cn", "alibaba", "tencent", "baidu", "huawei", "bytedance"]

                for commit in commits:
                    author = commit.get("commit", {}).get("author", {})
                    email = author.get("email", "").lower()
                    name = author.get("name", "").lower()

                    # Check for China affiliation
                    if any(domain in email for domain in china_domains):
                        china_contributors.append({
                            "name": author.get("name"),
                            "email": author.get("email"),
                            "commits": 1,
                            "confidence": 0.9
                        })

        except Exception as e:
            logger.debug(f"Error analyzing commits for {org}/{repo}: {e}")

        return {
            "china_contributors": china_contributors,
            "china_commit_ratio": len(china_contributors) / 100 if china_contributors else 0
        }

    def save_scan_results(self, results: Dict, prefix: str = "scan") -> Path:
        """Save scan results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"{prefix}_{timestamp}.json"

        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)

        logger.info(f"Results saved to {output_file}")
        return output_file

    def generate_supply_chain_report(self, scan_results: Dict) -> Dict:
        """Generate supply chain risk report"""
        report = {
            "report_type": "supply_chain_risk_assessment",
            "generated_at": datetime.now().isoformat(),
            "critical_findings": [],
            "recommendations": []
        }

        # Analyze results
        for org, org_data in scan_results.get("organizations", {}).items():
            if org_data.get("organization_risk_score", 0) > 0.7:
                report["critical_findings"].append({
                    "organization": org,
                    "risk_score": org_data["organization_risk_score"],
                    "china_dependencies": org_data.get("total_china_dependencies", 0),
                    "high_risk_count": org_data.get("high_risk_dependencies", 0),
                    "severity": "CRITICAL"
                })

                report["recommendations"].append({
                    "organization": org,
                    "action": "Immediate supply chain audit required",
                    "priority": "HIGH",
                    "mitigation": "Consider alternative packages or vendoring critical dependencies"
                })

        return report


if __name__ == "__main__":
    scanner = GitHubDependencyScanner()

    print("[GITHUB DEPENDENCY SCANNER]")
    print("Scanning Italian defense contractors for China-maintained dependencies...")

    # Scan Italian organizations
    italy_results = scanner.scan_italy_defense_contractors()

    # Generate report
    report = scanner.generate_supply_chain_report(italy_results)

    # Save comprehensive results
    scanner.save_scan_results(italy_results, "italy_defense_supply_chain")
    scanner.save_scan_results(report, "supply_chain_risk_report")

    print(f"\n[SUMMARY]")
    print(f"Organizations scanned: {italy_results['summary']['total_organizations']}")
    print(f"China dependencies found: {italy_results['summary']['total_china_dependencies']}")
    print(f"High risk dependencies: {italy_results['summary']['high_risk_dependencies']}")
    print(f"\nResults saved to F:/OSINT_DATA/github_dependencies/")

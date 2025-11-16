#!/usr/bin/env python3
"""
ETO Dataset Collector - Automated collection of Emerging Technology Observatory datasets

Monitors and downloads datasets from:
- Zenodo (Country AI Activity Metrics, etc.)
- GitHub (Semiconductor Supply Chain, etc.)
- Direct downloads (other datasets)

Runs weekly to check for updates and download new versions.
"""

import requests
import hashlib
import json
import logging
import time
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
from urllib.parse import urljoin

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class ETODatasetCollector:
    """Collector for ETO (Emerging Technology Observatory) datasets."""

    # ETO Dataset Registry
    DATASETS = {
        "country_ai_metrics": {
            "name": "Country AI Activity Metrics",
            "source_type": "zenodo",
            "zenodo_doi": "10.5281/zenodo.13984221",
            "files": [
                "publications_yearly_articles.csv",
                "publications_yearly_citations.csv",
                "publications_summary.csv",
                "patents_yearly_applications.csv",
                "patents_yearly_granted.csv",
                "patents_summary.csv",
                "companies_yearly_disclosed.csv",
                "companies_yearly_estimated.csv",
                "companies_summary.csv"
            ],
            "update_frequency": "monthly",
            "description": "National-level metrics for AI research, patents, and investment"
        },
        "semiconductor_supply_chain": {
            "name": "Advanced Semiconductor Supply Chain",
            "source_type": "github",
            "github_repo": "georgetown-cset/eto-supply-chain",
            "github_path": "data",
            "files": [
                "inputs.csv",
                "providers.csv",
                "provision.csv",
                "sequence.csv",
                "stages.csv"
            ],
            "update_frequency": "periodic",
            "description": "Supply chain data for advanced logic chip production"
        },
        "cross_border_research": {
            "name": "Cross-Border Tech Research Metrics",
            "source_type": "zenodo",
            "zenodo_doi": "10.5281/zenodo.14510656",
            "files": ["cross_border_research_metrics.csv"],
            "update_frequency": "periodic",
            "description": "Cross-border collaboration in AI, robotics, cybersecurity"
        },
        "private_sector_ai": {
            "name": "Private-Sector AI Indicators",
            "source_type": "zenodo",
            "zenodo_doi": "10.5281/zenodo.14194293",
            "files": ["private_sector_ai_indicators.csv"],
            "update_frequency": "periodic",
            "description": "AI activity indicators for companies worldwide"
        },
        "agora_ai_governance": {
            "name": "AGORA AI Governance Dataset",
            "source_type": "zenodo",
            "zenodo_doi": "10.5281/zenodo.14291866",
            "files": ["agora_documents.csv", "agora_metadata.csv"],
            "update_frequency": "frequent",
            "description": "AI laws, regulations, and governance documents"
        },
        "openalex_overlay": {
            "name": "ETO OpenAlex Overlay",
            "source_type": "zenodo",
            "zenodo_doi": "10.5281/zenodo.14237445",
            "files": ["openalex_emerging_tech_labels.csv"],
            "update_frequency": "periodic",
            "description": "Emerging tech classifications for OpenAlex works"
        }
    }

    # Storage paths
    BASE_DIR = Path("F:/ETO_Datasets")
    STATE_FILE = BASE_DIR / "eto_collection_state.json"
    DOWNLOADS_DIR = BASE_DIR / "downloads"
    PROCESSED_DIR = BASE_DIR / "processed"

    # API endpoints
    ZENODO_API = "https://zenodo.org/api/records/"
    GITHUB_API = "https://api.github.com"

    def __init__(self):
        """Initialize the ETO collector."""
        self.state = {}
        self.downloads_made = []
        self.updates_found = []

        # Create directories
        self.BASE_DIR.mkdir(parents=True, exist_ok=True)
        self.DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
        self.PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

        # Load state
        self.load_state()

    def load_state(self):
        """Load collection state from disk."""
        if self.STATE_FILE.exists():
            try:
                with open(self.STATE_FILE, 'r', encoding='utf-8') as f:
                    self.state = json.load(f)
                logging.info(f"Loaded state from {self.STATE_FILE}")
            except Exception as e:
                logging.error(f"Failed to load state: {e}")
                self.state = {"datasets": {}, "last_check": None}
        else:
            self.state = {"datasets": {}, "last_check": None}
            logging.info("Initialized new state file")

    def save_state(self):
        """Save collection state to disk."""
        try:
            self.state["last_check"] = datetime.now(timezone.utc).isoformat()

            with open(self.STATE_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, indent=2, ensure_ascii=False)

            logging.info(f"Saved state to {self.STATE_FILE}")
        except Exception as e:
            logging.error(f"Failed to save state: {e}")

    def calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of a file."""
        sha256_hash = hashlib.sha256()

        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(65536), b""):
                sha256_hash.update(byte_block)

        return sha256_hash.hexdigest()

    def check_zenodo_dataset(self, dataset_id: str, config: Dict) -> Tuple[bool, Dict]:
        """
        Check Zenodo for dataset updates.

        Returns:
            (has_update, metadata)
        """
        doi = config["zenodo_doi"]
        record_id = doi.split(".")[-1]  # Extract record ID from DOI

        try:
            # Query Zenodo API
            url = f"{self.ZENODO_API}{record_id}"
            response = requests.get(url, timeout=30)

            if response.status_code != 200:
                logging.error(f"Zenodo API error for {dataset_id}: HTTP {response.status_code}")
                return False, {}

            data = response.json()

            # Extract version info
            version = data.get("metadata", {}).get("version", "unknown")
            modified = data.get("modified", data.get("created"))
            files_info = data.get("files", [])

            # Check if we have this version
            current_version = self.state.get("datasets", {}).get(dataset_id, {}).get("version")

            if current_version != version:
                logging.info(f"✨ New version found for {dataset_id}: {current_version} → {version}")
                return True, {
                    "version": version,
                    "modified": modified,
                    "files": files_info,
                    "doi": doi,
                    "record_id": record_id
                }
            else:
                logging.info(f"✓ {dataset_id} is up to date (version: {version})")
                return False, {}

        except Exception as e:
            logging.error(f"Error checking Zenodo dataset {dataset_id}: {e}")
            return False, {}

    def download_zenodo_files(self, dataset_id: str, config: Dict, metadata: Dict) -> List[Path]:
        """Download files from Zenodo."""
        downloaded_files = []
        record_id = metadata["record_id"]

        try:
            # Get download URLs from Zenodo API
            url = f"{self.ZENODO_API}{record_id}"
            response = requests.get(url, timeout=30)
            data = response.json()

            files_info = data.get("files", [])

            for file_info in files_info:
                filename = file_info.get("key")
                download_url = file_info.get("links", {}).get("self")

                if not download_url:
                    logging.warning(f"No download URL for {filename}")
                    continue

                # Create version-specific directory
                version_dir = self.DOWNLOADS_DIR / dataset_id / metadata["version"]
                version_dir.mkdir(parents=True, exist_ok=True)

                output_path = version_dir / filename

                # Download file
                logging.info(f"Downloading {filename} from Zenodo...")
                file_response = requests.get(download_url, stream=True, timeout=60)

                if file_response.status_code == 200:
                    with open(output_path, 'wb') as f:
                        for chunk in file_response.iter_content(chunk_size=8192):
                            f.write(chunk)

                    # Calculate checksum
                    checksum = self.calculate_checksum(output_path)

                    downloaded_files.append(output_path)
                    logging.info(f"✓ Downloaded {filename} (checksum: {checksum[:16]}...)")

                    # Store in state
                    if dataset_id not in self.state["datasets"]:
                        self.state["datasets"][dataset_id] = {}

                    if "files" not in self.state["datasets"][dataset_id]:
                        self.state["datasets"][dataset_id]["files"] = {}

                    self.state["datasets"][dataset_id]["files"][filename] = {
                        "checksum": checksum,
                        "downloaded": datetime.now(timezone.utc).isoformat(),
                        "size": output_path.stat().st_size,
                        "path": str(output_path)
                    }
                else:
                    logging.error(f"Failed to download {filename}: HTTP {file_response.status_code}")

            # Update dataset version in state
            self.state["datasets"][dataset_id]["version"] = metadata["version"]
            self.state["datasets"][dataset_id]["modified"] = metadata["modified"]
            self.state["datasets"][dataset_id]["source"] = "zenodo"

            return downloaded_files

        except Exception as e:
            logging.error(f"Error downloading Zenodo files for {dataset_id}: {e}")
            return []

    def check_github_dataset(self, dataset_id: str, config: Dict) -> Tuple[bool, Dict]:
        """
        Check GitHub repository for dataset updates.

        Returns:
            (has_update, metadata)
        """
        repo = config["github_repo"]
        path = config.get("github_path", "")

        try:
            # Get repository info
            repo_url = f"{self.GITHUB_API}/repos/{repo}"
            response = requests.get(repo_url, timeout=30)

            if response.status_code != 200:
                logging.error(f"GitHub API error for {dataset_id}: HTTP {response.status_code}")
                return False, {}

            repo_data = response.json()
            last_commit = repo_data.get("pushed_at")

            # Get contents of data directory
            contents_url = f"{self.GITHUB_API}/repos/{repo}/contents/{path}"
            contents_response = requests.get(contents_url, timeout=30)

            if contents_response.status_code != 200:
                logging.error(f"GitHub contents API error: HTTP {contents_response.status_code}")
                return False, {}

            files_info = contents_response.json()

            # Check if last_commit is different
            current_commit = self.state.get("datasets", {}).get(dataset_id, {}).get("last_commit")

            if current_commit != last_commit:
                logging.info(f"✨ New commit found for {dataset_id}: {current_commit} → {last_commit}")
                return True, {
                    "last_commit": last_commit,
                    "files": files_info,
                    "repo": repo,
                    "path": path
                }
            else:
                logging.info(f"✓ {dataset_id} is up to date (last commit: {last_commit})")
                return False, {}

        except Exception as e:
            logging.error(f"Error checking GitHub dataset {dataset_id}: {e}")
            return False, {}

    def download_github_files(self, dataset_id: str, config: Dict, metadata: Dict) -> List[Path]:
        """Download files from GitHub."""
        downloaded_files = []

        try:
            files_info = metadata["files"]
            repo = metadata["repo"]

            # Create commit-specific directory
            commit_short = metadata["last_commit"][:10]
            version_dir = self.DOWNLOADS_DIR / dataset_id / commit_short
            version_dir.mkdir(parents=True, exist_ok=True)

            for file_info in files_info:
                if file_info["type"] != "file":
                    continue

                filename = file_info["name"]
                download_url = file_info["download_url"]

                output_path = version_dir / filename

                # Download file
                logging.info(f"Downloading {filename} from GitHub...")
                response = requests.get(download_url, stream=True, timeout=60)

                if response.status_code == 200:
                    with open(output_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)

                    # Calculate checksum
                    checksum = self.calculate_checksum(output_path)

                    downloaded_files.append(output_path)
                    logging.info(f"✓ Downloaded {filename} (checksum: {checksum[:16]}...)")

                    # Store in state
                    if dataset_id not in self.state["datasets"]:
                        self.state["datasets"][dataset_id] = {}

                    if "files" not in self.state["datasets"][dataset_id]:
                        self.state["datasets"][dataset_id]["files"] = {}

                    self.state["datasets"][dataset_id]["files"][filename] = {
                        "checksum": checksum,
                        "downloaded": datetime.now(timezone.utc).isoformat(),
                        "size": output_path.stat().st_size,
                        "path": str(output_path)
                    }
                else:
                    logging.error(f"Failed to download {filename}: HTTP {response.status_code}")

            # Update dataset commit in state
            self.state["datasets"][dataset_id]["last_commit"] = metadata["last_commit"]
            self.state["datasets"][dataset_id]["source"] = "github"

            return downloaded_files

        except Exception as e:
            logging.error(f"Error downloading GitHub files for {dataset_id}: {e}")
            return []

    def check_and_download_dataset(self, dataset_id: str, config: Dict) -> bool:
        """Check for updates and download if needed."""
        source_type = config["source_type"]

        logging.info(f"\n{'='*60}")
        logging.info(f"Checking: {config['name']}")
        logging.info(f"Source: {source_type}")
        logging.info(f"{'='*60}")

        has_update = False
        metadata = {}

        # Check for updates based on source type
        if source_type == "zenodo":
            has_update, metadata = self.check_zenodo_dataset(dataset_id, config)
        elif source_type == "github":
            has_update, metadata = self.check_github_dataset(dataset_id, config)
        else:
            logging.warning(f"Unknown source type: {source_type}")
            return False

        # Download if update found
        if has_update:
            logging.info(f"📥 Downloading updated dataset: {config['name']}")

            if source_type == "zenodo":
                files = self.download_zenodo_files(dataset_id, config, metadata)
            elif source_type == "github":
                files = self.download_github_files(dataset_id, config, metadata)
            else:
                files = []

            if files:
                self.downloads_made.extend(files)
                self.updates_found.append({
                    "dataset_id": dataset_id,
                    "name": config["name"],
                    "files": len(files),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
                logging.info(f"✅ Successfully downloaded {len(files)} files for {config['name']}")
                return True
            else:
                logging.error(f"❌ Failed to download files for {config['name']}")
                return False

        return False

    def run_collection(self):
        """Run complete collection cycle."""
        logging.info("\n" + "="*60)
        logging.info("ETO Dataset Collection - Starting")
        logging.info("="*60 + "\n")

        start_time = time.time()

        # Check each dataset
        for dataset_id, config in self.DATASETS.items():
            try:
                self.check_and_download_dataset(dataset_id, config)
                time.sleep(2)  # Rate limiting
            except Exception as e:
                logging.error(f"Error processing {dataset_id}: {e}")

        # Save state
        self.save_state()

        # Generate report
        elapsed = time.time() - start_time

        logging.info("\n" + "="*60)
        logging.info("ETO Dataset Collection - Complete")
        logging.info("="*60)
        logging.info(f"Duration: {elapsed:.1f} seconds")
        logging.info(f"Updates found: {len(self.updates_found)}")
        logging.info(f"Files downloaded: {len(self.downloads_made)}")

        if self.updates_found:
            logging.info("\nUpdated Datasets:")
            for update in self.updates_found:
                logging.info(f"  - {update['name']}: {update['files']} files")

        # Save run report
        report_file = self.BASE_DIR / f"run_report_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "duration_seconds": elapsed,
                "updates_found": self.updates_found,
                "files_downloaded": [str(f) for f in self.downloads_made]
            }, f, indent=2)

        logging.info(f"\nReport saved to: {report_file}")

    def get_status(self) -> Dict:
        """Get current collection status."""
        status = {
            "last_check": self.state.get("last_check"),
            "datasets": {}
        }

        for dataset_id, config in self.DATASETS.items():
            dataset_state = self.state.get("datasets", {}).get(dataset_id, {})

            status["datasets"][dataset_id] = {
                "name": config["name"],
                "source": config["source_type"],
                "version": dataset_state.get("version") or dataset_state.get("last_commit", "not_downloaded"),
                "last_modified": dataset_state.get("modified") or dataset_state.get("last_commit"),
                "files": len(dataset_state.get("files", {})),
                "update_frequency": config["update_frequency"]
            }

        return status


def main():
    """Main entry point."""
    collector = ETODatasetCollector()

    # Run collection
    collector.run_collection()

    # Print status
    print("\n" + "="*60)
    print("Current Status:")
    print("="*60)
    status = collector.get_status()
    print(json.dumps(status, indent=2))


if __name__ == "__main__":
    main()

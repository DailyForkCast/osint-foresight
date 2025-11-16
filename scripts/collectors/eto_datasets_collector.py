#!/usr/bin/env python3
"""
ETO Datasets Collector - Emerging Technology Observatory
Weekly collection of strategic technology datasets

Monitors and downloads from:
- Zenodo (Country AI Metrics, Private Sector AI, etc.)
- GitHub (Semiconductor Supply Chain, etc.)
- ETO Website (AGORA, OpenAlex Overlay, etc.)
"""

import json
import hashlib
import requests
import logging
import time
import os
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

# Setup logging
LOG_DIR = Path("F:/ETO_Datasets/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / f"eto_collection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# Configuration
ROOT_DIR = Path("F:/ETO_Datasets")
STATE_FILE = ROOT_DIR / "STATE" / "eto_state.json"
LOCK_FILE = ROOT_DIR / "STATE" / "eto_state.lock"
CONFIG_FILE = ROOT_DIR / "STATE" / "eto_datasets_config.json"

# ETO Dataset Registry
DATASETS_CONFIG = {
    "country_ai_metrics": {
        "name": "Country AI Activity Metrics",
        "source": "zenodo",
        "zenodo_doi": "10.5281/zenodo.13984221",
        "zenodo_record_id": "13984221",
        "update_frequency": "monthly",
        "description": "National-level metrics for AI research, patents, and investment",
        "expected_files": [
            "publications_yearly_articles.csv",
            "publications_yearly_citations.csv",
            "publications_summary.csv",
            "patents_yearly_applications.csv",
            "patents_yearly_granted.csv",
            "patents_summary.csv",
            "companies_yearly_disclosed.csv",
            "companies_yearly_estimated.csv",
            "companies_summary.csv"
        ]
    },
    "semiconductor_supply_chain": {
        "name": "Advanced Semiconductor Supply Chain",
        "source": "github",
        "github_repo": "georgetown-cset/eto-supply-chain",
        "github_branch": "main",
        "github_path": "data",
        "update_frequency": "periodic",
        "description": "Supply chain data for advanced logic chip production",
        "expected_files": [
            "inputs.csv",
            "providers.csv",
            "provision.csv",
            "sequence.csv",
            "stages.csv"
        ]
    },
    "cross_border_research": {
        "name": "Cross-Border Tech Research Metrics",
        "source": "zenodo",
        "zenodo_doi": "10.5281/zenodo.14510656",
        "zenodo_record_id": "14510656",
        "update_frequency": "periodic",
        "description": "Cross-border collaboration in AI, robotics, cybersecurity",
        "expected_files": ["cross_border_research_metrics.csv"]
    },
    "private_sector_ai": {
        "name": "Private-Sector AI Indicators",
        "source": "zenodo",
        "zenodo_doi": "10.5281/zenodo.14194293",
        "zenodo_record_id": "14194293",
        "update_frequency": "periodic",
        "description": "AI activity indicators for companies worldwide",
        "expected_files": ["private_sector_ai_indicators.csv"]
    },
    "agora_ai_governance": {
        "name": "AGORA AI Governance Dataset",
        "source": "zenodo",
        "zenodo_doi": "10.5281/zenodo.14291866",
        "zenodo_record_id": "14291866",
        "update_frequency": "frequent",
        "description": "AI laws, regulations, and governance documents",
        "expected_files": ["agora_documents.csv", "agora_metadata.csv"]
    },
    "openalex_overlay": {
        "name": "ETO OpenAlex Overlay",
        "source": "zenodo",
        "zenodo_doi": "10.5281/zenodo.14237445",
        "zenodo_record_id": "14237445",
        "update_frequency": "periodic",
        "description": "Emerging tech classifications for OpenAlex works",
        "expected_files": ["openalex_emerging_tech_labels.csv"]
    }
}


class StateLockError(Exception):
    """Raised when state file lock cannot be acquired"""
    pass


class StateManager:
    """Manages incremental collection state with file locking"""

    def __init__(self):
        self.state = None
        self.lock_acquired = False

    def acquire_lock(self, timeout: int = 30):
        """Acquire exclusive lock on state file"""
        wait_time = 0
        while LOCK_FILE.exists() and wait_time < timeout:
            logger.warning(f"State file locked, waiting... ({wait_time}s)")
            time.sleep(1)
            wait_time += 1

        if LOCK_FILE.exists():
            raise StateLockError(f"Could not acquire lock after {timeout}s")

        # Create lock file
        LOCK_FILE.write_text(json.dumps({
            "locked_at": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid()
        }, indent=2))

        self.lock_acquired = True
        logger.info("State lock acquired")

    def release_lock(self):
        """Release state file lock"""
        if LOCK_FILE.exists():
            LOCK_FILE.unlink()
        self.lock_acquired = False
        logger.info("State lock released")

    def load_state(self) -> Dict:
        """Load state from file, initialize if missing"""
        if not STATE_FILE.exists():
            logger.warning("State file not found, initializing...")
            self.state = self._initialize_state()
            self.save_state()
        else:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                self.state = json.load(f)

        logger.info(f"State loaded: version {self.state.get('version')}")
        return self.state

    def save_state(self):
        """Save state atomically"""
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

        temp_file = STATE_FILE.with_suffix('.tmp')
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)

        # Atomic rename
        temp_file.replace(STATE_FILE)
        logger.info("State saved successfully")

    def _initialize_state(self) -> Dict:
        """Initialize fresh state"""
        return {
            "version": "1.0",
            "last_check": None,
            "datasets": {}
        }


class ETOCollector:
    """Main ETO datasets collector"""

    ZENODO_API = "https://zenodo.org/api/records/"
    GITHUB_API = "https://api.github.com"

    def __init__(self):
        self.state_manager = StateManager()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ETO-Dataset-Collector/1.0 (OSINT-Foresight; Research; +https://github.com/osint-foresight)'
        })

        self.downloads_made = []
        self.updates_found = []

        # Create directory structure
        self.downloads_dir = ROOT_DIR / "downloads"
        self.merged_dir = ROOT_DIR / "MERGED"
        self.qa_dir = ROOT_DIR / "QA"

        for dir_path in [self.downloads_dir, self.merged_dir, self.qa_dir, LOG_DIR]:
            dir_path.mkdir(parents=True, exist_ok=True)

    def calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(65536), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def check_zenodo_update(self, dataset_id: str, config: Dict) -> Tuple[bool, Dict]:
        """Check Zenodo for dataset updates"""
        record_id = config["zenodo_record_id"]

        try:
            url = f"{self.ZENODO_API}{record_id}"
            response = self.session.get(url, timeout=30)

            if response.status_code != 200:
                logger.error(f"Zenodo API error for {dataset_id}: HTTP {response.status_code}")
                return False, {}

            data = response.json()

            version = data.get("metadata", {}).get("version", "unknown")
            modified = data.get("modified", data.get("created"))
            files_info = data.get("files", [])

            # Check if we have this version
            current_version = self.state_manager.state.get("datasets", {}).get(dataset_id, {}).get("version")

            if current_version != version:
                logger.info(f"✨ New version found for {dataset_id}: {current_version} → {version}")
                return True, {
                    "version": version,
                    "modified": modified,
                    "files": files_info,
                    "doi": config["zenodo_doi"],
                    "record_id": record_id
                }
            else:
                logger.info(f"✓ {dataset_id} is up to date (version: {version})")
                return False, {}

        except Exception as e:
            logger.error(f"Error checking Zenodo dataset {dataset_id}: {e}")
            return False, {}

    def download_zenodo_files(self, dataset_id: str, config: Dict, metadata: Dict) -> List[Path]:
        """Download files from Zenodo"""
        downloaded_files = []
        record_id = metadata["record_id"]

        try:
            url = f"{self.ZENODO_API}{record_id}"
            response = self.session.get(url, timeout=30)
            data = response.json()
            files_info = data.get("files", [])

            # Create version-specific directory
            version = metadata["version"]
            version_dir = self.downloads_dir / dataset_id / version
            version_dir.mkdir(parents=True, exist_ok=True)

            for file_info in files_info:
                filename = file_info.get("key")
                download_url = file_info.get("links", {}).get("self")

                if not download_url:
                    logger.warning(f"No download URL for {filename}")
                    continue

                output_path = version_dir / filename

                logger.info(f"📥 Downloading {filename}...")
                file_response = self.session.get(download_url, stream=True, timeout=60)

                if file_response.status_code == 200:
                    with open(output_path, 'wb') as f:
                        for chunk in file_response.iter_content(chunk_size=8192):
                            f.write(chunk)

                    checksum = self.calculate_checksum(output_path)
                    downloaded_files.append(output_path)

                    logger.info(f"✓ Downloaded {filename} ({output_path.stat().st_size} bytes)")
                    logger.info(f"  Checksum: {checksum[:16]}...")

                    # Store in state
                    if dataset_id not in self.state_manager.state["datasets"]:
                        self.state_manager.state["datasets"][dataset_id] = {}

                    if "files" not in self.state_manager.state["datasets"][dataset_id]:
                        self.state_manager.state["datasets"][dataset_id]["files"] = {}

                    self.state_manager.state["datasets"][dataset_id]["files"][filename] = {
                        "checksum": checksum,
                        "downloaded": datetime.now(timezone.utc).isoformat(),
                        "size": output_path.stat().st_size,
                        "path": str(output_path)
                    }
                else:
                    logger.error(f"Failed to download {filename}: HTTP {file_response.status_code}")

            # Update dataset version
            self.state_manager.state["datasets"][dataset_id]["version"] = version
            self.state_manager.state["datasets"][dataset_id]["modified"] = metadata["modified"]
            self.state_manager.state["datasets"][dataset_id]["source"] = "zenodo"
            self.state_manager.state["datasets"][dataset_id]["doi"] = config["zenodo_doi"]

            return downloaded_files

        except Exception as e:
            logger.error(f"Error downloading Zenodo files for {dataset_id}: {e}")
            return []

    def check_github_update(self, dataset_id: str, config: Dict) -> Tuple[bool, Dict]:
        """Check GitHub repository for updates"""
        repo = config["github_repo"]
        path = config.get("github_path", "")

        try:
            repo_url = f"{self.GITHUB_API}/repos/{repo}"
            response = self.session.get(repo_url, timeout=30)

            if response.status_code != 200:
                logger.error(f"GitHub API error for {dataset_id}: HTTP {response.status_code}")
                return False, {}

            repo_data = response.json()
            last_commit = repo_data.get("pushed_at")

            # Get contents
            contents_url = f"{self.GITHUB_API}/repos/{repo}/contents/{path}"
            contents_response = self.session.get(contents_url, timeout=30)

            if contents_response.status_code != 200:
                logger.error(f"GitHub contents API error: HTTP {contents_response.status_code}")
                return False, {}

            files_info = contents_response.json()

            # Check if commit changed
            current_commit = self.state_manager.state.get("datasets", {}).get(dataset_id, {}).get("last_commit")

            if current_commit != last_commit:
                logger.info(f"✨ New commit found for {dataset_id}")
                return True, {
                    "last_commit": last_commit,
                    "files": files_info,
                    "repo": repo,
                    "path": path
                }
            else:
                logger.info(f"✓ {dataset_id} is up to date (commit: {last_commit[:10]})")
                return False, {}

        except Exception as e:
            logger.error(f"Error checking GitHub dataset {dataset_id}: {e}")
            return False, {}

    def download_github_files(self, dataset_id: str, config: Dict, metadata: Dict) -> List[Path]:
        """Download files from GitHub"""
        downloaded_files = []

        try:
            files_info = metadata["files"]

            # Create commit-specific directory
            commit_short = metadata["last_commit"][:10]
            version_dir = self.downloads_dir / dataset_id / commit_short
            version_dir.mkdir(parents=True, exist_ok=True)

            for file_info in files_info:
                if file_info["type"] != "file":
                    continue

                filename = file_info["name"]
                download_url = file_info["download_url"]
                output_path = version_dir / filename

                logger.info(f"📥 Downloading {filename}...")
                response = self.session.get(download_url, stream=True, timeout=60)

                if response.status_code == 200:
                    with open(output_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)

                    checksum = self.calculate_checksum(output_path)
                    downloaded_files.append(output_path)

                    logger.info(f"✓ Downloaded {filename} ({output_path.stat().st_size} bytes)")
                    logger.info(f"  Checksum: {checksum[:16]}...")

                    # Store in state
                    if dataset_id not in self.state_manager.state["datasets"]:
                        self.state_manager.state["datasets"][dataset_id] = {}

                    if "files" not in self.state_manager.state["datasets"][dataset_id]:
                        self.state_manager.state["datasets"][dataset_id]["files"] = {}

                    self.state_manager.state["datasets"][dataset_id]["files"][filename] = {
                        "checksum": checksum,
                        "downloaded": datetime.now(timezone.utc).isoformat(),
                        "size": output_path.stat().st_size,
                        "path": str(output_path)
                    }
                else:
                    logger.error(f"Failed to download {filename}: HTTP {response.status_code}")

            # Update dataset
            self.state_manager.state["datasets"][dataset_id]["last_commit"] = metadata["last_commit"]
            self.state_manager.state["datasets"][dataset_id]["source"] = "github"
            self.state_manager.state["datasets"][dataset_id]["repo"] = config["github_repo"]

            return downloaded_files

        except Exception as e:
            logger.error(f"Error downloading GitHub files for {dataset_id}: {e}")
            return []

    def check_and_download_dataset(self, dataset_id: str, config: Dict) -> bool:
        """Check for updates and download if needed"""
        logger.info(f"\n{'='*80}")
        logger.info(f"Checking: {config['name']}")
        logger.info(f"Source: {config['source']}")
        logger.info(f"{'='*80}")

        has_update = False
        metadata = {}

        # Check for updates based on source
        if config["source"] == "zenodo":
            has_update, metadata = self.check_zenodo_update(dataset_id, config)
        elif config["source"] == "github":
            has_update, metadata = self.check_github_update(dataset_id, config)
        else:
            logger.warning(f"Unknown source type: {config['source']}")
            return False

        # Download if update found
        if has_update:
            logger.info(f"📥 Downloading updated dataset: {config['name']}")

            if config["source"] == "zenodo":
                files = self.download_zenodo_files(dataset_id, config, metadata)
            elif config["source"] == "github":
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
                logger.info(f"✅ Successfully downloaded {len(files)} files")
                return True
            else:
                logger.error(f"❌ Failed to download files")
                return False

        return False

    def run_collection(self):
        """Run complete weekly collection cycle"""
        logger.info("\n" + "="*80)
        logger.info("ETO Dataset Collection - Starting Weekly Check")
        logger.info("="*80 + "\n")

        start_time = time.time()

        try:
            # Acquire lock
            self.state_manager.acquire_lock()

            # Load state
            self.state_manager.load_state()

            # Check each dataset
            for dataset_id, config in DATASETS_CONFIG.items():
                try:
                    self.check_and_download_dataset(dataset_id, config)
                    time.sleep(2)  # Rate limiting
                except Exception as e:
                    logger.error(f"Error processing {dataset_id}: {e}")

            # Update last check time
            self.state_manager.state["last_check"] = datetime.now(timezone.utc).isoformat()

            # Save state
            self.state_manager.save_state()

            # Import downloaded datasets into database
            if self.downloads_made:
                logger.info("\n" + "="*80)
                logger.info("Importing downloaded datasets into osint_master.db...")
                logger.info("="*80)

                try:
                    from eto_database_integration import ETODatabaseIntegration

                    with ETODatabaseIntegration() as db:
                        db.create_schemas()
                        db.create_indexes()
                        import_stats = db.import_all_datasets(self.downloads_dir)

                        logger.info("\nDatabase Import Complete:")
                        for dataset, tables in import_stats.items():
                            logger.info(f"  {dataset}:")
                            for table, rows in tables.items():
                                logger.info(f"    {table}: {rows:,} rows")

                except Exception as e:
                    logger.error(f"Error importing to database: {e}")
                    logger.error("Data still saved to files, but database import failed")

        finally:
            # Always release lock
            if self.state_manager.lock_acquired:
                self.state_manager.release_lock()

        # Generate report
        elapsed = time.time() - start_time

        logger.info("\n" + "="*80)
        logger.info("ETO Dataset Collection - Complete")
        logger.info("="*80)
        logger.info(f"Duration: {elapsed:.1f} seconds")
        logger.info(f"Updates found: {len(self.updates_found)}")
        logger.info(f"Files downloaded: {len(self.downloads_made)}")

        if self.updates_found:
            logger.info("\nUpdated Datasets:")
            for update in self.updates_found:
                logger.info(f"  - {update['name']}: {update['files']} files")

        # Save run report
        report_file = self.qa_dir / f"run_report_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "duration_seconds": elapsed,
                "updates_found": self.updates_found,
                "files_downloaded": [str(f) for f in self.downloads_made],
                "datasets_checked": len(DATASETS_CONFIG)
            }, f, indent=2)

        logger.info(f"\nReport saved to: {report_file}")


def main():
    """Main entry point"""
    import os

    collector = ETOCollector()
    collector.run_collection()


if __name__ == "__main__":
    main()

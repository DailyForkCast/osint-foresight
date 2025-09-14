#!/usr/bin/env python3
"""
OSINT Foresight Master Data Pull Script
Orchestrates data collection from all configured sources to external drive
"""
import os
import sys
import json
import yaml
import logging
import hashlib
import datetime
from pathlib import Path
from typing import Dict, List, Optional
import subprocess
import time

# Configuration
PROJECT_DIR = Path("C:/Projects/OSINT - Foresight")
EXTERNAL_DATA_DIR = Path("F:/OSINT_Data")
CONFIG_DIR = PROJECT_DIR / "config"
LOG_DIR = EXTERNAL_DATA_DIR / "logs"

# Setup logging
LOG_DIR.mkdir(parents=True, exist_ok=True)
log_file = LOG_DIR / f"data_pull_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DataPullOrchestrator:
    """Master orchestrator for all data pulls"""

    def __init__(self):
        self.config = self.load_configuration()
        self.sources = self.load_sources()
        self.pull_status = {}
        self.timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

    def load_configuration(self) -> Dict:
        """Load pull configuration"""
        config_file = CONFIG_DIR / "pull_configuration.yaml"
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)

    def load_sources(self) -> Dict:
        """Load data sources configuration"""
        sources_file = CONFIG_DIR / "sources.yaml"
        with open(sources_file, 'r') as f:
            return yaml.safe_load(f)

    def check_storage_space(self) -> bool:
        """Check if sufficient storage space available"""
        import shutil
        total, used, free = shutil.disk_usage("F:/")
        free_gb = free / (1024**3)

        logger.info(f"External drive space: {free_gb:.2f} GB free")

        # Require at least 100GB free
        if free_gb < 100:
            logger.error("Insufficient storage space. Need at least 100GB free")
            return False
        return True

    def get_manifest_path(self, source: str, country: Optional[str] = None) -> Path:
        """Get manifest file path for tracking downloads"""
        if country:
            manifest_dir = EXTERNAL_DATA_DIR / "manifests" / f"country={country}"
        else:
            manifest_dir = EXTERNAL_DATA_DIR / "manifests" / "global"

        manifest_dir.mkdir(parents=True, exist_ok=True)
        return manifest_dir / f"{source}_manifest.json"

    def load_manifest(self, source: str, country: Optional[str] = None) -> Dict:
        """Load download manifest for incremental updates"""
        manifest_path = self.get_manifest_path(source, country)

        if manifest_path.exists():
            with open(manifest_path, 'r') as f:
                return json.load(f)
        return {
            "source": source,
            "country": country,
            "last_update": None,
            "files": {},
            "statistics": {}
        }

    def save_manifest(self, manifest: Dict, source: str, country: Optional[str] = None):
        """Save download manifest"""
        manifest_path = self.get_manifest_path(source, country)
        manifest["last_update"] = datetime.datetime.now().isoformat()

        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)

    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file for deduplication"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()

    def pull_crossref_data(self, countries: List[str] = None):
        """Pull Crossref publication and event data"""
        logger.info("Starting Crossref data pull")

        # Import the crossref puller
        script_path = PROJECT_DIR / "scripts" / "data_pull" / "pull_crossref.py"

        if not countries:
            countries = self.get_priority_countries(priority=1)

        for country in countries:
            logger.info(f"Pulling Crossref data for {country}")

            # Check manifest for last pull
            manifest = self.load_manifest("crossref", country)

            # Run the pull script
            since_date = manifest.get("last_update", "2024-01-01") if manifest.get("last_update") else "2024-01-01"
            cmd = [
                sys.executable,
                str(script_path),
                "--country", country,
                "--output", str(EXTERNAL_DATA_DIR / f"country={country}" / "crossref"),
                "--since", since_date
            ]

            try:
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                logger.info(f"Crossref pull for {country} completed")

                # Update manifest
                manifest["statistics"]["last_pull_count"] = len(result.stdout.split('\n'))
                self.save_manifest(manifest, "crossref", country)

            except subprocess.CalledProcessError as e:
                logger.error(f"Crossref pull for {country} failed: {e.stderr}")

    def pull_cordis_data(self):
        """Pull CORDIS EU project data"""
        logger.info("Starting CORDIS data pull")

        output_dir = EXTERNAL_DATA_DIR / "cordis"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Check if we already have recent data
        manifest = self.load_manifest("cordis")

        if manifest.get("last_update"):
            last_update = datetime.datetime.fromisoformat(manifest["last_update"])
            if (datetime.datetime.now() - last_update).days < 30:
                logger.info("CORDIS data is recent (< 30 days old), skipping")
                return

        # Pull CORDIS data
        script_path = PROJECT_DIR / "scripts" / "data_pull" / "pull_cordis.py"

        cmd = [
            sys.executable,
            str(script_path),
            "--output", str(output_dir)
        ]

        try:
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.info("CORDIS pull completed")

            # Update manifest
            self.save_manifest(manifest, "cordis")

        except subprocess.CalledProcessError as e:
            logger.error(f"CORDIS pull failed: {e.stderr}")

    def pull_worldbank_indicators(self, countries: List[str] = None):
        """Pull World Bank indicators"""
        logger.info("Starting World Bank indicators pull")

        if not countries:
            countries = self.get_all_countries()

        script_path = PROJECT_DIR / "scripts" / "data_pull" / "pull_worldbank.py"

        for country in countries:
            output_dir = EXTERNAL_DATA_DIR / f"country={country}" / "worldbank"
            output_dir.mkdir(parents=True, exist_ok=True)

            manifest = self.load_manifest("worldbank", country)

            cmd = [
                sys.executable,
                str(script_path),
                "--country", country,
                "--output", str(output_dir)
            ]

            try:
                subprocess.run(cmd, capture_output=True, text=True, check=True)
                logger.info(f"World Bank pull for {country} completed")
                self.save_manifest(manifest, "worldbank", country)

            except subprocess.CalledProcessError as e:
                logger.error(f"World Bank pull for {country} failed: {e.stderr}")

    def pull_patent_data(self, countries: List[str] = None):
        """Pull patent data from Google BigQuery"""
        logger.info("Starting patent data pull")

        if not countries:
            countries = self.get_priority_countries(priority=1)

        script_path = PROJECT_DIR / "scripts" / "data_pull" / "pull_patents.py"

        for country in countries:
            output_dir = EXTERNAL_DATA_DIR / f"country={country}" / "patents"
            output_dir.mkdir(parents=True, exist_ok=True)

            manifest = self.load_manifest("patents", country)

            # Check if we have recent data
            if manifest.get("last_update"):
                last_update = datetime.datetime.fromisoformat(manifest["last_update"])
                if (datetime.datetime.now() - last_update).days < 90:
                    logger.info(f"Patent data for {country} is recent, skipping")
                    continue

            cmd = [
                sys.executable,
                str(script_path),
                "--country", country,
                "--output", str(output_dir),
                "--limit", "10000"  # Limit for initial pulls
            ]

            try:
                subprocess.run(cmd, capture_output=True, text=True, check=True)
                logger.info(f"Patent pull for {country} completed")
                self.save_manifest(manifest, "patents", country)

            except subprocess.CalledProcessError as e:
                logger.error(f"Patent pull for {country} failed: {e.stderr}")

    def pull_github_activity(self, countries: List[str] = None):
        """Pull GitHub activity data for countries"""
        logger.info("Starting GitHub activity pull")

        if not countries:
            countries = self.get_priority_countries(priority=1)

        script_path = PROJECT_DIR / "scripts" / "data_pull" / "pull_github.py"

        for country in countries:
            output_dir = EXTERNAL_DATA_DIR / f"country={country}" / "github"
            output_dir.mkdir(parents=True, exist_ok=True)

            manifest = self.load_manifest("github", country)

            cmd = [
                sys.executable,
                str(script_path),
                "--country", country,
                "--output", str(output_dir),
                "--since", manifest.get("last_update", "2024-01-01")
            ]

            try:
                subprocess.run(cmd, capture_output=True, text=True, check=True)
                logger.info(f"GitHub pull for {country} completed")
                self.save_manifest(manifest, "github", country)

            except subprocess.CalledProcessError as e:
                logger.error(f"GitHub pull for {country} failed: {e.stderr}")

    def get_priority_countries(self, priority: int) -> List[str]:
        """Get countries by priority level"""
        countries = []
        for country, config in self.config.get("countries", {}).items():
            if config.get("priority") == priority:
                countries.append(country)
        return countries

    def get_all_countries(self) -> List[str]:
        """Get all configured countries"""
        return list(self.config.get("countries", {}).keys())

    def run_daily_pulls(self):
        """Run all daily data pulls"""
        logger.info("Starting daily data pulls")

        if not self.check_storage_space():
            return

        # Priority 1 countries - pull everything
        priority_1 = self.get_priority_countries(priority=1)

        # Daily sources
        daily_sources = self.config["frequencies"]["daily"]

        for source in daily_sources:
            if source == "patent_filings":
                self.pull_patent_data(priority_1)
            elif source == "regulatory_updates":
                # Add regulatory pull when implemented
                pass

        logger.info("Daily pulls completed")

    def run_weekly_pulls(self):
        """Run all weekly data pulls"""
        logger.info("Starting weekly data pulls")

        if not self.check_storage_space():
            return

        # All countries for weekly pulls
        all_countries = self.get_all_countries()

        # Weekly sources
        weekly_sources = self.config["frequencies"]["weekly"]

        for source in weekly_sources:
            if source == "crossref_publications":
                self.pull_crossref_data(all_countries[:10])  # Start with first 10
            elif source == "github_activity":
                self.pull_github_activity(all_countries[:10])
            elif source == "standards_updates":
                # Add standards pull when implemented
                pass

        logger.info("Weekly pulls completed")

    def run_monthly_pulls(self):
        """Run all monthly data pulls"""
        logger.info("Starting monthly data pulls")

        if not self.check_storage_space():
            return

        # Monthly sources
        monthly_sources = self.config["frequencies"]["monthly"]

        for source in monthly_sources:
            if source == "cordis_projects":
                self.pull_cordis_data()
            elif source == "worldbank_indicators":
                self.pull_worldbank_indicators(self.get_all_countries()[:20])
            # Add other monthly sources

        logger.info("Monthly pulls completed")

    def generate_pull_report(self) -> str:
        """Generate summary report of data pulls"""
        report = []
        report.append(f"Data Pull Report - {self.timestamp}")
        report.append("=" * 60)

        # Check all manifests
        manifest_dir = EXTERNAL_DATA_DIR / "manifests"
        if manifest_dir.exists():
            for manifest_file in manifest_dir.rglob("*_manifest.json"):
                with open(manifest_file, 'r') as f:
                    manifest = json.load(f)

                source = manifest.get("source", "unknown")
                country = manifest.get("country", "global")
                last_update = manifest.get("last_update", "never")

                report.append(f"{source:20} {country:10} Last: {last_update}")

        report.append("=" * 60)

        # Check storage usage
        import shutil
        total, used, free = shutil.disk_usage("F:/")

        report.append(f"Storage: {used/(1024**3):.2f} GB used, {free/(1024**3):.2f} GB free")

        return "\n".join(report)

    def run_test_pull(self):
        """Run a test pull with minimal data"""
        logger.info("Running test data pull")

        if not self.check_storage_space():
            return

        # Test with one country
        test_countries = ["AT"]  # Austria as test

        logger.info("Testing Crossref pull...")
        self.pull_crossref_data(test_countries)

        logger.info("Testing World Bank pull...")
        self.pull_worldbank_indicators(test_countries)

        logger.info("Test pull completed")

        # Generate report
        report = self.generate_pull_report()
        logger.info(f"\n{report}")

        # Save report
        report_file = EXTERNAL_DATA_DIR / "reports" / f"pull_report_{self.timestamp}.txt"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        report_file.write_text(report)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="OSINT Foresight Data Pull Orchestrator")
    parser.add_argument("--mode", choices=["test", "daily", "weekly", "monthly", "full"],
                      default="test", help="Pull mode")
    parser.add_argument("--countries", nargs="+", help="Specific countries to pull")

    args = parser.parse_args()

    orchestrator = DataPullOrchestrator()

    if args.mode == "test":
        orchestrator.run_test_pull()
    elif args.mode == "daily":
        orchestrator.run_daily_pulls()
    elif args.mode == "weekly":
        orchestrator.run_weekly_pulls()
    elif args.mode == "monthly":
        orchestrator.run_monthly_pulls()
    elif args.mode == "full":
        orchestrator.run_daily_pulls()
        orchestrator.run_weekly_pulls()
        orchestrator.run_monthly_pulls()

    # Generate final report
    report = orchestrator.generate_pull_report()
    print(f"\n{report}")


if __name__ == "__main__":
    main()

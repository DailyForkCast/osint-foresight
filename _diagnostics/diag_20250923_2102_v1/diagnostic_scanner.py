#!/usr/bin/env python3
"""
Full Project Diagnostic & Data Readiness Audit v1.2
Session ID: diag_20250923_2102_v1
"""

import os
import json
import hashlib
import csv
import sqlite3
import gzip
import zipfile
import tarfile
from datetime import datetime
from pathlib import Path
from collections import defaultdict, Counter
import chardet
import re
from typing import Dict, List, Tuple, Any, Optional
import logging

# Session configuration
SESSION_CONFIG = {
    "SESSION_ID": "diag_20250923_2102_v1",
    "ROOT_DIR": "C:/Projects/OSINT - Foresight",
    "OUTPUT_DIR": "C:/Projects/OSINT - Foresight/_diagnostics/diag_20250923_2102_v1",
    "TIMEFRAME_REFERENCE": "2010-present",
    "DEFAULT_ENCODINGS": ["utf-8", "utf-8-sig", "latin-1"],
    "LOCALE_LANGS": ["en", "it", "de", "fr", "es", "nl", "zh", "el", "bg", "pt"],
    "MAX_SCAN_BYTES_PER_FILE": 32 * 1024 * 1024,  # 32MB
    "DRY_RUN": False
}

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"{SESSION_CONFIG['OUTPUT_DIR']}/diagnostic.log"),
        logging.StreamHandler()
    ]
)

class DiagnosticScanner:
    def __init__(self):
        self.session_id = SESSION_CONFIG["SESSION_ID"]
        self.root_dir = Path(SESSION_CONFIG["ROOT_DIR"])
        self.output_dir = Path(SESSION_CONFIG["OUTPUT_DIR"])
        self.results = {
            "session": SESSION_CONFIG,
            "timestamp": datetime.now().isoformat(),
            "inventory": {},
            "dataset_manifest": [],
            "quality_scores": {},
            "joinability_matrix": {},
            "coverage_analysis": {},
            "entity_registry": {},
            "technology_registry": {},
            "zero_evidence_probes": [],
            "governance": {},
            "warnings": []
        }

    def compute_file_hash(self, filepath: Path) -> str:
        """Compute SHA-256 hash of file"""
        sha256_hash = hashlib.sha256()
        try:
            with open(filepath, "rb") as f:
                for byte_block in iter(lambda: f.read(65536), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            logging.warning(f"Could not hash {filepath}: {e}")
            return "ERROR"

    def detect_encoding(self, filepath: Path) -> str:
        """Detect file encoding"""
        try:
            with open(filepath, 'rb') as f:
                raw = f.read(10000)
                result = chardet.detect(raw)
                return result['encoding'] or 'utf-8'
        except:
            return 'utf-8'

    def scan_directory(self, path: Path) -> Dict:
        """Recursively scan directory structure"""
        inventory = {
            "path": str(path),
            "files": [],
            "directories": {},
            "stats": {
                "total_files": 0,
                "total_size_bytes": 0,
                "file_types": Counter(),
                "encodings": Counter()
            }
        }

        try:
            for item in path.iterdir():
                if item.is_file():
                    file_info = self.analyze_file(item)
                    inventory["files"].append(file_info)
                    inventory["stats"]["total_files"] += 1
                    inventory["stats"]["total_size_bytes"] += file_info["size_bytes"]
                    inventory["stats"]["file_types"][file_info["extension"]] += 1
                    inventory["stats"]["encodings"][file_info.get("encoding", "unknown")] += 1

                elif item.is_dir() and not item.name.startswith('.'):
                    # Skip hidden directories
                    sub_inventory = self.scan_directory(item)
                    inventory["directories"][item.name] = sub_inventory

        except Exception as e:
            logging.error(f"Error scanning {path}: {e}")
            inventory["error"] = str(e)

        return inventory

    def analyze_file(self, filepath: Path) -> Dict:
        """Analyze individual file"""
        file_info = {
            "name": filepath.name,
            "path": str(filepath),
            "size_bytes": filepath.stat().st_size,
            "modified": datetime.fromtimestamp(filepath.stat().st_mtime).isoformat(),
            "extension": filepath.suffix.lower(),
            "hash": self.compute_file_hash(filepath) if filepath.stat().st_size < 100*1024*1024 else "LARGE_FILE"
        }

        # Detect data files
        if filepath.suffix.lower() in ['.csv', '.tsv', '.json', '.jsonl', '.xml', '.parquet', '.db', '.sqlite']:
            file_info["encoding"] = self.detect_encoding(filepath)
            file_info["profile"] = self.profile_data_file(filepath)

        # Detect archives
        elif filepath.suffix.lower() in ['.zip', '.gz', '.tar', '.7z', '.rar']:
            file_info["archive_info"] = self.analyze_archive(filepath)

        return file_info

    def profile_data_file(self, filepath: Path) -> Dict:
        """Profile data file structure and content"""
        profile = {
            "type": filepath.suffix.lower(),
            "row_count": 0,
            "columns": [],
            "sample_rows": []
        }

        try:
            if filepath.suffix.lower() in ['.csv', '.tsv']:
                delimiter = '\t' if filepath.suffix.lower() == '.tsv' else ','
                encoding = self.detect_encoding(filepath)

                with open(filepath, 'r', encoding=encoding, errors='ignore') as f:
                    reader = csv.reader(f, delimiter=delimiter)
                    headers = next(reader, None)
                    if headers:
                        profile["columns"] = headers

                    for i, row in enumerate(reader):
                        profile["row_count"] += 1
                        if i < 3:  # Sample first 3 rows
                            profile["sample_rows"].append(row[:5])  # First 5 columns only

            elif filepath.suffix.lower() == '.json':
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        profile["row_count"] = len(data)
                        if data:
                            profile["columns"] = list(data[0].keys()) if isinstance(data[0], dict) else []
                    elif isinstance(data, dict):
                        profile["columns"] = list(data.keys())
                        profile["row_count"] = 1

            elif filepath.suffix.lower() in ['.db', '.sqlite']:
                conn = sqlite3.connect(filepath)
                cursor = conn.cursor()
                tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
                profile["tables"] = []
                for table in tables:
                    table_name = table[0]
                    count = cursor.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
                    profile["tables"].append({"name": table_name, "row_count": count})
                conn.close()

        except Exception as e:
            profile["error"] = str(e)

        return profile

    def analyze_archive(self, filepath: Path) -> Dict:
        """Analyze archive contents"""
        archive_info = {
            "type": filepath.suffix.lower(),
            "file_count": 0,
            "total_size": 0,
            "contents": []
        }

        try:
            if filepath.suffix.lower() == '.zip':
                with zipfile.ZipFile(filepath, 'r') as zf:
                    for info in zf.filelist:
                        archive_info["file_count"] += 1
                        archive_info["total_size"] += info.file_size
                        archive_info["contents"].append(info.filename)

            elif filepath.suffix.lower() == '.gz':
                archive_info["compressed_size"] = filepath.stat().st_size

        except Exception as e:
            archive_info["error"] = str(e)

        return archive_info

    def identify_china_patterns(self, text: str) -> List[str]:
        """Identify China-related patterns in text"""
        china_patterns = [
            # Companies
            r'huawei', r'xiaomi', r'alibaba', r'tencent', r'baidu', r'bytedance',
            r'zte', r'lenovo', r'dji', r'byd', r'geely', r'haier',
            # Institutions
            r'tsinghua', r'peking university', r'fudan', r'chinese academy',
            r'cas\b', r'cnpc', r'sinopec', r'state grid',
            # General terms
            r'china', r'chinese', r'beijing', r'shanghai', r'shenzhen',
            r'prc\b', r"people's republic", r'中国', r'中文'
        ]

        found = []
        text_lower = text.lower()
        for pattern in china_patterns:
            if re.search(pattern, text_lower):
                found.append(pattern)

        return found

    def run_zero_evidence_probe(self, query: str, locations: List[Path]) -> Dict:
        """Run zero-evidence probe for specific query"""
        probe_result = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "locations_searched": len(locations),
            "matches_found": 0,
            "match_locations": [],
            "variants_tested": []
        }

        # Generate query variants
        variants = [
            query.lower(),
            query.upper(),
            query.replace(' ', '_'),
            query.replace(' ', '-'),
            query.replace(' ', '')
        ]
        probe_result["variants_tested"] = variants

        for location in locations:
            if location.exists() and location.is_file():
                try:
                    content = location.read_text(encoding='utf-8', errors='ignore')
                    for variant in variants:
                        if variant in content.lower():
                            probe_result["matches_found"] += 1
                            probe_result["match_locations"].append({
                                "file": str(location),
                                "variant": variant
                            })
                            break
                except:
                    pass

        return probe_result

    def generate_readiness_scores(self) -> Dict:
        """Generate data readiness scores"""
        scores = {
            "overall": 0,
            "data_coverage": 0,
            "data_quality": 0,
            "joinability": 0,
            "china_intelligence": 0,
            "confidence_band": "low",
            "support": {
                "datasets": 0,
                "rows": 0,
                "concentration_gini": 0
            }
        }

        # Calculate based on inventory
        if self.results["inventory"]:
            total_files = sum([inv["stats"]["total_files"]
                             for inv in self.results["inventory"].values()])
            data_files = sum([len([f for f in inv["files"]
                              if f["extension"] in ['.csv', '.json', '.db', '.tsv', '.xml']])
                            for inv in self.results["inventory"].values()])

            if total_files > 0:
                scores["data_coverage"] = min(100, (data_files / total_files) * 200)

        scores["overall"] = sum([
            scores["data_coverage"],
            scores["data_quality"],
            scores["joinability"],
            scores["china_intelligence"]
        ]) / 4

        # Determine confidence band
        if scores["overall"] > 70:
            scores["confidence_band"] = "high"
        elif scores["overall"] > 40:
            scores["confidence_band"] = "medium"
        else:
            scores["confidence_band"] = "low"

        return scores

    def run_diagnostic(self):
        """Execute full diagnostic scan"""
        logging.info(f"Starting diagnostic scan - Session: {self.session_id}")

        # Task 0: File system inventory
        logging.info("Task 0: Scanning file system...")
        data_dir = self.root_dir / "data"
        if data_dir.exists():
            self.results["inventory"]["data"] = self.scan_directory(data_dir)

        artifacts_dir = self.root_dir / "artifacts"
        if artifacts_dir.exists():
            self.results["inventory"]["artifacts"] = self.scan_directory(artifacts_dir)

        countries_dir = self.root_dir / "countries"
        if countries_dir.exists():
            self.results["inventory"]["countries"] = self.scan_directory(countries_dir)

        # Task 1: Create dataset manifest
        logging.info("Task 1: Creating dataset manifest...")
        self.create_dataset_manifest()

        # Task 7: Zero-evidence probes
        logging.info("Task 7: Running zero-evidence probes...")
        critical_queries = [
            "Leonardo DRS",
            "COSCO Shipping",
            "Piraeus Port",
            "China Three Gorges",
            "Huawei",
            "ByteDance"
        ]

        data_files = []
        for root, dirs, files in os.walk(self.root_dir / "data"):
            for file in files:
                if Path(file).suffix in ['.csv', '.json', '.tsv', '.txt', '.md']:
                    data_files.append(Path(root) / file)

        for query in critical_queries:
            if len(data_files) > 0:
                probe = self.run_zero_evidence_probe(query, data_files[:100])  # Sample first 100 files
                self.results["zero_evidence_probes"].append(probe)

        # Generate readiness scores
        logging.info("Generating readiness scores...")
        self.results["readiness_scores"] = self.generate_readiness_scores()

        # Save results
        self.save_results()

    def create_dataset_manifest(self):
        """Create comprehensive dataset manifest"""
        manifest = []

        processed_dir = self.root_dir / "data" / "processed"
        if processed_dir.exists():
            for dataset_dir in processed_dir.iterdir():
                if dataset_dir.is_dir():
                    dataset_info = {
                        "name": dataset_dir.name,
                        "path": str(dataset_dir),
                        "files": [],
                        "total_size": 0,
                        "data_types": Counter(),
                        "created": datetime.fromtimestamp(dataset_dir.stat().st_ctime).isoformat()
                    }

                    for file in dataset_dir.rglob("*"):
                        if file.is_file():
                            dataset_info["files"].append(file.name)
                            dataset_info["total_size"] += file.stat().st_size
                            dataset_info["data_types"][file.suffix] += 1

                    manifest.append(dataset_info)

        self.results["dataset_manifest"] = manifest

    def save_results(self):
        """Save diagnostic results"""
        # Save JSON results
        json_output = self.output_dir / "diagnostic_results.json"
        with open(json_output, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, default=str)

        # Generate markdown report
        self.generate_markdown_report()

        logging.info(f"Results saved to {self.output_dir}")

    def generate_markdown_report(self):
        """Generate markdown diagnostic report"""
        report_lines = [
            f"# OSINT Foresight Project Diagnostic Report",
            f"**Session ID:** {self.session_id}",
            f"**Timestamp:** {self.results['timestamp']}",
            f"**Root Directory:** {self.root_dir}",
            "",
            "## Executive Summary",
            "",
            "### Readiness Scores",
            f"- **Overall Score:** {self.results['readiness_scores']['overall']:.1f}/100",
            f"- **Confidence Band:** {self.results['readiness_scores']['confidence_band']}",
            f"- **Data Coverage:** {self.results['readiness_scores']['data_coverage']:.1f}/100",
            "",
            "## File System Inventory",
            ""
        ]

        # Add inventory statistics
        for category, inventory in self.results["inventory"].items():
            if inventory and "stats" in inventory:
                stats = inventory["stats"]
                report_lines.extend([
                    f"### {category.upper()}",
                    f"- Total Files: {stats['total_files']}",
                    f"- Total Size: {stats['total_size_bytes'] / (1024*1024):.2f} MB",
                    f"- File Types: {dict(stats['file_types'].most_common(5))}",
                    ""
                ])

        # Add dataset manifest
        report_lines.extend([
            "## Dataset Manifest",
            "",
            "| Dataset | Files | Size (MB) | Types |",
            "|---------|-------|-----------|-------|"
        ])

        for dataset in self.results["dataset_manifest"][:20]:  # Top 20 datasets
            size_mb = dataset["total_size"] / (1024*1024)
            types = ", ".join([f"{k}({v})" for k, v in dataset["data_types"].most_common(3)])
            report_lines.append(
                f"| {dataset['name']} | {len(dataset['files'])} | {size_mb:.2f} | {types} |"
            )

        # Add zero-evidence probe results
        report_lines.extend([
            "",
            "## Zero-Evidence Probe Results",
            "",
            "| Query | Locations Searched | Matches Found | Confidence |",
            "|-------|-------------------|---------------|------------|"
        ])

        for probe in self.results["zero_evidence_probes"]:
            confidence = "HIGH" if probe["matches_found"] > 5 else "MEDIUM" if probe["matches_found"] > 0 else "LOW"
            report_lines.append(
                f"| {probe['query']} | {probe['locations_searched']} | {probe['matches_found']} | {confidence} |"
            )

        # Add warnings
        if self.results["warnings"]:
            report_lines.extend([
                "",
                "## Warnings",
                ""
            ])
            for warning in self.results["warnings"]:
                report_lines.append(f"- {warning}")

        # Save report
        report_path = self.output_dir / "diagnostic_report.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(report_lines))

if __name__ == "__main__":
    scanner = DiagnosticScanner()
    scanner.run_diagnostic()

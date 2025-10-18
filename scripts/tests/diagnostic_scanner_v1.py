#!/usr/bin/env python3
"""
Full Project Diagnostic & Data Readiness Audit (v1.0)
Implements the battle-tested diagnostic prompt with all guardrails
"""

import os
import json
import hashlib
import sqlite3
import gzip
import zipfile
import tarfile
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter
import re
import csv
import pandas as pd
import chardet
from typing import Dict, List, Set, Tuple, Any
import logging

# Session Configuration
SESSION_ID = f"diag_{datetime.now().strftime('%Y%m%d_%H%M')}_v1"
ROOT_DIRS = [
    "C:/Projects/OSINT - Foresight",
    "F:/OSINT_Data"
]
OUTPUT_DIR = f"C:/Projects/OSINT - Foresight/_diagnostics/{SESSION_ID}"
MAX_SCAN_BYTES = 32 * 1024 * 1024  # 32MB
TIMEFRAME_REFERENCE = "2010-present"
DEFAULT_ENCODINGS = ['utf-8', 'utf-8-sig', 'latin-1']
LOCALE_LANGS = ["en", "it", "de", "zh", "el", "pl", "hu", "cs", "pt"]

# Create output directory
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"{OUTPUT_DIR}/diagnostic.log"),
        logging.StreamHandler()
    ]
)

class DiagnosticScanner:
    def __init__(self):
        self.file_inventory = []
        self.schema_profiles = {}
        self.entity_catalog = defaultdict(set)
        self.coverage_map = defaultdict(dict)
        self.quality_metrics = {}
        self.joinability_matrix = defaultdict(list)
        self.prior_analyses = []
        self.zero_evidence_log = []
        self.language_detections = defaultdict(Counter)
        self.governance_flags = {}
        self.readiness_scores = {}

        # China-related patterns for zero-evidence probe
        self.china_patterns = {
            'companies': [
                'huawei', 'zte', 'alibaba', 'tencent', 'baidu', 'bytedance',
                'lenovo', 'xiaomi', 'dji', 'hikvision', 'dahua', 'cosco',
                'sinopec', 'petrochina', 'bank of china', 'icbc', 'haier'
            ],
            'variants': {
                'huawei': ['华为', 'HW', 'Huawei Tech'],
                'zte': ['中兴', 'zhongxing', 'ZTE Corp'],
                'alibaba': ['阿里巴巴', 'alicloud', 'taobao'],
                'cosco': ['中远', 'china ocean shipping'],
            },
            'bri_terms': [
                'belt and road', 'bri', 'silk road', '一带一路',
                'belt & road', 'b&r initiative', 'obor'
            ],
            'institutions': [
                'chinese academy', 'cas', '中科院', 'confucius',
                'hanban', '孔子学院'
            ]
        }

    def compute_file_hash(self, filepath: Path, max_bytes: int = None) -> str:
        """Compute SHA-256 hash of file (optionally truncated)"""
        sha256 = hashlib.sha256()
        bytes_read = 0

        try:
            with open(filepath, 'rb') as f:
                while chunk := f.read(8192):
                    sha256.update(chunk)
                    bytes_read += len(chunk)
                    if max_bytes and bytes_read >= max_bytes:
                        logging.info(f"Hash truncated at {max_bytes} bytes: {filepath}")
                        break
            return sha256.hexdigest()
        except Exception as e:
            logging.error(f"Hash computation failed for {filepath}: {e}")
            return f"ERROR_{str(e)[:20]}"

    def detect_encoding(self, filepath: Path, sample_size: int = 10000) -> str:
        """Detect file encoding with fallback"""
        try:
            with open(filepath, 'rb') as f:
                sample = f.read(sample_size)

            # Try chardet
            detection = chardet.detect(sample)
            if detection['confidence'] > 0.7:
                return detection['encoding']

            # Try default encodings
            for encoding in DEFAULT_ENCODINGS:
                try:
                    sample.decode(encoding)
                    return encoding
                except:
                    continue

            return 'latin-1'  # Ultimate fallback
        except:
            return 'binary'

    def profile_schema(self, filepath: Path) -> Dict:
        """Profile file schema based on extension and content"""
        profile = {
            'path': str(filepath),
            'size_bytes': filepath.stat().st_size,
            'modified': datetime.fromtimestamp(filepath.stat().st_mtime).isoformat(),
            'encoding': 'unknown',
            'format': filepath.suffix.lower(),
            'schema': {},
            'sample_rows': [],
            'row_count': 0,
            'parse_errors': []
        }

        try:
            # Handle different file types
            if filepath.suffix.lower() in ['.csv', '.tsv', '.txt', '.dat']:
                profile['encoding'] = self.detect_encoding(filepath)
                delimiter = '\t' if filepath.suffix.lower() in ['.tsv', '.dat'] else ','

                with open(filepath, 'r', encoding=profile['encoding'], errors='replace') as f:
                    # Read header
                    header = f.readline().strip().split(delimiter)
                    profile['schema']['fields'] = header
                    profile['schema']['field_count'] = len(header)

                    # Sample rows
                    for i in range(5):
                        line = f.readline()
                        if not line:
                            break
                        profile['sample_rows'].append(line.strip().split(delimiter)[:10])

                    # Count total rows (streaming)
                    f.seek(0)
                    profile['row_count'] = sum(1 for _ in f)

            elif filepath.suffix.lower() == '.json':
                profile['encoding'] = self.detect_encoding(filepath)
                with open(filepath, 'r', encoding=profile['encoding']) as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        profile['row_count'] = len(data)
                        if data:
                            profile['schema']['fields'] = list(data[0].keys()) if isinstance(data[0], dict) else ['value']
                            profile['sample_rows'] = data[:3]
                    elif isinstance(data, dict):
                        profile['schema']['fields'] = list(data.keys())
                        profile['row_count'] = 1

            elif filepath.suffix.lower() == '.db':
                conn = sqlite3.connect(filepath)
                cursor = conn.cursor()

                # Get tables
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                profile['schema']['tables'] = [t[0] for t in tables]

                # Sample each table
                for table in profile['schema']['tables'][:5]:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    profile['schema'][f'{table}_count'] = count

                    cursor.execute(f"PRAGMA table_info({table})")
                    columns = cursor.fetchall()
                    profile['schema'][f'{table}_columns'] = [c[1] for c in columns]

                conn.close()

            elif filepath.suffix.lower() in ['.gz']:
                # Handle compressed files
                if '.csv' in filepath.name or '.tsv' in filepath.name or '.dat' in filepath.name:
                    with gzip.open(filepath, 'rt', encoding='utf-8', errors='replace') as f:
                        header = f.readline().strip()
                        delimiter = '\t' if '\t' in header else ','
                        profile['schema']['fields'] = header.split(delimiter)
                        profile['schema']['field_count'] = len(profile['schema']['fields'])

                        # Sample rows
                        for i in range(5):
                            line = f.readline()
                            if not line:
                                break
                            profile['sample_rows'].append(line.strip().split(delimiter)[:10])

        except Exception as e:
            profile['parse_errors'].append(str(e))
            logging.error(f"Schema profiling failed for {filepath}: {e}")

        return profile

    def run_zero_evidence_probe(self, filepath: Path, patterns: Dict) -> List[Dict]:
        """Run zero-evidence probe to verify 'no China' claims"""
        probe_log = []

        try:
            encoding = self.detect_encoding(filepath)

            # Search for each pattern category
            for category, terms in patterns.items():
                if not isinstance(terms, list):
                    continue

                for term in terms:
                    probe_entry = {
                        'file': str(filepath),
                        'category': category,
                        'term': term,
                        'variants_tested': [],
                        'matches': 0,
                        'sample_contexts': []
                    }

                    # Test original term
                    with open(filepath, 'r', encoding=encoding, errors='replace') as f:
                        content = f.read(MAX_SCAN_BYTES)
                        content_lower = content.lower()

                        if term.lower() in content_lower:
                            probe_entry['matches'] = content_lower.count(term.lower())
                            # Get context
                            idx = content_lower.find(term.lower())
                            if idx != -1:
                                start = max(0, idx - 50)
                                end = min(len(content), idx + len(term) + 50)
                                probe_entry['sample_contexts'].append(content[start:end])

                    # Test variants if available
                    if category == 'companies' and term in self.china_patterns.get('variants', {}):
                        for variant in self.china_patterns['variants'][term]:
                            probe_entry['variants_tested'].append(variant)
                            if variant.lower() in content_lower:
                                probe_entry['matches'] += content_lower.count(variant.lower())

                    if probe_entry['matches'] > 0:
                        probe_log.append(probe_entry)

        except Exception as e:
            logging.error(f"Zero-evidence probe failed for {filepath}: {e}")

        return probe_log

    def scan_directory(self, root_dir: Path):
        """Scan directory tree and build comprehensive inventory"""
        logging.info(f"Scanning directory: {root_dir}")

        # Define relevant extensions
        data_extensions = {
            '.csv', '.tsv', '.json', '.xml', '.db', '.sqlite', '.xlsx', '.xls',
            '.dat', '.txt', '.gz', '.zip', '.tar', '.bz2', '.parquet', '.jsonl'
        }

        analysis_extensions = {'.md', '.py', '.ipynb', '.html', '.pdf', '.docx'}

        for filepath in root_dir.rglob('*'):
            if not filepath.is_file():
                continue

            # Skip huge files for now
            if filepath.stat().st_size > 1e9:  # 1GB
                logging.warning(f"Skipping large file: {filepath} ({filepath.stat().st_size:,} bytes)")
                continue

            file_info = {
                'path': str(filepath),
                'name': filepath.name,
                'extension': filepath.suffix.lower(),
                'size_bytes': filepath.stat().st_size,
                'modified': datetime.fromtimestamp(filepath.stat().st_mtime).isoformat(),
                'hash': self.compute_file_hash(filepath, MAX_SCAN_BYTES),
                'category': 'unknown'
            }

            # Categorize file
            if filepath.suffix.lower() in data_extensions:
                file_info['category'] = 'data'
                # Profile schema for data files
                if filepath.stat().st_size < MAX_SCAN_BYTES:
                    self.schema_profiles[str(filepath)] = self.profile_schema(filepath)
            elif filepath.suffix.lower() in analysis_extensions:
                file_info['category'] = 'analysis'
                if 'analysis' in str(filepath).lower() or 'report' in str(filepath).lower():
                    self.prior_analyses.append(file_info)

            self.file_inventory.append(file_info)

            # Run zero-evidence probe on relevant files
            if file_info['category'] == 'data' and filepath.stat().st_size < MAX_SCAN_BYTES:
                probe_results = self.run_zero_evidence_probe(filepath, self.china_patterns)
                if probe_results:
                    self.zero_evidence_log.extend(probe_results)

    def compute_readiness_scores(self):
        """Compute analysis readiness scores"""
        # Count by category
        data_files = [f for f in self.file_inventory if f['category'] == 'data']
        analysis_files = [f for f in self.file_inventory if f['category'] == 'analysis']

        # Assess coverage
        usaspending_ready = any('usaspending' in f['path'].lower() for f in data_files)
        cordis_ready = any('cordis' in f['path'].lower() for f in data_files)
        ted_ready = any('ted' in f['path'].lower() for f in data_files)
        openalex_ready = any('openalex' in f['path'].lower() for f in data_files)

        self.readiness_scores = {
            'overall': {
                'score': 0.0,
                'confidence_band': 'low',
                'support': {
                    'datasets': len(data_files),
                    'total_rows': sum(p.get('row_count', 0) for p in self.schema_profiles.values()),
                    'prior_analyses': len(analysis_files)
                }
            },
            'by_source': {
                'usaspending': {'ready': usaspending_ready, 'files': 0, 'confidence': 'low'},
                'cordis': {'ready': cordis_ready, 'files': 0, 'confidence': 'low'},
                'ted': {'ready': ted_ready, 'files': 0, 'confidence': 'low'},
                'openalex': {'ready': openalex_ready, 'files': 0, 'confidence': 'low'}
            },
            'by_analysis_type': {
                'china_penetration': {'feasible': True, 'confidence': 'medium'},
                'technology_transfer': {'feasible': True, 'confidence': 'low'},
                'supply_chain': {'feasible': usaspending_ready, 'confidence': 'low'},
                'research_collaboration': {'feasible': cordis_ready or openalex_ready, 'confidence': 'medium'}
            }
        }

        # Count files per source
        for f in data_files:
            path_lower = f['path'].lower()
            if 'usaspending' in path_lower:
                self.readiness_scores['by_source']['usaspending']['files'] += 1
            elif 'cordis' in path_lower:
                self.readiness_scores['by_source']['cordis']['files'] += 1
            elif 'ted' in path_lower:
                self.readiness_scores['by_source']['ted']['files'] += 1
            elif 'openalex' in path_lower:
                self.readiness_scores['by_source']['openalex']['files'] += 1

        # Update confidence based on file counts
        for source, info in self.readiness_scores['by_source'].items():
            if info['files'] > 10:
                info['confidence'] = 'high'
            elif info['files'] > 3:
                info['confidence'] = 'medium'

        # Calculate overall score
        ready_sources = sum(1 for s in self.readiness_scores['by_source'].values() if s['ready'])
        self.readiness_scores['overall']['score'] = ready_sources / 4.0

        if ready_sources >= 3:
            self.readiness_scores['overall']['confidence_band'] = 'high'
        elif ready_sources >= 2:
            self.readiness_scores['overall']['confidence_band'] = 'medium'

    def generate_report(self):
        """Generate comprehensive diagnostic report"""
        report = []
        report.append(f"# Full Project Diagnostic Report")
        report.append(f"**Session ID:** {SESSION_ID}")
        report.append(f"**Generated:** {datetime.now().isoformat()}")
        report.append(f"**Root Directories:** {', '.join(ROOT_DIRS)}")
        report.append("")

        # File Inventory Summary
        report.append("## 1. File Inventory")
        report.append(f"- Total files scanned: {len(self.file_inventory)}")
        report.append(f"- Data files: {len([f for f in self.file_inventory if f['category'] == 'data'])}")
        report.append(f"- Analysis files: {len([f for f in self.file_inventory if f['category'] == 'analysis'])}")
        report.append(f"- Total size: {sum(f['size_bytes'] for f in self.file_inventory):,} bytes")
        report.append("")

        # Schema Profiles
        report.append("## 2. Schema Profiles")
        for path, profile in list(self.schema_profiles.items())[:10]:
            report.append(f"\n### {Path(path).name}")
            report.append(f"- **Path:** `{path}`")
            report.append(f"- **Size:** {profile['size_bytes']:,} bytes")
            report.append(f"- **Rows:** {profile.get('row_count', 'unknown')}")
            report.append(f"- **Encoding:** {profile.get('encoding', 'unknown')}")
            if 'fields' in profile.get('schema', {}):
                report.append(f"- **Fields ({len(profile['schema']['fields'])}):** {', '.join(profile['schema']['fields'][:10])}")
            if profile.get('parse_errors'):
                report.append(f"- **Parse Errors:** {profile['parse_errors']}")
        report.append("")

        # Zero-Evidence Probe Results
        report.append("## 3. Zero-Evidence Probe Results")
        if self.zero_evidence_log:
            report.append(f"Found {len(self.zero_evidence_log)} China-related patterns:")
            for entry in self.zero_evidence_log[:20]:
                report.append(f"\n- **File:** `{entry['file']}`")
                report.append(f"  - Term: '{entry['term']}' ({entry['category']})")
                report.append(f"  - Matches: {entry['matches']}")
                if entry['sample_contexts']:
                    report.append(f"  - Context: `{entry['sample_contexts'][0][:100]}...`")
        else:
            report.append("No China-related patterns found in scanned files.")
        report.append("")

        # Readiness Scores
        report.append("## 4. Readiness Assessment")
        report.append(f"### Overall Score: {self.readiness_scores['overall']['score']:.2f}")
        report.append(f"- Confidence: {self.readiness_scores['overall']['confidence_band']}")
        report.append(f"- Datasets: {self.readiness_scores['overall']['support']['datasets']}")
        report.append(f"- Total Rows: {self.readiness_scores['overall']['support']['total_rows']:,}")
        report.append("")

        report.append("### By Data Source:")
        for source, info in self.readiness_scores['by_source'].items():
            status = "✓" if info['ready'] else "✗"
            report.append(f"- **{source.upper()}** {status}: {info['files']} files ({info['confidence']} confidence)")
        report.append("")

        report.append("### By Analysis Type:")
        for analysis_type, info in self.readiness_scores['by_analysis_type'].items():
            feasible = "✓" if info['feasible'] else "✗"
            report.append(f"- **{analysis_type.replace('_', ' ').title()}** {feasible}: {info['confidence']} confidence")
        report.append("")

        # Prior Analyses
        if self.prior_analyses:
            report.append("## 5. Prior Analyses Found")
            for analysis in self.prior_analyses[:10]:
                report.append(f"- `{analysis['path']}` ({analysis['size_bytes']:,} bytes)")
        report.append("")

        # Save report
        report_text = "\n".join(report)
        report_path = Path(OUTPUT_DIR) / "report_diagnostic.md"
        report_path.write_text(report_text, encoding='utf-8')
        logging.info(f"Report saved to: {report_path}")

        # Save JSON outputs
        json_outputs = {
            'session_id': SESSION_ID,
            'timestamp': datetime.now().isoformat(),
            'file_inventory': self.file_inventory[:100],  # Truncate for size
            'schema_profiles': {k: v for k, v in list(self.schema_profiles.items())[:50]},
            'zero_evidence_log': self.zero_evidence_log,
            'readiness_scores': self.readiness_scores,
            'prior_analyses': self.prior_analyses[:50]
        }

        json_path = Path(OUTPUT_DIR) / "diagnostic_data.json"
        json_path.write_text(json.dumps(json_outputs, indent=2, default=str), encoding='utf-8')
        logging.info(f"JSON data saved to: {json_path}")

        return report_text

def main():
    """Run comprehensive diagnostic scan"""
    print(f"Starting diagnostic scan - Session ID: {SESSION_ID}")
    print(f"Output directory: {OUTPUT_DIR}")

    scanner = DiagnosticScanner()

    # Scan all root directories
    for root_dir in ROOT_DIRS:
        root_path = Path(root_dir)
        if root_path.exists():
            scanner.scan_directory(root_path)
        else:
            logging.warning(f"Root directory not found: {root_dir}")

    # Compute readiness scores
    scanner.compute_readiness_scores()

    # Generate report
    report = scanner.generate_report()

    print("\n" + "="*70)
    print("DIAGNOSTIC SCAN COMPLETE")
    print("="*70)
    print(f"Files scanned: {len(scanner.file_inventory)}")
    print(f"Data sources profiled: {len(scanner.schema_profiles)}")
    print(f"China patterns found: {len(scanner.zero_evidence_log)}")
    print(f"Overall readiness: {scanner.readiness_scores['overall']['score']:.2%}")
    print(f"\nFull report: {OUTPUT_DIR}/report_diagnostic.md")
    print(f"JSON data: {OUTPUT_DIR}/diagnostic_data.json")

    return scanner

if __name__ == "__main__":
    scanner = main()

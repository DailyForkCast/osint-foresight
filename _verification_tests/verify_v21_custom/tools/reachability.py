#!/usr/bin/env python3
"""
T00: Global Reachability & Location-Level Coverage Test
Computes OS-verified bytes per location and ensures ≥99.9% coverage
"""

import os
import json
import csv
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime
import argparse
import sys

class ReachabilityVerifier:
    def __init__(self, roots, excludes_file=None):
        self.roots = [Path(r) for r in roots]
        self.excludes = self.load_excludes(excludes_file) if excludes_file else []
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'locations': {},
            'total_reachable_bytes': 0,
            'total_manifest_bytes': 0,
            'coverage': 0.0,
            'missed_files': [],
            'assertions': {}
        }

    def load_excludes(self, excludes_file):
        """Load exclusion patterns"""
        excludes = []
        if Path(excludes_file).exists():
            with open(excludes_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        excludes.append(line)
        return excludes

    def is_excluded(self, path):
        """Check if path matches any exclusion pattern"""
        path_str = str(path)
        for pattern in self.excludes:
            if pattern in path_str:
                return True
        return False

    def compute_os_bytes(self, root):
        """Compute total bytes reachable from OS for a location"""
        location_stats = {
            'path': str(root),
            'os_bytes': 0,
            'os_file_count': 0,
            'excluded_bytes': 0,
            'excluded_count': 0,
            'unreadable_bytes': 0,
            'unreadable_count': 0,
            'errors': []
        }

        # Try PowerShell method for Windows
        if os.name == 'nt':
            try:
                cmd = f'powershell -Command "Get-ChildItem -Path \'{root}\' -Recurse -File | Measure-Object -Property Length -Sum | Select-Object -ExpandProperty Sum"'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
                if result.returncode == 0 and result.stdout.strip():
                    try:
                        ps_bytes = int(result.stdout.strip())
                        location_stats['os_bytes'] = ps_bytes
                    except:
                        pass
            except Exception as e:
                location_stats['errors'].append(f"PowerShell error: {str(e)}")

        # Python os.walk method as fallback or primary
        python_bytes = 0
        python_files = 0

        for dirpath, dirnames, filenames in os.walk(root):
            # Skip excluded directories
            dirnames[:] = [d for d in dirnames if not self.is_excluded(Path(dirpath) / d)]

            for filename in filenames:
                filepath = Path(dirpath) / filename

                if self.is_excluded(filepath):
                    try:
                        size = filepath.stat().st_size
                        location_stats['excluded_bytes'] += size
                        location_stats['excluded_count'] += 1
                    except:
                        pass
                    continue

                try:
                    stats = filepath.stat()
                    python_bytes += stats.st_size
                    python_files += 1
                except PermissionError:
                    location_stats['unreadable_count'] += 1
                except Exception as e:
                    location_stats['errors'].append(f"{filepath}: {str(e)}")

        # Use Python count if PowerShell failed
        if location_stats['os_bytes'] == 0:
            location_stats['os_bytes'] = python_bytes

        location_stats['os_file_count'] = python_files
        location_stats['effective_bytes'] = location_stats['os_bytes'] - location_stats['excluded_bytes']

        return location_stats

    def load_manifest(self):
        """Load the inventory manifest from Phase 0"""
        manifest_path = Path("C:/Projects/OSINT - Foresight/inventory_manifest.json")
        if not manifest_path.exists():
            raise FileNotFoundError(f"Manifest not found: {manifest_path}")

        with open(manifest_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def compute_manifest_bytes(self, manifest):
        """Compute bytes from manifest"""
        manifest_bytes = 0
        manifest_files = 0

        for dataset_name, dataset in manifest.get('datasets', {}).items():
            for file_entry in dataset.get('files', []):
                manifest_bytes += file_entry.get('size', 0)
                manifest_files += 1

        return manifest_bytes, manifest_files

    def find_missed_files(self, location_stats, manifest):
        """Find files in OS but not in manifest"""
        missed = []

        # Get all manifest paths
        manifest_paths = set()
        for dataset_name, dataset in manifest.get('datasets', {}).items():
            for file_entry in dataset.get('files', []):
                manifest_paths.add(file_entry['path'])

        # Walk each location and find missing files
        for loc_name, loc_stats in location_stats.items():
            root = Path(loc_stats['path'])
            if not root.exists():
                continue

            for dirpath, dirnames, filenames in os.walk(root):
                # Skip excluded directories
                dirnames[:] = [d for d in dirnames if not self.is_excluded(Path(dirpath) / d)]

                for filename in filenames:
                    filepath = Path(dirpath) / filename

                    if self.is_excluded(filepath):
                        continue

                    if str(filepath) not in manifest_paths:
                        try:
                            stats = filepath.stat()
                            reason = self.determine_miss_reason(filepath, manifest)
                            missed.append({
                                'path': str(filepath),
                                'size': stats.st_size,
                                'reason': reason,
                                'dev': stats.st_dev,
                                'inode': stats.st_ino,
                                'mtime': datetime.fromtimestamp(stats.st_mtime).isoformat()
                            })
                        except Exception as e:
                            missed.append({
                                'path': str(filepath),
                                'size': 0,
                                'reason': 'UNREADABLE',
                                'error': str(e)
                            })

        return missed

    def determine_miss_reason(self, filepath, manifest):
        """Determine why a file was missed"""
        path_str = str(filepath).lower()

        if '.git' in path_str:
            return 'EXCLUDED'
        elif '__pycache__' in path_str:
            return 'EXCLUDED'
        elif filepath.suffix in ['.pyc', '.pyo', '.tmp', '.log']:
            return 'TRANSIENT'
        elif len(str(filepath)) > 260:
            return 'LONG_PATH'
        elif filepath.suffix in ['.gz', '.zip', '.tar', '.7z']:
            return 'NESTED_ARCHIVE_UNINDEXED'
        else:
            return 'OTHER'

    def verify_location_coverage(self, location_stats, manifest_location_bytes):
        """Verify coverage for a specific location"""
        effective_bytes = location_stats['effective_bytes']

        if effective_bytes == 0:
            return 0.0, 'NO_DATA'

        coverage = manifest_location_bytes / effective_bytes

        if coverage >= 0.999:
            status = 'PASS'
        elif coverage >= 0.95:
            status = 'WARN'
        else:
            status = 'FAIL'

        return coverage, status

    def run(self):
        """Execute reachability verification"""
        print("\n" + "="*60)
        print("T00: GLOBAL REACHABILITY & COVERAGE TEST")
        print("="*60)

        # Load manifest
        print("\nLoading inventory manifest...")
        manifest = self.load_manifest()
        total_manifest_bytes, total_manifest_files = self.compute_manifest_bytes(manifest)
        self.results['total_manifest_bytes'] = total_manifest_bytes
        print(f"Manifest: {total_manifest_files:,} files, {total_manifest_bytes:,} bytes")

        # Compute OS bytes per location
        print("\nComputing OS-reachable bytes per location...")
        location_stats = {}

        for root in self.roots:
            if root.exists():
                print(f"\nScanning: {root}")
                stats = self.compute_os_bytes(root)
                location_stats[root.name] = stats
                self.results['total_reachable_bytes'] += stats['effective_bytes']

                print(f"  OS bytes: {stats['os_bytes']:,}")
                print(f"  Excluded: {stats['excluded_bytes']:,}")
                print(f"  Effective: {stats['effective_bytes']:,}")
                print(f"  Files: {stats['os_file_count']:,}")
            else:
                print(f"\nSkipping non-existent: {root}")

        self.results['locations'] = location_stats

        # Calculate global coverage
        if self.results['total_reachable_bytes'] > 0:
            self.results['coverage'] = (
                self.results['total_manifest_bytes'] /
                self.results['total_reachable_bytes']
            )
        else:
            self.results['coverage'] = 0.0

        print(f"\nGlobal Coverage: {self.results['coverage']:.1%}")

        # Find missed files
        print("\nFinding missed files...")
        self.results['missed_files'] = self.find_missed_files(location_stats, manifest)
        print(f"Missed files: {len(self.results['missed_files'])}")

        # Set assertions
        self.results['assertions']['coverage_ge_0_999'] = (
            'OK' if self.results['coverage'] >= 0.999 else 'FAIL'
        )

        self.results['assertions']['missed_bytes_report_empty_or_justified'] = (
            'OK' if len(self.results['missed_files']) == 0 or
            all(m['reason'] in ['EXCLUDED', 'TRANSIENT'] for m in self.results['missed_files'])
            else 'FAIL'
        )

        # Save results
        self.save_results()

        # Print summary
        print("\n" + "="*40)
        print("RESULTS")
        print("="*40)
        print(f"Coverage: {self.results['coverage']:.3%}")
        print(f"Coverage ≥ 99.9%: {self.results['assertions']['coverage_ge_0_999']}")
        print(f"Missed files justified: {self.results['assertions']['missed_bytes_report_empty_or_justified']}")

        # Return exit code
        if all(v == 'OK' for v in self.results['assertions'].values()):
            print("\n[PASS] All assertions passed")
            return 0
        else:
            print("\n[FAIL] Some assertions failed")
            return 1

    def save_results(self):
        """Save verification results"""
        base_dir = Path("_verification_tests/verify_v21_custom/artifacts")
        base_dir.mkdir(parents=True, exist_ok=True)

        # Save main results
        with open(base_dir / "reachable_bytes.json", 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, default=str)

        # Save missed files report
        if self.results['missed_files']:
            with open(base_dir / "missed_bytes_report.csv", 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['path', 'size', 'reason', 'dev', 'inode', 'mtime']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for missed in self.results['missed_files']:
                    writer.writerow({k: missed.get(k, '') for k in fieldnames})

        print(f"\nResults saved to {base_dir}")


def main():
    parser = argparse.ArgumentParser(description='Reachability and coverage verification')
    parser.add_argument('--roots', nargs='+', default=[
        'C:/Projects/OSINT - Foresight/data/processed',
        'F:/OSINT_DATA',
        'F:/TED_Data',
        'F:/OSINT_Backups'
    ], help='Root directories to scan')
    parser.add_argument('--excludes', help='Exclusions file')

    args = parser.parse_args()

    verifier = ReachabilityVerifier(args.roots, args.excludes)
    return verifier.run()


if __name__ == "__main__":
    sys.exit(main())

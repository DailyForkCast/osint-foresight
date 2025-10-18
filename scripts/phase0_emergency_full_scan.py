#!/usr/bin/env python3
"""
PHASE 0 EMERGENCY FULL SCAN - Addresses 97.2% data discrepancy
Must inventory 890GB across F: drive locations
"""

import os
import json
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime
import sys

class EmergencyInventoryScanner:
    def __init__(self):
        # CRITICAL: Use actual F: drive paths from OS verification
        self.data_locations = {
            'project_data': {
                'path': 'C:/Projects/OSINT - Foresight/data',
                'expected_bytes': 1_365_608_409,
                'expected_gb': 1.27
            },
            'osint_data': {
                'path': 'F:/OSINT_DATA',
                'expected_bytes': 476_478_435_776,
                'expected_gb': 443.73
            },
            'ted_data': {
                'path': 'F:/TED_Data',
                'expected_bytes': 25_980_724_657,
                'expected_gb': 24.20
            },
            'osint_backups': {
                'path': 'F:/OSINT_Backups',
                'expected_bytes': 451_964_296_198,
                'expected_gb': 420.92
            },
            'horizons_data': {
                'path': 'F:/2025-09-14 Horizons',
                'expected_bytes': 199_347_516,
                'expected_gb': 0.19
            }
        }

        self.total_expected_bytes = 955_988_364_556  # 890.31 GB

        self.inventory = {
            'generated': datetime.now().isoformat(),
            'version': '2.0-EMERGENCY',
            'critical_note': 'Emergency scan to address 97.2% data discrepancy',
            'datasets': {},
            'by_location': {},
            'os_verification': {},
            'summary': {
                'total_size_bytes': 0,
                'total_files': 0,
                'by_type': {},
                'coverage_vs_os': 0.0
            },
            'all_files': []
        }

    def verify_os_bytes(self, path):
        """Get OS-reported bytes for a path using PowerShell"""
        print(f"  OS verification for {path}...")

        if not Path(path).exists():
            print(f"    WARNING: Path does not exist: {path}")
            return 0, "PATH_NOT_FOUND"

        try:
            # PowerShell command to get total bytes
            cmd = f'powershell -Command "(Get-ChildItem -Path \'{path}\' -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum"'

            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)

            if result.returncode == 0 and result.stdout.strip():
                try:
                    bytes_found = int(result.stdout.strip())
                    return bytes_found, "SUCCESS"
                except ValueError:
                    return 0, f"PARSE_ERROR: {result.stdout[:100]}"
            else:
                return 0, f"COMMAND_ERROR: {result.stderr[:100] if result.stderr else 'No output'}"

        except subprocess.TimeoutExpired:
            return 0, "TIMEOUT"
        except Exception as e:
            return 0, f"ERROR: {str(e)}"

    def scan_location(self, name, location_info):
        """Scan a single location completely"""
        path = location_info['path']
        expected_bytes = location_info['expected_bytes']

        print(f"\nScanning {name}: {path}")
        print(f"  Expected: {expected_bytes:,} bytes ({location_info['expected_gb']:.2f} GB)")

        location_data = {
            'name': name,
            'path': path,
            'expected_bytes': expected_bytes,
            'found_bytes': 0,
            'file_count': 0,
            'files': [],
            'os_verified_bytes': 0,
            'os_status': '',
            'coverage': 0.0
        }

        # First, get OS verification
        os_bytes, os_status = self.verify_os_bytes(path)
        location_data['os_verified_bytes'] = os_bytes
        location_data['os_status'] = os_status

        if os_bytes > 0:
            print(f"  OS verified: {os_bytes:,} bytes")
            coverage = (os_bytes / expected_bytes) * 100
            print(f"  Coverage vs expected: {coverage:.1f}%")

            if coverage < 90:
                print(f"  ⚠️ WARNING: Low coverage! Missing {100-coverage:.1f}% of expected data")

        # Now scan with Python (no restrictions)
        if not Path(path).exists():
            print(f"  ❌ Path does not exist!")
            location_data['error'] = 'PATH_NOT_EXIST'
            return location_data

        print(f"  Scanning files (no depth limit)...")
        file_count = 0
        total_bytes = 0

        try:
            for root, dirs, files in os.walk(path):
                # Show progress every 1000 files
                if file_count % 1000 == 0 and file_count > 0:
                    print(f"    Progress: {file_count} files, {total_bytes/1e9:.2f} GB")

                for filename in files:
                    filepath = Path(root) / filename

                    try:
                        stats = filepath.stat()
                        file_info = {
                            'path': str(filepath),
                            'size': stats.st_size,
                            'modified': datetime.fromtimestamp(stats.st_mtime).isoformat(),
                            'extension': filepath.suffix.lower()
                        }

                        location_data['files'].append(file_info)
                        self.inventory['all_files'].append(file_info)

                        total_bytes += stats.st_size
                        file_count += 1

                        # Update file type statistics
                        ext = filepath.suffix.lower() or 'no_extension'
                        if ext not in self.inventory['summary']['by_type']:
                            self.inventory['summary']['by_type'][ext] = {
                                'count': 0,
                                'bytes': 0
                            }
                        self.inventory['summary']['by_type'][ext]['count'] += 1
                        self.inventory['summary']['by_type'][ext]['bytes'] += stats.st_size

                    except Exception as e:
                        # Log error but continue
                        if 'errors' not in location_data:
                            location_data['errors'] = []
                        location_data['errors'].append(f"{filepath}: {str(e)}")

        except Exception as e:
            print(f"  ❌ Scan error: {str(e)}")
            location_data['scan_error'] = str(e)

        location_data['found_bytes'] = total_bytes
        location_data['file_count'] = file_count

        # Calculate coverage
        if expected_bytes > 0:
            location_data['coverage'] = (total_bytes / expected_bytes) * 100

        print(f"  Found: {file_count:,} files, {total_bytes:,} bytes ({total_bytes/1e9:.2f} GB)")
        print(f"  Coverage: {location_data['coverage']:.1f}%")

        if location_data['coverage'] < 90:
            print(f"  ⚠️ WARNING: Low coverage for {name}!")

        return location_data

    def generate_samples(self, num_samples=10):
        """Generate random samples with SHA256 and hex dumps"""
        import random

        if not self.inventory['all_files']:
            return []

        samples = []
        sample_files = random.sample(
            self.inventory['all_files'],
            min(num_samples, len(self.inventory['all_files']))
        )

        for file_info in sample_files:
            filepath = Path(file_info['path'])

            try:
                # Compute SHA256
                sha256 = hashlib.sha256()
                with open(filepath, 'rb') as f:
                    for chunk in iter(lambda: f.read(8192), b''):
                        sha256.update(chunk)

                # Get hex dump (first 2KB)
                with open(filepath, 'rb') as f:
                    hex_dump = f.read(2048).hex()[:200]  # First 200 hex chars

                samples.append({
                    'path': str(filepath),
                    'size': file_info['size'],
                    'sha256': sha256.hexdigest(),
                    'hex_preview': hex_dump
                })

            except Exception as e:
                samples.append({
                    'path': str(filepath),
                    'size': file_info['size'],
                    'error': str(e)
                })

        return samples

    def run(self):
        """Execute emergency full scan"""
        print("\n" + "="*70)
        print("PHASE 0: EMERGENCY FULL INVENTORY SCAN")
        print("="*70)
        print(f"\nTarget: {self.total_expected_bytes:,} bytes (890.31 GB)")
        print("Scanning 5 locations including F: drive...\n")

        # Scan each location
        for name, location_info in self.data_locations.items():
            location_data = self.scan_location(name, location_info)
            self.inventory['datasets'][name] = location_data
            self.inventory['by_location'][name] = location_data

            # Update totals
            self.inventory['summary']['total_size_bytes'] += location_data['found_bytes']
            self.inventory['summary']['total_files'] += location_data['file_count']

        # Calculate overall coverage
        self.inventory['summary']['coverage_vs_os'] = (
            self.inventory['summary']['total_size_bytes'] / self.total_expected_bytes * 100
        )

        # Generate samples
        print("\nGenerating random samples...")
        self.inventory['random_samples'] = self.generate_samples()

        # Save inventory
        print("\nSaving emergency inventory...")
        output_file = Path("C:/Projects/OSINT - Foresight/emergency_inventory_manifest.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.inventory, f, indent=2, default=str)
        print(f"Saved to: {output_file}")

        # Generate report
        self.generate_report()

        # Final summary
        print("\n" + "="*70)
        print("EMERGENCY SCAN COMPLETE")
        print("="*70)
        print(f"Total files: {self.inventory['summary']['total_files']:,}")
        print(f"Total bytes: {self.inventory['summary']['total_size_bytes']:,}")
        print(f"Total GB: {self.inventory['summary']['total_size_bytes']/1e9:.2f}")
        print(f"\nCoverage vs OS expected: {self.inventory['summary']['coverage_vs_os']:.1f}%")

        if self.inventory['summary']['coverage_vs_os'] < 90:
            print("\n⚠️ CRITICAL WARNING: Less than 90% of expected data found!")
            print("Check F: drive accessibility and permissions.")
            return 1
        else:
            print("\n✅ SUCCESS: Adequate coverage achieved")
            return 0

    def generate_report(self):
        """Generate detailed report"""
        report = "# Emergency Inventory Scan Report\n\n"
        report += f"Generated: {self.inventory['generated']}\n\n"

        report += "## Coverage Summary\n\n"
        report += f"- **Expected**: {self.total_expected_bytes:,} bytes (890.31 GB)\n"
        report += f"- **Found**: {self.inventory['summary']['total_size_bytes']:,} bytes\n"
        report += f"- **Coverage**: {self.inventory['summary']['coverage_vs_os']:.1f}%\n\n"

        report += "## Location Breakdown\n\n"
        report += "| Location | Expected (GB) | Found (GB) | Coverage | Status |\n"
        report += "|----------|---------------|------------|----------|--------|\n"

        for name, data in self.inventory['by_location'].items():
            expected_gb = data['expected_bytes'] / 1e9
            found_gb = data['found_bytes'] / 1e9
            coverage = data['coverage']
            status = '✅' if coverage > 90 else '⚠️' if coverage > 50 else '❌'

            report += f"| {name} | {expected_gb:.2f} | {found_gb:.2f} | {coverage:.1f}% | {status} |\n"

        report += "\n## File Type Distribution\n\n"
        report += "| Extension | Count | Size (GB) |\n"
        report += "|-----------|-------|-----------|\n"

        for ext, stats in sorted(
            self.inventory['summary']['by_type'].items(),
            key=lambda x: x[1]['bytes'],
            reverse=True
        )[:20]:  # Top 20 types
            report += f"| {ext} | {stats['count']:,} | {stats['bytes']/1e9:.2f} |\n"

        report += "\n## Critical Issues\n\n"

        for name, data in self.inventory['by_location'].items():
            if data['coverage'] < 90:
                report += f"- **{name}**: Only {data['coverage']:.1f}% coverage\n"
                if 'error' in data:
                    report += f"  - Error: {data['error']}\n"
                if data['os_status'] != 'SUCCESS':
                    report += f"  - OS Status: {data['os_status']}\n"

        # Save report
        report_file = Path("C:/Projects/OSINT - Foresight/emergency_scan_report.md")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\nReport saved to: {report_file}")


if __name__ == "__main__":
    scanner = EmergencyInventoryScanner()
    sys.exit(scanner.run())

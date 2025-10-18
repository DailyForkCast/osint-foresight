#!/usr/bin/env python3
"""
T05: Multi-Enumerator Parity Test
Verifies Python os.walk matches PowerShell enumeration
"""

import os
import json
import csv
import subprocess
from pathlib import Path
from datetime import datetime
import argparse
import sys

class EnumeratorParityChecker:
    def __init__(self, roots):
        self.roots = [Path(r) for r in roots]
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'test': 'T05_enumerator_parity',
            'locations': {},
            'total_python_files': 0,
            'total_python_bytes': 0,
            'total_powershell_files': 0,
            'total_powershell_bytes': 0,
            'discrepancies': [],
            'status': 'PENDING'
        }

    def enumerate_python(self, root):
        """Enumerate files using Python os.walk"""
        files_dict = {}
        total_bytes = 0
        total_files = 0

        for dirpath, dirnames, filenames in os.walk(root):
            for filename in filenames:
                filepath = Path(dirpath) / filename
                try:
                    stats = filepath.stat()
                    files_dict[str(filepath)] = {
                        'size': stats.st_size,
                        'mtime': stats.st_mtime
                    }
                    total_bytes += stats.st_size
                    total_files += 1
                except Exception as e:
                    files_dict[str(filepath)] = {
                        'size': -1,
                        'error': str(e)
                    }

        return files_dict, total_bytes, total_files

    def enumerate_powershell(self, root):
        """Enumerate files using PowerShell"""
        try:
            # PowerShell command to get all files with size
            cmd = f'''powershell -Command "
            Get-ChildItem -Path '{root}' -Recurse -File -ErrorAction SilentlyContinue |
            Select-Object FullName, Length |
            ConvertTo-Json
            "'''

            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)

            if result.returncode != 0:
                return {}, 0, 0

            # Parse PowerShell JSON output
            try:
                ps_data = json.loads(result.stdout)
                if not isinstance(ps_data, list):
                    ps_data = [ps_data] if ps_data else []

                files_dict = {}
                total_bytes = 0
                total_files = 0

                for item in ps_data:
                    if 'FullName' in item and 'Length' in item:
                        path = item['FullName']
                        size = item['Length'] if item['Length'] is not None else 0
                        files_dict[path] = {'size': size}
                        total_bytes += size
                        total_files += 1

                return files_dict, total_bytes, total_files

            except json.JSONDecodeError:
                return {}, 0, 0

        except Exception as e:
            print(f"PowerShell enumeration error: {e}")
            return {}, 0, 0

    def compare_enumerations(self, python_files, ps_files, location):
        """Compare Python and PowerShell enumerations"""
        discrepancies = []

        # Find files only in Python
        python_only = set(python_files.keys()) - set(ps_files.keys())
        for path in python_only:
            discrepancies.append({
                'location': location,
                'path': path,
                'issue': 'PYTHON_ONLY',
                'python_size': python_files[path].get('size', -1),
                'ps_size': 'N/A'
            })

        # Find files only in PowerShell
        ps_only = set(ps_files.keys()) - set(python_files.keys())
        for path in ps_only:
            discrepancies.append({
                'location': location,
                'path': path,
                'issue': 'POWERSHELL_ONLY',
                'python_size': 'N/A',
                'ps_size': ps_files[path].get('size', -1)
            })

        # Check size mismatches for common files
        common_files = set(python_files.keys()) & set(ps_files.keys())
        for path in common_files:
            py_size = python_files[path].get('size', -1)
            ps_size = ps_files[path].get('size', -1)

            if py_size != ps_size and py_size != -1 and ps_size != -1:
                discrepancies.append({
                    'location': location,
                    'path': path,
                    'issue': 'SIZE_MISMATCH',
                    'python_size': py_size,
                    'ps_size': ps_size,
                    'diff': py_size - ps_size
                })

        return discrepancies

    def run(self):
        """Execute parity check"""
        print("\n" + "="*60)
        print("T05: MULTI-ENUMERATOR PARITY TEST")
        print("="*60)

        all_discrepancies = []

        for root in self.roots:
            if not root.exists():
                print(f"\nSkipping non-existent: {root}")
                continue

            print(f"\nChecking parity for: {root}")

            # Python enumeration
            print("  Running Python enumeration...")
            py_files, py_bytes, py_count = self.enumerate_python(root)
            print(f"    Found: {py_count:,} files, {py_bytes:,} bytes")

            # PowerShell enumeration
            print("  Running PowerShell enumeration...")
            ps_files, ps_bytes, ps_count = self.enumerate_powershell(root)
            print(f"    Found: {ps_count:,} files, {ps_bytes:,} bytes")

            # Compare
            print("  Comparing enumerations...")
            discrepancies = self.compare_enumerations(py_files, ps_files, str(root))

            if discrepancies:
                print(f"    Found {len(discrepancies)} discrepancies")
                all_discrepancies.extend(discrepancies)
            else:
                print("    Perfect parity achieved!")

            # Store results
            self.results['locations'][str(root)] = {
                'python_files': py_count,
                'python_bytes': py_bytes,
                'powershell_files': ps_count,
                'powershell_bytes': ps_bytes,
                'discrepancy_count': len(discrepancies),
                'parity': len(discrepancies) == 0
            }

            self.results['total_python_files'] += py_count
            self.results['total_python_bytes'] += py_bytes
            self.results['total_powershell_files'] += ps_count
            self.results['total_powershell_bytes'] += ps_bytes

        self.results['discrepancies'] = all_discrepancies

        # Determine overall status
        if len(all_discrepancies) == 0:
            self.results['status'] = 'PASS'
        elif len(all_discrepancies) < 10:
            self.results['status'] = 'WARN'
        else:
            self.results['status'] = 'FAIL'

        # Save results
        self.save_results()

        # Print summary
        print("\n" + "="*40)
        print("PARITY TEST RESULTS")
        print("="*40)
        print(f"Total discrepancies: {len(all_discrepancies)}")
        print(f"Python total: {self.results['total_python_files']:,} files, {self.results['total_python_bytes']:,} bytes")
        print(f"PowerShell total: {self.results['total_powershell_files']:,} files, {self.results['total_powershell_bytes']:,} bytes")
        print(f"\nStatus: {self.results['status']}")

        return 0 if self.results['status'] == 'PASS' else 1

    def save_results(self):
        """Save parity check results"""
        base_dir = Path("_verification_tests/verify_v21_custom/artifacts")
        base_dir.mkdir(parents=True, exist_ok=True)

        # Save JSON results
        with open(base_dir / "enum_parity_results.json", 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, default=str)

        # Save discrepancies CSV if any
        if self.results['discrepancies']:
            with open(base_dir / "enum_diff.csv", 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['location', 'path', 'issue', 'python_size', 'ps_size', 'diff']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for disc in self.results['discrepancies']:
                    writer.writerow({k: disc.get(k, '') for k in fieldnames})

        print(f"\nResults saved to {base_dir}")


def main():
    parser = argparse.ArgumentParser(description='Enumerator parity check')
    parser.add_argument('--roots', nargs='+', default=[
        'C:/Projects/OSINT - Foresight/data',
        'F:/OSINT_DATA',
        'F:/TED_Data',
        'F:/OSINT_Backups',
        'F:/2025-09-14 Horizons'
    ], help='Root directories to check')

    args = parser.parse_args()

    checker = EnumeratorParityChecker(args.roots)
    return checker.run()


if __name__ == "__main__":
    sys.exit(main())

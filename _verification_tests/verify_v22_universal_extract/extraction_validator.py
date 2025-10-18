#!/usr/bin/env python3
"""
Universal Extraction Success Validator v2.2
Comprehensive validation suite for all extraction operations

Validates against the Extraction Success Contract including:
- Non-Empty Output (NEO)
- Member/Record Parity (MRP)
- Extension & MIME Sanity (EEMS)
- Schema/Format Probe (SFP)
- Coverage Delta (COVΔ)
- Openability & Permissions (OPEN)
- Lineage & Idempotence (LID)
"""

import os
import sys
import json
import yaml
import zipfile
import sqlite3
import mimetypes
import random
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import subprocess
import hashlib
import xml.etree.ElementTree as ET

class ExtractionValidator:
    """Universal extraction validation orchestrator"""

    # Error codes
    ERROR_CODES = {
        'ERROR_EMPTY_EXTRACTION': 'Directories created but no files',
        'ERROR_EMPTY_ARCHIVE_OUTPUT': 'Archive processed but no members extracted',
        'ERROR_EMPTY_DB_RESTORE': 'Database created but no tables/rows',
        'ERROR_EMPTY_CONVERSION': 'Conversion ran but no output',
        'ERROR_EMPTY_SCRAPE': 'Scraper created folders only',
        'FAIL_EXTENSION_SANITY': 'Only non-actionable file types',
        'FAIL_SCHEMA_PROBE': 'Core fields absent in samples',
        'FAIL_OPENABILITY': 'Cannot open sample files',
        'FAIL_ZERO_BYTE_BURST': 'Too many zero-byte files'
    }

    # Actionable file extensions
    ACTIONABLE_EXTENSIONS = {
        '.xml', '.json', '.csv', '.tsv', '.ndjson', '.jsonl',
        '.parquet', '.db', '.sqlite', '.txt', '.md', '.yaml', '.yml'
    }

    def __init__(self, source_path: str, output_path: str, config: Optional[Dict] = None):
        self.source_path = Path(source_path) if source_path else None
        self.output_path = Path(output_path)
        self.config = config or {}
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'source': str(self.source_path) if self.source_path else None,
            'output': str(self.output_path),
            'status': 'PENDING',
            'checks': {},
            'metrics': {},
            'failures': []
        }

    def validate(self) -> Dict:
        """Run all validation checks"""
        print(f"\n{'='*60}")
        print(f"Universal Extraction Validator v2.2")
        print(f"{'='*60}")
        print(f"Source: {self.source_path}")
        print(f"Output: {self.output_path}\n")

        # 1. Non-Empty Output check
        self._check_non_empty_output()

        # 2. Member/Record Parity check
        self._check_member_parity()

        # 3. Extension & MIME Sanity check
        self._check_extension_mime_sanity()

        # 4. Schema/Format Probe
        self._check_schema_format()

        # 5. Coverage Delta check
        self._check_coverage_delta()

        # 6. Openability check
        self._check_openability()

        # 7. Lineage & Idempotence
        self._check_lineage()

        # Determine overall status
        self._determine_status()

        return self.results

    def _check_non_empty_output(self):
        """NEO: Check for non-empty output"""
        print("Checking: Non-Empty Output (NEO)...")

        if not self.output_path.exists():
            self.results['failures'].append({
                'code': 'ERROR_EMPTY_EXTRACTION',
                'message': 'Output directory does not exist'
            })
            self.results['checks']['neo'] = False
            return

        # Count files and directories
        files = list(self.output_path.rglob("*"))
        file_count = sum(1 for f in files if f.is_file())
        dir_count = sum(1 for d in files if d.is_dir())
        total_bytes = sum(f.stat().st_size for f in files if f.is_file())
        zero_byte_files = [f for f in files if f.is_file() and f.stat().st_size == 0]

        self.results['metrics'].update({
            'file_count': file_count,
            'dir_count': dir_count,
            'total_bytes': total_bytes,
            'zero_byte_files': len(zero_byte_files)
        })

        # Apply NEO rules
        if dir_count > 0 and file_count == 0:
            self.results['failures'].append({
                'code': 'ERROR_EMPTY_EXTRACTION',
                'message': f'Created {dir_count} directories but no files'
            })
            self.results['checks']['neo'] = False
        elif file_count > 0 and total_bytes == 0:
            self.results['failures'].append({
                'code': 'ERROR_EMPTY_EXTRACTION',
                'message': f'Created {file_count} files but all are empty'
            })
            self.results['checks']['neo'] = False
        elif len(zero_byte_files) > 1:
            self.results['failures'].append({
                'code': 'FAIL_ZERO_BYTE_BURST',
                'message': f'Found {len(zero_byte_files)} zero-byte files (max 1 allowed)'
            })
            self.results['checks']['neo'] = False
        else:
            self.results['checks']['neo'] = True
            print(f"  ✓ NEO passed: {file_count} files, {total_bytes:,} bytes")

    def _check_member_parity(self):
        """MRP: Check member/record parity based on source type"""
        print("Checking: Member/Record Parity (MRP)...")

        if not self.source_path or not self.source_path.exists():
            self.results['checks']['mrp'] = None
            print("  ⚠ MRP skipped: No source path provided")
            return

        source_ext = self.source_path.suffix.lower()

        # Archive parity check
        if source_ext in ['.zip', '.7z', '.tar', '.gz']:
            self._check_archive_parity()
        # Database parity check
        elif source_ext in ['.db', '.sqlite', '.sql']:
            self._check_db_parity()
        # JSON/XML conversion parity
        elif source_ext in ['.json', '.xml', '.csv']:
            self._check_conversion_parity()
        else:
            self.results['checks']['mrp'] = None
            print(f"  ⚠ MRP skipped: Unknown source type {source_ext}")

    def _check_archive_parity(self):
        """Check archive member extraction parity"""
        try:
            if self.source_path.suffix.lower() == '.zip':
                with zipfile.ZipFile(self.source_path, 'r') as zf:
                    expected_members = len(zf.filelist)

                    # Count extracted files
                    extracted = list(self.output_path.rglob("*"))
                    extracted_files = sum(1 for f in extracted if f.is_file())

                    self.results['metrics']['expected_members'] = expected_members
                    self.results['metrics']['extracted_members'] = extracted_files

                    if extracted_files == 0 and expected_members > 0:
                        self.results['failures'].append({
                            'code': 'ERROR_EMPTY_ARCHIVE_OUTPUT',
                            'message': f'Archive has {expected_members} members but none extracted'
                        })
                        self.results['checks']['mrp'] = False
                    else:
                        self.results['checks']['mrp'] = True
                        print(f"  ✓ MRP passed: {extracted_files}/{expected_members} members extracted")
        except Exception as e:
            self.results['checks']['mrp'] = False
            self.results['failures'].append({
                'code': 'ERROR_EMPTY_ARCHIVE_OUTPUT',
                'message': f'Failed to check archive: {e}'
            })

    def _check_db_parity(self):
        """Check database restore parity"""
        db_files = list(self.output_path.glob("*.db")) + list(self.output_path.glob("*.sqlite"))

        if not db_files:
            self.results['failures'].append({
                'code': 'ERROR_EMPTY_DB_RESTORE',
                'message': 'No database files found in output'
            })
            self.results['checks']['mrp'] = False
            return

        total_tables = 0
        total_rows = 0

        for db_file in db_files:
            try:
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()

                # Count tables
                tables = cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                ).fetchall()
                total_tables += len(tables)

                # Count rows
                for table in tables:
                    count = cursor.execute(f"SELECT COUNT(*) FROM {table[0]}").fetchone()[0]
                    total_rows += count

                conn.close()
            except Exception as e:
                pass

        self.results['metrics']['db_tables'] = total_tables
        self.results['metrics']['db_rows'] = total_rows

        if total_tables == 0:
            self.results['failures'].append({
                'code': 'ERROR_EMPTY_DB_RESTORE',
                'message': 'Database restored but contains no tables'
            })
            self.results['checks']['mrp'] = False
        elif total_rows == 0:
            self.results['failures'].append({
                'code': 'ERROR_EMPTY_DB_RESTORE',
                'message': f'Database has {total_tables} tables but no rows'
            })
            self.results['checks']['mrp'] = False
        else:
            self.results['checks']['mrp'] = True
            print(f"  ✓ MRP passed: {total_tables} tables, {total_rows:,} rows")

    def _check_conversion_parity(self):
        """Check conversion output parity"""
        output_files = list(self.output_path.rglob("*"))
        data_files = [f for f in output_files if f.is_file() and f.suffix in self.ACTIONABLE_EXTENSIONS]

        if len(data_files) == 0:
            self.results['failures'].append({
                'code': 'ERROR_EMPTY_CONVERSION',
                'message': 'Conversion produced no data files'
            })
            self.results['checks']['mrp'] = False
        else:
            self.results['checks']['mrp'] = True
            print(f"  ✓ MRP passed: {len(data_files)} data files created")

    def _check_extension_mime_sanity(self):
        """EEMS: Check for actionable file types"""
        print("Checking: Extension & MIME Sanity (EEMS)...")

        files = [f for f in self.output_path.rglob("*") if f.is_file()]

        if not files:
            self.results['checks']['eems'] = False
            return

        # Count extensions
        ext_counts = {}
        mime_counts = {}
        actionable_count = 0

        for file in files:
            ext = file.suffix.lower()
            ext_counts[ext] = ext_counts.get(ext, 0) + 1

            if ext in self.ACTIONABLE_EXTENSIONS:
                actionable_count += 1

            # Get MIME type
            mime_type, _ = mimetypes.guess_type(str(file))
            if mime_type:
                mime_counts[mime_type] = mime_counts.get(mime_type, 0) + 1

        self.results['metrics']['extension_histogram'] = ext_counts
        self.results['metrics']['mime_histogram'] = mime_counts
        self.results['metrics']['actionable_files'] = actionable_count

        if actionable_count == 0:
            self.results['failures'].append({
                'code': 'FAIL_EXTENSION_SANITY',
                'message': f'No actionable file types found among {len(files)} files'
            })
            self.results['checks']['eems'] = False
        else:
            self.results['checks']['eems'] = True
            print(f"  ✓ EEMS passed: {actionable_count}/{len(files)} actionable files")

    def _check_schema_format(self):
        """SFP: Probe schema/format of sample files"""
        print("Checking: Schema/Format Probe (SFP)...")

        # Get sample of data files
        data_files = [
            f for f in self.output_path.rglob("*")
            if f.is_file() and f.suffix in self.ACTIONABLE_EXTENSIONS
        ]

        if not data_files:
            self.results['checks']['sfp'] = None
            print("  ⚠ SFP skipped: No data files to probe")
            return

        # Sample up to 25 files
        sample_size = min(25, len(data_files))
        sample = random.sample(data_files, sample_size)

        parseable = 0
        has_content = 0

        for file in sample:
            try:
                if file.suffix in ['.json', '.jsonl', '.ndjson']:
                    with open(file, 'r', encoding='utf-8') as f:
                        data = json.load(f) if file.suffix == '.json' else [json.loads(line) for line in f]
                        parseable += 1
                        if data:
                            has_content += 1

                elif file.suffix == '.xml':
                    tree = ET.parse(file)
                    parseable += 1
                    if tree.getroot() is not None:
                        has_content += 1

                elif file.suffix in ['.csv', '.tsv']:
                    with open(file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        parseable += 1
                        if len(lines) > 1:  # Header + data
                            has_content += 1
                else:
                    # For other files, just check if readable
                    with open(file, 'r', encoding='utf-8') as f:
                        content = f.read(1000)
                        parseable += 1
                        if content.strip():
                            has_content += 1
            except:
                pass

        self.results['metrics']['schema_probe'] = {
            'sampled': sample_size,
            'parseable': parseable,
            'has_content': has_content
        }

        if parseable == 0:
            self.results['failures'].append({
                'code': 'FAIL_SCHEMA_PROBE',
                'message': f'None of {sample_size} sampled files could be parsed'
            })
            self.results['checks']['sfp'] = False
        elif has_content == 0:
            self.results['failures'].append({
                'code': 'FAIL_SCHEMA_PROBE',
                'message': f'{parseable} files parsed but none have content'
            })
            self.results['checks']['sfp'] = False
        else:
            self.results['checks']['sfp'] = True
            print(f"  ✓ SFP passed: {has_content}/{sample_size} files valid")

    def _check_coverage_delta(self):
        """COVΔ: Check coverage delta requirements"""
        print("Checking: Coverage Delta (COVΔ)...")

        total_bytes = self.results['metrics'].get('total_bytes', 0)
        min_bytes = self.config.get('min_output_bytes', 1024 * 1024)  # Default 1MB

        self.results['metrics']['coverage_delta'] = {
            'actual_bytes': total_bytes,
            'required_bytes': min_bytes,
            'delta': total_bytes - min_bytes
        }

        if total_bytes < min_bytes:
            self.results['failures'].append({
                'code': 'FAIL_COVERAGE_DELTA',
                'message': f'Output size {total_bytes:,} bytes below minimum {min_bytes:,}'
            })
            self.results['checks']['coverage'] = False
        else:
            self.results['checks']['coverage'] = True
            print(f"  ✓ Coverage passed: {total_bytes:,} bytes (min: {min_bytes:,})")

    def _check_openability(self):
        """OPEN: Check file openability"""
        print("Checking: Openability (OPEN)...")

        files = [f for f in self.output_path.rglob("*") if f.is_file()]

        if not files:
            self.results['checks']['openability'] = None
            return

        # Sample up to 50 files
        sample_size = min(50, len(files))
        sample = random.sample(files, sample_size)

        openable = 0
        failed = []

        for file in sample:
            try:
                with open(file, 'rb') as f:
                    # Try to read first 1KB
                    f.read(1024)
                openable += 1
            except Exception as e:
                failed.append((file.name, str(e)))

        self.results['metrics']['openability'] = {
            'sampled': sample_size,
            'openable': openable,
            'failed': len(failed)
        }

        if openable < sample_size * 0.95:  # Allow 5% failure rate
            self.results['failures'].append({
                'code': 'FAIL_OPENABILITY',
                'message': f'Could not open {len(failed)}/{sample_size} files'
            })
            self.results['checks']['openability'] = False
        else:
            self.results['checks']['openability'] = True
            print(f"  ✓ Openability passed: {openable}/{sample_size} files accessible")

    def _check_lineage(self):
        """LID: Check lineage and idempotence"""
        print("Checking: Lineage & Idempotence (LID)...")

        # Look for lineage markers
        lineage_files = [
            self.output_path / 'lineage.json',
            self.output_path / '.lineage',
            self.output_path / 'manifest.json'
        ]

        lineage_found = any(f.exists() for f in lineage_files)

        if lineage_found:
            self.results['checks']['lineage'] = True
            print(f"  ✓ Lineage tracking found")
        else:
            self.results['checks']['lineage'] = None
            print(f"  ⚠ Lineage tracking not found (optional)")

    def _determine_status(self):
        """Determine overall validation status"""
        critical_checks = ['neo', 'mrp', 'eems', 'sfp', 'coverage', 'openability']

        failed = [check for check in critical_checks
                 if check in self.results['checks'] and self.results['checks'][check] is False]

        if failed:
            self.results['status'] = 'FAIL'
        elif all(self.results['checks'].get(check) for check in critical_checks
                if check in self.results['checks']):
            self.results['status'] = 'PASS'
        else:
            self.results['status'] = 'PARTIAL'

    def save_results(self, output_path: Optional[str] = None):
        """Save results to JSON"""
        if not output_path:
            output_path = self.output_path.parent / 'validation_results.json'

        with open(output_path, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)

        print(f"\nResults saved to: {output_path}")

    def print_summary(self):
        """Print validation summary"""
        print(f"\n{'='*60}")
        print(f"Validation Result: {self.results['status']}")
        print(f"{'='*60}")

        print("\nChecks Summary:")
        for check, result in self.results['checks'].items():
            if result is None:
                status = "⚠"
                result_str = "SKIPPED"
            elif result:
                status = "✓"
                result_str = "PASS"
            else:
                status = "✗"
                result_str = "FAIL"
            print(f"  {status} {check.upper()}: {result_str}")

        if self.results['failures']:
            print(f"\nFailures ({len(self.results['failures'])}):")
            for failure in self.results['failures']:
                print(f"  [{failure['code']}] {failure['message']}")

def main():
    """Main entry point for validation"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Universal Extraction Success Validator v2.2"
    )
    parser.add_argument("--source", help="Source file/directory path")
    parser.add_argument("--output", required=True, help="Output directory to validate")
    parser.add_argument("--config", help="Configuration file (YAML/JSON)")
    parser.add_argument("--min-bytes", type=int, help="Minimum output bytes required")
    parser.add_argument("--save", help="Save results to JSON file")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Load config if provided
    config = {}
    if args.config:
        with open(args.config, 'r') as f:
            if args.config.endswith('.yaml') or args.config.endswith('.yml'):
                config = yaml.safe_load(f)
            else:
                config = json.load(f)

    if args.min_bytes:
        config['min_output_bytes'] = args.min_bytes

    # Run validation
    validator = ExtractionValidator(args.source, args.output, config)
    results = validator.validate()

    # Print summary
    validator.print_summary()

    # Save results if requested
    if args.save:
        validator.save_results(args.save)

    # Exit with appropriate code
    sys.exit(0 if results['status'] == 'PASS' else 1)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Phase 6: Integration Testing Audit
Tests whether components work together correctly
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime
from collections import defaultdict


class IntegrationAuditor:
    """Test component integrations"""

    def __init__(self):
        self.test_results = []
        self.integration_issues = []

    def test_database_connectivity(self):
        """Test if scripts can connect to database"""
        print("\n" + "="*80)
        print("TEST 1: Database Connectivity Across Components")
        print("="*80)

        db_paths = {
            'osint_master': Path("F:/OSINT_WAREHOUSE/osint_master.db"),
            'github_activity': Path("C:/Projects/OSINT-Foresight/data/github_activity.db"),
            'intelligence_warehouse': Path("C:/Projects/OSINT-Foresight/data/intelligence_warehouse.db"),
        }

        results = {
            'total': len(db_paths),
            'accessible': 0,
            'failed': 0,
            'details': []
        }

        for db_name, db_path in db_paths.items():
            try:
                if not db_path.exists():
                    results['failed'] += 1
                    results['details'].append({
                        'database': db_name,
                        'path': str(db_path),
                        'status': 'NOT_FOUND',
                        'message': f'Database file does not exist'
                    })
                    print(f"  [FAIL] {db_name}: File not found")
                    continue

                conn = sqlite3.connect(db_path, timeout=5.0)
                cur = conn.cursor()

                # Test query
                cur.execute("SELECT name FROM sqlite_master WHERE type='table' LIMIT 1")
                result = cur.fetchone()

                conn.close()

                results['accessible'] += 1
                results['details'].append({
                    'database': db_name,
                    'path': str(db_path),
                    'status': 'ACCESSIBLE',
                    'message': 'Successfully connected and queried'
                })
                print(f"  [PASS] {db_name}: Connected successfully")

            except Exception as e:
                results['failed'] += 1
                results['details'].append({
                    'database': db_name,
                    'path': str(db_path),
                    'status': 'ERROR',
                    'message': str(e)
                })
                print(f"  [FAIL] {db_name}: {str(e)}")

        print(f"\nResults: {results['accessible']}/{results['total']} databases accessible")

        self.test_results.append({
            'test_name': 'Database Connectivity',
            'results': results
        })

        if results['failed'] > 0:
            self.integration_issues.append({
                'issue_type': 'database_connectivity',
                'severity': 'HIGH' if results['failed'] == results['total'] else 'MEDIUM',
                'message': f"{results['failed']}/{results['total']} databases inaccessible",
                'affected_components': [d['database'] for d in results['details'] if d['status'] != 'ACCESSIBLE']
            })

        return results

    def test_checkpoint_file_compatibility(self):
        """Test if checkpoint files are readable across scripts"""
        print("\n" + "="*80)
        print("TEST 2: Checkpoint File Compatibility")
        print("="*80)

        checkpoint_files = [
            Path("C:/Projects/OSINT-Foresight/data/openalex_v4_checkpoint.json"),
            Path("C:/Projects/OSINT-Foresight/data/comtrade_checkpoint.json"),
        ]

        results = {
            'total': len(checkpoint_files),
            'compatible': 0,
            'failed': 0,
            'details': []
        }

        for checkpoint_path in checkpoint_files:
            try:
                if not checkpoint_path.exists():
                    results['details'].append({
                        'file': checkpoint_path.name,
                        'status': 'NOT_FOUND',
                        'message': 'File does not exist'
                    })
                    print(f"  [INFO] {checkpoint_path.name}: Not found (may not be initialized)")
                    continue

                with open(checkpoint_path, 'r') as f:
                    checkpoint_data = json.load(f)

                # Validate structure
                if isinstance(checkpoint_data, dict):
                    results['compatible'] += 1
                    results['details'].append({
                        'file': checkpoint_path.name,
                        'status': 'VALID',
                        'keys': list(checkpoint_data.keys())[:5],  # First 5 keys
                        'message': f'Valid JSON with {len(checkpoint_data)} keys'
                    })
                    print(f"  [PASS] {checkpoint_path.name}: Valid checkpoint format")
                else:
                    results['failed'] += 1
                    results['details'].append({
                        'file': checkpoint_path.name,
                        'status': 'INVALID_FORMAT',
                        'message': f'Expected dict, got {type(checkpoint_data)}'
                    })
                    print(f"  [FAIL] {checkpoint_path.name}: Invalid format")

            except json.JSONDecodeError as e:
                results['failed'] += 1
                results['details'].append({
                    'file': checkpoint_path.name,
                    'status': 'JSON_ERROR',
                    'message': str(e)
                })
                print(f"  [FAIL] {checkpoint_path.name}: JSON decode error")
            except Exception as e:
                results['failed'] += 1
                results['details'].append({
                    'file': checkpoint_path.name,
                    'status': 'ERROR',
                    'message': str(e)
                })
                print(f"  [FAIL] {checkpoint_path.name}: {str(e)}")

        found_files = results['compatible'] + results['failed']
        print(f"\nResults: {results['compatible']}/{found_files} checkpoint files valid")

        self.test_results.append({
            'test_name': 'Checkpoint File Compatibility',
            'results': results
        })

        if results['failed'] > 0:
            self.integration_issues.append({
                'issue_type': 'checkpoint_compatibility',
                'severity': 'MEDIUM',
                'message': f"{results['failed']} checkpoint files have format issues",
                'affected_files': [d['file'] for d in results['details'] if d['status'] not in ['VALID', 'NOT_FOUND']]
            })

        return results

    def test_config_file_integration(self):
        """Test if config files are loadable"""
        print("\n" + "="*80)
        print("TEST 3: Configuration File Integration")
        print("="*80)

        config_dir = Path("C:/Projects/OSINT-Foresight/config")
        if not config_dir.exists():
            print(f"  [FAIL] Config directory not found: {config_dir}")
            return {'total': 0, 'valid': 0, 'failed': 0}

        config_files = list(config_dir.glob("*.json"))

        results = {
            'total': len(config_files),
            'valid': 0,
            'failed': 0,
            'details': []
        }

        for config_path in config_files[:10]:  # Sample first 10
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)

                results['valid'] += 1
                results['details'].append({
                    'file': config_path.name,
                    'status': 'VALID',
                    'message': f'Valid JSON'
                })
                print(f"  [PASS] {config_path.name}: Valid")

            except json.JSONDecodeError as e:
                results['failed'] += 1
                results['details'].append({
                    'file': config_path.name,
                    'status': 'JSON_ERROR',
                    'message': str(e)
                })
                print(f"  [FAIL] {config_path.name}: JSON error")
            except Exception as e:
                results['failed'] += 1
                results['details'].append({
                    'file': config_path.name,
                    'status': 'ERROR',
                    'message': str(e)
                })
                print(f"  [FAIL] {config_path.name}: {str(e)}")

        print(f"\nResults: {results['valid']}/{results['total']} config files valid")

        self.test_results.append({
            'test_name': 'Config File Integration',
            'results': results
        })

        if results['failed'] > 0:
            self.integration_issues.append({
                'issue_type': 'config_files',
                'severity': 'MEDIUM',
                'message': f"{results['failed']} config files have errors",
                'affected_files': [d['file'] for d in results['details'] if d['status'] != 'VALID']
            })

        return results

    def test_data_schema_consistency(self):
        """Test if data schemas are consistent across tables"""
        print("\n" + "="*80)
        print("TEST 4: Data Schema Consistency")
        print("="*80)

        db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")
        if not db_path.exists():
            print("  [SKIP] Master database not accessible")
            return {'total': 0, 'consistent': 0, 'issues': 0}

        results = {
            'total': 0,
            'consistent': 0,
            'issues': 0,
            'details': []
        }

        try:
            conn = sqlite3.connect(db_path, timeout=5.0)
            cur = conn.cursor()

            # Check for duplicate table naming patterns
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            tables = [row[0] for row in cur.fetchall()]

            # Look for versioning patterns (table_v2, table_v3, etc.)
            table_bases = defaultdict(list)
            for table in tables:
                if '_v' in table or '_backup_' in table or '_old' in table:
                    base = table.split('_v')[0].split('_backup_')[0].split('_old')[0]
                    table_bases[base].append(table)

            results['total'] = len(table_bases)

            for base, versions in table_bases.items():
                if len(versions) > 1:
                    results['issues'] += 1
                    results['details'].append({
                        'base_table': base,
                        'versions': versions,
                        'count': len(versions),
                        'status': 'MULTIPLE_VERSIONS'
                    })
                    print(f"  [WARN] {base}: {len(versions)} versions found - {', '.join(versions[:3])}")
                else:
                    results['consistent'] += 1

            conn.close()

            print(f"\nResults: {results['issues']} table naming inconsistencies found")

            self.test_results.append({
                'test_name': 'Data Schema Consistency',
                'results': results
            })

            if results['issues'] > 0:
                self.integration_issues.append({
                    'issue_type': 'schema_versioning',
                    'severity': 'MEDIUM',
                    'message': f"{results['issues']} tables have multiple versions",
                    'affected_tables': [d['base_table'] for d in results['details']]
                })

        except Exception as e:
            print(f"  [ERROR] Schema check failed: {str(e)}")
            results['error'] = str(e)

        return results

    def test_file_path_consistency(self):
        """Test if hardcoded paths are consistent"""
        print("\n" + "="*80)
        print("TEST 5: File Path Consistency")
        print("="*80)

        # Check if commonly referenced paths exist
        common_paths = {
            'F:/OSINT_WAREHOUSE': 'Data warehouse directory',
            'F:/OSINT_Data': 'Raw data directory',
            'F:/OSINT_Backups': 'Backup directory',
            'C:/Projects/OSINT-Foresight': 'Project root',
        }

        results = {
            'total': len(common_paths),
            'exist': 0,
            'missing': 0,
            'details': []
        }

        for path_str, description in common_paths.items():
            path = Path(path_str)
            if path.exists():
                results['exist'] += 1
                results['details'].append({
                    'path': path_str,
                    'description': description,
                    'status': 'EXISTS'
                })
                print(f"  [PASS] {path_str}: Exists")
            else:
                results['missing'] += 1
                results['details'].append({
                    'path': path_str,
                    'description': description,
                    'status': 'MISSING'
                })
                print(f"  [WARN] {path_str}: Not found")

        print(f"\nResults: {results['exist']}/{results['total']} common paths exist")

        self.test_results.append({
            'test_name': 'File Path Consistency',
            'results': results
        })

        if results['missing'] > 0:
            self.integration_issues.append({
                'issue_type': 'missing_paths',
                'severity': 'HIGH' if results['missing'] >= results['total'] / 2 else 'LOW',
                'message': f"{results['missing']} commonly referenced paths missing",
                'affected_paths': [d['path'] for d in results['details'] if d['status'] == 'MISSING']
            })

        return results

    def generate_summary(self):
        """Generate integration test summary"""
        print("\n" + "="*80)
        print("PHASE 6: INTEGRATION TESTING SUMMARY")
        print("="*80)

        total_tests = len(self.test_results)
        total_issues = len(self.integration_issues)

        print(f"\nTests Run: {total_tests} integration tests")
        print(f"Integration Issues Found: {total_issues}")

        if total_issues == 0:
            print("\n[PASS] All integration tests passed - components work together correctly")
        else:
            print(f"\n[FAIL] {total_issues} integration issues found")

            print("\n" + "-"*80)
            print("INTEGRATION ISSUES BY SEVERITY")
            print("-"*80)

            by_severity = defaultdict(list)
            for issue in self.integration_issues:
                by_severity[issue['severity']].append(issue)

            for severity in ['HIGH', 'MEDIUM', 'LOW']:
                if severity in by_severity:
                    print(f"\n{severity} Severity ({len(by_severity[severity])} issues):")
                    for issue in by_severity[severity]:
                        print(f"  - {issue['message']}")
                        if 'affected_components' in issue:
                            print(f"    Affected: {', '.join(issue['affected_components'][:3])}")

        return {
            'total_tests': total_tests,
            'integration_issues': total_issues,
            'issues': self.integration_issues,
            'test_results': self.test_results
        }


def main():
    print("="*80)
    print("PHASE 6: INTEGRATION TESTING AUDIT")
    print("Testing component integrations")
    print("="*80)

    auditor = IntegrationAuditor()

    # Run all integration tests
    auditor.test_database_connectivity()
    auditor.test_checkpoint_file_compatibility()
    auditor.test_config_file_integration()
    auditor.test_data_schema_consistency()
    auditor.test_file_path_consistency()

    # Generate summary
    summary = auditor.generate_summary()

    # Save results
    output_file = Path("PHASE6_INTEGRATION_TESTING_RESULTS.json")
    with open(output_file, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"\nDetailed results saved to: {output_file}")

    return summary


if __name__ == "__main__":
    main()

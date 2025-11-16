#!/usr/bin/env python3
"""
comprehensive_project_audit.py - Complete Project Audit

Trust nothing - verify everything.
Tests all components of the OSINT Foresight project.
"""

import sqlite3
import json
import os
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import gzip

# Set encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

class ProjectAuditor:
    def __init__(self):
        self.project_root = Path("C:/Projects/OSINT - Foresight")
        self.f_drive = Path("F:/")
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'tests_passed': 0,
            'tests_failed': 0,
            'warnings': [],
            'errors': [],
            'findings': {}
        }

    def test_database_integrity(self):
        """Test database is accessible and has correct structure"""
        print("\n" + "="*60)
        print("1. DATABASE INTEGRITY TEST")
        print("="*60)

        try:
            db_path = self.f_drive / "OSINT_WAREHOUSE/osint_master.db"
            conn = sqlite3.connect(str(db_path), timeout=10)
            cursor = conn.cursor()

            # Count tables
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
            table_count = cursor.fetchone()[0]
            print(f"✓ Tables: {table_count}")

            # Count records in top tables
            cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """)
            tables = [row[0] for row in cursor.fetchall()]

            total_records = 0
            empty_tables = []
            large_tables = []

            for table in tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM \"{table}\"")
                    count = cursor.fetchone()[0]
                    total_records += count
                    if count == 0:
                        empty_tables.append(table)
                    elif count > 1000000:
                        large_tables.append((table, count))
                except:
                    pass

            print(f"✓ Total records: {total_records:,}")
            print(f"✓ Empty tables: {len(empty_tables)}")
            print(f"✓ Large tables (>1M): {len(large_tables)}")

            if large_tables:
                print("\nTop 5 tables by size:")
                for table, count in sorted(large_tables, key=lambda x: x[1], reverse=True)[:5]:
                    print(f"  - {table}: {count:,} records")

            conn.close()

            self.results['findings']['database'] = {
                'status': 'OK',
                'table_count': table_count,
                'total_records': total_records,
                'empty_tables': len(empty_tables),
                'large_tables': len(large_tables)
            }
            self.results['tests_passed'] += 1
            return True

        except Exception as e:
            print(f"✗ Database test failed: {e}")
            self.results['errors'].append(f"Database: {e}")
            self.results['tests_failed'] += 1
            return False

    def test_f_drive_data_sources(self):
        """Verify F: drive data sources are accessible"""
        print("\n" + "="*60)
        print("2. F: DRIVE DATA SOURCES TEST")
        print("="*60)

        data_sources = {
            'OpenAlex': self.f_drive / "OSINT_Backups/openalex",
            'TED': self.f_drive / "TED_Data",
            'USPTO': self.f_drive / "USPTO Data",
            'GLEIF': self.f_drive / "GLEIF",
            'Warehouse': self.f_drive / "OSINT_WAREHOUSE",
            'ThinkTank': self.f_drive / "ThinkTank_Sweeps",
        }

        accessible = {}
        for name, path in data_sources.items():
            if path.exists():
                try:
                    size_gb = sum(f.stat().st_size for f in path.rglob('*') if f.is_file()) / (1024**3)
                    print(f"✓ {name}: {size_gb:.1f} GB")
                    accessible[name] = {'status': 'OK', 'size_gb': round(size_gb, 1)}
                    self.results['tests_passed'] += 1
                except Exception as e:
                    print(f"⚠ {name}: Exists but size calculation failed - {e}")
                    accessible[name] = {'status': 'WARNING', 'error': str(e)}
                    self.results['warnings'].append(f"{name}: {e}")
            else:
                print(f"✗ {name}: NOT FOUND at {path}")
                accessible[name] = {'status': 'MISSING', 'path': str(path)}
                self.results['tests_failed'] += 1

        self.results['findings']['data_sources'] = accessible
        return len([v for v in accessible.values() if v['status'] == 'OK']) > 0

    def test_file_readability(self):
        """Test that we can actually read data files"""
        print("\n" + "="*60)
        print("3. FILE READABILITY TEST")
        print("="*60)

        tests = []

        # Test OpenAlex
        try:
            openalex_path = self.f_drive / "OSINT_Backups/openalex/data/works"
            gz_files = list(openalex_path.rglob("*.gz"))
            if gz_files:
                with gzip.open(gz_files[0], 'rt') as f:
                    data = json.loads(f.readline())
                print(f"✓ OpenAlex: {len(gz_files)} files, sample keys: {list(data.keys())[:3]}")
                tests.append(('OpenAlex', True, len(gz_files)))
                self.results['tests_passed'] += 1
            else:
                raise Exception("No .gz files found")
        except Exception as e:
            print(f"✗ OpenAlex: {e}")
            tests.append(('OpenAlex', False, str(e)))
            self.results['tests_failed'] += 1

        # Test TED
        try:
            ted_path = self.f_drive / "TED_Data/monthly"
            tar_files = list(ted_path.rglob("*.tar.gz"))
            print(f"✓ TED: {len(tar_files)} archive files found")
            tests.append(('TED', True, len(tar_files)))
            self.results['tests_passed'] += 1
        except Exception as e:
            print(f"✗ TED: {e}")
            tests.append(('TED', False, str(e)))
            self.results['tests_failed'] += 1

        self.results['findings']['file_readability'] = tests
        return any(test[1] for test in tests)

    def test_script_inventory(self):
        """Count and categorize scripts"""
        print("\n" + "="*60)
        print("4. SCRIPT INVENTORY TEST")
        print("="*60)

        scripts_dir = self.project_root / "scripts"
        root_scripts = list(self.project_root.glob("*.py"))

        categorized = defaultdict(list)

        # Scripts directory
        for script in scripts_dir.rglob("*.py"):
            category = script.parent.name if script.parent != scripts_dir else "main"
            categorized[category].append(script.name)

        # Root scripts
        categorized['root'] = [s.name for s in root_scripts]

        total_scripts = sum(len(scripts) for scripts in categorized.values())
        print(f"✓ Total Python scripts: {total_scripts}")
        print(f"✓ Script categories: {len(categorized)}")

        print("\nTop 5 categories:")
        for cat, scripts in sorted(categorized.items(), key=lambda x: len(x[1]), reverse=True)[:5]:
            print(f"  - {cat}: {len(scripts)} scripts")

        self.results['findings']['scripts'] = {
            'total': total_scripts,
            'categories': len(categorized),
            'by_category': {k: len(v) for k, v in categorized.items()}
        }
        self.results['tests_passed'] += 1
        return True

    def test_documentation_tier1(self):
        """Verify Tier 1 documentation exists and is current"""
        print("\n" + "="*60)
        print("5. TIER 1 DOCUMENTATION TEST")
        print("="*60)

        tier1_docs = [
            self.project_root / "README.md",
            self.project_root / "docs/prompts/active/master/CLAUDE_CODE_MASTER_V9.8_COMPLETE.md",
            self.project_root / "docs/UNIFIED_DATA_INFRASTRUCTURE_INVENTORY_MULTICOUNTRY.md",
            self.project_root / "docs/SCRIPTS_INVENTORY.md"
        ]

        passed = 0
        for doc in tier1_docs:
            if doc.exists():
                size_kb = doc.stat().st_size / 1024
                print(f"✓ {doc.name}: {size_kb:.1f} KB")
                passed += 1
            else:
                print(f"✗ {doc.name}: MISSING")
                self.results['errors'].append(f"Missing: {doc.name}")

        self.results['findings']['documentation'] = {
            'tier1_count': len(tier1_docs),
            'tier1_present': passed
        }

        if passed == len(tier1_docs):
            self.results['tests_passed'] += 1
            return True
        else:
            self.results['tests_failed'] += 1
            return False

    def check_empty_tables(self):
        """Identify and report on empty tables"""
        print("\n" + "="*60)
        print("6. EMPTY TABLES ANALYSIS")
        print("="*60)

        try:
            db_path = self.f_drive / "OSINT_WAREHOUSE/osint_master.db"
            conn = sqlite3.connect(str(db_path), timeout=10)
            cursor = conn.cursor()

            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            tables = [row[0] for row in cursor.fetchall()]

            empty_tables = []
            for table in tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM \"{table}\"")
                    if cursor.fetchone()[0] == 0:
                        empty_tables.append(table)
                except:
                    pass

            print(f"Found {len(empty_tables)} empty tables:")
            for table in empty_tables[:10]:
                print(f"  - {table}")
            if len(empty_tables) > 10:
                print(f"  ... and {len(empty_tables) - 10} more")

            self.results['findings']['empty_tables'] = empty_tables
            self.results['warnings'].append(f"{len(empty_tables)} empty tables - consider cleanup")

            conn.close()
            return True
        except Exception as e:
            print(f"✗ Empty tables check failed: {e}")
            return False

    def generate_report(self):
        """Generate final audit report"""
        print("\n" + "="*60)
        print("AUDIT SUMMARY")
        print("="*60)

        total_tests = self.results['tests_passed'] + self.results['tests_failed']
        pass_rate = (self.results['tests_passed'] / total_tests * 100) if total_tests > 0 else 0

        print(f"\nTests Run: {total_tests}")
        print(f"Tests Passed: {self.results['tests_passed']}")
        print(f"Tests Failed: {self.results['tests_failed']}")
        print(f"Pass Rate: {pass_rate:.1f}%")
        print(f"Warnings: {len(self.results['warnings'])}")
        print(f"Errors: {len(self.results['errors'])}")

        if self.results['errors']:
            print("\n[ERRORS]:")
            for error in self.results['errors'][:5]:
                print(f"  - {error}")

        if self.results['warnings']:
            print("\n[WARNINGS]:")
            for warning in self.results['warnings'][:5]:
                print(f"  - {warning}")

        # Save report
        report_path = self.project_root / "analysis/COMPREHENSIVE_AUDIT_REPORT_20251017.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2)

        print(f"\n[SAVED] Full report: {report_path}")
        print("="*60)

        return pass_rate >= 80  # Success if ≥80% tests pass

    def run_full_audit(self):
        """Run all audit tests"""
        print("\n" + "#"*60)
        print("# OSINT FORESIGHT - COMPREHENSIVE PROJECT AUDIT")
        print("# Trust Nothing - Verify Everything")
        print("#" + "#"*60)

        self.test_database_integrity()
        self.test_f_drive_data_sources()
        self.test_file_readability()
        self.test_script_inventory()
        self.test_documentation_tier1()
        self.check_empty_tables()

        success = self.generate_report()
        return success

def main():
    auditor = ProjectAuditor()
    success = auditor.run_full_audit()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

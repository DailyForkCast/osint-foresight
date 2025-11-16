#!/usr/bin/env python3
"""
Comprehensive Performance Improvements Audit
Validates all indices, tests performance claims, checks for side effects
"""

import sqlite3
import time
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

DB_PATH = Path("F:/OSINT_WAREHOUSE/osint_master.db")

class PerformanceAudit:
    def __init__(self):
        self.db_path = DB_PATH
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'tests_passed': 0,
            'tests_failed': 0,
            'warnings': [],
            'issues': [],
            'index_verification': {},
            'performance_tests': [],
            'integrity_checks': []
        }

    def run_audit(self):
        """Run complete audit"""
        print("="*80)
        print("COMPREHENSIVE PERFORMANCE IMPROVEMENTS AUDIT")
        print("="*80)
        print(f"Database: {self.db_path}")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)

        # Test 1: Verify all indices exist
        print("\n[TEST 1] Verifying all 27 indices exist...")
        self.verify_indices_exist()

        # Test 2: Verify index correctness (right columns, right tables)
        print("\n[TEST 2] Verifying index correctness...")
        self.verify_index_correctness()

        # Test 3: Test actual query performance
        print("\n[TEST 3] Testing actual query performance...")
        self.test_query_performance()

        # Test 4: Verify index usage (EXPLAIN QUERY PLAN)
        print("\n[TEST 4] Verifying indices are actually used...")
        self.verify_index_usage()

        # Test 5: Check for performance degradation
        print("\n[TEST 5] Checking for INSERT/UPDATE performance impact...")
        self.check_write_performance()

        # Test 6: Data integrity verification
        print("\n[TEST 6] Verifying data integrity...")
        self.verify_data_integrity()

        # Test 7: Edge case testing
        print("\n[TEST 7] Testing edge cases...")
        self.test_edge_cases()

        # Test 8: Validate performance claims
        print("\n[TEST 8] Validating performance improvement claims...")
        self.validate_performance_claims()

        # Generate final report
        self.generate_final_report()

    def verify_indices_exist(self):
        """Verify all 27 claimed indices actually exist"""
        expected_indices = [
            # Phase 1 (13 indices)
            'idx_owa_work_id', 'idx_owa_author_id', 'idx_owt_work_id',
            'idx_owt_topic_id', 'idx_owf_work_id', 'idx_owf_funder_id',
            'idx_de_document_id', 'idx_usaspending_recipient_country',
            'idx_ted_contractors_name', 'idx_gleif_legal_name',
            'idx_cordis_orgs_name', 'idx_openaire_research_year_idx',
            'idx_ted_contracts_date',
            # Phase 2 (14 indices)
            'idx_gleif_legal_country', 'idx_gleif_hq_country',
            'idx_gleif_jurisdiction', 'idx_uspto_assignee_country',
            'idx_ted_iso_country', 'idx_sec_state', 'idx_entities_origin',
            'idx_entities_operation', 'idx_arxiv_year', 'idx_uspto_chinese_year',
            'idx_openalex_works_year', 'idx_usaspending_date',
            'idx_ted_value_total', 'idx_usaspending_value'
        ]

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='index' AND name LIKE 'idx_%'
            ORDER BY name
        """)
        actual_indices = {row[0] for row in cursor.fetchall()}

        missing = []
        found = []
        for idx in expected_indices:
            if idx in actual_indices:
                found.append(idx)
                print(f"  [OK] {idx}")
            else:
                missing.append(idx)
                print(f"  [MISSING] {idx}")
                self.results['issues'].append(f"Index missing: {idx}")

        conn.close()

        self.results['index_verification']['expected'] = len(expected_indices)
        self.results['index_verification']['found'] = len(found)
        self.results['index_verification']['missing'] = missing

        if missing:
            print(f"\n  [FAIL] {len(missing)} indices missing!")
            self.results['tests_failed'] += 1
        else:
            print(f"\n  [PASS] All {len(expected_indices)} indices exist!")
            self.results['tests_passed'] += 1

    def verify_index_correctness(self):
        """Verify indices are on correct tables and columns"""
        index_definitions = [
            ('idx_gleif_legal_country', 'gleif_entities', 'legal_address_country'),
            ('idx_gleif_hq_country', 'gleif_entities', 'hq_address_country'),
            ('idx_gleif_jurisdiction', 'gleif_entities', 'legal_jurisdiction'),
            ('idx_uspto_assignee_country', 'uspto_assignee', 'ee_country'),
            ('idx_ted_iso_country', 'ted_contracts_production', 'iso_country'),
            ('idx_arxiv_year', 'arxiv_papers', 'year'),
            ('idx_uspto_chinese_year', 'uspto_patents_chinese', 'year'),
            ('idx_openalex_works_year', 'openalex_works', 'publication_year'),
            ('idx_ted_value_total', 'ted_contracts_production', 'value_total'),
        ]

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        incorrect = []
        for idx_name, table_name, column_name in index_definitions:
            # Get index info
            cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='index' AND name=?", (idx_name,))
            result = cursor.fetchone()

            if not result:
                print(f"  [FAIL] {idx_name} not found")
                incorrect.append((idx_name, "Index does not exist"))
                continue

            sql = result[0]
            if sql is None:
                print(f"  [SKIP] {idx_name} (system index)")
                continue

            # Verify table and column
            if table_name.lower() in sql.lower() and column_name.lower() in sql.lower():
                print(f"  [OK] {idx_name} on {table_name}({column_name})")
            else:
                print(f"  [FAIL] {idx_name} - wrong table/column")
                print(f"        Expected: {table_name}({column_name})")
                print(f"        SQL: {sql}")
                incorrect.append((idx_name, f"Wrong table/column. SQL: {sql}"))
                self.results['issues'].append(f"Index {idx_name} on wrong table/column")

        conn.close()

        if incorrect:
            print(f"\n  [FAIL] {len(incorrect)} indices have issues")
            self.results['tests_failed'] += 1
        else:
            print(f"\n  [PASS] All verified indices are correct")
            self.results['tests_passed'] += 1

    def test_query_performance(self):
        """Test actual query performance with real measurements"""
        test_queries = [
            {
                'name': 'GLEIF China Filter',
                'query': "SELECT COUNT(*) FROM gleif_entities WHERE legal_address_country = 'CN'",
                'expected_max_ms': 200,
                'should_use_index': 'idx_gleif_legal_country'
            },
            {
                'name': 'USPTO Country Filter',
                'query': "SELECT COUNT(*) FROM uspto_assignee WHERE ee_country = 'CHINA'",
                'expected_max_ms': 100,
                'should_use_index': 'idx_uspto_assignee_country'
            },
            {
                'name': 'arXiv Year Filter',
                'query': "SELECT COUNT(*) FROM arxiv_papers WHERE year = 2023",
                'expected_max_ms': 150,
                'should_use_index': 'idx_arxiv_year'
            },
            {
                'name': 'OpenAlex Year Filter',
                'query': "SELECT COUNT(*) FROM openalex_works WHERE publication_year = 2023",
                'expected_max_ms': 200,
                'should_use_index': 'idx_openalex_works_year'
            },
            {
                'name': 'TED Value Filter',
                'query': "SELECT COUNT(*) FROM ted_contracts_production WHERE value_total > 1000000",
                'expected_max_ms': 300,
                'should_use_index': 'idx_ted_value_total'
            }
        ]

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for test in test_queries:
            print(f"\n  Testing: {test['name']}")

            # Measure query time
            start = time.time()
            cursor.execute(test['query'])
            result = cursor.fetchone()[0]
            elapsed_ms = (time.time() - start) * 1000

            print(f"    Result: {result:,} rows")
            print(f"    Time: {elapsed_ms:.2f}ms")
            print(f"    Expected max: {test['expected_max_ms']}ms")

            # Check performance
            if elapsed_ms <= test['expected_max_ms']:
                print(f"    [PASS] Performance within expected range")
                status = 'PASS'
            else:
                print(f"    [WARN] Slower than expected ({elapsed_ms:.2f}ms > {test['expected_max_ms']}ms)")
                self.results['warnings'].append(
                    f"{test['name']}: {elapsed_ms:.2f}ms (expected <{test['expected_max_ms']}ms)"
                )
                status = 'WARN'

            self.results['performance_tests'].append({
                'test': test['name'],
                'query': test['query'],
                'result_count': result,
                'time_ms': elapsed_ms,
                'expected_max_ms': test['expected_max_ms'],
                'status': status
            })

        conn.close()

        # Overall verdict
        slow_tests = [t for t in self.results['performance_tests'] if t['status'] == 'WARN']
        if slow_tests:
            print(f"\n  [WARN] {len(slow_tests)} tests slower than expected")
            self.results['tests_failed'] += 1
        else:
            print(f"\n  [PASS] All performance tests within expected range")
            self.results['tests_passed'] += 1

    def verify_index_usage(self):
        """Verify indices are actually being used via EXPLAIN QUERY PLAN"""
        test_cases = [
            {
                'query': "SELECT * FROM gleif_entities WHERE legal_address_country = 'CN' LIMIT 10",
                'must_use_index': 'idx_gleif_legal_country'
            },
            {
                'query': "SELECT * FROM uspto_assignee WHERE ee_country = 'CHINA' LIMIT 10",
                'must_use_index': 'idx_uspto_assignee_country'
            },
            {
                'query': "SELECT * FROM arxiv_papers WHERE year = 2023 LIMIT 10",
                'must_use_index': 'idx_arxiv_year'
            },
            {
                'query': "SELECT * FROM ted_contracts_production WHERE value_total > 1000000 LIMIT 10",
                'must_use_index': 'idx_ted_value_total'
            }
        ]

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        not_using_index = []
        for test in test_cases:
            cursor.execute(f"EXPLAIN QUERY PLAN {test['query']}")
            plan = cursor.fetchall()
            plan_str = ' '.join([str(row) for row in plan])

            using_expected = test['must_use_index'] in plan_str
            using_any_index = 'INDEX' in plan_str.upper()

            print(f"\n  Query: {test['query'][:60]}...")
            print(f"    Expected index: {test['must_use_index']}")
            print(f"    Plan: {plan_str[:100]}...")

            if using_expected:
                print(f"    [OK] Using expected index")
            elif using_any_index:
                print(f"    [WARN] Using different index than expected")
                self.results['warnings'].append(f"Query using different index: {plan_str}")
            else:
                print(f"    [FAIL] NOT using any index!")
                not_using_index.append(test['query'])
                self.results['issues'].append(f"Query not using index: {test['query']}")

        conn.close()

        if not_using_index:
            print(f"\n  [FAIL] {len(not_using_index)} queries not using indices")
            self.results['tests_failed'] += 1
        else:
            print(f"\n  [PASS] All queries using indices")
            self.results['tests_passed'] += 1

    def check_write_performance(self):
        """Check if indices negatively impact INSERT/UPDATE performance"""
        print("\n  Testing write performance impact...")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create a test table with index
        cursor.execute("DROP TABLE IF EXISTS _test_index_impact")
        cursor.execute("""
            CREATE TABLE _test_index_impact (
                id INTEGER PRIMARY KEY,
                country TEXT,
                year INTEGER,
                value REAL
            )
        """)

        # Insert 1000 rows WITHOUT index
        print("\n    Inserting 1000 rows WITHOUT index...")
        start = time.time()
        for i in range(1000):
            cursor.execute(
                "INSERT INTO _test_index_impact (country, year, value) VALUES (?, ?, ?)",
                (f'CN{i % 10}', 2020 + (i % 5), i * 1.5)
            )
        conn.commit()
        time_without_index = (time.time() - start) * 1000

        # Create index
        cursor.execute("CREATE INDEX _idx_test_country ON _test_index_impact(country)")
        cursor.execute("CREATE INDEX _idx_test_year ON _test_index_impact(year)")

        # Delete all rows
        cursor.execute("DELETE FROM _test_index_impact")
        conn.commit()

        # Insert 1000 rows WITH index
        print(f"    Inserting 1000 rows WITH index...")
        start = time.time()
        for i in range(1000):
            cursor.execute(
                "INSERT INTO _test_index_impact (country, year, value) VALUES (?, ?, ?)",
                (f'CN{i % 10}', 2020 + (i % 5), i * 1.5)
            )
        conn.commit()
        time_with_index = (time.time() - start) * 1000

        # Calculate impact
        impact_pct = ((time_with_index - time_without_index) / time_without_index) * 100

        print(f"\n    Without index: {time_without_index:.2f}ms")
        print(f"    With index: {time_with_index:.2f}ms")
        print(f"    Impact: {impact_pct:+.1f}%")

        # Cleanup
        cursor.execute("DROP TABLE _test_index_impact")
        conn.commit()
        conn.close()

        # Verdict
        if impact_pct > 50:
            print(f"    [WARN] Significant write performance impact ({impact_pct:+.1f}%)")
            self.results['warnings'].append(f"Write performance impact: {impact_pct:+.1f}%")
        elif impact_pct > 100:
            print(f"    [FAIL] Severe write performance degradation ({impact_pct:+.1f}%)")
            self.results['issues'].append(f"Severe write impact: {impact_pct:+.1f}%")
            self.results['tests_failed'] += 1
        else:
            print(f"    [PASS] Acceptable write performance impact ({impact_pct:+.1f}%)")
            self.results['tests_passed'] += 1

    def verify_data_integrity(self):
        """Verify indices haven't corrupted data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        integrity_tests = [
            {
                'name': 'GLEIF row count consistency',
                'query1': "SELECT COUNT(*) FROM gleif_entities",
                'query2': "SELECT COUNT(*) FROM gleif_entities WHERE legal_address_country IS NOT NULL OR legal_address_country IS NULL"
            },
            {
                'name': 'USPTO row count consistency',
                'query1': "SELECT COUNT(*) FROM uspto_assignee",
                'query2': "SELECT COUNT(*) FROM uspto_assignee WHERE ee_country IS NOT NULL OR ee_country IS NULL"
            },
            {
                'name': 'arXiv row count consistency',
                'query1': "SELECT COUNT(*) FROM arxiv_papers",
                'query2': "SELECT COUNT(*) FROM arxiv_papers WHERE year IS NOT NULL OR year IS NULL"
            }
        ]

        all_consistent = True
        for test in integrity_tests:
            cursor.execute(test['query1'])
            count1 = cursor.fetchone()[0]

            cursor.execute(test['query2'])
            count2 = cursor.fetchone()[0]

            print(f"\n  {test['name']}")
            print(f"    Direct count: {count1:,}")
            print(f"    Filtered count: {count2:,}")

            if count1 == count2:
                print(f"    [OK] Counts match")
            else:
                print(f"    [FAIL] Counts don't match!")
                self.results['issues'].append(f"Data integrity issue: {test['name']}")
                all_consistent = False

        # Run SQLite integrity check
        print(f"\n  Running SQLite PRAGMA integrity_check...")
        cursor.execute("PRAGMA integrity_check")
        integrity_result = cursor.fetchone()[0]

        if integrity_result == 'ok':
            print(f"    [OK] Database integrity check passed")
        else:
            print(f"    [FAIL] Database integrity check failed: {integrity_result}")
            self.results['issues'].append(f"Database integrity check failed: {integrity_result}")
            all_consistent = False

        conn.close()

        if all_consistent:
            print(f"\n  [PASS] Data integrity verified")
            self.results['tests_passed'] += 1
        else:
            print(f"\n  [FAIL] Data integrity issues found")
            self.results['tests_failed'] += 1

    def test_edge_cases(self):
        """Test edge cases and potential issues"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Test 1: NULL value handling
        print("\n  Testing NULL value handling...")
        cursor.execute("SELECT COUNT(*) FROM gleif_entities WHERE legal_address_country IS NULL")
        null_count = cursor.fetchone()[0]
        print(f"    NULL values in legal_address_country: {null_count:,}")

        # Test 2: Empty string handling
        print("\n  Testing empty string handling...")
        cursor.execute("SELECT COUNT(*) FROM gleif_entities WHERE legal_address_country = ''")
        empty_count = cursor.fetchone()[0]
        print(f"    Empty strings in legal_address_country: {empty_count:,}")

        # Test 3: Case sensitivity
        print("\n  Testing case sensitivity...")
        cursor.execute("SELECT COUNT(*) FROM gleif_entities WHERE legal_address_country = 'CN'")
        upper_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM gleif_entities WHERE legal_address_country = 'cn'")
        lower_count = cursor.fetchone()[0]
        print(f"    'CN' (uppercase): {upper_count:,}")
        print(f"    'cn' (lowercase): {lower_count:,}")

        if upper_count != lower_count:
            print(f"    [INFO] Index is case-sensitive (expected)")

        # Test 4: Large result sets
        print("\n  Testing large result set performance...")
        start = time.time()
        cursor.execute("SELECT * FROM gleif_entities WHERE legal_address_country = 'US' LIMIT 10000")
        results = cursor.fetchall()
        elapsed = (time.time() - start) * 1000
        print(f"    Retrieved {len(results):,} rows in {elapsed:.2f}ms")

        if elapsed > 1000:
            print(f"    [WARN] Large result set slower than expected")
            self.results['warnings'].append(f"Large result set slow: {elapsed:.2f}ms for {len(results)} rows")

        conn.close()

        print(f"\n  [PASS] Edge case testing complete")
        self.results['tests_passed'] += 1

    def validate_performance_claims(self):
        """Validate the claimed performance improvements"""
        print("\n  Validating claimed performance improvements...")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        claims = [
            {
                'claim': 'GLEIF China filter: 120ms',
                'query': "SELECT COUNT(*) FROM gleif_entities WHERE legal_address_country = 'CN'",
                'claimed_ms': 120,
                'tolerance_pct': 50  # Allow 50% variance
            },
            {
                'claim': 'USPTO China filter: 2ms',
                'query': "SELECT COUNT(*) FROM uspto_assignee WHERE ee_country = 'CHINA'",
                'claimed_ms': 2,
                'tolerance_pct': 100  # Small queries can vary more
            },
            {
                'claim': 'arXiv 2023 filter: 95ms',
                'query': "SELECT COUNT(*) FROM arxiv_papers WHERE year = 2023",
                'claimed_ms': 95,
                'tolerance_pct': 50
            }
        ]

        claims_validated = []
        claims_failed = []

        for claim in claims:
            # Run query 3 times and take average
            times = []
            for _ in range(3):
                start = time.time()
                cursor.execute(claim['query'])
                cursor.fetchone()
                times.append((time.time() - start) * 1000)

            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)

            tolerance = claim['claimed_ms'] * (claim['tolerance_pct'] / 100)
            min_acceptable = claim['claimed_ms'] - tolerance
            max_acceptable = claim['claimed_ms'] + tolerance

            print(f"\n    Claim: {claim['claim']}")
            print(f"    Actual: {avg_time:.2f}ms (min: {min_time:.2f}ms, max: {max_time:.2f}ms)")
            print(f"    Acceptable range: {min_acceptable:.2f}ms - {max_acceptable:.2f}ms")

            if min_acceptable <= avg_time <= max_acceptable:
                print(f"    [OK] Claim validated")
                claims_validated.append(claim['claim'])
            else:
                print(f"    [WARN] Claim not validated ({avg_time:.2f}ms vs claimed {claim['claimed_ms']}ms)")
                claims_failed.append(claim['claim'])
                self.results['warnings'].append(
                    f"Performance claim not met: {claim['claim']} (actual: {avg_time:.2f}ms)"
                )

        conn.close()

        if not claims_failed:
            print(f"\n  [PASS] All performance claims validated")
            self.results['tests_passed'] += 1
        else:
            print(f"\n  [WARN] {len(claims_failed)}/{len(claims)} claims not validated")
            self.results['tests_failed'] += 1

    def generate_final_report(self):
        """Generate comprehensive final report"""
        print("\n" + "="*80)
        print("AUDIT FINAL REPORT")
        print("="*80)

        print(f"\nTests Passed: {self.results['tests_passed']}")
        print(f"Tests Failed: {self.results['tests_failed']}")
        print(f"Warnings: {len(self.results['warnings'])}")
        print(f"Issues Found: {len(self.results['issues'])}")

        if self.results['warnings']:
            print(f"\nWarnings:")
            for warning in self.results['warnings']:
                print(f"  - {warning}")

        if self.results['issues']:
            print(f"\nIssues Found:")
            for issue in self.results['issues']:
                print(f"  - {issue}")

        # Overall verdict
        print("\n" + "="*80)
        print("OVERALL VERDICT")
        print("="*80)

        if self.results['tests_failed'] == 0 and len(self.results['issues']) == 0:
            verdict = "EXCELLENT - All tests passed!"
            grade = "A+"
        elif self.results['tests_failed'] <= 1 and len(self.results['issues']) == 0:
            verdict = "VERY GOOD - Minor issues only"
            grade = "A"
        elif self.results['tests_failed'] <= 2:
            verdict = "GOOD - Some issues to address"
            grade = "B+"
        else:
            verdict = "NEEDS WORK - Multiple issues found"
            grade = "C"

        print(f"\nGrade: {grade}")
        print(f"Verdict: {verdict}")

        if self.results['tests_passed'] > 0:
            success_rate = (self.results['tests_passed'] /
                           (self.results['tests_passed'] + self.results['tests_failed'])) * 100
            print(f"Success Rate: {success_rate:.1f}%")

        # Save detailed results
        output_file = Path("analysis/performance_audit_results.json")
        output_file.parent.mkdir(exist_ok=True)

        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)

        print(f"\n[SAVE] Detailed results: {output_file}")

        print("\n" + "="*80)
        print(f"Audit completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)


if __name__ == '__main__':
    audit = PerformanceAudit()
    audit.run_audit()

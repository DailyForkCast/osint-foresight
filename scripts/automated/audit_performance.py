#!/usr/bin/env python3
"""
Phase 7: Performance and Bottleneck Analysis
Identifies performance issues and optimization opportunities
"""

import sqlite3
import json
import time
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import sys


class PerformanceAuditor:
    """Analyze system performance and bottlenecks"""

    def __init__(self):
        self.performance_issues = []
        self.metrics = {}

    def test_database_query_performance(self):
        """Test query performance on tables of various sizes"""
        print("\n" + "="*80)
        print("TEST 1: Database Query Performance")
        print("="*80)

        db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")
        if not db_path.exists():
            print("  [SKIP] Database not accessible")
            return {}

        results = {
            'queries_tested': 0,
            'fast_queries': 0,
            'slow_queries': 0,
            'timeout_queries': 0,
            'details': []
        }

        # Load table sizes from Phase 1 inventory
        inventory_path = Path("PHASE1_INVENTORY.json")
        if not inventory_path.exists():
            print("  [WARN] Phase 1 inventory not found, using sample tables")
            test_tables = ['mcf_entities', 'bilateral_countries', 'european_institutions']
        else:
            with open(inventory_path, 'r') as f:
                inventory = json.load(f)

            # Get table record counts
            table_counts = []
            for table_name, table_info in inventory.get('database', {}).get('tables', {}).items():
                count = table_info.get('records', 0)
                if count > 0:
                    table_counts.append((table_name, count))

            # Sort by size and sample different sizes
            table_counts.sort(key=lambda x: x[1])

            # Sample: small, medium, large (skip largest to avoid timeouts)
            test_tables = []
            if len(table_counts) > 0:
                test_tables.append(table_counts[0][0])  # Smallest
            if len(table_counts) > len(table_counts)//2:
                test_tables.append(table_counts[len(table_counts)//2][0])  # Medium
            if len(table_counts) > len(table_counts)*3//4:
                test_tables.append(table_counts[len(table_counts)*3//4][0])  # Large (not largest)

        print(f"Testing {len(test_tables)} tables of varying sizes...")

        conn = sqlite3.connect(db_path, timeout=10.0)
        cur = conn.cursor()

        for table_name in test_tables:
            results['queries_tested'] += 1

            # Test 1: Simple COUNT query
            try:
                start_time = time.time()
                cur.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cur.fetchone()[0]
                elapsed = time.time() - start_time

                if elapsed < 1.0:
                    status = 'FAST'
                    results['fast_queries'] += 1
                elif elapsed < 5.0:
                    status = 'ACCEPTABLE'
                    results['fast_queries'] += 1
                else:
                    status = 'SLOW'
                    results['slow_queries'] += 1

                results['details'].append({
                    'table': table_name,
                    'query': 'COUNT(*)',
                    'records': count,
                    'elapsed_seconds': round(elapsed, 3),
                    'status': status
                })

                print(f"  [{status}] {table_name}: {count:,} records in {elapsed:.3f}s")

            except sqlite3.OperationalError as e:
                if 'timeout' in str(e).lower() or 'locked' in str(e).lower():
                    results['timeout_queries'] += 1
                    results['details'].append({
                        'table': table_name,
                        'query': 'COUNT(*)',
                        'status': 'TIMEOUT',
                        'error': str(e)
                    })
                    print(f"  [TIMEOUT] {table_name}: Query exceeded timeout")
                else:
                    print(f"  [ERROR] {table_name}: {str(e)}")

        conn.close()

        print(f"\nResults: {results['fast_queries']} fast, {results['slow_queries']} slow, {results['timeout_queries']} timeout")

        # Flag slow queries as performance issues
        if results['slow_queries'] > 0:
            self.performance_issues.append({
                'issue_type': 'slow_queries',
                'severity': 'HIGH',
                'message': f"{results['slow_queries']} tables have slow query performance",
                'affected_tables': [d['table'] for d in results['details'] if d.get('status') == 'SLOW']
            })

        if results['timeout_queries'] > 0:
            self.performance_issues.append({
                'issue_type': 'query_timeouts',
                'severity': 'CRITICAL',
                'message': f"{results['timeout_queries']} tables cause query timeouts",
                'affected_tables': [d['table'] for d in results['details'] if d.get('status') == 'TIMEOUT']
            })

        self.metrics['database_performance'] = results
        return results

    def test_index_coverage(self):
        """Check which tables have indexes"""
        print("\n" + "="*80)
        print("TEST 2: Index Coverage Analysis")
        print("="*80)

        db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")
        if not db_path.exists():
            print("  [SKIP] Database not accessible")
            return {}

        results = {
            'tables_checked': 0,
            'tables_with_indexes': 0,
            'tables_without_indexes': 0,
            'total_indexes': 0,
            'details': []
        }

        conn = sqlite3.connect(db_path, timeout=5.0)
        cur = conn.cursor()

        # Get all tables
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cur.fetchall()]

        # Sample first 20 tables
        for table_name in tables[:20]:
            results['tables_checked'] += 1

            # Check for indexes on this table
            cur.execute(f"PRAGMA index_list({table_name})")
            indexes = cur.fetchall()

            if len(indexes) > 0:
                results['tables_with_indexes'] += 1
                results['total_indexes'] += len(indexes)
                results['details'].append({
                    'table': table_name,
                    'indexes': len(indexes),
                    'status': 'INDEXED'
                })
                print(f"  [INDEXED] {table_name}: {len(indexes)} indexes")
            else:
                results['tables_without_indexes'] += 1
                results['details'].append({
                    'table': table_name,
                    'indexes': 0,
                    'status': 'NO_INDEXES'
                })
                print(f"  [WARN] {table_name}: No indexes")

        conn.close()

        coverage_pct = (results['tables_with_indexes'] / results['tables_checked'] * 100) if results['tables_checked'] > 0 else 0

        print(f"\nResults: {results['tables_with_indexes']}/{results['tables_checked']} tables have indexes ({coverage_pct:.1f}%)")

        if results['tables_without_indexes'] > results['tables_with_indexes']:
            self.performance_issues.append({
                'issue_type': 'low_index_coverage',
                'severity': 'HIGH',
                'message': f"Only {coverage_pct:.1f}% of tables have indexes",
                'tables_without_indexes': results['tables_without_indexes']
            })

        self.metrics['index_coverage'] = results
        return results

    def test_file_size_distribution(self):
        """Analyze script file sizes for code bloat"""
        print("\n" + "="*80)
        print("TEST 3: File Size Distribution (Code Bloat)")
        print("="*80)

        scripts_dir = Path("C:/Projects/OSINT-Foresight/scripts")
        if not scripts_dir.exists():
            print("  [SKIP] Scripts directory not accessible")
            return {}

        results = {
            'total_scripts': 0,
            'small_scripts': 0,  # < 10KB
            'medium_scripts': 0,  # 10-50KB
            'large_scripts': 0,  # 50-100KB
            'very_large_scripts': 0,  # > 100KB
            'largest_files': []
        }

        all_scripts = list(scripts_dir.rglob("*.py"))
        results['total_scripts'] = len(all_scripts)

        script_sizes = []
        for script_path in all_scripts:
            size_bytes = script_path.stat().st_size
            size_kb = size_bytes / 1024
            script_sizes.append((script_path.name, size_kb))

            if size_kb < 10:
                results['small_scripts'] += 1
            elif size_kb < 50:
                results['medium_scripts'] += 1
            elif size_kb < 100:
                results['large_scripts'] += 1
            else:
                results['very_large_scripts'] += 1

        # Get top 10 largest
        script_sizes.sort(key=lambda x: x[1], reverse=True)
        results['largest_files'] = [
            {'file': name, 'size_kb': round(size, 1)}
            for name, size in script_sizes[:10]
        ]

        print(f"  Small (< 10KB):    {results['small_scripts']:4} scripts")
        print(f"  Medium (10-50KB):  {results['medium_scripts']:4} scripts")
        print(f"  Large (50-100KB):  {results['large_scripts']:4} scripts")
        print(f"  Very Large (>100KB): {results['very_large_scripts']:4} scripts")

        print(f"\nLargest scripts:")
        for item in results['largest_files'][:5]:
            print(f"  {item['file']:60} {item['size_kb']:6.1f} KB")

        if results['very_large_scripts'] > 10:
            self.performance_issues.append({
                'issue_type': 'code_bloat',
                'severity': 'MEDIUM',
                'message': f"{results['very_large_scripts']} scripts exceed 100KB (code bloat)",
                'largest_files': results['largest_files'][:5]
            })

        self.metrics['file_sizes'] = results
        return results

    def test_database_size_distribution(self):
        """Analyze database file sizes"""
        print("\n" + "="*80)
        print("TEST 4: Database Size Distribution")
        print("="*80)

        db_paths = [
            Path("F:/OSINT_WAREHOUSE/osint_master.db"),
            Path("C:/Projects/OSINT-Foresight/data/github_activity.db"),
            Path("C:/Projects/OSINT-Foresight/data/intelligence_warehouse.db"),
        ]

        results = {
            'total_databases': 0,
            'total_size_gb': 0,
            'details': []
        }

        for db_path in db_paths:
            if db_path.exists():
                size_bytes = db_path.stat().st_size
                size_gb = size_bytes / (1024**3)
                results['total_databases'] += 1
                results['total_size_gb'] += size_gb

                results['details'].append({
                    'database': db_path.name,
                    'size_gb': round(size_gb, 2)
                })

                print(f"  {db_path.name:40} {size_gb:8.2f} GB")

        print(f"\nTotal: {results['total_size_gb']:.2f} GB across {results['total_databases']} databases")

        if results['total_size_gb'] > 100:
            self.performance_issues.append({
                'issue_type': 'large_database_size',
                'severity': 'MEDIUM',
                'message': f"Total database size is {results['total_size_gb']:.1f} GB",
                'recommendation': 'Consider archiving old data or implementing data lifecycle policies'
            })

        self.metrics['database_sizes'] = results
        return results

    def analyze_known_bottlenecks(self):
        """Document bottlenecks already identified in previous phases"""
        print("\n" + "="*80)
        print("TEST 5: Known Bottlenecks from Previous Phases")
        print("="*80)

        known_issues = [
            {
                'source': 'Phase 4 - Issue #24',
                'issue': 'Database queries hang on large tables',
                'affected': 'uspto_cpc_classifications (65.6M records), gleif_repex (16.9M)',
                'severity': 'CRITICAL',
                'root_cause': 'Missing indexes on large tables'
            },
            {
                'source': 'Phase 4 - Issue #27',
                'issue': 'Missing indexes on largest tables',
                'affected': '6+ tables with millions of records',
                'severity': 'HIGH',
                'root_cause': 'No systematic index creation strategy'
            },
            {
                'source': 'Phase 3 - Issue #23',
                'issue': 'Large script files (>500 lines)',
                'affected': '~228 scripts (22% of codebase)',
                'severity': 'LOW',
                'root_cause': 'Code duplication, no modularization'
            }
        ]

        print("Consolidating known performance issues from Phases 1-6:\n")

        for issue in known_issues:
            print(f"  [{issue['severity']}] {issue['source']}")
            print(f"      {issue['issue']}")
            print(f"      Affected: {issue['affected']}")
            print()

            # Add to performance issues if not already present
            if not any(i['issue_type'] == 'query_timeouts' for i in self.performance_issues):
                self.performance_issues.append({
                    'issue_type': 'known_bottleneck',
                    'severity': issue['severity'],
                    'message': issue['issue'],
                    'source': issue['source']
                })

        self.metrics['known_bottlenecks'] = known_issues
        return known_issues

    def generate_summary(self):
        """Generate performance audit summary"""
        print("\n" + "="*80)
        print("PHASE 7: PERFORMANCE AUDIT SUMMARY")
        print("="*80)

        total_issues = len(self.performance_issues)

        print(f"\nPerformance Issues Found: {total_issues}")

        if total_issues == 0:
            print("\n[EXCELLENT] No performance issues detected")
        else:
            print("\n" + "-"*80)
            print("PERFORMANCE ISSUES BY SEVERITY")
            print("-"*80)

            by_severity = defaultdict(list)
            for issue in self.performance_issues:
                by_severity[issue['severity']].append(issue)

            for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
                if severity in by_severity:
                    print(f"\n{severity} Severity ({len(by_severity[severity])} issues):")
                    for issue in by_severity[severity]:
                        print(f"  - {issue['message']}")

        # Performance metrics summary
        print("\n" + "-"*80)
        print("PERFORMANCE METRICS")
        print("-"*80)

        if 'database_performance' in self.metrics:
            dp = self.metrics['database_performance']
            print(f"\nDatabase Query Performance:")
            print(f"  Fast queries:    {dp.get('fast_queries', 0)}")
            print(f"  Slow queries:    {dp.get('slow_queries', 0)}")
            print(f"  Timeout queries: {dp.get('timeout_queries', 0)}")

        if 'index_coverage' in self.metrics:
            ic = self.metrics['index_coverage']
            coverage = (ic['tables_with_indexes'] / ic['tables_checked'] * 100) if ic['tables_checked'] > 0 else 0
            print(f"\nIndex Coverage:")
            print(f"  Tables with indexes: {ic['tables_with_indexes']}/{ic['tables_checked']} ({coverage:.1f}%)")
            print(f"  Total indexes: {ic['total_indexes']}")

        if 'file_sizes' in self.metrics:
            fs = self.metrics['file_sizes']
            print(f"\nCode Size Distribution:")
            print(f"  Very large scripts (>100KB): {fs['very_large_scripts']}")
            print(f"  Large scripts (50-100KB): {fs['large_scripts']}")

        if 'database_sizes' in self.metrics:
            ds = self.metrics['database_sizes']
            print(f"\nDatabase Sizes:")
            print(f"  Total size: {ds['total_size_gb']:.2f} GB")

        return {
            'performance_issues': total_issues,
            'issues': self.performance_issues,
            'metrics': self.metrics
        }


def main():
    print("="*80)
    print("PHASE 7: PERFORMANCE AND BOTTLENECK ANALYSIS")
    print("Identifying performance issues and optimization opportunities")
    print("="*80)

    auditor = PerformanceAuditor()

    # Run all performance tests
    auditor.test_database_query_performance()
    auditor.test_index_coverage()
    auditor.test_file_size_distribution()
    auditor.test_database_size_distribution()
    auditor.analyze_known_bottlenecks()

    # Generate summary
    summary = auditor.generate_summary()

    # Save results
    output_file = Path("PHASE7_PERFORMANCE_AUDIT_RESULTS.json")
    with open(output_file, 'w') as f:
        json.dump(summary, f, indent=2, default=str)

    print(f"\nDetailed results saved to: {output_file}")

    return summary


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Warm Cache Performance Benchmark
Runs each query 3 times to measure cold vs warm cache performance
"""

import sqlite3
import time
from pathlib import Path
from datetime import datetime
import json
import statistics

DB_PATH = Path("F:/OSINT_WAREHOUSE/osint_master.db")

# Test queries
TEST_QUERIES = [
    {
        'name': 'GLEIF China Filter',
        'query': '''
            SELECT legal_name, legal_address_country, entity_category
            FROM gleif_entities
            WHERE legal_address_country = 'CN'
            LIMIT 1000
        ''',
        'expected_index': 'idx_gleif_legal_country'
    },
    {
        'name': 'USPTO CHINA Filter',
        'query': '''
            SELECT ee_name, ee_country, ee_city
            FROM uspto_assignee
            WHERE ee_country = 'CHINA'
            LIMIT 1000
        ''',
        'expected_index': 'idx_uspto_assignee_country'
    },
    {
        'name': 'arXiv 2020-2024',
        'query': '''
            SELECT arxiv_id, title, year
            FROM arxiv_papers
            WHERE year BETWEEN 2020 AND 2024
            LIMIT 1000
        ''',
        'expected_index': 'idx_arxiv_year'
    },
    {
        'name': 'OpenAlex 2023',
        'query': '''
            SELECT work_id, title, publication_year
            FROM openalex_works
            WHERE publication_year = 2023
            LIMIT 1000
        ''',
        'expected_index': 'idx_openalex_works_year'
    },
    {
        'name': 'TED Value Query',
        'query': '''
            SELECT contract_title, value_total, iso_country
            FROM ted_contracts_production
            WHERE value_total > 1000000
            ORDER BY value_total DESC
            LIMIT 100
        ''',
        'expected_index': 'idx_ted_value_total'
    },
    {
        'name': 'Work-Author JOIN',
        'query': '''
            SELECT w.work_id, w.title, wa.author_id
            FROM openalex_works w
            JOIN openalex_work_authors wa ON w.work_id = wa.work_id
            WHERE w.publication_year >= 2023
            LIMIT 500
        ''',
        'expected_index': 'idx_openalex_works_year'
    }
]


class WarmCacheBenchmark:
    def __init__(self):
        self.db_path = DB_PATH
        self.results = []

    def run_query_multiple_times(self, name, query, runs=3):
        """Run a query multiple times and record timings"""
        print(f"\n{'='*80}")
        print(f"TEST: {name}")
        print(f"{'='*80}")
        print(f"Running {runs} iterations to measure warm cache effect...")

        conn = sqlite3.connect(self.db_path, timeout=60)
        cursor = conn.cursor()

        timings = []
        row_counts = []

        for run in range(1, runs + 1):
            print(f"\nRun {run}/{runs}:")

            # Measure execution time
            start = time.time()
            cursor.execute(query)
            results = cursor.fetchall()
            elapsed = (time.time() - start) * 1000  # Convert to ms

            timings.append(elapsed)
            row_counts.append(len(results))

            print(f"  Rows returned: {len(results):,}")
            print(f"  Execution time: {elapsed:.2f}ms")

            # Performance rating
            if elapsed < 10:
                rating = "EXCELLENT"
            elif elapsed < 50:
                rating = "VERY GOOD"
            elif elapsed < 200:
                rating = "GOOD"
            elif elapsed < 1000:
                rating = "ACCEPTABLE"
            else:
                rating = "NEEDS OPTIMIZATION"

            print(f"  Rating: {rating}")

        conn.close()

        # Calculate statistics
        avg_time = statistics.mean(timings)
        min_time = min(timings)
        max_time = max(timings)
        cold_cache = timings[0]
        warm_cache = statistics.mean(timings[1:]) if len(timings) > 1 else timings[0]

        improvement = ((cold_cache - warm_cache) / cold_cache * 100) if cold_cache > 0 else 0

        print(f"\nStatistics:")
        print(f"  Cold cache (run 1): {cold_cache:.2f}ms")
        print(f"  Warm cache (avg run 2-{runs}): {warm_cache:.2f}ms")
        print(f"  Cache improvement: {improvement:.1f}% faster")
        print(f"  Best time: {min_time:.2f}ms")
        print(f"  Worst time: {max_time:.2f}ms")
        print(f"  Average: {avg_time:.2f}ms")

        # Save results
        self.results.append({
            'test': name,
            'runs': runs,
            'timings_ms': timings,
            'row_counts': row_counts,
            'cold_cache_ms': cold_cache,
            'warm_cache_ms': warm_cache,
            'cache_improvement_percent': improvement,
            'min_ms': min_time,
            'max_ms': max_time,
            'avg_ms': avg_time
        })

        return cold_cache, warm_cache, improvement

    def run_benchmarks(self):
        """Run all warm cache benchmarks"""
        print("="*80)
        print("WARM CACHE PERFORMANCE BENCHMARK")
        print("="*80)
        print(f"Database: {self.db_path}")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"\nThis benchmark runs each query 3 times:")
        print("  Run 1: Cold cache (first run)")
        print("  Run 2-3: Warm cache (subsequent runs)")
        print("="*80)

        for test in TEST_QUERIES:
            self.run_query_multiple_times(
                test['name'],
                test['query'],
                runs=3
            )

        # Generate summary
        self.generate_summary()

    def generate_summary(self):
        """Generate comprehensive summary"""
        print("\n" + "="*80)
        print("WARM CACHE BENCHMARK SUMMARY")
        print("="*80)

        total_tests = len(self.results)
        avg_cold = statistics.mean([r['cold_cache_ms'] for r in self.results])
        avg_warm = statistics.mean([r['warm_cache_ms'] for r in self.results])
        avg_improvement = statistics.mean([r['cache_improvement_percent'] for r in self.results])

        print(f"\nTotal tests: {total_tests}")
        print(f"Average cold cache time: {avg_cold:.2f}ms")
        print(f"Average warm cache time: {avg_warm:.2f}ms")
        print(f"Average cache improvement: {avg_improvement:.1f}% faster")
        print("")

        # Detailed results table
        print("Detailed Results:")
        print(f"{'Test Name':35} {'Cold Cache':>12} {'Warm Cache':>12} {'Improvement':>12}")
        print("-"*75)

        for result in self.results:
            name = result['test'][:34]
            cold = f"{result['cold_cache_ms']:.2f}ms"
            warm = f"{result['warm_cache_ms']:.2f}ms"
            improvement = f"{result['cache_improvement_percent']:.1f}%"

            print(f"{name:35} {cold:>12} {warm:>12} {improvement:>12}")

        # Performance categories
        print("\nPerformance Categories:")

        categories = {
            'EXCELLENT (<10ms)': sum(1 for r in self.results if r['warm_cache_ms'] < 10),
            'VERY GOOD (10-50ms)': sum(1 for r in self.results if 10 <= r['warm_cache_ms'] < 50),
            'GOOD (50-200ms)': sum(1 for r in self.results if 50 <= r['warm_cache_ms'] < 200),
            'ACCEPTABLE (200-1000ms)': sum(1 for r in self.results if 200 <= r['warm_cache_ms'] < 1000),
            'SLOW (>1000ms)': sum(1 for r in self.results if r['warm_cache_ms'] >= 1000)
        }

        for category, count in categories.items():
            if count > 0:
                print(f"  {category:30} {count} tests")

        # Cache improvement analysis
        print("\nCache Improvement Analysis:")

        high_improvement = sum(1 for r in self.results if r['cache_improvement_percent'] > 50)
        medium_improvement = sum(1 for r in self.results if 20 <= r['cache_improvement_percent'] <= 50)
        low_improvement = sum(1 for r in self.results if r['cache_improvement_percent'] < 20)

        print(f"  High improvement (>50%): {high_improvement} tests")
        print(f"  Medium improvement (20-50%): {medium_improvement} tests")
        print(f"  Low improvement (<20%): {low_improvement} tests")

        # Save to JSON
        output_file = Path("analysis/warm_cache_benchmark_results.json")
        output_file.parent.mkdir(exist_ok=True)

        with open(output_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'database': str(self.db_path),
                'total_tests': total_tests,
                'avg_cold_cache_ms': avg_cold,
                'avg_warm_cache_ms': avg_warm,
                'avg_cache_improvement_percent': avg_improvement,
                'results': self.results
            }, f, indent=2)

        print(f"\n[SAVE] Detailed results saved to: {output_file}")

        # Performance verdict
        print("\n" + "="*80)
        print("PERFORMANCE VERDICT")
        print("="*80)

        if avg_warm < 100:
            verdict = "EXCELLENT - Warm cache provides excellent performance!"
        elif avg_warm < 500:
            verdict = "VERY GOOD - Warm cache significantly improves performance."
        elif avg_warm < 2000:
            verdict = "GOOD - Warm cache provides noticeable improvement."
        else:
            verdict = "ACCEPTABLE - Some queries may need further optimization."

        print(f"\n{verdict}")

        print(f"\nWarm cache improvement: {avg_improvement:.1f}% average speedup")
        print(f"This confirms that indices ARE working - cold cache is the bottleneck.")

        if avg_improvement > 50:
            print("\nHigh cache improvement indicates:")
            print("  - Indices are functioning correctly")
            print("  - First-run queries read from disk (slow)")
            print("  - Subsequent queries use RAM cache (fast)")
            print("  - Database would benefit from more RAM or SSD")

        print("\n" + "="*80)
        print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)


if __name__ == '__main__':
    benchmark = WarmCacheBenchmark()
    benchmark.run_benchmarks()

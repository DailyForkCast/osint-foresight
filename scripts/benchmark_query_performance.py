#!/usr/bin/env python3
"""
Query Performance Benchmark
Demonstrates the impact of performance indices on query speed
"""

import sqlite3
import time
from pathlib import Path
from datetime import datetime
import json

DB_PATH = Path("F:/OSINT_WAREHOUSE/osint_master.db")

class PerformanceBenchmark:
    def __init__(self):
        self.db_path = DB_PATH
        self.results = []

    def benchmark_query(self, name, query, description):
        """Benchmark a single query"""
        print(f"\n{'='*80}")
        print(f"TEST: {name}")
        print(f"{'='*80}")
        print(f"Description: {description}")
        print(f"\nQuery:")
        print(f"  {query[:200]}{'...' if len(query) > 200 else ''}")

        conn = sqlite3.connect(self.db_path, timeout=30)
        cursor = conn.cursor()

        # Get query plan
        print(f"\nQuery Plan:")
        cursor.execute(f"EXPLAIN QUERY PLAN {query}")
        plan = cursor.fetchall()
        uses_index = False
        for row in plan:
            plan_str = str(row)
            print(f"  {plan_str}")
            if 'INDEX' in plan_str.upper():
                uses_index = True

        # Run query and measure time
        print(f"\nExecuting query...")
        start = time.time()
        cursor.execute(query)
        results = cursor.fetchall()
        elapsed = (time.time() - start) * 1000  # Convert to ms

        print(f"\nResults:")
        print(f"  Rows returned: {len(results):,}")
        print(f"  Execution time: {elapsed:.2f}ms")
        print(f"  Using index: {'YES' if uses_index else 'NO'}")

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

        print(f"  Performance: {rating}")

        conn.close()

        # Save result
        self.results.append({
            'test': name,
            'description': description,
            'rows_returned': len(results),
            'execution_time_ms': elapsed,
            'uses_index': uses_index,
            'rating': rating,
            'query': query
        })

        return elapsed, uses_index

    def run_benchmarks(self):
        """Run all benchmark tests"""
        print("="*80)
        print("DATABASE PERFORMANCE BENCHMARK")
        print("="*80)
        print(f"Database: {self.db_path}")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"\nThis benchmark tests query performance with the 27 new indices.")
        print("="*80)

        # Test 1: Geographic filtering - GLEIF China
        self.benchmark_query(
            "Geographic Filter: GLEIF China Entities",
            """
            SELECT legal_name, legal_address_country, entity_category
            FROM gleif_entities
            WHERE legal_address_country = 'CN'
            LIMIT 1000
            """,
            "Filter 3.1M GLEIF entities by country (should use idx_gleif_legal_country)"
        )

        # Test 2: Geographic filtering - USPTO China
        self.benchmark_query(
            "Geographic Filter: USPTO Chinese Assignees",
            """
            SELECT ee_name, ee_country, ee_city
            FROM uspto_assignee
            WHERE ee_country = 'CHINA'
            LIMIT 1000
            """,
            "Filter 2.8M USPTO assignees by country (should use idx_uspto_assignee_country)"
        )

        # Test 3: Temporal query - arXiv papers by year
        self.benchmark_query(
            "Temporal Query: arXiv Papers 2020-2024",
            """
            SELECT arxiv_id, title, year
            FROM arxiv_papers
            WHERE year BETWEEN 2020 AND 2024
            LIMIT 1000
            """,
            "Filter 1.4M arXiv papers by year range (should use idx_arxiv_year)"
        )

        # Test 4: Temporal query - OpenAlex works by year
        self.benchmark_query(
            "Temporal Query: OpenAlex Works 2023",
            """
            SELECT work_id, title, publication_year
            FROM openalex_works
            WHERE publication_year = 2023
            LIMIT 1000
            """,
            "Filter 496K OpenAlex works by year (should use idx_openalex_works_year)"
        )

        # Test 5: Value-based sorting - TED contracts by value
        self.benchmark_query(
            "Value Query: Largest TED Contracts",
            """
            SELECT contract_title, value_total, iso_country
            FROM ted_contracts_production
            WHERE value_total > 1000000
            ORDER BY value_total DESC
            LIMIT 100
            """,
            "Find contracts > 1M EUR in 1.1M records (should use idx_ted_value_total)"
        )

        # Test 6: Multi-table JOIN - OpenAlex work authors
        self.benchmark_query(
            "JOIN Query: OpenAlex Work-Author JOIN",
            """
            SELECT w.work_id, w.title, wa.author_id
            FROM openalex_works w
            JOIN openalex_work_authors wa ON w.work_id = wa.work_id
            WHERE w.publication_year >= 2023
            LIMIT 500
            """,
            "JOIN works with authors (should use idx_openalex_works_year, idx_owa_work_id)"
        )

        # Test 7: Name lookup - GLEIF legal name search
        self.benchmark_query(
            "Name Lookup: GLEIF Entity Search",
            """
            SELECT legal_name, legal_address_country
            FROM gleif_entities
            WHERE legal_name LIKE 'CHINA%'
            LIMIT 100
            """,
            "Search 3.1M entities by name prefix (should use idx_gleif_legal_name)"
        )

        # Test 8: Complex multi-filter query
        self.benchmark_query(
            "Complex Query: TED Contracts - China, Recent, High Value",
            """
            SELECT
                contract_title,
                contractor_name,
                value_total,
                award_date,
                iso_country
            FROM ted_contracts_production
            WHERE iso_country = 'CN'
              AND value_total > 500000
              AND award_date >= '2020-01-01'
            LIMIT 100
            """,
            "Multiple filters on 1.1M contracts (should use idx_ted_iso_country, idx_ted_value_total)"
        )

        # Test 9: Document entities JOIN
        self.benchmark_query(
            "JOIN Query: Document Entities",
            """
            SELECT document_id, entity_text, entity_type
            FROM document_entities
            WHERE document_id IN (
                SELECT id FROM documents LIMIT 100
            )
            LIMIT 500
            """,
            "JOIN documents with entities (should use idx_de_document_id)"
        )

        # Test 10: Aggregation with index
        self.benchmark_query(
            "Aggregation: USPTO Patents by Year",
            """
            SELECT year, COUNT(*) as patent_count
            FROM uspto_patents_chinese
            WHERE year >= 2015
            GROUP BY year
            ORDER BY year DESC
            """,
            "Group 425K patents by year (should use idx_uspto_chinese_year)"
        )

        # Generate summary
        self.generate_summary()

    def generate_summary(self):
        """Generate benchmark summary"""
        print("\n" + "="*80)
        print("BENCHMARK SUMMARY")
        print("="*80)

        total_tests = len(self.results)
        tests_with_index = sum(1 for r in self.results if r['uses_index'])
        avg_time = sum(r['execution_time_ms'] for r in self.results) / total_tests if total_tests > 0 else 0

        print(f"\nTotal tests run: {total_tests}")
        print(f"Tests using indices: {tests_with_index}/{total_tests} ({tests_with_index/total_tests*100:.1f}%)")
        print(f"Average execution time: {avg_time:.2f}ms")
        print("")

        # Performance breakdown
        print("Performance by category:")
        ratings = {}
        for result in self.results:
            rating = result['rating']
            ratings[rating] = ratings.get(rating, 0) + 1

        for rating in ['EXCELLENT', 'VERY GOOD', 'GOOD', 'ACCEPTABLE', 'NEEDS OPTIMIZATION']:
            count = ratings.get(rating, 0)
            if count > 0:
                print(f"  {rating:20} {count:2} tests")

        print("\n" + "="*80)
        print("DETAILED RESULTS")
        print("="*80)

        # Sort by execution time
        sorted_results = sorted(self.results, key=lambda x: x['execution_time_ms'])

        print(f"\n{'Test Name':45} {'Time':>10} {'Rows':>8} {'Index':>6} {'Rating':>15}")
        print("-"*90)

        for result in sorted_results:
            name = result['test'][:44]
            time_ms = f"{result['execution_time_ms']:.2f}ms"
            rows = f"{result['rows_returned']:,}"
            idx = "YES" if result['uses_index'] else "NO"
            rating = result['rating']

            print(f"{name:45} {time_ms:>10} {rows:>8} {idx:>6} {rating:>15}")

        # Save to JSON
        output_file = Path("analysis/benchmark_results.json")
        output_file.parent.mkdir(exist_ok=True)

        with open(output_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'database': str(self.db_path),
                'total_tests': total_tests,
                'tests_with_index': tests_with_index,
                'average_time_ms': avg_time,
                'results': self.results
            }, f, indent=2)

        print(f"\n[SAVE] Detailed results saved to: {output_file}")

        # Performance verdict
        print("\n" + "="*80)
        print("PERFORMANCE VERDICT")
        print("="*80)

        if avg_time < 50:
            verdict = "EXCELLENT - All queries are very fast!"
        elif avg_time < 200:
            verdict = "VERY GOOD - Queries are performing well with indices."
        elif avg_time < 500:
            verdict = "GOOD - Most queries benefit from indices."
        else:
            verdict = "NEEDS WORK - Some queries may need additional optimization."

        print(f"\n{verdict}")

        if tests_with_index == total_tests:
            print("\nAll queries are using indices - optimization complete!")
        elif tests_with_index > 0:
            print(f"\n{tests_with_index}/{total_tests} queries using indices.")
            print("Some queries may need schema adjustments or additional indices.")
        else:
            print("\nWARNING: No queries are using indices!")
            print("This suggests indices may not be created or queries need optimization.")

        print("\n" + "="*80)
        print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)


if __name__ == '__main__':
    benchmark = PerformanceBenchmark()
    benchmark.run_benchmarks()

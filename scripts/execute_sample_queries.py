#!/usr/bin/env python3
"""
Execute Sample Queries - Comprehensive Database Analysis
Runs sample queries from the guide against the consolidated master database
Date: October 30, 2025
"""

import sqlite3
import time
import json
from datetime import datetime

DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"
OUTPUT_FILE = "analysis/SAMPLE_QUERY_RESULTS_20251030.md"

class QueryExecutor:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH, timeout=120)
        self.cur = self.conn.cursor()
        self.results = []

    def execute_query(self, query_num, title, description, sql, params=None):
        """Execute a single query and capture results"""
        print(f'\n{"=" * 80}')
        print(f'QUERY {query_num}: {title}')
        print(f'{"=" * 80}')
        print(f'Description: {description}')
        print()

        result = {
            'query_num': query_num,
            'title': title,
            'description': description,
            'sql': sql,
            'timestamp': datetime.now().isoformat(),
            'execution_time': None,
            'row_count': 0,
            'results': [],
            'error': None
        }

        try:
            start = time.time()
            if params:
                self.cur.execute(sql, params)
            else:
                self.cur.execute(sql)
            results = self.cur.fetchall()
            elapsed = time.time() - start

            result['execution_time'] = f"{elapsed:.3f}s"
            result['row_count'] = len(results)
            result['results'] = results[:20]  # Limit to first 20 rows

            print(f'Execution time: {elapsed:.3f}s')
            print(f'Rows returned: {len(results)}')
            if len(results) > 0:
                print(f'Sample (first {min(5, len(results))} rows):')
                for i, row in enumerate(results[:5], 1):
                    # Convert to safe ASCII representation
                    row_str = str(row)
                    if len(row_str) > 120:
                        row_str = row_str[:117] + '...'
                    print(f'  {i}. {row_str}')
            else:
                print('  (No results)')

        except Exception as e:
            result['error'] = str(e)
            print(f'ERROR: {e}')

        self.results.append(result)
        return result

    def write_markdown_report(self):
        """Write all results to markdown file"""
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write('# Sample Query Results - Master Database Analysis\n')
            f.write(f'**Execution Date**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
            f.write(f'**Database**: {DB_PATH}\n')
            f.write('\n---\n\n')

            f.write('## Executive Summary\n\n')
            f.write(f'- **Total Queries Executed**: {len(self.results)}\n')
            f.write(f'- **Successful**: {sum(1 for r in self.results if not r["error"])}\n')
            f.write(f'- **Failed**: {sum(1 for r in self.results if r["error"])}\n')
            f.write(f'- **Total Rows Returned**: {sum(r["row_count"] for r in self.results)}\n')
            f.write('\n---\n\n')

            for result in self.results:
                f.write(f'## Query {result["query_num"]}: {result["title"]}\n\n')
                f.write(f'**Description**: {result["description"]}\n\n')
                f.write(f'**Execution Time**: {result["execution_time"]}\n\n')
                f.write(f'**Rows Returned**: {result["row_count"]}\n\n')

                if result['error']:
                    f.write(f'**ERROR**: {result["error"]}\n\n')
                elif result['row_count'] > 0:
                    f.write('**Sample Results** (first 10 rows):\n\n')
                    f.write('```\n')
                    for i, row in enumerate(result['results'][:10], 1):
                        f.write(f'{i}. {row}\n')
                    f.write('```\n\n')
                else:
                    f.write('*(No results returned)*\n\n')

                f.write(f'**SQL Query:**\n```sql\n{result["sql"]}\n```\n\n')
                f.write('---\n\n')

    def run_all_queries(self):
        """Execute comprehensive query suite"""

        # QUERY 1: China-related research trends
        self.execute_query(
            1,
            "China-Related Research Output (2020-2025)",
            "Temporal analysis of China-related research publications and datasets",
            """
            SELECT
                year,
                COUNT(*) as total_publications,
                COUNT(CASE WHEN type = 'publication' THEN 1 END) as publications,
                COUNT(CASE WHEN type = 'dataset' THEN 1 END) as datasets
            FROM openaire_research
            WHERE china_related = 1 AND year >= 2020
            GROUP BY year
            ORDER BY year DESC
            """
        )

        # QUERY 2: Temporal trends comparison
        self.execute_query(
            2,
            "Research Trends - China vs Total (2015-2025)",
            "Year-over-year comparison showing China-related percentage of all research",
            """
            SELECT
                year,
                COUNT(*) as total_research,
                SUM(CASE WHEN china_related = 1 THEN 1 ELSE 0 END) as china_related,
                ROUND(SUM(CASE WHEN china_related = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as china_pct
            FROM openaire_research
            WHERE year >= 2015 AND year <= 2025
            GROUP BY year
            ORDER BY year DESC
            """
        )

        # QUERY 3: Top collaboration partners
        self.execute_query(
            3,
            "Top Countries by China Collaboration Volume",
            "Identifies primary research collaboration partners with China",
            """
            SELECT
                primary_country,
                COUNT(*) as collaboration_count
            FROM openaire_collaborations
            WHERE is_china_collaboration = 1
              AND primary_country IS NOT NULL
              AND primary_country <> ''
            GROUP BY primary_country
            ORDER BY collaboration_count DESC
            LIMIT 20
            """
        )

        # QUERY 4: GLEIF Chinese entity distribution
        self.execute_query(
            4,
            "GLEIF Chinese Entity Distribution by Region",
            "Legal entities registered with LEI across Chinese territories",
            """
            SELECT
                legal_address_country,
                COUNT(*) as entity_count,
                COUNT(DISTINCT entity_category) as distinct_categories
            FROM gleif_entities
            WHERE legal_address_country IN ('CN', 'HK', 'MO', 'TW')
            GROUP BY legal_address_country
            ORDER BY entity_count DESC
            """
        )

        # QUERY 5: OpenSanctions Chinese entities
        self.execute_query(
            5,
            "Chinese Entities on Sanctions Lists",
            "Count and categorization of Chinese entities appearing on sanctions lists",
            """
            SELECT
                entity_type,
                COUNT(*) as entity_count
            FROM opensanctions_entities
            WHERE china_related = 1
            GROUP BY entity_type
            ORDER BY entity_count DESC
            """
        )

        # QUERY 6: Corporate relationships volume
        self.execute_query(
            6,
            "GLEIF Relationship Network Scale",
            "Volume of corporate relationships by relationship type",
            """
            SELECT
                relationship_type,
                COUNT(*) as relationship_count
            FROM gleif_relationships
            WHERE relationship_type IS NOT NULL
            GROUP BY relationship_type
            ORDER BY relationship_count DESC
            LIMIT 15
            """
        )

        # QUERY 7: Cross-dataset - GLEIF entities by country (top 20)
        self.execute_query(
            7,
            "GLEIF Global Entity Distribution (Top 20 Countries)",
            "Legal entity counts by country - shows where LEI registration is most common",
            """
            SELECT
                legal_address_country as country,
                COUNT(*) as entity_count
            FROM gleif_entities
            WHERE legal_address_country IS NOT NULL
            GROUP BY legal_address_country
            ORDER BY entity_count DESC
            LIMIT 20
            """
        )

        # QUERY 8: Research type distribution (China-related)
        self.execute_query(
            8,
            "China-Related Research by Type",
            "Distribution of publication types in China-related research",
            """
            SELECT
                type,
                COUNT(*) as count,
                ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM openaire_research WHERE china_related = 1), 2) as percentage
            FROM openaire_research
            WHERE china_related = 1
            GROUP BY type
            ORDER BY count DESC
            """
        )

        # QUERY 9: OpenSanctions country distribution
        self.execute_query(
            9,
            "Sanctions List Geographic Distribution",
            "Countries with most entities on sanctions lists",
            """
            SELECT
                countries,
                COUNT(*) as entity_count
            FROM opensanctions_entities
            WHERE countries IS NOT NULL
              AND countries <> ''
            GROUP BY countries
            ORDER BY entity_count DESC
            LIMIT 20
            """
        )

        # QUERY 10: Recent research activity
        self.execute_query(
            10,
            "Recent China-Related Research (2024-2025)",
            "Most recent research publications involving China",
            """
            SELECT
                year,
                countries,
                type,
                LENGTH(title) as title_length
            FROM openaire_research
            WHERE china_related = 1
              AND year >= 2024
            ORDER BY year DESC
            LIMIT 25
            """
        )

        print(f'\n{"=" * 80}')
        print('ALL QUERIES COMPLETE')
        print(f'{"=" * 80}')
        print(f'\nTotal queries executed: {len(self.results)}')
        print(f'Successful: {sum(1 for r in self.results if not r["error"])}')
        print(f'Failed: {sum(1 for r in self.results if r["error"])}')
        print(f'\nWriting results to: {OUTPUT_FILE}')

        self.write_markdown_report()
        print('Report written successfully!')

    def close(self):
        self.conn.close()

def main():
    print('=' * 80)
    print('SAMPLE QUERY EXECUTOR - Consolidated Master Database')
    print('=' * 80)
    print()
    print(f'Database: {DB_PATH}')
    print(f'Output: {OUTPUT_FILE}')
    print()

    executor = QueryExecutor()
    try:
        executor.run_all_queries()
    finally:
        executor.close()

if __name__ == '__main__':
    main()

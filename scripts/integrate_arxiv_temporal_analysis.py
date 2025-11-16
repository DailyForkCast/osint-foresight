#!/usr/bin/env python3
"""
Integrate arXiv Data into Temporal Analysis
Combines OpenAIRE and arXiv datasets for comprehensive research trend analysis
Date: October 30, 2025
"""

import sqlite3
import json
from datetime import datetime
from collections import defaultdict

MASTER_DB = "F:/OSINT_WAREHOUSE/osint_master.db"
ARXIV_DB = "C:/Projects/OSINT-Foresight/data/kaggle_arxiv_processing.db"
OUTPUT_FILE = "analysis/ARXIV_OPENAIRE_TEMPORAL_ANALYSIS_20251030.md"
JSON_OUTPUT = "analysis/arxiv_openaire_temporal_analysis_20251030.json"

class TemporalAnalyzer:
    def __init__(self):
        self.conn = sqlite3.connect(MASTER_DB, timeout=120)
        self.cur = self.conn.cursor()
        # Attach arXiv database
        self.cur.execute(f"ATTACH DATABASE '{ARXIV_DB}' AS arxiv")
        self.results = {}

    def execute_query(self, query_name, description, sql):
        """Execute query and store results"""
        print(f"\n{'='*80}")
        print(f"Executing: {query_name}")
        print(f"{'='*80}")
        print(f"Description: {description}\n")

        try:
            self.cur.execute(sql)
            results = self.cur.fetchall()
            self.results[query_name] = {
                'description': description,
                'sql': sql,
                'results': results,
                'row_count': len(results)
            }
            print(f"OK - Returned {len(results)} rows")
            if results and len(results) <= 20:
                for row in results[:10]:
                    print(f"  {row}")
            return results
        except Exception as e:
            print(f"ERROR: {e}")
            self.results[query_name] = {
                'description': description,
                'sql': sql,
                'error': str(e)
            }
            return []

    def run_analysis(self):
        """Execute comprehensive temporal analysis"""

        print("\n" + "="*80)
        print("ARXIV + OPENAIRE TEMPORAL ANALYSIS")
        print("="*80)

        # QUERY 1: OpenAIRE temporal trends (2015-2025)
        self.execute_query(
            "openaire_temporal_trends",
            "OpenAIRE research output by year (2015-2025)",
            """
            SELECT
                year,
                COUNT(*) as total_publications,
                SUM(CASE WHEN china_related = 1 THEN 1 ELSE 0 END) as china_related,
                ROUND(SUM(CASE WHEN china_related = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as china_pct
            FROM openaire_research
            WHERE year >= 2015 AND year <= 2025
            GROUP BY year
            ORDER BY year DESC
            """
        )

        # QUERY 2: arXiv year distribution
        self.execute_query(
            "arxiv_year_distribution",
            "arXiv paper publication years - check data range",
            """
            SELECT
                MIN(year) as earliest_year,
                MAX(year) as latest_year,
                COUNT(*) as total_papers,
                COUNT(DISTINCT year) as distinct_years
            FROM arxiv.kaggle_arxiv_papers
            WHERE year IS NOT NULL
            """
        )

        # QUERY 3: arXiv temporal trends (2015-2025 for comparison)
        self.execute_query(
            "arxiv_temporal_trends",
            "arXiv paper output by year (2015-2025)",
            """
            SELECT
                year,
                COUNT(*) as total_papers
            FROM arxiv.kaggle_arxiv_papers
            WHERE year >= 2015 AND year <= 2025
              AND year IS NOT NULL
            GROUP BY year
            ORDER BY year DESC
            """
        )

        # QUERY 4: arXiv technology categories over time
        self.execute_query(
            "arxiv_technology_temporal",
            "arXiv papers by technology domain (2015-2025)",
            """
            SELECT
                p.year,
                t.technology_domain,
                COUNT(*) as paper_count
            FROM arxiv.kaggle_arxiv_papers p
            JOIN arxiv.kaggle_arxiv_technology t ON p.id = t.paper_id
            WHERE p.year >= 2015 AND p.year <= 2025
              AND p.year IS NOT NULL
              AND t.technology_domain IS NOT NULL
            GROUP BY p.year, t.technology_domain
            ORDER BY p.year DESC, paper_count DESC
            """
        )

        # QUERY 5: Check for China-related indicators in arXiv
        self.execute_query(
            "arxiv_china_indicators",
            "Identify China-related papers in arXiv (author affiliations sample)",
            """
            SELECT
                p.year,
                COUNT(DISTINCT p.id) as papers_with_china_authors
            FROM arxiv.kaggle_arxiv_papers p
            JOIN arxiv.kaggle_arxiv_authors a ON p.id = a.paper_id
            WHERE (
                LOWER(a.affiliation) LIKE '%china%'
                OR LOWER(a.affiliation) LIKE '%chinese%'
                OR LOWER(a.affiliation) LIKE '%beijing%'
                OR LOWER(a.affiliation) LIKE '%shanghai%'
                OR LOWER(a.affiliation) LIKE '%tsinghua%'
                OR LOWER(a.affiliation) LIKE '%peking university%'
            )
            AND p.year >= 2015 AND p.year <= 2025
            AND p.year IS NOT NULL
            GROUP BY p.year
            ORDER BY p.year DESC
            """
        )

        # QUERY 6: Combined dataset statistics
        self.execute_query(
            "combined_dataset_stats",
            "Combined OpenAIRE + arXiv coverage statistics",
            """
            SELECT
                'OpenAIRE' as source,
                COUNT(*) as total_records,
                MIN(year) as earliest_year,
                MAX(year) as latest_year,
                SUM(CASE WHEN china_related = 1 THEN 1 ELSE 0 END) as china_related_records
            FROM openaire_research
            WHERE year IS NOT NULL

            UNION ALL

            SELECT
                'arXiv' as source,
                COUNT(*) as total_records,
                MIN(year) as earliest_year,
                MAX(year) as latest_year,
                NULL as china_related_records
            FROM arxiv.kaggle_arxiv_papers
            WHERE year IS NOT NULL
            """
        )

        # QUERY 7: Year-over-year growth comparison
        self.execute_query(
            "yoy_growth_comparison",
            "Year-over-year growth rates: OpenAIRE vs arXiv",
            """
            WITH openaire_yearly AS (
                SELECT year, COUNT(*) as count
                FROM openaire_research
                WHERE year >= 2015 AND year <= 2025
                GROUP BY year
            ),
            arxiv_yearly AS (
                SELECT year, COUNT(*) as count
                FROM arxiv.kaggle_arxiv_papers
                WHERE year >= 2015 AND year <= 2025
                  AND year IS NOT NULL
                GROUP BY year
            )
            SELECT
                o.year,
                o.count as openaire_count,
                a.count as arxiv_count,
                ROUND((o.count * 100.0 / (SELECT SUM(count) FROM openaire_yearly)), 2) as openaire_pct,
                ROUND((a.count * 100.0 / (SELECT SUM(count) FROM arxiv_yearly)), 2) as arxiv_pct
            FROM openaire_yearly o
            LEFT JOIN arxiv_yearly a ON o.year = a.year
            ORDER BY o.year DESC
            """
        )

        # QUERY 8: Top arXiv categories (2020-2025)
        self.execute_query(
            "arxiv_top_categories_recent",
            "Most active arXiv categories (2020-2025)",
            """
            SELECT
                c.category,
                COUNT(DISTINCT p.id) as paper_count,
                COUNT(DISTINCT p.year) as years_active
            FROM arxiv.kaggle_arxiv_papers p
            JOIN arxiv.kaggle_arxiv_categories c ON p.id = c.paper_id
            WHERE p.year >= 2020 AND p.year <= 2025
              AND p.year IS NOT NULL
              AND c.category IS NOT NULL
            GROUP BY c.category
            ORDER BY paper_count DESC
            LIMIT 20
            """
        )

        # QUERY 9: China-related research growth comparison
        self.execute_query(
            "china_research_growth",
            "China-related research growth: OpenAIRE baseline vs arXiv potential",
            """
            SELECT
                year,
                COUNT(*) as openaire_china_papers,
                ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM openaire_research WHERE china_related = 1), 2) as pct_of_total
            FROM openaire_research
            WHERE china_related = 1
              AND year >= 2015 AND year <= 2025
            GROUP BY year
            ORDER BY year DESC
            """
        )

        # QUERY 10: Technology domain overlap check
        self.execute_query(
            "technology_domain_distribution",
            "arXiv technology domains - strategic technology focus",
            """
            SELECT
                technology_domain,
                COUNT(DISTINCT paper_id) as papers,
                ROUND(COUNT(DISTINCT paper_id) * 100.0 / (SELECT COUNT(DISTINCT paper_id) FROM arxiv.kaggle_arxiv_technology), 2) as pct
            FROM arxiv.kaggle_arxiv_technology
            WHERE technology_domain IS NOT NULL
            GROUP BY technology_domain
            ORDER BY papers DESC
            LIMIT 15
            """
        )

        print("\n" + "="*80)
        print("ANALYSIS COMPLETE")
        print("="*80)
        print(f"\nTotal queries executed: {len(self.results)}")
        print(f"Successful: {sum(1 for r in self.results.values() if 'error' not in r)}")
        print(f"Failed: {sum(1 for r in self.results.values() if 'error' in r)}")

    def write_report(self):
        """Generate markdown report"""
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write("# arXiv + OpenAIRE Temporal Analysis\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Master Database**: {MASTER_DB}\n")
            f.write(f"**arXiv Database**: {ARXIV_DB}\n")
            f.write("\n---\n\n")

            f.write("## Executive Summary\n\n")
            f.write(f"- **Total Queries**: {len(self.results)}\n")
            f.write(f"- **Successful**: {sum(1 for r in self.results.values() if 'error' not in r)}\n")
            f.write(f"- **Failed**: {sum(1 for r in self.results.values() if 'error' in r)}\n")
            f.write("\n---\n\n")

            # Write each query result
            for query_name, data in self.results.items():
                f.write(f"## {query_name.replace('_', ' ').title()}\n\n")
                f.write(f"**Description**: {data['description']}\n\n")

                if 'error' in data:
                    f.write(f"**ERROR**: {data['error']}\n\n")
                else:
                    f.write(f"**Rows Returned**: {data['row_count']}\n\n")
                    if data['results']:
                        f.write("**Results**:\n\n```\n")
                        for row in data['results'][:50]:  # Limit output
                            f.write(f"{row}\n")
                        f.write("```\n\n")

                f.write(f"**SQL**:\n```sql\n{data['sql']}\n```\n\n")
                f.write("---\n\n")

        print(f"\nOK - Report written to: {OUTPUT_FILE}")

        # Also write JSON for programmatic access
        json_safe_results = {}
        for query_name, data in self.results.items():
            json_safe_results[query_name] = {
                'description': data['description'],
                'row_count': data.get('row_count', 0),
                'results': [list(row) for row in data.get('results', [])] if 'results' in data else [],
                'error': data.get('error')
            }

        with open(JSON_OUTPUT, 'w', encoding='utf-8') as f:
            json.dump(json_safe_results, f, indent=2, ensure_ascii=False)

        print(f"OK - JSON data written to: {JSON_OUTPUT}")

    def close(self):
        self.conn.close()

def main():
    print("="*80)
    print("ARXIV + OPENAIRE TEMPORAL ANALYSIS")
    print("="*80)
    print()

    analyzer = TemporalAnalyzer()
    try:
        analyzer.run_analysis()
        analyzer.write_report()
    finally:
        analyzer.close()

    print("\n" + "="*80)
    print("INTEGRATION COMPLETE")
    print("="*80)

if __name__ == '__main__':
    main()

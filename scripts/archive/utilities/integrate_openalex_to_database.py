#!/usr/bin/env python3
"""
Integrate OpenAlex Chinese Research Data to Database
"""

import pandas as pd
import sqlite3
from pathlib import Path
from datetime import datetime
import json

class OpenAlexIntegrator:
    def __init__(self):
        self.openalex_dir = Path("data/openalex_chinese_research")
        self.output_dir = Path("F:/OSINT_Data/openalex_analytics")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.stats = {}

    def create_openalex_database(self):
        """Create OpenAlex analytics database"""
        print("\n" + "="*80)
        print("CREATING: OpenAlex Analytics Database")
        print("="*80)

        db_path = self.output_dir / 'openalex_chinese_research.db'
        print(f"\nDatabase: {db_path}")

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        total_records = 0

        # Table 1: Research Papers by Topic
        print("\n[1/3] Loading chinese_research_by_topic...")
        df = pd.read_csv(self.openalex_dir / 'chinese_research_by_topic.csv')
        df.to_sql('research_papers', conn, if_exists='replace', index=False)

        # Create indices
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tech_category ON research_papers(technology_category)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_pub_year ON research_papers(publication_year)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_openalex_id ON research_papers(openalex_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_doi ON research_papers(doi)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_citations ON research_papers(cited_by_count)")

        print(f"  Loaded: {len(df):,} records")
        print(f"  Indices: technology_category, publication_year, openalex_id, doi, citations")
        total_records += len(df)

        # Table 2: Top Institutions
        print("\n[2/3] Loading top_chinese_institutions...")
        df = pd.read_csv(self.openalex_dir / 'top_chinese_institutions.csv')
        df.to_sql('research_institutions', conn, if_exists='replace', index=False)

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_inst_id ON research_institutions(institution_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_inst_name ON research_institutions(institution_name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_works_count ON research_institutions(works_count_2020_2025)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_h_index ON research_institutions(h_index)")

        print(f"  Loaded: {len(df):,} records")
        print(f"  Indices: institution_id, institution_name, works_count, h_index")
        total_records += len(df)

        # Table 3: Annual Trends
        print("\n[3/3] Loading annual_trends_by_topic...")
        df = pd.read_csv(self.openalex_dir / 'annual_trends_by_topic.csv')
        df.to_sql('annual_publication_trends', conn, if_exists='replace', index=False)

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_trend_year ON annual_publication_trends(year)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_trend_category ON annual_publication_trends(technology_category)")

        print(f"  Loaded: {len(df):,} records")
        print(f"  Indices: year, technology_category")
        total_records += len(df)

        # Create views for analysis
        print("\n[VIEWS] Creating analytical views...")

        # View 1: Growth Analysis
        cursor.execute("""
            CREATE VIEW IF NOT EXISTS topic_growth_analysis AS
            SELECT
                technology_category,
                SUM(CASE WHEN year <= 2015 THEN publication_count ELSE 0 END) as pre_policy_total,
                SUM(CASE WHEN year > 2015 THEN publication_count ELSE 0 END) as post_policy_total,
                ROUND(
                    (CAST(SUM(CASE WHEN year > 2015 THEN publication_count ELSE 0 END) AS REAL) /
                     NULLIF(SUM(CASE WHEN year <= 2015 THEN publication_count ELSE 0 END), 0) - 1) * 100,
                    1
                ) as growth_pct
            FROM annual_publication_trends
            GROUP BY technology_category
            ORDER BY growth_pct DESC
        """)
        print("  Created: topic_growth_analysis")

        # View 2: Recent Impact Leaders
        cursor.execute("""
            CREATE VIEW IF NOT EXISTS high_impact_recent_papers AS
            SELECT
                technology_category,
                title,
                publication_year,
                cited_by_count,
                chinese_institutions,
                doi
            FROM research_papers
            WHERE publication_year >= 2020
                AND cited_by_count > 100
            ORDER BY cited_by_count DESC
        """)
        print("  Created: high_impact_recent_papers")

        # View 3: Institution Rankings
        cursor.execute("""
            CREATE VIEW IF NOT EXISTS institution_rankings AS
            SELECT
                institution_name,
                works_count_2020_2025,
                h_index,
                i10_index,
                cited_by_count,
                RANK() OVER (ORDER BY works_count_2020_2025 DESC) as rank_by_works,
                RANK() OVER (ORDER BY h_index DESC) as rank_by_h_index
            FROM research_institutions
            ORDER BY works_count_2020_2025 DESC
        """)
        print("  Created: institution_rankings")

        # Create metadata
        print("\n[METADATA] Creating database_metadata...")
        metadata = {
            'created': datetime.now().isoformat(),
            'source': 'OpenAlex API',
            'total_records': total_records,
            'tables': 3,
            'views': 3,
            'date_range': '2011-2025',
            'technology_topics': 10,
            'top_institutions': 100,
            'cost': '$0.00 (free API)',
            'purpose': 'Chinese technology research publications and institution analysis'
        }

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS database_metadata (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)

        for key, value in metadata.items():
            cursor.execute("INSERT OR REPLACE INTO database_metadata (key, value) VALUES (?, ?)",
                         (key, str(value)))

        conn.commit()
        conn.close()

        print(f"\n[OK] Database created successfully")
        print(f"  Total records: {total_records:,}")
        print(f"  Size: {db_path.stat().st_size / (1024**2):.2f} MB")

        self.stats['openalex_analytics'] = {
            'path': str(db_path),
            'records': total_records,
            'tables': 3,
            'views': 3,
            'size_mb': db_path.stat().st_size / (1024**2)
        }

        return db_path

    def test_queries(self, db_path):
        """Test database with sample queries"""
        print("\n" + "="*80)
        print("TESTING DATABASE QUERIES")
        print("="*80)

        conn = sqlite3.connect(db_path)

        # Query 1: Growth analysis
        print("\n[QUERY 1: Topic Growth Analysis]")
        df = pd.read_sql_query("SELECT * FROM topic_growth_analysis", conn)
        print(df.to_string(index=False))

        # Query 2: Top cited papers by topic
        print("\n[QUERY 2: Most Cited Papers by Topic (2020+)]")
        query = """
            SELECT
                technology_category,
                COUNT(*) as papers,
                AVG(cited_by_count) as avg_citations,
                MAX(cited_by_count) as max_citations
            FROM research_papers
            WHERE publication_year >= 2020
            GROUP BY technology_category
            ORDER BY avg_citations DESC
        """
        df = pd.read_sql_query(query, conn)
        print(df.to_string(index=False))

        # Query 3: Publication trends
        print("\n[QUERY 3: Annual Publication Trends (All Topics)]")
        query = """
            SELECT
                year,
                SUM(publication_count) as total_publications
            FROM annual_publication_trends
            GROUP BY year
            ORDER BY year
        """
        df = pd.read_sql_query(query, conn)
        print(df.to_string(index=False))

        # Query 4: Top institutions
        print("\n[QUERY 4: Top 10 Institutions by H-Index]")
        query = """
            SELECT
                institution_name,
                works_count_2020_2025,
                h_index,
                cited_by_count
            FROM research_institutions
            ORDER BY h_index DESC
            LIMIT 10
        """
        df = pd.read_sql_query(query, conn)
        print(df.to_string(index=False))

        conn.close()

    def generate_integration_summary(self):
        """Generate summary report"""
        print("\n" + "="*80)
        print("INTEGRATION SUMMARY")
        print("="*80)

        summary = {
            'integration_date': datetime.now().isoformat(),
            'databases_created': len(self.stats),
            'total_records': sum(s['records'] for s in self.stats.values()),
            'total_size_mb': sum(s['size_mb'] for s in self.stats.values()),
            'databases': self.stats
        }

        output_file = self.output_dir / 'integration_summary.json'
        with open(output_file, 'w') as f:
            json.dump(summary, f, indent=2)

        print(f"\nDatabases created: {summary['databases_created']}")
        print(f"Total records: {summary['total_records']:,}")
        print(f"Total size: {summary['total_size_mb']:.2f} MB")

        print("\n[DATABASE LOCATION]")
        for db_name, info in self.stats.items():
            print(f"\n  {db_name}:")
            print(f"    Path: {info['path']}")
            print(f"    Records: {info['records']:,}")
            print(f"    Tables: {info['tables']}")
            print(f"    Views: {info['views']}")
            print(f"    Size: {info['size_mb']:.2f} MB")

        print(f"\n\nSummary saved: {output_file}")

        return summary

    def integrate_all(self):
        """Run complete integration"""
        print("="*80)
        print("OPENALEX DATA INTEGRATION")
        print("="*80)

        # Create database
        db_path = self.create_openalex_database()

        # Test queries
        self.test_queries(db_path)

        # Generate summary
        summary = self.generate_integration_summary()

        print("\n" + "="*80)
        print("INTEGRATION COMPLETE")
        print("="*80)

        return summary

def main():
    integrator = OpenAlexIntegrator()
    summary = integrator.integrate_all()

    print("\n" + "="*80)
    print("NEXT STEPS")
    print("="*80)
    print("\n1. Database ready for queries:")
    print("   sqlite3 F:/OSINT_Data/openalex_analytics/openalex_chinese_research.db")
    print("\n2. Sample queries available:")
    print("   - SELECT * FROM topic_growth_analysis;")
    print("   - SELECT * FROM high_impact_recent_papers LIMIT 20;")
    print("   - SELECT * FROM institution_rankings LIMIT 20;")
    print("\n3. Ready to extract more papers (increase from 200 to 10,000+ per topic)")

if __name__ == "__main__":
    main()

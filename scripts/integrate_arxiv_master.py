"""
Integrate arXiv data into F:/OSINT_WAREHOUSE/osint_master.db
Adds AI, Quantum, and Space publication data from arXiv API queries
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

# Paths
MASTER_DB = Path("F:/OSINT_WAREHOUSE/osint_master.db")
AI_DATA = Path("C:/Projects/OSINT - Foresight/analysis/ai_tech/arxiv_api_analysis.json")
QUANTUM_DATA = Path("C:/Projects/OSINT - Foresight/analysis/quantum_tech/arxiv_quantum_analysis.json")
SPACE_DATA = Path("C:/Projects/OSINT - Foresight/analysis/space_tech/arxiv_space_analysis.json")

def create_arxiv_tables(conn):
    """Create tables for arXiv data if they don't exist"""

    # Main papers table
    conn.execute("""
    CREATE TABLE IF NOT EXISTS arxiv_papers (
        arxiv_id TEXT PRIMARY KEY,
        title TEXT,
        published_date TEXT,
        year INTEGER,
        month INTEGER,
        updated_date TEXT,
        summary TEXT,
        primary_category TEXT,
        technology_domain TEXT,
        collection_date TEXT
    )
    """)

    # Authors table
    conn.execute("""
    CREATE TABLE IF NOT EXISTS arxiv_authors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        arxiv_id TEXT,
        author_name TEXT,
        author_order INTEGER,
        FOREIGN KEY (arxiv_id) REFERENCES arxiv_papers(arxiv_id)
    )
    """)

    # Categories table (papers can have multiple categories)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS arxiv_categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        arxiv_id TEXT,
        category TEXT,
        is_primary BOOLEAN,
        FOREIGN KEY (arxiv_id) REFERENCES arxiv_papers(arxiv_id)
    )
    """)

    # Summary statistics table
    conn.execute("""
    CREATE TABLE IF NOT EXISTS arxiv_statistics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        technology_domain TEXT,
        category TEXT,
        year INTEGER,
        paper_count INTEGER,
        collection_date TEXT,
        UNIQUE(technology_domain, category, year)
    )
    """)

    # Integration metadata
    conn.execute("""
    CREATE TABLE IF NOT EXISTS arxiv_integration_metadata (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        integration_date TEXT,
        technology_domain TEXT,
        total_papers INTEGER,
        categories_analyzed TEXT,
        years_covered TEXT,
        data_source TEXT,
        notes TEXT
    )
    """)

    conn.commit()
    print("[OK] arXiv tables created/verified")

def load_arxiv_data(file_path):
    """Load arXiv JSON data"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def insert_papers(conn, papers, technology_domain, collection_date):
    """Insert papers into database"""

    inserted = 0
    skipped = 0

    for paper in papers:
        try:
            # Insert paper
            conn.execute("""
                INSERT OR IGNORE INTO arxiv_papers (
                    arxiv_id, title, published_date, year, month,
                    updated_date, summary, primary_category,
                    technology_domain, collection_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                paper['id'],
                paper['title'],
                paper['published'],
                paper['year'],
                paper['month'],
                paper['updated'],
                paper.get('summary', ''),
                paper['categories'][0] if paper['categories'] else None,
                technology_domain,
                collection_date
            ))

            if conn.total_changes > 0:
                inserted += 1

                # Insert authors
                for idx, author in enumerate(paper['authors']):
                    conn.execute("""
                        INSERT INTO arxiv_authors (arxiv_id, author_name, author_order)
                        VALUES (?, ?, ?)
                    """, (paper['id'], author, idx))

                # Insert categories
                for idx, category in enumerate(paper['categories']):
                    conn.execute("""
                        INSERT INTO arxiv_categories (arxiv_id, category, is_primary)
                        VALUES (?, ?, ?)
                    """, (paper['id'], category, idx == 0))
            else:
                skipped += 1

        except Exception as e:
            print(f"  [WARN] Error inserting paper {paper.get('id', 'unknown')}: {e}")
            continue

    return inserted, skipped

def insert_statistics(conn, data, technology_domain, collection_date):
    """Insert aggregated statistics"""

    category_year_data = data.get('papers_per_category_per_year', {})

    for category, years in category_year_data.items():
        for year, count in years.items():
            conn.execute("""
                INSERT OR REPLACE INTO arxiv_statistics (
                    technology_domain, category, year, paper_count, collection_date
                ) VALUES (?, ?, ?, ?, ?)
            """, (technology_domain, category, int(year), count, collection_date))

    print(f"  [OK] Statistics inserted for {len(category_year_data)} categories")

def insert_metadata(conn, technology_domain, total_papers, categories, years, collection_date):
    """Insert integration metadata"""

    conn.execute("""
        INSERT INTO arxiv_integration_metadata (
            integration_date, technology_domain, total_papers,
            categories_analyzed, years_covered, data_source, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        collection_date,
        technology_domain,
        total_papers,
        ', '.join(categories),
        years,
        'arXiv API (http://export.arxiv.org/api/query)',
        'Initial integration - data quality issues noted (year-to-year volatility)'
    ))

def integrate_arxiv_data():
    """Main integration function"""

    print("=" * 80)
    print("arXiv DATA INTEGRATION TO MASTER DATABASE")
    print("=" * 80)
    print()

    if not MASTER_DB.exists():
        print(f"[ERROR] Master database not found: {MASTER_DB}")
        return

    print(f"Master database: {MASTER_DB}")
    print(f"Size: {MASTER_DB.stat().st_size / (1024**3):.2f} GB")
    print()

    # Connect to database
    conn = sqlite3.connect(str(MASTER_DB))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")

    # Create tables
    create_arxiv_tables(conn)

    collection_date = datetime.now().isoformat()

    # Process each technology domain
    technologies = [
        ('AI', AI_DATA, 'Artificial Intelligence'),
        ('Quantum', QUANTUM_DATA, 'Quantum Technology'),
        ('Space', SPACE_DATA, 'Space Technology')
    ]

    total_papers_inserted = 0

    for domain_short, data_path, domain_full in technologies:
        print(f"\n{'=' * 80}")
        print(f"Processing: {domain_full}")
        print(f"{'=' * 80}")

        if not data_path.exists():
            print(f"[WARN] Data file not found: {data_path}")
            continue

        # Load data
        print(f"Loading data from: {data_path.name}")
        data = load_arxiv_data(data_path)

        # Get metadata
        metadata = data.get('metadata', {})
        categories = metadata.get('categories', [])
        years = metadata.get('years', [])
        sample_papers = data.get('sample_papers', [])

        print(f"  Categories: {len(categories)}")
        print(f"  Years: {min(years) if years else 'N/A'} - {max(years) if years else 'N/A'}")
        print(f"  Sample papers available: {len(sample_papers)}")

        # Insert sample papers (first 100)
        if sample_papers:
            print(f"\nInserting sample papers...")
            inserted, skipped = insert_papers(conn, sample_papers, domain_short, collection_date)
            print(f"  [OK] Inserted: {inserted}, Skipped (duplicates): {skipped}")
            total_papers_inserted += inserted

        # Insert statistics
        print(f"\nInserting statistics...")
        insert_statistics(conn, data, domain_short, collection_date)

        # Insert metadata
        total_papers = data.get('total_papers_per_year', {})
        total_count = sum(total_papers.values()) if total_papers else len(sample_papers)

        insert_metadata(
            conn,
            domain_short,
            total_count,
            categories,
            f"{min(years)}-{max(years)}" if years else "2020-2025",
            collection_date
        )

        print(f"  [OK] Metadata recorded (total papers in analysis: {total_count:,})")

    # Commit all changes
    conn.commit()

    # Generate summary
    print(f"\n{'=' * 80}")
    print("INTEGRATION SUMMARY")
    print(f"{'=' * 80}")

    # Count records
    papers_count = conn.execute("SELECT COUNT(*) FROM arxiv_papers").fetchone()[0]
    authors_count = conn.execute("SELECT COUNT(*) FROM arxiv_authors").fetchone()[0]
    stats_count = conn.execute("SELECT COUNT(*) FROM arxiv_statistics").fetchone()[0]

    print(f"\nRecords in master database:")
    print(f"  Papers (sample): {papers_count:,}")
    print(f"  Authors: {authors_count:,}")
    print(f"  Statistics entries: {stats_count:,}")

    # Technology breakdown
    print(f"\nPapers per technology:")
    tech_counts = conn.execute("""
        SELECT technology_domain, COUNT(*)
        FROM arxiv_papers
        GROUP BY technology_domain
    """).fetchall()

    for tech, count in tech_counts:
        print(f"  {tech}: {count:,}")

    # Year breakdown
    print(f"\nPapers per year (sample):")
    year_counts = conn.execute("""
        SELECT year, COUNT(*)
        FROM arxiv_papers
        GROUP BY year
        ORDER BY year
    """).fetchall()

    for year, count in year_counts:
        print(f"  {year}: {count:,}")

    # Statistics summary
    print(f"\nStatistics coverage:")
    stats_summary = conn.execute("""
        SELECT technology_domain, COUNT(DISTINCT category),
               MIN(year), MAX(year), SUM(paper_count)
        FROM arxiv_statistics
        GROUP BY technology_domain
    """).fetchall()

    for tech, cat_count, min_year, max_year, total in stats_summary:
        print(f"  {tech}: {cat_count} categories, {min_year}-{max_year}, {total:,} total papers")

    conn.close()

    print(f"\n{'=' * 80}")
    print("[OK] INTEGRATION COMPLETE")
    print(f"{'=' * 80}")
    print(f"\nMaster database updated: {MASTER_DB}")
    print(f"Integration date: {collection_date}")
    print(f"Total sample papers inserted: {total_papers_inserted:,}")
    print()

if __name__ == '__main__':
    integrate_arxiv_data()

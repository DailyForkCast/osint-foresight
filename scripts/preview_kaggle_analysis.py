"""
Quick Preview Analysis on Partial Kaggle arXiv Data
Run while processing continues - shows interim insights
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

PROCESSING_DB = Path("C:/Projects/OSINT - Foresight/data/kaggle_arxiv_processing.db")
OUTPUT_FILE = Path("C:/Projects/OSINT - Foresight/analysis/kaggle_preview_results.json")

def preview_analysis():
    """Quick analysis on partial dataset"""

    print("=" * 80)
    print("KAGGLE ARXIV PREVIEW ANALYSIS (PARTIAL DATA)")
    print("=" * 80)
    print()

    if not PROCESSING_DB.exists():
        print("[ERROR] Database not found")
        return

    conn = sqlite3.connect(str(PROCESSING_DB))

    results = {
        'analysis_date': datetime.now().isoformat(),
        'note': 'Partial data - processing in progress'
    }

    # Overall stats
    papers = conn.execute("SELECT COUNT(*) FROM kaggle_arxiv_papers").fetchone()[0]
    authors_total = conn.execute("SELECT COUNT(*) FROM kaggle_arxiv_authors").fetchone()[0]
    unique_authors = conn.execute("SELECT COUNT(DISTINCT author_name) FROM kaggle_arxiv_authors").fetchone()[0]

    print(f"Papers processed: {papers:,}")
    print(f"Author records: {authors_total:,}")
    print(f"Unique authors: {unique_authors:,}")
    print()

    results['total_papers'] = papers
    results['total_author_records'] = authors_total
    results['unique_authors'] = unique_authors

    # Technology breakdown
    print("Papers per technology:")
    tech_counts = conn.execute("""
        SELECT technology_domain, COUNT(DISTINCT arxiv_id) as papers,
               AVG(match_score) as avg_score
        FROM kaggle_arxiv_technology
        GROUP BY technology_domain
        ORDER BY papers DESC
    """).fetchall()

    results['technology_breakdown'] = []
    for tech, count, score in tech_counts:
        pct = (count / papers * 100) if papers > 0 else 0
        print(f"  {tech:20s}: {count:>8,} papers ({pct:>5.1f}%) [score: {score:.2f}]")
        results['technology_breakdown'].append({
            'technology': tech,
            'papers': count,
            'percentage': pct,
            'avg_match_score': score
        })

    # Recent trends (2020-2024)
    print("\nRecent trends (2020-2024):")
    recent_by_tech = {}

    for tech, _, _ in tech_counts[:5]:  # Top 5 technologies
        trends = conn.execute("""
            SELECT submission_year, COUNT(*) as papers
            FROM kaggle_arxiv_papers p
            JOIN kaggle_arxiv_technology t ON p.arxiv_id = t.arxiv_id
            WHERE t.technology_domain = ?
              AND submission_year BETWEEN 2020 AND 2024
            GROUP BY submission_year
            ORDER BY submission_year
        """, (tech,)).fetchall()

        if trends and len(trends) >= 2:
            recent_by_tech[tech] = {year: count for year, count in trends}

            # Calculate growth
            first_count = trends[0][1]
            last_count = trends[-1][1]
            growth = ((last_count - first_count) / first_count * 100) if first_count > 0 else 0

            print(f"\n{tech}:")
            for year, count in trends:
                print(f"  {year}: {count:>6,} papers")
            print(f"  Growth 2020-2024: {growth:+.1f}%")

    results['recent_trends'] = recent_by_tech

    # Top categories
    print("\n" + "=" * 80)
    print("Top 10 arXiv categories (overall):")
    top_cats = conn.execute("""
        SELECT category, COUNT(*) as papers
        FROM kaggle_arxiv_categories
        GROUP BY category
        ORDER BY papers DESC
        LIMIT 10
    """).fetchall()

    results['top_categories'] = []
    for cat, count in top_cats:
        print(f"  {cat:25s}: {count:>8,} papers")
        results['top_categories'].append({'category': cat, 'papers': count})

    # Interdisciplinary papers
    print("\n" + "=" * 80)
    print("Interdisciplinary research:")
    multi_tech = conn.execute("""
        SELECT COUNT(DISTINCT arxiv_id)
        FROM (
            SELECT arxiv_id, COUNT(DISTINCT technology_domain) as tech_count
            FROM kaggle_arxiv_technology
            GROUP BY arxiv_id
            HAVING tech_count > 1
        )
    """).fetchone()[0]

    pct_multi = (multi_tech / papers * 100) if papers > 0 else 0
    print(f"  Papers spanning multiple technologies: {multi_tech:,} ({pct_multi:.1f}%)")

    results['interdisciplinary_papers'] = multi_tech
    results['interdisciplinary_percentage'] = pct_multi

    # Top technology pairs
    print("\nTop technology pairs (papers appearing in both):")
    pairs = conn.execute("""
        SELECT t1.technology_domain as tech1,
               t2.technology_domain as tech2,
               COUNT(DISTINCT t1.arxiv_id) as papers
        FROM kaggle_arxiv_technology t1
        JOIN kaggle_arxiv_technology t2 ON t1.arxiv_id = t2.arxiv_id
        WHERE t1.technology_domain < t2.technology_domain
        GROUP BY t1.technology_domain, t2.technology_domain
        ORDER BY papers DESC
        LIMIT 10
    """).fetchall()

    results['top_technology_pairs'] = []
    for tech1, tech2, count in pairs:
        print(f"  {tech1} + {tech2}: {count:,} papers")
        results['top_technology_pairs'].append({
            'tech1': tech1,
            'tech2': tech2,
            'papers': count
        })

    # Geographic distribution (top 10 countries)
    print("\n" + "=" * 80)
    print("Geographic distribution (inferred from affiliations):")
    countries = conn.execute("""
        SELECT inferred_country, COUNT(DISTINCT arxiv_id) as papers
        FROM kaggle_arxiv_authors
        WHERE inferred_country IS NOT NULL
        GROUP BY inferred_country
        ORDER BY papers DESC
        LIMIT 10
    """).fetchall()

    results['top_countries'] = []
    if countries:
        for country, count in countries:
            print(f"  {country:20s}: {count:>8,} papers")
            results['top_countries'].append({'country': country, 'papers': count})
    else:
        print("  (No country data inferred yet)")

    # Collaboration stats
    print("\n" + "=" * 80)
    print("Collaboration patterns:")
    collab = conn.execute("""
        SELECT AVG(author_count) as avg_auth,
               MIN(author_count) as min_auth,
               MAX(author_count) as max_auth
        FROM kaggle_arxiv_papers
        WHERE author_count > 0
    """).fetchone()

    if collab:
        avg_auth, min_auth, max_auth = collab
        print(f"  Average authors per paper: {avg_auth:.1f}")
        print(f"  Range: {min_auth} - {max_auth} authors")

        results['collaboration'] = {
            'avg_authors': avg_auth,
            'min_authors': min_auth,
            'max_authors': max_auth
        }

    # Save results
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(results, f, indent=2)

    print("\n" + "=" * 80)
    print("[OK] PREVIEW COMPLETE")
    print(f"Results saved: {OUTPUT_FILE}")
    print("=" * 80)
    print()

    conn.close()

if __name__ == '__main__':
    preview_analysis()

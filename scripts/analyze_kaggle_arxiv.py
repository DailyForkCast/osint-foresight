"""
Comprehensive Analysis Queries for Kaggle arXiv Dataset
Extracts insights across all 9 technology domains
"""

import sqlite3
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# Paths
PROCESSING_DB = Path("C:/Projects/OSINT - Foresight/data/kaggle_arxiv_processing.db")
OUTPUT_DIR = Path("C:/Projects/OSINT - Foresight/analysis/kaggle_arxiv_analysis")

def run_analysis():
    """Execute comprehensive analysis queries"""

    print("=" * 80)
    print("KAGGLE ARXIV COMPREHENSIVE ANALYSIS")
    print("=" * 80)
    print()

    if not PROCESSING_DB.exists():
        print(f"[ERROR] Database not found: {PROCESSING_DB}")
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(PROCESSING_DB))

    # =========================================================================
    # QUERY 1: Papers Per Technology (Overall Count)
    # =========================================================================
    print("\n" + "=" * 80)
    print("QUERY 1: PAPERS PER TECHNOLOGY")
    print("=" * 80)

    tech_counts = conn.execute("""
        SELECT technology_domain, COUNT(DISTINCT arxiv_id) as papers,
               AVG(match_score) as avg_score
        FROM kaggle_arxiv_technology
        GROUP BY technology_domain
        ORDER BY papers DESC
    """).fetchall()

    results_q1 = []
    for tech, count, avg_score in tech_counts:
        print(f"  {tech:20s}: {count:>8,} papers (avg match score: {avg_score:.2f})")
        results_q1.append({
            'technology': tech,
            'paper_count': count,
            'avg_match_score': avg_score
        })

    # =========================================================================
    # QUERY 2: Year-Over-Year Growth (2015-2024)
    # =========================================================================
    print("\n" + "=" * 80)
    print("QUERY 2: PUBLICATION TRENDS (2015-2024)")
    print("=" * 80)

    yearly_trends = {}

    for tech, _, _ in tech_counts:
        trends = conn.execute("""
            SELECT submission_year, COUNT(*) as papers
            FROM kaggle_arxiv_papers p
            JOIN kaggle_arxiv_technology t ON p.arxiv_id = t.arxiv_id
            WHERE t.technology_domain = ?
              AND submission_year >= 2015 AND submission_year <= 2024
            GROUP BY submission_year
            ORDER BY submission_year
        """, (tech,)).fetchall()

        yearly_trends[tech] = {year: count for year, count in trends}

        # Calculate CAGR (2015-2024)
        if trends and len(trends) >= 2:
            first_year, first_count = trends[0]
            last_year, last_count = trends[-1]

            if first_count > 0 and last_year > first_year:
                years = last_year - first_year
                cagr = ((last_count / first_count) ** (1 / years) - 1) * 100

                print(f"\n{tech}:")
                for year, count in trends:
                    print(f"  {year}: {count:>6,} papers")
                print(f"  CAGR ({first_year}-{last_year}): {cagr:+.1f}%")

    # Save trends
    with open(OUTPUT_DIR / "yearly_trends.json", 'w') as f:
        json.dump(yearly_trends, f, indent=2)

    # =========================================================================
    # QUERY 3: Top Categories Per Technology
    # =========================================================================
    print("\n" + "=" * 80)
    print("QUERY 3: TOP 5 ARXIV CATEGORIES PER TECHNOLOGY")
    print("=" * 80)

    top_categories = {}

    for tech, _, _ in tech_counts:
        cats = conn.execute("""
            SELECT c.category, COUNT(*) as papers
            FROM kaggle_arxiv_categories c
            JOIN kaggle_arxiv_technology t ON c.arxiv_id = t.arxiv_id
            WHERE t.technology_domain = ?
            GROUP BY c.category
            ORDER BY papers DESC
            LIMIT 5
        """, (tech,)).fetchall()

        print(f"\n{tech}:")
        top_categories[tech] = []
        for cat, count in cats:
            print(f"  {cat:20s}: {count:>6,} papers")
            top_categories[tech].append({'category': cat, 'papers': count})

    # Save
    with open(OUTPUT_DIR / "top_categories.json", 'w') as f:
        json.dump(top_categories, f, indent=2)

    # =========================================================================
    # QUERY 4: Author Productivity Analysis
    # =========================================================================
    print("\n" + "=" * 80)
    print("QUERY 4: AUTHOR PRODUCTIVITY (TOP 10 AUTHORS PER TECHNOLOGY)")
    print("=" * 80)

    top_authors = {}

    for tech, _, _ in tech_counts[:3]:  # Top 3 technologies only (for speed)
        authors = conn.execute("""
            SELECT a.author_name, COUNT(DISTINCT a.arxiv_id) as papers,
                   a.inferred_affiliation, a.inferred_country
            FROM kaggle_arxiv_authors a
            JOIN kaggle_arxiv_technology t ON a.arxiv_id = t.arxiv_id
            WHERE t.technology_domain = ?
            GROUP BY a.author_name
            ORDER BY papers DESC
            LIMIT 10
        """, (tech,)).fetchall()

        print(f"\n{tech}:")
        top_authors[tech] = []
        for author, paper_count, affiliation, country in authors:
            affil_str = f"{affiliation}, {country}" if affiliation and country else affiliation or country or "Unknown"
            print(f"  {author[:40]:40s}: {paper_count:>4} papers ({affil_str})")
            top_authors[tech].append({
                'author': author,
                'papers': paper_count,
                'affiliation': affiliation,
                'country': country
            })

    # Save
    with open(OUTPUT_DIR / "top_authors.json", 'w') as f:
        json.dump(top_authors, f, indent=2)

    # =========================================================================
    # QUERY 5: Multi-Technology Papers (Interdisciplinary Research)
    # =========================================================================
    print("\n" + "=" * 80)
    print("QUERY 5: INTERDISCIPLINARY PAPERS (Multiple Technologies)")
    print("=" * 80)

    multi_tech = conn.execute("""
        SELECT arxiv_id, COUNT(DISTINCT technology_domain) as tech_count
        FROM kaggle_arxiv_technology
        GROUP BY arxiv_id
        HAVING tech_count > 1
        ORDER BY tech_count DESC
    """).fetchall()

    print(f"\nPapers spanning multiple technologies: {len(multi_tech):,}")

    # Distribution
    tech_count_dist = {}
    for _, count in multi_tech:
        tech_count_dist[count] = tech_count_dist.get(count, 0) + 1

    print("\nDistribution:")
    for num_techs, num_papers in sorted(tech_count_dist.items()):
        print(f"  {num_techs} technologies: {num_papers:>6,} papers")

    # Top interdisciplinary papers
    print("\nTop 5 most interdisciplinary papers:")
    top_inter = conn.execute("""
        SELECT p.arxiv_id, p.title,
               GROUP_CONCAT(t.technology_domain, ', ') as technologies,
               p.submission_year
        FROM kaggle_arxiv_papers p
        JOIN kaggle_arxiv_technology t ON p.arxiv_id = t.arxiv_id
        GROUP BY p.arxiv_id
        HAVING COUNT(DISTINCT t.technology_domain) >= 3
        ORDER BY COUNT(DISTINCT t.technology_domain) DESC
        LIMIT 5
    """).fetchall()

    for arxiv_id, title, techs, year in top_inter:
        print(f"\n  {arxiv_id} ({year})")
        print(f"  {title[:70]}...")
        print(f"  Technologies: {techs}")

    # =========================================================================
    # QUERY 6: Collaboration Patterns (Authors Per Paper)
    # =========================================================================
    print("\n" + "=" * 80)
    print("QUERY 6: COLLABORATION PATTERNS")
    print("=" * 80)

    collab_stats = {}

    for tech, _, _ in tech_counts:
        stats = conn.execute("""
            SELECT
                AVG(author_count) as avg_authors,
                MIN(author_count) as min_authors,
                MAX(author_count) as max_authors
            FROM kaggle_arxiv_papers p
            JOIN kaggle_arxiv_technology t ON p.arxiv_id = t.arxiv_id
            WHERE t.technology_domain = ?
        """, (tech,)).fetchone()

        avg_auth, min_auth, max_auth = stats
        print(f"\n{tech}:")
        print(f"  Avg authors per paper: {avg_auth:.1f}")
        print(f"  Range: {min_auth} - {max_auth} authors")

        collab_stats[tech] = {
            'avg_authors': avg_auth,
            'min_authors': min_auth,
            'max_authors': max_auth
        }

    # Save
    with open(OUTPUT_DIR / "collaboration_stats.json", 'w') as f:
        json.dump(collab_stats, f, indent=2)

    # =========================================================================
    # QUERY 7: Geographic Distribution (Inferred Countries)
    # =========================================================================
    print("\n" + "=" * 80)
    print("QUERY 7: GEOGRAPHIC DISTRIBUTION (TOP 10 COUNTRIES)")
    print("=" * 80)

    countries = conn.execute("""
        SELECT inferred_country, COUNT(DISTINCT arxiv_id) as papers
        FROM kaggle_arxiv_authors
        WHERE inferred_country IS NOT NULL
        GROUP BY inferred_country
        ORDER BY papers DESC
        LIMIT 10
    """).fetchall()

    print("\nOverall (all technologies):")
    for country, paper_count in countries:
        print(f"  {country:20s}: {paper_count:>6,} papers")

    # Per technology
    geo_by_tech = {}
    for tech, _, _ in tech_counts[:5]:  # Top 5 technologies
        tech_countries = conn.execute("""
            SELECT a.inferred_country, COUNT(DISTINCT a.arxiv_id) as papers
            FROM kaggle_arxiv_authors a
            JOIN kaggle_arxiv_technology t ON a.arxiv_id = t.arxiv_id
            WHERE t.technology_domain = ?
              AND a.inferred_country IS NOT NULL
            GROUP BY a.inferred_country
            ORDER BY papers DESC
            LIMIT 5
        """, (tech,)).fetchall()

        print(f"\n{tech}:")
        geo_by_tech[tech] = []
        for country, paper_count in tech_countries:
            print(f"  {country:20s}: {paper_count:>6,} papers")
            geo_by_tech[tech].append({'country': country, 'papers': paper_count})

    # Save
    with open(OUTPUT_DIR / "geographic_distribution.json", 'w') as f:
        json.dump(geo_by_tech, f, indent=2)

    # =========================================================================
    # QUERY 8: Recent Trends (Last 3 Years)
    # =========================================================================
    print("\n" + "=" * 80)
    print("QUERY 8: RECENT TRENDS (2022-2024)")
    print("=" * 80)

    recent_trends = {}

    for tech, _, _ in tech_counts:
        recent = conn.execute("""
            SELECT submission_year, COUNT(*) as papers
            FROM kaggle_arxiv_papers p
            JOIN kaggle_arxiv_technology t ON p.arxiv_id = t.arxiv_id
            WHERE t.technology_domain = ?
              AND submission_year BETWEEN 2022 AND 2024
            GROUP BY submission_year
            ORDER BY submission_year
        """, (tech,)).fetchall()

        if recent:
            recent_trends[tech] = {year: count for year, count in recent}

            # Calculate growth
            years = [r[0] for r in recent]
            counts = [r[1] for r in recent]

            if len(counts) >= 2:
                growth_rate = ((counts[-1] - counts[0]) / counts[0] * 100) if counts[0] > 0 else 0

                print(f"\n{tech}:")
                for year, count in recent:
                    print(f"  {year}: {count:>6,} papers")
                print(f"  Growth (2022-2024): {growth_rate:+.1f}%")

    # Save
    with open(OUTPUT_DIR / "recent_trends.json", 'w') as f:
        json.dump(recent_trends, f, indent=2)

    # =========================================================================
    # QUERY 9: Keyword Frequency (Top Emerging Terms)
    # =========================================================================
    print("\n" + "=" * 80)
    print("QUERY 9: TOP KEYWORDS IN TITLES (2023-2024)")
    print("=" * 80)

    # Extract keywords from titles (simple word frequency)
    import re
    from collections import Counter

    for tech, _, _ in tech_counts[:3]:  # Top 3 technologies
        titles = conn.execute("""
            SELECT p.title
            FROM kaggle_arxiv_papers p
            JOIN kaggle_arxiv_technology t ON p.arxiv_id = t.arxiv_id
            WHERE t.technology_domain = ?
              AND p.submission_year BETWEEN 2023 AND 2024
        """, (tech,)).fetchall()

        # Count words
        word_counts = Counter()
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                     'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
                     'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                     'would', 'should', 'could', 'may', 'might', 'must', 'can', 'using',
                     'based', 'via', 'through', 'into', 'over', 'after', 'before'}

        for (title,) in titles:
            words = re.findall(r'\b[a-z]+\b', title.lower())
            for word in words:
                if word not in stopwords and len(word) > 3:
                    word_counts[word] += 1

        print(f"\n{tech} (Top 15 keywords 2023-2024):")
        for word, count in word_counts.most_common(15):
            print(f"  {word:20s}: {count:>5,}")

    # =========================================================================
    # QUERY 10: Technology Overlap Matrix
    # =========================================================================
    print("\n" + "=" * 80)
    print("QUERY 10: TECHNOLOGY OVERLAP MATRIX")
    print("=" * 80)

    # Papers that appear in multiple technologies
    overlap_matrix = {}

    tech_list = [t[0] for t in tech_counts]

    for tech1 in tech_list:
        overlap_matrix[tech1] = {}
        for tech2 in tech_list:
            if tech1 == tech2:
                continue

            overlap = conn.execute("""
                SELECT COUNT(DISTINCT t1.arxiv_id)
                FROM kaggle_arxiv_technology t1
                JOIN kaggle_arxiv_technology t2 ON t1.arxiv_id = t2.arxiv_id
                WHERE t1.technology_domain = ?
                  AND t2.technology_domain = ?
            """, (tech1, tech2)).fetchone()[0]

            overlap_matrix[tech1][tech2] = overlap

    print("\nPapers appearing in both technologies:")
    print(f"\n{'':20s}", end='')
    for tech in tech_list[:5]:  # First 5 only
        print(f"{tech[:10]:>12s}", end='')
    print()

    for tech1 in tech_list[:5]:
        print(f"{tech1:20s}", end='')
        for tech2 in tech_list[:5]:
            if tech1 == tech2:
                print(f"{'--':>12s}", end='')
            else:
                count = overlap_matrix.get(tech1, {}).get(tech2, 0)
                print(f"{count:>12,}", end='')
        print()

    # Save
    with open(OUTPUT_DIR / "technology_overlap.json", 'w') as f:
        json.dump(overlap_matrix, f, indent=2)

    # =========================================================================
    # SUMMARY REPORT
    # =========================================================================
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE - SUMMARY")
    print("=" * 80)

    total_papers = conn.execute("SELECT COUNT(*) FROM kaggle_arxiv_papers").fetchone()[0]
    total_authors = conn.execute("SELECT COUNT(DISTINCT author_name) FROM kaggle_arxiv_authors").fetchone()[0]

    print(f"\nTotal papers in database: {total_papers:,}")
    print(f"Unique authors: {total_authors:,}")
    print(f"Technologies analyzed: {len(tech_counts)}")
    print(f"\nOutput directory: {OUTPUT_DIR}")
    print(f"Files created: {len(list(OUTPUT_DIR.glob('*.json')))} JSON files")

    # Create summary document
    summary = {
        'analysis_date': datetime.now().isoformat(),
        'total_papers': total_papers,
        'unique_authors': total_authors,
        'technologies': len(tech_counts),
        'papers_per_technology': results_q1,
        'files_generated': [f.name for f in OUTPUT_DIR.glob('*.json')]
    }

    with open(OUTPUT_DIR / "analysis_summary.json", 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"\nSummary saved: {OUTPUT_DIR / 'analysis_summary.json'}")

    conn.close()

    print("\n" + "=" * 80)
    print("[OK] ANALYSIS COMPLETE")
    print("=" * 80)
    print()

if __name__ == '__main__':
    run_analysis()

"""
Query arXiv API for AI publications and generate time-series analysis
NO FABRICATION - Only report actual data from arXiv API
"""

import urllib.request
import xml.etree.ElementTree as ET
import json
import time
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timedelta

# AI-relevant arXiv categories
AI_CATEGORIES = {
    'cs.LG': 'Machine Learning',
    'cs.AI': 'Artificial Intelligence',
    'cs.CV': 'Computer Vision',
    'cs.CL': 'Computation and Language (NLP)',
    'cs.RO': 'Robotics',
    'cs.NE': 'Neural and Evolutionary Computing',
    'cs.MA': 'Multiagent Systems'
}

def query_arxiv(search_query, start=0, max_results=2000, sort_by='submittedDate', sort_order='descending'):
    """
    Query arXiv API
    Returns list of papers with metadata
    """
    base_url = 'http://export.arxiv.org/api/query?'
    query = f'search_query={search_query}&start={start}&max_results={max_results}&sortBy={sort_by}&sortOrder={sort_order}'

    full_url = base_url + query
    print(f"Querying: {search_query[:80]}... (start={start}, max={max_results})")

    try:
        response = urllib.request.urlopen(full_url, timeout=60).read()
        root = ET.fromstring(response)

        # Parse Atom XML
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        papers = []

        for entry in root.findall('atom:entry', ns):
            try:
                # Extract published date
                published_str = entry.find('atom:published', ns).text
                published_date = datetime.strptime(published_str, "%Y-%m-%dT%H:%M:%SZ")

                paper = {
                    'id': entry.find('atom:id', ns).text.split('/abs/')[-1],
                    'title': entry.find('atom:title', ns).text.strip().replace('\n', ' '),
                    'published': published_str,
                    'year': published_date.year,
                    'month': published_date.month,
                    'updated': entry.find('atom:updated', ns).text,
                    'summary': entry.find('atom:summary', ns).text.strip()[:500],  # First 500 chars
                    'authors': [author.find('atom:name', ns).text for author in entry.findall('atom:author', ns)],
                    'categories': [cat.attrib['term'] for cat in entry.findall('atom:category', ns)]
                }
                papers.append(paper)
            except Exception as e:
                print(f"  Warning: Error parsing entry: {e}")
                continue

        print(f"  Retrieved {len(papers)} papers")
        return papers

    except Exception as e:
        print(f"  ERROR: {e}")
        return []

def query_category_by_year(category, year, max_per_query=2000):
    """
    Query all papers in a category for a specific year
    arXiv API limits to 30,000 results per query, so we may need multiple queries
    """
    start_date = f"{year}0101000"
    end_date = f"{year}1231235959"

    search_query = f"cat:{category}+AND+submittedDate:[{start_date}+TO+{end_date}]"

    all_papers = []
    start = 0

    while True:
        papers = query_arxiv(search_query, start=start, max_results=max_per_query)

        if not papers:
            break

        all_papers.extend(papers)

        # If we got fewer than max_results, we've reached the end
        if len(papers) < max_per_query:
            break

        start += max_per_query

        # Stop if we've hit the 30,000 result limit
        if start >= 30000:
            print(f"  [WARN] Hit 30,000 result limit for {category} {year}")
            break

        # Be respectful with rate limiting
        time.sleep(3)

    return all_papers

def analyze_ai_publications():
    """
    Query arXiv for AI publications (2020-2025) and generate time-series
    """
    print("=" * 80)
    print("arXiv AI PUBLICATION ANALYSIS (API Method)")
    print("=" * 80)
    print()

    results = {
        'metadata': {
            'source': 'arXiv API (http://export.arxiv.org/api/query)',
            'query_date': datetime.now().isoformat(),
            'categories': list(AI_CATEGORIES.keys()),
            'years': list(range(2020, 2026))
        },
        'papers_per_category_per_year': {},
        'total_papers_per_year': defaultdict(int),
        'all_papers': []
    }

    # Query each category for each year
    for category in sorted(AI_CATEGORIES.keys()):
        print(f"\n{'=' * 80}")
        print(f"Category: {category} - {AI_CATEGORIES[category]}")
        print(f"{'=' * 80}")

        results['papers_per_category_per_year'][category] = {}

        for year in range(2020, 2026):
            print(f"\nQuerying {category} for {year}...")

            papers = query_category_by_year(category, year)

            count = len(papers)
            results['papers_per_category_per_year'][category][year] = count
            results['total_papers_per_year'][year] += count
            results['all_papers'].extend(papers)

            print(f"[OK] {category} {year}: {count:,} papers")

            # Be respectful with rate limiting between categories/years
            time.sleep(3)

    # Calculate growth rates (CAGR)
    print(f"\n{'=' * 80}")
    print("PUBLICATION TRENDS (2020-2025)")
    print(f"{'=' * 80}")

    for category in sorted(AI_CATEGORIES.keys()):
        print(f"\n{category} - {AI_CATEGORIES[category]}:")

        years_data = results['papers_per_category_per_year'][category]

        for year in sorted(years_data.keys()):
            count = years_data[year]
            print(f"  {year}: {count:>6,}")

        # Calculate CAGR
        if 2020 in years_data and 2025 in years_data:
            start_count = years_data[2020]
            end_count = years_data[2025]

            if start_count > 0:
                cagr = ((end_count / start_count) ** (1 / 5) - 1) * 100
                print(f"  CAGR (2020-2025): {cagr:+.1f}%")

    # Print totals
    print(f"\n{'=' * 80}")
    print("TOTAL AI PAPERS PER YEAR:")
    print(f"{'=' * 80}")

    for year in sorted(results['total_papers_per_year'].keys()):
        count = results['total_papers_per_year'][year]
        print(f"  {year}: {count:>7,}")

    # Save results
    output_file = Path("C:/Projects/OSINT - Foresight/analysis/ai_tech/arxiv_api_analysis.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Don't save all papers (too large), just metadata and counts
    save_data = {
        'metadata': results['metadata'],
        'papers_per_category_per_year': results['papers_per_category_per_year'],
        'total_papers_per_year': dict(results['total_papers_per_year']),
        'sample_papers': results['all_papers'][:100]  # Save first 100 as samples
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(save_data, f, indent=2, ensure_ascii=False)

    print(f"\n[OK] Analysis saved to: {output_file}")
    print(f"Total papers analyzed: {len(results['all_papers']):,}")

    return results

if __name__ == '__main__':
    print("Starting arXiv API analysis...")
    print("This will take ~15-20 minutes due to rate limiting (3 sec between requests)")
    print()

    results = analyze_ai_publications()

    print("\n" + "=" * 80)
    print("[OK] ANALYSIS COMPLETE")
    print("=" * 80)

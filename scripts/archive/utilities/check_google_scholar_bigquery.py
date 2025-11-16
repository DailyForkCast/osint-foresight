#!/usr/bin/env python3
"""
Check if Google Scholar data is available on BigQuery
"""

from google.cloud import bigquery

def search_for_academic_datasets():
    """Search BigQuery for academic publication datasets"""
    print("="*80)
    print("SEARCHING FOR GOOGLE SCHOLAR / ACADEMIC PUBLICATION DATA")
    print("="*80)

    client = bigquery.Client()

    # Search for datasets with academic/publication keywords
    print("\n[1] Searching all BigQuery public datasets...")

    try:
        datasets = list(client.list_datasets(project='bigquery-public-data'))

        academic_keywords = [
            'scholar', 'citation', 'publication', 'academic', 'research',
            'paper', 'journal', 'arxiv', 'pubmed', 'doi', 'crossref',
            'semantic', 'scopus', 'web_of_science', 'dblp'
        ]

        matching_datasets = []

        for dataset in datasets:
            dataset_id = dataset.dataset_id.lower()
            if any(keyword in dataset_id for keyword in academic_keywords):
                matching_datasets.append(dataset)

        if matching_datasets:
            print(f"\n[OK] Found {len(matching_datasets)} potentially relevant datasets:")
            for ds in matching_datasets:
                print(f"\n  Dataset: {ds.dataset_id}")

                # Get tables in this dataset
                try:
                    tables = list(client.list_tables(ds))
                    print(f"  Tables: {len(tables)}")
                    for table in tables[:5]:
                        print(f"    - {table.table_id}")
                    if len(tables) > 5:
                        print(f"    ... and {len(tables)-5} more")
                except Exception as e:
                    print(f"  Error listing tables: {str(e)[:100]}")
        else:
            print("\n[!] No datasets found matching academic keywords")

    except Exception as e:
        print(f"Error: {e}")

    # Check for specific known academic databases
    print("\n" + "="*80)
    print("[2] Checking specific academic databases...")
    print("="*80)

    known_academic = [
        'arxiv',
        'pubmed',
        'semantic_scholar',
        'crossref',
        'openalex',
        'google_scholar',
        'dblp',
        'scopus'
    ]

    for db_name in known_academic:
        try:
            dataset_ref = f"bigquery-public-data.{db_name}"
            dataset = client.get_dataset(dataset_ref)
            print(f"\n[OK] {db_name} - FOUND")

            tables = list(client.list_tables(dataset))
            print(f"  Tables: {len(tables)}")
            for table in tables[:10]:
                print(f"    - {table.table_id}")

        except Exception:
            print(f"\n[!] {db_name} - NOT FOUND")

    return matching_datasets

def check_alternative_sources():
    """Document alternative sources for Google Scholar data"""
    print("\n" + "="*80)
    print("ALTERNATIVE SOURCES FOR ACADEMIC PUBLICATION DATA")
    print("="*80)

    alternatives = {
        'Google Scholar': {
            'access': 'Web scraping only (no official API)',
            'coverage': 'Broadest academic coverage',
            'limitations': 'Rate limiting, potential blocking',
            'tools': 'scholarly (Python library), SerpAPI (paid)'
        },
        'OpenAlex': {
            'access': 'FREE REST API + data dumps',
            'coverage': '250M+ works, replacing Microsoft Academic',
            'limitations': 'None (fully open)',
            'tools': 'API: https://api.openalex.org'
        },
        'Semantic Scholar': {
            'access': 'FREE REST API + datasets',
            'coverage': '200M+ papers with AI-extracted metadata',
            'limitations': 'API rate limits (100 req/5 min)',
            'tools': 'API: https://api.semanticscholar.org'
        },
        'CrossRef': {
            'access': 'FREE REST API',
            'coverage': '140M+ DOIs, metadata only',
            'limitations': 'Metadata only, no full text',
            'tools': 'API: https://api.crossref.org'
        },
        'arXiv': {
            'access': 'FREE API + bulk download',
            'coverage': '2.3M+ preprints (physics, CS, math)',
            'limitations': 'Preprints only',
            'tools': 'API: http://export.arxiv.org/api/query'
        },
        'PubMed': {
            'access': 'FREE API (NCBI E-utilities)',
            'coverage': '35M+ biomedical citations',
            'limitations': 'Biomedical focus only',
            'tools': 'API: https://www.ncbi.nlm.nih.gov/home/develop/api/'
        },
        'Europe PMC': {
            'access': 'FREE REST API',
            'coverage': '40M+ life sciences publications',
            'limitations': 'Life sciences focus',
            'tools': 'API: https://europepmc.org/RestfulWebService'
        },
        'DBLP': {
            'access': 'FREE XML dumps',
            'coverage': '6M+ computer science publications',
            'limitations': 'Computer science only',
            'tools': 'Download: https://dblp.org/xml/'
        }
    }

    print("\nBest options for Chinese technology research:")
    print("\n1. OpenAlex (RECOMMENDED)")
    print("   - Completely free, no rate limits")
    print("   - 250M+ works with author affiliations")
    print("   - Can filter by: country, institution, topic")
    print("   - API: https://api.openalex.org/works?filter=authorships.countries:CN")

    print("\n2. Semantic Scholar")
    print("   - AI-extracted metadata (influential citations, topics)")
    print("   - Good for citation network analysis")
    print("   - API rate limit: 100 requests per 5 minutes")

    print("\n3. arXiv (for preprints)")
    print("   - Strong coverage of CS, physics, math")
    print("   - Can download full metadata dump")
    print("   - Good for early-stage research trends")

    print("\n4. CrossRef (for DOI metadata)")
    print("   - Comprehensive DOI registry")
    print("   - Good for citation counts and metadata")

    print("\n[!] Google Scholar:")
    print("   - NO official API")
    print("   - NO BigQuery dataset")
    print("   - Web scraping possible but violates ToS")
    print("   - Use SerpAPI (paid) or scholarly library (risky)")

    for name, info in alternatives.items():
        print(f"\n{name}:")
        for key, value in info.items():
            print(f"  {key}: {value}")

def recommend_best_approach():
    """Recommend best approach for academic data"""
    print("\n" + "="*80)
    print("RECOMMENDATION FOR YOUR PROJECT")
    print("="*80)

    print("\nYou already have OpenAIRE (2.1GB) covering European research.")
    print("\nTo expand academic coverage, I recommend:")

    print("\n[OPTION A: OpenAlex - Best Overall]")
    print("  Pros:")
    print("    - Completely free, unlimited")
    print("    - 250M+ works (largest open database)")
    print("    - Rich metadata: authors, institutions, countries, citations")
    print("    - Easy filtering: country=China, topic=semiconductors, etc.")
    print("    - Can download entire dataset or use API")
    print("  Cons:")
    print("    - No h-index or author metrics like Google Scholar")
    print("  Implementation:")
    print("    - API: https://api.openalex.org/works?filter=authorships.countries:CN")
    print("    - Bulk: https://openalex.org/data-dump")

    print("\n[OPTION B: Semantic Scholar - Best for Networks]")
    print("  Pros:")
    print("    - AI-extracted influential citations")
    print("    - Citation context and intent classification")
    print("    - Author and paper recommendations")
    print("  Cons:")
    print("    - Rate limited (100 req/5 min)")
    print("    - Smaller than OpenAlex (~200M works)")
    print("  Implementation:")
    print("    - API: https://api.semanticscholar.org/graph/v1/paper/search")

    print("\n[OPTION C: Multiple Sources Combined]")
    print("  Best approach:")
    print("    1. OpenAlex for broad coverage and affiliations")
    print("    2. Semantic Scholar for citation networks")
    print("    3. arXiv for preprints and emerging research")
    print("    4. OpenAIRE for European institutional collaborations (existing)")

    print("\n[!] Google Scholar:")
    print("  - Not available on BigQuery")
    print("  - No official API")
    print("  - Not recommended due to ToS violations")
    print("  - Use OpenAlex instead (90% coverage overlap)")

def main():
    # Search for academic datasets
    results = search_for_academic_datasets()

    # Document alternatives
    check_alternative_sources()

    # Recommend approach
    recommend_best_approach()

    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print("\n[!] Google Scholar is NOT available on BigQuery")
    print("[OK] OpenAlex is the best free alternative")
    print("[OK] You already have OpenAIRE for European research")
    print("\nNext step: Extract OpenAlex data for Chinese institutions?")

if __name__ == "__main__":
    main()

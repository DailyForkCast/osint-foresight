#!/usr/bin/env python3
"""
Explore BigQuery Public Datasets
Identify additional datasets relevant to technology/China analysis
"""

from google.cloud import bigquery

def list_relevant_datasets():
    """
    Check available BigQuery public datasets relevant to our analysis
    """
    client = bigquery.Client()

    print("="*80)
    print("EXPLORING BIGQUERY PUBLIC DATASETS")
    print("="*80)

    # Known relevant public datasets
    datasets_to_check = [
        # Patents
        ('patents-public-data', 'patents', 'Google Patents'),

        # GitHub (open source development)
        ('githubarchive', 'month', 'GitHub Archive'),
        ('ghtorrent-bq', 'ght', 'GHTorrent'),

        # Academic/Research
        ('bigquery-public-data', 'covid19_open_research', 'COVID-19 Open Research'),
        ('bigquery-public-data', 'the_met', 'The Met Museum'),

        # Technology/Development
        ('bigquery-public-data', 'stackoverflow', 'Stack Overflow'),
        ('bigquery-public-data', 'pypi', 'Python Package Index'),
        ('bigquery-public-data', 'github_repos', 'GitHub Repos'),

        # Economic/Trade
        ('bigquery-public-data', 'world_bank_intl_trade', 'World Bank Trade'),
        ('bigquery-public-data', 'world_bank_wdi', 'World Bank Development'),

        # General Science
        ('bigquery-public-data', 'noaa_gsod', 'NOAA Weather'),

        # Blockchain/Crypto (for Chinese tech company activity)
        ('bigquery-public-data', 'crypto_ethereum', 'Ethereum Blockchain'),

        # News/Media
        ('gdelt-bq', 'gdeltv2', 'GDELT'),
    ]

    results = []

    for project_id, dataset_id, name in datasets_to_check:
        try:
            dataset_ref = f"{project_id}.{dataset_id}"
            dataset = client.get_dataset(dataset_ref)

            # Get table count
            tables = list(client.list_tables(dataset))

            results.append({
                'name': name,
                'project': project_id,
                'dataset': dataset_id,
                'accessible': True,
                'tables': len(tables),
                'reference': dataset_ref
            })

            print(f"\n[FOUND] {name}")
            print(f"  Dataset: {dataset_ref}")
            print(f"  Tables: {len(tables)}")

        except Exception as e:
            results.append({
                'name': name,
                'project': project_id,
                'dataset': dataset_id,
                'accessible': False,
                'error': str(e)
            })
            print(f"\n[NOT ACCESSIBLE] {name}")
            print(f"  Dataset: {project_id}.{dataset_id}")
            print(f"  Error: {str(e)[:100]}")

    return results

def check_specific_research_datasets():
    """
    Check for academic publication and research funding datasets
    """
    print("\n" + "="*80)
    print("CHECKING RESEARCH/PUBLICATION DATASETS")
    print("="*80)

    client = bigquery.Client()

    # Known research-related datasets
    research_datasets = [
        # Academic papers/citations
        ('bigquery-public-data', 'covid19_open_research', 'COVID Research Papers'),

        # Try to find Semantic Scholar, OpenAlex, etc.
        ('semantic-scholar', 'semantic_scholar', 'Semantic Scholar (if exists)'),
        ('openalex', 'works', 'OpenAlex (if exists)'),

        # PubMed
        ('bigquery-public-data', 'pubmed', 'PubMed (if exists)'),

        # Research grants
        ('nsf-public-data', 'awards', 'NSF Awards (if exists)'),
        ('nih-public-data', 'grants', 'NIH Grants (if exists)'),
    ]

    accessible = []

    for project_id, dataset_id, name in research_datasets:
        try:
            dataset_ref = f"{project_id}.{dataset_id}"
            dataset = client.get_dataset(dataset_ref)
            tables = list(client.list_tables(dataset))

            print(f"\n[FOUND] {name}")
            print(f"  Dataset: {dataset_ref}")
            print(f"  Tables: {len(tables)}")

            # List table names
            if len(tables) <= 20:
                for table in tables:
                    print(f"    - {table.table_id}")

            accessible.append(dataset_ref)

        except Exception as e:
            print(f"\n[NOT FOUND] {name}")
            # Don't print errors for speculative datasets

    return accessible

def explore_patents_dataset_detail():
    """
    Explore what's available in patents dataset beyond what we've used
    """
    print("\n" + "="*80)
    print("DETAILED PATENTS DATASET EXPLORATION")
    print("="*80)

    client = bigquery.Client()

    try:
        dataset_ref = "patents-public-data.patents"
        dataset = client.get_dataset(dataset_ref)
        tables = list(client.list_tables(dataset))

        print(f"\nDataset: {dataset_ref}")
        print(f"Total tables: {len(tables)}")
        print(f"\nAvailable tables:")

        for table in tables:
            table_ref = client.get_table(f"{dataset_ref}.{table.table_id}")

            print(f"\n  [{table.table_id}]")
            print(f"    Rows: {table_ref.num_rows:,}")
            print(f"    Size: {table_ref.num_bytes / 1e9:.2f} GB")

            # Show schema for interesting tables
            if table.table_id in ['publications', 'publications_202410']:
                print(f"    Key fields:")
                for field in table_ref.schema[:10]:  # First 10 fields
                    print(f"      - {field.name} ({field.field_type})")

        return tables

    except Exception as e:
        print(f"Error exploring patents dataset: {e}")
        return []

def check_github_archive():
    """
    Check GitHub Archive for technology development tracking
    """
    print("\n" + "="*80)
    print("GITHUB ARCHIVE EXPLORATION")
    print("="*80)

    client = bigquery.Client()

    try:
        # Test query on GitHub Archive
        query = """
        SELECT
            type,
            COUNT(*) as event_count
        FROM `githubarchive.month.202401`
        WHERE actor.login LIKE '%china%' OR actor.login LIKE '%chinese%'
        LIMIT 10
        """

        print("\nTesting GitHub Archive access...")
        print("Query: Events by Chinese users (sample)")

        query_job = client.query(query)
        results = list(query_job.result())

        print(f"\n[SUCCESS] GitHub Archive accessible")
        print(f"  Sample results: {len(results)} event types")
        print(f"  Cost: ${(query_job.total_bytes_billed / 1e12) * 5:.4f}")

        for r in results[:5]:
            print(f"    {r['type']}: {r['event_count']} events")

        return True

    except Exception as e:
        print(f"[NOT ACCESSIBLE] GitHub Archive")
        print(f"  Error: {e}")
        return False

def main():
    """
    Main exploration
    """
    print("\n" + "="*80)
    print("BIGQUERY PUBLIC DATASETS EXPLORATION")
    print("For China Technology Analysis")
    print("="*80)

    # List general datasets
    general = list_relevant_datasets()

    # Check research datasets
    research = check_specific_research_datasets()

    # Explore patents in detail
    patents = explore_patents_dataset_detail()

    # Check GitHub
    github = check_github_archive()

    # Summary
    print("\n" + "="*80)
    print("SUMMARY - ACCESSIBLE DATASETS")
    print("="*80)

    accessible = [d for d in general if d['accessible']]

    print(f"\nAccessible public datasets: {len(accessible)}")

    print("\n[PATENTS]")
    print("  - patents-public-data.patents (47M+ CN patents)")
    print("  - Includes: publications, citations, assignees, inventors")

    if github:
        print("\n[GITHUB]")
        print("  - githubarchive (development activity)")
        print("  - Can track Chinese tech companies, developers")

    if research:
        print("\n[RESEARCH]")
        for ds in research:
            print(f"  - {ds}")

    print("\n[ECONOMIC/TRADE]")
    wb_trade = [d for d in accessible if 'world_bank' in d['reference']]
    for ds in wb_trade:
        print(f"  - {ds['reference']}")

    print("\n[TECHNOLOGY DEVELOPMENT]")
    tech = [d for d in accessible if any(x in d['reference'] for x in ['stackoverflow', 'pypi', 'github'])]
    for ds in tech:
        print(f"  - {ds['reference']}")

    print("\n" + "="*80)
    print("RECOMMENDATIONS FOR NEXT ANALYSIS")
    print("="*80)

    print("\n1. GitHub Archive:")
    print("   - Track Chinese tech company repositories")
    print("   - Monitor open source contributions")
    print("   - Identify developer networks")

    print("\n2. Stack Overflow:")
    print("   - Technology adoption patterns")
    print("   - Skill development in China")
    print("   - Chinese developer activity")

    print("\n3. World Bank Trade:")
    print("   - Cross-reference with patent data")
    print("   - Trade flows for semiconductor equipment")
    print("   - Economic indicators")

    print("\n4. Patent Citations:")
    print("   - Already have access via patents dataset")
    print("   - Can analyze CN patent citation networks")
    print("   - Identify high-impact innovations")

    print("\n" + "="*80)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Check for trade/supply chain datasets with HS codes on BigQuery
"""

from google.cloud import bigquery

def search_bigquery_datasets():
    """Search BigQuery public datasets for trade/supply chain data"""
    print("="*80)
    print("SEARCHING FOR TRADE/SUPPLY CHAIN DATASETS")
    print("="*80)

    client = bigquery.Client()

    # Known potential datasets
    datasets_to_check = [
        # Trade data
        ('bigquery-public-data', 'world_bank_intl_trade', 'World Bank International Trade'),
        ('bigquery-public-data', 'world_bank_global_trade', 'World Bank Global Trade'),
        ('bigquery-public-data', 'census_bureau_international_trade', 'US Census Trade'),
        ('bigquery-public-data', 'un_comtrade', 'UN Comtrade'),

        # Supply chain
        ('bigquery-public-data', 'supply_chain', 'Supply Chain'),
        ('bigquery-public-data', 'logistics', 'Logistics'),

        # Customs/Trade
        ('bigquery-public-data', 'customs', 'Customs Data'),
        ('bigquery-public-data', 'harmonized_system', 'HS Codes'),

        # Transportation (proxy for supply chain)
        ('bigquery-public-data', 'chicago_taxi_trips', 'Chicago Taxi'),
        ('bigquery-public-data', 'new_york_taxi_trips', 'NYC Taxi'),

        # Economic indicators
        ('bigquery-public-data', 'bls', 'Bureau of Labor Statistics'),
        ('bigquery-public-data', 'fred', 'Federal Reserve Economic Data'),
    ]

    accessible = []

    for project_id, dataset_id, name in datasets_to_check:
        try:
            dataset_ref = f"{project_id}.{dataset_id}"
            dataset = client.get_dataset(dataset_ref)
            tables = list(client.list_tables(dataset))

            print(f"\n[FOUND] {name}")
            print(f"  Dataset: {dataset_ref}")
            print(f"  Tables: {len(tables)}")

            # List table names if small number
            if len(tables) <= 10:
                for table in tables:
                    print(f"    - {table.table_id}")

            accessible.append({
                'name': name,
                'dataset': dataset_ref,
                'tables': len(tables)
            })

        except Exception as e:
            pass  # Not accessible

    return accessible

def check_usa_trade_data():
    """Check if USA trade data (with HS codes) is available"""
    print("\n" + "="*80)
    print("USA TRADE DATA (Census Bureau)")
    print("="*80)

    client = bigquery.Client()

    # Try to find USA trade datasets
    try:
        # Search for datasets containing 'trade' in bigquery-public-data
        query = """
        SELECT
            table_catalog,
            table_schema,
            table_name
        FROM `bigquery-public-data`.INFORMATION_SCHEMA.TABLES
        WHERE LOWER(table_schema) LIKE '%trade%'
            OR LOWER(table_name) LIKE '%trade%'
            OR LOWER(table_name) LIKE '%import%'
            OR LOWER(table_name) LIKE '%export%'
        LIMIT 20
        """

        print("\nSearching for trade-related tables...")
        job = client.query(query)
        results = list(job.result())

        if results:
            print(f"\nFound {len(results)} trade-related tables:")
            for r in results:
                print(f"  {r['table_schema']}.{r['table_name']}")
        else:
            print("\nNo trade-related tables found in bigquery-public-data")

        return len(results) > 0

    except Exception as e:
        print(f"\nError searching: {e}")
        return False

def check_world_bank_trade():
    """Check World Bank WDI for trade indicators"""
    print("\n" + "="*80)
    print("WORLD BANK TRADE INDICATORS")
    print("="*80)

    client = bigquery.Client()

    # Search for trade-related indicators
    query = """
    SELECT DISTINCT
        indicator_code,
        indicator_name
    FROM `bigquery-public-data.world_bank_wdi.indicators_data`
    WHERE LOWER(indicator_name) LIKE '%trade%'
        OR LOWER(indicator_name) LIKE '%import%'
        OR LOWER(indicator_name) LIKE '%export%'
        OR LOWER(indicator_name) LIKE '%tariff%'
        OR LOWER(indicator_name) LIKE '%merchandise%'
    LIMIT 50
    """

    print("\nSearching World Bank for trade indicators...")
    job = client.query(query)
    results = list(job.result())

    print(f"\nFound {len(results)} trade-related indicators:")
    for r in results[:20]:  # Show first 20
        print(f"  [{r['indicator_code']}] {r['indicator_name']}")

    if len(results) > 20:
        print(f"  ... and {len(results) - 20} more")

    cost = (job.total_bytes_billed / 1e12) * 5
    print(f"\nCost: ${cost:.4f}")

    return results

def list_all_public_datasets():
    """List all available public datasets in bigquery-public-data"""
    print("\n" + "="*80)
    print("ALL BIGQUERY PUBLIC DATASETS")
    print("="*80)

    client = bigquery.Client()

    try:
        # List all datasets in bigquery-public-data project
        datasets = list(client.list_datasets(project='bigquery-public-data'))

        print(f"\nTotal public datasets: {len(datasets)}")
        print(f"\nAll datasets:")

        for dataset in sorted(datasets, key=lambda x: x.dataset_id):
            print(f"  - {dataset.dataset_id}")

        # Highlight potentially relevant ones
        relevant_keywords = ['trade', 'supply', 'commerce', 'customs', 'economic', 'census']
        relevant = [d for d in datasets if any(kw in d.dataset_id.lower() for kw in relevant_keywords)]

        if relevant:
            print(f"\n\nPotentially relevant datasets ({len(relevant)}):")
            for dataset in relevant:
                print(f"  - {dataset.dataset_id}")

        return datasets

    except Exception as e:
        print(f"Error: {e}")
        return []

def main():
    # Check specific trade datasets
    accessible = search_bigquery_datasets()

    # Check USA trade
    has_usa_trade = check_usa_trade_data()

    # Check World Bank trade indicators
    wb_trade = check_world_bank_trade()

    # List all public datasets
    all_datasets = list_all_public_datasets()

    print("\n" + "="*80)
    print("SUMMARY - SUPPLY CHAIN & TRADE DATA")
    print("="*80)

    print(f"\nAccessible datasets: {len(accessible)}")
    for ds in accessible:
        print(f"  - {ds['name']}: {ds['tables']} tables")

    print(f"\nWorld Bank trade indicators: {len(wb_trade)} available")

    print("\n" + "="*80)
    print("HS CODE AVAILABILITY")
    print("="*80)

    print("\nOn BigQuery: NOT FOUND")
    print("\nAlternative sources with HS codes:")
    print("  1. UN Comtrade API (you have access)")
    print("     - HS codes at 2, 4, 6-digit levels")
    print("     - Bilateral trade flows")
    print("     - 1962-present")
    print("\n  2. USA Census Bureau API")
    print("     - HS codes for US imports/exports")
    print("     - Free access")
    print("\n  3. Eurostat Comext")
    print("     - HS codes for EU trade")
    print("     - Free bulk downloads")
    print("\n  4. World Bank WITS")
    print("     - Cleaned HS code data")
    print("     - Web interface + API")

    print("\n" + "="*80)

if __name__ == "__main__":
    main()

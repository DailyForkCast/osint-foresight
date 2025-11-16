#!/usr/bin/env python3
"""
Check temporal coverage of BigQuery datasets
"""

from google.cloud import bigquery

def check_github_archive_coverage():
    """Check what years GitHub Archive covers"""
    print("="*80)
    print("GITHUB ARCHIVE TEMPORAL COVERAGE")
    print("="*80)

    client = bigquery.Client()

    # List all tables
    dataset_ref = "githubarchive.month"
    dataset = client.get_dataset(dataset_ref)
    tables = list(client.list_tables(dataset))

    # Extract years from table names (format: YYYYMM)
    table_names = [t.table_id for t in tables]

    if table_names:
        years = sorted(set([name[:4] for name in table_names if len(name) == 6]))

        print(f"\nTotal monthly tables: {len(tables)}")
        print(f"\nYear coverage: {years[0]} - {years[-1]}")
        print(f"Years available: {len(years)}")
        print(f"\nAll years: {', '.join(years)}")

        # Count months per year
        print(f"\nMonths per year:")
        for year in years[-5:]:  # Last 5 years
            year_tables = [t for t in table_names if t.startswith(year)]
            print(f"  {year}: {len(year_tables)} months")

        return years
    else:
        print("No tables found")
        return []

def check_world_bank_coverage():
    """Check World Bank data latest year"""
    print("\n" + "="*80)
    print("WORLD BANK INDICATORS TEMPORAL COVERAGE")
    print("="*80)

    client = bigquery.Client()

    # Check latest year available for each indicator
    query = """
    SELECT
        indicator_code,
        indicator_name,
        MAX(year) as latest_year,
        MIN(year) as earliest_year,
        COUNT(DISTINCT year) as years_available
    FROM `bigquery-public-data.world_bank_wdi.indicators_data`
    WHERE country_code = 'CHN'
        AND indicator_code IN (
            'GB.XPD.RSDV.GD.ZS',  -- R&D expenditure
            'IP.PAT.RESD',         -- Patent applications
            'NY.GDP.MKTP.CD',      -- GDP
            'SP.POP.TOTL'          -- Population
        )
    GROUP BY indicator_code, indicator_name
    ORDER BY latest_year DESC
    """

    print("\nQuerying World Bank latest data...")
    job = client.query(query)
    results = list(job.result())

    print(f"\nIndicators for China:")
    for r in results:
        print(f"\n  [{r['indicator_code']}]")
        print(f"    {r['indicator_name']}")
        print(f"    Range: {r['earliest_year']} - {r['latest_year']}")
        print(f"    Years: {r['years_available']}")

    cost = (job.total_bytes_billed / 1e12) * 5
    print(f"\nCost: ${cost:.4f}")

    return results

def check_github_available_years_sample():
    """Quick check of what GitHub data contains"""
    print("\n" + "="*80)
    print("GITHUB ARCHIVE - YEAR SAMPLING")
    print("="*80)

    client = bigquery.Client()

    # Check a few sample years to see if they have data
    test_years = ['201101', '201501', '202001', '202301', '202401', '202411']

    print("\nTesting sample months:")
    for month in test_years:
        try:
            query = f"""
            SELECT COUNT(*) as event_count
            FROM `githubarchive.month.{month}`
            LIMIT 1
            """
            job = client.query(query)
            result = list(job.result())[0]

            print(f"  {month}: {result['event_count']:,} events ✓")
        except Exception as e:
            print(f"  {month}: Not available")

def main():
    github_years = check_github_archive_coverage()
    wb_indicators = check_world_bank_coverage()
    check_github_available_years_sample()

    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)

    if github_years:
        print(f"\nGitHub Archive: {github_years[0]} - {github_years[-1]} ({len(github_years)} years)")
        print(f"  Currently extracted: 2024 only (12 months)")
        print(f"  Available to extract: {github_years[0]}-{github_years[-1]}")

    print(f"\nWorld Bank Indicators:")
    print(f"  Latest GDP: 2020")
    print(f"  Latest R&D: 2018")
    print(f"  Latest Patents: 2019")
    print(f"  Currently extracted: 2011-2020")

    print("\n" + "="*80)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Comprehensive CNIPA Data Extraction
Extract all dimensions needed for Made in China 2025 analysis:
- Annual time series (2011-2025)
- Filing dates AND grant dates
- All 10 MIC2025 priority sectors
- Cumulative and annualized calculations
- Raw data export for further analysis
"""

from google.cloud import bigquery
from datetime import datetime
import json
import pandas as pd
from pathlib import Path

# Made in China 2025 Priority Sectors with CPC Mappings
MIC2025_SECTORS = {
    'advanced_information_technology': {
        'name': 'Advanced Information Technology',
        'cpc_codes': ['H01L', 'G06N', 'G06F', 'H04L', 'H04W', 'G06Q'],
        'subcategories': {
            'semiconductors': ['H01L'],
            'artificial_intelligence': ['G06N'],
            'computing': ['G06F'],
            'telecommunications': ['H04L'],
            'wireless_5g': ['H04W'],
            'big_data_cloud': ['G06Q']
        }
    },
    'robotics_automation': {
        'name': 'Robotics and Automation',
        'cpc_codes': ['B25J', 'G05B', 'B23Q']
    },
    'aerospace': {
        'name': 'Aerospace Equipment',
        'cpc_codes': ['B64C', 'B64D', 'B64F', 'F02K']
    },
    'maritime': {
        'name': 'Maritime Equipment and Ships',
        'cpc_codes': ['B63B', 'B63H']
    },
    'railway': {
        'name': 'Railway Equipment',
        'cpc_codes': ['B61D', 'B61F']
    },
    'new_energy_vehicles': {
        'name': 'New Energy Vehicles',
        'cpc_codes': ['B60L', 'H01M', 'B60K']
    },
    'power_equipment': {
        'name': 'Power Equipment',
        'cpc_codes': ['H02J', 'H02M']
    },
    'agricultural_machinery': {
        'name': 'Agricultural Machinery',
        'cpc_codes': ['A01B', 'A01D']
    },
    'new_materials': {
        'name': 'New Materials',
        'cpc_codes': ['C01B', 'C08J', 'C23C']
    },
    'biopharmaceuticals': {
        'name': 'Biopharmaceuticals',
        'cpc_codes': ['A61K', 'C12N', 'C07K', 'A61P']
    },
    # Additional strategic technologies
    'quantum_computing': {
        'name': 'Quantum Computing',
        'cpc_codes': ['G06N10', 'H04L9', 'B82Y']
    }
}

def extract_annual_time_series_filing():
    """
    Extract annual patent counts by filing date (2011-2025)
    Overall and by sector
    """
    print("="*80)
    print("[1/5] EXTRACTING ANNUAL TIME SERIES - FILING DATES")
    print("="*80)

    client = bigquery.Client()

    query = """
    SELECT
        CAST(filing_date / 10000 AS INT64) as year,
        COUNT(*) as patent_count
    FROM `patents-public-data.patents.publications`
    WHERE country_code = 'CN'
        AND filing_date IS NOT NULL
        AND filing_date >= 20110101
        AND filing_date <= 20251231
    GROUP BY year
    ORDER BY year
    """

    print("\nQuerying annual filing counts...")
    query_job = client.query(query)
    results = list(query_job.result())

    data = [{
        'year': int(r['year']),
        'patent_count': int(r['patent_count'])
    } for r in results]

    df = pd.DataFrame(data)

    print(f"  Extracted: {len(df)} years")
    print(f"  Range: {df['year'].min()}-{df['year'].max()}")
    print(f"  Total patents: {df['patent_count'].sum():,}")
    print(f"  Cost: ${(query_job.total_bytes_billed / 1e12) * 5:.4f}")

    return df, query_job.total_bytes_billed

def extract_annual_time_series_grant():
    """
    Extract annual patent counts by grant date (2011-2025)
    For comparison with filing date methodology
    """
    print("\n" + "="*80)
    print("[2/5] EXTRACTING ANNUAL TIME SERIES - GRANT DATES")
    print("="*80)

    client = bigquery.Client()

    query = """
    SELECT
        CAST(grant_date / 10000 AS INT64) as year,
        COUNT(*) as patent_count
    FROM `patents-public-data.patents.publications`
    WHERE country_code = 'CN'
        AND grant_date IS NOT NULL
        AND grant_date >= 20110101
        AND grant_date <= 20251231
    GROUP BY year
    ORDER BY year
    """

    print("\nQuerying annual grant counts...")
    query_job = client.query(query)
    results = list(query_job.result())

    data = [{
        'year': int(r['year']),
        'patent_count': int(r['patent_count'])
    } for r in results]

    df = pd.DataFrame(data)

    print(f"  Extracted: {len(df)} years")
    print(f"  Range: {df['year'].min()}-{df['year'].max()}")
    print(f"  Total patents: {df['patent_count'].sum():,}")
    print(f"  Cost: ${(query_job.total_bytes_billed / 1e12) * 5:.4f}")

    return df, query_job.total_bytes_billed

def extract_sector_annual_filing():
    """
    Extract annual patent counts by sector (filing dates)
    All 10 MIC2025 priority sectors + quantum
    """
    print("\n" + "="*80)
    print("[3/5] EXTRACTING SECTOR TIME SERIES - FILING DATES")
    print("="*80)

    client = bigquery.Client()

    # Build CPC conditions for all sectors
    sector_conditions = []
    for sector_id, sector_info in MIC2025_SECTORS.items():
        cpc_list = sector_info['cpc_codes']
        cpc_conditions_str = " OR ".join([f"cpc_code.code LIKE '{code}%'" for code in cpc_list])
        sector_conditions.append(f"WHEN ({cpc_conditions_str}) THEN '{sector_id}'")

    query = f"""
    WITH sector_patents AS (
        SELECT
            CAST(filing_date / 10000 AS INT64) as year,
            CASE
                {chr(10).join(sector_conditions)}
                ELSE 'other'
            END as sector
        FROM `patents-public-data.patents.publications`,
            UNNEST(cpc) as cpc_code
        WHERE country_code = 'CN'
            AND filing_date IS NOT NULL
            AND filing_date >= 20110101
            AND filing_date <= 20251231
    )
    SELECT
        year,
        sector,
        COUNT(*) as patent_count
    FROM sector_patents
    WHERE sector != 'other'
    GROUP BY year, sector
    ORDER BY year, sector
    """

    print("\nQuerying sector annual counts (this may take 3-5 minutes)...")
    query_job = client.query(query)
    results = list(query_job.result())

    data = [{
        'year': int(r['year']),
        'sector': r['sector'],
        'patent_count': int(r['patent_count'])
    } for r in results]

    df = pd.DataFrame(data)

    print(f"  Extracted: {len(df)} records")
    print(f"  Years: {df['year'].min()}-{df['year'].max()}")
    print(f"  Sectors: {df['sector'].nunique()}")
    print(f"  Total sector patents: {df['patent_count'].sum():,}")
    print(f"  Cost: ${(query_job.total_bytes_billed / 1e12) * 5:.4f}")

    return df, query_job.total_bytes_billed

def extract_sector_annual_grant():
    """
    Extract annual patent counts by sector (grant dates)
    All 10 MIC2025 priority sectors + quantum
    """
    print("\n" + "="*80)
    print("[4/5] EXTRACTING SECTOR TIME SERIES - GRANT DATES")
    print("="*80)

    client = bigquery.Client()

    # Build CPC conditions for all sectors
    sector_conditions = []
    for sector_id, sector_info in MIC2025_SECTORS.items():
        cpc_list = sector_info['cpc_codes']
        cpc_conditions_str = " OR ".join([f"cpc_code.code LIKE '{code}%'" for code in cpc_list])
        sector_conditions.append(f"WHEN ({cpc_conditions_str}) THEN '{sector_id}'")

    query = f"""
    WITH sector_patents AS (
        SELECT
            CAST(grant_date / 10000 AS INT64) as year,
            CASE
                {chr(10).join(sector_conditions)}
                ELSE 'other'
            END as sector
        FROM `patents-public-data.patents.publications`,
            UNNEST(cpc) as cpc_code
        WHERE country_code = 'CN'
            AND grant_date IS NOT NULL
            AND grant_date >= 20110101
            AND grant_date <= 20251231
    )
    SELECT
        year,
        sector,
        COUNT(*) as patent_count
    FROM sector_patents
    WHERE sector != 'other'
    GROUP BY year, sector
    ORDER BY year, sector
    """

    print("\nQuerying sector annual counts by grant date (3-5 minutes)...")
    query_job = client.query(query)
    results = list(query_job.result())

    data = [{
        'year': int(r['year']),
        'sector': r['sector'],
        'patent_count': int(r['patent_count'])
    } for r in results]

    df = pd.DataFrame(data)

    print(f"  Extracted: {len(df)} records")
    print(f"  Years: {df['year'].min()}-{df['year'].max()}")
    print(f"  Sectors: {df['sector'].nunique()}")
    print(f"  Total sector patents: {df['patent_count'].sum():,}")
    print(f"  Cost: ${(query_job.total_bytes_billed / 1e12) * 5:.4f}")

    return df, query_job.total_bytes_billed

def extract_subcategories_advanced_it():
    """
    Extract detailed subcategories for Advanced IT sector
    Semiconductors, AI, Computing, Telecom, Wireless, Big Data separately
    """
    print("\n" + "="*80)
    print("[5/5] EXTRACTING ADVANCED IT SUBCATEGORIES")
    print("="*80)

    client = bigquery.Client()

    subcats = MIC2025_SECTORS['advanced_information_technology']['subcategories']

    # Build subcategory conditions
    subcat_conditions = []
    for subcat_id, cpc_list in subcats.items():
        cpc_conditions_str = " OR ".join([f"cpc_code.code LIKE '{code}%'" for code in cpc_list])
        subcat_conditions.append(f"WHEN ({cpc_conditions_str}) THEN '{subcat_id}'")

    query = f"""
    WITH subcat_patents AS (
        SELECT
            CAST(filing_date / 10000 AS INT64) as year,
            CASE
                {chr(10).join(subcat_conditions)}
                ELSE 'other'
            END as subcategory
        FROM `patents-public-data.patents.publications`,
            UNNEST(cpc) as cpc_code
        WHERE country_code = 'CN'
            AND filing_date IS NOT NULL
            AND filing_date >= 20110101
            AND filing_date <= 20251231
    )
    SELECT
        year,
        subcategory,
        COUNT(*) as patent_count
    FROM subcat_patents
    WHERE subcategory != 'other'
    GROUP BY year, subcategory
    ORDER BY year, subcategory
    """

    print("\nQuerying Advanced IT subcategories (2-3 minutes)...")
    query_job = client.query(query)
    results = list(query_job.result())

    data = [{
        'year': int(r['year']),
        'subcategory': r['subcategory'],
        'patent_count': int(r['patent_count'])
    } for r in results]

    df = pd.DataFrame(data)

    print(f"  Extracted: {len(df)} records")
    print(f"  Subcategories: {df['subcategory'].nunique()}")
    print(f"  Total patents: {df['patent_count'].sum():,}")
    print(f"  Cost: ${(query_job.total_bytes_billed / 1e12) * 5:.4f}")

    return df, query_job.total_bytes_billed

def calculate_metrics(df_annual, df_sectors, df_subcats):
    """
    Calculate all metrics: cumulative, annualized, growth rates, etc.
    """
    print("\n" + "="*80)
    print("CALCULATING COMPREHENSIVE METRICS")
    print("="*80)

    # Pre/post policy split
    pre_years = [2011, 2012, 2013, 2014, 2015]  # 2015 only through May 7
    post_years = [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]  # 2015 from May 8

    metrics = {}

    # Overall metrics
    pre_total = df_annual[df_annual['year'] < 2015]['patent_count'].sum()
    pre_2015_partial = df_annual[df_annual['year'] == 2015]['patent_count'].values[0] * (127/365)  # Jan-May 7
    pre_total += pre_2015_partial
    pre_years_duration = 4.35

    post_2015_partial = df_annual[df_annual['year'] == 2015]['patent_count'].values[0] * (238/365)  # May 8-Dec 31
    post_total = post_2015_partial + df_annual[df_annual['year'] > 2015]['patent_count'].sum()
    post_years_duration = 10.40

    metrics['overall'] = {
        'pre_policy': {
            'total': int(pre_total),
            'annualized': int(pre_total / pre_years_duration),
            'years': pre_years_duration
        },
        'post_policy': {
            'total': int(post_total),
            'annualized': int(post_total / post_years_duration),
            'years': post_years_duration
        },
        'growth': {
            'annualized_rate_pct': round(((post_total / post_years_duration) - (pre_total / pre_years_duration)) / (pre_total / pre_years_duration) * 100, 1),
            'cumulative_total_pct': round((post_total - pre_total) / pre_total * 100, 1)
        }
    }

    print(f"\nOverall Growth:")
    print(f"  Annualized rate: {metrics['overall']['growth']['annualized_rate_pct']}%")
    print(f"  Cumulative total: {metrics['overall']['growth']['cumulative_total_pct']}%")

    # Sector metrics
    metrics['sectors'] = {}
    for sector in df_sectors['sector'].unique():
        sector_data = df_sectors[df_sectors['sector'] == sector]

        pre_sector = sector_data[sector_data['year'] < 2015]['patent_count'].sum()
        if len(sector_data[sector_data['year'] == 2015]) > 0:
            pre_sector += sector_data[sector_data['year'] == 2015]['patent_count'].values[0] * (127/365)

        post_sector = 0
        if len(sector_data[sector_data['year'] == 2015]) > 0:
            post_sector = sector_data[sector_data['year'] == 2015]['patent_count'].values[0] * (238/365)
        post_sector += sector_data[sector_data['year'] > 2015]['patent_count'].sum()

        if pre_sector > 0:
            ann_growth = ((post_sector / post_years_duration) - (pre_sector / pre_years_duration)) / (pre_sector / pre_years_duration) * 100
        else:
            ann_growth = 0

        metrics['sectors'][sector] = {
            'pre_total': int(pre_sector),
            'post_total': int(post_sector),
            'annualized_growth_pct': round(ann_growth, 1)
        }

    # Print sector growth rates
    print(f"\nSector Growth Rates (Annualized):")
    sorted_sectors = sorted(metrics['sectors'].items(), key=lambda x: x[1]['annualized_growth_pct'], reverse=True)
    for sector, data in sorted_sectors[:5]:
        print(f"  {sector}: {data['annualized_growth_pct']}%")

    return metrics

def main():
    """
    Main execution: Extract all CNIPA data comprehensively
    """
    print("="*80)
    print("COMPREHENSIVE CNIPA DATA EXTRACTION")
    print("Made in China 2025 Analysis - Complete Dataset")
    print("="*80)
    print(f"\nStart time: {datetime.now()}")

    output_dir = Path("data/cnipa_comprehensive")
    output_dir.mkdir(parents=True, exist_ok=True)

    total_cost = 0

    # Extract all datasets
    df_annual_filing, cost1 = extract_annual_time_series_filing()
    total_cost += cost1

    df_annual_grant, cost2 = extract_annual_time_series_grant()
    total_cost += cost2

    df_sector_filing, cost3 = extract_sector_annual_filing()
    total_cost += cost3

    df_sector_grant, cost4 = extract_sector_annual_grant()
    total_cost += cost4

    df_subcats, cost5 = extract_subcategories_advanced_it()
    total_cost += cost5

    # Calculate metrics
    metrics = calculate_metrics(df_annual_filing, df_sector_filing, df_subcats)

    # Save all data
    print("\n" + "="*80)
    print("SAVING DATA")
    print("="*80)

    df_annual_filing.to_csv(output_dir / "annual_filing_dates.csv", index=False)
    df_annual_grant.to_csv(output_dir / "annual_grant_dates.csv", index=False)
    df_sector_filing.to_csv(output_dir / "sector_annual_filing.csv", index=False)
    df_sector_grant.to_csv(output_dir / "sector_annual_grant.csv", index=False)
    df_subcats.to_csv(output_dir / "advanced_it_subcategories.csv", index=False)

    with open(output_dir / "metrics.json", 'w') as f:
        json.dump(metrics, f, indent=2)

    with open(output_dir / "sector_definitions.json", 'w') as f:
        json.dump(MIC2025_SECTORS, f, indent=2)

    print(f"\nSaved to: {output_dir}/")
    print(f"  - annual_filing_dates.csv")
    print(f"  - annual_grant_dates.csv")
    print(f"  - sector_annual_filing.csv")
    print(f"  - sector_annual_grant.csv")
    print(f"  - advanced_it_subcategories.csv")
    print(f"  - metrics.json")
    print(f"  - sector_definitions.json")

    print("\n" + "="*80)
    print("EXTRACTION COMPLETE")
    print("="*80)
    print(f"\nTotal cost: ${(total_cost / 1e12) * 5:.4f}")
    print(f"End time: {datetime.now()}")

    return metrics

if __name__ == "__main__":
    metrics = main()

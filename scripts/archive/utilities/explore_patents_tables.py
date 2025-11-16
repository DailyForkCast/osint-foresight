#!/usr/bin/env python3
"""
Explore all tables in patents-public-data.patents
"""

from google.cloud import bigquery

def explore_all_patent_tables():
    client = bigquery.Client()

    dataset_ref = "patents-public-data.patents"
    dataset = client.get_dataset(dataset_ref)
    tables = list(client.list_tables(dataset))

    print("="*80)
    print("PATENTS DATASET - ALL TABLES")
    print("="*80)

    table_info = []

    for table in tables:
        table_ref = client.get_table(f"{dataset_ref}.{table.table_id}")

        info = {
            'name': table.table_id,
            'rows': table_ref.num_rows,
            'size_gb': table_ref.num_bytes / 1e9,
            'fields': [f.name for f in table_ref.schema]
        }

        table_info.append(info)

        # Print summary
        print(f"\n[{table.table_id}]")
        print(f"  Rows: {table_ref.num_rows:,}")
        print(f"  Size: {table_ref.num_bytes / 1e9:.2f} GB")

        # Show schema for non-publication tables (smaller, more interesting)
        if 'publication' not in table.table_id.lower():
            print(f"  Fields ({len(table_ref.schema)}):")
            for field in table_ref.schema[:20]:
                print(f"    - {field.name} ({field.field_type})")
                if field.field_type == 'RECORD':
                    for subfield in field.fields[:3]:
                        print(f"      └─ {subfield.name} ({subfield.field_type})")

    return table_info

def test_useful_queries():
    """
    Test queries on non-publication tables
    """
    print("\n" + "="*80)
    print("TESTING USEFUL PATENT QUERIES")
    print("="*80)

    client = bigquery.Client()

    # Test 1: Check assignees table
    print("\n[1] Testing assignees table...")
    query1 = """
    SELECT
        assignee_harmonized,
        COUNT(*) as patent_count
    FROM `patents-public-data.patents.publications`,
        UNNEST(assignee_harmonized) as assignee_harmonized
    WHERE country_code = 'CN'
        AND filing_date >= 20150101
        AND filing_date < 20150102
    GROUP BY assignee_harmonized.name
    ORDER BY patent_count DESC
    LIMIT 5
    """

    try:
        job1 = client.query(query1)
        results1 = list(job1.result())

        print(f"  SUCCESS - Top Chinese assignees (2015-01-01):")
        for r in results1:
            print(f"    {r['assignee_harmonized']['name']}: {r['patent_count']} patents")
        print(f"  Cost: ${(job1.total_bytes_billed / 1e12) * 5:.4f}")
    except Exception as e:
        print(f"  Error: {e}")

    # Test 2: Check citations
    print("\n[2] Testing citations...")
    query2 = """
    SELECT
        COUNT(DISTINCT publication_number) as patents_with_citations,
        COUNT(*) as total_citations
    FROM `patents-public-data.patents.publications`,
        UNNEST(citation) as citation
    WHERE country_code = 'CN'
        AND filing_date >= 20150101
        AND filing_date < 20150201
    LIMIT 1
    """

    try:
        job2 = client.query(query2)
        results2 = list(job2.result())

        r = results2[0]
        print(f"  SUCCESS - Citations (Jan 2015):")
        print(f"    Patents with citations: {r['patents_with_citations']:,}")
        print(f"    Total citation records: {r['total_citations']:,}")
        print(f"  Cost: ${(job2.total_bytes_billed / 1e12) * 5:.4f}")
    except Exception as e:
        print(f"  Error: {e}")

    # Test 3: Inventors
    print("\n[3] Testing inventors...")
    query3 = """
    SELECT
        COUNT(DISTINCT publication_number) as patents,
        COUNT(DISTINCT inventor.name) as unique_inventors
    FROM `patents-public-data.patents.publications`,
        UNNEST(inventor_harmonized) as inventor
    WHERE country_code = 'CN'
        AND filing_date >= 20150101
        AND filing_date < 20150201
    LIMIT 1
    """

    try:
        job3 = client.query(query3)
        results3 = list(job3.result())

        r = results3[0]
        print(f"  SUCCESS - Inventors (Jan 2015):")
        print(f"    Patents: {r['patents']:,}")
        print(f"    Unique inventors: {r['unique_inventors']:,}")
        print(f"  Cost: ${(job3.total_bytes_billed / 1e12) * 5:.4f}")
    except Exception as e:
        print(f"  Error: {e}")

def main():
    tables = explore_all_patent_tables()
    test_useful_queries()

    print("\n" + "="*80)
    print("AVAILABLE DATA WITHIN PATENTS DATASET")
    print("="*80)

    print("\n✓ Publications - Basic patent data (country, dates, CPC)")
    print("✓ Assignees - Patent owners (companies, universities, individuals)")
    print("✓ Inventors - Individual inventors")
    print("✓ Citations - Patent citation networks (who cites whom)")
    print("✓ CPC Classifications - Technology categorization")
    print("✓ Families - Patent families (same invention, multiple jurisdictions)")
    print("✓ Abstracts/Claims - Full text analysis possible")

    print("\n" + "="*80)
    print("HIGH-VALUE ANALYSES POSSIBLE")
    print("="*80)

    print("\n1. ASSIGNEE ANALYSIS")
    print("   - Huawei, ZTE, Xiaomi patent portfolios")
    print("   - Chinese universities (Tsinghua, Peking, etc.)")
    print("   - State-owned enterprises")
    print("   - Track ownership changes over time")

    print("\n2. CITATION NETWORK ANALYSIS")
    print("   - Which Chinese patents are highly cited?")
    print("   - Do Chinese patents cite US/EU patents?")
    print("   - Cross-border technology transfer")
    print("   - Innovation quality vs quantity")

    print("\n3. INVENTOR NETWORKS")
    print("   - Co-invention patterns")
    print("   - University-industry collaboration")
    print("   - International co-inventors (tech transfer)")
    print("   - Mobility of inventors between companies")

    print("\n4. PATENT FAMILIES")
    print("   - Which Chinese inventions filed globally?")
    print("   - Strategic vs domestic-only patents")
    print("   - Geographic filing strategies")

    print("\n" + "="*80)

if __name__ == "__main__":
    main()

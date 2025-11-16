#!/usr/bin/env python3
"""
Patent Coverage Expansion - From 4 to 81 Countries
Uses Google BigQuery patents-public-data (FREE tier)
Expands China collaboration patent collection to all target countries
"""

import json
import sys
import io
from pathlib import Path
from datetime import datetime
from google.cloud import bigquery

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Target countries (81 total)
COUNTRIES = {
    # EU27
    "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR",
    "DE", "GR", "HU", "IE", "IT", "LV", "LT", "LU", "MT", "NL",
    "PL", "PT", "RO", "SK", "SI", "ES", "SE",
    # UK + EFTA
    "GB", "NO", "CH", "IS", "LI",
    # Balkans
    "AL", "BA", "XK", "ME", "MK", "RS",
    # Caucasus
    "AM", "AZ", "GE",
    # Turkey
    "TR",
    # Strategic Partners (already in original 4)
    "US", "CA", "AU", "NZ", "JP", "KR", "SG", "IL", "IN",
    # Additional strategic
    "TW", "MY", "TH", "VN", "PH", "ID",
    # Middle East
    "AE", "SA", "QA", "KW", "BH", "OM",
    # Africa (select)
    "ZA", "EG", "KE", "NG",
    # Latin America
    "BR", "MX", "CL", "AR", "CO",
    # Central Asia
    "KZ", "UZ",
    # Other
    "RU", "UA", "BY", "MD", "FO", "GL"
}

# Technology categories
TECH_CATEGORIES = {
    "artificial_intelligence": ["G06N", "G06F15/18", "G06F15/76"],
    "semiconductors": ["H01L21", "H01L23", "H01L27", "H01L29"],
    "quantum_computing": ["G06N10", "H01L39"],
    "telecommunications": ["H04L", "H04W", "H04B"],
    "nuclear": ["G21", "G01T"],
    "aerospace": ["B64", "B63"],
    "biotechnology": ["C12N", "C12Q", "C07K"],
    "advanced_materials": ["C01B", "C04B", "C08"],
    "energy_storage": ["H01M", "H01G"],
    "cybersecurity": ["H04L9", "G06F21"]
}

def create_bigquery_client():
    """Initialize BigQuery client"""
    try:
        client = bigquery.Client()
        print(f"✅ BigQuery client initialized (Project: {client.project})")
        return client
    except Exception as e:
        print(f"❌ ERROR: Could not initialize BigQuery client: {e}")
        print("   Make sure you have run: gcloud auth application-default login")
        sys.exit(1)

def build_patent_query(country_code, tech_category=None):
    """
    Build BigQuery SQL for China collaboration patents

    CORRECTED: Uses proper UNNEST on assignee_harmonized ARRAY<STRUCT>
    Finds patents where:
    - At least one assignee/inventor from target country
    - At least one assignee/inventor from China/HK/MO
    - Published 2015-2025 (10-year window)
    """

    query = f"""
    SELECT
        p.publication_number,
        p.family_id,
        -- Extract title text from ARRAY<STRUCT<text STRING, language STRING>>
        (
            SELECT t.text
            FROM UNNEST(p.title_localized) AS t
            WHERE t.language = 'en'
            LIMIT 1
        ) AS title,
        -- Extract abstract text from ARRAY<STRUCT<text STRING, language STRING>>
        (
            SELECT a.text
            FROM UNNEST(p.abstract_localized) AS a
            WHERE a.language = 'en'
            LIMIT 1
        ) AS abstract,
        p.filing_date,
        p.publication_date,
        p.grant_date,
        -- Aggregate assignees from target country
        (
            SELECT STRING_AGG(DISTINCT asn.name, '; ')
            FROM UNNEST(p.assignee_harmonized) AS asn
            WHERE asn.country_code = '{country_code}'
        ) AS {country_code.lower()}_assignees,
        -- Aggregate China assignees
        (
            SELECT STRING_AGG(DISTINCT asn.name, '; ')
            FROM UNNEST(p.assignee_harmonized) AS asn
            WHERE asn.country_code IN ('CN', 'HK', 'MO')
        ) AS china_assignees,
        -- Aggregate all inventors
        (
            SELECT STRING_AGG(DISTINCT inv.name || ' (' || inv.country_code || ')', '; ')
            FROM UNNEST(p.inventor_harmonized) AS inv
        ) AS inventors,
        -- Get CPC codes as string (cpc is ARRAY<STRUCT<code STRING, ...>>)
        (
            SELECT STRING_AGG(DISTINCT cpc_item.code, '; ')
            FROM UNNEST(p.cpc) AS cpc_item
        ) AS cpc_codes,
        p.country_code AS publication_country
    FROM
        `patents-public-data.patents.publications` AS p
    WHERE
        -- At least one assignee OR inventor from target country
        (
            EXISTS (
                SELECT 1 FROM UNNEST(p.assignee_harmonized) AS a
                WHERE a.country_code = '{country_code}'
            )
            OR EXISTS (
                SELECT 1 FROM UNNEST(p.inventor_harmonized) AS i
                WHERE i.country_code = '{country_code}'
            )
        )
        -- At least one assignee OR inventor from China/HK/Macau
        AND (
            EXISTS (
                SELECT 1 FROM UNNEST(p.assignee_harmonized) AS a
                WHERE a.country_code IN ('CN', 'HK', 'MO')
            )
            OR EXISTS (
                SELECT 1 FROM UNNEST(p.inventor_harmonized) AS i
                WHERE i.country_code IN ('CN', 'HK', 'MO')
            )
        )
        -- Recent publications (2015-2025)
        AND p.publication_date >= 20150101
        AND p.publication_date <= 20251231
    LIMIT 5000
    """

    return query

def process_country(client, country_code, output_dir):
    """Process a single country - all technologies combined"""

    print(f"\n{'=' * 80}")
    print(f"PROCESSING: {country_code}")
    print(f"{'=' * 80}")

    country_output = output_dir / "by_country" / f"{country_code}_china"
    country_output.mkdir(parents=True, exist_ok=True)

    # Query all technologies for this country
    query = build_patent_query(country_code)

    print(f"  Running BigQuery (all technologies)...")
    print(f"  (This may take 1-5 minutes depending on result size)")

    try:
        query_job = client.query(query)
        results = query_job.result()

        patents = []
        for row in results:
            # Get field dynamically based on country_code
            country_assignees_field = f"{country_code.lower()}_assignees"

            patent = {
                "publication_number": row.publication_number,
                "family_id": row.family_id,
                "title": row.title if row.title else "",
                "abstract": row.abstract if row.abstract else "",
                "filing_date": str(row.filing_date) if row.filing_date else "",
                "publication_date": str(row.publication_date) if row.publication_date else "",
                "grant_date": str(row.grant_date) if row.grant_date else "",
                f"{country_code}_assignees": getattr(row, country_assignees_field, ""),
                "china_assignees": row.china_assignees if row.china_assignees else "",
                "inventors": row.inventors if row.inventors else "",
                "cpc_codes": row.cpc_codes if row.cpc_codes else "",
                "publication_country": row.publication_country,
                "technology_category": categorize_patent(row.cpc_codes if row.cpc_codes else ""),
                "verification": f"BigQuery {datetime.now().date()}"
            }
            patents.append(patent)

        patent_count = len(patents)

        # Save patents
        patents_file = country_output / "patents.json"
        with open(patents_file, 'w', encoding='utf-8') as f:
            json.dump(patents, f, indent=2, ensure_ascii=False)

        # Save metadata
        metadata = {
            "country_code": country_code,
            "patent_count": patent_count,
            "query_date": datetime.now().isoformat(),
            "date_range": "2015-2025",
            "query_type": "all_technologies",
            "source": "Google BigQuery patents-public-data"
        }

        metadata_file = country_output / "metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)

        print(f"  ✅ Found {patent_count} China collaboration patents")
        print(f"  💾 Saved to: {patents_file}")

        return patent_count

    except Exception as e:
        print(f"  ❌ ERROR querying {country_code}: {e}")
        return 0

def categorize_patent(cpc_codes_str):
    """Categorize patent based on CPC codes"""
    if not cpc_codes_str:
        return "other"

    cpc_codes = cpc_codes_str.split('; ')

    for category, prefixes in TECH_CATEGORIES.items():
        for prefix in prefixes:
            if any(code.startswith(prefix) for code in cpc_codes):
                return category

    return "other"

def main():
    """Main processing function"""

    print("=" * 80)
    print("PATENT COVERAGE EXPANSION - 81 COUNTRIES")
    print("=" * 80)
    print(f"Target Countries: {len(COUNTRIES)}")
    print(f"Technology Categories: {len(TECH_CATEGORIES)}")
    print(f"Data Source: Google BigQuery patents-public-data (FREE tier)")
    print()

    # Setup output directory
    output_dir = Path("data/processed/patents_expanded_81_countries")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize BigQuery client
    client = create_bigquery_client()

    # Process all countries
    total_patents = 0
    country_results = {}

    for i, country_code in enumerate(sorted(COUNTRIES), start=1):
        print(f"\n[{i}/{len(COUNTRIES)}]")

        patent_count = process_country(client, country_code, output_dir)
        total_patents += patent_count
        country_results[country_code] = patent_count

    # Generate summary
    print("\n" + "=" * 80)
    print("PROCESSING COMPLETE")
    print("=" * 80)
    print(f"Countries Processed: {len(COUNTRIES)}")
    print(f"Total Patents Found: {total_patents:,}")
    print(f"Average per Country: {total_patents / len(COUNTRIES):.1f}")

    # Top countries
    top_countries = sorted(country_results.items(), key=lambda x: x[1], reverse=True)[:10]
    print("\nTop 10 Countries by Patent Count:")
    for country, count in top_countries:
        print(f"  {country}: {count:,}")

    # Save summary
    summary = {
        "processing_date": datetime.now().isoformat(),
        "total_countries": len(COUNTRIES),
        "total_patents": total_patents,
        "average_per_country": total_patents / len(COUNTRIES),
        "countries": country_results,
        "top_10_countries": dict(top_countries),
        "source": "Google BigQuery patents-public-data"
    }

    summary_file = output_dir / "EXPANSION_SUMMARY.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)

    print(f"\n💾 Summary saved to: {summary_file}")
    print("\n✅ EXPANSION COMPLETE")

    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  INTERRUPTED BY USER")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

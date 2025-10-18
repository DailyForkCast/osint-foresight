#!/usr/bin/env python3
"""
OpenAIRE Multi-Country Data Collection Script

Systematically collects research collaboration data from OpenAIRE
for priority EU countries to identify China partnerships.
"""

import os
import sys
import json
import time
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

# Add the collectors directory to Python path
sys.path.append(str(Path(__file__).parent / "collectors"))
from openaire_client import OpenAIREClient

# Priority countries from README
PRIORITY_COUNTRIES = {
    # Tier 1 - Gateway Countries
    'HU': 'Hungary',
    'GR': 'Greece',

    # Tier 2 - BRI & High Penetration
    'IT': 'Italy',
    'PL': 'Poland',
    'PT': 'Portugal',
    'CZ': 'Czech Republic',

    # Tier 3 - Major Economies
    'DE': 'Germany',
    'FR': 'France',
    'ES': 'Spain',

    # Additional BRI countries
    'BG': 'Bulgaria',
    'HR': 'Croatia',
    'EE': 'Estonia',
    'LV': 'Latvia',
    'LT': 'Lithuania',
    'LU': 'Luxembourg',
    'MT': 'Malta',
    'RO': 'Romania',
    'SK': 'Slovakia',
    'SI': 'Slovenia'
}

def main():
    """Execute comprehensive OpenAIRE data collection"""

    print("="*80)
    print("OpenAIRE Multi-Country China Collaboration Analysis")
    print("="*80)
    print(f"Target countries: {len(PRIORITY_COUNTRIES)}")
    print(f"Analysis date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Initialize client
    output_dir = "C:/Projects/OSINT - Foresight/data/processed/openaire_multicountry"
    client = OpenAIREClient(output_dir=output_dir)

    # Results storage
    all_results = {}
    country_overviews = {}
    china_collaborations = {}

    print("Phase 1: Country Research Overviews")
    print("-" * 40)

    # Get overview for each country
    for country_code, country_name in PRIORITY_COUNTRIES.items():
        print(f"Getting overview for {country_name} ({country_code})...")

        try:
            overview = client.get_country_research_overview(country_code)
            country_overviews[country_code] = overview

            total = overview['total_research_products']
            recent = overview['recent_publications']
            print(f"  Total research products: {total:,}")
            print(f"  Recent publications (last year): {recent:,}")

        except Exception as e:
            print(f"  ERROR: {e}")
            country_overviews[country_code] = {
                'error': str(e),
                'country': country_code
            }

        time.sleep(1)  # Be respectful to API

    print("\nPhase 2: China Collaboration Analysis")
    print("-" * 40)

    # Analyze China collaborations for each country
    for country_code, country_name in PRIORITY_COUNTRIES.items():
        print(f"Analyzing {country_name}-China collaborations...")

        try:
            # Get larger sample for collaboration detection
            china_collabs = client.analyze_china_collaborations(
                country=country_code,
                max_results=1000
            )

            if not china_collabs.empty:
                china_collaborations[country_code] = {
                    'total_collaborations': len(china_collabs),
                    'data': china_collabs.to_dict('records'),
                    'years_covered': {
                        'min': int(china_collabs['year'].min()) if not china_collabs['year'].isna().all() else None,
                        'max': int(china_collabs['year'].max()) if not china_collabs['year'].isna().all() else None
                    },
                    'research_types': china_collabs['result_type'].value_counts().to_dict()
                }

                print(f"  Found {len(china_collabs)} collaborations")

                # Show temporal distribution
                if not china_collabs['year'].isna().all():
                    years = china_collabs['year'].value_counts().sort_index()
                    print(f"  Years: {china_collabs['year'].min():.0f}-{china_collabs['year'].max():.0f}")

                # Show research types
                types = china_collabs['result_type'].value_counts()
                if len(types) > 0:
                    print(f"  Top type: {types.index[0]} ({types.iloc[0]} items)")

            else:
                china_collaborations[country_code] = {
                    'total_collaborations': 0,
                    'data': [],
                    'message': 'No China collaborations detected in sample'
                }
                print(f"  No China collaborations found in sample")

        except Exception as e:
            print(f"  ERROR: {e}")
            china_collaborations[country_code] = {
                'error': str(e),
                'country': country_code
            }

        time.sleep(2)  # Longer pause between countries

    print("\nPhase 3: Data Consolidation and Analysis")
    print("-" * 40)

    # Consolidate results
    analysis_results = {
        'metadata': {
            'analysis_date': datetime.now().isoformat(),
            'countries_analyzed': len(PRIORITY_COUNTRIES),
            'data_source': 'OpenAIRE Graph API',
            'collection_method': 'Multi-country systematic sampling'
        },
        'country_overviews': country_overviews,
        'china_collaborations': china_collaborations
    }

    # Calculate summary statistics
    total_research_products = 0
    total_recent_publications = 0
    total_china_collaborations = 0
    countries_with_collaborations = 0

    for country_code in PRIORITY_COUNTRIES:
        # Overview stats
        if country_code in country_overviews and 'total_research_products' in country_overviews[country_code]:
            total_research_products += country_overviews[country_code]['total_research_products']
            total_recent_publications += country_overviews[country_code]['recent_publications']

        # Collaboration stats
        if country_code in china_collaborations and 'total_collaborations' in china_collaborations[country_code]:
            collabs = china_collaborations[country_code]['total_collaborations']
            total_china_collaborations += collabs
            if collabs > 0:
                countries_with_collaborations += 1

    # Add summary to results
    analysis_results['summary'] = {
        'total_research_products': total_research_products,
        'total_recent_publications': total_recent_publications,
        'total_china_collaborations': total_china_collaborations,
        'countries_with_collaborations': countries_with_collaborations,
        'countries_analyzed': len(PRIORITY_COUNTRIES)
    }

    print("SUMMARY RESULTS:")
    print(f"  Countries analyzed: {len(PRIORITY_COUNTRIES)}")
    print(f"  Total research products: {total_research_products:,}")
    print(f"  Recent publications (last year): {total_recent_publications:,}")
    print(f"  Total China collaborations found: {total_china_collaborations:,}")
    print(f"  Countries with China collaborations: {countries_with_collaborations}")

    # Save comprehensive results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Save JSON
    json_file = Path(output_dir) / f"openaire_multicountry_analysis_{timestamp}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(analysis_results, f, indent=2, ensure_ascii=False, default=str)

    print(f"\nResults saved to: {json_file}")

    # Create summary report
    report_file = Path(output_dir) / f"OPENAIRE_MULTICOUNTRY_ANALYSIS_{timestamp}.md"

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# OpenAIRE Multi-Country Analysis Results\n")
        f.write(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Data Source:** OpenAIRE Graph API\n")
        f.write(f"**Countries:** {len(PRIORITY_COUNTRIES)} EU priority countries\n\n")

        f.write("## Executive Summary\n\n")
        f.write(f"- **Countries analyzed:** {len(PRIORITY_COUNTRIES)}\n")
        f.write(f"- **Total research products:** {total_research_products:,}\n")
        f.write(f"- **Recent publications:** {total_recent_publications:,}\n")
        f.write(f"- **China collaborations found:** {total_china_collaborations:,}\n")
        f.write(f"- **Countries with collaborations:** {countries_with_collaborations}\n\n")

        f.write("## Country Research Overview\n\n")
        f.write("| Country | Code | Total Products | Recent Publications |\n")
        f.write("|---------|------|----------------|--------------------|\n")

        for country_code, country_name in PRIORITY_COUNTRIES.items():
            if country_code in country_overviews and 'total_research_products' in country_overviews[country_code]:
                overview = country_overviews[country_code]
                f.write(f"| {country_name} | {country_code} | {overview['total_research_products']:,} | {overview['recent_publications']:,} |\n")
            else:
                f.write(f"| {country_name} | {country_code} | ERROR | ERROR |\n")

        f.write("\n## China Collaboration Analysis\n\n")
        f.write("| Country | Code | Collaborations Found | Sample Size |\n")
        f.write("|---------|------|---------------------|-------------|\n")

        for country_code, country_name in PRIORITY_COUNTRIES.items():
            if country_code in china_collaborations and 'total_collaborations' in china_collaborations[country_code]:
                collabs = china_collaborations[country_code]['total_collaborations']
                f.write(f"| {country_name} | {country_code} | {collabs} | 1,000 |\n")
            else:
                f.write(f"| {country_name} | {country_code} | ERROR | 1,000 |\n")

        f.write(f"\n## Zero Fabrication Compliance\n\n")
        f.write("All numbers are actual counts from OpenAIRE API responses. ")
        f.write("Sample sizes limited to 1,000 research products per country due to API constraints. ")
        f.write("No projections or estimates included.\n\n")

        f.write(f"---\n\n")
        f.write(f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} from OpenAIRE Graph API*\n")

    print(f"Summary report saved to: {report_file}")
    print("\n" + "="*80)
    print("OpenAIRE multi-country analysis completed!")
    print("="*80)

if __name__ == "__main__":
    main()

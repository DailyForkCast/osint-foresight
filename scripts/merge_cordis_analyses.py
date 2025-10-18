#!/usr/bin/env python3
"""
Merge CORDIS analyses - combining Greece data with multi-country results
Creates comprehensive unified dataset with all 66 countries
"""

import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

def load_latest_file(pattern, directory):
    """Load the most recent file matching pattern"""
    files = list(directory.glob(pattern))
    if not files:
        return None
    latest = max(files, key=lambda x: x.stat().st_mtime)
    with open(latest, 'r', encoding='utf-8') as f:
        return json.load(f)

def merge_analyses():
    """Merge Greece-specific data with multi-country analysis"""

    # Load multi-country analysis
    multicountry_dir = Path("data/processed/cordis_multicountry")
    multicountry_data = load_latest_file("cordis_china_collaborations_*.json", multicountry_dir)

    if not multicountry_data:
        print("Error: No multi-country analysis found")
        return

    # Load Greece/Albania/Kosovo analysis
    specific_dir = Path("data/processed/cordis_specific_countries")
    specific_data = load_latest_file("greece_albania_kosovo_analysis_*.json", specific_dir)

    if not specific_data:
        print("Error: No Greece/Albania/Kosovo analysis found")
        return

    print("Loaded data files successfully")
    print(f"Multi-country: {len(multicountry_data['countries'])} countries")
    print(f"Greece analysis: {len(specific_data['countries'])} countries")

    # Extract Greece data
    greece_data = specific_data['countries'].get('GR', {})

    if not greece_data:
        print("Error: No Greece data found in specific analysis")
        return

    print(f"\nGreece statistics:")
    print(f"  Total projects: {greece_data['total_projects']}")
    print(f"  China collaborations: {greece_data['china_collaborations']}")

    # Update or add Greece to multi-country data
    if 'GR' in multicountry_data['countries']:
        print("\nUpdating existing Greece entry...")
        old_collab = multicountry_data['countries']['GR']['china_collaborations']
        print(f"  Old China collaborations: {old_collab}")
    else:
        print("\nAdding Greece as new entry...")
        old_collab = 0

    # Replace/add Greece data
    # Ensure country_name is present
    if 'country_name' not in greece_data:
        greece_data['country_name'] = 'Greece'
    multicountry_data['countries']['GR'] = greece_data

    # Update metadata
    multicountry_data['metadata']['updated'] = datetime.now().strftime('%Y%m%d_%H%M%S')
    multicountry_data['metadata']['greece_corrected'] = True
    multicountry_data['metadata']['total_countries_with_china'] = sum(
        1 for c in multicountry_data['countries'].values()
        if c.get('china_collaborations', 0) > 0
    )

    # Recalculate total unique China projects
    all_china_projects = set()
    for country_data in multicountry_data['countries'].values():
        if 'sample_projects' in country_data:
            for proj in country_data['sample_projects']:
                if 'id' in proj:
                    all_china_projects.add(proj['id'])

    # Add Greece's full project list if available
    if 'china_projects' in greece_data:
        for proj in greece_data['china_projects']:
            if 'id' in proj:
                all_china_projects.add(proj['id'])

    multicountry_data['metadata']['total_unique_china_projects'] = len(all_china_projects)

    print(f"\nUpdated statistics:")
    print(f"  Total countries with China collaborations: {multicountry_data['metadata']['total_countries_with_china']}")
    print(f"  Total unique China projects: {multicountry_data['metadata']['total_unique_china_projects']}")

    return multicountry_data

def generate_unified_report(data):
    """Generate comprehensive report with all countries including Greece"""

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    report = f"""# CORDIS Multi-Country China Collaboration Analysis (COMPLETE)
Generated: {timestamp}
Data Sources: H2020 and Horizon Europe

## Executive Summary

**CORRECTED ANALYSIS INCLUDING GREECE**

Total unique projects with China: {data['metadata'].get('total_unique_china_projects', 'Unknown')}
Countries analyzed: 70 (excluding China)
Countries with China collaborations: {data['metadata'].get('total_countries_with_china', 'Unknown')}

### Greece Correction Note
Greece was initially missed due to country code issues. Greece uses both 'GR' and 'EL' codes in CORDIS.
After correction: Greece has 104 China collaborations (79 H2020 + 25 Horizon Europe)

## Country Rankings by China Collaborations (UPDATED)

| Rank | Country | China Projects | Total Projects | Collaboration Rate | Unique Chinese Orgs |
|------|---------|---------------|----------------|-------------------|-------------------|
"""

    # Sort countries by China collaborations
    sorted_countries = sorted(
        [(code, country) for code, country in data['countries'].items()],
        key=lambda x: x[1].get('china_collaborations', 0),
        reverse=True
    )

    rank = 1
    for country_code, country_data in sorted_countries:
        if country_data.get('china_collaborations', 0) > 0:
            collab_rate = (
                country_data['china_collaborations'] / country_data['total_projects'] * 100
                if country_data['total_projects'] > 0 else 0
            )

            # Get country name
            country_name = country_data.get('country_name', country_code)

            # Highlight Greece
            if country_code == 'GR':
                report += f"| **{rank}** | **{country_name} ({country_code})** ⚠️ | "
            else:
                report += f"| {rank} | {country_name} ({country_code}) | "

            report += f"{country_data['china_collaborations']} | "
            report += f"{country_data['total_projects']} | "
            report += f"{collab_rate:.2f}% | "
            report += f"{country_data.get('unique_chinese_orgs', 'N/A')} |\n"
            rank += 1

    # Technology areas aggregation
    report += "\n## Aggregated Technology Focus Areas\n\n"
    all_topics = defaultdict(int)
    for country_data in data['countries'].values():
        if 'technology_areas' in country_data:
            for topic, count in country_data['technology_areas'].items():
                all_topics[topic] += count

    report += "| Topic | Total Projects |\n|-------|---------------|\n"
    for topic, count in sorted(all_topics.items(), key=lambda x: x[1], reverse=True)[:30]:
        report += f"| {topic} | {count} |\n"

    # Chinese organizations aggregation
    report += "\n## Top Chinese Partner Organizations (Global)\n\n"
    all_chinese_orgs = defaultdict(int)
    for country_data in data['countries'].values():
        if 'chinese_organizations' in country_data:
            if isinstance(country_data['chinese_organizations'], dict):
                for org, count in country_data['chinese_organizations'].items():
                    all_chinese_orgs[org] += count

    report += "| Organization | Total Collaborations |\n|--------------|--------------------|\n"
    for org, count in sorted(all_chinese_orgs.items(), key=lambda x: x[1], reverse=True)[:30]:
        report += f"| {org} | {count} |\n"

    # Regional analysis
    report += "\n## Regional Analysis\n\n"

    regions = {
        'Western Europe': ['UK', 'FR', 'DE', 'NL', 'BE', 'LU', 'IE'],
        'Southern Europe': ['ES', 'PT', 'IT', 'GR', 'MT', 'CY'],
        'Northern Europe': ['SE', 'DK', 'FI', 'NO', 'IS', 'EE', 'LV', 'LT'],
        'Central/Eastern Europe': ['PL', 'CZ', 'SK', 'HU', 'RO', 'BG', 'HR', 'SI', 'AT', 'CH'],
        'Balkans': ['RS', 'BA', 'ME', 'MK', 'AL', 'XK'],
        'North America': ['US', 'CA'],
        'Asia-Pacific': ['JP', 'KR', 'AU', 'NZ', 'SG', 'IN', 'MY', 'TH', 'VN', 'TW'],
        'Latin America': ['BR', 'MX', 'AR', 'CL'],
        'Africa & Middle East': ['ZA', 'IL', 'SA', 'EG', 'KE', 'NG']
    }

    for region_name, region_codes in regions.items():
        region_total = 0
        region_china = 0
        for code in region_codes:
            if code in data['countries']:
                country_data = data['countries'][code]
                region_total += country_data.get('total_projects', 0)
                region_china += country_data.get('china_collaborations', 0)

        if region_total > 0:
            rate = region_china / region_total * 100
            report += f"### {region_name}\n"
            report += f"- Total projects: {region_total:,}\n"
            report += f"- China collaborations: {region_china}\n"
            report += f"- Collaboration rate: {rate:.2f}%\n\n"

    # Countries with no China collaboration
    no_collab = []
    for code, country_data in data['countries'].items():
        if country_data.get('china_collaborations', 0) == 0:
            country_name = country_data.get('country_name', code)
            no_collab.append(f"{country_name} ({code})")

    if no_collab:
        report += "\n## Countries with No China Collaborations\n\n"
        report += ", ".join(sorted(no_collab))
        report += "\n\n"

    # Data quality note
    report += """
## Data Quality Notes

1. **Greece Correction**: Initially reported as having 0 China collaborations due to country code mismatch (GR vs EL). After correction: 104 collaborations found.
2. **Albania & Kosovo**: Confirmed to have 0 China collaborations after detailed analysis.
3. **United Arab Emirates**: Still showing 0 collaborations - may need similar country code verification.
4. **Project Counting**: Some projects involve multiple EU countries, so sum of country collaborations exceeds unique project count.

## Methodology

- Data source: CORDIS H2020 (2014-2020) and Horizon Europe (2021-2027) databases
- Analysis date: """ + timestamp + """
- Country codes: ISO 3166-1 alpha-2
- China collaborations: Projects with at least one Chinese organization participant
"""

    return report

def save_unified_results(data, report):
    """Save the unified analysis results"""
    output_dir = Path("data/processed/cordis_unified")
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Save comprehensive JSON
    json_file = output_dir / f"cordis_complete_analysis_{timestamp}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # Save report
    report_file = output_dir / f"CORDIS_COMPLETE_ANALYSIS_{timestamp}.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)

    # Create a summary for quick reference
    summary = {
        'timestamp': timestamp,
        'total_countries': len(data['countries']),
        'countries_with_china': data['metadata']['total_countries_with_china'],
        'total_unique_projects': data['metadata']['total_unique_china_projects'],
        'top_5_countries': []
    }

    sorted_countries = sorted(
        [(code, c) for code, c in data['countries'].items()],
        key=lambda x: x[1].get('china_collaborations', 0),
        reverse=True
    )

    for code, country in sorted_countries[:5]:
        summary['top_5_countries'].append({
            'code': code,
            'name': country.get('country_name', code),
            'collaborations': country.get('china_collaborations', 0)
        })

    summary_file = output_dir / f"summary_{timestamp}.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)

    print(f"\nFiles saved:")
    print(f"  - {json_file}")
    print(f"  - {report_file}")
    print(f"  - {summary_file}")

    return json_file, report_file, summary_file

def main():
    print("=" * 60)
    print("CORDIS Analysis Merger - Creating Unified Dataset")
    print("=" * 60)

    # Merge the analyses
    print("\nStep 1: Loading and merging data...")
    merged_data = merge_analyses()

    if not merged_data:
        print("Error: Failed to merge data")
        return

    # Generate comprehensive report
    print("\nStep 2: Generating unified report...")
    report = generate_unified_report(merged_data)

    # Save everything
    print("\nStep 3: Saving unified results...")
    json_file, report_file, summary_file = save_unified_results(merged_data, report)

    print("\n" + "=" * 60)
    print("MERGE COMPLETE")
    print("=" * 60)

    # Print summary
    with open(summary_file, 'r') as f:
        summary = json.load(f)

    print(f"\nFinal Statistics:")
    print(f"  Total countries analyzed: {summary['total_countries']}")
    print(f"  Countries with China collaborations: {summary['countries_with_china']}")
    print(f"  Total unique China projects: {summary['total_unique_projects']}")
    print(f"\nTop 5 Countries:")
    for i, country in enumerate(summary['top_5_countries'], 1):
        print(f"  {i}. {country['name']}: {country['collaborations']} projects")

if __name__ == "__main__":
    main()

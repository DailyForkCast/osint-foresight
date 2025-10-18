"""
Quality Assurance Script for OpenAlex Collaboration Detection
Analyzes why collaboration numbers are unexpectedly low
"""

import json
import gzip
from pathlib import Path
from collections import Counter, defaultdict
import logging

logging.basicConfig(level=logging.INFO)

def analyze_collaboration_detection():
    """Analyze the collaboration detection logic and find issues"""

    base_path = Path("F:/OSINT_Backups/openalex/data")

    # Take a sample file
    sample_file = base_path / "works/updated_date=2024-12-12/part_000.gz"

    if not sample_file.exists():
        # Try another file
        sample_file = base_path / "works/updated_date=2024-12-07/part_000.gz"

    if not sample_file.exists():
        print("Sample file not found, searching for any gz file...")
        gz_files = list(base_path.rglob("*.gz"))
        if gz_files:
            sample_file = gz_files[0]
        else:
            print("No gz files found!")
            return

    print(f"Analyzing: {sample_file}")

    stats = {
        'total_papers': 0,
        'papers_with_countries': 0,
        'papers_with_china': 0,
        'china_only': 0,
        'china_with_any_other': 0,
        'china_with_tracked': 0,
        'multi_country_no_china': 0,
        'sample_china_collabs': []
    }

    country_counts = Counter()
    china_partner_counts = Counter()

    # Countries we're tracking
    tracked_countries = {
        "DE", "FR", "IT", "ES", "NL", "BE", "LU", "SE", "DK", "FI", "NO", "IS",
        "PL", "CZ", "SK", "HU", "RO", "BG", "HR", "SI", "EE", "LV", "LT",
        "GR", "CY", "MT", "PT", "AT", "IE", "CH", "GB", "AL", "MK", "RS", "ME",
        "BA", "TR", "UA", "XK", "GE", "AM", "FO", "GL", "US", "CA", "AU", "NZ",
        "JP", "KR", "SG", "TW", "IN", "TH", "MY", "VN", "IL", "AE", "SA",
        "BR", "MX", "AR", "CL", "ZA", "EG", "KE", "NG", "RU", "BY", "KZ"
    }

    try:
        with gzip.open(sample_file, 'rt', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                if line_num > 5000:  # Analyze first 5000 papers
                    break

                try:
                    paper = json.loads(line.strip())
                    stats['total_papers'] += 1

                    # Extract all countries
                    countries = set()
                    institution_details = []

                    for authorship in paper.get("authorships", []):
                        for inst in authorship.get("institutions", []):
                            country_code = inst.get("country_code", "")
                            if country_code:
                                countries.add(country_code)
                                country_counts[country_code] += 1

                                if "CN" in countries:
                                    institution_details.append({
                                        'country': country_code,
                                        'name': inst.get("display_name", "Unknown"),
                                        'author': authorship.get("author", {}).get("display_name", "Unknown")
                                    })

                    if not countries:
                        continue

                    stats['papers_with_countries'] += 1

                    # China analysis
                    if "CN" in countries:
                        stats['papers_with_china'] += 1

                        if len(countries) == 1:
                            stats['china_only'] += 1
                        else:
                            stats['china_with_any_other'] += 1

                            # Check partners
                            other_countries = countries - {"CN"}
                            for country in other_countries:
                                china_partner_counts[country] += 1

                            # Check if any partner is tracked
                            tracked_partners = other_countries & tracked_countries
                            if tracked_partners:
                                stats['china_with_tracked'] += 1

                            # Save sample
                            if len(stats['sample_china_collabs']) < 5:
                                stats['sample_china_collabs'].append({
                                    'title': paper.get("title", "")[:100],
                                    'year': paper.get("publication_year"),
                                    'countries': list(countries),
                                    'tracked_partners': list(tracked_partners),
                                    'institutions': institution_details[:5]
                                })

                    elif len(countries) > 1:
                        stats['multi_country_no_china'] += 1

                except Exception as e:
                    continue

    except Exception as e:
        print(f"Error reading file: {e}")
        return stats

    # Analysis results
    print("\n" + "="*60)
    print("COLLABORATION DETECTION QUALITY ASSURANCE")
    print("="*60)

    print(f"\nPAPER STATISTICS:")
    print(f"  Total papers analyzed: {stats['total_papers']:,}")
    print(f"  Papers with country data: {stats['papers_with_countries']:,} ({stats['papers_with_countries']/max(stats['total_papers'],1)*100:.1f}%)")

    print(f"\nCHINA PAPERS:")
    print(f"  Total with China: {stats['papers_with_china']:,} ({stats['papers_with_china']/max(stats['total_papers'],1)*100:.1f}%)")
    print(f"  China only (no collab): {stats['china_only']:,}")
    print(f"  China with ANY other country: {stats['china_with_any_other']:,}")
    print(f"  China with TRACKED countries: {stats['china_with_tracked']:,}")

    if stats['china_with_any_other'] > 0:
        print(f"\n  Detection rate: {stats['china_with_tracked']/stats['china_with_any_other']*100:.1f}% of China collabs are with tracked countries")

    print(f"\nTOP 20 COUNTRIES OVERALL:")
    for country, count in country_counts.most_common(20):
        tracked = "✓" if country in tracked_countries else " "
        print(f"  [{tracked}] {country}: {count:,}")

    print(f"\nTOP 20 CHINA PARTNERS:")
    untracked_partners = []
    for country, count in china_partner_counts.most_common(20):
        tracked = "✓" if country in tracked_countries else "✗"
        print(f"  [{tracked}] {country}: {count}")
        if country not in tracked_countries:
            untracked_partners.append(country)

    if untracked_partners:
        print(f"\n⚠️ MISSING COUNTRIES IN TRACKING:")
        print(f"  Not tracking: {', '.join(untracked_partners[:10])}")

    print(f"\nSAMPLE CHINA COLLABORATIONS:")
    for i, collab in enumerate(stats['sample_china_collabs'], 1):
        print(f"\n{i}. {collab['title']}")
        print(f"   Year: {collab['year']}")
        print(f"   Countries: {', '.join(collab['countries'])}")
        if collab['tracked_partners']:
            print(f"   Tracked: {', '.join(collab['tracked_partners'])}")
        else:
            print(f"   ⚠️ NO TRACKED PARTNERS (but has: {', '.join([c for c in collab['countries'] if c != 'CN'])})")

    # Estimate real numbers
    if stats['china_with_any_other'] > 0:
        print(f"\n" + "="*60)
        print("PROJECTION FOR FULL DATASET:")
        print("="*60)

        # Current processing shows 135K China papers out of 15.7M total
        scale_factor = 15700000 / max(stats['total_papers'], 1)

        print(f"  Estimated total China papers: {int(stats['papers_with_china'] * scale_factor):,}")
        print(f"  Estimated China collaborations (ANY country): {int(stats['china_with_any_other'] * scale_factor):,}")
        print(f"  Estimated China collaborations (TRACKED only): {int(stats['china_with_tracked'] * scale_factor):,}")

        print(f"\n⚠️ ISSUE: We're missing {100 - (stats['china_with_tracked']/max(stats['china_with_any_other'],1)*100):.1f}% of collaborations!")
        print(f"  These are with countries not in our tracking list")

    return stats

if __name__ == "__main__":
    stats = analyze_collaboration_detection()

    # Save detailed results
    output_file = Path("C:/Projects/OSINT - Foresight/data/processed/openalex_multicountry_temporal/QA_REPORT.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(stats, f, indent=2)

    print(f"\nDetailed report saved to: {output_file}")

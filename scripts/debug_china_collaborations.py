"""
Debug script to find and analyze China collaborations in OpenAlex data
"""

import json
import gzip
from pathlib import Path
from collections import defaultdict, Counter
import logging

logging.basicConfig(level=logging.INFO)

def find_china_collaborations(max_files=10):
    """Find actual China collaborations in the data"""

    base_path = Path("F:/OSINT_Backups/openalex/data/works")

    # Countries we're tracking
    countries_of_interest = {
        "DE", "FR", "IT", "ES", "NL", "BE", "LU", "SE", "DK", "FI", "NO", "IS",
        "PL", "CZ", "SK", "HU", "RO", "BG", "HR", "SI", "EE", "LV", "LT",
        "GR", "CY", "MT", "PT", "AT", "IE", "CH", "GB", "AL", "MK", "RS", "ME",
        "BA", "TR", "UA", "XK", "GE", "AM", "FO", "GL", "US", "CA", "AU", "NZ",
        "JP", "KR", "SG", "TW", "IN", "TH", "MY", "VN", "IL", "AE", "SA",
        "BR", "MX", "AR", "CL", "ZA", "EG", "KE", "NG", "RU", "BY", "KZ"
    }

    stats = {
        "total_papers": 0,
        "papers_with_institutions": 0,
        "papers_with_countries": 0,
        "papers_with_china": 0,
        "china_solo": 0,
        "china_multi_country": 0,
        "china_tracked_country": 0
    }

    country_counts = Counter()
    china_partners = Counter()
    sample_collaborations = []

    # Process files
    gz_files = list(base_path.rglob("*.gz"))[:max_files]

    for file_idx, gz_file in enumerate(gz_files):
        logging.info(f"Processing file {file_idx + 1}/{len(gz_files)}: {gz_file.name}")

        try:
            with gzip.open(gz_file, 'rt', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    if line_num > 1000:  # Sample 1000 papers per file
                        break

                    try:
                        paper = json.loads(line.strip())
                        stats["total_papers"] += 1

                        # Extract countries
                        countries = set()
                        institutions_by_country = defaultdict(list)

                        authorships = paper.get("authorships", [])
                        has_institutions = False

                        for authorship in authorships:
                            for inst in authorship.get("institutions", []):
                                has_institutions = True
                                country_code = inst.get("country_code", "")
                                if country_code:
                                    countries.add(country_code)
                                    inst_name = inst.get("display_name", "Unknown")
                                    institutions_by_country[country_code].append(inst_name)
                                    country_counts[country_code] += 1

                        if has_institutions:
                            stats["papers_with_institutions"] += 1

                        if countries:
                            stats["papers_with_countries"] += 1

                        # Check China involvement
                        if "CN" in countries:
                            stats["papers_with_china"] += 1

                            if len(countries) == 1:
                                stats["china_solo"] += 1
                            else:
                                stats["china_multi_country"] += 1

                                # Track partners
                                for country in countries:
                                    if country != "CN":
                                        china_partners[country] += 1

                                # Check if any partner is in our tracked countries
                                tracked_partners = [c for c in countries
                                                  if c != "CN" and c in countries_of_interest]

                                if tracked_partners:
                                    stats["china_tracked_country"] += 1

                                    # Save sample
                                    if len(sample_collaborations) < 5:
                                        sample_collaborations.append({
                                            "title": paper.get("title", "")[:100],
                                            "year": paper.get("publication_year"),
                                            "doi": paper.get("doi", ""),
                                            "countries": list(countries),
                                            "tracked_partners": tracked_partners,
                                            "china_institutions": institutions_by_country.get("CN", [])[:3],
                                            "partner_institutions": {
                                                c: institutions_by_country[c][:3]
                                                for c in tracked_partners
                                            },
                                            "source": f"{gz_file.name}:{line_num}"
                                        })

                    except json.JSONDecodeError:
                        continue
                    except Exception as e:
                        if line_num <= 5:  # Only log first few errors
                            logging.debug(f"Error processing paper: {e}")
                        continue

        except Exception as e:
            logging.error(f"Error processing file {gz_file}: {e}")
            continue

    # Print results
    print("\n" + "="*60)
    print("CHINA COLLABORATION ANALYSIS RESULTS")
    print("="*60)

    print(f"\nPapers Analyzed:")
    print(f"  Total papers: {stats['total_papers']:,}")
    print(f"  Papers with institutions: {stats['papers_with_institutions']:,} ({stats['papers_with_institutions']/max(stats['total_papers'],1)*100:.1f}%)")
    print(f"  Papers with country codes: {stats['papers_with_countries']:,} ({stats['papers_with_countries']/max(stats['total_papers'],1)*100:.1f}%)")

    print(f"\nChina Papers:")
    print(f"  Total with China: {stats['papers_with_china']:,} ({stats['papers_with_china']/max(stats['total_papers'],1)*100:.2f}%)")
    print(f"  China only: {stats['china_solo']:,}")
    print(f"  China + other countries: {stats['china_multi_country']:,}")
    print(f"  China + tracked countries: {stats['china_tracked_country']:,}")

    if stats['china_tracked_country'] == 0 and stats['china_multi_country'] > 0:
        print(f"\n⚠️ WARNING: Found {stats['china_multi_country']} multi-country collaborations")
        print(f"  but NONE with our tracked countries!")
        print(f"\n  China's actual partners (not tracked):")
        for country, count in china_partners.most_common(10):
            tracked = "YES" if country in countries_of_interest else "NO"
            print(f"    {country}: {count} papers [{tracked}]")

    print(f"\nTop 30 countries overall:")
    for country, count in country_counts.most_common(30):
        tracked = "YES" if country in countries_of_interest else "NO "
        print(f"  {country}: {count:4d} [{tracked}]")

    if stats['china_multi_country'] > 0:
        print(f"\nTop China collaboration partners:")
        for country, count in china_partners.most_common(20):
            tracked = "YES" if country in countries_of_interest else "NO"
            print(f"  {country}: {count:3d} [{tracked}]")

    if sample_collaborations:
        print(f"\n{'='*60}")
        print(f"SAMPLE CHINA-TRACKED COUNTRY COLLABORATIONS")
        print(f"{'='*60}")
        for i, collab in enumerate(sample_collaborations, 1):
            print(f"\n{i}. {collab['title']}")
            print(f"   Year: {collab['year']}")
            print(f"   Countries: {', '.join(collab['countries'])}")
            print(f"   Tracked partners: {', '.join(collab['tracked_partners'])}")
            print(f"   China institutions: {', '.join(collab['china_institutions'][:2])}")
            for country, insts in collab['partner_institutions'].items():
                print(f"   {country} institutions: {', '.join(insts[:2])}")
            print(f"   Source: {collab['source']}")

    return stats, sample_collaborations

if __name__ == "__main__":
    import sys
    max_files = int(sys.argv[1]) if len(sys.argv) > 1 else 10

    print(f"Analyzing {max_files} OpenAlex files for China collaborations...")
    stats, samples = find_china_collaborations(max_files)

    if stats['china_tracked_country'] == 0:
        print("\n🔍 DIAGNOSIS: No collaborations with tracked countries found.")
        print("   Possible issues:")
        print("   1. Need to process more files")
        print("   2. China collaborations may be with non-tracked countries")
        print("   3. Data might be older or from specific fields")
    else:
        print(f"\n✅ SUCCESS: Found {stats['china_tracked_country']} collaborations with tracked countries!")

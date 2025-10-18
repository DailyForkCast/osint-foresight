"""
Analyze OpenAlex Metadata Coverage
Determines which metadata fields are most commonly available
"""

import json
import gzip
from pathlib import Path
from collections import Counter, defaultdict
import logging

logging.basicConfig(level=logging.INFO)

def analyze_metadata_coverage():
    """Analyze which metadata fields are available across OpenAlex papers"""

    base_path = Path("F:/OSINT_Backups/openalex/data")

    # Find sample files to analyze
    gz_files = list(base_path.rglob("*.gz"))[:5]  # Analyze 5 files

    if not gz_files:
        print("No data files found!")
        return

    stats = {
        'total_papers': 0,
        'field_coverage': defaultdict(int),
        'field_combinations': defaultdict(int),
        'quality_tiers': {
            'complete': 0,  # All key fields
            'high': 0,      # Most fields
            'medium': 0,    # Basic fields
            'low': 0        # Minimal fields
        },
        'samples_by_quality': {
            'complete': [],
            'high': [],
            'medium': [],
            'low': []
        }
    }

    # Key metadata fields to check
    metadata_fields = {
        'id': 'Paper ID',
        'doi': 'DOI',
        'title': 'Title',
        'abstract': 'Abstract',
        'publication_year': 'Year',
        'publication_date': 'Full Date',
        'type': 'Publication Type',
        'language': 'Language',
        'authorships': 'Authors',
        'concepts': 'Concepts/Topics',
        'keywords': 'Keywords',
        'mesh': 'MeSH Terms',
        'referenced_works': 'References',
        'related_works': 'Related Works',
        'cited_by_count': 'Citation Count',
        'is_oa': 'Open Access Status',
        'primary_location': 'Primary Venue',
        'locations': 'All Venues',
        'best_oa_location': 'Best OA Link',
        'sustainable_development_goals': 'SDGs',
        'grants': 'Funding/Grants',
        'apc_list': 'APC Info',
        'apc_paid': 'APC Paid Status',
        'has_fulltext': 'Fulltext Available'
    }

    # Fields specifically for collaboration analysis
    collaboration_fields = {
        'has_authorships': False,
        'has_institutions': False,
        'has_countries': False,
        'has_affiliations': False,
        'has_ror_ids': False,
        'institution_count': 0,
        'country_count': 0,
        'author_count': 0
    }

    print(f"Analyzing {len(gz_files)} files for metadata coverage...")

    for file_idx, gz_file in enumerate(gz_files):
        print(f"\nProcessing file {file_idx+1}: {gz_file.name}")

        try:
            with gzip.open(gz_file, 'rt', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    if line_num > 2000:  # Sample 2000 papers per file
                        break

                    try:
                        paper = json.loads(line.strip())
                        stats['total_papers'] += 1

                        # Check which fields are present
                        present_fields = []
                        for field, name in metadata_fields.items():
                            if field in paper and paper[field]:
                                stats['field_coverage'][name] += 1
                                present_fields.append(name)

                        # Deep dive into collaboration metadata
                        collab_info = collaboration_fields.copy()

                        if 'authorships' in paper and paper['authorships']:
                            collab_info['has_authorships'] = True
                            collab_info['author_count'] = len(paper['authorships'])

                            countries = set()
                            institutions = set()

                            for authorship in paper['authorships']:
                                # Check for institutions
                                if 'institutions' in authorship and authorship['institutions']:
                                    collab_info['has_institutions'] = True

                                    for inst in authorship['institutions']:
                                        if inst:
                                            inst_name = inst.get('display_name', '')
                                            if inst_name:
                                                institutions.add(inst_name)

                                            # Check for country
                                            if 'country_code' in inst and inst['country_code']:
                                                collab_info['has_countries'] = True
                                                countries.add(inst['country_code'])

                                            # Check for ROR ID
                                            if 'ror' in inst and inst['ror']:
                                                collab_info['has_ror_ids'] = True

                                            # Check for raw affiliation
                                            if 'raw_affiliation_string' in authorship:
                                                collab_info['has_affiliations'] = True

                            collab_info['institution_count'] = len(institutions)
                            collab_info['country_count'] = len(countries)

                        # Categorize paper quality
                        if collab_info['has_countries'] and collab_info['country_count'] > 0:
                            quality = 'complete'
                        elif collab_info['has_institutions'] and collab_info['institution_count'] > 0:
                            quality = 'high'
                        elif collab_info['has_authorships'] and collab_info['author_count'] > 0:
                            quality = 'medium'
                        else:
                            quality = 'low'

                        stats['quality_tiers'][quality] += 1

                        # Save sample for each quality tier
                        if len(stats['samples_by_quality'][quality]) < 2:
                            sample = {
                                'title': paper.get('title', '')[:100] if paper.get('title') else 'No title',
                                'year': paper.get('publication_year', 'Unknown'),
                                'type': paper.get('type', 'Unknown'),
                                'authors': collab_info['author_count'],
                                'institutions': collab_info['institution_count'],
                                'countries': collab_info['country_count'],
                                'has_doi': bool(paper.get('doi')),
                                'has_abstract': bool(paper.get('abstract')),
                                'fields_present': len(present_fields)
                            }
                            stats['samples_by_quality'][quality].append(sample)

                    except Exception as e:
                        continue

        except Exception as e:
            print(f"Error processing file: {e}")
            continue

    # Generate report
    print("\n" + "="*60)
    print("OPENALEX METADATA COVERAGE ANALYSIS")
    print("="*60)

    print(f"\nTotal papers analyzed: {stats['total_papers']:,}")

    print("\n## GENERAL METADATA COVERAGE")
    print("-" * 40)
    for field_name, count in sorted(stats['field_coverage'].items(),
                                   key=lambda x: x[1], reverse=True):
        coverage_pct = (count / stats['total_papers']) * 100
        bar = '█' * int(coverage_pct / 5) + '░' * (20 - int(coverage_pct / 5))
        print(f"{field_name:25} {bar} {coverage_pct:5.1f}% ({count:,})")

    print("\n## COLLABORATION METADATA QUALITY TIERS")
    print("-" * 40)
    for tier, count in stats['quality_tiers'].items():
        pct = (count / stats['total_papers']) * 100
        print(f"{tier.upper():10} papers: {count:6,} ({pct:5.1f}%)")

    print("\n## WHAT'S TYPICALLY AVAILABLE")
    print("-" * 40)

    high_coverage = []
    medium_coverage = []
    low_coverage = []

    for field_name, count in stats['field_coverage'].items():
        coverage_pct = (count / stats['total_papers']) * 100
        if coverage_pct > 80:
            high_coverage.append((field_name, coverage_pct))
        elif coverage_pct > 20:
            medium_coverage.append((field_name, coverage_pct))
        else:
            low_coverage.append((field_name, coverage_pct))

    print("\n✅ HIGH COVERAGE (>80%):")
    for field, pct in sorted(high_coverage, key=lambda x: x[1], reverse=True):
        print(f"  • {field}: {pct:.1f}%")

    print("\n⚠️ MEDIUM COVERAGE (20-80%):")
    for field, pct in sorted(medium_coverage, key=lambda x: x[1], reverse=True):
        print(f"  • {field}: {pct:.1f}%")

    print("\n❌ LOW COVERAGE (<20%):")
    for field, pct in sorted(low_coverage, key=lambda x: x[1], reverse=True):
        print(f"  • {field}: {pct:.1f}%")

    print("\n## COLLABORATION ANALYSIS FEASIBILITY")
    print("-" * 40)

    complete_pct = (stats['quality_tiers']['complete'] / stats['total_papers']) * 100
    high_pct = (stats['quality_tiers']['high'] / stats['total_papers']) * 100
    usable_pct = complete_pct + high_pct

    print(f"\n🎯 Papers suitable for country-level collaboration analysis:")
    print(f"   {stats['quality_tiers']['complete']:,} papers ({complete_pct:.1f}%)")

    print(f"\n📊 Papers suitable for institution-level analysis:")
    print(f"   {stats['quality_tiers']['complete'] + stats['quality_tiers']['high']:,} papers ({usable_pct:.1f}%)")

    print(f"\n📝 Papers with only author information:")
    print(f"   {stats['quality_tiers']['medium']:,} papers ({(stats['quality_tiers']['medium']/stats['total_papers'])*100:.1f}%)")

    print("\n## SAMPLE PAPERS BY QUALITY TIER")
    print("-" * 40)

    for tier in ['complete', 'high', 'medium', 'low']:
        if stats['samples_by_quality'][tier]:
            print(f"\n{tier.upper()} QUALITY EXAMPLES:")
            for i, sample in enumerate(stats['samples_by_quality'][tier], 1):
                print(f"\n  {i}. {sample['title']}")
                print(f"     Year: {sample['year']} | Type: {sample['type']}")
                print(f"     Authors: {sample['authors']} | Institutions: {sample['institutions']} | Countries: {sample['countries']}")
                print(f"     Has DOI: {sample['has_doi']} | Has Abstract: {sample['has_abstract']}")
                print(f"     Total fields: {sample['fields_present']}")

    # Save detailed report
    output_file = Path("C:/Projects/OSINT - Foresight/data/processed/openalex_multicountry_temporal/analysis/METADATA_COVERAGE_REPORT.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'total_papers_analyzed': stats['total_papers'],
            'field_coverage': dict(stats['field_coverage']),
            'quality_tiers': stats['quality_tiers'],
            'samples': stats['samples_by_quality'],
            'recommendations': {
                'country_analysis_feasible': f"{complete_pct:.1f}% of papers",
                'institution_analysis_feasible': f"{usable_pct:.1f}% of papers",
                'author_only': f"{(stats['quality_tiers']['medium']/stats['total_papers'])*100:.1f}% of papers"
            }
        }, f, indent=2)

    print(f"\n\nDetailed report saved to: {output_file}")

    return stats

if __name__ == "__main__":
    stats = analyze_metadata_coverage()

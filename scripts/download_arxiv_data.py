"""
Download and analyze arXiv AI publications data from Kaggle
NO FABRICATION - Only report actual data
"""

import json
import os
import sys
import subprocess
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# Force UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# AI-relevant arXiv categories
AI_CATEGORIES = {
    'cs.LG': 'Machine Learning',
    'cs.AI': 'Artificial Intelligence',
    'cs.CV': 'Computer Vision',
    'cs.CL': 'Computation and Language (NLP)',
    'cs.RO': 'Robotics',
    'cs.NE': 'Neural and Evolutionary Computing',
    'cs.MA': 'Multiagent Systems'
}

def download_kaggle_arxiv():
    """Download arXiv dataset from Kaggle"""

    data_dir = Path("C:/Projects/OSINT - Foresight/data/external/arxiv")
    data_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("DOWNLOADING ARXIV DATASET FROM KAGGLE")
    print("=" * 80)
    print(f"Dataset: Cornell-University/arxiv")
    print(f"Size: ~1.6 GB compressed")
    print(f"Destination: {data_dir}")
    print()

    # Change to data directory
    os.chdir(data_dir)

    # Download using Kaggle API
    try:
        result = subprocess.run(
            ['kaggle', 'datasets', 'download', '-d', 'Cornell-University/arxiv'],
            capture_output=True,
            text=True,
            timeout=1800  # 30 minute timeout
        )

        print(result.stdout)
        if result.returncode == 0:
            print("[+] Download successful")

            # Check if zip file exists
            zip_file = data_dir / "arxiv.zip"
            if zip_file.exists():
                print(f"[+]� Downloaded: {zip_file} ({zip_file.stat().st_size / 1e9:.2f} GB)")

                # Extract
                print("\n[+]� Extracting archive...")
                extract_result = subprocess.run(
                    ['unzip', '-o', 'arxiv.zip'],
                    capture_output=True,
                    text=True,
                    timeout=600  # 10 minute timeout
                )

                if extract_result.returncode == 0:
                    print("[+] Extraction successful")

                    # Check for JSON file
                    json_file = data_dir / "arxiv-metadata-oai-snapshot.json"
                    if json_file.exists():
                        print(f"[+]� Metadata file: {json_file} ({json_file.stat().st_size / 1e9:.2f} GB)")
                        return json_file
                    else:
                        print("[+][+]  Metadata file not found after extraction")
                        # List files in directory
                        print("Files in directory:")
                        for f in data_dir.iterdir():
                            print(f"  - {f.name}")
                else:
                    print(f"[+] Extraction failed: {extract_result.stderr}")
        else:
            print(f"[+] Download failed: {result.stderr}")

    except subprocess.TimeoutExpired:
        print("[+] Download timed out (30 minutes exceeded)")
    except Exception as e:
        print(f"[+] Error: {e}")

    return None

def filter_ai_papers(input_file):
    """Filter arXiv data to AI-relevant categories"""

    print("\n" + "=" * 80)
    print("FILTERING AI-RELEVANT PAPERS")
    print("=" * 80)
    print(f"Input: {input_file}")
    print(f"Categories: {', '.join(AI_CATEGORIES.keys())}")
    print()

    ai_papers = []
    category_counts = defaultdict(int)
    total_papers = 0
    year_counts = defaultdict(lambda: defaultdict(int))

    print("Processing papers...")

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                if line_num % 100000 == 0:
                    print(f"  Processed {line_num:,} papers...")

                try:
                    paper = json.loads(line)
                    total_papers += 1

                    # Get categories
                    categories_str = paper.get('categories', '')
                    categories = set(categories_str.split())

                    # Check if any AI category
                    ai_cats = categories & AI_CATEGORIES.keys()

                    if ai_cats:
                        # Extract year from first version
                        year = None
                        if 'versions' in paper and len(paper['versions']) > 0:
                            created = paper['versions'][0].get('created', '')
                            try:
                                # Parse: "Mon, 12 Jun 2017 17:57:34 GMT"
                                date = datetime.strptime(created, "%a, %d %b %Y %H:%M:%S %Z")
                                year = date.year
                            except:
                                pass

                        # Add to results
                        paper['ai_categories'] = list(ai_cats)
                        paper['year'] = year
                        ai_papers.append(paper)

                        # Update stats
                        for cat in ai_cats:
                            category_counts[cat] += 1
                            if year and 2020 <= year <= 2025:
                                year_counts[cat][year] += 1

                except json.JSONDecodeError:
                    continue
                except Exception as e:
                    if line_num < 10:  # Only print first few errors
                        print(f"  Warning: Error processing line {line_num}: {e}")
                    continue

        print(f"\n[+] Processing complete")
        print(f"Total papers in dataset: {total_papers:,}")
        print(f"AI-relevant papers: {len(ai_papers):,} ({len(ai_papers)/total_papers*100:.1f}%)")

        # Print category breakdown
        print("\n" + "-" * 80)
        print("PAPERS PER CATEGORY:")
        print("-" * 80)
        for cat in sorted(AI_CATEGORIES.keys()):
            count = category_counts[cat]
            name = AI_CATEGORIES[cat]
            print(f"{cat:8} ({name:40}): {count:>8,}")

        # Print time series
        print("\n" + "-" * 80)
        print("PUBLICATION TRENDS (2020-2025):")
        print("-" * 80)

        for cat in sorted(AI_CATEGORIES.keys()):
            print(f"\n{cat} - {AI_CATEGORIES[cat]}:")
            years = sorted(year_counts[cat].keys())

            if years:
                for year in years:
                    count = year_counts[cat][year]
                    print(f"  {year}: {count:>6,}")

                # Calculate CAGR if we have enough data
                if len(years) >= 2 and years[0] in [2020, 2021]:
                    start_year = min(years)
                    end_year = max(years)
                    start_count = year_counts[cat][start_year]
                    end_count = year_counts[cat][end_year]
                    years_diff = end_year - start_year

                    if start_count > 0 and years_diff > 0:
                        cagr = ((end_count / start_count) ** (1 / years_diff) - 1) * 100
                        print(f"  CAGR ({start_year}-{end_year}): {cagr:+.1f}%")
            else:
                print("  No data for 2020-2025")

        # Save filtered data
        output_file = Path("C:/Projects/OSINT - Foresight/data/processed/arxiv_ai_papers.json")
        output_file.parent.mkdir(parents=True, exist_ok=True)

        print(f"\n[+]� Saving filtered papers to: {output_file}")

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'metadata': {
                    'source': 'arXiv via Kaggle',
                    'download_date': datetime.now().isoformat(),
                    'total_papers': total_papers,
                    'ai_papers': len(ai_papers),
                    'categories': list(AI_CATEGORIES.keys())
                },
                'category_counts': dict(category_counts),
                'year_counts': {cat: dict(counts) for cat, counts in year_counts.items()},
                'papers': ai_papers[:10000]  # Save first 10,000 for now (full dataset is large)
            }, f, indent=2, ensure_ascii=False)

        print(f"[+] Saved {min(len(ai_papers), 10000):,} papers (first 10,000)")

        # Save summary statistics
        summary_file = Path("C:/Projects/OSINT - Foresight/analysis/ai_tech/arxiv_publication_analysis.json")
        summary_file.parent.mkdir(parents=True, exist_ok=True)

        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump({
                'source': 'arXiv via Kaggle (Cornell-University/arxiv)',
                'analysis_date': datetime.now().isoformat(),
                'dataset_statistics': {
                    'total_papers_in_arxiv': total_papers,
                    'ai_relevant_papers': len(ai_papers),
                    'percentage_ai': round(len(ai_papers) / total_papers * 100, 2)
                },
                'papers_per_category': dict(category_counts),
                'publication_trends_2020_2025': {
                    cat: dict(counts) for cat, counts in year_counts.items()
                },
                'categories_analyzed': AI_CATEGORIES
            }, f, indent=2, ensure_ascii=False)

        print(f"[+] Saved summary to: {summary_file}")

        return ai_papers, category_counts, year_counts

    except FileNotFoundError:
        print(f"[+] File not found: {input_file}")
        return None, None, None
    except Exception as e:
        print(f"[+] Error during filtering: {e}")
        import traceback
        traceback.print_exc()
        return None, None, None

def main():
    """Main execution"""

    print("=" * 80)
    print(" " * 20 + "arXiv AI PUBLICATION ANALYSIS")
    print("=" * 80)
    print()

    # Check if data already exists
    data_dir = Path("C:/Projects/OSINT - Foresight/data/external/arxiv")
    json_file = data_dir / "arxiv-metadata-oai-snapshot.json"

    if json_file.exists():
        print(f"[+] Found existing arXiv data: {json_file}")
        print(f"   Size: {json_file.stat().st_size / 1e9:.2f} GB")
        print()
        user_input = input("Download fresh data? (y/N): ").strip().lower()

        if user_input == 'y':
            json_file = download_kaggle_arxiv()
    else:
        print("[+]� arXiv data not found, downloading...")
        json_file = download_kaggle_arxiv()

    # Filter and analyze
    if json_file and json_file.exists():
        ai_papers, category_counts, year_counts = filter_ai_papers(json_file)

        if ai_papers:
            print("\n" + "=" * 80)
            print("[+] ANALYSIS COMPLETE")
            print("=" * 80)
            print(f"AI-relevant papers identified: {len(ai_papers):,}")
            print(f"Data saved to: C:/Projects/OSINT - Foresight/data/processed/arxiv_ai_papers.json")
            print(f"Summary saved to: C:/Projects/OSINT - Foresight/analysis/ai_tech/arxiv_publication_analysis.json")
    else:
        print("\n[+] Cannot proceed without arXiv data")
        print("Please ensure Kaggle credentials are configured:")
        print("  1. Create Kaggle account: https://www.kaggle.com/")
        print("  2. Go to Account settings > API > Create New API Token")
        print("  3. Save kaggle.json to ~/.kaggle/")

if __name__ == '__main__':
    main()

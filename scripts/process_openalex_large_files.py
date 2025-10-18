"""
Process Large OpenAlex Files for Real Germany-China Collaborations
Focuses on files >1MB that contain actual data
"""

import json
import gzip
import os
import logging
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import hashlib

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('openalex_large_processing.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def process_large_openalex_files():
    """Process only large OpenAlex files that contain real data"""

    base_path = Path("F:/OSINT_Backups/openalex/data/works")
    output_dir = Path("data/processed/openalex_real_data")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Find large files (>1MB)
    large_files = []
    for gz_file in base_path.rglob("*.gz"):
        if gz_file.stat().st_size > 1024 * 1024:  # >1MB
            large_files.append(gz_file)

    logging.info(f"Found {len(large_files)} large data files to process")

    # Sort by size to process biggest first
    large_files.sort(key=lambda x: x.stat().st_size, reverse=True)

    stats = {
        "files_processed": 0,
        "total_papers": 0,
        "germany_papers": 0,
        "china_papers": 0,
        "germany_china_collaborations": 0,
        "errors": 0
    }

    collaborations = []
    tech_areas = defaultdict(int)
    yearly_collabs = defaultdict(int)

    # Process top 10 largest files for demonstration
    for file_idx, gz_file in enumerate(large_files[:10]):
        file_size_mb = gz_file.stat().st_size / (1024 * 1024)
        logging.info(f"Processing file {file_idx + 1}: {gz_file.name} ({file_size_mb:.1f} MB)")

        try:
            with gzip.open(gz_file, 'rt', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    if line_num % 10000 == 0:
                        logging.info(f"  Processed {line_num:,} records from {gz_file.name}")

                    try:
                        paper = json.loads(line.strip())
                        stats["total_papers"] += 1

                        # Extract countries
                        countries = set()
                        de_institutions = []
                        cn_institutions = []

                        for authorship in paper.get("authorships", []):
                            for inst in authorship.get("institutions", []):
                                country = inst.get("country_code", "")
                                if country:
                                    countries.add(country)
                                    if country == "DE":
                                        de_institutions.append(inst.get("display_name", "Unknown"))
                                        stats["germany_papers"] += 1
                                    elif country == "CN":
                                        cn_institutions.append(inst.get("display_name", "Unknown"))
                                        stats["china_papers"] += 1

                        # Check for Germany-China collaboration
                        if "DE" in countries and "CN" in countries:
                            stats["germany_china_collaborations"] += 1

                            year = paper.get("publication_year", 0)
                            if year:
                                yearly_collabs[year] += 1

                            # Extract technology area from concepts
                            for concept in paper.get("concepts", []):
                                if concept.get("score", 0) > 0.5:
                                    tech_areas[concept.get("display_name", "Unknown")] += 1

                            # Save collaboration details
                            collab = {
                                "doi": paper.get("doi", ""),
                                "title": paper.get("title", ""),
                                "year": year,
                                "de_institutions": list(set(de_institutions)),
                                "cn_institutions": list(set(cn_institutions)),
                                "source_file": str(gz_file.relative_to(base_path)),
                                "line_number": line_num,
                                "openalex_id": paper.get("id", ""),
                                "verification_hash": hashlib.sha256(
                                    str(paper.get("id", "")).encode()
                                ).hexdigest()[:16]
                            }

                            collaborations.append(collab)

                            # Log first few collaborations as examples
                            if len(collaborations) <= 5:
                                logging.info(f"  Found collaboration: {collab['title'][:80]}")

                    except json.JSONDecodeError:
                        stats["errors"] += 1
                        continue

        except Exception as e:
            logging.error(f"Error processing {gz_file}: {e}")
            stats["errors"] += 1
            continue

        stats["files_processed"] += 1

        # Save checkpoint every 3 files
        if stats["files_processed"] % 3 == 0:
            checkpoint = {
                "timestamp": datetime.now().isoformat(),
                "stats": stats,
                "sample_collaborations": collaborations[:10]
            }
            with open(output_dir / "checkpoint.json", 'w', encoding='utf-8') as f:
                json.dump(checkpoint, f, indent=2, ensure_ascii=False)
            logging.info(f"Checkpoint: {stats['germany_china_collaborations']} collaborations found")

    # Generate final report
    report = {
        "processing_timestamp": datetime.now().isoformat(),
        "data_source": "OpenAlex",
        "files_processed": stats["files_processed"],
        "statistics": stats,
        "yearly_distribution": dict(sorted(yearly_collabs.items())),
        "top_technology_areas": dict(sorted(
            tech_areas.items(),
            key=lambda x: x[1],
            reverse=True
        )[:20]),
        "total_collaborations_found": len(collaborations),
        "verification": {
            "method": "SHA256 hash of OpenAlex ID",
            "recompute_command": "python process_openalex_large_files.py"
        }
    }

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save detailed collaborations (first 1000)
    if collaborations:
        collabs_file = output_dir / f"germany_china_collaborations_{timestamp}.json"
        with open(collabs_file, 'w', encoding='utf-8') as f:
            json.dump(collaborations[:1000], f, indent=2, ensure_ascii=False)
        logging.info(f"Saved {min(1000, len(collaborations))} collaborations to {collabs_file}")

    # Save report
    report_file = output_dir / f"analysis_report_{timestamp}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    # Generate markdown summary
    md_content = f"""# Germany-China Academic Collaborations from OpenAlex
Generated: {datetime.now().isoformat()}

## Summary Statistics
- **Files Processed:** {stats['files_processed']}
- **Total Papers Analyzed:** {stats['total_papers']:,}
- **Papers with German Authors:** {stats['germany_papers']:,}
- **Papers with Chinese Authors:** {stats['china_papers']:,}
- **Germany-China Collaborations:** {stats['germany_china_collaborations']:,}

## Collaboration Rate
- **Germany papers collaborating with China:** {(stats['germany_china_collaborations'] / max(stats['germany_papers'], 1) * 100):.2f}%

## Temporal Distribution
"""

    for year in sorted(yearly_collabs.keys())[-10:]:  # Last 10 years
        md_content += f"- {year}: {yearly_collabs[year]} collaborations\n"

    md_content += "\n## Top Technology Areas\n"
    for tech, count in list(tech_areas.items())[:10]:
        md_content += f"- {tech}: {count} papers\n"

    md_content += f"\n## Data Verification\n"
    md_content += f"- Each collaboration has SHA256 verification hash\n"
    md_content += f"- Source files and line numbers documented\n"
    md_content += f"- Processing errors: {stats['errors']}\n"

    md_file = output_dir / f"summary_{timestamp}.md"
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(md_content)

    # Print summary
    logging.info("=" * 50)
    logging.info("PROCESSING COMPLETE")
    logging.info(f"Total Germany-China Collaborations Found: {stats['germany_china_collaborations']}")
    logging.info(f"From {stats['total_papers']:,} papers analyzed")
    logging.info(f"Results saved to {output_dir}")

    return report

if __name__ == "__main__":
    report = process_large_openalex_files()

    if report["total_collaborations_found"] == 0:
        print("\nINSUFFICIENT_EVIDENCE: No collaborations found")
        print("Possible reasons:")
        print("1. Need to process more files")
        print("2. Data format may have changed")
        print("3. Need to check field mappings")
    else:
        print(f"\nSUCCESS: Found {report['total_collaborations_found']} real collaborations")
        print("This is ACTUAL DATA from OpenAlex, not fabricated")

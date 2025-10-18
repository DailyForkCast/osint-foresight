"""
Process OpenAlex for Germany-China Technology Collaborations
REAL DATA ONLY - No fabrication
Uses streaming to handle 420GB dataset
"""

import json
import gzip
import os
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Generator
from collections import defaultdict
import hashlib

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('openalex_germany_china.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class GermanyChinaAnalyzer:
    """Analyze real Germany-China collaborations from OpenAlex"""

    def __init__(self, base_path: str = "F:/OSINT_Backups/openalex/data"):
        self.base_path = Path(base_path)
        self.output_dir = Path("data/processed/openalex_germany_china")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize tracking
        self.stats = {
            "total_papers": 0,
            "germany_papers": 0,
            "china_papers": 0,
            "germany_china_collaborations": 0,
            "errors": 0
        }

        # Technology areas to track
        self.critical_tech = {
            "artificial_intelligence": ["artificial intelligence", "machine learning", "deep learning", "neural network"],
            "quantum": ["quantum computing", "quantum communication", "quantum cryptography"],
            "semiconductors": ["semiconductor", "microchip", "integrated circuit"],
            "biotechnology": ["biotechnology", "gene editing", "CRISPR", "synthetic biology"],
            "advanced_materials": ["graphene", "nanomaterial", "metamaterial"],
            "aerospace": ["aerospace", "satellite", "spacecraft", "aviation"]
        }

        self.collaborations = []
        self.tech_overlap = defaultdict(list)

    def process_works_directory(self, limit: int = None) -> Dict:
        """Process all works files in OpenAlex"""
        works_dir = self.base_path / "works"

        if not works_dir.exists():
            return {
                "status": "INSUFFICIENT_EVIDENCE",
                "reason": f"Works directory not found at {works_dir}",
                "needed": "OpenAlex works data files"
            }

        # Find all .gz files
        gz_files = list(works_dir.rglob("*.gz"))
        logging.info(f"Found {len(gz_files)} data files to process")

        if not gz_files:
            return {
                "status": "INSUFFICIENT_EVIDENCE",
                "reason": "No .gz files found in works directory",
                "searched": str(works_dir)
            }

        # Process each file
        for file_idx, gz_file in enumerate(gz_files[:limit] if limit else gz_files):
            logging.info(f"Processing file {file_idx + 1}/{len(gz_files)}: {gz_file.name}")
            self._process_single_file(gz_file)

            # Save checkpoint every 10 files
            if (file_idx + 1) % 10 == 0:
                self._save_checkpoint(file_idx + 1)

        return self._generate_analysis()

    def _process_single_file(self, gz_file: Path):
        """Process a single compressed file"""
        try:
            with gzip.open(gz_file, 'rt', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    if line_num % 1000 == 0 and line_num > 0:
                        logging.debug(f"  Processed {line_num} records from {gz_file.name}")

                    try:
                        paper = json.loads(line.strip())
                        self._analyze_paper(paper, gz_file.name, line_num)
                    except json.JSONDecodeError:
                        self.stats["errors"] += 1
                        continue

        except Exception as e:
            logging.error(f"Error processing {gz_file}: {e}")
            self.stats["errors"] += 1

    def _analyze_paper(self, paper: Dict, source_file: str, line_num: int):
        """Analyze a single paper for Germany-China collaboration"""
        self.stats["total_papers"] += 1

        # Extract country codes from institutions
        countries = set()
        institutions_by_country = defaultdict(list)

        for authorship in paper.get("authorships", []):
            for inst in authorship.get("institutions", []):
                country_code = inst.get("country_code", "")
                if country_code:
                    countries.add(country_code)
                    inst_name = inst.get("display_name", "Unknown")
                    institutions_by_country[country_code].append(inst_name)

        # Check for Germany and/or China involvement
        has_germany = "DE" in countries
        has_china = "CN" in countries

        if has_germany:
            self.stats["germany_papers"] += 1
        if has_china:
            self.stats["china_papers"] += 1

        # Process Germany-China collaboration
        if has_germany and has_china:
            self.stats["germany_china_collaborations"] += 1

            # Extract collaboration details
            collab = {
                "doi": paper.get("doi", ""),
                "title": paper.get("title", ""),
                "year": paper.get("publication_year", 0),
                "german_institutions": list(set(institutions_by_country["DE"])),
                "chinese_institutions": list(set(institutions_by_country["CN"])),
                "source_file": source_file,
                "line_number": line_num,
                "verification_hash": hashlib.sha256(
                    json.dumps(paper.get("id", "")).encode()
                ).hexdigest()[:16]
            }

            # Check for critical technology areas
            title_lower = (paper.get("title", "") or "").lower()
            abstract = (paper.get("abstract", "") or "").lower() if paper.get("abstract") else ""
            full_text = f"{title_lower} {abstract}"

            for tech_area, keywords in self.critical_tech.items():
                if any(keyword in full_text for keyword in keywords):
                    collab["technology_area"] = tech_area
                    self.tech_overlap[tech_area].append({
                        "year": collab["year"],
                        "doi": collab["doi"],
                        "title": collab["title"][:100]
                    })
                    break

            self.collaborations.append(collab)

    def _save_checkpoint(self, files_processed: int):
        """Save processing checkpoint"""
        checkpoint = {
            "timestamp": datetime.now().isoformat(),
            "files_processed": files_processed,
            "stats": self.stats.copy(),
            "collaborations_found": len(self.collaborations)
        }

        checkpoint_file = self.output_dir / "checkpoint.json"
        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(checkpoint, f, indent=2)

        logging.info(f"Checkpoint saved: {files_processed} files, {len(self.collaborations)} collaborations")

    def _generate_analysis(self) -> Dict:
        """Generate final analysis report"""
        # Calculate percentages and trends
        collab_rate = 0
        if self.stats["germany_papers"] > 0:
            collab_rate = (self.stats["germany_china_collaborations"] /
                          self.stats["germany_papers"]) * 100

        # Group by year
        yearly_collabs = defaultdict(int)
        for collab in self.collaborations:
            year = collab.get("year", 0)
            if year > 2010:  # Focus on recent collaborations
                yearly_collabs[year] += 1

        # Top collaborating institutions
        de_inst_count = defaultdict(int)
        cn_inst_count = defaultdict(int)

        for collab in self.collaborations:
            for inst in collab.get("german_institutions", []):
                de_inst_count[inst] += 1
            for inst in collab.get("chinese_institutions", []):
                cn_inst_count[inst] += 1

        analysis = {
            "summary": {
                "total_papers_analyzed": self.stats["total_papers"],
                "germany_papers": self.stats["germany_papers"],
                "china_papers": self.stats["china_papers"],
                "germany_china_collaborations": self.stats["germany_china_collaborations"],
                "collaboration_rate": round(collab_rate, 2),
                "processing_errors": self.stats["errors"]
            },
            "temporal_analysis": {
                "yearly_collaborations": dict(sorted(yearly_collabs.items())),
                "trend": "INCREASING" if self._calculate_trend(yearly_collabs) > 0 else "DECREASING"
            },
            "institutional_analysis": {
                "top_german_institutions": dict(sorted(
                    de_inst_count.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:10]),
                "top_chinese_institutions": dict(sorted(
                    cn_inst_count.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:10])
            },
            "technology_overlap": {
                tech: len(papers) for tech, papers in self.tech_overlap.items()
            },
            "verification": {
                "data_source": "OpenAlex",
                "processing_timestamp": datetime.now().isoformat(),
                "records_with_verification_hash": len(self.collaborations),
                "recompute_command": "python process_openalex_germany_china.py"
            }
        }

        return analysis

    def _calculate_trend(self, yearly_data: Dict[int, int]) -> float:
        """Calculate simple trend (positive or negative)"""
        if len(yearly_data) < 2:
            return 0

        years = sorted(yearly_data.keys())
        if len(years) >= 3:
            recent = sum(yearly_data[y] for y in years[-3:]) / 3
            earlier = sum(yearly_data[y] for y in years[:3]) / 3
            return recent - earlier
        return 0

    def save_results(self):
        """Save all results with verification"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save detailed collaborations
        collabs_file = self.output_dir / f"collaborations_{timestamp}.json"
        with open(collabs_file, 'w', encoding='utf-8') as f:
            json.dump(self.collaborations, f, indent=2, ensure_ascii=False)

        # Save analysis
        analysis = self._generate_analysis()
        analysis_file = self.output_dir / f"analysis_{timestamp}.json"
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)

        # Generate markdown report
        report = self._generate_markdown_report(analysis)
        report_file = self.output_dir / f"report_{timestamp}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)

        logging.info(f"Results saved to {self.output_dir}")
        return analysis_file, collabs_file, report_file

    def _generate_markdown_report(self, analysis: Dict) -> str:
        """Generate human-readable markdown report"""
        report = f"""# Germany-China Academic Collaboration Analysis
Generated: {datetime.now().isoformat()}
Data Source: OpenAlex

## Summary

- **Total Papers Analyzed:** {analysis['summary']['total_papers_analyzed']:,}
- **Papers with German Authors:** {analysis['summary']['germany_papers']:,}
- **Papers with Chinese Authors:** {analysis['summary']['china_papers']:,}
- **Germany-China Collaborations:** {analysis['summary']['germany_china_collaborations']:,}
- **Collaboration Rate:** {analysis['summary']['collaboration_rate']}%

## Temporal Trends

Trend: **{analysis['temporal_analysis']['trend']}**

### Yearly Collaborations
"""
        for year, count in analysis['temporal_analysis']['yearly_collaborations'].items():
            report += f"- {year}: {count} papers\n"

        report += "\n## Top Collaborating Institutions\n\n### German Institutions\n"
        for inst, count in list(analysis['institutional_analysis']['top_german_institutions'].items())[:5]:
            report += f"1. {inst}: {count} collaborations\n"

        report += "\n### Chinese Institutions\n"
        for inst, count in list(analysis['institutional_analysis']['top_chinese_institutions'].items())[:5]:
            report += f"1. {inst}: {count} collaborations\n"

        report += "\n## Technology Areas\n"
        for tech, count in analysis['technology_overlap'].items():
            report += f"- **{tech.replace('_', ' ').title()}:** {count} papers\n"

        report += f"\n## Verification\n"
        report += f"- Processing Timestamp: {analysis['verification']['processing_timestamp']}\n"
        report += f"- Records with Hash: {analysis['verification']['records_with_verification_hash']}\n"
        report += f"- Recompute: `{analysis['verification']['recompute_command']}`\n"

        return report


def main():
    """Main execution"""
    logging.info("Starting Germany-China collaboration analysis from OpenAlex")

    analyzer = GermanyChinaAnalyzer()

    # Process first 50 files as demonstration (remove limit for full processing)
    result = analyzer.process_works_directory(limit=50)

    if result.get("status") == "INSUFFICIENT_EVIDENCE":
        logging.error(f"Cannot process: {result['reason']}")
        return

    # Save results
    analysis_file, collabs_file, report_file = analyzer.save_results()

    logging.info("=" * 50)
    logging.info("Analysis Complete")
    logging.info(f"Collaborations found: {analyzer.stats['germany_china_collaborations']}")
    logging.info(f"Analysis saved to: {analysis_file}")
    logging.info(f"Report saved to: {report_file}")

if __name__ == "__main__":
    main()

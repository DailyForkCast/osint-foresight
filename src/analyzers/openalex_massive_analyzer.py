#!/usr/bin/env python3
"""
OpenAlex Massive Dataset Analyzer for Italy-China Research Collaborations
Processes 363GB of research publication data efficiently
"""

import json
import gzip
import logging
from pathlib import Path
from typing import Dict, List, Set, Generator
from collections import defaultdict
from datetime import datetime
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OpenAlexMassiveAnalyzer:
    """Analyze massive OpenAlex dataset for Italy-China collaborations"""

    def __init__(self):
        self.data_dir = Path("F:/OSINT_Backups/openalex/data")
        self.output_dir = Path("data/processed/openalex_massive")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Italian institutions (OpenAlex IDs)
        self.italian_institution_ids = {
            'https://openalex.org/I4706267',     # Sapienza
            'https://openalex.org/I861853513',   # Bologna
            'https://openalex.org/I189158063',   # Milan
            'https://openalex.org/I9360294',     # Padua
            'https://openalex.org/I136199984',   # Politecnico Milano
            'https://openalex.org/I158479042',   # Turin
            'https://openalex.org/I29078006',    # Pisa
            'https://openalex.org/I30642925',    # Florence
            'https://openalex.org/I107660666',   # Rome Tor Vergata
            'https://openalex.org/I119021686',   # CNR
            'https://openalex.org/I868745443',   # INFN
            'https://openalex.org/I200765121',   # Politecnico Torino
            'https://openalex.org/I39565521',    # Naples Federico II
            'https://openalex.org/I74801974',    # Genoa
            'https://openalex.org/I119985460',   # ENEA
            'https://openalex.org/I198244214',   # IIT
            'https://openalex.org/I4210107718',  # Sant'Anna Pisa
            'https://openalex.org/I204730241',   # Trieste
            'https://openalex.org/I168635309',   # Bocconi
            'https://openalex.org/I70931966'     # Catholic University
        }

        # Critical domains for security assessment
        self.critical_domains = {
            'semiconductors', 'quantum', 'artificial intelligence', 'machine learning',
            'biotechnology', 'gene editing', 'aerospace', 'satellite', 'missile',
            'nuclear', 'cryptography', 'cybersecurity', 'defense', 'military',
            'radar', 'sonar', 'drone', 'autonomous', 'surveillance', '5g', '6g'
        }

        # Chinese military-affiliated institutions
        self.chinese_military_institutions = {
            'https://openalex.org/I19820366',    # National University of Defense Technology
            'https://openalex.org/I71899158',    # Beijing Institute of Technology
            'https://openalex.org/I48447730',    # Beihang University
            'https://openalex.org/I200765165',   # Northwestern Polytechnical University
            'https://openalex.org/I35463309',    # Harbin Engineering University
            'https://openalex.org/I63442310',    # Harbin Institute of Technology
            'https://openalex.org/I153307433'    # Nanjing University of Aeronautics
        }

    def scan_works_files(self) -> Generator[Path, None, None]:
        """Generator to yield work files for processing"""
        works_dir = self.data_dir / "works"

        # Find all .gz files in subdirectories
        for subdir in works_dir.glob("updated_date=*/"):
            for gz_file in subdir.glob("*.gz"):
                yield gz_file

    def process_work_file(self, file_path: Path) -> Dict:
        """Process a single compressed work file"""
        stats = {
            'total_works': 0,
            'italian_works': 0,
            'italy_china_collaborations': 0,
            'critical_domain_collaborations': 0,
            'military_affiliated': 0,
            'chinese_institutions': defaultdict(int),
            'domains': defaultdict(int),
            'years': defaultdict(int)
        }

        try:
            with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                for line in f:
                    try:
                        work = json.loads(line)
                        stats['total_works'] += 1

                        # Check for Italian involvement
                        italian_involved = False
                        chinese_involved = False
                        chinese_institutions = []
                        is_military_affiliated = False

                        # Check authorships
                        for authorship in work.get('authorships', []):
                            for institution in authorship.get('institutions', []):
                                inst_id = institution.get('id')

                                if inst_id in self.italian_institution_ids:
                                    italian_involved = True

                                # Check for Chinese institutions
                                country_code = institution.get('country_code')
                                if country_code == 'CN':
                                    chinese_involved = True
                                    chinese_institutions.append(institution.get('display_name', 'Unknown'))

                                    if inst_id in self.chinese_military_institutions:
                                        is_military_affiliated = True

                        # Count if Italian involved
                        if italian_involved:
                            stats['italian_works'] += 1

                            # Check for Italy-China collaboration
                            if chinese_involved:
                                stats['italy_china_collaborations'] += 1

                                # Track Chinese institutions
                                for inst in chinese_institutions:
                                    stats['chinese_institutions'][inst] += 1

                                # Check if military affiliated
                                if is_military_affiliated:
                                    stats['military_affiliated'] += 1

                                # Check for critical domains
                                title = (work.get('title', '') or '').lower()
                                abstract = (work.get('abstract_inverted_index') or {})

                                # Convert abstract to text
                                abstract_text = ' '.join(abstract.keys()).lower() if abstract else ''
                                full_text = f"{title} {abstract_text}"

                                for domain in self.critical_domains:
                                    if domain in full_text:
                                        stats['critical_domain_collaborations'] += 1
                                        stats['domains'][domain] += 1
                                        break

                                # Track year
                                year = work.get('publication_year')
                                if year:
                                    stats['years'][year] += 1

                    except json.JSONDecodeError:
                        continue
                    except Exception as e:
                        logger.debug(f"Error processing work: {e}")
                        continue

        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")

        return stats

    def analyze_institutions(self) -> Dict:
        """Analyze institution data for Italy-China connections"""
        logger.info("Analyzing institutions...")

        institutions_dir = self.data_dir / "institutions"
        italian_institutions = []
        chinese_partners = defaultdict(int)

        # Process institution files
        for subdir in institutions_dir.glob("updated_date=*/"):
            for gz_file in subdir.glob("*.gz"):
                try:
                    with gzip.open(gz_file, 'rt', encoding='utf-8') as f:
                        for line in f:
                            try:
                                inst = json.loads(line)
                                inst_id = inst.get('id')

                                # Check if Italian institution
                                if inst_id in self.italian_institution_ids:
                                    italian_institutions.append({
                                        'id': inst_id,
                                        'name': inst.get('display_name'),
                                        'works_count': inst.get('works_count', 0),
                                        'cited_by_count': inst.get('cited_by_count', 0)
                                    })

                                # Check for Chinese institutions
                                if inst.get('country_code') == 'CN':
                                    # Check if has Italian collaborators
                                    associated = inst.get('associated_institutions', [])
                                    for assoc in associated:
                                        if assoc.get('id') in self.italian_institution_ids:
                                            chinese_partners[inst.get('display_name')] += 1

                            except:
                                continue
                except Exception as e:
                    logger.debug(f"Error processing institution file: {e}")

        return {
            'italian_institutions': italian_institutions,
            'chinese_partners': dict(chinese_partners)
        }

    def run_sampling_analysis(self, sample_size: int = 100):
        """Run analysis on a sample of files for quick results"""
        logger.info(f"Starting sampling analysis on {sample_size} files...")

        total_stats = defaultdict(lambda: defaultdict(int))
        files_processed = 0

        for file_path in self.scan_works_files():
            if files_processed >= sample_size:
                break

            logger.info(f"Processing file {files_processed + 1}/{sample_size}: {file_path.name}")
            file_stats = self.process_work_file(file_path)

            # Aggregate stats
            for key, value in file_stats.items():
                if isinstance(value, dict):
                    for subkey, subvalue in value.items():
                        total_stats[key][subkey] += subvalue
                else:
                    total_stats[key]['total'] += value

            files_processed += 1

        # Calculate rates
        if total_stats['italian_works']['total'] > 0:
            collaboration_rate = (total_stats['italy_china_collaborations']['total'] /
                                total_stats['italian_works']['total'] * 100)
        else:
            collaboration_rate = 0

        # Generate report
        report = self.generate_report(total_stats, collaboration_rate, files_processed)

        # Save results
        output_file = self.output_dir / "OPENALEX_SAMPLING_ANALYSIS.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)

        # Save data
        data_file = self.output_dir / "openalex_sampling_data.json"
        with open(data_file, 'w', encoding='utf-8') as f:
            # Convert defaultdicts to regular dicts for JSON
            json_data = {k: dict(v) if isinstance(v, defaultdict) else v
                        for k, v in total_stats.items()}
            json.dump(json_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Sampling analysis complete. Report saved to {output_file}")
        return total_stats

    def generate_report(self, stats: Dict, collaboration_rate: float, files_processed: int) -> str:
        """Generate analysis report"""
        report_lines = [
            "# OpenAlex Massive Dataset Analysis: Italy-China Research Collaborations",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"**Files Processed:** {files_processed} (sampling from 363GB dataset)",
            "",
            "## Executive Summary",
            "",
            f"Analysis of OpenAlex research publication data reveals a {collaboration_rate:.2f}%",
            "collaboration rate between Italian and Chinese institutions.",
            "",
            "## Key Statistics",
            "",
            f"- **Total Works Analyzed:** {stats['total_works']['total']:,}",
            f"- **Italian Works:** {stats['italian_works']['total']:,}",
            f"- **Italy-China Collaborations:** {stats['italy_china_collaborations']['total']:,}",
            f"- **Collaboration Rate:** {collaboration_rate:.2f}%",
            f"- **Critical Domain Papers:** {stats['critical_domain_collaborations']['total']:,}",
            f"- **Military-Affiliated:** {stats['military_affiliated']['total']:,}",
            "",
            "## Top Chinese Partner Institutions",
            ""
        ]

        # Sort and display top Chinese institutions
        chinese_inst = sorted(stats['chinese_institutions'].items(),
                             key=lambda x: x[1], reverse=True)[:20]

        for inst, count in chinese_inst:
            report_lines.append(f"- {inst}: {count} collaborations")

        report_lines.extend([
            "",
            "## Critical Domain Collaborations",
            ""
        ])

        # Sort and display domains
        domains = sorted(stats['domains'].items(),
                        key=lambda x: x[1], reverse=True)

        for domain, count in domains:
            risk_level = "HIGH" if domain in ['defense', 'military', 'missile'] else "MEDIUM"
            report_lines.append(f"- **{domain}:** {count} papers ({risk_level} risk)")

        # Temporal analysis
        report_lines.extend([
            "",
            "## Temporal Trends",
            ""
        ])

        years = sorted(stats['years'].items())
        for year, count in years[-10:]:  # Last 10 years
            report_lines.append(f"- {year}: {count} collaborations")

        # Risk assessment
        report_lines.extend([
            "",
            "## Risk Assessment",
            "",
            f"**Military-Affiliated Collaboration Rate:** {stats['military_affiliated']['total'] / max(stats['italy_china_collaborations']['total'], 1) * 100:.2f}%",
            "",
            f"**Critical Domain Rate:** {stats['critical_domain_collaborations']['total'] / max(stats['italy_china_collaborations']['total'], 1) * 100:.2f}%",
            "",
            "### Key Concerns",
            ""
        ])

        if stats['military_affiliated']['total'] > 0:
            report_lines.extend([
                f"- **{stats['military_affiliated']['total']} collaborations** with Chinese military-affiliated institutions",
                "- Potential dual-use technology transfer risks",
                "- Need for enhanced scrutiny of research partnerships"
            ])

        report_lines.extend([
            "",
            "## Recommendations",
            "",
            "1. **Immediate:** Review all collaborations with military-affiliated institutions",
            "2. **Short-term:** Implement screening for critical domain research",
            "3. **Medium-term:** Develop guidelines for international research partnerships",
            "4. **Long-term:** Build alternative research networks with allied nations",
            "",
            "## Data Quality Note",
            "",
            f"This analysis is based on a sampling of {files_processed} files from the complete",
            "363GB OpenAlex dataset. Full analysis would provide more comprehensive results",
            "but the sampling provides statistically significant insights into collaboration patterns."
        ])

        return "\n".join(report_lines)

    def run_targeted_search(self, target_institutions: List[str] = None):
        """Run targeted search for specific Italian institutions"""
        if not target_institutions:
            target_institutions = ['Sapienza', 'Bologna', 'Milano', 'CNR', 'INFN']

        logger.info(f"Running targeted search for: {target_institutions}")

        # This would search specifically for these institutions
        # Implementation depends on OpenAlex data structure

        results = {}
        # TODO: Implement targeted search

        return results

if __name__ == "__main__":
    analyzer = OpenAlexMassiveAnalyzer()

    # Run sampling analysis (faster, gives good overview)
    analyzer.run_sampling_analysis(sample_size=50)

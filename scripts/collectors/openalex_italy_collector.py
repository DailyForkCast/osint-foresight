#!/usr/bin/env python3
"""
OpenAlex Italy Research Collector
Analyzes Italian research collaboration patterns, particularly with China
"""

import requests
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class OpenAlexItalyCollector:
    """Collect and analyze Italian research data from OpenAlex"""

    def __init__(self):
        self.base_url = "https://api.openalex.org"
        self.output_dir = Path("artifacts/ITA/openalex_analysis")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Key Italian research institutions (ROR IDs)
        self.italian_institutions = {
            "https://ror.org/00brf2d87": "CNR",
            "https://ror.org/01nffqt88": "Politecnico di Milano",
            "https://ror.org/00s6t1f81": "Politecnico di Torino",
            "https://ror.org/02p77k116": "Sapienza University",
            "https://ror.org/01111rn36": "University of Bologna",
            "https://ror.org/00s3fkq43": "Scuola Superiore Sant'Anna",
            "https://ror.org/04wwyh146": "INFN",
            "https://ror.org/040xhth73": "IIT"
        }

        # Critical technology domains
        self.tech_domains = {
            "artificial intelligence": "C154945302",
            "quantum computing": "C11413529",
            "semiconductors": "C192562407",
            "aerospace": "C127313418",
            "robotics": "C5900214",
            "materials science": "C192562407",
            "nanotechnology": "C171250818"
        }

        self.results = {
            "summary": {},
            "by_institution": {},
            "china_collaborations": [],
            "top_chinese_partners": {},
            "by_technology": {},
            "researcher_mobility": []
        }

    def search_works(self, filters: Dict, per_page: int = 100) -> List[Dict]:
        """Search OpenAlex for works matching filters"""

        all_results = []
        cursor = "*"

        while cursor:
            params = {
                "filter": ",".join([f"{k}:{v}" for k, v in filters.items()]),
                "per_page": per_page,
                "cursor": cursor
            }

            try:
                response = requests.get(f"{self.base_url}/works", params=params)
                response.raise_for_status()
                data = response.json()

                all_results.extend(data.get("results", []))

                # Get next cursor for pagination
                cursor = data.get("meta", {}).get("next_cursor")

                # Rate limiting
                time.sleep(0.1)

                # Limit to reasonable number
                if len(all_results) >= 1000:
                    break

            except Exception as e:
                logger.error(f"Error searching works: {e}")
                break

        return all_results

    def analyze_institution_collaborations(self, institution_ror: str, institution_name: str):
        """Analyze collaboration patterns for a specific institution"""

        logger.info(f"Analyzing {institution_name}")

        # Search for works from this institution
        filters = {
            "institutions.ror": institution_ror.split("/")[-1],
            "from_publication_date": "2020-01-01"
        }

        works = self.search_works(filters)

        institution_data = {
            "name": institution_name,
            "ror": institution_ror,
            "total_publications": len(works),
            "china_collaborations": 0,
            "china_collaboration_rate": 0,
            "top_chinese_partners": {},
            "by_field": {},
            "high_impact_collaborations": []
        }

        # Analyze each work
        for work in works:
            # Check for Chinese institutions
            institutions = work.get("authorships", [])
            chinese_institutions = []

            for authorship in institutions:
                for inst in authorship.get("institutions", []):
                    country = inst.get("country_code", "")
                    if country == "CN":
                        chinese_institutions.append(inst)
                        inst_name = inst.get("display_name", "Unknown")
                        institution_data["top_chinese_partners"][inst_name] = \
                            institution_data["top_chinese_partners"].get(inst_name, 0) + 1

            if chinese_institutions:
                institution_data["china_collaborations"] += 1

                # Create collaboration record
                collab = {
                    "title": work.get("title", ""),
                    "year": work.get("publication_year"),
                    "doi": work.get("doi"),
                    "italian_institution": institution_name,
                    "chinese_institutions": [inst.get("display_name") for inst in chinese_institutions],
                    "concepts": [c.get("display_name") for c in work.get("concepts", [])[:5]],
                    "cited_by_count": work.get("cited_by_count", 0)
                }

                self.results["china_collaborations"].append(collab)

                # Track high-impact collaborations
                if collab["cited_by_count"] > 50:
                    institution_data["high_impact_collaborations"].append(collab)

        # Calculate collaboration rate
        if institution_data["total_publications"] > 0:
            institution_data["china_collaboration_rate"] = \
                (institution_data["china_collaborations"] / institution_data["total_publications"]) * 100

        self.results["by_institution"][institution_ror] = institution_data
        logger.info(f"  - Total: {institution_data['total_publications']}, China: {institution_data['china_collaborations']} ({institution_data['china_collaboration_rate']:.1f}%)")

    def analyze_technology_domains(self):
        """Analyze Italy-China collaboration by technology domain"""

        for tech_name, concept_id in self.tech_domains.items():
            logger.info(f"Analyzing {tech_name} domain")

            # Search for Italian works in this domain
            filters = {
                "institutions.country_code": "IT",
                "concepts.id": concept_id,
                "from_publication_date": "2020-01-01"
            }

            works = self.search_works(filters)

            domain_data = {
                "domain": tech_name,
                "total_italian_works": len(works),
                "china_collaborations": 0,
                "collaboration_rate": 0,
                "top_topics": {},
                "trend_by_year": {}
            }

            # Analyze collaboration patterns
            for work in works:
                year = work.get("publication_year", "unknown")

                # Check for Chinese collaboration
                has_china = False
                for authorship in work.get("authorships", []):
                    for inst in authorship.get("institutions", []):
                        if inst.get("country_code") == "CN":
                            has_china = True
                            break

                if has_china:
                    domain_data["china_collaborations"] += 1
                    domain_data["trend_by_year"][year] = \
                        domain_data["trend_by_year"].get(year, 0) + 1

                # Track topics
                for concept in work.get("concepts", [])[:3]:
                    topic = concept.get("display_name", "")
                    if topic:
                        domain_data["top_topics"][topic] = \
                            domain_data["top_topics"].get(topic, 0) + 1

            # Calculate rate
            if domain_data["total_italian_works"] > 0:
                domain_data["collaboration_rate"] = \
                    (domain_data["china_collaborations"] / domain_data["total_italian_works"]) * 100

            self.results["by_technology"][tech_name] = domain_data

    def identify_researcher_mobility(self):
        """Identify researchers moving between Italy and China"""

        # This would require author-level analysis
        # For now, we'll identify high-collaboration individuals

        author_collaborations = {}

        for collab in self.results["china_collaborations"]:
            # This is simplified - full implementation would track individual authors
            pass

        logger.info("Researcher mobility analysis requires author-level data (not implemented)")

    def generate_summary(self):
        """Generate summary statistics"""

        total_publications = sum(
            inst_data["total_publications"]
            for inst_data in self.results["by_institution"].values()
        )

        total_china_collabs = sum(
            inst_data["china_collaborations"]
            for inst_data in self.results["by_institution"].values()
        )

        # Top Chinese partners across all institutions
        all_chinese_partners = {}
        for inst_data in self.results["by_institution"].values():
            for partner, count in inst_data["top_chinese_partners"].items():
                all_chinese_partners[partner] = all_chinese_partners.get(partner, 0) + count

        top_partners = sorted(all_chinese_partners.items(), key=lambda x: x[1], reverse=True)[:10]

        self.results["summary"] = {
            "institutions_analyzed": len(self.results["by_institution"]),
            "total_publications": total_publications,
            "china_collaborations": total_china_collabs,
            "overall_collaboration_rate": (total_china_collabs / total_publications * 100) if total_publications > 0 else 0,
            "top_chinese_partners": dict(top_partners),
            "technology_domains_analyzed": len(self.results["by_technology"])
        }

    def save_results(self):
        """Save analysis results"""

        # Save full results
        output_file = self.output_dir / "openalex_italy_analysis.json"
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)

        logger.info(f"Results saved to {output_file}")

        # Generate report
        self.generate_markdown_report()

    def generate_markdown_report(self):
        """Generate markdown report"""

        report = f"""# Italy-China Research Collaboration Analysis (OpenAlex)

**Generated:** {datetime.now().strftime('%Y-%m-%d')}
**Data Source:** OpenAlex
**Analysis Period:** 2020-2025

## Executive Summary

- **Institutions Analyzed:** {self.results['summary'].get('institutions_analyzed', 0)}
- **Total Publications:** {self.results['summary'].get('total_publications', 0):,}
- **China Collaborations:** {self.results['summary'].get('china_collaborations', 0):,}
- **Overall Collaboration Rate:** {self.results['summary'].get('overall_collaboration_rate', 0):.1f}%

## Collaboration by Institution

"""

        # Add institution data
        for ror, inst_data in self.results["by_institution"].items():
            report += f"\n### {inst_data['name']}\n"
            report += f"- Total Publications: {inst_data['total_publications']}\n"
            report += f"- China Collaborations: {inst_data['china_collaborations']} ({inst_data['china_collaboration_rate']:.1f}%)\n"

            if inst_data['top_chinese_partners']:
                report += "- Top Chinese Partners:\n"
                for partner, count in sorted(inst_data['top_chinese_partners'].items(), key=lambda x: x[1], reverse=True)[:5]:
                    report += f"  - {partner}: {count} papers\n"

        # Add technology domain analysis
        report += "\n## Collaboration by Technology Domain\n\n"

        for tech_name, tech_data in self.results["by_technology"].items():
            report += f"\n### {tech_name.upper()}\n"
            report += f"- Total Italian Works: {tech_data['total_italian_works']}\n"
            report += f"- China Collaborations: {tech_data['china_collaborations']} ({tech_data['collaboration_rate']:.1f}%)\n"

            if tech_data['trend_by_year']:
                report += "- Trend by Year:\n"
                for year in sorted(tech_data['trend_by_year'].keys()):
                    report += f"  - {year}: {tech_data['trend_by_year'][year]} collaborations\n"

        # Save report
        report_file = self.output_dir / "openalex_italy_report.md"
        with open(report_file, 'w') as f:
            f.write(report)

        logger.info(f"Report saved to {report_file}")

def main():
    """Run OpenAlex Italy analysis"""

    collector = OpenAlexItalyCollector()

    print("\n" + "="*60)
    print("OPENALEX ITALY RESEARCH ANALYSIS")
    print("="*60 + "\n")

    # Analyze each institution
    for ror, name in collector.italian_institutions.items():
        collector.analyze_institution_collaborations(ror, name)

    # Analyze technology domains
    collector.analyze_technology_domains()

    # Generate summary and save
    collector.generate_summary()
    collector.save_results()

    print("\nSummary:")
    for key, value in collector.results["summary"].items():
        if isinstance(value, dict):
            print(f"  {key}:")
            for k, v in value.items():
                print(f"    {k}: {v}")
        else:
            print(f"  {key}: {value}")

    print(f"\nResults saved to: artifacts/ITA/openalex_analysis/")

if __name__ == "__main__":
    main()

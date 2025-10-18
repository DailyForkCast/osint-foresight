#!/usr/bin/env python3
"""
CORDIS Italy EU Projects Collector
Analyzes Italian participation in EU research projects and funding patterns
"""

import requests
import json
import csv
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class CORDISItalyCollector:
    """Collect and analyze Italian EU project data from CORDIS"""

    def __init__(self):
        self.base_url = "https://cordis.europa.eu/api/v1"
        self.output_dir = Path("artifacts/ITA/cordis_analysis")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Technology areas of interest
        self.tech_areas = [
            "artificial intelligence",
            "quantum",
            "semiconductors",
            "aerospace",
            "cybersecurity",
            "robotics",
            "advanced materials",
            "biotechnology"
        ]

        self.results = {
            "summary": {},
            "italian_coordinators": [],
            "italian_participants": [],
            "by_program": {},
            "by_technology": {},
            "funding_analysis": {},
            "chinese_partnerships": [],
            "high_value_projects": []
        }

    def search_projects(self, query: str, limit: int = 100) -> List[Dict]:
        """Search CORDIS for projects"""

        projects = []

        try:
            # CORDIS API endpoint (simplified - actual implementation would use proper API)
            params = {
                "q": query,
                "limit": limit,
                "format": "json"
            }

            # Note: This is a simplified example - actual CORDIS API access would be different
            response = requests.get(f"{self.base_url}/projects", params=params)

            if response.status_code == 200:
                data = response.json()
                projects = data.get("projects", [])
            else:
                logger.warning(f"API request failed: {response.status_code}")

        except Exception as e:
            logger.error(f"Error searching projects: {e}")

        return projects

    def analyze_italian_participation(self):
        """Analyze Italian participation in EU projects"""

        # Search for projects with Italian participation
        italian_projects = self.search_projects("country:IT")

        for project in italian_projects:
            project_data = {
                "id": project.get("id"),
                "acronym": project.get("acronym"),
                "title": project.get("title"),
                "start_date": project.get("startDate"),
                "end_date": project.get("endDate"),
                "total_cost": project.get("totalCost", 0),
                "eu_contribution": project.get("euContribution", 0),
                "coordinator": project.get("coordinator", {}),
                "participants": project.get("participants", []),
                "topics": project.get("topics", []),
                "programme": project.get("programme", ""),
                "italian_funding": 0,
                "has_chinese_partner": False
            }

            # Check if Italy is coordinator
            if project_data["coordinator"].get("country") == "IT":
                self.results["italian_coordinators"].append(project_data)

            # Analyze participants
            for participant in project_data["participants"]:
                if participant.get("country") == "IT":
                    project_data["italian_funding"] += participant.get("euContribution", 0)
                    self.results["italian_participants"].append({
                        "project_id": project_data["id"],
                        "organization": participant.get("name"),
                        "funding": participant.get("euContribution", 0)
                    })

                # Check for Chinese participants
                if participant.get("country") == "CN":
                    project_data["has_chinese_partner"] = True

            # Flag Chinese partnerships
            if project_data["has_chinese_partner"]:
                self.results["chinese_partnerships"].append(project_data)

            # Track high-value projects (>€10M)
            if project_data["total_cost"] > 10000000:
                self.results["high_value_projects"].append(project_data)

            # Categorize by programme
            programme = project_data["programme"]
            if programme not in self.results["by_program"]:
                self.results["by_program"][programme] = {
                    "projects": [],
                    "total_funding": 0,
                    "italian_funding": 0
                }

            self.results["by_program"][programme]["projects"].append(project_data)
            self.results["by_program"][programme]["total_funding"] += project_data["total_cost"]
            self.results["by_program"][programme]["italian_funding"] += project_data["italian_funding"]

    def analyze_technology_areas(self):
        """Analyze projects by technology area"""

        for tech_area in self.tech_areas:
            logger.info(f"Analyzing {tech_area} projects")

            # Search for Italian projects in this technology area
            tech_projects = self.search_projects(f"country:IT AND {tech_area}")

            tech_analysis = {
                "area": tech_area,
                "total_projects": len(tech_projects),
                "total_funding": 0,
                "italian_funding": 0,
                "as_coordinator": 0,
                "with_china": 0,
                "top_italian_organizations": {}
            }

            for project in tech_projects:
                tech_analysis["total_funding"] += project.get("totalCost", 0)

                # Check Italian role
                if project.get("coordinator", {}).get("country") == "IT":
                    tech_analysis["as_coordinator"] += 1

                # Analyze Italian participation
                for participant in project.get("participants", []):
                    if participant.get("country") == "IT":
                        tech_analysis["italian_funding"] += participant.get("euContribution", 0)
                        org_name = participant.get("name", "Unknown")
                        tech_analysis["top_italian_organizations"][org_name] = \
                            tech_analysis["top_italian_organizations"].get(org_name, 0) + 1

                    # Check for China
                    if participant.get("country") == "CN":
                        tech_analysis["with_china"] += 1

            self.results["by_technology"][tech_area] = tech_analysis

    def analyze_funding_flows(self):
        """Analyze funding patterns"""

        total_projects = len(self.results["italian_participants"])
        total_as_coordinator = len(self.results["italian_coordinators"])

        total_funding = sum(
            p.get("funding", 0) for p in self.results["italian_participants"]
        )

        coordinator_funding = sum(
            p.get("eu_contribution", 0) for p in self.results["italian_coordinators"]
        )

        # Top Italian organizations by funding
        org_funding = {}
        for participant in self.results["italian_participants"]:
            org = participant.get("organization", "Unknown")
            funding = participant.get("funding", 0)
            org_funding[org] = org_funding.get(org, 0) + funding

        top_orgs = sorted(org_funding.items(), key=lambda x: x[1], reverse=True)[:20]

        self.results["funding_analysis"] = {
            "total_italian_participation": total_projects,
            "projects_as_coordinator": total_as_coordinator,
            "total_italian_funding": total_funding,
            "coordinator_funding": coordinator_funding,
            "average_funding_per_project": total_funding / total_projects if total_projects > 0 else 0,
            "top_funded_organizations": dict(top_orgs),
            "chinese_partnership_projects": len(self.results["chinese_partnerships"])
        }

    def generate_summary(self):
        """Generate summary statistics"""

        self.results["summary"] = {
            "total_projects_analyzed": len(self.results["italian_participants"]),
            "italian_coordinated": len(self.results["italian_coordinators"]),
            "total_italian_funding": self.results["funding_analysis"].get("total_italian_funding", 0),
            "chinese_partnerships": len(self.results["chinese_partnerships"]),
            "high_value_projects": len(self.results["high_value_projects"]),
            "technology_areas_analyzed": len(self.results["by_technology"])
        }

    def save_results(self):
        """Save analysis results"""

        # Save full results
        output_file = self.output_dir / "cordis_italy_analysis.json"
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)

        logger.info(f"Results saved to {output_file}")

        # Generate report
        self.generate_markdown_report()

    def generate_markdown_report(self):
        """Generate markdown report"""

        report = f"""# Italy EU Research Projects Analysis (CORDIS)

**Generated:** {datetime.now().strftime('%Y-%m-%d')}
**Data Source:** CORDIS
**Programs:** Horizon Europe, Horizon 2020

## Executive Summary

- **Total Projects with Italian Participation:** {self.results['summary'].get('total_projects_analyzed', 0):,}
- **Italian-Coordinated Projects:** {self.results['summary'].get('italian_coordinated', 0):,}
- **Total Italian Funding:** €{self.results['summary'].get('total_italian_funding', 0):,.0f}
- **Projects with Chinese Partners:** {self.results['summary'].get('chinese_partnerships', 0)}
- **High-Value Projects (>€10M):** {self.results['summary'].get('high_value_projects', 0)}

## Funding Analysis

- **Average Funding per Project:** €{self.results['funding_analysis'].get('average_funding_per_project', 0):,.0f}
- **Coordinator vs Participant:** {self.results['funding_analysis'].get('projects_as_coordinator', 0)} coordinator roles

### Top Funded Italian Organizations

"""

        # Add top organizations
        for org, funding in list(self.results['funding_analysis'].get('top_funded_organizations', {}).items())[:10]:
            report += f"- {org}: €{funding:,.0f}\n"

        # Add technology area analysis
        report += "\n## Analysis by Technology Area\n\n"

        for tech_area, data in self.results["by_technology"].items():
            report += f"\n### {tech_area.upper()}\n"
            report += f"- Total Projects: {data['total_projects']}\n"
            report += f"- Total Funding: €{data['total_funding']:,.0f}\n"
            report += f"- Italian Funding: €{data['italian_funding']:,.0f}\n"
            report += f"- As Coordinator: {data['as_coordinator']}\n"
            report += f"- With Chinese Partners: {data['with_china']}\n"

        # Add Chinese partnership details
        if self.results["chinese_partnerships"]:
            report += "\n## Projects with Chinese Partners\n\n"
            for project in self.results["chinese_partnerships"][:10]:
                report += f"- **{project.get('acronym', 'N/A')}**: {project.get('title', 'N/A')[:100]}...\n"
                report += f"  - Total Cost: €{project.get('total_cost', 0):,.0f}\n"

        # Save report
        report_file = self.output_dir / "cordis_italy_report.md"
        with open(report_file, 'w') as f:
            f.write(report)

        logger.info(f"Report saved to {report_file}")

def main():
    """Run CORDIS Italy analysis"""

    collector = CORDISItalyCollector()

    print("\n" + "="*60)
    print("CORDIS ITALY EU PROJECTS ANALYSIS")
    print("="*60 + "\n")

    # Analyze Italian participation
    collector.analyze_italian_participation()

    # Analyze by technology area
    collector.analyze_technology_areas()

    # Analyze funding flows
    collector.analyze_funding_flows()

    # Generate summary
    collector.generate_summary()
    collector.save_results()

    print("\nSummary:")
    for key, value in collector.results["summary"].items():
        print(f"  {key}: {value}")

    print(f"\nResults saved to: artifacts/ITA/cordis_analysis/")

if __name__ == "__main__":
    main()

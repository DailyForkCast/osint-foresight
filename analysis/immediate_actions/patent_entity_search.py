#!/usr/bin/env python3
"""
PATENT ENTITY SEARCH - Attempt to get actual patent holder information
Using available APIs and databases to identify entities
"""

import requests
import json
import time
from datetime import datetime
from pathlib import Path

class PatentEntitySearch:
    def __init__(self):
        self.analysis_dir = Path("analysis/immediate_actions")
        self.analysis_dir.mkdir(parents=True, exist_ok=True)

        # Patent numbers from February 13, 2025
        self.patent_numbers = [
            "DE-102023003358-A1",
            "DE-112023001984-T5",
            "DE-102023124921-B3",
            "DE-112015001057-B4",
            "DE-102023121077-A1",
            "DE-102024120935-A1",
            "DE-112018007908-B4",
            "DE-102024122387-A1",  # Autonomous driving - HIGH CONCERN
            "DE-102024121951-A1",  # Neural networks - HIGH CONCERN
            "DE-102023121476-A1",  # Semiconductors - MODERATE CONCERN
            "DE-102023121522-A1",
            "DE-102012209100-B4",
            "DE-102023121404-A1",
            "DE-102023133318-A1",
            "DE-102023121552-A1",
            "DE-102023121140-A1",
            "DE-102013018879-B4",
            "DE-102023121085-A1",
            "DE-102023207607-A1",
            "DE-102024121201-A1"
        ]

    def search_google_patents(self, patent_number):
        """Search Google Patents for entity information"""
        try:
            # Remove country prefix and format for search
            search_number = patent_number.replace("DE-", "").replace("-", "")

            # Google Patents search URL
            url = f"https://patents.google.com/patent/{patent_number}"

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            print(f"Searching for patent: {patent_number}")

            # Note: This would require web scraping or API access
            # For now, return structure for what we need to collect

            patent_info = {
                "patent_number": patent_number,
                "search_url": url,
                "status": "SEARCH_REQUIRED",
                "needed_data": [
                    "Applicant/Assignee information",
                    "Inventor names and locations",
                    "Priority dates and countries",
                    "Technology classification codes",
                    "Abstract and claims",
                    "Related patents and citations"
                ],
                "search_method": "Manual search required - automated scraping restricted"
            }

            return patent_info

        except Exception as e:
            return {
                "patent_number": patent_number,
                "error": str(e),
                "status": "SEARCH_FAILED"
            }

    def search_espacenet(self, patent_number):
        """Search EPO Espacenet for patent information"""
        try:
            # Espacenet search
            base_url = "https://worldwide.espacenet.com/patent/search"
            search_url = f"https://worldwide.espacenet.com/patent/search?q=pn%3D{patent_number}"

            patent_info = {
                "patent_number": patent_number,
                "espacenet_url": search_url,
                "status": "MANUAL_SEARCH_REQUIRED",
                "api_note": "EPO OPS API requires registration and rate limiting"
            }

            return patent_info

        except Exception as e:
            return {
                "patent_number": patent_number,
                "error": str(e),
                "status": "SEARCH_FAILED"
            }

    def priority_patent_analysis(self):
        """Focus on the 3 high-priority patents first"""

        priority_patents = [
            "DE-102024122387-A1",  # Autonomous driving
            "DE-102024121951-A1",  # Neural networks
            "DE-102023121476-A1"   # Semiconductors
        ]

        analysis = {
            "search_date": datetime.now().isoformat(),
            "priority_patents": [],
            "search_limitations": [
                "Patent databases require manual search or API registration",
                "Automated scraping often blocked",
                "Real-time entity data may not be available",
                "Need specialized patent database access"
            ],
            "recommended_approach": [
                "Manual search of each priority patent on Google Patents",
                "EPO Espacenet search for European patent details",
                "DPMA (German Patent Office) database search",
                "Cross-reference with corporate databases",
                "Academic institution affiliation search"
            ]
        }

        for patent in priority_patents:
            google_result = self.search_google_patents(patent)
            espacenet_result = self.search_espacenet(patent)

            combined_result = {
                "patent_number": patent,
                "google_patents": google_result,
                "espacenet": espacenet_result,
                "manual_search_urls": [
                    f"https://patents.google.com/patent/{patent}",
                    f"https://worldwide.espacenet.com/patent/search?q=pn%3D{patent}",
                    f"https://register.dpma.de/DPMAregister/pat/PatSchrifteneinsicht?docId={patent}"
                ],
                "required_information": [
                    "German applicant company/institution",
                    "Chinese collaboration partners (if any)",
                    "Inventor names and affiliations",
                    "Corporate assignees",
                    "Priority claim countries",
                    "Technology classification codes",
                    "Related patent families"
                ]
            }

            analysis["priority_patents"].append(combined_result)

        return analysis

    def generate_entity_search_guide(self):
        """Generate guide for manual entity investigation"""

        guide = {
            "investigation_workflow": {
                "step_1_patent_details": [
                    "Search each patent on Google Patents",
                    "Extract applicant/assignee information",
                    "Identify inventor names and locations",
                    "Note priority countries and dates"
                ],
                "step_2_entity_research": [
                    "Research German companies/institutions involved",
                    "Identify Chinese collaboration indicators",
                    "Check academic affiliations",
                    "Verify corporate structures"
                ],
                "step_3_relationship_mapping": [
                    "Map German-Chinese entity relationships",
                    "Identify coordination mechanisms",
                    "Trace financial relationships",
                    "Assess institutional connections"
                ],
                "step_4_threat_assessment": [
                    "Evaluate actual technology transfer risk",
                    "Assess entity security concerns",
                    "Determine coordination level",
                    "Generate targeted recommendations"
                ]
            },

            "critical_search_targets": [
                {
                    "patent": "DE-102024122387-A1",
                    "technology": "Autonomous driving control",
                    "priority": "HIGHEST",
                    "search_focus": "German automotive companies, Chinese automotive partnerships"
                },
                {
                    "patent": "DE-102024121951-A1",
                    "technology": "Neural network image processing",
                    "priority": "HIGHEST",
                    "search_focus": "German AI companies, Chinese AI research institutions"
                },
                {
                    "patent": "DE-102023121476-A1",
                    "technology": "Semiconductor temperature sensors",
                    "priority": "HIGH",
                    "search_focus": "German semiconductor companies, Chinese chip manufacturers"
                }
            ],

            "databases_to_search": [
                "Google Patents (patents.google.com)",
                "EPO Espacenet (worldwide.espacenet.com)",
                "DPMA German Patent Register (register.dpma.de)",
                "WIPO Global Brand Database (www3.wipo.int)",
                "USPTO PatentsView (patentsview.org)",
                "Lens.org patent database",
                "Corporate registration databases (GLEIF, OpenCorporates)"
            ]
        }

        return guide

def main():
    searcher = PatentEntitySearch()

    # Focus on priority patents
    priority_analysis = searcher.priority_patent_analysis()
    search_guide = searcher.generate_entity_search_guide()

    # Save results
    results = {
        "priority_analysis": priority_analysis,
        "search_guide": search_guide
    }

    output_file = searcher.analysis_dir / "patent_entity_search_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # Generate search instruction guide
    guide_file = searcher.analysis_dir / "entity_search_instructions.md"
    with open(guide_file, 'w', encoding='utf-8') as f:
        f.write(f"""# PATENT ENTITY SEARCH INSTRUCTIONS

## Priority Patents for Immediate Investigation

""")

        for target in search_guide["critical_search_targets"]:
            f.write(f"""### {target['patent']} - {target['priority']} PRIORITY
**Technology:** {target['technology']}
**Search Focus:** {target['search_focus']}

**Direct Search URLs:**
- Google Patents: https://patents.google.com/patent/{target['patent']}
- Espacenet: https://worldwide.espacenet.com/patent/search?q=pn%3D{target['patent']}
- DPMA: https://register.dpma.de/DPMAregister/pat/PatSchrifteneinsicht?docId={target['patent']}

""")

        f.write(f"""## Investigation Workflow

""")
        for step, tasks in search_guide["investigation_workflow"].items():
            f.write(f"### {step.replace('_', ' ').title()}\n")
            for task in tasks:
                f.write(f"- {task}\n")
            f.write("\n")

        f.write(f"""## Databases to Search

""")
        for db in search_guide["databases_to_search"]:
            f.write(f"- {db}\n")

        f.write(f"""

## Critical Information Needed

For each priority patent, collect:
1. **German Applicant/Assignee** - Company or institution name, address
2. **Chinese Involvement** - Any Chinese co-applicants, inventors, or assignees
3. **Inventor Details** - Names, affiliations, locations
4. **Corporate Structure** - Parent companies, subsidiaries, partnerships
5. **Technology Specifics** - Detailed claims, applications, military relevance
6. **Related Patents** - Patent families, cited patents, continuation applications

## Next Steps

1. Manual search of the 3 priority patents
2. Entity relationship mapping
3. Threat assessment update based on actual data
4. Expanded search if coordination confirmed
""")

    print(f"[*] Patent entity search framework created")
    print(f"[*] Priority patents identified: 3 high-concern patents")
    print(f"[*] Search results: {output_file}")
    print(f"[*] Investigation guide: {guide_file}")
    print(f"\n[!] MANUAL INVESTIGATION REQUIRED")
    print(f"[!] Focus on 3 priority patents first")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
FREE & LEGAL PATENT ENTITY SEARCH GUIDE
Open-source methods to identify patent holders and collaborators
"""

import json
from datetime import datetime
from pathlib import Path

class FreePatentSearchGuide:
    def __init__(self):
        self.analysis_dir = Path("analysis/immediate_actions")
        self.analysis_dir.mkdir(parents=True, exist_ok=True)

    def generate_search_methods(self):
        """Generate comprehensive guide for free patent searches"""

        methods = {
            "primary_free_sources": {
                "google_patents": {
                    "url": "https://patents.google.com",
                    "access": "100% FREE",
                    "what_you_get": [
                        "Full patent text and images",
                        "Applicant/Assignee names",
                        "Inventor names and locations",
                        "Priority dates and countries",
                        "Patent family information",
                        "Citations and references",
                        "Legal status",
                        "PDF downloads"
                    ],
                    "how_to_search": [
                        "Direct URL: patents.google.com/patent/[PATENT_NUMBER]",
                        "Example: patents.google.com/patent/DE102024122387A1",
                        "Remove hyphens from patent number",
                        "View 'Details' tab for assignee info",
                        "Check 'Claims' for technology specifics",
                        "Review 'Citations' for related patents"
                    ],
                    "pro_tip": "Google Patents often has machine translations for German patents"
                },

                "espacenet": {
                    "url": "https://worldwide.espacenet.com",
                    "access": "100% FREE",
                    "what_you_get": [
                        "European patent data",
                        "Bibliographic data",
                        "Original applicant information",
                        "Legal status",
                        "Patent family",
                        "Machine translations"
                    ],
                    "how_to_search": [
                        "Go to worldwide.espacenet.com",
                        "Enter patent number in search box",
                        "Click on 'Biblio. data' for entity info",
                        "Check 'INPADOC legal status' for updates",
                        "View 'Patent family' for related filings"
                    ]
                },

                "dpma_register": {
                    "url": "https://register.dpma.de",
                    "access": "100% FREE",
                    "what_you_get": [
                        "Official German patent data",
                        "Original German applicant names",
                        "Legal representatives",
                        "File history",
                        "Official documents"
                    ],
                    "how_to_search": [
                        "Go to register.dpma.de",
                        "Select 'Patent' search",
                        "Enter application number",
                        "Click 'Bibliographic data' for applicant",
                        "Check 'Verfahrensstand' for status"
                    ],
                    "language_note": "Interface in German but Chrome can translate"
                },

                "lens_org": {
                    "url": "https://www.lens.org",
                    "access": "FREE with registration",
                    "what_you_get": [
                        "Scholarly citations of patents",
                        "Institutional affiliations",
                        "Academic connections",
                        "Patent landscapes",
                        "Bulk data export (limited)"
                    ],
                    "how_to_search": [
                        "Create free account at lens.org",
                        "Search by patent number",
                        "View 'Institutions' tab",
                        "Check 'Scholarly Works' citing the patent",
                        "Export results as CSV"
                    ]
                },

                "patentscope_wipo": {
                    "url": "https://patentscope.wipo.int",
                    "access": "100% FREE",
                    "what_you_get": [
                        "International patent applications",
                        "PCT applications",
                        "National phase entries",
                        "Machine translations",
                        "Legal status"
                    ],
                    "how_to_search": [
                        "Go to patentscope.wipo.int",
                        "Search by German patent number",
                        "Check if PCT application exists",
                        "View 'National Phase' for other countries",
                        "Download full documents"
                    ]
                }
            },

            "entity_research_sources": {
                "gleif": {
                    "url": "https://search.gleif.org",
                    "purpose": "Verify company legal entities",
                    "what_you_get": "Legal entity identifiers, corporate structure",
                    "how": "Search company name from patent"
                },

                "opencorporates": {
                    "url": "https://opencorporates.com",
                    "purpose": "Company registration data",
                    "what_you_get": "Directors, addresses, filings",
                    "how": "Search German company names"
                },

                "unternehmensregister": {
                    "url": "https://www.unternehmensregister.de",
                    "purpose": "German company register",
                    "what_you_get": "Official German company data",
                    "how": "Search by company name (some docs are paid)"
                },

                "chinese_entity_search": {
                    "qcc_international": "https://www.qcc.com/english",
                    "purpose": "Chinese company information",
                    "limitation": "Limited free searches",
                    "alternative": "Search company name + 'China' in Google"
                }
            },

            "academic_collaboration_sources": {
                "google_scholar": {
                    "url": "https://scholar.google.com",
                    "how": "Search inventor names from patent",
                    "what_you_get": "Academic affiliations, research papers, co-authors"
                },

                "research_gate": {
                    "url": "https://www.researchgate.net",
                    "how": "Search inventor/researcher names",
                    "what_you_get": "Institutional affiliations, collaborations"
                },

                "orcid": {
                    "url": "https://orcid.org",
                    "how": "Search researcher names",
                    "what_you_get": "Verified researcher profiles, affiliations"
                },

                "semantic_scholar": {
                    "url": "https://www.semanticscholar.org",
                    "how": "Search author names or paper titles",
                    "what_you_get": "Co-authorship networks, institutional connections"
                }
            }
        }

        return methods

    def create_step_by_step_workflow(self):
        """Create detailed workflow for patent investigation"""

        workflow = {
            "step_1_initial_patent_search": {
                "time_required": "5-10 minutes per patent",
                "actions": [
                    {
                        "action": "Open Google Patents",
                        "url": "https://patents.google.com",
                        "search": "DE102024122387A1 (remove hyphens)",
                        "extract": [
                            "Current Assignee name",
                            "Original Assignee name",
                            "Inventor names and cities",
                            "Priority date and country",
                            "Application date"
                        ]
                    },
                    {
                        "action": "Cross-check on Espacenet",
                        "url": "https://worldwide.espacenet.com",
                        "verify": "Applicant names match",
                        "additional": "Check for PCT application"
                    },
                    {
                        "action": "German Patent Office",
                        "url": "https://register.dpma.de",
                        "verify": "Official German applicant",
                        "check": "Legal representative (often reveals connections)"
                    }
                ]
            },

            "step_2_entity_identification": {
                "time_required": "10-15 minutes per entity",
                "actions": [
                    {
                        "action": "Company verification",
                        "source": "GLEIF or OpenCorporates",
                        "search": "German company name from patent",
                        "extract": [
                            "Legal entity identifier (LEI)",
                            "Registered address",
                            "Parent company",
                            "Directors/officers"
                        ]
                    },
                    {
                        "action": "Chinese entity search",
                        "method": "Search for Chinese co-inventors or priority countries",
                        "sources": [
                            "Google: '[Inventor Name] China university'",
                            "Google: '[Company Name] China partnership'",
                            "Patent citations to Chinese patents"
                        ]
                    }
                ]
            },

            "step_3_collaboration_mapping": {
                "time_required": "15-20 minutes per patent",
                "actions": [
                    {
                        "action": "Academic collaboration check",
                        "source": "Google Scholar",
                        "search": "Inventor names from patent",
                        "look_for": [
                            "Joint papers with Chinese authors",
                            "Conference presentations in China",
                            "Visiting professor positions",
                            "Research grants"
                        ]
                    },
                    {
                        "action": "Corporate partnership search",
                        "method": "Google search combinations",
                        "searches": [
                            "'[German Company]' + 'China' + 'partnership'",
                            "'[German Company]' + 'Chinese' + 'joint venture'",
                            "'[German Company]' + '[Chinese University]'"
                        ]
                    }
                ]
            },

            "step_4_documentation": {
                "action": "Screenshot and save all findings",
                "organize": [
                    "Patent number folder",
                    "Screenshots of assignee info",
                    "Entity registration data",
                    "Collaboration evidence",
                    "Related patents"
                ]
            }
        }

        return workflow

    def generate_search_queries(self):
        """Generate specific search queries for the 3 priority patents"""

        queries = {
            "DE-102024122387-A1_autonomous": {
                "google_patents": "https://patents.google.com/patent/DE102024122387A1",
                "espacenet": "https://worldwide.espacenet.com/patent/search?q=pn%3DDE102024122387",
                "dpma": "https://register.dpma.de/DPMAregister/pat/register?AKZ=1020241223871",
                "entity_searches": [
                    "Google: 'autonomous driving' + 'German' + 'Chinese' + 'collaboration' + '2024'",
                    "Google: 'Volkswagen' OR 'BMW' OR 'Mercedes' + 'China' + 'autonomous' + '2024'",
                    "Scholar: Check inventor names for Chinese co-authors"
                ]
            },

            "DE-102024121951-A1_neural": {
                "google_patents": "https://patents.google.com/patent/DE102024121951A1",
                "espacenet": "https://worldwide.espacenet.com/patent/search?q=pn%3DDE102024121951",
                "dpma": "https://register.dpma.de/DPMAregister/pat/register?AKZ=1020241219511",
                "entity_searches": [
                    "Google: 'neural network' + 'German' + 'Chinese' + 'research' + '2024'",
                    "Scholar: Inventor names + 'neural network' + 'China'",
                    "Check: Max Planck Institute, Fraunhofer + China collaborations"
                ]
            },

            "DE-102023121476-A1_semiconductor": {
                "google_patents": "https://patents.google.com/patent/DE102023121476A1",
                "espacenet": "https://worldwide.espacenet.com/patent/search?q=pn%3DDE102023121476",
                "dpma": "https://register.dpma.de/DPMAregister/pat/register?AKZ=1020231214761",
                "entity_searches": [
                    "Google: 'Infineon' OR 'Bosch' + 'China' + 'semiconductor' + '2023'",
                    "Google: 'temperature sensor' + 'semiconductor' + 'German Chinese'",
                    "Check: SMIC, Huawei connections to German semiconductor companies"
                ]
            }
        }

        return queries

def main():
    guide = FreePatentSearchGuide()

    methods = guide.generate_search_methods()
    workflow = guide.create_step_by_step_workflow()
    queries = guide.generate_search_queries()

    # Save comprehensive guide
    full_guide = {
        "search_methods": methods,
        "workflow": workflow,
        "specific_queries": queries,
        "time_estimate": "2-3 hours for all 3 priority patents",
        "cost": "$0 - All sources are free"
    }

    output_file = guide.analysis_dir / "free_patent_search_guide.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(full_guide, f, indent=2, ensure_ascii=False)

    # Create actionable markdown guide
    guide_file = guide.analysis_dir / "HOW_TO_SEARCH_PATENTS_FREE.md"
    with open(guide_file, 'w', encoding='utf-8') as f:
        f.write("""# HOW TO SEARCH PATENT ENTITIES - 100% FREE & LEGAL

## Time Required: 30-45 minutes per patent
## Cost: $0

## QUICK START - Priority Patents

### 1. DE-102024122387-A1 (Autonomous Driving)
**Direct link:** https://patents.google.com/patent/DE102024122387A1

**What to extract:**
- Current Assignee (German company)
- Inventor names and locations
- Check if any Chinese names/locations
- Priority country (if China = red flag)

### 2. DE-102024121951-A1 (Neural Networks)
**Direct link:** https://patents.google.com/patent/DE102024121951A1

**What to extract:**
- Assignee/Applicant name
- Research institution if academic
- Inventor affiliations
- Related patents in family

### 3. DE-102023121476-A1 (Semiconductor Sensors)
**Direct link:** https://patents.google.com/patent/DE102023121476A1

**What to extract:**
- Semiconductor company name
- Technology classification codes
- Patent family countries
- Legal status

## STEP-BY-STEP PROCESS

### Step 1: Google Patents (5 minutes)
1. Click the direct link above
2. Click "Details" tab
3. Screenshot the Assignee field
4. Note all Inventor names and cities
5. Check Priority date/country
6. Download PDF for records

### Step 2: Verify on Espacenet (5 minutes)
1. Go to worldwide.espacenet.com
2. Paste patent number
3. Click "Biblio. data"
4. Verify applicant matches Google Patents
5. Check "Patent family" for other countries

### Step 3: Company Research (10 minutes)
1. Search company name on:
   - https://opencorporates.com (free company data)
   - https://search.gleif.org (legal entity verification)
2. Google: "[Company Name] China partnership"
3. Check company website for China offices/partnerships

### Step 4: Academic/Inventor Search (10 minutes)
1. Google Scholar: Search each inventor name
2. Look for:
   - Papers with Chinese co-authors
   - Chinese institutional affiliations
   - Conferences in China
3. ResearchGate: Check inventor profiles

### Step 5: Documentation (5 minutes)
1. Create folder for patent number
2. Save screenshots of:
   - Patent assignee info
   - Company registration
   - Any China connections found
3. Write brief summary

## WHAT YOU'RE LOOKING FOR

### 🔴 RED FLAGS (High Concern)
- Chinese co-applicants or co-assignees
- Priority claim from China
- Chinese inventors listed
- German company with known China JV

### 🟡 YELLOW FLAGS (Moderate Concern)
- Inventors with Chinese university affiliations
- Patent family includes China filings
- German company with China operations
- Technology areas matching China's strategic priorities

### 🟢 GREEN FLAGS (Lower Concern)
- Only German/EU entities
- No China patent family members
- Established German company without China presence
- Consumer/commercial focus only

## FREE TOOLS SUMMARY

| Tool | URL | What You Get |
|------|-----|--------------|
| Google Patents | patents.google.com | Full patent text, assignees, inventors |
| Espacenet | worldwide.espacenet.com | European patent data, families |
| DPMA Register | register.dpma.de | Official German patent data |
| Lens.org | lens.org | Academic connections (free account) |
| OpenCorporates | opencorporates.com | Company information |
| GLEIF | search.gleif.org | Legal entity verification |
| Google Scholar | scholar.google.com | Academic affiliations |

## TOTAL TIME: 2-3 hours for all 3 patents
## TOTAL COST: $0

Start with Google Patents - it has everything you need for initial assessment!
""")

    print("[+] Free patent search guide created")
    print("[+] All methods are 100% legal and free")
    print(f"[+] Guide saved to: {guide_file}")
    print(f"[+] Detailed methods: {output_file}")
    print("\n[*] Estimated time: 30-45 minutes per patent")
    print("[*] Total cost: $0")

if __name__ == "__main__":
    main()

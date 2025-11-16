"""
BCI Ecosystem Patent Analysis Framework
========================================
Identifies Chinese patents across BCI and related ecosystem technologies.

Purpose:
- Track Chinese patent filings for BCI enabling technologies (graphene, optogenetics, FUS)
- Track Chinese patents for BCI derivative applications (neural swarms, brain-to-brain)
- Detect technology transfer (EU research → Chinese patents)
- Identify PLA-affiliated patent assignees

Created: 2025-10-26
Database: F:/USPTO Data/ (66GB XML files)
"""

import json
from pathlib import Path
from typing import Dict, List, Set

# ============================================================================
# CONFIGURATION
# ============================================================================

# CPC Classification Codes for BCI Ecosystem Technologies
CPC_CODES = {
    "BCI_Core": [
        "A61B5/04",      # EEG, brain signals
        "A61B5/0476",    # EEG recording
        "A61B5/0478",    # Brain mapping
        "A61B5/055",     # MRI for brain imaging
        "G06F3/015",     # Brain-computer interfaces for human-machine interaction
        "A61N1/36",      # Neurostimulation
    ],

    "Graphene_Electrodes": [
        "A61B5/04",      # EEG electrodes
        "A61B5/0408",    # EEG electrode arrangements
        "A61N1/05",      # Electrodes for neurostimulation
        "H01L29/16",     # Graphene semiconductor devices
        "H01B1/04",      # Conductive materials (graphene)
    ],

    "Optogenetics": [
        "A61N5/06",      # Light therapy
        "A61N5/067",     # Irradiation of brain
        "C12N15/867",    # Recombinant DNA (light-sensitive proteins)
        "C07K14/47",     # Rhodopsins (channelrhodopsin, halorhodopsin)
    ],

    "Focused_Ultrasound": [
        "A61N7/00",      # Ultrasound therapy
        "A61N7/02",      # Localized ultrasound (focused ultrasound)
        "A61B8/08",      # Ultrasound imaging and therapy combined
        "A61B17/22",     # Ultrasound surgical systems
    ],

    "Neural_Dust_Wireless": [
        "A61B5/0031",    # Implantable sensors
        "A61B5/00",      # Medical sensors
        "H02J50/23",     # Wireless power transfer to implants
        "H04Q9/00",      # Wireless telemetry
        "A61B5/07",      # Piezoelectric sensors
    ],

    "Neural_Prosthetics": [
        "A61F2/70",      # Prosthetic neural interfaces
        "A61F2/72",      # Peripheral nerve prosthetics
        "B25J9/16",      # Robot control via neural interfaces
        "A61B5/24",      # Detecting/recording bioelectric signals for prosthetic control
    ],

    "Brain_to_Brain": [
        "G06F3/015",     # Brain-computer interfaces
        "A61N1/36",      # TMS for brain-to-brain
        "H04M3/56",      # Neural communication systems (synthetic telepathy)
    ],

    "Neural_Swarm_Control": [
        "G05D1/00",      # Robot control systems
        "G05D1/02",      # Multi-robot coordination
        "B64C39/02",     # Unmanned aerial vehicles (drones)
        "G06F3/015",     # Brain-computer interface control
    ],

    "TMS_tDCS": [
        "A61N1/36",      # Transcranial magnetic stimulation
        "A61N1/40",      # Transcranial direct current stimulation
        "A61N2/00",      # Magnetic field therapy
    ],

    "Neural_Authentication": [
        "G06F21/32",     # Biometric authentication
        "A61B5/04",      # EEG recording for authentication
        "G06K9/00",      # Pattern recognition (brainwave patterns)
    ]
}

# Keywords for technology-specific searches
TECHNOLOGY_KEYWORDS = {
    "Graphene_Electrodes": [
        "graphene electrode",
        "graphene neural",
        "carbon nanotube electrode",
        "flexible electrode",
        "biocompatible electrode"
    ],

    "Optogenetics": [
        "optogenetic",
        "channelrhodopsin",
        "halorhodopsin",
        "light-activated neuron",
        "optical neural control"
    ],

    "Focused_Ultrasound": [
        "focused ultrasound",
        "transcranial focused ultrasound",
        "tFUS",
        "ultrasound neuromodulation",
        "ultrasonic brain"
    ],

    "Neural_Dust": [
        "neural dust",
        "ultrasound-powered implant",
        "wireless neural sensor",
        "neurograins",
        "piezoelectric neural"
    ],

    "Brain_to_Brain": [
        "brain-to-brain",
        "brain to brain",
        "synthetic telepathy",
        "neural telepathy",
        "direct brain communication"
    ],

    "Neural_Swarm": [
        "neural swarm",
        "brain-controlled swarm",
        "thought-controlled drone",
        "multi-robot brain control",
        "swarm" + "brain-computer"
    ],

    "TMS_tDCS": [
        "transcranial magnetic stimulation",
        "transcranial direct current",
        "non-invasive brain stimulation"
    ],

    "Neural_Authentication": [
        "brainwave biometric",
        "neural authentication",
        "eeg authentication",
        "brain-based authentication"
    ]
}

# PLA-affiliated assignee patterns (partial match)
PLA_PATTERNS = [
    "People's Liberation Army",
    "PLA",
    "Military Medical",
    "Academy of Military",
    "National Defense",
    "China Aerospace Science",
    "China Electronics Technology Corporation",
    "CETC",
    "Academy of Military Sciences"
]

# ============================================================================
# PATENT SEARCH TEMPLATES
# ============================================================================

def generate_uspto_search_query(technology: str, cpc_codes: List[str], keywords: List[str]) -> str:
    """
    Generate USPTO patent search query for specific technology.

    Args:
        technology: Technology name (e.g., "Graphene_Electrodes")
        cpc_codes: List of CPC classification codes
        keywords: List of keyword phrases to search

    Returns:
        USPTO search query string
    """

    # CPC query part
    cpc_query = " OR ".join([f"CPC:{code}" for code in cpc_codes])

    # Keyword query part
    keyword_query = " OR ".join([f'"{kw}"' for kw in keywords])

    # Chinese assignee filter
    assignee_filter = "AN/CN"  # Assignee country = China

    query = f"""
    Technology: {technology}

    Search Query:
    ({cpc_query}) AND ({keyword_query}) AND ({assignee_filter})

    Date Range: 2000-01-01 to 2025-12-31

    Fields to Extract:
    - Patent Number
    - Title
    - Abstract
    - Assignee Name
    - Assignee Country
    - Filing Date
    - Grant Date (if granted)
    - CPC Codes
    - Inventors
    - Inventor Locations
    - Citations (to detect EU research citations)
    """

    return query


def generate_epo_search_query(technology: str, cpc_codes: List[str], keywords: List[str]) -> str:
    """
    Generate EPO patent search query for specific technology.

    Args:
        technology: Technology name
        cpc_codes: List of CPC classification codes
        keywords: List of keyword phrases

    Returns:
        EPO OPS API query string
    """

    # EPO uses CQL (Common Query Language)
    cpc_query = " or ".join([f"cpc={code}" for code in cpc_codes])
    keyword_query = " or ".join([f'ti="{kw}" or ab="{kw}"' for kw in keywords])

    query = f"""
    Technology: {technology}

    EPO OPS Query:
    ({cpc_query}) and ({keyword_query}) and pa=CN

    Date Range: pd within "20000101,20251231"

    Fields:
    - Publication number
    - Title (en, zh)
    - Abstract (en, zh)
    - Applicant
    - Inventor
    - Filing date
    - Publication date
    - Classifications
    - Citations
    """

    return query


# ============================================================================
# ANALYSIS FUNCTIONS
# ============================================================================

def detect_pla_affiliation(assignee_name: str) -> bool:
    """
    Detect if patent assignee is PLA-affiliated.

    Args:
        assignee_name: Patent assignee/applicant name

    Returns:
        True if PLA-affiliated, False otherwise
    """
    assignee_lower = assignee_name.lower()

    for pattern in PLA_PATTERNS:
        if pattern.lower() in assignee_lower:
            return True

    return False


def analyze_citation_timeline(patent_filing_date: str, cited_papers: List[Dict]) -> Dict:
    """
    Analyze if patent cites EU research and filing timeline.

    Args:
        patent_filing_date: Patent filing date (YYYY-MM-DD)
        cited_papers: List of cited research papers

    Returns:
        Analysis dict with potential technology transfer indicators
    """

    analysis = {
        "cites_eu_research": False,
        "eu_citations_count": 0,
        "shortest_gap_days": None,
        "suspicious_timeline": False,  # Filed <2 years after EU publication
        "cited_papers": []
    }

    # Implementation would check cited_papers for EU affiliations
    # and calculate time gap between publication and patent filing

    return analysis


def generate_patent_report(technology: str, patent_data: List[Dict]) -> str:
    """
    Generate intelligence report for Chinese patents in technology area.

    Args:
        technology: Technology name
        patent_data: List of patent records

    Returns:
        Markdown formatted intelligence report
    """

    total_patents = len(patent_data)
    pla_patents = sum(1 for p in patent_data if detect_pla_affiliation(p.get('assignee', '')))

    report = f"""
# Chinese Patent Analysis: {technology}

**Date:** 2025-10-26
**Total Patents:** {total_patents}
**PLA-Affiliated:** {pla_patents} ({100*pla_patents/total_patents:.1f}%)

## Summary Statistics

- **Filing Trend:** [Implement temporal analysis]
- **Top Assignees:** [Extract top 10]
- **Geographic Distribution:** [Chinese city/province]
- **Technology Subcategories:** [CPC code breakdown]

## Key Findings

### PLA-Affiliated Patents
[List PLA-affiliated patents with titles and assignees]

### Recent Filings (2023-2025)
[List most recent patents - indicate emerging areas]

### Technology Transfer Indicators
[Patents citing EU research within 2 years]

## Intelligence Assessment

**Risk Level:** [HIGH/MEDIUM/LOW based on PLA involvement, filing growth]
**Technology Maturity:** [Based on patent claims, figures]
**Military Application Potential:** [Assess dual-use potential]

## Recommended Actions

1. [Specific follow-up based on findings]
2. [e.g., Track specific Chinese companies]
3. [e.g., Alert European researchers citing in this area]
    """

    return report


# ============================================================================
# MAIN EXECUTION TEMPLATES
# ============================================================================

def main_search_workflow():
    """
    Main workflow for BCI ecosystem patent searches.

    NOTE: This is a template/framework. Actual USPTO XML parsing
    requires separate implementation using existing project scripts.
    """

    print("BCI Ecosystem Patent Analysis Framework")
    print("=" * 60)
    print()

    # Generate search queries for all technologies
    for tech_name, cpc_codes in CPC_CODES.items():
        keywords = TECHNOLOGY_KEYWORDS.get(tech_name, [])

        print(f"\n{'='*60}")
        print(f"Technology: {tech_name}")
        print(f"{'='*60}")

        # USPTO Query
        print("\n--- USPTO Search Query ---")
        uspto_query = generate_uspto_search_query(tech_name, cpc_codes, keywords)
        print(uspto_query)

        # EPO Query
        print("\n--- EPO Search Query ---")
        epo_query = generate_epo_search_query(tech_name, cpc_codes, keywords)
        print(epo_query)

    print("\n" + "="*60)
    print("NEXT STEPS:")
    print("="*60)
    print("1. Use existing USPTO XML parser to extract patents matching CPC codes")
    print("2. Filter by Chinese assignees (AN/CN)")
    print("3. Apply keyword filtering to titles/abstracts")
    print("4. Check assignee names against PLA patterns")
    print("5. Cross-reference with OpenAlex publications (citation analysis)")
    print("6. Generate technology-specific intelligence reports")
    print()
    print("Database Locations:")
    print("  USPTO: F:/USPTO Data/ (66GB XML)")
    print("  Output: analysis/bci_ecosystem_patents_[technology]_[date].json")


# ============================================================================
# INTEGRATION WITH EXISTING SCRIPTS
# ============================================================================

"""
Integration Points:

1. USPTO XML Parser:
   - Use existing scripts in scripts/collectors/
   - Modify to accept CPC code filters
   - Add Chinese assignee detection

2. OpenAlex Cross-Reference:
   - Query OpenAlex for papers published 1-3 years before patent filing
   - Check if patent cites OpenAlex papers
   - Flag EU authors → Chinese patents timeline

3. Database Schema:
   CREATE TABLE bci_ecosystem_patents (
       patent_id TEXT PRIMARY KEY,
       patent_number TEXT,
       title TEXT,
       abstract TEXT,
       technology_area TEXT,  -- From CPC_CODES keys
       assignee_name TEXT,
       assignee_country TEXT,
       pla_affiliated BOOLEAN,
       filing_date TEXT,
       grant_date TEXT,
       cpc_codes TEXT,  -- JSON array
       keywords_matched TEXT,  -- JSON array
       cites_eu_research BOOLEAN,
       eu_papers_cited TEXT,  -- JSON array of DOIs
       days_after_publication INTEGER,  -- Fastest EU paper → patent gap
       created_at TEXT
   );

4. Monitoring Dashboard:
   - Monthly updates: New Chinese BCI ecosystem patents
   - Alert: PLA-affiliated patents
   - Alert: Patents filed <1 year after EU publication
   - Trend: YoY growth by technology area
"""


if __name__ == "__main__":
    # Print framework documentation and search templates
    main_search_workflow()

    print("\n" + "="*60)
    print("PRIORITY EXECUTION ORDER")
    print("="*60)
    print()
    print("IMMEDIATE (Week 1):")
    print("  1. Graphene_Electrodes (HIGH Chinese activity)")
    print("  2. Focused_Ultrasound (VERY HIGH Chinese activity 2020-2025)")
    print("  3. Neural_Swarm_Control (CRITICAL military application)")
    print()
    print("SHORT-TERM (Weeks 2-3):")
    print("  4. Optogenetics (PLA involvement)")
    print("  5. Neural_Dust_Wireless (Watch for Chinese catch-up)")
    print("  6. BCI_Core (baseline for ecosystem comparison)")
    print()
    print("MEDIUM-TERM (Month 2):")
    print("  7. Neural_Prosthetics")
    print("  8. Brain_to_Brain")
    print("  9. Neural_Authentication")
    print(" 10. TMS_tDCS")
    print()
    print("Run this script to generate search queries, then execute")
    print("USPTO/EPO searches using existing patent processing pipeline.")

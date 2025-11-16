#!/usr/bin/env python3
"""
OSINT Foresight Data Audit - Phase 6: Usability & Analysis Readiness
Creates query cookbooks, integration recipes, and usability profiles
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

output_dir = Path("C:/Projects/OSINT - Foresight/audit_outputs")
output_dir.mkdir(exist_ok=True)

print("="*80)
print("PHASE 6: USABILITY & ANALYSIS READINESS")
print("="*80)
print()

# Primary database
db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
conn = sqlite3.connect(db_path, timeout=30)
cursor = conn.cursor()

# ============================================================================
# Task 1: Query Cookbook - Common Analysis Patterns
# ============================================================================

print("TASK 1: QUERY COOKBOOK GENERATION")
print("-" * 40)

query_cookbook = {
    "metadata": {
        "created": datetime.now().isoformat(),
        "database": db_path,
        "description": "Common query patterns for OSINT analysis"
    },
    "queries": []
}

# Query 1: Top Chinese entities by dataset
query_cookbook["queries"].append({
    "id": "Q1",
    "name": "Top Chinese Entities by Dataset",
    "description": "Find top 10 Chinese entities across USAspending, patents, research",
    "use_case": "Entity intelligence - Who are the major Chinese players?",
    "queries": {
        "usaspending": """
SELECT
    recipient_name,
    COUNT(*) as contracts,
    SUM(federal_action_obligation) as total_value,
    MIN(action_date) as first_contract,
    MAX(action_date) as latest_contract
FROM usaspending_china_374
WHERE recipient_name IS NOT NULL
GROUP BY recipient_name
ORDER BY total_value DESC
LIMIT 10;
        """,
        "uspto": """
SELECT
    assignee_name,
    COUNT(*) as patents,
    MIN(grant_date) as first_patent,
    MAX(grant_date) as latest_patent
FROM uspto_patents_chinese
WHERE assignee_name IS NOT NULL
GROUP BY assignee_name
ORDER BY patents DESC
LIMIT 10;
        """,
        "openalex": """
SELECT
    institution_name,
    country_code,
    COUNT(*) as papers
FROM openalex_work_authors
WHERE country_code = 'CN'
GROUP BY institution_name, country_code
ORDER BY papers DESC
LIMIT 10;
        """
    },
    "expected_output": "Top 10 entities with contract/patent/paper counts and date ranges",
    "caveats": [
        "USAspending: Filtered subset (Chinese detections only)",
        "USPTO: Only Chinese-origin patents (not all assignees)",
        "OpenAlex: Strategic tech subset only"
    ]
})

# Query 2: Temporal trends
query_cookbook["queries"].append({
    "id": "Q2",
    "name": "Chinese Entity Activity Over Time",
    "description": "Track growth/decline in Chinese entity presence by year",
    "use_case": "Temporal analysis - Is Chinese activity increasing?",
    "queries": {
        "usaspending_by_year": """
SELECT
    strftime('%Y', action_date) as year,
    COUNT(*) as contracts,
    SUM(federal_action_obligation) as total_value
FROM usaspending_china_374
WHERE action_date IS NOT NULL
GROUP BY year
ORDER BY year;
        """,
        "uspto_by_year": """
SELECT
    strftime('%Y', grant_date) as year,
    COUNT(*) as patents,
    COUNT(DISTINCT assignee_name) as unique_assignees
FROM uspto_patents_chinese
WHERE grant_date IS NOT NULL
GROUP BY year
ORDER BY year;
        """,
        "openalex_by_year": """
SELECT
    publication_year as year,
    COUNT(*) as papers,
    COUNT(DISTINCT institution_name) as unique_institutions
FROM openalex_works
WHERE publication_year IS NOT NULL
GROUP BY year
ORDER BY year;
        """
    },
    "expected_output": "Year-by-year counts showing temporal trends",
    "caveats": [
        "Different date ranges across datasets",
        "Recent years may be incomplete (publication lag)"
    ]
})

# Query 3: Cross-dataset entity lookup
query_cookbook["queries"].append({
    "id": "Q3",
    "name": "Single Entity Across All Datasets",
    "description": "Find all occurrences of a specific entity (e.g., Huawei)",
    "use_case": "Entity profiling - Complete picture of one company",
    "queries": {
        "usaspending_huawei": """
SELECT
    recipient_name,
    COUNT(*) as contracts,
    SUM(federal_action_obligation) as total_value
FROM usaspending_china_374
WHERE recipient_name LIKE '%HUAWEI%'
GROUP BY recipient_name;
        """,
        "uspto_huawei": """
SELECT
    assignee_name,
    COUNT(*) as patents,
    MIN(grant_date) as first_patent,
    MAX(grant_date) as latest_patent
FROM uspto_patents_chinese
WHERE assignee_name LIKE '%HUAWEI%'
GROUP BY assignee_name;
        """,
        "ted_huawei": """
SELECT
    contractor_name,
    COUNT(*) as contracts
FROM ted_contractors
WHERE contractor_name LIKE '%HUAWEI%'
GROUP BY contractor_name;
        """
    },
    "expected_output": "All instances of entity across datasets with name variations",
    "caveats": [
        "Name variations may require multiple searches",
        "Subsidiary names may differ from parent"
    ]
})

# Query 4: Geographic distribution
query_cookbook["queries"].append({
    "id": "Q4",
    "name": "Chinese Collaboration Partners by Country",
    "description": "Which countries collaborate most with Chinese entities?",
    "use_case": "Geographic analysis - International partnerships",
    "queries": {
        "openalex_collaborations": """
SELECT
    a1.country_code as partner_country,
    COUNT(DISTINCT a1.work_id) as joint_papers
FROM openalex_work_authors a1
JOIN openalex_work_authors a2 ON a1.work_id = a2.work_id
WHERE a2.country_code = 'CN'
  AND a1.country_code != 'CN'
  AND a1.country_code IS NOT NULL
GROUP BY a1.country_code
ORDER BY joint_papers DESC;
        """
    },
    "expected_output": "Countries ranked by collaboration volume with China",
    "caveats": [
        "Only captures research collaborations",
        "Does not include procurement/commercial relationships"
    ]
})

# Query 5: Technology domain analysis
query_cookbook["queries"].append({
    "id": "Q5",
    "name": "Chinese Activity by Technology Domain",
    "description": "Which technologies have most Chinese involvement?",
    "use_case": "Technology intelligence - Where is China focused?",
    "queries": {
        "openalex_topics": """
SELECT
    t.topic_name,
    COUNT(DISTINCT w.work_id) as papers_with_chinese_authors
FROM openalex_work_topics t
JOIN openalex_works w ON t.work_id = w.work_id
JOIN openalex_work_authors a ON w.work_id = a.work_id
WHERE a.country_code = 'CN'
GROUP BY t.topic_name
ORDER BY papers_with_chinese_authors DESC
LIMIT 20;
        """,
        "arxiv_categories": """
SELECT
    c.category,
    COUNT(DISTINCT c.arxiv_id) as papers
FROM arxiv_categories c
GROUP BY c.category
ORDER BY papers DESC
LIMIT 20;
        """
    },
    "expected_output": "Technology domains ranked by Chinese involvement",
    "caveats": [
        "Topic classifications may overlap",
        "arXiv query shows all papers (not Chinese-specific without additional filtering)"
    ]
})

print(f"  Generated {len(query_cookbook['queries'])} query patterns")
for q in query_cookbook['queries']:
    print(f"    {q['id']}: {q['name']}")

# Save query cookbook
with open(output_dir / "query_cookbook.json", "w", encoding='utf-8') as f:
    json.dump(query_cookbook, f, indent=2, ensure_ascii=False)

print(f"\n[SAVED] query_cookbook.json")

# ============================================================================
# Task 2: Data Quality Caveats by Dataset
# ============================================================================

print("\n" + "="*80)
print("TASK 2: DATA QUALITY CAVEATS")
print("-" * 40)

data_caveats = {
    "metadata": {
        "created": datetime.now().isoformat(),
        "purpose": "Critical warnings for each dataset"
    },
    "datasets": {}
}

# USAspending caveats
data_caveats["datasets"]["usaspending_china_374"] = {
    "dataset_name": "USAspending Chinese Entity Contracts",
    "row_count": 42205,
    "caveats": [
        {
            "severity": "CRITICAL",
            "issue": "This is a FILTERED SUBSET, not complete USAspending",
            "impact": "Only contracts detected with Chinese entity indicators included",
            "mitigation": "Cannot calculate market share or % of total federal spending"
        },
        {
            "severity": "HIGH",
            "issue": "Detection-based false positives confirmed",
            "impact": "PRI-DJI entities ($1.65B) incorrectly classified as Chinese",
            "mitigation": "Verify entity origin before analysis - check recipient_country_code"
        },
        {
            "severity": "HIGH",
            "issue": "Placeholder entities mask true recipients",
            "impact": "14,739 contracts ($5.2B) labeled 'MISCELLANEOUS FOREIGN AWARDEES'",
            "mitigation": "Exclude placeholder entities or note data quality in analysis"
        },
        {
            "severity": "MEDIUM",
            "issue": "Hong Kong classification ambiguous",
            "impact": "$235M in HK university contracts - PRC or separate?",
            "mitigation": "Decide on HK treatment based on research question"
        },
        {
            "severity": "LOW",
            "issue": "Missing 1998 data",
            "impact": "One year gap in 1997-2025 range",
            "mitigation": "Note gap in temporal analyses"
        }
    ],
    "recommendations": [
        "Always check recipient_country_code to verify entity origin",
        "Filter out placeholder entities (MISCELLANEOUS, MULTIPLE RECIPIENTS)",
        "Document Hong Kong treatment in methodology",
        "Validate high-value detections manually"
    ]
}

# TED caveats
data_caveats["datasets"]["ted_contracts_production"] = {
    "dataset_name": "TED EU Procurement Contracts",
    "row_count": 1131420,
    "caveats": [
        {
            "severity": "HIGH",
            "issue": "60% NULL contractor names",
            "impact": "683,182 contracts have no contractor identified",
            "mitigation": "Filter WHERE contractor_name IS NOT NULL for entity analysis"
        },
        {
            "severity": "MEDIUM",
            "issue": "System artifacts in data",
            "impact": "514 records are 'Infructueux' (unsuccessful) or 'Sans suite' (no follow-up)",
            "mitigation": "Exclude these pseudo-entities from contractor analysis"
        },
        {
            "severity": "MEDIUM",
            "issue": "No Chinese entities detected in top 100",
            "impact": "Either low Chinese presence or detection issue",
            "mitigation": "Investigate European subsidiaries of Chinese companies"
        },
        {
            "severity": "LOW",
            "issue": "Heavy pharmaceutical bias in top contractors",
            "impact": "May not represent overall EU procurement patterns",
            "mitigation": "Sample may be skewed toward certain sectors"
        }
    ],
    "recommendations": [
        "Always filter for non-NULL contractor names",
        "Exclude French system artifacts (Infructueux, Sans suite)",
        "Consider manual search for Chinese subsidiary names",
        "Verify sector distribution matches research scope"
    ]
}

# USPTO caveats
data_caveats["datasets"]["uspto_patents_chinese"] = {
    "dataset_name": "USPTO Chinese-Origin Patents",
    "row_count": 425074,
    "caveats": [
        {
            "severity": "CRITICAL",
            "issue": "LIMITED TEMPORAL RANGE: 2015-2024 only",
            "impact": "Missing 14 years of recent patent history (2001-2014)",
            "mitigation": "Cannot analyze long-term trends or compare to pre-2015 baseline"
        },
        {
            "severity": "HIGH",
            "issue": "This is Chinese-detected subset, not all USPTO",
            "impact": "Only patents with Chinese entity indicators included",
            "mitigation": "Cannot calculate Chinese % of total USPTO patents"
        },
        {
            "severity": "MEDIUM",
            "issue": "16.8% NULL patent numbers",
            "impact": "71,424 records are applications without granted patent numbers",
            "mitigation": "Filter WHERE patent_number IS NOT NULL for granted patents only"
        },
        {
            "severity": "MEDIUM",
            "issue": "Taiwan entities may be included",
            "impact": "Hon Hai (Foxconn) 6,829 patents - Taiwan company, not PRC",
            "mitigation": "Verify entity nationality for Taiwan/HK companies"
        },
        {
            "severity": "LOW",
            "issue": "Multiple name variations for same entity",
            "impact": "China Star Optoelectronics appears under 3+ name variations",
            "mitigation": "Group by normalized names for accurate entity counts"
        }
    ],
    "recommendations": [
        "DO NOT use for long-term trend analysis (only 10 years coverage)",
        "Verify Taiwan vs PRC classification for major entities",
        "Filter NULL patent_number for granted-only analysis",
        "Normalize entity names before aggregation"
    ]
}

# OpenAlex caveats
data_caveats["datasets"]["openalex_works"] = {
    "dataset_name": "OpenAlex Strategic Tech Research",
    "row_count": 17739,
    "caveats": [
        {
            "severity": "CRITICAL",
            "issue": "HEAVILY FILTERED SUBSET - strategic tech keywords/topics only",
            "impact": "Not representative of all research, only targeted domains",
            "mitigation": "Cannot calculate % of all research or make general claims"
        },
        {
            "severity": "MEDIUM",
            "issue": "37% NULL DOIs",
            "impact": "6,561 papers lack DOI for cross-referencing",
            "mitigation": "Cannot link to all external databases via DOI"
        },
        {
            "severity": "LOW",
            "issue": "Historical coverage back to 1861",
            "impact": "Very old papers may be digitization artifacts",
            "mitigation": "Consider filtering to modern research (e.g., post-1990)"
        }
    ],
    "recommendations": [
        "Always note this is strategic tech subset in analysis",
        "Do not calculate percentages against 'all research'",
        "Use title/abstract search as fallback when DOI missing",
        "Consider temporal filtering for modern research focus"
    ]
}

# arXiv caveats
data_caveats["datasets"]["arxiv_papers"] = {
    "dataset_name": "arXiv Research Papers",
    "row_count": 1443097,
    "caveats": [
        {
            "severity": "MEDIUM",
            "issue": "Preprint repository, not peer-reviewed",
            "impact": "Quality varies, may include non-validated research",
            "mitigation": "Note preprint status in methodology"
        },
        {
            "severity": "LOW",
            "issue": "Physics/CS/Math bias",
            "impact": "arXiv coverage strongest in these domains",
            "mitigation": "May not represent other scientific fields"
        }
    ],
    "recommendations": [
        "Cross-reference with peer-reviewed sources when possible",
        "Note arXiv disciplinary bias in multi-domain analyses"
    ]
}

# GLEIF caveats
data_caveats["datasets"]["gleif_entities"] = {
    "dataset_name": "GLEIF Legal Entity Identifiers",
    "row_count": 3086233,
    "caveats": [
        {
            "severity": "HIGH",
            "issue": "Schema issues detected in Phase 4",
            "impact": "Column 'registration_authority' not found - query failed",
            "mitigation": "Verify schema before querying, update scripts"
        },
        {
            "severity": "MEDIUM",
            "issue": "Not linked to other datasets",
            "impact": "LEI not used for entity resolution in Phase 4",
            "mitigation": "Implement LEI matching for cross-dataset entity resolution"
        }
    ],
    "recommendations": [
        "Verify schema with PRAGMA table_info before querying",
        "Use for entity resolution - link USAspending/TED/USPTO entities via LEI"
    ]
}

print(f"  Generated caveats for {len(data_caveats['datasets'])} datasets")
for dataset, info in data_caveats['datasets'].items():
    critical_count = sum(1 for c in info['caveats'] if c['severity'] == 'CRITICAL')
    print(f"    {dataset}: {len(info['caveats'])} caveats ({critical_count} CRITICAL)")

# Save caveats
with open(output_dir / "data_quality_caveats.json", "w", encoding='utf-8') as f:
    json.dump(data_caveats, f, indent=2, ensure_ascii=False)

print(f"\n[SAVED] data_quality_caveats.json")

# ============================================================================
# Task 3: Integration Recipes for Cross-Dataset Queries
# ============================================================================

print("\n" + "="*80)
print("TASK 3: CROSS-DATASET INTEGRATION RECIPES")
print("-" * 40)

integration_recipes = {
    "metadata": {
        "created": datetime.now().isoformat(),
        "description": "Recipes for combining multiple datasets"
    },
    "recipes": []
}

# Recipe 1: Entity 360° profile
integration_recipes["recipes"].append({
    "id": "R1",
    "name": "Entity 360° Profile",
    "description": "Complete profile of entity across all datasets",
    "use_case": "Deep dive on single company (e.g., Huawei)",
    "steps": [
        {
            "step": 1,
            "action": "Identify entity name variations",
            "query": "SELECT DISTINCT assignee_name FROM uspto_patents_chinese WHERE assignee_name LIKE '%HUAWEI%'",
            "output": "List of all name variations (Huawei Technologies, Huawei Tech Co Ltd, etc.)"
        },
        {
            "step": 2,
            "action": "Get patent portfolio",
            "query": "SELECT COUNT(*), MIN(grant_date), MAX(grant_date) FROM uspto_patents_chinese WHERE assignee_name LIKE '%HUAWEI%'",
            "output": "Patent count and date range"
        },
        {
            "step": 3,
            "action": "Get US government contracts",
            "query": "SELECT COUNT(*), SUM(federal_action_obligation) FROM usaspending_china_374 WHERE recipient_name LIKE '%HUAWEI%'",
            "output": "Contract count and total value"
        },
        {
            "step": 4,
            "action": "Get research output",
            "query": "Manual search needed - OpenAlex doesn't have Huawei as institution",
            "output": "Research paper count (if corporate research lab exists)"
        },
        {
            "step": 5,
            "action": "Get EU procurement",
            "query": "SELECT COUNT(*) FROM ted_contractors WHERE contractor_name LIKE '%HUAWEI%'",
            "output": "EU contract count"
        }
    ],
    "integration_method": "Manual aggregation across queries",
    "challenges": [
        "Name variations require fuzzy matching",
        "No common identifier (LEI not used)",
        "Different entity types (parent vs subsidiaries)"
    ]
})

# Recipe 2: Temporal comparison across datasets
integration_recipes["recipes"].append({
    "id": "R2",
    "name": "Chinese Activity Timeline",
    "description": "Track Chinese entity activity trends across all datasets",
    "use_case": "Is Chinese involvement increasing over time?",
    "steps": [
        {
            "step": 1,
            "action": "Extract USAspending by year",
            "query": "SELECT strftime('%Y', action_date) as year, COUNT(*), SUM(federal_action_obligation) FROM usaspending_china_374 GROUP BY year",
            "output": "Contracts and spending by year"
        },
        {
            "step": 2,
            "action": "Extract USPTO by year",
            "query": "SELECT strftime('%Y', grant_date) as year, COUNT(*) FROM uspto_patents_chinese GROUP BY year",
            "output": "Patents by year"
        },
        {
            "step": 3,
            "action": "Extract OpenAlex by year",
            "query": "SELECT publication_year, COUNT(*) FROM openalex_works w JOIN openalex_work_authors a ON w.work_id = a.work_id WHERE a.country_code = 'CN' GROUP BY publication_year",
            "output": "Papers with Chinese authors by year"
        },
        {
            "step": 4,
            "action": "Merge in Excel/Python",
            "method": "Export each query to CSV, join on year column",
            "output": "Combined timeline with all metrics"
        }
    ],
    "integration_method": "Export + manual merge (no SQL join across tables)",
    "challenges": [
        "Different date ranges (USPTO only 2015+)",
        "Different units (contracts vs patents vs papers)",
        "No automated cross-dataset query"
    ],
    "visualization": "Multi-line chart with year on X-axis, normalized metrics on Y-axis"
})

# Recipe 3: Technology domain focus
integration_recipes["recipes"].append({
    "id": "R3",
    "name": "Chinese Technology Domain Analysis",
    "description": "Which technologies have highest Chinese concentration?",
    "use_case": "Technology intelligence - Where is China investing?",
    "steps": [
        {
            "step": 1,
            "action": "Get patent technology classes",
            "query": "SELECT cpc_class, COUNT(*) FROM patentsview_cpc_strategic JOIN uspto_patents_chinese USING (patent_id) GROUP BY cpc_class ORDER BY COUNT(*) DESC",
            "output": "Top CPC classes in Chinese patents"
        },
        {
            "step": 2,
            "action": "Get research topics",
            "query": "SELECT topic_name, COUNT(*) FROM openalex_work_topics t JOIN openalex_work_authors a USING (work_id) WHERE a.country_code = 'CN' GROUP BY topic_name",
            "output": "Top research topics from Chinese institutions"
        },
        {
            "step": 3,
            "action": "Get arXiv categories",
            "query": "Manual - arXiv doesn't have author nationality field",
            "output": "Would require author institution → country mapping"
        },
        {
            "step": 4,
            "action": "Map to ASPI Critical Tech domains",
            "method": "Manual mapping of CPC classes and topics to 15 ASPI domains",
            "output": "Chinese activity by critical technology area"
        }
    ],
    "integration_method": "Manual mapping to common technology taxonomy",
    "challenges": [
        "Different classification systems (CPC vs OpenAlex topics vs arXiv categories)",
        "No standard mapping to ASPI Critical Tech domains",
        "Requires domain expertise to map accurately"
    ]
})

# Recipe 4: Geographic collaboration network
integration_recipes["recipes"].append({
    "id": "R4",
    "name": "China Collaboration Network",
    "description": "Which countries collaborate most with China?",
    "use_case": "International relations - Partnership patterns",
    "steps": [
        {
            "step": 1,
            "action": "Get research collaborations",
            "query": "SELECT a1.country_code, a1.institution_name, COUNT(DISTINCT a1.work_id) FROM openalex_work_authors a1 JOIN openalex_work_authors a2 USING (work_id) WHERE a2.country_code = 'CN' AND a1.country_code != 'CN' GROUP BY a1.country_code, a1.institution_name",
            "output": "Countries and institutions collaborating with China in research"
        },
        {
            "step": 2,
            "action": "Cannot get commercial partnerships from current data",
            "limitation": "USAspending = US contracts only, TED = EU contracts only",
            "mitigation": "Use research collaborations as proxy for partnership strength"
        },
        {
            "step": 3,
            "action": "Visualize collaboration network",
            "method": "Export to Gephi/Cytoscape for network visualization",
            "output": "Network graph with China at center, partners as nodes"
        }
    ],
    "integration_method": "Research collaborations only (commercial data limited)",
    "challenges": [
        "Only captures research partnerships",
        "Missing commercial/procurement relationships",
        "US/EU procurement data doesn't show international partnerships"
    ]
})

print(f"  Generated {len(integration_recipes['recipes'])} integration recipes")
for recipe in integration_recipes['recipes']:
    print(f"    {recipe['id']}: {recipe['name']}")

# Save integration recipes
with open(output_dir / "integration_recipes.json", "w", encoding='utf-8') as f:
    json.dump(integration_recipes, f, indent=2, ensure_ascii=False)

print(f"\n[SAVED] integration_recipes.json")

# ============================================================================
# Task 4: Usability Profiles by Use Case
# ============================================================================

print("\n" + "="*80)
print("TASK 4: USABILITY PROFILES BY USE CASE")
print("-" * 40)

usability_profiles = {
    "metadata": {
        "created": datetime.now().isoformat(),
        "description": "Dataset suitability for common research questions"
    },
    "use_cases": []
}

# Use case 1: Technology transfer investigation
usability_profiles["use_cases"].append({
    "use_case": "Technology Transfer Investigation",
    "research_question": "Is Chinese company X acquiring Western technology through procurement, patents, or research?",
    "datasets_needed": ["USAspending", "TED", "USPTO", "OpenAlex"],
    "readiness_score": "70/100",
    "strengths": [
        "USPTO patents show technology acquisition via IP",
        "USAspending shows US government tech procurement",
        "OpenAlex shows research collaborations"
    ],
    "limitations": [
        "No private sector procurement data (only government)",
        "USPTO limited to 2015+ (missing earlier transfers)",
        "Cannot trace research → commercial pathway"
    ],
    "recommended_workflow": "1. Search USPTO for entity patents, 2. Check USAspending for contracts, 3. Find research collaborations in OpenAlex, 4. Manual investigation of commercial relationships",
    "additional_data_needed": [
        "Private sector M&A data",
        "Technology licensing agreements",
        "Joint venture databases"
    ]
})

# Use case 2: Supply chain risk assessment
usability_profiles["use_cases"].append({
    "use_case": "Supply Chain Risk Assessment",
    "research_question": "Which critical supply chains have Chinese entity involvement?",
    "datasets_needed": ["USAspending", "TED", "GLEIF"],
    "readiness_score": "50/100",
    "strengths": [
        "USAspending shows Chinese suppliers to US government",
        "TED shows EU procurement (though low Chinese detection)",
        "GLEIF can map corporate ownership"
    ],
    "limitations": [
        "No private sector supply chain data",
        "GLEIF not integrated with other datasets",
        "Cannot trace multi-tier supply chains",
        "Missing critical sector data (semiconductors, rare earths, pharmaceuticals)"
    ],
    "recommended_workflow": "1. Identify Chinese entities in procurement, 2. Check GLEIF for ownership structure, 3. Manual research on sector-specific supply chains",
    "additional_data_needed": [
        "Import/export data (US Census, Eurostat)",
        "Corporate supply chain disclosures",
        "Industry-specific supplier databases"
    ]
})

# Use case 3: Research security monitoring
usability_profiles["use_cases"].append({
    "use_case": "Research Security Monitoring",
    "research_question": "Which Western institutions collaborate with Chinese entities in sensitive tech?",
    "datasets_needed": ["OpenAlex", "arXiv", "USAspending (grants)"],
    "readiness_score": "80/100",
    "strengths": [
        "OpenAlex excellent for research collaborations (119 countries)",
        "arXiv good for preprint research (1.4M papers)",
        "Can identify institution-level partnerships",
        "Can track by technology domain"
    ],
    "limitations": [
        "OpenAlex is strategic tech subset (not comprehensive)",
        "Cannot access author nationality (only institution country)",
        "Missing sensitive research (classified, restricted)",
        "No access control or export control violation data"
    ],
    "recommended_workflow": "1. Query OpenAlex for China collaborations by institution, 2. Filter by sensitive tech topics, 3. Cross-reference with ASPI tech tracker, 4. Manual investigation of flagged institutions",
    "additional_data_needed": [
        "University research grant databases",
        "Restricted party lists (BIS Entity List, etc.)",
        "Talent program participation (Thousand Talents, etc.)"
    ]
})

# Use case 4: Patent landscape analysis
usability_profiles["use_cases"].append({
    "use_case": "Patent Landscape Analysis",
    "research_question": "What is China's patent strategy in technology domain X?",
    "datasets_needed": ["USPTO", "PatentsView CPC"],
    "readiness_score": "60/100",
    "strengths": [
        "425K Chinese-origin patents in USPTO",
        "CPC classification for technology mapping",
        "Can identify top assignees and filing trends"
    ],
    "limitations": [
        "CRITICAL: Only 2015-2024 coverage (missing 2001-2014)",
        "Only USPTO (missing EPO, CNIPA, WIPO)",
        "No patent family linkage",
        "No citation network analysis"
    ],
    "recommended_workflow": "1. Filter patents by CPC class, 2. Aggregate by Chinese assignee, 3. Analyze filing trends 2015-2024, 4. Note limitation: Cannot compare to pre-2015",
    "additional_data_needed": [
        "EPO patents (European patent office)",
        "CNIPA patents (Chinese patent office)",
        "Patent family data (INPADOC)",
        "Pre-2015 USPTO data"
    ]
})

# Use case 5: Temporal trend analysis
usability_profiles["use_cases"].append({
    "use_case": "Temporal Trend Analysis",
    "research_question": "Is Chinese involvement in Western systems increasing over time?",
    "datasets_needed": ["All datasets"],
    "readiness_score": "65/100",
    "strengths": [
        "USAspending: 28 years (1997-2025)",
        "OpenAlex: 116 years (1861-2025)",
        "arXiv: 36 years (1990-2025)",
        "Can show long-term research trends"
    ],
    "limitations": [
        "USPTO only 10 years (2015-2024) - CANNOT DO LONG-TERM PATENT TRENDS",
        "Different start dates make comparison difficult",
        "Recent years incomplete (publication lag)"
    ],
    "recommended_workflow": "1. Do NOT use USPTO for long-term trends, 2. Focus on OpenAlex/arXiv for historical analysis, 3. Use USAspending for procurement trends, 4. Note date range limitations explicitly",
    "additional_data_needed": [
        "Pre-2015 USPTO data",
        "Normalized time series data"
    ]
})

print(f"  Generated {len(usability_profiles['use_cases'])} use case profiles")
for profile in usability_profiles['use_cases']:
    print(f"    {profile['use_case']}: {profile['readiness_score']} ready")

# Save usability profiles
with open(output_dir / "usability_profiles.json", "w", encoding='utf-8') as f:
    json.dump(usability_profiles, f, indent=2, ensure_ascii=False)

print(f"\n[SAVED] usability_profiles.json")

# ============================================================================
# Summary Statistics
# ============================================================================

print("\n" + "="*80)
print("SUMMARY STATISTICS")
print("="*80)

summary = {
    "audit_date": datetime.now().isoformat(),
    "query_cookbook": {
        "total_patterns": len(query_cookbook["queries"]),
        "patterns": [q["id"] + ": " + q["name"] for q in query_cookbook["queries"]]
    },
    "data_caveats": {
        "datasets_covered": len(data_caveats["datasets"]),
        "critical_issues": sum(
            sum(1 for c in info["caveats"] if c["severity"] == "CRITICAL")
            for info in data_caveats["datasets"].values()
        ),
        "high_issues": sum(
            sum(1 for c in info["caveats"] if c["severity"] == "HIGH")
            for info in data_caveats["datasets"].values()
        )
    },
    "integration_recipes": {
        "total_recipes": len(integration_recipes["recipes"]),
        "recipes": [r["id"] + ": " + r["name"] for r in integration_recipes["recipes"]]
    },
    "usability_profiles": {
        "use_cases_covered": len(usability_profiles["use_cases"]),
        "average_readiness": sum(
            int(uc["readiness_score"].split("/")[0])
            for uc in usability_profiles["use_cases"]
        ) / len(usability_profiles["use_cases"])
    }
}

print(f"\nQuery Cookbook: {summary['query_cookbook']['total_patterns']} patterns")
print(f"Data Caveats: {summary['data_caveats']['datasets_covered']} datasets")
print(f"  - {summary['data_caveats']['critical_issues']} CRITICAL issues")
print(f"  - {summary['data_caveats']['high_issues']} HIGH issues")
print(f"Integration Recipes: {summary['integration_recipes']['total_recipes']} recipes")
print(f"Usability Profiles: {summary['usability_profiles']['use_cases_covered']} use cases")
print(f"  - Average readiness: {summary['usability_profiles']['average_readiness']:.0f}/100")

# Save summary
with open(output_dir / "phase6_usability_summary.json", "w") as f:
    json.dump(summary, f, indent=2)

print(f"\n[SAVED] phase6_usability_summary.json")

conn.close()

print("\n" + "="*80)
print("PHASE 6 COMPLETE")
print("="*80)
print(f"\nOutput files saved to: {output_dir}")
print()

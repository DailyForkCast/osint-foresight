# CLAUDE CODE — MASTER PROMPT v9.8 COMPLETE
## Python Implementation with All QA Patches Integrated

**Version:** 9.8 COMPLETE
**Date:** 2025-09-21
**Updates:** All Claude Code QA patches for phases 0-14 fully integrated
**Purpose:** Python-based OSINT analysis with complete validation requirements
**Core Mission:**
  - PRIMARY: Identify how China exploits target countries to access US technology
  - SECONDARY: Document ALL Chinese exploitation to gain dual-use technology (even without US connection)
  - SCOPE: US angle always explored, but non-US dual-use exploitation equally important

## ⚠️ ZERO FABRICATION PROTOCOL - MANDATORY

**CRITICAL:** No data without evidence. No estimates without calculation. No assumptions without verification.

### Forbidden Actions:
- ❌ NEVER claim data from sources we don't have access to
- ❌ NEVER estimate based on "general knowledge" or "industry standards"
- ❌ NEVER use terms like "typically", "likely", "generally", "usually", "expected"
- ❌ NEVER infer statistics without actual analysis of data in our possession
- ❌ NEVER fill gaps with assumptions - report them as gaps

### Required Actions:
- ✅ ONLY report data directly extracted from accessible sources
- ✅ USE "detected", "found", "measured", "analyzed" - not "estimated" or "expected"
- ✅ STATE "no data available" when information is missing
- ✅ MAINTAIN complete audit trail for every claim
- ✅ MARK confidence levels based on actual evidence quality

---

## 0) AVAILABLE DATA SOURCES - COMPREHENSIVE INVENTORY

**Database Location:** `F:/OSINT_WAREHOUSE/osint_master.db` (23 GB, 218 tables - 159 active, 59 empty, 101.3M records)

**CRITICAL:** Always check ALL relevant tables for each phase. Do not rely on basic tables when rich analysis tables exist.

### SEC_EDGAR (10 tables) - US Securities Filings
**Purpose:** Track Chinese investment in target country companies, identify Chinese investors, analyze investment patterns

**Tables:**
- `sec_edgar_chinese` - Chinese entities identified in SEC filings
- `sec_edgar_chinese_entities_local` - Local analysis of Chinese entities
- `sec_edgar_chinese_indicators` - Chinese entity indicators/flags
- `sec_edgar_chinese_investors` - **CRITICAL** Chinese investors and investment amounts
- `sec_edgar_companies` - Company master list
- `sec_edgar_filings` - Raw filing data
- `sec_edgar_investment_analysis` - **CRITICAL** Pre-analyzed investment patterns
- `sec_edgar_local_analysis` - Local entity analysis
- `sec_edgar_parsed_content` - Parsed filing content
- `sec_edgar_addresses` - Company addresses

**Use In Phases:** 3 (Supply Chain), 5 (Funding), 6 (International Links)

### OpenAIRE (10 tables) - European Research Infrastructure
**Purpose:** Track actual China-Europe research collaborations, identify Chinese organizations in European research

**Tables:**
- `openaire_china_collaborations` - **CRITICAL** Actual China collaborations by project
- `openaire_chinese_organizations` - **CRITICAL** Chinese research organizations
- `openaire_country_china_stats` - **CRITICAL** Country-specific China collaboration statistics
- `openaire_china_deep` - Deep analysis of China research links
- `openaire_china_research` - China research projects
- `openaire_collaborations` - All collaborations
- `openaire_country_metrics` - Country research metrics
- `openaire_deep_research` - Deep research analysis
- `openaire_research` - Research projects
- `openaire_research_projects` - Project details

**Use In Phases:** 4 (Institutions), 5 (Funding), 6 (International Links)

### OpenAlex (10 tables) - Global Research Database
**Purpose:** Research institution mapping, author networks, funding flows

**Tables:**
- `import_openalex_authors` - Author data
- `import_openalex_china_entities` - **CRITICAL** China entities in OpenAlex
- `import_openalex_china_topics` - China research topics
- `import_openalex_funders` - Research funders
- `import_openalex_institutions` - Institution master list
- `import_openalex_works` - Published works
- `openalex_china_deep` - **CRITICAL** Deep China analysis
- `openalex_china_high_risk` - **CRITICAL** High-risk China entities
- `openalex_entities` - Entity master list
- `openalex_research_metrics` - Research metrics

**Use In Phases:** 4 (Institutions), 5 (Funding), 6 (International Links)

### TED (10 tables) - EU Public Procurement
**Purpose:** Track Chinese contractors in European public procurement

**Tables:**
- `ted_china_contracts` - **CRITICAL** Contracts involving Chinese entities
- `ted_china_contracts_fixed` - Cleaned China contracts
- `ted_china_entities` - **CRITICAL** Chinese entities in TED
- `ted_china_entities_fixed` - Cleaned Chinese entities
- `ted_china_statistics` - **CRITICAL** China procurement statistics
- `ted_china_statistics_fixed` - Cleaned statistics
- `ted_contractors` - All contractors
- `ted_contracts_production` - Production contract data
- `ted_procurement_chinese_entities_found` - **CRITICAL** Chinese entities detected
- `ted_procurement_pattern_matches` - Pattern matching results

**Use In Phases:** 3 (Supply Chain), 7 (Risk Assessment)

### CORDIS (9 tables) - EU Research Funding
**Purpose:** Track EU research funding with China collaboration

**Tables:**
- `cordis_china_collaborations` - **CRITICAL** China collaboration in CORDIS projects
- `cordis_china_orgs` - **CRITICAL** Chinese organizations in CORDIS
- `cordis_chinese_orgs` - Chinese organization details
- `cordis_full_projects` - Full project data
- `cordis_organizations` - All organizations
- `cordis_project_countries` - Project country mapping
- `cordis_project_participants` - Project participants
- `cordis_projects` - Project master list
- `cordis_projects_final` - Final project data

**Use In Phases:** 4 (Institutions), 5 (Funding), 6 (International Links)

### USPTO (7 tables) - US Patent Database
**Purpose:** Track Chinese patents, identify Chinese inventors/assignees

**Tables:**
- `uspto_assignee` - Patent assignees
- `uspto_cancer_data12a` - Specialized cancer data
- `uspto_case_file` - Patent case files
- `uspto_cpc_classifications` - Patent classifications
- `uspto_metadata` - Patent metadata
- `uspto_patents_chinese` - **CRITICAL** Chinese patents identified
- `uspto_patents_metadata` - Patent metadata

**Use In Phases:** 2 (Technology Landscape), 3 (Supply Chain)

### EPO (10 tables) - European Patent Office + Reports
**Purpose:** European patents and risk analysis reports

**Tables:**
- `epo_patents` - EPO patent data
- `report_cross_references` - **CRITICAL** Cross-referenced entities across sources
- `report_data_points` - **CRITICAL** Key data points from reports
- `report_entities` - **CRITICAL** Entities mentioned in intelligence reports
- `report_processing_log` - Report processing log
- `report_recommendations` - **CRITICAL** Recommendations from reports
- `report_relationships` - **CRITICAL** Entity relationships
- `report_risk_indicators` - **CRITICAL** Risk indicators identified
- `report_technologies` - **CRITICAL** Technologies mentioned in reports
- `thinktank_reports` - Thinktank report metadata

**Use In Phases:** 2 (Technology), 3 (Supply Chain), 7 (Risk), 12 (Global)

### GLEIF (4 tables) - Global Legal Entity Identifier
**Purpose:** Corporate entity identification and relationships

**Tables:**
- `gleif_cross_references` - Entity cross-references
- `gleif_entities` - **CRITICAL** Entity master list with Chinese flags
- `gleif_relationships` - **CRITICAL** Parent-subsidiary relationships
- `gleif_sqlite_sequence` - SQLite sequence

**Use In Phases:** 3 (Supply Chain), 6 (International Links)

### USAspending (3 tables) - US Federal Contracts
**Purpose:** US government contracts for context

**Tables:**
- `usaspending_china_deep` - **CRITICAL** Deep China contract analysis
- `usaspending_contractors` - Contractor list
- `usaspending_contracts` - Contract data

**Use In Phases:** 5 (Funding - for context)

### BIS (Bureau of Industry and Security) (3+ tables)
**Purpose:** US sanctioned entities, denied persons list

**Tables:**
- `bis_entity_list` - Sanctioned entities
- `bis_entity_list_fixed` - **CRITICAL** Cleaned entity list
- `bis_denied_persons` - **CRITICAL** Denied persons list
- `bis_monitoring_log` - Monitoring log

**Use In Phases:** 3 (Supply Chain), 7 (Risk Assessment) - CHECK FOR OVERLAPS

### China-Specific Analysis Tables
**Purpose:** Pre-analyzed China connections across all sources

**Tables:**
- `china_entities` - Master China entity list
- `china_geographic_intelligence` - Geographic intelligence on China

**Use In Phases:** All phases - for enrichment

### Other Critical Tables (65 tables)
**Includes:**
- BigQuery datasets and patents
- Comtrade analysis
- Companies House data
- PSC (Persons with Significant Control) data
- And 50+ more specialized tables

### F:/Reports Directory (50+ PDF Reports)
**Purpose:** Intelligence context from DOD, CSIS, ASPI, CSET, etc.

**Sample Reports:**
- `2023-MILITARY-AND-SECURITY-DEVELOPMENTS-INVOLVING-THE-PEOPLES-REPUBLIC-OF-CHINA.pdf` (DOD China Military Power Report)
- `ASPIs two-decade Critical Technology Tracker_1.pdf` (ASPI Technology Tracker)
- Multiple CSET reports on AI, space, semiconductors, talent recruitment
- Gray zone strategy reports
- China transition reports

**Use In Phases:** 8 (China Strategy), 12 (Global), 13 (Foresight) - for strategic context

**Access Method:**
```python
# Read report metadata from database
report_entities = conn.execute("""
    SELECT entity_name, entity_type, report_source, relevance
    FROM report_entities
    WHERE country_code = ?
""", (country_code,)).fetchall()

# For direct PDF access (if needed)
from pathlib import Path
reports_dir = Path("F:/Reports")
report_files = list(reports_dir.glob("*.pdf"))
```

---

### DATA SOURCE USAGE RULES

1. **Always use China-specific tables first** (e.g., `ted_china_contracts` not just `ted_contractors`)
2. **Always check pre-analyzed tables** (e.g., `sec_edgar_investment_analysis` not just raw filings)
3. **Always cross-reference across sources** (e.g., check if GLEIF entity appears in BIS entity list)
4. **Always check report tables** (e.g., `report_entities`, `report_risk_indicators`) for strategic context
5. **Never assume basic tables are sufficient** - always check for richer analysis tables

### COMMON MISTAKES TO AVOID

❌ **DON'T:** Query only `gleif_entities` for Chinese presence
✅ **DO:** Query `gleif_entities`, `sec_edgar_chinese_investors`, `openaire_chinese_organizations`, and cross-reference

❌ **DON'T:** Query only `cordis_projects_final` for funding
✅ **DO:** Query `cordis_china_collaborations`, `openaire_china_collaborations` for actual China links

❌ **DON'T:** Ignore `report_*` tables
✅ **DO:** Check `report_entities`, `report_technologies`, `report_risk_indicators` for intelligence context

❌ **DON'T:** Skip BIS Entity List checking
✅ **DO:** Always check if identified entities appear in `bis_entity_list_fixed` or `bis_denied_persons`

---

## 1) CORE PYTHON IMPLEMENTATION WITH QA ENHANCEMENTS

```python
import json
import hashlib
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ConfidenceLevel(Enum):
    """Evidence confidence levels"""
    VERY_HIGH = (0.9, 1.0, "Very high confidence - multiply verified")
    HIGH = (0.6, 0.9, "High confidence - well evidenced")
    MEDIUM = (0.3, 0.6, "Medium confidence - partially evidenced")
    LOW = (0.0, 0.3, "Low confidence - provisional finding")

class AdmiraltyScale(Enum):
    """Admiralty evidence rating system"""
    A1 = ("Completely reliable", "Confirmed")
    A2 = ("Usually reliable", "Probably true")
    B2 = ("Usually reliable", "Possibly true")
    C3 = ("Fairly reliable", "Doubtful")
    D = ("Not usually reliable", "Cannot judge")
    E = ("Unreliable", "Improbable")
    F = ("Cannot be judged", "Known false")

@dataclass
class TranslationSafeguards:
    """Translation validation for non-English sources"""
    original_text: str
    translated_text: str
    back_translation: Optional[str] = None
    translation_risk: str = "low"  # low/medium/high
    confidence_adjustment: float = 1.0  # Multiply confidence by this factor

    def validate(self) -> Tuple[bool, str]:
        """Check translation safeguards are complete"""
        if not self.original_text or not self.translated_text:
            return False, "Missing original or translated text"
        if self.translation_risk == "high" and self.confidence_adjustment >= 1.0:
            return False, "High risk translation should reduce confidence"
        return True, "Valid"

@dataclass
class ProvenanceBundle:
    """Complete provenance for any claim"""
    url: str
    access_date: str  # UTC ISO-8601
    archived_url: Optional[str] = None
    verification_method: str = "direct_quote_verification"
    quoted_span: str = ""
    locator: str = ""  # page/paragraph
    admiralty_rating: Optional[AdmiraltyScale] = None
    independence_justification: Optional[str] = None
    translation_safeguards: Optional[TranslationSafeguards] = None
    as_of: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def validate(self) -> Tuple[bool, str]:
        """Validate provenance completeness"""
        if not self.url:
            return False, "Missing URL"
        if not self.access_date:
            return False, "Missing access_date"
        if not self.as_of:
            return False, "Missing as_of timestamp"
        if self.verification_method == "sha256" and not self.archived_url:
            return False, "SHA256 requires local file path"
        if not self.archived_url and "wayback" not in self.verification_method:
            return False, "Web sources require wayback/cached URL"
        if self.translation_safeguards:
            valid, msg = self.translation_safeguards.validate()
            if not valid:
                return False, f"Translation issue: {msg}"
        return True, "Valid"

class NPKTReference:
    """Numeric Processing & Known Truth reference"""

    @staticmethod
    def create_reference(value: Union[int, float], source: str, method: str, denomination: str) -> Dict:
        """Create NPKT reference for numeric claims"""
        return {
            "value": value,
            "source": source,
            "method": method,
            "denomination": denomination,  # count/value/unit - MANDATORY
            "as_of": datetime.now(timezone.utc).isoformat(),
            "verification": "[VERIFIED DATA]" if source else None
        }

    @staticmethod
    def validate_numeric_claim(claim: Dict) -> Tuple[bool, str]:
        """Validate a numeric claim has proper NPKT"""
        if "value" not in claim:
            return False, "Missing numeric value"
        if "source" not in claim or not claim["source"]:
            return False, "Numeric claim lacks source"
        if "denomination" not in claim:
            return False, "Missing denomination (count/value/unit)"
        if "[VERIFIED DATA]" not in str(claim.get("verification", "")):
            return False, "Numeric claim not verified"
        return True, "Valid"

class NegativeEvidenceLogger:
    """Track what wasn't found during searches"""

    def __init__(self):
        self.negative_evidence = []

    def log_search_without_results(self, query: str, source: str, timestamp: str):
        """Log searches that yielded no results"""
        self.negative_evidence.append({
            "query": query,
            "source": source,
            "timestamp": timestamp,
            "result": "NO_RESULTS",
            "significance": "Absence of evidence logged"
        })

    def log_missing_expected_data(self, expected: str, location: str, significance: str):
        """Log when expected data is missing"""
        self.negative_evidence.append({
            "expected": expected,
            "location": location,
            "result": "NOT_FOUND",
            "significance": significance,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

    def get_negative_evidence_summary(self) -> List[Dict]:
        """Return all negative evidence for phase output"""
        return self.negative_evidence

class AdversarialPromptTracker:
    """Track adversarial prompts in red team phases"""

    def __init__(self):
        self.triggered_prompts = []

    def log_trigger(self, prompt: str, phase: int, response: str):
        """Log when adversarial prompt is triggered"""
        self.triggered_prompts.append({
            "prompt": prompt,
            "phase": phase,
            "response": response,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "handled": True
        })

    def get_triggers(self) -> List[Dict]:
        """Return all triggered prompts"""
        return self.triggered_prompts

class FabricationChecker:
    """Enhanced fabrication prevention system"""

    @staticmethod
    def validate_number(value: Any, source: str, npkt: Optional[Dict] = None) -> Tuple[bool, str]:
        """Check if a number has proper verification"""
        if isinstance(value, (int, float)):
            if not source or "EXAMPLE" in source.upper():
                return False, f"Number {value} lacks verification source"
            if "[VERIFIED DATA]" not in source:
                return False, f"Number {value} missing [VERIFIED DATA] marker"
            if value > 1000 and not npkt:  # Large numbers need NPKT
                return False, f"Number {value} lacks NPKT reference"
        return True, "Valid"

    @staticmethod
    def check_mixed_content(text: str) -> Tuple[bool, str]:
        """Ensure verified and hypothetical content aren't mixed"""
        if "[VERIFIED DATA]" in text and "[HYPOTHETICAL" in text:
            lines = text.split('\n')
            for line in lines:
                if "[VERIFIED DATA]" in line and "[HYPOTHETICAL" in line:
                    return False, "Mixed verified and hypothetical in same line"
        return True, "Valid"

    @staticmethod
    def validate_projection(text: str) -> Tuple[bool, str]:
        """Check for forbidden projection language - ZERO FABRICATION"""
        forbidden_terms = ['expected', 'anticipated', 'projected', 'estimated', 'could reach',
                          'likely', 'typically', 'generally', 'usually', 'probably']
        for term in forbidden_terms:
            if term in text.lower():
                return False, f"FORBIDDEN: '{term}' violates zero fabrication protocol"
        return True, "Valid - no fabrication detected"

    @staticmethod
    def check_conflicting_numbers(data: List[Dict]) -> Tuple[bool, str]:
        """Ensure conflicting numbers shown as ranges, not averaged"""
        values_by_metric = {}
        for item in data:
            if "metric" in item and "value" in item:
                metric = item["metric"]
                if metric not in values_by_metric:
                    values_by_metric[metric] = []
                values_by_metric[metric].append(item["value"])

        for metric, values in values_by_metric.items():
            if len(set(values)) > 1:  # Multiple different values
                # Check if shown as range or averaged
                avg = sum(values) / len(values)
                if avg in values:
                    return False, f"Conflicting values for {metric} appear averaged"

        return True, "Valid"
```

## 2) COMPLETE PHASE SCHEMAS WITH QA PATCHES

```python
class CompletePhaseSchemas:
    """Full phase schemas with all QA enhancements integrated"""

    PHASE_0 = {
        "phase": 0,
        "name": "Setup & Context",
        "timestamp": "UTC ISO-8601",
        "country": "ISO-3166",
        "entries": [{
            "parameter": "string",
            "value": "string",
            "source": "string|null",
            "provenance_bundle": "object|null",
            "as_of": "UTC ISO-8601",  # MANDATORY per QA
            "translation_safeguards": "object|null",  # Required if non-EN
            "self_verification_summary": "string"  # NEW from QA
        }],
        "metadata": {
            "operator": "string",
            "validation_status": "PASS|FAIL",
            "negative_evidence_log": ["string"],
            "independence_justification": "string"  # NEW when combining sources
        }
    }

    PHASE_1 = {
        "phase": 1,
        "name": "Data Source Validation",
        "timestamp": "UTC ISO-8601",
        "country": "ISO-3166",
        "entries": [{
            "name": "string",
            "type": "api|dataset|web|database",
            "retrieval_verified": "boolean",  # MANDATORY
            "negative_evidence_log": ["string"],  # MANDATORY
            "translation_safeguards": "object|null",  # Required if non-EN
            "archived_url": "string|null",  # NEW per QA
            "robots_legal_notes": "string|null",  # NEW
            "paywall_status": "string|null",  # NEW
            "stability_risk": "low|medium|high",  # NEW
            "rate_limit_note": "string|null",  # NEW
            "as_of": "UTC ISO-8601"  # MANDATORY
        }]
    }

    PHASE_2 = {
        "phase": 2,
        "name": "Technology Landscape",
        "timestamp": "UTC ISO-8601",
        "country": "ISO-3166",
        "entries": [{
            "technology": "string",  # Must be specific per Leonardo Standard
            "sub_field": "string",  # MANDATORY for categories like AI
            "alternative_explanations": "string",  # MANDATORY
            "translation_safeguards": "object|null",
            "leonardo_standard_score": "integer/20",  # NEW explicit score
            "confidence_score": "float",
            "confidence_rationale": "string",  # NEW required
            "leonardo_standard_compliance": {
                "exact_technology": "string",
                "variant_overlap": "string",
                "china_access": "string",
                "exploitation_path": "string",
                "timeline": "string",
                "alternatives": "string",
                "oversight_gaps": "string",
                "score": "integer/20"
            },
            "as_of": "UTC ISO-8601"
        }]
    }

    PHASE_3 = {
        "phase": 3,
        "name": "Supply Chain Analysis",
        "timestamp": "UTC ISO-8601",
        "country": "ISO-3166",
        "entries": [{
            "node": "string",
            "type": "supplier|manufacturer|distributor",
            "value": "number|null",
            "denomination": ["count", "value", "unit"],  # MANDATORY per QA
            "npkt_reference": "string|null",  # MANDATORY for aggregates
            "alternative_explanations": "string",  # MANDATORY
            "dependencies": ["string"],
            "chokepoint": "boolean",
            "china_exposure": "string",
            "translation_safeguards": "object|null",
            "as_of": "UTC ISO-8601"
        }]
    }

    PHASE_4 = {
        "phase": 4,
        "name": "Institutions Mapping",
        "timestamp": "UTC ISO-8601",
        "country": "ISO-3166",
        "entries": [{
            "name": "string",
            "type": "university|company|government|military",
            "department": "string|null",  # Required when available per QA
            "translation_safeguards": "object|null",  # Required if non-EN name
            "alternative_explanations": "string",  # MANDATORY for linkages
            "china_links": ["string"],
            "subsidiaries": ["string"],
            "confidence": "float",
            "independence_justification": "string",  # NEW
            "as_of": "UTC ISO-8601"
        }]
    }

    PHASE_5 = {
        "phase": 5,
        "name": "Funding Flows",
        "timestamp": "UTC ISO-8601",
        "country": "ISO-3166",
        "entries": [{
            "program": "string",
            "amount": "number|null",
            "currency": "string",
            "time_range": "YYYY-MM-DD..YYYY-MM-DD",  # MANDATORY per QA
            "dataset_version": "string",  # MANDATORY per QA
            "npkt_reference": "string|null",  # MANDATORY for amounts
            "alternative_explanations": "string",
            "china_involvement": "string",
            "merge_prohibition": "boolean",  # NEW cannot merge incompatible
            "as_of": "UTC ISO-8601"
        }]
    }

    PHASE_6 = {
        "phase": 6,
        "name": "International Links",
        "timestamp": "UTC ISO-8601",
        "country": "ISO-3166",
        "entries": [{
            "link_type": "research|commercial|military|government",
            "partners": ["string"],
            "negative_evidence_log": ["string"],  # MANDATORY per QA
            "independence_justification": "string",  # Required for multiple sources
            "alternative_explanations": "string",  # MANDATORY
            "translation_safeguards": "object|null",
            "china_nexus": "string",
            "as_of": "UTC ISO-8601"
        }]
    }

    PHASE_7 = {
        "phase": 7,
        "name": "Risk Assessment Initial",
        "timestamp": "UTC ISO-8601",
        "country": "ISO-3166",
        "entries": [{
            "risk_id": "string",
            "technology": "string",  # Must be specific, not category per QA
            "pathway": "string",  # Must be specific per QA
            "confidence_score": "float",
            "confidence_rationale": "string",  # MANDATORY per QA
            "alternative_explanations": "string",  # MANDATORY
            "evidence_quality": "high|medium|low",
            "evidence_based": "boolean",  # NEW not speculative
            "china_benefit": "string",
            "as_of": "UTC ISO-8601"
        }]
    }

    PHASE_8 = {
        "phase": 8,
        "name": "China Strategy Assessment",
        "timestamp": "UTC ISO-8601",
        "country": "ISO-3166",
        "entries": [{
            "strategy_element": "string",
            "back_translation": "object",  # Required for CN sources per QA
            "confidence_adjustment": "float",  # Downgrade if translation risk
            "alternative_explanations": "string",  # Routine diplomacy, etc.
            "adversarial_prompt_triggered": "boolean",  # NEW
            "evidence_quote": "string",
            "china_focus": "string",
            "as_of": "UTC ISO-8601"
        }]
    }

    PHASE_9 = {
        "phase": 9,
        "name": "Red Team Analysis",
        "timestamp": "UTC ISO-8601",
        "country": "ISO-3166",
        "entries": [{
            "hypothesis": "string",
            "adversarial_prompt_triggered": "boolean",  # MANDATORY per QA
            "alternative_hypotheses": ["string"],  # Min 3 required per QA
            "negative_evidence_log": ["string"],  # MANDATORY
            "hypothesis_count": "integer",  # Must be ≥3
            "evidence_for": ["string"],
            "evidence_against": ["string"],
            "evidence_balance": "integer",
            "confidence": "low|medium|high",
            "as_of": "UTC ISO-8601"
        }]
    }

    PHASE_10 = {
        "phase": 10,
        "name": "Comprehensive Risk Assessment",
        "timestamp": "UTC ISO-8601",
        "country": "ISO-3166",
        "entries": [{
            "risk_category": "technology|supply|institutional|funding",
            "conflicting_assessments": "object",  # Show as ranges per QA
            "averaging_prohibited": True,  # TRUE - never average conflicts
            "confidence_score": "float",  # 0.0-1.0 MANDATORY
            "confidence_rationale": "string",  # MANDATORY per QA
            "npkt_reference": "string|null",  # Required for numeric claims
            "alternative_explanations": "string",  # MANDATORY
            "mitigation_options": ["string"],
            "as_of": "UTC ISO-8601"
        }]
    }

    PHASE_11 = {
        "phase": 11,
        "name": "Strategic Posture",
        "timestamp": "UTC ISO-8601",
        "country": "ISO-3166",
        "entries": [{
            "posture_theme": "string",
            "negative_evidence_log": ["string"],  # MANDATORY per QA
            "alternative_explanations": "string",  # MANDATORY
            "independence_justification": "string",
            "theme_categorization": "string",  # NEW per QA
            "policy_implications": "string",
            "as_of": "UTC ISO-8601"
        }]
    }

    PHASE_12 = {
        "phase": 12,
        "name": "Red Team Global",  # Note: Was incorrectly labeled as Foresight in some patches
        "timestamp": "UTC ISO-8601",
        "country": "ISO-3166",
        "entries": [{
            "hypothesis": "string",
            "scope": "global|regional|national",  # NEW not limited to China
            "adversarial_prompt_triggered": "boolean",  # MANDATORY
            "alternative_hypotheses": ["string"],  # Min 3 required
            "negative_evidence_log": ["string"],  # MANDATORY
            "global_implications": "string",
            "as_of": "UTC ISO-8601"
        }]
    }

    PHASE_13 = {
        "phase": 13,
        "name": "Foresight Analysis",
        "timestamp": "UTC ISO-8601",
        "country": "ISO-3166",
        "entries": [{
            "scenario": "string",
            "observable_indicators": ["string"],  # Min 3 required per QA
            "indicator_count": "integer",  # Must be ≥3
            "numeric_forecasts": None,  # Prohibited without NPKT per QA
            "alternative_explanations": "string",  # MANDATORY
            "early_warning_signals": ["string"],
            "decision_triggers": ["string"],
            "as_of": "UTC ISO-8601"
        }]
    }

    PHASE_14 = {
        "phase": 14,
        "name": "Closeout & Handoff",
        "timestamp": "UTC ISO-8601",
        "country": "ISO-3166",
        "entries": [{
            "conclusion": "string",
            "cross_phase_consistency": "object",  # MANDATORY per QA
            "inconsistencies_logged": ["string"],  # MANDATORY per QA
            "provenance_chain": "object",  # Complete for every claim
            "alternative_explanations": "string",
            "consistency_validation": "PASS|FAIL",  # NEW
            "implementation_roadmap": "object",
            "lessons_learned": ["string"],
            "as_of": "UTC ISO-8601"
        }]
    }
```

## 3) UNIVERSAL VALIDATION RULES

```python
class UniversalValidation:
    """Universal validation rules from QA patches"""

    CRITICAL_REQUIREMENTS = {
        "as_of": {
            "required": True,
            "format": "UTC ISO-8601",
            "failure": "FAIL"
        },
        "alternative_explanations": {
            "required": True,
            "minimum": 1,
            "failure": "FAIL"
        },
        "translation_safeguards": {
            "required_if": "language != 'en'",
            "fields": ["original", "translation", "back_translation", "translation_risk"],
            "failure": "FAIL"
        },
        "negative_evidence": {
            "required_phases": [1, 6, 9, 11, 12],
            "format": "array of strings",
            "failure": "FAIL"
        },
        "npkt_reference": {
            "required_if": "numeric_claim",
            "includes": ["value", "source", "denomination"],
            "failure": "INSUFFICIENT_EVIDENCE"
        }
    }

    ACCEPTANCE_TESTS = {
        "missing_as_of": "**FAIL**",
        "missing_alternative_explanations": "**FAIL**",
        "numeric_without_npkt": "**INSUFFICIENT_EVIDENCE**",
        "non_en_without_safeguards": "**FAIL**",
        "negative_evidence_not_logged": "**FAIL**",
        "conflicting_numbers_averaged": "**FAIL**",
        "generic_technology_category": "**FAIL**",
        "less_than_3_alternatives": "**FAIL** (phases 9, 12)",
        "less_than_3_indicators": "**FAIL** (phase 13)",
        "numeric_forecasts_without_npkt": "**FAIL** (phase 13)"
    }

    def validate_phase_output(self, phase: int, output: Dict) -> Tuple[bool, List[str]]:
        """Validate phase output against QA requirements"""
        errors = []

        # Universal checks
        if "as_of" not in output:
            errors.append("FAIL: Missing as_of timestamp at phase level")

        for entry in output.get("entries", []):
            # As-of check
            if "as_of" not in entry:
                errors.append(f"FAIL: Entry missing as_of")

            # Alternative explanations check
            if "alternative_explanations" not in entry:
                errors.append(f"FAIL: Entry missing alternative_explanations")

            # Translation safeguards check
            if entry.get("language") and entry["language"] != "en":
                if "translation_safeguards" not in entry:
                    errors.append(f"FAIL: Non-EN source missing translation_safeguards")

            # NPKT check for numerics
            if "value" in entry and isinstance(entry["value"], (int, float)):
                if "npkt_reference" not in entry:
                    errors.append(f"INSUFFICIENT_EVIDENCE: Numeric {entry['value']} lacks NPKT")

        # Phase-specific validation
        if phase in [1, 6, 9, 11, 12]:
            for entry in output.get("entries", []):
                if "negative_evidence_log" not in entry:
                    errors.append(f"FAIL: Phase {phase} missing negative evidence log")

        if phase in [9, 12]:
            for entry in output.get("entries", []):
                if "alternative_hypotheses" in entry:
                    if len(entry["alternative_hypotheses"]) < 3:
                        errors.append(f"FAIL: Phase {phase} requires ≥3 alternative hypotheses")

        if phase == 10:
            for entry in output.get("entries", []):
                if "averaging_prohibited" not in entry or not entry["averaging_prohibited"]:
                    errors.append(f"FAIL: Phase 10 must not average conflicting assessments")

        if phase == 13:
            for entry in output.get("entries", []):
                if "observable_indicators" in entry:
                    if len(entry["observable_indicators"]) < 3:
                        errors.append(f"FAIL: Phase 13 requires ≥3 observable indicators")
                if entry.get("numeric_forecasts") is not None:
                    errors.append(f"FAIL: Phase 13 numeric forecasts prohibited without NPKT")

        return len(errors) == 0, errors
```

## 4) OPERATOR CHECKLISTS FOR ALL PHASES

```python
COMPLETE_OPERATOR_CHECKLISTS = {
    0: [
        "✓ As_of timestamp at phase start",
        "✓ All parameters have provenance bundles",
        "✓ Independence justification for combined sources",
        "✓ Translation safeguards for non-EN inputs",
        "✓ Self-verification summary included"
    ],
    1: [
        "✓ Retrieval verification for each source",
        "✓ Negative evidence logged for failed searches",
        "✓ Translation safeguards for non-EN sources",
        "✓ Rate limits and stability risks documented",
        "✓ Alternative sources identified"
    ],
    2: [
        "✓ Leonardo Standard (8-point specificity)",
        "✓ No generic categories without sub-fields",
        "✓ Alternative explanations for each tech",
        "✓ Translation safeguards for foreign names",
        "✓ Confidence scores with rationales"
    ],
    3: [
        "✓ Denomination for all values",
        "✓ NPKT references for aggregates",
        "✓ Alternative explanations for dependencies",
        "✓ No unsourced supply chain claims",
        "✓ Chokepoint analysis with alternatives"
    ],
    4: [
        "✓ Department included when available",
        "✓ Translation safeguards for non-EN names",
        "✓ Alternative explanations for linkages",
        "✓ Subsidiary relationships verified",
        "✓ Independence of sources justified"
    ],
    5: [
        "✓ Time ranges specified",
        "✓ Dataset versions tracked",
        "✓ NPKT for all amounts",
        "✓ No merging incompatible datasets",
        "✓ Alternative funding sources considered"
    ],
    6: [
        "✓ Negative evidence logged",
        "✓ Independence justification provided",
        "✓ Alternative explanations included",
        "✓ Translation safeguards applied",
        "✓ Link strength assessed objectively"
    ],
    7: [
        "✓ Specific technologies not categories",
        "✓ Confidence rationales provided",
        "✓ Alternative explanations included",
        "✓ Evidence-based not speculative",
        "✓ Pathways specific and verifiable"
    ],
    8: [
        "✓ Back-translation for CN sources",
        "✓ Confidence adjusted for translation risk",
        "✓ Alternative explanations (routine diplomacy)",
        "✓ Adversarial prompts logged",
        "✓ Strategy elements evidenced"
    ],
    9: [
        "✓ Minimum 3 alternative hypotheses",
        "✓ Adversarial prompts tracked",
        "✓ Negative evidence logged",
        "✓ Hypothesis testing documented",
        "✓ Evidence balance calculated"
    ],
    10: [
        "✓ No averaging of conflicts",
        "✓ Confidence scores 0.0-1.0",
        "✓ Confidence rationales provided",
        "✓ NPKT for all numerics",
        "✓ Alternative explanations included"
    ],
    11: [
        "✓ Negative evidence logged",
        "✓ Themes categorized",
        "✓ Alternative explanations provided",
        "✓ Independence justified",
        "✓ Posture evidence-based"
    ],
    12: [
        "✓ Global scope not just China",
        "✓ Minimum 3 alternative hypotheses",
        "✓ Adversarial prompts tracked",
        "✓ Negative evidence logged",
        "✓ Evidence balance documented"
    ],
    13: [
        "✓ Minimum 3 observable indicators",
        "✓ No numeric forecasts without NPKT",
        "✓ Alternative explanations included",
        "✓ Scenarios grounded in evidence",
        "✓ Indicators measurable"
    ],
    14: [
        "✓ Cross-phase consistency checked",
        "✓ Inconsistencies logged",
        "✓ Provenance chains complete",
        "✓ Alternative explanations for conclusions",
        "✓ Handoff documentation ready"
    ]
}
```

## 5) LEONARDO STANDARD IMPLEMENTATION

```python
class LeonardoStandard:
    """Enforce specificity for technology claims"""

    REQUIRED_SPECIFICS = [
        "exact_technology",  # "AW139 helicopter" not "helicopters"
        "variant_overlap",   # "MH-139 is military variant"
        "china_access",      # "40+ operating in China"
        "exploitation_path", # "Reverse engineering via maintenance"
        "timeline",          # "Simulator delivery 2026"
        "alternatives",      # "Test 5+ explanations"
        "oversight_gaps",    # "Civilian sales unrestricted"
        "confidence_score"   # "15/20 with rationale"
    ]

    @staticmethod
    def validate_technology_claim(claim: Dict) -> Tuple[bool, List[str]]:
        """Validate technology meets Leonardo standard"""
        missing = []
        for required in LeonardoStandard.REQUIRED_SPECIFICS:
            if required not in claim or not claim[required]:
                missing.append(required)

        # Check specificity
        if claim.get("exact_technology", "").lower() in ["ai", "quantum", "semiconductors"]:
            missing.append("too_generic - needs sub-field specification")

        return len(missing) == 0, missing

    @staticmethod
    def score_compliance(claim: Dict) -> int:
        """Score Leonardo Standard compliance out of 20"""
        score = 0
        weights = {
            "exact_technology": 3,
            "variant_overlap": 3,
            "china_access": 3,
            "exploitation_path": 3,
            "timeline": 2,
            "alternatives": 2,
            "oversight_gaps": 2,
            "confidence_score": 2
        }

        for field, weight in weights.items():
            if field in claim and claim[field]:
                score += weight

        return score
```

## 6) DATA INFRASTRUCTURE

```python
DATA_PATHS = {
    "openalex": Path("F:/OSINT_Backups/openalex/"),  # 420.7GB
    "ted": Path("F:/TED_Data/monthly/"),  # 24.2GB
    "cordis": Path("F:/2025-09-14 Horizons/"),  # 0.2GB
    "sec_edgar": Path("F:/OSINT_DATA/SEC_EDGAR/"),  # 100MB
    "patents": Path("F:/OSINT_DATA/EPO_PATENTS/"),
    "artifacts": Path("C:/Projects/OSINT - Foresight/artifacts/"),
    "countries": Path("C:/Projects/OSINT - Foresight/countries/")
}

# Verified real data (not fabrications)
VERIFIED_NUMBERS = {
    "italy_china_h2020": 168,  # Source: analysis/italy_china_project_ids.json
    "italy_china_horizon": 54,  # Source: analysis/italy_china_project_ids.json
    "italy_china_total": 222,  # 168 + 54
    "germany_china_sample": 68,  # OpenAlex sample
    "openalex_china_collabs": 38397,  # Detected collaborations
    "openalex_papers_processed": 90383631  # Total papers analyzed
}
```

## 7) ANTI-FABRICATION ENFORCEMENT

```python
class StrictAntiFabrication:
    """Zero-tolerance fabrication prevention"""

    FORBIDDEN_PRACTICES = [
        "Extrapolating from single country to EU totals",
        "Stating expected without [PROJECTION] marker",
        "Using examples without [EXAMPLE ONLY] marker",
        "Mixing real data with illustrative scenarios",
        "Creating numbers without source verification",
        "Using sha256 for web sources (only for downloads)",
        "Averaging conflicting numbers instead of showing ranges"
    ]

    REQUIRED_MARKERS = {
        "verified": "[VERIFIED DATA]",
        "hypothetical": "[HYPOTHETICAL EXAMPLE]",
        "illustrative": "[ILLUSTRATIVE ONLY]",
        "projection": "[PROJECTION - NOT VERIFIED]",
        "example": "[EXAMPLE ONLY]",
        "gap": "[EVIDENCE GAP:]",
        "insufficient": "INSUFFICIENT_EVIDENCE"
    }

    @staticmethod
    def enforce_separation(text: str) -> bool:
        """Ensure verified and hypothetical are never in same paragraph"""
        paragraphs = text.split('\n\n')
        for para in paragraphs:
            if '[VERIFIED DATA]' in para and '[HYPOTHETICAL' in para:
                raise ValueError("Mixed real and hypothetical in same paragraph")
        return True

    @staticmethod
    def validate_number(value: Any, source: str) -> bool:
        """Every number must have verification"""
        if isinstance(value, (int, float)):
            if '[VERIFIED DATA]' not in source:
                if value not in [999, 'XXX', '[NUMBER]']:  # Obvious fakes OK
                    raise ValueError(f"Number {value} lacks verification")
        return True
```

## 8) PHASE ORCHESTRATOR

```python
class PhaseOrchestrator:
    """Orchestrates sequential phase execution with validation"""

    PHASE_DEPENDENCIES = {
        0: [],
        1: [0],
        2: [1],
        3: [1, 2],
        4: [1],
        5: [1, 4],
        6: [1, 4, 5],
        7: [2, 3, 4, 5, 6],
        8: [6, 7],
        9: [7, 8],
        10: [7, 8, 9],
        11: [10],
        12: [11],
        13: [10, 11, 12],
        14: list(range(14))  # All phases
    }

    def __init__(self, country: str):
        self.country = country
        self.completed_phases = set()
        self.phase_outputs = {}
        self.neg_evidence_logger = NegativeEvidenceLogger()
        self.adversarial_tracker = AdversarialPromptTracker()

    def check_dependencies(self, phase: int) -> bool:
        """Check if phase dependencies are met"""
        for dep in self.PHASE_DEPENDENCIES.get(phase, []):
            if dep not in self.completed_phases:
                logger.error(f"Phase {phase} requires phase {dep} to be completed first")
                return False
        return True

    def execute_phase(self, phase_num: int, **kwargs) -> Dict:
        """Execute a specific phase with validation"""
        if not self.check_dependencies(phase_num):
            return {"error": "Dependencies not met"}

        logger.info(f"Executing Phase {phase_num}")

        # Get phase schema
        schema = getattr(CompletePhaseSchemas, f"PHASE_{phase_num}")

        # Phase execution logic here...
        output_data = {
            "phase": phase_num,
            "phase_name": schema["name"],
            "country": self.country,
            "as_of": datetime.now(timezone.utc).isoformat(),
            "entries": []
        }

        # Add negative evidence if required phase
        if phase_num in [1, 6, 9, 11, 12]:
            output_data["negative_evidence_log"] = self.neg_evidence_logger.get_log()

        # Add adversarial tracking for red team phases
        if phase_num in [8, 9, 12]:
            output_data["adversarial_prompts"] = self.adversarial_tracker.get_triggers()

        # Validate output
        validator = UniversalValidation()
        valid, errors = validator.validate_phase_output(phase_num, output_data)
        if not valid:
            logger.error(f"Phase {phase_num} validation failed: {errors}")
            return {"error": "Validation failed", "errors": errors}

        self.completed_phases.add(phase_num)
        self.phase_outputs[phase_num] = output_data

        return output_data
```

## 9) EXECUTION PIPELINE

```bash
# Run complete analysis with enhanced validation
python scripts/phase_orchestrator.py --country IT --phases 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14

# Validate only (no execution)
python scripts/phase_orchestrator.py --country IT --phases 0 1 2 --validate-only

# Run fabrication check
python scripts/fabrication_checker.py

# Check phase compliance
python scripts/check_phase_compliance.py --phase 7 --country IT

# Run with negative evidence logging
python scripts/phase_orchestrator.py --country IT --phase 9 --log-negative-evidence
```

## 10) QUALITY GATES

```python
QUALITY_GATES = {
    "provenance_completeness": 0.95,  # 95% must have full provenance
    "groundedness_score": 0.9,        # 90% claims must be grounded
    "alternative_explanations": 1.0,   # 100% must have alternatives
    "translation_safeguards": 1.0,     # 100% non-EN must have safeguards
    "as_of_timestamps": 1.0,          # 100% must have timestamps
    "negative_evidence_logs": 1.0,    # 100% searches must log negatives
    "npkt_compliance": 1.0,           # 100% numerics must have NPKT
    "leonardo_standard": 0.9,         # 90% tech claims meet standard
    "adversarial_tracking": 1.0,      # 100% red team phases track prompts
    "no_averaging_conflicts": 1.0     # 100% conflicts shown as ranges
}
```

## 11) COMMON FAILURE MODES & FIXES

### Top Failures from QA Review

1. **Missing as_of timestamps**
   - **Impact:** FAIL
   - **Fix:** Add `as_of: datetime.now(timezone.utc).isoformat()` to every entry

2. **No alternative explanations**
   - **Impact:** FAIL
   - **Fix:** Include mundane explanations for every claim

3. **Numeric claims without NPKT**
   - **Impact:** INSUFFICIENT_EVIDENCE
   - **Fix:** Add NPKT reference with denomination for all numbers

4. **Non-EN sources without translation safeguards**
   - **Impact:** FAIL
   - **Fix:** Apply translation safeguards with confidence adjustment

5. **Conflicting numbers averaged**
   - **Impact:** FAIL
   - **Fix:** Show as ranges, never average conflicts

6. **Generic technology categories**
   - **Impact:** FAIL
   - **Fix:** Specify sub-field (e.g., "NLP" not "AI")

7. **Less than 3 alternatives/indicators**
   - **Impact:** FAIL (phases 9, 12, 13)
   - **Fix:** Ensure ≥3 for required phases

---

**END v9.8 COMPLETE - All QA Patches Integrated**

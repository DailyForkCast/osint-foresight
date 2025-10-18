# CLAUDE CODE — MASTER PROMPT v9.6 SEQUENTIAL
## Python Implementation Framework with Enhanced Phase Validation

**Version:** 9.6 SEQUENTIAL
**Date:** 2025-09-21
**Purpose:** Python-based OSINT analysis with enhanced phase schemas and stricter validation
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

## 1) CORE PYTHON IMPLEMENTATION

```python
import json
import hashlib
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
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
    translation_safeguards: Optional[Dict] = None
    as_of: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def validate(self) -> Tuple[bool, str]:
        """Validate provenance completeness"""
        if not self.url:
            return False, "Missing URL"
        if not self.access_date:
            return False, "Missing access_date"
        if self.verification_method == "sha256" and not self.archived_url:
            return False, "SHA256 requires local file path"
        if not self.archived_url and "wayback" not in self.verification_method:
            return False, "Web sources require wayback/cached URL"
        return True, "Valid"

class FabricationChecker:
    """Enhanced fabrication prevention system"""

    @staticmethod
    def validate_number(value: Any, source: str) -> Tuple[bool, str]:
        """Check if a number has proper verification"""
        if isinstance(value, (int, float)):
            if not source or "EXAMPLE" in source.upper():
                return False, f"Number {value} lacks verification source"
            if "[VERIFIED DATA]" not in source:
                return False, f"Number {value} missing [VERIFIED DATA] marker"
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

@dataclass
class PhaseValidator:
    """Validates phase outputs against requirements"""

    phase_number: int
    phase_name: str
    required_outputs: List[str]
    required_schemas: Dict[str, List[str]]

    def validate_output(self, output_data: Dict) -> Tuple[bool, List[str]]:
        """Validate phase output completeness"""
        errors = []

        # Check as_of timestamp
        if 'as_of' not in output_data:
            errors.append("Missing as_of timestamp at phase level")

        # Check required outputs exist
        for required_file in self.required_outputs:
            if required_file not in output_data.get('files', []):
                errors.append(f"Missing required output: {required_file}")

        # Validate schemas for each entry
        for schema_name, required_fields in self.required_schemas.items():
            if schema_name in output_data:
                for entry in output_data[schema_name]:
                    for field in required_fields:
                        if field not in entry:
                            errors.append(f"Missing {field} in {schema_name}")

                    # Special validations
                    if 'alternative_explanations' not in entry:
                        errors.append(f"Missing alternative_explanations in {schema_name}")

                    if 'evidence_quote' in required_fields and not entry.get('evidence_quote'):
                        errors.append(f"Empty evidence_quote in {schema_name}")

                    if 'provenance_bundle' in entry:
                        pb = ProvenanceBundle(**entry['provenance_bundle'])
                        valid, msg = pb.validate()
                        if not valid:
                            errors.append(f"Invalid provenance: {msg}")

        return len(errors) == 0, errors

class PhaseOrchestrator:
    """Orchestrates sequential phase execution with validation"""

    def __init__(self, country: str):
        self.country = country
        self.phases = self._initialize_phases()
        self.completed_phases = set()
        self.phase_outputs = {}

    def _initialize_phases(self) -> Dict[int, PhaseValidator]:
        """Initialize all phase validators with schemas"""
        return {
            0: PhaseValidator(
                0, "Setup & Context",
                ["country_profile.json", "research_parameters.yaml", "threat_vectors.md"],
                {}
            ),
            1: PhaseValidator(
                1, "Data Source Validation",
                ["data_sources_validated.json", "collection_capabilities.yaml", "coverage_gaps.md"],
                {
                    "sources": ["id", "url", "archived_url", "access_date", "paywall_status",
                              "rate_limit_note", "coverage_detected", "as_of"]
                }
            ),
            2: PhaseValidator(
                2, "Technology Landscape",
                ["tech_landscape.md", "tech_landscape_table.csv"],
                {
                    "technologies": ["tech_name", "TRL_or_maturity", "evidence_quote",
                                   "china_overlap", "exploitation_path", "alternative_explanations",
                                   "as_of", "provenance_bundle"]
                }
            ),
            3: PhaseValidator(
                3, "Supply Chain Analysis",
                ["supply_chain_storyline.md", "dependency_table.csv"],
                {
                    "dependencies": ["supplier_name", "contract_identifier", "denomination",
                                   "evidence_quote", "alternative_explanations", "as_of",
                                   "provenance_bundle"]
                }
            ),
            4: PhaseValidator(
                4, "Institutions Mapping",
                ["institutions.md", "institutions_table.csv"],
                {
                    "institutions": ["institution_name", "department", "evidence_quote",
                                   "china_linkage", "alternative_explanations", "as_of",
                                   "provenance_bundle"]
                }
            ),
            5: PhaseValidator(
                5, "Funding Flows",
                ["funding_flows.md", "funding_flows_table.csv"],
                {
                    "funding": ["source_name", "program_or_budget_line", "time_range",
                              "evidence_quote", "alternative_explanations", "as_of",
                              "provenance_bundle"]
                }
            ),
            6: PhaseValidator(
                6, "International Links",
                ["international_links.md", "international_links_table.csv"],
                {
                    "links": ["partner_entity", "link_type", "evidence_quote",
                            "independence_justification", "alternative_explanations",
                            "as_of", "provenance_bundle"]
                }
            ),
            7: PhaseValidator(
                7, "Risk Assessment Initial",
                ["risk_assessment_initial.md", "risk_matrix.csv"],
                {
                    "risks": ["risk_id", "technology", "pathway", "evidence_quote",
                            "alternative_explanations", "confidence", "confidence_rationale",
                            "as_of", "provenance_bundle"]
                }
            ),
            8: PhaseValidator(
                8, "China Strategy Assessment",
                ["china_strategy.md", "china_strategy_table.csv"],
                {
                    "strategies": ["strategy_id", "focus_area", "evidence_quote",
                                 "translation_safeguards", "alternative_explanations",
                                 "confidence", "confidence_rationale", "as_of",
                                 "provenance_bundle"]
                }
            ),
            9: PhaseValidator(
                9, "Red Team Analysis",
                ["red_team.md", "red_team_matrix.csv"],
                {
                    "hypotheses": ["hypothesis_id", "hypothesis_text", "evidence_for",
                                 "evidence_against", "adversarial_prompt_triggered",
                                 "negative_evidence_log", "confidence", "as_of",
                                 "provenance_bundle"]
                }
            ),
            10: PhaseValidator(
                10, "Comprehensive Risk Assessment",
                ["comprehensive_risk_matrix.json", "mitigation_strategies.md", "risk_timeline.json"],
                {}
            ),
            11: PhaseValidator(
                11, "Strategic Posture",
                ["strategic_posture_assessment.json", "policy_contradictions.md", "forecast_scenarios.json"],
                {}
            ),
            12: PhaseValidator(
                12, "Foresight Analysis",
                ["scenario_narratives.json", "early_warning_indicators.json",
                 "decision_triggers.md", "monitoring_priorities.json"],
                {}
            ),
            13: PhaseValidator(
                13, "Extended Analysis",
                ["extended_findings.json", "cross_reference_matrix.json",
                 "strategic_implications.md", "cascade_analysis.json"],
                {}
            ),
            14: PhaseValidator(
                14, "Closeout & Handoff",
                ["executive_brief.pdf", "master_findings.json", "implementation_roadmap.md",
                 "monitoring_dashboard_spec.json", "lessons_learned.md"],
                {}
            )
        }

    def check_dependencies(self, phase: int) -> bool:
        """Check if phase dependencies are met"""
        dependencies = {
            0: [],
            1: [0],
            2: [1],
            3: [2],
            4: [3],
            5: [3],
            6: [2, 3, 4, 5],
            7: [6],
            8: [7],
            9: [7],
            10: [8, 9],
            11: [10],
            12: [11],
            13: [12],
            14: list(range(14))
        }

        for dep in dependencies.get(phase, []):
            if dep not in self.completed_phases:
                logger.error(f"Phase {phase} requires phase {dep} to be completed first")
                return False
        return True

    def execute_phase(self, phase_num: int, **kwargs) -> Dict:
        """Execute a specific phase with validation"""
        if not self.check_dependencies(phase_num):
            return {"error": "Dependencies not met"}

        validator = self.phases[phase_num]
        logger.info(f"Executing Phase {phase_num}: {validator.phase_name}")

        # Phase-specific execution logic would go here
        # This is a template showing the structure

        output_data = {
            "phase": phase_num,
            "phase_name": validator.phase_name,
            "country": self.country,
            "as_of": datetime.now(timezone.utc).isoformat(),
            "files": validator.required_outputs,
            # Add phase-specific data here
        }

        # Validate output
        valid, errors = validator.validate_output(output_data)
        if not valid:
            logger.error(f"Phase {phase_num} validation failed: {errors}")
            return {"error": "Validation failed", "errors": errors}

        self.completed_phases.add(phase_num)
        self.phase_outputs[phase_num] = output_data

        return output_data

class NPKTProcessor:
    """Numeric Processing & Known Truth handler"""

    def __init__(self, data_path: Path):
        self.data_path = data_path
        self.known_truths = {}

    def register_truth(self, identifier: str, value: Any, source: str, verification: str):
        """Register a known truth value"""
        self.known_truths[identifier] = {
            "value": value,
            "source": source,
            "verification": verification,
            "registered_at": datetime.now(timezone.utc).isoformat()
        }

    def verify_claim(self, identifier: str, claimed_value: Any) -> Tuple[bool, str]:
        """Verify a claim against known truth"""
        if identifier not in self.known_truths:
            return False, "INSUFFICIENT_EVIDENCE"

        truth = self.known_truths[identifier]
        if truth["value"] != claimed_value:
            return False, f"Mismatch: claimed {claimed_value}, truth is {truth['value']}"

        return True, f"Verified against {truth['source']}"

    def compute_from_source(self, source_file: Path, computation: str) -> Optional[Any]:
        """Compute a value from source data"""
        try:
            # This would implement actual computation logic
            # Example: counting records, summing values, etc.
            pass
        except Exception as e:
            logger.error(f"Computation failed: {e}")
            return None

class TranslationSafeguards:
    """Handle non-English source validation"""

    @staticmethod
    def apply_safeguards(original: str, language: str) -> Dict:
        """Apply translation safeguards to non-English text"""
        result = {
            "original": original,
            "language": language,
            "translation": "",  # Would use actual translation service
            "back_translation": "",  # Translate back to check
            "translation_risk": False
        }

        # Check for divergence
        if result["back_translation"] != original:
            result["translation_risk"] = True
            logger.warning(f"Translation risk detected for {language} text")

        return result

class AlternativeExplanations:
    """Generate and track alternative explanations"""

    MUNDANE_EXPLANATIONS = {
        "timing_patterns": [
            "Publishing schedules (journals release on specific days)",
            "Conference deadlines (everyone submits same week)",
            "Fiscal calendars (year-end spending rushes)",
            "Academic calendars (semester deadlines)",
            "Industry events (trade show announcements)",
            "Regulatory deadlines (compliance dates)"
        ],
        "collaboration_patterns": [
            "Standard academic exchange",
            "EU Horizon Europe framework requirement",
            "Industry best practice",
            "Regulatory compliance",
            "Market competition response",
            "Technology maturity timing"
        ],
        "funding_patterns": [
            "Normal budget cycles",
            "Standard grant disbursement",
            "Routine R&D investment",
            "Regular procurement schedule"
        ]
    }

    @classmethod
    def generate_alternatives(cls, pattern_type: str, context: str) -> List[str]:
        """Generate relevant alternative explanations"""
        base_explanations = cls.MUNDANE_EXPLANATIONS.get(pattern_type, [])

        # Add context-specific alternatives
        contextual = []
        if "china" in context.lower():
            contextual.append("Normal trade relationship")
            contextual.append("Standard diplomatic engagement")

        return base_explanations + contextual

    @staticmethod
    def test_hypothesis(hypothesis: str, evidence_for: List[str],
                       evidence_against: List[str]) -> Dict:
        """Test a hypothesis against evidence"""
        return {
            "hypothesis": hypothesis,
            "evidence_for": evidence_for,
            "evidence_against": evidence_against,
            "evidence_balance": len(evidence_for) - len(evidence_against),
            "confidence": "Low" if len(evidence_against) > len(evidence_for) else "Medium"
        }

def main():
    """Main execution entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='OSINT Foresight Analysis Framework')
    parser.add_argument('--country', required=True, help='Target country code')
    parser.add_argument('--phases', nargs='+', type=int, help='Phases to execute')
    parser.add_argument('--validate-only', action='store_true', help='Only validate, don\'t execute')

    args = parser.parse_args()

    # Initialize orchestrator
    orchestrator = PhaseOrchestrator(args.country)

    # Execute requested phases
    for phase in args.phases or range(15):
        if args.validate_only:
            validator = orchestrator.phases[phase]
            logger.info(f"Validating Phase {phase}: {validator.phase_name}")
        else:
            result = orchestrator.execute_phase(phase)
            if "error" in result:
                logger.error(f"Phase {phase} failed: {result['error']}")
                break
            logger.info(f"Phase {phase} completed successfully")

    logger.info("Execution complete")

if __name__ == "__main__":
    main()
```

## 2) VALIDATION REQUIREMENTS

### Enhanced Phase Validation Rules

```python
class EnhancedValidation:
    """Stricter validation rules from v9.5 improvements"""

    PHASE_1_RULES = {
        "archived_url": "Required for all sources",
        "paywall_status": "Must be marked for Tier-A eligibility",
        "rate_limits": "Required for API sources",
        "robots_legal": "Required for scraped sources"
    }

    PHASE_2_RULES = {
        "specificity": "No generic categories (AI, quantum) without sub-field",
        "leonardo_standard": "Every tech must have 8 specific points",
        "alternative_explanations": "Mandatory for all collaborations",
        "translation_safeguards": "Required for non-EN sources"
    }

    PHASE_3_RULES = {
        "denomination": "Required (count/value/unit)",
        "npkt_reference": "Required for any totals",
        "independence_justification": "Required when comparing suppliers"
    }

    PHASE_4_RULES = {
        "department_field": "Required when source provides",
        "translation_safeguards": "Mandatory for non-EN institution names"
    }

    PHASE_5_RULES = {
        "time_range": "Cannot merge across different ranges",
        "dataset_version": "Cannot merge different versions",
        "npkt_reference": "Required for all numeric claims"
    }

    PHASE_6_RULES = {
        "negative_evidence_log": "Required - list what wasn't found",
        "independence_justification": "Required for multiple sources"
    }

    PHASE_7_RULES = {
        "specific_technology": "No generic risk categories",
        "exploitation_pathway": "Must be specific and evidenced",
        "confidence_rationale": "Must justify rating with evidence weight"
    }

    PHASE_8_RULES = {
        "cn_language": "Must include original + translation + back-translation",
        "translation_risk": "Must downgrade confidence if present",
        "alternative_explanations": "Required (routine diplomacy, etc.)"
    }

    PHASE_9_RULES = {
        "minimum_alternatives": "≥3 hypotheses per major claim",
        "adversarial_prompts": "Must log when triggered",
        "negative_evidence": "Must log queries with no results"
    }
```

## 3) DATA INFRASTRUCTURE

```python
DATA_PATHS = {
    "openalex": Path("F:/OSINT_Backups/openalex/"),
    "ted": Path("F:/TED_Data/monthly/"),
    "cordis": Path("F:/2025-09-14 Horizons/"),
    "sec_edgar": Path("F:/OSINT_DATA/SEC_EDGAR/"),
    "patents": Path("F:/OSINT_DATA/EPO_PATENTS/"),
    "artifacts": Path("C:/Projects/OSINT - Foresight/artifacts/"),
    "countries": Path("C:/Projects/OSINT - Foresight/countries/")
}

# Verified real data (not fabrications)
VERIFIED_NUMBERS = {
    "italy_china_h2020": 168,  # Source: analysis/italy_china_project_ids.json
    "italy_china_horizon": 54,  # Source: analysis/italy_china_project_ids.json
    "italy_china_total": 222,  # 168 + 54
    "germany_china_sample": 68  # OpenAlex sample
}
```

## 4) ANTI-FABRICATION ENFORCEMENT

```python
class StrictAntiF abrication:
    """Zero-tolerance fabrication prevention"""

    FORBIDDEN_PRACTICES = [
        "Extrapolating from single country to EU totals",
        "Stating expected without [PROJECTION] marker",
        "Using examples without [EXAMPLE ONLY] marker",
        "Mixing real data with illustrative scenarios",
        "Creating numbers without source verification",
        "Using sha256 for web sources (only for downloads)"
    ]

    REQUIRED_MARKERS = {
        "verified": "[VERIFIED DATA]",
        "hypothetical": "[HYPOTHETICAL EXAMPLE]",
        "illustrative": "[ILLUSTRATIVE ONLY]",
        "projection": "[PROJECTION - NOT VERIFIED]",
        "example": "[EXAMPLE ONLY]",
        "gap": "[EVIDENCE GAP:]"
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
            missing.append("too_generic")

        return len(missing) == 0, missing
```

## 6) EXECUTION PIPELINE

```bash
# Run complete analysis
python scripts/phase_orchestrator.py --country IT --phases 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14

# Validate only (no execution)
python scripts/phase_orchestrator.py --country IT --phases 0 1 2 --validate-only

# Run fabrication check
python scripts/fabrication_checker.py

# Schedule regular checks
python scripts/schedule_fabrication_checks.py
```

## 7) QUALITY GATES

```python
QUALITY_GATES = {
    "provenance_completeness": 0.95,  # 95% must have full provenance
    "groundedness_score": 0.9,        # 90% claims must be grounded
    "alternative_explanations": 1.0,   # 100% must have alternatives
    "translation_safeguards": 1.0,     # 100% non-EN must have safeguards
    "as_of_timestamps": 1.0,          # 100% must have timestamps
    "negative_evidence_logs": 1.0     # 100% searches must log negatives
}
```

---

**END v9.6 SEQUENTIAL - Python Implementation with Enhanced Validation**

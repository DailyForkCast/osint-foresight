#!/usr/bin/env python3
"""
CORE VALIDATION FRAMEWORK v9.8
Complete implementation of Master Prompt v9.8 validation requirements
Zero Fabrication Protocol + Universal Validation + NPKT References
"""

import json
import hashlib
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# SECTION 1: CONFIDENCE AND EVIDENCE LEVELS
# ============================================================================

class ConfidenceLevel(Enum):
    """Evidence confidence levels per v9.8"""
    VERY_HIGH = (0.9, 1.0, "Very high confidence - multiply verified")
    HIGH = (0.6, 0.9, "High confidence - well evidenced")
    MEDIUM = (0.3, 0.6, "Medium confidence - partially evidenced")
    LOW = (0.0, 0.3, "Low confidence - provisional finding")

    def __init__(self, min_val: float, max_val: float, description: str):
        self.min_val = min_val
        self.max_val = max_val
        self.description = description

    @classmethod
    def from_score(cls, score: float) -> 'ConfidenceLevel':
        """Get confidence level from numeric score"""
        for level in cls:
            if level.min_val <= score <= level.max_val:
                return level
        return cls.LOW

class AdmiraltyScale(Enum):
    """Admiralty evidence rating system"""
    A1 = ("Completely reliable", "Confirmed")
    A2 = ("Usually reliable", "Probably true")
    B2 = ("Usually reliable", "Possibly true")
    C3 = ("Fairly reliable", "Doubtful")
    D = ("Not usually reliable", "Cannot judge")
    E = ("Unreliable", "Improbable")
    F = ("Cannot be judged", "Known false")

    def __init__(self, reliability: str, credibility: str):
        self.reliability = reliability
        self.credibility = credibility

# ============================================================================
# SECTION 2: TRANSLATION SAFEGUARDS
# ============================================================================

@dataclass
class TranslationSafeguards:
    """Translation validation for non-English sources"""
    original_text: str
    translated_text: str
    source_language: str
    back_translation: Optional[str] = None
    translation_risk: str = "low"  # low/medium/high
    confidence_adjustment: float = 1.0  # Multiply confidence by this factor
    translation_method: str = "automated"  # automated/professional/verified

    def validate(self) -> Tuple[bool, str]:
        """Check translation safeguards are complete"""
        if not self.original_text or not self.translated_text:
            return False, "Missing original or translated text"

        if self.translation_risk == "high" and self.confidence_adjustment >= 1.0:
            return False, "High risk translation should reduce confidence"

        if self.source_language != "en" and not self.back_translation:
            return False, "Non-English source requires back-translation"

        return True, "Valid"

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)

# ============================================================================
# SECTION 3: PROVENANCE BUNDLE SYSTEM
# ============================================================================

@dataclass
class ProvenanceBundle:
    """Complete provenance for any claim - v9.8 compliant"""
    url: str
    access_date: str  # UTC ISO-8601
    archived_url: Optional[str] = None
    verification_method: str = "direct_quote_verification"
    quoted_span: str = ""
    locator: str = ""  # page/paragraph/section
    admiralty_rating: Optional[AdmiraltyScale] = None
    independence_justification: Optional[str] = None
    translation_safeguards: Optional[TranslationSafeguards] = None
    as_of: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    sha256_hash: Optional[str] = None  # For downloaded files

    def validate(self) -> Tuple[bool, str]:
        """Validate provenance completeness"""
        if not self.url:
            return False, "Missing URL"

        if not self.access_date:
            return False, "Missing access_date"

        if not self.as_of:
            return False, "Missing as_of timestamp"

        # Check verification method requirements
        if self.verification_method == "sha256" and not self.sha256_hash:
            return False, "SHA256 verification requires hash"

        if not self.archived_url and "file://" not in self.url:
            return False, "Web sources require archived URL or wayback machine"

        if self.translation_safeguards:
            valid, msg = self.translation_safeguards.validate()
            if not valid:
                return False, f"Translation issue: {msg}"

        return True, "Valid"

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        if self.admiralty_rating:
            data['admiralty_rating'] = self.admiralty_rating.name
        if self.translation_safeguards:
            data['translation_safeguards'] = self.translation_safeguards.to_dict()
        return data

# ============================================================================
# SECTION 4: NPKT REFERENCE SYSTEM
# ============================================================================

class NPKTReference:
    """Numeric Processing & Known Truth reference - MANDATORY for all numbers"""

    VALID_DENOMINATIONS = ["count", "value", "unit", "percentage", "ratio", "score"]

    @staticmethod
    def create_reference(
        value: Union[int, float],
        source: str,
        method: str,
        denomination: str,
        currency: Optional[str] = None,
        unit: Optional[str] = None
    ) -> Dict:
        """Create NPKT reference for numeric claims"""

        if denomination not in NPKTReference.VALID_DENOMINATIONS:
            raise ValueError(f"Invalid denomination: {denomination}. Must be one of {NPKTReference.VALID_DENOMINATIONS}")

        if not source:
            raise ValueError("NPKT requires source for every number")

        reference = {
            "value": value,
            "source": source,
            "method": method,
            "denomination": denomination,
            "as_of": datetime.now(timezone.utc).isoformat(),
            "verification": "[VERIFIED DATA]" if source else None
        }

        if currency and denomination == "value":
            reference["currency"] = currency

        if unit and denomination == "unit":
            reference["unit_type"] = unit

        return reference

    @staticmethod
    def validate_numeric_claim(claim: Dict) -> Tuple[bool, str]:
        """Validate a numeric claim has proper NPKT"""
        if "value" not in claim:
            return False, "Missing numeric value"

        if "source" not in claim or not claim["source"]:
            return False, "Numeric claim lacks source"

        if "denomination" not in claim:
            return False, "Missing denomination (count/value/unit)"

        if claim["denomination"] not in NPKTReference.VALID_DENOMINATIONS:
            return False, f"Invalid denomination: {claim['denomination']}"

        if "[VERIFIED DATA]" not in str(claim.get("verification", "")):
            return False, "Numeric claim not verified"

        if "as_of" not in claim:
            return False, "Missing as_of timestamp for numeric claim"

        return True, "Valid"

# ============================================================================
# SECTION 5: NEGATIVE EVIDENCE LOGGER
# ============================================================================

class NegativeEvidenceLogger:
    """Track what wasn't found during searches - MANDATORY for phases 1,6,9,11,12"""

    def __init__(self):
        self.negative_evidence = []
        self.search_count = 0
        self.null_results_count = 0

    def log_search_without_results(self, query: str, source: str, timestamp: Optional[str] = None):
        """Log searches that yielded no results"""
        if not timestamp:
            timestamp = datetime.now(timezone.utc).isoformat()

        self.negative_evidence.append({
            "type": "search_null_result",
            "query": query,
            "source": source,
            "timestamp": timestamp,
            "result": "NO_RESULTS",
            "significance": "Absence of evidence logged"
        })

        self.search_count += 1
        self.null_results_count += 1

        logger.info(f"Negative evidence: No results for '{query}' in {source}")

    def log_missing_expected_data(self, expected: str, location: str, significance: str):
        """Log when expected data is missing"""
        self.negative_evidence.append({
            "type": "missing_expected",
            "expected": expected,
            "location": location,
            "result": "NOT_FOUND",
            "significance": significance,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

        logger.warning(f"Missing expected data: {expected} at {location}")

    def log_data_gap(self, gap_type: str, description: str, impact: str):
        """Log identified data gaps"""
        self.negative_evidence.append({
            "type": "data_gap",
            "gap_type": gap_type,
            "description": description,
            "impact": impact,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

        logger.warning(f"Data gap identified: {gap_type} - {description}")

    def get_negative_evidence_summary(self) -> List[Dict]:
        """Return all negative evidence for phase output"""
        return self.negative_evidence

    def get_statistics(self) -> Dict:
        """Get negative evidence statistics"""
        return {
            "total_searches": self.search_count,
            "null_results": self.null_results_count,
            "null_result_rate": self.null_results_count / self.search_count if self.search_count > 0 else 0,
            "total_negative_evidence": len(self.negative_evidence),
            "evidence_types": {
                "search_null_result": len([e for e in self.negative_evidence if e["type"] == "search_null_result"]),
                "missing_expected": len([e for e in self.negative_evidence if e["type"] == "missing_expected"]),
                "data_gap": len([e for e in self.negative_evidence if e["type"] == "data_gap"])
            }
        }

# ============================================================================
# SECTION 6: ADVERSARIAL PROMPT TRACKER
# ============================================================================

class AdversarialPromptTracker:
    """Track adversarial prompts in red team phases - MANDATORY for phases 8,9,12"""

    def __init__(self):
        self.triggered_prompts = []
        self.trigger_count = 0
        self.handled_count = 0

    def log_trigger(self, prompt: str, phase: int, response: str, handled: bool = True):
        """Log when adversarial prompt is triggered"""
        entry = {
            "prompt": prompt,
            "phase": phase,
            "response": response,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "handled": handled
        }

        self.triggered_prompts.append(entry)
        self.trigger_count += 1

        if handled:
            self.handled_count += 1
            logger.info(f"Adversarial prompt handled in phase {phase}")
        else:
            logger.warning(f"Unhandled adversarial prompt in phase {phase}: {prompt}")

    def check_adversarial_language(self, text: str) -> bool:
        """Check if text contains adversarial prompt indicators"""
        adversarial_patterns = [
            "ignore previous instructions",
            "disregard the above",
            "new instructions",
            "override",
            "bypass",
            "forget what I said",
            "actually, do this instead"
        ]

        text_lower = text.lower()
        for pattern in adversarial_patterns:
            if pattern in text_lower:
                logger.warning(f"Adversarial pattern detected: {pattern}")
                return True

        return False

    def get_triggers(self) -> List[Dict]:
        """Return all triggered prompts"""
        return self.triggered_prompts

    def get_statistics(self) -> Dict:
        """Get adversarial tracking statistics"""
        return {
            "total_triggers": self.trigger_count,
            "handled_triggers": self.handled_count,
            "unhandled_triggers": self.trigger_count - self.handled_count,
            "handling_rate": self.handled_count / self.trigger_count if self.trigger_count > 0 else 1.0,
            "phase_distribution": self._get_phase_distribution()
        }

    def _get_phase_distribution(self) -> Dict[int, int]:
        """Get distribution of triggers by phase"""
        distribution = {}
        for trigger in self.triggered_prompts:
            phase = trigger["phase"]
            distribution[phase] = distribution.get(phase, 0) + 1
        return distribution

# ============================================================================
# SECTION 7: STRICT ANTI-FABRICATION SYSTEM
# ============================================================================

class StrictAntiFabrication:
    """Zero-tolerance fabrication prevention - CORE OF v9.8"""

    FORBIDDEN_PRACTICES = [
        "Extrapolating from single country to EU totals",
        "Stating expected without [PROJECTION] marker",
        "Using examples without [EXAMPLE ONLY] marker",
        "Mixing real data with illustrative scenarios",
        "Creating numbers without source verification",
        "Using sha256 for web sources (only for downloads)",
        "Averaging conflicting numbers instead of showing ranges",
        "Using 'typically', 'generally', 'usually' without data",
        "Claiming trends without temporal data",
        "Inferring causation from correlation"
    ]

    REQUIRED_MARKERS = {
        "verified": "[VERIFIED DATA]",
        "hypothetical": "[HYPOTHETICAL EXAMPLE]",
        "illustrative": "[ILLUSTRATIVE ONLY]",
        "projection": "[PROJECTION - NOT VERIFIED]",
        "example": "[EXAMPLE ONLY]",
        "gap": "[EVIDENCE GAP:]",
        "insufficient": "[INSUFFICIENT EVIDENCE]",
        "conflicting": "[CONFLICTING DATA - SHOWN AS RANGE]"
    }

    FORBIDDEN_TERMS = [
        'expected', 'anticipated', 'projected', 'estimated',
        'could reach', 'likely', 'typically', 'generally',
        'usually', 'probably', 'presumably', 'apparently',
        'seemingly', 'roughly', 'approximately', 'about'
    ]

    @classmethod
    def validate_text(cls, text: str) -> Tuple[bool, List[str]]:
        """Validate text for fabrication violations"""
        violations = []

        # Check for forbidden terms without proper markers
        for term in cls.FORBIDDEN_TERMS:
            if term in text.lower():
                # Check if it has appropriate marker
                if not any(marker in text for marker in cls.REQUIRED_MARKERS.values()):
                    violations.append(f"Forbidden term '{term}' without required marker")

        # Check for mixed verified and hypothetical
        if cls._check_mixed_content(text):
            violations.append("Mixed verified and hypothetical content in same section")

        # Check for numeric claims without verification
        numbers = re.findall(r'\b\d+(?:\.\d+)?\b', text)
        for number in numbers:
            if float(number) > 100:  # Significant numbers
                if "[VERIFIED DATA]" not in text:
                    violations.append(f"Number {number} lacks [VERIFIED DATA] marker")

        return len(violations) == 0, violations

    @classmethod
    def _check_mixed_content(cls, text: str) -> bool:
        """Ensure verified and hypothetical content aren't mixed"""
        if "[VERIFIED DATA]" in text and "[HYPOTHETICAL" in text:
            # Split by paragraphs
            paragraphs = text.split('\n\n')
            for para in paragraphs:
                if "[VERIFIED DATA]" in para and "[HYPOTHETICAL" in para:
                    return True
        return False

    @classmethod
    def validate_number(cls, value: Any, source: str, npkt: Optional[Dict] = None) -> Tuple[bool, str]:
        """Check if a number has proper verification"""
        if isinstance(value, (int, float)):
            if not source or "EXAMPLE" in source.upper():
                return False, f"Number {value} lacks verification source"

            if "[VERIFIED DATA]" not in source:
                return False, f"Number {value} missing [VERIFIED DATA] marker"

            if value > 1000 and not npkt:
                return False, f"Number {value} lacks NPKT reference"

            if npkt:
                valid, msg = NPKTReference.validate_numeric_claim(npkt)
                if not valid:
                    return False, f"Number {value} NPKT validation failed: {msg}"

        return True, "Valid"

    @classmethod
    def check_conflicting_numbers(cls, data: List[Dict]) -> Tuple[bool, str]:
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
                    return False, f"Conflicting values for {metric} appear averaged instead of shown as range"

        return True, "Valid - conflicts shown as ranges"

    @classmethod
    def generate_compliance_report(cls, text: str, data: List[Dict]) -> Dict:
        """Generate comprehensive anti-fabrication compliance report"""
        text_valid, text_violations = cls.validate_text(text)
        numbers_valid, numbers_msg = cls.check_conflicting_numbers(data)

        return {
            "compliant": text_valid and numbers_valid,
            "text_validation": {
                "valid": text_valid,
                "violations": text_violations
            },
            "number_validation": {
                "valid": numbers_valid,
                "message": numbers_msg
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "framework_version": "v9.8"
        }

# ============================================================================
# SECTION 8: UNIVERSAL VALIDATION RULES
# ============================================================================

class UniversalValidation:
    """Universal validation rules from QA patches - MANDATORY FOR ALL PHASES"""

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
        elif not self._is_valid_iso_timestamp(output["as_of"]):
            errors.append("FAIL: Invalid as_of timestamp format (must be ISO-8601)")

        if "timestamp" not in output:
            errors.append("FAIL: Missing timestamp field")

        if "country" not in output:
            errors.append("FAIL: Missing country field")

        # Entry-level validation
        for i, entry in enumerate(output.get("entries", [])):
            entry_errors = self._validate_entry(entry, phase, i)
            errors.extend(entry_errors)

        # Phase-specific validation
        phase_errors = self._validate_phase_specific(phase, output)
        errors.extend(phase_errors)

        return len(errors) == 0, errors

    def _validate_entry(self, entry: Dict, phase: int, index: int) -> List[str]:
        """Validate individual entry"""
        errors = []
        prefix = f"Entry {index}"

        # As-of check
        if "as_of" not in entry:
            errors.append(f"{prefix}: FAIL - Missing as_of")

        # Alternative explanations check
        if "alternative_explanations" not in entry:
            errors.append(f"{prefix}: FAIL - Missing alternative_explanations")

        # Translation safeguards check
        if entry.get("language") and entry["language"] != "en":
            if "translation_safeguards" not in entry:
                errors.append(f"{prefix}: FAIL - Non-EN source missing translation_safeguards")

        # NPKT check for numerics
        if "value" in entry and isinstance(entry["value"], (int, float)):
            if "npkt_reference" not in entry:
                errors.append(f"{prefix}: INSUFFICIENT_EVIDENCE - Numeric {entry['value']} lacks NPKT")
            else:
                valid, msg = NPKTReference.validate_numeric_claim(entry["npkt_reference"])
                if not valid:
                    errors.append(f"{prefix}: FAIL - NPKT validation: {msg}")

        return errors

    def _validate_phase_specific(self, phase: int, output: Dict) -> List[str]:
        """Phase-specific validation rules"""
        errors = []

        # Negative evidence required phases
        if phase in [1, 6, 9, 11, 12]:
            if "negative_evidence_log" not in output:
                errors.append(f"FAIL: Phase {phase} missing negative_evidence_log")
            elif not isinstance(output["negative_evidence_log"], list):
                errors.append(f"FAIL: Phase {phase} negative_evidence_log must be array")

        # Alternative hypotheses requirements
        if phase in [9, 12]:
            for entry in output.get("entries", []):
                if "alternative_hypotheses" in entry:
                    if len(entry["alternative_hypotheses"]) < 3:
                        errors.append(f"FAIL: Phase {phase} requires ≥3 alternative hypotheses")

        # Phase 10 specific
        if phase == 10:
            for entry in output.get("entries", []):
                if "averaging_prohibited" not in entry or not entry["averaging_prohibited"]:
                    errors.append("FAIL: Phase 10 must not average conflicting assessments")

        # Phase 13 specific
        if phase == 13:
            for entry in output.get("entries", []):
                if "observable_indicators" in entry:
                    if len(entry["observable_indicators"]) < 3:
                        errors.append("FAIL: Phase 13 requires ≥3 observable indicators")

                if entry.get("numeric_forecasts") is not None:
                    errors.append("FAIL: Phase 13 numeric forecasts prohibited without NPKT")

        return errors

    def _is_valid_iso_timestamp(self, timestamp: str) -> bool:
        """Check if timestamp is valid ISO-8601"""
        try:
            datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return True
        except:
            return False

    def generate_validation_report(self, phase: int, output: Dict) -> Dict:
        """Generate comprehensive validation report"""
        valid, errors = self.validate_phase_output(phase, output)

        return {
            "phase": phase,
            "valid": valid,
            "errors": errors,
            "error_count": len(errors),
            "validation_timestamp": datetime.now(timezone.utc).isoformat(),
            "validator_version": "v9.8",
            "result": "PASS" if valid else "FAIL",
            "next_steps": self._get_remediation_steps(errors) if errors else []
        }

    def _get_remediation_steps(self, errors: List[str]) -> List[str]:
        """Get remediation steps for validation errors"""
        steps = []

        if any("as_of" in e for e in errors):
            steps.append("Add as_of timestamp to all entries")

        if any("alternative_explanations" in e for e in errors):
            steps.append("Add alternative_explanations to all entries")

        if any("NPKT" in e for e in errors):
            steps.append("Add NPKT references for all numeric claims")

        if any("translation_safeguards" in e for e in errors):
            steps.append("Add translation safeguards for non-English sources")

        if any("negative_evidence" in e for e in errors):
            steps.append("Log negative evidence for all searches")

        return steps

# ============================================================================
# SECTION 9: VALIDATION ORCHESTRATOR
# ============================================================================

class ValidationOrchestrator:
    """Orchestrate all validation components"""

    def __init__(self):
        self.universal_validator = UniversalValidation()
        self.neg_evidence_logger = NegativeEvidenceLogger()
        self.adversarial_tracker = AdversarialPromptTracker()
        self.anti_fabrication = StrictAntiFabrication

        self.validation_history = []
        self.validation_stats = {
            "total_validations": 0,
            "passed": 0,
            "failed": 0,
            "phases_validated": set()
        }

    def validate_complete_output(self, phase: int, output: Dict, text: str = None) -> Dict:
        """Complete validation of phase output"""

        # Universal validation
        universal_valid, universal_errors = self.universal_validator.validate_phase_output(phase, output)

        # Anti-fabrication check
        fabrication_report = None
        if text:
            fabrication_report = self.anti_fabrication.generate_compliance_report(
                text,
                output.get("entries", [])
            )

        # Compile results
        all_valid = universal_valid and (fabrication_report["compliant"] if fabrication_report else True)

        validation_result = {
            "phase": phase,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "overall_valid": all_valid,
            "universal_validation": {
                "valid": universal_valid,
                "errors": universal_errors
            },
            "anti_fabrication": fabrication_report if fabrication_report else {"skipped": "No text provided"},
            "negative_evidence_stats": self.neg_evidence_logger.get_statistics(),
            "adversarial_stats": self.adversarial_tracker.get_statistics() if phase in [8, 9, 12] else None,
            "result": "PASS" if all_valid else "FAIL"
        }

        # Update statistics
        self.validation_stats["total_validations"] += 1
        if all_valid:
            self.validation_stats["passed"] += 1
        else:
            self.validation_stats["failed"] += 1
        self.validation_stats["phases_validated"].add(phase)

        # Store in history
        self.validation_history.append(validation_result)

        return validation_result

    def get_validation_summary(self) -> Dict:
        """Get summary of all validations"""
        return {
            "statistics": {
                **self.validation_stats,
                "phases_validated": list(self.validation_stats["phases_validated"]),
                "pass_rate": self.validation_stats["passed"] / self.validation_stats["total_validations"]
                    if self.validation_stats["total_validations"] > 0 else 0
            },
            "negative_evidence": self.neg_evidence_logger.get_statistics(),
            "adversarial_tracking": self.adversarial_tracker.get_statistics(),
            "history_count": len(self.validation_history),
            "framework_version": "v9.8",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

# ============================================================================
# SECTION 10: DEMONSTRATION AND TESTING
# ============================================================================

def demonstrate_validation_framework():
    """Demonstrate the complete validation framework"""

    print("\n" + "="*80)
    print("CORE VALIDATION FRAMEWORK v9.8 - DEMONSTRATION")
    print("="*80)

    # Initialize orchestrator
    orchestrator = ValidationOrchestrator()

    # Example Phase 1 output (with deliberate errors for testing)
    phase_1_output = {
        "phase": 1,
        "name": "Data Source Validation",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "country": "IT",
        "entries": [
            {
                "name": "CORDIS",
                "type": "database",
                "retrieval_verified": True,
                # Missing: as_of, alternative_explanations, negative_evidence_log
            },
            {
                "name": "TED",
                "type": "database",
                "retrieval_verified": True,
                "as_of": datetime.now(timezone.utc).isoformat(),
                "alternative_explanations": "Standard EU procurement database",
                "negative_evidence_log": ["No access to unpublished tenders"],
                "value": 416877349668.15,  # Missing NPKT reference
            }
        ]
    }

    # Validate
    print("\n1. VALIDATING PHASE 1 OUTPUT")
    print("-" * 40)

    result = orchestrator.validate_complete_output(1, phase_1_output)

    print(f"Overall Valid: {result['overall_valid']}")
    print(f"Result: {result['result']}")

    if result['universal_validation']['errors']:
        print("\nValidation Errors:")
        for error in result['universal_validation']['errors'][:5]:  # Show first 5
            print(f"  - {error}")

    # Demonstrate NPKT reference creation
    print("\n2. CREATING NPKT REFERENCE")
    print("-" * 40)

    npkt = NPKTReference.create_reference(
        value=416877349668.15,
        source="ted_china_contracts_fixed table",
        method="SUM(contract_value) aggregation",
        denomination="value",
        currency="EUR"
    )

    print(f"NPKT Reference created:")
    print(json.dumps(npkt, indent=2))

    # Demonstrate anti-fabrication check
    print("\n3. ANTI-FABRICATION CHECK")
    print("-" * 40)

    bad_text = "The total is expected to reach approximately 500 billion typically"
    good_text = "[VERIFIED DATA] The total is €416,877,349,668.15 based on TED database analysis"

    bad_valid, bad_violations = StrictAntiFabrication.validate_text(bad_text)
    good_valid, good_violations = StrictAntiFabrication.validate_text(good_text)

    print(f"Bad text valid: {bad_valid}")
    if bad_violations:
        print(f"  Violations: {bad_violations}")

    print(f"Good text valid: {good_valid}")

    # Demonstrate negative evidence logging
    print("\n4. NEGATIVE EVIDENCE LOGGING")
    print("-" * 40)

    neg_logger = orchestrator.neg_evidence_logger
    neg_logger.log_search_without_results("China quantum computing Italy", "CORDIS")
    neg_logger.log_missing_expected_data("Patent filings 2024", "USPTO", "Critical for trend analysis")

    print(f"Negative evidence logged: {len(neg_logger.get_negative_evidence_summary())} items")

    # Final summary
    print("\n5. VALIDATION SUMMARY")
    print("-" * 40)

    summary = orchestrator.get_validation_summary()
    print(json.dumps(summary, indent=2))

    print("\n" + "="*80)
    print("DEMONSTRATION COMPLETE")
    print("Framework ready for production use with Master Prompt v9.8")
    print("="*80)

if __name__ == "__main__":
    demonstrate_validation_framework()

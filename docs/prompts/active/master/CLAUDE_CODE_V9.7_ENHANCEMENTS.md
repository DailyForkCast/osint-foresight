# CLAUDE CODE v9.7 ENHANCEMENTS
## QA Patch Integration for Phases 0-14

**Date:** 2025-09-21
**Purpose:** Claude Code specific enhancements from QA patches
**Note:** These enhancements supplement the main CLAUDE_CODE_MASTER_V9.7_SEQUENTIAL.md

---

## PHASE-SPECIFIC ENHANCEMENTS FROM QA PATCHES

### Phase 0: Setup & Context
**QA Issues Found:**
- Missing as_of timestamps
- No self-verification summary
- Independence justification not applied when combining sources

**Enhanced Requirements:**
```python
PHASE_0_ENHANCED = {
    "entries": [{
        "as_of": "ISO-8601",  # MANDATORY - was missing
        "translation_safeguards": "object|null",  # Required if non-EN
        "self_verification_summary": "string"  # NEW from QA patch
    }],
    "metadata": {
        "independence_justification": "string"  # NEW when combining sources
    }
}
```

### Phase 1: Data Source Validation
**QA Issues Found:**
- Missing negative evidence logs
- No retrieval verification
- Translation safeguards not applied

**Enhanced Requirements:**
```python
PHASE_1_ENHANCED = {
    "entries": [{
        "retrieval_verified": "boolean",  # MANDATORY
        "negative_evidence_log": ["string"],  # MANDATORY
        "archived_url": "string|null",  # NEW: Required
        "robots_legal_notes": "string|null",  # NEW
        "paywall_status": "string|null",  # NEW
        "stability_risk": "low|medium|high",  # NEW
        "rate_limit_note": "string|null"  # NEW
    }]
}
```

### Phase 2: Technology Landscape
**QA Issues Found:**
- Generic technology categories without sub-fields
- Missing alternative explanations
- No Leonardo Standard compliance scoring

**Enhanced Requirements:**
```python
PHASE_2_ENHANCED = {
    "entries": [{
        "sub_field": "string",  # MANDATORY for categories like AI
        "alternative_explanations": "string",  # MANDATORY
        "leonardo_standard_score": "integer/20",  # NEW: Explicit score
        "confidence_rationale": "string"  # NEW: Required
    }]
}
```

### Phase 3: Supply Chain Analysis
**QA Issues Found:**
- Missing denomination for values
- No NPKT references for aggregates
- Alternative explanations absent

**Enhanced Requirements:**
```python
PHASE_3_ENHANCED = {
    "entries": [{
        "denomination": ["count", "value", "unit"],  # MANDATORY
        "npkt_reference": "string|null",  # MANDATORY for aggregates
        "alternative_explanations": "string"  # MANDATORY
    }]
}
```

### Phase 4: Institutions Mapping
**QA Issues Found:**
- Department field missing when available
- Translation safeguards not applied for non-EN names
- No alternative explanations for linkages

**Enhanced Requirements:**
```python
PHASE_4_ENHANCED = {
    "entries": [{
        "department": "string|null",  # Required when available
        "translation_safeguards": "object|null",  # Required if non-EN
        "alternative_explanations": "string",  # MANDATORY for linkages
        "independence_justification": "string"  # NEW
    }]
}
```

### Phase 5: Funding Flows
**QA Issues Found:**
- Time ranges not specified
- Dataset versions not tracked
- NPKT missing for amounts

**Enhanced Requirements:**
```python
PHASE_5_ENHANCED = {
    "entries": [{
        "time_range": "YYYY-MM-DD..YYYY-MM-DD",  # MANDATORY
        "dataset_version": "string",  # MANDATORY
        "npkt_reference": "string|null",  # MANDATORY for amounts
        "merge_prohibition": "boolean"  # NEW: Cannot merge incompatible
    }]
}
```

### Phase 6: International Links
**QA Issues Found:**
- Negative evidence not logged
- Independence justification missing
- Alternative explanations absent

**Enhanced Requirements:**
```python
PHASE_6_ENHANCED = {
    "entries": [{
        "negative_evidence_log": ["string"],  # MANDATORY
        "independence_justification": "string",  # Required for multiple sources
        "alternative_explanations": "string"  # MANDATORY
    }]
}
```

### Phase 7: Risk Assessment Initial
**QA Issues Found:**
- Generic technology categories used
- Confidence rationale missing
- Pathways not specific

**Enhanced Requirements:**
```python
PHASE_7_ENHANCED = {
    "entries": [{
        "technology": "string",  # Must be specific, not category
        "pathway": "string",  # Must be specific
        "confidence_rationale": "string",  # MANDATORY
        "evidence_based": "boolean"  # NEW: Not speculative
    }]
}
```

### Phase 8: China Strategy Assessment
**QA Issues Found:**
- Back-translation not applied for CN sources
- Confidence not adjusted for translation risk
- Alternative explanations missing

**Enhanced Requirements:**
```python
PHASE_8_ENHANCED = {
    "entries": [{
        "back_translation": "object",  # Required for CN sources
        "confidence_adjustment": "float",  # Downgrade if translation risk
        "alternative_explanations": "string",  # Routine diplomacy, etc.
        "adversarial_prompt_triggered": "boolean"  # NEW
    }]
}
```

### Phase 9: Red Team Analysis
**QA Issues Found:**
- Less than 3 alternative hypotheses
- Adversarial prompts not tracked
- Negative evidence not logged

**Enhanced Requirements:**
```python
PHASE_9_ENHANCED = {
    "entries": [{
        "adversarial_prompt_triggered": "boolean",  # MANDATORY
        "alternative_hypotheses": ["string"],  # Min 3 required
        "negative_evidence_log": ["string"],  # MANDATORY
        "hypothesis_count": "integer"  # Must be ≥3
    }]
}
```

### Phase 10: Comprehensive Risk Assessment
**QA Issues Found:**
- Conflicting numbers averaged instead of shown as ranges
- Confidence scores missing rationales
- NPKT references absent

**Enhanced Requirements:**
```python
PHASE_10_ENHANCED = {
    "entries": [{
        "conflicting_assessments": "object",  # Show as ranges
        "averaging_prohibited": "boolean",  # TRUE - never average
        "confidence_score": "float",  # 0.0-1.0 MANDATORY
        "confidence_rationale": "string",  # MANDATORY
        "npkt_reference": "string|null"  # Required for numerics
    }]
}
```

### Phase 11: Strategic Posture
**QA Issues Found:**
- Negative evidence not logged
- Themes not categorized
- Alternative explanations missing

**Enhanced Requirements:**
```python
PHASE_11_ENHANCED = {
    "entries": [{
        "negative_evidence_log": ["string"],  # MANDATORY
        "theme_categorization": "string",  # NEW
        "alternative_explanations": "string"  # MANDATORY
    }]
}
```

### Phase 12: Foresight Analysis
**QA Issues Found:**
- Less than 3 observable indicators
- Numeric forecasts without NPKT
- Alternative explanations absent

**Enhanced Requirements:**
```python
PHASE_12_ENHANCED = {
    "entries": [{
        "observable_indicators": ["string"],  # Min 3 required
        "indicator_count": "integer",  # Must be ≥3
        "numeric_forecasts": "null",  # Prohibited without NPKT
        "alternative_explanations": "string"
    }]
}
```

### Phase 13: Extended Analysis
**QA Issues Found:**
- Cross-domain links not identified
- Second-order effects not tracked
- Alternative explanations missing

**Enhanced Requirements:**
```python
PHASE_13_ENHANCED = {
    "entries": [{
        "cross_domain_links": ["string"],  # MANDATORY
        "second_order_effects": ["string"],  # MANDATORY
        "cascade_analysis": "object",  # NEW
        "alternative_explanations": "string"
    }]
}
```

### Phase 14: Closeout & Handoff
**QA Issues Found:**
- Cross-phase consistency not checked
- Inconsistencies not logged
- Provenance chains incomplete

**Enhanced Requirements:**
```python
PHASE_14_ENHANCED = {
    "entries": [{
        "cross_phase_consistency": "object",  # MANDATORY
        "inconsistencies_logged": ["string"],  # MANDATORY
        "provenance_chain": "object",  # Complete for every claim
        "consistency_validation": "PASS|FAIL"  # NEW
    }]
}
```

---

## UNIVERSAL ENHANCEMENTS

### Critical Classes to Add

```python
class NegativeEvidenceLogger:
    """Track what wasn't found during searches"""

    def log_search_without_results(self, query: str, source: str, timestamp: str):
        """Log searches that yielded no results"""

    def log_missing_expected_data(self, expected: str, location: str, significance: str):
        """Log when expected data is missing"""

class TranslationSafeguardsEnhanced:
    """Enhanced translation validation for non-English sources"""

    def apply_safeguards(self, original: str, language: str) -> Dict:
        """Apply translation safeguards with confidence adjustment"""

class NPKTReferenceEnhanced:
    """Enhanced Numeric Processing & Known Truth reference"""

    def create_reference(self, value, source, method, denomination) -> Dict:
        """Create NPKT reference with mandatory denomination"""
```

### Universal Validation Rules

```python
UNIVERSAL_SAFEGUARDS = {
    "as_of_mandatory": "All entries must include as_of timestamp",
    "alternative_explanations_mandatory": "All entries must include alternative explanations",
    "non_en_translation_safeguards": "Non-EN sources require translation safeguards",
    "negative_evidence_logging": "Must log what wasn't found"
}

NUMERIC_ENFORCEMENT = {
    "npkt_required": "All totals require NPKT reference",
    "denomination_required": "Must specify count/value/unit",
    "no_totals_without_verification": "Totals only with valid NPKT",
    "no_averaging_conflicts": "Show conflicting numbers as ranges, never average"
}

ACCEPTANCE_TESTS = {
    "missing_as_of": "**FAIL**",
    "missing_alternative_explanations": "**FAIL**",
    "numeric_without_npkt": "**INSUFFICIENT_EVIDENCE**",
    "non_en_without_safeguards": "**FAIL**",
    "negative_evidence_not_logged": "**FAIL**",
    "conflicting_numbers_averaged": "**FAIL**"
}
```

---

## OPERATOR CHECKLISTS

### Pre-Phase Checklist (All Phases)
- [ ] Previous phase outputs validated
- [ ] Dependencies satisfied
- [ ] Negative evidence logger initialized
- [ ] Translation safeguards ready for non-EN sources
- [ ] NPKT tracking enabled for numerics

### Phase-Specific Checklists

**Phase 0:**
- [ ] As_of applied at phase start
- [ ] All baseline data sources/APIs logged with provenance
- [ ] Independence justification applied when combining configs
- [ ] Translation safeguards included if non-EN inputs
- [ ] Self-verification summary appended

**Phase 1:**
- [ ] Each source has retrieval verification
- [ ] Negative evidence logged for failed searches
- [ ] Translation safeguards for non-EN sources
- [ ] Rate limits and stability risks documented
- [ ] Alternative sources identified where applicable

**Phase 2:**
- [ ] Leonardo Standard applied (8-point specificity)
- [ ] No generic technology categories without sub-fields
- [ ] Alternative explanations for each technology
- [ ] Translation safeguards for foreign tech names
- [ ] Confidence scores with rationales

**Phase 3:**
- [ ] Denomination specified for all values
- [ ] NPKT references for all aggregates
- [ ] Alternative explanations for dependencies
- [ ] No unsourced supply chain claims
- [ ] Chokepoint analysis includes alternatives

**Phase 4:**
- [ ] Department included when available
- [ ] Translation safeguards for non-EN names
- [ ] Alternative explanations for all linkages
- [ ] Subsidiary relationships verified
- [ ] Independence of sources justified

**Phase 5:**
- [ ] Time ranges specified for all data
- [ ] Dataset versions tracked
- [ ] NPKT for all numeric amounts
- [ ] No merging across incompatible datasets
- [ ] Alternative funding sources considered

**Phase 6:**
- [ ] Negative evidence logged
- [ ] Independence justification provided
- [ ] Alternative explanations included
- [ ] Translation safeguards applied
- [ ] Link strength assessed objectively

**Phase 7:**
- [ ] Specific technologies not categories
- [ ] Confidence rationales provided
- [ ] Alternative explanations included
- [ ] Evidence-based not speculative
- [ ] Pathways are specific and verifiable

**Phase 8:**
- [ ] Back-translation for CN sources
- [ ] Confidence adjusted for translation risk
- [ ] Alternative explanations (routine diplomacy)
- [ ] Adversarial prompts logged
- [ ] Strategy elements evidenced

**Phase 9:**
- [ ] Minimum 3 alternative hypotheses
- [ ] Adversarial prompts tracked
- [ ] Negative evidence logged
- [ ] Hypothesis testing documented
- [ ] Evidence balance calculated

**Phase 10:**
- [ ] No averaging of conflicts
- [ ] Confidence scores 0.0-1.0
- [ ] Confidence rationales provided
- [ ] NPKT for all numerics
- [ ] Alternative explanations included

**Phase 11:**
- [ ] Negative evidence logged
- [ ] Themes categorized
- [ ] Alternative explanations provided
- [ ] Independence justified
- [ ] Posture evidence-based

**Phase 12:**
- [ ] Minimum 3 observable indicators
- [ ] No numeric forecasts without NPKT
- [ ] Alternative explanations included
- [ ] Scenarios grounded in evidence
- [ ] Indicators measurable

**Phase 13:**
- [ ] Cross-domain links identified
- [ ] Second-order effects tracked
- [ ] Cascade analysis completed
- [ ] Alternative explanations provided
- [ ] Extended findings evidenced

**Phase 14:**
- [ ] Cross-phase consistency checked
- [ ] Inconsistencies logged
- [ ] Provenance chains complete
- [ ] Alternative explanations for conclusions
- [ ] Handoff documentation complete

---

## COMMON FAILURE MODES & FIXES

### Top 5 Failures from QA Review

1. **Missing as_of timestamps**
   - **Impact:** FAIL
   - **Fix:** Add `as_of` to every entry and phase output

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

---

## IMPLEMENTATION NOTES

1. **Integration:** These enhancements should be integrated with the main v9.7 prompt
2. **Priority:** Focus on universal safeguards first (as_of, alternatives, NPKT)
3. **Testing:** Run fabrication checker after implementing each phase
4. **Documentation:** Update phase outputs to include all new required fields
5. **Validation:** Use enhanced validators before marking phase complete

---

**END CLAUDE CODE v9.7 ENHANCEMENTS**

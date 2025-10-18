# Master Prompt v9.6/v9.7 Complete Update Summary
**Date:** 2025-09-21
**Status:** Successfully Completed All Updates

## Overview

Successfully incorporated all ChatGPT QA improvements for phases 0-14 into master prompts:
- **CHATGPT_MASTER_PROMPT_V9.6_SEQUENTIAL.md** (upgraded from v9.4)
- **CLAUDE_CODE_MASTER_V9.7_SEQUENTIAL.md** (upgraded from v9.5/v9.6)

## Version History

| Prompt | Previous | Current | Changes |
|--------|----------|---------|---------|
| ChatGPT | v9.4 | v9.6 | Added complete schemas for phases 0-14 |
| Claude Code | v9.5 | v9.7 | Added Python implementation for phases 0-14 |

## Complete Improvements by Phase

### Phases 1-5 (Data Collection & Mapping)
#### Phase 1: Data Source Validation
- ✅ Added: `archived_url`, `robots_legal_notes`, `paywall_status`, `stability_risk`, `rate_limit_note`
- ✅ Enforces retrievability verification for all sources
- ✅ Tracks operational metadata for planning

#### Phase 2: Technology Landscape
- ✅ Added: `alternative_explanations`, `translation_safeguards`
- ✅ Enforces Leonardo Standard (8-point specificity)
- ✅ Rejects generic categories without sub-field specifics

#### Phase 3: Supply Chain
- ✅ Added: `denomination` field (count/value/unit)
- ✅ Requires NPKT reference for all aggregates
- ✅ Mandates alternative explanations for dependencies

#### Phase 4: Institutions
- ✅ Added: `department` field requirement when available
- ✅ Enforces translation safeguards for non-EN names
- ✅ Requires alternative explanations for all linkages

#### Phase 5: Funding Flows
- ✅ Added: `time_range`, `dataset_version` tracking
- ✅ Prevents merging across incompatible datasets
- ✅ Requires NPKT for all numeric claims

### Phases 6-9 (Analysis & Assessment)
#### Phase 6: International Links
- ✅ Added: Negative evidence logging requirement
- ✅ Mandates independence justification
- ✅ Requires alternative explanations for all partnerships

#### Phase 7: Risk Assessment Initial
- ✅ Added: `confidence_rationale` requirement
- ✅ Links risks to specific technologies (not categories)
- ✅ Requires evidence-based confidence ratings

#### Phase 8: China Strategy
- ✅ Added: Back-translation requirement for CN sources
- ✅ Downgrades confidence when translation risk detected
- ✅ Requires alternative explanations (routine diplomacy)

#### Phase 9: Red Team
- ✅ Added: `adversarial_prompt_triggered` tracking
- ✅ Requires ≥3 alternative hypotheses per claim
- ✅ Mandates negative evidence logging

### Phases 10-14 (Synthesis & Closeout) - NEW IN v9.6/v9.7
#### Phase 10: Comprehensive Risk Assessment
- ✅ Added complete `risk_entry_schema` with categories
- ✅ Prevents averaging conflicting numbers (show ranges)
- ✅ Requires confidence score 0.0-1.0 with rationale
- ✅ NPKT required for all numeric claims
- ✅ Alternative explanations mandatory

#### Phase 11: Strategic Posture
- ✅ Added `posture_entry_schema` with themes
- ✅ Requires negative evidence logging
- ✅ Mandates alternative explanations
- ✅ Independence justification for sources

#### Phase 12: Foresight Analysis (Note: Was incorrectly labeled as "Red Team Global" in patch)
- ✅ Added `foresight_entry_schema` with horizons
- ✅ Requires minimum 3 observable indicators per scenario
- ✅ No numeric forecasts without NPKT
- ✅ Alternative explanations required

#### Phase 13: Extended Analysis
- ✅ Added `extended_entry_schema`
- ✅ Requires cross-domain linking
- ✅ Second-order effects tracking
- ✅ Alternative explanations mandatory

#### Phase 14: Closeout & Handoff
- ✅ Added `closeout_entry_schema`
- ✅ Requires cross-phase consistency checks
- ✅ Inconsistencies must be logged
- ✅ Each conclusion needs provenance
- ✅ Alternative explanations for major conclusions

## Universal Improvements (All Phases)

### Mandatory Requirements
1. **as_of timestamps** - Required at phase AND item level
2. **Alternative explanations** - Required for ALL major claims
3. **Translation safeguards** - Required for ALL non-EN sources
4. **Negative evidence logs** - Required for phases 6, 9, 11, 12
5. **Provenance bundles** - Complete for every claim
6. **Admiralty Scale ratings** - For all evidence

### Enhanced Validation Rules
- Phase outputs missing `as_of` → **FAIL**
- Any numeric claim without NPKT → **INSUFFICIENT_EVIDENCE**
- Missing alternative_explanations → **FAIL**
- Non-EN source without translation_safeguards → **FAIL**
- Conflicting numbers averaged → **FAIL**
- Inconsistencies not logged → **FAIL**

## Anti-Fabrication Measures Status

### ✅ Maintained at Highest Level
- Zero-fabrication principle unchanged
- [VERIFIED DATA] marking requirements
- Segregation of real vs hypothetical
- SHA256 only for downloads (not web)
- INSUFFICIENT_EVIDENCE for missing data

### ✅ Enhanced with New Safeguards
- Negative evidence logging (what wasn't found)
- Translation risk flagging and confidence adjustment
- Adversarial prompt tracking in red team phases
- Stricter denomination requirements (count/value/unit)
- Cross-phase consistency checking in Phase 14
- Conflicting numbers shown as ranges, never averaged

## Python Implementation (Claude Code v9.7)

### New Classes & Methods
```python
# Enhanced validation for phases 10-14
class PhaseValidator:
    # Now includes validators for all 15 phases (0-14)

class EnhancedValidation:
    # Added rules for phases 10-14:
    PHASE_10_RULES = {
        "no_averaging": "Show conflicting numbers as ranges",
        "confidence_score": "Required 0.0-1.0 with rationale",
        "npkt_mandatory": "For all numeric claims"
    }

    PHASE_11_RULES = {
        "negative_evidence": "Required log of searches",
        "themes": "Must categorize posture claims"
    }

    PHASE_12_RULES = {
        "minimum_indicators": "≥3 observable per scenario",
        "no_numeric_forecasts": "Without NPKT"
    }

    PHASE_13_RULES = {
        "cross_domain": "Must link connections",
        "second_order": "Track cascade effects"
    }

    PHASE_14_RULES = {
        "consistency_check": "Cross-phase validation",
        "log_inconsistencies": "Must document conflicts"
    }
```

## Updated References

### Documents Updated
- ✅ README.md - Now points to v9.6 and v9.7
- ✅ Master prompt files created and archived
- ✅ Previous versions archived in `/docs/prompts/archive/2025-09-21-pre-v9.5/`

### File Locations
- ChatGPT v9.6: `docs/prompts/active/master/CHATGPT_MASTER_PROMPT_V9.6_SEQUENTIAL.md`
- Claude Code v9.7: `docs/prompts/active/master/CLAUDE_CODE_MASTER_V9.7_SEQUENTIAL.md`
- Archives: `docs/prompts/archive/2025-09-21-pre-v9.5/`

## Testing & Validation

### Recommended Tests
1. **Fabrication Check:**
   ```bash
   python scripts/fabrication_checker.py
   ```

2. **Phase Validation:**
   ```bash
   python scripts/phase_orchestrator.py --country IT --phases 0-14 --validate-only
   ```

3. **Schema Compliance:**
   - Check existing artifacts against new schemas
   - Verify all required fields present

## Key Takeaways

1. **Complete Coverage:** All phases 0-14 now have detailed schemas and validation rules
2. **Stricter Validation:** Every phase has acceptance tests and failure conditions
3. **Anti-Fabrication Enhanced:** Multiple layers of protection against data fabrication
4. **Consistency Enforcement:** Phase 14 now validates cross-phase consistency
5. **Observable Indicators:** Foresight analysis requires concrete, measurable indicators
6. **Translation Safety:** All non-English sources require full translation safeguards
7. **Negative Evidence:** What we didn't find is as important as what we did

## Next Steps

1. **Run validation** on existing artifacts to identify gaps
2. **Update phase executors** to implement new schemas
3. **Test cross-phase consistency** checks in Phase 14
4. **Monitor fabrication checker** for compliance

---

**Status:** All requested improvements successfully incorporated while maintaining highest anti-fabrication standards.

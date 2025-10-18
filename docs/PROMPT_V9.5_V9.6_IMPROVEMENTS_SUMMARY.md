# Master Prompt v9.5/v9.6 Improvements Summary
**Date:** 2025-09-21
**Status:** Successfully Updated

## Overview

ChatGPT provided detailed QA patches for phases 1-9, which have been incorporated into:
- **CHATGPT_MASTER_PROMPT_V9.5_SEQUENTIAL.md** (upgraded from v9.4)
- **CLAUDE_CODE_MASTER_V9.6_SEQUENTIAL.md** (upgraded from v9.5)

## Key Improvements Added

### 1. Enhanced Schema Definitions for Each Phase

Every phase now has detailed schema requirements with mandatory fields:

#### Phase 1 (Data Source Validation)
- Added: `archived_url`, `robots_legal_notes`, `paywall_status`, `stability_risk`, `rate_limit_note`
- Enforces retrievability verification for all sources
- Tracks operational metadata for planning

#### Phase 2 (Technology Landscape)
- Added: `alternative_explanations`, `translation_safeguards`
- Enforces Leonardo Standard (8-point specificity)
- Rejects generic categories without sub-field specifics

#### Phase 3 (Supply Chain)
- Added: `denomination` field (count/value/unit)
- Requires NPKT reference for all aggregates
- Mandates alternative explanations for dependencies

#### Phase 4 (Institutions)
- Added: `department` field requirement when available
- Enforces translation safeguards for non-EN names
- Requires alternative explanations for all linkages

#### Phase 5 (Funding Flows)
- Added: `time_range`, `dataset_version` tracking
- Prevents merging across incompatible datasets
- Requires NPKT for all numeric claims

#### Phase 6 (International Links)
- Added: Negative evidence logging requirement
- Mandates independence justification
- Requires alternative explanations for all partnerships

#### Phase 7 (Risk Assessment Initial)
- Added: `confidence_rationale` requirement
- Links risks to specific technologies (not categories)
- Requires evidence-based confidence ratings

#### Phase 8 (China Strategy)
- Added: Back-translation requirement for CN sources
- Downgrades confidence when translation risk detected
- Requires alternative explanations (routine diplomacy)

#### Phase 9 (Red Team)
- Added: `adversarial_prompt_triggered` tracking
- Requires ≥3 alternative hypotheses per claim
- Mandates negative evidence logging

### 2. Stricter Validation Rules

#### Universal Requirements (All Phases)
- `as_of` timestamp mandatory at phase AND item level
- Alternative explanations required for ALL major claims
- Translation safeguards for ALL non-EN sources
- Admiralty Scale ratings for ALL evidence

#### Acceptance Tests
- Phase outputs missing `as_of` → **FAIL**
- Any numeric claim without NPKT → **INSUFFICIENT_EVIDENCE**
- Missing alternative_explanations → **FAIL**
- Non-EN source without translation_safeguards → **FAIL**

### 3. Enhanced Anti-Fabrication Measures

All existing anti-fabrication measures remain intact and are strengthened:

#### Maintained Safeguards
- Zero-fabrication principle unchanged
- [VERIFIED DATA] marking requirements
- Segregation of real vs hypothetical
- SHA256 only for downloads (not web)

#### New Safeguards
- Negative evidence logging (what wasn't found)
- Translation risk flagging and confidence adjustment
- Adversarial prompt tracking in red team phase
- Stricter denomination requirements for numbers

### 4. Python Implementation Enhancements (Claude Code)

#### New Classes Added
- `PhaseValidator`: Validates each phase output against schema
- `EnhancedValidation`: Implements v9.5 stricter rules
- `AlternativeExplanations`: Generates mundane explanations
- `TranslationSafeguards`: Handles non-EN validation

#### Validation Pipeline
```python
# Each phase now validated against:
- Required outputs
- Required schema fields
- Alternative explanations
- Translation safeguards
- As_of timestamps
- Provenance bundles
```

## Backward Compatibility

All changes are **additive** - no existing functionality removed:
- Previous phase definitions preserved
- All anti-fabrication rules maintained
- Existing workflows still function
- New validations layer on top

## Testing Recommendations

1. Run fabrication checker to ensure compliance:
   ```bash
   python scripts/fabrication_checker.py
   ```

2. Validate phase outputs:
   ```bash
   python scripts/phase_orchestrator.py --country IT --phases 0-14 --validate-only
   ```

3. Check for missing fields in existing artifacts

## Summary

The v9.5/v9.6 updates successfully incorporate ChatGPT's QA improvements while maintaining the highest anti-fabrication standards. Key additions:

- ✅ Detailed schemas for phases 1-9
- ✅ Stricter validation requirements
- ✅ Alternative explanations mandatory
- ✅ Translation safeguards enforced
- ✅ Negative evidence logging
- ✅ As_of timestamps at all levels
- ✅ Zero-fabrication measures intact

The prompts are now more rigorous and will catch more potential issues during phase execution.

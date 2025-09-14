# TEMPORAL AWARENESS & CITATION PRECISION IMPLEMENTATION

## Executive Summary

Comprehensive implementation of temporal awareness and citation precision requirements across all OSINT Foresight phases, addressing critical issues identified with ChatGPT outputs on September 13, 2025.

## Critical Issues Addressed

### 1. Temporal Awareness Problems
- **Issue**: Recommendations targeting 2024 and early 2025 (already past)
- **Solution**: Mandatory temporal checks at start/end of every phase
- **Implementation**: 8-12 month minimum delays for all new initiatives

### 2. Citation Precision Problems
- **Issue**: Homepage-only citations without specific document URLs
- **Solution**: Exact URL requirements with accessed_date tracking
- **Implementation**: Validation system rejecting non-specific citations

## Implementation Components

### Core Requirements Documents

1. **Master Requirements** (`docs/prompts/MASTER_PROMPT_REQUIREMENTS.md`)
   - Combined temporal and citation requirements
   - Phase-specific guidelines
   - Common error examples

2. **Temporal Injection** (`docs/prompts/TEMPORAL_AWARENESS_INJECT.md`)
   - Start/end checks for every phase
   - Realistic timeline templates
   - Implementation delay factors

3. **Citation Injection** (`docs/prompts/CITATION_REQUIREMENTS_INJECT.md`)
   - Exact URL requirements
   - Accessed_date tracking
   - Source validation checklist

4. **Phase Template** (`docs/prompts/PHASE_INJECTION_TEMPLATE.md`)
   - Universal injection template
   - Phase-specific customizations
   - Quick reference cards

### Technical Implementation

1. **Temporal Validator** (`src/utils/temporal_validator.py`)
   ```python
   validator = TemporalValidator(date(2025, 9, 13))
   valid, errors = validator.validate_recommendation(rec)
   ```

2. **Citation Validator** (`src/utils/citation_validator.py`)
   ```python
   validator = CitationValidator()
   valid, errors = validator.validate(citation)
   ```

3. **Phase Output Validator** (`scripts/validate_phase_output.py`)
   ```bash
   python scripts/validate_phase_output.py output.json
   ```

### Configuration Files

1. **Temporal Requirements** (`config/temporal_awareness_requirements.yaml`)
   - Implementation delays by type
   - Budget cycle awareness
   - Realistic timeline templates

2. **Citation Standards** (`config/citation_standards.yaml`)
   - URL validation rules
   - Required metadata fields
   - Archive requirements

## Key Timeline Adjustments

### Current Context (September 13, 2025)
- **Quarter**: Q3 2025 (75% through year)
- **Days Remaining**: 109 in 2025
- **Fiscal Year**: FY2025/2026 (varies by country)
- **Next Budget**: FY2027 (first changeable)

### Realistic Timelines
| Action Type | Minimum Delay | Typical | Complex |
|------------|---------------|---------|---------|
| Policy Change | 3-6 months | 6-9 months | 12+ months |
| Legislation | 12-18 months | 18-24 months | 36+ months |
| Procurement | 9-15 months | 15-18 months | 24+ months |
| R&D Program | 12 months | 24 months | 36+ months |
| Major Capability | 18-24 months | 36 months | 60+ months |

### Adjusted Horizons
- **Immediate**: Q4 2025 start, Q2 2026 results
- **Short-term**: 2026-2027
- **Medium-term**: 2028-2029
- **Long-term**: 2030+

## Citation Requirements

### Mandatory Fields
```json
{
  "exact_url": "https://site.com/2025/09/document.pdf",
  "title": "Exact Document Title",
  "accessed_date": "2025-09-13",
  "author": "Author Name",
  "publication": "Publication Name",
  "publication_date": "2025-09-13"
}
```

### Examples

**CORRECT**:
```
NATO. (2025, September 10). Defense Planning Process 2025-2030.
Retrieved 2025-09-13, from
https://www.nato.int/docu/2025/defense-planning-process-2025-2030.pdf
```

**INCORRECT**:
```
See NATO website
Available at: www.nato.int
According to government sources
```

## Phase-Specific Implementation

### Phase 0-1: Setup & Indicators
- Data likely 3-6 months old
- Every indicator needs source URL
- Baseline: 2019-2024 complete, 2025 partial

### Phase 2-3: Landscape & Supply Chain
- Policies 2019-2024 are historical
- New policies need 12-18 month runway
- Procurement cycles 9-15 months minimum

### Phase 4-7: Institutions & Funding
- Current academic year 2025-2026
- Next funding cycle 2026-2027
- Budget planning for FY2027

### Phase 8-9: Risk & Posture
- Near-term = 2026-2027
- Medium-term = 2028-2030
- Past risks (2024) focus on mitigation

### Phase 10-11: Scenarios & Foresight
- 2-year = 2027
- 5-year = 2030
- 10-year = 2035

### Phase 12-13: Implementation
- Planning starts Q4 2025
- Execution begins 2026
- Measurable results 2027+

## Validation Process

### Pre-Submission Checklist
1. Run temporal validator on all recommendations
2. Verify all citations have exact URLs
3. Check all dates ≥ September 2025
4. Confirm implementation delays included
5. Validate budget cycles (FY2027+)

### Automated Validation
```bash
# Validate any phase output
python scripts/validate_phase_output.py reports/phase8_risk.json

# Check specific date
python scripts/validate_phase_output.py output.md --date 2025-09-13

# Save validation report
python scripts/validate_phase_output.py output.json --output validation.txt
```

## Common Errors to Avoid

### Temporal Errors
- ❌ "Achieve X by end of 2025" (only 3.5 months left!)
- ❌ "Increase FY2025 budget" (already set)
- ❌ "Deploy immediately" (nothing is immediate)
- ✅ "Begin Q4 2025, deploy Q3 2026"
- ✅ "Target FY2027 budget increase"

### Citation Errors
- ❌ "According to ministry website"
- ❌ "See government portal"
- ❌ "Available at www.example.com"
- ✅ "Ministry (2025). Title. Retrieved 2025-09-13, from [exact URL]"

## Standard Disclaimers

### For All Outputs
```
*Analysis date: September 13, 2025. All recommendations assume 8-12 month
minimum implementation delays. Budget impacts begin FY2027. Major capabilities
require 18-24 month development.*
```

### For Citations
```
*All sources accessed September 2025. URLs verified as of access date.
Archive copies available upon request.*
```

## Enforcement

1. **ChatGPT**: Include injection template in every prompt
2. **Claude Code**: Run validators before output
3. **Manual Review**: Use validation checklists
4. **APIs**: Programmatic validation of dates and URLs

## Quick Reference

| If You Want To Say... | You Should Say... | Because... |
|----------------------|-------------------|------------|
| "By 2025" | "By Q3 2026" | Only 3.5 months left in 2025 |
| "Immediately" | "Starting Q4 2025" | Nothing is immediate |
| "FY2025 budget" | "FY2027 budget" | FY2026 already locked |
| "Quick win" | "12-month initiative" | Quick still takes time |
| "This year" | "Within 12 months" | 2025 is almost over |

## Files Created

### Documentation
- `docs/prompts/MASTER_PROMPT_REQUIREMENTS.md`
- `docs/prompts/TEMPORAL_AWARENESS_INJECT.md`
- `docs/prompts/CITATION_REQUIREMENTS_INJECT.md`
- `docs/prompts/PHASE_INJECTION_TEMPLATE.md`
- `docs/prompts/phase_0_universal_with_checks.md`
- `docs/prompts/phase_8_risk_with_checks.md`

### Configuration
- `config/temporal_awareness_requirements.yaml`
- `config/citation_standards.yaml`

### Implementation
- `src/utils/temporal_validator.py`
- `src/utils/citation_validator.py`
- `scripts/validate_phase_output.py`

## Next Steps

1. **Immediate (Q4 2025)**
   - Apply injection templates to all phase prompts
   - Train team on validation requirements
   - Set up automated validation pipeline

2. **Short-term (Q1-Q2 2026)**
   - Monitor compliance rates
   - Refine validation rules based on usage
   - Integrate with CI/CD pipeline

3. **Medium-term (2026-2027)**
   - Extend validation to all outputs
   - Create validation dashboard
   - Automate correction suggestions

## Success Metrics

- 100% of outputs pass temporal validation
- 100% of citations include exact URLs
- 0 recommendations for past dates
- 100% accessed_date compliance
- All implementation timelines ≥ 8 months

---

*Implementation completed September 13, 2025. Version 1.0*

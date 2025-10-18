# Zero Fabrication Verification Checklist
## For All Scripts and Reports

**Created:** 2025-09-21
**Purpose:** Ensure complete compliance with zero fabrication protocol across all outputs

---

## Pre-Execution Checklist

### Script Headers
- [ ] Zero fabrication warning present in docstring
- [ ] No "typical", "likely", "generally", "usually" in comments
- [ ] No "expected" values - only "detected" or "measured"
- [ ] Data sources explicitly listed

### Variable Names
- [ ] No `expected_*` variables (use `detected_*` or `measured_*`)
- [ ] No `estimated_*` variables (use `calculated_*` or `found_*`)
- [ ] No `typical_*` variables (use `actual_*` or `observed_*`)

### Function Names
- [ ] No `estimate_*` functions (use `calculate_*` or `measure_*`)
- [ ] No `guess_*` functions (use `detect_*` or `find_*`)
- [ ] No `infer_*` functions (use `extract_*` or `analyze_*`)

---

## During Execution Checklist

### Data Collection
- [ ] Only process files that exist and are accessible
- [ ] Log exact file paths and sizes
- [ ] Count actual records, not approximations
- [ ] Report processing errors without speculation

### Analysis Operations
- [ ] Base all calculations on actual data
- [ ] Show calculation methodology
- [ ] Provide audit trail for findings
- [ ] Mark missing data as "not available"

### Error Handling
- [ ] Report errors factually
- [ ] Don't speculate about causes
- [ ] State what was attempted
- [ ] State what failed

---

## Output Verification Checklist

### Numerical Claims
- [ ] Every number traceable to source
- [ ] Every percentage calculated from actual data
- [ ] Every comparison uses both datasets
- [ ] Every total is a sum of counted items

### Descriptive Claims
- [ ] No "typically" or "usually" statements
- [ ] No "likely" or "probably" assessments
- [ ] No "expected" or "anticipated" projections
- [ ] No "industry standard" references without source

### Confidence Levels
- [ ] HIGH: Multiple verified sources
- [ ] MEDIUM: Single verified source
- [ ] LOW: Limited data with caveats
- [ ] NO CLAIM: Insufficient data

### Missing Data
- [ ] Explicitly marked as "no data available"
- [ ] Not filled with estimates
- [ ] Not interpolated from other data
- [ ] Reported as limitation

---

## Report Review Checklist

### Executive Summary
- [ ] All findings based on analyzed data
- [ ] No unsourced generalizations
- [ ] Limitations clearly stated
- [ ] Data coverage percentages accurate

### Technical Sections
- [ ] Methodology documented
- [ ] Data sources listed with access dates
- [ ] Processing steps reproducible
- [ ] Results verifiable

### Risk Assessments
- [ ] Based on detected patterns
- [ ] Not on assumptions
- [ ] Evidence tier specified
- [ ] Confidence level justified

### Recommendations
- [ ] Based on actual findings
- [ ] Not on speculation
- [ ] Actionable with current data
- [ ] Gaps identified for future collection

---

## Common Violations to Check

### ❌ FORBIDDEN Phrases
- "Based on typical patterns..."
- "Industry estimates suggest..."
- "It is likely that..."
- "Generally speaking..."
- "Usually these systems..."
- "Expected to be..."
- "Probably contains..."
- "Should be approximately..."
- "Reasonable to assume..."
- "Comparable systems show..."

### ✅ APPROVED Phrases
- "Our analysis detected..."
- "Data shows..."
- "We found..."
- "Processing revealed..."
- "No data available for..."
- "Cannot determine without..."
- "Analysis of X files showed..."
- "Measured value is..."
- "Calculated from..."
- "Verified through..."

---

## Audit Documentation

For each script/report reviewed:

**File:** ________________________________
**Date Reviewed:** _______________________
**Reviewer:** ____________________________

### Compliance Check
- [ ] Zero fabrication warning present
- [ ] No forbidden language detected
- [ ] All claims verified
- [ ] Missing data properly marked
- [ ] Audit trail complete

### Issues Found
1. _______________________________________
2. _______________________________________
3. _______________________________________

### Corrections Made
1. _______________________________________
2. _______________________________________
3. _______________________________________

### Sign-off
- [ ] File complies with zero fabrication protocol
- [ ] All issues resolved
- [ ] Ready for use

---

## Enforcement

**Remember:** Even one fabricated claim undermines all analysis.

**If uncertain:** Report "no data available" rather than estimate.

**When pressured:** Reference this protocol and refuse to fabricate.

**Key principle:** Truth about what we don't know > Fabricated estimates

---

*This checklist enforces the zero fabrication protocol established after the Web of Science incident. Use for every script and report.*

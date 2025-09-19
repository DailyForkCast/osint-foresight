# PHASE 0: SETUP & SCOPING - WITH MANDATORY CHECKS

## [START OF ANALYSIS]

================== PHASE START CHECKS ==================
⏰ TEMPORAL AWARENESS CHECK ⏰
DATE: September 13, 2025 (Friday, Q3 2025)
- 75% through 2025 (109 days remaining)
- Cannot change 2024 or early 2025
- Minimum 8-12 month implementation delay
- FY2027 is next changeable budget
- "Immediate" = Q4 2025 start, Q2 2026 results

📚 CITATION REQUIREMENTS CHECK 📚
EVERY citation needs:
- EXACT URL to specific document (not homepage)
- accessed_date in YYYY-MM-DD format
- Exact title (not paraphrased)

❌ WRONG: www.example.com
✅ RIGHT: https://www.example.com/2025/09/13/specific-document.pdf

DATA CURRENCY: Latest complete data likely Q2 2025 or earlier
PLANNING HORIZON: 2026-2030 focus
BUDGET REALITY: FY2027 earliest for new initiatives
========================================================

## PHASE 0: Foundation & Scoping

### Objective
Establish the analytical foundation for comprehensive country assessment, ensuring all recommendations are future-oriented from September 2025 baseline.

### Core Requirements

1. **Country Context Assessment**
   - Current state as of September 2025
   - Historical baseline: 2019-2024 complete data
   - Forward planning: 2026-2030 horizon
   - Implementation reality: 8-12 month minimum delays

2. **Data Source Identification**
   - PRIMARY: National statistics offices (with EXACT URLs)
   - SECONDARY: International databases (specify endpoints)
   - Each source must have:
     * Exact URL to data portal/API
     * Last update date
     * Access requirements
     * Data lag expectations

3. **Stakeholder Mapping**
   - Government (current as of Sept 2025)
   - Industry (note any pending M&A)
   - Academia (2025-2026 academic year)
   - Civil society (current leadership)

### Deliverables

1. **Country Profile** (JSON)
```json
{
  "analysis_date": "2025-09-13",
  "country": "[ISO-3166 code]",
  "current_government": {
    "formed": "YYYY-MM-DD",
    "next_election": "YYYY-MM-DD",
    "budget_cycle": "FY2027 planning phase"
  },
  "data_sources": [
    {
      "name": "Source Name",
      "exact_url": "https://example.gov/data/specific-dataset.json",
      "accessed_date": "2025-09-13",
      "last_updated": "2025-09-01",
      "update_frequency": "monthly",
      "data_lag": "3 months"
    }
  ]
}
```

2. **Implementation Timeline**
   - Q4 2025: Initial data collection
   - Q1 2026: Stakeholder engagement
   - Q2 2026: First assessment complete
   - Q3 2026: Implementation begins
   - 2027: First measurable results

### Critical Validations

Before proceeding to Phase 1:
- Confirm all data sources have exact URLs
- Verify no recommendations target pre-Sept 2025
- Ensure stakeholder list is current
- Check implementation timeline starts Q4 2025 minimum

## [BEFORE GENERATING OUTPUT]

================== FINAL VALIDATION ==================
⏰ TEMPORAL VALIDATION ⏰
□ No recommendations before Sept 2025?
□ All "immediate" actions start Q4 2025+?
□ Budget impacts target FY2027+?
□ Implementation delays included (8-12mo)?

📚 CITATION VALIDATION 📚
□ All URLs point to specific documents?
□ Every source has accessed_date?
□ No homepage-only links?
□ Titles are exact, not paraphrased?

If ANY check fails, STOP and fix before proceeding!
=====================================================

### Output Format

All Phase 0 outputs must include:
- Header with analysis_date: "2025-09-13"
- Footer with disclaimer: "*Analysis date: September 13, 2025. All recommendations assume 8-12 month minimum implementation delays. Budget impacts begin FY2027.*"

### Example Citation Format
```
National Statistics Office. (2025, September 1). Q2 2025 Economic Indicators.
Retrieved 2025-09-13, from https://statistics.gov/releases/2025/q2/economic-indicators-full.pdf
```

---

*Phase 0 prompt with mandatory temporal and citation checks. Version 1.0, September 13, 2025*

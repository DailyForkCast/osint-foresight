# PHASE INJECTION TEMPLATE - APPLY TO ALL PHASES

## How to Use This Template

**CRITICAL**: This template MUST be injected into EVERY phase prompt (0-13) for both ChatGPT and Claude Code.

Insert the START CHECK at the beginning of each phase prompt and the END CHECK before generating any output.

---

## START OF PHASE CHECK (Insert at beginning)

```markdown
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
========================================================
```

## END OF PHASE CHECK (Insert before output)

```markdown
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
```

## PHASE-SPECIFIC INJECTIONS

### Phase 0: Setup & Scoping
```markdown
[After START CHECK, add:]
DATA CURRENCY: Latest complete data likely Q2 2025 or earlier
PLANNING HORIZON: 2026-2030 focus
BUDGET REALITY: FY2027 earliest for new initiatives
```

### Phase 1: Ecosystem Mapping
```markdown
[After START CHECK, add:]
BASELINE DATE: September 2025 current state
PROJECTION YEARS: 2026, 2027, 2030, 2035
DATA LAG: Account for 3-6 month reporting delays
```

### Phase 2: Strategic Indicators
```markdown
[After START CHECK, add:]
INDICATOR TRACKING: 2019-2024 historical, 2025 partial
TARGETS: Set for 2026-2027 minimum
VERIFICATION: All indicators need source URLs with dates
```

### Phase 3: Technology Landscape
```markdown
[After START CHECK, add:]
POLICY TIMELINE: 2019-2024 enacted, 2025 implementing
NEW POLICIES: 12-18 month legislative cycle
TECHNOLOGY ADOPTION: 18-24 month deployment
```

### Phase 4: Supply Chain
```markdown
[After START CHECK, add:]
PROCUREMENT REALITY: 9-15 month cycles minimum
CONTRACT MODS: 3-6 months
SUPPLY CHAIN SHIFTS: 12-24 months to implement
```

### Phase 5: Institutions
```markdown
[After START CHECK, add:]
ACADEMIC YEAR: 2025-2026 current
NEXT FUNDING: 2026-2027 cycle
COLLABORATION TIME: 3-6 months to establish
```

### Phase 6: Funding & Investment
```markdown
[After START CHECK, add:]
BUDGET CYCLES: FY2026 locked, FY2027 planning now
GRANT CYCLES: 6-12 month lead times
ROI HORIZONS: 2028+ for major investments
```

### Phase 7: International Links
```markdown
[After START CHECK, add:]
PARTNERSHIP FORMATION: 6-12 months minimum
MOU NEGOTIATION: 3-6 months typical
JOINT PROGRAMS: 2-3 year development
```

### Phase 8: Risk Assessment
```markdown
[After START CHECK, add:]
RISK HORIZONS: Near=2026-27, Med=2028-30, Long=2031+
MITIGATION TIME: 8-12 months to implement
PAST RISKS (2024): Focus on mitigation, not prevention
```

### Phase 9: Strategic Posture
```markdown
[After START CHECK, add:]
POSTURE CHANGES: 12-18 months to implement
CAPABILITY GAPS: 24-36 months to close
STRATEGIC SHIFTS: 3-5 year horizons
```

### Phase 10: Red Team
```markdown
[After START CHECK, add:]
SCENARIO BASE: September 2025 starting point
ADVERSARY TIMELINE: Their planning also takes time
RESPONSE TIME: 6-12 months for countermeasures
```

### Phase 11: Foresight
```markdown
[After START CHECK, add:]
FORECAST PERIODS: 2yr=2027, 5yr=2030, 10yr=2035
TREND EMERGENCE: 12-24 months visibility
DISRUPTION LEAD: 18-36 months typical
```

### Phase 12: Extended Analysis
```markdown
[After START CHECK, add:]
DEEP DIVE TIMELINE: Current state September 2025
IMPLEMENTATION: Q4 2025 planning, 2026 execution
MEASUREMENT: 2027+ for impact assessment
```

### Phase 13: Closeout & Handoff
```markdown
[After START CHECK, add:]
HANDOFF DATE: Document September 2025 state
NEXT STEPS: Q4 2025 - Q1 2026 actions
REVIEW CYCLE: Q2 2026 first checkpoint
SUCCESS METRICS: Measurable by 2027
```

## STANDARD DISCLAIMERS TO ADD

### For Executive Summaries
```markdown
*Analysis date: September 13, 2025. All recommendations assume 8-12 month minimum implementation delays. Budget impacts begin FY2027. Major capabilities require 18-24 month development.*
```

### For Technical Reports
```markdown
*All sources accessed September 2025. URLs verified as of access date. Implementation timelines account for procurement, legislative, and organizational constraints.*
```

### For Policy Briefs
```markdown
*Current as of September 13, 2025. Policy changes require 12-18 month legislative cycles. Budget allocations target FY2027 and beyond.*
```

## AUTOMATIC REJECTION TRIGGERS

Your output will be REJECTED if it contains:
1. Actions for dates before September 2025
2. "End of 2025" targets (only 3.5 months left!)
3. FY2025/FY2026 budget changes
4. Homepage-only citations
5. Missing accessed_dates
6. "Immediate" results without 8-month delay

## QUICK REFERENCE CARD

| Wrong | Right | Why |
|-------|-------|-----|
| "By 2025" | "By Q3 2026" | Need 8-12 months |
| "www.site.com" | "https://site.com/doc.pdf" | Exact URL required |
| "According to NATO" | "NATO (2025). Title. Retrieved 2025-09-13, from [URL]" | Full citation |
| "FY2025 budget" | "FY2027 budget" | FY2026 locked |
| "Deploy now" | "Deploy Q3 2026" | Implementation time |

## ENFORCEMENT

- ChatGPT: Auto-inject checks via system prompt
- Claude Code: Run validators before output
- Manual Review: Use checklists for verification
- APIs: Validate all dates and URLs programmatically

---

**Remember: Professional analysis requires both temporal realism and citation precision!**

# Lithuania OpenAlex Data Gap
## Cross-Reference Limitation - Insufficient Data for Validation

---
**Date:** 2025-11-02
**Status:** ⚠️ DATA GAP IDENTIFIED
**Impact:** Cannot validate academic collaboration claims without additional data collection
---

## Summary

Attempted to cross-reference GDELT media events with Lithuania-China academic collaboration data from OpenAlex. **Current database has insufficient Lithuania coverage for validation.**

---

## Data Availability Check

**OpenAlex Tables in osint_master.db:**
- `openalex_works`: 496,392 works total
- `openalex_institutions`: 0 records (empty table)
- `openalex_work_authors`: 7,936,171 author-institution-work links

**Lithuania-Specific Data:**
- Works with Lithuanian authors (country_code='LT'): **1,334**
- Works with Chinese authors (country_code='CN'): 230,361
- **Lithuania-China co-authored works: 38**

**Temporal Coverage:**
- Query returned only 1997: 1 work
- No data for 2019-2023 period needed for validation

---

## Comparison to Conversation Summary Claim

**Claim to Validate (from conversation summary):**
> Lithuania-China research collaboration: 1,209 works (2020) → 129 works (2021)
> Change: -1,080 works (-89.3%)

**Current Database:**
- Total Lithuania-China collaborations: 38 (across all years)
- 2020 data: Not available in current dataset
- 2021 data: Not available in current dataset

**Gap Analysis:**
- Need: ~1,300-1,400 Lithuania-China works for 2020-2021 validation
- Have: 38 Lithuania-China works (all years combined)
- **Data gap: ~97% of required works missing**

---

## Root Cause Analysis

### Why is Lithuania Data Missing?

**OpenAlex Collection Strategy:**
Our OpenAlex data collection focused on:
1. **Strategic technologies** (AI, quantum, semiconductors, etc.)
2. **High-risk Chinese entities** (PLA-affiliated institutions, SOEs)
3. **Specific countries** (primarily US, Germany, other major research nations)

**Lithuania was not prioritized** in initial collection because:
- Small research output relative to US, Germany, UK, France
- Not a major technology leader in strategic domains
- Collection optimized for high-volume China collaboration patterns

**Result:** Lithuania works only appear when they:
- Include strategic technology keywords
- Involve high-risk Chinese institutions
- Happen to be in collected time periods

This explains 1,334 Lithuanian works vs. likely 50,000+ total Lithuanian research output.

---

## Data Collection Options

### Option A: OpenAlex API Collection (Recommended)
**Pros:**
- Free API access
- Can target Lithuania specifically (country_code filter)
- Comprehensive coverage

**Cons:**
- Requires API requests (rate limits apply)
- Time to collect: ~2-4 hours for full Lithuania dataset

**Estimated Coverage:**
- Lithuanian institutions: ~50-100 active research institutions
- Lithuanian works (2019-2023): ~50,000-100,000 publications
- Lithuania-China collaborations (2019-2023): ~500-2,000 works

**API Query:**
```
https://api.openalex.org/works?filter=institutions.country_code:LT,authorships.institutions.country_code:CN,publication_year:2019-2023
```

###Option B: OpenAlex Kaggle Snapshot
**Pros:**
- Bulk download (faster)
- Complete dataset

**Cons:**
- 295 GB compressed (requires significant storage/processing)
- Need to filter for Lithuania
- Snapshot may be outdated

**Not recommended** for single-country validation (too resource-intensive).

### Option C: Alternative Data Sources
**1. OpenAire (European research)**
- May have better Lithuania coverage (EU-focused)
- Check: F:/OSINT_DATA/OPENAIRE/ or F:/OSINT_WAREHOUSE tables

**2. CORDIS (EU grants)**
- Lithuania participates in EU Framework Programmes
- Can show Lithuania-China project collaborations

**3. Direct Institution Contact**
- Lithuanian Research Council
- Major Lithuanian universities (Vilnius University, Kaunas University of Technology)

---

## Impact on GDELT Validation

### Cross-Reference Status

| Data Source | Status | Finding |
|------------|--------|---------|
| Trade Data (Eurostat) | ✅ VALIDATED | Lithuanian exports to China decreased 90% (2020-2023) |
| Academic Collaboration (OpenAlex) | ⚠️ DATA GAP | Insufficient data for validation |
| Procurement (TED) | 🔄 NEXT | Move to this cross-reference |

**Implication:**
- GDELT events validated by trade data (strong evidence)
- Cannot yet validate academic collaboration claim (data limitation, not disproof)
- Need additional data sources for comprehensive validation

---

## Recommendation

**Immediate Action:**
1. **SKIP OpenAlex validation** for now (data collection required)
2. **PROCEED with TED procurement cross-reference** (data available)
3. **DOCUMENT limitation** in final validation report

**Short-term (1-2 days):**
1. Collect full Lithuania OpenAlex data via API
2. Re-run collaboration analysis
3. Validate temporal patterns vs. GDELT timeline

**Alternative Validation (if OpenAlex collection delayed):**
1. Check OpenAire database for Lithuania-China EU grants
2. Query CORDIS for Lithuania-China collaborative projects
3. Contact Lithuanian institutions directly for collaboration statistics

---

## Data Quality Note

**Zero Fabrication Protocol:**

**What We Can State:**
- ✅ Our current OpenAlex database has 38 Lithuania-China collaborations
- ✅ This is insufficient for validating the -89.3% drop claim
- ✅ Our collection strategy focused on strategic technologies, not comprehensive country coverage

**What We Cannot State:**
- ❌ Cannot say "the -89.3% drop did not occur" (absence of evidence ≠ evidence of absence)
- ❌ Cannot infer Lithuania collaboration trends from 38 works
- ❌ Cannot validate or invalidate the conversation summary claim without additional data

**Conclusion:**
- Data gap identified, not a validation failure
- Need targeted data collection to proceed
- Alternative cross-references (TED, OpenAire, CORDIS) may provide validation

---

## Files Related to This Analysis

**Scripts Created:**
- `check_lithuania_openalex.py` - Initial availability check (hit schema error)
- Database queries (inline Python) - Confirmed 38 Lithuania-China works

**Database Tables Queried:**
- `openalex_works` (496,392 records)
- `openalex_work_authors` (7,936,171 records)
- `openalex_institutions` (0 records - empty)

**Related Documentation:**
- LITHUANIA_TRADE_VALIDATION_20251102.md (trade cross-reference ✅ validated)
- LITHUANIA_TAIWAN_CRISIS_GDELT_VALIDATION_20251102.md (GDELT event timeline)

---

## Next Steps

### Immediate (Ready to Execute)

**1. TED Procurement Cross-Reference (Step 1C)**
- Check Lithuanian government contracts with Chinese companies
- Timeline: 2020-2023
- Compare to GDELT economic measures events
- Expected effort: 30 minutes (data available in database)

**2. Document Cross-Reference Summary**
- Create comprehensive validation report
- Note data gaps alongside validated findings
- Provide recommendations for future work

**Status:** Marking OpenAlex validation as "Data Gap - Collection Required"

---

**Analysis Complete: 2025-11-02**
**Analyst: Claude Code**
**Next: Proceed with TED procurement cross-reference (data available)**
**OpenAlex Status: ⚠️ DATA GAP - Requires targeted collection**


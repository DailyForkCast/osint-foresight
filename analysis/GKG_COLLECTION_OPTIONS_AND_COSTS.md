# GDELT GKG Collection - Options and Costs

**Status**: Ready to execute, awaiting approval

**Date**: November 5, 2025

---

## Executive Summary

The GDELT Global Knowledge Graph (GKG) contains thematic, organizational, and sentiment data that would enable keyword searches like "quantum research" or "university partnership" across our existing 8.4M GDELT events.

**Current Capability**: Can search by actors (e.g., China, specific countries)
**Missing Capability**: Cannot search by themes/keywords
**Solution**: Collect GKG data to add this search capability

---

## Validated Cost Estimates

Tests completed Nov 5, 2025 confirm:
- **1.77 TB scanned per day** with China filter
- **28,640 China-related records per day** (7.43% of all GKG records)
- **Cost: $8.86 per day** ($5/TB after 1TB free tier)

### Collection Options

| Option | Days | Records | Cost | Time | Recommendation |
|--------|------|---------|------|------|----------------|
| **Option 1: Test (30 days)** | 30 | ~860K | **$260.77** | 3 min | **START HERE** |
| **Option 2: Recent year (365 days)** | 365 | ~10.5M | $3,228.48 | 37 min | If test successful |
| **Option 3: Full backfill (2,115 days)** | 2,115 | ~60.6M | $18,731.48 | 212 min | Only if critical |

---

## What GKG Data Provides

Sample records from Nov 4, 2024 show:

### Themes
- `ARMEDCONFLICT` - Military conflicts
- `WB_332_CAPITAL_MARKETS` - Financial sector activity
- `TAX_FNCACT_CHAIRMAN` - Corporate governance
- `SCIENCE`, `TECH`, `QUANTUM`, `SEMICONDUCTOR` - Technology domains

### Organizations
- `Peoples Liberation Army`
- `China Army`
- `National Republic China`
- `United States Bloomberg Agency`
- `Siemens`, `Panasonic` (companies)
- Universities (by name)

### Enables Searches Like:
- "Show me quantum research partnerships between European universities and China"
- "Find semiconductor supply chain discussions"
- "Track university collaboration announcements"
- "Identify military technology themes"

---

## Technical Details

**Billing**: Confirmed ACTIVE (Nov 5, 2025)
- Project: osint-foresight-2025
- Account: 0185E1-13AF92-839C8E (OPEN)

**Date Coverage**: Jan 5, 2020 to Nov 5, 2025 (2,115 days)
- 99.2% coverage (2,115 of 2,132 calendar days have data)
- Aligns with existing 8.4M GDELT events

**Script**: `scripts/collectors/gdelt_gkg_collector.py`
- Checkpoint/resume support (can stop and restart anytime)
- Filters for China-related themes and organizations
- Uses correct timestamp format (YYYYMMDDHHMMSS)
- Cost tracking and reporting built-in

---

## Recommendations

### Recommended Approach
1. **Start with Option 1 (30 days, $260.77)**
   - Test data quality and usefulness
   - Validate search capabilities meet requirements
   - Assess value before larger investment

2. **If test successful, expand to Option 2 (365 days, $3,228)**
   - Provides full year of recent intelligence
   - Covers current geopolitical landscape
   - Sufficient for most analysis needs

3. **Avoid Option 3 unless justified**
   - $18,731 is significant cost
   - Historical data (2020-2024) may have limited value
   - Only proceed if historical trend analysis required

### Alternative: Free Approach (No Cost)
If budget constraints exist, we can:
- Continue using existing events-only search (by actors)
- Target specific high-value dates for GKG collection (e.g., key policy events)
- Collect GKG incrementally as budget allows
- Use direct GDELT downloads instead of BigQuery (more labor-intensive)

---

## Next Steps

**AWAITING USER APPROVAL** before executing collection.

To proceed with Option 1 (30-day test):
```bash
python scripts/collectors/gdelt_gkg_collector.py --limit-days 30
```

To proceed with Option 2 (365 days):
```bash
python scripts/collectors/gdelt_gkg_collector.py --limit-days 365
```

To proceed with custom date range:
```bash
python scripts/collectors/gdelt_gkg_collector.py \
  --start-date 20240101 \
  --end-date 20241231
```

---

## Risk Assessment

**Financial Risk**: Low to Medium
- Costs are predictable (validated)
- Can stop collection at any time (checkpoint system)
- 1 TB free tier reduces initial costs

**Technical Risk**: Low
- BigQuery billing confirmed working
- Test queries successful
- Script includes error handling and resumption

**Value Risk**: Medium
- GKG data may or may not meet analysis needs
- Recommend starting with small test (Option 1)
- Can always expand if valuable

---

## Files Created

**Analysis**:
- `analysis/gkg_test_results.json` - Initial test results
- `analysis/gkg_strategy_analysis.json` - Coverage analysis
- `analysis/gkg_collection_strategy.json` - Collection options
- `analysis/gkg_cost_estimate_corrected.json` - Date range analysis
- `analysis/gkg_cost_validation.json` - Cost validation results
- `analysis/gkg_structure_investigation.json` - Table structure findings
- `analysis/gkg_corrected_cost_estimates.json` - Validated estimates

**Scripts**:
- `scripts/collectors/gdelt_gkg_collector.py` - Production-ready collector (NOT EXECUTED)

**Test Scripts** (safe to delete):
- `test_gkg_query.py`
- `analyze_gkg_strategy.py`
- `fix_gkg_cost_estimate.py`
- `validate_gkg_cost.py`
- `test_gkg_2024_dates.py`
- `investigate_gkg_structure.py`
- `test_gkg_correct_format.py`

---

## Decision Required

**Question**: Which collection option do you want to proceed with?

- [ ] **Option 1**: 30-day test ($260.77) - RECOMMENDED
- [ ] **Option 2**: 365 days ($3,228.48)
- [ ] **Option 3**: Full backfill 2,115 days ($18,731.48)
- [ ] **Option 4**: Custom date range (specify dates)
- [ ] **Option 5**: Do not collect (continue with events-only search)

**Additional Options**:
- [ ] Collect incrementally (e.g., 10 days per month as budget allows)
- [ ] Target specific high-value dates only (e.g., major policy announcements)
- [ ] Explore alternative data sources for keyword search

---

**NOTE**: No collection will proceed without explicit approval. The GKG collector script is ready but will only run when you execute it with the command line arguments shown above.

# Fabrication Analysis Results
**Date:** 2025-09-21
**Status:** Analysis Complete

## Executive Summary

Our fabrication checker identified 318 "high-severity" issues, but investigation revealed most were **FALSE POSITIVES**. The numbers 168 and 222 that were flagged as "known fabrications" are actually **VERIFIED DATA** from real CORDIS analysis.

## Key Findings

### ✅ VERIFIED Numbers (Wrongly Flagged)

| Number | What It Is | Source | Verification |
|--------|------------|--------|--------------|
| **168** | H2020 Italy-China projects | `analysis/italy_china_project_ids.json` | 168 actual project IDs listed |
| **54** | Horizon Europe Italy-China projects | `analysis/italy_china_project_ids.json` | 54 actual project IDs listed |
| **222** | Total Italy-China projects | `analysis/italy_china_project_ids.json` | 168 + 54 = 222 |
| **68** | Germany-China OpenAlex papers | OpenAlex sample processing | Verified in processing logs |

These numbers should be marked as `[VERIFIED DATA]` not removed.

### ❌ TRUE Fabrications (Need Removal)

| Number | Why It's Fabricated | Action Needed |
|--------|-------------------|---------------|
| **€12B** | Made-up EU-China trade figure | Remove all instances |
| **4,500** | Hypothetical TED contract count | Mark as [HYPOTHETICAL EXAMPLE] |
| **100,000-500,000** | Invented collaboration range | Remove or mark as example |

## Issue Breakdown

### High Severity (318 issues)
- **~256 false positives**: Numbers 168/222 appearing without markers (but they're real!)
- **~62 true issues**: Other fabrications that need fixing

### Medium Severity (1,704 issues)
Most are formatting issues:
- Year ranges in commands (2010-2025) flagged as "unverified ranges"
- File sizes (420.7GB) flagged as needing verification markers
- Implementation lag (3-5 years) flagged as range without source

## Actions Taken

1. **Updated fabrication_checker.py**
   - Removed 168 and 222 from "known_fabrications" list
   - Added comment that these are verified numbers

2. **Identified data source**
   - Located `analysis/italy_china_project_ids.json`
   - Confirmed it contains exactly 168 H2020 and 54 Horizon Europe project IDs
   - Total of 222 matches all documentation

## Recommendations

### Immediate Actions
1. Add `[VERIFIED DATA]` markers to all instances of 168/222/68
2. Update documentation to reference source: `analysis/italy_china_project_ids.json`
3. Remove or mark actual fabrications (€12B, 4,500, 100,000-500,000)

### Process Improvements
1. Before marking a number as "fabrication", check if data file exists
2. Distinguish between:
   - Missing markers (formatting issue)
   - Actual fabrications (false data)
3. Create allowlist for verified numbers with sources

## Verification Commands

To verify the numbers yourself:
```python
import json
data = json.load(open('analysis/italy_china_project_ids.json'))
print(f"H2020: {len(data['h2020_italy_china_ids'])}")  # Output: 168
print(f"Horizon: {len(data['horizon_italy_china_ids'])}")  # Output: 54
print(f"Total: {data['total_count']}")  # Output: 222
```

## Summary

**The numbers 168 and 222 are REAL, not fabricated.** They represent actual CORDIS projects with verifiable IDs. The fabrication checker was overly aggressive in flagging them because they appeared without `[VERIFIED DATA]` markers, but the data itself is legitimate.

The real fabrications (€12B, 4,500 contracts, 100,000-500,000 collaborations) remain in the known_fabrications list and should be removed from documentation.

---

*Next step: Add proper [VERIFIED DATA] markers throughout documentation*

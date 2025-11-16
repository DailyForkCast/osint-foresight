# OpenAlex V2 Production Diagnostic Report

**Date**: 2025-10-12
**Issue**: Very low acceptance rate in production run (~5 works from 174 files)

---

## Problem Summary

Production run was stopped at 18% completion (174/971 files) due to extremely low results:
- **Expected at 18%**: ~360 works (based on 2,000 total target)
- **Actual**: ~5-6 works
- **Variance**: 98% below expected

---

## Root Cause Analysis

### 1. Sequential vs Diverse Sampling Bias

**Test Results** (27 files, diverse sampling):
- Files sampled from 20 different date directories (2023-2025)
- 32,096 works scanned → 56 accepted (0.17% rate)
- All 9 technologies represented
- 100% precision

**Production** (174 files, sequential):
- Processing files 1-174 sequentially from early date directories
- Likely all from 2023 or early date ranges
- Same validation algorithm, but different content distribution
- Much lower match rate suggests early data has different characteristics

### 2. Topic Distribution Hypothesis

Early OpenAlex data (2023) may have:
- Different topic taxonomy (OpenAlex topics evolved over time)
- Less complete topic metadata
- Different field distributions
- Lower quality topic assignments

### 3. Validation Strictness

**Moderate strictness requirements**:
```python
# For topic validation to pass:
if pattern_lower in topic_name:
    # Require high score for broad matches
    if len(pattern_lower) > 5 or topic_score > 0.5:
        return True, topic_name
```

This may be too restrictive for:
- Early data with lower topic scores
- Works with less developed topic assignments
- Edge cases where topics are relevant but scored lower

---

## Proposed Solutions

### Solution 1: Switch to Lenient Strictness (RECOMMENDED FIRST)

**What it does**:
```python
if strictness == 'lenient':
    # Any substring match
    if pattern_lower in topic_name or topic_name in pattern_lower:
        return True, topic_name
```

**Why**:
- Removes score requirements
- More permissive topic matching
- Still has keyword + topic validation (2-stage)
- Should significantly increase acceptance rate

**Risk**: May introduce some false positives, but still better than V1's 80-90% FP rate

### Solution 2: Expand RELEVANT_TOPICS Lists

**Current gaps identified**:
- AI: Only 9 patterns, could add 'computation', 'learning', 'automation'
- Quantum: Very restrictive (all contain 'quantum'), could add 'physics', 'computing'
- Semiconductors: Could add 'electronics', 'circuits', 'materials'
- Smart_City: Could add 'urban', 'infrastructure', 'transportation'

**Recommendation**: Try Solution 1 first, expand topics if needed

### Solution 3: Continue Production with Patience

**Rationale**:
- Sequential processing means early files may not be representative
- After 300-500 files, should hit more diverse date ranges
- Acceptance rate may naturally improve as newer data is processed

**Why NOT recommended**: Would waste 6-12 hours on likely-too-strict run

---

## Recommended Action Plan

### Phase 1: Quick Lenient Test (10 minutes)
```bash
# Clear test data
DELETE FROM openalex_works WHERE validation_keyword IS NOT NULL;

# Run lenient sample test
python scripts/integrate_openalex_full_v2.py --sample --max-per-tech 1000 --strictness lenient
```

**Success criteria**:
- 100-300 works accepted from ~100 files
- Precision still >80% on manual review
- Better technology distribution

### Phase 2: Production Decision
If lenient test successful:
```bash
# Run production with lenient
python scripts/integrate_openalex_full_v2.py --max-per-tech 10000 --strictness lenient
```

If lenient has too many false positives:
- Expand RELEVANT_TOPICS lists
- Create "balanced" strictness level between lenient and moderate
- Retest

---

## Validation Quality Expectations

### Moderate vs Lenient Comparison

| Metric | Moderate (Current) | Lenient (Proposed) |
|--------|-------------------|-------------------|
| Topic validation | Pattern + score > 0.5 | Pattern only |
| Expected FP rate | 0-10% | 10-20% |
| Expected acceptance | 0.17% (too low) | 0.5-1.0% (target) |
| Production yield | ~2,000 works | ~5,000-10,000 works |

Both still have:
- ✅ Word boundary keyword matching
- ✅ Source exclusion (biology/medicine)
- ✅ Quality checks (abstract, not retracted)

---

## Test Results Archive

### Final Test (Moderate, Diverse Sampling)
- **Files**: 27 from 20 date directories
- **Scanned**: 32,096 works
- **Accepted**: 56 works (0.17%)
- **Precision**: 100%
- **FP reduction**: 78.5%

### Production Attempt 1 (Moderate, Sequential)
- **Files**: 174 (18% of 971)
- **Accepted**: ~5 works
- **Rate**: ~0.003% (60x lower than test)
- **Status**: Stopped for review

---

## Next Steps

1. **Immediate**: Run lenient sample test to assess viability
2. **Review**: Manual quality check of lenient results
3. **Decision**: Proceed with lenient production or adjust further
4. **Monitor**: Track false positive rate during production

---

**Status**: ⏳ AWAITING LENIENT TEST RESULTS
**Updated**: 2025-10-12 11:00

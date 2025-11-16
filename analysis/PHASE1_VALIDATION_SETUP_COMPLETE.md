# Phase 1: Detection Accuracy Validation - SETUP COMPLETE

**Date:** 2025-10-14
**Status:** Ready for Manual Review

---

## What Was Created

### 1. Manual Review Samples ✓

**File:** `analysis/manual_review/manual_review_samples_20251014_172628.csv`

**Sample Distribution:**
- **101-column format:** 75 samples (from 5,109 detections)
- **305-column format:** 100 samples (from 159,513 detections)
- **206-column format:** 75 samples (from 1,936 detections)
- **TOTAL:** 250 samples

**Sampling Method:**
- Random sampling from each format
- Proportional to population size
- All confidence levels represented

### 2. Review Instructions ✓

**File:** `analysis/manual_review/REVIEW_INSTRUCTIONS.txt`

**Contents:**
- Classification guidelines (YES/NO/UNCERTAIN)
- Confidence scoring system (1-5)
- Taiwan policy explanation
- Example cases
- Reference information

### 3. Precision Calculator ✓

**File:** `calculate_precision_from_review.py`

**Features:**
- Calculates overall precision
- Breaks down by format, confidence, detection type
- Identifies false positive patterns
- Generates JSON results

---

## How to Use

### Step 1: Open the CSV File

```
Location: C:/Projects/OSINT - Foresight/analysis/manual_review/
File: manual_review_samples_20251014_172628.csv
```

**Open in:** Excel, Google Sheets, or any CSV editor

### Step 2: Review Each Row

For each transaction, fill in:

1. **TRUE_POSITIVE column:**
   - `YES` = Correctly detected as China-related
   - `NO` = Incorrectly detected (false positive)
   - `UNCERTAIN` = Cannot determine

2. **CONFIDENCE_SCORE column:**
   - `5` = Absolutely China-related
   - `4` = Very likely
   - `3` = Probably
   - `2` = Probably not
   - `1` = Definitely not

3. **NOTES column:**
   - Explain your reasoning, especially for NO and UNCERTAIN

### Step 3: Key Classification Rules

**TRUE POSITIVE (YES):**
- Recipient is Chinese company/entity
- Work performed in China/Hong Kong
- Taiwan company with work in mainland China (per policy)
- Chinese sub-awardee

**FALSE POSITIVE (NO):**
- "China" in name but not related to PRC (e.g., porcelain company)
- Taiwan only (no mainland China connection)
- Name confusion (e.g., "FACCHINA" Italian surname)

**UNCERTAIN:**
- Insufficient information in data
- Ambiguous case
- Need external verification

### Step 4: Save When Complete

Save as: `manual_review_samples_20251014_172628_COMPLETED.csv`

### Step 5: Calculate Precision

Run the calculator:

```bash
python calculate_precision_from_review.py
```

This will:
- Calculate precision (true positives / total classified)
- Break down by format and confidence level
- Identify false positive patterns
- Save results to JSON

---

## Expected Outcomes

### Success Criteria

**Target:** ≥95% precision

**Calculation:**
```
Precision = TRUE POSITIVES / (TRUE POSITIVES + FALSE POSITIVES)
```

**What This Validates:**
- Detection methodology is accurate
- Taiwan policy working correctly
- False positive rate is acceptable
- Confidence scoring is meaningful

### Possible Results

**Scenario 1: Precision ≥95%**
- ✓ Detection methodology validated
- ✓ Proceed to Phase 2 analyses with confidence
- ✓ Document findings

**Scenario 2: Precision 90-95%**
- Review false positive patterns
- Consider refining detection rules
- Still acceptable for most use cases
- Document limitations

**Scenario 3: Precision <90%**
- Investigate systematic issues
- Refine detection methodology
- May need to reprocess data
- Document and fix before proceeding

---

## Time Estimate

**Per Transaction:** ~2 minutes

**Total Time:**
- 250 transactions × 2 min = ~8 hours
- Can be done in multiple sessions
- Recommend 50-100 transactions per session

**Sessions:**
- Session 1: 50 transactions (~2 hours)
- Session 2: 50 transactions (~2 hours)
- Session 3: 50 transactions (~2 hours)
- Session 4: 50 transactions (~2 hours)
- Session 5: 50 transactions (~2 hours)

---

## Reference Fields in CSV

| Field | Description | Use for Review |
|-------|-------------|----------------|
| review_id | Unique review identifier | Track progress |
| format | Which format (101/305/206) | Context |
| transaction_id | USAspending transaction ID | Lookup if needed |
| recipient_name | Who receives money | Primary classification |
| recipient_country | Recipient location | Key detection field |
| pop_country | Place of performance | Key detection field |
| sub_awardee_country | Subcontractor location | Secondary detection |
| award_amount | Dollar value | Context |
| award_description | What is this for | Additional context |
| action_date | When | Context |
| highest_confidence | AUTO: Detection confidence | Compare to your score |
| detection_types | AUTO: How detected | Validate method |
| awarding_agency | Which US agency | Context |

---

## Important Policy Notes

### Taiwan Detection Policy (Option A)

**Taiwan recipient + China POP = TRUE POSITIVE**

This is INTENTIONAL, not an error.

**Rationale:**
- Tracks work performed IN China regardless of recipient nationality
- Captures cross-strait economic activity
- Same logic as US company working in China

**Examples:**
```
✓ National Taiwan University → Research in Beijing = YES
✓ Taiwan tech company → Office in Shanghai = YES
✗ Taiwan Semiconductor → Work in Taiwan only = NO
```

### Hong Kong Policy

Hong Kong = TRUE POSITIVE

Hong Kong is considered part of PRC sphere for detection purposes.

---

## Quality Assurance Tips

### Consistency Checks

As you review, verify:

1. **Similar transactions classified similarly**
   - Same recipient → same classification
   - Same country pattern → same classification

2. **Detection type correlation**
   - "country" detections = should be accurate
   - "name" detections = may have more false positives

3. **Confidence score matches detection**
   - HIGH confidence → should be YES
   - LOW confidence → may be NO

### Common Pitfalls to Avoid

1. **Don't assume "China" in name = China entity**
   - "China porcelain" ≠ PRC
   - "Beijing Street" ≠ PRC city

2. **Don't confuse Taiwan with PRC**
   - Taiwan alone ≠ China
   - Taiwan + China POP = China (per policy)

3. **Don't mark as UNCERTAIN unnecessarily**
   - Use available fields to decide
   - UNCERTAIN should be <10% of reviews

---

## After Validation Complete

### Next Steps (Phase 2)

Once precision is validated (≥95%), proceed to:

1. **Value Distribution Analysis**
   - Top 10 transactions verification
   - Statistical analysis
   - Outlier detection

2. **Agency Analysis**
   - Which agencies most involved
   - Volume rankings
   - Temporal trends

3. **Temporal Analysis**
   - Trends over time
   - Event correlation
   - Seasonality

4. **Entity Profiling**
   - Top recipients
   - Entity deduplication
   - Classification

5. **Topic Modeling**
   - What are transactions for
   - Technology focus areas
   - Dual-use identification

### Documentation Updates

After validation:

1. Update analysis framework with precision results
2. Document any detection improvements needed
3. Create comprehensive data quality report
4. Prepare findings summary

---

## Files Created Summary

| File | Purpose | Location |
|------|---------|----------|
| manual_review_samples_*.csv | Review data | analysis/manual_review/ |
| REVIEW_INSTRUCTIONS.txt | How to review | analysis/manual_review/ |
| sample_generation_summary.json | Sample metadata | analysis/manual_review/ |
| calculate_precision_from_review.py | Precision calculator | Project root |
| PHASE1_VALIDATION_SETUP_COMPLETE.md | This document | analysis/ |

---

## Contact & Support

**Questions about:**
- Taiwan policy → See `analysis/TAIWAN_POLICY_FINAL_DECISION.md`
- Detection methodology → See processor scripts in `scripts/`
- Data quality → See `analysis/USASPENDING_COMPREHENSIVE_ANALYSIS_FRAMEWORK.md`

---

## Status

- ✓ Samples generated (250 total)
- ✓ Instructions created
- ✓ Calculator ready
- ⏳ **NEXT: Manual review** (user action required)
- ⏳ Precision calculation (after review)
- ⏳ Phase 2 analyses (after validation)

**Ready to begin manual review!**

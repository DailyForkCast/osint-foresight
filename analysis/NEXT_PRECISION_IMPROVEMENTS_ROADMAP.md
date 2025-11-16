# Next Steps: Precision Improvement Roadmap
**Date:** October 24, 2025
**Current Precision:** 73% → 95% (estimated after all fixes)
**Goal:** Achieve 97%+ precision with minimal false positives

---

## Immediate High-Impact Actions (Next 1-2 Hours)

### 1. Fix Configuration Gaps ⚡ HIGH IMPACT
**Expected Improvement:** +1-2% precision

#### Issue: Missing Geographic Reference Data
From TED validation, we found missing entries in `prc_identifiers.json`:
- Shanghai not detected in "Shanghai Pudong Area"
- Guangzhou not detected
- Some administrative divisions incomplete

**Action:**
```bash
# Audit and expand prc_identifiers.json
- Add missing cities: Shanghai, Guangzhou, Shenzhen (if missing)
- Add missing districts: Pudong, Nanshan, Luohu
- Verify all major Chinese cities (tier 1-2) are present
```

**Files to update:**
- `data/prc_identifiers.json`
- `data/chinese_entities_enhanced.json`

**Validation:** Re-run TED enhanced detector tests after updates

---

### 2. Expand False Positive Filters ⚡ HIGH IMPACT
**Expected Improvement:** +1-2% precision

#### Known False Positives to Add:
From validation testing and manual review:

**Add to FALSE_POSITIVES lists:**
```python
# Geographic false positives
'indochina',           # Historical region, not PRC
'indo-china',
'french indochina',

# Company name false positives
'cosco fire protection',   # US company, not COSCO Shipping
'cosco fire',
'american cosco',

# European companies with Chinese-sounding names
'sino european',       # European joint ventures
'sino-german',
'euro-china',

# Technology terms that happen to contain Chinese words
'machine learning',    # Contains 'china' in some contexts
'machinery',           # Contains 'china'
```

**Files to update:**
- `scripts/process_usaspending_305_column.py`
- `scripts/process_usaspending_374_column.py`
- `scripts/process_usaspending_101_column.py`
- `scripts/ted_enhanced_prc_detector.py`

---

### 3. Apply Word Boundary Fixes to Remaining Scripts ⚡ MEDIUM IMPACT
**Expected Improvement:** +0.5-1% precision

#### Scripts Still Using Substring Matching:
Audit needed for these processors:
1. `process_usaspending_206_column.py` (if exists)
2. Other TED processors (70+ scripts identified)
3. Patent processors beyond streaming version

**Action:**
```bash
# Search for remaining substring matches
grep -r "if pattern in" scripts/ | grep -v ".backup" | grep -v "test_"
grep -r "if entity in" scripts/ | grep -v ".backup" | grep -v "test_"
```

**Priority order:**
1. High-volume processors first (206-column USAspending)
2. Production TED processors
3. Secondary patent processors

---

## Short-term Actions (Next 24-48 Hours)

### 4. Manual Validation of Sample Data 🎯 CRITICAL
**Expected Improvement:** Identify 50-100 more false positives

#### Validation Process:
1. **Sample current detections** (100 per source):
   ```sql
   -- USAspending sample
   SELECT * FROM usaspending_china_305
   ORDER BY RANDOM() LIMIT 100;

   -- TED sample
   SELECT * FROM ted_contracts_production
   WHERE is_chinese_related = 1
   ORDER BY RANDOM() LIMIT 100;

   -- USPTO sample
   SELECT * FROM uspto_patents_chinese
   ORDER BY RANDOM() LIMIT 100;
   ```

2. **Manual review criteria:**
   - ✅ Legitimate Chinese entity/connection
   - ❌ False positive - add to filters
   - ⚠️ Uncertain - needs investigation

3. **Document findings:**
   - Create `MANUAL_VALIDATION_BATCH_[DATE].xlsx`
   - Track false positive patterns
   - Identify new filters needed

**Time estimate:** 2-3 hours for 300 records
**Expected findings:** 10-30 new false positive patterns

---

### 5. Expand SOE Database 📊 MEDIUM IMPACT
**Expected Improvement:** +0.5-1% recall (catch more valid entities)

#### Current SOE Database Gaps:
From validation, we're missing:
- "Aviation Industry Corporation" variant of AVIC
- Provincial SOE variants
- Merged/renamed companies post-2020

**Action:**
1. **Update `data/prc_soe_database.json`:**
   - Add AVIC variant: "Aviation Industry Corporation"
   - Add CASC variant: "China Aerospace Science"
   - Add CASIC variant: "China Aerospace Science and Industry"

2. **Research recent SOE changes:**
   - Check 2020-2025 SOE mergers/acquisitions
   - Add new names to aliases_variants
   - Update known_subsidiaries

**Sources:**
- `data/prc_soe_historical_database.json` (already have this!)
- SASAC official SOE list updates

---

### 6. Cross-Source Validation 🔍 HIGH VALUE
**Expected Improvement:** Identify systemic issues

#### Cross-Reference Analysis:
Compare same entities across different data sources:

**Example:**
```sql
-- Find entities in USPTO but not in USAspending
SELECT DISTINCT u.assignee_name
FROM uspto_patents_chinese u
WHERE u.assignee_name LIKE '%HUAWEI%'
AND NOT EXISTS (
    SELECT 1 FROM usaspending_china_305 usa
    WHERE usa.recipient_name LIKE '%HUAWEI%'
);
```

**Benefits:**
- Identify inconsistent detection
- Find spelling variations
- Discover false negatives (missed entities)
- Validate detection quality

**Create script:** `scripts/cross_source_entity_validator.py`

---

## Medium-term Actions (Next Week)

### 7. Re-process Data with Fixed Detection 🔄 CRITICAL
**Expected Improvement:** Apply all fixes to production data

#### Re-processing Priority:
1. **USAspending 374-column** (100GB, 46% of dataset)
   - High volume, high impact
   - Expected: -800 false positives

2. **TED** (if using enhanced detector)
   - Expected: -50 false positives
   - Nuctech now detected

3. **USPTO** (if needed)
   - Expected: -2,000 false positives from geographic patterns

**Monitoring:**
- Track before/after counts
- Validate precision improvement
- Check for unexpected drops (could indicate bugs)

---

### 8. Implement Confidence Scoring 📈 ADVANCED
**Expected Improvement:** Better prioritization, not precision

#### Multi-Signal Confidence Scores:
Instead of binary detection, use weighted confidence:

```python
confidence_score = 0

# Tier 1: Country code (100 points)
if country_code == 'CN': confidence_score += 100

# Tier 2: Known company (80 points)
if is_known_company(): confidence_score += 80

# Tier 3: Geographic indicators (50 points)
if chinese_city_detected(): confidence_score += 50

# Tier 4: Postal code (60 points)
if chinese_postal_code(): confidence_score += 60

# Classification
if confidence_score >= 100: tier = "VERY_HIGH"
elif confidence_score >= 70: tier = "HIGH"
elif confidence_score >= 50: tier = "MEDIUM"
else: tier = "LOW"
```

**Benefits:**
- Prioritize manual review (start with LOW confidence)
- Set thresholds for different use cases
- Better reporting and analytics

**Already implemented in:** USPTO streaming processor
**Need to implement in:** USAspending, TED

---

### 9. Add Machine Learning Validation (Optional) 🤖 ADVANCED
**Expected Improvement:** Catch edge cases

#### Approach:
Use existing high-confidence detections as training data:

1. **Features:**
   - Entity name characteristics (length, character distribution)
   - Geographic indicators present
   - Contract/patent text content
   - Historical patterns

2. **Model:**
   - Random Forest or Gradient Boosting
   - Train on confidence_score >= 100 (positive) and known false positives (negative)
   - Predict probability for uncertain cases (confidence 50-70)

3. **Use case:**
   - Validate uncertain detections
   - Identify new false positive patterns
   - Suggest additional filters

**Time investment:** 4-8 hours
**Value:** Moderate - only worth it if dealing with thousands of uncertain cases

---

## Validation & Quality Assurance

### 10. Create Automated Precision Monitoring 📊
**Continuous improvement**

#### Metrics Dashboard:
```python
# Track over time
precision_metrics = {
    'total_detections': count,
    'false_positive_rate': estimated_fp_rate,
    'true_positive_rate': estimated_tp_rate,
    'precision': estimated_precision,
    'by_source': {
        'usaspending': {...},
        'ted': {...},
        'uspto': {...},
        'openalex': {...}
    }
}
```

**Create script:** `scripts/precision_monitoring_dashboard.py`

**Benefits:**
- Track improvements over time
- Identify regressions quickly
- Prioritize improvement efforts

---

## Estimated Impact Summary

| Action | Time | Precision Gain | Priority |
|--------|------|----------------|----------|
| 1. Fix configuration gaps | 30 min | +1-2% | ⚡ HIGH |
| 2. Expand false positive filters | 1 hour | +1-2% | ⚡ HIGH |
| 3. Apply word boundaries to remaining scripts | 2 hours | +0.5-1% | 🎯 MEDIUM |
| 4. Manual validation sample | 3 hours | Identify issues | ⚡ CRITICAL |
| 5. Expand SOE database | 1 hour | +0.5-1% recall | 🎯 MEDIUM |
| 6. Cross-source validation | 2 hours | Identify issues | 🎯 HIGH |
| 7. Re-process data | 8-12 hours | Apply all fixes | ⚡ CRITICAL |
| 8. Implement confidence scoring | 4 hours | Better prioritization | 💡 NICE-TO-HAVE |
| 9. ML validation (optional) | 8 hours | Edge cases | 💡 OPTIONAL |
| 10. Precision monitoring | 2 hours | Ongoing tracking | 🎯 MEDIUM |

---

## Recommended Next Steps (Right Now)

### Option A: Quick Wins (1-2 hours total) ⚡
**Best for immediate impact**

1. Update `prc_identifiers.json` with missing cities/districts (30 min)
2. Add false positive filters to all processors (1 hour)
3. Re-run validation tests to confirm improvements (15 min)
4. Generate updated precision estimate (15 min)

**Expected gain:** +2-3% precision

---

### Option B: Comprehensive Improvement (4-6 hours) 🎯
**Best for thorough improvement**

1. Do Option A (2 hours)
2. Manual validation of 300 sample records (3 hours)
3. Update SOE database based on findings (1 hour)
4. Create cross-source validator script (2 hours)
5. Document all findings and next steps (30 min)

**Expected gain:** +3-5% precision + identification of systemic issues

---

### Option C: Full Re-processing (12-24 hours) 🔄
**Best for production deployment**

1. Do Option B (8 hours)
2. Re-process USAspending 374-column (4-6 hours)
3. Re-process TED with improved detection (2-4 hours)
4. Re-process USPTO if needed (4-6 hours)
5. Generate before/after comparison reports (2 hours)
6. Update all documentation (1 hour)

**Expected gain:** Full application of all fixes to production data

---

## My Recommendation

**Start with Option A (Quick Wins)** - We can complete this right now:

1. ✅ Update configuration files (30 min)
2. ✅ Add false positive filters (1 hour)
3. ✅ Re-validate (15 min)
4. ✅ Generate report (15 min)

This gives us immediate +2-3% precision improvement with minimal time investment.

Then while **OpenAlex is processing in background** (still 660 files remaining), we can:
- Start manual validation sampling
- Build cross-source validator
- Plan full re-processing strategy

**Ready to start with Option A?**

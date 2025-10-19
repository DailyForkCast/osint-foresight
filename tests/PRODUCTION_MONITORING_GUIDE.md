# Production Monitoring Guide - Chinese Entity Detection

**Purpose**: Track detection performance in production and collect patterns for continuous improvement
**Date**: 2025-10-18
**Status**: ✅ ACTIVE MONITORING

---

## 📊 What to Monitor

### 1. New Bypass Attempts

**What to watch for:**
- Entities that should be detected but aren't
- New obfuscation techniques
- Spelling variations not in current patterns

**How to identify:**
- Manual review of undetected records
- User reports of missed entities
- Cross-reference with known Chinese companies

**Action when found:**
```python
# Add to CHINESE_NAME_PATTERNS in scripts/process_usaspending_305_column.py
CHINESE_NAME_PATTERNS = {
    # ... existing patterns ...
    'new_variant',  # ADD NEW PATTERN HERE
}
```

**Log format:**
```
Date: 2025-10-XX
Bypass Type: Misspelling
Entity: "Huwaie" (should be Huawei)
Action: Added 'huwaie' to CHINESE_NAME_PATTERNS
Test: Created regression test in tests/test_regression.py
```

---

### 2. False Positives

**What to watch for:**
- US companies incorrectly flagged as Chinese
- Restaurant chains with "China" in name
- Geographic locations (cities, beaches)
- Legitimate substring matches

**How to identify:**
- Manual review of high-volume detections
- User reports of incorrect flags
- Cross-reference with known US companies

**Action when found:**
```python
# Add to FALSE_POSITIVES in scripts/process_usaspending_305_column.py
FALSE_POSITIVES = {
    # ... existing patterns ...
    'new_false_positive_pattern',  # ADD HERE
}
```

**Log format:**
```
Date: 2025-10-XX
False Positive: "China Garden Restaurant"
Type: US restaurant chain
Action: Added 'china garden' to FALSE_POSITIVES
Test: Added to test_false_positive_regression tests
```

---

### 3. Edge Cases

**What to watch for:**
- Unusual character encodings
- Non-Latin scripts
- Very long company names
- Special characters/symbols
- Mixed language names

**How to identify:**
- Processing errors in logs
- Inconsistent detection across similar records
- Unicode handling issues

**Action when found:**
```python
# Add to edge case tests in tests/test_regression.py
def test_new_edge_case(self):
    """Description of edge case"""
    assert self.processor._has_chinese_name("edge case example") == expected_result
```

**Log format:**
```
Date: 2025-10-XX
Edge Case: Company name with emoji characters
Behavior: Detection failed due to unicode error
Action: Added unicode normalization
Test: Added test_emoji_in_company_name
```

---

## 📈 Performance Metrics to Track

### Detection Rate Metrics

**Track monthly:**
```sql
-- Example query for USAspending
SELECT
    DATE_TRUNC('month', action_date) as month,
    COUNT(*) as total_records,
    COUNT(CASE WHEN detection_count > 0 THEN 1 END) as chinese_detected,
    ROUND(100.0 * COUNT(CASE WHEN detection_count > 0 THEN 1 END) / COUNT(*), 2) as detection_rate_pct
FROM usaspending_china_305
GROUP BY month
ORDER BY month DESC
LIMIT 12;
```

**Expected patterns:**
- USAspending: ~0.5-1% detection rate
- TED: ~0.5-0.6% detection rate
- USPTO: ~40% detection rate
- OpenAlex: Limited by metadata availability

**Alert if:**
- Detection rate drops >20% month-over-month
- Detection rate spikes >50% month-over-month
- May indicate pattern changes or data quality issues

---

### Confidence Distribution

**Track quarterly:**
```sql
-- Example: Distribution of confidence scores
SELECT
    CASE
        WHEN highest_confidence >= 0.90 THEN 'High (0.90+)'
        WHEN highest_confidence >= 0.65 THEN 'Medium (0.65-0.89)'
        WHEN highest_confidence >= 0.30 THEN 'Low (0.30-0.64)'
        ELSE 'Very Low (<0.30)'
    END as confidence_tier,
    COUNT(*) as record_count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER(), 2) as percentage
FROM usaspending_china_305
WHERE detection_count > 0
GROUP BY confidence_tier
ORDER BY MIN(highest_confidence) DESC;
```

**Expected distribution:**
- High confidence (0.90+): 60-70% (country code matches)
- Medium confidence (0.65-0.89): 25-35% (name matches)
- Low confidence (0.30-0.64): 5-10% (product sourcing)

**Alert if:**
- High confidence drops below 50%
- Low confidence exceeds 20%
- May indicate data quality degradation

---

### False Positive Rate

**Track with manual sampling:**

**Monthly sampling process:**
1. Random sample 100 detections per data source
2. Manual review for false positives
3. Calculate precision: `true_positives / (true_positives + false_positives)`
4. Target: ≥95% precision

**Sample review template:**
```
Month: 2025-10
Data Source: USAspending
Sample Size: 100 detections
True Positives: 96
False Positives: 4
Precision: 96%

False Positive Examples:
1. "China Creek Cafe" - US restaurant
2. "Fine China Company" - US ceramics
3. "China Mountain Outfitters" - US outdoor gear
4. "China Peak Ski Resort" - US ski resort

Actions:
- Added 'china creek', 'china mountain', 'china peak' to FALSE_POSITIVES
- Created regression tests for ski resort/cafe patterns
```

---

## 🔍 Pattern Collection Workflow

### Step 1: Identify New Pattern

**Sources:**
- Production logs
- User reports
- Manual review
- Cross-reference with external databases

**Documentation:**
```
Pattern Type: [Misspelling|Abbreviation|Obfuscation|False Positive]
Entity: "exact string that triggered/should trigger detection"
Data Source: USAspending|TED|USPTO|etc
Frequency: How often seen in production
Current Behavior: What happens now
Expected Behavior: What should happen
```

---

### Step 2: Validate Pattern

**Validation checklist:**
- [ ] Confirmed across multiple records (not one-off)
- [ ] Cross-referenced with external sources
- [ ] Won't create new false positives
- [ ] Fits existing pattern structure
- [ ] Tested manually with detection functions

**Validation command:**
```bash
python -c "from scripts.process_usaspending_305_column import USAspending305Processor; p = USAspending305Processor(); print(p._has_chinese_name('NEW PATTERN HERE'))"
```

---

### Step 3: Add to Codebase

**For new Chinese entity patterns:**
```python
# File: scripts/process_usaspending_305_column.py
# Line: ~40 (CHINESE_NAME_PATTERNS)

CHINESE_NAME_PATTERNS = {
    # ... existing patterns ...
    'new_pattern',  # ADD HERE with comment explaining why
}
```

**For new false positives:**
```python
# File: scripts/process_usaspending_305_column.py
# Line: ~47-75 (FALSE_POSITIVES)

FALSE_POSITIVES = {
    # ... existing patterns ...
    'new_false_positive',  # ADD HERE with comment explaining source
}
```

---

### Step 4: Create Regression Test

**Add to `tests/test_regression.py`:**

```python
def test_new_pattern_YYYYMMDD(self):
    """Description: Why this pattern was added

    Date Added: YYYY-MM-DD
    Issue: Brief description of problem
    Fix: What was added to fix it
    """
    assert self.processor._has_chinese_name("pattern to test") == expected_result
```

---

### Step 5: Validate Changes

**Run full test suite:**
```bash
# All tests including new regression test
pytest tests/ -v --tb=short

# Just the new test
pytest tests/test_regression.py::TestClassName::test_new_pattern_YYYYMMDD -v
```

**Expected results:**
- All existing tests still pass (no regressions)
- New test passes
- No new failures introduced

---

### Step 6: Document Change

**Update change log in `tests/PRODUCTION_MONITORING_LOG.md`:**
```markdown
## 2025-10-XX

### Pattern Added: [Name]
- **Type**: Misspelling/Abbreviation/etc
- **Pattern**: 'new_pattern'
- **Location**: CHINESE_NAME_PATTERNS / FALSE_POSITIVES
- **Reason**: Brief explanation
- **Test**: test_new_pattern_YYYYMMDD
- **Impact**: X records affected in production
```

---

## 📝 Monitoring Schedule

### Daily (Automated)
- [ ] Check processing logs for errors
- [ ] Monitor detection counts for anomalies
- [ ] Review any user-reported issues

### Weekly (Manual - 30 minutes)
- [ ] Review 20 random detections per data source
- [ ] Check for new obfuscation patterns
- [ ] Identify any recurring false positives
- [ ] Update pattern lists if needed

### Monthly (Manual - 2 hours)
- [ ] Sample 100 detections per source for precision
- [ ] Calculate false positive rate
- [ ] Review confidence score distribution
- [ ] Analyze detection rate trends
- [ ] Update regression tests for new patterns

### Quarterly (Manual - 4 hours)
- [ ] Comprehensive performance review
- [ ] Update detection methodology if needed
- [ ] Review threshold values (confidence scores)
- [ ] Assess need for major improvements
- [ ] Update documentation

---

## 🚨 Alert Thresholds

**Immediate action required:**
- Detection rate drops >30% from baseline
- False positive rate exceeds 10%
- Processing errors >5% of records
- Critical bypass reported (known Chinese entity not detected)

**Review within 1 week:**
- Detection rate changes 10-30%
- False positive rate 5-10%
- New pattern appears >5 times
- User reports uncertainty in detection

**Monitor, no immediate action:**
- Detection rate changes <10%
- False positive rate <5%
- One-off unusual patterns
- Expected seasonal variations

---

## 📊 Reporting Template

### Monthly Detection Report

**Period:** YYYY-MM
**Data Sources:** USAspending, TED, USPTO, OpenAlex

**Metrics:**
- Total records processed: X,XXX,XXX
- Chinese entities detected: XX,XXX
- Overall detection rate: X.XX%
- False positive rate: X.X% (from sampling)
- Precision: XX.X%

**Patterns Added:**
- X new misspelling patterns
- X new false positive exclusions
- X edge case fixes

**Issues Identified:**
- Brief description of any problems
- Actions taken or planned

**Recommendations:**
- Any suggested improvements
- Patterns to watch next month

---

## 🔄 Continuous Improvement Process

### Pattern Discovery → Validation → Implementation → Testing → Deployment

1. **Discovery**: Find new pattern in production
2. **Validation**: Confirm it's real and recurring
3. **Implementation**: Add to appropriate set (CHINESE_NAME_PATTERNS or FALSE_POSITIVES)
4. **Testing**: Create regression test
5. **Deployment**: Commit to git, deploy to production
6. **Monitoring**: Track impact on detection metrics

**Cycle time target:** <1 week from discovery to deployment

---

## 📞 Contact & Escalation

**For pattern additions:**
- Review and add following this guide
- Create regression test
- Update production monitoring log

**For major issues:**
- Critical bypasses (known entities not detected)
- Widespread false positives (>10% of detections)
- System errors or performance degradation

**For methodology changes:**
- Changes to confidence scoring
- New detection methods
- Threshold adjustments
- Major refactoring

---

## 📚 Additional Resources

- [Detection System Documentation](../README.md#chinese-entity-detection-system)
- [Issue Tracker](ISSUE_TRACKER.md) - Original 9 issues and fixes
- [Validation Findings](VALIDATION_FINDINGS_REPORT.md) - Red team results
- [Fix Implementation](FIX_IMPLEMENTATION_COMPLETE.md) - What we fixed
- [Unit Tests](unit/test_chinese_detection.py) - 31 core tests
- [Integration Tests](integration/test_detection_pipeline.py) - 8 pipeline tests
- [Regression Tests](test_regression.py) - 28 regression tests

---

**Last Updated:** 2025-10-18
**Next Review:** 2025-11-18
**Monitoring Status:** ✅ ACTIVE

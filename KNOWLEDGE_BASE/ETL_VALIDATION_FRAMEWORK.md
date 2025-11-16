# ETL VALIDATION FRAMEWORK - Zero Fabrication Protocol
**Date:** November 3, 2025
**Purpose:** Comprehensive QA/QC measures for bilateral linkage table ETL pipelines
**Compliance:** Zero Fabrication Protocol, IC standards alignment

---

## CRITICAL PRINCIPLE: NO FABRICATION

**Every link must be:**
1. ✅ Derived from actual data in source tables
2. ✅ Traceable to specific source records
3. ✅ Validated with explicit match criteria
4. ✅ Documented with confidence level
5. ✅ Reversible (can delete and regenerate)

**NEVER:**
- ❌ Infer relationships without explicit evidence
- ❌ Assume entity equivalence without validation
- ❌ Create temporal links based solely on proximity
- ❌ Extrapolate missing data
- ❌ Use "common sense" to fill gaps

---

## 1. ENTITY MATCHING VALIDATION

### Problem: Same entity, different names
- "Huawei Technologies Co., Ltd." vs "Huawei" vs "华为"
- "University of Cambridge" vs "Cambridge University" vs "Cambridge"

### Validation Requirements:

**A. Exact Match (Confidence: 100%)**
```sql
-- SAFE: Identical strings
WHERE source1.entity_name = source2.entity_name
```
- ✅ No ambiguity
- ✅ Can link directly
- ⚠️ Misses variants

**B. Normalized Match (Confidence: 95%)**
```sql
-- SAFE: After standardization
WHERE UPPER(TRIM(source1.entity_name)) = UPPER(TRIM(source2.entity_name))
```
- ✅ Handles case/whitespace differences
- ⚠️ Still misses "Inc." vs "Incorporated"

**C. GLEIF LEI Match (Confidence: 100%)**
```sql
-- GOLD STANDARD: Legal Entity Identifier
WHERE source1.lei = source2.lei
  AND source1.lei IS NOT NULL
```
- ✅ Globally unique identifier
- ✅ Authoritative
- ⚠️ Only ~2M entities have LEIs

**D. Fuzzy Match (Confidence: 60-90%)**
```python
# REQUIRES MANUAL REVIEW
if similarity(name1, name2) > 0.90:  # High threshold
    flag_for_review()
```
- ❌ NEVER auto-link on fuzzy match alone
- ✅ Use for flagging candidates
- ✅ Require manual validation

**E. Cross-Reference Match (Confidence: 85-95%)**
```sql
-- Multiple weak signals = stronger confidence
WHERE source1.name LIKE '%' || source2.short_name || '%'
  AND source1.country_code = source2.country_code
  AND source1.sector = source2.sector
```
- ✅ Multiple criteria reduce false positives
- ⚠️ Still requires validation sample

### MANDATORY ENTITY MATCH VALIDATION:

**Before ETL runs:**
1. Check entity name distributions in both tables
2. Identify ambiguous names (e.g., "Google" = Google LLC? Alphabet Inc? Google China?)
3. Create disambiguation rules

**During ETL:**
1. Track match method for each link (`exact`, `lei`, `normalized`, `fuzzy_validated`)
2. Log match confidence score (0-100)
3. Record source IDs for audit trail

**After ETL:**
1. Sample 100 random links for manual verification
2. Verify no entity matched to multiple entities (1-to-many check)
3. Verify entities in expected country (e.g., Lithuanian entity for Lithuania event)

---

## 2. TEMPORAL ALIGNMENT VALIDATION

### Problem: Different date meanings
- Patent `filing_date` vs `grant_date` vs `priority_date`
- Contract `notice_date` vs `award_date` vs `completion_date`
- Bilateral event `announcement_date` vs `effective_date`

### Validation Requirements:

**A. Date Field Documentation**
```python
DATE_FIELD_MEANINGS = {
    'ted_contracts': {
        'publication_date': 'Date TED notice published (NOT contract award)',
        'award_date': 'Date contract awarded to winner',
        'deadline_date': 'Submission deadline for bids'
    },
    'bilateral_events': {
        'event_date': 'Date event occurred or announced',
        'effective_date': 'Date policy took effect (may be NULL)'
    },
    'uspto_patents': {
        'filing_date': 'Date application filed',
        'grant_date': 'Date patent granted',
        'priority_date': 'Earliest filing date worldwide'
    }
}
```

**B. Temporal Link Criteria**
```sql
-- SAFE: Explicit date range
WHERE patent.grant_date BETWEEN event.event_date
                            AND DATE(event.event_date, '+2 years')
  AND link_type = 'granted_within_2_years_after_event'

-- UNSAFE: Implicit causality
-- WHERE patent.grant_date > event.event_date  -- NO! Implies causation
```

**C. Lag Windows**
```python
RESEARCH_TO_PATENT_LAG = {
    'minimum': 365,    # 1 year minimum (extremely fast)
    'typical': 1095,   # 3 years typical
    'maximum': 3650    # 10 years maximum (very old research)
}

# Document assumption
if days_between(paper_date, patent_date) < RESEARCH_TO_PATENT_LAG['minimum']:
    log_warning('Unusually fast research-to-patent: verify data')
```

### MANDATORY TEMPORAL VALIDATION:

**Before ETL:**
1. Document which date fields are used for matching
2. Define maximum allowed temporal gap
3. Identify NULL date handling strategy

**During ETL:**
1. Track temporal gap for each link (days between events)
2. Flag outliers (e.g., patent "based on" research published 20 years later)
3. Record date field used (`event_date`, `effective_date`, etc.)

**After ETL:**
1. Plot histogram of temporal gaps (should show expected distribution)
2. Verify no future links (patent_date > today)
3. Check for temporal outliers (>3 std deviations from mean)

---

## 3. GEOGRAPHIC MATCHING VALIDATION

### Problem: Country code inconsistencies
- ISO-2 (CN) vs ISO-3 (CHN) vs Name (China)
- Multiple country affiliations (paper with authors from 5 countries)
- Disputed territories (Taiwan, Hong Kong)

### Validation Requirements:

**A. Country Code Standardization**
```python
# REQUIRED: Always use ISO-2 (Alpha-2)
COUNTRY_CODES = {
    'CN': 'China',
    'LT': 'Lithuania',
    'TW': 'Taiwan',  # Per project policy: separate from CN
    'HK': 'Hong Kong'  # Separate from CN
}

# Conversion table required
ISO3_TO_ISO2 = {
    'CHN': 'CN',
    'LTU': 'LT',
    'TWN': 'TW'
}
```

**B. Multi-Country Handling**
```sql
-- SAFE: Explicit criteria
WHERE (source1.country_code = 'LT' OR source2.country_code = 'LT')
  AND (source1.country_code = 'CN' OR source2.country_code = 'CN')
  AND link_note = 'Lithuania-China collaboration'

-- UNSAFE: Ambiguous
-- WHERE source1.country_code = 'LT'  -- Is this LT-LT or LT-CN event?
```

**C. Geographic Scope Definition**
```python
# Document exactly what constitutes a "bilateral" link
BILATERAL_LINK_DEFINITION = {
    'bilateral_academic_links': 'Paper with >=1 Lithuanian author AND >=1 Chinese author',
    'bilateral_procurement_links': 'TED contract buyer in EU, contractor in China',
    'bilateral_patent_links': 'Patent with >=1 inventor in country A, assignee in country B'
}
```

### MANDATORY GEOGRAPHIC VALIDATION:

**Before ETL:**
1. Verify country code format consistency across source tables
2. Create mapping table for any non-ISO-2 codes
3. Define Taiwan/Hong Kong handling per project policy

**During ETL:**
1. Track which countries are involved in each link
2. Flag links involving >2 countries (may indicate multi-lateral)
3. Verify country codes are valid ISO-2

**After ETL:**
1. Verify no XX or NULL country codes in links
2. Check distribution by country pair (should match expected patterns)
3. Validate Taiwan is classified separately per project policy

---

## 4. CONFIDENCE SCORING

### Every link must have confidence score (0-100)

**Confidence Levels:**

**100% - Authoritative Identifier Match**
- LEI matched across sources
- DOI matched across sources
- USPTO patent number matched

**95% - Exact String Match + Context**
- Exact entity name + country + sector match
- Exact date + entity + transaction type match

**85% - Normalized Match + Context**
- Normalized name + country match
- Date within 30 days + normalized name

**75% - Strong Circumstantial**
- Similar name (>90% similarity) + country + temporal proximity
- Geographic + temporal + domain alignment

**60% - Moderate Circumstantial**
- Fuzzy name match (80-90%) + country OR temporal
- Requires manual review before use

**<60% - Insufficient Evidence**
- Do NOT create link
- Flag for future investigation

### MANDATORY CONFIDENCE TRACKING:

```sql
CREATE TABLE bilateral_[type]_links (
    link_id INTEGER PRIMARY KEY,
    source_table_1 TEXT NOT NULL,
    source_id_1 INTEGER NOT NULL,
    source_table_2 TEXT NOT NULL,
    source_id_2 INTEGER NOT NULL,

    -- REQUIRED FIELDS
    match_method TEXT NOT NULL,  -- 'exact', 'lei', 'normalized', 'fuzzy_validated'
    confidence_score INTEGER NOT NULL CHECK(confidence_score >= 60 AND confidence_score <= 100),
    match_criteria TEXT NOT NULL,  -- JSON: {"entity_match": "exact", "temporal_gap_days": 45, ...}

    -- AUDIT TRAIL
    created_date TEXT NOT NULL,
    created_by TEXT NOT NULL,  -- Script name or analyst ID
    validation_status TEXT DEFAULT 'unvalidated',  -- 'unvalidated', 'validated', 'rejected'
    validation_notes TEXT,

    -- PROVENANCE
    data_source_1 TEXT NOT NULL,
    data_source_2 TEXT NOT NULL,
    collection_date_1 TEXT NOT NULL,
    collection_date_2 TEXT NOT NULL
);
```

---

## 5. CAUSALITY VS CORRELATION

### CRITICAL: Temporal proximity ≠ Causation

**SAFE LANGUAGE:**
- ✅ "Patent granted 18 months after bilateral agreement"
- ✅ "Contract awarded within 6 months of diplomatic event"
- ✅ "Research collaboration began same year as MoU signing"

**UNSAFE LANGUAGE:**
- ❌ "Patent resulted from bilateral agreement"
- ❌ "Diplomatic event led to contract"
- ❌ "MoU caused research collaboration"

### Link Type Classification:

**Type 1: Direct Attribution**
```sql
-- REQUIRES: Explicit citation or reference
WHERE patent.references LIKE '%agreement_id%'
   OR paper.acknowledgments LIKE '%funded by agreement_id%'
```
- Can say: "Patent explicitly references agreement"
- Confidence: 100%

**Type 2: Temporal Association**
```sql
-- NO CAUSALITY IMPLIED
WHERE event2_date BETWEEN event1_date AND DATE(event1_date, '+1 year')
```
- Can say: "Event2 occurred within 1 year of Event1"
- Cannot say: "Event1 caused Event2"
- Confidence: 85% (that temporal association exists)

**Type 3: Thematic Association**
```sql
-- Same technology domain
WHERE patent.technology_field = agreement.technology_field
  AND patent.assignee_country = agreement.country_b
```
- Can say: "Patent in same technology domain as agreement"
- Cannot say: "Patent implements agreement"
- Confidence: 75%

---

## 6. ETL VALIDATION CHECKPOINTS

### Stage 1: Pre-ETL Validation

**1.1 Source Data Quality Check**
```python
def validate_source_tables():
    # Check 1: Tables exist and accessible
    assert table_exists('ted_contracts')
    assert table_exists('bilateral_events')

    # Check 2: Required fields present
    assert 'entity_name' in get_columns('ted_contracts')
    assert 'event_date' in get_columns('bilateral_events')

    # Check 3: No mass NULLs in key fields
    null_rate = get_null_rate('ted_contracts', 'entity_name')
    assert null_rate < 0.10, f"Too many NULLs: {null_rate:.1%}"

    # Check 4: Date fields parseable
    assert all_dates_valid('bilateral_events', 'event_date')

    # Check 5: Country codes valid
    invalid_codes = get_invalid_country_codes('ted_contracts')
    assert len(invalid_codes) == 0, f"Invalid codes: {invalid_codes}"
```

**1.2 Expected Volume Estimation**
```python
# Estimate expected links BEFORE running ETL
def estimate_link_volume():
    ted_chinese_contractors = count_where('ted_contracts',
                                          'contractor_country = "CN"')
    bilateral_events = count('bilateral_events')

    # Conservative estimate: 5-10% of Chinese contractors linked to events
    expected_min = ted_chinese_contractors * 0.05
    expected_max = ted_chinese_contractors * 0.10

    return (expected_min, expected_max)

# If actual results outside expected range, STOP and investigate
```

### Stage 2: During-ETL Validation

**2.1 Real-Time Quality Checks**
```python
def validate_link_as_created(link):
    # Check 1: No self-links
    assert link.source_id_1 != link.source_id_2 or link.source_table_1 != link.source_table_2

    # Check 2: Confidence score present and valid
    assert 60 <= link.confidence_score <= 100

    # Check 3: Match method documented
    assert link.match_method in ['exact', 'lei', 'normalized', 'fuzzy_validated']

    # Check 4: Temporal sanity
    if link.has_dates():
        assert link.date_2 >= link.date_1, "Reverse chronology"
        gap_days = (link.date_2 - link.date_1).days
        assert gap_days < 3650, "Gap >10 years - unlikely"

    # Check 5: Geographic consistency
    if link.has_countries():
        assert link.country_1 in VALID_ISO2_CODES
        assert link.country_2 in VALID_ISO2_CODES
```

**2.2 Running Statistics**
```python
# Track metrics during ETL
etl_stats = {
    'links_created': 0,
    'links_rejected_low_confidence': 0,
    'links_rejected_geographic': 0,
    'links_rejected_temporal': 0,
    'average_confidence': 0.0,
    'by_match_method': {'exact': 0, 'lei': 0, 'normalized': 0, 'fuzzy': 0}
}

# ALERT if:
# - Reject rate > 50% (criteria too strict or data quality issue)
# - Reject rate < 5% (criteria too loose, likely creating false positives)
# - Average confidence < 75 (too many weak links)
```

### Stage 3: Post-ETL Validation

**3.1 Statistical Validation**
```python
def validate_completed_etl(table_name):
    # Check 1: Volume within expected range
    actual_count = count(table_name)
    expected_min, expected_max = estimate_link_volume()
    assert expected_min <= actual_count <= expected_max, \
        f"Volume unexpected: {actual_count} not in [{expected_min}, {expected_max}]"

    # Check 2: No duplicate links
    duplicates = find_duplicates(table_name,
                                 ['source_table_1', 'source_id_1',
                                  'source_table_2', 'source_id_2'])
    assert len(duplicates) == 0, f"Found {len(duplicates)} duplicate links"

    # Check 3: Confidence distribution
    confidence_dist = get_distribution(table_name, 'confidence_score')
    assert confidence_dist['mean'] >= 75, "Average confidence too low"

    # Check 4: Geographic distribution
    country_pairs = get_top_country_pairs(table_name, n=10)
    # Manual review: Do top pairs make sense?

    # Check 5: Temporal distribution
    temporal_gaps = get_distribution(table_name, 'temporal_gap_days')
    assert temporal_gaps['max'] < 3650, "Some gaps >10 years"
    # Plot histogram for manual review
```

**3.2 Sample Validation (MANDATORY)**
```python
def manual_sample_validation(table_name, sample_size=100):
    """
    CRITICAL: Human review of random sample
    """
    # Stratified sampling
    samples = {
        'high_confidence': sample_where(table_name, 'confidence_score >= 90', n=30),
        'medium_confidence': sample_where(table_name, 'confidence_score BETWEEN 75 AND 89', n=40),
        'low_confidence': sample_where(table_name, 'confidence_score BETWEEN 60 AND 74', n=30)
    }

    # Output for manual review
    for category, records in samples.items():
        export_for_review(records, f'validation_{category}.xlsx')

    print(f"""
    MANUAL VALIDATION REQUIRED:
    - Review validation_{category}.xlsx files
    - For each link, verify:
      1. Entities are actually same organization
      2. Temporal relationship makes sense
      3. Geographic assignment correct
      4. Confidence score appropriate

    - Calculate precision: (correct_links / total_reviewed)
    - If precision < 90%: STOP, revise matching criteria
    - If precision >= 95%: ETL validated, can use links
    - If precision 90-95%: Acceptable, but note limitations
    """)
```

**3.3 Cross-Table Consistency**
```python
def validate_cross_table_consistency():
    # Check 1: All source IDs exist
    orphaned = find_orphaned_links('bilateral_patent_links',
                                   'source_table_1', 'source_id_1')
    assert len(orphaned) == 0, f"Found {len(orphaned)} orphaned links"

    # Check 2: Country codes consistent across tables
    # If bilateral_patent_links says entity in CN,
    # verify entities table agrees

    # Check 3: No conflicting links
    # E.g., entity can't be in both CN and LT simultaneously
```

---

## 7. FABRICATION RED FLAGS

### Automatic Rejection Criteria

**Reject if:**
1. ❌ Entity name match <80% similarity AND no other validation
2. ❌ Temporal gap >10 years without explicit justification
3. ❌ Geographic mismatch (entity in CN, event in LT, no relationship documented)
4. ❌ Confidence score <60
5. ❌ Source ID doesn't exist in source table
6. ❌ NULL in any required field
7. ❌ Created date in future
8. ❌ Same link already exists (duplicate)

### Manual Review Required:

**Flag for review if:**
- ⚠️ Confidence score 60-74
- ⚠️ Fuzzy match used (even if high similarity)
- ⚠️ Temporal gap <30 days (unusually fast)
- ⚠️ Temporal gap >5 years (unusually slow)
- ⚠️ Entity appears in >20 links (possible hub entity or matching error)
- ⚠️ Country pair is unusual (e.g., Lithuania-North Korea)

---

## 8. ETL ROLLBACK PLAN

### Every ETL must be reversible

**Before ETL:**
```sql
-- Create snapshot
CREATE TABLE bilateral_patent_links_backup_20251103 AS
SELECT * FROM bilateral_patent_links;

-- Document pre-ETL state
INSERT INTO etl_runs (
    run_id, table_name, run_date, records_before,
    etl_script, parameters
) VALUES (
    'ETL_20251103_001', 'bilateral_patent_links', '2025-11-03',
    (SELECT COUNT(*) FROM bilateral_patent_links),
    'etl_patent_links_v2.py', '{"confidence_threshold": 75, ...}'
);
```

**After ETL:**
```sql
-- Document post-ETL state
UPDATE etl_runs SET
    records_after = (SELECT COUNT(*) FROM bilateral_patent_links),
    records_added = records_after - records_before,
    validation_status = 'pending',
    completion_date = '2025-11-03 15:30:00'
WHERE run_id = 'ETL_20251103_001';
```

**Rollback procedure:**
```sql
-- If validation fails
DELETE FROM bilateral_patent_links
WHERE created_date >= '2025-11-03' AND created_by = 'etl_patent_links_v2.py';

-- Verify rollback
SELECT COUNT(*) FROM bilateral_patent_links;  -- Should match records_before
```

---

## 9. DOCUMENTATION REQUIREMENTS

### Every ETL Pipeline Must Document:

**A. Matching Criteria Document**
```yaml
# etl_patent_links_matching_criteria.yaml
entity_matching:
  method: normalized_string_match
  preprocessing:
    - convert_to_uppercase
    - remove_legal_suffixes  # Inc., Ltd., Co.
    - remove_punctuation
  threshold: exact_match_only
  ambiguous_names:  # Known problematic entities
    - "Google": require_lei_or_manual_validation
    - "Huawei": check_subsidiary_vs_parent

temporal_matching:
  date_field_1: patent.grant_date
  date_field_2: agreement.effective_date
  allowed_gap_min: 0
  allowed_gap_max: 730  # 2 years
  justification: "Patents typically take 1-2 years to grant after research begins"

geographic_matching:
  country_field_1: patent.assignee_country_code
  country_field_2: agreement.country_b_code
  code_format: ISO-2
  multi_country_handling: require_at_least_one_match
```

**B. Validation Results Document**
```json
{
  "etl_run_id": "ETL_20251103_001",
  "table": "bilateral_patent_links",
  "validation_date": "2025-11-03",
  "sample_validation": {
    "sample_size": 100,
    "correct_links": 94,
    "precision": 0.94,
    "reviewer": "manual_review_analyst_1"
  },
  "statistical_validation": {
    "total_links": 1245,
    "average_confidence": 83.2,
    "confidence_distribution": {
      "90-100": 412,
      "80-89": 531,
      "70-79": 268,
      "60-69": 34
    },
    "temporal_gap_stats": {
      "mean_days": 456,
      "median_days": 421,
      "std_dev_days": 187,
      "outliers_flagged": 12
    }
  },
  "validation_status": "PASSED",
  "approved_by": "data_quality_team",
  "notes": "12 outliers flagged for secondary review. Precision 94% exceeds 90% threshold."
}
```

---

## 10. ETL PRIORITY RANKING

### Based on data availability and validation difficulty:

**TIER 1 - High Confidence, Ready to Execute:**

1. **bilateral_procurement_links (ted_contracts → bilateral_events)**
   - ✅ Both tables have reliable date fields
   - ✅ Country codes standardized
   - ✅ Geographic matching straightforward
   - ⚠️ Entity matching may need normalization

2. **bilateral_academic_links expansion (more CEIAS → entities)**
   - ✅ Already has 528 records (proven process)
   - ✅ University names relatively stable
   - ⚠️ Need to add new CEIAS reports as they become available

**TIER 2 - Moderate Complexity:**

3. **bilateral_investments (financial data → bilateral_events)**
   - ⚠️ Need external data source (Rhodium, Mercator, MOFCOM)
   - ⚠️ Investment amounts may be estimates
   - ⚠️ Deal dates may be announcement vs closing

4. **bilateral_agreements (policy docs → structured data)**
   - ⚠️ Requires document parsing (PDFs)
   - ⚠️ Need explicit identification of agreements (not just mentions)
   - ⚠️ Effective dates may differ from announcement dates

**TIER 3 - High Complexity, Requires Manual Input:**

5. **bilateral_sanctions_links (export controls → entities)**
   - ⚠️ Requires Entity List, SDN List, DPL List integration
   - ⚠️ Entity matching difficult (aliases, subsidiaries)
   - ⚠️ Temporal: list changes over time (need version tracking)

6. **bilateral_trade (Comtrade → bilateral flows)**
   - ⚠️ Massive dataset (UN Comtrade)
   - ⚠️ HS code classification required
   - ⚠️ Aggregation level decisions (country-level vs commodity-level)

---

## SUMMARY VALIDATION CHECKLIST

### Before any ETL runs:

- [ ] Source tables validated (exist, accessible, quality checked)
- [ ] Matching criteria documented in YAML
- [ ] Expected volume range calculated
- [ ] Confidence scoring rubric defined
- [ ] Rollback plan created
- [ ] Manual validation sample size determined

### During ETL:

- [ ] Real-time validation on each link
- [ ] Running statistics tracked
- [ ] Reject reasons logged
- [ ] Progress monitoring

### After ETL:

- [ ] Volume within expected range
- [ ] No duplicate links
- [ ] Confidence distribution acceptable (mean ≥75)
- [ ] Manual sample validation completed (precision ≥90%)
- [ ] Statistical outliers reviewed
- [ ] Cross-table consistency verified
- [ ] Validation results documented
- [ ] Backup created before deployment

### Documentation:

- [ ] Matching criteria YAML created
- [ ] Validation results JSON created
- [ ] Known limitations documented
- [ ] Rollback instructions documented
- [ ] ETL run logged in etl_runs table

---

**ZERO FABRICATION COMPLIANCE: Every link must have explicit evidence trail from source data to link creation. No inferences, no assumptions, no extrapolations.**

**"If we can't point to the specific source records and matching criteria that created the link, the link should not exist."**

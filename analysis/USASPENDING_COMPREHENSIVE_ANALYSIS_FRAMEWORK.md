# USAspending Comprehensive Analysis Framework

**Purpose:** Ensure most accurate and complete understanding of 166,558 China-related detections across 117.9M records

**Status:** Initial framework - to be executed systematically

---

## 1. DATA QUALITY ANALYSIS

### 1.1 Completeness Assessment
**Goal:** Understand data coverage and gaps

**Tests:**
- [ ] **Field Completeness Audit**
  - Count NULL/empty values per field across all 166,558 detections
  - Identify critical fields with high NULL rates
  - Document which fields are unreliable for analysis

- [ ] **Temporal Coverage Analysis**
  - Date range: earliest to latest transactions
  - Identify gaps in temporal coverage
  - Volume trends over time (are recent years better covered?)

- [ ] **Geographic Coverage**
  - Which Chinese cities/provinces appear most?
  - Hong Kong vs mainland distribution
  - US agency geographic patterns

**SQL Queries Needed:**
```sql
-- Field completeness
SELECT
  COUNT(*) as total,
  COUNT(recipient_name) as has_recipient,
  COUNT(award_description) as has_description,
  COUNT(awarding_agency) as has_agency,
  COUNT(action_date) as has_date
FROM usaspending_china_305;

-- Temporal distribution
SELECT
  strftime('%Y', action_date) as year,
  COUNT(*) as transactions,
  SUM(award_amount) as total_value
FROM usaspending_china_305
GROUP BY year
ORDER BY year;

-- Geographic patterns
SELECT
  recipient_country_name,
  pop_country_name,
  COUNT(*) as count
FROM usaspending_china_305
GROUP BY recipient_country_name, pop_country_name
ORDER BY count DESC;
```

### 1.2 Value Distribution Analysis
**Goal:** Identify anomalies and understand financial patterns

**Tests:**
- [ ] **Outlier Detection**
  - Top 10 highest value transactions (validate they're real)
  - Transactions with $0 amounts (why?)
  - Negative amounts (modifications/deobligations?)

- [ ] **Statistical Distribution**
  - Mean, median, mode of award amounts
  - Standard deviation
  - Percentile breakdown (25th, 50th, 75th, 90th, 99th)

- [ ] **Value Concentration**
  - Top 10 recipients by total value
  - Agency concentration (which agencies spend most?)
  - Temporal concentration (which years had highest spending?)

**Implementation:**
```python
# analyze_value_distributions.py
- Calculate statistics per format
- Identify top transactions for manual review
- Create value distribution histograms
- Flag suspicious patterns
```

### 1.3 Duplicate Detection
**Goal:** Ensure we're not double-counting

**Tests:**
- [ ] **Cross-Format Duplicates**
  - Already checked: 101↔305, 101↔206, 305↔206 overlaps
  - Validate these represent same transactions
  - Document deduplication strategy for combined analysis

- [ ] **Within-Format Duplicates**
  - Check for duplicate transaction_ids within each table
  - Identify near-duplicates (same recipient, amount, date)

- [ ] **Entity Name Variations**
  - "CHINA MOBILE" vs "CHINA MOBILE COMMUNICATIONS"
  - "HUAWEI TECHNOLOGIES" vs "HUAWEI TECH CO LTD"
  - Build entity resolution mapping

---

## 2. DETECTION ACCURACY VALIDATION

### 2.1 Precision Analysis (False Positive Rate)
**Goal:** Ensure detected records are truly China-related

**Tests:**
- [ ] **Manual Review Sample**
  - Randomly sample 100 detections from each format (300 total)
  - Manual classification: True Positive, False Positive, Uncertain
  - Calculate precision rate
  - Document false positive patterns

- [ ] **Low Confidence Review**
  - Review all detections with confidence < 0.70
  - Verify name-based detections (highest FP risk)
  - Document acceptable vs unacceptable false positives

- [ ] **Edge Case Analysis**
  - "CHINA" in street addresses (e.g., "123 China St")
  - Company names with geographic terms (not entity names)
  - Non-Chinese entities with Chinese-sounding names

**Sample Review Template:**
```
Transaction ID: [ID]
Recipient: [Name]
Detection Type: [country/name/etc]
True Positive? [YES/NO/UNCERTAIN]
Notes: [Why/why not]
```

### 2.2 Recall Analysis (False Negative Rate)
**Goal:** Estimate how many China-related transactions we missed

**Tests:**
- [ ] **Known Entity Search**
  - Create list of 50 known Chinese companies
  - Search full 117M records for these entities
  - Compare detection rate vs expected presence

- [ ] **Country Code Analysis**
  - Query full dataset for CHN/HKG country codes
  - Compare count to our detections
  - Investigate discrepancies

- [ ] **Random Sample Review**
  - Sample 10,000 NON-detected records randomly
  - Manual review for missed China connections
  - Estimate false negative rate

**SQL Query:**
```sql
-- Find potential misses in raw data
SELECT COUNT(*)
FROM [raw_usaspending_table]
WHERE (recipient_country LIKE '%CHINA%'
   OR recipient_country = 'CHN'
   OR pop_country LIKE '%CHINA%')
  AND transaction_id NOT IN (
    SELECT transaction_id FROM usaspending_china_305
  );
```

### 2.3 Confidence Score Validation
**Goal:** Verify confidence scores are meaningful

**Tests:**
- [ ] **Confidence vs Manual Review**
  - Sample 50 each from HIGH/MEDIUM/LOW confidence
  - Calculate actual precision for each tier
  - Validate confidence thresholds are appropriate

- [ ] **Detection Type Analysis**
  - Precision by detection type (country vs name vs entity)
  - Should country-based have higher precision than name-based
  - Validate our confidence scoring logic

---

## 3. SEMANTIC ANALYSIS

### 3.1 Award Description Analysis
**Goal:** Understand WHAT these transactions are for

**Tests:**
- [ ] **Topic Modeling**
  - Extract key terms from award_description field
  - Cluster transactions by topic
  - Identify common themes (research, procurement, grants, etc.)

- [ ] **Technology Focus**
  - Search descriptions for technology terms
  - AI, quantum, semiconductor, biotech keywords
  - Identify dual-use technology transfers

- [ ] **Program Analysis**
  - Group by program_title/program_number
  - Identify which US programs have most China involvement
  - Compare assistance vs contracts

**Implementation:**
```python
# semantic_analyzer.py
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

# Extract topics from descriptions
# Identify technology-related transactions
# Create thematic summary report
```

### 3.2 Agency Pattern Analysis
**Goal:** Which US agencies are most involved?

**Tests:**
- [ ] **Agency Volume Rankings**
  - Top 20 agencies by transaction count
  - Top 20 by total dollar value
  - Compare 101-column (assistance) vs others (contracts)

- [ ] **Agency-Specific Patterns**
  - DoD vs civilian agency patterns
  - Research agencies (NSF, NIH) vs operational
  - Temporal trends by agency

- [ ] **Sub-Agency Drilling**
  - Within DoD: which service branches?
  - Within HHS: which institutes?
  - Identify anomalies

### 3.3 Temporal Trend Analysis
**Goal:** How has China involvement changed over time?

**Tests:**
- [ ] **Time Series Analysis**
  - Monthly/quarterly transaction volume
  - Value trends over time
  - Detection rate changes (improving data quality?)

- [ ] **Event Correlation**
  - Do transactions spike around major events?
  - Policy changes reflected in data?
  - COVID-19 impact visible?

- [ ] **Seasonality**
  - Fiscal year end patterns?
  - Academic calendar patterns (grants)?

---

## 4. ENTITY ANALYSIS

### 4.1 Recipient Profiling
**Goal:** Who are we transacting with?

**Tests:**
- [ ] **Top Recipients Analysis**
  - Top 50 Chinese recipients by transaction count
  - Top 50 by total value
  - Profile each: known entity? State-owned? Private?

- [ ] **Entity Type Classification**
  - Universities vs companies vs government
  - State-owned enterprises vs private
  - Research institutions vs commercial

- [ ] **Geographic Clustering**
  - Beijing vs Shanghai vs Shenzhen patterns
  - Tier 1 vs Tier 2 cities
  - Hong Kong role

### 4.2 Entity Deduplication
**Goal:** Resolve name variations

**Tests:**
- [ ] **Name Normalization**
  - "CHINA TELECOM" = "CHINA TELECOM CORPORATION" = "中国电信"?
  - Build canonical name mapping
  - Apply to create master entity list

- [ ] **Parent-Subsidiary Detection**
  - Identify corporate structures
  - Map subsidiaries to parents
  - Aggregate by corporate group

- [ ] **Cross-Reference with External Data**
  - Match to GLEIF data (if processed)
  - Match to company registries
  - Validate entity identities

### 4.3 Relationship Network Analysis
**Goal:** Understand connections

**Tests:**
- [ ] **Collaboration Networks**
  - Which US entities work with which Chinese entities?
  - Repeat relationships vs one-offs
  - Agency-recipient relationship mapping

- [ ] **Multi-Hop Analysis**
  - US entity → Taiwan entity → China POP
  - Identify intermediary patterns
  - Map indirect China connections

---

## 5. CROSS-FORMAT CONSISTENCY

### 5.1 Overlap Analysis
**Goal:** Understand why same transaction in multiple formats

**Tests:**
- [ ] **Detailed Overlap Investigation**
  - Already know counts, but WHY do they overlap?
  - Are values consistent?
  - Are detection types consistent?
  - Which version is "truth"?

- [ ] **Format-Specific Patterns**
  - What's unique to 101-column (assistance)?
  - What's unique to 305-column?
  - What's unique to 206-column?
  - Document optimal use case for each

### 5.2 Deduplication Strategy
**Goal:** Create unified view

**Tests:**
- [ ] **Master Record Selection**
  - When transaction appears in multiple formats, which to keep?
  - Prefer most complete record
  - Document selection criteria

- [ ] **Unified Dataset Creation**
  - Deduplicated master table
  - ~166K detections → ~[deduplicated count]
  - Preserve format provenance

---

## 6. INTEGRATION WITH OTHER SOURCES

### 6.1 Cross-Source Entity Resolution
**Goal:** Link to patents, grants, etc.

**Tests:**
- [ ] **Patent Linkage**
  - Match USAspending recipients to USPTO patent assignees
  - Identify entities in both datasets
  - Temporal alignment (funding → patents?)

- [ ] **OpenAlex Linkage**
  - Match to research publications
  - Grants → Papers workflow
  - Collaboration patterns

- [ ] **TED Procurement Linkage**
  - EU procurement + US procurement = global picture
  - Same entities in both?

### 6.2 External Validation
**Goal:** Verify against known ground truth

**Tests:**
- [ ] **Known Case Studies**
  - Identify 10 well-documented China-US transactions
  - Are they in our data?
  - If not, why not?

- [ ] **Published Reports**
  - Compare our findings to GAO reports
  - Compare to think tank analyses
  - Validate key statistics match

---

## 7. POLICY COMPLIANCE VERIFICATION

### 7.1 Taiwan Policy Implementation
**Goal:** Verify Option A working correctly

**Tests:**
- [ ] **Taiwan Record Deep Dive**
  - Review all 71 Taiwan records individually
  - Confirm all have China/HK POP
  - Confirm none are name-based only

- [ ] **Taiwan Exclusion Verification**
  - Search for "REPUBLIC OF CHINA" without Taiwan POP
  - Should be 0 results
  - Verify fix is working

### 7.2 NULL Handling Verification
**Goal:** Ensure no data fabrication

**Tests:**
- [ ] **NULL Pattern Analysis**
  - Fields with high NULL rates
  - Consistency of NULL representation
  - No unexpected values appearing

- [ ] **Zero Value Investigation**
  - Why do some transactions have $0 amounts?
  - Are these modifications? Deobligations?
  - Should they be included?

---

## 8. USE CASE VALIDATION

### 8.1 Intelligence Question Testing
**Goal:** Can we answer key questions?

**Sample Questions:**
- [ ] Which US agencies have most China exposure?
- [ ] What technology areas are most active?
- [ ] Which Chinese entities are most active?
- [ ] Has activity increased or decreased over time?
- [ ] What's the total financial exposure?
- [ ] Which transactions represent highest risk?
- [ ] Are there unexpected patterns?

### 8.2 Gap Analysis
**Goal:** What DON'T we know?

**Tests:**
- [ ] **Missing Context**
  - Do we know ultimate use of funds?
  - Do we have outcome data?
  - Classification levels (unclass only?)

- [ ] **Data Limitations**
  - What's not in USAspending data?
  - Black budget items?
  - Classified programs?
  - State/local government transactions?

---

## 9. STATISTICAL VALIDATION

### 9.1 Sanity Checks
**Goal:** Do the numbers make sense?

**Tests:**
- [ ] **Detection Rate Reasonableness**
  - 166K detections / 118M records = 0.14%
  - Is this realistic? Too high? Too low?
  - Compare to known China trade statistics

- [ ] **Value Reasonableness**
  - Total value detected
  - Compare to known US-China economic data
  - Order of magnitude check

- [ ] **Distribution Checks**
  - Does Benford's Law apply?
  - Are values suspiciously round?
  - Anomaly patterns

### 9.2 Comparison Baselines
**Goal:** How do we compare to expectations?

**Tests:**
- [ ] **Other Countries**
  - Run same detection on other countries (UK, Germany, Japan)
  - Is China higher/lower than expected?
  - Normalize by trade volume

- [ ] **Historical Trends**
  - Compare 2015 vs 2020 vs 2024
  - Are trends consistent with policy changes?
  - Major events visible in data?

---

## 10. PRODUCTION VALIDATION

### 10.1 Checkpoint Verification
**Goal:** Did production runs complete correctly?

**Tests:**
- [ ] **Record Count Verification**
  - 101: Processed 57.2M, expected ~57.2M ✓
  - 305: Processed 51.2M, expected ~51.2M ✓
  - 206: Processed 9.6M, expected ~9.6M ✓
  - Total: 117.9M ✓

- [ ] **Detection Count Verification**
  - Compare checkpoint files to database counts
  - Verify all batches saved
  - No data loss during processing

- [ ] **Value Totals**
  - Sum all award_amount values
  - Compare to checkpoint totals
  - Verify no overflow/truncation

### 10.2 Database Integrity
**Goal:** Is database healthy?

**Tests:**
- [ ] **Index Verification**
  - All indexes created?
  - Query performance acceptable?
  - No corruption

- [ ] **Schema Consistency**
  - All expected columns present?
  - Data types correct?
  - Constraints enforced?

---

## PRIORITY EXECUTION ORDER

### Phase 1: Critical Validation (Do First)
1. ✓ Taiwan policy verification
2. ✓ NULL handling verification
3. **Detection accuracy manual review** (100 samples per format)
4. **Top 10 value transactions verification**
5. **Agency volume rankings**

### Phase 2: Understanding (Do Next)
6. **Temporal trend analysis**
7. **Award description topic modeling**
8. **Recipient profiling (Top 50)**
9. **Cross-format deduplication**
10. **Field completeness audit**

### Phase 3: Deep Analysis (Do Later)
11. **Entity deduplication and name normalization**
12. **Network relationship analysis**
13. **Integration with patents/grants**
14. **Statistical distribution analysis**
15. **Use case validation testing**

---

## TOOLS AND SCRIPTS NEEDED

### Immediate Priority:
- `manual_review_sample.py` - Generate random sample for review
- `value_distribution_analyzer.py` - Statistical analysis
- `agency_rankings.py` - Agency volume analysis
- `temporal_trends.py` - Time series analysis
- `topic_modeler.py` - Award description analysis

### Secondary Priority:
- `entity_deduplicator.py` - Name normalization
- `cross_format_deduplicator.py` - Master record creation
- `network_analyzer.py` - Relationship mapping
- `integration_matcher.py` - Cross-source linking
- `comprehensive_report_generator.py` - Final report

---

## SUCCESS CRITERIA

**We have "complete understanding" when:**
1. ✓ Detection accuracy validated (>95% precision)
2. ✓ False negative rate estimated (<5%)
3. ✓ Taiwan policy correctly implemented
4. ✓ NULL handling verified (no fabrication)
5. ✓ Top 50 entities profiled and validated
6. ✓ Temporal trends documented
7. ✓ Agency patterns understood
8. ✓ Technology focus areas identified
9. ✓ Cross-format deduplication complete
10. ✓ Integration strategy with other sources defined
11. ✓ All key intelligence questions answerable
12. ✓ Limitations and gaps documented
13. ✓ Reproducible analysis framework established
14. ✓ Comprehensive report generated

---

## DELIVERABLES

1. **Manual Review Results** (Precision/recall estimates)
2. **Value Distribution Report** (Statistics, outliers, patterns)
3. **Agency Analysis Report** (Rankings, patterns, trends)
4. **Temporal Trends Report** (Time series, events, changes)
5. **Entity Profile Report** (Top recipients, classifications)
6. **Topic Analysis Report** (Technology focus, themes)
7. **Deduplication Report** (Master entity list, deduplicated dataset)
8. **Integration Strategy** (Cross-source linking plan)
9. **Limitations Document** (Known gaps, caveats)
10. **Comprehensive Intelligence Report** (Final synthesis)

---

**Next Step:** Execute Phase 1 critical validation tests to establish confidence in the data foundation.

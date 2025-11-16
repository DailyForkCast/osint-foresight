# OpenAlex V5 - Concurrent Processing + NULL Data Protocol

**Date**: 2025-10-12
**Version**: V5 (Evolution from V4)
**Methodology**: USPTO NULL data handling applied to OpenAlex

---

## Executive Summary

**V5 implements TWO major enhancements beyond V4:**

1. **Concurrent Processing by Date Ranges**: 4 parallel processes, each handling ~126 date directories
2. **NULL Data Protocol**: Captures works that FAILED keyword matching but show other strategic signals

**Expected Results:**
- Processing time: ~2-3 hours (vs 45 minutes for V4's 10K limit)
- Works collected: ~100,000 (vs 12,366 in V4)
- NULL captures: ~10,000-20,000 "uncertain" works for keyword gap analysis
- Coverage: ~50-70% of OpenAlex dataset

---

## Part 1: Concurrent Processing

### How It Works

**Problem V4 Had:**
- Sequential processing of 971 files
- Early termination after 10K works per technology
- Only 7.4% of dataset scanned

**V5 Solution:**
- Split 504 date directories into 4 partitions
- Run 4 parallel processes simultaneously
- Each partition: ~126 directories, ~243 files
- Target: 25,000 works per technology per partition

### Partition Structure

**Partition 1**: `updated_date=2023-05-17` to `updated_date=2024-03-15` (~126 dirs)
**Partition 2**: `updated_date=2024-03-16` to `updated_date=2024-10-22` (~126 dirs)
**Partition 3**: `updated_date=2024-10-23` to `updated_date=2025-04-11` (~126 dirs)
**Partition 4**: `updated_date=2025-04-12` to `updated_date=2025-08-18` (~126 dirs)

### Resource Requirements

**Per Partition:**
- CPU: 1 core at ~80% utilization
- RAM: ~2-4 GB
- Disk I/O: Moderate (reading compressed files)
- Time: ~2-3 hours per partition

**Total System:**
- CPU: 4 cores recommended
- RAM: 8-16 GB total
- Disk: F: drive (OSINT_Backups) for reads, F: drive (OSINT_WAREHOUSE) for writes
- Time: ~2-3 hours (all run in parallel)

### Expected Output

**Per Partition:**
- Works collected: ~25,000 per technology × 9 technologies = ~225,000 works
- NULL captures: ~2,000-5,000 uncertain works
- Log file: `openalex_v4_partition_X.log`

**Combined (All 4 Partitions):**
- Works collected: ~900,000 total (will deduplicate to ~100,000 unique)
- NULL captures: ~10,000-20,000 uncertain works
- Processing time: ~2-3 hours
- Coverage: ~50-70% of OpenAlex dataset

---

## Part 2: NULL Data Protocol

### Concept (USPTO Methodology)

**In USPTO Processing, we captured:**
- Patents with NULL assignee (unassigned IP)
- Patents with NULL inventor location (missing geographic data)
- Patents with NULL CPC codes (unclassified)

**In OpenAlex, we capture:**
- Works that FAILED keyword matching BUT have relevant topics
- Works that PASSED keyword matching BUT failed topic validation
- Works from strategic institutions that failed both validations

This identifies **gaps in our keyword coverage** and **potential false positives**.

### Three NULL Categories

#### Category 1: Keyword FAIL + Topic PASS
**What it captures:**
- Works with relevant OpenAlex topics (e.g., "quantum computing")
- BUT no V4 keyword matches
- **Indicates: Missing keywords in our V4 configuration**

**Example:**
```
Title: "Variational Quantum Eigensolver for Molecular Simulation"
Topics: [quantum algorithm (0.8), computational chemistry (0.6)]
Keywords: NONE matched
NULL Reason: KEYWORD_FAIL_TOPIC_PASS
Action: Consider adding "variational quantum eigensolver" to keywords
```

**Additional Signals Captured:**
- Has Chinese institution? (Yes/No)
- Has strategic funder? (NSF, DOD, NSFC, etc.)
- High citations? (>50 citations)

**Database Table:** `openalex_null_keyword_fails`

#### Category 2: Keyword PASS + Topic FAIL
**What it captures:**
- Works that matched a V4 keyword
- BUT have no relevant OpenAlex topics
- **Indicates: Potential false positives, keyword too broad**

**Example:**
```
Title: "Machine Learning for Predicting Diabetes Risk"
Keywords: "machine learning" (matched AI)
Topics: [medicine (0.9), endocrinology (0.7), public health (0.5)]
NULL Reason: KEYWORD_PASS_TOPIC_FAIL
Action: Consider refining "machine learning" to be more specific
```

**Database Table:** `openalex_null_topic_fails`

#### Category 3: Strategic Institution + Both FAIL
**What it captures:**
- Works from strategic institutions (Tsinghua, MIT, Max Planck, etc.)
- BUT failed both keyword AND topic validation
- **Indicates: Potentially relevant works we're completely missing**

**Example:**
```
Title: "Novel Photonic Integration Techniques for High-Speed Computing"
Institution: MIT
Topics: [optics (0.8), photonics (0.7), computer architecture (0.6)]
Keywords: NONE matched
Topics: NONE matched (not in our 327 patterns)
NULL Reason: STRATEGIC_INSTITUTION_BOTH_FAIL
Action: Consider adding photonics keywords and topics
```

**Database Table:** `openalex_null_strategic_institution`

---

## Part 3: How to Use

### Step 1: Launch Concurrent Processing

```bash
cd "C:\Projects\OSINT - Foresight"
python scripts/integrate_openalex_concurrent.py
```

**What happens:**
1. Script analyzes 504 date directories
2. Partitions into 4 chunks (~126 dirs each)
3. Asks for confirmation
4. Launches 4 background processes
5. Monitors progress every 60 seconds
6. Reports when all complete (~2-3 hours)

### Step 2: Monitor Progress

**Check individual partition logs:**
```bash
tail -f openalex_v4_partition_1.log
tail -f openalex_v4_partition_2.log
tail -f openalex_v4_partition_3.log
tail -f openalex_v4_partition_4.log
```

**Check database counts:**
```bash
python -c "import sqlite3; conn = sqlite3.connect('F:/OSINT_WAREHOUSE/osint_master.db'); print(f'Works: {conn.execute(\"SELECT COUNT(*) FROM openalex_works\").fetchone()[0]:,}'); print(f'NULL Keyword Fails: {conn.execute(\"SELECT COUNT(*) FROM openalex_null_keyword_fails\").fetchone()[0]:,}'); conn.close()"
```

### Step 3: Analyze NULL Data Captures

**Query Category 1: Keyword gaps**
```sql
SELECT technology_domain, COUNT(*) as missing_keyword_count,
       GROUP_CONCAT(DISTINCT matched_topic) as topics_we_missed
FROM openalex_null_keyword_fails
GROUP BY technology_domain
ORDER BY missing_keyword_count DESC;
```

**Query Category 2: False positive keywords**
```sql
SELECT technology_domain, matched_keyword, COUNT(*) as false_positive_count,
       GROUP_CONCAT(DISTINCT actual_topics) as actual_topics_found
FROM openalex_null_topic_fails
GROUP BY technology_domain, matched_keyword
HAVING false_positive_count > 10
ORDER BY false_positive_count DESC;
```

**Query Category 3: Strategic institution gaps**
```sql
SELECT institution_country, institution_name, COUNT(*) as missed_works,
       GROUP_CONCAT(DISTINCT all_topics) as topics_they_publish
FROM openalex_null_strategic_institution
GROUP BY institution_country, institution_name
ORDER BY missed_works DESC
LIMIT 20;
```

### Step 4: Refine Keywords Based on NULL Data

**Example workflow:**

1. Find missing keywords:
```sql
SELECT matched_topic, COUNT(*) as frequency
FROM openalex_null_keyword_fails
WHERE technology_domain = 'Quantum'
GROUP BY matched_topic
ORDER BY frequency DESC
LIMIT 20;
```

2. Review high-frequency topics:
   - "topological quantum" appears 150 times
   - "quantum simulator" appears 120 times
   - "trapped ion" appears 95 times

3. Update `config/openalex_technology_keywords_expanded.json`:
```json
{
  "Quantum": {
    "quantum_hardware": [
      "superconducting qubit",
      "topological qubit",
      "ion trap",
      "trapped ion",          // ADD THIS
      "quantum dot",
      "qubit array",
      "quantum register",
      "quantum simulator"      // ADD THIS
    ]
  }
}
```

4. Run V6 with refined keywords

---

## Part 4: Expected Impact Analysis

### Concurrent Processing Impact

**V4 Results (Baseline):**
- Files processed: 971 (all touched, early termination)
- Works scanned: 40,084,873 (7.4% of dataset)
- Works collected: 12,366
- Time: 45.5 minutes

**V5 Expected (Concurrent + Increased Limits):**
- Files processed: 971 (all fully processed)
- Works scanned: ~270,000,000 (50-70% of dataset)
- Works collected: ~100,000 (before deduplication)
- Works unique: ~80,000-90,000 (after deduplication)
- Time: ~2-3 hours (parallelized)

**Improvement:**
- Works: 6.5-7.3x more than V4
- Coverage: 10x more dataset scanned
- Time: 2.6-4x longer but 10x more coverage

### NULL Data Impact

**Category 1: Keyword Gaps**
- Expected captures: ~5,000-10,000 works
- Value: Identifies missing keywords for V6
- Example: "variational quantum", "neuromorphic", "terahertz"

**Category 2: False Positives**
- Expected captures: ~3,000-7,000 works
- Value: Identifies overly broad keywords
- Example: "machine learning" too broad, captures medical ML

**Category 3: Strategic Institution Gaps**
- Expected captures: ~2,000-5,000 works
- Value: Identifies completely new technology areas
- Example: Photonics integration, spintronics, metamaterials

**Total NULL Captures:** ~10,000-22,000 works for analysis

---

## Part 5: Comparison to V4

| Aspect | V4 | V5 | Change |
|--------|-----|-----|--------|
| **Processing Mode** | Sequential | Concurrent (4 processes) | Parallelized |
| **Works per Technology** | 10,000 | 25,000 per partition | 2.5x |
| **Expected Total Works** | 12,366 | ~80,000-90,000 | 6.5-7.3x |
| **Dataset Coverage** | 7.4% | ~50-70% | 10x |
| **Processing Time** | 45.5 min | ~2-3 hours | 2.6-4x |
| **NULL Captures** | None | ~10,000-22,000 | NEW |
| **Keyword Refinement** | Static | Data-driven from NULL | Iterative |
| **Performance** | 880K works/min | ~1.5-2.25M works/min | 1.7-2.6x |

---

## Part 6: V6 Roadmap (Based on NULL Data)

### After V5 Completes

**Step 1: Analyze NULL Captures** (1-2 hours)
- Query each NULL category
- Identify top 20 missing keywords per technology
- Identify top 10 overly broad keywords

**Step 2: Refine Configurations** (1 hour)
- Update `config/openalex_technology_keywords_expanded.json`
- Add missing keywords from Category 1
- Refine broad keywords from Category 2
- Add new technology areas from Category 3

**Step 3: Run V6 with Refined Keywords** (2-3 hours)
- Same concurrent processing
- Updated keywords (expected: 400-450 keywords)
- Expected: +15-25% more relevant works
- Fewer false positives

### V6 Expected Improvements

**Keyword Expansion:**
- V5: 355 keywords
- V6: 400-450 keywords (data-driven additions)
- Improvement: +12-27% keyword coverage

**Quality Improvements:**
- Reduced false positive rate (from Category 2 analysis)
- Increased true positive rate (from Category 1 additions)
- Better strategic coverage (from Category 3)

**Expected V6 Results:**
- Works collected: ~95,000-110,000
- False positive reduction: 80%+ (vs 75.4% in V4)
- Keyword gap reduction: -60% (vs V5)

---

## Part 7: Technical Implementation

### Concurrent Architecture

```
┌─────────────────────────────────────────────────┐
│     integrate_openalex_concurrent.py            │
│     (Main Launcher)                             │
└─────────────────┬───────────────────────────────┘
                  │
                  ├─→ Worker 1: Partition 1 (2023-05 to 2024-03)
                  ├─→ Worker 2: Partition 2 (2024-03 to 2024-10)
                  ├─→ Worker 3: Partition 3 (2024-10 to 2025-04)
                  └─→ Worker 4: Partition 4 (2025-04 to 2025-08)
                       │
                       ├─→ Process files in partition
                       ├─→ Validate works (4-stage)
                       ├─→ Capture NULL data
                       └─→ Insert to master DB
```

### Database Schema (NEW TABLES)

```sql
-- Category 1: Keyword fails, topic passes
CREATE TABLE openalex_null_keyword_fails (
    work_id TEXT PRIMARY KEY,
    doi TEXT,
    title TEXT,
    publication_year INTEGER,
    cited_by_count INTEGER,
    abstract TEXT,
    technology_domain TEXT,
    null_reason TEXT,                -- KEYWORD_FAIL_TOPIC_PASS
    matched_topic TEXT,              -- What topic DID match
    topic_score REAL,
    has_chinese_institution BOOLEAN, -- Additional signal
    has_strategic_funder BOOLEAN,    -- Additional signal
    high_citations BOOLEAN,          -- Additional signal
    created_date TEXT
);

-- Category 2: Keyword passes, topic fails
CREATE TABLE openalex_null_topic_fails (
    work_id TEXT PRIMARY KEY,
    doi TEXT,
    title TEXT,
    publication_year INTEGER,
    cited_by_count INTEGER,
    abstract TEXT,
    technology_domain TEXT,
    matched_keyword TEXT,    -- Which keyword matched
    actual_topics TEXT,      -- What topics it actually has
    created_date TEXT
);

-- Category 3: Strategic institution, both fail
CREATE TABLE openalex_null_strategic_institution (
    work_id TEXT PRIMARY KEY,
    doi TEXT,
    title TEXT,
    publication_year INTEGER,
    institution_id TEXT,
    institution_name TEXT,
    institution_country TEXT,
    abstract TEXT,
    all_topics TEXT,        -- What topics does strategic inst publish?
    created_date TEXT
);
```

---

## Part 8: Success Criteria

### V5 Success Criteria

1. **All 4 partitions complete** without errors
2. **Works collected:** >80,000 unique works
3. **NULL captures:** >10,000 total across all categories
4. **Processing time:** <4 hours total
5. **Database integrity:** No corrupted records
6. **Coverage:** >50% of OpenAlex dataset scanned

### V5 Quality Metrics

1. **False positive rate:** <25% (vs 24.6% in V4)
2. **Deduplication rate:** ~10-15% (expected overlap between partitions)
3. **NULL Category 1 captures:** >3,000 (keyword gaps)
4. **NULL Category 2 captures:** >2,000 (false positive candidates)
5. **NULL Category 3 captures:** >1,000 (strategic institution gaps)

---

## Part 9: Limitations and Risks

### Limitations

1. **No deduplication between partitions** during processing
   - Works may be captured multiple times across partitions
   - Deduplication happens post-processing via `work_id PRIMARY KEY`
   - Expected: ~10-15% duplication rate

2. **Higher disk I/O and database contention**
   - 4 processes writing to same database
   - WAL mode mitigates but doesn't eliminate locks
   - Occasional write delays expected

3. **NULL data requires manual review**
   - Automated capture but human analysis needed
   - Not all NULL captures are true gaps
   - Requires domain expertise to interpret

### Risks

**Low Risk:**
- Database corruption (WAL mode protects)
- Process failures (each partition independent)
- Missing data (PRIMARY KEY constraints prevent duplicates)

**Medium Risk:**
- Excessive processing time (may take >4 hours on slower systems)
- Database lock contention (4 concurrent writers)
- NULL data false positives (not all gaps are meaningful)

**Mitigation:**
- Monitor each partition log independently
- Can restart failed partitions individually
- NULL data is separate tables, doesn't affect main collection

---

## Part 10: Commands Quick Reference

### Launch Concurrent Processing
```bash
cd "C:\Projects\OSINT - Foresight"
python scripts/integrate_openalex_concurrent.py
```

### Monitor Progress
```bash
# Watch all partition logs
tail -f openalex_v4_partition_*.log

# Check database counts
python -c "import sqlite3; conn = sqlite3.connect('F:/OSINT_WAREHOUSE/osint_master.db'); print(f'Works: {conn.execute(\"SELECT COUNT(*) FROM openalex_works\").fetchone()[0]:,}'); conn.close()"
```

### Analyze NULL Data
```bash
# Connect to database
sqlite3 "F:/OSINT_WAREHOUSE/osint_master.db"

# Query keyword gaps
SELECT technology_domain, COUNT(*) FROM openalex_null_keyword_fails GROUP BY technology_domain;

# Query false positives
SELECT technology_domain, matched_keyword, COUNT(*) FROM openalex_null_topic_fails GROUP BY technology_domain, matched_keyword ORDER BY COUNT(*) DESC LIMIT 20;

# Query strategic institution gaps
SELECT institution_name, COUNT(*) FROM openalex_null_strategic_institution GROUP BY institution_name ORDER BY COUNT(*) DESC LIMIT 20;
```

---

## Conclusion

**V5 represents a major evolution in the OpenAlex processing methodology:**

1. **Concurrent Processing:** 4x parallelization, 10x dataset coverage
2. **NULL Data Protocol:** USPTO methodology applied, captures 10K-22K "uncertain" works
3. **Increased Limits:** 25K per tech per partition = ~100K total works
4. **Data-Driven Refinement:** V6 will use NULL data to improve keywords

**Expected Results:**
- Works: ~80,000-90,000 (6.5-7.3x improvement over V4)
- Coverage: 50-70% of OpenAlex (vs 7.4% in V4)
- NULL Captures: ~10,000-22,000 for keyword gap analysis
- Processing Time: 2-3 hours (parallelized)

**The USPTO NULL data methodology enables continuous improvement of our keyword configuration based on actual gaps in coverage.**

---

**Status**: Ready to launch
**Next Step**: Run `python scripts/integrate_openalex_concurrent.py`
**Expected Completion**: 2-3 hours from launch

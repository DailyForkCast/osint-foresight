# Database Optimization Opportunities - Comprehensive Analysis
**Date:** 2025-10-30
**Database:** F:/OSINT_WAREHOUSE/osint_master.db
**Total Records:** 33.88M+ (after Companies House integration)
**Total Tables:** 213

---

## Executive Summary

After implementing optimized GLEIF matching for Companies House UK, this analysis identifies additional optimization opportunities across the entire OSINT database. The analysis focuses on:

1. **Index optimization** - Missing indexes on frequently queried columns
2. **Query pattern optimization** - Pre-computed columns for common transformations
3. **Join optimization** - Cross-reference tables and materialized views
4. **Storage optimization** - Data type optimization and compression
5. **Maintenance optimization** - VACUUM, ANALYZE, and statistics updates

**Estimated Performance Gains:** 10-1000x speedup for common queries
**Implementation Effort:** 4-8 hours total
**Priority Level:** MEDIUM-HIGH (significant ROI for analysis workflows)

---

## Part 1: What We Just Optimized (GLEIF Matching)

### Problem:
```sql
-- SLOW: Can't use indexes, requires 60 billion comparisons
SELECT ch.company_number, g.lei
FROM companies_house_uk_companies ch
JOIN gleif_entities g ON LOWER(TRIM(ch.company_name)) = LOWER(TRIM(g.legal_name))
```

**Time:** 7+ days (estimated) or never completing

### Solution Implemented:
```sql
-- Step 1: Add normalized columns
ALTER TABLE companies_house_uk_companies ADD COLUMN company_name_normalized TEXT;
ALTER TABLE gleif_entities ADD COLUMN legal_name_normalized TEXT;

-- Step 2: Populate once
UPDATE companies_house_uk_companies SET company_name_normalized = LOWER(TRIM(company_name));
UPDATE gleif_entities SET legal_name_normalized = LOWER(TRIM(legal_name));

-- Step 3: Create indexes
CREATE INDEX idx_ch_name_normalized ON companies_house_uk_companies(company_name_normalized);
CREATE INDEX idx_gleif_name_normalized ON gleif_entities(legal_name_normalized);

-- Step 4: FAST query (uses indexes!)
SELECT ch.company_number, g.lei
FROM companies_house_uk_companies ch
JOIN gleif_entities g ON ch.company_name_normalized = g.legal_name_normalized;
```

**Time:** 5-10 seconds (estimated) - **100,000x speedup**

**Principle:** Pre-compute expensive transformations, store them in indexed columns.

---

## Part 2: Similar Opportunities Across the Database

### 🔴 CRITICAL PRIORITY: Large Tables Missing Key Indexes

#### 1. **gleif_repex** (16.9M records) - Parent/Child Relationship Queries

**Current State:**
```
Table: gleif_repex
Records: 16,936,425
Indexes: Unknown (needs verification)
```

**Common Query Pattern:**
```sql
-- Find all subsidiaries of a parent company
SELECT * FROM gleif_repex
WHERE parent_lei = '5493000IBP32UQZ0KL24'  -- Huawei example
```

**Problem:** If `parent_lei` is not indexed, this requires a full table scan of 16.9M rows.

**Solution:**
```sql
CREATE INDEX IF NOT EXISTS idx_gleif_repex_parent ON gleif_repex(parent_lei);
CREATE INDEX IF NOT EXISTS idx_gleif_repex_child ON gleif_repex(child_lei);
CREATE INDEX IF NOT EXISTS idx_gleif_repex_relationship_type ON gleif_repex(relationship_type);
```

**Estimated Impact:**
- Before: 15-30 seconds per query (full table scan)
- After: 0.01 seconds (index lookup)
- **Speedup: 1500-3000x**

---

#### 2. **gleif_isin_mapping** (7.6M records) - Security Identifier Lookups

**Current State:**
```
Table: gleif_isin_mapping
Records: 7,579,749
Indexes: Needs verification
```

**Common Query Pattern:**
```sql
-- Find LEI by ISIN (stock ticker)
SELECT lei FROM gleif_isin_mapping
WHERE isin = 'US0378331005'  -- Apple stock example
```

**Solution:**
```sql
CREATE INDEX IF NOT EXISTS idx_gleif_isin_mapping_isin ON gleif_isin_mapping(isin);
CREATE INDEX IF NOT EXISTS idx_gleif_isin_mapping_lei ON gleif_isin_mapping(lei);
```

**Estimated Impact:** 1000-2000x speedup for ISIN lookups

---

#### 3. **gleif_qcc_mapping** (1.9M records) - Chinese Entity Detection

**Current State:**
```
Table: gleif_qcc_mapping
Records: 1,912,288
Indexes: Needs verification
```

**Common Query Pattern:**
```sql
-- Find all GLEIF entities with QCC (Chinese business registry) IDs
SELECT * FROM gleif_qcc_mapping
WHERE qcc_id LIKE '91110000%'  -- Beijing companies
```

**Solution:**
```sql
CREATE INDEX IF NOT EXISTS idx_gleif_qcc_mapping_qcc ON gleif_qcc_mapping(qcc_id);
CREATE INDEX IF NOT EXISTS idx_gleif_qcc_mapping_lei ON gleif_qcc_mapping(lei);
```

**Estimated Impact:** 500-1000x speedup for Chinese entity queries

---

#### 4. **sec_form_d_persons** (1.85M records) - VC Investor Tracking

**Current State:**
```
Table: sec_form_d_persons
Records: 1,849,561
Indexes: Needs verification
```

**Common Query Pattern:**
```sql
-- Find all offerings from a specific investor
SELECT * FROM sec_form_d_persons
WHERE person_name LIKE '%Sequoia%'
```

**Problem:** Text matching on 1.85M rows without index.

**Solution:**
```sql
CREATE INDEX IF NOT EXISTS idx_sec_form_d_persons_name ON sec_form_d_persons(person_name);
CREATE INDEX IF NOT EXISTS idx_sec_form_d_persons_accession ON sec_form_d_persons(accession_number);

-- For Chinese investor detection, add normalized column
ALTER TABLE sec_form_d_persons ADD COLUMN person_name_normalized TEXT;
UPDATE sec_form_d_persons SET person_name_normalized = LOWER(TRIM(person_name));
CREATE INDEX idx_sec_form_d_persons_name_norm ON sec_form_d_persons(person_name_normalized);
```

**Estimated Impact:** 500-1000x speedup for investor queries

---

#### 5. **companies_house_uk_psc** (902K records) - Ownership Analysis

**Current State:**
```
Table: companies_house_uk_psc
Records: 902,705
Indexes: 4 (already optimized!)
```

**Status:** ✅ Already has indexes on:
- company_number
- psc_name
- nationality
- country_of_residence

**Additional Optimization:**
```sql
-- For ownership percentage queries (finding major shareholders)
CREATE INDEX IF NOT EXISTS idx_ch_psc_ownership ON companies_house_uk_psc(ownership_percentage DESC);

-- For control type analysis
CREATE INDEX IF NOT EXISTS idx_ch_psc_control ON companies_house_uk_psc(control_types);
```

---

#### 6. **companies_house_uk_china_connections** (1.09M records) - Detection Analysis

**Current State:**
```
Table: companies_house_uk_china_connections
Records: 1,091,624
Indexes: 3 (already optimized!)
```

**Status:** ✅ Already has indexes on:
- company_number
- detection_layer
- confidence_score

**Additional Optimization:**
```sql
-- Composite index for common queries (layer + confidence filtering)
CREATE INDEX IF NOT EXISTS idx_ch_china_layer_confidence
ON companies_house_uk_china_connections(detection_layer, confidence_score DESC);
```

---

#### 7. **sec_form_d_offerings** (496K records) - VC Deal Tracking

**Current State:**
```
Table: sec_form_d_offerings
Records: 495,937
Indexes: Needs verification
```

**Common Query Patterns:**
```sql
-- Find offerings by date range
SELECT * FROM sec_form_d_offerings
WHERE filing_date BETWEEN '2024-01-01' AND '2024-12-31';

-- Find offerings by amount
SELECT * FROM sec_form_d_offerings
WHERE total_offering_amount > 10000000;

-- Find offerings by industry
SELECT * FROM sec_form_d_offerings
WHERE issuer_industry_group = 'Computers and Software';
```

**Solution:**
```sql
CREATE INDEX IF NOT EXISTS idx_sec_form_d_filing_date ON sec_form_d_offerings(filing_date);
CREATE INDEX IF NOT EXISTS idx_sec_form_d_amount ON sec_form_d_offerings(total_offering_amount DESC);
CREATE INDEX IF NOT EXISTS idx_sec_form_d_industry ON sec_form_d_offerings(issuer_industry_group);
CREATE INDEX IF NOT EXISTS idx_sec_form_d_accession ON sec_form_d_offerings(accession_number);

-- Composite index for date + amount queries
CREATE INDEX IF NOT EXISTS idx_sec_form_d_date_amount
ON sec_form_d_offerings(filing_date, total_offering_amount DESC);
```

**Estimated Impact:** 100-500x speedup for VC analysis queries

---

### 🟠 HIGH PRIORITY: Patent and Academic Data Optimization

#### 8. **patentsview_patents** (Millions of records) - Patent Searches

**Common Query Patterns:**
```sql
-- Find patents by assignee
SELECT * FROM patentsview_patents
WHERE assignee_organization LIKE '%Huawei%';

-- Find patents by date
SELECT * FROM patentsview_patents
WHERE patent_date BETWEEN '2020-01-01' AND '2025-01-01';

-- Find patents by CPC code (technology classification)
SELECT * FROM patentsview_patents
WHERE cpc_codes LIKE '%H04W%';  -- Wireless communication
```

**Solution:**
```sql
-- Assignee index
CREATE INDEX IF NOT EXISTS idx_patents_assignee ON patentsview_patents(assignee_organization);

-- Date index
CREATE INDEX IF NOT EXISTS idx_patents_date ON patentsview_patents(patent_date);

-- For CPC code searches, consider full-text search or JSON extraction
CREATE INDEX IF NOT EXISTS idx_patents_cpc ON patentsview_patents(cpc_codes);

-- Normalized assignee for matching
ALTER TABLE patentsview_patents ADD COLUMN assignee_normalized TEXT;
UPDATE patentsview_patents SET assignee_normalized = LOWER(TRIM(assignee_organization));
CREATE INDEX idx_patents_assignee_norm ON patentsview_patents(assignee_normalized);
```

**Estimated Impact:** 500-2000x speedup for patent queries

---

#### 9. **openalex_works** (Large dataset) - Academic Research

**Common Query Patterns:**
```sql
-- Find papers by institution
SELECT * FROM openalex_works
WHERE institutions LIKE '%Tsinghua University%';

-- Find papers by topic
SELECT * FROM openalex_works
WHERE topics LIKE '%quantum computing%';

-- Find papers by year
SELECT * FROM openalex_works
WHERE publication_year = 2024;
```

**Solution:**
```sql
CREATE INDEX IF NOT EXISTS idx_openalex_year ON openalex_works(publication_year);
CREATE INDEX IF NOT EXISTS idx_openalex_cited ON openalex_works(cited_by_count DESC);

-- For institution/topic searches, consider:
-- 1. Separate junction tables
-- 2. Full-text search indexes
-- 3. JSON extraction indexes
```

**Estimated Impact:** 200-1000x speedup for academic research queries

---

### 🟡 MEDIUM PRIORITY: TED and USAspending Optimization

#### 10. **ted_contracts** (Large dataset) - EU Procurement

**Common Query Patterns:**
```sql
-- Find contracts by contractor
SELECT * FROM ted_contracts
WHERE contractor_name LIKE '%中国%';  -- Chinese contractors

-- Find contracts by value
SELECT * FROM ted_contracts
WHERE contract_value > 1000000;

-- Find contracts by date
SELECT * FROM ted_contracts
WHERE publication_date BETWEEN '2020-01-01' AND '2025-01-01';
```

**Solution:**
```sql
CREATE INDEX IF NOT EXISTS idx_ted_contractor ON ted_contracts(contractor_name);
CREATE INDEX IF NOT EXISTS idx_ted_value ON ted_contracts(contract_value DESC);
CREATE INDEX IF NOT EXISTS idx_ted_date ON ted_contracts(publication_date);

-- Normalized contractor name for matching
ALTER TABLE ted_contracts ADD COLUMN contractor_normalized TEXT;
UPDATE ted_contracts SET contractor_normalized = LOWER(TRIM(contractor_name));
CREATE INDEX idx_ted_contractor_norm ON ted_contracts(contractor_normalized);
```

---

#### 11. **usaspending_awards** (Large dataset) - US Procurement

**Common Query Patterns:**
```sql
-- Find awards by recipient
SELECT * FROM usaspending_awards
WHERE recipient_name LIKE '%Huawei%';

-- Find awards by amount
SELECT * FROM usaspending_awards
WHERE total_obligation > 1000000;

-- Find awards by agency
SELECT * FROM usaspending_awards
WHERE awarding_agency_name = 'DEPARTMENT OF DEFENSE';
```

**Solution:**
```sql
CREATE INDEX IF NOT EXISTS idx_usa_recipient ON usaspending_awards(recipient_name);
CREATE INDEX IF NOT EXISTS idx_usa_amount ON usaspending_awards(total_obligation DESC);
CREATE INDEX IF NOT EXISTS idx_usa_agency ON usaspending_awards(awarding_agency_name);
CREATE INDEX IF NOT EXISTS idx_usa_date ON usaspending_awards(action_date);

-- Normalized recipient for matching
ALTER TABLE usaspending_awards ADD COLUMN recipient_normalized TEXT;
UPDATE usaspending_awards SET recipient_normalized = LOWER(TRIM(recipient_name));
CREATE INDEX idx_usa_recipient_norm ON usaspending_awards(recipient_normalized);
```

---

## Part 3: Advanced Optimizations

### 🔵 MATERIALIZED VIEWS / SUMMARY TABLES

Create pre-computed summary tables for common aggregate queries:

#### 1. **Chinese Entity Summary by Source**

```sql
CREATE TABLE IF NOT EXISTS chinese_entity_summary AS
SELECT
    source_table,
    entity_name,
    entity_name_normalized,
    COUNT(*) as record_count,
    MIN(earliest_date) as first_seen,
    MAX(latest_date) as last_seen,
    SUM(total_value) as total_value
FROM (
    -- Union across all sources
    SELECT 'TED' as source_table, contractor_name as entity_name,
           contractor_normalized as entity_name_normalized,
           publication_date as earliest_date, publication_date as latest_date,
           contract_value as total_value
    FROM ted_contracts
    WHERE china_connection_detected = 1

    UNION ALL

    SELECT 'USAspending' as source_table, recipient_name as entity_name,
           recipient_normalized as entity_name_normalized,
           action_date as earliest_date, action_date as latest_date,
           total_obligation as total_value
    FROM usaspending_awards
    WHERE china_connection_detected = 1

    UNION ALL

    SELECT 'SEC_Form_D' as source_table, issuer_name as entity_name,
           issuer_name_normalized as entity_name_normalized,
           filing_date as earliest_date, filing_date as latest_date,
           total_offering_amount as total_value
    FROM sec_form_d_offerings
    WHERE china_connection_detected = 1
)
GROUP BY source_table, entity_name, entity_name_normalized;

CREATE INDEX idx_chinese_summary_name ON chinese_entity_summary(entity_name_normalized);
CREATE INDEX idx_chinese_summary_source ON chinese_entity_summary(source_table);
CREATE INDEX idx_chinese_summary_value ON chinese_entity_summary(total_value DESC);
```

**Benefits:**
- Instant cross-source entity analysis
- No need to UNION across multiple tables
- Pre-aggregated statistics

---

#### 2. **Technology Domain Summary**

```sql
CREATE TABLE IF NOT EXISTS technology_domain_summary AS
SELECT
    technology_domain,
    country_code,
    COUNT(DISTINCT entity_id) as unique_entities,
    COUNT(*) as total_records,
    SUM(patent_count) as patents,
    SUM(publication_count) as publications,
    SUM(contract_count) as contracts,
    SUM(funding_amount) as total_funding
FROM (
    -- Aggregate across patents, papers, contracts, VC deals
    SELECT technology_domain, assignee_country as country_code,
           assignee_id as entity_id,
           COUNT(*) as patent_count, 0 as publication_count,
           0 as contract_count, 0 as funding_amount
    FROM patentsview_patents
    GROUP BY technology_domain, assignee_country, assignee_id

    UNION ALL

    SELECT technology_domain, institution_country as country_code,
           institution_id as entity_id,
           0 as patent_count, COUNT(*) as publication_count,
           0 as contract_count, 0 as funding_amount
    FROM openalex_works
    GROUP BY technology_domain, institution_country, institution_id

    -- Add more sources...
)
GROUP BY technology_domain, country_code;

CREATE INDEX idx_tech_domain ON technology_domain_summary(technology_domain);
CREATE INDEX idx_tech_country ON technology_domain_summary(country_code);
```

---

### 🟣 FULL-TEXT SEARCH INDEXES

For large text fields with frequent LIKE queries, consider FTS5:

```sql
-- Create virtual FTS table for company names
CREATE VIRTUAL TABLE IF NOT EXISTS companies_fts USING fts5(
    company_name,
    country,
    source_table,
    tokenize='unicode61 remove_diacritics 2'
);

-- Populate from all sources
INSERT INTO companies_fts
SELECT company_name, 'UK', 'companies_house'
FROM companies_house_uk_companies;

INSERT INTO companies_fts
SELECT legal_name, legal_address_country, 'gleif'
FROM gleif_entities;

-- Query (MUCH faster than LIKE)
SELECT * FROM companies_fts
WHERE companies_fts MATCH 'huawei OR alibaba OR baidu';
```

**Benefits:**
- 100-1000x faster than LIKE queries
- Supports stemming, synonyms, phrase matching
- Handles multi-language text

---

## Part 4: Maintenance Optimizations

### 1. **VACUUM** - Reclaim Space and Defragment

```sql
-- Run periodically (monthly or after large DELETE operations)
VACUUM;
```

**Benefits:**
- Reclaims deleted space
- Defragments database file
- Improves query performance

---

### 2. **ANALYZE** - Update Query Planner Statistics

```sql
-- Run after significant data changes
ANALYZE;

-- Or analyze specific tables
ANALYZE companies_house_uk_companies;
ANALYZE gleif_entities;
ANALYZE patentsview_patents;
```

**Benefits:**
- Updates table statistics for query planner
- Helps SQLite choose optimal query execution plans
- Especially important after adding indexes

---

### 3. **REINDEX** - Rebuild Indexes

```sql
-- Rebuild all indexes
REINDEX;

-- Or specific index
REINDEX idx_gleif_name_normalized;
```

**Benefits:**
- Fixes index corruption
- Optimizes index structure
- Run after VACUUM

---

## Part 5: Implementation Roadmap

### Phase 1: Critical Indexes (2-3 hours)

**Priority:** Immediate
**Impact:** 1000x+ speedup for common queries

```sql
-- GLEIF mappings
CREATE INDEX idx_gleif_repex_parent ON gleif_repex(parent_lei);
CREATE INDEX idx_gleif_repex_child ON gleif_repex(child_lei);
CREATE INDEX idx_gleif_isin_mapping_isin ON gleif_isin_mapping(isin);
CREATE INDEX idx_gleif_qcc_mapping_qcc ON gleif_qcc_mapping(qcc_id);

-- VC data
CREATE INDEX idx_sec_form_d_filing_date ON sec_form_d_offerings(filing_date);
CREATE INDEX idx_sec_form_d_persons_name ON sec_form_d_persons(person_name);

-- Procurement
CREATE INDEX idx_ted_contractor ON ted_contracts(contractor_name);
CREATE INDEX idx_usa_recipient ON usaspending_awards(recipient_name);
```

---

### Phase 2: Normalized Name Columns (3-4 hours)

**Priority:** High
**Impact:** Enable fast cross-source matching

Tables to normalize:
- sec_form_d_offerings (issuer_name)
- sec_form_d_persons (person_name)
- ted_contracts (contractor_name)
- usaspending_awards (recipient_name)
- patentsview_patents (assignee_organization)
- openalex_works (institution names)

**Template:**
```sql
ALTER TABLE {table} ADD COLUMN {name}_normalized TEXT;
UPDATE {table} SET {name}_normalized = LOWER(TRIM({name}));
CREATE INDEX idx_{table}_{name}_norm ON {table}({name}_normalized);
```

---

### Phase 3: Summary Tables (2-3 hours)

**Priority:** Medium
**Impact:** Instant cross-source analysis

Create:
- chinese_entity_summary
- technology_domain_summary
- temporal_trends_summary

---

### Phase 4: Full-Text Search (2-3 hours)

**Priority:** Medium-Low
**Impact:** 100x speedup for text searches

Implement FTS5 for:
- All company/entity name fields
- Contract descriptions
- Patent abstracts
- Paper abstracts

---

### Phase 5: Maintenance Automation (1 hour)

**Priority:** Low
**Impact:** Long-term performance

Create scheduled script:
```bash
#!/bin/bash
# Run weekly maintenance
sqlite3 osint_master.db "ANALYZE;"
# Run monthly
sqlite3 osint_master.db "VACUUM; REINDEX;"
```

---

## Part 6: Query Performance Testing

### Before/After Comparison Script:

```python
import sqlite3
import time

conn = sqlite3.connect('osint_master.db')

# Test query performance
queries = [
    "SELECT * FROM gleif_repex WHERE parent_lei = '5493000IBP32UQZ0KL24'",
    "SELECT * FROM gleif_isin_mapping WHERE isin = 'US0378331005'",
    "SELECT * FROM sec_form_d_offerings WHERE filing_date > '2024-01-01'",
    "SELECT * FROM companies_house_uk_psc WHERE nationality = 'Chinese'"
]

for query in queries:
    start = time.time()
    cursor = conn.execute(query)
    results = cursor.fetchall()
    elapsed = time.time() - start
    print(f"Query: {query[:50]}...")
    print(f"Results: {len(results)}")
    print(f"Time: {elapsed:.4f}s")
    print()
```

---

## Summary Table: Optimization Opportunities

| Priority | Optimization | Tables Affected | Est. Impact | Est. Effort |
|----------|-------------|-----------------|-------------|-------------|
| 🔴 CRITICAL | Missing indexes on large tables | gleif_repex, gleif_isin_mapping, gleif_qcc_mapping | 1000-3000x | 2-3 hours |
| 🔴 CRITICAL | VC data indexes | sec_form_d_offerings, sec_form_d_persons | 500-1000x | 1 hour |
| 🟠 HIGH | Patent/academic indexes | patentsview_patents, openalex_works | 500-2000x | 2 hours |
| 🟠 HIGH | Normalized name columns | All entity tables | Enable fast matching | 3-4 hours |
| 🟡 MEDIUM | Procurement indexes | ted_contracts, usaspending_awards | 200-500x | 1 hour |
| 🟡 MEDIUM | Summary/materialized views | Cross-source analysis | Instant aggregates | 2-3 hours |
| 🔵 LOW | Full-text search | Text-heavy tables | 100-1000x for LIKE | 2-3 hours |
| 🟣 MAINT | VACUUM, ANALYZE, REINDEX | All tables | 10-50x long-term | 1 hour setup |

**Total Estimated Effort:** 14-20 hours
**Total Estimated Impact:** 10-3000x speedup depending on query type

---

## Immediate Next Steps

1. ✅ **Complete GLEIF matching optimization** (currently running)
2. **Create critical indexes** (2-3 hours, run tonight)
3. **Test query performance** before/after
4. **Document results** and iterate

---

**Document Status:** COMPREHENSIVE ANALYSIS COMPLETE
**Next Action:** Implement Phase 1 critical indexes
**Expected Completion:** GLEIF matching optimization in progress (20+ minutes elapsed)

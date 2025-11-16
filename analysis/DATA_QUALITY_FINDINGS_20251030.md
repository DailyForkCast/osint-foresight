# Critical Data Quality Findings - Database Consolidation QA/QC
**Date**: October 30, 2025
**Audit Trigger**: Post-consolidation comprehensive QA/QC audit
**Status**: 🔴 **CRITICAL ISSUES FOUND**

---

## Executive Summary

Comprehensive QA/QC audit discovered **critical data quality issues** in both OpenAIRE and OpenSanctions datasets merged into the master database. The merge scripts used a "common columns only" approach that resulted in significant data loss.

**Severity**: CRITICAL - Production readiness BLOCKED
**Impact**: 67% of OpenAIRE fields NULL, 50% of OpenSanctions fields NULL
**Root Cause**: Schema mismatch between source and target databases, incomplete column mapping
**Action Required**: Re-merge with corrected mapping scripts

---

## Issue 1: OpenAIRE Research Products - Critical Field Loss

### Data Quality Status
- **Total Records**: 156,221
- **Fields Populated**: 3 out of 9 (33%)
- **Fields NULL**: 6 out of 9 (67%)
- **Usability**: ❌ UNUSABLE for analysis

### NULL Analysis
```
Field                 NULL Count    NULL %    Status      Impact
==================   ==========  ========  =========  =========================
id                            0      0.0%  ✓ OK       Primary key intact
title                         0      0.0%  ✓ OK       Research product name
created_at                    0      0.0%  ✓ OK       Merge timestamp
authors               156,221    100.0%  ✗ CRITICAL Cannot identify researchers
organizations         156,221    100.0%  ✗ CRITICAL Cannot filter by institution
countries             156,221    100.0%  ✗ CRITICAL Cannot do country analysis
year                  156,221    100.0%  ✗ CRITICAL Cannot do temporal analysis
type                  156,221    100.0%  ✗ CRITICAL Cannot categorize research
china_related         156,221    100.0%  ✗ CRITICAL Cannot detect China links
```

### Root Cause Analysis

**Schema Mismatch:**

Source database (`openaire_production.db - research_products`):
```
id                INTEGER     ✓ Available
country_code      TEXT        ✓ Available  → Should map to "countries"
title             TEXT        ✓ Available  ✓ Mapped correctly
date_accepted     TEXT        ✓ Available  → Should map to "year"
result_type       TEXT        ✓ Available  → Should map to "type"
doi               TEXT        ✓ Available  (not used in target)
processing_batch  INTEGER     ✓ Available  (not used in target)
has_collaboration BOOLEAN     ✓ Available  (not used in target)
raw_data          TEXT        ✓ Available  → Could parse for authors, orgs
```

Target database (`osint_master.db - openaire_research`):
```
id                TEXT        ✓ Common field (copied)
title             TEXT        ✓ Common field (copied)
authors           TEXT        ✗ No source equivalent
organizations     TEXT        ✗ No source equivalent
countries         TEXT        ✗ NOT MAPPED (source has country_code)
year              INTEGER     ✗ NOT MAPPED (source has date_accepted)
type              TEXT        ✗ NOT MAPPED (source has result_type)
china_related     BOOLEAN     ✗ Requires calculation logic
created_at        TIMESTAMP   ✓ Auto-generated
```

**Merge Script Behavior:**
- Line 126: `common_cols = set(source_cols.keys()) & set(target_cols.keys())`
- Only copies columns with **exact name match** in both databases
- Result: Only "id" and "title" matched, all other fields NULL

### Impact Assessment
- ❌ Cannot perform China-related analysis (primary use case)
- ❌ Cannot filter by country (critical requirement)
- ❌ Cannot perform temporal trends (year field empty)
- ❌ Cannot categorize by research type
- ❌ Cannot identify collaborating institutions
- ✅ Can only see research titles (minimal value)

**Production Impact**: OpenAIRE data is effectively **unusable** for intended analysis purposes.

---

## Issue 2: OpenSanctions Entities - Partial Field Loss

### Data Quality Status
- **Total Records**: 183,766 (after duplicate cleanup)
- **Fields Populated**: 5 out of 10 (50%)
- **Fields NULL**: 5 out of 10 (50%)
- **Usability**: ⚠️ PARTIALLY USABLE but missing critical fields

### NULL Analysis
```
Field                 NULL Count    NULL %    Status      Impact
==================   ==========  ========  =========  =========================
entity_id                     0      0.0%  ✓ OK       Primary key intact
entity_name                   0      0.0%  ✓ OK       Entity identification
entity_type                   0      0.0%  ✓ OK       Entity classification
china_related                 0      0.0%  ✓ OK       Chinese affiliation flag
created_at                    0      0.0%  ✓ OK       Merge timestamp
countries                66,686     36.3%  ⚠️ WARN    Country data 64% complete
sanction_programs       183,766    100.0%  ✗ CRITICAL Cannot identify sanctions
aliases                 183,766    100.0%  ✗ CRITICAL Cannot match alternate names
birth_date              183,766    100.0%  ⚠️ WARN    Biographical data missing
risk_score              183,766    100.0%  ⚠️ WARN    Risk assessment missing
```

### Root Cause Analysis

**Schema Mismatch:**

Source database (`sanctions.db - entities`):
```
id                     TEXT    ✓ Available  → Mapped to entity_id (v2)
name                   TEXT    ✓ Available  → Mapped to entity_name (v2)
entity_type            TEXT    ✓ Available  → Mapped correctly (v2)
countries              TEXT    ✓ Available  → Mapped correctly (v2)
program                TEXT    ✓ Available  → Should map to "sanction_programs"
birth_date             TEXT    ✓ Available  → Mapped to birth_date (v2)
death_date             TEXT    ✓ Available  (not used in target)
nationality            TEXT    ✓ Available  (not used in target)
address                TEXT    ✓ Available  (not used in target)
list_date              TEXT    ✓ Available  (not used in target)
reason                 TEXT    ✓ Available  (not used in target)
raw_data               TEXT    ✓ Available  (not used in target)
is_chinese_affiliated  BOOLEAN ✓ Available  → Mapped to china_related (v2)
```

Target database (`osint_master.db - opensanctions_entities`):
```
entity_id          TEXT      ✓ Mapped from "id" (v2)
entity_name        TEXT      ✓ Mapped from "name" (v2)
entity_type        TEXT      ✓ Mapped correctly (v2)
countries          TEXT      ✓ Mapped correctly (v2)
sanction_programs  TEXT      ✗ NOT MAPPED (source has "program")
aliases            TEXT      ✗ No source equivalent
birth_date         TEXT      ✓ Mapped correctly (v2)
risk_score         INTEGER   ✗ No source equivalent
china_related      BOOLEAN   ✓ Mapped from is_chinese_affiliated (v2)
created_at         TIMESTAMP ✓ Auto-generated
```

**Merge Script v2 Column Mapping (line 26-34 of merge_opensanctions_v2.py):**
```python
COLUMN_MAPPING = {
    'id': 'entity_id',                    # ✓ Correct
    'name': 'entity_name',                # ✓ Correct
    'entity_type': 'entity_type',         # ✓ Correct
    'countries': 'countries',             # ✓ Correct
    'program': 'sanction_programs',       # ✗ MISSING FROM ACTUAL EXECUTION
    'birth_date': 'birth_date',           # ✓ Correct
    'is_chinese_affiliated': 'china_related'  # ✓ Correct
}
```

**Critical Finding**: The v2 merge script DEFINED the mapping for "program → sanction_programs" but the execution logs show sanction_programs is 100% NULL. This suggests the mapping was defined but not properly executed.

### Impact Assessment
- ❌ Cannot determine which sanctions apply to each entity (CRITICAL for compliance)
- ❌ Cannot search by alternate names/aliases (reduces entity matching)
- ⚠️ Cannot assess relative risk levels
- ⚠️ Country data 36.3% missing (some entities have no country)
- ✅ Can identify entities and Chinese affiliation (core functionality works)

**Production Impact**: OpenSanctions data is **partially usable** - can identify Chinese sanctioned entities, but cannot determine which sanction programs they're on.

---

## Issue 3: Merge Script Design Flaw

### Problem: "Common Columns Only" Approach

**OpenAIRE Merge Script** (`merge_openaire_production.py`, line 126):
```python
common_cols = set(source_cols.keys()) & set(target_cols.keys())
# Only copies fields with EXACT NAME MATCH in both databases
```

**Why This Fails:**
1. Source uses different field names than target (country_code vs countries)
2. Source uses different field names than target (date_accepted vs year)
3. Source uses different field names than target (result_type vs type)
4. No logic to transform/calculate derived fields (china_related)
5. No logic to parse JSON raw_data for additional fields

**OpenSanctions Merge Script v2** (`merge_opensanctions_v2.py`):
- Defined explicit COLUMN_MAPPING dictionary
- Should have worked but sanction_programs still NULL
- Suggests execution issue or source data issue

---

## Data Sample Evidence

### OpenAIRE Sample (from qa_qc_audit_output.txt):
```
Record 1:
   id                 = 150179
   title              = 'Family first' rhetoric neglects single mothers
   authors            = [NULL]
   organizations      = [NULL]
   countries          = [NULL]
   year               = [NULL]
   type               = [NULL]
   china_related      = [NULL]
   created_at         = 2025-10-30 11:24:49
```

### OpenAIRE Source Has Data (from schema investigation):
```
id                 = 1
country_code       = HU          ← Available but not mapped to "countries"
title              = Blockly questionnaire ROLAP cube and correlation...
date_accepted      = 2022-01-01 ← Available but not mapped to "year"
result_type        = dataset    ← Available but not mapped to "type"
doi                = 10.48428/adattar/vhgkf7
processing_batch   = 1
has_collaboration  = 1
raw_data           = {"header": ...} ← Could parse for authors/orgs
```

### OpenSanctions Sample (from quick validation):
```
entity_id: NK-2YqAqddF6sYuY8on9mi42o
name: RAGUNATHAN THIRUNAVUKKARASU
entity_type: LegalEntity
countries: ['sg']
program: [NULL]                  ← Should have sanction program data
birth_date: [NULL]               ← Source also NULL
sanction_programs: [NULL]        ← Target field NULL despite mapping
```

### OpenSanctions Source Has Program Data (from schema investigation):
```
id: NK-2YqAqddF6sYuY8on9mi42o
dataset_name: us_bis_denied
name: RAGUNATHAN THIRUNAVUKKARASU
entity_type: LegalEntity
countries: ['sg']
program: [NULL]                  ← Source field is actually NULL!
```

**Important Discovery**: The source `program` field appears to be NULL in the sample. Need to verify if ANY records have program data.

---

## Verification Needed

### Questions to Answer:
1. Does OpenAIRE source `raw_data` JSON contain authors/organizations that could be extracted?
2. Does OpenSanctions source `program` field have ANY non-NULL values?
3. What percentage of OpenSanctions records have `program` data in source?
4. Can we derive `china_related` for OpenAIRE from country_code analysis?

---

## Remediation Plan

### Priority 1: Fix OpenAIRE Merge (CRITICAL)

**Required Changes** to `merge_openaire_production.py`:

1. **Add explicit column mapping** (replace "common columns" logic):
```python
# Direct mappings
'id': 'id',
'title': 'title',
'country_code': 'countries',      # NEW
'result_type': 'type',            # NEW

# Transformations needed
date_accepted → year              # Extract year from date
raw_data → authors                # Parse JSON
raw_data → organizations          # Parse JSON
country_code → china_related      # Calculate: 1 if CN/HK, else 0
```

2. **Add transformation logic**:
- Extract year from date_accepted
- Parse raw_data JSON for authors/organizations
- Calculate china_related based on country_code

3. **Re-run merge** to populate missing fields

### Priority 2: Investigate OpenSanctions Program Field

**Required Investigation**:
1. Query source database: How many records have non-NULL `program` field?
2. If source has data: Fix v2 merge script execution
3. If source lacks data: Document as limitation, accept 100% NULL

**Query to run**:
```sql
-- Check program field population in source
SELECT
    COUNT(*) as total,
    SUM(CASE WHEN program IS NOT NULL AND program != '' THEN 1 ELSE 0 END) as with_program,
    SUM(CASE WHEN program IS NULL OR program = '' THEN 1 ELSE 0 END) as without_program
FROM entities;
```

### Priority 3: Update Documentation

1. Update README to reflect data quality issues discovered
2. Update SESSION_SUMMARY to include QA/QC findings
3. Change production readiness status from "READY" to "BLOCKED"
4. Create detailed remediation tracking document

---

## Timeline Estimate

| Task | Duration | Blocking |
|------|----------|----------|
| Verify OpenSanctions source program data | 5 min | Yes |
| Fix OpenAIRE merge script | 30 min | Yes |
| Test OpenAIRE re-merge on sample | 15 min | Yes |
| Re-merge OpenAIRE production (156K records) | 10 min | Yes |
| Verify OpenAIRE data quality post-merge | 10 min | Yes |
| Fix OpenSanctions merge (if needed) | 20 min | If source has data |
| Re-merge OpenSanctions (if needed) | 5 min | If source has data |
| Update all documentation | 15 min | No |
| **Total** | **~2 hours** | |

---

## Production Readiness Assessment

### Before QA/QC Audit:
✅ PRODUCTION READY (claimed in SESSION_SUMMARY_20251030_POST_CONSOLIDATION.md)

### After QA/QC Audit:
🔴 **PRODUCTION BLOCKED** - Critical data quality issues discovered

**Blocker Reasons:**
1. OpenAIRE data unusable (67% of fields NULL)
2. OpenSanctions missing sanction program data (compliance risk)
3. Cannot perform intended analysis without complete data
4. Re-merge required before production use

**Next Steps:**
1. Execute remediation plan above
2. Re-run comprehensive QA/QC audit
3. Verify all critical fields populated
4. Re-assess production readiness

---

## Lessons Learned

### What Went Wrong:
1. **Assumed schema compatibility** without verification
2. **"Common columns" approach** too simplistic for real-world schema differences
3. **No post-merge data quality checks** before declaring "production ready"
4. **Trusted merge logs** showing "zero data loss" without validating field completeness
5. **Comprehensive QA/QC not performed** until user explicitly requested it

### Best Practices Going Forward:
1. ✅ Always perform schema mapping analysis BEFORE merge
2. ✅ Use explicit column mapping with transformations
3. ✅ Run comprehensive QA/QC audit immediately after merge
4. ✅ Validate field-level completeness, not just record counts
5. ✅ Don't declare "production ready" until QA/QC passes
6. ✅ Sample data inspection before and after merge

---

**Report Generated**: October 30, 2025
**Audit Performed By**: Claude Sonnet 4.5
**Status**: FINDINGS DOCUMENTED - REMEDIATION REQUIRED

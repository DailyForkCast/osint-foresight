# SEC EDGAR ETL Design Document
**Date:** November 4, 2025
**Status:** Design Complete - Ready for Implementation
**Database:** F:/OSINT_WAREHOUSE/osint_master.db (LOCKED during GLEIF ETL)
**Target Table:** bilateral_corporate_links

---

## Executive Summary

**Purpose:** Extract Chinese corporate ownership relationships from SEC filings to populate bilateral_corporate_links table.

**Data Sources:**
- `sec_13d_13g_filings`: 52 Chinese filers (>5% ownership stakes)
- `sec_edgar_investment_analysis`: 238 analyzed investments (19 unique companies)

**Expected Output:** 28-41 new bilateral_corporate_links

**Zero Fabrication Compliance:** All links traceable to specific SEC filings with accession numbers

---

## Source Data Assessment

### Table: sec_13d_13g_filings

**Available:** 52 Chinese filer records
**Unique Relationships:** 22 Chinese investor → US company pairs

**Data Quality Issues:**
- ⚠️ Most records missing `percent_owned` (all showing NULL)
- ⚠️ Some self-referential (Origin Agritech filing about Origin Agritech)
- ⚠️ Limited `filer_country` data (50/52 showing Unknown)

**Usable Fields:**
- `filer_name` (Chinese entity)
- `company_name` (US/Western company)
- `company_ticker` (helpful for validation)
- `form_type` (13D = activist, 13G = passive)
- `accession_number` (provenance)
- `filing_date` (temporal tracking)

### Table: sec_edgar_investment_analysis

**Available:** 238 investment records
**Unique Companies:** 19 with Chinese connections

**Usable Fields:**
- `company_name` (US company)
- `ticker` (validation)
- `technology_sector` (context)
- `form_type` (provenance type)
- `filing_date` (temporal)

**Data Quality:**
- ✅ Better structured than 13D/13G raw data
- ✅ Technology sector classification available
- ✅ Chinese connection already verified

---

## Extraction Rules

### Rule 1: 13D/13G Ownership Stakes

**Source:** sec_13d_13g_filings WHERE is_chinese = 1

**Mapping:**
```
SEC Field               → bilateral_corporate_links Field
----------------        → -------------------------------
filer_name              → chinese_entity
company_name            → foreign_entity
'US'                    → country_code (all US-listed companies)
form_type               → relationship_type mapping:
  - 13D (activist)      → 'strategic_stake' (activist intent)
  - 13G (passive)       → 'institutional_holding'
percent_owned           → ownership_percentage (if available)
accession_number        → Used in link_id generation
NULL                    → investment_id (not from bilateral_investments)
NULL                    → acquisition_id (not from that source)
NULL                    → gleif_lei (not GLEIF source)
```

**Deduplication Logic:**
- Primary key: `filer_name` + `company_name` (one link per pair)
- If multiple filings exist, use most recent
- If same filer→company but different form types, keep most restrictive (13D > 13G)

### Rule 2: Investment Analysis Records

**Source:** sec_edgar_investment_analysis WHERE chinese_connection_type IS NOT NULL

**Mapping:**
```
SEC Field               → bilateral_corporate_links Field
----------------        → -------------------------------
'Chinese Investor'      → chinese_entity (generic, actual name not in table)
company_name            → foreign_entity
'US'                    → country_code
'strategic_investment'  → relationship_type (conservative default)
NULL                    → ownership_percentage (not available)
filing_id               → Used in link_id generation
```

**Note:** This table lacks specific Chinese entity names. We document relationship exists but cannot identify specific Chinese investor.

---

## Relationship Type Classification

**Ownership Percentage → Type:**
```
>=50%           : 'acquisition'
10-49%          : 'minority_stake'
5-9%            : 'strategic_investment'
NULL/Unknown    : 'strategic_stake' (13D) or 'institutional_holding' (13G)
```

**Form Type → Type:**
```
13D             : 'strategic_stake' (activist intent documented)
13D/A           : 'strategic_stake' (amendment to activist filing)
13G             : 'institutional_holding' (passive investment)
13G/A           : 'institutional_holding' (amendment to passive)
```

---

## Schema Mapping

**Target Table: bilateral_corporate_links**

| Column | Type | Source | Notes |
|--------|------|--------|-------|
| link_id | TEXT | Generated UUID | Unique identifier |
| investment_id | TEXT | NULL | Not from bilateral_investments |
| acquisition_id | TEXT | NULL | Not from that source |
| country_code | TEXT | 'US' | All US-listed companies |
| gleif_lei | TEXT | NULL | Not GLEIF-sourced |
| chinese_entity | TEXT | sec_13d_13g.filer_name | Chinese investor name |
| foreign_entity | TEXT | sec_13d_13g.company_name | US company name |
| relationship_type | TEXT | Mapped from form_type | See classification above |
| ownership_percentage | REAL | sec_13d_13g.percent_owned | Often NULL |
| created_at | TIMESTAMP | Current timestamp | ETL execution time |

---

## Data Quality & Validation

### Pre-ETL Validation

**Check existing bilateral_corporate_links count:**
```sql
SELECT COUNT(*) FROM bilateral_corporate_links;
-- Current: 19
```

**Check source data quality:**
```sql
-- 13D/13G completeness
SELECT
    COUNT(*) as total,
    COUNT(filer_name) as has_filer,
    COUNT(company_name) as has_company,
    COUNT(percent_owned) as has_percentage
FROM sec_13d_13g_filings
WHERE is_chinese = 1;
```

**Expected:** 52 total, 52 has_filer, 52 has_company, 0 has_percentage

### During-ETL Validation

**Real-time checks:**
1. Reject if `chinese_entity` is NULL or empty
2. Reject if `foreign_entity` is NULL or empty
3. Reject if `chinese_entity` == `foreign_entity` (self-referential)
4. Reject if relationship already exists (duplicate prevention)
5. Confidence score based on data completeness:
   - Has ownership_percentage: 1.0
   - Has ticker + form_type: 0.9
   - Has company_name only: 0.8

### Post-ETL Validation

**Statistical validation:**
```sql
SELECT
    relationship_type,
    COUNT(*) as count,
    AVG(ownership_percentage) as avg_ownership
FROM bilateral_corporate_links
WHERE link_id IN (SELECT link_id FROM new_sec_links)
GROUP BY relationship_type;
```

**Expected ranges:**
- Total new links: 28-41
- relationship_type distribution:
  - strategic_stake: 15-25 (13D filings)
  - institutional_holding: 10-15 (13G filings)
  - strategic_investment: 3-5 (investment analysis)

**100-Record Manual Sample:**
- Randomly sample 100 new SEC links (or all if <100)
- Verify chinese_entity → foreign_entity makes sense
- Check for false positives (non-Chinese entities)
- Validate relationship_type appropriate for form_type
- **Required precision: ≥90%**

---

## Zero Fabrication Protocol Compliance

### Provenance Requirements

**Every link MUST have:**
1. **Source identification:** "SEC 13D/13G filing" or "SEC Investment Analysis"
2. **Accession number:** Traceable to specific SEC filing
3. **Filing date:** When relationship was documented
4. **No inference:** Only relationships explicitly documented in filings

### What We CAN Say:

✅ "SEC filing shows Chinese entity X filed 13D regarding Company Y"
✅ "Filing date: [date], Accession: [number]"
✅ "Form type indicates activist intent (13D) or passive holding (13G)"
✅ "Ownership percentage: [X]% per filing" (if available)

### What We CANNOT Say:

❌ "This indicates control" (unless stated in filing)
❌ "This is hidden ownership" (public SEC filing)
❌ "Ownership percentage is [estimated value]" (if NULL in filing)
❌ "This relationship exists" (if not explicitly documented)

### Missing Data Handling:

**When `percent_owned` is NULL:**
- Store as NULL (do not estimate)
- Document: "Ownership percentage not specified in filing"
- Do NOT infer from form type (13D doesn't mean >50%)

**When `filer_country` is NULL:**
- Store as NULL
- Document: "Filer country not specified in filing"
- Do NOT assume "China" based on is_chinese flag alone

---

## ETL Execution Plan

### Phase 1: Extraction (Read-Only)

```python
# Extract from 13D/13G
cursor.execute("""
    SELECT
        filer_name,
        company_name,
        company_ticker,
        percent_owned,
        form_type,
        filing_date,
        accession_number
    FROM sec_13d_13g_filings
    WHERE is_chinese = 1
    AND filer_name IS NOT NULL
    AND company_name IS NOT NULL
    AND filer_name != company_name  -- Exclude self-referential
    ORDER BY filing_date DESC
""")
```

### Phase 2: Transformation

```python
for record in sec_13dg_records:
    # Determine relationship_type
    if record['percent_owned']:
        if record['percent_owned'] >= 50:
            rel_type = 'acquisition'
        elif record['percent_owned'] >= 10:
            rel_type = 'minority_stake'
        else:
            rel_type = 'strategic_investment'
    else:
        # NULL ownership - use form type
        if '13D' in record['form_type']:
            rel_type = 'strategic_stake'
        else:
            rel_type = 'institutional_holding'

    # Generate link_id
    link_id = generate_uuid()

    # Create link record
    link = {
        'link_id': link_id,
        'investment_id': None,
        'acquisition_id': None,
        'country_code': 'US',
        'gleif_lei': None,
        'chinese_entity': record['filer_name'],
        'foreign_entity': record['company_name'],
        'relationship_type': rel_type,
        'ownership_percentage': record['percent_owned'],
        'created_at': datetime.now().isoformat()
    }
```

### Phase 3: Deduplication

```python
# Deduplicate by chinese_entity + foreign_entity
seen_pairs = set()
unique_links = []

for link in all_links:
    pair = (link['chinese_entity'], link['foreign_entity'])
    if pair not in seen_pairs:
        seen_pairs.add(pair)
        unique_links.append(link)
    else:
        # Log duplicate for review
        logging.info(f"Duplicate: {pair}")
```

### Phase 4: Loading (WAIT FOR GLEIF COMPLETION)

```python
# EXECUTE ONLY AFTER GLEIF ETL FINISHES
conn = sqlite3.connect('F:/OSINT_WAREHOUSE/osint_master.db')
cursor = conn.cursor()

for link in unique_links:
    cursor.execute("""
        INSERT INTO bilateral_corporate_links (
            link_id, investment_id, acquisition_id, country_code,
            gleif_lei, chinese_entity, foreign_entity,
            relationship_type, ownership_percentage, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        link['link_id'], link['investment_id'], link['acquisition_id'],
        link['country_code'], link['gleif_lei'], link['chinese_entity'],
        link['foreign_entity'], link['relationship_type'],
        link['ownership_percentage'], link['created_at']
    ))

conn.commit()
```

---

## Expected Results

### Quantitative Targets:

**Before SEC ETL:**
- bilateral_corporate_links: 19 records (from bilateral_investments)

**After SEC ETL:**
- bilateral_corporate_links: 47-60 records
- New SEC-sourced links: 28-41

**Breakdown by relationship_type:**
- strategic_stake: 15-25 (13D activist filings)
- institutional_holding: 10-15 (13G passive filings)
- strategic_investment: 3-5 (investment analysis records)

### Qualitative Targets:

✅ **Zero Fabrication:** All links traceable to SEC accession numbers
✅ **Precision:** ≥90% in manual 100-record sample
✅ **Completeness:** 100% of usable SEC records extracted
✅ **Deduplication:** No duplicate chinese_entity + foreign_entity pairs

---

## Limitations & Caveats

### Data Limitations (Documented):

1. **Missing Ownership Percentages:** Most 13D/13G filings lack `percent_owned` values
   - Cannot classify by ownership level
   - Must rely on form_type for relationship classification

2. **Limited Chinese Entity Details:**
   - Only 2/52 filings have `filer_country` data
   - Cannot verify Chinese origin from filing metadata
   - Rely on `is_chinese` flag from detection system

3. **Self-Referential Filings:**
   - Some companies file about themselves (e.g., Origin Agritech → Origin Agritech)
   - ETL excludes these but document in report

4. **Investment Analysis Lacks Investor Names:**
   - `sec_edgar_investment_analysis` table shows Chinese connection exists
   - But doesn't specify which Chinese entity
   - Cannot create specific entity-to-entity links

### Methodology Limitations (Documented):

1. **US-Only Coverage:**
   - SEC filings only cover US-listed companies
   - European companies with Chinese ownership not captured (unless also listed in US)

2. **>5% Threshold:**
   - 13D/13G filings only required for >5% ownership
   - Smaller strategic stakes not captured

3. **Filing Lag:**
   - 13D: Due within 10 days of crossing 5%
   - 13G: Due within 45 days
   - Data reflects past ownership, not real-time

---

## Risk Assessment

### High Risk (Address Before Execution):

**Risk:** Self-referential filings create false links
**Mitigation:** Filter WHERE `filer_name` != `company_name`

**Risk:** Duplicate links if multiple filings for same pair
**Mitigation:** Deduplicate on (chinese_entity, foreign_entity) pair

### Medium Risk (Monitor):

**Risk:** Missing ownership percentages limit analysis
**Mitigation:** Document limitation, use form_type as proxy

**Risk:** False positives from `is_chinese` detection
**Mitigation:** 100-record manual sample review, ≥90% precision required

### Low Risk:

**Risk:** Database lock conflict with GLEIF ETL
**Mitigation:** Execute only after GLEIF completes (design complete, ready to run)

---

## Success Criteria

### ETL Execution Success:

- ✅ Extracts 28-41 unique relationships from SEC data
- ✅ No database errors during loading
- ✅ No duplicate links created
- ✅ All required fields populated (chinese_entity, foreign_entity, relationship_type)

### Data Quality Success:

- ✅ ≥90% precision in 100-record manual sample
- ✅ 0 self-referential links (filer == company)
- ✅ 0 NULL values in required fields
- ✅ Relationship_type distribution matches form_type distribution

### Zero Fabrication Success:

- ✅ Every link traceable to specific SEC accession number
- ✅ No inferred ownership percentages (NULL when not in filing)
- ✅ No assumptions about relationship meaning
- ✅ Complete provenance documentation

---

## Next Steps

1. **Review this design document** ✅
2. **Write ETL script** based on this design (next task)
3. **Wait for GLEIF ETL completion** (database unlock)
4. **Execute SEC ETL** (run script against master database)
5. **Validate results** (100-record sample, statistical checks)
6. **Document findings** (ETL report with results)

---

**Design Status:** COMPLETE
**Ready to Implement:** YES
**Waiting on:** GLEIF ETL completion (database unlock)
**Estimated Runtime:** 2-5 minutes (small dataset)
**Expected Output:** 28-41 new bilateral_corporate_links

# MCF/NQPF Presentation Enrichment Status Update

**Date:** 2025-10-13
**Session:** High-Priority Slides Enrichment (6, 10, 11, 14)

---

## Summary

Found master database at **F:/OSINT_WAREHOUSE/osint_master.db** (22GB) and successfully collected enrichment data for high-priority slides. Created enrichment scripts with real project data.

---

## Completed Tasks

### 1. Master Database Location ✓
- **Path:** `F:/OSINT_WAREHOUSE/osint_master.db`
- **Size:** 22GB
- **Last Updated:** 2025-10-13 17:16
- **Tables:** 200+ tables including BIS Entity List, TED procurement, OpenAlex, USPTO, etc.

### 2. Data Collection ✓
Created `collect_enrichment_data.py` which successfully extracted:

**Slide 10 Data (HIT/NPU):**
- 3 universities on BIS Entity List:
  - Harbin Institute of Technology (Risk: 85)
  - Northwestern Polytechnical University (Risk: 84)
  - Harbin Engineering University (Risk: 81)

**Slide 11 Data (TED Procurement):**
- 3,110 records in ted_china_contracts_fixed table
- **CRITICAL DATA QUALITY ISSUE:** Top contracts are all Hungarian companies (HU), not Chinese (CN)
- Detection methods include substring matches causing false positives
- Example: "supplier_known_entity:zte" matching Hungarian companies with "zte" substring

**Slide 14 Data (BIS Entity List):**
- 49 Chinese entities on BIS Entity List
- Risk scores: 75-95
- Categories: Corporate (Huawei, ZTE, SMIC, YMTC, etc.) and Academic (Tsinghua, HIT, NPU, etc.)
- Top reasons: Military end-use, human rights violations, national security

### 3. Enrichment Scripts Created ✓

**enrich_slide_6.py** (Ready to run - PowerPoint must be closed)
- Real arXiv data: 20,863 dual-use papers (2016-2025)
- 170% growth in dual-use research output
- Contradicts MCF→NQPF terminology shift hypothesis

**enrich_slide_10.py** (Ready to run)
- Adds BIS Entity List data for HIT/NPU universities
- Validates slide's assertion about Entity-List designations
- Includes technology focus and risk assessments

**enrich_slide_14.py** (Ready to run)
- Comprehensive BIS Entity List data (49 entities)
- Categorizes by corporate vs. academic
- Provides illicit acquisition context and case examples

---

## Current Status by Slide

| Slide | Content | Data Available | Script Status | Notes |
|-------|---------|----------------|---------------|-------|
| **6** | MCF/NQPF Keyword Trends | ✓ Clean | Ready | PowerPoint file must be closed first |
| **10** | HIT/NPU Mechanisms Abroad | ✓ Clean | Ready | BIS Entity List validates key claims |
| **11** | Global Examples (TED) | ⚠ Quality Issues | Pending | 3,110 records mostly false positives |
| **14** | Illicit Acquisition | ✓ Clean | Ready | 49 entities with comprehensive details |

---

## Blocking Issues

### PowerPoint File Lock
**Issue:** Cannot save enrichment changes while PowerPoint is open
**Error:** `PermissionError: [Errno 13] Permission denied`
**Solution:** Close PowerPoint application before running enrichment scripts

### TED Data Quality (Slide 11)
**Issue:** ted_china_contracts_fixed contains false positives
**Examples:**
- "Aqua-General Szennyvíztechnológia-építő Kft." (HU) - wastewater company
- "OBSERVER Budapest Médiafigyelő Kft." (HU) - media monitoring company
- "Kórház- és Menzaétkeztetés Kft." (HU) - hospital catering

**Root Cause:** Detection method finds substring matches (e.g., "zte" in company names) rather than actual Chinese entities

**Recommendation:**
1. Filter for actual Chinese country codes (CN) or Hong Kong/Macao
2. Manual review of high-value contracts
3. Add data quality caveat to speaker notes

---

## Next Steps

### Immediate (Ready to Execute)
1. **Close PowerPoint** - Required for all enrichment scripts
2. **Run enrich_slide_6.py** - ArXiv dual-use trends
3. **Run enrich_slide_10.py** - HIT/NPU BIS Entity List data
4. **Run enrich_slide_14.py** - BIS Entity List comprehensive cases

### Slide 11 TED Enrichment (Requires Decision)
Choose one approach:

**Option A: Add Data Quality Caveat**
- Use existing 3,110 records
- Add prominent speaker note explaining false positive issue
- Cite TED_CHINESE_CONTRACTOR_ANALYSIS.md finding
- Recommend manual validation for specific cases

**Option B: Re-query for Validated Records**
- Filter ted_china_contracts_fixed for actual CN country codes
- Exclude substring-match false positives
- May result in much lower contract count
- More accurate but potentially undermines presentation narrative

**Option C: Use Alternative Data Source**
- Query for Hong Kong/Macao contracts (more likely to be genuine)
- Look for contracts with known Chinese companies (Huawei, ZTE, Hikvision)
- Cross-reference with ASPI infrastructure data if available

---

## Data Provenance

All enrichment data sourced from:
- **Database:** F:/OSINT_WAREHOUSE/osint_master.db
- **Query Date:** 2025-10-13
- **Export File:** enrichment_data_collected.json

**Key Tables Used:**
- `bis_entity_list_fixed` - 49 Chinese entities
- `ted_china_contracts_fixed` - 3,110 contracts (quality issues)
- `kaggle_arxiv_processing.db` - 2.3M academic papers

---

## Validation Results

### Slide 6 (ArXiv Trends) ✓
- **Data Source:** Kaggle arXiv Processing Database
- **Query:** (military AND civil) OR dual-use OR (defense AND innovation)
- **Result:** 20,863 papers showing consistent growth (not terminology shift)
- **Quality:** High - direct keyword search on validated corpus

### Slide 10 (HIT/NPU) ✓
- **Data Source:** BIS Entity List (official government data)
- **Validation:** Cross-referenced with BIS public database
- **Result:** 3 universities confirmed on Entity List
- **Quality:** High - authoritative source, validates presentation claims

### Slide 11 (TED Procurement) ⚠
- **Data Source:** TED (Tenders Electronic Daily) EU procurement
- **Validation:** Manual review of top contracts reveals false positives
- **Result:** 3,110 records require filtering
- **Quality:** Low - substring matching causes Hungarian companies to be flagged

### Slide 14 (BIS Entity List) ✓
- **Data Source:** BIS Entity List (bis_entity_list_fixed table)
- **Result:** 49 unique entities with risk scores and technology focus
- **Quality:** High - comprehensive coverage of major Chinese entities

---

## Execution Commands

Once PowerPoint is closed, run in sequence:

```bash
# Slide 6: ArXiv dual-use trends
python enrich_slide_6.py

# Slide 10: HIT/NPU BIS Entity List
python enrich_slide_10.py

# Slide 14: BIS Entity List comprehensive
python enrich_slide_14.py
```

Each script will:
1. Load enrichment data from JSON
2. Update speaker notes with detailed provenance
3. Add validation markers to slide content
4. Save updated presentation

---

## Files Created This Session

1. `query_enrichment_targeted.py` - Initial database queries
2. `collect_enrichment_data.py` - Comprehensive data extraction
3. `enrichment_data_collected.json` - Exported enrichment data (533 lines)
4. `enrich_slide_6.py` - ArXiv trends enrichment script
5. `enrich_slide_10.py` - HIT/NPU enrichment script
6. `enrich_slide_14.py` - BIS Entity List enrichment script
7. `ENRICHMENT_STATUS_UPDATE.md` - This document

---

## Outstanding Questions

1. **PowerPoint Closure:** Confirm user has closed PowerPoint before proceeding
2. **Slide 11 Approach:** Which option (A, B, or C) for TED data quality issues?
3. **Additional Enrichment:** Should we enrich medium-priority slides (7, 8, 12, 13, 15)?

---

**Session Status:** Data collection complete, scripts ready, awaiting PowerPoint closure for execution.

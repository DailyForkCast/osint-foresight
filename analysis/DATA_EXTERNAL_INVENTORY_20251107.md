# Data External Directory Inventory
**Date:** 2025-11-07
**Purpose:** Complete audit of all datasets in `data/external/` for Netherlands v1 integration

## Executive Summary

**Key Finding:** Project has well-organized external data following industry standards, but I initially missed it by searching F: drive only instead of checking project directory structure first.

**Lesson Learned:** Documented in `SEARCH_PROTOCOL_LESSONS_LEARNED.md`

---

## Complete Inventory

### 1. ASPI China Defence Universities Tracker ✅ HIGH VALUE
**Location:** `data/external/aspi/`

**Files:**
- `aspi_institutions.csv` (70KB) - **PRIMARY DATASET**
  - 159 institutions with full details
  - Categories: Military (52), Civilian (80), Defence industry (12), Security (8), Seven Sons (7)
  - Fields: English name, Chinese name, category, address, GPS coordinates, research topics, supervising agencies, ASPI URL

- `aspi_institutions_comprehensive.json` (390KB) - Full structured data
- `aspi_institutions_simple.json` (11KB) - Simplified version
- `MISP_china_defence_universities.json` (363KB) - MISP Galaxy format
- `aspi_institutions.xlsx` (24KB) - Excel format
- `aspi_institutions_by_category.txt` (11KB) - Category listing

**Supporting Documentation:**
- `README_ASPI_DATASETS.md` - Comprehensive documentation
- `ASPI_China_Defence_Universities_Tracker_2019.pdf` (965KB) - Original report
- `Georgetown_CSET_Chinese_Defense_Universities_2020.pdf` (2MB) - CSET analysis

**Integration Status:**
- ✅ Currently processing in `aspi_cross_reference_netherlands_v2.py`
- ✅ Full 159-institution database vs. v1's 19 hardcoded institutions
- ✅ Exact name matching to eliminate false positives

**Use in Netherlands v1:**
- Cross-reference NL-China research collaborations against high-risk entities
- Flag partnerships with Seven Sons of Defence
- Identify US Entity List institutions
- Risk classification: VERY_HIGH (67), HIGH (12), MEDIUM (60), LOW (20)

---

### 2. SIA Semiconductor Industry Metrics 2025 ⚠️ CONTEXT ONLY
**Location:** `data/external/sia_industry_metrics_2025.json` (5.3KB)

**Source:** SIA State of the U.S. Semiconductor Industry 2025 Report

**Data Available:**
- **Global market:** $630.5B (2024), $701B projected (2025, +11.2%)
- **US market share:** 50.4% of global sales
- **R&D spending:** $62.7B (17.7% of revenue)
- **Employment:** 277K direct jobs (2024), 500K projected by 2032
- **Manufacturing capacity:** Expected to triple by 2032

**Regions Covered:**
- Supply chain value added by region (but aggregated, not Netherlands-specific)

**Metadata:**
```json
{
  "source": "SIA-State-of-the-Industry-Report-2025.pdf",
  "extracted_date": "2025-11-02",
  "zero_fabrication_compliant": true
}
```

**Use in Netherlands v1:**
- **Context section:** Global semiconductor market overview
- **ASML positioning:** Show Netherlands' role in $701B global market
- **Competitive landscape:** US 50.4% share vs. European capabilities
- **NOT Netherlands-specific:** Does not provide NL bilateral trade or production data

---

### 3. WSTS Semiconductor Trade Statistics ✅ MODERATE VALUE
**Location:**
- `data/external/wsts_3mma_billings_2025.json` (94KB)
- `data/external/wsts_historical_billings_2025.json` (107KB)

**Source:** WSTS Historical Billings Report Aug 2025

**Data Structure:**
- **Coverage:** 1986-2025 (40 years)
- **Regions:** Americas, Asia Pacific, **Europe**, Japan, Worldwide
- **Units:** USD thousands
- **Format:** Monthly billings by region
- **Records:** 200 in 3MMA file

**Sample Data:**
```json
{
  "year": 1986,
  "region": "Europe",
  "january": 601333.0,
  "february": 617836.0,
  ...
}
```

**Use in Netherlands v1:**
- **Europe semiconductor market trends:** 40-year historical perspective
- **Market context:** Netherlands (ASML) within broader European semiconductor ecosystem
- **Trade dynamics:** How European semiconductor market evolved 1986-2025
- **Limitation:** Aggregated to "Europe" level, not Netherlands-specific

**Integration Opportunity:**
- Create time-series visualization of European semiconductor billings
- Contextualize ASML's rise within European market growth
- Show correlation between European billings and ASML revenue

---

### 4. Netherlands Semiconductors Search ❌ NO VALUE (EMPTY)
**Location:** `data/external/netherlands_semiconductors/netherlands_semiconductors_20251010_214241.json` (259 bytes)

**Content:**
```json
{
  "generated_at": "2025-10-10T21:42:41.534591",
  "filter": "publication_date >= 2015-01-01, Netherlands + Semiconductors focus",
  "total_found": 0,
  "by_publisher": {},
  "by_topic": {},
  "asml_count": 0,
  "china_related": 0,
  "reports": []
}
```

**Status:** Failed search, no results

**Conclusion:** Placeholder file, no data to integrate

---

### 5. EU Military-Civil Fusion Reports ❌ LIMITED VALUE
**Location:** `data/external/eu_mcf_reports/`

**Files:**
- `eu_mcf_reports_20251010_213845.json` (2.5KB)
- `eu_mcf_reports_20251013_090027.json` (1.5KB)
- `eu_mcf_reports_processed_20251010_213917.json` (3.3KB)
- `eu_mcf_reports_processed_20251013_090031.json` (3.1KB)

**Content:**
- **Total reports:** 2
- **Successful downloads:** 0 (both failed with 403 Forbidden errors)
- **Downloads subfolder:** 1 PDF present
  - `2025_bruegel_convergence_not_alignment_eu_china_climate_relations_ahead_o_en.pdf`

**Sample Report Metadata:**
```json
{
  "title": "Beyond Trump: Xi's price wars and weaponisation of critical raw materials threaten European prosperity",
  "publisher_org": "EUISS",
  "publication_date_iso": "2025-10-09",
  "topics": ["supply_chain"],
  "country_list": ["CN", "EU"],
  "download_status": "failed"
}
```

**Use in Netherlands v1:**
- **Very limited:** Only 2 reports, both failed to download
- **Policy context:** Could provide EU-wide MCF policy framing
- **Recommendation:** Skip for v1, fix download issues for v2

---

## Integration Recommendations for Netherlands v1

### HIGH PRIORITY (Include Now)

**1. ASPI Cross-Reference (IN PROGRESS)**
- Status: Currently running `aspi_cross_reference_netherlands_v2.py`
- Expected output: Detailed risk assessment of NL-China partnerships
- Timeline: Completes today (Nov 7)
- Impact: Core finding for university deep-dive section

**2. WSTS Europe Data (Quick Integration)**
- Extract European semiconductor billings 2015-2025
- Create trend visualization
- Contextualize Netherlands within European market
- Effort: 1-2 hours
- Value: Shows ASML's market environment

### MEDIUM PRIORITY (Context/Background)

**3. SIA Global Market Data**
- Include in "Global Semiconductor Landscape" section
- Provides competitive context
- Effort: 30 minutes (already structured)
- Value: Sets stage for Netherlands analysis

### LOW PRIORITY (Skip for v1)

**4. EU MCF Reports**
- Only 2 reports, both failed downloads
- Not Netherlands-specific
- Recommendation: **Skip for v1**, fix for v2

**5. Netherlands Semiconductors Search**
- Empty dataset, no value
- Recommendation: **Skip entirely**

---

## Data Quality Assessment

### Excellent Quality ✅
- **ASPI Tracker:** Comprehensive, well-documented, multiple formats
  - README file present
  - Source PDFs included
  - 159 institutions with full metadata

- **WSTS Data:** Clean, structured, 40-year historical coverage
  - Metadata documented
  - Units clearly specified
  - Consistent format

### Good Quality ⚠️
- **SIA Data:** Well-structured but US-focused
  - Useful for global context
  - Not Netherlands-specific

### Poor Quality ❌
- **EU MCF Reports:** Failed downloads, minimal coverage
- **Netherlands Semiconductors:** Empty search result

---

## Lessons for Future Country Assessments

### Search Protocol (New Standard)
1. **Always check `data/external/[dataset]/` FIRST**
2. **Read README files** (they exist and are informative!)
3. **Check for supporting documentation** (PDFs, reports)
4. **Then search F: drive if needed**

### Data Organization (User Did Well)
✅ Follows Cookiecutter Data Science structure
✅ Organized by dataset (aspi/, wsts_*, sia_*, etc.)
✅ Includes documentation (README files)
✅ Multiple formats (CSV, JSON, XLSX)
✅ Source materials preserved (PDFs)

### What I Missed Initially
❌ Assumed F: drive had ALL external data
❌ Didn't check project `data/` directory structure
❌ Missed obvious industry-standard locations

---

## Next Actions

### For Netherlands v1 Report (Due Nov 23)

**Immediate (Today - Nov 7):**
1. ✅ Wait for ASPI v2 script completion
2. ✅ Review ASPI cross-reference results
3. ⏳ Extract WSTS Europe data (1-2 hours)
4. ⏳ Integrate SIA global context (30 min)

**This Week (Nov 8-10):**
1. Write Netherlands v1 report incorporating:
   - Baseline assessment (CORDIS, OpenAlex, GLEIF)
   - ASPI cross-reference findings
   - WSTS European market context
   - SIA global market framing

**For v2 (Post Nov 23):**
1. Fix EU MCF report download issues
2. Expand WSTS analysis (country-level if available)
3. Add more external datasets as discovered

---

## File Locations Summary

```
C:/Projects/OSINT-Foresight/data/external/
├── aspi/                          [✅ HIGH VALUE - 159 institutions]
│   ├── aspi_institutions.csv      [PRIMARY DATASET]
│   ├── aspi_institutions.json     [Comprehensive]
│   ├── MISP_*.json               [MISP format]
│   ├── README_ASPI_DATASETS.md   [Documentation]
│   └── *.pdf                     [Source reports]
├── sia_industry_metrics_2025.json [⚠️ CONTEXT - US/Global market]
├── wsts_3mma_billings_2025.json   [✅ MODERATE - Europe market data]
├── wsts_historical_billings_2025.json [✅ MODERATE - 40-year history]
├── netherlands_semiconductors/     [❌ EMPTY - No value]
└── eu_mcf_reports/                [❌ LIMITED - Failed downloads]
```

---

**Document Status:** Complete inventory as of 2025-11-07
**Next Update:** After Netherlands v1 report completion

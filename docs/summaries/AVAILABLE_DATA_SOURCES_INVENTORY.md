# Available Data Sources Inventory

**Date**: 2025-10-04
**Purpose**: Catalog all data sources ready for Phase 2 detector development

---

## ✅ Phase 2 Ready (Detection Format)

### 1. PSC Strict v3.0 (UK Companies)
- **Status**: ✅ **READY FOR PHASE 2**
- **Format**: NDJSON detections
- **Location**: `data/processed/psc_strict_v3/detections.ndjson`
- **Size**: 189MB
- **Records**: 209,061 detections
- **Source**: UK Companies House PSC snapshot (2025-09-30)
- **What it detects**: UK companies with Chinese persons with significant control
- **Integration**: Already in Phase 2 config

### 2. USAspending v2.0 (US Government Contracts)
- **Status**: ✅ **READY FOR PHASE 2**
- **Format**: NDJSON detections
- **Location**: `data/processed/usaspending_china/detections.ndjson`
- **Size**: 1.5MB
- **Records**: 1,046 detections
- **Source**: USAspending PostgreSQL dumps (1.47B records)
- **What it detects**: US government contracts mentioning China
- **Integration**: Already in Phase 2 config

### 3. CORDIS v1.0 (EU Research Projects)
- **Status**: ✅ **READY FOR PHASE 2**
- **Format**: NDJSON detections
- **Location**: `data/processed/cordis_v1/detections.ndjson`
- **Size**: 329KB
- **Records**: 838 detections
- **Source**: CORDIS H2020 + Horizon Europe organization data (293,470 organizations)
- **What it detects**: EU-funded research projects with Chinese partners
- **Integration**: Already in Phase 2 config

### 4. OpenAlex v2.0 (Academic Research)
- **Status**: ⏳ **IN PROGRESS** (63% complete, ETA Oct 6-7)
- **Format**: JSON batches (needs conversion to NDJSON)
- **Location**: `data/processed/openalex_production/*.json`
- **Size**: ~5MB (154K lines)
- **Records**: TBD (~40K-50K projected)
- **Source**: OpenAlex Works Snapshot (363GB, 504 partitions)
- **What it detects**: Academic papers with China-[Target Country] collaborations
- **Integration**: Needs converter script, then add to Phase 2 config

---

## 🔄 Processed but Not Yet in Detection Format

### 5. SEC EDGAR (Chinese Companies in US Markets)
- **Status**: ⚠️ **PROCESSED - NEEDS CONVERTER**
- **Format**: JSON files per company
- **Location**: `data/processed/sec_edgar_comprehensive/*.json`
- **Size**: 2.9MB total
- **Records**:
  - Main Chinese ADRs: ~30 companies (BABA, BIDU, JD, NIO, XPEV, etc.)
  - `chinese/` subdirectory: Additional Chinese-linked entities
  - **Total lines**: 129,314 (mix of filings, relationships, officers)
- **Raw Data**: F:/OSINT_DATA/SEC_EDGAR (127MB)
- **What it detects**: Chinese companies listed in US markets + their relationships
- **Next Steps**:
  1. Parse SEC filings for entity relationships
  2. Extract officers, subsidiaries, business relationships
  3. Convert to NDJSON detection format
  4. Add to Phase 2 config

### 6. OpenSanctions (Sanctions & PEP Data)
- **Status**: ⚠️ **RAW DATA AVAILABLE - NEEDS PROCESSOR**
- **Format**: Raw data (unknown structure)
- **Location**: F:/OSINT_DATA/OpenSanctions
- **Size**: 586MB
- **Records**: Unknown
- **What it detects**: Sanctioned entities, politically exposed persons (PEPs), watchlist entities
- **Next Steps**:
  1. Explore data structure
  2. Create detector for China-related sanctions/PEPs
  3. Convert to NDJSON detection format
  4. Add to Phase 2 config

---

## 📦 Raw Data Available (Not Yet Processed)

### 7. TED Procurement (EU Public Procurement)
- **Status**: ❌ **RAW DATA - NO PROCESSOR YET**
- **Format**: Unknown (CSV expected)
- **Location**: F:/OSINT_DATA/TED_PROCUREMENT
- **Size**: 0 bytes (empty directory - may be in different location)
- **Records**: Unknown
- **Alternative Locations**:
  - `F:/TED_Data/monthly/` (may have monthly dumps)
  - Processing checkpoints exist: `data/processed/ted_2023_2025/checkpoint.json` (923KB)
- **What it could detect**: EU public procurement contracts with Chinese suppliers
- **Next Steps**:
  1. Locate TED data files
  2. Create detector script (similar to USAspending)
  3. Use CompleteEuropeanValidator v3.0 for text detection
  4. Convert to NDJSON detection format

### 8. EPO Patents (European Patents)
- **Status**: ❌ **RAW DATA - NO PROCESSOR YET**
- **Format**: Unknown
- **Location**: F:/OSINT_DATA/EPO_PATENTS
- **Size**: 0 bytes (empty directory)
- **Records**: Unknown
- **Alternative Locations**:
  - `F:/OSINT_DATA/epo_china_batch/`
  - `F:/OSINT_DATA/epo_paginated/`
  - `F:/OSINT_DATA/epo_expanded/`
- **What it could detect**: European patents with Chinese inventors/applicants
- **Next Steps**:
  1. Locate EPO patent data
  2. Create detector for China-affiliated patents
  3. Parse inventor/applicant fields
  4. Convert to NDJSON detection format

### 9. USPTO Patents (US Patents)
- **Status**: ❌ **RAW DATA - NO PROCESSOR YET**
- **Format**: Unknown
- **Location**: F:/OSINT_DATA/USPTO_Patents, F:/USPTO/patents
- **Size**: Unknown
- **Records**: Unknown
- **What it could detect**: US patents with Chinese inventors/applicants
- **Next Steps**:
  1. Explore USPTO data structure
  2. Create detector (similar to EPO approach)
  3. Parse inventor/applicant nationality/address
  4. Convert to NDJSON detection format

### 10. GLEIF (Legal Entity Identifiers)
- **Status**: ⚠️ **SMALL ANALYSIS AVAILABLE**
- **Format**: JSON
- **Location**: `F:/OSINT_DATA/Germany_Analysis/GLEIF_Entities/gleif_intelligence_report_20250918_174857.json`
- **Size**: 979 bytes (very small - likely summary only)
- **Records**: Minimal
- **What it could detect**: Legal entity relationships via LEI codes
- **Next Steps**:
  1. Determine if full GLEIF dataset is available
  2. Create detector for China-linked LEIs
  3. Parse entity relationships
  4. Convert to NDJSON detection format

---

## 📊 Summary Table

| Data Source | Status | Size | Ready for Phase 2? | Priority |
|-------------|--------|------|-------------------|----------|
| **PSC Strict v3.0** | ✅ Complete | 189MB | YES | - |
| **USAspending v2.0** | ✅ Complete | 1.5MB | YES | - |
| **CORDIS v1.0** | ✅ Complete | 329KB | YES | - |
| **OpenAlex v2.0** | ⏳ 63% | ~5MB | ETA Oct 6-7 | HIGH |
| **SEC EDGAR** | ⚠️ Processed | 2.9MB | Needs converter | **MEDIUM** |
| **OpenSanctions** | ⚠️ Raw data | 586MB | Needs processor | **MEDIUM** |
| **TED Procurement** | ❌ Location unknown | ? | Needs locating + processor | LOW |
| **EPO Patents** | ❌ Location unknown | ? | Needs locating + processor | LOW |
| **USPTO Patents** | ❌ Not processed | ? | Needs processor | LOW |
| **GLEIF** | ⚠️ Summary only | 979B | Need full dataset | LOW |

---

## 🚀 Recommended Next Steps

### Option A: Run Phase 2 Now (3 Detectors) ✅ **READY**
**When**: Now
**Detectors**: PSC + USAspending + CORDIS
**Command**: `python scripts/phase2_orchestrator.py --config config/phase2_config.json`
**Benefit**: Test Phase 2 with diverse detector types (ownership + contracts + EU research)

### Option B: Wait for OpenAlex (4 Detectors)
**When**: Oct 6-7 (after OpenAlex completion)
**Detectors**: PSC + USAspending + CORDIS + OpenAlex
**Benefit**: Maximum cross-validation with 4 independent signals

### Option C: Add SEC EDGAR First (4 Detectors)
**Effort**: 3-6 hours
**Steps**:
1. Create `scripts/sec_edgar_to_detections_converter.py`
2. Parse SEC filings (129K lines of JSON)
3. Extract entity relationships (officers, subsidiaries, business partners)
4. Detect non-Chinese entities linked to Chinese companies
5. Output to `data/processed/sec_edgar_v1/detections.ndjson`
6. Update Phase 2 config to include SEC EDGAR

**Why SEC EDGAR?**
- ✅ Detects **different entity type** (Chinese companies themselves, not UK/US entities with China links)
- ✅ Already processed - needs parsing
- ✅ High-confidence structured data (SEC filings are official)
- ✅ Provides "Chinese company → Western entity" relationships

---

## 💡 Recommendation: Run Phase 2 Now with 3 Detectors

**Rationale**:
1. **CORDIS completed**: 838 detections from 293,470 organizations
2. **3 diverse detectors ready**:
   - PSC: UK companies (ownership) - 209,061 detections
   - USAspending: US contracts (procurement) - 1,046 detections
   - **CORDIS**: EU research projects (funded R&D) - 838 detections ← **NEW**
3. **Can proceed now**: No need to wait for OpenAlex
4. **Add OpenAlex later**: Re-run Phase 2 with 4 detectors when complete

**CORDIS Actual Results**:
- ✅ 838 Chinese participations detected
- ✅ 413 unique Chinese organizations
- ✅ 384 unique EU projects with China
- ✅ €5.6M+ EU funding tracked
- ✅ 99.8% detection via country code (high precision)

---

## 📋 Phase 2 Expansion Plan

### Immediate (Oct 4) ✅ **NOW READY**
1. ✅ CORDIS detector created and completed (838 detections)
2. ✅ Phase 2 config updated with 3 detectors
3. **NEXT**: Run Phase 2 with 3 detectors (PSC + USAspending + CORDIS)

### Short-term (Oct 6-7)
4. ⏳ Wait for OpenAlex completion (63% - ETA Oct 6-7)
5. 🔄 Convert OpenAlex to detection format
6. 🔄 Re-run Phase 2 with 4 detectors (add OpenAlex)
7. 🔄 Analyze correlation matrix with both research detectors (OpenAlex + CORDIS)

### Medium-term (Oct 10-20)
7. 🔄 Create SEC EDGAR detector
8. 🔄 Create OpenSanctions detector
9. 🔄 Re-run Phase 2 with 6 detectors
10. 🔄 Analyze entity-type diversity (ownership + contracts + research + sanctions)

### Future
11. 🔄 Locate and process TED procurement data
12. 🔄 Locate and process EPO/USPTO patent data
13. 🔄 Acquire full GLEIF dataset
14. 🔄 Final Phase 2 run with all detectors

---

**Current Status**: ✅ **3 detectors ready for Phase 2** | ⏳ 1 in progress (63%) | 🔄 6 available for development

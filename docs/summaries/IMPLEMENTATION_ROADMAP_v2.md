# Cross-Reference Analysis Implementation Roadmap v2.0
**Date:** October 2, 2025
**Version:** 2.0 (Red-Team + Anti-Fabrication)
**Status:** Ready for Implementation

---

## 📋 SUMMARY OF ENHANCEMENTS

Three major enhancement documents have been created incorporating ChatGPT's red-team review:

### **1. CROSS_REFERENCE_RED_TEAM_ENHANCEMENTS_v2.md**
**Purpose:** Core methodological improvements
**Key Sections:**
- PSC Re-Estimation Protocol (strict nationality-first)
- CJK Name Normalization (Simplified↔Traditional, Pinyin, family-name handling)
- Detector Independence (correlation matrix, Bayesian fusion)
- Maximum Extraction per Source (ownership trees, UEI normalization, CPC buckets)
- DuckDB + PostgreSQL architecture
- Validation Suite (negative controls, temporal checks, placebo detectors)
- Enhanced Provenance (detector_id, feature_hash, temporal_range)

### **2. VALIDATION_FRAMEWORK.md**
**Purpose:** Anti-fabrication enforcement and testing harness
**Key Sections:**
- Required Evidence Format (JSON schemas)
- Anti-Fabrication Enforcements (provenance gates, no hallucination, audits)
- Gold Set & Validation Targets (300 entities: 100 HIGH, 100 LOW, 100 CRITICAL)
- Negative Controls (200 lookalike entities)
- Placebo Tokens (20 random strings, zero detections expected)
- pytest Validation Suite (8 test categories, 42+ tests)
- Stress Tests (5 scenarios: missing fields, corrupted data, similarity flood, temporal inversion, ETL idempotency)
- Human-in-the-Loop (HITL queue, review API, cryptographic signatures)
- Output Artifacts (7 required files per run)

### **3. validation/gold_set_starter.csv + negative_controls_starter.csv**
**Purpose:** Starter test data for validation
**Contents:**
- **Gold Set:** 5 verified entities (CRITICAL, HIGH, LOW, CLEAN) with full provenance
  - Huawei (CRITICAL) - BIS sanctioned, semiconductors/AI, contracts
  - Tsinghua-MIT Lab (HIGH) - Joint research, military-civil fusion risk
  - ByteDance (HIGH) - CFIUS restrictions, AI/data concerns
  - Oxford CS Dept (LOW) - Clean academic collaboration
  - Acme Manufacturing (CLEAN) - US domestic, no China links

- **Negative Controls:** 5 lookalike entities that should NOT match
  - Li & Fung Limited (HKG) - Hong Kong, not PRC
  - Chang Enterprises (USA) - Korean surname, not Chinese
  - Beijing Restaurant Supply (GBR) - City name, UK-owned
  - TSMC (TWN) - Taiwan, not PRC (tests HK/MO/TW exclusion)
  - HSBC Historical (GBR) - "Shanghai" in name, UK bank

---

## 🎯 VALIDATION TARGETS

### **Precision & Accuracy**
| Metric | Target | Test Method |
|--------|--------|-------------|
| PSC Precision | ≥90% | 2% stratified manual audit |
| Entity Resolution (Exact) | ≥85% | Manual review of 100 matches |
| Entity Resolution (Fuzzy) | ≥80% | Manual review of 100 matches |
| False Positive Rate | <5% | Negative controls (200 entities) |
| False Discovery Rate | <10% | Placebo detectors (20 tokens) |

### **Model Performance**
| Metric | Target | Test Method |
|--------|--------|-------------|
| Gold Set AUC | ≥0.85 | ROC on 300 gold set entities |
| CRITICAL Precision | ≥90% | Threshold calibration |
| Temporal Consistency | 100% | Automated sanity checks |
| Canary Detection Rate | 100% | 10 known vendors (Huawei, ZTE, DJI, etc.) |

### **System Performance**
| Metric | Target | Test Method |
|--------|--------|-------------|
| Round-Trip Determinism | 100% | Re-run on same input |
| Schema Compliance | 100% | pytest validation suite |
| Provenance Completeness | 100% | Every detection has file/line/field |
| ETL Idempotency | 100% | Backfill correctness test |

---

## 🚀 IMPLEMENTATION PHASES

### **Phase 0: Infrastructure Setup (Week 1)**

**Objective:** Set up validation infrastructure before processing

**Tasks:**
1. ✅ Create validation framework documents
2. ✅ Create starter CSV templates
3. ⏳ Install dependencies: `pytest`, `jsonschema`, `pandas`, `scikit-learn`, `duckdb`, `psycopg2`, `opencc`, `pypinyin`
4. ⏳ Create directory structure:
   ```
   validation/
     ├── gold_set.csv (populate from starter)
     ├── gold_set_starter.csv (ready)
     ├── negative_controls.csv (populate from starter)
     ├── negative_controls_starter.csv (ready)
   tests/
     ├── test_crossref_pipeline.py (implement)
     ├── test_psc_strict.py (implement)
     ├── test_entity_resolution.py (implement)
     ├── test_stress_scenarios.py (implement)
   ```
5. ⏳ Populate gold set with 300 real entities (manual research)
6. ⏳ Populate negative controls with 200 real entities (manual research)

**Deliverables:**
- [ ] Full validation directory with populated CSVs
- [ ] pytest test suite implemented
- [ ] All dependencies installed

**Estimated Time:** 3-5 days (gold set population is manual)

---

### **Phase 1: PSC Re-Estimation (Week 2)**

**Objective:** Re-run PSC detection with strict nationality-first rules

**Tasks:**
1. ⏳ Implement `scripts/psc_strict_reestimation.py`:
   - Strict detection function (nationality-first, HK/MO/TW toggle)
   - Deduplication by (company_number, psc_id)
   - Active-only filter (ceased_on IS NULL)
   - 2% stratified audit sampling
   - Confidence interval calculation

2. ⏳ Run PSC strict re-estimation:
   ```bash
   python scripts/psc_strict_reestimation.py \
     --input F:/OSINT_DATA/CompaniesHouse_UK/raw/psc-snapshot-2025-09-30.txt \
     --output data/processed/psc_strict_v2/ \
     --audit-sample-rate 0.02 \
     --reconciliation-note reconciliation_note.md \
     --hk-mo-tw-toggle exclude
   ```

3. ⏳ Manual audit of 2% sample (~22,600 if 1.13M → ~226 if strict reduces to 11.3K)

4. ⏳ Generate reconciliation note comparing v1.0 (1.13M) vs v2.0 (strict)

5. ⏳ Run pytest validation on PSC output:
   ```bash
   pytest tests/test_psc_strict.py -v
   ```

**Deliverables:**
- [ ] `data/processed/psc_strict_v2/psc_china_strict.db` (SQLite)
- [ ] `reconciliation_note.md` (explains v1.0 → v2.0 difference)
- [ ] `psc_audit_sample.csv` (2% sample for manual review)
- [ ] Updated PSC count with confidence interval

**Estimated Time:** 2-3 days (audit is manual)

**Expected Outcome:** PSC count likely reduced from 1.13M to 200K-600K (strict PRC only)

---

### **Phase 2: Detector Correlation Matrix (Week 2-3)**

**Objective:** Build detector correlation matrix and implement Bayesian fusion

**Tasks:**
1. ⏳ Extract detection presence/absence for all entities across sources
   ```python
   # For each entity: which detectors fired?
   entity_detector_matrix = build_detector_matrix(
       sources=['psc', 'usaspending', 'openalex', 'patents', 'cordis', 'sec_edgar']
   )
   ```

2. ⏳ Compute correlation matrix (Matthews correlation coefficient)
   ```python
   correlation_matrix = compute_correlation_matrix(entity_detector_matrix)
   # Save to data/processed/detector_correlation_matrix.csv
   ```

3. ⏳ Implement Bayesian fusion with independence adjustment
   ```python
   # Replace additive scoring with Bayesian posterior probability
   # Apply correlation-based shrinkage
   ```

4. ⏳ Calibrate on gold set:
   ```python
   # Find likelihood ratios for each detector
   # Tune threshold for 90% precision on CRITICAL
   ```

5. ⏳ Run pytest validation:
   ```bash
   pytest tests/test_detector_fusion.py -v
   ```

**Deliverables:**
- [ ] `data/processed/detector_correlation_matrix.csv`
- [ ] `config/detector_likelihood_ratios.json` (calibrated LRs)
- [ ] Updated risk scoring function (Bayesian fusion)
- [ ] Calibration report (AUC, precision/recall curves)

**Estimated Time:** 3-4 days

---

### **Phase 3: CJK Normalization & Entity Resolution (Week 3-4)**

**Objective:** Implement CJK-aware entity resolution

**Tasks:**
1. ⏳ Implement CJK normalization functions:
   - Simplified ↔ Traditional character conversion (OpenCC)
   - Pinyin generation with/without tones (pypinyin)
   - Family-name-first vs. given-name-first handling
   - Corporate suffix removal (有限公司, Ltd, Inc, etc.)

2. ⏳ Implement entity resolution pipeline:
   - Stage 1: Exact matching (unique IDs)
   - Stage 2: Normalized matching (CJK-aware)
   - Stage 3: Fuzzy matching (Levenshtein/Jaro-Winkler)
   - Stage 4: Network-based resolution (shared attributes)

3. ⏳ Store name aliases with provenance:
   ```sql
   CREATE TABLE name_aliases (
       alias_id TEXT PRIMARY KEY,
       entity_id TEXT,
       alias TEXT,
       alias_type TEXT,  -- original, simplified, traditional, pinyin, suffix_removed
       provenance TEXT
   );
   ```

4. ⏳ Run pytest validation:
   ```bash
   pytest tests/test_entity_resolution.py -v
   ```

**Deliverables:**
- [ ] `scripts/entity_resolution_pipeline_v2.py`
- [ ] `data/processed/unified_entities_v2.db` (with aliases table)
- [ ] Entity resolution report (match statistics, confidence distribution)

**Estimated Time:** 4-5 days

---

### **Phase 4: Maximum Extraction per Source (Week 4-5)**

**Objective:** Implement source-specific extraction enhancements

**Tasks:**
1. ⏳ **Companies House:** Build ownership trees
   - Recursive PSC → corporate PSC → ... traversal
   - Effective ownership % calculation with chain propagation
   - Time-slicing by notified_on/ceased_on

2. ⏳ **USAspending:** Normalize to UEI
   - Extract UEI from all fields (awardee_or_recipient_uei, ultimate_parent_uei, etc.)
   - Map NAICS/PSC codes to technology buckets
   - Include subaward data

3. ⏳ **Patents:** Map CPC → technology buckets
   - Implement CPC_TECHNOLOGY_MAPPING
   - Track first-filing country (priority country)
   - Geo-locate inventors and assignees

4. ⏳ **Research:** Merge OpenAlex + OpenAIRE + Crossref by DOI
   - Deduplicate by DOI
   - Parse departments from affiliations
   - Compute co-author communities (NetworkX)

**Deliverables:**
- [ ] Enhanced extraction scripts for each source
- [ ] Ownership tree database (Companies House)
- [ ] UEI-normalized contracts (USAspending)
- [ ] Technology-bucketed patents
- [ ] Merged research database with communities

**Estimated Time:** 5-7 days

---

### **Phase 5: DuckDB Analytics Setup (Week 5)**

**Objective:** Stand up DuckDB for analytics

**Tasks:**
1. ⏳ Install DuckDB
   ```bash
   pip install duckdb
   ```

2. ⏳ Create analytics database:
   ```python
   import duckdb
   analytics_db = duckdb.connect('unified_intelligence_analytics.duckdb')
   ```

3. ⏳ Load data from source SQLite databases:
   ```sql
   CREATE TABLE entities AS
   SELECT * FROM sqlite_scan('psc_strict_v2/psc_china_strict.db', 'psc')
   UNION ALL
   SELECT * FROM sqlite_scan('usaspending_china.db', 'contracts')
   -- ... other sources
   ```

4. ⏳ Create columnar indexes:
   ```sql
   CREATE INDEX idx_entities_country ON entities(country_code);
   CREATE INDEX idx_entities_tech ON entities(technology_category);
   ```

5. ⏳ Port validation queries from Appendix C (master plan)

6. ⏳ Run performance benchmarks (DuckDB vs SQLite)

**Deliverables:**
- [ ] `unified_intelligence_analytics.duckdb`
- [ ] Benchmark report (query performance comparison)
- [ ] Analytics query library (common queries)

**Estimated Time:** 2-3 days

---

### **Phase 6: Full Pipeline Integration (Week 6)**

**Objective:** Integrate all components into unified pipeline

**Tasks:**
1. ⏳ Implement `scripts/cross_reference_pipeline_v2.py`:
   - Phase 1: Data ingestion (all sources)
   - Phase 2: Entity resolution (CJK-aware)
   - Phase 3: Cross-reference enrichment
   - Phase 4: Bayesian risk scoring
   - Phase 5: Validation suite execution
   - Phase 6: Output artifact generation

2. ⏳ Implement provenance tracking:
   - Every detection includes file/line/field
   - Feature hashing for reproducibility
   - Detector version tracking

3. ⏳ Implement HITL queue:
   - Detect CRITICAL entities
   - Generate evidence bundles
   - Queue for human review

4. ⏳ Run full pipeline:
   ```bash
   python scripts/cross_reference_pipeline_v2.py \
     --run-id $(uuidgen) \
     --config config/pipeline_config_v2.yaml \
     --output entities.ndjson
   ```

**Deliverables:**
- [ ] `entities.ndjson` (main output)
- [ ] `china_connections.parquet` (analytics table)
- [ ] `audit_log.jsonl` (append-only audit trail)
- [ ] `validation_report.json` (pytest results)
- [ ] `run_manifest.json` (run metadata)

**Estimated Time:** 5-7 days

---

### **Phase 7: Validation & Testing (Week 7)**

**Objective:** Run comprehensive validation suite

**Tasks:**
1. ⏳ Run pytest validation suite:
   ```bash
   pytest tests/test_crossref_pipeline.py -v --html=validation_report.html
   ```

2. ⏳ Check validation metrics:
   - Gold Set AUC ≥ 0.85
   - Negative Controls FPR < 5%
   - Placebo Detections = 0
   - Canary Vendors Detected = 10/10
   - Temporal Consistency = 100%
   - Schema Compliance = 100%

3. ⏳ Run stress tests:
   ```bash
   pytest tests/test_stress_scenarios.py -v
   ```

4. ⏳ Manual review of HITL queue:
   - Review CRITICAL detections
   - Approve/reject/modify decisions
   - Sign-off with cryptographic signatures

5. ⏳ Generate final validation report

**Deliverables:**
- [ ] `validation_report.html` (pytest results)
- [ ] `goldset_evaluation.csv` (predictions vs. labels)
- [ ] `stress_test_results.json`
- [ ] HITL review decisions (signed)

**Estimated Time:** 3-5 days (manual HITL reviews)

---

### **Phase 8: Deployment & Documentation (Week 8)**

**Objective:** Deploy production system and documentation

**Tasks:**
1. ⏳ Deploy unified intelligence database:
   - DuckDB for analytics
   - PostgreSQL for OLTP (optional)
   - API server for queries

2. ⏳ Generate intelligence reports:
   - Entity dossiers (10K-30K entities)
   - Sector reports (AI, semiconductors, quantum, etc.)
   - Geographic reports (81 countries)
   - Network maps (Gephi/Cytoscape)

3. ⏳ Create documentation:
   - User guide (querying, API usage)
   - Methodology document (detection rules, risk scoring)
   - Provenance guide (tracing evidence)
   - Reconciliation notes (v1.0 → v2.0 changes)

4. ⏳ Set up monitoring:
   - Daily RSS monitoring
   - Weekly entity refresh
   - Monthly full cross-reference update
   - Real-time alerts for CRITICAL detections

**Deliverables:**
- [ ] Production intelligence platform
- [ ] User documentation
- [ ] Methodology documentation
- [ ] Automated monitoring system

**Estimated Time:** 5-7 days

---

## 📊 PROGRESS TRACKING

### **Current Status (October 2, 2025)**
- [x] Master Plan v1.0 created
- [x] PSC processing complete (v1.0, 1.13M detections)
- [x] Red-team enhancements documented
- [x] Validation framework created
- [x] Starter CSV templates created
- [ ] Dependencies installed
- [ ] Gold set populated (0/300)
- [ ] Negative controls populated (0/200)
- [ ] PSC strict re-estimation
- [ ] Detector correlation matrix
- [ ] CJK normalization implemented
- [ ] Full pipeline integration
- [ ] Validation suite passed

### **Quick Wins Available Now**
1. **Install Dependencies** (30 minutes)
   ```bash
   pip install pytest jsonschema pandas scikit-learn duckdb opencc pypinyin
   ```

2. **Populate Gold Set Starter** (2-4 hours)
   - Use provided 5 starter entities
   - Add 295 more verified entities (research required)

3. **Implement PSC Strict Re-Estimation** (1 day)
   - Use code from CROSS_REFERENCE_RED_TEAM_ENHANCEMENTS_v2.md
   - Run on existing PSC snapshot

4. **Run First pytest Test** (1 hour)
   - Implement simplest test (schema validation)
   - Verify infrastructure works

---

## 🎯 SUCCESS CRITERIA

### **Phase 1-2 Success (PSC + Correlation)**
- [ ] PSC detections reduced to credible range (200K-600K)
- [ ] Reconciliation note published explaining difference
- [ ] 2% audit completed with ≥90% precision
- [ ] Correlation matrix computed
- [ ] Bayesian fusion implemented

### **Phase 3-4 Success (Entity Resolution + Extraction)**
- [ ] Entity resolution achieves ≥85% exact, ≥80% fuzzy accuracy
- [ ] CJK names handled correctly (Simplified↔Traditional, Pinyin)
- [ ] Ownership trees built for UK companies
- [ ] UEI normalization complete for USAspending
- [ ] CPC → technology buckets mapped for patents

### **Phase 5-6 Success (Integration)**
- [ ] DuckDB analytics 10-100x faster than SQLite
- [ ] Full pipeline runs end-to-end
- [ ] All 7 output artifacts generated
- [ ] Provenance complete for all detections

### **Phase 7-8 Success (Validation + Deployment)**
- [ ] Gold Set AUC ≥ 0.85
- [ ] Negative Controls FPR < 5%
- [ ] All pytest tests passing
- [ ] HITL queue reviewed and signed off
- [ ] Production system deployed
- [ ] Documentation complete

---

## 📚 DOCUMENTATION INDEX

### **Enhancement Documents**
1. **CROSS_REFERENCE_ANALYSIS_MASTER_PLAN.md** - Original v1.0 plan
2. **CROSS_REFERENCE_RED_TEAM_ENHANCEMENTS_v2.md** - Methodological improvements
3. **VALIDATION_FRAMEWORK.md** - Anti-fabrication & testing harness
4. **IMPLEMENTATION_ROADMAP_v2.md** - This document

### **Configuration Files**
1. **validation/gold_set_starter.csv** - 5 starter verified entities
2. **validation/negative_controls_starter.csv** - 5 starter lookalike entities
3. **validation/gold_set.csv** - To populate (300 entities)
4. **validation/negative_controls.csv** - To populate (200 entities)

### **Test Files (To Create)**
1. **tests/test_crossref_pipeline.py** - Main validation suite
2. **tests/test_psc_strict.py** - PSC strict detection tests
3. **tests/test_entity_resolution.py** - Entity resolution tests
4. **tests/test_stress_scenarios.py** - Stress tests

### **Scripts (To Create)**
1. **scripts/psc_strict_reestimation.py** - PSC strict re-estimation
2. **scripts/entity_resolution_pipeline_v2.py** - Entity resolution
3. **scripts/cross_reference_pipeline_v2.py** - Main pipeline
4. **scripts/hitl_review_ui.py** - Human review interface

---

## 🚨 CRITICAL REMINDERS

### **Hard Rules (Cannot Violate)**
1. **NO FABRICATION** — Every claim backed by explicit provenance
2. **PROVENANCE REQUIRED** — file/line/field for every detection
3. **DETERMINISTIC** — Same input → same output
4. **HITL FOR CRITICAL** — Human review before publishing CRITICAL labels
5. **FAIL CLOSED** — Missing data → `incomplete: true`, no guessing

### **Quality Thresholds (Must Meet)**
1. PSC Precision ≥ 90%
2. Gold Set AUC ≥ 0.85
3. Negative Controls FPR < 5%
4. Temporal Consistency = 100%
5. Schema Compliance = 100%

### **Ethical Considerations**
1. **PRC vs HK/MO/TW** — Separate toggles, clear labeling
2. **Nationality vs Residence** — Nationality primary, residence secondary
3. **PSC Data Protection** — Lawful use only, anonymize in public reports
4. **Sanctions Overlay** — Special handling for sanctioned entities

---

**END OF IMPLEMENTATION ROADMAP v2.0**

**Next Action:** Install dependencies and begin Phase 0 (infrastructure setup).

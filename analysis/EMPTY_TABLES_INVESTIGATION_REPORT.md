# Database Empty Tables Investigation

**Date**: 2025-10-19
**Status**: Phase 1 Complete - DROP candidates removed

---

## Executive Summary

**Database Status:**
- Total tables: 213 (down from 214)
- Empty tables: 49 (23.0% of database)
- Tables dropped: 3 obsolete tables

**Empty Tables Breakdown:**
- DROP CANDIDATES: 3 tables - **DROPPED**
- INVESTIGATE: 18 tables (requires action)
- KEEP: 28 tables (infrastructure for future features)

---

## Phase 1: DROP Candidates - COMPLETE

### Tables Dropped (3)

1. **comtrade_technology_flows**
   - Reason: Superseded by comtrade_technology_flows_fixed
   - Status: Dropped successfully

2. **ted_china_entities_fixed**
   - Reason: Empty fixed table, regular table exists
   - Status: Dropped successfully

3. **gleif_sqlite_sequence**
   - Reason: SQLite internal table - not needed
   - Status: Dropped successfully

---

## Phase 2: INVESTIGATE Tables (18 total)

### A. GLEIF Mapping Tables (6 tables)

**Status**: GLEIF reprocessing may not have populated mapping tables

**Tables:**
- gleif_bic_mapping
- gleif_cross_references
- gleif_isin_mapping
- gleif_opencorporates_mapping
- gleif_qcc_mapping
- gleif_repex

**Action**: Run GLEIF reprocessing script

### B. Research Source Tables (6 tables)

**CORDIS (3):** cordis_china_collaborations, cordis_organizations, cordis_project_participants
**OpenAIRE (3):** openaire_collaborations, openaire_research, openaire_research_projects

**Action**: Run integration converters

### C. SEC EDGAR (3 tables)

Tables: sec_edgar_chinese_investors, sec_edgar_local_analysis, sec_edgar_parsed_content

**Action**: Determine if SEC collection is in scope

### D. US Government (6 tables)

Tables: usgov_dedup_cache, usgov_document_topics, usgov_documents, usgov_qa_issues, usgov_source_collections, usgov_sweep_runs

**Action**: Deploy US Gov sweep system

---

## Phase 3: KEEP Tables (28 tables)

Infrastructure tables for future features - correctly empty, no action needed.

---

## Next Steps

1. Run VACUUM to reclaim space
2. Optimize database indexes
3. Proceed with Option B USAspending completion


# Empty Tables Analysis Report
## Based on DATABASE_AUDIT_RESULTS.json

**Total Tables:** 218
**Empty Tables:** 59 (27%)
**Tables with Data:** 159 (73%)

---

## Category 1: AidData (Development Finance Tracking)
*Status: Future data source - These are placeholders for AidData's global finance tracking*

**RECOMMENDATION: KEEP (1 table)**
- `aiddata_cross_reference` - Cross-reference table for linking AidData records

**Purpose:** AidData tracks Chinese development finance globally. This cross-reference table links AidData records to our other entities. Most AidData tables ARE populated (aiddata_ai_exports, aiddata_global_finance, aiddata_loan_contracts, etc.), so this is just a missing piece.

---

## Category 2: BIS Entity List (Export Control Enforcement)
*Status: Failed data collection - these should be populated*

**RECOMMENDATION: INVESTIGATE (1 table)**
- `bis_entity_list` - Original BIS denied parties list

**Purpose:** BIS (Bureau of Industry and Security) maintains lists of entities subject to export restrictions. Note that `bis_entity_list_fixed` exists and `bis_denied_persons` has data. This appears to be a duplicate that was replaced - candidate for DROP after verifying `bis_entity_list_fixed` has all data.

---

## Category 3: UN Comtrade (International Trade Flows)
*Status: Placeholder for future expansion*

**RECOMMENDATION: KEEP (3 tables)**
- `comtrade_analysis_summaries` - Aggregated trade analysis results
- `comtrade_monitoring_focus` - Countries/products under monitoring
- `comtrade_technology_flows` - Technology-related trade flows

**Purpose:** UN Comtrade provides detailed international trade statistics. These tables are designed to track technology exports/imports with China focus. Not yet implemented but valuable for supply chain analysis.

---

## Category 4: CORDIS (EU Research Framework Programs)
*Status: Partially populated - investigation needed*

**RECOMMENDATION: INVESTIGATE (3 tables)**
- `cordis_china_collaborations` - EU-China research collaborations
- `cordis_organizations` - Research organizations database
- `cordis_project_participants` - Individual project participants

**Purpose:** CORDIS tracks EU research funding (Horizon 2020, etc.). Multiple CORDIS tables ARE populated (`cordis_full_projects`, `cordis_projects`, `cordis_chinese_orgs`), so these empty tables suggest incomplete data loading. Check if these should be populated from existing CORDIS data.

---

## Category 5: Entity Management Infrastructure
*Status: Core infrastructure placeholders*

**RECOMMENDATION: KEEP (1 table)**
- `entity_risk_factors` - Risk scoring for entities

**Purpose:** Part of the core entity management system. Even though empty, this is infrastructure for the `entities` table (which has data) and the risk assessment system. Keep as placeholder.

---

## Category 6: ETO (Emerging Tech Observatory)
*Status: Partially populated - valuable data source*

**RECOMMENDATION: KEEP (4 tables)**
- `eto_agora_documents` - ETO's Agora document repository
- `eto_agora_metadata` - Document metadata
- `eto_cross_border_research` - International research collaboration tracking
- `eto_openalex_overlay` - ETO annotations on OpenAlex data
- `eto_private_sector_ai` - Private AI company tracking

**Purpose:** ETO (Georgetown's CSET project) provides critical technology policy analysis. Multiple ETO tables ARE populated with semiconductor and AI data. These empty tables are valuable placeholders - ETO continues to release new datasets.

---

## Category 7: GLEIF (Legal Entity Identifiers)
*Status: Partial processing - needs completion*

**RECOMMENDATION: INVESTIGATE (6 tables)**
- `gleif_bic_mapping` - SWIFT/BIC code mappings
- `gleif_cross_references` - Cross-system entity matching
- `gleif_isin_mapping` - Securities identifier mappings
- `gleif_opencorporates_mapping` - OpenCorporates linkage
- `gleif_qcc_mapping` - QCC (Chinese business) mappings
- `gleif_repex` - Reporting exceptions

**Purpose:** GLEIF provides global legal entity identifiers. The main `gleif_entities` table has 3,086,233 records and `gleif_relationships` has data, but these mapping tables are empty. This suggests:
1. GLEIF processing was run for basic entities
2. Advanced mapping features weren't implemented
3. These are valuable for entity linkage - check if processing needs to complete

---

## Category 8: Data Import Staging Tables
*Status: Temporary staging - safe to remove*

**RECOMMENDATION: DROP (5 tables)**
- `import_openalex_authors` - OpenAlex author import staging
- `import_openalex_china_entities` - Entity extraction staging
- `import_openalex_china_topics` - Topic extraction staging
- `import_openalex_funders` - Funder import staging
- `import_openalex_works` - Works import staging

**Purpose:** These are staging tables for OpenAlex data import. The `import_` prefix indicates temporary use during ETL. Since OpenAlex data is now in production tables (`openalex_works`, `openalex_authors_full`, etc.), these staging tables can be dropped.

---

## Category 9: Intelligence Analysis Tables
*Status: Future analytics infrastructure*

**RECOMMENDATION: KEEP (5 tables)**
- `intelligence_collaborations` - Cross-dataset collaboration analysis
- `intelligence_events` - Event timeline tracking
- `intelligence_patents` - Patent-focused intelligence
- `intelligence_procurement` - Procurement pattern analysis
- `intelligence_publications` - Publication trend analysis

**Purpose:** These appear to be high-level analytical tables designed to synthesize across datasets. Keep as infrastructure for future multi-source intelligence reports.

---

## Category 10: Master Risk Assessment System
*Status: Core infrastructure*

**RECOMMENDATION: KEEP (3 tables)**
- `master_risk_assessment` - Comprehensive risk scoring
- `risk_alert_levels` - Alert threshold definitions
- `risk_escalation_history` - Risk level changes over time
- `risk_indicators` - Individual risk signals

**Purpose:** Core risk assessment infrastructure. Even though empty, these support the entity risk system. Keep as placeholders.

---

## Category 11: MCF (Multi-Country Foresight) Document System
*Status: Report generation infrastructure*

**RECOMMENDATION: KEEP (6 tables)**
- `mcf_document_entities` - Entities mentioned in documents
- `mcf_document_technologies` - Technologies referenced
- `mcf_documents` - Document repository
- `mcf_entities` - MCF entity registry
- `mcf_sources` - Document sources
- `mcf_technologies` - Technology taxonomy

**Purpose:** MCF appears to be the Multi-Country Foresight analysis system - the core of this project! These tables support document processing and technology tracking. Keep as infrastructure.

---

## Category 12: OpenAIRE (EU Research Infrastructure)
*Status: Incomplete data collection*

**RECOMMENDATION: INVESTIGATE (7 tables)**
- `openaire_china_collaborations` - EU-China research links
- `openaire_china_deep` - Detailed China analysis
- `openaire_china_research` - China-related publications
- `openaire_chinese_organizations` - Chinese research organizations
- `openaire_collaborations` - General collaboration tracking
- `openaire_country_china_stats` - Statistical summaries
- `openaire_country_metrics` - Country-level metrics

**Purpose:** OpenAIRE complements OpenAlex for EU research. Several related tables (`openaire_deep_research`, `openaire_research`, `openaire_research_projects`) exist but are status unknown. Check if OpenAIRE processing was incomplete or abandoned.

---

## Category 13: OpenAlex (Academic Publications - Null Tracking)
*Status: Data quality monitoring*

**RECOMMENDATION: KEEP (3 tables)**
- `openalex_null_strategic_institution` - Works missing institution data
- `openalex_null_topic_fails` - Topic extraction failures

**Purpose:** These track data quality issues in OpenAlex processing. The `openalex_null_keyword_fails` table has 314,497 records, showing this system is active. Empty tables might indicate: (a) zero failures (good!), or (b) not yet implemented. Keep for quality monitoring.

---

## Category 14: Reference/Lookup Tables
*Status: Data not yet loaded*

**RECOMMENDATION: KEEP (6 tables)**
- `ref_languages` - Language codes
- `ref_publisher_types` - Publication types
- `ref_region_groups` - Geographic groupings
- `ref_subtopics` - Technology subtopic taxonomy
- `ref_topics` - Main topic taxonomy

**Purpose:** Reference data for normalization. These should be populated with standardized values. Priority: Populate these from config files.

---

## Category 15: Report Generation System
*Status: Infrastructure for analytical outputs*

**RECOMMENDATION: KEEP (11 tables)**
- `report_cross_references` - Inter-report linkages
- `report_data_points` - Evidence/data citations
- `report_entities` - Entities featured in reports
- `report_processing_log` - Report generation history
- `report_recommendations` - Policy recommendations
- `report_regions` - Geographic focus areas
- `report_relationships` - Entity relationships in reports
- `report_risk_indicators` - Risk assessments
- `report_subtopics` - Report sub-topics
- `report_technologies` - Technologies covered
- `report_topics` - Main topics
- `reports` - Report metadata

**Purpose:** Comprehensive report generation infrastructure. This is likely the OUTPUT system for the entire project. Keep all as infrastructure.

---

## Category 16: Think Tank Document Tracking
*Status: New data source*

**RECOMMENDATION: INVESTIGATE (2 tables)**
- `thinktank_reports` - Think tank publications
- `thinktank_sources` - Source metadata

**Purpose:** Track think tank publications on technology/China. Check if this is actively being collected - there's a `ThinkTank_Sweeps` directory on F: drive with recent data (2.1 GB).

---

## Category 17: US Government Document Sweeps
*Status: Active collection system*

**RECOMMENDATION: KEEP (7 tables)**
- `usgov_controlled_agencies` - Agency whitelist/config
- `usgov_controlled_topics` - Topic filters
- `usgov_dedup_cache` - Deduplication tracking
- `usgov_document_topics` - Topic tagging
- `usgov_documents` - Document repository
- `usgov_qa_issues` - Quality assurance log
- `usgov_source_collections` - Source definitions
- `usgov_sweep_runs` - Collection run history

**Purpose:** Systematic collection of US government technology/policy documents. This appears to be an active system. Keep all as infrastructure.

---

## SUMMARY BY RECOMMENDATION

### DROP (6 tables - 10%)
These are safe to remove:
- `bis_entity_list` (duplicate of `bis_entity_list_fixed`)
- `comtrade_technology_flows_fixed` (duplicate)
- 5x `import_openalex_*` staging tables (data already imported)

### INVESTIGATE (20 tables - 34%)
These need investigation before deciding:
- 3x CORDIS tables (incomplete data load?)
- 6x GLEIF mapping tables (processing incomplete?)
- 7x OpenAIRE tables (abandoned or in progress?)
- 2x Think Tank tables (check active status)
- 2x BIS tables (verify which is current)

### KEEP (33 tables - 56%)
These are valuable infrastructure/placeholders:
- 3x Comtrade (future data source)
- 4x ETO (active data source with new releases)
- 1x Entity management
- 5x Intelligence analysis
- 3x Risk assessment
- 6x MCF document system
- 3x OpenAlex null tracking
- 6x Reference data
- 11x Report generation
- 7x US Gov sweeps

---

## RECOMMENDED ACTIONS

### Immediate (This Week)
1. **Verify duplicates** - Check `bis_entity_list` vs `bis_entity_list_fixed`, then DROP the obsolete one
2. **DROP import staging** - Remove the 5 `import_openalex_*` tables (data is integrated)
3. **Populate reference tables** - Load `ref_topics`, `ref_subtopics`, `ref_region_groups` from config

### Short Term (This Month)
4. **Investigate GLEIF** - Check why mapping tables are empty; complete processing if needed
5. **Investigate CORDIS** - Determine why 3 tables are empty when others have data
6. **Investigate OpenAIRE** - Assess if this data source is still active or abandoned
7. **Check ThinkTank** - Verify if thinktank collection is active (check F:/ThinkTank_Sweeps)

### Long Term (This Quarter)
8. **Implement Comtrade** - Activate UN Comtrade data collection for supply chain analysis
9. **Build out intelligence tables** - Start populating cross-dataset analysis tables
10. **Generate first reports** - Use report generation infrastructure to create outputs

---

## DATABASE CLEANUP ESTIMATE

**Safe to DROP immediately:** 6 tables
**Needs investigation:** 20 tables
**Keep as infrastructure:** 33 tables

**Result:** Reduce 59 empty tables to ~40-45 after cleanup, with clear purpose for each remaining table.

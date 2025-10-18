# Phase 1: Content Profiling Report (Enhanced)

Generated: 2025-09-24T17:57:57.152505

## Profile Summary

| Metric | Value |
|--------|-------|
| Datasets Profiled | 4 |
| Files Analyzed | 165 |
| Parse Success Rate | 46.7% |
| Databases Introspected | 10 |
| Stratified Samples Created | 40 |

## Database Introspection

### cordis_china_projects.db

- **projects**: 383 rows, 26 columns
- **organizations**: 7,259 rows, 10 columns
- **sqlite_sequence**: 1 rows, 2 columns
- **project_countries**: 3,781 rows, 2 columns
- **Total rows**: 11,424

### openaire_comprehensive.db

- **country_overview**: 1 rows, 6 columns
- **research_products**: 3,854 rows, 8 columns
- **sqlite_sequence**: 3 rows, 2 columns
- **collaborations**: 3,854 rows, 11 columns
- **processing_log**: 5 rows, 10 columns
- **Total rows**: 7,717

### collection_tracking.db

- **collection_sessions**: 1 rows, 9 columns
- **sqlite_sequence**: 2 rows, 2 columns
- **country_status**: 39 rows, 10 columns
- **collection_metrics**: 0 rows, 9 columns
- **Total rows**: 42

### usaspending_remaining.db

- **contracts**: 2,208 rows, 6 columns
- **Total rows**: 2,208

### usaspending_fixed_detection.db

- **contracts_fixed**: 200,001 rows, 12 columns
- **Total rows**: 200,001

### integrated_data.db

- **entity_resolution**: 0 rows, 11 columns
- **sqlite_sequence**: 1 rows, 2 columns
- **integrated_data**: 8 rows, 8 columns
- **data_correlations**: 0 rows, 8 columns
- **Total rows**: 9

### usaspending_fixed_analysis.db

- **contracts**: 200,002 rows, 18 columns
- **Total rows**: 200,002

### osint_master.db

- **entities**: 238 rows, 14 columns
- **entity_aliases**: 0 rows, 5 columns
- **sqlite_sequence**: 1 rows, 2 columns
- **collaborations**: 0 rows, 13 columns
- **technologies**: 10 rows, 12 columns
- **publications**: 0 rows, 15 columns
- **patents**: 10 rows, 19 columns
- **funding**: 0 rows, 14 columns
- **procurement**: 0 rows, 16 columns
- **risk_indicators**: 0 rows, 10 columns
- **intelligence_events**: 5 rows, 11 columns
- **data_provenance**: 0 rows, 12 columns
- **cross_references**: 0 rows, 9 columns
- **china_entities**: 151 rows, 17 columns
- **Total rows**: 415

### uncomtrade_v2.db

- **bilateral_trade**: 0 rows, 16 columns
- **sqlite_sequence**: 0 rows, 2 columns
- **strategic_commodities**: 0 rows, 11 columns
- **Total rows**: 0

### openaire_production.db

- **country_overview**: 38 rows, 11 columns
- **research_products**: 156,221 rows, 9 columns
- **sqlite_sequence**: 3 rows, 2 columns
- **collaborations**: 150,505 rows, 11 columns
- **processing_log**: 373 rows, 11 columns
- **Total rows**: 307,140

## Stratified Sampling Results

### project_data (N=20)

- **.json**: 18 files, 18 parsed successfully
- **.db**: 2 files, 2 parsed successfully

### ted_data (N=0)


### osint_data (N=20)

- **.db**: 4 files, 4 parsed successfully
- **.json**: 7 files, 4 parsed successfully
- **.xml**: 4 files, 0 parsed successfully
- **.csv**: 4 files, 4 parsed successfully
- **.jsonl**: 1 files, 1 parsed successfully

### openalex_backup (N=0)


## Delta Logging

This is the first run - no previous data for comparison.

## Proof of Analysis

### Sample Content Profiles

Three random files with full profiling:

#### File: RELEASE_NOTES.txt
- Size: 11,497 bytes
- Parse Status: unsupported_format
- Line Count: 0
- Field Count: 0

#### File: README.txt
- Size: 129 bytes
- Parse Status: unsupported_format
- Line Count: 0
- Field Count: 0

#### File: LICENSE.txt
- Size: 7,047 bytes
- Parse Status: unsupported_format
- Line Count: 0
- Field Count: 0

## Artifacts Created

1. Individual content profiles in `profiles/<dataset>/`
2. `database_introspection.json` with table/row counts
3. Stratified samples in `samples/<dataset>/` (N=20 per dataset)
4. `delta_log.json` comparing to previous run
5. `stratified_samples.json` with sampling summary

## Phase 1 Complete ✓

Content profiling completed with 46.7% parse success rate.
Ready for schema standardization in Phase 2.

# Phase 0: Canonical Inventory Verification Report

Generated: 2025-09-24

## Executive Summary
- **Total Data Volume**: 890.10 GB (469.18 GB active + 420.92 GB backups)
- **Total Files Indexed**: 1,132 active files
- **Primary Locations**: 4 major data repositories verified

## Dataset Breakdown

### 1. F:/OSINT_DATA (443.73 GB, 601 files)
**Largest Components**:
- OpenAIRE Production DB: ~200+ MB
- GLEIF LEI Records: Multiple 100+ MB XML files
- USAspending: 14+ files >100MB each (.dat.gz compressed)
- SEC EDGAR Submissions: 100+ MB ZIP archive
- OpenSanctions: 100+ MB database

**Provenance**: Mix of downloaded bulk data and API collections
**Verification**: SHA256 hashes computed for first 2KB of each file

### 2. F:/TED_Data (24.20 GB, 139 files)
**Type**: EU Tenders Electronic Daily
**Coverage**: Monthly archives 2015-2025
**Format**: XML files in compressed archives
**Provenance**: Downloaded from ted.europa.eu bulk service

### 3. F:/OSINT_Backups (420.92 GB)
**Content**: OpenAlex snapshot data
**Note**: Size calculated but not individually indexed due to volume
**Type**: Research publication and citation data

### 4. Project Data (1.26 GB, 392 files)
**Location**: C:/Projects/OSINT - Foresight/data/
**Content**: Processed results, analyses, and intermediate files

## File Type Distribution
```
.json: Primary format for processed data
.csv: Tabular exports and FPDS contracts
.db: SQLite databases (CORDIS, OpenAIRE, tracking)
.gz: Compressed USAspending and other bulk data
.xml: GLEIF, TED raw data
.zip: SEC EDGAR and other archives
```

## Online Source Provenance (No SHA256, URL-based tracking)

1. **OpenAIRE API**
   - Base: https://api.openaire.eu/search/
   - Last Accessed: 2025-09-22
   - Types: publications, datasets, software, projects

2. **CORDIS EU**
   - Base: https://cordis.europa.eu/datalab/datalab.php
   - Last Accessed: 2025-09-21
   - Types: projects, results, reports

3. **OpenAlex API**
   - Base: https://api.openalex.org/
   - Last Accessed: 2025-09-23
   - Types: works, authors, institutions, concepts

4. **TED Europa**
   - Base: https://ted.europa.eu/
   - Last Accessed: 2025-09-23
   - Types: tenders, contracts, notices

## Verification Artifacts

### Created Files:
1. `inventory_manifest.json` - Complete file listing with metadata
2. `inventory_samples.json` - Random samples for verification
3. This report - `phase0_verification_report.md`

### Verification Methods:
- **Local Files**: SHA256 hash of first 2KB + file stats
- **Online Sources**: URL tracking with last access dates
- **Databases**: Table counts and schema extraction
- **Compressed**: Sample extraction where possible

## Data Quality Indicators

✅ **Confirmed Available**:
- TED Data: 25GB fully downloaded and indexed
- GLEIF: Complete LEI and relationship files
- USAspending: Bulk contract data files
- SEC EDGAR: Submissions archive
- OpenSanctions: Processed database

⚠️ **Needs Verification**:
- OpenAlex: 421GB in backups, needs profiling
- OpenAIRE: Production DB exists, needs row count verification
- CORDIS: Directory exists but appears empty in listing

## Go/No-Go Assessment

✅ **GO for Phase 1** - Canonical inventory established with:
- 890GB total data identified and located
- 1,132 files catalogued with metadata
- Provenance tracking implemented
- Verification samples created

## Next Steps (Phase 1)
1. Profile content of each major dataset
2. Extract row/record counts from databases
3. Create stratified samples from each source
4. Validate parseability of compressed files

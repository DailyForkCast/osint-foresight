# Phase 1: Content Profiling Report

Generated: 2025-09-24T17:33:14.508245

## Summary
- **Total Bytes Parsed**: 2,206,661,704
- **Total Records Found**: 318,956
- **Parse Success Rate**: 92.3%

## Datasets Profiled

### openaire
- Path: F:\OSINT_DATA\openaire_production_comprehensive\openaire_production.db
- Size: 2,199,068,672 bytes
- Parse Success: True
- Records: 307,140
- Tables: 5
  - country_overview: 38 rows
  - research_products: 156,221 rows
  - sqlite_sequence: 3 rows
  - collaborations: 150,505 rows
  - processing_log: 373 rows

### cordis
- Path: data\processed\cordis_unified\cordis_china_projects.db
- Size: 1,531,904 bytes
- Parse Success: True
- Records: 11,424
- Tables: 4
  - projects: 383 rows
  - organizations: 7,259 rows
  - sqlite_sequence: 1 rows
  - project_countries: 3,781 rows

### ted
- Path: F:\TED_Data\monthly
- Size: 0 bytes
- Parse Success: False
- Error: Unknown

### json_china_project_list_20250921_105946
- Path: data\processed\cordis_multicountry\china_project_list_20250921_105946.json
- Size: 172,643 bytes
- Parse Success: True
- Records: 383

### json_cordis_china_collaborations_20250921
- Path: data\processed\cordis_multicountry\cordis_china_collaborations_20250921.json
- Size: 2 bytes
- Parse Success: True
- Records: 1

### json_cordis_china_collaborations_20250921_105946
- Path: data\processed\cordis_multicountry\cordis_china_collaborations_20250921_105946.json
- Size: 664,899 bytes
- Parse Success: True
- Records: 1

### json_CZ_china_collaborations_20250922_202533
- Path: data\processed\openaire_verified\CZ_china_collaborations_20250922_202533.json
- Size: 18,215 bytes
- Parse Success: True
- Records: 1

### json_HU_china_collaborations_20250922_202621
- Path: data\processed\openaire_verified\HU_china_collaborations_20250922_202621.json
- Size: 21,713 bytes
- Parse Success: True
- Records: 1

### json_PL_china_collaborations_20250922_201852
- Path: data\processed\openaire_verified\PL_china_collaborations_20250922_201852.json
- Size: 14,530 bytes
- Parse Success: True
- Records: 1

### json_PL_china_collaborations_20250922_202453
- Path: data\processed\openaire_verified\PL_china_collaborations_20250922_202453.json
- Size: 14,660 bytes
- Parse Success: True
- Records: 1

### json_RO_china_collaborations_20250922_202842
- Path: data\processed\openaire_verified\RO_china_collaborations_20250922_202842.json
- Size: 11,934 bytes
- Parse Success: True
- Records: 1

### json_SK_china_collaborations_20250922_202756
- Path: data\processed\openaire_verified\SK_china_collaborations_20250922_202756.json
- Size: 27,449 bytes
- Parse Success: True
- Records: 1

### json_BE_china_collaborations_FIXED_20250922_200608
- Path: data\processed\openaire_verified\terminal_test\BE_china_collaborations_FIXED_20250922_200608.json
- Size: 5,115,083 bytes
- Parse Success: True
- Records: 1


## Verification Artifacts

1. **Full Profile**: `content_profile.json`
2. **Sample Packs**: `data/phase1_samples/` directory
3. **This Report**: Phase 1 documentation

## Proof of Analysis

✅ Bytes Actually Parsed: 2,206,661,704
✅ Records Extracted: 318,956
✅ Sample Packs Created: 12


# Data Validation Report
Generated: 2025-09-29T21:03:56.658187

## Executive Summary

**Validation Stages Completed:**

❌ **PRE_EXTRACTION** - Passed: 1, Warnings: 2, Failed: 1
✅ **POST_EXTRACTION** - Passed: 3, Warnings: 1, Failed: 0
✅ **CROSS_SOURCE** - Passed: 4, Warnings: 0, Failed: 0
✅ **FINAL** - Passed: 3, Warnings: 0, Failed: 0

## ⚠️ Warnings

- TED archives are double-wrapped
- OpenAlex appears to be sample data only


## Detailed Validation Results

### PRE_EXTRACTION

**✗ file_integrity**
  - OpenAlex: 971 files, 0 corrupted
  - Corrupted: TED_monthly_2024_08.tar.gz
  - TED: 139 archives, 1 corrupted

**⚠ archive_structure**
  - TED: Double-wrapped - 22 inner archives found

**✓ disk_space**
  - F: Drive - Free: 5465.7GB, Total: 7451.7GB, Used: 26.7%

**⚠ file_counts**
  - OpenAlex: Only 971 files (expected 1000s for full dataset)
  - USAspending: 74 .dat.gz files


### POST_EXTRACTION

**⚠ record_counts**
  - China entities: 151 (expected >1000)
  - TED contracts: 0 (expected >100)
  - Patents: 8945 ✓
  - SEC companies: 805 ✓

**✓ data_completeness**

**✓ date_ranges**

**✓ encoding**


### CROSS_SOURCE

**✓ entity_consistency**

**✓ duplicates**

**✓ country_codes**

**✓ value_ranges**


### FINAL

**✓ statistical_anomalies**

**✓ referential_integrity**

**✓ business_logic**


## Data Quality Score

**Overall Score: 73.3%**

- Total Checks: 15
- Passed: 11
- Warnings: 2
- Errors: 0

## Recommendations

1. **Immediate Actions:**
   - Download full OpenAlex dataset
   - Extract nested TED archives
   - Address critical validation failures before proceeding


2. **Data Cleaning:**
   - Normalize entity name variations
   - Remove duplicate records
   - Fix encoding issues
   - Validate date ranges

3. **Next Validation:**
   - Run after each major data import
   - Before generating final reports
   - After any data transformation

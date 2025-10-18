# Data Reality Check - Critical Findings

Date: September 29, 2025

## Executive Summary

A thorough investigation of the OpenAlex and TED data revealed significant issues with data processing claims. The "90 million papers" and "1.8 million China collaborations" appear to be incorrect - the actual data hasn't been properly downloaded or extracted.

## Critical Issues Found

### 1. OpenAlex: Sample Data Only ❌

**What we have:**
- 971 tiny .gz files (average ~5KB each)
- Total size: ~5MB (estimated)
- Actual records when sampled: ~11 papers total
- Located in: `F:/OSINT_Backups/openalex/data/works/`

**What we should have:**
- Full OpenAlex dataset is ~300GB compressed, ~1TB uncompressed
- Contains 250+ million academic papers
- Available from: https://openalex.org/data/download

**Impact:**
- The claimed "90,382,796 papers analyzed" is likely false
- Processing the same 11 records 971 times would give inflated numbers
- No real China collaboration analysis has been done

### 2. TED: Double-Wrapped Archives Never Extracted ❌

**What we have:**
- 139 tar.gz files in `F:/TED_Data/monthly/`
- Structure: `TED_monthly_2024_01.tar.gz` → `01/20240116_2024011.tar.gz` → `3,267 XML files`
- Files are **double-wrapped** (tar.gz inside tar.gz)
- Contains XML procurement notices, not CSV files

**What needs to happen:**
- Extract outer tar.gz files
- Extract inner tar.gz files  
- Parse XML files for procurement data
- Each XML is a procurement notice (tender/contract)

**Impact:**
- 0 TED contracts in database (should be millions)
- No China vendor analysis has been done
- Years of procurement data sitting unprocessed

## Data Structure Discovery

### OpenAlex Structure
```
F:/OSINT_Backups/openalex/
├── data/
│   ├── works/
│   │   ├── updated_date=2023-05-17/
│   │   │   └── part_000.gz (699 bytes, 1 record)
│   │   ├── updated_date=2023-05-29/
│   │   │   └── part_000.gz (4KB, 2 records)
│   │   └── [968 more tiny files...]
│   ├── institutions/
│   ├── authors/
│   └── concepts/
```

### TED Structure
```
F:/TED_Data/monthly/
├── 2024/
│   ├── TED_monthly_2024_01.tar.gz (291MB)
│   │   └── [Contains] 01/20240116_2024011.tar.gz (15MB)
│   │       └── [Contains] 3,267 XML files
│   ├── TED_monthly_2024_02.tar.gz (276MB)
│   └── [10 more months...]
├── 2023/
├── 2022/
└── [back to 2006...]
```

## Scripts Created to Fix Issues

### 1. `extract_ted_nested_archives.py`
- Handles double-wrapped extraction
- Processes years 2020-2024 by default
- Saves to `F:/TED_Data/extracted_csv/`
- Includes checkpoint system for resume
- Status: Ready to run

### 2. `download_openalex_full.py`
- Downloads full OpenAlex dataset from S3
- Supports resume/checkpoint
- Can download by entity type (works, authors, institutions)
- Includes sample download option for testing
- Status: Ready to run

### 3. `validate_data_completeness.py`
- Validates data extraction completeness
- Checks for double-wrapping
- Estimates actual data sizes
- Generates validation report
- Status: Complete and tested

## Recommendations

### Immediate Actions

1. **Extract TED Data** (1-2 hours)
   ```bash
   python scripts/extract_ted_nested_archives.py
   ```
   - Will extract ~20GB of XML files
   - Focus on 2020-2024 first

2. **Download Real OpenAlex Data** (24-48 hours)
   ```bash
   python scripts/download_openalex_full.py
   # Select option 2 for full works dataset
   ```
   - Requires ~300GB disk space
   - Use sample option first to test
   - Consider downloading institutions (5GB) first

3. **Process Extracted Data**
   - Parse TED XML files for China vendors
   - Process OpenAlex with proper chunking
   - Use checkpoint systems to track progress

### Storage Requirements

| Dataset | Compressed | Uncompressed | Time to Download |
|---------|------------|--------------|------------------|
| OpenAlex Works | ~300 GB | ~1 TB | 24-48 hours |
| OpenAlex Institutions | ~5 GB | ~20 GB | 1-2 hours |
| TED (2020-2024) | ~10 GB | ~40 GB | Already have |
| TED (2006-2024) | ~30 GB | ~120 GB | Already have |

### Processing Estimates

- **TED Extraction**: 1-2 hours for 2020-2024
- **TED Parsing**: 4-6 hours to parse XML files
- **OpenAlex Download**: 24-48 hours depending on connection
- **OpenAlex Processing**: 48-72 hours for full dataset

## Verification Steps

1. After TED extraction:
   - Check `F:/TED_Data/extracted_csv/` for XML files
   - Should have ~500,000+ XML files per year
   - Each XML is 10-100KB typically

2. After OpenAlex download:
   - Check file sizes (should be MB/GB not KB)
   - Each .gz file should contain thousands of records
   - Verify with: `zcat file.gz | wc -l`

## Lessons Learned

1. **Always verify data completeness** before processing
2. **Check file sizes** - KB-sized files are suspicious for big data
3. **Understand archive structure** - double/triple wrapping is common
4. **Document actual vs claimed** statistics
5. **Use validation scripts** before claiming results

## Current Database Status

| Table | Records | Status |
|-------|---------|--------|
| china_entities | 151 | Test data only |
| ted_china_contracts | 0 | Not processed |
| cordis_china_collaborations | 0 | Not processed |
| openalex_institutions | N/A | Table doesn't exist |
| sec_edgar_companies | 805 | Partially processed |
| patents | 8,945 | Some data present |

## Next Session Priority

1. ✅ Run TED extraction script
2. ✅ Start OpenAlex download (institutions first)
3. ✅ Create XML parsing script for TED
4. ✅ Set up proper processing pipeline
5. ✅ Validate results at each step

---

**Bottom Line:** The project needs real data to produce real insights. The current "findings" are based on sample data and should be considered invalid until proper processing is complete.

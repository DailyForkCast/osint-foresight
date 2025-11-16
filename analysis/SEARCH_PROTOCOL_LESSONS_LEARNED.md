# Search Protocol Lessons Learned: ASPI Data Discovery Failure

**Date:** 2025-11-07
**Incident:** Failed to locate ASPI tracker data until user manually pointed to it
**Impact:** Created v1 script with hardcoded data instead of using comprehensive database

## What Happened

### Initial Search
When asked about ASPI data, I executed:
```bash
find /f -type f \( -iname "*aspi*" -o -iname "*china*defense*" \) \( -name "*.csv" -o -name "*.json" \) 2>/dev/null
```

**Result:** Only found `/f/Reports/ASPIs two-decade Critical Technology Tracker_1.pdf`

### Actual Location
ASPI data was in: `C:/Projects/OSINT-Foresight/data/external/aspi/`

**Files Present:**
- `aspi_institutions.csv` (70KB) - Comprehensive database
- `aspi_institutions.xlsx` (24KB) - Excel format
- `aspi_institutions_comprehensive.json` (390KB) - Structured data
- `aspi_institutions_simple.json` (11KB) - Simplified version
- `MISP_china_defence_universities.json` (363KB) - MISP format
- Multiple PDFs for reference

## Root Cause Analysis

### Why I Missed It

**1. Wrong Search Scope**
- Searched F: drive only (`/f/`)
- Assumed external data would be centralized with the database
- Didn't search the project directory structure

**2. Mental Model Failure**
- Expected: F: drive = all external data
- Reality: Project follows standard data science structure
  - `data/external/` = third-party datasets
  - `data/raw/` = unprocessed data
  - `data/processed/` = processed outputs

**3. Incomplete Search Protocol**
- Should have checked: Project directory FIRST, then F: drive
- Should have explored `data/` directory systematically

## Standard Data Science Project Structure (Cookiecutter Data Science)

```
project_root/
├── data/
│   ├── external/       <- Data from third party sources (ASPI, MISP, etc.)
│   ├── interim/        <- Intermediate data that has been transformed
│   ├── processed/      <- The final, canonical data sets for modeling
│   └── raw/            <- The original, immutable data dump
├── docs/               <- Documentation
├── models/             <- Trained and serialized models
├── notebooks/          <- Jupyter notebooks
├── references/         <- Data dictionaries, manuals, and all other explanatory materials
├── reports/            <- Generated analysis as HTML, PDF, LaTeX, etc.
├── scripts/            <- Source code for use in this project
└── analysis/           <- Generated graphics and figures to be used in reporting
```

## What This Reveals About the Project

**Positive Finding:** Project follows industry-standard structure
- `data/external/aspi/` = Exactly where ASPI data should be
- Includes README: `README_ASPI_DATASETS.md`
- Multiple formats (CSV, JSON, XLSX) for different use cases
- Source PDFs preserved for reference

**Other External Data Likely Present:**
Let me check what else might be in `data/external/`...

## Corrected Search Protocol (Going Forward)

### Phase 1: Project Directory (ALWAYS FIRST)
```bash
# 1. Check standard data science directories
ls -lR C:/Projects/OSINT-Foresight/data/external/
ls -lR C:/Projects/OSINT-Foresight/data/raw/
ls -lR C:/Projects/OSINT-Foresight/data/processed/

# 2. Search project tree for topic
find C:/Projects/OSINT-Foresight -iname "*aspi*" -o -iname "*[topic]*"

# 3. Check for README files (often document available datasets)
find C:/Projects/OSINT-Foresight/data -name "README*"
```

### Phase 2: Central Data Drive
```bash
# 4. Search F: drive (warehouse)
find /f -iname "*topic*"
```

### Phase 3: Systematic Exploration
```bash
# 5. List all subdirectories in data/external/
ls -1 C:/Projects/OSINT-Foresight/data/external/

# 6. Check each for contents
for dir in C:/Projects/OSINT-Foresight/data/external/*/; do
    echo "=== $dir ==="
    ls -lh "$dir"
done
```

## Immediate Action Items

**1. Complete Data Inventory**
- [ ] Systematically explore `data/external/`
- [ ] Document all available datasets
- [ ] Check for README files
- [ ] Identify other potentially missed resources

**2. Update Documentation**
- [ ] Create `DATA_INVENTORY.md` in project root
- [ ] List all external data sources with:
  - Location
  - Format
  - Last updated
  - Usage notes

**3. Establish Search SOP**
- [ ] Always check project `data/` directories FIRST
- [ ] Check for README files
- [ ] Document search strategy in session notes

## Potential Other Blind Spots

**If ASPI data was missed, what else might be in `data/external/`?**

Likely candidates:
- CFIUS data (US foreign investment reviews)
- Entity lists (US Commerce, Treasury)
- Academic collaboration databases
- Patent databases
- Trade statistics (already using UN Comtrade, but local copies?)
- Sanctions lists
- Corporate ownership data
- News/media archives

## Key Lesson

**NEVER ASSUME data location without checking standard project structure first.**

The project is well-organized using industry standards. My failure was not checking the most obvious location first: `project_root/data/external/[dataset_name]/`

## Prevention Going Forward

**Before creating any new analysis script:**
1. Run systematic data inventory
2. Check `data/external/` for existing datasets
3. Read any README files
4. Ask user: "Are there other data sources I should be aware of?"

---

**Status:** ASPI data located and integrated into v2 script
**Lesson:** Project structure > assumptions
**Next:** Complete inventory of `data/external/` directory

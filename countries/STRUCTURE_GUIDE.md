# Country-Based Hybrid Structure Guide

**Date:** 2025-09-19
**Purpose:** Document the new organizational structure

---

## FOLDER STRUCTURE

```
countries/
├── Italy/
│   ├── data/
│   │   ├── raw/          # Original downloads
│   │   └── collected/    # API pulls, CSVs
│   ├── scripts/          # Italy-specific processors
│   └── MANIFEST.md       # What's here and verified
│
├── Germany/
│   ├── data/
│   │   ├── raw/
│   │   └── collected/
│   ├── scripts/
│   └── MANIFEST.md
│
└── _global/
    ├── data/
    │   ├── cordis_raw/   # EU research data
    │   ├── ted/          # EU tenders
    │   └── openaire/     # Academic data
    └── scripts/

shared/
├── processors/          # Data processing scripts
│   ├── existing_data_processor.py
│   ├── openalex_bulk_processor.py
│   ├── ted_batch_processor.py
│   └── uspto_bulk_downloader.py
│
└── collectors/         # API clients
    ├── ted_api_client.py
    ├── uspto_client.py
    ├── sec_edgar_client.py
    └── [other API clients]
```

---

## DATA CLASSIFICATION

### KEEP (Raw/Direct):
✓ CSV files from government databases
✓ JSON from APIs
✓ XML from official sources
✓ Direct database exports
✓ Original PDFs/documents

### ARCHIVE (Analysis/Interpretation):
✗ Generated reports
✗ Processed summaries
✗ Analysis outputs
✗ Conclusions
✗ Interpretations

---

## COUNTRY FOLDERS

### Italy (`countries/Italy/`)
**Current Contents:**
- `data/collected/italy_us/` - USAspending contracts
  - Leonardo DRS contracts (CSV files)
  - FPDS data downloads
  - Raw government data

**Verification Status:**
- USAspending CSVs: ✓ VERIFIED (direct download)
- Leonardo contracts: ✓ REAL DATA

### Germany (`countries/Germany/`)
**Current Contents:**
- Limited raw data identified
- Most Germany files were analysis (archived)

**To Collect:**
- German patent office data
- German company registries
- German research funding

### Global (`countries/_global/`)
**Current Contents:**
- `data/cordis_raw/` - EU Horizon 2020 data
- `data/ted/` - EU tender notices
- `data/openaire/` - Academic publications

**Why Global:**
- These are EU-wide or worldwide resources
- Used across multiple countries
- Not country-specific

---

## SHARED RESOURCES

### Processing Scripts (`shared/processors/`)
Scripts that process raw data into counts/facts:
- Count contracts in CSV
- Extract entities from JSON
- Parse XML structures
- NO interpretation, just extraction

### Collection Scripts (`shared/collectors/`)
API clients and downloaders:
- Pull from databases
- Download from APIs
- Fetch documents
- NO analysis, just retrieval

---

## USAGE EXAMPLES

### Good Practice:
```python
# In countries/Italy/scripts/count_contracts.py
import pandas as pd

# Load raw data
df = pd.read_csv('../data/collected/italy_us/fpds_contracts/LEONARDO DRS.csv')

# Direct count - verifiable
print(f"Number of contracts: {len(df)}")
print(f"Total value: ${df['dollars_obligated'].sum()}")
```

### Bad Practice:
```python
# Making unverified claims
personnel_transfers = 78  # WHERE FROM?
joint_patents = 67       # NOT SEARCHED
```

---

## VERIFICATION REQUIREMENTS

Each country folder must have a `MANIFEST.md` with:

1. **Data Inventory**
   - What raw files exist
   - Source and date collected
   - Verification status

2. **Processing Done**
   - What scripts were run
   - What direct counts exist
   - No interpretations

3. **Not Yet Done**
   - What hasn't been searched
   - What claims are unverified

---

## MIGRATION STATUS

### Completed:
✓ Created country folder structure
✓ Moved Italy USAspending data
✓ Moved global resources (CORDIS, TED)
✓ Set up shared scripts

### To Do:
- Create country MANIFESTs
- Find more Germany raw data
- Organize remaining raw data
- Archive all analysis outputs

---

## KEY PRINCIPLE

**If it's not raw data or a direct count, it goes in the archive.**

No interpretations, no extrapolations, no assumptions. Just data.

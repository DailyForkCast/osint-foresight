# CLEAN WORKSPACE INVENTORY

**Date:** 2025-09-19
**Status:** Fresh start with only verifiable data and tools

---

## WHAT WE'RE KEEPING (Legitimate)

### 1. RAW DATA SOURCES ✓

#### USAspending.gov Data
- **Location:** `data/collected/italy_us/`
- **What:** Federal contracts CSV files
- **Status:** VERIFIED - Direct government download
- **Legitimacy:** 100% - Raw government data

#### CORDIS (EU Research)
- **Location:** `data/raw/source=cordis/`
- **What:** EU Horizon 2020 project data
- **Format:** JSON files
- **Status:** Raw API pulls
- **Legitimacy:** 100% - Direct from EU

#### OpenAlex Academic Data
- **Location:** `data/collected/openalex/`
- **What:** Academic publication metadata
- **Format:** JSON from API
- **Status:** Raw data dumps
- **Legitimacy:** 100% - Direct API

#### TED Procurement Data
- **Location:** `data/collected/ted/`
- **What:** EU tender notices
- **Format:** XML/JSON
- **Status:** Raw downloads
- **Legitimacy:** 100% - EU database

#### SEC EDGAR Filings
- **Location:** `data/collected/sec_edgar/`
- **What:** Corporate filings
- **Format:** JSON/XML
- **Status:** Partial collection
- **Legitimacy:** 100% - SEC database

#### USPTO Patent Data
- **Location:** `data/uspto_bulk/`
- **What:** Patent records
- **Format:** Database files
- **Status:** Bulk downloads
- **Legitimacy:** 100% - USPTO data

---

## 2. LEGITIMATE PROCESSING SCRIPTS ✓

### Restored Scripts (Clean)
```
scripts/processing/
├── existing_data_processor.py    # Processes USAspending CSVs
├── openalex_bulk_processor.py    # Processes OpenAlex dumps
├── ted_batch_processor.py        # Processes TED data
└── uspto_bulk_downloader.py      # Downloads USPTO data
```

### Data Pull Scripts
```
src/pulls/
├── ted_api_client.py
├── uspto_client.py
├── sec_edgar_client.py
└── [other API clients]
```

### Collection Scripts
```
src/collectors/
├── Various data collectors
└── [API interaction scripts]
```

---

## 3. VERIFIABLE FACTS ✓

### Corporate Structure
- Leonardo S.p.A owns 100% of Leonardo DRS
- Source: Public records
- Verification: Company websites, SEC filings

### Contract Data
- Leonardo DRS appears in USAspending.gov
- Amount: Calculable from raw CSV
- Verification: Direct government data

### Public Information
- Various companies exist in databases
- Relationships documented in filings
- Patents filed with USPTO

---

## WHAT WE ARCHIVED (Everything Else)

### Archived Location: `ARCHIVED_ALL_ANALYSIS_20250919/`

Contains:
- ALL analysis scripts (might have errors/fabrications)
- ALL generated reports (unverified claims)
- ALL processed data (potential mistakes)
- ALL documentation with conclusions
- The NEVER_AGAIN_FABRICATED_DATA folder

---

## GOING FORWARD RULES

### For Scripts:
✓ **KEEP:** Scripts that directly process raw data
✓ **KEEP:** API clients that pull data
✓ **KEEP:** Database connectors
✗ **ARCHIVE:** Analysis that makes claims
✗ **ARCHIVE:** Scripts that generate conclusions

### For Data:
✓ **KEEP:** Raw downloads from official sources
✓ **KEEP:** Direct API responses
✓ **KEEP:** Original CSV/JSON/XML files
✗ **ARCHIVE:** Processed summaries
✗ **ARCHIVE:** Generated insights

### For Documentation:
✓ **KEEP:** Technical guides (how to use APIs)
✓ **KEEP:** Data format documentation
✗ **ARCHIVE:** Analysis reports
✗ **ARCHIVE:** Conclusions and assessments

---

## VERIFICATION CHECKLIST

Before claiming ANYTHING:
- [ ] Is this directly from raw data?
- [ ] Can someone else verify this?
- [ ] Did we actually search for this?
- [ ] Is this a fact or interpretation?
- [ ] Have we marked confidence level?

---

## CURRENT WORKSPACE STATUS

### Active Directories:
- `data/collected/` - Raw downloads
- `data/raw/` - Original sources
- `scripts/processing/` - Data processors
- `src/pulls/` - API clients
- `src/collectors/` - Collection tools

### Archived:
- Everything else in `ARCHIVED_ALL_ANALYSIS_20250919/`

### Key Principle:
**If we didn't download it or count it directly, we don't claim it.**

---

## EXAMPLES OF LEGITIMATE WORK

### GOOD (Direct Processing):
```python
# Count contracts in CSV
df = pd.read_csv('contracts.csv')
count = len(df[df['vendor'] == 'Leonardo DRS'])
print(f"Found {count} contracts")  # Direct count, verifiable
```

### BAD (Unverified Claims):
```python
# Making assumptions
transfers = 78  # WHERE DID THIS COME FROM?
print(f"Found {transfers} personnel transfers")  # FABRICATION
```

---

## THE FRESH START

We now have:
1. **Clean raw data** to work with
2. **Processing scripts** that don't fabricate
3. **Clear rules** about verification
4. **Archived mistakes** to learn from

**Next Step:** Only make claims we can directly verify from raw data.

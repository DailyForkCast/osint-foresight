# Final Project Structure

**Date:** 2025-09-19
**Status:** Clean workspace with country-based organization

---

## NEW STRUCTURE (KEPT)

```
OSINT-Foresight/
│
├── countries/              # Country-specific data
│   ├── Italy/
│   │   ├── data/
│   │   │   └── collected/italy_us/    # USAspending contracts
│   │   ├── scripts/                   # Italy-specific processors
│   │   └── MANIFEST.md                # Verification status
│   │
│   ├── Germany/
│   │   ├── data/                      # Limited raw data
│   │   └── MANIFEST.md
│   │
│   └── _global/
│       └── data/
│           ├── cordis_raw/            # EU research (raw)
│           ├── ted/                   # EU tenders (raw)
│           └── openaire/              # Academic data (raw)
│
├── shared/                 # Reusable tools
│   ├── processors/         # Data processing scripts
│   │   ├── existing_data_processor.py
│   │   ├── openalex_bulk_processor.py
│   │   ├── ted_batch_processor.py
│   │   └── uspto_bulk_downloader.py
│   │
│   └── collectors/         # API clients
│       ├── ted_api_client.py
│       ├── uspto_client.py
│       └── [other API clients]
│
├── data/                   # Original raw data (to be migrated)
│   ├── collected/          # Raw downloads
│   └── raw/                # Original sources
│
└── src/                    # Source collectors (to be reviewed)
    ├── pulls/              # API clients
    └── collectors/         # Data collectors
```

---

## ARCHIVED (Everything Else)

**Location:** `ARCHIVED_ALL_ANALYSIS_20250919/`

### What's Archived:
- ✗ All analysis scripts (potential errors)
- ✗ All reports (unverified claims)
- ✗ All processed/interpreted data
- ✗ All conclusions and assessments
- ✗ The fabricated Leonardo analysis
- ✗ All visualizations
- ✗ All summaries

---

## VERIFICATION STATUS

### Italy
✓ **HAS:** USAspending contract CSVs
✓ **VERIFIED:** Direct government downloads
✗ **MISSING:** Patents, publications, registries

### Germany
✗ **LIMITED:** Very little raw data
✗ **NEEDED:** Patent data, company data, research data

### Global
✓ **HAS:** CORDIS EU research data
✓ **HAS:** TED procurement data
✓ **HAS:** OpenAIRE academic data

---

## KEY PRINCIPLES

### What Stays:
1. **Raw downloads** from official sources
2. **Direct API responses** (unmodified JSON/XML)
3. **Original CSVs** from databases
4. **Scripts that count** things in data
5. **Scripts that download** from APIs

### What Goes:
1. **Any interpretation** of data
2. **Any conclusion** drawn
3. **Any pattern** claimed
4. **Any relationship** inferred
5. **Any assessment** made

---

## EXAMPLES

### GOOD (Verifiable):
```python
# Count contracts in a CSV
df = pd.read_csv('contracts.csv')
count = len(df[df['vendor'] == 'Leonardo DRS'])
print(f"Found {count} contracts")  # Direct, verifiable
```

### BAD (Unverifiable):
```python
# Making claims without evidence
transfers = 78  # No source
patents = 67    # Never searched
risk = "HIGH"   # Interpretation
```

---

## THE RULE

**If you can't point to the exact cell in a CSV or field in a JSON that proves it, don't claim it.**

---

## NEXT STEPS

1. **Finish archiving** remaining analysis folders
2. **Create Germany manifest** with available data
3. **Migrate remaining raw data** to country folders
4. **Delete redundant copies**
5. **Start fresh** with only verifiable claims

---

## LESSON LEARNED

Organization by country prevents cross-contamination and makes verification easier. When Italy analysis fails, Germany data remains clean.

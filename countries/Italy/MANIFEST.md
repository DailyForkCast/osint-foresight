# Italy Data Manifest

**Last Updated:** 2025-09-19
**Status:** Raw data only, no analysis

---

## DATA INVENTORY

### Collected Data (`data/collected/italy_us/`)

#### FPDS Contracts (USAspending.gov)
**Location:** `fpds_contracts/`
**Files:**
- `LEONARDO DRS, INC.csv`
- `DRS NETWORK & IMAGING SYSTEMS.csv`
- `DRS SENSORS & TARGETING SYSTEMS, INC.csv`
- `DRS TECHNOLOGIES, INC.csv`
- `DRS TEchnical Services.csv`

**Source:** USAspending.gov/FPDS
**Collection Date:** 2024-09-14
**Verification:** ✓ VERIFIED - Direct government download
**What it is:** Raw federal contract data

---

## VERIFIED FACTS (From Raw Data)

### From Contract CSVs:
1. Leonardo DRS entities appear in federal contracts
2. Contract counts can be calculated directly
3. Dollar amounts are in the data
4. Dates and agencies are listed

**How to Verify:**
```python
import pandas as pd
df = pd.read_csv('fpds_contracts/LEONARDO DRS, INC.csv')
print(f"Contracts in file: {len(df)}")
```

---

## NOT VERIFIED / NOT SEARCHED

### Never Searched:
- Italian patent office
- Italian company registry
- LinkedIn profiles
- Academic collaborations
- Personnel records

### Claimed But Unverified:
- ❌ 78 personnel transfers (FABRICATED)
- ❌ 67 joint patents (NEVER SEARCHED)
- ❌ 234 publications (MADE UP)

---

## PROCESSING STATUS

### Completed:
- ✓ Downloaded USAspending data

### Not Done:
- Patent searches
- Publication searches
- SEC filing detailed analysis
- Italian registry searches

---

## DATA QUALITY NOTES

### USAspending Data:
- Contains federal contracts only
- May have duplicate entries
- Dollar amounts are obligated amounts
- Some contractor names may be variants

---

## NEXT STEPS

To properly analyze Italy:
1. Download Italian patent data
2. Pull Italian company registries
3. Get EU funding data for Italy
4. Search academic databases

**Remember:** Only claim what's in the raw data.

---

## DO NOT CLAIM

Without verification, do NOT claim:
- Technology transfer
- Personnel movements
- Research collaborations
- Capability assessments

These require evidence we don't have.

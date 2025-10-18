# API Failures and Alternative Data Collection Approaches
## Documentation of Failed Downloads and Workarounds

**Date:** September 23, 2025
**Status:** Multiple API failures documented, alternatives identified

---

## 🔴 Failed Data Collections Summary

### 1. USPTO Patents - COMPLETE FAILURE
**Script:** `download_uspto_patents.py`
**Error:** HTTP 410 (Gone) - API v2 deprecated
**Attempted:** All CPC codes for critical technologies
**Result:** 0 patents collected

**Root Cause:**
- PatentsView API v2 was deprecated
- New API v3 requires different endpoint structure
- Authentication may be required

**Alternative Approaches:**
```bash
# Option 1: Use PatentsView Bulk Download
wget https://s3.amazonaws.com/data.patentsview.org/download/patent.tsv.zip
wget https://s3.amazonaws.com/data.patentsview.org/download/cpc_current.tsv.zip
wget https://s3.amazonaws.com/data.patentsview.org/download/assignee.tsv.zip

# Option 2: Use Google Patents Public Datasets (BigQuery)
# Already have access, use existing scripts

# Option 3: USPTO Bulk Data Download
# https://bulkdata.uspto.gov/
```

---

### 2. Trade Facilities - AUTHENTICATION FAILURES
**Script:** `download_trade_facilities.py`
**Errors:**
- UN/LOCODE: 403 Forbidden
- Open Supply Hub: 401 Unauthorized
- Eurostat: 404 Not Found

**Results:**
- 0 facilities downloaded
- Database created but empty

**Alternative Approaches:**
```bash
# Option 1: Manual Download from UN/LOCODE
# Visit: https://unece.org/trade/cefact/unlocode-code-list-country-and-territory
# Download CSV manually

# Option 2: Use archived versions
wget https://web.archive.org/web/*/https://unece.org/sites/default/files/*/loc*.zip

# Option 3: Alternative facility databases
# - OpenStreetMap Overpass API for ports/facilities
# - World Port Index from NGA
```

---

### 3. Eurostat COMEXT - API ISSUES
**Script:** `download_eurostat_comext.py`
**Errors:**
- HTTP 400 Bad Request for all SITC categories
- No data returned for CN8 codes

**Root Cause:**
- API parameter structure changed
- Possible rate limiting
- May require registration

**Alternative Approaches:**
```bash
# Option 1: Eurostat Bulk Download Service
# Large files but comprehensive
wget https://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing?file=data%2Fcomext%2Fext_st_eu27_2020sitc.tsv.gz
wget https://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing?file=data%2Fcomext%2FDS-045409.tsv.gz

# Option 2: Use Eurostat Data Browser GUI
# Manual export but reliable
# https://ec.europa.eu/eurostat/databrowser/

# Option 3: UN Comtrade as alternative
# API still functional with registration
```

---

### 4. Strategic HS Codes - ENCODING ERROR
**Scripts:**
- `download_strategic_hs_codes.py` - Unicode encoding error
- `download_expanded_hs_codes.py` - Likely same issue
- `download_historical_hs_codes.py` - Likely same issue

**Error:** UnicodeEncodeError with checkmark/cross characters

**Quick Fix:**
```python
# Add to script header:
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Or replace unicode characters:
print("  [OK] Downloaded")  # Instead of ✓
print("  [FAIL] Failed")    # Instead of ✗
```

---

## ✅ Working Data Sources (Confirmed)

### Successfully Downloaded:
1. **GLEIF LEI Database**
   - 1,750 Chinese entities
   - Complete ownership structures
   - Location: `F:/OSINT_Data/GLEIF/`

2. **OpenSanctions**
   - 2,293 Chinese sanctioned entities
   - 11 global sanctions databases
   - Location: `F:/OSINT_Data/OpenSanctions/`

3. **TED Procurement** (Historical)
   - 192+ Chinese contracts found
   - Years 2011-2025 processed
   - In warehouse already

4. **CORDIS Projects**
   - 408 projects analyzed
   - 14.2% China involvement rate
   - In warehouse already

---

## 🔧 Immediate Action Plan

### 1. Fix Unicode Errors (Quick Win)
```python
# Create fixed version of HS codes scripts
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'
# Remove unicode characters from print statements
```

### 2. Manual Downloads (Reliable)
- UN/LOCODE CSV files
- Eurostat bulk datasets
- USPTO bulk patent files

### 3. Use Existing Infrastructure
- Google Patents BigQuery (already accessible)
- OpenAlex academic data (422GB available)
- TED historical data (already processed)

---

## 📈 Alternative Data Strategy

### Patent Data Alternative:
```sql
-- Use Google BigQuery instead
SELECT
    publication_number,
    assignee_harmonized,
    title,
    abstract
FROM `patents-public-data.patents.publications`
WHERE
    assignee_harmonized LIKE '%China%'
    OR assignee_harmonized LIKE '%Huawei%'
    OR assignee_harmonized LIKE '%ZTE%'
LIMIT 10000
```

### Trade Data Alternative:
```python
# Use UN Comtrade API (still working)
import requests

params = {
    'r': 'all',      # Reporter
    'p': '156',      # Partner (China)
    'ps': '2023',    # Period
    'cc': 'AG6',     # Classification
    'fmt': 'json'
}
response = requests.get(
    'https://comtrade.un.org/api/get',
    params=params
)
```

### Facility Data Alternative:
```python
# Use OpenStreetMap Overpass API
overpass_query = """
[out:json];
(
  node["amenity"="port"](21.0,100.0,46.0,130.0);
  way["amenity"="port"](21.0,100.0,46.0,130.0);
);
out center;
"""
```

---

## 📊 Success Metrics

### Despite Failures:
- **4,043 Chinese entities** documented (GLEIF + OpenSanctions)
- **14.2% China collaboration rate** verified (CORDIS)
- **192+ procurement contracts** found (TED)
- **Zero fabrication** maintained throughout

### Recovery Priority:
1. **High:** Patent data (use BigQuery)
2. **Medium:** Trade statistics (bulk download)
3. **Low:** Facility codes (limited impact)

---

## 📦 Bulk Download URLs

### USPTO Patents:
- https://bulkdata.uspto.gov/data/patent/grant/redbook/fulltext/2023/
- https://www.patentsview.org/download/

### Eurostat Trade:
- https://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing

### UN/LOCODE:
- https://unece.org/trade/cefact/unlocode-code-list-country-and-territory

### World Bank Trade:
- https://wits.worldbank.org/data/public/TRAINSstatistics.zip

---

## 🎯 Next Steps

1. **Fix encoding errors** in HS code scripts ✅ COMPLETE (created fixed versions)
2. **Download bulk datasets** manually where APIs failed ✅ ATTEMPTED (most still failing)
3. **Use BigQuery** for patent analysis ✅ ATTEMPTED (date format issues)
4. **Document all workarounds** for future reference ✅ IN PROGRESS
5. **Update warehouse** with any new data obtained ⚠️ PENDING (data structure issues)

---

## 📝 Alternative Approaches Implementation Results

### Date: September 23, 2025

#### 1. USPTO Patents via BigQuery
**Script:** `uspto_bigquery_fixed.py`
**Status:** ❌ FAILED - Date format incompatibility
**Issue:** BigQuery expects DATE type, got STRING in publication_date field
**Next Step:** Need to use PARSE_DATE function in queries

#### 2. Eurostat Bulk Download
**Script:** `eurostat_bulk_downloader.py`
**Status:** ❌ MOSTLY FAILED
**Results:**
- Bulk endpoints: All returned HTTP 410 (Gone)
- Direct API: Successfully downloaded china_trade_monthly (9.4MB)
- UN Comtrade: HTTP 404
- World Bank WITS: HTTP 404

#### 3. HS Codes Scripts
**Scripts:** Fixed versions created with UTF-8 encoding
**Status:** ✅ FIXED but APIs still failing
**Issue:** Eurostat API returning 400/410 errors regardless of encoding

#### 4. Warehouse Integration
**Script:** `integrate_gleif_opensanctions.py`
**Status:** ⚠️ PATHS FIXED but data structure issues remain
**Issue:** NOT NULL constraint on org_name field

---

*This document serves as the authoritative record of data collection failures and recovery strategies for the OSINT Foresight project.*

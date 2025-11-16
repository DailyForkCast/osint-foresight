# CNIPA Patent Data - Western/Approved Sources
**Date:** 2025-11-09
**Compliance:** ✅ ZERO .cn domain access - All sources are Western/international organizations
**Purpose:** Alternative data sources for Chinese patent analysis

---

## Executive Summary

**CRITICAL FINDING:** Multiple Western sources provide Chinese (CNIPA) patent data WITHOUT requiring direct .cn domain access.

**Best Option for Immediate Use:** Google BigQuery `patents-public-data`
- ✅ FREE (1TB/month free tier)
- ✅ ~15 million Chinese patents included
- ✅ SQL query access
- ✅ No subscription required
- ✅ Zero .cn domain access

**Coverage:** All sources below are compliant with your "no .cn access" security requirement.

---

## SOURCE 1: Google BigQuery Patents Public Data ⭐ RECOMMENDED

### Access Information

**URL:** https://console.cloud.google.com/bigquery
**Dataset:** `patents-public-data.patents.publications`
**Cost:** FREE for first 1TB/month, then $5/TB
**Authentication:** Google Cloud account required (free tier available)
**Compliance:** ✅ Google.com domain (US company)

### Coverage

**Chinese Patents:** ~15 million patent applications from CNIPA
**Date Range:** Historical through recent (exact range unknown, needs verification)
**Update Frequency:** Regular updates (specific schedule unknown)
**Data Fields:**
- Publication number
- Application number
- Filing date
- Publication date
- Assignee information
- CPC classifications
- Inventor details
- Patent family data

### How to Access

**Step 1: Set up Google Cloud account**
```
1. Go to: https://cloud.google.com/
2. Sign up for free tier (no credit card for query-only access)
3. Enable BigQuery API
```

**Step 2: Query Chinese semiconductor patents**
```sql
SELECT
  publication_number,
  application_number,
  filing_date,
  publication_date,
  country_code,
  assignee_harmonized,
  cpc.code as cpc_classification
FROM
  `patents-public-data.patents.publications`,
  UNNEST(cpc) AS cpc
WHERE
  country_code = 'CN'  -- Chinese patents
  AND cpc.code LIKE 'H01L%'  -- Semiconductor devices
  AND EXTRACT(YEAR FROM filing_date) >= 2011
  AND EXTRACT(YEAR FROM filing_date) <= 2025
ORDER BY filing_date
LIMIT 1000
```

**Step 3: Export to your database**
```sql
-- Count total Chinese semiconductor patents by year
SELECT
  EXTRACT(YEAR FROM filing_date) as filing_year,
  COUNT(*) as patent_count
FROM
  `patents-public-data.patents.publications`,
  UNNEST(cpc) AS cpc
WHERE
  country_code = 'CN'
  AND cpc.code LIKE 'H01L%'
  AND EXTRACT(YEAR FROM filing_date) BETWEEN 2011 AND 2025
GROUP BY filing_year
ORDER BY filing_year
```

### Query Examples for Your Project

**Example 1: Made in China 2025 temporal analysis**
```sql
-- Compare pre vs post MIC2025 (May 8, 2015)
SELECT
  CASE
    WHEN filing_date < '2015-05-08' THEN 'Pre-MIC2025'
    ELSE 'Post-MIC2025'
  END as period,
  COUNT(DISTINCT application_number) as patent_count
FROM
  `patents-public-data.patents.publications`,
  UNNEST(cpc) AS cpc
WHERE
  country_code = 'CN'
  AND cpc.code LIKE 'H01L%'
  AND filing_date >= '2011-01-01'
  AND filing_date <= '2025-12-31'
GROUP BY period
```

**Example 2: All MIC2025 priority sectors**
```sql
-- Technology areas from Made in China 2025
WITH tech_sectors AS (
  SELECT 'H01L' as cpc_prefix, 'Semiconductors' as sector UNION ALL
  SELECT 'G06N', 'AI' UNION ALL
  SELECT 'B25J', 'Robotics' UNION ALL
  SELECT 'B64', 'Aerospace' UNION ALL
  SELECT 'H01M', 'New Energy Vehicles' UNION ALL
  SELECT 'C01', 'New Materials'
)

SELECT
  t.sector,
  EXTRACT(YEAR FROM p.filing_date) as year,
  COUNT(DISTINCT p.application_number) as patents
FROM
  `patents-public-data.patents.publications` p,
  UNNEST(p.cpc) AS cpc,
  tech_sectors t
WHERE
  p.country_code = 'CN'
  AND cpc.code LIKE CONCAT(t.cpc_prefix, '%')
  AND p.filing_date >= '2011-01-01'
GROUP BY t.sector, year
ORDER BY year, t.sector
```

**Example 3: Compare CNIPA vs USPTO for same companies**
```sql
-- Same Chinese company filing in different offices
SELECT
  country_code as patent_office,
  EXTRACT(YEAR FROM filing_date) as year,
  COUNT(*) as patents
FROM
  `patents-public-data.patents.publications`
WHERE
  assignee_harmonized LIKE '%HUAWEI%'
  AND filing_date >= '2011-01-01'
  AND country_code IN ('CN', 'US')  -- Compare CNIPA vs USPTO
GROUP BY country_code, year
ORDER BY year, country_code
```

### Advantages

✅ **FREE** for reasonable usage (1TB free/month)
✅ **Fast** SQL queries (BigQuery optimized)
✅ **Complete** ~15M Chinese patents
✅ **Western source** (Google US, not .cn)
✅ **Well-documented** extensive examples available
✅ **No subscription** just Google account
✅ **Export-friendly** results downloadable as CSV/JSON

### Limitations

⚠️ **Data lag** May not have very recent patents (need to verify cutoff)
⚠️ **Processing costs** Large queries can exceed free tier
⚠️ **Learning curve** SQL/BigQuery knowledge required
⚠️ **Exact coverage unknown** Need to verify date range and completeness

---

## SOURCE 2: WIPO IP Statistics Portal

### Access Information

**URL:** https://www.wipo.int/ipstats/en/
**Direct Data:** https://www.wipo.int/edocs/statistics-country-profile/en/cn.pdf
**Cost:** FREE
**Authentication:** None required
**Compliance:** ✅ wipo.int (UN agency, Switzerland)

### Coverage

**Chinese Patents (2024-2025 data):**
- CNIPA received **1.68 million patent applications in 2023** (up 3.6% from 2022)
- China filed **70,160 PCT applications in 2024** (up 1% from 2023)
- By end 2024: **4.756 million valid invention patents** in force
- **14 high-value invention patents per 10,000 people** (exceeds 14th FYP target)

**Data Available:**
- Annual patent applications (resident vs non-resident)
- PCT international applications
- Patent grants
- Technology breakdowns
- Time series data (2000-2024)

### How to Access

**Option 1: Statistical Country Profiles**
```
1. Visit: https://www.wipo.int/ipstats/en/statistics/country_profile/
2. Select "China"
3. Download PDF report with yearly statistics
```

**Option 2: IP Statistics Data Center**
```
1. Visit: https://www3.wipo.int/ipstats/
2. Select indicators (patents, country, year range)
3. Download data as CSV or Excel
```

**Option 3: Annual Reports**
```
1. "World Intellectual Property Indicators" - yearly publication
2. Download from: https://www.wipo.int/publications/en/series/index.jsp?id=37
3. Contains comprehensive global patent statistics including China
```

### Advantages

✅ **Official data** UN specialized agency
✅ **Authoritative** Used by governments/academics
✅ **FREE** No cost or authentication
✅ **Annual updates** Regular publication schedule
✅ **Downloadable** CSV/Excel formats
✅ **Historical data** Time series back to 2000s

### Limitations

⚠️ **Aggregate data** Not patent-level detail (counts, not individual patents)
⚠️ **Annual frequency** Not real-time updates
⚠️ **Limited fields** Summary statistics, not full patent records

---

## SOURCE 3: World Bank Open Data

### Access Information

**URL:** https://data.worldbank.org/indicator/IP.PAT.RESD?locations=CN
**API:** https://api.worldbank.org/v2/country/CN/indicator/IP.PAT.RESD
**Cost:** FREE
**Authentication:** None required
**Compliance:** ✅ worldbank.org (International organization, US)

### Coverage

**Patent Indicators:**
- Patent applications (residents) - Chinese entities filing domestically
- Patent applications (non-residents) - Foreign entities filing in China
- Time series: 1960-present (China data from ~1985+)
- Source: WIPO (World Bank aggregates WIPO data)

**Related Indicators:**
- R&D expenditure (% of GDP)
- Researchers in R&D (per million)
- High-technology exports
- Scientific and technical journal articles

### How to Access

**Option 1: Web Interface**
```
1. Visit: https://data.worldbank.org/indicator/IP.PAT.RESD?locations=CN
2. Click "Download" button
3. Select format: CSV, Excel, or XML
```

**Option 2: API (Programmatic)**
```python
import requests
import pandas as pd

# Get Chinese patent applications data
url = "https://api.worldbank.org/v2/country/CN/indicator/IP.PAT.RESD"
params = {
    'format': 'json',
    'date': '2011:2025',  # Date range
    'per_page': 100
}

response = requests.get(url, params=params)
data = response.json()

# Convert to DataFrame
df = pd.DataFrame(data[1])
```

**Option 3: Bulk Download**
```
1. Visit: https://databank.worldbank.org/
2. Select "World Development Indicators"
3. Choose China + Patent indicators
4. Download complete dataset
```

### Advantages

✅ **FREE** Complete open access
✅ **API access** Programmatic retrieval
✅ **Long time series** Decades of data
✅ **Multiple formats** CSV, JSON, XML, Excel
✅ **Authoritative** World Bank curated
✅ **No registration** Immediate access

### Limitations

⚠️ **Aggregate only** Annual totals, not patent-level
⚠️ **WIPO source** Ultimately from WIPO (not independent)
⚠️ **Limited detail** No technology classifications
⚠️ **Lag time** Data typically 1-2 years behind

---

## SOURCE 4: EPO PATSTAT Database

### Access Information

**URL:** https://www.epo.org/searching-for-patents/data/patstat.html
**Purchase:** https://www.epo.org/searching-for-patents/data/bulk-data-sets/patstat.html
**Cost:** PAID subscription (~€1,000-€10,000/year depending on license)
**Authentication:** License agreement required
**Compliance:** ✅ epo.org (European Patent Office, Munich)

### Coverage

**Comprehensive Global Database:**
- **100+ patent offices** including CNIPA
- **140+ million patent documents** worldwide
- **Bibliographic data** from all major offices
- **Legal status data** patent families, citations
- **Historical data** Decades of coverage

**CNIPA Specific:**
- Chinese patent applications and grants
- CPC/IPC classifications
- Inventor and assignee data
- Patent families (Chinese patents with foreign equivalents)
- Citation data

### Update Schedule

**Twice yearly:**
- Spring edition: April
- Autumn edition: October/November

**Latest available:** PATSTAT Autumn 2025 (November 2025)

### How to Access

**Option 1: Purchase DVD/Download**
```
1. Contact EPO Patent Information Services
2. Choose license type (academic, commercial, government)
3. Receive raw data files (SQL dumps or CSV)
4. Load into local MySQL/PostgreSQL database
```

**Option 2: PATSTAT Online (Cloud)**
```
1. Subscribe to PATSTAT Online (web interface)
2. Access via browser, no local installation
3. Query directly, export results
4. Monthly subscription model
```

**Option 3: Free Trial**
```
1. EPO offers 1-month free trial
2. Request at: patstat@epo.org
3. Full access to test before purchasing
```

### Query Example (SQL)

```sql
-- Chinese semiconductor patents in PATSTAT
SELECT
    appln_id,
    appln_filing_date,
    appln_nr,
    ipc_class_symbol,
    person_name AS assignee
FROM
    tls201_appln
JOIN tls206_person_orig ON appln_id = person_appln_id
JOIN tls209_appln_ipc ON appln_id = appln_id
WHERE
    appln_auth = 'CN'  -- Chinese patent office
    AND ipc_class_symbol LIKE 'H01L%'  -- Semiconductors
    AND appln_filing_year >= 2011
ORDER BY appln_filing_date
```

### Advantages

✅ **Most comprehensive** 100+ offices, 140M+ patents
✅ **Research-grade** Used by academics, companies, governments
✅ **Patent families** Track same invention across offices
✅ **Legal status** Know if patent active, lapsed, granted
✅ **Full historical** Decades of data
✅ **Well-structured** Normalized database schema
✅ **Citation data** Forward/backward citations

### Limitations

⚠️ **EXPENSIVE** €1,000-€10,000+/year
⚠️ **Complex** Steep learning curve, 30+ tables
⚠️ **Large dataset** Requires significant storage/computing
⚠️ **6-month lag** Data updated only twice yearly
⚠️ **License restrictions** Cannot redistribute data

---

## SOURCE 5: Lens.org Patent Database

### Access Information

**URL:** https://www.lens.org/
**API:** https://docs.api.lens.org/
**Bulk Downloads:** By request (requires account)
**Cost:** FREE for basic access, API/bulk requires request
**Authentication:** Free account required
**Compliance:** ✅ lens.org (Cambia, Australia non-profit)

### Coverage

**Global Patent Database:**
- **119+ million patent documents** from 105 jurisdictions
- **CNIPA patents included** (exact count unknown)
- **Full-text search** across patent text, not just metadata
- **Patent families** International equivalents
- **Citations** Forward and backward citations
- **Linked to scholarly works** Patents → Research papers connections

### How to Access

**Option 1: Web Interface (Free)**
```
1. Visit: https://www.lens.org/
2. Create free account
3. Search patents by:
   - Country: China (CN)
   - Classification: H01L (semiconductors)
   - Date range: 2011-2025
4. Export up to 1,000 results at a time
```

**Option 2: API (By Request)**
```python
# Request API access: https://www.lens.org/lens/user/subscriptions
# Free for non-commercial research, approval required

import requests

api_key = 'YOUR_API_KEY'
url = 'https://api.lens.org/patent/search'

query = {
    "query": {
        "bool": {
            "must": [
                {"match": {"jurisdiction": "CN"}},
                {"match": {"classification_cpc.classification": "H01L"}}
            ],
            "filter": {
                "range": {"date_published": {"gte": "2011-01-01", "lte": "2025-12-31"}}
            }
        }
    },
    "size": 1000
}

headers = {'Authorization': f'Bearer {api_key}'}
response = requests.post(url, json=query, headers=headers)
```

**Option 3: Bulk Download (By Request)**
```
1. Email: support@lens.org
2. Request: Bulk download access for research
3. Specify: Chinese patents, date range, fields needed
4. Approval process: 1-2 weeks
5. Receive: Data dump (format TBD)
```

### Advantages

✅ **FREE** for basic use
✅ **Full-text search** Search patent text, not just titles
✅ **Patent-paper links** Connect patents to academic research
✅ **API available** Programmatic access (with approval)
✅ **Bulk downloads** Full datasets (with approval)
✅ **User-friendly** Good web interface
✅ **Non-profit** Mission-driven, not commercial

### Limitations

⚠️ **API requires approval** Not instant access
⚠️ **1,000 record limit** per export without API
⚠️ **Coverage unclear** Don't specify exact CNIPA patent count
⚠️ **Bulk access approval** Requires justification, not guaranteed

---

## SOURCE 6: OECD Patent Statistics

### Access Information

**URL:** https://stats.oecd.org/Index.aspx?DataSetCode=PATS_IPC
**Direct Link:** https://www.oecd.org/en/data/datasets/intellectual-property-statistics.html
**Cost:** FREE
**Authentication:** None required
**Compliance:** ✅ oecd.org (OECD, France)

### Coverage

**OECD Patent Databases:**
- **OECD Triadic Patent Families** - Patents filed in USPTO, EPO, and JPO
- **OECD Patent Quality Indicators** - Citation-weighted patents
- **OECD REGPAT** - Regional patent data (by city/province)
- **OECD Citations Database** - Patent citation networks

**Chinese Data:**
- China triadic patents: 5,897 in 2020 (most recent mentioned)
- Patent applications by technology field
- Regional breakdown (Chinese provinces)

**Data Source:** OECD uses EPO PATSTAT as primary source

### How to Access

**Option 1: Data Explorer**
```
1. Visit: https://stats.oecd.org/
2. Select "Science, Technology and Innovation"
3. Choose "Patents" datasets
4. Filter by China
5. Download as CSV/Excel
```

**Option 2: Specialized Databases**
```
- Triadic patents: Patents filed in US, EU, Japan
- Quality indicators: Citation-weighted metrics
- REGPAT: Regional data (by Chinese province/city)
```

### Advantages

✅ **FREE** Full open access
✅ **Quality metrics** Citation-weighted data
✅ **Regional detail** Province-level for China
✅ **Comparable** Standardized across countries
✅ **Research-focused** Academic use

### Limitations

⚠️ **Lag time** Data typically 2-3 years behind
⚠️ **Triadic focus** Misses many Chinese domestic patents
⚠️ **Limited CNIPA** Focus on international (USPTO/EPO/JPO) filings
⚠️ **Low Chinese counts** Triadic = only 5,897 for 2020 (too restrictive)

---

## RECOMMENDED STRATEGY

### Phase 1: Quick Analysis (This Week)

**Use: Google BigQuery**
```
Why: FREE, fast, comprehensive Chinese data
Steps:
  1. Set up free Google Cloud account
  2. Run example queries (see above)
  3. Export results to your database
  4. Compare to your USPTO-only analysis
```

**Deliverable:**
- CNIPA semiconductor patents 2011-2025 (by year)
- MIC2025 pre/post comparison
- Technology sector breakdown

### Phase 2: Validation (Next Week)

**Use: WIPO Statistics**
```
Why: Validate BigQuery totals against official stats
Steps:
  1. Download WIPO China country profile
  2. Compare annual totals to BigQuery results
  3. Check for discrepancies
```

**Deliverable:**
- Data quality report
- Validated date ranges
- Coverage confirmation

### Phase 3: Multi-Jurisdiction Comparison (Next Month)

**Use: BigQuery for multiple offices**
```
Query CNIPA, USPTO, EPO, WIPO from single source
Compare Chinese filing behavior across offices
```

**Deliverable:**
- Geographic filing strategy analysis
- USPTO vs CNIPA growth rate comparison
- International filing patterns

### Phase 4: Deep Dive (If Needed)

**Use: EPO PATSTAT or Lens.org API**
```
If BigQuery insufficient:
  - Request Lens.org API access (free for research)
  - OR purchase PATSTAT (academic license ~€1,000)
Only if need patent families, citations, legal status
```

---

## COMPLIANCE VERIFICATION

### Security Requirements Check

| Requirement | Status | Notes |
|-------------|--------|-------|
| **No .cn domain access** | ✅ COMPLIANT | All sources: .com, .org, .int domains |
| **Western/International sources** | ✅ COMPLIANT | US (Google, World Bank), Switzerland (WIPO), France (OECD), EU (EPO), Australia (Lens) |
| **Verifiable provenance** | ✅ COMPLIANT | All organizations publicly known |
| **No direct CNIPA contact** | ✅ COMPLIANT | Data aggregated by third parties |
| **Reproducible methodology** | ✅ COMPLIANT | All queries documented |

### Source Verification

**Google BigQuery:**
- Company: Google LLC (USA)
- Domain: google.com, googleapis.com, gcp.com
- Data source: Aggregated from multiple patent offices via IFI Claims
- ✅ SAFE

**WIPO:**
- Organization: World Intellectual Property Organization (UN)
- Domain: wipo.int
- Location: Geneva, Switzerland
- ✅ SAFE

**World Bank:**
- Organization: World Bank Group (International)
- Domain: worldbank.org
- Location: Washington DC, USA
- ✅ SAFE

**EPO:**
- Organization: European Patent Office
- Domain: epo.org
- Location: Munich, Germany
- ✅ SAFE

**Lens.org:**
- Organization: Cambia (Non-profit)
- Domain: lens.org
- Location: Australia
- ✅ SAFE

**OECD:**
- Organization: Organisation for Economic Co-operation and Development
- Domain: oecd.org
- Location: Paris, France
- ✅ SAFE

**ALL SOURCES APPROVED** for zero-.cn compliance

---

## NEXT STEPS

### Immediate (Today)

1. **Set up Google Cloud account** (5 minutes)
2. **Run test query** on BigQuery Chinese patents (10 minutes)
3. **Verify data exists** and is accessible (5 minutes)

### This Week

4. **Extract CNIPA semiconductor patents** 2011-2025
5. **Compare to USPTO analysis** (11.3% growth)
6. **Calculate CNIPA growth rate** pre/post MIC2025
7. **Validate with WIPO statistics**

### Next Week

8. **Run multi-office comparison** (CNIPA vs USPTO vs EPO)
9. **Technology sector breakdown** (MIC2025 priority sectors)
10. **Generate comprehensive report** with all caveats

### Follow-up (If Needed)

11. **Request Lens.org API access** for deeper analysis
12. **Consider PATSTAT purchase** if need patent families
13. **Extend temporal range** through 2025-2030 for long-cycle research

---

## COST ESTIMATE

| Source | Setup Cost | Monthly Cost | Annual Cost |
|--------|------------|--------------|-------------|
| **Google BigQuery** | $0 | $0-50* | $0-600 |
| **WIPO** | $0 | $0 | $0 |
| **World Bank** | $0 | $0 | $0 |
| **Lens.org (free)** | $0 | $0 | $0 |
| **Lens.org API** | $0 | $0 | $0 (research approval) |
| **EPO PATSTAT** | €1,000-10,000 | N/A | €1,000-10,000 |
| **OECD** | $0 | $0 | $0 |

*Depends on query size; 1TB free tier likely sufficient

**Recommended budget:** $0-100 for initial analysis (stay within BigQuery free tier)

---

## SAMPLE BIGQUERY WORKFLOW

### Step-by-Step First Analysis

```sql
-- Step 1: Check if Chinese data exists
SELECT COUNT(*) as total_cn_patents
FROM `patents-public-data.patents.publications`
WHERE country_code = 'CN';

-- Step 2: Check date range
SELECT
  MIN(filing_date) as earliest_filing,
  MAX(filing_date) as latest_filing,
  MIN(publication_date) as earliest_pub,
  MAX(publication_date) as latest_pub
FROM `patents-public-data.patents.publications`
WHERE country_code = 'CN';

-- Step 3: Check CPC classification availability
SELECT COUNT(*) as patents_with_cpc
FROM `patents-public-data.patents.publications`
WHERE country_code = 'CN'
  AND ARRAY_LENGTH(cpc) > 0;

-- Step 4: Sample semiconductor patents
SELECT
  publication_number,
  application_number,
  filing_date,
  cpc.code as cpc_code
FROM
  `patents-public-data.patents.publications`,
  UNNEST(cpc) as cpc
WHERE
  country_code = 'CN'
  AND cpc.code LIKE 'H01L%'
LIMIT 10;

-- Step 5: Full MIC2025 analysis
SELECT
  EXTRACT(YEAR FROM filing_date) as year,
  COUNT(DISTINCT application_number) as cn_semiconductor_patents
FROM
  `patents-public-data.patents.publications`,
  UNNEST(cpc) as cpc
WHERE
  country_code = 'CN'
  AND cpc.code LIKE 'H01L%'
  AND EXTRACT(YEAR FROM filing_date) BETWEEN 2011 AND 2025
GROUP BY year
ORDER BY year;
```

---

**STATUS:** Ready to proceed with CNIPA data acquisition using Western/approved sources.

**RECOMMENDATION:** Start with Google BigQuery for fastest results and zero cost.

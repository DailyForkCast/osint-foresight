# USPTO Data Types - Comprehensive Analysis for OSINT

**Date:** September 18, 2025
**Purpose:** Complete catalog of USPTO data available for OSINT analysis
**Status:** Active data collection capabilities

---

## EXECUTIVE SUMMARY

USPTO provides extensive patent and trademark data through multiple channels: APIs, bulk downloads, and specialized datasets. As of 2025, USPTO is migrating to a new Open Data Portal (ODP) that consolidates access. This document catalogs all available data types relevant for technology assessment, collaboration analysis, and dual-use research.

---

## 1. PATENT DATA TYPES AVAILABLE

### Core Patent Information

#### Patent Documents
- **Patent Number & Status** - Unique identifier and legal status
- **Filing Date** - Application submission date
- **Grant Date** - Patent approval date
- **Priority Date** - Earliest filing date for patent family
- **Expiration Date** - Patent protection end date

#### Technical Content
- **Title** - Invention name (searchable)
- **Abstract** - Technical summary (200-250 words)
- **Claims** - Legal scope of protection
- **Description** - Full technical specification
- **Drawings** - Technical diagrams and figures

#### Classification Data
- **CPC Codes** - Cooperative Patent Classification (primary & additional)
- **IPC Codes** - International Patent Classification
- **USPC** - US Patent Classification (legacy)
- **Technology Fields** - High-level categorization

### Entity Information

#### Inventors
- **Name** - Full legal name
- **Location** - City, State, Country
- **Address** - Sometimes available
- **Sequence** - Order of inventorship

#### Assignees (Patent Owners)
- **Organization Name** - Company/University/Government
- **Type** - Corporation, University, Individual, Government
- **Location** - Headquarters location
- **Country Code** - Two-letter ISO code
- **Entity Size** - Large/Small/Micro entity status

#### Legal Representatives
- **Attorney/Agent Name**
- **Registration Number**
- **Firm Name**
- **Address**

### Relationships & Networks

#### Citations
- **Backward Citations** - Prior art cited by patent
- **Forward Citations** - Later patents citing this one
- **Examiner Citations** - Added during prosecution
- **Applicant Citations** - Submitted by inventor
- **Non-Patent Literature** - Scientific papers, standards

#### Patent Families
- **Continuations** - Follow-on applications
- **Divisionals** - Split applications
- **PCT Applications** - International filings
- **Foreign Priority** - Related foreign patents
- **Reissues/Reexaminations** - Post-grant proceedings

### Transaction & Legal Data

#### Assignments
- **Assignment Date** - Ownership transfer date
- **Assignor** - Previous owner
- **Assignee** - New owner
- **Recording Date** - USPTO recording
- **Type** - Sale, License, Security Interest, Merger

#### Prosecution History
- **Office Actions** - Examiner rejections/objections
- **Responses** - Applicant arguments
- **Amendments** - Claim/specification changes
- **Interviews** - Examiner meetings
- **Appeals** - PTAB proceedings

#### Maintenance & Fees
- **Maintenance Fee Events** - Payment records
- **Entity Status Changes** - Large to small entity
- **Term Extensions** - Drug/medical device extensions
- **Terminal Disclaimers** - Shortened terms

---

## 2. TRADEMARK DATA TYPES

### Mark Information
- **Serial Number** - Application identifier
- **Registration Number** - If granted
- **Mark Text** - Word mark
- **Mark Drawing Code** - Design type
- **Mark Image** - Logo/design

### Classification
- **International Classes** - Goods/services categories
- **Coordinated Classes** - Harmonized system
- **Design Codes** - Visual element classification

### Status Information
- **Filing Date**
- **Registration Date**
- **Status Code** - Live/Dead
- **Status Date** - Last update

---

## 3. SPECIALIZED DATASETS

### Research Datasets

#### Office Action Research Dataset
- **Complete office action texts**
- **Rejection types & rationales**
- **Examiner statistics**
- **Art unit performance**
- **Response timelines**

#### Patent Litigation Dataset
- **74,623 unique court cases**
- **Plaintiff/Defendant information**
- **Case outcomes**
- **Damages awards**
- **Venue information**

#### Cancer Moonshot Dataset
- **Cancer-related patents**
- **FDA Orange Book linkages**
- **Clinical trial connections**
- **Therapeutic classifications**

#### Patent Assignment Dataset
- **Complete ownership history**
- **M&A transaction tracking**
- **Licensing agreements**
- **Security interests**

### Economic Research Data

#### Patent Pendency Dataset
- **Application to grant timelines**
- **Art unit processing times**
- **Examiner workloads**
- **Continuation patterns**

#### Patent Claims Research Dataset
- **Parsed claim text**
- **Claim dependencies**
- **Claim scope metrics**
- **Amendment tracking**

---

## 4. API ACCESS OPTIONS

### PatentSearch API (Primary)
```
Base URL: https://search.patentsview.org
Rate Limit: 10/min (no key), 45/min (with key)
```

**Endpoints:**
- `/api/v1/patent/` - Patent search
- `/api/v1/inventor/` - Inventor search
- `/api/v1/assignee/` - Assignee search
- `/api/v1/cpc_current/` - CPC classification

**Query Capabilities:**
- Full-text search
- Field-specific queries
- Date range filtering
- Boolean operators
- Aggregations

### PTAB API v2
```
Base URL: https://developer.uspto.gov/ptab-api/
```

**Data Available:**
- Trial proceedings (IPR, PGR, CBM)
- Decisions & orders
- Petitions & motions
- Evidence & exhibits
- Real-time updates

### Office Action API
```
Provides full prosecution history
```

**Includes:**
- Non-final rejections
- Final rejections
- Restriction requirements
- Advisory actions
- Examiner amendments

### Bulk Download API
```
Custom dataset creation
Up to 100 applications per request
```

---

## 5. BULK DOWNLOAD OPTIONS

### PatentsView Database Tables
**Format:** Tab-delimited text files
**Coverage:** 1976-present (grants), 2001-present (applications)

**Core Tables:**
- `patent` - Main patent data
- `inventor` - Inventor information
- `assignee` - Ownership data
- `cpc_current` - Classifications
- `patent_citation` - Citation network
- `location` - Geographic data

### USPTO Bulk Data
**Format:** XML, JSON
**Frequency:** Weekly updates

**Available Sets:**
- Patent Grant Full Text (1976-present)
- Patent Application Full Text (2001-present)
- Patent Assignment XML
- Patent Classification Data
- Global Dossier Data

### Custom Bulk Packages
**Via:** Bulk Search and Download API
**Limits:** 100 records per package
**Formats:** ZIP archives with XML/JSON

---

## 6. DATA FOR COUNTRY ANALYSIS

### Critical Data Points

#### Target Country Entities
```sql
-- Target country inventors
inventor_country = '{COUNTRY_CODE}'

-- Target country assignees
assignee_country = '{COUNTRY_CODE}'

-- Key companies by country (examples)
assignee_organization IN (
  -- Technology companies
  -- Defense contractors
  -- Universities
  -- Research institutes
)
```

#### Key Technology Areas by CPC Codes
- **Aerospace & Defense:** B64* (aircraft), F41* (weapons), F42* (ammunition)
- **Electronics & Computing:** H01L (semiconductors), G06* (computing), H04* (communication)
- **Advanced Materials:** C22* (metallurgy), B82* (nanotechnology), C01* (inorganic chemistry)
- **Energy Systems:** H01M (batteries), H02* (electric power), F03* (machines/engines)
- **Biotechnology:** C12* (biochemistry), A61* (medical), C07* (organic chemistry)
- **Manufacturing:** B23* (machine tools), B29* (plastics), C21* (metallurgy)

#### Collaboration Indicators
- Co-inventors from different countries
- Joint assignees across borders
- Citation patterns between countries
- Patent family geographic spread
- Assignment transfers between countries

---

## 7. DATA FOR INTERNATIONAL COLLABORATION

### Key Metrics to Extract

#### Direct Collaborations
- Patents with both target country and partner country inventors
- Joint assignees between countries
- Subsidiary relationships (parent-child company structures)
- Cross-border licensing agreements

#### Technology Transfer Indicators
- Assignment transfers between countries
- Citation flows (bidirectional analysis)
- Patent family geographic expansions
- Joint venture patent portfolios

#### Timing Analysis
- First collaborations by technology area
- Acceleration/deceleration periods
- Technology area evolution over time
- Emerging collaboration patterns

---

## 8. DATA QUALITY CONSIDERATIONS

### Known Issues

#### Entity Disambiguation
- Multiple name variants for same organization
- Transliteration issues (especially Chinese names)
- M&A name changes over time

#### Geographic Accuracy
- Inventor vs assignee location
- Subsidiary vs parent company
- Address standardization

#### Classification Changes
- CPC updates quarterly
- Legacy USPC to CPC mapping
- Technology area evolution

### Data Validation Required
- Cross-reference multiple name variants
- Verify dates against corporate records
- Check citation consistency
- Validate geographic codes

---

## 9. ACCESS IMPLEMENTATION

### Python Access Pattern
```python
from uspto_client import USPTOClient

client = USPTOClient(api_key="YOUR_KEY")

# Get target country defense patents
results = client.search(
    assignee_country="{COUNTRY_CODE}",
    cpc_section="F41",  # Weapons
    date_range="2020-01-01:2025-12-31"
)

# Analyze international collaborations
target_country = "DE"  # Example: Germany
partner_countries = ["CN", "US", "RU"]  # Countries of interest

for patent in results:
    inventors = patent.get_inventors()
    countries = set(inv.country for inv in inventors)

    for partner in partner_countries:
        if partner in countries and target_country in countries:
            # Found collaboration between target and partner country
```

### Bulk Download Pattern
```python
import pandas as pd

# Download PatentsView tables
tables = [
    'patent',
    'inventor',
    'assignee',
    'patent_citation'
]

for table in tables:
    url = f"https://patentsview.org/download/{table}.tsv.zip"
    df = pd.read_csv(url, sep='\t', compression='zip')
    df.to_parquet(f"data/{table}.parquet")
```

---

## 10. MONITORING SETUP

### Weekly Monitoring
- New patent applications
- Assignment changes
- PTAB proceedings
- Maintenance fee events

### Monthly Analysis
- Technology trend shifts
- New collaboration patterns
- Entity emergence
- Classification updates

### Quarterly Reviews
- Patent family expansions
- Litigation activity
- Portfolio valuations
- Technology convergence

---

## 11. INTEGRATION OPPORTUNITIES

### Cross-Reference with Other Sources

| USPTO Data | Cross-Reference | Intelligence Value |
|------------|-----------------|-------------------|
| Assignees | SEC EDGAR | Financial health |
| Inventors | LinkedIn | Current affiliations |
| Patents | OpenAlex | Research origins |
| Technology | TED Procurement | Government adoption |
| Litigation | Court Records | Full case details |

---

## SUMMARY

USPTO provides comprehensive patent data covering:
- **Technical specifications** for capability assessment
- **Ownership chains** for relationship mapping
- **Citation networks** for knowledge flows
- **Geographic data** for collaboration analysis
- **Classification codes** for technology tracking
- **Legal events** for status monitoring

This data enables objective analysis of technology development, international collaborations, and potential dual-use concerns through documented facts rather than speculation.

---

*Last Updated: September 18, 2025*
*Next Review: October 1, 2025*

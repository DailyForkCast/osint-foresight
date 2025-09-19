# Manual Trademark & Patent Search Process for Italian Technology Companies

**Document Version:** 1.0
**Created:** 2025-09-16
**Purpose:** Step-by-step guide for compliant data collection from official IP databases

---

## Table of Contents
1. [Overview](#overview)
2. [Trademark Searches](#trademark-searches)
3. [Patent Searches](#patent-searches)
4. [Data Export Standards](#data-export-standards)
5. [File Naming Convention](#file-naming-convention)
6. [Quality Checklist](#quality-checklist)

---

## Overview

This document provides a standardized process for manually searching and exporting intellectual property data for Italian technology companies. All methods described are fully compliant with database terms of service.

### Target Companies

**Tier 1 - Defense & Aerospace**
- Leonardo S.p.A. (formerly Finmeccanica)
- Fincantieri S.p.A.
- Thales Alenia Space Italia
- Telespazio S.p.A.
- Avio S.p.A.

**Tier 2 - Technology & Electronics**
- STMicroelectronics
- Datalogic S.p.A.
- Engineering Ingegneria Informatica
- Reply S.p.A.
- Prysmian Group

**Tier 3 - Industrial & Energy**
- Ansaldo Energia
- Danieli & C.
- IMA Group
- Maire Tecnimont

---

## Trademark Searches

### 1. EUIPO eSearch (Primary Source for EU Trademarks)

**URL:** https://euipo.europa.eu/eSearch/

#### Search Process:
1. Navigate to Advanced Search
2. Select "Trade marks" tab
3. Enter search parameters:
   - **Proprietor name:** Company name (e.g., "Leonardo")
   - **Proprietor country:** IT (Italy)
   - **Nice Classification:**
     - Class 9 (Scientific/Computing)
     - Class 12 (Vehicles/Defense)
     - Class 35 (Business Services)
     - Class 38 (Telecommunications)
     - Class 42 (Technology Services)
4. Set date range (recommended: 2015-present for recent activity)
5. Click "Search"

#### Export Process:
1. Select relevant results (checkbox)
2. Click "Export" button
3. Choose format:
   - **Recommended:** CSV (for data aggregation)
   - **Alternative:** Excel (for immediate analysis)
4. Select fields to export:
   - ✓ Application/Registration number
   - ✓ Trade mark name
   - ✓ Proprietor name
   - ✓ Filing date
   - ✓ Nice classes
   - ✓ Status
   - ✓ Territory
5. Download file

#### Expected Output:
CSV file with 50-500 records per major company

### 2. WIPO Global Brand Database

**URL:** https://www3.wipo.int/branddb/en/

#### Search Process:
1. Click "Search by" → "Name"
2. Enter parameters:
   - **Holder:** Company name
   - **Holder Address Country:** IT
3. Filter by:
   - **Origin:** EM (European Union)
   - **Status:** Active
   - **Nice Class:** 9, 12, 35, 38, 42
4. Execute search

#### Export Process:
1. Click "Export" icon
2. Select "Current result list"
3. Choose "CSV" format
4. Download (max 10,000 records)

### 3. Italian UIBM Database

**URL:** https://www.uibm.gov.it/bancadati/

#### Search Process:
1. Select "Marchi" (Trademarks)
2. Enter "Titolare" (Owner): Company name
3. Set "Stato" (Status): "Registrato" (Registered)
4. Search

#### Export Process:
1. Select results
2. Export to Excel/CSV
3. Save with UTF-8 encoding for Italian characters

---

## Patent Searches

### 1. Espacenet (European Patent Office)

**URL:** https://worldwide.espacenet.com/

#### Search Process:
1. Select "Advanced search"
2. Enter parameters:
   - **Applicant:** Company name
   - **Country:** IT
   - **Publication date:** 20150101 to 20251231
   - **IPC Classification:** (for technology filtering)
     - H01L (Semiconductors)
     - G06F (Computing)
     - B64 (Aerospace)
     - F41 (Weapons)
3. Execute search

#### Export Process:
1. Select results (max 500 at a time)
2. Click "Export"
3. Choose "CSV" or "XLS"
4. Select fields:
   - Publication number
   - Title
   - Applicant
   - Filing date
   - IPC codes
   - Abstract

### 2. Google Patents

**URL:** https://patents.google.com/

#### Search Process:
1. Advanced search:
   ```
   assignee:"Leonardo" OR assignee:"Finmeccanica"
   country:IT OR country:EP
   after:filing:2015
   ```
2. Filter by:
   - Patent Office: EPO, IT
   - Status: Active
   - Type: Patent/Application

#### Export Process:
1. Select "Download" → "CSV"
2. Choose up to 1000 results
3. Download includes:
   - Patent ID
   - Title
   - Assignee
   - Filing/Priority dates
   - Classifications

---

## Data Export Standards

### File Structure Requirements

#### Trademark Files Must Include:
- Application/Registration Number
- Mark Name/Text
- Owner/Proprietor
- Filing Date
- Nice Classes
- Status
- Territory/Jurisdiction

#### Patent Files Must Include:
- Publication Number
- Title
- Applicant/Assignee
- Filing Date
- Priority Date
- IPC/CPC Classifications
- Abstract (if available)
- Legal Status

### Data Quality Standards

1. **Completeness**: Minimum 80% of fields populated
2. **Date Format**: YYYY-MM-DD (ISO 8601)
3. **Encoding**: UTF-8 for all files
4. **Duplicates**: Remove before saving
5. **Company Names**: Standardize variations
   - "Leonardo S.p.A." = "Leonardo SpA" = "Leonardo"
   - Document variations in separate column

---

## File Naming Convention

### Format:
`[SOURCE]_[COMPANY]_[TYPE]_[DATERANGE]_[EXPORTDATE].csv`

### Examples:
- `EUIPO_Leonardo_TM_2015-2025_20250916.csv`
- `EPO_STMicro_Patents_2020-2025_20250916.csv`
- `WIPO_Fincantieri_TM_2018-2025_20250916.csv`

### Directory Structure:
```
data/collected/
├── trademarks/
│   ├── euipo/
│   ├── wipo/
│   └── uibm/
├── patents/
│   ├── epo/
│   ├── google/
│   └── wipo/
└── aggregated/
    └── [processed files]
```

---

## Quality Checklist

### Before Export:
- [ ] Correct company name spelling
- [ ] Appropriate date range (recommend 5-10 years)
- [ ] Relevant classifications selected
- [ ] Status filters applied (active/registered)
- [ ] Territory filters set (EU/IT focus)

### After Export:
- [ ] File saved with correct naming convention
- [ ] CSV format verified (comma-separated)
- [ ] UTF-8 encoding confirmed
- [ ] Record count logged
- [ ] Spot check 5 records for accuracy
- [ ] No sensitive/restricted data included

### Documentation:
- [ ] Search parameters recorded
- [ ] Export date/time noted
- [ ] Number of records documented
- [ ] Any anomalies or gaps identified
- [ ] File location confirmed

---

## Search Tips & Best Practices

### 1. Company Name Variations
Always search multiple variations:
- Full legal name: "Leonardo S.p.A."
- Common name: "Leonardo"
- Former names: "Finmeccanica"
- Subsidiaries: "Leonardo Electronics"

### 2. Date Ranges
- Recent activity: Last 5 years
- Historical analysis: 10-15 years
- Trend analysis: Year-by-year exports

### 3. Classification Codes
**Technology-relevant Nice Classes (Trademarks):**
- Class 9: Scientific, electronic, software
- Class 12: Vehicles, aircraft, vessels
- Class 35: Business, data processing
- Class 38: Telecommunications
- Class 42: Scientific/technological services

**Technology-relevant IPC Codes (Patents):**
- B64: Aircraft, aviation
- F41: Weapons
- G06: Computing
- H01: Electronic components
- H04: Electronic communication

### 4. Export Limits
- EUIPO: 500 records per export
- WIPO: 10,000 records per export
- Espacenet: 500 records per export
- Google Patents: 1,000 records per export

### 5. Rate Limiting
- Wait 5-10 seconds between searches
- Maximum 100 searches per hour
- Avoid automated tools/scripts

---

## Troubleshooting

### Common Issues:

**Problem:** No results found
- Try simpler company name
- Remove special characters
- Check spelling variations
- Broaden date range

**Problem:** Too many results
- Add classification filters
- Narrow date range
- Filter by status (active only)
- Use advanced search operators

**Problem:** Export fails
- Reduce number of records
- Try different format (CSV vs XLS)
- Check browser settings
- Clear cache/cookies

**Problem:** Character encoding issues
- Save as UTF-8
- Use LibreOffice for opening
- Check language settings

---

## Next Steps

After completing searches and exports:

1. **Organize Files**: Place in correct directory structure
2. **Run Aggregator**: Use `csv_aggregator.py` to combine files
3. **Data Validation**: Check for completeness and accuracy
4. **Analysis**: Run analysis scripts on aggregated data
5. **Reporting**: Generate insights for technology assessment

---

## Compliance Note

All search and export methods described in this document:
- Use official database interfaces
- Comply with terms of service
- Respect rate limits
- Use built-in export features
- Do not involve web scraping
- Are suitable for commercial research

---

**Document maintained by:** OSINT Foresight Team
**Last updated:** 2025-09-16
**Review schedule:** Quarterly

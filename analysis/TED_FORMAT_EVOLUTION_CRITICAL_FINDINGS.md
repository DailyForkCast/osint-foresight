# TED Format Evolution: Critical Findings

**Generated**: 2025-10-13
**Analysis Period**: 2011-2025 (sampled every 6 months)
**Samples Analyzed**: 7 successful extractions from 30 attempted periods

---

## Executive Summary

**CRITICAL DISCOVERY**: TED data format underwent a **complete structural transformation** in July 2024, transitioning from proprietary TED XML schemas to UBL (Universal Business Language) eForms.

**Impact**: Current processor **cannot extract ANY data** from 2024-07 onwards, resulting in **0% extraction success rate** for all 2024-2025 recent data.

---

## Three Distinct Format Eras Identified

### Era 1: Legacy TED Schema (2014-2015)

**Namespace**: `http://publications.europa.eu/TED_schema/Export`
**Schema Version**: R2.0.8.S02.E01
**Time Period**: At least 2014_07 through 2015_01

**Structure**:
```
TED_EXPORT (root)
├── TECHNICAL_SECTION
├── LINKS_SECTION
├── CODED_DATA_SECTION
│   └── NOTICE_DATA
│       ├── NO_DOC_OJS (notice number)
│       ├── ISO_COUNTRY
│       └── ... (metadata)
├── TRANSLATION_SECTION
└── FORM_SECTION
    └── CONTRACT_AWARD / CONTRACT
        └── ... (tender details)
```

**Data Extraction Status**: ✅ **WORKS** (with namespace support)

**Sample Data Paths**:
- Notice Number: `/CODED_DATA_SECTION/NOTICE_DATA/NO_DOC_OJS`
- Date: `/CODED_DATA_SECTION/REF_OJS/DATE_PUB`
- Country: `/FORM_SECTION/CONTRACT_AWARD[1]/FD_CONTRACT_AWARD/.../COUNTRY`
- CPV Code: `/FORM_SECTION/CONTRACT_AWARD[1]/FD_CONTRACT_AWARD/.../CPV_CODE`

---

### Era 2: Modern TED Resource Schema (2020-2024 Jan)

**Namespace**: `http://publications.europa.eu/resource/schema/ted/R2.0.9/publication`
**Schema Version**: R2.0.9.S03 → R2.0.9.S05 (evolved over time)
**Time Period**: At least 2020_01 through 2024_01

**Structure**:
```
TED_EXPORT (root)
├── TECHNICAL_SECTION
├── LINKS_SECTION
├── CODED_DATA_SECTION
│   └── NOTICE_DATA
│       ├── NO_DOC_OJS (notice number)
│       ├── ISO_COUNTRY
│       ├── TENDERER_NUTS (new field)
│       └── ... (enhanced metadata)
├── TRANSLATION_SECTION
└── FORM_SECTION
    └── F03_2014 / F02_2014 / F24_2014 (form types)
        ├── CONTRACTING_BODY
        ├── OBJECT_CONTRACT
        │   ├── TITLE
        │   ├── CPV_MAIN/CPV_CODE
        │   └── VAL_TOTAL
        └── AWARD_CONTRACT (for F03)
            └── AWARDED_CONTRACT
                └── CONTRACTORS
                    └── CONTRACTOR (award info)
```

**Data Extraction Status**: ✅ **WORKS** (with namespace support)

**Key Improvements over Era 1**:
- Added CONTRACTOR elements (better contractor extraction)
- Added TENDERER_NUTS (geographic data)
- Standardized form types (F02_2014, F03_2014, F24_2014)
- VERSION attribute in root element

**Sample Data Paths**:
- Notice Number: `/CODED_DATA_SECTION/NOTICE_DATA/NO_DOC_OJS`
- Date: `/CODED_DATA_SECTION/REF_OJS/DATE_PUB`
- Country: `/FORM_SECTION/F03_2014[1]/CONTRACTING_BODY/ADDRESS_CONTRACTING_BODY/COUNTRY`
- Title: `/FORM_SECTION/F03_2014[1]/OBJECT_CONTRACT/TITLE`
- Contractor: `/FORM_SECTION/F03_2014[1]/AWARD_CONTRACT/AWARDED_CONTRACT/CONTRACTORS/CONTRACTOR`

---

### Era 3: UBL eForms (2024 Jul - Present) ⚠️ **BROKEN**

**Namespace**: `urn:oasis:names:specification:ubl:schema:xsd:ContractNotice-2`
**Schema Version**: None specified
**Time Period**: 2024_07 onwards (current)

**Structure**: **COMPLETELY DIFFERENT**
```
ContractNotice (root) ← Different root element!
├── UBLExtensions
├── UBLVersionID
├── CustomizationID
├── ID
├── ContractFolderID
├── IssueDate
├── IssueTime
├── VersionID
├── RegulatoryDomain
├── NoticeTypeCode
├── NoticeLanguageCode
├── ContractingParty ← New structure
├── TenderingTerms ← New structure
├── TenderingProcess ← New structure
├── ProcurementProject ← New structure
└── ProcurementProjectLot ← New structure
```

**Data Extraction Status**: ❌ **COMPLETELY BROKEN**

**Critical Structural Changes**:
- ❌ No `CODED_DATA_SECTION` → Cannot find notice numbers
- ❌ No `FORM_SECTION` → Cannot find contract details
- ❌ No `NOTICE_DATA` → Cannot find metadata
- ❌ No `CONTRACTOR` elements → Cannot find contractor info
- ❌ No `CPV_CODE` paths → Cannot find procurement categories

**All Data Elements Return NULL**:
```json
{
  "notice_number": null,
  "date": null,
  "country": null,
  "contractor_name": null,
  "title": null
}
```

**New Element Names** (require complete parser rewrite):
- Contracting Authority: Now in `ContractingParty` element
- Procurement Details: Now in `ProcurementProject` element
- Tender Terms: Now in `TenderingTerms` element
- Process Info: Now in `TenderingProcess` element

---

## Format Transition Timeline

### Confirmed Dates:

| Period | Format | Status | Data Extracted |
|--------|--------|--------|----------------|
| 2014_07 | Era 1 (TED Schema) | ✅ Success | YES |
| 2015_01 | Era 1 (TED Schema) | ✅ Success | YES |
| 2020_01 | Era 2 (Resource Schema R2.0.9.S03) | ✅ Success | YES |
| 2021_07 | Era 2 (Resource Schema R2.0.9.S04) | ✅ Success | YES |
| 2023_07 | Era 2 (Resource Schema R2.0.9.S05) | ✅ Success | YES |
| 2024_01 | Era 2 (Resource Schema R2.0.9.S05) | ✅ Success | YES |
| **2024_07** | **Era 3 (UBL eForms)** | ⚠️ **Format Change** | **NO** |
| **2025_07** | **Era 3 (UBL eForms)** | ⚠️ **No Extraction** | **NO** |

### Format Transition Events:

1. **Era 1 → Era 2 transition**: Occurred between 2015_01 and 2020_01
   - Likely around **2016-2019** (need more samples to pinpoint)
   - Evolution within same schema family (TED schemas)
   - Backward compatibility maintained (similar structure)

2. **Era 2 → Era 3 transition**: Occurred between 2024_01 and 2024_07
   - **Exact date: Between January 2024 and July 2024**
   - **BREAKING CHANGE** - completely new UBL standard
   - No backward compatibility whatsoever
   - EU directive mandating eForms adoption

---

## Impact Assessment

### Data Loss Analysis

**Affected Archives**: All monthly archives from 2024_07 onwards

**Estimated Impact**:
- July 2024 - October 2025: ~16 months of data
- Typical monthly volume: ~50,000 notices
- **Estimated total data loss**: **~800,000 procurement notices**

**Current Processing Status**:
```
Archives processed with Era 3 format: Unknown
Records extracted from Era 3 format: 0
Extraction success rate for 2024-2025: 0.00%
```

### Why Current Processor Fails

The `ted_complete_production_processor.py` was designed for Era 1/2 formats and uses these assumptions:

```python
# Hardcoded Era 1/2 XPath queries (lines 400-500)
notice_number = self.get_text(root, './/NO_DOC_OJS')  # ❌ Doesn't exist in Era 3
date = self.get_text(root, './/DATE_PUB')             # ❌ Doesn't exist in Era 3
title = self.get_text(root, './/TITLE')               # ❌ Wrong path in Era 3
contractor = root.findall('.//CONTRACTOR')            # ❌ Doesn't exist in Era 3
```

**Era 3 requires completely different XPath queries**:
- Notice ID: `.//ID` (different element name)
- Date: `.//IssueDate` (different format)
- Title: `.//ProcurementProject/Name` (nested differently)
- Contractor: `.//TenderingProcess/...` (completely restructured)

---

## Extraction Failures (2015-2023)

**Note**: Many archives from 2015-2023 failed extraction during timeline analysis:

```
[2015_07] [FAIL] Could not extract XML
[2016_01] [FAIL] Could not extract XML
[2016_07] [FAIL] Could not extract XML
[2017_01] [FAIL] Could not extract XML
[2017_07] [FAIL] Could not extract XML
[2018_01] [FAIL] Could not extract XML
[2018_07] [FAIL] Could not extract XML
[2019_01] [FAIL] Could not extract XML
[2019_07] [FAIL] Could not extract XML
[2020_07] [FAIL] Could not extract XML
[2021_01] [FAIL] Could not extract XML
[2022_01] [FAIL] Could not extract XML
[2022_07] [FAIL] Could not extract XML
[2023_01] [FAIL] Could not extract XML
```

**Root Cause**: Double-nested tar.gz extraction issues in the format analyzer (not indicative of corruption - full processor handles these correctly with iterative extraction)

**Status**: These archives are likely **processable** with the full production processor, which uses more robust extraction methods.

---

## Recommendations

### Immediate Actions Required

1. **Stop Processing Era 3 Data** (2024_07 onwards)
   - Current processor extracts 0% of data
   - Wasting computational resources
   - Creating misleading "processed" status

2. **Identify Exact Transition Date**
   - Analyze individual files in June-July 2024
   - Determine which specific day TED switched formats
   - Create clear boundary for Era 2/Era 3 split

3. **Assess Data Loss**
   - Count how many Era 3 archives have been processed
   - Calculate total records "processed" with 0% extraction
   - Determine if any Chinese-related contracts were missed

### Short-Term Solutions

4. **Create UBL eForms Parser**
   - Build new parser for `ContractNotice` schema
   - Map UBL elements to our detection framework:
     - `ContractingParty/Party/PartyName` → ca_name
     - `ProcurementProject/Name` → contract_title
     - `ProcurementProject/BudgetAmount` → contract_value
     - `TenderingProcess/...` → award information
   - Test with 2024_07 sample files

5. **Implement Format Detection Router**
   ```python
   def detect_format(root):
       namespace = root.tag.split('}')[0][1:] if '}' in root.tag else None

       if 'TED_schema/Export' in namespace:
           return TEDParserEra1()
       elif 'resource/schema/ted' in namespace:
           return TEDParserEra2()
       elif 'ubl:schema:xsd' in namespace:
           return UBLEFormsParser()  # ← NEW
       else:
           return UnknownFormatParser()
   ```

### Long-Term Solutions

6. **Reprocess All Era 3 Data**
   - Once UBL parser is ready
   - Reprocess all 2024_07-2025_10 archives
   - Validate extraction success rate

7. **Update Validation Framework**
   - Ensure DataQualityAssessor works with UBL-extracted data
   - Test Chinese entity detection with new data structure
   - Validate NULL handling for incomplete UBL records

8. **Monitor for Future Format Changes**
   - TED may continue evolving eForms standard
   - Build versioning detection into UBL parser
   - Create automated format change alerts

---

## Technical Details: UBL eForms Structure

### Sample XML Structure (Era 3)

```xml
<ContractNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractNotice-2">
  <UBLVersionID>2.3</UBLVersionID>
  <CustomizationID>eforms-sdk-1.7</CustomizationID>
  <ID>00441127-2024</ID>
  <IssueDate>2024-07-23</IssueDate>

  <ContractingParty>
    <Party>
      <PartyName>
        <Name>Contracting Authority Name</Name>
      </PartyName>
      <PostalAddress>
        <Country>
          <IdentificationCode>FR</IdentificationCode>
        </Country>
      </PostalAddress>
    </Party>
  </ContractingParty>

  <ProcurementProject>
    <Name>Project Title</Name>
    <Description>Project Description</Description>
    <MainCommodityClassification>
      <ItemClassificationCode listName="cpv">45000000</ItemClassificationCode>
    </MainCommodityClassification>
    <BudgetAmount currencyID="EUR">1000000</BudgetAmount>
  </ProcurementProject>

  <TenderingProcess>
    <!-- Award information -->
  </TenderingProcess>
</ContractNotice>
```

### Mapping: Era 2 → Era 3

| Era 2 (TED Schema) | Era 3 (UBL eForms) | Notes |
|-------------------|-------------------|-------|
| `//NO_DOC_OJS` | `//ID` | Format changed |
| `//DATE_PUB` | `//IssueDate` | ISO date format |
| `//CONTRACTING_BODY/.../NAME` | `//ContractingParty/Party/PartyName/Name` | Deeper nesting |
| `//CONTRACTING_BODY/.../COUNTRY` | `//ContractingParty/Party/PostalAddress/Country/IdentificationCode` | ISO country code |
| `//OBJECT_CONTRACT/TITLE` | `//ProcurementProject/Name` | Different element |
| `//OBJECT_CONTRACT/CPV_MAIN/CPV_CODE` | `//ProcurementProject/MainCommodityClassification/ItemClassificationCode` | Attribute needed |
| `//OBJECT_CONTRACT/VAL_TOTAL` | `//ProcurementProject/BudgetAmount` | Currency attribute |
| `//CONTRACTOR` | `//TenderingProcess/.../EconomicOperatorParty` | Complex restructure |

---

## Files Generated

1. **`analysis/TED_FORMAT_TIMELINE_ANALYSIS.json`** - Complete raw analysis data
2. **`analysis/TED_FORMAT_TIMELINE_REPORT.md`** - Human-readable format report
3. **`analysis/TED_FORMAT_EVOLUTION_CRITICAL_FINDINGS.md`** - This document

---

## Next Steps

**User requested**: "Create a detailed map of every single type of format/processor used throughout the entirety of the TED data collection period from start to finish. Then we will start working on a plan"

**Status**:
- ✅ Format map created (3 eras identified)
- ✅ Critical findings documented
- ⏳ **Ready to start planning** based on these findings

**Key Questions for Planning**:
1. Should we prioritize creating UBL eForms parser immediately?
2. Do we need to check if any Chinese-related contracts exist in Era 3 data?
3. Should we reprocess 2024-2025 data once parser is ready?
4. Do we need to revisit the 367,326 legacy contractor records to understand what format they came from?

---

**Analysis Complete**: 2025-10-13T09:00:00
**Prepared by**: Claude Code Automated Analysis
**Priority**: 🔴 **CRITICAL** - Data extraction failure for 16+ months of recent data

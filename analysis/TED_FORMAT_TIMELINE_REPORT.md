# TED XML Format Timeline Analysis
**Generated**: 2025-10-13T08:53:56.010504
**Periods Analyzed**: 30

---

## Format Groups Identified: 3

### Format Group 1

**Namespace**: `http://publications.europa.eu/TED_schema/Export`

**Schema**: `http://publications.europa.eu/TED_schema/Export/R2.0.8.S02.E01 TED_EXPORT.xsd`

**Time Period**: 2014_07 to 2015_01 (2 samples)

**Structure**:
- Top-level elements: TECHNICAL_SECTION, LINKS_SECTION, CODED_DATA_SECTION, TRANSLATION_SECTION, FORM_SECTION
- Has CODED_DATA_SECTION: True
- Has FORM_SECTION: True
- Has NOTICE_DATA: True

**Data Element Locations**:
- NO_DOC_OJS: `/CODED_DATA_SECTION/NOTICE_DATA/NO_DOC_OJS`
- DATE_PUB: `/CODED_DATA_SECTION/REF_OJS/DATE_PUB`
- COUNTRY: `/FORM_SECTION/CONTRACT_AWARD[1]/FD_CONTRACT_AWARD/CONTRACTING_AUTHORITY_INFORMATION_CONTRACT_AWARD/NAME_ADDRESSES_CONTACT_CONTRACT_AWARD/CA_CE_CONCESSIONAIRE_PROFILE/COUNTRY`
- CPV_CODE: `/FORM_SECTION/CONTRACT_AWARD[1]/FD_CONTRACT_AWARD/OBJECT_CONTRACT_INFORMATION_CONTRACT_AWARD_NOTICE/DESCRIPTION_AWARD_NOTICE_INFORMATION/CPV/CPV_MAIN/CPV_CODE`

**Sample Data Found**:
- notice_number: `2014/S 123-218274`
- date: `20140701`
- country: `GR`

---

### Format Group 2

**Namespace**: `http://publications.europa.eu/resource/schema/ted/R2.0.9/publication`

**Schema**: `http://publications.europa.eu/resource/schema/ted/R2.0.9/publication TED_EXPORT.xsd`

**Time Period**: 2020_01 to 2024_01 (4 samples)

**Structure**:
- Top-level elements: TECHNICAL_SECTION, LINKS_SECTION, CODED_DATA_SECTION, TRANSLATION_SECTION, FORM_SECTION
- Has CODED_DATA_SECTION: True
- Has FORM_SECTION: True
- Has NOTICE_DATA: True

**Data Element Locations**:
- NO_DOC_OJS: `/CODED_DATA_SECTION/NOTICE_DATA/NO_DOC_OJS`
- DATE_PUB: `/CODED_DATA_SECTION/REF_OJS/DATE_PUB`
- CONTRACTOR: `/FORM_SECTION/F03_2014[1]/AWARD_CONTRACT/AWARDED_CONTRACT/CONTRACTORS/CONTRACTOR`
- COUNTRY: `/FORM_SECTION/F03_2014[1]/CONTRACTING_BODY/ADDRESS_CONTRACTING_BODY/COUNTRY`
- TITLE: `/FORM_SECTION/F03_2014[1]/OBJECT_CONTRACT/TITLE`
- CPV_CODE: `/FORM_SECTION/F03_2014[1]/OBJECT_CONTRACT/CPV_MAIN/CPV_CODE`
- VAL_TOTAL: `/FORM_SECTION/F03_2014[1]/OBJECT_CONTRACT/VAL_TOTAL`

**Sample Data Found**:
- notice_number: `2020/S 022-046946`
- date: `20200131`
- country: `HU`

---

### Format Group 3

**Namespace**: `urn:oasis:names:specification:ubl:schema:xsd:ContractNotice-2`

**Schema**: `None`

**Time Period**: 2024_07 to 2025_07 (2 samples)

**Structure**:
- Top-level elements: UBLExtensions, UBLVersionID, CustomizationID, ID, ContractFolderID, IssueDate, IssueTime, VersionID, RegulatoryDomain, NoticeTypeCode, NoticeLanguageCode, ContractingParty, TenderingTerms, TenderingProcess, ProcurementProject, ProcurementProjectLot
- Has CODED_DATA_SECTION: False
- Has FORM_SECTION: False
- Has NOTICE_DATA: False

**Data Element Locations**:

**Sample Data Found**:

---


# USAspending Database - Complete Schema (206 Columns)

**Total Columns**: 206
**Analysis Date**: 2025-10-11
**Source**: USAspending PostgreSQL database export

---

## Executive Summary

This schema represents the complete structure of USAspending transaction data, which includes federal contracts, grants, loans, and other financial assistance.

### Key Field Categories:

- **Location**: 46 fields
- **Agency**: 38 fields
- **Subaward**: 30 fields
- **Transaction**: 29 fields
- **Recipient**: 24 fields
- **Financial**: 14 fields
- **Classification**: 12 fields
- **Description**: 3 fields
- **Contract**: 3 fields
- **Search**: 3 fields
- **Timestamp**: 2 fields
- **System**: 2 fields

---

## Table of Contents

- [Agency](#agency) (38 fields)
- [Classification](#classification) (12 fields)
- [Contract](#contract) (3 fields)
- [Description](#description) (3 fields)
- [Financial](#financial) (14 fields)
- [Location](#location) (46 fields)
- [Recipient](#recipient) (24 fields)
- [Search](#search) (3 fields)
- [Subaward](#subaward) (30 fields)
- [System](#system) (2 fields)
- [Timestamp](#timestamp) (2 fields)
- [Transaction](#transaction) (29 fields)

---

## Agency

**Total Fields**: 38

### [9] `funding_toptier_agency_id`

**Description**: Funding agency top-tier code

**Sample Values**:
- `097`
- `049`
- `047`

### [10] `funding_toptier_agency_name`

**Description**: Funding agency top-tier name

**Sample Values**:
- `Department of Defense (DOD)`
- `National Science Foundation (NSF)`
- `General Services Administration (GSA)`

### [11] `funding_subtier_agency_code`

**Description**: Funding agency subtier code

**Sample Values**:
- `97AK`
- `4900`
- `4732`

### [12] `funding_subtier_agency_name`

**Description**: Funding agency subtier name

**Sample Values**:
- `DEFENSE INFORMATION SYSTEMS AGENCY (DISA)`
- `National Science Foundation`
- `FEDERAL ACQUISITION SERVICE`

### [13] `funding_office_code`

**Description**: Funding office code

**Sample Values**:
- `HC1084`
- `490505`
- `47QFLA`

### [14] `funding_office_name`

**Description**: Funding office name

**Sample Values**:
- `IT CONTRACTING DIVISION - PL84`
- `DIV OF COMPUTER  NETWORK SYSTEMS`
- `GSA FAS AAS REGION 5`

### [15] `awarding_toptier_agency_id`

**Description**: Awarding agency top-tier code

**Sample Values**:
- `097`
- `049`
- `485`

### [16] `awarding_toptier_agency_name`

**Description**: Awarding agency top-tier name

**Sample Values**:
- `Department of Defense (DOD)`
- `National Science Foundation (NSF)`
- `Corporation for National and Community Service (CNCS)`

### [17] `awarding_subtier_agency_code`

**Description**: Awarding agency subtier code

**Sample Values**:
- `2100`
- `4900`
- `1700`

### [18] `awarding_subtier_agency_name`

**Description**: Awarding agency subtier name

**Sample Values**:
- `DEPT OF THE ARMY`
- `National Science Foundation`
- `DEPT OF THE NAVY`

### [19] `awarding_office_code`

**Description**: Awarding office code

**Sample Values**:
- `W910NZ`
- `490505`
- `M95450`

### [20] `awarding_office_name`

**Description**: Awarding office name

**Sample Values**:
- `USA PEO, COMMAND CONTROL AND COMMUN`
- `DIV OF COMPUTER  NETWORK SYSTEMS`
- `COMMANDER`

### [93] `awarding_agency_code`

**Description**: Awarding agency code

*No non-null values in sample*

### [99] `funding_agency_code`

**Description**: Funding agency code

**Sample Values**:
- `9700`
- `4732`

### [100] `funding_agency_name`

**Description**: Funding agency name

**Sample Values**:
- `9700`
- `4732`

### [101] `funding_sub_agency_code`

**Description**: Funding sub-agency code

**Sample Values**:
- `4900`
- `9577`
- `7529`

### [102] `funding_sub_agency_name`

**Description**: Funding sub-agency name

**Sample Values**:
- `National Science Foundation`
- `Corporation for National and Community Service`
- `National Institutes of Health`

### [103] `funding_office_code_2`

**Description**: Funding office code (duplicate)

**Sample Values**:
- `4900`
- `9577`
- `7529`

### [104] `funding_office_name_2`

**Description**: Funding office name (duplicate)

*No non-null values in sample*

### [105] `awarding_agency_code_2`

**Description**: Awarding agency code (duplicate)

*No non-null values in sample*

### [106] `awarding_agency_name_2`

**Description**: Awarding agency name (duplicate)

*No non-null values in sample*

### [107] `awarding_sub_agency_code`

**Description**: Awarding sub-agency code

*No non-null values in sample*

### [108] `awarding_sub_agency_name`

**Description**: Awarding sub-agency name

*No non-null values in sample*

### [109] `awarding_office_code_2`

**Description**: Awarding office code (duplicate)

*No non-null values in sample*

### [122] `funding_agency_code_3`

**Description**: Funding agency code (3rd instance)

**Sample Values**:
- `97AK`
- `4900`
- `4732`

### [123] `funding_agency_name_3`

**Description**: Funding agency name (3rd instance)

**Sample Values**:
- `DEFENSE INFORMATION SYSTEMS AGENCY (DISA)`
- `National Science Foundation`
- `FEDERAL ACQUISITION SERVICE`

### [124] `funding_sub_agency_code_2`

**Description**: Funding sub-agency code (2nd instance)

**Sample Values**:
- `2100`
- `4900`
- `1700`

### [125] `funding_sub_agency_name_2`

**Description**: Funding sub-agency name (2nd instance)

**Sample Values**:
- `DEPT OF THE ARMY`
- `National Science Foundation`
- `DEPT OF THE NAVY`

### [142] `awarding_agency_name_4`

**Description**: Awarding agency name (4th instance)

**Sample Values**:
- `Department of Defense`
- `National Science Foundation`
- `General Services Administration`

### [143] `awarding_agency_code_4`

**Description**: Awarding agency code (4th instance)

**Sample Values**:
- `DOD`
- `NSF`
- `GSA`

### [144] `awarding_sub_agency_name_3`

**Description**: Awarding sub-agency name (3rd instance)

**Sample Values**:
- `Defense Information Systems Agency`
- `National Science Foundation`
- `Federal Acquisition Service`

### [145] `awarding_sub_agency_code_2`

**Description**: Awarding sub-agency code (2nd instance)

**Sample Values**:
- `DISA`
- `NSF`
- `FAS`

### [146] `funding_agency_name_4`

**Description**: Funding agency name (4th instance)

**Sample Values**:
- `Department of Defense`
- `National Science Foundation`
- `Corporation for National and Community Service`

### [147] `funding_agency_code_4`

**Description**: Funding agency code (4th instance)

**Sample Values**:
- `DOD`
- `NSF`
- `CNCS`

### [148] `funding_sub_agency_name_3`

**Description**: Funding sub-agency name (3rd instance)

**Sample Values**:
- `Department of the Army`
- `National Science Foundation`
- `Department of the Navy`

### [149] `funding_sub_agency_code_3`

**Description**: Funding sub-agency code (3rd instance)

**Sample Values**:
- `USA`
- `NSF`
- `USN`

### [204] `awarding_toptier_agency_code`

**Description**: Awarding top-tier agency code (clean)

**Sample Values**:
- `097`
- `049`
- `047`

### [205] `funding_toptier_agency_code`

**Description**: Funding top-tier agency code (clean)

**Sample Values**:
- `097`
- `049`
- `485`

---

## Classification

**Total Fields**: 12

### [47] `naics_code`

**Description**: NAICS industry classification code

**Sample Values**:
- `334111`
- `334220`
- `336413`

### [48] `naics_description`

**Description**: NAICS industry description

**Sample Values**:
- `ELECTRONIC COMPUTER MANUFACTURING`
- `RADIO AND TELEVISION BROADCASTING AND WIRELESS COMMUNICATIONS EQUIPMENT MANUFACT...`
- `OTHER AIRCRAFT PARTS AND AUXILIARY EQUIPMENT MANUFACTURING`

### [49] `cfda_number`

**Description**: CFDA program number (grants)

**Sample Values**:
- `47.070`
- `94.006`
- `93.361, 93.837`

### [50] `cfda_title`

**Description**: CFDA program title (grants)

**Sample Values**:
- `Computer and Information Science and Engineering`
- `AmeriCorps State and National 94.006`
- `Cardiovascular Diseases Research, Nursing Research`

### [128] `naics_code_2`

**Description**: NAICS code (duplicate)

**Sample Values**:
- `334111`
- `334220`
- `336413`

### [129] `cfda_number_2`

**Description**: CFDA number (duplicate)

**Sample Values**:
- `47.070`
- `94.006`
- `93.361, 93.837`

### [130] `cfda_program_title`

**Description**: CFDA program title

*No non-null values in sample*

### [131] `sai_number`

**Description**: SAI number

*No non-null values in sample*

### [150] `cfda_number_3`

**Description**: CFDA number (3rd instance)

**Sample Values**:
- `47.070`
- `94.006`
- `93.361`

### [151] `cfda_title_2`

**Description**: CFDA title (2nd instance)

**Sample Values**:
- `Computer and Information Science and Engineering`
- `AmeriCorps State and National 94.006`
- `Nursing Research`

### [163] `product_or_service_code`

**Description**: PSC code

**Sample Values**:
- `7B22`
- `7G20`
- `1560`

### [164] `product_or_service_code_description`

**Description**: PSC description

**Sample Values**:
- `IT AND TELECOM - COMPUTE: SERVERS (HARDWARE AND PERPETUAL LICENSE SOFTWARE)`
- `IT AND TELECOM - NETWORK: ANALOG VOICE PRODUCTS (HARDWARE AND PERPETUAL LICENSE ...`
- `AIRFRAME STRUCTURAL COMPONENTS`

---

## Contract

**Total Fields**: 3

### [132] `type_of_contract_pricing`

**Description**: Contract pricing type

*No non-null values in sample*

### [133] `type_of_contract_pricing_desc`

**Description**: Contract pricing description

*No non-null values in sample*

### [160] `type_of_contract_pricing_code`

**Description**: Contract pricing type code

**Sample Values**:
- `J`

---

## Description

**Total Fields**: 3

### [46] `award_description`

**Description**: Description of the award/contract

**Sample Values**:
- `MFOCS PROCESSING UNIT (PU)`
- `NSF BPC-A: Institute for African-American Mentoring in Computing Sciences (iAAMC...`
- `L3 SOLE SOURCE IDIQ TO35 MCSC  LINK 16`

### [82] `subaward_description`

**Description**: Detailed sub-award description

**Sample Values**:
- `PURCHASE OF TABLET BEZELS TO SUPPORT PROGRAM PRODUCTION.`
- `THE PRIMARY GOAL OF IAAMCS IS TO INCREASE THE NUMBER OF AFRICAN AMERICAN STUDENT...`
- `PURCHASE OF DISPLAY BASE TO SUPPORT PROGRAM PRODUCTION.`

### [159] `prime_award_base_transaction_description`

**Description**: Base transaction description

**Sample Values**:
- `AWARD`

---

## Financial

**Total Fields**: 14

### [6] `federal_action_obligation`

**Description**: Transaction dollar amount

**Sample Values**:
- `89369808.72`
- `5053715.00`
- `30988171.77`

### [96] `treasury_accounts_funding_this_award`

**Description**: Treasury account codes

*No non-null values in sample*

### [97] `federal_accounts_funding_this_award`

**Description**: Federal account codes

*No non-null values in sample*

### [98] `object_classes_funding_this_award`

**Description**: Object class codes

*No non-null values in sample*

### [140] `total_dollars_obligated`

**Description**: Total dollars obligated

**Sample Values**:
- `195556480`
- `90594651`
- `225474370`

### [141] `base_and_exercised_options_value`

**Description**: Base + exercised options value

**Sample Values**:
- `2023-01-11`
- `2019-07-03`
- `2025-06-18`

### [153] `total_outlays`

**Description**: Total outlays

**Sample Values**:
- `<1M`

### [183] `treasury_account_identifiers`

**Description**: Treasury account identifier

**Sample Values**:
- `126627514`
- `51678009`
- `101926284`

### [184] `tas_rendering_label`

**Description**: TAS rendering label

**Sample Values**:
- `1217`
- `655`
- `634`

### [185] `disaster_emergency_fund_code`

**Description**: Disaster/emergency fund code

**Sample Values**:
- `1255`
- `2141`
- `1821`

### [186] `transaction_obligated_amount`

**Description**: Transaction obligated amount

**Sample Values**:
- `1188`
- `655`
- `1174`

### [200] `treasury_account_symbol`

**Description**: Treasury account symbol (JSON array)

**Sample Values**:
- `[{"code": "0801", "name": "REIMBURSABLE"}]`
- `[{"code": null, "name": null}]`
- `[{"code": "0850", "name": "ASSISTED ACQUISITION SERVICES (AAS) - FLOW-THRU"}]`

### [202] `original_loan_subsidy_cost`

**Description**: Original loan subsidy cost

**Sample Values**:
- `f7df7035-9f6d-35a6-d1dd-20a3495bb044`
- `92c7747b-7913-b56d-247a-190447a528e0`
- `e8e0fa61-c2f2-c029-d296-89b598da2d3c`

### [203] `face_value_loan_guarantee`

**Description**: Face value of loan guarantee

**Sample Values**:
- `C`
- `R`

---

## Location

**Total Fields**: 46

### [28] `recipient_location_country_code`

**Description**: Prime recipient country code

**Sample Values**:
- `USA`

### [29] `recipient_location_country_name`

**Description**: Prime recipient country name

**Sample Values**:
- `UNITED STATES`

### [30] `recipient_location_state_code`

**Description**: Prime recipient state code

**Sample Values**:
- `FL`
- `UT`
- `NY`

### [31] `recipient_location_state_name`

**Description**: Prime recipient state name

**Sample Values**:
- `FLORIDA`
- `Florida`
- `UTAH`

### [32] `recipient_location_zip_code`

**Description**: Prime recipient ZIP code

**Sample Values**:
- `329356715`
- `326111941`
- `841162925`

### [33] `recipient_location_congressional_code`

**Description**: Prime recipient congressional district

**Sample Values**:
- `08`
- `03`
- `02`

### [34] `recipient_location_county_code`

**Description**: Prime recipient county code

*No non-null values in sample*

### [35] `recipient_location_city_name`

**Description**: Prime recipient city

**Sample Values**:
- `MELBOURNE`
- `GAINESVILLE`
- `SALT LAKE CITY`

### [36] `recipient_location_address_line1`

**Description**: Prime recipient street address

**Sample Values**:
- `100 N BABCOCK ST`
- `1523 UNION RD RM 207`
- `640 N 2200 W`

### [38] `pop_country_code`

**Description**: Place of performance country code

**Sample Values**:
- `USA`

### [39] `pop_country_name`

**Description**: Place of performance country name

**Sample Values**:
- `UNITED STATES`

### [40] `pop_state_code`

**Description**: Place of performance state code

**Sample Values**:
- `FL`
- `VA`
- `NY`

### [41] `pop_state_name`

**Description**: Place of performance state name

**Sample Values**:
- `FLORIDA`
- `Florida`
- `VIRGINIA`

### [42] `pop_zip_code`

**Description**: Place of performance ZIP code

**Sample Values**:
- `329356715`
- `326112002`
- `225548808`

### [43] `pop_congressional_code`

**Description**: Place of performance congressional district

**Sample Values**:
- `08`
- `03`
- `07`

### [44] `pop_city_name`

**Description**: Place of performance city

**Sample Values**:
- `MELBOURNE`
- `GAINESVILLE`
- `STAFFORD`

### [45] `pop_address_line1`

**Description**: Place of performance address

*No non-null values in sample*

### [156] `recipient_location_state_fips`

**Description**: Recipient state FIPS code

*No non-null values in sample*

### [165] `recipient_country_code_2`

**Description**: Recipient country code (duplicate)

**Sample Values**:
- `USA`

### [166] `recipient_country_name_2`

**Description**: Recipient country name (duplicate)

**Sample Values**:
- `UNITED STATES`

### [167] `recipient_county_code`

**Description**: Recipient county code

**Sample Values**:
- `039`
- `125`
- `055`

### [168] `recipient_county_name`

**Description**: Recipient county name

**Sample Values**:
- `UNION`
- `TUSCALOOSA`
- `MONROE`

### [169] `recipient_zip_4`

**Description**: Recipient ZIP+4

**Sample Values**:
- `07036`
- `35487`
- `14623`

### [170] `recipient_zip_last4`

**Description**: Recipient ZIP last 4 digits

**Sample Values**:
- `40350`
- `77256`
- `63000`

### [171] `recipient_congressional_district`

**Description**: Recipient congressional district

**Sample Values**:
- `10`
- `07`
- `25`

### [172] `recipient_location_congressional_code_2`

**Description**: Recipient congressional code (dup)

**Sample Values**:
- `SINGLE ZIP CODE`
- `STATE-WIDE`

### [173] `pop_country_code_2`

**Description**: POP country code (duplicate)

**Sample Values**:
- `USA`

### [174] `pop_country_name_2`

**Description**: POP country name (duplicate)

**Sample Values**:
- `UNITED STATES`

### [175] `pop_county_code`

**Description**: POP county code

**Sample Values**:
- `039`
- `125`
- `047`

### [176] `pop_county_name`

**Description**: POP county name

**Sample Values**:
- `UNION`
- `TUSCALOOSA`
- `KINGS`

### [177] `pop_zip_4`

**Description**: POP ZIP+4

**Sample Values**:
- `07036`
- `35487`
- `11220`

### [178] `pop_zip_last4`

**Description**: POP ZIP last 4 digits

**Sample Values**:
- `40350`
- `77256`
- `10016`

### [179] `pop_congressional_district`

**Description**: POP congressional district

**Sample Values**:
- `10`
- `07`
- `12`

### [187] `recipient_state_code`

**Description**: Recipient state code (clean)

**Sample Values**:
- `08`
- `03`
- `02`

### [188] `recipient_state_code_2`

**Description**: Recipient state code (duplicate)

**Sample Values**:
- `08`
- `03`
- `07`

### [189] `pop_state_code_2`

**Description**: POP state code (duplicate)

**Sample Values**:
- `07`
- `25`
- `10`

### [190] `pop_state_code_3`

**Description**: POP state code (3rd instance)

**Sample Values**:
- `07`
- `10`
- `02`

### [191] `recipient_county_code_2`

**Description**: Recipient county code (duplicate)

**Sample Values**:
- `12009`
- `12001`
- `49035`

### [192] `recipient_state_code_3`

**Description**: Recipient state code (3rd instance)

**Sample Values**:
- `12`
- `49`
- `36`

### [193] `pop_county_code_2`

**Description**: POP county code (duplicate)

**Sample Values**:
- `12009`
- `12001`
- `51179`

### [194] `pop_state_code_4`

**Description**: POP state code (4th instance)

**Sample Values**:
- `12`
- `51`
- `36`

### [195] `recipient_county_name_2`

**Description**: Recipient county name (duplicate)

**Sample Values**:
- `BREVARD`
- `ALACHUA`
- `STAFFORD`

### [196] `recipient_county_code_3`

**Description**: Recipient county code (3rd instance)

**Sample Values**:
- `009`
- `001`
- `035`

### [197] `pop_county_name_2`

**Description**: POP county name (duplicate)

**Sample Values**:
- `BREVARD`
- `Alachua`
- `SALT LAKE`

### [198] `pop_county_code_3`

**Description**: POP county code (3rd instance)

**Sample Values**:
- `009`
- `001`
- `179`

### [199] `pop_county_name_3`

**Description**: POP county name (3rd instance)

**Sample Values**:
- `BREVARD`
- `Alachua`
- `STAFFORD`

---

## Recipient

**Total Fields**: 24

### [21] `recipient_duns`

**Description**: Prime recipient DUNS number

**Sample Values**:
- `969663814`
- `837322494`

### [22] `recipient_uei`

**Description**: Prime recipient Unique Entity Identifier

**Sample Values**:
- `MC27B7LGBL34`
- `NNFQH1JAPEP3`
- `FRJQGQHDX4J3`

### [23] `recipient_name`

**Description**: Prime recipient legal business name

**Sample Values**:
- `DRS NETWORK & IMAGING SYSTEMS, LLC`
- `UNIVERSITY OF FLORIDA`
- `L3 TECHNOLOGIES, INC.`

### [24] `recipient_doing_business_as_name`

**Description**: Prime recipient DBA name

**Sample Values**:
- `DIVISION OF SPONSORED RESEARCH`
- `GEORGIA STATE UNIVERSITY RESEARCH FOUNDATION INC`

### [25] `recipient_parent_duns`

**Description**: Prime recipient parent DUNS

**Sample Values**:
- `159621697`

### [26] `recipient_parent_uei`

**Description**: Prime recipient parent UEI

**Sample Values**:
- `W8PTMRME1496`
- `D4GCCCMXR1H3`
- `SJULQDJ8NZU7`

### [27] `recipient_parent_name`

**Description**: Prime recipient ultimate parent name

**Sample Values**:
- `LEONARDO DRS  INC.`
- `BOARD OF GOVERNERS STATE UNIVERSITY SYSTEM OF FLORIDA`
- `L3 TECHNOLOGIES  INC.`

### [37] `business_categories`

**Description**: Business type classifications

**Sample Values**:
- `For Profit Organization,Limited Liability Company,Manufacturer of Goods`
- `Public/State Controlled Institution of Higher Education`
- `For Profit Organization,Manufacturer of Goods`

### [83] `business_categories_array`

**Description**: Business categories as array

*No non-null values in sample*

### [110] `officer_1_name`

**Description**: Highly compensated officer #1 name

**Sample Values**:
- `John A Baylouny`

### [111] `officer_1_amount`

**Description**: Highly compensated officer #1 amount

**Sample Values**:
- `1659238.00`

### [112] `officer_2_name`

**Description**: Highly compensated officer #2 name

**Sample Values**:
- `Mark A Dorfman`

### [113] `officer_2_amount`

**Description**: Highly compensated officer #2 amount

**Sample Values**:
- `1513173.00`

### [114] `officer_3_name`

**Description**: Highly compensated officer #3 name

**Sample Values**:
- `Michael D Dippold`

### [115] `officer_3_amount`

**Description**: Highly compensated officer #3 amount

**Sample Values**:
- `1520103.00`

### [116] `officer_4_name`

**Description**: Highly compensated officer #4 name

**Sample Values**:
- `Jason W Rinsky`

### [117] `officer_4_amount`

**Description**: Highly compensated officer #4 amount

**Sample Values**:
- `992331.00`

### [118] `officer_5_name`

**Description**: Highly compensated officer #5 name

**Sample Values**:
- `Jerry K Hathaway`

### [119] `officer_5_amount`

**Description**: Highly compensated officer #5 amount

**Sample Values**:
- `827755.00`

### [154] `recipient_name_2`

**Description**: Recipient name (duplicate)

**Sample Values**:
- `MICROCAST TECHNOLOGIES CORP.`
- `UNIVERSITY OF ALABAMA`
- `FIELDTEX PRODUCTS INC.`

### [155] `recipient_parent_name_2`

**Description**: Recipient parent name (duplicate)

**Sample Values**:
- `MICROCAST TECHNOLOGIES CORP.`
- `THE UNIVERSITY OF ALABAMA SYSTEM`
- `BOARD OF REGENTS OF THE UNIVERSITY OF NEBRASKA`

### [157] `business_types_array`

**Description**: Business types as PostgreSQL array

**Sample Values**:
- `{category_business,corporate_entity_not_tax_exempt,limited_liability_corporation...`
- `{higher_education,public_institution_of_higher_education}`
- `{category_business,corporate_entity_not_tax_exempt,manufacturer_of_goods,other_t...`

### [158] `business_categories_list`

**Description**: Business categories list

**Sample Values**:
- `{21146}`
- `{65814,72835,75617}`
- `{34823}`

### [161] `sam_exception`

**Description**: SAM exception code

*No non-null values in sample*

---

## Search

**Total Fields**: 3

### [180] `award_description_tsvector`

**Description**: Full-text search vector for award description

**Sample Values**:
- `'and':5,10 'bezels':17 'compute':7 'corp':3 'hardware':9 'it':4 'license':12 'mi...`
- `'1':101 '2':116 '3':130 'a':26,49,62 'activities':74 'administered':45 'advisor'...`
- `'and':5,10 'base':17 'compute':7 'corp':3 'display':16 'hardware':9 'it':4 'lice...`

### [181] `award_ids_tsvector`

**Description**: Full-text search vector for award IDs

**Sample Values**:
- `'10p0067116':2 'hc108422f0088':1`
- `'-03':3 '1457855':1 'ufdsp00010406':2`
- `'10p0066186':2 'hc108422f0088':1`

### [182] `recipient_name_tsvector`

**Description**: Full-text search vector for recipient name

**Sample Values**:
- `'corp':3 'microcast':1 'technologies':2`
- `'alabama':3 'of':2 'university':1`
- `'fieldtex':1 'inc':3 'products':2`

---

## Subaward

**Total Fields**: 30

### [52] `subaward_action_date_fiscal_year`

**Description**: Sub-award fiscal year

**Sample Values**:
- `2022`
- `2017`
- `2025`

### [53] `subaward_action_date_month`

**Description**: Sub-award month

**Sample Values**:
- `4`
- `10`
- `6`

### [54] `subaward_number`

**Description**: Sub-award identifier

**Sample Values**:
- `10P0067116`
- `UFDSP00010406-03`
- `10P0066186`

### [55] `subaward_amount`

**Description**: Sub-award dollar amount

**Sample Values**:
- `292593.92`
- `68215.00`
- `785622.50`

### [56] `sub_action_date`

**Description**: Sub-award action date

**Sample Values**:
- `2022-03-17`
- `2017-08-03`
- `2022-05-05`

### [57] `sub_awardee_duns`

**Description**: Sub-awardee DUNS number

**Sample Values**:
- `847706504`
- `014396969`
- `064250186`

### [58] `sub_awardee_uei`

**Description**: Sub-awardee UEI

**Sample Values**:
- `QNAYGNZRBLU6`
- `NB5EZ1F1X729`
- `CADNUR19PMM5`

### [59] `sub_awardee_name`

**Description**: Sub-awardee name

**Sample Values**:
- `MICROCAST TECHNOLOGIES CORP.`
- `UNIVERSITY OF ALABAMA`
- `FIELDTEX PRODUCTS INC.`

### [60] `sub_awardee_doing_business_as_name`

**Description**: Sub-awardee DBA name

**Sample Values**:
- `DIVISION OF SPONSORED RESEARCH`
- `OHIO STATE UNIVERSITY OFFICE OF SPONSORED PROGRAMS, THE`

### [61] `sub_awardee_parent_duns`

**Description**: Sub-awardee parent DUNS

**Sample Values**:
- `847706504`
- `007180078`

### [62] `sub_awardee_parent_uei`

**Description**: Sub-awardee parent UEI

**Sample Values**:
- `QNAYGNZRBLU6`
- `TWJWHYEM8T63`
- `WGK8J9FEKW65`

### [63] `sub_awardee_parent_name`

**Description**: Sub-awardee parent name

**Sample Values**:
- `MICROCAST TECHNOLOGIES CORP.`
- `THE UNIVERSITY OF ALABAMA SYSTEM`
- `BOARD OF REGENTS OF THE UNIVERSITY OF NEBRASKA`

### [64] `sub_awardee_country_code`

**Description**: Sub-awardee country code

**Sample Values**:
- `USA`

### [65] `sub_awardee_country_name`

**Description**: Sub-awardee country name

**Sample Values**:
- `United States`
- `UNITED STATES`

### [66] `sub_awardee_state_code`

**Description**: Sub-awardee state code

**Sample Values**:
- `NJ`
- `AL`
- `NY`

### [67] `sub_awardee_state_name`

**Description**: Sub-awardee state name

**Sample Values**:
- `NEW JERSEY`
- `ALABAMA`
- `NEW YORK`

### [68] `sub_awardee_zip_code`

**Description**: Sub-awardee ZIP code

**Sample Values**:
- `070366342`
- `354870001`
- `14623-2748`

### [69] `sub_awardee_congressional_code`

**Description**: Sub-awardee congressional district

**Sample Values**:
- `10`
- `07`
- `25`

### [70] `sub_awardee_county_code`

**Description**: Sub-awardee county code

*No non-null values in sample*

### [71] `sub_awardee_city_name`

**Description**: Sub-awardee city

**Sample Values**:
- `LINDEN`
- `TUSCALOOSA`
- `ROCHESTER`

### [72] `sub_awardee_address_line1`

**Description**: Sub-awardee address

**Sample Values**:
- `1611 W ELIZABETH AVE`
- `200 HACKBERRY LANE`
- `2921 BRIGHTON HENRIETTA TOWN LINE RD`

### [73] `sub_awardee_business_categories`

**Description**: Sub-awardee business types

**Sample Values**:
- `SELF-CERTIFIED SMALL DISADVANTAGED BUSINESS,FOR-PROFIT ORGANIZATION,MANUFACTURER...`
- `FOR PROFIT ORGANIZATION,BUSINESS OR ORGANIZATION,MANUFACTURER OF GOODS`
- `NONPROFIT ORGANIZATION`

### [74] `sub_pop_country_code`

**Description**: Sub-award place of performance country code

**Sample Values**:
- `USA`

### [75] `sub_pop_country_name`

**Description**: Sub-award place of performance country

**Sample Values**:
- `United States`
- `UNITED STATES`

### [76] `sub_pop_state_code`

**Description**: Sub-award place of performance state code

**Sample Values**:
- `NJ`
- `AL`
- `NY`

### [77] `sub_pop_state_name`

**Description**: Sub-award place of performance state

**Sample Values**:
- `NEW JERSEY`
- `ALABAMA`
- `NEW YORK`

### [78] `sub_pop_zip_code`

**Description**: Sub-award place of performance ZIP

**Sample Values**:
- `070366342`
- `354870104.0`
- `112202508.0`

### [79] `sub_pop_congressional_code`

**Description**: Sub-award place of performance congressional district

**Sample Values**:
- `10`
- `07`
- `12`

### [80] `sub_pop_city_name`

**Description**: Sub-award place of performance city

**Sample Values**:
- `LINDEN`
- `TUSCALOOSA`
- `BROOKLYN`

### [81] `sub_pop_address_line1`

**Description**: Sub-award place of performance address

*No non-null values in sample*

---

## System

**Total Fields**: 2

### [94] `internal_id`

**Description**: Internal system identifier (UUID)

**Sample Values**:
- `168CB38E-FCB9-11EF-8E2A-E7034F2D18CD`
- `C354D0B6-FCCC-11EF-AB59-07ECA35F602B`
- `168CBC30-FCB9-11EF-8E2A-E7034F2D18CD`

### [201] `generated_pragmatic_obligation`

**Description**: Generated pragmatic obligation ID

**Sample Values**:
- `d2126cd6-57c0-413f-1983-5b4216598036-C`
- `369ac1e4-8d93-3063-b933-3586dffba549-C`
- `b09dcd04-a8c9-ee78-bf74-30e428504408-C`

---

## Timestamp

**Total Fields**: 2

### [0] `create_date`

**Description**: Database record creation timestamp

**Sample Values**:
- `2025-04-07 22:55:40.497628+00`
- `2025-04-07 23:20:38.172356+00`
- `2025-04-24 09:01:40.986752+00`

### [1] `update_date`

**Description**: Database record last modified timestamp

**Sample Values**:
- `2025-04-07 22:55:40.497628+00`
- `2025-04-07 23:20:38.172356+00`
- `2025-04-24 09:01:40.986752+00`

---

## Transaction

**Total Fields**: 29

### [2] `transaction_id`

**Description**: Internal database transaction ID

**Sample Values**:
- `2125944`
- `4874063`
- `2124992`

### [3] `generated_unique_award_id`

**Description**: USAspending generated unique award identifier

**Sample Values**:
- `CONT_AWD_HC108422F0088_9700_HC102818D0045_9700`
- `ASST_NON_1457855_049`
- `CONT_AWD_47QFLA24F0097_4732_47QFLA20D0014_4732`

### [4] `piid`

**Description**: Procurement Instrument Identifier (contract number)

**Sample Values**:
- `HC108422F0088`
- `1457855`
- `47QFLA24F0097`

### [5] `parent_award_id`

**Description**: Parent IDV/award identifier

**Sample Values**:
- `HC102818D0045`
- `47QFLA20D0014`
- `SPRPA114D002U`

### [7] `action_date`

**Description**: Date of the transaction action

**Sample Values**:
- `2022-03-10`
- `2015-06-30`
- `2024-06-27`

### [8] `fiscal_year`

**Description**: Fiscal year of transaction

**Sample Values**:
- `FY2022`
- `FY2015`
- `FY2024`

### [51] `prime_award_transaction_type`

**Description**: Sub-award or sub-grant indicator

**Sample Values**:
- `sub-contract`
- `sub-grant`

### [84] `award_latest_action_date`

**Description**: Latest action date for award

*No non-null values in sample*

### [85] `award_latest_action_date_fiscal_year`

**Description**: Latest action fiscal year

*No non-null values in sample*

### [86] `award_base_action_date`

**Description**: Base action date

*No non-null values in sample*

### [87] `award_base_action_date_fiscal_year`

**Description**: Base action fiscal year

*No non-null values in sample*

### [88] `period_of_performance_start_date`

**Description**: Performance start date

*No non-null values in sample*

### [89] `period_of_performance_current_end_date`

**Description**: Performance current end date

*No non-null values in sample*

### [90] `period_of_performance_potential_end_date`

**Description**: Performance potential end date

*No non-null values in sample*

### [91] `ordering_period_end_date`

**Description**: IDV ordering period end

*No non-null values in sample*

### [92] `solicitation_date`

**Description**: Solicitation date

*No non-null values in sample*

### [95] `date_signed`

**Description**: Date contract was signed

**Sample Values**:
- `2022-04-28 00:00:00+00`
- `2017-10-09 00:00:00+00`
- `2022-06-29 00:00:00+00`

### [120] `fain`

**Description**: Federal Award Identification Number (grants)

**Sample Values**:
- `20360727`
- `23069193`
- `20360730`

### [121] `uri`

**Description**: URI for other awards

*No non-null values in sample*

### [126] `referenced_idv_agency_iden`

**Description**: Referenced IDV agency identifier

*No non-null values in sample*

### [127] `referenced_idv_agency_desc`

**Description**: Referenced IDV agency description

*No non-null values in sample*

### [134] `award_type_code`

**Description**: Award type code

*No non-null values in sample*

### [135] `award_type`

**Description**: Award type description

*No non-null values in sample*

### [136] `record_type`

**Description**: Record type (procurement/assistance)

**Sample Values**:
- `procurement`
- `grant`

### [137] `type_of_transaction_code`

**Description**: Transaction type code

**Sample Values**:
- `C`
- `04`
- `05`

### [138] `piid_2`

**Description**: PIID (duplicate)

**Sample Values**:
- `HC108422F0088`
- `47QFLA24F0097`
- `SPRPA122F0027`

### [139] `fain_2`

**Description**: FAIN (duplicate)

**Sample Values**:
- `1457855`
- `18ACHNY001`
- `UH3HL165740`

### [152] `fiscal_year_2`

**Description**: Fiscal year (duplicate)

**Sample Values**:
- `2022`
- `2017`
- `2025`

### [162] `action_type_code`

**Description**: Action type code

**Sample Values**:
- `A`
- `C`

---

## China Entity Detection Strategy

Based on the complete schema, here are the key fields for detecting China-related transactions:

### Primary Detection Fields (Direct Entity Identification)

1. **[23] `recipient_name`** - Prime contractor/recipient name
2. **[27] `recipient_parent_name`** - Ultimate parent organization
3. **[29] `recipient_location_country_name`** - Recipient country
4. **[39] `pop_country_name`** - Where work is performed
5. **[59] `sub_awardee_name`** - Sub-contractor name
6. **[63] `sub_awardee_parent_name`** - Sub-contractor parent
7. **[65] `sub_awardee_country_name`** - Sub-contractor country

### Secondary Detection Fields (Context and Classification)

8. **[46] `award_description`** - Detailed description of award
9. **[47-48] `naics_code/description`** - Industry classification
10. **[163-164] `product_or_service_code`** - PSC classification
11. **[82] `subaward_description`** - Sub-award details
12. **[180-182] Text search vectors** - Full-text search capability

### Financial and Risk Assessment Fields

13. **[6] `federal_action_obligation`** - Transaction amount
14. **[140] `total_dollars_obligated`** - Total obligated
15. **[10/16] Agency names** - Awarding agencies (DOD, DOE, etc.)
16. **[7] `action_date`** - Transaction date

### Identification Fields (Cross-Reference)

17. **[22] `recipient_uei`** - Unique Entity Identifier
18. **[21] `recipient_duns`** - DUNS number
19. **[4] `piid`** - Procurement instrument ID
20. **[120] `fain`** - Federal award ID (grants)

---

## Processing Recommendations

### Multi-Field Detection Strategy

1. **Country Check** (Columns 29, 39, 65, 75):
   - Look for 'China', 'Hong Kong', 'PRC', 'People's Republic of China'
   - Check both recipient location AND place of performance
   - Check both prime AND sub-awardee countries

2. **Entity Name Check** (Columns 23, 27, 59, 63):
   - Scan for known Chinese companies (Huawei, ZTE, etc.)
   - Look for Chinese name patterns
   - Check parent companies (many use US subsidiaries)

3. **Description Analysis** (Columns 46, 82):
   - Search for China-related keywords
   - Identify technology sectors of interest
   - Cross-reference with sensitive NAICS/PSC codes

4. **Full-Text Search** (Columns 180-182):
   - Use PostgreSQL text search vectors for efficiency
   - Can search across multiple text fields simultaneously

### Performance Optimization

- **Batch Processing**: Process 100k-500k records at a time
- **Index Fields**: Country codes, recipient names, NAICS codes
- **NULL Handling**: Many fields have high NULL rates (\N)
- **Size**: 215 GB total, ~50M+ transactions estimated

---

*Generated by USAspending Schema Mapper - 2025-10-11*

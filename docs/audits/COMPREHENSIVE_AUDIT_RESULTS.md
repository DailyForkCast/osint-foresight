# Comprehensive Audit Results
**Date:** 2025-11-03
**Total Tests:** 117
**Pass Rate:** 93.2%

## Summary by Category

- **Abbreviation Attack**: 8/8 (100.0%)
- **BIS Entity List**: 19/20 (95.0%)
- **Context: Product vs Entity**: 2/7 (28.6%)
- **False Positives**: 18/18 (100.0%)
- **Geographic Ambiguity**: 5/7 (71.4%)
- **Non-Chinese Entities**: 17/17 (100.0%)
- **Taiwan Exclusion**: 18/18 (100.0%)
- **Typographic Evasion**: 13/13 (100.0%)
- **Unicode Attack**: 9/9 (100.0%)

## All Test Results

### [PASS] Cyrillic 'а' (U+0430) instead of Latin 'a'
- **Category:** Unicode Attack
- **Severity:** LOW
- **Expected:** DETECTED
- **Actual:** DETECTED
- **Evidence:** Input bytes: Hu\u0430wei

### [PASS] Cyrillic 'а' and 'е' instead of Latin
- **Category:** Unicode Attack
- **Severity:** LOW
- **Expected:** DETECTED
- **Actual:** DETECTED
- **Evidence:** Input bytes: Hu\u0430w\u0435i

### [PASS] Cyrillic 'Н' (U+041D) instead of Latin 'H'
- **Category:** Unicode Attack
- **Severity:** LOW
- **Expected:** DETECTED
- **Actual:** DETECTED
- **Evidence:** Input bytes: \u041duawei

### [PASS] Cyrillic 'Т' (U+0422) instead of Latin 'T'
- **Category:** Unicode Attack
- **Severity:** LOW
- **Expected:** DETECTED
- **Actual:** DETECTED
- **Evidence:** Input bytes: Z\u0422E

### [PASS] Zero-width space (U+200B)
- **Category:** Unicode Attack
- **Severity:** LOW
- **Expected:** DETECTED
- **Actual:** DETECTED
- **Evidence:** Input bytes: Hua\u200bwei

### [PASS] Zero-width non-joiner (U+200C)
- **Category:** Unicode Attack
- **Severity:** LOW
- **Expected:** DETECTED
- **Actual:** DETECTED
- **Evidence:** Input bytes: Hua\u200cwei

### [PASS] Zero-width no-break space (U+FEFF)
- **Category:** Unicode Attack
- **Severity:** LOW
- **Expected:** DETECTED
- **Actual:** DETECTED
- **Evidence:** Input bytes: Hua\ufeffwei

### [PASS] Greek capital Eta (U+0397) looks like H
- **Category:** Unicode Attack
- **Severity:** LOW
- **Expected:** DETECTED
- **Actual:** DETECTED
- **Evidence:** Input bytes: \u0397uawei

### [PASS] Cyrillic Small Ie (U+0435) looks like e
- **Category:** Unicode Attack
- **Severity:** LOW
- **Expected:** DETECTED
- **Actual:** DETECTED
- **Evidence:** Input bytes: Huaw\u0435i

### [PASS] Hyphenated name
- **Category:** Typographic Evasion
- **Severity:** LOW
- **Expected:** DETECTED
- **Actual:** DETECTED
- **Evidence:** Input: 'Hua-wei'

### [PASS] Hyphenated with suffix
- **Category:** Typographic Evasion
- **Severity:** LOW
- **Expected:** DETECTED
- **Actual:** DETECTED
- **Evidence:** Input: 'Hua-wei Technologies'

### [PASS] Hyphenated location
- **Category:** Typographic Evasion
- **Severity:** LOW
- **Expected:** DETECTED
- **Actual:** DETECTED
- **Evidence:** Input: 'Hong-Kong'

### [PASS] Hyphenated company
- **Category:** Typographic Evasion
- **Severity:** LOW
- **Expected:** DETECTED
- **Actual:** DETECTED
- **Evidence:** Input: 'ZTE-Corporation'

### [PASS] Dot separated
- **Category:** Typographic Evasion
- **Severity:** LOW
- **Expected:** DETECTED
- **Actual:** DETECTED
- **Evidence:** Input: 'Hua.wei'

### [PASS] Comma separated
- **Category:** Typographic Evasion
- **Severity:** LOW
- **Expected:** DETECTED
- **Actual:** DETECTED
- **Evidence:** Input: 'Hua,wei'

### [PASS] Underscore separated
- **Category:** Typographic Evasion
- **Severity:** LOW
- **Expected:** DETECTED
- **Actual:** DETECTED
- **Evidence:** Input: 'Hua_wei'

### [PASS] Slash separated
- **Category:** Typographic Evasion
- **Severity:** LOW
- **Expected:** DETECTED
- **Actual:** DETECTED
- **Evidence:** Input: 'Hua/wei'

### [PASS] Double space
- **Category:** Typographic Evasion
- **Severity:** LOW
- **Expected:** DETECTED
- **Actual:** DETECTED
- **Evidence:** Input: 'Hua  wei'

### [PASS] Triple space
- **Category:** Typographic Evasion
- **Severity:** LOW
- **Expected:** DETECTED
- **Actual:** DETECTED
- **Evidence:** Input: 'Hua   wei'

### [PASS] Mixed case
- **Category:** Typographic Evasion
- **Severity:** LOW
- **Expected:** DETECTED
- **Actual:** DETECTED
- **Evidence:** Input: 'hUaWeI'

### [PASS] All caps
- **Category:** Typographic Evasion
- **Severity:** LOW
- **Expected:** DETECTED
- **Actual:** DETECTED
- **Evidence:** Input: 'HUAWEI'

### [PASS] All lowercase
- **Category:** Typographic Evasion
- **Severity:** LOW
- **Expected:** DETECTED
- **Actual:** DETECTED
- **Evidence:** Input: 'huawei'

### [PASS] HW = Huawei
- **Category:** Abbreviation Attack
- **Severity:** LOW
- **Expected:** NOT DETECTED
- **Actual:** NOT DETECTED
- **Evidence:** Input: 'HW Technologies'

### [PASS] ZT = ZTE
- **Category:** Abbreviation Attack
- **Severity:** LOW
- **Expected:** NOT DETECTED
- **Actual:** NOT DETECTED
- **Evidence:** Input: 'ZT Corporation'

### [PASS] Full ZTE
- **Category:** Abbreviation Attack
- **Severity:** LOW
- **Expected:** DETECTED
- **Actual:** DETECTED
- **Evidence:** Input: 'ZTE Corp'

### [PASS] Spaced ZTE
- **Category:** Abbreviation Attack
- **Severity:** LOW
- **Expected:** DETECTED
- **Actual:** DETECTED
- **Evidence:** Input: 'Z T E'

### [PASS] Partial Huawei
- **Category:** Abbreviation Attack
- **Severity:** LOW
- **Expected:** NOT DETECTED
- **Actual:** NOT DETECTED
- **Evidence:** Input: 'Hua Corporation'

### [PASS] Partial Huawei
- **Category:** Abbreviation Attack
- **Severity:** LOW
- **Expected:** NOT DETECTED
- **Actual:** NOT DETECTED
- **Evidence:** Input: 'Wei Technologies'

### [PASS] COMAC aircraft manufacturer
- **Category:** Abbreviation Attack
- **Severity:** LOW
- **Expected:** DETECTED
- **Actual:** DETECTED
- **Evidence:** Input: 'COMAC Aviation'

### [PASS] AVIC aerospace
- **Category:** Abbreviation Attack
- **Severity:** LOW
- **Expected:** DETECTED
- **Actual:** DETECTED
- **Evidence:** Input: 'AVIC Corporation'

### [FAIL] Product mention
- **Category:** Context: Product vs Entity
- **Severity:** MEDIUM
- **Expected:** NOT DETECTED
- **Actual:** DETECTED
- **Evidence:** Input: 'Compatible with Huawei devices'

### [PASS] Entity name
- **Category:** Context: Product vs Entity
- **Severity:** LOW
- **Expected:** DETECTED
- **Actual:** DETECTED
- **Evidence:** Input: 'Huawei Technologies Co., Ltd.'

### [PASS] Sourcing
- **Category:** Context: Product vs Entity
- **Severity:** LOW
- **Expected:** DETECTED
- **Actual:** DETECTED
- **Evidence:** Input: 'Made in China'

### [FAIL] Customer relationship
- **Category:** Context: Product vs Entity
- **Severity:** MEDIUM
- **Expected:** NOT DETECTED
- **Actual:** DETECTED
- **Evidence:** Input: 'China Mobile subscriber'

### [FAIL] Past employment
- **Category:** Context: Product vs Entity
- **Severity:** MEDIUM
- **Expected:** NOT DETECTED
- **Actual:** DETECTED
- **Evidence:** Input: 'Former Huawei employee, now at Google'

### [FAIL] Negative mention
- **Category:** Context: Product vs Entity
- **Severity:** MEDIUM
- **Expected:** NOT DETECTED
- **Actual:** DETECTED
- **Evidence:** Input: 'Not affiliated with Huawei'

### [FAIL] Critical mention
- **Category:** Context: Product vs Entity
- **Severity:** MEDIUM
- **Expected:** NOT DETECTED
- **Actual:** DETECTED
- **Evidence:** Input: 'Anti-Huawei policy'

### [PASS] US town
- **Category:** Geographic Ambiguity
- **Severity:** LOW
- **Expected:** NOT DETECTED (US location)
- **Actual:** NOT DETECTED
- **Evidence:** Input: 'China, Michigan' | Name: False, Country: False

### [PASS] US location
- **Category:** Geographic Ambiguity
- **Severity:** LOW
- **Expected:** NOT DETECTED (US location)
- **Actual:** NOT DETECTED
- **Evidence:** Input: 'China Beach, California' | Name: False, Country: False

### [PASS] US location
- **Category:** Geographic Ambiguity
- **Severity:** LOW
- **Expected:** NOT DETECTED (US location)
- **Actual:** NOT DETECTED
- **Evidence:** Input: 'China Cove, California' | Name: False, Country: False

### [PASS] US city
- **Category:** Geographic Ambiguity
- **Severity:** LOW
- **Expected:** NOT DETECTED (US location)
- **Actual:** NOT DETECTED
- **Evidence:** Input: 'Chino, California' | Name: False, Country: False

### [PASS] US city
- **Category:** Geographic Ambiguity
- **Severity:** LOW
- **Expected:** NOT DETECTED (US location)
- **Actual:** NOT DETECTED
- **Evidence:** Input: 'Chino Hills, California' | Name: False, Country: False

### [FAIL] Street name
- **Category:** Geographic Ambiguity
- **Severity:** HIGH
- **Expected:** NOT DETECTED (US location)
- **Actual:** DETECTED
- **Evidence:** Input: 'Shanghai Tunnel, Portland Oregon' | Name: True, Country: True

### [FAIL] Street in HK
- **Category:** Geographic Ambiguity
- **Severity:** HIGH
- **Expected:** NOT DETECTED (US location)
- **Actual:** DETECTED
- **Evidence:** Input: 'Beijing Road, Hong Kong' | Name: True, Country: True

### [PASS] HUAWEI TECHNOLOGIES CO., LTD.
- **Category:** BIS Entity List
- **Severity:** LOW
- **Expected:** DETECTED (on BIS Entity List)
- **Actual:** DETECTED
- **Evidence:** Source: BIS Entity List

### [PASS] ZTE CORPORATION
- **Category:** BIS Entity List
- **Severity:** LOW
- **Expected:** DETECTED (on BIS Entity List)
- **Actual:** DETECTED
- **Evidence:** Source: BIS Entity List

### [PASS] HIKVISION
- **Category:** BIS Entity List
- **Severity:** LOW
- **Expected:** DETECTED (on BIS Entity List)
- **Actual:** DETECTED
- **Evidence:** Source: BIS Entity List

### [PASS] DAHUA TECHNOLOGY CO., LTD.
- **Category:** BIS Entity List
- **Severity:** LOW
- **Expected:** DETECTED (on BIS Entity List)
- **Actual:** DETECTED
- **Evidence:** Source: BIS Entity List

### [PASS] HYTERA COMMUNICATIONS CORPORATION LIMITED
- **Category:** BIS Entity List
- **Severity:** LOW
- **Expected:** DETECTED (on BIS Entity List)
- **Actual:** DETECTED
- **Evidence:** Source: BIS Entity List

### [PASS] HANGZHOU HIKVISION DIGITAL TECHNOLOGY CO., LTD.
- **Category:** BIS Entity List
- **Severity:** LOW
- **Expected:** DETECTED (on BIS Entity List)
- **Actual:** DETECTED
- **Evidence:** Source: BIS Entity List

### [PASS] SEMICONDUCTOR MANUFACTURING INTERNATIONAL CORPORATION
- **Category:** BIS Entity List
- **Severity:** LOW
- **Expected:** DETECTED (on BIS Entity List)
- **Actual:** DETECTED
- **Evidence:** Source: BIS Entity List

### [PASS] CHINA ELECTRONICS TECHNOLOGY GROUP CORPORATION
- **Category:** BIS Entity List
- **Severity:** LOW
- **Expected:** DETECTED (on BIS Entity List)
- **Actual:** DETECTED
- **Evidence:** Source: BIS Entity List

### [PASS] ACADEMY OF MILITARY MEDICAL SCIENCES
- **Category:** BIS Entity List
- **Severity:** LOW
- **Expected:** DETECTED (on BIS Entity List)
- **Actual:** DETECTED
- **Evidence:** Source: BIS Entity List

### [PASS] BEIJING COMPUTATIONAL SCIENCE RESEARCH CENTER
- **Category:** BIS Entity List
- **Severity:** LOW
- **Expected:** DETECTED (on BIS Entity List)
- **Actual:** DETECTED
- **Evidence:** Source: BIS Entity List

### [FAIL] BEIHANG UNIVERSITY
- **Category:** BIS Entity List
- **Severity:** CRITICAL
- **Expected:** DETECTED (on BIS Entity List)
- **Actual:** NOT DETECTED
- **Evidence:** Source: BIS Entity List

### [PASS] CHINA ACADEMY OF AEROSPACE AERODYNAMICS
- **Category:** BIS Entity List
- **Severity:** LOW
- **Expected:** DETECTED (on BIS Entity List)
- **Actual:** DETECTED
- **Evidence:** Source: BIS Entity List

### [PASS] HARBIN INSTITUTE OF TECHNOLOGY
- **Category:** BIS Entity List
- **Severity:** LOW
- **Expected:** DETECTED (on BIS Entity List)
- **Actual:** DETECTED
- **Evidence:** Source: BIS Entity List

### [PASS] HARBIN ENGINEERING UNIVERSITY
- **Category:** BIS Entity List
- **Severity:** LOW
- **Expected:** DETECTED (on BIS Entity List)
- **Actual:** DETECTED
- **Evidence:** Source: BIS Entity List

### [PASS] NORTHWESTERN POLYTECHNICAL UNIVERSITY
- **Category:** BIS Entity List
- **Severity:** LOW
- **Expected:** DETECTED (on BIS Entity List)
- **Actual:** DETECTED
- **Evidence:** Source: BIS Entity List

### [PASS] NANJING UNIVERSITY OF AERONAUTICS AND ASTRONAUTICS
- **Category:** BIS Entity List
- **Severity:** LOW
- **Expected:** DETECTED (on BIS Entity List)
- **Actual:** DETECTED
- **Evidence:** Source: BIS Entity List

### [PASS] NANJING UNIVERSITY OF SCIENCE AND TECHNOLOGY
- **Category:** BIS Entity List
- **Severity:** LOW
- **Expected:** DETECTED (on BIS Entity List)
- **Actual:** DETECTED
- **Evidence:** Source: BIS Entity List

### [PASS] NATIONAL UNIVERSITY OF DEFENSE TECHNOLOGY
- **Category:** BIS Entity List
- **Severity:** LOW
- **Expected:** DETECTED (on BIS Entity List)
- **Actual:** DETECTED
- **Evidence:** Source: BIS Entity List

### [PASS] SICHUAN UNIVERSITY
- **Category:** BIS Entity List
- **Severity:** LOW
- **Expected:** DETECTED (on BIS Entity List)
- **Actual:** DETECTED
- **Evidence:** Source: BIS Entity List

### [PASS] TIANJIN UNIVERSITY
- **Category:** BIS Entity List
- **Severity:** LOW
- **Expected:** DETECTED (on BIS Entity List)
- **Actual:** DETECTED
- **Evidence:** Source: BIS Entity List

### [PASS] TSMC (Taiwan Semiconductor Manufacturing Company)
- **Category:** Taiwan Exclusion
- **Severity:** LOW
- **Expected:** NOT DETECTED (Taiwan ROC ≠ China PRC)
- **Actual:** NOT DETECTED
- **Evidence:** Taiwan companies must not be flagged as Chinese

### [PASS] Foxconn (Hon Hai Precision Industry)
- **Category:** Taiwan Exclusion
- **Severity:** LOW
- **Expected:** NOT DETECTED (Taiwan ROC ≠ China PRC)
- **Actual:** NOT DETECTED
- **Evidence:** Taiwan companies must not be flagged as Chinese

### [PASS] MediaTek (Semiconductor designer)
- **Category:** Taiwan Exclusion
- **Severity:** LOW
- **Expected:** NOT DETECTED (Taiwan ROC ≠ China PRC)
- **Actual:** NOT DETECTED
- **Evidence:** Taiwan companies must not be flagged as Chinese

### [PASS] Taiwan Mobile (Telecom company)
- **Category:** Taiwan Exclusion
- **Severity:** LOW
- **Expected:** NOT DETECTED (Taiwan ROC ≠ China PRC)
- **Actual:** NOT DETECTED
- **Evidence:** Taiwan companies must not be flagged as Chinese

### [PASS] Taiwan Semiconductor (Generic reference)
- **Category:** Taiwan Exclusion
- **Severity:** LOW
- **Expected:** NOT DETECTED (Taiwan ROC ≠ China PRC)
- **Actual:** NOT DETECTED
- **Evidence:** Taiwan companies must not be flagged as Chinese

### [PASS] Formosa Plastics (Petrochemical company)
- **Category:** Taiwan Exclusion
- **Severity:** LOW
- **Expected:** NOT DETECTED (Taiwan ROC ≠ China PRC)
- **Actual:** NOT DETECTED
- **Evidence:** Taiwan companies must not be flagged as Chinese

### [PASS] Acer (Computer manufacturer)
- **Category:** Taiwan Exclusion
- **Severity:** LOW
- **Expected:** NOT DETECTED (Taiwan ROC ≠ China PRC)
- **Actual:** NOT DETECTED
- **Evidence:** Taiwan companies must not be flagged as Chinese

### [PASS] ASUS (Computer hardware)
- **Category:** Taiwan Exclusion
- **Severity:** LOW
- **Expected:** NOT DETECTED (Taiwan ROC ≠ China PRC)
- **Actual:** NOT DETECTED
- **Evidence:** Taiwan companies must not be flagged as Chinese

### [PASS] HTC (Smartphone manufacturer)
- **Category:** Taiwan Exclusion
- **Severity:** LOW
- **Expected:** NOT DETECTED (Taiwan ROC ≠ China PRC)
- **Actual:** NOT DETECTED
- **Evidence:** Taiwan companies must not be flagged as Chinese

### [PASS] Giant Manufacturing (Bicycle manufacturer)
- **Category:** Taiwan Exclusion
- **Severity:** LOW
- **Expected:** NOT DETECTED (Taiwan ROC ≠ China PRC)
- **Actual:** NOT DETECTED
- **Evidence:** Taiwan companies must not be flagged as Chinese

### [PASS] Taipei (Taiwan location)
- **Category:** Taiwan Exclusion
- **Severity:** LOW
- **Expected:** NOT DETECTED (Taiwan location)
- **Actual:** NOT DETECTED
- **Evidence:** Taiwan locations must not be detected as China

### [PASS] Kaohsiung (Taiwan location)
- **Category:** Taiwan Exclusion
- **Severity:** LOW
- **Expected:** NOT DETECTED (Taiwan location)
- **Actual:** NOT DETECTED
- **Evidence:** Taiwan locations must not be detected as China

### [PASS] Taichung (Taiwan location)
- **Category:** Taiwan Exclusion
- **Severity:** LOW
- **Expected:** NOT DETECTED (Taiwan location)
- **Actual:** NOT DETECTED
- **Evidence:** Taiwan locations must not be detected as China

### [PASS] Tainan (Taiwan location)
- **Category:** Taiwan Exclusion
- **Severity:** LOW
- **Expected:** NOT DETECTED (Taiwan location)
- **Actual:** NOT DETECTED
- **Evidence:** Taiwan locations must not be detected as China

### [PASS] Taiwan (Taiwan location)
- **Category:** Taiwan Exclusion
- **Severity:** LOW
- **Expected:** NOT DETECTED (Taiwan location)
- **Actual:** NOT DETECTED
- **Evidence:** Taiwan locations must not be detected as China

### [PASS] Republic of China (Taiwan location)
- **Category:** Taiwan Exclusion
- **Severity:** LOW
- **Expected:** NOT DETECTED (Taiwan location)
- **Actual:** NOT DETECTED
- **Evidence:** Taiwan locations must not be detected as China

### [PASS] ROC (Taiwan location)
- **Category:** Taiwan Exclusion
- **Severity:** LOW
- **Expected:** NOT DETECTED (Taiwan location)
- **Actual:** NOT DETECTED
- **Evidence:** Taiwan locations must not be detected as China

### [PASS] Formosa (Taiwan location)
- **Category:** Taiwan Exclusion
- **Severity:** LOW
- **Expected:** NOT DETECTED (Taiwan location)
- **Actual:** NOT DETECTED
- **Evidence:** Taiwan locations must not be detected as China

### [PASS] Apple Inc. (US tech company)
- **Category:** Non-Chinese Entities
- **Severity:** LOW
- **Expected:** NOT DETECTED
- **Actual:** NOT DETECTED
- **Evidence:** US tech company

### [PASS] Microsoft Corporation (US tech company)
- **Category:** Non-Chinese Entities
- **Severity:** LOW
- **Expected:** NOT DETECTED
- **Actual:** NOT DETECTED
- **Evidence:** US tech company

### [PASS] Google LLC (US tech company)
- **Category:** Non-Chinese Entities
- **Severity:** LOW
- **Expected:** NOT DETECTED
- **Actual:** NOT DETECTED
- **Evidence:** US tech company

### [PASS] Amazon.com Inc. (US tech company)
- **Category:** Non-Chinese Entities
- **Severity:** LOW
- **Expected:** NOT DETECTED
- **Actual:** NOT DETECTED
- **Evidence:** US tech company

### [PASS] Siemens AG (German conglomerate)
- **Category:** Non-Chinese Entities
- **Severity:** LOW
- **Expected:** NOT DETECTED
- **Actual:** NOT DETECTED
- **Evidence:** German conglomerate

### [PASS] Nokia Corporation (Finnish telecom)
- **Category:** Non-Chinese Entities
- **Severity:** LOW
- **Expected:** NOT DETECTED
- **Actual:** NOT DETECTED
- **Evidence:** Finnish telecom

### [PASS] Ericsson (Swedish telecom)
- **Category:** Non-Chinese Entities
- **Severity:** LOW
- **Expected:** NOT DETECTED
- **Actual:** NOT DETECTED
- **Evidence:** Swedish telecom

### [PASS] SAP SE (German software)
- **Category:** Non-Chinese Entities
- **Severity:** LOW
- **Expected:** NOT DETECTED
- **Actual:** NOT DETECTED
- **Evidence:** German software

### [PASS] Sony Corporation (Japanese electronics)
- **Category:** Non-Chinese Entities
- **Severity:** LOW
- **Expected:** NOT DETECTED
- **Actual:** NOT DETECTED
- **Evidence:** Japanese electronics

### [PASS] Toyota Motor Corporation (Japanese automotive)
- **Category:** Non-Chinese Entities
- **Severity:** LOW
- **Expected:** NOT DETECTED
- **Actual:** NOT DETECTED
- **Evidence:** Japanese automotive

### [PASS] NTT DoCoMo (Japanese telecom)
- **Category:** Non-Chinese Entities
- **Severity:** LOW
- **Expected:** NOT DETECTED
- **Actual:** NOT DETECTED
- **Evidence:** Japanese telecom

### [PASS] SoftBank Group (Japanese conglomerate)
- **Category:** Non-Chinese Entities
- **Severity:** LOW
- **Expected:** NOT DETECTED
- **Actual:** NOT DETECTED
- **Evidence:** Japanese conglomerate

### [PASS] Samsung Electronics (Korean electronics)
- **Category:** Non-Chinese Entities
- **Severity:** LOW
- **Expected:** NOT DETECTED
- **Actual:** NOT DETECTED
- **Evidence:** Korean electronics

### [PASS] LG Corporation (Korean conglomerate)
- **Category:** Non-Chinese Entities
- **Severity:** LOW
- **Expected:** NOT DETECTED
- **Actual:** NOT DETECTED
- **Evidence:** Korean conglomerate

### [PASS] SK Hynix (Korean semiconductor)
- **Category:** Non-Chinese Entities
- **Severity:** LOW
- **Expected:** NOT DETECTED
- **Actual:** NOT DETECTED
- **Evidence:** Korean semiconductor

### [PASS] Taiwan Semiconductor Manufacturing Company (TSMC)
- **Category:** Non-Chinese Entities
- **Severity:** LOW
- **Expected:** NOT DETECTED
- **Actual:** NOT DETECTED
- **Evidence:** TSMC

### [PASS] Hon Hai Precision Industry (Foxconn)
- **Category:** Non-Chinese Entities
- **Severity:** LOW
- **Expected:** NOT DETECTED
- **Actual:** NOT DETECTED
- **Evidence:** Foxconn

### [PASS] China King Restaurant (US restaurant chain)
- **Category:** False Positives
- **Severity:** LOW
- **Expected:** NOT DETECTED (false positive)
- **Actual:** NOT DETECTED
- **Evidence:** Name: False, Country: False

### [PASS] China Wok (US restaurant)
- **Category:** False Positives
- **Severity:** LOW
- **Expected:** NOT DETECTED (false positive)
- **Actual:** NOT DETECTED
- **Evidence:** Name: False, Country: False

### [PASS] Great Wall Restaurant (US restaurant)
- **Category:** False Positives
- **Severity:** LOW
- **Expected:** NOT DETECTED (false positive)
- **Actual:** NOT DETECTED
- **Evidence:** Name: False, Country: False

### [PASS] Panda Express (US restaurant chain)
- **Category:** False Positives
- **Severity:** LOW
- **Expected:** NOT DETECTED (false positive)
- **Actual:** NOT DETECTED
- **Evidence:** Name: False, Country: False

### [PASS] P.F. Chang's (US restaurant chain)
- **Category:** False Positives
- **Severity:** LOW
- **Expected:** NOT DETECTED (false positive)
- **Actual:** NOT DETECTED
- **Evidence:** Name: False, Country: False

### [PASS] Chinese Historical Society of America (US cultural org)
- **Category:** False Positives
- **Severity:** LOW
- **Expected:** NOT DETECTED (false positive)
- **Actual:** NOT DETECTED
- **Evidence:** Name: False, Country: False

### [PASS] Chinese American Museum (US museum)
- **Category:** False Positives
- **Severity:** LOW
- **Expected:** NOT DETECTED (false positive)
- **Actual:** NOT DETECTED
- **Evidence:** Name: False, Country: False

### [PASS] Museum of Chinese in America (US museum)
- **Category:** False Positives
- **Severity:** LOW
- **Expected:** NOT DETECTED (false positive)
- **Actual:** NOT DETECTED
- **Evidence:** Name: False, Country: False

### [PASS] Chinati Foundation (US art museum in Texas)
- **Category:** False Positives
- **Severity:** LOW
- **Expected:** NOT DETECTED (false positive)
- **Actual:** NOT DETECTED
- **Evidence:** Name: False, Country: False

### [PASS] China Beach (California location)
- **Category:** False Positives
- **Severity:** LOW
- **Expected:** NOT DETECTED (false positive)
- **Actual:** NOT DETECTED
- **Evidence:** Name: False, Country: False

### [PASS] China Cove (California location)
- **Category:** False Positives
- **Severity:** LOW
- **Expected:** NOT DETECTED (false positive)
- **Actual:** NOT DETECTED
- **Evidence:** Name: False, Country: False

### [PASS] China, Michigan (US town)
- **Category:** False Positives
- **Severity:** LOW
- **Expected:** NOT DETECTED (false positive)
- **Actual:** NOT DETECTED
- **Evidence:** Name: False, Country: False

### [PASS] Homer Laughlin China Company (US porcelain manufacturer)
- **Category:** False Positives
- **Severity:** LOW
- **Expected:** NOT DETECTED (false positive)
- **Actual:** NOT DETECTED
- **Evidence:** Name: False, Country: False

### [PASS] Fine china dinnerware (Porcelain products)
- **Category:** False Positives
- **Severity:** LOW
- **Expected:** NOT DETECTED (false positive)
- **Actual:** NOT DETECTED
- **Evidence:** Name: False, Country: False

### [PASS] T K C Enterprises (Contains 'k c')
- **Category:** False Positives
- **Severity:** LOW
- **Expected:** NOT DETECTED (false positive)
- **Actual:** NOT DETECTED
- **Evidence:** Name: False, Country: False

### [PASS] Mavich LLC (Contains 'avic')
- **Category:** False Positives
- **Severity:** LOW
- **Expected:** NOT DETECTED (false positive)
- **Actual:** NOT DETECTED
- **Evidence:** Name: False, Country: False

### [PASS] Aztec Environmental (Contains 'zte')
- **Category:** False Positives
- **Severity:** LOW
- **Expected:** NOT DETECTED (false positive)
- **Actual:** NOT DETECTED
- **Evidence:** Name: False, Country: False

### [PASS] COMAC Pump & Well (Not COMAC aircraft)
- **Category:** False Positives
- **Severity:** LOW
- **Expected:** NOT DETECTED (false positive)
- **Actual:** NOT DETECTED
- **Evidence:** Name: False, Country: False


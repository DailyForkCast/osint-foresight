# Comprehensive Audit Plan - Chinese Entity Detection System
**Date:** 2025-11-03
**Objective:** Find EVERY problem in the detection system
**Approach:** Adversarial, systematic, evidence-based

---

## Audit Methodology

### Phase 1: Adversarial Testing (Evasion Techniques)
**Goal:** Try to break the system with obfuscation and edge cases

**Test Categories:**
1. **Unicode Attacks**
   - Cyrillic lookalikes (а, е, о vs a, e, o)
   - Homoglyphs (different Unicode characters that look identical)
   - Zero-width spaces and invisible characters
   - Right-to-left override attacks
   - Mixed scripts (Chinese + Latin characters)

2. **Typographic Evasion**
   - Hyphenation: "Hua-wei", "Hong-Kong"
   - Extra spaces: "H u a w e i"
   - Misspellings: "Hwawei", "Huawai"
   - Case variations: "hUaWeI"
   - Punctuation insertion: "Hua.wei", "Hua,wei"

3. **Abbreviation Attacks**
   - Two-letter: "HW", "ZT"
   - Three-letter: "ZTE" → "Z T E"
   - Acronyms: "COMAC" → "COM AC"
   - Partial names: "Hua Corp"

4. **Legal Entity Suffixes**
   - "Huawei Inc" vs "Huawei LLC" vs "Huawei GmbH"
   - "Huawei Technologies (USA) Inc."
   - "Huawei Device Co., Ltd."
   - "Beijing Corporation of America"

---

### Phase 2: Contextual Accuracy Testing
**Goal:** Ensure system distinguishes entity relationships from mentions

**Test Categories:**
1. **Product vs Entity**
   - "Compatible with Huawei devices" (product mention)
   - "Huawei Technologies Co., Ltd." (entity)
   - "Made in China" (sourcing)
   - "China Mobile subscriber" (customer of Chinese company)

2. **Person vs Entity**
   - "John Smith, former Huawei employee, now at Google"
   - "China policy expert"
   - "Chinese-American researcher"
   - "Born in Beijing, works in USA"

3. **Negative/Critical Mentions**
   - "Anti-China stance"
   - "Not affiliated with Chinese entities"
   - "Divested from Chinese ownership"
   - "CFIUS rejected due to Chinese ties"

4. **Geographic Ambiguity**
   - "China, Michigan" (US town)
   - "China Beach" (California location)
   - "Beijing Road, Hong Kong" (street name)
   - "Shanghai Tunnel, Portland Oregon"

---

### Phase 3: Ground Truth Validation
**Goal:** Validate against known, authoritative lists

**Test Categories:**
1. **BIS Entity List Validation**
   - All 24+ Chinese entities on BIS Entity List
   - Should: 100% detection rate
   - Measure: Precision, recall, confidence scores

2. **OpenSanctions Cross-Reference**
   - Database has 2,293 Chinese sanctioned entities
   - Sample 100 random entities
   - Validate detection accuracy
   - Measure confidence distribution

3. **GLEIF Chinese Entities**
   - Database has 1,750 Chinese LEIs
   - Sample 100 entities with legal names
   - Test detection across various legal forms
   - Validate country code extraction

4. **Known Non-Chinese Entities**
   - Fortune 500 US companies
   - European multinationals
   - Japanese corporations (Sony, Toyota, NTT)
   - Korean companies (Samsung, LG, SK)
   - Taiwanese companies (TSMC, Foxconn, MediaTek)

---

### Phase 4: Geopolitical Edge Cases
**Goal:** Ensure correct handling of sensitive distinctions

**Test Categories:**
1. **Taiwan (ROC) Exclusion**
   - TSMC (Taiwan Semiconductor Manufacturing Company)
   - Foxconn (Hon Hai Precision Industry)
   - MediaTek (chip designer)
   - Taiwan Mobile, Taiwan Semiconductor
   - "Taipei" (capital city)
   - "Formosa" (historical name)
   - "Republic of China" (official name)

2. **Hong Kong Distinction**
   - Should detect as Hong Kong, NOT China
   - "Hong Kong Exchanges and Clearing"
   - "HK SAR"
   - "HSBC Hong Kong"
   - Verify separate categorization

3. **Historical/Former Chinese Entities**
   - "Formerly owned by Chinese entity"
   - "Divested in 2020"
   - "Previously Beijing Corp, now Washington Corp"
   - Should NOT detect current ownership

4. **Chinese Diaspora**
   - "Chinese-American Chamber of Commerce"
   - "Overseas Chinese Association"
   - "Chinese Cultural Center (San Francisco)"
   - Should distinguish from PRC entities

---

### Phase 5: False Positive Deep Dive
**Goal:** Find all incorrectly flagged non-Chinese entities

**Test Categories:**
1. **US Geographic Locations**
   - China, Michigan
   - China Beach, California
   - China Cove, California
   - Chino, California
   - Chino Hills, California

2. **Restaurant Chains**
   - China King
   - China Wok
   - Great Wall Restaurant
   - Panda Express
   - P.F. Chang's

3. **Cultural Organizations**
   - Chinese Historical Society (US-based)
   - Chinese American Museum
   - Chinese Language Services (translation companies)
   - Confucius Institute (complex - some US-based)

4. **Porcelain/Ceramics**
   - Homer Laughlin China Company (US porcelain)
   - Fine china
   - Bone china
   - China cabinet

5. **Substring False Positives**
   - T K C Enterprises (contains "k c")
   - Mavich LLC (contains "avic")
   - Aztec Environmental (contains "zte")
   - COMAC Pump (not COMAC aircraft)

6. **European Names**
   - Italian surnames: Facchinaggi, Vecchini
   - Spanish surnames: Montesinos, Chinchilla
   - French: Chinard, Chineaud

---

### Phase 6: Confidence Scoring Validation
**Goal:** Verify confidence scores accurately reflect detection strength

**Test Categories:**
1. **Very High Confidence (0.90-0.95)**
   - Country code: "CHN"
   - Known entities: "Huawei Technologies Co., Ltd."
   - Multiple indicators: "Beijing Telecom, China"

2. **High Confidence (0.70-0.85)**
   - Major Chinese cities: "Shanghai Corporation"
   - Hong Kong: "Hong Kong Exchanges"
   - Multiple weak indicators

3. **Medium Confidence (0.50-0.65)**
   - Generic Chinese indicators: "China Trading Company"
   - Single indicator: "Beijing Corp"

4. **Low Confidence (0.30-0.40)**
   - Product sourcing: "Made in China"
   - Ambiguous mentions: "China acceptable"

5. **No Detection (< 0.30)**
   - False positives should score < 0.30
   - Non-Chinese entities

**Validation:**
- Confidence scores should be monotonic with evidence strength
- Multiple indicators should increase confidence
- Confidence should never decrease when adding confirming evidence

---

### Phase 7: Production Data Validation
**Goal:** Measure actual performance on real data

**Test Categories:**
1. **USAspending Sample Validation**
   - Random sample: 1,000 records flagged as Chinese
   - Manual review by human analyst
   - Calculate:
     - True Positives (correctly flagged)
     - False Positives (incorrectly flagged)
     - Precision = TP / (TP + FP)
   - Target: ≥95% precision

2. **TED Contracts Sample Validation**
   - Random sample: 500 of 6,470 flagged contracts
   - Manual review
   - Calculate precision
   - Target: ≥95% precision

3. **USPTO Patents Sample Validation**
   - Random sample: 500 of 425,074 Chinese patents
   - Verify assignee is actually Chinese
   - Calculate precision
   - Target: ≥90% precision (lower threshold for historical data)

4. **False Negative Estimation**
   - Sample 1,000 records NOT flagged
   - Manual review for missed Chinese entities
   - Calculate:
     - False Negatives (missed Chinese entities)
     - Recall = TP / (TP + FN)
   - Target: ≥90% recall

---

### Phase 8: Regression Testing
**Goal:** Ensure previously fixed issues stay fixed

**Test Categories:**
1. **Historical False Positives**
   - "64.6% false positives removed" claim
   - What were they?
   - Are they in the test suite?
   - Can they recur?

2. **Known Bypass Techniques**
   - All bypasses from RED_TEAM_VALIDATION.py
   - Spaced names (fixed)
   - Misspellings (partially fixed)
   - Hyphenated names (NOT FIXED)

3. **Fabrication Incidents**
   - Incident 004: Lithuania data query error
   - Are query validation tests in place?
   - Can similar errors recur?

---

### Phase 9: Integration Testing
**Goal:** Test full detection pipeline, not just individual functions

**Test Categories:**
1. **End-to-End Detection**
   - Input: Full USAspending record
   - Output: Detection result with confidence
   - Validate all fields used correctly

2. **Multi-Field Detection**
   - vendor_name + recipient_country_code
   - vendor_name + pop_country_name
   - Conflicting signals (name says China, country says USA)

3. **Database Integration**
   - Insert detection result
   - Query detection result
   - Validate data integrity

---

### Phase 10: Security Testing
**Goal:** Ensure system can't be exploited

**Test Categories:**
1. **Injection Attacks**
   - SQL injection in entity names
   - XSS in descriptions
   - Command injection attempts

2. **Denial of Service**
   - 1 MB entity name
   - 10,000 nested parentheses
   - ReDoS (Regular Expression DoS)

3. **Data Leakage**
   - Does error message leak patterns?
   - Can attacker infer detection rules?

---

## Success Criteria

### Must Pass (Blockers)
- [ ] Zero security vulnerabilities
- [ ] Zero Taiwan/ROC false positives
- [ ] ≥95% precision on USAspending sample
- [ ] ≥90% recall on USAspending sample
- [ ] BIS Entity List: 100% detection

### Should Pass (Important)
- [ ] Zero Chinati Foundation type false positives
- [ ] Hyphenated names detected
- [ ] Confidence scores validated
- [ ] ≥95% precision on TED sample
- [ ] OpenSanctions sample: ≥95% accuracy

### Nice to Have (Improvements)
- [ ] Unicode attack resistance
- [ ] Context disambiguation
- [ ] Historical entity handling
- [ ] Diaspora organization distinction

---

## Test Execution Order

**Week 1: Quick Wins**
1. Run Phase 1 (Adversarial) - find immediate bypasses
2. Run Phase 5 (False Positives) - find immediate noise
3. Run Phase 4 (Geopolitical) - validate Taiwan handling

**Week 2: Ground Truth**
4. Run Phase 3 (Ground Truth) - validate against known lists
5. Run Phase 6 (Confidence) - validate scoring

**Week 3: Production**
6. Run Phase 7 (Production) - measure real performance
7. Run Phase 8 (Regression) - ensure fixes stick

**Week 4: Integration**
8. Run Phase 9 (Integration) - end-to-end validation
9. Run Phase 10 (Security) - ensure safety
10. Generate comprehensive report

---

## Metrics to Track

### Detection Quality
- **Precision:** TP / (TP + FP) - of flagged entities, % actually Chinese
- **Recall:** TP / (TP + FN) - of Chinese entities, % we caught
- **F1 Score:** 2 * (Precision * Recall) / (Precision + Recall)
- **False Positive Rate:** FP / (FP + TN)

### Confidence Calibration
- **Confidence Distribution:** Histogram of scores
- **Precision by Confidence Band:**
  - [0.90-0.95]: Should be ~100% precision
  - [0.70-0.85]: Should be ~95% precision
  - [0.50-0.65]: Should be ~85% precision
  - [0.30-0.40]: Should be ~50% precision (sourcing)

### Coverage
- **Test Coverage:** % of code executed
- **Requirement Coverage:** % of specs tested
- **Edge Case Coverage:** % of known edge cases in tests

---

## Deliverables

1. **Comprehensive Test Suite** (`tests/test_comprehensive_audit.py`)
2. **Ground Truth Validation Results** (CSV with manual review)
3. **Precision/Recall Report** (measured on production data)
4. **Bypass Catalog** (all discovered evasion techniques)
5. **False Positive Catalog** (all incorrectly flagged entities)
6. **Confidence Calibration Report** (precision by confidence band)
7. **Executive Summary** (1-page findings and recommendations)
8. **Remediation Roadmap** (prioritized fixes)

---

**Audit Lead:** Independent Review
**Timeline:** 4 weeks
**Next Action:** Execute Phase 1 adversarial testing
